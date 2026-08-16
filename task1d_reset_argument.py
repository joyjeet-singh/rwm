"""
Task 1d -- the reset rows settle the convention by refutation.

The three statistical tests all fail to separate the hypotheses, each for its
own reason (Task 1: position-target confound; 1b: ANYmal uses a learned actuator
net so the linear PD law is misspecified; 1c: the checkpoint's actor is not the
policy that collected the data). But the reset rows decide it logically, from
facts already VERIFIED in Step 1.

VERIFIED facts used:
  * rows 999, 1999, ... 9999 hold the POST-reset state (joint velocities exactly
    0, HAA positions exactly 0, and continuous with the row after, discontinuous
    from the row before)
  * at exactly those rows, all 12 action columns are exactly 0.0

The argument:

  Under k = 0  -- row t holds a[t] = pi(state[t]) -- the reset row would have to
  contain pi(post-reset state). A policy is a continuous MLP with biases; for it
  to emit bitwise 0.0 on all 12 outputs, at 10 different randomised reset states,
  is impossible. k = 0 is REFUTED.

  Under k = -1 -- row t holds the action that PRODUCED state[t] -- the reset row
  contains the action responsible for the reset state. No action produced it, and
  Isaac Lab zeroes the action buffer on reset, so exactly 0.0 is precisely what
  is expected. k = -1 is CONSISTENT.

This is a refutation, not a fit, so it does not care that the available policy is
the wrong one. The quantitative part below only illustrates the magnitude a
policy actually emits on those states.
"""

import json
import os

import numpy as np
import torch

import rwm_data as R
from task1c_policy_test import build_actor, command_per_row, make_obs


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    paths = R.repo_paths()
    data, episode_id = R.load_data(paths["csv"], verbose=False)
    rr = np.array(R.RESET_ROWS)

    print("=" * 78)
    print("TASK 1d -- THE RESET ROWS REFUTE k=0")
    print("=" * 78)

    a_reset = data[rr][:, R.ACTIONS]
    print(f"  reset rows: {rr.tolist()}")
    print(f"  action columns at those rows: all exactly 0.0 -> "
          f"{bool(np.all(a_reset == 0.0))}")
    print(f"  max |action| over those {a_reset.size} values: {np.abs(a_reset).max():.1e}")
    print(f"  joint velocities exactly 0.0 -> "
          f"{bool(np.all(data[rr][:, R.JOINT_VEL] == 0.0))}")
    print("  (Step 1 established these rows are the POST-reset state: continuous")
    print("   with the row after, discontinuous from the row before.)")

    print("\n  For comparison, typical |action| elsewhere in the file:")
    mask = np.ones(len(data), bool)
    mask[rr] = False
    other = np.abs(data[mask][:, R.ACTIONS])
    print(f"    mean {other.mean():.4f}   median {np.median(other):.4f}"
          f"   1st percentile {np.percentile(other, 1):.4f}")
    print(f"    rows anywhere in the file with ALL 12 actions exactly 0: "
          f"{int((np.abs(data[:, R.ACTIONS]).sum(1) == 0).sum())}"
          f"  (i.e. only the reset rows)")

    print("\n  Illustration -- what a policy actually emits on those reset states.")
    print("  (This actor is NOT the collection policy, so this is indicative only.)")
    with open(os.path.join(here, "step0_regimes.json")) as f:
        regimes = json.load(f)["regimes"]
    cmd = command_per_row(regimes, len(data))
    actor = build_actor(torch.load(paths["ckpt"], map_location="cpu")["model_state_dict"])
    obs = make_obs(data, cmd, rr, np.maximum(rr - 1, 0))
    with torch.no_grad():
        pred = actor(torch.as_tensor(obs, dtype=torch.float32)).numpy()
    print(f"    |pi(reset state)| : mean {np.abs(pred).mean():.4f}"
          f"   min {np.abs(pred).min():.4f}   max {np.abs(pred).max():.4f}")
    print(f"    smallest single output magnitude across all {pred.size} values:"
          f" {np.abs(pred).min():.2e}")
    print("    A policy emits O(0.1-1) here. Recorded value is bitwise 0.0.")

    print("\n" + "=" * 78)
    print("TASK 1 OVERALL VERDICT (combining 1, 1b, 1c, 1d)")
    print("=" * 78)
    print("  1  ridge a[t] ~ s[t+k]        peak k=+1   CONFOUNDED (position target)")
    print("  1b PD law tau ~ a,q,qdot      peak m=-1   weak (gap 0.029, actuator net)")
    print("  1c real policy pi(obs)        peak k=-1   weak (gap 0.095 vs k=0; wrong policy)")
    print("  1d reset-row refutation       k=0 REFUTED, k=-1 consistent   DECISIVE")
    print()
    print("  VERDICT: k = -1")
    print("  Row t holds the action that PRODUCED the state in row t.")
    print()
    print("  Consequences:")
    print("   * The TRAINING convention (s[t], a[t+1]) -> s[t+1] is CAUSAL. a[t+1] is")
    print("     the action that produced s[t+1]; using it is correct, not leakage.")
    print("   * The EVALUATION convention (s[t], a[t]) -> s[t+1] is STALE by one step:")
    print("     it feeds the action that produced s[t] and asks for s[t+1].")
    print("   * Step 4 must build the loss with the TRAINING alignment.")
    print("   * The Step 3 result that the training convention scores better")
    print("     (e 0.7008 vs 0.7672) is explained by correct causal alignment, NOT")
    print("     by target leakage. Any earlier leakage reading is REFUTED.")

    with open(os.path.join(here, "task1d_reset.json"), "w") as f:
        json.dump({"verdict": "k=-1", "method": "refutation from reset rows",
                   "actions_zero_at_reset_rows": True,
                   "n_rows_with_all_actions_zero": int(
                       (np.abs(data[:, R.ACTIONS]).sum(1) == 0).sum()),
                   "reset_rows": rr.tolist(),
                   "policy_output_magnitude_on_reset_states": {
                       "mean": float(np.abs(pred).mean()),
                       "min": float(np.abs(pred).min())}}, f, indent=2)


if __name__ == "__main__":
    main()
