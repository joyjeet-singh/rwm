"""R1 item 2: append the pre-registration of rule X2 (PLAN Annex 1) to FINDINGS_LEDGER.md as the next M- entry,
and move RESULTS.md's M- row. The motivation figures are read from the artifacts (R-76's released-checkpoint half,
R-79's Arm A re-measurement), and the script's SHA-256 is computed from the file as it stands. Writes .bak copies,
refuses to run twice, and asserts results/action_sensitivity.json does not exist. Run from the repository root.
"""
import hashlib
import json
import os
import re
import shutil

L, RES = "FINDINGS_LEDGER.md", "RESULTS.md"
SCRIPT, ART = "scripts/action_sensitivity.py", "results/action_sensitivity.json"
assert not os.path.exists(ART), f"{ART} exists: the rule can no longer be pre-registered"
led = open(L, encoding="utf-8").read()
nm = max(int(n) for n in re.findall(r"^### M-(\d+) ", led, re.M)) + 1
MID = f"M-{nm:02d}"
assert MID == "M-84", MID                                 # the script's RULE_ID
assert "PRE-REGISTERED rule X2" not in led
assert re.search(r'^RULE_ID = "M-84"$', open(SCRIPT).read(), re.M)
sha = hashlib.sha256(open(SCRIPT, "rb").read()).hexdigest()

A = json.load(open("results/alignment_by_horizon.json"))
rs = A["released"]["summary"]
am = A["arm_a"]["10000"]
pct = lambda v: f"{v:+.1f}%"
ci = lambda c: f"[{c[0]:.1f}, {c[1]:.1f}]"
m = lambda h: am["summary_three_seed_mean_pct"][str(h)]["rel_l1"]
ex = lambda h: all(am["summary_per_seed"][s][str(h)]["rel_l1"]["ci95_pct"][0] > 0 for s in ("0", "1", "2"))
assert ex(100) and ex(368) and not ex(1) and not ex(8)
r8 = rs["all_ten_n20"]["8"]["rel_l1"]["pct"]

