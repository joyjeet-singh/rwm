"""
E7 -- two more free baselines for the ranking claim, because one adversary is one.

WHY. §6.7's ranking result rests on ensemble disagreement beating the FORECAST STEP
INDEX -- a counter that costs nothing and that neither original paper ran. It is a
good adversary and it is a single one, and a claim that survives exactly one
competitor is a claim about that competitor.

Two more, both free in the same sense: no ensemble, no second forward pass, nothing
the rollout does not already produce.

  step-size    ||mu_t - mu_{t-1}||, the magnitude of the model's own predicted
               state change. A model moving fast is a model in a regime where it is
               likely to be wrong, and this is available from the rollout itself.
  entry-res    the model's one-step error at the step BEFORE the forecast
               window opens -- a genuine prediction from 31 steps of history, and
               not a component of the error it is asked to rank. One scalar per
               trajectory, so it ranks trajectories and not steps; that is a real
               limit and is reported. See M-52 for what it replaced and why.

If disagreement beats these too, §6.7 stops resting on one competitor.

    python scripts/e7_free_baselines.py --power   the MDE, from quantities that
                                                  already exist (run FIRST)
    python scripts/e7_free_baselines.py           the comparison

The power run touches only disagreement, error and the forecast index -- all of
which §6.7 already reports. Neither new baseline is computed until M-51 is
committed.

Writes results/e7_free_baselines_power.json and results/e7_free_baselines.json.
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

START, LEN = E.START_STEP, 400
N_BOOT = 4000
Z95, Z80 = 1.959963985, 0.8416212336


def _corr(a, b):
    a, b = np.asarray(a).ravel(), np.asarray(b).ravel()
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 3 or a[m].std() == 0 or b[m].std() == 0:
        return np.nan
    return float(np.corrcoef(a[m], b[m])[0, 1])


def _partial(x, y, z):
    """r(x, y) with z regressed out of both, linearly."""
    x, y, z = (np.asarray(v, dtype=np.float64).ravel() for v in (x, y, z))
    m = np.isfinite(x) & np.isfinite(y) & np.isfinite(z)
    x, y, z = x[m], y[m], z[m]
    if len(x) < 4 or z.std() == 0:
        return np.nan
    Zm = np.column_stack([np.ones_like(z), z])
    rx = x - Zm @ np.linalg.lstsq(Zm, x, rcond=None)[0]
    ry = y - Zm @ np.linalg.lstsq(Zm, y, rcond=None)[0]
    return _corr(rx, ry)


def _within_step(x, y):
    """Correlation computed inside each forecast step and averaged.

    Any quantity that is constant within a step -- the forecast index is, and a
    per-trajectory scalar is -- contributes exactly nothing here. It is the
    strongest control available and needs no model of the confound's shape.
    """
    rs = [_corr(x[:, t], y[:, t]) for t in range(x.shape[1])]
    rs = [r for r in rs if np.isfinite(r)]
    return float(np.mean(rs)) if rs else np.nan


def load_panel():
    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    data, ep = R.load_data(paths["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"),
                         verbose=False)
    allep = sorted(set(split["train_episodes"]) | set(split["holdout_episodes"]))
    starts = MET.non_overlapping_starts(ep, allep, LEN)
    n_ind, n_traj = int(MET.n_independent(starts, LEN)), len(starts)
    sd = torch.load(paths["ckpt"], map_location="cpu")["system_dynamics_state_dict"]
    model = S.ReferenceRWM(sd); model.eval()
    idx = np.asarray(starts)[:, None] + np.arange(LEN)[None, :]
    raw = data[idx]
    st = torch.as_tensor(R.normalise_state(raw[:, :, R.STATE_COLS],
                                           cfg["state_data_mean"], cfg["state_data_std"]),
                         dtype=torch.float32)
    ac = torch.as_tensor(raw[:, :, R.ACTION_COLS], dtype=torch.float32)
    pred, alea, epi, alea_s, epi_s = model.rollout_uncertainty(
        st.clone(), ac, START, action_offset=1)
    P = pred.numpy().astype(np.float64)
    S_ = st.numpy().astype(np.float64)
    err = np.abs(P - S_)[:, START:].sum(-1)                 # (n_traj, T)
    dis = epi_s.numpy().astype(np.float64)[:, START:]
    T = err.shape[1]
    fidx = np.broadcast_to(np.arange(T, dtype=np.float64), err.shape).copy()
    # One extra rollout, opened one step earlier, so that step START-1 is a
    # genuine one-step prediction rather than a copy of the truth. 1.4 s.
    p2, _, _, _, _ = model.rollout_uncertainty(st.clone(), ac, START - 1,
                                               action_offset=1)
    entry_res = np.abs(p2.numpy().astype(np.float64)[:, START - 1]
                       - S_[:, START - 1]).sum(-1)
    assert entry_res.std() > 0, "the entry residual is constant; the rollout is not predicting"
    return {"P": P, "S": S_, "err": err, "dis": dis, "fidx": fidx,
            "entry_res": entry_res,
            "n_ind": n_ind, "n_traj": n_traj, "T": T}


def baselines(D):
    """The two free baselines.

    step-size costs nothing: it is a difference of predictions the rollout has
    already made.

    entry-res costs ONE EXTRA ROLLOUT here and nothing in deployment, and M-52
    records why the difference matters. M-51 specified "the residual on the last
    teacher-forced step of the history window", which does not exist in the
    artifact it named: rollout_uncertainty sets `pred = state.clone()` and only
    writes from start_step onward, so the whole history region is a copy of the
    truth and its residual is identically zero. The substitute is a genuine
    one-step prediction made from 31 steps of history -- one step BEFORE the
    forecast window opens, so it is not a component of the error it is asked to
    rank, which the obvious alternative (the error at the first forecast step)
    would have been.
    """
    P, S_ = D["P"], D["S"]
    step = np.linalg.norm(np.diff(P, axis=1), axis=-1)[:, START - 1:]
    step = step[:, :D["T"]]
    res = D["entry_res"]
    entry = np.broadcast_to(res[:, None], D["err"].shape).copy()
    return {"step-size": step, "entry-res": entry}


def power():
    D = load_panel()
    rng = np.random.default_rng(20260829)
    n = D["n_traj"]
    err, dis, fidx = D["err"], D["dis"], D["fidx"]

    def diff(i):
        """r(disagreement, error) - r(index, error), the shape M-51 compares."""
        return _corr(dis[i], err[i]) - _corr(fidx[i], err[i])

    def part(i):
        return _partial(dis[i], err[i], fidx[i])

    vals_d = [diff(rng.integers(0, n, n)) for _ in range(N_BOOT)]
    vals_p = [part(rng.integers(0, n, n)) for _ in range(N_BOOT)]
    vals_d = np.array([v for v in vals_d if np.isfinite(v)])
    vals_p = np.array([v for v in vals_p if np.isfinite(v)])
    se_d, se_p = float(vals_d.std(ddof=1)), float(vals_p.std(ddof=1))
    mde_d, mde_p = (Z95 + Z80) * se_d, (Z95 + Z80) * se_p

    rec = {
        "committed_before": "either new baseline is computed",
        "estimated_from": "disagreement, realised error and the forecast index — "
                          "all three already reported in §6.7. Neither new "
                          "baseline is touched here.",
        "n_independent": D["n_ind"], "n_trajectories": D["n_traj"],
        "n_steps": D["T"],
        "observed_r_disagreement": _corr(dis, err),
        "observed_r_index": _corr(fidx, err),
        "observed_margin_over_index": _corr(dis, err) - _corr(fidx, err),
        "observed_partial_given_index": _partial(dis, err, fidx),
        "bootstrap_se_margin": se_d,
        "bootstrap_se_partial": se_p,
        "mde_80pct_power": {"margin": float(mde_d), "partial": float(mde_p)},
        "n_boot": N_BOOT,
    }
    print("E7 — POWER, BEFORE THE NEW BASELINES EXIST")
    print("=" * 88)
    print(f"  n_independent = {D['n_ind']}, {D['n_traj']} trajectories, {D['T']} steps")
    print(f"  observed r(disagreement, error) = {rec['observed_r_disagreement']:+.4f}")
    print(f"  observed r(forecast index, error) = {rec['observed_r_index']:+.4f}")
    print(f"  margin over the index            = {rec['observed_margin_over_index']:+.4f}")
    print(f"  partial r given the index        = {rec['observed_partial_given_index']:+.4f}")
    print(f"  MDE on a margin                  = {mde_d:.4f}")
    print(f"  MDE on a partial correlation     = {mde_p:.4f}")
    json.dump(rec, open(os.path.join(R.RESULTS, "e7_free_baselines_power.json"), "w"),
              indent=2)
    print("  wrote results/e7_free_baselines_power.json")
    return 0


def main():
    PW = json.load(open(os.path.join(R.RESULTS, "e7_free_baselines_power.json")))
    TH = PW["mde_80pct_power"]
    D = load_panel()
    B = baselines(D)
    err, dis, fidx = D["err"], D["dis"], D["fidx"]
    rng = np.random.default_rng(20260829)
    n = D["n_traj"]

    def boot(fn):
        v = [fn(rng.integers(0, n, n)) for _ in range(N_BOOT)]
        v = np.array([x for x in v if np.isfinite(x)])
        return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]

    r_dis = _corr(dis, err)
    rows = []
    for name, b in list(B.items()) + [("forecast-index", fidx)]:
        r_b = _corr(b, err)
        part = _partial(dis, err, b)
        ws_dis = _within_step(dis, err)
        ws_b = _within_step(b, err)
        rows.append({
            "baseline": name,
            "free": True,
            "r_baseline_error": r_b,
            "r_disagreement_error": r_dis,
            "margin": r_dis - r_b,
            "margin_ci": boot(lambda i, b=b: _corr(dis[i], err[i]) - _corr(b[i], err[i])),
            "partial_disagreement_given_baseline": part,
            "partial_ci": boot(lambda i, b=b: _partial(dis[i], err[i], b[i])),
            "partial_baseline_given_disagreement": _partial(b, err, dis),
            "within_step_r_disagreement": ws_dis,
            "within_step_r_baseline": ws_b,
            "margin_beats_mde": bool(r_dis - r_b > TH["margin"]),
            "partial_beats_mde": bool(part > TH["partial"]),
        })

    new = [r for r in rows if r["baseline"] != "forecast-index"]
    beaten = [r for r in new if r["margin_beats_mde"] and r["partial_beats_mde"]]
    if len(beaten) == len(new):
        verdict = "SURVIVES BOTH"
    elif not beaten:
        verdict = "SURVIVES NEITHER"
    else:
        verdict = "SURVIVES " + ", ".join(r["baseline"] for r in beaten) + " ONLY"

    print("E7 — DISAGREEMENT AGAINST THREE FREE BASELINES")
    print("=" * 104)
    print(f"  released checkpoint, n_independent = {D['n_ind']}, {D['T']} forecast steps")
    print(f"  r(disagreement, error) = {r_dis:+.4f}")
    print(f"  MDE (M-51): margin {TH['margin']:.4f}, partial {TH['partial']:.4f}\n")
    print(f"  {'baseline':<16}{'r(base,err)':>13}{'margin':>10}{'partial':>10}"
          f"{'within-step base':>18}{'  verdict'}")
    for r in rows:
        tag = ("—" if r["baseline"] == "forecast-index"
               else ("beaten" if r["margin_beats_mde"] and r["partial_beats_mde"]
                     else "NOT beaten"))
        print(f"  {r['baseline']:<16}{r['r_baseline_error']:>+13.4f}"
              f"{r['margin']:>+10.4f}{r['partial_disagreement_given_baseline']:>+10.4f}"
              f"{r['within_step_r_baseline']:>+18.4f}  {tag}")
    print("=" * 104)
    print(f"  M-51 VERDICT: {verdict}")

    out = {"design": {"n_independent": D["n_ind"], "n_trajectories": D["n_traj"],
                      "n_steps": D["T"], "n_boot": N_BOOT,
                      "bootstrap_unit": "whole trajectory"},
           "thresholds": TH, "baselines": rows, "n_new_baselines": len(new),
           "n_beaten": len(beaten), "verdict": verdict}
    json.dump(out, open(os.path.join(R.RESULTS, "e7_free_baselines.json"), "w"), indent=2)
    print("  wrote results/e7_free_baselines.json")
    return 0


if __name__ == "__main__":
    sys.exit(power() if "--power" in sys.argv else main())
