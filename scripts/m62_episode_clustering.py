"""2.1 -- M-62: does any headline verdict change when the bootstrap resamples EPISODES
rather than 400-step trajectories?

M-62 was committed before any episode-clustered figure existed. It names five cells, and
it names in advance which of them this rule can and cannot speak to. That advance
statement is honoured here literally: the cells it declared uninformative are reported as
uninformative and their full three-value bootstrap distribution is printed, rather than a
percentile interval that would imply more than n=2 can carry.

THE DESIGN IS FIXED BY THE DATA. Each of the ten episodes contributes exactly two
non-overlapping 400-step trajectories, so the episode level halves n exactly:
out-of-sample 4 -> 2, in-sample 16 -> 8, all ten 20 -> 10.

WHY n=2 IS UNINFORMATIVE BY CONSTRUCTION, not by bad luck. Resampling 2 units with
replacement draws from 4 equally likely ordered samples that collapse to 3 distinct
multisets -- {AA, AB, BB} at probabilities 1/4, 1/2, 1/4. The entire sampling
distribution takes at most three values, so any percentile interval is a choice among
three numbers. M-62 said so before the run and this script prints the three values.
"""
import itertools
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import torch  # noqa: E402
import rwm_data as R  # noqa: E402
import rollout_eval as E  # noqa: E402
import rwm_metrics as MET  # noqa: E402
import per_triple_cache as PTC  # noqa: E402

N_BOOT = 20000
HS = (1, 8, 32, 100, 128, 368)


def episode_map(episodes, traj_len=400):
    """Trajectory -> episode, recomputed from the same function the rollouts used."""
    data, ep = R.load_data(R.repo_paths()["csv"], verbose=False)
    starts = MET.non_overlapping_starts(ep, episodes, traj_len)
    return np.array([int(ep[s]) for s in starts]), np.array(starts)


def boot_traj(stat, n_traj, rng, n_boot=N_BOOT):
    """Resample whole trajectories -- M-27's unit, the level every published interval uses."""
    vals = []
    for _ in range(n_boot):
        v = stat(rng.integers(0, n_traj, n_traj))
        if v is not None and np.isfinite(v):
            vals.append(v)
    return np.array(vals)


def boot_episode(stat, traj_ep, rng, n_boot=N_BOOT):
    """Resample whole EPISODES, taking every trajectory of each drawn episode.

    An episode drawn twice contributes its trajectories twice, which is what a cluster
    bootstrap at that level means.
    """
    eps = np.unique(traj_ep)
    idx_by_ep = {e: np.flatnonzero(traj_ep == e) for e in eps}
    vals = []
    for _ in range(n_boot):
        drawn = rng.integers(0, len(eps), len(eps))
        idx = np.concatenate([idx_by_ep[eps[d]] for d in drawn])
        v = stat(idx)
        if v is not None and np.isfinite(v):
            vals.append(v)
    return np.array(vals)


def enumerate_episode_draws(stat, traj_ep):
    """Every distinct multiset of episodes, with its probability. For n=2 this is the
    whole sampling distribution in three values, which is the point."""
    eps = list(np.unique(traj_ep))
    idx_by_ep = {e: np.flatnonzero(traj_ep == e) for e in eps}
    n = len(eps)
    counts = {}
    for draw in itertools.product(range(n), repeat=n):
        key = tuple(sorted(draw))
        counts[key] = counts.get(key, 0) + 1
    total = n ** n
    rows = []
    for key, c in sorted(counts.items()):
        idx = np.concatenate([idx_by_ep[eps[d]] for d in key])
        v = stat(idx)
        rows.append({"episodes_drawn": [int(eps[d]) for d in key],
                     "probability": c / total,
                     "value": None if v is None or not np.isfinite(v) else float(v)})
    return rows


def ci(vals):
    if len(vals) < 2:
        return [None, None]
    return [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))]


def moved(a, b):
    """M-62's committed definition: an interval that excluded zero now spans it, or the
    reverse. Both bounds must exist for the question to be askable."""
    if None in a or None in b:
        return None
    return (a[0] > 0 or a[1] < 0) != (b[0] > 0 or b[1] < 0)


def pooled_corr(x, y):
    a, b = np.asarray(x).ravel(), np.asarray(y).ravel()
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 3 or a[m].std() == 0 or b[m].std() == 0:
        return None
    return float(np.corrcoef(a[m], b[m])[0, 1])


