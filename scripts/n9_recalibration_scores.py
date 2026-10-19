"""
N9 (round 5; POST HOC) -- scoring the per-horizon recalibration. docs/presubmission/round5/PROTOCOLS.md §5 N9 is the
specification; this is a summary. It never re-opens X7, M-69 or M-70 and changes no verdict: X7 read +-1 sigma coverage only;
this adds the scores a reader also needs -- +-2 sigma coverage, Gaussian CRPS and NLL, and the interval width -- before and
after each rescaling.

INPUT. X7's leave-one-episode-out fit, reused exactly: the released checkpoint's per-episode rollouts
(task_d3_perhorizon.episode_rollout) and x7_loeo_recalibration.reading(), unchanged, which fits per fold e the per-horizon
multiplier c_fold[e][h] and the constant cc[e] on the other nine episodes.
PER HORIZON and calibration C in {before (1), constant (cc[e]), per-horizon (c_fold[e][h])}: each episode scored with its own
fold's multiplier, the ten episodes pooled by concatenation (ratio of sums, as task_d3_cross_model.counts/pooled), with
task_d3_perhorizon.cover's mask (finite C*sigma > 0): +-1 and +-2 sigma coverage, mean Gaussian CRPS and NLL with scale
C*sigma (PROTOCOLS §1), and mean +-1 sigma interval width 2*C*sigma, normalised-state units. Intervals: X7's draw matrix,
default_rng(0).integers(0, 20, (20000, 20)) over the 20 trajectories in X7's order. Epistemic (X7's quantity); aleatoric too.
ASSERTION, before any score: X7's +-1 sigma coverage and interval for all three calibrations at every horizon, from
reading(), equal results/x7_loeo_recalibration.json within 1e-12, and every multiplier within 1e-9 relative.
Writes results/n9_recalibration_scores.json. Run from the repository root.
"""
import json
import math
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import torch  # noqa: E402
import rwm_data as R  # noqa: E402
import task_d3_perhorizon as TD3  # noqa: E402
import x7_loeo_recalibration as X7  # noqa: E402
import x11_common as C  # noqa: E402

OUT = os.path.join(R.RESULTS, "n9_recalibration_scores.json")
HS = X7.HS
START = TD3.START
TOL_COV, TOL_C = 1e-12, 1e-9
MODULES = ("scripts/n9_recalibration_scores.py", "scripts/x7_loeo_recalibration.py", "scripts/task_d3_perhorizon.py",
           "scripts/task_d3_cross_model.py", "src/score_reference.py", "scripts/x11_common.py")


def phi_cdf(z):
    return 0.5 * (1.0 + torch.special.erf(torch.from_numpy(z) / math.sqrt(2.0)).numpy())


def sums(err, sig, c, h):
    """Per trajectory: (valid, +-1 hits, +-2 hits, CRPS sum, NLL sum, width sum) with scale c*sigma, steps 1..h."""
    sl = slice(START, START + h)
    e = np.ascontiguousarray(err[:, sl])
    g = np.ascontiguousarray(sig[:, sl]) * c
    m = np.isfinite(g) & (g > 0) & np.isfinite(e)
    gs = np.where(m, g, 1.0)
    z = np.where(m, e / gs, 0.0)
    crps = gs * (z * (2 * phi_cdf(z) - 1) + 2 * np.exp(-0.5 * z * z) / math.sqrt(2 * math.pi) - 1 / math.sqrt(math.pi))
    nll = 0.5 * np.log(2 * math.pi * gs ** 2) + 0.5 * z * z
    n = e.shape[0]
    f = lambda a: np.where(m, a, 0.0).reshape(n, -1).sum(1)
    return np.stack([m.reshape(n, -1).sum(1), f(e <= g), f(e <= 2 * g), f(crps), f(nll), f(2 * gs)], 1).astype(np.float64)


