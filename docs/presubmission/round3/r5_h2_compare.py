"""R5 item H2: every numeric (and boolean) field of results/a1_ab_by_horizon.json is unchanged to 1e-12 after the
regeneration; the only field that may differ is trend.reading. Compares against the committed copy. Exit 1 (BLOCKED)
on any other difference. Run from the repository root."""
import json
import subprocess
import sys

P = "results/a1_ab_by_horizon.json"
old = json.loads(subprocess.run(["git", "show", f"HEAD:{P}"], capture_output=True, text=True, check=True).stdout)
new = json.load(open(P))
n_num, diffs = 0, []


def walk(a, b, path):
    global n_num
    if isinstance(a, dict):
        if set(a) != set(b):
            diffs.append((path, "keys", sorted(set(a) ^ set(b))))
        for k in set(a) & set(b):
            walk(a[k], b[k], f"{path}.{k}")
    elif isinstance(a, list):
        if len(a) != len(b):
            diffs.append((path, "length", len(a), len(b)))
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, f"{path}[{i}]")
    elif isinstance(a, bool) or a is None:
        if a != b:
            diffs.append((path, a, b))
    elif isinstance(a, (int, float)):
        n_num += 1
        if not isinstance(b, (int, float)) or abs(a - b) > 1e-12:
            diffs.append((path, a, b))
    elif a != b and path != "$.trend.reading":
        diffs.append((path, a, b))


walk(old, new, "$")
print(f"numeric fields compared: {n_num}; differences outside trend.reading: {len(diffs)}")
for d in diffs[:20]:
    print("  ", d)
print("old reading:", old["trend"]["reading"])
print("new reading:", new["trend"]["reading"])
sys.exit(1 if diffs else 0)
