import os
import time
import subprocess
from colorama import Fore, Style
from tests.utils import timeout


def run_c_integration_tests(test_name):
    """
    Compile and run C version of an integration test to measure runtime performance.
    This is used for comparison with the WHILE/EWHILE versions.

    This function performs the following steps:
    1. Compiles the C version of the test using gcc with GMP library
    2. Executes the compiled program with a timeout of 10 seconds
    3. Measures and reports the execution time
    4. Captures and displays the program output

    Args:
        test_name (str): Base name of the test without extension (e.g., 'fib_test')

    Returns:
        float: Runtime in seconds, or None if compilation or execution failed
    """
    # gmp_lib.c is already in the tests/integration_tests directory
    # No need to copy it

    # Compile the C version
    compile_result = os.system(
        f"gcc -o ./out/{test_name}_c ./tests/integration_tests/{test_name}.c -Wall -lgmp"
    )
    if compile_result != 0:
        print(f"  {Fore.RED}✗ Compilation failed{Style.RESET_ALL}")
        return None

    # Run with timeout using the timeout decorator
    @timeout(10)
    def run_c_test(test_cmd):
        start_time = time.time()
        result = subprocess.run(test_cmd, capture_output=True, text=True, check=True)
        end_time = time.time()
        return result, end_time - start_time

    # Run and capture output
    try:
        result, runtime = run_c_test([f"./out/{test_name}_c"])

        # Display result
        print(
            f"  {Fore.GREEN}✓{Style.RESET_ALL} C runtime: {Fore.CYAN}{runtime:.4f}s{Style.RESET_ALL}"
        )
        for line in result.stdout.strip().split("\n"):
            if line.startswith("Result:"):
                print(f"  {Fore.GREEN}✓{Style.RESET_ALL} {line}")

        return runtime
    except TimeoutError as e:
        print(f"  {Fore.RED}✗ TIMEOUT: {str(e)}{Style.RESET_ALL}")
        return None
    except subprocess.CalledProcessError as e:
        print(f"  {Fore.RED}✗ Execution failed: {e}{Style.RESET_ALL}")
        if e.stdout:
            print(f"    Output: {e.stdout}")
        if e.stderr:
            print(f"    Error: {e.stderr}")
        return None
