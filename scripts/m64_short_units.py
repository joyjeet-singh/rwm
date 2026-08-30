"""3.1 -- M-64: does the horizon-scoped power increase from shorter evaluation units
change any verdict at h <= 128?

THE UNIT, fixed in the rule: 32 history rows + h forecast rows, non-overlapping within an
episode, boundaries respected exactly as section 3 defines them. History length 32 is
START_STEP and is not varied. h = 368 needs 400 rows and is untouched, so M-23 keeps its
anchor.

COUNTS ARE VERIFIED TWO WAYS -- from the segment lengths alone and from the built index --
exactly as section 3 does for the crossing count. A disagreement is the finding and stops the
measurement.

r_dd IS EXCLUDED BY DESIGN. Shorter units give fewer forecast steps to demean against,
which makes section 6.7's short-horizon instability worse rather than better. It stays at the
400-step unit.

THE INTERACTION THE RULE MUST NOT BE READ WITHOUT. More units from the same ten episodes
are not more independent if the episode is the operative cluster. M-62 returned NO MOVE, so
the episode-level version here is corroboration and is stored as a footnote field rather
than featured (Session 3 addendum A.2). n_independent is always reported at the UNIT level
and labelled as such, and no short-unit figure replaces a 400-step figure anywhere.
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

HS = (1, 8, 32, 100, 128)
START = E.START_STEP
SEEDS = (0, 1, 2)
N_BOOT = 20000
TARGET1 = 0.6827


# ----------------------------------------------------------------- index ----
def episode_spans():
    """(episode, first_row, n_rows) from the structural boundaries in src/rwm_data.py.
    ep0 is 999 rows and ep1..ep9 are 1,000; the final orphan row is discarded."""
    spans, prev = [], 0
    for e, r in enumerate(R.RESET_ROWS):
        spans.append((e, prev, r - prev))
        prev = r
    return spans                      # ten spans; row 9999 begins the discarded stub


def build_index(episodes, h):
    """Non-overlapping 32+h units inside each episode. Returns start rows and their
    episode ids, plus BOTH count derivations for the two-way check."""
    U = START + h
    spans = {e: (s, n) for e, s, n in episode_spans()}
    from_lengths = sum(spans[e][1] // U for e in episodes)
    starts, eps = [], []
    for e in episodes:
        first, n = spans[e]
        for k in range(n // U):
            s = first + k * U
            assert s + U <= first + n, "unit crosses an episode boundary"
            starts.append(s); eps.append(e)
    return np.asarray(starts), np.asarray(eps), int(from_lengths), len(starts)


# --------------------------------------------------------------- rollouts ----
def unit_rollout(model, data, cfg, starts, h, uncertainty, floor=False):
    """Fresh 32+h rollouts. Returns (signed residual, aleatoric, epistemic, pred, truth)."""
    idx = np.asarray(starts)[:, None] + np.arange(START + h)[None, :]
    raw = data[idx]
    st = torch.as_tensor(R.normalise_state(raw[:, :, R.STATE_COLS],
                                           cfg["state_data_mean"], cfg["state_data_std"]),
                         dtype=torch.float32)
    ac = torch.as_tensor(raw[:, :, R.ACTION_COLS], dtype=torch.float32)
    if floor:
        p = st.clone()
        p[:, START:] = st[:, START - 1:START].expand(-1, h, -1)
        return None, None, None, p[:, START:], st[:, START:]
    if uncertainty:
        pred, alea, epi, _a, _e = model.rollout_uncertainty(st.clone(), ac, START,
                                                            action_offset=1)
        return ((pred - st).numpy()[:, START:], alea.numpy()[:, START:],
                epi.numpy()[:, START:], pred[:, START:], st[:, START:])
    pred, sg = model.rollout_full(st.clone(), ac, START, action_offset=1)
    return ((pred - st).numpy()[:, START:], sg.numpy()[:, START:], None,
            pred[:, START:], st[:, START:])


def rel_l1(pred, truth):
    """Section 3.1's relative-L1, per unit: a 45-term sum in normalised space, meaned over steps."""
    nu = (pred - truth).abs().sum(-1)
    de = truth.abs().sum(-1)
    return (nu / de).mean(1).numpy()


