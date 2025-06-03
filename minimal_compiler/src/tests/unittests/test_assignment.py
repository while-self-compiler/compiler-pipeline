import unittest
from minimal_compiler.src.generator.template_loader import set_path_explicitly
from util import compile_and_run

class TestAssignment(unittest.TestCase):
    def __init__(self, methodName = "runTest"):
        super().__init__(methodName)

        set_path_explicitly("./generator/templates/")

    def test_assignment_plus(self):
        code = """
            x0 = x1 + 32
        """
        args = {"n1": 10}

        expected_result = 42

        result = compile_and_run(code, "test_assignment_plus", args)
        
        self.assertEqual(result, expected_result)

    def test_assignment_minus(self):
        code = """
            x0 = x1 - 10
        """
        args = {"n1": 52}

        expected_result = 42

        result = compile_and_run(code, "test_assignment_minus", args)

        self.assertEqual(result, expected_result)
        