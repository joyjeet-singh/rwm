"""
Step 5.9 -- the main experiment: autoregressive (Arm A) versus teacher forcing (Arm B).

Arm A is the reference objective exactly as implemented: from forecast step 1 onward the
state branch consumes its own reparameterised sample (system_dynamics.py:216).
Arm B changes exactly one thing -- the state branch consumes the true next state, which is
the regime the auxiliary branch already uses (system_dynamics.py:264). The loss, the
auxiliary branch, the data, the alignment and every hyperparameter are identical.

No gradient clipping is applied. 5.7a established the reference has none in the
world-model path: `max_grad_norm=1.0` and `clip_grad_norm_` exist, but only in the PPO
policy optimiser (ppo.py:380). ModelOptimizerConfig carries only learning_rate and
weight_decay, and model_training.py runs loss.backward() straight into optimizer.step().
Adding clipping would change the exact dynamic under study, so it is logged and observed
instead.

Usage:
  python scripts/step5_train.py --arm A --seed 0
"""

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               os.pardir, "src"))

import numpy as np
import torch

import rwm_data as R
import rollout_eval as E
import rwm_metrics as MET
import rwm_model as M
import rwm_train as T

TERMS = M.TOTAL_WEIGHT_KEYS
LIVE = ("state", "bound", "contact", "termination")
CHECKPOINTS = (500, 2500)
LOG_EVERY = 25
CKPT_EVERY = 250
SPIKE_FACTOR = 5.0
SPIKE_WINDOW = 50
HORIZONS = (1, 4, 8, 16, 32, 64, 128, 256, 368)
GROUP_HORIZONS = (1, 8, 368)


def grad_norm(model):
    tot = 0.0
    for p in model.parameters():
        if p.grad is not None:
            tot += float(p.grad.detach().pow(2).sum())
    return tot ** 0.5


def evaluate_checkpoint(model, data, episode_id, split, cfg, base_cfg, scale, tag):
    """Protocol A on held-out episodes at offset 1, both metrics, per 5.9."""
    model.eval()
    res = E.evaluate(lambda hs, ha, fa: _predict(model, hs, ha, fa),
                     data, split, {**base_cfg, "episode_id": episode_id})
    idx = E.sample_trajectories(episode_id, split["holdout_episodes"], seed=0)
    raw = data[idx]
    st = torch.as_tensor(R.normalise_state(raw[:, :, R.STATE_COLS],
                                          cfg["state_data_mean"], cfg["state_data_std"]),
                         dtype=torch.float32)
    ac = torch.as_tensor(raw[:, :, R.ACTION_COLS], dtype=torch.float32)
    pred = model.rollout(st.clone(), ac, E.START_STEP, action_offset=1)

    hold = st.clone()
    hold[:, E.START_STEP:] = st[:, E.START_STEP - 1:E.START_STEP].expand(
        -1, st.shape[1] - E.START_STEP, -1)

    cm = res["clean"]["per_step_mean"]
    fl = E.evaluate(E.hold_last_predictor(), data, split,
                    {**base_cfg, "episode_id": episode_id,
                     "noise_scales": []})["clean"]["per_step_mean"]
    n_model, _ = MET.nrmse_per_step(pred, st, scale, E.START_STEP)
    n_floor, _ = MET.nrmse_per_step(hold, st, scale, E.START_STEP)

    horizon = {h: {"e": float(cm[:h].mean()), "floor_e": float(fl[:h].mean()),
                   "ratio": float(cm[:h].mean() / fl[:h].mean()),
                   "nrmse": float(n_model[:h].mean()),
                   "nrmse_floor": float(n_floor[:h].mean())}
               for h in HORIZONS}

    groups = {}
    for h in GROUP_HORIZONS:
        groups[h] = {}
        for name, cols in (("base lin vel", R.LIN_VEL), ("base ang vel", R.ANG_VEL),
                           ("proj gravity", R.GRAVITY), ("joint pos", R.JOINT_POS),
                           ("joint vel", R.JOINT_VEL), ("joint torque", R.JOINT_TAU)):
            c = list(cols)
            num = (pred[:, E.START_STEP:, c] - st[:, E.START_STEP:, c]).abs().sum(-1)
            den = st[:, E.START_STEP:, c].abs().sum(-1)
            r = num / den
            groups[h][name] = {
                "median": float(r.median(0).values[:h].median()),
                "frac_r_gt_10": float((r > 10.0).float().mean(0)[:h].mean()),
                "nrmse": float(MET.nrmse_groups(pred, st, scale, E.START_STEP)[name][:h].mean())}

    return {"tag": tag, "e": res["clean"]["e"], "median_r": res["clean"]["median_r"],
            "frac_r_gt_10": res["clean"]["frac_r_gt_10"],
            "nrmse_368": float(n_model.mean()),
            "horizon": horizon, "groups": groups,
            "noise": {k: {"e": v["e"], "median_r": v["median_r"]}
                      for k, v in res["noise"].items()},
            "per_step_mean": cm.tolist(), "nrmse_per_step": n_model.tolist(),
            "floor_per_step": fl.tolist(), "floor_nrmse_per_step": n_floor.tolist()}


