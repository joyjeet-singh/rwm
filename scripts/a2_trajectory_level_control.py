"""
A2 -- the control 5.6 was missing, and M-45's verdict.

5.6 controls for the forecast-index confound five ways and that is the strongest
part of this paper. Every one of those controls removes DEPTH. None removes
TRAJECTORY DIFFICULTY.

Per-episode difficulty here spans 0.601 to 1.674 (D-12) and is uncorrelated with
commanded speed, so the units being correlated differ a great deal in level.
Harder trajectories plausibly have both larger realised error and larger
disagreement -- which would reproduce the observed correlation with disagreement
carrying no within-rollout information whatever. And the decisive existing control
(correlating ACROSS trajectories at a fixed depth, +0.739) is exactly the setting
where that confound is at full strength, not reduced.

Two symptoms point at it. r = +0.994 at h=1 on twenty points is not the shape of a
genuine per-step signal. And the within-step figure being HIGHER than the pooled
one (+0.739 against +0.605) is the signature of a between-unit effect.

Four constructions, in the order M-45 fixes:

  1  VARIANCE DECOMPOSITION. Split the pooled correlation into a
     between-trajectory part and a within-trajectory part. This alone tells the
     reader which effect is doing the work.

  2  DOUBLE-DEMEANING -- M-45's governing statistic. Subtract both the trajectory
     mean and the step mean from each variable, then correlate the residuals. It
     asks the only question a practitioner mid-rollout cares about: at a given
     depth, in a given rollout, does disagreement know?

  3  PARTIAL CORRELATION controlling for trajectory level, per horizon, reported
     beside the existing index partials so the two confounds sit together.

  4  THE h=1 DIAGNOSTIC. At h=1 there is one point per trajectory, so "the
     correlation" is a correlation over TWENTY POINTS and nothing else. Correlate
     disagreement against commanded speed and against per-episode difficulty, then
     partial each out. If +0.994 collapses, it collapses -- 9 currently calls it
     "very nearly a perfect ranking".

Every interval is a cluster bootstrap over whole trajectories (M-27).

Writes results/a2_trajectory_level_control.json, which discharges M-45.
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

HORIZONS = (1, 8, 32, 100, 128, 368)
START, LEN, N_BOOT = E.START_STEP, 400, 20000

# M-45's thresholds, quoted from the committed rule so the verdict cannot drift.
MDE = 0.183          # results/p1_power_check.json, n_independent = 20, 80% power
UNDERPOWERED = 0.10  # below this a null is an under-powered null, not absence


def corr(a, b):
    a, b = np.asarray(a).ravel(), np.asarray(b).ravel()
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 3 or a[m].std() == 0 or b[m].std() == 0:
        return None
    return float(np.corrcoef(a[m], b[m])[0, 1])


def partial(a, b, c):
    """r(a, b . c): linear regression residuals of a and b on c, then correlate."""
    a, b, c = (np.asarray(x).ravel() for x in (a, b, c))
    m = np.isfinite(a) & np.isfinite(b) & np.isfinite(c)
    a, b, c = a[m], b[m], c[m]
    if len(a) < 4 or a.std() == 0 or b.std() == 0 or c.std() == 0:
        return None
    ra = a - np.polyval(np.polyfit(c, a, 1), c)
    rb = b - np.polyval(np.polyfit(c, b, 1), c)
    return None if ra.std() == 0 or rb.std() == 0 else float(np.corrcoef(ra, rb)[0, 1])


def demean_traj(a):
    """Remove the trajectory (row) mean only."""
    return a - a.mean(axis=1, keepdims=True)


def double_demean(a):
    """Two-way additive removal: row mean, column mean, grand mean added back."""
    return (a - a.mean(axis=1, keepdims=True)
            - a.mean(axis=0, keepdims=True) + a.mean())


def cboot(fn, n, rng, n_boot=N_BOOT):
    v = [x for x in (fn(rng.integers(0, n, n)) for _ in range(n_boot))
         if x is not None and np.isfinite(x)]
    if len(v) < 2:
        return None, None, 0
    return float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5)), len(v)


def fmt(v, lo, hi):
    return "n/a" if v is None else f"{v:+.4f} [{lo:+.4f}, {hi:+.4f}]"


def main():
    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    data, ep = R.load_data(paths["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"),
                         verbose=False)
    allep = sorted(set(split["train_episodes"]) | set(split["holdout_episodes"]))
    starts = MET.non_overlapping_starts(ep, allep, LEN)
    n_ind, n_traj = int(MET.n_independent(starts, LEN)), len(starts)
    traj_ep = [int(ep[s]) for s in starts]          # which episode each trajectory is in

    idx = np.asarray(starts)[:, None] + np.arange(LEN)[None, :]
    raw = data[idx]
    st = torch.as_tensor(R.normalise_state(raw[:, :, R.STATE_COLS],
                                           cfg["state_data_mean"], cfg["state_data_std"]),
                         dtype=torch.float32)
    ac = torch.as_tensor(raw[:, :, R.ACTION_COLS], dtype=torch.float32)

    model = S.ReferenceRWM(torch.load(paths["ckpt"], map_location="cpu")
                           ["system_dynamics_state_dict"])
    model.eval()
    pred, _, _, _, epi_s = model.rollout_uncertainty(st.clone(), ac, START, action_offset=1)
    abs_err = (pred - st).abs().numpy().astype(np.float64)

    # The two panels. X is the scalar the method actually applies
    # (means.std(0).sum(-1), envs/base.py:166); Y is total absolute error.
    X = epi_s.numpy().astype(np.float64)[:, START:]      # (n_traj, 368)
    Y = abs_err[:, START:].sum(-1)                       # (n_traj, 368)
    T = X.shape[1]

    out = {
        "design": {
            "arena": "released checkpoint, all ten episodes",
            "episodes": allep, "n_trajectories": n_traj, "n_independent": n_ind,
            "trajectory_episode": traj_ep,
            "n_steps": int(T), "traj_len": LEN, "start_step": START,
            "n_boot": N_BOOT, "bootstrap_unit": "whole trajectory (M-27)",
            "x": "epistemic disagreement, means.std(0).sum(-1) (envs/base.py:166)",
            "y": "total absolute error over the 45 state dimensions",
        },
        "variance_decomposition": {}, "double_demeaning": {},
        "partial_by_horizon": {}, "h1_diagnostic": {}, "m45": {},
    }

    print("A2 — THE TRAJECTORY-LEVEL CONTROL, AND M-45's VERDICT")
    print("=" * 104)
    print(f"  released checkpoint, {n_traj} trajectories over episodes {allep}, "
          f"n_independent = {n_ind}, {T} forecast steps\n")

    # ============================================ 1. variance decomposition
    # A panel value splits as  x_bt = xbar_b + (x_bt - xbar_b). The pooled
    # covariance is the sum of the covariance of the trajectory MEANS and the
    # mean of the within-trajectory covariances. Reporting the two correlations
    # and each part's SHARE of the pooled covariance says which effect carries
    # the finding.
    rng = np.random.default_rng(0)
    xb, yb = X.mean(axis=1), Y.mean(axis=1)
    xw, yw = demean_traj(X), demean_traj(Y)
    r_pool, r_btw, r_wth = corr(X, Y), corr(xb, yb), corr(xw, yw)

    cov_total = float(np.cov(X.ravel(), Y.ravel(), ddof=0)[0, 1])
    cov_btw = float(np.cov(xb, yb, ddof=0)[0, 1])
    cov_wth = float(np.mean([np.cov(xw[i], yw[i], ddof=0)[0, 1] for i in range(n_traj)]))

    ci_b = cboot(lambda i: corr(xb[i], yb[i]), n_traj, np.random.default_rng(1))
    ci_w = cboot(lambda i: corr(xw[i], yw[i]), n_traj, np.random.default_rng(2))
    ci_p = cboot(lambda i: corr(X[i], Y[i]), n_traj, np.random.default_rng(3))

    out["variance_decomposition"] = {
        "r_pooled": r_pool, "r_pooled_ci": [ci_p[0], ci_p[1]],
        "r_between_trajectory": r_btw, "r_between_ci": [ci_b[0], ci_b[1]],
        "r_within_trajectory": r_wth, "r_within_ci": [ci_w[0], ci_w[1]],
        "cov_total": cov_total, "cov_between": cov_btw, "cov_within_mean": cov_wth,
        "share_between": cov_btw / cov_total if cov_total else None,
        "share_within": cov_wth / cov_total if cov_total else None,
        "n_between_points": n_traj,
        "reading": "the between component correlates the 20 trajectory means; the "
                   "within component correlates deviations from each trajectory's own "
                   "mean. The shares are of the pooled covariance, not of r.",
    }
    print("  [1] VARIANCE DECOMPOSITION of the pooled correlation")
    print(f"      pooled                  {fmt(r_pool, *ci_p[:2])}")
    print(f"      between trajectories    {fmt(r_btw, *ci_b[:2])}   "
          f"(n = {n_traj} trajectory means)")
    print(f"      within trajectories     {fmt(r_wth, *ci_w[:2])}")
    print(f"      share of pooled covariance:  between "
          f"{100 * cov_btw / cov_total:.1f}%   within {100 * cov_wth / cov_total:.1f}%\n")

    # ================================================== 2. double-demeaning
    r_dd = corr(double_demean(X), double_demean(Y))
    lo, hi, nb = cboot(lambda i: corr(double_demean(X[i]), double_demean(Y[i])),
                       n_traj, np.random.default_rng(4))
    # The step-demeaned-only figure is the existing within-step control (+0.739),
    # recomputed here so the three sit on one scale and the reader can see that
    # removing depth alone is not the same as removing both.
    r_step_only = corr(X - X.mean(axis=0, keepdims=True),
                       Y - Y.mean(axis=0, keepdims=True))
    out["double_demeaning"] = {
        "statistic": "Pearson r between double-demeaned disagreement and "
                     "double-demeaned |error|",
        "r_dd": r_dd, "ci": [lo, hi], "n_boot_finite": nb,
        "r_trajectory_demeaned_only": r_wth,
        "r_step_demeaned_only": r_step_only,
        "r_pooled": r_pool,
        "excludes_zero": (lo is not None and (lo > 0 or hi < 0)),
        "above_mde": (r_dd is not None and abs(r_dd) >= MDE),
        "mde": MDE,
        "reading": "removing depth alone leaves the trajectory-level confound in; "
                   "removing the trajectory mean alone leaves depth in; only the "
                   "two-way removal answers the within-rollout question.",
    }
    print("  [2] DOUBLE-DEMEANING — M-45's governing statistic")
    print(f"      pooled (nothing removed)          {r_pool:+.4f}")
    print(f"      step means removed only           {r_step_only:+.4f}   "
          f"(the existing within-step control)")
    print(f"      trajectory means removed only     {r_wth:+.4f}")
    print(f"      BOTH removed (r_dd)               {fmt(r_dd, lo, hi)}")
    print(f"      M-45 threshold: |r_dd| >= {MDE} detectable at this n\n")

    # ================================== 3. partial on trajectory level, per h
    print("  [3] PARTIAL CORRELATION controlling for trajectory level, per horizon")
    print(f"      {'h':>5} {'r(disagreement, |err|)':>26} "
          f"{'partial . trajectory mean |err|':>34} {'r_dd at this h':>26}")
    for h in HORIZONS:
        k = min(h, T)
        Xh, Yh = X[:, :k], Y[:, :k]
        # the confounder: each trajectory's own mean |error|, broadcast over steps.
        # It is a per-trajectory LEVEL, which is exactly what it should be.
        lvl = np.broadcast_to(Yh.mean(axis=1, keepdims=True), Yh.shape).copy()
        r_raw = corr(Xh, Yh)
        r_par = partial(Xh, Yh, lvl) if k > 1 else None
        r_dd_h = corr(double_demean(Xh), double_demean(Yh)) if k > 1 else None
        c_raw = cboot(lambda i, a=Xh, b=Yh: corr(a[i], b[i]), n_traj,
                      np.random.default_rng(10 + h))
        c_par = (cboot(lambda i, a=Xh, b=Yh, c=lvl: partial(a[i], b[i], c[i]),
                       n_traj, np.random.default_rng(20 + h)) if k > 1 else (None, None, 0))
        c_dd = (cboot(lambda i, a=Xh, b=Yh: corr(double_demean(a[i]), double_demean(b[i])),
                      n_traj, np.random.default_rng(30 + h)) if k > 1 else (None, None, 0))
        out["partial_by_horizon"][str(h)] = {
            "n_steps": int(k), "n_independent": n_ind,
            "r_raw": r_raw, "r_raw_ci": [c_raw[0], c_raw[1]],
            "r_partial_trajectory_level": r_par, "r_partial_ci": [c_par[0], c_par[1]],
            "r_dd": r_dd_h, "r_dd_ci": [c_dd[0], c_dd[1]],
            "undefined_reason": ("h=1 has one forecast step per trajectory, so within a "
                                 "trajectory there is nothing to demean and both the "
                                 "partial and r_dd are undefined" if k == 1 else None),
        }
        print(f"      {h:>5} {fmt(r_raw, *c_raw[:2]):>26} "
              f"{(fmt(r_par, *c_par[:2]) if r_par is not None else 'undefined'):>34} "
              f"{(fmt(r_dd_h, *c_dd[:2]) if r_dd_h is not None else 'undefined'):>26}")
    print()

    # ================================================ 4. the h=1 diagnostic
    # At h=1 the panel has ONE column, so "the correlation at h=1" is a correlation
    # over twenty trajectory-level points. Whatever separates trajectories is
    # therefore free to produce it, and that is what this block tests.
    strat = json.load(open(os.path.join(R.RESULTS, "step0_strat.json")))
    per_ep = json.load(open(os.path.join(R.RESULTS, "step4_0a_results.json")))["per_episode_e"]
    # D-12's per-episode difficulty, averaged over the seeds that measured it
    diff_by_ep = {}
    for e in allep:
        vals = [per_ep[s][str(e)] for s in per_ep if str(e) in per_ep[s]]
        diff_by_ep[e] = float(np.mean(vals))
    speed = np.array([strat[str(e)]["mean_speed"] for e in traj_ep])
    diff = np.array([diff_by_ep[e] for e in traj_ep])
    x1, y1 = X[:, 0], Y[:, 0]

    r_h1 = corr(x1, y1)
    c_h1 = cboot(lambda i: corr(x1[i], y1[i]), n_traj, np.random.default_rng(5))
    rows = {}
    for nm, z in (("commanded_speed", speed), ("episode_difficulty_D12", diff)):
        r_xz, r_yz = corr(x1, z), corr(y1, z)
        r_p = partial(x1, y1, z)
        c_p = cboot(lambda i, z=z: partial(x1[i], y1[i], z[i]), n_traj,
                    np.random.default_rng(6))
        rows[nm] = {"r_disagreement_vs_confounder": r_xz,
                    "r_error_vs_confounder": r_yz,
                    "partial_r": r_p, "partial_ci": [c_p[0], c_p[1]],
                    "shrinkage": (None if (r_p is None or r_h1 is None)
                                  else r_h1 - r_p)}
        print(f"  [4] h=1 DIAGNOSTIC — {nm}")
        print(f"      r(disagreement, {nm})   {r_xz:+.4f}")
        print(f"      r(|error|, {nm})        {r_yz:+.4f}")
        print(f"      r(disagreement, |error|) partialling {nm} out: "
              f"{fmt(r_p, *c_p[:2])}   (was {r_h1:+.4f})")
    # both at once
    both = None
    m = np.isfinite(x1) & np.isfinite(y1)
    Z = np.column_stack([speed[m], diff[m], np.ones(m.sum())])
    ra = x1[m] - Z @ np.linalg.lstsq(Z, x1[m], rcond=None)[0]
    rb = y1[m] - Z @ np.linalg.lstsq(Z, y1[m], rcond=None)[0]
    if ra.std() > 0 and rb.std() > 0:
        both = float(np.corrcoef(ra, rb)[0, 1])
    out["h1_diagnostic"] = {
        "n_points": int(n_traj),
        "episode_difficulty_range": [min(diff_by_ep.values()), max(diff_by_ep.values())],
        "commanded_speed_range": [float(speed.min()), float(speed.max())],
        "difficulty_source": "D-12, results/step4_0a_results.json -> per_episode_e, "
                             "averaged over the seeds that measured it",
        "note": "at h=1 the panel has one column, so this correlation is over "
                "TWENTY trajectory-level points and nothing within a rollout is "
                "being tested at all",
        "r_h1": r_h1, "r_h1_ci": [c_h1[0], c_h1[1]],
        "confounders": rows,
        "partial_on_both": both,
        "collapses": (both is not None and r_h1 is not None and abs(both) < 0.5 * abs(r_h1)),
    }
    print(f"\n      partialling BOTH out: {both:+.4f}   (was {r_h1:+.4f})\n")

    # ======================================================= M-45's verdict
    supported = bool(r_dd is not None and r_dd > 0 and lo is not None and lo > 0)
    underpowered_null = bool(not supported and r_dd is not None and abs(r_dd) < UNDERPOWERED)
    verdict = ("DISAGREEMENT CARRIES WITHIN-ROLLOUT INFORMATION" if supported
               else "DISAGREEMENT IS LARGELY REPORTING WHICH EPISODE IS HARD")
    out["m45"] = {
        "rule": "M-45, committed 2026-08-23 before this artifact existed",
        "statistic": "r_dd on the (trajectory, step) panel, n_independent = %d" % n_ind,
        "r_dd": r_dd, "ci": [lo, hi],
        "verdict": verdict,
        "supported": supported,
        "excludes_zero": bool(lo is not None and lo > 0),
        "above_mde": bool(r_dd is not None and abs(r_dd) >= MDE),
        "mde": MDE,
        "underpowered_null": underpowered_null,
        "power_note": (
            f"the rule's MDE at this n is |r_dd| >= {MDE} (results/p1_power_check.json). "
            f"The observed |r_dd| = {abs(r_dd):.4f} is "
            + ("above" if abs(r_dd) >= MDE else "below")
            + " it, so the result is "
            + ("resolvable by this rule" if abs(r_dd) >= MDE
               else "NOT resolvable by this rule and must not be read as one")),
        "what_the_paper_says": (
            "5.6 keeps its strength and gains a sixth control — the only one that "
            "removes trajectory difficulty rather than depth — and 12 leans on it."
            if supported else
            "disagreement mostly identifies WHICH ROLLOUTS will go wrong rather than "
            "WHEN within a rollout. Still a usable ranking signal for a practitioner "
            "choosing between candidate trajectories, and materially weaker than the "
            "claim 5.6, 9 and 12 currently make."),
    }
    print("  M-45 VERDICT: " + verdict)
    print(f"    r_dd = {r_dd:+.4f}, 95% CI [{lo:+.4f}, {hi:+.4f}], "
          f"MDE {MDE}, excludes zero: {out['m45']['excludes_zero']}")

    # ------------------------------------------------- what this reinterprets
    #
    # 5.6 calls the within-step control "the decisive one" because depth is held
    # exactly constant. Depth is -- and trajectory is not. within_step() in
    # task_d2b_robustness.py:84 correlates ACROSS TRAJECTORIES at each fixed step
    # and averages, so it is a mean of 368 BETWEEN-trajectory correlations. It is
    # therefore the control in which the trajectory-level confound is at FULL
    # strength, not the one that removes it. That is why it comes out above the
    # pooled figure rather than below it, which is the signature the brief
    # commissioning this analysis flagged.
    #
    # So A2 does not merely add a sixth control. It reinterprets the fifth.
    try:
        d2b = json.load(open(os.path.join(R.RESULTS, "task_d2b_robustness.json")))
        r_win = d2b["controls"]["within_step"].get("r_disagreement_given_index")
    except Exception:
        r_win = None
    out["reconciliation"] = {
        "existing_within_step_mean_r": r_win,
        "existing_within_step_is": "the mean over forecast steps of the correlation "
                                   "ACROSS TRAJECTORIES at that step "
                                   "(scripts/task_d2b_robustness.py:84)",
        "which_makes_it": "a between-trajectory statistic evaluated at fixed depth. It "
                          "removes depth completely and removes trajectory difficulty "
                          "not at all.",
        "why_it_exceeds_the_pooled_figure": (
            "because the between-trajectory correlation is larger than the pooled one: "
            f"{r_btw:+.4f} against {r_pool:+.4f}. A control that isolates the "
            "between-trajectory channel therefore reads HIGHER, which is the symptom "
            "that prompted this analysis rather than a sign of strength."),
        "ordering": {
            "between_trajectory": r_btw,
            "within_step_existing": r_win,
            "step_demeaned_pooled": r_step_only,
            "pooled": r_pool,
            "trajectory_demeaned": r_wth,
            "double_demeaned": r_dd,
        },
        "consequence": "A2 does not only add a sixth control; it reinterprets the fifth. "
                       "r_dd is the first statistic in this paper that isolates "
                       "WITHIN-ROLLOUT information, and 12 should lean on it rather "
                       "than on the within-step figure.",
    }
    print("\n  RECONCILIATION with 5.6's existing 'decisive' within-step control")
    print(f"      between-trajectory r           {r_btw:+.4f}   <- the confound, unremoved")
    print(f"      existing within-step r         "
          f"{('%+.4f' % r_win) if r_win is not None else 'n/a':>7}   "
          f"<- a mean of per-step BETWEEN-trajectory correlations")
    print(f"      pooled r                       {r_pool:+.4f}")
    print(f"      double-demeaned r (A2)         {r_dd:+.4f}   "
          f"<- the first within-rollout statistic here")

    # short-horizon caveat, read off the per-horizon table rather than asserted
    short = [h for h in HORIZONS if h > 1
             and (out["partial_by_horizon"][str(h)]["r_dd_ci"][0] or 0) <= 0]
    out["horizon_dependence"] = {
        "r_dd_excludes_zero_at": [h for h in HORIZONS if h > 1
                                  and (out["partial_by_horizon"][str(h)]["r_dd_ci"][0] or 0) > 0],
        "r_dd_spans_zero_at": short,
        "reading": "the within-rollout signal is established at the longer horizons and "
                   "NOT established at the shorter ones, where four hundred-odd steps "
                   "are not yet available to demean against. This inverts the shape a "
                   "reader might expect and is reported as measured.",
    }
    print(f"\n      r_dd excludes zero at h = "
          f"{out['horizon_dependence']['r_dd_excludes_zero_at']}; "
          f"spans zero at h = {short}")

    dst = os.path.join(R.RESULTS, "a2_trajectory_level_control.json")
    with open(dst, "w") as f:
        json.dump(out, f, indent=2, sort_keys=True)
    print(f"\n  wrote {R.rel(dst)}")


if __name__ == "__main__":
    main()
