#!/usr/bin/env python3
import os
import sys
import subprocess
import urllib.request
import tarfile
import shutil

BUILDS = {
    "Transpiler": ["bash ./transpiler/src/parser/generate_parser.sh"],
}


def check_emscripten():
    """Check if emscripten is available"""
    try:
        result = subprocess.run(["emcc", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("Emscripten found")
        else:
            raise Exception("Emscripten not found")
    except FileNotFoundError:
        raise Exception("Emscripten not found")


def download_and_extract_gmp():
    """Download and extract GMP if not already present"""
    gmp_dir = "bigint_library/gmp"
    gmp_url = "https://gmplib.org/download/gmp/gmp-6.3.0.tar.xz"
    gmp_archive = "gmp-6.3.0.tar.xz"

    if os.path.exists(gmp_dir):
        print("GMP directory already exists")
        return

    print("Downloading GMP...")
    urllib.request.urlretrieve(gmp_url, gmp_archive)
    print("GMP downloaded successfully")

    print("Extracting GMP...")
    with tarfile.open(gmp_archive, "r:xz") as tar:
        tar.extractall("bigint_library/")

    # Rename the extracted directory to just 'gmp'
    extracted_dir = "bigint_library/gmp-6.3.0"
    if os.path.exists(extracted_dir):
        shutil.move(extracted_dir, gmp_dir)

    # Clean up the archive
    os.remove(gmp_archive)
    print("GMP extracted successfully")


def build_gmp():
    """Build GMP library if not already built"""
    gmp_dir = "bigint_library/gmp"
    libgmp_path = os.path.join(gmp_dir, ".libs", "libgmp.a")

    if os.path.exists(libgmp_path):
        print("GMP library already built")
        return

    print("Building GMP library...")
    original_dir = os.getcwd()
    os.chdir(gmp_dir)

    # Configure GMP for emscripten
    configure_result = subprocess.run(
        ["emconfigure", "./configure", "--disable-assembly", "--host=none"],
        capture_output=True,
        text=True,
    )

    if configure_result.returncode != 0:
        os.chdir(original_dir)
        raise Exception(f"GMP configure failed: {configure_result.stderr}")

    # Build GMP
    make_result = subprocess.run(["emmake", "make"], capture_output=True, text=True)

    os.chdir(original_dir)

    if make_result.returncode != 0:
        raise Exception(f"GMP make failed: {make_result.stderr}")

    print("GMP library built successfully")


def build_gmp_lib():
    """Build gmp_lib.c with GMP"""
    print("Building gmp_lib.c...")

    # List of all functions to export
    exported_functions = [
        "_is_gt",
        "_set_to_zero",
        "_copy",
        "_is_equal",
        "_add",
        "_sub",
        "_right_shift",
        "_left_shift",
        "_mul",
        "_big_div",
        "_mod",
        "_create_bigint",
        "_push_u32_to_bigint",
        "_read_bigint",
        "_get_next_u32",
        "_free_bigint",
    ]

    compile_result = subprocess.run(
        [
            "emcc",
            "bigint_library/gmp_lib.c",
            "bigint_library/gmp/.libs/libgmp.a",
            "-I",
            "bigint_library/gmp",
            "-s",
            "MODULARIZE=1",
            "-s",
            "INITIAL_MEMORY=134217728",
            "-s",
            "MAXIMUM_MEMORY=2147483648",
            "-s",
            "ALLOW_MEMORY_GROWTH=1",
            "-s",
            f"EXPORTED_FUNCTIONS={exported_functions}",
            "-s",
            "ENVIRONMENT='node'",
            "-s",
            "WASM=1",
            "-O3",
            "-o",
            "wasm_runner/gmp_lib.js",
        ],
        capture_output=True,
        text=True,
    )

    if compile_result.returncode != 0:
        raise Exception(f"Failed to compile gmp_lib.c: {compile_result.stderr}")

    print("gmp_lib.c compiled successfully")


def build_original_bigint_lib():
    """Build original bigint library with clang"""
    # Check if clang is available
    clang_check = subprocess.run(["clang", "--version"], capture_output=True, text=True)
    if clang_check.returncode != 0:
        raise Exception("clang is not available")

    print("Building original Bigint Library")
    print("Stack size is set to 8MB")
    print("Initial memory is set to 8MB and max memory is set to 800MB")

    compile_result = subprocess.run(
        [
            "clang",
            "--target=wasm32",
            "-O3",
            "-flto",
            "-nostdlib",
            "-Wl,--no-entry",
            "-Wl,--export-all",
            "-Wl,--lto-O3",
            "-Wl,--initial-memory=16777216,--max-memory=847249408",
            "-Wl,-z,stack-size=8388608",  # 8MB in bytes
            "-o",
            "wasm_runner/bigint_lib.wasm",
            "bigint_library/bigint_lib.c",
        ],
        capture_output=True,
        text=True,
    )

    if compile_result.returncode != 0:
        raise Exception(
            f"Failed to compile original bigint library: {compile_result.stderr}"
        )

    print("Original bigint library built successfully")


def build():
    print("Starting build...")
    sys.stdout.flush()

    print("Installing Python dependencies from requirements.txt...")
    sys.stdout.flush()
    os.system("pip install -r requirements.txt")

    for name, commands in BUILDS.items():
        print(f"Building {name}...")
        sys.stdout.flush()
        for command in commands:
            os.system(command)

    # Build bigint libraries only if --bigint flag is specified
    if "--bigint" in sys.argv:
        print("Building GMP-based Bigint Library...")
        try:
            check_emscripten()
            download_and_extract_gmp()
            build_gmp()
            build_gmp_lib()
            print("GMP-based bigint library built successfully")
        except Exception as e:
            print(f"GMP build failed: {e}")

        try:
            build_original_bigint_lib()
        except Exception as e:
            print(f"Original bigint library build failed: {e}")
    else:
        print("Skipping bigint library builds (use --bigint flag to build)")

    print("Done.")


if __name__ == "__main__":
    build()
