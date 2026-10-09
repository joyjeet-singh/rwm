"""
Pre-submission S3, item 4 -- the one-step alignment defect, with intervals.

§7.2 reports that the released evaluation pairs each prediction with the previous row's
action (action_offset = 0) where training pairs it with the same row's (offset 1), and that
this overstates the released checkpoint's error at h = 368 by 75% in nRMSE and 9.5% in
relative-L1 (results/step4_0a_results.json). Those are point estimates. This script gives
them intervals and shows what they rest on.

THE MODEL AND THE ROLLOUT are step4_0a_restate.py's exactly: the released checkpoint
(score_reference.ReferenceRWM), rolled out from 32 history rows under each pairing.

THREE ARENAS, and why each:
  protocol_a    the ten trajectories results/step4_0a_results.json was computed on -- the
                harness's Protocol A, sampled with seed 0 from the held-out pair, and
                overlapping. Point estimates only: it exists to show this script reproduces
                the published figures, and overlapping windows are not independent units, so
                no interval is computed on it.
  held_out_n4   the held-out pair's four non-overlapping 400-step trajectories, §5's arena,
                n_independent = 4. The governing arena for the intervals.
  all_ten_n20   the twenty non-overlapping 400-step trajectories of all ten episodes,
                n_independent = 20: the companion §7.2 reports, in-sample for the checkpoint.

THE STATISTICS. The overstatement is err(offset 0) / err(offset 1) - 1 at h = 368, on:
  rel_l1       the upstream's relative-L1, e = mean over trajectories and steps of r_t
               (rollout_eval.relative_error), the figure the paper prints as 9.5%;
  nrmse_curve  nRMSE as step4_0a_restate.py computes it -- the RMSE across trajectories at
               each step, per dimension over the training scale, meaned over dimensions and
               then over steps 1..368 (rwm_metrics.nrmse_per_step + summarise): the figure
               the paper prints as 75%;
  nrmse_form1  nRMSE form 1 (rwm_metrics.nrmse_pooled): pooled over trajectories, steps and
               dimensions before dividing, the form §3.1 names as primary.
THE INTERVALS are 95% cluster bootstraps over whole trajectories with BOTH pairings inside
each draw, so every draw compares the same resampled trajectories under the two pairings:
exact over all 4**4 = 256 resamples at n = 4, and 20,000 Monte Carlo resamples with generator
seed 0 at n = 20. The per-trajectory errors and ratios are stored beside them.

Writes results/alignment_defect_ci.json.
"""
import itertools
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import torch  # noqa: E402

import rollout_eval as E  # noqa: E402
import rwm_data as R  # noqa: E402
import rwm_metrics as MET  # noqa: E402
import score_reference as S  # noqa: E402

H = 368
MC_N, MC_SEED = 20000, 0


def rollout(model, data, cfg, idx, offset):
    """step4_0a_restate.rollout_for, verbatim in behaviour."""
    raw = data[idx]
    st = torch.as_tensor(R.normalise_state(raw[:, :, R.STATE_COLS],
                                           cfg["state_data_mean"], cfg["state_data_std"]),
                         dtype=torch.float32)
    ac = torch.as_tensor(raw[:, :, R.ACTION_COLS], dtype=torch.float32)
    with torch.no_grad():
        out = model.rollout(st, ac, E.START_STEP, action_offset=offset)
    # The released checkpoint's ReferenceRWM.rollout returns (pred, alea, epis, contacts, terms);
    # our models' RWMEnsemble.rollout returns pred itself. `pred, *_ = <tensor>` takes the tensor's
    # FIRST TRAJECTORY, which numpy then broadcasts against every trajectory's truth, and round 2's
    # N1 scored our Arm A exactly that way (ledger R-79). A tensor is taken whole, and the shape is
    # asserted so that neither return type can be misread again.
    pred = out[0] if isinstance(out, tuple) else out
    assert pred.shape == st.shape, f"rollout returned {tuple(pred.shape)} for states {tuple(st.shape)}"
    return pred.double().numpy(), st.double().numpy()


