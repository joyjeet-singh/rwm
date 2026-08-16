"""
Step 4 / 0a -- restate the Step 3 results under the causal convention.

Every Step 3 number was computed at action_offset=0, which D-13 established is
the stale alignment. This reruns the whole Step 3 battery at action_offset=1 and
reports both side by side.

The framing is deliberate and is NOT "we corrected our earlier numbers":

    offset 1  = what the reference checkpoint can actually do
    offset 0  = what the released evaluation code reports
    the gap   = the measured cost of B-05

Both are real; they answer different questions. The offset-0 column stays in the
ledger permanently because it is what the released code produces.

Also re-tests the two qualitative conclusions that could in principle flip:
  R-05  boundary crossing does not explain the A/B gap
  D-12  per-episode difficulty spans ~3x and is uncorrelated with commanded speed
"""

import json
import os

import numpy as np
import torch

import rwm_data as R
import rollout_eval as E
import rwm_metrics as MET
import score_reference as S

OFFSETS = (0, 1)
LABEL = {0: "offset 0 (released eval)", 1: "offset 1 (causal)"}


def rollout_for(model, data, idx, cfg, offset):
    raw = data[idx]
    st = torch.as_tensor(R.normalise_state(raw[:, :, R.STATE_COLS],
                                           cfg["state_data_mean"], cfg["state_data_std"]),
                         dtype=torch.float32)
    ac = torch.as_tensor(raw[:, :, R.ACTION_COLS], dtype=torch.float32)
    pred, *_ = model.rollout(st, ac, E.START_STEP, action_offset=offset)
    return pred, st


