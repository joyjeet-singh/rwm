"""
N5 (POST HOC, round 4, PLAN Annex 3) -- our models' figures under the stale action timing, with intervals, at every
horizon in both arenas, and the forecast shift they cause.

POST HOC: computed after the data existed, as the remedy for §7.2 putting a -0.99% (held-out, unresolved) beside a
+124.6% (training episodes) with no intervals. It re-opens no rule and changes no verdict.

MODELS AND ARENAS, exactly rule X2's (scripts/action_sensitivity.py's model_plan and setting, imported):
  Arm A and Arm B at 2,500 and 10,000 iterations, seeds 0-2, on their own training episodes' 16 independent 400-step
  trajectories (in_sample_n16) and the held-out pair's 4 (held_out_n4); the released checkpoint on its own training data,
  all ten episodes' 20 (all_ten_n20), and the held-out pair's 4.
HORIZONS. All six, {1, 8, 32, 100, 128, 368} (X2 read h <= 100 only), cumulative over forecast steps 1..h.
MEASURES, each by X2's machinery, imported (the rollout hook, traj_means, delta, draws_for, e_with_ci):
  E      the stale timing's change in relative-L1 error, err(offset 0) / err(offset 1) - 1, in percent; for our arms the
         mean over the three seeds of each seed's E; 95% interval over whole trajectories, the same resample for every
         seed and both timings inside each draw: exact over all 256 at n = 4, 20,000 Monte Carlo draws
         (alignment_defect_ci's recipe) at n = 16 and n = 20.
  Delta  the forecast shift: relative-L1 of the stale-timing forecast against the causal one over steps 1..h
         (rollout_eval.relative_error with the causal forecast as target), mean over seeds. 0 for a model that ignores
         the action.
  err    each model's relative-L1 error at the causal timing (and at the stale one), mean over seeds.

ASSERTIONS, before anything is written:
  (a) at h <= 100, E, its interval and Delta equal results/action_sensitivity.json's stale-action (I1_stale) cells for
      every model and arena, to 1e-9 (Annex 3 names E and Delta at h = 8; every shared cell is checked);
  (b) Arm A's three-seed E on the held-out pair equals results/alignment_by_horizon.json's corrected arm_a block (R-79)
      at every horizon and both checkpoints, to 1e-6; and the released checkpoint's E and interval equal its released
      block at every horizon in both arenas, to 1e-6.

  python scripts/n5_stale_armA_ci.py
Writes results/n5_stale_armA_ci.json.
"""
import hashlib
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402

import action_sensitivity as AS  # noqa: E402
import rwm_data as R  # noqa: E402

