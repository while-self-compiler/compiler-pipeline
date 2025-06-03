from minimal_compiler.src.generator.template_loader import load_helper_functions
from minimal_compiler.src.optimiser.ir_classes import *
from utils import config


class WhileWasmVisitor:
    def __init__(self, symbol_table, constant_table):
        self.wasm_code = ""

        self.optimisation_counter = 0

        self.symbol_table = symbol_table

        self.constant_table = constant_table
        self.constant_pointers = {}
        self.declared_constants = set()

        self.block_counter = 0

    def visit(self, node):
        # dispatch to the correct visit method

        if isinstance(node, ProgramNode):
            return self.visitProgramNode(node)
        elif isinstance(node, SequenceNode):
            return self.visitSequenceNode(node)
        elif isinstance(node, AssignmentNode):
            return self.visitAssignmentNode(node)
        elif isinstance(node, WhileNode):
            return self.visitWhileNode(node)
        elif isinstance(node, ConditionNode):
            return self.visitConditionNode(node)
        elif isinstance(node, AssignmentNodeTwoVar):
            return self.visitAssignmentTwoVarNode(node)
        elif isinstance(node, EmptyNode):
            return self.visitEmptyNode(node)
        elif isinstance(node, PrintNode):
            return self.visitPrintNode(node)
        else:
            raise Exception(f"Unhandled node type: {type(node)}")

    def get_wasm_code(self):
        return self.wasm_code

    def visitProgramNode(self, node: ProgramNode):
        self.wasm_code += "(module\n"
        self.wasm_code += load_helper_functions()
        self.wasm_code += """
            (import "env" "copy" (func $copy (param i32 i32)))
            (import "env" "add" (func $add (param i32 i32 i32)))
            (import "env" "sub" (func $sub (param i32 i32 i32)))
            (import "env" "mul" (func $mul (param i32 i32 i32)))
            (import "env" "div" (func $div (param i32 i32 i32)))
            (import "env" "right_shift" (func $right_shift (param i32 i32 i32)))
            (import "env" "left_shift" (func $left_shift (param i32 i32 i32)))
            (import "env" "mod" (func $mod (param i32 i32 i32)))
            (import "env" "set_to_zero" (func $set_to_zero (param i32)))
            (import "env" "is_gt" (func $is_gt (param i32 i32) (result i32)))"""
        if config.use_gmp:
            self.wasm_code += """
            (import "env" "create_bigint" (func $create_bigint (result i32)))
            (import "env" "push_u32_to_bigint" (func $push_u32_to_bigint (param i32)))
            """
        else:
            self.wasm_code += """
                (import "env" "allocate" (func $allocate (result i32)))
                (import "env" "create_chunk" (func $create_chunk (param i32) (result i32)))
                (import "env" "set_value" (func $set_value (param i32 i32)))
                (import "env" "set_next" (func $set_next (param i32 i32)))
                (import "env" "get_value" (func $get_value (param i32) (result i32)))
                (import "env" "get_next" (func $get_next (param i32) (result i32)))"""

        # declare variables as locals and init with 0 (rule of while language)
        # parameter list for variables:
        # if just x1 and x4 detected in code than the arguments between get also filled:
        # [Min, Max] = [0, 4] => x1, x2, x3, x4
        # find argument with highest index
        self.wasm_code += '(func $main (export "main")'
        max_index = (
            max([int(var[1:]) for var in self.symbol_table.variables])
            if self.symbol_table.variables
            else 0
        )
        arguments_incl_between = [f"x{i}" for i in range(1, max_index + 1)]
        for var_name in arguments_incl_between:
            self.wasm_code += f"(param $arg_{var_name} i32)\n"  # Before bigint chunk pointers: f"(param $arg_{var_name} {var_type})\n"
        self.wasm_code += f" (result i32)\n"
        self.wasm_code += f"(local $currentNode i32)\n"
        self.wasm_code += f"(local $nextNode i32)\n"
        self.wasm_code += (
            f"(local $x0 i32)\n"  # return value (can not be defined via arguments)
        )
        for var_name in self.symbol_table.variables:  # declaration section
            if var_name == "x0":
                continue

            self.wasm_code += f"(local ${var_name} i32)\n"  # Before bigint chunk pointers: f"(local ${var_name} {var_type})\n"
        for var_name in self.constant_table.get_full_table().values():
            self.wasm_code += f"(local ${var_name} i32)\n"
            self.wasm_code += f"(local $node_ptr_{var_name} i32)\n"
        for value, var_name in self.constant_table.get_full_table().items():
            if config.use_gmp:
                self.wasm_code += f";; Creating bigint from u32 blocks for {var_name}\n"
                self.wasm_code += f"(local.set ${var_name} (call $create_bigint))\n"

                temp = value
                while temp > 0:
                    chunk = temp & 0xFFFFFFFF
                    self.wasm_code += (
                        f"(call $push_u32_to_bigint (i32.const {chunk}))\n"
                    )
                    temp = temp >> 32
            else:
                self.wasm_code += f";; Creating bigint chunk chain for {var_name}\n"
                temp = value
                self.wasm_code += f"(local.set $currentNode (call $allocate))\n"
                self.wasm_code += f"(local.set ${var_name} (local.get $currentNode))\n"

                while temp > 0:
                    chunk = temp & 0xFFFFFFFF

                    self.wasm_code += f"(call $set_value (local.get $currentNode) (i32.const {chunk}))\n"

                    temp = temp >> 32

                    if temp > 0:
                        self.wasm_code += f"(local.set $nextNode (call $allocate))\n"
                        self.wasm_code += f"(call $set_next (local.get $currentNode) (local.get $nextNode))\n"
                        self.wasm_code += (
                            f"(local.set $currentNode (local.get $nextNode))\n"
                        )

        for var_name in self.symbol_table.variables:
            if var_name == "x0":
                continue

            self.wasm_code += f"(local.set ${var_name} (local.get $arg_{var_name}))\n"  # default value 0: via an extension of while can we change this now outside via arguments (previously (i32.const 0))

        # init x0 with 0
        if config.use_gmp:
            self.wasm_code += "(call $create_bigint)\n"
        else:
            self.wasm_code += "(call $create_chunk (i32.const 0))\n"
        self.wasm_code += "(local.set $x0)\n"

        if node.stmt is not None:
            self.visit(node.stmt)

        self.wasm_code += "(local.get $x0)\n"
        self.wasm_code += ")\n"
        self.wasm_code += ")\n"

        # print("Optimisation Counter:", self.optimisation_counter)
        return None

    def visitAssignmentNode(self, node: AssignmentNode):
        x_i = node.target
        x_j = node.source
        operator = node.operator
        right_operand = node.value

        # Compile time constant handling (constant table lookup)
        right_operand_name = self.constant_table.get(int(right_operand))

        # debug print
        # self.wasm_code += f"(i32.load (local.get ${x_j}))(call $printf)(drop)"

        if operator == "+":
            self.wasm_code += f"(call $add (local.get ${x_i}) (local.get ${x_j}) (local.get ${right_operand_name}))\n"
        else:
            self.wasm_code += f"(call $sub (local.get ${x_i}) (local.get ${x_j}) (local.get ${right_operand_name}))\n"

        return None

    def visitAssignmentTwoVarNode(self, node: AssignmentNodeTwoVar):
        x_i = node.target
        x_j = node.source
        operator = node.operator
        x_k = node.x_k
        c_2 = node.c_2
        c_1 = node.c_1

        self.wasm_code += f";; Optimised assignment detected: {x_i} = {x_j} {operator} ({x_k} / {c_2} * {c_1})\n"

        if (
            x_j == x_k and c_2 == 1 and c_1 == 1 and operator == "-"
        ):  # if x_j - x_j then we can just set x_i to 0
            self.wasm_code += f"(call $set_to_zero (local.get ${x_i}))\n"
        elif operator == "+":
            self.wasm_code += f"(call $add (local.get ${x_i}) (local.get ${x_j}) (local.get ${x_k}))\n"
        elif operator == ">>":
            self.wasm_code += f"(call $right_shift (local.get ${x_i}) (local.get ${x_j}) (local.get ${x_k}))\n"
            self.optimisation_counter += 1

        elif operator == "<<":
            self.wasm_code += f"(call $left_shift (local.get ${x_i}) (local.get ${x_j}) (local.get ${x_k}))\n"
            self.optimisation_counter += 1

        elif operator == "%":
            self.wasm_code += f"(call $mod (local.get ${x_i}) (local.get ${x_j}) (local.get ${x_k}))\n"
            self.optimisation_counter += 1

        elif operator == "/":
            self.wasm_code += f"(call $div (local.get ${x_i}) (local.get ${x_j}) (local.get ${x_k}))\n"
        elif operator == "*":
            self.wasm_code += f"(call $mul (local.get ${x_i}) (local.get ${x_j}) (local.get ${x_k}))\n"
            self.optimisation_counter += 1
        else:
            self.wasm_code += f"(call $sub (local.get ${x_i}) (local.get ${x_j}) (local.get ${x_k}))\n"

        # set x_k to 0
        # self.wasm_code += f"(call $set_to_zero (local.get ${x_k}))\n"

        return None

    def visitPrintNode(self, node: PrintNode):
        var_name = node.variable
        self.wasm_code += f";; Printing {var_name}\n"
        self.wasm_code += f"(call $printf (local.get ${var_name}))(drop)\n"
        return None

    def visitWhileNode(self, node: WhileNode):
        current_counter = self.block_counter
        self.block_counter += 1
        self.wasm_code += f"\n(block $while_block{current_counter}\n"
        self.wasm_code += f"(loop $while_loop{current_counter}\n"

        self.visit(node.condition)

        # Attention: No use of is_zero function: greater_than gives a value 0 or 1 back (and no pointer)
        # So we can directly use (i32.eqz) and not (call $is_zero)
        self.wasm_code += "(i32.eqz)\n"

        self.wasm_code += f"(br_if $while_block{current_counter})\n"

        self.visit(node.body)

        self.wasm_code += f"(br $while_loop{current_counter})\n"
        self.wasm_code += ")\n"
        self.wasm_code += ")\n"

        return None

    def visitSequenceNode(self, node: SequenceNode):
        for stmt_ctx in node.statements:
            self.visit(stmt_ctx)

        return None

    def visitConditionNode(self, node: ConditionNode):
        var_name = node.variable
        condition_value = node.value

        if int(condition_value) != 0:
            # throw compile time error: condition value is always 0
            # quick change because of semantics of while language
            raise ValueError(f"Condition value should be 0: {condition_value}")

        # Compile time constant handling
        condition_value_name = self.constant_table.get(int(condition_value))

        self.wasm_code += f";; Checking {var_name} > {condition_value}\n"
        self.wasm_code += f"(call $is_gt (local.get ${var_name})(local.get ${condition_value_name}))\n"

        return None

    def visitEmptyNode(self, node: EmptyNode):
        self.wasm_code += f";; {node.reason}\n"

        return None
