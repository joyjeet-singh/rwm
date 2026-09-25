"""
Q3 / M-70 -- does the per-horizon correction reorder cumulative penalties?

WHAT THIS DISCHARGES. `M-70`, pre-registered in commit 6b87e325d6f24640925d6d69447755a8341b2fa7
before any part of this statistic existed. This script implements that rule and nothing else. It
chooses nothing: every threshold, every convention and every branch below is read off the
committed rule text, and where the rule and a convenient alternative differ, the rule wins.

WHY THE STATISTIC IS WHAT IT IS. The penalty is `r~ = r - lambda*u`, and §6.8's repair is one
positive scalar `c(h)` per forecast horizon. WITHIN a horizon, multiplying every `u` by a
positive constant cannot change any ranking -- it is a monotone transform -- so a proxy comparing
states at the same rollout depth finds nothing BY CONSTRUCTION, and a null there would mean the
measurement was ill-posed rather than that the correction is harmless. What the correction changes
is the relative weight ACROSS depths, so the statistic is the penalty accumulated ALONG a rollout.

    P_raw(i)  = sum_{t=1..368} u_i(t)
    P_corr(i) = sum_{t=1..368} c_out(i)(band(t)) * u_i(t)

A pair {i, j} REORDERS when sign(P_raw(i) - P_raw(j)) != sign(P_corr(i) - P_corr(j)), and
f = (reordering pairs) / (defined pairs) over the C(4, 2) = 6 pairs of the held-out arena.

THE ONE THING THIS SCRIPT RECOMPUTES, AND THE PERMISSION THAT ALLOWS IT. `u` is not stored
anywhere: §6.8's own script computes it and discards it (`pred, alea, epi, _, _` at
scripts/task_d3_perhorizon.py:54). `M-70` therefore carries a permission, ruled by the user on
2026-09-20, for ONE deterministic re-derivation through the same entry point -- the released
checkpoint, `start_step = 32`, `action_offset = 1`, batched one call per held-out episode exactly
as §6.8 batches it. That is the whole of the permission and this script stays inside it: it
trains nothing, fits nothing, and introduces no data, seed, arena or model the paper does not
already have. `episode_rollout` below mirrors §6.8's function line for line; it differs only in
KEEPING the scalar epistemic output that §6.8 throws away.

    python scripts/q3_penalty_reordering.py

Reads results/task_d3_perhorizon.json and the released checkpoint.
Writes results/q3_penalty_reordering.json and results/q3_penalty_reordering_report.txt.
"""
import json
import os
import sys
from itertools import combinations, product

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import torch  # noqa: E402
import rwm_data as R  # noqa: E402
import rollout_eval as E  # noqa: E402
import rwm_metrics as MET  # noqa: E402
import score_reference as S  # noqa: E402

PREREG = "6b87e325d6f24640925d6d69447755a8341b2fa7"
HORIZONS = (1, 8, 32, 100, 128, 368)
START, LEN = E.START_STEP, 400
N_STEPS = 368                      # t = 1 .. 368, absolute index START + t - 1
ACTION_OFFSET = 1                  # M-70's permission; the value §6.8 uses
N_BOOT = 4000
BOOT_SEED = 20260920
# M-70's design table, quoted verbatim from the committed rule (6b87e32): the exact binomial 95%
# interval for k of 6 pairs reordering. A quotation of the rule, not a figure derived here.
M70_TABLE = {0: (0.0000, 0.4593), 1: (0.0042, 0.6412), 2: (0.0433, 0.7772),
             3: (0.1181, 0.8819), 4: (0.2228, 0.9567), 5: (0.3588, 0.9958),
             6: (0.5407, 1.0000)}


def bands():
    """The partition of steps M-70 pins: band(1)={1}, band(8)={2..8}, ... band(368)={129..368}.

    Returned as an array `b` with b[t-1] = the horizon labelling the band containing step t.
    """
    b = np.empty(N_STEPS, dtype=int)
    lo = 1
    for h in HORIZONS:
        b[lo - 1:h] = h
        lo = h + 1
    assert lo - 1 == N_STEPS
    # every step in exactly one band, and the bands are window(h) minus window(previous)
    assert set(np.unique(b)) == set(HORIZONS)
    assert (np.bincount(b, minlength=369)[list(HORIZONS)] ==
            np.diff((0,) + HORIZONS)).all()
    return b


