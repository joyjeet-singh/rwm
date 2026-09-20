"""
Q2 -- how many independent trajectories would settle the step-size margin?

WHY. §6.7 reports that the model's own predicted step size ranks realised error at
+0.4697 against five-member ensemble disagreement's +0.6053. The margin, +0.1357, is
below the threshold `M-51` fixed before either new baseline existed, so the verdict is
SURVIVES entry-res ONLY and the comparison is recorded as unresolved rather than as a
win for either side. §11 calls settling it "the cheapest open question here for anyone
with a second dataset". A referee asked for a number.

TWO NUMBERS, BECAUSE THERE ARE TWO QUESTIONS, AND THE FIRST DRAFT OF THIS SCRIPT
CONFLATED THEM. The conflation is recorded here because it is the interesting part.

  (a) HOW MANY TRAJECTORIES WOULD RESOLVE THIS MARGIN?  The margin is a difference of
      two correlations, and what decides whether it can be told from zero is ITS OWN
      sampling variability. `e7_free_baselines.py` already bootstraps exactly that, per
      baseline, and stores the interval as `margin_ci`. This is the referee's question.

  (b) AT WHAT n WOULD `M-51`'s PROTOCOL, RE-RUN AS PRE-REGISTERED, FIRE ON A MARGIN THIS
      SIZE?  `M-51` fixed ONE threshold before either new baseline existed, estimated
      from the FORECAST-INDEX margin -- necessarily, since the new baselines did not
      exist to be bootstrapped. That is correct pre-registration and it is a different
      quantity: the index margin's bootstrap standard error is about 1.9x the step-size
      margin's. The dominant reason, measured rather than assumed, is that the forecast
      index's OWN correlation with error is about 1.8x more variable across resampled
      trajectories than step-size's is; the covariance terms then widen the gap further.
      Run --empirical for the decomposition.

Answering (a) with (b)'s standard error inflates the requirement about 3.6-fold. The
first draft of this script did precisely that -- it took the stored `bootstrap_se_margin`,
which belongs to the index margin, and applied it to the step-size margin's effect -- and
a reviewer caught it. Both numbers are reported below, each against its own question.

WHAT IS THE SAME IN BOTH. The construction `M-51` used, unchanged:

    MDE = (Z95 + Z80) * se        Z95 = 1.959963985  (two-sided, alpha = 0.05)
                                  Z80 = 0.8416212336 (80% power)

with se a bootstrap standard error over WHOLE 400-step trajectories, 4,000 replicates,
and the statistic a difference of two correlations with realised error. Only n moves,
as se(n) = se(n0) * sqrt(n0 / n), n0 = 20.

WHERE (a)'s STANDARD ERROR COMES FROM WITHOUT A ROLLOUT. `e7_free_baselines.py:main`
bootstraps each baseline's own margin with the same unit and the same 4,000 replicates
and stores a 2.5/97.5 percentile interval. Halving its width and dividing by Z95 recovers
the standard error under approximate normality of the bootstrap distribution. Run with
--empirical to bootstrap the margin directly instead and compare; they agree to under 1%.

THE VERDICT DOES NOT MOVE, AND THIS SCRIPT DOES NOT MOVE IT. On the step-size margin's
own standard error the threshold at n = 20 is still above the observed margin, so §6.7's
verdict stands exactly as published. What changes is how close it was: against `M-51`'s
pre-registered threshold the margin reads as under half of what the sample resolves, and
against its own statistic's it is over nine tenths of it. `M-51`'s threshold is
conservative when applied to this baseline, and that is a property of the pre-registered
design worth stating rather than hiding. Every figure in that comparison is computed
below and printed from the computation, never typed here.

    python scripts/q2_free_baseline_power.py              both curves, from artifacts
    python scripts/q2_free_baseline_power.py --empirical  additionally bootstraps the
                                                          step-size margin directly, to
                                                          check the interval-implied
                                                          standard error and the
                                                          1/sqrt(n) rescaling

Reads results/e7_free_baselines_power.json and results/e7_free_baselines.json.
Writes results/q2_free_baseline_power.json.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import rwm_data as R  # noqa: E402

# The same constants e7_free_baselines.py uses. Not re-chosen here.
Z95, Z80 = 1.959963985, 0.8416212336
GRID = [20, 25, 30, 40, 50, 60, 70, 80, 90, 100, 120, 150, 200, 300, 400]
BASELINE = "step-size"


def _load():
    pw = json.load(open(os.path.join(R.RESULTS, "e7_free_baselines_power.json")))
    fb = json.load(open(os.path.join(R.RESULTS, "e7_free_baselines.json")))
    row = next(b for b in fb["baselines"] if b["baseline"] == BASELINE)
    return pw, fb, row


def _check_same_construction(pw):
    """Refuse to run unless the stored thresholds really are (Z95+Z80)*se.

    NOTE ON WHAT THIS DOES AND DOES NOT CONSTRAIN, because an earlier version of this
    script claimed more for it than it delivers. It pins the two Z constants and the
    multiplication -- nothing else. It CANNOT see which baseline a standard error
    belongs to, so it would not have caught this script's first-draft defect of pairing
    the index margin's standard error with the step-size margin's effect. The guard
    against that is structural instead: the primary answer below derives its standard
    error from the SAME baseline row it takes its effect from, and --empirical
    re-derives it by bootstrap.
    """
    for key, se_key in (("margin", "bootstrap_se_margin"), ("partial", "bootstrap_se_partial")):
        want = pw["mde_80pct_power"][key]
        got = (Z95 + Z80) * pw[se_key]
        assert abs(got - want) < 1e-12, (
            f"reconstructed threshold on the {key} is {got!r}, the artifact stores "
            f"{want!r}; the (Z95+Z80)*se construction this script inverts is not the "
            "one e7_free_baselines.py used")


def _se_from_ci(lo, hi):
    """Standard error implied by a 95% percentile interval, under approximate normality."""
    return (hi - lo) / 2.0 / Z95


def _mde_at(se_n0, n0, n):
    return (Z95 + Z80) * se_n0 * math.sqrt(n0 / n)


def _smallest_n(se_n0, n0, target, cap=1000000):
    closed = (Z95 + Z80) ** 2 * se_n0 ** 2 * n0 / target ** 2
    n = max(1, int(math.floor(closed)))
    while n <= cap and _mde_at(se_n0, n0, n) > target:
        n += 1
    assert n <= cap, "no n within the cap resolves the margin"
    assert _mde_at(se_n0, n0, n) <= target
    assert n == 1 or _mde_at(se_n0, n0, n - 1) > target
    return n, closed


def _curve(se_n0, n0, target, extra):
    out = []
    for n in sorted(set(GRID + list(extra))):
        mde = _mde_at(se_n0, n0, n)
        out.append({"n_independent": n, "mde": mde,
                    "resolvable": bool(mde <= target), "shortfall": mde - target})
    return out


def _empirical(n_have, seed, n_boot):
    """Bootstrap the step-size margin directly, with E7's own panel and statistic."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import e7_free_baselines as E7  # noqa: E402

    D = E7.load_panel()
    B = E7.baselines(D)
    err, dis, fidx, b = D["err"], D["dis"], D["fidx"], B[BASELINE]
    assert D["n_traj"] == n_have

    def se_of(fn):
        # A FRESH generator per statistic, each on E7's own seed, so that the index-margin
        # control replays e7_free_baselines.py:power's exact draws and must reproduce its
        # stored value. Sharing one generator would advance it past those draws and the
        # control would compare against different random numbers.
        rng = np.random.default_rng(seed)
        v = [fn(rng.integers(0, n_have, n_have)) for _ in range(n_boot)]
        v = np.array([x for x in v if np.isfinite(x)])
        return float(v.std(ddof=1))

    # Why the two standard errors differ, measured on one shared set of draws so the
    # variances and covariances are comparable. Recorded because the obvious explanation
    # — that disagreement is correlated with step-size and not with the forecast index —
    # is false: the index is correlated with disagreement too, just less.
    rng = np.random.default_rng(seed)
    draws = [rng.integers(0, n_have, n_have) for _ in range(n_boot)]
    rd = np.array([E7._corr(dis[i], err[i]) for i in draws])
    rs = np.array([E7._corr(b[i], err[i]) for i in draws])
    rf = np.array([E7._corr(fidx[i], err[i]) for i in draws])
    ok = np.isfinite(rd) & np.isfinite(rs) & np.isfinite(rf)
    rd, rs, rf = rd[ok], rs[ok], rf[ok]
    vd, vs, vf = rd.var(ddof=1), rs.var(ddof=1), rf.var(ddof=1)
    cs, cf = np.cov(rd, rs, ddof=1)[0, 1], np.cov(rd, rf, ddof=1)[0, 1]

    return {
        "se_step_size_margin": se_of(
            lambda i: E7._corr(dis[i], err[i]) - E7._corr(b[i], err[i])),
        "se_index_margin_control": se_of(
            lambda i: E7._corr(dis[i], err[i]) - E7._corr(fidx[i], err[i])),
        "variance_decomposition": {
            "what": "var(margin) = var(r_dis) + var(r_baseline) - 2 cov, over one shared set of "
                    "bootstrap draws. Answers why M-51's threshold is conservative here.",
            "pooled_r_disagreement_step_size": E7._corr(dis, b),
            "pooled_r_disagreement_forecast_index": E7._corr(dis, fidx),
            "sd_r_disagreement_error": float(np.sqrt(vd)),
            "sd_r_step_size_error": float(np.sqrt(vs)),
            "sd_r_forecast_index_error": float(np.sqrt(vf)),
            "sd_ratio_index_over_step_size": float(np.sqrt(vf / vs)),
            "cov_disagreement_step_size": float(cs),
            "cov_disagreement_forecast_index": float(cf),
            "corr_across_draws_step_size": float(cs / np.sqrt(vd * vs)),
            "corr_across_draws_forecast_index": float(cf / np.sqrt(vd * vf)),
            "se_ratio_with_covariances": float(np.sqrt(vd + vf - 2 * cf) / np.sqrt(vd + vs - 2 * cs)),
            "se_ratio_if_covariances_were_zero": float(np.sqrt(vd + vf) / np.sqrt(vd + vs)),
            "reading": "The dominant driver is that the forecast index's OWN correlation with "
                       "error is far more variable across resampled trajectories than step-size's "
                       "is; that alone accounts for most of the ratio. The covariance terms, which "
                       "have opposite signs across draws, widen it the rest of the way. The "
                       "premise that the forecast index is uncorrelated with disagreement is "
                       "false and is not what drives this.",
        },
    }


