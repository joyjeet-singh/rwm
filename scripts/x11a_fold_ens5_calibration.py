"""
Rule X11a (round 5; PRE-REGISTERED, exploratory) -- the ensemble-5 arms' calibration on held-out episodes at
n_independent = 20, and X10's in-sample-against-held-out ratio with every episode in both roles.

It never re-opens a discharged rule, and nothing it returns changes a verdict. PROTOCOLS.md §4 holds the rule.

MODELS. Arm A at ensemble size 5, seeds 0-2, 2,500 iterations, one set per X3 fold: the existing
runs/armA_seed<s>_ens5 for {1, 8}, and runs/x3_armA_ho<ab>_seed<s>_ens5 (X11's queue) for the other four.

ARENAS. Held-out: each fold's four non-overlapping 400-row trajectories, rolled out by that fold's arms, one batch
of 4 per fold; the five folds pool to 20 trajectories, each episode's two once. In-sample: each fold's sixteen
training trajectories, one batch of 16 per fold; across the five folds each of the 20 trajectories is in-sample in
exactly four folds.

STATISTICS, copied from task_d3_ens5.py (calibration, lines 243-278) with only the arena changed: per seed, rho =
mean|error| / mean sigma_epistemic, +-1 and +-2 sigma coverage and the count of dimensions with r > 0, pooled over
(trajectory, step <= h, dimension); the pooled value is the mean over seeds; the interval resamples whole
trajectories with the seeds pooled inside each draw, default_rng(0).integers(0, n, (20000, n)).
X10's Q(h) = rho_in(h) / rho_out(h), per seed and pooled as task_d3_ens5 pools. Because both arenas now hold the same
20 trajectories (a trajectory's in-sample value is the mean over the four folds that trained on it, numerator and
denominator separately), the interval is a PAIRED bootstrap over the 20 trajectories, one draw matrix
default_rng(0).integers(0, 20, (20000, 20)); X10's own interval resampled two disjoint arenas independently.

VERDICT at h = 1 (X10's labels): IN-SAMPLE FLATTERS (Q < 1 in 3 of 3 seeds and the pooled interval below 1);
IN-SAMPLE IS WORSE (Q > 1 in 3 of 3 and the interval above 1); MIXED otherwise. h = 100 carries "the label it would
carry", not a second verdict.

ASSERTIONS (before any reading): (a) every run record trained on its fold's complement at ensemble 5 and 2,500
iterations with finite losses; (b) for fold {1, 8}, the held-out calibration through this code reproduces
results/task_d3_ens5.json calibration at every horizon, the intervals included, within 1e-12; (c) for every arm and
both arenas, the harness agrees with our trainer's forward to < 1e-5 (task_d3_ens5.py:128).

  --assert-only   run (b) and (c) on fold {1, 8} only (no X11 run needed) and write
                  docs/presubmission/round5/gt1_x11a_assert.json; no reading.
Writes results/x11a_fold_ens5_calibration.json. Run from the repository root.
"""
import argparse
import json
import os
import statistics
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import torch  # noqa: E402
import rwm_data as R  # noqa: E402
import x11_common as C  # noqa: E402

RULE = "X11a"
RULE_ID = "M-97"
FROZEN = ('scripts/x11a_fold_ens5_calibration.py', 'scripts/x11_common.py')
HORIZONS = (1, 8, 32, 100, 128, 368)
START, N_BOOT, TOL_REPRO, TOL_HARNESS = C.START, 20000, 1e-12, 1e-5
LABELS = ("IN-SAMPLE FLATTERS", "IN-SAMPLE IS WORSE", "MIXED")
OUT = os.path.join(R.RESULTS, "x11a_fold_ens5_calibration.json")
ASSERT_OUT = os.path.join(C.ROOT, "docs", "presubmission", "round5", "gt1_x11a_assert.json")
MODULES = ("scripts/x11a_fold_ens5_calibration.py", "scripts/x11_common.py", "scripts/task_d3_ens5.py",
           "scripts/x3_cross_fold.py", "src/score_reference.py", "src/rwm_model.py", "src/rwm_data.py",
           "src/rwm_metrics.py", "src/rollout_eval.py")


