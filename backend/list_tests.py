import glob
import re

print("--- BACKEND TEST FILES ---")
for f in sorted(glob.glob("tests/*.py")):
    content = open(f, encoding="utf-8").read()
    test_count = len(re.findall(r"def test_", content))
    print(f"{f}: {test_count} test functions")
