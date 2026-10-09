"""R2: the template edits for one item at a time (PLAN round 3, R2; Annex 2 E1/E4/E5, Annex 3 A1-A6, A5b).

Every replacement uses the whitespace-tolerant matcher (CLAUDE.md of the parent folder's rule 4, kept here because it
has caught real failures), asserts its anchor matches exactly once, writes a .bak before any change and writes nothing
unless every assertion passes. Usage, from the repository root:  $PY docs/presubmission/round3/r2_patch.py <item>
"""
import re
import shutil
import subprocess
import sys

T = "PAPER.template.md"
BAK = "/Users/Shared/rwm_verify/evidence/R3R2"


def pat(old):
    return re.compile(r"[\s>]+".join(re.escape(w) for w in old.split()))


def apply(text, edits):
    for old, new in edits:
        hits = pat(old).findall(text)
        assert len(hits) == 1, (len(hits), old[:90])
    for old, new in edits:
        text = pat(old).sub(lambda m: new, text, count=1)
    return text


def insert_after(text, anchor, addition):
    hits = pat(anchor).findall(text)
    assert len(hits) == 1, (len(hits), anchor[:90])
    m = pat(anchor).search(text)
    return text[:m.end()] + addition + text[m.end():]


ITEMS = {}

# --------------------------------------------------------------------------------------------- E1 (item 1)
A1 = (" Its second heatmap prints training hours: {{orig_h_32_8}} for the centre and {{orig_h_32_32}} for "
      "{{orig_tied_label}}, {{orig_h_ratio}}×, so on the original's own figures the centre matches that neighbour's "
      "printed error, {{orig_e_32_8}}, in under half the time. Our measured cost per iteration for the same pair is "
      "{{n3_cost_M32_N32}}× (the table's last column).")
A2_CLOSE = (" That is a statement about learning speed at this budget, not about converged accuracy: trained "
            "{{n3_long_factor_word}} as long, the centre passes both winning shorter histories on "
            "{{n3_sh_long_nread_word}} of the {{n3_n_readings_word}} readings (below), so it does not contradict the "
            "original's steep fall to M = 8, whose training budget the original does not state.")
A3 = ("A longer training forecast costs more per iteration, {{n3_cost_M32_N16}}× the centre's for {{n3_lf_label}} and "
      "{{n3_cost_M32_N32}}× for {{mn_best_config}}; the shorter histories that win cost less, {{n3_cost_M8_N8}}× for "
      "{{n3_sh_label_M8_N8}} and {{n3_cost_M2_N8}}× for {{n3_sh_label_M2_N8}} (`results/mn_compute_matched.json`; "
      "Appendix U gives every reading, signed as in the table). The shorter histories win on all "
      "{{n3_n_readings_word}} readings at {{iters_main}} iterations while using well under half the centre's "
      "computation, so that part of the verdict needs no compute correction. The longer forecasts' wins do. Trained "
      "to {{n3_k_mid}} iterations, the centre has had {{n3_best_over_mid}}× the computation of {{mn_best_config}}, and "
      "the readings split: {{mn_best_config}} is still ahead on the held-out pair at h = {{v2_diag_h}} "
      "({{n3_best_D_mid}} {{n3_best_ci_mid}}), the centre is ahead on the in-sample arena at h = {{v2_deploy_h}} "
      "({{n3_best_ins_D_mid_h100}} {{n3_best_ins_ci_mid_h100}}), and the other two are not resolved. At "
      "{{iters_long}} iterations, {{n3_best_over_long}}× the computation, the centre is ahead on both in-sample "
      "readings and neither held-out difference is resolved. Trained that long, it also passes both shorter "
      "histories on {{n3_sh_long_nread_word}} of the {{n3_n_readings_word}} readings: on the held-out pair at "
      "h = {{v2_diag_h}}, {{n3_sh_label_M2_N8}} by {{n3_sh_D_long_M2_N8}} {{n3_sh_ci_long_M2_N8}} and "
      "{{n3_sh_label_M8_N8}} by {{n3_sh_D_long_M8_N8}} {{n3_sh_ci_long_M8_N8}}, with {{n3_sh_over_long_M2_N8}}× and "
      "{{n3_sh_over_long_M8_N8}}× their computation, and on both in-sample readings; on the held-out pair at "
      "h = {{v2_deploy_h}} neither difference is resolved. Which setting is most accurate therefore depends on how "
      "long each is trained. None of this re-opens rule M-74.")
