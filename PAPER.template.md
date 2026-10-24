# Right Ranking, Wrong Scale: Reproducing the Robotic World Model's Dynamics Model and Testing the Uncertainty of Its Follow-up

---

## Abstract

We reimplement the dynamics model of the Robotic World Model (RWM) and test the uncertainty its follow-up, RWM-U, uses as a reward penalty in offline policy optimisation. Our rebuild matches the release's gradients. RWM's claim that training on its own rollouts, not one-step targets, lowers long-horizon error holds on held-out data: holding each of ten episodes out once, at the original's training length, it wins on every one at the pre-registered horizon; on short windows at one step it loses. RWM-U's ensemble disagreement ranks errors right but sizes them wrong: it ranks them better than the forecast step (Spearman {{n11_d2_sp_epi_h100|s2}} at a hundred steps), yet in every ensemble measured, error exceeds what the spread implies even at one step. The release feeds every member the ensemble mean, so spread does not track accumulated error: at {{v2_deploy_h}} steps on the released checkpoint one-sigma coverage is {{x9_rel_mean_cov1_h100|s2}}% against {{v3_cov_nominal1|s2}}%, and rolling each member on its own predictions raises it to {{x9_rel_per_cov1_h100|s2}}%. Each member's variance collapses: the implemented loss, squared error on a sampled prediction, is minimised at zero. Rescaling the released checkpoint's spread per horizon (fitted on nine episodes, scored on the tenth) restores one-sigma coverage, not two-sigma. We fix two pipeline defects. One robot, gait and dataset; no policy is trained.

---

## 1. Introduction

Offline model-based reinforcement learning trains a robot's policy inside a learned simulator. The Robotic World Model (RWM; Li, Krause and Hutter) learns such a simulator for a quadruped from recorded robot data, and its follow-up, RWM-U, adds an ensemble of predictors whose disagreement penalises the reward, in the manner of MOPO (Yu et al., 2020). A policy can be trusted inside the simulator only as far as the simulator's errors are known, so the penalty has two jobs: to rank where the model is more likely to be wrong, and to say by how much. We test whether it does either, on the released code and checkpoint and on models we rebuilt from the papers' descriptions.

**What we found, in plain words.** The rebuild matches the release's gradients before any training, so later differences belong to the method and not to our wiring (§3.1). RWM's central claim, that training on the model's own rollouts lowers long-horizon error more than training on one-step targets (teacher forcing), holds on episodes the models never saw: with each of ten episodes held out once, rollout training wins on every episode at the pre-registered horizon, and on short windows at one step it loses (§4.1, Figure 1a). The other two claims we tested get only weak tests (§4.2, §4.3).

RWM-U's ensemble disagreement ranks errors correctly and sizes them wrongly, in three separate ways. Even at one step, every ensemble's error exceeds what its spread implies (§5.2). The five members share one trunk, so they can disagree only about what that trunk carries (§5.3). And the release feeds every member the ensemble mean, so the spread does not grow with the horizon as the error does; rolling each member on its own predictions, which is not the released method, partly repairs this (§5.4, Figure 1b). Separately, the per-member variance the method discards collapses because the implemented loss is minimised at zero (§5.5). The spread ranks error better than the forecast step does (§5.6), and rescaling it per horizon restores one-sigma coverage, though not two-sigma, on the released checkpoint; on episodes a model never saw the evidence is mixed (§5.7). We also fix two defects in the released pipeline (§6). Everything is measured on one robot, one gait and one dataset, and no policy is trained, so what the miscalibration costs a policy is not tested (§7).

Figure 1 shows one finding about each original paper. Panel (a) is the base paper's claim that training on rollouts beats teacher forcing, measured on episodes the models never saw: the gap at h = {{v2_diag_h}}, one interval per fold and one point per held-out episode. Panel (b) asks whether the follow-up's spread grows with the horizon as the error does, under the released rollout and under a per-member rollout that is not the released method.

**Contributions.**

- **RWM's claims, tested.** Holding each of the ten episodes out once, rollout training beats teacher forcing at {{v2_diag_h}} steps on every episode and loses at one step on short windows (§4.1). The other two claims get weak tests (§4.2 and §4.3); two pipeline defects get fixes (§6).
- **Three gaps between RWM-U's spread and its error.** Even at one step every ensemble's error exceeds its spread; members sharing one trunk can disagree only about what that trunk carries; feeding them the ensemble mean stops the spread accumulating, which per-member rollout partly repairs (§5.2 to §5.4).
- **Why the discarded per-member variance collapses.** The implemented loss is squared error on a sampled prediction, not the Gaussian likelihood, so its optimum is σ = 0: derived, shown against known synthetic noise, and approached at an ordinary Adam step per iteration (§5.5).
- **What the spread is still good for.** It ranks error better than the forecast step (Spearman). It is also ahead of the model's step size on shorter units at the method's horizon, by a pre-registered rule, and under exploratory ranks on whole trajectories, where the pre-registered linear test could not resolve the margin (§5.6). On the released checkpoint, per-horizon rescaling fixes one-sigma coverage, not the tails; on episodes a model never saw the evidence is mixed (§5.7).

§2 places the work; §3 covers the data, metrics and statistics; §4 and §5 test the two papers; §6 describes the pipeline defects; §7 gives lessons and limitations; §8 concludes and states what reproduces.

---

## 2. Background and related work

**RWM and RWM-U.** RWM (Li, Krause and Hutter) trains a recurrent dynamics model on a quadruped's proprioceptive data and uses it as a simulator for policy learning. RWM-U's ensemble of five predictors shares one state trunk, as its authors state, and penalises the reward by the members' disagreement. The penalty follows MOPO (Yu et al., 2020), which penalises the reward by an ensemble uncertainty estimate, and MOReL (Kidambi et al., 2020), which detects unknown states by pairwise ensemble disagreement; both branch short rollouts from real states, as MBPO does (Janner et al., 2019). As we read MOPO, the penalty is meant to bound the model's one-step error at the states the policy visits. That is the use against which §5.2 measures the spread.

**Multi-step training.** Training a dynamics model on its own multi-step predictions rather than on one-step targets is an established remedy for compounding error; Venkatraman et al. (2015), Bengio et al. (2015) for sequences, Talvitie (2017) and Lambert et al. (2021) are examples. That sets the prior for §4: a long-horizon advantage for rollout training is what these methods aim at, so the direction of RWM's claim is expected, and the test is whether it holds on held-out episodes of this dataset and what happens at one step.

**Ensembles that share a trunk.** Deep ensembles are trained from different initialisations and data orderings (Lakshminarayanan et al., 2017). Reinforcement-learning ensembles with a shared torso include Bootstrapped DQN (Osband et al., 2016) and randomised prior functions (Osband et al., 2018). That heads sharing a trunk under-report disagreement is established (Lee et al. (2015), Fort, Hu and Lakshminarayanan (2019), Wen et al. (2020) and Havasi et al. (2021)). RWM-U documents its shared trunk; §5.3 asks what the sharing costs.

**Calibration, recalibration and conformal prediction.** Lu et al. (2022) compare uncertainty heuristics for offline model-based reinforcement learning under a protocol built "to capture the specific covariate shift induced by model-based RL", and report rank and bivariate correlation with true model error separately. That is our distinction between ranking and scale, on the same family of penalties, and the closest precedent. We add coverage measurements on a released checkpoint. Kuleshov et al. (2018) recalibrate regression uncertainty, and Malik et al. (2019) do so for a dynamics model inside model-based reinforcement learning, arguing that "good uncertainties must be calibrated". Our per-horizon rescaling (§5.7) fits a scale on some held-out data and scores it on other held-out data, which resembles split conformal prediction (Angelopoulos and Bates (2021), Stankevičiūtė et al. (2021), Lindemann et al. (2023)); we make no claim of the conformal guarantee.

**Evaluation statistics.** Henderson et al. (2018) and Agarwal et al. (2021) are the reference points for reporting reinforcement-learning results from few runs. Our intervals rest on few seeds and few trajectories, so §3.4 reports the count beside every interval.

**The PETS lineage.** The bounded log-σ head is inherited from PETS (Chua et al., 2018); Appendix J asks which public descendants inherit its objective as well. Seitzer et al. (2022) show failure modes of σ heads trained by maximising likelihood; the released state loss is not a likelihood at all (§5.5).

---

## 3. Setup

### 3.1 The reimplementation

We rebuilt the dynamics model from the papers' descriptions and the released module: a recurrent (GRU) ensemble whose members predict the next proprioceptive state with a mean head and a bounded log-σ head, plus auxiliary heads for contact and termination. The paper describes two loss terms; the implementation has {{diff_terms}}. Before any training, our outputs match the released module's bitwise, and our losses and gradients match exactly (a maximum difference of {{diff_grad_max}}) across those {{diff_terms}} terms and {{diff_n_params}} parameter tensors (Appendix A). A later discrepancy therefore belongs to the method or the data, not to our wiring.

### 3.2 Data, arenas and independent units

The released dataset is {{rows}} rows of ANYmal D proprioceptive state and policy actions at 50 Hz, {{c2_pct|s2}}% of the data budget the reference trains on: ten concatenated 20-second episodes of {{ep_rest_rows}} rows (the first has {{ep0_rows}}), with a termination column that is identically zero. We recover the episode boundaries from the rows at which every joint velocity and action is zero (supplement S16). Table 1 lists the arenas we measure on, each with its count of mutually non-overlapping 400-step trajectories, which is the sample size.

| Arena | Episodes | Independent 400-step trajectories | Used for |
|---|---|---|---|
| Held-out pair | the two episodes withheld when training our models | {{m23_nind}} | our models' out-of-sample claims |
| Training episodes | the other eight | {{x10_n_in}} | our models' in-sample readings |
| All ten episodes | the whole release | {{e7_nind}} | the released checkpoint |
| Fold held-out pairs | five folds, each holding out two episodes, each episode once | {{x3_n}} ({{m23_nind}} per fold) | the fold replication and the fold ensembles |

*Table 1: the arenas; our models are the {{iters_main}}-iteration arms. The held-out pair's {{m23_nind}} trajectories come from two episodes.*

Two 400-step trajectories whose spans overlap are not independent evidence, so we count only non-overlapping ones, report the count beside every interval, and resample whole trajectories (§3.4). A bootstrap over {{m23_nind}} trajectories has {{c3_resamples}} distinct resamples, so its intervals are coarse, and that count bounds every long-horizon claim about the held-out pair.

**The released checkpoint's training data is not recorded.** No file in either released repository records which rows trained the released checkpoint, and the checkpoint stores no data statistic, hash or path (its tagged iteration is {{n12_ckpt_iter}}). Its one-step error is the same on the eight episodes our own model trained on and the two it did not ({{n12_rel_l1_h1_released_on_train|s2}} against {{n12_rel_l1_h1_released_on_heldout|s2}}), where our model's differs ({{n12_rel_l1_h1_armA_in|s2}} against {{n12_rel_l1_h1_armA_out|s2}}). That is consistent with its having trained on all ten episodes, on some, or on none, and the data cannot tell which. We therefore call its arena its ten released episodes and never call it held out. Everything here ran on two CPU cores (Appendix B).

### 3.3 Metrics and floors

**Relative-L1** is the reference's own metric, which keeps our numbers comparable to the upstream's printed ones: at each forecast step, the summed absolute error over the state dimensions divided by the summed absolute true state, on normalised states, averaged over trajectories and over the steps after the first {{v2_history}}, which are teacher-forced. Its denominator can pass through zero, so we also report **normalised RMSE (nRMSE)**: the root of the squared error pooled over the state dimensions, divided by the dimensions' mean standard deviation over the training episodes. A value of one is not the training-mean floor, because that predictor scores the root-mean-square of the dimensions' standard deviations over their mean, which is at least one; we report three floors: predicting the training mean, holding the last state, and repeating a seasonal pattern (§4.3; Appendix F defines them).

