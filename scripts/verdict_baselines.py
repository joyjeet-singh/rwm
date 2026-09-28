"""
Rules M-75 and M-76 -- the verdicts on the architecture claim, computed exactly as the rules
state them. Committed and pushed before any baseline run starts (PLAN S2b step 6).

THE RULES (FINDINGS_LEDGER.md, ### M-75 and ### M-76), one family each:
  M-75  baselines teacher-forced (regime tf), Table S7 sizes -- the claim as made;
  M-76  baselines autoregressive (regime ar), Table S7 sizes -- architecture at a fixed regime.
  statistic  D_b = mean over the 4 held-out trajectories of
                   [3-seed mean err_b(traj) - 3-seed mean err_RWM(traj)],
             relative-L1 at h = 368; RWM is Arm A (32, 8) at 2,500 iterations, seeds 0-2.
  test       exactly M-74's: the exact 256-resample cluster bootstrap and two-sided p
             (scripts/p5_sweep_power.py), Holm step-down at alpha = 0.05 over the three
             baselines of the rule (scripts/verdict_mn_sweep.holm), exact ties broken by the
             priority order MLP, RSSM, transformer.
  per baseline  RWM BETTER (rejected, D_b > 0) / BASELINE BETTER (rejected, D_b < 0) /
                CANNOT BE SETTLED (anything else).
  overall    first match: 1 any BASELINE BETTER; 2 all three RWM BETTER; 3 at least one RWM
             BETTER and the rest CANNOT BE SETTLED; 4 none resolves. Named, for M-75:
             DOES NOT REPRODUCE / REPRODUCES / PARTIAL / CANNOT BE SETTLED; for M-76:
             A BASELINE AHEAD / RWM AHEAD OF ALL THREE / PARTIAL / CANNOT BE SETTLED.
  failure    a governing baseline missing, short of three seeds, or with a non-finite value:
             the rule cannot be discharged as written -- no verdict.

Reported alongside, never governing: every horizon and nRMSE under the same test; the four
per-trajectory differences; the in-sample arena (Monte Carlo, 20,000 resamples, seed 0);
the per-episode sign over all ten episodes; the hold-last floor; wall_clock_s and parameter
counts; and the parameter-matched variants, if they were run, under the same test.

  python scripts/verdict_baselines.py --self-test
  python scripts/verdict_baselines.py              # self-test, then both verdicts (S8)

Reads results/baselines_eval.json, results/baselines_timing.json and
results/p6_baseline_power.json. Writes results/baselines_verdict.json.
"""
import argparse
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402

import p5_sweep_power as P5  # noqa: E402
import verdict_mn_sweep as VMN  # noqa: E402

ALPHA = VMN.ALPHA
ORDER = ("mlp", "rssm", "transformer")
RULES = {
    "M-75": {"regime": "tf", "names": ("DOES NOT REPRODUCE", "REPRODUCES", "PARTIAL",
                                        "CANNOT BE SETTLED")},
    "M-76": {"regime": "ar", "names": ("A BASELINE AHEAD", "RWM AHEAD OF ALL THREE", "PARTIAL",
                                        "CANNOT BE SETTLED")},
}
MC_N, MC_SEED = 20000, 0
CannotDischarge = VMN.CannotDischarge


def per_baseline(d, rejected):
    if rejected and d > 0:
        return "RWM BETTER"
    if rejected and d < 0:
        return "BASELINE BETTER"
    return "CANNOT BE SETTLED"


def overall(results, names):
    vals = list(results.values())
    if "BASELINE BETTER" in vals:
        return names[0]
    if all(v == "RWM BETTER" for v in vals):
        return names[1]
    if "RWM BETTER" in vals:
        return names[2]
    return names[3]


def family(per_traj, order, names, exact=True, draws=None):
    """per_traj: {arch: (n_traj,) differences baseline - RWM}. The whole governed test."""
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
    h = VMN.holm(p, list(order))
    res = {k: per_baseline(diffs[k], h[k]["rejected"]) for k in per_traj}
    return {"verdict": overall(res, names), "m": len(per_traj),
            "per_baseline": {k: {"result": res[k], "D": diffs[k],
                                 "per_traj": [float(x) for x in per_traj[k]], "p": p[k],
                                 "ci95": ci[k], "rank": h[k]["rank"], "level": h[k]["level"],
                                 "rejected": h[k]["rejected"]}
                             for k in order if k in per_traj}}