APP_U = """
## Appendix U — the settings sweep at equal training compute

Post hoc (ledger R-78; `results/mn_compute_matched.json`); it re-opens no rule, and rule M-74's verdict,
{{mn_verdict}}, stands as a statement about the {{iters_main}}-iteration budget (§5.2). Each row sets one of the
{{mn_n_better_word}} configurations that beat the centre at {{iters_main}} iterations against the centre trained to
{{iters_main}}, {{n3_k_mid}} or {{iters_long}} iterations: {{n3_appU_nrows_word}} rows of {{n3_n_readings_word}}
readings each. A longer forecast costs more per iteration than the centre, a shorter history less, so the centre's
longer runs ask whether a configuration's win survives giving the centre at least as much training computation.

| configuration (cost per iteration ÷ the centre's) | centre trained to (iterations) | compute ratio (centre's total ÷ configuration's) | h = {{v2_deploy_h}}, held-out pair ({{mn_nind}}) | h = {{v2_deploy_h}}, in-sample ({{mn_nind_ins}}) | h = {{v2_diag_h}}, held-out pair ({{mn_nind}}) | h = {{v2_diag_h}}, in-sample ({{mn_nind_ins}}) |
|---|---|---|---|---|---|---|
{{n3_appU_table}}

**Arenas: the held-out pair (episodes {{h2h_episodes}}, {{mn_nind}} non-overlapping {{h2h_unit}}-step trajectories,
n_independent = {{mn_nind}}) and the in-sample arena (the training episodes' {{mn_nind_ins}} non-overlapping
{{h2h_unit}}-step trajectories, n_independent = {{mn_nind_ins}}). Checkpoints: each configuration at {{iters_main}}
iterations, the centre at the iterations in the second column; three seeds each.** Each cell is D, the configuration's
relative-L1 minus the centre's, the mean over trajectories of the three-seed means, with its 95% interval: exact over
all 256 ordered resamples on the held-out pair, 20,000 Monte Carlo resamples (seed 0) in-sample. Negative favours the
configuration, so every reading here is signed as in §5.2's table; bold where the interval excludes zero. Cost per
iteration is steady training time per iteration, timed
without contention; the compute ratio is the centre's total training computation over the configuration's.
"""
ITEMS["e1"] = {
    "edits": [
        ("**The history length departs furthest from the original.**", "**At our budget, shorter histories win.**"),
        ("A longer training forecast costs more per iteration, {{n3_cost_M32_N16}}× the centre's for {{n3_lf_label}} "
         "and {{n3_cost_M32_N32}}× for {{mn_best_config}}, so at a given iteration count those also had more "
         "computation; the shorter histories that win cost less, {{n3_cost_M8_N8}}× and {{n3_cost_M2_N8}}×. Training "
         "the centre longer controls for this (`results/mn_compute_matched.json`; differences signed as in the table). "
         "At {{n3_k_mid}} iterations the centre has had {{n3_best_over_mid}}× the computation of {{mn_best_config}} at "
         "{{iters_main}}, and {{mn_best_config}} is still ahead at h = {{v2_diag_h}}, a difference of {{n3_best_D_mid}} "
         "{{n3_best_ci_mid}}, so its advantage is not an artefact of extra computation per iteration. That is as far as "
         "it goes. At {{iters_long}} iterations, {{n3_best_over_long}}× the computation, the difference is "
         "{{n3_best_D_long}} {{n3_best_ci_long}}, not resolved; on the in-sample arena the centre at {{n3_k_mid}} "
         "already draws level with {{mn_best_config}} ({{n3_best_ins_D_mid}} {{n3_best_ins_ci_mid}}) and passes "
         "{{n3_lf_label}} ({{n3_lf_ins_D_mid}} {{n3_lf_ins_ci_mid}}); and at {{iters_long}}, on the held-out pair, it "
         "passes both shorter histories, {{n3_sh_long_clause}}. None of this re-opens rule M-74.", A3),
        ("post hoc), so the ranking is at this budget, not at convergence.",
         "post hoc), so the ranking is at this budget, not at convergence, and it changes with training length "
         "(Appendix U)."),
    ],
    "inserts": [
        ("its longest-forecast neighbour (`docs/presubmission/ORIGINAL_SPECS.md` a.5).", A1),
        ("though other readings the rule reports put shorter histories behind it: {{mn_mvar_other_worse}}.", A2_CLOSE),
    ],
    "append_before_final_rule": APP_U,
}

