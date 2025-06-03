import unittest
from minimal_compiler.src.generator.template_loader import set_path_explicitly
from util import compile_and_run

class TestAssignment(unittest.TestCase):
    def __init__(self, methodName = "runTest"):
        super().__init__(methodName)

        set_path_explicitly("./generator/templates/")

    # because semantics of while say that variables are >= 0 
    def test_negative_assignment(self):
        code = """
            x0 = x1 - 32
        """
        args = {"n1": 10}

        expected_result = 0

        result = compile_and_run(code, "test_negative_assignment", args)

        self.assertEqual(result, expected_result)

    def test_negative_assignment_bigint(self):
        code = """
            x0 = x1 - 100000000000000000000001
        """
        args = {"n1": 100000000000000000000000}

        expected_result = 0

        result = compile_and_run(code, "test_negative_assignment_bigint", args)

        self.assertEqual(result, expected_result)

    def test_negative_assignment_bigint_with_bigint_constant(self):
        code = """
            x0 = x1 - 100000000000000000000000
        """
        args = {"n1": 100000000000000000000000}

        expected_result = 0

        result = compile_and_run(code, "test_negative_assignment_bigint_with_bigint_constant", args)

        self.assertEqual(result, expected_result)

    def test_negative_while_no_entry(self):
        code = """
            x1 = x1 - 42;

            While x1 > 0 Do
                x0 = x0 + 1;
                x1 = x1 - 1
            End
        """
        args = {"n1": 0}

        expected_result = 0 # no change because no loop is entered

        result = compile_and_run(code, "test_negative_while_no_entry", args)

        self.assertEqual(result, expected_result)