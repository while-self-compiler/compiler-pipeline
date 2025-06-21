const EXAMPLE_SCRIPTS = [
  "fib.while",
  "factorial.while",
  "self_compiler.while"
];

document.addEventListener("DOMContentLoaded", () => {
  const compileBtn = document.getElementById("open-run");
  //const codeEditor = document.getElementById("codeEditor");
  const outputArea = document.getElementById("outputArea");
  const select = document.getElementById("scriptSelect");
  const languageSelect = document.getElementById("languageSelect");
  const settingsBtn = document.getElementById("open-settings");
  const closeSettingsBtn = document.getElementById("close-settings");

  generateIterationRadios('iteration-container', [
    {
      id: 'iteration-it1',
      label: 'IT1',
      tooltip: 'This setting allows the generator to decide for itself which algorithm is best / easiest for the grammar entered.'
    },
    {
      id: 'iteration-it2',
      label: 'IT2',
      tooltip: 'This setting allows the generator to decide for itself which algorithm is best / easiest for the grammar entered.'
    },
    {
      id: 'iteration-it3',
      label: 'IT3',
      tooltip: 'This setting allows the generator to decide for itself which algorithm is best / easiest for the grammar entered.'
    }
  ], 'iteration-it1');

  function updateVariableToolbar(code) {
    const toolbar = document.getElementById('variable-toolbar');
    toolbar.innerHTML = '';

    const matches = code.match(/\bx(\d+)\b/g);
    if (!matches) return;

    const nums = matches
      .map(m => parseInt(m.slice(1)))
      .filter(n => !isNaN(n) && n > 0); // ignore x0

    if (nums.length === 0) return;

    const max = Math.max(...nums);

    for (let n = 1; n <= max; n++) {
      const wrapper = document.createElement('div');
      wrapper.style.display = 'flex';
      wrapper.style.alignItems = 'center';

      const label = document.createElement('label');
      label.innerHTML = `n<sub>${n}</sub> =`;
      label.style.marginRight = '4px';

      const input = document.createElement('input');
      input.type = 'text';
      input.id = `n${n}`;
      input.name = `n${n}`; 
      input.value = '0';

      wrapper.appendChild(label);
      wrapper.appendChild(input);
      toolbar.appendChild(wrapper);
    }
  }

  settingsBtn.addEventListener("click", () => {
    // hide the main content and show the settings
    document.getElementById("editor-container").style.display = "none";
    document.getElementById("settings-container").style.display = "block";
  });
  closeSettingsBtn.addEventListener("click", () => {
    // hide the settings and show the main content
    document.getElementById("editor-container").style.display = "block";
    document.getElementById("settings-container").style.display = "none";
  });

  const codeEditor = CodeMirror.fromTextArea(document.getElementById("codeEditor"), {
    mode: "text/x-while",
    theme: "material",
    lineNumbers: true,
    indentUnit: 2,
    tabSize: 2,
    lineWrapping: true
  });
  codeEditor.on("change", () => {
    const code = codeEditor.getValue();
    updateVariableToolbar(code);
  });

  EXAMPLE_SCRIPTS.forEach(file => {
    const opt = document.createElement("option");
    opt.value = file;
    opt.textContent = file;
    select.appendChild(opt);
  });

  function getModeFromFilename(filename) {
    if (filename.endsWith(".while")) return "text/x-while";
    if (filename.endsWith(".ewhile")) return "text/x-ewhile";
    return "text/x-while"; // Default mode
  }

  function filterScriptsByMode(mode) {
    select.innerHTML = `<option value="">Select a script</option>`;

    const extension = mode === "text/x-while" ? ".while" : ".ewhile";

    EXAMPLE_SCRIPTS.forEach(file => {
      if (file.endsWith(extension)) {
        const opt = document.createElement("option");
        opt.value = file;
        opt.textContent = file;
        select.appendChild(opt);
      }
    });
  }

  // filterScriptsByMode(languageSelect.value);
  
  select.addEventListener("change", async () => {
    const file = select.value;
    if (!file) return;

    try {
      const res = await fetch(`example_scripts/${file}`);
      if (!res.ok) throw new Error(`The file ${file} could not be loaded: ${res.status}`);
      const content = await res.text();

      codeEditor.setValue(content);

      const detectedMode = getModeFromFilename(file);

      codeEditor.setOption("mode", detectedMode);

      // languageSelect.value = detectedMode;

      outputArea.textContent = `Script loaded: ${file}`;
      outputArea.style.color = "#4caf50";

    } catch (err) {
      outputArea.textContent = `Error: ${err.message}`;
      outputArea.style.color = "#ff6b6b";
    }
  });

  compileBtn.addEventListener("click", async () => {
    renderPipelineStatus([
      { id: 'run', label: 'Prepare and encode input', status: 'pending' },
      { id: 'selfCompile', label: 'Compile with self compiler', status: 'pending' },
      { id: 'execute', label: 'Execute compiled WASM file', status: 'pending' }
    ]);

    const code = codeEditor.getValue().trim();

    if (!code) {
      outputArea.textContent =
        "Error: No code to compile. Please enter some WHILE code.";
      outputArea.style.color = "#ff6b6b";
      updatePipelineStep('run', 'error');
      updatePipelineStep('selfCompile', 'error');
      updatePipelineStep('execute', 'error');
      return;
    }

    try {
      const uppercaseCode = code.toUpperCase();
      const hexString = textToAsciiHex(code);
      const asciiResult = textToAsciiBigInt(code);
      const asciiBigInt = asciiResult.bigint;
      const byteCount = asciiResult.byteCount;

      outputArea.textContent = 
        "Compiling WHILE code...\n\n" +
        "Original code:\n" + code + "\n\n" +
        "Uppercase code:\n" + truncateString(uppercaseCode) + "\n\n" +
        "ASCII Hex representation:\n" + truncateString(hexString) + "\n\n" +
        "ASCII BigInt:\n" + truncateString(asciiBigInt.toString()) + "\n\n" +
        "Byte count:\n" + byteCount + "\n\n" +
        "Running self_compiler.wasm...";
      outputArea.style.color = "#2196f3";

      console.log("WHILE code converted to ASCII hex:", hexString);
      console.log("WHILE code as BigInt:", asciiBigInt);
      console.log("Byte count:", byteCount);
  
      const parameters = {
        "n1": asciiBigInt,  // ASCII representation as BigInt
        "n2": BigInt(byteCount)  // Number of bytes as BigInt
      };

      updatePipelineStep('run', 'success');

      console.log(`Running self_compiler.wasm with n1=${asciiBigInt}, n2=${byteCount}`);

      const response = await fetch("content/self_compiler.wasm");
      if (!response.ok) {
        throw new Error(`Failed to load self_compiler.wasm: ${response.status}`);
      }

      updatePipelineStep('selfCompile', 'success');

      const wasmBytes = await response.arrayBuffer();

      let result = "";
      try {
        result = await runWasmInWorker(wasmBytes, parameters);
        updatePipelineStep('execute', 'success');
      } catch (err) {
        updatePipelineStep('execute', 'error');
        throw err;  
      }      
      const resultBigInt = BigInt(result);
      let hexResult = resultBigInt.toString(16);
      
      if (hexResult.length % 2 !== 0) {
        hexResult = "0" + hexResult;
      }
      
      const wasmHex = "00" + hexResult;
      updatePipelineStep('execute', 'success');
      console.log(`Self compiler result: ${result}`);
      console.log(`Hex representation: ${hexResult}`);
      console.log(`WASM hex with prefix: ${wasmHex}`);
      
      const wasmBytesFromResult = new Uint8Array(wasmHex.length / 2);
      for (let i = 0; i < wasmHex.length; i += 2) {
        wasmBytesFromResult[i / 2] = parseInt(wasmHex.substr(i, 2), 16);
      }
      
      outputArea.textContent = 
        "Compilation completed! Running compiled WASM...\n\n" +
        "Original code:\n" + code + "\n\n" +
        "Self compiler result (decimal):\n" + truncateString(result.toString()) + "\n\n" +
        "Self compiler result (hex):\n" + truncateString(hexResult) + "\n\n" +
        "WASM bytes (with 00 prefix):\n" + truncateString(wasmHex) + "\n\n" +
        "Executing compiled WASM...";
      outputArea.style.color = "#2196f3";

      const toolbar = document.getElementById('variable-toolbar');
      const inputs = Array.from(toolbar.querySelectorAll('input[id^="n"]'))
        .filter(input => /^n[1-9]\d*$/.test(input.id)); 

      const parametersRuntime = {};
      inputs.forEach(input => {
        const key = input.id;
        let val = input.value.trim();
        try {
          val = val === '' ? 0n : BigInt(val);
        } catch {
          val = 0n;
        }
        parametersRuntime[key] = val;
      });
      
      const finalResult = await runWasm(wasmBytesFromResult.buffer, parametersRuntime);
      
      outputArea.textContent = 
        "Full compilation and execution completed!\n\n" +
        "Self compiler output (decimal):\n" + result.toString() + "\n\n" +
        "Self compiler output (hex):\n" + hexResult  + "\n\n" +
        "WASM bytes:\n" + wasmHex  + "\n\n"

      const outputWatCheckbox = document.getElementById('output-wat');
      const printWat = outputWatCheckbox && outputWatCheckbox.checked;
      if(printWat) {
        const watCode = await generateWatCode(wasmBytes);
        const newWindow = window.open();
        newWindow.document.write('<pre>' + escapeHtml(watCode) + '</pre>');
        newWindow.document.title = 'WAT Code Output';
        newWindow.document.close();
      }

      outputArea.style.color = "#4caf50";

      document.getElementById("resultbar").innerHTML = "";
      const wrapper = document.createElement('div');
      wrapper.style.display = 'flex';
      wrapper.style.alignItems = 'center';

      const label = document.createElement('label');
      label.innerHTML = `x<sub>0</sub> = ${finalResult.toString()}`;
      label.style.marginRight = '4px';

      wrapper.appendChild(label);
      document.getElementById("resultbar").appendChild(wrapper);
    } catch (error) {
      outputArea.textContent = 
        "Compilation failed!\n\n" +
        "Original code:\n" + code + "\n\n" +
        "Error:\n" + error.message;
      outputArea.style.color = "#ff6b6b";
      console.error("Compilation error:", error);
    }

    compileBtn.classList.add("clicked");
    setTimeout(() => {
      compileBtn.classList.remove("clicked");
    }, 200);
  });
/*
  codeEditor.addEventListener("input", () => {
    codeEditor.style.height = "auto";
    codeEditor.style.height = codeEditor.scrollHeight + "px";
  });*/
  /*
  languageSelect.addEventListener("change", (e) => {
    console.log("Language changed to:", e.target.value);
    const mode = e.target.value;  
    codeEditor.setOption("mode", mode);
    filterScriptsByMode(mode);
    codeEditor.setValue("");
    outputArea.textContent = "";
  });*/
});

