importScripts("wasm_runner.js");
importScripts("../../content/gmp_lib.js");     

self.onmessage = async (e) => { // Attention: if gmp_lib.js changes, we have to change gmp_lib.wasm path inside gmp_lib.js from /js/utils/ to ../../content
  const { wasmBytes, parameters } = e.data;

  try {
    const result = await runWasm(wasmBytes, parameters);
    self.postMessage({ success: true, result: result?.toString?.() ?? result });
  } catch (error) {
    self.postMessage({ success: false, error: error.message });
  }
};
