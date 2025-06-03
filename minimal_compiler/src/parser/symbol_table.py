from minimal_compiler.src.parser.parser import AssignmentContext, WhileStmtContext

class SymbolTable:
    def __init__(self):
        self.variables = {}  
        self.next_address = 0 

    def add_variable(self, name):
        if name not in self.variables:
            self.variables[name] = {"used": False, "assigned": False, "type": "i32"} # TODO: Change dynamic alocation of size

    def mark_used(self, name):
        if name in self.variables:
            self.variables[name]["used"] = True

    def mark_assigned(self, name):
        if name in self.variables:
            self.variables[name]["assigned"] = True

    def get_type(self, name):
        if name in self.variables:
            return self.variables[name]["type"]
        return "i32" # default type
    
    def set_type(self, name, type):
        if name in self.variables:
            self.variables[name]["type"] = type

    def is_used(self, name):
        if name in self.variables:
            return self.variables[name]["used"]
        return False
    
    def is_assigned(self, name):
        if name in self.variables:
            return self.variables[name]["assigned"]
        return False


class SymbolTableBuilder:
    def __init__(self):
        self.symbol_table = SymbolTable()

    def enterAssignment(self, ctx: AssignmentContext):
        var_name = ctx.VAR(0).getText()
        used_var_name = ctx.VAR(1).getText()    

        self.symbol_table.add_variable(var_name) # target variable
        self.symbol_table.add_variable(used_var_name) # source variable
        self.symbol_table.mark_assigned(var_name)
        self.symbol_table.mark_used(used_var_name)

    def enterPrintStmt(self, ctx):
        var_name = ctx.VAR().getText()
        self.symbol_table.add_variable(var_name)
        self.symbol_table.mark_used(var_name)

    def enterWhileStmt(self, ctx: WhileStmtContext):
        cond_var = ctx.condition().VAR().getText()
        self.symbol_table.add_variable(cond_var)
        self.symbol_table.mark_used(cond_var)        

    def get_symbol_table(self):
        return self.symbol_table