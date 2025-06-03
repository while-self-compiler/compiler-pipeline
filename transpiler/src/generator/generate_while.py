from transpiler.src.generator.visitor import EWhileWhileVisitor

def generate(tree, symbol_table_manager):
    visitor = EWhileWhileVisitor(symbol_table_manager)
    visitor.visit(tree)
    
    return visitor.get_output()