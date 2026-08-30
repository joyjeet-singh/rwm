"""The per-triple (trajectory, forecast step, state dimension) cache.

WHY THIS EXISTS. Every rollout in this project builds `err` and `sig` at
(n_traj, h, 45), reduces them to pooled aggregates, and discards the arrays.
`scripts/task_d_nind20.py:115` is the canonical instance. Three pre-registered
rules -- M-62 (episode clustering), M-63 (per-dimension coverage) and M-65 (the
oracle rescale) -- all need the arrays rather than the aggregates, and M-64 needs
the episode map. One stored rollout serves all four.

WHERE IT WRITES, AND WHY NOT `results/`. `cache/`, gitignored. The paper commits
in section 8 and Appendix D to reproducing "0.90% of the 905,391 numeric values under
results/", and that partition is load-bearing for the honesty argument (M-28 --
counting carried-in files once inflated the published figure by fiftyfold). A
per-triple array is tens of megabytes of numbers; writing it into `results/` moves
a denominator the paper cites. The existing exclusion mechanism does not cover it
honestly either: that mechanism's stated principle is that `step4_5_timing.json`
measures the machine rather than the model, and a per-triple error array measures
the model. `results/` keeps only the derived statistics the paper cites.

WHAT IS STORED. Signed residuals, not absolute. Signed is strictly more
informative and the absolute value is one call away; storing the absolute value
would have thrown away the sign counts section 6.6 reports. The aleatoric and epistemic
terms are stored separately rather than combined, because section 6.2 reports them
separately and their combination is a derived quantity.

THE RESIDUAL SPACE IS RECORDED, NOT ASSUMED. relative-L1 and nRMSE differ in how
they treat the denominator (section 3.1), so a convention error would hide exactly here.
Every cached object names the space its residuals live in and the constants that
define it.
"""
import hashlib
import json
import os

import numpy as np

# Repo root, from this file's location: src/ -> repo root.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "cache")

# The two upstream pins, from setup.sh:14-15. Recorded in every cached object so a
# cache built against a different upstream can never be mistaken for this one.
LITE_COMMIT = "13a798e9d35dabf12c0e6e02977b25ec64dfb2bd"
RSL_COMMIT = "18eebcdd7145284c8d5eed5d8ed1a4b96c649693"

SCHEMA = 1

REQUIRED = ("err", "sig_aleatoric", "sig_epistemic", "traj_to_episode",
            "traj_start_row", "model_id", "arena", "unit_length",
            "n_independent", "lite_commit", "rsl_commit", "residual_space")


def path_for(model_id, arena, unit_length):
    """One object per model x arena x unit-length. Arena strings contain spaces;
    they are slugged for the filename and kept verbatim inside the object."""
    slug = arena.lower().replace(" ", "_").replace("/", "-")
    return os.path.join(CACHE, f"{model_id}__{slug}__u{unit_length}.npz")


def write(model_id, arena, unit_length, err_signed, sig_aleatoric, sig_epistemic,
          traj_to_episode, traj_start_row, n_independent, start_step,
          residual_space, residual_space_detail, extra=None):
    """Write one cached object. Arrays are stored float64 exactly as computed --
    no downcast, because the gate that reads this back compares bitwise.

    err_signed: (n_traj, h, 45) signed residual, prediction minus truth.
    sig_*:      (n_traj, h, 45) predicted sigma, the two terms kept apart.
    """
    os.makedirs(CACHE, exist_ok=True)
    err_signed = np.asarray(err_signed, dtype=np.float64)
    sig_aleatoric = np.asarray(sig_aleatoric, dtype=np.float64)
    sig_epistemic = np.asarray(sig_epistemic, dtype=np.float64)
    for nm, a in (("sig_aleatoric", sig_aleatoric), ("sig_epistemic", sig_epistemic)):
        assert a.shape == err_signed.shape, f"{nm} {a.shape} != err {err_signed.shape}"
    n_traj = err_signed.shape[0]
    assert len(traj_to_episode) == n_traj, "episode map length != n_traj"
    assert len(traj_start_row) == n_traj, "start-row length != n_traj"

    meta = {
        "schema": SCHEMA,
        "model_id": model_id,
        "arena": arena,
        "unit_length": int(unit_length),
        "start_step": int(start_step),
        "n_trajectories": int(n_traj),
        "n_independent": int(n_independent),
        "n_forecast_steps": int(err_signed.shape[1]),
        "n_dims": int(err_signed.shape[2]),
        # Named, not assumed -- see the module docstring.
        "residual_space": residual_space,
        "residual_space_detail": residual_space_detail,
        "residual_sign_convention": "prediction minus truth",
        "sigma_terms": "aleatoric and epistemic stored separately; total is derived",
        "lite_commit": LITE_COMMIT,
        "rsl_commit": RSL_COMMIT,
    }
    if extra:
        meta.update(extra)

    p = path_for(model_id, arena, unit_length)
    np.savez_compressed(
        p,
        err=err_signed,
        sig_aleatoric=sig_aleatoric,
        sig_epistemic=sig_epistemic,
        traj_to_episode=np.asarray(traj_to_episode, dtype=np.int64),
        traj_start_row=np.asarray(traj_start_row, dtype=np.int64),
        meta=np.array(json.dumps(meta, sort_keys=True)),
    )
    return p, meta


def read(model_id, arena, unit_length):
    """Load a cached object. Returns (arrays_dict, meta_dict)."""
    p = path_for(model_id, arena, unit_length)
    if not os.path.exists(p):
        raise FileNotFoundError(p)
    z = np.load(p, allow_pickle=False)
    meta = json.loads(str(z["meta"]))
    arrays = {k: z[k] for k in ("err", "sig_aleatoric", "sig_epistemic",
                                "traj_to_episode", "traj_start_row")}
    missing = [f for f in REQUIRED
               if f not in arrays and f not in meta]
    if missing:
        raise AssertionError(f"cached object {p} missing required fields: {missing}")
    return arrays, meta


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()
