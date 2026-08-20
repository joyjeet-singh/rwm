"""Is the bootstrap resampling the right unit?

task5_2_bootstrap.py and task4_contamination_analysis.py both build their sample as

    A = np.concatenate([per_traj(model(seed=s), starts, L, h) for s in SEEDS])

so the vector handed to the resampler has length 3 x n_traj, while the record written
alongside it reports n_independent = n_traj and task5_2_report.txt describes the interval
as being over independent trajectories.

Each trajectory therefore appears three times, once per training seed, and those three
values share the same held-out rows. Resampling them independently breaks that clustering
and can only make the interval narrower than it should be.

This script recomputes the same per-trajectory values and compares:

  naive   -- resample all 3*n_traj values independently, as implemented
  cluster -- resample TRAJECTORIES, carrying all three seeds with each draw

and reports whether any 'excludes zero' verdict changes. Writes
results/review_bootstrap_unit.json and results/review_bootstrap_unit_report.txt.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import torch  # noqa: E402
import rwm_data as R  # noqa: E402
import rollout_eval as E  # noqa: E402
import rwm_metrics as MET  # noqa: E402
import rwm_model as M  # noqa: E402

START = E.START_STEP
SEEDS, CKPTS = (0, 1, 2), (500, 2500)
N_BOOT = 10000

paths = R.repo_paths()
cfg = R.load_reference_config(paths["lite"])
data, ep = R.load_data(paths["csv"], verbose=False)
split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"),
                     verbose=False)
ARENAS = {"out-of-sample": list(split["holdout_episodes"]),
          "in-sample": list(split["train_episodes"])}


def per_traj(model, starts, L, h):
    """One relative-L1 value per trajectory. Identical to task5_2_bootstrap.per_traj."""
    idx = np.asarray(starts)[:, None] + np.arange(L)[None, :]
    raw = data[idx]
    st = torch.as_tensor(R.normalise_state(raw[:, :, R.STATE_COLS],
                                           cfg["state_data_mean"], cfg["state_data_std"]),
                         dtype=torch.float32)
    ac = torch.as_tensor(raw[:, :, R.ACTION_COLS], dtype=torch.float32)
    p = model.rollout(st.clone(), ac, START, action_offset=1)
    nu = (p[:, START:START + h] - st[:, START:START + h]).abs().sum(-1)
    de = st[:, START:START + h].abs().sum(-1)
    return (nu / de).mean(1).numpy()


def load(arm, seed, ckpt):
    m = M.build_from_config(cfg, ensemble_size=1)
    sd = torch.load(f"runs/arm{arm}_seed{seed}/weights_{ckpt}.pt", map_location="cpu")
    m.load_state_dict(sd["model_state_dict"], strict=True)
    m.eval()
    return m


def boot_naive(A, B, n=N_BOOT, seed=0):
    """As implemented: resample the pooled (seed, trajectory) values."""
    rng = np.random.default_rng(seed)
    k = len(A)
    idx = rng.integers(0, k, size=(n, k))
    g = B[idx].mean(1) - A[idx].mean(1)
    return float(g.mean()), float(np.percentile(g, 2.5)), float(np.percentile(g, 97.5))


def boot_cluster(Am, Bm, n=N_BOOT, seed=0):
    """Correct unit: resample TRAJECTORIES, carrying all seeds. Am, Bm are (n_seed, n_traj)."""
    rng = np.random.default_rng(seed)
    t = Am.shape[1]
    idx = rng.integers(0, t, size=(n, t))
    # for each resample, take those trajectory columns across every seed, then mean
    g = np.empty(n)
    for i in range(n):
        c = idx[i]
        g[i] = Bm[:, c].mean() - Am[:, c].mean()
    return float(g.mean()), float(np.percentile(g, 2.5)), float(np.percentile(g, 97.5))


def main():
    out = {}
    rows = []
    for arena, eps in ARENAS.items():
        for L, hs in ((400, (8, 368)), (200, (8, 168))):
            st_ = MET.non_overlapping_starts(ep, eps, L)
            ni = MET.n_independent(st_, L)
            for c in CKPTS:
                mods = {(a, s): load(a, s, c) for a in ("A", "B") for s in SEEDS}
                for h in hs:
                    Am = np.stack([per_traj(mods[("A", s)], st_, L, h) for s in SEEDS])
                    Bm = np.stack([per_traj(mods[("B", s)], st_, L, h) for s in SEEDS])
                    A, B = Am.reshape(-1), Bm.reshape(-1)

                    gn, lon, hin = boot_naive(A, B)
                    gc, loc, hic = boot_cluster(Am, Bm)

                    # how much of the variance is between trajectories vs between seeds?
                    d = Bm - Am                       # (n_seed, n_traj) per-trajectory gap
                    traj_means = d.mean(axis=0)
                    var_between_traj = float(traj_means.var(ddof=1)) if d.shape[1] > 1 else 0.0
                    var_within_traj = float(d.var(axis=0, ddof=1).mean()) if d.shape[0] > 1 else 0.0

                    key = f"{arena}|{L}|{c}|h{h}"
                    rec = {
                        "n_trajectories": int(Am.shape[1]),
                        "n_independent_reported": int(ni),
                        "n_pooled_values": int(len(A)),
                        "naive": {"gap": gn, "ci": [lon, hin], "width": hin - lon,
                                  "excludes_zero": bool(lon > 0 or hin < 0)},
                        "cluster": {"gap": gc, "ci": [loc, hic], "width": hic - loc,
                                    "excludes_zero": bool(loc > 0 or hic < 0)},
                        "width_ratio_cluster_over_naive": (hic - loc) / (hin - lon),
                        "var_between_trajectories": var_between_traj,
                        "var_within_trajectory_across_seeds": var_within_traj,
                    }
                    rec["verdict_changes"] = (rec["naive"]["excludes_zero"]
                                              != rec["cluster"]["excludes_zero"])
                    out[key] = rec
                    rows.append((key, rec))
                    print(f"  {key:<34} naive {'EXCL' if rec['naive']['excludes_zero'] else 'span'}"
                          f"  cluster {'EXCL' if rec['cluster']['excludes_zero'] else 'span'}"
                          f"  width x{rec['width_ratio_cluster_over_naive']:.2f}"
                          f"{'   <-- VERDICT CHANGES' if rec['verdict_changes'] else ''}")

    changed = [k for k, r in rows if r["verdict_changes"]]
    ratios = [r["width_ratio_cluster_over_naive"] for _, r in rows]
    summary = {
        "n_cells": len(rows),
        "n_verdict_changes": len(changed),
        "cells_that_change": changed,
        "width_ratio_min": min(ratios), "width_ratio_max": max(ratios),
        "width_ratio_mean": float(np.mean(ratios)),
    }
    out["_summary"] = summary

    op = os.path.join(R.RESULTS, "review_bootstrap_unit.json")
    json.dump(out, open(op, "w"), indent=2)

    L_ = []
    A_ = L_.append
    A_("REVIEW -- IS THE BOOTSTRAP RESAMPLING THE RIGHT UNIT?")
    A_("=" * 86)
    A_("")
    A_("  naive   = resample all (seed x trajectory) values independently, as implemented in")
    A_("            scripts/task5_2_bootstrap.py:28-32 and task4_contamination_analysis.py:27")
    A_("  cluster = resample TRAJECTORIES, carrying all three seeds with each draw")
    A_("")
    A_(f"  {'cell':<34}{'n_traj':>7}{'pooled':>7}  {'naive':>12}  {'cluster':>12}  {'width':>7}")
    for key, r in rows:
        A_(f"  {key:<34}{r['n_trajectories']:>7}{r['n_pooled_values']:>7}  "
           f"{('EXCLUDES' if r['naive']['excludes_zero'] else 'spans 0'):>12}  "
           f"{('EXCLUDES' if r['cluster']['excludes_zero'] else 'spans 0'):>12}  "
           f"x{r['width_ratio_cluster_over_naive']:>6.2f}"
           f"{'  <-- CHANGES' if r['verdict_changes'] else ''}")
    A_("")
    A_(f"  cells: {summary['n_cells']}   verdict changes: {summary['n_verdict_changes']}")
    A_(f"  CI width ratio (cluster / naive): min x{summary['width_ratio_min']:.2f}  "
       f"mean x{summary['width_ratio_mean']:.2f}  max x{summary['width_ratio_max']:.2f}")
    if changed:
        A_("")
        A_("  CELLS WHOSE VERDICT DEPENDS ON THE RESAMPLING UNIT:")
        for k in changed:
            A_(f"    {k}")
    A_("")
    A_(f"  written: {R.rel(op)}")
    rp = os.path.join(R.RESULTS, "review_bootstrap_unit_report.txt")
    open(rp, "w").write("\n".join(L_) + "\n")
    print()
    print("\n".join(L_))


if __name__ == "__main__":
    main()
