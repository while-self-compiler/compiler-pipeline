import unittest
from minimal_compiler.src.generator.template_loader import set_path_explicitly
from util import compile_and_run

class TestWhile(unittest.TestCase):
    def __init__(self, methodName = "runTest"):
        super().__init__(methodName)

        set_path_explicitly("./generator/templates/")

    def test_x1_to_x0(self):
        code = """
            x1 = x1 + 32;
            x2 = x2 + 10;

            While x2 > 0 Do
                x1 = x1 + 1;
                x2 = x2 - 1
            End;

            x0 = x1 + 0
        """
        args = {"n1": 0}

        expected_result = 42

        result = compile_and_run(code, "test_x1_to_x0", args)

        self.assertEqual(result, expected_result)

    def test_nested_while(self):
        code = """
            x0 = x0 + 32;
            x1 = x1 + 10;
            x3 = x3 + 10;

            While x1 > 0 Do
                x0 = x0 + 1;
                x1 = x1 - 1;

                While x3 > 0 Do
                    x2 = x2 + 1;
                    x3 = x3 - 1
                End;

                x3 = x3 + 10
            End
        """
        args = {"n1": 0}

        expected_result = 42

        result = compile_and_run(code, "test_nested_while", args)

        self.assertEqual(result, expected_result)