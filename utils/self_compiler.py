import sys
from colorama import Fore, Back, Style
from utils.utils import merge_ewhile_files
from utils.minimal_compiler import compile_to_wasm
from utils.wasm_runner import run_wasm
from utils.wasm_tools import (
    hex_to_wasm_bytes,
    print_wasm_as_hex,
    wasm_bytes_to_wat,
    wasm_to_file,
)
from transpiler.transpile import generate_while
from utils import config


def self_compiler(filepath, inputs):
    """Compile and run a program using the self-compiler.

    The self-compiler is a WHILE language implementation of a WHILE language compiler.
    This function orchestrates the process of merging necessary components,
    compiling the self-compiler itself, and using it to compile and run the target program.

    Args:
        filepath (str): Path to the source file to compile
        inputs (list): List of input values for the program

    Returns:
        str: Output from the WASM execution
    """
    print(
        f"\n{Back.MAGENTA}{Fore.WHITE}{Style.BRIGHT} COMPILING SELF-COMPILER {Style.RESET_ALL}"
    )
    filepath_macros = sys.path[0] + "/self_compiler/macros.ewhile"
    filepath_lexer = sys.path[0] + "/self_compiler/lexer.ewhile"

    if config.use_gmp:
        filepath_generator = sys.path[0] + "/self_compiler/generator_gmp.ewhile"
    else:
        filepath_generator = sys.path[0] + "/self_compiler/generator.ewhile"

    filepath_compiler = merge_ewhile_files(
        [filepath_macros, filepath_lexer, filepath_generator]
    )
    wasm_filepath_compiler = compile_to_wasm(filepath_compiler)

    print(
        f"\n{Back.CYAN}{Fore.BLACK}{Style.BRIGHT} RUNNING SELF-COMPILER {Style.RESET_ALL}"
    )
    inputs_self = generate_ascii(filepath)

    output = run_wasm(wasm_filepath_compiler, inputs_self)
    output_backup = output
    if config.print_self_compiler_to_file:
        output_file = sys.path[0] + config.self_compiler_output_file_txt
        output_file_hex = sys.path[0] + config.self_compiler_output_file_hex

        # prepare output
        lines = str(output).splitlines()

        # Extract x0 value for WASM generation
        output_number = 0
        for line in lines:
            if line.startswith("x0="):
                output_number = int(line.split("=")[1])
                break
        output = int(output_number)

        # Generate and display hex output
        output_bytes = hex(output)[2:]
        output_bytes = "00" + str(output_bytes)

        with open(output_file, "w") as f:
            f.write(str(output))

        with open(output_file_hex, "w") as f:
            f.write(output_bytes)

    output = output_backup

    try:
        # config.use_gmp = False
        wasm_file = wasm_to_file(output)
        
        if config.no_execution:
            print(f"{Fore.YELLOW}Execution skipped (no-execution flag is set){Style.RESET_ALL}")
            print(f"{Fore.BLUE}WASM file built at:{Style.RESET_ALL} {Fore.CYAN}{wasm_file}{Style.RESET_ALL}")
            return ""
            
        print(
            f"\n{Back.GREEN}{Fore.BLACK}{Style.BRIGHT} RUNNING COMPILED WASM {Style.RESET_ALL}"
        )
        output = run_wasm(wasm_file, inputs)

        # Check if output contains an error message (has colorama formatting)
        if not (Fore.RED in output or Back.RED in output):
            # Format the output more nicely, highlighting the x0 value
            output_lines = output.strip().split("\n")
            formatted_output = []
            for line in output_lines:
                if line.startswith("x0="):
                    value = line.split("=")[1]
                    formatted_output.append(
                        f"{Back.GREEN}{Fore.BLACK} x0= {Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT} {value} {Style.RESET_ALL}"
                    )
                else:
                    formatted_output.append(line)

            print(f"\n{Back.BLUE}{Fore.WHITE}{Style.BRIGHT} OUTPUT {Style.RESET_ALL}")
            print("\n".join(formatted_output))
        else:
            # Error messages are already formatted
            print(output)

        return output

    except RuntimeError as e:
        print(
            f"{Back.RED}{Fore.WHITE} ERROR {Style.RESET_ALL} {Fore.RED}{str(e)}{Style.RESET_ALL}"
        )
        print(f"{Fore.YELLOW}Try to run:{Style.RESET_ALL}")

        print(
            f"{Fore.CYAN}wasm-objdump.exe ./out/self_compiler.wasm -x{Style.RESET_ALL}"
        )
        print(f"{Fore.CYAN}wasm-validate.exe ./out/self_compiler.wasm{Style.RESET_ALL}")
        print(
            f"{Fore.CYAN}wasm-decompile.exe ./out/self_compiler.wasm -o ./out/self_compiler.wasm.decompiled{Style.RESET_ALL}"
        )


