import os
import sys
import subprocess
from colorama import Fore, Back, Style
from utils import config


def run_wasm(filepath, inputs, suppress_output=False):
    """Execute a WebAssembly file with the provided inputs.

    Runs a compiled WASM file using a JavaScript runner, handling input processing,
    output capturing, and error handling. Large inputs are written to temporary files.

    Args:
        filepath (str): Path to the WASM file to execute
        inputs (list): List of input values or parameters for the program
        suppress_output (bool, optional): If True, suppresses console output but still captures it. Defaults to False.

    Returns:
        str: Output from the WASM execution, including any error messages
    """
    # Choose the appropriate runner based on the gmp flag
    if config.use_gmp:
        wasm_runner = os.path.join(sys.path[0], "wasm_runner", "gmp_runner.js")
    else:
        wasm_runner = os.path.join(sys.path[0], "wasm_runner", "wasm_runner.js")

    # if input is to long, write it to a file
    final_inputs = []
    for inp in inputs:
        if len(inp) > 300:  # size limit
            name, value = inp.split("=")
            input_file_path = os.path.join(sys.path[0], "out", f"{name}.txt")
            os.makedirs(os.path.dirname(input_file_path), exist_ok=True)
            with open(input_file_path, "w") as f:
                f.write(value)
            final_inputs.append(f"{name}_file={input_file_path}")
        else:
            final_inputs.append(inp)

    args = ["node", wasm_runner, filepath] + final_inputs

    # Always capture the output when running in suppress mode
    # so we can extract the x0 value, but don't display it
    if suppress_output:
        # Create a subprocess with suppressed console output but captured stdout/stderr
        # We'll still parse the output but won't display it
        stdout = subprocess.PIPE
        stderr = subprocess.PIPE
    else:
        # Use the config settings for normal operation
        stdout = subprocess.PIPE if config.is_capture_output else None
        stderr = subprocess.PIPE if config.is_capture_output else None

    result = subprocess.run(args, stdout=stdout, stderr=stderr, text=True, check=True)

    output = result.stdout if result.stdout else ""

    if result.stderr:
        error_msg = f"{Back.RED}{Fore.WHITE}RuntimeError:{Style.RESET_ALL} {Fore.RED}{result.stderr}{Style.RESET_ALL}"
        return error_msg

    return output
