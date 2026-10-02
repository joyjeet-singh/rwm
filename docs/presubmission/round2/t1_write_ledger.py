"""T1: append the three post hoc ledger entries for N1, N2 and N3 (round2/PLAN.md T1), and keep
RESULTS.md's per-prefix count row in step (ledger_check.py's fourth invariant).

Every figure is read from the artifacts; nothing is typed. IDs are the next free R- numbers in
FINDINGS_LEDGER.md. Refuses to run twice (asserts no entry already cites these artifacts).
Run from the repository root.
"""
import json
import re

L = "FINDINGS_LEDGER.md"
led = open(L, encoding="utf-8").read()
for art in ("alignment_by_horizon.json", "pooled_nrmse_rescore.json", "mn_compute_matched.json"):
    assert f"results/{art}" not in led, f"an entry already cites results/{art}"
nxt = max(int(n) for n in re.findall(r"^### R-(\d+) ", led, re.M)) + 1
ids = [f"R-{nxt + i:02d}" for i in range(3)]
J = lambda p: json.load(open(p))
n1, n2, n2a = J("results/alignment_by_horizon.json"), J("results/pooled_nrmse_rescore.json"), J("results/pooled_nrmse_alongside.json")
n3, n4 = J("results/mn_compute_matched.json"), J("results/training_tail_slopes.json")
pct = lambda v: f"{v:+.2f}%"
ci = lambda c: f"[{c[0]:+.2f}, {c[1]:+.2f}]"
HS = [str(h) for h in n1["horizons"]]

# ---------------------------------------------------------------- N1
rs = n1["released"]["summary"]
def resolved(arena, stat):
    return [h for h in HS if rs[arena][h][stat]["ci95_pct"][0] > 0 or rs[arena][h][stat]["ci95_pct"][1] < 0]
rows = [f"| {h} | {pct(rs['held_out_n4'][h]['rel_l1']['pct'])} {ci(rs['held_out_n4'][h]['rel_l1']['ci95_pct'])} | "
        f"{pct(rs['held_out_n4'][h]['nrmse_form1']['pct'])} {ci(rs['held_out_n4'][h]['nrmse_form1']['ci95_pct'])} | "
        f"{pct(rs['all_ten_n20'][h]['rel_l1']['pct'])} {ci(rs['all_ten_n20'][h]['rel_l1']['ci95_pct'])} | "
        f"{pct(rs['all_ten_n20'][h]['nrmse_form1']['pct'])} {ci(rs['all_ten_n20'][h]['nrmse_form1']['ci95_pct'])} |" for h in HS]
am = n1["arm_a"]
arow = [f"| {h} | {pct(am['2500']['summary_three_seed_mean_pct'][h]['rel_l1'])} "
        f"({', '.join(pct(am['2500']['summary_per_seed'][s][h]['rel_l1']['pct']) for s in ('0', '1', '2'))}) | "
        f"{pct(am['10000']['summary_three_seed_mean_pct'][h]['rel_l1'])} "
        f"({', '.join(pct(am['10000']['summary_per_seed'][s][h]['rel_l1']['pct']) for s in ('0', '1', '2'))}) |" for h in HS]
