import time
from colorama import Fore, Style
from tests.utils import timeout, get_wasm_execution_time, get_wasm_instruction_count
from utils.minimal_compiler import compile_to_wasm
from utils.self_compiler import run_wasm
from utils.utils import get_x0_value


def test_minimal_compiler(test_file, expected_output):
    """
    Test the minimal compiler by compiling and executing a WHILE file.

    This function tests the minimal compiler pipeline by performing the following steps:
    1. Compiles the input WHILE/EWHILE file to WebAssembly (WASM) with a 10-second timeout
    2. Counts the number of instructions in the generated WASM file by analyzing the WAT format
    3. Executes the generated WASM with a 10-second timeout
    4. Extracts the execution time and output value (x0)
    5. Verifies that the output matches the expected value
    6. Reports detailed metrics including compile time, execution time, and instruction count

    Args:
        test_file (str): Path to the test file (.ewhile or .while)
        expected_output (str): Expected output value from the program

    Returns:
        tuple: (success, correct, wasm_filepath, compile_time, run_time, x0_value, wasm_instructions)
            - success (bool): Whether compilation and execution were successful
            - correct (bool): Whether the output matches the expected output
            - wasm_filepath (str): Path to the generated WASM file
            - compile_time (float): Time taken for compilation in seconds
            - run_time (float): Time taken for execution in seconds
            - x0_value (str): Output value from the program (x0 register)
            - wasm_instructions (int): Number of WASM instructions in the generated file
    """
    print(
        f"\n{Fore.YELLOW}{Style.BRIGHT}▶ 2. Testing Minimal Compiler{Style.RESET_ALL}"
    )

    try:
        # Use timeout for minimal compiler
        @timeout(10)
        def run_minimal_compilation(input_file):
            return compile_to_wasm(input_file)

        # Compile with minimal compiler
        minimal_compile_start = time.time()
        wasm_filepath = run_minimal_compilation(test_file)
        minimal_compile_end = time.time()
        minimal_compile_time = minimal_compile_end - minimal_compile_start

        # Count WASM instructions using wasm-stats
        wasm_instructions = get_wasm_instruction_count(wasm_filepath)

        # Run compiled program with timeout
        @timeout(10)
        def run_minimal_wasm(filepath):
            return run_wasm(filepath, [], suppress_output=True)

        # Get output from WASM execution
        minimal_output = run_minimal_wasm(wasm_filepath)

        # Extract execution time reported directly from the WASM runner
        minimal_run_time = get_wasm_execution_time(minimal_output)
        if minimal_run_time is None:
            print(
                f"  {Fore.RED}✗ Could not get WASM execution time from runner output{Style.RESET_ALL}"
            )
            minimal_run_time = 0

        # Extract output and check correctness
        minimal_x0_value = str(get_x0_value(minimal_output))
        minimal_correct = minimal_x0_value == expected_output

        # Display results
        result_color = Fore.GREEN if minimal_correct else Fore.RED
        print(
            f"  {Fore.GREEN}✓{Style.RESET_ALL} Compile time: {Fore.GREEN}{minimal_compile_time:.4f}s{Style.RESET_ALL}"
        )
        print(
            f"  {Fore.GREEN}✓{Style.RESET_ALL} WASM execution time: {Fore.CYAN}{minimal_run_time:.4f}s{Style.RESET_ALL}"
        )
        print(
            f"  {Fore.GREEN}✓{Style.RESET_ALL} WASM instructions: {Fore.CYAN}{wasm_instructions}{Style.RESET_ALL}"
        )

        result_symbol = "✓" if minimal_correct else "✗"
        print(
            f"  {result_color}{result_symbol}{Style.RESET_ALL} Result correct: {result_color}{minimal_correct}{Style.RESET_ALL} (Expected: {expected_output}, Got: {minimal_x0_value})"
        )

        return (
            True,
            minimal_correct,
            wasm_filepath,
            minimal_compile_time,
            minimal_run_time,
            minimal_x0_value,
            wasm_instructions,
        )
    except TimeoutError as e:
        print(f"  {Fore.RED}✗ TIMEOUT: {str(e)}{Style.RESET_ALL}")
        return False, False, None, 0, 0, None, 0
    except Exception as e:
        print(f"  {Fore.RED}✗ ERROR in minimal compiler: {str(e)}{Style.RESET_ALL}")
        return False, False, None, 0, 0, None, 0
