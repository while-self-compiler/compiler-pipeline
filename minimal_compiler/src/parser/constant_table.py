from minimal_compiler.src.parser.parser import AssignmentContext, ConditionContext

class ConstantTable:
    def __init__(self):
        self.table = {}
        self.index = 0

    def add(self, value):
        if value not in self.table:
            rep_name = f"constant_{self.index}"
            self.table[value] = rep_name
            self.index += 1

        return self.table[value]

    def get(self, value):
        return self.table[value]
    
    def get_full_table(self):
        return self.table
    
    def __str__(self):
        return str(self.table)
    

class ConstantTableBuilder:
    def __init__(self):
        self.constant_table = ConstantTable()

    def enterAssignment(self, ctx: AssignmentContext):
        if hasattr(ctx, "const") and ctx.const is not None:
            const_value = int(ctx.const.getText())
            self.constant_table.add(const_value)

    def enterCondition(self, ctx: ConditionContext):
        if hasattr(ctx, "const_token") and ctx.const_token is not None:
            const_value = int(ctx.const_token.getText())
            self.constant_table.add(const_value)

    def get_constant_table(self):
        return self.constant_table