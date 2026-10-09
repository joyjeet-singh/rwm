"""R3: the template edits, one item at a time (PLAN round 3, R3; Annex 2 E2/E3, Annex 3 A7-A10, A13).

The matcher, the exactly-once assertions and the .bak discipline are r2_patch.py's, imported. Usage, from the
repository root:  $PY docs/presubmission/round3/r3_patch.py <item>
"""
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r2_patch import apply, insert_after, pat  # noqa: E402

T = "PAPER.template.md"
BAK = "/Users/Shared/rwm_verify/evidence/R3R3"
ITEMS = {}

# --------------------------------------------------------------------------------------------- E2 (item 1)
A7 = ("- **The released evaluation is misaligned by one step; over all ten episodes it raises the checkpoint's error up "
      "to h = 32, and from h = {{v2_deploy_h}} the change is not resolved.** Evaluation feeds the action from *t−1* "
      "where training pairs states and actions index-for-index, and shifting its action index by one step fixes it. On "
      "all ten episodes' {{ad20_nind}} independent trajectories, all of them training data for this checkpoint, the "
      "stale action raises its relative-L1 error by {{adh20_rel_h1}}% {{adh20_rel_ci_h1}} at h = 1 and "
      "{{adh20_rel_h32}}% {{adh20_rel_ci_h32}} at h = 32, and changes it by {{adh20_rel_h100}}% "
      "{{adh20_rel_ci_h100}} at h = {{v2_deploy_h}} and {{ad20_rel}}% {{ad20_rel_ci}} at h = {{v2_diag_h}}; on the "
      "held-out pair's {{ad_nind}} it raises it at every horizon reported, by {{ad_rel}}% {{ad_rel_ci}} at "
      "h = {{v2_diag_h}} (§7.2).")
A8 = ("§7.2's alignment defect is given in both metrics, over all ten episodes and on the held-out pair. Over all ten "
      "episodes the two metrics agree that the stale action raises error at h = 8 and 32 and that from "
      "h = {{v2_deploy_h}} the change is not resolved, and they differ at h = 1, where relative-L1 resolves the rise "
      "and nRMSE does not.")
P72 = ("What the stale pairing costs depends on the horizon. All ten episodes are this checkpoint's training data, so "
       "the held-out pair is not more honest here, only smaller, and the larger arena leads. Over all ten episodes' "
       "{{ad20_nind}} independent trajectories the stale action raises the released checkpoint's relative-L1 error by "
       "{{adh20_rel_h1}}% {{adh20_rel_ci_h1}} at h = 1, {{adh20_rel_h8}}% {{adh20_rel_ci_h8}} at h = 8 and "
       "{{adh20_rel_h32}}% {{adh20_rel_ci_h32}} at h = 32, and from h = {{v2_deploy_h}} the change is not resolved: "
       "{{adh20_rel_h100}}% {{adh20_rel_ci_h100}} there and {{ad20_rel}}% {{ad20_rel_ci}} at h = {{v2_diag_h}}, where "
       "single trajectories run from {{ad20_traj_lo}}% to {{ad20_traj_hi}}%. In nRMSE the rise is resolved at h = 8 "
       "and 32 ({{adh20_nrmse_h8}}% {{adh20_nrmse_ci_h8}} and {{adh20_nrmse_h32}}% {{adh20_nrmse_ci_h32}}) but not at "
       "h = 1 ({{adh20_nrmse_h1}}% {{adh20_nrmse_ci_h1}}), and from h = {{v2_deploy_h}} it is not resolved either "
       "({{adh20_nrmse_h100}}% {{adh20_nrmse_ci_h100}} there, {{ad20_nrmse}}% {{ad20_nrmse_ci}} at h = {{v2_diag_h}}). "
       "Each is a 95% interval from a cluster bootstrap over whole trajectories, both pairings inside each draw "
       "(`results/alignment_by_horizon.json`, `results/alignment_defect_ci.json`). On the held-out pair's {{ad_nind}} "
       "independent trajectories the stale action raises the error at every horizon reported: by {{adh_rel_h1}}% "
       "{{adh_rel_ci_h1}} at h = 1, by {{adh_rel_h100}}% {{adh_rel_ci_h100}} at h = {{v2_deploy_h}}, where the larger "
       "arena resolves no change, and at h = {{v2_diag_h}} by {{ad_rel}}% {{ad_rel_ci}} on relative-L1 and "
       "{{ad_nrmse}}% {{ad_nrmse_ci}} in nRMSE, with per-trajectory values {{ad_rel_traj}} and {{ad_nrmse_traj}}. "
       "Shifting the evaluation loop's two action slices by one step (`model_training.py:129` and `:132`) aligns it "
       "with training; our harness does this with `action_offset = 1` (`src/score_reference.py:180-190`). Our own "
       "Arm A checkpoints at {{iters_long}} iterations, trained under the causal pairing, change by "
       "{{stale_armA_rel_h1}}% at h = 1 and {{stale_armA_rel_h368}}% at h = {{v2_diag_h}} when fed the stale one "
       "(three-seed mean, relative-L1, held-out pair; ledger R-79, which replaces R-76's void figures).")
