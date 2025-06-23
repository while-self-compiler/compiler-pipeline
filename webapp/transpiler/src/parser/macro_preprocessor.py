from antlr4 import InputStream, CommonTokenStream, ParseTreeWalker
from antlr4.TokenStreamRewriter import TokenStreamRewriter
from transpiler.src.parser.error_handling import EWhileLexerErrorListener, EWhileParserErrorListener
from transpiler.src.parser.generated_ewhile_parser.ewhileLexer import ewhileLexer  
from transpiler.src.parser.generated_ewhile_parser.ewhileParser import ewhileParser
from transpiler.src.parser.generated_ewhile_parser.ewhileListener import ewhileListener

class MacroPreprocessorListener(ewhileListener):
    def __init__(self, rewriter: TokenStreamRewriter):
        self.rewriter = rewriter
        self.macros = {}

    def enterMacroStmt(self, ctx):
        macro_name = ctx.VAR().getText()
        # Attention: the macro_body should also have WS tokens (from hidden channel)
        macro_body = self.rewriter.getText("ewhile", ctx.stmt().start.tokenIndex, ctx.stmt().stop.tokenIndex)
        
        self.macros[macro_name] = macro_body
        
        self.rewriter.delete("ewhile", from_idx=ctx.start.tokenIndex, to_idx=ctx.stop.tokenIndex)

    def enterMacroAccessStmt(self, ctx):
        macro_name = ctx.VAR().getText()
        if macro_name in self.macros:
            replacement_text = self.macros[macro_name]
            self.rewriter.replace("ewhile", ctx.start.tokenIndex, ctx.stop.tokenIndex, replacement_text)
        else:
            raise Exception(f"PreprocessorError: Macro `{macro_name}` not defined!")

def preprocess_macros(input_text: str) -> str:
    input_stream = InputStream(input_text)
    lexer = ewhileLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = ewhileParser(token_stream)

    lexer.removeErrorListeners()
    lexer.addErrorListener(EWhileLexerErrorListener())
    parser.removeErrorListeners()
    parser.addErrorListener(EWhileParserErrorListener())

    tree = parser.prog()

    rewriter = TokenStreamRewriter(token_stream)
    listener = MacroPreprocessorListener(rewriter)
    walker = ParseTreeWalker()
    walker.walk(listener, tree)

    preprocessed_text = rewriter.getText("ewhile", 0, len(token_stream.tokens) - 1)
    return preprocessed_text
