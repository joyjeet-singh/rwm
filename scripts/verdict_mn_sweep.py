"""
M-74 -- the verdict on the configuration claim, computed exactly as the rule states it.

Committed and pushed before the first sweep run starts (PLAN S2a; M-74, "What the
discharging session may and may not do"). Nothing here may change after the runs exist.

THE RULE, as M-74 fixes it (FINDINGS_LEDGER.md, ### M-74):
  statistic   D_c = mean over the 4 held-out trajectories of
                    [3-seed mean err_c(traj) - 3-seed mean err_centre(traj)],
              relative-L1 at h = 368, centre (M, N) = (32, 8).
  test        exact cluster bootstrap over the 4 trajectories: all 4**4 = 256 ordered
              resamples, equally likely, seeds pooled inside each draw; two-sided
              p = min(1, 2 min(P*(D* <= 0), P*(D* >= 0))). The implementation is
              scripts/p5_sweep_power.py's, imported, so the MDE the rule quotes and the
              verdict it returns come from one piece of code.
  Holm        step-down at family-wise alpha = 0.05 over the m configurations run,
              p-values ascending, exact ties broken by M-74's priority order; reject the
              k-th while p_(k) <= alpha / (m - k + 1), stop at the first that fails.
  direction   rejected with D_c > 0 = excludes zero in the centre's favour;
              rejected with D_c < 0 = excludes zero in c's favour.
  branches    first match wins:
              1 NOT OPTIMAL AT OUR BUDGET  some D_c excludes zero in c's favour
              2 REPRODUCES, RESOLVED       every D_c > 0, and every one excludes zero in
                                           the centre's favour
              3 CONSISTENT WITH OPTIMAL    every D_c > 0, none in c's favour, not all
                                           in the centre's
              4 CANNOT BE DISTINGUISHED    anything else
  failure     a configuration without all three seeds, or with a non-finite value, means
              the rule cannot be discharged as written: this script stops, no verdict.

Reported alongside, never governing: every horizon and nRMSE under the same test; the
four per-trajectory differences; the in-sample arena (n_independent = 16, Monte Carlo
cluster bootstrap of 20,000 resamples, generator seed 0, one draw per replicate shared
across configurations, as scripts/a1_ab_by_horizon.py:52-53 and :118-134); the
per-episode sign over all ten episodes; training-window counts; wall_clock_s; the
hold-last floor; and the MDE from results/p5_sweep_power.json.

  python scripts/verdict_mn_sweep.py --self-test   # every branch on synthetic inputs
  python scripts/verdict_mn_sweep.py               # self-test, then the verdict (S8)

Reads results/mn_sweep_eval.json and results/p5_sweep_power.json. Writes
results/mn_sweep_verdict.json.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402

import p5_sweep_power as P5  # noqa: E402

ALPHA = 0.05
CENTRE = "M32_N8"
GOV_METRIC, GOV_H = "l1", "368"
MC_N, MC_SEED = 20000, 0
BRANCHES = ("NOT OPTIMAL AT OUR BUDGET", "REPRODUCES, RESOLVED", "CONSISTENT WITH OPTIMAL",
            "CANNOT BE DISTINGUISHED")


class CannotDischarge(Exception):
    """M-74: the rule cannot be discharged as written."""


# ------------------------------------------------------------- the test
def holm(pvals, order):
    """Holm step-down. pvals: {key: p}; order: the priority order (tie-break).

    Returns {key: {"rank", "level", "p", "rejected"}}.
    """
    m = len(pvals)
    ranked = sorted(pvals, key=lambda k: (pvals[k], order.index(k)))
    out, going = {}, True
    for i, k in enumerate(ranked):
        level = ALPHA / (m - i)
        rej = going and pvals[k] <= level
        if not rej:
            going = False
        out[k] = {"rank": i + 1, "level": level, "p": pvals[k], "rejected": bool(rej)}
    return out


def branch(diffs, rejected):
    """diffs: {key: D_c}; rejected: {key: bool}. Returns (branch, conditions)."""
    c_favour = [k for k in diffs if rejected[k] and diffs[k] < 0]
    centre_favour = [k for k in diffs if rejected[k] and diffs[k] > 0]
    centre_lowest = all(d > 0 for d in diffs.values())
    cond = {"configs_excluding_zero_in_their_favour": c_favour,
            "configs_excluding_zero_in_centre_favour": centre_favour,
            "centre_has_lowest_error": centre_lowest}
    if c_favour:
        return BRANCHES[0], cond
    if centre_lowest and len(centre_favour) == len(diffs):
        return BRANCHES[1], cond
    if centre_lowest:
        return BRANCHES[2], cond
    return BRANCHES[3], cond


def family(per_traj, order, exact=True, draws=None):
    """per_traj: {key: (n_traj,) per-trajectory differences}. The whole governed test."""
    diffs = {k: float(np.mean(v)) for k, v in per_traj.items()}
    if exact:
        p = {k: P5.boot_p(v) for k, v in per_traj.items()}
        ci = {k: P5.boot_ci(v) for k, v in per_traj.items()}
    else:
        p, ci = {}, {}
        for k, v in per_traj.items():
            b = np.asarray(v)[draws].mean(1)
            p[k] = float(min(1.0, 2 * min(np.mean(b <= 0), np.mean(b >= 0))))
            ci[k] = [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]
    h = holm(p, order)
    rejected = {k: h[k]["rejected"] for k in per_traj}
    br, cond = branch(diffs, rejected)
    return {"branch": br, "conditions": cond, "m": len(per_traj),
            "per_config": {k: {"D": diffs[k], "per_traj": [float(x) for x in per_traj[k]],
                               "p": p[k], "ci95": ci[k], **{x: h[k][x] for x in
                                                           ("rank", "level", "rejected")},
                               "direction": (None if not h[k]["rejected"] else
                                             ("centre" if diffs[k] > 0 else "config"))}
                           for k in order if k in per_traj}}


# ------------------------------------------------------------- the data
def seed_mean(rec, arena, metric, h):
    seeds = rec["seeds"]
    if sorted(seeds) != ["0", "1", "2"]:
        raise CannotDischarge(f"M{rec['M']}_N{rec['N']}: seeds {sorted(seeds)}, not 0, 1, 2")
    a = np.array([seeds[s][arena][h][metric] for s in ("0", "1", "2")], dtype=float)
    if not np.all(np.isfinite(a)):
        raise CannotDischarge(f"M{rec['M']}_N{rec['N']}: non-finite {metric} at h={h}")
    return a.mean(0)


def differences(ev, order, arena, metric, h):
    c = seed_mean(ev["configs"][CENTRE], arena, metric, h)
    return {k: seed_mean(ev["configs"][k], arena, metric, h) - c for k in order}


def main_verdict():
    ev = json.load(open(os.path.join(P5.R.RESULTS, "mn_sweep_eval.json")))
    p5 = json.load(open(os.path.join(P5.R.RESULTS, "p5_sweep_power.json")))
    timing = json.load(open(os.path.join(P5.R.RESULTS, "mn_sweep_timing.json")))
    order = [f"M{m}_N{n}" for m, n in timing["queued_configs"]]
    # The priority order breaks Holm ties, and ties at p = 0 are routine, so it is checked
    # against M-74's own grid (p5_sweep_power.GRID) rather than taken from the queue:
    # what was run must be that grid, or a prefix of it after a drop from the bottom.
    grid = [f"M{m}_N{n}" for m, n in P5.GRID]
    if order != grid[:len(order)] or not order:
        raise CannotDischarge(f"queued order {order} is not a prefix of M-74's grid {grid}")
    if timing.get("dropped_configs") and not timing.get("drop_recorded_in"):
        raise CannotDischarge(f"configurations {timing['dropped_configs']} were dropped with "
                              f"no ledger entry recording the drop (M-74)")
    missing = [k for k in [CENTRE] + order if k not in ev["configs"]]
    if missing:
        raise CannotDischarge(f"configurations queued but not scored: {missing}")
    ho, ins_ = ev["arenas"]["held_out"], ev["arenas"]["in_sample"]
    if ho["n_independent"] != 4 or ho["starts"] != p5["traj_start_row"]:
        raise CannotDischarge(f"held-out arena is not M-74's: {ho['starts']}")
    if ins_["n_independent"] != 16:
        raise CannotDischarge(f"in-sample arena has n_independent {ins_['n_independent']}, not 16")

    gov = family(differences(ev, order, "held_out", GOV_METRIC, GOV_H), order)
    alongside = {f"{mt}_h{h}": family(differences(ev, order, "held_out", mt, str(h)), order)
                 for mt in ("l1", "nrmse") for h in ev["horizons"]}
    ins = ev["arenas"]["in_sample"]
    rng = np.random.default_rng(MC_SEED)
    draws = rng.integers(0, ins["n_independent"], size=(MC_N, ins["n_independent"]))
    in_sample = {f"{mt}_h{h}": family(differences(ev, order, "in_sample", mt, str(h)), order,
                                      exact=False, draws=draws)
                 for mt in ("l1", "nrmse") for h in ("100", "368")}

    # Per-episode sign over all ten episodes: each episode's two windows, averaged.
    eps = {}
    for a in ("held_out", "in_sample"):
        d = differences(ev, order, a, GOV_METRIC, GOV_H)
        for k in order:
            for w, e in enumerate(ev["arenas"][a]["episode_of_window"]):
                eps.setdefault(k, {}).setdefault(e, []).append(float(d[k][w]))
    sign_counts = {k: {"positive": int(sum(bool(np.mean(v) > 0) for v in eps[k].values())),
                       "negative": int(sum(bool(np.mean(v) < 0) for v in eps[k].values())),
                       "n_episodes": len(eps[k]),
                       "per_episode": {str(e): float(np.mean(v)) for e, v in sorted(eps[k].items())}}
                   for k in order}

    runs = {k: {s: {"wall_clock_s": ev["configs"][k]["seeds"][s]["wall_clock_s"],
                    "n_train_windows": ev["configs"][k]["seeds"][s]["n_train_windows"]}
                for s in ev["configs"][k]["seeds"]} for k in [CENTRE] + order}
    floor = {a: {h: float(np.mean(ev["floor"][a][h]["l1"])) for h in ("100", "368")}
             for a in ("held_out", "in_sample")}
    mde = {k: p5["estimates"][k]["binding_mde_pct_of_centre"]
           for k in ("l1_h368", "l1_h100", "nrmse_h368", "nrmse_h100")}
    out = {"rule": "M-74", "verdict": gov["branch"], "governing": gov,
           "governing_metric": "relative-L1", "governing_horizon": 368,
           "priority_order": order, "alpha": ALPHA,
           "alongside": alongside, "in_sample": in_sample,
           "in_sample_bootstrap": {"n_resamples": MC_N, "generator_seed": MC_SEED,
                                   "draws_shared_across_configs": True},
           "per_episode_sign": sign_counts, "runs": runs, "hold_last_floor_l1": floor,
           "mde_pct_of_centre_holm_step_1": mde, "mde_source": "results/p5_sweep_power.json",
           "inputs": ["results/mn_sweep_eval.json", "results/p5_sweep_power.json",
                      "results/mn_sweep_timing.json"]}
    json.dump(out, open(os.path.join(P5.R.RESULTS, "mn_sweep_verdict.json"), "w"), indent=2)
    print(f"  M-74 returns: {gov['branch']}")
    for k, v in gov["per_config"].items():
        print(f"    {k:<8} D {v['D']:+.4f}  p {v['p']:.5f}  Holm rank {v['rank']} level "
              f"{v['level']:.5f}  {'REJECTED toward ' + v['direction'] if v['rejected'] else 'not rejected'}")
    print(f"  wrote {os.path.relpath(os.path.join(P5.R.RESULTS, 'mn_sweep_verdict.json'), P5.R.REPO_ROOT)}")


# ------------------------------------------------------------- self-test
def self_test():
    """Every branch, the test's arithmetic and the failure path, on synthetic inputs."""
    order = [f"c{i}" for i in range(8)]
    up = np.array([0.3, 0.2, 0.25, 0.1])            # all four positive
    fails = []

    def check(name, cond):
        print(f"    {'ok  ' if cond else 'FAIL'} {name}")
        if not cond:
            fails.append(name)

    # the exact bootstrap's sign structure, which M-74 states in advance
    check("all four share a sign -> p = 0", P5.boot_p(up) == 0.0)
    check("3 of 4 with a dominated minority -> p = 2/256",
          P5.boot_p(np.array([0.5, 0.5, 0.5, -0.01])) == 2 / 256)
    check("2 of 4 -> p >= 0.125", P5.boot_p(np.array([0.5, 0.5, -0.01, -0.01])) >= 0.125)
    brute = np.mean([np.mean([up[i] for i in idx]) <= 0
                     for idx in __import__("itertools").product(range(4), repeat=4)])
    check("exact tail equals a brute-force enumeration", brute == 0.0)

    # branch 1: one configuration beats the centre on all four trajectories
    f = family({k: (up if k != "c3" else -up) for k in order}, order)
    check("NOT OPTIMAL when one config excludes zero in its favour",
          f["branch"] == BRANCHES[0] and f["conditions"]["configs_excluding_zero_in_their_favour"] == ["c3"])
    # branch 2: every config worse on all four trajectories
    f = family({k: up for k in order}, order)
    check("REPRODUCES, RESOLVED when every D_c excludes zero for the centre", f["branch"] == BRANCHES[1])
    # branch 3: all worse in point estimate, one unresolvable (2 of 4)
    mixed_pos = np.array([0.6, 0.5, -0.1, -0.1])
    f = family({k: (up if k != "c0" else mixed_pos) for k in order}, order)
    check("CONSISTENT WITH OPTIMAL when all D_c > 0 but one is unresolved", f["branch"] == BRANCHES[2])
    # branch 4: one config lower in point estimate but unresolvable
    mixed_neg = -mixed_pos
    f = family({k: (up if k != "c5" else mixed_neg) for k in order}, order)
    check("CANNOT BE DISTINGUISHED when a D_c <= 0 is not rejected", f["branch"] == BRANCHES[3])
    # an exact zero is not 'the centre has the lowest error'
    zero = np.array([0.1, -0.1, 0.2, -0.2])
    f = family({k: (up if k != "c1" else zero) for k in order}, order)
    check("D_c = 0 exactly -> CANNOT BE DISTINGUISHED", f["branch"] == BRANCHES[3])

    # Holm: a 3-of-4 pattern (p = 2/256) is rejected only from step 3 of 8 onward
    three = np.array([0.5, 0.5, 0.5, -0.01])
    f = family({"c0": three, **{k: mixed_pos for k in order[1:]}}, order)
    check("3-of-4 not rejected at Holm step 1 of 8", not f["per_config"]["c0"]["rejected"])
    f = family({"c0": up, "c1": up, "c2": three, **{k: mixed_pos for k in order[3:]}}, order)
    check("3-of-4 rejected at Holm step 3 of 8, after two rejections",
          f["per_config"]["c2"]["rejected"] and f["per_config"]["c2"]["rank"] == 3)
    # Holm stops at the first failure: nothing after it is rejected
    f = family({"c0": up, "c1": mixed_pos, "c2": up, **{k: mixed_pos for k in order[3:]}}, order)
    ranks = sorted(f["per_config"].values(), key=lambda v: v["rank"])
    first_fail = next(i for i, v in enumerate(ranks) if not v["rejected"])
    check("Holm step-down stops at the first failure",
          not any(v["rejected"] for v in ranks[first_fail:]))
    # exact ties broken by the priority order
    f = family({k: up for k in order}, order)
    check("tied p-values ranked in priority order",
          [f["per_config"][k]["rank"] for k in order] == list(range(1, 9)))
    # a dropped configuration: m shrinks and the levels loosen
    f = family({k: up for k in order[:6]}, order[:6])
    check("m = 6 after a drop, first level alpha/6", abs(f["per_config"]["c0"]["level"] - ALPHA / 6) < 1e-15)

    # branches are exhaustive and mutually exclusive over random inputs
    rng = np.random.default_rng(1)
    exclusive = True
    for _ in range(300):
        pt = {k: rng.normal(rng.normal(0, 0.1), 0.1, 4) for k in order}
        f = family(pt, order)
        d = {k: f["per_config"][k]["D"] for k in order}
        r = {k: f["per_config"][k]["rejected"] for k in order}
        c1 = any(r[k] and d[k] < 0 for k in order)
        low = all(v > 0 for v in d.values())
        c2 = (not c1) and low and all(r[k] and d[k] > 0 for k in order)
        c3 = (not c1) and low and not c2
        c4 = not (c1 or c2 or c3)
        exclusive &= sum((c1, c2, c3, c4)) == 1 and f["branch"] == BRANCHES[[c1, c2, c3, c4].index(True)]
    check("branches exhaustive and mutually exclusive (300 random families)", exclusive)

    # the in-sample Monte Carlo path runs and agrees in sign with the exact path
    draws = np.random.default_rng(MC_SEED).integers(0, 4, size=(MC_N, 4))
    f = family({k: up for k in order}, order, exact=False, draws=draws)
    check("Monte Carlo path: all-positive rejected toward the centre", f["branch"] == BRANCHES[1])

    # failure: a configuration with two seeds cannot be discharged
    rec = {"M": 16, "N": 8, "seeds": {"0": {}, "1": {}}}
    try:
        seed_mean(rec, "held_out", "l1", "368")
        check("missing seed raises CannotDischarge", False)
    except CannotDischarge:
        check("missing seed raises CannotDischarge", True)
    rec = {"M": 16, "N": 8, "seeds": {s: {"held_out": {"368": {"l1": [0.1, np.nan, 0.1, 0.1]}}}
                                      for s in ("0", "1", "2")}}
    try:
        seed_mean(rec, "held_out", "l1", "368")
        check("non-finite value raises CannotDischarge", False)
    except CannotDischarge:
        check("non-finite value raises CannotDischarge", True)
    # end to end: a synthetic evaluator file through main_verdict, in a scratch directory
    import tempfile
    real = P5.R.RESULTS
    grid = [[32, 32], [16, 8], [32, 16], [8, 8], [32, 2], [32, 1], [2, 8], [1, 8]]
    keys = [f"M{m}_N{n}" for m, n in grid]
    ho_ep, in_ep = [1, 1, 8, 8], [0, 0, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 9, 9]

    def synth(shift):
        """3 seeds; held-out and in-sample per-trajectory values = base + shift."""
        g = np.random.default_rng(7)
        seeds = {}
        for s in ("0", "1", "2"):
            seeds[s] = {"wall_clock_s": 1.0, "n_train_windows": 1}
            for a, n in (("held_out", 4), ("in_sample", 16)):
                seeds[s][a] = {h: {mt: (0.5 + shift + 0.001 * g.standard_normal(n)).tolist()
                                   for mt in ("l1", "nrmse")}
                               for h in ("1", "8", "32", "100", "128", "368")}
        return {"seeds": seeds}
    ev = {"horizons": [1, 8, 32, 100, 128, 368],
          "arenas": {"held_out": {"n_independent": 4, "starts": [999, 1399, 7999, 8399],
                                  "episode_of_window": ho_ep},
                     "in_sample": {"n_independent": 16, "episode_of_window": in_ep}},
          "floor": {a: {h: {"l1": [1.0] * n} for h in ("100", "368")}
                    for a, n in (("held_out", 4), ("in_sample", 16))},
          "configs": {CENTRE: {"M": 32, "N": 8, **synth(0.0)}}}
    for i, (k, (m, n)) in enumerate(zip(keys, grid)):
        ev["configs"][k] = {"M": m, "N": n, **synth(0.2 if i else -0.2)}   # (32,32) better
    p5 = {"traj_start_row": [999, 1399, 7999, 8399],
          "estimates": {k: {"binding_mde_pct_of_centre": 1.0}
                        for k in ("l1_h368", "l1_h100", "nrmse_h368", "nrmse_h100")}}
    with tempfile.TemporaryDirectory() as td:
        for name, obj in (("mn_sweep_eval.json", ev), ("p5_sweep_power.json", p5),
                          ("mn_sweep_timing.json", {"queued_configs": grid})):
            json.dump(obj, open(os.path.join(td, name), "w"))
        P5.R.RESULTS = td
        try:
            main_verdict()
            v = json.load(open(os.path.join(td, "mn_sweep_verdict.json")))
            check("end to end: a better (32, 32) returns NOT OPTIMAL, naming it",
                  v["verdict"] == BRANCHES[0] and
                  v["governing"]["conditions"]["configs_excluding_zero_in_their_favour"] == ["M32_N32"])
            check("end to end: per-episode signs cover all ten episodes",
                  all(x["n_episodes"] == 10 for x in v["per_episode_sign"].values()))
            json.dump({"queued_configs": [grid[1], grid[0]] + grid[2:]},
                      open(os.path.join(td, "mn_sweep_timing.json"), "w"))
            try:
                main_verdict()
                check("end to end: a queue order other than M-74's grid stops the verdict", False)
            except CannotDischarge:
                check("end to end: a queue order other than M-74's grid stops the verdict", True)
            json.dump({"queued_configs": grid[:6], "dropped_configs": grid[6:],
                       "drop_recorded_in": None},
                      open(os.path.join(td, "mn_sweep_timing.json"), "w"))
            try:
                main_verdict()
                check("end to end: an unrecorded drop stops the verdict", False)
            except CannotDischarge:
                check("end to end: an unrecorded drop stops the verdict", True)
            json.dump({"queued_configs": grid}, open(os.path.join(td, "mn_sweep_timing.json"), "w"))
            del ev["configs"]["M16_N8"]["seeds"]["2"]
            json.dump(ev, open(os.path.join(td, "mn_sweep_eval.json"), "w"))
            try:
                main_verdict()
                check("end to end: a missing seed stops the verdict", False)
            except CannotDischarge:
                check("end to end: a missing seed stops the verdict", True)
        finally:
            P5.R.RESULTS = real
    print(f"  self-test: {'PASS' if not fails else 'FAIL'} ({len(fails)} failed)")
    return not fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", help="run the self-test only")
    args = ap.parse_args()
    print("=" * 90)
    print("M-74 VERDICT SCRIPT")
    print("=" * 90)
    ok = self_test()
    if not ok:
        sys.exit(1)
    if args.self_test:
        return
    try:
        main_verdict()
    except CannotDischarge as e:
        print(f"  M-74 CANNOT BE DISCHARGED AS WRITTEN: {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()
