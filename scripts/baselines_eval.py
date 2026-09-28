"""
Rules M-75 and M-76 -- the evaluator for the architecture baselines.

Scores every queued baseline, and RWM (the existing Arm A, (32, 8), seeds 0-2, 2,500
iterations), on the SAME windows, with the SAME metrics, through the SAME functions as the
M-74 sweep: scripts/mn_sweep_eval.py's arenas, window arrays, metrics and hold-last floor are
imported, not copied. So the baselines, RWM and the sweep are all scored on section 5's four
held-out trajectories (rows 999, 1399, 7999, 8399; 32 history rows; 368 forecast rows) and
on the 16-window in-sample arena.

Rollout: each baseline's own rollout(history, actions, start_step = 32, action_offset = 1),
autoregressive from the history, feeding back the mean (src/baselines/).

    python scripts/baselines_eval.py              # S8: every queued baseline -> results/baselines_eval.json
    python scripts/baselines_eval.py --self-test  # untrained baselines, temp dir, plumbing only

The queued baselines are read from results/baselines_timing.json ("queued").
"""
import argparse
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import torch  # noqa: E402

import baselines as BL  # noqa: E402
import mn_sweep_eval as MN  # noqa: E402
import rollout_eval as E  # noqa: E402
import rwm_data as R  # noqa: E402
import rwm_metrics as MET  # noqa: E402
import rwm_model as M  # noqa: E402

SEEDS = (0, 1, 2)
ITERS = 2500
M_HIST = 32


def key(arch, regime, spec):
    return f"{arch}_{regime}_{spec}"


def weights_path(runs, arch, regime, spec, s, iters):
    return os.path.join(runs, f"baseline_{arch}_{regime}_{spec}_seed{s}", f"weights_{iters}.pt")


def run_artifact(results, arch, regime, spec, s):
    return os.path.join(results, f"baseline_run_{arch}_{regime}_{spec}_seed{s}.json")


