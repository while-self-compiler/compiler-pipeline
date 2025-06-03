import os
import glob
from colorama import Fore, Back, Style, init
from tests.transpiler_tests import test_transpiler
from tests.minimal_compiler_tests import test_minimal_compiler
from tests.self_compiler_tests import test_self_compiler
from tests.c_integration_tests import run_c_integration_tests

# Initialize colorama
init(autoreset=True)


def run_integration_tests(target_compilers="both"):
    """
    Run all integration tests found in the integration_tests directory.

    This function is the main integration test coordinator that:
    1. Finds all .ewhile and .while test files in the integration_tests directory
    2. For each test file, runs the full compilation and execution pipeline:
       - Transpiles EWHILE to WHILE code (for .ewhile files)
       - Compiles WHILE code using the minimal compiler (if specified)
       - Compiles WHILE code using the self-hosted compiler (if specified)
       - Runs the equivalent C implementation for performance comparison
    3. Verifies outputs against solution files (.sol)
    4. Collects and reports detailed metrics including:
       - Compilation time
       - Execution time
       - Number of WASM instructions generated
       - Performance comparison with C implementation
    5. Provides a comprehensive test summary

    The function supports both .ewhile and .while files and can test different
    compiler configurations based on the target_compilers parameter.

    Args:
        target_compilers (str): Which compilers to test. Options are:
            "both" - test both minimal and self compiler
            "minimal" - test only minimal compiler
            "self" - test only self compiler

    Returns:
        tuple: (passed, failed) - Count of tests that passed and failed
    """
    print(
        f"\n{Back.BLUE}{Fore.WHITE}{Style.BRIGHT}═══════════════ Running Integration Tests ═══════════════{Style.RESET_ALL}"
    )
    test_dir = "./tests/integration_tests"

    # Find all .ewhile and .while files in the test directory
    ewhile_files = glob.glob(f"{test_dir}/*.ewhile")
    while_files = glob.glob(f"{test_dir}/*.while")
    test_files = ewhile_files + while_files

    if not test_files:
        print(f"No integration test files (.ewhile or .while) found in {test_dir}")
        return

    passed = 0
    failed = 0

    # Initialize compiler-specific counters
    minimal_passed_count = 0
    minimal_failed_count = 0
    self_passed_count = 0
    self_failed_count = 0

    for test_file in test_files:
        # Track metrics for reporting
        minimal_run_time = None
        self_run_time = None
        c_run_time = None
        minimal_x0_value = None
        self_x0_value = None
        self_correct = False
        minimal_correct = False

        # Get base name for reporting
        base_name = os.path.basename(test_file)
        print(
            f"\n{Fore.CYAN}{Style.BRIGHT}╔══════ Testing: {base_name} ══════╗{Style.RESET_ALL}"
        )

        # Determine file extension and find matching .sol file
        file_ext = os.path.splitext(test_file)[1]
        sol_file = test_file.replace(file_ext, ".sol")
        if not os.path.exists(sol_file):
            print(f"  ERROR: No solution file found for {base_name}")
            failed += 1
            continue

        # Read expected output
        with open(sol_file, "r") as f:
            expected_output = f.read().strip()

        # Track component success/failure
        transpiler_success = False
        minimal_compiler_success = False
        self_compiler_success = False

        # ===== TEST TRANSPILER =====
        transpiler_success, while_filepath, transpile_time, tokens = test_transpiler(
            test_file
        )

        # Extract base name for C implementation test
        base_name_no_ext = os.path.splitext(base_name)[0]

        if transpiler_success:
            # ===== TEST MINIMAL COMPILER =====
            if target_compilers in ["both", "minimal"]:
                (
                    minimal_compiler_success,
                    minimal_correct,
                    wasm_filepath,
                    minimal_compile_time,
                    minimal_run_time,
                    minimal_x0_value,
                    wasm_instructions,
                ) = test_minimal_compiler(test_file, expected_output)

            # ===== TEST SELF COMPILER =====
            if target_compilers in ["both", "self"]:
                (
                    self_compiler_success,
                    self_correct,
                    self_wasm_file,
                    self_compile_time,
                    self_run_time,
                    self_x0_value,
                    self_wasm_instructions,
                ) = test_self_compiler(test_file, expected_output)

        # ===== TEST C IMPLEMENTATION =====
        print(
            f"\n{Fore.YELLOW}{Style.BRIGHT}▶ 4. Testing C Implementation{Style.RESET_ALL}"
        )
        c_run_time = run_c_integration_tests(base_name_no_ext)

        # Determine overall pass/fail
        minimal_pass = minimal_compiler_success and minimal_correct
        self_pass = self_compiler_success and self_correct

        # Update compiler-specific counters
        if target_compilers in ["both", "minimal"]:
            if minimal_pass:
                minimal_passed_count += 1
            elif minimal_compiler_success:
                minimal_failed_count += 1

        if target_compilers in ["both", "self"]:
            if self_pass:
                self_passed_count += 1
            elif self_compiler_success or (
                self_x0_value is None and target_compilers in ["both", "self"]
            ):
                # Count as a failure if the test was attempted but failed or timed out
                self_failed_count += 1

        # Print report for this test
        print(
            f"\n{Fore.CYAN}{Style.BRIGHT}╚════ Test Results: {base_name} ════╝{Style.RESET_ALL}"
        )
        print(f"  {Fore.WHITE}Expected Value: {expected_output}{Style.RESET_ALL}")

        if minimal_x0_value is not None:
            status = Fore.GREEN + "✓ PASS" if minimal_correct else Fore.RED + "✗ FAIL"
            print(
                f"  Minimal Compiler Output: {minimal_x0_value} [{status}{Style.RESET_ALL}] WASM Runtime: {Fore.CYAN}{minimal_run_time:.4f}s{Style.RESET_ALL}"
            )

        if self_x0_value is not None:
            status = Fore.GREEN + "✓ PASS" if self_correct else Fore.RED + "✗ FAIL"
            print(
                f"  Self Compiler Output: {self_x0_value} [{status}{Style.RESET_ALL}] WASM Runtime: {Fore.CYAN}{self_run_time:.4f}s{Style.RESET_ALL}"
            )

        # Print C implementation comparison
        if c_run_time is not None:
            # Calculate speedup compared to C version
            if minimal_run_time is not None and c_run_time > 0 and minimal_run_time > 0:
                minimal_speedup = c_run_time / minimal_run_time
                speedup_text = (
                    f"{Fore.GREEN}x{minimal_speedup:.2f} faster{Style.RESET_ALL}"
                    if minimal_speedup > 1
                    else f"{Fore.RED}x{1 / minimal_speedup:.2f} slower{Style.RESET_ALL}"
                )
                print(
                    f"  C vs Minimal: {speedup_text} than C (C: {Fore.CYAN}{c_run_time:.4f}s{Style.RESET_ALL})"
                )

            if self_run_time is not None and c_run_time > 0 and self_run_time > 0:
                self_speedup = c_run_time / self_run_time
                speedup_text = (
                    f"{Fore.GREEN}x{self_speedup:.2f} faster{Style.RESET_ALL}"
                    if self_speedup > 1
                    else f"{Fore.RED}x{1 / self_speedup:.2f} slower{Style.RESET_ALL}"
                )
                print(
                    f"  C vs Self: {speedup_text} than C (C: {Fore.CYAN}{c_run_time:.4f}s{Style.RESET_ALL})"
                )

        # Determine overall test result message based on which compilers were tested
        if target_compilers == "both":
            if minimal_pass and self_pass:
                print(
                    f"\n   {Fore.GREEN}OVERALL: PASS - {base_name} (Both compilers){Style.RESET_ALL} "
                )
                passed += 1
            elif minimal_pass:
                print(
                    f"\n   {Fore.GREEN}OVERALL: PASS - {base_name} (Minimal compiler only){Style.RESET_ALL} "
                )
                passed += 1
            elif self_pass:
                print(
                    f"\n   {Fore.GREEN}OVERALL: PASS - {base_name} (Self compiler only){Style.RESET_ALL} "
                )
                passed += 1
            else:
                print(
                    f"\n   {Fore.RED}OVERALL: FAIL - {base_name} (Both compilers failed){Style.RESET_ALL} "
                )
                failed += 1
        elif target_compilers == "minimal":
            if minimal_pass:
                print(
                    f"\n   {Fore.GREEN}OVERALL: PASS - {base_name} (Minimal compiler){Style.RESET_ALL} "
                )
                passed += 1
            else:
                print(
                    f"\n   {Fore.RED}OVERALL: FAIL - {base_name} (Minimal compiler){Style.RESET_ALL} "
                )
                failed += 1
        elif target_compilers == "self":
            if self_pass:
                print(
                    f"\n   {Fore.GREEN}OVERALL: PASS - {base_name} (Self compiler){Style.RESET_ALL} "
                )
                passed += 1
            else:
                print(
                    f"\n   {Fore.RED}OVERALL: FAIL - {base_name} (Self compiler){Style.RESET_ALL} "
                )
                failed += 1

    print(
        f"\n{Back.BLUE}{Fore.WHITE}{Style.BRIGHT}═══════════════ Integration Test Summary ═══════════════{Style.RESET_ALL}"
    )
    print(
        f"  {Fore.CYAN}TOTAL TESTS: {passed + failed} | {Fore.GREEN}PASSED: {passed} | {Fore.RED}FAILED: {failed}{Style.RESET_ALL}"
    )

    # Print compiler-specific summary
    if target_compilers in ["both", "minimal"]:
        print(
            f"  {Fore.CYAN}MINIMAL COMPILER: {Fore.GREEN}PASSED: {minimal_passed_count} | {Fore.RED}FAILED: {minimal_failed_count}{Style.RESET_ALL}"
        )
    if target_compilers in ["both", "self"]:
        print(
            f"  {Fore.CYAN}SELF COMPILER: {Fore.GREEN}PASSED: {self_passed_count} | {Fore.RED}FAILED: {self_failed_count}{Style.RESET_ALL}"
        )

    return passed, failed
