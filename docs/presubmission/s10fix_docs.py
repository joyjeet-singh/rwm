"""S10-fix, B3: refresh the hand-written copies of section 8's reproduction figures from the artifact.

Every figure written here is read from results/paper_numbers.json (the ver_* keys, themselves read from
results/verify_reproduction.json); none is typed. Each pattern must match exactly once, and nothing is
written until all have. The appended lines are added only if absent, so a second run is a no-op.
Run from the repository root, after the build has regenerated results/paper_numbers.json.
"""
import json, re, shutil, subprocess, os

N = json.load(open("results/paper_numbers.json"))
v = lambda k: N[k]["value"] if isinstance(N[k], dict) else N[k]
fig = {k: str(v(k)) for k in ("ver_differing", "ver_values", "ver_claim_pct", "ver_overstate")}

def ws(s):  # whitespace-tolerant: a phrase may wrap across lines
    return r"\s+".join(s.split())

# docs/COVER_STATEMENT.md, section "A build gate published as failing" (the tail S27/S28 wording)
COVER = [
    (ws(r"differ; [\d,]+ of [\d,]+ do, so it fails"),
     f"differ; {fig['ver_differing']} of {fig['ver_values']} do, so it fails"),
    (ws(r"and none of the [\d,]+ is a measurement,"),
     f"and none of the {fig['ver_differing']} is a measurement,"),
    (ws(r"stated over the [\d.]+% of the numeric values"),
     f"stated over the {fig['ver_claim_pct']}% of the numeric values"),
    (ws(r"overstate it about [\d,]+-fold,"),
     f"overstate it about {fig['ver_overstate']}-fold,"),
]
CHECKLIST_NOTE = (
    "\n*[2026-09-30, pre-submission S10-fix] The clean-clone figures in both passes below describe the "
    "commits they name. The paper, `docs/BUILD_CHECKS.md` and `README.md` now print a later clean-clone "
    "measurement, restated after S11's findings (`docs/DEFERRED.md`, 2026-09-30).*\n")
CHECKLIST_ANCHOR = "it is the level of its \"Open items\" heading.\n"
DEFERRED_LINE = (
    "[2026-09-30] [pre-submission S10-fix] RESOLVED — the tail S27 entry on section 8's denominator. "
    "By the user's ruling of 2026-09-30 (docs/presubmission/DECISIONS_FOR_USER.md#S11-clean-clone-blocked), "
    "section 8, docs/BUILD_CHECKS.md (two places) and README.md now say the percentage is of the numeric "
    "values under results/ that the comparison counts, and the figures were restated from a clean clone "
    "of the fixed commit. [class: RESOLVED]\n")

edits = {}
t = open("docs/COVER_STATEMENT.md", encoding="utf-8").read()
for rx, new in COVER:
    n = len(re.findall(rx, t))
    assert n == 1, f"COVER_STATEMENT: {rx!r} matches {n} times"
for rx, new in COVER:
    t = re.sub(rx, new, t, count=1)
edits["docs/COVER_STATEMENT.md"] = t

c = open("docs/SUBMISSION_CHECKLIST.md", encoding="utf-8").read()
if CHECKLIST_NOTE.strip() not in c:
    assert c.count(CHECKLIST_ANCHOR) == 1, "SUBMISSION_CHECKLIST anchor not found exactly once"
    edits["docs/SUBMISSION_CHECKLIST.md"] = c.replace(CHECKLIST_ANCHOR, CHECKLIST_ANCHOR + CHECKLIST_NOTE, 1)

d = open("docs/DEFERRED.md", encoding="utf-8").read()
if DEFERRED_LINE not in d:
    edits["docs/DEFERRED.md"] = d + ("" if d.endswith("\n") else "\n") + DEFERRED_LINE

for f, new in edits.items():
    shutil.copy(f, f + ".bak")
    open(f, "w", encoding="utf-8").write(new)
    print(subprocess.run(["diff", f + ".bak", f], capture_output=True, text=True).stdout)
    os.remove(f + ".bak")
print("figures:", fig, "| files edited:", list(edits))
