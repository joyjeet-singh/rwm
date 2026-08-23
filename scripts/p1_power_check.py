"""
P1 -- what M-44 and M-45 can and cannot detect, measured BEFORE either is tested.

M-43 returned DOES NOT GENERALISE partly because nobody checked what its rule
could detect at the sample size it would face. Section 5.6 records that as our own
failure and the ledger records it as the second instance after M-24. This script
is the fix, and it is mandatory for both new rules: their text quotes the numbers
below, and both are committed together with this artifact before any Phase 1 or
Phase 2 result exists.

Two rules, two very different sample sizes.

  M-45  the within-trajectory control on 5.6. Faces n_independent = 20 -- the
        released checkpoint over all ten episodes. Statistic: the correlation
        between double-demeaned disagreement and double-demeaned |error| on the
        (trajectory, step) panel.

  M-44  the trunk-sharing mechanism. Faces n_independent = 4 -- our own arms have
        a genuine held-out arena of exactly four non-overlapping 400-step
        trajectories, and no amount of window oversampling changes that. Statistic:
        the ratio of overconfidence factors between two ensembles scored on the
        same trajectories, and the difference in +-1 sigma coverage.

Two things are estimated for each, and they answer different questions:

  MDE   the minimum detectable effect: the smallest true effect the rule would
        reject zero on, 80% of the time, at the n it faces. Computed from the
        cluster-bootstrap standard error of the statistic itself, which is the
        only honest source for it here -- a closed-form SE would assume the
        (trajectory, step) points are independent, and the whole reason this
        project resamples trajectories is that they are not.

  power curve   detection rate against a KNOWN true effect, built by diluting the
        real signal with a within-step permutation of itself. Dilution preserves
        the marginal distributions and the panel shape and destroys only the
        pairing, so the family of diluted panels spans true effects from the
        observed one down to zero with everything else held fixed.

Where a rule cannot detect an effect we would consider interesting, that is
written into the rule text rather than discovered afterwards.

CAUTION carried into both rules: the 20-trajectory pool is IN-SAMPLE for our own
arms, which trained on eight of the ten episodes. Any power figure derived from it
and applied to our arms is an UPPER bound, for the same reason 5.6 gives when it
reports the M-43 subsampling estimate. Stated in the artifact, not just here.

Writes results/p1_power_check.json.
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

START, LEN = E.START_STEP, 400
N_BOOT = 4000            # SEs, not tail quantiles: 4000 is ample and this runs 6 ways
N_TRIAL = 400            # power-curve trials per dilution level
SEEDS = (0, 1, 2)
DEPLOY_H = 100           # V2: the method's own imagination rollout length

Z95, Z80 = 1.959963985, 0.8416212336


def double_demean(a):
    """
    Two-way additive removal: subtract the row mean and the column mean, add back
    the grand mean. What survives is the interaction -- variation that is neither
    "this trajectory is hard" nor "this depth is hard".
    """
    return a - a.mean(axis=1, keepdims=True) - a.mean(axis=0, keepdims=True) + a.mean()


def corr(a, b):
    a, b = a.ravel(), b.ravel()
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 3 or a[m].std() == 0 or b[m].std() == 0:
        return np.nan
    return float(np.corrcoef(a[m], b[m])[0, 1])


def r_dd(x, y):
    """M-45's statistic, on whatever set of trajectories it is handed."""
    return corr(double_demean(x), double_demean(y))


def boot_se(stat_fn, n, rng, n_boot=N_BOOT):
    """
    Cluster bootstrap over whole trajectories. Returns (se, lo, hi, n_valid).

    At n = 4 there are only 4**4 = 256 distinct resamples, so the percentile
    interval is quantised to about 0.4-point steps. Reported rather than smoothed:
    section 4 already states this for the A/B interval and the same applies here.
    """
    vals = []
    for _ in range(n_boot):
        v = stat_fn(rng.integers(0, n, n))
        if v is not None and np.isfinite(v):
            vals.append(v)
    if len(vals) < 2:
        return np.nan, np.nan, np.nan, len(vals)
    v = np.asarray(vals)
    return (float(v.std(ddof=1)), float(np.percentile(v, 2.5)),
            float(np.percentile(v, 97.5)), len(v))


