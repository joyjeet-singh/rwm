"""
Step 4 / 5 -- CPU timing. This decides whether we rent anything.

Times 20 training iterations at batch 1024 and 256, for ensemble_size 1 and 5,
and projects wall clock for 500 (config) and 2500 (paper Table S7) iterations.
Run before the overfit test so the overfit budget is chosen, not guessed.
"""

import json
import os
import resource
import time

import numpy as np
import torch

import rwm_data as R
import rollout_eval as E
import rwm_model as M
import rwm_train as T

N_ITER = 20
WARMUP = 3


def peak_rss_mb():
    r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return r / (1024 * 1024) if r > 1 << 30 else r / 1024   # macOS bytes, Linux KB


def fmt_hours(sec):
    if sec < 3600:
        return f"{sec/60:.1f} min"
    if sec < 86400:
        return f"{sec/3600:.1f} h"
    return f"{sec/86400:.1f} days"


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    data, episode_id = R.load_data(paths["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(here, "step0_strat.json"),
                         verbose=False)

    print("=" * 82)
    print("STEP 4 / 5 -- CPU TIMING")
    print("=" * 82)
    print(f"  torch {torch.__version__}, threads {torch.get_num_threads()}, CPU only")

    print("\n  2b -- hyperparameters, imported from the config:")
    T.report_hyperparameters(cfg)

    ds = T.WindowDataset(data, episode_id, split["train_episodes"], cfg)
    print(f"\n  2a -- dataset: {len(ds)} windows of {T.WINDOW} steps from episodes"
          f" {ds.episodes}")
    assert len(ds) == 7687, f"expected 7,687 training windows, got {len(ds)}"
    print(f"    matches the 7,687 expected on the seed-0 split")

    weights = cfg["loss_weights"]
    results = {}
    print("\n" + "-" * 82)
    print(f"  timing {N_ITER} iterations after {WARMUP} warm-up, per configuration")
    print("-" * 82)
    print(f"  {'ens':>4s} {'batch':>6s} {'s/iter':>9s} {'std':>8s}"
          f" {'500 iters':>12s} {'2500 iters':>12s} {'peak RSS MB':>12s}")
    for ens in (1, 5):
        for bs in (1024, 256):
            model = M.build_from_config(cfg, ensemble_size=ens)
            opt = T.make_optimizer(model, cfg)
            g = torch.Generator().manual_seed(0)
            for _ in range(WARMUP):
                T.train_step(model, opt, ds.sample(bs, g), weights)
            ts = []
            for _ in range(N_ITER):
                t0 = time.perf_counter()
                T.train_step(model, opt, ds.sample(bs, g), weights)
                ts.append(time.perf_counter() - t0)
            ts = np.array(ts)
            per = float(ts.mean())
            rss = peak_rss_mb()
            results[f"ens{ens}_bs{bs}"] = {
                "s_per_iter": per, "std": float(ts.std()),
                "proj_500_s": per * 500, "proj_2500_s": per * 2500,
                "peak_rss_mb": rss}
            print(f"  {ens:>4d} {bs:>6d} {per:>9.3f} {ts.std():>8.3f}"
                  f" {fmt_hours(per*500):>12s} {fmt_hours(per*2500):>12s} {rss:>12.0f}")
            del model, opt

    print("\n" + "-" * 82)
    print("  PROJECTIONS (single seed, one training run)")
    print("-" * 82)
    ref_cfg = results["ens5_bs1024"]
    print(f"  Reference configuration is ensemble 5, batch {cfg['batch_size']}:")
    print(f"    config's {cfg['max_iterations']} iterations -> "
          f"{fmt_hours(ref_cfg['proj_500_s'])}")
    print(f"    paper's 2500 iterations           -> {fmt_hours(ref_cfg['proj_2500_s'])}")
    print(f"  Cheapest configuration (ensemble 1, batch 256):")
    c = results["ens1_bs256"]
    print(f"    500 iterations  -> {fmt_hours(c['proj_500_s'])}")
    print(f"    2500 iterations -> {fmt_hours(c['proj_2500_s'])}")

    # Step 6 will want cross-validation: 5 folds x however many seeds
    five_fold = ref_cfg["proj_500_s"] * 5
    print(f"\n  Step 6 five-fold cross-validation (M-05) at the reference config,")
    print(f"  500 iterations per fold: {fmt_hours(five_fold)}")
    print(f"  ... and at 2500 iterations per fold: "
          f"{fmt_hours(ref_cfg['proj_2500_s'] * 5)}")

    results["recommendation"] = recommend(ref_cfg, five_fold)
    print(f"\n  RECOMMENDATION: {results['recommendation']}")
    with open(os.path.join(here, "step4_5_timing.json"), "w") as f:
        json.dump({"results": results, "n_iter": N_ITER,
                   "torch": torch.__version__,
                   "threads": torch.get_num_threads()}, f, indent=2)
    return results


def recommend(ref_cfg, five_fold):
    h = ref_cfg["proj_500_s"] / 3600
    if five_fold / 3600 < 12:
        return (f"run locally -- a single reference-config run is {h:.1f} h and the "
                f"full five-fold Step 6 sweep is {five_fold/3600:.1f} h, which fits "
                f"overnight on this machine at no cost")
    if h < 6:
        return (f"single runs locally ({h:.1f} h each); rent only if Step 6 needs the "
                f"full five-fold sweep at 2500 iterations")
    return (f"rent -- a single run projects to {h:.1f} h and the five-fold sweep to "
            f"{five_fold/3600:.1f} h, which is past what this machine should absorb")


if __name__ == "__main__":
    main()
