"""Round 2, T6/T7: which check anchors (check_comparative_claims.py CLAIMS 'says' and other pinned
fragments) fall inside a line range of PAPER.template.md. Usage: t6_anchors.py START END"""
import re
import sys
sys.path.insert(0, "scripts")
import check_comparative_claims as C  # noqa: E402

a, b = int(sys.argv[1]), int(sys.argv[2])
T = open("PAPER.template.md").read()
lines = T.split("\n")
seg = "\n".join(lines[a - 1:b])
flat = lambda s: re.sub(r"\s+", " ", s)
for c in C.CLAIMS:
    for fld in ("says", "anchor", "fragment", "near", "phrase"):
        v = c.get(fld)
        if isinstance(v, str) and len(v) > 8 and flat(v) in flat(seg):
            print(f"  {c['id']:<7} {c['kind']:<28} {fld}: {v[:80]!r}")