# --------------------------------------------------------------- bootstrap ---
def boot_ci(per_unit_num, per_unit_den, unit_ep, rng_seed=0):
    """Cluster bootstrap at BOTH levels from per-unit partial means.

    Returns (unit_level_ci, episode_level_ci). The episode level is the footnote field:
    M-62 returned NO MOVE, so it corroborates rather than competes.
    """
    num = np.asarray(per_unit_num, dtype=np.float64)
    den = None if per_unit_den is None else np.asarray(per_unit_den, dtype=np.float64)
    n = len(num)

    def pct(vals):
        vals = vals[np.isfinite(vals)]
        return ([float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))]
                if len(vals) > 1 else [None, None])

    rng = np.random.default_rng(rng_seed)
    i = rng.integers(0, n, (N_BOOT, n))
    a = num[i].mean(1)
    unit = pct(a if den is None else a / den[i].mean(1))

    eps = np.unique(unit_ep)
    by = {e: np.flatnonzero(unit_ep == e) for e in eps}
    rng2 = np.random.default_rng(rng_seed)
    vals = []
    for _ in range(N_BOOT):
        drawn = rng2.integers(0, len(eps), len(eps))
        j = np.concatenate([by[eps[d]] for d in drawn])
        v = num[j].mean() if den is None else num[j].mean() / den[j].mean()
        vals.append(v)
    return unit, pct(np.asarray(vals))


def excl0(ci):
    return None if ci[0] is None else bool(ci[0] > 0 or ci[1] < 0)