max_arm = max(abs(am[it]["summary_three_seed_mean_pct"][h][k]) for it in am for h in HS for k in ("rel_l1", "nrmse_form1"))
h1 = rs["held_out_n4"]["1"]["rel_l1"]
ho_res, ten_res = resolved("held_out_n4", "rel_l1"), resolved("all_ten_n20", "rel_l1")
ten_neg = [h for h in HS if rs["all_ten_n20"][h]["rel_l1"]["pct"] < 0]
hmax = max(HS, key=lambda h: rs["held_out_n4"][h]["rel_l1"]["pct"])
hmin = min(HS, key=lambda h: rs["held_out_n4"][h]["rel_l1"]["pct"])
e1 = f"""
### {ids[0]} — The alignment defect's cost depends on the horizon, and our own checkpoints barely feel it (post hoc) · **NEW**
**Post hoc** (round 2, analysis N1). Not pre-registered; it re-opens no rule and changes no verdict.

**What was measured.** The overstatement err(offset 0) / err(offset 1) − 1 — the released evaluation's
pairing (each prediction with the previous row's action) over training's causal pairing — at every
horizon section 3.1 uses, cumulative over steps 1..h, on the released checkpoint and on our Arm A.
The statistic, the rollout and the bootstrap are `scripts/alignment_defect_ci.py`'s, imported and
run with its horizon set to each h: 95% cluster bootstrap over whole trajectories with both pairings
inside each draw, exact over all 256 resamples on the held-out pair (n_independent = 4), 20,000 Monte
Carlo resamples (seed 0) over all ten episodes (n_independent = 20). At h = 368 the script reproduces
`results/alignment_defect_ci.json` to 1e-9 in both arenas.

**The released checkpoint.** Relative-L1 and nRMSE form 1, overstatement with its interval:

| h | held-out pair, rel-L1 | held-out pair, nRMSE | all ten episodes, rel-L1 | all ten episodes, nRMSE |
|---|---|---|---|---|
""" + "\n".join(rows) + f"""

On the held-out pair the relative-L1 interval excludes zero at h = {', '.join(ho_res) or 'none'}; at h = 1 the stale
action raises the error by {pct(h1['pct'])} {ci(h1['ci95_pct'])}. Over all ten episodes (in-sample for this checkpoint) the
relative-L1 interval excludes zero at h = {', '.join(ten_res) or 'none'}, and the point estimate is negative at
h = {', '.join(ten_neg) or 'none'}. On the held-out pair the relative-L1 overstatement is largest at h = {hmax}
({pct(rs['held_out_n4'][hmax]['rel_l1']['pct'])}) and smallest at h = {hmin} ({pct(rs['held_out_n4'][hmin]['rel_l1']['pct'])}): the cost is concentrated at short horizons,
and at h = 368 it is the small, sign-unstable figure section 7.2 already reports.

**Our Arm A**, trained under the causal pairing, on the held-out pair: relative-L1 overstatement,
3-seed mean (seeds 0, 1, 2):

| h | 2,500 iterations | 10,000 iterations |
|---|---|---|
""" + "\n".join(arow) + f"""

Every 3-seed mean, in both metrics and at both checkpoints, is within {max_arm:.2f}% of zero: our checkpoints are
almost insensitive to the stale pairing, so the model card's untested sentence that a consumer feeding
actions the other way "will get materially worse numbers" is not borne out for these checkpoints.
**Evidence** `RUN` `results/alignment_by_horizon.json`; `SRC` `scripts/alignment_by_horizon.py`, `scripts/alignment_defect_ci.py`.
**Status** CONFIRMED · **Relevance** CONTRIB
"""

# ---------------------------------------------------------------- N2
tsm = n2["three_seed_mean"]
c = tsm["M32_N8"]["held_out"]
changed = n2a["readings_whose_result_changed"]
def ch(key):
    rid, rk = key.split(" ", 1)
    r = n2a["readings"][rid][rk]
    return f"{rid}, {rk.replace('|', ', ').replace('nrmse_h', 'nRMSE at h = ')}: {r['committed']['result']} → {r['pooled']['result']}"
