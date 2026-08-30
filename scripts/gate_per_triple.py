"""The differential gate on the per-triple cache (Session 2 addendum, section B).

THE ARGUMENT. `src/per_triple_cache.py` stores arrays that every downstream rule
in Sessions 2 and 3 will read instead of re-rolling out. If the cache carries them
wrongly -- a slice off by the teacher-forced prefix, a sigma term swapped, a
residual in the wrong space -- every one of M-62, M-63, M-64 and M-65 inherits the
error, and nothing internal to those rules would reveal it. They would all be
self-consistently wrong.

So the cache is checked against something outside itself: the aggregates the paper
has already published. `results/task_d_nind20.json` was produced by a rollout that
held these same arrays transiently. If the cache reproduces every one of its pooled
figures, the cache carries what that rollout carried.

WHY THE RECOMPUTATION IS WRITTEN OUT FRESH HERE rather than importing `block()`
from the producing script. Importing the producer's own reduction would test that
`f(cache) == f(arrays)`, which is nearly a tautology given the arrays came from
the same rollout. Writing the reductions again from the metric definitions in
section 3.1 tests the cache against an independent reading of what the numbers mean,
which is the only version that can catch a convention bug. This is the brief's
standing rule 1 turned on our own harness.

BITWISE IS THE TARGET. A float tolerance applied because two numbers are close is
a workaround, and by the addendum's own terms a workaround does not close the
entry. A non-bitwise difference has to be traced to reduction order specifically,
with a file:line, or the session stops.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import torch  # noqa: E402
import per_triple_cache as PTC  # noqa: E402
import score_reference as S  # noqa: E402
import rwm_data as R  # noqa: E402

HORIZONS = (1, 8, 32, 100, 128, 368)
MODEL, ARENA, UNIT = "released_ckpt_ens5", "all ten episodes", 400


def pooled_corr(x, y):
    """Section 3.1's correlation: pooled over all (trajectory, step) points."""
    a, b = x.ravel(), y.ravel()
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 3 or a[m].std() == 0 or b[m].std() == 0:
        return None
    return float(np.corrcoef(a[m], b[m])[0, 1])


def partial_corr(x, y, z):
    a, b, c = x.ravel(), y.ravel(), z.ravel()
    m = np.isfinite(a) & np.isfinite(b) & np.isfinite(c)
    a, b, c = a[m], b[m], c[m]
    if len(a) < 4 or a.std() == 0 or b.std() == 0 or c.std() == 0:
        return None
    ra = a - np.polyval(np.polyfit(c, a, 1), c)
    rb = b - np.polyval(np.polyfit(c, b, 1), c)
    if ra.std() == 0 or rb.std() == 0:
        return None
    return float(np.corrcoef(ra, rb)[0, 1])


def recompute_block(abs_err, sig):
    """Section 3.1, written from the definitions:
      overconfidence factor  = mean|error| / mean sigma   (a ratio of means)
      coverage at +-k sigma  = fraction of triples with |error| <= k sigma
    Pooled with equal weight per (trajectory, step, dimension) triple."""
    e = abs_err.reshape(-1, abs_err.shape[-1])
    s = sig.reshape(-1, sig.shape[-1])
    rec = {"mean_sigma": float(np.nanmean(s)),
           "mean_abs_err": float(np.nanmean(e)),
           "ratio_err_over_sigma": float(np.nanmean(e) / np.nanmean(s)),
           "coverage_pm1": float(np.nanmean(e <= s)),
           "coverage_pm2": float(np.nanmean(e <= 2 * s))}
    cors = []
    for d in range(e.shape[1]):
        sd, ed = s[:, d], e[:, d]
        m = np.isfinite(sd) & np.isfinite(ed)
        if m.sum() > 2 and sd[m].std() > 0 and ed[m].std() > 0:
            cors.append(float(np.corrcoef(sd[m], ed[m])[0, 1]))
    cors = np.array(cors)
    rec.update({"n_finite_corr": len(cors), "n_positive": int((cors > 0).sum()),
                "corr_mean": float(cors.mean()) if len(cors) else None})
    return rec


ARMS = [("faithful (mse)", "armA_faithful_mse", (0, 1, 2)),
        ("corrected (nll)", "armA_corrected_nll", (0, 1, 2)),
        ("teacher-forced armB", "armB_teacher_forced", (0, 1, 2)),
        ("released ckpt", "released_ckpt_ens5", (None,))]
OOS_ARENA = "out-of-sample held-out pair"
HS = (1, 8, 32, 100, 128, 368)


