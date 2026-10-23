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

## S3 What should travel, and the conclusion's discussion

*Was the paper's Appendix S, "the conclusion's discussion of the ranking, the scale, the per-dimension evidence, and what should travel (§12)"; moved here to meet the length limit.*

**What should travel, as §12 stated it.** §12 keeps two sentences of this paragraph.

**What should travel from this paper, and what should not.** The findings are of three kinds. *Properties of the objective and of how its bounds are built* are the ones to expect elsewhere,
and only where both are present together: §6.3 derives the σ = 0 optimum from squared
error on a sampled prediction through a bounded head whose floor nothing pushes back up, so it
should hold wherever both are present, the hypothesis §2 states and leaves untested outside this
codebase. On §2's count the substitution is present in {{q1_n_inherit}} of the {{q1_n_examined}}
descendants examined, and there only in a non-default mode; the survey did not examine the floor,
so that is an upper bound on how often both are. *Properties of this released artifact* should be checked
rather than assumed in any other: the one-step misalignment in its evaluation harness (§7.2), the
trunk its five members share (§6.4), and its specific overconfidence factors,
{{d1n_alea_ratio_h100}}× for the aleatoric σ and {{d1n_epi_ratio_h100}}× for the epistemic term
at h = {{v2_deploy_h}} (§6.2), are measurements of one checkpoint. *Properties of this dataset
and its arenas* are limits on what could be resolved, not findings in either direction, and neither pinned repository can lift them (§3): our arms' held-out arena holds {{m23_nind}} independent 400-step
trajectories and all ten episodes hold {{d1n_nind}}, which is why §11 and supplementary S2 leave the replication at
ensemble size 5, the free-baseline margin over whole trajectories at h = {{v2_diag_h}} and capacity's share of the
trunk-sharing effect open rather than settled (on shorter units at h = {{v2_deploy_h}}, rule X6 settles the margin on the
checkpoint's training episodes). §5.2's configuration verdict should not travel either: it is
resolved, but at our data budget, and says nothing about the original's.

The more useful finding is asymmetric, and it cuts both ways. The scale failure is established and large. The scale may be repairable per horizon, but on a model that has not seen the test episodes the evidence is mixed. On the released checkpoint a per-horizon multiplier, fitted on one episode and scored on another, brings every coverage estimate within {{d3_tol}} points of nominal, where a global multiplier manages {{d3_epi_const_ok}} of the {{d3_epi_cells}} epistemic cells, though no single cell is resolvable at this arena and the cells are not independent trials (§6.7). Fitted on nine episodes and scored on the tenth, the epistemic coverage over all {{x7_n_traj}} trajectories is within the band at every horizon (rule X7). On Arm A, whose model never saw those episodes, its own multipliers manage {{d3x_own_epi_ok}} of {{d3x_own_epi_cells}} epistemic cells. And the ranking use the follow-up claims does survive a real test: against the forecast step index, a free baseline neither original paper ran, ensemble disagreement wins at every horizon and keeps {{d2b_par_all}} once the index is partialled out. Against a second free baseline it does less well: the model's own predicted step size ranks error at {{e7_step_r}} against disagreement's {{e7_r_dis}}, a margin this sample cannot resolve at h = {{v2_diag_h}}, so the verdict is {{e7_verdict}} ({{e7_verdict_gloss}}). On shorter units of the same episodes, at h = {{v2_deploy_h}}, a later rule resolves that margin in disagreement's favour (rule X6: **{{x6_reading}}**, {{x6_margin}} {{x6_ci}}), on the checkpoint's training data. **The control this rests on removes trajectory difficulty rather than forecast depth**: with both the rollout and the depth held constant, disagreement still correlates {{a2_rdd}} {{a2_rdd_ci}} with realised error (§6.6). That is smaller than the {{a2_r_pooled}} pooled figure, and it is the one that means what a practitioner needs it to mean: not a re-encoding of the clock, and not merely a report of which episode is hard. It is the closest either original work comes to a claim this reproduction strengthens rather than qualifies, and even there the strengthening is of the ordering, not of the ensemble that produces it, since a free subtraction ranks nearly as well over whole trajectories.

What does not survive is the per-dimension form of the ordering evidence. Three of the five σ estimates we measured order their own errors better than chance in direction: the epistemic term on every one of the {{perm_all_epi_ndim_h368}} dimensions at h={{v2_diag_h}}, and the faithful and teacher-forced arms. That count is a direction, not a tally of independent trials, since the dimensions are physically coupled (§6.5). The released checkpoint's *aleatoric* head does the opposite, ranking error inversely at h = {{v2_diag_h}} on every one of {{perm_all_relale_ndim_h368}} dimensions over all ten episodes and at chance on the held-out pair alone, a dependence on arena that §6.5 sets out. The corrected arm sits at chance in both. Once the coupling is respected by permuting whole trajectories, no per-dimension count in this paper reaches significance after multiplicity correction; the independent-trials P-values an earlier draft carried were wrong by up to a factor of about {{perm_worst_factor}} and are withdrawn (`S-15`). Neither quantity yields a usable interval. Per dimension, uncertainty in this family of models should be read as a weak ordering at best, or fixed at the objective. As the scalar the method applies, ensemble disagreement gets the order right (§6.6) and the size wrong: it should not be read as a scale, and a ranking use deserves its own validation on the deployment distribution rather than trust inherited from here.

---

## S4 Related work in full

*Was the first part of the paper's Appendix I, "related work in full"; moved here to meet the length limit. The PETS lineage of the bounded σ head stays in the paper.*

**Related work in full (§2).** §2 keeps the direct precedent, what is new here, and the PETS lineage in
two sentences, with one line for each of the rest. Those lines stood in §2 as follows; the lineage
follows in full after them.

**The method's family.** MOPO (Yu, Thomas, Yu, Ermon, Zou, Levine, Finn and Ma, NeurIPS 2020)
penalises the reward by an ensemble uncertainty estimate to solve a pessimistic MDP; MOReL
(Kidambi, Rajeswaran, Netrapalli and Joachims, NeurIPS 2020) builds an unknown-state detector from
pairwise ensemble disagreement instead; and both branch short model rollouts from real states in
the manner of MBPO (Janner, Fu, Zhang and Levine, NeurIPS 2019). The follow-up we reproduce adapts
MOPO's penalty into MBPO's loop, which is what "MOPO-PPO" names, and its 100-step imagination
horizon sits inside MBPO's trade between rollout length and model error (§6.2).

**What "ensemble" is supposed to mean.** Deep ensembles (Lakshminarayanan, Pritzel and Blundell,
NeurIPS 2017) are several networks trained from *different random initialisations and different
data orderings*, and their spread is the uncertainty estimate. The released checkpoint's five
members share one GRU trunk, one recurrent hidden state, and {{v1_shared_pct}}% of each member's
state-prediction parameters, so whatever their spread measures, it is not what a deep ensemble
measures (§6.4).

**Three sources of uncertainty, and the one nobody here estimates.** Abbas, Sokota, Talvitie and
White (ICML 2020) separate predictive uncertainty in model-based RL into aleatoric noise,
parameter uncertainty, and **model inadequacy**, and observe that selective-planning work attends
almost entirely to the second. The checkpoint we measure emits an aleatoric term and a
parameter-uncertainty term, discards the first before use (§6.1), and has no estimate of the third,
which is precisely the component that compounds with rollout depth: the shape §6.5 reports.

**Why miscalibration is the expected finding.** Modern networks are systematically miscalibrated
(Guo, Pleiss, Sun and Weinberger, ICML 2017), and calibration degrades further under covariate
shift, worsening with distance from the training distribution (Ovadia, Fertig, Ren, Nado, Sculley,
Nowozin, Dillon, Lakshminarayanan and Snoek, NeurIPS 2019). An autoregressive rollout manufactures
its own covariate shift, increasing with depth, so horizon-dependent calibration failure is what
one should expect; our contribution on this axis is the *magnitude* and the *mechanism*, not the
direction. §6.7's per-horizon multiplier is a coarse instance of calibrated regression (Kuleshov,
Fenner and Ermon, ICML 2018), a post-hoc map fitted on one episode and scored on another, applied
to a horizon index; we do not present it as a new idea.

