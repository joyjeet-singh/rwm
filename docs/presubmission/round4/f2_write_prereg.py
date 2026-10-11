"""F2 item 3: append the pre-registrations of rules X6, X7 and X8 (PLAN round 4, Annex 2) to FINDINGS_LEDGER.md as M-88,
M-89 and M-90, and move RESULTS.md's M- row. F1's f1_write_prereg.py, adapted. X5 is NOT RUN (D-38) and has no entry.

Every motivation figure is read from an artifact; each script's SHA-256 is computed from the file as it stands, and the
claims each entry makes about what ran before the freeze are checked against the saved output of those runs (their logs
name the SHA-256). Writes .bak copies outside the repository, refuses to run twice, and asserts no reading exists.
Run from the repository root:  $PY docs/presubmission/round4/f2_write_prereg.py
"""
import hashlib
import json
import os
import re
import shutil

L, RES = "FINDINGS_LEDGER.md", "RESULTS.md"
BAK = "/Users/Shared/rwm_verify/evidence/R4F2"
S = {"X6": "scripts/x6_stepsize_short_units.py", "X7": "scripts/x7_loeo_recalibration.py", "X8": "scripts/x8_released_pairing.py"}
O = {"X6": "results/x6_stepsize_short_units.json", "X7": "results/x7_loeo_recalibration.json", "X8": "results/x8_released_pairing.json"}
EXTRA = ["results/x8_sweep_eval_offset0.json", "results/x8_baselines_eval_offset0.json"]
for p in list(O.values()) + EXTRA:
    assert not os.path.exists(p) and not os.path.exists(p + ".blocked"), f"{p} exists: the rule can no longer be pre-registered"
led = open(L, encoding="utf-8").read()
nm = max(int(n) for n in re.findall(r"^### M-(\d+) ", led, re.M)) + 1
IDS = {"X6": f"M-{nm}", "X7": f"M-{nm + 1}", "X8": f"M-{nm + 2}"}
assert IDS == {"X6": "M-88", "X7": "M-89", "X8": "M-90"}, IDS
for k in IDS:
    assert f"PRE-REGISTERED rule {k}" not in led
    assert re.search(rf'^RULE_ID = "{IDS[k]}"$', open(S[k]).read(), re.M), k
sha = {k: hashlib.sha256(open(p, "rb").read()).hexdigest() for k, p in S.items()}
import ast
def modules_of(path):
    tree = ast.parse(open(path, encoding="utf-8").read())
    node = next(n for n in tree.body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "MODULES")
    return [m for m in ast.literal_eval(node.value) if m != path]
mods = {k: modules_of(p) for k, p in S.items()}
modline = lambda k: ("**The code it imports, at pre-registration** (each file's SHA-256, also recorded in the output's "
                     "`code_sha256`): " + "; ".join(f"`{m}` `{hashlib.sha256(open(m, 'rb').read()).hexdigest()}`" for m in mods[k]) + ".")
J = lambda p: json.load(open(p))
LOG = lambda n: open(os.path.join(BAK, n), encoding="utf-8").read()
for k, n_as in (("X6", "(a)-(c)"), ("X7", "(a)-(b)"), ("X8", "(a)-(d)")):
    a, d = LOG(f"{k.lower()}_assert_only.log"), LOG(f"{k.lower()}_dryrun.log")
    assert f"script SHA-256 {sha[k]}" in a and f"--assert-only: assertions {n_as} pass" in a and "FAIL" not in a, k
    assert f"{os.path.basename(S[k])} SHA-256 {sha[k]}" in d and "DRY RUN main()" in d, k

# ---- motivation, read from artifacts (all known before these rules)
e7 = J("results/e7_free_baselines.json")
e7s = {r["baseline"]: r for r in e7["baselines"]}["step-size"]
d3 = J("results/task_d3_perhorizon.json")["quantities"]["epistemic"]["verdict"]
alg = J("results/alignment_by_horizon.json")["released"]["summary"]["all_ten_n20"]["8"]["rel_l1"]
v74 = J("results/mn_sweep_verdict.json")["verdict"]
vb = {k: v["verdict"] for k, v in J("results/baselines_verdict.json")["rules"].items()}
v23 = J("results/task5_analysis.json")["m23"]["verdict"]
f4 = lambda x: f"{x:+.4f}"
import sys
sys.path.insert(0, "scripts"); sys.path.insert(0, "src")
import m64_short_units as M64  # noqa: E402  (the index builder only: it counts units and rolls nothing out)
n_units = {h: M64.build_index(list(range(10)), h)[3] for h in (32, 100)}

