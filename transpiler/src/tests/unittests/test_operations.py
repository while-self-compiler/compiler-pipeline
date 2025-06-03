import unittest
from minimal_compiler.src.generator.template_loader import set_path_explicitly
from util import compile_and_run

class TestPrograms(unittest.TestCase):
    def __init__(self, methodName = "runTest"):
        super().__init__(methodName)

        set_path_explicitly("../../minimal_compiler/src/generator/templates/")

    def test_bitshift_right(self):
        code = """
            let valOne, valTwo, valThree;
            valTwo = 16;
            valThree = x1;
            valOne = valTwo >> valThree;
            x0 = valOne
        """
        args1 = {"n1": 2}
        args2 = {"n1": 0}
        args3 = {"n1": 10}
        args4 = {"n1": 1}

        expected_result1 = 4 
        expected_result2 = 16
        expected_result3 = 0 
        expected_result4 = 8

        results = compile_and_run(code, "test_bitshift_right", [args1, args2, args3, args4])
        
        result1 = results[0]
        result2 = results[1]
        result3 = results[2]
        result4 = results[3]

        self.assertEqual(result1, expected_result1, f"Test case with {args1} failed, expected {expected_result1}, got {result1}")
        self.assertEqual(result2, expected_result2, f"Test case with {args2} failed, expected {expected_result2}, got {result2}")
        self.assertEqual(result3, expected_result3, f"Test case with {args3} failed, expected {expected_result3}, got {result3}")
        self.assertEqual(result4, expected_result4, f"Test case with {args4} failed, expected {expected_result4}, got {result4}")

    def test_bitshift_left(self):
        code = """
            let valOne, valTwo, valThree;
            valTwo = 2;
            valThree = x1;
            valOne = valTwo << valThree;
            x0 = valOne
        """
        args1 = {"n1": 2}
        args2 = {"n1": 0}
        args3 = {"n1": 3}
        args4 = {"n1": 1}

        expected_result1 = 8
        expected_result2 = 2
        expected_result3 = 16 
        expected_result4 = 4

        results = compile_and_run(code, "test_bitshift_left", [args1, args2, args3, args4])
        
        result1 = results[0]
        result2 = results[1]
        result3 = results[2]
        result4 = results[3]

        self.assertEqual(result1, expected_result1, f"Test case with {args1} failed, expected {expected_result1}, got {result1}")
        self.assertEqual(result2, expected_result2, f"Test case with {args2} failed, expected {expected_result2}, got {result2}")
        self.assertEqual(result3, expected_result3, f"Test case with {args3} failed, expected {expected_result3}, got {result3}")
        self.assertEqual(result4, expected_result4, f"Test case with {args4} failed, expected {expected_result4}, got {result4}")

    def test_division(self):
        code = """
            let valOne, valTwo, valThree;
            valTwo = 16;
            valThree = x1;
            valOne = valTwo / valThree;
            x0 = valOne
        """
        args1 = {"n1": 2}
        args2 = {"n1": 1}
        args3 = {"n1": 16}
        args4 = {"n1": 5}

        expected_result1 = 8 
        expected_result2 = 16
        expected_result3 = 1
        expected_result4 = 3

        results = compile_and_run(code, "test_division", [args1, args2, args3, args4])
        
        result1 = results[0]
        result2 = results[1]
        result3 = results[2]
        result4 = results[3]

        self.assertEqual(result1, expected_result1, f"Test case with {args1} failed, expected {expected_result1}, got {result1}")
        self.assertEqual(result2, expected_result2, f"Test case with {args2} failed, expected {expected_result2}, got {result2}")
        self.assertEqual(result3, expected_result3, f"Test case with {args3} failed, expected {expected_result3}, got {result3}")
        self.assertEqual(result4, expected_result4, f"Test case with {args4} failed, expected {expected_result4}, got {result4}")

    def test_multiplication(self):
        code = """
            let valOne, valTwo, valThree;
            valTwo = 16;
            valThree = x1;
            valOne = valTwo * valThree;
            x0 = valOne
        """
        args1 = {"n1": 2}
        args2 = {"n1": 0}
        args3 = {"n1": 10}
        args4 = {"n1": 1}

        expected_result1 = 32 
        expected_result2 = 0
        expected_result3 = 160
        expected_result4 = 16

        results = compile_and_run(code, "test_multiplication", [args1, args2, args3, args4])
        
        result1 = results[0]
        result2 = results[1]
        result3 = results[2]
        result4 = results[3]

        self.assertEqual(result1, expected_result1, f"Test case with {args1} failed, expected {expected_result1}, got {result1}")
        self.assertEqual(result2, expected_result2, f"Test case with {args2} failed, expected {expected_result2}, got {result2}")
        self.assertEqual(result3, expected_result3, f"Test case with {args3} failed, expected {expected_result3}, got {result3}")
        self.assertEqual(result4, expected_result4, f"Test case with {args4} failed, expected {expected_result4}, got {result4}")

    def test_max(self):
        code = """
            let valOne, valTwo, valThree;
            valTwo = 16;
            valThree = x1;
            valOne = valTwo ^? valThree;
            x0 = valOne
        """
        args1 = {"n1": 2}
        args2 = {"n1": 0}
        args3 = {"n1": 15}
        args4 = {"n1": 17}

        expected_result1 = 16 
        expected_result2 = 16
        expected_result3 = 16 
        expected_result4 = 17

        results = compile_and_run(code, "test_max", [args1, args2, args3, args4])
        
        result1 = results[0]
        result2 = results[1]
        result3 = results[2]
        result4 = results[3]

        self.assertEqual(result1, expected_result1, f"Test case with {args1} failed, expected {expected_result1}, got {result1}")
        self.assertEqual(result2, expected_result2, f"Test case with {args2} failed, expected {expected_result2}, got {result2}")
        self.assertEqual(result3, expected_result3, f"Test case with {args3} failed, expected {expected_result3}, got {result3}")
        self.assertEqual(result4, expected_result4, f"Test case with {args4} failed, expected {expected_result4}, got {result4}")

    def test_min(self):
        code = """
            let valOne, valTwo, valThree;
            valTwo = 16;
            valThree = x1;
            valOne = valTwo v? valThree;
            x0 = valOne
        """
        args1 = {"n1": 2}
        args2 = {"n1": 0}
        args3 = {"n1": 15}
        args4 = {"n1": 17}

        expected_result1 = 2 
        expected_result2 = 0
        expected_result3 = 15 
        expected_result4 = 16

        results = compile_and_run(code, "test_min", [args1, args2, args3, args4])
        
        result1 = results[0]
        result2 = results[1]
        result3 = results[2]
        result4 = results[3]

        self.assertEqual(result1, expected_result1, f"Test case with {args1} failed, expected {expected_result1}, got {result1}")
        self.assertEqual(result2, expected_result2, f"Test case with {args2} failed, expected {expected_result2}, got {result2}")
        self.assertEqual(result3, expected_result3, f"Test case with {args3} failed, expected {expected_result3}, got {result3}")
        self.assertEqual(result4, expected_result4, f"Test case with {args4} failed, expected {expected_result4}, got {result4}")