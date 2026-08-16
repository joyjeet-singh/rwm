"""
Task 1c -- settle the action convention with the actual policy.

The checkpoint's `model_state_dict` is the actor/critic the Step 2/3 brief told
us to ignore. It is the decisive instrument here: instead of asking a linear
surrogate which state best explains the action, we can run the real policy and
ask which state, fed as its observation, REPRODUCES the recorded action.

The observation layout is not guessed. anymal_d_flat.py:53 builds it as

    cat([base_lin_vel(3), base_ang_vel(3), projected_gravity(3),
         base_velocity(3)=command, joint_pos(12), joint_vel(12),
         last_action(12)])                                        = 48

in raw (denormalised) units, and base_cfg.py:118-120 gives actor_hidden_dims
[128,128,128] with elu -- matching the actor tensors 48->128->128->128->12.

The two hypotheses differ ONLY in which row supplies the state block; both use
A[t-1] in the last-action slot:

    k =  0  (row t holds a[t]):     A[t] = pi(state[t],   ..., A[t-1])
    k = -1  (row t holds a[t-1]):   A[t] = pi(state[t-1], ..., A[t-1])

The command is not recorded. It is taken per-regime from the Step 0 segmentation
(a well-tracking policy achieves close to its command). Any error there is a
constant per-regime offset that hits both hypotheses equally, so the comparison
stays fair.

Caveat checked below: this actor may be a policy trained later in imagination
rather than the one that collected the CSV. If neither hypothesis reproduces the
actions, that is the explanation and the test returns inconclusive.
"""

import json
import os

import numpy as np
import torch
import torch.nn as nn

import rwm_data as R
import rollout_eval as E


def build_actor(sd):
    """48 -> 128 -> 128 -> 128 -> 12, elu between (base_cfg.py:118-120)."""
    net = nn.Sequential(
        nn.Linear(48, 128), nn.ELU(),
        nn.Linear(128, 128), nn.ELU(),
        nn.Linear(128, 128), nn.ELU(),
        nn.Linear(128, 12))
    with torch.no_grad():
        for i in (0, 2, 4, 6):
            net[i].weight.copy_(sd[f"actor.{i}.weight"])
            net[i].bias.copy_(sd[f"actor.{i}.bias"])
    net.eval()
    return net


def command_per_row(regimes, n):
    """Per-row (vx, vy, wz) command, taken as the Step 0 regime mean."""
    cmd = np.zeros((n, 3))
    for r in regimes:
        cmd[r["start"]:r["end"] + 1] = [r["vx"], r["vy"], r["wz"]]
    return cmd


def make_obs(data, cmd, state_rows, last_action_rows):
    return np.hstack([
        data[state_rows][:, R.LIN_VEL],
        data[state_rows][:, R.ANG_VEL],
        data[state_rows][:, R.GRAVITY],
        cmd[state_rows],
        data[state_rows][:, R.JOINT_POS],
        data[state_rows][:, R.JOINT_VEL],
        data[last_action_rows][:, R.ACTIONS],
    ])


