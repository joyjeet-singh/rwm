"""
Round 2, N1 (post hoc) -- what the one-step alignment defect costs at each horizon, and how
sensitive our own checkpoints are to the stale pairing.

PLAN round2 Annex 1, N1. Nothing here is pre-registered, and nothing here re-opens a rule.

THE STATISTIC is alignment_defect_ci.py's, imported, not copied: the overstatement
err(offset 0) / err(offset 1) - 1, where offset 0 is the released evaluation's pairing (each
prediction with the previous row's action) and offset 1 is training's (causal). Relative-L1
and nRMSE form 1 are cumulative over steps 1..h, as section 3.1 defines them. That module
fixes its horizon in the module constant H (368); this script sets H to each horizon in turn
and calls the module's own arena() -- rollout, pooled statistics, per-trajectory values and
the same 95% cluster bootstrap over whole trajectories with both pairings inside each draw:
exact over all 256 resamples at n = 4, 20,000 Monte Carlo resamples (generator seed 0) at
n = 20. No bootstrap is written here.

TWO PARTS:
  released   the released checkpoint (score_reference.ReferenceRWM), horizons
             {1, 8, 32, 100, 128, 368}, arenas held_out_n4 (section 5's four held-out
             trajectories) and all_ten_n20 (all ten episodes; in-sample for the checkpoint).
             ASSERTED: at h = 368 every value equals results/alignment_defect_ci.json to 1e-9.
  arm_a      our Arm A, trained under the causal pairing (offset 1), seeds 0-2, at 2,500
             iterations (runs/armA_seed{s}/weights_2500.pt, the runs section 5 and the sweep's
             centre use) and at 10,000 (runs/armA_seed{s}_10k/weights_10000.pt): the same ratio
             on the held-out arena at the same six horizons, per seed with the exact n = 4
             interval, and the 3-seed mean of the per-seed overstatement.
             ASSERTED (round 3, ledger R-79): the 3-seed mean relative-L1 under the causal
             pairing equals results/mn_compute_matched.json's three_seed_mean_l1 on the same
             held-out arena, at every horizon and both checkpoints, to 1e-6. Round 2 had no such
             check, and alignment_defect_ci.rollout then took only the first trajectory of our
             models' rollout, so the Arm A figures it wrote were void.

Per-trajectory values are stored for every arena, model and horizon.

Writes results/alignment_by_horizon.json.
"""
import itertools
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, os.pardir, "src"))
import numpy as np  # noqa: E402
import torch  # noqa: E402

import alignment_defect_ci as ADC  # noqa: E402
import rollout_eval as E  # noqa: E402
import rwm_data as R  # noqa: E402
import rwm_metrics as MET  # noqa: E402
import rwm_model as M  # noqa: E402
import score_reference as S  # noqa: E402

HORIZONS = (1, 8, 32, 100, 128, 368)
SEEDS = (0, 1, 2)
ARM_A = {"2500": "runs/armA_seed{s}/weights_2500.pt", "10000": "runs/armA_seed{s}_10k/weights_10000.pt"}
STATS = ("rel_l1", "nrmse_form1")      # the two the paper uses; nrmse_curve is kept as computed
TOL = 1e-9


def at_horizon(h, *args):
    """alignment_defect_ci.arena() with its horizon set to h."""
    ADC.H = h
    try:
        return ADC.arena(*args)
    finally:
        ADC.H = 368


def close(a, b, tol=TOL):
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(close(a[k], b[k], tol) for k in a)
    if isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(close(x, y, tol) for x, y in zip(a, b))
    if isinstance(a, (int, float)):
        return abs(float(a) - float(b)) <= tol
    return a == b


