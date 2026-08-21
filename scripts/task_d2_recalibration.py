"""D2 — can one scalar fix the calibration?

Fit a single multiplier c on sigma, per model, and report coverage after. The
question the brief poses: if one scalar restores calibration, the head learns the
right shape and the wrong scale, which is constructive and gives users a concrete
recommendation. If a scalar cannot fix it because coverage degrades with horizon,
that is harder evidence that the failure is structural.

The scalar is fitted on ONE held-out episode and evaluated on the OTHER, in both
directions, so it is never fitted on its own test set. Two fits are reported:

  c@h1     matches +-1 sigma coverage to 68.3% at h = 1 only
  c@all    matches it over the whole 368-step rollout

and each is then evaluated at h = 1, 8, 32, 128, 368 on the other episode. If
c@h1 restores h=1 but not the rest, the failure is a horizon failure, not a
scale one.

Covers the four models of task1_calibration plus the released checkpoint's
EPISTEMIC term, which C-14 shows is the quantity the method actually uses.

Writes results/task_d2_recalibration.json.
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
import rwm_model as M  # noqa: E402
import score_reference as S  # noqa: E402

TARGET = 0.6827
HORIZONS = (1, 8, 32, 128, 368)
START = E.START_STEP
LEN = 400
SEEDS = (0, 1, 2)

paths = R.repo_paths()
cfg = R.load_reference_config(paths["lite"])
data, ep = R.load_data(paths["csv"], verbose=False)
split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"), verbose=False)
HOLD = list(split["holdout_episodes"])


def traj(episode):
    st_ = MET.non_overlapping_starts(ep, [episode], LEN)
    idx = np.asarray(st_)[:, None] + np.arange(LEN)[None, :]
    raw = data[idx]
    s = torch.as_tensor(R.normalise_state(raw[:, :, R.STATE_COLS],
                                          cfg["state_data_mean"], cfg["state_data_std"]),
                        dtype=torch.float32)
    a = torch.as_tensor(raw[:, :, R.ACTION_COLS], dtype=torch.float32)
    return s, a, len(st_)


def arm_model(tag, seed):
    m = M.build_from_config(cfg, ensemble_size=1)
    m.load_state_dict(torch.load(f"runs/armA_seed{seed}{tag}/weights_2500.pt",
                                 map_location="cpu")["model_state_dict"], strict=True)
    m.eval()
    return m


def armB_model(seed):
    m = M.build_from_config(cfg, ensemble_size=1)
    m.load_state_dict(torch.load(f"runs/armB_seed{seed}/weights_2500.pt",
                                 map_location="cpu")["model_state_dict"], strict=True)
    m.eval()
    return m


def collect(kind, episode):
    """Return (abs_err, sigma) arrays of shape (B, T, D) for one episode."""
    s, a, _ = traj(episode)
    if kind == "released_epistemic":
        sd = torch.load(paths["ckpt"], map_location="cpu")["system_dynamics_state_dict"]
        m = S.ReferenceRWM(sd); m.eval()
        pred, alea, epi, _, _ = m.rollout_uncertainty(s.clone(), a, START, action_offset=1)
        return (pred - s).abs().numpy(), epi.numpy()
    if kind == "released_aleatoric":
        sd = torch.load(paths["ckpt"], map_location="cpu")["system_dynamics_state_dict"]
        m = S.ReferenceRWM(sd); m.eval()
        pred, alea, epi, _, _ = m.rollout_uncertainty(s.clone(), a, START, action_offset=1)
        return (pred - s).abs().numpy(), alea.numpy()
    errs, sigs = [], []
    for seed in SEEDS:
        m = armB_model(seed) if kind == "armB" else arm_model(
            "_nll" if kind == "nll" else "", seed)
        pred, sig = m.rollout_full(s.clone(), a, START, action_offset=1)
        errs.append((pred - s).abs().numpy())
        sigs.append(sig.numpy())
    return np.concatenate(errs), np.concatenate(sigs)


def cover(err, sig, c, h):
    sl = slice(START, START + h)
    e, g = err[:, sl], sig[:, sl] * c
    m = np.isfinite(g) & (g > 0)
    return float((e[m] <= g[m]).mean()) if m.any() else float("nan")


def fit_scalar(err, sig, h):
    """Smallest c whose +-1 sigma coverage reaches the calibrated target."""
    lo, hi = 1e-6, 1e9
    for _ in range(200):
        mid = (lo * hi) ** 0.5
        if cover(err, sig, mid, h) < TARGET:
            lo = mid
        else:
            hi = mid
    return (lo * hi) ** 0.5


def main():
    MODELS = [("faithful (mse)", "mse"), ("corrected (nll)", "nll"),
              ("teacher-forced armB", "armB"),
              ("released aleatoric", "released_aleatoric"),
              ("released EPISTEMIC (used by the method)", "released_epistemic")]
    out = {"target_coverage": TARGET, "holdout_episodes": HOLD, "models": {}}
    print("D2 — POST-HOC RECALIBRATION")
    print("=" * 100)
    print(f"  one scalar per model, fitted on one held-out episode, evaluated on the other")
    print(f"  target +-1 sigma coverage {100*TARGET:.1f}%\n")

    for label, kind in MODELS:
        cache = {e: collect(kind, e) for e in HOLD}
        rec = {"fits": []}
        print(f"  {label}")
        for fit_ep in HOLD:
            test_ep = [e for e in HOLD if e != fit_ep][0]
            fe, fs = cache[fit_ep]
            te, ts = cache[test_ep]
            for mode, hh in (("c@h1", 1), ("c@all", 368)):
                c = fit_scalar(fe, fs, hh)
                covs = {h: cover(te, ts, c, h) for h in HORIZONS}
                base = {h: cover(te, ts, 1.0, h) for h in HORIZONS}
                rec["fits"].append({"fit_episode": fit_ep, "test_episode": test_ep,
                                    "mode": mode, "scalar": c,
                                    "coverage_after": covs, "coverage_before": base})
                cs = "  ".join(f"h{h}:{100*covs[h]:5.1f}%" for h in HORIZONS)
                print(f"    fit ep{fit_ep} -> test ep{test_ep}  {mode:<6} c={c:>10.4g}   {cs}")
        out["models"][label] = rec
        b = rec["fits"][0]["coverage_before"]
        print(f"    {'before (c=1)':<38}" + "  ".join(f"h{h}:{100*b[h]:5.1f}%" for h in HORIZONS))
        print()

    # verdict: does a single scalar hold across horizons?
    v = {}
    for label, rec in out["models"].items():
        f1 = [f for f in rec["fits"] if f["mode"] == "c@h1"]
        ok_h1 = all(abs(f["coverage_after"][1] - TARGET) < 0.10 for f in f1)
        ok_far = all(abs(f["coverage_after"][368] - TARGET) < 0.10 for f in f1)
        v[label] = {"c_at_h1_restores_h1": ok_h1, "same_c_restores_h368": ok_far,
                    "scalars": [f["scalar"] for f in f1]}
    out["verdict"] = v
    print("  does one scalar generalise across horizon?")
    for k, r in v.items():
        print(f"    {k:<42} h=1 {'yes' if r['c_at_h1_restores_h1'] else 'NO':<4} "
              f"h=368 {'yes' if r['same_c_restores_h368'] else 'NO'}")

    op = os.path.join(R.RESULTS, "task_d2_recalibration.json")
    json.dump(out, open(op, "w"), indent=2)
    print(f"\n  wrote {R.rel(op)}")


if __name__ == "__main__":
    main()
