import shutil
import subprocess
import sys
import time
import os
from pathlib import Path


missing = []

def run_tests(cc):
    print(f"=== Testing with {cc} ===")
    result = subprocess.run([sys.executable, "./tests/run_tests.py", "--cc", cc])
    return result.returncode

def delete_files(extension):
    if extension.startswith("."):
        extension = extension[1:]
    if extension in ("zc", "py"):
        raise Exception("cant delete .zc or .py files")
    tests_dir = Path(__file__).parent
    for filename in tests_dir.glob(f"**/*.{extension}"):
        try:
            filename.unlink()
        except Exception as e:
            print(f"Failed to delete {filename}: {e}")

def delete_log_files():
    delete_files(".log")

delete_files(".log")
delete_files(".zc.c")

# Always test with gcc (default)
if shutil.which("gcc"):
    run_tests("gcc")
    time.sleep(.2)
else:
    missing.append("gcc")

# Check for clang
if shutil.which("clang"):
    run_tests("clang")
    time.sleep(.2)
else:
    missing.append("clang")

# Check for zig
if shutil.which("zig"):
    run_tests("zig")
    time.sleep(.2)
else:
    missing.append("zig")

# Check for tcc
if shutil.which("tcc"):
    run_tests("tcc")
    time.sleep(.2)   
else:
    missing.append("tcc")

if missing:
    print("\nWARNING: The following compilers were not found and their tests were skipped:")
    for cc in missing:
        print(f"  - {cc}")