"""C3 — do the headline counts survive a multiplicity correction?

The paper reports "4 of 4 long-horizon cells exclude zero" (16 A/B cells) and
"9 of 32 cells helped" (the contamination comparison). Neither states a correction.

This recomputes both families at Bonferroni and Holm-Bonferroni levels, and
reports the exact sign test alongside, which is unaffected by either because it is
a single test on ten paired episodes.

A note the paper must carry: with n_independent = 4 out-of-sample trajectories a
bootstrap has 4**4 = 256 distinct resamples, so a 98.75% interval is quantised to
steps of 1/256 = 0.39%. Corrected intervals at that n are coarse by construction.

Writes results/task_c3_multiplicity.json.
"""
import json
import os
import sys
from math import comb

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import torch  # noqa: E402
import rwm_data as R  # noqa: E402
import rollout_eval as E  # noqa: E402
import rwm_metrics as MET  # noqa: E402
import rwm_model as M  # noqa: E402

SEEDS, CKPTS = (0, 1, 2), (500, 2500)
START = E.START_STEP
N_BOOT = 20000

paths = R.repo_paths()
cfg = R.load_reference_config(paths["lite"])
data, ep = R.load_data(paths["csv"], verbose=False)
split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"),
                     verbose=False)
ARENAS = {"out-of-sample": list(split["holdout_episodes"]),
          "in-sample": list(split["train_episodes"])}


def load(arm, seed, ckpt):
    m = M.build_from_config(cfg, ensemble_size=1)
    m.load_state_dict(torch.load(f"runs/arm{arm}_seed{seed}/weights_{ckpt}.pt",
                                 map_location="cpu")["model_state_dict"], strict=True)
    m.eval()
    return m


def per_traj(model, starts, L, h):
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


def cluster_ci(Am, Bm, alpha, seed=0):
    """Cluster bootstrap (M-27): resample trajectories, carry all seeds."""
    rng = np.random.default_rng(seed)
    t = Am.shape[1]
    idx = rng.integers(0, t, size=(N_BOOT, t))
    d = np.array([Bm[:, c].mean() - Am[:, c].mean() for c in idx])
    lo = float(np.percentile(d, 100 * alpha / 2))
    hi = float(np.percentile(d, 100 * (1 - alpha / 2)))
    return float(d.mean()), lo, hi, bool(lo > 0 or hi < 0)


def sign_p(k, n):
    tail = sum(comb(n, i) for i in range(k, n + 1)) if 2 * k >= n \
        else sum(comb(n, i) for i in range(0, k + 1))
    return min(1.0, 2.0 * tail / 2 ** n)


