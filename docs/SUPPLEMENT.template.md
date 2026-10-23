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

---

## S13 The earlier title and abstract

*Was the paper's title and abstract before the rewrite for the review of 19 October (the title was "Right Order, Wrong Size: A Verified Reproduction of the Robotic World Model and the Uncertainty It Reports"); moved here whole. Section numbers in this passage are the earlier paper's.*

**Abstract**

We rebuild the *Robotic World Model* (RWM; arXiv:2501.10100v1) and its uncertainty-aware follow-up
(arXiv:2504.16680v1), matching the released code's outputs, losses and gradients.
The base paper's central training claim reproduces under a rule committed in advance (seed {{m23_seed}}): over
{{d1_seeds}} seeds, training on the model's own rollouts beats teacher forcing {{d1_ratio}}× at {{v2_diag_h}} steps,
though not at one step on short windows. Retrained on fixed folds holding out each episode once ({{iters_main}} iterations, not {{iters_long}}), its direction **{{x3_reading}}** ({{x3_n}} trajectories).
At {{v2_diag_h}} steps RWM beats MLP, RSSM and transformer baselines built to our reading, all worse than predicting
no change; matched only in size, the transformer is unresolved ({{x4_reading}}).
On accuracy alone, {{mn_better_kinds}} beat the original's setting at our budget, no reading favouring it; trained
longer, it passes each on some reading (post hoc): the ranking depends on training budget. Magnitudes rest on
{{nind_oos_400}} held-out trajectories, {{c2_pct}}% of the reference's data, one robot, gait and terrain.
The follow-up's uncertainty gets the order right and the size wrong: ensemble disagreement correlates {{d4_r}} with error but is {{d1n_epi_ratio_h100}}× too small at {{v2_deploy_h}} steps on training data.
Predicted step size ranks error nearly as well over whole trajectories, worse on shorter units at {{v2_deploy_h}} steps. Members share {{v1_shared_pct}}% of parameters; independent models are
{{m44_ratio_gain}}× better calibrated, still overconfident. The implemented loss provably drives the discarded
per-member σ to zero. Per-horizon rescaling brings the released checkpoint's coverage within {{d3_tol}} points of nominal
for disagreement at every horizon on training episodes left out of each fit; on episodes our ensembles never saw,
only {{d3x_own_epi_ok}} of {{d3x_own_epi_cells}} cells. The released evaluation is one step stale;
over all ten episodes this raises the checkpoint's short-horizon relative-L1 error. We train no policy: we bound
what the uncertainty reports, not its cost.

---

---

## S14 The earlier introduction and contributions

*Was the paper's section 1 before the rewrite for the review of 19 October, with the Figure 1 sentence the figures session added; moved here whole. Section numbers in this passage are the earlier paper's.*

**Introduction (was §1)**

A world model that reports its own uncertainty is more useful than one that does not, and the
uncertainty-aware Robotic World Model reports one. This paper asks what that number means,
and the title gives the answer: it gets the order of the model's errors right and their size
wrong.

Figure 1 shows one finding about each original paper. Panel (a) is the base paper's claim that training on rollouts beats teacher forcing, measured on episodes the models never saw: the gap at h = {{v2_diag_h}}, one interval per fold and one point per held-out episode. Panel (b) asks whether the uncertainty-aware follow-up's spread grows with the horizon as the error does, under the released rollout and under a per-member rollout that is not the released method.

We set out to reproduce the base paper: rebuild the proprioceptive dynamics model from scratch,
check it against the released implementation, and test the central training claim, which holds at long horizons.
The rebuild made a second question cheap to ask: *is the predicted σ calibrated?* Neither of the
two the checkpoint emits is. On data it trained on, the per-member σ is too small by
{{d1n_alea_ratio_h1}}× at h = 1 to {{d1n_alea_ratio_h368}}× at h = {{v2_diag_h}}, by construction
(§6.3), and the ensemble disagreement the method uses by {{d1n_epi_ratio_h1}}× to
{{d1n_epi_ratio_h368}}×. The disagreement still ranks realised error, the use the method makes of it
(§6.6).

This is a reproduction in the stronger sense: the contribution is not that the numbers came out
the same, but what re-measuring the method reveals about where it is robust and where it is not.
Three things distinguish it from a re-run of the authors' code. **We rebuilt rather than
imported**, and matched the rebuild to the reference before any training (Appendix A), so a later
discrepancy belongs to the method, not to our wiring. **Decision rules were committed to git
before the data**, with timestamps a reader can check (§8, Figure 3); several returned verdicts against the original or could not settle the question, and we report each (Appendix E). **We keep our withdrawn findings in the record.** The ledger keeps
{{n_superseded}} superseded entries, each beside the evidence that withdrew it:
{{n_retractions_lower}} claims withdrawn on evidence, {{n_retract_framing_word}} framings withdrawn,
and the rest early hypotheses closed as housekeeping (§8 and the supplementary
`docs/BUILD_CHECKS.md`; every pre-registered rule, with its lead time and verdict, is in Appendix E). §9 gives the lessons in a form
a practitioner can use without reading the rest.

**Contributions.**

- **The uncertainty gets the order right and the size wrong, in the first calibration
  measurement we are aware of for this released checkpoint** (Lu et al. (2022) measure this family
  of penalties on models they train themselves; §2). Ensemble disagreement ranks realised error,
  correlating {{a2_rdd}} with it with rollout and forecast depth held fixed, yet on data the
  checkpoint trained on it is {{d1n_epi_ratio_h1}}× smaller than that error at h = 1 and
  {{d1n_epi_ratio_h100}}× at h = {{v2_deploy_h}} (§6.2, §6.6). It beats {{e7_n_beaten}} of the
  {{e7_n_new}} free baselines added here; the model's own predicted step size ranks error at {{e7_step_r}} against its {{e7_r_dis}} over the {{e7_nind}} whole trajectories, a margin they cannot resolve at h = {{v2_diag_h}}, while on {{x6_n_units}} shorter units at h = {{v2_deploy_h}} a rule committed before its reading finds disagreement ahead, {{x6_margin}} {{x6_ci}} (rule X6: **{{x6_reading}}**; §6.6, §11).
- **The base paper's central training claim reproduces, and reverses at one step.** A rule committed before the runs, run on seed {{m23_seed}} of each arm, found autoregressive training ahead by {{m23_ratio}}× at h = {{v2_diag_h}}; {{d1_seeds}} seeds at {{iters_long}} iterations extend it: the factor is {{d1_ratio}}×, and {{d1_ratio_h100}}× at h = {{v2_deploy_h}}, on the held-out pair's {{a1_nind}} independent 400-step trajectories (§5); retrained on fixed folds with each of the ten episodes held out once, the direction replicates, {{x3_gap}} {{x3_ci}} at h = {{v2_diag_h}} over {{x3_n}} trajectories at {{iters_main}} iterations, not {{iters_long}} (rule X3: **{{x3_reading}}**). At one step a second pre-registered rule, on {{m64_h1_n}} independent
  {{m64_h1_unit}}-row units, finds a gap of {{m64_h1_gap}} {{m64_h1_ci}} in favour of **teacher forcing** (§5).
- **Two more of the base paper's claims, tested under rules committed before the runs.** RWM is
  ahead at h = {{v2_diag_h}} of MLP, RSSM and transformer baselines built to our reading of its
  specification and trained with RWM's settings, whether teacher-forced as the original trains them or autoregressively, on the held-out pair's {{mn_nind}} independent trajectories at {{iters_main}} iterations, though every baseline is worse there than predicting no change; matched to RWM's parameter count, the MLP stays behind and the transformer cannot be told apart (rule X4: **{{x4_reading}}**; size is one axis), and neither reading our RSSM's forecast from its prior's expected or sampled latent nor retraining it with two other settings on one seed removes its open-loop collapse (rule X1, exploratory: **{{x1_final_reading}}**; §5.3). On accuracy alone at our budget, {{mn_n_better_word}} of the {{mn_n_configs_word}} one-factor neighbours of the original's {{mn_centre_label}} beat it, {{mn_n_short_better_word}} shorter histories at under half its cost per iteration and {{mn_better_long_phrase}} at more (no reading the rule reports puts the centre ahead of any of them), but trained longer the centre passes each of them on at least one reading (post hoc), so the ranking depends on the training budget; the original chose the centre as a trade-off with training time, which its own printed hours are consistent with and we do not test (§5.2).
- **The σ = 0 optimum of the implemented objective.** The implemented state loss is minimised at
  σ = 0, so the per-member σ the method discards collapses by construction: derived, and
  demonstrated against known noise (§6.3).
- **Trunk-sharing, tested.** The five members share one trunk, one recurrent state and
  {{v1_shared_pct}}% of each member's parameters, so their spread can express only uncertainty the
  trunk already carries (§6.4). Under a rule committed before the runs, on the held-out pair's {{r2_nind}} independent trajectories, {{r2_n_indep}} independently initialised full models are {{m44_ratio_gain}}× better calibrated than the shared-trunk arms, against a pre-registered minimum detectable effect of {{m44_mde_ratio}}×, and still {{r2_indep_ratio_h100}}× overconfident at h = {{v2_deploy_h}}; they also differ in capacity and data order, so this bounds the sharing effect rather than isolating it (§6.8).
- **Per-horizon recalibration, with mixed evidence.** One multiplier per horizon, fitted on one
  episode and scored on the other, brings every released-checkpoint coverage estimate near nominal
  where a global one does not, though no single cell is resolvable and the cells are unseen only by
  the multiplier, since the checkpoint trained on both episodes (§6.7); on Arm A, which never saw them, its own multipliers manage
  {{d3x_own_epi_ok}} of {{d3x_own_epi_cells}} disagreement cells. Fitted on nine episodes and scored on the tenth, the disagreement's coverage over all {{x7_n_traj}} trajectories is within the band at every horizon (rule X7: **{{x7_summary}}**), again on episodes the checkpoint trained on.
- **The released evaluation is misaligned by one step; over all ten episodes it raises the checkpoint's relative-L1 error up to h = 32, and from h = {{v2_deploy_h}} the change is not resolved.** Evaluation feeds the action from *t−1* where training pairs states and actions index-for-index, and shifting its action index by one step fixes it. On all ten episodes' {{ad20_nind}} independent trajectories, all of them training data for this checkpoint, the stale action raises its relative-L1 error by {{adh20_rel_h1}}% {{adh20_rel_ci_h1}} at h = 1 and {{adh20_rel_h32}}% {{adh20_rel_ci_h32}} at h = 32, and changes it by {{adh20_rel_h100}}% {{adh20_rel_ci_h100}} at h = {{v2_deploy_h}} and {{ad20_rel}}% {{ad20_rel_ci}} at h = {{v2_diag_h}}; on the held-out pair's {{ad_nind}} it raises it at every horizon reported, by {{ad_rel}}% {{ad_rel_ci}} at h = {{v2_diag_h}} (§7.2).
- **A from-scratch reimplementation verified at the gradient level.** Outputs match the released
  module bitwise, and losses and gradients match to {{diff_grad_max}} across {{diff_terms}} loss
  terms and {{diff_n_params}} parameter tensors, before any training (Appendix A).

---

---

## S15 The earlier related work

*Was the paper's section 2 before the rewrite for the review of 19 October; moved here whole. S4 holds the rest of that section. Section numbers in this passage are the earlier paper's.*

**Related work (was §2)**

This paper asks whether an ensemble-disagreement penalty is calibrated, and separates its use as a
*ranking* from its use as a *scale*. Both questions have a literature, and one paper asked almost
exactly ours four years earlier; below we say which parts of what follows are new. Supplementary S4
gives the rest of this section in full.

**The direct precedent.** Lu, Ball, Parker-Holder, Osborne and Roberts (*Revisiting Design Choices
in Offline Model-Based Reinforcement Learning*, ICLR 2022) compare uncertainty heuristics in
offline model-based RL under protocols built, in their words, to "capture the specific covariate
shift induced by model-based RL", in order to assess calibration. They report Spearman rank and
Pearson bivariate correlation against true model error **separately**, and observe that "despite
the similar rank correlations $\rho$, the bivariate correlations $r$ can vary considerably": a
configuration can keep the ordering while the penalty's size relative to the error changes. That
is our ranking-versus-scale distinction, on the same family of penalties. They also find the
ensemble standard deviation, the exact quantity `system_dynamics.py:126` computes and
`envs/base.py:166` applies, to track model error *better* than the penalties of MOPO and MOReL,
being "strikingly similar" to the latter but better behaved; §6.6 finds the same quantity a usable
ranking signal.

**What is new here is four things.** Lu et al. measure models they train themselves, on simulated
benchmarks, and their statistics describe ordering and shape, not coverage. We measure a
**released checkpoint** from a pipeline its authors deployed on hardware, where reading the penalty
as an interval has consequences. We measure **coverage** against a nominal. We verify our
reimplementation against the reference at the gradient level before any training (Appendix A). And
§6.3 derives the σ = 0 optimum for the objective the released code *substitutes*, squared error on
a reparameterised sample, rather than for the likelihood the parameterisation was built around.

**Where the parameterisation comes from.** The clamp of the bounded log-σ head whose optimum §6.3
shows is σ = 0 is inherited, line for line, from the probabilistic ensembles of Chua, Calandra, McAllister
and Levine (PETS, NeurIPS 2018), but the objective is not: the released code replaces PETS's
likelihood with squared error on a sampled prediction and ties the upper bound to the floor. So
**a descendant of this lineage that made the same substitution, and left nothing pushing its
variance floor back up, would inherit the same optimum**, a hypothesis about mechanism untested in
any other descendant (§11). Of {{q1_n_looked}} public repositories the survey looked at, {{q1_n_carry}} carry the construction, the ones its protocol counts as examined, and {{q1_n_inherit}} of those trains it against a sampled squared error, only in
an optional mode, so on this sample of convenience the substitution is rare (Appendix I).

**The method's family.** MOPO (Yu et al., NeurIPS 2020) penalises the reward by an ensemble
uncertainty estimate and MOReL (Kidambi et al., NeurIPS 2020) detects unknown states by pairwise
ensemble disagreement, both branching short model rollouts from real states as MBPO (Janner et al.,
NeurIPS 2019) does. The follow-up we reproduce puts MOPO's penalty into MBPO's loop, which is what
"MOPO-PPO" names.

**What "ensemble" is supposed to mean.** Deep ensembles (Lakshminarayanan, Pritzel and Blundell,
NeurIPS 2017) are networks trained from *different random initialisations and different data
orderings*, whereas the released checkpoint's five members share one GRU trunk, one recurrent hidden
state and {{v1_shared_pct}}% of each member's state-prediction parameters (§6.4).

