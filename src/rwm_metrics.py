"""
Step 4 / 0b -- a second metric with a fixed denominator.

The reference relative-L1 metric divides by sum_d |true[t,d]| at each timestep.
M-09 showed what that costs: `inf` on base angular velocity from h>=8, and an
11.4% blow-up rate on projected gravity at h=368, because a 3-dim denominator
in normalised space passes through zero.

Normalised RMSE fixes the denominator once, over the TRAINING episodes:

    nrmse[d] = RMSE(pred[..., d], true[..., d]) / scale[d]
    scale[d] = std of normalised dimension d over training-episode rows

`scale` is a constant stored in results/step4_0a_results.json under `nrmse_scale`
(it is NOT in results/manifest.json, which this line used to claim), never recomputed per timestep and
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


# --------------------------------------------------------------------------
# Task 3 -- effective sample size and the pooled (form 1) aggregation
# --------------------------------------------------------------------------
def n_independent(start_rows, len_traj):
    """
    Number of mutually non-overlapping trajectories among the given starts.

    Two 400-step trajectories whose spans touch at all count as one sample. Greedy
    left-to-right selection on sorted starts gives the maximum such set for
    intervals of equal length. Reported alongside n_trajectories everywhere,
    because a long-horizon figure built on 100 overlapping windows drawn from two
    episodes has an effective sample size far below 100.
    """
    import numpy as _np
    s = _np.sort(_np.asarray(start_rows))
    if len(s) == 0:
        return 0
    kept, last = 1, s[0]
    for r in s[1:]:
        if r - last >= len_traj:
            kept += 1
            last = r
    return kept


def non_overlapping_starts(episode_id, episodes, len_traj):
    """Maximal set of non-overlapping trajectory starts inside the given episodes."""
    import numpy as _np
    out = []
    for e in episodes:
        idx = _np.flatnonzero(episode_id == e)
        if len(idx) == 0:
            continue
        c, last = idx[0], idx[-1]
        while c + len_traj - 1 <= last:
            out.append(int(c))
            c += len_traj
    return out


def nrmse_pooled(sq_err, scale, keep=None):
    """
    FORM 1, the primary aggregation from Task 3d onward.

        sqrt( mean over dims of MSE_d ) / mean over dims of scale_d

    Pools before dividing, so a single near-constant dimension cannot dominate.
    Form 2 -- mean over dims of RMSE_d/scale_d -- is a mean of ratios and gives
    whichever dimension has the smallest scale unbounded leverage (M-19, R-29).

    sq_err: (n_traj, T', 45) squared error. keep: optional dimension subset.
    """
    import numpy as _np
    mse = sq_err.mean(axis=0)
    if keep is not None:
        mse, sc = mse[:, keep], _np.asarray(scale)[keep]
    else:
        sc = _np.asarray(scale)
    return float((_np.sqrt(mse.mean(axis=1)) / sc.mean()).mean())


def nrmse_form2(sq_err, scale, keep=None):
    """FORM 2, retained for continuity with everything reported before M-19."""
    import numpy as _np
    mse = sq_err.mean(axis=0)
    if keep is not None:
        mse, sc = mse[:, keep], _np.asarray(scale)[keep]
    else:
        sc = _np.asarray(scale)
    return float((_np.sqrt(mse) / sc).mean())