ITEMS["e2"] = {"edits": [
    ("- **The released evaluation is misaligned by one step; the cost is concentrated at short horizons, and at "
     "h = {{v2_diag_h}} it is small and not consistent in sign.** Evaluation feeds the action from *t−1* where training "
     "pairs states and actions index-for-index, and shifting its action index by one step fixes it. On the held-out "
     "pair's {{ad_nind}} independent trajectories, which this checkpoint trained on, the stale action raises its "
     "relative-L1 error by {{adh_rel_h1}}% {{adh_rel_ci_h1}} at h = 1, and at h = {{v2_diag_h}} by {{ad_rel}}% "
     "{{ad_rel_ci}} on relative-L1 and {{ad_nrmse}}% {{ad_nrmse_ci}} in nRMSE; over all ten episodes the sign at "
     "h = {{v2_diag_h}} reverses (§7.2).", A7),
    ("§7.2's alignment defect is given in both metrics side by side at h = {{v2_diag_h}}, on the same {{ad_nind}} "
     "independent trajectories: {{ad_rel}}% {{ad_rel_ci}} on relative-L1 and {{ad_nrmse}}% {{ad_nrmse_ci}} in nRMSE; "
     "its larger cost at short horizons is given on relative-L1, at h = 1.", A8),
    ("What the stale pairing costs is concentrated at short horizons; at h = {{v2_diag_h}} it is small, and its sign "
     "is not consistent. On the held-out pair's {{ad_nind}} independent trajectories it overstates the released "
     "checkpoint's error at h = {{v2_diag_h}} by **{{ad_rel}}% {{ad_rel_ci}} on relative-L1** and **{{ad_nrmse}}% "
     "{{ad_nrmse_ci}} in nRMSE** (each a 95% interval from a cluster bootstrap over whole trajectories, both pairings "
     "inside each draw; `results/alignment_defect_ci.json`). Shifting the evaluation loop's two action slices by one "
     "step (`model_training.py:129` and `:132`) aligns it with training; our harness does this with "
     "`action_offset = 1` (`src/score_reference.py:180-190`). The four per-trajectory values are {{ad_rel_traj}} on "
     "relative-L1 and {{ad_nrmse_traj}} in nRMSE. Over all ten episodes, {{ad20_nind}} independent trajectories, the "
     "sign reverses: {{ad20_rel}}% {{ad20_rel_ci}} on relative-L1 and {{ad20_nrmse}}% {{ad20_nrmse_ci}} in nRMSE, with "
     "single trajectories from {{ad20_traj_lo}}% to {{ad20_traj_hi}}%. Every arena here is in-sample for this "
     "checkpoint, which trained on all ten episodes. One step ahead, where a stale action should matter most, it "
     "changes the checkpoint's relative-L1 error by {{adh_rel_h1}}% {{adh_rel_ci_h1}} on the held-out pair's "
     "{{ad_nind}} trajectories, and by {{adh_rel_h100}}% {{adh_rel_ci_h100}} at h = {{v2_deploy_h}}, the method's own "
     "horizon (`results/alignment_by_horizon.json`). Our own Arm A checkpoints at {{iters_long}} iterations, trained "
     "under the causal pairing, change by {{stale_armA_rel_h1}}% at h = 1 and {{stale_armA_rel_h368}}% at "
     "h = {{v2_diag_h}} when fed the stale one (three-seed mean, relative-L1, held-out pair).", P72),
]}

