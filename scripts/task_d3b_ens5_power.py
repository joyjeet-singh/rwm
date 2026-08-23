"""D3b — the n=20 companion, and the power M-43's rule actually had at n=4.

M-43 returned DOES NOT GENERALISE. It failed on its second condition: the paired
difference excluded zero at 1 of 4 horizons, not a majority. Its FIRST condition
passed everywhere -- disagreement led the forecast index in 12 of 12
seed-horizon cells, every paired point estimate positive, +0.204 to +0.545.

That pattern -- direction replicating, separation failing -- is what a sample-size
limit looks like. Our own arms can only be scored out-of-sample on the held-out
pair, which is n_independent = 4, while section 5.6's finding was measured at
n_independent = 20. This quantifies the difference rather than asserting it.

Two things, neither of which governs M-43's verdict:

  COMPANION   the same measurement on all ten episodes (n_independent = 20), so
              the comparison with section 5.6 is like-for-like on sample size.
              This arena is IN-SAMPLE for our arms -- they trained on eight of
              the ten episodes -- and is reported as a companion for that reason,
              never as an out-of-sample result.

  POWER       the empirical power of M-43's criterion at n=4. Draw 4 trajectories
              at a time from the 20-trajectory pool, run the same paired bootstrap
              on each draw, and count how often the interval excludes zero. If
              that fraction is low for the effect size actually present, the rule
              could not have passed at n=4 whatever the model did, and saying so
              is not an excuse but a measurement.

Writes results/task_d3b_ens5_power.json.
"""
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import torch  # noqa: E402
import rwm_data as R  # noqa: E402
import rollout_eval as E  # noqa: E402
import rwm_metrics as MET  # noqa: E402
import score_reference as S  # noqa: E402

HORIZONS = (8, 32, 128, 368)
START, LEN, SEEDS = E.START_STEP, 400, (0, 1, 2)
N_BOOT, N_DRAWS, SUB_N = 4000, 400, 4


def pooled_corr(x, y):
    a, b = x.ravel(), y.ravel()
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 3 or a[m].std() == 0 or b[m].std() == 0:
        return None
    return float(np.corrcoef(a[m], b[m])[0, 1])


def _stats(x, y):
    """Per-trajectory sufficient statistics for a pooled Pearson correlation.

    n, sum x, sum y, sum x^2, sum y^2, sum xy are all ADDITIVE over trajectories,
    and a cluster bootstrap only ever sums whole trajectories. So a resample is a
    weighted sum of these six numbers per trajectory rather than a recomputation
    over every point in it. That is exact, not an approximation, and it turns the
    power analysis from hours into seconds.
    """
    return np.stack([np.full(x.shape[0], x.shape[1], float),
                     x.sum(1), y.sum(1), (x * x).sum(1), (y * y).sum(1), (x * y).sum(1)], 1)


def _corr_from(t):
    """t: (..., 6) summed sufficient statistics -> correlation, NaN where undefined."""
    n, sx, sy, sxx, syy, sxy = (t[..., i] for i in range(6))
    cov = n * sxy - sx * sy
    vx, vy = n * sxx - sx * sx, n * syy - sy * sy
    d = np.sqrt(np.where(vx > 0, vx, np.nan) * np.where(vy > 0, vy, np.nan))
    return cov / d


def paired_ci(dis, err, fi, rng, n_boot=N_BOOT):
    """Bootstrap CI on r(disagreement) - r(index), resampling whole trajectories."""
    n = dis.shape[0]
    sd, si = _stats(dis, err), _stats(fi, err)
    obs = float(_corr_from(sd.sum(0)) - _corr_from(si.sum(0)))
    if not np.isfinite(obs):
        return None, None, None
    counts = np.zeros((n_boot, n))
    draw = rng.integers(0, n, (n_boot, n))
    for k in range(n):
        counts[:, k] = (draw == k).sum(1)
    v = _corr_from(counts @ sd) - _corr_from(counts @ si)
    v = v[np.isfinite(v)]
    if v.size == 0:
        return obs, None, None
    return obs, float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))


