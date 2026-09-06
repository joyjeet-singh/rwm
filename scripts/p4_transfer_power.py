"""
P4 -- what M-69 can and cannot detect, measured BEFORE any cross-model
multiplier is fitted.

M-24 records a pre-registered rule anchored away from the regime the claim was
about. M-43 records a rule committed without anyone first computing what it
could detect at the arena it would face, which R-67 then had to estimate
afterwards. P1 fixed that omission for M-44 and M-45 and P3 fixed it for M-68.
This script is the same fix for M-69 -- the cross-model transfer of section 6.8's
per-horizon multiplier -- and it is run and committed BEFORE any multiplier is
fitted on Arm A, before any multiplier is applied across models, and before
results/task_d3_cross_model.json exists.

WHAT IS BEING ESTIMATED. Not the transfer result: no cross-model multiplier
exists and nothing here forecasts one. What is estimated is the SAMPLING
VARIABILITY of the statistic M-69 governs on -- the +-1 sigma coverage of one
held-out CELL -- at the arena that rule will actually face. Section 6.8 scores
each cell on ONE held-out episode, which is TWO non-overlapping 400-step
trajectories, so the estimation unit is n = 2 and not the arena's 4. That
variability is a property of the arena, the horizon and the statistic rather
than of which model produced the multiplier, so it can be measured now.

WHY IT MATTERS HERE MORE THAN USUAL. Section 12 of the revision brief specifies
a TOLERANCE column -- a cell counts when its held-out coverage lands within 10
points of the 68.27% nominal -- and a tolerance test is only meaningful at
horizons where the tolerance is larger than what the arena can resolve. Where the
MDE below exceeds 10 points, a cell landing inside the band is not evidence that
the multiplier transferred; it is evidence that this arena cannot tell. This
script is what let M-69 be written knowing that: the tolerance column is produced
and reported, and labelled unpowered, while the statistic the rule's verdict
GOVERNS on is the paired change below. That choice was made here, before the
table exists, rather than after it is seen.

THE METHOD IS M-43's, the one P3 used and M-68's text quotes. The all-ten-episode
pool has twenty non-overlapping 400-step trajectories. Draw TWO at a time -- the
size of the set one cell is scored on -- and recompute the coverage on each draw.
C(20, 2) = 190 draws, so the enumeration is EXHAUSTIVE and the subsampling step
carries no Monte-Carlo error of its own. The spread across draws is the sampling
SE at n = 2.

  Finite-population correction. Sampling two of twenty WITHOUT replacement is
  tighter than sampling two from an unbounded population by the factor
  (N - n) / (N - 1) on the variance. The raw across-draw SD is therefore divided
  by sqrt(18/19) so that the SE, and the MDE built on it, describe the arena the
  rule faces rather than the pool it was calibrated on. Both figures are stored.

NO MULTIPLIER IS FITTED HERE, DELIBERATELY. Coverage variance depends on where
coverage sits, so it has to be measured with sigma scaled into the regime the
criterion lives in rather than at c = 1, where coverage is near zero and its
spread is meaninglessly small. The scalars used are the ones section 6.8 ALREADY
PUBLISHED in results/task_d3_perhorizon.json -- read from that artifact, not
refitted -- one per (quantity, horizon, fold direction). Every horizon therefore
carries two subsampling estimates, and the larger binds.

  This script scores the RELEASED CHECKPOINT ONLY. Scoring an Arm A model under
  a released-fitted scalar would be one arena away from the very quantity M-69 is
  about, and a pre-registration whose power artifact lets a reader approximate the
  answer is not a pre-registration. The cost of that choice is stated in the rule.

A SECOND STATISTIC, PAIRED, AND WHY IT IS HERE. The tolerance test above is
UNPAIRED: it asks where one cell's coverage sits, so it carries the full
between-trajectory heterogeneity of the arena. M-69's verdict instead governs on
the PAIRED change -- the same cell's coverage under a multiplier fitted on a
different model minus its coverage under section 6.8's own multiplier, on the
SAME trajectories, the same horizon and the same quantity -- which cancels most
of that heterogeneity. Its SE cannot be estimated from cross-model values without
computing the answer, so it is estimated from a PROXY swap that is available now:
the same two published scalars, fit-on-episode-1 against fit-on-episode-8, applied
to the same trajectories. Both are scalars a different fit produced, so the proxy
measures what the pairing cancels rather than what a model change does. It is a
proxy and the rule says so; it is not a forecast of the transfer difference.

CROSS-CHECK. The cluster bootstrap over whole trajectories (M-27) on the four
real held-out trajectories, drawing two at a time with replacement, which is the
scoring set size a cell faces. It answers a slightly different question -- the
bootstrap's own SE on the trajectories in hand -- and it is computed for both
scalars at every horizon.

THE BINDING MDE at each (quantity, horizon) is the LARGEST of the four estimates:
two published scalars x (subsampling, bootstrap cross-check). Taking the maximum
rather than arguing for one of them makes the rule strictly harder to satisfy,
which is the direction a pre-registration should err in. Which estimate bound
each figure is recorded, so a reader can check the choice rather than take it.

CAVEAT carried into the rule. The twenty-trajectory pool is IN-SAMPLE for our own
arms, which trained on eight of the ten episodes, and section 6.8 states the same
caveat where it reports the M-43 subsampling estimate. In-sample trajectories are
easier and more alike, so the across-draw spread they give is, if anything, an
UNDERSTATEMENT of the spread the held-out arena produces -- which makes the MDE
built on it an optimistic floor rather than a ceiling. The held-out cross-check is
recorded for exactly that reason and enters the maximum.

Trains nothing, fits nothing, reads no artifact that does not already exist, and
writes results/p4_transfer_power.json.
"""
import itertools
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
import torch  # noqa: E402
import rwm_data as R  # noqa: E402
import rollout_eval as E  # noqa: E402
import rwm_metrics as MET  # noqa: E402
import score_reference as S  # noqa: E402