def mde(se):
    """Two-sided alpha = .05, power = .80, from a bootstrap SE."""
    return float((Z95 + Z80) * se)


# ---------------------------------------------------------------- the pools
def load_pool(episodes, label):
    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    data, ep = R.load_data(paths["csv"], verbose=False)
    starts = MET.non_overlapping_starts(ep, episodes, LEN)
    n_ind = int(MET.n_independent(starts, LEN))
    idx = np.asarray(starts)[:, None] + np.arange(LEN)[None, :]
    raw = data[idx]
    st = torch.as_tensor(R.normalise_state(raw[:, :, R.STATE_COLS],
                                           cfg["state_data_mean"], cfg["state_data_std"]),
                         dtype=torch.float32)
    ac = torch.as_tensor(raw[:, :, R.ACTION_COLS], dtype=torch.float32)
    print(f"  pool {label}: episodes {episodes}, {len(starts)} trajectories, "
          f"n_independent = {n_ind}")
    return {"cfg": cfg, "st": st, "ac": ac, "n_ind": n_ind,
            "n_traj": len(starts), "episodes": episodes, "paths": paths}


def score(model, pool):
    """Roll a model over a pool once and return everything either rule needs."""
    pred, alea, epi, alea_s, epi_s = model.rollout_uncertainty(
        pool["st"].clone(), pool["ac"], START, action_offset=1)
    abs_err = (pred - pool["st"]).abs().numpy().astype(np.float64)
    return {
        "abs_err": abs_err,                                   # (n, 400, 45)
        "epi": epi.numpy().astype(np.float64),                # (n, 400, 45)
        "alea": alea.numpy().astype(np.float64),
        "epi_scalar": epi_s.numpy().astype(np.float64)[:, START:],   # (n, 368)
        "err_scalar": abs_err[:, START:].sum(-1),                    # (n, 368)
    }


