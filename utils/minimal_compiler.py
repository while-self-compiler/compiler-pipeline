import sys
import os
from colorama import Fore, Back, Style
from utils.wasm_runner import run_wasm
from transpiler.transpile import generate_while
from minimal_compiler.src.parser.create_parsetree import create_cached_parsetree
from minimal_compiler.src.generator.generate_wasm import generate
from minimal_compiler.src.optimiser.ast import ASTBuilder
from minimal_compiler.src.optimiser.base_optimiser import OptimiserManager
from minimal_compiler.src.optimiser.optimisers.structural_tree_pattern_matching import (
    StructuralTreePatternMatchingOptimiser,
)
from utils import config


def minimal_compiler(filepath, inputs):
    """Compile a WHILE/EWHILE program using the minimal compiler and run it.

    Compiles the specified file to WebAssembly and executes it with the provided inputs.
    Formats and displays the output with syntax highlighting.
    If config.no_execution is True, skips the execution step and returns an empty string.

    Args:
        filepath (str): Path to the source file (.while or .ewhile)
        inputs (list): List of input values for the program

    Returns:
        str: Output from the WASM execution or empty string if execution is skipped
    """
    print(
        f"{Back.BLUE}{Fore.WHITE}{Style.BRIGHT} COMPILING WITH MINIMAL COMPILER {Style.RESET_ALL}"
    )
    wasm_filepath = compile_to_wasm(filepath)
    
    if config.no_execution:
        print(f"{Fore.YELLOW}Execution skipped (no-execution flag is set){Style.RESET_ALL}")
        print(f"{Fore.BLUE}WASM file built at:{Style.RESET_ALL} {Fore.CYAN}{wasm_filepath}{Style.RESET_ALL}")
        return ""
        
    output = run_wasm(wasm_filepath, inputs)

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


def compile_to_wasm(filepath):
    """Compile a WHILE/EWHILE file to WebAssembly.

    If the file is an EWHILE file, it first generates a WHILE file before compilation.
    Processes the file through the appropriate compilation steps to generate a WASM file.

    Args:
        filepath (str): Path to the source file (.while or .ewhile)

    Returns:
        str: Path to the compiled WebAssembly file
    """
    if filepath.endswith(".ewhile"):
        while_filepath = generate_while(filepath)
        # read while file and convert to hex ascii numbers
        with open(while_filepath, "r") as file:
            code = file.read()
        ascii_code_hex = ""
        num_bytes = 0
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

    else:
        while_filepath = filepath
    wat_filepath = generate_wat(while_filepath)
    wasm_filepath = generate_wasm(wat_filepath)
    return wasm_filepath


def generate_wat(filepath):
    """Generate a WebAssembly Text (WAT) file from a WHILE file.

    Parses the WHILE file, builds an abstract syntax tree, optionally applies optimizations,
    and generates a WAT file from the processed tree.

    Args:
        filepath (str): Path to the WHILE file

    Returns:
        str: Path to the generated WAT file
    """
    # Clear the parse tree cache to ensure a fresh compilation process
    create_cached_parsetree.cache_clear()

    with open(filepath, "r") as file:
        code = file.read()
    tree, symbol_table, constant_table = create_cached_parsetree(code)

    # optimise the tree
    ast_builder = ASTBuilder()  # Using a custom ast as an intermediate representation
    ast = ast_builder.visit(tree)

    # print_ast_structure(ast)

    if not config.no_optimisation:
        optimiser_manager = OptimiserManager(
            # TODO: Evtl. add rerun or reordering optimiser
            # Also copy propagation possible with x0 = x1 + 0 to x0 = copy(x1)
            [
                StructuralTreePatternMatchingOptimiser(),
            ]
        )
        optimised_ast = optimiser_manager.optimise(ast)
    else:
        print(f"{Fore.YELLOW}No optimisation applied{Style.RESET_ALL}")
        optimised_ast = ast

    # print_ast_structure(optimised_ast)

    wat = generate(optimised_ast, symbol_table, constant_table)
    filename = os.path.basename(filepath)
    out_dir = sys.path[0] + "/out"
    os.makedirs(out_dir, exist_ok=True)
    wat_filepath = out_dir + "/" + filename.replace(".while", ".wat")
    with open(wat_filepath, "w") as file:
        file.write(wat)

    print(
        f"{Fore.BLUE}Compiled wat file:{Style.RESET_ALL} {Fore.CYAN}{wat_filepath}{Style.RESET_ALL}"
    )
    return wat_filepath


def generate_wasm(filepath):
    """Generate a WebAssembly binary file from a WAT file.

    Converts a WebAssembly Text (WAT) file to a WebAssembly binary (WASM) file
    using the wat2wasm external tool.

    Args:
        filepath (str): Path to the WAT file

    Returns:
        str: Path to the generated WASM file
    """
    wasm_filepath = filepath.replace(".wat", ".wasm")
    os.system(f"wat2wasm {filepath} -o {wasm_filepath}")

    print(
        f"{Fore.BLUE}Compiled wasm file:{Style.RESET_ALL} {Fore.CYAN}{wasm_filepath}{Style.RESET_ALL}"
    )
    return wasm_filepath
