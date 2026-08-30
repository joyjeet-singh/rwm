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

    print(f"  figures recomputed from the cache : {checked}")
    print(f"  bitwise identical to the published: {exact}")
    print(f"  differing                          : {len(mismatched)}\n")
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
