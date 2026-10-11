"""
Rule X8 (ledger M-90; PRE-REGISTERED, exploratory, inference only) -- would any verdict change under the released
evaluation's action timing? Round 4, PLAN Annex 2 X8 (objection O6).

It never re-opens M-23 or M-74-M-76, and nothing it returns changes their verdicts: it says what each would have
returned had our models been scored with the released evaluation's pairing.

THE PAIRING. Offset 1 (causal) pairs the prediction of state i with action i; every rule here was scored that way.
Offset 0 is the released evaluation's: state i with action i - 1. Each rule's own evaluator scores through
scripts/mn_sweep_eval.score(..., action_offset), whose offset 0 moves every action one row later, the window's first
row repeated, and rolls out at the causal pairing (mn_sweep_eval._pairing), so one definition reaches RWM and every
baseline. For RWM this equals its native action_offset=0 (assertion (d)), and RWM never reads the repeated row; the
RSSM reads it at its first filtering step only.

RE-SCORED AT OFFSET 0, each with its rule's own evaluator and statistic, all imported:
  M-74's sweep: the centre and 8 configurations x seeds 0-2 at 2,500 iterations; the evaluator is mn_sweep_eval's
    arena and score; the verdict and alongside branches are verdict_mn_sweep's differences and family.
  M-75 and M-76's baselines: 6 families x seeds 0-2 at 2,500, and RWM; the evaluator is baselines_eval.evaluate; the
    verdicts are verdict_baselines.one_rule.
  The A/B comparison: Arm A and Arm B, seeds 0-2. Its reading is M-23's three conditions, applied with three seeds:
    (1) Arm A leads (gap = seed-mean B - seed-mean A > 0, mean over the held-out trajectories) at 2,500 and at 10,000;
    (2) the 95% interval of the 10,000-iteration gap has its lower bound above zero; (3) the per-episode gap at 10,000
    is positive in all ten episodes. Relative-L1 at h = 368. The interval and the per-episode sign are the by-horizon
    table's (a1_ab_by_horizon: review_bootstrap_unit.boot_cluster at 20,000 draws, seed 0, and its per-episode means).
    The label follows task5_analyse.py's code, which discharged M-23: REPRODUCES AT LONG HORIZON if all three hold,
    FAILS TO REPRODUCE if (1) fails, CANNOT BE SETTLED otherwise. (M-23's text says it fails only if Arm A does not
    lead at 10,000; the two differ only if Arm A trails at 2,500 and leads at 10,000.)

READING, per rule (M-74, M-75, M-76, and the A/B comparison): SAME VERDICT, or VERDICT WOULD CHANGE TO <label>.
For M-74, M-75 and M-76 the comparison is with the committed verdict (results/mn_sweep_verdict.json,
results/baselines_verdict.json). For the A/B comparison it is with the same three-seed computation at offset 1, since
M-23 itself was discharged on seed 1.
ALONGSIDE, for each rule: every reading in its alongside set that changes between offset 1 and offset 0 --
  M-74: each held-out branch at every horizon and metric, the in-sample branches at h = 100 and 368, and each
    configuration's per-episode sign over all ten episodes (positive and negative counts; verdict_mn_sweep computes
    it inside its main(), so those lines are copied, and assertion (a) checks them against the committed counts);
  M-75, M-76: the same for their alongside and in-sample families, and each baseline's per-episode sign
    (verdict_baselines.one_rule's per_episode_sign);
  A/B: M-23 as discharged (seed 1, its own bootstrap: 10,000 resamples, seed 0, ≡ boot_cluster on one seed); M-23's
    alongside set with three seeds -- its three conditions at h = 8 (held-out), on nRMSE (h = 368, held-out) and in
    the in-sample arena (h = 368); its h = 168 on 200-step trajectories is not computed, since no evaluator for
    200-step windows takes an offset; task5_analyse's three gap statuses (h = 8 held-out, h = 368 and h = 8
    in-sample, at 10,000); and the by-horizon table at 10,000: each horizon's interval excluding zero, each
    horizon's per-episode sign count, and the trend's reading (a1_ab_by_horizon.trend_reading).
COPIED, not imported, and asserted: task5_analyse's M-23 label and gap-status logic (task5_analyse runs on import),
a1_ab_by_horizon's per-episode gap and by-horizon fields (inside its main()), verdict_mn_sweep's per-episode sign, and
task5's bootstrap in assertion (c). The three-seed condition (1) uses the point gap, as the by-horizon table reports it;
M-23 as discharged uses task5's bootstrap mean. Each rule's own interval is kept, so the A/B intervals at n = 4 are
Monte Carlo (20,000 draws; 10,000 for seed 1), not Annex 2's exact enumeration.

ASSERTIONS, before any reading (a failure stops the run; nothing is read):
  (a) offset 1 through this script reproduces, to 1e-6, every per-trajectory value of results/mn_sweep_eval.json and
      results/baselines_eval.json, and the committed verdicts and alongside branches exactly;
  (b) offset 1 reproduces results/a1_ab_by_horizon.json (per-trajectory means, gaps, intervals, sign tests, trend
      reading), results/task5_analysis.json's seed-1 M-23 gaps, intervals, per-episode gaps and verdict, Arm A's
      2,500- and 10,000-iteration values in results/mn_compute_matched.json, and Arm B's 2,500-iteration values in
      results/x3_armB_2500_reference.json, to 1e-6 relative to max(1, |value|) (errors reach 7, where float32 rounding
      alone is about 1e-6);
  (c) review_bootstrap_unit.boot_cluster on one seed reproduces task5_analyse's M-23 bootstrap (the same draws);
  (d) offset 0 is the released pairing: for Arm A at 10,000 on the held-out pair, mn_sweep_eval.score at offset 0
      equals the model's native action_offset=0 rollout (to 1e-12), and the ratio of the two offsets' errors reproduces
      results/alignment_by_horizon.json's per-seed stale-pairing change (as 1 + pct/100), to 1e-6. Before the reading,
      the native equality is also checked for every sweep configuration with M < 32, seeds 0-2, held-out arena.
  Per-episode values are rolled out one episode per batch, as a1 and task5_analyse roll them: at h = 368 the batch
  changes the float rounding, which a diverging forecast amplifies (about 1e-2 between per-arena and per-episode
  batches).
A non-finite score, or any internal check failing, stops the run with a .blocked record and no reading.

CAVEAT, in every sentence that reports it: our models under the released pairing; it says nothing direct about the
original papers' printed numbers.

  python scripts/x8_released_pairing.py --self-test     # synthetic values only
  python scripts/x8_released_pairing.py --assert-only   # assertions (a)-(d) on cases committed artifacts hold
  python scripts/x8_released_pairing.py                 # self-test, assertions, then the rule (refuses unless
                                                        # ledger M-90 records this file's SHA-256)
Writes results/x8_released_pairing.json, and the offset-0 scores: results/x8_sweep_eval_offset0.json and
results/x8_baselines_eval_offset0.json.
"""
import argparse
import copy
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import torch  # noqa: E402

