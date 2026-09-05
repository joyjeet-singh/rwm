"""
P3 -- what M-68 can and cannot detect, measured BEFORE the combined arm exists.

M-24 records a pre-registered rule anchored without regard to the regime it would
be applied in. M-43 repeated the failure at a different axis: it was committed
without anyone computing what it could detect at n_independent = 4, and R-67 had
to estimate that AFTERWARDS, by subsampling four trajectories at a time from a
twenty-trajectory pool. P1 fixed the omission for M-44 and M-45. This script is
the same fix for M-68 -- the combined arm, five independently-initialised models
trained under gaussian_nll -- and it is run and committed BEFORE the two missing
training runs exist, so that a result near the threshold is read as near the
threshold rather than as a finding.

WHAT IS BEING ESTIMATED. Not the effect: the combined arm does not exist and
nothing here predicts it. What is estimated is the SAMPLING VARIABILITY of the
two statistics M-68 governs on, at each horizon in M-68's grid, at the
n_independent the rule will actually face. That variability is a property of the
arena, the horizon and the amount of cancellation the pairing buys -- not of
which arm is under test -- so it can be measured now from arms that exist.

THE METHOD IS M-43's, which is the method R-67 used and the one M-68's text
quotes. The all-ten-episode pool has twenty non-overlapping 400-step
trajectories. Draw four at a time -- the size of the genuine out-of-sample arena
-- and recompute the paired statistic on each draw. C(20,4) = 4,845 draws, so the
enumeration is EXHAUSTIVE: there is no Monte-Carlo error in the subsampling step
itself. The spread across draws is the sampling SE at n = 4.

  Finite-population correction. Sampling four of twenty WITHOUT replacement is
  tighter than sampling four from an unbounded population by the factor
  (N - n) / (N - 1) on the variance. The raw across-draw SD is therefore divided
  by sqrt(16/19) so that the SE, and the MDE built on it, describe the arena the
  rule faces rather than the pool it was calibrated on. Both figures are stored.

TWO CALIBRATIONS.

  same-objective   the section 6.10 independent ensemble (five mse ens1 models)
                   against the shared-trunk ens5 arms. This is exactly M-44's
                   contrast and differs from M-68's only in the objective. Five
                   members, so the epistemic spread is the least noisy available.

  cross-objective  the three gaussian_nll ens1 models that already exist, scored
                   together as an independent ensemble, against the same
                   shared-trunk arms. This points in the direction M-68's contrast
                   points -- independence AND objective at once -- and carries
                   three members rather than five, so its spread is noisier.
                   Conservative for that reason.

CROSS-CHECK. The same statistics on the real four-trajectory held-out arena, with
the cluster bootstrap over whole trajectories (M-27) that M-68 will actually use.
It answers a slightly different question -- what the bootstrap's own SE is on the
four trajectories in hand -- and it is computed for both calibrations.

THE BINDING MDE at each horizon is the LARGEST of those four estimates: two
calibrations x (subsampling, bootstrap). Taking the maximum rather than arguing
for one of them makes the rule strictly harder to satisfy, which is the direction
a pre-registration should err in, and it removes the judgement call P1 had to make
between its two calibrations. Which estimate bound each figure is recorded per
horizon, so a reader can check the choice rather than take it.

CAVEAT carried into the rule. The twenty-trajectory pool is IN-SAMPLE for our own
arms, which trained on eight of the ten episodes. Section 5.6 states the same
caveat where it reports the M-43 subsampling estimate. In-sample trajectories are
easier and more alike, so the across-draw spread they give is, if anything, an
UNDERSTATEMENT of the spread the held-out arena produces -- which makes the MDE
built on it an optimistic floor, not a ceiling. The held-out cross-check is
recorded for exactly that reason.

Trains nothing, reads no artifact that does not already exist, and writes
results/p3_combined_arm_power.json.
"""
import itertools
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
import torch  # noqa: E402
import rwm_data as R  # noqa: E402
import rollout_eval as E  # noqa: E402
import rwm_metrics as MET  # noqa: E402
import score_reference as S  # noqa: E402
# The independent-ensemble rollout protocol is imported rather than copied: the
# comparison is only interpretable if the protocol is identical to the one the
# scoring harness uses, and two copies of a rollout drift. M-30's lesson applied
# to Python rather than to bash.
from r2_independent_ensemble import rollout_independent  # noqa: E402