def main():
    rng = np.random.default_rng(0)
    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    data, ep = R.load_data(paths["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"),
                         verbose=False)
    train, hold = sorted(split["train_episodes"]), sorted(split["holdout_episodes"])
    allep = sorted(set(train) | set(hold))
    starts = MET.non_overlapping_starts(ep, allep, LEN)
    n_ind, n_traj = int(MET.n_independent(starts, LEN)), len(starts)

    idx = np.asarray(starts)[:, None] + np.arange(LEN)[None, :]
    raw = data[idx]
    st = torch.as_tensor(R.normalise_state(raw[:, :, R.STATE_COLS],
                                           cfg["state_data_mean"], cfg["state_data_std"]),
                         dtype=torch.float32)
    ac = torch.as_tensor(raw[:, :, R.ACTION_COLS], dtype=torch.float32)

    print("D3b — n=20 COMPANION, AND THE POWER M-43's RULE HAD AT n=4")
    print("=" * 104)
    print(f"  all {len(allep)} episodes, n_independent = {n_ind}")
    print(f"  IN-SAMPLE for our arms: they trained on {len(train)} of {len(allep)} episodes "
          f"({train}).")
    print(f"  Companion only. M-43's verdict stands on the out-of-sample arena.\n")

    out = {"design": {"arena": "all-episodes", "episodes": allep,
                      "train_episodes": train, "holdout_episodes": hold,
                      "n_independent": n_ind, "n_trajectories": n_traj,
                      "in_sample_for_our_arms": True,
                      "governs_m43": False,
                      "n_boot": N_BOOT, "n_subsample_draws": N_DRAWS, "subsample_n": SUB_N},
           "companion": {}, "power": {}}

    RS = {}
    for s in SEEDS:
        sd = torch.load(f"runs/armA_seed{s}_ens5/weights_2500.pt",
                        map_location="cpu")["model_state_dict"]
        m = S.ReferenceRWM(sd); m.eval()
        pred, alea, epi, alea_s, epi_s = m.rollout_uncertainty(st.clone(), ac, START,
                                                               action_offset=1)
        RS[s] = {"err": (pred - st).abs().numpy().astype(np.float64),
                 "epi_s": epi_s.numpy().astype(np.float64)}
        print(f"  seed {s}: rolled out on {n_traj} trajectories")

    print(f"\n  COMPANION — the same table at n_independent = {n_ind} (in-sample)")
    hdr = f"    {'seed':>5}{'h':>6}{'r(index)':>12}{'r(disagr)':>12}{'paired diff [95% CI]':>28}"
    print(hdr); print("    " + "-" * (len(hdr) - 4))
    for h in HORIZONS:
        rows = []
        for s in SEEDS:
            err = RS[s]["err"][:, START:START + h].sum(-1)
            dis = RS[s]["epi_s"][:, START:START + h]
            T = err.shape[1]
            fi = np.broadcast_to(np.arange(T, dtype=np.float64), err.shape).copy()
            obs, lo, hi = paired_ci(dis, err, fi, np.random.default_rng(0))
            rows.append({"seed": s, "r_index": pooled_corr(fi, err),
                         "r_disagreement": pooled_corr(dis, err),
                         "paired_diff": obs, "ci_lo": lo, "ci_hi": hi,
                         "excludes_zero": bool(lo is not None and lo > 0)})
            print(f"    {s:>5}{h:>6}{rows[-1]['r_index']:>+12.3f}"
                  f"{rows[-1]['r_disagreement']:>+12.3f}"
                  f"{f'{obs:+.3f} [{lo:+.3f}, {hi:+.3f}]':>28}")
        out["companion"][str(h)] = {
            "per_seed": rows,
            "leads_all_seeds": all(r["r_disagreement"] > r["r_index"] for r in rows),
            "excludes_zero_all_seeds": all(r["excludes_zero"] for r in rows)}

    lead_all = all(v["leads_all_seeds"] for v in out["companion"].values())
    excl_n = sum(v["excludes_zero_all_seeds"] for v in out["companion"].values())
    out["companion_summary"] = {
        "leads_at_every_horizon": lead_all,
        "n_excluding_zero": excl_n, "n_horizons": len(HORIZONS),
        "would_have_passed_m43": bool(lead_all and excl_n > len(HORIZONS) / 2),
        "caveat": ("this arena is in-sample for our arms and therefore cannot discharge M-43, "
                   "which is stated over the out-of-sample arena")}
    print(f"\n    would this arena have satisfied M-43's two conditions? "
          f"{out['companion_summary']['would_have_passed_m43']} "
          f"(leads everywhere {lead_all}, excludes zero at {excl_n} of {len(HORIZONS)})")
    print("    -- recorded as a companion. It is in-sample and does not discharge M-43.")

    # ---- POWER ------------------------------------------------------------
    print(f"\n  POWER — how often M-43's criterion fires at n={SUB_N}, drawn from this pool")
    print(f"    {'h':>6}{'effect (n=20)':>16}{'fires at n=4':>16}{'of draws':>11}")
    for h in HORIZONS:
        s = SEEDS[0]
        err_f = RS[s]["err"][:, START:START + h].sum(-1)
        dis_f = RS[s]["epi_s"][:, START:START + h]
        T = err_f.shape[1]
        fi_f = np.broadcast_to(np.arange(T, dtype=np.float64), err_f.shape).copy()
        full, _, _ = paired_ci(dis_f, err_f, fi_f, np.random.default_rng(0))
        fires = 0
        for _ in range(N_DRAWS):
            sub = rng.choice(n_traj, SUB_N, replace=False)
            _, lo, _ = paired_ci(dis_f[sub], err_f[sub], fi_f[sub],
                                 np.random.default_rng(0), n_boot=1000)
            fires += bool(lo is not None and lo > 0)
        p = fires / N_DRAWS
        out["power"][str(h)] = {"effect_at_n20": full, "power_at_n4": p,
                                "n_draws": N_DRAWS, "subsample_n": SUB_N, "seed_used": s}
        print(f"    {h:>6}{full:>+16.3f}{100*p:>15.1f}%{N_DRAWS:>11}")

    mp = statistics.mean(v["power_at_n4"] for v in out["power"].values())
    worst_h = min(out["power"], key=lambda k: out["power"][k]["power_at_n4"])
    worst_p = out["power"][worst_h]["power_at_n4"]
    # The pool subsampled here is IN-SAMPLE, where the effect is larger than on
    # the held-out pair (+0.43..+0.79 against +0.20..+0.55). Power estimated at a
    # larger effect is an UPPER BOUND on the power the rule actually had, and
    # saying "the rule could not have passed" would overstate it in the other
    # direction. Both facts go in the artifact.
    oos = json.load(open(os.path.join(R.RESULTS, "task_d3_ens5.json")))["governing"]
    oos_eff = [r["paired_diff"] for h in HORIZONS for r in oos[str(h)]["per_seed"]]
    ins_eff = [v["effect_at_n20"] for v in out["power"].values()]
    out["power_summary"] = {
        "mean_power_at_n4": mp,
        "worst_horizon": int(worst_h), "worst_power": worst_p,
        "in_sample_effect_range": [min(ins_eff), max(ins_eff)],
        "out_of_sample_effect_range": [min(oos_eff), max(oos_eff)],
        "is_upper_bound": True,
        "statement": (
            f"At n_independent = {SUB_N}, M-43's paired-difference criterion fires on "
            f"{100*mp:.0f}% of draws on average and on only {100*worst_p:.0f}% at h={worst_h}. "
            f"That estimate is an UPPER BOUND on the power the rule actually had: it subsamples "
            f"a pool that is in-sample for these arms, where the effect is "
            f"{min(ins_eff):+.3f} to {max(ins_eff):+.3f}, against {min(oos_eff):+.3f} to "
            f"{max(oos_eff):+.3f} on the held-out pair the rule is stated over. So the rule was "
            f"under-powered at n=4 -- decisively at h={worst_h} -- and we do not claim it could "
            f"not have passed, only that it was committed without anyone checking what it could "
            f"detect.")}
    print(f"\n  mean power at n={SUB_N}: {100*mp:.1f}%   worst h={worst_h} at {100*worst_p:.1f}%")
    print(f"  in-sample effect {min(ins_eff):+.3f}..{max(ins_eff):+.3f}  vs  "
          f"out-of-sample {min(oos_eff):+.3f}..{max(oos_eff):+.3f}")
    print(f"  -> this power estimate is an UPPER BOUND (larger effect than the rule faces)")

    op = os.path.join(R.RESULTS, "task_d3b_ens5_power.json")
    json.dump(out, open(op, "w"), indent=2)
    print(f"\n  wrote {R.rel(op)}")


if __name__ == "__main__":
    main()
