from transpiler.config import ALLOW_COMMENTS

import re


TEMPLATES = [
    "add",
    "sub",
    "mul",
    "mul_constant",
    "div",
    "div_constant",
    "bit_shift_left",
    "bit_shift_right",
    "modulo",
    "max",
    "min",
    "if_else",
    "if",
    "condition_equals",
    "condition_not_equals",
    "condition_greater",
    "while",
    "reset",
    "declaration",
]

class TemplateManager:
    def __init__(self, global_zero_constant):
        self.templates = self.load_templates()
        self.global_zero_constant = global_zero_constant

    def load_templates(self):
        templates = {}
        template_dir = "/transpiler/src/generator/templates"
        for function_name in TEMPLATES:
            with open(f"{template_dir}/{function_name}.twhile", "r") as f:
                templates[function_name] = f.read()           

        return templates

    def get_template(self, name):
        return self.templates[name]

    def format_template(self, code, variables, blocks=[], semicolon=False):
        # replace {{n}} with variables[n]
        for i, var_name in enumerate(variables):
            replace_name = "{{" + f"{i}" + "}}"
            code = code.replace(replace_name, var_name)

        # replace [n] with blocks[n]
        for i, block in enumerate(blocks):
            replace_name = "[" + f"{i}" + "]"
            code = code.replace(replace_name, block)

        # replace {{g}} with global_zero_constant
        code = code.replace("{{" + "g" + "}}", str(self.global_zero_constant))

        if semicolon:
            code += ";"

        if not ALLOW_COMMENTS:
            # remove singleline comments (with "/")
            cleaned_lines = []
            for line in code.splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith('/'):
                    continue
                line_no_inline_comment = re.split(r'\s*/', line, maxsplit=1)[0].rstrip()
                if line_no_inline_comment:  
                    cleaned_lines.append(line_no_inline_comment)

            return '\n'.join(cleaned_lines)

        return code

    def prepare_template(self, name, variables, blocks=[], semicolon=False):
        if name not in self.templates:
            raise Exception(f"Template {name} not found") 

        return self.format_template(self.templates[name], variables, blocks, semicolon)