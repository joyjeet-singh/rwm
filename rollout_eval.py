"""
Step 2 -- evaluation harness for the RWM reproduction.

No model code lives here. The harness sees a model only through

    predict_fn(history_states, history_actions, future_actions) -> predicted_states

and scores whatever comes back. The same harness scores the reference
checkpoint (Step 3) and the from-scratch model (Step 6).

Protocol, and where it deviates from the reference:

  MATCHED   10 trajectories x 400 steps (num_eval_trajectories, len_eval_trajectory
            in base_cfg.py:45-46); first 32 steps history (start_step =
            history_horizon, model_training.py:201); true actions at every step;
            metric exactly as model_training.py:203; noise scales from
            base_cfg.py:99 applied exactly as model_training.py:221-227.

  DEVIATED  Trajectories are sampled only from held-out episodes and may not
            cross an episode boundary. The reference builds eval trajectories
            from the full dataset before any split (train.py:109) and splits
            training windows with random_split over windows overlapping by 39
            of 40 rows (model_training.py:33). Both leak. Protocol B below
            reproduces the reference behaviour so the two can be compared.
"""

import json
import os

import numpy as np
import torch

import rwm_data as R

HISTORY = 32
LEN_TRAJ = 400
N_TRAJ = 10
NOISE_SCALES = [0.1, 0.2, 0.4, 0.5, 0.8]
START_STEP = HISTORY          # model_training.py:201  self.start_step = self.history_horizon
BLOWUP = 10.0                 # r_t above this counts as a blow-up