HORIZONS = (1, 8, 32, 100, 128, 368)
START, LEN = E.START_STEP, 400
N_SUB = 4                  # the size of the genuine out-of-sample arena
N_BOOT = 20000             # cross-check only; matches the scoring harness
MSE_SEEDS = (0, 1, 2, 3, 4)      # section 6.10's independent ensemble
NLL_SEEDS = (0, 1, 2)            # the gaussian_nll ens1 models that already exist
SHARED_SEEDS = (0, 1, 2)         # the shared-trunk ens5 arms

Z95, Z80 = 1.959963985, 0.8416212336


def _short(name):
    """Compact label for the console table; the JSON carries the full name."""
    a, b = name.rsplit("_", 1)
    return f"{a.split('_')[0]}-{b[:4]}"


def mde(se):
    """Two-sided alpha = .05, power = .80, from an SE. Same formula as P1."""
    return float((Z95 + Z80) * se)


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
    print(f"  pool {label}: episodes {list(episodes)}, {len(starts)} trajectories, "
          f"n_independent = {n_ind}")
    return {"st": st, "ac": ac, "n_ind": n_ind, "n_traj": len(starts),
            "episodes": list(episodes)}


def load_ens1(seed, tag=""):
    w = f"runs/armA_seed{seed}{tag}/weights_2500.pt"
    assert os.path.exists(w), f"missing {w}"
    m = S.ReferenceRWM(torch.load(w, map_location="cpu")["model_state_dict"],
                       ensemble=1, hidden=256)
    m.eval()
    return m


def score_independent(seeds, tag, pool):
    """Roll N independent ens1 models as one ensemble; spread is across models."""
    models = [load_ens1(s, tag) for s in seeds]
    pred, _alea, epi, _as, _es = rollout_independent(models, pool["st"].clone(), pool["ac"])
    err = (pred - pool["st"]).abs().numpy().astype(np.float64)
    sig = epi.numpy().astype(np.float64)
    assert sig[:, START:].mean() > 0, "zero spread: the members are the same object"
    assert np.isfinite(err[:, START:]).all() and np.isfinite(sig[:, START:]).all()
    return {"abs_err": err, "epi": sig}


def score_shared(seed, pool):
    w = f"runs/armA_seed{seed}_ens5/weights_2500.pt"
    assert os.path.exists(w), f"missing {w}"
    m = S.ReferenceRWM(torch.load(w, map_location="cpu")["model_state_dict"])
    m.eval()
    pred, _alea, epi, _as, _es = m.rollout_uncertainty(
        pool["st"].clone(), pool["ac"], START, action_offset=1)
    return {"abs_err": (pred - pool["st"]).abs().numpy().astype(np.float64),
            "epi": epi.numpy().astype(np.float64)}


def per_trajectory(sc, h):
    """
    Per-trajectory reductions at horizon h.

    rho over a set of trajectories is sum|error| / sum sigma over that set, and
    coverage is the mean of the per-trajectory coverage fractions, because every
    trajectory contributes the same number of (step, dim) cells. So a subsample
    statistic is an exact function of these three vectors and the 4,845-way
    enumeration costs nothing.
    """
    sl = slice(START, START + h)
    e, g = sc["abs_err"][:, sl], sc["epi"][:, sl]
    n = e.shape[0]
    return {"sum_err": e.reshape(n, -1).sum(1),
            "sum_sig": g.reshape(n, -1).sum(1),
            "cov1": (e <= g).reshape(n, -1).mean(1),
            "cov2": (e <= 2 * g).reshape(n, -1).mean(1)}


