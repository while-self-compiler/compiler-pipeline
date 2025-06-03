// Node.js script to load and run WASM modules
const fs = require("fs").promises;
const path = require("path");

async function parseArgs(argv) {
  const argsObj = {};

  for (const arg of argv) {
    const [key, valRaw] = arg.split("=");

    if (key.endsWith("_file")) {
      const actualKey = key.replace("_file", "");
      const fileContent = await fs.readFile(valRaw, "utf8");
      argsObj[actualKey] = BigInt(fileContent.trim());
    } else {
      try {
        const val = BigInt(valRaw.trim());
        argsObj[key] = val >= 0n ? val : 0n;
      } catch {
        console.warn(`Warning: ${key}=${valRaw} invalid, set to 0`);
        argsObj[key] = 0n;
      }
    }
  }

  return argsObj;
}

async function runWasmTest() {
  try {
    // Create shared memory
    const memory = new WebAssembly.Memory({ initial: 10 });

    // Load bigint_lib.wasm first
    const libPath = path.join(__dirname, "bigint_lib.wasm");
    const libBytes = await fs.readFile(libPath);
    const libModule = await WebAssembly.instantiate(libBytes, {
      env: {
        memory,
        printjs: (ptr) => {
          console.log(`[WASM printjs] Pointer: ${ptr}`);
        },
      },
    });

    // Get the exports from the library
    const libExports = libModule.instance.exports;

    // Get the WebAssembly file path from command line arguments
    const wasmFile = process.argv[2];
    if (!wasmFile) {
      console.error("Error: No WebAssembly file specified");
      console.error("Usage: node wasm_runner.js <wasm_file>");
      process.exit(1);
    }

    // Load the specified WebAssembly file
    const testPath = path.resolve(wasmFile);
    const testBytes = await fs.readFile(testPath);
    const testModule = await WebAssembly.instantiate(testBytes, {
      env: {
        // Pass the required functions from the library
        get_value: libExports.get_value,
        set_value: libExports.set_value,
        get_next: libExports.get_next,
        set_next: libExports.set_next,
        fib: libExports.fib,
        allocate: libExports.allocate,
        create_chunk: libExports.create_chunk,
        add: libExports.add,
        sub: libExports.sub,
        set_to_zero: libExports.set_to_zero,
        is_gt: libExports.is_gt,
        copy: libExports.copy,
        mul: libExports.mul,
        div: libExports.big_div,
        mod: libExports.mod,
        left_shift: libExports.left_shift,
        right_shift: libExports.right_shift,
        // Implement printf function for debugging
        printf: (ptr) => {
          // console.log(`[WASM printf] Pointer: ${ptr}`);

          // Get the BigInt value that the pointer points to
          const bigintValue = readBigInt(libExports.get_value, libExports.get_next, ptr);

          console.log(`[echo] ${bigintValue}`);

          // Return the pointer (convention for printf-like functions)
          return ptr;
        },
        // Share memory between modules
        memory: memory,
      },
    });

    const mainFunction = testModule.instance.exports.main;
    const paramCount = mainFunction.length;

    function writeBigInt(value) {
      const bigValue = BigInt(value);

      if (bigValue === 0n) {
        // Special case: create a single node with value 0
        const ptr = libExports.create_chunk(0);
        return ptr;
      }

      let tempValue = bigValue;
      let firstNodePtr = 0;
      let prevNodePtr = 0;

      // Break the number into 32-bit chunks and create linked list
      while (tempValue > 0n) {
        const chunk = Number(tempValue & 0xffffffffn);
        const nodePtr = libExports.create_chunk(chunk);

        // Link it to the previous node if this isn't the first node
        if (prevNodePtr !== 0) libExports.set_next(prevNodePtr, nodePtr);
        else firstNodePtr = nodePtr;

        prevNodePtr = nodePtr;
        tempValue = tempValue >> 32n;
      }

      return firstNodePtr;
    }

    function mainWrapper(argsObj) {
      const argsArray = new Array(paramCount).fill(0);

      for (const [key, value] of Object.entries(argsObj)) {
        const index = parseInt(key.replace("n", ""), 10);

        if (isNaN(index)) {
          console.error(`Warning: Invalid argument key format`);
          continue;
        }

        if (index > paramCount) {
          console.error(
            `RuntimeError: Argument index ${index} out of bounds for function (expected max index ${paramCount})`
          );
          return;
        }

        if (value < 0n) {
          console.error(
            `RuntimeError: ${key}=${value} not in the set of natural numbers`
          );
          return;
        }

        const ptr = writeBigInt(value);
        argsArray[index - 1] = ptr;
      }

      // go trough argsArray and for every 0 value, set it to bigint pointer to 0
      for (let i = 0; i < argsArray.length; i++) {
        if (argsArray[i] === 0) {
          argsArray[i] = libExports.create_chunk(0);
        }
      }

      console.log("Calling main function with args:", argsArray);

      return mainFunction(...argsArray);
    }

    // cmd line parsing - FIXED to use BigInt instead of Number
    const argsObj = await parseArgs(process.argv.slice(3));

    for (const [key] of Object.entries(argsObj)) {
      const index = parseInt(key.replace("n", ""), 10);
      if (isNaN(index) ||index <= 0 || index > paramCount) {
        console.error(`RuntimeError: Invalid argument index: ${key}`);
        return;
      }
    }

    const argsFormatted = Array.from({ length: paramCount }, (_, idx) => {
      const key = `n${idx + 1}`;
      return `${key}=${argsObj[key] || 0n}`;
    });

    console.log(`\nP_${paramCount}(${argsFormatted.join(", ")})`);

    // Start measuring WASM execution time
    const startTime = process.hrtime.bigint();
    
    const resultPtr = mainWrapper(argsObj);
    
    // End measurement and calculate duration in milliseconds
    const endTime = process.hrtime.bigint();
    const executionTimeNs = Number(endTime - startTime);
    const executionTimeMs = executionTimeNs / 1_000_000; // Convert ns to ms
    
    const resultValue = readBigInt(
      libExports.get_value,
      libExports.get_next,
      resultPtr
    );
    
    // Output the result and execution time in a parsable format
    console.log(`x0=${resultValue}`);
    console.log(`wasm_execution_time=${executionTimeMs}`);
  } catch (error) {
    console.error("Error during WebAssembly execution:", error);
  }
}

function readBigInt(get_value, get_next, ptr) {
  let result = 0n;
  let multiplier = 1n;
  let currentPtr = ptr;

  // console.log("Reading bigint from memory:");

  // Traverse the linked list
  while (currentPtr !== 0) {
    const value = get_value(currentPtr);
    const uvalue = value >>> 0;

    const nextPtr = get_next(currentPtr);

    result += BigInt(uvalue) * multiplier;

    currentPtr = nextPtr;
    multiplier *= 0x100000000n;
  }

  return result;
}

// Run the test
runWasmTest().catch((err) => console.error("Full error:", err));
