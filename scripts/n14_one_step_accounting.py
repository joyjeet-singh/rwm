"""
N14 (round 5; POST HOC, optional) -- how much one-step error the ensemble can account for. docs/presubmission/round5/
PROTOCOLS.md §5 N14 is the specification; this is a summary. Descriptive; it re-opens no rule.

At forecast step 1 (h = 1), K members: E[e^2] = mean over (trajectory, dimension) of (members' mean - truth)^2; E[s^2] = the
mean across-member sample variance (ddof = 1); R = E[e^2] / ((1 + 1/K) E[s^2]). R = 1 if the truth behaves like one more draw
from the members' spread; R > 1 if the ensemble accounts for less of the error than that. Models: the ensemble-5 arms (seeds
0-2, held-out pair; per seed and seed mean), the independent ensemble (K = 5 and K = 3, held-out pair) and the released
checkpoint (all ten episodes; in-sample for it only if it trained on this recording, PREMISES P20). Full 400-step rollouts
through the existing functions, then index START. Interval: whole trajectories, 20,000 draws, default_rng(0), R recomputed in
each draw as a ratio of means.
ASSERTION, first: at h = 1, rho and +-1 sigma coverage reproduce task_d3_ens5.json, r2_independent_ensemble.json and
task_d_nind20.json within 1e-6 relative.
Writes results/n14_one_step_accounting.json. Run from the repository root.
"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import torch  # noqa: E402
import rwm_data as R  # noqa: E402
import r2_independent_ensemble as R2  # noqa: E402
import x9_per_member_propagation as X9  # noqa: E402
import x11_common as C  # noqa: E402

OUT = os.path.join(R.RESULTS, "n14_one_step_accounting.json")
START, N_BOOT, TOL = X9.START, 20000, 1e-6
J = lambda n: json.load(open(os.path.join(R.RESULTS, n)))
MODULES = ("scripts/n14_one_step_accounting.py", "scripts/x9_per_member_propagation.py", "scripts/r2_independent_ensemble.py",
           "scripts/x11_common.py", "src/score_reference.py")


def parts(r):
    """r: a MEAN rollout dict from X9 (pred, err, s). Per trajectory: mean squared error and mean across-member variance at step 1."""
    e = (r["pred"][:, START] - r["st"][:, START]).numpy().astype(np.float64)
    s2 = r["s"][:, START] ** 2
    return (e ** 2).mean(1), s2.mean(1)


def ratio(e2, s2, K, idx=None):
    if idx is None:
        return float(e2.mean() / ((1 + 1 / K) * s2.mean()))
    return e2[idx].mean(1) / ((1 + 1 / K) * s2[idx].mean(1))


def main():
    os.chdir(C.ROOT)
    t0 = time.perf_counter()
    s20, s4, _ = X9.arenas()
    st20, ac20 = C.tensors(s20)
    st4, ac4 = C.tensors(s4)
    rel = X9.mean_shared(X9.released(), st20, ac20); rel["st"] = st20
    e5 = {}
    for s in C.ENS5_SEEDS:
        e5[s] = X9.mean_shared(C.load_ens5(C.ens5_weights((1, 8), s))[0], st4, ac4); e5[s]["st"] = st4
    ind_m = [C.load_single(C.single_weights((1, 8), s)) for s in C.SINGLE_SEEDS]
    ind = X9.mean_indep(ind_m, st4, ac4); ind["st"] = st4
    ind3 = X9.mean_indep(ind_m[:3], st4, ac4); ind3["st"] = st4
    # assertion: h = 1 rho and coverage
    d = 0.0
    rel_ = lambda a, b: abs(a - b) / max(1e-12, abs(b))
    w = J("task_d_nind20.json")["d1_by_horizon"]["1"]["epistemic"]
    b = R2.block(rel["err"], rel["s"], slice(START, START + 1))
    d = max(d, rel_(b["ratio_err_over_sigma"], w["ratio_err_over_sigma"]), rel_(b["coverage_pm1"], w["coverage_pm1"]))
    cal = J("task_d3_ens5.json")["calibration"]["1"]["per_seed"]
    for j, s in enumerate(C.ENS5_SEEDS):
        b = R2.block(e5[s]["err"], e5[s]["s"], slice(START, START + 1))
        d = max(d, rel_(b["ratio_err_over_sigma"], cal[j]["ratio_err_over_sigma"]), rel_(b["coverage_pm1"], cal[j]["coverage_pm1"]))
    wi = J("r2_independent_ensemble.json")["independent"]["1"]
    b = R2.block(ind["err"], ind["s"], slice(START, START + 1))
    d = max(d, rel_(b["ratio_err_over_sigma"], wi["ratio_err_over_sigma"]), rel_(b["coverage_pm1"], wi["coverage_pm1"]))
    A = {"h1_reproduction": {"pass": bool(d <= TOL), "max_rel_diff": d, "tolerance": TOL,
                             "against": ["results/task_d_nind20.json d1_by_horizon.1.epistemic",
                                         "results/task_d3_ens5.json calibration.1.per_seed",
                                         "results/r2_independent_ensemble.json independent.1"]}}
    print(f"  assertion h1_reproduction: {'PASS' if A['h1_reproduction']['pass'] else 'FAIL'} {d}")
    if not A["h1_reproduction"]["pass"]:
        C.blocked(OUT, "the reproduction assertion failed", assertions=A)
    out_m = {}

    def one(name, rs, K):
        P = [parts(r) for r in rs]
        n = len(P[0][0])
        dr = np.random.default_rng(0).integers(0, n, (N_BOOT, n))
        # the seed mean of the per-seed ratios, recomputed in each draw (one seed: that seed's ratio)
        v = np.mean([ratio(e2, s2, K, dr) for e2, s2 in P], 0)
        out_m[name] = {"K": K, "n_trajectories": n, "E_e2": float(np.mean([e2.mean() for e2, _ in P])),
                       "E_s2": float(np.mean([s2.mean() for _, s2 in P])),
                       "R": float(np.mean([ratio(e2, s2, K) for e2, s2 in P])),
                       "R_ci": [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))],
                       "per_seed_R": ([ratio(e2, s2, K) for e2, s2 in P] if len(P) > 1 else None)}
    one("e5", [e5[s] for s in C.ENS5_SEEDS], 5)
    one("ind", [ind], 5)
    one("ind3", [ind3], 3)
    one("rel", [rel], 5)
    out = {"analysis": "N14", "post_hoc": True, "descriptive": True, "optional": True,
           "never_reopens": "M-44, M-65 or any rule; nothing here changes a verdict",
           "script": "scripts/n14_one_step_accounting.py", "script_sha256": C.sha256("scripts/n14_one_step_accounting.py"),
           "design": {"statistic": "R = E[e^2] / ((1 + 1/K) E[s^2]) at forecast step 1",
                      "seed_pooling": "e5: the mean over seeds of each seed's R, recomputed in each draw",
                      "arenas": {"e5": "held-out pair, 4", "ind": "held-out pair, 4", "ind3": "held-out pair, 4",
                                 "rel": "all ten episodes, 20 (PREMISES P20)"},
                      "specification": "docs/presubmission/round5/PROTOCOLS.md §5 N14"},
           "assertions": A, "models": out_m,
           "code_sha256": {p: C.sha256(p) for p in MODULES},
           "git_head": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
           "timing": {"wall_clock_s": time.perf_counter() - t0, "torch_threads": torch.get_num_threads(), "cpu_count": os.cpu_count()}}
    json.dump(out, open(OUT, "w"), indent=1)
    for k, v in out_m.items():
        print(f"  {k}: R = {v['R']:.3f} {v['R_ci']}  (K = {v['K']}, n = {v['n_trajectories']})")
    print(f"  wrote {R.rel(OUT)}")


if __name__ == "__main__":
    main()