function truncateString(str, maxLength = 50) {
  if (str.length <= maxLength) {
    return str;
  }
  return str.substring(0, maxLength) + "...";
}

function renderPipelineStatus(steps) {
  const container = document.getElementById("pipeline-status");
  container.innerHTML = ''; // Clear previous

  steps.forEach(step => {
    const div = document.createElement("div");
    div.className = `pipeline-step ${step.status}`;
    div.textContent = step.label;
    div.id = `pipeline-${step.id}`;
    container.appendChild(div);
  });
}

function updatePipelineStep(id, status) {
  const step = document.getElementById(`pipeline-${id}`);
  if (step) {
    step.className = `pipeline-step ${status}`;
  }
}

function runWasmInWorker(wasmBytes, parameters) {
  return new Promise((resolve, reject) => {
    const worker = new Worker("js/utils/wasm_worker.js"); 

    worker.onmessage = (e) => {
      const { success, result, error } = e.data;
      worker.terminate();

      if (success) {
        resolve(result);
      } else {
        reject(new Error(error));
      }
    };

    worker.onerror = (err) => {
      worker.terminate();
      reject(err);
    };

    worker.postMessage({ wasmBytes, parameters });
  });
}

function resetPipelineStatus(steps) {
  steps.forEach(id => updatePipelineStep(id, 'pending'));
}

