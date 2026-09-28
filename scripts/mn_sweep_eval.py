"""
M-74 -- the common-window evaluator for the M/N sweep.

EVERY CONFIGURATION IS SCORED ON THE SAME FORECAST TARGET ROWS. A window is a start row
s; its forecast targets are rows s + M_MAX ... s + M_MAX + 367 (368 steps) for every
configuration, and a configuration with history M sees the M rows immediately before
them, s + M_MAX - M ... s + M_MAX - 1. M_MAX is the longest history in the grid. Rule
M-74's grid tops out at M = 32, so M_MAX = 32 and the held-out windows are exactly §5's
four trajectories (starts 999, 1399, 7999, 8399) -- asserted below, not assumed.

Two arenas, as M-74 states them:
  held-out   episodes 1 and 8, two non-overlapping windows each, n_independent = 4.
             This arena governs.
  in-sample  the eight training episodes, two windows each, n_independent = 16.
             Reported only.

Rollout: the existing harness, autoregressive from the history, hidden state carried,
action_offset = 1 (causal), one batched call per arena per model. Metrics: relative-L1
(the upstream's; per trajectory, the mean over forecast steps 1..h of summed |error| over
summed |truth|) and nRMSE form 1 (rwm_metrics.nrmse_pooled per trajectory, training-
episode scale), at h = 1, 8, 32, 100, 128, 368, cumulative. The hold-last floor holds
row s + M_MAX - 1, so it is the same for every configuration.

  --centre-only   score the existing Arm A (32, 8) seeds 0-2 at 2,500 iterations and
                  write results/mn_sweep_centre.json (S2a; inference only). The held-out
                  relative-L1 must reproduce results/head_to_head_accuracy.json.
  (default)       score the centre and every configuration the sweep queued
                  (results/mn_sweep_timing.json, "queued_configs") and write
                  results/mn_sweep_eval.json (S8). A missing checkpoint is an error.
"""
import argparse
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import torch  # noqa: E402

import rollout_eval as E  # noqa: E402
import rwm_data as R  # noqa: E402
import rwm_metrics as MET  # noqa: E402
import rwm_model as M  # noqa: E402

CENTRE = (32, 8)
SEEDS = (0, 1, 2)
ITERS = 2500
FORECAST = 368
HORIZONS = (1, 8, 32, 100, 128, 368)
HELD_OUT_STARTS = [999, 1399, 7999, 8399]      # §5's trajectories, asserted


def weights_path(m, n, s):
    if (m, n) == CENTRE:
        return os.path.join("runs", f"armA_seed{s}", f"weights_{ITERS}.pt")
    return os.path.join("runs", f"mn_M{m}_N{n}_seed{s}", f"weights_{ITERS}.pt")


def run_artifact(m, n, s):
    if (m, n) == CENTRE:
        return os.path.join("results", f"step5_armA_seed{s}.json")
    return os.path.join("results", f"mn_sweep_run_M{m}_N{n}_seed{s}.json")


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def arena(ep, episodes, m_max):
    starts = MET.non_overlapping_starts(ep, episodes, m_max + FORECAST)
    n_ind = int(MET.n_independent(starts, m_max + FORECAST))
    return {"episodes": list(episodes), "starts": [int(s) for s in starts],
            "episode_of_window": [int(ep[s]) for s in starts], "n_independent": n_ind,
            "forecast_rows": [[int(s + m_max), int(s + m_max + FORECAST - 1)] for s in starts]}


def metrics(err, truth, scale):
    """err, truth: (n_traj, 368, 45) -> {h: {"l1": [..], "nrmse": [..]}} per trajectory."""
    num = np.abs(err).sum(-1)
    den = np.abs(truth).sum(-1)
    sq = err.astype(np.float64) ** 2
    out = {}
    for h in HORIZONS:
        out[str(h)] = {"l1": (num[:, :h] / den[:, :h]).mean(1).tolist(),
                       "nrmse": [MET.nrmse_pooled(sq[t:t + 1, :h], scale)
                                 for t in range(err.shape[0])]}
    return out


