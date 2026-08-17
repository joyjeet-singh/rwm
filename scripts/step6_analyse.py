"""
Step 6.4/6.5/6.7 -- evaluate the pre-registered rule and pool the collapse fits.

M-16 is evaluated on BOTH metrics separately (6.4). R-20 showed relative-L1 and nRMSE
invert the model-versus-floor ordering at h=1; they agreed at h=8, but that is not to be
taken on trust for the A-versus-B comparison. If the two metrics return opposite verdicts,
that disagreement outranks either verdict and is the headline result.

The rule, quoted from M-16 exactly as pre-registered:

  Reproduces / fails to reproduce, and can be reported, only if BOTH:
    1. the A-vs-B ordering at h=8 is the SAME at 500 and at 2500, AND
    2. the difference between arms EXCEEDS the seed spread within arms.
  Cannot be settled at this budget if EITHER:
    1. the ordering FLIPS between checkpoints, OR
    2. the difference falls INSIDE the seed spread.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               os.pardir, "src"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import rwm_data as R

ARMS = ("A", "B")
SEEDS = (0, 1, 2)
CKPTS = ("500", "2500")
HORIZONS = (1, 4, 8, 16, 32, 64, 128, 256, 368)
LR = 1e-4
CKPT_LOG_DELTA = -14.4629


def load():
    d = {}
    for a in ARMS:
        for s in SEEDS:
            p = os.path.join(R.RESULTS, f"step5_arm{a}_seed{s}.json")
            d[(a, s)] = json.load(open(p))
    return d


def stat(runs, arm, ckpt, h, key):
    v = [runs[(arm, s)]["evaluations"][ckpt]["horizon"][str(h)][key] for s in SEEDS]
    return np.array(v)


def main():
    runs = load()
    out = {}

    # ------------------------------------------------ per-run health
    print("=" * 92)
    print("STEP 6 -- SIX RUNS COMPLETE")
    print("=" * 92)
    print(f"  {'run':<12s} {'wall h':>7s} {'s/iter':>7s} {'spikes':>7s} {'|grad| med':>11s}"
          f" {'|grad| max':>11s} {'final state':>12s} {'tail slope/iter':>16s}")
    health = {}
    for a in ARMS:
        for s in SEEDS:
            r = runs[(a, s)]
            g = r["grad_norm_stats"]
            health[f"{a}{s}"] = {
                "wall_h": r["wall_clock_s"] / 3600, "s_per_iter": r["s_per_iter"],
                "n_spikes": r["n_spikes"], "grad_median": g["median"], "grad_max": g["max"],
                "final_state": r["final_terms"]["state"],
                "tail_slope": r["state_loss_tail_slope_250"]}
            print(f"  arm{a} seed{s:<5d} {r['wall_clock_s']/3600:>7.2f} {r['s_per_iter']:>7.3f}"
                  f" {r['n_spikes']:>7d} {g['median']:>11.3f} {g['max']:>11.3f}"
                  f" {r['final_terms']['state']:>12.4f} {r['state_loss_tail_slope_250']:>+16.3e}")
    tot = sum(runs[k]["wall_clock_s"] for k in runs) / 3600
    print(f"\n  total wall clock across six runs: {tot:.2f} h")
    print(f"  spike count, all runs: {sum(runs[k]['n_spikes'] for k in runs)}")
    all_tail = [runs[k]["state_loss_tail_slope_250"] for k in runs]
    print(f"  every run still falling at 2500? {all(t < 0 for t in all_tail)}"
          f"   (slopes {min(all_tail):.2e} to {max(all_tail):.2e})")
    out["health"] = health

    # ------------------------------------------------ 5.12 comparison table
    print("\n" + "=" * 92)
    print("5.12 / 6.4 -- THE COMPARISON TABLE (mean +- sd over 3 seeds)")
    print("=" * 92)
    table = {}
    for metric, key in (("relative-L1 e", "e"), ("nRMSE", "nrmse")):
        print(f"\n  {metric}")
        print(f"    {'':<18s} {'Arm A (autoregressive)':>26s} {'Arm B (teacher forcing)':>26s}"
              f" {'floor':>9s}")
        for h in (8, 368):
            for c in CKPTS:
                A, B = stat(runs, "A", c, h, key), stat(runs, "B", c, h, key)
                fl = stat(runs, "A", c, h, "floor_e" if key == "e" else "nrmse_floor")[0]
                table[(metric, h, c)] = {"A_mean": float(A.mean()), "A_sd": float(A.std()),
                                        "B_mean": float(B.mean()), "B_sd": float(B.std()),
                                        "A_all": A.tolist(), "B_all": B.tolist(),
                                        "floor": float(fl)}
                print(f"    h={h:<3d} @{c:<5s}  {A.mean():>13.4f} +- {A.std():<9.4f}"
                      f" {B.mean():>13.4f} +- {B.std():<9.4f} {fl:>9.4f}")
    out["table"] = {f"{m}|h{h}|{c}": v for (m, h, c), v in table.items()}

    # ------------------------------------------------ 6.4 evaluate M-16
    print("\n" + "=" * 92)
    print("6.4 -- M-16 EVALUATED, ON BOTH METRICS SEPARATELY")
    print("=" * 92)
    verdicts = {}
    for metric, key in (("relative-L1 e", "e"), ("nRMSE", "nrmse")):
        A5, B5 = stat(runs, "A", "500", 8, key), stat(runs, "B", "500", 8, key)
        A25, B25 = stat(runs, "A", "2500", 8, key), stat(runs, "B", "2500", 8, key)
        # lower error is better, so "leads" = smaller
        lead5 = "A" if A5.mean() < B5.mean() else "B"
        lead25 = "A" if A25.mean() < B25.mean() else "B"
        same_order = lead5 == lead25
        diff25 = abs(A25.mean() - B25.mean())
        spread25 = max(A25.std(), B25.std())
        exceeds = diff25 > spread25
        settled = same_order and exceeds
        v = {"metric": metric,
             "h8_500": {"A": float(A5.mean()), "B": float(B5.mean()), "leader": lead5},
             "h8_2500": {"A": float(A25.mean()), "B": float(B25.mean()), "leader": lead25},
             "ordering_same": bool(same_order),
             "arm_difference_2500": float(diff25),
             "max_seed_sd_2500": float(spread25),
             "difference_exceeds_spread": bool(exceeds),
             "verdict": ("settled" if settled else "cannot be settled at this budget")}
        verdicts[metric] = v
        print(f"\n  {metric}, evaluated at h=8:")
        print(f"    @500 : A {A5.mean():.4f} +- {A5.std():.4f}   B {B5.mean():.4f}"
              f" +- {B5.std():.4f}   -> {lead5} leads")
        print(f"    @2500: A {A25.mean():.4f} +- {A25.std():.4f}   B {B25.mean():.4f}"
              f" +- {B25.std():.4f}   -> {lead25} leads")
        print(f"    condition 1, ordering same at both checkpoints : {same_order}")
        print(f"    condition 2, |A-B| {diff25:.4f} > max seed sd {spread25:.4f} : {exceeds}")
        print(f"    -> VERDICT: {v['verdict'].upper()}")
    out["verdicts"] = verdicts

    v1, v2 = verdicts["relative-L1 e"], verdicts["nRMSE"]
    agree = v1["verdict"] == v2["verdict"]
    print(f"\n  do the two metrics agree on the verdict? {agree}")
    if not agree:
        print("  *** THEY DISAGREE. Per 6.4 this disagreement OUTRANKS either verdict and is")
        print("  *** the headline methodological result: a pre-registered rule returning")
        print("  *** opposite answers under two reasonable metrics.")
    out["metrics_agree"] = bool(agree)

    # the 6.1 pre-registered flip pattern
    flip_pattern = None
    for metric, v in verdicts.items():
        if not v["ordering_same"]:
            pat = f"{v['h8_500']['leader']}@500 -> {v['h8_2500']['leader']}@2500"
            is_tf = (v["h8_500"]["leader"] == "B" and v["h8_2500"]["leader"] == "A")
            print(f"\n  FLIP under {metric}: {pat}")
            print(f"    matches the 6.1 pre-registered teacher-forcing signature"
                  f" (B@500 -> A@2500): {is_tf}")
            flip_pattern = {"metric": metric, "pattern": pat,
                            "matches_preregistered_tf_signature": bool(is_tf)}
    out["flip_pattern"] = flip_pattern

    # ------------------------------------------------ 6.5 pooled collapse fit
    print("\n" + "=" * 92)
    print("6.5 -- POOLED COLLAPSE FIT ACROSS ALL SIX RUNS")
    print("=" * 92)
    rates, ses = [], []
    print(f"  {'run':<12s} {'rate/iter':>13s} {'stderr':>11s} {'rate/lr':>9s}"
          f" {'exp(logdel)@2500':>18s}")
    per_run = {}
    for a in ARMS:
        for s in SEEDS:
            r = runs[(a, s)]
            it = np.array([c["iter"] for c in r["collapse"]], dtype=float)
            ld = np.log(np.array([c["exp_log_delta_logstd_mean"] for c in r["collapse"]]))
            n = len(it)
            slope, inter = np.polyfit(it, ld, 1)
            resid = ld - (slope * it + inter)
            se = float(np.sqrt((resid ** 2).sum() / (n - 2) / ((it - it.mean()) ** 2).sum()))
            rates.append(float(slope)); ses.append(se)
            per_run[f"{a}{s}"] = {"rate": float(slope), "stderr": se,
                                 "rate_over_lr": abs(float(slope)) / LR,
                                 "final_exp_log_delta": float(np.exp(ld[-1]))}
            print(f"  arm{a} seed{s:<5d} {slope:>13.4e} {se:>11.2e}"
                  f" {abs(slope)/LR:>9.3f} {np.exp(ld[-1]):>18.6f}")
    rates = np.array(rates)
    pooled = float(rates.mean())
    sem = float(rates.std(ddof=1) / np.sqrt(len(rates)))
    print(f"\n  pooled rate: {pooled:.4e} +- {sem:.2e} (sem over 6 runs)")
    print(f"  run-to-run sd: {rates.std(ddof=1):.3e}"
          f"  ({100*rates.std(ddof=1)/abs(pooled):.2f}% of the mean)")
    print(f"  spread min..max: {rates.min():.4e} .. {rates.max():.4e}")
    print(f"  pooled rate / lr = {abs(pooled)/LR:.4f}")
    print(f"\n  placed beside the earlier measurements:")
    print(f"    {'measurement':<34s} {'lr':>8s} {'rate':>13s} {'rate/lr':>9s}")
    print(f"    {'overfit, 451 iters (R-17)':<34s} {'1e-4':>8s} {-9.318e-05:>13.3e} {0.93:>9.2f}")
    print(f"    {'overfit, 2000 iters (R-18)':<34s} {'1e-3':>8s} {-7.025e-04:>13.3e} {0.70:>9.2f}")
    print(f"    {'six main runs, pooled':<34s} {'1e-4':>8s} {pooled:>13.3e}"
          f" {abs(pooled)/LR:>9.2f}")
    iters_needed = CKPT_LOG_DELTA / pooled
    lr_needed = CKPT_LOG_DELTA / (5000 * pooled / LR)
    print(f"\n  from the POOLED fit, to reach the released checkpoint's {CKPT_LOG_DELTA}:")
    print(f"    iterations at lr 1e-4 : {iters_needed:,.0f}")
    print(f"    lr to arrive in 5000  : {abs(lr_needed):.2e}  ({abs(lr_needed)/LR:.0f}x configured)")
    out["collapse"] = {"per_run": per_run, "pooled_rate": pooled, "sem": sem,
                       "run_to_run_sd": float(rates.std(ddof=1)),
                       "pooled_rate_over_lr": abs(pooled) / LR,
                       "iters_to_checkpoint": float(iters_needed),
                       "lr_for_5000_iters": float(abs(lr_needed))}

    # ------------------------------------------------ plot
    fig, ax = plt.subplots(1, 3, figsize=(17, 5))
    for a, col in (("A", "#1f77b4"), ("B", "#d62728")):
        for s in SEEDS:
            r = runs[(a, s)]
            cur = np.array(r["evaluations"]["2500"]["per_step_mean"])
            ax[0].plot(np.arange(1, len(cur) + 1), cur, color=col, lw=1.0,
                       alpha=0.75, label=f"Arm {a}" if s == 0 else None)
    fl = np.array(runs[("A", 0)]["evaluations"]["2500"]["floor_per_step"])
    ax[0].plot(np.arange(1, len(fl) + 1), fl, "k:", lw=1.5, label="hold-last floor")
    ax[0].set_xlabel("forecast step"); ax[0].set_ylabel("relative-L1 $r_t$")
    ax[0].set_title("Per-step error at 2500 iterations, 3 seeds per arm")
    ax[0].legend(fontsize=9); ax[0].grid(alpha=0.3)

    for a, col in (("A", "#1f77b4"), ("B", "#d62728")):
        for s in SEEDS:
            r = runs[(a, s)]
            cur = np.array(r["evaluations"]["2500"]["nrmse_per_step"])
            ax[1].plot(np.arange(1, len(cur) + 1), cur, color=col, lw=1.0, alpha=0.75,
                       label=f"Arm {a}" if s == 0 else None)
    nfl = np.array(runs[("A", 0)]["evaluations"]["2500"]["floor_nrmse_per_step"])
    ax[1].plot(np.arange(1, len(nfl) + 1), nfl, "k:", lw=1.5, label="floor")
    ax[1].axhline(1.0, color="0.5", lw=0.8)
    ax[1].set_xlabel("forecast step"); ax[1].set_ylabel("nRMSE")
    ax[1].set_title("Same, nRMSE (1.0 = training mean)")
    ax[1].legend(fontsize=9); ax[1].grid(alpha=0.3)

    for a, col in (("A", "#1f77b4"), ("B", "#d62728")):
        for s in SEEDS:
            r = runs[(a, s)]
            it = [c["iter"] for c in r["collapse"]]
            v = [c["exp_log_delta_logstd_mean"] for c in r["collapse"]]
            ax[2].plot(it, v, color=col, lw=1.1, alpha=0.75,
                       label=f"Arm {a}" if s == 0 else None)
    ax[2].axhline(5.234e-07, color="k", ls=":", label="released checkpoint")
    ax[2].set_yscale("log"); ax[2].set_xlabel("iteration")
    ax[2].set_ylabel("exp(log_delta_logstd)")
    ax[2].set_title("Collapse trajectories, all six runs")
    ax[2].legend(fontsize=9); ax[2].grid(alpha=0.3)
    fig.tight_layout()
    p = os.path.join(R.FIGURES, "step6_arms_comparison.png")
    fig.savefig(p, dpi=140); plt.close(fig)
    print(f"\n  wrote {R.rel(p)}")

    jp = os.path.join(R.RESULTS, "step6_analysis.json")
    with open(jp, "w") as f:
        json.dump(out, f, indent=2)
    print(f"  wrote {R.rel(jp)}")
    return out


if __name__ == "__main__":
    main()
