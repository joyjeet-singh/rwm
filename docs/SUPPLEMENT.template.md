# Supplementary material

This document holds the text that left the paper's PDF to meet its length (ruling Y4): appendices, detail
tables and passages moved out of the main text whole. Nothing that left the PDF left the record. Every number below
is a placeholder (a key name in double braces) filled from `results/paper_numbers.json` by `scripts/build_paper.py`, exactly as the paper's
are, and the paper's checks read this file as they read the paper.

`docs/SUPPLEMENT.md` is generated from `docs/SUPPLEMENT.template.md`; edit the template, never the generated file.

## Contents

The sections are added as they leave the paper. Each keeps the heading it had in the paper and
says where in the paper it was.

## S1 What testing the untested claims would require

*Was the paper's Appendix C, "what testing the untested claims would require"; moved here to meet the length limit.*

Appendix D's first table marks {{orig_n_tested}} claims tested and the rest not. "Not tested" is an apology
unless it comes with a price, so here is what each would cost. We give compute orders where we
can estimate them honestly from this project's own measurements and say so where we cannot.

**Every row needs what this reproduction did not have: interaction.** Our arms train on the released CSV, which is a recording. Those claims need a
policy acting in an environment, simulated or real, and the environment responding. In
simulation that means Isaac Lab, which needs an RTX-class NVIDIA GPU, and no amount of CPU
substitutes: the reference's data generation is GPU-parallel simulation, not a data-loading
problem. For the hardware-transfer and real-robot rows the binding constraint is a robot rather
than compute. **A GPU would not be enough on its own.** The code that generates data is in
neither repository this reproduction pins: the only code that touches the file reads it
(`train.py:44` in the lite release), the lite release's environment rolls the learned model forward
rather than physics, and its readme places collection in a third repository, the authors' Isaac Lab
extension (`readme.md:13`), which this reproduction does not pin and which would need Isaac Lab and
an RTX-class GPU (ledger `D-36`).

| untested claim | what it needs | order |
|---|---|---|
| Sample efficiency, {{c2_ref}} against ~250M transitions (§IV-E) | Isaac Lab, an RTX-class GPU, the MBPO-PPO loop, and a PPO baseline run to convergence for the comparison | the reference reports {{c2_ref}} pretraining transitions and 50 min of RWM training on their hardware; the PPO baseline's 250M is the dominant cost |
| MBPO-PPO beats SHAC and Dreamer (§IV-E) | the above, plus SHAC and Dreamer implementations at matched budgets | three policy-learning stacks, each tuned enough that the comparison is fair — the largest engineering item here |
| Zero-shot hardware transfer (§IV-E) | all of the above, plus an ANYmal, a safe test area, and the sim-to-real stack | not estimable in compute; the binding constraint is hardware access, not GPU hours |
| Generality across quadruped, humanoid, manipulation (§IV-D) | recorded state-action data from a humanoid and a manipulator, which means Isaac Lab and a policy in each environment to generate it — the released CSV is one robot on one terrain | one data-generation run per morphology, plus a world-model training campaign each on the scale of ours, {{rt_runs}} runs in {{rt_hours}} h; the model training is the cheap half and the data is not |
| Offline MBRL on real robots (2504.16680v1) | a real robot, a logged dataset from it, and the offline MBRL loop | not estimable in compute; hardware access again, and a claim the follow-up itself states as prospective |
| Whether the penalty improves the learned policy (2504.16680v1 §5) | Isaac Lab, the MOPO-PPO loop, and at minimum an ablation with the penalty weight at zero | one policy-learning stack; the cheapest of the rows that need a simulator, and the one that would bound §11's open question about what the miscalibration costs |


**Two claims this table once priced as within reach of this setup have since been run**: the
configuration claim (§5.2) and the architecture claim (§5.3), {{rt_pre_runs}} runs and
{{rt_pre_hours}} h of CPU training between them (Appendix B). The {{appE_n_sim_word}} that remain all
need a simulator or hardware, and no amount of care with the released CSV changes that.

**What we would do first.** The penalty ablation. It is the cheapest of the simulator-requiring
items, it bears directly on a limitation §11 states our measurements cannot settle — whether the
miscalibration we document costs anything downstream, where §11's policy-free proxy tests only
whether the per-horizon correction reorders the penalty component and measures no cost — and it
needs no robot.



---

