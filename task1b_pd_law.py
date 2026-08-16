"""
Task 1b -- a confound-free test of the action convention, using the PD law.

Why Task 1's regression cannot settle the question. It regresses a_row[t] on
s[t+k] and finds the peak at k=+1, which is NEITHER hypothesis. The reason is
that the action is a JOINT POSITION TARGET, not an abstract control symbol: the
joints move toward it, so the action necessarily resembles FUTURE joint states.
Step 1 measured exactly this -- action leads joint position by ~4 steps, peak
r = 0.74-0.85. Twelve of the 45 regressors are joint positions, so "action
looks like where the joints are heading" dominates "action is a function of the
observation the policy saw", and the apparent peak is pushed to positive k for
reasons that have nothing to do with the recording convention.

The clean test. Isaac Lab's position actuator applies

    tau = Kp * (q_desired - q) - Kd * qdot,     q_desired = default + scale * action

which is EXACT, LINEAR, and PER-JOINT. So for joint j, tau_j at a given instant
is a linear function of exactly three recorded quantities at that same instant:
the action, the joint position, and the joint velocity.

Fit, per joint, for each action offset m:

    tau_row[t, j]  ~  c0 + c1 * a_row[t+m, j] + c2 * q_row[t, j] + c3 * qdot_row[t, j]

q and qdot are held at row t -- the same row as the torque -- so the only thing
varying is which row's action was in force when that torque was produced. The
smoothness confound cannot operate here, because the fit is conditioned on the
joint state at the same instant. The offset that recovers the PD law is the
offset at which the action and the torque belong to the same control step.

Recovering c1/c2 = -scale also gives the action scale, which is not recorded
anywhere in either repository.
"""

import json
import os

import numpy as np

import rwm_data as R
import rollout_eval as E

OFFSETS = [-2, -1, 0, 1, 2]
LEGS = ["LF", "LH", "RF", "RH"]
JOINTS = [f"{leg}_{j}" for j in ("HAA", "HFE", "KFE") for leg in LEGS]


