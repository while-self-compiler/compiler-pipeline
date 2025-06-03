import unittest
from minimal_compiler.src.generator.template_loader import set_path_explicitly
from util import compile_and_run

class TestPrograms(unittest.TestCase):
    def __init__(self, methodName = "runTest"):
        super().__init__(methodName)

        set_path_explicitly("./generator/templates/")

    def test_factorial(self):
        code = """
            x2 = x2 + 1;

            While x1 > 0 Do
                x3 = x2 + 0;   
                x4 = x1 - 1;   
                While x4 > 0 Do
                    x5 = x3 + 0;
                    While x5 > 0 Do
                        x2 = x2 + 1;
                        x5 = x5 - 1
                    End;

                    x4 = x4 - 1
                End;
                x1 = x1 - 1
            End;

            x0 = x2 + 0
        """
        args1 = {"n1": 5}
        args2 = {"n1": 0}

        expected_result1 = 120 
        expected_result2 = 1

        result1 = compile_and_run(code, "test_factorial", args1)
        result2 = compile_and_run(code, "test_factorial", args2)

        self.assertEqual(result1, expected_result1)
        self.assertEqual(result2, expected_result2)

    def test_fibonacci(self):
        code = """
            x2 = x2 + 0;
            x3 = x3 + 1;
            x1 = x1 - 1;

            While x1 > 0 Do
                x4 = x2 + 0;  
                x5 = x3 + 0;
                While x5 > 0 Do
                    x4 = x4 + 1;
                    x5 = x5 - 1
                End;

                x2 = x3 + 0;  
                x3 = x4 + 0;  
                x1 = x1 - 1
            End;

            x0 = x3 + 0
        """
        args1 = {"n1": 1}
        args2 = {"n1": 5}

        expected_result1 = 1 
        expected_result2 = 5

        result1 = compile_and_run(code, "test_fibonacci", args1)
        result2 = compile_and_run(code, "test_fibonacci", args2)

        self.assertEqual(result1, expected_result1)
        self.assertEqual(result2, expected_result2)