common = lambda k, what, vals: f"""**What the discharging session may and may not do.** Session F2 runs `{S[k]}` as committed, having asserted its SHA-256
equals the one recorded here; records the reading exactly as the script returns it, with the {vals} values, in a new
ledger entry; and changes only this entry's Status line. Not: change the {what}; add a reading; or read any number here as
bearing on a discharged rule.
**Evidence** `SRC` `{S[k]}`; `RUN` `{O[k]}` (awaited).
**Status** PRE-REGISTERED, NOT YET DISCHARGED — awaits `{O[k]}` · **Relevance** METHOD
"""

prov = lambda k, extra: f"""**Entered before any of its readings exists.** `{O[k]}` does not exist{extra}. The script that computes every reading
below, `{S[k]}` (SHA-256 `{sha[k]}`), is committed in the same commit as this text, whose subject begins `PRE-REGISTER`,
and refuses to compute the rule unless this entry records its SHA-256. Before that commit, on these bytes, it ran only its
synthetic self-test, its `--assert-only` mode, which computes only cases committed artifacts already hold, and a dry run
of its whole `main()` from a harness outside the repository"""

e6 = f"""
### {IDS['X6']} — PRE-REGISTERED rule X6: does ensemble disagreement beat the model's own predicted step size on more, shorter units? · **NEW**
{prov('X6', '')}, with the short-unit panels replaced by synthetic arrays. Every assertion passed. The outputs of all three, each naming
this SHA-256, are in the session's evidence folder. This is round 4's rule X6 (PLAN Annex 2, objection O4). Inference only, on
the released checkpoint.

**Exploratory, and bounded.** It never re-opens M-51, M-52, M-64 or any discharged rule, and nothing here is read as bearing on
them.

**Known before this rule** (its motivation): on the released checkpoint's 20 independent 400-step trajectories at h = 368,
disagreement's margin over the predicted step size is {f4(e7s['margin'])} [{f4(e7s['margin_ci'][0])}, {f4(e7s['margin_ci'][1])}]
(`results/e7_free_baselines.json`). M-51 compared it with its MDE, {e7['thresholds']['margin']:.4f}, not with zero, and returned
{e7['verdict']}. With 20 trajectories, the comparison with step size was not settled at the size M-51 asked for.

**Model.** The released checkpoint, ensemble of 5, as released.

**Units.** All ten episodes, non-overlapping units of 32 + h rows within each episode, built by M-64's index builder
(`m64_short_units.build_index`, imported), at h ∈ {{32, 100}}: {n_units[32]} units at h = 32 and {n_units[100]} at h = 100, counted two ways (assertion
(d)). **h = 100 governs**, the method's imagination horizon.

**Panel.** `e7_free_baselines.load_panel(starts, length)`, imported. It is the panel M-51 read: the rollout at the causal pairing from 32
history rows, |error| as the per-step sum over the 45 state dimensions, disagreement as the applied epistemic scalar, and
`e7_free_baselines.baselines()`'s step size, ‖μ_t − μ_(t−1)‖. F2 gave `load_panel` the `starts` and `length` arguments.
With its defaults it rewrites `results/e7_free_baselines.json` and its power record byte-identically.

**Statistic.** M-51/M-52's margin, r(disagreement, |error|) − r(step size, |error|), each a Pearson correlation over every
(unit, step) cell (`e7_free_baselines._corr`, imported). Paired: both correlations are recomputed on the same resampled units.
**Interval:** 95%, over whole units, Annex 2's recipe. That is 20,000 Monte Carlo resamples of the units with replacement from
`numpy.random.default_rng(0)`, the statistic recomputed on each, with percentiles 2.5 and 97.5. The resampling loop is
`e7_free_baselines`' own. It is a closure inside that script's `main()`, so it is copied, not imported. Assertion (b) shows the copy, at
e7's settings, reproduces e7's committed intervals.

**MDE, computed and printed before the reading:** M-51's method (`e7_free_baselines --power`) at this n, from disagreement, |error|
and the forecast index only, so the step size is not touched. It is the bootstrap SD of the margin over the forecast index, from
4,000 resamples at seed 20260829, times z_0.975 + z_0.80. The same SD for the step-size margin itself is reported alongside, after
the reading. Neither enters the reading.

**Reading**, at h = 100:
- **DISAGREEMENT BEATS STEP SIZE** if the interval's lower bound > 0;
- **STEP SIZE BEATS DISAGREEMENT** if its upper bound < 0;
- **NOT RESOLVED** otherwise.

**Alongside, never governing:**
- h = 32, with the label it would carry;
- the partial r(disagreement, |error| | step size) (`e7_free_baselines._partial`) at both horizons, with the same interval;
- both correlations, and the counts.

**Assertions, before any reading** (a failure stops the run with no reading):
- **(a)** on the 400-step unit at h = 368, the imported functions reproduce `results/e7_free_baselines.json`'s r values for every
  baseline and the step-size margin, to 1e-9; `load_panel(starts, length)` given the default starts equals the default call
  bitwise;
- **(b)** the resampling loop at e7's settings (4,000 resamples, `default_rng(20260829)`, shared in e7's order) reproduces e7's
  step-size margin and partial intervals, to 1e-9;
- **(c)** the MDE computation at M-51's settings reproduces `results/e7_free_baselines_power.json`, to 1e-9;
- **(d)** at each h, M-64's two unit counts agree, and every unit lies inside one episode.

**Failure.** A non-finite value in the reading, or any internal check failing, stops the run with a `.blocked` record beside
its output and no reading.

**Caveats, in every sentence that reports it:**
- every unit is in the released checkpoint's training data;
- the units are non-overlapping within an episode, but they share the ten episodes, and the interval resamples units, not
  episodes;
- the statistic is a correlation over (unit, step) cells, not a ranking of units.

**Deviations from PLAN Annex 2, all stated above:**
- the resampling loop is copied, not imported, because e7's is a closure; it is asserted equal to e7's;
- `load_panel` gained arguments whose defaults are unchanged;
- the step-size margin's own SD and MDE (after the reading) and the partial's interval are added alongside;
- the failure clause is added.

{modline('X6')}

{common('X6', 'model, units, horizons, panel, statistic, interval, MDE method or thresholds', 'MDE and alongside')}"""