def roll(m, sd, ar):
    pred, alea, epi, _, _ = m.rollout_uncertainty(ar["st"].clone(), ar["ac"], START, action_offset=1)
    d = float((C.harness_check(sd, ar["st"], ar["ac"]) - pred).abs().max())
    return {"err": (pred - ar["st"]).abs().numpy().astype(np.float64),
            "epi": epi.numpy().astype(np.float64), "harness_max_diff": d}


def calibration(per_seed, draws):
    """task_d3_ens5.py:243-278. per_seed: {s: {"err", "epi"}} of shape (n_traj, 400, 45)."""
    def _ci(per_traj_num, per_traj_den=None):
        a = per_traj_num.mean(axis=0)[draws].mean(axis=1)
        v = a if per_traj_den is None else a / per_traj_den.mean(axis=0)[draws].mean(axis=1)
        v = v[np.isfinite(v)]
        return ([float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] if len(v) > 1 else [None, None])

    seeds = sorted(per_seed)
    cal = {}
    for h in HORIZONS:
        rows = []
        pe, pg, p1, p2 = [], [], [], []
        for s in seeds:
            eT = per_seed[s]["err"][:, START:START + h]
            gT = per_seed[s]["epi"][:, START:START + h]
            e, g = eT.reshape(-1, 45), gT.reshape(-1, 45)
            npos = 0
            for d in range(45):
                a, b = g[:, d], e[:, d]
                if a.std() > 0 and b.std() > 0 and np.corrcoef(a, b)[0, 1] > 0:
                    npos += 1
            rows.append({"seed": s, "ratio_err_over_sigma": float(np.nanmean(e) / np.nanmean(g)),
                         "coverage_pm1": float(np.nanmean(e <= g)), "coverage_pm2": float(np.nanmean(e <= 2 * g)),
                         "n_positive": npos})
            pe.append(np.nanmean(eT, axis=(1, 2))); pg.append(np.nanmean(gT, axis=(1, 2)))
            p1.append(np.nanmean(eT <= gT, axis=(1, 2))); p2.append(np.nanmean(eT <= 2 * gT, axis=(1, 2)))
        pe, pg, p1, p2 = map(np.asarray, (pe, pg, p1, p2))
        cal[str(h)] = {"per_seed": rows,
                       "mean_ratio": statistics.mean(r["ratio_err_over_sigma"] for r in rows),
                       "mean_cov1": statistics.mean(r["coverage_pm1"] for r in rows),
                       "mean_cov2": statistics.mean(r["coverage_pm2"] for r in rows),
                       "mean_npos": statistics.mean(r["n_positive"] for r in rows),
                       "ratio_ci": _ci(pe, pg), "cov1_ci": _ci(p1), "cov2_ci": _ci(p2),
                       "bootstrap_unit": "whole trajectory, seeds pooled within each draw",
                       "n_independent": int(pe.shape[1]),
                       "_per_traj": {"err": pe, "sig": pg}}
    return cal


def strip(cal):
    return {h: {k: v for k, v in c.items() if not k.startswith("_")} for h, c in cal.items()}


def max_diff(got, want):
    """Largest absolute difference over every numeric leaf of want; a missing or extra leaf is infinite."""
    if isinstance(want, dict):
        return max([max_diff(got.get(k) if isinstance(got, dict) else None, v) for k, v in want.items()] or [0.0])
    if isinstance(want, list):
        if not isinstance(got, list) or len(got) != len(want):
            return float("inf")
        return max([max_diff(g, w) for g, w in zip(got, want)] or [0.0])
    if isinstance(want, bool) or isinstance(want, str) or want is None:
        return 0.0 if got == want else float("inf")
    if not isinstance(got, (int, float)):
        return float("inf")
    return abs(float(got) - float(want))


