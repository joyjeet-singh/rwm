"""
Data layer for the RWM reproduction.

Everything downstream (window builder, split, trajectory sampler) reads the
`episode_id` array built here. Nothing downstream consults column 65 for episode
structure -- column 65 is identically zero in this file and does not mark the
resets.

Normalisation constants are imported from the reference config, never retyped.
"""

import hashlib
import importlib.util
import os
import sys

import numpy as np

# --------------------------------------------------------------------------
# column map (VERIFIED against the reference loader, see report)
# --------------------------------------------------------------------------
LIN_VEL = list(range(0, 3))
ANG_VEL = list(range(3, 6))
GRAVITY = list(range(6, 9))
JOINT_POS = list(range(9, 21))
JOINT_VEL = list(range(21, 33))
JOINT_TAU = list(range(33, 45))
ACTIONS = list(range(45, 57))
CONTACT_THIGH = list(range(57, 61))
CONTACT_FOOT = list(range(61, 65))
CONTACTS = CONTACT_THIGH + CONTACT_FOOT
TERMINATION = 65

STATE_COLS = list(range(0, 45))
ACTION_COLS = ACTIONS
STATE_DIM = 45
ACTION_DIM = 12
CONTACT_DIM = 8
TERMINATION_DIM = 1

HAA_COLS = JOINT_POS[0:4]          # the four HAA joint positions
DT = 0.02

# Episode structure, established structurally in Step 1 and hard-coded here.
# Boundary rows are the FIRST row of each new episode.
RESET_ROWS = [999, 1999, 2999, 3999, 4999, 5999, 6999, 7999, 8999, 9999]
STUB_ROW = 9999                    # one-row episode at the end; discarded
N_ROWS = 10000
N_EPISODES = 10                    # ep0 = rows 0..998, ep1..ep9 = 1000 rows each

LEGS = ["LF", "LH", "RF", "RH"]
JOINT_NAMES = [f"{leg}_{j}" for j in ("HAA", "HFE", "KFE") for leg in LEGS]
STATE_GROUPS = [
    ("v", LIN_VEL, "m/s"), ("omega", ANG_VEL, "rad/s"), ("g", GRAVITY, "unit"),
    ("q", JOINT_POS, "rad"), ("qdot", JOINT_VEL, "rad/s"), ("tau", JOINT_TAU, "Nm"),
]


def repo_paths(base=None):
    base = base or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return {
        "lite": os.path.join(base, "robotic_world_model_lite"),
        "rsl": os.path.join(base, "rsl_rl_rwm"),
        "csv": os.path.join(base, "robotic_world_model_lite", "assets", "data",
                            "state_action_data_0.csv"),
        "ckpt": os.path.join(base, "robotic_world_model_lite", "assets", "models",
                             "pretrain_rnn_ens.pt"),
    }


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_commit(repo_dir):
    head = os.path.join(repo_dir, ".git", "HEAD")
    if not os.path.exists(head):
        return "not a git checkout"
    with open(head) as f:
        ref = f.read().strip()
    if ref.startswith("ref: "):
        p = os.path.join(repo_dir, ".git", ref[5:])
        if os.path.exists(p):
            with open(p) as f:
                return f.read().strip()
        packed = os.path.join(repo_dir, ".git", "packed-refs")
        if os.path.exists(packed):
            with open(packed) as f:
                for line in f:
                    if line.rstrip().endswith(ref[5:]):
                        return line.split()[0]
    return ref


# --------------------------------------------------------------------------
# reference config
# --------------------------------------------------------------------------
def load_reference_config(lite_repo):
    """
    Import the reference dataclass config and return the constants we need.

    Imported, never retyped. The config package is pure dataclasses (no torch),
    so it loads without touching the CUDA-pinned dependencies in setup.py.
    """
    scripts = os.path.join(lite_repo, "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    spec = importlib.util.spec_from_file_location(
        "_rwm_configs", os.path.join(scripts, "configs", "__init__.py"),
        submodule_search_locations=[os.path.join(scripts, "configs")])
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_rwm_configs"] = mod
    sys.modules["configs"] = mod
    spec.loader.exec_module(mod)
    cfg = mod.AnymalDFlatConfig

    data = cfg.DataConfig()
    arch = cfg.ModelArchitectureConfig()
    env = cfg.EnvironmentConfig()
    base_data = mod.BaseConfig.DataConfig()
    base_env = mod.BaseConfig.EnvironmentConfig()
    # eval_traj_noise_scale lives in ModelTrainingConfig (base_cfg.py:99), which
    # AnymalDFlatConfig inherits unchanged (`pass`).
    train_cfg = cfg.ModelTrainingConfig()

    out = {
        "state_data_mean": np.asarray(data.state_data_mean, dtype=np.float64),
        "state_data_std": np.asarray(data.state_data_std, dtype=np.float64),
        "action_data_mean": np.asarray(data.action_data_mean, dtype=np.float64),
        "action_data_std": np.asarray(data.action_data_std, dtype=np.float64),
        "state_idx_dict": data.state_idx_dict,
        "history_horizon": arch.history_horizon,
        "forecast_horizon": arch.forecast_horizon,
        "ensemble_size": arch.ensemble_size,
        "contact_dim": arch.contact_dim,
        "termination_dim": arch.termination_dim,
        "architecture_config": arch.architecture_config,
        "step_dt": base_env.step_dt if hasattr(base_env, "step_dt") else env.step_dt,
        "num_eval_trajectories": base_data.num_eval_trajectories,
        "len_eval_trajectory": base_data.len_eval_trajectory,
        "eval_traj_noise_scale": list(train_cfg.eval_traj_noise_scale),
        "num_visualizations": base_data.num_visualizations,
        # training hyperparameters, imported not retyped (Step 4 / 2b)
        "loss_weights": dict(train_cfg.system_dynamics_loss_weights),
        "batch_size": train_cfg.batch_size,
        "max_iterations": train_cfg.max_iterations,
        "save_interval": train_cfg.save_interval,
        "learning_rate": cfg.ModelOptimizerConfig().learning_rate,
        "weight_decay": cfg.ModelOptimizerConfig().weight_decay,
        "command_resample_interval_range": getattr(
            env, "command_resample_interval_range", None),
    }
    for k in ("state_data_mean", "state_data_std"):
        assert out[k].shape == (STATE_DIM,), f"{k} has shape {out[k].shape}"
    for k in ("action_data_mean", "action_data_std"):
        assert out[k].shape == (ACTION_DIM,), f"{k} has shape {out[k].shape}"
    assert np.all(out["state_data_std"] > 0), "state_data_std has a non-positive entry"
    out["actions_are_normalised"] = not (
        np.all(out["action_data_mean"] == 0.0) and np.all(out["action_data_std"] == 1.0))
    return out


