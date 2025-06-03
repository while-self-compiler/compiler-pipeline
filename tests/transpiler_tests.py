import time
import os
from colorama import Fore, Style
from tests.utils import timeout, count_while_tokens
from transpiler.transpile import generate_while


def test_transpiler(test_file):
    """
    Test the transpiler component by generating a WHILE file from an EWHILE file.

    This function tests the transpilation process which converts EWHILE code to WHILE code.
    If the input file is already a WHILE file, it skips the transpilation step.
    The function also measures the transpilation time and counts the tokens in the generated WHILE file.
    A timeout of 10 seconds is applied to the transpilation process.

    Args:
        test_file (str): Path to the test file (.ewhile or .while)

    Returns:
        tuple: (success, while_filepath, transpile_time, tokens)
            - success (bool): Whether transpilation was successful
            - while_filepath (str): Path to the generated WHILE file or original file if input was already WHILE
            - transpile_time (float): Time taken for transpilation in seconds
            - tokens (int): Number of tokens in the generated WHILE file
    """
    file_ext = os.path.splitext(test_file)[1]
    is_while_file = file_ext == ".while"

    if is_while_file:
        print(
            f"\n{Fore.YELLOW}{Style.BRIGHT}▶ 1. Testing Transpiler {Fore.BLUE}[SKIPPED - Using .while file directly]{Style.RESET_ALL}"
        )
        return True, test_file, 0, 0

    print(f"\n{Fore.YELLOW}{Style.BRIGHT}▶ 1. Testing Transpiler{Style.RESET_ALL}")
    try:
        # Use the timeout decorator for the transpilation step
        @timeout(10)
        def run_transpilation(input_file):
            return generate_while(input_file)

        transpile_start = time.time()
        while_filepath = run_transpilation(test_file)
        transpile_end = time.time()
        transpile_time = transpile_end - transpile_start

        # Count tokens in generated while file
        with open(while_filepath, "r") as f:
            while_content = f.read()
            tokens = count_while_tokens(while_content)
            if tokens is None:
                tokens = "unknown"

        print(
            f"  {Fore.GREEN}✓{Style.RESET_ALL} Transpilation time: {Fore.GREEN}{transpile_time:.4f}s{Style.RESET_ALL}"
        )
        print(
            f"  {Fore.GREEN}✓{Style.RESET_ALL} Generated tokens: {Fore.CYAN}{tokens}{Style.RESET_ALL}"
        )
        return True, while_filepath, transpile_time, tokens
    except TimeoutError as e:
        print(f"  {Fore.RED}✗ TIMEOUT: {str(e)}{Style.RESET_ALL}")
        return False, None, 0, "unknown"
    except Exception as e:
        print(f"  {Fore.RED}✗ ERROR in transpiler: {str(e)}{Style.RESET_ALL}")
        return False, None, 0, "unknown"
