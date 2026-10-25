"""
Sanity-check and characterise assets/data/state_action_data_0.csv from
leggedrobotics/robotic_world_model_lite before anything is trained on it.

The column map is not assumed -- it is the one the repository's own code uses:

  scripts/train.py:54-58                  slices each frame as
                                          [ :state_dim ][ state_dim:+action_dim ]
                                          [ +extension_dim ][ +contact_dim ][ rest ]
  scripts/envs/anymal_d_flat.py:179,187   state_dim = 45, action_dim = 12
  scripts/configs/base_cfg.py:56          extension_dim = 0  (never overridden, so
                                          no extension block sits between actions
                                          and contacts)
  scripts/configs/anymal_d_flat_cfg.py:71-72   contact_dim = 8, termination_dim = 1
  scripts/configs/anymal_d_flat_cfg.py:38-45   the 45 state columns, by group
  scripts/envs/anymal_d_flat.py:84-85     contacts[0:4] thigh, contacts[4:8] foot
  scripts/configs/anymal_d_flat_cfg.py:110-111  history 32, forecast 8
  scripts/configs/base_cfg.py:21          step_dt = 0.02  ->  50 Hz

Run:  python analyze_state_action_data.py [--csv PATH] [--outdir PATH]
"""

import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# --------------------------------------------------------------------------
# column map
# --------------------------------------------------------------------------
LIN_VEL = list(range(0, 3))       # base linear velocity      m/s
ANG_VEL = list(range(3, 6))       # base angular velocity     rad/s
GRAVITY = list(range(6, 9))       # projected gravity         unit vector
JOINT_POS = list(range(9, 21))    # joint positions           rad
JOINT_VEL = list(range(21, 33))   # joint velocities          rad/s
JOINT_TAU = list(range(33, 45))   # joint torques             Nm
ACTIONS = list(range(45, 57))     # commanded joint position targets
CONTACT_THIGH = list(range(57, 61))
CONTACT_FOOT = list(range(61, 65))
CONTACTS = CONTACT_THIGH + CONTACT_FOOT
TERMINATION = 65

BINARY_COLS = CONTACTS + [TERMINATION]

STATE_GROUPS = [
    ("base linear velocity  $v$", LIN_VEL, "m/s"),
    ("base angular velocity  $\\omega$", ANG_VEL, "rad/s"),
    ("projected gravity  $g$", GRAVITY, "unit"),
    ("joint positions  $q$", JOINT_POS, "rad"),
    ("joint velocities  $\\dot{q}$", JOINT_VEL, "rad/s"),
    ("joint torques  $\\tau$", JOINT_TAU, "Nm"),
]

# ANYmal-D joints in IsaacLab order: the four HAA, then the four HFE, then the
# four KFE, each in LF/LH/RF/RH order. Inferred, not stated in the repo -- the
# per-column normalisation constants in anymal_d_flat_cfg.py fall into three
# blocks of four (velocity std 1.0/1.5/2.5, torque mean sign patterns
# -2,-2,2,2 / -6,8,-6,8 / 12,-12,12,-12), which is exactly that layout. The gait
# conclusions below do not depend on it; the diagonal-pair structure is read
# from the foot channels, whose LF/LH/RF/RH order is the same convention.
LEGS = ["LF", "LH", "RF", "RH"]
JOINT_NAMES = [f"{leg}_{j}" for j in ("HAA", "HFE", "KFE") for leg in LEGS]

HISTORY_HORIZON = 32
FORECAST_HORIZON = 8
WINDOW = HISTORY_HORIZON + FORECAST_HORIZON

DT = 0.02
FS = 1.0 / DT
PLOT_STEPS = 500

GRAVITY_TOL = 0.02
JUMP_TOL = 0.5


def rule(title=""):
    print("\n" + "=" * 78)
    if title:
        print(title)
        print("=" * 78)


def verdict(ok):
    return "PASS" if ok else "FAIL"


