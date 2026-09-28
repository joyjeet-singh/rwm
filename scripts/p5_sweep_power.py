"""
P5 -- what rule M-74 (the M/N configuration sweep) can detect, measured BEFORE any
sweep run exists.

WHY THIS EXISTS. M-43 was committed without a power check and returned a verdict it
could not have returned otherwise; the standing rule since M-44 is that no new rule
enters git without its minimum detectable effect in its own text. This script is that
estimate for the sweep, and it reads only runs that already exist.

WHAT THE RULE WILL FACE. Each non-centre configuration c is compared with the centre
(M, N) = (32, 8) through

    D_c = mean over the 4 held-out trajectories of
          [ 3-seed mean err_c(traj) - 3-seed mean err_centre(traj) ]

at the anchor horizon, with a cluster bootstrap over whole trajectories (seeds pooled
inside each draw, never resampled -- M-27) and Holm's correction across the
configurations of the grid. At n_independent = 4 the bootstrap has exactly
4**4 = 256 equally likely ordered resamples, so it is evaluated EXACTLY here, as the
verdict script will evaluate it: no Monte Carlo, no seed.

WHAT IS ESTIMATED, and by what. Two estimates, in the two forms the earlier power
checks used (scripts/p1_power_check.py for M-44 and M-45):

  MDE, formula   M-44's: (z_(1-a/2) + z_.80) x the cluster-bootstrap SE of the
                 statistic under the SAME-configuration null -- the three Arm A seed
                 pairs, their SE scaled by 1/sqrt(3) because the rule compares 3-seed
                 means, not single seeds. At a = .05 and at every Holm level.
  MDE, exact     a power curve by DILUTION, as P1 builds M-45's: a proportional effect
                 (configuration c is (1 + delta) x the centre on every trajectory) plus
                 the same null noise, N(0, sqrt(2/3) x the Arm A seed SD) per trajectory,
                 is diluted from +100% to zero and every point is scored with the rule's
                 own EXACT test at each Holm level. delta80 is the smallest effect
                 detected, in the right direction, in 80% of trials.

WHY NOT P1's CROSS-ARCHITECTURE CALIBRATION. P1 took a conservative SE from a real
contrast between two different models. The only real configuration contrast available
here is Arm B against Arm A, and it is enormous and uneven (+12.3 on one trajectory,
about +1 on the others, at h = 368): its SE measures the size of that effect, not the
noise a small effect must clear, and it would put the MDE above 1,000% of the centre's
error. At n = 4 the exact test turns on whether all four trajectories share a sign, which
a spread in MAGNITUDE does not prevent. So the Arm B contrast is reported instead as a
check that the exact test detects a real configuration change, and the spread-in-SIGN
limit is stated exactly (min_p_by_sign_pattern).

THE NUMBER THE RULE QUOTES is the larger of the two MDEs at Holm's first step: the
conservative one, because the design question is what the rule can NOT see.

CAUTIONS written into the artifact:
  * the sweep's common forecast windows are, for this grid (longest history 32),
    exactly these four held-out trajectories -- so the arena here is the arena the
    rule will face, not a proxy for it;
  * the noise model is estimated from three seeds (two degrees of freedom per
    trajectory) and assumes a new configuration's seed noise equals the centre's;
  * an effect that changes sign across trajectories cannot be detected at n = 4 at
    any size, only one of a consistent sign;
  * the MDE is for ONE configuration at the stated Holm level. A configuration tested
    after others have been rejected faces a looser level, and the artifact lists the
    MDE at every Holm step.

Reads the stored rollouts in cache/ (scripts/task1_calibration.py STORE_PER_TRIPLE=1);
no model is evaluated. Writes results/p5_sweep_power.json.
"""
import itertools
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402

import per_triple_cache as PTC  # noqa: E402
import rollout_eval as E  # noqa: E402
import rwm_data as R  # noqa: E402
import rwm_metrics as MET  # noqa: E402