import a1_ab_by_horizon as A1  # noqa: E402
import baselines_eval as BE  # noqa: E402
import mn_sweep_eval as MN  # noqa: E402
import review_bootstrap_unit as RB  # noqa: E402
import rollout_eval as E  # noqa: E402
import rwm_data as R  # noqa: E402
import rwm_metrics as MET  # noqa: E402
import rwm_model as M  # noqa: E402
import verdict_baselines as VB  # noqa: E402
import verdict_mn_sweep as VMN  # noqa: E402

RULE_ID = "M-90"
SEEDS = (0, 1, 2)
HS = tuple(MN.HORIZONS)
ITERS = 2500
M23_LABELS = ("REPRODUCES AT LONG HORIZON", "FAILS TO REPRODUCE", "CANNOT BE SETTLED")
M23_NBOOT, M23_SEED = 10000, 0                    # task5_analyse.boot's defaults
TOL, TOL_NATIVE = 1e-6, 1e-12
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
OUT = os.path.join(R.RESULTS, "x8_released_pairing.json")
SWEEP_OUT = os.path.join(R.RESULTS, "x8_sweep_eval_offset0.json")
BASE_OUT = os.path.join(R.RESULTS, "x8_baselines_eval_offset0.json")
STRAT = os.path.join(R.RESULTS, "step0_strat.json")
MODULES = ("scripts/x8_released_pairing.py", "scripts/mn_sweep_eval.py", "scripts/baselines_eval.py",
           "scripts/verdict_mn_sweep.py", "scripts/verdict_baselines.py", "scripts/a1_ab_by_horizon.py",
           "scripts/review_bootstrap_unit.py", "scripts/p5_sweep_power.py", "src/rwm_model.py", "src/rollout_eval.py",
           "src/rwm_data.py", "src/rwm_metrics.py", "src/baselines/__init__.py",
           "src/baselines/common.py", "src/baselines/rssm.py", "src/baselines/mlp.py", "src/baselines/transformer.py")


class NonFinite(Exception):
    pass


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def blocked(reason, **detail):
    json.dump({"BLOCKED": reason, **detail}, open(OUT + ".blocked", "w"), indent=1, default=str)
    raise SystemExit(f"BLOCKED: {reason} (results/x8_released_pairing.json.blocked); no reading written")


def J(name):
    return json.load(open(os.path.join(R.RESULTS, name)))


def reading_of(committed, now):
    return "SAME VERDICT" if now == committed else f"VERDICT WOULD CHANGE TO {now}"


def changes(a, b):
    """The keys whose value differs between two {key: label} maps, as {key: [a, b]}."""
    return {k: [a[k], b[k]] for k in a if a[k] != b[k]}


def finite_tree(x):
    if isinstance(x, dict):
        return all(finite_tree(v) for v in x.values())
    if isinstance(x, (list, tuple)):
        return all(finite_tree(v) for v in x)
    if isinstance(x, float):
        return bool(np.isfinite(x))
    return True


