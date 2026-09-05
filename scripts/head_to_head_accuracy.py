"""The released checkpoint and the from-scratch arms, side by side on absolute accuracy.

WHY. Every comparison this paper makes against the released checkpoint is a comparison of
CALIBRATION (§6.2) or a comparison of one training rule against another (§5). Neither says
how good the reimplementation is as a forecaster next to the artifact it reimplements. A
reader cannot get that from the two tables we do print, because they never share a row set.

WHAT IS AND IS NOT COMPUTED HERE. Nothing is rolled out. Every model row is read from the
per-triple cache (`src/per_triple_cache.py`), which stores the SIGNED residual of a rollout
that has already happened and whose arrays `scripts/gate_per_triple.py` verifies bitwise
against their producer. The prediction is never reconstructed and no checkpoint is loaded.
The hold-last floor is not a model at all: it is the true state at the last teacher-forced
step, so it is computed from the data and needs no rollout.

ONE ARENA FOR THE WHOLE TABLE. The cache holds all four model rows on the out-of-sample
held-out pair at a 400-step unit, and that is the only arena on which all of them exist, so
it is the one arena the table is stated over. It is out-of-sample for our arms and, as
`results/insample_framing.json` records from the released checkpoint's own training set,
IN-SAMPLE for the released checkpoint, which trained on all ten episodes. The direction of
that bias is stated in the paper beside the table; it is not corrected for here, because
correcting it would require an arena the released checkpoint does not have in this dataset.

THE INPUT SET IS FROZEN AND RECORDED, not discovered (Appendix B, `M-66`). The file list is
the literal tuple below, and every file it names is recorded in the artifact with its
sha256, so a cache rebuilt from different weights cannot be mistaken for this one.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402

import per_triple_cache as PTC  # noqa: E402
import rollout_eval as E  # noqa: E402
import rwm_data as R  # noqa: E402
import rwm_metrics as MET  # noqa: E402

OUT = "head_to_head_accuracy.json"
ARENA = "out-of-sample held-out pair"
UNIT = 400
HORIZONS = (1, 8, 100, 368)

# The five rows, frozen. Seeds are listed explicitly rather than discovered; an empty
# seed tuple is a single model with no seed, and `None` is the hold-last floor, which
# has no cached rollout because it has no model.
ROWS = (
    ("released", "released checkpoint (as released, ensemble of 5)", "released_ckpt_ens5", (None,)),
    ("armA", "Arm A — autoregressive, faithful MSE", "armA_faithful_mse", (0, 1, 2)),
    ("armAnll", "Arm A — autoregressive, gaussian_nll", "armA_corrected_nll", (0, 1, 2)),
    ("armB", "Arm B — teacher-forced", "armB_teacher_forced", (0, 1, 2)),
    ("floor", "hold-last floor (no model)", None, ()),
)


def model_ids():
    out = []
    for _key, _label, slug, seeds in ROWS:
        if slug is None:
            continue
        for s in seeds:
            out.append(slug if s is None else f"{slug}_seed{s}")
    return out


def main():
    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    data, ep = R.load_data(paths["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"),
                         verbose=False)
    oos = list(split["holdout_episodes"])
    starts = MET.non_overlapping_starts(ep, oos, UNIT)
    n_ind = int(MET.n_independent(starts, UNIT))
    START = E.START_STEP

    # The nRMSE denominator is the fixed training-episode scale, recomputed by the same
    # deterministic function and cross-checked against the stored copy, exactly as
    # scripts/task2_reference_nrmse.py does. It is never derived from the evaluation set.
    scale = MET.training_scale(data, ep, split["train_episodes"],
                               cfg["state_data_mean"], cfg["state_data_std"])
    stored_scale = np.array(json.load(open(os.path.join(R.RESULTS,
                                                        "step4_0a_results.json")))["nrmse_scale"])
    assert np.allclose(scale, stored_scale), "scale vector differs from the stored one"

    idx = np.asarray(starts)[:, None] + np.arange(UNIT)[None, :]
    st = R.normalise_state(data[idx][:, :, R.STATE_COLS],
                           cfg["state_data_mean"], cfg["state_data_std"]).astype(np.float32)
    truth = st[:, START:]                       # (n_traj, 368, 45), the forecast window
    den = np.abs(truth).sum(-1)                 # relative-L1 denominator, per (traj, step)

    print("=" * 96)
    print("HEAD TO HEAD — the released checkpoint against the from-scratch arms, absolute accuracy")
    print("=" * 96)
    print(f"  arena          : {ARENA}, episodes {oos}")
    print(f"  units          : {len(starts)} non-overlapping {UNIT}-step trajectories, "
          f"n_independent = {n_ind}")
    print(f"  forecast window: steps {START}..{UNIT - 1}, {truth.shape[1]} steps")
    print(f"  metrics        : nRMSE form 1 (pooled) and relative-L1, both cumulative over 1..h\n")

    def cells(err):
        """err: (n_traj, 368, 45) signed residual, prediction minus truth."""
        assert err.shape == truth.shape, f"{err.shape} != {truth.shape}"
        num = np.abs(err).sum(-1)
        sq = (err.astype(np.float64)) ** 2
        return {str(h): {"l1": float((num[:, :h] / den[:, :h]).mean()),
                         "nrmse": MET.nrmse_pooled(sq[:, :h], scale)}
                for h in HORIZONS}

    # Provenance of every file this reads, recorded rather than assumed.
    files = []
    for mid in model_ids():
        p = PTC.path_for(mid, ARENA, UNIT)
        files.append({"path": R.rel(p),
                      "sha256": PTC.sha256(p), "bytes": os.path.getsize(p)})

    rows, provenance = {}, {}
    for key, label, slug, seeds in ROWS:
        if slug is None:
            # Hold-last: predict the last teacher-forced state for every forecast step.
            err = np.repeat(st[:, START - 1:START], truth.shape[1], axis=1) - truth
            rows[key] = {"label": label, "n_models": 0, "per_model": {},
                         "cells": cells(err)}
            provenance[key] = {"rollout": "none — the floor is the observed state at "
                                          "step 31, not a model output"}
            continue
        per_model, metas = {}, []
        for s in seeds:
            mid = slug if s is None else f"{slug}_seed{s}"
            arr, meta = PTC.read(mid, ARENA, UNIT)
            assert meta["arena"] == ARENA, f"{mid}: arena {meta['arena']}"
            assert meta["unit_length"] == UNIT, f"{mid}: unit {meta['unit_length']}"
            assert meta["start_step"] == START, f"{mid}: start {meta['start_step']}"
            assert meta["n_trajectories"] == len(starts), f"{mid}: n_traj"
            assert meta["n_independent"] == n_ind, f"{mid}: n_independent"
            assert meta["episodes"] == oos, f"{mid}: episodes {meta['episodes']}"
            assert meta["residual_space"] == "config-normalised state", f"{mid}: space"
            assert meta["residual_sign_convention"] == "prediction minus truth", f"{mid}: sign"
            per_model[mid] = cells(arr["err"])
            metas.append(meta)
        agg = {}
        for h in HORIZONS:
            for m in ("l1", "nrmse"):
                v = [per_model[k][str(h)][m] for k in per_model]
                agg.setdefault(str(h), {})[m] = float(np.mean(v))
                agg[str(h)][m + "_sd_ddof1"] = float(np.std(v, ddof=1)) if len(v) > 1 else None
        rows[key] = {"label": label, "n_models": len(per_model), "per_model": per_model,
                     "cells": agg}
        provenance[key] = {"model_ids": sorted(per_model),
                           "produced_by": sorted({m["produced_by"] for m in metas}),
                           "lite_commit": sorted({m["lite_commit"] for m in metas}),
                           "rsl_commit": sorted({m["rsl_commit"] for m in metas})}

    hdr = "    " + f"{'row':<50s}" + "".join(f"{'h=' + str(h):>20s}" for h in HORIZONS)
    print(hdr)
    print("    " + f"{'':<50s}" + "".join(f"{'nRMSE':>10s}{'rel-L1':>10s}" for _ in HORIZONS))
    print("    " + "-" * (50 + 20 * len(HORIZONS)))
    for key, label, _slug, _seeds in ROWS:
        line = "    " + f"{rows[key]['label']:<50s}"
        for h in HORIZONS:
            c = rows[key]["cells"][str(h)]
            line += f"{c['nrmse']:>10.4f}{c['l1']:>10.4f}"
        print(line)

    # The one thing a reader will want checked rather than asserted in prose: whether the
    # reimplementation is ahead of or behind the released checkpoint, per horizon, per
    # metric. Derived here so the paper's sentence is read from the artifact.
    best = {}
    for h in HORIZONS:
        for m in ("nrmse", "l1"):
            ranked = sorted(((rows[k]["cells"][str(h)][m], k) for k, _l, _s, _q in ROWS))
            best[f"{m}_h{h}"] = {"leader": ranked[0][1], "value": ranked[0][0],
                                 "released": rows["released"]["cells"][str(h)][m],
                                 "order": [k for _v, k in ranked]}
    def leaders_at(h):
        return {best[f"{m}_h{h}"]["leader"] for m in ("nrmse", "l1")}

    # A horizon is only awarded to a row when BOTH metrics agree it leads there. The two
    # aggregations have inverted a comparison against the released checkpoint before
    # (M-19, R-27, R-29, Appendix H), so a horizon where they disagree is reported as a
    # disagreement rather than resolved by picking one.
    rel_sweep = [h for h in HORIZONS if leaders_at(h) == {"released"}]
    armA_sweep = [h for h in HORIZONS if leaders_at(h) <= {"armA", "armAnll"}
                  and len(leaders_at(h)) == 1]
    split = [h for h in HORIZONS if len(leaders_at(h)) > 1]
    assert len(rel_sweep) + len(armA_sweep) + len(split) <= len(HORIZONS)
    print(f"\n  both metrics put the released checkpoint first at h = {rel_sweep or 'none'}")
    print(f"  both metrics put an Arm A variant first at h = {armA_sweep or 'none'}")
    print(f"  the two metrics name different leaders at h = {split or 'none'}")

    ins = json.load(open(os.path.join(R.RESULTS, "insample_framing.json")))
    assert ins["fully_in_sample"] is True, "insample_framing no longer says fully in-sample"

    rec = {
        "table": "head-to-head absolute accuracy, released checkpoint vs from-scratch arms",
        "computation": "read from stored rollouts; no model is evaluated here",
        "arena": ARENA,
        "arena_episodes": oos,
        "n_trajectories": len(starts),
        "n_independent": n_ind,
        "traj_start_row": [int(s) for s in starts],
        "unit_length": UNIT,
        "start_step": START,
        "n_forecast_steps": int(truth.shape[1]),
        "horizons": list(HORIZONS),
        "arm_checkpoint": "weights_2500.pt",
        "arm_seeds": [0, 1, 2],
        "seed_aggregation": "mean over seeds of the per-seed value; the per-seed values "
                            "are in per_model and the ddof=1 spread beside each cell",
        "metrics": {"nrmse": "form 1, pooled (src/rwm_metrics.py:nrmse_pooled); "
                             "cumulative mean over forecast steps 1..h",
                    "l1": "relative-L1 (src/rollout_eval.py:143); cumulative mean over "
                          "forecast steps 1..h"},
        "released_checkpoint": ins["released_checkpoint"],
        "released_ckpt_arena_is_in_sample": ins["fully_in_sample"],
        "released_ckpt_in_sample_reason": ins["note_on_split"],
        "released_ckpt_trained_on_n_episodes": ins["n_trained_on"],
        "released_ckpt_bias_direction": ins["direction_of_bias"],
        "rows": rows,
        "leaders": best,
        "released_leads_both_metrics_at": rel_sweep,
        "armA_leads_both_metrics_at": armA_sweep,
        "metrics_disagree_at": split,
        # A.4 / Appendix B: the input set as data, in the artifact.
        "input_files": files,
        "input_selection": "explicit frozen list; no pattern-based discovery",
        "no_new_rollout": ("every model row is a stored per-triple cache object written by "
                           "scripts/task1_calibration.py STORE_PER_TRIPLE=1 and verified "
                           "bitwise by scripts/gate_per_triple.py; nothing is rolled out here"),
    }
    json.dump(rec, open(os.path.join(R.RESULTS, OUT), "w"), indent=2)
    print(f"\n  wrote results/{OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