HORIZONS = (1, 8, 32, 100, 128, 368)
START, LEN = E.START_STEP, 400
N_SUB = 2                  # trajectories one section 6.8 cell is scored on
N_BOOT = 20000             # cross-check only; matches the scoring harness
TARGET = 0.6827            # section 6.8's nominal, unchanged
TOL_PTS = 10.0             # section 6.8's tolerance, unchanged

Z95, Z80 = 1.959963985, 0.8416212336


def mde(se):
    """Two-sided alpha = .05, power = .80, from an SE. Same formula as P1 and P3."""
    return float((Z95 + Z80) * se)


def load_pool(episodes, label):
    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    data, ep = R.load_data(paths["csv"], verbose=False)
    starts = MET.non_overlapping_starts(ep, episodes, LEN)
    n_ind = int(MET.n_independent(starts, LEN))
    idx = np.asarray(starts)[:, None] + np.arange(LEN)[None, :]
    raw = data[idx]
    st = torch.as_tensor(R.normalise_state(raw[:, :, R.STATE_COLS],
                                           cfg["state_data_mean"], cfg["state_data_std"]),
                         dtype=torch.float32)
    ac = torch.as_tensor(raw[:, :, R.ACTION_COLS], dtype=torch.float32)
    print(f"  pool {label}: episodes {list(episodes)}, {len(starts)} trajectories, "
          f"n_independent = {n_ind}")
    return {"st": st, "ac": ac, "n_ind": n_ind, "n_traj": len(starts),
            "episodes": list(episodes)}


def score_released(pool):
    """The released checkpoint, scored exactly as scripts/task_d3_perhorizon.py
    scores it: same entry point, same action offset, same start step."""
    paths = R.repo_paths()
    sd = torch.load(paths["ckpt"], map_location="cpu")["system_dynamics_state_dict"]
    m = S.ReferenceRWM(sd)
    m.eval()
    pred, alea, epi, _as, _es = m.rollout_uncertainty(
        pool["st"].clone(), pool["ac"], START, action_offset=1)
    return {"abs_err": (pred - pool["st"]).abs().numpy().astype(np.float64),
            "aleatoric": alea.numpy().astype(np.float64),
            "epistemic": epi.numpy().astype(np.float64)}


def per_trajectory_counts(sc, quantity, c, h):
    """
    Per-trajectory (covered, valid) cell counts at horizon h under scalar c.

    task_d3_perhorizon.cover() pools every finite, positive-sigma cell and takes
    the mean, so a subsample's coverage is sum(covered) / sum(valid) over the
    trajectories drawn. Keeping the two counts per trajectory makes every draw an
    exact reduction of these two vectors, which is what lets the 190-way
    enumeration cost nothing.
    """
    sl = slice(START, START + h)
    e = sc["abs_err"][:, sl]
    g = sc[quantity][:, sl] * c
    n = e.shape[0]
    m = np.isfinite(g) & (g > 0)
    cov = (m & (e <= g)).reshape(n, -1).sum(1).astype(np.float64)
    val = m.reshape(n, -1).sum(1).astype(np.float64)
    assert (val > 0).all(), f"a trajectory has no valid cell at h={h} ({quantity})"
    return cov, val


