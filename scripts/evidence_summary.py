"""3.2 -- the evidence summary table. NO NEW MEASUREMENT.

One row per headline claim, so a reader can hold the three evaluation arenas in
their head before meeting any of them. Every cell is READ from an artifact under
`results/` or derived from one by a rule stated here; nothing is typed.

WHY THE ARENA COLUMN NEEDS A DERIVATION AND NOT A LABEL. Four of the artifacts
below record their arena as a sentence ("out-of-sample held-out pair", "released
checkpoint, all ten episodes"), three record it as an episode list, and two
record neither. Typing a label for those two would be exactly the failure this
project has caught four times. So the arena is resolved three ways, in this
order, and every route ends at the same registry:

  by episode list   the arena's episodes, matched against the split
  by arena sentence the phrase the artifact itself stored
  by n_independent  the registry's counts are distinct, so the count identifies
                    the arena on its own

THE REGISTRY is built from `results/insample_framing.json` (which holds our
split and what the released checkpoint trained on) and
`results/review_bootstrap_unit.json` (which holds the independent-trajectory
count each arena carries at the 400-step unit).

IN-SAMPLE FOR THE MODEL MEASURED is not a property of the arena. The released
checkpoint trained on all ten episodes, so *every* arena is in-sample for it,
including the one our split calls out-of-sample. Our own arms trained on eight,
so the held-out pair is out-of-sample for them and nothing else is. The column
is therefore computed as: does the arena's episode set intersect the set the
measured model trained on. Which model each row measures is read from the
artifact that records it -- a checkpoint path in the design block, or the report
header the run printed.

MULTIPLICITY is answered by one rule, applied to whatever each row's artifact
records:

  yes / no             the claim's cell is a member of a recorded family and
                       Holm-Bonferroni does or does not reject it
  could not at this n  the artifact records a minimum detectable effect and the
                       measured effect is below it
  not applicable       the claim is not a member of any recorded family

Writes results/evidence_summary.json.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402

OUT = "evidence_summary.json"

_cache = {}


def J(name):
    if name not in _cache:
        _cache[name] = json.load(open(os.path.join(R.RESULTS, name)))
    return _cache[name]


def T(name):
    return open(os.path.join(R.RESULTS, name)).read()


# ------------------------------------------------------------- arena registry
# Surface forms are how a SECTION of the paper writes an arena; the registry key
# is how this table writes it. Both are needed: the arena_consistency build check
# compares the two.
LABEL_FORMS = {
    "out-of-sample": ("out-of-sample", "held-out", "held out", "holdout"),
    "in-sample": ("in-sample",),
    "all ten episodes": ("all ten", "all 10 episodes", "ten episodes"),
}


def registry():
    IF = J("insample_framing.json")
    BU = J("review_bootstrap_unit.json")

    def bu_nind(prefix):
        return next(v["n_independent_reported"] for k, v in BU.items()
                    if k != "_summary" and k.startswith(prefix))

    return {
        "out-of-sample": {"episodes": sorted(IF["our_holdout_episodes"]),
                          "n_independent": bu_nind("out-of-sample|400")},
        "in-sample": {"episodes": sorted(IF["our_train_episodes"]),
                      "n_independent": bu_nind("in-sample|400")},
        "all ten episodes": {"episodes": sorted(IF["released_ckpt_trained_on_episodes"]),
                             "n_independent": IF["n_independent"]},
    }


ARENA = registry()


def arena_of_episodes(eps):
    eps = sorted(int(x) for x in eps)
    hit = [k for k, v in ARENA.items() if v["episodes"] == eps]
    assert len(hit) == 1, f"episode set {eps} matches {hit}"
    return hit[0]


def arena_of_text(s):
    low = s.lower()
    hit = [k for k, forms in LABEL_FORMS.items() if any(f in low for f in forms)]
    assert len(hit) == 1, f"arena sentence {s!r} matches {hit}"
    return hit[0]


def arena_of_nind(n):
    hit = [k for k, v in ARENA.items() if v["n_independent"] == n]
    assert len(hit) == 1, f"n_independent {n} matches {hit}"
    return hit[0]


# --------------------------------------------------------------- model column
def measured_model(evidence):
    """'released checkpoint' or 'our arms', from the text the artifact stored."""
    ckpt = os.path.basename(J("insample_framing.json")["released_checkpoint"])
    low = evidence.lower()
    if ckpt.lower() in low or "released checkpoint" in low or "reference checkpoint" in low:
        return "released checkpoint"
    return "our arms"


def trained_on(model):
    IF = J("insample_framing.json")
    return (sorted(IF["released_ckpt_trained_on_episodes"]) if model == "released checkpoint"
            else sorted(IF["our_train_episodes"]))


def in_sample(model, arena):
    return "yes" if set(ARENA[arena]["episodes"]) & set(trained_on(model)) else "no"


# --------------------------------------------------------- verdict/multiplicity
def gap_verdict(gap, excludes_zero):
    if not excludes_zero:
        return "gap spans zero"
    return ("gap excludes zero, favouring "
            + ("autoregressive training" if gap > 0 else "teacher forcing"))


def ratio_verdict(ci):
    return ("overconfident; the ratio interval excludes 1" if ci[0] > 1
            else "not resolved; the ratio interval spans 1")


def multiplicity(family_rejected=None, mde_met=None):
    if family_rejected is not None:
        return "yes" if family_rejected else "no"
    if mde_met is False:
        return "could not at this n"
    return "not applicable"


# ---------------------------------------------------------------------- rows
def build_rows():
    A1 = J("a1_ab_by_horizon.json")
    M64 = J("m64_short_units.json")
    D20 = J("task_d_nind20.json")
    E7 = J("e7_free_baselines.json")
    A2 = J("a2_trajectory_level_control.json")
    R2 = J("r2_independent_ensemble.json")
    M49 = J("m49_capacity_matched.json")
    D3 = J("task_d3_perhorizon.json")
    S4 = J("step4_0a_results.json")
    C3 = J("task_c3_multiplicity.json")
    V2 = J("v2_deployment_horizon.json")

    # The three horizons this table names are read, not typed: the upstream's
    # open-loop diagnostic length, the method's own imagination rollout length,
    # and the shortest horizon on the evaluation grid.
    diag = V2["horizons"]["open_loop_diagnostic"]["value"]
    deploy = V2["verdict"]["deployment_horizon_is"]
    one = min(A1["design"]["horizons"])

    rows = []

    # --- 1, 2: the A/B training claim, at the two horizons that disagree ------
    a1_arena = arena_of_text(A1["design"]["arena"])
    a1_model = measured_model(A1["design"]["checkpoint"])
    ab_family = (C3["holm_bonferroni"]["n_rejected"] == C3["family_ab"]["n_long_horizon"])
    g368 = A1["by_horizon"][str(diag)]
    rows.append({
        "claim": (f'Autoregressive training beats teacher forcing at '
                  f'h = {g368["horizon"]}'),
        "section": "5",
        "arena": a1_arena,
        "n_independent": g368["n_independent"],
        "in_sample": in_sample(a1_model, a1_arena),
        "verdict": gap_verdict(g368["gap"], g368["gap_excludes_zero"]),
        # Round 2, T10 review: the multiplicity family was corrected at the 500- and 2,500-iteration
        # checkpoints (results/task_c3_multiplicity.json), not at this row's 10,000.
        "multiplicity": (multiplicity(family_rejected=ab_family) + ", at the "
                         + " and ".join(f"{int(c):,}" for c in sorted({x["cell"].split("|")[2]
                                        for x in C3["holm_bonferroni"]["steps"]}, key=int))
                         + "-iteration checkpoints"),
        "model": a1_model,
        "artifacts": ["results/a1_ab_by_horizon.json", "results/task_c3_multiplicity.json"],
    })

    # M-64's own arena_matching line records that this cell is the short-unit
    # rebuild of a1_ab_by_horizon.json's row, so it measures the same arms.
    m64c = M64["cells"]["C_section_5_ab_gap"]
    m64_arena_key = next(iter(m64c))
    m64h1 = m64c[m64_arena_key][str(one)]
    rows.append({
        "claim": f"The same comparison reverses at h = {one}, at the short unit M-64 built",
        "section": "5",
        "arena": arena_of_text(m64_arena_key),
        "n_independent": m64h1["n_independent_unit_level"],
        "in_sample": in_sample(a1_model, arena_of_text(m64_arena_key)),
        "verdict": gap_verdict(m64h1["gap"], m64h1["gap_excludes_zero"]),
        "multiplicity": multiplicity(),
        "model": a1_model,
        "artifacts": ["results/m64_short_units.json"],
        # M-64's arena_matching line: this cell is the short-unit rebuild of
        # a1_ab_by_horizon.json's row, so its checkpoint is that artifact's.
        "checkpoint_from": ["results/a1_ab_by_horizon.json"],
    })

    # --- S9: the configuration and architecture claims (rules M-74, M-75, M-76) --
    # Each rule applies Holm within its own family, so its verdict is already corrected.
    MV, BV, ME = J("mn_sweep_verdict.json"), J("baselines_verdict.json"), J("mn_sweep_eval.json")
    mn_arena = arena_of_episodes(ME["arenas"]["held_out"]["episodes"])
    _better = MV["governing"]["conditions"]["configs_excluding_zero_in_their_favour"]
    rows.append({
        "claim": "(M, N) = (32, 8) is the optimal configuration on accuracy alone (the accuracy half of the trade-off)",
        "section": "5.2",
        "arena": mn_arena,
        "n_independent": ME["arenas"]["held_out"]["n_independent"],
        "in_sample": in_sample("our arms", mn_arena),
        # Round 2, T3 item 4(c): a returned verdict is printed verbatim, in the case the rule returned it.
        "verdict": (MV["verdict"] + f"; {len(_better)} of {MV['governing']['m']} "
                    "neighbours beat the centre"),
        "multiplicity": "yes",
        "model": "our arms",
        "artifacts": ["results/mn_sweep_verdict.json", "results/mn_sweep_eval.json"],
    })
    # Round 2, T9: section 5.3 ends "the architecture claim rests on the MLP and the transformer",
    # because rule X1 found no read-out or retraining that rescues our RSSM. The rows carry that
    # qualifier only while X1's reading is the one that makes the RSSM uninformative.
    assert J("rssm_diagnostics.json")["final_reading"] == "NOT RESCUED BY THE SETTINGS TRIED"
    # Round 2, T10 (Annex 4 item 3): every statement of this verdict says the baselines were
    # trained with RWM's settings and that, at the rule's horizon, each is worse than predicting
    # no change. The second half is asserted as paper_numbers.py asserts it for section 5.3.
    import numpy as _np
    _BE = J("baselines_eval.json")
    _m3 = lambda cfg, h: float(_np.mean([_np.mean(cfg["seeds"][s]["held_out"][str(h)]["l1"])
                                         for s in cfg["seeds"]]))
    _fl = BV["hold_last_floor_l1"]["held_out"][str(diag)]
    assert all(_m3(_BE["configs"][f"{b}_{g}_s7"], diag) > _fl
               for b in BV["priority_order"] for g in ("tf", "ar"))
    for _rule, _how in (("M-75", "teacher-forced, as the original trains them"),
                        ("M-76", "trained autoregressively: architecture at one training regime, "
                                 "not the original's claim")):
        _R = BV["rules"][_rule]
        rows.append({
            "claim": f"RWM beats MLP, RSSM and transformer baselines trained with RWM's settings ({_how}; "
                     f"the RSSM comparison uninformative, rule X1)",
            "section": "5.3",
            "arena": mn_arena,
            "n_independent": ME["arenas"]["held_out"]["n_independent"],
            "in_sample": in_sample("our arms", mn_arena),
            "verdict": f"{_R['verdict']}; at h = {diag} every baseline is worse than predicting no change",
            "multiplicity": "yes",
            "model": "our arms",
            "artifacts": ["results/baselines_verdict.json", "results/baselines_eval.json"],
        })

    # --- 3, 4, 5: the calibration claims -------------------------------------
    d20_arena = arena_of_text(D20["design"]["arena"])
    d20_model = measured_model(D20["design"]["checkpoint"])
    for h, tag in ((one, "epistemic"), (deploy, "epistemic"), (one, "aleatoric")):
        cell = D20["d1_by_horizon"][str(h)][tag]
        claim = ("Ensemble disagreement is smaller than realised error"
                 if tag == "epistemic" else
                 "The aleatoric σ head has collapsed and is orders of magnitude "
                 "smaller than realised error")
        rows.append({
            "claim": f"{claim}, at h = {h}",
            "section": "6.2",
            "arena": d20_arena,
            "n_independent": D20["design"]["n_independent"],
            "in_sample": in_sample(d20_model, d20_arena),
            "verdict": ratio_verdict(cell["ratio_err_over_sigma_ci"]),
            "multiplicity": multiplicity(),
            "model": d20_model,
            "artifacts": ["results/task_d_nind20.json"],
        })

    # --- 6: the ranking claim against the forecast step index ----------------
    idx = D20["d2_forecast_index"][str(deploy)]
    rows.append({
        "claim": (f'Disagreement ranks realised error better than the forecast '
                  f'step index, at h = {idx["horizon"]}'),
        "section": "6.6",
        "arena": d20_arena,
        "n_independent": idx["n_independent"],
        "in_sample": in_sample(d20_model, d20_arena),
        "verdict": ("paired difference excludes zero" if idx["paired_ci_lo"] > 0
                    else "paired difference spans zero"),
        "multiplicity": multiplicity(),
        "model": d20_model,
        "artifacts": ["results/task_d_nind20.json"],
    })

    # --- 7: the ranking claim against predicted step size --------------------
    step = next(b for b in E7["baselines"] if b["baseline"] == "step-size")
    e7_arena = arena_of_nind(E7["design"]["n_independent"])
    e7_model = measured_model(T("e7_free_baselines_report.txt"))
    rows.append({
        "claim": "Disagreement ranks realised error better than the model's own predicted step size",
        "section": "6.6",
        "arena": e7_arena,
        "n_independent": E7["design"]["n_independent"],
        "in_sample": in_sample(e7_model, e7_arena),
        # Round 3, R4 (S2): the label glossed where it first appears outside section 6.6 and Appendices E and K
        "verdict": (f"{E7['verdict']} (disagreement beats the one-step error before the window, but not the "
                    f"model's predicted step size): step size not beaten, the margin below the minimum detectable "
                    f"effect; the partial survives"
                    if step["partial_beats_mde"] and not step["margin_beats_mde"]
                    else "beats it on both the margin and the partial"
                    if step["margin_beats_mde"] and step["partial_beats_mde"]
                    else "not separated from the baseline"),
        "multiplicity": multiplicity(mde_met=step["margin_beats_mde"]),
        "model": e7_model,
        "artifacts": ["results/e7_free_baselines.json"],
    })

    # --- 8: the double-demeaned control --------------------------------------
    a2_arena = arena_of_text(A2["design"]["arena"])
    a2_model = measured_model(A2["design"]["arena"])
    rows.append({
        "claim": ("With both the rollout and the depth held constant, disagreement "
                  "still tracks error"),
        "section": "6.6",
        "arena": a2_arena,
        "n_independent": A2["design"]["n_independent"],
        "in_sample": in_sample(a2_model, a2_arena),
        # Derived from M-45's own booleans rather than quoting its verdict
        # sentence: the sentence is set in capitals, and a capitalised token
        # overruns the p{} column this table is typeset in.
        "verdict": ("interval excludes zero and clears the minimum detectable effect"
                    if A2["m45"]["excludes_zero"] and A2["m45"]["above_mde"]
                    else "interval spans zero" if not A2["m45"]["excludes_zero"]
                    else "interval excludes zero, below the minimum detectable effect"),
        "multiplicity": multiplicity(mde_met=A2["m45"]["above_mde"]),
        "model": a2_model,
        "artifacts": ["results/a2_trajectory_level_control.json"],
    })

    # --- 9: the per-horizon multiplier --------------------------------------
    d3_arena = arena_of_episodes(D3["holdout_episodes"])
    d3_model = measured_model(T("task_d3_perhorizon_report.txt"))
    d3v = D3["quantities"]["epistemic"]["verdict"]
    d3x_own = J("task_d3_cross_model.json")["armA_own_model"]["epistemic"]
    # p4 scored this model under these same multipliers: is the tolerance band
    # resolvable at any quantity x horizon pair of this arena?
    d3_res = [v for q in J("p4_transfer_power.json")["tolerance_resolvable"].values()
              for v in q.values()]
    rows.append({
        "claim": "A per-horizon multiplier brings coverage near nominal where a constant one does not",
        "section": "6.7",
        "arena": d3_arena,
        "n_independent": sum(D3["design"]["trajectories_per_episode"].values()),
        "in_sample": in_sample(d3_model, d3_arena),
        # S4: the released checkpoint trained on both held-out episodes, so its cells are
        # unseen by the multiplier only; Arm A's own multipliers are the same test on a model
        # that never saw them (results/task_d3_cross_model.json).
        "verdict": (("every released-checkpoint point estimate unseen by the multiplier within tolerance"
                     if d3v["per_horizon_restores_calibration"]
                     else "not every released-checkpoint point estimate unseen by the multiplier within tolerance")
                    + f"; on Arm A at {J('task_d3_cross_model.json')['design']['iterations']:,} iterations, "
                      f"unseen by its model too, {d3x_own['cells_within_tolerance']}"
                      f" of {d3x_own['n_cells']} epistemic cells"
                    + ("" if all(d3_res) else "; tolerance not resolvable at this arena")),
        "multiplicity": multiplicity(mde_met=all(d3_res)),
        "model": d3_model,
        "artifacts": ["results/task_d3_perhorizon.json", "results/p4_transfer_power.json",
                      "results/task_d3_cross_model.json"],
    })

    # --- 10, 11: the two ensemble-topology contrasts --------------------------
    for art, name, claim in (
            (R2, "r2_independent_ensemble", "An ensemble that shares no trunk is "
             "better calibrated than the released topology"),
            (M49, "m49_capacity_matched", "The same contrast at matched capacity")):
        arena = arena_of_text(art["design"]["arena"])
        model = measured_model(T(f"{name}_report.txt"))
        cond = art["m44"]["conditions"]
        mde_keys = [k for k in cond if k.endswith("_mde")]
        rows.append({
            "claim": claim,
            # the matched-capacity result is reported in §11, not §6.10 (S10)
            "section": "6.8" if name == "r2_independent_ensemble" else "11",
            "arena": arena,
            "n_independent": art["design"]["n_independent"],
            "in_sample": in_sample(model, arena),
            "verdict": art["m44"]["verdict"],
            "multiplicity": multiplicity(mde_met=all(cond[k] for k in mde_keys)),
            "model": model,
            "artifacts": [f"results/{name}.json"],
        })

    # --- 11a: the combined arm. Its own rule, its own conditions, its own
    # section. It is not folded into the loop above because M-68's condition set
    # is not M-44's and reading it out of the m44 block would report the wrong
    # rule's conditions beside the right rule's verdict.
    C68 = J("r2_combined_arm.json")
    _c68 = C68["m68"]
    _c68arena = arena_of_text(C68["design"]["arena"])
    _c68cond = _c68["conditions"]
    _c68mde = [k for k in _c68cond if k.endswith("_mde")]
    rows.append({
        "claim": "Independence and the corrected objective together improve on the "
                 "released topology",
        "section": "6.8",
        "arena": _c68arena,
        "n_independent": C68["design"]["n_independent"],
        "in_sample": in_sample(measured_model(T("r2_combined_arm_report.txt")), _c68arena),
        "verdict": _c68["verdict"],
        "multiplicity": multiplicity(mde_met=all(_c68cond[k] for k in _c68mde)),
        "model": measured_model(T("r2_combined_arm_report.txt")),
        "artifacts": ["results/r2_combined_arm.json"],
    })

    # --- 12: the action-alignment defect -------------------------------------
    # Round 3, R3 (Annex 2 E2): described over all ten episodes, the larger arena and this checkpoint's own
    # training data; the held-out pair is not more honest here, only smaller.
    s4_arena = arena_of_episodes(range(10))
    s4_model = measured_model(T("step3_report.txt"))
    stale = S4["protocols"]["A_off0"]["nrmse"][str(diag)]
    causal = S4["protocols"]["A_off1"]["nrmse"][str(diag)]
    # Round 2, T3 item 4(b), ruling A (DECISIONS.md#T3-alignment-framing): the cost by horizon (N1, R-76).
    # Concentrated at short horizons if the held-out pair's largest relative-L1 overstatement lies at
    # h < diag and exceeds the h = diag one; not consistent in sign at h = diag if the held-out pair and
    # all ten episodes disagree in sign there.
    # Round 3, R3: the verdict reads the all-ten-episodes curve on relative-L1. The rise must run unbroken from
    # h = 1 to the last horizon whose interval excludes zero, and no later horizon may be resolved either way.
    AH = J("alignment_by_horizon.json")["released"]["summary"]
    _t20 = {int(h): v["rel_l1"]["ci95_pct"] for h, v in AH["all_ten_n20"].items()}
    _hs = sorted(_t20)
    _rise = [h for h in _hs if _t20[h][0] > 0]
    assert _rise and _rise == _hs[:len(_rise)], f"the rise is not unbroken from h = {_hs[0]}: {_rise}"
    _upto = _rise[-1]
    assert all(_t20[h][0] <= 0 <= _t20[h][1] for h in _hs[len(_rise):]), "a later horizon is resolved"
    _cost = (f"raises error up to h = {_upto} on relative-L1; not resolved from h = {_hs[len(_rise)]}"
             if len(_rise) < len(_hs) else "raises error at every horizon on relative-L1")
    rows.append({
        "claim": "The released evaluation pairs states and actions one step stale",
        "section": "7.2",
        "arena": s4_arena,
        "n_independent": ARENA[s4_arena]["n_independent"],
        "in_sample": in_sample(s4_model, s4_arena),
        "verdict": (("defect confirmed in the code; " + _cost) if stale > causal
                    else "not confirmed; the released pairing does not score worse"),
        "multiplicity": multiplicity(),
        "model": s4_model,
        "artifacts": ["results/step4_0a_results.json", "results/alignment_by_horizon.json"],
    })
    return rows


def checkpoint_of(row):
    """The checkpoint a row is measured at, read from its artifacts (S10, user ruling D2).

    "released" for the released checkpoint; otherwise the training iterations the row's own
    artifact records, from design.iterations, a top-level checkpoint_iterations, or a
    design.checkpoint of the form weights_<N>.pt. A row with none of these fails loudly
    rather than printing a blank, which would read as "no checkpoint".
    """
    if row["model"] == "released checkpoint":
        return "released"
    for a in row.get("checkpoint_from", []) + row["artifacts"]:
        d = J(os.path.basename(a))
        ds = d.get("design") or {}
        it = ds.get("iterations") or d.get("checkpoint_iterations")
        if not it and isinstance(ds.get("checkpoint"), str):
            m = re.search(r"weights_(\d+)\.pt", ds["checkpoint"])
            it = int(m.group(1)) if m else None
        if it:
            return f"{int(it):,} iterations"
    raise AssertionError(f"no checkpoint recorded for: {row['claim']}")


def arena_label(row):
    """Round 2, T3 item 4(a): the held-out pair is out-of-sample for our arms only. The released
    checkpoint trained on it, so its rows there name the arena, "held-out pair", and the in-sample
    column already says yes. The registry key (row["arena"]) is unchanged."""
    if row["model"] == "released checkpoint" and row["arena"] == "out-of-sample":
        return "held-out pair"
    return row["arena"]


def markdown(rows):
    # Six columns carrying eight fields. With the checkpoint column (S10, D2) eight
    # columns' unbreakable words no longer fit the line and the PDF gate failed on
    # overfull boxes, so the section rides with the claim and n_independent with its arena.
    return "\n".join(
        f'| {r["claim"]} (§{r["section"]}) | {arena_label(r)} ({r["n_independent"]}) | '
        f'{r["checkpoint"]} | {r["in_sample"]} | {r["verdict"]} | {r["multiplicity"]} |'
        for r in rows)


def main():
    rows = build_rows()
    for r in rows:
        r["checkpoint"] = checkpoint_of(r)
    out = {
        "what": "one row per headline claim, for section 3.2",
        "computation": "none; every cell is read from an artifact or derived from one",
        "arena_registry": ARENA,
        "arena_surface_forms": {k: list(v) for k, v in LABEL_FORMS.items()},
        "n_rows": len(rows),
        "rows": rows,
        "table_markdown": markdown(rows),
    }

    print("=" * 96)
    print("3.2 — EVIDENCE SUMMARY TABLE (no new measurement)")
    print("=" * 96)
    for k, v in ARENA.items():
        print(f"  arena {k:<18s} episodes {v['episodes']}  n_independent {v['n_independent']}")
    print()
    print(f"  {'section':<8s} {'arena':<18s} {'n_ind':>5s}  {'in-sample':<9s} claim")
    for r in rows:
        print(f"  {r['section']:<8s} {r['arena']:<18s} {r['n_independent']:>5d}  "
              f"{r['in_sample']:<9s} {r['claim'][:52]}")
    print(f"\n  {len(rows)} rows")

    op = os.path.join(R.RESULTS, OUT)
    json.dump(out, open(op, "w"), indent=2)
    print(f"  wrote {R.rel(op)}")


if __name__ == "__main__":
    main()