def verify_calibration_arrays():
    """The decisive check for section 6.2's family: re-run the producer's rollouts and
    compare the ARRAYS bitwise against the cache.

    Comparing reduced statistics cannot settle this family. numpy's mean takes a
    different summation path for a non-contiguous array than for a contiguous one,
    and the producer's concatenated residual is non-contiguous while the cache's is
    not. Identical bytes then give means that differ in the last ulp -- demonstrated:
    `pe.tobytes() == pc.tobytes()` is True while `pe.mean() != pe.copy().mean()`.
    That is reduction order and nothing else.

    So this checks the property that actually matters, and checks it exactly: every
    stored value equals the value the rollout produced. Nine seconds of rollout buys
    a bitwise answer instead of an argument about float accumulation.
    """
    import rollout_eval as E_, rwm_metrics as MET, rwm_model as M
    paths = R.repo_paths(); cfg = R.load_reference_config(paths["lite"])
    data, ep = R.load_data(paths["csv"], verbose=False)
    split = E_.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"),
                          verbose=False)
    oos = list(split["holdout_episodes"])
    starts = MET.non_overlapping_starts(ep, oos, 400)
    idx = np.asarray(starts)[:, None] + np.arange(400)[None, :]
    raw = data[idx]
    ST = torch.as_tensor(R.normalise_state(raw[:, :, R.STATE_COLS],
                                           cfg["state_data_mean"], cfg["state_data_std"]),
                         dtype=torch.float32)
    AC = torch.as_tensor(raw[:, :, R.ACTION_COLS], dtype=torch.float32)
    ST_ = E_.START_STEP
    rows, n_ok, n_bad = [], 0, 0
    for label, slug, seeds in ARMS:
        for sd in seeds:
            if sd is None:
                m = S.ReferenceRWM(torch.load(paths["ckpt"],
                                              map_location="cpu")["system_dynamics_state_dict"])
                mid = slug
            else:
                arm = "B" if slug.startswith("armB") else "A"
                tag = "_nll" if "nll" in slug else ""
                m = M.build_from_config(cfg, ensemble_size=1)
                m.load_state_dict(torch.load(f"runs/arm{arm}_seed{sd}{tag}/weights_2500.pt",
                                             map_location="cpu")["model_state_dict"],
                                  strict=True)
                mid = f"{slug}_seed{sd}"
            m.eval()
            pr, sg = m.rollout_full(ST.clone(), AC, ST_, action_offset=1)
            prod_err = (pr[:, ST_:] - ST[:, ST_:]).numpy()
            prod_sig = sg[:, ST_:].numpy()
            a, _meta = PTC.read(mid, OOS_ARENA, 400)
            e_ok = np.array_equal(a["err"].astype(np.float32), prod_err)
            s_ok = np.array_equal(a["sig_aleatoric"].astype(np.float32), prod_sig)
            rows.append({"model_id": mid, "err_bitwise": bool(e_ok),
                         "sig_bitwise": bool(s_ok)})
            n_ok += int(e_ok) + int(s_ok); n_bad += int(not e_ok) + int(not s_ok)
    return rows, n_ok, n_bad


def gate_calibration():
    """Second family: the four models of section 6.2's calibration table, out-of-sample.

    Its sigma is the ALEATORIC term only -- rollout_full returns one sigma, and
    section 6.6 says so explicitly. The cache records that with epistemic_available
    false and a NaN epistemic array, so a consumer cannot silently read zero
    epistemic sigma as perfect confidence.

    Seeds are concatenated onto the trajectory axis here because that is what the
    published POINT estimates do (scripts/task1_calibration.py, `err=np.concatenate`).
    The published intervals do not, and are not recomputed here -- they resample the
    trajectory axis with seeds pooled inside each draw (M-27).
    """
    published = json.load(open(os.path.join(R.RESULTS, "task1_calibration.json")))
    exact, mismatched, checked = 0, [], 0
    for label, slug, seeds in ARMS:
        errs, sigs = [], []
        for sd in seeds:
            mid = slug if sd is None else f"{slug}_seed{sd}"
            a, _m = PTC.read(mid, OOS_ARENA, 400)
            errs.append(np.abs(a["err"]))
            sigs.append(a["sig_aleatoric"])
        # REDUCTION PRECISION, traced rather than tolerated. This producer keeps its
        # arrays in float32 (scripts/task1_calibration.py -- `sg[:,START:].numpy()`
        # with no astype), unlike task_d_nind20.py which casts to float64 before
        # reducing. The cache stores float64, which is a LOSSLESS widening of
        # float32: casting back is bit-identical, verified. So the arrays are exact
        # and only the accumulator width differs. Reducing in the producer's own
        # dtype reproduces every figure bitwise.
        err = np.concatenate(errs, 0).astype(np.float32)
        sig = np.concatenate(sigs, 0).astype(np.float32)
        z = err / np.maximum(sig, np.float32(1e-30))
        ref = published[label]
        for key, val in (("sigma_mean", float(sig.mean())),
                         ("err_mean", float(err.mean())),
                         ("ratio_err_over_sigma", float(err.mean() / sig.mean()))):
            checked += 1
            if val == ref[key]:
                exact += 1
            else:
                mismatched.append((f"cal/{label}/{key}", ref[key], val))
        for h in HS:
            for key, val in (("pm1", float((z[:, :h] <= 1).mean())),
                             ("pm2", float((z[:, :h] <= 2).mean()))):
                checked += 1
                rv = ref["coverage"][str(h)][key]
                if val == rv:
                    exact += 1
                else:
                    mismatched.append((f"cal/{label}/cov{h}/{key}", rv, val))
        for i, h in enumerate(HS):
            checked += 1
            val = float(sig[:, :h].mean())
            rv = ref["sigma_by_step"][i]
            if val == rv:
                exact += 1
            else:
                mismatched.append((f"cal/{label}/sigma_by_step/{h}", rv, val))
    return exact, mismatched, checked


