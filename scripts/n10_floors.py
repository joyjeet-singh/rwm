"""
N10 (round 5; POST HOC) -- floors: what predictors that use no model score on every long-horizon table's arenas.
docs/presubmission/round5/PROTOCOLS.md §5 N10 is the specification; this is a summary. It re-opens no rule and changes no
verdict.

nRMSE FORM 1 (src/rwm_metrics.py:115-133): mean over steps t <= h of sqrt(mean_d MSE_{t,d}) / mean_d scale_d, scale_d the
standard deviation of normalised state dimension d over the arena's training-episode rows (MET.training_scale). Two
conventions, labelled: per trajectory then averaged (mn_sweep_eval.metrics) and pooled over the arena's trajectories
(head_to_head_accuracy). On X3's five-fold arena the pooled convention is the mean over folds of each fold's pooled value
(DECISIONS.md#G4-n10-pooled). The ADDED FORM divides by sqrt(mean_d scale_d^2): it equals form 1 times
kappa = mean(scale) / sqrt(mean(scale^2)) for any predictor, reported per arena (and per fold).
PREDICTORS. (1) hold the last state (mn_sweep_eval.floor); (2) the training mean, the per-dimension mean of normalised state
over the arena's training-episode rows; (3) seasonal-naive: with o the last history row and P the period, step j >= 1 is
forecast by row o - P + 1 + ((j - 1) mod P); for P > 32 rows before the window are read from the CSV where they lie in the
same episode, else that trajectory falls back to hold-last and is counted.
THE PERIOD, fixed from training episodes before any held-out scoring: per training episode and joint-position dimension
(R.JOINT_POS), x = the normalised series minus its episode mean, ACF(L) = sum_t x_t x_{t+L} / sum_t x_t^2, averaged over the
12 dimensions and then the episodes (equal weight); P = the smallest L in [10, 100] that is a local maximum with
ACF(L) >= 0.8 max over the window. For the default split and for each X3 fold. `--period` prints them; they are written
into PERIODS in their own commit; scoring refuses to run while any is None and asserts each equals its recomputation.
ARENAS (h in {1, 8, 32, 100, 128, 368}): (i) the held-out pair, 4 trajectories, default split; (ii) the default split's 16
training trajectories; (iii) X3's five folds pooled, 20, each fold with its own training mean, scale and period; (iv) all ten
episodes, 20, default split.
ASSERTIONS (hold-last; float32 provenance, so 1e-6 absolute): mn_sweep_verdict.json hold_last_floor_l1; head_to_head_accuracy
rows.floor (pooled); a1_ab_by_horizon floor; the default training scale equals step4_0a_results.json nrmse_scale
(np.allclose, as mn_sweep_eval.py:133-135); this file's hold-last equals mn_sweep_eval.floor exactly.

  --period   compute and print the periods from training episodes only; no arena is scored.
Writes results/n10_floors.json. Run from the repository root.
"""
import argparse
import json
import math
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import rwm_data as R  # noqa: E402
import rollout_eval as E  # noqa: E402
import rwm_metrics as MET  # noqa: E402
import mn_sweep_eval as MN  # noqa: E402
import x11_common as C  # noqa: E402

OUT = os.path.join(R.RESULTS, "n10_floors.json")
HS = (1, 8, 32, 100, 128, 368)
M_HIST, FORECAST, LEN = 32, MN.FORECAST, 400
WINDOW, FRAC = (10, 100), 0.8
TOL = 1e-6
# Fixed from the training episodes by `--period` before any held-out scoring (PROTOCOLS §5 N10).
PERIODS = {"default": None, "02": None, "34": None, "56": None, "79": None}
MODULES = ("scripts/n10_floors.py", "scripts/mn_sweep_eval.py", "src/rwm_metrics.py", "src/rwm_data.py",
           "src/rollout_eval.py", "scripts/x11_common.py")


def norm_all():
    cfg, data, ep = C.data()
    return R.normalise_state(data[:, R.STATE_COLS], cfg["state_data_mean"], cfg["state_data_std"])


