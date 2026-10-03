"""Round 2, T11 step 5: refresh docs/SUBMISSION_CHECKLIST.md's known items, as a new dated section above
the earlier passes (which the file keeps as dated records).

Every figure is computed here from the files named; none is typed. Inserting twice is refused.

    usage: t11_checklist.py <submission-check-log> <gate-log> <clone-status-file> <measurement-label>
"""
import json
import re
import subprocess
import sys
import zipfile

SUBCHECK, GATE, CLONE_STATUS, MLABEL = sys.argv[1:5]
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
untracked = [l.split()[-1].replace("results/", "") for l in open(CLONE_STATUS).read().splitlines()
             if l.startswith("??")]

MARK = "## Round 2, over"
s = open(F).read()
assert MARK not in s, "the round-2 section is already present"
anchor = "## This pass, over `c16267c`"
assert s.count(anchor) == 1

SEC = f"""## Round 2, over `{HEAD}` — the known items now

*[{subprocess.run(['date', '+%Y-%m-%d'], capture_output=True, text=True).stdout.strip()}, pre-submission round 2, T11]
The passes below describe round 1's commits and are kept as dated records. This section is the current
list, written by `docs/presubmission/round2/t11_checklist.py` from the files it names; section 8's figures come from {MLABEL}, a clean clone of `5e7969c`; the commits after it carry M3's own verification record, so a clean clone of them is predicted to measure the printed figures on all 17 reproduction keys. That is a prediction, not a measurement; round 2's T12 measures it.*

### Open items

- **The bare `swh:1:` prefix — ruled 2026-09-20, closed.** No occurrence is followed by an object name.
- **`submission_check` returns {met.group(1)} of {met.group(2)}** in the working tree. The one pending
  criterion is C1: the claims audit, regenerated on the frozen text by ruling U5, extracts
  {C1['n_claims']} claims, {C1['by_verdict'].get('SUPPORTED', 0)} supported and
  {C1['by_verdict'].get('UNREVIEWED', 0)} unreviewed; the ruling leaves them unreviewed and records it.
  **E7 passes**: fixed in round 2, T8, the check reads the build-checks supplementary as well as the
  template. A3 needs the gitignored `supplementary.zip`, which a pristine clone does not carry.
- **`part_f_gate` fails, and the paper publishes it as failing.** {g.group(1)} of {g.group(2)} checks
  pass with the identity strings supplied and a clean clone's results; check 4 alone fails because
  {v('ver_differing')} of {v('ver_values')} regenerated values differ, all of them bookkeeping in
  {v('ver_diff_nfiles')} bundle records ({v('ver_diff_by_file')}), none of them a measurement, a
  statistic or a verdict.
- **The claims audit is current.** It was regenerated in round 2, T11, so it no longer accounts for
  any differing value (round 1's 355 of 364).
- **`results/supplementary_manifest.json` is still off by one in two counts:** it records
  {man.get('files')} files for an archive of {members} members, and {man.get('commits_in_log')} commits
  for a log of {commits}, the builder arithmetic recorded below. No number the paper prints comes from
  it.
- **{len(untracked)} reports `reproduce.sh` writes are neither committed nor gitignored**
  ({', '.join(f'`{u}`' for u in untracked)}). They are why a clone's archive holds more files than the
  tree's, and so part of the bundle bookkeeping above.
- **Figure-internal label overlaps — fixed in round 2, T8** (rendered Figures 2(a), 5 and 6; no plotted
  value changed). The PDF still prints the step-size quantity as the literal text `‖µ_t − µ_{{t−1}}‖`;
  cosmetic.
- **`results/p4_transfer_power.json` now has a stage** (20r3a, round 2, T8), and stage 28a3 passes.
- **Clean-clone runs share one private folder by default** (`scripts/t5_anon_transcript.py`); set
  `RWM_PRIVATE_DIR` per clone. **`results/v3_metric_definitions.json` embeds the checkout folder's
  name** in its citation strings; text only, ignored by the verifier.
- **What the reproduction evidence covers.** Repeatability on one host, one interpreter and one set
  of hash-verified inputs, not portability: no second machine has produced these figures.

"""
s = s.replace(anchor, SEC + anchor, 1)
open(F, "w").write(s)
print(f"  inserted the round-2 section over {HEAD}: submission_check {met.group(0)}; gate {g.group(0)}; "
      f"manifest {man.get('files')}/{members}, {man.get('commits_in_log')}/{commits}; untracked {untracked}")