def main():
    gate = json.load(open(os.path.join(R.RESULTS, "m64_free_gate.json")))
    assert gate["verdict"] == "PASS", "the free gate did not pass; M-64 does not run"

    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    data, ep = R.load_data(paths["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"),
                         verbose=False)
    ARENAS = {"out-of-sample held-out pair": list(split["holdout_episodes"]),
              "in-sample training episodes": list(split["train_episodes"])}
    # Cell B's published 400-step comparator (results/task_d_nind20.json) is measured over
    # ALL TEN episodes, so the short-unit side needs that arena too. Comparing an all-ten
    # 400-step figure against an out-of-sample short-unit figure would fold an arena change
    # into what is supposed to be a unit change -- exactly the confusion M-64's "every
    # figure carries its unit, its arena and its n_independent" exists to prevent.
    ARENAS_B = dict(ARENAS)
    ARENAS_B["all ten episodes"] = sorted(set(split["holdout_episodes"])
                                          | set(split["train_episodes"]))

    out = {"rule": "M-64", "free_gate": {"artifact": "results/m64_free_gate.json",
                                         "verdict": gate["verdict"],
                                         "n_pass": gate["n_pass"], "n_fail": gate["n_fail"]},
           "unit_definition": f"{START} history rows + h forecast rows, non-overlapping "
                              f"within an episode, boundaries per section 3",
           "horizons": list(HS),
           "h368_untouched": "h = 368 needs 400 rows; M-23 keeps its anchor and denominator",
           "r_dd_excluded": ("by design: shorter units give fewer steps to demean against, "
                             "which worsens section 6.7's short-horizon instability. It stays at "
                             "the 400-step unit."),
           "clustering_note": ("n_independent is reported at the UNIT level. M-62 returned "
                               "NO MOVE, so the episode-level interval stored beside each "
                               "figure is corroboration, not a competing column."),
           "arena_matching": ("each cell is compared arena-matched to the artifact holding its 400-step figure: cell C against a1_ab_by_horizon.json (out-of-sample), cell B against task_d_nind20.json (all ten episodes)"),
           "index": {}, "cells": {}}

    # ---------------- the index, verified two ways --------------------------
    index = {}
    for arena, eps in ARENAS_B.items():
        out["index"][arena] = {}
        for h in HS:
            st, ue, from_len, from_idx = build_index(eps, h)
            if from_len != from_idx:
                out["index"][arena][str(h)] = {"MISMATCH": True,
                                               "from_segment_lengths": from_len,
                                               "from_built_index": from_idx}
                json.dump(out, open(os.path.join(R.RESULTS, "m64_short_units.json"), "w"),
                          indent=2)
                raise SystemExit(f"COUNT MISMATCH {arena} h={h}: {from_len} vs {from_idx}")
            index[(arena, h)] = (st, ue)
            out["index"][arena][str(h)] = {
                "unit_length": START + h, "n_units": from_idx,
                "from_segment_lengths": from_len, "from_built_index": from_idx,
                "counts_agree": True, "n_episodes": len(eps),
                "n_independent_unit_level": from_idx,
                "units_per_episode": {str(int(e)): int((ue == e).sum())
                                      for e in np.unique(ue)}}

    print("M-64 index built and verified two ways:")
    for arena in ARENAS:
        print("  " + arena + ": " + ", ".join(
            f"h={h} n={out['index'][arena][str(h)]['n_units']}" for h in HS))

    # ---------------- cell A: section 6.2's calibration table -----------------------
    ARMS = [("faithful (mse)", "A", "", SEEDS), ("corrected (nll)", "A", "_nll", SEEDS),
            ("teacher-forced armB", "B", "", SEEDS), ("released ckpt", None, None, (None,))]
    cellA = {}
    for label, arm, tag, seeds in ARMS:
        models = []
        for s in seeds:
            if arm is None:
                sd = torch.load(paths["ckpt"], map_location="cpu")["system_dynamics_state_dict"]
                m = S.ReferenceRWM(sd)
            else:
                m = M.build_from_config(cfg, ensemble_size=1)
                m.load_state_dict(torch.load(f"runs/arm{arm}_seed{s}{tag}/weights_2500.pt",
                                             map_location="cpu")["model_state_dict"],
                                  strict=True)
            m.eval(); models.append(m)
        cellA[label] = {}
        for arena in ARENAS:
            cellA[label][arena] = {}
            for h in HS:
                st, ue = index[(arena, h)]
                pe, pg, p1 = [], [], []
                for m in models:
                    e, g, _gi, _p, _t = unit_rollout(m, data, cfg, st, h, False)
                    e = np.abs(e)
                    pe.append(e.mean(axis=(1, 2))); pg.append(g.mean(axis=(1, 2)))
                    p1.append((e <= g).mean(axis=(1, 2)))
                pe, pg, p1 = np.mean(pe, 0), np.mean(pg, 0), np.mean(p1, 0)
                cu, ce = boot_ci(pe, pg, ue)
                k1u, k1e = boot_ci(p1, None, ue)
                cellA[label][arena][str(h)] = {
                    "unit_length": START + h, "n_independent_unit_level": int(len(st)),
                    "n_episodes": len(ARENAS[arena]),
                    "ratio_err_over_sigma": float(pe.mean() / pg.mean()),
                    "ratio_ci_unit_level": cu,
                    "coverage_pm1": float(p1.mean()), "coverage_pm1_ci_unit_level": k1u,
                    "coverage_pm1_excludes_calibrated_target": (
                        None if k1u[0] is None else bool(k1u[1] < TARGET1 or k1u[0] > TARGET1)),
                    "footnote_episode_level": {"ratio_ci": ce, "coverage_pm1_ci": k1e,
                                               "n_episodes": len(ARENAS[arena])}}
    out["cells"]["A_section_6_2_calibration"] = cellA
    print("  cell A done")

    # ---------------- cell B: section 6.7's pooled correlation and free baselines ----
    sd = torch.load(paths["ckpt"], map_location="cpu")["system_dynamics_state_dict"]
    rel = S.ReferenceRWM(sd); rel.eval()
    cellB = {}
    for arena in ARENAS_B:
        cellB[arena] = {}
        for h in HS:
            st, ue = index[(arena, h)]
            e, _a, gi, pred, _t = unit_rollout(rel, data, cfg, st, h, True)
            abs_e = np.abs(e)
            # the scalar penalty as applied, summed in torch as the model defines it
            disagree = torch.as_tensor(gi, dtype=torch.float32).sum(-1).numpy().astype(np.float64)
            err_s = abs_e.sum(-1)
            n_units, T = err_s.shape
            fidx = np.broadcast_to(np.arange(T, dtype=np.float64), err_s.shape).copy()
            # free baseline: the model's own predicted step size ||mu_t - mu_{t-1}||
            pm = pred.numpy().astype(np.float64)
            step = np.zeros_like(err_s)
            if T > 1:
                step[:, 1:] = np.linalg.norm(np.diff(pm, axis=1), axis=-1)

            def pc(x, y):
                a, b = x.ravel(), y.ravel()
                mk = np.isfinite(a) & np.isfinite(b)
                if mk.sum() < 3 or a[mk].std() == 0 or b[mk].std() == 0:
                    return None
                return float(np.corrcoef(a[mk], b[mk])[0, 1])

            def paired(idx):
                d, f, er = disagree[idx], fidx[idx], err_s[idx]
                r1, r2 = pc(d, er), pc(f, er)
                return None if (r1 is None or r2 is None) else r1 - r2

            rng = np.random.default_rng(0)
            vals = [paired(rng.integers(0, n_units, n_units)) for _ in range(2000)]
            vals = np.array([v for v in vals if v is not None and np.isfinite(v)])
            pd_ci = ([float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))]
                     if len(vals) > 1 else [None, None])
            eps_u = np.unique(ue); by = {x: np.flatnonzero(ue == x) for x in eps_u}
            rng2 = np.random.default_rng(0)
            ev = []
            for _ in range(2000):
                dr = rng2.integers(0, len(eps_u), len(eps_u))
                v = paired(np.concatenate([by[eps_u[d]] for d in dr]))
                if v is not None and np.isfinite(v):
                    ev.append(v)
            pd_ci_ep = ([float(np.percentile(ev, 2.5)), float(np.percentile(ev, 97.5))]
                        if len(ev) > 1 else [None, None])
            cellB[arena][str(h)] = {
                "unit_length": START + h, "n_independent_unit_level": int(n_units),
                "n_episodes": len(ARENAS_B[arena]), "n_forecast_steps": int(T),
                "r_disagreement": pc(disagree, err_s),
                "r_step_index": pc(fidx, err_s) if T > 1 else None,
                "r_step_size_free_baseline": pc(step, err_s) if T > 1 else None,
                "paired_diff_disagreement_minus_index": paired(np.arange(n_units)),
                "paired_diff_ci_unit_level": pd_ci,
                "paired_diff_excludes_zero": excl0(pd_ci),
                "footnote_episode_level": {"paired_diff_ci": pd_ci_ep,
                                           "excludes_zero": excl0(pd_ci_ep)},
                "note_h1": ("at h=1 there is one forecast step per unit, so the index is "
                            "constant and its correlation is undefined -- the same reason "
                            "the 400-step table leaves it blank" if T == 1 else None)}
    out["cells"]["B_section_6_7_ranking"] = cellB
    print("  cell B done")

    # ---------------- cell C: section 5's A/B gap ----------------------------------
    ab = {}
    for a in ("A", "B"):
        for s in SEEDS:
            m = M.build_from_config(cfg, ensemble_size=1)
            m.load_state_dict(torch.load(f"runs/arm{a}_seed{s}_10k/weights_10000.pt",
                                         map_location="cpu")["model_state_dict"], strict=True)
            m.eval(); ab[(a, s)] = m
    cellC = {}
    for arena in ARENAS:
        cellC[arena] = {}
        for h in HS:
            st, ue = index[(arena, h)]
            per = {}
            for k, m in ab.items():
                _e, _g, _gi, p, t = unit_rollout(m, data, cfg, st, h, False)
                per[k] = rel_l1(p, t)
            A = np.stack([per[("A", s)] for s in SEEDS]).mean(0)
            B = np.stack([per[("B", s)] for s in SEEDS]).mean(0)
            gap = B - A                                    # positive favours Arm A
            gu, ge = boot_ci(gap, None, ue)
            _f1, _f2, _f3, pf, tf = unit_rollout(None, data, cfg, st, h, False, floor=True)
            floor = rel_l1(pf, tf)
            cellC[arena][str(h)] = {
                "unit_length": START + h, "n_independent_unit_level": int(len(st)),
                "n_episodes": len(ARENAS[arena]),
                "metric": "relative-L1 (the reference's own, model_training.py:203)",
                "A_mean": float(A.mean()), "B_mean": float(B.mean()),
                "ratio_B_over_A": float(B.mean() / A.mean()),
                "gap": float(gap.mean()), "gap_ci_unit_level": gu,
                "gap_excludes_zero": excl0(gu),
                "hold_last_floor": float(floor.mean()),
                "footnote_episode_level": {"gap_ci": ge, "excludes_zero": excl0(ge)}}
    out["cells"]["C_section_5_ab_gap"] = cellC
    print("  cell C done")

    # ---------------- verdict, over all five committed horizons -------------
    ab400 = json.load(open(os.path.join(R.RESULTS, "a1_ab_by_horizon.json")))
    d20 = json.load(open(os.path.join(R.RESULTS, "task_d_nind20.json")))
    moves = []
    for h in HS:
        was = bool(ab400["by_horizon"][str(h)]["gap_excludes_zero"])
        now = cellC["out-of-sample held-out pair"][str(h)]["gap_excludes_zero"]
        if now is not None and now != was:
            moves.append({"cell": "C section 5 A/B gap",
                          "arena": "out-of-sample (matched to a1_ab_by_horizon.json)",
                          "h": h,
                          "excluded_zero_at_400_step": was,
                          "excludes_zero_at_short_unit": now})
        w2 = d20["d2_forecast_index"][str(h)]
        if w2.get("paired_ci_lo") is not None:
            was2 = bool(w2["paired_ci_lo"] > 0 or w2["paired_ci_hi"] < 0)
            # arena-matched: task_d_nind20.json is the all-ten arena, so the short-unit
            # side must be all-ten as well.
            now2 = cellB["all ten episodes"][str(h)]["paired_diff_excludes_zero"]
            if now2 is not None and now2 != was2:
                moves.append({"cell": "B section 6.7 paired difference",
                              "arena": "all ten episodes (matched to task_d_nind20.json)",
                              "h": h, "excluded_zero_at_400_step": was2,
                              "excludes_zero_at_short_unit": now2})
    out["verdict"] = {
        "discharged_over": list(HS),
        "note_on_printing": ("the rule is discharged over all five committed horizons. "
                             "Which cells the PAPER prints is a separate question -- "
                             "h = 1, 8 and 100 carry the argument, h = 32 and 128 are "
                             "landmarks that live here in the artifact. The distinction "
                             "between the set a rule is discharged over and the cells "
                             "printed is stated once in the body so it does not read as "
                             "selective reporting."),
        "n_verdicts_moved": len(moves), "moved": moves,
        "result": "MOVES" if moves else "NO MOVE",
        "reading": ("NO MOVE: the extra units narrow intervals without changing any "
                    "verdict, and both units are reported side by side."
                    if not moves else
                    "MOVES: both units are reported, each naming its unit, arena and "
                    "n_independent, and the affected claim is narrowed in the body."),
    }
    op = os.path.join(R.RESULTS, "m64_short_units.json")
    json.dump(out, open(op, "w"), indent=2)
    print(f"  VERDICT: {out['verdict']['result']} ({len(moves)} moved)")
    print(f"  wrote {R.rel(op)}")


if __name__ == "__main__":
    main()
