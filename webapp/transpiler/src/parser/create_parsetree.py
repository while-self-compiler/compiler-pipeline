from antlr4 import *
from transpiler.src.parser.generated_ewhile_parser.ewhileLexer import ewhileLexer  
from transpiler.src.parser.generated_ewhile_parser.ewhileParser import ewhileParser
from transpiler.src.parser.symbol_table import SymbolTableBuilder, SymbolTableManager
from transpiler.src.parser.error_handling import EWhileParserErrorListener, EWhileLexerErrorListener
from functools import lru_cache
from transpiler.src.parser.macro_preprocessor import preprocess_macros


@lru_cache(maxsize=128)
def create_cached_parsetree(input):
    """
    This function creates a parse tree from the input string.
    It uses a lru cache decorator to avoid re-parsing the same input string.

    Parameters:
    input (str): The input string to parse.
    """
    preprocessed_input = preprocess_macros(input)
    input_stream = InputStream(preprocessed_input)

    lexer = ewhileLexer(input_stream)
    token_stream = CommonTokenStream(lexer)

    parser = ewhileParser(token_stream)

    lexer.removeErrorListeners()
    lexer.addErrorListener(EWhileLexerErrorListener())
    parser.removeErrorListeners()
    parser.addErrorListener(EWhileParserErrorListener())

    try:
        tree = parser.prog() # start rule is prog
    except Exception as e:
        raise e
    
    # symboltable
    symbol_table_builder = SymbolTableBuilder()
    walker = ParseTreeWalker()
    walker.walk(symbol_table_builder, tree)
    
    return tree, SymbolTableManager(symbol_table_builder.get_global_scope())