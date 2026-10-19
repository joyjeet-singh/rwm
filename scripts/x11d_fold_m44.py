"""
Rule X11d (round 5; PRE-REGISTERED, exploratory) -- M-44's comparison of an ensemble of independently trained
models with the shared-trunk ensemble, on X3's five folds, n_independent = 20.

It never re-opens M-44 (MECHANISM SUPPORTED, at n = 4) or M-49 or M-68; nothing here changes a verdict.
PROTOCOLS.md §4 holds the rule.

MODELS, per fold: the independent ensemble is that fold's five Arm A single models, seeds 0-4, 2,500 iterations
(X3's seeds 0-2 and X11's seeds 3-4; runs/armA_seed<s> for {1, 8}); the shared trunk is that fold's three
ensemble-5 arms (as X11a). ARENA: each fold's four held-out trajectories, one batch of 4 per fold, pooled to 20.
Rollouts: r2_independent_ensemble.rollout_independent (every member keeps its own recurrent state; the ensemble
mean is fed back to all) and ReferenceRWM.rollout_uncertainty, both at action_offset = 1.

STATISTICS, THRESHOLDS AND BRANCHES copied from r2_independent_ensemble.py:211-389 with only the arena changed:
per horizon, the independent ensemble's and each shared-trunk seed's rho, coverage and spread (block()); at the
deployment horizon (results/v2_deployment_horizon.json, h = 100), per shared-trunk seed, the log ratio of
overconfidence factors and the +-1 sigma coverage difference, each with a paired cluster-bootstrap interval
(cboot_paired, default_rng(100 + s) and default_rng(200 + s), 20,000 draws, now over 20 trajectories); the
decomposition of the improvement into spread and accuracy; and M-44's verdict, every condition against every
shared-trunk seed: MECHANISM SUPPORTED iff the independent ensemble's overconfidence is lower, its interval
excludes zero, the improvement is at least the MDE ratio, its coverage is higher, that interval excludes zero, and
the shift is at least the MDE in points; UNRESOLVABLE if the two quantities disagree in direction; MECHANISM NOT
SUPPORTED otherwise. The MDE thresholds are M-44's committed ones, 1.45x and 2.26 points (r2_independent_ensemble.py:
50-51), unchanged. Alongside, not a reading: the label the same conditions would give against the n = 20 MDE in
results/x11_power.json (m44.n20.binding_cross_architecture), computed in GT1 before any fold run existed.

ASSERTIONS (before any reading): (a) every ensemble-5 and single-model record trained on its fold's complement at
the queued size with finite losses; (b) this code on fold {1, 8} alone reproduces
results/r2_independent_ensemble.json (independent, shared_trunk, comparison, decomposition and every m44 field
this code computes) within 1e-12.

  --assert-only   (b) only; writes docs/presubmission/round5/gt1_x11d_assert.json.
Writes results/x11d_fold_m44.json. Run from the repository root.
"""
import argparse
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
import x11_common as C  # noqa: E402
import x11a_fold_ens5_calibration as XA  # noqa: E402

RULE = "X11d"
RULE_ID = "M-100"
FROZEN = ('scripts/x11d_fold_m44.py', 'scripts/x11a_fold_ens5_calibration.py', 'scripts/x11_common.py')
HORIZONS, START, TOL_REPRO = R2.HORIZONS, C.START, 1e-12
MDE_RATIO, MDE_COV = R2.MDE_RATIO, R2.MDE_COV_PTS
OUT = os.path.join(R.RESULTS, "x11d_fold_m44.json")
ASSERT_OUT = os.path.join(C.ROOT, "docs", "presubmission", "round5", "gt1_x11d_assert.json")
MODULES = ("scripts/x11d_fold_m44.py", "scripts/x11a_fold_ens5_calibration.py", "scripts/x11_common.py",
           "scripts/r2_independent_ensemble.py", "scripts/x3_cross_fold.py", "src/score_reference.py",
           "src/rwm_data.py", "src/rwm_metrics.py", "src/rollout_eval.py")