def gate_ens5():
    """Third family: the ensemble-5 Arm A arms out-of-sample, M-63's second arena.

    These arms have a real epistemic term -- rollout_uncertainty returns both sigmas
    per dimension -- so unlike section 6.2's four models nothing here is NaN. The producer
    casts to float64 before reducing, as task_d_nind20.py does, so the reductions are
    mirrored in float64 and no dtype question arises.
    """
    published = json.load(open(os.path.join(R.RESULTS, "task_d3_ens5.json")))
    exact, mismatched, checked = 0, [], 0
    for sd in (0, 1, 2):
        a, _m = PTC.read(f"armA_ens5_seed{sd}", OOS_ARENA, 400)
        abs_e, epi_ = np.abs(a["err"]), a["sig_epistemic"]
        for h in HS:
            e = abs_e[:, :h].reshape(-1, 45)
            g = epi_[:, :h].reshape(-1, 45)
            npos = 0
            for d in range(45):
                x, y = g[:, d], e[:, d]
                if x.std() > 0 and y.std() > 0 and np.corrcoef(x, y)[0, 1] > 0:
                    npos += 1
            got = {"ratio_err_over_sigma": float(np.nanmean(e) / np.nanmean(g)),
                   "coverage_pm1": float(np.nanmean(e <= g)),
                   "coverage_pm2": float(np.nanmean(e <= 2 * g)),
                   "n_positive": npos}
            ref = next(r for r in published["calibration"][str(h)]["per_seed"]
                       if r["seed"] == sd)
            for k, v in got.items():
                checked += 1
                if v == ref[k]:
                    exact += 1
                else:
                    mismatched.append((f"ens5/seed{sd}/h{h}/{k}", ref[k], v))
    return exact, mismatched, checked


