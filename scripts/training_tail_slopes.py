"""
Round 2, N3 part 4 (post hoc) -- are the runs still learning when they stop?

PLAN round2 Annex 1, N3 part 4. The training-loss slope over the final 250 iterations, for
every M/N sweep run, every Table S7 baseline run, and Arm A and Arm B at 2,500 and 10,000
iterations. The definition is scripts/step5_train.py's, which stores it as
state_loss_tail_slope_250: np.polyfit(np.arange(250), curves["state"][-250:], 1)[0], in loss
units per iteration. Where a run artifact stores it, it is used; where it does not (the
baselines), it is computed from curves["state"] by the same definition.

ASSERTED first: the definition reproduces every stored slope (sweep runs, Arm A and Arm B at
2,500 and at 10,000) to 1e-12 relative.

Also recorded: each 10k run's slope over iterations 2,251-2,500 of its own curve, beside the
2,500-iteration run's, which it replicates.

Writes results/training_tail_slopes.json.
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, os.pardir, "src"))
import numpy as np  # noqa: E402

import rwm_data as R  # noqa: E402

TAIL = 250


def slope(curve):
    tail = np.asarray(curve[-TAIL:], dtype=np.float64)
    assert len(tail) == TAIL
    return float(np.polyfit(np.arange(len(tail)), tail, 1)[0])


def main():
    res = R.RESULTS
    runs = {}
    groups = {
        "sweep": sorted(glob.glob(os.path.join(res, "mn_sweep_run_M*_N*_seed[012].json"))),
        "baseline": sorted(glob.glob(os.path.join(res, "baseline_run_*_s7_seed[012].json"))),
        "arm_2500": sorted(glob.glob(os.path.join(res, "step5_arm[AB]_seed[012].json"))),
        "arm_10000": sorted(glob.glob(os.path.join(res, "step5_arm[AB]_seed[012]_10k.json"))),
    }
    assert [len(groups[g]) for g in groups] == [24, 18, 6, 6], {g: len(v) for g, v in groups.items()}
    checked, maxrel = 0, 0.0
    for g, files in groups.items():
        for f in files:
            d = json.load(open(f))
            curve = d["curves"]["state"]
            mine = slope(curve)
            stored = d.get("state_loss_tail_slope_250")
            if stored is not None:
                rel = abs(mine - stored) / max(abs(stored), 1e-300)
                assert rel < 1e-12, f"{f}: recomputed slope {mine} vs stored {stored}"
                maxrel, checked = max(maxrel, rel), checked + 1
            name = os.path.basename(f)[:-5]
            runs[name] = {"group": g, "iterations": len(curve), "slope_per_iter": stored if stored is not None else mine,
                          "source": "stored state_loss_tail_slope_250" if stored is not None else "computed from curves.state",
                          "still_falling": (stored if stored is not None else mine) < 0,
                          "final_state_loss": float(curve[-1])}
            if g == "arm_10000":
                runs[name]["slope_iters_2251_2500"] = slope(curve[:2500])
                twin = name.replace("_10k", "")
                runs[name]["twin_2500_run"] = twin

    for name, r in runs.items():
        if r["group"] == "arm_10000":
            r["twin_2500_slope"] = runs[r["twin_2500_run"]]["slope_per_iter"]
            r["twin_matches"] = abs(r["slope_iters_2251_2500"] - r["twin_2500_slope"]) <= 1e-12 * max(1.0, abs(r["twin_2500_slope"]))

    def span(group_names):
        v = [r["slope_per_iter"] for r in runs.values() if r["group"] in group_names]
        return {"n": len(v), "min": min(v), "max": max(v), "n_falling": sum(x < 0 for x in v), "n_flat_or_rising": sum(x >= 0 for x in v)}

    out = {"purpose": "round 2 N3 part 4 (post hoc): training-loss slope over the final 250 iterations",
           "post_hoc": True,
           "definition": "np.polyfit(np.arange(250), curves['state'][-250:], 1)[0], loss units per iteration (scripts/step5_train.py)",
           "definition_reproduces_stored": {"runs_checked": checked, "max_rel_diff": maxrel, "tolerance": 1e-12},
           "runs": runs,
           "summary": {"at_2500_all": span({"sweep", "baseline", "arm_2500"}),
                       "sweep": span({"sweep"}), "baseline": span({"baseline"}), "arm_2500": span({"arm_2500"}),
                       "arm_10000": span({"arm_10000"})}}
    op = os.path.join(res, "training_tail_slopes.json")
    json.dump(out, open(op, "w"), indent=2)
    print("=" * 90)
    print("N3 part 4 (post hoc) — state-loss slope over the final 250 iterations")
    print("=" * 90)
    print(f"  the definition reproduces {checked} stored slopes (max relative diff {maxrel:.1e})")
    for k, v in out["summary"].items():
        print(f"  {k:<12} n={v['n']:>2}  slopes {v['min']:+.3e} to {v['max']:+.3e}   falling {v['n_falling']}, flat or rising {v['n_flat_or_rising']}")
    for name, r in runs.items():
        if r["group"] == "arm_10000":
            print(f"  {name}: at 2,251-2,500 {r['slope_iters_2251_2500']:+.3e} vs its 2,500 twin {r['twin_2500_slope']:+.3e} "
                  f"({'identical' if r['twin_matches'] else 'DIFFERENT'}); at 10,000 {r['slope_per_iter']:+.3e}")
    print(f"  wrote {R.rel(op)}")


if __name__ == "__main__":
    main()