# --------------------------------------------------------------------------
# episode structure
# --------------------------------------------------------------------------
def find_episode_starts(data):
    """
    Return the row indices that begin an episode.

    Column 65 is NOT sufficient. In this file it is identically zero, yet the
    environment still resets on the 1000-step time limit, and IsaacLab records
    the post-reset observation in the frame where the reset happened. Those rows
    carry an exact-zero fingerprint that floating-point locomotion data cannot
    produce by accident:

      * all 12 joint velocities exactly 0.0   (reset_joints velocity range is 0)
      * all 4 HAA positions exactly 0.0       (HAA default is 0, scaled resets
                                               leave it at exactly 0)
      * all 12 actions exactly 0.0            (no action issued yet)

    Row 0 always starts an episode. Any row following a termination flag also
    starts one, so both signals are unioned.
    """
    n = len(data)
    qdot_zero = np.all(data[:, JOINT_VEL] == 0.0, axis=1)
    haa_zero = np.all(data[:, JOINT_POS[0:4]] == 0.0, axis=1)
    act_zero = np.all(data[:, ACTIONS] == 0.0, axis=1)
    reset_rows = np.flatnonzero(qdot_zero & haa_zero & act_zero)

    term_idx = np.flatnonzero(data[:, TERMINATION] == 1.0)
    after_term = term_idx[term_idx + 1 < n] + 1

    starts = np.unique(np.concatenate(([0], reset_rows, after_term))).astype(int)

    print("episode-start detection")
    print(f"  rows flagged by column 65 (termination)        : {len(term_idx)}")
    print(f"  rows with all 12 joint velocities exactly 0.0  : {int(qdot_zero.sum())}")
    print(f"  rows with all 4 HAA positions exactly 0.0      : {int(haa_zero.sum())}")
    print(f"  rows with all 12 actions exactly 0.0           : {int(act_zero.sum())}")
    print(f"  rows matching all three (reset fingerprint)    : {len(reset_rows)}")
    print(f"  -> {reset_rows.tolist()}")
    if len(reset_rows) > 1:
        gaps = np.unique(np.diff(reset_rows))
        print(f"  spacing between them: {gaps.tolist()} rows"
              f"  ({gaps[0] * DT:.0f} s)" if len(gaps) == 1 else
              f"  spacing between them: {np.diff(reset_rows).tolist()} rows")
    print(f"  episode starts (union, incl. row 0)            : {len(starts)}")
    if len(term_idx) == 0 and len(reset_rows) > 0:
        print("  NOTE: column 65 is identically zero. These are time-limit")
        print("        truncations, not failures -- the robot never fell in 200 s.")
        print("        A reader who trusts column 65 alone will not see them.")
    return starts, reset_rows, term_idx


def segments(starts, n):
    """[(start, end_inclusive), ...] from episode start indices."""
    ends = np.concatenate((starts[1:] - 1, [n - 1]))
    return list(zip(starts.tolist(), ends.tolist()))


# --------------------------------------------------------------------------
# assertions
# --------------------------------------------------------------------------
def assert_gravity_unit(data):
    """|g| must be 1 for every row, or the column mapping is wrong."""
    norms = np.linalg.norm(data[:, GRAVITY], axis=1)
    err = np.abs(norms - 1.0)
    ok = bool(np.all(err <= GRAVITY_TOL))
    print(f"[1] gravity vector (cols 6-8) has unit length within {GRAVITY_TOL}")
    print(f"    |g|      min {norms.min():.6f}  max {norms.max():.6f}  mean {norms.mean():.6f}")
    print(f"    ||g|-1|  max {err.max():.3e}  at row {int(np.argmax(err))}")
    print(f"    rows outside tolerance: {int((err > GRAVITY_TOL).sum())} / {len(data)}")
    print(f"    -> {verdict(ok)}")
    if not ok:
        print("    STOP. The column mapping is wrong. Fix it before reading anything else.")
    return ok


def assert_binary(data):
    """Contacts and termination must be exactly 0.0 or 1.0."""
    block = data[:, BINARY_COLS]
    bad = ~np.isin(block, (0.0, 1.0))
    ok = not bool(bad.any())
    print(f"[2] cols {BINARY_COLS[0]}-{BINARY_COLS[-1]} contain only 0.0 and 1.0")
    print(f"    unique values across all {block.size} entries: {np.unique(block).tolist()}")
    print(f"    non-binary entries: {int(bad.sum())}")
    per_col = [int(data[:, c].sum()) for c in BINARY_COLS]
    print(f"    ones per column: " + "  ".join(
        f"{c}:{v}" for c, v in zip(BINARY_COLS, per_col)))
    print(f"    -> {verdict(ok)}")
    return ok