**The closest published work to our one constructive result.** Malik, Kuleshov, Song, Nemer,
Seymour and Ermon (ICML 2019) recalibrate a dynamics model's uncertainty inside model-based RL,
and argue that "good uncertainties must be calibrated" rather than merely well ranked, the
distinction §6.2 and §6.6 draw. §6.7 is a horizon-indexed instance: a single global multiplier
**fails**, its fitted value varying across horizons, where a per-horizon one puts every
released-checkpoint estimate within its tolerance band, though those cells are unseen by the
multiplier but not by the model and no single cell is resolvable (§6.7). An open-loop rollout's
error accumulates with depth, so a horizon-blind recalibration cannot follow it.

**§6.4's mechanism is known, and we say so.** That heads sharing a trunk under-report disagreement
relative to independently initialised networks is established: Lee, Purushwalkam, Cogswell,
Crandall and Batra (arXiv:1511.06314) treat ensemble diversity as something to engineer rather than
assume; Fort, Hu and Lakshminarayanan (arXiv:1912.02757) show that independent initialisation buys
a decorrelation subspace methods do not match; and BatchEnsemble (Wen, Tran and Ba, ICLR 2020) and
MIMO (Havasi, Jenatton, Fort, Liu, Snoek, Lakshminarayanan, Dai and Tran, ICLR 2021) share
deliberately and state what they trade away. **What is ours is finding it in a released robotics
checkpoint, with the sharing quantified at {{v1_shared_pct}}% of each member and its cost bounded by the {{m44_ratio_gain}}× an independent ensemble gains (§6.8).** The problem is not sharing; it is sharing and then reading the
spread as though the members were independent.

