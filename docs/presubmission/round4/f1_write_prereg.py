"""F1 item 5: append the pre-registrations of rules X3 and X4 (PLAN round 4, Annex 2) to FINDINGS_LEDGER.md as M-86 and
M-87, and move RESULTS.md's M- row. Round 3's r1_write_prereg.py, adapted.

Every motivation figure is read from an artifact; each script's SHA-256 is computed from the file as it stands. Writes .bak
copies outside the repository, refuses to run twice, and asserts that no run or reading either rule reads exists yet:
no X3 run record or weights, no matched-baseline run record or weights, and neither rule's output.
Run from the repository root:  $PY docs/presubmission/round4/f1_write_prereg.py
"""
import glob
import hashlib
import json
import os
import re
import shutil

L, RES = "FINDINGS_LEDGER.md", "RESULTS.md"
BAK = "/Users/Shared/rwm_verify/evidence/R4F1"
S3, S4 = "scripts/x3_cross_fold.py", "scripts/x4_matched_baselines.py"
O3, O4 = "results/x3_cross_fold.json", "results/x4_matched_baselines.json"
data_x3 = glob.glob("results/x3_run_*.json") + glob.glob("runs/x3_arm*")
data_x4 = glob.glob("results/baseline_run_*_matched_seed*.json") + glob.glob("runs/baseline_*_matched_seed*")
assert not data_x3, f"X3 data exist: {data_x3}"
assert not data_x4, f"X4 data exist: {data_x4}"
assert not os.path.exists(O3) and not os.path.exists(O4) and not os.path.exists("results/x4_matched_baselines_eval.json")
led = open(L, encoding="utf-8").read()
nm = max(int(n) for n in re.findall(r"^### M-(\d+) ", led, re.M)) + 1
M3, M4 = f"M-{nm}", f"M-{nm + 1}"
assert (M3, M4) == ("M-86", "M-87"), (M3, M4)
assert "PRE-REGISTERED rule X3" not in led and "PRE-REGISTERED rule X4" not in led
assert re.search(r'^RULE_ID = "M-86"$', open(S3).read(), re.M) and re.search(r'^RULE_ID = "M-87"$', open(S4).read(), re.M)
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
sha3, sha4 = sha(S3), sha(S4)
J = lambda p: json.load(open(p))
# the claims the entries make about what ran before the freeze, checked against the saved output of those runs
LOG = lambda n: open(os.path.join(BAK, n), encoding="utf-8").read()
x3a, x4a, x3d, x4d = LOG("x3_assert_only.log"), LOG("x4_assert_only.log"), LOG("x3_dryrun.log"), LOG("x4_dryrun.log")
assert f"script SHA-256 {sha3}" in x3a and "--assert-only: assertions (a)-(g) pass" in x3a and "FAIL" not in x3a
assert f"script SHA-256 {sha4}" in x4a and "--assert-only: assertions (a)-(c) pass" in x4a and "FAIL" not in x4a
assert f"x3_cross_fold.py SHA-256 {sha3}" in x3d and "DRY RUN reading()" in x3d and "a NaN score stops the reading" in x3d
assert f"x4_matched_baselines.py SHA-256 {sha4}" in x4d and "DRY RUN reading()" in x4d and "raises CannotDischarge" in x4d
probes3 = sorted(os.path.basename(p) for p in glob.glob("runs/timing_probe_round4/x3_run_*.json"))
probes4 = sorted(glob.glob("runs/timing_probe_round4/baseline_run_*_matched_*.json")
                 + glob.glob("runs/baselines_probe/baseline_run_*_matched_*.json"))
assert not glob.glob("runs/timing_probe_round4/**/*.pt", recursive=True) and \
    not glob.glob("runs/baselines_probe/**/*_matched_*/*.pt", recursive=True), "a timing probe saved a checkpoint"
for f in probes4:
    assert J(f)["hyperparameters"]["iterations"] == 20, f"{f} is not a 20-iteration probe"
for f in glob.glob("runs/timing_probe_round4/x3_run_*.json"):
    a = J(f)
    assert a["hyperparameters"]["iterations"] == 20 and not a["evaluations"], f"{f} is not a 20-iteration, no-evaluation probe"