class Ctx:
    def __init__(self):
        paths = R.repo_paths()
        self.cfg = R.load_reference_config(paths["lite"])
        self.data, self.ep = R.load_data(paths["csv"], verbose=False)
        self.split = E.make_split(seed=0, strat_path=STRAT, verbose=False)
        self.scale = MET.training_scale(self.data, self.ep, self.split["train_episodes"], self.cfg["state_data_mean"],
                                        self.cfg["state_data_std"])
        self.arenas = {"held_out": MN.arena(self.ep, self.split["holdout_episodes"], 32),
                       "in_sample": MN.arena(self.ep, self.split["train_episodes"], 32)}
        assert self.arenas["held_out"]["starts"] == MN.HELD_OUT_STARTS and self.arenas["in_sample"]["n_independent"] == 16

    def rwm(self, w, m=32, n=8):
        c = dict(self.cfg)
        c["history_horizon"], c["forecast_horizon"] = m, n
        model = M.build_from_config(c, ensemble_size=1)
        model.load_state_dict(torch.load(w, map_location="cpu")["model_state_dict"], strict=True)
        model.eval()
        return model

    def score(self, model, m, offset):
        return {a: MN.score(model, self.data, self.cfg, self.scale, v["starts"], m, 32, offset)
                for a, v in self.arenas.items()}


# ------------------------------------------------------------------ M-74, the sweep
def sweep_order():
    t = J("mn_sweep_timing.json")
    return [tuple(c) for c in t["queued_configs"]]


def sweep_eval(ctx, offset):
    configs = [MN.CENTRE] + sweep_order()
    out = {"arenas": ctx.arenas, "horizons": list(HS), "action_offset": offset, "configs": {}}
    for m, n in configs:
        rec = {"M": m, "N": n, "seeds": {}}
        for s in SEEDS:
            rec["seeds"][str(s)] = ctx.score(ctx.rwm(MN.weights_path(m, n, s), m, n), m, offset)
        out["configs"][f"M{m}_N{n}"] = rec
    return out


def sweep_verdict(ev):
    order = [f"M{m}_N{n}" for m, n in sweep_order()]
    gov = VMN.family(VMN.differences(ev, order, "held_out", VMN.GOV_METRIC, VMN.GOV_H), order)
    al = {f"{mt}_h{h}": VMN.family(VMN.differences(ev, order, "held_out", mt, str(h)), order)["branch"]
          for mt in ("l1", "nrmse") for h in ev["horizons"]}
    draws = np.random.default_rng(VMN.MC_SEED).integers(0, 16, size=(VMN.MC_N, 16))
    ins = {f"{mt}_h{h}": VMN.family(VMN.differences(ev, order, "in_sample", mt, str(h)), order, exact=False,
                                    draws=draws)["branch"] for mt in ("l1", "nrmse") for h in ("100", "368")}
    # The per-episode sign over all ten episodes, M-74's alongside: verdict_mn_sweep.main_verdict computes it inline
    # (not importable), so these lines are copied from it; assertion (a) checks them against the committed counts.
    eps = {}
    for a in ("held_out", "in_sample"):
        d = VMN.differences(ev, order, a, VMN.GOV_METRIC, VMN.GOV_H)
        for k in order:
            for w, e in enumerate(ev["arenas"][a]["episode_of_window"]):
                eps.setdefault(k, {}).setdefault(e, []).append(float(d[k][w]))
    sign = {k: [int(sum(bool(np.mean(v) > 0) for v in eps[k].values())), int(sum(bool(np.mean(v) < 0) for v in eps[k].values()))]
            for k in order}
    return {"verdict": gov["branch"], "alongside": al, "in_sample": ins, "per_episode_sign": sign}


def committed_sweep():
    v = J("mn_sweep_verdict.json")
    return {"verdict": v["verdict"], "alongside": {k: x["branch"] for k, x in v["alongside"].items()},
            "in_sample": {k: x["branch"] for k, x in v["in_sample"].items()},
            "per_episode_sign": {k: [x["positive"], x["negative"]] for k, x in v["per_episode_sign"].items()}}


# ------------------------------------------------------------------ M-75, M-76, the baselines
def baselines_queued():
    q = [tuple(x) for x in J("baselines_timing.json")["queued"]]
    assert all(s == "s7" for _, _, s in q) and len(q) == 6, q
    return q


def baselines_verdicts(ev):
    out = {}
    for rid in VB.RULES:
        r = VB.one_rule(ev, rid, "s7")
        out[rid] = {"verdict": r["verdict"], "alongside": {k: x["verdict"] for k, x in r["alongside"].items()},
                    "in_sample": {k: x["verdict"] for k, x in r["in_sample"].items()},
                    "per_episode_sign": {k: [x["positive"], x["negative"]] for k, x in r["per_episode_sign"].items()}}
    return out


def committed_baselines():
    v = J("baselines_verdict.json")["rules"]
    return {rid: {"verdict": r["verdict"], "alongside": {k: x["verdict"] for k, x in r["alongside"].items()},
                  "in_sample": {k: x["verdict"] for k, x in r["in_sample"].items()},
                  "per_episode_sign": {k: [x["positive"], x["negative"]] for k, x in r["per_episode_sign"].items()}}
            for rid, r in v.items()}


# ------------------------------------------------------------------ the A/B comparison
AB_W = {10000: "runs/arm{a}_seed{s}_10k/weights_10000.pt", 2500: "runs/arm{a}_seed{s}/weights_2500.pt"}


