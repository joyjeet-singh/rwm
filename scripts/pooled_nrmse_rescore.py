"""
Round 2, N2 (post hoc) -- nRMSE as section 3.1 defines it, for the M/N sweep and the
architecture baselines.

PLAN round2 Annex 1, N2. Nothing here is pre-registered; no discharged rule is re-opened, no
committed evaluation or verdict artifact is edited, and no verdict changes.

THE DEVIATION. Section 3.1's nRMSE form 1 (rwm_metrics.nrmse_pooled) pools the squared error
across trajectories before taking the root, as scripts/head_to_head_accuracy.py does. The
sweep and baseline evaluators (scripts/mn_sweep_eval.py, scripts/baselines_eval.py) instead
apply form 1 to each trajectory alone and their consumers average those per-trajectory values.
The two aggregations differ (RWM at h = 368: 0.5425 pooled against 0.4911 averaged), and the
stored per-trajectory values cannot be converted, so the rollouts are re-run.

WHAT IS RE-RUN, with each evaluator's own code: the sweep's score() (mn_sweep_eval.score, which
the baseline evaluator also uses) is called unchanged; its metrics() is wrapped for the call so
the raw errors are captured beside the per-trajectory values it returns. Models: the sweep's
centre (Arm A, 2,500 iterations) and its eight configurations, and the six Table S7 baseline
families, seeds 0-2, both arenas (held-out n = 4, in-sample n = 16), horizons 1, 8, 32, 100,
128, 368.

ASSERTED before anything new is written:
  (a) the centre's pooled nRMSE, per seed, equals head_to_head_accuracy.json's Arm A value at
      h in {1, 8, 100, 368} to 1e-6;
  (b) every model's per-trajectory relative-L1 (and per-trajectory nRMSE) equals the committed
      evaluator artifact to 1e-6;
  (c) the fast pooled form used inside the bootstrap equals rwm_metrics.nrmse_pooled exactly
      on every full arena and on sampled resamples;
  (d) the reading machinery below, run with the rules' own per-trajectory statistic on the
      committed data, reproduces every committed alongside nRMSE reading of M-74, M-75 and
      M-76 exactly (D, p, interval, Holm rank and level, rejection, branch or verdict).

THE POOLED READINGS. The verdict scripts' reading function (family) takes per-trajectory
differences, and pooled nRMSE has no per-trajectory value -- substituting one number per
model would make every resample identical. So each alongside nRMSE reading is recomputed with
the rule's design unchanged except the statistic: D = (3-seed mean pooled nRMSE of the
configuration) - (the same for the reference), recomputed on each of the rule's own resamples
(p5_sweep_power.resample_index's 256 at n = 4; the verdict's 20,000 Monte Carlo draws, seed 0,
at n = 16), seeds pooled inside each draw; p and the interval by the rules' formulas; Holm by
verdict_mn_sweep.holm; the branch by verdict_mn_sweep.branch (M-74) or verdict_baselines'
per_baseline and overall (M-75, M-76). Committed and pooled readings are written side by side.

THE DIVERGED FLAG (PLAN Annex 2, E7), defined here before any table renders it: a model row is
diverged if any seed's mean relative-L1 over the held-out trajectories at h = 368 exceeds 10x
the hold-last floor's.

Writes results/pooled_nrmse_rescore.json and results/pooled_nrmse_alongside.json.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, os.pardir, "src"))
import numpy as np  # noqa: E402
import torch  # noqa: E402

import baselines as BL  # noqa: E402
import mn_sweep_eval as MN  # noqa: E402
import p5_sweep_power as P5  # noqa: E402
import rollout_eval as E  # noqa: E402
import rwm_data as R  # noqa: E402
import rwm_metrics as MET  # noqa: E402
import rwm_model as M  # noqa: E402
import verdict_baselines as VB  # noqa: E402
import verdict_mn_sweep as VMN  # noqa: E402

SEEDS = ("0", "1", "2")
HORIZONS = MN.HORIZONS
H2H_H = (1, 8, 100, 368)
TOL = 1e-6
DIVERGED_X = 10.0
CHUNK = 2000

_orig_metrics = MN.metrics
_captured = []


def _capturing_metrics(err, truth, scale):
    _captured.append(np.asarray(err, dtype=np.float64))
    return _orig_metrics(err, truth, scale)


def score(model, data, cfg, scale, starts, m, m_max=32):
    """mn_sweep_eval.score, unchanged, plus the raw errors it scored."""
    _captured.clear()
    MN.metrics = _capturing_metrics
    try:
        per_traj = MN.score(model, data, cfg, scale, starts, m, m_max)
    finally:
        MN.metrics = _orig_metrics
    assert len(_captured) == 1
    err = _captured[0]                                  # (n_traj, 368, 45)
    sq = err ** 2
    pooled = {str(h): float(MET.nrmse_pooled(sq[:, :h], scale)) for h in HORIZONS}
    q = sq.mean(-1)                                     # (n_traj, 368): mean over dims per step
    return per_traj, pooled, q, sq


def fast_pooled(q, sel, smean):
    """nrmse_pooled over the trajectories in sel (repeats allowed), every horizon at once.
    nrmse_pooled = mean over steps of sqrt(mean over trajectories and dims of sq) / mean(scale)."""
    per_step = np.sqrt(q[sel].mean(-2)) / smean         # (..., 368)
    cum = np.cumsum(per_step, -1)
    return {str(h): cum[..., h - 1] / h for h in HORIZONS}


# ------------------------------------------------------------------ the reading machinery
def dist(diff_fn, point_fn, keys, draws):
    """Per-key resampled distribution of the statistic, over the rule's draws, chunked.
    diff_fn(key, sel) -> {h: array over the draws in sel}; point_fn(key) -> {h: float}."""
    out = {k: {str(h): [] for h in HORIZONS} for k in keys}
    for i in range(0, len(draws), CHUNK):
        sel = draws[i:i + CHUNK]
        for k in keys:
            v = diff_fn(k, sel)
            for h in map(str, HORIZONS):
                out[k][h].append(v[h])
    return {k: {h: np.concatenate(out[k][h]) for h in out[k]} for k in keys}, {k: point_fn(k) for k in keys}


def p_and_ci(b, exact):
    """The rules' formulas: p5_sweep_power.boot_p / boot_ci (exact), the verdicts' Monte Carlo branch."""
    p = float(min(1.0, 2 * min(np.mean(b <= 0), np.mean(b >= 0))))
    if exact:
        s = np.sort(b)
        ci = [float(np.quantile(s, 0.025)), float(np.quantile(s, 0.975))]
    else:
        ci = [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]
    return p, ci


def reading(dists, point, h, order, exact, decide):
    keys = [k for k in order if k in dists]
    p, ci = {}, {}
    for k in keys:
        p[k], ci[k] = p_and_ci(dists[k][h], exact)
    hol = VMN.holm(p, list(order))
    rejected = {k: hol[k]["rejected"] for k in keys}
    D = {k: point[k][h] for k in keys}
    return {"result": decide(D, rejected),
            "per_key": {k: {"D": D[k], "p": p[k], "ci95": ci[k], "rank": hol[k]["rank"],
                            "level": hol[k]["level"], "rejected": hol[k]["rejected"]} for k in keys}}


def m74_decide(D, rejected):
    return VMN.branch(D, rejected)[0]


def m7x_decide(names):
    def f(D, rejected):
        return VB.overall({k: VB.per_baseline(D[k], rejected[k]) for k in D}, names)
    return f


def same(a, b, tol=1e-12):
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def main():
    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    data, ep = R.load_data(paths["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"), verbose=False)
    scale = MET.training_scale(data, ep, split["train_episodes"], cfg["state_data_mean"], cfg["state_data_std"])
    smean = float(np.asarray(scale).mean())
    ev_mn = json.load(open(os.path.join(R.RESULTS, "mn_sweep_eval.json")))
    ev_bl = json.load(open(os.path.join(R.RESULTS, "baselines_eval.json")))
    arenas = {"held_out": MN.arena(ep, split["holdout_episodes"], 32),
              "in_sample": MN.arena(ep, split["train_episodes"], 32)}
    assert arenas["held_out"]["starts"] == ev_mn["arenas"]["held_out"]["starts"] == ev_bl["arenas"]["held_out"]["starts"]
    assert arenas["in_sample"]["starts"] == ev_mn["arenas"]["in_sample"]["starts"] == ev_bl["arenas"]["in_sample"]["starts"]

    timing = json.load(open(os.path.join(R.RESULTS, "mn_sweep_timing.json")))
    sweep = [(32, 8)] + [tuple(c) for c in timing["queued_configs"]]
    bl_queue = [tuple(q) for q in json.load(open(os.path.join(R.RESULTS, "baselines_timing.json")))["queued"]]

    models, check_b, maxdiff_b = {}, [], 0.0
    def record(key, family, committed, build, m, wpath):
        rec = {"family": family, "seeds": {}}
        for s in SEEDS:
            w = wpath(int(s))
            model = build()
            model.load_state_dict(torch.load(w, map_location="cpu")["model_state_dict"], strict=True)
            model.eval()
            rs = {"weights": os.path.relpath(w, R.REPO_ROOT) if os.path.isabs(w) else w}
            for a in ("held_out", "in_sample"):
                per_traj, pooled, q, sq = score(model, data, cfg, scale, arenas[a]["starts"], m)
                if s == "0" and key in CHECK_C:
                    SQ[(key, a)] = sq
                for h in map(str, HORIZONS):
                    for mt in ("l1", "nrmse"):
                        theirs = committed["seeds"][s][a][h][mt]
                        d = max(abs(x - y) for x, y in zip(per_traj[h][mt], theirs))
                        nonlocal_max[0] = max(nonlocal_max[0], d)
                        assert d < TOL, f"{key} seed {s} {a} h={h} {mt}: per-trajectory differs from the committed evaluator by {d}"
                rs[a] = {"pooled_nrmse": pooled,
                         "mean_per_traj_nrmse": {h: float(np.mean(per_traj[h]["nrmse"])) for h in pooled},
                         "per_traj_l1": {h: per_traj[h]["l1"] for h in pooled},
                         "mean_l1": {h: float(np.mean(per_traj[h]["l1"])) for h in pooled}}
                Q.setdefault(key, {}).setdefault(s, {})[a] = q
            rec["seeds"][s] = rs
        models[key] = rec

    nonlocal_max = [0.0]
    Q, SQ, CHECK_C = {}, {}, ("M32_N8", "mlp_tf_s7", "rssm_ar_s7")
    for m, n in sweep:
        key = f"M{m}_N{n}"
        c = dict(cfg)
        c["history_horizon"], c["forecast_horizon"] = m, n
        record(key, "sweep", ev_mn["configs"][key], lambda c=c: M.build_from_config(c, ensemble_size=1),
               m, lambda s, m=m, n=n: MN.weights_path(m, n, s))
    for arch, regime, spec in bl_queue:
        key = f"{arch}_{regime}_{spec}"
        record(key, "baseline", ev_bl["configs"][key], lambda a=arch, sp=spec: BL.build(a, sp, cfg),
               32, lambda s, a=arch, r=regime, sp=spec: os.path.join("runs", f"baseline_{a}_{r}_{sp}_seed{s}", "weights_2500.pt"))

    # (a) the centre against the head-to-head table (pooled form 1)
    h2h = json.load(open(os.path.join(R.RESULTS, "head_to_head_accuracy.json")))
    da = max(abs(models["M32_N8"]["seeds"][s]["held_out"]["pooled_nrmse"][str(h)]
                 - h2h["rows"]["armA"]["per_model"][f"armA_faithful_mse_seed{s}"][str(h)]["nrmse"])
             for s in SEEDS for h in H2H_H)
    assert da < TOL, f"(a) the centre's pooled nRMSE differs from the head-to-head table by {da}"

    # (c) the fast pooled form against rwm_metrics.nrmse_pooled
    rng = np.random.default_rng(12345)
    dc = 0.0
    for key in CHECK_C:
        for a in ("held_out", "in_sample"):
            q, sq = Q[key]["0"][a], SQ[(key, a)]
            n = q.shape[0]
            for sel in [np.arange(n)] + [rng.integers(0, n, n) for _ in range(5)]:
                fp = fast_pooled(q, sel[None, :], smean)
                for h in HORIZONS:
                    dc = max(dc, abs(float(fp[str(h)][0]) - float(MET.nrmse_pooled(sq[sel, :h], scale))))
    SQ.clear()
    assert dc < 1e-12, f"(c) fast pooled form differs from nrmse_pooled by {dc}"

    # the hold-last floor and the diverged flag (E7)
    floor = {a: {str(h): float(np.mean(ev_mn["floor"][a][str(h)]["l1"])) for h in HORIZONS} for a in arenas}
    diverged = {}
    for key, rec in models.items():
        per_seed = {s: rec["seeds"][s]["held_out"]["mean_l1"]["368"] for s in SEEDS}
        diverged[key] = {"per_seed_mean_l1_h368": per_seed, "floor_l1_h368": floor["held_out"]["368"],
                         "threshold": DIVERGED_X * floor["held_out"]["368"],
                         "diverged": any(v > DIVERGED_X * floor["held_out"]["368"] for v in per_seed.values())}

    # ---- the readings ------------------------------------------------------------------
    exact4 = P5.resample_index(4)
    mc16 = np.random.default_rng(VMN.MC_SEED).integers(0, 16, size=(VMN.MC_N, 16))
    draws = {"held_out": (exact4, True), "in_sample": (mc16, False)}

    def pooled_fns(arena, ref):
        """D = 3-seed mean pooled nRMSE of key minus the reference's, on each resample."""
        n = len(arenas[arena]["starts"])
        def mean_pooled(key, sel):
            return {h: np.mean([fast_pooled(Q[key][s][arena], sel, smean)[h] for s in SEEDS], 0) for h in map(str, HORIZONS)}
        def diff(key, sel):
            a, b = mean_pooled(key, sel), mean_pooled(ref, sel)
            return {h: a[h] - b[h] for h in a}
        def point(key):
            d = diff(key, np.arange(n)[None, :])
            return {h: float(d[h][0]) for h in d}
        return diff, point

    def committed_fns(ev, arena, ref, seed_mean):
        """the rules' own statistic, exactly as family() forms it: per-trajectory differences of the
        verdict module's seed_mean, averaged over each resample (p5_sweep_power.boot_dist's form)."""
        d = {k: {h: seed_mean(ev["configs"][k], arena, "nrmse", h) - seed_mean(ev["configs"][ref], arena, "nrmse", h)
                 for h in map(str, HORIZONS)} for k in ev["configs"]}
        def diff(key, sel):
            return {h: np.asarray(d[key][h], dtype=np.float64)[sel].mean(-1) for h in d[key]}
        def point(key):
            return {h: float(np.mean(d[key][h])) for h in d[key]}
        return diff, point

    rules = {
        "M-74": {"ev": ev_mn, "verdict": json.load(open(os.path.join(R.RESULTS, "mn_sweep_verdict.json"))),
                 "ref": "M32_N8", "order": [f"M{m}_N{n}" for m, n in timing["queued_configs"]],
                 "decide": m74_decide, "result_key": "branch", "per_key": "per_config",
                 "in_sample_h": ("100", "368"), "seed_mean": VMN.seed_mean},
    }
    bv = json.load(open(os.path.join(R.RESULTS, "baselines_verdict.json")))
    for rid in ("M-75", "M-76"):
        reg = VB.RULES[rid]["regime"]
        rules[rid] = {"ev": ev_bl, "verdict": bv["rules"][rid], "ref": "rwm",
                      "order": [f"{a}_{reg}_s7" for a in VB.ORDER], "arch_of": {f"{a}_{reg}_s7": a for a in VB.ORDER},
                      "decide": m7x_decide(VB.RULES[rid]["names"]), "result_key": "verdict", "per_key": "per_baseline",
                      "in_sample_h": tuple(str(h) for h in HORIZONS), "seed_mean": VB.seed_mean}
    # the reference model of M-75/M-76 is RWM, scored by baselines_eval exactly as the sweep's centre
    Q["rwm"] = Q["M32_N8"]
    models_rwm_check = max(abs(a - b) for s in SEEDS for a_ in ("held_out", "in_sample") for h in map(str, HORIZONS)
                           for a, b in zip(ev_bl["configs"]["rwm"]["seeds"][s][a_][h]["nrmse"],
                                           ev_mn["configs"]["M32_N8"]["seeds"][s][a_][h]["nrmse"]))
    assert models_rwm_check < TOL, f"baselines_eval's RWM differs from the sweep's centre by {models_rwm_check}"

    alongside, repro_d = {}, {"readings_compared": 0, "fields": ["D", "p", "ci95", "rank", "level", "rejected", "result"]}
    for rid, ru in rules.items():
        order, ref = ru["order"], ru["ref"]
        alongside[rid] = {}
        for arena in ("held_out", "in_sample"):
            dr, exact = draws[arena]
            hs = [str(h) for h in HORIZONS] if arena == "held_out" else list(ru["in_sample_h"])
            dc_, pc_ = dist(*committed_fns(ru["ev"], arena, ref, ru["seed_mean"]), order, dr)
            dp_, pp_ = dist(*pooled_fns(arena, ref), order, dr)
            for h in hs:
                committed_rd = reading(dc_, pc_, h, order, exact, ru["decide"])
                pooled_rd = reading(dp_, pp_, h, order, exact, ru["decide"])
                # (d) the machinery reproduces the committed reading exactly
                src = ru["verdict"]["alongside" if arena == "held_out" else "in_sample"][f"nrmse_h{h}"]
                assert committed_rd["result"] == src[ru["result_key"]], f"(d) {rid} {arena} h={h}: {committed_rd['result']} vs {src[ru['result_key']]}"
                for k in order:
                    sk = ru.get("arch_of", {}).get(k, k)
                    c, s_ = committed_rd["per_key"][k], src[ru["per_key"]][sk]
                    for f in ("D", "p"):
                        assert same(c[f], s_[f]), f"(d) {rid} {arena} h={h} {k} {f}: {c[f]} vs {s_[f]}"
                    assert all(same(x, y) for x, y in zip(c["ci95"], s_["ci95"])), f"(d) {rid} {arena} h={h} {k} ci"
                    assert c["rank"] == s_["rank"] and same(c["level"], s_["level"]) and c["rejected"] == s_["rejected"]
                repro_d["readings_compared"] += 1
                changed_keys = [k for k in order if (pooled_rd["per_key"][k]["rejected"], np.sign(pooled_rd["per_key"][k]["D"]))
                                != (committed_rd["per_key"][k]["rejected"], np.sign(committed_rd["per_key"][k]["D"]))]
                alongside[rid][f"{arena}|nrmse_h{h}"] = {
                    "committed": committed_rd, "pooled": pooled_rd,
                    "result_changed": committed_rd["result"] != pooled_rd["result"],
                    "keys_whose_direction_or_rejection_changed": changed_keys}

    rescore = {
        "purpose": "round 2 N2 (post hoc): nRMSE form 1 pooled across trajectories (section 3.1), for the sweep and the baselines",
        "post_hoc": True,
        "deviation": "the sweep and baseline evaluators apply form 1 per trajectory and their consumers average; section 3.1 pools across trajectories",
        "evaluator_code": "mn_sweep_eval.score (used by both evaluators), called unchanged; its metrics() wrapped only to capture the raw errors",
        "arenas": {a: {"starts": arenas[a]["starts"], "n_independent": arenas[a]["n_independent"]} for a in arenas},
        "horizons": list(HORIZONS), "seeds": [int(s) for s in SEEDS], "checkpoint_iterations": 2500,
        "asserts": {"a_centre_matches_head_to_head_pooled": {"horizons": list(H2H_H), "max_abs_diff": da, "tolerance": TOL},
                    "b_per_trajectory_l1_and_nrmse_match_committed_evaluators": {"max_abs_diff": nonlocal_max[0], "tolerance": TOL},
                    "c_fast_pooled_equals_nrmse_pooled": {"max_abs_diff": dc, "tolerance": 1e-12},
                    "rwm_in_baselines_eval_equals_sweep_centre": {"max_abs_diff": models_rwm_check, "tolerance": TOL}},
        "hold_last_floor_mean_l1": floor,
        "diverged_flag": {"definition": f"a model row is diverged if any seed's mean relative-L1 over the held-out trajectories at h = 368 exceeds {DIVERGED_X:g}x the hold-last floor's",
                          "rows": diverged,
                          "flagged": sorted(k for k, v in diverged.items() if v["diverged"])},
        "models": models,
        "three_seed_mean": {k: {a: {"pooled_nrmse": {h: float(np.mean([v["seeds"][s][a]["pooled_nrmse"][h] for s in SEEDS])) for h in map(str, HORIZONS)},
                                    "mean_per_traj_nrmse": {h: float(np.mean([v["seeds"][s][a]["mean_per_traj_nrmse"][h] for s in SEEDS])) for h in map(str, HORIZONS)},
                                    "mean_l1": {h: float(np.mean([v["seeds"][s][a]["mean_l1"][h] for s in SEEDS])) for h in map(str, HORIZONS)}}
                                for a in arenas} for k, v in models.items()},
    }
    changed = sorted(f"{rid} {k}" for rid in alongside for k, v in alongside[rid].items() if v["result_changed"])
    along = {
        "purpose": "round 2 N2 (post hoc): each rule's alongside nRMSE readings, committed (per-trajectory average) and pooled (section 3.1), side by side",
        "post_hoc": True,
        "never_governing": "governing verdicts use relative-L1 at h = 368 and are unaffected; a changed alongside reading is reported, never substituted into a discharged rule",
        "method": ("the rule's design with only the statistic changed: D = 3-seed mean pooled nRMSE of the configuration minus the "
                   "reference's, recomputed on each of the rule's own resamples (p5_sweep_power.resample_index at n = 4; the "
                   "verdict's 20,000 Monte Carlo draws, seed 0, at n = 16), seeds pooled inside each draw; p and interval by the "
                   "rules' formulas; Holm by verdict_mn_sweep.holm; branch by verdict_mn_sweep.branch or verdict_baselines.per_baseline/overall. "
                   "The verdict scripts' family() takes per-trajectory differences, which pooled nRMSE does not have."),
        "assert_d_machinery_reproduces_committed_readings": repro_d,
        "readings": alongside,
        "readings_whose_result_changed": changed,
        "inputs": ["results/mn_sweep_eval.json", "results/baselines_eval.json", "results/mn_sweep_verdict.json",
                   "results/baselines_verdict.json", "results/head_to_head_accuracy.json"],
    }
    json.dump(rescore, open(os.path.join(R.RESULTS, "pooled_nrmse_rescore.json"), "w"), indent=2)
    json.dump(along, open(os.path.join(R.RESULTS, "pooled_nrmse_alongside.json"), "w"), indent=2)

    print("=" * 100)
    print("N2 (post hoc) — nRMSE form 1 pooled across trajectories, for the sweep and the baselines")
    print("=" * 100)
    print(f"  (a) centre vs head-to-head: max |diff| {da:.2e};  (b) per-trajectory vs evaluators: {nonlocal_max[0]:.2e};  "
          f"(c) fast pooled: {dc:.2e};  (d) committed readings reproduced: {repro_d['readings_compared']}")
    for k, v in rescore["three_seed_mean"].items():
        ho = v["held_out"]
        print(f"  {k:<18} held-out h=368  pooled {ho['pooled_nrmse']['368']:.4f}  per-traj avg {ho['mean_per_traj_nrmse']['368']:.4f}  "
              f"rel-L1 {ho['mean_l1']['368']:.4f}{'   † diverged' if diverged[k]['diverged'] else ''}")
    print(f"  diverged rows (E7): {rescore['diverged_flag']['flagged']}")
    print(f"  alongside readings whose result changed under pooling: {changed or 'none'}")
    print("  wrote results/pooled_nrmse_rescore.json, results/pooled_nrmse_alongside.json")


if __name__ == "__main__":
    main()