def main():
    rng = lambda: np.random.default_rng(0)                      # noqa: E731
    out = {"rule": "M-62", "committed": "before any episode-clustered figure existed",
           "verdict_moves_definition": ("an interval that excluded zero now spans it, or "
                                        "the reverse, or a pre-registered condition that "
                                        "held now fails"),
           "design": {}, "cells": {}}

    # ---------------- the design, from the data --------------------------------
    split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"),
                         verbose=False)
    oos = list(split["holdout_episodes"])
    ins = list(split["train_episodes"])
    allep = sorted(set(oos) | set(ins))
    for name, eps in (("out-of-sample", oos), ("in-sample", ins), ("all ten", allep)):
        tep, _ = episode_map(eps)
        out["design"][name] = {"episodes": [int(e) for e in eps],
                               "n_episodes": len(eps),
                               "n_trajectories": int(len(tep)),
                               "n_trajectory_level": int(len(tep)),
                               "n_episode_level": len(eps),
                               "trajectories_per_episode": int(len(tep) / len(eps))}

    print("=" * 100)
    print("M-62 — EPISODE-LEVEL CLUSTERING")
    print("=" * 100)
    for k, v in out["design"].items():
        print(f"  {k:<15} episodes {v['n_episodes']:>2}   trajectories {v['n_trajectories']:>2}"
              f"   n: trajectory {v['n_trajectory_level']:>2} -> episode {v['n_episode_level']:>2}")

    # ================= CELL 3 — section 6.7, all ten episodes ==================
    # The one cell with power: n = 20 -> 10. Also the cell whose own evidence
    # (r_between = +0.878, 51.7% of the pooled covariance) motivated the rule.
    a, meta = PTC.read("released_ckpt_ens5", "all ten episodes", 400)
    tep_all = np.asarray(a["traj_to_episode"])
    abs_err = np.abs(a["err"])
    # The scalar penalty as applied: means.std(0).sum(-1), summed in torch as the model
    # defines it (src/score_reference.py:119) -- the gate's own reduction-order trace.
    epi_scalar = torch.as_tensor(a["sig_epistemic"], dtype=torch.float32).sum(-1).numpy().astype(np.float64)
    err_scalar = abs_err.sum(-1)

    def r_pooled(idx):
        return pooled_corr(epi_scalar[idx], err_scalar[idx])

    def r_dd(idx):
        """Double-demeaned: remove the trajectory mean AND the step mean from both."""
        x, y = epi_scalar[idx], err_scalar[idx]
        x = x - x.mean(1, keepdims=True) - x.mean(0, keepdims=True) + x.mean()
        y = y - y.mean(1, keepdims=True) - y.mean(0, keepdims=True) + y.mean()
        return pooled_corr(x, y)

    cell3 = {}
    for stat_name, fn in (("pooled_r", r_pooled), ("r_dd", r_dd)):
        pt = fn(np.arange(len(tep_all)))
        bt = boot_traj(fn, len(tep_all), rng())
        be = boot_episode(fn, tep_all, rng())
        cit, cie = ci(bt), ci(be)
        wt, we = cit[1] - cit[0], cie[1] - cie[0]
        cell3[stat_name] = {
            "point_estimate": pt,
            "trajectory_level": {"ci": cit, "n": int(len(tep_all)), "n_boot_finite": len(bt),
                                 "excludes_zero": bool(cit[0] > 0 or cit[1] < 0)},
            "episode_level": {"ci": cie, "n": int(len(np.unique(tep_all))),
                              "n_boot_finite": len(be),
                              "excludes_zero": bool(cie[0] > 0 or cie[1] < 0)},
            "width_ratio_episode_over_trajectory": we / wt if wt else None,
            "verdict_moved": moved(cit, cie),
            "informative": True,
        }
    out["cells"]["3_section_6_7_pooled_and_rdd"] = {
        "arena": "all ten episodes", "artifact": "results/task_d_nind20.json + "
        "results/a2_trajectory_level_control.json",
        "informative_at_episode_level": True,
        "why": "n = 20 -> 10; the only named cell with real power at this level",
        "statistics": cell3}

    print("\n  CELL 3 — §6.7, all ten episodes (the cell with power)")
    for k, v in cell3.items():
        t, e = v["trajectory_level"], v["episode_level"]
        print(f"    {k:<10} point {v['point_estimate']:+.4f}")
        print(f"      trajectory n={t['n']:<3} [{t['ci'][0]:+.4f}, {t['ci'][1]:+.4f}]  "
              f"excludes 0: {t['excludes_zero']}")
        print(f"      episode    n={e['n']:<3} [{e['ci'][0]:+.4f}, {e['ci'][1]:+.4f}]  "
              f"excludes 0: {e['excludes_zero']}   "
              f"width x{v['width_ratio_episode_over_trajectory']:.2f}")
        print(f"      VERDICT MOVED: {v['verdict_moved']}")

    # ============ CELLS 1, 2, 4 — out-of-sample, n = 2 at episode level ========
    # M-62 declared these NOT INFORMATIVE AT THIS CLUSTER LEVEL in advance, and
    # required the three-value distribution printed rather than an interval.
    tep_oos, _ = episode_map(oos)

    # --- cell 1: section 5's A/B gap, per-trajectory values already published -------
    a1 = json.load(open(os.path.join(R.RESULTS, "a1_ab_by_horizon.json")))
    cell1 = {}
    for h in HS:
        g = np.asarray(a1["by_horizon"][str(h)]["gap_per_trajectory"], dtype=np.float64)
        stat = lambda idx, g=g: float(g[idx].mean())                       # noqa: E731
        bt = boot_traj(stat, len(g), rng())
        cit = ci(bt)
        cell1[str(h)] = {
            "point_estimate": float(g.mean()),
            "trajectory_level": {"ci": cit, "n": int(len(g)),
                                 "excludes_zero": bool(cit[0] > 0 or cit[1] < 0),
                                 "published_ci": a1["by_horizon"][str(h)]["gap_ci"]},
            "episode_level": {"n": 2, "interval_reported": False,
                              "reason": "n=2: the sampling distribution has three values",
                              "full_distribution": enumerate_episode_draws(stat, tep_oos)},
        }
    out["cells"]["1_section_5_ab_gap"] = {
        "arena": "out-of-sample held-out pair",
        "artifact": "results/a1_ab_by_horizon.json",
        "informative_at_episode_level": False,
        "why": "n = 2 episodes; three distinct multisets; uninformative by construction",
        "by_horizon": cell1}

    # --- cell 2: section 6.2's four-model calibration table, from the cache --------
    ARMS = [("faithful (mse)", "armA_faithful_mse", (0, 1, 2)),
            ("corrected (nll)", "armA_corrected_nll", (0, 1, 2)),
            ("teacher-forced armB", "armB_teacher_forced", (0, 1, 2)),
            ("released ckpt", "released_ckpt_ens5", (None,))]
    cell2 = {}
    for label, slug, seeds in ARMS:
        es, gs = [], []
        for sd in seeds:
            mid = slug if sd is None else f"{slug}_seed{sd}"
            arr, _ = PTC.read(mid, "out-of-sample held-out pair", 400)
            es.append(np.abs(arr["err"])); gs.append(arr["sig_aleatoric"])
        # (seeds, n_traj) partial means -- seeds pooled inside each draw, never resampled
        pe = np.stack([e.mean(axis=(1, 2)) for e in es], 0)
        pg = np.stack([g.mean(axis=(1, 2)) for g in gs], 0)

        def stat(idx, pe=pe, pg=pg):
            return float(pe.mean(0)[idx].mean() / pg.mean(0)[idx].mean())

        bt = boot_traj(stat, pe.shape[1], rng())
        cit = ci(bt)
        cell2[label] = {
            "statistic": "ratio_err_over_sigma (aleatoric)",
            "point_estimate": stat(np.arange(pe.shape[1])),
            "trajectory_level": {"ci": cit, "n": int(pe.shape[1])},
            "episode_level": {"n": 2, "interval_reported": False,
                              "reason": "n=2: the sampling distribution has three values",
                              "full_distribution": enumerate_episode_draws(stat, tep_oos)},
        }
    out["cells"]["2_section_6_2_calibration"] = {
        "arena": "out-of-sample held-out pair",
        "artifact": "results/task1_calibration.json",
        "informative_at_episode_level": False,
        "why": "n = 2 episodes; three distinct multisets; uninformative by construction",
        "by_model": cell2}

    # --- cell 4: section 6.10's paired contrast, per-trajectory already published ---
    r2 = json.load(open(os.path.join(R.RESULTS, "r2_independent_ensemble.json")))
    cell4 = {"artifact": "results/r2_independent_ensemble.json",
             "informative_at_episode_level": False,
             "why": "n = 2 episodes; three distinct multisets; uninformative by construction",
             "note": ("M-44 is DISCHARGED over this cell at the trajectory level and its "
                      "verdict stands as returned. Nothing here re-opens it.")}
    _pt = None
    for k in ("per_trajectory", "per_traj"):
        _pt = next((v for kk, v in _flatten(r2) if kk.endswith(k)), None)
        if _pt is not None:
            break
    if _pt is not None and isinstance(_pt, list) and len(_pt) == len(tep_oos):
        arr = np.asarray(_pt, dtype=np.float64)
        stat = lambda idx: float(arr[idx].mean())                          # noqa: E731
        bt = boot_traj(stat, len(arr), rng())
        cell4["point_estimate"] = float(arr.mean())
        cell4["trajectory_level"] = {"ci": ci(bt), "n": int(len(arr))}
        cell4["episode_level"] = {"n": 2, "interval_reported": False,
                                  "full_distribution": enumerate_episode_draws(stat, tep_oos)}
    else:
        cell4["episode_level"] = {"n": 2, "interval_reported": False,
                                  "reason": ("the published per-trajectory vector is not a "
                                             "flat 4-vector of one statistic; the cell is "
                                             "uninformative at n=2 either way, so it is "
                                             "reported as such rather than reshaped")}
    out["cells"]["4_section_6_10_paired_contrast"] = cell4

    # ================= CELL 5 — section 6.8, not bootstrappable ================
    out["cells"]["5_section_6_8_per_horizon_multiplier"] = {
        "arena": "out-of-sample held-out pair",
        "artifact": "results/task_d3_perhorizon.json",
        "informative_at_episode_level": False,
        "not_bootstrappable": True,
        "why": ("§6.8's folds are ALREADY episode-level by construction: each multiplier is "
                "fitted on one held-out episode and scored on the other. What episode "
                "clustering would change is not the fold but an interval on the 12 held-out "
                "cells, and at the episode level each direction has n = 1, so no interval is "
                "computable at all. Declared in M-62 before the run; no degenerate interval "
                "is printed."),
        "n_episode_level_per_direction": 1}

    print("\n  CELLS 1, 2, 4 — out-of-sample, n=2 at episode level: NOT INFORMATIVE")
    print("    (three-value distributions printed in the artifact, per M-62)")
    print("  CELL 5 — §6.8: NOT BOOTSTRAPPABLE at episode level, n=1 per direction")

    # ================= verdict =================================================
    informative = [("3/" + k, v) for k, v in cell3.items()]
    any_moved = any(v["verdict_moved"] for _, v in informative
                    if v["verdict_moved"] is not None)
    out["verdict"] = {
        "informative_cells": [n for n, _ in informative],
        "n_informative": len(informative),
        "n_uninformative_by_construction": 4,
        "any_verdict_moved": bool(any_moved),
        "result": "MOVES" if any_moved else "NO MOVE",
        "reading": ("NO MOVE: no verdict changes in any cell this rule can speak to. One "
                    "sentence records the check and names the arenas in which it was "
                    "informative." if not any_moved else
                    "MOVES: both units are reported side by side and the affected claim is "
                    "narrowed in the body, never reverted to the trajectory-level figure."),
        "scope": ("Four of the five named cells are out-of-sample, where an episode "
                  "bootstrap has n=2 and is uninformative by construction. This was stated "
                  "in M-62 before the run, not discovered here."),
    }
    print(f"\n  VERDICT: {out['verdict']['result']}  "
          f"({out['verdict']['n_informative']} informative statistics, "
          f"{out['verdict']['n_uninformative_by_construction']} cells uninformative by construction)")

    op = os.path.join(R.RESULTS, "m62_episode_clustering.json")
    json.dump(out, open(op, "w"), indent=2)
    print(f"  wrote {R.rel(op)}")


def _flatten(o, p=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from _flatten(v, p + "/" + str(k))
    elif isinstance(o, list):
        yield p, o
    else:
        yield p, o


if __name__ == "__main__":
    main()