def ab_scores(ctx, offset, seeds=SEEDS, iters=(2500, 10000)):
    """Each model on both arenas, batched per arena as a1 and task5_analyse batch them, and, at 10,000 iterations, on each
    episode's own trajectories batched per episode, as their per-episode sign tests are. The batch matters at h = 368:
    float rounding differs with the batch and a diverging forecast amplifies it (about 1e-2 between the two batchings)."""
    out = {}
    for a in "AB":
        for s in seeds:
            for it in iters:
                model = ctx.rwm(AB_W[it].format(a=a, s=s))
                out[(a, s, it)] = ctx.score(model, 32, offset)
                if it == 10000:
                    out[(a, s, it)]["episodes"] = {
                        str(e): MN.score(model, ctx.data, ctx.cfg, ctx.scale, MET.non_overlapping_starts(ctx.ep, [e], 400),
                                         32, 32, offset) for e in range(R.N_EPISODES)}
    return out


def arr(sc, arm, it, arena, h, seeds=SEEDS, metric="l1"):
    return np.array([sc[(arm, s, it)][arena][str(h)][metric] for s in seeds], dtype=np.float64)   # (n_seed, n_traj)


def gap_ci(Am, Bm, n=A1.N_BOOT, seed=A1.BOOT_SEED):
    g, lo, hi = RB.boot_cluster(Am, Bm, n=n, seed=seed)
    return float((Bm.mean(0) - Am.mean(0)).mean()), float(g), float(lo), float(hi)


def per_episode(ctx, sc, it, h, seeds=SEEDS, metric="l1"):
    """Each episode's gap at 10,000 iterations: the mean over seeds of B's mean over the episode's trajectories, minus
    the same for A, each episode rolled out as its own batch -- a1's sign test and task5_analyse's condition 3 (both
    copied: a1's is inside its main(), and task5_analyse runs on import)."""
    assert it == 10000
    ep_mean = lambda a, s, e: float(np.mean(sc[(a, s, it)]["episodes"][e][str(h)][metric]))
    return {str(e): float(np.mean([ep_mean("B", s, str(e)) for s in seeds]) - np.mean([ep_mean("A", s, str(e)) for s in seeds]))
            for e in range(R.N_EPISODES)}


def m23_label(c1, c2, c3):
    """task5_analyse.py's M-23 label, copied (it runs on import)."""
    return M23_LABELS[0] if (c1 and c2 and c3) else (M23_LABELS[1] if not c1 else M23_LABELS[2])


def m23_conditions(ctx, sc, arena, metric, h, seeds=SEEDS, n=A1.N_BOOT, seed=A1.BOOT_SEED, point=True):
    """M-23's three conditions on one arena, metric and horizon: (1) Arm A leads at 2,500 and 10,000 (the gap on this
    arena); (2) the 10,000-iteration gap's interval has its lower bound above zero; (3) the per-episode gap at 10,000 is
    positive in all ten episodes (always over all ten, per-episode batches). point=True uses the point gap for (1), as
    the by-horizon table reports it; False uses the bootstrap mean, as task5_analyse did for seed 1."""
    g = {}
    for it in (2500, 10000):
        A, B = arr(sc, "A", it, arena, h, seeds, metric), arr(sc, "B", it, arena, h, seeds, metric)
        p, bm, lo, hi = gap_ci(A, B, n=n, seed=seed)
        g[it] = {"A": float(A.mean()), "B": float(B.mean()), "gap": p if point else bm, "ci": [lo, hi]}
    pe = per_episode(ctx, sc, 10000, h, seeds, metric)
    c1, c2, c3 = g[2500]["gap"] > 0 and g[10000]["gap"] > 0, g[10000]["ci"][0] > 0, all(v > 0 for v in pe.values())
    return {"arena": arena, "metric": metric, "h": h, "c1": bool(c1), "c2": bool(c2), "c3": bool(c3),
            "label": m23_label(c1, c2, c3), "gaps": g, "per_episode_10000": pe}


