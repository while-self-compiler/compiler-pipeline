import sys
import os
from utils import config
from minimal_compiler.src.parser.create_parsetree import (
    create_cached_parsetree as create_cached_parsetree_minimal_compiler,
)
from minimal_compiler.src.generator.generate_wasm import generate as generate_wasm
from minimal_compiler.src.optimiser.ast import ASTBuilder
from minimal_compiler.src.optimiser.base_optimiser import OptimiserManager
from minimal_compiler.src.optimiser.optimisers.structural_tree_pattern_matching import (
    StructuralTreePatternMatchingOptimiser,
)

from transpiler.src.parser.create_parsetree import (
    create_cached_parsetree as create_cached_parsetree_transpiler,
)
from transpiler.src.generator.generate_while import generate as generate_while

# Set use_gmp to False for unit tests to use the original bigint library
config.use_gmp = False


def compile_and_run(code: str, name: str, args_list) -> int:
    # create temp folder if not exists
    if not os.path.exists("./transpiler/src/tests/unittests/temp/"):
        os.makedirs("./transpiler/src/tests/unittests/temp/")

    # ewhile to while
    code = toWhile(code, "./transpiler/src/tests/unittests/temp/" + name + ".ewhile")

    # while to wat
    toWat(code, "./transpiler/src/tests/unittests/temp/" + name + ".wat")

    # wat to wasm
    import subprocess

    subprocess.run(
        [
            "wat2wasm",
            "./transpiler/src/tests/unittests/temp/" + name + ".wat",
            "-o",
            "./transpiler/src/tests/unittests/temp/" + name + ".wasm",
        ]
    )

    # wasm to result via node
    results = []
    for args in args_list:
        args_string = ""
        if args is not None:
            for key, value in args.items():
                args_string += f"{key}={value} "

        result = subprocess.run(
            [
                "node",
                "./wasm_runner/wasm_runner.js",
                "./transpiler/src/tests/unittests/temp/" + name + ".wasm",
                args_string,
            ],
            capture_output=True,
        ).stdout.decode("utf-8")

        for line in result.splitlines():
            if line.startswith("x0="):
                result = line[3:].strip()
                break

        results.append(int(result))

    return results


def toWhile(input_data=None, file_path=None):
    if input_data is None:
        try:
            if not os.path.isabs(file_path):
                file_path = os.path.join(os.getcwd(), file_path)

            with open(file_path, "r") as file:
                code = file.read()

            tree, symbol_table_manager = create_cached_parsetree_transpiler(code)

            return generate_while(tree, symbol_table_manager)
        except Exception as e:
            print(e)
    else:
        try:
            code = input_data
            tree, symbol_table_manager = create_cached_parsetree_transpiler(code)

            return generate_while(tree, symbol_table_manager)
        except Exception as e:
            print(e)


def toWat(input_data=None, wasm_file_path=None):
    try:
        code = input_data
        tree, symbol_table, constant_table = create_cached_parsetree_minimal_compiler(
            code
        )

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

        wasm = generate_wasm(optimised_ast, symbol_table, constant_table)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

    with open(wasm_file_path, "w") as file:
        file.write(wasm)