e7_ = f"""
### {IDS['X7']} — PRE-REGISTERED rule X7: §6.7's per-horizon recalibration, fitted on nine episodes and scored on the tenth · **NEW**
{prov('X7', '')}, with the ten episodes' rollouts replaced by synthetic arrays. Every assertion passed. The outputs of all three, each
naming this SHA-256, are in the session's evidence folder. This is round 4's rule X7 (PLAN Annex 2, objection O5). Inference
only, on the released checkpoint.

**Exploratory, and bounded.** It never re-opens M-69, M-70 or any discharged rule, and nothing here is read as bearing on them.

**Known before this rule** (its motivation): §6.7's per-horizon multiplier was fitted on one held-out episode and scored on the
other, in both directions: two folds of two trajectories each. Its epistemic multiplier landed within 10 points of 68.27% in
{d3['per_horizon_cells_calibrated']} of {d3['n_cells']} held-out cells, against {d3['constant_cells_calibrated']} for one constant multiplier
(`results/task_d3_perhorizon.json`). Two folds of two trajectories cannot resolve a single cell.

**Model.** The released checkpoint, ensemble of 5, as released. The epistemic term governs; the aleatoric is alongside.

**Trajectories.** Each episode's two non-overlapping 400-step trajectories (32 history rows, 368 forecast rows), 20 in all, from
`task_d3_perhorizon.episode_rollout`, imported.

**Design.** For each episode e:
- fit the per-horizon multiplier c_h on the other nine episodes' 18 trajectories, with §6.7's fitting function
  (`task_d3_perhorizon.fit_scalar`, imported: the smallest c reaching 68.27% ±1σ coverage, by bisection in log space);
- score ±1σ coverage on e's two trajectories, with §6.7's coverage (`task_d3_perhorizon.cover`): every finite, positive-σ cell over
  forecast steps 1..h × 45 state dimensions.

Each trajectory is scored once, by a multiplier not fitted on it. Per trajectory, coverage is reduced to (covered, valid) counts
and pooled over the 20 trajectories (`task_d3_cross_model.counts` and `pooled`, imported; assertion (b) shows this is an exact
reduction of `cover()`).

**Interval.** 95%, over whole trajectories: 20,000 Monte Carlo resamples of the 20 trajectories, `numpy.random.default_rng(0)`, one
draw shared by every horizon, quantity and variant, with percentiles 2.5 and 97.5. This is `task_d3_cross_model`'s recipe and
Annex 2's.

**Reading**, per horizon h ∈ {{1, 8, 32, 100, 128, 368}}, against the band 68.27% ± 10 points, [58.27%, 78.27%] (§6.7's target and
tolerance, read from `task_d3_perhorizon.TARGET` and `task_d3_cross_model.TOL`):
- **WITHIN BAND** if the interval lies inside the band (its edges count as inside);
- **OUTSIDE BAND** if it lies wholly outside it;
- **UNRESOLVED** otherwise.

**Governing summary**, for the epistemic term: **"WITHIN BAND AT k OF 6 HORIZONS"**.

**Alongside, never governing:**
- the aleatoric term under the same design;
- the constant-multiplier version of the same design (one c fitted at h = 1 on the nine episodes, §6.7's constant recipe, scored
  at every h);
- the coverage before any multiplier;
- the spread of the fitted c_h across the ten folds.

**Assertions, before any reading** (a failure stops the run with no reading):
- **(a)** §6.7's own two-fold design, rerun through the imported functions, reproduces every cell of `results/task_d3_perhorizon.json`,
  to 1e-9 (c relative to max(1, |c|)): each fit's c, its coverage after and its coverage before, per-horizon and constant, in
  both quantities;
- **(b)** `counts()` pooled over a fold's trajectories equals `cover()` on them, to 1e-12;
- **(c)** every episode yields two 400-step trajectories, 20 in all.

**Failure.** A non-finite value in the reading, or any internal check failing, stops the run with a `.blocked` record beside
its output and no reading.

**Caveat, in every sentence that reports it:** unseen by the multiplier, not by the model. The released checkpoint trained on all
ten episodes, so every scored trajectory is in its training data.

**Deviations from PLAN Annex 2, all stated above:**
- the interval's two-line loop composes imported pieces with the cross-model recipe;
- the coverage before any multiplier is added alongside;
- the band's edges count as inside;
- the failure clause is added.

{modline('X7')}

{common('X7', 'model, trajectories, design, fitting or coverage function, interval, band or labels', 'alongside')}"""

