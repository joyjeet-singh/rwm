"""A.1 -- the free differential gate on M-64's new rollout invocations.

THE ARGUMENT, from SESSION_2B.md and the Session 3 addendum. The full set of
non-overlapping short units cannot be cut from the cached 400-step rollouts: the second
and later units start inside the long rollout's autoregressive region, where a fresh unit
would teacher-force from ground truth instead.

But the FIRST short unit of each long rollout is an exact slice. Same start row, same
32-row teacher-forced prefix, same deterministic mean feedback -- so forecast steps 1..h of
the cached 400-step rollout must equal a fresh 32+h unit at that row, BITWISE.

That gives Session 3's new rollout machinery a known-good side for free, before any
short-unit statistic is computed. If the short-unit builder has an off-by-one in the
history window, feeds actions at the wrong offset, or slices the forecast from the wrong
place, this catches it against the cache rather than against itself.

Same stop condition as Session 2's half one: an unexplained difference stops the session.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import torch  # noqa: E402
import rwm_data as R  # noqa: E402
import rollout_eval as E  # noqa: E402
import rwm_model as M  # noqa: E402
import score_reference as S  # noqa: E402
import per_triple_cache as PTC  # noqa: E402

HS = (1, 8, 32, 100, 128)
START = E.START_STEP

# (cache model_id, arena, loader, uses rollout_uncertainty)
CASES = [
    ("released_ckpt_ens5", "all ten episodes", ("released", None), True),
    ("released_ckpt_ens5", "out-of-sample held-out pair", ("released", None), False),
    ("armA_faithful_mse_seed0", "out-of-sample held-out pair", ("arm", ("A", 0, "")), False),
    ("armA_corrected_nll_seed1", "out-of-sample held-out pair", ("arm", ("A", 1, "_nll")), False),
    ("armB_teacher_forced_seed2", "out-of-sample held-out pair", ("arm", ("B", 2, "")), False),
    ("armA_ens5_seed0", "out-of-sample held-out pair", ("ens5", 0), True),
]


def build(kind, spec, cfg, paths):
    if kind == "released":
        sd = torch.load(paths["ckpt"], map_location="cpu")["system_dynamics_state_dict"]
        m = S.ReferenceRWM(sd)
    elif kind == "ens5":
        sd = torch.load(f"runs/armA_seed{spec}_ens5/weights_2500.pt",
                        map_location="cpu")["model_state_dict"]
        m = S.ReferenceRWM(sd)
    else:
        arm, seed, tag = spec
        m = M.build_from_config(cfg, ensemble_size=1)
        m.load_state_dict(torch.load(f"runs/arm{arm}_seed{seed}{tag}/weights_2500.pt",
                                     map_location="cpu")["model_state_dict"], strict=True)
    m.eval()
    return m


def short_unit_rollout(model, data, cfg, start_rows, h, uncertainty):
    """One fresh 32+h unit per start row. Returns (signed residual, aleatoric, epistemic),
    each (n_units, h, 45); epistemic is None for an ensemble-size-1 arm."""
    length = START + h
    idx = np.asarray(start_rows)[:, None] + np.arange(length)[None, :]
    raw = data[idx]
    st = torch.as_tensor(R.normalise_state(raw[:, :, R.STATE_COLS],
                                           cfg["state_data_mean"], cfg["state_data_std"]),
                         dtype=torch.float32)
    ac = torch.as_tensor(raw[:, :, R.ACTION_COLS], dtype=torch.float32)
    if uncertainty:
        pred, alea, epi, _as, _es = model.rollout_uncertainty(st.clone(), ac, START,
                                                              action_offset=1)
        return ((pred - st).numpy()[:, START:], alea.numpy()[:, START:],
                epi.numpy()[:, START:])
    pred, sg = model.rollout_full(st.clone(), ac, START, action_offset=1)
    return (pred - st).numpy()[:, START:], sg.numpy()[:, START:], None


def main():
    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    data, _ep = R.load_data(paths["csv"], verbose=False)

    rows, n_ok, n_bad = [], 0, 0
    for model_id, arena, (kind, spec), unc in CASES:
        arrays, meta = PTC.read(model_id, arena, 400)
        starts = np.asarray(arrays["traj_start_row"])
        model = build(kind, spec, cfg, paths)
        for h in HS:
            err_f, alea_f, epi_f = short_unit_rollout(model, data, cfg, starts, h, unc)
            # The cache stores float64 widened from the producer's float32; compare in
            # float32, the dtype the rollout actually produced. The widening is lossless,
            # which Session 2's gate established by a bit-identical round trip.
            e_ok = np.array_equal(arrays["err"][:, :h].astype(np.float32), err_f)
            a_ok = np.array_equal(arrays["sig_aleatoric"][:, :h].astype(np.float32), alea_f)
            if epi_f is None:
                g_ok = True          # ens1 arms: cache holds NaN by design, nothing to compare
            else:
                g_ok = np.array_equal(arrays["sig_epistemic"][:, :h].astype(np.float32), epi_f)
            ok = bool(e_ok and a_ok and g_ok)
            n_ok += int(ok); n_bad += int(not ok)
            rows.append({"model_id": model_id, "arena": arena, "h": h,
                         "n_units_compared": int(len(starts)),
                         "err_bitwise": bool(e_ok), "sig_aleatoric_bitwise": bool(a_ok),
                         "sig_epistemic_bitwise": bool(g_ok),
                         "epistemic_compared": epi_f is not None,
                         "pass": ok})

    out = {
        "gate": "M-64 free gate -- first short unit of each cached rollout is an exact slice",
        "claim": ("forecast steps 1..h of a cached 400-step rollout must equal a fresh "
                  "32+h unit at the same start row, bitwise, because the teacher-forced "
                  "prefix and the deterministic mean feedback are identical"),
        "horizons": list(HS), "history_rows": START,
        "n_comparisons": len(rows), "n_pass": n_ok, "n_fail": n_bad,
        "tolerance_applied": False,
        "dtype_note": ("compared in float32, the dtype the rollout produces. The cache "
                       "stores float64, a lossless widening -- established in Session 2 by "
                       "a bit-identical round trip."),
        "comparisons": rows,
        "verdict": "PASS" if n_bad == 0 else "FAIL",
    }
    op = os.path.join(R.RESULTS, "m64_free_gate.json")
    json.dump(out, open(op, "w"), indent=2)

    print("=" * 92)
    print("M-64 FREE GATE — first short unit vs the cached 400-step rollout")
    print("=" * 92)
    print(f"  comparisons {len(rows)}   pass {n_ok}   fail {n_bad}")
    for r in rows:
        if not r["pass"]:
            print(f"    !! {r['model_id']} [{r['arena']}] h={r['h']}  "
                  f"err {r['err_bitwise']} alea {r['sig_aleatoric_bitwise']} "
                  f"epi {r['sig_epistemic_bitwise']}")
    print(f"  verdict: {out['verdict']}")
    print(f"  wrote {R.rel(op)}")
    return 0 if n_bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
