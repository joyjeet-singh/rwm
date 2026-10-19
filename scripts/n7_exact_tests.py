"""
N7 (round 5; POST HOC) -- exact randomisation tests wherever the paper reports a paired comparison at
n_independent = 4 with a bootstrap interval, and the exact episode-level test for the 20-trajectory arenas.
docs/presubmission/round5/PROTOCOLS.md §5 N7 is the specification; this is a summary. It never re-opens a rule and
changes no verdict: every stored verdict, interval and p stands as committed, and this reports beside them what an
exact test gives.

TEST. For n values d_1..d_n: T = mean(d); over all 2^n sign vectors e, two-sided p = #{e : |mean(e*d)| >= |T| - 1e-12}
/ 2^n; "k of n" = how many d_u carry T's sign. Smallest attainable p = 2 / 2^n: 0.125 at n = 4, 0.00195 at n = 10.
UNITS. The trajectory at n = 4; the episode (the mean of its two trajectories) for the 20-trajectory arenas. Seeds are
averaged within trajectory first (M-27). Per-shared-seed comparisons are tested per seed as stored and seed-averaged.
INPUTS (stored per-trajectory values unless noted): 1 a1_ab_by_horizon; 2 mn_sweep_verdict (governing and the
held-out alongsides); 3 baselines_verdict M-75 and M-76 (the same); 4 x4_matched_baselines; 5 r2_independent_ensemble,
r2_combined_arm, m49_capacity_matched (per shared seed) and r2_combined_arm m68.objective_isolated; 6 alignment_defect_ci
held_out_n4; 7 task_d3_ens5's M-43, re-rolled, as a WITHIN-trajectory estimand; 8 x3_cross_fold, a1's per-episode sign
test, and X9's (a) and (d) per-trajectory values (episode level).
ASSERTIONS, before any test (PROTOCOLS' tolerances): stored points and intervals reproduced from the stored lists by each
artifact's own functions; see assert_* below.
Writes results/n7_exact_tests.json. Run from the repository root.
"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import rwm_data as R  # noqa: E402
import rwm_metrics as MET  # noqa: E402
import p5_sweep_power as P5  # noqa: E402
import review_bootstrap_unit as RB  # noqa: E402
import a1_ab_by_horizon as A1  # noqa: E402
import task_d3_ens5 as TD  # noqa: E402
import x11_common as C  # noqa: E402
import x11b_fold_m43 as XB  # noqa: E402

OUT = os.path.join(R.RESULTS, "n7_exact_tests.json")
J = lambda n: json.load(open(os.path.join(R.RESULTS, n)))
HS = ("1", "8", "32", "100", "128", "368")
MODULES = ("scripts/n7_exact_tests.py", "scripts/p5_sweep_power.py", "scripts/review_bootstrap_unit.py",
           "scripts/a1_ab_by_horizon.py", "scripts/task_d3_ens5.py", "scripts/x11b_fold_m43.py", "scripts/x11_common.py")


def flip(d):
    d = np.asarray(d, dtype=np.float64)
    n = len(d)
    T = float(d.mean())
    eps = 1 - 2 * ((np.arange(2 ** n)[:, None] >> np.arange(n)[None, :]) & 1)
    p = float((np.abs((eps * d).mean(1)) >= abs(T) - 1e-12).sum() / 2 ** n)
    k = int((np.sign(d) == np.sign(T)).sum()) if T != 0 else 0
    return {"n": n, "T": T, "p": p, "k": k, "p_min": 2.0 / 2 ** n}


class Rows:
    def __init__(self):
        self.rows, self.d = [], 0.0

    def add(self, src, path, d, unit="trajectory", stored_ci=None, stored_p=None, note=None):
        r = {"source": src, "path": path, "unit": unit, **flip(d), "values": [float(x) for x in d]}
        if stored_ci is not None:
            r["stored_interval"] = [float(x) for x in stored_ci]
        if stored_p is not None:
            r["stored_p"] = float(stored_p)
        if note:
            r["note"] = note
        self.rows.append(r)
        return r


def episodes_of(starts):
    _, _, ep = C.data()
    return [int(ep[s]) for s in starts]


def by_episode(vals, eps):
    out = {}
    for v, e in zip(vals, eps):
        out.setdefault(e, []).append(v)
    assert all(len(x) == 2 for x in out.values()) and len(out) == 10, {k: len(v) for k, v in out.items()}
    return [float(np.mean(out[e])) for e in sorted(out)]


def main():
    os.chdir(C.ROOT)
    t0 = time.perf_counter()
    rows, A = Rows(), {}

    # 1 -------------------------------------------------------------- a1
    a1 = J("a1_ab_by_horizon.json")
    d1p = d1i = 0.0
    for h in HS:
        b = a1["by_horizon"][h]
        g = np.asarray(b["gap_per_trajectory"])
        # a1's own arithmetic: the float32 mean of its float32 per-trajectory array (a1_ab_by_horizon.py:156,170;
        # DECISIONS.md#G4-n7-a1)
        d1p = max(d1p, abs(float(np.asarray(b["gap_per_trajectory"], dtype=np.float32).mean()) - b["gap"]))
        _, lo, hi = RB.boot_cluster(np.asarray(b["A_per_trajectory"])[None], np.asarray(b["B_per_trajectory"])[None],
                                    n=A1.N_BOOT, seed=A1.BOOT_SEED)
        d1i = max(d1i, abs(lo - b["gap_ci"][0]), abs(hi - b["gap_ci"][1]))
        rows.add("results/a1_ab_by_horizon.json", f"by_horizon/{h}/gap_per_trajectory", g, stored_ci=b["gap_ci"])
    A["1"] = {"pass": bool(d1p <= 1e-12 and d1i <= 1e-7), "point_max_abs_diff": d1p, "interval_max_abs_diff": d1i,
              "tolerances": [1e-12, 1e-7]}

    # 2-4 ------------------------------------------------------------ the Holm families and their alongsides
    d24p = d24i = 0.0
    fam = {}

    def node(src, path, x, family=None):
        nonlocal d24p, d24i
        pt = np.asarray(x["per_traj"])
        d24p = max(d24p, abs(pt.mean() - x["D"]))
        ci, p = P5.boot_ci(pt), P5.boot_p(pt)
        d24i = max(d24i, abs(ci[0] - x["ci95"][0]), abs(ci[1] - x["ci95"][1]), abs(p - x["p"]))
        r = rows.add(src, path, pt, stored_ci=x["ci95"], stored_p=x["p"])
        if family:
            fam.setdefault(family, []).append(r)

    sw = J("mn_sweep_verdict.json")
    for c, x in sw["governing"]["per_config"].items():
        node("results/mn_sweep_verdict.json", f"governing/per_config/{c}", x, "sweep M-74")
    for k, blk in sw["alongside"].items():
        for c, x in blk["per_config"].items():
            node("results/mn_sweep_verdict.json", f"alongside/{k}/per_config/{c}", x)
    bv = J("baselines_verdict.json")
    for rule in ("M-75", "M-76"):
        rr = bv["rules"][rule]
        for bl, x in rr["governing"]["per_baseline"].items():
            node("results/baselines_verdict.json", f"rules/{rule}/governing/per_baseline/{bl}", x, f"baselines {rule}")
        for k, blk in rr["alongside"].items():
            for bl, x in blk["per_baseline"].items():
                node("results/baselines_verdict.json", f"rules/{rule}/alongside/{k}/per_baseline/{bl}", x)
    x4 = J("x4_matched_baselines.json")
    for bl, x in x4["reading"]["per_baseline"].items():
        node("results/x4_matched_baselines.json", f"reading/per_baseline/{bl}", x, "x4 X4")
    for k in ("l1_h100", "l1_h32"):
        for bl, x in x4["alongside"][k]["per_baseline"].items():
            node("results/x4_matched_baselines.json", f"alongside/{k}/per_baseline/{bl}", x)
    A["2-4"] = {"pass": bool(d24p <= 1e-12 and d24i <= 1e-12), "point_max_abs_diff": d24p,
                "interval_and_p_max_abs_diff": d24i, "tolerance": 1e-12,
                "functions": "p5_sweep_power.boot_ci, boot_p (scripts/p5_sweep_power.py:124-139)"}
    alpha = {"sweep M-74": sw["alpha"], "baselines M-75": bv["alpha"], "baselines M-76": bv["alpha"], "x4 X4": 0.05}
    families = {}
    for f, rs in fam.items():
        m = len(rs)
        families[f] = {"m": m, "alpha": alpha[f], "holm_first_level": alpha[f] / m, "p_min_attainable": rs[0]["p_min"],
                       "can_any_reject": bool(rs[0]["p_min"] <= alpha[f] / m),
                       "exact_p": {r["path"].split("/")[-1]: r["p"] for r in rs},
                       "stored_bootstrap_p": {r["path"].split("/")[-1]: r["stored_p"] for r in rs}}

    # 5 -------------------------------------------------------------- per shared seed
    d5 = 0.0
    seedavg = {}
    for src, tag in (("r2_independent_ensemble.json", "r2"), ("r2_combined_arm.json", "r2_combined"),
                     ("m49_capacity_matched.json", "m49")):
        cmp_ = J(src)["comparison"]["per_shared_seed"]
        lrs, cds = [], []
        for s in ("0", "1", "2"):
            x = cmp_[s]
            lr, cd = np.asarray(x["log_ratio_per_trajectory"]), np.asarray(x["coverage_diff_pts_per_trajectory"])
            d5 = max(d5, float(np.abs(np.asarray(x["ratio_per_trajectory"]) - np.exp(lr)).max()))
            d5 = max(d5, abs(cd.mean() - x["coverage_diff_pts"]) * 1e-3)    # scaled: tolerance 1e-9 below
            rows.add(f"results/{src}", f"comparison/per_shared_seed/{s}/log_ratio_per_trajectory", lr, stored_ci=x["log_ratio_ci"])
            rows.add(f"results/{src}", f"comparison/per_shared_seed/{s}/coverage_diff_pts_per_trajectory", cd,
                     stored_ci=x["coverage_ci_pts"])
            lrs.append(lr); cds.append(cd)
        seedavg[tag] = {"log_ratio": rows.add(f"results/{src}", "comparison/per_shared_seed/mean_over_seeds/log_ratio",
                                              np.mean(lrs, 0), note="seed-averaged within trajectory"),
                        "coverage_diff_pts": rows.add(f"results/{src}", "comparison/per_shared_seed/mean_over_seeds/coverage_diff_pts",
                                                      np.mean(cds, 0), note="seed-averaged within trajectory")}
    ob = J("r2_combined_arm.json")["m68"]["objective_isolated"]
    cd = np.asarray(ob["coverage_diff_pts_per_trajectory"])
    d5c = abs(cd.mean() - ob["coverage_diff_pts"])
    rows.add("results/r2_combined_arm.json", "m68/objective_isolated/log_ratio_per_trajectory", ob["log_ratio_per_trajectory"],
             stored_ci=ob["ratio_ci"], note="stored interval is on the ratio")
    rows.add("results/r2_combined_arm.json", "m68/objective_isolated/coverage_diff_pts_per_trajectory", cd,
             stored_ci=ob["coverage_ci_pts"])
    d5r = 0.0
    for src in ("r2_independent_ensemble.json", "r2_combined_arm.json", "m49_capacity_matched.json"):
        for s, x in J(src)["comparison"]["per_shared_seed"].items():
            d5r = max(d5r, float(np.abs(np.asarray(x["ratio_per_trajectory"]) - np.exp(x["log_ratio_per_trajectory"])).max()))
    d5m = max(max(abs(np.mean(x["coverage_diff_pts_per_trajectory"]) - x["coverage_diff_pts"])
                  for x in J(src)["comparison"]["per_shared_seed"].values())
              for src in ("r2_independent_ensemble.json", "r2_combined_arm.json", "m49_capacity_matched.json"))
    d5m = max(d5m, d5c)
    A["5"] = {"pass": bool(d5r <= 1e-12 and d5m <= 1e-9), "ratio_vs_exp_log_max_abs_diff": d5r,
              "coverage_mean_max_abs_diff": d5m, "tolerances": [1e-12, 1e-9]}

    # 6 -------------------------------------------------------------- alignment
    al = J("alignment_defect_ci.json")["arenas"]["held_out_n4"]
    d6 = 0.0
    for m in ("rel_l1", "nrmse_form1"):
        o0, o1 = np.asarray(al["per_trajectory"]["offset0"][m]), np.asarray(al["per_trajectory"]["offset1"][m])
        ov = np.asarray(al["per_trajectory_overstatement_pct"][m])
        d6 = max(d6, float(np.abs(ov - 100 * (o0 - o1) / o1).max()))
        rows.add("results/alignment_defect_ci.json", f"arenas/held_out_n4/per_trajectory/offset0-offset1/{m}", o0 - o1)
        rows.add("results/alignment_defect_ci.json", f"arenas/held_out_n4/per_trajectory_overstatement_pct/{m}", ov,
                 stored_ci=al["ci95_pct"][m])
    A["6"] = {"pass": bool(d6 <= 1e-9), "max_abs_diff": d6, "tolerance": 1e-9}

    # 7 -------------------------------------------------------------- M-43, re-rolled, within trajectory
    ar = C.arena((1, 8))
    R5 = {s: XB.roll(C.load_ens5(C.ens5_weights((1, 8), s))[0], ar) for s in C.ENS5_SEEDS}
    gov, _ = XB.governing(R5, 4)
    want = J("task_d3_ens5.json")["governing"]
    d7 = 0.0
    for h in ("8", "32", "128", "368"):
        for g_, w_ in zip(gov[h]["per_seed"], want[h]["per_seed"]):
            for k in ("r_index", "r_disagreement", "paired_diff", "paired_ci_lo", "paired_ci_hi"):
                d7 = max(d7, abs(g_[k] - w_[k]))
    A["7"] = {"pass": bool(d7 <= 1e-9), "max_abs_diff": d7, "tolerance": 1e-9,
              "against": "results/task_d3_ens5.json governing (r_index, r_disagreement, paired_diff and its interval)"}
    m43 = {}
    for h in (8, 32, 128, 368):
        per_seed = []
        for s in C.ENS5_SEEDS:
            err = R5[s]["err"][:, C.START:C.START + h].sum(-1)
            dis = R5[s]["epi_s"][:, C.START:C.START + h]
            fi = np.broadcast_to(np.arange(h, dtype=np.float64), err.shape).copy()
            per_seed.append([TD.pooled_corr(dis[t:t + 1], err[t:t + 1]) - TD.pooled_corr(fi[t:t + 1], err[t:t + 1])
                             for t in range(4)])
        d = np.mean(per_seed, 0)
        r = rows.add("results/task_d3_ens5.json", f"governing/{h} (re-rolled; within-trajectory)", d,
                     note="WITHIN-trajectory estimand r_t(disagreement, error) - r_t(index, error), seed-averaged; the stored "
                          "statistic is a correlation pooled over trajectories and has no per-trajectory decomposition")
        r["k_per_seed"] = [int((np.asarray(x) > 0).sum()) for x in per_seed]
        r["stored_pooled_paired_diff_per_seed"] = [x["paired_diff"] for x in want[str(h)]["per_seed"]]
        m43[str(h)] = r

    # 8 -------------------------------------------------------------- the 20-trajectory arenas, episode level
    x3 = J("x3_cross_fold.json")
    pt = x3["per_trajectory"]
    eps3 = pt["episode"]
    d8 = 0.0
    x3rows = {}
    for h in HS:
        gap = (np.mean(pt["armB_per_seed_l1"][h], 0) - np.mean(pt["armA_per_seed_l1"][h], 0))
        if h == "368":
            d8 = max(d8, abs(gap.mean() - x3["reading"]["gap"]))
            st = x3["part_of_rule"]["per_episode_sign_test_h368"]["per_episode_mean_gap"]
            pe = by_episode(gap, eps3)
            d8 = max(d8, max(abs(pe[i] - st[str(e)]) for i, e in enumerate(sorted(set(eps3)))))
        x3rows[h] = rows.add("results/x3_cross_fold.json", f"per_trajectory gap B-A, h = {h} (episode level)",
                             by_episode(gap, eps3), unit="episode")
    A["8"] = {"pass": bool(d8 <= 1e-9), "max_abs_diff": d8, "tolerance": 1e-9,
              "against": "results/x3_cross_fold.json reading.gap and part_of_rule.per_episode_sign_test_h368"}
    a1rows = {}
    for h in HS:
        st = a1["sign_test"].get(h)
        if st:
            a1rows[h] = rows.add("results/a1_ab_by_horizon.json", f"sign_test/{h}/per_episode_gap",
                                 [st["per_episode_gap"][e] for e in sorted(st["per_episode_gap"], key=int)],
                                 unit="episode", stored_p=st["exact_two_sided_p"],
                                 note="stored p is the exact binomial sign test, which ignores magnitudes")
    x9 = J("x9_per_member_propagation.json")
    s20 = MET.non_overlapping_starts(C.data()[2], list(range(R.N_EPISODES)), C.LEN)
    eps_rel = episodes_of(s20)
    eps_fold = episodes_of([t["start_row"] for t in x9["design"]["fold_trajectories"]])
    x9rows = {}
    for a, eps in (("rel", eps_rel), ("fold", eps_fold)):
        for h in HS[1:]:
            tr = x9["tables"][a][h]["per_trajectory"]
            for k in ("f", "log_ratio"):
                x9rows[f"{a}_{k}_h{h}"] = rows.add("results/x9_per_member_propagation.json",
                                                   f"tables/{a}/{h}/per_trajectory/{k} (episode level)",
                                                   by_episode(tr[k], eps), unit="episode")

    for k, v in A.items():
        print(f"  assertion ({k}): {'PASS' if v['pass'] else 'FAIL'}  "
              f"{ {kk: vv for kk, vv in v.items() if kk not in ('pass', 'against', 'functions')} }")
    if not all(v["pass"] for v in A.values()):
        C.blocked(OUT, "a reproduction assertion failed", assertions=A)
    n4 = [r for r in rows.rows if r["n"] == 4]
    out = {"analysis": "N7", "post_hoc": True,
           "never_reopens": ("M-23, M-43, M-44, M-49, M-68, M-74, M-75, M-76, X3, X4, X9 and the alignment defect's "
                             "reading; every stored verdict, interval and p stands; nothing here changes a verdict"),
           "script": "scripts/n7_exact_tests.py", "script_sha256": C.sha256("scripts/n7_exact_tests.py"),
           "design": {"test": "exact two-sided sign-flip over all 2^n sign vectors of the unit differences",
                      "units": "trajectory at n = 4; episode (mean of its two trajectories) for 20-trajectory arenas",
                      "seeds": "averaged within trajectory first (M-27)",
                      "episode_level_held_out_pair": "2 units: the smallest attainable p is 0.5, so no test is possible",
                      "specification": "docs/presubmission/round5/PROTOCOLS.md §5 N7"},
           "assertions": A, "rows": rows.rows, "families": families,
           "summary": {"n_tested": len(rows.rows), "n_n4": len(n4), "p_min_n4": 2.0 / 16,
                       "n_4of4": sum(1 for r in n4 if r["k"] == 4),
                       "n_n4_stored_bootstrap_p_below_005": sum(1 for r in n4 if r.get("stored_p") is not None and r["stored_p"] < 0.05),
                       "m43_within": {h: {"p": r["p"], "k": r["k"]} for h, r in m43.items()},
                       "seed_averaged": {t: {k: {"p": r["p"], "k": r["k"], "T": r["T"]} for k, r in v.items()} for t, v in seedavg.items()},
                       "a1": {h: {"p": r["p"], "k": r["k"]} for h, r in {h: rows.rows[i] for i, h in enumerate(HS)}.items()},
                       "x3_episode": {h: {"p": r["p"], "k": r["k"]} for h, r in x3rows.items()},
                       "a1_episode": {h: {"p": r["p"], "k": r["k"], "stored_binomial_p": r["stored_p"]} for h, r in a1rows.items()},
                       "x9_episode": {k: {"p": r["p"], "k": r["k"]} for k, r in x9rows.items()}},
           "code_sha256": {p: C.sha256(p) for p in MODULES},
           "git_head": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
           "timing": {"wall_clock_s": time.perf_counter() - t0, "cpu_count": os.cpu_count()}}
    json.dump(out, open(OUT, "w"), indent=1)
    print(f"  N7: {len(rows.rows)} rows ({len(n4)} at n = 4, {out['summary']['n_4of4']} of them 4 of 4); families "
          f"{ {f: v['can_any_reject'] for f, v in families.items()} }")
    print(f"  wrote {R.rel(OUT)}")


if __name__ == "__main__":
    main()
