class Node:
    def accept(self, visitor):
        pass  
    
    def __str__(self):
        return "Node"

class ProgramNode(Node):
    def __init__(self, stmt):
        self.stmt = stmt

    def accept(self, visitor):
        return visitor.visitProg(self) 

    def __str__(self):
        return f"ProgramNode({self.stmt})"

class AssignmentNode(Node):
    def __init__(self, target, source, operator, value):
        self.target = target
        self.source = source
        self.operator = operator
        self.value = value

    def accept(self, visitor):
        return visitor.visitAssignmentStmt(self)

    def __str__(self):
        return f"AssignmentNode({self.target}, {self.source}, {self.operator}, {self.value})"
    
class PrintNode(Node):
    def __init__(self, variable):
        self.variable = variable

    def accept(self, visitor):
        return visitor.visitPrintStmt(self)

    def __str__(self):
        return f"PrintNode({self.variable})"

class WhileNode(Node):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def accept(self, visitor):
        return visitor.visitWhileStmt(self)

    def __str__(self):
        return f"WhileNode({self.condition}, {self.body})"

class ConditionNode(Node):
    def __init__(self, variable, value):
        self.variable = variable
        self.value = value

    def accept(self, visitor):
        return visitor.visitCondition(self)

    def __str__(self):
        return f"ConditionNode({self.variable}, {self.value})"

class SequenceNode(Node):
    def __init__(self, statements):
        self.statements = statements

    def accept(self, visitor):
        return visitor.visitSequenceStmt(self)

    def __str__(self):
        return f"SequenceNode({self.statements})"
    
class AssignmentNodeTwoVar(Node):
    def __init__(self, target, source, operator, x_k, c_2, c_1): 
        self.target = target
        self.source = source
        self.operator = operator
        self.x_k = x_k
        self.c_2 = c_2
        self.c_1 = c_1

    def accept(self, visitor):
        return visitor.visitAssignmentTwoVarStmt(self)

    def __str__(self):
        return f"AssignmentNodeTwoVar({self.target}, {self.source}, {self.operator}, {self.x_k}, {self.c_2}, {self.c_1})"
    
class EmptyNode(Node):
    def __init__(self, reason):
        self.reason = reason

    def accept(self, visitor):
        return visitor.visitEmptyNode(self)

    def __str__(self):
        return "EmptyNode"