def log_ratio(A, B, i):
    ra = A["sum_err"][i].sum() / A["sum_sig"][i].sum()
    rb = B["sum_err"][i].sum() / B["sum_sig"][i].sum()
    return float(np.log(ra / rb))


def cov_diff_pts(A, B, i, key="cov1"):
    return float(100 * (A[key][i].mean() - B[key][i].mean()))


def subsample_se(A, B, n_pool, key="cov1"):
    """
    M-43's method: every C(n_pool, 4) draw, exhaustively.

    Returns (se_log_ratio, se_coverage_pts, n_draws) already corrected for the
    finite pool, plus the uncorrected pair.
    """
    draws = list(itertools.combinations(range(n_pool), N_SUB))
    lr = np.array([log_ratio(A, B, list(d)) for d in draws])
    cv = np.array([cov_diff_pts(A, B, list(d), key) for d in draws])
    fpc = (n_pool - N_SUB) / (n_pool - 1)
    raw = (float(lr.std(ddof=1)), float(cv.std(ddof=1)))
    return {"n_draws": len(draws),
            "fpc_variance_factor": float(fpc),
            "log_ratio_se_raw": raw[0], "coverage_diff_se_pts_raw": raw[1],
            "log_ratio_se": raw[0] / float(np.sqrt(fpc)),
            "coverage_diff_se_pts": raw[1] / float(np.sqrt(fpc))}


def bootstrap_se(A, B, n, rng, key="cov1"):
    """The cross-check: cluster bootstrap over whole trajectories (M-27)."""
    lr, cv = [], []
    for _ in range(N_BOOT):
        i = rng.integers(0, n, n)
        v = log_ratio(A, B, i)
        if np.isfinite(v):
            lr.append(v)
        w = cov_diff_pts(A, B, i, key)
        if np.isfinite(w):
            cv.append(w)
    return {"log_ratio_se": float(np.std(lr, ddof=1)),
            "coverage_diff_se_pts": float(np.std(cv, ddof=1)),
            "n_valid": [len(lr), len(cv)]}


