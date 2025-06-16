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
  compileBtn.addEventListener("click", () => {
    const code = codeEditor.value.trim();

    if (!code) {
      outputArea.textContent =
        "Error: No code to compile. Please enter some WHILE code.";
      outputArea.style.color = "#ff6b6b";
      return;
    }

    // Convert code to uppercase first, then to ASCII hex values
    const uppercaseCode = code.toUpperCase();
    const hexString = textToAsciiHex(code);
    const asciiBigInt = textToAsciiBigInt(code);

    // Display both the original code and the hex representation
    outputArea.textContent = 
      "Compilation request received! (Backend not implemented yet)\n\n" +
      "Original code:\n" + code + "\n\n" +
      "Uppercase code:\n" + uppercaseCode + "\n\n" +
      "ASCII Hex representation:\n" + hexString + "\n\n" +
      "ASCII BigInt:\n" + asciiBigInt.toString();
    outputArea.style.color = "#4caf50";
    
    // Also log to console
    console.log("WHILE code converted to ASCII hex:", hexString);
    console.log("WHILE code as BigInt:", asciiBigInt);

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
      const inputBigInt = textToAsciiBigInt(inputCode);
      
      // Create parameters object with the input value as n1
      const parameters = {
        "n1": inputBigInt
      };

      console.log(`Running WASM with input: "${inputCode}" -> BigInt: ${inputBigInt}`);

      // Fetch the WASM file
      const response = await fetch("content/example.wasm");
      if (!response.ok) {
        throw new Error(`Failed to load WASM file: ${response.status}`);
      }
      
      const wasmBytes = await response.arrayBuffer();
      
      // Run the WASM using our runner function with parameters
      const result = await runWasm(wasmBytes, parameters);
      
      outputArea.textContent = `WASM execution completed!\nInput: "${inputCode}"\nInput as BigInt: ${inputBigInt}\nResult: ${result}`;
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
