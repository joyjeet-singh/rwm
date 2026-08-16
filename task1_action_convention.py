"""
Task 1 -- which action convention is causally correct.

The question is what row t's action columns hold: the action APPLIED at t
(computed from observation s[t]), or the action that PRODUCED s[t] (computed
from s[t-1]).

The test: the velocity-tracking policy is close to a deterministic function of
its observation, and 33 of the 45 state dims are also policy observations
(base lin vel, base ang vel, projected gravity, joint pos, joint vel). So
regress the recorded action a_row[t] on the state s[t+k] and see which offset
explains it best.

  peak at k =  0  ->  row t holds a[t]      -> the EVAL convention is causal
  peak at k = -1  ->  row t holds a[t-1]    -> the TRAINING convention is causal

NOT run here, deliberately: comparing which of (s[t],a[t]) or (s[t],a[t+1])
predicts s[t+1] better. Both hypotheses predict that a[t+1] wins -- under one
it is causal, under the other it leaks the target -- so that comparison carries
no information about this question. The Step 3 "action alignment check" was
exactly that comparison and is therefore not evidence for the convention.

What the state does NOT contain: the 3 velocity command dims and the 12
previous-action dims that the policy also sees (observation_dim = 48 =
45 state-ish + 3 command, with torques swapped for last-action). The command is
constant within a regime, so it acts as an unmodelled per-regime offset and
caps R². The optional robustness check adds a_row[t-1] as a regressor.
"""

import json
import os

import numpy as np

import rwm_data as R
import rollout_eval as E

OFFSETS = [-2, -1, 0, 1, 2]
ALPHAS = [1e-3, 1e-2, 1e-1, 1e0, 1e1, 1e2, 1e3, 1e4]
LEGS = ["LF", "LH", "RF", "RH"]
JOINTS = [f"{leg}_{j}" for j in ("HAA", "HFE", "KFE") for leg in LEGS]


def build_pairs(data, episode_id, k, episodes, cfg, with_prev_action=False):
    """
    Rows t (in `episodes`) such that t+k is in the same episode.
    X = normalised s[t+k]  (+ optionally raw a_row[t-1]),  y = raw a_row[t].
    """
    n = len(data)
    t = np.arange(n)
    ok = np.isin(episode_id, list(episodes)) & (episode_id >= 0)
    tk = t + k
    ok &= (tk >= 0) & (tk < n)
    tk_c = np.clip(tk, 0, n - 1)
    ok &= episode_id[tk_c] == episode_id            # same episode, drops crossings
    if with_prev_action:
        ok &= (t - 1 >= 0)
        tm1 = np.clip(t - 1, 0, n - 1)
        ok &= episode_id[tm1] == episode_id
    t = t[ok]
    X = R.normalise_state(data[t + k][:, R.STATE_COLS],
                          cfg["state_data_mean"], cfg["state_data_std"])
    if with_prev_action:
        X = np.hstack([X, data[t - 1][:, R.ACTION_COLS]])
    y = data[t][:, R.ACTION_COLS]
    return X, y


def ridge_fit(X, y, alpha):
    """Closed-form ridge with an unpenalised intercept."""
    xm, ym = X.mean(0), y.mean(0)
    Xc, yc = X - xm, y - ym
    G = Xc.T @ Xc + alpha * np.eye(X.shape[1])
    W = np.linalg.solve(G, Xc.T @ yc)
    return W, ym - xm @ W


def r2_per_dim(y, yhat):
    ss_res = ((y - yhat) ** 2).sum(0)
    ss_tot = ((y - y.mean(0)) ** 2).sum(0)
    return 1.0 - ss_res / ss_tot


def run(data, episode_id, cfg, train_eps, test_eps, with_prev_action=False):
    out = {}
    for k in OFFSETS:
        Xtr, ytr = build_pairs(data, episode_id, k, train_eps, cfg, with_prev_action)
        Xte, yte = build_pairs(data, episode_id, k, test_eps, cfg, with_prev_action)
        best = None
        by_alpha = {}
        for a in ALPHAS:
            W, b = ridge_fit(Xtr, ytr, a)
            r2 = r2_per_dim(yte, Xte @ W + b)
            by_alpha[a] = float(r2.mean())
            if best is None or r2.mean() > best["mean_r2"]:
                best = {"alpha": a, "mean_r2": float(r2.mean()),
                        "per_dim_r2": r2.tolist()}
        best["by_alpha"] = by_alpha
        best["n_train"], best["n_test"] = len(Xtr), len(Xte)
        best["alpha_spread"] = float(max(by_alpha.values()) - min(by_alpha.values()))
        out[k] = best
    return out


