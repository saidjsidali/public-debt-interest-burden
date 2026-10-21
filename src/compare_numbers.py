"""Compare two key_numbers.json files with a numeric tolerance.

Used in CI: a fresh run on another operating system can differ in the last
digits of floating-point results, so numbers are compared with a relative
tolerance instead of byte by byte.

    python src/compare_numbers.py committed.json outputs/key_numbers.json
"""

import json
import math
import sys

REL_TOL = 1e-7
ABS_TOL = 1e-9


def differences(a, b, path=""):
    if isinstance(a, dict) and isinstance(b, dict):
        out = [f"{path}/{k}: missing" for k in a.keys() ^ b.keys()]
        for k in a.keys() & b.keys():
            out += differences(a[k], b[k], f"{path}/{k}")
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [f"{path}: length {len(a)} vs {len(b)}"]
        return [d for i, (x, y) in enumerate(zip(a, b)) for d in differences(x, y, f"{path}/{i}")]
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        if not math.isclose(a, b, rel_tol=REL_TOL, abs_tol=ABS_TOL):
            return [f"{path}: {a} vs {b}"]
        return []
    return [] if a == b else [f"{path}: {a!r} vs {b!r}"]


def main(old, new):
    diff = differences(json.load(open(old, encoding="utf-8")), json.load(open(new, encoding="utf-8")))
    for d in diff[:50]:
        print(d)
    print(f"{len(diff)} differences")
    return 1 if diff else 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:3]))
