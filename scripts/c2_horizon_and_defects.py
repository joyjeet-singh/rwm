"""
C2 -- the h=100 sweep, and the outright errors the revision brief found.

WHAT THIS FIXES. The paper re-anchored from h=368 (the upstream's open-loop
diagnostic length) to h=100 (the method's own imagination rollout length). The
tables followed and parts of the prose did not, so sentences quoting an h=368
figure sat beside h=100 tables without saying so. `scripts/horizon_sweep.py`
finds them mechanically; this applies the fixes it points at, plus the nine
defects of the brief's Part 3 and the scoping of Part 4.

Every edit is asserted to match exactly once, and the matcher is
whitespace-tolerant because single-line search strings fail on wrapped prose --
which has bitten this project repeatedly. Nothing is written until every
assertion has passed.

Run with --write. `scripts/horizon_sweep.py` should report zero findings
afterwards, and `check_comparative_claims.py` registers it as a check kind so it
stays that way.
"""
import difflib
import re
import shutil
import sys

TEMPLATE = "PAPER.template.md"

# (label, old, new). `old` is matched whitespace-tolerantly.
EDITS = [

    # =====================================================================
    # PART 1 -- the sweep. Every one of these quotes a horizon-indexed
    # calibration figure without naming the horizon, or names the wrong one.
    # =====================================================================

    # -- abstract ---------------------------------------------------------
    # The A/B factor and the epistemic coverage are both 4.61 and sat three
    # sentences apart, which reads as a typo. They are now a "factor of" against
    # a percentage-against-percentage, at named and different horizons.
    ("1.3a abstract: the A/B claim names the horizon its rule was stated over",
     "**The base paper's central training claim reproduces.** Autoregressive training "
     "beats teacher forcing {{d1_ratio}}-fold on the reference's own relative-L1 error, "
     "on held-out episodes, under a rule committed to git before the runs that tested it.",

     "**The base paper's central training claim reproduces.** Autoregressive training beats\n"
     "teacher forcing by a factor of {{d1_ratio}} on the reference's own relative-L1 error at\n"
     "h = {{v2_diag_h}}, the horizon its pre-registered rule names, and by {{d1_ratio_h100}} at\n"
     "h = {{v2_deploy_h}} — on held-out episodes, under a rule committed to git before the runs\n"
     "that tested it."),

    ("1.3b abstract: name h=100, and give the aleatoric gap as a factor rather "
     "than a wrong order of magnitude",
     "**Neither uncertainty output the follow-up adds is usable as an interval.** At the horizon "
     "its own imagination rollouts run to, the ensemble disagreement it penalises rewards with is "
     "{{d1n_epi_ratio_h100}}× smaller than the realised error, covering {{d1n_epi_cov1_h100}}% of "
     "outcomes at ±1σ against a calibrated two thirds. The per-member σ, which the method computes "
     "and discards, is worse by three orders of magnitude, and we derive why: the implemented "
     "objective's optimum is σ = 0.",

     "**Neither uncertainty output the follow-up adds is usable as an interval.** At\n"
     "h = {{v2_deploy_h}}, the horizon its own imagination rollouts run to, the ensemble\n"
     "disagreement it penalises rewards with is {{d1n_epi_ratio_h100}}× smaller than the realised\n"
     "error, and {{d1n_epi_cov1_h100}}% of outcomes fall inside ±1σ where {{v3_cov_nominal1}}% is\n"
     "calibrated. The per-member σ, which the method computes and discards, is worse at that same\n"
     "horizon by a further factor of {{d1n_epi_over_alea_h100}}, and we derive why: the implemented\n"
     "objective's optimum is σ = 0."),

    # -- 6.2 --------------------------------------------------------------
    ("1.8 6.2 released-checkpoint note: two figures, two arenas AND two horizons",
     "*A note on the released checkpoint's row, so the next table does not read as a "
     "contradiction.* Its {{cal_rel_ratio}}× is measured on those same {{b2_nind}} trajectories, "
     "for comparability with the three arms beside it. The released checkpoint trained on all ten "
     "episodes, so its own best-sampled figure is the {{d1n_alea_ratio_h100}}× below, at "
     "n_independent = {{d1n_nind}}. Both are correct; they are different arenas, and neither is a "
     "held-out measurement *of the released checkpoint*, which has no held-out arena in this "
     "dataset.",

     "*A note on the released checkpoint's row, so the next table does not read as a\n"
     "contradiction.* Its {{cal_rel_ratio}}× is the whole {{v2_diag_h}}-step rollout on those same\n"
     "{{b2_nind}} trajectories, for comparability with the three arms beside it. The released\n"
     "checkpoint trained on all ten episodes, so its own best-sampled figure is the\n"
     "{{d1n_alea_ratio_h100}}× below — cumulative to h = {{v2_deploy_h}}, at n_independent =\n"
     "{{d1n_nind}}. **Both are correct and they differ in two ways at once: a different arena and a\n"
     "different horizon.** Neither is a held-out measurement *of the released checkpoint*, which has\n"
     "no held-out arena in this dataset."),

    ("1.1 6.2 epistemic summary: the ratio between the two terms is itself "
     "horizon-dependent, and this paired the h=368 one with h=100 figures",
     "Epistemic is {{d1n_epi_over_alea_h368}}× better than aleatoric and still wrong by "
     "**{{d1n_epi_ratio_h1}}×** at one step and **{{d1n_epi_ratio_h100}}× "
     "[{{d1n_epi_ratio_ci_h100}}]** at h = {{v2_deploy_h}}, the method's own imagination rollout "
     "length, with ±1σ coverage of {{d1n_epi_cov1_h100}}% [{{d1n_epi_cov1_ci_h100}}] where a "
     "calibrated Gaussian gives {{v3_cov_nominal1}}%.",

     "At h = {{v2_deploy_h}}, the method's own imagination rollout length, epistemic is\n"
     "{{d1n_epi_over_alea_h100}}× better than aleatoric and still wrong by\n"
     "**{{d1n_epi_ratio_h100}}× [{{d1n_epi_ratio_ci_h100}}]**, with ±1σ coverage of\n"
     "{{d1n_epi_cov1_h100}}% [{{d1n_epi_cov1_ci_h100}}] where a calibrated Gaussian gives\n"
     "{{v3_cov_nominal1}}%. At one step it is **{{d1n_epi_ratio_h1}}×** out and\n"
     "{{d1n_epi_over_alea_h1}}× better than aleatoric; at h = {{v2_diag_h}} the two-term ratio is\n"
     "{{d1n_epi_over_alea_h368}}×. **The gap between the two uncertainty terms is itself\n"
     "horizon-dependent, which is why each figure above names its horizon.**"),

    # -- 6.4 --------------------------------------------------------------
    ("1.x 6.4 closing sentence: the ens5 figure it quotes back is the h=100 one",
     "So §6.2's \"our arms fail the same way at {{e5_ratio_h100}}×\" compares two instances of one "
     "architecture, not two architectures.",

     "So §6.2's \"our arms fail the same way at {{e5_ratio_h100}}× at h = {{v2_deploy_h}}\" compares "
     "two instances of one architecture, not two architectures."),

    # -- 6.6 --------------------------------------------------------------
    ("1.9 6.6: the ratio beside the sign count had no horizon of its own",
     "the epistemic term correlates positively with realised error on **{{b2_epi_npos_h368}} of "
     "{{b2_epi_ndim_h368}}** dimensions, matching the best aleatoric head here on the sign count, "
     "while being {{b2_epi_ratio_h368}}× overconfident.",

     "the epistemic term correlates positively with realised error on **{{b2_epi_npos_h368}} of "
     "{{b2_epi_ndim_h368}}** dimensions, matching the best aleatoric head here on the sign count, "
     "while being {{b2_epi_ratio_h368}}× overconfident at h = {{v2_diag_h}}."),

    ("1.4 6.6 cross-reference: the abstract and 13 quote h=100, not h=368",
     "§6.2 quotes {{d1n_epi_ratio_h368}}× for the same ratio at n_independent = {{d1n_nind}}, "
     "which is the figure the abstract and §13 use.",

     "§6.2 quotes {{d1n_epi_ratio_h368}}× for the same ratio at h = {{v2_diag_h}} and "
     "n_independent = {{d1n_nind}}. The figure the abstract and §13 use is neither of those: it is "
     "{{d1n_epi_ratio_h100}}× at h = {{v2_deploy_h}}, on the same {{d1n_nind}} trajectories."),

    # The 6.6 table's two P columns are both h=368 and the table never said so.
    ("1.x 6.6 table: the permutation columns are h=368 and the header did not say so",
     "| model | σ variation across inputs (CoV) | dims with r(σ, error) > 0, out-of-sample | "
     "perm P, out-of-sample | perm P, in-sample |",

     "| model | σ variation across inputs (CoV) | dims with r(σ, error) > 0 at "
     "h={{v2_diag_h}}, out-of-sample | perm P at h={{v2_diag_h}}, out-of-sample | "
     "perm P at h={{v2_diag_h}}, in-sample |"),

    ("1.x 6.5: the four permutation P-values it quotes are all h=368",
     "Under the trajectory permutation test of §6.6 those counts give P = "
     "{{perm_oos_faithA_p_h368}} and {{perm_oos_nll_p_h368}} out of sample, "
     "{{perm_ins_faithA_p_h368}} and {{perm_ins_nll_p_h368}} in sample.",

     "Under the trajectory permutation test of §6.6, at h = {{v2_diag_h}}, those counts give P = "
     "{{perm_oos_faithA_p_h368}} and {{perm_oos_nll_p_h368}} out of sample, "
     "{{perm_ins_faithA_p_h368}} and {{perm_ins_nll_p_h368}} in sample."),

    ("1.x 6.6 arena sentence: its counts are h=368",
     "It is not the only arena, and for the released checkpoint's aleatoric head it is not the "
     "most informative one: at n_independent = {{relale_all_nind}} over all ten episodes that head "
     "is {{relale_all_pos_h368}}/{{perm_all_relale_ndim_h368}} — negatively correlated with error "
     "on *every* dimension — against {{relale_oos_pos_h368}}/{{perm_all_relale_ndim_h368}} here.",

     "It is not the only arena, and for the released checkpoint's aleatoric head it is not the "
     "most informative one: at h = {{v2_diag_h}} and n_independent = {{relale_all_nind}} over all "
     "ten episodes that head is {{relale_all_pos_h368}}/{{perm_all_relale_ndim_h368}} — negatively "
     "correlated with error on *every* dimension — against "
     "{{relale_oos_pos_h368}}/{{perm_all_relale_ndim_h368}} here."),

    ("1.x 6.6 worst-cell paragraph: name the horizon the move is measured at",
     "It moves from {{perm_ins_armB_binom_h368}} to {{perm_ins_armB_p_h368}} — a factor of about "
     "{{perm_worst_factor}} — because under a null that preserves the dependence, a random "
     "re-pairing already yields {{perm_worst_null}} of {{perm_ins_armB_ndim_h368}} dimensions "
     "positive on average. Observing {{perm_ins_armB_npos_h368}} of {{perm_ins_armB_ndim_h368}} "
     "against that null is close to unremarkable.",

     "At h = {{v2_diag_h}} it moves from {{perm_ins_armB_binom_h368}} to "
     "{{perm_ins_armB_p_h368}} — a factor of about {{perm_worst_factor}} — because under a null "
     "that preserves the dependence, a random re-pairing already yields {{perm_worst_null}} of "
     "{{perm_ins_armB_ndim_h368}} dimensions positive on average. Observing "
     "{{perm_ins_armB_npos_h368}} of {{perm_ins_armB_ndim_h368}} against that null is close to "
     "unremarkable."),

    ("1.x 6.6 null-mean sentence: 'long' and 'short' horizon named as numbers",
     "At long horizon the shared forecast-depth trend lifts the null to "
     "{{perm_all_epi_null_h128}} of 45, so a count of 45 is close to what chance alone delivers; "
     "at short horizon the null sits near {{perm_all_epi_null_h1}} and the same count is genuinely "
     "surprising.",

     "At long horizon the shared forecast-depth trend lifts the null to "
     "{{perm_all_epi_null_h128}} of 45 at h = 128, so a count of 45 is close to what chance alone "
     "delivers; at h = 1 the null sits near {{perm_all_epi_null_h1}} and the same count is "
     "genuinely surprising."),

    # -- 6.7 --------------------------------------------------------------
    ("1.x 6.7: the counter's full-rollout figure is h=368",
     "**Disagreement wins at every horizon tested.** The counter reaches {{d2b_idx_h368}} over the "
     "full rollout against disagreement's {{d2b_epi_h368}}, and the index leads in "
     "{{d2b_n_index_wins}} of {{d2b_n_horizons_tested}} horizons.",

     "**Disagreement wins at every horizon tested.** Over the full h = {{v2_diag_h}} rollout the "
     "counter reaches {{d2b_idx_h368}} against disagreement's {{d2b_epi_h368}}, and the index "
     "leads in {{d2b_n_index_wins}} of {{d2b_n_horizons_tested}} horizons."),

    # -- 10 ---------------------------------------------------------------
    ("1.x 10 first lesson: the two ratios are both h=100 and said so only obliquely",
     "But it is too small to be an interval by a wide margin — {{d1n_epi_ratio_h100}}× "
     "[{{d1n_epi_ratio_ci_h100}}] on the released checkpoint and {{e5_ratio_h100}}× "
     "[{{e5_ratio_ci_h100}}] on the ensemble-5 arms we trained, both at the horizon the method "
     "itself rolls out over — and a risk gate or safety margin that reads σ as a distance is not "
     "supported at any horizon, on either.",

     "But it is too small to be an interval by a wide margin — at h = {{v2_deploy_h}}, the horizon "
     "the method itself rolls out over, {{d1n_epi_ratio_h100}}× [{{d1n_epi_ratio_ci_h100}}] on the "
     "released checkpoint and {{e5_ratio_h100}}× [{{e5_ratio_ci_h100}}] on the ensemble-5 arms we "
     "trained — and a risk gate or safety margin that reads σ as a distance is not supported at "
     "any horizon, on either."),

    ("1.5 10 sixth lesson: quote the deployment horizon a practitioner reads for",
     "The predicted variance has an optimum at zero under the implemented one, which is why the "
     "released checkpoint's σ is {{d1n_alea_ratio_h368}}× smaller than its own error.",

     "The predicted variance has an optimum at zero under the implemented one, which is why the "
     "released checkpoint's σ is {{d1n_alea_ratio_h100}}× smaller than its own error at "
     "h = {{v2_deploy_h}}, and {{d1n_alea_ratio_h368}}× at h = {{v2_diag_h}}."),

    # -- 12 ---------------------------------------------------------------
    ("1.6 12: the ens5 headline is now the h=100 one",
     "They reproduce the *direction* of §6.7's finding in {{e5_lead_cells}} of "
     "{{e5_total_cells}} seed-horizon cells and the *calibration* failure at {{e5_ratio_h368}}× — "
     "but the pre-registered rule governing the replication returns **{{e5_verdict}}**,",

     "They reproduce the *direction* of §6.7's finding in {{e5_lead_cells}} of "
     "{{e5_total_cells}} seed-horizon cells and the *calibration* failure at {{e5_ratio_h100}}× at "
     "h = {{v2_deploy_h}} ({{e5_ratio_h368}}× at h = {{v2_diag_h}}) — but the pre-registered rule "
     "governing the replication returns **{{e5_verdict}}**,"),

    # -- 13 ---------------------------------------------------------------
    ("1.2 13: the two-term ratio must be the one at the horizon the sentence scopes to",
     "The epistemic term the method actually penalises with is better by a factor of "
     "{{d1n_epi_over_alea_h368}} and still {{d1n_epi_ratio_h100}}× [{{d1n_epi_ratio_ci_h100}}] "
     "overconfident where it is used.",

     "The epistemic term the method actually penalises with is better by a factor of "
     "{{d1n_epi_over_alea_h100}} and still {{d1n_epi_ratio_h100}}× [{{d1n_epi_ratio_ci_h100}}] "
     "overconfident where it is used — both figures at h = {{v2_deploy_h}}."),

    ("1.x 13: the all-episodes dimension count is h=368",
     "The released checkpoint's *aleatoric* head does the opposite, ranking error inversely on "
     "every one of {{perm_all_relale_ndim_h368}} dimensions over all ten episodes and at chance on "
     "the held-out pair alone",

     "The released checkpoint's *aleatoric* head does the opposite, ranking error inversely at "
     "h = {{v2_diag_h}} on every one of {{perm_all_relale_ndim_h368}} dimensions over all ten "
     "episodes and at chance on the held-out pair alone"),

    # -- 5 ----------------------------------------------------------------
    ("1.x 5: the hold-last floor is an h=368 figure and 'the same cell' did not say so",
     "*Against a baseline, because neither number means anything without one.* The hold-last "
     "floor — predicting that nothing changes — scores **{{floor_h368}}** in the same cell.",

     "*Against a baseline, because neither number means anything without one.* The hold-last "
     "floor — predicting that nothing changes — scores **{{floor_h368}}** in the same "
     "h = {{v2_diag_h}} cell."),

    # -- Appendix F -------------------------------------------------------
    ("1.7 Appendix F: the scale verdict quoted h=368 in a paper anchored to h=100",
     "**Not supported as a scale**: {{d1n_epi_ratio_h368}}× overconfident, repairable per horizon "
     "(§6.8)",

     "**Not supported as a scale**: {{d1n_epi_ratio_h100}}× overconfident at h = "
     "{{v2_deploy_h}}, the method's own rollout length, and {{d1n_epi_ratio_h368}}× at the "
     "h = {{v2_diag_h}} diagnostic horizon; repairable per horizon (§6.8)"),

    ("1.x Appendix F: the sign count in the same cell is h=368",
     "**Weaker per-dimension than we first reported**: the "
     "{{d1n_epi_npos_h368}}-of-{{d1n_epi_ndim_h368}} sign count gives a permutation P of "
     "{{perm_oos_epi_p_h368}} (out-of-sample) and {{perm_ins_epi_p_h368}} (in-sample), and no cell "
     "survives multiplicity correction (§6.6).",

     "**Weaker per-dimension than we first reported**: at h = {{v2_diag_h}} the "
     "{{d1n_epi_npos_h368}}-of-{{d1n_epi_ndim_h368}} sign count gives a permutation P of "
     "{{perm_oos_epi_p_h368}} (out-of-sample) and {{perm_ins_epi_p_h368}} (in-sample), and no cell "
     "survives multiplicity correction (§6.6)."),

    # =====================================================================
    # PART 2 -- the gaps the re-anchoring opened.
    # =====================================================================

    # -- 2.1: the h=100 row of 6.7's main table --------------------------
    ("2.1a 6.7 main table: add the h=100 row the horizon grid declares",
     "| 32 | {{d2b_idx_h32}} {{d2b_idx_ci_h32}} | **{{d2b_epi_h32}}** {{d2b_epi_ci_h32}} | "
     "{{d2b_par_h32}} {{d2b_par_ci_h32}} | {{d2p_diff_h32}} {{d2p_ci_h32}} |\n"
     "| 128 |",

     "| 32 | {{d2b_idx_h32}} {{d2b_idx_ci_h32}} | **{{d2b_epi_h32}}** {{d2b_epi_ci_h32}} | "
     "{{d2b_par_h32}} {{d2b_par_ci_h32}} | {{d2p_diff_h32}} {{d2p_ci_h32}} |\n"
     "| **{{v2_deploy_h}}** | {{d2b_idx_h100}} {{d2b_idx_ci_h100}} | **{{d2b_epi_h100}}** "
     "{{d2b_epi_ci_h100}} | {{d2b_par_h100}} {{d2b_par_ci_h100}} | {{d2p_diff_h100}} "
     "{{d2p_ci_h100}} |\n"
     "| 128 |"),

    ("2.1b 6.7: two horizons now have overlapping marginal intervals, not one",
     "The distinction matters at exactly one place. At {{d2p_overlap_h}} the marginal intervals "
     "*do* overlap — it is the horizon where the counter is strongest ({{d2b_idx_h128}}) and the "
     "margin narrowest — and an earlier draft of this paper wrongly asserted that they never do. "
     "The paired difference there is {{d2p_diff_h128}} {{d2p_ci_h128}}, which excludes zero, but "
     "only just: {{d2p_narrowest_lo}} is the smallest lower bound in the table and we would not "
     "rest anything on that horizon alone.",

     "The distinction matters at {{d2p_n_overlap}} of the {{d2p_n_horizons}} horizons. At "
     "{{d2p_overlap_h}} the marginal intervals *do* overlap, and an earlier draft of this paper "
     "wrongly asserted that they never do. {{d2b_idx_strongest_h}} is where the counter is "
     "strongest ({{d2b_idx_h128}}) and the margin narrowest: the paired difference there is "
     "{{d2p_diff_h128}} {{d2p_ci_h128}}, which excludes zero, but only just — "
     "{{d2p_narrowest_lo}} is the smallest lower bound in the table and we would not rest anything "
     "on that horizon alone. At h = {{v2_deploy_h}} the paired difference is {{d2p_diff_h100}} "
     "{{d2p_ci_h100}}, which also excludes zero.",),

    # -- 2.1: r_dd in a table rather than only in prose -------------------
    ("2.1c 6.7: r_dd per horizon, in a table rather than only in prose",
     "Two qualifications a reader should carry away with that. The within-rollout effect is "
     "**materially smaller than the pooled figure** — {{a2_rdd}} against {{a2_r_pooled}} — so a "
     "practitioner should expect disagreement to separate *rollouts* better than it separates "
     "*moments within a rollout*. And it is **not established at short horizon**: r_dd's interval "
     "excludes zero at {{a2_excl_h}} and spans zero at {{a2_spans_h}}, where too few steps exist "
     "to demean against. That inverts the shape one might expect and we report it as measured.",

     "**Per horizon, on the same {{a2_nind}} trajectories and the same cluster bootstrap:**\n"
     "\n"
     "| h | r_dd, double-demeaned | 95% CI | excludes zero |\n"
     "|---|---|---|---|\n"
     "| 1 | — | — | — |\n"
     "| 8 | {{a2_rdd_h8}} | {{a2_rdd_ci_h8}} | no |\n"
     "| 32 | {{a2_rdd_h32}} | {{a2_rdd_ci_h32}} | no |\n"
     "| **{{v2_deploy_h}}** | **{{a2_rdd_h100}}** | **{{a2_rdd_ci_h100}}** | **yes** |\n"
     "| 128 | {{a2_rdd_h128}} | {{a2_rdd_ci_h128}} | yes |\n"
     "| {{v2_diag_h}} | {{a2_rdd_h368}} | {{a2_rdd_ci_h368}} | yes |\n"
     "\n"
     "*(h = 1 has one forecast step per trajectory, so there is nothing within a rollout to demean "
     "against and r_dd is undefined rather than zero.)*\n"
     "\n"
     "Two qualifications a reader should carry away with that. The within-rollout effect is "
     "**materially smaller than the pooled figure** — {{a2_rdd}} against {{a2_r_pooled}} — so a "
     "practitioner should expect disagreement to separate *rollouts* better than it separates "
     "*moments within a rollout*. And it is **not established at short horizon**: r_dd's interval "
     "excludes zero at {{a2_excl_h}} and spans zero at {{a2_spans_h}}, where too few steps exist "
     "to demean against. That inverts the shape one might expect and we report it as measured. At "
     "the deployment horizon it is established, at {{a2_rdd_h100}} {{a2_rdd_ci_h100}}."),

    # -- 2.2: 5's framing ------------------------------------------------
    ("2.2a 5 header claim: the rule's horizon is the diagnostic one, not 'deploys at'",
     "**Claim under test.** Training the dynamics model on its own autoregressive rollouts beats "
     "training it with teacher forcing, at the horizons the method deploys at.",

     "**Claim under test.** Training the dynamics model on its own autoregressive rollouts beats "
     "training it with teacher forcing, at long forecast horizons.\n"
     "\n"
     "**Which horizon, stated before the result.** The rule below is anchored at "
     "h = {{v2_diag_h}}, which §3.1 identifies as the upstream's **open-loop diagnostic** length "
     "and explicitly not a deployment horizon. That is the horizon the rule was committed over and "
     "the horizon its verdict is returned at; we do not re-anchor a discharged rule. But the "
     "paper's own deployment horizon is h = {{v2_deploy_h}}, so the same comparison is reported "
     "there too, below, and the two differ in size."),

    ("2.2b 5: report the A/B result at the deployment horizon as well",
     "*The out-of-sample effect size, over {{d1_seeds}} seeds.* Autoregressive training reaches "
     "**{{d1_A_mean}} ± {{d1_A_sd}}** against teacher forcing's **{{d1_B_mean}} ± {{d1_B_sd}}** "
     "(standard deviation over seeds, `ddof=1`) — a factor of **{{d1_ratio}}×**.",

     "*The out-of-sample effect size, over {{d1_seeds}} seeds.* At h = {{v2_diag_h}}, the "
     "horizon M-23 is stated over, autoregressive training reaches **{{d1_A_mean}} ± "
     "{{d1_A_sd}}** against teacher forcing's **{{d1_B_mean}} ± {{d1_B_sd}}** (standard deviation "
     "over seeds, `ddof=1`) — a factor of **{{d1_ratio}}×**.\n"
     "\n"
     "**At the deployment horizon the same comparison is smaller, and we report it rather than "
     "leaving the reader to assume the headline transfers.** At h = {{v2_deploy_h}} — the "
     "method's own imagination rollout length, and the horizon everything in §6 is anchored to — "
     "the same three seeds give **{{d1_A_mean_h100}} ± {{d1_A_sd_h100}}** against "
     "**{{d1_B_mean_h100}} ± {{d1_B_sd_h100}}**, a factor of **{{d1_ratio_h100}}×**. The direction "
     "is the same and the margin is roughly half. **M-23's verdict stands as returned at "
     "h = {{v2_diag_h}}**; this figure is reported beside it and discharges nothing."),

    # -- 2.3: the permutation family ------------------------------------
    ("2.3 6.2: the permutation column now has a test at every horizon",
     "The last column of the table above gives permutation P-values over whole trajectories, not "
     "binomial ones, computed on the same {{perm_all_nind}} trajectories as the counts beside "
     "them; §6.6 explains why a binomial null is inadmissible here and how far it was wrong. These "
     "are five tests on one family and none survives Holm–Bonferroni across the arena's "
     "{{perm_all_holm_n}} cells — the smallest is {{perm_all_holm_min_cell}} at "
     "{{perm_all_holm_min_p}} against a threshold of {{perm_all_holm_thr}}. Read the column as a "
     "consistency check on direction, not as five independent findings.",

     "The last column of the table above gives permutation P-values over whole trajectories, not "
     "binomial ones, computed on the same {{perm_all_nind}} trajectories as the counts beside "
     "them; §6.6 explains why a binomial null is inadmissible here and how far it was wrong. "
     "**h = {{v2_deploy_h}} carries the abstract, so it is tested rather than left blank**: an "
     "earlier draft ran the permutation test on the pre-revision five-horizon grid and printed "
     "\"—\" in the one row the headline rests on. These are {{perm_n_tests_col_word}} tests on one "
     "family and none survives Holm–Bonferroni across the arena's {{perm_all_holm_n}} cells — the "
     "smallest is {{perm_all_holm_min_cell}} at {{perm_all_holm_min_p}} against a threshold of "
     "{{perm_all_holm_thr}}. Read the column as a consistency check on direction, not as "
     "{{perm_n_tests_col_word}} independent findings."),

    # =====================================================================
    # PART 3 -- the outright errors.
    # =====================================================================

    ("3.1 6.8: the two largest deviations are not opposite, and not both at one horizon",
     "The two largest deviations are both at h={{d3_worst_h}} on the aleatoric term, in opposite "
     "directions ({{d3_worst_cov}}% and {{d3_second_cov}}%), which is a mild sign that the fitted "
     "multiplier is least stable at that horizon.",

     "The two largest deviations are both on the {{d3_second_q}} term and {{d3_top2_same_side}} "
     "target — {{d3_worst_cov}}% at h={{d3_worst_h}} and {{d3_second_cov}}% at "
     "h={{d3_second_h}} — so the fitted multiplier is mildly **conservative** at the long "
     "horizons rather than unstable in both directions. An earlier draft described them as "
     "opposite; they are not, and the `sign` family of checks now covers this sentence."),

    ("3.2 6.7: a wrapped line beginning with a pipe was read as a LaTeX table",
     "M-45's threshold, fixed before the statistic was computed, was that this interval exclude "
     "zero; the rule's minimum detectable effect at this sample size is |r_dd| ≥ {{p1_m45_mde}}, "
     "estimated by a dilution study which put the detection threshold between a true effect of "
     "{{p1_m45_undetected}} (not detected) and {{p1_m45_detected}} (detected). The observed effect "
     "is comfortably above it.",

     "M-45's threshold, fixed before the statistic was computed, was that this interval exclude "
     "zero. The rule's minimum detectable effect at this sample size is an absolute r_dd of "
     "{{p1_m45_mde}} or more, estimated by a dilution study which put the detection threshold "
     "between a true effect of {{p1_m45_undetected}} (not detected) and {{p1_m45_detected}} "
     "(detected). The observed effect is comfortably above it."),

    ("3.3 4: 'without exception' is false — Appendix E puts two of the eight in CPU reach",
     "The eight we did not test are, without exception, claims about **policy learning or "
     "hardware**: zero-shot transfer, the sample-efficiency result, the comparisons against SHAC "
     "and Dreamer, generality across robot morphologies, and the core claim that penalising "
     "rewards by disagreement improves the learned policy. Each needs a simulator, an RL loop and "
     "an ANYmal; this work trains no policy at all.",

     "Of the eight we did not test, **six are claims about policy learning or hardware**: "
     "zero-shot transfer, the sample-efficiency result, the comparisons against SHAC and Dreamer, "
     "generality across robot morphologies, and the core claim that penalising rewards by "
     "disagreement improves the learned policy. Each of those needs a simulator, an RL loop and an "
     "ANYmal; this work trains no policy at all. **The remaining two need none of that and we "
     "still did not run them**: the M/N configuration sweep and the MLP/RSSM/transformer baseline "
     "comparison are within reach of the CPU budget this project already spent, and Appendix E "
     "prices both. They are unrun for want of time, not for want of hardware, and saying so is the "
     "honest form of this paragraph — an earlier draft claimed all eight were blocked \"without "
     "exception\", which Appendix E contradicts two rows later."),

    ("3.4 Appendix B: the parts must sum to the total",
     "Training all {{rt_runs}} runs takes **{{rt_hours}} hours** of recorded wall clock on two "
     "CPU cores: {{rt_hours_10k}} hours for the {{rt_runs_10k}} runs at 10,000 iterations and "
     "{{rt_hours_short}} for the remaining {{rt_runs_short}} at 2,500.",

     "Training all {{rt_runs}} runs takes **{{rt_hours}} hours** of recorded wall clock on two "
     "CPU cores: {{rt_hours_10k}} hours for the {{rt_runs_10k}} runs at 10,000 iterations and "
     "{{rt_hours_short}} for the remaining {{rt_runs_short}} at 2,500. (Those were rounded to "
     "whole hours in an earlier draft, where 20 + 27 did not make 46; the `arithmetic` check now "
     "asserts that a stated total equals the sum of its stated parts.)"),

    ("3.7 10: quote h=1's interval from the same artifact 6.7's table quotes it from",
     "At one forecast step it ranks whole rollouts almost perfectly — {{a2_h1_r}} {{a2_h1_ci}} "
     "across the {{a2_h1_npoints}} trajectories,",

     "At one forecast step it ranks whole rollouts almost perfectly — {{d2_epi_h1}} "
     "{{d2_epi_ci_h1}} across the {{a2_h1_npoints}} trajectories,"),

    ("3.8 Appendix F: five depth controls in total, not one plus five further",
     "beats the forecast-index counter at every horizon, keeps {{d2b_par_all}} after partialling "
     "that counter out, and survives five further controls on forecast depth plus a sixth on "
     "trajectory difficulty",

     "beats the forecast-index counter at every horizon and survives "
     "{{d2r_ncontrols}} controls on forecast depth — the linear partial that keeps "
     "{{d2b_par_all}}, and four harder ones — plus a sixth on trajectory difficulty"),

    # =====================================================================
    # PART 4 -- scoping.
    # =====================================================================

    ("4.1 contributions: 2 credits Lu et al. with assessing calibration of this family",
     "- **The first calibration measurement of either uncertainty output.** Both are overconfident "
     "by one to four orders of magnitude, with intervals over independent trajectories at every "
     "horizon; and the aleatoric collapse is derived analytically from the implemented objective "
     "rather than observed (§6.2, §6.3).",

     "- **The first calibration measurement of either uncertainty output of this released "
     "checkpoint.** Lu et al. (2022) assess calibration for this family of penalties on models "
     "they train themselves (§2); we measure coverage against a nominal, on a checkpoint its "
     "authors deployed. Both outputs are overconfident by one to four orders of magnitude, with "
     "intervals over independent trajectories at every horizon; and the aleatoric collapse is "
     "derived analytically from the implemented objective rather than observed (§6.2, §6.3)."),

    ("4.2 contributions: 6.10 is the strongest new result and had no bullet",
     "- **A working repair**: one multiplier per horizon, fitted on one held-out episode and\n"
     "  scored on the other, restores nominal coverage where a global multiplier does not (§6.8).",

     "- **The mechanism tested rather than asserted, under a rule committed before the runs.** An "
     "ensemble of {{r2_n_indep}} independently-initialised full models, sharing nothing, is "
     "{{m44_ratio_gain}}× better calibrated than the shared-trunk arms against a pre-registered "
     "minimum detectable effect of {{m44_mde_ratio}}×. The decomposition says what that is made "
     "of: σ larger by {{r2_sigma_x_h100}}×, {{r2_from_sigma_h100}}% of the improvement at "
     "h = {{v2_deploy_h}}, reversing to {{r2_from_acc_h368}}% from accuracy at "
     "h = {{v2_diag_h}} (§6.10).\n"
     "- **A working repair**: one multiplier per horizon, fitted on one held-out episode and\n"
     "  scored on the other, restores nominal coverage where a global multiplier does not (§6.8)."),

    ("4.3 12: capacity is a third non-isolated factor and 12 named only two",
     "**The independent-ensemble comparison bounds the trunk-sharing effect rather than isolating "
     "it.** §6.10's contrast trains five models at five seeds and scores them together. "
     "Independently-seeded runs differ in **both** initialisation *and* data ordering, whereas the "
     "shared-trunk heads differ only in head initialisation. So the comparison conflates "
     "trunk-sharing with data-order diversity.",

     "**The independent-ensemble comparison bounds the trunk-sharing effect rather than isolating "
     "it, on three axes.** §6.10's contrast trains five models at five seeds and scores them "
     "together. Independently-seeded runs differ in **both** initialisation *and* data ordering, "
     "whereas the shared-trunk heads differ only in head initialisation. They also differ in "
     "**capacity**: the independent arm carries {{v1_cap_indep}} state-pathway parameters against "
     "the shared-trunk arm's {{v1_cap_shared}}, a factor of {{v1_cap_ratio}}, because each member "
     "brings its own trunk. Greater capacity can inflate σ as well as shrink error, and σ is the "
     "column the mechanism claim rests on — §6.10's decomposition separates the σ gain from the "
     "accuracy gain, but it does not separate capacity from independence. The clean version would "
     "be five trunks at one fifth the width each, matched on total capacity; that is a different "
     "architecture and a different training run, and it is out of scope here. So the comparison "
     "conflates trunk-sharing with data-order diversity and with capacity."),

    # =====================================================================
    # A second pass over what the sweep still flagged after the first.
    # These are not in the brief's list: the scanner found them.
    # =====================================================================

    ("sweep abstract: 'that same horizon' is a back-reference, not a label",
     "The per-member σ, which the method computes and discards, is worse at that same "
     "horizon by a further factor of {{d1n_epi_over_alea_h100}}, and we derive why: "
     "the implemented objective's optimum is σ = 0.",

     "The per-member σ, which the method computes and discards, is worse again at\n"
     "h = {{v2_deploy_h}} by a further factor of {{d1n_epi_over_alea_h100}}, and we derive why:\n"
     "the implemented objective's optimum is σ = 0."),

    ("sweep 6.7: r_dd at the deployment horizon, named",
     "At the deployment horizon it is established, at {{a2_rdd_h100}} {{a2_rdd_ci_h100}}.",
     "At h = {{v2_deploy_h}} it is established, at {{a2_rdd_h100}} {{a2_rdd_ci_h100}}."),

    # The sweep's own find, and a real one: a range across six horizons was
    # written as the h=1 and h=8 values, and h=368's 1.49 falls below it.
    ("sweep 6.10: the sigma-gain range did not span every horizon it claimed to",
     "σ is larger by {{r2_sigma_x_h1}}–{{r2_sigma_x_h8}}× at every horizon, which is the "
     "direction trunk-sharing predicts, and at h = {{v2_deploy_h}} it is "
     "**{{r2_from_sigma_h100}}%** of the improvement.",

     "σ is larger at every horizon — by {{r2_sigma_x_lo}}× at its weakest "
     "(h = {{r2_sigma_x_lo_h}}) and {{r2_sigma_x_hi}}× at its strongest "
     "(h = {{r2_sigma_x_hi_h}}) — which is the direction trunk-sharing predicts, and at "
     "h = {{v2_deploy_h}} it is {{r2_sigma_x_h100}}×, **{{r2_from_sigma_h100}}%** of the "
     "improvement. An earlier draft gave that range as the h = 1 and h = 8 values, which do not "
     "span it."),

    # =====================================================================
    # A third pass: the abstract's word budget. Horizon labelling costs words
    # and numerals, and the abstract went to 279 words against a 250 cap that
    # exists because an earlier version of it was 650. Trim rather than raise.
    # =====================================================================

    ("abstract: trim to the budget, keeping every horizon label",
     "**The base paper's central training claim reproduces.** Autoregressive training beats "
     "teacher forcing by a factor of {{d1_ratio}} on the reference's own relative-L1 error at "
     "h = {{v2_diag_h}}, the horizon its pre-registered rule names, and by {{d1_ratio_h100}} at "
     "h = {{v2_deploy_h}} — on held-out episodes, under a rule committed to git before the runs "
     "that tested it.",

     "**The base paper's central training claim reproduces.** On held-out episodes, under a rule\n"
     "committed to git before the runs that tested it, autoregressive training beats teacher\n"
     "forcing by a factor of {{d1_ratio}} on the reference's own relative-L1 error at\n"
     "h = {{v2_diag_h}}, the horizon that rule names, and {{d1_ratio_h100}} at\n"
     "h = {{v2_deploy_h}}."),

    ("abstract: the same trim on the uncertainty paragraph",
     "**Neither uncertainty output the follow-up adds is usable as an interval.** At "
     "h = {{v2_deploy_h}}, the horizon its own imagination rollouts run to, the ensemble "
     "disagreement it penalises rewards with is {{d1n_epi_ratio_h100}}× smaller than the realised "
     "error, and {{d1n_epi_cov1_h100}}% of outcomes fall inside ±1σ where {{v3_cov_nominal1}}% is "
     "calibrated. The per-member σ, which the method computes and discards, is worse again at "
     "h = {{v2_deploy_h}} by a further factor of {{d1n_epi_over_alea_h100}}, and we derive why: "
     "the implemented objective's optimum is σ = 0.",

     "**Neither uncertainty output the follow-up adds is usable as an interval.** At\n"
     "h = {{v2_deploy_h}}, the horizon its own imagination rollouts run to, the ensemble\n"
     "disagreement it penalises rewards with is {{d1n_epi_ratio_h100}}× smaller than the realised\n"
     "error: {{d1n_epi_cov1_h100}}% of outcomes fall inside ±1σ where {{v3_cov_nominal1}}% is\n"
     "calibrated. The per-member σ, which the method computes and discards, is a further\n"
     "{{d1n_epi_over_alea_h100}}× worse there, and we derive why: the implemented objective's\n"
     "optimum is σ = 0."),

    ("abstract: the ranking paragraph, tightened",
     "**As a ranking it survives adversarial testing.** It beats the forecast step index "
     "— a free counter neither paper ran — at every horizon, and with both the rollout and "
     "the forecast depth held constant it still correlates {{a2_rdd}} with realised error, so it "
     "is not merely reporting which episode is hard.",

     "**As a ranking it survives adversarial testing.** It beats the forecast step index — a free\n"
     "counter neither paper ran — at every horizon, and over the full rollout, with both the\n"
     "rollout and the forecast depth held constant, still correlates {{a2_rdd}} with realised\n"
     "error. It is not merely reporting which episode is hard."),

    ("abstract: the repair paragraph, tightened",
     "**The interval is repairable.** One multiplier per horizon, fitted on one held-out episode "
     "and scored on the other, restores nominal coverage on every held-out cell; a single global "
     "multiplier manages {{d3_epi_const_ok}} of them.",

     "**The interval is repairable.** One multiplier per horizon, fitted on one held-out episode\n"
     "and scored on the other, restores nominal coverage on every held-out cell; one global\n"
     "multiplier manages {{d3_epi_const_ok}}."),


    # =====================================================================
    # A fourth pass: the abstract is still 17 words over. Horizon labels are
    # not negotiable -- they are the point of this revision -- so the words
    # come out of the prose around them.
    # =====================================================================

    ("abstract: opening sentence, tightened",
     "We reproduce the proprioceptive dynamics model of Li, Krause and Hutter (*Robotic World "
     "Model*, arXiv:2501.10100v1) and its uncertainty-aware follow-up (arXiv:2504.16680v1) from "
     "scratch on CPU, checking it against the released reference at the gradient level first.",

     "We rebuild the proprioceptive dynamics model of Li, Krause and Hutter (*Robotic World\n"
     "Model*, arXiv:2501.10100v1) and its uncertainty-aware follow-up (arXiv:2504.16680v1) from\n"
     "scratch on CPU, checked against the released reference at gradient level."),

    ("abstract: training paragraph, tightened",
     "**The base paper's central training claim reproduces.** On held-out episodes, under a rule "
     "committed to git before the runs that tested it, autoregressive training beats teacher "
     "forcing by a factor of {{d1_ratio}} on the reference's own relative-L1 error at "
     "h = {{v2_diag_h}}, the horizon that rule names, and {{d1_ratio_h100}} at "
     "h = {{v2_deploy_h}}.",

     "**The base paper's central training claim reproduces.** Under a rule committed to git\n"
     "before the runs that tested it, autoregressive training beats teacher forcing on held-out\n"
     "episodes by {{d1_ratio}}× on the reference's own relative-L1 error at h = {{v2_diag_h}}, the\n"
     "horizon the rule names, and {{d1_ratio_h100}}× at h = {{v2_deploy_h}}."),

    ("abstract: ranking paragraph, tightened again",
     "**As a ranking it survives adversarial testing.** It beats the forecast step index — a free "
     "counter neither paper ran — at every horizon, and over the full rollout, with both the "
     "rollout and the forecast depth held constant, still correlates {{a2_rdd}} with realised "
     "error. It is not merely reporting which episode is hard.",

     "**As a ranking it survives adversarial testing.** It beats the forecast step index — a free\n"
     "counter neither paper ran — at every horizon, and with the rollout and the forecast depth\n"
     "both held constant still correlates {{a2_rdd}} with realised error over the full rollout:\n"
     "not merely a report of which episode is hard."),

    ("abstract: closing line, tightened",
     "No number here is typed; every claim this work has retracted on its own evidence is kept in "
     "the record (§9).",

     "No number here is typed, and every claim this work has retracted is kept in the record\n"
     "(§9)."),

    # =====================================================================
    # PART 5 -- what the four new check kinds asked for once they existed.
    # =====================================================================

    ("C14: the abstract's last horizon-unscoped figure",
     "The per-member σ, which the method computes and discards, is a further "
     "{{d1n_epi_over_alea_h100}}× worse there, and we derive why: the implemented objective's "
     "optimum is σ = 0.",

     "The per-member σ, which the method computes and discards, is a further\n"
     "{{d1n_epi_over_alea_h100}}× worse at h = {{v2_deploy_h}}, and we derive why: the\n"
     "implemented objective's optimum is σ = 0."),

    ("C16: appendix D enumerates the check kinds the checker registers, generated",
     "**The check kinds.** `scripts/check_comparative_claims.py` verifies {{cc_n}} claims across "
     "{{cc_kinds}} kinds: *overlap* (two intervals do or do not overlap), *extremum* (a named cell "
     "is the max or min of its family), *sign* (a stated rise or fall matches the direction of the "
     "difference), *orders* (a stated count of orders of magnitude matches `round(log10(ratio))`), "
     "*cell* (a k-of-45 count is the arena and horizon the text names), *compare* (a stated "
     "ordering between two scalars), *relvar* (a stated ratio of relative variabilities), and "
     "*count-consistency* (one count asserted in several places, in words or numerals, agrees with "
     "the ledger everywhere).",

     "**The check kinds.** `scripts/check_comparative_claims.py` verifies {{cc_n}} claims across\n"
     "{{cc_kinds}} kinds: {{cc_kind_list}}.\n"
     "\n"
     "That list is generated from the checker's own registry rather than written here. It was\n"
     "written here, and §9 quoted a generated count beside it; the two had drifted seven kinds\n"
     "apart, inside the appendix whose subject is count consistency. The `kind-count` check now\n"
     "asserts that the number §9 claims, the number this list enumerates and the number the\n"
     "checker registers at run time are one number."),

    ("C17: 4 must not restate the quantifier it withdraws, and its counts are derived",
     "Of the eight we did not test, **six are claims about policy learning or hardware**: "
     "zero-shot transfer, the sample-efficiency result, the comparisons against SHAC and Dreamer, "
     "generality across robot morphologies, and the core claim that penalising rewards by "
     "disagreement improves the learned policy. Each of those needs a simulator, an RL loop and an "
     "ANYmal; this work trains no policy at all. **The remaining two need none of that and we "
     "still did not run them**: the M/N configuration sweep and the MLP/RSSM/transformer baseline "
     "comparison are within reach of the CPU budget this project already spent, and Appendix E "
     "prices both. They are unrun for want of time, not for want of hardware, and saying so is the "
     "honest form of this paragraph — an earlier draft claimed all eight were blocked \"without "
     "exception\", which Appendix E contradicts two rows later.",

     "Of the {{n_untested_word}} we did not test, **{{appE_n_sim_word}} are claims about policy\n"
     "learning or hardware**: zero-shot transfer, the sample-efficiency result, the comparisons\n"
     "against SHAC and Dreamer, generality across robot morphologies, and the core claim that\n"
     "penalising rewards by disagreement improves the learned policy. Those need a simulator, an\n"
     "RL loop and an ANYmal; this work trains no policy at all. **The remaining\n"
     "{{appE_n_cpu_word}} need none of that and we still did not run them**: the M/N configuration\n"
     "sweep and the MLP/RSSM/transformer baseline comparison are within reach of the CPU budget\n"
     "this project already spent, and Appendix E prices both. They are unrun for want of time, not\n"
     "for want of hardware. An earlier draft made this a universal claim about all\n"
     "{{n_untested_word}}, which Appendix E contradicts two rows later; the `scope-consistency`\n"
     "check now reads the quantifier here against the enumeration there, and both counts above are\n"
     "derived from those two tables rather than typed."),

    # =====================================================================
    # PART 4.4 -- the RWM-O -> RWM-U claim, re-verified against v3 itself.
    # Challenged as possibly describing two variants rather than one rename.
    # It is a rename: the names never co-occur in any version and only the
    # expansion of the letter changed.
    # =====================================================================

    ("4.4a references: state what the two names expand to, and that they never co-occur",
     "*Read at v1; now at {{v4_current}}, last revised {{v4_current_date}}. §5.1 and Eq. 4–5 "
     "keep their numbers there; every figure and appendix table has moved, and the model is "
     "renamed RWM-O to RWM-U. The crosswalk is in `results/original_paper_figures.json`.*",

     "*Read at v1; now at {{v4_current}}, last revised {{v4_current_date}}. §5.1 and Eq. 4–5\n"
     "keep their numbers there; every figure and appendix table has moved, and the model is\n"
     "renamed {{v4_name_v1}} to {{v4_name_v3}} — the same model, with the letter re-expanded from\n"
     "\"{{v4_exp_v1}}\" to \"{{v4_exp_v3}}\". The two names never co-occur: v1 uses\n"
     "{{v4_name_v1}} {{v4_name_n_v1}} times and no {{v4_name_v3}}, v3 the reverse. The crosswalk\n"
     "is in `results/original_paper_figures.json`.*"),

    ("4.4b Appendix F header: the same, stated once rather than asserted twice",
     "{{v2_fig_v1}} became {{v2_fig_v3}}, and the model was renamed RWM-O to RWM-U. All locations "
     "are recorded in `results/original_paper_figures.json`.*",

     "{{v2_fig_v1}} became {{v2_fig_v3}}, and the model was renamed {{v4_name_v1}} to\n"
     "{{v4_name_v3}}, which is a re-expansion of the letter (\"{{v4_exp_v1}}\" to\n"
     "\"{{v4_exp_v3}}\") rather than a second variant: no version of the paper contains both\n"
     "names. All locations, and the occurrence counts that establish that, are recorded in\n"
     "`results/original_paper_figures.json`.*"),

    # =====================================================================
    # PART 5 (cont.) -- appendix D's own record of what the self-test found in
    # the checker. It said "Two" and listed two; there are more, and the count
    # was typed inside the appendix whose subject is count consistency.
    # =====================================================================

    ("appendix D: the checker's own defect list, generated and no longer two",
     "**Two defects the self-test found in the checker itself.** Its first version applied a "
     "fixed corruption per kind — `expect: \"disjoint\"` to every overlap check — so for claims "
     "that already expected that value the corruption was a no-op, and two of eleven assertions "
     "reported as missed. They were not missed; nothing had been corrupted. Corruptions now "
     "invert relative to each claim's own expectation. Later, a label helper prefixed a horizon "
     "to family keys that were already model names, producing `h=teacher-forced armB`, which "
     "matched nothing and failed two checks whose extrema were correct. Both were defects in the "
     "checker rather than in the paper, and both surfaced because the checks were run rather than "
     "assumed.",

     "**{{cc_selfdefects_word}} defects the self-test has found in the checker itself**, rather\n"
     "than in the paper. Each surfaced because the checks were run rather than assumed, and the\n"
     "last two are the ones a reader should weigh, because both are failures of *coverage* rather\n"
     "than of arithmetic — an assertion that cannot fail, and a kind with no assertion attached,\n"
     "both of which read as protection and are not:{{cc_selfdefect_list}}\n"
     "\n"
     "Corruptions now invert relative to each claim's own expectation, every registered kind\n"
     "carries at least one claim, and every claim is corrupted on every build: {{cc_st_caught}} of\n"
     "{{cc_st_n}} caught against {{cc_n}} claims, with no exemptions. This list is generated from\n"
     "the checker rather than written here, so a fourth entry cannot be forgotten."),

    ("appendix D: what the widened placeholder gate now refuses",
     "None is a numeral. None appears in `results/paper_numbers.json`. Each was typed.",

     "None is a numeral. None appears in `results/paper_numbers.json`. Each was typed.\n"
     "\n"
     "**A sixth failure mode is not a relation at all, and it defeated the gate rather than\n"
     "evading it.** `build_paper.py` asserted that no `{{`-delimited placeholder survived\n"
     "substitution, and none did — while a sentence of §6.7 reached the PDF as an empty\n"
     "one-column table. The sentence contained `|r_dd|`, the line wrapped so that the pipe began a\n"
     "line, and the Markdown-to-LaTeX converter read a leading pipe as a table row. Every numeral\n"
     "in it was correct and provenanced. The gate now refuses three further shapes as well as\n"
     "unresolved braces: a pipe-led line with no separator row beneath it, a single-braced token\n"
     "that names a real key, and any key resolving to an empty or null value. The converter\n"
     "requires the separator row before it will build a table."),

    # =====================================================================
    # Cross-references into appendix D that the appendix's own rewrite made
    # stale. Both were typed counts of things the appendix enumerates.
    # =====================================================================

    ("9: the cross-reference into appendix D counted the checker's defects by hand",
     "**Appendix D gives the argument, the kinds, the self-test, two defects found in the checker "
     "itself, and the two exclusions from the numeric comparison.**",

     "**Appendix D gives the argument, the kinds, the self-test, the "
     "{{cc_selfdefects_lower}} defects the self-test has found in the checker itself, and the two "
     "exclusions from the numeric comparison.**"),

    ("appendix D: a sixth failure mode was added, so 'five' no longer counts them",
     "Five failure modes survive it, and all five occurred in this paper:",
     "Six failure modes survive it, and all six occurred in this paper. Five are relations "
     "between provenanced numbers; the sixth is not a relation at all and is set out after the "
     "list:"),

    # =====================================================================
    # The framing-retraction enumerations, generated. Both were typed lists
    # standing beside a generated count, and this revision entered three more.
    # =====================================================================

    ("9: name the framing retraction rather than numbering it by position",
     "The most consequential is the second framing retraction: the inference from per-dimension "
     "sign counts to a binomial P-value, which assumed an independence the 45 state dimensions do "
     "not have (§6.6).",

     "The most consequential of those is `S-15`: the inference from per-dimension sign counts to "
     "a binomial P-value, which assumed an independence the 45 state dimensions do not have "
     "(§6.6). It was named by position here until the second pre-submission review entered three "
     "more framing retractions and moved it."),

    ("appendix D: generate the framing-retraction list rather than typing two of them",
     "The {{n_retract_framing_word}} framing retractions are the claim that a pre-registration "
     "was pre-registered, and the binomial inference of §6.6. Each is a numbered entry in "
     "`FINDINGS_LEDGER.md` with its evidence and its successor.",

     "**The {{n_retract_framing_word}} framing retractions**, withdrawn as stated claims rather\n"
     "than as numbers, and generated from the ledger rather than listed here — a typed\n"
     "enumeration beside a generated count is the same defect as a typed count, and this list was\n"
     "typed with two entries when the ledger held two:{{n_retract_framing_list}}\n"
     "\n"
     "The last four were entered by the second pre-submission review. `S-16`, `S-17` and `S-18`\n"
     "are sentences of the 24 August draft that were false. `S-19` is different in kind and worse\n"
     "in one respect: §8 had already narrowed that claim in the paper, and the narrowing was never\n"
     "entered in the ledger, so the withdrawn version went on standing in the ledger's own\n"
     "contributions summary and in the public README after the paper had withdrawn it. A\n"
     "retraction that holds in one document and not in the repository is not a retraction, and\n"
     "the `retraction-consistency` check now reads all five reader-facing files rather than\n"
     "three. Each is an entry in `FINDINGS_LEDGER.md` with its evidence and its successor."),

    # =====================================================================
    # 2.3 (cont.) -- the table cell the prose was rewritten around. The
    # permutation column printed "--" at h=100 because the test had never been
    # run there; it has been now, in all three arenas.
    # =====================================================================

    ("2.3b 6.2 table: the h=100 permutation cell is a P-value, not a dash",
     "| 100 | {{d1n_alea_ratio_h100}}× [{{d1n_alea_ratio_ci_h100}}] | {{d1n_alea_cov1_h100}}% | "
     "**{{d1n_epi_ratio_h100}}×** [{{d1n_epi_ratio_ci_h100}}] | {{d1n_epi_cov1_h100}}% "
     "[{{d1n_epi_cov1_ci_h100}}] | {{d1n_epi_cov2_h100}}% | "
     "{{d1n_epi_npos_h100}}/{{d1n_epi_ndim_h100}} | — |",

     "| **{{v2_deploy_h}}** | {{d1n_alea_ratio_h100}}× [{{d1n_alea_ratio_ci_h100}}] | "
     "{{d1n_alea_cov1_h100}}% | **{{d1n_epi_ratio_h100}}×** [{{d1n_epi_ratio_ci_h100}}] | "
     "{{d1n_epi_cov1_h100}}% [{{d1n_epi_cov1_ci_h100}}] | {{d1n_epi_cov2_h100}}% | "
     "{{d1n_epi_npos_h100}}/{{d1n_epi_ndim_h100}} | {{perm_all_epi_p_h100}} |"),

    # =====================================================================
    # Readability: the note about the withdrawn range interrupted the sentence
    # it corrected. Move it to the end of the paragraph, where the other
    # earlier-draft notes in this paper sit.
    # =====================================================================

    ("6.10: move the withdrawn-range note out of the middle of the reading",
     "σ is larger at every horizon — by {{r2_sigma_x_lo}}× at its weakest "
     "(h = {{r2_sigma_x_lo_h}}) and {{r2_sigma_x_hi}}× at its strongest "
     "(h = {{r2_sigma_x_hi_h}}) — which is the direction trunk-sharing predicts, and at "
     "h = {{v2_deploy_h}} it is {{r2_sigma_x_h100}}×, **{{r2_from_sigma_h100}}%** of the "
     "improvement. An earlier draft gave that range as the h = 1 and h = 8 values, which do not "
     "span it. So the",

     "σ is larger at every horizon — by {{r2_sigma_x_lo}}× at its weakest\n"
     "(h = {{r2_sigma_x_lo_h}}) and {{r2_sigma_x_hi}}× at its strongest\n"
     "(h = {{r2_sigma_x_hi_h}}) — which is the direction trunk-sharing predicts, and at\n"
     "h = {{v2_deploy_h}} it is {{r2_sigma_x_h100}}×, **{{r2_from_sigma_h100}}%** of the\n"
     "improvement. So the"),

    ("6.10: and put it where the paragraph ends",
     "so a reader who takes the {{r2_total_x_h368}}× figure at that horizon as a measure of the "
     "architectural effect would overstate it. We report both columns for that reason.",

     "so a reader who takes the {{r2_total_x_h368}}× figure at that horizon as a measure of the\n"
     "architectural effect would overstate it. We report both columns for that reason. (An\n"
     "earlier draft gave the σ range above as the h = 1 and h = 8 values, which do not span it —\n"
     "h = {{r2_sigma_x_lo_h}}'s {{r2_sigma_x_lo}}× falls below the stated floor. Found by the\n"
     "horizon sweep, which flagged the sentence for carrying two horizons' figures while naming\n"
     "two others.)"),

    # =====================================================================
    # P0 (pending-work brief) -- the history rewrite has to be disclosed,
    # because the people most likely to notice it are the ones checking the
    # pre-registration argument against the repository.
    # =====================================================================

    ("Data and code: disclose the history rewrite and what it moved",
     "The pre-registration argument in §9 rests on commit timestamps, and those are "
     "author-settable via `git commit --date`. That matters, because §9 is load-bearing. Two "
     "things address it.",

     "**The repository's history was rewritten once, and §9 depends on that history, so we say\n"
     "what changed.** A supplementary file quoting private correspondence was committed and\n"
     "briefly published before consent to quote it had been given; it was purged from the history\n"
     "rather than merely deleted, because a deletion commit leaves the content recoverable from a\n"
     "public repository indefinitely. Purging a path rewrites every commit from the one that\n"
     "introduced it onward, so **{{f4_n_commits}} of the commits Figure 4 cites keep their\n"
     "identifiers and two do not** — the two whose data post-dates that file. Timestamps, content\n"
     "and ordering are unchanged; only the hashes moved, and Figure 4 resolves each rule by its\n"
     "commit subject for that reason. The transcript itself reaches reviewers in the anonymised\n"
     "supplementary archive, which is not published.\n"
     "\n"
     "The pre-registration argument in §9 rests on commit timestamps, and those are\n"
     "author-settable via `git commit --date`. That matters, because §9 is load-bearing. Two\n"
     "things address it."),

    # =====================================================================
    # PART A (pending-work brief) -- the A/B result becomes a curve.
    #
    # 2.58x at h=100 against 4.61x at h=368 is the largest substantive change in
    # this revision, and 3.1 declares h=368 not a deployment horizon. Left as a
    # line item beside the headline that reads as horizon shopping. As a curve it
    # is a finding: the advantage grows monotonically with depth and h=368 is the
    # end of a trend.
    # =====================================================================

    ("A1/A2/A3 5: the effect size becomes a curve, with the pre-registered point marked",
     "*The out-of-sample effect size, over {{d1_seeds}} seeds.* At h = {{v2_diag_h}}, the "
     "horizon M-23 is stated over, autoregressive training reaches **{{d1_A_mean}} ± "
     "{{d1_A_sd}}** against teacher forcing's **{{d1_B_mean}} ± {{d1_B_sd}}** (standard deviation "
     "over seeds, `ddof=1`) — a factor of **{{d1_ratio}}×**.\n"
     "\n"
     "**At the deployment horizon the same comparison is smaller, and we report it rather than "
     "leaving the reader to assume the headline transfers.** At h = {{v2_deploy_h}} — the "
     "method's own imagination rollout length, and the horizon everything in §6 is anchored to — "
     "the same three seeds give **{{d1_A_mean_h100}} ± {{d1_A_sd_h100}}** against "
     "**{{d1_B_mean_h100}} ± {{d1_B_sd_h100}}**, a factor of **{{d1_ratio_h100}}×**. The direction "
     "is the same and the margin is roughly half. **M-23's verdict stands as returned at "
     "h = {{v2_diag_h}}**; this figure is reported beside it and discharges nothing.",

     "*The out-of-sample effect size, at every horizon rather than one.* At h = {{v2_diag_h}},\n"
     "the horizon M-23 is stated over, autoregressive training reaches **{{d1_A_mean}} ±\n"
     "{{d1_A_sd}}** against teacher forcing's **{{d1_B_mean}} ± {{d1_B_sd}}** (standard deviation\n"
     "over seeds, `ddof=1`) — a factor of **{{d1_ratio}}×**. At h = {{v2_deploy_h}}, the method's\n"
     "own imagination rollout length and the horizon everything in §6 is anchored to, the same\n"
     "three seeds give **{{d1_ratio_h100}}×**.\n"
     "\n"
     "**Quoting one of those and not the other would be a choice, so we report the curve**\n"
     "(Figure 6). Same rollouts, same {{d1_seeds}} seeds, same held-out arena, n_independent =\n"
     "{{a1_nind}}, with a cluster bootstrap over whole trajectories:\n"
     "\n"
     "| h | autoregressive | teacher forcing | ratio | gap [95% CI] | excludes 0 | hold-last floor | A vs floor | B vs floor | episodes A leads |\n"
     "|---|---|---|---|---|---|---|---|---|---|\n"
     "| 1 | {{a1_A_h1}} ± {{a1_A_sd_h1}} | {{a1_B_h1}} ± {{a1_B_sd_h1}} | {{a1_ratio_h1}}× | {{a1_gap_h1}} {{a1_gap_ci_h1}} | **{{a1_excl_h1}}** | {{a1_floor_h1}} | {{a1_floor_over_A_h1}}× | {{a1_B_over_floor_h1}}× | {{a1_sign_pos_h1}}/{{a1_sign_n_h1}} |\n"
     "| 8 | {{a1_A_h8}} ± {{a1_A_sd_h8}} | {{a1_B_h8}} ± {{a1_B_sd_h8}} | {{a1_ratio_h8}}× | {{a1_gap_h8}} {{a1_gap_ci_h8}} | {{a1_excl_h8}} | {{a1_floor_h8}} | {{a1_floor_over_A_h8}}× | {{a1_B_over_floor_h8}}× | {{a1_sign_pos_h8}}/{{a1_sign_n_h8}} |\n"
     "| 32 | {{a1_A_h32}} ± {{a1_A_sd_h32}} | {{a1_B_h32}} ± {{a1_B_sd_h32}} | {{a1_ratio_h32}}× | {{a1_gap_h32}} {{a1_gap_ci_h32}} | {{a1_excl_h32}} | {{a1_floor_h32}} | {{a1_floor_over_A_h32}}× | {{a1_B_over_floor_h32}}× | {{a1_sign_pos_h32}}/{{a1_sign_n_h32}} |\n"
     "| **{{v2_deploy_h}}** | **{{a1_A_h100}} ± {{a1_A_sd_h100}}** | **{{a1_B_h100}} ± {{a1_B_sd_h100}}** | **{{a1_ratio_h100}}×** | **{{a1_gap_h100}} {{a1_gap_ci_h100}}** | **{{a1_excl_h100}}** | {{a1_floor_h100}} | **{{a1_floor_over_A_h100}}×** | **{{a1_B_over_floor_h100}}×** | **{{a1_sign_pos_h100}}/{{a1_sign_n_h100}}** |\n"
     "| 128 | {{a1_A_h128}} ± {{a1_A_sd_h128}} | {{a1_B_h128}} ± {{a1_B_sd_h128}} | {{a1_ratio_h128}}× | {{a1_gap_h128}} {{a1_gap_ci_h128}} | {{a1_excl_h128}} | {{a1_floor_h128}} | {{a1_floor_over_A_h128}}× | {{a1_B_over_floor_h128}}× | {{a1_sign_pos_h128}}/{{a1_sign_n_h128}} |\n"
     "| **{{v2_diag_h}}** *(M-23)* | **{{a1_A_h368}} ± {{a1_A_sd_h368}}** | **{{a1_B_h368}} ± {{a1_B_sd_h368}}** | **{{a1_ratio_h368}}×** | **{{a1_gap_h368}} {{a1_gap_ci_h368}}** | **{{a1_excl_h368}}** | {{a1_floor_h368}} | **{{a1_floor_over_A_h368}}×** | **{{a1_B_over_floor_h368}}×** | **{{a1_sign_pos_h368}}/{{a1_sign_n_h368}}** |\n"
     "\n"
     "**The advantage {{a1_monotone}} grow monotonically with forecast depth.** The gap excludes\n"
     "zero at {{a1_n_excl}} of {{a1_n_horizons}} horizons and spans it at {{a1_spans_zero_at}}.\n"
     "That is the reading a single figure cannot give: h = {{v2_diag_h}} is the end of a trend\n"
     "rather than a point we picked, h = {{v2_deploy_h}} sits partway along it, and the claim is\n"
     "weakest exactly where the model is trained.\n"
     "\n"
     "**Only the h = {{v2_diag_h}} row is pre-registered.** M-23 was committed at that horizon,\n"
     "before the runs, and its verdict stands as returned. Every other row was computed after the\n"
     "data existed, so by this paper's own standard (§9) it is not a pre-registration and carries\n"
     "none of the weight one would — the same treatment §6.7 gives the expectation we held about\n"
     "the counter-baseline. Nothing in the table discharges or re-opens M-23; the rule's anchor\n"
     "being the diagnostic horizon rather than the deployment one is recorded as M-46.\n"
     "\n"
     "**Two things in that table were not visible from h = {{v2_diag_h}} alone, and one of them\n"
     "cuts against us.** Teacher forcing is worse than the hold-last floor at\n"
     "{{a1_B_worse_than_floor_at}}, so §5's sharpest line is not an artifact of the longest\n"
     "horizon — at h = {{v2_deploy_h}} it is still {{a1_B_over_floor_h100}}× worse than assuming\n"
     "nothing changes. But **at h = 1 the floor beats *both* arms**: it scores {{a1_floor_h1}}\n"
     "against autoregressive training's {{a1_A_h1}}, the only horizon where a trained model loses\n"
     "to predicting no change at all. At 50 Hz one step is 20 ms and the state barely moves, so\n"
     "that is what one should expect; it is stated because §5 quoted the h = {{v2_diag_h}} margin\n"
     "over the floor with no indication that it does not hold everywhere."),

    ("A3 5: the sign test is reported at the deployment horizon too",
     "*The sign test, which does not depend on n.* At h = 368 the per-episode gap favours "
     "autoregressive training on **{{c3_sign_pos}} of {{c3_sign_n}}** episodes — an exact "
     "two-sided binomial test, p = **{{c3_sign_p}}**.",

     "*The sign test, which does not depend on n.* At h = {{v2_diag_h}} the per-episode gap "
     "favours autoregressive training on **{{c3_sign_pos}} of {{c3_sign_n}}** episodes — an exact "
     "two-sided binomial test, p = **{{c3_sign_p}}**. At h = {{v2_deploy_h}} it is "
     "**{{a1_sign_pos_h100}} of {{a1_sign_n_h100}}**, p = **{{a1_sign_p_h100}}**, so the count "
     "the abstract leans on is not an artifact of the longest horizon; at h = 1 it is "
     "{{a1_sign_pos_h1}} of {{a1_sign_n_h1}}, which is the same story the interval tells."),

    ("A4 abstract: the A/B claim quotes the curve rather than two points",
     "**The base paper's central training claim reproduces.** Under a rule committed to git\n"
     "before the runs that tested it, autoregressive training beats teacher forcing on held-out\n"
     "episodes by {{d1_ratio}}× on the reference's own relative-L1 error at h = {{v2_diag_h}}, the\n"
     "horizon the rule names, and {{d1_ratio_h100}}× at h = {{v2_deploy_h}}.",

     "**The base paper's central training claim reproduces, and the advantage grows with\n"
     "horizon.** Under a rule committed to git before the runs that tested it, autoregressive\n"
     "training beats teacher forcing on held-out episodes by {{d1_ratio}}× on the reference's own\n"
     "relative-L1 error at h = {{v2_diag_h}}, the horizon the rule names. Across the grid the\n"
     "ratio rises monotonically to that figure — {{d1_ratio_h100}}× at h = {{v2_deploy_h}}, the\n"
     "horizon the method deploys at — and the gap excludes zero at {{a1_n_excl}} of\n"
     "{{a1_n_horizons}} horizons."),

    # The abstract is over its budget again after Part A. The horizon labels stay
    # and the interval count goes: it is in 5 and in Figure 6, and the abstract
    # has to say what the shape is, not enumerate it.
    ("abstract: trim Part A back inside the budget",
     "**The base paper's central training claim reproduces, and the advantage grows with\n"
     "horizon.** Under a rule committed to git before the runs that tested it, autoregressive\n"
     "training beats teacher forcing on held-out episodes by {{d1_ratio}}× on the reference's own\n"
     "relative-L1 error at h = {{v2_diag_h}}, the horizon the rule names. Across the grid the\n"
     "ratio rises monotonically to that figure — {{d1_ratio_h100}}× at h = {{v2_deploy_h}}, the\n"
     "horizon the method deploys at — and the gap excludes zero at {{a1_n_excl}} of\n"
     "{{a1_n_horizons}} horizons.",

     "**The base paper's central training claim reproduces, and the advantage grows with\n"
     "horizon.** Under a rule committed to git before the runs that tested it, autoregressive\n"
     "training beats teacher forcing on held-out episodes by {{d1_ratio}}× on the reference's own\n"
     "relative-L1 error at h = {{v2_diag_h}}, the horizon the rule names, rising monotonically to\n"
     "that figure from {{d1_ratio_h100}}× at h = {{v2_deploy_h}}, where the method deploys."),

    # Fourteen words over. The uncertainty paragraph is the longest and carries
    # the most repetition ("the horizon its own imagination rollouts run to" is
    # said twice in the abstract by this point).
    ("abstract: the uncertainty paragraph, tightened once more",
     "**Neither uncertainty output the follow-up adds is usable as an interval.** At\n"
     "h = {{v2_deploy_h}}, the horizon its own imagination rollouts run to, the ensemble\n"
     "disagreement it penalises rewards with is {{d1n_epi_ratio_h100}}× smaller than the realised\n"
     "error: {{d1n_epi_cov1_h100}}% of outcomes fall inside ±1σ where {{v3_cov_nominal1}}% is\n"
     "calibrated. The per-member σ, which the method computes and discards, is a further\n"
     "{{d1n_epi_over_alea_h100}}× worse at h = {{v2_deploy_h}}, and we derive why: the\n"
     "implemented objective's optimum is σ = 0.",

     "**Neither uncertainty output the follow-up adds is usable as an interval.** At\n"
     "h = {{v2_deploy_h}} the ensemble disagreement it penalises rewards with is\n"
     "{{d1n_epi_ratio_h100}}× smaller than the realised error: {{d1n_epi_cov1_h100}}% of outcomes\n"
     "fall inside ±1σ where {{v3_cov_nominal1}}% is calibrated. The per-member σ, which the method\n"
     "computes and discards, is a further {{d1n_epi_over_alea_h100}}× worse there, and we derive\n"
     "why: the implemented objective's optimum is σ = 0."),

    ("abstract: the ranking paragraph, tightened once more",
     "**As a ranking it survives adversarial testing.** It beats the forecast step index — a free\n"
     "counter neither paper ran — at every horizon, and with the rollout and the forecast depth\n"
     "both held constant still correlates {{a2_rdd}} with realised error over the full rollout:\n"
     "not merely a report of which episode is hard.",

     "**As a ranking it survives adversarial testing.** It beats the forecast step index — a free\n"
     "counter neither paper ran — at every horizon, and with the rollout and the depth both held\n"
     "constant still correlates {{a2_rdd}} with realised error: not merely a report of which\n"
     "episode is hard."),

    # The horizon-consistency check caught the previous trim: "a further 349x
    # worse THERE" is a back-reference, and a back-reference is what the whole
    # sweep exists to refuse. The label goes back in and the words come out of
    # the prose around it.
    ("abstract: restore the horizon the trim dropped, and pay for it in prose",
     "**Neither uncertainty output the follow-up adds is usable as an interval.** At\n"
     "h = {{v2_deploy_h}} the ensemble disagreement it penalises rewards with is\n"
     "{{d1n_epi_ratio_h100}}× smaller than the realised error: {{d1n_epi_cov1_h100}}% of outcomes\n"
     "fall inside ±1σ where {{v3_cov_nominal1}}% is calibrated. The per-member σ, which the method\n"
     "computes and discards, is a further {{d1n_epi_over_alea_h100}}× worse there, and we derive\n"
     "why: the implemented objective's optimum is σ = 0.",

     "**Neither uncertainty output the follow-up adds is usable as an interval.** At\n"
     "h = {{v2_deploy_h}} the ensemble disagreement it penalises rewards with is\n"
     "{{d1n_epi_ratio_h100}}× smaller than realised error: {{d1n_epi_cov1_h100}}% of outcomes fall\n"
     "inside ±1σ where {{v3_cov_nominal1}}% is calibrated. The per-member σ the method computes\n"
     "and discards is a further {{d1n_epi_over_alea_h100}}× worse at h = {{v2_deploy_h}}, and we\n"
     "derive why: the implemented objective's optimum is σ = 0."),

    # =====================================================================
    # A4 -- propagate. Every remaining site that quotes the A/B factor or the
    # floor margin as if one horizon spoke for all of them.
    # =====================================================================

    ("A4 contributions: the training bullet quotes the curve",
     "- **The base paper's central training claim reproduces**, at a factor of {{d1_ratio}}× on\n"
     "  relative-L1 over {{d1_seeds}} seeds, under a rule committed to git before the runs existed (§5).",

     "- **The base paper's central training claim reproduces, and the advantage grows with\n"
     "  forecast horizon**: a factor of {{d1_ratio}}× on relative-L1 at h = {{v2_diag_h}} over\n"
     "  {{d1_seeds}} seeds, under a rule committed to git before the runs existed, rising\n"
     "  monotonically to that from {{d1_ratio_h100}}× at h = {{v2_deploy_h}} and a gap that spans\n"
     "  zero at {{a1_spans_zero_at}} (§5)."),

    ("A4 4: name the horizon on the figure the originals never gave",
     "So our {{d1_ratio}}× is neither a confirmation of a published figure nor a",
     "So our {{d1_ratio}}× at h = {{v2_diag_h}} is neither a confirmation of a published figure nor a"),

    ("A4 5: the earlier single-seed comparison names its horizon",
     "unfavourable to Arm B, and the three-seed ratio is {{d1_ratio}}× rather than {{m23_ratio}}×.",
     "unfavourable to Arm B, and the three-seed ratio at h = {{v2_diag_h}} is {{d1_ratio}}× rather "
     "than {{m23_ratio}}×."),

    ("A4 5: the floor paragraph reports both horizons and the one place it inverts",
     "*Against a baseline, because neither number means anything without one.* The hold-last "
     "floor — predicting that nothing changes — scores **{{floor_h368}}** in the same "
     "h = {{v2_diag_h}} cell. Autoregressive training beats it by **{{floor_over_A}}×**. "
     "**Teacher forcing is {{B_over_floor}}× worse than assuming nothing changes at all**, which "
     "is the sharper statement of what exposure bias costs here: the arm that reaches a lower "
     "training loss ends up predicting the future worse than a model that makes no prediction.",

     "*Against a baseline, because neither number means anything without one.* The hold-last\n"
     "floor — predicting that nothing changes — scores **{{floor_h368}}** in the same\n"
     "h = {{v2_diag_h}} cell, and autoregressive training beats it by **{{floor_over_A}}×** there\n"
     "and by {{a1_floor_over_A_h100}}× at h = {{v2_deploy_h}}. **Teacher forcing is\n"
     "{{B_over_floor}}× worse than assuming nothing changes at all** at h = {{v2_diag_h}}, and\n"
     "{{a1_B_over_floor_h100}}× worse at h = {{v2_deploy_h}}: the arm that reaches a lower\n"
     "training loss ends up predicting the future worse than a model that makes no prediction, at\n"
     "{{a1_B_worse_than_floor_at}} we measured. That is the sharper statement of what exposure\n"
     "bias costs here. **The floor is not a weak baseline everywhere**, and the table above says\n"
     "where it is not: at {{a1_A_worse_than_floor_at}} it beats the autoregressive arm as well."),

    ("A4 5.1: the data-budget sentence quotes one horizon and reads as if it held at all",
     "A dynamics model trained on {{c2_pct}}% of the reference's data still reproduces the "
     "autoregressive-versus-teacher-forcing result at {{d1_ratio}}× and still beats the hold-last "
     "floor by {{floor_over_A}}× at h=368.",

     "A dynamics model trained on {{c2_pct}}% of the reference's data still reproduces the "
     "autoregressive-versus-teacher-forcing result — {{d1_ratio}}× at h = {{v2_diag_h}} and "
     "{{d1_ratio_h100}}× at h = {{v2_deploy_h}} — and still beats the hold-last floor, by "
     "{{floor_over_A}}× and {{a1_floor_over_A_h100}}× at those two horizons."),

    # =====================================================================
    # PART B (pending-work brief) -- the h=100 consequences still open.
    # =====================================================================

    ("B1 10: bind the frequency claim to the recomputed count",
     "on a paired test that excludes zero at every horizon where the index is defined, and it "
     "retains {{d2b_par_all}} once that index is partialled out (§6.7).",

     "on a paired test that excludes zero at {{d2p_n_separating}} of the {{d2p_n_horizons}} "
     "horizons where the index is defined — every one of them — and it retains {{d2b_par_all}} "
     "once that index is partialled out (§6.7)."),

    ("B2 6.7: M-43's denominator is its own four horizons and does not follow the grid",
     "**It returns {{e5_verdict}}.** The first condition passes completely — disagreement leads "
     "the index in **{{e5_lead_cells}} of {{e5_total_cells}}** seed-horizon cells, every paired "
     "estimate positive, {{e5_diff_lo}} to {{e5_diff_hi}}. The second fails: the paired difference "
     "excludes zero at {{e5_n_excl}} of {{e5_n_horizons}} horizons, not a majority. We report the "
     "verdict the rule returns and do not rewrite the rule.",

     "**It returns {{e5_verdict}}.** The first condition passes completely — disagreement leads\n"
     "the index in **{{e5_lead_cells}} of {{e5_total_cells}}** seed-horizon cells, every paired\n"
     "estimate positive, {{e5_diff_lo}} to {{e5_diff_hi}}. The second fails: the paired difference\n"
     "excludes zero at {{e5_n_excl}} of {{e5_n_horizons}} horizons, not a majority. We report the\n"
     "verdict the rule returns and do not rewrite the rule.\n"
     "\n"
     "**And we do not rewrite its denominator either, which is the less obvious half of the same\n"
     "discipline.** M-43 was committed over {{e5_n_horizons}} horizons, before the data. Adding\n"
     "h = {{v2_deploy_h}} to the evaluation grid after the fact would change what \"a majority of\n"
     "horizons\" means in a rule already discharged — a way of moving a threshold that looks like\n"
     "reporting rather than like moving a threshold. The verdict above is over M-43's own\n"
     "{{e5_n_horizons}}. The released checkpoint's table in §6.7 does follow the six-horizon grid,\n"
     "because no pre-registration is stated over it; the two counts are deliberately different\n"
     "numbers and the build keeps them in separate keys for that reason."),

    ("B3 Appendix D: the overlap claim has now been wrong twice",
     "- **an interval relation that is not the one asserted** — \"the intervals do not overlap\", "
     "where at\n  h=128 they overlap across 0.604–0.643;",

     "- **an interval relation that is not the one asserted** — \"the intervals do not overlap\",\n"
     "  where at h=128 they overlap across 0.604–0.643. **This one has now been wrong twice.**\n"
     "  The correction said the distinction mattered \"at exactly one place\"; adding h = 100 to\n"
     "  the grid made it two, and the sentence recording the first error carried the second. A\n"
     "  stated *frequency* — \"at exactly one place\", \"in all four\", \"the only\" — is a claim\n"
     "  about a count, and no kind bound one to a recomputed count until `frequency-consistency`;"),

    ("B4 6.6: h=100 belongs in the horizon story, where it supports the reading",
     "Over all ten episodes (n_independent = {{perm_all_nind}}): {{perm_all_epi_p_h1}}, "
     "{{perm_all_epi_p_h8}} and {{perm_all_epi_p_h128}}. Two independent arenas at four and five "
     "times the sample say the effect is strongest at *short* horizon.",

     "Over all ten episodes (n_independent = {{perm_all_nind}}): {{perm_all_epi_p_h1}}, "
     "{{perm_all_epi_p_h8}} and {{perm_all_epi_p_h128}}, with h = {{v2_deploy_h}} at "
     "{{perm_all_epi_p_h100}} sitting between h=32's {{perm_all_epi_p_h32}} and h=128's "
     "{{perm_all_epi_p_h128}} — the horizon added by this revision falls where the existing "
     "reading says it should, which is worth stating because it was not free to. Two independent "
     "arenas at four and five times the sample say the effect is strongest at *short* horizon."),
]


