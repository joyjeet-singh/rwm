"""
Rule X11c (round 5; PRE-REGISTERED, exploratory) -- the per-horizon recalibration on episodes the model never saw:
task_d3_perhorizon.py's "fit on one held-out episode, score on the other" protocol, applied to each X3 fold's
ensemble-5 arms on that fold's own held-out pair, and pooled over the five folds.

It never re-opens a discharged rule (M-69, M-70, M-89 or the D3 per-horizon reading), and nothing here changes a
verdict. PROTOCOLS.md §4 holds the rule.

MODELS: as X11a. ROLLOUTS: task_d3_perhorizon.episode_rollout (lines 44-56) with the model as an argument, one
batch per episode (its two trajectories), action_offset = 1.

STATISTICS, THRESHOLDS AND BRANCHES copied from task_d3_perhorizon.py:85-127 with only the arena changed: for each
fold, seed, quantity (aleatoric, epistemic) and direction (fit on one held-out episode, score on the other), the
per-horizon scalar c(h) = fit_scalar(fit episode, h) and the constant c = fit_scalar(fit episode, 1), each scored
by cover() on the other episode, beside the coverage before any scalar. A cell is calibrated iff its coverage is
within 0.10 of 68.27%. Per quantity, over all cells (5 folds x 2 directions x 6 horizons x 3 seeds = 180):
the per-horizon scalar RESTORES CALIBRATION iff every cell is calibrated (task_d3_perhorizon's
`per_horizon_restores_calibration`); the count of calibrated cells is reported for both scalars. The epistemic
quantity governs (as M-89). Alongside, not a reading: per seed and horizon, the coverage pooled over the ten test
episodes (20 trajectories) with a 95% interval (20,000 draws of the 20 trajectories, default_rng(0); seeds pooled
inside each draw for the seed-pooled row) and X7's band labels (WITHIN BAND if the interval lies in
[58.27%, 78.27%], OUTSIDE BAND if it misses it, UNRESOLVED otherwise).

ASSERTIONS (before any reading): (a) as X11a; (b) the released checkpoint on fold {1, 8} through this code
reproduces results/task_d3_perhorizon.json `quantities` (fits, constant_fits, verdict) within 1e-9, a scalar c
relative to max(1, |c|) (x7_loeo_recalibration.py's TOL_A).

  --assert-only   (b) only; writes docs/presubmission/round5/gt1_x11c_assert.json.
Writes results/x11c_fold_recalibration.json. Run from the repository root.
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
import rwm_metrics as MET  # noqa: E402
import score_reference as S  # noqa: E402
import task_d3_perhorizon as TD3  # noqa: E402
import task_d3_cross_model as CM  # noqa: E402
import x11_common as C  # noqa: E402

RULE = "X11c"
RULE_ID = "M-99"
FROZEN = ('scripts/x11c_fold_recalibration.py', 'scripts/x11_common.py')
HORIZONS, TARGET, TOL = TD3.HORIZONS, TD3.TARGET, 0.10
START, N_BOOT, TOL_A = C.START, 20000, 1e-9
LO, HI = TARGET - CM.TOL, TARGET + CM.TOL
BAND_LABELS = ("WITHIN BAND", "OUTSIDE BAND", "UNRESOLVED")
OUT = os.path.join(R.RESULTS, "x11c_fold_recalibration.json")
ASSERT_OUT = os.path.join(C.ROOT, "docs", "presubmission", "round5", "gt1_x11c_assert.json")
MODULES = ("scripts/x11c_fold_recalibration.py", "scripts/x11_common.py", "scripts/task_d3_perhorizon.py",
           "scripts/task_d3_cross_model.py", "scripts/x3_cross_fold.py", "src/score_reference.py",
           "src/rwm_data.py", "src/rwm_metrics.py", "src/rollout_eval.py")


def episode_rollout(m, episode):
    """task_d3_perhorizon.py:44-56 with the model as an argument."""
    cfg, data, ep = C.data()
    starts = MET.non_overlapping_starts(ep, [episode], C.LEN)
    st, ac = C.tensors(starts)
    pred, alea, epi, _, _ = m.rollout_uncertainty(st.clone(), ac, START, action_offset=1)
    return ((pred - st).abs().numpy().astype(np.float64),
            alea.numpy().astype(np.float64), epi.numpy().astype(np.float64), len(starts))


def recal(cache, hold):
    """task_d3_perhorizon.py:85-127 (the two quantities' fits and verdicts), verbatim but for the printing."""
    out = {}
    for qi, qname in ((2, "aleatoric"), (3, "epistemic")):
        rec = {"fits": [], "constant_fits": []}
        for fit_ep in hold:
            test_ep = [e for e in hold if e != fit_ep][0]
            fe, fa, fp, _ = cache[fit_ep]
            te, ta, tp, _ = cache[test_ep]
            fsig = fa if qname == "aleatoric" else fp
            tsig = ta if qname == "aleatoric" else tp
            c_const = TD3.fit_scalar(fe, fsig, 1)
            for h in HORIZONS:
                c_h = TD3.fit_scalar(fe, fsig, h)
                rec["fits"].append({"fit_episode": fit_ep, "test_episode": test_ep, "h": h, "c": c_h,
                                    "coverage_after": TD3.cover(te, tsig, c_h, h),
                                    "coverage_before": TD3.cover(te, tsig, 1.0, h)})
                rec["constant_fits"].append({"fit_episode": fit_ep, "test_episode": test_ep, "h": h, "c": c_const,
                                             "coverage_after": TD3.cover(te, tsig, c_const, h)})
        ok = [abs(f["coverage_after"] - TARGET) < TOL for f in rec["fits"]]
        okc = [abs(f["coverage_after"] - TARGET) < TOL for f in rec["constant_fits"]]
        worst = max(rec["fits"], key=lambda f: abs(f["coverage_after"] - TARGET))
        spread = [f["c"] for f in rec["fits"]]
        rec["verdict"] = {"per_horizon_cells_calibrated": int(sum(ok)), "n_cells": len(ok),
                          "constant_cells_calibrated": int(sum(okc)),
                          "per_horizon_restores_calibration": bool(all(ok)), "worst_cell": worst,
                          "c_ratio_max_over_min": float(max(spread) / min(spread)), "tolerance": TOL}
        out[qname] = rec
    return out


def rel_diff(got, want):
    if isinstance(want, dict):
        return max([rel_diff(got.get(k) if isinstance(got, dict) else None, v) for k, v in want.items()] or [0.0])
    if isinstance(want, list):
        if not isinstance(got, list) or len(got) != len(want):
            return float("inf")
        return max([rel_diff(g, w) for g, w in zip(got, want)] or [0.0])
    if isinstance(want, (bool, str)) or want is None:
        return 0.0 if got == want else float("inf")
    if not isinstance(got, (int, float)):
        return float("inf")
    return abs(float(got) - float(want)) / max(1.0, abs(float(want)))


def assert_fold18():
    sd = torch.load(R.repo_paths()["ckpt"], map_location="cpu")["system_dynamics_state_dict"]
    m = S.ReferenceRWM(sd)
    m.eval()
    want = json.load(open(os.path.join(R.RESULTS, "task_d3_perhorizon.json")))
    hold = list(want["holdout_episodes"])
    assert hold == [1, 8], hold
    got = recal({e: episode_rollout(m, e) for e in hold}, hold)
    d = rel_diff(got, want["quantities"])
    return {"b": {"pass": bool(d <= TOL_A), "max_abs_diff": d, "tolerance": TOL_A,
                  "against": "results/task_d3_perhorizon.json quantities (released checkpoint, fold {1, 8})"}}


def band(ci):
    if LO <= ci[0] and ci[1] <= HI:
        return BAND_LABELS[0]
    if ci[1] < LO or ci[0] > HI:
        return BAND_LABELS[1]
    return BAND_LABELS[2]


def reading():
    t0 = time.perf_counter()
    frozen = C.require_prereg(RULE_ID, FROZEN, OUT)
    bad = {f"{C.fid(f)}_s{s}": C.check_record(C.ens5_record(f, s), f, 5) for f in C.FOLDS for s in C.ENS5_SEEDS}
    bad = {k: v for k, v in bad.items() if v}
    if bad:
        C.blocked(OUT, "assertion (a): a run record is wrong", problems=bad)
    a18 = assert_fold18()
    if not a18["b"]["pass"]:
        C.blocked(OUT, "assertion (b) failed", b=a18["b"])
    per, sha = {}, {}
    # per-trajectory (covered, valid) counts for the pooled alongside: [quantity][scalar][h][seed] -> lists over test eps
    pool = {q: {k: {h: {s: ([], []) for s in C.ENS5_SEEDS} for h in HORIZONS} for k in ("per_horizon", "constant", "before")}
            for q in ("aleatoric", "epistemic")}
    order = []
    for f in C.FOLDS:
        hold = sorted(f)
        for s in C.ENS5_SEEDS:
            w = C.ens5_weights(f, s)
            sha[f"{C.fid(f)}_s{s}"] = C.sha256(w)
            m, _ = C.load_ens5(w)
            cache = {e: episode_rollout(m, e) for e in hold}
            for e in hold:
                if cache[e][3] != 2:
                    C.blocked(OUT, f"episode {e} has {cache[e][3]} trajectories, not 2")
                if not all(np.isfinite(x[:, START:]).all() for x in cache[e][:3]):
                    C.blocked(OUT, f"non-finite rollout, fold {C.fid(f)} seed {s} episode {e}")
            r = recal(cache, hold)
            per[f"{C.fid(f)}_s{s}"] = r
            for q, k in (("aleatoric", 1), ("epistemic", 2)):
                fits = {(x["test_episode"], x["h"]): x for x in r[q]["fits"]}
                cfits = {(x["test_episode"], x["h"]): x for x in r[q]["constant_fits"]}
                for te in hold:
                    for h in HORIZONS:
                        for name, c in (("per_horizon", fits[(te, h)]["c"]), ("constant", cfits[(te, h)]["c"]),
                                        ("before", 1.0)):
                            cv, vl = CM.counts(cache[te][0], cache[te][k], c, h)
                            pool[q][name][h][s][0].append(cv)
                            pool[q][name][h][s][1].append(vl)
            if s == C.ENS5_SEEDS[0]:
                order += [{"fold": C.fid(f), "test_episode": te} for te in hold]
    summary = {}
    for q in ("aleatoric", "epistemic"):
        cells = [x for r in per.values() for x in r[q]["fits"]]
        ccells = [x for r in per.values() for x in r[q]["constant_fits"]]
        ok = [abs(x["coverage_after"] - TARGET) < TOL for x in cells]
        okc = [abs(x["coverage_after"] - TARGET) < TOL for x in ccells]
        summary[q] = {"per_horizon_cells_calibrated": int(sum(ok)), "n_cells": len(ok),
                      "constant_cells_calibrated": int(sum(okc)),
                      "per_horizon_restores_calibration": bool(all(ok)),
                      "worst_cell": max(cells, key=lambda x: abs(x["coverage_after"] - TARGET)), "tolerance": TOL}
    draws = np.random.default_rng(0).integers(0, 20, (N_BOOT, 20))
    along = {}
    for q in ("aleatoric", "epistemic"):
        along[q] = {}
        for name in ("per_horizon", "constant", "before"):
            along[q][name] = {}
            for h in HORIZONS:
                rows = {}
                cs, vs = [], []
                for s in C.ENS5_SEEDS:
                    cv = np.concatenate(pool[q][name][h][s][0]); vl = np.concatenate(pool[q][name][h][s][1])
                    assert cv.shape == (20,), cv.shape
                    bd = np.array([CM.pooled(cv, vl, i) for i in draws])
                    ci = [float(np.percentile(bd, 2.5)), float(np.percentile(bd, 97.5))]
                    rows[str(s)] = {"coverage": CM.pooled(cv, vl), "ci95": ci, "label": band(ci)}
                    cs.append(cv); vs.append(vl)
                cv, vl = np.sum(cs, 0), np.sum(vs, 0)
                bd = np.array([CM.pooled(cv, vl, i) for i in draws])
                ci = [float(np.percentile(bd, 2.5)), float(np.percentile(bd, 97.5))]
                along[q][name][str(h)] = {"per_seed": rows, "seeds_pooled": {"coverage": CM.pooled(cv, vl),
                                                                            "ci95": ci, "label": band(ci)}}
    gov = summary["epistemic"]
    out = {"rule": RULE, "ledger": RULE_ID, "frozen_sha256": frozen, "script": "scripts/x11c_fold_recalibration.py",
           "script_sha256": C.sha256("scripts/x11c_fold_recalibration.py"), "exploratory": True,
           "never_reopens": "M-69, M-70, M-89, the D3 per-horizon reading or any discharged rule; nothing here changes a verdict",
           "design": {"folds": [list(f) for f in C.FOLDS], "seeds": list(C.ENS5_SEEDS), "horizons": list(HORIZONS),
                      "target": TARGET, "tolerance": TOL, "band": [LO, HI], "test_episodes": order,
                      "copied_from": "scripts/task_d3_perhorizon.py:44-56, 85-127; arena changed only"},
           "assertions": {"a": {"pass": True}, **a18},
           "per_fold_seed": per, "summary": summary,
           "verdict": {"quantity": "epistemic",
                       "label": ("PER-HORIZON SCALAR RESTORES CALIBRATION" if gov["per_horizon_restores_calibration"]
                                 else "PER-HORIZON SCALAR DOES NOT RESTORE CALIBRATION"),
                       "cells_calibrated": gov["per_horizon_cells_calibrated"], "n_cells": gov["n_cells"],
                       "constant_cells_calibrated": gov["constant_cells_calibrated"]},
           "alongside": {"status": "alongside, not a reading", "pooled_over_folds": along},
           "weights_sha256": sha, "code_sha256": {p: C.sha256(p) for p in MODULES},
           "git_head": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
           "timing": {"wall_clock_s": time.perf_counter() - t0, "torch_threads": torch.get_num_threads(),
                      "cpu_count": os.cpu_count()}}
    json.dump(out, open(OUT, "w"), indent=1, default=float)
    print(f"  X11c: {out['verdict']['label']} ({gov['per_horizon_cells_calibrated']} of {gov['n_cells']} cells; "
          f"constant {gov['constant_cells_calibrated']})")
    print(f"  wrote {R.rel(OUT)}")


def main():
    os.chdir(C.ROOT)
    ap = argparse.ArgumentParser()
    ap.add_argument("--assert-only", action="store_true")
    args = ap.parse_args()
    if args.assert_only:
        a = assert_fold18()
        json.dump({"rule": RULE, "script_sha256": C.sha256("scripts/x11c_fold_recalibration.py"), **a},
                  open(ASSERT_OUT, "w"), indent=1)
        for k, v in a.items():
            print(f"  assertion {k}: {'PASS' if v['pass'] else 'FAIL'} (max diff {v['max_abs_diff']})")
        sys.exit(0 if all(v["pass"] for v in a.values()) else 1)
    reading()


if __name__ == "__main__":
    main()