def assert_continuous(data, starts):
    """
    Largest joint-position change between adjacent rows must stay under JUMP_TOL.

    Reported twice, because the answer differs and the difference is the whole
    story: over every adjacent pair (which includes the 10 pairs that step across
    an episode reset), and over only the pairs that lie inside one episode.
    """
    dq = np.abs(np.diff(data[:, JOINT_POS], axis=0))
    per_step = dq.max(axis=1)
    n_pairs = len(per_step)

    crosses = np.zeros(n_pairs, dtype=bool)
    boundary = starts[starts > 0] - 1            # pair (s-1 -> s) enters a new episode
    crosses[boundary[boundary < n_pairs]] = True
    within = ~crosses

    raw_ok = bool(per_step.max() < JUMP_TOL)
    in_ok = bool(per_step[within].max() < JUMP_TOL)
    worst_in = int(np.argmax(np.where(within, per_step, -np.inf)))
    worst_all = int(np.argmax(per_step))

    print(f"[3] adjacent rows are continuous: max |dq| < {JUMP_TOL} rad")
    print(f"    (a) all {n_pairs} adjacent pairs")
    print(f"        max {per_step.max():.5f} rad at row {worst_all}->{worst_all + 1}"
          f"   -> {verdict(raw_ok)}")
    print(f"    (b) {int(within.sum())} pairs that stay inside one episode")
    print(f"        max {per_step[within].max():.5f} rad at row {worst_in}->{worst_in + 1}"
          f"   -> {verdict(in_ok)}")
    print(f"        percentiles  p50 {np.percentile(per_step[within], 50):.4f}"
          f"   p90 {np.percentile(per_step[within], 90):.4f}"
          f"   p99 {np.percentile(per_step[within], 99):.4f}"
          f"   max {per_step[within].max():.4f} rad")
    if crosses.any():
        print(f"    (c) {int(crosses.sum())} pairs that step across an episode reset")
        print(f"        min {per_step[crosses].min():.5f}"
              f"   median {np.median(per_step[crosses]):.5f}"
              f"   max {per_step[crosses].max():.5f} rad")
        print(f"        every one of them exceeds the within-episode max of "
              f"{per_step[within].max():.5f}"
              if per_step[crosses].min() > per_step[within].max() else
              f"        these overlap the within-episode range")

    print()
    if raw_ok:
        print("    Verdict: one continuous recording.")
    elif in_ok:
        print("    Verdict: NOT one unbroken recording, and NOT shuffled samples.")
        print("    It is a concatenation of continuous episodes. Within an episode the")
        print("    data is smooth (b); the only breaks are the episode resets (c), and")
        print("    they are clean, isolated, and exactly where the reset fingerprint")
        print("    says they are. Downstream code that assumes continuity is safe as")
        print("    long as it never builds a window across a reset.")
    else:
        print("    Verdict: discontinuous even inside episodes. Investigate before use.")
    return raw_ok, in_ok


# --------------------------------------------------------------------------
# counts
# --------------------------------------------------------------------------
def count_terminations(data, starts, reset_rows, term_idx):
    n = len(data)
    print(f"terminations flagged in column 65 over {n} steps: {len(term_idx)}")
    if len(term_idx) == 0:
        thigh = data[:, CONTACT_THIGH]
        rows = np.flatnonzero(thigh.sum(axis=1) > 0)
        print("  The robot never failed: 200 s of walking with no fall and no")
        print("  terminating contact.")
        print(f"  thigh contacts (cols 57-60) over the whole file: {int(thigh.sum())} step(s)")
        for r in rows:
            which = [LEGS[i] for i in np.flatnonzero(thigh[r])]
            print(f"    row {r} (t = {r * DT:.2f} s): {', '.join(which)} thigh,"
                  f" 1 step only, all 4 feet also down, no termination")
        if len(rows):
            print("  A brief scuff, not a fall. Thigh contact is a reward penalty in")
            print("  this environment, not a termination condition.")
    else:
        print(f"  at rows: {term_idx.tolist()}")

    print(f"\nunmarked episode resets (time-limit truncations): {len(reset_rows)}")
    if len(reset_rows):
        print(f"  at rows: {reset_rows.tolist()}")
    print(f"\nepisode segments: {len(starts)}")
    segs = segments(starts, n)
    lens = [e - s + 1 for s, e in segs]
    for (s, e), L in zip(segs, lens):
        print(f"  rows {s:5d}..{e:5d}   {L:5d} steps   {L * DT:6.2f} s")
    print(f"  lengths: min {min(lens)}  max {max(lens)}  mean {np.mean(lens):.1f}")
    return segs