def seed_mean(rec, arena, metric, h):
    seeds = rec["seeds"]
    if sorted(seeds) != ["0", "1", "2"]:
        raise CannotDischarge(f"{rec.get('arch')}: seeds {sorted(seeds)}, not 0, 1, 2")
    a = np.array([seeds[s][arena][h][metric] for s in ("0", "1", "2")], dtype=float)
    if not np.all(np.isfinite(a)):
        raise CannotDischarge(f"{rec.get('arch')}: non-finite {metric} at h={h}")
    return a.mean(0)


def differences(ev, keys, arena, metric, h):
    r = seed_mean(ev["configs"]["rwm"], arena, metric, h)
    return {arch: seed_mean(ev["configs"][k], arena, metric, h) - r for arch, k in keys.items()}


def one_rule(ev, rid, spec="s7"):
    rule = RULES[rid]
    keys = {a: f"{a}_{rule['regime']}_{spec}" for a in ORDER}
    missing = [k for k in keys.values() if k not in ev["configs"]]
    if missing:
        if spec == "s7":
            raise CannotDischarge(f"{rid}: governing baselines not scored: {missing}")
        return None
    gov = family(differences(ev, keys, "held_out", "l1", "368"), ORDER, rule["names"])
    alongside = {f"{mt}_h{h}": family(differences(ev, keys, "held_out", mt, str(h)), ORDER,
                                      rule["names"])
                 for mt in ("l1", "nrmse") for h in ev["horizons"]}
    ins = ev["arenas"]["in_sample"]
    draws = np.random.default_rng(MC_SEED).integers(0, ins["n_independent"],
                                                    size=(MC_N, ins["n_independent"]))
    in_sample = {f"{mt}_h{h}": family(differences(ev, keys, "in_sample", mt, str(h)), ORDER,
                                      rule["names"], exact=False, draws=draws)
                 for mt in ("l1", "nrmse") for h in ev["horizons"]}
    eps = {}
    for a in ("held_out", "in_sample"):
        d = differences(ev, keys, a, "l1", "368")
        for arch in ORDER:
            for w, e in enumerate(ev["arenas"][a]["episode_of_window"]):
                eps.setdefault(arch, {}).setdefault(e, []).append(float(d[arch][w]))
    signs = {arch: {"positive": int(sum(bool(np.mean(v) > 0) for v in eps[arch].values())),
                    "negative": int(sum(bool(np.mean(v) < 0) for v in eps[arch].values())),
                    "n_episodes": len(eps[arch]),
                    "per_episode": {str(e): float(np.mean(v)) for e, v in sorted(eps[arch].items())}}
             for arch in ORDER}
    return {"rule": rid, "regime": rule["regime"], "spec": spec, "verdict": gov["verdict"],
            "governing": gov, "alongside": alongside, "in_sample": in_sample,
            "per_episode_sign": signs,
            "runs": {k: {s: {x: v.get(x) for x in ("wall_clock_s", "n_params")}
                         for s, v in ev["configs"][k]["seeds"].items()} for k in keys.values()}}


