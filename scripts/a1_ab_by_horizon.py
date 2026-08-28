"""
A1 -- the autoregressive-versus-teacher-forcing result at EVERY horizon.

WHY THIS EXISTS. §3.1 states that h=368 is the upstream's open-loop diagnostic
length and explicitly not a deployment horizon, and §5 then led with a result
measured there. The same comparison at h=100 -- the method's own imagination
rollout length, which everything in §6 is anchored to -- is 2.58x rather than
4.61x. Reported as a line item beside the headline, that reads like horizon
shopping. Reported as a curve it is a finding: the advantage GROWS with horizon,
h=8's gap spans zero, and h=368 is the end of a trend rather than a point
someone picked.

WHAT IT COMPUTES, all on the SAME rollouts, out-of-sample, three seeds:

  ratio B/A            the headline, per horizon
  gap and interval     Arm B minus Arm A per trajectory, 95% cluster bootstrap
                       over whole trajectories (M-27) on the n_independent = 4
                       the held-out arena actually has
  hold-last floor      predicting that nothing changes, per horizon. §5's
                       sharpest line is that teacher forcing is WORSE than this,
                       and that line was only ever checked at h=368
  A over floor         Arm A's margin over the same baseline
  sign test            per-episode gap over all ten episodes, exact two-sided
                       binomial, per horizon. §5 quotes 10 of 10 at h=368 and
                       the abstract leans on it; the count at h=100 was unknown

WHAT IT DOES NOT DO. It does not touch M-23. That rule is stated over h=368, was
committed before the data, and its verdict stands as returned. Everything here at
any other horizon was computed after the data existed and carries none of a
pre-registration's weight -- the same distinction §6.7 draws about the
counter-baseline expectation, and it is drawn in §5 in the same words.

Writes results/a1_ab_by_horizon.json.
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

START = E.START_STEP
LEN = 400
SEEDS = (0, 1, 2)
ARMS = ("A", "B")
N_BOOT = 20000
BOOT_SEED = 0          # fixed, so the intervals are reproducible bitwise


def horizons():
    """The reporting grid, from V2 and the n=20 table rather than typed here."""
    D = json.load(open(os.path.join(R.RESULTS, "task_d_nind20.json")))
    return sorted(int(h) for h in D["d1_by_horizon"])


def rel_l1_per_traj(model, starts, hs):
    """Relative-L1 per trajectory at each horizon, the reference's own metric.

    `model=None` is the hold-last floor: hold the last teacher-forced state for
    the whole rollout, which is the prediction that nothing changes.
    """
    idx = np.asarray(starts)[:, None] + np.arange(LEN)[None, :]
    raw = R.DATA[idx]
    st = torch.as_tensor(R.normalise_state(raw[:, :, R.STATE_COLS],
                                           R.CFG["state_data_mean"], R.CFG["state_data_std"]),
                         dtype=torch.float32)
    ac = torch.as_tensor(raw[:, :, R.ACTION_COLS], dtype=torch.float32)
    if model is None:
        p = st.clone()
        p[:, START:] = st[:, START - 1:START].expand(-1, LEN - START, -1)
    else:
        p = model.rollout(st.clone(), ac, START, action_offset=1)
    out = {}
    for h in hs:
        nu = (p[:, START:START + h] - st[:, START:START + h]).abs().sum(-1)
        de = st[:, START:START + h].abs().sum(-1)
        out[h] = (nu / de).mean(1).numpy()          # one value per trajectory
    return out


def sign_p(k, n):
    """Exact two-sided binomial P for k of n, matching task_c3_multiplicity.py."""
    tail = lambda x: sum(comb(n, i) for i in range(x, n + 1)) / 2 ** n
    return float(min(1.0, 2 * min(tail(k), 1 - tail(k) + comb(n, k) / 2 ** n)))


def main():
    paths = R.repo_paths()
    R.CFG = R.load_reference_config(paths["lite"])
    R.DATA, ep = R.load_data(paths["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"),
                         verbose=False)
    oos = list(split["holdout_episodes"])
    hs = horizons()

    models = {}
    for a in ARMS:
        for s in SEEDS:
            w = f"runs/arm{a}_seed{s}_10k/weights_10000.pt"
            assert os.path.exists(w), f"missing {w}"
            m = M.build_from_config(R.CFG, ensemble_size=1)
            m.load_state_dict(torch.load(w, map_location="cpu")["model_state_dict"], strict=True)
            m.eval()
            models[(a, s)] = m

    # ---- out-of-sample: effect size, interval, floor -----------------------
    starts = MET.non_overlapping_starts(ep, oos, LEN)
    n_ind = int(MET.n_independent(starts, LEN))
    per = {(a, s): rel_l1_per_traj(models[(a, s)], starts, hs) for a in ARMS for s in SEEDS}
    floor = rel_l1_per_traj(None, starts, hs)

    rng = np.random.default_rng(BOOT_SEED)
    # One index draw per bootstrap replicate, SHARED across arms and horizons:
    # the two arms are scored on the same trajectories, so resampling them
    # together is the paired comparison and resampling them apart is not.
    draws = rng.integers(0, len(starts), size=(N_BOOT, len(starts)))

    by_h = {}
    for h in hs:
        A = np.stack([per[("A", s)][h] for s in SEEDS])     # (seeds, traj)
        B = np.stack([per[("B", s)][h] for s in SEEDS])
        a_mean = A.mean(1)                                   # per seed
        b_mean = B.mean(1)
        # Seeds are pooled INSIDE each draw rather than resampled: seeds are not
        # trajectories (M-27). The resampling unit is the whole trajectory.
        gap_traj = B.mean(0) - A.mean(0)                     # per trajectory
        boots = gap_traj[draws].mean(1)
        lo, hi = np.percentile(boots, [2.5, 97.5])
        by_h[str(h)] = {
            "horizon": h,
            "n_independent": n_ind,
            "n_trajectories": len(starts),
            "A": {"per_seed": {str(s): float(a_mean[i]) for i, s in enumerate(SEEDS)},
                  "mean": float(a_mean.mean()),
                  "sd_ddof1": float(a_mean.std(ddof=1))},
            "B": {"per_seed": {str(s): float(b_mean[i]) for i, s in enumerate(SEEDS)},
                  "mean": float(b_mean.mean()),
                  "sd_ddof1": float(b_mean.std(ddof=1))},
            "ratio_B_over_A": float(b_mean.mean() / a_mean.mean()),
            "gap": float(gap_traj.mean()),
            "gap_ci": [float(lo), float(hi)],
            "gap_excludes_zero": bool(lo > 0 or hi < 0),
            "floor": float(floor[h].mean()),
            "floor_over_A": float(floor[h].mean() / a_mean.mean()),
            "B_over_floor": float(b_mean.mean() / floor[h].mean()),
            "B_worse_than_floor": bool(b_mean.mean() > floor[h].mean()),
        }

    # ---- the sign test, over all ten episodes -----------------------------
    # Per EPISODE, not per trajectory: episodes are genuinely separable units,
    # which is what makes a binomial null admissible here and inadmissible for
    # the 45 coupled state dimensions of §6.6.
    all_eps = sorted(set(split["train_episodes"]) | set(split["holdout_episodes"]))
    sign = {}
    for h in hs:
        pos, per_ep = 0, {}
        for e in all_eps:
            st_e = MET.non_overlapping_starts(ep, [e], LEN)
            if not len(st_e):
                continue
            a = np.mean([rel_l1_per_traj(models[("A", s)], st_e, [h])[h].mean() for s in SEEDS])
            b = np.mean([rel_l1_per_traj(models[("B", s)], st_e, [h])[h].mean() for s in SEEDS])
            per_ep[str(e)] = float(b - a)
            pos += (b - a) > 0
        sign[str(h)] = {"n_episodes": len(per_ep), "n_positive": int(pos),
                        "exact_two_sided_p": sign_p(int(pos), len(per_ep)),
                        "per_episode_gap": per_ep}

    trend = [by_h[str(h)]["ratio_B_over_A"] for h in hs]
    out = {
        "design": {
            "arena": "out-of-sample held-out pair",
            "episodes": oos,
            "n_independent": n_ind,
            "n_trajectories": len(starts),
            "traj_len": LEN,
            "seeds": list(SEEDS),
            "checkpoint": "weights_10000.pt",
            "metric": "relative-L1, the reference's own (model_training.py:203)",
            "bootstrap_unit": "whole trajectory (M-27); seeds pooled inside each draw",
            "n_boot": N_BOOT,
            "horizons": hs,
        },
        "prereg_note": (
            "M-23 is stated over h=368 and its verdict stands as returned there. Every other "
            "horizon in this file was computed after the data existed and carries none of a "
            "pre-registration's weight -- the same standard 6.7 applies to the counter-baseline "
            "expectation."),
        "by_horizon": by_h,
        "sign_test": sign,
        "trend": {
            "ratios": {str(h): by_h[str(h)]["ratio_B_over_A"] for h in hs},
            "monotone_increasing": bool(all(x < y for x, y in zip(trend, trend[1:]))),
            "reading": ("the advantage grows with forecast horizon; h=368 is the end of a trend "
                        "rather than a selected point, and h=8 -- the horizon the model is "
                        "trained on -- is where it is not established"),
            "n_excluding_zero": sum(1 for h in hs if by_h[str(h)]["gap_excludes_zero"]),
            "n_horizons": len(hs),
            "excludes_zero_at": [h for h in hs if by_h[str(h)]["gap_excludes_zero"]],
            "spans_zero_at": [h for h in hs if not by_h[str(h)]["gap_excludes_zero"]],
        },
    }
    op = os.path.join(R.RESULTS, "a1_ab_by_horizon.json")
    json.dump(out, open(op, "w"), indent=2)

    print("A1 — THE A/B RESULT ACROSS THE HORIZON GRID")
    print("=" * 104)
    print(f"  out-of-sample, {len(SEEDS)} seeds, n_independent = {n_ind}, "
          f"{N_BOOT:,} cluster-bootstrap draws over whole trajectories\n")
    print(f"  {'h':>5} {'Arm A':>16} {'Arm B':>16} {'B/A':>7} {'gap':>9} "
          f"{'95% CI':>20} {'excl 0':>7} {'floor':>8} {'A/floor':>8} {'B/floor':>8} {'sign':>7}")
    for h in hs:
        r = by_h[str(h)]
        g = sign[str(h)]
        print(f"  {h:>5} {r['A']['mean']:>8.4f}±{r['A']['sd_ddof1']:<7.4f} "
              f"{r['B']['mean']:>8.4f}±{r['B']['sd_ddof1']:<7.4f} "
              f"{r['ratio_B_over_A']:>6.2f}x {r['gap']:>+9.4f} "
              f"[{r['gap_ci'][0]:>+8.4f},{r['gap_ci'][1]:>+8.4f}] "
              f"{'yes' if r['gap_excludes_zero'] else 'NO':>7} "
              f"{r['floor']:>8.4f} {r['floor_over_A']:>7.1f}x {r['B_over_floor']:>7.2f}x "
              f"{g['n_positive']:>3}/{g['n_episodes']:<3}")
    t = out["trend"]
    print(f"\n  ratio is monotone increasing in horizon: {t['monotone_increasing']}")
    print(f"  gap excludes zero at {t['n_excluding_zero']} of {t['n_horizons']} horizons "
          f"(spans zero at {t['spans_zero_at'] or 'none'})")
    print(f"  teacher forcing is worse than the hold-last floor at: "
          f"{[h for h in hs if by_h[str(h)]['B_worse_than_floor']] or 'no horizon'}")
    print(f"\n  M-23 is stated over h=368 only. {R.rel(op)}")


if __name__ == "__main__":
    main()
