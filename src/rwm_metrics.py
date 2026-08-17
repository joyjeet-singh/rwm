"""
Step 4 / 0b -- a second metric with a fixed denominator.

The reference relative-L1 metric divides by sum_d |true[t,d]| at each timestep.
M-09 showed what that costs: `inf` on base angular velocity from h>=8, and an
11.4% blow-up rate on projected gravity at h=368, because a 3-dim denominator
in normalised space passes through zero.

Normalised RMSE fixes the denominator once, over the TRAINING episodes:

    nrmse[d] = RMSE(pred[..., d], true[..., d]) / scale[d]
    scale[d] = std of normalised dimension d over training-episode rows

`scale` is a constant stored in the manifest, never recomputed per timestep and
never derived from held-out data. So it cannot approach zero, and the reading is
clean: 1.0 means "no better than predicting the training mean", below 1.0 means
the model carries information about that dimension.

Both metrics are reported everywhere from here on. Relative-L1 exists to compare
against the paper; nRMSE exists to reason with.
"""

import numpy as np
import torch

import rwm_data as R


def training_scale(data, episode_id, train_episodes, state_mean, state_std):
    """
    scale[d] = std of normalised state dim d over training-episode rows only.

    Computed once and stored. Uses the config normalisation first so the metric
    lives in the same space as the model's predictions.
    """
    rows = np.isin(episode_id, list(train_episodes)) & (episode_id >= 0)
    norm = R.normalise_state(data[rows][:, R.STATE_COLS], state_mean, state_std)
    scale = norm.std(axis=0)
    assert scale.shape == (R.STATE_DIM,)
    assert np.all(scale > 0), "a state dimension is constant over the training episodes"
    return scale


def nrmse_per_step(pred, true, scale, start_step):
    """
    Returns (per_step_overall, per_step_per_dim).
      per_step_overall  (T-start,)      mean over dims of the per-dim nRMSE
      per_step_per_dim  (T-start, 45)
    RMSE is taken across trajectories at each forecast step.
    """
    sc = torch.as_tensor(scale, dtype=pred.dtype)
    err = pred[:, start_step:] - true[:, start_step:]          # (B, T', 45)
    rmse = torch.sqrt((err ** 2).mean(dim=0))                  # (T', 45)
    per_dim = rmse / sc
    return per_dim.mean(dim=-1).numpy(), per_dim.numpy()


def nrmse_groups(pred, true, scale, start_step):
    """Per-state-group nRMSE curves, averaged over each group's dimensions."""
    _, per_dim = nrmse_per_step(pred, true, scale, start_step)
    out = {}
    for name, cols in (("base lin vel", R.LIN_VEL), ("base ang vel", R.ANG_VEL),
                       ("proj gravity", R.GRAVITY), ("joint pos", R.JOINT_POS),
                       ("joint vel", R.JOINT_VEL), ("joint torque", R.JOINT_TAU)):
        out[name] = per_dim[:, list(cols)].mean(axis=1)
    return out


def summarise(curve, horizons=(1, 8, 32, 128, 368)):
    """Cumulative mean of a per-step curve at each horizon."""
    return {h: float(curve[:h].mean()) for h in horizons if h <= len(curve)}