def _pat(frag):
    return re.compile(r"[\s>]+".join(re.escape(w) for w in frag.split()))


def patch(text, old, new, label):
    """Whitespace-tolerant single-occurrence replacement.

    An edit already applied is reported and skipped rather than asserted on, so
    the script is re-runnable: the sweep is iterative by design and a second pass
    must not have to re-derive which of the first pass's edits already landed.
    Already-applied is a strict condition -- the OLD text absent AND the NEW text
    present exactly once -- so a genuinely missed edit still fails loudly.
    """
    # Applied-ness is tested BEFORE pendingness, because several edits wrap their
    # own `old` inside their `new` -- 2.1c inserts a table above the paragraph it
    # keeps. Testing `old` first re-fires those on every pass and inserts the
    # table again.
    done = list(_pat(new).finditer(text))
    if done:
        assert len(done) == 1, (
            f"[{label}] its replacement appears {len(done)} times; "
            f"a previous pass applied it more than once")
        return text, "already applied"
    hits = list(_pat(old).finditer(text))
    assert len(hits) == 1, (
        f"[{label}] matched {len(hits)} times, expected 1\n"
        f"  first 110 chars of pattern: {old[:110]!r}")
    return text[:hits[0].start()] + new + text[hits[0].end():], "ok"


def superseded_by(i):
    """The later edit that rewrites edit i's output, if there is one.

    The sweep is iterative: a first pass rewrote the abstract, a second pass
    renamed a back-reference inside what the first pass wrote, and a third
    trimmed the result to the word budget. On a re-run the first pass's `old` is
    gone and so is its `new`, and asserting on either would fail on an edit that
    landed correctly. An edit is superseded exactly when a LATER edit's `old`
    matches inside this one's `new` -- which is checkable rather than declared,
    so a genuinely missing edit still fails.
    """
    for j in range(i + 1, len(EDITS)):
        # Either direction of containment counts: a later edit may rewrite part
        # of what this one produced (its `old` sits inside this `new`), or may
        # swallow this one's output whole (this `new` sits inside its `old`).
        if (_pat(EDITS[j][1]).search(EDITS[i][2])
                or _pat(EDITS[i][2]).search(EDITS[j][1])):
            return EDITS[j][0]
    return None