# ---- motivation, read from artifacts (all known before these rules)
d1 = J("results/task_d1_threeseed.json")
a1 = J("results/a1_ab_by_horizon.json")["by_horizon"]["368"]
gpt = a1["gap_per_trajectory"]
share = max(gpt) / sum(gpt)
bver = J("results/baseline_verification.json")
npar = {k: v["n_params"] for k, v in bver["baselines"].items()}
rwm = bver["rwm_state_pathway_params"]
m76 = J("results/baselines_verdict.json")["rules"]["M-76"]["verdict"]
tim = J("results/round4_queue_timing.json")
assert tim["x3"]["seeds"] == [0, 1, 2] and tim["x4"]["seeds"] == [0, 1, 2] and not tim["blocked"]
ref = J("results/x3_armB_2500_reference.json")
fold = J("docs/presubmission/round4/f1_fold_support.json")
assert fold["a"]["pass"] and fold["b"]["pass"] and fold["c"]["pass"]
c_tr = J("results/m64_short_units.json")["cells"]["C_section_5_ab_gap"]["out-of-sample held-out pair"]["1"]
f2 = lambda x: f"{x:.2f}"
ci4 = lambda c: f"[{c[0]:+.4f}, {c[1]:+.4f}]"

common_tail = """**What the discharging session may and may not do.** Session F5, after the queue has finished and its gate has passed,
runs `{S}` unchanged, having asserted its SHA-256 equals the one recorded here; records the reading exactly as the script
returns it, with the {vals} values, in a new ledger entry; and changes only this entry's Status line.
Not: change the {what}; add a reading; or read any number here as bearing on a discharged rule."""