def coverage(cov, val, i):
    i = list(i)
    return float(cov[i].sum() / val[i].sum())


def subsample_se(cov, val, n_pool):
    """M-43's method: every C(n_pool, 2) draw, exhaustively."""
    draws = list(itertools.combinations(range(n_pool), N_SUB))
    cv = np.array([coverage(cov, val, d) for d in draws]) * 100.0
    fpc = (n_pool - N_SUB) / (n_pool - 1)
    raw = float(cv.std(ddof=1))
    return {"n_draws": len(draws), "fpc_variance_factor": float(fpc),
            "coverage_se_pts_raw": raw,
            "coverage_se_pts": raw / float(np.sqrt(fpc)),
            "coverage_mean_pts": float(cv.mean())}


def paired_diff_pts(a, b, i):
    """Coverage under scalar a minus coverage under scalar b, on the SAME draw."""
    return 100.0 * (coverage(a[0], a[1], i) - coverage(b[0], b[1], i))


def paired_subsample_se(a, b, n_pool):
    draws = list(itertools.combinations(range(n_pool), N_SUB))
    d = np.array([paired_diff_pts(a, b, list(x)) for x in draws])
    fpc = (n_pool - N_SUB) / (n_pool - 1)
    raw = float(d.std(ddof=1))
    return {"n_draws": len(draws), "fpc_variance_factor": float(fpc),
            "diff_se_pts_raw": raw, "diff_se_pts": raw / float(np.sqrt(fpc)),
            "diff_mean_pts": float(d.mean())}


def paired_bootstrap_se(a, b, n, rng):
    d = np.array([paired_diff_pts(a, b, rng.integers(0, n, N_SUB))
                  for _ in range(N_BOOT)])
    return {"diff_se_pts": float(d.std(ddof=1)), "n_valid": int(d.size)}


def bootstrap_se(cov, val, n, rng):
    """The cross-check: cluster bootstrap over whole trajectories (M-27), drawing
    N_SUB of the n held-out trajectories with replacement."""
    cv = []
    for _ in range(N_BOOT):
        i = rng.integers(0, n, N_SUB)
        v = coverage(cov, val, i)
        if np.isfinite(v):
            cv.append(v)
    cv = np.array(cv) * 100.0
    return {"coverage_se_pts": float(cv.std(ddof=1)), "n_valid": int(cv.size),
            "distinct_resamples": int(n ** N_SUB)}


