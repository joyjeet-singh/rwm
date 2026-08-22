"""D2 robustness — is the forecast-index control adequate?

D2 reports a PARTIAL correlation of ensemble disagreement with realised error,
controlling for forecast step index, and finds it barely moves (+0.605 -> +0.596).
That is the paper's one claim that STRENGTHENS an original result, so it deserves
the hardest test we can give it.

The concern is specific and fair: the partial correlation regresses out the index
LINEARLY, and error does not grow linearly with rollout depth. An under-powered
control leaves index-driven variance in the residuals and inflates what
disagreement appears to contribute. If the finding is an artifact of a weak
control, a stronger control will destroy it.

Five controls of increasing strength, on the same rollouts:

  linear         partial r on the raw index                       (what D2 reports)
  log            partial r on log(1 + index)
  cubic          partial r on a degree-3 polynomial in the index
  spearman       rank partial correlation -- removes ANY monotone dependence
  within-step    correlation computed WITHIN each forecast step and averaged;
                 the index is held exactly constant, so it cannot contribute at
                 all. This is the strongest control available and needs no model
                 of the index-error relationship.

The within-step control is the one that settles it. If disagreement still tracks
error when the forecast step is fixed, it is not re-encoding the clock.

Also reported: the same five for the forecast index against error, controlling
for disagreement -- the symmetric question, which no result should be quoted
without.

Writes results/task_d2b_robustness.json.
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

START, LEN, N_BOOT = E.START_STEP, 400, 20000


def _corr(a, b):
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 3 or a[m].std() == 0 or b[m].std() == 0:
        return np.nan
    return float(np.corrcoef(a[m], b[m])[0, 1])


def _resid(y, X):
    """Residual of y after least-squares removal of the columns of X (plus intercept)."""
    A = np.column_stack([np.ones(len(y))] + list(X))
    beta, *_ = np.linalg.lstsq(A, y, rcond=None)
    return y - A @ beta


def partial(x, y, z, mode):
    """r(x, y . z) under the named control."""
    x, y, z = x.ravel(), y.ravel(), z.ravel()
    m = np.isfinite(x) & np.isfinite(y) & np.isfinite(z)
    x, y, z = x[m], y[m], z[m]
    if mode == "spearman":
        r = lambda v: np.argsort(np.argsort(v)).astype(np.float64)
        x, y, z = r(x), r(y), r(z)
        cols = [z]
    elif mode == "linear":
        cols = [z]
    elif mode == "log":
        cols = [np.log1p(z - z.min())]
    elif mode == "cubic":
        zz = (z - z.mean()) / max(z.std(), 1e-12)
        cols = [zz, zz ** 2, zz ** 3]
    else:
        raise ValueError(mode)
    return _corr(_resid(x, cols), _resid(y, cols))


def within_step(x, y):
    """Correlation across trajectories WITHIN each forecast step, averaged.

    The index is exactly constant inside each step, so it contributes nothing by
    construction. x, y are (n_traj, T).
    """
    rs, ns = [], 0
    for t in range(x.shape[1]):
        r = _corr(x[:, t], y[:, t])
        if np.isfinite(r):
            rs.append(r); ns += 1
    return (float(np.mean(rs)) if rs else np.nan,
            float(np.median(rs)) if rs else np.nan,
            int(sum(1 for r in rs if r > 0)), ns)


def main():
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
    pred, alea, epi, alea_s, epi_s = model.rollout_uncertainty(st.clone(), ac, START,
                                                               action_offset=1)
    err = (pred - st).abs().numpy().astype(np.float64)[:, START:].sum(-1)   # (n_traj, T)
    dis = epi_s.numpy().astype(np.float64)[:, START:]                       # (n_traj, T)
    T = err.shape[1]
    fidx = np.broadcast_to(np.arange(T, dtype=np.float64), err.shape).copy()

    rng = np.random.default_rng(0)

    def boot(fn):
        v = []
        for _ in range(2000):
            i = rng.integers(0, n_traj, n_traj)
            r = fn(i)
            if r is not None and np.isfinite(r):
                v.append(r)
        return (float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))) if v else (None, None)

    out = {"design": {"n_independent": n_ind, "n_trajectories": n_traj, "n_steps": int(T),
                      "n_boot": 2000, "bootstrap_unit": "whole trajectory"},
           "raw": {"r_disagreement_error": _corr(dis.ravel(), err.ravel()),
                   "r_index_error": _corr(fidx.ravel(), err.ravel())},
           "controls": {}}

    print("D2b — IS THE FORECAST-INDEX CONTROL ADEQUATE?")
    print("=" * 100)
    print(f"  released checkpoint, n_independent = {n_ind}, {T} forecast steps\n")
    print(f"  raw r(disagreement, error) = {out['raw']['r_disagreement_error']:+.3f}")
    print(f"  raw r(step index,   error) = {out['raw']['r_index_error']:+.3f}\n")
    print(f"  {'control':<14}{'r(disagr, err . index)':>26}{'r(index, err . disagr)':>26}")
    print("  " + "-" * 64)
    for mode in ("linear", "log", "cubic", "spearman"):
        a = partial(dis, err, fidx, mode)
        b = partial(fidx, err, dis, mode)
        lo, hi = boot(lambda i: partial(dis[i], err[i], fidx[i], mode))
        out["controls"][mode] = {"r_disagreement_given_index": a,
                                 "ci_lo": lo, "ci_hi": hi,
                                 "r_index_given_disagreement": b}
        print(f"  {mode:<14}{f'{a:+.3f} [{lo:+.3f}, {hi:+.3f}]':>26}{b:>26.3f}")

    mean_r, med_r, npos, nst = within_step(dis, err)
    lo, hi = boot(lambda i: within_step(dis[i], err[i])[0])
    out["controls"]["within_step"] = {
        "r_disagreement_given_index": mean_r, "median": med_r,
        "ci_lo": lo, "ci_hi": hi,
        "steps_positive": npos, "n_steps": nst,
        "note": ("correlation across trajectories at a FIXED forecast step, averaged over "
                 "steps; the index is constant within each step so it cannot contribute")}
    print(f"  {'within-step':<14}{f'{mean_r:+.3f} [{lo:+.3f}, {hi:+.3f}]':>26}"
          f"{'n/a by construction':>26}")
    print(f"\n  within-step: positive on {npos} of {nst} forecast steps, median r = {med_r:+.3f}")

    weakest = min(v["r_disagreement_given_index"] for v in out["controls"].values()
                  if np.isfinite(v["r_disagreement_given_index"]))
    out["verdict"] = {
        "weakest_partial": weakest,
        "survives_all_controls": bool(weakest > 0.2),
        "beats_index_under_all_controls": all(
            v["r_disagreement_given_index"] > abs(v.get("r_index_given_disagreement", 0))
            for k, v in out["controls"].items() if k != "within_step")}
    print(f"\n  weakest partial across all controls: {weakest:+.3f}")
    print(f"  survives every control: {out['verdict']['survives_all_controls']}")

    op = os.path.join(R.RESULTS, "task_d2b_robustness.json")
    json.dump(out, open(op, "w"), indent=2)
    print(f"\n  wrote {R.rel(op)}")


if __name__ == "__main__":
    main()