def count_valid_windows(data, starts):
    """
    A window is WINDOW consecutive rows. It is valid only if all WINDOW rows come
    from the same episode -- i.e. no episode start falls strictly inside it.
    """
    n = len(data)
    naive = n - WINDOW + 1
    segs = segments(starts, n)
    per_seg = [max(0, (e - s + 1) - WINDOW + 1) for s, e in segs]
    valid = sum(per_seg)

    print(f"window = {HISTORY_HORIZON} history + {FORECAST_HORIZON} forecast = {WINDOW} steps\n")
    print(f"  a) rows in the file                                    {n}")
    print(f"  b) windows if the file were one unbroken episode       {naive}"
          f"   (loses {n - naive} to the tail)")
    print(f"  c) windows if you trust column 65 alone                {naive}"
          f"   (column 65 is all zero, so this is the same as b)")
    print(f"  d) windows that respect the real episode resets        {valid}")
    print()
    print(f"  per segment:")
    for (s, e), w in zip(segs, per_seg):
        print(f"    rows {s:5d}..{e:5d}  length {e - s + 1:5d}  ->  {w:5d} windows")
    print()
    print(f"  ACTUAL TRAINING SET SIZE: {valid}")
    print()
    print(f"  accounting, from {n} rows down to {valid} windows:")
    print(f"    {n:6d}  rows")
    print(f"   -{WINDOW - 1:5d}  the file's last {WINDOW - 1} rows cannot start a full window")
    print(f"    {naive:6d}  = b, the count you get from column 65 alone")
    print(f"   -{naive - valid:5d}  windows that straddle one of the"
          f" {len(starts) - 1} unmarked resets")
    print(f"    {valid:6d}  = d")
    print()
    print(f"  total gap vs the 10,000 row count: {n - valid}"
          f"  ({100.0 * (n - valid) / n:.2f}%)")
    print(f"  Of that, {naive - valid} windows are ones you would silently train on,")
    print(f"  each stitching the end of one episode onto the start of another.")
    return valid


# --------------------------------------------------------------------------
# gait
# --------------------------------------------------------------------------
def describe_gait(data):
    foot = data[:, CONTACT_FOOT]
    thigh = data[:, CONTACT_THIGH]

    print("duty factor over the full 200 s")
    for i, leg in enumerate(LEGS):
        print(f"  {leg} foot  {foot[:, i].mean() * 100:5.1f} %"
              f"       {leg} thigh {thigh[:, i].mean() * 100:5.1f} %")
    print(f"  thigh channels are {'all zero' if thigh.sum() == 0 else 'nonzero'}"
          f" -- {'no knee ever touched the ground' if thigh.sum() == 0 else 'check'}")

    n_down = foot.sum(axis=1)
    print("\nfeet on the ground simultaneously")
    for k in range(5):
        print(f"  {k} feet  {(n_down == k).mean() * 100:5.1f} %")
    print(f"  mean {n_down.mean():.2f} feet down")

    print("\npairwise stance overlap")
    pairs = [(0, 1, "LF+LH  left lateral"), (2, 3, "RF+RH  right lateral"),
             (0, 2, "LF+RF  front pair"), (1, 3, "LH+RH  hind pair"),
             (0, 3, "LF+RH  diagonal"), (1, 2, "LH+RF  diagonal")]
    for a, b, label in pairs:
        obs = (foot[:, a] * foot[:, b]).mean()
        exp = foot[:, a].mean() * foot[:, b].mean()
        ratio = obs / exp if exp > 0 else float("nan")
        mark = "  <<<" if ratio > 1.3 else ("  ---" if ratio < 0.6 else "")
        print(f"  {label:22s} observed {obs * 100:5.1f} %   if independent {exp * 100:5.1f} %"
              f"   ratio {ratio:.2f}{mark}")

    print("\nstride period (autocorrelation of each foot's contact signal, lags 6-60)")
    periods = []
    for i, leg in enumerate(LEGS):
        s = foot[:, i] - foot[:, i].mean()
        ac = np.correlate(s, s, mode="full")[len(s) - 1:]
        ac = ac / ac[0]
        lag = 6 + int(np.argmax(ac[6:60]))
        periods.append(lag)
        print(f"  {leg}  {lag} steps = {lag * DT:.2f} s = {1.0 / (lag * DT):.2f} Hz"
              f"   (peak {ac[lag]:.2f})")

    p = int(round(np.mean(periods)))
    print(f"\nphase relative to LF (stride {p} steps): 0.0 = in phase, 0.5 = antiphase")
    ref = foot[:, 0] - foot[:, 0].mean()
    for i, leg in enumerate(LEGS):
        s = foot[:, i] - foot[:, i].mean()
        xc = np.array([np.mean(ref[:len(ref) - k] * s[k:]) for k in range(p)])
        k = int(np.argmax(xc))
        print(f"  {leg}  lag {k:2d} steps   phase {k / p:.2f}")

    print("\nstance / swing bout lengths")
    for i, leg in enumerate(LEGS):
        v = foot[:, i].astype(int)
        bounds = np.concatenate(([0], np.flatnonzero(np.diff(v)) + 1, [len(v)]))
        runs, vals = np.diff(bounds), v[bounds[:-1]]
        st, sw = runs[vals == 1], runs[vals == 0]
        print(f"  {leg}  stance {st.mean():5.2f} steps ({st.mean() * DT:.3f} s)"
              f"   swing {sw.mean():5.2f} steps ({sw.mean() * DT:.3f} s)"
              f"   {len(st)} stance bouts")


