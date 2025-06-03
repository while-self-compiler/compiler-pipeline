#!/usr/bin/env python3
"""
Main test runner for the WHILE/EWHILE project.

This script provides a command-line interface to run various tests for the WHILE/EWHILE
language project, including unit tests, integration tests, and library tests.

Usage:
    python test.py [options]

Options:
    -m: Run minimal compiler unit tests
    -t: Run transpiler unit tests
    -i: Run integration tests (both compilers)
    -im: Run integration tests (minimal compiler only)
    -is: Run integration tests (self compiler only)
"""

import sys
from tests.unit_tests import run_unittests
from tests.integration_tests import run_integration_tests
from utils import config

# Set higher recursion limit for the self compiler
# This is needed because the ANTLR ParseTree structure can get very deep
sys.setrecursionlimit(100000000)

# Test directory constants
TEST_DIRECTORY_MINIMAL_COMPILER = "./minimal_compiler/src/tests/unittests"
TEST_DIRECTORY_TRANSPILER = "./transpiler/src/tests/unittests"
TEST_DIRECTORY_SELF_COMPILER = "./self_compiler/tests/unittests"


if __name__ == "__main__":
    sys.set_int_max_str_digits(50000)
    args = sys.argv[1:]

    if "--no-gmp" in args:
        config.use_gmp = False

    if "-m" in args:
        run_unittests("Minimal Compiler", TEST_DIRECTORY_MINIMAL_COMPILER)
    elif "-t" in args:
        run_unittests("Transpiler", TEST_DIRECTORY_TRANSPILER)
    elif "-i" in args:
        run_integration_tests("both")
    elif "-im" in args:
        run_integration_tests("minimal")
    elif "-is" in args:
        run_integration_tests("self")