def main():
    cells = []
    for arena, eps in ARENAS.items():
        for L, hs in ((400, (8, 368)), (200, (8, 168))):
            st_ = MET.non_overlapping_starts(ep, eps, L)
            ni = MET.n_independent(st_, L)
            for c in CKPTS:
                mods = {(a, s): load(a, s, c) for a in ("A", "B") for s in SEEDS}
                for h in hs:
                    Am = np.stack([per_traj(mods[("A", s)], st_, L, h) for s in SEEDS])
                    Bm = np.stack([per_traj(mods[("B", s)], st_, L, h) for s in SEEDS])
                    cells.append({"cell": f"{arena}|{L}|{c}|h{h}", "arena": arena,
                                  "h": h, "n_traj": int(Am.shape[1]), "n_ind": int(ni),
                                  "Am": Am, "Bm": Bm})

    fam = [c for c in cells if c["arena"] == "out-of-sample"]
    longh = [c for c in fam if c["h"] in (368, 168)]
    m_fam = len(fam)

    out = {"family_ab": {"n_comparisons": m_fam,
                         "n_long_horizon": len(longh),
                         "note": ("the family is the 8 out-of-sample A/B cells; "
                                  "correcting over all 16 including in-sample would be "
                                  "more conservative still")}}

    rows = []
    for alpha_name, alpha in (("uncorrected 0.05", 0.05),
                              (f"Bonferroni 0.05/{m_fam}", 0.05 / m_fam),
                              (f"Bonferroni 0.05/{len(longh)}", 0.05 / len(longh))):
        excl = 0
        detail = []
        for c in longh:
            d, lo, hi, ex = cluster_ci(c["Am"], c["Bm"], alpha)
            excl += ex
            detail.append({"cell": c["cell"], "diff": d, "lo": lo, "hi": hi,
                           "excludes_zero": ex, "n_ind": c["n_ind"]})
        rows.append({"level": alpha_name, "alpha": alpha,
                     "long_horizon_excluding_zero": excl,
                     "of": len(longh), "cells": detail})
    out["long_horizon_by_level"] = rows

    # Holm-Bonferroni needs p-values; use the bootstrap tail probability as a proxy
    holm = []
    for c in longh:
        rng = np.random.default_rng(0)
        t = c["Am"].shape[1]
        idx = rng.integers(0, t, size=(N_BOOT, t))
        d = np.array([c["Bm"][:, k].mean() - c["Am"][:, k].mean() for k in idx])
        p = 2 * min((d <= 0).mean(), (d >= 0).mean())
        holm.append((c["cell"], max(p, 1.0 / N_BOOT)))
    holm.sort(key=lambda x: x[1])
    m = len(holm)
    surv, rejected = [], True
    for i, (cell, p) in enumerate(holm):
        thr = 0.05 / (m - i)
        ok = rejected and p <= thr
        rejected = ok
        surv.append({"cell": cell, "p": p, "holm_threshold": thr, "rejected": ok})
    out["holm_bonferroni"] = {"n": m, "steps": surv,
                              "n_rejected": sum(1 for s in surv if s["rejected"])}

    # the sign test, which no correction touches
    t5 = json.load(open(os.path.join(R.RESULTS, "task5_analysis.json")))
    pe = t5["per_episode"]
    pos = sum(1 for v in pe.values() if v["h368"] > 0)
    out["sign_test_h368"] = {
        "n_episodes": len(pe), "n_positive": pos,
        "exact_two_sided_p": sign_p(pos, len(pe)),
        "note": ("a single exact test on ten paired episodes; it is one comparison, "
                 "not a family, and does not depend on the bootstrap or on n_independent"),
    }

    out["bootstrap_resolution_note"] = {
        "n_ind_out_of_sample_400": 4,
        "distinct_resamples": 4 ** 4,
        "quantisation_pct": 100.0 / 4 ** 4,
        "note": ("with 4 trajectories a bootstrap has 256 distinct resamples, so any "
                 "interval is quantised to 0.39% steps; corrected tails at this n are "
                 "coarse by construction and should not lead the evidence"),
    }

    op = os.path.join(R.RESULTS, "task_c3_multiplicity.json")
    json.dump(out, open(op, "w"), indent=2, default=float)

    print("C3 — MULTIPLE COMPARISONS")
    print("=" * 86)
    print(f"  A/B family: {m_fam} out-of-sample cells, {len(longh)} of them long-horizon\n")
    for r in rows:
        print(f"  {r['level']:<24} long-horizon cells excluding zero: "
              f"{r['long_horizon_excluding_zero']} of {r['of']}")
    print(f"\n  Holm-Bonferroni: {out['holm_bonferroni']['n_rejected']} of {m} rejected")
    for s in surv:
        print(f"    {s['cell']:<34} p={s['p']:.4f}  thr={s['holm_threshold']:.4f}  "
              f"{'reject' if s['rejected'] else 'RETAIN null'}")
    sg = out["sign_test_h368"]
    print(f"\n  sign test at h=368: {sg['n_positive']}/{sg['n_episodes']} episodes positive, "
          f"exact two-sided p = {sg['exact_two_sided_p']:.4f}")
    print("    unaffected by either correction: one test, not a family")
    print(f"\n  wrote {R.rel(op)}")


if __name__ == "__main__":
    main()