def ab_reading(ctx, sc, sc1):
    """sc: three seeds at 2,500 and 10,000 for this offset; sc1: seed 1 (M-23 as discharged), the same offset."""
    held = lambda it, h: (arr(sc, "A", it, "held_out", h), arr(sc, "B", it, "held_out", h))
    three = m23_conditions(ctx, sc, "held_out", "l1", 368)
    # M-23 as discharged: seed 1, task5_analyse's bootstrap (10,000 resamples, seed 0, its bootstrap mean as the gap)
    s1 = m23_conditions(ctx, sc1, "held_out", "l1", 368, seeds=(1,), n=M23_NBOOT, seed=M23_SEED, point=False)
    seed1 = {"c1": s1["c1"], "c2": s1["c2"], "c3": s1["c3"], "label": s1["label"], "gaps": s1["gaps"],
             "per_episode": s1["per_episode_10000"]}
    # M-23's own alongside set, with three seeds: the three conditions at h = 8, on nRMSE, and in the in-sample arena
    # (h = 168 on 200-step trajectories is not computed: no evaluator for 200-step windows takes an offset)
    cond_along = {"h=8 held-out": m23_conditions(ctx, sc, "held_out", "l1", 8),
                  "nRMSE h=368 held-out": m23_conditions(ctx, sc, "held_out", "nrmse", 368),
                  "h=368 in-sample": m23_conditions(ctx, sc, "in_sample", "l1", 368)}

    def status(A, B):
        """task5_analyse's secondary status, copied."""
        p, _, lo, hi = gap_ci(A, B)
        ex = lo > 0 or hi < 0
        return {"gap": p, "ci95": [lo, hi], "status": ("A leads, CI excludes 0" if p > 0 and ex else
                                                        ("spans zero" if not ex else "B leads"))}
    sec = {"h=8 held-out": status(*held(10000, 8)),
           "h=368 in-sample": status(arr(sc, "A", 10000, "in_sample", 368), arr(sc, "B", 10000, "in_sample", 368)),
           "h=8 in-sample": status(arr(sc, "A", 10000, "in_sample", 8), arr(sc, "B", 10000, "in_sample", 8))}
    by_h, sign = {}, {}
    for h in HS:
        A, B = held(10000, h)
        p, _, lo, hi = gap_ci(A, B)
        by_h[str(h)] = {"gap": p, "gap_ci": [lo, hi], "gap_excludes_zero": bool(lo > 0 or hi < 0),
                        "ratio_B_over_A": float(B.mean() / A.mean()), "A_per_trajectory": A.mean(0).tolist(),
                        "B_per_trajectory": B.mean(0).tolist()}
        e = per_episode(ctx, sc, 10000, h)
        k = sum(1 for v in e.values() if v > 0)
        sign[str(h)] = {"n_episodes": len(e), "n_positive": k, "exact_two_sided_p": A1.sign_p(k, len(e)), "per_episode_gap": e}
    trend = A1.trend_reading(by_h, list(HS), int(ctx.cfg["forecast_horizon"]))
    return {"m23_three_seeds": three, "m23_seed1_as_discharged": seed1, "m23_conditions_alongside": cond_along,
            "secondaries_three_seeds": sec, "by_horizon": by_h, "sign_test": sign, "trend_reading": trend}


def ab_alongside_labels(r):
    lab = {"M-23 as discharged (seed 1)": r["m23_seed1_as_discharged"]["label"]}
    lab.update({f"M-23 conditions {k}": v["label"] for k, v in r["m23_conditions_alongside"].items()})
    lab.update({f"secondary {k}": v["status"] for k, v in r["secondaries_three_seeds"].items()})
    lab.update({f"by-horizon h={h} excludes zero": v["gap_excludes_zero"] for h, v in r["by_horizon"].items()})
    lab.update({f"by-horizon h={h} episodes positive": v["n_positive"] for h, v in r["sign_test"].items()})
    lab["trend reading"] = r["trend_reading"]
    return lab


# ------------------------------------------------------------------ assertions
def maxdiff_eval(ev, committed_cfg, keys):
    d, n = 0.0, 0
    for k in keys:
        for s, rec in ev["configs"][k]["seeds"].items():
            for ar in ("held_out", "in_sample"):
                for h, mv in rec[ar].items():
                    for mt, vals in mv.items():
                        for x, y in zip(vals, committed_cfg[k]["seeds"][s][ar][h][mt]):
                            d, n = max(d, abs(x - y)), n + 1
    return d, n


