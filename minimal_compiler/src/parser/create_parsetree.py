from minimal_compiler.src.parser.symbol_table import SymbolTableBuilder
from minimal_compiler.src.parser.constant_table import ConstantTableBuilder
from functools import lru_cache
from minimal_compiler.src.parser.lexer import tokenize
from minimal_compiler.src.parser.parser import HandParser, SimpleParseTreeWalker


@lru_cache(maxsize=128)
def create_cached_parsetree(input):
    """
    This function creates a parse tree from the input string.
    It uses a lru cache decorator to avoid re-parsing the same input string.

    The lexer and parser are written per hand because of performance reasons.

    Parameters:
    input (str): The input string to parse.
    """
    
    tokens = tokenize(input)
    
    parser = HandParser(tokens)
    tree = parser.parse_prog()

    # symboltable
    symbol_table_builder = SymbolTableBuilder()
    walker = SimpleParseTreeWalker()
    walker.walk(symbol_table_builder, tree)
    
    # constant table
    constant_table_builder = ConstantTableBuilder()
    walker.walk(constant_table_builder, tree)
    
    return tree, symbol_table_builder.get_symbol_table(), constant_table_builder.get_constant_table()