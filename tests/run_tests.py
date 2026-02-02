import os
import sys
import subprocess
import argparse
import tempfile
from pathlib import Path
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

def run_test(test_path: Path, zc_path: Path, extra_args: list):
    test_name = test_path.name
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        # Construct command: absolute paths ensure no confusion in tmp_dir
        cmd = [str(zc_path.absolute()), "run", str(test_path.absolute()), "--emit-c"] + extra_args
        
        try:
            proc = subprocess.run(cmd, cwd=tmp_dir, capture_output=True, text=True, timeout=30)
            output = proc.stdout + proc.stderr
            
            if proc.returncode != 0:
                return test_name, False, output
            
            if not (tmp_path / "out.c").exists():
                return test_name, False, f"{output}\nERROR: 'out.c' was not generated."
            
            return test_name, True, output
        except Exception as e:
            return test_name, False, f"Exception: {str(e)}"

def find_zc_binary():
    build_dirs = [Path("./build/Debug"), Path("./build"), Path(".")]
    name = "zc.exe" if os.name == "nt" else "zc"
    for d in build_dirs:
        if (d / name).is_file(): return d / name
    return None

def main():
    parser = argparse.ArgumentParser(description="Zen C Test Suite Runner")
    parser.add_argument("--cc", default="gcc", help="C compiler backend to use")
    parser.add_argument("--dir", default="tests", help="Directory containing .zc tests")
    parser.add_argument("-j", "--jobs", type=int, default=os.cpu_count(), help="Number of parallel jobs")
    args, extra = parser.parse_known_args()

    zc_path = find_zc_binary()
    if not zc_path:
        print(f"{RED}Error: 'zc' binary not found.{RESET}")
        sys.exit(1)

    test_dir = Path(args.dir)
    # Sorting ensures the submission order is deterministic
    test_files = sorted(list(test_dir.rglob("*.zc")))
    
    if not test_files:
        print(f"No tests found in {test_dir}")
        sys.exit(0)

    # Setup Log File
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_name = f"test_results_{args.cc}_{timestamp}.log"
    log_path = test_dir / log_name
    log_entries = []

    header = f"** Zen C Test Suite: {args.cc} **\nStarted: {timestamp}\n"
    print(f"{BOLD}{header}{RESET}")
    log_entries.append(header)

    passed_count = 0
    failed_tests = []
    zc_extra_args = ["--cc", args.cc] + extra

    # Using a list to keep track of futures in order
    with ProcessPoolExecutor(max_workers=args.jobs) as executor:
        # 1. Submit all tests and store the 'future' objects in a list
        # This preserves the sorted order from test_files
        future_list = [
            executor.submit(run_test, f, zc_path, zc_extra_args) 
            for f in test_files
        ]
        
        # 2. Iterate through the futures in the order they were submitted
        for i, future in enumerate(future_list, 1):
            # This blocks until THIS specific test is done
            name, success, log = future.result()
            
            status_text = "PASS" if success else "FAIL"
            color = GREEN if success else RED
            
            # Print to console in order
            print(f"[{i:3}/{len(test_files)}] Testing {name.ljust(40)} {color}{status_text}{RESET}")
            
            log_entries.append(f"[{status_text}] {name}")
            
            if success:
                passed_count += 1
            else:
                failed_tests.append((name, log))

    # Summary Generation
    summary = (
        "\n" + "-"*50 + 
        f"\nSummary:\n  Passed: {passed_count}\n  Failed: {len(failed_tests)}\n" + 
        "-"*50 + "\n"
    )
    
    if failed_tests:
        summary += "\nFailed Test Details:\n"
        for name, log in failed_tests:
            summary += f"\n--- {name} ---\n{log}\n"

    print(summary)
    log_entries.append(summary)
    
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(log_entries))

    print(f"{BOLD}Log saved to:{RESET} {log_path}")
    sys.exit(0 if not failed_tests else 1)

if __name__ == "__main__":
    main()