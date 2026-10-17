"""Round 4, F11 step 5: refresh docs/SUBMISSION_CHECKLIST.md's known items, as a new dated section above the
earlier passes (which the file keeps as dated records). Round 3's r8_checklist.py, adapted: round 3's four
logged items are reported closed, each with the round-4 commit that closed it, and round 4's logged items
are listed from docs/presubmission/round4/OUT_OF_SCOPE.md.

Every figure is computed here from the files named; none is typed. Inserting twice is refused.

    usage: f11_checklist.py <submission-check-log> <gate-log> <clone-status-file> <measurement-label> <measured-commit>
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
git = lambda *a: subprocess.run(["git", *a], capture_output=True, text=True).stdout.strip()  # noqa: E731
HEAD = git("rev-parse", "--short=7", "HEAD")

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
# the stray workplan copy found between F4 and F5 must not ship
for zp in ("supplementary.zip", "supplementary_anon.zip"):
    assert not [x for x in zipfile.ZipFile(zp).namelist() if "TMLR_CODEX_WORKPLAN" in x], zp

# round 3's four logged items, and the round-4 commit that closed each (found by subject, asserted present)
def commit(subject_rx):
    hits = git("log", "--format=%h %s", "presubmission4", "--extended-regexp", f"--grep={subject_rx}").splitlines()
    assert len(hits) == 1, (subject_rx, hits)
    return hits[0].split()[0]


C_R0 = commit(r"^\[F9\]\[H3a\] C7\.1 checks the length")
C_R5 = commit(r"^\[F3\]\[2\] N6 \(post hoc\)")
C_R7 = commit(r"^\[F9\]\[H3b\] task2_3_matched_and_trend\.py records")
oos = open("docs/presubmission/round4/OUT_OF_SCOPE.md").read()
oos_items = [l for l in oos.splitlines() if l.startswith("- ")]
assert len(oos_items) == 8, len(oos_items)       # the list below names each; a new item must be added here

MARK = "## Round 4, over"
s = open(F).read()
assert MARK not in s, "the round-4 section is already present"
anchor = "## Round 3, over `"
assert s.count(anchor) == 1

SEC = f"""## Round 4, over `{HEAD}` — the known items now

*[{subprocess.run(['date', '+%Y-%m-%d'], capture_output=True, text=True).stdout.strip()}, pre-submission round 4, F11]
The sections below describe earlier commits and are kept as dated records. This section is the current
list, written by `docs/presubmission/round4/f11_checklist.py` from the files it names. Section 8's figures
come from {MLABEL}, a clean clone of `{MCOMMIT}`; a clean clone of the commits after it is predicted to
measure the printed figures on all 17 reproduction keys. That is a prediction, not a measurement; round 4's
F12 measures it. Round 4's commits are local: none had been pushed when this was written.*

### Open items

- **The bare `swh:1:` prefix — ruled 2026-09-20, closed.** No occurrence is followed by an object name.
- **`submission_check` returns {met.group(1)} of {met.group(2)}** in the working tree. The one pending
  criterion is C1: the claims audit, regenerated on the frozen text by ruling U5 (round 4, F11), extracts
  {C1['n_claims']} claims, {C1['by_verdict'].get('SUPPORTED', 0)} supported and
  {C1['by_verdict'].get('UNREVIEWED', 0)} unreviewed; the ruling leaves them unreviewed and records it.
  E7 passes.
- **`part_f_gate` fails, and the paper publishes it as failing.** {g.group(1)} of {g.group(2)} checks
  pass with the identity strings supplied and a clean clone's results; check 4 alone fails because
  {v('ver_differing')} of {v('ver_values')} regenerated values differ, all of them bookkeeping in
  {v('ver_diff_nfiles')} bundle record{'s' if int(v('ver_diff_nfiles')) != 1 else ''} ({v('ver_diff_by_file')}), none of them a measurement, a
  statistic or a verdict.
- **The supplementary manifest is exact.** It records {man['files']} files for an archive of {members}
  members, and {man['commits_in_log']} commits for a log of {commits}; both are counted, and asserted.
- **No report `reproduce.sh` writes is left untracked and unignored**: a clean clone's status after
  `reproduce.sh` lists no untracked file.
- **Round 3's four logged items are closed** (`docs/presubmission/round3/OUT_OF_SCOPE.md`):
  - R0, BUILD_CHECKS' list of claims withdrawn on evidence had no length guard: C7.1 now counts its
    items (`{C_R0}`);
  - R5, §6.7's per-episode difficulty averaged the stale and causal action offsets: it uses the causal
    timing alone, post hoc analysis N6, ledger `D-39` (`{C_R5}`);
  - R6, §5.2's per-configuration readings for rule M-74: confirmed in place in round 4 (F4 and F9);
  - R7, Appendix H's R-46 row had no n_independent: it names both arenas' counts (`{C_R7}`).
- **Round 4's logged items** (`docs/presubmission/round4/OUT_OF_SCOPE.md`; none changes what is uploaded):
  - the released code's `dof_acc_l2` reward term subtracts joint positions from joint velocities; neither
    the paper nor the ledger reports it (F0);
  - per-trajectory values at h = 368 depend on how trajectories are batched in the rollout, by up to about
    1e-2; the workplan's optional sensitivity for X3 was not run (F2);
  - two file:line citations in `docs/DEFERRED.md` and `docs/presubmission/OUT_OF_SCOPE.md` are stale (F4);
  - Appendix E prints rule M-84's verdict without the one-policy caveat, which sits in §7.2, Appendix H
    and Appendix V (F4);
  - the resumed queue runner overwrote the first runner's log lines, and a stray workplan copy was
    deleted before any bundle was built; neither bundle carries it (between F4 and F5);
  - two tracked files under `docs/presubmission/`, which no bundle ships, carry a local home path, one of
    them in a round-4 commit's history, so a push would publish it in the repository (F7);
  - rule IDs repeat within §5's sections, where W8 keeps one per section for verdicts only (F8);
  - the supplementary transcript heads two quotations "Quoted in §6.1", which since F8 print in
    Appendix H's "§6.1 in full" passage; the check that compares them with the transcript was
    re-pointed in F11 and covers all five again (F11).
- **TMLR's live rules, read 2026-10-17** (`docs/presubmission/round4/TMLR_CHECK.md`): the style files
  are the official, unmodified ones; any length is allowed; the submission is a long one. Every
  author's quota and complete OpenReview profile are the authors' to confirm before submitting.
- **Figure-internal label overlaps — fixed in round 2, T8.** The PDF prints the step-size quantity as
  LaTeX math since round 3, R4.
- **Clean-clone runs share one private folder by default** (`scripts/t5_anon_transcript.py`); set
  `RWM_PRIVATE_DIR` per clone. **`results/v3_metric_definitions.json` embeds the checkout folder's
  name** in its citation strings; text only, ignored by the verifier.
- **What the reproduction evidence covers.** Repeatability on one host, one interpreter and one set
  of hash-verified inputs, not portability: no second machine has produced these figures.

"""
s = s.replace(anchor, SEC + anchor, 1)
open(F, "w").write(s)
print(f"  inserted the round-4 section over {HEAD}: submission_check {met.group(0)}; gate {g.group(0)}; "
      f"manifest {man['files']}/{members}, {man['commits_in_log']}/{commits}; untracked none; "
      f"round-3 items closed by {C_R0}, {C_R5}, {C_R7}; round-4 items {len(oos_items)}")