def self_compiler_prebuilt(prebuilt_wasm_path, filepath, inputs):
    """Compile and run a program using a prebuilt self-compiler WASM file.

    This function uses an existing compiled self-compiler WASM file from the
    bootstrapping directory instead of compiling the self-compiler from source.

    Args:
        prebuilt_wasm_path (str): Path to the prebuilt self-compiler WASM file
        filepath (str): Path to the source file to compile
        inputs (list): List of input values for the program

    Returns:
        str: Output from the WASM execution
    """
    print(
        f"\n{Back.MAGENTA}{Fore.WHITE}{Style.BRIGHT} USING PREBUILT SELF-COMPILER {Style.RESET_ALL}"
    )
    print(
        f"{Fore.BLUE}Prebuilt compiler:{Style.RESET_ALL} {Fore.CYAN}{prebuilt_wasm_path}{Style.RESET_ALL}"
    )

    print(
        f"\n{Back.CYAN}{Fore.BLACK}{Style.BRIGHT} RUNNING PREBUILT SELF-COMPILER {Style.RESET_ALL}"
    )
    inputs_self = generate_ascii(filepath)

    output = run_wasm(prebuilt_wasm_path, inputs_self)
    output_backup = output
    if config.print_self_compiler_to_file:
        output_file = sys.path[0] + config.self_compiler_output_file_txt
        output_file_hex = sys.path[0] + config.self_compiler_output_file_hex

        # prepare output
        lines = str(output).splitlines()

        # Extract x0 value for WASM generation
        output_number = 0
        for line in lines:
            if line.startswith("x0="):
                output_number = int(line.split("=")[1])
                break
        output = int(output_number)

        # Generate and display hex output
        output_bytes = hex(output)[2:]
        output_bytes = "00" + str(output_bytes)

        with open(output_file, "w") as f:
            f.write(str(output))

        with open(output_file_hex, "w") as f:
            f.write(output_bytes)

    output = output_backup

    try:
        wasm_file = wasm_to_file(output)
        
        if config.no_execution:
            print(f"{Fore.YELLOW}Execution skipped (no-execution flag is set){Style.RESET_ALL}")
            print(f"{Fore.BLUE}WASM file built at:{Style.RESET_ALL} {Fore.CYAN}{wasm_file}{Style.RESET_ALL}")
            return ""
            
        print(
            f"\n{Back.GREEN}{Fore.BLACK}{Style.BRIGHT} RUNNING COMPILED WASM {Style.RESET_ALL}"
        )
        output = run_wasm(wasm_file, inputs)

        # Check if output contains an error message (has colorama formatting)
        if not (Fore.RED in output or Back.RED in output):
            # Format the output more nicely, highlighting the x0 value
            output_lines = output.strip().split("\n")
            formatted_output = []
            for line in output_lines:
                if line.startswith("x0="):
                    value = line.split("=")[1]
                    formatted_output.append(
                        f"{Back.GREEN}{Fore.BLACK} x0= {Style.RESET_ALL}{Fore.GREEN}{Style.BRIGHT} {value} {Style.RESET_ALL}"
                    )
                else:
                    formatted_output.append(line)

            print(f"\n{Back.BLUE}{Fore.WHITE}{Style.BRIGHT} OUTPUT {Style.RESET_ALL}")
            print("\n".join(formatted_output))
        else:
            # Error messages are already formatted
            print(output)

        return output

    except RuntimeError as e:
        print(
            f"{Back.RED}{Fore.WHITE} ERROR {Style.RESET_ALL} {Fore.RED}{str(e)}{Style.RESET_ALL}"
        )
        print(f"{Fore.YELLOW}Try to run:{Style.RESET_ALL}")

        print(
            f"{Fore.CYAN}wasm-objdump.exe ./out/self_compiler.wasm -x{Style.RESET_ALL}"
        )
        print(f"{Fore.CYAN}wasm-validate.exe ./out/self_compiler.wasm{Style.RESET_ALL}")
        print(
            f"{Fore.CYAN}wasm-decompile.exe ./out/self_compiler.wasm -o ./out/self_compiler.wasm.decompiled{Style.RESET_ALL}"
        )


def generate_ascii(filepath):
    """Generate ASCII hex representation of a file's content.

    If the file is an EWHILE file, it first transpiles it to a WHILE file.
    Reads the file's content and converts each character to its ASCII value,
    creating a hexadecimal string and counting the total number of bytes.
    Used to prepare input for the self-compiler.

    Args:
        filepath (str): Path to the file to process (.while or .ewhile)

    Returns:
        list: A list containing two strings - the ASCII hex input and byte count,
              formatted as ["n1=<hex_value>", "n2=<byte_count>"]
    """
    # Check if the file is an EWHILE file and transpile it first
    if filepath.endswith(".ewhile"):
        print(
            f"{Fore.BLUE}Transpiling EWHILE file:{Style.RESET_ALL} {Fore.CYAN}{filepath}{Style.RESET_ALL}"
        )
        while_filepath = generate_while(filepath)
        filepath = while_filepath

    ascii_code_hex = ""
    num_bytes = 0
    with open(filepath, "r") as file:
        code = file.read()
    for char in code:
        num_bytes += 1
        ascii_value = ord(char.upper())
        ascii_value_hex = hex(ascii_value)[2:]
        if len(ascii_value_hex) < 2:
            ascii_value_hex = "0" + ascii_value_hex
        ascii_code_hex += ascii_value_hex
    print(
        f"{Fore.BLUE}ASCII input size:{Style.RESET_ALL} {Fore.YELLOW}{num_bytes} bytes{Style.RESET_ALL}"
    )

    # print the hex code as ascii strem
    # print_auscii_code(int(ascii_code_hex, 16))

    input_var = "n1=" + str(int(ascii_code_hex, 16))
    bytes_var = "n2=" + str(num_bytes)

    return [input_var, bytes_var]