def stats(err, true, scale, sel):
    """The three pooled statistics over the trajectories in sel (with repeats)."""
    e, t = err[sel][:, E.START_STEP:E.START_STEP + H], true[sel][:, E.START_STEP:E.START_STEP + H]
    rel = float((np.abs(e).sum(-1) / np.abs(t).sum(-1)).mean())
    curve = (np.sqrt((e ** 2).mean(axis=0)) / scale).mean(-1)          # nrmse_per_step
    return {"rel_l1": rel, "nrmse_curve": float(curve.mean()),
            "nrmse_form1": float(MET.nrmse_pooled(e ** 2, scale))}


def per_traj(err, true, scale):
    e, t = err[:, E.START_STEP:E.START_STEP + H], true[:, E.START_STEP:E.START_STEP + H]
    return {"rel_l1": (np.abs(e).sum(-1) / np.abs(t).sum(-1)).mean(1).tolist(),
            "nrmse_form1": [float(MET.nrmse_pooled(e[k:k + 1] ** 2, scale))
                            for k in range(len(e))]}


def arena(model, data, cfg, scale, idx, draws):
    out = {"starts": [int(s) for s in idx[:, 0]], "n_trajectories": int(len(idx))}
    runs = {o: rollout(model, data, cfg, idx, o) for o in (0, 1)}
    err = {o: runs[o][0] - runs[o][1] for o in (0, 1)}
    true = runs[1][1]
    allsel = np.arange(len(idx))
    point = {o: stats(err[o], true, scale, allsel) for o in (0, 1)}
    out["pooled"] = {f"offset{o}": point[o] for o in (0, 1)}
    out["overstatement_pct"] = {k: 100 * (point[0][k] / point[1][k] - 1) for k in point[0]}
    pt = {o: per_traj(err[o], true, scale) for o in (0, 1)}
    out["per_trajectory"] = {f"offset{o}": pt[o] for o in (0, 1)}
    out["per_trajectory_overstatement_pct"] = {
        k: [100 * (a / b - 1) for a, b in zip(pt[0][k], pt[1][k])] for k in pt[0]}
    if draws is not None:
        boots = {k: [] for k in point[0]}
        for sel in draws:
            s0, s1 = stats(err[0], true, scale, sel), stats(err[1], true, scale, sel)
            for k in boots:
                boots[k].append(100 * (s0[k] / s1[k] - 1))
        out["ci95_pct"] = {k: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]
                           for k, v in boots.items()}
        out["n_resamples"] = len(draws)
    return out