# --------------------------------------------------------------------------
# data
# --------------------------------------------------------------------------
def build_episode_id(n=N_ROWS, reset_rows=RESET_ROWS, stub_row=STUB_ROW):
    """
    episode_id[i] = index of the episode row i belongs to, or -1 for the
    discarded one-row stub at the end.
    """
    ep = np.full(n, -1, dtype=np.int64)
    starts = [0] + [r for r in reset_rows if r != stub_row]
    ends = starts[1:] + [stub_row]
    for k, (s, e) in enumerate(zip(starts, ends)):
        ep[s:e] = k
    ep[stub_row] = -1
    return ep


def assert_episode_structure(data, episode_id, verbose=True):
    """
    Re-derive the resets from the data and check they match the hard-coded rows.
    At every boundary row: all 12 joint velocities, the 4 HAA joint positions,
    and all 12 actions must be exactly zero.
    """
    qdot_zero = np.all(data[:, JOINT_VEL] == 0.0, axis=1)
    haa_zero = np.all(data[:, HAA_COLS] == 0.0, axis=1)
    act_zero = np.all(data[:, ACTIONS] == 0.0, axis=1)
    derived = np.flatnonzero(qdot_zero & haa_zero & act_zero).tolist()

    assert derived == RESET_ROWS, (
        f"reset fingerprint disagrees with hard-coded rows\n"
        f"  derived:   {derived}\n  hard-coded: {RESET_ROWS}")
    for r in RESET_ROWS:
        assert np.all(data[r, JOINT_VEL] == 0.0), f"row {r}: joint velocities not all zero"
        assert np.all(data[r, HAA_COLS] == 0.0), f"row {r}: HAA positions not all zero"
        assert np.all(data[r, ACTIONS] == 0.0), f"row {r}: actions not all zero"

    assert np.all(data[:, TERMINATION] == 0.0), "column 65 is not identically zero"
    counts = np.bincount(episode_id[episode_id >= 0], minlength=N_EPISODES)
    assert counts[0] == 999, f"ep0 has {counts[0]} rows, expected 999"
    assert np.all(counts[1:] == 1000), f"ep1..ep9 lengths: {counts[1:]}"
    assert episode_id[STUB_ROW] == -1, "stub row not excluded"
    assert int((episode_id == -1).sum()) == 1, "more than one row excluded"

    if verbose:
        print("  episode structure asserted:")
        print(f"    reset fingerprint re-derived from data -> {derived}")
        print(f"    matches hard-coded RESET_ROWS")
        print(f"    column 65 identically zero: True (episode structure NOT recoverable from it)")
        print(f"    ep0 = 999 rows, ep1..ep9 = 1000 rows each, row {STUB_ROW} discarded")
    return derived


def load_data(csv_path, verbose=True):
    """Return (data [10000,66] float64, episode_id [10000] int64)."""
    import pandas as pd
    data = pd.read_csv(csv_path, header=None).to_numpy(dtype=np.float64)
    assert data.shape == (N_ROWS, 66), f"expected (10000, 66), got {data.shape}"
    assert np.isfinite(data).all(), "non-finite entries in the CSV"
    episode_id = build_episode_id(len(data))
    if verbose:
        print(f"  loaded {data.shape[0]} rows x {data.shape[1]} cols"
              f"  ({data.shape[0] * DT:.0f} s at {1/DT:.0f} Hz)")
    assert_episode_structure(data, episode_id, verbose=verbose)
    return data, episode_id


def normalise_state(state, mean, std):
    return (state - mean) / std


def denormalise_state(state, mean, std):
    return state * std + mean


def normalise_action(action, mean, std):
    return (action - mean) / std


def valid_window_starts(episode_id, window):
    """
    Start indices s such that rows s..s+window-1 all lie in the same episode
    (and none is the discarded stub).
    """
    n = len(episode_id)
    starts = []
    for s in range(n - window + 1):
        seg = episode_id[s:s + window]
        if seg[0] >= 0 and np.all(seg == seg[0]):
            starts.append(s)
    return np.asarray(starts, dtype=np.int64)
