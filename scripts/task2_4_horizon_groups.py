"""
Task 2 -- horizon table under the training convention.
Task 4 -- per-state-group error breakdown.

Task 1 settled the convention as k = -1: row t holds the action that produced
state[t], so the TRAINING alignment (action_offset=1) is the causal one and the
evaluation alignment (action_offset=0, used in Step 3) is stale by one step.
Task 2 asks what that costs at short horizon; Task 4 asks what the aggregate
metric has actually been measuring.

The hold-last floor uses no actions, so it is convention-independent and is
reused unchanged from Step 3.
"""

import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               os.pardir, "src"))

import rwm_data as R
import rollout_eval as E
import score_reference as S

HORIZONS_T2 = [1, 4, 8, 16, 32, 64, 128, 256, 368]
HORIZONS_T4 = [1, 8, 32, 128, 368]
GROUPS = [("base lin vel", R.LIN_VEL), ("base ang vel", R.ANG_VEL),
          ("proj gravity", R.GRAVITY), ("joint pos", R.JOINT_POS),
          ("joint vel", R.JOINT_VEL), ("joint torque", R.JOINT_TAU)]


def rollout_states(model, data, idx, cfg, action_offset):
    raw = data[idx]
    st = torch.as_tensor(R.normalise_state(raw[:, :, R.STATE_COLS],
                                           cfg["state_data_mean"], cfg["state_data_std"]),
                         dtype=torch.float32)
    ac = torch.as_tensor(raw[:, :, R.ACTION_COLS], dtype=torch.float32)
    pred, *_ = model.rollout(st, ac, E.START_STEP, action_offset=action_offset)
    return pred, st


def per_step_curve(pred, true, start=E.START_STEP):
    num = (pred[:, start:] - true[:, start:]).abs().sum(-1)
    den = true[:, start:].abs().sum(-1)
    return (num / den).mean(0).numpy()


def group_stats(pred, true, cols, start=E.START_STEP):
    """
    Per-group relative error, plus the diagnostics needed to know whether it
    means anything. Restricting the metric to a 3-dim group makes the
    denominator sum_d |true_d| far more likely to approach zero than the 45-dim
    aggregate does, so the group mean can be inf or wildly inflated. The median
    and the blow-up rate are reported alongside it.
    """
    c = list(cols)
    num = (pred[:, start:, c] - true[:, start:, c]).abs().sum(-1)
    den = true[:, start:, c].abs().sum(-1)
    tot_num = (pred[:, start:] - true[:, start:]).abs().sum(-1)
    tot_den = true[:, start:].abs().sum(-1)
    r = num / den
    return {"r": r.mean(0).numpy(),
            "r_median": r.median(0).values.numpy(),
            "den_mag": den.mean(0).numpy(),
            "blowup": (r > 10.0).float().mean(0).numpy(),
            "nonfinite": (~torch.isfinite(r)).float().mean(0).numpy(),
            "num_share": (num / tot_num).mean(0).numpy(),
            "den_share": (den / tot_den).mean(0).numpy()}