## S2 The limitations in full

*Was the paper's Appendix R, "the limitations in full (§11)"; moved here to meet the length limit.*

**Effective sample size bounds the long-horizon magnitudes.** The out-of-sample arena has
{{m23_nind}} independent 400-step trajectories (the n = {{m23_nind}} caveat of §3). That is the
binding constraint on §5's magnitudes, and no amount of trajectory oversampling changes it. The direction is re-tested on all ten episodes, each held out once: rule X3 trains both arms on {{x3_n_new_folds_word}} more fixed folds beside §5's own and returns **{{x3_reading}}** over {{x3_n}} trajectories, at {{iters_main}} iterations rather than {{iters_long}} (Appendix L). Nor can a larger
dataset be generated here: the data generator is in neither pinned repository, and the one the lite
release points to runs in a simulator this work did not have (supplementary S1). The released checkpoint's lack
of a held-out arena is therefore a constraint, not a choice.

**Ensemble size: supported, not established.** Our main arms run at ensemble size 1, where the epistemic term is identically zero, so the epistemic measurements were first made on the released checkpoint alone. The {{e5_seeds}} ensemble-5 Arm A arms (§6.6) reproduce the *direction* of §6.6's finding in {{e5_lead_cells}} of {{e5_total_cells}} seed-horizon cells and the *calibration* failure, {{e5_ratio_h100}}× at h = {{v2_deploy_h}}, but the pre-registered rule governing the replication returns **{{e5_verdict}}**: its second condition needs the paired difference to exclude zero at a majority of horizons, and it does at {{e5_n_excl}} of {{e5_n_horizons}}. Our arms have a held-out arena of only {{e5_nind}} independent trajectories, and the rule was written without checking what it could detect there. **So §6.6's finding is established on the released checkpoint and supported but not established on a model we trained.**

**One dataset, one gait, one terrain.** All commands are drawn from one bounded box and the gait
is a single trot throughout. "Generalisation" here means across velocity commands, not across
gaits or terrain.

**The per-horizon recalibration is tested on two episodes, or on episodes the model trained on.** §6.7's remedy puts every released-checkpoint estimate within the band across the two held-out episodes in both directions, though at this n no single cell is resolvable, and those cells are unseen by the multiplier only, because the checkpoint trained on both episodes. Rule X7 widens the released checkpoint's test to all ten episodes, each scored by a multiplier fitted on the other nine, and returns **{{x7_summary}}** for the epistemic term (Appendix Y); those episodes, too, are unseen by the multiplier only. On Arm A, whose model never saw them, the same recipe manages {{d3x_own_epi_ok}} of {{d3x_own_epi_cells}} epistemic and {{d3x_own_ale_ok}} of {{d3x_own_ale_cells}} aleatoric cells, and two episodes is not a demonstration that the multipliers transfer to a new robot, gait or terrain. Treat the lookup table as a recipe to refit, not as constants to copy.

**Two secondary analyses rest on a single training seed**, the long-horizon trend fit and the per-dimension matched comparison, both on seed 1 alone, as their artifacts record. The headline A/B verdict rests on one seed too, seed {{m23_seed}}, the one its rule ran on; the magnitudes
beside it are three-seed means with per-seed values (§5).