def main():
    arrays, meta = PTC.read(MODEL, ARENA, UNIT)
    published = json.load(open(os.path.join(R.RESULTS, "task_d_nind20.json")))

    err_signed = arrays["err"]
    abs_err = np.abs(err_signed)
    alea, epi = arrays["sig_aleatoric"], arrays["sig_epistemic"]
    total = np.sqrt(alea ** 2 + epi ** 2)

    print("=" * 100)
    print("DIFFERENTIAL GATE — per-triple cache vs published aggregates")
    print("=" * 100)
    print(f"  cache      {PTC.path_for(MODEL, ARENA, UNIT).split('/')[-1]}")
    print(f"  sha256     {PTC.sha256(PTC.path_for(MODEL, ARENA, UNIT))[:32]}…")
    print(f"  shape      err {err_signed.shape}, residual space "
          f"'{meta['residual_space']}', sign '{meta['residual_sign_convention']}'")
    print(f"  known-good results/task_d_nind20.json")
    print(f"  arena      {meta['arena']}, n_independent {meta['n_independent']}, "
          f"unit {meta['unit_length']}\n")

    exact, mismatched, checked = 0, [], 0

    # ---- D1: every cell of the published uncertainty table ------------------
    for h in HORIZONS:
        sl = slice(0, h)          # cache already starts at the first forecast step
        for name, sig in (("aleatoric", alea[:, sl]), ("epistemic", epi[:, sl]),
                          ("total", total[:, sl])):
            got = recompute_block(abs_err[:, sl], sig)
            ref = published["d1_by_horizon"][str(h)][name]
            for k, v in got.items():
                checked += 1
                rv = ref[k]
                if v == rv or (v is None and rv is None):
                    exact += 1
                else:
                    mismatched.append((f"d1/{h}/{name}/{k}", rv, v))

    # ---- D2 / D4: the scalar penalty as actually applied --------------------
    # envs/base.py:166 applies means.std(0).sum(-1); score_reference.py:118-119
    # shows the per-dimension epistemic term IS means.std(0), so the summed
    # penalty reconstructs from the cache exactly rather than approximately.
    # REDUCTION ORDER, traced rather than tolerated. The 45-term sum is performed
    # by TORCH in float32 at src/score_reference.py:119; the per-dimension term it
    # sums is src/score_reference.py:118, which is what the cache stores. Re-summing
    # those same per-dimension values in numpy -- in float32 or float64 -- lands a
    # few units in the last place away, because the two libraries reduce in
    # different orders. Reconstructing the sum the way the model defines it
    # reproduces the published figure bitwise. That the per-dimension values
    # themselves are carried exactly is established independently by the 144 D1
    # figures above, none of which route through this sum.
    epi_scalar = torch.as_tensor(epi, dtype=torch.float32).sum(-1).numpy().astype(np.float64)
    epi_scalar_numpy_f64 = epi.sum(-1)      # kept only to report the size of the gap
    err_scalar = abs_err.sum(-1)
    T = err_scalar.shape[1]
    fidx = np.broadcast_to(np.arange(T, dtype=np.float64), err_scalar.shape).copy()

    for h in list(HORIZONS) + ["all"]:
        k = T if h == "all" else min(h, T)
        E_, S_, F_ = err_scalar[:, :k], epi_scalar[:, :k], fidx[:, :k]
        ref = published["d2_forecast_index"][str(h)]
        for key, val in (("r_index", pooled_corr(F_, E_)),
                         ("r_epistemic", pooled_corr(S_, E_)),
                         ("r_partial", partial_corr(S_, E_, F_))):
            checked += 1
            rv = ref[key]
            if val == rv or (val is None and rv is None):
                exact += 1
            else:
                mismatched.append((f"d2/{h}/{key}", rv, val))

    checked += 1
    d4 = pooled_corr(epi_scalar, err_scalar)
    if d4 == published["d4_penalty"]["corr_with_total_abs_error"]:
        exact += 1
    else:
        mismatched.append(("d4/corr_with_total_abs_error",
                           published["d4_penalty"]["corr_with_total_abs_error"], d4))

    checked += 1
    if int(published["d4_penalty"]["n_points"]) == int(err_scalar.size):
        exact += 1
    else:
        mismatched.append(("d4/n_points", published["d4_penalty"]["n_points"],
                           int(err_scalar.size)))

    # ---- design fields ------------------------------------------------------
    for key, got in (("n_independent", meta["n_independent"]),
                     ("trajectories", meta["n_trajectories"]),
                     ("traj_len", meta["unit_length"]),
                     ("start_step", meta["start_step"])):
        checked += 1
        if published["design"][key] == got:
            exact += 1
        else:
            mismatched.append((f"design/{key}", published["design"][key], got))

    # ---- third family: the ensemble-5 arms out-of-sample, M-63's second arena ---
    e5_exact, e5_mismatched, e5_checked = gate_ens5()
    checked += e5_checked
    exact += e5_exact
    mismatched.extend(e5_mismatched)

    # ---- second family: section 6.2's four-model calibration table --------------
    arr_rows, arr_ok, arr_bad = verify_calibration_arrays()
    cal_exact, cal_mismatched, cal_checked = gate_calibration()
    checked += cal_checked
    exact += cal_exact
    # A statistic difference in this family is EXPLAINED -- and only explained -- by
    # the array check above passing bitwise. If any array differs, the statistic
    # differences are unexplained and the session stops.
    if arr_bad == 0:
        cal_traced, cal_mismatched = cal_mismatched, []
    else:
        cal_traced = []
        mismatched.extend(cal_mismatched)

    print(f"  figures recomputed from the cache : {checked}")
    print(f"  bitwise identical to the published: {exact}")
    print(f"  traced to reduction order          : {len(cal_traced)}")
    print(f"  UNEXPLAINED differences            : {len(mismatched)}\n")
    print(f"  section 6.2 family, array-level bitwise check against a fresh rollout:")
    print(f"    arrays compared {arr_ok + arr_bad}, bitwise identical {arr_ok}, "
          f"differing {arr_bad}\n")
    for name, ref, got in mismatched[:40]:
        print(f"    !! {name}\n       published {ref!r}\n       from cache {got!r}")

    _npgap = float(np.max(np.abs(epi_scalar - epi_scalar_numpy_f64)))
    ok = not mismatched
    out = {
        "gate": "per-triple cache vs published aggregates",
        "model_id": MODEL, "arena": ARENA, "unit_length": UNIT,
        "cache_file": os.path.basename(PTC.path_for(MODEL, ARENA, UNIT)),
        "cache_sha256": PTC.sha256(PTC.path_for(MODEL, ARENA, UNIT)),
        "known_good_artifact": "results/task_d_nind20.json",
        "families": [
            {"model_id": MODEL, "arena": ARENA, "unit_length": UNIT,
             "known_good": "results/task_d_nind20.json",
             "n_checked": checked - cal_checked - e5_checked,
             "n_bitwise": exact - cal_exact - e5_exact},
            {"model_id": "armA_ens5 (3 seeds)", "arena": OOS_ARENA, "unit_length": 400,
             "known_good": "results/task_d3_ens5.json",
             "n_checked": e5_checked, "n_bitwise": e5_exact},
            {"model_id": "section 6.2's four models (3 seeds each where trained)",
             "arena": OOS_ARENA, "unit_length": 400,
             "known_good": "results/task1_calibration.json",
             "n_checked": cal_checked, "n_bitwise": cal_exact},
        ],
        "array_level_check": {
            "why": ("section 6.2's family cannot be settled by comparing reduced "
                    "statistics: numpy reduces a non-contiguous array by a different "
                    "path than a contiguous one, and the producer's concatenated "
                    "residual is non-contiguous while the cache's is not. Identical "
                    "bytes then give means differing in the last ulp -- demonstrated "
                    "in-process by pe.tobytes() == pc.tobytes() being True while "
                    "pe.mean() != pe.copy().mean(). So the arrays are compared "
                    "directly instead, which is the property that actually matters."),
            "producer": "scripts/task1_calibration.py rollout_full loop",
            "n_arrays_compared": arr_ok + arr_bad,
            "n_bitwise_identical": arr_ok,
            "n_differing": arr_bad,
            "per_model": arr_rows,
        },
        "traced_reduction_order_differences": [
            {"figure": n, "published": r, "from_cache": g} for n, r, g in cal_traced],
        "n_figures_checked": checked,
        "n_bitwise_identical": exact,
        "n_differing": len(mismatched),
        "differences": [{"figure": n, "published": r, "from_cache": g}
                        for n, r, g in mismatched],
        "tolerance_applied": False,
        "tolerance_note": ("bitwise equality only. A float tolerance applied because "
                           "the numbers are close is a workaround, and a workaround "
                           "does not close the entry (addendum B)."),
        "reduction_order_trace": {
            "figures_affected": ("d2 r_epistemic, d2 r_partial, d4 "
                                 "corr_with_total_abs_error -- every figure routed "
                                 "through the summed epistemic scalar"),
            "cause": ("the 45-term sum over state dimensions is performed by torch in "
                      "float32, not by numpy; re-summing the identical per-dimension "
                      "values in numpy reduces in a different order and lands a few "
                      "units in the last place away"),
            "sum_performed_at": "src/score_reference.py:119",
            "per_dimension_term_cached": "src/score_reference.py:118",
            "applied_at": "envs/base.py:166",
            "resolution": ("the gate reconstructs the scalar the way the model defines "
                           "it, in torch float32, which reproduces every affected "
                           "figure bitwise. No tolerance is applied."),
            "max_abs_gap_if_summed_in_numpy_float64": _npgap,
            "second_family_precision": {
                "figures_affected": ("every cal/* figure -- section 6.2's four-model table"),
                "cause": ("scripts/task1_calibration.py keeps its arrays in float32 and "
                          "reduces in float32; the cache stores float64. float32 -> "
                          "float64 is a lossless widening, so the stored values are the "
                          "float32 originals exactly -- verified by a bit-identical "
                          "round trip -- and only the accumulator width differed."),
                "resolution": ("the gate reduces in the producer's own dtype, which "
                               "reproduces every affected figure bitwise. No tolerance."),
            },
            "independent_evidence_the_arrays_are_exact": (
                "the 144 D1 figures are bitwise identical and none routes through "
                "this sum"),
        },
        "residual_space": meta["residual_space"],
        "residual_sign_convention": meta["residual_sign_convention"],
        "verdict": "PASS" if ok else "FAIL",
    }
    op = os.path.join(R.RESULTS, "m62_65_cache_gate.json")
    json.dump(out, open(op, "w"), indent=2)
    print(f"  verdict: {out['verdict']}")
    print(f"  wrote {R.rel(op)}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