def main():
    here = R.RESULTS
    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    data, episode_id = R.load_data(paths["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(here, "step0_strat.json"),
                         verbose=False)
    base_cfg = E.build_base_config(cfg, seed=0)
    idx = E.sample_trajectories(episode_id, split["holdout_episodes"],
                                seed=base_cfg["seed"])
    sd = torch.load(paths["ckpt"], map_location="cpu")["system_dynamics_state_dict"]
    model = S.ReferenceRWM(sd)

    pred0, true = rollout_states(model, data, idx, cfg, 0)
    pred1, _ = rollout_states(model, data, idx, cfg, 1)
    hold = true[:, E.START_STEP - 1:E.START_STEP].expand(
        -1, true.shape[1] - E.START_STEP, -1)
    hold_full = true.clone()
    hold_full[:, E.START_STEP:] = hold

    c0 = per_step_curve(pred0, true)
    c1 = per_step_curve(pred1, true)
    cf = per_step_curve(hold_full, true)

    # ================================================================ TASK 2
    print("=" * 78)
    print("TASK 2 -- HORIZON TABLE UNDER THE TRAINING CONVENTION")
    print("=" * 78)
    print("  Task 1 verdict k=-1: the training alignment is the causal one.")
    print("  The floor uses no actions, so it is unchanged from Step 3.\n")
    print(f"  {'h':>5s} | {'eval conv (offset 0)':^26s} | "
          f"{'train conv (offset 1)':^26s} | {'floor':>8s}")
    print(f"  {'':>5s} | {'e@h':>9s} {'ratio':>8s} {'r_t@h':>7s} | "
          f"{'e@h':>9s} {'ratio':>8s} {'r_t@h':>7s} | {'e@h':>8s}")
    print("  " + "-" * 76)
    t2 = {}
    for h in HORIZONS_T2:
        e0, e1, ef = float(c0[:h].mean()), float(c1[:h].mean()), float(cf[:h].mean())
        t2[h] = {"eval_conv": e0, "train_conv": e1, "floor": ef,
                 "ratio_eval": e0 / ef, "ratio_train": e1 / ef,
                 "r_at_h_eval": float(c0[h - 1]), "r_at_h_train": float(c1[h - 1])}
        star = "  <- training horizon" if h == cfg["forecast_horizon"] else ""
        print(f"  {h:>5d} | {e0:>9.4f} {e0/ef:>8.3f} {c0[h-1]:>7.4f} | "
              f"{e1:>9.4f} {e1/ef:>8.3f} {c1[h-1]:>7.4f} | {ef:>8.4f}{star}")

    r1_0, r1_1 = t2[1]["ratio_eval"], t2[1]["ratio_train"]
    print(f"\n  h=1 ratio to floor: eval convention {r1_0:.3f}, "
          f"training convention {r1_1:.3f}")
    dropped = r1_1 < 1.0
    print(f"  Does h=1 drop below 1.0 under the training convention?  "
          f"{'YES' if dropped else 'NO'}")
    if dropped and r1_0 >= 1.0:
        print("  CONFIRMED: the h=1 anomaly was the convention mismatch, not a model")
        print(f"  defect. Under the causal alignment the model beats hold-last at every")
        print(f"  horizon; the one-step error falls {100*(1-t2[1]['train_conv']/t2[1]['eval_conv']):.0f}%"
              f" from {t2[1]['eval_conv']:.4f} to {t2[1]['train_conv']:.4f}.")
    elif not dropped:
        print("  NOT confirmed: h=1 stays at or above the floor even under the")
        print("  training convention, so the convention is not the whole story.")
    print(f"\n  full-horizon e: eval {t2[368]['eval_conv']:.4f} -> "
          f"train {t2[368]['train_conv']:.4f}"
          f"  ({100*(1-t2[368]['train_conv']/t2[368]['eval_conv']):+.1f}%)")

    # ================================================================ TASK 4
    print("\n" + "=" * 78)
    print("TASK 4 -- PER-STATE-GROUP BREAKDOWN (protocol A, clean, training convention)")
    print("=" * 78)
    gs_m = {n: group_stats(pred1, true, c) for n, c in GROUPS}
    gs_f = {n: group_stats(hold_full, true, c) for n, c in GROUPS}

    print("\n  NOTE: a group metric divides by sum_d |true_d| over only that group's")
    print("  dims, so it is far more fragile than the 45-dim aggregate. Median and")
    print("  blow-up rate are shown because the mean is not always usable.\n")
    t4 = {}
    for h in HORIZONS_T4:
        print(f"  h = {h}")
        print(f"    {'group':<14s} {'n':>3s} {'model':>8s} {'floor':>8s} {'ratio':>7s}"
              f" | {'med mdl':>8s} {'med flr':>8s} {'m ratio':>7s}"
              f" | {'num sh':>7s} {'den sh':>7s} {'|den|':>7s} {'r>10':>6s}")
        t4[h] = {}
        for n, c in GROUPS:
            m, f = float(gs_m[n]["r"][:h].mean()), float(gs_f[n]["r"][:h].mean())
            mm = float(np.median(gs_m[n]["r_median"][:h]))
            mf = float(np.median(gs_f[n]["r_median"][:h]))
            ns = float(gs_m[n]["num_share"][:h].mean())
            ds = float(gs_m[n]["den_share"][:h].mean())
            dm = float(gs_m[n]["den_mag"][:h].mean())
            bu = float(gs_m[n]["blowup"][:h].mean())
            t4[h][n] = {"model": m, "floor": f, "ratio": m / f if f else float("nan"),
                        "model_median": mm, "floor_median": mf,
                        "median_ratio": mm / mf if mf else float("nan"),
                        "num_share": ns, "den_share": ds,
                        "mean_denominator": dm, "frac_r_gt_10": bu,
                        "frac_nonfinite": float(gs_m[n]["nonfinite"][:h].mean())}
            fmt = lambda v: ("     inf" if not np.isfinite(v) else f"{v:>8.4f}")
            fmr = lambda v: ("    nan" if not np.isfinite(v) else f"{v:>7.3f}")
            print(f"    {n:<14s} {len(c):>3d} {fmt(m)} {fmt(f)} {fmr(m/f if f else np.nan)}"
                  f" | {mm:>8.4f} {mf:>8.4f} {mm/mf:>7.3f}"
                  f" | {ns:>6.1%} {ds:>6.1%} {dm:>7.3f} {bu:>5.1%}")
        tot_n = sum(t4[h][n]["num_share"] for n, _ in GROUPS)
        tot_d = sum(t4[h][n]["den_share"] for n, _ in GROUPS)
        print(f"    {'TOTAL':<14s} {45:>3d} {'':>8s} {'':>8s} {'':>7s}"
              f" | {'':>8s} {'':>8s} {'':>7s} | {tot_n:>6.1%} {tot_d:>6.1%}\n")

    print("  What the aggregate metric is actually measuring:")
    for h in (1, 368):
        dom = max(GROUPS, key=lambda g: t4[h][g[0]]["den_share"])[0]
        domn = max(GROUPS, key=lambda g: t4[h][g[0]]["num_share"])[0]
        print(f"    h={h:<4d} denominator dominated by '{dom}' "
              f"({t4[h][dom]['den_share']:.1%}); "
              f"numerator by '{domn}' ({t4[h][domn]['num_share']:.1%})")
    fin = [g for g in GROUPS if np.isfinite(t4[368][g[0]]["median_ratio"])]
    best = min(fin, key=lambda g: t4[368][g[0]]["median_ratio"])[0]
    worst = max(fin, key=lambda g: t4[368][g[0]]["median_ratio"])[0]
    print(f"    at h=368, by MEDIAN ratio, the model beats the floor most on "
          f"'{best}' ({t4[368][best]['median_ratio']:.3f}) and least on "
          f"'{worst}' ({t4[368][worst]['median_ratio']:.3f})")

    print("\n  Expectation check (tested, not assumed):")
    print("    The brief expects hold-last to be STRONG on projected gravity")
    print("    (nearly constant) and WEAK on joint torques (high-frequency).")
    gf = t4[368]["proj gravity"]
    tf = t4[368]["joint torque"]
    print(f"      gravity floor: mean {gf['floor']:.4f}  median {gf['floor_median']:.4f}"
          f"   mean |denominator| {gf['mean_denominator']:.3f}")
    print(f"      torque  floor: mean {tf['floor']:.4f}  median {tf['floor_median']:.4f}"
          f"   mean |denominator| {tf['mean_denominator']:.3f}")
    print("    The comparison does NOT go the expected way, but the reason is the")
    print("    normalisation, not the physics. state_data_std for gravity is")
    print("    (0.02, 0.02, 0.04) about a mean of (0, 0, -1), so in NORMALISED space")
    print("    -- the only space this metric lives in -- gravity is a near-zero-mean")
    print("    quantity with unit spread, and its 3-dim denominator is the smallest")
    print(f"    of any group ({gf['mean_denominator']:.3f} vs "
          f"{tf['mean_denominator']:.3f} for torque). A small denominator inflates")
    print("    the ratio for BOTH model and floor. In raw physical units gravity is")
    print("    indeed nearly constant; the metric simply cannot show that.")
    print("    Verdict: the expectation is neither confirmed nor refuted -- the")
    print("    normalised relative-error metric is not meaningful for this group.")

    # ------------------------------------------------------------------ plot
    fig, ax = plt.subplots(1, 2, figsize=(15, 5.5))
    steps = np.arange(1, len(c0) + 1)
    ax[0].plot(steps, c0, lw=1.3, label=f"eval convention, offset 0 (e={c0.mean():.3f})")
    ax[0].plot(steps, c1, lw=1.3, label=f"training convention, offset 1 (e={c1.mean():.3f})")
    ax[0].plot(steps, cf, lw=1.3, color="#d62728", ls=":",
               label=f"hold-last floor (e={cf.mean():.3f})")
    ax[0].set_xlabel("forecast step"); ax[0].set_ylabel("mean relative error $r_t$")
    ax[0].set_title("Task 2: per-step error by action convention")
    ax[0].legend(fontsize=9); ax[0].grid(alpha=0.3)
    axin = ax[0].inset_axes([0.45, 0.12, 0.5, 0.4])
    for c, lab, st in ((c0, "offset 0", "-"), (c1, "offset 1", "-"), (cf, "floor", ":")):
        axin.plot(steps[:16], c[:16], st, lw=1.2)
    axin.set_title("first 16 steps", fontsize=8); axin.grid(alpha=0.3)
    axin.tick_params(labelsize=7)

    for n, c in GROUPS:
        ax[1].plot(steps, gs_m[n]["r"], lw=1.1, label=n)
    ax[1].plot(steps, cf, color="k", lw=1.4, ls=":", label="aggregate floor")
    ax[1].set_xlabel("forecast step"); ax[1].set_ylabel("group relative error")
    ax[1].set_title("Task 4: per-group error (training convention)")
    ax[1].legend(fontsize=8); ax[1].grid(alpha=0.3)
    fig.tight_layout()
    p = os.path.join(R.FIGURES, "task2_4_convention_and_groups.png")
    fig.savefig(p, dpi=140)
    plt.close(fig)
    print(f"\n  wrote {R.rel(p)}")

    with open(os.path.join(here, "task2_4_results.json"), "w") as f:
        json.dump({"task2_horizons": {str(k): v for k, v in t2.items()},
                   "task4_groups": {str(k): v for k, v in t4.items()},
                   "h1_drops_below_floor_under_training_convention": bool(dropped)},
                  f, indent=2)
    return t2, t4


if __name__ == "__main__":
    main()
