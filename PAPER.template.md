# Right Order, Wrong Size: A Verified Reproduction of the Robotic World Model and the Uncertainty It Reports

---

## Abstract

We rebuild the proprioceptive dynamics model of the *Robotic World Model* (arXiv:2501.10100v1)
and its uncertainty-aware follow-up (arXiv:2504.16680v1) from scratch on CPU, matching the released
implementation's outputs, losses and gradients exactly before training. With {{c2_pct}}% of the
reference's world-model data, one robot, gait and terrain, and {{nind_oos_400}} independent
held-out trajectories, the base paper's central training claim reproduces under a rule committed in advance and run on one seed
per arm: over {{d1_seeds}} seeds, training on the model's own rollouts beats teacher forcing {{d1_ratio}}× at
{{v2_diag_h}} steps and {{d1_ratio_h100}}× at {{v2_deploy_h}}, though teacher forcing leads at one step. RWM is ahead of MLP, RSSM and transformer baselines built to our reading of the original and
trained like it, though at {{v2_diag_h}} steps each does worse than predicting no change.
On accuracy alone, {{mn_better_kinds}} beat the original's chosen setting at
our budget, the best even when that setting trains longer; it was chosen as a trade-off with training time,
which we do not test. The follow-up's uncertainty gets the order right and the size wrong.
Ensemble disagreement, the method's reward penalty, correlates {{a2_r_pooled}} with
realised error ({{a2_rdd}} with rollout and depth held fixed), yet on the checkpoint's training data is {{d1n_epi_ratio_h1}}× smaller than that error at one step and
{{d1n_epi_ratio_h100}}× at the method's {{v2_deploy_h}}-step horizon. A free signal, the model's predicted step size,
ranks error nearly as well ({{e7_step_r}}), by an unresolved margin. The members share {{v1_shared_pct}}% of their parameters; at {{v2_deploy_h}} steps, five independent models are
{{r2_total_x_h100}}× better calibrated and still {{r2_indep_ratio_h100}}× overconfident. The implemented loss provably drives the per-member σ the method discards to zero, as data
with known noise confirm. A per-horizon rescaling brings the released checkpoint's
coverage within {{d3_tol}} points of nominal on its training episodes (no cell resolvable), and
only {{d3x_own_epi_ok}} of {{d3x_own_epi_cells}} disagreement cells on episodes our ensembles never saw:
a recipe to refit, not a demonstrated fix. Separately, the released evaluation pairs each prediction with the previous step's action, inflating error mainly at short horizons; at the longest the cost is small and not consistent in sign. We train no policy, so we bound what the uncertainty reports, not what its
miscalibration costs.

---

## 1. Introduction

A world model that reports its own uncertainty is more useful than one that does not, and the
uncertainty-aware Robotic World Model reports one. This paper asks what that number means,
and the title gives the answer: it gets the order of the model's errors right and their size
wrong.

We set out to reproduce the base paper: rebuild the proprioceptive dynamics model from scratch,
check it against the released implementation, and test the central training claim. The claim
holds. The rebuild then made a second question cheap to ask: *is the predicted σ calibrated?*
Neither of the two the checkpoint emits is. On data it trained on, the per-member σ is too small
by {{d1n_alea_ratio_h1}}× at h = 1 to {{d1n_alea_ratio_h368}}× at h = {{v2_diag_h}}, and the
ensemble disagreement the method actually uses by {{d1n_epi_ratio_h1}}× to {{d1n_epi_ratio_h368}}×
over the same horizons; the first failure is structural rather than incidental. The disagreement
still ranks realised error, which is the use the method makes of it (§6.7); what is wrong is its
size.

This is a reproduction in the stronger sense: the contribution is not that the numbers came out
the same, but what re-measuring the method reveals about where it is robust and where it is not.
Three things distinguish it from a re-run of the authors' code. **We rebuilt rather than
imported**, and matched the rebuild to the reference before any training (Appendix A), so a
discrepancy found later belongs to the method, not to our wiring. **Decision rules were committed
to git before the data**, with timestamps a reader can check (§8, Figure 1); one returned "cannot
be settled", and we report it. **We keep our withdrawn findings in the record.** The ledger keeps
{{n_superseded}} superseded entries, each beside the evidence that withdrew it:
{{n_retractions_lower}} claims withdrawn on evidence, {{n_retract_framing_word}} framings withdrawn,
and the rest early hypotheses closed as housekeeping (§8 and the supplementary
`docs/BUILD_CHECKS.md`). Appendix E gives every pre-registered rule with its lead time and its
verdict, and §9 gives the lessons in a form a practitioner can use without reading the rest.

**Contributions.**

- **The uncertainty gets the order right and the size wrong, in the first calibration
  measurement we are aware of for this released checkpoint** (Lu et al. (2022) measure this family
  of penalties on models they train themselves; §2). Ensemble disagreement ranks realised error,
  and still correlates {{a2_rdd}} with it with the rollout and forecast depth held fixed, yet on
  data the checkpoint trained on it is {{d1n_epi_ratio_h1}}× smaller than that error at h = 1 and
  {{d1n_epi_ratio_h100}}× at h = {{v2_deploy_h}} (§6.2, §6.7). It beats {{e7_n_beaten}} of the
  {{e7_n_new}} free baselines added here; the model's own predicted step size ranks error at
  {{e7_step_r}} against its {{e7_r_dis}}, a margin that {{q2_n_req}} independent trajectories would
  resolve if it is real, against the {{e7_nind}} here (§11).
- **The base paper's central training claim reproduces, and reverses at one step.** A rule committed before
  the runs, run on one seed per arm, found autoregressive training ahead by {{m23_ratio}}× at
  h = {{v2_diag_h}}; over {{d1_seeds}} seeds the factor is {{d1_ratio}}×, and {{d1_ratio_h100}}× at
  h = {{v2_deploy_h}} (§5). At one step a second pre-registered rule, on {{m64_h1_n}} independent
  {{m64_h1_unit}}-row units, finds a gap of {{m64_h1_gap}} {{m64_h1_ci}} in favour of **teacher forcing** (§5).
- **Two more of the base paper's claims, tested under rules committed before the runs.** RWM is
  ahead at h = {{v2_diag_h}} of MLP, RSSM and transformer baselines built to our reading of its
  specification and trained with RWM's settings, whether teacher-forced as the original trains them
  or autoregressively, though every baseline is worse there than predicting no change and our RSSM's
  open-loop collapse is not a matter of how its forecast is read (§5.3). On accuracy alone,
  {{mn_n_better_word}} of the {{mn_n_configs_word}} one-factor neighbours of the original's
  {{mn_centre_label}} beat it at our budget — {{mn_better_long_phrase}}, and the
  {{mn_n_short_better_word}} shorter histories {{mn_mvar_better_list}}, although the original's error
  falls steeply as the history grows to M = 8 — the best of them even when the centre trains longer;
  the original chose the centre as a trade-off with training time, which we do not test (§5.2).
- **The σ = 0 optimum of the implemented objective.** The implemented state loss is minimised at
  σ = 0, so the per-member σ the method discards collapses by construction: derived rather than
  observed, and demonstrated against known noise (§6.3).
- **Trunk-sharing, tested.** The five members share one trunk, one recurrent state and
  {{v1_shared_pct}}% of each member's parameters, so their spread can express only uncertainty the
  trunk already carries (§6.4). Under a rule committed before the runs, {{r2_n_indep}}
  independently initialised full models are {{m44_ratio_gain}}× better calibrated than the
  shared-trunk arms, against a pre-registered minimum detectable effect of {{m44_mde_ratio}}×, and
  still {{r2_indep_ratio_h100}}× overconfident at h = {{v2_deploy_h}} (§6.10).
- **Per-horizon recalibration, with mixed evidence.** One multiplier per horizon, fitted on one
  episode and scored on the other, brings every released-checkpoint coverage estimate near nominal
  where a global multiplier does not, though no single cell is resolvable (§6.8). Those cells are
  unseen by the multiplier only, because the checkpoint trained on both episodes; on Arm A, whose
  model never saw them, its own multipliers manage {{d3x_own_epi_ok}} of {{d3x_own_epi_cells}}
  disagreement cells.
- **The released evaluation is misaligned by one step; the cost is concentrated at short horizons, and at
  h = {{v2_diag_h}} it is small and not consistent in sign.** Evaluation feeds the action from *t−1* where
  training pairs states and actions index-for-index, and shifting its action index by one step fixes it. On
  the held-out pair's {{ad_nind}} independent trajectories, which this checkpoint trained on, the stale
  action raises its relative-L1 error by
  {{adh_rel_h1}}% {{adh_rel_ci_h1}} at h = 1, and at h = {{v2_diag_h}} by {{ad_rel}}% {{ad_rel_ci}} on
  relative-L1 and {{ad_nrmse}}% {{ad_nrmse_ci}} in nRMSE; over all ten episodes the sign at h = {{v2_diag_h}}
  reverses (§7.2).
- **A from-scratch reimplementation verified at the gradient level.** Outputs match the released
  module bitwise, and losses and gradients match to {{diff_grad_max}} across {{diff_terms}} loss
  terms and {{diff_n_params}} parameter tensors, before any training (Appendix A).

---

## 2. Related work

This paper asks whether an ensemble-disagreement penalty is calibrated, and separates its use as a
*ranking* from its use as a *scale*. Both questions have a literature, and one paper asked almost
exactly ours four years earlier; below we say which parts of what follows are new.

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
being "strikingly similar" to the latter but better behaved; §6.7 finds the same quantity a usable
ranking signal.

**What is new here is four things.** Lu et al. measure models they train themselves, on simulated
benchmarks, and their statistics describe ordering and shape, not coverage. We measure a
**released checkpoint** from a pipeline its authors deployed on hardware, where reading the penalty
as an interval has consequences; we measure **coverage** against a nominal; we verify our
reimplementation against the reference at the gradient level before any training (Appendix A); and
§6.3 derives the σ = 0 optimum for the objective the released code *substitutes*, squared error on
a reparameterised sample, rather than for the likelihood the parameterisation was built around.

**Where the parameterisation comes from.** The bounded log-σ head that §6.3 shows has its optimum
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
gap, where PETS keeps the two bounds independent. §6.3 needs both changes: the substitution removes
the log-σ term, and the tie is why the bound regulariser does not take its place, since the floor
cancels out of it. In a descendant that kept PETS's independent bounds, the same regulariser pushes
the floor up while the objective pulls σ down onto it, a case §6.3 does not derive and we have not
tested (ledger `M-72`). So **a descendant of this lineage that replaced the likelihood with a
sampled squared error, and left nothing pushing its variance floor back up, would inherit the same
optimum.** That is a hypothesis about mechanism, untested in any other descendant (§11).

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
hold. A further {{q1_n_absent}} repositories lack the construction, among them mainline `rsl_rl`:
the bounded head exists in the fork this paper pins, not in the library it forks, and we do not
count the fork, since counting what §6.3 measured as evidence that the result travels would be
circular. The protocol capped the survey at {{q1_cap}} repositories; it stopped at
{{q1_n_examined}}, and its notes give no reason. We wrote the protocol before the search, but
neither it nor its hash reached git before the results did, so that order rests on our own record;
it is a search protocol, not one of Appendix E's decision rules. Search engines rank and truncate,
so this is a sample of convenience, but on it the substitution is rare, and a reader who takes the
hypothesis to reach widely infers more than the evidence supports.

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
which is precisely the component that compounds with rollout depth: the shape §6.9 reports.

**Why miscalibration is the expected finding.** Modern networks are systematically miscalibrated
(Guo, Pleiss, Sun and Weinberger, ICML 2017), and calibration degrades further under covariate
shift, worsening with distance from the training distribution (Ovadia, Fertig, Ren, Nado, Sculley,
Nowozin, Dillon, Lakshminarayanan and Snoek, NeurIPS 2019). An autoregressive rollout manufactures
its own covariate shift, increasing with depth, so horizon-dependent calibration failure is what
one should expect; our contribution on this axis is the *magnitude* and the *mechanism*, not the
direction. §6.8's per-horizon multiplier is a coarse instance of calibrated regression (Kuleshov,
Fenner and Ermon, ICML 2018), a post-hoc map fitted on one episode and scored on another, applied
to a horizon index; we do not present it as a new idea.

**The closest published work to our one constructive result.** Malik, Kuleshov, Song, Nemer,
Seymour and Ermon (ICML 2019) recalibrate a dynamics model's uncertainty inside model-based RL,
and argue that "good uncertainties must be calibrated" rather than merely well ranked, the
distinction §6.2 and §6.7 draw. §6.8 is a horizon-indexed instance: a single global multiplier
**fails**, its fitted value varying across horizons, where a per-horizon one puts every
released-checkpoint estimate within its tolerance band, though those cells are unseen by the
multiplier but not by the model and no single cell is resolvable (§6.8). An open-loop rollout's
error accumulates with depth, so a horizon-blind recalibration cannot follow it.

**§6.4's mechanism is known, and we say so.** That heads sharing a trunk under-report disagreement
relative to independently initialised networks is established: Lee, Purushwalkam, Cogswell,
Crandall and Batra (arXiv:1511.06314) treat ensemble diversity as something to engineer rather than
assume; Fort, Hu and Lakshminarayanan (arXiv:1912.02757) show that independent initialisation buys
a decorrelation subspace methods do not match; and BatchEnsemble (Wen, Tran and Ba, ICLR 2020) and
MIMO (Havasi, Jenatton, Fort, Liu, Snoek, Lakshminarayanan, Dai and Tran, ICLR 2021) share
deliberately and state what they trade away. **What is ours is finding it in a released robotics
checkpoint, with the sharing quantified at {{v1_shared_pct}}% of each member and the cost measured
at {{m44_ratio_gain}}× (§6.10).** The problem is not sharing; it is sharing and then reading the
spread as though the members were independent.

**And the objective in §6.3 has a neighbour.** Seitzer, Tavakoli, Antic and Martius (ICLR 2022)
identify failure modes of heteroscedastic σ heads trained by maximising log-likelihood. The
released model's state loss is not a log-likelihood at all (a *sample* enters a squared error), so
the failure §6.3 derives is more basic than theirs and does not depend on the optimiser. §6.3
derives it and demonstrates it against known noise.

*Every entry cited here and in §5.3 was checked against the paper itself: title, full author list
and year from the arXiv record, venue from the record or, where it names none, from the paper's own
first page, and every sentence we attribute matched verbatim against the paper's text.
{{t1_n_verified}} of {{t1_n_refs}} entries are verified and {{t1_n_frag_ok}} of {{t1_n_frag}}
attributed fragments match verbatim, though {{t1_n_frag_oneword}} of those are single common words
whose match verifies nothing about the attribution (`results/t1_bibliography_verified.json`). No
entry was added that was not verified.*

---

## 3. Setup

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
terms; the implementation has {{diff_terms}}.

**Evaluation.** Two arenas, kept separate throughout: *out-of-sample*, the two episodes withheld
from training, and *in-sample*, the eight used for it. The released evaluation draws its
trajectories from training data, and the original does not distinguish the two. **The released
checkpoint trained on all ten episodes, so it has no held-out arena in this dataset**, and every
figure for it is in-sample; later sections refer back to this as the in-sample caveat of §3. More
data cannot be generated from either repository this reproduction pins. Neither contains code that
writes a dataset: the only code that touches the file reads it (`train.py:44` in the lite release),
and the lite release's environment rolls the learned model forward rather than physics. Its readme
sends anyone wanting simulator-based collection to the authors' Isaac Lab extension
(`readme.md:13`), which we do not pin and which would need Isaac Lab and an RTX-class GPU
(Appendix C).

**Effective sample size.** Trajectory count is not sample size. Two 400-step trajectories whose
spans overlap are not independent evidence, and the out-of-sample arena contains only
{{m23_nind}} mutually non-overlapping 400-step trajectories. A bootstrap over whole trajectories at
that size has {{c3_resamples}} distinct resamples, so its intervals are quantised at that
resolution. Every long-horizon verdict in this paper survives a bootstrap over independent
trajectories, every table reports that count, and §8 reports both resampling units where they
differ. Later sections refer back to this as the n = {{m23_nind}} caveat of §3. One trajectory can carry
much of a long-horizon effect: a one-step shift of the action moves the released checkpoint's
{{v2_diag_h}}-step relative-L1 error on single trajectories of its own training episodes by anywhere from
{{ad20_traj_lo}}% to {{ad20_traj_hi}}% (§7.2), which illustrates why {{m23_nind}} trajectories bound every
long-horizon claim.

### 3.1 Metrics

Each metric is stated as implemented, with the `file:line` of its implementation, because a reader
who cannot see the denominator cannot check the headline.

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
from held-out data. A value of 1.0 means no better than predicting the training mean. **The
aggregation is form 1**: pool the per-dimension mean squared errors, then divide, a ratio of means.
A mean of per-dimension ratios gives whichever dimension has the smallest scale unbounded leverage;
Appendix G gives both forms and the comparison the second one inverts.

**Coverage at ±kσ** is the fraction of scalar (trajectory, forecast step, state dimension) triples
whose absolute realised error falls within k times the σ predicted for that same triple:

$${{v3_coverage}}$$

It is pooled over all three axes with equal weight per triple. It is **cumulative** over steps
1..h: coverage "at h" averages the whole rollout up to h and is not the value at step h, and every
horizon-indexed quantity in this paper follows the same convention. Because it is built from an
*absolute* error, $z \le k$ is the two-sided event, so the calibrated targets are
$\mathrm{erf}(k/\sqrt{2})$: **{{v3_cov_nominal1}}%** at ±1σ and **{{v3_cov_nominal2}}%** at ±2σ.
**That nominal is checked rather than assumed.** Rescaling each model's σ by the single constant that makes mean|error| / mean σ equal a calibrated Gaussian's {{m65_calib_ratio}} lands coverage at or above {{v3_cov_nominal1}}% in every one of {{m65_n_cells}} model × horizon cells, with {{m65_n_heavy}} below it (`M-65`), so the shortfalls reported below are a property of the scale and not of the tail.

**The overconfidence factor** is how many times larger the typical realised error is than the
typical predicted σ:

$${{v3_rho}}$$

It too is a **ratio of means**, because a mean of ratios is unbounded whenever a single σ
approaches zero, which is exactly the regime §6.3 puts these models in. $\rho = 1$ is *not*
calibration: a calibrated Gaussian has mean|error| / σ = $\sqrt{2/\pi}$ = {{v3_rho_calibrated}}. So
$\rho$ is reported as a magnitude of miscalibration and coverage as the calibrated reading, and
both appear everywhere.

**Which metric each headline uses.** The A/B training claim (§5) is relative-L1, because the claim
is about reproducing the upstream's comparison and that is the upstream's metric. The calibration
claims (§6.2) are the overconfidence factor and coverage, because neither error metric involves σ.
The ranking claims (§6.7) are Pearson correlations between the applied scalar penalty and total
absolute error, because a ranking claim is about order rather than scale. Every headline number in
the abstract names its metric. §7.2's alignment defect is given in both metrics side by side at h = {{v2_diag_h}}, on the same
{{ad_nind}} independent trajectories: {{ad_rel}}% {{ad_rel_ci}} on relative-L1 and {{ad_nrmse}}%
{{ad_nrmse_ci}} in nRMSE; its larger cost at short horizons is given on relative-L1, at h = 1.