**And the objective in §6.3 has a neighbour.** Seitzer, Tavakoli, Antic and Martius (ICLR 2022)
identify failure modes of heteroscedastic σ heads trained by maximising log-likelihood. The
released model's state loss is not a log-likelihood at all (a *sample* enters a squared error), so
the failure §6.3 derives is more basic than theirs and does not depend on the optimiser. §6.3
derives it and demonstrates it against known noise.

## S5 The penalised quantity and the discarded term, from the first author

*Was the closing part of the paper's Appendix H, "findings not in the main text"; moved here to meet the length limit.*

**§6.1 in full: the penalised quantity and the discarded term, from the first author.** §6.1 keeps two sentences of this passage.

Eq. 4 specifies a **variance** while `system_dynamics.py:126` computes a **standard deviation**,
which with $\lambda = 1$ differ by a square. We asked, and the first author confirms the code is
operative: the penalty is applied to the standard deviation as intended, and Eq. 4 is "more of a
high-level explanation" (personal communication, 21 August 2026, quoted with the first author's
permission; the exchange is reproduced, anonymised, in the supplementary
`SUPPLEMENTARY_CORRESPONDENCE.md`, and see Data and code). We measure the code's quantity
throughout, which is the intended one.

The same correspondence confirms the discard directly: "the aleatoric term is not used in
downstream training. It is reported in Fig. 3 (right) as an analysis of the model behavior."
(The figure number follows arXiv:2504.16680**v1**; in the current {{v4_current}} it is Fig. 4, and
the crosswalk is in `results/original_paper_figures.json`.) So the discard is the intended design,
not an implementation slip: the aleatoric head, the one the state loss and the bound loss shape
and §6.3 explains, is computed on every imagination step to shape training and be inspected, and
is never consumed.

## S6 Measurements the paper does not use, with their evidence

*Was the last block of rows of the paper's Appendix H table, "findings not in the main text"; moved here to meet the length limit. Measurements are at {{iters_main}} training iterations unless a row says otherwise or concerns the released checkpoint, and each row names its arena.*