**Three sources of uncertainty, and the one nobody here estimates.** Abbas, Sokota, Talvitie and
White (ICML 2020) separate aleatoric noise, parameter uncertainty and **model inadequacy**; the
checkpoint we measure has no estimate of the third, the component that compounds with rollout depth
(§6.5).

**Why miscalibration is the expected finding.** Networks are miscalibrated (Guo et al., ICML 2017),
more so under covariate shift (Ovadia et al., NeurIPS 2019), and a rollout manufactures its own
shift, increasing with depth, so our contribution on this axis is the *magnitude* and the
*mechanism*, not the direction.

**Recalibration.** §6.7's per-horizon multiplier is a coarse instance of calibrated regression
(Kuleshov, Fenner and Ermon, ICML 2018), and Malik et al. (ICML 2019) recalibrate a dynamics model's
uncertainty inside model-based RL, arguing that "good uncertainties must be calibrated"; what §6.7
adds is the horizon index, and the finding that a single global multiplier **fails**.

**§6.4's mechanism is known, and we say so.** That heads sharing a trunk under-report disagreement
is established (Lee et al., arXiv:1511.06314; Fort, Hu and Lakshminarayanan, arXiv:1912.02757;
BatchEnsemble, ICLR 2020; MIMO, ICLR 2021). **What is ours is finding it in a released robotics
checkpoint, with the sharing quantified at {{v1_shared_pct}}% of each member and its cost bounded by the {{m44_ratio_gain}}× an independent ensemble gains (§6.8).**

**And the objective in §6.3 has a neighbour.** Seitzer, Tavakoli, Antic and Martius (ICLR 2022)
identify failure modes of σ heads trained by maximising log-likelihood; the released state loss is
not a log-likelihood at all, so the failure §6.3 derives is more basic than theirs.



---

---

## S16 The earlier setup

*Was the paper's section 3 (data, evaluation, effective sample size, metrics, horizons and what each claim rests on) before the rewrite for the review of 19 October; moved here whole. Section numbers in this passage are the earlier paper's.*

**Setup (was §3)**

**Data.** The released dataset is {{rows}} rows of ANYmal D proprioceptive state and policy
actions at 50 Hz: ten concatenated 20-second episodes, with a termination column that is
identically zero, so nothing in the file marks the boundaries.

**The segments are not all the same length.** The first episode is {{ep0_rows}} rows and the other
{{n_ep_rest_word}} are {{ep_rest_rows}} each, with a reset at rows {{reset_rows_first}},
{{reset_rows_second}} … {{reset_rows_last}} and {{orphan_rows}} orphan row at the end of the file
that begins an eleventh episode and ends immediately: {{row_structure}}. We recover the boundaries
from the data: at every reset row the twelve joint velocities, the four HAA joint positions and all
twelve actions are exactly zero, and no other row has that fingerprint. Ten equal segments of
{{ep_rest_rows}} would give one fewer crossing window and one more usable one, so the counts below
differ by one from that reading; `results/step0_regimes.json` re-derives the crossing count from the
segment lengths alone, and the two agree.

A window is {{win_len}} rows, {{win_hist}} of history and {{win_fore}} of forecast, and the
reference window builder marks all {{win_naive}} windows valid, including {{win_cross}} that splice
one episode's end onto the next one's start. The usable, episode-respecting count is
{{win_usable}}: {{rows}} rows, less {{win_tail}} that cannot start a full window, less
{{win_cross}} that cross a boundary. The contamination rate is {{contam_pct}}%.

**Model.** A GRU-based ensemble predicting the next proprioceptive state, with a mean head and a
bounded log-σ head, plus auxiliary heads for contact and termination. The paper describes two loss
terms; the implementation has {{diff_terms}}. Before any training, our rebuild's outputs match the
released module's bitwise, and its losses and gradients match to {{diff_grad_max}} across those
{{diff_terms}} terms and {{diff_n_params}} parameter tensors (Appendix A).

**Evaluation.** Two arenas, kept separate throughout: *out-of-sample*, the two episodes withheld
from training, and *in-sample*, the eight used for it. The released evaluation draws its
trajectories from training data, and the original does not distinguish the two. **The released
checkpoint trained on all ten episodes, so it has no held-out arena in this dataset**, and every
figure for it is in-sample; later sections refer back to this as the in-sample caveat of §3. More
data cannot be generated from either repository this reproduction pins (supplementary S1).

**Effective sample size.** Trajectory count is not sample size. Two 400-step trajectories whose
spans overlap are not independent evidence, and the out-of-sample arena contains only
{{m23_nind}} mutually non-overlapping 400-step trajectories. A bootstrap over whole trajectories at
that size has {{c3_resamples}} distinct resamples, so its intervals are quantised at that
resolution. Every long-horizon verdict in this paper is computed with a bootstrap over independent trajectories, every table reports that count, and §8 reports both resampling units where they
differ. Later sections refer back to this as the n = {{m23_nind}} caveat of §3. One trajectory can carry
much of a long-horizon effect: a one-step shift of the action moves the released checkpoint's
{{v2_diag_h}}-step relative-L1 error on single trajectories of its own training episodes by anywhere from
{{ad20_traj_lo}}% to {{ad20_traj_hi}}% (§7.2), which illustrates why {{m23_nind}} trajectories bound every
long-horizon claim.

**Metrics (was §3.1)**

Each metric is stated as implemented, because a reader who cannot see the denominator cannot check the headline. Appendix G gives each metric's formula and
the check on the coverage nominal.

**Relative-L1** is the reference's own metric, reproduced in behaviour (`model_training.py:203`) so
that our numbers are comparable to the upstream's printed one. At each forecast step it is the summed
absolute error over the state dimensions divided by the summed absolute true state, on
config-normalised states, averaged flat over trajectories and over the steps after the first
{{v2_history}}, which are teacher-forced. The denominator, a 45-term sum in normalised space, is
recomputed at every step, so it can pass through zero, which is why this metric goes non-finite on
low-dimensional state groups and why a second one exists.

**Normalised RMSE** fixes the denominator once: the root of the squared error pooled over the state
dimensions, divided by the dimensions' mean standard deviation over the training episodes only, a
constant stored in `results/step4_0a_results.json` and never recomputed per step or derived from
held-out data. A value of 1.0 means no better than predicting the training mean. **The aggregation
is form 1**, a ratio of means; a mean of per-dimension ratios would give whichever dimension has the
smallest scale unbounded leverage (Appendix G).

**Coverage at ±kσ** is the fraction of (trajectory, forecast step, state dimension) triples, pooled
with equal weight, whose absolute error falls within k times the σ predicted for that triple. It is
two-sided, so its calibrated targets are **{{v3_cov_nominal1}}%** at ±1σ and
**{{v3_cov_nominal2}}%** at ±2σ.

**The overconfidence factor** $\rho$ is the mean absolute error over the mean predicted σ, a ratio
of means. $\rho = 1$ is *not* calibration, since a calibrated Gaussian has $\rho = \sqrt{2/\pi}$ =
{{v3_rho_calibrated}}, so $\rho$ is reported as a magnitude of miscalibration and coverage as the
calibrated reading.

**Which metric each headline uses.** The A/B training claim (§5) is relative-L1, because the claim
is about reproducing the upstream's comparison and that is the upstream's metric. The calibration
claims (§6.2) are the overconfidence factor and coverage, because neither error metric involves σ.
The ranking claims (§6.6) are Pearson correlations between the applied scalar penalty and total
absolute error, because a ranking claim is about order rather than scale. Every headline number in
the abstract names its metric. §7.2's alignment defect is given in both metrics, over all ten episodes and on the held-out pair. Over all ten episodes the two metrics agree that the stale action raises error at h = 8 and 32 and that from h = {{v2_deploy_h}} the change is not resolved, and they differ at h = 1, where relative-L1 resolves the rise and nRMSE does not.

**Horizons.** Curves are reported at $h \in \{1,\,8,\,32,\,{{v2_deploy_h}},\,128,\,{{v2_diag_h}}\}$.
Every horizon-indexed quantity is cumulative over steps 1..h, not the value at step h. Two of those are load-bearing and the rest are landmarks. **h = {{v2_deploy_h}}** is the method's
own imagination rollout length, the horizon over which the uncertainty-penalised policy loop
actually runs this model (arXiv:2504.16680 Table S9 in v1 and Table S11 in v3, with the same
value). **h = {{v2_diag_h}}** is the upstream's open-loop diagnostic length: `len_eval_trajectory` =
{{v2_len_eval}} minus the {{v2_history}}-step teacher-forced prefix, the curve the follow-up plots
as its uncertainty figure. It is {{v2_ratio}}× the method's own rollout length and is not a
deployment horizon. Every table keeps both: h = {{v2_diag_h}} makes our numbers comparable to the
original's *figure*, and h = {{v2_deploy_h}} to its *method*.

**What each claim rests on (was §3.2)**

Every headline claim in this paper is measured on the out-of-sample or in-sample arena above, or on all ten episodes together, at a stated number of independent units (400-step trajectories unless the row says otherwise). Each is also at a stated checkpoint: the released one, or ours at a stated
number of training iterations. Appendix D's second table, "What each tested claim rests on", gives each claim's arena, sample size, checkpoint and verdict. It is generated from the artifacts each claim is computed from, so no arena label, sample size or checkpoint in it is typed by hand.

---

---

## S17 The earlier method section

*Was the paper's section 8 (the ledger, the one failed pre-registration, the withdrawal counts and the resampling-unit correction) before the rewrite for the review of 19 October; moved here whole. Section 3.4 of the paper keeps what the paper needs. Section numbers in this passage are the earlier paper's.*

**Method (was §8)**

**An append-only ledger.** Every claim here has a permanent identifier, an evidence class (source, data, run, external, inference) and a status, in `FINDINGS_LEDGER.md` ({{n_entries}} entries). Claims are never edited in place: one that turns out to be wrong is marked superseded, pointed at what replaced it, and kept.

**Pre-registration, and one failure of it.** Decision rules were committed to git before the data that tested them, with one exception. Figure 3 and Appendix E give the lead time for each of the {{appG_n_lead}} whose data exist; {{appG_n_positive}} are positive and {{appG_n_negative}} is not. Every positive bar is a difference of two commit timestamps. **The negative one is not**: it is the duplication-control rule (§7.4), whose *data* side is the moment the control runs finished, a line in `results/control_driver.log` rather than a commit, dated from the commit that introduced that line. The rule was stated in conversation before the runs and reached git **{{lead_task3}} after they finished**, and we found it only by auditing our own `git log`. The measurement stands, because the arm was built without reference to its outcome, but the claim that it was pre-registered does not, and it is withdrawn. A discipline that is only checked when it succeeds is not a discipline.

**{{n_retractions_word}} claims withdrawn on evidence**, and {{n_retract_framing_word}} framings withdrawn rather than numbers, out of {{n_superseded}} superseded entries kept in the record (the supplementary `docs/BUILD_CHECKS.md` lists them). The most consequential of the framings withdrawn is the inference from per-dimension sign counts to a binomial P-value, which assumed an independence the 45 state dimensions do not have (§6.5). Found by our own pre-submission audit, it withdraws the strength of evidence behind what an earlier draft called its strongest result.

**A statistic that was resampling the wrong unit.** Our bootstrap pooled three seeds over a shared trajectory set and resampled the pooled vector while reporting the independent-trajectory count, so each trajectory appeared three times. Resampling trajectories instead widens intervals by a mean {{bu_mean_ratio}}× and changes {{bu_changes}} of {{bu_cells}} verdicts, in {{bu_change_cell}}, already recorded as unresolvable. Every long-horizon verdict survives; both units are reported.



---

---

## S18 The earlier data and code section

*Was the paper's closing section 'Data and code' before the rewrite for the review of 19 October; its history and anonymity paragraphs are S8 and S9, and the rest is moved here whole. Section numbers in this passage are the earlier paper's.*

**Data and code**

The full repository — code, every artifact under `results/`, and `FINDINGS_LEDGER.md` with the
complete claim record including the retractions — accompanies this submission as anonymised
supplementary material, and will be released under a permanent archival identifier on
acceptance. Neither upstream repository is redistributed; `setup.sh` fetches both at pinned
commits and verifies two SHA-256 hashes.



The pre-registration argument in §8 rests on commit timestamps, and those are
author-settable via `git commit --date`. That matters, because §8 is load-bearing. Two
things address it. The
supplementary material includes an anonymised `git log` covering every commit cited here, so the
ordering in Figure 3 is checkable at review time. In the submitted paper and bundle, commit identifiers are replaced by stable
anonymous labels, with ordering, timestamps and subjects unchanged, and the map from label to
identifier is disclosed on acceptance. And **the repository was archived by a
third-party archive before submission**, under a permanent identifier whose visit timestamp is
not author-controllable. Neither the identifier nor the date of that visit appears here: both
resolve to a named repository, and a date is a one-field lookup away from an origin. They are
disclosed on acceptance.

What that archive establishes should be stated precisely, because it is easy to overclaim. It
does **not** prove any individual commit date is genuine. It proves that the repository, with the
whole pre-registration history in the form this paper cites, existed no later than that archival
moment, as recorded by a third party with no interest in the claim — so nothing in the record can
have been back-dated afterwards. That bounds §8 rather than proving it, and a reviewer should
read it as such.

---

## S19 The earlier sections on the original papers' claims

*Were the paper's fourth section (what the original papers claim, and which claims we test) and fifth (the base paper's central claim, the data budget, the configuration claim and the architecture claim) before the rewrite for the review of 19 October; moved here whole. Section numbers in this passage are the earlier paper's.*

**What the original papers claim, and which claims we test (was §4)**

A reproduction that does not say what it left alone invites the reader to assume it tested
everything. It did not.

**We tested {{orig_n_tested_word}} claims and left {{n_untested_word}} untested.** The {{orig_n_tested_word}} are the base paper's
autoregressive-versus-teacher-forcing comparison and its claim that teacher forcing generalises
poorly (§5), its configuration claim (§5.2) and its claim against MLP, RSSM and transformer
baselines (§5.3), and the follow-up's two claims about what its uncertainty outputs report (§6).
**Every one of the {{n_untested_word}} we did not test needs a simulator or hardware we do not have**: {{appF_sim_list}}.
**{{appF_n_polhw_word}} of them are claims about policy learning or hardware** — every one but
{{appF_model_list}}, which needs a simulator and recorded data from other robots but is a claim
about the model rather than about a policy. This work trains no policy and runs on two CPU cores.
The counts and lists are generated from the classification tags in the verdict column of Appendix D's first table, so none of them is typed. §11 states what the untested claims bound, and supplementary S1 what testing them
would take.

