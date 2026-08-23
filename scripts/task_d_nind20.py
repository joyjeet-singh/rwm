"""D1, D2, D4 — the epistemic table at n=20, the forecast-index baseline, and the
penalty correlation with an interval.

All three share one expensive object: rollouts of the released five-member
checkpoint over ALL TEN episodes, giving 20 mutually non-overlapping 400-step
trajectories instead of the 4 the held-out pair admits. The released checkpoint
trained on all ten, so restricting it to two buys no independence -- the same
argument this paper makes elsewhere about that checkpoint. n=20 is five times the
sample and the coarse-bootstrap caveat that applies at n=4 does not apply here.

D1  the full uncertainty table at every horizon, at n_independent=20.

D2  THE BASELINE THE FOLLOW-UP NEVER RAN. arXiv:2504.16680 claims ensemble
    disagreement "closely follows the trend of the prediction error", justifying
    its role as a trust metric. A trust metric must beat a trivial alternative to
    be worth computing. The trivial alternative here is the forecast step index:
    a counter, available for free, requiring no ensemble and no model. We compute

      r(forecast index, |error|)      the counter
      r(epistemic sigma, |error|)     the trust metric
      partial r(epistemic, |error| . index)

    The partial correlation is the number that matters: it is what ensemble
    disagreement contributes BEYOND knowing how deep into the rollout you are.

D4  the scalar penalty as actually applied -- means.std(0).sum(-1) at
    envs/base.py:166 -- against total absolute error, with a cluster bootstrap
    over whole trajectories (never over trajectory x step, per M-27) and its
    n_independent stated.

Writes results/task_d_nind20.json.
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
import score_reference as S  # noqa: E402

HORIZONS = (1, 8, 32, 100, 128, 368)
START, LEN, N_BOOT = E.START_STEP, 400, 20000


def cluster_boot(fn, n_traj, rng, n_boot=N_BOOT):
    """Bootstrap resampling WHOLE TRAJECTORIES. M-27: resampling trajectory x step
    pairs narrows every interval by about sqrt(steps) and is wrong."""
    vals = []
    for _ in range(n_boot):
        idx = rng.integers(0, n_traj, n_traj)
        v = fn(idx)
        if v is not None and np.isfinite(v):
            vals.append(v)
    if not vals:
        return None, None, 0
    v = np.array(vals)
    return float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5)), len(v)


def pooled_corr(x, y):
    """x, y: (n_traj, T) -> scalar correlation over all pooled points."""
    a, b = x.ravel(), y.ravel()
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 3 or a[m].std() == 0 or b[m].std() == 0:
        return None
    return float(np.corrcoef(a[m], b[m])[0, 1])


def partial_corr(x, y, z):
    """r(x, y . z) -- correlation of x and y with z partialled out of both."""
    a, b, c = x.ravel(), y.ravel(), z.ravel()
    m = np.isfinite(a) & np.isfinite(b) & np.isfinite(c)
    a, b, c = a[m], b[m], c[m]
    if len(a) < 4 or a.std() == 0 or b.std() == 0 or c.std() == 0:
        return None
    ra = a - np.polyval(np.polyfit(c, a, 1), c)
    rb = b - np.polyval(np.polyfit(c, b, 1), c)
    if ra.std() == 0 or rb.std() == 0:
        return None
    return float(np.corrcoef(ra, rb)[0, 1])


def cluster_ci_from_per_traj(num, den, rng, n_boot=N_BOOT):
    """
    95% cluster-bootstrap interval for a ratio of means, resampling whole
    trajectories, computed from PER-TRAJECTORY partial sums.

    This is exact, not an approximation. The design is balanced -- every
    trajectory contributes the same h x 45 cells -- so the mean over any
    resampled set of trajectories is the mean of those trajectories' own means,
    and the ratio of pooled means is the ratio of the resampled per-trajectory
    means. Bootstrapping n numbers instead of n x h x 45 makes 20,000 draws
    cost nothing, which is why every cell in 5.2 can now carry an interval
    rather than only the ones that were cheap.

    num, den: (n_traj,) per-trajectory means. For coverage, den is None and num
    is the per-trajectory hit rate.
    """
    n = len(num)
    idx = rng.integers(0, n, (n_boot, n))
    a = num[idx].mean(axis=1)
    v = a if den is None else a / den[idx].mean(axis=1)
    v = v[np.isfinite(v)]
    if len(v) < 2:
        return None, None, 0
    return float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5)), len(v)


def block(err, sig, rng=None):
    """
    err, sig: (n_traj, h, 45). Everything is pooled over the last two axes for the
    point estimate and resampled over the FIRST for the interval -- M-27's unit.
    """
    e = err.reshape(-1, err.shape[-1]); s = sig.reshape(-1, sig.shape[-1])
    rec = {"mean_sigma": float(np.nanmean(s)), "mean_abs_err": float(np.nanmean(e)),
           "ratio_err_over_sigma": float(np.nanmean(e) / np.nanmean(s)),
           "coverage_pm1": float(np.nanmean(e <= s)),
           "coverage_pm2": float(np.nanmean(e <= 2 * s))}

    # A1 -- every ratio and every coverage in 5.2 now carries a 95% interval over
    # independent trajectories, which is the standard this paper declares for
    # itself in 2 and had not been applying to its own calibration tables.
    if rng is not None:
        ax = (1, 2)
        pe = np.nanmean(err, axis=ax)                       # (n_traj,)
        ps = np.nanmean(sig, axis=ax)
        p1 = np.nanmean(err <= sig, axis=ax)
        p2 = np.nanmean(err <= 2 * sig, axis=ax)
        n_traj = err.shape[0]
        for key, (a, b) in (("ratio_err_over_sigma", (pe, ps)),
                            ("coverage_pm1", (p1, None)),
                            ("coverage_pm2", (p2, None))):
            lo, hi, nb = cluster_ci_from_per_traj(a, b, rng)
            rec[f"{key}_ci"] = [lo, hi]
            rec[f"{key}_n_boot_finite"] = nb
        rec["bootstrap_unit"] = "whole trajectory (M-27)"
        rec["n_trajectories_resampled"] = int(n_traj)
    cors = []
    for d in range(e.shape[1]):
        sd, ed = s[:, d], e[:, d]
        m = np.isfinite(sd) & np.isfinite(ed)
        if m.sum() > 2 and sd[m].std() > 0 and ed[m].std() > 0:
            cors.append(float(np.corrcoef(sd[m], ed[m])[0, 1]))
    cors = np.array(cors)
    rec.update({"n_finite_corr": len(cors), "n_positive": int((cors > 0).sum()),
                "corr_mean": float(cors.mean()) if len(cors) else None})
    return rec


def main():
    rng = np.random.default_rng(0)
    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    data, ep = R.load_data(paths["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"),
                         verbose=False)
    allep = sorted(set(split["train_episodes"]) | set(split["holdout_episodes"]))
    starts = MET.non_overlapping_starts(ep, allep, LEN)
    n_ind = int(MET.n_independent(starts, LEN))
    n_traj = len(starts)

    sd = torch.load(paths["ckpt"], map_location="cpu")["system_dynamics_state_dict"]
    model = S.ReferenceRWM(sd); model.eval()
    idx = np.asarray(starts)[:, None] + np.arange(LEN)[None, :]
    raw = data[idx]
    st = torch.as_tensor(R.normalise_state(raw[:, :, R.STATE_COLS],
                                           cfg["state_data_mean"], cfg["state_data_std"]),
                         dtype=torch.float32)
    ac = torch.as_tensor(raw[:, :, R.ACTION_COLS], dtype=torch.float32)
    pred, alea, epi, alea_s, epi_s = model.rollout_uncertainty(st.clone(), ac, START,
                                                               action_offset=1)
    abs_err = (pred - st).abs().numpy().astype(np.float64)
    alea = alea.numpy().astype(np.float64)
    epi = epi.numpy().astype(np.float64)
    total = np.sqrt(alea ** 2 + epi ** 2)

    out = {"design": {"checkpoint": R.rel(paths["ckpt"]), "ensemble_size": model.ensemble,
                      "arena": "all ten episodes", "episodes": allep,
                      "trajectories": n_traj, "n_independent": n_ind,
                      "traj_len": LEN, "start_step": START, "action_offset": 1,
                      "n_boot": N_BOOT, "bootstrap_unit": "whole trajectory (M-27)",
                      "rationale": ("the released checkpoint trained on all ten episodes, so "
                                    "restricting it to the held-out pair buys no independence")},
           "d1_by_horizon": {}, "d2_forecast_index": {}, "d4_penalty": {}}

    print("D1 / D2 / D4 — RELEASED CHECKPOINT AT n_independent = %d" % n_ind)
    print("=" * 104)
    print(f"  {model.ensemble} members, episodes {allep}, {n_traj} non-overlapping "
          f"400-step trajectories\n")

    # ---------------- D1 ----------------
    print("  D1 — the uncertainty table, n_independent = %d, every cell with a "
          "95%% cluster-bootstrap interval (A1)" % n_ind)
    hdr = (f"  {'h':>4} {'quantity':<11} {'err/sigma [95% CI]':>30} "
           f"{'cov+-1s [95% CI]':>28} {'cov+-2s [95% CI]':>28} {'dims r>0':>10}")
    print(hdr); print("  " + "-" * (len(hdr) - 2))
    for h in HORIZONS:
        sl = slice(START, START + h)
        rec = {}
        for name, sig in (("aleatoric", alea[:, sl]), ("epistemic", epi[:, sl]),
                          ("total", total[:, sl])):
            b = block(abs_err[:, sl], sig, rng=np.random.default_rng(0))
            rec[name] = b
            rr, rc = b["ratio_err_over_sigma"], b["ratio_err_over_sigma_ci"]
            c1, c1c = b["coverage_pm1"], b["coverage_pm1_ci"]
            c2, c2c = b["coverage_pm2"], b["coverage_pm2_ci"]
            print(f"  {h:>4} {name:<11} "
                  f"{f'{rr:,.1f} [{rc[0]:,.1f}, {rc[1]:,.1f}]':>30} "
                  f"{f'{100*c1:.2f}% [{100*c1c[0]:.2f}, {100*c1c[1]:.2f}]':>28} "
                  f"{f'{100*c2:.2f}% [{100*c2c[0]:.2f}, {100*c2c[1]:.2f}]':>28} "
                  f"{b['n_positive']:>4}/{b['n_finite_corr']:<4}")
        out["d1_by_horizon"][str(h)] = rec
        print()

    # ---------------- D2 ----------------
    # Scalars per (trajectory, step): the trust metric is the summed epistemic
    # sigma, exactly what envs/base.py:166 applies. The counter is the step index.
    # The error is total absolute error, the quantity the follow-up says the trust
    # metric tracks.
    epi_scalar = epi_s.numpy().astype(np.float64)[:, START:]        # (n_traj, T)
    err_scalar = abs_err[:, START:].sum(-1)                         # (n_traj, T)
    T = err_scalar.shape[1]
    fidx = np.broadcast_to(np.arange(T, dtype=np.float64), err_scalar.shape).copy()

    print("  D2 — the forecast-index baseline the follow-up never ran")
    hdr2 = (f"  {'h':>5} {'r(index, |err|)':>26} {'r(epistemic, |err|)':>30} "
            f"{'partial r(epi,|err| . index)':>32} {'PAIRED diff [95% CI]':>26}")
    print(hdr2); print("  " + "-" * (len(hdr2) - 2))
    for h in list(HORIZONS) + ["all"]:
        k = T if h == "all" else min(h, T)
        E_, S_, F_ = err_scalar[:, :k], epi_scalar[:, :k], fidx[:, :k]
        r_idx, r_epi = pooled_corr(F_, E_), pooled_corr(S_, E_)
        r_par = partial_corr(S_, E_, F_)
        ci = {}
        for nm, fn in (("index", lambda i: pooled_corr(F_[i], E_[i])),
                       ("epistemic", lambda i: pooled_corr(S_[i], E_[i])),
                       ("partial", lambda i: partial_corr(S_[i], E_[i], F_[i]))):
            lo, hi, nb = cluster_boot(fn, n_traj, np.random.default_rng(0))
            ci[nm] = {"lo": lo, "hi": hi, "n_boot_finite": nb}
        # PAIRED difference, resampling whole trajectories and recomputing BOTH
        # correlations inside each draw. Two marginal intervals overlapping is not
        # evidence of no difference when both are measured on the same
        # trajectories -- the draws are correlated, and the paired test is both
        # correct for this design and more powerful. The marginal intervals
        # overlap at h=128; this is the test that decides whether that matters.
        def _pair(i):
            a, b = pooled_corr(S_[i], E_[i]), pooled_corr(F_[i], E_[i])
            return None if (a is None or b is None) else a - b
        d_obs = (None if (r_epi is None or r_idx is None) else r_epi - r_idx)
        d_lo, d_hi, d_nb = cluster_boot(_pair, n_traj, np.random.default_rng(0))
        rec = {"horizon": h, "n_steps": int(k), "n_independent": n_ind,
               "r_index": r_idx, "r_epistemic": r_epi, "r_partial": r_par,
               "ci": ci,
               "marginal_ci_overlap": (
                   None if r_idx is None else
                   not (ci["index"]["hi"] < ci["epistemic"]["lo"]
                        or ci["epistemic"]["hi"] < ci["index"]["lo"])),
               "paired_diff": d_obs, "paired_ci_lo": d_lo, "paired_ci_hi": d_hi,
               "paired_n_boot_finite": d_nb,
               "paired_excludes_zero": (d_lo is not None and d_lo > 0),
               "index_wins": (r_idx is not None and r_epi is not None
                              and abs(r_idx) >= abs(r_epi))}
        out["d2_forecast_index"][str(h)] = rec
        f = lambda v, c: (f"{v:+.3f} [{c['lo']:+.3f}, {c['hi']:+.3f}]"
                          if v is not None and c['lo'] is not None else "n/a")
        pd_ = ("n/a" if d_obs is None else
               f"{d_obs:+.3f} [{d_lo:+.3f}, {d_hi:+.3f}]")
        print(f"  {str(h):>5} {f(r_idx, ci['index']):>26} {f(r_epi, ci['epistemic']):>30} "
              f"{f(r_par, ci['partial']):>32} {pd_:>26}"
              + ("   OVERLAP" if rec["marginal_ci_overlap"] else "")
              + ("   <-- COUNTER WINS" if rec["index_wins"] else ""))
    print()

    # ---------------- D4 ----------------
    r_pen = pooled_corr(epi_scalar, err_scalar)
    lo, hi, nb = cluster_boot(lambda i: pooled_corr(epi_scalar[i], err_scalar[i]),
                              n_traj, np.random.default_rng(0))
    out["d4_penalty"] = {
        "definition": "means.std(0).sum(-1)  (system_dynamics.py:126)",
        "applied_at": "envs/base.py:166  rewards += uncertainty_penalty_weight * epistemic * dt",
        "corr_with_total_abs_error": r_pen,
        "ci_lo": lo, "ci_hi": hi, "n_boot_finite": nb,
        "n_independent": n_ind, "n_trajectories": n_traj,
        "n_points": int(np.isfinite(epi_scalar).sum()),
        "bootstrap_unit": "whole trajectory",
        "note": ("section 5.2 previously quoted this correlation with no interval and no n. "
                 "The interval is a cluster bootstrap over whole trajectories; pooling "
                 "trajectory x step pairs would narrow it by about sqrt(T) (M-27).")}
    print("  D4 — the scalar penalty actually applied, against total absolute error")
    print(f"      r = {r_pen:+.3f}   95% CI [{lo:+.3f}, {hi:+.3f}]   "
          f"n_independent = {n_ind}   trajectories = {n_traj}   points = {out['d4_penalty']['n_points']:,}")

    op = os.path.join(R.RESULTS, "task_d_nind20.json")
    json.dump(out, open(op, "w"), indent=2)
    print(f"\n  wrote {R.rel(op)}")


if __name__ == "__main__":
    main()
