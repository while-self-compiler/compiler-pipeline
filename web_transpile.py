from transpiler.src.parser.create_parsetree import create_cached_parsetree

from transpiler.src.generator.generate_while import generate


def transpile_to_while(source_code: str) -> str:
    create_cached_parsetree.cache_clear()

    tree, symbol_table_manager = create_cached_parsetree(source_code)

    whi = generate(tree, symbol_table_manager)

    return whi


def main():
    import sys

    if len(sys.argv) > 1:
        result = transpile_to_while(sys.argv[1])

        print(result)

    else:
        print("Error")


if __name__ == "__main__":
    main()
