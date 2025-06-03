from colorama import Fore, Back, Style
import os
import sys
import subprocess
from utils import config


def print_wasm_as_hex(output):
    """Convert WASM output to a hexadecimal representation and display it.

    Extracts the x0 value from the output, converts it to a hexadecimal string,
    and displays it in a formatted table with offset, hex data, and ASCII representation.

    Args:
        output (str): The output from a WASM execution

    Returns:
        str: The hexadecimal representation of the output
    """
    print(f"{Back.BLUE}{Fore.WHITE}{Style.BRIGHT} WASM HEX DATA {Style.RESET_ALL}")
    lines = output.splitlines()
    output_number = 0
    for line in lines:
        if line.startswith("x0="):
            output_number = int(line.split("=")[1])
            break
    output = int(output_number)

    hex_output = hex(output)[2:]
    hex_output = "00" + hex_output

    # Display total size information
    print(
        f"{Fore.BLUE}Hex length:{Style.RESET_ALL} {Fore.YELLOW}{len(hex_output)} chars{Style.RESET_ALL}"
    )
    print(
        f"{Fore.BLUE}Binary size:{Style.RESET_ALL} {Fore.YELLOW}{len(hex_output) // 2} bytes{Style.RESET_ALL}"
    )

    # Create the header for the hex table
    print(
        f"\n{Fore.MAGENTA}{'OFFSET':<8} | {'HEX DATA':<20} | {'ASCII':<16}{Style.RESET_ALL}"
    )
    print(f"{Fore.MAGENTA}{'─' * 8} | {'─' * 20} | {'─' * 16}{Style.RESET_ALL}")

    # Split hex output into chunks of 4 characters (2 bytes) and display in table
    chunks = [hex_output[i : i + 4] for i in range(0, len(hex_output), 4)]
    line_count = 0
    line_chunks = []
    line_ascii = ""

    for i, chunk in enumerate(chunks):
        line_chunks.append(chunk)
        # Try to display ASCII representation if possible
        for j in range(0, len(chunk), 2):
            byte_val = chunk[j : j + 2]
            if len(byte_val) == 2:
                try:
                    char_val = chr(int(byte_val, 16))
                    # Replace non-printable characters with dots
                    if 32 <= int(byte_val, 16) <= 126:
                        line_ascii += char_val
                    else:
                        line_ascii += "."
                except ValueError:
                    line_ascii += "."

        # Print a full line every 4 chunks (8 bytes)
        if (i + 1) % 4 == 0 or i == len(chunks) - 1:
            offset = line_count * 8
            hex_data = " ".join(line_chunks)
            print(
                f"{Fore.CYAN}{offset:08x}{Style.RESET_ALL} | {Fore.YELLOW}{hex_data:<20}{Style.RESET_ALL} | {Fore.GREEN}{line_ascii:<16}{Style.RESET_ALL}"
            )
            line_count += 1
            line_chunks = []
            line_ascii = ""

    return hex_output