**Horizons.** Curves are reported at $h \in \{1,\,8,\,32,\,{{v2_deploy_h}},\,128,\,{{v2_diag_h}}\}$.
Two of those are load-bearing and the rest are landmarks. **h = {{v2_deploy_h}}** is the method's
own imagination rollout length, the horizon over which the uncertainty-penalised policy loop
actually runs this model (arXiv:2504.16680 Table S9 in v1 and Table S11 in v3, with the same
value). **h = {{v2_diag_h}}** is the upstream's open-loop diagnostic length: `len_eval_trajectory` =
{{v2_len_eval}} minus the {{v2_history}}-step teacher-forced prefix, the curve the follow-up plots
as its uncertainty figure. It is {{v2_ratio}}× the method's own rollout length and is not a
deployment horizon. Every table keeps both: h = {{v2_diag_h}} makes our numbers comparable to the
original's *figure*, and h = {{v2_deploy_h}} to its *method*.

### 3.2 What each claim rests on

Every headline claim in this paper is measured on one of the three arenas above, at a stated
number of independent trajectories, and at one checkpoint: the released one, or ours at a stated
number of training iterations. The table is generated from the artifacts each claim is computed
from, so no arena label, sample size or checkpoint in it is typed by hand.

| claim (§) | arena (n_independent) | checkpoint | in-sample for the model measured? | verdict | survives multiplicity correction? |
|---|---|---|---|---|---|
{{evidence_table}}

---

## 4. What the original papers claim, and which claims we test

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
The counts and lists are generated from the classification tags in Appendix D's verdict
column, and they replace a withdrawn claim that every untested claim concerns policy learning or
hardware (`S-17`). §11 states what the untested claims bound, and Appendix C what testing them
would take.

**For {{orig_n_without_word}} of the {{orig_n_tested_word}} claims we tested, the original reports no quantitative
figure.** Each is asserted qualitatively and shown in a plot, with no number in text, caption or
table; §6.7's coefficient is the first figure attached to the follow-up's "strong correlation"
between disagreement and error. The exceptions are the configuration claim and the teacher-forcing
claim, whose values one heatmap prints in every cell (§5.2). For the teacher-forced {{mn_n1_label}}
it prints {{orig_tf_e_n1}} against {{orig_tf_e_centre}} at the centre, {{orig_tf_ratio}}× worse, on
evaluation data and at a horizon it does not state; our sweep's {{mn_n1_label}} is
{{mn_tf_ratio}}× worse on relative-L1 at h = {{v2_diag_h}}. Our {{d1_ratio}}× uses a different definition of teacher forcing
(`docs/presubmission/ORIGINAL_SPECS.md` §2); §5 relates the two. Where a magnitude is legible only from a plotted curve we say so rather
than estimating it from the axis.

**Appendix D gives the full table**, claim by claim, with what the original states, where it
states it, and our verdict.

---

## 5. The base paper's central claim reproduces

**Claim under test.** Training the dynamics model on its own autoregressive rollouts beats training it with teacher forcing, at long forecast horizons.

**Rule, committed in advance** (rule M-23, Appendix E; commit `efc35b8`), naming conditions rather
than outcomes. Three conditions, all required: the out-of-sample gap at h = 368 excludes zero
under a bootstrap over independent trajectories; the sign is consistent across episodes; and the effect survives at 10,000 iterations rather than only at the paper's 2,500. The rule was run on
seed {{m23_seed}} of each arm: autoregressive {{m23_A_s1}} against teacher forcing {{m23_B_s1}} at
h = {{v2_diag_h}}, {{m23_ratio}}×, gap interval [{{m23_ci_lo}}, {{m23_ci_hi}}]. The {{iters_long}}-iteration runs of seeds
{{m23_other_seeds}} were trained after the verdict (ledger R-60, entered {{r60_date}}), so the three-seed
figures below extend it
and carry none of its weight. The rule is anchored at
h = {{v2_diag_h}}, the upstream's **open-loop diagnostic** length and not a deployment horizon
(§3.1), and its verdict is returned there; we do not re-anchor a discharged rule. The method's own
horizon is h = {{v2_deploy_h}}, so the comparison is reported there too, and the two differ in size.

**Result.** Every condition {{m23_c1}}. We give the evidence in order of how little it depends
on the small held-out sample.

*The sign test, which does not depend on n.* At h = {{v2_diag_h}} the per-episode gap favours autoregressive training on **{{c3_sign_pos}} of {{c3_sign_n}}** episodes, an exact two-sided binomial test with p = **{{c3_sign_p}}**. At h = {{v2_deploy_h}} it is **{{a1_sign_pos_h100}} of {{a1_sign_n_h100}}**, p = **{{a1_sign_p_h100}}**, and at h = 1 it is {{a1_sign_pos_h1}} of {{a1_sign_n_h1}}, the same story the interval tells. It is one test on ten paired episodes, with no bootstrap and no multiplicity correction, and unlike §6's per-dimension counts, episodes are separable units, so a binomial null is admissible. **Its scope is narrower than the arena labels suggest**: {{n_train_eps}} of the {{c3_sign_n}} episodes are training data for *both* arms. The test is a valid **paired** comparison, since both arms saw identical data and an episode-level difference is due to the training rule rather than to memorisation, but it is not ten out-of-sample episodes and does not measure generalisation. The out-of-sample effect size below carries that burden, on {{nind_oos_400}} independent trajectories.

*The in-sample arena, where the sample is larger.* The same comparison on the eight training
episodes has {{nind_ins_400}} independent 400-step trajectories against the held-out arena's
{{nind_oos_400}}, {{nind_ratio}}× more, and gives the same direction at every horizon and checkpoint
but one: at h = 8 after 500 iterations teacher forcing leads in-sample, with an interval that
excludes zero at both trajectory lengths (`results/review_bootstrap_unit.json`).

*The out-of-sample effect size, at every horizon.* At h = {{v2_diag_h}}, the rule's horizon, the
three-seed extension puts autoregressive training at **{{d1_A_mean}} ± {{d1_A_sd}}** against teacher forcing's
**{{d1_B_mean}} ± {{d1_B_sd}}** (standard deviation over seeds, `ddof=1`), a factor of **{{d1_ratio}}×**. Arm B predicts each of the window's {{win_fore}} forecast targets from
true inputs, where the original's teacher forcing is N = 1; the sweep's {{mn_n1_label}}, trained that way, is
{{mn_tf_ratio}}× worse than the centre at h = {{v2_diag_h}} at {{iters_main}} iterations (§5.2), so the direction
holds under both definitions.
At h = {{v2_deploy_h}}, the method's own imagination rollout length and the
horizon everything in §6 is anchored to, the same three seeds give **{{d1_ratio_h100}}×**.
Quoting one and not the other would be a choice, so we report the curve (Figure 2): same rollouts,
same {{d1_seeds}} seeds at {{iters_long}} training iterations, same held-out arena,
n_independent = {{a1_nind}}, with a cluster bootstrap over whole trajectories:

