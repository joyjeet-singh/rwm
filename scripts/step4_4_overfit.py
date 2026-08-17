"""
Step 4 / 4 -- overfit one batch.

If the model cannot memorise a single batch, the bug is in the code and not in
the hyperparameters. Also carries the 1b collapse monitor: log
exp(log_delta_logstd) and exp(min_logstd) every 25 iterations, so the prediction
"collapse is the optimum of this objective" can be checked rather than asserted.

Prediction, made before running (1b):
  E[(mu + sigma*eps - y)^2] = (mu - y)^2 + sigma^2
  The state loss is squared error on a reparameterised sample and there is no
  log-sigma term anywhere, so it is minimised at sigma = 0. The bound loss,
  mean(max_logstd) - mean(min_logstd) = mean(exp(log_delta_logstd)), pushes the
  same way and has a constant positive gradient on log_delta_logstd.
  => exp(log_delta_logstd) should fall monotonically toward 0 from its
     initial value of exp(0) = 1, even on a single batch.

Run with --iters / --batch / --ensemble to fit the measured CPU budget.
"""

import argparse
import json
import os
import time

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
import rwm_model as M
import rwm_train as T

TERMS = M.TOTAL_WEIGHT_KEYS
THRESH = 1e-4


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iters", type=int, default=2000)
    ap.add_argument("--batch", type=int, default=1024)
    ap.add_argument("--ensemble", type=int, default=5)
    ap.add_argument("--max-seconds", type=float, default=1800.0)
    ap.add_argument("--lr", type=float, default=None,
                    help="override the config learning rate (Step 5.1 uses 1e-3)")
    ap.add_argument("--tag", default="")
    args = ap.parse_args()

    here = R.RESULTS
    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    data, episode_id = R.load_data(paths["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(here, "step0_strat.json"),
                         verbose=False)
    weights = cfg["loss_weights"]

    print("=" * 82)
    print(f"STEP 4 / 4 -- OVERFIT ONE BATCH  (ensemble {args.ensemble}, "
          f"batch {args.batch}, cap {args.iters} iters / {args.max_seconds:.0f} s)")
    print("=" * 82)

    ds = T.WindowDataset(data, episode_id, split["train_episodes"], cfg)
    g = torch.Generator().manual_seed(0)
    idx = torch.randint(0, len(ds), (args.batch,), generator=g)
    batch = ds.batch(idx)
    print(f"  one fixed batch of {args.batch} windows drawn from {len(ds)} training windows")

    torch.manual_seed(0)
    model = M.build_from_config(cfg, ensemble_size=args.ensemble)
    if args.lr is not None:
        cfg = {**cfg, "learning_rate": args.lr}
    opt = T.make_optimizer(model, cfg)
    print(f"  fresh random init, {sum(p.numel() for p in model.parameters()):,} parameters")
    print(f"  optimizer Adam lr={cfg['learning_rate']} weight_decay={cfg['weight_decay']}")

    c0 = model.collapse_stats()
    print(f"\n  collapse monitor at init: exp(log_delta) {c0['exp_log_delta_logstd_mean']:.6f}"
          f"   exp(min_logstd) {c0['exp_min_logstd_mean']:.6e}")
    print("  PREDICTION: exp(log_delta) falls monotonically toward 0\n")

    hist = {k: [] for k in TERMS}
    hist["total"] = []
    collapse = []
    reached = None
    t0 = time.perf_counter()
    it = 0
    print(f"  {'iter':>6s} {'state':>11s} {'bound':>10s} {'contact':>10s} "
          f"{'termin':>9s} {'total':>11s} {'exp(logdel)':>12s} {'s':>7s}")
    while it < args.iters and (time.perf_counter() - t0) < args.max_seconds:
        terms, total = T.train_step(model, opt, batch, weights)
        for k, v in zip(TERMS, terms):
            hist[k].append(v)
        hist["total"].append(total)
        if it % 25 == 0 or it == args.iters - 1:
            cs = model.collapse_stats()
            cs["iter"] = it
            collapse.append(cs)
            print(f"  {it:>6d} {terms[0]:>11.6f} {terms[2]:>10.3e} {terms[5]:>10.6f} "
                  f"{terms[6]:>9.3e} {total:>11.6f} "
                  f"{cs['exp_log_delta_logstd_mean']:>12.6f} "
                  f"{time.perf_counter()-t0:>7.0f}")
        if terms[0] < THRESH and reached is None:
            reached = it
            print(f"\n  state loss fell below {THRESH:g} at iteration {it}")
            break
        it += 1
    elapsed = time.perf_counter() - t0

    print("\n" + "-" * 82)
    print(f"  ran {it+1} iterations in {elapsed:.0f} s "
          f"({elapsed/max(it+1,1):.2f} s/iter)")
    if reached is not None:
        print(f"  ITERATIONS TO state loss < {THRESH:g}: {reached}")
    else:
        print(f"  did NOT reach {THRESH:g}; final state loss {hist['state'][-1]:.6f}"
              f"  (from {hist['state'][0]:.6f}, "
              f"{100*(1-hist['state'][-1]/hist['state'][0]):.1f}% reduction)")

    print(f"\n  did each of the seven terms move?")
    print(f"    {'term':<14s} {'first':>13s} {'last':>13s} {'change':>13s}  moved?")
    moved = {}
    for k in TERMS:
        a, b = hist[k][0], hist[k][-1]
        mv = abs(b - a) > 1e-12
        moved[k] = bool(mv)
        note = ""
        if k == "termination":
            note = "  <- expected ~0: target all-zero (D-03/X-04)"
        elif k in ("sequence", "kl", "extension"):
            note = "  <- expected exactly 0 (inert term)"
        print(f"    {k:<14s} {a:>13.3e} {b:>13.3e} {b-a:>+13.3e}  {mv}{note}")

    print(f"\n  collapse monitor (1b):")
    print(f"    {'iter':>6s} {'exp(log_delta)':>16s} {'exp(min_logstd)':>17s}")
    for c in collapse[::max(1, len(collapse) // 12)]:
        print(f"    {c['iter']:>6d} {c['exp_log_delta_logstd_mean']:>16.6f}"
              f" {c['exp_min_logstd_mean']:>17.6e}")
    d = [c["exp_log_delta_logstd_mean"] for c in collapse]
    mono = all(d[i] >= d[i + 1] for i in range(len(d) - 1))
    print(f"\n    exp(log_delta): {d[0]:.6f} -> {d[-1]:.6f}"
          f"   monotonically decreasing: {mono}")
    print(f"    PREDICTION {'CONFIRMED' if mono and d[-1] < d[0] else 'NOT CONFIRMED'}"
          f" -- the interval {'is closing' if d[-1] < d[0] else 'is not closing'}"
          f" even on a single batch")
    print(f"    released checkpoint sits at exp(log_delta) = 5.23e-07 (C-10);"
          f" we are at {d[-1]:.3e} after {it+1} iterations")

    # -------------------------------------------------------------- plot
    fig, ax = plt.subplots(1, 3, figsize=(16, 4.5))
    ax[0].semilogy(hist["state"], lw=1.2, label="state")
    ax[0].semilogy(hist["total"], lw=1.0, alpha=0.7, label="weighted total")
    ax[0].axhline(THRESH, color="#d62728", ls=":", label=f"threshold {THRESH:g}")
    ax[0].set_xlabel("iteration"); ax[0].set_ylabel("loss"); ax[0].legend(fontsize=8)
    ax[0].set_title("Overfit one batch: state loss"); ax[0].grid(alpha=0.3)
    for k in ("bound", "contact", "termination"):
        ax[1].semilogy(np.maximum(hist[k], 1e-20), lw=1.1, label=k)
    ax[1].set_xlabel("iteration"); ax[1].legend(fontsize=8); ax[1].grid(alpha=0.3)
    ax[1].set_title("Other active terms")
    it_ax = [c["iter"] for c in collapse]
    ax[2].semilogy(it_ax, d, lw=1.4, color="#d62728")
    ax[2].axhline(5.23e-07, color="k", ls=":", label="released checkpoint (C-10)")
    ax[2].set_xlabel("iteration"); ax[2].set_ylabel("exp(log_delta_logstd)")
    ax[2].set_title("Collapse monitor"); ax[2].legend(fontsize=8); ax[2].grid(alpha=0.3)
    fig.tight_layout()
    p = os.path.join(R.FIGURES, f"step4_overfit{args.tag}.png")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    fig.savefig(p, dpi=140)
    plt.close(fig)
    print(f"\n  wrote {R.rel(p)}")

    out = {"config": vars(args), "iterations_run": it + 1, "elapsed_s": elapsed,
           "s_per_iter": elapsed / max(it + 1, 1),
           "reached_threshold_at": reached, "threshold": THRESH,
           "first": {k: hist[k][0] for k in TERMS},
           "last": {k: hist[k][-1] for k in TERMS},
           "moved": moved, "collapse": collapse,
           "collapse_monotonic": bool(mono),
           "state_curve": hist["state"]}
    with open(os.path.join(here, f"step4_4_overfit{args.tag}.json"), "w") as f:
        json.dump(out, f, indent=2)
    return out


if __name__ == "__main__":
    main()
