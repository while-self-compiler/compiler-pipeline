from transpiler.src.parser.symbol_table import SymbolTableManager
from transpiler.src.parser.generated_ewhile_parser.ewhileParser import ewhileParser
from transpiler.src.parser.generated_ewhile_parser.ewhileVisitor import ewhileVisitor
from transpiler.src.generator.template_loader import TemplateManager
from transpiler.config import TEMP_VARIABLE_REUSE_SAME_SCOPE


class EWhileWhileVisitor(ewhileVisitor):
    # TODO: Make rules for templates, to define if a template variable needs to be reset or not (i.e. some variables get reseted automatically, because of a while induction variable)
    # TODO: TemplateManager should have access to create new temp variables, so it can just fill out the rest of the template (=> create a new temp var template)

    def __init__(self, scope_manager: SymbolTableManager):
        self.scope_manager = scope_manager
        self.scope_manager.prepare()
        self.global_zero_constant = self.scope_manager.get_constant_zero()

        self.output = ""
        self.template_manager = TemplateManager(self.global_zero_constant)

    def get_output(self):
        return self.output

    def visitProg(self, ctx: ewhileParser.ProgContext):
        if ctx.stmt() is not None:
            self.output = self.visit(ctx.stmt())
        return self.output

    def visitAssignmentStmt(self, ctx: ewhileParser.AssignmentStmtContext):
        return self.visit(ctx.assignment())
    
    def visitMacroAccessStmt(self, ctx):
        # This is an error: Macros should be preprocessed before visiting the parse tree.

        macro_name = ctx.VAR().getText()
        raise Exception(f"PreprocessorError: Macro {macro_name} is not defined.\nPlease define the macro before using it.")
    
    def visitMacroStmt(self, ctx):
        # This is an error: Macros should be preprocessed before visiting the parse tree.

        macro_name = ctx.VAR().getText()
        raise Exception(f"PreprocessorError: Macro {macro_name} is defined but not replaces (there is probably a bug in the preprocessor).")

    def visitAssignment(self, ctx: ewhileParser.AssignmentContext):
        target = ctx.varTarget.text
        target_transpiled = self.scope_manager.get_current_scope().get_transpiled_name(target) or target
        isTemplateAvailable, op, variables, temps = self.visit(ctx.expression())

        if isTemplateAvailable:
            template_temps = ""

            for i, temp in enumerate(temps):
                if i == len(temps) - 1:
                    template_temps += self.template_manager.prepare_template("reset", [temp])
                else:
                    template_temps += self.template_manager.prepare_template("reset", [temp], semicolon=True)
            
            if TEMP_VARIABLE_REUSE_SAME_SCOPE and temps and len(temps) > 0:
                self.scope_manager.put_list_of_temp_variables_in_pool(temps)
          
            if len(temps) > 0:
                return self.template_manager.prepare_template(op, [target_transpiled] + variables + temps, semicolon=True) + template_temps
            else:
                return self.template_manager.prepare_template(op, [target_transpiled] + variables + temps)
        else:
            num_2 = 0
            if len(variables) > 1:
                num_2 = variables[1]

            expr_str = f"{variables[0]} {op} {num_2}"
            return f"{target_transpiled} = {expr_str}"
        
    def visitDeclarationStmt(self, ctx):
        return self.visit(ctx.declaration())
    
    def visitPrintStmt(self, ctx):
        value = ctx.VAR().getText()
        if not value:
            value = ctx.X_VAR().getText()

        value_transpiled = self.scope_manager.get_current_scope().get_transpiled_name(value)

        if not value_transpiled:
            raise Exception(f"SemanticException: Print Variable {value} is not defined.")

        return ctx.PRINT().getText() + " " + value_transpiled
    
    def visitDeclaration(self, ctx: ewhileParser.DeclarationContext):
        variables = []

        i = 0
        while ctx.VAR(i) is not None:
            variables.append(ctx.VAR(i).getText())
            i += 1

        variables_transpiled = [self.scope_manager.get_current_scope().get_transpiled_name(var) for var in variables]
        template = ""

        for i, var in enumerate(variables_transpiled):
            if i == len(variables_transpiled) - 1:
                template += self.template_manager.prepare_template("declaration", [var])
            else:
                template += self.template_manager.prepare_template("declaration", [var], semicolon=True)

        return template

    def visitExpression(self, ctx: ewhileParser.ExpressionContext): # TODO: Check isTemplateAvailable directly in the TemplateManager
        left = ctx.left.text
        left_mapped = self.scope_manager.get_current_scope().get_transpiled_name(left) if not left.isdigit() else left

        if ctx.op is None: # copy operation
            if left.isdigit():
                return (False, '+', [self.global_zero_constant, left_mapped], [])
            else: 
                return (False, '+', [left_mapped, '0'], [])
        else:
            if left.isdigit():
                raise Exception("SyntaxError: Left operand of an expression with an operation must be a variable.")

            op = ctx.op.text

            if op == '+':
                right = ctx.right.text
                if right.isdigit():
                    return (False, '+', [left_mapped, right], [])
                else:
                    right_mapped = self.scope_manager.get_current_scope().get_transpiled_name(right) or right
                    return (True, "add", [left_mapped, right_mapped], [self.scope_manager.get_temp_variable()])
            elif op == '-':
                right = ctx.right.text
                if right.isdigit():
                    return (False, '-', [left_mapped, right], [])
                else:
                    right_mapped = self.scope_manager.get_current_scope().get_transpiled_name(right) or right
                    return (True, "sub", [left_mapped, right_mapped], [self.scope_manager.get_temp_variable()])
            elif op == '*':
                right = ctx.right.text
                if right.isdigit():
                    return (True, "mul_constant", [left_mapped, right], [self.scope_manager.get_temp_variable()])
                else:
                    right_mapped = self.scope_manager.get_current_scope().get_transpiled_name(right) or right
                    return (True, "mul", [left_mapped, right_mapped], [self.scope_manager.get_temp_variable(), self.scope_manager.get_temp_variable(), self.scope_manager.get_temp_variable()])
            elif op == '/':
                right = ctx.right.text
                if right.isdigit():
                    return (True, "div_constant", [left_mapped, right], [self.scope_manager.get_temp_variable()])
                else:
                    right_mapped = self.scope_manager.get_current_scope().get_transpiled_name(right) or right
                    return (True, "div", [left_mapped, right_mapped], [self.scope_manager.get_temp_variable(), self.scope_manager.get_temp_variable(), self.scope_manager.get_temp_variable(), self.scope_manager.get_temp_variable()])
            elif op == '<<':
                right = ctx.right.text
                if right.isdigit():
                    raise Exception("SyntaxError: Left shift only supported with variables.")
                else:
                    right_mapped = self.scope_manager.get_current_scope().get_transpiled_name(right) or right
                    return (True, "bit_shift_left", [left_mapped, right_mapped], [self.scope_manager.get_temp_variable(), self.scope_manager.get_temp_variable(), self.scope_manager.get_temp_variable(), self.scope_manager.get_temp_variable(), self.scope_manager.get_temp_variable(), self.scope_manager.get_temp_variable(), self.scope_manager.get_temp_variable(), self.scope_manager.get_temp_variable()])
            elif op == '>>':
                right = ctx.right.text
                if right.isdigit():
                    raise Exception("SyntaxError: Right shift only supported with variables.")
                else:
                    right_mapped = self.scope_manager.get_current_scope().get_transpiled_name(right) or right

                    temp_1 = self.scope_manager.get_temp_variable()
                    temp_2 = self.scope_manager.get_temp_variable()
                    temp_3 = self.scope_manager.get_temp_variable()
                    temp_4 = self.scope_manager.get_temp_variable()
                    temp_5 = self.scope_manager.get_temp_variable()
                    temp_6 = self.scope_manager.get_temp_variable()

                    return (True, "bit_shift_right", [left_mapped, right_mapped], [temp_1, temp_2, temp_3, temp_4, temp_5, temp_6])
            elif op == '%':
                right = ctx.right.text
                if right.isdigit():
                    raise Exception("SyntaxError: Modulo only supported with variables.")
                else:
                    right_mapped = self.scope_manager.get_current_scope().get_transpiled_name(right) or right
                    return (True, "modulo", [left_mapped, right_mapped], [self.scope_manager.get_temp_variable(), self.scope_manager.get_temp_variable()])
            elif op == '^?':
                right = ctx.right.text
                if right.isdigit():
                    raise Exception("SyntaxError: MAX only supported with variables.")
                else:
                    right_mapped = self.scope_manager.get_current_scope().get_transpiled_name(right) or right
                    return (True, "max", [left_mapped, right_mapped], [self.scope_manager.get_temp_variable(), self.scope_manager.get_temp_variable()])
            elif op == 'v?':
                right = ctx.right.text
                if right.isdigit():
                    raise Exception("SyntaxError: MIN only supported with variables.")
                else:
                    right_mapped = self.scope_manager.get_current_scope().get_transpiled_name(right) or right
                    return (True, "min", [left_mapped, right_mapped], [self.scope_manager.get_temp_variable(), self.scope_manager.get_temp_variable()])
            else:
                raise Exception(f"SyntaxError: Unsupported operator: {op}")    
            
    def visitWhileStmt(self, ctx: ewhileParser.WhileStmtContext):
        condition_type, cond_temps, blocks = self.visit(ctx.condition())
        cond_value = cond_temps[2]

        condition_with_semicolon = self.template_manager.prepare_template(
            condition_type, cond_temps, blocks, semicolon=True
        )
        condition_without_semicolon = self.template_manager.prepare_template(
            condition_type, cond_temps, blocks, semicolon=False
        )

        cond_resets = ""
        for i, t in enumerate(cond_temps):
            is_last = (i == len(cond_temps) - 1)
            cond_resets += self.template_manager.prepare_template(
                "reset",
                [t],
                semicolon=not is_last
            )

        self.scope_manager.go_next_scope()
        body_code = self.visit(ctx.stmt())
        self.scope_manager.go_previous_scope()

        code = self.template_manager.prepare_template(
            "while",
            [cond_value],
            [condition_with_semicolon, body_code, condition_without_semicolon],
            semicolon=True
        )

        code += cond_resets

        if TEMP_VARIABLE_REUSE_SAME_SCOPE:
            self.scope_manager.put_list_of_temp_variables_in_pool(cond_temps)

        return code

    
    def visitCondition(self, ctx: ewhileParser.ConditionContext):
        op = ctx.op.text

        isTemplateAvailableLeft, opLeft, variablesLeft, tempsLeft = self.visit(ctx.expression(0))
        isTemplateAvailableRight, opRight, variablesRight, tempsRight = self.visit(ctx.expression(1))

        X = self.scope_manager.get_temp_variable()
        Y = self.scope_manager.get_temp_variable()
        cond_value = self.scope_manager.get_temp_variable()
        
        input_variables = [X, Y, cond_value]

        block_left = ""
        block_right = ""

        if isTemplateAvailableLeft:
            template_temps = ""

            for i, temp in enumerate(tempsLeft):
                template_temps += self.template_manager.prepare_template("reset", [temp], semicolon=True)
    
            block_left = self.template_manager.prepare_template(opLeft, [X] + variablesLeft + tempsLeft, semicolon=True) + template_temps
        else:
            num_2 = 0
            if len(variablesLeft) > 1:
                num_2 = variablesLeft[1]
            expr_str_left = f"{variablesLeft[0]} {opLeft} {num_2}"
            block_left = f"{X} = {expr_str_left};"
        
        if isTemplateAvailableRight:
            template_temps = ""

            for i, temp in enumerate(tempsRight):
                template_temps += self.template_manager.prepare_template("reset", [temp], semicolon=True)

            block_right = self.template_manager.prepare_template(opRight, [Y] + variablesRight + tempsRight, semicolon=True) + template_temps
        else:
            num_2 = 0
            if len(variablesRight) > 1:
                num_2 = variablesRight[1]

            expr_str_right = f"{variablesRight[0]} {opRight} {num_2}"
            block_right = f"{Y} = {expr_str_right};"
        
        if op == '==':
            return ("condition_equals", input_variables + [self.scope_manager.get_temp_variable(), self.scope_manager.get_temp_variable(), self.scope_manager.get_temp_variable()] , [block_left, block_right])
        elif op == '!=':
            return ("condition_not_equals", input_variables + [self.scope_manager.get_temp_variable(), self.scope_manager.get_temp_variable(), self.scope_manager.get_temp_variable()] , [block_left, block_right])
        elif op == '>':
            return ("condition_greater", input_variables, [block_left, block_right])
        else:
            raise Exception(f"SyntaxError: Unsupported operator: {op}")

    def visitSequenceStmt(self, ctx: ewhileParser.SequenceStmtContext):
        first = self.visit(ctx.stmt(0))
        second = self.visit(ctx.stmt(1))
        return f"{first};\n{second}"
    
    def visitElseStmt(self, ctx: ewhileParser.ElseStmtContext):
        return self.visit(ctx.stmt())

    def visitIfStmt(self, ctx: ewhileParser.IfStmtContext):
        condition_type, cond_temps, blocks = self.visit(ctx.condition())
        cond_value = cond_temps[2]
        condition = self.template_manager.prepare_template(
            condition_type, cond_temps, blocks, semicolon=True
        )

        cond_resets = ""
        for i, t in enumerate(cond_temps):
            is_last = (i == len(cond_temps) - 1)
            cond_resets += self.template_manager.prepare_template(
                "reset",
                [t],
                semicolon=True
            )

        need = 4 if ctx.elseStmt() is None else 5
        if_temps = [self.scope_manager.get_temp_variable() for _ in range(need)]

        self.scope_manager.go_next_scope()
        then_code = self.visit(ctx.stmt())
        self.scope_manager.go_previous_scope()

        else_code = None
        if ctx.elseStmt() is not None:
            self.scope_manager.go_next_scope()
            else_code = self.visit(ctx.elseStmt())
            self.scope_manager.go_previous_scope()

        if else_code is None:
            code = self.template_manager.prepare_template(
                "if",
                [cond_value] + if_temps,
                [condition, then_code],
                semicolon=True
            )
        else:
            code = self.template_manager.prepare_template(
                "if_else",
                [cond_value] + if_temps,
                [condition, then_code, else_code],
                semicolon=True
            )

        code += cond_resets

        if_resets = ""
        for i, t in enumerate(if_temps):
            is_last = (i == len(if_temps) - 1)
            if_resets += self.template_manager.prepare_template(
                "reset",
                [t],
                semicolon=not is_last
            )
        code += if_resets

        if TEMP_VARIABLE_REUSE_SAME_SCOPE:
            self.scope_manager.put_list_of_temp_variables_in_pool(cond_temps + if_temps)

        return code