| finding | evidence (ledger ID, artifact) | bearing on the paper |
|---|---|---|
| ***Measurements*** | | |
| The data hold {{d10_n_regimes}} plateaus of achieved base velocity, {{d10_per_ep_word}} per episode with a third in episode {{d10_extra_ep}}; the command itself is not recorded, and the plateaus match the simulator's command resampling | D-10; `results/step0_regimes.json` | A held-out episode is not a near-duplicate of a training one: the held-out pair tests generalisation across velocity commands, within one gait and terrain |
| `state_min_logstd`, on the slower gradient path C-11 identifies, drifts {{o12_rate_ratio}}× slower than `log_delta_logstd`; extrapolated from one Arm A run's rates, the two imply about {{r25_implied_ld}} and {{r25_implied_min}} iterations for the released variance state, an order of magnitude rather than a fitted count | R-25; `results/step6_3_min_logstd.json` | §7.5's conclusion does not rest on one parameter |
| Over overlapping trajectories on the held-out pair, which the released checkpoint trained on, its worst twentieth carry {{r30_tail_share}}% of its squared error at h = {{v2_diag_h}} as each dimension's own scale weights it (form 2, which `g_z` dominates; Appendix G), and they start within {{r30_n_regions_word}} short ranges of rows, one per episode; on the {{r30_n_nonoverlap}} non-overlapping trajectories the largest is {{r30_maxmed}}× the median | R-30; `results/taskAB_gate_r27.json` | A tail measured on overlapping trajectories can be one short stretch of data, which a count of independent trajectories (§3) exposes |
| The A/B relative-L1 gap at h = {{v2_diag_h}} (teacher forcing's error minus autoregressive training's, over {{r39_n_per_ep}} independent trajectories per episode) is positive on all {{r39_n_eps_word}} episodes, from {{r39_gap_lo}} up; episode {{r39_ep}}, one of the held-out pair, gives {{r39_ep_gap}}, {{r39_ep_over_next}}× the next largest, so the pair's {{r39_gap_holdout}} is {{r39_ho_over_other}}× the other {{r39_n_other_word}} episodes' {{r39_gap_other}} | R-39; `results/task4_arenas.json` | The direction is robust across episodes; a magnitude read from the held-out pair overstates the typical episode |
| Per state dimension, over the whole {{v2_diag_h}}-step forecast, the released checkpoint loses to the hold-last floor on {{r45_rel_all}} of {{r45_n_dims}} across all ten episodes ({{r45_nind_all}} independent {{h2h_unit}}-step trajectories) and on {{r45_rel_ho}} on the held-out pair ({{r45_nind_ho}}), including all three components of the gravity vector; Arm A at {{iters_long}} iterations loses on {{r45_A_n}} in each, {{r45_A_dim}} | R-45, and R-29 on overlapping trajectories; `results/task2_3_matched_trend.json` | Per dimension, a model trained from scratch fails far less often, even on the pair the checkpoint trained on and Arm A did not. In aggregate it does not: on the held-out pair the released checkpoint is ahead at h = 8 and level at h = {{v2_diag_h}} (R-45). One seed (seed {{r45_seed}}, supplementary S2) |
| Over {{r46_n_ck_word}} checkpoints up to {{iters_long}} iterations, the absolute A/B gap at h = {{v2_diag_h}} narrows as both arms improve (held-out pair, n_independent = {{r46_o_nind}} 400-step trajectories, {{r46_o_gap0}} to {{r46_o_gap1}}; in-sample, n_independent = {{r46_i_nind}}, {{r46_i_gap0}} to {{r46_i_gap1}}), while the ratio does not shrink ({{r46_o_ratio0}}× to {{r46_o_ratio1}}×, in-sample {{r46_i_ratio0}}× to {{r46_i_ratio1}}×). The held-out values are not monotone: both peak at the {{r46_pk_ord}} checkpoint ({{r46_o_gap_pk}}, {{r46_o_ratio_pk}}×), one anomalous Arm B value | R-46; `results/task2_3_matched_trend.json` | An absolute effect quoted early overstates what remains, a ratio does not, and §5 reports ratios at {{iters_long}} iterations; one seed (seed {{r45_seed}}, supplementary S2) |
| Our trained models respond to the action they are given: fed another trajectory's actions, Arm A's error at h = 8 on its in-sample arena's {{x2_n_ins}} trajectories rises by {{x2_E_swap_2500}}% at {{iters_main}} iterations and {{x2_E_swap_10k}}% at {{iters_long}} (rule X2, pre-registered: {{x2_reading}}) | M-84, M-85; `results/action_sensitivity.json` | A world model must respond to actions before it can serve policy optimisation; ours do on this test, though every action in the data comes from one policy and no policy is trained here (§7.2, Appendix V) |