**For {{orig_n_without_word}} of the {{orig_n_tested_word}} claims we tested, the original reports no quantitative
figure.** Each is asserted qualitatively and shown in a plot, with no number in text, caption or
table; §6.6's coefficient is the first figure attached to the follow-up's "strong correlation"
between disagreement and error. The exceptions are the configuration claim and the teacher-forcing
claim, whose values one heatmap prints in every cell (§5.2). Appendix L sets its teacher-forcing cell beside
ours, which uses a different definition of teacher forcing. Where a magnitude is legible only from a plotted curve we say so rather
than estimating it from the axis.

**Appendix D's first table gives it in full**, claim by claim, with what the original states, where it
states it, and our verdict.

---

**The base paper's central claim reproduces (was §5)**

**Claim under test.** Training the dynamics model on its own autoregressive rollouts beats training it with teacher forcing, at long forecast horizons.

**Rule, committed in advance** (rule M-23; Appendix E gives its commit and lead time), naming conditions rather
than outcomes. Three conditions, all required: the out-of-sample gap at h = 368 excludes zero
under a bootstrap over independent trajectories; the sign is consistent across episodes; and the effect survives at 10,000 iterations rather than only at the paper's 2,500. The rule was run on
seed {{m23_seed}} of each arm: autoregressive {{m23_A_s1}} against teacher forcing {{m23_B_s1}} at
h = {{v2_diag_h}}, {{m23_ratio}}×, gap interval [{{m23_ci_lo}}, {{m23_ci_hi}}]. The {{iters_long}}-iteration runs of seeds
{{m23_other_seeds}} were trained after the verdict (the ledger records them on {{r60_date}}), so the three-seed
figures below extend it
and carry none of its weight. The rule is anchored at
h = {{v2_diag_h}}, the upstream's **open-loop diagnostic** length and not a deployment horizon
(§3.1), and its verdict is returned there; we do not re-anchor a discharged rule. The method's own
horizon is h = {{v2_deploy_h}}, so the comparison is reported there too, and the two differ in size.

**Result.** Every condition {{m23_c1}}. We give the evidence in order of how little it depends
on the small held-out sample.

*The sign test, which does not depend on n.* At h = {{v2_diag_h}} the per-episode gap favours autoregressive training on **{{c3_sign_pos}} of {{c3_sign_n}}** episodes, an exact two-sided binomial test with p = **{{c3_sign_p}}**. At h = {{v2_deploy_h}} it is **{{a1_sign_pos_h100}} of {{a1_sign_n_h100}}**, p = **{{a1_sign_p_h100}}**, and at h = 1 it is {{a1_sign_pos_h1}} of {{a1_sign_n_h1}}, the same story the interval tells. It uses no bootstrap or multiplicity correction, and episodes, unlike §6's state dimensions, are separable units, so a binomial null is admissible. **Its scope is narrower than the arena labels suggest**: {{n_train_eps}} of the {{c3_sign_n}} episodes are training data for *both* arms. The test is a valid **paired** comparison, since both arms saw identical data and an episode-level difference is due to the training rule rather than to memorisation, but it is not ten out-of-sample episodes and does not measure generalisation. The out-of-sample effect size below carries that burden, on {{nind_oos_400}} independent trajectories.

*The in-sample arena, where the sample is larger.* The same comparison on the eight training
episodes has {{nind_ins_400}} independent 400-step trajectories against the held-out arena's
{{nind_oos_400}}, {{nind_ratio}}× more. It gives the same direction at every horizon and checkpoint
but one: at h = 8 after 500 iterations teacher forcing leads in-sample, with an interval that
excludes zero at both trajectory lengths (`results/review_bootstrap_unit.json`).

*The out-of-sample effect size, at every horizon.* At h = {{v2_diag_h}}, the rule's horizon, the
three-seed extension puts autoregressive training at **{{d1_A_mean}} ± {{d1_A_sd}}** against teacher forcing's
**{{d1_B_mean}} ± {{d1_B_sd}}** (standard deviation over seeds, `ddof=1`), a factor of **{{d1_ratio}}×**. Arm B predicts each of the window's {{win_fore}} forecast targets from
true inputs, where the original's teacher forcing is $N = 1$, and the direction holds under both
definitions (Appendix L).
At h = {{v2_deploy_h}}, the method's own imagination rollout length and the
horizon everything in §6 is anchored to, the same three seeds give **{{d1_ratio_h100}}×**.
Quoting one and not the other would be a choice, so we report the curve (Figure 6, Appendix L): same rollouts,
same {{d1_seeds}} seeds at {{iters_long}} training iterations, same held-out arena,
n_independent = {{a1_nind}}, with a cluster bootstrap over whole trajectories. The two floor columns are each arm's error divided by the hold-last floor's, so a value below one beats the floor:

