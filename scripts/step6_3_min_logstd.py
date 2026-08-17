"""
Step 6.3 -- a second, slower variance clock for O-12.

O-12 rests on `log_delta_logstd`, whose gradient comes from the bound loss and is therefore
constant in sign, giving a rate of ~0.94 x lr. `min_logstd` is a different parameter on a
different gradient path: C-11 established that it CANCELS out of the bound loss algebraically,
so it moves only through the weaker sigma term in the state loss.

If the released checkpoint's `min_logstd` also sits far from its initialisation, O-12 gains a
second independent parameter telling the same story on a slower clock. Two parameters with
different gradient paths both implying far more optimisation than any documented count is much
harder to explain away than one.

Honest caveat, stated before computing: `min_logstd`'s drift is NOT expected to be linear the
way `log_delta_logstd`'s is, because its gradient depends on sigma itself, which is shrinking.
The extrapolation below is therefore an order-of-magnitude statement, not a fitted count.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               os.pardir, "src"))

import numpy as np
import torch

import rwm_data as R

INIT_MIN_LOGSTD = -5.0          # mlp.py:78
CKPT_LOG_DELTA = -14.4629       # C-10


def main():
    paths = R.repo_paths()
    sd = torch.load(paths["ckpt"], map_location="cpu")["system_dynamics_state_dict"]

    print("=" * 82)
    print("STEP 6.3 -- min_logstd AS A SECOND AXIS FOR O-12")
    print("=" * 82)

    mins = torch.cat([sd[f"state_heads.{i}.state_min_logstd"].flatten() for i in range(5)])
    per_head = [float(sd[f"state_heads.{i}.state_min_logstd"].mean()) for i in range(5)]
    m = float(mins.mean())
    sigma = float(np.exp(m))

    print("\n  released checkpoint, state_min_logstd:")
    for i, v in enumerate(per_head):
        print(f"    head {i}: mean {v:+.4f}   sigma = exp(mean) = {np.exp(v):.4e}")
    print(f"    across all 5 heads x 45 dims: mean {m:+.4f}"
          f"   min {float(mins.min()):+.4f}   max {float(mins.max()):+.4f}"
          f"   sd {float(mins.std()):.4f}")
    print(f"    sigma = exp(mean) = {sigma:.4e}")
    print(f"    initialisation (mlp.py:78) = {INIT_MIN_LOGSTD:+.1f}"
          f"   ->  sigma_init = {np.exp(INIT_MIN_LOGSTD):.4e}")
    travel = m - INIT_MIN_LOGSTD
    print(f"    distance travelled from init: {travel:+.4f} in log space"
          f"  (a factor of {np.exp(travel):.3f} in sigma)")

    # ---- Arm A's measured drift rate for the same parameter ---------------
    ap = os.path.join(R.RESULTS, "step5_armA_seed0.json")
    assert os.path.exists(ap), "Arm A seed 0 results required"
    d = json.load(open(ap))
    c = d["collapse"]
    it = np.array([x["iter"] for x in c], dtype=float)
    ml = np.log(np.array([x["exp_min_logstd_mean"] for x in c]))
    ld = np.log(np.array([x["exp_log_delta_logstd_mean"] for x in c]))

    def fit(y):
        n = len(it)
        slope, inter = np.polyfit(it, y, 1)
        resid = y - (slope * it + inter)
        se = float(np.sqrt((resid ** 2).sum() / (n - 2) / ((it - it.mean()) ** 2).sum()))
        return float(slope), se

    s_min, se_min = fit(ml)
    s_del, se_del = fit(ld)

    print("\n  Arm A seed 0, measured drift over 2500 iterations at lr 1e-4:")
    print(f"    {'parameter':<22s} {'start':>10s} {'end':>10s} {'rate/iter':>13s} {'stderr':>10s}")
    print(f"    {'log_delta_logstd':<22s} {ld[0]:>10.6f} {ld[-1]:>10.6f}"
          f" {s_del:>13.3e} {se_del:>10.2e}")
    print(f"    {'min_logstd':<22s} {ml[0]:>10.6f} {ml[-1]:>10.6f}"
          f" {s_min:>13.3e} {se_min:>10.2e}")
    print(f"    ratio of rates (log_delta / min_logstd): {abs(s_del/s_min):.1f}x")
    print(f"    -> min_logstd drifts ~{abs(s_del/s_min):.0f}x slower, as C-11 predicts:")
    print(f"       it takes no gradient from the bound loss, only the weaker sigma path.")

    # ---- how far would that rate have to run? ----------------------------
    iters_needed = travel / s_min
    print("\n  ORDER-OF-MAGNITUDE extrapolation (NOT a fitted count -- min_logstd's")
    print("  gradient depends on sigma, which is itself shrinking, so the drift is")
    print("  not expected to stay linear):")
    print(f"    to travel {travel:+.4f} at Arm A's measured {s_min:.3e} per iteration:")
    print(f"      ~{iters_needed:,.0f} iterations   (order 1e{int(np.floor(np.log10(abs(iters_needed)))):d})")
    print(f"    for comparison, log_delta_logstd implies "
          f"{CKPT_LOG_DELTA/s_del:,.0f} iterations (order "
          f"1e{int(np.floor(np.log10(abs(CKPT_LOG_DELTA/s_del)))):d})")

    print("\n" + "=" * 82)
    agree = abs(np.log10(abs(iters_needed)) - np.log10(abs(CKPT_LOG_DELTA / s_del))) < 1.0
    if abs(travel) < 0.2:
        print("  VERDICT: the released min_logstd has barely moved from its initialisation,")
        print("  so it does NOT provide a second axis. O-12 continues to rest on")
        print("  log_delta_logstd alone.")
        verdict = "no second axis"
    elif agree:
        print("  VERDICT: min_logstd gives O-12 a SECOND INDEPENDENT AXIS, and the two agree")
        print("  to within an order of magnitude despite travelling on different gradient")
        print("  paths and at rates differing ~5x. Two parameters implying the same conclusion")
        print("  is much harder to explain away than one.")
        verdict = "second axis, agrees"
    else:
        print("  VERDICT: min_logstd has moved substantially, so it IS a second axis, but the")
        print("  implied iteration counts differ by more than an order of magnitude. Report")
        print("  both; the disagreement constrains which escape hatch in O-12 is live.")
        verdict = "second axis, disagrees"
    print("=" * 82)

    out = {"checkpoint_min_logstd_mean": m, "checkpoint_sigma": sigma,
           "per_head_means": per_head,
           "checkpoint_min_logstd_min": float(mins.min()),
           "checkpoint_min_logstd_max": float(mins.max()),
           "checkpoint_min_logstd_sd": float(mins.std()),
           "init_min_logstd": INIT_MIN_LOGSTD, "distance_travelled": travel,
           "armA_rate_min_logstd": s_min, "armA_rate_min_logstd_stderr": se_min,
           "armA_rate_log_delta": s_del, "armA_rate_log_delta_stderr": se_del,
           "rate_ratio": abs(s_del / s_min),
           "iters_implied_min_logstd": float(iters_needed),
           "iters_implied_log_delta": float(CKPT_LOG_DELTA / s_del),
           "verdict": verdict}
    jp = os.path.join(R.RESULTS, "step6_3_min_logstd.json")
    with open(jp, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\n  wrote {R.rel(jp)}")
    return out


if __name__ == "__main__":
    main()