def main():
    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    data, ep = R.load_data(paths["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"), verbose=False)
    scale = MET.training_scale(data, ep, split["train_episodes"], cfg["state_data_mean"], cfg["state_data_std"])

    s4 = MET.non_overlapping_starts(ep, split["holdout_episodes"], E.LEN_TRAJ)
    s20 = MET.non_overlapping_starts(ep, list(range(10)), E.LEN_TRAJ)
    assert MET.n_independent(s4, E.LEN_TRAJ) == 4 and MET.n_independent(s20, E.LEN_TRAJ) == 20
    mk = lambda st: np.asarray(st)[:, None] + np.arange(E.LEN_TRAJ)[None, :]
    exact4 = np.array(list(itertools.product(range(4), repeat=4)))
    mc20 = np.random.default_rng(ADC.MC_SEED).integers(0, 20, size=(ADC.MC_N, 20))

    # ---- part 1: the released checkpoint ------------------------------------------------
    ref = S.ReferenceRWM(torch.load(paths["ckpt"], map_location="cpu")["system_dynamics_state_dict"])
    ref.eval()
    released = {"held_out_n4": {}, "all_ten_n20": {}}
    for h in HORIZONS:
        released["held_out_n4"][str(h)] = at_horizon(h, ref, data, cfg, scale, mk(s4), exact4)
        released["all_ten_n20"][str(h)] = at_horizon(h, ref, data, cfg, scale, mk(s20), mc20)

    committed = json.load(open(os.path.join(R.RESULTS, "alignment_defect_ci.json")))["arenas"]
    repro = {}
    for a in ("held_out_n4", "all_ten_n20"):
        mine, theirs = released[a]["368"], committed[a]
        keys = ("starts", "n_trajectories", "pooled", "overstatement_pct", "per_trajectory",
                "per_trajectory_overstatement_pct", "ci95_pct", "n_resamples")
        bad = [k for k in keys if not close(mine[k], theirs[k])]
        assert not bad, f"{a} at h = 368 does not reproduce alignment_defect_ci.json in {bad}"
        repro[a] = {"fields_compared": list(keys), "tolerance": TOL, "reproduced": True}

    # ---- part 2: our Arm A, trained under the causal pairing --------------------------------
    arm_a = {}
    for it, pattern in ARM_A.items():
        per_seed = {}
        for s in SEEDS:
            w = pattern.format(s=s)
            assert os.path.exists(w), f"missing {w}"
            model = M.build_from_config(cfg, ensemble_size=1)
            model.load_state_dict(torch.load(w, map_location="cpu")["model_state_dict"], strict=True)
            model.eval()
            per_seed[str(s)] = {"weights": w,
                                **{str(h): at_horizon(h, model, data, cfg, scale, mk(s4), exact4)
                                   for h in HORIZONS}}
        mean = {str(h): {k: float(np.mean([per_seed[str(s)][str(h)]["overstatement_pct"][k]
                                           for s in SEEDS])) for k in STATS}
                for h in HORIZONS}
        arm_a[it] = {"per_seed": per_seed, "three_seed_mean_overstatement_pct": mean}

    # Round 3 (ledger R-79): Arm A under the causal pairing must score what the sweep evaluator
    # scored on the same trajectories (mn_sweep_eval.score, results/mn_compute_matched.json), or
    # no Arm A figure is written. Its 2,500 entry uses the 10k runs' 2,500-iteration checkpoints,
    # byte-identical to the runs ARM_A names (round 3 PREFLIGHT P1).
    mcm = json.load(open(os.path.join(R.RESULTS, "mn_compute_matched.json")))
    mcm = mcm["part2_centre_at_more_compute"]["three_seed_mean_l1"]
    arm_a_check = {}
    for it in arm_a:
        worst = max(abs(float(np.mean([arm_a[it]["per_seed"][str(s)][str(h)]["pooled"]["offset1"]["rel_l1"]
                                       for s in SEEDS])) - mcm[it]["held_out"][str(h)])
                    for h in HORIZONS)
        assert worst <= 1e-6, (f"Arm A at {it} under the causal pairing does not reproduce "
                               f"mn_compute_matched.json (max |difference| {worst:.3e})")
        arm_a_check[it] = {"max_abs_diff": worst, "tolerance": 1e-6, "reproduced": True}

    def summary(rec):
        return {k: {"pct": rec["overstatement_pct"][k],
                    "ci95_pct": rec.get("ci95_pct", {}).get(k)} for k in STATS}

    out = {"purpose": "round 2 N1 (post hoc): the alignment defect's cost at each horizon on the released "
                      "checkpoint, and our Arm A's sensitivity to the stale pairing",
           "post_hoc": True,
           "statistic": "err(offset 0) / err(offset 1) - 1, in percent; alignment_defect_ci.py's arena(), "
                        "imported, with its horizon set to each h; cumulative over steps 1..h",
           "offsets": {"0": "the released evaluation's pairing (stale action)", "1": "training's pairing (causal)"},
           "horizons": list(HORIZONS),
           "bootstrap": {"held_out_n4": "exact, all 256 ordered resamples of whole trajectories, both pairings inside each draw",
                         "all_ten_n20": f"Monte Carlo, {ADC.MC_N} resamples, generator seed {ADC.MC_SEED}"},
           "arenas": {"held_out_n4": {"starts": [int(x) for x in s4], "n_independent": 4,
                                      "note": "section 5's held-out pair; out-of-sample for our runs, in-sample for the released checkpoint"},
                      "all_ten_n20": {"starts": [int(x) for x in s20], "n_independent": 20,
                                      "note": "all ten episodes; in-sample for the released checkpoint"}},
           "released": {"summary": {a: {h: summary(released[a][h]) for h in released[a]} for a in released},
                        "full": released,
                        "reproduces_alignment_defect_ci_at_h368": repro},
           "arm_a_offset1_reproduces_mn_compute_matched": arm_a_check,
           "arm_a": {it: {"summary_three_seed_mean_pct": v["three_seed_mean_overstatement_pct"],
                          "summary_per_seed": {s: {h: summary(v["per_seed"][s][h]) for h in map(str, HORIZONS)}
                                               for s in v["per_seed"]},
                          "full": v["per_seed"]}
                     for it, v in arm_a.items()},
           "weights": {"arm_a_2500": ARM_A["2500"], "arm_a_10000": ARM_A["10000"],
                       "released": "setup.sh's pretrain_rnn_ens.pt"}}
    op = os.path.join(R.RESULTS, "alignment_by_horizon.json")
    json.dump(out, open(op, "w"), indent=2)

    print("=" * 100)
    print("N1 (post hoc) — the alignment defect by horizon: err(offset 0) / err(offset 1) - 1, percent")
    print("=" * 100)
    print(f"  reproduces alignment_defect_ci.json at h = 368 (tolerance {TOL}): {repro}")
    for a in ("held_out_n4", "all_ten_n20"):
        print(f"  released checkpoint, {a}:")
        for h in map(str, HORIZONS):
            r = released[a][h]
            print("    h={:>3}  rel-L1 {:+7.2f}% [{:+7.2f}, {:+7.2f}]   nRMSE form 1 {:+7.2f}% [{:+7.2f}, {:+7.2f}]".format(
                h, r["overstatement_pct"]["rel_l1"], *r["ci95_pct"]["rel_l1"],
                r["overstatement_pct"]["nrmse_form1"], *r["ci95_pct"]["nrmse_form1"]))
    for it, v in arm_a.items():
        print(f"  our Arm A at {it} iterations, held-out arena, 3-seed mean (per seed):")
        for h in map(str, HORIZONS):
            m = v["three_seed_mean_overstatement_pct"][h]
            ps = [v["per_seed"][str(s)][h]["overstatement_pct"]["rel_l1"] for s in SEEDS]
            print(f"    h={h:>3}  rel-L1 {m['rel_l1']:+7.2f}%  {np.round(ps, 2).tolist()}   nRMSE form 1 {m['nrmse_form1']:+7.2f}%")
    print(f"  wrote {R.rel(op)}")


if __name__ == "__main__":
    main()