| h | autoregressive | teacher forcing | ratio | gap [95% CI] | excludes 0 | hold-last floor | A vs floor | B vs floor | episodes A leads |
|---|---|---|---|---|---|---|---|---|---|
| 1 | {{a1_A_h1}} ± {{a1_A_sd_h1}} | {{a1_B_h1}} ± {{a1_B_sd_h1}} | {{a1_ratio_h1}}× | {{a1_gap_h1}} {{a1_gap_ci_h1}} | **{{a1_excl_h1}}** | {{a1_floor_h1}} | {{a1_floor_over_A_h1}}× | {{a1_B_over_floor_h1}}× | {{a1_sign_pos_h1}}/{{a1_sign_n_h1}} |
| 8 | {{a1_A_h8}} ± {{a1_A_sd_h8}} | {{a1_B_h8}} ± {{a1_B_sd_h8}} | {{a1_ratio_h8}}× | {{a1_gap_h8}} {{a1_gap_ci_h8}} | {{a1_excl_h8}} | {{a1_floor_h8}} | {{a1_floor_over_A_h8}}× | {{a1_B_over_floor_h8}}× | {{a1_sign_pos_h8}}/{{a1_sign_n_h8}} |
| 32 | {{a1_A_h32}} ± {{a1_A_sd_h32}} | {{a1_B_h32}} ± {{a1_B_sd_h32}} | {{a1_ratio_h32}}× | {{a1_gap_h32}} {{a1_gap_ci_h32}} | {{a1_excl_h32}} | {{a1_floor_h32}} | {{a1_floor_over_A_h32}}× | {{a1_B_over_floor_h32}}× | {{a1_sign_pos_h32}}/{{a1_sign_n_h32}} |
| **{{v2_deploy_h}}** | **{{a1_A_h100}} ± {{a1_A_sd_h100}}** | **{{a1_B_h100}} ± {{a1_B_sd_h100}}** | **{{a1_ratio_h100}}×** | **{{a1_gap_h100}} {{a1_gap_ci_h100}}** | **{{a1_excl_h100}}** | {{a1_floor_h100}} | **{{a1_floor_over_A_h100}}×** | **{{a1_B_over_floor_h100}}×** | **{{a1_sign_pos_h100}}/{{a1_sign_n_h100}}** |
| 128 | {{a1_A_h128}} ± {{a1_A_sd_h128}} | {{a1_B_h128}} ± {{a1_B_sd_h128}} | {{a1_ratio_h128}}× | {{a1_gap_h128}} {{a1_gap_ci_h128}} | {{a1_excl_h128}} | {{a1_floor_h128}} | {{a1_floor_over_A_h128}}× | {{a1_B_over_floor_h128}}× | {{a1_sign_pos_h128}}/{{a1_sign_n_h128}} |
| **{{v2_diag_h}}** *(the rule's horizon)* | **{{a1_A_h368}} ± {{a1_A_sd_h368}}** | **{{a1_B_h368}} ± {{a1_B_sd_h368}}** | **{{a1_ratio_h368}}×** | **{{a1_gap_h368}} {{a1_gap_ci_h368}}** | **{{a1_excl_h368}}** | {{a1_floor_h368}} | **{{a1_floor_over_A_h368}}×** | **{{a1_B_over_floor_h368}}×** | **{{a1_sign_pos_h368}}/{{a1_sign_n_h368}}** |

**The advantage {{a1_monotone}} grow monotonically with forecast depth.** Over 400-step
trajectories the gap excludes zero at {{a1_n_excl}} of {{a1_n_horizons}} horizons and
spans it at {{a1_spans_zero_at}}: h = {{v2_diag_h}} is the end of a trend rather than a point we
picked, h = {{v2_deploy_h}} sits partway along it, and the claim is weakest exactly where the
model is trained. **Only the h = {{v2_diag_h}} row is the rule's horizon, and the rule ran on seed {{m23_seed}} alone.** Every
value in the table is a three-seed mean computed after the data existed, so by this paper's own standard (§8)
none carries a pre-registration's weight, the same treatment §6.7 gives the expectation we held about the
counter-baseline, and nothing in the table discharges or re-opens the rule.

**At h = 1 the table understates the evidence, and the correction runs against us.** The row
rests on {{a1_nind}} independent 400-step trajectories. A 400-step unit is required only by the
longest horizon. Under a rule committed before the index was built (rule M-64, Appendix E), we
rebuilt it at {{m64_h1_unit}} rows, 32 of history and one forecast step, non-overlapping within an
episode, which yields {{m64_h1_n}} units on the same two episodes. The gap is {{m64_h1_gap}}
{{m64_h1_ci}}: it **excludes zero, in favour of teacher forcing** ({{m64_h1_ratio}}×). Both
readings are true at their own unit and both are reported: the 400-step unit is the one the rule above was discharged on, and the short unit resolves the sign. At one step **autoregressive
training is worse**, the direction the sign test and the hold-last floor already pointed.

*Against a baseline, because neither number means anything without one.* The hold-last
floor, predicting that nothing changes, scores **{{a1_floor_h368}}** in the h = {{v2_diag_h}}
cell, and autoregressive training beats it by **{{a1_floor_over_A_h368}}×** there and by
{{a1_floor_over_A_h100}}× at h = {{v2_deploy_h}}. **Teacher forcing is
{{a1_B_over_floor_h368}}× worse than assuming nothing changes at all** at h = {{v2_diag_h}}, and
{{a1_B_over_floor_h100}}× worse at h = {{v2_deploy_h}}: the arm that reaches a lower training loss
predicts the future worse than a model that makes no prediction, at {{a1_B_worse_than_floor_at}}
we measured. That is the sharper statement of what exposure bias costs here. **The floor is not a
weak baseline everywhere**: at {{a1_A_worse_than_floor_at}} it beats the autoregressive arm as well,
scoring {{a1_floor_h1}} at h = 1 against autoregressive training's {{a1_A_h1}}, the only horizon where the autoregressive arm loses to predicting no change. At 50 Hz one step is 20 ms and the state
barely moves, so that is what one should expect.

*Seeds, and what four trajectories can show.* Seed spread is not symmetric between the arms: Arm A
ranges {{d1_A_lo}}–{{d1_A_hi}} across seeds ({{d1_A_relsd}}% relative), Arm B
{{d1_B_lo}}–{{d1_B_hi}} ({{d1_B_relsd}}%). Teacher forcing is more than twice as variable across
seeds as autoregressive training at this horizon, so a single-seed comparison of these two arms is
unreliable. For a single seed the bootstrap over trajectories gives the 95% interval
[{{m23_ci_lo}}, {{m23_ci_hi}}] on n = {{m23_nind}} independent trajectories; by the n = {{m23_nind}}
caveat of §3 its tails move in steps of {{c3_quant}}%, so it corroborates the sign test rather
than being the primary evidence. The four per-trajectory gaps behind it (Arm B minus Arm A, three
seeds pooled, at h = {{v2_diag_h}}) are **{{a1_gap_traj_h368}}**. All
{{a1_gap_traj_n_positive_h368}} of {{a1_gap_traj_n_h368}} are positive, which is the sign test,
but one trajectory carries {{a1_gap_traj_max_h368}} against a smallest of
{{a1_gap_traj_min_h368}}, which no interval on four units shows. At h = {{v2_deploy_h}} the four
are {{a1_gap_traj_h100}}. §6.10's and §11's paired contrasts at the same n store their four
per-trajectory values in `results/r2_independent_ensemble.json` and
`results/m49_capacity_matched.json`; §6.2's two held-out tables, at n_independent = {{b2_nind}},
give intervals only, coarse for the same reason.

**What is small, and where it resolves.** At h = 8, the horizon the model is trained on, the
advantage is small, and it resolves only with the longer training and all {{d1_seeds}} seeds. The table
above, at {{iters_long}} iterations with {{d1_seeds}} seeds pooled, gives an h = 8 gap of {{a1_gap_h8}}
{{a1_gap_ci_h8}}, which excludes zero, a factor of {{a1_ratio_h8}}×. The single seed the rule was
run on (seed {{m23_seed}}) gives an h = 8 gap of {{m23_h8_gap}} at the same {{iters_long}}-iteration checkpoint,
and its interval {{m23_h8_excl}}. At the {{bu_ckpts}}-iteration checkpoints, with all {{d1_seeds}} seeds
pooled, the out-of-sample gap excludes zero in **{{ab_short_excl}} of {{ab_short_cells}}** h = 8 cells (both
trajectory lengths crossed with both checkpoints). An earlier rule of ours, anchored at h = 8 and
evaluated at those same checkpoints (rule M-16, Appendix E), returned "cannot be settled".
**The advantage is small at the training horizon and large beyond it.**

At long horizons the pattern is consistent across the design. Under the cluster bootstrap, the
out-of-sample gap excludes zero in **{{ab_long_excl}} of {{ab_long_cells}}** long-horizon cells,
both trajectory lengths crossed with the {{bu_ckpts}}-iteration checkpoints. These figures are
relative-L1; the nRMSE aggregation is reported separately and does not change the direction.

**Multiplicity.** Those {{ab_long_cells}} cells sit in a family of {{c3_family}} out-of-sample
comparisons. All {{c3_bonf_excl}} of {{c3_long}} still exclude zero at a Bonferroni level of
0.05/{{c3_family}}, and Holm–Bonferroni rejects **{{c3_holm_rejected}} of {{c3_long}}**. The sign
test above is unaffected either way.

**How good the reimplementation is as a model, next to the artifact it reimplements.**
The tables above compare two training rules with each other and §6.2's compares calibration, so
neither puts the released checkpoint and our arms side by side on absolute accuracy. Both
aggregations, for those and for §5.3's architecture baselines, and one arena:

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
{{h2h_ntraj}} non-overlapping {{h2h_unit}}-step trajectories, n_independent = {{h2h_nind}}.**
Arm rows are the mean over {{h2h_nseeds}} seeds at {{iters_main}} training iterations (the `{{h2h_arm_ckpt}}` checkpoint), with
per-seed values in `results/head_to_head_accuracy.json`; nRMSE is form 1 (§3.1), and both metrics
are cumulative over forecast steps 1..h. Every RWM row is read from the stored rollouts behind §6.2's
calibration tables, so no model is run to build it. The architecture-baseline rows (§5.3) come from
their own evaluator on the same four trajectories, whose relative-L1 reproduces the Arm A row
exactly; their nRMSE is pooled as §3.1 defines it, recomputed afterwards from the same rollouts
(post hoc, `results/pooled_nrmse_rescore.json`), and † marks a diverged row (§5.3). **This table is at {{iters_main}} iterations and §5's by-horizon table at {{iters_long}}**, which is why Arm A's relative-L1 at h = {{v2_diag_h}} reads {{h2h_armA_l1_h368}} here and {{a1_A_h368}} there: the same arm, trained longer.

Both metrics put the released checkpoint first at {{h2h_released_sweeps_at}}, they name
different leaders at {{h2h_split_at}}, and at {{h2h_armA_sweeps_at}} both put an Arm A variant
ahead of it: the reimplementation is behind the artifact it reimplements at short horizons and
ahead of it at the longest horizon we measure. That reading flatters the released checkpoint, because the split is ours: the arena is
out-of-sample for our arms and in-sample for it, which trained on all
{{h2h_ckpt_neps_word}} episodes (the in-sample caveat of §3).

### 5.1 The data budget, which is the one part of the sample-efficiency claim we can measure

The base paper's headline is a sample-efficiency result: policies transfer to hardware from {{c2_ref}} state transitions of world-model pretraining against ~250M for the model-free baseline (Table I). That is a claim about policy learning and hardware, which we cannot test, but its *world-model* half is a quantity we can count exactly.

**Our arms consume {{c2_trans}} distinct state transitions**: the {{c2_rows}} rows of the eight training episodes less one per episode boundary ({{c2_bounds}} of them), a transition being a consecutive pair of rows inside one episode. It is deliberately not the {{c2_windows}} training windows, which overlap almost completely (consecutive {{win_len}}-row windows start one row apart), nor the {{c2_draws}} window draws a run makes, which resample the same data with replacement. Against the reference's {{c2_ref}}, that is **{{c2_ratio}}× less data, {{c2_pct}}% of its world-model budget**.

A dynamics model trained on {{c2_pct}}% of the reference's data still reproduces the training result, {{d1_ratio}}× at h = {{v2_diag_h}} and {{d1_ratio_h100}}× at h = {{v2_deploy_h}}, and still beats the hold-last floor, by {{floor_over_A}}× and {{a1_floor_over_A_h100}}× at those two horizons. That is what this paper can add to the sample-efficiency question without training a policy.

**Three limits.** It is not a reproduction of the {{c2_ref}}-against-250M comparison, which is about policy learning. It says nothing about whether a policy trained inside our model would transfer to hardware, or anywhere. And our model is evaluated on the narrow distribution it trained on (one robot, one gait, one terrain, velocity commands from a single bounded box), where the reference's {{c2_ref}} transitions span considerably more; a smaller data budget buys less than it appears to when the evaluation distribution shrinks with it.

### 5.2 The configuration claim: history and forecast horizons

**Claim under test.** The model reads a history of M past steps and, in training, forecasts the
next N steps from its own predictions. The base paper sweeps both and says that moderate values give
an optimal trade-off between accuracy and training time, with {{mn_centre_label}} as the instance
(§IV-C). Its heatmap prints the error of every cell, and the centre's is the tied-lowest, level with
its longest-forecast neighbour (`docs/presubmission/ORIGINAL_SPECS.md` a.5).

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
The rules' evaluator averaged nRMSE per trajectory, where §3.1 pools it. The nRMSE readings quoted
alongside the rules here and in §5.3 are pooled, recomputed afterwards (post hoc; ledger R-77,
`results/pooled_nrmse_alongside.json`), and return what the averaged ones did everywhere except
{{n2_n_changed_word}} in-sample readings of §5.3's rules: {{n2_changed_list}}.

**Result: {{mn_verdict}}.** {{mn_better_list}} beat the centre, {{mn_worse_list}} are worse, and
{{mn_unres_list}} cannot be told apart from it. At h = {{v2_diag_h}} the lowest error is {{mn_best_config}}'s,
{{mn_best_l1_h368}} against the centre's {{mn_centre_l1_h368}}, a difference of {{mn_best_D}}
{{mn_best_ci}}. The verdict does not rest on the anchor: on the in-sample arena's {{mn_nind_ins}} independent {{h2h_unit}}-step trajectories, {{mn_insample_clause}}, and among the held-out readings the rule
reports alongside, {{mn_alongside_clause}}.

**The history length departs furthest from the original.** The original's error falls steeply
from M = 1 to M = 8 and then flattens (`ORIGINAL_SPECS.md` a.5). On the governing reading ours does
not fall at all: {{mn_mvar_better_list}}, histories shorter than the centre's, beat it, and no
shorter history is resolvably worse, though other readings the rule reports put shorter histories
behind it: {{mn_mvar_other_worse}}. The original's direction on N holds: the shortest forecasts
are far worse, which is §5's teacher-forcing result again, and the longest are better, so the
centre's tie with its longest-forecast neighbour becomes a loss.

**Accuracy at equal compute (post hoc; ledger R-78).** A longer training forecast costs more per
iteration, {{n3_cost_M32_N16}}× the centre's for {{n3_lf_label}} and {{n3_cost_M32_N32}}× for {{mn_best_config}}, so at
a given iteration count those also had more computation; the shorter histories that win cost less,
{{n3_cost_M8_N8}}× and {{n3_cost_M2_N8}}×. Training the centre longer controls for this
(`results/mn_compute_matched.json`; differences signed as in the table). At {{n3_k_mid}} iterations
the centre has had {{n3_best_over_mid}}× the computation of {{mn_best_config}} at {{iters_main}}, and
{{mn_best_config}} is still ahead at h = {{v2_diag_h}}, a difference of {{n3_best_D_mid}}
{{n3_best_ci_mid}}, so its advantage is not an artefact of extra computation per iteration. That is
as far as it goes. At {{iters_long}} iterations, {{n3_best_over_long}}× the computation, the
difference is {{n3_best_D_long}} {{n3_best_ci_long}}, not resolved; on the in-sample arena the centre
at {{n3_k_mid}} already draws level with {{mn_best_config}} ({{n3_best_ins_D_mid}} {{n3_best_ins_ci_mid}})
and passes {{n3_lf_label}} ({{n3_lf_ins_D_mid}} {{n3_lf_ins_ci_mid}}); and at {{iters_long}} it passes
both shorter histories, {{n3_sh_long_clause}}. None of this re-opens rule M-74.

**Limits.** One factor is varied at a time, so no interaction between M and N is tested. Our data
budget is {{c2_pct}}% of the reference's (§5.1), and the original states neither the ablation's
budget, its evaluation data nor the horizon behind its error, so the verdict holds at our budget and
no further: a larger one may favour a longer history. All {{tail_n}} runs at {{iters_main}} iterations,
the sweep's, the baselines' and both arms', are still lowering their training loss at the end, with slopes
from {{tail_slope_lo}} to {{tail_slope_hi}} per thousand iterations (`results/training_tail_slopes.json`,
post hoc), so the ranking is at this budget, not at convergence. With {{mn_nind}} independent trajectories, the rule's minimum detectable effect at h = {{v2_diag_h}},
the difference its first Holm step would usually detect, is about {{mn_mde_h368}}% of the centre's
error.

### 5.3 The architecture claim: MLP, RSSM and transformer baselines

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

**Arena as in §5.2: {{h2h_arena}}, {{h2h_ntraj}} non-overlapping {{h2h_unit}}-step trajectories, n_independent = {{mn_nind}}.** Each row is the mean over
{{mn_seeds_word}} seeds at {{iters_main}} iterations (`results/baselines_eval.json`). A difference is
positive when RWM is better, and "result" is after Holm (`results/baselines_verdict.json`). The last
column is timed beside RWM in one sitting (`results/mn_compute_matched.json`); hours per run are in
Appendix B. † marks a diverged row, one where any seed's mean relative-L1 at h = {{v2_diag_h}} exceeds
{{div_factor}}× the hold-last floor's (`results/pooled_nrmse_rescore.json`, post hoc). Run-away
rollouts dominate those {{div_n_word}} rows' means; per seed they are {{div_per_seed}}. No verdict
depends on that magnitude, only on the sign: each such row's four per-trajectory differences from
RWM are all positive, so every bootstrap resample favours RWM whatever their size.

**Result: {{bl_tf_verdict}} with the baselines teacher-forced, and {{bl_ar_verdict}} with them
trained autoregressively.** RWM is ahead of baselines built to our reading of Table S7 and trained
with RWM's settings for {{iters_main}} iterations: all {{bl_n_rows_word}} comparisons favour it, with
intervals that exclude zero. That says less than it seems at h = {{v2_diag_h}}, where every baseline
row, in both regimes, is above the hold-last floor and RWM is below it: no baseline beats predicting
no change. The second verdict compares architectures at one training regime and is not a verdict on
the original's claim, which the first carries. The lead is a long-horizon one, and the rules'
relative-L1 readings at other horizons say where it starts. Teacher-forced, the baselines fall
resolvably behind from {{bl_tf_lead_from}} (the transformer from {{bl_tf_tr_lead_from}}).
Trained autoregressively, the RSSM falls behind from {{bl_ar_rssm_lead_from}}, but the MLP and the transformer only from {{bl_ar_lead_from}}, the method's own horizon, where they trail by
{{bl_ar_mlp_D_h100}} {{bl_ar_mlp_ci_h100}}, about {{bl_ar_mlp_pct_h100}}% of RWM's
{{h2h_armA_l1_h100}}, and {{bl_ar_tr_D_h100}} {{bl_ar_tr_ci_h100}}. Before those horizons a baseline
cannot be told apart from RWM: at h = 1 both rules return {{bl_tf_h1}}, and at h = 8 both return
{{bl_tf_h8}}.

**Our RSSM is not an informative comparison.** Teacher-forced, it is the most accurate model here one
step ahead, {{h2h_bl_rssm_tf_l1_h1}} against RWM's {{h2h_armA_l1_h1}} and the floor's {{x1_floor_h1}},
though not resolvably, and it has collapsed open-loop by h = 32, where its {{x1_tf_mode_h32}} is above
the floor's {{x1_floor_h32}}. The original adds that an RSSM trained autoregressively performs
comparably to RWM; ours does not, {{h2h_bl_rssm_ar_l1_h368}} against RWM's {{bl_rwm_l1_h368}} at
h = {{v2_diag_h}}. A diagnostic committed before its readings existed (rule X1, ledger M-80;
exploratory, it re-opens neither rule) asks why. Its Part A reads the forecast differently, feeding
the prior's expected or sampled latent in place of its most likely one: the error at h = 32 falls to
{{x1_tf_exp_h32}} and {{x1_tf_samp_h32}}, still above the floor, so it returns **{{x1_reading_a}}**
(M-81). Its Part B is descriptive: over the history, the teacher-forced RSSM's one-step error from its
prior is {{x1b_tf_ratio_lo}} to {{x1b_tf_ratio_hi}}× its error from its posterior at the same
recurrent state (the autoregressive one's at most {{x1b_ar_ratio_hi}}×), with {{x1b_kl_lo}} to
{{x1b_kl_hi}} nats of KL divergence between them per step. {{rssm_partc_sentence}} The failure may be
our RSSM rather than the architecture: Table S7's latent is ambiguous, and we read it in DreamerV2's
naming, without its layer-normalised recurrent cell (`BASELINE_SPECS.md`, the RSSM rows). Until X1
says otherwise, the architecture claim rests on the MLP and the transformer.

**Limits.** One robot on flat ground; the original has several environments. The baselines
are our reading of a table that fixes their shapes and nothing else. Their loss, optimiser and
budget are RWM's, not tuned for them. Their sizes are Table S7's, not matched to RWM's;
parameter-matched variants were specified but not run. With {{mn_nind}} independent trajectories, the minimum detectable effect at h = {{v2_diag_h}} is
about {{bl_mde_h368}}% of RWM's error, well below every difference here.

---

## 6. Neither of the checkpoint's uncertainty outputs is usable as an interval

*How this section runs.* §6.1–§6.2 settle which quantity the method uses and measure it; §6.3–§6.5 examine why each output fails; §6.6–§6.7 separate the magnitude of the failure from its ordering, and test the ordering against free baselines; §6.8–§6.11 ask what would fix it.

### 6.1 Which quantity the method actually uses

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
is never consumed. We report both quantities below. Our own arms are ensemble size 1, where the
epistemic term is identically zero by construction, so the epistemic measurement is possible only
on the released checkpoint.

**What the follow-up does and does not claim.** It does not claim its uncertainty is a calibrated
interval. Its §5.1 claims the epistemic term "closely follows the trend of the prediction error"
and that this "justifies its role as a trust metric", and of the aleatoric term it observes only
that it "remains low, reflecting small stochasticity in the environment". Our measurement
**supports the first claim**: the epistemic ordering is real and strong. What follows is therefore
not a refutation of a calibration claim nobody made, but three things the papers do not address:
that the aleatoric head is discarded before use, that neither quantity is usable as a scale, and
that the low aleatoric value has a different cause than the one offered.

### 6.2 The measurement

For each model we compute the mean predicted σ, the mean absolute realised error, and the fraction
of realised errors falling inside ±1σ. A calibrated Gaussian puts {{v3_cov_nominal1}}% inside ±1σ (§3.1).

| model | mean \|error\| / mean σ, whole {{v2_diag_h}}-step rollout | coverage at ±1σ, h=1 | coverage at ±1σ, h={{v2_deploy_h}} |
|---|---|---|---|
| faithful Arm A (sampled MSE) | {{cal_faithA_ratio}}× [{{cal_faithA_ratio_ci}}] | {{cal_faithA_cov1}}% [{{cal_faithA_cov1_ci}}] | {{cal_faithA_cov100}}% [{{cal_faithA_cov100_ci}}] |
| corrected Arm A (`gaussian_nll`) | {{cal_nll_ratio}}× [{{cal_nll_ratio_ci}}] | {{cal_nll_cov1}}% [{{cal_nll_cov1_ci}}] | {{cal_nll_cov100}}% [{{cal_nll_cov100_ci}}] |
| teacher-forced Arm B | {{cal_armB_ratio}}× [{{cal_armB_ratio_ci}}] | {{cal_armB_cov1}}% [{{cal_armB_cov1_ci}}] | {{cal_armB_cov100}}% [{{cal_armB_cov100_ci}}] |
| released checkpoint | {{cal_rel_ratio}}× [{{cal_rel_ratio_ci}}] | {{cal_rel_cov1}}% [{{cal_rel_cov1_ci}}] | {{cal_rel_cov100}}% [{{cal_rel_cov100_ci}}] |

*Our arms are at {{iters_main}} training iterations; the released checkpoint is as released. Every cell carries a 95% interval from a cluster bootstrap over whole trajectories, n_independent = {{b2_nind}}, quantised as the n = {{b2_nind}} caveat of §3 describes; where three seeds contribute, seeds are pooled inside each draw rather than resampled, because seeds are not trajectories (§8).*

**All four rows are the held-out arena** — the two episodes withheld from our own arms, n_independent = {{b2_nind}} 400-step trajectories — because that is the only arena on which our arms can be scored fairly. On the aleatoric head every model is overconfident by between one and four orders of magnitude (Figure 3); that is the quantity §6.1 shows the method discards. The released checkpoint's {{cal_rel_ratio}}× is its whole {{v2_diag_h}}-step rollout on those same {{b2_nind}} trajectories, for comparability with the arms; its best-sampled figure is the {{d1n_alea_ratio_h100}}× below, cumulative to h = {{v2_deploy_h}} at n_independent = {{d1n_nind}}. **Both are correct, on a different arena and a different horizon**, and neither is out-of-sample for that checkpoint (the in-sample caveat of §3).

**The quantity the method does use is also uncalibrated.** On the released {{b2_members}}-member checkpoint over all {{d1n_eps}} episodes, n_independent = **{{d1n_nind}}** non-overlapping 400-step trajectories. The checkpoint trained on all ten, so restricting it to the held-out pair would buy no independence and cost four fifths of the sample; that version, at n_independent = {{b2_nind}}, is in the supplementary material (`results/task_b2_epistemic.json`). Its epistemic column agrees in direction with this one at all {{agree_epi}} of {{agree_nh}} horizons; its aleatoric column agrees at {{agree_alea}} of {{agree_nh}}, flipping sign at {{agree_alea_dis}}, where both readings sit close to chance and the aleatoric σ is in any case {{d1n_alea_ratio_h1}}× (h = 1) to {{d1n_alea_ratio_h368}}× (h = {{v2_diag_h}}) too small for its ordering to be the interesting quantity.

| h | aleatoric err/σ [95% CI] | aleatoric ±1σ | epistemic err/σ [95% CI] | epistemic ±1σ [95% CI] | epistemic ±2σ | dims r>0 | permutation P |
|---|---|---|---|---|---|---|---|
| 1 | {{d1n_alea_ratio_h1}}× [{{d1n_alea_ratio_ci_h1}}] | {{d1n_alea_cov1_h1}}% | **{{d1n_epi_ratio_h1}}×** [{{d1n_epi_ratio_ci_h1}}] | {{d1n_epi_cov1_h1}}% [{{d1n_epi_cov1_ci_h1}}] | {{d1n_epi_cov2_h1}}% | {{d1n_epi_npos_h1}}/{{d1n_epi_ndim_h1}} | {{perm_all_epi_p_h1}} |
| 8 | {{d1n_alea_ratio_h8}}× [{{d1n_alea_ratio_ci_h8}}] | {{d1n_alea_cov1_h8}}% | {{d1n_epi_ratio_h8}}× [{{d1n_epi_ratio_ci_h8}}] | {{d1n_epi_cov1_h8}}% [{{d1n_epi_cov1_ci_h8}}] | {{d1n_epi_cov2_h8}}% | {{d1n_epi_npos_h8}}/{{d1n_epi_ndim_h8}} | {{perm_all_epi_p_h8}} |
| 32 | {{d1n_alea_ratio_h32}}× [{{d1n_alea_ratio_ci_h32}}] | {{d1n_alea_cov1_h32}}% | {{d1n_epi_ratio_h32}}× [{{d1n_epi_ratio_ci_h32}}] | {{d1n_epi_cov1_h32}}% [{{d1n_epi_cov1_ci_h32}}] | {{d1n_epi_cov2_h32}}% | {{d1n_epi_npos_h32}}/{{d1n_epi_ndim_h32}} | {{perm_all_epi_p_h32}} |
| **{{v2_deploy_h}}** | {{d1n_alea_ratio_h100}}× [{{d1n_alea_ratio_ci_h100}}] | {{d1n_alea_cov1_h100}}% | **{{d1n_epi_ratio_h100}}×** [{{d1n_epi_ratio_ci_h100}}] | {{d1n_epi_cov1_h100}}% [{{d1n_epi_cov1_ci_h100}}] | {{d1n_epi_cov2_h100}}% | {{d1n_epi_npos_h100}}/{{d1n_epi_ndim_h100}} | {{perm_all_epi_p_h100}} |
| 128 | {{d1n_alea_ratio_h128}}× [{{d1n_alea_ratio_ci_h128}}] | {{d1n_alea_cov1_h128}}% | {{d1n_epi_ratio_h128}}× [{{d1n_epi_ratio_ci_h128}}] | {{d1n_epi_cov1_h128}}% [{{d1n_epi_cov1_ci_h128}}] | {{d1n_epi_cov2_h128}}% | {{d1n_epi_npos_h128}}/{{d1n_epi_ndim_h128}} | {{perm_all_epi_p_h128}} |
| 368 | {{d1n_alea_ratio_h368}}× [{{d1n_alea_ratio_ci_h368}}] | {{d1n_alea_cov1_h368}}% | {{d1n_epi_ratio_h368}}× [{{d1n_epi_ratio_ci_h368}}] | {{d1n_epi_cov1_h368}}% [{{d1n_epi_cov1_ci_h368}}] | {{d1n_epi_cov2_h368}}% | {{d1n_epi_npos_h368}}/{{d1n_epi_ndim_h368}} | {{perm_all_epi_p_h368}} |

**Read the h = 1 row first.** At one step the disagreement the method penalises rewards with is
already **{{d1n_epi_ratio_h1}}× [{{d1n_epi_ratio_ci_h1}}]** smaller than realised error, with ±1σ
coverage of {{d1n_epi_cov1_h1}}% [{{d1n_epi_cov1_ci_h1}}] against a calibrated
{{v3_cov_nominal1}}%. The discarded per-member σ is {{d1n_alea_ratio_h1}}× out at h = 1 as well.
Everything further down the table is deterioration from a starting point that is already broken.

**Why that row, and not the deep ones.** The obvious objection is that a per-step σ is a
*conditional* quantity: it says how uncertain the next state is given this input, and in an
open-loop rollout the input is the model's own previous output, wrong by an amount σ never claimed
to describe. Comparing it with *accumulated* rollout error would then make the {{v2_diag_h}}-step
figure an artifact of that mismatch. (§6.9 answers a different objection, that a model trained on
{{win_fore}} steps cannot be expected to speak about {{v2_diag_h}}.) **h = 1 answers it at no extra
cost.** At one step there is no accumulation: the input *is* the true state, and σ is asked exactly
the question it was trained to answer. At h = 1 it is out by {{d1n_epi_ratio_h1}}×, and
{{d1n_epi_cov1_h1}}% of outcomes fall inside an interval that should hold {{v3_cov_nominal1}}%.
Whatever compounding does at depth, it did not do that.

**And that row is measured on data the checkpoint trained on**: all ten episodes, {{insample_n_overlap}} of {{insample_n_arena}} of them (`results/insample_framing.json`). In-sample measurement biases *toward* better calibration, so the {{d1n_epi_ratio_h1}}× at h = 1 is if anything flattering: an upper bound on how well this checkpoint is calibrated. So the horizon curve is not the claim; it is the shape of the deterioration, and the claim is the h = 1 row. We keep h = {{v2_deploy_h}} because it is where the method actually deploys, and h = {{v2_diag_h}} because it is the upstream's own diagnostic length.

At h = {{v2_deploy_h}}, the method's own imagination rollout length, epistemic is
{{d1n_epi_over_alea_h100}}× better than aleatoric and still wrong by
**{{d1n_epi_ratio_h100}}× [{{d1n_epi_ratio_ci_h100}}]**, with ±1σ coverage of
{{d1n_epi_cov1_h100}}% [{{d1n_epi_cov1_ci_h100}}] where a calibrated Gaussian gives
{{v3_cov_nominal1}}%. At one step it is **{{d1n_epi_ratio_h1}}×** out and
{{d1n_epi_over_alea_h1}}× better than aleatoric; at h = {{v2_diag_h}} the two-term ratio is
{{d1n_epi_over_alea_h368}}×. **The gap between the two uncertainty terms is itself
horizon-dependent, which is why each figure above names its horizon.** At the open-loop diagnostic horizon of h = {{v2_diag_h}} it is {{d1n_epi_ratio_h368}}× [{{d1n_epi_ratio_ci_h368}}] with {{d1n_epi_cov1_h368}}% coverage, barely different from h = {{v2_deploy_h}}. **Total** uncertainty, `sqrt(aleatoric² + epistemic²)`, equals the epistemic value to four significant figures at every horizon, because the aleatoric term is too small to move it.

**A constant scale error would not matter, and this one is not constant.** The penalty enters as `r̃ = r − λu`, so a `u` uniformly `c` times too small is arithmetically identical to running with `λ/c`, and λ is tuned. Rescaling σ by the single constant that best calibrates it, fitted and scored on the same data and so an upper bound on what *any* constant achieves, needs {{m65_c_h1}} at h = 1 and {{m65_c_h368}} at h = {{v2_diag_h}}, a factor of {{m65_c_growth}} across the rollout (rule M-65, Appendix E). No single λ is both of those. The mechanism is §6.9's: σ grows far more slowly than error, which grows by an order of magnitude, so the ratio runs {{d1n_epi_ratio_h1}}× at h = 1, {{d1n_epi_ratio_h100}}× at h = {{v2_deploy_h}} and {{d1n_epi_ratio_h368}}× at h = {{v2_diag_h}}. The penalty is applied at every step of a {{v2_deploy_h}}-step imagination rollout, so its *profile across the rollout* is wrong in a way no rescaling can correct: deep-rollout states are under-penalised relative to their realised risk. This bounds what the quantity reports across depth, not what the distortion costs a trained policy (the policy caveat of §11).

**The larger sample changes one thing materially.** At n_independent = {{b2_nind}} the epistemic ordering looked like chance at short horizon, {{b2_epi_npos_h1}} of {{b2_epi_ndim_h1}} dimensions at h=1. At n_independent = {{d1n_nind}} it is {{d1n_epi_npos_h1}} of {{d1n_epi_ndim_h1}} at h=1, with mean r = {{d1n_epi_r_h1}}, the *strongest* mean correlation of any horizon, and the in-sample permutation test agrees (§6.6). The short-horizon "chance" result was an artifact of four trajectories, not a property of the model.

**Two pre-registered checks on how these numbers are read.** The first (rule M-62, Appendix E) asks whether any verdict depends on resampling 400-step trajectories rather than whole episodes, which two trajectories share. It returns **{{m62_verdict}}**: in the one arena with power at that level, all ten episodes (n = {{m62_n_traj}} falling to {{m62_n_ep}}), the pooled correlation's interval widens by {{m62_width_pct}}% and the double-demeaned one's width changes by a factor of {{m62_rdd_width_ratio}}, and neither crosses zero. The other {{m62_n_uninformative}} cells it names are out-of-sample, where an episode bootstrap has n = {{m62_n_ep_oos}} and three distinct resamples; the rule said so in advance, and they are reported as uninformative rather than as intervals.

**The second (rule M-63, Appendix E) asks whether the one-step failure is a few bad channels or all of them**, since a pooled coverage is the unweighted mean of 45 per-dimension ones. It returns **{{m63_verdict}}**: the interquartile range across dimensions is {{m63_iqr}} points against a {{m63_iqr_thr}}-point threshold committed in advance, and the five worst dimensions carry well under half of the shortfall. **No channel is exempt**, which is what §6.3's mechanism predicts: an objective whose optimum is σ = 0 has no reason to spare any dimension. The reading is coarse by construction: at h = 1 on {{d1n_nind}} trajectories a per-dimension coverage moves in {{m63_quant}}-point steps, a limit the rule fixed before the run.

**The released checkpoint is no longer the only ensemble measured.** Three Arm A arms at ensemble size 5 (§6.7, {{e5_seeds}} seeds, out-of-sample, n_independent = {{e5_nind}} 400-step trajectories, {{iters_main}} training iterations) give, averaged over seeds:

| h | epistemic err/σ [95% CI] | ±1σ [95% CI] | ±2σ | dims r>0 |
|---|---|---|---|---|
| 1 | {{e5_ratio_h1}}× [{{e5_ratio_ci_h1}}] | {{e5_cov1_h1}}% [{{e5_cov1_ci_h1}}] | {{e5_cov2_h1}}% | {{e5_npos_h1}}/45 |
| 8 | {{e5_ratio_h8}}× [{{e5_ratio_ci_h8}}] | {{e5_cov1_h8}}% [{{e5_cov1_ci_h8}}] | {{e5_cov2_h8}}% | {{e5_npos_h8}}/45 |
| 32 | {{e5_ratio_h32}}× [{{e5_ratio_ci_h32}}] | {{e5_cov1_h32}}% [{{e5_cov1_ci_h32}}] | {{e5_cov2_h32}}% | {{e5_npos_h32}}/45 |
| 100 | **{{e5_ratio_h100}}×** [{{e5_ratio_ci_h100}}] | {{e5_cov1_h100}}% [{{e5_cov1_ci_h100}}] | {{e5_cov2_h100}}% | {{e5_npos_h100}}/45 |
| 128 | {{e5_ratio_h128}}× [{{e5_ratio_ci_h128}}] | {{e5_cov1_h128}}% [{{e5_cov1_ci_h128}}] | {{e5_cov2_h128}}% | {{e5_npos_h128}}/45 |
| 368 | **{{e5_ratio_h368}}×** [{{e5_ratio_ci_h368}}] | {{e5_cov1_h368}}% [{{e5_cov1_ci_h368}}] | {{e5_cov2_h368}}% | {{e5_npos_h368}}/45 |

Our arms are **better calibrated than the released checkpoint and fail the same way**: {{e5_ratio_h100}}× overconfident at h = {{v2_deploy_h}} against its {{d1n_epi_ratio_h100}}×, with {{e5_cov1_h100}}% coverage where a calibrated Gaussian gives {{v3_cov_nominal1}}%. §6.4 establishes that the two are the same architecture in the respect that matters here, so this is a comparison of like with like. Being closer to calibrated is not being calibrated.

The last column of the released checkpoint's table gives permutation P-values over whole trajectories, not binomial ones, on the same {{perm_all_nind}} trajectories as the counts beside them; §6.6 explains why a binomial null is inadmissible here. h = {{v2_deploy_h}} is tested too, because it carries the abstract's headline figure. These are {{perm_n_tests_col_word}} tests on one family and none survives Holm–Bonferroni across the arena's {{perm_all_holm_n}} cells: the smallest is {{perm_all_holm_min_cell}} at {{perm_all_holm_min_p}} against a threshold of {{perm_all_holm_thr}}. Read the column as a consistency check on direction, not as {{perm_n_tests_col_word}} independent findings.

The scalar penalty as actually applied, `means.std(0).sum(-1)` at `envs/base.py:166`, correlates **{{d4_r}}** with total absolute error over the rollout, 95% CI {{d4_ci}} from a bootstrap over whole trajectories, n_independent = {{d4_nind}} ({{d4_npoints}} pooled trajectory-step points). The interval resamples whole trajectories, not trajectory-step pairs, which would narrow it by about the square root of the rollout length.

### 6.3 Why the aleatoric head collapses: the optimum is σ = 0

This subsection explains the aleatoric column and only that column; ensemble disagreement is not
shaped by the mechanism below, and why *it* is miscalibrated is not established here. It also
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

**The derivation above covers two terms, and the objective has {{e4_n_terms}}.** Its completeness
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
`"single"` on both paths, and `kl` and `extension` are zero because their dimensions are. Of the
{{e4_n_terms}}, exactly {{e4_n_touch}} reach σ: {{e4_touching}}. The remaining {{e4_n_inert}}
produce a gradient of exactly zero, not merely a term the code suggests is irrelevant
(`results/e4_sigma_gradients.json`).

**The derivation says the collapse happens on any dataset, and that is testable.** It matters
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
over its own {{e5s_seeds}} and is not re-opened by more seeds (§8); what twenty establish is that
the hedge below was necessary. **The recovering arm is seed-variable, and the rule said so before
the runs**: its slopes span {{e5s_nll_slope_range}}, a factor of
{{e5s_nll_slope_spread_factor}}, and two of {{e5s_seeds}} seeds recover a σ spread of only
{{e5s_nll_spread_lo}}× against the truth's {{e5s_span}}×. So what this experiment establishes is
the **contrast**, that one objective tracks the noise at all and the other does not, and not the
magnitude of the recovery, which this training budget does not pin down. **{{e5s_verdict}}**, which is the verdict the rule names for that pattern.

*The statistic is the slope, not the correlation, because a correlation is scale-free: a σ̂ that is
essentially constant still returns a large one off its own numerical noise. Under a permutation
null, the same data with the input-to-noise pairing destroyed, a head whose σ spanned
{{e5s_null_spread}}× returned correlations as large as ±{{e5s_null_r_max}}, while its slope was
{{e5s_null_slope_p95}}. The detection threshold is set at the slope corresponding to a
{{e5s_span_floor}}× spread rather than at that noise floor, and the measured false-positive rate at
zero signal is {{e5s_fp_rate}}%.*

**What this does that the derivation alone could not.** It removes the competing explanation
rather than arguing against it: the stochasticity here is large, known and input-dependent, and the
collapse happens anyway. The design's limit, stated in the rule, holds: the dilution ladder detects
the signal at full strength and at no dilution below it, so this establishes that σ does not track
the noise **at all**, not the magnitude of how badly.

We predicted the collapse from this algebra before training, then observed it. Three run counts
appear below and they are not the same set. This project trained {{run_total}} runs for §5–§7, besides the {{rt_pre_runs}} of §5.2 and §5.3
(Appendix B), of
which {{n_runs}} are at the released `rnn_hidden_size` of {{released_width}} and form the collapse
family; the remaining {{n_runs_offwidth}} are the capacity-matched arm of rule M-49 (Appendix E) at
width {{m49_width}}, a different architecture, excluded from every rate quoted here (Appendix B).
Across all {{n_runs}} runs of that family the collapse is linear in iteration count and its rate is
nearly identical (Figure 4a). Rates are fitted on {{e2_fitted_runs}} of those {{n_runs}}: the
{{e2_excluded_10k}} 10,000-iteration runs continue seeds already counted at 2,500 and would
double-weight them. Figure 4(a) shows all {{n_runs}} runs of the collapse family and Figure 4(b)
only the {{e2_fitted_runs}} the rate is fitted on, so the scatter and the quoted statistic describe
the same set. The {{run_total}} runs, with the width column separating the collapse family from the
capacity-matched arm:

| arm | iterations | ensemble | objective | dataset | width | seeds | seed ids |
|---|---|---|---|---|---|---|---|
{{run_table}}

**Two different things are being explained here, and §6.6 separates them.** *Magnitude collapse
is objective-driven.* It occurs in all {{e2_mse_runs}} sampled-MSE runs at a rate of
{{e2_mse_rate}} per iteration with a standard deviation of {{e2_mse_sd}}, **including the
teacher-forced arm**, which shares the objective, and reverses to {{e2_nll_rate}} in the
{{e2_nll_runs}} runs that change it. *Input-independence is not.* It varies by a factor of
{{cal_armB_over_faithA_cov}} between two arms trained under the same objective, so the objective
cannot be what produces it.

Under the corrected objective the sign flips (Figure 4b), the strongest evidence that the mechanism
is the objective and not the optimiser, the data or the architecture.

### 6.4 Why the epistemic term may be miscalibrated: the members are not independent models

§6.3 explains the aleatoric column and leaves the epistemic one open. This subsection supplies a
candidate, structurally symmetric to §6.3's, from source and from the checkpoint's own tensors;
nothing here is trained and nothing is inferred from a measurement. The effect is known (§2). What
is ours is finding it in a released robotics checkpoint, with the sharing quantified at
{{v1_shared_pct}}% of each member and the cost measured at {{m44_ratio_gain}}× on the
overconfidence factor (§6.10).

**The released five-member ensemble is not five models.** `system_dynamics.py:34` builds **one**
`state_base`. `system_dynamics.py:35-41` replicates the *heads* `ensemble_size` times, and only
the heads. In the forward pass `system_dynamics.py:87` evaluates the trunk **once** and `:90`
hands the identical feature vector to every head; `system_dynamics.py:126` then computes the
epistemic term as the standard deviation across those heads.

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
ensemble-5 arms build one trunk the same way (`src/rwm_model.py:164-167`), evaluate it once
(`:182`), hand the same vector to every head (`:185`) and compute the same spread (`:200`). Their
tensor names and parameter counts match the released checkpoint exactly —
{{v1_shared_params}} shared, {{v1_private_params}} per head, {{v1_total_params}} in total, on all
{{v1_n_arms_checked}} arms checked (`results/v1_ensemble_topology.json`). So §6.2's "our arms fail the same way at {{e5_ratio_h100}}× at h = {{v2_deploy_h}}" compares two instances of one architecture, not two architectures.

**What this is and is not.** It is a *candidate* mechanism, established structurally. It does not
show that trunk-sharing is *the* explanation for §6.2's miscalibration; architecture could be a
minor contributor to a failure dominated by something else. That needs an ensemble which shares
nothing, pre-registered as rule M-44 (Appendix E) and reported in §6.10. The topology is a fact
about the released artifact; the mechanism is a hypothesis about that fact.

### 6.5 The correction fails differently rather than succeeding

The reference contains an unused `gaussian_nll` branch. Running it reverses the collapse and
improves the magnitude from {{cal_faithA_ratio}}× to {{cal_nll_ratio}}× overconfident. It does not produce a usable estimate, and it destroys something the faithful arm had: the σ-versus-error ordering falls from {{cal_faithA_npos}}/{{cal_faithA_ndim}} dimensions positively correlated to {{cal_nll_npos}}/{{cal_nll_ndim}}, which is chance. Under the trajectory permutation test of §6.6, at h = {{v2_diag_h}}, those counts give P = {{perm_oos_faithA_p_h368}} and {{perm_oos_nll_p_h368}} out of sample, {{perm_ins_faithA_p_h368}} and {{perm_ins_nll_p_h368}} in sample. The faithful arm's ordering is the one result in this family that points the same way in both arenas; it is also the weakest effect of the three, and it does not survive multiplicity correction either.

### 6.6 The failure is one of magnitude; the ordering is weaker than it looks

Adding the teacher-forced arm, trained for §5, sharpens the finding (our arms at {{iters_main}} training iterations; the released checkpoint as released):

| model | σ variation across inputs (CoV) | dims with r(σ, error) > 0 at h={{v2_diag_h}}, out-of-sample | perm P at h={{v2_diag_h}}, out-of-sample | perm P at h={{v2_diag_h}}, in-sample |
|---|---|---|---|---|
| faithful Arm A | {{cal_faithA_cov}} | {{cal_faithA_npos}}/{{cal_faithA_ndim}} | {{perm_oos_faithA_p_h368}} | {{perm_ins_faithA_p_h368}} |
| corrected Arm A | {{cal_nll_cov}} | {{cal_nll_npos}}/{{cal_nll_ndim}} | {{perm_oos_nll_p_h368}} | {{perm_ins_nll_p_h368}} |
| **teacher-forced Arm B** | **{{cal_armB_cov}}** | **{{cal_armB_npos}}/{{cal_armB_ndim}}** | **{{perm_oos_armB_p_h368}}** | **{{perm_ins_armB_p_h368}}** |
| released checkpoint | {{cal_rel_cov}} | {{cal_rel_npos}}/{{cal_rel_ndim}} | {{perm_oos_relale_p_h368}} | {{perm_ins_relale_p_h368}} |

**The CoV column is the aleatoric σ in every row**, the only σ the ensemble-size-1 arms have. Our ensemble-5 arms (§6.7) have both: their aleatoric CoV is comparable to the other arms', and their *epistemic* term is far more input-dependent than any aleatoric head here, at {{e5_cov_lo}}–{{e5_cov_hi}} against the released checkpoint's {{cal_rel_cov}}. **The count column is the out-of-sample arena** (n_independent = {{relale_oos_nind}}), so that all four models are compared on trajectories none of our arms trained on. For the released checkpoint's aleatoric head it is not the most informative arena: at h = {{v2_diag_h}} and n_independent = {{relale_all_nind}} over all ten episodes that head is {{relale_all_pos_h368}}/{{perm_all_relale_ndim_h368}}, negatively correlated with error on *every* dimension, against {{relale_oos_pos_h368}}/{{perm_all_relale_ndim_h368}} here; §12 quotes the larger arena.

Arm B's σ is {{cal_armB_over_faithA_cov}}× more input-dependent than the faithful arm's, and it has the largest mean correlation of the four (r = {{cal_armB_r}}). It is still {{cal_armB_ratio}}× overconfident.

**The P column is a permutation P, not a binomial one**, and the binomial P-values an earlier draft attached to these counts are withdrawn (`S-15`). A binomial null treats the 45 state dimensions as independent trials, and they are not: position, velocity and torque for the same joint are physically coupled, and base linear and angular velocity are coupled through the gait. More importantly, error grows with rollout depth in every trajectory, so *any* σ that also grows with depth correlates with *any* trajectory's error, including one it was never paired with.

We therefore permute whole trajectories. The null pairs each trajectory's σ with a different trajectory's realised error, which keeps both marginal distributions and the entire cross-dimension dependence structure and destroys only the association under test. The correction is large, and largest exactly where we leaned hardest. The worst-affected cell is {{perm_worst_model}} at h={{perm_worst_h}}, in the {{perm_worst_arena}} arena. At h = {{v2_diag_h}} it moves from {{perm_ins_armB_binom_h368}} to {{perm_ins_armB_p_h368}}, a factor of about {{perm_worst_factor}}, because under a null that keeps the dependence a random re-pairing already yields {{perm_worst_null}} of {{perm_ins_armB_ndim_h368}} dimensions positive on average, so observing {{perm_ins_armB_npos_h368}} of {{perm_ins_armB_ndim_h368}} is close to unremarkable. A fair coin centres the count at {{perm_faircoin}} of {{perm_ins_armB_ndim_h368}}; the dependence-preserving null centres it between {{perm_null_lo}} and {{perm_null_hi}} depending on model, horizon and arena.

So σ *collapsing in magnitude* is objective-driven, and σ *becoming input-independent* is not.
The teacher-forced arm collapses in magnitude exactly like the autoregressive ones — same
objective, same rate — while retaining {{cal_armB_over_faithA_cov}}× more variation across
inputs. Input-independence is a property of the autoregressive arms and the released checkpoint,
and input-dependence and correct ranking are both achievable without the interval becoming
meaningful. One candidate mechanism, stated as an untested hypothesis: autoregressive feedback
narrows the input distribution toward the model's own manifold, leaving a heteroscedastic head less
variation to key on.

**The same pattern holds for the quantity the method uses, and this is where the correction bites hardest.** At h=128 and h=368 the epistemic term correlates positively with realised error on **{{b2_epi_npos_h368}} of {{b2_epi_ndim_h368}}** dimensions, matching the best aleatoric head here on the sign count, while being {{b2_epi_ratio_h368}}× overconfident at h = {{v2_diag_h}}. **Figures in this paragraph are the held-out arena (n_independent = {{b2_nind}}) unless labelled otherwise**, so the epistemic term and the four aleatoric heads are compared on identical trajectories; §6.2 quotes {{d1n_epi_ratio_h368}}× for the same ratio at h = {{v2_diag_h}} and n_independent = {{d1n_nind}}, and the abstract and §12 use {{d1n_epi_ratio_h100}}× at h = {{v2_deploy_h}} on those {{d1n_nind}} trajectories. Nor does it beat Arm B's head on strength: its mean correlation at h=368 is {{b2_epi_r_h368}} against {{cal_armB_r}}. The two rank comparably, and neither is close to an interval. Under the permutation null that count gives P = {{perm_oos_epi_p_h368}} out of sample and {{perm_ins_epi_p_h368}} in sample, against {{perm_oos_epi_binom_h368}} from the independent-trials test. It still fails the horizon test the same way: σ grows {{b2_epi_sigma_growth}}× from h=1 to h=368 while error grows {{b2_epi_err_growth}}×.

**The larger arenas agree with each other against the smallest.** At n_independent = {{perm_oos_nind}} 400-step trajectories out of sample, the epistemic ordering looks strongest at long horizon ({{perm_oos_epi_p_h128}} at h=128, {{perm_oos_epi_p_h368}} at h=368) and unremarkable at short ({{perm_oos_epi_p_h1}} at h=1). Both larger arenas invert that. In sample (n_independent = {{perm_ins_nind}}): {{perm_ins_epi_p_h1}} at h=1, {{perm_ins_epi_p_h8}} at h=8, against {{perm_ins_epi_p_h128}} at h=128. Over all ten episodes (n_independent = {{perm_all_nind}}): {{perm_all_epi_p_h1}}, {{perm_all_epi_p_h8}} and {{perm_all_epi_p_h128}}, with h = {{v2_deploy_h}} at {{perm_all_epi_p_h100}}, between h=32's {{perm_all_epi_p_h32}} and h=128's {{perm_all_epi_p_h128}}. Two larger arenas at four and five times the sample say the effect is strongest at *short*
horizon, though they are not independent: all {{perm_ins_nind}} in-sample trajectories are among
the {{perm_all_nind}}.

The null means explain why, and the explanation is the one that motivates §6.7. At long horizon the shared forecast-depth trend lifts the null to {{perm_all_epi_null_h128}} of 45 at h = 128, so a count of 45 is close to what chance alone delivers; at h = 1 the null sits near {{perm_all_epi_null_h1}} and the same count is genuinely surprising. The out-of-sample arena is not wrong so much as blind: at {{perm_oos_nind}} trajectories its smallest attainable P-value is {{perm_oos_floor}}, so it cannot tell a strong effect from a marginal one at any horizon. **That blindness belongs to the 400-step unit, not to the arena**: a {{m64_h1_unit}}-row unit gives {{m64_oos_n_h1}} independent units on the same two episodes, and {{m64_oos_n_h100}} at h = {{v2_deploy_h}} (rule M-64, Appendix E). We did not recompute this permutation family at the shorter unit, so what the short units change is the scope of the design claim, not any verdict: the arena is underpowered at h = {{v2_diag_h}}, which needs the full {{long_unit_rows}} rows, and is no longer demonstrably so at h = 128 and below. Running it there is one pass over stored rollouts, and we did not do it. The small arena's numbers are reported because it is the only arena out-of-sample for our own arms, not because it is the better measurement.

**Nothing here survives multiplicity correction, in any of the three arenas.** Holm–Bonferroni over each arena's {{perm_oos_holm_n}} model × horizon cells at α = 0.05 rejects {{perm_oos_holm_rej}} out of sample, {{perm_ins_holm_rej}} in sample and {{perm_all_holm_rej}} over all ten episodes. Out of sample that is a property of the design: with {{perm_oos_nind}} independent trajectories the smallest attainable P-value is {{perm_oos_floor}}, which already exceeds the smallest Holm threshold {{perm_oos_holm_thr}}, so no effect of any size could have been rejected there. In sample the miss is real: the smallest P in the family is {{perm_ins_holm_min_cell}} at {{perm_ins_holm_min_p}} against a threshold of {{perm_ins_holm_thr}}.

So this section's claim is: **the magnitude failure is established and large; the ordering is directionally consistent across every model and horizon we measured, and is not established at conventional significance once the dependence between dimensions is respected.**

**The failure is specifically magnitude calibration, in both components.**

### 6.7 Ensemble disagreement beats the trivial baseline

The follow-up justifies ensemble disagreement as a trust metric on the grounds that it "closely follows the trend of the prediction error". §6.6 shows the per-dimension version of that claim is weaker than it looks; this section finds that the *scalar* the method applies tracks error well, which coexists with §6.6 without contradiction, and asks the question that matters more to a practitioner: **does disagreement beat something free?** The quantity is a usable ranking signal and is still not an interval.

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

**The last column is the test of whether disagreement beats the counter.** Comparing the two marginal intervals for overlap is the wrong comparison: both correlations are measured on the *same* trajectories, so their sampling errors move together and the marginal intervals are needlessly conservative. The paired difference, resampling whole trajectories and recomputing *both* correlations inside each draw, is the appropriate and more powerful test. It excludes zero at **{{d2p_n_separating}} of {{d2p_n_horizons}}** horizons. The distinction matters at {{d2p_n_overlap}} of them: at {{d2p_overlap_h}} the marginal intervals *do* overlap. {{d2b_idx_strongest_h}} is where the counter is strongest ({{d2b_idx_h128}}) and the margin narrowest: the paired difference there is {{d2p_diff_h128}} {{d2p_ci_h128}}, which excludes zero only just: {{d2p_narrowest_lo}} is the smallest lower bound in the table, at the 400-step unit. At the shorter unit of rule M-64 (Appendix E), {{m64_h128_n}} non-overlapping units over the same ten episodes give {{m64_h128_ci}} for the same paired difference, so that horizon carries more weight than it did. At h = {{v2_deploy_h}} the paired difference is {{d2p_diff_h100}} {{d2p_ci_h100}}, which also excludes zero.

**The third column asks whether disagreement merely re-encodes the clock.** Partialling the step index out of both variables *lowers* disagreement's correlation by {{d2b_shrink_all_abs}}, from {{d2b_epi_all}} to {{d2b_par_all}}. Almost none of what disagreement knows is explained by how deep into the rollout you are: it carries real information about *this* rollout.

**What survives removing each confound.** A linear partial is not much of a control: error
does not grow linearly with depth, and a control that under-fits the index leaves index-driven
variance in the residual and flatters disagreement. The first five rows after the pooled baseline
below are **depth controls**, each partialling out a different model of how far into the rollout
you are; the last four **decompose** the pooled figure into its between-trajectory and
within-trajectory parts, and the last of those was pre-registered before it was computed (rule
M-45, Appendix E). **One row is not comparable to the others**: the rank partial is a correlation
of ranks rather than of values, so its being larger than the pooled figure says nothing about how
much depth explains.

| what is removed | correlation | 95% CI | what survives it |
|---|---|---|---|
| nothing (pooled) | {{a2_r_pooled}} | {{a2_r_pooled_ci}} | — |
| the step index, linearly | {{d2b_par_all}} | — | depth explains {{d2b_shrink_all_abs}} of it, from {{d2b_epi_all}} |
| log(1 + index) | {{d2r_log}} | {{d2r_log_ci}} | a non-linear model of depth |
| a cubic in the index | {{d2r_cub}} | {{d2r_cub_ci}} | any polynomial trend in depth |
| any monotone function of depth (rank partial) | {{d2r_spr}} | {{d2r_spr_ci}} | depth in any monotone form |
| depth exactly, within each forecast step | **{{d2r_win}}** | {{d2r_win_ci}} | positive at {{d2r_win_pos}} of {{d2r_win_n}} steps, median {{d2r_win_med}}[^stepcount] |
| forecast-step means only | {{a2_step_only}} | — | the within-step control, pooled |
| trajectory means only | {{a2_r_within}} | {{a2_r_within_ci}} | — |
| everything within a trajectory — the {{a2_nind}} trajectory means alone | {{a2_r_between}} | {{a2_r_between_ci}} | do harder rollouts disagree more? |
| **both, additively (r_dd)** | **{{a2_rdd}}** | **{{a2_rdd_ci}}** | **at a given depth, in a given rollout, does disagreement know?** |

[^stepcount]: Adjacent forecast steps on the same {{a2_nind}} trajectories are heavily dependent — structurally the same problem §6.6 spends a page correcting for the 45 coupled state dimensions. The count is descriptive; the interval {{d2r_win_ci}} is the statistic, and no P-value attaches to {{d2r_win_pos}}/{{d2r_win_n}}.

The weakest figure across the {{d2r_ncontrols}} depth controls is {{d2r_weakest}}, so disagreement
is not re-encoding the clock: at a fixed depth it still knows which rollouts are going wrong. But
depth was never the only confound. Per-episode difficulty spans {{d12_lo}} to {{d12_hi}} and is
uncorrelated with commanded speed, so if harder trajectories simply have both larger error and
larger disagreement, the pooled correlation would look exactly as it does with disagreement
carrying no within-rollout information at all. Two things pointed there: the
{{a2_h1_npoints}}-point h = 1 figure of {{a2_h1_r}}, which is not the shape of a genuine per-step
signal, and the within-step control coming out *above* the pooled figure, the signature of a
between-unit effect.

**The verdict.** The between-trajectory correlation is {{a2_r_between}} and the two components
contribute {{a2_share_between}}% and {{a2_share_within}}% of the pooled covariance, so a large
part of what this section reports is a between-rollout effect. That reinterprets the within-step
control: it is a mean of {{d2r_win_n}} between-trajectory correlations, which is why it reads
{{d2r_win}} against the pooled {{a2_r_pooled}} rather than below it. The decisive statistic is the
double-demeaned one, and it survives: {{a2_rdd}} {{a2_rdd_ci}} at n_independent = {{a2_nind}},
against the rule's pre-committed threshold that the interval exclude zero and a minimum detectable
effect of {{p1_m45_mde}} from the bootstrap's standard error; a dilution study missed an effect of
{{p1_m45_undetected}} and caught one of {{p1_m45_detected}}. **The rule returns
{{m45_verdict}}**: with both the rollout and the depth held constant, disagreement still tracks
error rather than merely reporting which episode is hard.
**Per horizon, on the same {{a2_nind}} trajectories and the same kind of cluster bootstrap:** it is
a separate run, so its h = {{v2_diag_h}} interval differs from the one above in the third
decimal, as the pooled interval above does from §6.2's {{d4_ci}}.

| h | r_dd, double-demeaned | 95% CI | excludes zero |
|---|---|---|---|
| 1 | — | — | — |
| 8 | {{a2_rdd_h8}} | {{a2_rdd_ci_h8}} | no |
| 32 | {{a2_rdd_h32}} | {{a2_rdd_ci_h32}} | no |
| **{{v2_deploy_h}}** | **{{a2_rdd_h100}}** | **{{a2_rdd_ci_h100}}** | **yes** |
| 128 | {{a2_rdd_h128}} | {{a2_rdd_ci_h128}} | yes |
| {{v2_diag_h}} | {{a2_rdd_h368}} | {{a2_rdd_ci_h368}} | yes |

*(h = 1 has one forecast step per trajectory, so there is nothing within a rollout to demean against and r_dd is undefined rather than zero.)*

Two qualifications go with that. The within-rollout effect is **materially smaller than the pooled figure**, {{a2_rdd}} against {{a2_r_pooled}}, so a practitioner should expect disagreement to separate *rollouts* better than it separates *moments within a rollout*. And it is **not established at short horizon**: r_dd's interval excludes zero at {{a2_excl_h}} and spans zero at {{a2_spans_h}}, where too few steps exist to demean against. At h = {{v2_deploy_h}} it is established, at {{a2_rdd_h100}} {{a2_rdd_ci_h100}}.

**The h = 1 figure survives the same test, but it is not what it looked like.** At h = 1 the panel
has one column, so {{a2_h1_r}} is a correlation over {{a2_h1_npoints}} *trajectory-level* points
and nothing within a rollout is being tested. Disagreement correlates {{a2_h1_speed_r}} with
commanded speed and {{a2_h1_diff_r}} with per-episode difficulty, and partialling both out of the
disagreement–error correlation leaves {{a2_h1_partial_both}}: it does not move, so the figure is
real and not a difficulty artifact. It is nevertheless a statement about **ranking whole rollouts
at one step ahead**, on {{a2_h1_npoints}} points, and §9 states it that way.

**Does it hold on a model we trained?** Everything above is measured on the released checkpoint, because our main arms run at ensemble size 1 where the epistemic term is identically zero. We therefore trained three Arm A arms at **ensemble size 5**, identical in every other setting, under a rule committed to git before the runs existed (rule M-43, Appendix E). It asked that disagreement lead the index at every horizon, and that the paired difference exclude zero at a majority of them.

**It returns {{e5_verdict}}.** The first condition passes completely: disagreement leads
the index in **{{e5_lead_cells}} of {{e5_total_cells}}** seed-horizon cells, every paired
estimate positive, {{e5_diff_lo}} to {{e5_diff_hi}}. The second fails: the paired difference
excludes zero at {{e5_n_excl}} of {{e5_n_horizons}} horizons, not a majority. We report the
verdict the rule returns and do not rewrite the rule, nor its denominator: it was committed over
{{e5_n_horizons}} horizons, and adding h = {{v2_deploy_h}} after the fact would change what "a
majority" means in a discharged rule. The released checkpoint's table above follows the six-horizon
grid, because no pre-registration is stated over it, so the two counts are deliberately different.

**What separates the two conditions is sample size, and we measured that rather than asserting it.** Our own arms can only be scored out-of-sample on the held-out pair, n_independent = {{e5_nind}}, where the released checkpoint's finding used {{d1n_nind}}. Subsampling four trajectories at a time from a twenty-trajectory pool, the rule's criterion fires on {{e5_power_mean}}% of draws on average and on only {{e5_power_worst}}% at h={{e5_power_worst_h}}. That estimate is an **upper bound**, because the pool it subsamples is in-sample for these arms, where the effect is {{e5_eff_ins}} against {{e5_eff_oos}} on the held-out pair. So the rule was under-powered at the sample size it faced, decisively at one horizon. We do not claim it could not have passed, only that it was committed without checking what it could detect: a failure of ours, the same one the ledger records as M-24, a rule anchored without regard to the regime it would be applied in.

*Reported as a companion and not as a discharge:* on all ten episodes (n_independent = {{e5_comp_nind}} 400-step trajectories, **in-sample** for these arms, which trained on eight of them) the same measurement excludes zero at {{e5_comp_excl}} of {{e5_comp_n}} horizons and would have satisfied both conditions. It cannot discharge the rule, which is stated over the out-of-sample arena; we record it only so the comparison with the released checkpoint's {{d1n_nind}} is like for like.

**We ran the baseline test expecting it to go the other way.** A counter matching disagreement would have been the more consequential result, making the trust metric close to vacuous, since a counter is free. We record that as an expectation only: it was not committed to git before the data existed, so by this paper's own standard (§8) it is not a pre-registration. It did not go that way against the counter. It went that way against something else.

**One adversary is one, so we added two more, and the ranking claim survives only one of them.**
A claim that beats exactly one competitor is a claim about that competitor. Under a rule committed
before either was computed (rule M-51, Appendix E, corrected by rule M-52), we added two baselines
needing no ensemble and no second model: `step-size`, the magnitude of the model's own predicted
state change ‖µ_t − µ_{t−1}‖, which costs nothing because the rollout has already made those
predictions; and `entry-res`, its one-step error at the step *before* the forecast window opens,
which costs **one extra rollout in this harness** and nothing in deployment, where a model consumes
the history to build its recurrent state anyway. The first rule called both free without
distinguishing those, and the second records the correction.

| baseline | r(baseline, error) | margin | partial r(disagreement given baseline) | beaten? |
|---|---|---|---|---|
| forecast step index *(the existing adversary)* | {{e7_index_r}} | {{e7_index_margin}} | {{e7_index_partial}} | — |
| `step-size` — ‖µ_t − µ_{t−1}‖ | **{{e7_step_r}}** | {{e7_step_margin}} | {{e7_step_partial}} | **{{e7_step_beaten}}** |
| `entry-res` — one-step error before the window | {{e7_entry_r}} | {{e7_entry_margin}} | {{e7_entry_partial}} | {{e7_entry_beaten}} |

*r(disagreement, error) = {{e7_r_dis}} on the released checkpoint at n_independent = {{e7_nind}} 400-step trajectories.
Minimum detectable effect, estimated before either baseline existed: {{e7_mde_margin}} on a margin,
{{e7_mde_partial}} on a partial.*

**The verdict is {{e7_verdict}}, and the reason is the row a reader should look at twice.**
Disagreement beats {{e7_n_beaten}} of the {{e7_n_new}} free baselines added here. The
magnitude of the model's own predicted state change ranks realised error at {{e7_step_r}}, against
{{e7_r_dis}} for the five-member ensemble disagreement the method is built on. The margin between
them, {{e7_step_margin}}, is **below** the {{e7_mde_margin}} this sample size can resolve, so at
n_independent = {{e7_nind}} 400-step trajectories we cannot say the ensemble ranks better than a
subtraction.

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

*A note on the `undefined` cell.* The within-step control holds the forecast step fixed and
correlates across trajectories, so it annihilates any quantity that is constant across
trajectories at a fixed step — which is the forecast index, whose within-step correlation is
therefore {{e7_index_ws}} rather than zero. It does **not** annihilate a per-trajectory scalar
like `entry-res`, which varies across exactly the axis the control varies over. Rule M-51 said the
opposite, and `M-54` records the correction.

### 6.8 One constant scalar does not fix it; a per-horizon one lands within the band, though no single cell is resolvable at this arena

**Recalibrating a dynamics model's uncertainty inside model-based RL is not new** (§2). What is
new here is the conditioning variable, the *forecast horizon*, and one negative result: a single
global multiplier **fails** where a per-horizon one shows no sign of failing. An open-loop
rollout's error accumulates with depth while its predicted σ does not (§6.9), so a horizon-blind
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

Fitting at one step works at one step and nowhere else. On the epistemic term — the quantity the
method uses — a scalar of {{d2_epi_c_lo}}–{{d2_epi_c_hi}} brings h=1 coverage to
{{d2_epi_cov1_lo}}–{{d2_epi_cov1_hi}}%, essentially calibrated against the {{d2_target}}% target,
and leaves h=368 at {{d2_epi_cov368_lo}}–{{d2_epi_cov368_hi}}%. On the aleatoric term a scalar of
{{d2_ale_c_lo}}–{{d2_ale_c_hi}} gives {{d2_ale_cov1_lo}}–{{d2_ale_cov1_hi}}% at h=1 and
{{d2_ale_cov368_lo}}–{{d2_ale_cov368_hi}}% at h=368. Fitting over the whole rollout instead
drives one-step coverage to 100%, an interval wide enough to be vacuous where the model is
accurate, while still falling short at the far end. A constant multiplier cannot track an error
that grows while σ does not (§6.9), so for a *constant* scale "right shape, wrong scale" does not
survive.

**On the released checkpoint a per-horizon scalar lands near target, and this is the one concrete remedy in this paper; on a model that has not seen the test episodes the evidence is mixed.** One multiplier per horizon is fitted on one held-out episode and evaluated on the other, in both directions, so no multiplier is ever scored on the episode that produced it. The two held-out episodes contribute {{d3_nind_tot}} non-overlapping 400-step trajectories between them, so each direction fits on n_independent = {{d3_nind_fit}} and is scored on the other {{d3_nind_fit}}. The last column repeats the test on Arm A at ensemble size {{d3x_ens}} and {{iters_main}} iterations ({{d3x_nseeds}} seeds), whose model never saw either episode:

| quantity | released checkpoint: cells unseen by the multiplier within {{d3_tol}} points of {{d3_target}}%, per-horizon c (unpowered) | same, constant c | same, per-horizon c fitted on a *different model* (unpowered) | range of fitted c | Arm A, its own per-horizon c: cells within the band, unseen by the model too |
|---|---|---|---|---|---|
| aleatoric | **{{d3_ale_ok}} / {{d3_ale_cells}}** | {{d3_ale_const_ok}} / {{d3_ale_cells}} | {{d3x_ale_ok}} / {{d3x_ale_cells}} | {{d3_ale_c_lo}} – {{d3_ale_c_hi}} ({{d3_ale_cspread}}×) | {{d3x_own_ale_ok}} / {{d3x_own_ale_cells}} |
| epistemic | **{{d3_epi_ok}} / {{d3_epi_cells}}** | {{d3_epi_const_ok}} / {{d3_epi_cells}} | {{d3x_epi_ok}} / {{d3x_epi_cells}} | {{d3_epi_c_lo}} – {{d3_epi_c_hi}} ({{d3_epi_cspread}}×) | {{d3x_own_epi_ok}} / {{d3x_own_epi_cells}} |

On the released checkpoint every point estimate lands within {{d3_tol}} points of the {{d3_target}}% target for both quantities. **That absolute test is UNPOWERED here, as in the *different model* column:** `results/p4_transfer_power.json` scored this model under these very multipliers and found the {{d3_tol}}-point band resolvable at {{d3x_tol_res}} of {{d3x_tol_pairs}} quantity-by-horizon pairs, with a binding minimum detectable effect of {{d3x_umde_lo}}–{{d3x_umde_hi}} points. So a cell inside the band is compatible with a true coverage well outside it, and nothing here shows any cell is outside it either. The largest deviation over all {{d3_ncells_all}} held-out cells is {{d3_worst_q}} at h={{d3_worst_h}}, fitted on episode {{d3_worst_ep}} and scored on the other, at {{d3_worst_cov}}%, {{d3_worst_dev}} points off target. The two largest deviations are both on the {{d3_second_q}} term and {{d3_top2_same_side}} target — {{d3_worst_cov}}% at h={{d3_worst_h}} and {{d3_second_cov}}% at h={{d3_second_h}} — so the fitted multiplier is mildly **conservative** at the long horizons rather than unstable in both directions. The constant scalar manages {{d3_epi_const_ok}} of {{d3_epi_cells}}, and those are the h=1 cells it was fitted at. **On Arm A, where the episodes are unseen by the model as well, its own multipliers manage {{d3x_own_epi_ok}} of {{d3x_own_epi_cells}} epistemic and {{d3x_own_ale_ok}} of {{d3x_own_ale_cells}} aleatoric cells**, so the recipe that lands every released-checkpoint cell does not carry over intact to a model that has not seen the test episodes.

**Three cautions.** The per-horizon scalar has one free parameter per horizon against the constant one's one, so it *must* fit better in sample; only cells unseen by the multiplier are evidence, and those are the cells reported. **That column is thinner than its count suggests:** the {{d3_epi_cells}} cells are {{d3_nhoriz}} horizons × two fold directions on the same {{d3_nind_tot}} trajectories, each multiplier fitted on n_independent = {{d3_nind_fit}} and scored on the other {{d3_nind_fit}}. They are not {{d3_epi_cells}} independent successes and no P-value attaches to the count, which is reported so a reader can see how thin the evidence is; later sections refer back to this as the §6.8 caution. And the correction is a calibration patch, not a fix: it leaves σ carrying no more information than before and rescales it by how far ahead you are looking. On the released checkpoint it nevertheless brings every estimate unseen by the multiplier near what the interval claims, which is what a downstream user needs, and it costs one lookup table.

**The fourth column: the table is a property of the model, not of the horizon.** Everything above is established across *episodes*, on one model. Whether the same lookup table works on a *different* model is a separate claim, and rule M-69 (Appendix E) fixed what an answer would look like — criterion, arena, horizons and minimum detectable effect — before any cross-model multiplier was computed. Multipliers were fitted on Arm A at ensemble size {{d3x_ens}} ({{d3x_nseeds}} seeds) and scored on the released checkpoint, then the reverse, over the same {{d3x_nind}} held-out trajectories and {{d3_nhoriz}} horizons. The statistic the rule governs on is the **paired** change in held-out coverage, coverage under the other model's multiplier minus coverage under the same model's, on the same trajectories, because this arena can resolve that (largest minimum detectable effect {{d3x_pmde_hi}} points against the ±{{d3x_band}}-point band) and cannot resolve the absolute one. The verdict is **{{d3x_verdict}}**: of {{d3x_ncells}} governing cells, {{d3x_n_out}} have a 95% interval on the paired change lying entirely outside the band, {{d3x_n_in}} entirely inside and {{d3x_n_strad}} straddling an edge, and the largest paired change has magnitude {{d3x_worst_delta}} points. That is branch {{d3x_branch}} of the rule's three. Per direction the verdict is the same: fitting on Arm A, **{{d3x_verdict_a2r}}** ({{d3x_n_out_a2r}} of {{d3x_ncells_a2r}} cells outside the band); fitting on the released checkpoint, **{{d3x_verdict_r2a}}** ({{d3x_n_out_r2a}} of {{d3x_ncells_r2a}}). The plainest statement of the gap is the multipliers themselves: Arm A's are {{d3x_ratio_lo}}× to {{d3x_ratio_hi}}× the released checkpoint's at the same horizon.

**The *different model* column is the absolute test, and it is unpowered for the reason above**, so a cell inside its band is not evidence the multiplier transferred. It is reported because dropping it would hide that this arena cannot resolve it; it is not the verdict and cannot move it. The §6.8 caution applies here unchanged and harder: the {{d3x_ncells}} governing cells are not {{d3x_ncells}} independent tests, the {{d3x_nseeds}} Arm A seeds share their training data and differ only in initialisation and ordering, and no P-value attaches to any count here. The two models also differ on several axes at once, so this bounds transfer between these two models rather than attributing it to any one difference.

So the accurate form of this section is: **a constant scalar does not repair the interval; on the released checkpoint a per-horizon one brings every estimate unseen by the multiplier within the band, though no single cell is resolvable at this arena, and does so across episodes but not across models. On episodes unseen by the model as well, Arm A's own multipliers manage {{d3x_own_epi_ok}} of {{d3x_own_epi_cells}} epistemic cells, so there the evidence is mixed.**

### 6.9 The structural excuse does not survive

One could argue that a model trained on an 8-step horizon cannot be expected to report calibrated
uncertainty about step 368. It cannot report it about step 8 either. Inside the trained horizon,
σ is flat while error grows (Figure 5; {{sig_arena}}, n_independent = {{sig_nind}} 400-step trajectories; our arms at
{{iters_main}} training iterations, the released checkpoint as released):

| model | σ growth, step 1 → 8 | error growth, step 1 → 8 |
|---|---|---|
| faithful Arm A | {{sig_faithA_growth}}× | {{err_faithA_growth}}× |
| corrected Arm A | {{sig_nll_growth}}× | {{err_nll_growth}}× |
| teacher-forced Arm B | {{sig_armB_growth}}× | {{err_armB_growth}}× |
| released checkpoint | {{sig_rel_growth}}× | {{err_rel_growth}}× |

The faithful arm's σ *declines* ({{sig_faithA_growth}}×) while its error grows
{{err_faithA_growth}}×. The coverage collapse in Figure 3(b) is therefore driven entirely by
growing error against a fixed σ.

### 6.10 Testing the mechanism: an ensemble that shares nothing

§6.4 establishes the topology as a fact and the mechanism as a hypothesis. This subsection tests
the hypothesis, under a rule committed to git before any of the artifacts below existed (rule
M-44, Appendix E), with a power check estimating what it could detect at the sample size it would
face.

**The contrast, and why it is affordable.** Training {{r2_n_indep}} genuinely independent models
from scratch costs about {{r2_scratch_h}} h of wall clock on two cores at these runs' iteration
count, against the {{rt_hours}} h Appendix B gives for all of §5–§7's runs. Arm A at ensemble size 1 already
existed at seeds 0, 1 and 2; we added {{r2_n_added_word}} more at about {{r2_added_h}} h each,
{{r2_added_h_total}} h in total, and scored the {{r2_n_indep}} together as an ensemble **at
evaluation time**. There is no new training code and no new architecture, and the disagreement
across {{r2_n_indep}} independently initialised *full models* is exactly the contrast §6.4 asks
for. The rollout protocol mirrors the shared-trunk one in every respect except the one under test:
each member sees the same input state, each keeps **its own** recurrent hidden state, and the
ensemble mean is fed back to all of them.

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

*Shares are of the log improvement, so they add to 100%. A share above 100% at h=1 means the
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
ordering (§11), so this comparison **bounds** the architectural effect rather than isolating it,
and the bound is generous to the mechanism by construction.

**And it does not repair the interval.** The independent ensemble is
{{r2_indep_ratio_h100}}× overconfident at h = {{v2_deploy_h}} with
{{r2_indep_cov1_h100}}% coverage where a calibrated Gaussian gives {{v3_cov_nominal1}}%. Better by
a factor of {{m44_ratio_gain}}, and still not an interval. Building the ensemble properly is worth
doing and it is not sufficient; §6.8's per-horizon multiplier remains the only correction in this paper whose estimates all land within the band, though only on the released checkpoint and no single cell is resolvable at this arena. On Arm A, whose model never saw the test episodes, it manages {{d3x_own_epi_ok}} of {{d3x_own_epi_cells}} epistemic cells (§6.8).


### 6.11 Both fixes on the same models: the combined arm

§6.10 changes the **topology** and holds the objective at `mse`; §6.5's arms change the
**objective** and hold the topology at ensemble size 1, where disagreement is zero by construction.
Neither answers the practitioner's question of what the two give together, and adding two effects
never measured on the same model is the arithmetic this paper criticises elsewhere. This subsection
runs the combination, under a rule committed to git before either new member existed (rule M-68,
Appendix E), with a minimum detectable effect estimated in advance as well.

**The arm.** {{m68_n_indep}} independently initialised full models, sharing no trunk and no hidden
state, trained under `gaussian_nll`, every setting identical to §6.10's arm except the loss type.
Three of the five, seeds 0, 1 and 2, already existed under that objective; two more were trained,
and the {{m68_n_indep}} are scored together as an ensemble at evaluation time under §6.10's rollout
protocol, on the same held-out arena of non-overlapping 400-step trajectories at
n_independent = {{m68_nind}}, over the same six horizons.

**Which σ the coverage is against.** The combined arm is the first arm in this paper carrying
**both** an aleatoric head that has not collapsed to zero and an across-member epistemic spread.
The figures below are the **epistemic** one, {{m68_sigma_used}}: the quantity the rule names and
§6.10's table reports, so the two tables are comparable line for line. The aleatoric head is
reported in §6.5 and does not enter here.

| h | combined err/σ | shared-trunk err/σ | combined ±1σ | shared ±1σ | combined ±2σ | shared ±2σ |
|---|---|---|---|---|---|---|
| 1 | {{m68_indep_ratio_h1}}× | {{m68_shared_ratio_h1}}× | {{m68_indep_cov1_h1}}% | {{m68_shared_cov1_h1}}% | {{m68_indep_cov2_h1}}% | {{m68_shared_cov2_h1}}% |
| 8 | {{m68_indep_ratio_h8}}× | {{m68_shared_ratio_h8}}× | {{m68_indep_cov1_h8}}% | {{m68_shared_cov1_h8}}% | {{m68_indep_cov2_h8}}% | {{m68_shared_cov2_h8}}% |
| 32 | {{m68_indep_ratio_h32}}× | {{m68_shared_ratio_h32}}× | {{m68_indep_cov1_h32}}% | {{m68_shared_cov1_h32}}% | {{m68_indep_cov2_h32}}% | {{m68_shared_cov2_h32}}% |
| **{{v2_deploy_h}}** | **{{m68_indep_ratio_h100}}×** | **{{m68_shared_ratio_h100}}×** | **{{m68_indep_cov1_h100}}%** | **{{m68_shared_cov1_h100}}%** | {{m68_indep_cov2_h100}}% | {{m68_shared_cov2_h100}}% |
| 128 | {{m68_indep_ratio_h128}}× | {{m68_shared_ratio_h128}}× | {{m68_indep_cov1_h128}}% | {{m68_shared_cov1_h128}}% | {{m68_indep_cov2_h128}}% | {{m68_shared_cov2_h128}}% |
| {{v2_diag_h}} | {{m68_indep_ratio_h368}}× | {{m68_shared_ratio_h368}}× | {{m68_indep_cov1_h368}}% | {{m68_shared_cov1_h368}}% | {{m68_indep_cov2_h368}}% | {{m68_shared_cov2_h368}}% |

*Same trajectories, same harness, same bootstrap unit as §6.10, every model at {{iters_main}} training iterations. The shared-trunk columns are the
mean over {{m68_n_shared}} seeds; the comparison below is paired against each of them separately.*

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

*The same σ-versus-accuracy split §6.10 uses, so the two arms' improvements can be compared part by
part. Shares are of the log improvement, so the two columns add to one.*

**The objective's own contribution is below what this design can resolve.** The rule scores the
combined arm against the **shared-trunk** arms, so its verdict measures the two fixes together. The
comparison that isolates the objective is against §6.10's independent arm, which differs from this
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
calibrated than the shared-trunk arms by essentially the amount §6.10 measured for independence
alone ({{m44_ratio_gain}}× there, {{m68_ratio_gain}}× here). **The two fixes do not add. A reader
who added them would have been wrong, which is why the arm was run.** That the objective's separate
effect is at most small is not a surprise once stated: the objective governs the **aleatoric**
head, and the epistemic term is a spread across members that the loss never sees.

**And it still does not repair the interval.** The combined arm is {{m68_indep_ratio_h100}}×
overconfident at h = {{v2_deploy_h}} with {{m68_indep_cov1_h100}}% coverage where a calibrated
Gaussian gives {{v3_cov_nominal1}}%. Better than the shared-trunk arms, no better than independence
alone, and still not an interval. §6.8's per-horizon multiplier remains the only correction in this paper whose estimates all land within the band, though only on the released checkpoint and no single cell is resolvable at this arena. On Arm A, whose model never saw the test episodes, it manages {{d3x_own_epi_ok}} of {{d3x_own_epi_cells}} epistemic cells (§6.8).

**What the arm does not separate.** It differs from the shared-trunk arms on three axes at once:
trunk sharing, the objective, and capacity (a factor of {{v1_cap_ratio}} in state-pathway
parameters, as §6.10's contrast also does; §11), and independently seeded runs also differ in data
ordering. The rule said so in advance: it bounds the combination and attributes nothing. The one
further comparison here, the `mse`/`gaussian_nll` pair above, which holds every other axis fixed,
sits outside the rule's governing statistics and under the design's own minimum detectable effect,
so it bounds the objective's separate contribution rather than measuring it.

---

## 7. Defects in the released pipeline

**7.1 Ten unmarked episode boundaries.** §3. The window builder reads a termination column that is
identically zero, so it marks all {{win_naive}} windows valid.

**7.2 Training and evaluation disagree on action alignment, and evaluation is the broken one.**
Row *t* holds the action that *produced* state *t*. The data say so directly: at every reset row
all twelve actions are exactly zero (§3), and a policy network with biases cannot emit exact zeros,
so those zeros mark the absence of a producing action — the reset produced that state, not a policy
step. The training path pairs states and actions index-for-index, which is causally correct; the
evaluation path feeds the action from *t−1* to predict state *t*, stale by one step.

What the stale pairing costs is concentrated at short horizons; at h = {{v2_diag_h}} it is small, and its
sign is not consistent. On the held-out pair's
{{ad_nind}} independent trajectories it overstates the released checkpoint's error at
h = {{v2_diag_h}} by **{{ad_rel}}% {{ad_rel_ci}} on relative-L1** and **{{ad_nrmse}}%
{{ad_nrmse_ci}} in nRMSE** (each a 95% interval from a cluster bootstrap over whole trajectories, both pairings
inside each draw; `results/alignment_defect_ci.json`). Shifting the evaluation loop's two action
slices by one step (`model_training.py:129` and `:132`) aligns it with training; our harness
does this with `action_offset = 1` (`src/score_reference.py:180-190`). The four per-trajectory values are {{ad_rel_traj}}
on relative-L1 and {{ad_nrmse_traj}} in nRMSE. Over all ten episodes, {{ad20_nind}} independent
trajectories, the sign reverses: {{ad20_rel}}% {{ad20_rel_ci}} on relative-L1 and {{ad20_nrmse}}%
{{ad20_nrmse_ci}} in nRMSE, with single trajectories from {{ad20_traj_lo}}% to {{ad20_traj_hi}}%.
Every arena here is in-sample for this checkpoint, which trained on all ten episodes. One step ahead, where a
stale action should matter most, it changes the checkpoint's relative-L1 error by {{adh_rel_h1}}%
{{adh_rel_ci_h1}} on the held-out pair's {{ad_nind}} trajectories, and by {{adh_rel_h100}}% {{adh_rel_ci_h100}}
at h = {{v2_deploy_h}}, the method's own horizon (`results/alignment_by_horizon.json`). Our own Arm A
checkpoints at {{iters_long}} iterations, trained under the causal pairing, change by {{stale_armA_rel_h1}}%
at h = 1 and {{stale_armA_rel_h368}}% at h = {{v2_diag_h}} when fed the stale one (three-seed mean,
relative-L1, held-out pair).

**7.3 No held-out evaluation.** Evaluation trajectories are drawn from training data. For the
released checkpoint, trained on the entire file, no held-out measurement is possible at all, and neither pinned repository can generate the data that would make one possible (§3).

**7.4 What the spliced windows cost: nothing measurable.** We trained a contaminated arm on
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
helps in {{tw_cc_cluster_helped}} (Figure 6a). The control is inert, differing from clean in
{{tw_dc_cluster_helped}} cells.

**So "costs nothing" is too strong.** Splicing raises training loss by {{contam_cost_pct}}% against
duplication's {{dup_cost_pct}}%, and improves rollout in {{tw_cc_cluster_helped}} of {{tw_cells}}
cells: measured effects in opposite directions, the signature of regularisation. The spliced
windows contain transitions the model cannot fit, it fits the rest less tightly as a result, and it
rolls out slightly better. The defensible statement is that **at this rate the splices do not harm
rollout and appear to help slightly. The unmarked boundaries remain a real defect on leakage
grounds; the physically-impossible-transition component costs nothing detectable at this rate.**

---

**7.5 The released artifacts do not reproduce the released checkpoint's variance state.**
The σ collapse is linear in iteration count and its rate is nearly identical across our runs
(§6.3), which makes it a clock, and read as a clock it puts the checkpoint's variance state out
of reach of a constant-rate run from the released initialisation at the configured learning rate,
at every iteration count the release, the paper and the checkpoint tag state. The first author's
account is that the released repository is several revisions removed from the setup that trained
the checkpoint, which supplies a mechanism, a warm start or a different `log_delta_logstd`
initialisation, that would explain it with no inconsistency at all. So this is a **documentation
gap between a release and a run**: common, worth recording, and much less interesting than an
inconsistency. `docs/APPENDIX_G_VARIANCE_ARITHMETIC.md`, shipped as supplementary, gives the
arithmetic and the five assumptions it rests on.

---

## 8. Method

**An append-only ledger.** Every claim here has a permanent identifier, an evidence class (source, data, run, external, inference) and a status, in `FINDINGS_LEDGER.md` ({{n_entries}} entries). Claims are never edited in place: one that turns out to be wrong is marked superseded, pointed at what replaced it, and kept.

**Pre-registration, and one failure of it.** Decision rules were committed to git before the data that tested them, with one exception. Figure 1 gives the lead time for {{f4_n_rules}} of them and Appendix E for all {{appG_n_rules}}; {{f4_n_positive}} of Figure 1's are positive and {{f4_n_negative}} is not. Figure 1 plots the set it was drawn over; Appendix E adds every rule since. Every positive bar is a difference of two commit timestamps. **The negative one is not**: it is the duplication-control rule (§7.4), whose *data* side is the moment the control runs finished, a line in `results/control_driver.log` rather than a commit, dated from the commit that introduced that line. The rule was stated in conversation before the runs and reached git **{{lead_task3}} after they finished**, and we found it only by auditing our own `git log`. The measurement stands, because the arm was built without reference to its outcome, but the claim that it was pre-registered does not, and it is withdrawn (`S-12`). A discipline that is only checked when it succeeds is not a discipline.

**{{n_retractions_word}} claims withdrawn on evidence**, and {{n_retract_framing_word}} framings withdrawn rather than numbers, out of {{n_superseded}} superseded entries kept in the record (the supplementary `docs/BUILD_CHECKS.md` lists them). The most consequential of the framings withdrawn is `S-15`: the inference from per-dimension sign counts to a binomial P-value, which assumed an independence the 45 state dimensions do not have (§6.6). Found by our own pre-submission audit, it withdraws the strength of evidence behind what an earlier draft called its strongest result.

**A statistic that was resampling the wrong unit.** Our bootstrap pooled three seeds over a shared trajectory set and resampled the pooled vector while reporting the independent-trajectory count, so each trajectory appeared three times. Resampling trajectories instead widens intervals by a mean {{bu_mean_ratio}}× and changes {{bu_changes}} of {{bu_cells}} verdicts, in {{bu_change_cell}}, already recorded as unresolvable. Every long-horizon verdict survives; both units are reported.

**Reproducibility, and a build that checks its own prose.** Every measured number in this paper is
substituted from an artifact on each build, and a quick run on a clean clone (`./reproduce.sh --quick --force`, which skips
training) rewrites {{ver_claim_pct}}% of the numeric values under `results/` that the comparison counts; the rest are carried in
and prove nothing about reproduction. **The number of regenerated values that differ and are
themselves a measurement, a statistic or the verdict of a test is {{ver_part_sci}}.** One of the
build's own gates, the clean-clone check in `part_f_gate`, requires that no regenerated value differ
at all; {{ver_differing}} do, so it fails, and it is published as failing rather than given a
tolerance. The accounting behind these figures, the registry of checks the build runs on this
paper's own prose, and the paper's record of verifying its own claims are in `docs/BUILD_CHECKS.md`,
shipped as supplementary.

---

## 9. Actionable lessons

{{n_lessons_word}} things a practitioner can apply without reading the rest of this paper.

**Use ensemble disagreement as a ranking signal, but price it against the free alternatives first. Do not read it as a distance. And expect it to degrade with horizon.** At one forecast step it ranks whole rollouts almost perfectly, {{d2_epi_h1}} {{d2_epi_ci_h1}} across the {{a2_h1_npoints}} trajectories, a ranking of *rollouts* rather than of moments within one, because at h=1 there is only one moment. Over the full rollout it falls to {{d4_r}} {{d4_ci}}: excellent where you can check it cheaply and merely good where you most need it. It beats the forecast step index at every horizon we tested, on a paired test that excludes zero at {{d2p_n_separating}} of the {{d2p_n_horizons}} horizons where the index is defined, and retains {{d2b_par_all}} once that index is partialled out (§6.7). **What it does not clearly beat is the model's own predicted step size**, which costs nothing and needs no ensemble: that ranks error at {{e7_step_r}} against disagreement's {{e7_r_dis}}, a margin of {{e7_step_margin}}, below the {{e7_mde_margin}} this sample can resolve. Disagreement carries information the subtraction does not, retaining {{e7_step_partial}} once step size is partialled out, and with both the forecast depth and the rollout held constant it still correlates {{a2_rdd}} {{a2_rdd_ci}} with error (§6.7); but a practitioner about to pay for five members should price the subtraction first. And it is too small to be an interval by a wide margin: at h = {{v2_deploy_h}}, the horizon the method rolls out over, {{d1n_epi_ratio_h100}}× [{{d1n_epi_ratio_ci_h100}}] on the released checkpoint and {{e5_ratio_h100}}× [{{e5_ratio_ci_h100}}] on the ensemble-5 arms we trained. A risk gate or safety margin that reads σ as a distance is not supported at any horizon, on either.

**If you need the interval, rescale per horizon, not globally, and refit on your own model.** One multiplier per forecast horizon, fitted on one episode and scored on another, brings every released-checkpoint coverage estimate within {{d3_tol}} points of nominal, though this arena cannot resolve any single cell to that band; a single global multiplier manages {{d3_epi_const_ok}} of them (§6.8). That checkpoint trained on both episodes; on Arm A, whose model never saw them, its own multipliers manage {{d3x_own_epi_ok}} of {{d3x_own_epi_cells}} epistemic cells. The cells are not independent trials (the §6.8 caution), so read the sweep as consistency and the per-cell deviations as the evidence. The fitted multipliers span {{d3_epi_cspread}}× across horizons, which is precisely why one number cannot serve.

**Do not convert per-dimension sign counts into P-values.** State dimensions in a robot are physically coupled and share a forecast-depth trend, so an independent-trials null is badly wrong, in our tables by up to {{perm_worst_factor}}× (§6.6). Permute whole trajectories instead. An earlier draft of this paper used the binomial version, and it made our weakest evidence look like our strongest (`S-15`).

**Count independent trajectories, not trajectories.** Two 400-step windows that overlap at all
are one piece of evidence, not two. The held-out arena here contains {{nind_oos_400}} independent
400-step trajectories however many windows are drawn from it, and that number bounds every
long-horizon claim (§3); reporting an interval beside a trajectory count rather than an
independent-trajectory count overstates precision. Resampling pooled seed × trajectory values instead of trajectories narrows
intervals by a further {{bu_mean_ratio}}× (§8).

**Anchor a decision rule to the horizon the claim is about.** Our first pre-registered rule was
anchored at h = 8, the training forecast horizon, and returned "cannot be settled"; the claim was
about deployment horizons. The rule was correct in form and pointed at the wrong regime, a failure
mode pre-registration does not protect against on its own.

**Check that the implemented loss is the described loss before reproducing any number from it.**
The paper describes two loss terms; the implementation has {{diff_terms}}. The predicted variance has an optimum at zero under the implemented one, which is why the released checkpoint's σ is {{d1n_alea_ratio_h100}}× smaller than its own error at h = {{v2_deploy_h}}, and {{d1n_alea_ratio_h368}}× at h = {{v2_diag_h}}. Reading the loss took an afternoon and explained a
result that would otherwise have looked like a training bug.

---

## 10. Broader impact

This is a reproduction of a dynamics model on public simulation data. It creates no new
capability, uses no personal data and deploys nothing.

The findings bear on one practice, and it is not the one the original method uses. The follow-up
applies ensemble disagreement as a reward penalty. For that use, our measurements support its
ordering (§6.7), with the qualification that a free signal ranks error nearly as well. A different
use is reading the same number as an error bar, a safety margin, or a trigger for handing control
to a fallback controller. The original papers neither make nor recommend that use, and it is the
use our measurements rule out. At the method's own {{v2_deploy_h}}-step horizon, the disagreement
is {{d1n_epi_ratio_h100}}× smaller than realised error and covers {{d1n_epi_cov1_h100}}% of
outcomes where {{v3_cov_nominal1}}% is expected. We say this because the released checkpoint
exposes the quantity, and it is easy to read as an interval.

We do not claim the original method is unsafe. No policy is trained here. The one policy-free
test we ran found that correcting the scale per horizon leaves every pairwise ordering of
accumulated penalty unchanged on the available trajectories (§11).

---

## 11. Limitations

**Effective sample size bounds every long-horizon claim.** The out-of-sample arena has
{{m23_nind}} independent 400-step trajectories (the n = {{m23_nind}} caveat of §3). That is the
binding constraint on §5, and no amount of trajectory oversampling changes it. Nor can a larger
dataset be generated here: the data generator is in neither pinned repository, and the one the lite
release points to runs in a simulator this work did not have (§3). The released checkpoint's lack
of a held-out arena is therefore a constraint, not a choice.

**Ensemble size: supported, not established.** Our main arms run at ensemble size 1, where the epistemic term is identically zero, so the epistemic measurements were first made on the released checkpoint alone. The {{e5_seeds}} ensemble-5 Arm A arms (§6.7) reproduce the *direction* of §6.7's finding in {{e5_lead_cells}} of {{e5_total_cells}} seed-horizon cells and the *calibration* failure, {{e5_ratio_h100}}× at h = {{v2_deploy_h}}, but the pre-registered rule governing the replication returns **{{e5_verdict}}**: its second condition needs the paired difference to exclude zero at a majority of horizons, and it does at {{e5_n_excl}} of {{e5_n_horizons}}. Our arms have a held-out arena of only {{e5_nind}} independent trajectories, and the rule was written without checking what it could detect there. **So §6.7's finding is established on the released checkpoint and supported but not established on a model we trained.**

**One dataset, one gait, one terrain.** All commands are drawn from one bounded box and the gait
is a single trot throughout. "Generalisation" here means across velocity commands, not across
gaits or terrain.

**The per-horizon recalibration is fitted and tested on two episodes only.** §6.8's remedy puts every released-checkpoint estimate within the band across the two held-out episodes in both directions, though at this n no single cell is resolvable, and those cells are unseen by the multiplier only, because the checkpoint trained on both episodes. On Arm A, whose model never saw them, the same recipe manages {{d3x_own_epi_ok}} of {{d3x_own_epi_cells}} epistemic and {{d3x_own_ale_ok}} of {{d3x_own_ale_cells}} aleatoric cells, and two episodes is not a demonstration that the multipliers transfer to a new robot, gait or terrain. Treat the lookup table as a recipe to refit, not as constants to copy.

**Two secondary analyses rest on a single training seed**, the long-horizon trend fit and the per-dimension matched comparison, both on seed 1 alone, as their artifacts record. The headline A/B verdict rests on one seed too, seed {{m23_seed}}, the one its rule ran on; the magnitudes
beside it are three-seed means with per-seed values (§5).

**The ranking claim is not established as needing an ensemble.** Under a rule committed before the
comparison (rule M-51, Appendix E), the model's own predicted state change, a subtraction needing no
ensemble, ranks error at {{e7_step_r}} against disagreement's {{e7_r_dis}}, and the margin is
smaller than this sample can resolve (§6.7). Disagreement retains {{e7_step_partial}} with that
baseline partialled out, so what is open is whether its increment is worth five models. **If the observed margin is the true one, settling it needs {{q2_n_req}} independent 400-step
trajectories, where all ten episodes provide {{e7_nind}}**, {{q2_factor}}× the present sample, by
the rule's own construction applied to the step-size margin's standard error
(`results/q2_free_baseline_power.json`). That is a required-sample-size estimate under an assumed
effect: it takes the true margin to be the observed {{e7_step_margin}} and new trajectories to vary
as these do, and if the true margin is smaller the requirement rises as its inverse square, to
{{q2_sens_n}} at {{q2_sens_margin}}. The margin is the only test left to pass, since the partial
already clears its threshold, {{e7_step_partial}} against {{e7_mde_partial}}. And it is closer to
resolving than §6.7's threshold of {{e7_mde_margin}} suggests: the rule had to fix that threshold
before this baseline existed, from the forecast-index margin, whose standard error is
{{q2_se_ratio}}× the step-size margin's. The observed margin is {{q2_pct_own}}% of what its own
statistic resolves at this sample and {{q2_pct_m51}}% of what the rule's threshold demands, and
re-run exactly as pre-registered that protocol would need {{q2_n_req_m51}} trajectories. §6.7's
verdict stands on either reading, because the margin is below both.

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

**The per-dimension ordering tests are underpowered at every sample size we can reach.** Once the coupling between state dimensions is respected (§6.6), the out-of-sample arena's {{perm_oos_nind}} independent trajectories cannot reject at any effect size, and the larger arenas can and do not: over all ten episodes the smallest P in the family is {{perm_all_holm_min_p}} against a threshold of {{perm_all_holm_thr}}. Resolving it at h = {{v2_diag_h}} needs more episodes than the released dataset contains, not a better test. At h = 128 and below that is no longer true: a shorter unit gives {{m64_oos_n_h100}} independent units at h = {{v2_deploy_h}} where the 400-step unit gives {{perm_oos_nind}} (§6.6), and we did not rerun this permutation family there. This limits the *per-dimension* evidence only; the aggregate scalar the method applies is one test rather than forty-five coupled ones, and more strongly supported (§6.7).

**No family-wide correction is applied across our own pre-registered rules.** There are {{appG_n_rules}} of them with per-rule verdicts (Appendix E), each reported against the thresholds it was committed with. Pre-registration is what licenses that: each rule is a separate question committed before its data, not one search over many outcomes, and a rule that fails is reported as failing. A reader who prefers a corrected family threshold can apply it from that count.

**The independent-ensemble comparison bounds the trunk-sharing effect rather than isolating it.** §6.10's contrast trains five models at five seeds and scores them together. Independently seeded runs differ in **both** initialisation *and* data ordering, whereas the shared-trunk heads differ only in head initialisation. They also differ in **capacity**: the independent arm carries {{v1_cap_indep}} state-pathway parameters against the shared-trunk arm's {{v1_cap_shared}}, a factor of {{v1_cap_ratio}}, because each member brings its own trunk, and greater capacity can inflate σ as well as shrink error. **Capacity is controlled separately.** Rule M-49 (Appendix E), committed with its minimum detectable effect before any of its models existed, trains {{r2_n_indep}} independent members at `rnn_hidden_size` {{m49_width}} against the released {{released_width}}, giving {{m49_matched_params}} state-pathway parameters against the shared-trunk arm's {{v1_cap_shared}}, a ratio of {{m49_matched_ratio}} where §6.10's contrast carried {{v1_cap_ratio}}. **With capacity held fixed the independent ensemble is still better calibrated on every shared-trunk seed, every paired interval still excludes zero, and the coverage gain of {{m49_cov_gain}} points still clears its own MDE.** The effect does not vanish when the confound is removed.

**It does shrink, and by more than this design can resolve.** The overconfidence improvement falls from {{m44_ratio_gain}}× unmatched to **{{m49_ratio_gain}}× matched**, against an MDE of {{m49_mde_ratio}}×, so the rule returns **{{m49_verdict_short}}**: {{m49_n_conditions_met}} of its {{m49_n_conditions}} conditions hold, and the ratio threshold is the one that does not. That is the third branch the rule names, and it names it because its MDE was almost exactly the size of the effect it re-tested, as §6.10 said before the runs. So trunk-sharing is **not** explained away by capacity: the effect points the same way on every pair, with every interval excluding zero. Whether capacity accounts for *any* of it this design does not answer: the point estimates fall by about {{m49_shrink}}, a difference no artifact here tests and far below the {{m49_mde_ratio}}× this comparison can resolve, and closing it needs more independent trajectories than the dataset contains. The comparison still conflates trunk-sharing with data-order diversity, which the rule does not address. That asymmetry is generous to the mechanism: had the factor barely moved despite the handicap, architecture would not be the explanation; since it moved, the design flaw is identified but not attributed to trunk-sharing alone. Isolating it would need an ensemble that shares data ordering and not parameters, a different experiment, as rule M-44 states in its own text.

**§6.4's mechanism is a structural fact plus a hypothesis.** That the five members share a trunk, a hidden state and {{v1_shared_pct}}% of each member's parameters is measured; that this *causes* the epistemic miscalibration is the hypothesis, and only §6.10 bears on it.

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

## 12. Conclusion

The Robotic World Model's central training claim reproduces at long horizons, and the margin is
large there, though teacher forcing leads at one step. Its
architecture claim also holds against baselines we built, while its chosen history and forecast
lengths are beaten at our budget (§5.2, §5.3). Neither
uncertainty output of the follow-up that adds them reports what a reader would take it to report.
At h = {{v2_deploy_h}}, the horizon the method's own imagination rollouts run to, the aleatoric σ is {{d1n_alea_ratio_h100}}× smaller than its own error, because the objective's optimum is σ = 0 and the term that should prevent this cancels out of the gradient. The epistemic term the method actually penalises with is better by a factor of {{d1n_epi_over_alea_h100}} and still {{d1n_epi_ratio_h100}}× [{{d1n_epi_ratio_ci_h100}}] overconfident where it is used, both figures at h = {{v2_deploy_h}}.

The more useful finding is asymmetric, and it cuts both ways. The scale failure is established and large. The scale may be repairable per horizon, but on a model that has not seen the test episodes the evidence is mixed. On the released checkpoint a per-horizon multiplier, fitted on one episode and scored on another, brings every coverage estimate within {{d3_tol}} points of nominal, though no single cell is resolvable at this arena and the cells are not independent trials (§6.8), where a global multiplier manages {{d3_epi_const_ok}} of them. On Arm A, whose model never saw those episodes, its own multipliers manage {{d3x_own_epi_ok}} of {{d3x_own_epi_cells}} epistemic cells. And the ranking use the follow-up claims does survive a real test: against the forecast step index, a free baseline neither original paper ran, ensemble disagreement wins at every horizon and keeps {{d2b_par_all}} once the index is partialled out. Against a second free baseline it does less well: the model's own predicted step size ranks error at {{e7_step_r}} against disagreement's {{e7_r_dis}}, a margin this sample cannot resolve, so the verdict is {{e7_verdict}}. **The control this rests on removes trajectory difficulty rather than forecast depth**: with both the rollout and the depth held constant, disagreement still correlates {{a2_rdd}} {{a2_rdd_ci}} with realised error (§6.7). That is smaller than the {{a2_r_pooled}} pooled figure, and it is the one that means what a practitioner needs it to mean: not a re-encoding of the clock, and not merely a report of which episode is hard. It is the closest either original work comes to a claim this reproduction strengthens rather than qualifies, and even there the strengthening is of the ordering, not of the ensemble that produces it, since a free subtraction ranks nearly as well.

What does not survive is the per-dimension form of the ordering evidence. Three of the five σ estimates we measured order their own errors better than chance in direction: the epistemic term on every one of the {{perm_all_epi_ndim_h368}} dimensions at h={{v2_diag_h}}, and the faithful and teacher-forced arms. That count is a direction, not a tally of independent trials, since the dimensions are physically coupled (§6.6). The released checkpoint's *aleatoric* head does the opposite, ranking error inversely at h = {{v2_diag_h}} on every one of {{perm_all_relale_ndim_h368}} dimensions over all ten episodes and at chance on the held-out pair alone, a dependence on arena that §6.6 sets out. The corrected arm sits at chance in both. Once the coupling is respected by permuting whole trajectories, no per-dimension count in this paper reaches significance after multiplicity correction; the independent-trials P-values an earlier draft carried were wrong by up to a factor of about {{perm_worst_factor}} and are withdrawn (`S-15`). Neither quantity yields a usable interval. Per dimension, uncertainty in this family of models should be read as a weak ordering at best, or fixed at the objective. As the scalar the method applies, ensemble disagreement gets the order right (§6.7) and the size wrong: it should not be read as a scale, and a ranking use deserves its own validation on the deployment distribution rather than trust inherited from here.

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
trajectories and all ten episodes hold {{d1n_nind}}, which is why §11 leaves the replication at
ensemble size 5, the free-baseline margin and capacity's share of the trunk-sharing effect open
rather than settled. §5.2's configuration verdict should not travel either: it is
resolved, but at our data budget, and says nothing about the original's.

---

## Data and code

The full repository — code, every artifact under `results/`, and `FINDINGS_LEDGER.md` with the
complete claim record including the retractions — accompanies this submission as anonymised
supplementary material, and will be released under a permanent archival identifier on
acceptance. Neither upstream repository is redistributed; `setup.sh` fetches both at pinned
commits and verifies two SHA-256 hashes.

**The repository's history was rewritten once, and §8 depends on that history, so we say
what changed.** A supplementary file quoting private correspondence was committed and
briefly published before consent to quote it had been given; it was purged from the history
rather than merely deleted, because a deletion commit leaves the content recoverable from a
public repository indefinitely. Purging a path rewrites every commit from the one that
introduced it onward, so **{{f4_n_commits}} of the commits Figure 1 cites keep their
identifiers and two do not** — the two whose data post-dates that file. Timestamps, content
and ordering are unchanged; only the hashes moved, and Figure 1 resolves each rule by its
commit subject for that reason. The transcript itself reaches reviewers in the anonymised
supplementary archive, which is not published.

The pre-registration argument in §8 rests on commit timestamps, and those are
author-settable via `git commit --date`. That matters, because §8 is load-bearing. Two
things address it. The
supplementary material includes an anonymised `git log` covering every commit cited here, so the
ordering in Figure 1 is checkable at review time. In the submitted paper and bundle, commit identifiers are replaced by stable
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

**On anonymity, stated rather than implied.** The code and data for this work are public, as they
are for most reproducibility work, and a reviewer who chooses to look can identify the author.
The submission is anonymised — the bundle is scrubbed and asserted clean of a deny-list, and the
files that carry identity are excluded from it — but that is anonymity of the *submission*, not
unfindability of the work. Making the repository private would remove the identifying link and
also remove the checkability §8 depends on, which is the worse trade. The decision and its
reasoning are recorded in `docs/DOUBLE_BLIND_DECISION.md`.

## References

1. C. Li, A. Krause, M. Hutter. *Robotic World Model: A Neural Network Simulator for Robust Policy
   Optimization in Robotics.* arXiv:2501.10100**v1**, 17 January 2025.
   *Read at v1, whose Roman-numeral sectioning our references follow; v2 (23 April 2025)
   renumbered to Arabic and moved IV-C into Appendix A.4.1.*
2. C. Li, A. Krause, M. Hutter. *Uncertainty-Aware Robotic World Model Makes Offline Model-Based
   Reinforcement Learning Work on Real Robots.* arXiv:2504.16680**v1**, 23 April 2025.
   *Read at v1; now at {{v4_current}}, last revised {{v4_current_date}}. §5.1 and Eq. 4–5
keep their numbers there; every figure and appendix table has moved, and the model is
renamed {{v4_name_v1}} to {{v4_name_v3}} — the same model, with the letter re-expanded from
"{{v4_exp_v1}}" to "{{v4_exp_v3}}". The two names never co-occur: v1 uses
{{v4_name_v1}} {{v4_name_n_v1}} times and no {{v4_name_v3}}, v3 the reverse. The crosswalk
is in `results/original_paper_figures.json`.*
{{t1_reference_list}}

*Entries {{t1_first_entry_n}}–{{t1_last_entry_n}} are the bibliography of §2 and §5.3, generated from
`results/t1_bibliography_verified.json` rather than listed here — a hand-maintained list of what a
paper cites drifts exactly as a hand-typed count does, and this one had: six entries cited in §2's
prose appeared in no reference entry while the note below claimed all of them verified. Each was checked against the paper itself: title and full author list from the arXiv record, venue from the record or the paper's first page, and for any sentence this paper attributes, the sentence matched verbatim against that paper's own text — {{t1_n_verified}} of {{t1_n_refs}} entries and {{t1_n_frag_ok}} of {{t1_n_frag}} attributed fragments,
{{t1_n_frag_oneword}} of them single common words whose presence the cited paper's subject guarantees,
so their match could not have failed and verifies nothing about the attribution
(`results/t1_bibliography_verified.json`, ledger `D-35`).*

## Appendix A — verification chain

What every downstream number rests on. Each level was passed before the next was attempted.

| level | claim | result |
|---|---|---|
| shapes | parameter counts match the reference | exact |
| wiring | inference outputs match the reference module | **{{wiring_max_diff}}**, bitwise |
| indexing | the harness feeds the actions it claims | bitwise against the raw CSV |
| residual | the zero-delta model is the hold-last floor | {{zero_delta_resid}} |
| **objective** | **losses and gradients match** | **{{diff_grad_max}} across {{diff_terms}} terms, {{diff_n_params}} tensors** |
| trainer | can memorise a single batch | {{overfit_reduction}}× loss reduction |

## Appendix B — reproducing

    ./setup.sh                     # clone upstreams at pinned commits
    python3.11 -m venv .venv && . .venv/bin/activate
    pip install -r requirements.txt
    ./reproduce.sh --quick --force # everything except training

`--force` matters: a clean clone already contains each stage's declared output, so without it every stage skips.

**Runtime.** Training stages are excluded by `--quick`, which is what makes the quick path practical. Training all {{rt_runs}} runs takes **{{rt_hours}} hours** of recorded wall clock on two CPU cores: {{rt_hours_10k}} hours for the {{rt_runs_10k}} runs at 10,000 iterations and {{rt_hours_short}} for the remaining {{rt_runs_short}} at 2,500. The longest single run is {{rt_longest}} hours. Every figure here is read from the `wall_clock_s` field of the run artifacts rather than estimated.

**{{rt_runs_m49}} of those {{rt_runs}} runs, {{rt_hours_m49}} hours, are `M-49`'s capacity-matched
arm at `rnn_hidden_size` {{m49_width}}** rather than the released {{released_width}}. They are part
of this project's CPU spend and are counted in the total above — the other {{rt_hours_released}}
hours are the {{n_runs}} runs at the released width, and the two parts are asserted to make the
total rather than stated beside it. They are **not** part of the
{{n_runs}} runs §6.3 fits the σ-collapse rate over, because that rate is a property of one
architecture and mixing widths into it would make "nearly identical across runs" a claim about two
different models. Every run artifact records the width it trained at, and `paper_numbers.py`
selects the collapse family by that field rather than by filename; `docs/BUILD_CHECKS.md`, shipped as supplementary, records how that selection came to be made.

**The pre-submission runs are counted separately.** §5.2's sweep and §5.3's baselines added
{{rt_pre_runs}} runs and **{{rt_pre_hours}} hours**: {{rt_sweep_runs}} sweep runs ({{rt_sweep_hours}} h),
then {{rt_bl_tf_runs}} teacher-forced and {{rt_bl_ar_runs}} autoregressive baseline runs
({{rt_bl_tf_hours}} h and {{rt_bl_ar_hours}} h), read from `results/presubmission_runtime.json`. They
are outside the total above, whose remainder that paragraph describes as released-width runs, which
the baselines are not. Of these, {{rt_pre_overlapped}} overlapped other CPU work a session logged,
which inflates their wall clock and changes no weight; the artifact lists each overlap. Per run family,
every run at {{iters_main}} iterations (the sweep's centre is §5's Arm A, whose runs are counted above):

| run family | runs | hours per run, mean | runs that overlapped other CPU work |
|---|---|---|---|
{{rt_pre_table}}

## Appendix C — what testing the untested claims would require

Appendix D's table marks {{orig_n_tested}} claims tested and the rest not. "Not tested" is an apology
unless it comes with a price, so here is what each would cost. We give compute orders where we
can estimate them honestly from this project's own measurements and say so where we cannot.

**Every row needs what this reproduction did not have: interaction.** Our arms train on the released CSV, which is a recording. Those claims need a
policy acting in an environment, simulated or real, and the environment responding. In
simulation that means Isaac Lab, which needs an RTX-class NVIDIA GPU, and no amount of CPU
substitutes: the reference's data generation is GPU-parallel simulation, not a data-loading
problem. For the hardware-transfer and real-robot rows the binding constraint is a robot rather
than compute. **A GPU would not be enough on its own.** The code that generates data is in
neither repository this reproduction pins: the lite release only reads its dataset, and its
readme places collection in a third repository, the authors' Isaac Lab extension, which this reproduction does not pin (§3, ledger `D-36`).

| untested claim | what it needs | order |
|---|---|---|
| Sample efficiency, {{c2_ref}} against ~250M transitions (§IV-E) | Isaac Lab, an RTX-class GPU, the MBPO-PPO loop, and a PPO baseline run to convergence for the comparison | the reference reports {{c2_ref}} pretraining transitions and 50 min of RWM training on their hardware; the PPO baseline's 250M is the dominant cost |
| MBPO-PPO beats SHAC and Dreamer (§IV-E) | the above, plus SHAC and Dreamer implementations at matched budgets | three policy-learning stacks, each tuned enough that the comparison is fair — the largest engineering item here |
| Zero-shot hardware transfer (§IV-E) | all of the above, plus an ANYmal, a safe test area, and the sim-to-real stack | not estimable in compute; the binding constraint is hardware access, not GPU hours |
| Generality across quadruped, humanoid, manipulation (§IV-D) | recorded state-action data from a humanoid and a manipulator, which means Isaac Lab and a policy in each environment to generate it — the released CSV is one robot on one terrain | one data-generation run per morphology, plus one world-model training run each at our {{rt_hours}} h scale; the model training is the cheap half and the data is not |
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

## Appendix D — every claim of the originals, and what we did with it

The body's §4 summarises this table. It is here in full because the third column — what the
original actually reports — is the answer to a question a reader of any reproduction should ask,
and because "no quantitative figure" is itself a finding that deserves to be checkable row by row.

*Section references follow arXiv:2501.10100**v1**, which uses Roman-numeral sectioning. v2
renumbered to Arabic and moved IV-C's material into Appendix A.4.1. References to
arXiv:2504.16680 follow **v1**, which is the version we read; it is now at
{{v4_current}} ({{v4_current_date}}), where §5.1 and Eq. 4–5 keep their numbers but every figure
and appendix table has moved — {{v2_fig_v1}} became {{v2_fig_v3}}, and the model was renamed {{v4_name_v1}} to
{{v4_name_v3}}, which is a re-expansion of the letter ("{{v4_exp_v1}}" to
"{{v4_exp_v3}}") rather than a second variant: no version of the paper contains both
names. All locations, and the occurrence counts that establish that, are recorded in
`results/original_paper_figures.json`.*

| claim, and where | tested | what the original reports | verdict |
|---|---|---|---|
| RWM-AR consistently outperforms RWM-TF (2501.10100 §IV-D) | **yes** | **no quantitative figure.** "significantly outperforms"; the gap is plotted in Fig. 7 and stated nowhere in text, caption or table | **reproduces** at long horizon (§5) |
| Teacher forcing gives "poor autoregressive performance" (§IV-C) | **yes** | **quantitative**: Fig. 6 prints e for the teacher-forced N=1 row, {{orig_tf_e_n1}} at {{mn_n1_label}} against {{orig_tf_e_centre}} at the centre, on unstated data and horizon; the passage itself gives no number | reproduces, and more strongly: Arm B is worse than the hold-last floor, and §5.2's {{mn_n1_label}} is {{mn_tf_ratio}}× the centre's error at h = {{v2_diag_h}} |
| M=32, N=8 gives the optimal trade-off between accuracy and training time (§IV-C) | **yes** | **quantitative**: Fig. 6 prints the error and the training hours of every cell of its grid, and the centre's error is the tied-lowest (`docs/presubmission/ORIGINAL_SPECS.md` a.5) | **{{mn_verdict}}** on the accuracy half (§5.2): {{mn_better_list}} beat it at our budget, the best of them even when the centre trains longer (post hoc). The trade-off with training time is not tested |
| Beats MLP, RSSM and transformer baselines (§IV-D) | **yes** | **no quantitative figure.** "consistently achieves the lowest prediction errors across all environments"; plotted in Fig. 7, with no number in text, caption or table | **{{bl_tf_verdict}}** with the baselines teacher-forced, as the original trains them, and **{{bl_ar_verdict}}** with them trained autoregressively, which compares architectures at one training regime rather than testing this claim (§5.3). The baselines are built to our reading of Table S7 and trained with RWM's settings; at h = {{v2_diag_h}} every one is worse than predicting no change, and the RSSM comparison is uninformative (rule X1), so the claim rests on the MLP and the transformer. One robot where the original has several |
| Zero-shot hardware transfer (§IV-E) | no | — | `[hardware: zero-shot transfer]` no hardware; this is a dynamics-model reproduction |
| Policies transfer to hardware from ~6M state transitions against ~250M for the model-free baseline (§IV-E) — the paper's headline sample-efficiency result | no | **{{orig_se_rwm}} against {{orig_se_ppo}} state transitions** at equal real tracking reward ({{orig_se_rwm_rew}} against {{orig_se_ppo_rew}}), Table I — the only table of numbers in either paper | `[policy, hardware: the sample-efficiency result]` **not tested.** It is a claim about policy learning and hardware deployment, and requires the RL loop, a simulator and an ANYmal. We reproduce the dynamics model only; no policy is trained anywhere in this work, so no transition count of ours is comparable |
| MBPO-PPO beats SHAC and Dreamer (§IV-E) | no | — | `[policy: the comparisons against SHAC and Dreamer]` no policy learning reproduced |
| Generality across quadruped, humanoid, manipulation (§IV-D) | no | plotted in Fig. 7; no numbers in text | `[model: generality across robot morphologies]` one released dataset, ANYmal D flat |
| Epistemic "closely follows the trend of the prediction error", justifying "its role as a trust metric" (2504.16680v1 §5.1) | **yes** | **no quantitative figure.** A "strong correlation" is asserted with no coefficient, interval or sample size; plotted in Fig. 2 (right) | **supported as a scalar ranking, against a real baseline** — the applied scalar correlates {{d4_r}} {{d4_ci}} with realised error at n_independent = {{d4_nind}}, beats the forecast-index counter at every horizon — though **not** the free `step-size` counter, {{e7_step_r}} against {{e7_r_dis}}, a margin below the {{e7_mde_margin}} minimum detectable effect ({{e7_verdict}}) — and survives {{d2r_ncontrols}} controls on forecast depth — the linear partial that keeps {{d2b_par_all}}, and four harder ones — plus a sixth on trajectory difficulty — the last giving {{a2_rdd}} {{a2_rdd_ci}} with both the rollout and the depth held constant (§6.7, M-45). **Weaker per-dimension**: at h = {{v2_diag_h}} the {{d1n_epi_npos_h368}}-of-{{d1n_epi_ndim_h368}} sign count gives a permutation P of {{perm_oos_epi_p_h368}} (out-of-sample) and {{perm_ins_epi_p_h368}} (in-sample), and no cell survives multiplicity correction (§6.6). **Not supported as a scale**: {{d1n_epi_ratio_h100}}× overconfident at h = {{v2_deploy_h}}, the method's own rollout length, and {{d1n_epi_ratio_h368}}× at the h = {{v2_diag_h}} diagnostic horizon; a per-horizon rescaling brings the released checkpoint near nominal, but on a model that has not seen the test episodes it does so in only {{d3x_own_epi_ok}} of {{d3x_own_epi_cells}} cells (§6.8) |
| Aleatoric "remains low, reflecting small stochasticity" (2504.16680v1 §5.1) | **yes** | **no quantitative figure.** "Low" is relative to the epistemic curve on the same axes of Fig. 2 (right); no absolute value, and no comparison against realised error | the observation holds; the explanation does not (§6.3) |
| Offline MBRL on real robots (2504.16680v1) | no | — | `[policy, hardware: offline MBRL on real robots]` not tested |
| Penalising rewards by ensemble disagreement improves the learned policy (2504.16680v1 Eq. 4–5, §5) — the follow-up's core method claim | no | Fig. 3 (right) plots epistemic uncertainty under three penalty weights during training; no numbers | `[policy: the core claim that penalising rewards by disagreement improves the learned policy]` **not tested.** We measure the penalty quantity itself — what it is (§6.1), how well it ranks error (§6.7), whether it is calibrated (§6.2) — but never train a policy with or without it. Our findings bound what the quantity *reports*, not what it *costs* (§11) |

---
## Appendix E — every pre-registered rule, its lead time and its verdict

§8's argument rests on decision rules committed to git before the data that tested them, and the
body names those rules by identifier. An identifier with no table behind it is either decoration
or an instruction to open a {{ledger_kb}} KB ledger, so here is the table. It is generated from
`FINDINGS_LEDGER.md` and `results/appendix_g_rules.json`; nothing in it is typed.

**Lead time** is the rule's commit timestamp subtracted from the commit that first held the data
it tested, resolved by commit *subject* rather than by hash — the history was rewritten once and
hashes did not survive it, while subjects did. Positive means the rule was in git before the data
existed. This is the same computation Figure 1 plots.

| rule | what it governs | commit | lead time | tested by | verdict |
|---|---|---|---|---|---|
{{appG_table}}

`M-69`'s discharge commit was amended {{m69_amend_min}} minutes after it was created, so the
rule's lead time depends on which timestamp is read: {{m69_lead_author}} by that commit's author
time, {{m69_lead_regen}} by its committer time. The table above renders {{m69_lead_pub}}, the value
`results/appendix_g_rules.json` holds; a clean rebuild regenerates that file from git and may
store either reading. Both readings are
positive, so the rule reached git before the data that tested it existed on either one, which is
what a lead time is here to establish.

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

## Appendix F — the variance-state arithmetic behind §7.5

§7.5 states the conclusion. The arithmetic and the five assumptions it rests on are in
`docs/APPENDIX_G_VARIANCE_ARITHMETIC.md`, shipped as supplementary, kept out of the body because the numbered
claim it once supported is retracted (`S-19`) and because a forensic case the section then defuses
with the author's own reply is not what a reader needs in the body of a reproduction.

So the finding is not that the release is internally inconsistent. It is that **the released
artifacts do not reproduce the released checkpoint's variance state, and the author's account is
that the released repository is not the one that trained it.** That is a documentation gap between
a release and a run — common, worth recording, and much less interesting than an inconsistency.
We report the arithmetic because it is what let us detect the gap at all, not as a charge against
the work.

---

---

## Appendix G — the two nRMSE aggregations, and the comparison one of them inverted

§3.1 states that this paper uses **form 1**: pool the per-dimension mean squared errors across the
{{cal_rel_ndim}} state dimensions, then divide by the pooled scale — a ratio of means. **Form 2**
is the mean of per-dimension ratios.

The two differ because the state dimensions differ widely in scale. Form 2 gives
whichever dimension has the smallest denominator unbounded leverage over the aggregate, and a
dimension that is nearly constant in the training episodes has a very small denominator. Form 1
has no such lever: a dimension contributes in proportion to its share of the total squared error.

**Why this appendix exists rather than a sentence.** The choice between the two once inverted a
published-model comparison in this project's own history — a result that favoured us under one
aggregation and did not under the other. The claim was withdrawn on our own evidence and is kept
in the record (`FINDINGS_LEDGER.md`). Form 2 figures appear nowhere in the body; they are retained
in `results/step4_0a_results.json` for continuity with figures this project published before the
inversion was found. This appendix gives the two definitions and the inversion rather than those figures, so continuity rests on that committed file and not on a deleted number.

The definition in force throughout the paper is the one §3.1 gives. Nothing in §5, §6 or §7 uses
form 2.

---