def evaluate(queued, runs, results, iters, out_path, check_artifacts=True):
    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    data, ep = R.load_data(paths["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"),
                         verbose=False)
    scale = MET.training_scale(data, ep, split["train_episodes"],
                               cfg["state_data_mean"], cfg["state_data_std"])
    arenas = {"held_out": MN.arena(ep, split["holdout_episodes"], M_HIST),
              "in_sample": MN.arena(ep, split["train_episodes"], M_HIST)}
    assert arenas["held_out"]["starts"] == MN.HELD_OUT_STARTS
    assert arenas["held_out"]["n_independent"] == 4 and arenas["in_sample"]["n_independent"] == 16

    missing = [weights_path(runs, *q, s, iters) for q in queued for s in SEEDS
               if not os.path.exists(weights_path(runs, *q, s, iters))]
    assert not missing, f"checkpoints missing, cannot score: {missing}"

    out_cfg = {}
    # RWM: the existing Arm A, scored exactly as the sweep scores its centre.
    rwm = {"arch": "rwm", "seeds": {}}
    for s in SEEDS:
        w = MN.weights_path(32, 8, s)
        model = M.build_from_config(cfg, ensemble_size=1)
        model.load_state_dict(torch.load(w, map_location="cpu")["model_state_dict"], strict=True)
        model.eval()
        art = json.load(open(MN.run_artifact(32, 8, s)))
        rwm["seeds"][str(s)] = {
            "weights": w, "weights_sha256": MN.sha256(w), "wall_clock_s": art["wall_clock_s"],
            # the state pathway only (state_base + state_heads), as p2_capacity_power counts it
            "n_params": BL.n_params(model.state_base) + BL.n_params(model.state_heads),
            "held_out": MN.score(model, data, cfg, scale, arenas["held_out"]["starts"], 32, 32),
            "in_sample": MN.score(model, data, cfg, scale, arenas["in_sample"]["starts"], 32, 32)}
    out_cfg["rwm"] = rwm

    for arch, regime, spec in queued:
        rec = {"arch": arch, "regime": regime, "spec": spec, "seeds": {}}
        for s in SEEDS:
            w = weights_path(runs, arch, regime, spec, s, iters)
            model = BL.build(arch, spec, cfg)
            model.load_state_dict(torch.load(w, map_location="cpu")["model_state_dict"],
                                  strict=True)
            model.eval()
            info = {"weights": os.path.relpath(w, R.REPO_ROOT), "weights_sha256": MN.sha256(w),
                    "n_params": BL.n_params(model)}
            if check_artifacts:
                art = json.load(open(run_artifact(results, arch, regime, spec, s)))
                hp = art["hyperparameters"]
                assert hp["iterations"] == iters and art["seed"] == s
                assert (art["arch"], art["regime"], art["spec"]) == (arch, regime, spec)
                assert all(np.isfinite(art["curves"]["total"])), f"{key(arch, regime, spec)} {s}: NaN"
                assert hp["n_params"] == info["n_params"]
                info.update({"wall_clock_s": art["wall_clock_s"],
                             "n_train_windows": hp["n_train_windows"]})
            for a in ("held_out", "in_sample"):
                info[a] = MN.score(model, data, cfg, scale, arenas[a]["starts"], M_HIST, M_HIST)
            rec["seeds"][str(s)] = info
        out_cfg[key(arch, regime, spec)] = rec

    # RWM must reproduce the head-to-head table (§5's arena), as the sweep's centre does.
    h2h = json.load(open(os.path.join(R.RESULTS, "head_to_head_accuracy.json")))
    assert all(v["n_params"] == BL.RWM_STATE_PATHWAY for v in rwm["seeds"].values())
    diff = max(abs(float(np.mean(rwm["seeds"][str(s)]["held_out"][str(h)]["l1"]))
                   - h2h["rows"]["armA"]["per_model"][f"armA_faithful_mse_seed{s}"][str(h)]["l1"])
               for s in SEEDS for h in h2h["horizons"])
    assert diff < 1e-6, f"RWM does not reproduce the head-to-head table: {diff}"

    out = {"rules": ["M-75", "M-76"], "arenas": arenas, "horizons": list(MN.HORIZONS),
           "seeds": list(SEEDS), "checkpoint_iterations": iters, "history_rows": M_HIST,
           "forecast_steps": MN.FORECAST,
           "rollout": "baseline.rollout(history, actions, start_step = 32, action_offset = 1)",
           "floor": {a: MN.floor(data, cfg, scale, arenas[a]["starts"], M_HIST)
                     for a in ("held_out", "in_sample")},
           "configs": out_cfg, "rwm_check": {"against": "results/head_to_head_accuracy.json",
                                             "max_abs_diff": diff}}
    json.dump(out, open(out_path, "w"), indent=2)
    return out


def self_test():
    """Untrained baselines, saved and scored end to end in a scratch directory."""
    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    queued = [(a, g, "s7") for a in ("mlp", "rssm", "transformer") for g in ("tf", "ar")]
    with tempfile.TemporaryDirectory() as td:
        for arch, regime, spec in queued:
            for s in SEEDS:
                torch.manual_seed(s)
                m = BL.build(arch, spec, cfg)
                p = weights_path(td, arch, regime, spec, s, 0)
                os.makedirs(os.path.dirname(p), exist_ok=True)
                torch.save({"model_state_dict": m.state_dict()}, p)
        out = evaluate(queued, td, td, 0, os.path.join(td, "eval.json"), check_artifacts=False)
    fine = all(np.all(np.isfinite(out["configs"][key(*q)]["seeds"][str(s)][a][h][mt]))
               for q in queued for s in SEEDS for a in ("held_out", "in_sample")
               for h in ("1", "368") for mt in ("l1", "nrmse"))
    print(f"  self-test: {len(queued)} baselines x 3 seeds scored end to end, all finite: {fine}; "
          f"RWM reproduces the head-to-head table to {out['rwm_check']['max_abs_diff']:.1e}")
    return fine


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        sys.exit(0 if self_test() else 1)
    timing = json.load(open(os.path.join(R.RESULTS, "baselines_timing.json")))
    queued = [tuple(q) for q in timing["queued"]]
    out = evaluate(queued, os.path.join(R.REPO_ROOT, "runs"), R.RESULTS, ITERS,
                   os.path.join(R.RESULTS, "baselines_eval.json"))
    print(f"  scored RWM and {len(queued)} baselines; wrote results/baselines_eval.json")


if __name__ == "__main__":
    main()