def assertions(ctx, td):
    out = {}
    # (a) the sweep and the baselines at offset 1
    ev1 = sweep_eval(ctx, 1)
    cm = J("mn_sweep_eval.json")
    d_s, n_s = maxdiff_eval(ev1, cm["configs"], list(ev1["configs"]))
    v1, vc = sweep_verdict(ev1), committed_sweep()
    eb1 = BE.evaluate(baselines_queued(), os.path.join(ROOT, "runs"), R.RESULTS, ITERS, os.path.join(td, "b1.json"),
                      action_offset=1)
    cb = J("baselines_eval.json")
    d_b, n_b = maxdiff_eval(eb1, cb["configs"], list(eb1["configs"]))
    bv1, bvc = baselines_verdicts(eb1), committed_baselines()
    out["a"] = {"pass": bool(d_s <= TOL and d_b <= TOL and v1["verdict"] == vc["verdict"] and v1["alongside"] == vc["alongside"]
                             and v1["in_sample"] == vc["in_sample"] and v1["per_episode_sign"] == vc["per_episode_sign"]
                             and bv1 == bvc),
                "sweep_max_abs_diff": d_s, "sweep_n_values": n_s, "baselines_max_abs_diff": d_b, "baselines_n_values": n_b,
                "sweep_verdict_offset1": v1["verdict"], "baselines_verdicts_offset1": {k: v["verdict"] for k, v in bv1.items()}}
    # (b) the A/B comparison at offset 1
    sc = ab_scores(ctx, 1)
    r = ab_reading(ctx, sc, sc)
    a1 = J("a1_ab_by_horizon.json")
    # Relative to the value's size, max(1, |committed|): these errors reach 7, where float32 rounding alone is 1e-6.
    rd = lambda u, v: abs(u - v) / max(1.0, abs(v))
    db = 0.0
    for h in HS:
        x, y = r["by_horizon"][str(h)], a1["by_horizon"][str(h)]
        db = max([db, rd(x["gap"], y["gap"]), *[rd(u, v) for u, v in zip(x["gap_ci"], y["gap_ci"])],
                  *[rd(u, v) for u, v in zip(x["A_per_trajectory"], y["A_per_trajectory"])],
                  *[rd(u, v) for u, v in zip(x["B_per_trajectory"], y["B_per_trajectory"])], rd(x["ratio_B_over_A"], y["ratio_B_over_A"])])
        s, t = r["sign_test"][str(h)], a1["sign_test"][str(h)]
        db = max([db, rd(s["exact_two_sided_p"], t["exact_two_sided_p"])]
                 + [rd(s["per_episode_gap"][e], t["per_episode_gap"][e]) for e in t["per_episode_gap"]])
        assert s["n_positive"] == t["n_positive"], f"sign test h = {h}"
    trend_ok = r["trend_reading"] == a1["trend"]["reading"]
    t5 = J("task5_analysis.json")
    s1 = r["m23_seed1_as_discharged"]
    for it in (2500, 10000):
        g = t5["gaps"][f"out-of-sample|{it}|h368"]
        db = max(db, rd(s1["gaps"][it]["A"], g["A"]), rd(s1["gaps"][it]["B"], g["B"]), rd(s1["gaps"][it]["gap"], g["gap"]),
                 *[rd(u, v) for u, v in zip(s1["gaps"][it]["ci"], g["ci"])])
    db = max([db] + [rd(s1["per_episode"][e], t5["per_episode"][e]["h368"]) for e in t5["per_episode"]])
    m23_ok = s1["label"] == t5["m23"]["verdict"] and [s1["c1"], s1["c2"], s1["c3"]] == [t5["m23"][k] for k in ("c1", "c2", "c3")]
    mc = J("mn_compute_matched.json")["part2_centre_at_more_compute"]["per_seed"]
    ref = J("x3_armB_2500_reference.json")["armB"]["per_model"]
    for s in SEEDS:
        for it in (2500, 10000):
            for ar in ("held_out", "in_sample"):
                for h in HS:
                    db = max([db] + [rd(u, v) for u, v in zip(sc[("A", s, it)][ar][str(h)]["l1"], mc[str(it)][str(s)][ar][str(h)])])
        for h in HS:
            db = max(db, rd(float(np.mean(sc[("B", s, 2500)]["held_out"][str(h)]["l1"])), ref[f"armB_teacher_forced_seed{s}"][str(h)]["l1"]))
    out["b"] = {"pass": bool(db <= TOL and trend_ok and m23_ok), "max_rel_diff": db, "trend_reading_equal": bool(trend_ok),
                "m23_seed1_reproduced": bool(m23_ok), "m23_three_seeds_offset1": r["m23_three_seeds"]["label"]}
    # (c) boot_cluster on one seed is task5_analyse's bootstrap
    A, B = arr(sc, "A", 10000, "held_out", 368, (1,)), arr(sc, "B", 10000, "held_out", 368, (1,))
    rng = np.random.default_rng(M23_SEED)
    i = rng.integers(0, A.shape[1], size=(M23_NBOOT, A.shape[1]))
    g = B[0][i].mean(1) - A[0][i].mean(1)
    t5b = (float(g.mean()), float(np.percentile(g, 2.5)), float(np.percentile(g, 97.5)))
    rb = RB.boot_cluster(A, B, n=M23_NBOOT, seed=M23_SEED)
    dc = max(abs(u - v) for u, v in zip(t5b, rb))
    out["c"] = {"pass": bool(dc <= 1e-12), "max_abs_diff": dc}
    # (d) offset 0 is the released pairing (Arm A at 10,000, held-out pair)
    ab = J("alignment_by_horizon.json")["arm_a"]["10000"]["summary_per_seed"]
    dn, dp = 0.0, 0.0
    starts = ctx.arenas["held_out"]["starts"]
    for s in SEEDS:
        model = ctx.rwm(AB_W[10000].format(a="A", s=s))
        s0 = MN.score(model, ctx.data, ctx.cfg, ctx.scale, starts, 32, 32, 0)
        st, ac = MN.window_arrays(ctx.data, ctx.cfg, starts, 32, 32)
        with torch.no_grad():
            pred = model.rollout(torch.as_tensor(st).clone(), torch.as_tensor(ac), 32, action_offset=0).numpy()
        native = MN.metrics(pred[:, 32:] - st[:, 32:], st[:, 32:], ctx.scale)
        dn = max([dn] + [abs(u - v) for h in HS for mt in ("l1", "nrmse") for u, v in zip(s0[str(h)][mt], native[str(h)][mt])])
        for h in HS:
            ratio = np.mean(s0[str(h)]["l1"]) / np.mean(sc[("A", s, 10000)]["held_out"][str(h)]["l1"])
            dp = max(dp, abs(ratio - (1 + ab[str(s)][str(h)]["rel_l1"]["pct"] / 100)))
    out["d"] = {"pass": bool(dn <= TOL_NATIVE and dp <= TOL), "native_max_abs_diff": dn,
                "stale_ratio_max_abs_diff": dp,
                "against": "results/alignment_by_horizon.json arm_a 10000 summary_per_seed rel_l1 pct, as the error ratio "
                           "1 + pct/100 (float32 rounding moves the percentage by about 1e-5 points)"}
    return out, {"sweep": v1, "baselines": bv1, "ab": r, "ab_scores": sc}