| h | autoregressive | teacher forcing | ratio | gap [95% CI] | excludes 0 | hold-last floor | A ÷ floor | B ÷ floor | episodes A leads |
|---|---|---|---|---|---|---|---|---|---|
| 1 | {{a1_A_h1}} ± {{a1_A_sd_h1}} | {{a1_B_h1}} ± {{a1_B_sd_h1}} | {{a1_ratio_h1}}× | {{a1_gap_h1}} {{a1_gap_ci_h1}} | **{{a1_excl_h1}}** | {{a1_floor_h1}} | {{a1_A_over_floor_h1}}× | {{a1_B_over_floor_h1}}× | {{a1_sign_pos_h1}}/{{a1_sign_n_h1}} |
| 8 | {{a1_A_h8}} ± {{a1_A_sd_h8}} | {{a1_B_h8}} ± {{a1_B_sd_h8}} | {{a1_ratio_h8}}× | {{a1_gap_h8}} {{a1_gap_ci_h8}} | {{a1_excl_h8}} | {{a1_floor_h8}} | {{a1_A_over_floor_h8}}× | {{a1_B_over_floor_h8}}× | {{a1_sign_pos_h8}}/{{a1_sign_n_h8}} |
| 32 | {{a1_A_h32}} ± {{a1_A_sd_h32}} | {{a1_B_h32}} ± {{a1_B_sd_h32}} | {{a1_ratio_h32}}× | {{a1_gap_h32}} {{a1_gap_ci_h32}} | {{a1_excl_h32}} | {{a1_floor_h32}} | {{a1_A_over_floor_h32}}× | {{a1_B_over_floor_h32}}× | {{a1_sign_pos_h32}}/{{a1_sign_n_h32}} |
| **{{v2_deploy_h}}** | **{{a1_A_h100}} ± {{a1_A_sd_h100}}** | **{{a1_B_h100}} ± {{a1_B_sd_h100}}** | **{{a1_ratio_h100}}×** | **{{a1_gap_h100}} {{a1_gap_ci_h100}}** | **{{a1_excl_h100}}** | {{a1_floor_h100}} | **{{a1_A_over_floor_h100}}×** | **{{a1_B_over_floor_h100}}×** | **{{a1_sign_pos_h100}}/{{a1_sign_n_h100}}** |
| 128 | {{a1_A_h128}} ± {{a1_A_sd_h128}} | {{a1_B_h128}} ± {{a1_B_sd_h128}} | {{a1_ratio_h128}}× | {{a1_gap_h128}} {{a1_gap_ci_h128}} | {{a1_excl_h128}} | {{a1_floor_h128}} | {{a1_A_over_floor_h128}}× | {{a1_B_over_floor_h128}}× | {{a1_sign_pos_h128}}/{{a1_sign_n_h128}} |
| **{{v2_diag_h}}** *(the rule's horizon)* | **{{a1_A_h368}} ± {{a1_A_sd_h368}}** | **{{a1_B_h368}} ± {{a1_B_sd_h368}}** | **{{a1_ratio_h368}}×** | **{{a1_gap_h368}} {{a1_gap_ci_h368}}** | **{{a1_excl_h368}}** | {{a1_floor_h368}} | **{{a1_A_over_floor_h368}}×** | **{{a1_B_over_floor_h368}}×** | **{{a1_sign_pos_h368}}/{{a1_sign_n_h368}}** |

**The advantage {{a1_monotone}} grow monotonically with forecast depth.** Over 400-step
trajectories the gap excludes zero at {{a1_n_excl}} of {{a1_n_horizons}} horizons and
spans it at {{a1_spans_zero_at}}. So h = {{v2_diag_h}} is the end of a trend rather than a point we
picked, h = {{v2_deploy_h}} sits partway along it, and the claim is weakest inside the horizon the model is trained on. **Only the h = {{v2_diag_h}} row is the rule's horizon, and the rule ran on seed {{m23_seed}} alone.** Every
value in the table is a three-seed mean computed after the data existed, so by this paper's own standard (§3.4)
none carries a pre-registration's weight. That is the same treatment §6.6 gives the expectation we held about the
counter-baseline, and nothing in the table discharges or re-opens the rule. Teacher forcing is more than
twice as variable across seeds as autoregressive training at h = {{v2_diag_h}}, so a single-seed
comparison of these two arms is unreliable; Appendix L gives the seed spread and the four
per-trajectory gaps, {{a1_gap_traj_n_positive_h368}} of {{a1_gap_traj_n_h368}} positive.

**At h = 1 the table understates the evidence, and the correction runs against us.** The row
rests on {{a1_nind}} independent 400-step trajectories, a unit only the longest horizon needs.
Under a rule committed before the index was built (rule M-64, Appendix E), we rebuilt it at
{{m64_h1_unit}} rows, 32 of history and one forecast step, non-overlapping within an episode:
{{m64_h1_n}} units on the same two episodes. The gap is {{m64_h1_gap}}
{{m64_h1_ci}}: it **excludes zero, in favour of teacher forcing** ({{m64_h1_ratio}}×). Both
readings are reported: the rule above was discharged on the 400-step unit, and the short unit resolves the sign. At one step **autoregressive
training is worse**, the direction the sign test and, on the 400-step unit, the hold-last floor already pointed.

*Against a baseline, because neither number means anything without one.* The hold-last floor,
predicting that nothing changes, scores **{{a1_floor_h368}}** at h = {{v2_diag_h}}, where
autoregressive training beats it by **{{a1_floor_over_A_h368}}×** ({{a1_floor_over_A_h100}}× at
h = {{v2_deploy_h}}) and **teacher forcing is {{a1_B_over_floor_h368}}× worse than assuming nothing
changes at all** ({{a1_B_over_floor_h100}}× at h = {{v2_deploy_h}}). Those are 400-step units, on
which the floor beats teacher forcing at {{a1_B_worse_than_floor_at}} and the autoregressive arm at
{{a1_A_worse_than_floor_at}}. On M-64's shorter units teacher forcing beats the floor at
h = {{m64_B_beats_floor_at}}, and both arms beat it at h = 1 (Appendix L).

**What is small, and where it resolves.** At h = 8, the horizon the model is trained on, the
advantage is small: the table's {{iters_long}}-iteration gap there excludes zero only with all
{{d1_seeds}} seeds pooled. At the {{bu_ckpts}}-iteration checkpoints the out-of-sample gap excludes zero in **{{ab_short_excl}} of {{ab_short_cells}}** h = 8
cells, and an earlier rule anchored there (rule M-16)
returned **{{m16_verdict}}**. **The advantage is small at the training horizon and large beyond
it**: at long horizons the out-of-sample gap excludes zero in **{{ab_long_excl}} of {{ab_long_cells}}** cells at those checkpoints, each
still excluding it after correction for the family of {{c3_family}} comparisons. Appendix L sets
these cells and our arms beside the released checkpoint they reimplement.

**Held out in turn, every episode tests the claim out of sample once.** The {{a1_nind}} trajectories above are one fold. Both arms were trained on {{x3_n_new_folds_word}} more such splits, fixed in advance, so that each episode is held out in exactly one of {{x3_n_folds_word}} (rule X3, committed before the runs; {{iters_main}} iterations, {{d1_seeds}} seeds). Over the {{x3_n}} independent out-of-sample trajectories of all ten episodes, the gap at h = {{v2_diag_h}} is {{x3_gap}} {{x3_ci}}, favouring autoregressive training: **{{x3_reading}}**. All {{x3_eps_pos}} of the {{x3_n_eps}} episodes favour it (P = {{x3_p}}), and every fold's own interval excludes zero, its gap running from {{x3_fold_lo}} to {{x3_fold_hi}} (Appendix L). At one step teacher forcing still leads on short units, {{x3_h1_gap}} {{x3_h1_ci}} over {{x3_h1_n}} {{x3_h1_unit}}-row units. These are {{iters_main}}-iteration models, not the {{iters_long}}-iteration ones behind the factor above, which X3 does not re-read; its interval resamples trajectories, carrying every seed, and its folds pair episodes in index order rather than by speed. The {{a1_nind}} trajectories of §5's arena are no longer the only out-of-sample evidence.

**The data budget, which is the one part of the sample-efficiency claim we can measure (was §5.1)**

The base paper's headline is a sample-efficiency result about policy learning and hardware, which
we cannot test, but its *world-model* half is a quantity we can count exactly: **our arms consume
{{c2_trans}} distinct state transitions, {{c2_ratio}}× less data than the reference's {{c2_ref}},
{{c2_pct}}% of its world-model budget**. On that budget the training result above still
reproduces. Appendix L gives the count and its three limits, the first being that this is not the
policy-learning comparison.

**The configuration claim: history and forecast horizons (was §5.2)**

**Claim under test.** The model reads a history of M past steps and, in training, forecasts the
next N steps from its own predictions. The base paper sweeps both and says that moderate values give
an optimal trade-off between accuracy and training time, with {{mn_centre_label}} as the instance
(§IV-C). Its heatmap prints the error of every cell, and the centre's is the tied-lowest, level with
its longest-forecast neighbour (`docs/presubmission/ORIGINAL_SPECS.md` a.5). Its second heatmap prints training hours: {{orig_h_32_8}} for the centre and {{orig_h_32_32}} for {{orig_tied_label}}, {{orig_h_ratio}}×, so on the original's own figures the centre matches that neighbour's printed error, {{orig_e_32_8}}, in under half the time. Our measured cost per iteration for the same pair is {{n3_cost_M32_N32}}× (the table's last column).

**Rule, committed in advance** (rule M-74, Appendix E). It tests the accuracy half only: whether the centre has the lowest error among its {{mn_n_configs_word}} one-factor neighbours in the original's
grid, M of {{mn_grid_M}} at the centre's N and N of {{mn_grid_N}} at its M. Each is trained as Arm A
is, for {{iters_main}} iterations on {{mn_seeds_word}} seeds. The statistic is a configuration's
relative-L1 at h = {{v2_diag_h}} minus the centre's, averaged over trajectories and tested by an exact
bootstrap over trajectories, with Holm's correction holding the chance of any false "better" in the
family at α = 0.05. Training time is reported and governs nothing: hours on
two CPU cores are not what the original timed on a GPU.

| (M, N) | relative-L1, h = {{v2_deploy_h}} | relative-L1, h = {{v2_diag_h}} | difference from the centre [95% interval] | result | cost per iteration, relative to the centre |
|---|---|---|---|---|---|
{{mn_table}}

**Arena: {{h2h_arena}}, episodes {{h2h_episodes}}, {{h2h_ntraj}} non-overlapping {{h2h_unit}}-step trajectories, n_independent = {{mn_nind}}.** Each row is the
mean over {{mn_seeds_word}} seeds at {{iters_main}} iterations (`results/mn_sweep_eval.json`). A
difference is positive when the centre is better, and "result" is after Holm
(`results/mn_sweep_verdict.json`). The last column is a configuration's steady training time per
iteration over the centre's, timed without contention (`results/mn_compute_matched.json`); hours per
run, and the {{mn_n_overlapped}} of {{rt_sweep_runs}} sweep runs that overlapped other logged CPU work,
are in Appendix B. The hold-last floor is {{mn_floor_h100}} at h = {{v2_deploy_h}} and {{mn_floor_h368}} at h = {{v2_diag_h}}.
The nRMSE readings quoted alongside the rules here and in §5.3 are pooled as §3.1 defines it,
recomputed afterwards (post hoc; Appendix U).

**Result: {{mn_verdict}}.** {{mn_better_list}} beat the centre ({{mn_better_kinds}}), {{mn_worse_list}} are worse, and
{{mn_unres_list}} cannot be told apart from it. At h = {{v2_diag_h}} the lowest error is {{mn_best_config}}'s,
{{mn_best_l1_h368}} against the centre's {{mn_centre_l1_h368}}, a difference of {{mn_best_D}}
{{mn_best_ci}}. The verdict does not rest on the anchor: on the in-sample arena's {{mn_nind_ins}} independent {{h2h_unit}}-step trajectories, {{mn_insample_clause}}, and among the held-out readings the rule
reports alongside, {{mn_alongside_clause}}. Per configuration, no reading puts the centre ahead of any of the {{mn_n_better_word}} winners, though several leave a winner unresolved: {{mn_winner_unres_clause}}. Per episode, {{mn_winner_episode_clause}}.

**At our budget, shorter histories win.** The original's error falls steeply
from M = 1 to M = 8 and then flattens (`ORIGINAL_SPECS.md` a.5). On the governing reading ours does
not fall steeply: {{mn_mvar_better_list}}, histories shorter than the centre's, beat it, and no
shorter history is resolvably worse. Other readings the rule reports, though, put shorter histories
behind it: {{mn_mvar_other_worse}}. That is a statement about learning speed at this budget, not about converged accuracy: trained {{n3_long_factor_word}} as long, the centre passes both winning shorter histories on {{n3_sh_long_nread_word}} of the {{n3_n_readings_word}} readings (Appendix U). So it does not contradict the original's steep fall to M = 8, whose training budget the original does not state. The original's direction on N holds: the shortest forecasts
are far worse, which is §5's teacher-forcing result again, and the longest are better, so the
centre's tie with its longest-forecast neighbour becomes a loss.

**Accuracy at equal compute (post hoc).** The shorter histories that win cost less per iteration
than the centre, {{n3_cost_M8_N8}}× for {{n3_sh_label_M8_N8}} and {{n3_cost_M2_N8}}× for
{{n3_sh_label_M2_N8}}, so their wins at {{iters_main}} iterations need no compute correction. The
longer forecasts' wins do. Trained to {{n3_k_mid}} iterations, {{n3_best_over_mid}}× the computation of
{{mn_best_config}}, the centre splits the readings with it; trained to {{iters_long}},
{{n3_best_over_long}}× its computation, it is ahead on both in-sample readings and neither held-out
difference is resolved. Which setting is most accurate therefore depends on how long each is
trained (Appendix U gives every reading); none of this re-opens rule M-74.

**Limits.** One factor is varied at a time, so no interaction between M and N is tested. Our data
budget is {{c2_pct}}% of the reference's (§5.1), and the original states neither the ablation's
budget, its evaluation data nor the horizon behind its error, so the verdict holds at our budget and
no further: a larger one may favour a longer history. All {{tail_n}} runs at {{iters_main}} iterations are still lowering their training loss at the end
(post hoc; Appendix U), so the ranking is at this budget, not at convergence, and it changes with
training length. With {{mn_nind}} independent trajectories, the rule's minimum detectable effect at h = {{v2_diag_h}},
the difference its first Holm step would usually detect, is about {{mn_mde_h368}}% of the centre's
error.

**The architecture claim: MLP, RSSM and transformer baselines (was §5.3)**

**Claim under test.** The base paper compares RWM with three **architecture baselines**: other network designs trained on the same data to make the same predictions. They are a multilayer
perceptron (MLP) over a flattened window of history; a recurrent state-space model (RSSM; Hafner et al., ICML 2019), in the form DreamerV2 refined (Hafner et al., ICLR 2021); and a decoder-only transformer. It says RWM
"consistently achieves the lowest prediction errors across all environments" (§IV-D), gives no number (Fig. 7), and trains the baselines teacher-forced.

**What we built.** The pinned upstream code has an MLP but no RSSM or transformer, so all three are ours, the MLP following the upstream one. They follow the shapes in the original's Table
S7 as we read it, with {{bl_params_list}} parameters against RWM's
{{bl_rwm_params}}. Where the table is silent they take RWM's data, windows, objective, optimiser,
iterations and seeds, and the RSSM takes its latent, activation and KL settings from DreamerV2. Each choice is a row of
`docs/presubmission/BASELINE_SPECS.md`. Only the predicted state is compared.

**Two rules, committed in advance** (M-75 and M-76, Appendix E). M-75 trains the baselines
teacher-forced, as the original does. M-76 trains them autoregressively, as RWM is, so that training rule and architecture are not confounded. Both take Arm A at {{iters_main}} iterations
as RWM and test each baseline's relative-L1 at h = {{v2_diag_h}} against it, on §5.2's arena with
§5.2's bootstrap and Holm correction.

| model | parameters | relative-L1, h = {{v2_deploy_h}} | relative-L1, h = {{v2_diag_h}} | difference from RWM [95% interval] | result | cost per iteration, relative to RWM |
|---|---|---|---|---|---|---|
{{bl_table}}
{{x4_table_rows}}

**Arena as in §5.2: {{h2h_arena}}, {{h2h_ntraj}} non-overlapping {{h2h_unit}}-step trajectories, n_independent = {{mn_nind}}.** Each row is the mean over
{{mn_seeds_word}} seeds at {{iters_main}} iterations (`results/baselines_eval.json`). A difference is
positive when RWM is better, and "result" is after Holm (`results/baselines_verdict.json`). The last
column is timed beside RWM in one sitting (`results/mn_compute_matched.json`); hours per run are in
Appendix B. † marks a diverged row, whose mean run-away rollouts dominate; no verdict depends on that
magnitude, only on the sign, which favours RWM on every trajectory (Appendix L). The two size-matched rows (rule X4) are trained autoregressively for {{iters_main}} iterations on {{mn_seeds_word}} seeds and scored on the same arena (`results/x4_matched_baselines.json`); they were not timed in that sitting, so their last cell is empty.

**Result: {{bl_tf_verdict}} with the baselines teacher-forced, and {{bl_ar_verdict}} with them
trained autoregressively.** RWM is ahead of baselines built to our reading of Table S7 and trained
with RWM's settings for {{iters_main}} iterations: all {{bl_n_rows_word}} comparisons favour it, with
intervals that exclude zero. That says less than it seems at h = {{v2_diag_h}}, where every baseline
row, in both regimes, is above the hold-last floor and RWM is below it: no baseline beats predicting
no change. The second verdict compares architectures at one training regime and is not a verdict on
the original's claim, which the first carries. The lead is a long-horizon one, and the rules'
relative-L1 readings at other horizons on the held-out pair say where it starts. Teacher-forced, the baselines fall
resolvably behind from {{bl_tf_lead_from}} (the transformer from {{bl_tf_tr_lead_from}}).
Trained autoregressively, the RSSM falls behind from {{bl_ar_rssm_lead_from}}, but the MLP and the transformer only from {{bl_ar_lead_from}}, the method's own horizon, where they trail by
{{bl_ar_mlp_D_h100}} {{bl_ar_mlp_ci_h100}}, about {{bl_ar_mlp_pct_h100}}% of RWM's
{{h2h_armA_l1_h100}}, and {{bl_ar_tr_D_h100}} {{bl_ar_tr_ci_h100}}. Before those horizons, on the held-out pair, a baseline
cannot be told apart from RWM: at h = 1 both rules return {{bl_tf_h1}}, and at h = 8 both return
{{bl_tf_h8}}. Post hoc, with nRMSE pooled as §3.1 defines it, {{n2_n_changed_word}} in-sample readings differ
from the per-trajectory average the rules' evaluator used. Teacher-forced, all three baselines lead
RWM at h = 1 (M-75's reading there becomes {{n2_m75_pooled}}, from {{n2_m75_committed}}), the same
one-step lead for teacher forcing as §5's. Trained autoregressively, the MLP's deficit at
h = {{v2_deploy_h}} is no longer resolved ({{n2_m76_pooled}}, from {{n2_m76_committed}}; Appendix L).
Neither changes a verdict; both rules govern at h = {{v2_diag_h}} on relative-L1.

**Our RSSM is not an informative comparison.** Teacher-forced, it has collapsed open-loop by h = 32
({{x1_tf_mode_h32}} against the floor's {{x1_floor_h32}}), and trained autoregressively it does not
perform comparably to RWM, as the original says an RSSM does ({{h2h_bl_rssm_ar_l1_h368}} against
{{bl_rwm_l1_h368}} at h = {{v2_diag_h}}). A diagnostic committed before its readings existed (rule
X1, exploratory; it re-opens neither rule) returns **{{x1_reading_a}}** for its Part A, which reads
the forecast from other latents, and **{{x1_final_reading}}** for its Part C, which retrains the
model. The failure may still be our RSSM rather than the architecture (Appendix L), so the
architecture claim rests on the MLP and the transformer.

**Limits.** One robot on flat ground; the original has several environments. The baselines
are our reading of a table that fixes their shapes and nothing else. Their loss, optimiser and
budget are RWM's, not tuned for them. Their sizes are Table S7's. Matched to RWM's parameter count instead (rule X4, committed before the runs; the table's last two rows), the autoregressive MLP and transformer return **{{x4_reading}}**. At h = {{v2_diag_h}} the MLP trails RWM by {{x4_D_mlp}} {{x4_ci_mlp}} ({{x4_res_mlp}}), and the transformer's {{x4_D_tf}} {{x4_ci_tf}} cannot be settled (p = {{x4_p_tf}}; {{x4_res_tf}}), as at h = {{v2_deploy_h}} and h = 32, which return {{x4_alongside_reading}} too. Matching the parameter count is one axis; the shapes and settings stay our reading of Table S7, and the size-matched RSSM was not run. With {{mn_nind}} independent trajectories, the minimum detectable effect at h = {{v2_diag_h}} is
about {{bl_mde_h368}}% of RWM's error, well below every difference here.

---

---

## S20 The earlier section 6.1

*Was the paper's section 6.1 before the rewrite for the review of 19 October; moved here whole with the rest of that section (S20 to S27). Section numbers in this passage are the earlier paper's.*

**Neither of the checkpoint's uncertainty outputs is usable as an interval (was §6)**

*How this section runs.* §6.1–§6.2 settle which quantity the method uses and measure it; §6.3–§6.4 examine why each output fails; §6.5–§6.6 separate the magnitude of the failure from its ordering, and test the ordering against free baselines; §6.7–§6.8 ask what would fix it.

**Which quantity the method actually uses (was §6.1)**

The released checkpoint emits **two** uncertainty quantities, and the method consumes only one of
them. This has to be settled before any calibration number means anything.

`system_dynamics.py:125` computes an **aleatoric** term, the mean over ensemble members of each
member's predicted σ. `system_dynamics.py:126` computes an **epistemic** term, the standard
deviation across the members' mean predictions. In `envs/base.py:142` the aleatoric term is bound
to a local variable that is never read again; the epistemic term is stored, returned to the policy
loop at `:158`, and applied at `:166` as a reward penalty with weight −1.0.

The paper agrees with its code. arXiv:2504.16680**v1** Eq. 4 defines the penalised quantity as
$u = \mathrm{Var}_b[\mu_b]$, the variance across ensemble members (the numbering is unchanged in
the current {{v4_current}}), and Eq. 5 applies it as $\tilde{r} = r - \lambda u$. The per-member
predicted variance enters the training objective and nothing downstream.

Eq. 4 specifies a **variance** where `system_dynamics.py:126` computes a **standard deviation**,
which with $\lambda = 1$ differ by a square. The first author confirms that the code's quantity is the
intended one, and that the aleatoric term is reported for analysis and never used downstream
(personal communication, quoted with the first author's permission; supplementary S5 gives the exchange).
We measure the code's quantity throughout. So the discard is the intended design, not an
implementation slip. We report both quantities below. Our own arms are ensemble size 1, where the
epistemic term is identically zero by construction, so the epistemic measurement is possible only
on the released checkpoint.

**What the follow-up does and does not claim.** It does not claim its uncertainty is a calibrated
interval. Its §3.2 claims the epistemic term "closely follows the trend of the prediction error"
and that this "justifies its role as a trust metric", and of the aleatoric term it observes only
that it "remains low, reflecting small stochasticity in the environment". Our measurement **supports the first claim**: the epistemic ordering is real (§6.6), though weaker per dimension than it looks (§6.5). What follows is therefore
not a refutation of a calibration claim nobody made, but three things the papers do not address:
that the aleatoric head is discarded before use, that neither quantity is usable as a scale, and
that the low aleatoric value has a different cause than the one offered.

---

## S21 The earlier section 6.2

*Was the paper's section 6.2 before the rewrite for the review of 19 October; moved here whole with the rest of that section (S20 to S27). Section numbers in this passage are the earlier paper's.*

**The measurement (was §6.2)**

For each model we compute the mean predicted σ, the mean absolute realised error, and the fraction
of realised errors falling inside ±1σ. A calibrated Gaussian puts {{v3_cov_nominal1}}% inside ±1σ (§3.1).

On the held-out pair, the only arena on which our arms can be scored fairly (n_independent =
{{b2_nind}} 400-step trajectories), every model's aleatoric head is overconfident by between one and four orders of magnitude over the whole {{v2_diag_h}}-step rollout (Figure 7; Appendix M gives the four models' table); for the released checkpoint that arena is in-sample (the in-sample caveat of §3). That is the quantity §6.1 shows the method discards.

**The quantity the method does use is also uncalibrated.** It is measured on the released {{b2_members}}-member checkpoint over all {{d1n_eps}} episodes, at n_independent = **{{d1n_nind}}** non-overlapping 400-step trajectories. The checkpoint trained on all ten, so restricting it to the held-out pair would buy no independence and cost four fifths of the sample; Appendix M compares that version with this one.

| h | aleatoric err/σ [95% CI] | aleatoric ±1σ | epistemic err/σ [95% CI] | epistemic ±1σ [95% CI] | epistemic ±2σ | dims r>0 | permutation P |
|---|---|---|---|---|---|---|---|
| 1 | {{d1n_alea_ratio_h1}}× [{{d1n_alea_ratio_ci_h1}}] | {{d1n_alea_cov1_h1}}% | **{{d1n_epi_ratio_h1}}×** [{{d1n_epi_ratio_ci_h1}}] | {{d1n_epi_cov1_h1}}% [{{d1n_epi_cov1_ci_h1}}] | {{d1n_epi_cov2_h1}}% | {{d1n_epi_npos_h1}}/{{d1n_epi_ndim_h1}} | {{perm_all_epi_p_h1}} |
| **{{v2_deploy_h}}** | {{d1n_alea_ratio_h100}}× [{{d1n_alea_ratio_ci_h100}}] | {{d1n_alea_cov1_h100}}% | **{{d1n_epi_ratio_h100}}×** [{{d1n_epi_ratio_ci_h100}}] | {{d1n_epi_cov1_h100}}% [{{d1n_epi_cov1_ci_h100}}] | {{d1n_epi_cov2_h100}}% | {{d1n_epi_npos_h100}}/{{d1n_epi_ndim_h100}} | {{perm_all_epi_p_h100}} |

*The h = 1 and h = {{v2_deploy_h}} rows; Appendix M gives every horizon. No permutation P in the arena survives Holm–Bonferroni, so that column is a consistency check on direction only.*

**Read the h = 1 row first.** At one step the disagreement the method penalises rewards with is
already **{{d1n_epi_ratio_h1}}× [{{d1n_epi_ratio_ci_h1}}]** smaller than realised error, with ±1σ
coverage of {{d1n_epi_cov1_h1}}% [{{d1n_epi_cov1_ci_h1}}] against a calibrated
{{v3_cov_nominal1}}%. The discarded per-member σ is {{d1n_alea_ratio_h1}}× out at h = 1 as well.
Everything further down the table is deterioration from a starting point that is already broken.

**Why that row, and not the deep ones.** The obvious objection is that a per-step σ is a
*conditional* quantity: it says how uncertain the next state is given this input, and in an
open-loop rollout the input is the model's own previous output, wrong by an amount σ never claimed
to describe. Comparing it with *accumulated* rollout error would then make the {{v2_diag_h}}-step
figure an artifact of that mismatch. (§6.5 answers a different objection, that a model trained on
{{win_fore}} steps cannot be expected to speak about {{v2_diag_h}}.) **h = 1 answers it at no extra
cost.** At one step there is no accumulation: the input *is* the true state, and σ is asked exactly
the question it was trained to answer, and the row above is its answer: whatever compounding does at depth, it did not produce that row.

**And that row is measured on data the checkpoint trained on**: all ten episodes, {{insample_n_overlap}} of {{insample_n_arena}} of them (`results/insample_framing.json`). In-sample measurement biases *toward* better calibration, so the {{d1n_epi_ratio_h1}}× at h = 1 is if anything flattering: an upper bound on how well this checkpoint is calibrated. So the horizon curve is not the claim; it is the shape of the deterioration, and the claim is the h = 1 row. We keep h = {{v2_deploy_h}} because it is where the method actually deploys, and h = {{v2_diag_h}} because it is the upstream's own diagnostic length.

At h = {{v2_deploy_h}}, the method's own imagination rollout length, epistemic is
{{d1n_epi_over_alea_h100}}× better than aleatoric and still wrong by
**{{d1n_epi_ratio_h100}}× [{{d1n_epi_ratio_ci_h100}}]**, with ±1σ coverage of
{{d1n_epi_cov1_h100}}% [{{d1n_epi_cov1_ci_h100}}] where a calibrated Gaussian gives
{{v3_cov_nominal1}}%. At one step epistemic is
{{d1n_epi_over_alea_h1}}× better than aleatoric, and at h = {{v2_diag_h}} {{d1n_epi_over_alea_h368}}×. **The gap between the two uncertainty terms is itself
horizon-dependent, which is why each figure above names its horizon.** At the open-loop diagnostic horizon of h = {{v2_diag_h}} it is {{d1n_epi_ratio_h368}}× [{{d1n_epi_ratio_ci_h368}}] with {{d1n_epi_cov1_h368}}% coverage, barely different from h = {{v2_deploy_h}}. **Total** uncertainty, `sqrt(aleatoric² + epistemic²)`, equals the epistemic value to four significant figures at every horizon, because the aleatoric term is too small to move it.

**A constant scale error would not matter, and this one is not constant.** The penalty enters as `r̃ = r − λu`, so a `u` uniformly `c` times too small is arithmetically identical to running with `λ/c`, and λ is tuned. Rescaling σ by the single constant that best calibrates it, fitted and scored on the same data and so an upper bound on what *any* constant achieves, needs {{m65_c_h1}} at h = 1 and {{m65_c_h368}} at h = {{v2_diag_h}}, a factor of {{m65_c_growth}} across the rollout (a rule committed in advance; Appendix E). No single λ is both of those. The mechanism is §6.5's: σ grows far more slowly than error, which grows by an order of magnitude, so the ratio runs {{d1n_epi_ratio_h1}}× at h = 1, {{d1n_epi_ratio_h100}}× at h = {{v2_deploy_h}} and {{d1n_epi_ratio_h368}}× at h = {{v2_diag_h}}. The penalty is applied at every step of a {{v2_deploy_h}}-step imagination rollout, so its *profile across the rollout* is wrong in a way no rescaling can correct: deep-rollout states are under-penalised relative to their realised risk. This bounds what the quantity reports across depth, not what the distortion costs a trained policy (the policy caveat of §11).

**Two rules committed in advance check how these numbers are read** (Appendix M). Resampling whole
episodes rather than 400-step trajectories changes no verdict in the one arena with the power to
show it, the out-of-sample cells being uninformative by design (rule M-62: **{{m62_verdict}}**). The epistemic term's one-step coverage failure is spread across the {{d1n_epi_ndim_h1}} state
dimensions rather than carried by a few (rule M-63: **{{m63_verdict}}**).

**The released checkpoint is no longer the only ensemble measured.** Three Arm A arms at ensemble size 5
(§6.6; out-of-sample, n_independent = {{e5_nind}} 400-step trajectories, {{iters_main}}
training iterations) are **better calibrated than the released checkpoint and fail the same way**:
{{e5_ratio_h100}}× [{{e5_ratio_ci_h100}}] overconfident at h = {{v2_deploy_h}} against its
{{b2_epi_ratio_h100}}× on the same held-out pair, with {{e5_cov1_h100}}% coverage where a calibrated
Gaussian gives {{v3_cov_nominal1}}%. §6.4 establishes that the two are the same architecture in the
respect that matters here, and Appendix M gives the arms' table at every horizon.

The scalar penalty as actually applied, `means.std(0).sum(-1)` at `envs/base.py:166`, correlates **{{d4_r}}** with total absolute error over the rollout, 95% CI {{d4_ci}} from a bootstrap over whole trajectories, n_independent = {{d4_nind}} ({{d4_npoints}} pooled trajectory-step points). The interval resamples whole trajectories, not trajectory-step pairs, which would narrow it by about the square root of the rollout length.

---

## S22 The earlier section 6.3

*Was the paper's section 6.3 before the rewrite for the review of 19 October; moved here whole with the rest of that section (S20 to S27). Section numbers in this passage are the earlier paper's.*

**Why the aleatoric head collapses: the optimum is σ = 0 (was §6.3)**

This subsection explains the aleatoric column and only that column, and leaves the epistemic one
open: ensemble disagreement is not shaped by the mechanism below, and why *it* is miscalibrated is not established here. It also
supplies the alternative explanation promised in §6.1. The follow-up reads the low aleatoric value
as reflecting "small stochasticity in the environment". The observation is correct and the reading
is not: σ is low because σ = 0 is the optimum of the loss that trains it, and it would be low on
any dataset, stochastic or not.

The state loss is squared error on a *sample* drawn from the predicted Gaussian, not a likelihood:

$$\mathcal{L} \;=\; \mathbb{E}\big[(\mu + \sigma\varepsilon - y)^2\big] \;=\; (\mu - y)^2 + \sigma^2$$

which is minimised at σ = 0 for any μ. There is no log-σ term to oppose it. The bound term that
appears to oppose it does not, because `max_logstd` is not an independent parameter — it is
constructed as `min_logstd + exp(log_delta_logstd)`, so

$$\overline{\log\sigma_{\max}} - \overline{\log\sigma_{\min}} \;=\; \overline{\exp(\log\Delta_{\log\sigma})}$$

and `min_logstd` cancels algebraically, taking no gradient from that term. The floor the interval
closes onto therefore freezes while the interval closes: a one-way ratchet.

**The derivation above covers two terms, and the objective has {{e4_n_terms}}.** Back-propagated
one at a time, exactly {{e4_n_touch}} reach σ ({{e4_touching}}) and the other {{e4_n_inert}} give a
gradient of exactly zero (Appendix J).

**The derivation says the collapse happens on any dataset, and that is testable.** Under a rule
committed before the runs (rule M-50, Appendix E) we trained the released head, unmodified but over a
one-dimensional state with no recurrent trunk, on synthetic data whose known noise varies
{{e5s_span}}× across the input range. **Under the implemented objective σ sits {{e5s_mse_under}}× below
the true noise and does not track it at all**, while under the authors' unused likelihood branch it
recovers the true level to a median ratio of {{e5s_nll_ratio}}, seed-variably. The rule returns
**{{e5s_verdict}}**, which establishes the contrast and not the size of the recovery (Appendix J).

We predicted the collapse from this algebra before training, then observed it: across all {{n_runs}} runs at the released width outside §4.2's sweep the log-σ range moves linearly in iteration count, falling under sampled MSE and rising under the corrected one (Figure 4a; Appendix J lists the runs and which the rate is fitted on). Figure 2 shows the same runs through σ itself: panel (a) draws the two bounds σ can take, and panel (b) divides the change in log Δ per iteration by the learning rate, which is where the Adam optimiser's step size shows.

**Two different things are being explained here, and §6.5 separates them.** *Magnitude collapse
is objective-driven.* It occurs in all {{e2_mse_runs}} sampled-MSE runs at a rate of
{{e2_mse_rate}} per iteration with a standard deviation of {{e2_mse_sd}}, **including the
teacher-forced arm**, which shares the objective, and reverses to {{e2_nll_rate}} in the
{{e2_nll_runs}} runs that change it. *Input-independence is not.* It varies by a factor of
{{cal_armB_over_faithA_cov}} between two arms trained under the same objective, so the objective
cannot be what produces it.

Under the corrected objective the sign flips (Figure 4b), the strongest evidence that the mechanism
is the objective and not the optimiser, the data or the architecture.

**The correction fails differently rather than succeeding.** The reference contains an unused `gaussian_nll` branch. Running it reverses the collapse and
improves the magnitude from {{cal_faithA_ratio}}× to {{cal_nll_ratio}}× overconfident. It does not produce a usable estimate, and it destroys something the faithful arm had: the σ-versus-error ordering falls from {{cal_faithA_npos}}/{{cal_faithA_ndim}} dimensions positively correlated to {{cal_nll_npos}}/{{cal_nll_ndim}}, which is chance. Neither ordering survives multiplicity correction (Appendix J).

---

## S23 The earlier section 6.4

*Was the paper's section 6.4 before the rewrite for the review of 19 October; moved here whole with the rest of that section (S20 to S27). Section numbers in this passage are the earlier paper's.*

**Why the epistemic term may be miscalibrated: the members are not independent models (was §6.4)**

§6.3 explains the aleatoric column and leaves the epistemic one open. This subsection supplies a
candidate, structurally symmetric to §6.3's, from source and from the checkpoint's own tensors;
nothing here is trained and nothing is inferred from a measurement. The effect is known (§2). What
is ours is finding it in a released robotics checkpoint, with the sharing quantified at {{v1_shared_pct}}% of each member and its cost bounded by the {{m44_ratio_gain}}× an independent ensemble gains on the overconfidence factor (§6.8).

**The released five-member ensemble is not five models.** The code builds one trunk, replicates only the heads,
evaluates the trunk once and hands every head the same feature vector, then takes the spread across
the heads as the epistemic term (Appendix J gives the lines).

The parameter counts make the scale of the sharing concrete. The state pathway is a
{{v1_shared_params}}-parameter two-layer GRU trunk plus {{v1_members_word}} heads of
{{v1_private_params}} parameters each. Per member, {{v1_shared_params}} of
{{v1_member_params}} parameters — **{{v1_shared_pct}}%** — are numerically identical to every
other member's. Only {{v1_private_pct}}% differ. Across the whole released object, the two shared
trunks are {{v1_shared_pct_model}}% of {{v1_total_params}} parameters.

**The sharing is stronger than the parameter count suggests.** The trunk owns a *single* recurrent
hidden state (`rnn.py:40`), and an autoregressive rollout feeds the ensemble **mean** back into it
(`system_dynamics.py:115`; `src/rwm_model.py:223` in our reimplementation). So the
{{v1_members_word}} members do not roll out independently at all. There is exactly
{{v1_hidden_states_word}} hidden-state trajectory between them, and disagreement at step *t* is the
spread of {{v1_members_word}} two-layer MLPs read off a single 256-dimensional vector.

**Members which share a feature extractor have correlated errors by construction, and their spread
cannot express uncertainty the shared trunk does not already carry.** Where a deep ensemble varies
initialisation *and* data ordering across whole models, here only the output heads differ, so the
quantity the method penalises rewards with is a lower bound on epistemic uncertainty by
construction. It is the same shape of finding as §6.3: not a training failure, a structural one.

**This applies to our own arms identically, which is why §6.2's comparison is fair.** Our
ensemble-5 arms build, evaluate and read their trunk the same way, and their tensor names and
parameter counts match the released checkpoint's exactly on all {{v1_n_arms_checked}} arms checked
(`results/v1_ensemble_topology.json`; Appendix J), so §6.2's comparison is of two instances of one
architecture.

**What this is and is not.** It is a *candidate* mechanism, established structurally. It does not
show that trunk-sharing is *the* explanation for §6.2's miscalibration; architecture could be a
minor contributor to a failure dominated by something else. That needs an ensemble which shares nothing, pre-registered and reported in §6.8. The topology is a fact
about the released artifact; the mechanism is a hypothesis about that fact.

---

## S24 The earlier section 6.5

*Was the paper's section 6.5 before the rewrite for the review of 19 October; moved here whole with the rest of that section (S20 to S27). Section numbers in this passage are the earlier paper's.*

**The failure is one of magnitude; the ordering is weaker than it looks (was §6.5)**

Adding the teacher-forced arm, trained for §4.1, sharpens the finding (our arms at {{iters_main}} training iterations; the released checkpoint as released). Arm B's σ is {{cal_armB_over_faithA_cov}}× more input-dependent than the faithful arm's, and it has the largest mean correlation of the four (r = {{cal_armB_r}}). It is still {{cal_armB_ratio}}× overconfident. So σ *collapsing in magnitude* is objective-driven, and σ *becoming input-independent* is not: the teacher-forced arm collapses in magnitude exactly like the autoregressive ones, same objective and same rate, while keeping that variation across inputs. Appendix K gives the four models' table, its arenas and a candidate mechanism.

**The same pattern holds for the quantity the method uses.** On the held-out pair (n_independent = {{b2_nind}} 400-step trajectories, in-sample for the checkpoint), the epistemic term correlates positively with realised error on **{{b2_epi_npos_h368}} of {{b2_epi_ndim_h368}}** dimensions at h = {{v2_diag_h}} while being {{b2_epi_ratio_h368}}× overconfident there, and its σ grows {{b2_epi_sigma_growth}}× from h = 1 to h = {{v2_diag_h}} while its error grows {{b2_epi_err_growth}}×. Under a permutation null that keeps the coupling between dimensions, nothing in this family survives Holm–Bonferroni in any of the three arenas, and out of sample at the 400-step unit nothing could, since its smallest attainable P already exceeds the smallest Holm threshold: at h = {{v2_diag_h}} the tests are underpowered at every sample size we can reach (Appendix K).

So this section's claim is: **the magnitude failure is established and large; the ordering points the right way for the epistemic term and the faithful and teacher-forced arms, not for the corrected arm or the released aleatoric head (supplementary S3), and is not established at conventional significance once the dependence between dimensions is respected. The failure is specifically magnitude calibration, in both components.**

**The structural excuse does not survive.** One could argue that a model trained on an 8-step horizon cannot be expected to report calibrated
uncertainty about step 368. It cannot report it about step 8 either. Inside the trained horizon,
σ is flat while error grows (Figure 5; {{sig_arena}}, n_independent = {{sig_nind}} 400-step trajectories, in-sample for the released checkpoint; Appendix K gives all four models): the faithful arm's σ *declines* ({{sig_faithA_growth}}×) while its error grows
{{err_faithA_growth}}×. The coverage collapse in Figure 7(b) is therefore driven entirely by
growing error against a fixed σ.

---

## S25 The earlier section 6.6

*Was the paper's section 6.6 before the rewrite for the review of 19 October; moved here whole with the rest of that section (S20 to S27). Section numbers in this passage are the earlier paper's.*

**Ensemble disagreement beats the trivial baseline (was §6.6)**

The follow-up justifies ensemble disagreement as a trust metric on the grounds that it "closely follows the trend of the prediction error". §6.5 shows the per-dimension version of that claim is weaker than it looks. This section finds that the *scalar* the method applies tracks error well, which coexists with §6.5 without contradiction, and asks the question that matters more to a practitioner: **does disagreement beat something free?** The quantity is a usable ranking signal and is still not an interval.

Error in an autoregressive rollout grows with depth, so the trivial competitor to any trust metric is the forecast step index — a counter. It needs no ensemble, no second forward pass and no model. If a counter ranks error as well as disagreement does, the ensemble is not earning its cost. Neither paper runs this comparison, so we do. All three correlations below are on the scalar the method applies, `means.std(0).sum(-1)` at `envs/base.py:166`, against total absolute error, on the released checkpoint over all ten episodes, n_independent =
{{d1n_nind}} trajectories, with 95% intervals from a bootstrap over whole trajectories.

| h | r(step index, \|error\|) | r(disagreement, \|error\|) | partial r(disagreement, \|error\| · index) | paired difference, disagreement − index |
|---|---|---|---|---|
| **1** | — | **{{d2_epi_h1}}** {{d2_epi_ci_h1}} | — | — |
| 8 | {{d2b_idx_h8}} {{d2b_idx_ci_h8}} | **{{d2b_epi_h8}}** {{d2b_epi_ci_h8}} | {{d2b_par_h8}} {{d2b_par_ci_h8}} | {{d2p_diff_h8}} {{d2p_ci_h8}} |
| 32 | {{d2b_idx_h32}} {{d2b_idx_ci_h32}} | **{{d2b_epi_h32}}** {{d2b_epi_ci_h32}} | {{d2b_par_h32}} {{d2b_par_ci_h32}} | {{d2p_diff_h32}} {{d2p_ci_h32}} |
| **{{v2_deploy_h}}** | {{d2b_idx_h100}} {{d2b_idx_ci_h100}} | **{{d2b_epi_h100}}** {{d2b_epi_ci_h100}} | {{d2b_par_h100}} {{d2b_par_ci_h100}} | {{d2p_diff_h100}} {{d2p_ci_h100}} |
| 128 | {{d2b_idx_h128}} {{d2b_idx_ci_h128}} | **{{d2b_epi_h128}}** {{d2b_epi_ci_h128}} | {{d2b_par_h128}} {{d2b_par_ci_h128}} | {{d2p_diff_h128}} {{d2p_ci_h128}} |
| 368 | {{d2b_idx_h368}} {{d2b_idx_ci_h368}} | **{{d2b_epi_h368}}** {{d2b_epi_ci_h368}} | {{d2b_par_h368}} {{d2b_par_ci_h368}} | {{d2p_diff_h368}} {{d2p_ci_h368}} |

*(h=1 has a single forecast step, so the index is constant and its correlation — and therefore the partial and the difference — undefined. The epistemic correlation is not, and it is the largest anywhere in this work: at one step, ensemble disagreement is very nearly a perfect ranking of realised error.)*

**Disagreement wins at every horizon tested.** Over the full h = {{v2_diag_h}} rollout the counter reaches {{d2b_idx_h368}} against disagreement's {{d2b_epi_h368}}, and the index leads in {{d2b_n_index_wins}} of {{d2b_n_horizons_tested}} horizons.

**The last column is the test of whether disagreement beats the counter.** Both correlations are measured on the *same* trajectories, so the paired difference, resampling whole trajectories and recomputing *both* inside each draw, is the right test (Appendix N). It excludes zero at **{{d2p_n_separating}} of {{d2p_n_horizons}}** horizons. The distinction matters at {{d2p_n_overlap}} of them: at {{d2p_overlap_h}} the marginal intervals *do* overlap. {{d2b_idx_strongest_h}} is where the counter is strongest ({{d2b_idx_h128}}) and the margin narrowest: the paired difference there is {{d2p_diff_h128}} {{d2p_ci_h128}}, which excludes zero only just: {{d2p_narrowest_lo}} is the smallest lower bound in the table, at the 400-step unit. At h = {{v2_deploy_h}} the paired difference is {{d2p_diff_h100}} {{d2p_ci_h100}}, which also excludes zero.

**The third column asks whether disagreement merely re-encodes the clock.** Partialling the step index out of both variables *lowers* disagreement's correlation by {{d2b_shrink_all_abs}}, from {{d2b_epi_all}} to {{d2b_par_all}}. Almost none of what disagreement knows is explained by how deep into the rollout you are: it carries real information about *this* rollout.

**What survives removing each confound** (Appendix N). Across {{d2r_ncontrols}} models of how far
into the rollout a step is, the weakest figure is {{d2r_weakest}}, so disagreement is not
re-encoding the clock; but the pooled figure is in large part a between-rollout effect, so the
statistic that matters holds both the rollout and the depth constant. Pre-registered as rule M-45,
it gives {{a2_rdd}} {{a2_rdd_ci}} at n_independent = {{a2_nind}} 400-step trajectories, and the rule returns
**{{m45_verdict}}**: disagreement still tracks error rather than merely reporting which episode is
hard.

Per horizon, the within-rollout effect is materially smaller than the pooled figure and not
established at short horizon (Appendix N gives its table).

**Does it hold on a model we trained?** Three Arm A arms at ensemble size 5 lead the index in
**{{e5_lead_cells}} of {{e5_total_cells}}** seed-horizon cells, but under a rule committed before the
runs (rule M-43) the paired difference excludes zero at only {{e5_n_excl}} of {{e5_n_horizons}}
horizons. It returns **{{e5_verdict}}**: at n_independent = {{e5_nind}} 400-step trajectories it was under-powered, which we measured after the fact (Appendix N). So the ranking finding is established on the released checkpoint and supported but not established on a model we trained.

**We ran the baseline test expecting it to go the other way**: the expectation we held about the
counter-baseline was that it would match disagreement. It was not committed to git before the data
existed, so by this paper's own standard (§3.4) it is not a pre-registration (Appendix N). It did not go that way against the counter. It went
that way against something else.

**One adversary is one, so we added two more, and the ranking claim survives only one of them.**
Under a rule committed before either was computed (rule M-51, corrected by rule M-52), we added two
baselines needing no ensemble and no second model: `step-size`, the magnitude of the model's own
predicted state change $\lVert \mu_t - \mu_{t-1} \rVert$, and `entry-res`, its one-step error just
before the forecast window opens (Appendix N gives what each costs).

| baseline | r(baseline, error) | margin | partial r(disagreement given baseline) | beaten? |
|---|---|---|---|---|
| forecast step index *(the existing adversary)* | {{e7_index_r}} | {{e7_index_margin}} | {{e7_index_partial}} | — |
| `step-size` — $\lVert \mu_t - \mu_{t-1} \rVert$ | **{{e7_step_r}}** | {{e7_step_margin}} | {{e7_step_partial}} | **{{e7_step_beaten}}** |
| `entry-res` — one-step error before the window | {{e7_entry_r}} | {{e7_entry_margin}} | {{e7_entry_partial}} | {{e7_entry_beaten}} |

*r(disagreement, error) = {{e7_r_dis}} on the released checkpoint over all ten episodes, n_independent = {{e7_nind}} 400-step trajectories.
Minimum detectable effect, estimated before either baseline existed: {{e7_mde_margin}} on a margin,
{{e7_mde_partial}} on a partial.*

**The verdict is {{e7_verdict}}, and the reason is the row a reader should look at twice.**
Disagreement beats {{e7_n_beaten}} of the {{e7_n_new}} free baselines added here. The
magnitude of the model's own predicted state change ranks realised error at {{e7_step_r}}, against
{{e7_r_dis}} for the five-member ensemble disagreement the method is built on. The margin between
them, {{e7_step_margin}}, is **below** the {{e7_mde_margin}} this sample size can resolve, so at
n_independent = {{e7_nind}} 400-step trajectories we cannot say the ensemble ranks better than a
subtraction. If the observed margin is the true one, settling it needs {{q2_n_req}} of them, an estimate under an assumed effect (§11, supplementary S2).

**On shorter units, at h = {{v2_deploy_h}}, the margin resolves.** The {{e7_nind}} whole trajectories cannot settle it at h = {{v2_diag_h}}, so a rule committed before its reading (rule X6, Appendix X) put the same comparison to {{x6_n_units}} non-overlapping units of {{x6_unit_len}} rows, the model's history plus h = {{v2_deploy_h}} forecast steps, cut inside the same ten episodes, on the same checkpoint. At h = {{v2_deploy_h}} the margin is {{x6_margin}} {{x6_ci}}: the interval excludes zero, the rule's criterion, so it returns **{{x6_reading}}**. Disagreement correlates {{x6_r_dis}} with error there against step size's {{x6_r_step}}, and keeps {{x6_partial}} {{x6_partial_ci}} with step size partialled out (Appendix X). The units are this checkpoint's training data, units from one episode are not independent of each other, and the interval resamples units, not episodes, so the margin at h = {{v2_deploy_h}} is resolved on this checkpoint's training episodes and no further; the margin at h = {{v2_diag_h}} is not re-tested.

**Disagreement does still carry information the subtraction does not.** With `step-size`
partialled out it retains {{e7_step_partial}}, far above the {{e7_mde_partial}} MDE for that test,
and holding the forecast step exactly fixed it keeps {{e7_ws_dis}} against `step-size`'s
{{e7_step_ws}}. It is not re-encoding predicted step size. What is not established is that it adds
enough to be worth five models. The rule fixed this reading in advance: the partial is the
load-bearing test and the margin is corroboration, so a baseline passing the partial while failing
the margin does not refute the ranking claim. **It does refute a framing.** "Disagreement ranks
error well" is supported. "You need the ensemble to rank error" is not.

**On this axis the follow-up's claim survives adversarial testing against a real baseline**, and
that is the strongest form of support this paper offers any claim of either original work — now with the qualification that a free baseline comes closer to it than the counter did.

---

## S26 The earlier section 6.7

*Was the paper's section 6.7 before the rewrite for the review of 19 October; moved here whole with the rest of that section (S20 to S27). Section numbers in this passage are the earlier paper's.*

**One constant scalar does not fix it; a per-horizon one lands within the band, though no single cell is resolvable at this arena (was §6.7)**

**Recalibrating a dynamics model's uncertainty inside model-based RL is not new** (§2). What is
new here is the conditioning variable, the *forecast horizon*, and one negative result: a single
global multiplier **fails** where a per-horizon one shows no sign of failing. An open-loop
rollout's error accumulates with depth while its predicted σ does not (§6.5), so a horizon-blind
recalibration cannot follow the thing it is trying to correct, and this section measures that.

If σ had the right shape and the wrong scale, a single multiplier would repair it, and the
finding would be a units problem with a one-line remedy. We tested that. A scalar was fitted on
**one** held-out episode and evaluated on the **other**, in both directions, so it is never
fitted on its own test set.

**Two senses of "unseen", kept apart from here on.** A cell is *unseen by the multiplier* when the
multiplier scoring it was fitted on the other episode, and *unseen by the model* when the model
never trained on that episode. The two held-out episodes are unseen by our arms' models, which
trained on the other {{n_train_eps}}, but not by the released checkpoint, which trained on all ten
(§3). **Every released-checkpoint cell in this section is therefore unseen by the multiplier
only.**

Fitting at one step works at one step and nowhere else. On the epistemic term a constant scalar
brings h = 1 coverage to {{d2_epi_cov1_lo}}–{{d2_epi_cov1_hi}}% against the {{d2_target}}% target and
leaves h = 368 at {{d2_epi_cov368_lo}}–{{d2_epi_cov368_hi}}%, and fitted over the whole rollout it
over-covers at one step while still falling short at the far end (Appendix T). A constant multiplier
cannot track an error that grows while σ does not (§6.5), so for a *constant* scale "right shape,
wrong scale" does not survive.

**On the released checkpoint a per-horizon scalar lands near target, and this is the one concrete remedy in this paper; on a model that has not seen the test episodes the evidence is mixed.** One multiplier per horizon is fitted on one held-out episode and evaluated on the other, in both
directions, so no multiplier is ever scored on the episode that produced it: each direction fits on
n_independent = {{d3_nind_fit}} of the two episodes' {{d3_nind_tot}} non-overlapping 400-step
trajectories and is scored on the other {{d3_nind_fit}}. On the released checkpoint every point
estimate lands within {{d3_tol}} points of the {{d3_target}}% target for both quantities,
**{{d3_epi_ok}} / {{d3_epi_cells}}** epistemic and **{{d3_ale_ok}} / {{d3_ale_cells}}** aleatoric cells,
against {{d3_epi_const_ok}} of {{d3_epi_cells}} for the constant scalar. **That absolute test is
UNPOWERED here:** the {{d3_tol}}-point band is resolvable at {{d3x_tol_res}} of {{d3x_tol_pairs}}
quantity-by-horizon pairs, so a cell inside the band is compatible with a true coverage well outside
it. **On Arm A at ensemble size {{d3x_ens}}, where the episodes are unseen by the model as well, its
own multipliers manage {{d3x_own_epi_ok}} of {{d3x_own_epi_cells}} epistemic and {{d3x_own_ale_ok}}
of {{d3x_own_ale_cells}} aleatoric cells**. So the recipe does not carry over intact to a model that
has not seen the test episodes (Appendix T gives the table and every deviation).

**Three cautions.** The per-horizon scalar has one free parameter per horizon against the constant one's one, so it *must* fit better in sample; only cells unseen by the multiplier are evidence, and those are the cells reported. **The count is thinner than it looks:** the {{d3_epi_cells}} cells are {{d3_nhoriz}} horizons × two fold directions on the same {{d3_nind_tot}} trajectories, each multiplier fitted on n_independent = {{d3_nind_fit}} and scored on the other {{d3_nind_fit}}. They are not {{d3_epi_cells}} independent successes and no P-value attaches to the count, which is reported so a reader can see how thin the evidence is; later sections refer back to this as the §6.7 caution, which the nine-episode fit below narrows for the released checkpoint. And the correction is a calibration patch, not a fix: it leaves σ carrying no more information than before and rescales it by how far ahead you are looking. On the released checkpoint it nevertheless brings every estimate unseen by the multiplier near what the interval claims, which is what a downstream user needs, and it costs one lookup table.

**Fitted on nine episodes and scored on the tenth (rule X7).** A rule committed before its reading (Appendix Y) repeats the design over all ten episodes: for each, the per-horizon multiplier is fitted on the other nine episodes' trajectories with the same fitting function and scored on its own. Each of the {{x7_n_traj}} trajectories is thus scored once, by a multiplier not fitted on it, and each horizon's coverage carries a 95% interval. On the epistemic term every one of those intervals lies inside the {{d3_tol}}-point band, all of them between {{x7_ci_min}}% and {{x7_ci_max}}%: **{{x7_summary}}**. Appendix Y gives the aleatoric term and the constant multiplier alongside. Those trajectories are unseen by the multiplier, not by the model, which trained on all ten episodes, so for the released checkpoint each horizon's coverage is now resolved within the band, though the six horizons share those trajectories and are not independent tests; the Arm A result stands as it is.

**The multipliers are a property of the model, not of the horizon.** Fitted on Arm A and scored on
the released checkpoint, and the reverse, on the same {{d3x_nind}} held-out trajectories, rule M-69 returns **{{d3x_verdict}}** on the paired change in coverage the arena can resolve: {{d3x_n_out}} of {{d3x_ncells}} governing cells, which are not independent tests, have an interval wholly outside the ±{{d3x_band}}-point band, and Arm A's multipliers are {{d3x_ratio_lo}}× to {{d3x_ratio_hi}}× the
released checkpoint's at the same horizon (Appendix T).

So the accurate form of this section is: **a constant scalar does not repair the interval; on the released checkpoint a per-horizon one brings every estimate unseen by the multiplier within the band, though no single cell is resolvable at this arena, and does so across episodes but not across models. On episodes unseen by the model as well, Arm A's own multipliers manage {{d3x_own_epi_ok}} of {{d3x_own_epi_cells}} epistemic cells, so there the evidence is mixed.** Fitted on nine episodes and scored on the tenth, the released checkpoint's epistemic coverage over all {{x7_n_traj}} trajectories is within the band at every horizon.

---

## S27 The earlier section 6.8

*Was the paper's section 6.8 before the rewrite for the review of 19 October; moved here whole with the rest of that section (S20 to S27). Section numbers in this passage are the earlier paper's.*

**Testing the mechanism: an ensemble that shares nothing, alone and with the corrected objective (was §6.8)**

§6.4 establishes the topology as a fact and the mechanism as a hypothesis. Two rules committed to git
before any of their artifacts existed test it, each with a minimum detectable effect estimated in
advance (Appendix E). The first scores {{r2_n_indep}} independently initialised full models, Arm A at
ensemble size 1 trained at {{r2_n_indep}} seeds, together as an ensemble at evaluation time. Each member keeps its own recurrent hidden state and the ensemble mean is fed back to all of them, so the
rollout differs from the shared-trunk one only in what is under test. The second repeats it with every member trained under `gaussian_nll`, so the two fixes are measured on the same models. Both are scored
on the held-out pair, n_independent = {{r2_nind}} 400-step trajectories, every model at {{iters_main}}
training iterations, against each of the shared-trunk seeds separately (Appendices O and P give the tables).

**Rule M-44 returns {{m44_verdict}}.** All {{m44_n_conditions_met}} of its {{m44_n_conditions}}
conditions hold against every one of the {{r2_n_shared}} shared-trunk seeds: at h = {{v2_deploy_h}}
the overconfidence factor improves **{{m44_ratio_gain}}×** against a minimum detectable effect of
{{m44_mde_ratio}}×, coverage rises a mean of {{m44_cov_gain}} points against {{m44_mde_cov}}, and every
paired interval excludes zero. σ itself grows {{r2_sigma_x_h100}}× there, **{{r2_from_sigma_h100}}%**
of the improvement, so the trunk-sharing mechanism is the larger part of the effect where the method operates. At h = {{v2_diag_h}}, {{r2_from_acc_h368}}% is the ensemble simply predicting better
(Appendix O).

**Rule M-68 returns {{m68_verdict}}**, branch {{m68_branch}} of the four it names: all
{{m68_n_conditions_met}} of its {{m68_n_conditions}} conditions hold, a **{{m68_ratio_gain}}×**
improvement against a minimum detectable effect of {{m68_mde_ratio}}×. That is essentially what
independence gave alone. Against the independent arm, which differs in the loss and nothing else,
switching to `gaussian_nll` multiplies the overconfidence factor by {{m68_vs_mse_ratio}}×
{{m68_vs_mse_ratio_ci}}, slightly the wrong way and below what the design can resolve (Appendix P).
**The two fixes do not add**: the objective's separate contribution is at most small, which the
design can bound but not establish as zero. Once stated that is no surprise: the objective governs
the aleatoric head, and the epistemic term is a spread across members the loss never sees.

**What the arms bound, and what they do not repair.** Independently seeded runs differ in data
ordering as well as initialisation, and the independent members carry {{v1_cap_ratio}}× the
shared-trunk arms' state-pathway parameters, so these comparisons bound the architectural effect rather than isolating it. At matched capacity the improvement falls to {{m49_ratio_gain}}× against a minimum detectable effect
of {{m49_mde_ratio}}×, so that rule returns **{{m49_verdict}}** (rule M-49, supplementary S2). Neither arm is an interval: at h = {{v2_deploy_h}} the independent ensemble is
{{r2_indep_ratio_h100}}× overconfident with {{r2_indep_cov1_h100}}% coverage and the combined arm
{{m68_indep_ratio_h100}}× with {{m68_indep_cov1_h100}}%, where a calibrated Gaussian gives
{{v3_cov_nominal1}}%. §6.7's per-horizon multiplier remains the only correction in this paper whose
estimates all land within the band, though only on the released checkpoint and with no single cell
resolvable at this arena.

---

---

---

## S28 The earlier defects section

*Was the paper's section seven (defects in the released pipeline) before the rewrite for the review of 19 October; moved here whole. Section numbers in this passage are the earlier paper's.*

**Defects in the released pipeline (was §7)**

Appendix H lists the ledger's other confirmed contributions that the body does not state, among
them defects in the released data pipeline and departures of the released code from the paper's
description.

**7.1 Ten unmarked episode boundaries.** §3. The window builder reads a termination column that is
identically zero, so it marks all {{win_naive}} windows valid.

**7.2 Training and evaluation disagree on action alignment, and evaluation is the broken one.**
Row *t* holds the action that *produced* state *t*. The data say so directly: at every reset row
all twelve actions are exactly zero (§3), and a policy network with biases cannot emit exact zeros,
so those zeros mark the absence of a producing action — the reset produced that state, not a policy step. They are what Isaac Lab, in which the data were recorded, writes at a reset: `ActionManager.reset()` sets its stored actions to zero (`action_manager.py:350-365` in Isaac Lab). The training path pairs states and actions index-for-index, which is causally correct; the
evaluation path feeds the action from *t−1* to predict state *t*, stale by one step.

What the stale pairing costs depends on the horizon. All ten episodes are this checkpoint's training data, so the held-out pair is not more honest here, only smaller, and the larger arena leads. Over all ten episodes' {{ad20_nind}} independent trajectories the stale action raises the released checkpoint's relative-L1 error by {{adh20_rel_h1}}% {{adh20_rel_ci_h1}} at h = 1, {{adh20_rel_h8}}% {{adh20_rel_ci_h8}} at h = 8 and {{adh20_rel_h32}}% {{adh20_rel_ci_h32}} at h = 32. From h = {{v2_deploy_h}} the change is not resolved: {{adh20_rel_h100}}% {{adh20_rel_ci_h100}} there and {{ad20_rel}}% {{ad20_rel_ci}} at h = {{v2_diag_h}}, where single trajectories run from {{ad20_traj_lo}}% to {{ad20_traj_hi}}%. In nRMSE the rise is resolved at h = 8 and 32 ({{adh20_nrmse_h8}}% {{adh20_nrmse_ci_h8}} and {{adh20_nrmse_h32}}% {{adh20_nrmse_ci_h32}}) but not at h = 1 ({{adh20_nrmse_h1}}% {{adh20_nrmse_ci_h1}}), and from h = {{v2_deploy_h}} it is not resolved either ({{adh20_nrmse_h100}}% {{adh20_nrmse_ci_h100}} there, {{ad20_nrmse}}% {{ad20_nrmse_ci}} at h = {{v2_diag_h}}). Each is a 95% interval from a cluster bootstrap over whole trajectories, both pairings inside each draw (`results/alignment_by_horizon.json`, `results/alignment_defect_ci.json`).

On the held-out pair's {{ad_nind}} independent trajectories the stale action raises the error at every horizon reported: by {{adh_rel_h1}}% {{adh_rel_ci_h1}} at h = 1 and by {{adh_rel_h100}}% {{adh_rel_ci_h100}} at h = {{v2_deploy_h}}, where all ten episodes resolve no change. At h = {{v2_diag_h}} it raises it by {{ad_rel}}% {{ad_rel_ci}} on relative-L1 and {{ad_nrmse}}% {{ad_nrmse_ci}} in nRMSE (Appendix V gives the per-trajectory values). Shifting the evaluation loop's two action slices by one step (`model_training.py:129` and `:132`) aligns it with training; our harness does this with `action_offset = 1` (`src/score_reference.py:180-190`). 

For models trained under the causal pairing, the stale one also raises error, and how much depends on the arena (three-seed means, computed post hoc; Appendix V gives every model at every horizon, each with its interval). A percentage change depends on how accurate the model already is as much as on how much the action matters. Measured as the shift in the forecast itself on their own training data, our {{iters_long}}-iteration Arm A and the released checkpoint move about equally at h = 8, and at h = {{v2_deploy_h}} the released checkpoint's forecast moves more (Appendix V).

Our models do use the action. Given another trajectory's actions, their error at h = 8 on their own training episodes' {{x2_n_ins}} trajectories rises by {{x2_E_swap_10k}}% {{x2_ci_swap_10k}} at {{iters_long}} iterations, and at {{iters_main}} iterations by {{x2_E_swap_2500}}% {{x2_ci_swap_2500}}, so rule X2, committed before its readings existed, returns **{{x2_reading}}** at both checkpoints (Appendix V). That shows the forecasts depend on the action, not that they predict a different action's consequences correctly: every action in the data comes from one policy. 

Rule X8 re-scores four of our rules with the released evaluation's timing, on the held-out pair's {{mn_nind}} trajectories, through each rule's own evaluator (the configuration and baseline rules at {{iters_main}} iterations, the A/B comparison at {{iters_long}}), and all four keep their verdicts, **{{x8_reading}}**, though {{x8_n_changed}} of their alongside readings change (Appendix Z); this concerns our models, not the original's printed numbers.

**7.3 No held-out evaluation.** Evaluation trajectories are drawn from training data. For the
released checkpoint, trained on the entire file, no held-out measurement is possible at all, and neither pinned repository can generate the data that would make one possible (§3).

**7.4 What the spliced windows cost: nothing measurable in rollout.** A contaminated arm trained with
{{arm_splices}} spliced windows added, at {{arm_contam_pct}}% contamination (below the pipeline's
{{contam_pct}}%, by design, so that no held-out row leaks), raises training loss by
{{contam_cost_pct}}% where a duplication control adding the same number of exact copies raises it by
{{dup_cost_pct}}%. In rollout, over {{tw_cells}} cells ({{tw_design}}), it is hurt in {{tw_cc_cluster_hurt}} and helped
in {{tw_cc_cluster_helped}} (Figure 8a), the signature of regularisation. At this rate the splices do
not harm rollout; the unmarked boundaries remain a real defect on leakage grounds (Appendix Q).

---

**7.5 The released artifacts do not reproduce the released checkpoint's variance state.** Read as a
clock, §5.5's collapse rate puts the checkpoint's variance state out of reach of a constant-rate run
from the released initialisation at the configured learning rate, at every iteration count the release, the paper and the checkpoint
tag state. The first author's account, that the release is several revisions removed from the setup
that trained it, supplies a mechanism, a warm start or a different initialisation, so this is a
documentation gap between a release and a run rather than an inconsistency (Appendix F and the
supplementary `docs/APPENDIX_G_VARIANCE_ARITHMETIC.md`).

---

## S29 The earlier lessons section

*Was the paper's section nine (actionable lessons) before the rewrite for the review of 19 October; moved here whole. Section numbers in this passage are the earlier paper's.*

**Actionable lessons (was §9)**

{{n_lessons_word}} things a practitioner can apply without reading the rest of this paper.

**Use ensemble disagreement as a ranking signal, but price it against the free alternatives first. Do not read it as a distance. And expect it to degrade with horizon.** On the released checkpoint's own training episodes, at one forecast step it ranks whole rollouts almost perfectly, {{d2_epi_h1}} {{d2_epi_ci_h1}} across the {{a2_h1_npoints}} trajectories, a ranking of *rollouts* rather than of moments within one, because at h=1 there is only one moment. Over the full rollout it falls to {{d4_r}} {{d4_ci}}: excellent where you can check it cheaply and merely good where you most need it. It beats the forecast step index at every horizon we tested, on a paired test that excludes zero at {{d2p_n_separating}} of the {{d2p_n_horizons}} horizons where the index is defined, and retains {{d2b_par_all}} once that index is partialled out (§5.6). **On whole trajectories, what it does not clearly beat is the model's own predicted step size**, which costs nothing and needs no ensemble: over the {{e7_nind}} 400-step trajectories that ranks error at {{e7_step_r}} against disagreement's {{e7_r_dis}}, a margin of {{e7_step_margin}}, below the {{e7_mde_margin}} that sample can resolve. On {{x6_n_units}} shorter units of the same episodes a later rule resolves the margin at h = {{v2_deploy_h}}, {{x6_margin}} {{x6_ci}} (rule X6, §5.6), on the checkpoint's training data only; the margin at h = {{v2_diag_h}} is not re-tested. Disagreement carries information the subtraction does not, retaining {{e7_step_partial}} once step size is partialled out, and with both the forecast depth and the rollout held constant it still correlates {{a2_rdd}} {{a2_rdd_ci}} with error (§5.6); but a practitioner about to pay for five members should price the subtraction first. And it is too small to be an interval by a wide margin: at h = {{v2_deploy_h}}, the horizon the method rolls out over, {{d1n_epi_ratio_h100}}× [{{d1n_epi_ratio_ci_h100}}] on the released checkpoint over all ten episodes, and on the held-out pair {{e5_ratio_h100}}× [{{e5_ratio_ci_h100}}] on the ensemble-5 arms we trained, against the released checkpoint's {{b2_epi_ratio_h100}}× there. A risk gate or safety margin that reads σ as a distance is not supported at any horizon, on either.

**If you need the interval, rescale per horizon, not globally, and refit on your own model.** One multiplier per forecast horizon, fitted on one episode and scored on another, brings every released-checkpoint coverage estimate within {{d3_tol}} points of nominal, though this arena cannot resolve any single cell to that band. Fitted on nine episodes and scored on the tenth, the epistemic coverage over all {{x7_n_traj}} trajectories lies within it at every horizon (rule X7, §5.7). A single global multiplier manages {{d3_epi_const_ok}} of the {{d3_epi_cells}} epistemic ones (§5.7). That checkpoint trained on both episodes; on Arm A, whose model never saw them, its own multipliers manage {{d3x_own_epi_ok}} of {{d3x_own_epi_cells}} epistemic cells. The cells are not independent trials (the §5.7 caution), so read the sweep as consistency and the per-cell deviations as the evidence. The fitted epistemic multipliers span {{d3_epi_cspread}}× across horizons, which is precisely why one number cannot serve.

**Do not convert per-dimension sign counts into P-values.** State dimensions in a robot are physically coupled and share a forecast-depth trend, so an independent-trials null is badly wrong, in our tables by up to {{perm_worst_factor}}× (§5.6, Appendix K). Permute whole trajectories instead. An earlier draft of this paper used the binomial version, and it made our weakest evidence look like our strongest.

**Count independent trajectories, not trajectories.** Two 400-step windows that overlap at all
are one piece of evidence, not two. The held-out arena here contains {{nind_oos_400}} independent
400-step trajectories however many windows are drawn from it, and that number bounds every
long-horizon magnitude (§3), though §4.1's direction is re-tested on all ten episodes, each held out once on fixed folds (rule X3: **{{x3_reading}}**, {{x3_n}} trajectories at {{iters_main}} iterations, not {{iters_long}}). Reporting an interval beside a trajectory count rather than an
independent-trajectory count overstates precision. Resampling pooled seed × trajectory values instead of trajectories narrows
intervals by a further {{bu_mean_ratio}}× (§3.4).

**Anchor a decision rule to the horizon the claim is about.** Our first pre-registered rule was
anchored at h = 8, the training forecast horizon, and returned **{{m16_verdict}}**; the claim was
about deployment horizons. The rule was correct in form and pointed at the wrong regime, a failure
mode pre-registration does not protect against on its own.

**Check that the implemented loss is the described loss before reproducing any number from it.**
The paper describes two loss terms; the implementation has {{diff_terms}}. The predicted variance has an optimum at zero under the implemented one, which is why the released checkpoint's σ is {{d1n_alea_ratio_h100}}× smaller than its own error at h = {{v2_deploy_h}}, and {{d1n_alea_ratio_h368}}× at h = {{v2_diag_h}}. Reading the loss took an afternoon and explained a
result that would otherwise have looked like a training bug.

---

## S30 The earlier limitations section

*Was the paper's section eleven (limitations) before the rewrite for the review of 19 October; moved here whole. Section numbers in this passage are the earlier paper's.*

**Limitations (was §11)**

Limits that belong to one result are stated beside it: the budget and our reading of Table S7
(§4.2, §4.3), the mechanism of §5.3 as a hypothesis, the per-dimension tests' power (§5.6, Appendix K), the
ensemble-5 replication (§5.6), the recalibration's two episodes (§5.7), which its nine-episode fit widens to all ten for the released checkpoint,
and what the independent ensemble bounds (§5.3). supplementary S2 gives each of those, and every limitation below, in full.

**What this study cannot address.** One robot, one gait (a trot) and one flat terrain, with every
command drawn from one bounded box, so "generalisation" here means across velocity commands only. No
policy is trained: no policy-learning result of either paper is reproduced or tested, the
sample-efficiency comparison included, and nothing here uses a GPU. Our arms use {{c2_pct}}% of the
reference's world-model data (§3.2). And the released checkpoint trained on all ten episodes, so it
has no held-out arena, and neither pinned repository can generate the data that would give it one
(supplementary S1). None of this can be lifted on CPU, and nothing in this paper claims otherwise.

**Effective sample size bounds the long-horizon magnitudes.** The headline magnitudes rest on the held-out pair, {{m23_nind}} independent 400-step trajectories (the n = {{m23_nind}} caveat of §3); the direction is re-tested on all ten episodes, each out of sample once on fixed folds (rule X3: **{{x3_reading}}**, {{x3_n}} trajectories at {{iters_main}} iterations, not {{iters_long}}; §4.1). A larger dataset cannot be generated here (supplementary S1), so the released checkpoint's lack of a held-out arena is a constraint, not a choice.

**On whole trajectories, the ranking claim is not established as needing an ensemble.** The model's
own predicted step size ranks error nearly as well, by a margin those {{e7_nind}} trajectories cannot
resolve at h = {{v2_diag_h}}; if the observed margin is the true one, settling it needs {{q2_n_req}}
independent 400-step trajectories, a required-sample-size estimate under an assumed effect (supplementary S2).
On {{x6_n_units}} shorter units cut inside the same episodes, which are the checkpoint's training data,
a rule committed before its reading finds disagreement ahead at h = {{v2_deploy_h}}, {{x6_margin}}
{{x6_ci}} (rule X6: **{{x6_reading}}**; §5.6, Appendix X); the margin at h = {{v2_diag_h}} is not re-tested.

**We did not measure what the miscalibration costs.** The penalty the follow-up applies is
{{d1n_epi_ratio_h100}}× overconfident at h = {{v2_deploy_h}}, the horizon its own imagination
rollouts run to, but its only use is to shape policy learning, and a test of that cost needing no policy, rule X5, could not be run, because the released data do not record the velocity command its reward terms score against (Appendix W). **The finding bounds what the quantity reports, not what it
costs**, and the ratio is not a measure of harm. Other sections refer back to this as the policy
caveat of §11. A proxy that needs no policy, the ordering of the penalty accumulated along whole
rollouts before and after the per-horizon correction, finds none of the {{q3_n_pairs}} pairs among the held-out pair's {{q3_nind}} trajectories reordered (in-sample for the checkpoint; rule M-70: **{{q3_verdict}}**). That proxy orders the penalty alone, though, not the penalised return, its null is partly structural, and its interval is degenerate (supplementary S2).

**No family-wide correction is applied across our own pre-registered rules.** There are
{{appG_n_rules}} of them (Appendix E), each reported, once its data exist, against the thresholds it was committed with (one is withdrawn as a
pre-registration because it reached git after its data, §3.4); a reader who prefers a corrected family threshold can apply it
from that count.

**Other descendants of the PETS parameterisation.** We did not test whether the σ = 0 optimum affects
them: the hypothesis is well-founded only for one that makes the same substitution and leaves nothing
pushing its floor back up, and is untested for any (§2, Appendix I).

---

## S31 The earlier conclusion section

*Was the paper's section twelve (conclusion) before the rewrite for the review of 19 October; moved here whole. Section numbers in this passage are the earlier paper's.*

**Conclusion (was §12)**

The Robotic World Model's central training claim reproduces at long horizons, and the margin is
large there, though teacher forcing leads at one step on the short windows built for it. RWM is
ahead at h = {{v2_diag_h}} of the baselines we built to our reading of it and trained with its settings, though there none of them beats predicting no change. Matched to RWM's parameter count, size being one axis, the transformer cannot be told apart from it (rule X4: {{x4_reading}}). On accuracy alone, {{mn_n_better_word}} other history and forecast lengths beat its chosen ones at our budget, no reading the rule reports putting the chosen ones ahead of any of them, in a ranking that changes when the chosen setting trains longer; it chose them as a trade-off with training time (§4.2, §4.3). Neither
uncertainty output of the follow-up that adds them reports what a reader would take it to report.
At h = {{v2_deploy_h}}, the horizon the method's own imagination rollouts run to, the aleatoric σ is {{d1n_alea_ratio_h100}}× smaller than its own error, because the objective's optimum is σ = 0 and the term that should prevent this cancels out of the gradient. The epistemic term the method actually penalises with is better by a factor of {{d1n_epi_over_alea_h100}} and still {{d1n_epi_ratio_h100}}× [{{d1n_epi_ratio_ci_h100}}] overconfident, both figures at h = {{v2_deploy_h}} on the {{d1n_nind}} trajectories of the checkpoint's own training episodes.

The ranking use the follow-up claims survives a real test. On the released checkpoint, ensemble disagreement beats the forecast step index at every horizon and, with both the rollout and the depth held constant, still correlates
{{a2_rdd}} {{a2_rdd_ci}} with realised error (§5.6). A free subtraction, though, the model's own
predicted step size, ranks error nearly as well, {{e7_step_r3}} against disagreement's {{d4_r}}, by a margin {{e7_nind}} whole trajectories cannot resolve at h = {{v2_diag_h}}
({{e7_verdict}}: {{e7_verdict_gloss}}); on {{x6_n_units}} shorter units of the same episodes, at h = {{v2_deploy_h}}, disagreement is ahead (rule X6, {{x6_margin}} {{x6_ci}}). The scale may be repairable per
horizon on the released checkpoint, where, fitted on nine episodes and scored on the tenth, the epistemic coverage over all {{x7_n_traj}} trajectories is within the band at every horizon (rule X7: **{{x7_summary}}**), but on a model that never saw the test episodes the evidence is
mixed (§5.7). Per dimension, no ordering reaches significance after multiplicity correction once the
coupling between dimensions is respected (§5.6). As the scalar the method applies, ensemble disagreement gets the
order right and the size wrong: it should not be read as a scale, and a ranking use deserves its own
validation on the deployment distribution (supplementary S3).

**What should travel from this paper, and what should not.** *Properties of the objective and of how
its bounds are built*, such as §5.5's σ = 0 optimum, are the ones to expect elsewhere, and only where both are present together, a hypothesis §2 states and leaves untested outside this codebase. *Properties of this released artifact*, its one-step misalignment, its
shared trunk and its specific overconfidence factors, should be checked rather than assumed in any
other. *Properties of this dataset and its arenas* are limits on what could be resolved, not
findings in either direction (supplementary S3 gives all three, and why §4.2's verdict should not travel either).

---

## S32 Appendix passages that restated the main text

*Passages of the earlier appendices that restated a result the paper states in its sections, or explained why an appendix existed; moved here whole when the appendices were rebuilt for the review of 19 October. Section numbers in these passages are the earlier paper's.*

**Why this appendix exists rather than a sentence.** The choice between the two once inverted a
published-model comparison in this project's own history — a result that favoured us under one
aggregation and did not under the other. The claim was withdrawn on our own evidence and is kept
in the record (`FINDINGS_LEDGER.md`). Form 2 figures appear nowhere in the body; they are retained
in `results/step4_0a_results.json` for continuity with figures this project published before the
inversion was found. This appendix gives the two definitions and the inversion rather than those figures, so continuity rests on that committed file and not on a deleted number.

**§5.5's term-by-term summary.** **The derivation above covers two terms, and the objective has {{e4_n_terms}}.** Each term,
back-propagated alone on one real batch, confirms it: {{e4_n_live}} are live under the released
configuration, exactly {{e4_n_touch}} reach σ ({{e4_touching}}), and the other {{e4_n_inert}} give a
gradient of exactly zero (`results/e4_sigma_gradients.json`, Appendix J).

**§5.5's run-count summary.** We predicted the collapse from this algebra before training, then observed it: across all {{n_runs}} runs at the released width outside §4.2's sweep the log-σ range moves linearly in iteration count at a nearly identical rate within each objective, falling under sampled MSE and rising under the corrected one (Figure 7a). Appendix J lists the runs, the capacity-matched arm excluded from
every rate, and the {{e2_fitted_runs}} the rate is fitted on.
