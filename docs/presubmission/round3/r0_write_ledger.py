"""R0 fix, ruling (A) of DECISIONS.md#R0-arm-a-rollout-defect: the ledger correction.

Appends S-21 (withdraws R-76's Arm A claim on evidence) and R-79 (Arm A's stale-pairing sensitivity,
measured correctly), sets R-76's Status line to SUPERSEDED IN PART (the in-place edit the ruling
authorises, which ledger_check.py requires of a retracted CONTRIB entry), and moves RESULTS.md's
per-prefix rows for R- and S-. Every figure is read from results/alignment_by_horizon.json or
docs/presubmission/round3/r0_defect_check.json; every sentence that states a pattern asserts it first.
Writes .bak copies before any change and refuses to run twice. Run from the repository root.
"""
import json
import re
import shutil

L, RES = "FINDINGS_LEDGER.md", "RESULTS.md"
led = open(L, encoding="utf-8").read()
nr = max(int(n) for n in re.findall(r"^### R-(\d+) ", led, re.M)) + 1
ns = max(int(n) for n in re.findall(r"^### S-(\d+) ", led, re.M)) + 1
RID, SID = f"R-{nr:02d}", f"S-{ns:02d}"
assert (RID, SID) == ("R-79", "S-21"), (RID, SID)   # scripts/alignment_defect_ci.py's comment names R-79
assert "### R-79 " not in led and "### S-21 " not in led

A = json.load(open("results/alignment_by_horizon.json"))
DC = json.load(open("docs/presubmission/round3/r0_defect_check.json"))
assert DC["verdict"] == "DEFECT CONFIRMED"
chk = A["arm_a_offset1_reproduces_mn_compute_matched"]
assert all(v["reproduced"] for v in chk.values())
HS = [str(h) for h in A["horizons"]]
am = A["arm_a"]
pct = lambda v: f"{v:+.2f}%"
ci = lambda c: f"[{c[0]:+.2f}, {c[1]:+.2f}]"
mean = lambda it, h, k: am[it]["summary_three_seed_mean_pct"][h][k]
seed = lambda it, s, h: am[it]["summary_per_seed"][s][h]["rel_l1"]
S3 = ("0", "1", "2")

# the criterion fixed before the corrected figures existed (DECISIONS.md, commit 2a6bac1)
cells = [(it, h, k, mean(it, h, k)) for it in am for h in HS for k in ("rel_l1", "nrmse_form1")]
worst = max(cells, key=lambda c: abs(c[3]))
assert abs(worst[3]) > 1.0, "the criterion is met: R-76's claim stands, and no S- entry may be written"
n_out = sum(1 for c in cells if abs(c[3]) > 1.0)

# per seed, where every seed's relative-L1 interval excludes zero
excl = lambda c: c[0] > 0 or c[1] < 0
all_res = {it: [h for h in HS if all(excl(seed(it, s, h)["ci95_pct"]) for s in S3)] for it in am}
none_pos = {it: [h for h in HS if all(seed(it, s, h)["ci95_pct"][0] <= 0 for s in S3)] for it in am}
# the sentences below say: from h = 100 every seed's interval excludes zero (and is positive) at both
# checkpoints, and at h = 1 and 8 no seed's does
for it in am:
    assert all(h in all_res[it] for h in ("100", "128", "368")), (it, all_res[it])
    assert all(seed(it, s, h)["ci95_pct"][0] > 0 for s in S3 for h in ("100", "128", "368"))
    assert all(h in none_pos[it] for h in ("1", "8")), (it, none_pos[it])
first_all = {it: min(all_res[it], key=int) for it in am}
rs = A["released"]["summary"]["held_out_n4"]
hmax_rel = max(HS, key=lambda h: rs[h]["rel_l1"]["pct"])
hmax_a10 = max(HS, key=lambda h: mean("10000", h, "rel_l1"))
assert hmax_a10 == "368" and int(hmax_rel) <= 32, (hmax_a10, hmax_rel)

r1, r0 = DC["rows"], DC["max_abs_diff_from_committed"]
lo_as, hi_as = min(r["as_is"] for r in r1), max(r["as_is"] for r in r1)
lo_c, hi_c = min(r["committed"] for r in r1), max(r["committed"] for r in r1)
x10 = next(r for r in r1 if r["iterations"] == 10000 and r["arena"] == "held_out" and r["h"] == 1)