## S7 Compute: runtimes, the queues and their overlaps

*Was the rest of the paper's Appendix B, after the reproduce commands; moved here to meet the length limit.*

**Runtime.** Training stages are excluded by `--quick`, which is what makes the quick path practical. Training all {{rt_runs}} runs takes **{{rt_hours}} hours** of recorded wall clock on two CPU cores: {{rt_hours_10k}} hours for the {{rt_runs_10k}} runs at 10,000 iterations and {{rt_hours_short}} for the remaining {{rt_runs_short}} at 2,500. The longest single run is {{rt_longest}} hours. Every figure here is read from the `wall_clock_s` field of the run artifacts rather than estimated.

**{{rt_runs_m49}} of those {{rt_runs}} runs, {{rt_hours_m49}} hours, are `M-49`'s capacity-matched
arm at `rnn_hidden_size` {{m49_width}}** rather than the released {{released_width}}. They are part
of this project's CPU spend and are counted in the total above — the other {{rt_hours_released}}
hours are the {{n_runs}} runs at the released width, and the two parts are asserted to make the
total rather than stated beside it. They are **not** part of the {{n_runs}} runs of §6.3's σ-collapse family, because §6.3's rate is a property of one architecture and mixing widths into it would make "nearly identical across runs" a claim about two
different models. Every run artifact records the width it trained at, and `paper_numbers.py`
selects the collapse family by that field rather than by filename; `docs/BUILD_CHECKS.md`, shipped as supplementary, records how that selection came to be made.

**The pre-submission runs are counted separately.** §5.2's sweep and §5.3's baselines added
{{rt_pre_runs}} runs and **{{rt_pre_hours}} hours**: {{rt_sweep_runs}} sweep runs ({{rt_sweep_hours}} h),
then {{rt_bl_tf_runs}} teacher-forced and {{rt_bl_ar_runs}} autoregressive baseline runs
({{rt_bl_tf_hours}} h and {{rt_bl_ar_hours}} h), read from `results/presubmission_runtime.json`. They
are outside the total above, whose remainder that paragraph describes as released-width runs, which
the baselines are not. Of these, {{rt_pre_overlapped}} overlapped other CPU work a session logged,
which inflates their wall clock and changes no weight; the artifact lists each overlap. Rule X1's Part C (§5.3) ran {{rt_x1c_runs}} more teacher-forced RSSM runs from a second queue, {{rt_x1c_hours}} hours, which are in neither total; {{rt_x1c_overlapped}} of them overlapped CPU work a session logged. Rules X3 and X4 (§5, §5.3) ran {{rt_r4_runs}} more runs from a third queue, {{rt_r4_hours}} hours ({{rt_r4_x3_runs}} for X3, {{rt_r4_x3_hours}} h; {{rt_r4_x4_runs}} for X4, {{rt_r4_x4_hours}} h), also in neither total; {{rt_r4_overlapped}} of them overlapped CPU work a session logged while that queue ran. That queue's log lost its first runner's lines when another session resumed it, so {{rt_r4_by_log}} of its runs are timed by the log and the rest by their weights files, as `results/presubmission_runtime.json` records run by run; the resumed runner's runs overlap no logged work because that session logged none. X1's rows follow the baselines', and X3's and X4's close the table. Per run family, every run at {{iters_main}} iterations (the sweep's centre is §5's Arm A, whose runs are counted above):

| run family | runs | hours per run, mean | runs that overlapped other CPU work |
|---|---|---|---|
{{rt_pre_table}}
{{rt_r4_table}}

## S8 The repository's history

*Was a paragraph of the paper's Data and code section; moved here to meet the length limit.*

