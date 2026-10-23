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

**No family-wide correction is applied across our own pre-registered rules.** There are 28 of them (Appendix E), each reported, once its data exist, against the thresholds it was committed with. Pre-registration is what licenses that: each rule is a separate question committed before its data, not one search over many outcomes, and a rule that fails is reported as failing. A reader who prefers a corrected family threshold can apply it from that count.

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
introduced it onward, so **37 of the 39 commits Figure 3 cites keep their identifiers and two do not**: the two made between that file's introduction and the purge. Timestamps, content and ordering are unchanged; only the hashes moved, and for that reason Figure 3 finds its first rules' commits by subject and the later ones by the commit that introduced their ledger heading, never by a stored hash alone. The transcript itself reaches reviewers in the anonymised
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
training) rewrites 0.73% of the numeric values under `results/` that the comparison counts; the rest are carried in
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

**Pre-registration, and one failure of it.** Decision rules were committed to git before the data that tested them, with one exception. Figure 3 and Appendix E give the lead time for each of the 28 whose data exist; 27 are positive and 1 is not. Every positive bar is a difference of two commit timestamps. **The negative one is not**: it is the duplication-control rule (§7.4), whose *data* side is the moment the control runs finished, a line in `results/control_driver.log` rather than a commit, dated from the commit that introduced that line. The rule was stated in conversation before the runs and reached git **2.9 hours after they finished**, and we found it only by auditing our own `git log`. The measurement stands, because the arm was built without reference to its outcome, but the claim that it was pre-registered does not, and it is withdrawn. A discipline that is only checked when it succeeds is not a discipline.

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