def native_check_sweep(ctx):
    """Before the reading: score(offset 0) equals the native offset-0 rollout for every sweep configuration with M < 32,
    seeds 0-2, on the held-out arena."""
    d, n_checked = 0.0, 0
    starts = ctx.arenas["held_out"]["starts"]
    for m, n in sweep_order():
        if m == 32:
            continue
        for s in SEEDS:
            model = ctx.rwm(MN.weights_path(m, n, s), m, n)
            s0 = MN.score(model, ctx.data, ctx.cfg, ctx.scale, starts, m, 32, 0)
            st, ac = MN.window_arrays(ctx.data, ctx.cfg, starts, m, 32)
            with torch.no_grad():
                pred = model.rollout(torch.as_tensor(st).clone(), torch.as_tensor(ac), m, action_offset=0).numpy()
            nat = MN.metrics(pred[:, m:] - st[:, m:], st[:, m:], ctx.scale)
            d = max([d] + [abs(u - v) for h in HS for mt in ("l1", "nrmse") for u, v in zip(s0[str(h)][mt], nat[str(h)][mt])])
            n_checked += 1
    return {"pass": bool(d <= TOL_NATIVE), "max_abs_diff": d, "n_models": n_checked}


def ledger_hashes(text):
    """Every 64-hex-digit token in backticks inside the ledger entry headed `### M-90 — `, lower-cased."""
    m = re.search(rf"^### {RULE_ID} — .*?(?=^### |\Z)", text, flags=re.M | re.S)
    return [] if not m else [x.lower() for x in re.findall(r"`([0-9a-fA-F]{64})`", m.group(0))]