**On whole trajectories, the ranking claim is not established as needing an ensemble.** Under a rule committed before the
comparison (rule M-51, Appendix E), the model's own predicted state change, a subtraction needing no
ensemble, ranks error at {{e7_step_r}} against disagreement's {{e7_r_dis}}, and the margin is
smaller than this sample can resolve (§6.6). Disagreement retains {{e7_step_partial}} with that
baseline partialled out, so what is open is whether its increment is worth five models. **If the observed margin is the true one, settling it needs {{q2_n_req}} independent 400-step
trajectories, where all ten episodes provide {{e7_nind}}**, {{q2_factor}}× the present sample, by
the rule's own construction applied to the step-size margin's standard error
(`results/q2_free_baseline_power.json`). That is a required-sample-size estimate under an assumed
effect: it takes the true margin to be the observed {{e7_step_margin}} and new trajectories to vary
as these do, and if the true margin is smaller the requirement rises as its inverse square, to
{{q2_sens_n}} at {{q2_sens_margin}}. The margin is the only test left to pass, since the partial
already clears its threshold, {{e7_step_partial}} against {{e7_mde_partial}}. And it is closer to
resolving than §6.6's threshold of {{e7_mde_margin}} suggests: the rule had to fix that threshold
before this baseline existed, from the forecast-index margin, whose standard error is
{{q2_se_ratio}}× the step-size margin's. The observed margin is {{q2_pct_own}}% of what its own
statistic resolves at this sample and {{q2_pct_m51}}% of what the rule's threshold demands, and
re-run exactly as pre-registered that protocol would need {{q2_n_req_m51}} trajectories. §6.6's
verdict stands on either reading, because the margin is below both. On shorter units the margin at h = {{v2_deploy_h}} resolves: rule X6, committed before its reading, cut the same ten episodes into {{x6_n_units}} non-overlapping {{x6_unit_len}}-row units and returns **{{x6_reading}}**, {{x6_margin}} {{x6_ci}} at h = {{v2_deploy_h}} against a minimum detectable effect of {{x6_mde}} (Appendix X). Those units are the checkpoint's training data and share its ten episodes, and the interval resamples units, not episodes, so this settles that margin on this checkpoint's training episodes only, and does not re-test the margin at h = {{v2_diag_h}}.

**We did not measure what the miscalibration costs.** The penalty the follow-up applies is miscalibrated as a scale, {{d1n_epi_ratio_h100}}× overconfident at h = {{v2_deploy_h}}, the horizon its own imagination rollouts run to, but the method's only use of that quantity is to shape policy learning, and we did not train a policy. A miscalibrated scale that enters as a relative penalty across candidate actions may cost little or a great deal; our measurements cannot tell which. **The finding bounds what the quantity reports, not what it costs**, and the ratio is not a measure of harm. Other sections refer back to this as the policy caveat of §11.

**A proxy that needs no policy finds no reordering, and is worth only what its bound allows.**
Within one horizon the per-horizon correction multiplies the penalty by a positive constant, which
cannot change any ranking, so a rule committed before the statistic was computed (rule M-70,
Appendix E) compares instead the penalty accumulated along each whole rollout, before and after
correction. The penalty is the released checkpoint's own ensemble disagreement, on the {{q3_nind}}
independent trajectories of the held-out pair, which are unseen by the multipliers applied to them
but not by the checkpoint (§3). Of the {{q3_n_pairs}} pairs, {{q3_n_reorder}} change order and the
rule returns **{{q3_verdict}}**: the correction leaves every pairwise ordering of accumulated
penalty unchanged, so whatever it changes downstream must act through the penalty's magnitude
rather than through which rollout is penalised more. The multipliers differ by {{q3_c_ratio}}×
across horizons, so the design could have produced reordering
(`results/q3_penalty_reordering.json`). Three things limit what that shows. **It is the ordering of
the penalty component alone, not of the penalised return**: this work has no reward function and no
tuned penalty weight, so the result bounds what the correction could do downstream and licenses no
statement about a policy or about the size of any downstream effect. **The null is partly
structural**, by a diagnostic computed after the verdict: the last horizon band, h = {{q3_dom_h}},
holds {{q3_dom_steps}} of the {{q3_steps}} steps and {{q3_dom_share}}% of the corrected penalty, and
the overall ordering is exactly that band's, so the per-horizon weights had little room to act. **And the rule's bootstrap interval corroborates nothing**: resampling trajectories creates no new
pairs, so with none reordering no resample can return anything else, and the interval is
degenerate by construction (`M-71`).

**The per-dimension ordering tests are underpowered at every sample size we can reach.** Once the coupling between state dimensions is respected (§6.5), the out-of-sample arena's {{perm_oos_nind}} independent trajectories cannot reject at any effect size, and the larger arenas can and do not: over all ten episodes the smallest P in the family is {{perm_all_holm_min_p}} against a threshold of {{perm_all_holm_thr}}. Resolving it at h = {{v2_diag_h}} needs more episodes than the released dataset contains, not a better test. At h = 128 and below that is no longer true: a shorter unit gives {{m64_oos_n_h100}} independent units at h = {{v2_deploy_h}} where the 400-step unit gives {{perm_oos_nind}} (Appendix K), and we did not rerun this permutation family there. This limits the *per-dimension* evidence only; the aggregate scalar the method applies is one test rather than forty-five coupled ones, and more strongly supported (§6.6).