def acf_curve(train_eps, Z, ep):
    lags = np.arange(WINDOW[0] - 1, WINDOW[1] + 2)
    per_ep = []
    for e in train_eps:
        x = Z[ep == e][:, R.JOINT_POS].astype(np.float64)
        x = x - x.mean(0)
        den = (x * x).sum(0)
        per_ep.append(np.mean([[(x[:-L, d] * x[L:, d]).sum() / den[d] for d in range(x.shape[1])] for L in lags], 1))
    return lags, np.mean(per_ep, 0)


def period_of(train_eps, Z, ep):
    lags, a = acf_curve(train_eps, Z, ep)
    inner = range(1, len(lags) - 1)
    mx = max(a[i] for i in inner)
    for i in inner:
        if a[i] >= a[i - 1] and a[i] >= a[i + 1] and a[i] >= FRAC * mx:
            return int(lags[i]), {int(lags[j]): float(a[j]) for j in inner}
    raise AssertionError("no local maximum in the window")


def split_of(name):
    return (E.make_split(seed=0, strat_path=C.STRAT, verbose=False) if name == "default"
            else E.fold_split([int(name[0]), int(name[1])], strat_path=C.STRAT))


def periods():
    _, _, ep = C.data()
    Z = norm_all()
    out = {}
    for name in PERIODS:
        P, curve = period_of(sorted(split_of(name)["train_episodes"]), Z, ep)
        out[name] = {"P": P, "acf": curve, "train_episodes": sorted(split_of(name)["train_episodes"])}
    return out


def predictors(starts, train_eps, P, Z32):
    """The three no-model forecasts for windows starting at `starts`: (truth, {name: pred}, n_fallback)."""
    cfg, data, ep = C.data()
    st, _ = MN.window_arrays(data, cfg, starts, M_HIST, M_HIST)          # (n, 400, 45) float32
    truth = st[:, M_HIST:]
    hold = np.repeat(st[:, M_HIST - 1:M_HIST], FORECAST, axis=1)
    rows = np.isin(ep, list(train_eps)) & (ep >= 0)
    mean = R.normalise_state(data[rows][:, R.STATE_COLS], cfg["state_data_mean"], cfg["state_data_std"]).mean(0)
    tmean = np.broadcast_to(mean.astype(np.float32), truth.shape).copy()
    seas, fb = np.empty_like(truth), 0
    j = np.arange(1, FORECAST + 1)
    for t, s in enumerate(starts):
        o = s + M_HIST - 1
        idx = o - P + 1 + ((j - 1) % P)
        if idx.min() < 0 or not (ep[idx] == ep[o]).all():
            seas[t] = hold[t]
            fb += 1
        else:
            seas[t] = Z32[idx]
    return st, truth, {"hold": hold, "mean": tmean, "seas": seas}, fb


def score(truth, pred, scale):
    err = (pred.astype(np.float64) - truth.astype(np.float64))
    pt = MN.metrics(err, truth, scale)
    sq = err ** 2
    out = {}
    kap = float(np.mean(scale) / np.sqrt(np.mean(np.asarray(scale) ** 2)))
    for h in HS:
        l1 = float(np.mean(pt[str(h)]["l1"]))
        nt = float(np.mean(pt[str(h)]["nrmse"]))
        npool = MET.nrmse_pooled(sq[:, :h], scale)
        # the added form, computed directly, must be form 1 times kappa
        mse = sq[:, :h].mean(0)
        rms_direct = float((np.sqrt(mse.mean(1)) / np.sqrt(np.mean(np.asarray(scale) ** 2))).mean())
        assert abs(rms_direct - npool * kap) <= 1e-12 * max(1.0, npool), (rms_direct, npool * kap)
        out[str(h)] = {"l1": l1, "nrmse_per_traj": nt, "nrmse_pooled": npool,
                       "nrmse_rms_per_traj": nt * kap, "nrmse_rms_pooled": npool * kap}
    return out, kap