def score(pred, true):
    ss_res = ((true - pred) ** 2).sum(0)
    ss_tot = ((true - true.mean(0)) ** 2).sum(0)
    r2 = 1.0 - ss_res / ss_tot
    return {"mean_r2": float(r2.mean()), "per_dim_r2": r2.tolist(),
            "mae": float(np.abs(true - pred).mean()),
            "rmse": float(np.sqrt(((true - pred) ** 2).mean()))}


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    paths = R.repo_paths()
    data, episode_id = R.load_data(paths["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(here, "step0_strat.json"),
                         verbose=False)
    test_eps = split["holdout_episodes"]

    with open(os.path.join(here, "step0_regimes.json")) as f:
        regimes = json.load(f)["regimes"]
    cmd = command_per_row(regimes, len(data))

    ck = torch.load(paths["ckpt"], map_location="cpu")
    actor = build_actor(ck["model_state_dict"])

    print("=" * 78)
    print("TASK 1c -- CONVENTION TEST USING THE ACTUAL POLICY")
    print("=" * 78)
    print("  observation layout from anymal_d_flat.py:53 (raw units, 48 dims)")
    print("  actor 48->128->128->128->12, elu (base_cfg.py:118-120)")
    print(f"  scored on held-out episodes {test_eps}")
    print("  commands taken per-regime from the Step 0 segmentation\n")

    n = len(data)
    t = np.arange(n)
    ok = np.isin(episode_id, test_eps) & (episode_id >= 0)
    ok &= t - 1 >= 0
    ok &= episode_id[np.clip(t - 1, 0, n - 1)] == episode_id
    t = t[ok]
    true_a = data[t][:, R.ACTIONS]

    res = {}
    print(f"  {'hypothesis':<44s} {'mean R2':>9s} {'MAE':>9s} {'RMSE':>9s}")
    for k, name in ((0, "k= 0  state[t]   -> A[t]   (eval conv. causal)"),
                    (-1, "k=-1  state[t-1] -> A[t]   (train conv. causal)")):
        obs = make_obs(data, cmd, t + k, t - 1)
        with torch.no_grad():
            pred = actor(torch.as_tensor(obs, dtype=torch.float32)).numpy()
        s = score(pred, true_a)
        res[k] = s
        print(f"  {name:<44s} {s['mean_r2']:>9.4f} {s['mae']:>9.4f} {s['rmse']:>9.4f}")

    # control offsets, to show the profile is peaked and not monotone
    print("\n  control offsets (same construction, other state rows):")
    for k in (-3, -2, 1, 2):
        obs = make_obs(data, cmd, np.clip(t + k, 0, n - 1), t - 1)
        with torch.no_grad():
            pred = actor(torch.as_tensor(obs, dtype=torch.float32)).numpy()
        s = score(pred, true_a)
        res[k] = s
        print(f"    k={k:+d}  mean R2 {s['mean_r2']:>8.4f}   MAE {s['mae']:.4f}")

    best = max(res, key=lambda k: res[k]["mean_r2"])
    others = sorted((v["mean_r2"] for kk, v in res.items() if kk != best), reverse=True)
    gap = res[best]["mean_r2"] - others[0]

    print(f"\n  peak at k = {best:+d}   mean R2 = {res[best]['mean_r2']:.4f}")
    print(f"  second best mean R2 = {others[0]:.4f}   gap = {gap:.4f}")

    print("\n  per-dimension R2 at the peak:")
    LEGS = ["LF", "LH", "RF", "RH"]
    J = [f"{l}_{j}" for j in ("HAA", "HFE", "KFE") for l in LEGS]
    for j in range(12):
        print(f"    {J[j]:<9s} {res[best]['per_dim_r2'][j]:>8.4f}")

    print("\n" + "=" * 78)
    print("TASK 1c VERDICT")
    print("=" * 78)
    if res[best]["mean_r2"] < 0.5:
        verdict = "inconclusive"
        print(f"  The policy does not reproduce the recorded actions under ANY offset")
        print(f"  (best mean R2 = {res[best]['mean_r2']:.4f}). The actor in this")
        print("  checkpoint is therefore not the policy that collected the CSV -- it is")
        print("  the model-based policy trained afterwards in imagination. This test")
        print("  cannot settle the convention.")
    elif gap < 0.05:
        verdict = "inconclusive"
        print(f"  Offsets are not separated (gap {gap:.4f}).")
    elif best == 0:
        verdict = "k=0"
        print("  The policy reproduces A[t] from state[t]. Row t holds a[t].")
        print("  -> EVAL convention causal; TRAINING convention leaks the target.")
    elif best == -1:
        verdict = "k=-1"
        print("  The policy reproduces A[t] from state[t-1]. Row t holds a[t-1].")
        print("  -> TRAINING convention causal; eval convention is stale by one step.")
    else:
        verdict = f"k={best:+d}"
        print("  Peak at an offset neither hypothesis predicts.")
    print(f"\n  VERDICT: {verdict}")

    with open(os.path.join(here, "task1c_policy.json"), "w") as f:
        json.dump({"verdict": verdict, "peak": int(best), "gap": float(gap),
                   "by_offset": {str(k): res[k] for k in res},
                   "test_episodes": test_eps}, f, indent=2)
    return verdict


if __name__ == "__main__":
    main()
