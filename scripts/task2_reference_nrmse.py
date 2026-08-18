"""
Task 2 -- the released checkpoint under nRMSE.

Every published comparison against the released checkpoint has used relative-L1, the paper's
metric. Its nRMSE has never been computed. R-20 showed the two metrics INVERT the
model-versus-floor ordering at h=1, and R-22 showed Arm A beating the floor on relative-L1 at
h=368 while losing to it on nRMSE. So the question is whether that pattern attaches to our
undertrained reproduction or to the released artifact itself.

The scale vector is the SAME fixed one the training runs used, derived from the training
episodes only. It is recomputed here by the same deterministic function and cross-checked
against the stored copy; it is never derived from the evaluation set.
"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np, torch
import rwm_data as R, rollout_eval as E, rwm_metrics as MET, score_reference as S

HOR = (1, 4, 8, 16, 32, 64, 128, 256, 368)
GROUPS = [("base lin vel", R.LIN_VEL), ("base ang vel", R.ANG_VEL),
          ("proj gravity", R.GRAVITY), ("joint pos", R.JOINT_POS),
          ("joint vel", R.JOINT_VEL), ("joint torque", R.JOINT_TAU)]

def main():
    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    data, ep = R.load_data(paths["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"), verbose=False)
    base = E.build_base_config(cfg, seed=0)

    scale = MET.training_scale(data, ep, split["train_episodes"],
                               cfg["state_data_mean"], cfg["state_data_std"])
    stored = np.array(json.load(open(os.path.join(R.RESULTS, "step4_0a_results.json")))["nrmse_scale"])
    assert np.allclose(scale, stored), "scale vector differs from the stored one"
    print("=" * 88)
    print("TASK 2 -- THE RELEASED CHECKPOINT UNDER nRMSE")
    print("=" * 88)
    print(f"  scale vector: identical to the stored training-episode vector "
          f"(max abs diff {np.abs(scale-stored).max():.2e})")
    print(f"  protocol A, held-out episodes {split['holdout_episodes']}, action_offset=1\n")

    sd = torch.load(paths["ckpt"], map_location="cpu")["system_dynamics_state_dict"]
    model = S.ReferenceRWM(sd)

    idx = E.sample_trajectories(ep, split["holdout_episodes"], seed=0)
    raw = data[idx]
    st = torch.as_tensor(R.normalise_state(raw[:, :, R.STATE_COLS],
                                           cfg["state_data_mean"], cfg["state_data_std"]),
                         dtype=torch.float32)
    ac = torch.as_tensor(raw[:, :, R.ACTION_COLS], dtype=torch.float32)
    pred, *_ = model.rollout(st.clone(), ac, E.START_STEP, action_offset=1)
    hold = st.clone()
    hold[:, E.START_STEP:] = st[:, E.START_STEP-1:E.START_STEP].expand(-1, st.shape[1]-E.START_STEP, -1)

    def l1(p):
        n = (p[:, E.START_STEP:] - st[:, E.START_STEP:]).abs().sum(-1)
        d = st[:, E.START_STEP:].abs().sum(-1)
        return (n/d).mean(0).numpy()
    e_m, e_f = l1(pred), l1(hold)
    n_m, _ = MET.nrmse_per_step(pred, st, scale, E.START_STEP)
    n_f, _ = MET.nrmse_per_step(hold, st, scale, E.START_STEP)

    print(f"  {'h':>4s} | {'e model':>9s} {'e floor':>9s} {'ratio':>7s} | "
          f"{'nRMSE mdl':>10s} {'nRMSE flr':>10s} {'ratio':>7s} | verdict")
    print("  " + "-"*84)
    rows = {}
    for h in HOR:
        em, ef = float(e_m[:h].mean()), float(e_f[:h].mean())
        nm, nf = float(n_m[:h].mean()), float(n_f[:h].mean())
        v = ("both beat floor" if em < ef and nm < nf else
             "both lose" if em > ef and nm > nf else "*** METRICS DISAGREE ***")
        rows[h] = {"e": em, "e_floor": ef, "e_ratio": em/ef,
                   "nrmse": nm, "nrmse_floor": nf, "nrmse_ratio": nm/nf, "verdict": v}
        print(f"  {h:>4d} | {em:>9.4f} {ef:>9.4f} {em/ef:>7.3f} | "
              f"{nm:>10.4f} {nf:>10.4f} {nm/nf:>7.3f} | {v}")

    print("\n" + "="*88)
    r368 = rows[368]
    below = r368["nrmse"] < r368["nrmse_floor"]
    print(f"  THE QUESTION: is the released checkpoint above or below the nRMSE floor at h=368?")
    print(f"    nRMSE model {r368['nrmse']:.4f}   nRMSE floor {r368['nrmse_floor']:.4f}"
          f"   ratio {r368['nrmse_ratio']:.3f}")
    print(f"    ANSWER: {'BELOW the floor -- it BEATS it' if below else 'ABOVE the floor -- it LOSES to it'}"
          f" by {abs(1-r368['nrmse_ratio'])*100:.1f}%")
    print(f"    (relative-L1 for comparison: {r368['e']:.4f} vs {r368['e_floor']:.4f},"
          f" beats by {(1-r368['e_ratio'])*100:.1f}%)")
    print("="*88)

    print("\n  per-group breakdown (median relative-L1, blow-up rate, nRMSE)")
    grp = {}
    for h in (1, 8, 368):
        print(f"\n    h={h}")
        grp[h] = {}
        ng = MET.nrmse_groups(pred, st, scale, E.START_STEP)
        ngf = MET.nrmse_groups(hold, st, scale, E.START_STEP)
        for name, cols in GROUPS:
            c = list(cols)
            num = (pred[:, E.START_STEP:, c] - st[:, E.START_STEP:, c]).abs().sum(-1)
            den = st[:, E.START_STEP:, c].abs().sum(-1)
            r = num/den
            med = float(r.median(0).values[:h].median())
            bu = float((r > 10.0).float().mean(0)[:h].mean())
            grp[h][name] = {"median_l1": med, "frac_r_gt_10": bu,
                            "nrmse": float(ng[name][:h].mean()),
                            "nrmse_floor": float(ngf[name][:h].mean())}
            print(f"      {name:<14s} med-L1 {med:>7.4f}  r>10 {bu:>5.1%}"
                  f"  nRMSE {ng[name][:h].mean():>7.4f} (floor {ngf[name][:h].mean():>7.4f})")

    out = {"scale_matches_stored": True, "horizons": rows, "groups": grp,
           "below_nrmse_floor_at_368": bool(below),
           "n_trajectories": 10}
    p = os.path.join(R.RESULTS, "task2_reference_nrmse.json")
    json.dump(out, open(p, "w"), indent=2)
    print(f"\n  wrote {R.rel(p)}")

main()