**The repository's history was rewritten once, and §8 depends on that history, so we say
what changed.** A supplementary file quoting private correspondence was committed and
briefly published before consent to quote it had been given; it was purged from the history
rather than merely deleted, because a deletion commit leaves the content recoverable from a
public repository indefinitely. Purging a path rewrites every commit from the one that
introduced it onward, so **{{f1_n_kept}} of the {{f1_n_cited}} commits Figure 3 cites keep their identifiers and {{f1_n_moved_word}} do not**: the {{f1_n_moved_word}} made between that file's introduction and the purge. Timestamps, content and ordering are unchanged; only the hashes moved, and for that reason Figure 3 finds its first rules' commits by subject and the later ones by the commit that introduced their ledger heading, never by a stored hash alone. The transcript itself reaches reviewers in the anonymised
supplementary archive, which is not published.

## S9 Anonymity

*Was a paragraph of the paper's Data and code section; moved here to meet the length limit.*

**On anonymity.** The code and data for this work are public, as they are for most reproducibility work, and the submission is anonymised: its bundle is scrubbed, asserted clean of a deny-list, and excludes the files that carry identity. Why the repository stays public, which §8's checkability depends on, is recorded in `docs/DOUBLE_BLIND_DECISION.md`.

## S10 Broader impact

*Was the paper's section 10. TMLR asks for a broader-impact statement only where there is a significant risk of harm, and this reproduction creates none, so the paper carries none (ruling G8-outline).*

## 10. Broader impact

This is a reproduction of a dynamics model on public simulation data. It creates no new
capability, uses no personal data and deploys nothing.

The findings bear on one practice, and it is not the one the original method uses. The follow-up
applies ensemble disagreement as a reward penalty. For that use, our measurements support its
ordering (§6.6), with the qualification that a free signal ranks error nearly as well. A different
use is reading the same number as an error bar, a safety margin, or a trigger for handing control
to a fallback controller. The original papers neither make nor recommend that use, and it is the
use our measurements rule out. At the method's own {{v2_deploy_h}}-step horizon, the disagreement
is {{d1n_epi_ratio_h100}}× smaller than realised error and covers {{d1n_epi_cov1_h100}}% of
outcomes where {{v3_cov_nominal1}}% is expected. We say this because the released checkpoint
exposes the quantity, and it is easy to read as an interval.

We do not claim the original method is unsafe. No policy is trained here. The one policy-free
test we ran found that correcting the scale per horizon leaves every pairwise ordering of accumulated penalty unchanged on the available trajectories, a test whose null is partly structural (§11).

## S11 Reproducibility accounting and the build's own checks

*Was a paragraph of the paper's section 8; moved here to meet the length limit.*

**Reproducibility, and a build that checks its own prose.** Every measured number in this paper is
substituted from an artifact on each build, and a quick run on a clean clone (`./reproduce.sh --quick --force`, which skips
training) rewrites {{ver_claim_pct}}% of the numeric values under `results/` that the comparison counts; the rest are carried in
and prove nothing about reproduction. **The number of regenerated values that differ and are
themselves a measurement, a statistic or the verdict of a test is {{ver_part_sci}}.** The clean-clone gate requires that
none differ at all; {{ver_differing}} do, so it fails and is published as failing. The supplementary
`docs/BUILD_CHECKS.md` gives the accounting and the checks the build runs on this paper's own prose.

## S12 Why X5 could not be run

*Was the body of the paper's Appendix W, whose heading stays for the rewrite; moved here to meet the length limit.*

Rule X5 would have tested what the miscalibration costs without training a policy. On windows of the method's imagination
length it would have compared the penalty the follow-up applies, summed along the forecast, with the model's error in
the return it forecasts over the same steps. It was to run only if every term of a reward subset that includes the two
command-tracking terms could be computed both from the recorded data and from the model's forecast. They cannot: both
score the base velocity against the velocity *command*, which the released data do not record and the model does not
output (the plateaus of achieved velocity in Appendix H are not the command; ledger D-38). Rule X5 was therefore neither
pre-registered nor run, and §11's policy caveat stands as written. The commit that pre-registered rules X6 to X8 names X5 in its subject; no X5 rule was entered (ledger D-38).

---
