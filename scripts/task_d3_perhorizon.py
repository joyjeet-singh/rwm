"""D3 — does a PER-HORIZON scalar restore calibration where a constant one cannot?

Section 5.6 shows a single multiplier on sigma fails, then says "a per-horizon or
input-dependent correction might still work". That sentence is a promissory note
and this pays it.

Design, identical in discipline to the constant-scalar test it extends: fit one
scalar PER HORIZON on ONE held-out episode, evaluate on the OTHER, in both
directions, so no scalar is ever evaluated on the episode that produced it. The
constant-scalar arm is recomputed here on exactly the same splits so the two are
comparable line for line -- the only difference between them is whether c may
depend on h.

The honest bar: a remedy must generalise across episodes. A per-horizon scalar has
five free parameters instead of one, so it fits its own episode better by
construction. What matters is the held-out column.

Writes results/task_d3_perhorizon.json.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import torch  # noqa: E402
import rwm_data as R  # noqa: E402
import rollout_eval as E  # noqa: E402
import rwm_metrics as MET  # noqa: E402
import score_reference as S  # noqa: E402

HORIZONS = (1, 8, 32, 128, 368)
START, LEN = E.START_STEP, 400
TARGET = 0.6827

paths = R.repo_paths()
cfg = R.load_reference_config(paths["lite"])
data, ep = R.load_data(paths["csv"], verbose=False)
split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"),
                     verbose=False)
HOLD = list(split["holdout_episodes"])


def episode_rollout(episode):
    starts = MET.non_overlapping_starts(ep, [episode], LEN)
    idx = np.asarray(starts)[:, None] + np.arange(LEN)[None, :]
    raw = data[idx]
    st = torch.as_tensor(R.normalise_state(raw[:, :, R.STATE_COLS],
                                           cfg["state_data_mean"], cfg["state_data_std"]),
                         dtype=torch.float32)
    ac = torch.as_tensor(raw[:, :, R.ACTION_COLS], dtype=torch.float32)
    sd = torch.load(paths["ckpt"], map_location="cpu")["system_dynamics_state_dict"]
    m = S.ReferenceRWM(sd); m.eval()
    pred, alea, epi, _, _ = m.rollout_uncertainty(st.clone(), ac, START, action_offset=1)
    return ((pred - st).abs().numpy().astype(np.float64),
            alea.numpy().astype(np.float64), epi.numpy().astype(np.float64), len(starts))


def cover(err, sig, c, h):
    sl = slice(START, START + h)
    e, g = err[:, sl], sig[:, sl] * c
    m = np.isfinite(g) & (g > 0)
    return float((e[m] <= g[m]).mean()) if m.any() else float("nan")


def fit_scalar(err, sig, h):
    lo, hi = 1e-9, 1e12
    for _ in range(300):
        mid = (lo * hi) ** 0.5
        if cover(err, sig, mid, h) < TARGET:
            lo = mid
        else:
            hi = mid
    return (lo * hi) ** 0.5


def main():
    cache = {e: episode_rollout(e) for e in HOLD}
    out = {"target_coverage": TARGET, "holdout_episodes": HOLD,
           "design": {"fit": "one held-out episode", "eval": "the other, both directions",
                      "traj_len": LEN, "start_step": START,
                      "trajectories_per_episode": {str(e): cache[e][3] for e in HOLD},
                      "note": ("the per-horizon scalar has 5 free parameters against the "
                               "constant scalar's 1, so it necessarily fits its own episode "
                               "better; only the held-out column is evidence")},
           "quantities": {}}

    print("D3 — PER-HORIZON RECALIBRATION")
    print("=" * 100)
    print(f"  released checkpoint, held-out episodes {HOLD}, target +-1 sigma coverage "
          f"{100*TARGET:.2f}%\n")

    for qi, qname in ((2, "aleatoric"), (3, "epistemic")):
        rec = {"fits": [], "constant_fits": []}
        print(f"  --- {qname} ---")
        print(f"    {'fit->test':<12}{'h':>6}{'c(h)':>13}{'cov after, per-h':>19}"
              f"{'c const':>13}{'cov after, const':>19}{'cov before':>13}")
        for fit_ep in HOLD:
            test_ep = [e for e in HOLD if e != fit_ep][0]
            fe, fa, fp, _ = cache[fit_ep]
            te, ta, tp, _ = cache[test_ep]
            fsig = fa if qname == "aleatoric" else fp
            tsig = ta if qname == "aleatoric" else tp
            c_const = fit_scalar(fe, fsig, 1)          # the section 5.6 recipe: fit at h=1
            for h in HORIZONS:
                c_h = fit_scalar(fe, fsig, h)
                cov_ph = cover(te, tsig, c_h, h)
                cov_cn = cover(te, tsig, c_const, h)
                cov_b = cover(te, tsig, 1.0, h)
                rec["fits"].append({"fit_episode": fit_ep, "test_episode": test_ep,
                                    "h": h, "c": c_h, "coverage_after": cov_ph,
                                    "coverage_before": cov_b})
                rec["constant_fits"].append({"fit_episode": fit_ep, "test_episode": test_ep,
                                             "h": h, "c": c_const,
                                             "coverage_after": cov_cn})
                print(f"    ep{fit_ep}->ep{test_ep:<7}{h:>6}{c_h:>13.4g}"
                      f"{100*cov_ph:>18.2f}%{c_const:>13.4g}{100*cov_cn:>18.2f}%"
                      f"{100*cov_b:>12.2f}%")
        # verdict: does the per-horizon scalar land within 10 points of target at
        # EVERY horizon, in BOTH directions?
        ok = [abs(f["coverage_after"] - TARGET) < 0.10 for f in rec["fits"]]
        okc = [abs(f["coverage_after"] - TARGET) < 0.10 for f in rec["constant_fits"]]
        worst = max(rec["fits"], key=lambda f: abs(f["coverage_after"] - TARGET))
        spread = [f["c"] for f in rec["fits"]]
        rec["verdict"] = {
            "per_horizon_cells_calibrated": int(sum(ok)), "n_cells": len(ok),
            "constant_cells_calibrated": int(sum(okc)),
            "per_horizon_restores_calibration": bool(all(ok)),
            "worst_cell": worst,
            "c_ratio_max_over_min": float(max(spread) / min(spread)),
            "tolerance": 0.10}
        out["quantities"][qname] = rec
        print(f"    -> per-horizon calibrated on {sum(ok)}/{len(ok)} held-out cells; "
              f"constant on {sum(okc)}/{len(okc)}. "
              f"c varies {max(spread)/min(spread):.3g}x across horizons.")
        print(f"    -> worst held-out cell: h={worst['h']} "
              f"({100*worst['coverage_after']:.2f}% against {100*TARGET:.2f}%)\n")

    op = os.path.join(R.RESULTS, "task_d3_perhorizon.json")
    json.dump(out, open(op, "w"), indent=2)
    print(f"  wrote {R.rel(op)}")


if __name__ == "__main__":
    main()