def roll_fold(f):
    ar = C.arena(f)
    models = [C.load_single(C.single_weights(f, s)) for s in C.SINGLE_SEEDS]
    pred, _, epi, _, _ = R2.rollout_independent(models, ar["st"].clone(), ar["ac"])
    ind = {"err": (pred - ar["st"]).abs().numpy().astype(np.float64), "epi": epi.numpy().astype(np.float64)}
    shared = {}
    for s in C.ENS5_SEEDS:
        m, _ = C.load_ens5(C.ens5_weights(f, s))
        p, _, e, _, _ = m.rollout_uncertainty(ar["st"].clone(), ar["ac"], START, action_offset=1)
        shared[s] = {"err": (p - ar["st"]).abs().numpy().astype(np.float64), "epi": e.numpy().astype(np.float64)}
    return ar, ind, shared


def compare(err_i, epi_i, shared, n_traj, mde_ratio, mde_cov):
    """r2_independent_ensemble.py:211-389 (table, paired comparison, decomposition, verdict), printing removed."""
    out = {"independent": {}, "shared_trunk": {}}
    for h in HORIZONS:
        sl = slice(START, START + h)
        bi = R2.block(err_i, epi_i, sl)
        bs = [R2.block(shared[s]["err"], shared[s]["epi"], sl) for s in C.ENS5_SEEDS]
        out["independent"][str(h)] = bi
        out["shared_trunk"][str(h)] = {
            "per_seed": {str(s): b for s, b in zip(C.ENS5_SEEDS, bs)},
            "mean_ratio": float(np.mean([b["ratio_err_over_sigma"] for b in bs])),
            "mean_cov1": float(np.mean([b["coverage_pm1"] for b in bs])),
            "mean_cov2": float(np.mean([b["coverage_pm2"] for b in bs]))}
    DEPLOY = json.load(open(os.path.join(R.RESULTS, "v2_deployment_horizon.json")))["verdict"]["deployment_horizon_is"]
    sl = slice(START, START + DEPLOY)

    def rho(e, g, i):
        ms = np.nanmean(g[i, sl])
        return float(np.nanmean(e[i, sl]) / ms) if ms > 0 else np.nan

    def cov(e, g, i):
        return float(np.nanmean(e[i, sl] <= g[i, sl]))

    per_pair = {}
    for s in C.ENS5_SEEDS:
        es, gs = shared[s]["err"], shared[s]["epi"]
        full = np.arange(n_traj)
        lr = float(np.log(rho(err_i, epi_i, full) / rho(es, gs, full)))
        dc = 100 * (cov(err_i, epi_i, full) - cov(es, gs, full))
        lo1, hi1, _ = R2.cboot_paired(lambda i: np.log(rho(err_i, epi_i, i) / rho(es, gs, i)), n_traj,
                                      np.random.default_rng(100 + s))
        lo2, hi2, _ = R2.cboot_paired(lambda i: 100 * (cov(err_i, epi_i, i) - cov(es, gs, i)), n_traj,
                                      np.random.default_rng(200 + s))
        plr = [float(np.log(rho(err_i, epi_i, [t]) / rho(es, gs, [t]))) for t in range(n_traj)]
        pdc = [float(100 * (cov(err_i, epi_i, [t]) - cov(es, gs, [t]))) for t in range(n_traj)]
        per_pair[str(s)] = {
            "log_ratio_per_trajectory": plr, "ratio_per_trajectory": [float(np.exp(x)) for x in plr],
            "coverage_diff_pts_per_trajectory": pdc,
            "log_ratio": lr, "ratio": float(np.exp(lr)), "log_ratio_ci": [lo1, hi1],
            "ratio_ci": [float(np.exp(lo1)), float(np.exp(hi1))],
            "ratio_excludes_zero": bool(hi1 < 0 or lo1 > 0), "ratio_improves": bool(lr < 0),
            "ratio_beats_mde": bool(np.exp(-lr) >= mde_ratio),
            "coverage_diff_pts": dc, "coverage_ci_pts": [lo2, hi2],
            "coverage_excludes_zero": bool(lo2 > 0 or hi2 < 0), "coverage_improves": bool(dc > 0),
            "coverage_beats_mde": bool(abs(dc) >= mde_cov)}
    decomp = {}
    for h in HORIZONS:
        i = out["independent"][str(h)]
        sd_ = out["shared_trunk"][str(h)]["per_seed"].values()
        se = float(np.mean([x["mean_abs_err"] for x in sd_]))
        ss = float(np.mean([x["mean_sigma"] for x in sd_]))
        sig_r, err_r = i["mean_sigma"] / ss, se / i["mean_abs_err"]
        tot = sig_r * err_r
        lt = np.log(tot)
        decomp[str(h)] = {"sigma_ratio_indep_over_shared": sig_r, "error_ratio_shared_over_indep": err_r,
                          "total_rho_improvement": float(tot),
                          "share_from_sigma": float(np.log(sig_r) / lt) if lt > 0 else None,
                          "share_from_accuracy": float(np.log(err_r) / lt) if lt > 0 else None,
                          "indep_mean_sigma": i["mean_sigma"], "shared_mean_sigma": ss,
                          "indep_mean_abs_err": i["mean_abs_err"], "shared_mean_abs_err": se}
    out["decomposition"] = decomp
    out["comparison"] = {"horizon": DEPLOY, "per_shared_seed": per_pair}
    out["m44"] = verdict(per_pair, mde_ratio, mde_cov)
    out["m44"]["horizon"] = DEPLOY
    return out