def main():
    write = "--write" in sys.argv
    original = open(TEMPLATE).read()
    text = original
    by_label = {e[0]: e for e in EDITS}
    applied = 0
    for i, (label, old, new) in enumerate(EDITS):
        sup = superseded_by(i)
        # An edit whose successor has already landed must not fire again: 2.1c's
        # `old` survives inside 2.1c's own output, so re-firing it would insert
        # the r_dd table a second time.
        if sup is not None and _pat(by_label[sup][2]).search(text):
            print(f"  {'superseded':<15} {label}  ->  {sup}")
            continue
        if not _pat(old).search(text) and not _pat(new).search(text):
            assert sup, (f"[{label}] neither its target nor its replacement is in the "
                         f"template, and no later edit rewrites its output")
            print(f"  {'superseded':<15} {label}  ->  {sup}")
            continue
        text, how = patch(text, old, new, label)
        applied += how == "ok"
        print(f"  {how:<15} {label}")
    print(f"\n  {applied} edits applied, {len(EDITS) - applied} already in place")
    if not write:
        print("  DRY RUN — re-run with --write")
        return
    shutil.copy(TEMPLATE, TEMPLATE + ".c2bak")
    open(TEMPLATE, "w").write(text)
    d = list(difflib.unified_diff(original.splitlines(), text.splitlines(),
                                  "before", "after", lineterm="", n=0))
    print(f"  wrote {TEMPLATE} ({len(d)} diff lines)")


if __name__ == "__main__":
    main()