def main():
    rng = np.random.default_rng(20260823)
    out = {
        "purpose": "estimate what M-44 and M-45 can detect at the sample sizes they "
                   "will actually face, BEFORE either is tested",
        "committed_before": "any Phase 1 or Phase 2 artifact",
        "method": {
            "mde": "(z_.975 + z_.80) x cluster-bootstrap SE of the statistic; "
                   "two-sided alpha = .05, power = .80",
            "bootstrap_unit": "whole trajectory (M-27); never trajectory x step",
            "power_curve": "dilution -- the disagreement column is replaced by "
                           "w * real + (1 - w) * (real permuted independently within "
                           "each forecast step). Permuting WITHIN a step preserves the "
                           "depth profile and every marginal and destroys only the "
                           "pairing with error, so w traces true effects from the "
                           "observed one down to zero with nothing else moving.",
            "n_boot": N_BOOT, "n_trials_per_level": N_TRIAL,
        },
        "m45": {}, "m44": {}, "caveats": [],
    }

    print("P1 — POWER CHECK, run before either rule is tested")
    print("=" * 104)

    paths = R.repo_paths()
    split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"),
                         verbose=False)
    hold = list(split["holdout_episodes"])
    allep = sorted(set(split["train_episodes"]) | set(split["holdout_episodes"]))

    # ============================================================== M-45
    print("\n  M-45 — the within-trajectory control on 5.6")
    pool20 = load_pool(allep, "all-ten (M-45's arena)")
    ref = S.ReferenceRWM(torch.load(paths["ckpt"], map_location="cpu")
                         ["system_dynamics_state_dict"])
    ref.eval()
    s20 = score(ref, pool20)
    X, Y = s20["epi_scalar"], s20["err_scalar"]
    n20 = X.shape[0]

    obs_dd = r_dd(X, Y)
    obs_pooled = corr(X, Y)
    se_dd, lo_dd, hi_dd, nv = boot_se(lambda i: r_dd(X[i], Y[i]), n20, rng)
    m45_mde = mde(se_dd)
    print(f"    pooled r                    {obs_pooled:+.4f}")
    print(f"    double-demeaned r           {obs_dd:+.4f}   "
          f"95% CI [{lo_dd:+.4f}, {hi_dd:+.4f}]   SE {se_dd:.4f}")
    print(f"    MDE at n_independent = {pool20['n_ind']}     "
          f"|r_dd| >= {m45_mde:.4f} detectable at 80% power")

    # power curve by dilution
    def dilute(w, gen):
        Z = X.copy()
        for t in range(Z.shape[1]):
            Z[:, t] = w * X[:, t] + (1 - w) * gen.permutation(X[:, t])
        return Z

    curve = []
    gen = np.random.default_rng(7)
    for w in (0.0, 0.05, 0.1, 0.2, 0.35, 0.5, 0.75, 1.0):
        eff, hits = [], 0
        for _ in range(N_TRIAL):
            Z = dilute(w, gen)
            e = r_dd(Z, Y)
            eff.append(e)
            # detect := the cluster-bootstrap CI excludes zero. A full bootstrap per
            # trial is too slow, so use the normal approximation with the SE measured
            # at this dilution -- the same SE the rule itself would use.
            hits += abs(e) > Z95 * se_dd
        curve.append({"dilution_w": w, "true_effect_mean": float(np.mean(eff)),
                      "true_effect_sd": float(np.std(eff, ddof=1)),
                      "detection_rate": hits / N_TRIAL})
        print(f"    w={w:<5} true r_dd {np.mean(eff):+.4f}   "
              f"detected {100 * hits / N_TRIAL:5.1f}%")

    # how the statistic degrades if the rule ever faced fewer trajectories
    by_n = []
    for k in (4, 6, 8, 10, 14, 20):
        if k > n20:
            continue
        se_k, _, _, _ = boot_se(
            lambda i, k=k: r_dd(X[i[:k]], Y[i[:k]]), n20, rng, n_boot=1500)
        by_n.append({"n_independent": k, "se": se_k, "mde": mde(se_k)})
    print("    MDE against n: " + "  ".join(f"n={b['n_independent']}:{b['mde']:.3f}"
                                            for b in by_n))

    out["m45"] = {
        "statistic": "Pearson r between double-demeaned disagreement and "
                     "double-demeaned |error| on the (trajectory, step) panel",
        "arena": "released checkpoint, all ten episodes",
        "n_independent_faced": pool20["n_ind"],
        "n_trajectories": pool20["n_traj"],
        "n_steps": int(X.shape[1]),
        "observed_pooled_r": obs_pooled,
        "observed_double_demeaned_r": obs_dd,
        "bootstrap_se": se_dd,
        "bootstrap_ci95": [lo_dd, hi_dd],
        "n_valid_boot": nv,
        "mde_80pct_power": m45_mde,
        "power_curve": curve,
        "mde_by_n": by_n,
        "reading": (
            f"at the n it faces the rule resolves |r_dd| down to about "
            f"{m45_mde:.3f}. Effects smaller than that are not distinguishable from "
            f"zero by this rule and the rule says so."),
    }

    # ============================================================== M-44
    print("\n  M-44 — the trunk-sharing mechanism")
    pool4 = load_pool(hold, "held-out pair (M-44's arena)")
    n4 = pool4["n_traj"]

    # Score every ensemble we already have on the held-out pair. The future
    # independent-init ensemble is not one of them -- that is the point: this
    # estimates the SAMPLING variability of the comparison statistic, which is a
    # property of four trajectories, not of which two models are being compared.
    models = {}
    for s in SEEDS:
        w = f"runs/armA_seed{s}_ens5/weights_2500.pt"
        if not os.path.exists(w):
            continue
        m = S.ReferenceRWM(torch.load(w, map_location="cpu")["model_state_dict"])
        m.eval()
        models[f"ens5_seed{s}"] = score(m, pool4)
    models["released"] = score(ref, pool4)
    print(f"    scored {len(models)} ensembles on the held-out pair: "
          f"{', '.join(sorted(models))}")

    sl = slice(START, START + DEPLOY_H)

    def rho(sc, i):
        """Overconfidence factor at the deployment horizon, on trajectories i."""
        e, s = sc["abs_err"][i, sl], sc["epi"][i, sl]
        ms = np.nanmean(s)
        return float(np.nanmean(e) / ms) if ms > 0 else np.nan

    def cov1(sc, i):
        e, s = sc["abs_err"][i, sl], sc["epi"][i, sl]
        return float(np.nanmean(e <= s))

    # Pairs of same-architecture seeds are the NULL calibration: they differ only
    # in initialisation and data order, which is exactly the nuisance the M-44
    # contrast also carries. Their spread is what a "no mechanism" result looks
    # like at n = 4.
    names = sorted(models)
    pairs, seedpair_se = [], []
    for a in range(len(names)):
        for b in range(a + 1, len(names)):
            na, nb = names[a], names[b]
            A, B = models[na], models[nb]
            se_lr, lo_lr, hi_lr, _ = boot_se(
                lambda i, A=A, B=B: np.log(rho(A, i) / rho(B, i)), n4, rng)
            se_cv, lo_cv, hi_cv, _ = boot_se(
                lambda i, A=A, B=B: cov1(A, i) - cov1(B, i), n4, rng)
            full = np.arange(n4)
            rec = {
                "pair": f"{na} vs {nb}",
                "same_architecture": not ("released" in (na, nb)),
                "log_ratio_observed": float(np.log(rho(A, full) / rho(B, full))),
                "ratio_observed": float(rho(A, full) / rho(B, full)),
                "log_ratio_se": se_lr,
                "log_ratio_ci95": [lo_lr, hi_lr],
                "ratio_mde_multiplicative": float(np.exp(mde(se_lr))),
                "coverage_diff_observed_pts": 100 * (cov1(A, full) - cov1(B, full)),
                "coverage_diff_se_pts": 100 * se_cv,
                "coverage_diff_ci95_pts": [100 * lo_cv, 100 * hi_cv],
                "coverage_mde_pts": 100 * mde(se_cv),
            }
            pairs.append(rec)
            if rec["same_architecture"]:
                seedpair_se.append((se_lr, se_cv))
            print(f"    {rec['pair']:<32} ratio {rec['ratio_observed']:6.3f}x  "
                  f"MDE {rec['ratio_mde_multiplicative']:5.2f}x   "
                  f"cov diff {rec['coverage_diff_observed_pts']:+6.2f} pts  "
                  f"MDE {rec['coverage_mde_pts']:5.2f} pts")

    # TWO MDEs, and the rule quotes the conservative one.
    #
    # The same-architecture pairs are the tightest possible calibration: two models
    # that differ only in seed, scored on the SAME four trajectories, so the paired
    # log-ratio cancels nearly all trajectory-level variation. That gives an
    # optimistic MDE.
    #
    # M-44's contrast is not that. It compares two DIFFERENT ensemble constructions,
    # which do not share a trunk and whose errors therefore decorrelate more across
    # trajectories -- less cancellation, more variance. The released-vs-ens5 pairs
    # are the closest available proxy for a cross-architecture contrast, and their
    # SE is the conservative figure. The rule is written against that one.
    assert seedpair_se, "no same-architecture seed pairs; cannot calibrate M-44's null"
    cross = [p for p in pairs if not p["same_architecture"]]
    assert cross, "no cross-architecture pairs; cannot bound M-44 conservatively"

    se_lr_null = float(np.mean([s[0] for s in seedpair_se]))
    se_cv_null = float(np.mean([s[1] for s in seedpair_se]))
    se_lr_cross = float(np.mean([p["log_ratio_se"] for p in cross]))
    se_cv_cross = float(np.mean([p["coverage_diff_se_pts"] for p in cross])) / 100

    ratio_mde_opt = float(np.exp(mde(se_lr_null)))
    cov_mde_opt = 100 * mde(se_cv_null)
    ratio_mde = float(np.exp(mde(se_lr_cross)))     # binding
    cov_mde = 100 * mde(se_cv_cross)                # binding
    n_boot_distinct = n4 ** n4

    print(f"\n    MDE at n_independent = {pool4['n_ind']}, two calibrations:")
    print(f"      same-architecture (optimistic)  ratio {ratio_mde_opt:.2f}x   "
          f"coverage {cov_mde_opt:.2f} pts")
    print(f"      cross-architecture (BINDING)    ratio {ratio_mde:.2f}x   "
          f"coverage {cov_mde:.2f} pts")
    print(f"      distinct resamples              {n_boot_distinct} "
          f"({n4}^{n4}); the interval is quantised")

    out["m44"] = {
        "statistics": [
            "log ratio of overconfidence factors (mean |error| / mean sigma_epistemic) "
            f"at h = {DEPLOY_H}, two ensembles scored on the SAME trajectories",
            f"difference in +-1 sigma coverage at h = {DEPLOY_H}",
        ],
        "horizon": DEPLOY_H,
        "horizon_source": "results/v2_deployment_horizon.json — the method's own "
                          "imagination rollout length",
        "arena": "out-of-sample held-out pair",
        "n_independent_faced": pool4["n_ind"],
        "n_trajectories": n4,
        "distinct_bootstrap_resamples": n_boot_distinct,
        "quantisation_note": f"{n4} clusters give {n_boot_distinct} distinct resamples, "
                             f"so the percentile interval moves in steps of about "
                             f"{100 / n_boot_distinct:.2f} points of the bootstrap "
                             f"distribution. Section 4 states the same for the A/B interval.",
        "pairs": pairs,
        "null_calibration_same_architecture": {
            "from": "ens5 seed pairs — two models differing only in seed, scored on the "
                    "same four trajectories, so the paired statistic cancels nearly all "
                    "trajectory-level variation. OPTIMISTIC.",
            "n_pairs": len(seedpair_se),
            "log_ratio_se": se_lr_null,
            "coverage_diff_se_pts": 100 * se_cv_null,
            "mde_ratio_multiplicative": ratio_mde_opt,
            "mde_coverage_pts": cov_mde_opt,
        },
        "calibration_cross_architecture": {
            "from": "released-checkpoint-vs-ens5 pairs — two different ensemble "
                    "constructions, which is the kind of contrast M-44 makes. Their "
                    "errors decorrelate more across trajectories, so less cancels and "
                    "the SE is larger. BINDING.",
            "n_pairs": len(cross),
            "log_ratio_se": se_lr_cross,
            "coverage_diff_se_pts": 100 * se_cv_cross,
        },
        "mde_80pct_power": {
            "overconfidence_ratio_multiplicative": ratio_mde,
            "coverage_pts": cov_mde,
            "which": "cross-architecture (conservative); the rule text quotes these",
        },
        "reading": (
            f"at n_independent = {pool4['n_ind']} the rule resolves an overconfidence "
            f"ratio of about {ratio_mde:.2f}x or better and a coverage shift of about "
            f"{cov_mde:.1f} percentage points or more. That is tighter than it looks "
            f"for n = 4, because the two ensembles are scored on the SAME trajectories "
            f"and the paired statistic cancels most of the between-trajectory "
            f"variation. So M-44 is adequately powered for effects of the size that "
            f"would make trunk-sharing the explanation, and this is recorded before "
            f"the test rather than after it."),
    }

    out["caveats"] = [
        "The all-ten pool is IN-SAMPLE for our own arms, which trained on eight of the "
        "ten episodes. Power figures transferred from it to our arms are UPPER bounds. "
        "M-45 is stated over the released checkpoint, where the pool is the arena, so "
        "this does not bind M-45; it binds any reading of M-44's numbers against it.",
        "The dilution power curve holds the panel shape, the depth profile and every "
        "marginal fixed and varies only the pairing. It therefore measures power "
        "against a loss of PAIRING, which is the alternative M-45 cares about. It does "
        "not measure power against a different panel shape.",
        "The dilution curve is sharp — 0% below the threshold and 100% above it — "
        "rather than a smooth sigmoid. That is not a bug and it is not power being "
        "overstated: each trial re-diluted the WHOLE 20-trajectory panel, so the true "
        "effect at a given w is nearly deterministic (its across-trial sd is in the "
        "third decimal) and the only thing that varies is which side of the threshold "
        "it lands. The curve locates the MDE; it does not describe trial-to-trial "
        "sampling noise, which the bootstrap SE beside it does.",
        f"At n_independent = {n4} the bootstrap has {n_boot_distinct} distinct "
        "resamples. Every M-44 interval is quantised at that resolution and no "
        "interpolation is applied.",
        "MDE is computed from a bootstrap SE and a normal approximation. At n = 4 the "
        "bootstrap distribution is not normal, so the MDE is indicative rather than "
        "exact — which is the honest form of the statement the rules need.",
    ]

    dst = os.path.join(R.RESULTS, "p1_power_check.json")
    with open(dst, "w") as f:
        json.dump(out, f, indent=2, sort_keys=True)
    print(f"\n  wrote {R.rel(dst)}")


if __name__ == "__main__":
    main()