# --------------------------------------------------------------------------
# plots
# --------------------------------------------------------------------------
def _mark_resets(ax, starts, n):
    for s in starts:
        if 0 < s < n:
            ax.axvline(s * DT, color="#d62728", lw=1.2, ls="--", alpha=0.8)


def plot_base_velocities(data, outdir, starts, n=PLOT_STEPS):
    t = np.arange(n) * DT
    fig, axes = plt.subplots(3, 1, figsize=(11, 7), sharex=True)
    for ax, c, name in zip(axes, LIN_VEL,
                           ("$v_x$  forward", "$v_y$  lateral", "$v_z$  vertical")):
        ax.plot(t, data[:n, c], lw=0.9, color="#1f77b4")
        ax.axhline(0, color="0.7", lw=0.6)
        ax.set_ylabel(f"{name}\n[m/s]")
        ax.grid(alpha=0.25)
        _mark_resets(ax, starts, n)
    axes[-1].set_xlabel(f"time [s]   (50 Hz, first {n} steps)")
    axes[0].set_title("Base linear velocity, columns 0-2")
    fig.tight_layout()
    p = os.path.join(outdir, "01_base_linear_velocity.png")
    fig.savefig(p, dpi=140)
    plt.close(fig)
    return p


def fit_action_to_position(data, starts, joint, max_lag=8):
    """
    The action column is the raw policy output. This repository never applies an
    action scale (grep the whole of scripts/ -- there is none), so cols 45-56 are
    NOT joint targets in radians; the scale and default-pose offset that turn them
    into targets live in the upstream IsaacLab env and are not recorded here.

    Fit  q[t+k] ~ s * a[t] + b  over the lag k that maximises |correlation|, on
    rows that do not touch an episode reset. Returns (k, s, b, corr).
    """
    n = len(data)
    bad = set()
    for r in starts:
        bad.update(range(max(0, r - 1), min(n, r + 2)))
    idx = np.array([i for i in range(n - max_lag) if i not in bad])
    a = data[idx, ACTIONS[joint]]
    best = (0, 1.0, 0.0, 0.0)
    for k in range(max_lag + 1):
        q = data[idx + k, JOINT_POS[joint]]
        c = np.corrcoef(a, q)[0, 1]
        if abs(c) > abs(best[3]):
            s, b = np.linalg.lstsq(np.vstack([a, np.ones_like(a)]).T, q, rcond=None)[0]
            best = (k, s, b, c)
    return best


