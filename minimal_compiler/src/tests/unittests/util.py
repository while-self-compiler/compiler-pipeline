import sys
import os
from minimal_compiler.src.parser.create_parsetree import create_cached_parsetree
from minimal_compiler.src.generator.generate_wasm import generate
from minimal_compiler.src.optimiser.ast import ASTBuilder
from minimal_compiler.src.optimiser.base_optimiser import OptimiserManager
from minimal_compiler.src.optimiser.optimisers.structural_tree_pattern_matching import (
    StructuralTreePatternMatchingOptimiser,
)
from utils import config


def compile_and_run(code: str, name: str, args: dict = None) -> int:
    # Force unit tests to use the original bigint library instead of GMP
    config.use_gmp = False

    # create temp folder if not exists
    if not os.path.exists("./minimal_compiler/src/tests/unittests/temp/"):
        os.makedirs("./minimal_compiler/src/tests/unittests/temp/")

    # while to wat
    main(code, "./minimal_compiler/src/tests/unittests/temp/" + name + ".while")

    # wat to wasm
    import subprocess

    subprocess.run(
        [
            "wat2wasm",
            "./minimal_compiler/src/tests/unittests/temp/" + name + ".wat",
            "-o",
            "./minimal_compiler/src/tests/unittests/temp/" + name + ".wasm",
        ]
    )

    # wasm to result via node
    args_string = ""
    if args is not None:
        for key, value in args.items():
            args_string += f"{key}={value} "

    result = subprocess.run(
        [
            "node",
            "./wasm_runner/wasm_runner.js",
            "./minimal_compiler/src/tests/unittests/temp/" + name + ".wasm",
            args_string,
        ],
        capture_output=True,
    ).stdout.decode("utf-8")

    for line in result.splitlines():
        if line.startswith("x0="):
            result = line[3:].strip()
            break

    return int(result)


def main(input_data=None, file_path=None):
    if input_data is None:
        if len(sys.argv) != 2:
            print(
                "Error: Invalid number of arguments. Please provide a file.",
                file=sys.stderr,
            )
            sys.exit(1)

        file_path = sys.argv[1]

        try:
            with open(file_path, "r") as file:
                code = file.read()

            tree, symbol_table, constant_table = create_cached_parsetree(code)

            # optimise the tree
            ast_builder = (
                ASTBuilder()
            )  # Using a custom ast as an intermediate representation
            ast = ast_builder.visit(tree)

            optimiser_manager = OptimiserManager(
                # TODO: Evtl. add rerun or reordering optimiser
                [
                    StructuralTreePatternMatchingOptimiser(),
                ]
            )
            optimised_ast = optimiser_manager.optimise(ast)

            wasm = generate(optimised_ast, symbol_table, constant_table)
        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            sys.exit(1)

        wasm_file_path = file_path.replace(".while", ".wat")
        with open(wasm_file_path, "w") as file:
            file.write(wasm)
    else:
        try:
            code = input_data
            tree, symbol_table, constant_table = create_cached_parsetree(code)

            # optimise the tree
            ast_builder = (
                ASTBuilder()
            )  # Using a custom ast as an intermediate representation
            ast = ast_builder.visit(tree)

            optimiser_manager = OptimiserManager(
                # TODO: Evtl. add rerun or reordering optimiser
                [
                    StructuralTreePatternMatchingOptimiser(),
                ]
            )
            optimised_ast = optimiser_manager.optimise(ast)

            wasm = generate(optimised_ast, symbol_table, constant_table)
        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            sys.exit(1)

        wasm_file_path = file_path.replace(".while", ".wat")
        with open(wasm_file_path, "w") as file:
            file.write(wasm)
