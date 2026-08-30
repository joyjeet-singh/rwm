"""2.2 -- M-63: is the h=1 coverage failure uniform across the 45 state dimensions?

Coverage at +-1 sigma is an indicator pooled with equal weight over every
(trajectory, step, dimension) triple, and every dimension contributes the same number of
triples. So POOLED COVERAGE IS EXACTLY THE UNWEIGHTED MEAN of the 45 per-dimension
coverages, and the pooled figure decomposes without approximation. A pooled 16.22% is
consistent both with 45 dimensions each near 16% and with a handful near zero dragging
down a majority near calibrated. Those are different findings and the paper cannot
currently tell them apart.

THE RESOLUTION LIMIT WAS FIXED IN ADVANCE and is severe at h=1. Per-dimension coverage on
B trajectories at horizon h is a fraction over B*h indicators, so it is quantised at
1/(B*h): 5.0 points on the released checkpoint at h=1, and 25 points per seed on the
ensemble-5 arms. M-63 therefore restricts the IQR test to the n=20 arena in advance and
reports the ensemble-5 distribution descriptively. Fixing which threshold applies where
before the run is the point; choosing afterwards is what S-12 was withdrawn for.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import rwm_data as R  # noqa: E402
import per_triple_cache as PTC  # noqa: E402

TARGET1 = 68.27          # erf(1/sqrt(2)), section 3.1
TARGET2 = 95.45
HS = (1, 100)

# The 45 channel names. Layout verified against pinned upstream at
# robotic_world_model_lite/scripts/envs/anymal_d_flat.py:58-64 -- base_lin_vel 0:3,
# base_ang_vel 3:6, projected_gravity 6:9, joint_pos 9:21, joint_vel 21:33,
# joint_torque 33:45 -- and mirrored at src/rwm_data.py:20-27.
NAMES = (["v_x", "v_y", "v_z", "w_x", "w_y", "w_z", "g_x", "g_y", "g_z"]
         + [f"q_{l}_{a}" for a in ("HAA", "HFE", "KFE") for l in ("LF", "LH", "RF", "RH")]
         + [f"qd_{l}_{a}" for a in ("HAA", "HFE", "KFE") for l in ("LF", "LH", "RF", "RH")]
         + [f"tau_{l}_{a}" for a in ("HAA", "HFE", "KFE") for l in ("LF", "LH", "RF", "RH")])
assert len(NAMES) == 45

# R-29: the seven dimensions where the released checkpoint loses to the hold-last floor.
# A DIFFERENT QUANTITY at a DIFFERENT horizon on a DIFFERENT arena -- per-dimension nRMSE
# against a floor at h=368 over 3,200 trajectories -- so the overlap below is reported as
# suggestive and carries no P-value. M-63 said so before the run.
R29_DIMS = ["v_z", "w_x", "w_y", "g_x", "g_y", "g_z", "tau_RF_HAA"]


def per_dim_coverage(abs_err, sig, k=1.0):
    """Fraction of triples within k sigma, per dimension. Shape (n_traj, h, 45)."""
    hit = abs_err <= k * sig
    return hit.reshape(-1, 45).mean(axis=0) * 100.0


def describe(cov, pooled, arena, n_indicators_per_dim):
    order = np.argsort(cov)
    worst5 = [{"dim": NAMES[i], "index": int(i), "coverage_pct": float(cov[i])}
              for i in order[:5]]
    # Shortfall decomposes exactly because pooling is an unweighted mean over dimensions.
    short = TARGET1 - cov
    tot = float(short.sum())
    share5 = float(short[order[:5]].sum() / tot) if tot > 0 else None
    q1, q3 = np.percentile(cov, [25, 75])
    return {
        "arena": arena,
        "n_indicators_per_dimension": int(n_indicators_per_dim),
        "quantisation_points": 100.0 / n_indicators_per_dim,
        "pooled_coverage_pct": float(pooled),
        "pooled_equals_unweighted_mean": bool(abs(float(cov.mean()) - pooled) < 1e-9),
        "median_pct": float(np.median(cov)),
        "iqr_points": float(q3 - q1),
        "q1_pct": float(q1), "q3_pct": float(q3),
        "min_pct": float(cov.min()), "max_pct": float(cov.max()),
        "pooled_inside_iqr": bool(q1 <= pooled <= q3),
        "five_worst": worst5,
        "shortfall_total_points": tot,
        "five_worst_share_of_shortfall": share5,
        "per_dimension": [{"dim": NAMES[i], "coverage_pct": float(cov[i])} for i in range(45)],
        "overlap_with_R29": {
            "r29_dims": R29_DIMS,
            "intersection_with_five_worst": sorted(
                set(R29_DIMS) & {w["dim"] for w in worst5}),
            "n_intersection": len(set(R29_DIMS) & {w["dim"] for w in worst5}),
            "caveat": ("R-29 is per-dimension nRMSE against the hold-last floor at h=368 "
                       "over 3,200 trajectories; this is coverage at +-1 sigma at h=1 and "
                       "h=100 on 20. A different quantity, horizon and arena. Suggestive "
                       "only; no P-value attaches."),
        },
    }


def main():
    out = {"rule": "M-63", "target_pm1_pct": TARGET1, "target_pm2_pct": TARGET2,
           "decomposition": ("pooled coverage is the unweighted mean of the 45 "
                             "per-dimension coverages, because every dimension "
                             "contributes the same number of triples"),
           "thresholds_committed_in_advance": {
               "uniform": "IQR of the 45 per-dimension coverages < 15 points AND the "
                          "pooled figure lies inside that IQR",
               "concentrated": "the five worst dimensions carry more than half the "
                               "shortfall from 68.27%",
               "iqr_test_applies_to": "the released checkpoint at n_independent = 20 only",
               "why": ("per-dimension coverage at h=1 on 4 trajectories takes only five "
                       "values; the IQR threshold is meaningless there and M-63 restricted "
                       "it before the run"),
           },
           "arenas": {}}

    print("=" * 100)
    print("M-63 — PER-DIMENSION COVERAGE AT +-1 SIGMA")
    print("=" * 100)

    # ---- arena 1: released checkpoint, all ten episodes, n_independent = 20 -----
    a, _m = PTC.read("released_ckpt_ens5", "all ten episodes", 400)
    abs_err, epi = np.abs(a["err"]), a["sig_epistemic"]
    for h in HS:
        e, g = abs_err[:, :h], epi[:, :h]
        cov = per_dim_coverage(e, g)
        pooled = float((e <= g).mean() * 100.0)
        d = describe(cov, pooled, "all ten episodes (n_independent = 20)",
                     e.shape[0] * e.shape[1])
        d["threshold_applies"] = True
        d["verdict"] = ("UNIFORM" if (d["iqr_points"] < 15 and d["pooled_inside_iqr"])
                        else ("CONCENTRATED" if d["five_worst_share_of_shortfall"] > 0.5
                              else "NEITHER"))
        out["arenas"][f"released_ckpt_all_ten_h{h}"] = d
        print(f"\n  RELEASED CHECKPOINT, all ten episodes, h={h}   "
              f"(quantised at {d['quantisation_points']:.2f} points)")
        print(f"    pooled {pooled:.2f}%   median {d['median_pct']:.2f}%   "
              f"IQR {d['iqr_points']:.2f} pts   range [{d['min_pct']:.2f}, {d['max_pct']:.2f}]")
        print(f"    five worst: " + ", ".join(
            f"{w['dim']} {w['coverage_pct']:.1f}%" for w in d["five_worst"]))
        print(f"    they carry {100*d['five_worst_share_of_shortfall']:.1f}% of the shortfall"
              f"   ->  {d['verdict']}")
        if d["overlap_with_R29"]["n_intersection"]:
            print(f"    overlap with R-29's seven: "
                  f"{d['overlap_with_R29']['intersection_with_five_worst']} (suggestive only)")

    # ---- arena 2: the ensemble-5 arms, out-of-sample, 3 seeds, n = 4 ------------
    for h in HS:
        covs, pools = [], []
        for sd in (0, 1, 2):
            arr, _ = PTC.read(f"armA_ens5_seed{sd}", "out-of-sample held-out pair", 400)
            e, g = np.abs(arr["err"])[:, :h], arr["sig_epistemic"][:, :h]
            covs.append(per_dim_coverage(e, g))
            pools.append(float((e <= g).mean() * 100.0))
        cov = np.mean(covs, axis=0)
        pooled = float(np.mean(pools))
        n_ind_per_dim = 4 * h * 3          # three seeds pooled
        d = describe(cov, pooled, "out-of-sample held-out pair, ensemble-5, 3 seeds "
                                  "(n_independent = 4)", n_ind_per_dim)
        d["threshold_applies"] = False
        d["verdict"] = "NOT ASSESSED — descriptive only"
        d["why_no_threshold"] = (
            "M-63 restricted the IQR test to the n=20 arena in advance. Per seed a "
            "per-dimension coverage at h=1 takes only the five values 0, 25, 50, 75, 100%; "
            "pooling three seeds gives 8.3-point steps. The distribution is reported "
            "descriptively and no threshold is applied.")
        d["per_seed_pooled_pct"] = pools
        out["arenas"][f"armA_ens5_oos_h{h}"] = d
        print(f"\n  ENSEMBLE-5 ARMS, out-of-sample, 3 seeds, h={h}   "
              f"(quantised at {d['quantisation_points']:.2f} points — descriptive only)")
        print(f"    pooled {pooled:.2f}%   median {d['median_pct']:.2f}%   "
              f"IQR {d['iqr_points']:.2f} pts   range [{d['min_pct']:.2f}, {d['max_pct']:.2f}]")
        print(f"    five worst: " + ", ".join(
            f"{w['dim']} {w['coverage_pct']:.1f}%" for w in d["five_worst"]))

    # ---- the rule's verdict ----------------------------------------------------
    gov = out["arenas"]["released_ckpt_all_ten_h1"]
    out["verdict"] = {
        "governing_arena": "released checkpoint, all ten episodes, h=1, n_independent=20",
        "result": gov["verdict"],
        "iqr_points": gov["iqr_points"],
        "pooled_inside_iqr": gov["pooled_inside_iqr"],
        "five_worst_share_of_shortfall": gov["five_worst_share_of_shortfall"],
        "five_worst": [w["dim"] for w in gov["five_worst"]],
        "reading": ("CONCENTRATED is the sharper finding and names which channels fail; "
                    "UNIFORM says the failure is a property of the whole state vector. "
                    "Both were reportable in advance and neither is a bad outcome."),
    }
    print(f"\n  VERDICT (governing arena, h=1): {out['verdict']['result']}")

    op = os.path.join(R.RESULTS, "m63_per_dimension_coverage.json")
    json.dump(out, open(op, "w"), indent=2)
    print(f"  wrote {R.rel(op)}")


if __name__ == "__main__":
    main()