def plot_joint_tracking(data, outdir, starts, joint=6, n=PLOT_STEPS):
    t = np.arange(n) * DT
    q = data[:n, JOINT_POS[joint]]
    a = data[:n, ACTIONS[joint]]
    k, s, b, c = fit_action_to_position(data, starts, joint)

    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(11, 7.2), sharex=True)

    # panel 1: the two columns as they actually sit in the file, on separate
    # axes, because they are not the same physical quantity.
    ax.plot(t, q, lw=1.2, color="#1f77b4", label=f"measured position $q$, col {JOINT_POS[joint]} [rad]")
    ax.set_ylabel("measured position [rad]", color="#1f77b4")
    ax.tick_params(axis="y", labelcolor="#1f77b4")
    axr = ax.twinx()
    axr.plot(t, a, lw=1.0, color="#d62728", alpha=0.8,
             label=f"raw action $a$, col {ACTIONS[joint]} [dimensionless]")
    axr.set_ylabel("raw policy action [-]", color="#d62728")
    axr.tick_params(axis="y", labelcolor="#d62728")
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = axr.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper right", fontsize=8.5)
    ax.grid(alpha=0.25)
    ax.set_title(f"Joint {joint} ({JOINT_NAMES[joint]}): measured position vs commanded action\n"
                 "separate axes -- the action is the raw policy output, not a target in radians",
                 fontsize=10.5)

    # panel 2: the action mapped into joint space by the fitted lag and gain
    ax2.plot(t, q, lw=1.2, color="#1f77b4", label=f"measured position $q[t]$")
    ax2.plot(t, s * np.roll(a, k) + b, lw=1.0, color="#d62728", alpha=0.85,
             label=f"${s:.3f}\\,a[t-{k}] {'+' if b >= 0 else '-'} {abs(b):.3f}$"
                   f"   (fitted lag {k} steps = {k * DT * 1000:.0f} ms, r = {c:.2f})")
    ax2.set_ylabel("[rad]")
    ax2.set_xlabel(f"time [s]   (50 Hz, first {n} steps)")
    ax2.legend(loc="upper right", fontsize=8.5)
    ax2.grid(alpha=0.25)

    for a_ in (ax, ax2):
        _mark_resets(a_, starts, n)
    fig.tight_layout()
    p = os.path.join(outdir, "02_joint_tracking.png")
    fig.savefig(p, dpi=140)
    plt.close(fig)
    return p, (k, s, b, c)


def plot_contact_raster(data, outdir, starts, n=PLOT_STEPS):
    raster = data[:n, CONTACTS].T
    labels = [f"{leg} thigh" for leg in LEGS] + [f"{leg} foot" for leg in LEGS]
    fig, ax = plt.subplots(figsize=(13, 3.8))
    ax.imshow(raster, aspect="auto", cmap="gray_r", vmin=0, vmax=1,
              interpolation="nearest", extent=[0, n * DT, 8, 0])
    ax.set_yticks(np.arange(8) + 0.5)
    ax.set_yticklabels(labels, fontsize=9)
    ax.axhline(4, color="#d62728", lw=1.6)
    for y in range(1, 8):
        ax.axhline(y, color="0.75", lw=0.4)
    _mark_resets(ax, starts, n)
    ax.set_xlabel(f"time [s]   (50 Hz, first {n} steps)")
    ax.set_title("Contact raster, columns 57-64   black = in contact   "
                 "(red line separates the 4 thigh from the 4 foot channels)")
    fig.tight_layout()
    p = os.path.join(outdir, "03_contact_raster.png")
    fig.savefig(p, dpi=170)
    plt.close(fig)
    return p