e3 = f"""
### {M3} — PRE-REGISTERED rule X3: does the base claim replicate when each episode is held out in turn? · **NEW**
**Entered before any of its data exists.** No run of X3's queue has been trained: no `results/x3_run_*.json` and no
`runs/x3_arm*` exist, and `{O3}` does not exist. The only training on a new fold so far is F1's two 20-iteration timing
probes on fold {{0, 2}} (`runs/timing_probe_round4/`: {", ".join(f"`{x}`" for x in probes3)}), which saved no checkpoint and
evaluated nothing. The script that computes every reading below, `{S3}`
(SHA-256 `{sha3}`), is committed in the same commit as this text, whose subject begins `PRE-REGISTER`, and refuses to
compute the rule unless this entry records its SHA-256. Before that commit, on these bytes, it ran only its synthetic
self-test and its `--assert-only` mode, which loads only existing weights (fold {{1, 8}} at 2,500 iterations and, for
assertion (f), Arm A and Arm B at 10,000) and computes no reading: assertions (a)-(g) passed. A dry run of `reading()`, the
code `main()` runs after the assertions, on untrained weights, from a harness outside the repository, also ran, and showed a
non-finite score stopping the reading. The outputs of both, each naming this SHA-256, are in the session's evidence folder. The ordering can be checked from `git log`. This is round 4's rule X3
(PLAN Annex 2, objection O1).

**Exploratory, and bounded.** It never re-opens M-23 or any discharged rule. Their verdicts are unchanged whatever it
returns, and nothing here is read as bearing on them. At 2,500 iterations, not 10,000: §5's headline ratio,
{d1['aggregate']['ratio_B_over_A']:.2f}x at h = 368 on the held-out pair at 10,000 iterations (`results/task_d1_threeseed.json`),
is not re-read.

**Known before this rule** (its motivation): §5's long-horizon figures rest on {a1['n_independent']} independent held-out
trajectories, and at h = 368 one of them carries {100 * share:.0f}% of the summed three-seed gap at 10,000 iterations
(`results/a1_ab_by_horizon.json`). At h = 1 on M-64's 33-row units the gap is {c_tr['gap']:+.4f} {ci4(c_tr['gap_ci_unit_level'])}
(B − A at 10,000 iterations, `results/m64_short_units.json`): teacher forcing ahead.

**Folds.** {{1, 8}} (the existing 2,500-iteration runs, `runs/arm{{A,B}}_seed<s>/weights_2500.pt`) and {{0, 2}}, {{3, 4}},
{{5, 6}}, {{7, 9}}, the remaining episodes paired in index order. Every episode is out of sample in exactly one fold. {{0, 2}} and
{{3, 4}} each hold two episodes from the same speed half, unlike `make_split`'s stratified {{1, 8}}; recorded, not corrected.

**Runs.** For each new fold: Arm A and Arm B, seeds 0-2, 2,500 iterations, trained by `scripts/step5_train.py --holdout a,b`
(`rollout_eval.fold_split`), otherwise identical to the existing 2,500-iteration runs: 24 runs. **Seeds:** three, by the user's
ruling `docs/presubmission/round4/DECISIONS.md#F1-x3-cap` (X3's cap raised from 22 to 24 CPU-hours before this entry; projected
{tim['x3']['projected_h']:.2f} h, `results/round4_queue_timing.json`). Annex 2's fallback (seeds 0-1, read with the same
thresholds) is not applied; it would have applied at the plan's 22 hours.

**Arena.** Each fold's held-out pair as non-overlapping 400-step trajectories (`mn_sweep_eval.arena`: 32 history rows, 368
forecast rows; 4 per fold), pooled over the five folds: **n = 20**. Scored by `mn_sweep_eval.score`, imported: the causal
pairing, relative-L1 cumulative over forecast steps 1..h, h ∈ {{1, 8, 32, 100, 128, 368}}.

**Statistic.** Per trajectory, gap = (seed-mean relative-L1 of Arm B) − (seed-mean relative-L1 of Arm A) at h = 368; its
mean over the 20 trajectories, with a 95% interval from M-23's three-seed bootstrap, imported:
`review_bootstrap_unit.boot_cluster` (whole trajectories resampled, every seed carried, seeds pooled inside each draw) at
`a1_ab_by_horizon`'s 20,000 Monte Carlo draws and generator seed 0. The by-horizon bootstrap itself is inline in
`a1_ab_by_horizon.py`'s `main()`; assertion (e) shows `boot_cluster` at its settings reproduces it.

**Reading**, at h = 368:
- **REPLICATES ACROSS FOLDS** if the interval's lower bound > 0;
- **REVERSES** if its upper bound < 0;
- **NOT RESOLVED** otherwise.

**Part of the rule, reported verbatim, with no verdict of its own:**
- the per-episode sign test: for each of the ten episodes, the sign of its mean gap at h = 368 (the mean of its two
  trajectories), the count positive and the exact two-sided binomial P (`a1_ab_by_horizon.sign_p`, imported);
- each fold's gap at h = 368 with its exact interval over all 256 ordered resamples of its four trajectories
  (`p5_sweep_power.boot_ci`, imported: M-74's and M-76's exact bootstrap).

**Alongside, never governing:**
- h = 100, the same statistic and interval, with the label it would carry;
- h = 1 on M-64's 33-row units pooled over the five folds' held-out episodes: the gap as M-64 defines it (B − A, so
  negative is the teacher-forcing lead), with M-64's unit-level interval and its episode-level footnote
  (`m64_short_units.build_index`, `unit_rollout`, `rel_l1`, `boot_ci`, imported);
- the ratio of means, Arm B's over Arm A's (`ratio_B_over_A`), at each horizon.

**Assertions, before any reading of a new fold** (a failure stops the run with no reading):
- **(a)** with {{1, 8}}, `rollout_eval.fold_split` gives the same training windows as `make_split(seed=0)` (SHA-256 of the index
  list, both ways), whose length equals the committed `n_train_windows`;
- **(b)** F1's 50-iteration run of Arm A, seed 0, reproduced the committed run's first 50 values of every loss trace **bitwise**,
  through `--holdout 1,8` and through the default path (the committed curves are full-precision floats, so the test is
  equality, not a tolerance). The script reads the PASS F1 recorded in `docs/presubmission/round4/f1_fold_support.json`; in a copy
  without `docs/presubmission/` (neither bundle ships it) it records the check as not available instead;
- **(c)** each new fold's training set excludes exactly its two episodes, no training window touches them, and its four held-out
  trajectories lie inside them;
- **(d)** fold {{1, 8}}'s readings reproduce the committed 2,500-iteration held-out relative-L1 at every horizon, to 1e-6: Arm A
  per trajectory and seed against `results/mn_compute_matched.json`'s 2,500 block, and Arm B per seed against
  `results/x3_armB_2500_reference.json`. That reference was built for this assertion by ruling (B) of
  `DECISIONS.md#F0-armB-2500-h128`, from the stored rollouts behind `results/head_to_head_accuracy.json`: equal to it on every
  shared cell, and within 1e-6 of `results/action_sensitivity.json`'s rollout at h = 32
  ({ref['checks']['armB_h32_vs_action_sensitivity_I0']['max_abs_diff']:.1e});
- **(e)** `boot_cluster` at 20,000 draws and seed 0 reproduces `results/a1_ab_by_horizon.json`'s three-seed intervals at every
  horizon, to 1e-6;
- **(f)** M-64's imported machinery reproduces `results/m64_short_units.json` cell C (held-out pair, h = 1, 10,000 iterations),
  to 1e-9;
- **(g)** `p5_sweep_power.boot_ci` and `a1_ab_by_horizon.sign_p` reproduce `results/baselines_verdict.json`'s M-76 intervals and
  `results/a1_ab_by_horizon.json`'s sign-test P values, to 1e-12;
- **(h)** every new run's record says rule X3, 2,500 iterations, its seed, arm and fold, with finite losses, and its weights
  exist.

**Failure.** A non-finite score anywhere the reading uses, or any internal check failing, stops the run with a
`.blocked` record beside its output and no reading (M-76's failure clause): the rule then cannot be discharged as written.

**Gate.** No session evaluates a run of the round-4 queue before F5 (PLAN §1.2 rule 5). The training driver evaluates its own
checkpoints at 500 and 2,500 iterations on Protocol A, as every 2,500-iteration run always has, and each run's log
(`runs/queue_logs/<id>.log`) prints them: those lines are not read before F5.

**Caveats, in every sentence that reports it:** 2,500 iterations, not 10,000; the seeds are not independent units (the
interval resamples trajectories, carrying every seed); the folds are fixed, not stratified by speed.

**Deviations from PLAN Annex 2, all stated above:** three seeds by ruling F1-x3-cap; the Arm B reference by ruling (B); the
interval function's form (`boot_cluster`, asserted equal to the inline original); M-64's sign convention and interval for the
h = 1 alongside; the exact per-fold interval's function; assertions (e)-(h) and the failure clause added.

{common_tail.format(S=S3, vals='part-of-rule and alongside', what='folds, models, seeds, iterations, arena, horizons, statistic, interval, thresholds or labels')}
**Evidence** `SRC` `{S3}`, `scripts/step5_train.py` (`--holdout`), `src/rollout_eval.py` (`fold_split`), `scripts/queue_run.py`;
`RUN` `{O3}` (awaited).
**Status** PRE-REGISTERED, NOT YET DISCHARGED — awaits `{O3}` · **Relevance** METHOD
"""

