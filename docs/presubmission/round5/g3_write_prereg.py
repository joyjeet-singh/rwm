"""G3 item 3: append the pre-registrations of X9 (M-101), X10 (M-102) and X11e (M-103) to FINDINGS_LEDGER.md, with the
rule text verbatim from docs/presubmission/round5/PROTOCOLS.md (§2, §3 and §4.2's X11e paragraph), and move RESULTS.md's
M- row. GT1's gt1_write_prereg.py, adapted.

Two mechanical changes to the quoted text, both stated in the entries: PROTOCOLS' `###` subheadings become bold lines
(the ledger splits entries on `### `, and so does every script's ledger_hashes), and the one backticked failure-record
path is split so that ledger_check does not read it as a promised artifact. Refuses to run twice; asserts that no X9,
X10 or X11e reading exists; asserts that the --assert-only and dry-run logs name each script's current SHA-256.
Run from the repository root:  $PY docs/presubmission/round5/g3_write_prereg.py
"""
import ast
import glob
import hashlib
import os
import re
import shutil

L, RES, P = "FINDINGS_LEDGER.md", "RESULTS.md", "docs/presubmission/round5/PROTOCOLS.md"
EV = "/Users/Shared/rwm_verify/evidence/R5G3"
X9S, X10S = "scripts/x9_per_member_propagation.py", "scripts/x10_insample_vs_heldout.py"
COMMON, XA = "scripts/x11_common.py", "scripts/x11a_fold_ens5_calibration.py"
data = glob.glob("results/x9_*") + glob.glob("results/x10_*") + glob.glob("results/x11e_*") + glob.glob("cache/x9_*")
assert not data, f"X9/X10/X11e data exist: {data}"
led = open(L, encoding="utf-8").read()
nm = max(int(n) for n in re.findall(r"^### M-(\d+) ", led, re.M)) + 1
assert nm == 101, nm
assert "PRE-REGISTERED rule X9" not in led and "PRE-REGISTERED rule X10" not in led
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
src9, src10 = open(X9S).read(), open(X10S).read()
assert re.search(r'^RULE_ID, RULE_ID_X11E = "M-101", "M-103"$', src9, re.M)
assert re.search(r'^RULE_ID = "M-102"$', src10, re.M)
F9 = (X9S, XA, COMMON)
F10 = (X10S, XA, COMMON)
frozen_of = lambda src: ast.literal_eval(re.search(r"^FROZEN = (\(.*?\))$", src, re.M).group(1))
assert frozen_of(src9) == F9 and frozen_of(src10) == F10
for s, log in ((X9S, "x9_assert_only.log"), (X10S, "x10_assert_only.log")):
    t = open(os.path.join(EV, log), encoding="utf-8").read()
    assert f"script SHA-256 {sha(s)}" in t and "FAIL" not in t and t.rstrip().endswith("exit 0"), s
dry = open(os.path.join(EV, "g3_dryrun.log"), encoding="utf-8").read()
for s in (X9S, X10S):
    assert f"== {os.path.basename(s)[:-3]} {sha(s)}" in dry, f"no dry run of the current {s}"

proto = open(P, encoding="utf-8").read()


def section(start, end):
    i, j = proto.index(start), proto.index(end)
    body = proto[i:j].split("\n", 1)[1].strip("\n -")
    body = re.sub(r"^### (.+)$", r"**\1.**", body, flags=re.M)
    body = body.replace("`results/x9_per_member_propagation.json.blocked`",
                        "`results/x9_per_member_propagation.json` + `.blocked`")
    assert "\n### " not in "\n" + body and not re.search(r"^## ", body, re.M)
    return body.strip()


R9 = section("## 2. X9", "## 3. X10")
R10 = section("## 3. X10", "## 4. X11")
i = proto.index("**X11e.** X9 (§2) unchanged")
R11E = proto[i:proto.index("\n\n", i)].strip()
SH = lambda paths: ", ".join(f"`{p}` `{sha(p)}`" for p in paths)

PRE = ("**Entered before any of its data exists.** No `results/x9_*`, `results/x10_*` or `results/x11e_*` file exists. Its "
       "frozen files are committed in the same commit as this text, whose subject begins `PRE-REGISTER`, and the script "
       "refuses to compute the reading unless this entry records the SHA-256 of every one of them "
       "(`scripts/x11_common.py` `require_prereg`). Before that commit, on these bytes, the script ran only its "
       "`--assert-only` mode (MEAN through the existing functions, forecast step 1 of PER-MEMBER for assertion (ii), and "
       "the one-member fold check for assertion (iii); no per-member number past step 1) and a dry run of its reading on "
       "**untrained random weights** from a harness outside the repository; both logs, naming these SHA-256s, are in the "
       "session's evidence folder. The ordering can be checked from `git log`.\n\n")
NOTE = ("**Rule text, verbatim from `docs/presubmission/round5/PROTOCOLS.md`** (committed in `2d71330` before any data; "
        "subheadings set in bold and one failure-record path split, so the ledger parses; PROTOCOLS governs where they "
        "differ):\n\n")