OUT = "p5_sweep_power.json"
ARENA = "out-of-sample held-out pair"
UNIT = 400
HORIZONS = (1, 8, 32, 100, 128, 368)
ANCHOR_H = 368          # the original never states the horizon behind "e" (ORIGINAL_SPECS a.3)
REPORTED_H = 100        # reported beside the anchor, as M-23 did
SEEDS = (0, 1, 2)
CENTRE = "armA_faithful_mse"            # Arm A, (32, 8), 2,500 iterations
CROSS = "armB_teacher_forced"           # Arm B, same window, teacher-forced
ALPHA, POWER = 0.05, 0.80
Z80 = 0.8416212335729143
# The proportional effect is diluted from DELTA_MAX (+100%) to zero in half-point steps.
DELTAS = tuple(round(x, 4) for x in np.arange(0.0, 1.0001, 0.005))
N_TRIAL = 4000
TRIAL_SEED = 0          # fixed: the power curve is reproducible bitwise

# Rule M-74's grid, in pre-registered priority order (highest first). The original's
# one-factor neighbours of (32, 8) in its own Fig. 6 grid, ordered by how close the
# original printed each one's error to the centre's (ORIGINAL_SPECS a.1, a.5).
GRID = ((32, 32), (16, 8), (32, 16), (8, 8), (32, 2), (32, 1), (2, 8), (1, 8))


def z(q):
    """Standard-normal quantile without scipy: bisection on erf, exact to 1e-12."""
    from math import erf, sqrt
    lo, hi = -10.0, 10.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if 0.5 * (1 + erf(mid / sqrt(2))) < q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# ------------------------------------------------------------- the exact bootstrap
def resample_index(n):
    """All n**n equally likely ordered resamples of n trajectories."""
    return np.array(list(itertools.product(range(n), repeat=n)), dtype=np.int64)


def boot_dist(d):
    """Exact bootstrap distribution of the mean of per-trajectory values d."""
    d = np.asarray(d, dtype=np.float64)
    return d[resample_index(len(d))].mean(1)


def boot_p(d):
    """Two-sided exact-bootstrap p: 2 x the smaller tail mass at zero, capped at 1."""
    b = boot_dist(d)
    return float(min(1.0, 2 * min(np.mean(b <= 0), np.mean(b >= 0))))


def boot_se(d):
    """SD of the exact bootstrap distribution (it is the distribution, so ddof = 0)."""
    return float(boot_dist(d).std())


def boot_ci(d, level=0.95):
    """Percentile interval of the exact distribution (256 equal-weight points)."""
    b = np.sort(boot_dist(d))
    a = (1 - level) / 2
    return [float(np.quantile(b, a)), float(np.quantile(b, 1 - a))]


def holm_levels(m, alpha=ALPHA):
    """The per-step thresholds of Holm's step-down: alpha/m, alpha/(m-1), ..., alpha."""
    return [alpha / (m - k) for k in range(m)]


def formula_mde(se, a):
    return float((z(1 - a / 2) + Z80) * se)


