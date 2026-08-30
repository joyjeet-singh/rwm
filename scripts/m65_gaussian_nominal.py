"""2.3 -- M-65: is the Gaussian nominal of 68.27% defensible, or is the error
distribution heavy-tailed?

Every coverage figure in this paper is read against 68.27% at +-1 sigma and 95.45% at
+-2 sigma, the two-sided Gaussian targets section 3.1 derives from erf(k/sqrt(2)). The paper has
never checked the marginal normality that nominal assumes.

A coverage shortfall has two possible causes and the paper currently attributes all of it
to one. Sigma may be the wrong SCALE, or the error distribution may be heavier-tailed than
Gaussian, in which case part of the shortfall would persist under a perfectly scaled sigma
and 68.27% is the wrong target to read against.

THE TEST. Rescale sigma by a single constant c chosen so that mean|error| / mean(c*sigma)
equals sqrt(2/pi) = 0.7979, the value a calibrated Gaussian gives. Since the
overconfidence factor rho is itself a ratio of means (section 3.1), c = rho / 0.7979 in closed
form -- no fitting and no search. Then measure coverage under c*sigma.

WHAT THIS CANNOT ESTABLISH, fixed before the run. The constant is fitted and evaluated on
the SAME data, deliberately. That makes it an UPPER BOUND on what any constant rescale
could achieve, which is what gives the negative branch its force: if coverage is still far
short when sigma is scaled as well as any constant could scale it, then no constant
rescaling -- and therefore no lambda -- repairs it. The positive branch is correspondingly
weak: an adequate oracle-rescaled coverage does NOT show a transferable constant exists,
and section 6.8 already establishes that a constant multiplier fails across horizons while a
per-horizon one succeeds.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import rwm_data as R  # noqa: E402
import per_triple_cache as PTC  # noqa: E402

CALIB = math.sqrt(2.0 / math.pi)          # 0.7978845608028654
TARGET1, TARGET2 = 68.27, 95.45
HS = (1, 8, 32, 100, 128, 368)

# Every cached model x arena x sigma term. The released checkpoint appears in both arenas
# because section 6.2 reports it in both and they differ in horizon as well as arena.
CASES = [
    ("released_ckpt_ens5", "all ten episodes", (None,), "epistemic", 20),
    ("released_ckpt_ens5", "all ten episodes", (None,), "aleatoric", 20),
    ("released_ckpt_ens5", "out-of-sample held-out pair", (None,), "aleatoric", 4),
    ("armA_faithful_mse", "out-of-sample held-out pair", (0, 1, 2), "aleatoric", 4),
    ("armA_corrected_nll", "out-of-sample held-out pair", (0, 1, 2), "aleatoric", 4),
    ("armB_teacher_forced", "out-of-sample held-out pair", (0, 1, 2), "aleatoric", 4),
    ("armA_ens5", "out-of-sample held-out pair", (0, 1, 2), "epistemic", 4),
    ("armA_ens5", "out-of-sample held-out pair", (0, 1, 2), "aleatoric", 4),
]


def load(slug, arena, seeds, term):
    es, gs = [], []
    key = "sig_epistemic" if term == "epistemic" else "sig_aleatoric"
    for sd in seeds:
        mid = slug if sd is None else f"{slug}_seed{sd}"
        a, _ = PTC.read(mid, arena, 400)
        es.append(np.abs(a["err"])); gs.append(a[key])
    return np.concatenate(es, 0), np.concatenate(gs, 0)


def branch(cov_orc):
    if cov_orc is None:
        return "UNDEFINED"
    if abs(cov_orc - TARGET1) <= 5.0:
        return "GAUSSIAN NOMINAL ADEQUATE"
    if cov_orc < TARGET1 - 5.0:
        return "HEAVY-TAILED"
    return "OVER-DISPERSED"


def main():
    out = {
        "rule": "M-65",
        "calibrated_ratio_sqrt_2_over_pi": CALIB,
        "targets": {"pm1_pct": TARGET1, "pm2_pct": TARGET2},
        "test": ("rescale sigma by a single constant c = rho / sqrt(2/pi) so that "
                 "mean|error| / mean(c*sigma) equals the calibrated Gaussian value, then "
                 "measure coverage under c*sigma"),
        "decomposition_fixed_in_advance": {
            "total_shortfall": "68.27 - cov_observed",
            "attributable_to_shape": "68.27 - cov_oracle",
            "attributable_to_scale": "cov_oracle - cov_observed",
            "note": "the two parts sum to the total by construction",
        },
        "thresholds_committed_in_advance": {
            "GAUSSIAN NOMINAL ADEQUATE": "oracle-rescaled +-1 sigma coverage in [63.27, 73.27]",
            "HEAVY-TAILED": "below 63.27",
            "OVER-DISPERSED": "above 73.27",
        },
        "cannot_establish": (
            "the constant is fitted and scored on the same data, deliberately. That makes "
            "it an UPPER BOUND on what any constant rescale could achieve, which gives the "
            "negative branch its force -- no constant, and therefore no lambda, does "
            "better. The positive branch is correspondingly weak and does not show a "
            "transferable constant exists; section 6.8 already shows a constant fails across "
            "horizons where a per-horizon one succeeds."),
        "minimum_detectable_effect": (
            "none in the sampling sense: c is a ratio of two means and the resulting "
            "coverage is a deterministic function of the stored errors. There is no "
            "estimator here whose power could be computed."),
        "cases": {},
    }

    print("=" * 108)
    print("M-65 — IS THE GAUSSIAN NOMINAL DEFENSIBLE?")
    print("=" * 108)
    print(f"  calibrated mean|error|/sigma = sqrt(2/pi) = {CALIB:.6f};  "
          f"targets {TARGET1}% at +-1 sigma, {TARGET2}% at +-2 sigma\n")

    verdicts = {}
    for slug, arena, seeds, term, n_ind in CASES:
        e, g = load(slug, arena, seeds, term)
        label = f"{slug} [{term}] {arena}"
        rows = {}
        print(f"  {label}   n_independent = {n_ind}")
        print(f"    {'h':>5} {'rho':>12} {'c':>12} {'cov obs':>9} {'cov orc':>9} "
              f"{'+-2s orc':>9} {'shape':>8} {'scale':>8}  verdict")
        for h in HS:
            eh, gh = e[:, :h], g[:, :h]
            mg = float(np.nanmean(gh))
            me = float(np.nanmean(eh))
            if not np.isfinite(mg) or mg <= 0:
                rows[str(h)] = {"undefined": True,
                                "reason": "sigma term unavailable for this model (NaN)"}
                continue
            rho = me / mg
            c = rho / CALIB
            cov_obs = float(np.nanmean(eh <= gh) * 100.0)
            cov_orc = float(np.nanmean(eh <= c * gh) * 100.0)
            cov2_obs = float(np.nanmean(eh <= 2 * gh) * 100.0)
            cov2_orc = float(np.nanmean(eh <= 2 * c * gh) * 100.0)
            shape = TARGET1 - cov_orc
            scale = cov_orc - cov_obs
            v = branch(cov_orc)
            rows[str(h)] = {
                "rho_err_over_sigma": rho, "oracle_constant_c": c,
                "coverage_pm1_observed_pct": cov_obs,
                "coverage_pm1_oracle_pct": cov_orc,
                "coverage_pm2_observed_pct": cov2_obs,
                "coverage_pm2_oracle_pct": cov2_orc,
                "gap_pm1_from_target_pts": cov_orc - TARGET1,
                "gap_pm2_from_target_pts": cov2_orc - TARGET2,
                "total_shortfall_pts": TARGET1 - cov_obs,
                "attributable_to_shape_pts": shape,
                "attributable_to_scale_pts": scale,
                "shape_share_of_shortfall": (shape / (TARGET1 - cov_obs)
                                             if TARGET1 - cov_obs > 0 else None),
                "verdict": v,
            }
            verdicts.setdefault(v, 0)
            verdicts[v] += 1
            print(f"    {h:>5} {rho:>12,.1f} {c:>12,.1f} {cov_obs:>8.2f}% {cov_orc:>8.2f}% "
                  f"{cov2_orc:>8.2f}% {shape:>7.1f} {scale:>7.1f}  {v}")
        out["cases"][label] = {"model_id": slug, "arena": arena, "sigma_term": term,
                               "n_independent": n_ind, "seeds": list(seeds),
                               "by_horizon": rows}
        print()

    gov = out["cases"]["released_ckpt_ens5 [epistemic] all ten episodes"]["by_horizon"]
    out["verdict"] = {
        "returned_per_model_and_horizon": True,
        "counts": verdicts,
        "governing_row": {
            "case": "released_ckpt_ens5 [epistemic] all ten episodes",
            "h1": gov["1"]["verdict"],
            "h100": gov["100"]["verdict"],
            "h1_oracle_coverage_pct": gov["1"]["coverage_pm1_oracle_pct"],
            "h100_oracle_coverage_pct": gov["100"]["coverage_pm1_oracle_pct"],
            "h1_shape_share": gov["1"]["shape_share_of_shortfall"],
        },
        "reading": ("Reported per model and per horizon, not pooled. Where models or "
                    "horizons disagree that is reported rather than summarised into one "
                    "word, as M-65 required in advance."),
    }
    print(f"  VERDICT COUNTS across all model x horizon cells: {verdicts}")
    print(f"  governing row (released checkpoint, epistemic, all ten): "
          f"h=1 {gov['1']['verdict']}, h=100 {gov['100']['verdict']}")

    op = os.path.join(R.RESULTS, "m65_gaussian_nominal.json")
    json.dump(out, open(op, "w"), indent=2)
    print(f"  wrote {R.rel(op)}")


if __name__ == "__main__":
    main()