def verdict(per_pair, mde_ratio, mde_cov):
    """r2_independent_ensemble.py:348-389, M-44's branch only."""
    P = list(per_pair.values())
    ratio_better = all(p["ratio_improves"] for p in P)
    ratio_excl = all(p["ratio_excludes_zero"] for p in P)
    ratio_mde = all(p["ratio_beats_mde"] for p in P)
    cov_better = all(p["coverage_improves"] for p in P)
    cov_excl = all(p["coverage_excludes_zero"] for p in P)
    cov_mde = all(p["coverage_beats_mde"] for p in P)
    supported = ratio_better and ratio_excl and ratio_mde and cov_better and cov_excl and cov_mde
    unresolvable = (ratio_better != cov_better) and not supported
    v = ("MECHANISM SUPPORTED" if supported
         else "UNRESOLVABLE — the two quantities disagree in direction" if unresolvable
         else "MECHANISM NOT SUPPORTED")
    return {"conditions": {"overconfidence_lower_in_all": ratio_better,
                           "overconfidence_interval_excludes_zero_in_all": ratio_excl,
                           "overconfidence_improvement_at_least_mde": ratio_mde,
                           "coverage_higher_in_all": cov_better,
                           "coverage_interval_excludes_zero_in_all": cov_excl,
                           "coverage_shift_at_least_mde": cov_mde},
            "mde_ratio": mde_ratio, "mde_coverage_pts": mde_cov,
            "supported": supported, "unresolvable": unresolvable, "verdict": v,
            "mean_ratio_improvement": float(np.exp(-np.mean([p["log_ratio"] for p in P]))),
            "mean_coverage_gain_pts": float(np.mean([p["coverage_diff_pts"] for p in P]))}


def assert_fold18():
    ar, ind, shared = roll_fold((1, 8))
    got = compare(ind["err"], ind["epi"], shared, 4, MDE_RATIO, MDE_COV)
    want = json.load(open(os.path.join(R.RESULTS, "r2_independent_ensemble.json")))
    d = max(XA.max_diff(got[k], want[k]) for k in ("independent", "shared_trunk", "comparison", "decomposition"))
    d = max(d, XA.max_diff(got["m44"], {k: want["m44"][k] for k in got["m44"]}))
    return {"b": {"pass": bool(d <= TOL_REPRO), "max_abs_diff": d, "tolerance": TOL_REPRO,
                  "against": "results/r2_independent_ensemble.json"}}