def window_arrays(data, cfg, starts, m, m_max):
    """State and action rows s + m_max - m ... s + m_max + 367 for each window s."""
    idx = np.asarray(starts)[:, None] + (m_max - m) + np.arange(m + FORECAST)[None, :]
    raw = data[idx]
    st = R.normalise_state(raw[:, :, R.STATE_COLS], cfg["state_data_mean"],
                           cfg["state_data_std"]).astype(np.float32)
    ac = raw[:, :, R.ACTION_COLS].astype(np.float32)
    return st, ac


def score(model, data, cfg, scale, starts, m, m_max):
    st, ac = window_arrays(data, cfg, starts, m, m_max)
    with torch.no_grad():
        pred = model.rollout(torch.as_tensor(st).clone(), torch.as_tensor(ac), m,
                             action_offset=1).numpy()
    truth = st[:, m:]
    return metrics(pred[:, m:] - truth, truth, scale)


def floor(data, cfg, scale, starts, m_max):
    st, _ = window_arrays(data, cfg, starts, m_max, m_max)
    truth = st[:, m_max:]
    hold = np.repeat(st[:, m_max - 1:m_max], FORECAST, axis=1)
    return metrics(hold - truth, truth, scale)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--centre-only", action="store_true")
    args = ap.parse_args()

    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    data, ep = R.load_data(paths["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"),
                         verbose=False)
    scale = MET.training_scale(data, ep, split["train_episodes"],
                               cfg["state_data_mean"], cfg["state_data_std"])
    stored = np.array(json.load(open(os.path.join(R.RESULTS, "step4_0a_results.json")))
                      ["nrmse_scale"])
    assert np.allclose(scale, stored), "nRMSE scale differs from the stored one"

    if args.centre_only:
        configs = [CENTRE]
    else:
        timing = json.load(open(os.path.join(R.RESULTS, "mn_sweep_timing.json")))
        configs = [CENTRE] + [tuple(c) for c in timing["queued_configs"]]
    m_max = 32
    assert max(m for m, _ in configs + [CENTRE]) == m_max, "M-74's longest history is 32"

    arenas = {"held_out": arena(ep, split["holdout_episodes"], m_max),
              "in_sample": arena(ep, split["train_episodes"], m_max)}
    assert arenas["held_out"]["starts"] == HELD_OUT_STARTS, arenas["held_out"]["starts"]
    assert arenas["held_out"]["n_independent"] == 4, "M-74 is written for n_independent = 4"
    assert arenas["in_sample"]["n_independent"] == 16, "M-74's in-sample arena is 16"

    missing = [weights_path(m, n, s) for m, n in configs for s in SEEDS
               if not os.path.exists(weights_path(m, n, s))]
    assert not missing, f"checkpoints missing, cannot score: {missing}"

    out_cfg = {}
    for m, n in configs:
        key = f"M{m}_N{n}"
        rec = {"M": m, "N": n, "centre": (m, n) == CENTRE, "seeds": {}}
        for s in SEEDS:
            w = weights_path(m, n, s)
            c = dict(cfg)
            c["history_horizon"], c["forecast_horizon"] = m, n
            model = M.build_from_config(c, ensemble_size=1)
            model.load_state_dict(torch.load(w, map_location="cpu")["model_state_dict"],
                                  strict=True)
            model.eval()
            art = json.load(open(run_artifact(m, n, s)))
            hp = art["hyperparameters"]
            assert hp["iterations"] == ITERS, f"{key} seed {s}: {hp['iterations']} iterations"
            assert art["seed"] == s and art["arm"] == "A"
            # The centre's artifacts (results/step5_armA_seed{0,1,2}.json) predate the M/N
            # and width fields (FILE_MAP.md §5), so only sweep runs can be checked for them;
            # the centre is checked instead by reproducing §5's head-to-head table below.
            if (m, n) != CENTRE:
                assert hp["history_horizon"] == m and hp["forecast_horizon"] == n
                assert hp["rnn_hidden_size"] == 256 and art["arch"] == "rwm"
            assert all(np.isfinite(art["curves"]["total"])), f"{key} seed {s}: NaN in loss"
            rec["seeds"][str(s)] = {
                "weights": w, "weights_sha256": sha256(w), "run_artifact": run_artifact(m, n, s),
                "wall_clock_s": art["wall_clock_s"], "n_train_windows": hp["n_train_windows"],
                "held_out": score(model, data, cfg, scale, arenas["held_out"]["starts"], m, m_max),
                "in_sample": score(model, data, cfg, scale, arenas["in_sample"]["starts"], m, m_max)}
        out_cfg[key] = rec

    # The centre's held-out relative-L1 must be the head-to-head table's (§5's arena).
    h2h = json.load(open(os.path.join(R.RESULTS, "head_to_head_accuracy.json")))
    check = []
    for s in SEEDS:
        for h in h2h["horizons"]:
            mine = float(np.mean(out_cfg["M32_N8"]["seeds"][str(s)]["held_out"][str(h)]["l1"]))
            theirs = h2h["rows"]["armA"]["per_model"][f"armA_faithful_mse_seed{s}"][str(h)]["l1"]
            assert abs(mine - theirs) < 1e-6, f"centre seed {s} h={h}: {mine} vs {theirs}"
            check.append(abs(mine - theirs))

    out = {"rule": "M-74",
           "what": ("the centre only (S2a re-score, inference only)" if args.centre_only
                    else "the centre and every queued sweep configuration (S8)"),
           "arenas": arenas, "m_max": m_max, "forecast_steps": FORECAST,
           "history_rows": {f"M{m}_N{n}": [[int(s + m_max - m), int(s + m_max - 1)]
                                           for s in arenas["held_out"]["starts"]]
                            for m, n in configs},
           "horizons": list(HORIZONS), "seeds": list(SEEDS), "checkpoint_iterations": ITERS,
           "metrics": {"l1": "relative-L1, per trajectory, mean over steps 1..h of summed "
                             "|error| / summed |truth|, config-normalised state",
                       "nrmse": "form 1, rwm_metrics.nrmse_pooled per trajectory, "
                                "training-episode scale"},
           "rollout": "model.rollout(history, actions, start_step = M, action_offset = 1), "
                      "one batched call per arena per model",
           "floor": {"held_out": floor(data, cfg, scale, arenas["held_out"]["starts"], m_max),
                     "in_sample": floor(data, cfg, scale, arenas["in_sample"]["starts"], m_max)},
           "configs": out_cfg,
           "centre_check": {"against": "results/head_to_head_accuracy.json armA per_model l1",
                            "max_abs_diff": max(check), "tolerance": 1e-6}}
    op = os.path.join(R.RESULTS, "mn_sweep_centre.json" if args.centre_only
                      else "mn_sweep_eval.json")
    json.dump(out, open(op, "w"), indent=2)
    print("=" * 90)
    print(f"M-74 COMMON-WINDOW EVALUATOR — {out['what']}")
    print("=" * 90)
    for a, v in arenas.items():
        print(f"  {a:<9} episodes {v['episodes']}  starts {v['starts']}  "
              f"n_independent = {v['n_independent']}")
    for key, rec in out_cfg.items():
        l1 = np.mean([np.mean(v["held_out"]["368"]["l1"]) for v in rec["seeds"].values()])
        l1_100 = np.mean([np.mean(v["held_out"]["100"]["l1"]) for v in rec["seeds"].values()])
        print(f"  {key:<8} held-out relative-L1  h=100 {l1_100:.4f}  h=368 {l1:.4f}")
    print(f"  centre reproduces the head-to-head table: max |diff| {max(check):.2e}")
    print(f"  wrote {R.rel(op)}")


if __name__ == "__main__":
    main()