def assert_fold18():
    """(b) and (c) on fold {1, 8}, where task_d3_ens5.json exists."""
    ar = C.arena((1, 8))
    per, hd = {}, {}
    for s in C.ENS5_SEEDS:
        m, sd = C.load_ens5(C.ens5_weights((1, 8), s))
        per[s] = roll(m, sd, ar)
        hd[s] = per[s]["harness_max_diff"]
    draws = np.random.default_rng(0).integers(0, 4, (N_BOOT, 4))
    got = strip(calibration(per, draws))
    want = json.load(open(os.path.join(R.RESULTS, "task_d3_ens5.json")))["calibration"]
    d = max_diff(got, {h: {k: v for k, v in c.items()} for h, c in want.items()})
    return {"b": {"pass": bool(d <= TOL_REPRO), "max_abs_diff": d, "tolerance": TOL_REPRO,
                  "against": "results/task_d3_ens5.json calibration, every horizon, intervals included"},
            "c_fold18": {"pass": bool(max(hd.values()) < TOL_HARNESS), "max_abs_diff": hd, "tolerance": TOL_HARNESS}}


def label(q_seeds, ci):
    if all(q < 1 for q in q_seeds) and ci[1] is not None and ci[1] < 1:
        return LABELS[0]
    if all(q > 1 for q in q_seeds) and ci[0] is not None and ci[0] > 1:
        return LABELS[1]
    return LABELS[2]


