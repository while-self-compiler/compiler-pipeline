from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener


class EWhileLexerErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        error_message = f"LexerError: At line {line}, column {column}: {msg}"
        raise Exception(error_message)

class EWhileParserErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):        
        error_message = f"SyntaxError: At line {line}, column {column}: {msg}"
        if offendingSymbol:
            error_message += f" (Found: '{offendingSymbol.text}')"
        raise Exception(error_message)