def main():
    print("P4 — POWER CHECK FOR M-69, run before any cross-model multiplier is fitted")
    print("=" * 104)

    split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"),
                         verbose=False)
    hold = list(split["holdout_episodes"])
    allep = sorted(set(split["train_episodes"]) | set(split["holdout_episodes"]))

    d3 = json.load(open(os.path.join(R.RESULTS, "task_d3_perhorizon.json")))
    assert d3["holdout_episodes"] == hold, "section 6.8's held-out pair is not this split's"
    assert abs(d3["target_coverage"] - TARGET) < 1e-12, "section 6.8's nominal moved"
    assert d3["quantities"]["epistemic"]["verdict"]["tolerance"] == TOL_PTS / 100.0, (
        "section 6.8's tolerance moved")

    pool20 = load_pool(allep, "all-ten (M-43's subsampling pool)")
    pool4 = load_pool(hold, "held-out pair (M-69's arena)")
    assert pool4["n_ind"] == 4, (
        f"the held-out arena is n_independent = {pool4['n_ind']}, not 4; M-69's grid "
        "is written against 4 and must not be changed silently")
    assert pool20["n_traj"] == 20, f"the pool is {pool20['n_traj']} trajectories, not 20"

    sc20 = score_released(pool20)
    sc4 = score_released(pool4)
    print("  scored the released checkpoint on both pools "
          "(ensemble of 5, action offset 1, start step 32)\n")

    out = {
        "purpose": "estimate what M-69 can detect at the arena and horizons it will "
                   "face, BEFORE any cross-model multiplier is fitted",
        "governing_rule": "M-69",
        "committed_before": "any fit of a per-horizon multiplier on Arm A, any "
                            "cross-model application, and results/task_d3_cross_model.json",
        "arena": "out-of-sample held-out pair",
        "n_independent_arena": pool4["n_ind"],
        "n_independent_per_cell": N_SUB,
        "holdout_episodes": hold,
        "horizons": list(HORIZONS),
        "target_coverage_pts": 100 * TARGET,
        "tolerance_pts": TOL_PTS,
        "statistic": "+-1 sigma coverage of one held-out cell, pooled over "
                     "(forecast step <= h) x 45 state dimensions x the trajectories "
                     "of one held-out episode, exactly as task_d3_perhorizon.cover() "
                     "computes it",
        "scalars_used": "the multipliers section 6.8 already published in "
                        "results/task_d3_perhorizon.json; NOTHING is refitted here",
        "model_scored": "released checkpoint only — see the module docstring",
        "method": {
            "primary": "M-43 subsampling — every C(20, 2) = 190 draw of two "
                       "trajectories from the all-ten pool, exhaustively enumerated; "
                       "the across-draw SD is the sampling SE at n = 2",
            "finite_population_correction": "the raw SD is divided by "
                                            "sqrt((20 - 2) / (20 - 1)) so it describes "
                                            "a scoring set of two rather than a pool of "
                                            "twenty",
            "mde": "(z_.975 + z_.80) x SE; two-sided alpha = .05, power = .80",
            "bootstrap_unit": "whole trajectory (M-27); never trajectory x step",
            "cross_check": f"cluster bootstrap, {N_BOOT} resamples of two of the four "
                           f"held-out trajectories",
            "binding": "at each (quantity, horizon) the LARGEST of the four estimates — "
                       "two published scalars x (subsampling, bootstrap cross-check)",
        },
        "per_quantity": {},
        "binding_mde_pts": {},
        "paired_binding_mde_pts": {},
        "tolerance_resolvable": {},
        "caveats": [],
    }

    rng = np.random.default_rng(0)
    print(f"  MDE on +-1 sigma coverage at n = {N_SUB} trajectories, by horizon "
          f"(percentage points)")
    print(f"    {'quantity':<12}{'h':>6}{'sub fit-ep1':>13}{'sub fit-ep8':>13}"
          f"{'boot fit-ep1':>14}{'boot fit-ep8':>14}{'BINDING':>10}"
          f"{'bound by':>16}{'< 10 pts?':>11}{'PAIRED MDE':>13}")
    print("    " + "-" * 122)

    for qname in ("aleatoric", "epistemic"):
        fits = d3["quantities"][qname]["fits"]
        qrec, qmde, qres, qpair = {}, {}, {}, {}
        for h in HORIZONS:
            cs = {f["fit_episode"]: f["c"] for f in fits if f["h"] == h}
            assert sorted(cs) == sorted(hold), (
                f"expected one published scalar per fold direction at h={h}, got {cs}")
            rec, cands, keep = {}, [], {}
            for fit_ep in hold:
                c = cs[fit_ep]
                cov20, val20 = per_trajectory_counts(sc20, qname, c, h)
                cov4, val4 = per_trajectory_counts(sc4, qname, c, h)
                keep[fit_ep] = ((cov20, val20), (cov4, val4))
                sub = subsample_se(cov20, val20, pool20["n_traj"])
                boo = bootstrap_se(cov4, val4, pool4["n_traj"], rng)
                rec[f"fit_ep{fit_ep}"] = {
                    "scalar_c": c, "subsampling": sub, "bootstrap": boo,
                    "mde_pts_subsampling": mde(sub["coverage_se_pts"]),
                    "mde_pts_bootstrap": mde(boo["coverage_se_pts"])}
                cands.append((mde(sub["coverage_se_pts"]), f"subsampling/fit_ep{fit_ep}"))
                cands.append((mde(boo["coverage_se_pts"]), f"bootstrap/fit_ep{fit_ep}"))
            e_a, e_b = hold
            psub = paired_subsample_se(keep[e_a][0], keep[e_b][0], pool20["n_traj"])
            pboo = paired_bootstrap_se(keep[e_a][1], keep[e_b][1], pool4["n_traj"], rng)
            rec["paired_proxy"] = {
                "pairing": f"scalar fitted on episode {e_a} against scalar fitted on "
                           f"episode {e_b}, same trajectories, same horizon",
                "subsampling": psub, "bootstrap": pboo,
                "proxy_scalar_ratio": float(max(cs[e_a], cs[e_b]) / min(cs[e_a], cs[e_b])),
                "mde_pts_subsampling": mde(psub["diff_se_pts"]),
                "mde_pts_bootstrap": mde(pboo["diff_se_pts"])}
            rec["paired_binding_mde_pts"] = max(rec["paired_proxy"]["mde_pts_subsampling"],
                                                rec["paired_proxy"]["mde_pts_bootstrap"])
            best = max(cands)
            rec["binding_mde_pts"] = best[0]
            rec["bound_by"] = best[1]
            rec["tolerance_resolvable"] = bool(best[0] < TOL_PTS)
            qrec[str(h)] = rec
            qmde[str(h)] = best[0]
            qres[str(h)] = rec["tolerance_resolvable"]
            qpair[str(h)] = rec["paired_binding_mde_pts"]
            print(f"    {qname:<12}{h:>6}"
                  f"{rec[f'fit_ep{e_a}']['mde_pts_subsampling']:>13.2f}"
                  f"{rec[f'fit_ep{e_b}']['mde_pts_subsampling']:>13.2f}"
                  f"{rec[f'fit_ep{e_a}']['mde_pts_bootstrap']:>14.2f}"
                  f"{rec[f'fit_ep{e_b}']['mde_pts_bootstrap']:>14.2f}"
                  f"{best[0]:>10.2f}{best[1]:>16}"
                  f"{('yes' if rec['tolerance_resolvable'] else 'NO'):>11}"
                  f"{rec['paired_binding_mde_pts']:>13.2f}")
        out["per_quantity"][qname] = qrec
        out["binding_mde_pts"][qname] = qmde
        out["tolerance_resolvable"][qname] = qres
        out["paired_binding_mde_pts"][qname] = qpair
        print()

    worst = max(max(v.values()) for v in out["binding_mde_pts"].values())
    n_res = sum(int(b) for v in out["tolerance_resolvable"].values() for b in v.values())
    n_cells = sum(len(v) for v in out["tolerance_resolvable"].values())
    out["summary"] = {
        "largest_binding_mde_pts": worst,
        "quantity_horizon_pairs_where_tolerance_resolvable": n_res,
        "quantity_horizon_pairs": n_cells,
        "largest_paired_binding_mde_pts":
            max(max(v.values()) for v in out["paired_binding_mde_pts"].values()),
        "largest_proxy_scalar_ratio":
            max(r["paired_proxy"]["proxy_scalar_ratio"]
                for q in out["per_quantity"].values() for r in q.values())}
    out["caveats"] = [
        "This is NOT a prediction of the transfer result. No cross-model multiplier "
        "exists and nothing here forecasts one; what is estimated is the sampling "
        "variability of a coverage figure, which is a property of the arena, the "
        "horizon and the statistic.",
        "The twenty-trajectory pool is IN-SAMPLE for our own arms, which trained on "
        "eight of the ten episodes, so its spread understates the held-out spread and "
        "the subsampling figures are an optimistic floor. The held-out cluster "
        "bootstrap is computed beside every figure and enters the maximum.",
        "Only the released checkpoint is scored. An Arm A model under a "
        "released-fitted scalar is one arena away from the quantity M-69 governs, and "
        "computing it here would let a reader approximate the answer from the "
        "pre-registration's own power artifact.",
        "The MDE is built from an SE and a normal approximation. At n = 2 the "
        "sampling distribution of a coverage figure is not normal, so the MDE is "
        "indicative rather than exact — it is a scale for reading a result, not a test.",
        "The paired proxy swaps two scalars that section 6.8 fitted on different "
        "episodes of the SAME model, and those two differ by at most "
        "the ratio recorded per horizon. A scalar fitted on a different model may "
        "differ by more, and a larger scalar change moves coverage further, so the "
        "paired MDE is a floor on what the paired statistic can resolve rather than "
        "a measurement of the transfer comparison itself.",
        "A coverage SE depends on where coverage sits. The scalars used put it near "
        "the nominal, which is the regime M-69's tolerance test lives in; a cell whose "
        "cross-model coverage lands far from the nominal carries a different SE than "
        "the figure tabulated here.",
    ]

    print(f"  largest binding MDE over all {n_cells} (quantity, horizon) pairs: "
          f"{worst:.2f} points against a {TOL_PTS:.0f}-point tolerance")
    print(f"  tolerance resolvable at {n_res} of {n_cells} pairs")

    op = os.path.join(R.RESULTS, "p4_transfer_power.json")
    json.dump(out, open(op, "w"), indent=2)
    print(f"\n  wrote {R.rel(op)}")


if __name__ == "__main__":
    main()
