"""B2 — measure the uncertainty quantity the method ACTUALLY uses.

B1 established that arXiv:2504.16680 penalises rewards with EPISTEMIC uncertainty
(Eq. 4-5), and that the released code does the same: envs/base.py:142 discards the
aleatoric term and base.py:166 applies `uncertainty_penalty_weight * epistemic`.
Section 4 of the paper measures the aleatoric head, which the method does not use.

So this measures, on the released five-member checkpoint, held-out episodes,
action offset 1:

  aleatoric  stds.mean(0)          per dim   (system_dynamics.py:125, what S4 measured)
  epistemic  means.std(0)          per dim   (system_dynamics.py:126, what is used)
  total      sqrt(alea^2 + epi^2)  per dim

each at h = 1, 8, 32, 128, 368: coverage at +-1 and +-2 sigma, the ratio of mean
absolute error to mean sigma, and the per-dimension correlation between sigma and
realised absolute error.

Our own arms are ensemble size 1, where epistemic is identically zero by
construction, so this measurement is only possible on the released checkpoint.

Writes results/task_b2_epistemic.json and a report.
"""
import json
import os
import sys
from math import comb

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import torch  # noqa: E402
import rwm_data as R  # noqa: E402
import rollout_eval as E  # noqa: E402
import rwm_metrics as MET  # noqa: E402
import score_reference as S  # noqa: E402

HORIZONS = (1, 8, 32, 100, 128, 368)
START = E.START_STEP
LEN = 400


def sign_p(k, n):
    if n == 0:
        return float("nan")
    tail = (sum(comb(n, i) for i in range(k, n + 1)) if 2 * k >= n
            else sum(comb(n, i) for i in range(0, k + 1)))
    return min(1.0, 2.0 * tail / 2 ** n)


def block(err, sig, name):
    """err, sig: (B, H, D) absolute error and sigma. Returns the calibration record."""
    e = err.reshape(-1, err.shape[-1])
    s = sig.reshape(-1, sig.shape[-1])
    finite = np.isfinite(s) & (s > 0)
    rec = {
        "name": name,
        "mean_sigma": float(np.nanmean(s)),
        "mean_abs_err": float(np.nanmean(e)),
        "ratio_err_over_sigma": float(np.nanmean(e) / np.nanmean(s)) if np.nanmean(s) > 0 else None,
        "coverage_pm1": float(np.nanmean(e <= s)),
        "coverage_pm2": float(np.nanmean(e <= 2 * s)),
        "frac_sigma_positive": float(finite.mean()),
    }
    # per-dimension correlation between sigma and realised |error|
    cors = []
    for d in range(e.shape[1]):
        sd, ed = s[:, d], e[:, d]
        m = np.isfinite(sd) & np.isfinite(ed)
        if m.sum() > 2 and sd[m].std() > 0 and ed[m].std() > 0:
            cors.append(float(np.corrcoef(sd[m], ed[m])[0, 1]))
    cors = np.array(cors)
    npos = int((cors > 0).sum())
    rec.update({"n_finite_corr": int(len(cors)),
                "corr_mean": float(cors.mean()) if len(cors) else None,
                "corr_median": float(np.median(cors)) if len(cors) else None,
                "n_positive": npos,
                "sign_p_two_sided": sign_p(npos, len(cors)) if len(cors) else None})
    return rec


def main():
    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    data, ep = R.load_data(paths["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"),
                         verbose=False)
    hold = list(split["holdout_episodes"])
    starts = MET.non_overlapping_starts(ep, hold, LEN)
    n_ind = MET.n_independent(starts, LEN)

    sd = torch.load(paths["ckpt"], map_location="cpu")["system_dynamics_state_dict"]
    model = S.ReferenceRWM(sd)
    model.eval()

    idx = np.asarray(starts)[:, None] + np.arange(LEN)[None, :]
    raw = data[idx]
    st = torch.as_tensor(R.normalise_state(raw[:, :, R.STATE_COLS],
                                           cfg["state_data_mean"], cfg["state_data_std"]),
                         dtype=torch.float32)
    ac = torch.as_tensor(raw[:, :, R.ACTION_COLS], dtype=torch.float32)

    pred, alea, epi, alea_s, epi_s = model.rollout_uncertainty(
        st.clone(), ac, START, action_offset=1)

    abs_err = (pred - st).abs().numpy()
    alea = alea.numpy()
    epi = epi.numpy()
    total = np.sqrt(alea ** 2 + epi ** 2)

    out = {
        "design": {
            "checkpoint": R.rel(paths["ckpt"]),
            "ensemble_size": model.ensemble,
            "arena": "out-of-sample", "holdout_episodes": hold,
            "trajectories": len(starts), "n_independent": int(n_ind),
            "traj_len": LEN, "start_step": START, "action_offset": 1,
            "note": ("epistemic is identically zero for ensemble_size 1, so this "
                     "measurement is possible only on the released checkpoint"),
        },
        "by_horizon": {},
    }

    print("B2 — THE UNCERTAINTY THE METHOD ACTUALLY USES")
    print("=" * 96)
    print(f"  released checkpoint, {model.ensemble} members, out-of-sample episodes {hold}, "
          f"n_independent = {n_ind}\n")
    hdr = (f"  {'h':>4} {'quantity':<11} {'mean sigma':>11} {'mean|err|':>10} "
           f"{'err/sigma':>10} {'cov+-1s':>9} {'cov+-2s':>9} {'r>0':>8} {'P':>10}")
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))

    for h in HORIZONS:
        sl = slice(START, START + h)
        e = abs_err[:, sl]
        rec = {}
        for name, sig in (("aleatoric", alea[:, sl]),
                          ("epistemic", epi[:, sl]),
                          ("total", total[:, sl])):
            b = block(e, sig, name)
            rec[name] = b
            print(f"  {h:>4} {name:<11} {b['mean_sigma']:>11.3e} {b['mean_abs_err']:>10.4f} "
                  f"{b['ratio_err_over_sigma']:>10.1f} {100*b['coverage_pm1']:>8.2f}% "
                  f"{100*b['coverage_pm2']:>8.2f}% {b['n_positive']:>3}/{b['n_finite_corr']:<4} "
                  f"{b['sign_p_two_sided']:>10.2e}")
        out["by_horizon"][str(h)] = rec
        print()

    # the released scalar penalty quantity itself, against total absolute error
    es = epi_s.numpy()[:, START:]
    tot_err = abs_err[:, START:].sum(-1)
    m = np.isfinite(es) & np.isfinite(tot_err)
    out["released_scalar_penalty"] = {
        "definition": "means.std(0).sum(-1)  (system_dynamics.py:126)",
        "applied_at": "envs/base.py:166  rewards += uncertainty_penalty_weight * epistemic * dt",
        "weight": -1.0,
        "corr_with_total_abs_error": float(np.corrcoef(es[m], tot_err[m])[0, 1]),
        "mean": float(es[m].mean()),
        "paper_defines_variance_code_uses_std": True,
    }
    print("  released scalar penalty (means.std(0).sum(-1), the quantity in base.py:166):")
    print(f"    correlation with total absolute error over the rollout: "
          f"{out['released_scalar_penalty']['corr_with_total_abs_error']:+.4f}")
    print(f"    mean value: {out['released_scalar_penalty']['mean']:.4e}")

    op = os.path.join(R.RESULTS, "task_b2_epistemic.json")
    json.dump(out, open(op, "w"), indent=2)
    print(f"\n  wrote {R.rel(op)}")


if __name__ == "__main__":
    main()
