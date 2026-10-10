"""Round 3, R8 step 5: refresh docs/SUBMISSION_CHECKLIST.md's known items, as a new dated section above the
earlier passes (which the file keeps as dated records), and mark the earlier passes' figure-overlap lines
resolved (round 2's OUT_OF_SCOPE, T8). Round 2 T11's t11_checklist.py, adapted.

Every figure is computed here from the files named; none is typed. Inserting twice is refused.

    usage: r8_checklist.py <submission-check-log> <gate-log> <clone-status-file> <measurement-label> <measured-commit>
"""
import json
import re
import subprocess
import sys
import zipfile

SUBCHECK, GATE, CLONE_STATUS, MLABEL, MCOMMIT = sys.argv[1:6]
F = "docs/SUBMISSION_CHECKLIST.md"
N = json.load(open("results/paper_numbers.json"))
v = lambda k: N[k]["value"] if isinstance(N[k], dict) else N[k]  # noqa: E731
HEAD = subprocess.run(["git", "rev-parse", "--short=7", "HEAD"], capture_output=True, text=True).stdout.strip()

sub = open(SUBCHECK).read()
met = re.search(r"(\d+)/(\d+) criteria met", sub)
pending = re.findall(r"^\s+PENDING\s+(\S+)", sub, re.M)
failing = re.findall(r"^\s+FAIL\s+(\S+)", sub, re.M)
assert met and pending == ["C1"] and not failing, (met, pending, failing)
assert re.search(r"PASS\s+E7", sub), "E7 is not passing"
gate = open(GATE).read()
g = re.search(r"(\d+)/(\d+) checks pass", gate)
assert g and re.findall(r"^\s+FAIL\s+(\S+)", gate, re.M) == ["4."], gate[-400:]
assert int(v("ver_part_sci")) == 0
C1 = json.load(open("results/task_c1_claims_audit.json"))
man = json.load(open("results/supplementary_manifest.json"))
z = zipfile.ZipFile("supplementary.zip")
members = len(z.namelist())
log = next(x for x in z.namelist() if x.endswith("GIT_LOG_ANONYMISED.txt"))
commits = sum(1 for l in z.read(log).decode().splitlines() if l and not l.startswith("#"))
assert man["files"] == members and man["commits_in_log"] == commits, (man, members, commits)
untracked = [l.split()[-1] for l in open(CLONE_STATUS).read().splitlines() if l.startswith("??")]
assert untracked == [], untracked

MARK = "## Round 3, over"
s = open(F).read()
assert MARK not in s, "the round-3 section is already present"
anchor = "## Round 2, over `"
assert s.count(anchor) == 1

