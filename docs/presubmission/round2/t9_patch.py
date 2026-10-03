"""Round 2, T9 item 2: the front-matter wording fixes, from the session's audit (evidence R2T9/t9_audit.md).

Wording only: every number stays a {{key}}, no claim is strengthened, and nothing leaves the paper.
Each edit is matched whitespace-tolerantly, must match exactly once, and nothing is written until every
edit has matched. Writes PAPER.template.md; the old version goes to the evidence folder first.
"""
import re
import shutil
import sys

T = "PAPER.template.md"
BAK = "/Users/Shared/rwm_verify/evidence/R2T9/bak/PAPER.template.md.t9patch"

EDITS = [
    # ---- abstract (369 words after these, cap 370; 22 numerals, cap 26) ----------------------
    ("F5 abstract: the three seeds extend the rule",
     "reproduces under a rule committed in advance and run on one seed per arm: over {{d1_seeds}} seeds, training on",
     "reproduces under a rule committed in advance, run on one seed per arm; {{d1_seeds}} seeds extend it: training on"),
    ("F6 abstract: the baseline lead has its horizon",
     "RWM beats MLP, RSSM and transformer baselines built to our reading of the original and trained with RWM's settings, though at {{v2_diag_h}} steps each does worse than predicting no change.",
     "At {{v2_diag_h}} steps RWM beats MLP, RSSM and transformer baselines built to our reading of the original and trained with RWM's settings, though each does worse than predicting no change."),
    ("F3 abstract: the equal-compute reading has its horizon",
     "our budget, the best even when that setting trains {{n3_mid_factor_word}} as long (post hoc); it was chosen as a trade-off with training time, which we do not test.",
     "our budget, the best, at {{v2_diag_h}} steps, even when that setting trains {{n3_mid_factor_word}} as long (post hoc); it was chosen as a trade-off with training time, untested here."),
    ("F12 abstract: +0.605 under the key section 6.2 prints (identical value, same statistic)",
     "Ensemble disagreement, the method's reward penalty, correlates {{a2_r_pooled}} with",
     "Ensemble disagreement, the method's reward penalty, correlates {{d4_r}} with"),
    ("F4/F12 abstract: the comparator, and M-44's own statistic",
     "at {{v2_deploy_h}} steps, five independent models are {{r2_total_x_h100}}× better calibrated and still {{r2_indep_ratio_h100}}× overconfident.",
     "at {{v2_deploy_h}} steps, independent models are {{m44_ratio_gain}}× better calibrated than our shared-trunk ones, still {{r2_indep_ratio_h100}}× overconfident."),

    # ---- contributions ----------------------------------------------------------------------
    ("F7 contribution 1: the sample size holds for the observed margin",
     "a margin {{q2_n_req}} independent trajectories would resolve if it is real, against the {{e7_nind}} here (§11).",
     "a margin {{q2_n_req}} independent trajectories would resolve if it is as large as observed, against the {{e7_nind}} here (§6.6, §11)."),
    ("Annex 4 item 4 / F11 contribution 2: seed, iterations, arena, and the extension",
     "A rule committed before the runs, run on one seed per arm, found autoregressive training ahead by {{m23_ratio}}× at h = {{v2_diag_h}}; over {{d1_seeds}} seeds the factor is {{d1_ratio}}×, and {{d1_ratio_h100}}× at h = {{v2_deploy_h}} (§5).",
     "A rule committed before the runs, run on seed {{m23_seed}} of each arm, found autoregressive training ahead by {{m23_ratio}}× at h = {{v2_diag_h}}; {{d1_seeds}} seeds at {{iters_long}} iterations extend it: the factor is {{d1_ratio}}×, and {{d1_ratio_h100}}× at h = {{v2_deploy_h}}, on the held-out pair's {{a1_nind}} independent 400-step trajectories (§5)."),
    ("F1/F11 contribution 3: arena and iterations; X1's final reading, not Part A alone",
     "specification and trained with RWM's settings, whether teacher-forced as the original trains them or autoregressively, though every baseline is worse there than predicting no change, and reading our RSSM's forecast from its prior's expected or sampled latent does not remove its open-loop collapse (exploratory; §5.3).",
     "specification and trained with RWM's settings, whether teacher-forced as the original trains them or autoregressively, on the held-out pair's {{mn_nind}} independent trajectories at {{iters_main}} iterations, though every baseline is worse there than predicting no change, and neither reading our RSSM's forecast from its prior's expected or sampled latent nor retraining it with two other settings on one seed removes its open-loop collapse (rule X1, exploratory: **{{x1_final_reading}}**; §5.3)."),
    ("F3 contribution 3: the equal-compute reading has its horizon and arena",
     "the best of them even when the centre trains {{n3_mid_factor_word}} as long (post hoc);",
     "the best of them, at h = {{v2_diag_h}} on the held-out pair, even when the centre trains {{n3_mid_factor_word}} as long (post hoc);"),
    ("F10 contribution 5: arena, and the comparison bounds the sharing effect",
     "Under a rule committed before the runs, {{r2_n_indep}} independently initialised full models are {{m44_ratio_gain}}× better calibrated than the shared-trunk arms, against a pre-registered minimum detectable effect of {{m44_mde_ratio}}×, and still {{r2_indep_ratio_h100}}× overconfident at h = {{v2_deploy_h}} (§6.8).",
     "Under a rule committed before the runs, on the held-out pair's {{r2_nind}} independent trajectories, {{r2_n_indep}} independently initialised full models are {{m44_ratio_gain}}× better calibrated than the shared-trunk arms, against a pre-registered minimum detectable effect of {{m44_mde_ratio}}×, and still {{r2_indep_ratio_h100}}× overconfident at h = {{v2_deploy_h}}; they also differ in capacity and data order, so this bounds the sharing effect rather than isolating it (§6.8)."),

    # ---- 3.2, 4 ------------------------------------------------------------------------------
    ("L2-06 section 3.2: two arenas plus all ten episodes; units; a stated checkpoint",
     "Every headline claim in this paper is measured on one of the three arenas above, at a stated number of independent trajectories, and at one checkpoint:",
     "Every headline claim in this paper is measured on the out-of-sample or in-sample arena above, or on all ten episodes together, at a stated number of independent units (400-step trajectories unless the row says otherwise), and at a stated checkpoint:"),
    ("L2-10 section 4: the iteration count behind each ratio",
     "{{mn_tf_ratio}}× worse on relative-L1 at h = {{v2_diag_h}}. Our {{d1_ratio}}× uses a different definition of teacher forcing",
     "{{mn_tf_ratio}}× worse on relative-L1 at h = {{v2_diag_h}} and {{iters_main}} iterations. Our {{d1_ratio}}×, at {{iters_long}}, uses a different definition of teacher forcing"),

    # ---- 5 and 9: M-16's verdict verbatim ---------------------------------------------------
    ("L2-07 section 5: M-16 verbatim",
     "evaluated at those same checkpoints (rule M-16, Appendix E), returned \"cannot be settled\".",
     "evaluated at those same checkpoints (rule M-16, Appendix E), returned **{{m16_verdict}}**."),
    ("L2-07 section 9: M-16 verbatim",
     "anchored at h = 8, the training forecast horizon, and returned \"cannot be settled\";",
     "anchored at h = 8, the training forecast horizon, and returned **{{m16_verdict}}**;"),
    ("L2-09 section 9 lesson 1: whose ranking, on which episodes",
     "At one forecast step it ranks whole rollouts almost perfectly, {{d2_epi_h1}}",
     "On the released checkpoint's own training episodes, at one forecast step it ranks whole rollouts almost perfectly, {{d2_epi_h1}}"),
    ("L2-08 section 9 lesson 2: the constant scalar's count is of the epistemic cells",
     "a single global multiplier manages {{d3_epi_const_ok}} of them (§6.7).",
     "a single global multiplier manages {{d3_epi_const_ok}} of the {{d3_epi_cells}} epistemic ones (§6.7)."),
    ("L2-08 section 9 lesson 2: the spread is the epistemic multipliers'",
     "The fitted multipliers span {{d3_epi_cspread}}× across horizons,",
     "The fitted epistemic multipliers span {{d3_epi_cspread}}× across horizons,"),

    # ---- 11 ------------------------------------------------------------------------------------
    ("L2-13 section 11: M-43's arena and power",
     "rule M-43 returns **{{e5_verdict}}** on their {{e5_nind}} independent 400-step trajectories (§6.6).",
     "rule M-43 returns **{{e5_verdict}}** on their {{e5_nind}} held-out 400-step trajectories, where it was under-powered (§6.6)."),
    ("L2-01 section 11: M-70's arena, in-sample status and degenerate interval",
     "finds none of the {{q3_n_pairs}} pairs reordered (rule M-70: **{{q3_verdict}}**), but it orders the penalty alone, not the penalised return, and its null is partly structural (Appendix R).",
     "finds none of the {{q3_n_pairs}} pairs among the held-out pair's {{q3_nind}} trajectories reordered (in-sample for the checkpoint; rule M-70: **{{q3_verdict}}**), but it orders the penalty alone, not the penalised return, its null is partly structural, and its interval is degenerate (Appendix R)."),

    # ---- 12 ------------------------------------------------------------------------------------
    ("F2 section 12: the baselines' settings and the lead's horizon",
     "ahead of the baselines we built to our reading of it, though at h = {{v2_diag_h}} none of them beats predicting no change,",
     "ahead at h = {{v2_diag_h}} of the baselines we built to our reading of it and trained with its settings, though there none of them beats predicting no change,"),
    ("F9 section 12: the calibration figures are in-sample",
     "overconfident where it is used, both figures at h = {{v2_deploy_h}}.",
     "overconfident, both figures at h = {{v2_deploy_h}} on the {{d1n_nind}} trajectories of the checkpoint's own training episodes."),
    ("F8 section 12: whose ranking",
     "The ranking use the follow-up claims survives a real test. Ensemble disagreement beats the forecast step index",
     "The ranking use the follow-up claims survives a real test. On the released checkpoint, ensemble disagreement beats the forecast step index"),

    # ---- appendices ----------------------------------------------------------------------------
    ("Annex 4 item 2 / F3 Appendix D: 'accuracy alone', and the equal-compute horizon",
     "**{{mn_verdict}}** on the accuracy half (§5.2): {{mn_better_list}} beat it at our budget, the best of them even when the centre trains",
     "**{{mn_verdict}}** on accuracy alone (§5.2): {{mn_better_list}} beat it at our budget, the best of them, at h = {{v2_diag_h}} on the held-out pair, even when the centre trains"),
    ("L2-02 Appendix R: the data-generation account moved to Appendix C in T6",
     "runs in a simulator this work did not have (§3).",
     "runs in a simulator this work did not have (Appendix C)."),
    ("L2-14 Appendix R: the pre-run statement is in rule M-49's own text",
     "the size of the effect it re-tested, as §6.8 said before the runs",
     "the size of the effect it re-tested, as rule M-49's own text said before the runs (ledger `M-49`)"),
]


def main():
    s = open(T).read()
    plan = []
    for name, old, new in EDITS:
        pat = re.compile(r"\s+".join(re.escape(w) for w in old.split()))
        hits = pat.findall(s)
        if len(hits) != 1:
            sys.exit(f"STOP: '{name}' matched {len(hits)} times")
        plan.append((name, pat, new))
    shutil.copy(T, BAK)
    for name, pat, new in plan:
        s = pat.sub(lambda _: new, s, count=1)
        print(f"  applied: {name}")
    open(T, "w").write(s)
    print(f"  {len(plan)} edits; old template saved to {BAK}")


if __name__ == "__main__":
    main()