# --------------------------------------------------------------------------------------------- restatements (item 2)
ITEMS["restate"] = {
    "edits": [
        # A4, the abstract (ruling V3), tightened to keep C12.1's word cap: the same claims, no finding dropped
        ("On accuracy alone, {{mn_better_kinds}} beat the original's setting at our budget, the best, at {{v2_diag_h}} "
         "steps, even when that setting trains {{n3_mid_factor_word}} as long (post hoc); it was chosen as a trade-off "
         "with training time, untested here.",
         "On accuracy alone, {{mn_better_kinds}} beat the original's setting at our budget; trained longer, it passes "
         "each on some reading (post hoc), so the ranking depends on training budget. Its trade-off with training time "
         "is untested here."),
        # A5, contribution 3's configuration half
        ("On accuracy alone, {{mn_n_better_word}} of the {{mn_n_configs_word}} one-factor neighbours of the original's "
         "{{mn_centre_label}} beat it at our budget — {{mn_better_long_phrase}}, and the {{mn_n_short_better_word}} "
         "shorter histories {{mn_mvar_better_list}}, although the original's error falls steeply as the history grows "
         "to M = 8 — the best of them, at h = {{v2_diag_h}} on the held-out pair, even when the centre trains "
         "{{n3_mid_factor_word}} as long (post hoc); the original chose the centre as a trade-off with training time, "
         "which we do not test (§5.2).",
         "On accuracy alone at our budget, {{mn_n_better_word}} of the {{mn_n_configs_word}} one-factor neighbours of "
         "the original's {{mn_centre_label}} beat it, {{mn_n_short_better_word}} shorter histories at under half its "
         "cost per iteration and {{mn_better_long_phrase}} at more, but trained longer the centre passes each of them "
         "on at least one reading (post hoc), so the ranking depends on the training budget; the original chose the "
         "centre as a trade-off with training time, which its own printed hours are consistent with and we do not "
         "test (§5.2)."),
        # A6, Appendix D's configuration row
        ("{{mn_better_list}} beat it at our budget, the best of them, at h = {{v2_diag_h}} on the held-out pair, even "
         "when the centre trains {{n3_mid_factor_word}} as long (post hoc, §5.2). The trade-off with training time is "
         "not tested |",
         "{{mn_better_list}} beat it at our budget, but the ranking depends on training length: trained longer, the "
         "centre passes each of them on at least one reading (post hoc, §5.2, Appendix U). The trade-off with training "
         "time is not tested; the original's printed hours are consistent with it |"),
        # A6, section 12
        ("beat its chosen ones at our budget, which it chose as a trade-off with training time (§5.2, §5.3).",
         "beat its chosen ones at our budget, a ranking that changes when the chosen setting trains longer; it chose "
         "them as a trade-off with training time (§5.2, §5.3)."),
    ],
}

