#!/usr/bin/env python3
import sys
import os
from transpiler.src.parser.create_parsetree import create_cached_parsetree
from transpiler.src.generator.generate_while import generate


def main():
    try:
        filepath = sys.argv[1]
        if not os.path.isabs(filepath):
            filepath = os.path.join(os.getcwd(), filepath)

        while_file = generate_while(filepath)
    except Exception as e:
        print(e)


def generate_while(filepath):
    # Clear the parse tree cache to ensure a fresh transpilation process
    create_cached_parsetree.cache_clear()
    
    with open(filepath, "r") as file:
        code = file.read()

    tree, symbol_table_manager = create_cached_parsetree(code)

    whi = generate(tree, symbol_table_manager)

    filename = os.path.basename(filepath)
    out_dir = sys.path[0] + "/out"
    os.makedirs(out_dir, exist_ok=True)
    while_filepath = out_dir + "/" + filename.replace(".ewhile", ".while")
    with open(while_filepath, "w") as file:
        file.write(whi)

    print(f"Generated while file: {while_filepath}")

    return while_filepath


if __name__ == "__main__":
    main()
