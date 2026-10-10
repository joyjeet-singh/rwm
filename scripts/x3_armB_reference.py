"""
Round 4, rule X3's reference for Arm B (ruling (B) of docs/presubmission/round4/DECISIONS.md#F0-armB-2500-h128).

X3's assertion reproduces "the committed 2,500-iteration held-out relative-L1 for Arm A
(mn_compute_matched.json's 2,500 block) and Arm B (PF1's artifact) at every horizon, to 1e-6".
No committed artifact held Arm B at h = 128 on section 5's four held-out trajectories
(round4/PREFLIGHT.md, PF1). This script makes that reference, before X3 is pre-registered,
from the stored rollouts behind results/head_to_head_accuracy.json -- the per-triple caches
cache/armB_teacher_forced_seed<s>__out-of-sample_held-out_pair__u400.npz, which
scripts/gate_per_triple.py verifies and whose SHA-256s that artifact records. Nothing is
rolled out and no checkpoint is loaded: it calls scripts/head_to_head_accuracy.py's own
compute() at six horizons instead of four.

ASSERTED BEFORE ANYTHING IS WRITTEN
  1. compute() at six horizons agrees with the committed results/head_to_head_accuracy.json on
     everything the two share: the arena, its trajectory starts, every input file's SHA-256,
     and every row's per-seed and three-seed cells at h = 1, 8, 100 and 368, to 1e-12.
  2. Arm B's per-seed relative-L1 at h = 32 equals results/action_sensitivity.json's unperturbed
     causal rollout (per_seed["arm_b_2500|seed<s>|held_out_n4|h32"].I0_per_trajectory_err, mean
     over the four trajectories) to 1e-6 -- a different code path (a rollout, not a cache).
Writes results/x3_armB_2500_reference.json: Arm B's row only, at h = 1, 8, 32, 100, 128, 368.
  python scripts/x3_armB_reference.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402

import head_to_head_accuracy as H2H  # noqa: E402
import rwm_data as R  # noqa: E402

SIX = (1, 8, 32, 100, 128, 368)
SEEDS = (0, 1, 2)
OUT = os.path.join(R.RESULTS, "x3_armB_2500_reference.json")
TOL_SAME, TOL_ROLLOUT = 1e-12, 1e-6


def gap(x, y):
    """|x - y|, with two Nones (a one-model row's spread) equal and one None against a number infinite."""
    if x is None or y is None:
        return 0.0 if x is None and y is None else float("inf")
    return abs(x - y)


def main():
    rec = H2H.compute(horizons=SIX)
    old = json.load(open(os.path.join(R.RESULTS, H2H.OUT)))
    shared = [str(h) for h in old["horizons"]]
    for k in ("arena", "arena_episodes", "traj_start_row", "n_independent", "unit_length", "start_step",
              "n_forecast_steps", "arm_checkpoint", "arm_seeds", "input_files"):
        assert rec[k] == old[k], f"(1) {k} differs from results/{H2H.OUT}"
    d1 = 0.0
    for row, r in old["rows"].items():
        for h in shared:
            for m, v in r["cells"][h].items():
                d1 = max(d1, gap(rec["rows"][row]["cells"][h][m], v))
            for mid, pm in r.get("per_model", {}).items():
                for m, v in pm[h].items():
                    d1 = max(d1, gap(rec["rows"][row]["per_model"][mid][h][m], v))
    assert d1 <= TOL_SAME, f"(1) compute() at six horizons differs from results/{H2H.OUT} by {d1}"
    AS = json.load(open(os.path.join(R.RESULTS, "action_sensitivity.json")))
    d2 = max(abs(rec["rows"]["armB"]["per_model"][f"armB_teacher_forced_seed{s}"]["32"]["l1"]
                 - float(np.mean(AS["per_seed"][f"arm_b_2500|seed{s}|held_out_n4|h32"]["I0_per_trajectory_err"])))
             for s in SEEDS)
    assert d2 <= TOL_ROLLOUT, f"(2) Arm B at h = 32 differs from results/action_sensitivity.json by {d2}"
    b = rec["rows"]["armB"]
    out = {"what": "rule X3's reference: Arm B (teacher-forced), 2,500 iterations, seeds 0-2, on section 5's four "
                   "held-out trajectories, relative-L1 and nRMSE, cumulative over forecast steps 1..h",
           "ruling": "docs/presubmission/round4/DECISIONS.md#F0-armB-2500-h128, option (B)",
           "producer": "scripts/x3_armB_reference.py, through scripts/head_to_head_accuracy.py's compute(horizons)",
           "computation": rec["computation"], "no_new_rollout": rec["no_new_rollout"],
           "arena": rec["arena"], "arena_episodes": rec["arena_episodes"], "traj_start_row": rec["traj_start_row"],
           "n_independent": rec["n_independent"], "unit_length": rec["unit_length"], "start_step": rec["start_step"],
           "arm_checkpoint": rec["arm_checkpoint"], "arm_seeds": rec["arm_seeds"], "horizons": list(SIX),
           "metrics": rec["metrics"], "seed_aggregation": rec["seed_aggregation"],
           "armB": {"label": b["label"], "n_models": b["n_models"], "per_model": b["per_model"], "cells": b["cells"]},
           "input_files": [f for f in rec["input_files"] if "armB_teacher_forced" in f["path"]],
           "checks": {"same_as_head_to_head_accuracy": {"horizons": [int(h) for h in shared], "max_abs_diff": d1,
                                                        "tolerance": TOL_SAME, "rows": sorted(old["rows"])},
                      "armB_h32_vs_action_sensitivity_I0": {"max_abs_diff": d2, "tolerance": TOL_ROLLOUT}}}
    json.dump(out, open(OUT, "w"), indent=2)
    print(f"  (1) same as results/{H2H.OUT} at h = {', '.join(shared)}: max |difference| {d1:.1e}")
    print(f"  (2) Arm B at h = 32 against results/action_sensitivity.json: max |difference| {d2:.1e}")
    print(f"  wrote {R.rel(OUT)}")


if __name__ == "__main__":
    main()