def main_verdict():
    res = P5.R.RESULTS
    ev = json.load(open(os.path.join(res, "baselines_eval.json")))
    timing = json.load(open(os.path.join(res, "baselines_timing.json")))
    p6 = json.load(open(os.path.join(res, "p6_baseline_power.json")))
    queued = {tuple(q) for q in timing["queued"]}
    gov = {(a, RULES[r]["regime"], "s7") for r in RULES for a in ORDER}
    if not gov <= queued:
        raise CannotDischarge(f"governing baselines never queued: {sorted(gov - queued)}")
    ho = ev["arenas"]["held_out"]
    if ho["n_independent"] != 4 or ho["starts"] != p6["traj_start_row"]:
        raise CannotDischarge(f"held-out arena is not the rules': {ho['starts']}")
    if ev["arenas"]["in_sample"]["n_independent"] != 16:
        raise CannotDischarge("in-sample arena is not n_independent = 16")
    out = {"rules": {}, "matched_variants": {}, "alpha": ALPHA, "priority_order": list(ORDER),
           "hold_last_floor_l1": {a: {h: float(np.mean(ev["floor"][a][h]["l1"]))
                                      for h in ("100", "368")} for a in ("held_out", "in_sample")},
           "mde_pct_of_rwm_holm_step_1": {r: {k: p6["rules"][r]["estimates"][k]
                                               ["binding_mde_pct_of_centre"]
                                               for k in ("l1_h368", "l1_h100")} for r in RULES},
           "inputs": ["results/baselines_eval.json", "results/baselines_timing.json",
                      "results/p6_baseline_power.json"]}
    for rid in RULES:
        out["rules"][rid] = one_rule(ev, rid, "s7")
        mv = one_rule(ev, rid, "matched")
        if mv is not None:
            out["matched_variants"][rid] = mv
    json.dump(out, open(os.path.join(res, "baselines_verdict.json"), "w"), indent=2)
    for rid, r in out["rules"].items():
        print(f"  {rid} returns: {r['verdict']}")
        for arch, v in r["governing"]["per_baseline"].items():
            print(f"    {arch:<12} D {v['D']:+.4f}  p {v['p']:.5f}  Holm rank {v['rank']} "
                  f"level {v['level']:.5f}  {v['result']}")
    print(f"  wrote {os.path.relpath(os.path.join(res, 'baselines_verdict.json'), P5.R.REPO_ROOT)}")


