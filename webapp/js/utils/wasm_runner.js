// Browser script to load and run WASM modules with GMP-based bigint library
// Simplified version with basic functionality only

async function runWasm(wasmBytes, parameters = {}) {
  try {
    // Load the GMP-based library (emscripten generated)
    const gmpModule = await GmpModule();


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
      },
    });

    // Get the main function and call it
    const mainFunction = wasmModule.instance.exports.main;
    if (typeof mainFunction === 'function') {
      console.log("Calling WASM main function...");
      
      const paramCount = mainFunction.length;
      const argsArray = new Array(paramCount).fill(0);

      // Process input parameters
      for (const [key, value] of Object.entries(parameters)) {
        const index = parseInt(key.replace("n", ""), 10);

        if (isNaN(index)) {
          console.error(`Warning: Invalid argument key format: ${key}`);
          continue;
        }

        if (index > paramCount) {
          console.error(
            `RuntimeError: Argument index ${index} out of bounds for function (expected max index ${paramCount})`
          );
          return null;
        }

        const ptr = writeBigInt(gmpModule, value);
        if (ptr === 0) {
          console.error(`RuntimeError: Failed to create bigint for ${key}=${value}`);
          return null;
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
      
      const result = mainFunction(...argsArray);
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

// Helper function to write BigInt values to GMP pointers
function writeBigInt(gmpModule, value) {
  let bigValue = BigInt(value);
  const ptr = gmpModule._create_bigint();
  while (bigValue > 0n) {
    // Push 32 bits of the bigint into the GMP bigint
    const block = Number(bigValue & 0xFFFFFFFFn);
    gmpModule._push_u32_to_bigint(block);
    bigValue >>= 32n; // Shift right by 32 bits
  }
  return ptr;
}