SEC = f"""## Round 3, over `{HEAD}` — the known items now

*[{subprocess.run(['date', '+%Y-%m-%d'], capture_output=True, text=True).stdout.strip()}, pre-submission round 3, R8]
The sections below describe earlier commits and are kept as dated records. This section is the current
list, written by `docs/presubmission/round3/r8_checklist.py` from the files it names. Section 8's figures
come from {MLABEL}, a clean clone of `{MCOMMIT}`; a clean clone of the commits after it is predicted to
measure the printed figures on all 17 reproduction keys. That is a prediction, not a measurement; round 3's
R9 measures it.*

### Open items

- **The bare `swh:1:` prefix — ruled 2026-09-20, closed.** No occurrence is followed by an object name.
- **`submission_check` returns {met.group(1)} of {met.group(2)}** in the working tree. The one pending
  criterion is C1: the claims audit, regenerated on the frozen text by ruling U5 (round 3, R8), extracts
  {C1['n_claims']} claims, {C1['by_verdict'].get('SUPPORTED', 0)} supported and
  {C1['by_verdict'].get('UNREVIEWED', 0)} unreviewed; the ruling leaves them unreviewed and records it.
  E7 passes.
- **`part_f_gate` fails, and the paper publishes it as failing.** {g.group(1)} of {g.group(2)} checks
  pass with the identity strings supplied and a clean clone's results; check 4 alone fails because
  {v('ver_differing')} of {v('ver_values')} regenerated values differ, all of them bookkeeping in
  {v('ver_diff_nfiles')} bundle records ({v('ver_diff_by_file')}), none of them a measurement, a
  statistic or a verdict.
- **The supplementary manifest is exact — fixed in round 3, R5.** It records {man['files']} files for an
  archive of {members} members, and {man['commits_in_log']} commits for a log of {commits}; both are
  counted, and asserted, rather than derived.
- **No report `reproduce.sh` writes is left untracked and unignored — fixed in round 3, R5.** The nine
  that nothing reads are gitignored and excluded by both bundlers; a clean clone's status after
  `reproduce.sh` lists no untracked file.
- **Figure-internal label overlaps — fixed in round 2, T8** (rendered Figures 2(a), 5 and 6; no plotted
  value changed). The earlier passes below still list them as deferred, and each such line now says it
  was fixed. The PDF prints the step-size quantity as LaTeX math since round 3, R4.
- **Four items are logged, not fixed** (`docs/presubmission/round3/OUT_OF_SCOPE.md`):
  - BUILD_CHECKS' list of claims withdrawn on evidence has no length guard (R0);
  - §6.7's per-episode difficulty averages the stale and causal action offsets, a question for the user (R5);
  - §5.2 gives rule M-74's alongside readings at the verdict level only (R6);
  - Appendix H's R-46 row has no recorded n_independent (R7).
- **Clean-clone runs share one private folder by default** (`scripts/t5_anon_transcript.py`); set
  `RWM_PRIVATE_DIR` per clone. **`results/v3_metric_definitions.json` embeds the checkout folder's
  name** in its citation strings; text only, ignored by the verifier.
- **What the reproduction evidence covers.** Repeatability on one host, one interpreter and one set
  of hash-verified inputs, not portability: no second machine has produced these figures.

"""
s = s.replace(anchor, SEC + anchor, 1)

# round 2's OUT_OF_SCOPE (T8): the earlier passes' overlap lines, each marked rather than rewritten
NOTE = " *[Fixed in round 2, T8; see the round-3 section.]*"
OVERLAP = [r"figure-internal labels overlap in Figure 2 \(panel \(a\)'s point labels near h = 100 to 128\) and",
           r"\*\*Cosmetic, deferred:\*\* figure-internal labels overlap in Figures 2 and 5, and page 27 prints the",
           r"DEFERRED, not a defect: figure-internal labels overlap bars or lines in Figures 1 and 2\.",
           r"\*\*Figure-internal labels overlap\*\* bars or lines in Figures 1, 2 and 5\. Cosmetic, deferred, and"]
for rx in OVERLAP:
    m = list(re.finditer(rx, s))
    assert len(m) == 1, (rx, len(m))
    # the note goes at the end of the item: its matched line, then every indented continuation line after it
    end = s.find("\n", m[0].end())
    while True:
        nxt = s.find("\n", end + 1)
        line = s[end + 1:nxt if nxt >= 0 else len(s)]
        if not line.strip() or not line[:1].isspace() or re.match(r"\s*(?:\d+\.|-)\s", line):
            break
        end = nxt
    item = s[m[0].start():end]
    note = (" *[The label overlaps were fixed in round 2, T8, and the step-size quantity is typeset as math since "
            "round 3, R4; see the round-3 section.]*" if "step-size" in item else NOTE)
    s = s[:end] + note + s[end:]
open(F, "w").write(s)
print(f"  inserted the round-3 section over {HEAD}: submission_check {met.group(0)}; gate {g.group(0)}; "
      f"manifest {man['files']}/{members}, {man['commits_in_log']}/{commits}; untracked none; "
      f"{len(OVERLAP)} overlap lines marked")