# --------------------------------------------------------------------------------------------- E3 (item 2), case R
A9R = (" They respond to the action. Given another trajectory's actions, their error at h = 8 on their {{x2_n_ins}} "
       "in-sample trajectories rises by {{x2_E_swap_10k}}% {{x2_ci_swap_10k}}, and at {{iters_main}} iterations by "
       "{{x2_E_swap_2500}}% {{x2_ci_swap_2500}}, so rule X2, committed before its readings existed (ledger M-84), "
       "returns **{{x2_reading}}** at both checkpoints (Appendix V). On those trajectories the stale action itself "
       "raises their error at h = 1 by {{x2_E_stale_10k_ins_h1}}% {{x2_ci_stale_10k_ins_h1}}; a one-step shift moves "
       "the action by {{x2_ctx_stale}} of its spread there, and a swap by {{x2_ctx_swap}}.")
APPH_ROW = ("| Our trained models respond to the action they are given: fed another trajectory's actions, Arm A's error at "
            "h = 8 on its in-sample arena rises by {{x2_E_swap_2500}}% at {{iters_main}} iterations and "
            "{{x2_E_swap_10k}}% at {{iters_long}} (rule X2, pre-registered: {{x2_reading}}) | M-84, M-85; "
            "`results/action_sensitivity.json` | A world model must respond to actions before it can serve policy "
            "optimisation; ours do on this test, though no policy is trained here (§7.2, Appendix V) |")
APP_V = """
## Appendix V — rule X2: whether our models respond to the action they are given

Rule X2 was committed and pushed before any of its readings existed (ledger M-84; Appendix E gives its lead time) and
is discharged in M-85. It is exploratory and re-opens no rule. It asks whether our trained models condition their
forecasts on the action they are given. Only the actions the forecast steps read are changed, so the history and the
recurrent state that meets the first forecast action are untouched. E is the change in relative-L1 error, cumulative
over forecast steps 1..h, against the true actions, err(I) / err(true) − 1 in percent: for our arms, the mean over
three seeds of each seed's E. Its 95% interval resamples whole trajectories, one resample for all seeds and both
interventions in each draw: exact over all 256 on the held-out pair, 20,000 Monte Carlo draws (seed 0) otherwise. The
interventions are the stale action (the released evaluation's offset), another trajectory's actions (a swap, each
trajectory taking the next one's), each action dimension's mean over the model's training rows, and the true actions
plus Gaussian noise at k times each dimension's training standard deviation (eight draws). **The readings** are Arm
A's, under the swap at h = 8 on its in-sample arena: **{{x2_reading}}** at {{iters_main}} iterations
({{x2_E_swap_2500}}% {{x2_ci_swap_2500}}) and at {{iters_long}} ({{x2_E_swap_10k}}% {{x2_ci_swap_10k}}). Arm B and the
released checkpoint get the same statistic, alongside and not as readings.

| model, checkpoint | actions given | h = 1 | h = 8 | h = 32 | h = {{v2_deploy_h}} |
|---|---|---|---|---|---|
{{x2_appV_own}}

**Arena: each model's own training data. For Arm A and Arm B, the in-sample arena: the training episodes'
{{x2_n_ins}} non-overlapping {{h2h_unit}}-step trajectories, n_independent = {{x2_n_ins}}. For the released checkpoint,
all ten episodes: {{ad20_nind}} trajectories, n_independent = {{ad20_nind}}. Checkpoints: Arm A and Arm B at
{{iters_main}} and {{iters_long}} iterations, three seeds each; the released checkpoint.** Each cell is E in percent
with its 95% interval; bold, the two readings. Arm B and the released checkpoint are alongside, not readings.

| model, checkpoint | actions given | h = 1 | h = 8 | h = 32 | h = {{v2_deploy_h}} |
|---|---|---|---|---|---|
{{x2_appV_ho}}

**Arena: the held-out pair (episodes {{h2h_episodes}}, {{ad_nind}} non-overlapping {{h2h_unit}}-step trajectories,
n_independent = {{ad_nind}}), out-of-sample for our arms and in-sample for the released checkpoint. Checkpoints as in
the first table.** No reading is made on this arena; every row is alongside.

| model, checkpoint | arena | stale action | another trajectory's actions | training mean | noise, k = 0.1 | noise, k = 0.5 |
|---|---|---|---|---|---|---|
{{x2_appV_delta}}

**Δ at h = 8, the relative-L1 of the forecast made with the changed actions measured against the forecast made with
the true ones (`rollout_eval.relative_error`), which is 0 for a model that ignores its actions. Arenas and checkpoints
as in the tables above; descriptive, no reading.** How far the interventions move the actions: on the forecast rows,
the action changes from one step to the next on {{x2_ctx_ins_frac}}% of steps on the in-sample arena,
{{x2_ctx_ho_frac}}% on the held-out pair and {{x2_ctx_ten_frac}}% over all ten episodes. A one-step shift moves the
action by {{x2_ctx_ins_stale}}, {{x2_ctx_ho_stale}} and {{x2_ctx_ten_stale}} of its spread (mean |a_t − a_(t−1)|
over mean |a_t − ā|), and the swap by {{x2_ctx_ins_swap}}, {{x2_ctx_ho_swap}} and {{x2_ctx_ten_swap}}
(`results/action_sensitivity.json`).
"""


