"""
N11 (round 5; POST HOC) -- rank correlations beside every Pearson ranking statistic the paper reports.
docs/presubmission/round5/PROTOCOLS.md §5 N11 is the specification; this is a summary. It re-opens no rule and changes no
verdict: each pre-registered verdict keeps the Pearson statistic it was committed with (DECISIONS Y8).

UNITS, each recomputed from the same pooled vectors and the SAME bootstrap draws as the Pearson value beside it (the draws are
taken from each original script's own generator and loop, and recorded):
  U1 task_d_nind20 D2 (sec. 6.6's table): r(index, error), r(disagreement, error), the partial given the index, the paired
     difference; h in {1, 8, 32, 100, 128, 368, all}; cluster_boot, a fresh default_rng(0) per statistic, 20,000 draws.
  U2 task_d3_ens5 M-43, per seed: the same four, cluster_boot default_rng(0) for the paired difference.
  U3 a2_trajectory_level_control: r_dd overall (default_rng(4)) and per horizon (default_rng(30 + h)).
  U4 e7_free_baselines: r(baseline, error), the margin and the partial, step-size, entry-res and the index, one
     default_rng(20260829) consumed in e7's order, 4,000 draws per interval.
  U5 x6_stepsize_short_units, h = 32 and 100: the margin and the partial, default_rng(0), 20,000 draws.
  U6 the per-dimension "positively correlated on k of 45" counts (task_d_nind20.block; task_d3_ens5): Spearman count only.
RANK STATISTICS. Spearman = Pearson of average ranks (ties share the mean rank) of the same finite pairs, re-ranked inside every
draw; rank partial = the unit's own partial function applied to ranks. Kendall tau_b and Kendall's partial tau as point
estimates only, tau_b exact in numpy (sign products over all pairs, chunked), self-tested against a brute-force loop.
ASSERTION, before any rank statistic: every Pearson value and interval of U1-U6 recomputed here equals the stored artifact
within 1e-12. TIMING: the first 200 Spearman draws of U1 at h = all are timed and the whole run projected.
Writes results/n11_rank_correlations.json. Run from the repository root.
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
import rollout_eval as E  # noqa: E402
import rwm_metrics as MET  # noqa: E402
import score_reference as S  # noqa: E402
import task_d_nind20 as TDN  # noqa: E402
import task_d3_ens5 as TD  # noqa: E402
import a2_trajectory_level_control as A2  # noqa: E402
import e7_free_baselines as E7  # noqa: E402
import x6_stepsize_short_units as X6  # noqa: E402
import x11_common as C  # noqa: E402
import x11b_fold_m43 as XB  # noqa: E402

OUT = os.path.join(R.RESULTS, "n11_rank_correlations.json")
START, TOL = E.START_STEP, 1e-12
J = lambda n: json.load(open(os.path.join(R.RESULTS, n)))
MODULES = ("scripts/n11_rank_correlations.py", "scripts/task_d_nind20.py", "scripts/task_d3_ens5.py",
           "scripts/a2_trajectory_level_control.py", "scripts/e7_free_baselines.py", "scripts/x6_stepsize_short_units.py",
           "scripts/x11b_fold_m43.py", "scripts/x11_common.py", "src/score_reference.py")


# ------------------------------------------------------------------ rank machinery
def avg_rank(a):
    o = np.argsort(a, kind="mergesort")
    s = a[o]
    r = np.empty(len(a), dtype=np.float64)
    b = np.flatnonzero(np.r_[True, s[1:] != s[:-1], True])
    r[o] = np.repeat(0.5 * (b[:-1] + b[1:] - 1) + 1.0, np.diff(b))
    return r


def _ranked(*xs):
    v = [np.asarray(x, dtype=np.float64).ravel() for x in xs]
    m = np.all([np.isfinite(x) for x in v], 0)
    return [avg_rank(x[m]) for x in v]


def sp(x, y, corr=TDN.pooled_corr):
    a, b = _ranked(x, y)
    return corr(a, b)


def sp_partial(x, y, z, partial=TDN.partial_corr):
    a, b, c = _ranked(x, y, z)
    return partial(a, b, c)


def tau_b(x, y, chunk=256):
    x, y = (np.asarray(v, dtype=np.float64).ravel() for v in (x, y))
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    n = len(x)
    S_ = 0.0
    for i in range(0, n, chunk):
        sx = np.sign(x[i:i + chunk, None] - x[None, :])
        sy = np.sign(y[i:i + chunk, None] - y[None, :])
        S_ += float((sx * sy).sum())
    S_ /= 2.0                                             # every unordered pair was counted twice
    n0 = n * (n - 1) / 2.0
    tie = lambda a: sum(t * (t - 1) / 2.0 for t in np.unique(a, return_counts=True)[1])
    return float(S_ / np.sqrt((n0 - tie(x)) * (n0 - tie(y))))


def tau_partial(x, y, z):
    txy, txz, tyz = tau_b(x, y), tau_b(x, z), tau_b(y, z)
    return float((txy - txz * tyz) / np.sqrt((1 - txz ** 2) * (1 - tyz ** 2)))


def self_test():
    rng = np.random.default_rng(5)
    x, y = rng.integers(0, 12, 200).astype(float), rng.integers(0, 9, 200).astype(float) + 0.3 * rng.integers(0, 3, 200)
    nc = nd = 0
    for i in range(200):
        for j in range(i + 1, 200):
            s = np.sign(x[i] - x[j]) * np.sign(y[i] - y[j])
            nc += s > 0
            nd += s < 0
    n0 = 200 * 199 / 2
    t = lambda a: sum(c * (c - 1) / 2 for c in np.unique(a, return_counts=True)[1])
    brute = (nc - nd) / np.sqrt((n0 - t(x)) * (n0 - t(y)))
    r = avg_rank(np.array([3.0, 1.0, 3.0, 2.0]))
    return {"tau_b_vs_brute_force_abs_diff": abs(tau_b(x, y) - brute), "avg_rank_ties": r.tolist(),
            "pass": bool(abs(tau_b(x, y) - brute) <= 1e-12 and r.tolist() == [3.5, 1.0, 3.5, 2.0])}


def rec_boot(boot, fn, *a):
    """Run an original bootstrap function, recording every index draw it makes."""
    draws = []

    def f(i):
        draws.append(np.array(i))
        return fn(i)
    res = boot(f, *a)
    return res, draws


def ci_of(vals):
    v = np.array([x for x in vals if x is not None and np.isfinite(x)])
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))], int(len(v))


class Diff:
    def __init__(self):
        self.d = 0.0

    def __call__(self, a, b):
        if a is None or b is None:
            if not (a is None and b is None):
                self.d = float("inf")
            return
        self.d = max(self.d, abs(float(a) - float(b)))


def main():
    os.chdir(C.ROOT)
    t0 = time.perf_counter()
    st_ = self_test()
    print(f"  self-test: {'PASS' if st_['pass'] else 'FAIL'} {st_}")
    if not st_["pass"]:
        C.blocked(OUT, "the rank self-test failed", self_test=st_)
    A, out = {}, {}

    # ---------------- the released checkpoint on all ten episodes (U1, U3, U6) ----------------
    cfg, data, ep = C.data()
    split = E.make_split(seed=0, strat_path=C.STRAT, verbose=False)
    allep = sorted(set(split["train_episodes"]) | set(split["holdout_episodes"]))
    starts = MET.non_overlapping_starts(ep, allep, TDN.LEN)
    st, ac = C.tensors(starts)
    model = S.ReferenceRWM(torch.load(R.repo_paths()["ckpt"], map_location="cpu")["system_dynamics_state_dict"])
    model.eval()
    pred, alea, epi, _, epi_s = model.rollout_uncertainty(st.clone(), ac, START, action_offset=1)
    abs_err = (pred - st).abs().numpy().astype(np.float64)
    alea, epi = alea.numpy().astype(np.float64), epi.numpy().astype(np.float64)
    epi_scalar = epi_s.numpy().astype(np.float64)[:, START:]
    err_scalar = abs_err[:, START:].sum(-1)
    T = err_scalar.shape[1]
    fidx = np.broadcast_to(np.arange(T, dtype=np.float64), err_scalar.shape).copy()
    n_traj = len(starts)

    # U1
    d2 = J("task_d_nind20.json")["d2_forecast_index"]
    dd = Diff()
    U1, probe = {}, None
    for h in list(TDN.HORIZONS) + ["all"]:
        k = T if h == "all" else min(h, T)
        E_, S_, F_ = err_scalar[:, :k], epi_scalar[:, :k], fidx[:, :k]
        w = d2[str(h)]
        r_idx, r_epi, r_par = TDN.pooled_corr(F_, E_), TDN.pooled_corr(S_, E_), TDN.partial_corr(S_, E_, F_)
        dd(r_idx, w["r_index"]); dd(r_epi, w["r_epistemic"]); dd(r_par, w["r_partial"])
        cis, draws = {}, None
        for nm, fn in (("index", lambda i: TDN.pooled_corr(F_[i], E_[i])),
                       ("epistemic", lambda i: TDN.pooled_corr(S_[i], E_[i])),
                       ("partial", lambda i: TDN.partial_corr(S_[i], E_[i], F_[i]))):
            (lo, hi, nb), dr = rec_boot(TDN.cluster_boot, fn, n_traj, np.random.default_rng(0))
            dd(lo, w["ci"][nm]["lo"]); dd(hi, w["ci"][nm]["hi"])
            draws = dr if draws is None else draws
            assert all(np.array_equal(a, b) for a, b in zip(draws, dr))
        pair = lambda i: (None if TDN.pooled_corr(S_[i], E_[i]) is None or TDN.pooled_corr(F_[i], E_[i]) is None
                          else TDN.pooled_corr(S_[i], E_[i]) - TDN.pooled_corr(F_[i], E_[i]))
        (plo, phi, _), dr = rec_boot(TDN.cluster_boot, pair, n_traj, np.random.default_rng(0))
        if w["paired_diff"] is not None:
            dd(r_epi - r_idx, w["paired_diff"]); dd(plo, w["paired_ci_lo"]); dd(phi, w["paired_ci_hi"])
        U1[str(h)] = {"F": F_, "E": E_, "S": S_, "draws": draws}
    A["U1"] = {"pass": bool(dd.d <= TOL), "max_abs_diff": dd.d, "against": "results/task_d_nind20.json d2_forecast_index"}

    # U3
    a2 = J("a2_trajectory_level_control.json")
    X, Y = epi_scalar, err_scalar
    d3 = Diff()
    r_dd = A2.corr(A2.double_demean(X), A2.double_demean(Y))
    (lo, hi, _), dr3 = rec_boot(A2.cboot, lambda i: A2.corr(A2.double_demean(X[i]), A2.double_demean(Y[i])), n_traj,
                                np.random.default_rng(4))
    d3(r_dd, a2["double_demeaning"]["r_dd"]); d3(lo, a2["double_demeaning"]["ci"][0]); d3(hi, a2["double_demeaning"]["ci"][1])
    U3 = {"all": {"X": X, "Y": Y, "draws": dr3}}
    for h in A2.HORIZONS:
        kk = min(h, T)
        if kk <= 1:
            continue
        Xh, Yh = X[:, :kk], Y[:, :kk]
        w = a2["partial_by_horizon"][str(h)]
        d3(A2.corr(A2.double_demean(Xh), A2.double_demean(Yh)), w["r_dd"])
        (lo, hi, _), drh = rec_boot(A2.cboot, lambda i, a=Xh, b=Yh: A2.corr(A2.double_demean(a[i]), A2.double_demean(b[i])),
                                    n_traj, np.random.default_rng(30 + h))
        d3(lo, w["r_dd_ci"][0]); d3(hi, w["r_dd_ci"][1])
        U3[str(h)] = {"X": Xh, "Y": Yh, "draws": drh}
    A["U3"] = {"pass": bool(d3.d <= TOL), "max_abs_diff": d3.d, "against": "results/a2_trajectory_level_control.json"}

    # U6, released
    d1 = J("task_d_nind20.json")["d1_by_horizon"]
    total = np.sqrt(alea ** 2 + epi ** 2)
    d6, U6 = Diff(), {}
    for h in TDN.HORIZONS:
        sl = slice(START, START + h)
        for q, sig in (("aleatoric", alea[:, sl]), ("epistemic", epi[:, sl]), ("total", total[:, sl])):
            e, s = abs_err[:, sl].reshape(-1, 45), sig.reshape(-1, 45)
            npos_p = npos_s = nfin = 0
            for d in range(45):
                sd, ed = s[:, d], e[:, d]
                m = np.isfinite(sd) & np.isfinite(ed)
                if m.sum() > 2 and sd[m].std() > 0 and ed[m].std() > 0:
                    nfin += 1
                    npos_p += np.corrcoef(sd[m], ed[m])[0, 1] > 0
                    npos_s += np.corrcoef(avg_rank(sd[m]), avg_rank(ed[m]))[0, 1] > 0
            d6(npos_p, d1[str(h)][q]["n_positive"]); d6(nfin, d1[str(h)][q]["n_finite_corr"])
            U6[f"rel_{q}_h{h}"] = {"pearson_n_positive": int(npos_p), "spearman_n_positive": int(npos_s), "n_finite": nfin}

    # ---------------- U2: the ensemble-5 arms, M-43 ----------------
    ar = C.arena((1, 8))
    R5 = {s: XB.roll(C.load_ens5(C.ens5_weights((1, 8), s))[0], ar) for s in C.ENS5_SEEDS}
    gov = J("task_d3_ens5.json")["governing"]
    cal = J("task_d3_ens5.json")["calibration"]
    d2u, U2 = Diff(), {}
    for h in TD.HORIZONS:
        for j, s in enumerate(C.ENS5_SEEDS):
            err = R5[s]["err"][:, START:START + h].sum(-1)
            dis = R5[s]["epi_s"][:, START:START + h]
            fi = np.broadcast_to(np.arange(err.shape[1], dtype=np.float64), err.shape).copy()
            w = gov[str(h)]["per_seed"][j]
            d2u(TD.pooled_corr(fi, err) if h > 1 else None, w["r_index"]); d2u(TD.pooled_corr(dis, err), w["r_disagreement"])
            d2u(TD.partial_corr(dis, err, fi) if h > 1 else None, w["r_partial"])
            drw = None
            if h > 1:
                f = lambda i: (None if (TD.pooled_corr(dis[i], err[i]) is None or TD.pooled_corr(fi[i], err[i]) is None)
                               else TD.pooled_corr(dis[i], err[i]) - TD.pooled_corr(fi[i], err[i]))
                (lo, hi, _), drw = rec_boot(TD.cluster_boot, f, 4, np.random.default_rng(0))
                d2u(lo, w["paired_ci_lo"]); d2u(hi, w["paired_ci_hi"])
            U2[f"h{h}_seed{s}"] = {"F": fi, "E": err, "S": dis, "draws": drw, "h": h}
    A["U2"] = {"pass": bool(d2u.d <= TOL), "max_abs_diff": d2u.d, "against": "results/task_d3_ens5.json governing"}
    # ensemble-5 per-dimension counts need the epistemic sigma, which XB.roll does not return; X11a's roll does
    import x11a_fold_ens5_calibration as XA
    for s in C.ENS5_SEEDS:
        m, sd_ = C.load_ens5(C.ens5_weights((1, 8), s))
        r = XA.roll(m, sd_, ar)
        for j_h, h in enumerate(TD.HORIZONS):
            e = r["err"][:, START:START + h].reshape(-1, 45)
            g = r["epi"][:, START:START + h].reshape(-1, 45)
            npos_p = npos_s = 0
            for d in range(45):
                a, b = g[:, d], e[:, d]
                if a.std() > 0 and b.std() > 0:
                    npos_p += np.corrcoef(a, b)[0, 1] > 0
                    npos_s += np.corrcoef(avg_rank(a), avg_rank(b))[0, 1] > 0
            d6(npos_p, cal[str(h)]["per_seed"][C.ENS5_SEEDS.index(s)]["n_positive"])
            U6[f"e5_seed{s}_h{h}"] = {"pearson_n_positive": int(npos_p), "spearman_n_positive": int(npos_s)}
    A["U6"] = {"pass": bool(d6.d == 0), "max_abs_diff": d6.d,
               "against": "results/task_d_nind20.json d1_by_horizon[*].n_positive; task_d3_ens5.json calibration per_seed n_positive"}

    # ---------------- U4: e7 ----------------
    e7 = {r["baseline"]: r for r in J("e7_free_baselines.json")["baselines"]}
    D = E7.load_panel()
    B = E7.baselines(D)
    err, dis, fidx7 = D["err"], D["dis"], D["fidx"]
    rng = np.random.default_rng(20260829)
    n = D["n_traj"]
    d4, U4 = Diff(), {}
    for name, b in list(B.items()) + [("forecast-index", fidx7)]:
        w = e7[name]
        dm = [rng.integers(0, n, n) for _ in range(E7.N_BOOT)]
        dp = [rng.integers(0, n, n) for _ in range(E7.N_BOOT)]
        vm = [E7._corr(dis[i], err[i]) - E7._corr(b[i], err[i]) for i in dm]
        vp = [E7._partial(dis[i], err[i], b[i]) for i in dp]
        ci_m, _ = ci_of(vm)
        ci_p, _ = ci_of(vp)
        d4(E7._corr(b, err), w["r_baseline_error"]); d4(E7._corr(dis, err) - E7._corr(b, err), w["margin"])
        d4(E7._partial(dis, err, b), w["partial_disagreement_given_baseline"])
        for x_, y_ in zip(ci_m + ci_p, w["margin_ci"] + w["partial_ci"]):
            d4(x_, y_)
        U4[name] = {"b": b, "dm": dm, "dp": dp}
    A["U4"] = {"pass": bool(d4.d <= TOL), "max_abs_diff": d4.d, "against": "results/e7_free_baselines.json baselines"}

    # ---------------- U5: x6 ----------------
    x6 = J("x6_stepsize_short_units.json")
    d5, U5 = Diff(), {}
    for h in X6.HS:
        D5, _ = X6.panel(h)
        B5 = E7.baselines(D5)
        er, di, stp, n5 = D5["err"], D5["dis"], B5["step-size"], D5["n_traj"]
        rng5 = np.random.default_rng(X6.BOOT_SEED)
        dm = [rng5.integers(0, n5, n5) for _ in range(X6.N_BOOT)]
        dp = [rng5.integers(0, n5, n5) for _ in range(X6.N_BOOT)]
        ci_m, _ = ci_of([X6.margin_of(di, stp, er)(i) for i in dm])
        ci_p, _ = ci_of([E7._partial(di[i], er[i], stp[i]) for i in dp])
        mg = E7._corr(di, er) - E7._corr(stp, er)
        if h == X6.H_READ:
            d5(mg, x6["reading"]["margin"]); [d5(a, b) for a, b in zip(ci_m, x6["reading"]["ci95"])]
        else:
            d5(mg, x6["alongside"][f"h{h}"]["margin"]); [d5(a, b) for a, b in zip(ci_m, x6["alongside"][f"h{h}"]["margin_ci"])]
        pw = x6["alongside"]["partial_disagreement_given_step_size"][str(h)]
        d5(E7._partial(di, er, stp), pw["value"]); [d5(a, b) for a, b in zip(ci_p, pw["ci95"])]
        U5[str(h)] = {"err": er, "dis": di, "step": stp, "dm": dm, "dp": dp, "n": n5}
    A["U5"] = {"pass": bool(d5.d <= TOL), "max_abs_diff": d5.d, "against": "results/x6_stepsize_short_units.json"}

    for k, v in A.items():
        print(f"  assertion {k}: {'PASS' if v['pass'] else 'FAIL'}  {v['max_abs_diff']}")
    if not all(v["pass"] for v in A.values()):
        C.blocked(OUT, "a Pearson reproduction failed", assertions=A)

    # ---------------- timing probe ----------------
    u = U1["all"]
    tp = time.perf_counter()
    for i in u["draws"][:200]:
        sp(u["S"][i], u["E"][i])
    per_draw = (time.perf_counter() - tp) / 200
    n_draws = sum(4 * len(v["draws"]) for v in U1.values()) + sum(len(v["draws"]) for v in U3.values())
    proj_min = per_draw * n_draws * 1.5 / 60
    print(f"  timing: {per_draw * 1e3:.2f} ms per Spearman draw at U1 h = all; projected about {proj_min:.0f} min")

    # ---------------- rank statistics ----------------
    R1 = {}
    for h, u in U1.items():
        F_, E_, S_ = u["F"], u["E"], u["S"]
        row = {"sp_idx": sp(F_, E_), "sp_epi": sp(S_, E_), "sp_par": sp_partial(S_, E_, F_)}
        row["sp_diff"] = None if row["sp_idx"] is None else row["sp_epi"] - row["sp_idx"]
        b_idx = [sp(F_[i], E_[i]) for i in u["draws"]]
        b_epi = [sp(S_[i], E_[i]) for i in u["draws"]]
        b_par = [sp_partial(S_[i], E_[i], F_[i]) for i in u["draws"]]
        b_dif = [None if (a is None or b is None) else b - a for a, b in zip(b_idx, b_epi)]
        for k_, bv in (("idx", b_idx), ("epi", b_epi), ("par", b_par), ("diff", b_dif)):
            if row[f"sp_{k_}"] is not None:
                row[f"sp_{k_}_ci"], row[f"sp_{k_}_n_finite"] = ci_of(bv)
        if h != "1":
            row["kt_idx"], row["kt_epi"] = tau_b(F_, E_), tau_b(S_, E_)
            row["kt_par"] = tau_partial(S_, E_, F_)
        else:
            row["kt_epi"] = tau_b(S_, E_)
        R1[h] = row
        print(f"  U1 h={h}: Spearman idx {row['sp_idx']} epi {row['sp_epi']:.4f} diff {row['sp_diff']}")
    R2 = {}
    for key, u in U2.items():
        F_, E_, S_ = u["F"], u["E"], u["S"]
        row = {"sp_idx": sp(F_, E_, TD.pooled_corr) if u["h"] > 1 else None, "sp_dis": sp(S_, E_, TD.pooled_corr),
               "sp_par": sp_partial(S_, E_, F_, TD.partial_corr) if u["h"] > 1 else None}
        if u["h"] > 1:
            row["sp_diff"] = row["sp_dis"] - row["sp_idx"]
            bv = [None if (sp(S_[i], E_[i], TD.pooled_corr) is None or sp(F_[i], E_[i], TD.pooled_corr) is None)
                  else sp(S_[i], E_[i], TD.pooled_corr) - sp(F_[i], E_[i], TD.pooled_corr) for i in u["draws"]]
            row["sp_diff_ci"], row["sp_diff_n_finite"] = ci_of(bv)
        R2[key] = row
    R3 = {}
    for h, u in U3.items():
        Xh, Yh = u["X"], u["Y"]
        v = sp(A2.double_demean(Xh), A2.double_demean(Yh), A2.corr)
        bv = [sp(A2.double_demean(Xh[i]), A2.double_demean(Yh[i]), A2.corr) for i in u["draws"]]
        ci, nf = ci_of(bv)
        R3[h] = {"sp_rdd": v, "sp_rdd_ci": ci, "n_finite": nf}
    R3["all"]["kt_rdd"] = tau_b(A2.double_demean(U3["all"]["X"]), A2.double_demean(U3["all"]["Y"]))
    R4 = {}
    for name, u in U4.items():
        b = u["b"]
        row = {"sp_r": sp(b, err, E7._corr), "sp_r_dis": sp(dis, err, E7._corr),
               "sp_partial": sp_partial(dis, err, b, E7._partial)}
        row["sp_margin"] = row["sp_r_dis"] - row["sp_r"]
        row["sp_margin_ci"], _ = ci_of([sp(dis[i], err[i], E7._corr) - sp(b[i], err[i], E7._corr) for i in u["dm"]])
        row["sp_partial_ci"], _ = ci_of([sp_partial(dis[i], err[i], b[i], E7._partial) for i in u["dp"]])
        row["kt_r"], row["kt_r_dis"] = tau_b(b, err), tau_b(dis, err)
        R4[name] = row
    R5_ = {}
    for h, u in U5.items():
        er, di, stp = u["err"], u["dis"], u["step"]
        row = {"sp_r_dis": sp(di, er, E7._corr), "sp_r_step": sp(stp, er, E7._corr),
               "sp_partial": sp_partial(di, er, stp, E7._partial)}
        row["sp_margin"] = row["sp_r_dis"] - row["sp_r_step"]
        row["sp_margin_ci"], _ = ci_of([sp(di[i], er[i], E7._corr) - sp(stp[i], er[i], E7._corr) for i in u["dm"]])
        row["sp_partial_ci"], _ = ci_of([sp_partial(di[i], er[i], stp[i], E7._partial) for i in u["dp"]])
        row["kt_r_dis"], row["kt_r_step"] = tau_b(di, er), tau_b(stp, er)
        R5_[h] = row
        print(f"  U5 h={h}: Spearman margin {row['sp_margin']:.4f} {row['sp_margin_ci']}")
    clean = lambda d: {k: v for k, v in d.items()}
    out = {"analysis": "N11", "post_hoc": True,
           "never_reopens": ("M-43, M-45, M-51, X6 or any discharged rule; each verdict keeps the Pearson statistic it was "
                             "committed with; nothing here changes a verdict"),
           "script": "scripts/n11_rank_correlations.py", "script_sha256": C.sha256("scripts/n11_rank_correlations.py"),
           "design": {"spearman": "Pearson of average ranks of the same finite pairs, re-ranked inside every draw",
                      "kendall": "tau_b exact, point estimates only; partial tau by Kendall's formula",
                      "draws": "each original script's own generator and loop, recorded and reused",
                      "specification": "docs/presubmission/round5/PROTOCOLS.md §5 N11"},
           "self_test": st_, "assertions": A,
           "timing_probe": {"ms_per_spearman_draw_u1_all": per_draw * 1e3, "projected_minutes": proj_min},
           "U1_d2_forecast_index": R1, "U2_m43_ens5": R2, "U3_a2_rdd": R3, "U4_e7_free_baselines": R4,
           "U5_x6_short_units": R5_, "U6_npos": U6,
           "code_sha256": {p: C.sha256(p) for p in MODULES},
           "git_head": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
           "timing": {"wall_clock_s": time.perf_counter() - t0, "torch_threads": torch.get_num_threads(),
                      "cpu_count": os.cpu_count()}}
    json.dump(out, open(OUT, "w"), indent=1)
    print(f"  wrote {R.rel(OUT)}")


if __name__ == "__main__":
    main()
