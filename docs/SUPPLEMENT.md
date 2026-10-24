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

Appendix D's first table marks 6 claims tested and the rest not. "Not tested" is an apology
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
| Sample efficiency, 6,000,000 against ~250M transitions (§IV-E) | Isaac Lab, an RTX-class GPU, the MBPO-PPO loop, and a PPO baseline run to convergence for the comparison | the reference reports 6,000,000 pretraining transitions and 50 min of RWM training on their hardware; the PPO baseline's 250M is the dominant cost |
| MBPO-PPO beats SHAC and Dreamer (§IV-E) | the above, plus SHAC and Dreamer implementations at matched budgets | three policy-learning stacks, each tuned enough that the comparison is fair — the largest engineering item here |
| Zero-shot hardware transfer (§IV-E) | all of the above, plus an ANYmal, a safe test area, and the sim-to-real stack | not estimable in compute; the binding constraint is hardware access, not GPU hours |
| Generality across quadruped, humanoid, manipulation (§IV-D) | recorded state-action data from a humanoid and a manipulator, which means Isaac Lab and a policy in each environment to generate it — the released CSV is one robot on one terrain | one data-generation run per morphology, plus a world-model training campaign each on the scale of ours, 33 runs in 49.8 h; the model training is the cheap half and the data is not |
| Offline MBRL on real robots (2504.16680v1) | a real robot, a logged dataset from it, and the offline MBRL loop | not estimable in compute; hardware access again, and a claim the follow-up itself states as prospective |
| Whether the penalty improves the learned policy (2504.16680v1 §5) | Isaac Lab, the MOPO-PPO loop, and at minimum an ablation with the penalty weight at zero | one policy-learning stack; the cheapest of the rows that need a simulator, and the one that would bound §11's open question about what the miscalibration costs |


**Two claims this table once priced as within reach of this setup have since been run**: the
configuration claim (§5.2) and the architecture claim (§5.3), 42 runs and
28.3 h of CPU training between them (Appendix B). The six that remain all
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
4 independent 400-step trajectories (the n = 4 caveat of §3). That is the
binding constraint on §5's magnitudes, and no amount of trajectory oversampling changes it. The direction is re-tested on all ten episodes, each held out once: rule X3 trains both arms on four more fixed folds beside §5's own and returns **REPLICATES ACROSS FOLDS** over 20 trajectories, at 2,500 iterations rather than 10,000 (Appendix L). Nor can a larger
dataset be generated here: the data generator is in neither pinned repository, and the one the lite
release points to runs in a simulator this work did not have (supplementary S1). The released checkpoint's lack
of a held-out arena is therefore a constraint, not a choice.

**Ensemble size: supported, not established.** Our main arms run at ensemble size 1, where the epistemic term is identically zero, so the epistemic measurements were first made on the released checkpoint alone. The 3 ensemble-5 Arm A arms (§6.6) reproduce the *direction* of §6.6's finding in 12 of 12 seed-horizon cells and the *calibration* failure, 10.5× at h = 100, but the pre-registered rule governing the replication returns **DOES NOT GENERALISE**: its second condition needs the paired difference to exclude zero at a majority of horizons, and it does at 1 of 4. Our arms have a held-out arena of only 4 independent trajectories, and the rule was written without checking what it could detect there. **So §6.6's finding is established on the released checkpoint and supported but not established on a model we trained.**

**One dataset, one gait, one terrain.** All commands are drawn from one bounded box and the gait
is a single trot throughout. "Generalisation" here means across velocity commands, not across
gaits or terrain.

**The per-horizon recalibration is tested on two episodes, or on episodes the model trained on.** §6.7's remedy puts every released-checkpoint estimate within the band across the two held-out episodes in both directions, though at this n no single cell is resolvable, and those cells are unseen by the multiplier only, because the checkpoint trained on both episodes. Rule X7 widens the released checkpoint's test to all ten episodes, each scored by a multiplier fitted on the other nine, and returns **WITHIN BAND AT 6 OF 6 HORIZONS** for the epistemic term (Appendix Y); those episodes, too, are unseen by the multiplier only. On Arm A, whose model never saw them, the same recipe manages 17 of 36 epistemic and 10 of 36 aleatoric cells, and two episodes is not a demonstration that the multipliers transfer to a new robot, gait or terrain. Treat the lookup table as a recipe to refit, not as constants to copy.

**Two secondary analyses rest on a single training seed**, the long-horizon trend fit and the per-dimension matched comparison, both on seed 1 alone, as their artifacts record. The headline A/B verdict rests on one seed too, seed 1, the one its rule ran on; the magnitudes
beside it are three-seed means with per-seed values (§5).

**On whole trajectories, the ranking claim is not established as needing an ensemble.** Under a rule committed before the
comparison (rule M-51, Appendix E), the model's own predicted state change, a subtraction needing no
ensemble, ranks error at +0.4697 against disagreement's +0.6053, and the margin is
smaller than this sample can resolve (§6.6). Disagreement retains +0.5430 with that
baseline partialled out, so what is open is whether its increment is worth five models. **If the observed margin is the true one, settling it needs 25 independent 400-step
trajectories, where all ten episodes provide 20**, 1.25× the present sample, by
the rule's own construction applied to the step-size margin's standard error
(`results/q2_free_baseline_power.json`). That is a required-sample-size estimate under an assumed
effect: it takes the true margin to be the observed +0.1357 and new trajectories to vary
as these do, and if the true margin is smaller the requirement rises as its inverse square, to
45 at +0.1000. The margin is the only test left to pass, since the partial
already clears its threshold, +0.5430 against 0.1131. And it is closer to
resolving than §6.6's threshold of 0.2891 suggests: the rule had to fix that threshold
before this baseline existed, from the forecast-index margin, whose standard error is
1.94× the step-size margin's. The observed margin is 91.1% of what its own
statistic resolves at this sample and 46.9% of what the rule's threshold demands, and
re-run exactly as pre-registered that protocol would need 91 trajectories. §6.6's
verdict stands on either reading, because the margin is below both. On shorter units the margin at h = 100 resolves: rule X6, committed before its reading, cut the same ten episodes into 70 non-overlapping 132-row units and returns **DISAGREEMENT BEATS STEP SIZE**, +0.2816 [+0.1978, +0.3896] at h = 100 against a minimum detectable effect of 0.1713 (Appendix X). Those units are the checkpoint's training data and share its ten episodes, and the interval resamples units, not episodes, so this settles that margin on this checkpoint's training episodes only, and does not re-test the margin at h = 368.

**We did not measure what the miscalibration costs.** The penalty the follow-up applies is miscalibrated as a scale, 33.4× overconfident at h = 100, the horizon its own imagination rollouts run to, but the method's only use of that quantity is to shape policy learning, and we did not train a policy. A miscalibrated scale that enters as a relative penalty across candidate actions may cost little or a great deal; our measurements cannot tell which. **The finding bounds what the quantity reports, not what it costs**, and the ratio is not a measure of harm. Other sections refer back to this as the policy caveat of §11.

**A proxy that needs no policy finds no reordering, and is worth only what its bound allows.**
Within one horizon the per-horizon correction multiplies the penalty by a positive constant, which
cannot change any ranking, so a rule committed before the statistic was computed (rule M-70,
Appendix E) compares instead the penalty accumulated along each whole rollout, before and after
correction. The penalty is the released checkpoint's own ensemble disagreement, on the 4
independent trajectories of the held-out pair, which are unseen by the multipliers applied to them
but not by the checkpoint (§3). Of the 6 pairs, 0 change order and the
rule returns **DOES NOT REORDER**: the correction leaves every pairwise ordering of accumulated
penalty unchanged, so whatever it changes downstream must act through the penalty's magnitude
rather than through which rollout is penalised more. The multipliers differ by 9.31×
across horizons, so the design could have produced reordering
(`results/q3_penalty_reordering.json`). Three things limit what that shows. **It is the ordering of
the penalty component alone, not of the penalised return**: this work has no reward function and no
tuned penalty weight, so the result bounds what the correction could do downstream and licenses no
statement about a policy or about the size of any downstream effect. **The null is partly
structural**, by a diagnostic computed after the verdict: the last horizon band, h = 368,
holds 240 of the 368 steps and 81.35% of the corrected penalty, and
the overall ordering is exactly that band's, so the per-horizon weights had little room to act. **And the rule's bootstrap interval corroborates nothing**: resampling trajectories creates no new
pairs, so with none reordering no resample can return anything else, and the interval is
degenerate by construction (`M-71`).

**The per-dimension ordering tests are underpowered at every sample size we can reach.** Once the coupling between state dimensions is respected (§6.5), the out-of-sample arena's 4 independent trajectories cannot reject at any effect size, and the larger arenas can and do not: over all ten episodes the smallest P in the family is 0.0037 against a threshold of 0.001667. Resolving it at h = 368 needs more episodes than the released dataset contains, not a better test. At h = 128 and below that is no longer true: a shorter unit gives 14 independent units at h = 100 where the 400-step unit gives 4 (Appendix K), and we did not rerun this permutation family there. This limits the *per-dimension* evidence only; the aggregate scalar the method applies is one test rather than forty-five coupled ones, and more strongly supported (§6.6).

**No family-wide correction is applied across our own pre-registered rules.** There are 35 of them (Appendix E), each reported, once its data exist, against the thresholds it was committed with. Pre-registration is what licenses that: each rule is a separate question committed before its data, not one search over many outcomes, and a rule that fails is reported as failing. A reader who prefers a corrected family threshold can apply it from that count.

**The independent-ensemble comparison bounds the trunk-sharing effect rather than isolating it.** §6.8's contrast trains five models at five seeds and scores them together. Independently seeded runs differ in **both** initialisation *and* data ordering, whereas the shared-trunk heads differ only in head initialisation. They also differ in **capacity**: the independent arm carries 3,570,820 state-pathway parameters against the shared-trunk arm's 1,024,132, a factor of 3.49, because each member brings its own trunk, and greater capacity can inflate σ as well as shrink error. **Capacity is controlled separately.** Rule M-49 (Appendix E), committed with its minimum detectable effect before any of its models existed, trains 5 independent members at `rnn_hidden_size` 124 against the released 256, giving 1,023,880 state-pathway parameters against the shared-trunk arm's 1,024,132, a ratio of 0.9998 where §6.8's contrast carried 3.49. It scores them on the held-out pair's 4 400-step trajectories, every model at 2,500 training iterations. **With capacity held fixed the independent ensemble is still better calibrated on every shared-trunk seed, every paired interval still excludes zero, and the coverage gain of +6.42 points still clears its own MDE.** The effect does not vanish when the confound is removed.

**It does shrink, and by more than this design can resolve.** The overconfidence improvement falls from 2.03× unmatched to **1.79× matched**, against an MDE of 2.00×, so the rule returns **UNDER-POWERED — favours the matched ensemble by less than the MDE**: 5 of its 6 conditions hold, and the ratio threshold is the one that does not. That is the third branch the rule names, and it names it because its MDE was almost exactly the size of the effect it re-tested, as rule M-49's own text said before the runs (ledger `M-49`). So trunk-sharing is **not** explained away by capacity: the effect points the same way on every pair, with every interval excluding zero. Whether capacity accounts for *any* of it this design does not answer: the point estimates fall by about 0.24, a difference no artifact here tests and far below the 2.00× this comparison can resolve, and closing it needs more independent trajectories than the dataset contains. The comparison still conflates trunk-sharing with data-order diversity, which the rule does not address. That asymmetry is generous to the mechanism: had the factor barely moved despite the handicap, architecture would not be the explanation; since it moved, the design flaw is identified but not attributed to trunk-sharing alone. Isolating it would need an ensemble that shares data ordering and not parameters, a different experiment, as rule M-44 states in its own text.

**§6.4's mechanism is a structural fact plus a hypothesis.** That the five members share a trunk, a hidden state and 89.15% of each member's parameters is measured; that this *causes* the epistemic miscalibration is the hypothesis, and only §6.8 bears on it.

**The configuration and architecture verdicts hold at our budget and on our reading.** §5.2
varies one factor at a time at 0.133% of the reference's data, so it cannot say what the
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
10 repositories we examined (§2), which bears on how far the hypothesis reaches, but
we tested the mechanism in none of them.

---

## S3 What should travel, and the conclusion's discussion

*Was the paper's Appendix S, "the conclusion's discussion of the ranking, the scale, the per-dimension evidence, and what should travel (§12)"; moved here to meet the length limit.*

**What should travel, as §12 stated it.** §12 keeps two sentences of this paragraph.

