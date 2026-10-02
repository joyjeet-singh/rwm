"""Round 2, T6/T7: body words by FILE_MAP section 13's rule, per section, from PAPER.md."""
import re
import sys

L = open("PAPER.md", encoding="utf-8").read().split("\n")
idx = lambda rx: next(i for i, l in enumerate(L) if re.match(rx, l))
s, d = idx(r"^## 1\. Introduction\s*$"), idx(r"^## Data and code\s*$")
heads = [(i, l) for i, l in enumerate(L) if re.match(r"^#{2,3} ", l)]
tab = lambda a, b: sum(len(l.split()) for l in L[a:b] if l.lstrip().startswith("|"))
print(f"body (Introduction to Data and code): {sum(len(l.split()) for l in L[s:d]):,}")
for k, (i, l) in enumerate(heads):
    j = heads[k + 1][0] if k + 1 < len(heads) else len(L)
    if (s <= i < d) or "-a" in sys.argv:
        w = sum(len(x.split()) for x in L[i:j])
        print(f"  {w:6,}  (tables {tab(i, j):5,})  {l[:90]}")
