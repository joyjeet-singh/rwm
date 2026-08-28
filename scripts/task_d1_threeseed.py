"""D1 — verify the new 10k runs, then recompute the headline over three seeds.

Two jobs, in order, because the second is worthless if the first fails.

1. CROSS-CHECK. A 10,000-iteration run and the 2,500-iteration run at the same
   seed share their first 2,500 iterations exactly: same seed, same data, same
   optimiser, and training here is bitwise reproducible. Every logged value in
   [0, 2500) must therefore be identical. Any mismatch means the runs are not
   comparable and the three-seed aggregate must not be formed.

2. AGGREGATE. Recompute the out-of-sample comparison over three seeds, reporting
   mean +- sd with ddof=1, alongside the single-seed figure the paper currently
   quotes.

   Reported at TWO horizons and the distinction matters. M-23 -- the rule that
   governs this comparison -- is stated over h=368, which 3.1 now labels the
   upstream's open-loop DIAGNOSTIC length rather than a deployment horizon. The
   rule's verdict stands as returned at the horizon it was written over; nothing
   here re-anchors it. h=100, the method's own imagination rollout length, is
   added beside it so the section can say what the same comparison does at the
   horizon the method actually deploys at, which the rest of the paper is
   anchored to. The top-level `aggregate` block stays h=368 so that M-23's
   verdict and every downstream key keep the horizon they were computed at.

Writes results/task_d1_threeseed.json.
"""
import glob
import json
import os
import statistics as st
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import torch  # noqa: E402
import rwm_data as R  # noqa: E402
import rollout_eval as E  # noqa: E402
import rwm_metrics as MET  # noqa: E402
import rwm_model as M  # noqa: E402

SEEDS = (0, 1, 2)
ARMS = ("A", "B")
START = E.START_STEP
LEN, H = 400, 368               # H: the horizon M-23 is stated over. Do not re-anchor.


def _deployment_horizon():
    """The method's own imagination rollout length, from V2 rather than typed, so
    that a change to which horizon the method deploys at cannot leave this script
    measuring the old one."""
    p = os.path.join(R.RESULTS, "v2_deployment_horizon.json")
    return int(json.load(open(p))["verdict"]["deployment_horizon_is"])


HORIZONS = (_deployment_horizon(), H)
CURVES = ("state", "bound", "contact", "termination", "total", "grad_norm")


def cross_check():
    """Every logged value in [0, 2500) must be identical between the 10k run and
    the 2500 run at the same seed."""
    rows = []
    for a in ARMS:
        for s in SEEDS:
            p10 = f"results/step5_arm{a}_seed{s}_10k.json"
            p25 = f"results/step5_arm{a}_seed{s}.json"
            if not (os.path.exists(p10) and os.path.exists(p25)):
                rows.append({"run": f"arm{a}_seed{s}", "status": "MISSING",
                             "have_10k": os.path.exists(p10), "have_2500": os.path.exists(p25)})
                continue
            d10, d25 = json.load(open(p10)), json.load(open(p25))
            n = min(len(d25["curves"]["state"]), 2500)
            worst, worst_key, ndiff, ntot = 0.0, None, 0, 0
            for k in CURVES:
                a10, a25 = d10["curves"][k][:n], d25["curves"][k][:n]
                for i, (x, y) in enumerate(zip(a10, a25)):
                    ntot += 1
                    if x != y:
                        ndiff += 1
                        d = abs(x - y)
                        if d > worst:
                            worst, worst_key = d, f"{k}[{i}]"
            rows.append({"run": f"arm{a}_seed{s}", "status": "MATCH" if ndiff == 0 else "MISMATCH",
                         "values_compared": ntot, "differing": ndiff,
                         "worst_abs_diff": worst, "worst_at": worst_key,
                         "iterations_compared": n})
    return rows


def per_traj(model, starts, L, h):
    idx = np.asarray(starts)[:, None] + np.arange(L)[None, :]
    raw = R.DATA[idx]
    st_ = torch.as_tensor(R.normalise_state(raw[:, :, R.STATE_COLS],
                                            R.CFG["state_data_mean"], R.CFG["state_data_std"]),
                          dtype=torch.float32)
    ac = torch.as_tensor(raw[:, :, R.ACTION_COLS], dtype=torch.float32)
    p = model.rollout(st_.clone(), ac, START, action_offset=1)
    nu = (p[:, START:START + h] - st_[:, START:START + h]).abs().sum(-1)
    de = st_[:, START:START + h].abs().sum(-1)
    return (nu / de).mean(1).numpy()