entry = f"""
### {MID} — PRE-REGISTERED rule X2: do our trained models condition their forecasts on the action they are given? · **NEW**
**Entered before any of its readings exists.** `{ART}` does not exist. The script that computes every reading below,
`{SCRIPT}` (SHA-256 `{sha}`), is committed in the same commit as this text, whose subject begins
`PRE-REGISTER`, and refuses to compute the rule unless this entry records its SHA-256. Before that commit it ran only
its synthetic self-test (untrained weights on synthetic data: the hook, assertions (b) and (c), the statistic, the
interval and all four outcomes) and its `--assert-only` mode, which rolls out only the cases committed artifacts already
hold (I0 and I1 for the released checkpoint and for Arm A's held-out pair, I0 elsewhere) and computes no reading:
assertion (a) passed. A dry run of its whole pipeline (both phases, every assertion, the measures and the output) on
synthetic data with untrained weights also ran, from a harness outside the repository that replaced the data, the
weights and assertion (a). The ordering can be checked from `git log`. This is round 3's rule X2 (PLAN Annex 1, ruling V1).

**Exploratory, and bounded.** It never re-opens M-23, M-64, M-74, M-75 or M-76. Their verdicts are unchanged whatever
it returns, and nothing here is read as bearing on them.

**Known before this rule** (its motivation; both post hoc):
- R-76: fed the action one step stale, the released checkpoint's relative-L1 error at h = 1 rises by
  {pct(rs['held_out_n4']['1']['rel_l1']['pct'])} {ci(rs['held_out_n4']['1']['rel_l1']['ci95_pct'])} on the held-out pair and by
  {pct(rs['all_ten_n20']['1']['rel_l1']['pct'])} {ci(rs['all_ten_n20']['1']['rel_l1']['ci95_pct'])} over all ten episodes, and at h = 8 by
  {pct(r8)} over all ten.
- R-79, which re-measured R-76's Arm A half after S-21 withdrew it: our Arm A at 10,000 iterations, on the held-out pair,
  changes by {pct(m(1))} at h = 1, {pct(m(8))} at h = 8 and {pct(m(368))} at h = 368 (3-seed mean). Every seed's interval
  excludes zero from h = 100 and none does at h = 1 or 8.
- Round 3's plan was written on R-76's void figures, which said our models barely notice the shift. They do notice it at
  long horizons. Whether they use the action at the horizons where its effect should first show is not settled by the
  stale shift, perhaps because consecutive actions differ little (X2's context figures measure how little). A world model that does not respond to actions cannot serve
  policy optimisation, which is what RWM is for. X2 asks the question directly. Its readings are new.

**Models** (inference only, existing weights):
- **Arm A**, seeds 0-2, at 2,500 and at 10,000 iterations (`runs/armA_seed{{s}}_10k/weights_{{2500,10000}}.pt`; the 2,500
  files are asserted byte-identical to the 2,500-iteration runs'). **This model gets the readings.**
- **Arm B**, the same seeds and checkpoints. Reported alongside only.
- **The released checkpoint.** Reported alongside only.

**Arenas** (400-step trajectories: 32 history rows, then 368 forecast rows; horizons {{1, 8, 32, 100}}, cumulative over
forecast steps 1..h, relative-L1 as section 3.1 defines it):
- for Arm A and Arm B, the sweep evaluator's **in-sample arena** (`mn_sweep_eval.arena()` over the eight training episodes:
  16 independent trajectories) and the **held-out pair** (4);
- for the released checkpoint, **all ten episodes** (20; its own training data) and the held-out pair (4).

**Interventions.** Only the actions the forecast steps read change. Under offset 1 the forecast steps read rows 32..399
of each window: the first step reads rows 1..32 and later step i reads row i (the two `a_in` lines of `rollout()` in
`src/rwm_model.py` and `src/score_reference.py`). The history pairs are untouched, so the recurrent state that meets the
first forecast action is identical across interventions. A hook wraps `model.rollout` inside
`alignment_defect_ci.rollout`, imported.
- **I0 true:** offset 1, the reference.
- **I1 stale:** offset 0, round 2's N1.
- **I2 swap:** trajectory i takes the actions of trajectory (i + 1) mod n of the same arena, in its start order, at the
  same forecast rows.
- **I3 mean:** each action dimension at the forecast rows is replaced by its mean over the model's own training rows:
  every row of the eight training episodes for Arm A and Arm B, every row of all ten for the released checkpoint.
- **I4 noise:** true actions plus e ~ N(0, (k·σ_d)²) at the forecast rows, k ∈ {{0.1, 0.5}}, σ_d that dimension's
  standard deviation (ddof 0) over the same training rows. 8 draws: one array
  z = `numpy.random.default_rng(0).standard_normal((8, n, 368, 12))` per arena, shared by every model and both k,
  e = k·σ·z. A trajectory's I4 error is its mean over the draws.

**Measures**, per model × checkpoint × arena × horizon × intervention:
- **E** = err(I) / err(I0) − 1, in percent: N1's overstatement (`alignment_defect_ci.stats()`'s relative-L1 over a
  draw's trajectories) with I in place of offset 0. For Arm A and Arm B it is the mean over the three seeds of each
  seed's E. **Interval:** percentiles 2.5 and 97.5 over whole-trajectory resamples, one resample per draw for all three
  seeds and both interventions. Exact over all 256 at n = 4; 20,000 Monte Carlo draws
  (`default_rng(0).integers(0, n, (20000, n))`, `alignment_defect_ci`'s recipe) at n = 16 and n = 20. The per-draw value
  is computed from per-trajectory means, asserted equal to `alignment_defect_ci.stats()` on every point estimate.
- **Δ** (descriptive): the relative-L1 of the intervened forecast against the I0 forecast over steps 1..h, by
  `rollout_eval.relative_error()` with the I0 forecast as target (PLAN Annex 1 names `src/rwm_metrics.py`, which has no
  relative-L1; `src/rollout_eval.py`'s is the paper's). Mean over draws for I4 and over seeds for Arm A and Arm B.
  It is 0 for a model that ignores the action.
- **Context** (descriptive), over each arena's forecast rows:
  - the fraction of steps with a_t ≠ a_(t−1) in any dimension;
  - mean |a_t − a_(t−1)| ÷ mean |a_t − ā|, with ā the per-dimension mean over the arena's forecast rows;
  - the same ratio for the swap, mean |a_swap,t − a_t| ÷ mean |a_t − ā|.

**Assertions, before any reading** (a failure stops the run with no reading):
- **(a)** I0 and I1 reproduce `results/alignment_by_horizon.json` on every field the two share: the released checkpoint
  to 1e-9 in both arenas, Arm A to 1e-6 on the held-out pair (every seed, both checkpoints).
  - On the in-sample arena, and the held-out pair, Arm A's I0 reproduces `results/mn_compute_matched.json`'s
    `three_seed_mean_l1` at 2,500 and 10,000, h ∈ {{1, 8, 32, 100}}, to 1e-6.
  - Beyond Annex 1, also to 1e-6:
    - Arm B's I0 at 2,500 (held-out, h ∈ {{1, 8, 100}}, per seed) and the released checkpoint's I0 (held-out,
      h ∈ {{1, 8, 100}}), against `results/head_to_head_accuracy.json`;
    - Arm B's I0 at 10,000 (held-out, h = 100, per seed), against `results/task_d1_threeseed.json`.
- **(b)** The offset is applied. Under I1, for every model and every window, the action tensor the model received
  differs from I0's at one forecast step or more, and the forecast differs (max |difference| > 0). The fraction of
  forecast steps whose input differs is recorded.
- **(c)** (beyond Annex 1) Each intervention reaches exactly the forecast steps:
  - under I0, forecast step j receives row 32 + j;
  - under I2, I3 and I4, the history pairs the model receives are I0's, and every forecast-step action is the
    transformed row.

**The reading.** One for Arm A at 2,500 and one for Arm A at 10,000: E under I2 (swap), h = 8, on the in-sample arena
(n = 16), three-seed mean. The first matching outcome applies:
1. **RESPONDS TO THE ACTION:** the interval's lower bound > 0 and the point estimate ≥ +10%.
2. **ERROR FALLS WITH WRONG ACTIONS:** the interval's upper bound < 0.
3. **DOES NOT RESPOND MEASURABLY:** the interval's upper bound < +10%.
4. **UNRESOLVED:** otherwise.

Arm B (in-sample arena) and the released checkpoint (all ten episodes) get the same statistic and the label it would
carry, marked "alongside, not a reading".

**Why these choices** (PLAN Annex 1):
- **h = 8** is the training forecast length: long enough for an action's effect to reach the state, short enough that
  open-loop drift does not dominate.
- **The in-sample arena:** whether a model uses its input is a property of the model, not of generalisation, and 16
  units give a usable interval.
- **The swap** is a realistic action sequence that is wrong for that state.
- **10%** is a deliberately low bar: the one-step-stale action alone raises the released checkpoint's error at h = 8 by
  {pct(r8)} over all ten episodes.

**Cap:** 30 projected CPU-minutes. The projection is made after the first model of each phase (phase 1: I0 and I1 for
every model, then the assertions; phase 2: I2-I4). Beyond the cap the run stops before writing readings.

**Deviations from PLAN Annex 1, all stated above:**
- the motivation's Arm A figures, by ruling (A) of round 3's R0 (Annex 1 quoted R-76's void ones);
- Δ's function;
- the added assertions in (a) and (c);
- the released checkpoint's alongside arena is all ten episodes (Annex 1 names none);
- one noise array per arena, shared by every model;
- a projection after the first model of each phase.

**What the discharging session may and may not do.** Run `{SCRIPT}` as committed (R1), record each Arm A reading
exactly as the script returns it, with the alongside values, in a new ledger entry, and change only this entry's Status
line. Not: change the models, arenas, horizons, interventions, draws, seeds, statistic, interval, threshold or reading;
add an intervention; or read any number here as bearing on M-23, M-64 or M-74-M-76.
**Evidence** `SRC` `{SCRIPT}`; `RUN` `{ART}` (awaited).
**Status** PRE-REGISTERED, NOT YET DISCHARGED — awaits `{ART}` · **Relevance** METHOD
"""

R = open(RES, encoding="utf-8").read()
row = re.search(r"^\| `M-` methodological findings \| (\d+) \|", R, re.M)
assert row and int(row.group(1)) == nm - 1, row
R = R.replace(row.group(0), f"| `M-` methodological findings | {nm} |", 1)
shutil.copy(L, "/Users/Shared/rwm_verify/evidence/R3R1/FINDINGS_LEDGER.md.prereg.bak")
shutil.copy(RES, "/Users/Shared/rwm_verify/evidence/R3R1/RESULTS.md.prereg.bak")
open(L, "w", encoding="utf-8").write(led.rstrip("\n") + "\n" + entry)
open(RES, "w", encoding="utf-8").write(R)
print(f"appended {MID} (script SHA-256 {sha}); RESULTS.md M- {nm - 1} -> {nm}")