**Coverage at ±kσ** is the fraction of (trajectory, step, dimension) triples whose absolute error is within k times the predicted σ; a calibrated Gaussian gives {{v3_cov_nominal1|s2}}% at ±1σ and {{v3_cov_nominal2|s2}}% at ±2σ. **The error-to-spread ratio** $\rho$ is the mean absolute error over the mean predicted σ; a calibrated Gaussian has $\rho$ = {{m65_calib_ratio|s2}}, so a ratio of one is not calibration, and we report $\rho$ beside that value. **"Too small by k"** means one thing: the factor k on σ that restores nominal ±1σ coverage. **Ranking statements** use Spearman's rank correlation, because a ranking claim is about order and a rank statistic does not depend on scale or on a linear relation; a rule committed with Pearson's correlation keeps it, and we say so (Appendix L gives Kendall's).

Curves are reported at horizons h = 1, 8, 32, {{v2_deploy_h}}, 128 and {{v2_diag_h}}, each cumulative from the first forecast step to h. **h = {{v2_deploy_h}}** is the method's own imagination rollout length. **h = {{v2_diag_h}}** is the upstream's open-loop diagnostic length, {{v2_len_eval}} minus the {{v2_history}}-step prefix, {{v2_ratio|s2}}× longer than the method's rollout and not a deployment horizon.

### 3.4 Statistical protocol, pre-registration and deviations

Intervals are 95% intervals from a cluster bootstrap over whole trajectories, the unit of dependence, as in the literature on inference with few clusters (Cameron et al., 2008); resampling seed × trajectory narrows every interval, as an earlier analysis of ours did before we corrected it (supplement S17). Comparisons at four trajectories use exact sign-flip tests. Their smallest attainable two-sided p is {{n7_p_min_n4_frac}}, above every Holm level we use, so no comparison at that size can be called resolved; each is reported with its exact p and as "k of the four". Multiplicity is controlled with Holm's procedure within each pre-registered family, and not across rules. Per-dimension evidence uses permutation nulls that keep the 45 state dimensions together, because they are not independent.

Decision rules were committed to git before the data that tested them, with timestamps a reader can check; Appendix E gives each rule, its lead time and its verdict verbatim. Pre-registration in machine learning has workshops of its own (Bertinetto et al. (2021), Albanie et al. (2022)); we commit each rule before its data so that the analysis cannot follow the result. One rule failed the discipline: the rule for the control that adds exact copies of windows reached git {{lead_task3}} after its runs finished, so we withdrew its claim to have been pre-registered. Several verdicts went against the original or could not settle the question, and we report each. The ledger keeps {{n_superseded}} superseded entries: {{n_retractions_lower}} claims withdrawn on evidence, {{n_retract_framing_word}} framings withdrawn, and the rest early hypotheses closed as housekeeping. Analyses written after the data are labelled post hoc and never change a verdict. Where our setup departs from the original's or from a rule, Appendix O and Appendix E say how.

---

## 4. The base paper's claims

### 4.1 Training on rollouts against teacher forcing

RWM's central claim is that training the dynamics model on its own autoregressive rollouts beats training it on one-step targets (teacher forcing) at long forecast horizons. §2 gives the prior: a long-horizon advantage is what multi-step training aims at, so the question is whether it holds on episodes the models never saw, and what happens at one step.

**Every episode held out once.** We trained both arms on five folds, fixed in advance, each holding out two episodes so that each of the ten episodes is held out exactly once ({{iters_main}} iterations, three seeds per arm per fold). Over the {{x3_n}} independent out-of-sample trajectories of all ten episodes, teacher forcing's relative-L1 error at h = {{v2_diag_h}} exceeds rollout training's by {{x3_gap|s2}} {{x3_ci|s2}}, a factor of {{x3_ratio_h368|s2}}: the direction replicates across folds. All {{x3_eps_pos}} of the {{x3_n_eps}} episodes favour rollout training (two-sided sign-flip test over the episodes, p = {{n7_x3_ep_p_h368|s1}}), and each fold's own gap, from {{x3_fold_lo|s2}} to {{x3_fold_hi|s2}}, is positive on each of its four trajectories (descriptive at four; Figure 1a). That test treats the ten episodes as exchangeable, although the models of different folds share most of their training episodes, so it is a statement about these ten episodes and this dataset, at its scale (§3.2). On the held-out pair the teacher-forced arm is worse than the training-mean floor at this horizon (nRMSE {{h2h_armB_nrmse_h368|s2}} against {{n10_mean_nrmse_heldout_h368|s2}}) and the rollout-trained arm is better ({{h2h_armA_nrmse_h368|s2}}), so the factor compares a model that works with one that drifts beyond the floors (Appendix F).

**At one step the order reverses, on short windows.** On {{x3_h1_n}} non-overlapping {{x3_h1_unit}}-row units, the same arms differ by {{x3_h1_gap|s2}} {{x3_h1_ci|s2}} at h = 1, in favour of teacher forcing, which is unsurprising because it trains on exactly that target. At the episode level the sign agrees on only {{n7_x3_ep_k_h1}} of ten episodes (sign-flip p = {{n7_x3_ep_p_h1|s2}}), so the reversal is a short-window result and is not resolved episode by episode. A rule committed before its runs, on the held-out pair's {{m64_h1_n}} independent {{m64_h1_unit}}-row units, finds the same sign, {{m64_h1_gap|s2}} {{m64_h1_ci|s2}} (Appendix G).

**Supporting evidence from longer training.** On the held-out pair, {{a1_nind}} trajectories from two episodes, three seeds trained for {{iters_long}} iterations give a factor of {{d1_ratio|s2}} at h = {{v2_diag_h}}, with an interval of {{a1_gap_ci_h368|s2}} on the gap; all {{n7_a1_k_h368}} trajectories agree in sign, and the exact p of {{n7_a1_p_h368_frac}} is the smallest attainable at four. A rule committed before those runs, on one seed per arm, found the advantage at h = {{v2_diag_h}}; the three-seed extension was computed afterwards and carries none of its weight. The advantage grows with the horizon and is weakest inside the eight steps the model is trained on (Appendix G gives every horizon).

### 4.2 The configuration claim

The original varies the history length M and the forecast length N and says moderate values trade accuracy against training time, with {{mn_centre_label}} as its instance. We tested only the accuracy half, one factor at a time, at {{iters_main}} iterations on the held-out pair. At that budget {{mn_better_kinds}} beat the centre, but with {{mn_nind}} trajectories no comparison can be significant after exact tests, and trained longer the centre passes each of them on some reading, so which setting is most accurate depends on the budget. The original's trade-off with training time is not tested, and at our budget the centre is not shown to be best and no alternative is shown to be better (Appendix H).

### 4.3 The architecture claim: consistent, but a weak test

The original says RWM beats an MLP, a recurrent state-space model (RSSM) and a transformer. We built all three to our reading of the original's table of shapes, gave them RWM's settings, and trained each both teacher-forced, as the original does, and autoregressively. Table 2 gives nRMSE at h = {{v2_diag_h}}. Every baseline is worse than RWM on all four trajectories, but at four trajectories even that gives only the smallest attainable exact p, and no baseline beats even the training mean, which is the stronger of the three floors here. The result is consistent with the claim and a weak test of it: the baselines are untuned, their sizes and settings are our reading, and four trajectories cannot reject anything.

| Model | nRMSE, h = {{v2_diag_h}} | worse than RWM on | exact p |
|---|---|---|---|
| RWM (our rollout-trained arm) | {{h2h_armA_nrmse_h368|s2}} | | |
| MLP, teacher-forced † | {{h2h_bl_mlp_tf_nrmse_h368|s2}} | {{n7_bl_mlp_tf_nrmse_h368_k}} of {{mn_nind}} | {{n7_bl_mlp_tf_nrmse_h368_p_frac}} |
| MLP, rollout-trained | {{h2h_bl_mlp_ar_nrmse_h368|s2}} | {{n7_bl_mlp_ar_nrmse_h368_k}} of {{mn_nind}} | {{n7_bl_mlp_ar_nrmse_h368_p_frac}} |
| Transformer, teacher-forced † | {{h2h_bl_transformer_tf_nrmse_h368|s2}} | {{n7_bl_transformer_tf_nrmse_h368_k}} of {{mn_nind}} | {{n7_bl_transformer_tf_nrmse_h368_p_frac}} |
| Transformer, rollout-trained | {{h2h_bl_transformer_ar_nrmse_h368|s2}} | {{n7_bl_transformer_ar_nrmse_h368_k}} of {{mn_nind}} | {{n7_bl_transformer_ar_nrmse_h368_p_frac}} |
| RSSM, teacher-forced | {{h2h_bl_rssm_tf_nrmse_h368|s2}} | {{n7_bl_rssm_tf_nrmse_h368_k}} of {{mn_nind}} | {{n7_bl_rssm_tf_nrmse_h368_p_frac}} |
| RSSM, rollout-trained † | {{h2h_bl_rssm_ar_nrmse_h368|s2}} | {{n7_bl_rssm_ar_nrmse_h368_k}} of {{mn_nind}} | {{n7_bl_rssm_ar_nrmse_h368_p_frac}} |
| Floor: predict the training mean | {{n10_mean_nrmse_heldout_h368|s2}} | | not tested |
| Floor: hold the last state | {{n10_hold_nrmse_heldout_h368|s2}} | | not tested |
| Floor: repeat a seasonal pattern | {{n10_seas_nrmse_heldout_h368|s2}} | | not tested |

*Table 2: nRMSE at h = {{v2_diag_h}} on the held-out pair ({{mn_nind}} independent 400-step trajectories from two episodes); our models at {{iters_main}} iterations, every model with RWM's settings. † a diverged row, whose size is not meaningful; only its sign is. A value below the training-mean floor beats predicting the average.*

Matched to RWM's parameter count instead, the rollout-trained MLP is worse than RWM on {{n7_x4_mlp_k}} of {{mn_nind}} trajectories and the transformer on {{n7_x4_transformer_k}} of {{mn_nind}} (exact p {{n7_x4_transformer_p_frac}}), so the transformer cannot be told apart from RWM; that tests parameter count and nothing else. Our RSSM collapses when rolled out and is not an informative comparison; the failure may be ours rather than the architecture's.

---

## 5. The follow-up's uncertainty

### 5.1 What RWM-U claims and what its code computes

RWM-U makes three claims about its ensemble that we can test. It says the learned variance "captures aleatoric uncertainty effectively" (its §4.1, unchanged across versions); that the disagreement across members "closely follows the trend of the prediction error" and so serves as a trust metric (its §5.1); and, from its second version on, that uncertainty is "effectively propagated over long horizons".

The released code computes two quantities at each step: the mean across members of each member's predicted σ, which we call aleatoric, and the standard deviation across the members' mean predictions, which we call epistemic (`system_dynamics.py:125-126`). Only the second reaches the policy. It is returned at `envs/base.py:158` and applied as a reward penalty with weight −1.0 at `:166`; the aleatoric term is bound to a variable that is never read again (`:142`). The paper's Eq. 4 specifies a variance where the code computes a standard deviation; the first author confirms that the code's quantity is the intended one and that the aleatoric term is reported for analysis only (supplement S5). We measure the code's quantity. RWM-U does not claim a calibrated interval, and a penalty weight can absorb a constant factor, so what we test is what the spread reports at one step and how that changes with the horizon (§5.2, §5.7). The five members share one recurrent trunk, as RWM-U's authors state, and §5.3 measures what that costs.

As we read MOPO's penalty, its job is to bound the model's error at the states the policy visits, one step at a time. That is the job against which we judge the spread, and it separates three gaps that a single ratio of spread to error runs together: the one-step gap on held-out data (§5.2); the gap between what an ensemble can and cannot see (§5.3); and the gap between a one-step spread and accumulated error (§5.4).

### 5.2 At one step, the spread already falls short

At one step nothing has accumulated: the input is the true state, and σ is asked the question it was trained on. Table 3 gives, for each ensemble, the ratio R of its mean squared error to the squared error its spread predicts, the factor k on σ that restores nominal coverage at h = 1 and at h = {{v2_deploy_h}}, and the ±1σ coverage at h = {{v2_deploy_h}} when the members are rolled out on their own predictions (§5.4).

| Ensemble | Arena (independent trajectories) | One-step R [95% CI] | k at h = 1 | k at h = {{v2_deploy_h}} | ±1σ coverage at h = {{v2_deploy_h}}, per-member rollout |
|---|---|---|---|---|---|
| Released checkpoint | all ten released episodes ({{e7_nind}}) | {{n14_R_rel|s2}} {{n14_R_rel_ci|s2}} | {{n8_k_rel_epi_h1|s2}} | {{n8_k_rel_epi_h100|s2}} | {{x9_rel_per_cov1_h100|s2}}% |
| Shared-trunk ensembles of five, our arms | held-out pair ({{m23_nind}}) | {{n14_R_e5|s2}} {{n14_R_e5_ci|s2}} | {{n8_k_e5_epi_h1|s2}} | {{n8_k_e5_epi_h100|s2}} | {{x9_e5_per_cov1_h100|s2}}% |
| Shared-trunk ensembles of five, our arms | five folds ({{x3_n}}) | not measured | not measured | not measured | {{x11e_per_cov1_h100|s2}}% |
| Independently trained members, five | held-out pair ({{m23_nind}}) | {{n14_R_ind|s2}} {{n14_R_ind_ci|s2}} | not measured | not measured | {{x9_ind_per_cov1_h100|s2}}% |
| Independently trained members, three | five folds ({{x3_n}}) | not measured | not measured | not measured | {{x9_fold_per_cov1_h100|s2}}% |

*Table 3: our arms at {{iters_main}} iterations, the released checkpoint as released. A cell the artifacts do not hold reads "not measured". Intervals at four trajectories are descriptive: the smallest exact p there is {{n7_p_min_n4_frac}}.*

Every interval for R lies above one: even at one step no ensemble's spread accounts for its error, and the independently trained members come closest. On the folds' {{x3_n}} independent held-out trajectories, the shared-trunk ensembles' error-to-spread ratio $\rho$ at one step is {{x11a_rho_out_h1|s2}}, against {{m65_calib_ratio|s2}} for a calibrated Gaussian. The released checkpoint's disagreement is {{d1n_epi_ratio_h1|s2}}× smaller than its error at h = 1, with {{d1n_epi_cov1_h1|s2}}% coverage, and the per-member σ the method discards is {{d1n_alea_ratio_h1}}× smaller than that error; which rows trained it is not recorded (§3.2), so that figure rests on all ten of its released episodes, {{e7_nind}} independent trajectories. R compares squared errors, so it is larger than the ratio of mean absolute error to spread and than the coverage-matching factor k; the three summarise one shortfall.

**Does measuring on training data flatter the result?** Not at one step. With every episode held out once and also scored in sample, the ratio of in-sample to held-out error-to-spread at h = 1 is {{x11a_q_h1|s2}} {{x11a_q_h1_ci|s2}}: not resolved in either direction. An earlier comparison on four held-out trajectories found it worse in sample, {{x10_q_h1|s2}} {{x10_q_h1_ci|s2}} (descriptive at four), and does not hold up at twenty. At h = {{v2_deploy_h}} in-sample measurement flatters ({{x11a_q_h100|s2}} {{x11a_q_h100_ci|s2}}). For each model the two arenas differ in episodes as well as in training status, so the reading depends on the horizon and not on a fixed sign.

### 5.3 What an ensemble can see: the shared trunk

Abbas et al. (2020) separate aleatoric noise, parameter uncertainty and model inadequacy. Spread across members estimates at most the second; to the extent that one-step error is model inadequacy, no spread across members estimates it. That bears on §5.2 before any trunk is considered.

The trunk is shared. The state pathway is one recurrent trunk plus {{v1_members_word}} small heads, and per member {{v1_shared_pct|s2}}% of the parameters are numerically identical to every other member's. An autoregressive rollout feeds the ensemble mean back into one recurrent state, so there is one hidden-state trajectory between them and the spread is that of {{v1_members_word}} heads reading one vector. RWM-U states the sharing; what we add is its measured size and consequence. Such members have correlated errors by construction, so their spread cannot express uncertainty the trunk does not already carry. Randomised prior functions and Bootstrapped DQN are ensembles of the same kind (Osband et al. (2016), Osband et al. (2018)). RWM-U calls its members a bootstrap ensemble; per-head resampling exists in the online training path and not in the offline one our arms follow (Appendix O).

Training five independently initialised full models and using them as an ensemble improves the error-to-spread ratio $\rho$ at h = {{v2_deploy_h}} by {{m44_ratio_gain|s2}}×, against a minimum detectable effect (the smallest gain the comparison could reliably detect) of {{m44_mde_ratio|s2}}×, on the held-out pair's {{m23_nind}} independent trajectories; on the folds' {{x3_n}} trajectories the gain is {{x11d_ratio_gain|s2}}× with {{x11d_cov_gain|s2}} points more coverage. That bounds the sharing effect and does not isolate it: independent members also differ in capacity ({{v1_cap_ratio|s2}}× the parameters) and in data order, and at matched capacity the gain, {{m49_ratio_gain|s2}}×, is below what that comparison can resolve. Combining independence with the corrected loss adds nothing beyond independence alone (Appendix K). Neither ensemble is an interval.

### 5.4 Does the spread accumulate?

RWM-U's second version says uncertainty is "effectively propagated over long horizons". Testing that against accumulated error is legitimate. It is not a test of calibration: at depth the input to σ is the model's own earlier output, wrong by an amount σ never claimed to describe, so a growing error-to-spread ratio is not a failure of the penalty's one-step job (§5.2).

The release feeds every member the ensemble mean through one recurrent state, so its spread at a deep step is a one-step spread at one shared history. We asked whether rolling each member out on its own predictions instead makes the spread track accumulated error. At h = {{v2_deploy_h}} it closes a share {{x9_rel_f_h100|s2}} {{x9_rel_f_h100_ci|s2}} of the log gap between spread and error (the log of the error-to-spread ratio, compared before and after the change) on the released checkpoint (its ten released episodes, {{e7_nind}} trajectories), {{x11e_f_h100|s2}} {{x11e_f_h100_ci|s2}} on the shared-trunk ensembles of the five folds ({{x3_n}}), and {{x9_fold_f_h100|s2}} {{x9_fold_f_h100_ci|s2}} on the independent ensembles of the folds. On the held-out pair's four trajectories the shared-trunk and independent ensembles close {{x9_e5_f_h100|s2}} and {{x9_ind_f_h100|s2}}, descriptive only (exact p {{x9_e5_p_h100_frac}}). At h = {{v2_deploy_h}} the released checkpoint's ±1σ coverage rises from {{x9_rel_mean_cov1_h100|s2}}% to {{x9_rel_per_cov1_h100|s2}}% and CRPS and NLL improve too, so the effect is not only a wider spread, but coverage stays below the {{x9_band_lo|s2}}–{{x9_band_hi|s2}}% band around the target, so it does not close the gap (Figure 1b).

What this settles: "effectively propagated" fails as the release rolls the ensemble out; most of the log gap closes when the members are rolled out separately, though coverage stays below the band. Per-member propagation is not the released method, and the release's own imagination rollout, which propagates one member per environment, is not tested.

### 5.5 Why the per-member variance collapses

The follow-up reads the low aleatoric value as reflecting small stochasticity in the environment. The observation is right and the reading is not. The implemented state loss is squared error on a sample from the predicted Gaussian, not a likelihood: its expectation is (μ − y)² + σ², which is minimised at σ = 0 for any μ. Nothing in the loss opposes it. The upper bound is built as the lower bound plus a learned gap, so the lower bound receives no gradient from the bound term and moves only through the state loss. The objective's optimum is σ = 0 per step; the fed-back sample is a second pathway we did not isolate, and the teacher-forced arm, which shares the loss, collapses at the same rate.

We tested it before training. On synthetic data whose known noise varies {{e5s_span|s2}}× over the input range, the released head under the implemented loss sits {{e5s_mse_under|s2}}× below the true noise and does not track it, while under the authors' unused likelihood branch it recovers the level (ratio {{e5s_nll_ratio|s2}}, averaged over seeds). Across the {{n_runs}} runs at the released width that the fitted rate uses (Figure 2 draws the {{fig8_n_runs}} logged runs of {{iters_main}} iterations) the log-σ range moves linearly in iteration count, falling under sampled MSE and rising under the likelihood (Figure 7, Appendix J).

Figure 2 shows σ itself, and the rate is an Adam property. The collapse moves log Δ, the log of the gap between the σ bounds, by a median {{n13_rate_over_lr_median|s2}} learning rates per iteration over {{n13_n_runs}} runs, the ordinary step of Adam (Kingma and Ba, 2015), and only the sign flip speaks to the objective. Even at the largest step Adam can take ({{n13_bound_over_lr|s2}}× the learning rate), the checkpoint's variance state would need {{n13_iters_worst}} iterations from the released initialisation, against the {{iters_main}} we trained for. The bounded head is inherited from PETS (Chua et al., 2018); of {{q1_n_looked}} public repositories inspected, {{q1_n_carry}} implement it and {{q1_n_inherit}} optionally trains it on sampled squared error (Appendix J).

### 5.6 Ranking

Disagreement ranks error well, and we report it with Spearman's rank correlation (§3.3), taken between the scalar the method applies and total absolute error across the pooled (trajectory, step) points up to the horizon, and at h = 1 across trajectories. On the released checkpoint over all ten released episodes ({{e7_nind}} independent trajectories), Spearman is {{n11_d2_sp_epi_h100|s2}} at h = {{v2_deploy_h}}, and its lead over the forecast step index, a counter that needs no ensemble, is resolved at every horizon from h = 8 on (at h = 1 the index is constant, so no comparison with it is defined); at h = 1 Pearson is the higher ({{d2_epi_h1|s2}} against {{n11_d2_sp_epi_h1|s2}}). The rules committed before these readings used Pearson, and their verdicts keep it.

Does the ensemble beat something free? Against the model's own predicted step size, whole trajectories cannot settle the margin at h = {{v2_diag_h}} under Pearson ({{e7_step_margin|s2}}, below the {{e7_mde_margin|s2}} that sample can resolve), though under ranks the margin has an interval above zero ({{n11_e7_sp_step_margin|s2}} {{n11_e7_sp_step_margin_ci|s2}}). A rule committed before its reading put the same comparison to {{x6_n_units}} non-overlapping shorter units at h = {{v2_deploy_h}} on the same checkpoint: the margin is {{x6_margin|s2}} {{x6_ci|s2}}, resolved on this checkpoint's ten released episodes and not re-tested at h = {{v2_diag_h}}. Disagreement keeps real information with step size partialled out, so "disagreement ranks error well" is supported, and "it ranks better than a free signal" holds on shorter units and under ranks but not under the pre-registered whole-trajectory test.

On a model we trained, a rule committed before its reading (disagreement against the index on the held-out pair, four trajectories) was inconclusive: the direction held at every horizon, but the paired interval excluded zero at {{e5_n_excl}} of {{e5_n_horizons}} horizons, short of the majority it required. The same comparison on the folds' {{x3_n}} trajectories, committed before its data, is resolved: disagreement leads at {{x11b_n_leads}} of {{x11b_n_horizons}} horizons and the paired interval excludes zero at {{x11b_n_excl}}.

### 5.7 Rescaling per horizon

A constant factor could be absorbed by the penalty's weight, so the one-step shortfall alone does not show the penalty mis-sized; what no constant can absorb is that the factor grows with the horizon. One constant scalar does not repair the spread, because the ratio of error to spread grows: on the released checkpoint the coverage-matching factor k (§3.3) is {{n8_k_rel_epi_h1|s2}} at h = 1 and {{n8_k_rel_epi_h368|s2}} at h = {{v2_diag_h}}. A multiplier per horizon is a split-conformal construction (Angelopoulos and Bates, 2021): a σ-normalised score, one quantile per horizon, fitted on calibration units and scored on others. Its finite-sample guarantee needs exchangeable calibration units, which here means episodes and not steps, and then coverage lies between the target and the target plus one over the number of calibration units plus one, so a ten-point band needs at least nine calibration episodes. The units of the nine-episode fit are the released checkpoint's ten released episodes; if it trained on them, which the data cannot rule out, its guarantee holds for in-sample use only.

Fitted on nine episodes and scored on the tenth, the released checkpoint's ±1σ coverage over all ten released episodes' {{x7_n_traj}} independent trajectories is within the band at every horizon. ±2σ is not restored: at h = {{v2_deploy_h}} it is {{n9_epi_perh_cov2_h100|s2}}% {{n9_epi_perh_cov2_h100_ci|s2}} against {{v3_cov_nominal2|s2}}%, because the errors are heavy-tailed (across all {{n8_n_cells}} cells of the tails analysis, {{n8_n_heavy}} over-cover at ±1σ and under-cover at ±2σ once σ is rescaled). CRPS improves, from {{n9_epi_before_crps_h100|s2}} to {{n9_epi_perh_crps_h100|s2}} at h = {{v2_deploy_h}}. Rescaling fixes the scale and not the shape. An earlier reading that every cell is Gaussian was withdrawn (Appendices M and E).

On episodes the model never saw, the evidence is mixed. The multipliers of our rollout-trained models calibrate {{d3x_own_epi_ok}} of {{d3x_own_epi_cells}} cells (a cell is one multiplier scored on one held-out unit at one horizon) on the held-out pair's {{m23_nind}} independent trajectories, and on the five folds a rule committed before its data finds the per-horizon multiplier calibrates {{x11c_cells_cal}} of {{x11c_n_cells}} cells and finds that it does not restore calibration, while the folds' pooled ±1σ coverage, reported beside it and not as a reading, is {{x11c_pooled_cov1_h100|s2}}% at h = {{v2_deploy_h}}, inside the ten-point band around the target. The verdict stands, and both measurements are the result: pooled across folds the multiplier lands near the target, cell by cell it often does not, and its guarantee is for the units that fitted it.

---

## 6. Defects in the released pipeline

Two defects in the released code and data bear on what precedes; Appendix N gives the rest, and Appendix O the places where the code departs from the paper's description.

**Unmarked episode boundaries.** The data file concatenates ten episodes with a termination column that is identically zero, so the window builder marks all {{win_naive}} windows valid, including {{win_cross}} that splice one episode's end onto the next one's start (§3.2). We recover the boundaries from the reset rows and exclude those windows. Training on spliced windows costs nothing measurable in rollout: over {{tw_cells}} cells a contaminated arm is hurt in {{tw_cc_cluster_hurt}} and helped in {{tw_cc_cluster_helped}}, consistent with regularisation and not with harm. The defect remains a real one on leakage grounds (Appendix N).

**The action is one step stale in evaluation.** Row t holds the action that produced state t: at every reset row all twelve actions are exactly zero, which a policy network with biases cannot emit, and which is what Isaac Lab writes at a reset. Training pairs a state with the action in its own row; evaluation feeds the action from the previous row, one step stale. Shifting the two action slices of the evaluation loop (`model_training.py:129` and `:132`) aligns it, and our harness does this with `action_offset = 1` (`src/score_reference.py:180-190`). On the released checkpoint's all ten released episodes ({{ad20_nind}} independent trajectories), the stale action raises relative-L1 error by {{adh20_rel_h1|s2}}% {{adh20_rel_ci_h1|s2}} at h = 1 and {{adh20_rel_h32|s2}}% {{adh20_rel_ci_h32|s2}} at h = 32; from h = {{v2_deploy_h}} the change is not resolved ({{adh20_rel_h100|s2}}% {{adh20_rel_ci_h100|s2}} there). On the held-out pair's {{ad_nind}} trajectories it raises the error at every horizon reported. Our own models trained under the causal pairing are also hurt by the stale one (Appendix N). We sent this to the first author before submission and had no reply when we submitted.

**Evaluation on training data.** The released evaluation draws its trajectories from the data the checkpoint may have trained on, and no file records which rows it used (§3.2), so no held-out measurement of the released checkpoint is possible. For our models we keep the two arenas apart throughout.

**The variance state.** The checkpoint's stored variance state cannot be reached from the released initialisation at a constant rate: even at the largest step Adam can take (Kingma and Ba, 2015), {{n13_iters_worst}} iterations would be needed, against the iteration counts that the release, the paper and the checkpoint's tag give. The first author's account, that the release is several revisions removed from the setup that trained it, supplies a mechanism such as a warm start. This is a documentation gap between a release and a run, not an inconsistency (Appendix J). The first author also confirmed Eq. 4's intended quantity and the discard of the aleatoric term (supplement S5).

---

## 7. Lessons and limitations

**Lessons for a practitioner.**
- *Use ensemble disagreement as a ranking signal, price it against free alternatives, and do not read it as a distance.* It ranks error well and better than the forecast step; on the released checkpoint it is also ahead of the model's own predicted step size on shorter units and under ranks, though the linear margin on whole trajectories is not resolved. Its size is wrong at every horizon, including one step (§5.2, §5.6).
- *If you need an interval, rescale per horizon and refit on your own model.* On the released checkpoint this restores one-sigma coverage and not two-sigma; on episodes a model never saw the evidence is mixed (§5.7).
- *Roll ensemble members out separately if you want their spread to track accumulated error.* Feeding every member the ensemble mean does not (§5.4).
- *Check that the implemented loss is the described loss.* Here the variance has an optimum at zero, which a reading of the code explained (§5.5).
- *Count independent trajectories, report an exact p beside every interval at four, and permute whole trajectories.* Sign counts over coupled state dimensions are not independent trials, and an earlier draft of this paper made its weakest evidence look strongest that way (§3.4).
- *Say which arena a calibration number comes from.* Measuring on training data neither flatters nor worsens one-step calibration resolvably, and flatters it at long horizons (§5.2).
- *Anchor a decision rule to the horizon the claim is about.* Our first rule was anchored at the training horizon and pointed at the wrong regime (Appendix G).

**Limitations.** One robot, one gait and one flat terrain, and one dataset, so "generalisation" here means across velocity commands only. No policy is trained, so what the miscalibration costs RWM-U's policies is untested. The reason it may matter is that MOPO's penalty is meant to bound one-step error at visited states, and the spread falls short of the error already at one step (§5.2). A test that needs no policy, of the penalty against the model's error in predicted return, could not be run because the released data do not record the velocity command its reward terms score against. The held-out pair is four trajectories from two episodes, so no comparison there can be significant; the fold replications reach twenty, but their models share most training episodes. The released checkpoint's training rows are not recorded. Our baselines are untuned readings of the original's table of shapes, and our data are a small fraction of the reference's. We apply no correction across our own {{appG_n_rules}} pre-registered rules, each reported against the threshold it was committed with. Whether other descendants of the PETS head inherit the σ = 0 optimum is untested.

---

## 8. Conclusion

RWM's central training claim reproduces on held-out episodes at long horizons and reverses at one step on short windows; its other two claims get weak tests, and at h = {{v2_diag_h}} the baselines we built never beat even the training mean. RWM-U's ensemble disagreement ranks error correctly and sizes it wrongly: even at one step every ensemble's error exceeds its spread, members that share a trunk can disagree only about what it carries, and the release's rollout stops the spread accumulating, which rolling members out separately partly repairs. The per-member variance collapses because the implemented loss is minimised at zero. Rescaling per horizon restores one-sigma coverage on the released checkpoint, not two-sigma, and on unseen episodes the evidence is mixed. As a scalar penalty, disagreement is a ranking and not a scale, and a ranking use deserves validation on the deployment distribution. What should travel is the objective's property, which should be checked wherever a bounded σ head is trained against sampled squared error; the released artifact's specific factors should be checked rather than assumed, and the limits of one robot's data are limits on what could be resolved, not findings in either direction.

| Claim | Evidence | Where it stands | Section |
|---|---|---|---|
| RWM: training on rollouts beats teacher forcing at long horizons | {{x3_n}} trajectories from all ten episodes, each held out once | holds at h = {{v2_diag_h}} on every episode; reverses at one step on short windows | §4.1 |
| RWM: moderate history and forecast lengths trade accuracy against training time | held-out pair, {{mn_nind}} trajectories | centre not shown best at our budget; the ranking depends on training length; the time trade-off is untested | §4.2 |
| RWM: it beats MLP, RSSM and transformer baselines | held-out pair, {{mn_nind}} trajectories | consistent with the claim, a weak test | §4.3 |
| RWM-U: the learned variance captures aleatoric uncertainty | our own runs, a synthetic test with known noise, and the released checkpoint's σ ({{e7_nind}} trajectories) | not supported: the objective's optimum is zero | §5.5 |
| RWM-U: disagreement is a trust metric | released checkpoint, {{e7_nind}} trajectories; our arms, {{m23_nind}} and {{x3_n}} | supported as a ranking; wrong as a scale at every horizon, including one step | §5.2, §5.6 |
| RWM-U: uncertainty is effectively propagated over long horizons | released checkpoint and our arms, {{e7_nind}} and {{x3_n}} trajectories | fails under the release's rollout; per-member rollout partly repairs it | §5.4 |

*Table 4: where each tested claim stands. Our arms are at {{iters_main}} iterations; the released checkpoint is as released.*

## Reproducibility and data

A clean clone reproduces every scientific value: of {{ver_values}} regenerated values, {{ver_identical}} are bitwise identical, and the {{ver_differing}} that differ are bookkeeping about the submission's own files ({{ver_diff_plain}}), while {{ver_part_sci}} are a measurement, a statistic or a verdict (supplement S11). Code, every artifact and the claim ledger accompany this submission as anonymised supplementary material, and a permanent archival identifier follows acceptance. Neither upstream repository is redistributed: `setup.sh` fetches both at pinned commits and verifies their hashes.

## References

1. C. Li, A. Krause, M. Hutter. *{{ref1_title_read}}.* arXiv:2501.10100**{{ref1_read}}**, {{ref1_read_date}}; current version {{ref1_current}}, {{ref1_current_date}}, under the same title.
   Presented as a workshop poster at {{ref1_conf}} (*{{ref1_workshop}}*); the venue's page does not say whether the workshop is archival.
   *Read at v1, whose Roman-numeral sectioning our references follow; v2 ({{ref1_v2_date}})
   renumbered to Arabic and moved IV-C into Appendix A.4.1.*
2. C. Li, A. Krause, M. Hutter. *{{ref2_title_read}}.* arXiv:2504.16680**{{ref2_read}}**, {{ref2_read_date}}; current version {{ref2_current}}, {{ref2_current_date}}, retitled *{{ref2_title_current}}.*
   Presented as a workshop poster at {{ref2_conf}} (*{{ref2_workshop}}*); the venue's page does not say whether the workshop is archival.
   *Read at v1. §3.2 and Eq. 4–5
keep their numbers there; every figure and appendix table has moved, and the model is
renamed {{v4_name_v1}} to {{v4_name_v3}} — the same model, with the letter re-expanded from
"{{v4_exp_v1}}" to "{{v4_exp_v3}}". The two names never co-occur: v1 uses
{{v4_name_v1}} {{v4_name_n_v1}} times and no {{v4_name_v3}}, v3 the reverse. The crosswalk
is in `results/original_paper_figures.json`.*
{{t1_reference_list}}

*Entries {{t1_first_entry_n}}–{{t1_last_entry_n}} are generated from `results/t1_bibliography_verified.json`. Each was checked against the paper itself: title and full author list from the arXiv record or, for an entry with no arXiv id, from its DOI's Crossref record or its proceedings page; venue from the record or the paper's first page; and every sentence this paper attributes matched verbatim against that paper's own text: {{t1_n_verified}} of {{t1_n_refs}} entries and {{t1_n_frag_ok}} of {{t1_n_frag}} attributed fragments, {{t1_n_frag_oneword}} of them single common words whose match verifies nothing about the attribution (ledger `D-35`). No entry was added that was not verified.*

## Appendix A — Reimplementation and equivalence

The reimplementation is checked against the released module level by level before any training, which is why a later difference belongs to the method and not to our wiring (§3.1).

What every downstream number rests on. Each level was passed before the next was attempted.

| level | claim | result |
|---|---|---|
| shapes | parameter counts match the reference | exact |
| wiring | inference outputs match the reference module | **{{wiring_max_diff}}**, bitwise |
| indexing | the harness feeds the actions it claims | bitwise against the raw CSV |
| residual | the zero-delta model is the hold-last floor | {{zero_delta_resid}} |
| **objective** | **losses and gradients match** | **{{diff_grad_max}} across {{diff_terms}} terms, {{diff_n_params}} tensors** |
| trainer | can memorise a single batch | {{overfit_reduction}}× loss reduction |

## Appendix B — Data, arenas and compute

The data file, its windows and the arenas of Table 1 (§3.2), and the commands that rerun the pipeline.

**Windows and boundaries.** The file has {{rows}} rows. The reference window builder marks all {{win_naive}} windows of {{win_len}} rows valid, {{win_cross}} of which splice one episode's end onto the next one's start; the usable, episode-respecting count is {{win_usable}}, and the contamination rate of the unfiltered set is {{contam_pct}}%. Everything here ran on two CPU cores; per-run times, the training queues and their overlaps are in supplement S7.

    ./setup.sh                     # clone upstreams at pinned commits
    python3.11 -m venv .venv && . .venv/bin/activate
    pip install -r requirements.txt
    ./reproduce.sh --quick --force # everything except training

`--force` matters: a clean clone already contains each stage's declared output, so without it every stage skips.

Runtimes, the queues that produced them and the CPU work they overlapped are in supplementary S7.

## Appendix C — Statistical methods

The procedures behind every interval and test in the paper (§3.4), stated once.

**Cluster bootstrap over trajectories.** Each 95% interval resamples whole 400-step trajectories, the unit of dependence, with replacement and recomputes the statistic inside every draw; seeds, where pooled, are pooled inside each draw. With {{m23_nind}} trajectories there are {{c3_resamples}} distinct resamples, so such intervals are coarse and the percentile method is unreliable; the literature on inference with few clusters is the reason (Cameron et al. (2008)), and we pair each interval at that size with an exact test. Resampling pooled seed × trajectory values instead of trajectories narrows intervals by a mean {{bu_mean_ratio}}× and changes {{bu_changes}} of {{bu_cells}} verdicts, in {{bu_change_cell}}; wherever the two units differ we report both.

**Exact sign-flip tests.** For a paired difference over n trajectories the statistic is the mean difference and the null makes each trajectory's sign equally likely; every sign pattern is enumerated and the p-value is two-sided. At four trajectories the smallest attainable p is {{n7_p_min_n4}}, above the first Holm level of the configuration sweep ({{n7_sweep_holm_first}}) and of the baseline and size-matched families, so none of those families can reject anything; {{n7_n_4of4}} of the {{n7_n_n4}} comparisons at four trajectories reach that minimum. At the episode level, at h = {{v2_diag_h}}, the ten episodes give a smallest p of {{n7_x3_ep_p_h368}}.

**Multiplicity.** Holm's procedure holds the chance of any false rejection at the five per cent level within each pre-registered family. No correction is applied across rules.

**Permutation nulls that keep dimensions together.** The 45 state dimensions of a robot are coupled and share a forecast-depth trend, so a null that treats them as independent trials is wrong. Where we test a per-dimension correlation, the null permutes whole trajectories, which preserves the coupling between dimensions; Appendix I gives the tests and the binomial version they replace.

## Appendix D — Claims of the originals and the version crosswalk

Each claim of the two original papers, what we did with it and where it stands (§4, §5, Table 4), and how the versions we read differ from the current ones.

The body's §4 summarises the first table. It is here in full because the third column — what the
original actually reports — is the answer to a question a reader of any reproduction should ask,
and because "no quantitative figure" is itself a finding that deserves to be checkable row by row. Its verdict cells quote figures from the sections they cite, each on that section's arena, n_independent and checkpoint; the second table gives them claim by claim.

*Section references follow arXiv:2501.10100**v1**, which uses Roman-numeral sectioning. v2
renumbered to Arabic and moved IV-C's material into Appendix A.4.1. References to
arXiv:2504.16680 follow **v1**, which is the version we read; it is now at
{{v4_current}} ({{v4_current_date}}), where §3.2 and Eq. 4–5 keep their numbers but every figure
and appendix table has moved — {{v2_fig_v1}} became {{v2_fig_v3}}, and the model was renamed {{v4_name_v1}} to
{{v4_name_v3}}, which is a re-expansion of the letter ("{{v4_exp_v1}}" to
"{{v4_exp_v3}}") rather than a second variant: no version of the paper contains both
names. All locations, and the occurrence counts that establish that, are recorded in
`results/original_paper_figures.json`.*

| claim, and where | tested | what the original reports | verdict |
|---|---|---|---|
| RWM-AR consistently outperforms RWM-TF (2501.10100 §IV-D) | **yes** | **no quantitative figure.** "significantly outperforms"; the gap is plotted in Fig. 7 and stated nowhere in text, caption or table | **reproduces** at long horizon (§4.1); retrained on fixed folds with each episode held out once it replicates, {{x3_gap}} {{x3_ci}} at h = {{v2_diag_h}} over all ten episodes' {{x3_n}} trajectories at {{iters_main}} iterations, not {{iters_long}} (rule X3: **{{x3_reading}}**, §4.1, Appendix G), and scored with the released evaluation's timing rule M-23's verdict stands (rule X8: **{{x8_reading}}**, Appendix E) |
| Teacher forcing gives "poor autoregressive performance" (§IV-C) | **yes** | **quantitative**: Fig. 6 prints e for the teacher-forced N=1 row, {{orig_tf_e_n1}} at {{mn_n1_label}} against {{orig_tf_e_centre}} at the centre, on unstated data and horizon; the passage itself gives no number | reproduces, and more strongly: on the 400-step unit Arm B is worse than the hold-last floor at every horizon (on M-64's shorter units only at the longest they reach), and §4.2's {{mn_n1_label}} is {{mn_tf_ratio}}× the centre's error at h = {{v2_diag_h}} |
| M=32, N=8 gives the optimal trade-off between accuracy and training time (§IV-C) | **yes** | **quantitative**: Fig. 6 prints the error and the training hours of every cell of its grid, and the centre's error is the tied-lowest (`docs/presubmission/ORIGINAL_SPECS.md` a.5) | **{{mn_verdict}}** on accuracy alone (§4.2): {{mn_better_list}} beat it at our budget (no reading its rule reports puts the centre ahead of any of them), but the ranking depends on training length: trained longer, the centre passes each of them on at least one reading (post hoc, §4.2, Appendix H). The trade-off with training time is not tested; the original's printed hours are consistent with it. Under the released evaluation's timing the rule keeps its verdict (rule X8: **{{x8_reading}}**, Appendix E) |
| Beats MLP, RSSM and transformer baselines (§IV-D) | **yes** | **no quantitative figure.** "consistently achieves the lowest prediction errors across all environments"; plotted in Fig. 7, with no number in text, caption or table | **{{bl_tf_verdict}}** with the baselines teacher-forced, as the original trains them, and **{{bl_ar_verdict}}** with them trained autoregressively, which compares architectures at one training regime rather than testing this claim (§4.3). Both are the rules' verdicts at h = {{v2_diag_h}}; from h = {{bl_tf_from_h}} and h = {{bl_ar_from_h}} respectively, every reading the rules report gives them, and at shorter horizons they split. The baselines are built to our reading of Table S7 and trained with RWM's settings; at h = {{v2_diag_h}} every one is worse than predicting no change, and rule X1's other read-outs and retraining variants did not rescue our RSSM (**{{x1_final_reading}}**), so the RSSM comparison stays uninformative and the claim rests on the MLP and the transformer. Matched to RWM's parameter count, they return **{{x4_reading}}** (rule X4): the MLP is behind ({{x4_res_mlp}}) and the transformer cannot be settled ({{x4_res_tf}}), matching size being one axis only (§4.3). Under the released evaluation's timing both rules keep their verdicts (rule X8: **{{x8_reading}}**, Appendix E). One robot where the original has several |
| Zero-shot hardware transfer (§IV-E) | no | — | `[hardware: zero-shot transfer]` no hardware; this is a dynamics-model reproduction |
| Policies transfer to hardware from ~6M state transitions against ~250M for the model-free baseline (its Limitations section and table, from v2 on; not in v1) — the paper's headline sample-efficiency result | no | **{{orig_se_rwm}} against {{orig_se_ppo}} state transitions** at equal real tracking reward ({{orig_se_rwm_rew}} against {{orig_se_ppo_rew}}), Table 1 from v2 on — the only table of numbers in either paper | `[policy, hardware: the sample-efficiency result]` **not tested.** It is a claim about policy learning and hardware deployment, and requires the RL loop, a simulator and an ANYmal. We reproduce the dynamics model only; no policy is trained anywhere in this work, so no transition count of ours is comparable |
| MBPO-PPO beats SHAC and Dreamer (§IV-E) | no | — | `[policy: the comparisons against SHAC and Dreamer]` no policy learning reproduced |
| Generality across quadruped, humanoid, manipulation (§IV-D) | no | plotted in Fig. 7; no numbers in text | `[model: generality across robot morphologies]` one released dataset, ANYmal D flat |
| Epistemic "closely follows the trend of the prediction error", justifying "its role as a trust metric" (2504.16680v1 §3.2) | **yes** | **no quantitative figure.** A "strong correlation" is asserted with no coefficient, interval or sample size; plotted in Fig. 2 (right) | **supported as a scalar ranking, against a real baseline** — the applied scalar correlates {{d4_r}} {{d4_ci}} with realised error at n_independent = {{d4_nind}}, beats the forecast-index counter at every horizon from h = 8 (the index is constant at h = 1) — though **not** the free `step-size` counter over whole trajectories at h = {{v2_diag_h}}, {{e7_step_r}} against {{e7_r_dis}}, a margin below the {{e7_mde_margin}} minimum detectable effect ({{e7_verdict}}: {{e7_verdict_gloss}}), which on {{x6_n_units}} shorter units at h = {{v2_deploy_h}} it does beat, {{x6_margin}} {{x6_ci}} (rule X6: **{{x6_reading}}**, Appendix L) — and survives {{d2r_ncontrols}} controls on forecast depth — the linear partial that keeps {{d2b_par_all}}, and four harder ones — plus a sixth on trajectory difficulty — the last giving {{a2_rdd}} {{a2_rdd_ci}} with both the rollout and the depth held constant (§5.6, M-45). **Weaker per-dimension**: at h = {{v2_diag_h}} the {{d1n_epi_npos_h368}}-of-{{d1n_epi_ndim_h368}} sign count gives a permutation P of {{perm_oos_epi_p_h368}} (out-of-sample) and {{perm_ins_epi_p_h368}} (in-sample), and no cell survives multiplicity correction (§5.6). **Not supported as a scale**: {{d1n_epi_ratio_h100}}× overconfident at h = {{v2_deploy_h}}, the method's own rollout length, and {{d1n_epi_ratio_h368}}× at the h = {{v2_diag_h}} diagnostic horizon; a per-horizon rescaling brings the released checkpoint near nominal, but on a model that has not seen the test episodes it does so in only {{d3x_own_epi_ok}} of {{d3x_own_epi_cells}} cells (§5.7) |
| Aleatoric "remains low, reflecting small stochasticity" (2504.16680v1 §3.2) | **yes** | **no quantitative figure.** "Low" is relative to the epistemic curve on the same axes of Fig. 2 (right); no absolute value, and no comparison against realised error | the observation holds; the explanation does not (§5.5) |
| Offline MBRL on real robots (2504.16680v1) | no | — | `[policy, hardware: offline MBRL on real robots]` not tested |
| Penalising rewards by ensemble disagreement improves the learned policy (2504.16680v1 Eq. 4–5, §4.1) — the follow-up's core method claim | no | Fig. 3 (right) plots epistemic uncertainty under three penalty weights during training; no numbers | `[policy: the core claim that penalising rewards by disagreement improves the learned policy]` **not tested.** We measure the penalty quantity itself — what it is (§5.1), how well it ranks error (§5.6), whether it is calibrated (§5.2) — but never train a policy with or without it. Our findings bound what the quantity *reports*, not what it *costs* (§7); a test of the cost needing no policy, rule X5, could not be run (Appendix D) |

**What each tested claim rests on.** The second table is §3.2's: one row per headline claim of this paper, with the section that owns it. Each row gives its own arena and number of independent units, its checkpoint, whether that arena is in-sample for the model measured, the verdict as its rule or analysis returned it, and whether it survives multiplicity correction. It is generated from the artifacts each claim is computed from (`results/evidence_summary.json`).

| claim (§) | arena (n_independent) | checkpoint | in-sample for the model measured? | verdict | survives multiplicity correction? |
|---|---|---|---|---|---|
{{evidence_table}}

---

**Versions.** We read {{ref1_read}} of the base paper and {{ref2_read}} of the follow-up; their current versions are {{ref1_current}} and {{ref2_current}}. The ensemble's rollout, the use of the ensemble mean, the shared trunk and the sentence on the learned variance are word for word the same in every version of the follow-up. What its second version added is the claim that uncertainty is effectively propagated over long horizons, which is therefore tested against accumulated error (§5.4). The base paper's sample-efficiency table is in its second version onward and not in the first. Both training tables moved between versions without changing their values; the follow-up was renamed ({{v4_name_v1}} to {{v4_name_v3}}) with the model unchanged. The workshop versions were not read.

**Rule X5.** The test of the penalty against the model's error in predicted return could not be run, because the released data do not record the velocity command its reward terms score against; supplement S12 gives the reason in full. It was never pre-registered as a rule, and nothing in the paper infers a command from achieved velocity.

## Appendix E — The pre-registration record

Every pre-registered rule with its plain name, identifier, committed hash, lead time and verbatim verdict, which supports §3.4's account of what was decided in advance; and the re-scoring of four rules under the released evaluation's timing.

§3.4's argument rests on decision rules committed to git before the data that tested them, and the
body names those rules by identifier. An identifier with no table behind it is either decoration
or an instruction to open a {{ledger_kb}} KB ledger, so here is the table. It is generated from
`FINDINGS_LEDGER.md` and `results/appendix_g_rules.json`; nothing in it is typed.

**Lead time** is the rule's commit timestamp subtracted from the commit that first held the data
it tested, never by a stored hash: the first rules' commits are found by *subject*, because the history was rewritten once and {{f1_n_moved_word}} of the commits Figure 3 cites changed hash (Data and code), and the later rules' by the commit that introduced their ledger heading. Positive means the rule was in git before the data
existed. This is the same computation Figure 3 plots. A rule whose data do not exist yet has neither a lead time nor a verdict, and Figure 3 leaves it out until they do.

| rule | what it governs | commit | lead time | tested by | verdict |
|---|---|---|---|---|---|
{{appG_table}}

`M-69`'s discharge commit was amended {{m69_amend_min}} minutes after it was created, so its lead time is {{m69_lead_author}} by that commit's author time and {{m69_lead_regen}} by its committer time. Both are positive, so the rule reached git before its data on either reading.

{{appG_n_rules}} rules, {{appG_n_lead}} with a computed lead time, of which
{{appG_n_positive}} are positive and {{appG_n_negative}} negative. **The negative one is
kept deliberately.** `S-12` withdraws the claim that the Task 3 duplication rule was
pre-registered; the control runs had finished before any threshold reached git. A table that
dropped it would be asserting exactly what the ledger retracts.

**`M-52` is in the table and that is deliberate.** It is the one mid-flight amendment to a
pre-registration in this project: `M-51` named a baseline that does not exist in the artifact it
named — the residual on the last teacher-forced step of the history window, which the rollout
helper never computes because it copies the history rather than predicting it — and `M-52` names
the replacement, committed before the replacement's statistic was computed. A table of pre-registrations that omitted the one amendment would be a highlights reel, so the table's rows are selected by each entry's `Status` line and their count is asserted against the set `scripts/ledger_check.py` reports.

**What each rule says, in its own committed words** is in the supplementary material, as
`docs/APPENDIX_G_RULES.md` — every rule's text unabridged, generated from the ledger by the same
script that generates this table. Quoting all {{appG_n_rules}} in full here would add pages to an
appendix whose job is to be checkable at a glance, and quoting them in part would ship
quotations ending mid-sentence. The table is the claim; the supplementary is the evidence.

---

**Rule X8.** Rule X8 re-scores four of our rules with the released evaluation's timing, through each rule's own evaluator, and all four keep their verdicts: for the configuration and baseline rules (M-74, M-75 and M-76, three seeds at {{iters_main}} iterations) and the A/B comparison (M-23's statistic, three seeds at {{iters_long}}), all on the held-out pair's {{mn_nind}} trajectories, it returns **{{x8_reading}}**, though {{x8_n_changed}} of their alongside readings change (Appendix E); this concerns our models, not the original's printed numbers.

Rule X8 was committed and pushed before its readings existed (ledger M-90; Appendix E gives its lead time) and is
discharged in M-93. It is exploratory and re-opens no rule. It re-scores rules M-74, M-75 and M-76 (their models at
{{iters_main}} iterations, three seeds each) and the A/B comparison at {{iters_long}} iterations (three seeds; M-23's
statistic and the by-horizon table's) with the released evaluation's timing, which pairs the prediction of each state
with the action before the one that produced it, through each rule's own evaluator and statistic. Every evaluator first
reproduces its committed artifact under the causal pairing. Our models were trained under the causal pairing, so this
asks whether any of our verdicts depends on the timing a reader of the released code would score them with; it says
nothing direct about the original papers' printed numbers. Every rule returns **{{x8_reading}}**, and {{x8_n_changed}}
of their alongside readings change: each changed cell is in bold below, and the by-horizon trend reading's change is quoted under the last table. The arena is the held-out pair, episodes {{h2h_episodes}},
{{mn_nind}} non-overlapping 400-step trajectories, n_independent = {{mn_nind}}, except where a row names the in-sample
arena ({{mn_nind_ins}}).

| reading | causal pairing, as committed | released pairing |
|---|---|---|
{{x8_tab_m74}}

**Rule M-74, the configuration sweep: nine configurations at {{iters_main}} iterations, three seeds each; arenas as
named in each row.** nRMSE as the rule's evaluator averages it, per trajectory. Bold, a reading that changes.

| reading | causal pairing, as committed | released pairing |
|---|---|---|
{{x8_tab_75}}

**Rule M-75, the baselines teacher-forced as the original trains them, at {{iters_main}} iterations, three seeds each;
arenas as named in each row.** The RSSM reads the window's first action row at its first filtering step, because the row
before it lies outside the window. Bold, a reading that changes.

| reading | causal pairing, as committed | released pairing |
|---|---|---|
{{x8_tab_76}}

**Rule M-76, the baselines trained autoregressively, at {{iters_main}} iterations, three seeds each; arenas as named in
each row.** The RSSM caveat of the previous table applies. Bold, a reading that changes.

| reading | causal pairing, as committed | released pairing |
|---|---|---|
{{x8_tab_ab}}

**The A/B comparison, Arm A against Arm B at {{iters_long}} iterations, three seeds each; arenas as named in each row,
the held-out pair otherwise.** Bold, a reading that changes. The by-horizon trend reading changes too, from "{{x8_trend_1}}"
under the causal pairing to "{{x8_trend_0}}" under the released one.

---

## Appendix F — Metrics and floors

Definitions of the metrics and floors (§3.3), the two nRMSE aggregations and the check on the coverage nominal.

**The floors (§3.3, Table 2).** Predicting the training mean forecasts every step by each dimension's mean over the arena's training-episode rows; holding the last state repeats the last history row; the seasonal floor repeats the history's last {{n10_period_default}} rows in order, a period of {{n10_period_s}} s fixed from the training episodes' joint-position autocorrelation before any held-out scoring ({{n10_period_min}} to {{n10_period_max}} rows across the folds).

**The metrics' formulas (§3.3).**

**Relative-L1** is the reference's own metric, reproduced in behaviour (`model_training.py:203`) so
that our numbers are comparable to the upstream's printed one. On config-normalised states, per
forecast step,

$${{v3_rel_l1}}$$

and the reported figure is the flat mean over trajectories and steps,

$${{v3_rel_l1_agg}}$$

with $t_0$ = `history_horizon` = {{v2_history}}: the first {{v2_history}} steps are teacher-forced
and excluded. The denominator is recomputed at every step as a 45-term sum in normalised space, so
it can pass through zero, which is why this metric goes non-finite on low-dimensional state groups
and why a second one exists.

**Normalised RMSE** fixes the denominator once, over the training episodes only:

$${{v3_nrmse}}$$

where the scale constant is

$${{v3_scale}}$$

computed once, stored in `results/step4_0a_results.json`, and never recomputed per step or derived
from held-out data. A value of one is not the training-mean floor (§3.3); the floors are scored directly, above. **The
aggregation is form 1**: pool the per-dimension mean squared errors, then divide, a ratio of means.
A mean of per-dimension ratios gives whichever dimension has the smallest scale unbounded leverage;
the rest of this appendix gives both forms, and supplement S32 the comparison the second one once inverted.

**Coverage at ±kσ** is the fraction of scalar (trajectory, forecast step, state dimension) triples
whose absolute realised error falls within k times the σ predicted for that same triple:

$${{v3_coverage}}$$

It is pooled over all three axes with equal weight per triple. It is **cumulative** over steps
1..h: coverage "at h" averages the whole rollout up to h and is not the value at step h, and every
horizon-indexed quantity in this paper follows the same convention. Because it is built from an
*absolute* error, $z \le k$ is the two-sided event, so the calibrated targets are
$\mathrm{erf}(k/\sqrt{2})$: **{{v3_cov_nominal1}}%** at ±1σ and **{{v3_cov_nominal2}}%** at ±2σ.
**That nominal is checked rather than assumed.** Rescaling each model's σ by the single constant that makes mean|error| / mean σ equal a calibrated Gaussian's {{m65_calib_ratio}} lands coverage above the rule's heavy-tail bound of {{m65_heavy_bound}}% in every one of {{m65_n_cells}} model × horizon cells, with {{m65_n_heavy}} below it ({{m65_n_adequate}} within its band around {{v3_cov_nominal1}}% and {{m65_n_over}} above it; `M-65`), so the shortfalls reported below are a property of the scale and not of the tail.

**The overconfidence factor** is how many times larger the typical realised error is than the
typical predicted σ:

$${{v3_rho}}$$

It too is a **ratio of means**, because a mean of ratios is unbounded whenever a single σ
approaches zero, which is exactly the regime §5.5 puts these models in. $\rho = 1$ is *not*
calibration: a calibrated Gaussian has mean|error| / σ = $\sqrt{2/\pi}$ = {{v3_rho_calibrated}}. So
$\rho$ is reported as a magnitude of miscalibration and coverage as the calibrated reading, and
both appear everywhere.

**The two aggregations.** §3.3 states that this paper uses **form 1**: pool the per-dimension mean squared errors across the
{{cal_rel_ndim}} state dimensions, then divide by the pooled scale — a ratio of means. **Form 2**
is the mean of per-dimension ratios.

The two differ because the state dimensions differ widely in scale. Form 2 gives
whichever dimension has the smallest denominator unbounded leverage over the aggregate, and a
dimension that is nearly constant in the training episodes has a very small denominator. Form 1
has no such lever: a dimension contributes in proportion to its share of the total squared error.

The definition in force throughout the paper is the one §3.3 gives. Nothing in §4.1, §5 or §6 uses
form 2.

---

## Appendix G — Rollout training against teacher forcing in detail

Detail behind §4.1: the hold-last floor, seeds, the short-horizon reading, the data budget, the long-horizon cells and their multiplicity.

Figure 4 shows the autoregressive-versus-teacher-forcing advantage by forecast horizon, the curve §4.1 refers to.

**Three passages of §4.1 in full.**

*Against a baseline, because neither number means anything without one.* The hold-last
floor, predicting that nothing changes, scores **{{a1_floor_h368}}** in the h = {{v2_diag_h}}
cell, and autoregressive training beats it by **{{a1_floor_over_A_h368}}×** there and by
{{a1_floor_over_A_h100}}× at h = {{v2_deploy_h}}. **Teacher forcing is
{{a1_B_over_floor_h368}}× worse than assuming nothing changes at all** at h = {{v2_diag_h}}, and
{{a1_B_over_floor_h100}}× worse at h = {{v2_deploy_h}}: the arm that reaches a lower training loss
predicts the future worse than a model that makes no prediction, at {{a1_B_worse_than_floor_at}} we measured on the 400-step unit, the sharper statement of what exposure bias costs here; but on M-64's shorter units, each {{m64_hist_rows}} + h rows long and non-overlapping ({{m64_units_list}} on these episodes), at the same checkpoint and on the same two episodes, it beats the floor at h = {{m64_B_beats_floor_at}} and loses to it only at the longest horizon those units reach, so that statement holds on the 400-step unit and not on the shorter one. **The floor is not a
weak baseline everywhere**: at {{a1_A_worse_than_floor_at}} it beats the autoregressive arm as well,
scoring {{a1_floor_h1}} at h = 1 against autoregressive training's {{a1_A_h1}}, the only horizon where the autoregressive arm loses to predicting no change on the 400-step unit; on the {{m64_h1_unit}}-row unit both arms beat the floor at h = 1 ({{m64_A_h1}} and {{m64_B_h1}} against {{m64_floor_h1}}). At 50 Hz one step is 20 ms and the state
barely moves, so that is what one should expect.

*Seeds, and what four trajectories can show.* Seed spread is not symmetric between the arms: Arm A
ranges {{d1_A_lo}}–{{d1_A_hi}} across seeds ({{d1_A_relsd}}% relative), Arm B
{{d1_B_lo}}–{{d1_B_hi}} ({{d1_B_relsd}}%). Teacher forcing is more than twice as variable across
seeds as autoregressive training at this horizon, so a single-seed comparison of these two arms is
unreliable. For a single seed the bootstrap over trajectories gives the 95% interval
[{{m23_ci_lo}}, {{m23_ci_hi}}] on n = {{m23_nind}} independent trajectories; by the n = {{m23_nind}}
caveat of §3 its tails move in steps of {{c3_quant}}%, so it corroborates the sign test rather
than being the primary evidence. The four per-trajectory gaps behind §4.1's three-seed table (Arm B minus Arm A, three seeds pooled, at h = {{v2_diag_h}}) are **{{a1_gap_traj_h368}}**. All
{{a1_gap_traj_n_positive_h368}} of {{a1_gap_traj_n_h368}} are positive, the direction of the sign test's {{c3_sign_pos}} of {{c3_sign_n}} episodes,
but one trajectory carries {{a1_gap_traj_max_h368}} against a smallest of
{{a1_gap_traj_min_h368}}, which no interval on four units shows. At h = {{v2_deploy_h}} the four
are {{a1_gap_traj_h100}}; this appendix notes where other sections store theirs.

**What is small, and where it resolves.** At h = 8, the horizon the model is trained on, the
advantage is small, and it resolves only with the longer training and all {{d1_seeds}} seeds. §4.1's by-horizon table, at {{iters_long}} iterations with {{d1_seeds}} seeds pooled, gives an h = 8 gap of {{a1_gap_h8}}
{{a1_gap_ci_h8}}, which excludes zero, a factor of {{a1_ratio_h8}}×. The single seed the rule was
run on (seed {{m23_seed}}) gives an h = 8 gap of {{m23_h8_gap}} at the same {{iters_long}}-iteration checkpoint,
and its interval {{m23_h8_excl}}. At the {{bu_ckpts}}-iteration checkpoints, with all {{d1_seeds}} seeds
pooled, the out-of-sample gap excludes zero in **{{ab_short_excl}} of {{ab_short_cells}}** h = 8 cells (both
trajectory lengths crossed with both checkpoints). An earlier rule of ours, anchored at h = 8 and
evaluated at those same checkpoints (rule M-16, Appendix E), returned **{{m16_verdict}}**.
**The advantage is small at the training horizon and large beyond it.**

**The data budget (§3.2).** §3.2 keeps two sentences of the following.

The base paper's headline is a sample-efficiency result: policies transfer to hardware from {{c2_ref}} state transitions of world-model pretraining against ~250M for the model-free baseline (Table I). That is a claim about policy learning and hardware, which we cannot test, but its *world-model* half is a quantity we can count exactly.

**Our arms consume {{c2_trans}} distinct state transitions**: the {{c2_rows}} rows of the eight training episodes less one per episode ({{c2_bounds}} of them), since an episode's first row has no predecessor, a transition being a consecutive pair of rows inside one episode. It is deliberately not the {{c2_windows}} training windows, which overlap almost completely (consecutive {{win_len}}-row windows start one row apart), nor the {{c2_draws}} window draws a {{iters_main}}-iteration run makes, which resample the same data with replacement. Against the reference's {{c2_ref}}, that is **{{c2_ratio}}× less data, {{c2_pct}}% of its world-model budget**.

A dynamics model trained on {{c2_pct}}% of the reference's data still reproduces the training result, {{d1_ratio}}× at h = {{v2_diag_h}} and {{d1_ratio_h100}}× at h = {{v2_deploy_h}} over {{d1_seeds}} seeds (the rule ran on seed {{m23_seed}}), and still beats the hold-last floor, by {{floor_over_A}}× and {{a1_floor_over_A_h100}}× at those two horizons. That is what this paper can add to the sample-efficiency question without training a policy.

**Three limits.** It is not a reproduction of the {{c2_ref}}-against-250M comparison, which is about policy learning. It says nothing about whether a policy trained inside our model would transfer to hardware, or anywhere. And our model is evaluated on the narrow distribution it trained on (one robot, one gait, one terrain, velocity commands from a single bounded box), where the reference's {{c2_ref}} transitions span considerably more; a smaller data budget buys less than it appears to when the evaluation distribution shrinks with it.

## Appendix H — Configuration and architecture claims in detail

Detail behind §4.2 and §4.3: the baselines and their diverged rows, the RSSM diagnostic, the reimplementation beside the released checkpoint, and the settings sweep at equal compute.

**Two passages of §4.3 in full.**

On the in-sample arena's {{mn_nind_ins}} trajectories, with nRMSE pooled as §3.3 defines it (computed afterwards, post hoc; ledger R-77), {{n2_n_changed_word}} readings differ from the per-trajectory average the rules' evaluator used. Teacher-forced, at h = 1 all three baselines are ahead of RWM: D, signed as the rules sign it (positive favours RWM), is {{n2_m75_D_mlp}} {{n2_m75_ci_mlp}} for the MLP, {{n2_m75_D_rssm}} {{n2_m75_ci_rssm}} for the RSSM and {{n2_m75_D_transformer}} {{n2_m75_ci_transformer}} for the transformer, so M-75's reading there is {{n2_m75_pooled}} where the average gave {{n2_m75_committed}}: the same one-step lead for teacher forcing as §4.1's. Trained autoregressively, the MLP's deficit at h = {{v2_deploy_h}} is no longer resolved ({{n2_m76_D_mlp}} {{n2_m76_ci_mlp}}), so M-76's reading there is {{n2_m76_pooled}} where the average gave {{n2_m76_committed}}. Neither changes a verdict; both rules govern at h = {{v2_diag_h}} on relative-L1.

**Our RSSM is not an informative comparison.** Teacher-forced, it is the most accurate of this section's models one
step ahead, {{h2h_bl_rssm_tf_l1_h1}} against RWM's {{h2h_armA_l1_h1}} and the floor's {{x1_floor_h1}},
though not resolvably, and it has collapsed open-loop by h = 32, where its {{x1_tf_mode_h32}} is above
the floor's {{x1_floor_h32}}. The original adds that an RSSM trained autoregressively performs
comparably to RWM; ours does not, {{h2h_bl_rssm_ar_l1_h368}} against RWM's {{bl_rwm_l1_h368}} at
h = {{v2_diag_h}}. A diagnostic committed before its readings existed (rule X1, ledger M-80;
exploratory, it re-opens neither rule) asks why. Its Part A reads the forecast differently, feeding
the prior's expected or sampled latent in place of its most likely one: the error at h = 32 falls to
{{x1_tf_exp_h32}} and {{x1_tf_samp_h32}}, still above the floor, so it returns **{{x1_reading_a}}**
(M-81). Its Part B is descriptive: over the history, the teacher-forced RSSM's one-step error from its
prior is {{x1b_tf_ratio_lo}}× to {{x1b_tf_ratio_hi}}× its error from its posterior at the same
recurrent state (the autoregressive one's at most {{x1b_ar_ratio_hi}}×), with {{x1b_kl_lo}} to
{{x1b_kl_hi}} nats of KL divergence between them per step. {{rssm_partc_sentence}} The failure may
still be our RSSM rather than the architecture: Table S7's latent is ambiguous, we read it in
DreamerV2's naming (`BASELINE_SPECS.md`, the RSSM rows), and X1 tried only the two settings above, on one seed, neither of them PlaNet's latent overshooting (Hafner et al., ICML 2019), which trains the prior's multi-step predictions in latent space and which PlaNet's own final RSSM agent did not need. So the architecture claim rests on the MLP and the transformer.

**Teacher forcing's two definitions (§4, §4.1).** §4 and §4.1 each keep a sentence of the following.

From §4, on the original's heatmap: For the teacher-forced {{mn_n1_label}}
it prints {{orig_tf_e_n1}} against {{orig_tf_e_centre}} at the centre, {{orig_tf_ratio}}× worse, on
evaluation data and at a horizon it does not state; our sweep's {{mn_n1_label}} is
{{mn_tf_ratio}}× worse on relative-L1 at h = {{v2_diag_h}} and {{iters_main}} iterations. Our {{d1_ratio}}×, at {{iters_long}}, uses a different definition of teacher forcing
(`docs/presubmission/ORIGINAL_SPECS.md` §2); the next paragraph relates the two.

From §4.1: Arm B predicts each of the window's {{win_fore}} forecast targets from
true inputs, where the original's teacher forcing is N = 1; the sweep's {{mn_n1_label}}, trained that way, is
{{mn_tf_ratio}}× worse than the centre at h = {{v2_diag_h}} at {{iters_main}} iterations (§4.2), so the direction
holds under both definitions.

**The diverged baseline rows (§4.3).** † marks a diverged row, one where any seed's mean relative-L1 at h = {{v2_diag_h}} exceeds
{{div_factor}} times the hold-last floor's (`results/pooled_nrmse_rescore.json`, post hoc). Run-away
rollouts dominate those {{div_n_word}} rows' means; per seed they are {{div_per_seed}}. No verdict
depends on that magnitude, only on the sign: each such row's {{mn_nind}} per-trajectory differences from
RWM are all positive, so every bootstrap resample favours RWM whatever their size.

**The long-horizon cells.** At long horizons §4.1's pattern is consistent across the design. Under the cluster bootstrap, the
out-of-sample gap excludes zero in **{{ab_long_excl}} of {{ab_long_cells}}** long-horizon cells,
both trajectory lengths crossed with the {{bu_ckpts}}-iteration checkpoints. These figures are
relative-L1; the nRMSE aggregation is reported separately and does not change the direction.

**Multiplicity.** Those {{ab_long_cells}} cells sit in a family of {{c3_family}} out-of-sample
comparisons. All {{c3_bonf_excl}} of {{c3_long}} still exclude zero at a Bonferroni level of
0.05/{{c3_family}}, and Holm–Bonferroni rejects **{{c3_holm_rejected}} of {{c3_long}}**. §4.1's sign
test is unaffected either way.

**How good the reimplementation is as a model, next to the artifact it reimplements.**
§4.1's tables compare two training rules with each other and §5.2's compares calibration, so
neither puts the released checkpoint and our arms side by side on absolute accuracy. Both
aggregations, for these models and for §4.3's architecture baselines, on one arena:

| model | nRMSE h = 1 | rel-L1 h = 1 | nRMSE h = 8 | rel-L1 h = 8 | nRMSE h = {{v2_deploy_h}} | rel-L1 h = {{v2_deploy_h}} | nRMSE h = {{v2_diag_h}} | rel-L1 h = {{v2_diag_h}} |
|---|---|---|---|---|---|---|---|---|
| released checkpoint | {{h2h_released_nrmse_h1}} | {{h2h_released_l1_h1}} | {{h2h_released_nrmse_h8}} | {{h2h_released_l1_h8}} | {{h2h_released_nrmse_h100}} | {{h2h_released_l1_h100}} | {{h2h_released_nrmse_h368}} | {{h2h_released_l1_h368}} |
| Arm A — autoregressive, faithful MSE | {{h2h_armA_nrmse_h1}} | {{h2h_armA_l1_h1}} | {{h2h_armA_nrmse_h8}} | {{h2h_armA_l1_h8}} | {{h2h_armA_nrmse_h100}} | {{h2h_armA_l1_h100}} | {{h2h_armA_nrmse_h368}} | {{h2h_armA_l1_h368}} |
| Arm A — autoregressive, `gaussian_nll` | {{h2h_armAnll_nrmse_h1}} | {{h2h_armAnll_l1_h1}} | {{h2h_armAnll_nrmse_h8}} | {{h2h_armAnll_l1_h8}} | {{h2h_armAnll_nrmse_h100}} | {{h2h_armAnll_l1_h100}} | {{h2h_armAnll_nrmse_h368}} | {{h2h_armAnll_l1_h368}} |
| Arm B — teacher-forced | {{h2h_armB_nrmse_h1}} | {{h2h_armB_l1_h1}} | {{h2h_armB_nrmse_h8}} | {{h2h_armB_l1_h8}} | {{h2h_armB_nrmse_h100}} | {{h2h_armB_l1_h100}} | {{h2h_armB_nrmse_h368}} | {{h2h_armB_l1_h368}} |
| {{h2h_bl_mlp_tf_label}} | {{h2h_bl_mlp_tf_nrmse_h1}} | {{h2h_bl_mlp_tf_l1_h1}} | {{h2h_bl_mlp_tf_nrmse_h8}} | {{h2h_bl_mlp_tf_l1_h8}} | {{h2h_bl_mlp_tf_nrmse_h100}} | {{h2h_bl_mlp_tf_l1_h100}} | {{h2h_bl_mlp_tf_nrmse_h368}} | {{h2h_bl_mlp_tf_l1_h368}} |
| {{h2h_bl_mlp_ar_label}} | {{h2h_bl_mlp_ar_nrmse_h1}} | {{h2h_bl_mlp_ar_l1_h1}} | {{h2h_bl_mlp_ar_nrmse_h8}} | {{h2h_bl_mlp_ar_l1_h8}} | {{h2h_bl_mlp_ar_nrmse_h100}} | {{h2h_bl_mlp_ar_l1_h100}} | {{h2h_bl_mlp_ar_nrmse_h368}} | {{h2h_bl_mlp_ar_l1_h368}} |
| {{h2h_bl_rssm_tf_label}} | {{h2h_bl_rssm_tf_nrmse_h1}} | {{h2h_bl_rssm_tf_l1_h1}} | {{h2h_bl_rssm_tf_nrmse_h8}} | {{h2h_bl_rssm_tf_l1_h8}} | {{h2h_bl_rssm_tf_nrmse_h100}} | {{h2h_bl_rssm_tf_l1_h100}} | {{h2h_bl_rssm_tf_nrmse_h368}} | {{h2h_bl_rssm_tf_l1_h368}} |
| {{h2h_bl_rssm_ar_label}} | {{h2h_bl_rssm_ar_nrmse_h1}} | {{h2h_bl_rssm_ar_l1_h1}} | {{h2h_bl_rssm_ar_nrmse_h8}} | {{h2h_bl_rssm_ar_l1_h8}} | {{h2h_bl_rssm_ar_nrmse_h100}} | {{h2h_bl_rssm_ar_l1_h100}} | {{h2h_bl_rssm_ar_nrmse_h368}} | {{h2h_bl_rssm_ar_l1_h368}} |
| {{h2h_bl_transformer_tf_label}} | {{h2h_bl_transformer_tf_nrmse_h1}} | {{h2h_bl_transformer_tf_l1_h1}} | {{h2h_bl_transformer_tf_nrmse_h8}} | {{h2h_bl_transformer_tf_l1_h8}} | {{h2h_bl_transformer_tf_nrmse_h100}} | {{h2h_bl_transformer_tf_l1_h100}} | {{h2h_bl_transformer_tf_nrmse_h368}} | {{h2h_bl_transformer_tf_l1_h368}} |
| {{h2h_bl_transformer_ar_label}} | {{h2h_bl_transformer_ar_nrmse_h1}} | {{h2h_bl_transformer_ar_l1_h1}} | {{h2h_bl_transformer_ar_nrmse_h8}} | {{h2h_bl_transformer_ar_l1_h8}} | {{h2h_bl_transformer_ar_nrmse_h100}} | {{h2h_bl_transformer_ar_l1_h100}} | {{h2h_bl_transformer_ar_nrmse_h368}} | {{h2h_bl_transformer_ar_l1_h368}} |
| hold-last floor | {{h2h_floor_nrmse_h1}} | {{h2h_floor_l1_h1}} | {{h2h_floor_nrmse_h8}} | {{h2h_floor_l1_h8}} | {{h2h_floor_nrmse_h100}} | {{h2h_floor_l1_h100}} | {{h2h_floor_nrmse_h368}} | {{h2h_floor_l1_h368}} |

**Arena, stated once for the whole table: {{h2h_arena}}, episodes {{h2h_episodes}},
{{h2h_ntraj}} non-overlapping {{h2h_unit}}-step trajectories, n_independent = {{h2h_nind}}; possibly in-sample for the released checkpoint (§3.2).**
Arm rows are the mean over {{h2h_nseeds}} seeds at {{iters_main}} training iterations (the `{{h2h_arm_ckpt}}` checkpoint), with
per-seed values in `results/head_to_head_accuracy.json`; nRMSE is form 1 (§3.3), and both metrics
are cumulative over forecast steps 1..h. Every RWM row is read from the stored rollouts behind §5.2's
calibration tables, so no model is run to build it. The architecture-baseline rows (§4.3) come from
their own evaluator on the same four trajectories, whose relative-L1 reproduces the Arm A row
exactly; their nRMSE is pooled as §3.3 defines it, recomputed afterwards with the same evaluator
(post hoc, `results/pooled_nrmse_rescore.json`), and † marks a diverged row (§4.3). **This table is at {{iters_main}} iterations and §4.1's by-horizon table at {{iters_long}}**, which is why Arm A's relative-L1 at h = {{v2_diag_h}} reads {{h2h_armA_l1_h368}} here and {{a1_A_h368}} there: the same arm, trained longer.

Both metrics put the released checkpoint first at {{h2h_released_sweeps_at}}, they name
different leaders at {{h2h_split_at}}, and at {{h2h_armA_sweeps_at}} both put an Arm A variant
ahead of it: the reimplementation is behind the artifact it reimplements at short horizons and
ahead of it at the longest horizon we measure. That reading flatters the released checkpoint, because the split is ours: the arena is
out-of-sample for our arms and in-sample for it, which trained on all
{{h2h_ckpt_neps_word}} episodes (the in-sample caveat of §3).

*Stored per-trajectory values elsewhere.* §5.3's and supplementary S2's paired contrasts at §4.1's n = {{m23_nind}} store their four
per-trajectory values in `results/r2_independent_ensemble.json` and
`results/m49_capacity_matched.json`; §5.2's two held-out tables, at n_independent = {{b2_nind}},
give intervals only, coarse for the same reason (the n = {{m23_nind}} caveat of §3).

**Rule X3, fold by fold (§4.1).** Rule X3 was committed and pushed before any of its runs existed (ledger M-86; Appendix E gives its lead time) and is discharged in M-94. It is exploratory and re-opens no rule: rule M-23 stands. The gap is Arm B's seed-mean relative-L1 minus Arm A's at h = {{v2_diag_h}}. Each fold's interval is exact over all {{boot_n_exact4}} ordered resamples of its trajectories; the pooled one is M-23's three-seed bootstrap, {{boot_n_mc}} draws (seed 0), whole trajectories, every seed carried.

| fold (episodes held out) | trajectories | gap at h = {{v2_diag_h}} [95% interval] | each episode's mean gap |
|---|---|---|---|
{{x3_fold_table}}

**Arena: each fold's held-out pair, out-of-sample for both arms, {{a1_nind}} non-overlapping 400-step trajectories per fold and {{x3_n}} pooled (n_independent = {{x3_n}}). Checkpoints: Arm A and Arm B at {{iters_main}} iterations, {{d1_seeds}} seeds per arm per fold.** Bold, the reading, **{{x3_reading}}**. The per-episode sign test is part of the rule and carries no verdict of its own: {{x3_eps_pos}} of {{x3_n_eps}} episodes positive, exact two-sided P = {{x3_p}}. Alongside: at h = {{v2_deploy_h}} the pooled gap is {{x3_gap_h100}} {{x3_ci_h100}}, and Arm B's mean error is {{x3_ratio_h368}}× Arm A's at h = {{v2_diag_h}}. The folds are fixed, not drawn: two of the new ones hold both their episodes from the same speed half, unlike §4.1's stratified fold.

---

Post hoc (ledger R-78; `results/mn_compute_matched.json`); it re-opens no rule, and rule M-74's verdict,
{{mn_verdict}}, stands as a statement about the {{iters_main}}-iteration budget (§4.2). Each row sets one of the
{{mn_n_better_word}} configurations that beat the centre at {{iters_main}} iterations against the centre trained to
{{iters_main}}, {{n3_k_mid}} or {{iters_long}} iterations: {{n3_appU_nrows_word}} rows of {{n3_n_readings_word}}
readings each. A longer forecast costs more per iteration than the centre, a shorter history less, so the centre's
longer runs ask whether a configuration's win survives giving the centre at least as much training computation.

**How §4.2's alongside readings were computed, and how far its runs had trained.** §4.2 keeps a
sentence of each.

The rules' evaluator averaged nRMSE per trajectory, where §3.3 pools it. The nRMSE readings quoted
alongside the rules here and in §4.3 are pooled, recomputed afterwards (post hoc,
`results/pooled_nrmse_alongside.json`), and, for this section's rule (M-74), return the same verdicts as the averaged ones (Appendix E gives the {{n2_n_changed_word}} readings of its rules that differ).

All {{tail_n}} runs at {{iters_main}} iterations,
the sweep's, the baselines' and both arms', are still lowering their training loss at the end, with slopes
from {{tail_slope_lo}} to {{tail_slope_hi}} per thousand iterations (`results/training_tail_slopes.json`,
post hoc), so the ranking is at this budget, not at convergence, and it changes with training length (Appendix H).

**§4.2's reading, in full.** §4.2 keeps three sentences of it.

**Accuracy at equal compute (post hoc; ledger R-78).** A longer training forecast costs more per iteration, {{n3_cost_M32_N16}}× the centre's for {{n3_lf_label}} and {{n3_cost_M32_N32}}× for {{mn_best_config}}; the shorter histories that win cost less, {{n3_cost_M8_N8}}× for {{n3_sh_label_M8_N8}} and {{n3_cost_M2_N8}}× for {{n3_sh_label_M2_N8}} (`results/mn_compute_matched.json`; the table below gives every reading, signed as in §4.2's table). The shorter histories win on all {{n3_n_readings_word}} readings at {{iters_main}} iterations while using well under half the centre's computation, so that part of the verdict needs no compute correction. The longer forecasts' wins do. Trained to {{n3_k_mid}} iterations, the centre has had {{n3_best_over_mid}}× the computation of {{mn_best_config}}, and the readings split: {{mn_best_config}} is still ahead on the held-out pair at h = {{v2_diag_h}} ({{n3_best_D_mid}} {{n3_best_ci_mid}}), the centre is ahead on the in-sample arena at h = {{v2_deploy_h}} ({{n3_best_ins_D_mid_h100}} {{n3_best_ins_ci_mid_h100}}), and the other two are not resolved. At {{iters_long}} iterations, {{n3_best_over_long}}× the computation, the centre is ahead on both in-sample readings and neither held-out difference is resolved. Trained that long, it also passes both shorter histories on {{n3_sh_long_nread_word}} of the {{n3_n_readings_word}} readings: on the held-out pair at h = {{v2_diag_h}}, {{n3_sh_label_M2_N8}} by {{n3_sh_D_long_M2_N8}} {{n3_sh_ci_long_M2_N8}} and {{n3_sh_label_M8_N8}} by {{n3_sh_D_long_M8_N8}} {{n3_sh_ci_long_M8_N8}}, with {{n3_sh_over_long_M2_N8}}× and {{n3_sh_over_long_M8_N8}}× their computation, and on both in-sample readings; on the held-out pair at h = {{v2_deploy_h}} neither difference is resolved. Which setting is most accurate therefore depends on how long each is trained. None of this re-opens rule M-74.

| configuration (cost per iteration ÷ the centre's) | centre trained to (iterations) | compute ratio (centre's total ÷ configuration's) | h = {{v2_deploy_h}}, held-out pair ({{mn_nind}}) | h = {{v2_deploy_h}}, in-sample ({{mn_nind_ins}}) | h = {{v2_diag_h}}, held-out pair ({{mn_nind}}) | h = {{v2_diag_h}}, in-sample ({{mn_nind_ins}}) |
|---|---|---|---|---|---|---|
{{n3_appU_table}}

**Arenas: the held-out pair (episodes {{h2h_episodes}}, {{mn_nind}} non-overlapping {{h2h_unit}}-step trajectories,
n_independent = {{mn_nind}}) and the in-sample arena (the training episodes' {{mn_nind_ins}} non-overlapping
{{h2h_unit}}-step trajectories, n_independent = {{mn_nind_ins}}). Checkpoints: each configuration at {{iters_main}}
iterations, the centre at the iterations in the second column; three seeds each.** Each cell is D, the configuration's
relative-L1 minus the centre's, the mean over trajectories of the three-seed means, with its 95% interval: exact over
all {{boot_n_exact4}} ordered resamples on the held-out pair, {{boot_n_mc}} Monte Carlo resamples (seed 0) in-sample. Negative favours the
configuration, so every reading here is signed as in §4.2's table; bold where the interval excludes zero. Cost per
iteration is steady training time per iteration, timed
without contention; the compute ratio is the centre's total training computation over the configuration's.

## Appendix I — Calibration in detail

Calibration behind §5.2 and §5.6: every horizon, the held-out-pair version, the ensemble-5 arms, the checks on how the numbers are read, and the per-dimension tests.

**Scope of the per-member readings.** {{x9_scope}}

Figure 5 shows the models' calibration on the held-out pair, the measurement §5.2 reports.

**The held-out-pair version (§5.2).** §5.2 states that restricting the checkpoint to the held-out pair would buy no independence and cost four fifths of the sample; that version, at n_independent = {{b2_nind}} 400-step trajectories, is in the supplementary material (`results/task_b2_epistemic.json`). Its epistemic column agrees in direction with this one at all {{agree_epi}} of {{agree_nh}} horizons; its aleatoric column agrees at {{agree_alea}} of {{agree_nh}} and differs at {{agree_alea_dis}}, and the aleatoric σ is in any case {{d1n_alea_ratio_h1}}× (h = 1) to {{d1n_alea_ratio_h368}}× (h = {{v2_diag_h}}) too small for its ordering to be the interesting quantity.

**§5.2's four-model table.** On the held-out pair, the four models stood as follows.

| model | mean \|error\| / mean σ, whole {{v2_diag_h}}-step rollout | coverage at ±1σ, h=1 | coverage at ±1σ, h={{v2_deploy_h}} |
|---|---|---|---|
| faithful Arm A (sampled MSE) | {{cal_faithA_ratio}}× [{{cal_faithA_ratio_ci}}] | {{cal_faithA_cov1}}% [{{cal_faithA_cov1_ci}}] | {{cal_faithA_cov100}}% [{{cal_faithA_cov100_ci}}] |
| corrected Arm A (`gaussian_nll`) | {{cal_nll_ratio}}× [{{cal_nll_ratio_ci}}] | {{cal_nll_cov1}}% [{{cal_nll_cov1_ci}}] | {{cal_nll_cov100}}% [{{cal_nll_cov100_ci}}] |
| teacher-forced Arm B | {{cal_armB_ratio}}× [{{cal_armB_ratio_ci}}] | {{cal_armB_cov1}}% [{{cal_armB_cov1_ci}}] | {{cal_armB_cov100}}% [{{cal_armB_cov100_ci}}] |
| released checkpoint | {{cal_rel_ratio}}× [{{cal_rel_ratio_ci}}] | {{cal_rel_cov1}}% [{{cal_rel_cov1_ci}}] | {{cal_rel_cov100}}% [{{cal_rel_cov100_ci}}] |

*Our arms are at {{iters_main}} training iterations; the released checkpoint is as released. Every cell carries a 95% interval from a cluster bootstrap over whole trajectories, n_independent = {{b2_nind}}, quantised as the n = {{b2_nind}} caveat of §3 describes; where three seeds contribute, seeds are pooled inside each draw rather than resampled, because seeds are not trajectories (§3.4).*

**All four rows are the held-out pair** — the two episodes withheld from our own arms, n_independent = {{b2_nind}} 400-step trajectories — because that is the only arena on which our arms can be scored fairly. On the aleatoric head every model is overconfident by between one and four orders of magnitude (Figure 5); that is the quantity §5.1 shows the method discards. The released checkpoint's {{cal_rel_ratio}}× is its whole {{v2_diag_h}}-step rollout on those same {{b2_nind}} trajectories, for comparability with the arms; its best-sampled figure is the {{d1n_alea_ratio_h100}}× below, cumulative to h = {{v2_deploy_h}} at n_independent = {{d1n_nind}}. **Both are correct, on a different arena and a different horizon**, and neither is out-of-sample for that checkpoint (the in-sample caveat of §3).

**§5.2's released-checkpoint table at every horizon.** Over all {{d1n_eps}} episodes, n_independent = {{d1n_nind}} non-overlapping 400-step trajectories, the released checkpoint as released:

| h | aleatoric err/σ [95% CI] | aleatoric ±1σ | epistemic err/σ [95% CI] | epistemic ±1σ [95% CI] | epistemic ±2σ | dims r>0 | permutation P |
|---|---|---|---|---|---|---|---|
| 1 | {{d1n_alea_ratio_h1}}× [{{d1n_alea_ratio_ci_h1}}] | {{d1n_alea_cov1_h1}}% | **{{d1n_epi_ratio_h1}}×** [{{d1n_epi_ratio_ci_h1}}] | {{d1n_epi_cov1_h1}}% [{{d1n_epi_cov1_ci_h1}}] | {{d1n_epi_cov2_h1}}% | {{d1n_epi_npos_h1}}/{{d1n_epi_ndim_h1}} | {{perm_all_epi_p_h1}} |
| 8 | {{d1n_alea_ratio_h8}}× [{{d1n_alea_ratio_ci_h8}}] | {{d1n_alea_cov1_h8}}% | {{d1n_epi_ratio_h8}}× [{{d1n_epi_ratio_ci_h8}}] | {{d1n_epi_cov1_h8}}% [{{d1n_epi_cov1_ci_h8}}] | {{d1n_epi_cov2_h8}}% | {{d1n_epi_npos_h8}}/{{d1n_epi_ndim_h8}} | {{perm_all_epi_p_h8}} |
| 32 | {{d1n_alea_ratio_h32}}× [{{d1n_alea_ratio_ci_h32}}] | {{d1n_alea_cov1_h32}}% | {{d1n_epi_ratio_h32}}× [{{d1n_epi_ratio_ci_h32}}] | {{d1n_epi_cov1_h32}}% [{{d1n_epi_cov1_ci_h32}}] | {{d1n_epi_cov2_h32}}% | {{d1n_epi_npos_h32}}/{{d1n_epi_ndim_h32}} | {{perm_all_epi_p_h32}} |
| **{{v2_deploy_h}}** | {{d1n_alea_ratio_h100}}× [{{d1n_alea_ratio_ci_h100}}] | {{d1n_alea_cov1_h100}}% | **{{d1n_epi_ratio_h100}}×** [{{d1n_epi_ratio_ci_h100}}] | {{d1n_epi_cov1_h100}}% [{{d1n_epi_cov1_ci_h100}}] | {{d1n_epi_cov2_h100}}% | {{d1n_epi_npos_h100}}/{{d1n_epi_ndim_h100}} | {{perm_all_epi_p_h100}} |
| 128 | {{d1n_alea_ratio_h128}}× [{{d1n_alea_ratio_ci_h128}}] | {{d1n_alea_cov1_h128}}% | {{d1n_epi_ratio_h128}}× [{{d1n_epi_ratio_ci_h128}}] | {{d1n_epi_cov1_h128}}% [{{d1n_epi_cov1_ci_h128}}] | {{d1n_epi_cov2_h128}}% | {{d1n_epi_npos_h128}}/{{d1n_epi_ndim_h128}} | {{perm_all_epi_p_h128}} |
| 368 | {{d1n_alea_ratio_h368}}× [{{d1n_alea_ratio_ci_h368}}] | {{d1n_alea_cov1_h368}}% | {{d1n_epi_ratio_h368}}× [{{d1n_epi_ratio_ci_h368}}] | {{d1n_epi_cov1_h368}}% [{{d1n_epi_cov1_ci_h368}}] | {{d1n_epi_cov2_h368}}% | {{d1n_epi_npos_h368}}/{{d1n_epi_ndim_h368}} | {{perm_all_epi_p_h368}} |

**The larger sample changes one thing materially.** At n_independent = {{b2_nind}} the epistemic ordering looked like chance at short horizon, {{b2_epi_npos_h1}} of {{b2_epi_ndim_h1}} dimensions at h=1. At n_independent = {{d1n_nind}} it is {{d1n_epi_npos_h1}} of {{d1n_epi_ndim_h1}} at h=1, with mean r = {{d1n_epi_r_h1}}, the *strongest* mean correlation of any horizon, and the in-sample permutation test agrees (Appendix C). The short-horizon "chance" result was an artifact of four trajectories, not a property of the model.

**The ensemble-5 arms (§5.2).** **The released checkpoint is no longer the only ensemble measured.** Three Arm A arms at ensemble size 5 (§5.6, {{e5_seeds}} seeds, out-of-sample, n_independent = {{e5_nind}} 400-step trajectories, {{iters_main}} training iterations) give, averaged over seeds:

| h | epistemic err/σ [95% CI] | ±1σ [95% CI] | ±2σ | dims r>0 |
|---|---|---|---|---|
| 1 | {{e5_ratio_h1}}× [{{e5_ratio_ci_h1}}] | {{e5_cov1_h1}}% [{{e5_cov1_ci_h1}}] | {{e5_cov2_h1}}% | {{e5_npos_h1}}/45 |
| 8 | {{e5_ratio_h8}}× [{{e5_ratio_ci_h8}}] | {{e5_cov1_h8}}% [{{e5_cov1_ci_h8}}] | {{e5_cov2_h8}}% | {{e5_npos_h8}}/45 |
| 32 | {{e5_ratio_h32}}× [{{e5_ratio_ci_h32}}] | {{e5_cov1_h32}}% [{{e5_cov1_ci_h32}}] | {{e5_cov2_h32}}% | {{e5_npos_h32}}/45 |
| 100 | **{{e5_ratio_h100}}×** [{{e5_ratio_ci_h100}}] | {{e5_cov1_h100}}% [{{e5_cov1_ci_h100}}] | {{e5_cov2_h100}}% | {{e5_npos_h100}}/45 |
| 128 | {{e5_ratio_h128}}× [{{e5_ratio_ci_h128}}] | {{e5_cov1_h128}}% [{{e5_cov1_ci_h128}}] | {{e5_cov2_h128}}% | {{e5_npos_h128}}/45 |
| 368 | **{{e5_ratio_h368}}×** [{{e5_ratio_ci_h368}}] | {{e5_cov1_h368}}% [{{e5_cov1_ci_h368}}] | {{e5_cov2_h368}}% | {{e5_npos_h368}}/45 |

Our arms are **better calibrated than the released checkpoint and fail the same way**: {{e5_ratio_h100}}× overconfident at h = {{v2_deploy_h}} against its {{b2_epi_ratio_h100}}× on the same held-out pair ({{d1n_epi_ratio_h100}}× over all ten episodes), with {{e5_cov1_h100}}% coverage where a calibrated Gaussian gives {{v3_cov_nominal1}}%. §5.3 establishes that the two are the same architecture in the respect that matters here, so this is a comparison of like with like. Being closer to calibrated is not being calibrated.

**Two pre-registered checks on how §5.2's numbers are read.** The first (rule M-62, Appendix E) asks whether any verdict depends on resampling 400-step trajectories rather than whole episodes, which two trajectories share. It returns **{{m62_verdict}}**: in the one arena with power at that level, all ten episodes (n = {{m62_n_traj}} falling to {{m62_n_ep}}), the pooled correlation's interval widens by {{m62_width_pct}}% and the double-demeaned one's width changes by a factor of {{m62_rdd_width_ratio}}, and neither crosses zero. The other {{m62_n_uninformative}} cells it names are out-of-sample, where an episode bootstrap has n = {{m62_n_ep_oos}} and three distinct resamples, or, for the per-horizon multiplier cell, one episode per direction and no interval at all; the rule said so in advance, and they are reported as uninformative rather than as intervals.

**The second (rule M-63, Appendix E) asks whether the one-step failure is a few bad channels or all of them**, since a pooled coverage is the unweighted mean of 45 per-dimension ones. It returns **{{m63_verdict}}**: the interquartile range across dimensions is {{m63_iqr}} points against a {{m63_iqr_thr}}-point threshold committed in advance, and the five worst dimensions carry well under half of the shortfall. **No channel is exempt.** The reading is coarse by construction: at h = 1 on {{d1n_nind}} trajectories a per-dimension coverage moves in {{m63_quant}}-point steps, a limit the rule fixed before the run.

The last column of §5.2's released-checkpoint table gives permutation P-values over whole trajectories, not binomial ones, on the same {{perm_all_nind}} trajectories as the counts beside them; Appendix C explains why a binomial null is inadmissible here. h = {{v2_deploy_h}} is tested too, because it carries the abstract's headline figure. These are {{perm_n_tests_col_word}} tests on one family and none survives Holm–Bonferroni across the arena's {{perm_all_holm_n}} cells: the smallest is {{perm_all_holm_min_cell}} at {{perm_all_holm_min_p}} against a threshold of {{perm_all_holm_thr}}. Read the column as a consistency check on direction, not as {{perm_n_tests_col_word}} independent findings.

---

Adding the teacher-forced arm, trained for §4.1, sharpens the finding (our arms at {{iters_main}} training iterations; the released checkpoint as released):

| model | σ variation across inputs (CoV) | dims with r(σ, error) > 0 at h={{v2_diag_h}}, held-out pair | perm P at h={{v2_diag_h}}, held-out pair | perm P at h={{v2_diag_h}}, training episodes |
|---|---|---|---|---|
| faithful Arm A | {{cal_faithA_cov}} | {{cal_faithA_npos}}/{{cal_faithA_ndim}} | {{perm_oos_faithA_p_h368}} | {{perm_ins_faithA_p_h368}} |
| corrected Arm A | {{cal_nll_cov}} | {{cal_nll_npos}}/{{cal_nll_ndim}} | {{perm_oos_nll_p_h368}} | {{perm_ins_nll_p_h368}} |
| **teacher-forced Arm B** | **{{cal_armB_cov}}** | **{{cal_armB_npos}}/{{cal_armB_ndim}}** | **{{perm_oos_armB_p_h368}}** | **{{perm_ins_armB_p_h368}}** |
| released checkpoint | {{cal_rel_cov}} | {{cal_rel_npos}}/{{cal_rel_ndim}} | {{perm_oos_relale_p_h368}} | {{perm_ins_relale_p_h368}} |

**The CoV column is the aleatoric σ in every row**, the only σ the ensemble-size-1 arms have. Our ensemble-5 arms (§5.6) have both: their aleatoric CoV is comparable to the other arms', and their *epistemic* term is far more input-dependent than any aleatoric head here, at {{e5_cov_lo}}–{{e5_cov_hi}} against the released checkpoint's {{cal_rel_cov}}. **The count column is the out-of-sample arena** (n_independent = {{relale_oos_nind}}), so that all four models are compared on trajectories none of our arms trained on. For the released checkpoint's aleatoric head it is not the most informative arena: at h = {{v2_diag_h}} and n_independent = {{relale_all_nind}} over all ten episodes that head is {{relale_all_pos_h368}}/{{perm_all_relale_ndim_h368}}, negatively correlated with error on *every* dimension, against {{relale_oos_pos_h368}}/{{perm_all_relale_ndim_h368}} here; supplementary S3 quotes the larger arena.

Arm B's σ is {{cal_armB_over_faithA_cov}}× more input-dependent than the faithful arm's, and it has the largest mean correlation of the four (r = {{cal_armB_r}}). It is still {{cal_armB_ratio}}× overconfident.

**The P column is a permutation P**, which pairs each trajectory's σ with a different trajectory's
realised error and so keeps the coupling between dimensions and the growth of error with depth that
every trajectory shares. The binomial P-values an earlier draft attached to these counts are
withdrawn (`S-15`), and the correction is large (Appendix I).

So σ *collapsing in magnitude* is objective-driven, and σ *becoming input-independent* is not.
The teacher-forced arm collapses in magnitude exactly like the autoregressive ones — same
objective, same rate — while retaining {{cal_armB_over_faithA_cov}}× more variation across
inputs. Input-independence is a property of the autoregressive arms and the released checkpoint,
and input-dependence and correct ranking are both achievable without the interval becoming
meaningful. One candidate mechanism, stated as an untested hypothesis: autoregressive feedback
narrows the input distribution toward the model's own manifold, leaving a heteroscedastic head less
variation to key on.

**The same pattern holds for the quantity the method uses, and this is where the correction bites hardest.** At h=128 and h=368 the epistemic term correlates positively with realised error on **{{b2_epi_npos_h368}} of {{b2_epi_ndim_h368}}** dimensions, matching the best aleatoric head here on the sign count, while being {{b2_epi_ratio_h368}}× overconfident at h = {{v2_diag_h}}. **Figures in this paragraph are the held-out arena (n_independent = {{b2_nind}}) unless labelled otherwise**, so the epistemic term and the four aleatoric heads are compared on identical trajectories; §5.2 quotes {{d1n_epi_ratio_h368}}× for the same ratio at h = {{v2_diag_h}} and n_independent = {{d1n_nind}}, and the abstract and §8 use {{d1n_epi_ratio_h100}}× at h = {{v2_deploy_h}} on those {{d1n_nind}} trajectories. Nor does it beat Arm B's head on strength: its mean correlation at h=368 is {{b2_epi_r_h368}} against {{cal_armB_r}}. The two rank comparably, and neither is close to an interval. Under the permutation null that count gives P = {{perm_oos_epi_p_h368}} on the held-out pair and {{perm_ins_epi_p_h368}} on the training episodes, both possibly in-sample for the checkpoint (§3.2), against {{perm_oos_epi_binom_h368}} from the independent-trials test. It still fails the horizon test the same way: σ grows {{b2_epi_sigma_growth}}× from h=1 to h=368 while error grows {{b2_epi_err_growth}}×.

**Across arenas, and after correction for multiplicity.** The two larger arenas, which are nested
(every in-sample trajectory is among the all-ten ones), put the epistemic ordering's strength at
*short* horizon, because at long horizon the forecast-depth trend every trajectory shares lifts the
null until a full count is close to chance, which is what motivates §5.6's index control. Nothing
here survives Holm–Bonferroni in any of the three arenas, and out of sample at the 400-step unit
nothing could, since its smallest attainable P already exceeds the smallest Holm threshold
(Appendix I).

**The structural excuse, with its table.** **The structural excuse does not survive.** One could argue that a model trained on an 8-step horizon cannot be expected to report calibrated
uncertainty about step 368. It cannot report it about step 8 either. Inside the trained horizon,
σ is flat while error grows (Figure 6; {{sig_arena}}, n_independent = {{sig_nind}} 400-step trajectories, possibly in-sample for the released checkpoint (§3.2); our arms at
{{iters_main}} training iterations, the released checkpoint as released):

| model | σ growth, step 1 → 8 | error growth, step 1 → 8 |
|---|---|---|
| faithful Arm A | {{sig_faithA_growth}}× | {{err_faithA_growth}}× |
| corrected Arm A | {{sig_nll_growth}}× | {{err_nll_growth}}× |
| teacher-forced Arm B | {{sig_armB_growth}}× | {{err_armB_growth}}× |
| released checkpoint | {{sig_rel_growth}}× | {{err_rel_growth}}× |

The faithful arm's σ *declines* ({{sig_faithA_growth}}×) while its error grows
{{err_faithA_growth}}×. The coverage collapse in Figure 5(b) is therefore driven entirely by
growing error against a fixed σ.

**The permutation tests.** **§5.6's P column is a permutation P, not a binomial one**, and the binomial P-values an earlier draft attached to its counts are withdrawn (`S-15`). A binomial null treats the 45 state dimensions as independent trials, and they are not: position, velocity and torque for the same joint are physically coupled, and base linear and angular velocity are coupled through the gait. More importantly, error grows with rollout depth in every trajectory, so *any* σ that also grows with depth correlates with *any* trajectory's error, including one it was never paired with.

We therefore permute whole trajectories. The null pairs each trajectory's σ with a different trajectory's realised error, which keeps both marginal distributions and the entire cross-dimension dependence structure and destroys only the association under test. The correction is large, and largest exactly where we leaned hardest. The worst-affected cell is {{perm_worst_model}} at h={{perm_worst_h}}, in the {{perm_worst_arena}} arena. At h = {{v2_diag_h}} it moves from {{perm_ins_armB_binom_h368}} to {{perm_ins_armB_p_h368}}, a factor of about {{perm_worst_factor}}, because under a null that keeps the dependence a random re-pairing already yields {{perm_worst_null}} of {{perm_ins_armB_ndim_h368}} dimensions positive on average, so observing {{perm_ins_armB_npos_h368}} of {{perm_ins_armB_ndim_h368}} is close to unremarkable. A fair coin centres the count at {{perm_faircoin}} of {{perm_ins_armB_ndim_h368}}; the dependence-preserving null centres it between {{perm_null_lo}} and {{perm_null_hi}} depending on model, horizon and arena.

**The larger arenas agree with each other against the smallest.** At n_independent = {{perm_oos_nind}} 400-step trajectories on the held-out pair, possibly in-sample for the checkpoint (§3.2), the epistemic ordering looks strongest at long horizon ({{perm_oos_epi_p_h128}} at h=128, {{perm_oos_epi_p_h368}} at h=368) and unremarkable at short ({{perm_oos_epi_p_h1}} at h=1). Both larger arenas invert that. In sample (n_independent = {{perm_ins_nind}}): {{perm_ins_epi_p_h1}} at h=1, {{perm_ins_epi_p_h8}} at h=8, against {{perm_ins_epi_p_h128}} at h=128. Over all ten episodes (n_independent = {{perm_all_nind}}): {{perm_all_epi_p_h1}}, {{perm_all_epi_p_h8}} and {{perm_all_epi_p_h128}}, with h = {{v2_deploy_h}} at {{perm_all_epi_p_h100}}, between h=32's {{perm_all_epi_p_h32}} and h=128's {{perm_all_epi_p_h128}}. Two larger arenas at four and five times the sample say the effect is strongest at *short*
horizon, though they are not independent: all {{perm_ins_nind}} in-sample trajectories are among
the {{perm_all_nind}}.

The null means explain why, and the explanation is the one that motivates §5.6. At long horizon the shared forecast-depth trend lifts the null to {{perm_all_epi_null_h128}} of 45 at h = 128, so a count of 45 is close to what chance alone delivers; at h = 1 the null sits near {{perm_all_epi_null_h1}} and the same count is genuinely surprising. The out-of-sample arena is not wrong so much as blind: at {{perm_oos_nind}} trajectories its smallest attainable P-value is {{perm_oos_floor}}, so it cannot tell a strong effect from a marginal one at any horizon. **That blindness belongs to the 400-step unit, not to the arena**: a {{m64_h1_unit}}-row unit gives {{m64_oos_n_h1}} independent units on the same two episodes, and {{m64_oos_n_h100}} at h = {{v2_deploy_h}} (rule M-64, Appendix E). We did not recompute this permutation family at the shorter unit, so what the short units change is the scope of the design claim, not any verdict: the arena is underpowered at h = {{v2_diag_h}}, which needs the full {{long_unit_rows}} rows, and is no longer demonstrably so at h = 128 and below. Running it there is one pass over stored rollouts, and we did not do it. The small arena's numbers are reported because it is the only arena out-of-sample for our own arms, not because it is the better measurement.

**Nothing here survives multiplicity correction, in any of the three arenas.** Holm–Bonferroni over each arena's {{perm_oos_holm_n}} model × horizon cells at α = 0.05 rejects {{perm_oos_holm_rej}} out of sample, {{perm_ins_holm_rej}} in sample and {{perm_all_holm_rej}} over all ten episodes. Out of sample that is a property of the design: with {{perm_oos_nind}} independent trajectories the smallest attainable P-value is {{perm_oos_floor}}, which already exceeds the smallest Holm threshold {{perm_oos_holm_thr}}, so no effect of any size could have been rejected there. In sample the miss is real: the smallest P in the family is {{perm_ins_holm_min_cell}} at {{perm_ins_holm_min_p}} against a threshold of {{perm_ins_holm_thr}}.

---

## Appendix J — Why the per-member σ collapses

Evidence behind §5.5: the synthetic-noise test, the term-by-term gradient check, the variance-state arithmetic and the PETS lineage with the survey counts.

**§5.5's permutation detail on the corrected objective.** Under the trajectory permutation test of §5.6, at h = {{v2_diag_h}}, those counts give P = {{perm_oos_faithA_p_h368}} and {{perm_oos_nll_p_h368}} out of sample, {{perm_ins_faithA_p_h368}} and {{perm_ins_nll_p_h368}} in sample. The faithful arm's ordering is the one result in this family that points the same way in both arenas; it is also the weakest effect of the three, and it does not survive multiplicity correction either.

**§5.5's derivation says the collapse happens on any dataset, and that is testable.** It matters
because it is what answers the follow-up's own explanation: on the released CSV, "small
stochasticity in the environment" and our reading are observationally identical, since the data may
simply be nearly deterministic. So under a rule committed before the runs (rule M-50, Appendix E)
we built data where it is not.

Synthetic data whose true noise level is **known** and varies by a factor of {{e5s_span}} across
the input range, with a non-constant true mean; the **same** bounded log-σ head as the released
model — `MLPStateHead` unmodified, including the double-softplus clamp, the learnable
`state_min_logstd` and `state_log_delta_logstd`, and the bound loss at its configured weight —
trained under each objective in turn on {{e5s_n_train}} points for {{e5s_iters}} iterations at
{{e5s_seeds}} seeds. Nothing else differs between the arms.

*Two ways this is not the released setting.* The head is built here over a **one-dimensional**
state with no recurrent trunk in front of it, where the released one predicts {{cal_rel_ndim}}
dimensions from a GRU. The trunk's absence is deliberate: the question is about the head's
objective, and a GRU would add a confound. The dimensionality matters because the state loss sums
over state dimensions, so at one dimension it is roughly {{cal_rel_ndim}}× smaller relative to the
bound term than in the released path. That makes this setting *more* favourable to σ surviving, and
the collapse happens anyway.

| objective | median σ̂ / σ_true | σ̂ spread across the input range | slope of log σ̂ on log σ_true |
|---|---|---|---|
| `mse` — the implemented branch | **{{e5s_mse_ratio}}** | {{e5s_mse_spread_range}}× | {{e5s_mse_slope}} |
| `gaussian_nll` — the authors' unused branch | {{e5s_nll_ratio}} | {{e5s_nll_spread_range}}× | {{e5s_nll_slope}} |

*Ratios and slopes are means over {{e5s_seeds}} seeds; spreads are the range across them, because
the mean of a spread hides which seeds recovered.*

**Under the implemented objective σ sits {{e5s_mse_under}}× below the true noise and does not
track it at all**: a spread of {{e5s_mse_spread}}× where the truth spans {{e5s_span}}×, and a
slope below the {{e5s_slope_thr}} the design can detect. Under the authors' own branch, same data
and same head, σ recovers the true level to a median ratio of {{e5s_nll_ratio}}, and every one of
the {{e5s_seeds}} seeds the rule was discharged over clears the slope threshold. **Twenty seeds
show that clearance is not general**: {{e5s_corrob_clearing}} of {{e5s_corrob_seeds}} clear it, so
the all-seeds criterion would not have held at that sample. The rule's verdict stands as returned
over its own {{e5s_seeds}} and is not re-opened by more seeds (§3.4); what twenty establish is that
the hedge below was necessary. **The recovering arm is seed-variable, and the rule said so before
the runs**: its slopes span {{e5s_nll_slope_range}}, a factor of
{{e5s_nll_slope_spread_factor}}, and its {{e5s_seeds}} seeds recover σ spreads of only {{e5s_nll_spread_range}}× against the truth's {{e5s_span}}×. So what this experiment establishes is
the **contrast**, that one objective tracks the noise at all and the other does not, and not the
magnitude of the recovery, which this training budget does not pin down. **{{e5s_verdict}}**, which is the verdict the rule names for that pattern.

*The statistic is the slope, not the correlation, because a correlation is scale-free: a σ̂ that is
essentially constant still returns a large one off its own numerical noise. Under a permutation
null, the same data with the input-to-noise pairing destroyed, a head whose σ spanned
{{e5s_null_spread}}× returned correlations as large as ±{{e5s_null_r_max}}, while its slope was
{{e5s_null_slope_p95}}. The detection threshold is set at the slope corresponding to a
{{e5s_span_floor}}× spread rather than at that noise floor, and the measured false-positive rate at
zero signal is {{e5s_fp_rate}}%.*

**What this does that §5.5's derivation alone could not.** It removes the competing explanation
rather than arguing against it: the stochasticity here is large, known and input-dependent, and the
collapse happens anyway. The design's limit, stated in the rule, holds: the dilution ladder detects
the signal at full strength and at no dilution below it, so this establishes that σ does not track
the noise **at all**, not the magnitude of how badly.

**§5.5's derivation covers two terms, and the objective has {{e4_n_terms}}.** Its completeness
rests on the other {{e4_n_inert}} being inert with respect to σ, so each term is computed alone on
one real batch ({{e4_batch}} windows from the training episodes, at freshly initialised weights of
the released architecture) and back-propagated alone, and the gradient reaching the log-σ tower,
`state_log_delta_logstd` and `state_min_logstd` is recorded. A term that cannot move σ produces
exactly zero on all three.

| loss term | live? | weight | where the reference computes it | ∂/∂ log-σ tower | ∂/∂ `log_delta_logstd` | ∂/∂ `min_logstd` |
|---|---|---|---|---|---|---|
{{e4_table}}

{{e4_n_live}} of the {{e4_n_terms}} configured terms are live at all under the released
configuration: `sequence_loss` is dead code, guarded by a `prediction_type` the reference sets to
`"single"` on both paths, and `extension` is zero because its dimension is, while `kl` belongs to the RSSM branch only. Of the
{{e4_n_terms}}, exactly {{e4_n_touch}} reach σ: {{e4_touching}}. The remaining {{e4_n_inert}}
produce a gradient of exactly zero, not merely a term the code suggests is irrelevant
(`results/e4_sigma_gradients.json`).

We predicted the collapse from §5.5's algebra before training, then observed it. Three run counts
appear below and they are not the same set. This project trained {{run_total}} runs for §4.1–§6, besides the {{rt_pre_runs}} of §4.2 and §4.3
(Appendix B), of
which {{n_runs}} are at the released `rnn_hidden_size` of {{released_width}} and form the collapse
family; the remaining {{n_runs_offwidth}} are the capacity-matched arm of rule M-49 (Appendix E) at
width {{m49_width}}, a different architecture, excluded from every rate §5.5 quotes (Appendix B).
Across all {{n_runs}} runs of that family the log-σ range moves linearly in iteration count at a nearly identical rate within each objective, falling under sampled MSE and rising under the corrected one (Figure 7a). Rates are fitted on {{e2_fitted_runs}} of those {{n_runs}}: the
{{e2_excluded_10k}} 10,000-iteration runs continue seeds already counted at 2,500 and would
double-weight them. Figure 7(a) shows all {{n_runs}} runs of the collapse family and Figure 7(b)
only the {{e2_fitted_runs}} the rate is fitted on, so the scatter and §5.5's quoted statistic describe
the same set. The {{run_total}} runs, with the width column separating the collapse family from the
capacity-matched arm:

| arm | iterations | ensemble | objective | dataset | width | seeds | seed ids |
|---|---|---|---|---|---|---|---|
{{run_table}}

---

**The variance-state arithmetic.** §6 states the conclusion. The arithmetic and the five assumptions it rests on are in
`docs/APPENDIX_G_VARIANCE_ARITHMETIC.md`, shipped as supplementary, kept out of the body because the numbered
claim it once supported is retracted (`S-19`) and because a forensic case the section then defuses
with the author's own reply is not what a reader needs in the body of a reproduction.

So the finding is not that the release is internally inconsistent. It is that **the released
artifacts do not reproduce the released checkpoint's variance state, and the author's account is
that the released repository is not the one that trained it.** That is a **documentation gap between a release and a run**: common, worth recording, and much less interesting than an inconsistency.
The σ collapse is linear in iteration count and its rate is nearly identical across our runs (§5.5), which makes it a clock, and read as a clock it puts the checkpoint's variance state out of reach of a constant-rate run from the released initialisation at the configured learning rate, at every iteration count the release, the paper and the checkpoint tag state. The first author's account is that the released repository is several revisions removed from the setup that trained the checkpoint, which supplies a mechanism, a warm start or a different `log_delta_logstd` initialisation, that would explain it with no inconsistency at all. We report the arithmetic because it is what let us detect the gap at all, not as a charge against the work.

---

**Where the parameterisation comes from.** The bounded log-σ head that §5.5 shows has its optimum
at σ = 0 is largely not this codebase's invention: its clamp is inherited, line for line, from the
probabilistic ensembles of Chua, Calandra, McAllister and Levine (PETS, NeurIPS 2018). PETS's
Appendix A.1 gives

```
logvar = max_logvar - softplus(max_logvar - logvar)
logvar = min_logvar + softplus(logvar - min_logvar)
```

and `architectures/mlp.py:92-93` is those two lines in log-standard-deviation rather than
log-variance, with `system_dynamics.py:302` supplying PETS's regulariser on the bounds.

What is **not** inherited is the objective, and one line of the bounds. PETS uses "the negative
log prediction probability as our loss function", and that likelihood's log-σ term opposes
σ → 0; `system_dynamics.py:283` substitutes squared error on a reparameterised sample, which has no
such term. And `architectures/mlp.py:91` builds the upper bound as the floor plus a learned positive
gap, where PETS keeps the two bounds independent. §5.5 needs both changes: the substitution removes
the log-σ term, and the tie is why the bound regulariser does not take its place, since the floor
cancels out of it. In a descendant that kept PETS's independent bounds, the same regulariser pushes
the floor up while the objective pulls σ down onto it, a case §5.5 does not derive and we have not
tested (ledger `M-72`). So **a descendant of this lineage that replaced the likelihood with a
sampled squared error, and left nothing pushing its variance floor back up, would inherit the same
optimum.** That is a hypothesis about mechanism, untested in any other descendant (§7).

**How often the substitution is made, which narrows the hypothesis.** Of {{q1_n_examined}} public
repositories examined on {{q1_date}} under the protocol in `results/q1_search_protocol.md`,
{{q1_n_carry}} carry the construction and {{q1_n_inherit}} of those trains it against a sampled
squared error, and that one only in an optional value-aware mode; the other {{q1_n_keep}} keep
PETS's likelihood (`results/q1_pets_descendants.json`). The protocol counts a repository only if
it has the bounded head, learnable bounds, and a loss that squares the error of a *sampled*
prediction; squaring the error of the predicted *mean*, an option several of these repositories
offer, leaves σ untrained rather than driving it to zero, and does not count. We read "learnable"
as "trainable by the code, by default or not", a reading settled after the survey, because in
`mbrl-lib` and in `va_mbpo`, the one repository that inherits, the bounds train only when a caller
switches that on (ledger `M-73`). The survey did not check how each repository treats its variance
floor, so {{q1_n_inherit}} of {{q1_n_examined}} is an upper bound on how often both conditions
hold. The survey looked at {{q1_n_looked}} in all; the other {{q1_n_absent}} lack the construction, so the protocol does not count them as examined, among them mainline `rsl_rl`:
the bounded head exists in the fork this paper pins, not in the library it forks, and we do not
count the fork, since counting what §5.5 measured as evidence that the result travels would be
circular. The protocol capped the survey at {{q1_cap}} repositories; it stopped at {{q1_n_examined}} examined, {{q1_n_looked}} looked at, and its notes give no reason. We wrote the protocol before the search, but
neither it nor its hash reached git before the results did, so that order rests on our own record;
it is a search protocol, not one of Appendix E's decision rules. Search engines rank and truncate,
so this is a sample of convenience, but on it the substitution is rare, and a reader who takes the
hypothesis to reach widely infers more than the evidence supports.

---

## Appendix K — The shared trunk and independent ensembles

The shared trunk behind §5.3, from the source and for our own arms, and the two pre-registered comparisons that test it: independent members, and independent members with the corrected objective.

**Source walkthrough.** `system_dynamics.py:34` builds **one**
`state_base`. `system_dynamics.py:35-41` replicates the *heads* `ensemble_size` times, and only
the heads. In the forward pass `system_dynamics.py:87` evaluates the trunk **once** and `:90`
hands the identical feature vector to every head; `system_dynamics.py:126` then computes the
epistemic term as the standard deviation across those heads.

**Our own arms.** **This applies to our own arms identically, which is why §5.2's comparison is fair.** Our
ensemble-5 arms build one trunk the same way (`src/rwm_model.py:164-167`), evaluate it once
(`:182`), hand the same vector to every head (`:185`) and compute the same spread (`:200`). Their
tensor names and parameter counts match the released checkpoint exactly —
{{v1_shared_params}} shared, {{v1_private_params}} per head, {{v1_total_params}} in total, on all
{{v1_n_arms_checked}} arms checked (`results/v1_ensemble_topology.json`). So §5.2's "our arms fail the same way at {{e5_ratio_h100}}× at h = {{v2_deploy_h}}" compares two instances of one architecture, not two architectures.

**The table for rule M-44.**

| h | independent err/σ | shared-trunk err/σ | independent ±1σ | shared-trunk ±1σ |
|---|---|---|---|---|
| 1 | {{r2_indep_ratio_h1}}× | {{r2_shared_ratio_h1}}× | {{r2_indep_cov1_h1}}% | {{r2_shared_cov1_h1}}% |
| 8 | {{r2_indep_ratio_h8}}× | {{r2_shared_ratio_h8}}× | {{r2_indep_cov1_h8}}% | {{r2_shared_cov1_h8}}% |
| 32 | {{r2_indep_ratio_h32}}× | {{r2_shared_ratio_h32}}× | {{r2_indep_cov1_h32}}% | {{r2_shared_cov1_h32}}% |
| **{{v2_deploy_h}}** | **{{r2_indep_ratio_h100}}×** | **{{r2_shared_ratio_h100}}×** | **{{r2_indep_cov1_h100}}%** | **{{r2_shared_cov1_h100}}%** |
| 128 | {{r2_indep_ratio_h128}}× | {{r2_shared_ratio_h128}}× | {{r2_indep_cov1_h128}}% | {{r2_shared_cov1_h128}}% |
| {{v2_diag_h}} | {{r2_indep_ratio_h368}}× | {{r2_shared_ratio_h368}}× | {{r2_indep_cov1_h368}}% | {{r2_shared_cov1_h368}}% |

*Same trajectories (the held-out pair), same harness, n_independent = {{r2_nind}}, every model at {{iters_main}} training iterations. The shared-trunk column is the mean
over {{r2_n_shared}} seeds; the comparison below is paired against each of them separately.*

§5.3 establishes the topology as a fact and the mechanism as a hypothesis. Rule M-44 tests
the hypothesis, under a rule committed to git before any of the artifacts below existed (rule
M-44, Appendix E), with a power check estimating what it could detect at the sample size it would
face.

**The contrast, and why it is affordable.** Training {{r2_n_indep}} genuinely independent models
from scratch costs about {{r2_scratch_h}} h of wall clock on two cores at these runs' iteration
count, against the {{rt_hours}} h Appendix B gives for the {{run_total}} runs of §4.1–§6 it times (§4.2's sweep and §4.3's baselines are counted apart). Arm A at ensemble size 1 already
existed at seeds 0, 1 and 2; we added {{r2_n_added_word}} more at about {{r2_added_h}} h each,
{{r2_added_h_total}} h in total, and scored the {{r2_n_indep}} together as an ensemble **at
evaluation time**. There is no new training code and no new architecture, and the disagreement
across {{r2_n_indep}} independently initialised *full models* is exactly the contrast §5.3 asks
for. The rollout protocol mirrors the shared-trunk one in every respect except the one under test:
each member sees the same input state, each keeps **its own** recurrent hidden state, and the
ensemble mean is fed back to all of them.

**The rule returns {{m44_verdict}}.** All {{m44_n_conditions_met}} of its
{{m44_n_conditions}} conditions hold, against every one of the {{r2_n_shared}} shared-trunk seeds.
At h = {{v2_deploy_h}} the independent ensemble's overconfidence factor is
{{r2_ratio_lo}}–{{r2_ratio_hi}}× the shared-trunk arms', a **{{m44_ratio_gain}}×** improvement
against a pre-registered minimum detectable effect of {{m44_mde_ratio}}×, and its ±1σ coverage is
{{r2_cov_lo}} to {{r2_cov_hi}} points higher, a mean of {{m44_cov_gain}} against an MDE of
{{m44_mde_cov}}. Every paired interval excludes zero. **Members that share a feature extractor do
produce a smaller spread, and the effect is large enough to matter.**

**Where the improvement comes from, which is not all one thing.** The overconfidence factor is
error over σ, so it improves if σ grows *or* if error shrinks, and only the first is the
trunk-sharing mechanism; five independent models also denoise better than five heads on one trunk,
an ordinary ensembling effect. Splitting the improvement into its two multiplicative parts:

| h | σ larger by | error smaller by | total | share from σ | share from accuracy |
|---|---|---|---|---|---|
| 1 | {{r2_sigma_x_h1}}× | {{r2_acc_x_h1}}× | {{r2_total_x_h1}}× | {{r2_from_sigma_h1}}% | {{r2_from_acc_h1}}% |
| 8 | {{r2_sigma_x_h8}}× | {{r2_acc_x_h8}}× | {{r2_total_x_h8}}× | {{r2_from_sigma_h8}}% | {{r2_from_acc_h8}}% |
| 32 | {{r2_sigma_x_h32}}× | {{r2_acc_x_h32}}× | {{r2_total_x_h32}}× | {{r2_from_sigma_h32}}% | {{r2_from_acc_h32}}% |
| **{{v2_deploy_h}}** | **{{r2_sigma_x_h100}}×** | {{r2_acc_x_h100}}× | {{r2_total_x_h100}}× | **{{r2_from_sigma_h100}}%** | {{r2_from_acc_h100}}% |
| 128 | {{r2_sigma_x_h128}}× | {{r2_acc_x_h128}}× | {{r2_total_x_h128}}× | {{r2_from_sigma_h128}}% | {{r2_from_acc_h128}}% |
| {{v2_diag_h}} | {{r2_sigma_x_h368}}× | {{r2_acc_x_h368}}× | {{r2_total_x_h368}}× | {{r2_from_sigma_h368}}% | {{r2_from_acc_h368}}% |

*On the held-out pair's {{r2_nind}} independent trajectories, independent against shared-trunk ensembles, all at {{iters_main}} iterations. Shares are of the log improvement, so they add to 100%. A share above 100% at h=1 means the
independent ensemble is very slightly the **worse** predictor there and the σ gain more than
covers it.*

**The reading, at the horizon the rule is stated over.** σ is larger at every horizon, by
{{r2_sigma_x_lo}}× at its weakest (h = {{r2_sigma_x_lo_h}}) and {{r2_sigma_x_hi}}× at its strongest
(h = {{r2_sigma_x_hi_h}}), the direction trunk-sharing predicts, and at h = {{v2_deploy_h}} it is
{{r2_sigma_x_h100}}×, **{{r2_from_sigma_h100}}%** of the improvement. So the mechanism is supported,
and it is the larger part of the effect where the method operates. At the open-loop diagnostic
horizon of h = {{v2_diag_h}} the split reverses: {{r2_from_acc_h368}}% of the improvement there is
the ensemble simply predicting better, so a reader who takes the {{r2_total_x_h368}}× figure at that
horizon as a measure of the architectural effect would overstate it.

**What this does and does not license.** It licenses saying that **the released ensemble's
disagreement understates epistemic uncertainty partly because its members are not independent
models**, with a measured size at the horizon that matters. It does not license attributing the
whole gap to trunk-sharing: independently seeded runs differ in *both* initialisation and data
ordering (supplementary S2), so this comparison **bounds** the architectural effect rather than isolating it,
and the bound is generous to the mechanism by construction.

**And it does not repair the interval.** The independent ensemble is
{{r2_indep_ratio_h100}}× overconfident at h = {{v2_deploy_h}} with
{{r2_indep_cov1_h100}}% coverage where a calibrated Gaussian gives {{v3_cov_nominal1}}%. Better by
a factor of {{m44_ratio_gain}}, and still not an interval. Building the ensemble properly is worth
doing and it is not sufficient; §5.7's per-horizon multiplier remains the only correction in this paper whose estimates all land within the band, though only on the released checkpoint and no single cell is resolvable at this arena. On Arm A, whose model never saw the test episodes, it manages {{d3x_own_epi_ok}} of {{d3x_own_epi_cells}} epistemic cells (§5.7).

---

**The table for rule M-68.**

| h | combined err/σ | shared-trunk err/σ | combined ±1σ | shared ±1σ | combined ±2σ | shared ±2σ |
|---|---|---|---|---|---|---|
| 1 | {{m68_indep_ratio_h1}}× | {{m68_shared_ratio_h1}}× | {{m68_indep_cov1_h1}}% | {{m68_shared_cov1_h1}}% | {{m68_indep_cov2_h1}}% | {{m68_shared_cov2_h1}}% |
| 8 | {{m68_indep_ratio_h8}}× | {{m68_shared_ratio_h8}}× | {{m68_indep_cov1_h8}}% | {{m68_shared_cov1_h8}}% | {{m68_indep_cov2_h8}}% | {{m68_shared_cov2_h8}}% |
| 32 | {{m68_indep_ratio_h32}}× | {{m68_shared_ratio_h32}}× | {{m68_indep_cov1_h32}}% | {{m68_shared_cov1_h32}}% | {{m68_indep_cov2_h32}}% | {{m68_shared_cov2_h32}}% |
| **{{v2_deploy_h}}** | **{{m68_indep_ratio_h100}}×** | **{{m68_shared_ratio_h100}}×** | **{{m68_indep_cov1_h100}}%** | **{{m68_shared_cov1_h100}}%** | {{m68_indep_cov2_h100}}% | {{m68_shared_cov2_h100}}% |
| 128 | {{m68_indep_ratio_h128}}× | {{m68_shared_ratio_h128}}× | {{m68_indep_cov1_h128}}% | {{m68_shared_cov1_h128}}% | {{m68_indep_cov2_h128}}% | {{m68_shared_cov2_h128}}% |
| {{v2_diag_h}} | {{m68_indep_ratio_h368}}× | {{m68_shared_ratio_h368}}× | {{m68_indep_cov1_h368}}% | {{m68_shared_cov1_h368}}% | {{m68_indep_cov2_h368}}% | {{m68_shared_cov2_h368}}% |

*Same trajectories (the held-out pair, n_independent = {{m68_nind}} 400-step trajectories), same harness, the same bootstrap unit, whole trajectories, as Appendix K's table, every model at {{iters_main}} training iterations. The shared-trunk columns are the
mean over {{m68_n_shared}} seeds; the comparison below is paired against each of them separately.*

§5.3 changes the **topology** and holds the objective at `mse`; §5.5's arms change the
**objective** and hold the topology at ensemble size 1, where disagreement is zero by construction.
Neither answers the practitioner's question of what the two give together, and adding two effects
never measured on the same model is the arithmetic this paper criticises elsewhere. Rule M-68
runs the combination, under a rule committed to git before either new member existed (rule M-68,
Appendix E), with a minimum detectable effect estimated in advance as well.

**The arm.** {{m68_n_indep}} independently initialised full models, sharing no trunk and no hidden
state, trained under `gaussian_nll`, every setting identical to §5.3's arm except the loss type.
Three of the five, seeds 0, 1 and 2, already existed under that objective; two more were trained,
and the {{m68_n_indep}} are scored together as an ensemble at evaluation time under §5.3's rollout
protocol, on the same held-out arena of non-overlapping 400-step trajectories at
n_independent = {{m68_nind}}, over the same six horizons.

**Which σ the coverage is against.** The combined arm is the first arm in this paper carrying
**both** an aleatoric head that has not collapsed to zero and an across-member epistemic spread.
The figures below are the **epistemic** one, {{m68_sigma_used}}: the quantity the rule names and
§5.3's table reports, so the two tables are comparable line for line. The aleatoric head is
reported in §5.5 and does not enter here.

**The rule returns {{m68_verdict}}**, branch {{m68_branch}} of the four it names. All
{{m68_n_conditions_met}} of its {{m68_n_conditions}} conditions hold, against every one of the
{{m68_n_shared}} shared-trunk seeds. At h = {{v2_deploy_h}} the combined arm's overconfidence
factor is {{m68_ratio_lo}}–{{m68_ratio_hi}}× the shared-trunk arms', a **{{m68_ratio_gain}}×**
improvement against a minimum detectable effect of {{m68_mde_ratio}}× fixed in advance
({{m68_mde_source}}); its ±1σ coverage is {{m68_cov_lo}} to {{m68_cov_hi}} points higher, a mean of
{{m68_cov_gain}} against an MDE of {{m68_mde_cov}} points; and every paired interval excludes zero.

**Condition (e), and how we read it.** The rule's fifth condition asks that both statistics move in
the improving direction at at least four of the six horizons, "against every shared-trunk seed",
and the rule states globally that a condition holds only if it holds against all three. We applied
the strict reading: a horizon counts only when **both** statistics improve there against **all
three** seeds. It holds at {{m68_n_dir}} of {{m68_n_horizons}} horizons, so the looser per-seed
reading would not have changed the verdict; we record which we applied because the rule does not
spell the difference out.

| h | σ larger by | error smaller by | total | share from σ | share from accuracy |
|---|---|---|---|---|---|
| 1 | {{m68_sigma_x_h1}}× | {{m68_acc_x_h1}}× | {{m68_total_x_h1}}× | {{m68_from_sigma_h1}}% | {{m68_from_acc_h1}}% |
| 8 | {{m68_sigma_x_h8}}× | {{m68_acc_x_h8}}× | {{m68_total_x_h8}}× | {{m68_from_sigma_h8}}% | {{m68_from_acc_h8}}% |
| 32 | {{m68_sigma_x_h32}}× | {{m68_acc_x_h32}}× | {{m68_total_x_h32}}× | {{m68_from_sigma_h32}}% | {{m68_from_acc_h32}}% |
| **{{v2_deploy_h}}** | **{{m68_sigma_x_h100}}×** | {{m68_acc_x_h100}}× | {{m68_total_x_h100}}× | **{{m68_from_sigma_h100}}%** | {{m68_from_acc_h100}}% |
| 128 | {{m68_sigma_x_h128}}× | {{m68_acc_x_h128}}× | {{m68_total_x_h128}}× | {{m68_from_sigma_h128}}% | {{m68_from_acc_h128}}% |
| {{v2_diag_h}} | {{m68_sigma_x_h368}}× | {{m68_acc_x_h368}}× | {{m68_total_x_h368}}× | {{m68_from_sigma_h368}}% | {{m68_from_acc_h368}}% |

*On the held-out pair, n_independent = {{m68_nind}} 400-step trajectories, every model at {{iters_main}} iterations: the same σ-versus-accuracy split Appendix K uses for rule M-44, so the two arms' improvements can be compared part by
part. Shares are of the log improvement, so the two columns add to one.*

**The objective's own contribution is below what this design can resolve.** The rule scores the
combined arm against the **shared-trunk** arms, so its verdict measures the two fixes together. The
comparison that isolates the objective is against §5.3's independent arm, which differs from this
one in the loss type and nothing else, from the same script on the same trajectories. At
h = {{v2_deploy_h}} switching `mse` for `gaussian_nll` multiplies the overconfidence factor by
**{{m68_vs_mse_ratio}}×** (95% interval from the same cluster bootstrap over whole trajectories,
{{m68_vs_mse_ratio_ci}}), the wrong direction, slightly; moves ±1σ coverage by
{{m68_vs_mse_cov_pts}} points ({{m68_vs_mse_cov_ci}}, which spans zero); and multiplies the
epistemic σ by {{m68_vs_mse_sigma_x}}×. Both effects sit under the minimum detectable effect fixed
in advance, {{m68_mde_ratio}}× on the factor and {{m68_mde_cov}} points on coverage
({{m68_mde_source}}), so although the factor's interval lies wholly on the worse side of no change,
the objective's separate effect is **below the size this design was built to resolve at
n_independent = {{m68_nind}}**, and the point estimate points away from an improvement. It does not
establish that the objective contributes nothing: reading a null out of an effect smaller than its
own floor is the error M-24 and M-43 record, and the rule's fourth branch exists to say
underpowered rather than null. What the arm does settle is the combination, which is better
calibrated than the shared-trunk arms by essentially the amount §5.3 measured for independence
alone ({{m44_ratio_gain}}× there, {{m68_ratio_gain}}× here). **The two fixes do not add. A reader
who added them would have been wrong, which is why the arm was run.** That the objective's separate
effect is at most small is not a surprise once stated: the objective governs the **aleatoric**
head, and the epistemic term is a spread across members that the loss never sees.

**And it still does not repair the interval.** The combined arm is {{m68_indep_ratio_h100}}×
overconfident at h = {{v2_deploy_h}} with {{m68_indep_cov1_h100}}% coverage where a calibrated
Gaussian gives {{v3_cov_nominal1}}%. Better than the shared-trunk arms, no better than independence
alone, and still not an interval. §5.7's per-horizon multiplier remains the only correction in this paper whose estimates all land within the band, though only on the released checkpoint and no single cell is resolvable at this arena. On Arm A, whose model never saw the test episodes, it manages {{d3x_own_epi_ok}} of {{d3x_own_epi_cells}} epistemic cells (§5.7).

**What the arm does not separate.** It differs from the shared-trunk arms on three axes at once:
trunk sharing, the objective, and capacity (a factor of {{v1_cap_ratio}} in state-pathway
parameters, as §5.3's contrast also does; supplementary S2), and independently seeded runs also differ in data
ordering. The rule said so in advance: it bounds the combination and attributes nothing. The one
further comparison here, the `mse`/`gaussian_nll` pair above, which holds every other axis fixed,
sits outside the rule's governing statistics and under the design's own minimum detectable effect,
so it bounds the objective's separate contribution rather than measuring it.

---

## Appendix L — Ranking against free signals

Detail behind §5.6: the correlation at each horizon, the robustness checks, the free baselines and their cost, and the rule on shorter units.

**Why §5.6's paired test, not overlapping intervals.** Comparing the two marginal intervals for overlap is the wrong comparison: both correlations are measured on the *same* trajectories, so their sampling errors move together and the marginal intervals are needlessly conservative. The paired difference, resampling whole trajectories and recomputing *both* correlations inside each draw, is the appropriate and more powerful test.

**§5.6's shorter-unit note at h = 128.** At the shorter unit of rule M-64 (Appendix E), {{m64_h128_n}} non-overlapping units over the same ten episodes give {{m64_h128_ci}} for the same paired difference, so that horizon carries more weight than it did.

**r_dd per horizon (§5.6).** **Per horizon, on the same {{a2_nind}} trajectories (the released checkpoint over all ten episodes) and the same kind of cluster bootstrap:** it is
a separate run, so its h = {{v2_diag_h}} interval differs from M-45's in §5.6, {{a2_rdd_ci}}, in the third decimal, as this appendix's pooled interval does from §5.2's {{d4_ci}}.

| h | r_dd, double-demeaned | 95% CI | excludes zero |
|---|---|---|---|
| 1 | — | — | — |
| 8 | {{a2_rdd_h8}} | {{a2_rdd_ci_h8}} | no |
| 32 | {{a2_rdd_h32}} | {{a2_rdd_ci_h32}} | no |
| **{{v2_deploy_h}}** | **{{a2_rdd_h100}}** | **{{a2_rdd_ci_h100}}** | **yes** |
| 128 | {{a2_rdd_h128}} | {{a2_rdd_ci_h128}} | yes |
| {{v2_diag_h}} | {{a2_rdd_h368}} | {{a2_rdd_ci_h368}} | yes |

*(h = 1 has one forecast step per trajectory, so there is nothing within a rollout to demean against and r_dd is undefined rather than zero.)*

The within-rollout effect is materially smaller than the pooled figure and not established at short
horizon; at h = 1 the correlation ranks whole rollouts, on {{a2_h1_npoints}} trajectory-level points
(Appendix L).

**Rule M-43 (§5.6).** **Does it hold on a model we trained?** Three Arm A arms at ensemble size 5 ({{iters_main}} training iterations, scored on the held-out pair), under a rule
committed before the runs (rule M-43, Appendix E), lead the index in **{{e5_lead_cells}} of
{{e5_total_cells}}** seed-horizon cells, but the paired difference excludes zero at only
{{e5_n_excl}} of {{e5_n_horizons}} horizons, so the rule returns **{{e5_verdict}}**. At
n_independent = {{e5_nind}} 400-step trajectories it was under-powered, which we measured after the fact and should have
checked before committing it (Appendix L).

**The expectation (§5.6).** **We ran the baseline test expecting it to go the other way.** A counter matching disagreement would have been the more consequential result, making the trust metric close to vacuous, since a counter is free. We record that as an expectation only: it was not committed to git before the data existed, so by this paper's own standard (§3.4) it is not a pre-registration. It did not go that way against the counter. It went that way against something else.

**The two free baselines and their cost (§5.6).** A claim that beats exactly one competitor is a claim about that competitor. Under a rule committed
before either was computed (rule M-51, Appendix E, corrected by rule M-52), we added two baselines
needing no ensemble and no second model: `step-size`, the magnitude of the model's own predicted
state change $\lVert \mu_t - \mu_{t-1} \rVert$, which costs nothing because the rollout has already made those
predictions; and `entry-res`, its one-step error at the step *before* the forecast window opens,
which costs **one extra rollout in this harness** and nothing in deployment, where a model consumes
the history to build its recurrent state anyway. The first rule called both free without
distinguishing those, and the second records the correction.

**X6's alongside readings (§5.6).** On the released checkpoint's {{x6_n_units}} units of {{x6_unit_len}} rows over its ten released episodes, at h = {{v2_deploy_h}} the margin also exceeds the {{x6_mde}} minimum detectable effect computed before the reading by rule M-51's method. Disagreement correlates {{x6_r_dis}} with error there against step size's {{x6_r_step}}, and keeps {{x6_partial}} {{x6_partial_ci}} with step size partialled out; alongside, on {{x6_n_units_h32}} units at h = 32 the margin is {{x6_margin_h32}} {{x6_ci_h32}}.

**What survives removing each confound.** A linear partial is not much of a control: error
does not grow linearly with depth, and a control that under-fits the index leaves index-driven
variance in the residual and flatters disagreement. The first five rows after the pooled baseline
below are **depth controls**, each partialling out a different model of how far into the rollout
you are; the last four **decompose** the pooled figure into its between-trajectory and
within-trajectory parts, and the last of those was pre-registered before it was computed (rule
M-45, Appendix E). **One row is not comparable to the others**: the rank partial is a correlation
of ranks rather than of values, so its being larger than the pooled figure says nothing about how much depth explains. Every row is the released checkpoint over all ten episodes, n_independent = {{a2_nind}} 400-step trajectories.

| what is removed | correlation | 95% CI | what survives it |
|---|---|---|---|
| nothing (pooled) | {{a2_r_pooled}} | {{a2_r_pooled_ci}} | — |
| the step index, linearly | {{d2b_par_all}} | — | depth explains {{d2b_shrink_all_abs}} of it, from {{d2b_epi_all}} |
| log(1 + index) | {{d2r_log}} | {{d2r_log_ci}} | a non-linear model of depth |
| a cubic in the index | {{d2r_cub}} | {{d2r_cub_ci}} | any polynomial trend in depth |
| any monotone function of depth (rank partial) | {{d2r_spr}} | {{d2r_spr_ci}} | depth in any monotone form |
| depth exactly, within each forecast step | **{{d2r_win}}** | {{d2r_win_ci}} | positive at {{d2r_win_pos}} of {{d2r_win_n}} steps, median {{d2r_win_med}}[^stepcount] |
| forecast-step means only | {{a2_step_only}} | — | the within-step control, pooled |
| everything within a trajectory | {{a2_r_within}} | {{a2_r_within_ci}} | — |
| the {{a2_nind}} trajectory means alone | {{a2_r_between}} | {{a2_r_between_ci}} | do harder rollouts disagree more? |
| **both, additively (r_dd)** | **{{a2_rdd}}** | **{{a2_rdd_ci}}** | **at a given depth, in a given rollout, does disagreement know?** |

[^stepcount]: Adjacent forecast steps on the same {{a2_nind}} trajectories are heavily dependent — structurally the same problem that §5.6's permutation null corrects for across the 45 coupled state dimensions (Appendix C). The count is descriptive; the interval {{d2r_win_ci}} is the statistic, and no P-value attaches to {{d2r_win_pos}}/{{d2r_win_n}}.

The weakest figure across the {{d2r_ncontrols}} depth controls is {{d2r_weakest}}, so disagreement
is not re-encoding the clock: at a fixed depth it still knows which rollouts are going wrong. But
depth was never the only confound. Per-episode difficulty, the released checkpoint's error on each
episode scored with the causal action pairing (§6), spans {{d12_lo}} to {{d12_hi}} and is barely
correlated with commanded speed ({{d12_speed_r}} across the ten episodes), so if harder trajectories simply have both larger error and
larger disagreement, the pooled correlation would look exactly as it does with disagreement
carrying no within-rollout information at all. Two things pointed there: the
{{a2_h1_npoints}}-point h = 1 figure of {{a2_h1_r}}, which is not the shape of a genuine per-step
signal, and the within-step control coming out *above* the pooled figure, the signature of a
between-unit effect.

**The verdict.** The between-trajectory correlation is {{a2_r_between}} and the two components
contribute {{a2_share_between}}% and {{a2_share_within}}% of the pooled covariance, so a large
part of what §5.6 reports is a between-rollout effect. That reinterprets the within-step
control: it is a mean of {{d2r_win_n}} between-trajectory correlations, which is why it reads
{{d2r_win}} against the pooled {{a2_r_pooled}} rather than below it. The decisive statistic is the
double-demeaned one, and it survives: {{a2_rdd}} {{a2_rdd_ci}} at n_independent = {{a2_nind}},
against the rule's pre-committed threshold that the interval exclude zero and a minimum detectable
effect of {{p1_m45_mde}} from the bootstrap's standard error; a dilution study missed an effect of
{{p1_m45_undetected}} and caught one of {{p1_m45_detected}}. **The rule returns
{{m45_verdict}}**: with both the rollout and the depth held constant, disagreement still tracks
error rather than merely reporting which episode is hard.

Two qualifications go with that. The within-rollout effect is **materially smaller than the pooled figure**, {{a2_rdd}} against {{a2_r_pooled}}, so a practitioner should expect disagreement to separate *rollouts* better than it separates *moments within a rollout*. And it is **not established at short horizon**: r_dd's interval excludes zero at {{a2_excl_h}} and spans zero at {{a2_spans_h}}, where too few steps exist to demean against. At h = {{v2_deploy_h}} it is established, at {{a2_rdd_h100}} {{a2_rdd_ci_h100}}.

**The h = 1 figure survives the same test, but it is not what it looked like.** At h = 1 the panel
has one column, so {{a2_h1_r}} is a correlation over {{a2_h1_npoints}} *trajectory-level* points
and nothing within a rollout is being tested. Disagreement correlates {{a2_h1_speed_r}} with
commanded speed and {{a2_h1_diff_r}} with per-episode difficulty, and partialling both out of the
disagreement–error correlation leaves {{a2_h1_partial_both}}: it does not move, so the figure is
real and not a difficulty artifact. It is nevertheless a statement about **ranking whole rollouts
at one step ahead**, on {{a2_h1_npoints}} points, and §7 states it that way.

**Does it hold on a model we trained?** Everything else in §5.6 is measured on the released checkpoint, because our main arms run at ensemble size 1 where the epistemic term is identically zero. We therefore trained three Arm A arms at **ensemble size 5**, at {{iters_main}} training iterations and identical in every other setting, under a rule committed to git before the runs existed (rule M-43, Appendix E). It asked that disagreement lead the index at every horizon, and that the paired difference exclude zero at a majority of them.

**It returns {{e5_verdict}}.** The first condition passes completely: disagreement leads
the index in **{{e5_lead_cells}} of {{e5_total_cells}}** seed-horizon cells, every paired
estimate positive, {{e5_diff_lo}} to {{e5_diff_hi}}. The second fails: the paired difference
excludes zero at {{e5_n_excl}} of {{e5_n_horizons}} horizons, not a majority. We report the
verdict the rule returns and do not rewrite the rule, nor its denominator: it was committed over
{{e5_n_horizons}} horizons, and adding h = {{v2_deploy_h}} after the fact would change what "a
majority" means in a discharged rule. §5.6's released-checkpoint table follows the six-horizon
grid, because no pre-registration is stated over it, so the two counts are deliberately different.

**What separates the two conditions is sample size, and we measured that rather than asserting it.** Our own arms can only be scored out-of-sample on the held-out pair, n_independent = {{e5_nind}}, where the released checkpoint's finding used {{d1n_nind}}. Subsampling four trajectories at a time from a twenty-trajectory pool, the rule's criterion fires on {{e5_power_mean}}% of draws on average and on only {{e5_power_worst}}% at h={{e5_power_worst_h}}. That estimate is an **upper bound**, because the pool it subsamples is in-sample for these arms, where the effect is {{e5_eff_ins}} against {{e5_eff_oos}} on the held-out pair. So the rule was under-powered at the sample size it faced, decisively at one horizon. We do not claim it could not have passed, only that it was committed without checking what it could detect: a failure of ours, the same one the ledger records as M-24, a rule anchored without regard to the regime it would be applied in.

*Reported as a companion and not as a discharge:* on all ten episodes (n_independent = {{e5_comp_nind}} 400-step trajectories, **in-sample** for these arms, which trained on eight of them) the same measurement excludes zero at {{e5_comp_excl}} of {{e5_comp_n}} horizons and would have satisfied both conditions. It cannot discharge the rule, which is stated over the out-of-sample arena; we record it only so the comparison with the released checkpoint's {{d1n_nind}} is like for like.

*Why the within-step control is undefined for the forecast index.* The within-step control holds the forecast step fixed and
correlates across trajectories, so it annihilates any quantity that is constant across
trajectories at a fixed step — which is the forecast index, whose within-step correlation is
therefore {{e7_index_ws}} rather than zero. It does **not** annihilate a per-trajectory scalar
like `entry-res`, which varies across exactly the axis the control varies over. Rule M-51 said the
opposite, and `M-54` records the correction.

---

Rule X6 was committed and pushed before its readings existed (ledger M-88; Appendix E gives its lead time) and is
discharged in M-91. It is exploratory and re-opens no rule: rules M-51 and M-52 stand. It puts §5.6's comparison to
more units. The released checkpoint's ten episodes are cut into non-overlapping units of the model's history plus h
forecast steps, inside each episode, by rule M-64's index builder, at h = 32 and h = {{v2_deploy_h}}, which governs. The
statistic is rules M-51 and M-52's margin, r(disagreement, |error|) − r(step size, |error|) on the applied scalar, a
Pearson correlation over every (unit, step) cell, imported from their script; its 95% interval resamples whole units,
paired, {{boot_n_mc}} times (seed 0). The rule reads **DISAGREEMENT BEATS STEP SIZE** if the interval's lower bound is
above zero, STEP SIZE BEATS DISAGREEMENT if its upper bound is below zero, and NOT RESOLVED otherwise. The minimum
detectable effect was computed by rule M-51's method at this n before the reading, and governs nothing.

| h | units (rows each) | r(disagreement, error) | r(step size, error) | margin [95% interval] | minimum detectable margin (rule M-51's method) | partial r(disagreement given step size) [95% interval] |
|---|---|---|---|---|---|---|
| {{v2_deploy_h}} | {{x6_n_units}} ({{x6_unit_len}}) | {{x6_r_dis}} | {{x6_r_step}} | **{{x6_margin}} {{x6_ci}}** | {{x6_mde}} | {{x6_partial}} {{x6_partial_ci}} |
| 32 | {{x6_n_units_h32}} ({{x6_unit_len_h32}}) | {{x6_r_dis_h32}} | {{x6_r_step_h32}} | {{x6_margin_h32}} {{x6_ci_h32}} | {{x6_mde_h32}} | {{x6_partial_h32}} {{x6_partial_ci_h32}} |

**Arena: all ten episodes, the released checkpoint's training data, as non-overlapping units inside each episode;
n_independent = the unit count at each horizon. Checkpoint: the released one.** Bold, the reading, which
returns **{{x6_reading}}**; the h = 32 row is alongside, and its margin would carry {{x6_label_h32}}. Units from one episode are not independent of each other, and the interval resamples units,
not episodes; the statistic is a correlation over (unit, step) cells, not a ranking of units.

---

## Appendix M — Per-horizon recalibration

Detail behind §5.7: the constant scalar, the per-horizon table, whether multipliers transfer between models, and the nine-episode fit.

**The constant scalar (§5.7).** On the released checkpoint, each scalar fitted on one held-out episode's {{d3_nind_fit}} trajectories and scored on the other's: fitting at one step works at one step and nowhere else. On the epistemic term — the quantity the
method uses — a scalar of {{d2_epi_c_lo}}–{{d2_epi_c_hi}} brings h=1 coverage to
{{d2_epi_cov1_lo}}–{{d2_epi_cov1_hi}}%, essentially calibrated against the {{d2_target}}% target,
and leaves h=368 at {{d2_epi_cov368_lo}}–{{d2_epi_cov368_hi}}%. On the aleatoric term a scalar of
{{d2_ale_c_lo}}–{{d2_ale_c_hi}} gives {{d2_ale_cov1_lo}}–{{d2_ale_cov1_hi}}% at h=1 and
{{d2_ale_cov368_lo}}–{{d2_ale_cov368_hi}}% at h=368. Fitting over the whole rollout instead
drives one-step coverage to 100%, an interval wide enough to be vacuous where the model is
accurate, while at the far end its coverage depends on which episode fitted the multiplier. A constant multiplier cannot track an error
that grows while σ does not (§5.6), so for a *constant* scale "right shape, wrong scale" does not
survive.

**The per-horizon table and its reading (§5.7).** One multiplier per horizon is fitted on one held-out episode and evaluated on the other, in both directions, so no multiplier is ever scored on the episode that produced it. The two held-out episodes contribute {{d3_nind_tot}} non-overlapping 400-step trajectories between them, so each direction fits on n_independent = {{d3_nind_fit}} and is scored on the other {{d3_nind_fit}}. The last column repeats the test on Arm A at ensemble size {{d3x_ens}} and {{iters_main}} iterations ({{d3x_nseeds}} seeds), whose model never saw either episode:

| quantity | released checkpoint: cells unseen by the multiplier within {{d3_tol}} points of {{d3_target}}%, per-horizon c (unpowered) | same, constant c | per-horizon c fitted on the *other* model, both models scored (unpowered) | range of fitted c | Arm A, its own per-horizon c: cells within the band, unseen by the model too |
|---|---|---|---|---|---|
| aleatoric | **{{d3_ale_ok}} / {{d3_ale_cells}}** | {{d3_ale_const_ok}} / {{d3_ale_cells}} | {{d3x_ale_ok}} / {{d3x_ale_cells}} | {{d3_ale_c_lo}} – {{d3_ale_c_hi}} ({{d3_ale_cspread}}×) | {{d3x_own_ale_ok}} / {{d3x_own_ale_cells}} |
| epistemic | **{{d3_epi_ok}} / {{d3_epi_cells}}** | {{d3_epi_const_ok}} / {{d3_epi_cells}} | {{d3x_epi_ok}} / {{d3x_epi_cells}} | {{d3_epi_c_lo}} – {{d3_epi_c_hi}} ({{d3_epi_cspread}}×) | {{d3x_own_epi_ok}} / {{d3x_own_epi_cells}} |

On the released checkpoint every point estimate lands within {{d3_tol}} points of the {{d3_target}}% target for both quantities. **That absolute test is UNPOWERED here, as in the *different model* column:** `results/p4_transfer_power.json` scored this model under these very multipliers and found the {{d3_tol}}-point band resolvable at {{d3x_tol_res}} of {{d3x_tol_pairs}} quantity-by-horizon pairs, with a binding minimum detectable effect of {{d3x_umde_lo}}–{{d3x_umde_hi}} points. So a cell inside the band is compatible with a true coverage well outside it, and nothing here shows any cell is outside it either. The largest deviation over all {{d3_ncells_all}} held-out cells is {{d3_worst_q}} at h={{d3_worst_h}}, fitted on episode {{d3_worst_ep}} and scored on the other, at {{d3_worst_cov}}%, {{d3_worst_dev}} points off target. The two largest deviations are both on the {{d3_second_q}} term and {{d3_top2_same_side}} target — {{d3_worst_cov}}% at h={{d3_worst_h}} and {{d3_second_cov}}% at h={{d3_second_h}} — so the fitted multiplier is mildly **conservative** at the long horizons rather than unstable in both directions. The constant scalar manages {{d3_epi_const_ok}} of {{d3_epi_cells}}, and those are the h=1 cells it was fitted at. **On Arm A, where the episodes are unseen by the model as well, its own multipliers manage {{d3x_own_epi_ok}} of {{d3x_own_epi_cells}} epistemic and {{d3x_own_ale_ok}} of {{d3x_own_ale_cells}} aleatoric cells**, so the recipe that lands every released-checkpoint cell does not carry over intact to a model that has not seen the test episodes.

**Rule M-69 (§5.7).** **The fourth column: the table is a property of the model, not of the horizon.** Under rule M-69
(Appendix E), multipliers fitted on Arm A and scored on the released checkpoint, and the reverse, on
the same {{d3x_nind}} held-out trajectories, return **{{d3x_verdict}}** on the paired change in coverage
the arena can resolve: {{d3x_n_out}} of {{d3x_ncells}} governing cells, which are not independent tests, have an interval wholly outside
the ±{{d3x_band}}-point band, and Arm A's multipliers are {{d3x_ratio_lo}}× to {{d3x_ratio_hi}}× the
released checkpoint's at the same horizon (Appendix M). The *different model* column is the absolute
test, unpowered for the reason above, so it is reported and cannot move that verdict.

**The fourth column: the table is a property of the model, not of the horizon.** Everything else in §5.7 is established across *episodes*, on one model. Whether the same lookup table works on a *different* model is a separate claim, and rule M-69 (Appendix E) fixed what an answer would look like — criterion, arena, horizons and minimum detectable effect — before any cross-model multiplier was computed. Multipliers were fitted on Arm A at ensemble size {{d3x_ens}} ({{d3x_nseeds}} seeds) and scored on the released checkpoint, then the reverse, over the same {{d3x_nind}} held-out trajectories and {{d3_nhoriz}} horizons. The statistic the rule governs on is the **paired** change in held-out coverage, coverage under the other model's multiplier minus coverage under the same model's, on the same trajectories, because this arena can resolve that (largest minimum detectable effect {{d3x_pmde_hi}} points against the ±{{d3x_band}}-point band) and cannot resolve the absolute one. The verdict is **{{d3x_verdict}}**: of {{d3x_ncells}} governing cells, {{d3x_n_out}} have a 95% interval on the paired change lying entirely outside the band, {{d3x_n_in}} entirely inside and {{d3x_n_strad}} straddling an edge, and the largest paired change has magnitude {{d3x_worst_delta}} points. That is branch {{d3x_branch}} of the rule's three. Per direction the verdict is the same: fitting on Arm A, **{{d3x_verdict_a2r}}** ({{d3x_n_out_a2r}} of {{d3x_ncells_a2r}} cells outside the band); fitting on the released checkpoint, **{{d3x_verdict_r2a}}** ({{d3x_n_out_r2a}} of {{d3x_ncells_r2a}}). The plainest statement of the gap is the multipliers themselves: Arm A's are {{d3x_ratio_lo}}× to {{d3x_ratio_hi}}× the released checkpoint's at the same horizon.

**The *different model* column is the absolute test, and it is unpowered for the reason §5.7 gives**, so a cell inside its band is not evidence the multiplier transferred. It is reported because dropping it would hide that this arena cannot resolve it; it is not the verdict and cannot move it. §5.7's caution applies here unchanged and harder: the {{d3x_ncells}} governing cells are not {{d3x_ncells}} independent tests, the {{d3x_nseeds}} Arm A seeds share their training data and differ only in initialisation and ordering, and no P-value attaches to any count here. The two models also differ on several axes at once, so this bounds transfer between these two models rather than attributing it to any one difference.

**X7's alongside readings.** Alongside, the aleatoric term returns {{x7_ale_summary}}, one constant multiplier lands within the band at {{x7_const_word}} of the {{x7_n_h_word}} horizons, and the fitted epistemic multipliers differ by at most {{x7_cspread}}× across the ten folds.

Rule X7 was committed and pushed before its readings existed (ledger M-89; Appendix E gives its lead time) and is
discharged in M-92. It is exploratory and re-opens no rule: rules M-69 and M-70 stand. For each of the ten episodes, the
per-horizon multiplier is fitted on the other nine episodes' non-overlapping 400-step trajectories with §5.7's fitting
function, imported, and scores ±1σ coverage on that episode's own; pooled, each of the {{x7_n_traj}} trajectories is
scored once, by a multiplier not fitted on it. A horizon reads WITHIN BAND if the coverage's 95% interval lies within
{{d3_tol}} points of {{d3_target}}%, OUTSIDE BAND if it lies wholly outside that band, and UNRESOLVED otherwise. The
epistemic term governs, and the reading counts its horizons WITHIN BAND. The interval resamples the {{x7_n_traj}}
trajectories {{boot_n_mc}} times (seed 0), one draw shared across horizons.

| h | epistemic, per-horizon multiplier (the reading) | aleatoric, per-horizon multiplier | epistemic, one constant multiplier | epistemic, no multiplier | epistemic multiplier across the ten folds (smallest – largest) |
|---|---|---|---|---|---|
{{x7_table}}

**Arena: all ten episodes' {{x7_n_traj}} non-overlapping 400-step trajectories, n_independent = {{x7_n_traj}}, each
scored by a multiplier fitted on the other nine episodes. Checkpoint: the released one.** Each cell is ±1σ coverage in
percent with its 95% interval and, for the multiplied columns, its label; bold, the reading, **{{x7_summary}}**. The other
columns are alongside: the aleatoric term returns {{x7_ale_summary}}, and one constant multiplier, fitted the same way,
lands within the band at {{x7_const_word}} of the {{x7_n_h_word}} horizons. Every trajectory is unseen by its multiplier
but perhaps not by the model, whose training rows are not recorded (§3.2), so this says nothing about a model that has not seen the test
episodes (§5.7's Arm A column).

**±2σ under the same fits (post hoc).** Scored post hoc on the same fits, arena and draws (X7's ±1σ cells are reproduced
exactly first), ±2σ coverage under the per-horizon multiplier stays below the {{v3_cov_nominal2}}% a calibrated Gaussian
gives at every horizon, so §5.7's "not two-sigma" holds at each one, not only at h = {{v2_deploy_h}}.

| h | epistemic ±2σ, per-horizon multiplier | epistemic ±2σ, one constant multiplier | epistemic ±2σ, no multiplier |
|---|---|---|---|
| 1 | **{{n9_epi_perh_cov2_h1}} {{n9_epi_perh_cov2_h1_ci}}** | {{n9_epi_const_cov2_h1}} {{n9_epi_const_cov2_h1_ci}} | {{n9_epi_before_cov2_h1}} {{n9_epi_before_cov2_h1_ci}} |
| 8 | **{{n9_epi_perh_cov2_h8}} {{n9_epi_perh_cov2_h8_ci}}** | {{n9_epi_const_cov2_h8}} {{n9_epi_const_cov2_h8_ci}} | {{n9_epi_before_cov2_h8}} {{n9_epi_before_cov2_h8_ci}} |
| 32 | **{{n9_epi_perh_cov2_h32}} {{n9_epi_perh_cov2_h32_ci}}** | {{n9_epi_const_cov2_h32}} {{n9_epi_const_cov2_h32_ci}} | {{n9_epi_before_cov2_h32}} {{n9_epi_before_cov2_h32_ci}} |
| 100 | **{{n9_epi_perh_cov2_h100}} {{n9_epi_perh_cov2_h100_ci}}** | {{n9_epi_const_cov2_h100}} {{n9_epi_const_cov2_h100_ci}} | {{n9_epi_before_cov2_h100}} {{n9_epi_before_cov2_h100_ci}} |
| 128 | **{{n9_epi_perh_cov2_h128}} {{n9_epi_perh_cov2_h128_ci}}** | {{n9_epi_const_cov2_h128}} {{n9_epi_const_cov2_h128_ci}} | {{n9_epi_before_cov2_h128}} {{n9_epi_before_cov2_h128_ci}} |
| 368 | **{{n9_epi_perh_cov2_h368}} {{n9_epi_perh_cov2_h368_ci}}** | {{n9_epi_const_cov2_h368}} {{n9_epi_const_cov2_h368_ci}} | {{n9_epi_before_cov2_h368}} {{n9_epi_before_cov2_h368_ci}} |

**Arena and checkpoint as in the table above.** Each cell is ±2σ coverage in percent with its 95% interval.

---

## Appendix N — Defects in the released pipeline

Detail behind §6: the stale action across models and horizons, the spliced windows' cost, and the pipeline rows the ledger confirms.

**The held-out pair's per-trajectory values (§6).** §6's sentence on the held-out pair at h = {{v2_diag_h}} ended "…, with per-trajectory values {{ad_rel_traj}} and {{ad_nrmse_traj}}", relative-L1 and nRMSE.

**Our models under the stale pairing (§6).** For models trained under the causal pairing, the stale one also raises error, and how much depends on the arena. On their own training episodes' {{x2_n_ins}} trajectories it raises our {{iters_long}}-iteration Arm A's relative-L1 error by {{n5_ins_h1}}% {{n5_ins_ci_h1}} at h = 1 and {{n5_ins_h100}}% {{n5_ins_ci_h100}} at h = {{v2_deploy_h}}; on the held-out pair's {{ad_nind}} it changes it by {{n5_ho_h1}}% {{n5_ho_ci_h1}} at h = 1, which those trajectories cannot resolve, and by {{n5_ho_h100}}% {{n5_ho_ci_h100}} at h = {{v2_deploy_h}} (three-seed means, computed post hoc, `results/n5_stale_armA_ci.json`; Appendix N gives every model at every horizon). Whether the action matters to them at all is rule X2's question, which returns **{{x2_reading}}** below, with its caveat that every action in the data comes from one policy.

**The forecast shift (§6).** A percentage change depends on how accurate the model already is as much as on how much the action matters: measured as the shift in the forecast itself, the stale action moves our model's forecast at h = 8 by {{n5_delta_armA_h8}} and the released checkpoint's by {{n5_delta_rel_h8}} on their own training data (Appendix N), so at h = 8 the two respond about equally, and our model's larger percentages there reflect its smaller error, {{n5_err_armA_h8}} against {{n5_err_rel_h8}} relative-L1 (`results/n5_stale_armA_ci.json`); at h = {{v2_deploy_h}} the released checkpoint's forecast moves more, {{n5_delta_rel_h100}} against {{n5_delta_armA_h100}}.

Rule X2 was committed and pushed before any of its readings existed (ledger M-84; Appendix E gives its lead time) and
is discharged in M-85. It is exploratory and re-opens no rule. It asks whether our trained models condition their
forecasts on the action they are given. Only the actions the forecast steps read are changed, so the history and the
recurrent state that meets the first forecast action are untouched. E is the change in relative-L1 error, cumulative
over forecast steps 1..h, against the true actions: the ratio err(I) / err(true), less one, in percent; for our arms, the mean over
three seeds of each seed's E. Its 95% interval resamples whole trajectories, one resample for all seeds and both
interventions in each draw: exact over all {{boot_n_exact4}} ordered resamples on the held-out pair, {{boot_n_mc}} Monte Carlo resamples (seed 0) otherwise. The
interventions are the stale action (the released evaluation's offset), another trajectory's actions (a swap, each
trajectory taking the next one's), each action dimension's mean over the model's training rows, and the true actions
plus Gaussian noise at k times each dimension's training standard deviation (eight draws). **The readings** are Arm
A's, under the swap at h = 8 on its in-sample arena: **{{x2_reading}}** at {{iters_main}} iterations
({{x2_E_swap_2500}}% {{x2_ci_swap_2500}}) and at {{iters_long}} ({{x2_E_swap_10k}}% {{x2_ci_swap_10k}}). The criterion was fixed in the rule before any reading existed (M-84), and the first outcome that matches applies: RESPONDS TO THE ACTION if the point estimate is at least {{x2_thr_pct}}% and the interval's lower bound is above zero; ERROR FALLS WITH WRONG ACTIONS if the interval's upper bound is below zero; DOES NOT RESPOND MEASURABLY if its upper bound is below {{x2_thr_pct}}%; otherwise UNRESOLVED. The bar is deliberately low: the one-step-stale action alone raises the released checkpoint's error at h = 8 by {{adh20_rel_h8}}% over all ten episodes. What the rule establishes is that our forecasts depend on the action. It does not establish that they depend on it correctly: every action in the data comes from one policy, so a forecast under an action that policy would not take has no recorded outcome to check it against. Arm B and the
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
n_independent = {{ad_nind}}), out-of-sample for our arms and possibly in-sample for the released checkpoint (§3.2). Checkpoints as in
the first table.** No reading is made on this arena; every row is alongside.

| model, checkpoint | arena | stale action | another trajectory's actions | training mean | noise, k = {{x2_k_lo}} | noise, k = {{x2_k_hi}} |
|---|---|---|---|---|---|---|
{{x2_appV_delta}}

**Δ at h = 8, the relative-L1 of the forecast made with the changed actions measured against the forecast made with
the true ones (`rollout_eval.relative_error`), which is zero for a model that ignores its actions. Arenas: each model's
own training data ({{x2_n_ins}} trajectories for our arms, {{ad20_nind}} for the released checkpoint) and the held-out
pair ({{ad_nind}}). Checkpoints: Arm A and Arm B at {{iters_main}} and {{iters_long}} iterations, three seeds each; the
released checkpoint. Descriptive, no reading.** How far the interventions move the actions: on the forecast rows,
the action changes from one step to the next on {{x2_ctx_ins_frac}}% of steps on the in-sample arena,
{{x2_ctx_ho_frac}}% on the held-out pair and {{x2_ctx_ten_frac}}% over all ten episodes. A one-step shift moves the
action by {{x2_ctx_ins_stale}}, {{x2_ctx_ho_stale}} and {{x2_ctx_ten_stale}} of its spread (the mean absolute change from one step to the next over the mean absolute deviation from
the action's mean), and the swap by {{x2_ctx_ins_swap}}, {{x2_ctx_ho_swap}} and {{x2_ctx_ten_swap}}
(`results/action_sensitivity.json`).

**The stale action at every horizon (post hoc).** Section 6's figures for our models come from this table, computed after rule X2's readings with its machinery, imported (`results/n5_stale_armA_ci.json`). Each cell is E under the stale action, in percent, with its 95% interval; no cell is a reading.

| model, checkpoint | arena (trajectories) | {{n5_appV_hdr}} |
|---|---|---|---|---|---|---|---|
{{n5_appV_table}}

**Arenas: each model's own training data (the in-sample arena's {{x2_n_ins}} trajectories for our arms, all ten episodes' {{ad20_nind}} for the released checkpoint) and the held-out pair ({{ad_nind}}), n_independent equal to the trajectory count. Checkpoints: Arm A and Arm B at {{iters_main}} and {{iters_long}} iterations, three seeds each, E the mean of each seed's; the released checkpoint.** The cells at h ≤ {{v2_deploy_h}} are the stale-action rows of the first two tables.

---

**The design.** We trained a contaminated arm on
{{arm_contam_windows}} windows, the clean {{arm_clean_windows}} plus {{arm_splices}} splices, and,
because that confounds *content* with *count*, a duplication control adding the same
{{arm_splices}} windows as exact copies of windows already present.

The arm's contamination rate is {{arm_contam_pct}}%, against the reference pipeline's
{{contam_pct}}%. It is deliberately lower: we splice only the {{bound_both_train}} boundaries whose
*both* sides are training episodes, because {{bound_touch_holdout}} of the {{bound_total}} between the ten full
episodes put held-out rows into training, a leakage problem rather than a physics one that would have
invalidated our own comparison. So this experiment measures the cost of training on physically
impossible transitions, not the reference's full exposure.

Training loss over the final 250 iterations: duplication costs {{dup_cost_pct}}%, splicing costs
{{contam_cost_pct}}%. The bootstrap interval on duplicated − clean is
[{{dup_ci_lo}}, {{dup_ci_hi}}], including zero, so the rise is caused by splice content, not by
dataset size.

In rollout, across {{tw_cells}} cells ({{tw_design}}, at two horizons on two
metrics), contamination hurts in **{{tw_cc_cluster_hurt}}** of {{tw_cells}} and
helps in {{tw_cc_cluster_helped}} (Figure 8a). The control is inert, differing from clean in
{{tw_dc_cluster_helped}} cells.

**So "costs nothing" is too strong.** Splicing raises training loss by {{contam_cost_pct}}% against
duplication's {{dup_cost_pct}}%, and improves rollout in {{tw_cc_cluster_helped}} of {{tw_cells}}
cells: measured effects in opposite directions, the signature of regularisation. The spliced
windows contain transitions the model cannot fit, it fits the rest less tightly as a result, and it
rolls out slightly better. The defensible statement is that **at this rate the splices do not harm
rollout and appear to help slightly. The unmarked boundaries remain a real defect on leakage
grounds; the physically-impossible-transition component costs nothing detectable at this rate.**

---

**Pipeline rows.** Code facts are cited by file and line at the pinned upstream commits.

| finding | evidence (ledger ID, artifact) | bearing on the paper |
|---|---|---|
| The reset guard tests index *values* for truthiness, so a reset at the first row would be missed | B-02; `train.py:143` | Latent twice over: this dataset has no reset at its first row and marks none at all (§6) |
| The train/test split draws windows at random, and adjacent windows share all but one of their {{win_len}} rows, so the released test loss is not held out | B-03; `model_training.py:33` | The held-out arena (§3) is built from whole episodes and does not use this split |

## Appendix O — Paper–code differences

Where the released code departs from the papers' descriptions (§5.1, §5.3, §6), each row checked against the code at the pinned commits.

The ledger tags some of its entries as contributions of this project. These are the confirmed ones the
body does not state, or uses without stating the finding itself, each checked against its ledger entry.
Code facts are cited by file and line at the pinned upstream commits; every measurement is read from
the artifact named. Measurements are at {{iters_main}} training iterations unless a row says otherwise or concerns the released checkpoint, and each row names its arena.

| finding | evidence (ledger ID, artifact) | bearing on the paper |
|---|---|---|
| The papers name a forecast decay factor and set it to one in every version (RWM Table S9; RWM-U Table S8); the training loss averages every forecast step with equal weight, which is that setting | C-17 (which corrects C-09); `system_dynamics.py:186-231` and both config files | A difference of naming, not of behaviour; our training does the same |
| The auxiliary heads (contact and termination) are trained on true next states, the state head on its own samples | M-13; `system_dynamics.py:217, 261` | In a rollout the auxiliary heads read predicted states they never trained on; this paper compares states only (§4.3) and does not measure them |
| Training feeds back a reparameterised sample, inference the mean | C-05; `system_dynamics.py:115, 217` | Our arms train and roll out the same way; for the released checkpoint, whose per-member σ has collapsed (§5.5), the sample is numerically the mean |
| Actions enter the network raw (the config's action mean and standard deviation are zeros and ones), and no action scale is recorded in either repository; measured against joint motion, they are not joint targets in radians | C-07, D-07; `anymal_d_flat_cfg.py` | A perturbation of one size means different things for actions and for states; no reported result perturbs either |
| The release's configuration, the follow-up's paper (its Table S8 in the first version, {{iters_main}}) and the checkpoint's own tag state three different training lengths; the first author believes the configuration's is a typo | C-13; `base_cfg.py:97`, the checkpoint's `iter` field | §6: none of them reaches the released variance state at a constant rate |

**The training tables.** RWM-U's training table fixes the iteration count, the forecast decay and the learning rate at the values our arms use ({{iters_main}} iterations), in every version; the released configuration and the checkpoint's tag state other iteration counts (§6).

**Bootstrap ensembles.** RWM-U describes its members as a bootstrap ensemble. Per-head resampling exists in the online training path and not in the offline path that our arms and the released checkpoint follow (C-18).
