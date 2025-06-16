document.addEventListener("DOMContentLoaded", () => {
  const compileBtn = document.getElementById("compileBtn");
  const runWasmBtn = document.getElementById("runWasmBtn");
  const codeEditor = document.getElementById("codeEditor");
  const outputArea = document.getElementById("outputArea");

  // Add sample WHILE code as a placeholder
  codeEditor.value = `x1 = x1 + 7;
while x1 > 0 do
  x0 = x0 + 1;
  x1 = x1 - 1
end`;

  // Add event listener for compile button
  compileBtn.addEventListener("click", async () => {
    const code = codeEditor.value.trim();

    if (!code) {
      outputArea.textContent =
        "Error: No code to compile. Please enter some WHILE code.";
      outputArea.style.color = "#ff6b6b";
      return;
    }

    try {
      // Convert code to uppercase first, then to ASCII hex values
      const uppercaseCode = code.toUpperCase();
      const hexString = textToAsciiHex(code);
      const asciiResult = textToAsciiBigInt(code);
      const asciiBigInt = asciiResult.bigint;
      const byteCount = asciiResult.byteCount;

      // Display processing information
      outputArea.textContent = 
        "Compiling WHILE code...\n\n" +
        "Original code:\n" + code + "\n\n" +
        "Uppercase code:\n" + uppercaseCode + "\n\n" +
        "ASCII Hex representation:\n" + hexString + "\n\n" +
        "ASCII BigInt:\n" + asciiBigInt.toString() + "\n\n" +
        "Byte count:\n" + byteCount + "\n\n" +
        "Running self_compiler.wasm...";
      outputArea.style.color = "#2196f3";

      // Also log to console
      console.log("WHILE code converted to ASCII hex:", hexString);
      console.log("WHILE code as BigInt:", asciiBigInt);
      console.log("Byte count:", byteCount);

      // Create parameters for self_compiler.wasm
      const parameters = {
        "n1": asciiBigInt,  // ASCII representation as BigInt
        "n2": BigInt(byteCount)  // Number of bytes as BigInt
      };

      console.log(`Running self_compiler.wasm with n1=${asciiBigInt}, n2=${byteCount}`);

      // Fetch and run self_compiler.wasm
      const response = await fetch("content/self_compiler.wasm");
      if (!response.ok) {
        throw new Error(`Failed to load self_compiler.wasm: ${response.status}`);
      }
      
      const wasmBytes = await response.arrayBuffer();
      
      // Run the self compiler with parameters
      const result = await runWasm(wasmBytes, parameters);
      
      // Convert the decimal result to hex and add 00 prefix
      const resultBigInt = BigInt(result);
      let hexResult = resultBigInt.toString(16);
      
      // Ensure even number of hex digits
      if (hexResult.length % 2 !== 0) {
        hexResult = "0" + hexResult;
      }
      
      // Add 00 prefix
      const wasmHex = "00" + hexResult;
      
      console.log(`Self compiler result: ${result}`);
      console.log(`Hex representation: ${hexResult}`);
      console.log(`WASM hex with prefix: ${wasmHex}`);
      
      // Convert hex string to bytes for WASM execution
      const wasmBytesFromResult = new Uint8Array(wasmHex.length / 2);
      for (let i = 0; i < wasmHex.length; i += 2) {
        wasmBytesFromResult[i / 2] = parseInt(wasmHex.substr(i, 2), 16);
      }
      
      outputArea.textContent = 
        "Compilation completed! Running compiled WASM...\n\n" +
        "Original code:\n" + code + "\n\n" +
        "Self compiler result (decimal):\n" + result + "\n\n" +
        "Self compiler result (hex):\n" + hexResult + "\n\n" +
        "WASM bytes (with 00 prefix):\n" + wasmHex + "\n\n" +
        "Executing compiled WASM...";
      outputArea.style.color = "#2196f3";
      
      // Run the compiled WASM without parameters
      const finalResult = await runWasm(wasmBytesFromResult.buffer);
      
      outputArea.textContent = 
        "Full compilation and execution completed!\n\n" +
        "Original WHILE code:\n" + code + "\n\n" +
        "Self compiler output (decimal):\n" + result + "\n\n" +
        "Self compiler output (hex):\n" + hexResult + "\n\n" +
        "WASM bytes:\n" + wasmHex + "\n\n" +
        "Final execution result:\n" + finalResult;
      outputArea.style.color = "#4caf50";

    } catch (error) {
      outputArea.textContent = 
        "Compilation failed!\n\n" +
        "Original code:\n" + code + "\n\n" +
        "Error:\n" + error.message;
      outputArea.style.color = "#ff6b6b";
      console.error("Compilation error:", error);
    }

    // Add visual feedback when button is clicked
    compileBtn.classList.add("clicked");
    setTimeout(() => {
      compileBtn.classList.remove("clicked");
    }, 200);
  });

  // Add event listener for run WASM button
  runWasmBtn.addEventListener("click", async () => {
    try {
      outputArea.textContent = "Loading and running example.wasm...";
      outputArea.style.color = "#2196f3";

      // Get the input value and convert to BigInt
      const inputCode = codeEditor.value.trim();
      const asciiResult = textToAsciiBigInt(inputCode);
      const inputBigInt = asciiResult.bigint;
      const inputByteCount = asciiResult.byteCount;
      
      // Create parameters object with the input value as n1
      const parameters = {
        "n1": inputBigInt
      };

      console.log(`Running WASM with input: "${inputCode}" -> BigInt: ${inputBigInt}, Bytes: ${inputByteCount}`);

      // Fetch the WASM file
      const response = await fetch("content/example.wasm");
      if (!response.ok) {
        throw new Error(`Failed to load WASM file: ${response.status}`);
      }
      
      const wasmBytes = await response.arrayBuffer();
      
      // Run the WASM using our runner function with parameters
      const result = await runWasm(wasmBytes, parameters);
      
      outputArea.textContent = `WASM execution completed!\nInput: "${inputCode}"\nInput as BigInt: ${inputBigInt}\nByte count: ${inputByteCount}\nResult: ${result}`;
      outputArea.style.color = "#4caf50";

      // Add visual feedback
      runWasmBtn.classList.add("clicked");
      setTimeout(() => {
        runWasmBtn.classList.remove("clicked");
      }, 200);
      
    } catch (error) {
      outputArea.textContent = `Error running WASM: ${error.message}`;
      outputArea.style.color = "#ff6b6b";
      console.error("WASM execution error:", error);
    }
  });

  // Add auto-resize functionality for the code editor
  codeEditor.addEventListener("input", () => {
    // Auto-adjust the height based on content
    codeEditor.style.height = "auto";
    codeEditor.style.height = codeEditor.scrollHeight + "px";
  });
});