# --------------------------------------------------------------------------
# split
# --------------------------------------------------------------------------
def make_split(seed=0, n_holdout=2, strat_path=None, verbose=True):
    """
    Episode-level split, seeded and printed. Step 0 established that the ten
    episodes carry different velocity commands (two regimes each, all distinct),
    so the held-out pair is stratified by mean commanded speed: the episodes are
    ranked by speed, cut into a fast half and a slow half, and one held-out
    episode is drawn from each. Without this a seed could hand back the two
    slowest episodes and the held-out score would describe only slow walking.
    """
    rng = np.random.default_rng(seed)
    eps = np.arange(R.N_EPISODES)

    speeds = None
    if strat_path and os.path.exists(strat_path):
        with open(strat_path) as f:
            strat = json.load(f)
        speeds = np.array([strat[str(e)]["mean_speed"] for e in eps])

    if speeds is None:
        holdout = np.sort(rng.choice(eps, size=n_holdout, replace=False))
        method = "uniform (no Step 0 stratification file found)"
    else:
        order = np.argsort(speeds)[::-1]
        fast, slow = order[:R.N_EPISODES // 2], order[R.N_EPISODES // 2:]
        holdout = np.sort([rng.choice(fast), rng.choice(slow)])
        method = "stratified by mean commanded speed (one fast, one slow)"

    train = np.array([e for e in eps if e not in holdout])
    split = {"seed": int(seed), "method": method,
             "train_episodes": train.tolist(), "holdout_episodes": holdout.tolist()}
    if speeds is not None:
        split["episode_mean_speeds"] = {int(e): float(speeds[e]) for e in eps}
        split["holdout_speeds"] = {int(e): float(speeds[e]) for e in holdout}
    if verbose:
        print(f"  split seed {seed}, {method}")
        print(f"  TRAIN episodes  : {train.tolist()}")
        print(f"  HELD-OUT episodes: {holdout.tolist()}")
        if speeds is not None:
            print(f"  held-out mean commanded speeds: "
                  f"{[f'ep{e}={speeds[e]:.2f} m/s' for e in holdout]}")
    return split


def training_window_rows(episode_id, split, window=40):
    """Every row index touched by a training window (used by acceptance test 5)."""
    rows = set()
    for s in R.valid_window_starts(episode_id, window):
        if episode_id[s] in split["train_episodes"]:
            rows.update(range(s, s + window))
    return rows


# --------------------------------------------------------------------------
# eval trajectories
# --------------------------------------------------------------------------
def sample_trajectories(episode_id, allowed_episodes, n_traj=N_TRAJ,
                        len_traj=LEN_TRAJ, seed=0, allow_boundary_cross=False):
    """
    Return (n_traj, len_traj) row indices.

    allow_boundary_cross=False -> protocol A: each trajectory lies inside one
    episode. True -> protocol B: uniform over all rows as train.py:85-86 does,
    boundary crossings permitted.
    """
    rng = np.random.default_rng(seed)
    if allow_boundary_cross:
        starts = rng.integers(0, len(episode_id) - len_traj + 1, size=n_traj)
    else:
        cand = np.array([s for s in R.valid_window_starts(episode_id, len_traj)
                         if episode_id[s] in allowed_episodes])
        assert len(cand) >= 1, "no valid trajectory start in the allowed episodes"
        starts = rng.choice(cand, size=n_traj, replace=len(cand) < n_traj)
    return starts[:, None] + np.arange(len_traj)[None, :]


def assert_within_episode(idx, episode_id):
    """Acceptance test 4."""
    for k, row in enumerate(idx):
        eps = episode_id[row]
        assert eps[0] >= 0, f"trajectory {k} starts in the discarded stub row"
        assert np.all(eps == eps[0]), (
            f"trajectory {k} crosses an episode boundary: "
            f"touches episodes {sorted(set(eps.tolist()))}")
    return True


def count_boundary_crossings(idx, episode_id):
    return sum(1 for row in idx if len(set(episode_id[row].tolist())) > 1)


# --------------------------------------------------------------------------
# metric
# --------------------------------------------------------------------------
def relative_error(pred, true, start_step=START_STEP):
    """
    model_training.py:203, verbatim in behaviour:

        r_t = sum_d |pred[t,d] - true[t,d]| / sum_d |true[t,d]|
        e   = mean over trajectories and timesteps of r_t

    pred/true: (B, len_traj, 45) NORMALISED states. Returns (e, r) with
    r of shape (B, len_traj - start_step).
    """
    num = (pred[:, start_step:] - true[:, start_step:]).abs().sum(dim=-1)
    den = true[:, start_step:].abs().sum(dim=-1)
    r = num / den
    return float(r.mean().item()), r


def metric_block(pred, true, start_step=START_STEP):
    e, r = relative_error(pred, true, start_step)
    rf = r.flatten()
    finite = torch.isfinite(rf)
    return {
        "e": e,
        "median_r": float(rf.median().item()),
        "frac_r_gt_10": float((rf > BLOWUP).double().mean().item()),
        "max_r": float(rf.max().item()),
        "frac_nonfinite": float((~finite).double().mean().item()),
        "per_step_mean": r.mean(dim=0).detach().cpu().numpy(),
        "per_step_median": r.median(dim=0).values.detach().cpu().numpy(),
    }


# --------------------------------------------------------------------------
# the harness
# --------------------------------------------------------------------------
def evaluate(predict_fn, data, split, config=None):
    """
    Score `predict_fn` under the protocol in `config`.

    predict_fn(history_states, history_actions, future_actions) -> predicted_states
        history_states  (B, 32, 45)  normalised
        history_actions (B, 32, 12)  normalised (identity: actions are not normalised)
        future_actions  (B, 368, 12) true actions at forecast steps 32..399
        returns         (B, 368, 45) predicted normalised states for steps 32..399

    The harness owns normalisation, windowing, the metric and the noise sweep.
    Nothing model-specific appears in this function.
    """
    cfg = dict(config or {})
    episode_id = cfg["episode_id"]
    seed = cfg.get("seed", 0)
    n_traj = cfg.get("n_traj", N_TRAJ)
    len_traj = cfg.get("len_traj", LEN_TRAJ)
    start_step = cfg.get("start_step", START_STEP)
    noise_scales = cfg.get("noise_scales", NOISE_SCALES)
    cross = cfg.get("allow_boundary_cross", False)
    s_mean, s_std = cfg["state_data_mean"], cfg["state_data_std"]
    a_mean, a_std = cfg["action_data_mean"], cfg["action_data_std"]

    idx = sample_trajectories(episode_id, split["holdout_episodes"], n_traj,
                              len_traj, seed=seed, allow_boundary_cross=cross)
    if not cross:
        assert_within_episode(idx, episode_id)
    n_cross = count_boundary_crossings(idx, episode_id)

    raw = data[idx]                                     # (B, len_traj, 66)
    state = torch.as_tensor(
        R.normalise_state(raw[:, :, R.STATE_COLS], s_mean, s_std), dtype=torch.float32)
    action = torch.as_tensor(
        R.normalise_action(raw[:, :, R.ACTION_COLS], a_mean, a_std), dtype=torch.float32)

    def run(st, ac):
        pred_future = predict_fn(st[:, :start_step], ac[:, :start_step], ac[:, start_step:])
        assert pred_future.shape == (st.shape[0], len_traj - start_step, R.STATE_DIM), (
            f"predict_fn returned {tuple(pred_future.shape)}, expected "
            f"{(st.shape[0], len_traj - start_step, R.STATE_DIM)}")
        full = st.clone()
        full[:, start_step:] = pred_future
        return full

    out = {"n_trajectories": int(n_traj), "len_trajectory": int(len_traj),
           "start_step": int(start_step), "forecast_steps": int(len_traj - start_step),
           "allow_boundary_cross": bool(cross),
           "n_trajectories_crossing_boundary": int(n_cross),
           "trajectory_start_rows": idx[:, 0].tolist(),
           "trajectory_episodes": sorted({int(e) for e in episode_id[idx].flatten()
                                          if e >= 0}),
           "seed": int(seed)}

    clean = metric_block(run(state, action), state, start_step)
    out["clean"] = clean

    # ---- noise sweep, matching model_training.py:221-227 exactly ----------
    # 1. noise on BOTH state and action
    # 2. in NORMALISED space (normalize() is applied at model_training.py:200,
    #    before this loop; actions are normalised by an identity transform)
    # 3. drawn ONCE over the whole (B, 400, D) tensor before the rollout, not
    #    resampled per rollout step
    # 4. the noised error divides by the NOISED trajectory (line 227)
    out["noise"] = {}
    for ns in noise_scales:
        g = torch.Generator().manual_seed(seed * 100003 + int(round(ns * 1000)))
        st_n = state + torch.randn(state.shape, generator=g) * ns
        ac_n = action + torch.randn(action.shape, generator=g) * ns
        out["noise"][str(ns)] = metric_block(run(st_n, ac_n), st_n, start_step)
    return out


# --------------------------------------------------------------------------
# reference predictors
# --------------------------------------------------------------------------
def oracle_predictor(true_states, start_step=START_STEP):
    """Acceptance test 1. Closes over the true states of the sampled trajectories."""
    def fn(hs, ha, fa):
        return true_states[:, start_step:].clone()
    return fn


def noisy_oracle_predictor(true_states, sigma, seed, start_step=START_STEP):
    """Acceptance test 3."""
    def fn(hs, ha, fa):
        g = torch.Generator().manual_seed(seed)
        t = true_states[:, start_step:]
        return t + torch.randn(t.shape, generator=g) * sigma
    return fn


def hold_last_predictor():
    """
    Acceptance test 2 -- THE FLOOR. Repeats the last observed state for all
    forecast steps. Any model that does not clearly beat this has learned nothing.
    """
    def fn(hs, ha, fa):
        return hs[:, -1:].expand(-1, fa.shape[1], -1).clone()
    return fn


# --------------------------------------------------------------------------
# acceptance tests
# --------------------------------------------------------------------------
def run_acceptance_tests(data, episode_id, split, base_cfg):
    print("\n" + "=" * 78)
    print("STEP 2 ACCEPTANCE TESTS")
    print("=" * 78)
    results = {}

    idx = sample_trajectories(episode_id, split["holdout_episodes"],
                              seed=base_cfg["seed"])
    raw = data[idx]
    true_states = torch.as_tensor(
        R.normalise_state(raw[:, :, R.STATE_COLS], base_cfg["state_data_mean"],
                          base_cfg["state_data_std"]), dtype=torch.float32)

    # ---- 1 oracle -------------------------------------------------------
    r1 = evaluate(oracle_predictor(true_states), data, split,
                  {**base_cfg, "episode_id": episode_id, "noise_scales": []})
    ok1 = r1["clean"]["e"] == 0.0
    print(f"\n  [1] oracle predictor          e = {r1['clean']['e']:.17g}")
    print(f"      required exactly 0 to float tolerance -> {'PASS' if ok1 else 'FAIL'}")
    results["test1_oracle"] = {"e": r1["clean"]["e"], "pass": bool(ok1)}

    # ---- 2 hold-last : THE FLOOR ---------------------------------------
    r2 = evaluate(hold_last_predictor(), data, split,
                  {**base_cfg, "episode_id": episode_id, "noise_scales": []})
    c2 = r2["clean"]
    ok2 = np.isfinite(c2["e"])
    print(f"\n  [2] hold-last predictor  <-- THE FLOOR")
    print(f"      e            = {c2['e']:.4f}")
    print(f"      median r_t   = {c2['median_r']:.4f}")
    print(f"      frac r_t>10  = {c2['frac_r_gt_10']:.4f}")
    print(f"      finite -> {'PASS' if ok2 else 'FAIL'}")
    results["test2_hold_last"] = {k: c2[k] for k in
                                  ("e", "median_r", "frac_r_gt_10", "max_r")}
    results["test2_hold_last"]["pass"] = bool(ok2)

    # ---- 3 oracle + noise ----------------------------------------------
    print(f"\n  [3] oracle + Gaussian noise at 3 magnitudes")
    sigmas = [0.01, 0.05, 0.25]
    es = []
    for s in sigmas:
        r = evaluate(noisy_oracle_predictor(true_states, s, seed=1234), data, split,
                     {**base_cfg, "episode_id": episode_id, "noise_scales": []})
        es.append(r["clean"]["e"])
        print(f"      sigma {s:<5} -> e = {r['clean']['e']:.6f}")
    mono = all(es[i] < es[i + 1] for i in range(len(es) - 1))
    ratios = [es[i + 1] / es[i] for i in range(len(es) - 1)]
    sig_ratios = [sigmas[i + 1] / sigmas[i] for i in range(len(sigmas) - 1)]
    prop = all(abs(r / sr - 1.0) < 0.15 for r, sr in zip(ratios, sig_ratios))
    print(f"      e ratios {[f'{r:.2f}' for r in ratios]} vs sigma ratios"
          f" {[f'{r:.2f}' for r in sig_ratios]}")
    print(f"      monotonic {mono}, roughly proportional {prop}"
          f" -> {'PASS' if (mono and prop) else 'FAIL'}")
    results["test3_noise_monotonic"] = {"sigmas": sigmas, "e": es,
                                        "monotonic": bool(mono),
                                        "proportional": bool(prop),
                                        "pass": bool(mono and prop)}

    # ---- 4 trajectories inside one episode ------------------------------
    ok4 = assert_within_episode(idx, episode_id)
    eps_touched = sorted({int(e) for e in episode_id[idx].flatten()})
    print(f"\n  [4] every eval trajectory inside a single episode")
    print(f"      episodes touched: {eps_touched}  (held-out = {split['holdout_episodes']})")
    assert set(eps_touched).issubset(set(split["holdout_episodes"])), \
        "eval trajectories touch a training episode"
    print(f"      -> {'PASS' if ok4 else 'FAIL'}")
    results["test4_within_episode"] = {"episodes_touched": eps_touched, "pass": bool(ok4)}

    # ---- 5 no row overlap with training windows -------------------------
    train_rows = training_window_rows(episode_id, split)
    eval_rows = set(idx.flatten().tolist())
    overlap = train_rows & eval_rows
    ok5 = len(overlap) == 0
    print(f"\n  [5] no eval row appears in any training window")
    print(f"      rows in training windows {len(train_rows)}, rows in eval "
          f"trajectories {len(eval_rows)}, overlap {len(overlap)}")
    print(f"      -> {'PASS' if ok5 else 'FAIL'}")
    results["test5_no_leakage"] = {"n_train_rows": len(train_rows),
                                   "n_eval_rows": len(eval_rows),
                                   "overlap": len(overlap), "pass": bool(ok5)}

    # ---- 6 determinism ---------------------------------------------------
    cfg6 = {**base_cfg, "episode_id": episode_id, "noise_scales": [0.2, 0.5]}
    a = evaluate(hold_last_predictor(), data, split, cfg6)
    b = evaluate(hold_last_predictor(), data, split, cfg6)
    ok6 = _identical(a, b)
    print(f"\n  [6] re-run with the same seed is byte-identical")
    print(f"      compared clean + 2 noise conditions, scalars and per-step curves")
    print(f"      -> {'PASS' if ok6 else 'FAIL'}")
    results["test6_determinism"] = {"pass": bool(ok6)}

    allp = all(v.get("pass", False) for v in results.values())
    print("\n" + "-" * 78)
    for k, v in results.items():
        print(f"  {'PASS' if v.get('pass') else 'FAIL'}  {k}")
    print(f"\n  HOLD-LAST FLOOR: e = {results['test2_hold_last']['e']:.4f}"
          f"   (median r_t = {results['test2_hold_last']['median_r']:.4f})")
    print(f"  ALL ACCEPTANCE TESTS {'PASS' if allp else 'FAIL'}")
    results["all_pass"] = bool(allp)
    return results


def _identical(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(_identical(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(_identical(x, y) for x, y in zip(a, b))
    if isinstance(a, np.ndarray):
        return a.shape == b.shape and np.array_equal(a, b)
    return a == b


# --------------------------------------------------------------------------
def build_base_config(cfg, seed=0):
    return {
        "seed": seed,
        "state_data_mean": cfg["state_data_mean"],
        "state_data_std": cfg["state_data_std"],
        "action_data_mean": cfg["action_data_mean"],
        "action_data_std": cfg["action_data_std"],
        "start_step": START_STEP,
        "n_traj": N_TRAJ,
        "len_traj": LEN_TRAJ,
        "noise_scales": cfg["eval_traj_noise_scale"],
    }


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    paths = R.repo_paths()
    print("=" * 78)
    print("STEP 2 -- EVALUATION HARNESS")
    print("=" * 78)

    cfg = R.load_reference_config(paths["lite"])
    print("\n  reference constants, imported from the config (never retyped):")
    print(f"    history_horizon        {cfg['history_horizon']}")
    print(f"    forecast_horizon       {cfg['forecast_horizon']}")
    print(f"    num_eval_trajectories  {cfg['num_eval_trajectories']}")
    print(f"    len_eval_trajectory    {cfg['len_eval_trajectory']}")
    print(f"    eval_traj_noise_scale  {cfg['eval_traj_noise_scale']}")
    print(f"    ensemble_size          {cfg['ensemble_size']}")
    print(f"    start_step             {START_STEP}  "
          f"(model_training.py:201 sets it to history_horizon)")
    print(f"    actions normalised?    {cfg['actions_are_normalised']}"
          f"   (action_data_mean all-zero, action_data_std all-one)")
    print(f"    state_data_mean[:6]    {cfg['state_data_mean'][:6]}")
    print(f"    state_data_std[:6]     {cfg['state_data_std'][:6]}")

    print()
    data, episode_id = R.load_data(paths["csv"])

    print("\n  " + "-" * 74)
    split = make_split(seed=0, strat_path=os.path.join(here, "step0_strat.json"))

    n_train_windows = sum(1 for s in R.valid_window_starts(episode_id, 40)
                          if episode_id[s] in split["train_episodes"])
    print(f"  training windows (40-step, inside training episodes only): {n_train_windows}")

    base_cfg = build_base_config(cfg, seed=0)
    results = run_acceptance_tests(data, episode_id, split, base_cfg)

    with open(os.path.join(here, "step2_acceptance.json"), "w") as f:
        json.dump({"split": split, "tests": results,
                   "n_train_windows": int(n_train_windows)}, f, indent=2)
    return results


if __name__ == "__main__":
    main()
