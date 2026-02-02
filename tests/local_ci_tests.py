import shutil
import subprocess
import sys

missing = []

def run_tests(cc):
    print(f"=== Testing with {cc} ===")
    result = subprocess.run([sys.executable, "./tests/run_tests.py", "--cc", cc])
    return result.returncode

# Always test with gcc (default)
run_tests("gcc")

# Check for clang
if shutil.which("clang"):
    run_tests("clang")
else:
    missing.append("clang")

# Check for zig
if shutil.which("zig"):
    run_tests("zig")
else:
    missing.append("zig")

# Check for tcc
if shutil.which("tcc"):
    run_tests("tcc")
else:
    missing.append("tcc")

if missing:
    print("\nWARNING: The following compilers were not found and their tests were skipped:")
    for cc in missing:
        print(f"  - {cc}")