def self_test():
    fails = []

    def check(name, cond):
        if not cond:
            fails.append(name)
    check("same verdict", reading_of("X", "X") == "SAME VERDICT")
    check("changed verdict", reading_of("X", "Y") == "VERDICT WOULD CHANGE TO Y")
    check("M-23: all three", m23_label(True, True, True) == M23_LABELS[0])
    check("M-23: no lead", m23_label(False, True, True) == M23_LABELS[1] and m23_label(False, False, False) == M23_LABELS[1])
    check("M-23: lead, interval spans", m23_label(True, False, True) == M23_LABELS[2])
    check("M-23: lead, sign inconsistent", m23_label(True, True, False) == M23_LABELS[2])
    check("changes lists only what moved", changes({"a": 1, "b": 2}, {"a": 1, "b": 3}) == {"b": [2, 3]})
    st = np.arange(12, dtype=np.float32).reshape(1, 4, 3)
    ac = np.arange(8, dtype=np.float32).reshape(1, 4, 2)
    _, a0 = MN._pairing((st, ac), 0)
    _, a1 = MN._pairing((st, ac), 1)
    check("offset 1 leaves the actions", np.array_equal(a1, ac))
    check("offset 0 moves every action one row later, the first repeated",
          np.array_equal(a0[0, 1:], ac[0, :-1]) and np.array_equal(a0[0, 0], ac[0, 0]))
    check("finite_tree catches a NaN", not finite_tree({"x": [1.0, float("nan")]}) and finite_tree({"x": [1.0, 2]}))
    h1 = "9" * 64
    fake = f"### M-89 — x\n`{'8' * 64}`\n### {RULE_ID} — PRE-REGISTERED rule X8\n`{h1}`\n"
    check("ledger: the entry's own hash only", ledger_hashes(fake) == [h1])
    check("ledger: another entry's hash does not count", ledger_hashes(fake.replace(f"### {RULE_ID} ", "### M-99 ")) == [])
    print(f"  self-test: {'PASS' if not fails else 'FAIL ' + str(fails)} (synthetic values; no reading)")
    return not fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--assert-only", action="store_true")
    args = ap.parse_args()
    os.chdir(ROOT)
    ok = self_test()
    if args.self_test or not ok:
        sys.exit(0 if ok else 1)
    me = sha256(os.path.abspath(__file__))
    print(f"  script SHA-256 {me}")
    if not args.assert_only:
        reg = ledger_hashes(open(os.path.join(ROOT, "FINDINGS_LEDGER.md"), encoding="utf-8").read())
        if me not in reg:
            blocked(f"ledger {RULE_ID} does not record this script's SHA-256 {me}: the rule is not pre-registered as run",
                    recorded=reg)
    try:
        ctx = Ctx()
        with tempfile.TemporaryDirectory() as td:
            asserts, ref = assertions(ctx, td)
    except (AssertionError, VB.CannotDischarge, VMN.CannotDischarge) as e:
        blocked(f"an internal check failed during the assertions: {e}")
    for k, v in asserts.items():
        print(f"  assertion ({k}): {'PASS' if v['pass'] else 'FAIL'}  " + ", ".join(
            f"{x} {y:.1e}" for x, y in v.items() if isinstance(y, float)))
    if not all(v["pass"] for v in asserts.values()):
        blocked("assertion(s) failed", assertions=asserts)
    if args.assert_only:
        print("  --assert-only: assertions (a)-(d) pass; nothing beyond cases committed artifacts hold was read")
        return
    try:
        asserts["d_sweep"] = native_check_sweep(ctx)
        if not asserts["d_sweep"]["pass"]:
            blocked("offset 0 differs from the native offset-0 rollout for a sweep configuration", assertions=asserts)
        ev0 = sweep_eval(ctx, 0)
        with tempfile.TemporaryDirectory() as td0:     # the offset-0 score file is written only once every check has passed
            eb0 = BE.evaluate(baselines_queued(), os.path.join(ROOT, "runs"), R.RESULTS, ITERS, os.path.join(td0, "b0.json"),
                              action_offset=0)
        sc0 = ab_scores(ctx, 0)
        if not (finite_tree(ev0["configs"]) and finite_tree(eb0["configs"]) and
                all(finite_tree(v) for v in sc0.values())):
            raise NonFinite("a non-finite score at offset 0")
        v0, bv0 = sweep_verdict(ev0), baselines_verdicts(eb0)
        r0 = ab_reading(ctx, sc0, sc0)
    except (AssertionError, NonFinite, VB.CannotDischarge, VMN.CannotDischarge) as e:
        blocked(f"the reading stopped: {e}", assertions=asserts)
    eb0.update({"action_offset": 0, "rollout": "baseline.rollout at the causal pairing, the actions moved one row later "
                                               "(mn_sweep_eval._pairing): the released evaluation's pairing",
                "rwm_check": {"note": "not applicable at offset 0", **eb0.get("rwm_check", {})}})
    json.dump(eb0, open(BASE_OUT, "w"), indent=2)
    json.dump(ev0, open(SWEEP_OUT, "w"), indent=2)
    vc, bvc = committed_sweep(), committed_baselines()
    r1 = ref["ab"]
    ab1, ab0 = r1["m23_three_seeds"]["label"], r0["m23_three_seeds"]["label"]
    readings = {
        "M-74": {"committed": vc["verdict"], "offset_0": v0["verdict"], "reading": reading_of(vc["verdict"], v0["verdict"]),
                 "alongside_changes": {**changes(vc["alongside"], v0["alongside"]),
                                       **{f"in_sample {k}": x for k, x in changes(vc["in_sample"], v0["in_sample"]).items()},
                                       **{f"per-episode sign {k} [positive, negative]": x
                                          for k, x in changes(vc["per_episode_sign"], v0["per_episode_sign"]).items()}}},
        **{rid: {"committed": bvc[rid]["verdict"], "offset_0": bv0[rid]["verdict"],
                 "reading": reading_of(bvc[rid]["verdict"], bv0[rid]["verdict"]),
                 "alongside_changes": {**changes(bvc[rid]["alongside"], bv0[rid]["alongside"]),
                                       **{f"in_sample {k}": x for k, x in changes(bvc[rid]["in_sample"], bv0[rid]["in_sample"]).items()},
                                       **{f"per-episode sign {k} [positive, negative]": x
                                          for k, x in changes(bvc[rid]["per_episode_sign"], bv0[rid]["per_episode_sign"]).items()}}}
           for rid in VB.RULES},
        "A/B (M-23's conditions, three seeds)": {"offset_1": ab1, "offset_0": ab0, "reading": reading_of(ab1, ab0),
                                                 "alongside_changes": changes(ab_alongside_labels(r1), ab_alongside_labels(r0))}}
    out = {"rule": "X8", "ledger": RULE_ID, "script": "scripts/x8_released_pairing.py", "script_sha256": me,
           "exploratory": True, "never_reopens": "M-23, M-74, M-75, M-76; nothing here changes their verdicts",
           "pairing": "offset 0 = each prediction of state i with action i - 1 (the released evaluation's); offset 1 = with "
                      "action i (causal, as every rule was scored)",
           "assertions": asserts, "readings": readings,
           "detail": {"M-74": {"offset_1": ref["sweep"], "offset_0": v0}, "baselines": {"offset_1": ref["baselines"], "offset_0": bv0},
                      "A/B": {"offset_1": {k: v for k, v in r1.items()}, "offset_0": r0}},
           "outputs": ["results/x8_sweep_eval_offset0.json", "results/x8_baselines_eval_offset0.json"],
           "caveats": ["our models under the released pairing; it says nothing direct about the original papers' printed numbers",
                       "the RSSM reads the window's first action row at its first filtering step (the row before it is outside "
                       "the window)"],
           "code_sha256": {p: sha256(os.path.join(ROOT, p)) for p in MODULES},
           "git_head": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()}
    json.dump(out, open(OUT, "w"), indent=2, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
    for k, v in readings.items():
        print(f"  X8 {k}: {v['reading']}" + (f"; alongside changes: {sorted(v['alongside_changes'])}" if v["alongside_changes"] else ""))
    print(f"  wrote {R.rel(OUT)}")


if __name__ == "__main__":
    main()
