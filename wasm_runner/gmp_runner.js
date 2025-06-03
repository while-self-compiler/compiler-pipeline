// Node.js script to load and run WASM modules with GMP-based bigint library
const fs = require("fs").promises;
const { read } = require("fs");
const path = require("path");

async function parseArgs(argv) {
  const argsObj = {};

  for (const arg of argv) {
    const [key, valRaw] = arg.split("=");

    if (key.endsWith("_file")) {
      const actualKey = key.replace("_file", "");
      const fileContent = await fs.readFile(valRaw, "utf8");
      argsObj[actualKey] = fileContent.trim();
    } else {
      try {
        const val = BigInt(valRaw.trim());
        argsObj[key] = val >= 0n ? val.toString() : "0";
      } catch {
        console.warn(`Warning: ${key}=${valRaw} invalid, set to 0`);
        argsObj[key] = "0";
      }
    }
  }

  return argsObj;
}

async function runWasmTest() {
  try {
    // Load the GMP-based library (emscripten generated)
    const createGmpModule = require('./gmp_lib.js');
    const gmpModule = await createGmpModule({
      // print: (text) => console.log(`[gmp_lib stdout] ${text}`),
      // printErr: (text) => console.error(`[gmp_lib stderr] ${text}`),
    });

    // Verify all required functions are exported
    const requiredFunctions = [
      '_create_bigint', '_push_u32_to_bigint', '_free_bigint',
      '_is_gt', '_set_to_zero', '_copy', '_is_equal', '_add', '_sub',
      '_right_shift', '_left_shift', '_mul', '_big_div', '_mod', '_read_bigint', '_get_next_u32'
    ];

    for (const funcName of requiredFunctions) {
      if (typeof gmpModule[funcName] !== 'function') {
        console.error(`CRITICAL ERROR: Function "${funcName}" is not exported from gmp_lib.js`);
        return;
      }
    }

    // Get the WebAssembly file path from command line arguments
    const wasmFile = process.argv[2];
    if (!wasmFile) {
      console.error("Error: No WebAssembly file specified");
      console.error("Usage: node gmp_runner.js <wasm_file>");
      process.exit(1);
    }

    // Create shared memory
    const memory = new WebAssembly.Memory({ initial: 4000 });

    // Load the specified WebAssembly file
    const testPath = path.resolve(wasmFile);
    const testBytes = await fs.readFile(testPath);
    const testModule = await WebAssembly.instantiate(testBytes, {
      env: {
        // Pass the required functions from the GMP library
        create_bigint: () => gmpModule._create_bigint(),
        push_u32_to_bigint: (value) => gmpModule._push_u32_to_bigint(value),
        add: (a, b, c) => gmpModule._add(a, b, c),
        sub: (a, b, c) => gmpModule._sub(a, b, c),
        set_to_zero: (ptr) => gmpModule._set_to_zero(ptr),
        is_gt: (a, b) => gmpModule._is_gt(a, b),
        copy: (dest, src) => gmpModule._copy(dest, src),
        mul: (output, a, b) => gmpModule._mul(output, a, b),
        div: (output, a, b) => gmpModule._big_div(output, a, b),
        mod: (output, a, b) => gmpModule._mod(output, a, b),
        left_shift: (output, input, shift) => gmpModule._left_shift(output, input, shift),
        right_shift: (output, input, shift) => gmpModule._right_shift(output, input, shift),
        // Implement printf function for debugging
        printf: (ptr) => {
          let output = readBigInt(ptr);
          console.log(`printf: ${output}`);
        },
        // Share memory between modules
        memory: memory,
      },
    });

    const mainFunction = testModule.instance.exports.main;
    const paramCount = mainFunction.length;

    function writeBigInt(valueStr) {
      let value = BigInt(valueStr);
      const ptr = gmpModule._create_bigint();
      while (value > 0n) {
        // Push 32 bits of the bigint into the GMP bigint
        const block = Number(value & 0xFFFFFFFFn);
        gmpModule._push_u32_to_bigint(block);
        value >>= 32n; // Shift right by 32 bits
      }
      return ptr;
    }

    function readBigInt(ptr) {
      // Read the bigint value as a string
      const blocks = gmpModule._read_bigint(ptr);
      let value = BigInt(0);
      let shift = 0;
      for (let i = 0; i < blocks; i++) {
        let out = gmpModule._get_next_u32();
        let outUnsigned = out >>> 0;
        let outBig = BigInt(outUnsigned);
        value += outBig << BigInt(shift);
        shift += 32;
      }
      return value;
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

        const ptr = writeBigInt(value);
        if (ptr === 0) {
          console.error(`RuntimeError: Failed to create bigint for ${key}=${value}`);
          return;
        }
        
        argsArray[index - 1] = ptr;
      }

      // Fill remaining positions with zero bigints
      for (let i = 0; i < argsArray.length; i++) {
        if (argsArray[i] === 0) {
          argsArray[i] = gmpModule._create_bigint();
        }
      }

      console.log("Calling main function with args:", argsArray);

      return mainFunction(...argsArray);
    }

    // cmd line parsing - uses string representation for large numbers
    const argsObj = await parseArgs(process.argv.slice(3));

    for (const [key] of Object.entries(argsObj)) {
      const index = parseInt(key.replace("n", ""), 10);
      if (isNaN(index) || index <= 0 || index > paramCount) {
        console.error(`RuntimeError: Invalid argument index: ${key}`);
        return;
      }
    }

    const argsFormatted = Array.from({ length: paramCount }, (_, idx) => {
      const key = `n${idx + 1}`;
      return `${key}=${argsObj[key] || "0"}`;
    });

    console.log(`\nP_${paramCount}(${argsFormatted.join(", ")})`);

    // Start measuring WASM execution time
    const startTime = process.hrtime.bigint();
    
    const resultPtr = mainWrapper(argsObj);
    
    // End measurement and calculate duration in milliseconds
    const endTime = process.hrtime.bigint();
    const executionTimeNs = Number(endTime - startTime);
    const executionTimeMs = executionTimeNs / 1_000_000; // Convert ns to ms
    
    // Read the result using GMP's bigint_to_string
    let resultValue = readBigInt(resultPtr);
    
    // Clean up allocated bigints
    for (const [key, value] of Object.entries(argsObj)) {
      const index = parseInt(key.replace("n", ""), 10);
      if (!isNaN(index) && index > 0 && index <= paramCount) {
        // Note: In a real implementation, you'd want to track and free all allocated pointers
      }
    }
    
    // Output the result and execution time in a parsable format
    console.log(`x0=${resultValue}`);
    console.log(`wasm_execution_time=${executionTimeMs}`);
  } catch (error) {
    console.error("Error during WebAssembly execution:", error);
  }
}

// Run the test
runWasmTest().catch((err) => console.error("Full error:", err));
