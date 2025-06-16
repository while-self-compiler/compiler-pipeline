document.addEventListener("DOMContentLoaded", () => {
  const compileBtn = document.getElementById("compileBtn");
  const codeEditor = document.getElementById("codeEditor");
  const outputArea = document.getElementById("outputArea");

  // Add sample WHILE code as a placeholder
  codeEditor.value = `x1 = x1 + 0;
while x1 > 0 do
  x0 = x0 + 1;
  x1 = x1 - 1;
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

    // For now, just show the parsed code since we're not implementing actual compilation yet
    outputArea.textContent =
      "Compilation request received! (Backend not implemented yet)\n\nParsed code:\n" +
      code;
    outputArea.style.color = "#4caf50";

    // Add visual feedback when button is clicked
    compileBtn.classList.add("clicked");
    setTimeout(() => {
      compileBtn.classList.remove("clicked");
    }, 200);
  });

  // Add auto-resize functionality for the code editor
  codeEditor.addEventListener("input", () => {
    // Auto-adjust the height based on content
    codeEditor.style.height = "auto";
    codeEditor.style.height = codeEditor.scrollHeight + "px";
  });
});