held_changed = [k for k in changed if "held_out" in k]
fl = n2["diverged_flag"]
e2 = f"""
### {ids[1]} — The sweep and baseline evaluators averaged nRMSE per trajectory where section 3.1 pools it; pooled, {'no held-out alongside reading changes' if not held_changed else str(len(held_changed)) + ' held-out alongside readings change'} (post hoc) · **NEW**
**Post hoc** (round 2, analysis N2). Not pre-registered; no discharged rule is re-opened and no committed
evaluation or verdict artifact is edited.

**The deviation.** Section 3.1's nRMSE form 1 (`rwm_metrics.nrmse_pooled`) pools squared error across
trajectories before the root, as `scripts/head_to_head_accuracy.py` does. `scripts/mn_sweep_eval.py`
and `scripts/baselines_eval.py` applied form 1 to each trajectory alone and their consumers averaged
those values. For RWM (Arm A, 2,500 iterations) at h = 368 on the held-out pair the two give
{c['pooled_nrmse']['368']:.4f} pooled and {c['mean_per_traj_nrmse']['368']:.4f} averaged.

**Re-run** with the evaluators' own `score()`: the sweep's centre and eight configurations and the six
Table S7 baseline families, seeds 0-2, both arenas, all six horizons. Asserted first, all passing:
the centre's pooled values equal the head-to-head table's (max difference
{n2['asserts']['a_centre_matches_head_to_head_pooled']['max_abs_diff']:.1e}); every per-trajectory relative-L1 and nRMSE equals the committed evaluators'
(max {n2['asserts']['b_per_trajectory_l1_and_nrmse_match_committed_evaluators']['max_abs_diff']:.1e}); and the reading machinery, run with the rules' own
per-trajectory statistic, reproduces all {n2a['assert_d_machinery_reproduces_committed_readings']['readings_compared']} committed alongside nRMSE readings of M-74, M-75 and M-76 exactly.

**The pooled readings.** The verdict scripts' reading function takes per-trajectory differences, which
pooled nRMSE does not have, so each alongside nRMSE reading was recomputed with the rule's design and
only the statistic changed: 3-seed mean pooled nRMSE minus the reference's, recomputed on each of the
rule's own resamples, with the rules' p, interval, Holm and branch functions. **The governing verdicts
use relative-L1 at h = 368 and are unaffected.** Readings whose result changes under pooling:
{'; '.join(ch(k) for k in changed) or 'none'}. Reported, never substituted into a discharged rule
(`results/pooled_nrmse_alongside.json` holds every reading side by side).

**The diverged flag**, defined here before any table renders it: {fl['definition']}. Flagged:
{', '.join(f"`{k}` ({', '.join(f'{v:.1f}' for v in fl['rows'][k]['per_seed_mean_l1_h368'].values())} against a threshold of {fl['rows'][k]['threshold']:.2f})" for k in fl['flagged'])}.
**Evidence** `RUN` `results/pooled_nrmse_rescore.json`, `results/pooled_nrmse_alongside.json`; `SRC` `scripts/pooled_nrmse_rescore.py`.
**Status** CONFIRMED · **Relevance** CONTRIB
"""

# ---------------------------------------------------------------- N3
p1 = n3["part1_relative_cost_per_iteration"]
rd = n3["part3_readings"]["readings"]
var = n3["annex3_variant"]
best = var["best_neighbour_at_h368"]
rrows = []
for key in sorted(rd, key=lambda k: (k.split("|")[0], int(k.split("@")[1]))):
    r = rd[key]
    a3, a1 = r["h368"]["held_out"], r["h100"]["held_out"]
    rrows.append(f"| {r['config']} @ 2,500 vs centre @ {r['centre_iterations']:,} | {r['compute_ratios']['config_total_compute_over_centre_at_k']:.2f}x | "
                 f"{a1['D']:+.4f} [{a1['ci95'][0]:+.4f}, {a1['ci95'][1]:+.4f}] | {a3['D']:+.4f} [{a3['ci95'][0]:+.4f}, {a3['ci95'][1]:+.4f}] |")
cr = n3["part2_centre_at_more_compute"]["three_seed_mean_l1"]
def verdict10(r):
    lo, hi = r["h368"]["held_out"]["ci95"]
    return "the configuration ahead" if hi < 0 else ("the centre ahead" if lo > 0 else "not resolved")
cfg_lab = lambda k: k[1:].replace("_N", ", ").join(["(", ")"])
at10k = "; ".join(f"{cfg_lab(r['config'])} {verdict10(r)}" for k, r in sorted(rd.items()) if r["centre_iterations"] == 10000)
s25 = n4["summary"]["at_2500_all"]
s10 = n4["summary"]["arm_10000"]
title3 = (f"{best[1:].replace('_N', ', ').join(['(', ')'])}'s advantage over the centre survives giving the centre twice the training compute"
          if var["variant"] == "a" else "At matched training compute the sweep's winners' advantage over the centre is not resolved")