def episode_rollout(episode, paths, cfg, data, ep):
    """§6.8's episode_rollout (scripts/task_d3_perhorizon.py:43-56), one call per episode,
    differing only in that it KEEPS epi_s -- the scalar epistemic term M-70 pins as `u`."""
    starts = MET.non_overlapping_starts(ep, [episode], LEN)
    idx = np.asarray(starts)[:, None] + np.arange(LEN)[None, :]
    raw = data[idx]
    st = torch.as_tensor(R.normalise_state(raw[:, :, R.STATE_COLS],
                                           cfg["state_data_mean"], cfg["state_data_std"]),
                         dtype=torch.float32)
    ac = torch.as_tensor(raw[:, :, R.ACTION_COLS], dtype=torch.float32)
    sd = torch.load(paths["ckpt"], map_location="cpu")["system_dynamics_state_dict"]
    m = S.ReferenceRWM(sd); m.eval()
    _pred, _alea, _epi, _alea_s, epi_s = m.rollout_uncertainty(
        st.clone(), ac, START, action_offset=ACTION_OFFSET)
    return epi_s.numpy().astype(np.float64), len(starts)


def reorders(pr_i, pr_j, pc_i, pc_j):
    """M-70's reorder test with its tie convention.

    Returns True, False, or a reason string when the pair is undefined. M-70 requires a
    non-finite value's "occurrence is reported rather than silently absorbed", so the two
    routes to undefined are distinguished rather than pooled.
    """
    if not all(np.isfinite(v) for v in (pr_i, pr_j, pc_i, pc_j)):
        return "non-finite"                          # checked first; NaN == NaN is False anyway
    if pr_i == pr_j or pc_i == pc_j:
        return "exact-tie"                           # no ordering to change
    return np.sign(pr_i - pr_j) != np.sign(pc_i - pc_j)


def statistic(P_raw, P_corr, members):
    """f over the pairs of `members`. Returns (f, n_reorder, n_defined, n_tie, n_nonfinite)."""
    n_re = n_def = n_tie = n_nf = 0
    for a, b in combinations(range(len(members)), 2):
        i, j = members[a], members[b]
        if i == j:
            continue                                 # degenerate self-pair, excluded
        r = reorders(P_raw[i], P_raw[j], P_corr[i], P_corr[j])
        if r == "exact-tie":
            n_tie += 1
        elif r == "non-finite":
            n_nf += 1
        else:
            n_def += 1
            n_re += int(r)
    f = (n_re / n_def) if n_def else None
    return f, n_re, n_def, n_tie, n_nf