def report(res, title):
    print(f"\n  {title}")
    print(f"  {'offset k':>9s} {'best alpha':>11s} {'mean R2':>9s} "
          f"{'spread over alphas':>19s} {'n_test':>8s}")
    for k in OFFSETS:
        r = res[k]
        print(f"  {k:>9d} {r['alpha']:>11.0e} {r['mean_r2']:>9.4f} "
              f"{r['alpha_spread']:>19.4f} {r['n_test']:>8d}")
    order = sorted(OFFSETS, key=lambda k: -res[k]["mean_r2"])
    peak, second = order[0], order[1]
    gap = res[peak]["mean_r2"] - res[second]["mean_r2"]
    spread = max(res[k]["alpha_spread"] for k in OFFSETS)
    print(f"\n    peak      k = {peak:+d}   mean R2 = {res[peak]['mean_r2']:.4f}")
    print(f"    second    k = {second:+d}   mean R2 = {res[second]['mean_r2']:.4f}")
    print(f"    gap to second place        : {gap:.4f}")
    print(f"    largest spread over alphas : {spread:.4f}")
    conclusive = gap > spread
    print(f"    gap {'>' if conclusive else '<='} alpha-spread -> "
          f"{'CONCLUSIVE' if conclusive else 'INCONCLUSIVE'}")
    return peak, second, gap, spread, conclusive


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    data, episode_id = R.load_data(paths["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(here, "step0_strat.json"),
                         verbose=False)
    train_eps, test_eps = split["train_episodes"], split["holdout_episodes"]

    print("=" * 78)
    print("TASK 1 -- WHICH ACTION CONVENTION IS CAUSALLY CORRECT")
    print("=" * 78)
    print(f"  fit on training episodes {train_eps}")
    print(f"  scored on held-out episodes {test_eps}")
    print(f"  inputs normalised with the config constants; alphas {ALPHAS}")
    print("  pairs crossing an episode boundary are dropped")

    res = run(data, episode_id, cfg, train_eps, test_eps)
    peak, second, gap, spread, conclusive = report(
        res, "held-out R2, regressors = s[t+k] only")

    print("\n  per-dimension held-out R2 at the best alpha for each offset")
    print(f"  {'joint':<9s}" + "".join(f"{f'k={k:+d}':>9s}" for k in OFFSETS))
    for j in range(12):
        print(f"  {JOINTS[j]:<9s}" +
              "".join(f"{res[k]['per_dim_r2'][j]:>9.4f}" for k in OFFSETS))
    haa = [np.mean([res[k]["per_dim_r2"][j] for j in range(4)]) for k in OFFSETS]
    hfe = [np.mean([res[k]["per_dim_r2"][j] for j in range(4, 8)]) for k in OFFSETS]
    kfe = [np.mean([res[k]["per_dim_r2"][j] for j in range(8, 12)]) for k in OFFSETS]
    print(f"  {'HAA mean':<9s}" + "".join(f"{v:>9.4f}" for v in haa))
    print(f"  {'HFE mean':<9s}" + "".join(f"{v:>9.4f}" for v in hfe))
    print(f"  {'KFE mean':<9s}" + "".join(f"{v:>9.4f}" for v in kfe))
    for name, vals in (("HAA", haa), ("HFE", hfe), ("KFE", kfe)):
        pk = OFFSETS[int(np.argmax(vals))]
        print(f"    {name} group peaks at k = {pk:+d}")

    # ---------------------------------------------------- robustness check
    print("\n" + "-" * 78)
    print("  ROBUSTNESS: add the previous recorded action a_row[t-1] as a regressor")
    print("  (Isaac Lab's velocity-task policy observation includes the last action)")
    print("-" * 78)
    res2 = run(data, episode_id, cfg, train_eps, test_eps, with_prev_action=True)
    peak2, second2, gap2, spread2, conc2 = report(
        res2, "held-out R2, regressors = s[t+k] and a_row[t-1]")
    moved = peak2 != peak
    print(f"\n    peak {'MOVED' if moved else 'did NOT move'}: "
          f"k = {peak:+d} -> k = {peak2:+d}")
    if moved:
        print("    The test is WEAKENED: adding the previous action changes the answer.")
    else:
        print("    The test holds up: the peak is unchanged by adding the previous action.")

    # ---------------------------------------------------------- the verdict
    print("\n" + "=" * 78)
    print("TASK 1 VERDICT")
    print("=" * 78)
    if not conclusive or moved:
        verdict = "inconclusive"
    elif peak == 0:
        verdict = "k=0"
    elif peak == -1:
        verdict = "k=-1"
    else:
        verdict = f"k={peak:+d} (neither hypothesis)"
    print(f"  VERDICT: {verdict}")
    if verdict == "k=0":
        print("  Row t holds a[t], the action applied at t.")
        print("  -> The EVALUATION convention (s[t], a[t]) -> s[t+1] is causal.")
        print("  -> The TRAINING convention (s[t], a[t+1]) -> s[t+1] LEAKS THE TARGET:")
        print("     a[t+1] is the policy's response to s[t+1], the very state being")
        print("     predicted. Step 4 must build the loss with the eval alignment.")
    elif verdict == "k=-1":
        print("  Row t holds a[t-1], the action that produced s[t].")
        print("  -> The TRAINING convention is causal; the eval convention is stale.")
    else:
        print("  The offsets are not separated well enough to call it.")

    with open(os.path.join(here, "task1_action_convention.json"), "w") as f:
        json.dump({"verdict": verdict, "peak": peak, "second": second,
                   "gap": gap, "alpha_spread": spread, "conclusive": conclusive,
                   "peak_with_prev_action": peak2, "peak_moved": bool(moved),
                   "state_only": {str(k): res[k] for k in res},
                   "with_prev_action": {str(k): res2[k] for k in res2},
                   "train_episodes": train_eps, "test_episodes": test_eps}, f, indent=2)
    return verdict


if __name__ == "__main__":
    main()