def reading():
    t0 = time.perf_counter()
    frozen = C.require_prereg(RULE_ID, FROZEN, OUT)
    bad = {}
    for f in C.FOLDS:
        for s in C.ENS5_SEEDS:
            b = C.check_record(C.ens5_record(f, s), f, 5)
            if b:
                bad[f"e5_{C.fid(f)}_s{s}"] = b
        for s in C.SINGLE_SEEDS:
            b = C.check_record(C.single_record(f, s), f, 1)
            if b:
                bad[f"single_{C.fid(f)}_s{s}"] = b
    if bad:
        C.blocked(OUT, "assertion (a): a run record is wrong", problems=bad)
    a18 = assert_fold18()
    if not a18["b"]["pass"]:
        C.blocked(OUT, "assertion (b) failed", b=a18["b"])
    inds, shs, order, sha = [], {s: [] for s in C.ENS5_SEEDS}, [], {}
    for f in C.FOLDS:
        for s in C.SINGLE_SEEDS:
            sha[f"single_{C.fid(f)}_s{s}"] = C.sha256(C.single_weights(f, s))
        for s in C.ENS5_SEEDS:
            sha[f"e5_{C.fid(f)}_s{s}"] = C.sha256(C.ens5_weights(f, s))
        ar, ind, shared = roll_fold(f)
        order += [{"fold": C.fid(f), "start_row": a, "episode": b} for a, b in zip(ar["starts"], ar["episode"])]
        if not (np.isfinite(ind["err"][:, START:]).all() and np.isfinite(ind["epi"][:, START:]).all()
                and ind["epi"][:, START:].mean() > 0):
            C.blocked(OUT, f"independent rollout non-finite or zero spread, fold {C.fid(f)}")
        inds.append(ind)
        for s in C.ENS5_SEEDS:
            shs[s].append(shared[s])
    err_i = np.concatenate([x["err"] for x in inds], 0)
    epi_i = np.concatenate([x["epi"] for x in inds], 0)
    shared = {s: {k: np.concatenate([x[k] for x in shs[s]], 0) for k in ("err", "epi")} for s in C.ENS5_SEEDS}
    res = compare(err_i, epi_i, shared, 20, MDE_RATIO, MDE_COV)
    pw = json.load(open(os.path.join(R.RESULTS, "x11_power.json")))["m44"]["n20"]["binding_cross_architecture"]
    rescored = {s: {**p, "ratio_beats_mde": bool(np.exp(-p["log_ratio"]) >= pw["ratio_mde_multiplicative"]),
                    "coverage_beats_mde": bool(abs(p["coverage_diff_pts"]) >= pw["coverage_mde_pts"])}
                for s, p in res["comparison"]["per_shared_seed"].items()}
    alt = verdict(rescored, pw["ratio_mde_multiplicative"], pw["coverage_mde_pts"])
    out = {"rule": RULE, "ledger": RULE_ID, "frozen_sha256": frozen, "script": "scripts/x11d_fold_m44.py", "script_sha256": C.sha256("scripts/x11d_fold_m44.py"),
           "exploratory": True, "never_reopens": "M-44, M-49, M-68 or any discharged rule; nothing here changes a verdict",
           "design": {"folds": [list(f) for f in C.FOLDS], "independent_seeds": list(C.SINGLE_SEEDS),
                      "shared_trunk_seeds": list(C.ENS5_SEEDS), "n_trajectories": 20, "n_independent": 20,
                      "trajectories": order, "n_boot": R2.N_BOOT, "mde_ratio": MDE_RATIO, "mde_coverage_pts": MDE_COV,
                      "mde_source": "M-44's committed thresholds (r2_independent_ensemble.py:50-51)",
                      "copied_from": "scripts/r2_independent_ensemble.py:211-389; arena changed only",
                      "design_limitation": json.load(open(os.path.join(R.RESULTS, "r2_independent_ensemble.json")))["m44"]["design_limitation"]},
           "assertions": {"a": {"pass": True}, **a18}, **res,
           "alongside": {"status": "alongside, not a reading",
                         "label_under_n20_mde": alt["verdict"], "n20_mde": pw, "conditions": alt["conditions"]},
           "weights_sha256": sha, "code_sha256": {p: C.sha256(p) for p in MODULES},
           "git_head": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
           "timing": {"wall_clock_s": time.perf_counter() - t0, "torch_threads": torch.get_num_threads(),
                      "cpu_count": os.cpu_count()}}
    json.dump(out, open(OUT, "w"), indent=1)
    print(f"  X11d: {res['m44']['verdict']} (mean ratio improvement {res['m44']['mean_ratio_improvement']:.3f}x, "
          f"coverage gain {res['m44']['mean_coverage_gain_pts']:+.2f} pts)")
    print(f"  wrote {R.rel(OUT)}")


def main():
    os.chdir(C.ROOT)
    ap = argparse.ArgumentParser()
    ap.add_argument("--assert-only", action="store_true")
    args = ap.parse_args()
    if args.assert_only:
        a = assert_fold18()
        json.dump({"rule": RULE, "script_sha256": C.sha256("scripts/x11d_fold_m44.py"), **a},
                  open(ASSERT_OUT, "w"), indent=1)
        for k, v in a.items():
            print(f"  assertion {k}: {'PASS' if v['pass'] else 'FAIL'} (max diff {v['max_abs_diff']})")
        sys.exit(0 if all(v["pass"] for v in a.values()) else 1)
    reading()


if __name__ == "__main__":
    main()