def main():
    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    data, ep = R.load_data(paths["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"),
                         verbose=False)
    HOLD = list(split["holdout_episodes"])

    D3 = json.load(open(os.path.join(R.RESULTS, "task_d3_perhorizon.json")))
    assert HOLD == D3["holdout_episodes"], "the arena is not §6.8's"
    assert D3["design"]["start_step"] == START and D3["design"]["traj_len"] == LEN
    fits = D3["quantities"]["epistemic"]["fits"]        # epistemic: u IS ensemble disagreement
    c_by_test = {}
    for cell in fits:
        c_by_test.setdefault(cell["test_episode"], {})[cell["h"]] = cell["c"]
    for e in HOLD:
        assert set(c_by_test[e]) == set(HORIZONS), f"episode {e} lacks a multiplier per horizon"

    b = bands()
    # one call per held-out episode, exactly as §6.8 batches it
    u, owner = [], []
    for e in HOLD:
        epi_s, n = episode_rollout(e, paths, cfg, data, ep)
        for k in range(n):
            u.append(epi_s[k, START:START + N_STEPS])
            owner.append(e)
    u = np.asarray(u)
    n_traj = len(owner)
    assert u.shape == (n_traj, N_STEPS), u.shape
    assert n_traj == 4, f"M-70's arena is 4 held-out trajectories, found {n_traj}"

    # c_out(i): the multipliers whose test_episode is i's own episode -- i.e. fitted on the OTHER
    w = np.asarray([[c_by_test[owner[i]][h] for h in b] for i in range(n_traj)])
    P_raw = u.sum(axis=1)
    P_corr = (w * u).sum(axis=1)

    f, n_re, n_def, n_tie, n_nf = statistic(P_raw, P_corr, list(range(n_traj)))
    n_undef = n_tie + n_nf

    # 95% cluster bootstrap over WHOLE TRAJECTORIES (M-27)
    rng = np.random.default_rng(BOOT_SEED)
    vals, drop_distinct, drop_undef = [], 0, 0
    while len(vals) < N_BOOT:
        members = list(rng.integers(0, n_traj, n_traj))
        if len(set(members)) < 2:
            drop_distinct += 1
            continue
        bf, _, bdef, _, _ = statistic(P_raw, P_corr, members)
        if bf is None:
            drop_undef += 1
            continue
        vals.append(bf)
    vals = np.asarray(vals)
    ci = [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))]

    # M-70's three branches, in its order. The first that matches is the verdict.
    if f == 1.0 and ci[0] > 0.5:
        verdict = "REORDERS"
    elif f == 0.0 and ci[1] < 0.5:
        verdict = "DOES NOT REORDER"
    else:
        verdict = "UNDERPOWERED"
    if n_undef > 2:
        verdict = "UNDERPOWERED"                      # by construction, whatever the rest shows

    c_ratio = D3["quantities"]["epistemic"]["verdict"]["c_ratio_max_over_min"]

    # EXHAUSTIVE enumeration of the bootstrap's whole sample space, computed rather than
    # asserted. M-70 makes both directional branches conditional on where the interval lies;
    # this establishes whether either condition is capable of failing.
    seen, ex_drop, ex_ok = set(), 0, 0
    for members in product(range(n_traj), repeat=n_traj):
        if len(set(members)) < 2:
            ex_drop += 1
            continue
        bf, _, bdef, _, _ = statistic(P_raw, P_corr, list(members))
        if bf is None:
            ex_drop += 1
            continue
        ex_ok += 1
        seen.add(bf)
    attainable = sorted(seen)
    # A branch's interval condition is VACUOUS when no attainable resample can violate it:
    # then it can never fail, and consulting it adds nothing to the branch's point test.
    # Symmetric by design -- branch 1 on the f = 1 side, branch 2 on the f = 0 side -- because
    # a resample [i, j, i, j] contains only the pair {i, j}, so the attainable set is {0}, {1},
    # or contains both, and only the first two make a condition vacuous.
    vacuous = []
    if all(v > 0.5 for v in attainable):
        vacuous.append("branch 1's interval condition (entirely above 1/2) can never fail")
    if all(v < 0.5 for v in attainable):
        vacuous.append("branch 2's interval condition (entirely below 1/2) can never fail")
    assert len(attainable) >= 1
    pred = M70_TABLE.get(n_re) if n_def == 6 else None
    narrower = (pred is not None) and ((ci[1] - ci[0]) < (pred[1] - pred[0]))

    # DIAGNOSTIC, not a branch condition and it changes no verdict. A null here could be
    # structural in a second way the rule's c_ratio does not catch: band(368) holds 240 of the
    # 368 steps, so if the accumulated penalty is dominated by one band then both orderings are
    # essentially that band's ordering and nothing could have reordered. These shares say whether
    # that is what happened.
    share_raw, share_corr, tail_order_matches = {}, {}, None
    for h in HORIZONS:
        m = (b == h)
        share_raw[str(h)] = float(u[:, m].sum() / u.sum())
        share_corr[str(h)] = float((w * u)[:, m].sum() / (w * u).sum())
    dom = max(share_corr, key=share_corr.get)
    mdom = (b == int(dom))
    tail_order_matches = bool(
        (np.argsort((w * u)[:, mdom].sum(axis=1)) == np.argsort(P_corr)).all())

    rec = {
        "rule": "M-70",
        "pre_registered_in": PREREG,
        "verdict": verdict,
        "statistic": {
            "f": f, "n_reordering_pairs": n_re, "n_defined_pairs": n_def,
            "n_undefined_pairs": n_undef,
            "n_undefined_exact_tie": n_tie, "n_undefined_non_finite": n_nf, "n_pairs_total": n_traj * (n_traj - 1) // 2,
            "ci95_cluster_bootstrap_over_trajectories": ci,
        },
        "arena": {
            "held_out_episodes": HOLD, "n_independent": n_traj,
            "trajectories_per_episode": {str(e): owner.count(e) for e in HOLD},
            "horizons": list(HORIZONS), "steps_per_trajectory": N_STEPS,
            "start_step": START, "traj_len": LEN,
            "bootstrap_unit": "whole trajectory",
            "n_boot": N_BOOT, "seed": BOOT_SEED,
            "resamples_discarded_fewer_than_two_distinct": drop_distinct,
            "resamples_discarded_all_pairs_undefined": drop_undef,
        },
        "per_trajectory": [
            {"episode": owner[i], "P_raw": float(P_raw[i]), "P_corr": float(P_corr[i]),
             "c_out_from_fold": "fitted on the other held-out episode"}
            for i in range(n_traj)
        ],
        "is_the_null_structural": {
            "what": "Diagnostic only. Changes no branch and no verdict. It asks whether one "
                    "horizon band so dominates the accumulated penalty that both orderings are "
                    "just that band's ordering, in which case no reordering could have occurred "
                    "for a reason having nothing to do with the correction.",
            "steps_per_band": {str(h): int((b == h).sum()) for h in HORIZONS},
            "share_of_raw_penalty_by_band": share_raw,
            "share_of_corrected_penalty_by_band": share_corr,
            "dominant_band_after_correction": int(dom),
            "dominant_band_share": share_corr[dom],
            "ordering_equals_dominant_band_ordering": tail_order_matches,
        },
        "spread_of_the_correction": {
            "c_ratio_max_over_min": c_ratio,
            "why_reported": "M-70 requires it beside the verdict. If the six multipliers barely "
                            "differed across bands the DOES NOT REORDER branch would be close to "
                            "forced and its licence would read as a finding when it was really a "
                            "property of the correction being nearly flat. This figure says "
                            "whether the design could have produced anything else.",
        },
        "the_interval_is_degenerate_by_construction": {
            "what": "A defect in M-70, not in this discharge, recorded because the rule's text is "
                    "frozen and cannot be corrected in place. Every pair formed from a resample is "
                    "one of the original six pairs, so if none of the six reorders then no "
                    "resample can yield a non-zero f. The attainable set of f under this "
                    "bootstrap is reported in attainable_set_of_f below, enumerated by this "
                    "script over the bootstrap's ENTIRE sample space rather than asserted: the "
                    "counts in exhaustive_check and the vacuous conditions in "
                    "branch_conditions_that_cannot_fail are all computed from that enumeration.",
            "consequence": ("The interval condition in branches 1 and 2 CANNOT FAIL when f is 0 "
                            "or 1, which is the only time it is consulted, so it is vacuous: "
                            "branch 2 reduces to 'f = 0' alone and branch 1 to 'f = 1' alone. "
                            f"The verdict returned, {verdict}, is unaffected, but the interval "
                            "must not be read as independent corroboration of it."),
            "comparison_with_the_rule_prediction": {
                "m70_table_row_quoted": ({"pairs_reordering": n_re, "of": 6,
                                          "interval": list(pred)} if pred else None),
                "bootstrap_interval_returned": ci,
                "narrower_than_predicted": narrower,
                "note": ("M-70 says the true interval would be WIDER than its binomial table, "
                         "because the six pairs rest on four units. narrower_than_predicted "
                         "records whether the bootstrap it mandates came back narrower instead; "
                         "a narrower interval shown to a referee without a note reads as a "
                         "precision this design cannot deliver."),
            },
            "attainable_set_of_f": attainable,
            "exhaustive_check": {"resamples": n_traj ** n_traj,
                                 "discarded": ex_drop, "admissible": ex_ok},
            "branch_conditions_that_cannot_fail": vacuous,
            "recorded_as": "ledger entry M-71",
        },
        "the_bound": (
            "M-70's bound, binding every branch equally. No reward function is available in this "
            "work. sum_t u(t) is the PENALTY COMPONENT ALONE, not the penalised return "
            "r~ = r - lambda*u. Whether a changed ordering of the penalty component changes the "
            "ordering of the return depends on the scale of r relative to lambda*u, and this "
            "project has neither r nor a tuned lambda. This verdict is therefore a BOUND on what "
            "the correction could do downstream, never a measurement of what it costs, and it "
            "licenses no statement about policy performance, learned behaviour, or the size of "
            "any downstream effect."),
        "what_was_recomputed": (
            "u only, under M-70's permission: one call to "
            "score_reference.ReferenceRWM.rollout_uncertainty per held-out episode, released "
            f"checkpoint, start_step {START}, action_offset {ACTION_OFFSET} -- the same "
            "entry point, "
            "checkpoint and "
            "CSV as scripts/task_d3_perhorizon.py, batched as it batches. Nothing was trained "
            "or fitted; the multipliers were read from results/task_d3_perhorizon.json."),
    }

    lines = []
    A = lines.append
    A("Q3 / M-70 — DOES THE PER-HORIZON CORRECTION REORDER CUMULATIVE PENALTIES?")
    A("=" * 88)
    A(f"  rule pre-registered in {PREREG}")
    A(f"  arena: held-out episodes {HOLD}, n_independent = {n_traj} whole {LEN}-step "
      "trajectories,")
    A(f"         {N_STEPS} forecast steps each, horizons {list(HORIZONS)}")
    A("")
    A(f"  {'episode':>8}  {'P_raw':>16}  {'P_corr':>16}")
    for i in range(n_traj):
        A(f"  {owner[i]:>8}  {P_raw[i]:>16.6f}  {P_corr[i]:>16.6f}")
    A("")
    A(f"  pairs: {n_def} defined, {n_undef} undefined, {n_re} reordering")
    A(f"  f = {f}")
    A(f"  95% cluster bootstrap over whole trajectories: [{ci[0]:.4f}, {ci[1]:.4f}]"
      f"   ({N_BOOT} resamples, {drop_distinct} discarded for <2 distinct,"
      f" {drop_undef} for all-undefined)")
    A("")
    A(f"  VERDICT: {verdict}")
    if vacuous:
        A("  NOTE: that interval is DEGENERATE BY CONSTRUCTION and is not corroboration. Every")
        A("  resampled pair is one of the original pairs, so the interval can only take values")
        A(f"  in {attainable}: exhaustively, all {ex_ok} admissible resamples of "
          f"{n_traj ** n_traj} ({ex_drop} discarded)")
        A("  return f in that set. Consequently:")
        for v in vacuous:
            A(f"    - {v}")
        A("  A defect in M-70, whose text is frozen; recorded as ledger entry M-71.")
    A(f"  spread of the correction, c_ratio_max_over_min = {c_ratio:.4f}")
    A("")
    A("  THE BOUND, binding this verdict as it binds every branch: this is the ordering of the")
    A("  penalty component alone, not of the penalised return. No reward function and no tuned")
    A("  lambda exist in this work, so the verdict bounds what the correction could do")
    A("  downstream and never measures what it costs. It licenses no statement about policy.")
    out = "\n".join(lines) + "\n"
    print(out, end="")

    json.dump(rec, open(os.path.join(R.RESULTS, "q3_penalty_reordering.json"), "w"), indent=2)
    open(os.path.join(R.RESULTS, "q3_penalty_reordering_report.txt"), "w").write(out)
    print("  wrote results/q3_penalty_reordering.json and _report.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