e4 = f"""
### {M4} — PRE-REGISTERED rule X4: is RWM still ahead of baselines matched to its size? · **NEW**
**Entered before any of its data exists.** No run of X4's queue has been trained: no `results/baseline_run_*_matched_seed*.json`
and no `runs/baseline_*_matched_seed*` exist, and `{O4}` does not exist. The only training of a matched baseline so far is
20-iteration timing probes, {len(probes4)} of them, F1's and round 1's ({", ".join(f"`{x}`" for x in probes4)}), none of which
saved a checkpoint or was scored. The script that computes every reading below,
`{S4}` (SHA-256 `{sha4}`), is committed in the same commit as this text, whose subject begins `PRE-REGISTER`, and refuses to
compute the rule unless this entry records its SHA-256. Before that commit, on these bytes, it ran only its synthetic
self-test and its `--assert-only` mode, which re-scores the committed Table S7 baselines and computes no reading: assertions
(a)-(c) passed. A dry run of `reading()` on untrained matched baselines, from a harness outside the repository, also ran, and
showed a non-finite score raising `CannotDischarge`. The outputs of both, each naming this SHA-256, are in the session's
evidence folder. This is round 4's rule
X4 (PLAN Annex 2, objection O2, ruling W2).

**Exploratory, and bounded.** It never re-opens M-75, M-76 or any discharged rule, and nothing here is read as bearing on them.
M-76's own Licenses line holds for it: architecture at a fixed regime, not the original's claim.

**Known before this rule** (its motivation): M-76 returned {m76} with the Table S7 sizes (`results/baselines_verdict.json`),
whose parameter counts differ from RWM's {rwm:,}-parameter state pathway: MLP {npar['mlp_s7']:,}, transformer
{npar['transformer_s7']:,}, RSSM {npar['rssm_s7']:,} (`results/baseline_verification.json`).

**Variants.** `docs/presubmission/BASELINE_SPECS.md` row 33 (MLP, width 295; {npar['mlp_matched']:,} parameters) and row 34
(transformer, d_model 160, learned positions; {npar['transformer_matched']:,}), each within ±5% of {rwm:,} (asserted), built by
`src/baselines`' `build(arch, "matched", cfg)`. Trained autoregressively, otherwise exactly as M-76 (`scripts/train_baseline.py`).
The matched RSSM is not run (ruling W2).

**Runs.** Seeds 0-2, 2,500 iterations, held-out {{1, 8}}: 6 runs, projected {tim['x4']['projected_h']:.2f} CPU-hours against X4's
10 (`results/round4_queue_timing.json`). Annex 2's fallback (seeds 0-1) does not apply.

**Statistic and test, M-76's, imported from `scripts/verdict_baselines.py`:** per baseline b, D_b = the mean over §5's four
held-out trajectories of [3-seed mean relative-L1 of b − 3-seed mean relative-L1 of RWM] at h = 368, RWM being Arm A (32, 8) at
2,500 iterations, seeds 0-2 (`differences`); the exact 256-resample cluster bootstrap and two-sided p, and Holm at α = 0.05 over
the family of two, MLP before transformer (`family`). Scoring is `scripts/baselines_eval.py`'s `evaluate`, imported.

**Reading:** the label `verdict_baselines.overall` returns for the family of two, first match:
1. **A MATCHED BASELINE AHEAD:** either baseline BASELINE BETTER;
2. **RWM AHEAD OF BOTH:** both RWM BETTER;
3. **PARTIAL:** one RWM BETTER and the other CANNOT BE SETTLED;
4. **CANNOT BE SETTLED:** neither resolves.

M-76's own labels say "A BASELINE AHEAD" and "RWM AHEAD OF ALL THREE". For two size-matched baselines the first gains "MATCHED"
and "ALL THREE" becomes "BOTH"; the function, the order of outcomes and the other two labels are M-76's. The self-test asserts a
defined label for every one of the nine combinations of two per-baseline results.

**Alongside, never governing:** the same test at h = 100 and h = 32 (relative-L1); the per-trajectory differences; each run's
wall clock and seconds per iteration, the parameter counts, and F1's probe cost per iteration.

**Assertions, before any reading** (a failure stops the run with no reading):
- **(a)** `baselines_eval.evaluate`, run on the original-size autoregressive baselines (MLP, RSSM, transformer), reproduces
  `results/baselines_eval.json` on every per-trajectory value they share, to 1e-6;
- **(b)** `verdict_baselines.family` on that output, with M-76's names, reproduces `results/baselines_verdict.json`'s M-76
  governing verdict and its per-baseline D, p and interval, to 1e-12;
- **(c)** each matched model as built is within ±5% of RWM's state pathway, and `BASELINE_SPECS.md` rows 33 and 34 are not
  UNVERIFIED;
- **(d)** every matched run's record names its architecture, regime ar, spec matched, 2,500 iterations, its seed, held-out
  {{1, 8}}, the built parameter count and finite losses, and its weights exist. The records say rule M-76, the trainer's label for
  regime ar (`scripts/train_baseline.py`), and the evaluator's file says M-75 and M-76; they are X4's runs.

**Failure.** A non-finite score (`verdict_baselines` raises `CannotDischarge`, M-76's failure clause), or any internal check
failing, stops the run with a `.blocked` record beside its output and no reading.

**Gate.** No session evaluates a run of the round-4 queue before F5 (PLAN §1.2 rule 5).

**Caveat, in every sentence that reports it:** matching the parameter count is one axis; the shapes and settings stay our
reading of Table S7.

**Deviations from PLAN Annex 2, all stated above:** the two reading labels; assertions (b)-(d) and the failure clause added.

{common_tail.format(S=S4, vals='alongside', what='variants, seeds, iterations, arena, horizons, statistic, test or labels')}
**Evidence** `SRC` `{S4}`, `scripts/train_baseline.py`, `scripts/queue_run.py`; `RUN` `{O4}` (awaited).
**Status** PRE-REGISTERED, NOT YET DISCHARGED — awaits `{O4}` · **Relevance** METHOD
"""

Rt = open(RES, encoding="utf-8").read()
row = re.search(r"^\| `M-` methodological findings \| (\d+) \|", Rt, re.M)
assert row and int(row.group(1)) == nm - 1, row
Rt = Rt.replace(row.group(0), f"| `M-` methodological findings | {nm + 1} |", 1)
os.makedirs(BAK, exist_ok=True)
shutil.copy(L, os.path.join(BAK, "FINDINGS_LEDGER.md.prereg.bak"))
shutil.copy(RES, os.path.join(BAK, "RESULTS.md.prereg.bak"))
open(L, "w", encoding="utf-8").write(led.rstrip("\n") + "\n" + e3 + e4)
open(RES, "w", encoding="utf-8").write(Rt)
print(f"appended {M3} ({S3} SHA-256 {sha3}) and {M4} ({S4} SHA-256 {sha4}); RESULTS.md M- {nm - 1} -> {nm + 1}")