def main():
    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    data, ep = R.load_data(paths["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"),
                         verbose=False)
    scale = MET.training_scale(data, ep, split["train_episodes"],
                               cfg["state_data_mean"], cfg["state_data_std"])
    model = S.ReferenceRWM(torch.load(paths["ckpt"], map_location="cpu")
                           ["system_dynamics_state_dict"])
    model.eval()

    idx_a = E.sample_trajectories(ep, split["holdout_episodes"], seed=0)
    s4 = MET.non_overlapping_starts(ep, split["holdout_episodes"], E.LEN_TRAJ)
    s20 = MET.non_overlapping_starts(ep, list(range(10)), E.LEN_TRAJ)
    assert MET.n_independent(s4, E.LEN_TRAJ) == 4 and MET.n_independent(s20, E.LEN_TRAJ) == 20
    mk = lambda st: np.asarray(st)[:, None] + np.arange(E.LEN_TRAJ)[None, :]
    exact4 = np.array(list(itertools.product(range(4), repeat=4)))
    mc20 = np.random.default_rng(MC_SEED).integers(0, 20, size=(MC_N, 20))

    res = {"protocol_a": arena(model, data, cfg, scale, idx_a, None),
           "held_out_n4": arena(model, data, cfg, scale, mk(s4), exact4),
           "all_ten_n20": arena(model, data, cfg, scale, mk(s20), mc20)}

    # The published figures, and whether this script reproduces them on their own arena.
    pub = json.load(open(os.path.join(R.RESULTS, "step4_0a_results.json")))["protocols"]
    pub_pct = {"rel_l1": 100 * (pub["A_off0"]["e"] / pub["A_off1"]["e"] - 1),
               "nrmse_curve": 100 * (pub["A_off0"]["nrmse"]["368"] / pub["A_off1"]["nrmse"]["368"] - 1)}
    # step4_0a accumulated in float32 through rollout_eval.evaluate; this script in float64.
    # So "reproduced" is judged at the precision the paper prints, and the raw gap is kept.
    _prec = {"rel_l1": 1, "nrmse_curve": 0}
    repro = {k: {"abs_diff_pct_points": abs(res["protocol_a"]["overstatement_pct"][k] - v),
                 "at_printed_precision": round(res["protocol_a"]["overstatement_pct"][k], _prec[k])
                 == round(v, _prec[k])} for k, v in pub_pct.items()}

    n4, n20 = res["held_out_n4"]["overstatement_pct"], res["all_ten_n20"]["overstatement_pct"]
    printed = {"nrmse": f"{pub_pct['nrmse_curve']:.0f}", "rel_l1": f"{pub_pct['rel_l1']:.1f}"}
    checks = {
        "n4_reproduces_printed_nrmse_curve": f"{n4['nrmse_curve']:.0f}" == printed["nrmse"],
        "n4_reproduces_printed_nrmse_form1": f"{n4['nrmse_form1']:.0f}" == printed["nrmse"],
        "n4_reproduces_printed_rel_l1": f"{n4['rel_l1']:.1f}" == printed["rel_l1"],
        "n20_same_direction": all(np.sign(n20[k]) == np.sign(n4[k]) for k in n4),
        "n20_within_2x": all(0.5 <= n20[k] / n4[k] <= 2.0 for k in n4 if n4[k] != 0),
    }
    out = {"purpose": "PLAN S3 item 4: the alignment defect's overstatement at h = 368, with "
                      "intervals, on the released checkpoint",
           "horizon": H, "offsets": {"0": "the released evaluation's pairing",
                                     "1": "training's pairing (causal)"},
           "published": {"source": "results/step4_0a_results.json protocols A_off0 / A_off1",
                         "pct": pub_pct, "printed": printed,
                         "reproduced_on_protocol_a": repro},
           "arenas": res, "checks": checks,
           "bootstrap": {"n4": "exact, all 256 ordered resamples of whole trajectories, both "
                               "pairings inside each draw",
                         "n20": f"Monte Carlo, {MC_N} resamples, generator seed {MC_SEED}"}}
    json.dump(out, open(os.path.join(R.RESULTS, "alignment_defect_ci.json"), "w"), indent=2)

    print("=" * 96)
    print("ALIGNMENT DEFECT — overstatement at h = 368, released checkpoint, offset 0 over offset 1")
    print("=" * 96)
    print(f"  published (step4_0a, Protocol A): nRMSE {pub_pct['nrmse_curve']:.2f}%  "
          f"rel-L1 {pub_pct['rel_l1']:.2f}%   reproduced here: {repro}")
    for a, r in res.items():
        o = r["overstatement_pct"]
        ci = r.get("ci95_pct", {})
        f = lambda k: f"{o[k]:6.2f}%" + (f" [{ci[k][0]:6.2f}, {ci[k][1]:6.2f}]" if k in ci else "")
        print(f"  {a:<12} n={r['n_trajectories']:>2}  nRMSE(curve) {f('nrmse_curve')}  "
              f"nRMSE(form 1) {f('nrmse_form1')}  rel-L1 {f('rel_l1')}")
        print(f"      per-trajectory rel-L1 {np.round(r['per_trajectory_overstatement_pct']['rel_l1'], 1).tolist()}")
        print(f"      per-trajectory nRMSE  {np.round(r['per_trajectory_overstatement_pct']['nrmse_form1'], 1).tolist()}")
    print(f"  checks: {checks}")
    print("  wrote results/alignment_defect_ci.json")


if __name__ == "__main__":
    main()
