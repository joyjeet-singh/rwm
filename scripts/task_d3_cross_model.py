"""D3 cross-model — is section 6.8's lookup table a property of the HORIZON or of the MODEL?

Section 6.8 establishes its per-horizon multiplier ACROSS EPISODES: each multiplier
is fitted on one held-out episode and scored on the other, in both directions. That
says nothing about whether the same table works on a DIFFERENT MODEL. This script is
the measurement that asks, and it is governed by M-69, which was committed before any
of it existed (fad7db7, with results/p4_transfer_power.json).

M-69's design, carried out here exactly as written and not reinterpreted:

  MODELS      the released checkpoint (section 6.8's own model) and Arm A at ensemble
              size 5, seeds 0/1/2, scored through the same entry point
              (score_reference.ReferenceRWM.rollout_uncertainty, action offset 1,
              start step 32) that section 6.8 uses.
  ARENA       the out-of-sample held-out pair, 4 non-overlapping 400-step trajectories,
              n_independent = 4. Section 6.8's arena, unchanged.
  HORIZONS    1, 8, 32, 100, 128, 368 — section 6.8's grid, not extended.
  DIRECTIONS  1: multipliers fitted on Arm A, scored on the released checkpoint.
              2: multipliers fitted on the released checkpoint, scored on Arm A.
  CELL        one (quantity, horizon, Arm A seed, direction): 2 x 6 x 3 x 2 = 72.

  GOVERNING STATISTIC, paired:

      Delta = 100 x ( coverage under the multiplier fitted on the OTHER model
                      - coverage under the multiplier fitted on the SAME model )

  on the same trajectories, horizon, quantity and scored model, so everything the two
  scalars share cancels. Both fold directions enter ONE statistic: each of the 4
  held-out trajectories is scored under the multiplier fitted on the episode it does
  NOT belong to, and the counts are pooled over all 4, which puts the statistic at
  n_independent = 4 without any multiplier ever being scored on the episode that
  produced it. Intervals are 95% cluster bootstrap over WHOLE TRAJECTORIES (M-27),
  20,000 resamples; at n = 4 there are 4^4 = 256 distinct resamples and every interval
  is quantised at that resolution.

  VERDICT     three ordered, exhaustive, mutually exclusive branches, first match wins:
              1 DOES NOT TRANSFER  any cell's 95% paired interval wholly OUTSIDE +-10
              2 TRANSFERS          every cell's interval wholly INSIDE +-10
              3 UNDERPOWERED       otherwise (at least one interval straddles an edge)
              Stated once over both directions together (the headline, and the stricter
              reading) and once per direction.

  REPORTED, NOT GOVERNING. The absolute column section 12 of the revision brief asks
  for — held-out cells whose coverage under a multiplier fitted on a DIFFERENT model
  lands within 10 points of the 68.27% nominal, counted per fold, 72 per quantity. It
  is UNPOWERED and labelled so: results/p4_transfer_power.json says the binding MDE on
  that unpaired quantity runs 12.55 to 40.62 points against a 10-point band and
  tolerance_resolvable is false at 0 of 12 (quantity, horizon) pairs, so a cell landing
  inside the band is not evidence a multiplier transferred — it is evidence this arena
  cannot tell. That is why M-69 governs on the paired change, and it was decided there,
  before this table existed. Arm A's own-model held-out coverage and the ratio between
  the two models' multipliers are reported for the same reason: so a reader can see
  whether section 6.8's remedy works on a model we trained at all.

WHAT THIS DOES NOT TOUCH. Section 6.8's own values. The released checkpoint's
per-horizon multipliers are READ from results/task_d3_perhorizon.json and never
refitted; the script asserts that scoring the released checkpoint under those published
scalars reproduces the published held-out coverages exactly, which is what makes the
"same-model" arm of Delta section 6.8's own number rather than a re-derivation of it.
results/task_d3_perhorizon.json is opened read-only and is not rewritten.

Trains nothing. Writes results/task_d3_cross_model.json.
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

HORIZONS = (1, 8, 32, 100, 128, 368)
START, LEN = E.START_STEP, 400
SEEDS = (0, 1, 2)
ENSEMBLE = 5
ITERS = 2500
TARGET = 0.6827          # section 6.8's nominal, unchanged
TOL = 0.10               # section 6.8's tolerance, unchanged
BAND_PTS = 100.0 * TOL   # the transfer band, in percentage points
N_BOOT = 20000
QUANTITIES = ("aleatoric", "epistemic")

paths = R.repo_paths()
cfg = R.load_reference_config(paths["lite"])
data, ep = R.load_data(paths["csv"], verbose=False)
split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"),
                     verbose=False)
HOLD = list(split["holdout_episodes"])


def episode_windows(episode):
    """The trajectories of one held-out episode, exactly as task_d3_perhorizon.py cuts
    them: non-overlapping 400-step windows, config-normalised state, raw actions."""
    starts = MET.non_overlapping_starts(ep, [episode], LEN)
    idx = np.asarray(starts)[:, None] + np.arange(LEN)[None, :]
    raw = data[idx]
    st = torch.as_tensor(R.normalise_state(raw[:, :, R.STATE_COLS],
                                           cfg["state_data_mean"], cfg["state_data_std"]),
                         dtype=torch.float32)
    ac = torch.as_tensor(raw[:, :, R.ACTION_COLS], dtype=torch.float32)
    return st, ac, len(starts)


def roll(model, st, ac):
    pred, alea, epi, _, _ = model.rollout_uncertainty(st.clone(), ac, START,
                                                      action_offset=1)
    return {"err": (pred - st).abs().numpy().astype(np.float64),
            "aleatoric": alea.numpy().astype(np.float64),
            "epistemic": epi.numpy().astype(np.float64)}


def released_model():
    sd = torch.load(paths["ckpt"], map_location="cpu")["system_dynamics_state_dict"]
    m = S.ReferenceRWM(sd)
    m.eval()
    return m, sd


def armA_model(seed):
    """An ensemble-5 Arm A checkpoint, loaded and CHECKED against our own trainer's
    forward before any number from it is compared with section 6.8's — the same guard
    scripts/task_d3_ens5.py applies to these weights."""
    w = f"runs/armA_seed{seed}_ens5/weights_{ITERS}.pt"
    sd = torch.load(w, map_location="cpu")["model_state_dict"]
    m = S.ReferenceRWM(sd)
    m.eval()
    return m, sd, w


def cover(err, sig, c, h):
    """Section 6.8's coverage, character for character: every finite, positive-sigma
    cell over (forecast step <= h) x 45 state dimensions, pooled."""
    sl = slice(START, START + h)
    e, g = err[:, sl], sig[:, sl] * c
    m = np.isfinite(g) & (g > 0)
    return float((e[m] <= g[m]).mean()) if m.any() else float("nan")


def fit_scalar(err, sig, h):
    """Section 6.8's fit: bisection in log space on the smallest c reaching nominal."""
    lo, hi = 1e-9, 1e12
    for _ in range(300):
        mid = (lo * hi) ** 0.5
        if cover(err, sig, mid, h) < TARGET:
            lo = mid
        else:
            hi = mid
    return (lo * hi) ** 0.5