def main():
    os.chdir(C.ROOT)
    t0 = time.perf_counter()
    cache = {e: TD3.episode_rollout(e) for e in X7.EPISODES}
    res, n_traj, order = X7.reading(cache)
    x7 = json.load(open(os.path.join(R.RESULTS, "x7_loeo_recalibration.json")))
    g, al = res["epistemic"], x7["alongside"]
    dcov = dc = 0.0
    for h in map(str, HS):
        for got, want in ((g["per_horizon"][h], x7["reading"]["per_horizon"][h]),
                          (g["constant_multiplier"]["per_horizon"][h], al["epistemic_constant_multiplier"]["per_horizon"][h]),
                          (g["before_any_multiplier"][h], al["epistemic_before_any_multiplier"][h])):
            dcov = max(dcov, abs(got["coverage"] - want["coverage"]), *(abs(a - b) for a, b in zip(got["ci95"], want["ci95"])))
        for e in X7.EPISODES:
            w = al["epistemic_c_spread_across_folds"][h]["per_fold"][str(e)]
            dc = max(dc, abs(g["c_spread_across_folds"][h]["per_fold"][str(e)] - w) / abs(w))
    for e in X7.EPISODES:
        w = al["epistemic_constant_multiplier"]["c_per_fold"][str(e)]
        dc = max(dc, abs(g["constant_multiplier"]["c_per_fold"][str(e)] - w) / abs(w))
    A = {"coverage_and_interval": {"pass": bool(dcov <= TOL_COV), "max_abs_diff": dcov, "tolerance": TOL_COV},
         "multipliers": {"pass": bool(dc <= TOL_C), "max_rel_diff": dc, "tolerance": TOL_C},
         "against": "results/x7_loeo_recalibration.json reading.per_horizon, alongside.epistemic_constant_multiplier, "
                    "alongside.epistemic_before_any_multiplier, alongside.epistemic_c_spread_across_folds"}
    print(f"  assertions: coverage {dcov:.1e}, multipliers {dc:.1e}")
    if not (A["coverage_and_interval"]["pass"] and A["multipliers"]["pass"]):
        C.blocked(OUT, "a reproduction assertion failed", assertions=A)

    draws = np.random.default_rng(X7.BOOT_SEED).integers(0, len(order), (X7.N_BOOT, len(order)))
    out_q = {}
    for q, k in X7.QUANT.items():
        rq = res[q]
        tab = {}
        for h in HS:
            hk = str(h)
            row = {}
            for name in ("before", "constant", "per_horizon"):
                S = []
                for e in X7.EPISODES:
                    c = {"before": 1.0, "constant": rq["constant_multiplier"]["c_per_fold"][str(e)],
                         "per_horizon": rq["c_spread_across_folds"][hk]["per_fold"][str(e)]}[name]
                    S.append(sums(cache[e][0], cache[e][k], c, h))
                S = np.concatenate(S, 0)                          # (20, 6) in X7's order
                pooled = S.sum(0)
                v = lambda P: {"cov1": P[1] / P[0], "cov2": P[2] / P[0], "crps": P[3] / P[0], "nll": P[4] / P[0],
                               "width": P[5] / P[0]}
                pt = v(pooled)
                B = S[draws].sum(1)                               # (20000, 6)
                bd = v(B.T)
                ci = {kk: [float(np.percentile(bd[kk], 2.5)), float(np.percentile(bd[kk], 97.5))] for kk in pt}
                row[name] = {kk: float(vv) for kk, vv in pt.items()}
                row[name]["ci95"] = ci
                row[name]["n_valid"] = int(pooled[0])
            tab[hk] = row
        out_q[q] = tab
    out = {"analysis": "N9", "post_hoc": True,
           "never_reopens": "X7 (M-89, M-92), M-69, M-70 or any discharged rule; nothing here changes a verdict",
           "script": "scripts/n9_recalibration_scores.py", "script_sha256": C.sha256("scripts/n9_recalibration_scores.py"),
           "design": {"model": "the released checkpoint, ensemble of 5, as X7", "fit": "X7's reading(), unchanged",
                      "calibrations": ["before (multiplier 1)", "constant (X7's cc[e], fitted at h = 1)",
                                       "per-horizon (X7's c_fold[e][h])"],
                      "pooling": "ratio of sums over the ten held-out episodes' 20 trajectories",
                      "interval": f"X7's draw matrix: default_rng({X7.BOOT_SEED}).integers(0, 20, ({X7.N_BOOT}, 20))",
                      "units": "CRPS and width in normalised-state units; NLL in nats per (step, dimension)",
                      "specification": "docs/presubmission/round5/PROTOCOLS.md §5 N9"},
           "assertions": A, "scores": out_q,
           "caveat": "unseen by the multiplier, not by the model: as X7, the released checkpoint may have trained on all ten episodes (PREMISES P20)",
           "code_sha256": {p: C.sha256(p) for p in MODULES},
           "git_head": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
           "timing": {"wall_clock_s": time.perf_counter() - t0, "torch_threads": torch.get_num_threads(),
                      "cpu_count": os.cpu_count()}}
    json.dump(out, open(OUT, "w"), indent=1)
    for h in ("1", "100", "368"):
        r = out_q["epistemic"][h]
        print("  h=%s " % h + "  ".join(f"{n}: cov1 {100 * r[n]['cov1']:.1f} cov2 {100 * r[n]['cov2']:.1f} crps {r[n]['crps']:.4f} "
                                         f"nll {r[n]['nll']:.2f} w {r[n]['width']:.3f}" for n in ("before", "constant", "per_horizon")))
    print(f"  wrote {R.rel(OUT)}")


if __name__ == "__main__":
    main()