HS = (1, 8, 32, 100, 128, 368)
TOL_X2, TOL_N1 = 1e-9, 1e-6
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
OUT = os.path.join(R.RESULTS, "n5_stale_armA_ci.json")
MODULES = ("scripts/n5_stale_armA_ci.py", "scripts/action_sensitivity.py", "scripts/alignment_defect_ci.py",
           "scripts/mn_sweep_eval.py", "src/rollout_eval.py", "src/rwm_model.py", "src/score_reference.py")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    t0, c0 = time.time(), time.process_time()
    paths, cfg, data, ep, split, scale, arenas, mk, norm = AS.setting()
    per = {}
    for spec in AS.model_plan():
        hook = AS.Hook(AS.load(paths, cfg, spec["kind"], spec["it"], spec["seed"]))
        for ar in spec["arenas"]:
            idx = mk(arenas[ar])
            r0, r1 = hook.run(data, cfg, idx, 1), hook.run(data, cfg, idx, 0)
            per[(spec["key"], spec["seed"], ar)] = {"c0": {h: AS.traj_means(r0, h) for h in HS},
                                                    "c1": {h: AS.traj_means(r1, h) for h in HS},
                                                    "delta": {h: float(AS.delta(r1, r0, h)) for h in HS}}
    out = {}
    for key in dict.fromkeys(k for k, _, _ in per):
        out[key] = {}
        seeds = sorted({s for k, s, _ in per if k == key}, key=lambda s: -1 if s is None else s)
        for ar in dict.fromkeys(a for k, _, a in per if k == key):
            cells = [per[(key, s, ar)] for s in seeds]
            n = len(cells[0]["c0"][1])
            D = AS.draws_for(n)
            out[key][ar] = {"n_trajectories": n, "seeds": [s for s in seeds], "by_horizon": {}}
            for h in HS:
                point, ci, _ = AS.e_with_ci([c["c1"][h] for c in cells], [c["c0"][h] for c in cells], D)
                out[key][ar]["by_horizon"][str(h)] = {
                    "E_pct": point, "ci95_pct": ci, "interval_excludes_zero": bool(ci[0] > 0 or ci[1] < 0),
                    "delta": float(np.mean([c["delta"][h] for c in cells])),
                    "err_causal": float(np.mean([c["c0"][h].mean() for c in cells])),
                    "err_stale": float(np.mean([c["c1"][h].mean() for c in cells])),
                    "per_seed_E_pct": [float(100 * (c["c1"][h].mean() / c["c0"][h].mean() - 1)) for c in cells]}

    # (a) X2's committed cells, h <= 100, every model and arena
    X2 = json.load(open(os.path.join(R.RESULTS, "action_sensitivity.json")))["results"]
    da, na = 0.0, 0
    for key, by_ar in X2.items():
        for ar, by_h in by_ar.items():
            for h, cell in by_h.items():
                mine, ref = out[key][ar]["by_horizon"][h], cell["I1_stale"]
                da = max([da, abs(mine["E_pct"] - ref["E_pct"]), abs(mine["delta"] - ref["delta"])]
                         + [abs(x - y) for x, y in zip(mine["ci95_pct"], ref["ci95_pct"])])
                na += 1
    # (b) round 2's N1 as corrected (R-79), and the released checkpoint's block
    N1 = json.load(open(os.path.join(R.RESULTS, "alignment_by_horizon.json")))
    db = 0.0
    for it in ("2500", "10000"):
        for h in HS:
            db = max(db, abs(out[f"arm_a_{it}"]["held_out_n4"]["by_horizon"][str(h)]["E_pct"]
                             - N1["arm_a"][it]["summary_three_seed_mean_pct"][str(h)]["rel_l1"]))
    for ar in ("all_ten_n20", "held_out_n4"):
        for h in HS:
            ref = N1["released"]["summary"][ar][str(h)]["rel_l1"]
            mine = out["released"][ar]["by_horizon"][str(h)]
            db = max([db, abs(mine["E_pct"] - ref["pct"])] + [abs(x - y) for x, y in zip(mine["ci95_pct"], ref["ci95_pct"])])
    asserts = {"a": {"pass": bool(da <= TOL_X2 and na > 0), "max_abs_diff": da, "n_cells": na,
                     "against": "results/action_sensitivity.json results[*][*][h <= 100].I1_stale"},
               "b": {"pass": bool(db <= TOL_N1), "max_abs_diff": db,
                     "against": "results/alignment_by_horizon.json arm_a summary_three_seed_mean_pct (held-out) and released summary"}}
    for k, v in asserts.items():
        print(f"  assertion ({k}): {'PASS' if v['pass'] else 'FAIL'}  max |difference| {v['max_abs_diff']:.1e}")
    if not all(v["pass"] for v in asserts.values()):
        raise SystemExit("N5: an assertion failed; nothing written")
    rec = {"analysis": "N5", "post_hoc": True,
           "what": "our models' (and the released checkpoint's) error change under the stale action timing (offset 0 against "
                   "the causal offset 1), with intervals, at every horizon in both arenas, and the forecast shift Delta",
           "never_reopens": "any rule; changes no verdict",
           "machinery": "scripts/action_sensitivity.py (rule X2's), imported: setting, model_plan, load, Hook, traj_means, "
                        "delta, draws_for, e_with_ci",
           "horizons": list(HS),
           "arenas": {"in_sample_n16": "our arms' own training episodes, 16 independent 400-step trajectories",
                      "held_out_n4": "the held-out pair, 4", "all_ten_n20": "all ten episodes, 20: the released checkpoint's own training data"},
           "interval": "95%, whole trajectories, the same resample for every seed and both timings: exact (256) at n = 4, "
                       "20,000 Monte Carlo draws at n = 16 and 20",
           "assertions": asserts, "results": out,
           "cpu_s": time.process_time() - c0, "wall_s": time.time() - t0,
           "code_sha256": {p: sha256(os.path.join(ROOT, p)) for p in MODULES},
           "git_head": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()}
    json.dump(rec, open(OUT, "w"), indent=2)
    a = out["arm_a_10000"]
    for ar in ("in_sample_n16", "held_out_n4"):
        print(f"  Arm A 10,000, {ar}: " + "; ".join(
            f"h={h} {a[ar]['by_horizon'][str(h)]['E_pct']:+.1f}% [{a[ar]['by_horizon'][str(h)]['ci95_pct'][0]:+.1f}, "
            f"{a[ar]['by_horizon'][str(h)]['ci95_pct'][1]:+.1f}]" for h in HS))
    print(f"  wrote {R.rel(OUT)}")


if __name__ == "__main__":
    main()