def _predict(model, hs, ha, fa):
    state = torch.cat([hs, torch.zeros(hs.shape[0], fa.shape[1], hs.shape[2])], 1)
    action = torch.cat([ha, fa], 1)
    return model.rollout(state, action, E.START_STEP, action_offset=1)[:, E.START_STEP:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=["A", "B"], required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--iters", type=int, default=2500)
    ap.add_argument("--batch", type=int, default=256)
    ap.add_argument("--ensemble", type=int, default=1)
    args = ap.parse_args()
    teacher_forcing = args.arm == "B"

    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    data, episode_id = R.load_data(paths["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"),
                         verbose=False)
    base_cfg = E.build_base_config(cfg, seed=0)
    weights = cfg["loss_weights"]
    scale = MET.training_scale(data, episode_id, split["train_episodes"],
                              cfg["state_data_mean"], cfg["state_data_std"])

    run = f"arm{args.arm}_seed{args.seed}"
    rundir = os.path.join(R.REPO_ROOT, "runs", run)
    os.makedirs(rundir, exist_ok=True)

    print("=" * 82)
    print(f"STEP 5 MAIN RUN -- {run}")
    print("=" * 82)
    print(f"  arm {args.arm}: state branch feeds back "
          f"{'the TRUE next state (teacher forcing)' if teacher_forcing else 'its own SAMPLE (autoregressive, faithful)'}")
    print(f"  auxiliary branch: teacher-forced in BOTH arms (system_dynamics.py:264)")
    print(f"  ensemble {args.ensemble}, batch {args.batch}, lr {cfg['learning_rate']},"
          f" weight_decay {cfg['weight_decay']}, {args.iters} iterations")
    print(f"  action alignment: causal, offset=1 (X-05)")
    print(f"  gradient clipping: NONE -- the reference has none in this path (5.7a)")

    ds = T.WindowDataset(data, episode_id, split["train_episodes"], cfg)
    print(f"  {len(ds)} training windows from episodes {ds.episodes}")

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    model = M.build_from_config(cfg, ensemble_size=args.ensemble)
    opt = T.make_optimizer(model, cfg)
    gen = torch.Generator().manual_seed(args.seed)

    hist = {k: [] for k in TERMS}
    hist["total"], hist["grad_norm"], hist["iter"] = [], [], []
    collapse, spikes, evals, ckpt_files = [], [], {}, []
    t0 = time.perf_counter()

    print(f"\n  {'iter':>6s} {'state':>10s} {'bound':>9s} {'contact':>9s} {'termin':>9s}"
          f" {'total':>10s} {'|grad|':>9s} {'exp(logdel)':>11s} {'s':>6s}")
    for it in range(args.iters):
        state, action, ext, contact, term = ds.sample(args.batch, gen)
        model.train()
        model.reset()
        opt.zero_grad(set_to_none=True)
        terms = model.compute_loss(state, action, ext, contact, term,
                                   teacher_forcing=teacher_forcing)
        total = M.weighted_total(terms, weights)
        total.backward()
        gn = grad_norm(model)                      # every iteration, pre-step, unclipped
        opt.step()

        tv = float(total)
        for k, v in zip(TERMS, terms):
            hist[k].append(float(v))
        hist["total"].append(tv)
        hist["grad_norm"].append(gn)
        hist["iter"].append(it)

        # 5.7c spike detector -- flag, record, never stop
        if it >= SPIKE_WINDOW:
            med = float(np.median(hist["total"][-SPIKE_WINDOW - 1:-1]))
            if med > 0 and tv > SPIKE_FACTOR * med:
                spikes.append({"iter": it, "total": tv, "trailing_median": med,
                               "factor": tv / med, "grad_norm": gn,
                               **{k: float(v) for k, v in zip(TERMS, terms)}})

        if it % LOG_EVERY == 0 or it == args.iters - 1:
            cs = model.collapse_stats(); cs["iter"] = it
            cs["wall_clock_s"] = time.perf_counter() - t0
            collapse.append(cs)
            print(f"  {it:>6d} {float(terms[0]):>10.5f} {float(terms[2]):>9.3e}"
                  f" {float(terms[5]):>9.5f} {float(terms[6]):>9.3e} {tv:>10.5f}"
                  f" {gn:>9.3f} {cs['exp_log_delta_logstd_mean']:>11.6f}"
                  f" {time.perf_counter()-t0:>6.0f}")

        step = it + 1
        if step in CHECKPOINTS:
            wp = os.path.join(rundir, f"weights_{step}.pt")
            torch.save({"model_state_dict": model.state_dict(), "iter": step,
                        "arm": args.arm, "seed": args.seed}, wp)
            evals[step] = evaluate_checkpoint(model, data, episode_id, split, cfg,
                                             base_cfg, scale, f"{run}@{step}")
            h = evals[step]["horizon"]
            print(f"    [checkpoint {step}]  e@8 {h[8]['e']:.4f}  e@368 {h[368]['e']:.4f}"
                  f"  nRMSE@8 {h[8]['nrmse']:.4f}  nRMSE@368 {h[368]['nrmse']:.4f}")
        elif step % CKPT_EVERY == 0:
            # rolling recovery point; keep only the most recent two (5.7d)
            wp = os.path.join(rundir, f"rolling_{step}.pt")
            torch.save({"model_state_dict": model.state_dict(),
                        "optimizer_state_dict": opt.state_dict(), "iter": step}, wp)
            ckpt_files.append(wp)
            for old in ckpt_files[:-2]:
                if os.path.exists(old):
                    os.remove(old)
            ckpt_files = ckpt_files[-2:]

    elapsed = time.perf_counter() - t0

    # ---------------------------------------------------------- collapse fit
    it_a = np.array([c["iter"] for c in collapse], dtype=float)
    ld = np.log(np.array([c["exp_log_delta_logstd_mean"] for c in collapse]))
    n = len(it_a)
    slope, intercept = np.polyfit(it_a, ld, 1)
    resid = ld - (slope * it_a + intercept)
    se = float(np.sqrt((resid ** 2).sum() / (n - 2) / ((it_a - it_a.mean()) ** 2).sum()))

    print("\n" + "-" * 82)
    print(f"  wall clock {elapsed/3600:.2f} h ({elapsed/args.iters:.3f} s/iter)")
    print(f"  final: " + "  ".join(f"{k} {hist[k][-1]:.4e}" for k in LIVE))
    print(f"  grad norm: mean {np.mean(hist['grad_norm']):.3f}"
          f"  median {np.median(hist['grad_norm']):.3f}"
          f"  p99 {np.percentile(hist['grad_norm'],99):.3f}"
          f"  max {np.max(hist['grad_norm']):.3f}")
    print(f"  spikes (>{SPIKE_FACTOR:g}x trailing {SPIKE_WINDOW}-median): {len(spikes)}"
          + (f"  at {[s['iter'] for s in spikes]}" if spikes else ""))
    print(f"  collapse fit: d(log_delta)/d(iter) = {slope:.4e} +- {se:.2e}"
          f"   (lr {cfg['learning_rate']:g}, rate/lr {abs(slope)/cfg['learning_rate']:.2f})")
    print(f"    exp(log_delta): {np.exp(ld[0]):.6f} -> {np.exp(ld[-1]):.6f}")
    print(f"    iterations implied to reach the checkpoint's -14.4629: "
          f"{-14.4629/slope:,.0f}")
    tail = np.array(hist["state"][-250:])
    tail_slope = float(np.polyfit(np.arange(len(tail)), tail, 1)[0])
    print(f"  state-loss slope over the final 250 iterations: {tail_slope:+.3e} per iter"
          f"  ({'still falling' if tail_slope < 0 else 'flat or rising'})")

    out = {"run": run, "arm": args.arm, "seed": args.seed,
           "teacher_forcing": teacher_forcing,
           "hyperparameters": {"ensemble": args.ensemble, "batch": args.batch,
                               "iterations": args.iters,
                               "learning_rate": cfg["learning_rate"],
                               "weight_decay": cfg["weight_decay"],
                               "loss_weights": weights, "action_offset": 1,
                               "gradient_clipping": None,
                               "n_train_windows": len(ds),
                               "train_episodes": split["train_episodes"],
                               "holdout_episodes": split["holdout_episodes"]},
           "data_sha256": R.sha256(paths["csv"]),
           "wall_clock_s": elapsed, "s_per_iter": elapsed / args.iters,
           "final_terms": {k: hist[k][-1] for k in TERMS},
           "grad_norm_stats": {"mean": float(np.mean(hist["grad_norm"])),
                               "median": float(np.median(hist["grad_norm"])),
                               "p99": float(np.percentile(hist["grad_norm"], 99)),
                               "max": float(np.max(hist["grad_norm"]))},
           "spikes": spikes, "n_spikes": len(spikes),
           "collapse": collapse,
           "collapse_fit": {"slope_per_iter": float(slope), "stderr": se,
                            "n_points": n, "rate_over_lr":
                                float(abs(slope) / cfg["learning_rate"]),
                            "iters_to_checkpoint_value": float(-14.4629 / slope)},
           "state_loss_tail_slope_250": tail_slope,
           "evaluations": evals,
           "curves": {k: hist[k] for k in ("state", "bound", "contact",
                                           "termination", "total", "grad_norm")},
           "torch": torch.__version__}
    jp = os.path.join(R.RESULTS, f"step5_{run}.json")
    with open(jp, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\n  wrote {R.rel(jp)}")
    print(f"  weights in {R.rel(rundir)} (gitignored)")
    return out


if __name__ == "__main__":
    main()