# --------------------------------------------------------------------------------------------- E4 (item 3)
A5B = (" On the in-sample arena's {{mn_nind_ins}} trajectories, with nRMSE pooled as §3.1 defines it (computed "
       "afterwards, post hoc; ledger R-77), {{n2_n_changed_word}} readings differ from the per-trajectory average the "
       "rules' evaluator used. Teacher-forced, at h = 1 all three baselines are ahead of RWM: D, signed as the rules "
       "sign it (positive favours RWM), is {{n2_m75_D_mlp}} {{n2_m75_ci_mlp}} for the MLP, {{n2_m75_D_rssm}} "
       "{{n2_m75_ci_rssm}} for the RSSM and {{n2_m75_D_transformer}} {{n2_m75_ci_transformer}} for the transformer, "
       "so M-75's reading there is {{n2_m75_pooled}} where the average gave {{n2_m75_committed}}: the same one-step "
       "lead for teacher forcing as §5's. Trained autoregressively, the MLP's deficit at h = {{v2_deploy_h}} is no "
       "longer resolved ({{n2_m76_D_mlp}} {{n2_m76_ci_mlp}}), so M-76's reading there is {{n2_m76_pooled}} where the "
       "average gave {{n2_m76_committed}}. Neither changes a verdict; both rules govern at h = {{v2_diag_h}} on "
       "relative-L1.")
ITEMS["e4"] = {
    "edits": [
        ("and return the same verdict as the averaged ones everywhere except {{n2_n_changed_word}} in-sample readings "
         "of §5.3's rules (which configurations a reading resolves can shift; the artifact lists each): "
         "{{n2_changed_list}}.",
         "and, for this section's rule (M-74), return the same verdicts as the averaged ones (§5.3 gives the "
         "{{n2_n_changed_word}} readings of its rules that differ)."),
    ],
    "inserts": [
        ("cannot be told apart from RWM: at h = 1 both rules return {{bl_tf_h1}}, and at h = 8 both return "
         "{{bl_tf_h8}}.", A5B),
    ],
}

# --------------------------------------------------------------------------------------------- E5 (item 4)
# Ruling V9. The attribution is verified verbatim against PlaNet's HTML through scripts/t1_bibliography.py (hafner2019's
# two fragments); PlaNet's own caveat, that its final RSSM agent did not need the objective, travels with it.
ITEMS["e5"] = {
    "edits": [
        ("and X1 tried only the two settings above, on one seed.",
         "and X1 tried only the two settings above, on one seed, neither of them PlaNet's latent overshooting "
         "(Hafner et al., ICML 2019), which trains the prior's multi-step predictions in latent space and which "
         "PlaNet's own final RSSM agent did not need."),
    ],
}


def run(item):
    spec = ITEMS[item]
    text = open(T, encoding="utf-8").read()
    new = apply(text, spec.get("edits", []))
    for anchor, add in spec.get("inserts", []):
        new = insert_after(new, anchor, add)
    if spec.get("append_before_final_rule"):
        assert new.rstrip().endswith("\n---"), new[-40:]
        body = new.rstrip()[:-3].rstrip("\n")
        new = body + "\n" + spec["append_before_final_rule"] + "\n---\n"
    keys_before = set(re.findall(r"\{\{([A-Za-z0-9_]+)\}\}", text))
    keys_after = set(re.findall(r"\{\{([A-Za-z0-9_]+)\}\}", new))
    shutil.copy(T, f"{BAK}/PAPER.template.md.{item}.bak")
    open(T, "w", encoding="utf-8").write(new)
    print(f"{item}: keys removed {sorted(keys_before - keys_after)}; added {sorted(keys_after - keys_before)}")
    subprocess.run(["git", "--no-pager", "diff", "--stat", T])


if __name__ == "__main__":
    run(sys.argv[1])
