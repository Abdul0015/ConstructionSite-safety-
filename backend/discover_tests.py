import glob
import re
import os

print("=================================================================")
print("COMPREHENSIVE BACKEND TEST FILES & FUNCTIONS DISCOVERY INVENTORY")
print("=================================================================")

test_files = sorted(glob.glob("tests/*.py"))
total_pytest_funcs = 0

for f in test_files:
    if f.endswith("__init__.py"):
        continue
    content = open(f, encoding="utf-8").read()
    test_funcs = re.findall(r"def (test_\w+)", content)
    total_pytest_funcs += len(test_funcs)
    print(f"\nFILE: {f}")
    print(f"  Pytest Functions Count: {len(test_funcs)}")
    if test_funcs:
        print("  Functions:")
        for fn in test_funcs:
            print(f"    - {fn}")
    else:
        print("  Type: Standalone Executable Script (uses top-level code or __main__ block)")

print("\n=================================================================")
print(f"TOTAL TEST FILES DISCOVERED: {len(test_files) - 1}")
print(f"TOTAL PYTEST TEST FUNCTIONS DISCOVERED: {total_pytest_funcs}")
print("=================================================================")