def reading():
    t0 = time.perf_counter()
    frozen = C.require_prereg(RULE_ID, FROZEN, OUT)
    bad = {f"{C.fid(f)}_s{s}": C.check_record(C.ens5_record(f, s), f, 5) for f in C.FOLDS for s in C.ENS5_SEEDS}
    bad = {k: v for k, v in bad.items() if v}
    if bad:
        C.blocked(OUT, "assertion (a): a run record is wrong", problems=bad)
    a18 = assert_fold18()
    held, ins, hd, sha, order = {s: [] for s in C.ENS5_SEEDS}, {}, {}, {}, []
    for f in C.FOLDS:
        ar, ia = C.arena(f), C.in_sample(f)
        order += list(zip([C.fid(f)] * 4, ar["starts"], ar["episode"]))
        for s in C.ENS5_SEEDS:
            w = C.ens5_weights(f, s)
            sha[f"{C.fid(f)}_s{s}"] = C.sha256(w)
            m, sd = C.load_ens5(w)
            r_out, r_in = roll(m, sd, ar), roll(m, sd, ia)
            hd[f"{C.fid(f)}_s{s}"] = max(r_out["harness_max_diff"], r_in["harness_max_diff"])
            held[s].append(r_out)
            ins[(C.fid(f), s)] = (ia["starts"], r_in)
    if not (a18["b"]["pass"] and max(hd.values()) < TOL_HARNESS):
        C.blocked(OUT, "assertion (b) or (c) failed", b=a18["b"], harness=hd)
    out_seed = {s: {k: np.concatenate([r[k] for r in held[s]], 0) for k in ("err", "epi")} for s in C.ENS5_SEEDS}
    for s, v in out_seed.items():
        if not (np.isfinite(v["err"][:, START:]).all() and np.isfinite(v["epi"][:, START:]).all()):
            C.blocked(OUT, f"non-finite held-out rollout, seed {s}")
    draws = np.random.default_rng(0).integers(0, 20, (N_BOOT, 20))
    cal_out = calibration(out_seed, draws)

    # in-sample, per trajectory: the mean over the four folds that trained on it, numerator and denominator apart
    start_of = [st for _, st, _ in order]
    q = {}
    for h in HORIZONS:
        sl = slice(START, START + h)
        pe_in, pg_in, c1_in = [], [], []
        rho_in, rho_out = {}, {}
        for s in C.ENS5_SEEDS:
            acc_e, acc_g, acc_c, cnt = (np.zeros(20) for _ in range(4))
            for f in C.FOLDS:
                starts, r = ins[(C.fid(f), s)]
                e, g = r["err"][:, sl], r["epi"][:, sl]
                for j, st in enumerate(starts):
                    t = start_of.index(st)
                    acc_e[t] += np.nanmean(e[j]); acc_g[t] += np.nanmean(g[j])
                    acc_c[t] += np.nanmean(e[j] <= g[j]); cnt[t] += 1
            if not (cnt == 4).all():
                C.blocked(OUT, f"a trajectory is in-sample in {sorted(set(cnt.tolist()))} folds, not 4")
            pe_in.append(acc_e / 4); pg_in.append(acc_g / 4); c1_in.append(acc_c / 4)
            rho_in[s] = float(pe_in[-1].mean() / pg_in[-1].mean())
            rho_out[s] = cal_out[str(h)]["per_seed"][C.ENS5_SEEDS.index(s)]["ratio_err_over_sigma"]
        pe_in, pg_in = np.asarray(pe_in).mean(0), np.asarray(pg_in).mean(0)
        po_e, po_g = cal_out[str(h)]["_per_traj"]["err"].mean(0), cal_out[str(h)]["_per_traj"]["sig"].mean(0)
        qd = (pe_in[draws].mean(1) / pg_in[draws].mean(1)) / (po_e[draws].mean(1) / po_g[draws].mean(1))
        qd = qd[np.isfinite(qd)]
        qs = {str(s): rho_in[s] / rho_out[s] for s in C.ENS5_SEEDS}
        ci = [float(np.percentile(qd, 2.5)), float(np.percentile(qd, 97.5))]
        q[str(h)] = {"q_per_seed": qs, "rho_in_per_seed": {str(s): v for s, v in rho_in.items()},
                     "rho_out_per_seed": {str(s): v for s, v in rho_out.items()},
                     "rho_in": statistics.mean(rho_in.values()), "rho_out": statistics.mean(rho_out.values()),
                     "q": statistics.mean(rho_in.values()) / statistics.mean(rho_out.values()),
                     "q_ci": ci, "n_boot_finite": int(len(qd)),
                     "cov1_in": float(np.asarray(c1_in).mean()),
                     "label_it_would_carry": label(list(qs.values()), ci)}
    out = {"rule": RULE, "ledger": RULE_ID, "frozen_sha256": frozen, "script": "scripts/x11a_fold_ens5_calibration.py",
           "script_sha256": C.sha256("scripts/x11a_fold_ens5_calibration.py"), "exploratory": True,
           "never_reopens": "M-43, M-44, X10 or any discharged rule; nothing here changes a verdict",
           "design": {"folds": [list(f) for f in C.FOLDS], "seeds": list(C.ENS5_SEEDS), "ensemble": 5,
                      "iterations": C.ITERS, "n_trajectories": 20, "n_independent": 20, "horizons": list(HORIZONS),
                      "trajectories": [{"fold": a, "start_row": b, "episode": c} for a, b, c in order],
                      "q_interval": "paired bootstrap over the 20 trajectories, default_rng(0), 20000 draws"},
           "assertions": {"a": {"pass": True}, **a18, "c": {"pass": True, "max_abs_diff": hd, "tolerance": TOL_HARNESS}},
           "calibration": strip(cal_out), "q": q,
           "verdict": {"h": 1, "label": q["1"]["label_it_would_carry"], "q": q["1"]["q"], "q_ci": q["1"]["q_ci"],
                       "q_per_seed": q["1"]["q_per_seed"]},
           "label_h100": q["100"]["label_it_would_carry"],
           "weights_sha256": sha,
           "code_sha256": {p: C.sha256(p) for p in MODULES},
           "git_head": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
           "timing": {"wall_clock_s": time.perf_counter() - t0, "torch_threads": torch.get_num_threads(),
                      "cpu_count": os.cpu_count()}}
    json.dump(out, open(OUT, "w"), indent=1)
    print(f"  X11a: Q(h=1) = {out['verdict']['q']:.4f} {out['verdict']['q_ci']} -> {out['verdict']['label']}")
    print(f"  wrote {R.rel(OUT)}")


def main():
    os.chdir(C.ROOT)
    ap = argparse.ArgumentParser()
    ap.add_argument("--assert-only", action="store_true")
    args = ap.parse_args()
    if args.assert_only:
        a = assert_fold18()
        json.dump({"rule": RULE, "script_sha256": C.sha256("scripts/x11a_fold_ens5_calibration.py"), **a},
                  open(ASSERT_OUT, "w"), indent=1)
        for k, v in a.items():
            print(f"  assertion {k}: {'PASS' if v['pass'] else 'FAIL'} (max diff {v['max_abs_diff']})")
        sys.exit(0 if all(v["pass"] for v in a.values()) else 1)
    reading()


if __name__ == "__main__":
    main()