def wasm_to_file(output):
    """Convert WASM output to a binary file.

    Processes the output from a WASM execution, extracts the x0 value,
    converts it to binary, and saves it to a file. Also displays formatted
    information about the generated file.

    Args:
        output (str): The output from a WASM execution

    Returns:
        str: Path to the generated WASM file
    """
    print(
        f"{Back.BLUE}{Fore.WHITE}{Style.BRIGHT} PROCESSING WASM OUTPUT {Style.RESET_ALL}"
    )
    lines = output.splitlines()

    # Format program output
    formatted_lines = []
    for line in lines:
        if line.startswith("x0="):
            value = line.split("=")[1]
            formatted_lines.append(
                f"{Fore.GREEN}x0={Style.BRIGHT}{value}{Style.RESET_ALL}"
            )
        else:
            formatted_lines.append(line)

    print(f"\n{Back.BLACK}\n".join(formatted_lines))

    # Extract x0 value for WASM generation
    output_number = 0
    for line in lines:
        if line.startswith("x0="):
            output_number = int(line.split("=")[1])
            break
    output = int(output_number)

    # Generate and display hex output
    output_bytes = hex(output)[2:]
    output_bytes = "00" + output_bytes

    # Show a preview of the hex data
    print(f"\n{Fore.BLUE}WASM Hex Preview:{Style.RESET_ALL}")
    preview_length = min(len(output_bytes), 60)
    preview = output_bytes[:preview_length]
    if len(output_bytes) > preview_length:
        preview += "..."
    print(f"{Fore.YELLOW}{preview}{Style.RESET_ALL}")
    print(
        f"{Fore.BLUE}Total hex length:{Style.RESET_ALL} {Fore.CYAN}{len(output_bytes)} chars{Style.RESET_ALL}"
    )

    if config.is_full_hex:
        print(f"{Fore.BLUE}Full hex data:{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{output_bytes}{Style.RESET_ALL}")

    output_bytes = bytes.fromhex(output_bytes)

    # Save to file
    filename = "wasm_output.wasm"
    out_dir = sys.path[0] + "/out"
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, filename), "wb") as f:
        f.write(output_bytes)
    print(
        f"{Fore.BLUE}Compiled WASM file:{Style.RESET_ALL} {Fore.CYAN}{out_dir}/{filename}{Style.RESET_ALL}"
    )
    print(
        f"{Fore.BLUE}File size:{Style.RESET_ALL} {Fore.YELLOW}{len(output_bytes)} bytes{Style.RESET_ALL}"
    )

    return out_dir + "/" + filename


def hex_to_wasm_bytes(hex_string):
    """Convert a hexadecimal string to bytes.

    Args:
        hex_string (str): The hexadecimal string to convert

    Returns:
        bytes: The byte representation of the hexadecimal string
    """
    return bytes.fromhex(hex_string)


def wasm_bytes_to_wat(wasm_bytes):
    """Convert WebAssembly binary to WebAssembly Text format.

    Saves the WASM bytes to a temporary file and uses the wasm2wat external tool
    to convert it to WAT format. Displays information about the conversion process.

    Args:
        wasm_bytes (bytes): The WebAssembly binary data

    Returns:
        str: The WebAssembly Text (WAT) representation
    """
    print(
        f"{Back.BLUE}{Fore.WHITE}{Style.BRIGHT} CONVERTING WASM TO WAT {Style.RESET_ALL}"
    )

    # Save input bytes to temporary file
    out_path = "./out/self_compiler.wasm"
    with open(out_path, "wb") as f:
        f.write(wasm_bytes)

    print(
        f"{Fore.BLUE}Saved WASM file:{Style.RESET_ALL} {Fore.CYAN}{out_path}{Style.RESET_ALL}"
    )
    print(
        f"{Fore.BLUE}File size:{Style.RESET_ALL} {Fore.YELLOW}{len(wasm_bytes)} bytes{Style.RESET_ALL}"
    )

    # Run the conversion command
    print(
        f"{Fore.BLUE}Running:{Style.RESET_ALL} {Fore.YELLOW}wasm2wat {out_path}{Style.RESET_ALL}"
    )
    result = subprocess.run(["wasm2wat", out_path], capture_output=True, text=True)

    # Check for errors
    if result.returncode != 0:
        error_msg = f"{Back.RED}{Fore.WHITE} ERROR {Style.RESET_ALL} {Fore.RED}wasm2wat failed:{Style.RESET_ALL}\n{result.stderr}"
        raise RuntimeError(error_msg)

    # Success output
    wat_content = result.stdout
    print(f"{Fore.GREEN}✓ Successfully converted to WAT{Style.RESET_ALL}")
    print(
        f"{Fore.BLUE}WAT size:{Style.RESET_ALL} {Fore.YELLOW}{len(wat_content)} chars{Style.RESET_ALL}"
    )

    return wat_content
