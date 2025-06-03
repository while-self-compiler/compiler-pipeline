import os

HELPER_FUNCTIONS = [
    "debug",
]

PATH = "./minimal_compiler/src/generator/templates/"

def set_path_explicitly(path):
    global PATH
    PATH = path

def load_helper_functions(as_string=True):
    helper_functions = {}
    template_dir = os.getcwd() + "/minimal_compiler/src/generator/templates"
    for function_name in HELPER_FUNCTIONS:
        with open(f"{template_dir}/{function_name}.wat", "r") as f:
            helper_functions[function_name] = f.read()           

    if as_string:
        helper_functions_str = ""
        for function_name, function_code in helper_functions.items():
            helper_functions_str += function_code
            helper_functions_str += "\n"

        return helper_functions_str
    else:
        return helper_functions
