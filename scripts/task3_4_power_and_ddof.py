"""
Task 3 -- fix the evaluation power problem instead of living with it.
Task 4 -- statistical hygiene: ddof=1 everywhere.

M-04 recorded protocol A varying by +-0.053 over evaluation seeds alone. That is sampling
noise from 10 trajectories, which is the reference's choice, not a constraint: the two
held-out episodes contain 1,202 valid non-crossing 400-step start points.

Every existing checkpoint is re-evaluated at 100 trajectories. No retraining. The
10-trajectory numbers stay in the ledger -- they are what the reference protocol yields, and
the difference between the two is itself the methodological result.

All spreads over seeds are reported with ddof=1 (Task 4).
"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np, torch
import rwm_data as R, rollout_eval as E, rwm_metrics as MET, score_reference as S, rwm_model as M

N_BIG = 100
ARMS, SEEDS, CKPTS = ("A", "B"), (0, 1, 2), (500, 2500)

def rollout_eval_at(model, data, ep, split, cfg, scale, n_traj, seed=0, offset=1):
    idx = E.sample_trajectories(ep, split["holdout_episodes"], n_traj=n_traj,
                                len_traj=400, seed=seed)
    raw = data[idx]
    st = torch.as_tensor(R.normalise_state(raw[:, :, R.STATE_COLS],
                                           cfg["state_data_mean"], cfg["state_data_std"]),
                         dtype=torch.float32)
    ac = torch.as_tensor(raw[:, :, R.ACTION_COLS], dtype=torch.float32)
    pred = model.rollout(st.clone(), ac, E.START_STEP, action_offset=offset)
    if isinstance(pred, tuple): pred = pred[0]
    hold = st.clone()
    hold[:, E.START_STEP:] = st[:, E.START_STEP-1:E.START_STEP].expand(-1, 400-E.START_STEP, -1)
    def l1(p):
        n = (p[:, E.START_STEP:] - st[:, E.START_STEP:]).abs().sum(-1)
        d = st[:, E.START_STEP:].abs().sum(-1)
        return (n/d).mean(0).numpy()
    nm, _ = MET.nrmse_per_step(pred, st, scale, E.START_STEP)
    nf, _ = MET.nrmse_per_step(hold, st, scale, E.START_STEP)
    return {"e": l1(pred), "e_floor": l1(hold), "nrmse": nm, "nrmse_floor": nf}

def main():
    paths = R.repo_paths(); cfg = R.load_reference_config(paths["lite"])
    data, ep = R.load_data(paths["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"), verbose=False)
    base = E.build_base_config(cfg, seed=0)
    scale = MET.training_scale(data, ep, split["train_episodes"],
                               cfg["state_data_mean"], cfg["state_data_std"])
    out = {"n_trajectories": N_BIG, "ddof": 1}

    print("="*90); print("TASK 3 -- RE-EVALUATION AT 100 TRAJECTORIES  (Task 4: ddof=1 throughout)"); print("="*90)
    print(f"  pool: 1,202 valid non-crossing 400-step starts in episodes {split['holdout_episodes']}")

    # ---- 3a: M-04's 20-seed experiment, at 10 and at 100 -------------------
    print("\n" + "-"*90); print("  M-04 REVISITED -- evaluation-seed spread at 10 vs 100 trajectories"); print("-"*90)
    sd_ref = torch.load(paths["ckpt"], map_location="cpu")["system_dynamics_state_dict"]
    ref = S.ReferenceRWM(sd_ref)
    m04 = {}
    for n in (10, N_BIG):
        es, ns = [], []
        for s in range(20):
            r = rollout_eval_at(ref, data, ep, split, cfg, scale, n, seed=s)
            es.append(float(r["e"].mean())); ns.append(float(r["nrmse"].mean()))
        es, ns = np.array(es), np.array(ns)
        m04[n] = {"e_mean": float(es.mean()), "e_sd": float(es.std(ddof=1)),
                  "nrmse_mean": float(ns.mean()), "nrmse_sd": float(ns.std(ddof=1))}
        print(f"    {n:>3d} traj, 20 eval seeds: e {es.mean():.4f} +- {es.std(ddof=1):.4f}"
              f"   nRMSE {ns.mean():.4f} +- {ns.std(ddof=1):.4f}")
    shrink_e = m04[10]["e_sd"]/m04[N_BIG]["e_sd"]
    shrink_n = m04[10]["nrmse_sd"]/m04[N_BIG]["nrmse_sd"]
    print(f"    spread shrinks {shrink_e:.2f}x on e, {shrink_n:.2f}x on nRMSE"
          f"   (sqrt(10) = {np.sqrt(10):.2f} would be pure sampling)")
    out["m04"] = {"by_n": m04, "shrink_e": shrink_e, "shrink_nrmse": shrink_n}

    # ---- 3b: every checkpoint at 100 traj ---------------------------------
    print("\n" + "-"*90); print("  ALL CHECKPOINTS AT 100 TRAJECTORIES"); print("-"*90)
    res = {}
    for a in ARMS:
        for s in SEEDS:
            for c in CKPTS:
                w = os.path.join(R.REPO_ROOT, "runs", f"arm{a}_seed{s}", f"weights_{c}.pt")
                m = M.build_from_config(cfg, ensemble_size=1)
                m.load_state_dict(torch.load(w, map_location="cpu")["model_state_dict"], strict=True)
                m.eval()
                r = rollout_eval_at(m, data, ep, split, cfg, scale, N_BIG)
                res[f"{a}{s}@{c}"] = {h: {"e": float(r["e"][:h].mean()),
                                          "nrmse": float(r["nrmse"][:h].mean())}
                                      for h in (1, 8, 368)}
                print(f"    arm{a} seed{s} @{c}:  e@8 {r['e'][:8].mean():.4f}"
                      f"  e@368 {r['e'].mean():.4f}"
                      f"  nRMSE@8 {r['nrmse'][:8].mean():.4f}  nRMSE@368 {r['nrmse'].mean():.4f}")
    rr = rollout_eval_at(ref, data, ep, split, cfg, scale, N_BIG)
    floor = {h: {"e": float(rr["e_floor"][:h].mean()), "nrmse": float(rr["nrmse_floor"][:h].mean())}
             for h in (1, 8, 368)}
    res["released"] = {h: {"e": float(rr["e"][:h].mean()), "nrmse": float(rr["nrmse"][:h].mean())}
                       for h in (1, 8, 368)}
    res["floor"] = floor
    print(f"    released      :  e@8 {rr['e'][:8].mean():.4f}  e@368 {rr['e'].mean():.4f}"
          f"  nRMSE@8 {rr['nrmse'][:8].mean():.4f}  nRMSE@368 {rr['nrmse'].mean():.4f}")
    print(f"    hold-last floor: e@8 {floor[8]['e']:.4f}  e@368 {floor[368]['e']:.4f}"
          f"  nRMSE@8 {floor[8]['nrmse']:.4f}  nRMSE@368 {floor[368]['nrmse']:.4f}")
    print(f"\n    released vs floor at h=368 (100 traj): "
          f"e {res['released'][368]['e']:.4f} vs {floor[368]['e']:.4f}"
          f" | nRMSE {res['released'][368]['nrmse']:.4f} vs {floor[368]['nrmse']:.4f}"
          f"  -> {'BEATS' if res['released'][368]['nrmse'] < floor[368]['nrmse'] else 'LOSES TO'} the nRMSE floor")
    out["checkpoints"] = res

    # ---- 3c/4: M-16 re-evaluated at 100 traj, ddof=1 ----------------------
    print("\n" + "-"*90); print("  M-16 RE-EVALUATED AT 100 TRAJECTORIES, ddof=1"); print("-"*90)
    verdicts = {}
    for metric in ("e", "nrmse"):
        A5 = np.array([res[f"A{s}@500"][8][metric] for s in SEEDS])
        B5 = np.array([res[f"B{s}@500"][8][metric] for s in SEEDS])
        A25 = np.array([res[f"A{s}@2500"][8][metric] for s in SEEDS])
        B25 = np.array([res[f"B{s}@2500"][8][metric] for s in SEEDS])
        l5 = "A" if A5.mean() < B5.mean() else "B"
        l25 = "A" if A25.mean() < B25.mean() else "B"
        diff = abs(A25.mean()-B25.mean()); spread = max(A25.std(ddof=1), B25.std(ddof=1))
        settled = (l5 == l25) and diff > spread
        verdicts[metric] = {"leader_500": l5, "leader_2500": l25, "same": l5 == l25,
                            "diff": float(diff), "spread_ddof1": float(spread),
                            "exceeds": bool(diff > spread),
                            "verdict": "settled" if settled else "cannot be settled at this budget",
                            "A2500_mean": float(A25.mean()), "A2500_sd": float(A25.std(ddof=1)),
                            "B2500_mean": float(B25.mean()), "B2500_sd": float(B25.std(ddof=1))}
        print(f"    {metric:>6s}: @500 {l5} leads, @2500 {l25} leads, same={l5==l25}")
        print(f"            A@2500 {A25.mean():.4f} +- {A25.std(ddof=1):.4f}"
              f"   B@2500 {B25.mean():.4f} +- {B25.std(ddof=1):.4f}")
        print(f"            |A-B| {diff:.4f} vs max sd(ddof=1) {spread:.4f} -> {verdicts[metric]['verdict'].upper()}")
    out["m16_at_100"] = verdicts
    agree = verdicts["e"]["verdict"] == verdicts["nrmse"]["verdict"]
    print(f"\n    metrics agree: {agree}")
    print(f"    M-16 verdict UNCHANGED from the 10-trajectory evaluation: "
          f"{all(v['verdict']=='settled' for v in verdicts.values())}")

    # ---- Task 4: ddof=0 vs ddof=1 on the ORIGINAL 10-traj numbers ---------
    print("\n" + "-"*90); print("  TASK 4 -- ddof=0 vs ddof=1 on the original 10-trajectory results"); print("-"*90)
    runs = {(a, s): json.load(open(os.path.join(R.RESULTS, f"step5_arm{a}_seed{s}.json")))
            for a in ARMS for s in SEEDS}
    dd = {}
    for metric, key in (("relative-L1", "e"), ("nRMSE", "nrmse")):
        for h in (8, 368):
            A = np.array([runs[("A", s)]["evaluations"]["2500"]["horizon"][str(h)][key] for s in SEEDS])
            B = np.array([runs[("B", s)]["evaluations"]["2500"]["horizon"][str(h)][key] for s in SEEDS])
            dd[f"{metric}|h{h}"] = {"A_mean": float(A.mean()), "A_sd0": float(A.std()),
                                    "A_sd1": float(A.std(ddof=1)), "B_mean": float(B.mean()),
                                    "B_sd0": float(B.std()), "B_sd1": float(B.std(ddof=1))}
            print(f"    {metric:<12s} h={h:<4d} A {A.mean():.4f} +- {A.std():.4f} (ddof0)"
                  f" / {A.std(ddof=1):.4f} (ddof1)   B {B.mean():.4f} +- {B.std():.4f} / {B.std(ddof=1):.4f}")
    for metric, key in (("relative-L1", "e"), ("nRMSE", "nrmse")):
        A = np.array([runs[("A", s)]["evaluations"]["2500"]["horizon"]["8"][key] for s in SEEDS])
        B = np.array([runs[("B", s)]["evaluations"]["2500"]["horizon"]["8"][key] for s in SEEDS])
        d, sp = abs(A.mean()-B.mean()), max(A.std(ddof=1), B.std(ddof=1))
        print(f"    M-16 condition 2 under ddof=1, {metric} h=8: {d:.4f} > {sp:.4f} -> {d > sp}")
        dd[f"m16_{key}"] = {"diff": float(d), "spread_ddof1": float(sp), "holds": bool(d > sp)}
    out["ddof"] = dd

    p = os.path.join(R.RESULTS, "task3_4_power_ddof.json")
    json.dump(out, open(p, "w"), indent=2)
    print(f"\n  wrote {R.rel(p)}")

main()
