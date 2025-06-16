// Browser script to load and run WASM modules with GMP-based bigint library
// Simplified version with basic functionality only

async function runWasm(wasmBytes) {
  try {
    // Load the GMP-based library (emscripten generated)
    const gmpModule = await GmpModule();

    // Create shared memory
    const memory = new WebAssembly.Memory({ initial: 4000 });

    // Load and instantiate the WebAssembly module
    const wasmModule = await WebAssembly.instantiate(wasmBytes, {
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
        printf: (ptr) => {
          const output = readBigInt(gmpModule, ptr);
          console.log(`printf: ${output}`);
        },
        // Share memory between modules
        memory: memory,
      },
    });

    // Get the main function and call it
    const mainFunction = wasmModule.instance.exports.main;
    if (typeof mainFunction === 'function') {
      console.log("Calling WASM main function...");
      const result = mainFunction();
      console.log("WASM execution completed");
      
      // If result is a pointer, try to read it as a BigInt
      if (typeof result === 'number' && result > 0) {
        try {
          const bigIntResult = readBigInt(gmpModule, result);
          console.log(`Result as BigInt: ${bigIntResult}`);
          return bigIntResult;
        } catch (error) {
          console.log(`Could not read result as BigInt, returning raw value: ${result}`);
          return result;
        }
      }
      
      return result;
    } else {
      console.error("Error: main function not found in WASM module");
      return null;
    }

  } catch (error) {
    console.error("Error during WebAssembly execution:", error);
    return null;
  }
}

// Helper function to read BigInt values from GMP pointers
function readBigInt(gmpModule, ptr) {
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