**No family-wide correction is applied across our own pre-registered rules.** There are {{appG_n_rules}} of them (Appendix E), each reported, once its data exist, against the thresholds it was committed with. Pre-registration is what licenses that: each rule is a separate question committed before its data, not one search over many outcomes, and a rule that fails is reported as failing. A reader who prefers a corrected family threshold can apply it from that count.

**The independent-ensemble comparison bounds the trunk-sharing effect rather than isolating it.** §6.8's contrast trains five models at five seeds and scores them together. Independently seeded runs differ in **both** initialisation *and* data ordering, whereas the shared-trunk heads differ only in head initialisation. They also differ in **capacity**: the independent arm carries {{v1_cap_indep}} state-pathway parameters against the shared-trunk arm's {{v1_cap_shared}}, a factor of {{v1_cap_ratio}}, because each member brings its own trunk, and greater capacity can inflate σ as well as shrink error. **Capacity is controlled separately.** Rule M-49 (Appendix E), committed with its minimum detectable effect before any of its models existed, trains {{r2_n_indep}} independent members at `rnn_hidden_size` {{m49_width}} against the released {{released_width}}, giving {{m49_matched_params}} state-pathway parameters against the shared-trunk arm's {{v1_cap_shared}}, a ratio of {{m49_matched_ratio}} where §6.8's contrast carried {{v1_cap_ratio}}. It scores them on the held-out pair's {{m23_nind}} 400-step trajectories, every model at {{iters_main}} training iterations. **With capacity held fixed the independent ensemble is still better calibrated on every shared-trunk seed, every paired interval still excludes zero, and the coverage gain of {{m49_cov_gain}} points still clears its own MDE.** The effect does not vanish when the confound is removed.

**It does shrink, and by more than this design can resolve.** The overconfidence improvement falls from {{m44_ratio_gain}}× unmatched to **{{m49_ratio_gain}}× matched**, against an MDE of {{m49_mde_ratio}}×, so the rule returns **{{m49_verdict}}**: {{m49_n_conditions_met}} of its {{m49_n_conditions}} conditions hold, and the ratio threshold is the one that does not. That is the third branch the rule names, and it names it because its MDE was almost exactly the size of the effect it re-tested, as rule M-49's own text said before the runs (ledger `M-49`). So trunk-sharing is **not** explained away by capacity: the effect points the same way on every pair, with every interval excluding zero. Whether capacity accounts for *any* of it this design does not answer: the point estimates fall by about {{m49_shrink}}, a difference no artifact here tests and far below the {{m49_mde_ratio}}× this comparison can resolve, and closing it needs more independent trajectories than the dataset contains. The comparison still conflates trunk-sharing with data-order diversity, which the rule does not address. That asymmetry is generous to the mechanism: had the factor barely moved despite the handicap, architecture would not be the explanation; since it moved, the design flaw is identified but not attributed to trunk-sharing alone. Isolating it would need an ensemble that shares data ordering and not parameters, a different experiment, as rule M-44 states in its own text.

**§6.4's mechanism is a structural fact plus a hypothesis.** That the five members share a trunk, a hidden state and {{v1_shared_pct}}% of each member's parameters is measured; that this *causes* the epistemic miscalibration is the hypothesis, and only §6.8 bears on it.

**The configuration and architecture verdicts hold at our budget and on our reading.** §5.2
varies one factor at a time at {{c2_pct}}% of the reference's data, so it cannot say what the
original's budget would favour. §5.3's baselines are our reconstruction of a table that fixes only
their shapes, tested on one robot where the original has several. Both sections state these limits
beside their results.

**Deliberately out of scope.** No policy-learning result of either paper is reproduced or tested:
there is no simulator, no RL loop, no ANYmal, and no policy is trained anywhere in this work. The
sample-efficiency comparison (roughly 6M against 250M transitions) is not tested for the same
reason, and nothing here uses a GPU. And **we did not test whether the σ = 0 optimum affects other
descendants of the PETS parameterisation** (§2): the clamp is inherited line for line, while the
objective and the tie between the bounds are this codebase's own, so the hypothesis is well-founded
only for a descendant that makes the substitution and leaves nothing pushing its floor back up, and
it is untested for any. We counted how often the substitution is made among the
{{q1_n_examined}} repositories we examined (§2), which bears on how far the hypothesis reaches, but
we tested the mechanism in none of them.

---
