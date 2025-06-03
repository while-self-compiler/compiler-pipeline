import os
import sys
from colorama import Fore, Style


def get_x0_value(output):
    """Extract the x0 value from program output.

    Parses the output of a WASM program and extracts the x0 value,
    which contains the result of program execution.

    Args:
        output (str): The output string from a WASM program execution

    Returns:
        int: The extracted x0 value as an integer
    """
    lines = output.splitlines()
    output_number = 0
    for line in lines:
        if line.startswith("x0="):
            output_number = int(line.split("=")[1])
            break
    output = int(output_number)

    return output


def print_auscii_code(code):
    """Print an ASCII representation of a hexadecimal code.

    Converts a numeric code to a hexadecimal string and prints each byte
    along with its corresponding ASCII character in a formatted table.

    Args:
        code (int): The numeric code to convert and print
    """
    ascii_hex = hex(code)[2:]
    if len(ascii_hex) % 2 != 0:
        ascii_hex = "0" + ascii_hex
    print(f"{Fore.MAGENTA}{'HEX':<6} | {'ASCII':<8}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'-' * 6} | {'-' * 8}{Style.RESET_ALL}")
    while len(ascii_hex) != 0:
        first_byte = ascii_hex[:2]
        character = chr(int(first_byte, 16))
        print(
            f"{Fore.YELLOW}{first_byte:<6}{Style.RESET_ALL} | {Fore.CYAN}{character:<8}{Style.RESET_ALL}"
        )
        ascii_hex = ascii_hex[2:]


def to_absolute_path(filepath):
    """Convert a relative path to an absolute path.

    If the provided path is not already an absolute path,
    convert it by prepending the current working directory.

    Args:
        filepath (str): The file path to convert

    Returns:
        str: The absolute path
    """
    if not os.path.isabs(filepath):
        filepath = os.path.join(os.getcwd(), filepath)
    return filepath


def merge_ewhile_files(filepaths):
    """Merge multiple ewhile files into a single output file.

    Reads the content of each file in the provided list, concatenates them
    with newlines in between, and writes the result to a new file in the output directory.

    Args:
        filepaths (list): List of file paths to merge

    Returns:
        str: Path to the merged output file
    """
    merged_code = ""
    for filepath in filepaths:
        with open(filepath, "r") as file:
            code = file.read()
            merged_code += code + "\n"

    out_dir = sys.path[0] + "/out"
    os.makedirs(out_dir, exist_ok=True)
    merged_filepath = out_dir + "/self_compiler.ewhile"
    with open(merged_filepath, "w") as file:
        file.write(merged_code)
    print(
        f"{Fore.BLUE}Merged files into:{Style.RESET_ALL} {Fore.CYAN}{merged_filepath}{Style.RESET_ALL}"
    )
    return merged_filepath
