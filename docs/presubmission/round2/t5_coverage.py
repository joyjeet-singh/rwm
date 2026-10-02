"""Round 2, T5 item 2(a): which contribution-tagged ledger entries the paper covers mechanically.

An entry is covered (a) if an artifact it names (results/claims_to_evidence.json `artifacts`, plus every
`results/...` path on its ledger **Evidence** line) is the `source` of a results/paper_numbers.json key that
PAPER.template.md or build_paper.py's captions use. It also records whether the template cites the entry's
ID. Template line numbers are of that revision. Writes docs/presubmission/round2/coverage_mechanical.json; COVERAGE.md is written from it plus the
phrase checks of item 2(b)."""
import json
import re
import subprocess
import sys

# Item 2(a) is the state BEFORE T5: by default the template at the commit before T5's first edit
# (d0c6451, the T4 log commit); pass a path to classify another. build_paper.py likewise.
REV = sys.argv[1] if len(sys.argv) > 1 else "d0c6451"
LED = open("FINDINGS_LEDGER.md").read()
CE = json.load(open("results/claims_to_evidence.json"))["entries"]
TPL = subprocess.check_output(["git", "show", f"{REV}:PAPER.template.md"], text=True).split("\n")
CAP = subprocess.check_output(["git", "show", f"{REV}:scripts/build_paper.py"], text=True)
PN = json.loads(subprocess.check_output(["git", "show", f"{REV}:results/paper_numbers.json"], text=True))

used = {}                                     # key -> first template line using it
for i, ln in enumerate(TPL, 1):
    for k in re.findall(r"\{\{(\w+)\}\}", ln):
        used.setdefault(k, i)
for k in re.findall(r'N\["(\w+)"\]', CAP):
    used.setdefault(k, "caption")
art2keys = {}
for k, line in used.items():
    for a in re.findall(r"results/[\w./-]+\.(?:json|txt|md|csv)", str(PN.get(k, {}).get("source", ""))):
        art2keys.setdefault(a, []).append((k, line))


def block(eid):
    m = re.search(r"^### " + re.escape(eid) + r" .*?(?=^### |\Z)", LED, re.M | re.S)
    return m.group(0) if m else ""


rows = []
for e in CE:
    if e["relevance"] != "CONTRIB":
        continue
    b = block(e["id"])
    ev = re.search(r"^\*\*Evidence\*\*(.*)$", b, re.M)
    arts = sorted(set(e["artifacts"]) | set(re.findall(r"results/[\w./-]+\.(?:json|txt|md|csv)", ev.group(1) if ev else "")))
    hits = [(a, k, l) for a in arts for k, l in art2keys.get(a, [])]
    lines = sorted({l for _, _, l in hits if l != "caption"})
    cited = [i for i, ln in enumerate(TPL, 1) if re.search(r"(?<![\w-])" + re.escape(e["id"]) + r"(?![\w])", ln)]
    rows.append({"id": e["id"], "claim": e["claim"], "status": e["status"], "artifacts": arts,
                 "mechanical_covered": bool(hits), "mechanical_lines": lines[:5],
                 "mechanical_keys": sorted({k for _, k, _ in hits})[:6], "id_cited_lines": cited[:5],
                 "superseded_note": bool(re.search(r"SUPERSEDED|superseded in part", b))})
json.dump(rows, open("docs/presubmission/round2/coverage_mechanical.json", "w"), indent=1)
n = len(rows)
print(f"{n} CONTRIB entries; status {sorted({r['status'] for r in rows})}")
print(f"  (a) covered mechanically: {sum(r['mechanical_covered'] for r in rows)}")
print(f"  ID cited in the template: {sum(bool(r['id_cited_lines']) for r in rows)}")
rest = [r for r in rows if not r["mechanical_covered"]]
print(f"  not covered by (a): {len(rest)}; of them ID-cited: {sum(bool(r['id_cited_lines']) for r in rest)}")
for r in rest:
    print(f"    {r['id']:6} {r['status']:12} cited={r['id_cited_lines'][:2]} {r['claim'][:90]}")