def fit_pd(data, episode_id, m, episodes, joints=range(12)):
    """Per-joint OLS of tau[t] on (a[t+m], q[t], qdot[t]). Returns R2 and coeffs."""
    n = len(data)
    t = np.arange(n)
    ok = np.isin(episode_id, list(episodes)) & (episode_id >= 0)
    tm = t + m
    ok &= (tm >= 0) & (tm < n)
    ok &= episode_id[np.clip(tm, 0, n - 1)] == episode_id
    t = t[ok]

    r2s, coefs = [], []
    for j in joints:
        a = data[t + m, R.ACTIONS[j]]
        q = data[t, R.JOINT_POS[j]]
        qd = data[t, R.JOINT_VEL[j]]
        y = data[t, R.JOINT_TAU[j]]
        X = np.column_stack([np.ones_like(a), a, q, qd])
        c, *_ = np.linalg.lstsq(X, y, rcond=None)
        pred = X @ c
        ss_res = ((y - pred) ** 2).sum()
        ss_tot = ((y - y.mean()) ** 2).sum()
        r2s.append(1.0 - ss_res / ss_tot)
        coefs.append(c)
    return np.array(r2s), np.array(coefs), len(t)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    paths = R.repo_paths()
    data, episode_id = R.load_data(paths["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(here, "step0_strat.json"),
                         verbose=False)
    test_eps = split["holdout_episodes"]

    print("=" * 78)
    print("TASK 1b -- CONFOUND-FREE CONVENTION TEST VIA THE PD LAW")
    print("=" * 78)
    print("  Task 1's regression is confounded: the action is a joint POSITION TARGET,")
    print("  so it resembles future joint states regardless of recording convention.")
    print("  Step 1 measured action leading joint position by ~4 steps. That, not the")
    print("  convention, is why Task 1 peaked at k=+1.")
    print()
    print("  This fit conditions on q[t] and qdot[t] from the SAME row as tau[t] and")
    print("  varies only the action offset, so smoothness cannot drive the result.")
    print(f"\n  scored on held-out episodes {test_eps}")
    print("\n  tau_row[t,j] ~ c0 + c1*a_row[t+m,j] + c2*q_row[t,j] + c3*qdot_row[t,j]\n")

    res = {}
    print(f"  {'offset m':>9s} {'mean R2':>10s} {'min R2':>9s} {'max R2':>9s}"
          f" {'implied scale':>14s} {'n':>7s}")
    for m in OFFSETS:
        r2, c, n = fit_pd(data, episode_id, m, test_eps)
        scale = -(c[:, 1] / c[:, 2])          # c1/c2 = -scale
        res[m] = {"mean_r2": float(r2.mean()), "per_joint_r2": r2.tolist(),
                  "implied_scale": scale.tolist(), "n": int(n)}
        print(f"  {m:>9d} {r2.mean():>10.6f} {r2.min():>9.6f} {r2.max():>9.6f}"
              f" {np.median(scale):>14.4f} {n:>7d}")

    order = sorted(OFFSETS, key=lambda m: -res[m]["mean_r2"])
    peak, second = order[0], order[1]
    gap = res[peak]["mean_r2"] - res[second]["mean_r2"]
    print(f"\n    peak   m = {peak:+d}   mean R2 = {res[peak]['mean_r2']:.6f}")
    print(f"    second m = {second:+d}   mean R2 = {res[second]['mean_r2']:.6f}")
    print(f"    gap = {gap:.6f}")

    print(f"\n  per-joint R2 at each offset")
    print(f"  {'joint':<9s}" + "".join(f"{f'm={m:+d}':>11s}" for m in OFFSETS))
    for j in range(12):
        print(f"  {JOINTS[j]:<9s}" +
              "".join(f"{res[m]['per_joint_r2'][j]:>11.6f}" for m in OFFSETS))

    print(f"\n  implied action scale at m = {peak:+d}  (from -c1/c2, per joint)")
    sc = np.array(res[peak]["implied_scale"])
    for j in range(12):
        print(f"    {JOINTS[j]:<9s} {sc[j]:.4f}")
    print(f"    median {np.median(sc):.4f}   mean {sc.mean():.4f}   std {sc.std():.4f}")

    # ------------------------------------------------------------- verdict
    print("\n" + "=" * 78)
    print("TASK 1b VERDICT")
    print("=" * 78)
    strong = res[peak]["mean_r2"] > 0.95 and gap > 0.05
    print(f"  peak at m = {peak:+d}, mean R2 = {res[peak]['mean_r2']:.6f}, "
          f"gap to second = {gap:.6f}")
    if not strong:
        verdict = "inconclusive"
        print("  The PD law is not recovered sharply enough at any offset to call it.")
    elif peak == 0:
        verdict = "k=0"
        print("  The PD law closes with the action in the SAME row as the torque.")
        print("  -> Row t holds the action applied at t, i.e. a[t].")
        print("  -> The EVALUATION convention (s[t], a[t]) -> s[t+1] is causal.")
        print("  -> The TRAINING convention (s[t], a[t+1]) -> s[t+1] LEAKS THE TARGET.")
        print("     Step 4 must build the loss with the eval alignment.")
    elif peak == -1:
        verdict = "k=-1"
        print("  The PD law closes with the action one row LATER than the torque.")
        print("  -> Row t holds a[t-1]; the TRAINING convention is causal.")
    else:
        verdict = f"m={peak:+d}"
        print("  Peak at an offset neither hypothesis predicts. Report as anomalous.")

    with open(os.path.join(here, "task1b_pd_law.json"), "w") as f:
        json.dump({"verdict": verdict, "peak": peak, "second": second, "gap": gap,
                   "by_offset": {str(m): res[m] for m in res},
                   "implied_action_scale_median": float(np.median(sc)),
                   "test_episodes": test_eps}, f, indent=2)
    return verdict


if __name__ == "__main__":
    main()