e3 = f"""
### {ids[2]} — {title3}, and every run is still learning at 2,500 iterations (post hoc) · **NEW**
**Post hoc** (round 2, analysis N3). Not pre-registered: section 5 had already printed the centre at
10,000 iterations on the same four held-out trajectories (round 2 PREFLIGHT.md, P2). M-74's verdict
(M-77) is not re-opened; no Holm step is applied and no verdict is returned.

**Cost per iteration, relative to the centre (32, 8).** The sweep's from `results/mn_sweep_timing.json`,
whose probes ran uncontended (PREFLIGHT.md, P3): {', '.join(f"{k} {v['relative_to_centre']:.2f}x" for k, v in sorted(p1['sweep'].items()) if k != 'M32_N8')}.
The six baseline families were re-probed for {p1['baselines_probe']['probe_iterations']} iterations beside a same-sitting centre probe
({p1['baselines_probe']['centre_steady_s_per_iter']:.3f} s per iteration, against round 1's {p1['sweep']['M32_N8']['steady_s_per_iter']:.3f}):
{', '.join(f"{k} {v['relative_to_same_sitting_centre']:.2f}x" for k, v in p1['baselines'].items())}.

**The centre at more compute.** Arm A's 10k runs scored with the sweep's evaluator; the 2,500
checkpoint reproduces the sweep's centre row (max difference {n3['part2_centre_at_more_compute']['reproduces_sweep_centre_at_2500']['max_abs_diff']:.1e}). Held-out relative-L1,
3-seed mean, at h = 368: {', '.join(f"{int(it):,} iterations {v['held_out']['368']:.4f}" for it, v in cr.items())}.

**The reading**, M-74's statistic and interval (exact, 256 resamples, n_independent = 4), relative-L1,
negative favouring the configuration; compute is the configuration's total training compute over the
centre's at k:

| comparison | compute | h = 100 | h = 368 |
|---|---|---|---|
""" + "\n".join(rrows) + f"""

The best neighbour at h = 368 under M-74 is {best}; against the centre at 5,000 iterations its h = 368
difference is {var['neighbour_minus_centre_at_5000_h368_held_out']['D']:+.4f} {ci(var['neighbour_minus_centre_at_5000_h368_held_out']['ci95'])}, so Annex 3's variant ({var['variant']}) applies.
Against the centre at 10,000 iterations, at h = 368: {at10k}.

**Non-convergence.** The state-loss slope over the final 250 iterations is negative for all
{s25['n']} runs at 2,500 iterations (sweep, Table S7 baselines, Arm A and Arm B), from {s25['min']:.2e} to
{s25['max']:.2e} per iteration; at 10,000 iterations {s10['n_falling']} of {s10['n']} Arm A and Arm B runs are still falling.
The sweep's ranking is a ranking at this budget, not at convergence.
**Evidence** `RUN` `results/mn_compute_matched.json`, `results/training_tail_slopes.json`; `SRC` `scripts/mn_compute_matched.py`, `scripts/training_tail_slopes.py`.
**Status** CONFIRMED · **Relevance** CONTRIB
"""

new = led.rstrip("\n") + "\n" + e1 + e2 + e3
open(L, "w", encoding="utf-8").write(new)
R = open("RESULTS.md", encoding="utf-8").read()
m = re.search(r"^(\|\s*`R-`[^|]*\|\s*)(\d+)(\s*\|)", R, re.M)
assert m and int(m.group(2)) == nxt - 1, (m and m.group(2), nxt - 1)
R = R[:m.start()] + m.group(1) + str(nxt + 2) + m.group(3) + R[m.end():]
open("RESULTS.md", "w", encoding="utf-8").write(R)
print("appended", ids, "| RESULTS.md R- row", nxt - 1, "->", nxt + 2)