def aggregate():
    paths = R.repo_paths()
    R.CFG = R.load_reference_config(paths["lite"])
    R.DATA, ep = R.load_data(paths["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"),
                         verbose=False)
    hold = list(split["holdout_episodes"])
    starts = MET.non_overlapping_starts(ep, hold, LEN)
    per_arm = {h: {} for h in HORIZONS}
    for a in ARMS:
        vals = {h: {} for h in HORIZONS}
        for s in SEEDS:
            w = f"runs/arm{a}_seed{s}_10k/weights_10000.pt"
            if not os.path.exists(w):
                continue
            m = M.build_from_config(R.CFG, ensemble_size=1)
            m.load_state_dict(torch.load(w, map_location="cpu")["model_state_dict"], strict=True)
            m.eval()
            # One rollout per seed, sliced at each horizon: the h=100 figure is a
            # prefix of the same rollout, not a second pass, so the two cannot
            # disagree about anything but their depth.
            for h in HORIZONS:
                vals[h][s] = float(per_traj(m, starts, LEN, h).mean())
        for h in HORIZONS:
            per_arm[h][a] = vals[h]
    return per_arm, int(MET.n_independent(starts, LEN))


def main():
    print("D1 — THREE-SEED RECOMPUTATION")
    print("=" * 84)
    xc = cross_check()
    print("  1. cross-check: 10k run vs the 2,500 run at the same seed\n")
    print(f"     {'run':<14}{'status':<10}{'compared':>10}{'differing':>11}{'worst':>12}")
    for r in xc:
        if r["status"] == "MISSING":
            print(f"     {r['run']:<14}{'MISSING':<10}"
                  f"  (10k={r['have_10k']}, 2500={r['have_2500']})")
        else:
            print(f"     {r['run']:<14}{r['status']:<10}{r['values_compared']:>10}"
                  f"{r['differing']:>11}{r['worst_abs_diff']:>12.3e}")
    bad = [r for r in xc if r["status"] == "MISMATCH"]
    missing = [r for r in xc if r["status"] == "MISSING"]
    out = {"cross_check": xc, "n_mismatch": len(bad), "n_missing": len(missing)}

    if bad:
        print("\n     !! CROSS-CHECK FAILED — the runs are not comparable.")
        print("     Not forming the three-seed aggregate.")
        json.dump(out, open(os.path.join(R.RESULTS, "task_d1_threeseed.json"), "w"), indent=2)
        return 1
    if missing:
        print(f"\n     {len(missing)} run(s) not yet present; aggregate is partial.")

    per_arm, n_ind = aggregate()
    by_h = {}
    for h in HORIZONS:
        print(f"\n  2. h={h} out-of-sample, n_independent = {n_ind}"
              + ("   [M-23's horizon]" if h == H else "   [the deployment horizon]") + "\n")
        agg = {}
        for a in ARMS:
            v = per_arm[h][a]
            if len(v) >= 2:
                mean, sd = st.mean(v.values()), st.stdev(v.values())
            else:
                mean, sd = (list(v.values())[0], float("nan")) if v else (float("nan"),) * 2
            agg[a] = {"per_seed": v, "mean": mean, "sd_ddof1": sd, "n_seeds": len(v)}
            seeds = "  ".join(f"seed{s} {x:.4f}" for s, x in sorted(v.items()))
            print(f"     Arm {a}: {seeds}")
            print(f"             mean {mean:.4f} ± {sd:.4f}  (n={len(v)}, ddof=1)")
        if agg["A"]["n_seeds"] and agg["B"]["n_seeds"]:
            ratio = agg["B"]["mean"] / agg["A"]["mean"]
            print(f"\n     ratio B/A over {agg['A']['n_seeds']} seeds: {ratio:.2f}×")
            agg["ratio_B_over_A"] = ratio
        by_h[str(h)] = agg
    # `aggregate` stays the h=368 block: M-23 is stated there and every key the
    # paper already carries was computed there. `by_horizon` is the addition.
    agg = by_h[str(H)]
    out["aggregate"] = agg
    out["by_horizon"] = by_h
    out["horizons"] = list(HORIZONS)
    out["n_independent"] = n_ind
    out["horizon"] = H
    out["rule_horizon"] = H
    out["rule_horizon_note"] = (
        "M-23 (commit efc35b8) is stated over h=368, which 3.1 labels the upstream's "
        "open-loop diagnostic length. Its verdict stands as returned at that horizon. "
        "by_horizon['100'] reports the same comparison at the method's own imagination "
        "rollout length and is reported alongside, not substituted for it.")
    op = os.path.join(R.RESULTS, "task_d1_threeseed.json")
    json.dump(out, open(op, "w"), indent=2)
    print(f"\n  wrote {R.rel(op)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
