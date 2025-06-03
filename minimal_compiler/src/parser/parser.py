class TerminalNode:
    def __init__(self, token):
        self.token = token
        self.text = token.text

    def getText(self):
        return self.token.text

class ProgContext:
    def __init__(self, stmt, eof_token):
        self.stmt = stmt
        self.eof = TerminalNode(eof_token)
        self.children = [stmt, self.eof]

    def getChildCount(self):
        return len(self.children)

    def getText(self):
        return "".join(child.getText() for child in self.children)
    
class PrintContext:
    def __init__(self, print_token, var_token):
        self.print_token = TerminalNode(print_token)
        self.var_token = TerminalNode(var_token)
        self.children = [self.print_token, self.var_token]

    def VAR(self):
        return self.var_token

    def getText(self):
        return "".join(child.getText() for child in self.children)

class AssignmentContext:
    def __init__(self, var1_token, assign_token, var2_token, op_token, const_token):
        self._var_tokens = [TerminalNode(var1_token), TerminalNode(var2_token)]
        self.assign = TerminalNode(assign_token)
        self.op = TerminalNode(op_token)
        self.const = TerminalNode(const_token)
        self.children = [self._var_tokens[0], self.assign, self._var_tokens[1], self.op, self.const]

    def VAR(self, idx=0):
        return self._var_tokens[idx]

    def getText(self):
        return "".join(child.getText() for child in self.children)

class WhileStmtContext:
    def __init__(self, while_token, condition_ctx, do_token, stmt_ctx, end_token):
        self.while_token = TerminalNode(while_token)
        self.condition_ctx = condition_ctx  
        self.do_token = TerminalNode(do_token)
        self.stmt_ctx = stmt_ctx           
        self.end_token = TerminalNode(end_token)
        self.children = [self.while_token, self.condition_ctx, self.do_token, self.stmt_ctx, self.end_token]

    def condition(self):
        return self.condition_ctx

    def getText(self):
        return "".join(child.getText() for child in self.children)

class ConditionContext:
    def __init__(self, var_token, greater_token, const_token):
        self.var_token = TerminalNode(var_token)
        self.greater_token = TerminalNode(greater_token)
        self.const_token = TerminalNode(const_token)
        self.children = [self.var_token, self.greater_token, self.const_token]

    def VAR(self):
        return self.var_token

    def getText(self):
        return "".join(child.getText() for child in self.children)

class SequenceStmtContext:
    def __init__(self, left_stmt, semi_token, right_stmt):
        self.left_stmt = left_stmt
        self.semi = TerminalNode(semi_token)
        self.right_stmt = right_stmt
        self.children = [self.left_stmt, self.semi, self.right_stmt]

    def getText(self):
        return "".join(child.getText() for child in self.children)

class HandParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current = self.tokens[self.pos]

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current = self.tokens[self.pos]
        else:
            self.current = None

    def match(self, expected_type):
        if self.current is None:
            raise SyntaxError(f'ParserException: Unexpected end, expected {expected_type}')
        if self.current.type == expected_type:
            token = self.current
            self.advance()
            return token
        else:
            raise SyntaxError(f'ParserException: Expected {expected_type}, but found {self.current.text} at {self.current.pos}')

    def parse_prog(self):
        stmt = self.parse_stmt()
        eof_token = self.match("EOF")
        return ProgContext(stmt, eof_token)

    def parse_stmt(self):
        if self.current.type == "VAR":
            node = self.parse_assignment()
        elif self.current.type == "WHILE":
            node = self.parse_while()
        elif self.current.type == "PRINT":
            node = self.parse_print()
        else:
            raise SyntaxError(f"ParserException: Unexpected token '{self.current.text}' at {self.current.pos} in stmt")
        
        while self.current and self.current.type == "SEMI":
            semi_token = self.match("SEMI")
            right = self.parse_stmt()
            node = SequenceStmtContext(node, semi_token, right)
        return node
    
    def parse_print(self):
        print_token = self.match("PRINT")
        var_token = self.match("VAR")
        return PrintContext(print_token, var_token)

    def parse_assignment(self):
        var1_token = self.match("VAR")
        assign_token = self.match("ASSIGN")
        var2_token = self.match("VAR")
        if self.current.type == "PLUS":
            op_token = self.match("PLUS")
        elif self.current.type == "MINUS":
            op_token = self.match("MINUS")
        else:
            raise SyntaxError(f"ParserException: Expected '+' or '-' but found '{self.current.text}' at {self.current.pos}")
        const_token = self.match("CONST")
        return AssignmentContext(var1_token, assign_token, var2_token, op_token, const_token)

    def parse_while(self):
        while_token = self.match("WHILE")
        cond_ctx = self.parse_condition()
        do_token = self.match("DO")
        stmt_ctx = self.parse_stmt()
        end_token = self.match("END")
        return WhileStmtContext(while_token, cond_ctx, do_token, stmt_ctx, end_token)

    def parse_condition(self):
        var_token = self.match("VAR")
        greater_token = self.match("GREATER")
        const_token = self.match("CONST")
        return ConditionContext(var_token, greater_token, const_token)

class SimpleParseTreeWalker:
    def walk(self, listener, node):
        method_name = "enter" + type(node).__name__.replace("Context", "")
        if hasattr(listener, method_name):
            getattr(listener, method_name)(node)

        if hasattr(node, "children"):
            for child in node.children:
                self.walk(listener, child)
