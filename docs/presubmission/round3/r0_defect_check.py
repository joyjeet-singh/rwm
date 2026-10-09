"""R0 preflight P2, the defect check: does alignment_defect_ci.rollout score our own (Arm A) models correctly?

alignment_defect_ci.rollout() unpacks `pred, *_ = model.rollout(...)`. The released checkpoint's
ReferenceRWM.rollout returns a tuple (pred, alea, epis, contacts, terms), so that takes pred. Our models'
RWMEnsemble.rollout returns the prediction tensor itself, shape (n_traj, 400, 45), so the same line takes
its FIRST TRAJECTORY, shape (400, 45), which numpy then broadcasts against every trajectory's truth.

This script uses the causal pairing (action_offset = 1) only. It computes no stale-pairing figure and no
rule-X2 reading. For Arm A seeds 0-2 at 2,500 and 10,000 iterations (the 10k runs' checkpoints, which P1
found byte-identical to the 2,500-iteration runs' at 2,500), on both of the sweep evaluator's arenas, it
compares the three-seed mean relative-L1 at h = 1, 8, 32, 100 three ways:
  committed  results/mn_compute_matched.json part2 three_seed_mean_l1 (mn_sweep_eval.score's path);
  as is      alignment_defect_ci.rollout + alignment_defect_ci.stats, imported, exactly as N1 ran them;
  unpacked   the same two functions, with model.rollout's tensor taken whole instead of unpacked.
It also checks that "as is" reproduces alignment_by_horizon.json's committed Arm A offset-1 errors on the
held-out pair, i.e. that the committed artifact carries the defect.
Run from the repository root:  $PY docs/presubmission/round3/r0_defect_check.py

Its committed output, round3/r0_defect_check.json, was produced at commit a2724f9, before the fix
(ruling (A), DECISIONS.md#R0-arm-a-rollout-defect). After the fix, alignment_defect_ci.rollout takes the
tensor whole, so "as is" equals "unpacked" and a re-run reports NOT CONFIRMED; that is the fix working.
"""
import json, os, sys

sys.path.insert(0, "scripts")
sys.path.insert(0, "src")
sys.argv = [sys.argv[0]]
import numpy as np  # noqa: E402
import torch  # noqa: E402

import alignment_defect_ci as ADC  # noqa: E402
import mn_sweep_eval as MSE  # noqa: E402
import rollout_eval as E  # noqa: E402
import rwm_data as R  # noqa: E402
import rwm_metrics as MET  # noqa: E402
import rwm_model as M  # noqa: E402

H = (1, 8, 32, 100)
paths = R.repo_paths()
cfg = R.load_reference_config(paths["lite"])
data, ep = R.load_data(paths["csv"], verbose=False)
split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"), verbose=False)
scale = MET.training_scale(data, ep, split["train_episodes"], cfg["state_data_mean"], cfg["state_data_std"])
arenas = {"held_out": MSE.arena(ep, split["holdout_episodes"], 32)["starts"],
          "in_sample": MSE.arena(ep, split["train_episodes"], 32)["starts"]}
mk = lambda st: np.asarray(st)[:, None] + np.arange(E.LEN_TRAJ)[None, :]
MC = json.load(open("results/mn_compute_matched.json"))["part2_centre_at_more_compute"]["three_seed_mean_l1"]
AB = json.load(open("results/alignment_by_horizon.json"))["arm_a"]


class Whole:
    """Presents model.rollout's tensor as a one-element tuple, so `pred, *_ =` takes it whole."""
    def __init__(self, m):
        self.m = m

    def rollout(self, *a, **k):
        return (self.m.rollout(*a, **k),)


def rel(model, idx, h):
    pred, true = ADC.rollout(model, data, cfg, idx, 1)
    ADC.H = h
    try:
        return ADC.stats(pred - true, true, scale, np.arange(len(idx)))["rel_l1"], pred.shape
    finally:
        ADC.H = 368


out = {"purpose": __doc__.split("\n")[0], "pairing": "action_offset = 1 only", "rows": []}
worst = {"as_is": 0.0, "unpacked": 0.0}
ab_ok = True
for it in ("2500", "10000"):
    models = []
    for s in (0, 1, 2):
        m = M.build_from_config(cfg, ensemble_size=1)
        m.load_state_dict(torch.load(f"runs/armA_seed{s}_10k/weights_{it}.pt", map_location="cpu")["model_state_dict"], strict=True)
        m.eval()
        models.append(m)
    for ar, st in arenas.items():
        idx = mk(st)
        for h in H:
            a = [rel(m, idx, h) for m in models]
            u = [rel(Whole(m), idx, h) for m in models]
            row = {"iterations": int(it), "arena": ar, "n": len(st), "h": h,
                   "committed": MC[it][ar][str(h)],
                   "as_is": float(np.mean([x[0] for x in a])), "as_is_pred_shape": list(a[0][1]),
                   "unpacked": float(np.mean([x[0] for x in u])), "unpacked_pred_shape": list(u[0][1])}
            for k in worst:
                worst[k] = max(worst[k], abs(row[k] - row["committed"]))
            out["rows"].append(row)
        if ar == "held_out":
            # the committed N1 artifact's own offset-1 errors, per seed and trajectory, at h = 1
            for s, m in enumerate(models):
                pred, true = ADC.rollout(m, data, cfg, idx, 1)
                e, t = (pred - true)[:, E.START_STEP:E.START_STEP + 1], true[:, E.START_STEP:E.START_STEP + 1]
                mine = (np.abs(e).sum(-1) / np.abs(t).sum(-1)).mean(1)
                theirs = AB[it]["full"][str(s)]["1"]["per_trajectory"]["offset1"]["rel_l1"]
                ab_ok &= bool(np.allclose(mine, theirs, rtol=0, atol=1e-9))
out["max_abs_diff_from_committed"] = worst
out["as_is_reproduces_alignment_by_horizon_arm_a_offset1_h1_per_trajectory"] = ab_ok
out["verdict"] = ("DEFECT CONFIRMED" if worst["unpacked"] <= 1e-6 < worst["as_is"] and ab_ok else "NOT CONFIRMED")
os.makedirs("/Users/Shared/rwm_verify/evidence/R3R0", exist_ok=True)
json.dump(out, open("/Users/Shared/rwm_verify/evidence/R3R0/defect_check.json", "w"), indent=1)
json.dump(out, open("docs/presubmission/round3/r0_defect_check.json", "w"), indent=1)
print(f"{'it':>6} {'arena':9} {'h':>3} {'committed':>10} {'as is':>10} {'unpacked':>10}")
for r in out["rows"]:
    print(f"{r['iterations']:>6} {r['arena']:9} {r['h']:>3} {r['committed']:10.6f} {r['as_is']:10.6f} {r['unpacked']:10.6f}")
print("pred shapes: as is", out["rows"][0]["as_is_pred_shape"], "unpacked", out["rows"][0]["unpacked_pred_shape"])
print("max |diff| from committed:", worst)
print("as is reproduces alignment_by_horizon.json Arm A offset-1 per-trajectory h=1 (1e-9):", ab_ok)
print("VERDICT:", out["verdict"])