def counts(err, sig, c, h):
    """Per-trajectory (covered, valid) cell counts, so a pooled coverage over any set
    of trajectories is sum(covered) / sum(valid) — an exact reduction of cover()."""
    sl = slice(START, START + h)
    e = err[:, sl]
    g = sig[:, sl] * c
    n = e.shape[0]
    m = np.isfinite(g) & (g > 0)
    cov = (m & (e <= g)).reshape(n, -1).sum(1).astype(np.float64)
    val = m.reshape(n, -1).sum(1).astype(np.float64)
    assert (val > 0).all(), f"a trajectory has no valid cell at h={h}"
    return cov, val


def pooled(cov, val, i=None):
    i = slice(None) if i is None else i
    return float(cov[i].sum() / val[i].sum())


def other(e):
    return [x for x in HOLD if x != e][0]


def main():
    print("D3 CROSS-MODEL — does section 6.8's per-horizon table transfer between MODELS?")
    print("=" * 118)
    print(f"  M-69, pre-registered in fad7db7. Held-out episodes {HOLD}, "
          f"target +-1 sigma coverage {100*TARGET:.2f}%, band +-{BAND_PTS:.0f} points.\n")

    d3 = json.load(open(os.path.join(R.RESULTS, "task_d3_perhorizon.json")))
    assert d3["holdout_episodes"] == HOLD, "section 6.8's held-out pair is not this split's"
    assert abs(d3["target_coverage"] - TARGET) < 1e-12, "section 6.8's nominal moved"
    for q in QUANTITIES:
        assert d3["quantities"][q]["verdict"]["tolerance"] == TOL, \
            "section 6.8's tolerance moved"

    power = json.load(open(os.path.join(R.RESULTS, "p4_transfer_power.json")))
    assert power["governing_rule"] == "M-69"

    # ---- roll every model out on every held-out episode, once ----------------
    win = {e: episode_windows(e) for e in HOLD}
    n_traj = {e: win[e][2] for e in HOLD}
    n_ind = int(MET.n_independent(MET.non_overlapping_starts(ep, HOLD, LEN), LEN))
    assert n_ind == 4, f"the held-out arena is n_independent = {n_ind}, not 4; M-69's " \
                       "grid is written against 4"
    assert sum(n_traj.values()) == 4, f"expected 4 trajectories, got {n_traj}"

    RO, meta = {}, {}
    rm, _ = released_model()
    RO["released"] = {e: roll(rm, win[e][0], win[e][1]) for e in HOLD}
    meta["released"] = {"weights": R.rel(paths["ckpt"]), "kind": "released checkpoint"}
    print(f"  released checkpoint: rolled out on episodes {HOLD}")

    own_ref = M.build_from_config(cfg, ensemble_size=ENSEMBLE)
    for s in SEEDS:
        m, sd, w = armA_model(s)
        own_ref.load_state_dict(sd, strict=True)
        own_ref.eval()
        key = f"armA_seed{s}_ens5"
        RO[key] = {}
        worst = 0.0
        for e in HOLD:
            st, ac, _ = win[e]
            p_own, _ = own_ref.rollout_full(st.clone(), ac, START, action_offset=1)
            pred, alea, epi, _, _ = m.rollout_uncertainty(st.clone(), ac, START,
                                                          action_offset=1)
            d = float((p_own - pred).abs().max())
            assert d < 1e-5, f"seed {s}: harness disagrees with the trainer by {d:.3e}"
            worst = max(worst, d)
            RO[key][e] = {"err": (pred - st).abs().numpy().astype(np.float64),
                          "aleatoric": alea.numpy().astype(np.float64),
                          "epistemic": epi.numpy().astype(np.float64)}
        meta[key] = {"weights": w, "kind": f"Arm A, ensemble {ENSEMBLE}, seed {s}, "
                                           f"{ITERS} iterations",
                     "max_diff_vs_trainer": worst}
        print(f"  {key}: rolled out on episodes {HOLD}, "
              f"harness vs trainer max |diff| = {worst:.3e}")
    print()

    out = {
        "governing_rule": "M-69",
        "rule_commit": "fad7db7fa1a43e58631c4d7c9f6f2f707901fab0",
        "power_artifact": "results/p4_transfer_power.json",
        "target_coverage": TARGET,
        "tolerance": TOL,
        "band_pts": BAND_PTS,
        "holdout_episodes": HOLD,
        "horizons": list(HORIZONS),
        "seeds": list(SEEDS),
        "design": {
            "arena": "out-of-sample held-out pair",
            "n_independent": n_ind,
            "n_trajectories": sum(n_traj.values()),
            "trajectories_per_episode": {str(e): n_traj[e] for e in HOLD},
            "traj_len": LEN, "start_step": START, "action_offset": 1,
            "ensemble": ENSEMBLE, "iterations": ITERS,
            "n_boot": N_BOOT, "bootstrap_unit": "whole trajectory",
            "distinct_resamples": n_ind ** n_ind,
            "governing_statistic": (
                "paired Delta = 100 x (coverage under the multiplier fitted on the "
                "OTHER model - coverage under the multiplier fitted on the SAME "
                "model), same trajectories, horizon, quantity and scored model; both "
                "fold directions pooled into one statistic at n_independent = 4, each "
                "trajectory scored under the multiplier fitted on the episode it does "
                "not belong to"),
            "released_multipliers": (
                "read from results/task_d3_perhorizon.json as published; never refitted"),
            "note": ("the absolute (unpaired) column is reported and is UNPOWERED: "
                     "results/p4_transfer_power.json gives tolerance_resolvable false "
                     "at 0 of 12 (quantity, horizon) pairs")},
        "models": meta,
        "multipliers": {},
        "cells": [],
        "absolute_column": {},
        "armA_own_model": {},
        "verdict": {},
    }

    rng = np.random.default_rng(0)
    boot_idx = rng.integers(0, sum(n_traj.values()), (N_BOOT, sum(n_traj.values())))

    def pooled_vectors(model_key, q, h, c_by_fit_ep):
        """Per-trajectory counts over all 4 held-out trajectories, each scored under
        the multiplier fitted on the episode it does NOT belong to."""
        cov, val, owner = [], [], []
        for e in HOLD:
            c = c_by_fit_ep[other(e)]
            cv, vl = counts(RO[model_key][e]["err"], RO[model_key][e][q], c, h)
            cov.append(cv)
            val.append(vl)
            owner += [e] * len(cv)
        return np.concatenate(cov), np.concatenate(val), np.array(owner)

    print(f"  {'quantity':<11}{'h':>5}{'dir':>10}{'seed':>6}{'c same':>12}{'c cross':>12}"
          f"{'ratio':>9}{'cov same':>11}{'cov cross':>11}{'Delta':>9}"
          f"{'95% CI':>20}{'branch':>10}")
    print("  " + "-" * 126)

    published = {}   # (q, h, fit_ep) -> section 6.8's c
    armA_c = {}      # (seed, q, h, fit_ep) -> c fitted on that Arm A model
    abs_hits = {q: [] for q in QUANTITIES}
    own_cells = []

    for q in QUANTITIES:
        fits = d3["quantities"][q]["fits"]
        for h in HORIZONS:
            for f in fits:
                if f["h"] == h:
                    published[(q, h, f["fit_episode"])] = f["c"]
            assert sorted(k[2] for k in published if k[0] == q and k[1] == h) == \
                sorted(HOLD), f"expected one published scalar per fold at h={h}"

            # section 6.8's published held-out coverages must come back out of this
            # harness exactly, or the "same-model" arm of Delta is not 6.8's number.
            for f in (x for x in fits if x["h"] == h):
                te = f["test_episode"]
                got = cover(RO["released"][te]["err"], RO["released"][te][q],
                            f["c"], h)
                assert abs(got - f["coverage_after"]) < 1e-12, (
                    f"released checkpoint under section 6.8's published c "
                    f"({q}, h={h}, fit ep{f['fit_episode']}) gives {got!r}, "
                    f"published {f['coverage_after']!r}")

            for s in SEEDS:
                key = f"armA_seed{s}_ens5"
                for fe in HOLD:
                    armA_c[(s, q, h, fe)] = fit_scalar(RO[key][fe]["err"],
                                                       RO[key][fe][q], h)

                pub = {e: published[(q, h, e)] for e in HOLD}
                arm = {e: armA_c[(s, q, h, e)] for e in HOLD}

                for direction, scored, c_same, c_cross in (
                        ("armA_to_released", "released", pub, arm),
                        ("released_to_armA", key, arm, pub)):
                    cov_s, val_s, owner = pooled_vectors(scored, q, h, c_same)
                    cov_x, val_x, _ = pooled_vectors(scored, q, h, c_cross)
                    assert np.array_equal(val_s, val_x), (
                        "the valid-cell mask moved with the scalar; it must not")

                    cs, cx = pooled(cov_s, val_s), pooled(cov_x, val_x)
                    delta = 100.0 * (cx - cs)

                    bs = cov_s[boot_idx].sum(1) / val_s[boot_idx].sum(1)
                    bx = cov_x[boot_idx].sum(1) / val_x[boot_idx].sum(1)
                    bd = 100.0 * (bx - bs)
                    lo, hi = (float(np.percentile(bd, 2.5)),
                              float(np.percentile(bd, 97.5)))

                    inside = bool(lo >= -BAND_PTS and hi <= BAND_PTS)
                    outside = bool(lo > BAND_PTS or hi < -BAND_PTS)
                    branch = "outside" if outside else ("inside" if inside
                                                        else "straddles")

                    # the absolute column, per fold, under the CROSS-model multiplier
                    for e in HOLD:
                        m_ = owner == e
                        cf = pooled(cov_x, val_x, m_)
                        abs_hits[q].append({
                            "h": h, "seed": s, "direction": direction,
                            "fit_episode": other(e), "test_episode": e,
                            "scored_model": scored,
                            "c": c_cross[other(e)],
                            "coverage": cf,
                            "within_tolerance": bool(abs(cf - TARGET) < TOL)})
                        if direction == "released_to_armA":
                            co = pooled(cov_s, val_s, m_)
                            own_cells.append({
                                "quantity": q, "h": h, "seed": s,
                                "fit_episode": other(e), "test_episode": e,
                                "c": c_same[other(e)], "coverage": co,
                                "within_tolerance": bool(abs(co - TARGET) < TOL)})

                    ratio = float(max(c_same[HOLD[0]], c_cross[HOLD[0]]) /
                                  min(c_same[HOLD[0]], c_cross[HOLD[0]]))
                    out["cells"].append({
                        "quantity": q, "h": h, "seed": s, "direction": direction,
                        "scored_model": scored,
                        "c_same_by_fit_episode": {str(e): c_same[e] for e in HOLD},
                        "c_cross_by_fit_episode": {str(e): c_cross[e] for e in HOLD},
                        "c_ratio_cross_over_same_by_fit_episode": {
                            str(e): float(c_cross[e] / c_same[e]) for e in HOLD},
                        "coverage_same": cs, "coverage_cross": cx,
                        "delta_pts": delta, "ci_lo_pts": lo, "ci_hi_pts": hi,
                        "interval_inside_band": inside,
                        "interval_outside_band": outside,
                        "interval_straddles_edge": bool(not inside and not outside)})

                    print(f"  {q:<11}{h:>5}{('A->rel' if direction.startswith('armA') else 'rel->A'):>10}"
                          f"{s:>6}{c_same[HOLD[0]]:>12.4g}{c_cross[HOLD[0]]:>12.4g}"
                          f"{ratio:>9.3g}{100*cs:>10.2f}%{100*cx:>10.2f}%"
                          f"{delta:>9.2f}{f'[{lo:.2f}, {hi:.2f}]':>20}{branch:>10}")
        print()

    # ---- the absolute column, and Arm A's own-model baseline ------------------
    for q in QUANTITIES:
        rows = abs_hits[q]
        ok = sum(r["within_tolerance"] for r in rows)
        out["absolute_column"][q] = {
            "cells_within_tolerance": int(ok), "n_cells": len(rows),
            "counted_as": "6 horizons x 2 fold directions x 3 seeds x 2 transfer "
                          "directions, per quantity",
            "powered": False,
            "unpowered_note": (
                "UNPOWERED. results/p4_transfer_power.json gives a binding MDE of "
                "12.55-40.62 points on this unpaired quantity against a 10-point "
                "band, and tolerance_resolvable is false at 0 of 12 (quantity, "
                "horizon) pairs. A cell inside the band is not evidence of transfer; "
                "it is evidence this arena cannot resolve the question."),
            "cells": rows}
        for direction in ("armA_to_released", "released_to_armA"):
            sub = [r for r in rows if r["direction"] == direction]
            out["absolute_column"][q][f"cells_within_tolerance_{direction}"] = \
                int(sum(r["within_tolerance"] for r in sub))
            out["absolute_column"][q][f"n_cells_{direction}"] = len(sub)

    for q in QUANTITIES:
        sub = [r for r in own_cells if r["quantity"] == q]
        out["armA_own_model"][q] = {
            "cells_within_tolerance": int(sum(r["within_tolerance"] for r in sub)),
            "n_cells": len(sub),
            "meaning": ("Arm A scored under a multiplier fitted on Arm A's own sigma "
                        "on the other held-out episode — direction 2's same-model "
                        "baseline, so a reader can see whether section 6.8's remedy "
                        "works on a model we trained at all"),
            "cells": sub}

    out["multipliers"] = {
        "released_published": {f"{q}|h{h}|fit_ep{e}": published[(q, h, e)]
                               for q in QUANTITIES for h in HORIZONS for e in HOLD},
        "armA_fitted": {f"seed{s}|{q}|h{h}|fit_ep{e}": armA_c[(s, q, h, e)]
                        for s in SEEDS for q in QUANTITIES
                        for h in HORIZONS for e in HOLD},
        "ratio_armA_over_released": {
            f"seed{s}|{q}|h{h}|fit_ep{e}": float(armA_c[(s, q, h, e)] /
                                                 published[(q, h, e)])
            for s in SEEDS for q in QUANTITIES for h in HORIZONS for e in HOLD}}
    _r = list(out["multipliers"]["ratio_armA_over_released"].values())
    out["multipliers"]["ratio_min"] = float(min(_r))
    out["multipliers"]["ratio_max"] = float(max(_r))

    # ---- M-69's verdict, evaluated by code -----------------------------------
    def verdict_over(cells, label):
        n_out = sum(c["interval_outside_band"] for c in cells)
        n_in = sum(c["interval_inside_band"] for c in cells)
        n_str = sum(c["interval_straddles_edge"] for c in cells)
        if n_out:
            v, br = "DOES NOT TRANSFER — A PROPERTY OF THE MODEL", 1
        elif n_in == len(cells):
            v, br = "TRANSFERS — A PROPERTY OF THE HORIZON", 2
        else:
            v, br = "UNDERPOWERED", 3
        worst = max(cells, key=lambda c: max(abs(c["ci_lo_pts"]), abs(c["ci_hi_pts"])))
        return {"scope": label, "verdict": v, "branch": br, "n_cells": len(cells),
                "n_intervals_outside_band": int(n_out),
                "n_intervals_inside_band": int(n_in),
                "n_intervals_straddling_edge": int(n_str),
                "largest_abs_delta_pts": max(abs(c["delta_pts"]) for c in cells),
                "widest_interval_cell": {k: worst[k] for k in
                                         ("quantity", "h", "seed", "direction",
                                          "delta_pts", "ci_lo_pts", "ci_hi_pts")}}

    out["verdict"]["both_directions"] = verdict_over(out["cells"], "both directions")
    for direction in ("armA_to_released", "released_to_armA"):
        out["verdict"][direction] = verdict_over(
            [c for c in out["cells"] if c["direction"] == direction], direction)
    out["verdict"]["caution"] = (
        "This is 6 horizons x two directions on the SAME 4 trajectories and is not 12 "
        "independent successes; nor are the 72 governing cells 72 independent tests. "
        "No P-value attaches to any count here and none is computed. The three Arm A "
        "seeds share training data and differ only in initialisation and data "
        "ordering, so they are not three independent models. The two models differ on "
        "several axes at once — training data, recipe, iteration count, and a "
        "released-checkpoint provenance S-19 records as not fully reconstructible — so "
        "this bounds transfer between these two models and is not an attribution.")

    v = out["verdict"]["both_directions"]
    print("  M-69 VERDICT")
    print("  " + "-" * 116)
    print(f"    both directions   : {v['verdict']}  (branch {v['branch']})")
    print(f"      of {v['n_cells']} governing cells: {v['n_intervals_inside_band']} "
          f"intervals wholly inside the +-{BAND_PTS:.0f}-point band, "
          f"{v['n_intervals_outside_band']} wholly outside, "
          f"{v['n_intervals_straddling_edge']} straddling an edge")
    for direction in ("armA_to_released", "released_to_armA"):
        d = out["verdict"][direction]
        print(f"    {direction:<18}: {d['verdict']}  (branch {d['branch']}; "
              f"{d['n_intervals_inside_band']} in / {d['n_intervals_outside_band']} out "
              f"/ {d['n_intervals_straddling_edge']} straddling of {d['n_cells']})")
    print(f"    largest |Delta| over all cells: {v['largest_abs_delta_pts']:.2f} points")
    for q in QUANTITIES:
        a = out["absolute_column"][q]
        print(f"    absolute column, {q}: {a['cells_within_tolerance']} / "
              f"{a['n_cells']} cells within {100*TOL:.0f} points of "
              f"{100*TARGET:.2f}% — UNPOWERED (see p4_transfer_power.json)")
        o = out["armA_own_model"][q]
        print(f"    Arm A own-model baseline, {q}: {o['cells_within_tolerance']} / "
              f"{o['n_cells']} cells within tolerance")
    print(f"    Arm A / released multiplier ratio spans "
          f"{out['multipliers']['ratio_min']:.3g}x to "
          f"{out['multipliers']['ratio_max']:.3g}x")
    print(f"\n    caution: {out['verdict']['caution']}")

    op = os.path.join(R.RESULTS, "task_d3_cross_model.json")
    json.dump(out, open(op, "w"), indent=2)
    print(f"\n  wrote {R.rel(op)}")


if __name__ == "__main__":
    main()
