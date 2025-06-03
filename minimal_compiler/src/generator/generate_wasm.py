from minimal_compiler.src.generator.visitor import WhileWasmVisitor

def generate(optimised_ast, symbol_table, constant_table):
    visitor = WhileWasmVisitor(symbol_table, constant_table)
    visitor.visit(optimised_ast)
    
    return visitor.get_wasm_code()