e8 = f"""
### {IDS['X8']} — PRE-REGISTERED rule X8: would any verdict change under the released evaluation's action timing? · **NEW**
{prov('X8', ', nor do its offset-0 score files')}. In that dry run "offset 0" was made to score at offset 1, so every value it
computed is a committed offset-1 value. Every reading came back SAME VERDICT, with no alongside change. Every assertion passed. The
outputs of all three, each naming this SHA-256, are in the session's evidence folder. This is round 4's rule X8 (PLAN Annex 2,
objection O6). Inference only.

**Exploratory, and bounded.** It never re-opens M-23 or M-74–M-76, and their verdicts are unchanged whatever it returns. It says
what each would have returned had our models been scored with the released evaluation's pairing.

**Known before this rule** (its motivation): the released evaluation pairs each prediction with the action one step stale, which
raises the released checkpoint's relative-L1 error at h = 8 by {alg['pct']:+.1f}% over all ten episodes
(`results/alignment_by_horizon.json`). Every rule here was scored at the causal pairing. Their committed verdicts: M-74 {v74}
(`results/mn_sweep_verdict.json`), M-75 {vb['M-75']} and M-76 {vb['M-76']} (`results/baselines_verdict.json`), and M-23 {v23}
(`results/task5_analysis.json`, seed 1).

**The pairing.** Offset 1, the causal pairing, pairs the prediction of state i with action i. Offset 0, the released evaluation's
pairing, pairs it with action i − 1. Each rule's own evaluator scores through `scripts/mn_sweep_eval.py`'s
`score(..., action_offset)`. F2 gave it that argument; its default, 1, rewrites `results/mn_sweep_eval.json` and
`results/baselines_eval.json` byte-identically. Offset 0 moves every action one row later, repeats the window's first row, and
rolls out at the causal pairing (`mn_sweep_eval._pairing`). So one definition reaches RWM and every baseline. For RWM it equals
the native `action_offset=0` (assertion (d)), and RWM never reads the repeated row. The RSSM reads it at its first filtering step
only.

**Re-scored at offset 0, each with its rule's own evaluator and statistic, imported:**
- **M-74's sweep:** the centre and 8 configurations, seeds 0-2, 2,500 iterations; `mn_sweep_eval`'s arena and score, then
  `verdict_mn_sweep`'s differences and family.
- **M-75's and M-76's baselines:** 6 families, seeds 0-2, 2,500 iterations, and RWM; `baselines_eval.evaluate`, then
  `verdict_baselines.one_rule`.
- **The A/B comparison:** Arm A and Arm B, seeds 0-2. Its reading is M-23's three conditions applied with three seeds, at
  relative-L1, h = 368:
  1. Arm A leads at 2,500 and at 10,000 iterations: the gap, seed-mean B − seed-mean A averaged over the held-out trajectories,
     is positive;
  2. the 95% interval of the 10,000-iteration gap has its lower bound above zero;
  3. the per-episode gap at 10,000 is positive in all ten episodes.

  The interval and the per-episode sign are the by-horizon table's: `review_bootstrap_unit.boot_cluster` at 20,000 draws, seed 0,
  and per-episode means with each episode rolled out as its own batch, as `a1_ab_by_horizon` does. The label follows the code that
  discharged M-23 (`task5_analyse.py`): REPRODUCES AT LONG HORIZON if all three hold, FAILS TO REPRODUCE if condition 1 fails,
  CANNOT BE SETTLED otherwise. M-23's text says it fails only if Arm A does not lead at 10,000; the two differ only if Arm A trails
  at 2,500 and leads at 10,000.

**Reading, per rule (M-74, M-75, M-76, the A/B comparison): SAME VERDICT, or VERDICT WOULD CHANGE TO ⟨label⟩.**
- M-74, M-75 and M-76 are compared with their committed verdicts.
- The A/B comparison is compared with the same three-seed computation at offset 1, because M-23 itself was discharged on seed 1.

**Alongside, for each rule:** every reading in its alongside set that changes between offset 1 and offset 0.
- M-74: each held-out branch at every horizon and metric, the in-sample branches at h = 100 and 368, and each configuration's
  per-episode sign over all ten episodes (its positive and negative counts).
- M-75 and M-76: the same, for their alongside and in-sample families, and each baseline's per-episode sign.
- The A/B comparison:
  - M-23 as discharged: seed 1, with its own bootstrap of 10,000 resamples, seed 0, which assertion (c) shows is
    `boot_cluster` on one seed;
  - M-23's own alongside set, with three seeds: its three conditions at h = 8 (held-out), on nRMSE (h = 368, held-out) and in the
    in-sample arena (h = 368). Its h = 168 on 200-step trajectories is not computed, because no evaluator for 200-step windows
    takes an offset;
  - the three gap statuses `task5_analyse.py` reported as M-23's secondaries, with three seeds at 10,000: h = 8 held-out, and h = 368
    and h = 8 in-sample;
  - the by-horizon table at 10,000: each horizon's interval excluding zero, each horizon's per-episode sign count, and the trend's
    reading (`a1_ab_by_horizon.trend_reading`).

**Assertions, before any reading** (a failure stops the run with no reading):
- **(a)** offset 1 through this script reproduces every per-trajectory value of `results/mn_sweep_eval.json` and
  `results/baselines_eval.json` to 1e-6, and the committed verdicts and alongside branches exactly.
- **(b)** offset 1 reproduces each of these to 1e-6 relative to max(1, |value|):
  - `results/a1_ab_by_horizon.json`: its per-trajectory means, gaps, intervals, sign tests and trend reading;
  - `results/task5_analysis.json`'s seed-1 M-23 gaps, intervals, per-episode gaps and verdict;
  - Arm A's 2,500- and 10,000-iteration values in `results/mn_compute_matched.json`;
  - Arm B's 2,500-iteration values in `results/x3_armB_2500_reference.json`.

  The tolerance is relative because these errors reach 7, where float32 rounding alone is about 1e-6.
- **(c)** `boot_cluster` on one seed reproduces `task5_analyse.py`'s M-23 bootstrap exactly: the same draws.
- **(d)** offset 0 is the released pairing. For Arm A at 10,000 on the held-out pair, `score` at offset 0 equals the model's native
  offset-0 rollout (to 1e-12), and the ratio of the two offsets' errors reproduces `results/alignment_by_horizon.json`'s per-seed
  stale-pairing change to 1e-6. Before the reading, the native equality is also checked for every sweep configuration with
  M < 32, seeds 0-2, on the held-out arena.

**Failure.** A non-finite score, or any internal check failing, stops the run with a `.blocked` record beside its output and no
reading.

**Caveat, in every sentence that reports it:** our models under the released pairing; it says nothing direct about the original
papers' printed numbers.

**Deviations from PLAN Annex 2, all stated above:**
- offset 0 is made by moving the actions, for every model;
- the A/B reading's three-seed form, and its comparison with offset 1; its condition 1 uses the point gap, as the by-horizon table
  reports it, where `task5_analyse.py` used the bootstrap mean for seed 1;
- some logic is copied, not imported, and each copy is asserted: `task5_analyse.py`'s M-23 label and gap-status logic (it runs on
  import); `a1_ab_by_horizon`'s per-episode gap and by-horizon fields and `verdict_mn_sweep`'s per-episode sign (inside their
  `main()`); and task5's bootstrap in assertion (c);
- each rule keeps its own interval, so the A/B intervals at n = 4 are Monte Carlo (20,000 draws, 10,000 for seed 1), not Annex 2's
  exact enumeration;
- M-23's h = 168 on 200-step trajectories is not computed;
- the per-episode batching;
- the relative tolerance in (b);
- the failure clause.

**The rules already pre-registered.** M-86 (X3) imports `mn_sweep_eval`'s `score` and M-87 (X4) imports `baselines_eval`'s
`evaluate`, both edited by F2 to take an offset. Both edits keep the defaults, and with them each producer rewrites its committed
artifact byte-identically. M-86's and M-87's scripts call them at the defaults, so neither rule's computation changes.

{modline('X8')}

{common('X8', 'models, seeds, pairing, evaluators, statistics, alongside sets or labels', 'alongside')}"""

Rt = open(RES, encoding="utf-8").read()
row = re.search(r"^\| `M-` methodological findings \| (\d+) \|", Rt, re.M)
assert row and int(row.group(1)) == nm - 1, row
Rt = Rt.replace(row.group(0), f"| `M-` methodological findings | {nm + 2} |", 1)
os.makedirs(BAK, exist_ok=True)
shutil.copy(L, os.path.join(BAK, "FINDINGS_LEDGER.md.prereg.bak"))
shutil.copy(RES, os.path.join(BAK, "RESULTS.md.prereg.bak"))
open(L, "w", encoding="utf-8").write(led.rstrip("\n") + "\n" + e6 + e7_ + e8)
open(RES, "w", encoding="utf-8").write(Rt)
print("appended " + ", ".join(f"{IDS[k]} ({S[k]} SHA-256 {sha[k]})" for k in IDS) + f"; RESULTS.md M- {nm - 1} -> {nm + 2}")