def apph_insert(text):
    """Appendix H's table: the new row goes after its last row."""
    i = text.index("## Appendix H")
    j = text.index("| finding | evidence (ledger ID, artifact) | bearing on the paper |", i)
    k = text.index("\n\n", j)
    return text[:k] + "\n" + APPH_ROW + text[k:]


ITEMS["e3"] = {"inserts": [("held-out pair; ledger R-79, which replaces R-76's void figures).", A9R)],
               "hook": apph_insert, "append_before_final_rule": APP_V}

# --------------------------------------------------------------------------------------------- the abstract (item 3)
ITEMS["abstract"] = {"edits": [
    # A10 (ruling V4), tightened to keep C12.1: "short-horizon error" for "error at short horizons", "from 100 steps"
    # for "from the method's 100-step horizon"; no finding dropped
    ("Separately, the released evaluation pairs each prediction with the previous step's action, inflating error "
     "mainly at short horizons; at the longest the cost is small and not consistent in sign.",
     "Separately, the released evaluation pairs each prediction with the previous step's action; over all ten "
     "episodes this raises the checkpoint's short-horizon error, and from {{v2_deploy_h}} steps the change is "
     "unresolved."),
    # A13: the step-size correlation at the precision of the disagreement correlation beside it
    ("ranks error nearly as well ({{e7_step_r}}; margin unresolved).",
     "ranks error nearly as well ({{e7_step_r3}}; margin unresolved)."),
    # ...and section 12, which restates the pair, at the same precision (part_f_gate check 6: abstract values appear
    # in the body)
    ("predicted step size, ranks error nearly as well, by a margin this sample cannot resolve",
     "predicted step size, ranks error nearly as well, {{e7_step_r3}} against disagreement's {{d4_r}}, by a margin "
     "this sample cannot resolve"),
]}


def run(item):
    spec = ITEMS[item]
    text = open(T, encoding="utf-8").read()
    new = apply(text, spec.get("edits", []))
    for anchor, add in spec.get("inserts", []):
        new = insert_after(new, anchor, add)
    if spec.get("hook"):
        new = spec["hook"](new)
    if spec.get("append_before_final_rule"):
        assert new.rstrip().endswith("\n---"), new[-40:]
        new = new.rstrip()[:-3].rstrip("\n") + "\n" + spec["append_before_final_rule"] + "\n---\n"
    kb = set(re.findall(r"\{\{([A-Za-z0-9_]+)\}\}", text))
    ka = set(re.findall(r"\{\{([A-Za-z0-9_]+)\}\}", new))
    shutil.copy(T, f"{BAK}/PAPER.template.md.{item}.bak")
    open(T, "w", encoding="utf-8").write(new)
    print(f"{item}: keys removed {sorted(kb - ka)}; added {sorted(ka - kb)}")
    subprocess.run(["git", "--no-pager", "diff", "--stat", T])


if __name__ == "__main__":
    run(sys.argv[1])
