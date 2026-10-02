"""
Train one architecture baseline for rules M-75 (regime tf) and M-76 (regime ar).

Everything except the model and its state loss is Arm A's, read from the same places
step5_train.py reads it: the reference config (learning rate, weight decay, loss weights),
the seed-0 split (episodes 1 and 8 held out), the same 40-row training windows
(rwm_train.WindowDataset, 7,687 of them), the same batch sampler and seeding
(torch.manual_seed, numpy seed, a torch.Generator for batches), Adam, batch 256, 2,500
iterations, no gradient clipping. The loss is the baseline's state loss
(src/baselines/common.py: RWM's sampled squared error and bound term) weighted by the
config's state and bound weights, plus, for the RSSM, its KL term at its own scale
(BASELINE_SPECS.md). There are no auxiliary heads and so no auxiliary loss.

    python scripts/train_baseline.py --arch mlp --regime tf --spec s7 --seed 0

Writes results/baseline_run_<arch>_<regime>_<spec>_seed<s>.json -- outside every
results/step5_*.json glob the paper reads -- and runs/baseline_<arch>_<regime>_<spec>_seed<s>/
weights_500.pt and weights_<iters>.pt.
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import torch  # noqa: E402

import baselines as BL  # noqa: E402
import rollout_eval as E  # noqa: E402
import rwm_data as R  # noqa: E402
import rwm_train as T  # noqa: E402

RULE = {"tf": "M-75", "ar": "M-76"}
LOG_EVERY = 25
CHECKPOINTS = (500, 2500)


def grad_norm(model):
    return sum(float(p.grad.detach().pow(2).sum()) for p in model.parameters()
               if p.grad is not None) ** 0.5


def build_everything(arch, spec, seed, batch=256):
    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    data, episode_id = R.load_data(paths["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"),
                         verbose=False)
    ds = T.WindowDataset(data, episode_id, split["train_episodes"], cfg)
    torch.manual_seed(seed)
    np.random.seed(seed)
    model = BL.build(arch, spec, cfg)
    opt = T.make_optimizer(model, cfg)
    gen = torch.Generator().manual_seed(seed)
    return cfg, data, episode_id, split, ds, model, opt, gen, paths


def loss_weights(model, cfg):
    kl_w = getattr(model, "kl_scale", 0.0)
    return {"state": cfg["loss_weights"]["state"], "bound": cfg["loss_weights"]["bound"],
            "kl": kl_w}


def train_iterations(model, opt, ds, gen, batch, iters, regime, w, on_iter=None):
    """The training loop, shared with the verification ladder."""
    hist = {k: [] for k in ("state", "bound", "kl", "total", "grad_norm")}
    for it in range(iters):
        state, action, _, _, _ = ds.sample(batch, gen)
        model.train()
        model.reset()
        opt.zero_grad(set_to_none=True)
        s, b, k = model.compute_state_loss(state, action, regime)
        total = w["state"] * s + w["bound"] * b + w["kl"] * k
        total.backward()
        gn = grad_norm(model)
        opt.step()
        for key, v in (("state", s), ("bound", b), ("kl", k), ("total", total)):
            hist[key].append(float(v))
        hist["grad_norm"].append(gn)
        if on_iter:
            on_iter(it, hist)
    return hist


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arch", choices=["mlp", "transformer", "rssm"], required=True)
    ap.add_argument("--regime", choices=["tf", "ar"], required=True)
    ap.add_argument("--spec", choices=["s7", "matched", "x1v1", "x1v2"], required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--iters", type=int, default=2500)
    ap.add_argument("--batch", type=int, default=256)
    ap.add_argument("--out-dir", default=None, help="timing probe: write here instead")
    args = ap.parse_args()
    if args.spec in ("x1v1", "x1v2"):
        assert args.arch == "rssm" and args.regime == "tf", "rule X1's variants are teacher-forced RSSMs (ledger M-80)"

    cfg, data, episode_id, split, ds, model, opt, gen, paths = build_everything(
        args.arch, args.spec, args.seed, args.batch)
    run = f"baseline_{args.arch}_{args.regime}_{args.spec}_seed{args.seed}"
    rundir = os.path.join(args.out_dir or os.path.join(R.REPO_ROOT, "runs"), run)
    os.makedirs(rundir, exist_ok=True)
    w = loss_weights(model, cfg)
    n_par = BL.n_params(model)
    print("=" * 82)
    print(f"BASELINE RUN -- {run}   (rule {RULE[args.regime]})")
    print("=" * 82)
    print(f"  {args.arch}, spec {args.spec}, regime {args.regime}, {n_par:,} parameters")
    print(f"  {len(ds)} training windows, batch {args.batch}, lr {cfg['learning_rate']}, "
          f"weight decay {cfg['weight_decay']}, {args.iters} iterations, loss weights {w}",
          flush=True)

    t0 = time.perf_counter()
    wall = []

    def on_iter(it, hist):
        step = it + 1
        if it % LOG_EVERY == 0 or it == args.iters - 1:
            wall.append({"iter": it, "wall_clock_s": time.perf_counter() - t0})
            print(f"  {it:>6d}  state {hist['state'][-1]:>10.5f}  bound {hist['bound'][-1]:>9.3e}"
                  f"  kl {hist['kl'][-1]:>9.4f}  |grad| {hist['grad_norm'][-1]:>9.3f}"
                  f"  {time.perf_counter() - t0:>6.0f}s", flush=True)
        if step in CHECKPOINTS and step <= args.iters:
            torch.save({"model_state_dict": model.state_dict(), "iter": step,
                        "arch": args.arch, "regime": args.regime, "spec": args.spec,
                        "seed": args.seed}, os.path.join(rundir, f"weights_{step}.pt"))

    hist = train_iterations(model, opt, ds, gen, args.batch, args.iters, args.regime, w, on_iter)
    elapsed = time.perf_counter() - t0
    out = {"rule": RULE[args.regime], "run": run, "arch": args.arch, "regime": args.regime,
           "spec": args.spec, "seed": args.seed,
           "hyperparameters": {"iterations": args.iters, "batch": args.batch,
                               "history_horizon": BL.HISTORY,
                               "forecast_horizon": T.WINDOW - BL.HISTORY,
                               "window": T.WINDOW, "learning_rate": cfg["learning_rate"],
                               "weight_decay": cfg["weight_decay"], "loss_weights": w,
                               "action_offset": 1, "gradient_clipping": None,
                               "n_train_windows": len(ds), "n_params": n_par,
                               "architecture": getattr(model, "spec", None) or
                               {"base_shape": getattr(model, "base_shape", None)},
                               "train_episodes": split["train_episodes"],
                               "holdout_episodes": split["holdout_episodes"]},
           "data_sha256": R.sha256(paths["csv"]),
           "wall_clock_s": elapsed, "s_per_iter": elapsed / args.iters,
           "wall_clock_log": wall,
           "final_terms": {k: hist[k][-1] for k in ("state", "bound", "kl", "total")},
           "curves": hist, "torch": torch.__version__}
    jp = os.path.join(args.out_dir or R.RESULTS, f"baseline_run_{args.arch}_{args.regime}_"
                                                 f"{args.spec}_seed{args.seed}.json")
    with open(jp, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\n  wall clock {elapsed / 3600:.2f} h ({elapsed / args.iters:.3f} s/iter)")
    print(f"  wrote {R.rel(jp)}")


if __name__ == "__main__":
    main()