E9 = (f"### M-101 — PRE-REGISTERED rule X9: does propagating each member on its own predictions make the spread track "
      f"accumulated error? · **NEW**\n" + PRE
      + "**Deviations, all stated before any per-member number existed.** (1) File names: PLAN's G3 section names "
        "`x9_ts_inf_propagation`; PROTOCOLS, committed first, names `x9_per_member_propagation`, and that name is used. "
        "(2) The first `--assert-only` failed assertion (ii) by 6.4e-7, then 7.1e-15: the members' mean and the "
        "statistics were reduced on arrays of a different shape and memory layout from MEAN's, so float32 and float64 "
        "rounding differed in the last place; every head output and the spread were bitwise identical. By the user's "
        "ruling (`docs/presubmission/round5/DECISIONS.md#G3-assert-ii`) the script now takes the mean and spread at each "
        "step with MEAN's own `torch.stack(...).mean(0)` and reduces C-contiguous arrays; the tolerance stayed 0.0 and "
        "the assertion then passed. (3) Added: the ledger-hash guard. (4) X11e (M-103) runs from the same script with "
        "`--x11e` and writes its own artifact, so this rule's discharged artifact never changes.\n\n"
      + NOTE + R9 + "\n\n"
      + f"**Frozen files and their SHA-256:** {SH(F9)}.\n\n"
      + "**What the discharging session may and may not do.** G3 runs the script unchanged after this commit, writes the "
        "verdicts exactly as returned into this entry's Status line, and changes nothing else here. Not: change the "
        "models, arenas, modes, horizons, statistics, intervals, thresholds or labels; add a reading; or read any number "
        "here as bearing on a discharged rule.\n\n"
      + f"**Evidence** `SRC` `{X9S}`, `scripts/x11_common.py`, `src/score_reference.py`, `scripts/r2_independent_ensemble.py`;\n"
        f"`RUN` `results/x9_per_member_propagation.json` (awaited).\n"
      + "**Status** PRE-REGISTERED, NOT YET DISCHARGED — awaits `results/x9_per_member_propagation.json` · **Relevance** METHOD\n")
E10 = (f"### M-102 — PRE-REGISTERED rule X10: does measuring on training data flatter an ensemble's calibration? · **NEW**\n"
       + PRE
       + "**Deviations.** Added: the ledger-hash guard; the statistics are computed by the frozen verbatim copy of "
         "`task_d3_ens5.py:243-278` in `scripts/x11a_fold_ens5_calibration.py` (`calibration`), which assertion (1) "
         "shows reproduces `results/task_d3_ens5.json`.\n\n"
       + NOTE + R10 + "\n\n"
       + f"**Frozen files and their SHA-256:** {SH(F10)}.\n\n"
       + "**What the discharging session may and may not do.** As M-101.\n\n"
       + f"**Evidence** `SRC` `{X10S}`, `scripts/x11a_fold_ens5_calibration.py`, `scripts/x11_common.py`;\n"
         f"`RUN` `results/x10_insample_vs_heldout.json` (awaited).\n"
       + "**Status** PRE-REGISTERED, NOT YET DISCHARGED — awaits `results/x10_insample_vs_heldout.json` · **Relevance** METHOD\n")
E11 = (f"### M-103 — PRE-REGISTERED rule X11e: X9's per-member propagation on X3's folds' ensemble-5 arms · **NEW**\n"
       "**Entered before any of its data exists.** No X11 fold ensemble-5 run has finished (the queue of "
       "`docs/presubmission/round5/RUN_QUEUE.md` is training) and no `results/x11e_*` file exists. Its reading is "
       "`scripts/x9_per_member_propagation.py --x11e`, frozen with X9 (M-101) in this commit, and it refuses to run "
       "unless this entry records the SHA-256 of every frozen file. The runs, arena and gate are X11's (M-97); the "
       "rule is X9's (M-101) unchanged, at n = 20.\n\n"
       "**Rule text, verbatim from `docs/presubmission/round5/PROTOCOLS.md` §4.2:**\n\n" + R11E + "\n\n"
       "**Deviation.** PROTOCOLS §4's table put X11e's numbers inside X9's artifact; they go to "
       "`results/x11e_fold_e5_propagation.json` instead, so that X9's discharged artifact is never rewritten.\n\n"
       f"**Frozen files and their SHA-256:** {SH(F9)}.\n\n"
       "**What the discharging session may and may not do.** GT2, after the queue has finished and X11's gate has passed, "
       "runs `--x11e` unchanged and writes its verdict exactly as returned into this entry's Status line. Not: anything "
       "M-101 forbids.\n\n"
       f"**Evidence** `SRC` `{X9S}`, `scripts/x11_common.py`;\n`RUN` `results/x11e_fold_e5_propagation.json` (awaited).\n"
       "**Status** PRE-REGISTERED, NOT YET DISCHARGED — awaits `results/x11e_fold_e5_propagation.json` · **Relevance** METHOD\n")

os.makedirs(EV, exist_ok=True)
shutil.copy(L, os.path.join(EV, "FINDINGS_LEDGER.md.bak"))
shutil.copy(RES, os.path.join(EV, "RESULTS.md.bak"))
with open(L, "a", encoding="utf-8") as f:
    f.write("\n" + "\n".join((E9, E10, E11)))
res = open(RES, encoding="utf-8").read()
old = "| `M-` methodological findings | 100 |"
assert res.count(old) == 1
open(RES, "w", encoding="utf-8").write(res.replace(old, "| `M-` methodological findings | 103 |"))
print("appended M-101, M-102, M-103; RESULTS.md M- 100 -> 103")
for p in sorted(set(F9 + F10)):
    print(f"  {p} {sha(p)[:12]}")
