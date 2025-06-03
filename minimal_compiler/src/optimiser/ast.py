from minimal_compiler.src.optimiser.ir_classes import * 
from minimal_compiler.src.parser.lexer import tokenize
from minimal_compiler.src.parser.parser import HandParser


class ASTBuilder: # Builder for tree-IR before optimisation
    def visit(self, node): # dynamic dispatch method for visitor pattern
            method_name = "visit" + type(node).__name__
            visitor = getattr(self, method_name, self.generic_visit)
            return visitor(node)
    
    def generic_visit(self, node): # fallback method for nodes without specific visit method
        if hasattr(node, "getText"):
            return node.getText()
        else:
            raise Exception("No visit method for " + type(node).__name__)

    def visitProgContext(self, ctx):
        if ctx.stmt:
            return ProgramNode(self.visit(ctx.stmt))
        else:
            return ProgramNode(EmptyNode("File is empty"))

    def visitAssignmentContext(self, ctx):
        target = ctx.VAR(0).getText()
        source = ctx.VAR(1).getText()
        operator = ctx.op.getText() 
        value = int(ctx.const.getText())
        return AssignmentNode(target, source, operator, value)

    def visitWhileStmtContext(self, ctx):
        condition = self.visit(ctx.condition_ctx)
        body = self.visit(ctx.stmt_ctx)
        return WhileNode(condition, body)

    def visitConditionContext(self, ctx):
        variable = ctx.var_token.getText()
        value = int(ctx.const_token.getText())
        return ConditionNode(variable, value)
    
    def visitPrintContext(self, ctx):
        variable = ctx.var_token.getText()
        return PrintNode(variable)

    def visitSequenceStmtContext(self, ctx): # Important: Flattening of the tree
        left_node = self.visit(ctx.left_stmt)
        right_node = self.visit(ctx.right_stmt)
        
        statements = []
        if isinstance(left_node, SequenceNode):
            statements.extend(left_node.statements)
        else:
            statements.append(left_node)
        
        if isinstance(right_node, SequenceNode):
            statements.extend(right_node.statements)
        else:
            statements.append(right_node)
            
        return SequenceNode(statements)
    
def parse_code(code: str):
    tokens = tokenize(code)
    parser = HandParser(tokens)
    tree = parser.parse_prog()
    return tree

def build_ast(code: str):
    tree = parse_code(code)
    ast_builder = ASTBuilder()  
    return ast_builder.visit(tree)

def unflatten_ast(node: 'Node') -> 'Node':
    if isinstance(node, SequenceNode):
        new_statements = [unflatten_ast(stmt) for stmt in node.statements]
        
        if len(new_statements) <= 1:
            return SequenceNode(new_statements)
        else:
            nested = new_statements[0]
            for stmt in new_statements[1:]:
                nested = SequenceNode([nested, stmt])
            return nested
    else:
        for key, value in node.__dict__.items():
            if hasattr(value, "getText") or isinstance(value, (SequenceNode, ProgramNode)):
                setattr(node, key, unflatten_ast(value))
            elif isinstance(value, list):
                new_list = []
                for item in value:
                    if hasattr(item, "getText") or isinstance(item, (SequenceNode, ProgramNode)):
                        new_list.append(unflatten_ast(item))
                    else:
                        new_list.append(item)
                setattr(node, key, new_list)
        return node

def print_ast_structure(node, indent=0):
    print(' ' * indent + f"{type(node).__name__}:")
    for key, value in node.__dict__.items():
        if hasattr(value, "getText") and not isinstance(value, list):
            print(' ' * (indent + 2) + f"{key}: {value.getText()}")
        elif isinstance(value, (ProgramNode, AssignmentNode, WhileNode, ConditionNode, SequenceNode)):
            print(' ' * (indent + 2) + f"{key}:")
            print_ast_structure(value, indent + 4)
        elif isinstance(value, list) and value and hasattr(value[0], "getText"):
            print(' ' * (indent + 2) + f"{key}: [")
            for item in value:
                print_ast_structure(item, indent + 4)
            print(' ' * (indent + 2) + "]")
        else:
            print(' ' * (indent + 2) + f"{key}: {value}")