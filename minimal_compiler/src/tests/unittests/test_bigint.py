import unittest
from minimal_compiler.src.generator.template_loader import set_path_explicitly
from util import compile_and_run

class TestWhile(unittest.TestCase):
    def __init__(self, methodName = "runTest"):
        super().__init__(methodName)

        set_path_explicitly("./generator/templates/")

    def test_bigint_constant_addition(self):
        code = """
            x0 = x1 + 100000000000000000000000
        """
        args = {"n1": 20}

        expected_result = 100000000000000000000020

        result = compile_and_run(code, "test_bigint_constant_addition", args)

        self.assertEqual(result, expected_result)

    def test_bigint_argument_and_constant(self):
        code = """
            x0 = x1 + 100000000000000000000000
        """
        args = {"n1": 100000000000000000000000}

        expected_result = 200000000000000000000000

        result = compile_and_run(code, "test_bigint_argument_and_constant", args)

        self.assertEqual(result, expected_result)

        