function generateIterationRadios(containerId, iterations, checkedId) {
  const container = document.getElementById(containerId);
  if (!container) {
    console.error(`Container with id '${containerId}' not found`);
    return;
  }

  container.innerHTML = ''; // Clear existing content

  iterations.forEach(({ id, label, tooltip }) => {
    const div = document.createElement('div');

    const input = document.createElement('input');
    input.type = 'radio';
    input.name = 'iteration';
    input.id = id;
    input.value = label.toLowerCase();
    if (id === checkedId) input.checked = true;

    const inputLabel = document.createElement('label');
    inputLabel.htmlFor = id;
    inputLabel.textContent = label;

    const tooltipDiv = document.createElement('div');
    tooltipDiv.className = 'tooltip';

    const img = document.createElement('img');
    img.className = 'question-mark';
    img.id = `help-${id}`;
    img.src = 'img/question_icon.png';

    const span = document.createElement('span');
    span.className = 'tooltiptext';
    span.textContent = tooltip;

    tooltipDiv.appendChild(img);
    tooltipDiv.appendChild(span);

    div.appendChild(input);
    div.appendChild(inputLabel);
    div.appendChild(tooltipDiv);
    div.appendChild(document.createElement('br'));

    container.appendChild(div);
  });
}

async function generateWatCode(wasmBytes) {
  // Wabt laden
  const wabt = await WabtModule();

  // WASM-Bytes als Uint8Array annehmen
  try {
    const module = wabt.readWasm(wasmBytes, { readDebugNames: true });
    module.generateNames();
    module.applyNames();
    const wat = module.toText({ foldExprs: false, inlineExport: false });
    module.destroy();
    return wat;
  } catch (e) {
    console.error("Fehler beim Konvertieren von WASM zu WAT:", e);
    return "// Fehler beim Erzeugen von WAT-Code";
  }
}

function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}