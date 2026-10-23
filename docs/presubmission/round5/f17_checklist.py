"""Round 5, G17 step 5: refresh docs/SUBMISSION_CHECKLIST.md's known items, as a new dated section above round 4's
(which the file keeps, with the earlier passes, as dated records). Round 4's f11_checklist.py, adapted: the
items are listed from docs/presubmission/round5/OUT_OF_SCOPE.md rather than named by hand.

Every figure is computed here from the files named; none is typed. A second run replaces the round-5 section it wrote.

    usage: f17_checklist.py <submission-check-log> <gate-log> <clone-status-file> <measurement-label> <measured-commit>
"""
import json
import re
import subprocess
import sys
import zipfile

SUBCHECK, GATE, CLONE_STATUS, MLABEL, MCOMMIT = sys.argv[1:6]
F = "docs/SUBMISSION_CHECKLIST.md"
N = json.load(open("results/paper_numbers.json"))
N = N.get("values", N)
v = lambda k: N[k]["value"]  # noqa: E731
git = lambda *a: subprocess.run(["git", *a], capture_output=True, text=True).stdout.strip()  # noqa: E731
HEAD = git("rev-parse", "--short=7", "HEAD")
G = json.load(open("results/round5_gates.json"))["gates"]

sub = open(SUBCHECK).read()
met = re.search(r"(\d+)/(\d+) criteria met", sub)
pending = re.findall(r"^\s+PENDING\s+(\S+)", sub, re.M)
failing = re.findall(r"^\s+FAIL\s+(\S+)", sub, re.M)
assert met and not failing, (met, pending, failing)
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
oos = [l for l in open("docs/presubmission/round5/OUT_OF_SCOPE.md").read().splitlines() if l.startswith("- ")]
oos_txt = "\n".join("  - " + re.sub(r"\s+", " ", x[2:])[:230] + ("…" if len(x) > 232 else "") for x in oos)

MARK = "## Round 5, over"
s = open(F).read()
anchor = "## Round 4, over `"
assert s.count(anchor) == 1
if MARK in s:
    assert s.count(MARK) == 1 and s.index(MARK) < s.index(anchor)
    s = s[:s.index(MARK)] + s[s.index(anchor):]

SEC = f"""## Round 5, over `{HEAD}` — the known items now

*[{subprocess.run(['date', '+%Y-%m-%d'], capture_output=True, text=True).stdout.strip()}, pre-submission round 5, G17]
The sections below describe earlier commits and are kept as dated records. This section is the current list,
written by `docs/presubmission/round5/f17_checklist.py` from the files it names. The reproduction figures in the
paper come from {MLABEL}, a clean clone of `{MCOMMIT}`; G18 measures a clone of the final commit. Rounds 4 and 5
were committed locally: none of it had been pushed when this was written.*

### Open items

- **The round-5 gates** (`results/round5_gates.json`, blocking): main content {G['pages']['value']} of 12 pages,
  abstract {G['abstract']['words']} words and {G['abstract']['numerals']} numerals, `ids`, `once`, `sig` at 0, `keys`
  0 missing.
- **`submission_check` returns {met.group(1)} of {met.group(2)}** in the working tree{('; pending: ' + ', '.join(pending)) if pending else ''}.
  The claims audit, regenerated on the frozen text (ruling U5), extracts {C1['n_claims']} claims,
  {C1['by_verdict'].get('SUPPORTED', 0)} supported and {C1['by_verdict'].get('UNREVIEWED', 0)} unreviewed.
- **`part_f_gate` fails check 4 alone, and the paper says so.** {g.group(1)} of {g.group(2)} checks pass with the
  identity strings supplied and a clean clone's results; check 4 fails because {v('ver_differing')} of
  {v('ver_values')} regenerated values differ, all bookkeeping about the submission's own files, none a
  measurement, a statistic or a verdict.
- **The supplementary manifest is exact:** {man['files']} files for an archive of {members} members, and
  {man['commits_in_log']} commits for a log of {commits}.
- **No report `reproduce.sh` writes is left untracked and unignored.**
- **Round 5's logged items** (`docs/presubmission/round5/OUT_OF_SCOPE.md`; none changes what is uploaded):
{oos_txt}
- **The review's residual risk** (`docs/presubmission/round5/REVIEW.md`): the appendix checkers stopped at their
  turn limits; Appendix O's code citations and a few tables were checked only by the build's gates.
- **TMLR's live rules, read 2026-10-24** (`docs/presubmission/round5/TMLR_CHECK.md`): the submission is a Regular
  one (at most 12 pages of main content); the blog since 15 October could not be read by fetch; every author's
  quota and complete OpenReview profile are the authors' to confirm.
- **What the reproduction evidence covers.** Repeatability on one host, one interpreter and one set of
  hash-verified inputs, not portability: no second machine has produced these figures.

"""
s = s.replace(anchor, SEC + anchor, 1)
open(F, "w").write(s)
print(f"  inserted the round-5 section over {HEAD}: submission_check {met.group(0)}; gate {g.group(0)}; manifest {man['files']}/{members}; round-5 items {len(oos)}")