def main():
    print("P3 — POWER CHECK FOR M-68, run before the combined arm exists")
    print("=" * 104)

    split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"),
                         verbose=False)
    hold = list(split["holdout_episodes"])
    allep = sorted(set(split["train_episodes"]) | set(split["holdout_episodes"]))

    pool20 = load_pool(allep, "all-ten (M-43's subsampling pool)")
    pool4 = load_pool(hold, "held-out pair (M-68's arena)")
    assert pool4["n_ind"] == N_SUB, (
        f"the held-out arena is n_independent = {pool4['n_ind']}, not {N_SUB}; "
        "M-68's grid is written against 4 and must not be changed silently")

    arms20, arms4 = {}, {}
    for label, seeds, tag in (("indep5_mse", MSE_SEEDS, ""),
                              ("indep3_nll", NLL_SEEDS, "_nll")):
        arms20[label] = score_independent(seeds, tag, pool20)
        arms4[label] = score_independent(seeds, tag, pool4)
        print(f"  scored {label}: {len(seeds)} ens1 models, tag {tag or '(none)'}")
    for s in SHARED_SEEDS:
        arms20[f"shared_seed{s}"] = score_shared(s, pool20)
        arms4[f"shared_seed{s}"] = score_shared(s, pool4)
    print(f"  scored {len(SHARED_SEEDS)} shared-trunk ens5 arms: seeds {list(SHARED_SEEDS)}\n")

    CAL = {"same_objective": "indep5_mse", "cross_objective": "indep3_nll"}
    out = {
        "purpose": "estimate what M-68 can detect at the n_independent and horizons it "
                   "will face, BEFORE the combined arm is trained",
        "governing_rule": "M-68",
        "committed_before": "runs/armA_seed3_nll and runs/armA_seed4_nll, and any "
                            "scoring of the combined arm",
        "arena": "out-of-sample held-out pair",
        "n_independent_faced": pool4["n_ind"],
        "n_trajectories_faced": pool4["n_traj"],
        "holdout_episodes": hold,
        "horizons": list(HORIZONS),
        "distinct_bootstrap_resamples": N_SUB ** N_SUB,
        "statistics": [
            "log ratio of overconfidence factors (mean |error| / mean sigma_epistemic), "
            "two ensembles scored on the SAME trajectories",
            "difference in +-1 sigma coverage, in percentage points",
        ],
        "method": {
            "primary": "M-43 subsampling — every C(20, 4) = 4,845 draw of four "
                       "trajectories from the all-ten pool, exhaustively enumerated; "
                       "the across-draw SD is the sampling SE at n = 4",
            "finite_population_correction": "the raw SD is divided by "
                                            "sqrt((20 - 4) / (20 - 1)) so it describes "
                                            "an arena of four rather than a pool of "
                                            "twenty",
            "mde": "(z_.975 + z_.80) x SE; two-sided alpha = .05, power = .80",
            "bootstrap_unit": "whole trajectory (M-27); never trajectory x step",
            "cross_check": f"cluster bootstrap, {N_BOOT} resamples, on the four "
                           f"held-out trajectories themselves",
            "binding": "at each horizon the LARGEST of the four estimates — two "
                       "calibrations x (subsampling, bootstrap cross-check)",
        },
        "calibrations": CAL,
        "per_horizon": {},
        "binding_mde": {},
        "caveats": [],
    }

    print("  MDE at n_independent = 4, by horizon "
          "(subsampling, finite-pool corrected)")
    print(f"    {'h':>5} {'same-obj ratio':>15} {'same-obj cov':>13} "
          f"{'cross-obj ratio':>16} {'cross-obj cov':>14} "
          f"{'BINDING ratio':>14} {'BINDING cov':>12} {'bound by r/cov':>21}")
    print("    " + "-" * 118)

    for h in HORIZONS:
        pt20 = {k: per_trajectory(v, h) for k, v in arms20.items()}
        pt4 = {k: per_trajectory(v, h) for k, v in arms4.items()}
        rec = {}
        for cal, arm in CAL.items():
            subs, boots = [], []
            for s in SHARED_SEEDS:
                subs.append(subsample_se(pt20[arm], pt20[f"shared_seed{s}"],
                                         pool20["n_traj"]))
                boots.append(bootstrap_se(pt4[arm], pt4[f"shared_seed{s}"],
                                          pool4["n_traj"],
                                          np.random.default_rng(20260905 + 10 * h + s)))
            se_lr = float(np.mean([x["log_ratio_se"] for x in subs]))
            se_cv = float(np.mean([x["coverage_diff_se_pts"] for x in subs]))
            se_lr_b = float(np.mean([x["log_ratio_se"] for x in boots]))
            se_cv_b = float(np.mean([x["coverage_diff_se_pts"] for x in boots]))
            rec[cal] = {
                "arm": arm,
                "n_pairs": len(SHARED_SEEDS),
                "n_draws": subs[0]["n_draws"],
                "subsampling": {
                    "log_ratio_se": se_lr,
                    "coverage_diff_se_pts": se_cv,
                    "mde_ratio_multiplicative": float(np.exp(mde(se_lr))),
                    "mde_coverage_pts": mde(se_cv),
                },
                "cluster_bootstrap_cross_check": {
                    "log_ratio_se": se_lr_b,
                    "coverage_diff_se_pts": se_cv_b,
                    "mde_ratio_multiplicative": float(np.exp(mde(se_lr_b))),
                    "mde_coverage_pts": mde(se_cv_b),
                },
            }
        # The binding figure is the LARGEST of the four estimates at this horizon --
        # two calibrations x (subsampling, bootstrap cross-check). Choosing the max
        # rather than arguing for one of them makes the rule strictly harder to
        # satisfy, which is the direction a pre-registration should err in, and it
        # removes the judgement call P1 had to make between its two calibrations.
        a = rec["same_objective"]["subsampling"]
        b = rec["cross_objective"]["subsampling"]
        ab = rec["same_objective"]["cluster_bootstrap_cross_check"]
        bb = rec["cross_objective"]["cluster_bootstrap_cross_check"]
        srcs = {"same_objective_subsampling": a, "cross_objective_subsampling": b,
                "same_objective_bootstrap": ab, "cross_objective_bootstrap": bb}
        rname = max(srcs, key=lambda k: srcs[k]["mde_ratio_multiplicative"])
        cname = max(srcs, key=lambda k: srcs[k]["mde_coverage_pts"])
        bind_r = srcs[rname]["mde_ratio_multiplicative"]
        bind_c = srcs[cname]["mde_coverage_pts"]
        rec["binding"] = {
            "mde_ratio_multiplicative": bind_r,
            "mde_coverage_pts": bind_c,
            "ratio_bound_by": rname,
            "coverage_bound_by": cname,
        }
        out["per_horizon"][str(h)] = rec
        out["binding_mde"][str(h)] = {"ratio_multiplicative": bind_r,
                                      "coverage_pts": bind_c}
        print(f"    {h:>5} {a['mde_ratio_multiplicative']:>14.3f}x "
              f"{a['mde_coverage_pts']:>12.2f} "
              f"{b['mde_ratio_multiplicative']:>15.3f}x {b['mde_coverage_pts']:>13.2f} "
              f"{bind_r:>13.3f}x {bind_c:>11.2f} "
              f"{_short(rec['binding']['ratio_bound_by']):>10}"
              f"/{_short(rec['binding']['coverage_bound_by']):<10}")

    worst_r = max(out["binding_mde"].values(), key=lambda v: v["ratio_multiplicative"])
    worst_c = max(out["binding_mde"].values(), key=lambda v: v["coverage_pts"])
    out["worst_horizon"] = {
        "ratio_multiplicative": worst_r["ratio_multiplicative"],
        "coverage_pts": worst_c["coverage_pts"],
        "note": "the loosest horizon in the grid; a rule that must hold at EVERY "
                "horizon is bounded by this one",
    }
    out["reading"] = (
        f"at n_independent = {pool4['n_ind']} M-68 resolves an overconfidence ratio of "
        f"{worst_r['ratio_multiplicative']:.2f}x or better and a +-1 sigma coverage "
        f"shift of {worst_c['coverage_pts']:.2f} percentage points or more at every "
        f"horizon in its grid. Smaller effects are not distinguishable from zero by "
        f"this rule and the rule says so in advance.")
    out["caveats"] = [
        "The 20-trajectory subsampling pool is IN-SAMPLE for our own arms, which "
        "trained on eight of the ten episodes. In-sample trajectories are easier and "
        "more alike, so the across-draw spread understates the held-out spread and the "
        "MDE built on it is an optimistic floor. The cluster-bootstrap cross-check on "
        "the four held-out trajectories is recorded beside every figure for that "
        "reason.",
        "Nothing here estimates the combined arm's EFFECT. The arm does not exist. "
        "What is estimated is the sampling variability of the comparison statistic, "
        "which is a property of four trajectories and of how much the pairing cancels.",
        "The cross-objective calibration carries three members, not five, because only "
        "three gaussian_nll models exist before the runs M-68 governs. A three-member "
        "spread is noisier than a five-member one, which is why it is the conservative "
        "of the two and not a substitute for the arm itself.",
        f"At n_independent = {N_SUB} the cluster bootstrap has {N_SUB ** N_SUB} "
        "distinct resamples, so every M-68 interval is quantised at that resolution. "
        "Section 4 states the same for the A/B interval and no interpolation is applied.",
        "MDE is computed from an SE and a normal approximation. At n = 4 the sampling "
        "distribution is not normal, so the MDE is indicative rather than exact — the "
        "honest form of the statement a pre-registered rule needs.",
    ]

    print(f"\n  {out['reading']}")

    dst = os.path.join(R.RESULTS, "p3_combined_arm_power.json")
    with open(dst, "w") as f:
        json.dump(out, f, indent=2, sort_keys=True)
    print(f"\n  wrote {R.rel(dst)}")


if __name__ == "__main__":
    main()