def main():
    pw, fb, row = _load()
    _check_same_construction(pw)

    n0 = pw["n_independent"]
    assert n0 == fb["design"]["n_independent"] == 20
    assert fb["design"]["bootstrap_unit"] == "whole trajectory"
    assert fb["design"]["n_boot"] == pw["n_boot"]

    margin = row["margin"]
    se_own = _se_from_ci(*row["margin_ci"])          # this baseline's own variability
    se_prereg = pw["bootstrap_se_margin"]            # M-51's, from the forecast index

    n_own, closed_own = _smallest_n(se_own, n0, margin)
    n_prereg, closed_prereg = _smallest_n(se_prereg, n0, margin)

    rec = {
        "question": "Referee Q2 — how many independent 400-step trajectories would settle the "
                    "step-size comparison?",
        "answer_to_the_referee": {
            "n_independent_required": n_own,
            "n_exact_unrounded": closed_own,
            "factor_over_current": n_own / n0,
            "se_used": se_own,
            "se_source": "the step-size baseline's own margin_ci in "
                         "results/e7_free_baselines.json, a 2.5/97.5 percentile interval from the "
                         "same bootstrap (whole trajectories, same n_boot); halved and divided by "
                         "Z95 under approximate normality of the bootstrap distribution",
            "mde_at_n0": (Z95 + Z80) * se_own,
            "resolvable_at_n0": bool((Z95 + Z80) * se_own <= margin),
            "curve": _curve(se_own, n0, margin, (n_own, n_own - 1)),
        },
        "answer_under_m51_as_pre_registered": {
            "n_independent_required": n_prereg,
            "n_exact_unrounded": closed_prereg,
            "factor_over_current": n_prereg / n0,
            "se_used": se_prereg,
            "se_source": "results/e7_free_baselines_power.json bootstrap_se_margin — the "
                         "FORECAST-INDEX margin's standard error, which is what M-51 could "
                         "estimate before either new baseline existed",
            "mde_at_n0": pw["mde_80pct_power"]["margin"],
            "what_this_answers": "at what n a re-run of M-51's protocol would fire on a margin "
                                 "of this size. It is NOT the referee's question, because the "
                                 "threshold is calibrated on a different and more variable "
                                 "statistic than the one it is applied to.",
            "curve": _curve(se_prereg, n0, margin, (n_prereg, n_prereg - 1)),
        },
        "why_the_two_differ": {
            "se_ratio_prereg_over_own": se_prereg / se_own,
            "n_ratio": n_prereg / n_own,
            "reason": "M-51 had to fix one threshold before either new baseline existed, so it "
                      "necessarily used the forecast-index margin's variability. That is correct "
                      "pre-registration, and it is conservative when applied to this baseline. "
                      "For WHY the two differ, see variance_decomposition under empirical_check: "
                      "it is measured there rather than asserted here, because the obvious "
                      "explanation — that disagreement is correlated with step-size and not with "
                      "the forecast index — is false. The index is correlated with disagreement "
                      "too, just less.",
        },
        "the_published_verdict_does_not_move": {
            "observed_margin": margin,
            "threshold_m51_pre_registered": pw["mde_80pct_power"]["margin"],
            "threshold_own_statistic": (Z95 + Z80) * se_own,
            "resolvable_under_either": False,
            "pct_of_m51_threshold": 100.0 * margin / pw["mde_80pct_power"]["margin"],
            "pct_of_own_threshold": 100.0 * margin / ((Z95 + Z80) * se_own),
            "note": (
                "§6.7's verdict SURVIVES entry-res ONLY stands on both readings: "
                f"{margin:+.4f} is below {pw['mde_80pct_power']['margin']:.4f} and also below "
                f"{(Z95 + Z80) * se_own:.4f}. What changes is the distance — the margin is "
                f"{100.0 * margin / pw['mde_80pct_power']['margin']:.0f}% of M-51's threshold and "
                f"{100.0 * margin / ((Z95 + Z80) * se_own):.0f}% of its own statistic's, so the "
                "comparison is much closer to resolving than the published threshold implies."),
        },
        "construction": {
            "inverts": "scripts/e7_free_baselines.py",
            "formula": "MDE(n) = (Z95 + Z80) * se(n), se(n) = se(n0) * sqrt(n0 / n)",
            "z95_two_sided_alpha_0.05": Z95,
            "z80_power": Z80,
            "statistic": "r(disagreement, error) - r(baseline, error), a difference of two "
                         "correlations",
            "bootstrap_unit": "whole 400-step trajectory",
            "n_boot_of_source_estimate": pw["n_boot"],
            "construction_checked": "the stored thresholds on both the margin and the partial are "
                                    "reproduced from the stored standard errors to within 1e-12. "
                                    "This pins the two constants and the multiplication only; it "
                                    "cannot see which baseline a standard error belongs to.",
        },
        "observed": {
            "baseline": BASELINE,
            "r_baseline_error": row["r_baseline_error"],
            "r_disagreement_error": row["r_disagreement_error"],
            "margin": margin,
            "margin_ci": row["margin_ci"],
            "partial_disagreement_given_baseline": row["partial_disagreement_given_baseline"],
            "n_independent": n0,
            "n_steps": pw["n_steps"],
            "margin_beats_mde_at_n0": row["margin_beats_mde"],
            "partial_beats_mde_at_n0": row["partial_beats_mde"],
        },
        "binding_test": "the margin. e7_free_baselines.py records a baseline as beaten only if "
                        "BOTH its margin and its partial clear their thresholds; for step-size "
                        "the partial already clears at n = 20 (+0.5430 against 0.1131) and the "
                        "margin does not, so the margin is what a larger sample would settle.",
        "assumption": "Both figures are required-sample-size estimates UNDER AN ASSUMED EFFECT. "
                      "They assume the margin's true value is the observed one and that further "
                      "400-step trajectories would resemble these twenty in variability. Neither "
                      "is a guarantee: if the true margin is smaller than observed, the "
                      "requirement rises as its inverse square, which is why a curve and a "
                      "sensitivity table are stored rather than a single number.",
        "sensitivity_to_assumed_margin": [
            {"assumed_margin": d,
             "n_required_own_statistic": _smallest_n(se_own, n0, d)[0],
             "n_required_m51_threshold": _smallest_n(se_prereg, n0, d)[0],
             "note": "observed" if abs(d - margin) < 1e-12 else "smaller than observed"}
            for d in (margin, 0.12, 0.10, 0.08, 0.07, 0.05)
        ],
        "generated_with": ("scripts/q2_free_baseline_power.py --empirical"
                           if "--empirical" in sys.argv else
                           "scripts/q2_free_baseline_power.py"),
    }

    if "--empirical" in sys.argv:
        emp = _empirical(n_have=n0, seed=20260829, n_boot=pw["n_boot"])
        rec["empirical_check"] = {
            "what": "E7's own panel and statistic, bootstrapped directly at n = 20 with E7's own "
                    "seed and n_boot. Two numbers: the step-size margin's standard error, which "
                    "the default path infers from margin_ci, and the index margin's, which acts "
                    "as a control because e7_free_baselines.py stores it and it must reproduce.",
            "se_step_size_margin_direct": emp["se_step_size_margin"],
            "se_step_size_margin_from_ci": se_own,
            "relative_gap": abs(emp["se_step_size_margin"] - se_own) / se_own,
            "se_index_margin_direct": emp["se_index_margin_control"],
            "se_index_margin_stored": se_prereg,
            "control_reproduces": bool(
                abs(emp["se_index_margin_control"] - se_prereg) < 1e-6),
            "variance_decomposition": emp["variance_decomposition"],
            "seed": 20260829,
        }
        assert rec["empirical_check"]["control_reproduces"], (
            "the index-margin control did not reproduce the stored standard error; the panel or "
            "the bootstrap has changed and no figure here can be trusted")

    a, b = rec["answer_to_the_referee"], rec["answer_under_m51_as_pre_registered"]
    print("Q2 — HOW MANY TRAJECTORIES WOULD SETTLE THE STEP-SIZE COMPARISON?")
    print("=" * 88)
    print(f"  observed margin {margin:+.4f}  "
          f"(r_dis {row['r_disagreement_error']:+.4f} - r_{BASELINE} "
          f"{row['r_baseline_error']:+.4f}), n_independent = {n0}\n")
    print(f"  (a) against ITS OWN sampling variability   se = {se_own:.4f}  "
          f"threshold {a['mde_at_n0']:.4f}  ->  n = {a['n_independent_required']}")
    print(f"  (b) under M-51's pre-registered threshold  se = {se_prereg:.4f}  "
          f"threshold {b['mde_at_n0']:.4f}  ->  n = {b['n_independent_required']}")
    print(f"      the two standard errors differ by {se_prereg / se_own:.2f}x, so the two "
          f"answers differ by {n_prereg / n_own:.2f}x\n")
    print(f"  {'n':>6}  {'MDE (own)':>10}  {'resolvable':>11}")
    for c in a["curve"]:
        print(f"  {c['n_independent']:>6}  {c['mde']:>10.4f}  "
              f"{'yes' if c['resolvable'] else 'no':>11}")
    if "empirical_check" in rec:
        e = rec["empirical_check"]
        print(f"\n  empirical: step-size se direct {e['se_step_size_margin_direct']:.6f} vs "
              f"{e['se_step_size_margin_from_ci']:.6f} from the interval "
              f"({e['relative_gap'] * 100:.2f}%)")
        print(f"             index-margin control reproduces the stored value: "
              f"{e['control_reproduces']}")
    v = rec["the_published_verdict_does_not_move"]
    print(f"\n  THE PUBLISHED VERDICT DOES NOT MOVE: {margin:+.4f} is below both thresholds "
          f"({v['threshold_m51_pre_registered']:.4f} and {v['threshold_own_statistic']:.4f}),")
    print(f"  so §6.7's SURVIVES entry-res ONLY stands. It is {v['pct_of_own_threshold']:.0f}% of "
          f"its own statistic's threshold, not {v['pct_of_m51_threshold']:.0f}%.")
    print("  ASSUMPTION: required sample size under an assumed effect. Not a guarantee.")

    json.dump(rec, open(os.path.join(R.RESULTS, "q2_free_baseline_power.json"), "w"), indent=2)
    print("\n  wrote results/q2_free_baseline_power.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