def main():
    os.chdir(C.ROOT)
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", action="store_true")
    args = ap.parse_args()
    t0 = time.perf_counter()
    per = periods()
    if args.period:
        for k, v in per.items():
            print(f"  period {k}: P = {v['P']} steps ({v['P'] * R.DT:.2f} s); training episodes {v['train_episodes']}")
        return
    if any(v is None for v in PERIODS.values()):
        C.blocked(OUT, "PERIODS are not fixed: run --period and commit them first")
    if any(per[k]["P"] != PERIODS[k] for k in PERIODS):
        C.blocked(OUT, "a recomputed period differs from its constant", recomputed={k: v["P"] for k, v in per.items()})

    cfg, data, ep = C.data()
    Z32 = norm_all().astype(np.float32)
    dsplit = split_of("default")
    dtrain, dhold = sorted(dsplit["train_episodes"]), sorted(dsplit["holdout_episodes"])
    dscale = MET.training_scale(data, ep, dtrain, cfg["state_data_mean"], cfg["state_data_std"])
    stored_scale = np.array(json.load(open(os.path.join(R.RESULTS, "step4_0a_results.json")))["nrmse_scale"])
    A = {"scale": {"pass": bool(np.allclose(dscale, stored_scale)), "max_abs_diff": float(np.abs(dscale - stored_scale).max()),
                   "against": "results/step4_0a_results.json nrmse_scale (np.allclose, as mn_sweep_eval.py:133-135)"}}
    arenas = {"heldout": (MN.arena(ep, dhold, M_HIST)["starts"], dtrain, PERIODS["default"], dscale),
              "insample": (MET.non_overlapping_starts(ep, dtrain, LEN), dtrain, PERIODS["default"], dscale),
              "all10": (MET.non_overlapping_starts(ep, list(range(R.N_EPISODES)), LEN), dtrain, PERIODS["default"], dscale)}
    res, fbs, kaps = {}, {}, {}
    for name, (starts, tr, P, scale) in arenas.items():
        st, truth, preds, fb = predictors(starts, tr, P, Z32)
        res[name] = {}
        for p, pr in preds.items():
            res[name][p], kaps[name] = score(truth, pr, scale)
        fbs[name] = fb
        if name == "heldout":
            fl = MN.floor(data, cfg, scale, starts, M_HIST)
            mine = MN.metrics(preds["hold"].astype(np.float64) - truth.astype(np.float64), truth, scale)
            A["hold_equals_mn_floor"] = {"pass": bool(all(np.array_equal(np.asarray(fl[h]["l1"]), np.asarray(mine[h]["l1"]))
                                                          and np.allclose(fl[h]["nrmse"], mine[h]["nrmse"], rtol=0, atol=1e-12)
                                                          for h in fl))}
    # (iii) the folds: each with its own training mean, scale and period
    fold_rows, fold_k = {}, {}
    for f in C.FOLDS:
        name = "default" if f == (1, 8) else C.fid(f)
        sp = split_of(name)
        tr = sorted(sp["train_episodes"])
        scale = MET.training_scale(data, ep, tr, cfg["state_data_mean"], cfg["state_data_std"])
        starts = MN.arena(ep, list(f), M_HIST)["starts"]
        st, truth, preds, fb = predictors(starts, tr, PERIODS[name], Z32)
        fbs[f"fold{C.fid(f)}"] = fb
        fold_rows[C.fid(f)] = {}
        for p, pr in preds.items():
            fold_rows[C.fid(f)][p], fold_k[C.fid(f)] = score(truth, pr, scale)
    res["fold"] = {}
    for p in ("hold", "mean", "seas"):
        res["fold"][p] = {}
        for h in map(str, HS):
            rs = [fold_rows[C.fid(f)][p][h] for f in C.FOLDS]
            res["fold"][p][h] = {"l1": float(np.mean([r["l1"] for r in rs])),
                                 "nrmse_per_traj": float(np.mean([r["nrmse_per_traj"] for r in rs])),
                                 "nrmse_pooled": float(np.mean([r["nrmse_pooled"] for r in rs])),
                                 "nrmse_rms_per_traj": float(np.mean([r["nrmse_rms_per_traj"] for r in rs])),
                                 "nrmse_rms_pooled": float(np.mean([r["nrmse_rms_pooled"] for r in rs])),
                                 "pooled_convention": "mean over the five folds of each fold's pooled value (DECISIONS.md#G4-n10-pooled)"}
    # the stored floors
    sw = json.load(open(os.path.join(R.RESULTS, "mn_sweep_verdict.json")))["hold_last_floor_l1"]
    hh = json.load(open(os.path.join(R.RESULTS, "head_to_head_accuracy.json")))["rows"]["floor"]["cells"]
    a1 = json.load(open(os.path.join(R.RESULTS, "a1_ab_by_horizon.json")))["by_horizon"]
    d = 0.0
    for ar_, key in (("heldout", "held_out"), ("insample", "in_sample")):
        for h in ("100", "368"):
            d = max(d, abs(res[ar_]["hold"][h]["l1"] - sw[key][h]))
    for h in ("1", "8", "100", "368"):
        d = max(d, abs(res["heldout"]["hold"][h]["l1"] - hh[h]["l1"]), abs(res["heldout"]["hold"][h]["nrmse_pooled"] - hh[h]["nrmse"]))
    for h in map(str, HS):
        d = max(d, abs(res["heldout"]["hold"][h]["l1"] - a1[h]["floor"]))
    A["stored_floors"] = {"pass": bool(d <= TOL), "max_abs_diff": d, "tolerance": TOL,
                          "against": ["results/mn_sweep_verdict.json hold_last_floor_l1",
                                      "results/head_to_head_accuracy.json rows.floor.cells (pooled)",
                                      "results/a1_ab_by_horizon.json by_horizon[h].floor"]}
    A["periods"] = {"pass": True, "recomputed_equal_constants": {k: v["P"] for k, v in per.items()}}
    for k, v in A.items():
        print(f"  assertion {k}: {'PASS' if v['pass'] else 'FAIL'}  {v.get('max_abs_diff', '')}")
    if not all(v["pass"] for v in A.values()):
        C.blocked(OUT, "a reproduction assertion failed", assertions=A)
    out = {"analysis": "N10", "post_hoc": True,
           "never_reopens": "M-23, M-74, M-75, M-76, X3, X4 or any discharged rule; nothing here changes a verdict",
           "script": "scripts/n10_floors.py", "script_sha256": C.sha256("scripts/n10_floors.py"),
           "design": {"horizons": list(HS), "periods": {k: {"P": v["P"], "seconds": v["P"] * R.DT,
                                                            "train_episodes": v["train_episodes"]} for k, v in per.items()},
                      "period_rule": "smallest local maximum in [10, 100] steps with ACF >= 0.8 x the window maximum",
                      "arenas": {"heldout": "default split's held-out pair, 4 trajectories",
                                 "insample": "default split's 16 training trajectories",
                                 "fold": "X3's five folds' held-out pairs, 20 trajectories, each fold its own mean, scale and period",
                                 "all10": "all ten episodes, 20 trajectories, default split"},
                      "nrmse": "form 1, src/rwm_metrics.py:115-133; *_rms_* is form 1 x kappa",
                      "specification": "docs/presubmission/round5/PROTOCOLS.md §5 N10; DECISIONS.md#G4-n10-pooled"},
           "assertions": A, "floors": res, "kappa": {**kaps, "folds": fold_k}, "fold_detail": fold_rows,
           "n_seasonal_fallback": fbs, "acf": {k: v["acf"] for k, v in per.items()},
           "code_sha256": {p: C.sha256(p) for p in MODULES},
           "git_head": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
           "timing": {"wall_clock_s": time.perf_counter() - t0, "cpu_count": os.cpu_count()}}
    json.dump(out, open(OUT, "w"), indent=1)
    for a in ("heldout", "fold", "all10"):
        print(f"  {a}: " + "  ".join(f"{p} l1 {res[a][p]['368']['l1']:.3f} nrmse {res[a][p]['368']['nrmse_pooled']:.3f}"
                                     for p in ("hold", "mean", "seas")) + "  (h = 368)")
    print(f"  kappa {kaps}; fallbacks {fbs}")
    print(f"  wrote {R.rel(OUT)}")


if __name__ == "__main__":
    main()
