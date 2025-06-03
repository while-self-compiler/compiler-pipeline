import functools
import signal
import subprocess
from colorama import Fore, Style


class TimeoutError(Exception):
    """
    Exception raised when a function execution exceeds the specified timeout.

    This exception is used by the timeout decorator to indicate that a function
    has taken longer than the allowed time to execute.
    """

    pass


def timeout(seconds):
    """
    Decorator that raises a TimeoutError if the decorated function takes longer than
    the specified number of seconds to execute.

    This decorator uses the SIGALRM signal to implement the timeout functionality.
    It's particularly useful for integration tests where functions might hang.

    Args:
        seconds (int): Maximum number of seconds the decorated function is allowed to run

    Returns:
        function: Decorated function that will raise TimeoutError if it exceeds the time limit

    Raises:
        TimeoutError: If the function execution exceeds the specified timeout
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            def handler(signum, frame):
                raise TimeoutError(f"Function timed out after {seconds} seconds")

            # Set the timeout handler
            original_handler = signal.signal(signal.SIGALRM, handler)
            signal.alarm(seconds)

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                # Reset the alarm and restore the original handler
                signal.alarm(0)
                signal.signal(signal.SIGALRM, original_handler)

        return wrapper

    return decorator


def get_wasm_execution_time(output):
    """
    Extracts the WASM execution time from the wasm_runner.js output.

    This function parses the output from the WASM runner to find a line that
    contains the execution time in the format 'wasm_execution_time=<time_in_ms>'.
    It then converts the time from milliseconds to seconds.

    Args:
        output (str): The output from run_wasm function

    Returns:
        float: The WASM execution time in seconds, or None if not found
    """
    for line in output.splitlines():
        if line.startswith("wasm_execution_time="):
            try:
                execution_time = float(line.split("=")[1])
                return execution_time / 1000.0  # Convert ms to seconds
            except (ValueError, IndexError):
                return None
    return None


def get_wasm_instruction_count(wasm_filepath):
    """
    Count WASM instructions using the wasm-stats command.

    This function runs wasm-stats on the given WASM file and parses the output
    to extract the total number of opcodes. If wasm-stats fails or the output
    cannot be parsed, it returns 0 as a fallback.

    Args:
        wasm_filepath (str): Path to the WASM file to analyze

    Returns:
        int: Total number of WASM opcodes, or 0 if counting fails
    """
    try:
        result = subprocess.run(
            ["wasm-stats", wasm_filepath],
            capture_output=True,
            text=True,
            check=True,
        )
        # Parse the output to extract total opcodes
        for line in result.stdout.splitlines():
            if line.startswith("Total opcodes:"):
                return int(line.split(":")[1].strip())

        # Fallback if parsing fails
        print(
            f"  {Fore.YELLOW}⚠{Style.RESET_ALL} Could not parse wasm-stats output, using fallback count"
        )
        return 0

    except subprocess.CalledProcessError:
        print(
            f"  {Fore.YELLOW}⚠{Style.RESET_ALL} wasm-stats command failed, using fallback count"
        )
        return 0
    except (ValueError, IndexError):
        print(
            f"  {Fore.YELLOW}⚠{Style.RESET_ALL} Could not parse opcode count from wasm-stats output"
        )
        return 0


def count_while_tokens(file_content):
    """
    Count tokens in WHILE language code by counting assignments and loops.

    Args:
        file_content (str): The content of the WHILE language file

    Returns:
        int: Total count of "=" and "while" tokens, or None if can't determine
    """
    if not file_content or not isinstance(file_content, str):
        print(f"  {Fore.YELLOW}⚠{Style.RESET_ALL} Couldn't determine number of tokens")
        return None

    # Convert to lowercase for case-insensitive counting
    content_lower = file_content.lower()
    equals_count = content_lower.count("=")
    while_count = content_lower.count("while")
    return equals_count + while_count