def per_traj_e(pred, true, start=E.START_STEP):
    num = (pred[:, start:] - true[:, start:]).abs().sum(-1)
    den = true[:, start:].abs().sum(-1)
    return (num / den).mean(dim=1)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    data, episode_id = R.load_data(paths["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(here, "step0_strat.json"),
                         verbose=False)
    base_cfg = E.build_base_config(cfg, seed=0)
    sd = torch.load(paths["ckpt"], map_location="cpu")["system_dynamics_state_dict"]
    model = S.ReferenceRWM(sd)

    scale = MET.training_scale(data, episode_id, split["train_episodes"],
                               cfg["state_data_mean"], cfg["state_data_std"])

    print("=" * 82)
    print("STEP 4 / 0a -- STEP 3 RESULTS RESTATED UNDER THE CAUSAL CONVENTION")
    print("=" * 82)
    print(f"  held-out episodes {split['holdout_episodes']}, "
          f"training {split['train_episodes']}")
    print(f"\n  0b nRMSE fixed scale (std of normalised dims over training episodes):")
    print(f"    min {scale.min():.4f}  median {np.median(scale):.4f}  max {scale.max():.4f}")
    for name, cols in (("v", R.LIN_VEL), ("omega", R.ANG_VEL), ("g", R.GRAVITY),
                       ("q", R.JOINT_POS), ("qdot", R.JOINT_VEL), ("tau", R.JOINT_TAU)):
        print(f"      {name:<6s} {np.array2string(scale[list(cols)][:3], precision=3)}"
              f"  (group mean {scale[list(cols)].mean():.3f})")

    out = {"nrmse_scale": scale.tolist(), "split": split}

    # ------------------------------------------------- protocols A and B
    res = {}
    for tag, cross in (("A", False), ("B", True)):
        for off in OFFSETS:
            r = E.evaluate(S.make_predict_fn(model, action_offset=off), data, split,
                           {**base_cfg, "episode_id": episode_id,
                            "allow_boundary_cross": cross})
            idx = E.sample_trajectories(episode_id, split["holdout_episodes"],
                                        seed=0, allow_boundary_cross=cross)
            pred, true = rollout_for(model, data, idx, cfg, off)
            curve, _ = MET.nrmse_per_step(pred, true, scale, E.START_STEP)
            r["nrmse"] = MET.summarise(curve)
            r["nrmse_curve"] = curve.tolist()
            res[(tag, off)] = r

    print("\n" + "-" * 82)
    print("PROTOCOL A AND B, CLEAN -- relative-L1 e, and nRMSE at h=368")
    print("-" * 82)
    print(f"  {'protocol':<12s} {'offset 0':>12s} {'offset 1':>12s} {'delta':>10s}"
          f" {'nRMSE off0':>12s} {'nRMSE off1':>12s}")
    for tag in ("A", "B"):
        e0, e1 = res[(tag, 0)]["clean"]["e"], res[(tag, 1)]["clean"]["e"]
        n0 = res[(tag, 0)]["nrmse"][368]
        n1 = res[(tag, 1)]["nrmse"][368]
        print(f"  {tag:<12s} {e0:>12.4f} {e1:>12.4f} {e1-e0:>+10.4f}"
              f" {n0:>12.4f} {n1:>12.4f}")
    print(f"\n  crossing trajectories in B: "
          f"{res[('B',1)]['n_trajectories_crossing_boundary']} of 10")

    # --------------------------------------------------------- noise sweep
    print("\n" + "-" * 82)
    print("NOISE SWEEP, BOTH PROTOCOLS AND BOTH CONVENTIONS (relative-L1 e)")
    print("-" * 82)
    print(f"  {'noise':>7s} | {'A off0':>9s} {'A off1':>9s} | {'B off0':>9s} {'B off1':>9s}")
    print("  " + "-" * 60)
    print(f"  {'clean':>7s} | {res[('A',0)]['clean']['e']:>9.4f} "
          f"{res[('A',1)]['clean']['e']:>9.4f} | {res[('B',0)]['clean']['e']:>9.4f} "
          f"{res[('B',1)]['clean']['e']:>9.4f}")
    for ns in cfg["eval_traj_noise_scale"]:
        k = str(ns)
        print(f"  {ns:>7} | {res[('A',0)]['noise'][k]['e']:>9.4f} "
              f"{res[('A',1)]['noise'][k]['e']:>9.4f} | "
              f"{res[('B',0)]['noise'][k]['e']:>9.4f} "
              f"{res[('B',1)]['noise'][k]['e']:>9.4f}")
    mono = {}
    for tag in ("A", "B"):
        for off in OFFSETS:
            seq = [res[(tag, off)]["clean"]["e"]] + \
                  [res[(tag, off)]["noise"][str(n)]["e"] for n in cfg["eval_traj_noise_scale"]]
            mono[(tag, off)] = all(seq[i] < seq[i + 1] for i in range(len(seq) - 1))
    print(f"\n  monotonic in noise?  " + "   ".join(
        f"{t} off{o}: {mono[(t,o)]}" for t in ("A", "B") for o in OFFSETS))
    print("  (R-07 recorded B as non-monotonic; check whether the convention changes that)")

    # --------------------------------------------------------- 20-seed spread
    print("\n" + "-" * 82)
    print("20-SEED SPREAD (M-04)")
    print("-" * 82)
    stab = {}
    for tag, cross in (("A", False), ("B", True)):
        for off in OFFSETS:
            es = []
            for s in range(20):
                r = E.evaluate(S.make_predict_fn(model, action_offset=off), data, split,
                               {**base_cfg, "episode_id": episode_id, "seed": s,
                                "allow_boundary_cross": cross, "noise_scales": []})
                es.append(r["clean"]["e"])
            es = np.array(es)
            stab[(tag, off)] = {"mean": float(es.mean()), "std": float(es.std()),
                                "min": float(es.min()), "max": float(es.max())}
            print(f"  protocol {tag} {LABEL[off]:<26s} e = {es.mean():.4f} +- {es.std():.4f}"
                  f"  (min {es.min():.4f}, max {es.max():.4f})")
    for off in OFFSETS:
        sep = abs(stab[("A", off)]["mean"] - stab[("B", off)]["mean"])
        pooled = np.hypot(stab[("A", off)]["std"], stab[("B", off)]["std"])
        print(f"    offset {off}: A-B separation {sep:.4f} vs pooled spread {pooled:.4f}"
              f"  -> {sep/pooled:.1f} sigma")

    # ------------------------------------------- R-05 crossing vs non-crossing
    print("\n" + "-" * 82)
    print("R-05 RETEST -- does boundary crossing explain the A/B gap?")
    print("-" * 82)
    r05 = {}
    for off in OFFSETS:
        idx = E.sample_trajectories(episode_id, split["holdout_episodes"], seed=0,
                                    allow_boundary_cross=True)
        pred, true = rollout_for(model, data, idx, cfg, off)
        pe = per_traj_e(pred, true).numpy()
        crossed = np.array([len(set(episode_id[row].tolist())) > 1 for row in idx])
        ec, en = float(pe[crossed].mean()), float(pe[~crossed].mean())
        r05[off] = {"e_crossing": ec, "e_non_crossing": en,
                    "crossing_worse": bool(ec > en)}
        print(f"  {LABEL[off]:<26s} crossing {ec:.4f}  non-crossing {en:.4f}"
              f"  -> crossing is {'WORSE' if ec > en else 'BETTER'}")
    survives_r05 = (not r05[0]["crossing_worse"]) and (not r05[1]["crossing_worse"])
    print(f"\n  R-05 conclusion ('crossing does not explain the gap') "
          f"{'SURVIVES' if survives_r05 else 'FLIPS -- REPORT LOUDLY'}")

    # ------------------------------------------------ D-12 per-episode difficulty
    print("\n" + "-" * 82)
    print("D-12 RETEST -- per-episode difficulty")
    print("-" * 82)
    with open(os.path.join(here, "step0_strat.json")) as f:
        speeds = {int(k): v["mean_speed"] for k, v in json.load(f).items()}
    ep_e = {0: {}, 1: {}}
    print(f"  {'ep':>3s} {'speed':>7s} {'e off0':>9s} {'e off1':>9s} {'nRMSE off1':>11s}")
    for e_i in range(R.N_EPISODES):
        idx = E.sample_trajectories(episode_id, [e_i], n_traj=20, seed=7)
        row = []
        for off in OFFSETS:
            pred, true = rollout_for(model, data, idx, cfg, off)
            v = float(per_traj_e(pred, true).mean())
            ep_e[off][e_i] = v
            row.append(v)
        curve, _ = MET.nrmse_per_step(pred, true, scale, E.START_STEP)
        print(f"  {e_i:>3d} {speeds[e_i]:>7.2f} {row[0]:>9.4f} {row[1]:>9.4f}"
              f" {curve.mean():>11.4f}")
    d12 = {}
    for off in OFFSETS:
        v = np.array([ep_e[off][i] for i in range(R.N_EPISODES)])
        sp = np.array([speeds[i] for i in range(R.N_EPISODES)])
        corr = float(np.corrcoef(sp, v)[0, 1])
        d12[off] = {"min": float(v.min()), "max": float(v.max()),
                    "ratio": float(v.max() / v.min()), "corr_with_speed": corr,
                    "holdout_mean": float(np.mean([ep_e[off][i]
                                                   for i in split["holdout_episodes"]])),
                    "all_mean": float(v.mean())}
        print(f"\n  {LABEL[off]:<26s} spread {v.min():.3f}-{v.max():.3f}"
              f"  ({v.max()/v.min():.1f}x)   corr with speed r = {corr:+.2f}")
        print(f"    held-out pair mean {d12[off]['holdout_mean']:.3f}"
              f" vs population {d12[off]['all_mean']:.3f}")
    survives_d12 = (d12[1]["ratio"] > 2.0) and (abs(d12[1]["corr_with_speed"]) < 0.3)
    print(f"\n  D-12 conclusion (~3x spread, uncorrelated with speed) "
          f"{'SURVIVES' if survives_d12 else 'FLIPS -- REPORT LOUDLY'}")

    out.update({
        "protocols": {f"{t}_off{o}": {"e": res[(t, o)]["clean"]["e"],
                                      "median_r": res[(t, o)]["clean"]["median_r"],
                                      "frac_r_gt_10": res[(t, o)]["clean"]["frac_r_gt_10"],
                                      "nrmse": res[(t, o)]["nrmse"],
                                      "noise": {k: res[(t, o)]["noise"][k]["e"]
                                                for k in res[(t, o)]["noise"]}}
                      for t in ("A", "B") for o in OFFSETS},
        "seed_spread": {f"{t}_off{o}": stab[(t, o)] for t in ("A", "B") for o in OFFSETS},
        "noise_monotonic": {f"{t}_off{o}": mono[(t, o)] for t in ("A", "B") for o in OFFSETS},
        "r05_retest": r05, "r05_survives": survives_r05,
        "d12_retest": d12, "d12_survives": survives_d12,
        "per_episode_e": {str(o): ep_e[o] for o in OFFSETS},
    })
    with open(os.path.join(here, "step4_0a_results.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(f"\n  wrote step4_0a_results.json")
    return out


if __name__ == "__main__":
    main()