def self_test():
    fails = []

    def check(name, cond):
        print(f"    {'ok  ' if cond else 'FAIL'} {name}")
        if not cond:
            fails.append(name)

    up = np.array([0.3, 0.2, 0.25, 0.1])
    mixed = np.array([0.6, 0.5, -0.1, -0.1])
    three = np.array([0.5, 0.5, 0.5, -0.01])
    for rid, rule in RULES.items():
        n = rule["names"]
        f = family({a: up for a in ORDER}, ORDER, n)
        check(f"{rid}: all three worse on every trajectory -> {n[1]}", f["verdict"] == n[1])
        f = family({"mlp": up, "rssm": -up, "transformer": up}, ORDER, n)
        check(f"{rid}: one baseline better on every trajectory -> {n[0]}", f["verdict"] == n[0])
        f = family({"mlp": up, "rssm": mixed, "transformer": up}, ORDER, n)
        check(f"{rid}: one unresolved, two RWM BETTER -> {n[2]}", f["verdict"] == n[2])
        f = family({a: mixed for a in ORDER}, ORDER, n)
        check(f"{rid}: none resolves -> {n[3]}", f["verdict"] == n[3])
        f = family({"mlp": -mixed, "rssm": mixed, "transformer": mixed}, ORDER, n)
        check(f"{rid}: a lower but unresolved baseline is CANNOT BE SETTLED, not better",
              f["per_baseline"]["mlp"]["result"] == "CANNOT BE SETTLED" and f["verdict"] == n[3])
    f = family({a: three for a in ORDER}, ORDER, RULES["M-75"]["names"])
    check("m = 3: a 3-of-4 pattern (p = 2/256) is rejected at Holm step 1",
          all(v["rejected"] for v in f["per_baseline"].values()))
    f = family({a: up for a in ORDER}, ORDER, RULES["M-75"]["names"])
    check("tied p-values ranked MLP, RSSM, transformer",
          [f["per_baseline"][a]["rank"] for a in ORDER] == [1, 2, 3])
    rng = np.random.default_rng(3)
    good = True
    for _ in range(300):
        f = family({a: rng.normal(rng.normal(0, 0.1), 0.1, 4) for a in ORDER}, ORDER,
                   RULES["M-76"]["names"])
        r = [v["result"] for v in f["per_baseline"].values()]
        c = ["BASELINE BETTER" in r, all(x == "RWM BETTER" for x in r),
             ("RWM BETTER" in r) and "BASELINE BETTER" not in r and not all(x == "RWM BETTER" for x in r),
             all(x == "CANNOT BE SETTLED" for x in r)]
        good &= sum(c) == 1 and f["verdict"] == RULES["M-76"]["names"][c.index(True)]
    check("overall branches exhaustive and mutually exclusive (300 random families)", good)

    # end to end on a synthetic evaluator file
    def synth(shift):
        g = np.random.default_rng(11)
        seeds = {}
        for s in ("0", "1", "2"):
            seeds[s] = {"wall_clock_s": 1.0, "n_params": 1}
            for a, n in (("held_out", 4), ("in_sample", 16)):
                seeds[s][a] = {h: {mt: (0.5 + shift + 0.001 * g.standard_normal(n)).tolist()
                                   for mt in ("l1", "nrmse")}
                               for h in ("1", "8", "32", "100", "128", "368")}
        return {"seeds": seeds}
    starts = [999, 1399, 7999, 8399]
    ev = {"horizons": [1, 8, 32, 100, 128, 368],
          "arenas": {"held_out": {"n_independent": 4, "starts": starts,
                                  "episode_of_window": [1, 1, 8, 8]},
                     "in_sample": {"n_independent": 16,
                                   "episode_of_window": [0, 0, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 9, 9]}},
          "floor": {a: {h: {"l1": [1.0] * n} for h in ("100", "368")}
                    for a, n in (("held_out", 4), ("in_sample", 16))},
          "configs": {"rwm": {"arch": "rwm", **synth(0.0)}}}
    for a in ORDER:
        ev["configs"][f"{a}_tf_s7"] = {"arch": a, **synth(0.3)}
        ev["configs"][f"{a}_ar_s7"] = {"arch": a, **synth(0.3 if a != "rssm" else -0.3)}
    timing = {"queued": [[a, g, "s7"] for a in ORDER for g in ("tf", "ar")]}
    p6 = {"traj_start_row": starts,
          "rules": {r: {"estimates": {k: {"binding_mde_pct_of_centre": 1.0}
                                      for k in ("l1_h368", "l1_h100")}} for r in RULES}}
    real = P5.R.RESULTS
    with tempfile.TemporaryDirectory() as td:
        for name, obj in (("baselines_eval.json", ev), ("baselines_timing.json", timing),
                          ("p6_baseline_power.json", p6)):
            json.dump(obj, open(os.path.join(td, name), "w"))
        P5.R.RESULTS = td
        try:
            main_verdict()
            v = json.load(open(os.path.join(td, "baselines_verdict.json")))
            check("end to end: M-75 REPRODUCES when every tf baseline is worse",
                  v["rules"]["M-75"]["verdict"] == "REPRODUCES")
            check("end to end: M-76 A BASELINE AHEAD when the ar RSSM is better",
                  v["rules"]["M-76"]["verdict"] == "A BASELINE AHEAD" and
                  v["rules"]["M-76"]["governing"]["per_baseline"]["rssm"]["result"] == "BASELINE BETTER")
            check("end to end: per-episode signs cover all ten episodes",
                  all(x["n_episodes"] == 10 for x in v["rules"]["M-75"]["per_episode_sign"].values()))
            check("end to end: no matched variants reported when none were run",
                  v["matched_variants"] == {})
            json.dump({"queued": timing["queued"][:5]}, open(os.path.join(td, "baselines_timing.json"), "w"))
            try:
                main_verdict()
                check("end to end: a governing baseline never queued stops the verdict", False)
            except CannotDischarge:
                check("end to end: a governing baseline never queued stops the verdict", True)
            json.dump(timing, open(os.path.join(td, "baselines_timing.json"), "w"))
            del ev["configs"]["rssm_tf_s7"]["seeds"]["1"]
            json.dump(ev, open(os.path.join(td, "baselines_eval.json"), "w"))
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
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    print("=" * 90)
    print("M-75 / M-76 VERDICT SCRIPT")
    print("=" * 90)
    if not self_test():
        sys.exit(1)
    if args.self_test:
        return
    try:
        main_verdict()
    except CannotDischarge as e:
        print(f"  CANNOT BE DISCHARGED AS WRITTEN: {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()
