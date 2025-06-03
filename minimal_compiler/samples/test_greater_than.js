// example call: node wasm_runner.js fib.wasm x0=10
const fs = require("fs");

async function runWasm() {
  const wasmPath = process.argv[2];
  if (!wasmPath) {
    console.error("Please provide the path to the WASM file.");
    return;
  }

  const wasmBuffer = fs.readFileSync(wasmPath);

  const imports = {
    env: {
      printf: console.log,
    },
  };

  const wasmModule = await WebAssembly.instantiate(wasmBuffer, imports);
  const exports = wasmModule.instance.exports;
  const memory = exports.memory;

  const mainFunction = exports.main;

  if (!mainFunction) {
    console.error("No valid function found in WASM module");
    return;
  }

  const paramCount = mainFunction.length;

  if (paramCount === 0) {
    console.error(
      "Main function has no parameters, can't proceed with arguments."
    );
    return;
  }

  // init the arguments array with 0s (default value)
  function mainWrapper(argsObj) {
    const argsArray = new Array(paramCount).fill(0);

    for (const [key, value] of Object.entries(argsObj)) {
      const index = parseInt(key.replace("x", ""), 10);

      if (isNaN(index)) {
        console.error(`Invalid argument key format: ${key}`);
        return;
      }

      if (index >= paramCount) {
        console.error(
          `Argument index ${index} out of bounds for function (expected max index ${
            paramCount - 1
          })`
        );
        return;
      }

      argsArray[index] = value;
    }

    return mainFunction(...argsArray);
  }

  // cmd line parsing
  const argsObj = Object.fromEntries(
    process.argv.slice(3).map((arg) => {
      const [key, value] = arg.split("=");
      const numericValue = Number(value);
      if (isNaN(numericValue)) {
        console.error(`Invalid argument value: ${value} for key: ${key}`);
        return [key, 0]; // default to 0
      }
      return [key, numericValue];
    })
  );

  for (const [key] of Object.entries(argsObj)) {
    const index = parseInt(key.replace("x", ""), 10);
    if (index < 0 || index >= paramCount) {
      console.error(`Invalid argument index: ${key}`);
      return;
    }
  }

  const argsFormatted = Array.from({ length: paramCount }, (_, idx) => {
    const key = `x${idx}`;
    return `${key}=${argsObj[key] || 0}`;
  });

  console.log(`Arguments (n=${paramCount}): [${argsFormatted.join(", ")}]`);
  console.log(argsObj);
  readBigInt(memory, mainWrapper(argsObj));
}

// Function to read a bigint from WebAssembly memory
function readBigInt(memory, ptr) {
  // Create a data view to read from the memory buffer
  const view = new DataView(memory.buffer);

  let result = 0n;
  let multiplier = 1n;
  let currentPtr = ptr;

  console.log("Reading bigint from memory:");

  // Traverse the linked list
  console.log(currentPtr, view, result, multiplier);
  while (currentPtr !== 0) {
    // Read the value at the current node
    const value = view.getUint32(currentPtr, true);

    // Read the next pointer
    const nextPtr = view.getInt32(currentPtr + 4, true);

    console.log(
      `  Node at ptr ${currentPtr}: value=${value}, nextPtr=${nextPtr}`
    );

    // Add this value to our result (shifted by appropriate amount)
    result += BigInt(value) * multiplier;

    // Move to the next node
    currentPtr = nextPtr;

    // Increase the multiplier for the next digit
    // Assuming base 2^32 representation
    multiplier *= 0x100000000n;
  }

  return result;
}

runWasm().catch(console.error);