table = "\n".join(
    f"| {h} | {pct(mean('2500', h, 'rel_l1'))} / {pct(mean('2500', h, 'nrmse_form1'))} | "
    + ", ".join(f"{pct(seed('2500', s, h)['pct'])} {ci(seed('2500', s, h)['ci95_pct'])}" for s in S3)
    + f" | {pct(mean('10000', h, 'rel_l1'))} / {pct(mean('10000', h, 'nrmse_form1'))} | "
    + ", ".join(f"{pct(seed('10000', s, h)['pct'])} {ci(seed('10000', s, h)['ci95_pct'])}" for s in S3) + " |"
    for h in HS)

s_entry = f"""
### {SID} — "Our own checkpoints barely feel the stale pairing" · **NEW**
**Retracts** `R-76`, its Arm A half: the claim that our checkpoints are almost insensitive to the stale pairing, and the conclusion it drew about the model card
**What is retracted:** R-76's title clause "our own checkpoints barely feel it", and its paragraph saying that every
3-seed mean, in both metrics and at both checkpoints, is within 0.93% of zero, "so the model card's untested sentence that
a consumer feeding actions the other way 'will get materially worse numbers' is not borne out for these checkpoints".
§7.2 and the model card printed two of those figures, at h = 1 and h = 368 for the 10,000-iteration checkpoints.

**Why: they were never a measurement of our models.** `scripts/alignment_defect_ci.py`'s `rollout()` unpacked
`pred, *_ = model.rollout(...)`. The released checkpoint's rollout returns a tuple, so that took its prediction. Our
models' `RWMEnsemble.rollout` returns the prediction tensor itself, so the same line took the tensor's **first
trajectory**, and numpy compared that one forecast with all four held-out trajectories' truths. Three of the four
units were unrelated pairs, whose mismatch swamped any effect of the action. Under the causal pairing that path
gave Arm A a relative-L1 error of {lo_as:.2f} to {hi_as:.2f} at every checkpoint, arena and horizon tested, where the
sweep evaluator gives {lo_c:.2f} to {hi_c:.2f} for the same checkpoints and trajectories (at 10,000 iterations, held-out
pair, h = 1: {x10['as_is']:.4f} against {x10['committed']:.4f}). Taking the tensor whole reproduces the sweep evaluator to
{r0['unpacked']:.1e} (`docs/presubmission/round3/r0_defect_check.py`, causal pairing only).

**What replaces it:** `{RID}`, the same comparison measured correctly. Before any corrected figure existed, the
criterion for keeping the claim was fixed and committed: every corrected 3-seed mean within ±1.00% of zero, in both
metrics, at both checkpoints and all six horizons (`docs/presubmission/round3/DECISIONS.md`,
`R0-arm-a-rollout-defect`). It is not met: {n_out} of {len(cells)} means lie outside it, the largest
{pct(worst[3])} ({'relative-L1' if worst[2] == 'rel_l1' else 'nRMSE form 1'}, {int(worst[0]):,} iterations, h = {worst[1]}).

**What is not retracted:** R-76's half on the released checkpoint. `alignment_defect_ci.json` regenerates
byte-identical after the fix, and every field of `alignment_by_horizon.json` outside its Arm A block is unchanged.
S-20 and everything it rests on are unaffected, since they concern the released checkpoint only.

**Who found it:** round 3's preflight (R0, P2). It found Arm A's h = 1 error in `alignment_by_horizon.json` far above
the sweep evaluator's for the same checkpoints and trajectories. The user ruled "Fix, re-measure, then X2"
on 2026-10-09 (`docs/presubmission/round3/DECISIONS.md`).
**Evidence** `RUN` `results/alignment_by_horizon.json` (`scripts/alignment_by_horizon.py`, `scripts/alignment_defect_ci.py`).
**Status** RETRACTED · **Relevance** METHOD
"""