def min_p_by_sign_pattern(n):
    """Smallest achievable two-sided p for k of n trajectories on the minority side.

    The minority can only pull the resampled mean across zero on draws made mostly of
    minority trajectories; the best case is when only the all-minority draws cross.
    """
    return {f"{n - k} of {n} share a sign": (0.0 if k == 0 else 2 * (k / n) ** n)
            for k in range(0, n // 2 + 1)}


# ------------------------------------------------------------- the data
def truth_and_scale():
    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    data, ep = R.load_data(paths["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"),
                         verbose=False)
    oos = list(split["holdout_episodes"])
    starts = MET.non_overlapping_starts(ep, oos, UNIT)
    n_ind = int(MET.n_independent(starts, UNIT))
    scale = MET.training_scale(data, ep, split["train_episodes"],
                               cfg["state_data_mean"], cfg["state_data_std"])
    stored = np.array(json.load(open(os.path.join(R.RESULTS, "step4_0a_results.json")))
                      ["nrmse_scale"])
    assert np.allclose(scale, stored), "nRMSE scale differs from the stored one"
    idx = np.asarray(starts)[:, None] + np.arange(UNIT)[None, :]
    st = R.normalise_state(data[idx][:, :, R.STATE_COLS],
                           cfg["state_data_mean"], cfg["state_data_std"]).astype(np.float32)
    truth = st[:, E.START_STEP:]
    return {"truth": truth, "den": np.abs(truth).sum(-1), "scale": scale,
            "starts": [int(s) for s in starts], "n_ind": n_ind, "episodes": oos}


def per_traj(slug, seeds, T):
    """(seeds, traj, horizons) relative-L1 and nRMSE (form 1), cumulative over 1..h."""
    l1 = np.zeros((len(seeds), len(T["starts"]), len(HORIZONS)))
    nr = np.zeros_like(l1)
    files = []
    for i, s in enumerate(seeds):
        mid = f"{slug}_seed{s}"
        arr, meta = PTC.read(mid, ARENA, UNIT)
        assert meta["arena"] == ARENA and meta["unit_length"] == UNIT
        assert meta["start_step"] == E.START_STEP, f"{mid}: start {meta['start_step']}"
        assert meta["episodes"] == T["episodes"], f"{mid}: episodes {meta['episodes']}"
        assert [int(x) for x in arr["traj_start_row"]] == T["starts"], f"{mid}: starts"
        assert meta["n_independent"] == T["n_ind"]
        assert meta["residual_sign_convention"] == "prediction minus truth"
        err = arr["err"]
        assert err.shape == T["truth"].shape, f"{mid}: {err.shape}"
        num = np.abs(err).sum(-1)
        sq = err.astype(np.float64) ** 2
        for j, h in enumerate(HORIZONS):
            l1[i, :, j] = (num[:, :h] / T["den"][:, :h]).mean(1)
            for t in range(err.shape[0]):
                nr[i, t, j] = MET.nrmse_pooled(sq[t:t + 1, :h], T["scale"])
        p = PTC.path_for(mid, ARENA, UNIT)
        files.append({"path": R.rel(p), "sha256": PTC.sha256(p)})
    return {"l1": l1, "nrmse": nr}, files


def cross_check_head_to_head(vals_centre, vals_cross):
    """The per-trajectory l1 must reproduce the head-to-head table's seed means."""
    h2h = json.load(open(os.path.join(R.RESULTS, "head_to_head_accuracy.json")))
    for key, v in (("armA", vals_centre), ("armB", vals_cross)):
        for h in h2h["horizons"]:
            j = HORIZONS.index(h)
            mine = float(v["l1"][:, :, j].mean())
            theirs = h2h["rows"][key]["cells"][str(h)]["l1"]
            assert abs(mine - theirs) < 1e-9, f"{key} h={h}: {mine} vs {theirs}"
    return "relative-L1 seed means reproduce results/head_to_head_accuracy.json to 1e-9"


# ------------------------------------------------------------- the estimates
def noise_model(x_centre, j):
    """Per-trajectory centre mean and the SD of a 3-seed-v-3-seed null contrast."""
    a = x_centre[:, :, j]                                     # (seeds, traj)
    k = len(a)
    return a.mean(0), a.std(0, ddof=1) * np.sqrt(2 / k)


def formula_null(x_centre, j, levels):
    """M-44's MDE on the same-configuration null: Arm A seed pairs, SE / sqrt(3)."""
    a = x_centre[:, :, j]
    pair_se = [boot_se(a[i] - a[k]) for i, k in itertools.combinations(range(len(a)), 2)]
    se = float(np.mean(pair_se) / np.sqrt(len(a)))
    return se, pair_se, {f"{lv:.6f}": formula_mde(se, lv) for lv in levels}


def effect_scan(mu, sd, levels):
    """Detection rate of the rule's EXACT test against a proportional effect.

    Configuration c is (1 + delta) x the centre on every trajectory, plus the
    same-configuration null noise: D_t = delta * mu_t + N(0, sd_t). delta is diluted
    from DELTA_MAX to zero. Detection = Holm-level rejection in the true direction.
    """
    rng = np.random.default_rng(TRIAL_SEED)
    eps = rng.standard_normal((N_TRIAL, len(mu))) * np.asarray(sd)
    idx = resample_index(len(mu))
    rows = []
    for delta in DELTAS:
        D = delta * np.asarray(mu)[None, :] + eps
        B = D[:, idx].mean(2)
        p = np.minimum(1.0, 2 * np.minimum((B <= 0).mean(1), (B >= 0).mean(1)))
        right = D.mean(1) > 0
        rows.append({"delta": delta, **{f"{lv:.6f}": float(np.mean((p <= lv) & right))
                                        for lv in levels}})
    return rows


def delta80(rows, lv):
    for r in rows:
        if r[f"{lv:.6f}"] >= POWER:
            return r["delta"]
    return None


def estimate(vals_centre, vals_cross, m, metric, h):
    j = HORIZONS.index(h)
    x_c, x_o = vals_centre[metric], vals_cross[metric]
    mu, sd = noise_model(x_c, j)
    ebar = float(mu.mean())
    levels = holm_levels(m)
    se, pair_se, fmde = formula_null(x_c, j, [ALPHA] + levels)
    scan = effect_scan(mu, sd, levels)
    d_obs = x_o[:, :, j].mean(0) - mu
    rec = {"metric": metric, "horizon": h, "centre_mean_err": ebar,
           "centre_per_traj": mu.tolist(), "null_sd_3v3_per_traj": sd.tolist(),
           "null_sd_over_centre_per_traj": (sd / mu).tolist(),
           "formula_null": {"se_3v3": se, "se_seed_pairs_1v1": pair_se,
                            "mde_abs_by_level": fmde,
                            "mde_pct_by_level": {k: 100 * v / ebar for k, v in fmde.items()}},
           "effect_scan": scan,
           "exact_mde_by_holm_step": [
               {"step": k + 1, "level": lv, "delta80_pct":
                None if delta80(scan, lv) is None else round(100 * delta80(scan, lv), 4)}
               for k, lv in enumerate(levels)],
           "observed_real_contrast": {
               "what": "Arm B (teacher-forced) minus Arm A, 3-seed means: a real change of "
                       "training configuration, scored by the rule's exact test",
               "per_traj": d_obs.tolist(), "mean": float(d_obs.mean()),
               "p_exact": boot_p(d_obs), "ci95_exact": boot_ci(d_obs),
               "n_positive": int((d_obs > 0).sum())}}
    ex1 = rec["exact_mde_by_holm_step"][0]["delta80_pct"]
    fo1 = rec["formula_null"]["mde_pct_by_level"][f"{levels[0]:.6f}"]
    assert ex1 is not None, f"{metric} h={h}: no delta up to {DELTAS[-1]} reaches 80%"
    rec["binding_mde_pct_of_centre"] = max(ex1, fo1)
    rec["binding_from"] = "exact test, proportional effect" if ex1 >= fo1 else "formula (M-44)"
    rec["binding_level"] = levels[0]
    return rec


def main():
    T = truth_and_scale()
    assert T["n_ind"] == 4, f"n_independent {T['n_ind']}, the rule is written for 4"
    vc, fc = per_traj(CENTRE, SEEDS, T)
    vo, fo = per_traj(CROSS, SEEDS, T)
    check = cross_check_head_to_head(vc, vo)
    m = len(GRID)
    print("=" * 100)
    print("P5 — WHAT RULE M-74 (THE M/N SWEEP) CAN DETECT, BEFORE ANY SWEEP RUN EXISTS")
    print("=" * 100)
    print(f"  arena        : {ARENA}, episodes {T['episodes']}, starts {T['starts']}, "
          f"n_independent = {T['n_ind']}")
    print(f"  grid (m = {m}): {', '.join(f'({a},{b})' for a, b in GRID)}")
    print(f"  Holm levels  : " + ", ".join(f"{a:.5f}" for a in holm_levels(m)))
    print(f"  {check}")
    est = {}
    for metric in ("l1", "nrmse"):
        for h in (ANCHOR_H, REPORTED_H):
            r = estimate(vc, vo, m, metric, h)
            est[f"{metric}_h{h}"] = r
            fp = r["formula_null"]["mde_pct_by_level"]
            print(f"\n  {metric} h={h}: centre {r['centre_mean_err']:.4f}, per traj "
                  f"{np.round(r['centre_per_traj'], 4).tolist()}, null SD/centre "
                  f"{np.round(r['null_sd_over_centre_per_traj'], 3).tolist()}")
            print(f"    formula (M-44) MDE, % of centre: a=.05 {fp[f'{ALPHA:.6f}']:.1f}; "
                  + "; ".join(f"Holm {k + 1} {fp[f'{lv:.6f}']:.1f}"
                              for k, lv in enumerate(holm_levels(m))))
            print("    exact-test MDE (delta80, %):     "
                  + "; ".join(f"Holm {x['step']} {x['delta80_pct']}"
                              for x in r["exact_mde_by_holm_step"]))
            o = r["observed_real_contrast"]
            print(f"    Arm B - Arm A (real contrast): mean {o['mean']:+.4f}, "
                  f"{o['n_positive']}/4 positive, exact p {o['p_exact']:.4f}")
            print(f"    BINDING: {r['binding_mde_pct_of_centre']:.1f}% of the centre's error "
                  f"({r['binding_from']}, Holm step 1, level {r['binding_level']:.5f})")
    out = {
        "purpose": "rule M-74 — the minimum detectable effect of D_c at the n it faces, "
                   "estimated before any sweep run exists",
        "method": {
            "statistic": "D_c = mean over 4 held-out trajectories of the 3-seed-mean error of "
                         "configuration c minus that of the centre (32, 8); seeds pooled inside "
                         "each draw",
            "bootstrap": "cluster bootstrap over whole trajectories, evaluated EXACTLY over all "
                         "4**4 = 256 equally likely ordered resamples",
            "p_value": "two-sided: 2 x min(P*(mean <= 0), P*(mean >= 0)), capped at 1",
            "mde_formula": "(z_(1-a/2) + z_.80) x exact-bootstrap SE under the same-"
                           "configuration null (Arm A seed pairs, SE / sqrt(3) for 3-seed "
                           "means) — M-44's method (scripts/p1_power_check.py)",
            "mde_exact": "dilution of a proportional effect: D_t = delta x centre_t + "
                         "N(0, sqrt(2/3) x Arm A seed SD_t), delta from 1.00 to 0 in steps of "
                         "0.005, scored by the rule's exact test at each Holm level; delta80 = "
                         "smallest delta detected in the right direction in >= 80% of "
                         f"{N_TRIAL} trials (generator seed {TRIAL_SEED})",
            "binding": "the larger of the formula and exact MDEs at Holm's first step",
            "why_no_cross_calibration": "the only real configuration contrast available (Arm B "
                                        "against Arm A) is enormous and uneven, so its SE "
                                        "measures that effect's size rather than the noise a "
                                        "small effect must clear; it is reported as a check "
                                        "that the exact test detects a real change",
        },
        "arena": ARENA, "episodes": T["episodes"], "traj_start_row": T["starts"],
        "n_independent": T["n_ind"], "unit_length": UNIT, "start_step": E.START_STEP,
        "horizons": list(HORIZONS), "anchor_horizon": ANCHOR_H, "reported_horizon": REPORTED_H,
        "centre": {"config": [32, 8], "cache_slug": CENTRE, "seeds": list(SEEDS),
                   "checkpoint": "weights_2500.pt"},
        "real_contrast_check": {"cache_slug": CROSS, "seeds": list(SEEDS),
                                "checkpoint": "weights_2500.pt"},
        "grid_priority_order": [list(g) for g in GRID], "m": m,
        "holm_levels": holm_levels(m),
        "n_resamples_exact": 4 ** 4,
        "min_p_by_sign_pattern": min_p_by_sign_pattern(4),
        "three_of_four_rejectable_at_holm_step": [
            k + 1 for k, a in enumerate(holm_levels(m)) if 2 * (1 / 4) ** 4 <= a],
        "input_check": check,
        "input_files": fc + fo,
        "per_traj": {"centre": {k: v.tolist() for k, v in vc.items()},
                     "cross": {k: v.tolist() for k, v in vo.items()}},
        "estimates": est,
        "cautions": [
            "the noise model rests on three seeds, two degrees of freedom per trajectory, "
            "and assumes a new configuration's seed noise equals the centre's",
            "the exact MDE is for an effect proportional to the centre's error on every "
            "trajectory; an effect of mixed sign across trajectories is not detectable at "
            "n = 4 at any size",
            "the MDE is quoted at Holm's first step, the strictest; a configuration tested "
            "after others are rejected faces a looser level (exact_mde_by_holm_step)",
            "at n = 4 a 3-of-4 sign pattern has two-sided p >= 2/256 = 0.0078, so it can be "
            "rejected only at a Holm step whose level is at least that",
        ],
    }
    json.dump(out, open(os.path.join(R.RESULTS, OUT), "w"), indent=2)
    print(f"\n  wrote results/{OUT}")


if __name__ == "__main__":
    main()
