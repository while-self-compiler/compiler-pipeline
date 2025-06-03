import sys
import unittest


def run_unittests(name, dir):
    """
    Run all unit tests discovered in the specified directory.

    This function discovers and runs all Python unit tests in the specified directory
    that match the pattern 'test_*.py'. It displays the name of the component being tested
    and uses the standard unittest framework to run the tests.

    Args:
        name (str): Name of the component being tested (for display purposes)
        dir (str): Directory path containing the unit tests

    Returns:
        None
    """
    print(f"Running unittests for {name} ({dir})")
    sys.stdout.flush()
    test_suite = unittest.defaultTestLoader.discover(dir, pattern="test_*.py")

    runner = unittest.TextTestRunner()
    runner.run(test_suite)