**What should travel from this paper, and what should not.** The findings are of three kinds. *Properties of the objective and of how its bounds are built* are the ones to expect elsewhere,
and only where both are present together: §6.3 derives the σ = 0 optimum from squared
error on a sampled prediction through a bounded head whose floor nothing pushes back up, so it
should hold wherever both are present, the hypothesis §2 states and leaves untested outside this
codebase. On §2's count the substitution is present in 1 of the 10
descendants examined, and there only in a non-default mode; the survey did not examine the floor,
so that is an upper bound on how often both are. *Properties of this released artifact* should be checked
rather than assumed in any other: the one-step misalignment in its evaluation harness (§7.2), the
trunk its five members share (§6.4), and its specific overconfidence factors,
11,683× for the aleatoric σ and 33.4× for the epistemic term
at h = 100 (§6.2), are measurements of one checkpoint. *Properties of this dataset
and its arenas* are limits on what could be resolved, not findings in either direction, and neither pinned repository can lift them (§3): our arms' held-out arena holds 4 independent 400-step
trajectories and all ten episodes hold 20, which is why §11 and supplementary S2 leave the replication at
ensemble size 5, the free-baseline margin over whole trajectories at h = 368 and capacity's share of the
trunk-sharing effect open rather than settled (on shorter units at h = 100, rule X6 settles the margin on the
checkpoint's training episodes). §5.2's configuration verdict should not travel either: it is
resolved, but at our data budget, and says nothing about the original's.

The more useful finding is asymmetric, and it cuts both ways. The scale failure is established and large. The scale may be repairable per horizon, but on a model that has not seen the test episodes the evidence is mixed. On the released checkpoint a per-horizon multiplier, fitted on one episode and scored on another, brings every coverage estimate within 10 points of nominal, where a global multiplier manages 2 of the 12 epistemic cells, though no single cell is resolvable at this arena and the cells are not independent trials (§6.7). Fitted on nine episodes and scored on the tenth, the epistemic coverage over all 20 trajectories is within the band at every horizon (rule X7). On Arm A, whose model never saw those episodes, its own multipliers manage 17 of 36 epistemic cells. And the ranking use the follow-up claims does survive a real test: against the forecast step index, a free baseline neither original paper ran, ensemble disagreement wins at every horizon and keeps +0.596 once the index is partialled out. Against a second free baseline it does less well: the model's own predicted step size ranks error at +0.4697 against disagreement's +0.6053, a margin this sample cannot resolve at h = 368, so the verdict is SURVIVES entry-res ONLY (disagreement beats the one-step error before the window, but not the model's predicted step size). On shorter units of the same episodes, at h = 100, a later rule resolves that margin in disagreement's favour (rule X6: **DISAGREEMENT BEATS STEP SIZE**, +0.2816 [+0.1978, +0.3896]), on the checkpoint's training data. **The control this rests on removes trajectory difficulty rather than forecast depth**: with both the rollout and the depth held constant, disagreement still correlates +0.419 [+0.318, +0.576] with realised error (§6.6). That is smaller than the +0.605 pooled figure, and it is the one that means what a practitioner needs it to mean: not a re-encoding of the clock, and not merely a report of which episode is hard. It is the closest either original work comes to a claim this reproduction strengthens rather than qualifies, and even there the strengthening is of the ordering, not of the ensemble that produces it, since a free subtraction ranks nearly as well over whole trajectories.

What does not survive is the per-dimension form of the ordering evidence. Three of the five σ estimates we measured order their own errors better than chance in direction: the epistemic term on every one of the 45 dimensions at h=368, and the faithful and teacher-forced arms. That count is a direction, not a tally of independent trials, since the dimensions are physically coupled (§6.5). The released checkpoint's *aleatoric* head does the opposite, ranking error inversely at h = 368 on every one of 45 dimensions over all ten episodes and at chance on the held-out pair alone, a dependence on arena that §6.5 sets out. The corrected arm sits at chance in both. Once the coupling is respected by permuting whole trajectories, no per-dimension count in this paper reaches significance after multiplicity correction; the independent-trials P-values an earlier draft carried were wrong by up to a factor of about 10^13 and are withdrawn (`S-15`). Neither quantity yields a usable interval. Per dimension, uncertainty in this family of models should be read as a weak ordering at best, or fixed at the objective. As the scalar the method applies, ensemble disagreement gets the order right (§6.6) and the size wrong: it should not be read as a scale, and a ranking use deserves its own validation on the deployment distribution rather than trust inherited from here.

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
members share one GRU trunk, one recurrent hidden state, and 89.15% of each member's
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
checkpoint, with the sharing quantified at 89.15% of each member and its cost bounded by the 2.03× an independent ensemble gains (§6.8).** The problem is not sharing; it is sharing and then reading the
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
(The figure number follows arXiv:2504.16680**v1**; in the current v3 it is Fig. 4, and
the crosswalk is in `results/original_paper_figures.json`.) So the discard is the intended design,
not an implementation slip: the aleatoric head, the one the state loss and the bound loss shape
and §6.3 explains, is computed on every imagination step to shape training and be inspected, and
is never consumed.

## S6 Measurements the paper does not use, with their evidence

*Was the last block of rows of the paper's Appendix H table, "findings not in the main text"; moved here to meet the length limit. Measurements are at 2,500 training iterations unless a row says otherwise or concerns the released checkpoint, and each row names its arena.*

| finding | evidence (ledger ID, artifact) | bearing on the paper |
|---|---|---|
| ***Measurements*** | | |
| The data hold 21 plateaus of achieved base velocity, two per episode with a third in episode 7; the command itself is not recorded, and the plateaus match the simulator's command resampling | D-10; `results/step0_regimes.json` | A held-out episode is not a near-duplicate of a training one: the held-out pair tests generalisation across velocity commands, within one gait and terrain |
| `state_min_logstd`, on the slower gradient path C-11 identifies, drifts 5.2× slower than `log_delta_logstd`; extrapolated from one Arm A run's rates, the two imply about 150,000 and 270,000 iterations for the released variance state, an order of magnitude rather than a fitted count | R-25; `results/step6_3_min_logstd.json` | §7.5's conclusion does not rest on one parameter |
| Over overlapping trajectories on the held-out pair, which the released checkpoint trained on, its worst twentieth carry 92.6% of its squared error at h = 368 as each dimension's own scale weights it (form 2, which `g_z` dominates; Appendix G), and they start within two short ranges of rows, one per episode; on the 4 non-overlapping trajectories the largest is 1.2× the median | R-30; `results/taskAB_gate_r27.json` | A tail measured on overlapping trajectories can be one short stretch of data, which a count of independent trajectories (§3) exposes |
| The A/B relative-L1 gap at h = 368 (teacher forcing's error minus autoregressive training's, over 2 independent trajectories per episode) is positive on all ten episodes, from +0.73 up; episode 1, one of the held-out pair, gives +6.97, 2.5× the next largest, so the pair's +3.98 is 3.0× the other eight episodes' +1.33 | R-39; `results/task4_arenas.json` | The direction is robust across episodes; a magnitude read from the held-out pair overstates the typical episode |
| Per state dimension, over the whole 368-step forecast, the released checkpoint loses to the hold-last floor on 18 of 45 across all ten episodes (20 independent 400-step trajectories) and on 8 on the held-out pair (4), including all three components of the gravity vector; Arm A at 10,000 iterations loses on 1 in each, `g_z` | R-45, and R-29 on overlapping trajectories; `results/task2_3_matched_trend.json` | Per dimension, a model trained from scratch fails far less often, even on the pair the checkpoint trained on and Arm A did not. In aggregate it does not: on the held-out pair the released checkpoint is ahead at h = 8 and level at h = 368 (R-45). One seed (seed 1, supplementary S2) |
| Over five checkpoints up to 10,000 iterations, the absolute A/B gap at h = 368 narrows as both arms improve (held-out pair, n_independent = 4 400-step trajectories, +3.33 to +1.20; in-sample, n_independent = 16, +1.72 to +0.87), while the ratio does not shrink (3.34× to 4.43×, in-sample 2.33× to 9.70×). The held-out values are not monotone: both peak at the second checkpoint (+6.74, 12.38×), one anomalous Arm B value | R-46; `results/task2_3_matched_trend.json` | An absolute effect quoted early overstates what remains, a ratio does not, and §5 reports ratios at 10,000 iterations; one seed (seed 1, supplementary S2) |
| Our trained models respond to the action they are given: fed another trajectory's actions, Arm A's error at h = 8 on its in-sample arena's 16 trajectories rises by +227.8% at 2,500 iterations and +676.3% at 10,000 (rule X2, pre-registered: RESPONDS TO THE ACTION) | M-84, M-85; `results/action_sensitivity.json` | A world model must respond to actions before it can serve policy optimisation; ours do on this test, though every action in the data comes from one policy and no policy is trained here (§7.2, Appendix V) |

## S7 Compute: runtimes, the queues and their overlaps

*Was the rest of the paper's Appendix B, after the reproduce commands; moved here to meet the length limit.*

**Runtime.** Training stages are excluded by `--quick`, which is what makes the quick path practical. Training all 33 runs takes **49.8 hours** of recorded wall clock on two CPU cores: 19.7 hours for the 6 runs at 10,000 iterations and 30.1 for the remaining 27 at 2,500. The longest single run is 4.4 hours. Every figure here is read from the `wall_clock_s` field of the run artifacts rather than estimated.

**5 of those 33 runs, 1.9 hours, are `M-49`'s capacity-matched
arm at `rnn_hidden_size` 124** rather than the released 256. They are part
of this project's CPU spend and are counted in the total above — the other 47.9
hours are the 28 runs at the released width, and the two parts are asserted to make the
total rather than stated beside it. They are **not** part of the 28 runs of §6.3's σ-collapse family, because §6.3's rate is a property of one architecture and mixing widths into it would make "nearly identical across runs" a claim about two
different models. Every run artifact records the width it trained at, and `paper_numbers.py`
selects the collapse family by that field rather than by filename; `docs/BUILD_CHECKS.md`, shipped as supplementary, records how that selection came to be made.

**The pre-submission runs are counted separately.** §5.2's sweep and §5.3's baselines added
42 runs and **28.3 hours**: 24 sweep runs (13.4 h),
then 9 teacher-forced and 9 autoregressive baseline runs
(7.9 h and 7.0 h), read from `results/presubmission_runtime.json`. They
are outside the total above, whose remainder that paragraph describes as released-width runs, which
the baselines are not. Of these, 8 overlapped other CPU work a session logged,
which inflates their wall clock and changes no weight; the artifact lists each overlap. Rule X1's Part C (§5.3) ran 2 more teacher-forced RSSM runs from a second queue, 4.2 hours, which are in neither total; 1 of them overlapped CPU work a session logged. Rules X3 and X4 (§5, §5.3) ran 30 more runs from a third queue, 26.5 hours (24 for X3, 17.7 h; 6 for X4, 8.8 h), also in neither total; 4 of them overlapped CPU work a session logged while that queue ran. That queue's log lost its first runner's lines when another session resumed it, so 4 of its runs are timed by the log and the rest by their weights files, as `results/presubmission_runtime.json` records run by run; the resumed runner's runs overlap no logged work because that session logged none. X1's rows follow the baselines', and X3's and X4's close the table. Per run family, every run at 2,500 iterations (the sweep's centre is §5's Arm A, whose runs are counted above):

| run family | runs | hours per run, mean | runs that overlapped other CPU work |
|---|---|---|---|
| (1, 8) (§5.2) | 3 | 0.15 | 0 |
| (2, 8) (§5.2) | 3 | 0.16 | 0 |
| (8, 8) (§5.2) | 3 | 0.30 | 1 |
| (16, 8) (§5.2) | 3 | 0.51 | 2 |
| (32, 1) (§5.2) | 3 | 0.51 | 0 |
| (32, 2) (§5.2) | 3 | 0.74 | 3 |
| (32, 16) (§5.2) | 3 | 0.78 | 1 |
| (32, 32) (§5.2) | 3 | 1.32 | 1 |
| MLP, teacher-forced (§5.3) | 3 | 0.04 | 0 |
| RSSM, teacher-forced (§5.3) | 3 | 1.88 | 0 |
| transformer, teacher-forced (§5.3) | 3 | 0.71 | 0 |
| MLP, autoregressive (§5.3) | 3 | 0.06 | 0 |
| RSSM, autoregressive (§5.3) | 3 | 1.53 | 0 |
| transformer, autoregressive (§5.3) | 3 | 0.74 | 0 |
| RSSM, teacher-forced, PlaNet's KL settings (rule X1, §5.3) | 1 | 2.11 | 1 |
| RSSM, teacher-forced, DreamerV2's layer-normalised cell (rule X1, §5.3) | 1 | 2.10 | 0 |
| Arm A, autoregressive, each episode held out in turn (rule X3, §5) | 12 | 0.74 | 2 |
| Arm B, teacher-forced, each episode held out in turn (rule X3, §5) | 12 | 0.73 | 2 |
| MLP, autoregressive, size-matched (rule X4, §5.3) | 3 | 0.10 | 0 |
| transformer, autoregressive, size-matched (rule X4, §5.3) | 3 | 2.83 | 0 |

## S8 The repository's history

*Was a paragraph of the paper's Data and code section; moved here to meet the length limit.*

**The repository's history was rewritten once, and §8 depends on that history, so we say
what changed.** A supplementary file quoting private correspondence was committed and
briefly published before consent to quote it had been given; it was purged from the history
rather than merely deleted, because a deletion commit leaves the content recoverable from a
public repository indefinitely. Purging a path rewrites every commit from the one that
introduced it onward, so **41 of the 43 commits Figure 3 cites keep their identifiers and two do not**: the two made between that file's introduction and the purge. Timestamps, content and ordering are unchanged; only the hashes moved, and for that reason Figure 3 finds its first rules' commits by subject and the later ones by the commit that introduced their ledger heading, never by a stored hash alone. The transcript itself reaches reviewers in the anonymised
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
use our measurements rule out. At the method's own 100-step horizon, the disagreement
is 33.4× smaller than realised error and covers 4.61% of
outcomes where 68.27% is expected. We say this because the released checkpoint
exposes the quantity, and it is easy to read as an interval.

We do not claim the original method is unsafe. No policy is trained here. The one policy-free
test we ran found that correcting the scale per horizon leaves every pairwise ordering of accumulated penalty unchanged on the available trajectories, a test whose null is partly structural (§11).

## S11 Reproducibility accounting and the build's own checks

*Was a paragraph of the paper's section 8; moved here to meet the length limit.*

**Reproducibility, and a build that checks its own prose.** Every measured number in this paper is
substituted from an artifact on each build, and a quick run on a clean clone (`./reproduce.sh --quick --force`, which skips
training) rewrites 0.68% of the numeric values under `results/` that the comparison counts; the rest are carried in
and prove nothing about reproduction. **The number of regenerated values that differ and are
themselves a measurement, a statistic or the verdict of a test is 0.** The clean-clone gate requires that
none differ at all; 3 do, so it fails and is published as failing. The supplementary
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
The base paper's central training claim reproduces under a rule committed in advance (seed 1): over
3 seeds, training on the model's own rollouts beats teacher forcing 4.61× at 368 steps,
though not at one step on short windows. Retrained on fixed folds holding out each episode once (2,500 iterations, not 10,000), its direction **REPLICATES ACROSS FOLDS** (20 trajectories).
At 368 steps RWM beats MLP, RSSM and transformer baselines built to our reading, all worse than predicting
no change; matched only in size, the transformer is unresolved (PARTIAL).
On accuracy alone, two shorter histories and both longer training forecasts beat the original's setting at our budget, no reading favouring it; trained
longer, it passes each on some reading (post hoc): the ranking depends on training budget. Magnitudes rest on
4 held-out trajectories, 0.133% of the reference's data, one robot, gait and terrain.
The follow-up's uncertainty gets the order right and the size wrong: ensemble disagreement correlates +0.605 with error but is 33.4× too small at 100 steps on training data.
Predicted step size ranks error nearly as well over whole trajectories, worse on shorter units at 100 steps. Members share 89.15% of parameters; independent models are
2.03× better calibrated, still overconfident. The implemented loss provably drives the discarded
per-member σ to zero. Per-horizon rescaling brings the released checkpoint's coverage within 10 points of nominal
for disagreement at every horizon on training episodes left out of each fit; on episodes our ensembles never saw,
only 17 of 36 cells. The released evaluation is one step stale;
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

Figure 1 shows one finding about each original paper. Panel (a) is the base paper's claim that training on rollouts beats teacher forcing, measured on episodes the models never saw: the gap at h = 368, one interval per fold and one point per held-out episode. Panel (b) asks whether the uncertainty-aware follow-up's spread grows with the horizon as the error does, under the released rollout and under a per-member rollout that is not the released method.

We set out to reproduce the base paper: rebuild the proprioceptive dynamics model from scratch,
check it against the released implementation, and test the central training claim, which holds at long horizons.
The rebuild made a second question cheap to ask: *is the predicted σ calibrated?* Neither of the
two the checkpoint emits is. On data it trained on, the per-member σ is too small by
1,827× at h = 1 to 20,669× at h = 368, by construction
(§6.3), and the ensemble disagreement the method uses by 8.3× to
34.4×. The disagreement still ranks realised error, the use the method makes of it
(§6.6).

This is a reproduction in the stronger sense: the contribution is not that the numbers came out
the same, but what re-measuring the method reveals about where it is robust and where it is not.
Three things distinguish it from a re-run of the authors' code. **We rebuilt rather than
imported**, and matched the rebuild to the reference before any training (Appendix A), so a later
discrepancy belongs to the method, not to our wiring. **Decision rules were committed to git
before the data**, with timestamps a reader can check (§8, Figure 3); several returned verdicts against the original or could not settle the question, and we report each (Appendix E). **We keep our withdrawn findings in the record.** The ledger keeps
24 superseded entries, each beside the evidence that withdrew it:
nine claims withdrawn on evidence, eight framings withdrawn,
and the rest early hypotheses closed as housekeeping (§8 and the supplementary
`docs/BUILD_CHECKS.md`; every pre-registered rule, with its lead time and verdict, is in Appendix E). §9 gives the lessons in a form
a practitioner can use without reading the rest.

**Contributions.**

- **The uncertainty gets the order right and the size wrong, in the first calibration
  measurement we are aware of for this released checkpoint** (Lu et al. (2022) measure this family
  of penalties on models they train themselves; §2). Ensemble disagreement ranks realised error,
  correlating +0.419 with it with rollout and forecast depth held fixed, yet on data the
  checkpoint trained on it is 8.3× smaller than that error at h = 1 and
  33.4× at h = 100 (§6.2, §6.6). It beats 1 of the
  2 free baselines added here; the model's own predicted step size ranks error at +0.4697 against its +0.6053 over the 20 whole trajectories, a margin they cannot resolve at h = 368, while on 70 shorter units at h = 100 a rule committed before its reading finds disagreement ahead, +0.2816 [+0.1978, +0.3896] (rule X6: **DISAGREEMENT BEATS STEP SIZE**; §6.6, §11).
- **The base paper's central training claim reproduces, and reverses at one step.** A rule committed before the runs, run on seed 1 of each arm, found autoregressive training ahead by 4.43× at h = 368; 3 seeds at 10,000 iterations extend it: the factor is 4.61×, and 2.58× at h = 100, on the held-out pair's 4 independent 400-step trajectories (§5); retrained on fixed folds with each of the ten episodes held out once, the direction replicates, +2.2275 [+1.3683, +3.5053] at h = 368 over 20 trajectories at 2,500 iterations, not 10,000 (rule X3: **REPLICATES ACROSS FOLDS**). At one step a second pre-registered rule, on 60 independent
  33-row units, finds a gap of -0.0194 [-0.0310, -0.0093] in favour of **teacher forcing** (§5).
- **Two more of the base paper's claims, tested under rules committed before the runs.** RWM is
  ahead at h = 368 of MLP, RSSM and transformer baselines built to our reading of its
  specification and trained with RWM's settings, whether teacher-forced as the original trains them or autoregressively, on the held-out pair's 4 independent trajectories at 2,500 iterations, though every baseline is worse there than predicting no change; matched to RWM's parameter count, the MLP stays behind and the transformer cannot be told apart (rule X4: **PARTIAL**; size is one axis), and neither reading our RSSM's forecast from its prior's expected or sampled latent nor retraining it with two other settings on one seed removes its open-loop collapse (rule X1, exploratory: **NOT RESCUED BY THE SETTINGS TRIED**; §5.3). On accuracy alone at our budget, four of the eight one-factor neighbours of the original's (M, N) = (32, 8) beat it, two shorter histories at under half its cost per iteration and both longer training forecasts at more (no reading the rule reports puts the centre ahead of any of them), but trained longer the centre passes each of them on at least one reading (post hoc), so the ranking depends on the training budget; the original chose the centre as a trade-off with training time, which its own printed hours are consistent with and we do not test (§5.2).
- **The σ = 0 optimum of the implemented objective.** The implemented state loss is minimised at
  σ = 0, so the per-member σ the method discards collapses by construction: derived, and
  demonstrated against known noise (§6.3).
- **Trunk-sharing, tested.** The five members share one trunk, one recurrent state and
  89.15% of each member's parameters, so their spread can express only uncertainty the
  trunk already carries (§6.4). Under a rule committed before the runs, on the held-out pair's 4 independent trajectories, 5 independently initialised full models are 2.03× better calibrated than the shared-trunk arms, against a pre-registered minimum detectable effect of 1.45×, and still 5.2× overconfident at h = 100; they also differ in capacity and data order, so this bounds the sharing effect rather than isolating it (§6.8).
- **Per-horizon recalibration, with mixed evidence.** One multiplier per horizon, fitted on one
  episode and scored on the other, brings every released-checkpoint coverage estimate near nominal
  where a global one does not, though no single cell is resolvable and the cells are unseen only by
  the multiplier, since the checkpoint trained on both episodes (§6.7); on Arm A, which never saw them, its own multipliers manage
  17 of 36 disagreement cells. Fitted on nine episodes and scored on the tenth, the disagreement's coverage over all 20 trajectories is within the band at every horizon (rule X7: **WITHIN BAND AT 6 OF 6 HORIZONS**), again on episodes the checkpoint trained on.
- **The released evaluation is misaligned by one step; over all ten episodes it raises the checkpoint's relative-L1 error up to h = 32, and from h = 100 the change is not resolved.** Evaluation feeds the action from *t−1* where training pairs states and actions index-for-index, and shifting its action index by one step fixes it. On all ten episodes' 20 independent trajectories, all of them training data for this checkpoint, the stale action raises its relative-L1 error by 55.0% [26.3, 92.7] at h = 1 and 37.4% [21.3, 65.4] at h = 32, and changes it by 8.2% [-10.4, 24.9] at h = 100 and -4.6% [-13.4, 3.2] at h = 368; on the held-out pair's 4 it raises it at every horizon reported, by 7.9% [3.1, 13.0] at h = 368 (§7.2).
- **A from-scratch reimplementation verified at the gradient level.** Outputs match the released
  module bitwise, and losses and gradients match to 0.000e+00 across 7 loss
  terms and 106 parameter tensors, before any training (Appendix A).

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
any other descendant (§11). Of 13 public repositories the survey looked at, 10 carry the construction, the ones its protocol counts as examined, and 1 of those trains it against a sampled squared error, only in
an optional mode, so on this sample of convenience the substitution is rare (Appendix I).

**The method's family.** MOPO (Yu et al., NeurIPS 2020) penalises the reward by an ensemble
uncertainty estimate and MOReL (Kidambi et al., NeurIPS 2020) detects unknown states by pairwise
ensemble disagreement, both branching short model rollouts from real states as MBPO (Janner et al.,
NeurIPS 2019) does. The follow-up we reproduce puts MOPO's penalty into MBPO's loop, which is what
"MOPO-PPO" names.

**What "ensemble" is supposed to mean.** Deep ensembles (Lakshminarayanan, Pritzel and Blundell,
NeurIPS 2017) are networks trained from *different random initialisations and different data
orderings*, whereas the released checkpoint's five members share one GRU trunk, one recurrent hidden
state and 89.15% of each member's state-prediction parameters (§6.4).

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
checkpoint, with the sharing quantified at 89.15% of each member and its cost bounded by the 2.03× an independent ensemble gains (§6.8).**

**And the objective in §6.3 has a neighbour.** Seitzer, Tavakoli, Antic and Martius (ICLR 2022)
identify failure modes of σ heads trained by maximising log-likelihood; the released state loss is
not a log-likelihood at all, so the failure §6.3 derives is more basic than theirs.



---

---

## S16 The earlier setup

*Was the paper's section 3 (data, evaluation, effective sample size, metrics, horizons and what each claim rests on) before the rewrite for the review of 19 October; moved here whole. Section numbers in this passage are the earlier paper's.*

**Setup (was §3)**

**Data.** The released dataset is 10,000 rows of ANYmal D proprioceptive state and policy
actions at 50 Hz: ten concatenated 20-second episodes, with a termination column that is
identically zero, so nothing in the file marks the boundaries.

**The segments are not all the same length.** The first episode is 999 rows and the other
nine are 1,000 each, with a reset at rows 999,
1,999 … 9,999 and 1 orphan row at the end of the file
that begins an eleventh episode and ends immediately: 999 + 9 × 1,000 + 1. We recover the boundaries
from the data: at every reset row the twelve joint velocities, the four HAA joint positions and all
twelve actions are exactly zero, and no other row has that fingerprint. Ten equal segments of
1,000 would give one fewer crossing window and one more usable one, so the counts below
differ by one from that reading; `results/step0_regimes.json` re-derives the crossing count from the
segment lengths alone, and the two agree.

A window is 40 rows, 32 of history and 8 of forecast, and the
reference window builder marks all 9,961 windows valid, including 352 that splice
one episode's end onto the next one's start. The usable, episode-respecting count is
9,609: 10,000 rows, less 39 that cannot start a full window, less
352 that cross a boundary. The contamination rate is 3.53%.

**Model.** A GRU-based ensemble predicting the next proprioceptive state, with a mean head and a
bounded log-σ head, plus auxiliary heads for contact and termination. The paper describes two loss
terms; the implementation has 7. Before any training, our rebuild's outputs match the
released module's bitwise, and its losses and gradients match to 0.000e+00 across those
7 terms and 106 parameter tensors (Appendix A).

**Evaluation.** Two arenas, kept separate throughout: *out-of-sample*, the two episodes withheld
from training, and *in-sample*, the eight used for it. The released evaluation draws its
trajectories from training data, and the original does not distinguish the two. **The released
checkpoint trained on all ten episodes, so it has no held-out arena in this dataset**, and every
figure for it is in-sample; later sections refer back to this as the in-sample caveat of §3. More
data cannot be generated from either repository this reproduction pins (supplementary S1).

**Effective sample size.** Trajectory count is not sample size. Two 400-step trajectories whose
spans overlap are not independent evidence, and the out-of-sample arena contains only
4 mutually non-overlapping 400-step trajectories. A bootstrap over whole trajectories at
that size has 256 distinct resamples, so its intervals are quantised at that
resolution. Every long-horizon verdict in this paper is computed with a bootstrap over independent trajectories, every table reports that count, and §8 reports both resampling units where they
differ. Later sections refer back to this as the n = 4 caveat of §3. One trajectory can carry
much of a long-horizon effect: a one-step shift of the action moves the released checkpoint's
368-step relative-L1 error on single trajectories of its own training episodes by anywhere from
-47.4% to +35.2% (§7.2), which illustrates why 4 trajectories bound every
long-horizon claim.

**Metrics (was §3.1)**

Each metric is stated as implemented, because a reader who cannot see the denominator cannot check the headline. Appendix G gives each metric's formula and
the check on the coverage nominal.

**Relative-L1** is the reference's own metric, reproduced in behaviour (`model_training.py:203`) so
that our numbers are comparable to the upstream's printed one. At each forecast step it is the summed
absolute error over the state dimensions divided by the summed absolute true state, on
config-normalised states, averaged flat over trajectories and over the steps after the first
32, which are teacher-forced. The denominator, a 45-term sum in normalised space, is
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
two-sided, so its calibrated targets are **68.27%** at ±1σ and
**95.45%** at ±2σ.

**The overconfidence factor** $\rho$ is the mean absolute error over the mean predicted σ, a ratio
of means. $\rho = 1$ is *not* calibration, since a calibrated Gaussian has $\rho = \sqrt{2/\pi}$ =
0.7979, so $\rho$ is reported as a magnitude of miscalibration and coverage as the
calibrated reading.

**Which metric each headline uses.** The A/B training claim (§5) is relative-L1, because the claim
is about reproducing the upstream's comparison and that is the upstream's metric. The calibration
claims (§6.2) are the overconfidence factor and coverage, because neither error metric involves σ.
The ranking claims (§6.6) are Pearson correlations between the applied scalar penalty and total
absolute error, because a ranking claim is about order rather than scale. Every headline number in
the abstract names its metric. §7.2's alignment defect is given in both metrics, over all ten episodes and on the held-out pair. Over all ten episodes the two metrics agree that the stale action raises error at h = 8 and 32 and that from h = 100 the change is not resolved, and they differ at h = 1, where relative-L1 resolves the rise and nRMSE does not.

**Horizons.** Curves are reported at $h \in \{1,\,8,\,32,\,100,\,128,\,368\}$.
Every horizon-indexed quantity is cumulative over steps 1..h, not the value at step h. Two of those are load-bearing and the rest are landmarks. **h = 100** is the method's
own imagination rollout length, the horizon over which the uncertainty-penalised policy loop
actually runs this model (arXiv:2504.16680 Table S9 in v1 and Table S11 in v3, with the same
value). **h = 368** is the upstream's open-loop diagnostic length: `len_eval_trajectory` =
400 minus the 32-step teacher-forced prefix, the curve the follow-up plots
as its uncertainty figure. It is 3.68× the method's own rollout length and is not a
deployment horizon. Every table keeps both: h = 368 makes our numbers comparable to the
original's *figure*, and h = 100 to its *method*.

**What each claim rests on (was §3.2)**

Every headline claim in this paper is measured on the out-of-sample or in-sample arena above, or on all ten episodes together, at a stated number of independent units (400-step trajectories unless the row says otherwise). Each is also at a stated checkpoint: the released one, or ours at a stated
number of training iterations. Appendix D's second table, "What each tested claim rests on", gives each claim's arena, sample size, checkpoint and verdict. It is generated from the artifacts each claim is computed from, so no arena label, sample size or checkpoint in it is typed by hand.

---

---

## S17 The earlier method section

*Was the paper's section 8 (the ledger, the one failed pre-registration, the withdrawal counts and the resampling-unit correction) before the rewrite for the review of 19 October; moved here whole. Section 3.4 of the paper keeps what the paper needs. Section numbers in this passage are the earlier paper's.*

**Method (was §8)**

**An append-only ledger.** Every claim here has a permanent identifier, an evidence class (source, data, run, external, inference) and a status, in `FINDINGS_LEDGER.md` (310 entries). Claims are never edited in place: one that turns out to be wrong is marked superseded, pointed at what replaced it, and kept.

**Pre-registration, and one failure of it.** Decision rules were committed to git before the data that tested them, with one exception. Figure 3 and Appendix E give the lead time for each of the 35 whose data exist; 34 are positive and 1 is not. Every positive bar is a difference of two commit timestamps. **The negative one is not**: it is the duplication-control rule (§7.4), whose *data* side is the moment the control runs finished, a line in `results/control_driver.log` rather than a commit, dated from the commit that introduced that line. The rule was stated in conversation before the runs and reached git **2.9 hours after they finished**, and we found it only by auditing our own `git log`. The measurement stands, because the arm was built without reference to its outcome, but the claim that it was pre-registered does not, and it is withdrawn. A discipline that is only checked when it succeeds is not a discipline.

**Nine claims withdrawn on evidence**, and eight framings withdrawn rather than numbers, out of 24 superseded entries kept in the record (the supplementary `docs/BUILD_CHECKS.md` lists them). The most consequential of the framings withdrawn is the inference from per-dimension sign counts to a binomial P-value, which assumed an independence the 45 state dimensions do not have (§6.5). Found by our own pre-submission audit, it withdraws the strength of evidence behind what an earlier draft called its strongest result.

**A statistic that was resampling the wrong unit.** Our bootstrap pooled three seeds over a shared trajectory set and resampled the pooled vector while reporting the independent-trajectory count, so each trajectory appeared three times. Resampling trajectories instead widens intervals by a mean 1.42× and changes 1 of 16 verdicts, in the out-of-sample h = 8 cell at 200-step trajectories and 2,500 iterations, already recorded as unresolvable. Every long-horizon verdict survives; both units are reported.



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

**We tested six claims and left six untested.** The six are the base paper's
autoregressive-versus-teacher-forcing comparison and its claim that teacher forcing generalises
poorly (§5), its configuration claim (§5.2) and its claim against MLP, RSSM and transformer
baselines (§5.3), and the follow-up's two claims about what its uncertainty outputs report (§6).
**Every one of the six we did not test needs a simulator or hardware we do not have**: zero-shot transfer, the sample-efficiency result, the comparisons against SHAC and Dreamer, generality across robot morphologies, offline MBRL on real robots and the core claim that penalising rewards by disagreement improves the learned policy.
**Five of them are claims about policy learning or hardware** — every one but
generality across robot morphologies, which needs a simulator and recorded data from other robots but is a claim
about the model rather than about a policy. This work trains no policy and runs on two CPU cores.
The counts and lists are generated from the classification tags in the verdict column of Appendix D's first table, so none of them is typed. §11 states what the untested claims bound, and supplementary S1 what testing them
would take.

**For four of the six claims we tested, the original reports no quantitative
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
seed 1 of each arm: autoregressive 0.3509 against teacher forcing 1.5540 at
h = 368, 4.43×, gap interval [0.56, 2.05]. The 10,000-iteration runs of seeds
0 and 2 were trained after the verdict (the ledger records them on 2026-08-22), so the three-seed
figures below extend it
and carry none of its weight. The rule is anchored at
h = 368, the upstream's **open-loop diagnostic** length and not a deployment horizon
(§3.1), and its verdict is returned there; we do not re-anchor a discharged rule. The method's own
horizon is h = 100, so the comparison is reported there too, and the two differ in size.

**Result.** Every condition holds. We give the evidence in order of how little it depends
on the small held-out sample.

*The sign test, which does not depend on n.* At h = 368 the per-episode gap favours autoregressive training on **10 of 10** episodes, an exact two-sided binomial test with p = **0.0020**. At h = 100 it is **10 of 10**, p = **0.0020**, and at h = 1 it is 3 of 10, the same story the interval tells. It uses no bootstrap or multiplicity correction, and episodes, unlike §6's state dimensions, are separable units, so a binomial null is admissible. **Its scope is narrower than the arena labels suggest**: 8 of the 10 episodes are training data for *both* arms. The test is a valid **paired** comparison, since both arms saw identical data and an episode-level difference is due to the training rule rather than to memorisation, but it is not ten out-of-sample episodes and does not measure generalisation. The out-of-sample effect size below carries that burden, on 4 independent trajectories.

*The in-sample arena, where the sample is larger.* The same comparison on the eight training
episodes has 16 independent 400-step trajectories against the held-out arena's
4, 4× more. It gives the same direction at every horizon and checkpoint
but one: at h = 8 after 500 iterations teacher forcing leads in-sample, with an interval that
excludes zero at both trajectory lengths (`results/review_bootstrap_unit.json`).

*The out-of-sample effect size, at every horizon.* At h = 368, the rule's horizon, the
three-seed extension puts autoregressive training at **0.3582 ± 0.0283** against teacher forcing's
**1.6497 ± 0.2858** (standard deviation over seeds, `ddof=1`), a factor of **4.61×**. Arm B predicts each of the window's 8 forecast targets from
true inputs, where the original's teacher forcing is $N = 1$, and the direction holds under both
definitions (Appendix L).
At h = 100, the method's own imagination rollout length and the
horizon everything in §6 is anchored to, the same three seeds give **2.58×**.
Quoting one and not the other would be a choice, so we report the curve (Figure 6, Appendix L): same rollouts,
same 3 seeds at 10,000 training iterations, same held-out arena,
n_independent = 4, with a cluster bootstrap over whole trajectories. The two floor columns are each arm's error divided by the hold-last floor's, so a value below one beats the floor:

| h | autoregressive | teacher forcing | ratio | gap [95% CI] | excludes 0 | hold-last floor | A ÷ floor | B ÷ floor | episodes A leads |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.1447 ± 0.0023 | 0.1319 ± 0.0172 | 0.91× | -0.0128 [-0.0329, +0.0013] | **no** | 0.0796 | 1.82× | 1.66× | 3/10 |
| 8 | 0.3087 ± 0.0318 | 0.3572 ± 0.0088 | 1.16× | +0.0485 [+0.0271, +0.0844] | yes | 0.3298 | 0.94× | 1.08× | 10/10 |
| 32 | 0.3415 ± 0.0491 | 0.6555 ± 0.0699 | 1.92× | +0.3140 [+0.1233, +0.5047] | yes | 0.5950 | 0.57× | 1.10× | 10/10 |
| **100** | **0.3700 ± 0.0290** | **0.9561 ± 0.0211** | **2.58×** | **+0.5861 [+0.2174, +0.9547]** | **yes** | 0.7558 | **0.49×** | **1.27×** | **10/10** |
| 128 | 0.3558 ± 0.0231 | 0.9881 ± 0.0376 | 2.78× | +0.6324 [+0.2716, +0.9931] | yes | 0.7999 | 0.44× | 1.24× | 10/10 |
| **368** *(the rule's horizon)* | **0.3582 ± 0.0283** | **1.6497 ± 0.2858** | **4.61×** | **+1.2915 [+0.7004, +2.3390]** | **yes** | 0.9930 | **0.36×** | **1.66×** | **10/10** |

**The advantage does grow monotonically with forecast depth.** Over 400-step
trajectories the gap excludes zero at 5 of 6 horizons and
spans it at h=1. So h = 368 is the end of a trend rather than a point we
picked, h = 100 sits partway along it, and the claim is weakest inside the horizon the model is trained on. **Only the h = 368 row is the rule's horizon, and the rule ran on seed 1 alone.** Every
value in the table is a three-seed mean computed after the data existed, so by this paper's own standard (§3.4)
none carries a pre-registration's weight. That is the same treatment §6.6 gives the expectation we held about the
counter-baseline, and nothing in the table discharges or re-opens the rule. Teacher forcing is more than
twice as variable across seeds as autoregressive training at h = 368, so a single-seed
comparison of these two arms is unreliable; Appendix L gives the seed spread and the four
per-trajectory gaps, 4 of 4 positive.

**At h = 1 the table understates the evidence, and the correction runs against us.** The row
rests on 4 independent 400-step trajectories, a unit only the longest horizon needs.
Under a rule committed before the index was built (rule M-64, Appendix E), we rebuilt it at
33 rows, 32 of history and one forecast step, non-overlapping within an episode:
60 units on the same two episodes. The gap is -0.0194
[-0.0310, -0.0093]: it **excludes zero, in favour of teacher forcing** (0.85×). Both
readings are reported: the rule above was discharged on the 400-step unit, and the short unit resolves the sign. At one step **autoregressive
training is worse**, the direction the sign test and, on the 400-step unit, the hold-last floor already pointed.

*Against a baseline, because neither number means anything without one.* The hold-last floor,
predicting that nothing changes, scores **0.9930** at h = 368, where
autoregressive training beats it by **2.8×** (2.0× at
h = 100) and **teacher forcing is 1.66× worse than assuming nothing
changes at all** (1.27× at h = 100). Those are 400-step units, on
which the floor beats teacher forcing at every horizon and the autoregressive arm at
h=1. On M-64's shorter units teacher forcing beats the floor at
h = 1, 8, 32 and 100, and both arms beat it at h = 1 (Appendix L).

**What is small, and where it resolves.** At h = 8, the horizon the model is trained on, the
advantage is small: the table's 10,000-iteration gap there excludes zero only with all
3 seeds pooled. At the 500 and 2,500-iteration checkpoints the out-of-sample gap excludes zero in **0 of 4** h = 8
cells, and an earlier rule anchored there (rule M-16)
returned **CANNOT BE SETTLED AT THIS BUDGET**. **The advantage is small at the training horizon and large beyond
it**: at long horizons the out-of-sample gap excludes zero in **4 of 4** cells at those checkpoints, each
still excluding it after correction for the family of 8 comparisons. Appendix L sets
these cells and our arms beside the released checkpoint they reimplement.

**Held out in turn, every episode tests the claim out of sample once.** The 4 trajectories above are one fold. Both arms were trained on four more such splits, fixed in advance, so that each episode is held out in exactly one of five (rule X3, committed before the runs; 2,500 iterations, 3 seeds). Over the 20 independent out-of-sample trajectories of all ten episodes, the gap at h = 368 is +2.2275 [+1.3683, +3.5053], favouring autoregressive training: **REPLICATES ACROSS FOLDS**. All 10 of the 10 episodes favour it (P = 0.002), and every fold's own interval excludes zero, its gap running from +0.6554 to +3.9828 (Appendix L). At one step teacher forcing still leads on short units, -0.0090 [-0.0126, -0.0053] over 300 33-row units. These are 2,500-iteration models, not the 10,000-iteration ones behind the factor above, which X3 does not re-read; its interval resamples trajectories, carrying every seed, and its folds pair episodes in index order rather than by speed. The 4 trajectories of §5's arena are no longer the only out-of-sample evidence.

**The data budget, which is the one part of the sample-efficiency claim we can measure (was §5.1)**

The base paper's headline is a sample-efficiency result about policy learning and hardware, which
we cannot test, but its *world-model* half is a quantity we can count exactly: **our arms consume
7,991 distinct state transitions, 751× less data than the reference's 6,000,000,
0.133% of its world-model budget**. On that budget the training result above still
reproduces. Appendix L gives the count and its three limits, the first being that this is not the
policy-learning comparison.

**The configuration claim: history and forecast horizons (was §5.2)**

**Claim under test.** The model reads a history of M past steps and, in training, forecasts the
next N steps from its own predictions. The base paper sweeps both and says that moderate values give
an optimal trade-off between accuracy and training time, with (M, N) = (32, 8) as the instance
(§IV-C). Its heatmap prints the error of every cell, and the centre's is the tied-lowest, level with
its longest-forecast neighbour (`docs/presubmission/ORIGINAL_SPECS.md` a.5). Its second heatmap prints training hours: 1.07 for the centre and 2.27 for (32, 32), 2.12×, so on the original's own figures the centre matches that neighbour's printed error, 0.47, in under half the time. Our measured cost per iteration for the same pair is 1.81× (the table's last column).

**Rule, committed in advance** (rule M-74, Appendix E). It tests the accuracy half only: whether the centre has the lowest error among its eight one-factor neighbours in the original's
grid, M of 1, 2, 8 and 16 at the centre's N and N of 1, 2, 16 and 32 at its M. Each is trained as Arm A
is, for 2,500 iterations on three seeds. The statistic is a configuration's
relative-L1 at h = 368 minus the centre's, averaged over trajectories and tested by an exact
bootstrap over trajectories, with Holm's correction holding the chance of any false "better" in the
family at α = 0.05. Training time is reported and governs nothing: hours on
two CPU cores are not what the original timed on a GPU.

| (M, N) | relative-L1, h = 100 | relative-L1, h = 368 | difference from the centre [95% interval] | result | cost per iteration, relative to the centre |
|---|---|---|---|---|---|
| **(32, 8)**, the centre | 0.4798 | **0.5856** | — | — | 1.00 |
| (1, 8) | 0.3796 | 0.5340 | -0.0516 [-0.1835, +0.0400] | not resolved | 0.23 |
| (2, 8) | 0.3524 | 0.4717 | -0.1139 [-0.2988, -0.0088] | **configuration better** | 0.26 |
| (8, 8) | 0.4043 | 0.4852 | -0.1004 [-0.2449, -0.0167] | **configuration better** | 0.40 |
| (16, 8) | 0.4467 | 0.6161 | +0.0305 [-0.0008, +0.0720] | not resolved | 0.60 |
| (32, 1) | 1.0903 | 3.7198 | +3.1342 [+1.3012, +6.5096] | centre better | 0.81 |
| (32, 2) | 0.8886 | 2.0374 | +1.4518 [+0.6250, +2.6933] | centre better | 0.95 |
| (32, 16) | 0.3544 | 0.3347 | -0.2509 [-0.5218, -0.0956] | **configuration better** | 1.35 |
| (32, 32) | 0.3348 | 0.2987 | -0.2869 [-0.5951, -0.1005] | **configuration better** | 1.81 |

**Arena: out-of-sample held-out pair, episodes 1 and 8, 4 non-overlapping 400-step trajectories, n_independent = 4.** Each row is the
mean over three seeds at 2,500 iterations (`results/mn_sweep_eval.json`). A
difference is positive when the centre is better, and "result" is after Holm
(`results/mn_sweep_verdict.json`). The last column is a configuration's steady training time per
iteration over the centre's, timed without contention (`results/mn_compute_matched.json`); hours per
run, and the 8 of 24 sweep runs that overlapped other logged CPU work,
are in Appendix B. The hold-last floor is 0.7558 at h = 100 and 0.9930 at h = 368.
The nRMSE readings quoted alongside the rules here and in §5.3 are pooled as §3.1 defines it,
recomputed afterwards (post hoc; Appendix U).

**Result: NOT OPTIMAL AT OUR BUDGET.** (32, 32), (32, 16), (8, 8) and (2, 8) beat the centre (two shorter histories and both longer training forecasts), (32, 2) and (32, 1) are worse, and
(1, 8) and (16, 8) cannot be told apart from it. At h = 368 the lowest error is (32, 32)'s,
0.2987 against the centre's 0.5856, a difference of -0.2869
[-0.5951, -0.1005]. The verdict does not rest on the anchor: on the in-sample arena's 16 independent 400-step trajectories, all four readings there return the same verdict, and among the held-out readings the rule
reports alongside, every one agrees except nRMSE at h = 1, which returns CANNOT BE DISTINGUISHED. Per configuration, no reading puts the centre ahead of any of the four winners, though several leave a winner unresolved: all four at h = 1 on the held-out pair in both metrics, the two longer forecasts also at h = 8, and (2, 8) on held-out nRMSE at h = 368, (8, 8) on in-sample relative-L1 at h = 368 and (32, 32) on in-sample nRMSE at h = 100. Per episode, the centre is ahead of (2, 8) on 1 and of (8, 8) on 2 of the ten, and of neither other winner on any.

**At our budget, shorter histories win.** The original's error falls steeply
from M = 1 to M = 8 and then flattens (`ORIGINAL_SPECS.md` a.5). On the governing reading ours does
not fall steeply: (2, 8) and (8, 8), histories shorter than the centre's, beat it, and no
shorter history is resolvably worse. Other readings the rule reports, though, put shorter histories
behind it: (1, 8) on in-sample relative-L1 and nRMSE at h = 368, and (16, 8) on held-out nRMSE at h = 368. That is a statement about learning speed at this budget, not about converged accuracy: trained four times as long, the centre passes both winning shorter histories on three of the four readings (Appendix U). So it does not contradict the original's steep fall to M = 8, whose training budget the original does not state. The original's direction on N holds: the shortest forecasts
are far worse, which is §5's teacher-forcing result again, and the longest are better, so the
centre's tie with its longest-forecast neighbour becomes a loss.

**Accuracy at equal compute (post hoc).** The shorter histories that win cost less per iteration
than the centre, 0.40× for (8, 8) and 0.26× for
(2, 8), so their wins at 2,500 iterations need no compute correction. The
longer forecasts' wins do. Trained to 5,000 iterations, 1.11× the computation of
(32, 32), the centre splits the readings with it; trained to 10,000,
2.21× its computation, it is ahead on both in-sample readings and neither held-out
difference is resolved. Which setting is most accurate therefore depends on how long each is
trained (Appendix U gives every reading); none of this re-opens rule M-74.

**Limits.** One factor is varied at a time, so no interaction between M and N is tested. Our data
budget is 0.133% of the reference's (§5.1), and the original states neither the ablation's
budget, its evaluation data nor the horizon behind its error, so the verdict holds at our budget and
no further: a larger one may favour a longer history. All 48 runs at 2,500 iterations are still lowering their training loss at the end
(post hoc; Appendix U), so the ranking is at this budget, not at convergence, and it changes with
training length. With 4 independent trajectories, the rule's minimum detectable effect at h = 368,
the difference its first Holm step would usually detect, is about 14.5% of the centre's
error.

**The architecture claim: MLP, RSSM and transformer baselines (was §5.3)**

**Claim under test.** The base paper compares RWM with three **architecture baselines**: other network designs trained on the same data to make the same predictions. They are a multilayer
perceptron (MLP) over a flattened window of history; a recurrent state-space model (RSSM; Hafner et al., ICML 2019), in the form DreamerV2 refined (Hafner et al., ICLR 2021); and a decoder-only transformer. It says RWM
"consistently achieves the lowest prediction errors across all environments" (§IV-D), gives no number (Fig. 7), and trains the baselines teacher-forced.

**What we built.** The pinned upstream code has an MLP but no RSSM or transformer, so all three are ours, the MLP following the upstream one. They follow the shapes in the original's Table
S7 as we read it, with 610,484 (MLP), 3,180,468 (RSSM) and 132,148 (transformer) parameters against RWM's
714,164. Where the table is silent they take RWM's data, windows, objective, optimiser,
iterations and seeds, and the RSSM takes its latent, activation and KL settings from DreamerV2. Each choice is a row of
`docs/presubmission/BASELINE_SPECS.md`. Only the predicted state is compared.

**Two rules, committed in advance** (M-75 and M-76, Appendix E). M-75 trains the baselines
teacher-forced, as the original does. M-76 trains them autoregressively, as RWM is, so that training rule and architecture are not confounded. Both take Arm A at 2,500 iterations
as RWM and test each baseline's relative-L1 at h = 368 against it, on §5.2's arena with
§5.2's bootstrap and Holm correction.

| model | parameters | relative-L1, h = 100 | relative-L1, h = 368 | difference from RWM [95% interval] | result | cost per iteration, relative to RWM |
|---|---|---|---|---|---|---|
| **RWM** (Arm A, autoregressive) | 714,164 | 0.4798 | **0.5856** | — | — | 1.00 |
| MLP, teacher-forced † | 610,484 | 1.2057 | 145.1650 | +144.5794 [+14.8420, +373.9553] | RWM better | 0.07 |
| RSSM, teacher-forced | 3,180,468 | 2.2128 | 6.3718 | +5.7862 [+2.6251, +10.8616] | RWM better | 2.37 |
| transformer, teacher-forced † | 132,148 | 2.0607 | 15.1548 | +14.5692 [+8.7931, +24.0102] | RWM better | 0.91 |
| MLP, autoregressive | 610,484 | 0.5400 | 1.4628 | +0.8772 [+0.4248, +1.5662] | RWM better | 0.08 |
| RSSM, autoregressive † | 3,180,468 | 3.2660 | 10.6405 | +10.0549 [+5.7436, +18.1659] | RWM better | 1.99 |
| transformer, autoregressive | 132,148 | 0.5821 | 1.8771 | +1.2915 [+0.7258, +1.8079] | RWM better | 0.97 |
| MLP, autoregressive, size-matched (X4) | 713,171 | 0.5893 | 1.4696 | +0.8840 [+0.2036, +1.6334] | RWM better | — |
| transformer, autoregressive, size-matched (X4) | 686,196 | 0.5846 | 0.7911 | +0.2055 [-0.0969, +0.7399] | CANNOT BE SETTLED | — |

**Arena as in §5.2: out-of-sample held-out pair, 4 non-overlapping 400-step trajectories, n_independent = 4.** Each row is the mean over
three seeds at 2,500 iterations (`results/baselines_eval.json`). A difference is
positive when RWM is better, and "result" is after Holm (`results/baselines_verdict.json`). The last
column is timed beside RWM in one sitting (`results/mn_compute_matched.json`); hours per run are in
Appendix B. † marks a diverged row, whose mean run-away rollouts dominate; no verdict depends on that
magnitude, only on the sign, which favours RWM on every trajectory (Appendix L). The two size-matched rows (rule X4) are trained autoregressively for 2,500 iterations on three seeds and scored on the same arena (`results/x4_matched_baselines.json`); they were not timed in that sitting, so their last cell is empty.

**Result: REPRODUCES with the baselines teacher-forced, and RWM AHEAD OF ALL THREE with them
trained autoregressively.** RWM is ahead of baselines built to our reading of Table S7 and trained
with RWM's settings for 2,500 iterations: all six comparisons favour it, with
intervals that exclude zero. That says less than it seems at h = 368, where every baseline
row, in both regimes, is above the hold-last floor and RWM is below it: no baseline beats predicting
no change. The second verdict compares architectures at one training regime and is not a verdict on
the original's claim, which the first carries. The lead is a long-horizon one, and the rules'
relative-L1 readings at other horizons on the held-out pair say where it starts. Teacher-forced, the baselines fall
resolvably behind from h = 32 (the transformer from h = 8).
Trained autoregressively, the RSSM falls behind from h = 8, but the MLP and the transformer only from h = 100, the method's own horizon, where they trail by
0.060 [0.024, 0.096], about 12.5% of RWM's
0.4798, and 0.102 [0.034, 0.185]. Before those horizons, on the held-out pair, a baseline
cannot be told apart from RWM: at h = 1 both rules return CANNOT BE SETTLED, and at h = 8 both return
PARTIAL. Post hoc, with nRMSE pooled as §3.1 defines it, two in-sample readings differ
from the per-trajectory average the rules' evaluator used. Teacher-forced, all three baselines lead
RWM at h = 1 (M-75's reading there becomes DOES NOT REPRODUCE, from CANNOT BE SETTLED), the same
one-step lead for teacher forcing as §5's. Trained autoregressively, the MLP's deficit at
h = 100 is no longer resolved (PARTIAL, from RWM AHEAD OF ALL THREE; Appendix L).
Neither changes a verdict; both rules govern at h = 368 on relative-L1.

**Our RSSM is not an informative comparison.** Teacher-forced, it has collapsed open-loop by h = 32
(1.0182 against the floor's 0.5950), and trained autoregressively it does not
perform comparably to RWM, as the original says an RSSM does (10.6405 against
0.5856 at h = 368). A diagnostic committed before its readings existed (rule
X1, exploratory; it re-opens neither rule) returns **NOT EVALUATION-LIMITED** for its Part A, which reads
the forecast from other latents, and **NOT RESCUED BY THE SETTINGS TRIED** for its Part C, which retrains the
model. The failure may still be our RSSM rather than the architecture (Appendix L), so the
architecture claim rests on the MLP and the transformer.

**Limits.** One robot on flat ground; the original has several environments. The baselines
are our reading of a table that fixes their shapes and nothing else. Their loss, optimiser and
budget are RWM's, not tuned for them. Their sizes are Table S7's. Matched to RWM's parameter count instead (rule X4, committed before the runs; the table's last two rows), the autoregressive MLP and transformer return **PARTIAL**. At h = 368 the MLP trails RWM by 0.884 [0.204, 1.633] (RWM BETTER), and the transformer's 0.206 [-0.097, 0.740] cannot be settled (p = 0.625; CANNOT BE SETTLED), as at h = 100 and h = 32, which return PARTIAL too. Matching the parameter count is one axis; the shapes and settings stay our reading of Table S7, and the size-matched RSSM was not run. With 4 independent trajectories, the minimum detectable effect at h = 368 is
about 12.0% of RWM's error, well below every difference here.

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
the current v3), and Eq. 5 applies it as $\tilde{r} = r - \lambda u$. The per-member
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
of realised errors falling inside ±1σ. A calibrated Gaussian puts 68.27% inside ±1σ (§3.1).

On the held-out pair, the only arena on which our arms can be scored fairly (n_independent =
4 400-step trajectories), every model's aleatoric head is overconfident by between one and four orders of magnitude over the whole 368-step rollout (Figure 7; Appendix M gives the four models' table); for the released checkpoint that arena is in-sample (the in-sample caveat of §3). That is the quantity §6.1 shows the method discards.

**The quantity the method does use is also uncalibrated.** It is measured on the released 5-member checkpoint over all 10 episodes, at n_independent = **20** non-overlapping 400-step trajectories. The checkpoint trained on all ten, so restricting it to the held-out pair would buy no independence and cost four fifths of the sample; Appendix M compares that version with this one.

| h | aleatoric err/σ [95% CI] | aleatoric ±1σ | epistemic err/σ [95% CI] | epistemic ±1σ [95% CI] | epistemic ±2σ | dims r>0 | permutation P |
|---|---|---|---|---|---|---|---|
| 1 | 1,827× [915, 3,110] | 0.11% | **8.3×** [6.1, 9.7] | 16.22% [13.44, 18.89] | 30.11% | 44/45 | 0.0056 |
| **100** | 11,683× [7,970, 15,846] | 0.04% | **33.4×** [28.7, 39.0] | 4.61% [4.12, 5.09] | 9.27% | 45/45 | 0.2769 |

*The h = 1 and h = 100 rows; Appendix M gives every horizon. No permutation P in the arena survives Holm–Bonferroni, so that column is a consistency check on direction only.*

**Read the h = 1 row first.** At one step the disagreement the method penalises rewards with is
already **8.3× [6.1, 9.7]** smaller than realised error, with ±1σ
coverage of 16.22% [13.44, 18.89] against a calibrated
68.27%. The discarded per-member σ is 1,827× out at h = 1 as well.
Everything further down the table is deterioration from a starting point that is already broken.

**Why that row, and not the deep ones.** The obvious objection is that a per-step σ is a
*conditional* quantity: it says how uncertain the next state is given this input, and in an
open-loop rollout the input is the model's own previous output, wrong by an amount σ never claimed
to describe. Comparing it with *accumulated* rollout error would then make the 368-step
figure an artifact of that mismatch. (§6.5 answers a different objection, that a model trained on
8 steps cannot be expected to speak about 368.) **h = 1 answers it at no extra
cost.** At one step there is no accumulation: the input *is* the true state, and σ is asked exactly
the question it was trained to answer, and the row above is its answer: whatever compounding does at depth, it did not produce that row.

**And that row is measured on data the checkpoint trained on**: all ten episodes, 10 of 10 of them (`results/insample_framing.json`). In-sample measurement biases *toward* better calibration, so the 8.3× at h = 1 is if anything flattering: an upper bound on how well this checkpoint is calibrated. So the horizon curve is not the claim; it is the shape of the deterioration, and the claim is the h = 1 row. We keep h = 100 because it is where the method actually deploys, and h = 368 because it is the upstream's own diagnostic length.

At h = 100, the method's own imagination rollout length, epistemic is
349× better than aleatoric and still wrong by
**33.4× [28.7, 39.0]**, with ±1σ coverage of
4.61% [4.12, 5.09] where a calibrated Gaussian gives
68.27%. At one step epistemic is
220× better than aleatoric, and at h = 368 600×. **The gap between the two uncertainty terms is itself
horizon-dependent, which is why each figure above names its horizon.** At the open-loop diagnostic horizon of h = 368 it is 34.4× [29.8, 40.3] with 3.59% coverage, barely different from h = 100. **Total** uncertainty, `sqrt(aleatoric² + epistemic²)`, equals the epistemic value to four significant figures at every horizon, because the aleatoric term is too small to move it.

**A constant scale error would not matter, and this one is not constant.** The penalty enters as `r̃ = r − λu`, so a `u` uniformly `c` times too small is arithmetically identical to running with `λ/c`, and λ is tuned. Rescaling σ by the single constant that best calibrates it, fitted and scored on the same data and so an upper bound on what *any* constant achieves, needs 10.4 at h = 1 and 43.2 at h = 368, a factor of 4 across the rollout (a rule committed in advance; Appendix E). No single λ is both of those. The mechanism is §6.5's: σ grows far more slowly than error, which grows by an order of magnitude, so the ratio runs 8.3× at h = 1, 33.4× at h = 100 and 34.4× at h = 368. The penalty is applied at every step of a 100-step imagination rollout, so its *profile across the rollout* is wrong in a way no rescaling can correct: deep-rollout states are under-penalised relative to their realised risk. This bounds what the quantity reports across depth, not what the distortion costs a trained policy (the policy caveat of §11).

**Two rules committed in advance check how these numbers are read** (Appendix M). Resampling whole
episodes rather than 400-step trajectories changes no verdict in the one arena with the power to
show it, the out-of-sample cells being uninformative by design (rule M-62: **NO MOVE**). The epistemic term's one-step coverage failure is spread across the 45 state
dimensions rather than carried by a few (rule M-63: **UNIFORM**).

**The released checkpoint is no longer the only ensemble measured.** Three Arm A arms at ensemble size 5
(§6.6; out-of-sample, n_independent = 4 400-step trajectories, 2,500
training iterations) are **better calibrated than the released checkpoint and fail the same way**:
10.5× [9.0, 11.5] overconfident at h = 100 against its
25.7× on the same held-out pair, with 8.19% coverage where a calibrated
Gaussian gives 68.27%. §6.4 establishes that the two are the same architecture in the
respect that matters here, and Appendix M gives the arms' table at every horizon.

The scalar penalty as actually applied, `means.std(0).sum(-1)` at `envs/base.py:166`, correlates **+0.605** with total absolute error over the rollout, 95% CI [+0.545, +0.694] from a bootstrap over whole trajectories, n_independent = 20 (7,360 pooled trajectory-step points). The interval resamples whole trajectories, not trajectory-step pairs, which would narrow it by about the square root of the rollout length.

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

**The derivation above covers two terms, and the objective has 7.** Back-propagated
one at a time, exactly 2 reach σ (`state` and `bound`) and the other 5 give a
gradient of exactly zero (Appendix J).

**The derivation says the collapse happens on any dataset, and that is testable.** Under a rule
committed before the runs (rule M-50, Appendix E) we trained the released head, unmodified but over a
one-dimensional state with no recurrent trunk, on synthetic data whose known noise varies
25× across the input range. **Under the implemented objective σ sits 21.7× below
the true noise and does not track it at all**, while under the authors' unused likelihood branch it
recovers the true level to a median ratio of 0.9779, seed-variably. The rule returns
**OBJECTIVE-DRIVEN**, which establishes the contrast and not the size of the recovery (Appendix J).

We predicted the collapse from this algebra before training, then observed it: across all 28 runs at the released width outside §4.2's sweep the log-σ range moves linearly in iteration count, falling under sampled MSE and rising under the corrected one (Figure 4a; Appendix J lists the runs and which the rate is fitted on). Figure 2 shows the same runs through σ itself: panel (a) draws the two bounds σ can take, and panel (b) divides the change in log Δ per iteration by the learning rate, which is where the Adam optimiser's step size shows.

**Two different things are being explained here, and §6.5 separates them.** *Magnitude collapse
is objective-driven.* It occurs in all 17 sampled-MSE runs at a rate of
-9.3857e-05 per iteration with a standard deviation of 6.0e-07, **including the
teacher-forced arm**, which shares the objective, and reverses to +3.2296e-05 in the
5 runs that change it. *Input-independence is not.* It varies by a factor of
15.6 between two arms trained under the same objective, so the objective
cannot be what produces it.

Under the corrected objective the sign flips (Figure 4b), the strongest evidence that the mechanism
is the objective and not the optimiser, the data or the architecture.

**The correction fails differently rather than succeeding.** The reference contains an unused `gaussian_nll` branch. Running it reverses the collapse and
improves the magnitude from 52.2× to 10.9× overconfident. It does not produce a usable estimate, and it destroys something the faithful arm had: the σ-versus-error ordering falls from 39/45 dimensions positively correlated to 21/45, which is chance. Neither ordering survives multiplicity correction (Appendix J).

---

## S23 The earlier section 6.4

*Was the paper's section 6.4 before the rewrite for the review of 19 October; moved here whole with the rest of that section (S20 to S27). Section numbers in this passage are the earlier paper's.*

**Why the epistemic term may be miscalibrated: the members are not independent models (was §6.4)**

§6.3 explains the aleatoric column and leaves the epistemic one open. This subsection supplies a
candidate, structurally symmetric to §6.3's, from source and from the checkpoint's own tensors;
nothing here is trained and nothing is inferred from a measurement. The effect is known (§2). What
is ours is finding it in a released robotics checkpoint, with the sharing quantified at 89.15% of each member and its cost bounded by the 2.03× an independent ensemble gains on the overconfidence factor (§6.8).

**The released five-member ensemble is not five models.** The code builds one trunk, replicates only the heads,
evaluates the trunk once and hands every head the same feature vector, then takes the spread across
the heads as the epistemic term (Appendix J gives the lines).

The parameter counts make the scale of the sharing concrete. The state pathway is a
636,672-parameter two-layer GRU trunk plus five heads of
77,492 parameters each. Per member, 636,672 of
714,164 parameters — **89.15%** — are numerically identical to every
other member's. Only 10.85% differ. Across the whole released object, the two shared
trunks are 63.81% of 1,995,569 parameters.

**The sharing is stronger than the parameter count suggests.** The trunk owns a *single* recurrent
hidden state (`rnn.py:40`), and an autoregressive rollout feeds the ensemble **mean** back into it
(`system_dynamics.py:115`; `src/rwm_model.py:223` in our reimplementation). So the
five members do not roll out independently at all. There is exactly
one hidden-state trajectory between them, and disagreement at step *t* is the
spread of five two-layer MLPs read off a single 256-dimensional vector.

**Members which share a feature extractor have correlated errors by construction, and their spread
cannot express uncertainty the shared trunk does not already carry.** Where a deep ensemble varies
initialisation *and* data ordering across whole models, here only the output heads differ, so the
quantity the method penalises rewards with is a lower bound on epistemic uncertainty by
construction. It is the same shape of finding as §6.3: not a training failure, a structural one.

**This applies to our own arms identically, which is why §6.2's comparison is fair.** Our
ensemble-5 arms build, evaluate and read their trunk the same way, and their tensor names and
parameter counts match the released checkpoint's exactly on all 3 arms checked
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

Adding the teacher-forced arm, trained for §4.1, sharpens the finding (our arms at 2,500 training iterations; the released checkpoint as released). Arm B's σ is 15.6× more input-dependent than the faithful arm's, and it has the largest mean correlation of the four (r = 0.257). It is still 315× overconfident. So σ *collapsing in magnitude* is objective-driven, and σ *becoming input-independent* is not: the teacher-forced arm collapses in magnitude exactly like the autoregressive ones, same objective and same rate, while keeping that variation across inputs. Appendix K gives the four models' table, its arenas and a candidate mechanism.

**The same pattern holds for the quantity the method uses.** On the held-out pair (n_independent = 4 400-step trajectories, in-sample for the checkpoint), the epistemic term correlates positively with realised error on **45 of 45** dimensions at h = 368 while being 39.7× overconfident there, and its σ grows 1.59× from h = 1 to h = 368 while its error grows 13.33×. Under a permutation null that keeps the coupling between dimensions, nothing in this family survives Holm–Bonferroni in any of the three arenas, and out of sample at the 400-step unit nothing could, since its smallest attainable P already exceeds the smallest Holm threshold: at h = 368 the tests are underpowered at every sample size we can reach (Appendix K).

So this section's claim is: **the magnitude failure is established and large; the ordering points the right way for the epistemic term and the faithful and teacher-forced arms, not for the corrected arm or the released aleatoric head (supplementary S3), and is not established at conventional significance once the dependence between dimensions is respected. The failure is specifically magnitude calibration, in both components.**

**The structural excuse does not survive.** One could argue that a model trained on an 8-step horizon cannot be expected to report calibrated
uncertainty about step 368. It cannot report it about step 8 either. Inside the trained horizon,
σ is flat while error grows (Figure 5; out-of-sample held-out pair, n_independent = 4 400-step trajectories, in-sample for the released checkpoint; Appendix K gives all four models): the faithful arm's σ *declines* (0.9241×) while its error grows
3.49×. The coverage collapse in Figure 7(b) is therefore driven entirely by
growing error against a fixed σ.

---

## S25 The earlier section 6.6

*Was the paper's section 6.6 before the rewrite for the review of 19 October; moved here whole with the rest of that section (S20 to S27). Section numbers in this passage are the earlier paper's.*

**Ensemble disagreement beats the trivial baseline (was §6.6)**

The follow-up justifies ensemble disagreement as a trust metric on the grounds that it "closely follows the trend of the prediction error". §6.5 shows the per-dimension version of that claim is weaker than it looks. This section finds that the *scalar* the method applies tracks error well, which coexists with §6.5 without contradiction, and asks the question that matters more to a practitioner: **does disagreement beat something free?** The quantity is a usable ranking signal and is still not an interval.

Error in an autoregressive rollout grows with depth, so the trivial competitor to any trust metric is the forecast step index — a counter. It needs no ensemble, no second forward pass and no model. If a counter ranks error as well as disagreement does, the ensemble is not earning its cost. Neither paper runs this comparison, so we do. All three correlations below are on the scalar the method applies, `means.std(0).sum(-1)` at `envs/base.py:166`, against total absolute error, on the released checkpoint over all ten episodes, n_independent =
20 trajectories, with 95% intervals from a bootstrap over whole trajectories.

| h | r(step index, \|error\|) | r(disagreement, \|error\|) | partial r(disagreement, \|error\| · index) | paired difference, disagreement − index |
|---|---|---|---|---|
| **1** | — | **+0.994** [+0.918, +0.999] | — | — |
| 8 | +0.181 [+0.108, +0.349] | **+0.738** [+0.537, +0.807] | +0.757 [+0.540, +0.822] | +0.556 [+0.241, +0.679] |
| 32 | +0.174 [+0.131, +0.336] | **+0.735** [+0.577, +0.823] | +0.756 [+0.604, +0.841] | +0.561 [+0.298, +0.674] |
| **100** | +0.490 [+0.394, +0.604] | **+0.628** [+0.574, +0.839] | +0.584 [+0.516, +0.815] | +0.138 [+0.034, +0.362] |
| 128 | +0.526 [+0.421, +0.643] | **+0.671** [+0.604, +0.846] | +0.617 [+0.534, +0.812] | +0.145 [+0.011, +0.324] |
| 368 | +0.269 [+0.106, +0.431] | **+0.605** [+0.545, +0.694] | +0.596 [+0.526, +0.687] | +0.337 [+0.147, +0.544] |

*(h=1 has a single forecast step, so the index is constant and its correlation — and therefore the partial and the difference — undefined. The epistemic correlation is not, and it is the largest anywhere in this work: at one step, ensemble disagreement is very nearly a perfect ranking of realised error.)*

**Disagreement wins at every horizon tested.** Over the full h = 368 rollout the counter reaches +0.269 against disagreement's +0.605, and the index leads in 0 of 5 horizons.

**The last column is the test of whether disagreement beats the counter.** Both correlations are measured on the *same* trajectories, so the paired difference, resampling whole trajectories and recomputing *both* inside each draw, is the right test (Appendix N). It excludes zero at **5 of 5** horizons. The distinction matters at 2 of them: at h=100 and h=128 the marginal intervals *do* overlap. h=128 is where the counter is strongest (+0.526) and the margin narrowest: the paired difference there is +0.145 [+0.011, +0.324], which excludes zero only just: +0.011 is the smallest lower bound in the table, at the 400-step unit. At h = 100 the paired difference is +0.138 [+0.034, +0.362], which also excludes zero.

**The third column asks whether disagreement merely re-encodes the clock.** Partialling the step index out of both variables *lowers* disagreement's correlation by 0.010, from +0.605 to +0.596. Almost none of what disagreement knows is explained by how deep into the rollout you are: it carries real information about *this* rollout.

**What survives removing each confound** (Appendix N). Across 5 models of how far
into the rollout a step is, the weakest figure is +0.582, so disagreement is not
re-encoding the clock; but the pooled figure is in large part a between-rollout effect, so the
statistic that matters holds both the rollout and the depth constant. Pre-registered as rule M-45,
it gives +0.419 [+0.318, +0.576] at n_independent = 20 400-step trajectories, and the rule returns
**DISAGREEMENT CARRIES WITHIN-ROLLOUT INFORMATION**: disagreement still tracks error rather than merely reporting which episode is
hard.

Per horizon, the within-rollout effect is materially smaller than the pooled figure and not
established at short horizon (Appendix N gives its table).

**Does it hold on a model we trained?** Three Arm A arms at ensemble size 5 lead the index in
**12 of 12** seed-horizon cells, but under a rule committed before the
runs (rule M-43) the paired difference excludes zero at only 1 of 4
horizons. It returns **DOES NOT GENERALISE**: at n_independent = 4 400-step trajectories it was under-powered, which we measured after the fact (Appendix N). So the ranking finding is established on the released checkpoint and supported but not established on a model we trained.

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
| forecast step index *(the existing adversary)* | +0.2686 | +0.3368 | +0.5957 | — |
| `step-size` — $\lVert \mu_t - \mu_{t-1} \rVert$ | **+0.4697** | +0.1357 | +0.5430 | **no** |
| `entry-res` — one-step error before the window | +0.1471 | +0.4582 | +0.5948 | yes |

*r(disagreement, error) = +0.6053 on the released checkpoint over all ten episodes, n_independent = 20 400-step trajectories.
Minimum detectable effect, estimated before either baseline existed: 0.2891 on a margin,
0.1131 on a partial.*

**The verdict is SURVIVES entry-res ONLY, and the reason is the row a reader should look at twice.**
Disagreement beats 1 of the 2 free baselines added here. The
magnitude of the model's own predicted state change ranks realised error at +0.4697, against
+0.6053 for the five-member ensemble disagreement the method is built on. The margin between
them, +0.1357, is **below** the 0.2891 this sample size can resolve, so at
n_independent = 20 400-step trajectories we cannot say the ensemble ranks better than a
subtraction. If the observed margin is the true one, settling it needs 25 of them, an estimate under an assumed effect (§11, supplementary S2).

**On shorter units, at h = 100, the margin resolves.** The 20 whole trajectories cannot settle it at h = 368, so a rule committed before its reading (rule X6, Appendix X) put the same comparison to 70 non-overlapping units of 132 rows, the model's history plus h = 100 forecast steps, cut inside the same ten episodes, on the same checkpoint. At h = 100 the margin is +0.2816 [+0.1978, +0.3896]: the interval excludes zero, the rule's criterion, so it returns **DISAGREEMENT BEATS STEP SIZE**. Disagreement correlates +0.6808 with error there against step size's +0.3992, and keeps +0.6361 [+0.5567, +0.7466] with step size partialled out (Appendix X). The units are this checkpoint's training data, units from one episode are not independent of each other, and the interval resamples units, not episodes, so the margin at h = 100 is resolved on this checkpoint's training episodes and no further; the margin at h = 368 is not re-tested.

**Disagreement does still carry information the subtraction does not.** With `step-size`
partialled out it retains +0.5430, far above the 0.1131 MDE for that test,
and holding the forecast step exactly fixed it keeps +0.7392 against `step-size`'s
+0.5196. It is not re-encoding predicted step size. What is not established is that it adds
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
trained on the other 8, but not by the released checkpoint, which trained on all ten
(§3). **Every released-checkpoint cell in this section is therefore unseen by the multiplier
only.**

Fitting at one step works at one step and nowhere else. On the epistemic term a constant scalar
brings h = 1 coverage to 63–74% against the 68.27% target and
leaves h = 368 at 17–21%, and fitted over the whole rollout it
over-covers at one step while still falling short at the far end (Appendix T). A constant multiplier
cannot track an error that grows while σ does not (§6.5), so for a *constant* scale "right shape,
wrong scale" does not survive.

**On the released checkpoint a per-horizon scalar lands near target, and this is the one concrete remedy in this paper; on a model that has not seen the test episodes the evidence is mixed.** One multiplier per horizon is fitted on one held-out episode and evaluated on the other, in both
directions, so no multiplier is ever scored on the episode that produced it: each direction fits on
n_independent = 2 of the two episodes' 4 non-overlapping 400-step
trajectories and is scored on the other 2. On the released checkpoint every point
estimate lands within 10 points of the 68.27% target for both quantities,
**12 / 12** epistemic and **12 / 12** aleatoric cells,
against 2 of 12 for the constant scalar. **That absolute test is
UNPOWERED here:** the 10-point band is resolvable at 0 of 12
quantity-by-horizon pairs, so a cell inside the band is compatible with a true coverage well outside
it. **On Arm A at ensemble size 5, where the episodes are unseen by the model as well, its
own multipliers manage 17 of 36 epistemic and 10
of 36 aleatoric cells**. So the recipe does not carry over intact to a model that
has not seen the test episodes (Appendix T gives the table and every deviation).

**Three cautions.** The per-horizon scalar has one free parameter per horizon against the constant one's one, so it *must* fit better in sample; only cells unseen by the multiplier are evidence, and those are the cells reported. **The count is thinner than it looks:** the 12 cells are 6 horizons × two fold directions on the same 4 trajectories, each multiplier fitted on n_independent = 2 and scored on the other 2. They are not 12 independent successes and no P-value attaches to the count, which is reported so a reader can see how thin the evidence is; later sections refer back to this as the §6.7 caution, which the nine-episode fit below narrows for the released checkpoint. And the correction is a calibration patch, not a fix: it leaves σ carrying no more information than before and rescales it by how far ahead you are looking. On the released checkpoint it nevertheless brings every estimate unseen by the multiplier near what the interval claims, which is what a downstream user needs, and it costs one lookup table.

**Fitted on nine episodes and scored on the tenth (rule X7).** A rule committed before its reading (Appendix Y) repeats the design over all ten episodes: for each, the per-horizon multiplier is fitted on the other nine episodes' trajectories with the same fitting function and scored on its own. Each of the 20 trajectories is thus scored once, by a multiplier not fitted on it, and each horizon's coverage carries a 95% interval. On the epistemic term every one of those intervals lies inside the 10-point band, all of them between 61.2% and 74.9%: **WITHIN BAND AT 6 OF 6 HORIZONS**. Appendix Y gives the aleatoric term and the constant multiplier alongside. Those trajectories are unseen by the multiplier, not by the model, which trained on all ten episodes, so for the released checkpoint each horizon's coverage is now resolved within the band, though the six horizons share those trajectories and are not independent tests; the Arm A result stands as it is.

**The multipliers are a property of the model, not of the horizon.** Fitted on Arm A and scored on
the released checkpoint, and the reverse, on the same 4 held-out trajectories, rule M-69 returns **DOES NOT TRANSFER — A PROPERTY OF THE MODEL** on the paired change in coverage the arena can resolve: 52 of 72 governing cells, which are not independent tests, have an interval wholly outside the ±10-point band, and Arm A's multipliers are 0.0069× to 1.36× the
released checkpoint's at the same horizon (Appendix T).

So the accurate form of this section is: **a constant scalar does not repair the interval; on the released checkpoint a per-horizon one brings every estimate unseen by the multiplier within the band, though no single cell is resolvable at this arena, and does so across episodes but not across models. On episodes unseen by the model as well, Arm A's own multipliers manage 17 of 36 epistemic cells, so there the evidence is mixed.** Fitted on nine episodes and scored on the tenth, the released checkpoint's epistemic coverage over all 20 trajectories is within the band at every horizon.

---

## S27 The earlier section 6.8

*Was the paper's section 6.8 before the rewrite for the review of 19 October; moved here whole with the rest of that section (S20 to S27). Section numbers in this passage are the earlier paper's.*

**Testing the mechanism: an ensemble that shares nothing, alone and with the corrected objective (was §6.8)**

§6.4 establishes the topology as a fact and the mechanism as a hypothesis. Two rules committed to git
before any of their artifacts existed test it, each with a minimum detectable effect estimated in
advance (Appendix E). The first scores 5 independently initialised full models, Arm A at
ensemble size 1 trained at 5 seeds, together as an ensemble at evaluation time. Each member keeps its own recurrent hidden state and the ensemble mean is fed back to all of them, so the
rollout differs from the shared-trunk one only in what is under test. The second repeats it with every member trained under `gaussian_nll`, so the two fixes are measured on the same models. Both are scored
on the held-out pair, n_independent = 4 400-step trajectories, every model at 2,500
training iterations, against each of the shared-trunk seeds separately (Appendices O and P give the tables).

**Rule M-44 returns MECHANISM SUPPORTED.** All 6 of its 6
conditions hold against every one of the 3 shared-trunk seeds: at h = 100
the overconfidence factor improves **2.03×** against a minimum detectable effect of
1.45×, coverage rises a mean of +7.12 points against 2.26, and every
paired interval excludes zero. σ itself grows 1.65× there, **71%**
of the improvement, so the trunk-sharing mechanism is the larger part of the effect where the method operates. At h = 368, 57% is the ensemble simply predicting better
(Appendix O).

**Rule M-68 returns THE COMBINATION IMPROVES CALIBRATION**, branch 2 of the four it names: all
5 of its 5 conditions hold, a **1.94×**
improvement against a minimum detectable effect of 1.218×. That is essentially what
independence gave alone. Against the independent arm, which differs in the loss and nothing else,
switching to `gaussian_nll` multiplies the overconfidence factor by 1.044×
[1.029, 1.054], slightly the wrong way and below what the design can resolve (Appendix P).
**The two fixes do not add**: the objective's separate contribution is at most small, which the
design can bound but not establish as zero. Once stated that is no surprise: the objective governs
the aleatoric head, and the epistemic term is a spread across members the loss never sees.

**What the arms bound, and what they do not repair.** Independently seeded runs differ in data
ordering as well as initialisation, and the independent members carry 3.49× the
shared-trunk arms' state-pathway parameters, so these comparisons bound the architectural effect rather than isolating it. At matched capacity the improvement falls to 1.79× against a minimum detectable effect
of 2.00×, so that rule returns **UNDER-POWERED — favours the matched ensemble by less than the MDE** (rule M-49, supplementary S2). Neither arm is an interval: at h = 100 the independent ensemble is
5.2× overconfident with 15.31% coverage and the combined arm
5.4× with 15.53%, where a calibrated Gaussian gives
68.27%. §6.7's per-horizon multiplier remains the only correction in this paper whose
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
identically zero, so it marks all 9,961 windows valid.

**7.2 Training and evaluation disagree on action alignment, and evaluation is the broken one.**
Row *t* holds the action that *produced* state *t*. The data say so directly: at every reset row
all twelve actions are exactly zero (§3), and a policy network with biases cannot emit exact zeros,
so those zeros mark the absence of a producing action — the reset produced that state, not a policy step. They are what Isaac Lab, in which the data were recorded, writes at a reset: `ActionManager.reset()` sets its stored actions to zero (`action_manager.py:350-365` in Isaac Lab). The training path pairs states and actions index-for-index, which is causally correct; the
evaluation path feeds the action from *t−1* to predict state *t*, stale by one step.

What the stale pairing costs depends on the horizon. All ten episodes are this checkpoint's training data, so the held-out pair is not more honest here, only smaller, and the larger arena leads. Over all ten episodes' 20 independent trajectories the stale action raises the released checkpoint's relative-L1 error by 55.0% [26.3, 92.7] at h = 1, 54.4% [37.5, 82.3] at h = 8 and 37.4% [21.3, 65.4] at h = 32. From h = 100 the change is not resolved: 8.2% [-10.4, 24.9] there and -4.6% [-13.4, 3.2] at h = 368, where single trajectories run from -47.4% to +35.2%. In nRMSE the rise is resolved at h = 8 and 32 (31.5% [24.7, 68.2] and 17.4% [7.7, 47.4]) but not at h = 1 (7.4% [-14.8, 87.8]), and from h = 100 it is not resolved either (7.9% [-18.9, 32.9] there, -2.1% [-10.0, 3.9] at h = 368). Each is a 95% interval from a cluster bootstrap over whole trajectories, both pairings inside each draw (`results/alignment_by_horizon.json`, `results/alignment_defect_ci.json`).

On the held-out pair's 4 independent trajectories the stale action raises the error at every horizon reported: by 34.2% [10.6, 75.0] at h = 1 and by 22.5% [6.3, 41.7] at h = 100, where all ten episodes resolve no change. At h = 368 it raises it by 7.9% [3.1, 13.0] on relative-L1 and 6.6% [1.0, 8.0] in nRMSE (Appendix V gives the per-trajectory values). Shifting the evaluation loop's two action slices by one step (`model_training.py:129` and `:132`) aligns it with training; our harness does this with `action_offset = 1` (`src/score_reference.py:180-190`). 

For models trained under the causal pairing, the stale one also raises error, and how much depends on the arena (three-seed means, computed post hoc; Appendix V gives every model at every horizon, each with its interval). A percentage change depends on how accurate the model already is as much as on how much the action matters. Measured as the shift in the forecast itself on their own training data, our 10,000-iteration Arm A and the released checkpoint move about equally at h = 8, and at h = 100 the released checkpoint's forecast moves more (Appendix V).

Our models do use the action. Given another trajectory's actions, their error at h = 8 on their own training episodes' 16 trajectories rises by +676.3% [+454.8, +1060.0] at 10,000 iterations, and at 2,500 iterations by +227.8% [+131.6, +398.2], so rule X2, committed before its readings existed, returns **RESPONDS TO THE ACTION** at both checkpoints (Appendix V). That shows the forecasts depend on the action, not that they predict a different action's consequences correctly: every action in the data comes from one policy. 

Rule X8 re-scores four of our rules with the released evaluation's timing, on the held-out pair's 4 trajectories, through each rule's own evaluator (the configuration and baseline rules at 2,500 iterations, the A/B comparison at 10,000), and all four keep their verdicts, **SAME VERDICT**, though 22 of their alongside readings change (Appendix Z); this concerns our models, not the original's printed numbers.

**7.3 No held-out evaluation.** Evaluation trajectories are drawn from training data. For the
released checkpoint, trained on the entire file, no held-out measurement is possible at all, and neither pinned repository can generate the data that would make one possible (§3).

**7.4 What the spliced windows cost: nothing measurable in rollout.** A contaminated arm trained with
195 spliced windows added, at 2.47% contamination (below the pipeline's
3.53%, by design, so that no held-out row leaks), raises training loss by
21.57% where a duplication control adding the same number of exact copies raises it by
0.90%. In rollout, over 32 cells (the held-out pair and the training episodes, 200 and 400-step trajectories, the 500 and 2,500-iteration checkpoints, n_independent 4 to 39), it is hurt in 0 and helped
in 9 (Figure 8a), the signature of regularisation. At this rate the splices do
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

Seven things a practitioner can apply without reading the rest of this paper.

**Use ensemble disagreement as a ranking signal, but price it against the free alternatives first. Do not read it as a distance. And expect it to degrade with horizon.** On the released checkpoint's own training episodes, at one forecast step it ranks whole rollouts almost perfectly, +0.994 [+0.918, +0.999] across the 20 trajectories, a ranking of *rollouts* rather than of moments within one, because at h=1 there is only one moment. Over the full rollout it falls to +0.605 [+0.545, +0.694]: excellent where you can check it cheaply and merely good where you most need it. It beats the forecast step index at every horizon we tested, on a paired test that excludes zero at 5 of the 5 horizons where the index is defined, and retains +0.596 once that index is partialled out (§5.6). **On whole trajectories, what it does not clearly beat is the model's own predicted step size**, which costs nothing and needs no ensemble: over the 20 400-step trajectories that ranks error at +0.4697 against disagreement's +0.6053, a margin of +0.1357, below the 0.2891 that sample can resolve. On 70 shorter units of the same episodes a later rule resolves the margin at h = 100, +0.2816 [+0.1978, +0.3896] (rule X6, §5.6), on the checkpoint's training data only; the margin at h = 368 is not re-tested. Disagreement carries information the subtraction does not, retaining +0.5430 once step size is partialled out, and with both the forecast depth and the rollout held constant it still correlates +0.419 [+0.318, +0.576] with error (§5.6); but a practitioner about to pay for five members should price the subtraction first. And it is too small to be an interval by a wide margin: at h = 100, the horizon the method rolls out over, 33.4× [28.7, 39.0] on the released checkpoint over all ten episodes, and on the held-out pair 10.5× [9.0, 11.5] on the ensemble-5 arms we trained, against the released checkpoint's 25.7× there. A risk gate or safety margin that reads σ as a distance is not supported at any horizon, on either.

**If you need the interval, rescale per horizon, not globally, and refit on your own model.** One multiplier per forecast horizon, fitted on one episode and scored on another, brings every released-checkpoint coverage estimate within 10 points of nominal, though this arena cannot resolve any single cell to that band. Fitted on nine episodes and scored on the tenth, the epistemic coverage over all 20 trajectories lies within it at every horizon (rule X7, §5.7). A single global multiplier manages 2 of the 12 epistemic ones (§5.7). That checkpoint trained on both episodes; on Arm A, whose model never saw them, its own multipliers manage 17 of 36 epistemic cells. The cells are not independent trials (the §5.7 caution), so read the sweep as consistency and the per-cell deviations as the evidence. The fitted epistemic multipliers span 9.31× across horizons, which is precisely why one number cannot serve.

**Do not convert per-dimension sign counts into P-values.** State dimensions in a robot are physically coupled and share a forecast-depth trend, so an independent-trials null is badly wrong, in our tables by up to 10^13× (§5.6, Appendix K). Permute whole trajectories instead. An earlier draft of this paper used the binomial version, and it made our weakest evidence look like our strongest.

**Count independent trajectories, not trajectories.** Two 400-step windows that overlap at all
are one piece of evidence, not two. The held-out arena here contains 4 independent
400-step trajectories however many windows are drawn from it, and that number bounds every
long-horizon magnitude (§3), though §4.1's direction is re-tested on all ten episodes, each held out once on fixed folds (rule X3: **REPLICATES ACROSS FOLDS**, 20 trajectories at 2,500 iterations, not 10,000). Reporting an interval beside a trajectory count rather than an
independent-trajectory count overstates precision. Resampling pooled seed × trajectory values instead of trajectories narrows
intervals by a further 1.42× (§3.4).

**Anchor a decision rule to the horizon the claim is about.** Our first pre-registered rule was
anchored at h = 8, the training forecast horizon, and returned **CANNOT BE SETTLED AT THIS BUDGET**; the claim was
about deployment horizons. The rule was correct in form and pointed at the wrong regime, a failure
mode pre-registration does not protect against on its own.

**Check that the implemented loss is the described loss before reproducing any number from it.**
The paper describes two loss terms; the implementation has 7. The predicted variance has an optimum at zero under the implemented one, which is why the released checkpoint's σ is 11,683× smaller than its own error at h = 100, and 20,669× at h = 368. Reading the loss took an afternoon and explained a
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
sample-efficiency comparison included, and nothing here uses a GPU. Our arms use 0.133% of the
reference's world-model data (§3.2). And the released checkpoint trained on all ten episodes, so it
has no held-out arena, and neither pinned repository can generate the data that would give it one
(supplementary S1). None of this can be lifted on CPU, and nothing in this paper claims otherwise.

**Effective sample size bounds the long-horizon magnitudes.** The headline magnitudes rest on the held-out pair, 4 independent 400-step trajectories (the n = 4 caveat of §3); the direction is re-tested on all ten episodes, each out of sample once on fixed folds (rule X3: **REPLICATES ACROSS FOLDS**, 20 trajectories at 2,500 iterations, not 10,000; §4.1). A larger dataset cannot be generated here (supplementary S1), so the released checkpoint's lack of a held-out arena is a constraint, not a choice.

**On whole trajectories, the ranking claim is not established as needing an ensemble.** The model's
own predicted step size ranks error nearly as well, by a margin those 20 trajectories cannot
resolve at h = 368; if the observed margin is the true one, settling it needs 25
independent 400-step trajectories, a required-sample-size estimate under an assumed effect (supplementary S2).
On 70 shorter units cut inside the same episodes, which are the checkpoint's training data,
a rule committed before its reading finds disagreement ahead at h = 100, +0.2816
[+0.1978, +0.3896] (rule X6: **DISAGREEMENT BEATS STEP SIZE**; §5.6, Appendix X); the margin at h = 368 is not re-tested.

**We did not measure what the miscalibration costs.** The penalty the follow-up applies is
33.4× overconfident at h = 100, the horizon its own imagination
rollouts run to, but its only use is to shape policy learning, and a test of that cost needing no policy, rule X5, could not be run, because the released data do not record the velocity command its reward terms score against (Appendix W). **The finding bounds what the quantity reports, not what it
costs**, and the ratio is not a measure of harm. Other sections refer back to this as the policy
caveat of §11. A proxy that needs no policy, the ordering of the penalty accumulated along whole
rollouts before and after the per-horizon correction, finds none of the 6 pairs among the held-out pair's 4 trajectories reordered (in-sample for the checkpoint; rule M-70: **DOES NOT REORDER**). That proxy orders the penalty alone, though, not the penalised return, its null is partly structural, and its interval is degenerate (supplementary S2).

**No family-wide correction is applied across our own pre-registered rules.** There are
35 of them (Appendix E), each reported, once its data exist, against the thresholds it was committed with (one is withdrawn as a
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
ahead at h = 368 of the baselines we built to our reading of it and trained with its settings, though there none of them beats predicting no change. Matched to RWM's parameter count, size being one axis, the transformer cannot be told apart from it (rule X4: PARTIAL). On accuracy alone, four other history and forecast lengths beat its chosen ones at our budget, no reading the rule reports putting the chosen ones ahead of any of them, in a ranking that changes when the chosen setting trains longer; it chose them as a trade-off with training time (§4.2, §4.3). Neither
uncertainty output of the follow-up that adds them reports what a reader would take it to report.
At h = 100, the horizon the method's own imagination rollouts run to, the aleatoric σ is 11,683× smaller than its own error, because the objective's optimum is σ = 0 and the term that should prevent this cancels out of the gradient. The epistemic term the method actually penalises with is better by a factor of 349 and still 33.4× [28.7, 39.0] overconfident, both figures at h = 100 on the 20 trajectories of the checkpoint's own training episodes.

The ranking use the follow-up claims survives a real test. On the released checkpoint, ensemble disagreement beats the forecast step index at every horizon and, with both the rollout and the depth held constant, still correlates
+0.419 [+0.318, +0.576] with realised error (§5.6). A free subtraction, though, the model's own
predicted step size, ranks error nearly as well, +0.470 against disagreement's +0.605, by a margin 20 whole trajectories cannot resolve at h = 368
(SURVIVES entry-res ONLY: disagreement beats the one-step error before the window, but not the model's predicted step size); on 70 shorter units of the same episodes, at h = 100, disagreement is ahead (rule X6, +0.2816 [+0.1978, +0.3896]). The scale may be repairable per
horizon on the released checkpoint, where, fitted on nine episodes and scored on the tenth, the epistemic coverage over all 20 trajectories is within the band at every horizon (rule X7: **WITHIN BAND AT 6 OF 6 HORIZONS**), but on a model that never saw the test episodes the evidence is
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

**§5.5's term-by-term summary.** **The derivation above covers two terms, and the objective has 7.** Each term,
back-propagated alone on one real batch, confirms it: 4 are live under the released
configuration, exactly 2 reach σ (`state` and `bound`), and the other 5 give a
gradient of exactly zero (`results/e4_sigma_gradients.json`, Appendix J).

**§5.5's run-count summary.** We predicted the collapse from this algebra before training, then observed it: across all 28 runs at the released width outside §4.2's sweep the log-σ range moves linearly in iteration count at a nearly identical rate within each objective, falling under sampled MSE and rising under the corrected one (Figure 7a). Appendix J lists the runs, the capacity-matched arm excluded from
every rate, and the 22 the rate is fitted on.