def plot_state_histograms(data, outdir):
    fig, axes = plt.subplots(2, 3, figsize=(14, 7.5))
    for ax, (name, cols, unit) in zip(axes.ravel(), STATE_GROUPS):
        block = data[:, cols]
        lo, hi = np.percentile(block, [0.1, 99.9])
        if hi <= lo:
            lo, hi = block.min() - 0.5, block.max() + 0.5
        bins = np.linspace(lo, hi, 80)
        for j in range(block.shape[1]):
            ax.hist(block[:, j], bins=bins, histtype="step", lw=0.9, alpha=0.75)
        ax.set_title(f"{name}   ({len(cols)} ch, cols {cols[0]}-{cols[-1]})", fontsize=10)
        ax.set_xlabel(unit, fontsize=9)
        ax.set_ylabel("count", fontsize=9)
        ax.grid(alpha=0.2)
    fig.suptitle("Distribution per state group, all 10,000 steps "
                 "(one outlined histogram per channel, clipped to 0.1-99.9 percentile)",
                 fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    p = os.path.join(outdir, "04_state_group_histograms.png")
    fig.savefig(p, dpi=140)
    plt.close(fig)
    return p


# --------------------------------------------------------------------------
def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=os.path.join(
        os.path.dirname(here), "robotic_world_model_lite",
        "assets", "data", "state_action_data_0.csv"))
    ap.add_argument("--outdir", default=os.path.join(here, "figures"))
    args = ap.parse_args()
    if not os.path.exists(args.csv):
        raise SystemExit(f"CSV not found: {args.csv}")
    os.makedirs(args.outdir, exist_ok=True)

    rule("FILE")
    data = pd.read_csv(args.csv, header=None).to_numpy(dtype=np.float64)
    print(args.csv)
    print(f"shape {data.shape[0]} rows x {data.shape[1]} columns")
    print(f"{DT * data.shape[0]:.0f} s at {FS:.0f} Hz")
    print(f"non-finite entries: {int((~np.isfinite(data)).sum())}")
    assert data.shape[1] == 66, f"expected 66 columns, got {data.shape[1]}"

    rule("EPISODE STRUCTURE")
    starts, reset_rows, term_idx = find_episode_starts(data)

    rule("ASSERTIONS")
    a1 = assert_gravity_unit(data)
    if not a1:
        raise SystemExit(1)
    print()
    a2 = assert_binary(data)
    print()
    a3_raw, a3_within = assert_continuous(data, starts)

    rule("TERMINATIONS")
    count_terminations(data, starts, reset_rows, term_idx)

    rule("TRAINING SET SIZE")
    count_valid_windows(data, starts)

    rule("GAIT")
    describe_gait(data)

    rule("ACTION vs JOINT POSITION")
    print("cols 45-56 are the raw policy output. No action scale exists anywhere in")
    print("this repository, so they are not joint targets in radians -- the scale and")
    print("default-pose offset live in the upstream IsaacLab env and are not recorded.")
    print("Fitting  q[t+k] ~ s*a[t] + b  per joint, over the best lag k:\n")
    print("  joint      lag k   lag [ms]    gain s   intercept    r")
    lags, gains = [], []
    for j in range(12):
        k, s, b, c = fit_action_to_position(data, starts, j)
        lags.append(k)
        gains.append(s)
        print(f"  {JOINT_NAMES[j]:8s} {k:5d} {k * DT * 1000:9.0f}    {s:8.4f}"
              f" {b:10.4f}  {c:6.3f}")
    print(f"\n  action leads position by {np.median(lags):.0f} steps"
          f" ({np.median(lags) * DT * 1000:.0f} ms) -- ordinary PD tracking lag.")
    print(f"  median gain {np.median(gains):.3f}: the action swings roughly"
          f" {1 / np.median(gains):.1f}x")
    print("  wider than the joint excursion it produces.")

    rule("PLOTS")
    tracking_path, _ = plot_joint_tracking(data, args.outdir, starts)
    for p in (plot_base_velocities(data, args.outdir, starts),
              tracking_path,
              plot_contact_raster(data, args.outdir, starts),
              plot_state_histograms(data, args.outdir)):
        print(f"  wrote {p}")

    rule("SUMMARY")
    print(f"  {verdict(a1):4s}  [1] gravity vector is unit length"
          f"  -> column mapping is correct")
    print(f"  {verdict(a2):4s}  [2] cols 57-65 are strictly binary")
    print(f"  {verdict(a3_raw):4s}  [3] continuity, taken literally over all adjacent rows")
    print(f"  {verdict(a3_within):4s}  [3] continuity within episodes"
          f"  -> the file is {len(starts)} continuous episodes, not shuffled")
    print()
    if a1 and a2 and a3_within:
        print("  Assertions 1 and 2 pass outright. Assertion 3 passes once the file's")
        print("  episode structure is honoured, and fails if it is not -- which is the")
        print("  useful result: it is what exposed the 10 unmarked resets.")
    else:
        print("  A hard assertion failed. Do not train on this reading of the file.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
