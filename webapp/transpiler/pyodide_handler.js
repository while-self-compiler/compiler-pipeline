export async function transpile(args) {
  const pyodide = await loadPyodide();

  // Buffer to collect stdout + stderr
  let output = "";

  // Redirect stdout
  pyodide.setStdout({
    batched: (text) => {
      output += text;
    }
  });

  // Redirect stderr
  pyodide.setStderr({
    batched: (text) => {
      output += text;
    }
  });

  // Your mkdirRecursive and manifest file loading code
  function mkdirRecursive(path) {
    const parts = path.split("/").filter(Boolean);
    let current = "";
    for (const part of parts) {
      current += "/" + part;
      try {
        const stat = pyodide.FS.stat(current);
        if (!pyodide.FS.isDir(stat.mode)) {
          throw new Error(`Path ${current} exists and is not a directory`);
        }
      } catch (e) {
        pyodide.FS.mkdir(current);
      }
    }
  }

  const manifest = await fetch("transpiler/manifest.json").then(res => res.json());
  for (const filepath of manifest) {
    const content = await fetch(filepath).then(res => res.text());
    const dir = filepath.split("/").slice(0, -1).join("/");
    if (dir) mkdirRecursive(dir);
    pyodide.FS.writeFile("/" + filepath, content);
  }
console.log("=== Files in FS ===");
console.log(pyodide.FS.readdir("/transpiler/src/generator/templates"));
  await pyodide.loadPackage("micropip");
  const micropip = pyodide.pyimport("micropip");
  await micropip.install("antlr4-python3-runtime");

  await pyodide.runPythonAsync(`
import sys
sys.path.append("/")
  `);

  const mainScript = await fetch("transpiler/transpile.py").then(res => res.text());

  // Run everything in one go so sys.argv works
  await pyodide.runPythonAsync(`
import sys
sys.argv = ${JSON.stringify(args)}
sys.path.append("/")
${mainScript}
  `);

  // Return collected output as string
  return output;
}