r_entry = f"""
### {RID} — Our own checkpoints do feel the stale pairing, from h = 100 on, where the released checkpoint's cost is concentrated at short horizons (post hoc; corrects R-76) · **NEW**
**Post hoc** (round 3, R0; a correction of round 2's N1). Not pre-registered; it re-opens no rule and changes no verdict.
It replaces R-76's Arm A half, which `{SID}` withdraws; R-76's released-checkpoint half stands.

**What was measured.** R-76's comparison on our Arm A, now measured correctly. It is the overstatement
err(offset 0) / err(offset 1) − 1, where offset 0 is the stale pairing and offset 1 the causal one. The trajectories
are the held-out pair's 4 non-overlapping 400-step trajectories, and the horizons are cumulative over steps 1..h.
The statistic, rollout and exact 256-resample cluster bootstrap are `scripts/alignment_defect_ci.py`'s, imported.
`rollout()` now takes a returned tensor whole and asserts its shape. `scripts/alignment_by_horizon.py` now asserts,
before writing any Arm A figure, that Arm A under the causal pairing reproduces `results/mn_compute_matched.json`'s
3-seed mean relative-L1 at every horizon (max difference {chk['2500']['max_abs_diff']:.1e} at 2,500 iterations and
{chk['10000']['max_abs_diff']:.1e} at 10,000). Seeds 0-2; at 2,500 the checkpoints are
`runs/armA_seed{{s}}/weights_2500.pt`, at 10,000 `runs/armA_seed{{s}}_10k/weights_10000.pt`.

**Arm A, held-out pair:** 3-seed mean (relative-L1 / nRMSE form 1), then each seed's relative-L1 with its exact interval:

| h | 2,500: 3-seed mean | 2,500: seeds 0, 1, 2 | 10,000: 3-seed mean | 10,000: seeds 0, 1, 2 |
|---|---|---|---|---|
{table}

**Reading.**
- Every seed's relative-L1 interval excludes zero from h = {first_all['10000']} at 10,000 iterations and from
  h = {first_all['2500']} at 2,500, and is positive there.
- At h = 1 and 8 no seed's interval lies above zero.
- At 10,000 iterations the 3-seed mean rises from {pct(mean('10000', '1', 'rel_l1'))} at h = 1 to
  {pct(mean('10000', '368', 'rel_l1'))} at h = 368, its largest, and is {pct(mean('10000', '100', 'rel_l1'))} at h = 100.
- At 2,500 it is {pct(mean('2500', '1', 'rel_l1'))} at h = 1 and {pct(mean('2500', '368', 'rel_l1'))} at h = 368.
- The shape is the reverse of the released checkpoint's on the same trajectories (R-76): its cost is largest at
  h = {hmax_rel} ({pct(rs[hmax_rel]['rel_l1']['pct'])}) and smallest at h = 368
  ({pct(rs['368']['rel_l1']['pct'])}).
- These are 4 independent trajectories, and the 3-seed mean carries no interval of its own here.

**What it changes.**
- §7.2 and the model card print this artifact's 10,000-iteration figures at h = 1 and h = 368 through keys
  `stale_armA_rel_h1` and `stale_armA_rel_h368`, so they now print the measured values.
- R-76's inference about the model card's earlier sentence goes with `{SID}`.
- Round 3's rule X2 was planned on the premise that our models barely notice the shift. It keeps its design
  (ruling V1), and its motivation cites this entry instead.
**Evidence** `RUN` `results/alignment_by_horizon.json`; `SRC` `scripts/alignment_by_horizon.py`, `scripts/alignment_defect_ci.py`.
**Status** CONFIRMED · **Relevance** CONTRIB
"""

# R-76's Status line: the sanctioned in-place edit (ruling A)
start = led.index("### R-76 — ")
end = led.index("\n### ", start + 5)
blk = led[start:end]
old_st = "**Status** CONFIRMED · **Relevance** CONTRIB"
assert blk.count(old_st) == 1, blk.count(old_st)
new_st = (f"**Status** SUPERSEDED IN PART by {SID} and {RID} — the released checkpoint's half stands as measured; "
          "the Arm A half was computed through a rollout that scored one trajectory's forecast against four "
          "trajectories' truths, and is withdrawn and re-measured · **Relevance** CONTRIB")
new_led = led[:start] + blk.replace(old_st, new_st) + led[end:]
assert new_led.count(new_st) == 1
new_led = new_led.rstrip("\n") + "\n" + s_entry + r_entry

R = open(RES, encoding="utf-8").read()
for pre, desc, old_n in (("R", "measured results", nr - 1), ("S", "superseded, retained", ns - 1)):
    row = f"| `{pre}-` {desc} | {old_n} |"
    assert R.count(row) == 1, row
    R = R.replace(row, f"| `{pre}-` {desc} | {old_n + 1} |")

shutil.copy(L, "/Users/Shared/rwm_verify/evidence/R3R0/FINDINGS_LEDGER.md.bak")
shutil.copy(RES, "/Users/Shared/rwm_verify/evidence/R3R0/RESULTS.md.bak")
open(L, "w", encoding="utf-8").write(new_led)
open(RES, "w", encoding="utf-8").write(R)
print(f"appended {SID} and {RID}; R-76 Status -> SUPERSEDED IN PART; RESULTS.md R- {nr - 1}->{nr}, S- {ns - 1}->{ns}")
print(f"criterion: {n_out}/{len(cells)} means outside +-1.00%, largest {worst}")
