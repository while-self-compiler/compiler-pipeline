#!/usr/bin/env python3
import sys
from colorama import Fore, Back, Style, init
from utils.utils import to_absolute_path
from utils.minimal_compiler import minimal_compiler
from utils.wasm_tools import (
    print_wasm_as_hex,
    hex_to_wasm_bytes,
    wasm_bytes_to_wat,
)
from utils.self_compiler import self_compiler, self_compiler_prebuilt
from utils.self_lexer_debug import self_lexer_debug
from utils import config


# Initialize colorama
init(autoreset=True)


def main():
    """Main entry point for the WHILE language compiler and runner.
    Parses command line arguments, sets up the environment,
    and delegates to the appropriate compiler based on the flags provided.
    """
    sys.setrecursionlimit(1000000)  # needed because of deep ANTLR ParseTree structure
    sys.set_int_max_str_digits(100000000)  # needed for large number inputs

    filepath = ""
    flags = []
    prebuilt_compiler = None

    inputs = []

    for arg in sys.argv[1:]:
        if arg.startswith("--"):
            flags.append(arg[2:])
        elif arg.endswith(".ewhile") or arg.endswith(".while"):
            filepath = arg
        elif arg.endswith(".wasm"):
            prebuilt_compiler = arg
        else:
            inputs.append(arg)

    filepath = to_absolute_path(filepath)

    try:
        if "full-hex" in flags:
            config.is_full_hex = True

        if "no-capture" in flags:
            config.is_capture_output = False

        if "self-lexer-input" in flags:
            config.is_self_lexer = True

        if "no-optimisation" in flags:
            config.no_optimisation = True

        if "no-gmp" in flags:
            config.use_gmp = False
            
        if "no-execution" in flags:
            config.no_execution = True

        output = ""

        if prebuilt_compiler:
            output = self_compiler_prebuilt(prebuilt_compiler, filepath, inputs)
        elif "self" in flags:
            output = self_compiler(filepath, inputs)
        elif "lexer" in flags:
            output = self_lexer_debug(filepath, inputs)
        else:
            output = minimal_compiler(filepath, inputs)

        if "hex" in flags:
            print_wasm_as_hex(output)
        if "wat" in flags:
            print(wasm_bytes_to_wat(hex_to_wasm_bytes(print_wasm_as_hex(output))))

    except Exception as e:
        print(
            f"{Back.RED}{Fore.WHITE} ERROR {Style.RESET_ALL} {Fore.RED}{str(e)}{Style.RESET_ALL}"
        )


if __name__ == "__main__":
    main()
