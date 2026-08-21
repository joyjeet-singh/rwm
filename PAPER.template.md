# What a world model's uncertainty outputs actually report: an independent reproduction of the Robotic World Model

---

## Abstract

We independently reproduce the proprioceptive dynamics model of Li, Krause and Hutter
(*Robotic World Model*, arXiv:2501.10100) and its uncertainty-aware follow-up
(arXiv:2504.16680), building the model from scratch on CPU and verifying it against the released
reference at the level of outputs, losses and gradients before training anything.

The base paper's central claim reproduces, and by a wide margin: trained autoregressively, the
model reaches normalised error {{m23_A}} at a 368-step horizon on held-out episodes against
{{m23_B}} for teacher forcing, a factor of {{m23_ratio}}×, with a bootstrap interval of
[{{m23_ci_lo}}, {{m23_ci_hi}}] excluding zero and the gap positive on all
{{m23_n_episodes_positive}} of {{m23_n_episodes}} episodes. That verdict was fixed by a decision
rule committed to git before the runs that tested it existed.

Neither of the follow-up's uncertainty outputs survives contact with a calibration measurement.
The checkpoint emits a per-member **aleatoric** σ and an **epistemic** ensemble disagreement, and
the method penalises rewards with the second while discarding the first. We measure both. The
aleatoric σ is **{{cal_rel_ratio}}× smaller than its own mean absolute error**
({{cal_rel_cov1}}% coverage at ±1σ against a calibrated 68.3%), and we show analytically why: the
state loss is squared error on a reparameterised sample with no log-σ term, minimised at σ = 0,
with the bound term that should oppose this cancelling algebraically. Running the correction —
the authors' own unused `gaussian_nll` branch — fails differently rather than succeeding, at
{{cal_nll_ratio}}× overconfidence. The epistemic term, the one the method actually consumes, is
two orders of magnitude better and still **{{b2_epi_ratio_h368}}× overconfident at the deployment
horizon**, with {{b2_epi_cov1_h368}}% coverage.

Measuring all four models we trained or scored puts the failure precisely. The teacher-forced arm
has the most input-dependent σ ({{cal_armB_over_faithA_cov}}× the autoregressive arm's) and the
strongest σ-versus-error ordering ({{cal_armB_npos}} of {{cal_armB_ndim}} dimensions positive,
P = {{cal_armB_p}}), and is still {{cal_armB_ratio}}× overconfident. These models can learn *which*
predictions will be worse. They cannot learn *how wrong* they will be. A downstream user who needs
a ranking may be served; one who needs an interval is not, under any of the four.

We also report four defects in the released pipeline, evidence that the released checkpoint cannot
have come from the released recipe, and {{n_retractions_lower}} retractions of our own numbered claims —
one of which is the finding that one of our own pre-registrations was not, in fact, pre-registered.
Every number in this paper is generated from a file in `results/`; none is typed by hand.

---

## 1. Introduction

A world model that reports its own uncertainty is more useful than one that does not, and the
uncertainty-aware Robotic World Model reports one. This paper asks what that number means.

We came to the question sideways. Our aim was an ordinary reproduction: rebuild the proprioceptive
dynamics model from scratch, check it against the released implementation, and see whether the
paper's central training claim holds. It does. But the same rebuild made a second question cheap
to ask, because we had a from-scratch model, the released checkpoint, and a harness that could
score both: *is the predicted σ calibrated?* It is not, by three to four orders of magnitude, and
the reason is structural rather than incidental.

Three things distinguish this from a re-run of the authors' code.

**We rebuilt rather than imported.** The forward pass, the loss and the training step are written
from scratch and then checked against the reference: outputs match bitwise, and losses and
gradients match to {{diff_grad_max}} across {{diff_terms}} loss terms and
{{diff_n_params}} parameter tensors before any training begins
(Appendix A). A discrepancy found later is therefore a property of the method, not of our wiring.

**Decision rules were committed before the data.** The verdicts below were fixed in advance, in
git, with timestamps a reader can check (§7, Figure 4). One of them returned "cannot be settled"
and we report that too.

**We retract our own findings when they fail.** Four claims in this work are withdrawn on evidence
this project produced, and the retractions are kept in the record rather than deleted. One of them
concerns the pre-registration discipline itself.

---

## 2. Setup

**Data.** The released dataset is {{rows}} rows of ANYmal D proprioceptive state and policy
actions at 50 Hz. It is not one recording: it is ten concatenated 20-second episodes, and its
termination column is identically zero, so nothing in the file marks the boundaries. The reference
window builder therefore marks all {{win_naive}} windows valid, including {{win_cross}} that
splice one episode's end onto the next one's start. The usable, episode-respecting count is
{{win_usable}} — {{rows}} rows, less {{win_tail}} that cannot start a full window, less
{{win_cross}} that cross a boundary. The contamination rate is {{contam_pct}}%.

**Model.** A GRU-based ensemble predicting the next proprioceptive state, with a mean head and a
bounded log-σ head, plus auxiliary heads for contact and termination. The paper describes two loss
terms; the implementation has {{diff_terms}}.

**Evaluation.** Two arenas, held separate throughout: *out-of-sample*, the two episodes withheld
from training, and *in-sample*, the eight used for it. We report both, because the released
evaluation draws its trajectories from training data and the distinction is invisible in the
original.

**Effective sample size.** Trajectory count is not sample size. Two 400-step trajectories whose
spans overlap are not independent evidence, and the out-of-sample arena contains only
{{m23_nind}} mutually non-overlapping 400-step trajectories. Every interval in this paper is a
bootstrap over independent trajectories, and every table reports that count.

---

## 3. The base paper's central claim reproduces

**Claim under test.** Training the dynamics model on its own autoregressive rollouts beats
training it with teacher forcing, at deployment horizons.

**Rule, committed in advance** (commit `efc35b8`, and it names conditions rather than outcomes).
Three conditions, all required: the out-of-sample gap at h = 368 excludes zero
under a bootstrap over independent trajectories; the sign is consistent across episodes; and the
effect survives at 10,000 iterations rather than only at the paper's 2,500.

**Result.** Every condition {{m23_c1}}. At h = 368 out-of-sample after
10,000 iterations, autoregressive training reaches **{{m23_A}}** against teacher forcing's
**{{m23_B}}** — a factor of **{{m23_ratio}}×**, gap {{m23_gap}}, 95% bootstrap interval
[{{m23_ci_lo}}, {{m23_ci_hi}}], on n = {{m23_nind}} independent trajectories. The per-episode gap
is positive on **{{m23_n_episodes_positive}} of {{m23_n_episodes}}** episodes.

**What does not hold, and we say so.** At h = 8 — the horizon the model is trained on — the same
comparison out-of-sample gives a gap of {{m23_h8_gap}} whose interval {{m23_h8_excl}}.
The advantage is a long-horizon phenomenon. An earlier rule of ours, anchored
at h = 8, returned "cannot be settled"; anchoring a rule to the horizon the claim is actually
about was a correction we had to make in advance of the runs, not after them (§7).

The pattern is consistent across the design. Under the correct cluster bootstrap, the
out-of-sample gap excludes zero in **{{ab_long_excl}} of {{ab_long_cells}}** long-horizon cells —
both trajectory lengths crossed with both checkpoints — and in **{{ab_short_excl}} of
{{ab_short_cells}}** at h = 8. These figures are relative-L1; the nRMSE aggregation is reported
separately and does not change the direction.

---

## 4. Neither of the checkpoint's uncertainty outputs is usable as an interval

### 4.1 Which quantity the method actually uses

The released checkpoint emits **two** uncertainty quantities, and the method consumes only one of
them. This has to be settled before any calibration number means anything.

`system_dynamics.py:125` computes an **aleatoric** term, the mean over ensemble members of each
member's predicted σ. `system_dynamics.py:126` computes an **epistemic** term, the standard
deviation across the members' mean predictions. In `envs/base.py:142` the aleatoric term is bound
to a local variable that is never read again; the epistemic term is stored, returned to the policy
loop at `:158`, and applied at `:166` as a reward penalty with weight −1.0.

The paper agrees with its code. arXiv:2504.16680 Eq. 4 defines the penalised quantity as
$u = \mathrm{Var}_b[\mu_b]$, the variance across ensemble members, and Eq. 5 applies it
as $\tilde{r} = r - \lambda u$. The per-member predicted variance enters the training objective and nothing
downstream.

One discrepancy between the two, minor but real: Eq. 4 specifies a **variance**, and
`system_dynamics.py:126` computes a **standard deviation**. With $\lambda = 1$ these differ by a square.
We measure the code's quantity throughout, because that is what produced the released
checkpoint's behaviour, and we do not treat either definition as authoritative.

So the aleatoric head — the one the state loss and the bound loss shape, and the one §4.2 explains
— is computed on every imagination step and discarded. We report both quantities below. Our own
arms are ensemble size 1, where the epistemic term is identically zero by construction, so the
epistemic measurement is possible only on the released checkpoint.

### 4.2 The measurement

For each model we compute the mean predicted σ, the mean absolute realised error, and the fraction
of realised errors falling inside ±1σ. A calibrated Gaussian puts 68.3% inside ±1σ.

| model | mean \|error\| / mean σ | coverage at ±1σ, h=1 | coverage at h=368 |
|---|---|---|---|
| faithful Arm A (sampled MSE) | {{cal_faithA_ratio}}× | {{cal_faithA_cov1}}% | {{cal_faithA_cov368}}% |
| corrected Arm A (`gaussian_nll`) | {{cal_nll_ratio}}× | {{cal_nll_cov1}}% | {{cal_nll_cov368}}% |
| teacher-forced Arm B | {{cal_armB_ratio}}× | {{cal_armB_cov1}}% | {{cal_armB_cov368}}% |
| released checkpoint | {{cal_rel_ratio}}× | {{cal_rel_cov1}}% | {{cal_rel_cov368}}% |

Every model is overconfident by between one and four orders of magnitude (Figure 1). Those are
aleatoric figures — the quantity §4.1 shows the method discards.

**The quantity the method does use is also uncalibrated.** On the released
{{b2_members}}-member checkpoint, out-of-sample, n = {{b2_nind}} independent trajectories:

| h | aleatoric err/σ | epistemic err/σ | epistemic ±1σ | epistemic ±2σ | dims r>0 | P |
|---|---|---|---|---|---|---|
| 1 | {{b2_alea_ratio_h1}}× | **{{b2_epi_ratio_h1}}×** | {{b2_epi_cov1_h1}}% | {{b2_epi_cov2_h1}}% | {{b2_epi_npos_h1}}/{{b2_epi_ndim_h1}} | {{b2_epi_p_h1}} |
| 8 | {{b2_alea_ratio_h8}}× | {{b2_epi_ratio_h8}}× | {{b2_epi_cov1_h8}}% | {{b2_epi_cov2_h8}}% | {{b2_epi_npos_h8}}/{{b2_epi_ndim_h8}} | {{b2_epi_p_h8}} |
| 32 | {{b2_alea_ratio_h32}}× | {{b2_epi_ratio_h32}}× | {{b2_epi_cov1_h32}}% | {{b2_epi_cov2_h32}}% | {{b2_epi_npos_h32}}/{{b2_epi_ndim_h32}} | {{b2_epi_p_h32}} |
| 128 | {{b2_alea_ratio_h128}}× | {{b2_epi_ratio_h128}}× | {{b2_epi_cov1_h128}}% | {{b2_epi_cov2_h128}}% | {{b2_epi_npos_h128}}/{{b2_epi_ndim_h128}} | {{b2_epi_p_h128}} |
| 368 | {{b2_alea_ratio_h368}}× | **{{b2_epi_ratio_h368}}×** | {{b2_epi_cov1_h368}}% | {{b2_epi_cov2_h368}}% | {{b2_epi_npos_h368}}/{{b2_epi_ndim_h368}} | {{b2_epi_p_h368}} |

Epistemic is two orders of magnitude better than aleatoric — {{b2_epi_over_alea_h1}}× larger at
h=1, {{b2_epi_over_alea_h368}}× at h=368 — and still wrong by
**{{b2_epi_ratio_h1}}×** at one step and **{{b2_epi_ratio_h368}}×** at the deployment horizon,
with ±1σ coverage of {{b2_epi_cov1_h368}}% where a calibrated Gaussian gives 68.3%. **Total**
uncertainty, `sqrt(aleatoric² + epistemic²)`, equals the epistemic value to four significant
figures at every horizon, because the aleatoric term is too small to move it.

The scalar penalty as actually applied — `means.std(0).sum(-1)` at `envs/base.py:166` —
correlates {{b2_penalty_corr}} with total absolute error over the rollout.

### 4.3 Why the aleatoric head collapses: the optimum is σ = 0

This subsection explains the aleatoric column and only that column. Ensemble disagreement is not
shaped by the mechanism below, and why *it* is miscalibrated is not established here.

The state loss is squared error on a *sample* drawn from the predicted Gaussian, not a likelihood:

$$\mathcal{L} \;=\; \mathbb{E}\big[(\mu + \sigma\varepsilon - y)^2\big] \;=\; (\mu - y)^2 + \sigma^2$$

which is minimised at σ = 0 for any μ. There is no log-σ term to oppose it. The bound term that
appears to oppose it does not, because `max_logstd` is not an independent parameter — it is
constructed as `min_logstd + exp(log_delta_logstd)`, so

$$\overline{\log\sigma_{\max}} - \overline{\log\sigma_{\min}} \;=\; \overline{\exp(\log\Delta_{\log\sigma})}$$

and `min_logstd` cancels algebraically, taking no gradient from that term. The floor the interval
closes onto therefore freezes while the interval closes: a one-way ratchet.

We predicted the collapse from this algebra before training, then observed it. Across all
{{n_runs}} runs the collapse is linear in iteration count and its rate is nearly identical
(Figure 3a). Under the corrected objective the sign flips (Figure 3b) — which is the strongest
evidence that the mechanism is the objective and not the optimiser, the data or the architecture.

### 4.4 The correction fails differently rather than succeeding

The reference contains an unused `gaussian_nll` branch. Running it reverses the collapse and
improves the magnitude from {{cal_faithA_ratio}}× to {{cal_nll_ratio}}× overconfident. It does not
produce a usable estimate, and it destroys something the faithful arm had: the σ-versus-error
ordering falls from {{cal_faithA_npos}}/{{cal_faithA_ndim}} dimensions positively correlated
(P = {{cal_faithA_p}}) to {{cal_nll_npos}}/{{cal_nll_ndim}} (P = {{cal_nll_p}}, chance).

### 4.5 The failure is one of magnitude, not of ordering

Measuring the teacher-forced arm — which we had trained for §3, and which our own first three
calibration tables omitted — sharpens the finding:

| model | σ variation across inputs (CoV) | dims with r(σ, error) > 0 | P |
|---|---|---|---|
| faithful Arm A | {{cal_faithA_cov}} | {{cal_faithA_npos}}/{{cal_faithA_ndim}} | {{cal_faithA_p}} |
| corrected Arm A | {{cal_nll_cov}} | {{cal_nll_npos}}/{{cal_nll_ndim}} | {{cal_nll_p}} |
| **teacher-forced Arm B** | **{{cal_armB_cov}}** | **{{cal_armB_npos}}/{{cal_armB_ndim}}** | **{{cal_armB_p}}** |
| released checkpoint | {{cal_rel_cov}} | {{cal_rel_npos}}/{{cal_rel_ndim}} | {{cal_rel_p}} |

Arm B's σ is {{cal_armB_over_faithA_cov}}× more input-dependent than the faithful arm's, and its
ordering is the strongest of the four by a wide margin (mean r = {{cal_armB_r}}). It is still
{{cal_armB_ratio}}× overconfident.

So σ collapsing to a constant is a property of the *autoregressive* arms and the released
checkpoint, not of the objective in general — and input-dependence and correct ranking are both
achievable without the interval becoming meaningful.

**The same pattern holds for the quantity the method uses, with the strongest evidence in this
paper.** At h=128 and h=368 the epistemic term correlates positively with realised error on
**{{b2_epi_npos_h368}} of {{b2_epi_ndim_h368}}** dimensions, P = {{b2_epi_p_h368}} — a better
ranking than any aleatoric head here — while being {{b2_epi_ratio_h368}}× overconfident. And it
fails the horizon test the same way: σ grows {{b2_epi_sigma_growth}}× from h=1 to h=368 while
error grows {{b2_epi_err_growth}}×.

**The failure is specifically magnitude calibration, in both components.**

### 4.6 The structural excuse does not survive

One could argue that a model trained on an 8-step horizon cannot be expected to report calibrated
uncertainty about step 368. It cannot report it about step 8 either. Inside the trained horizon,
σ is flat while error grows (Figure 2):

| model | σ growth, step 1 → 8 | error growth, step 1 → 8 |
|---|---|---|
| faithful Arm A | {{sig_faithA_growth}}× | {{err_faithA_growth}}× |
| corrected Arm A | {{sig_nll_growth}}× | {{err_nll_growth}}× |
| teacher-forced Arm B | {{sig_armB_growth}}× | {{err_armB_growth}}× |
| released checkpoint | {{sig_rel_growth}}× | {{err_rel_growth}}× |

The faithful arm's σ *declines* ({{sig_faithA_growth}}×) while its error grows
{{err_faithA_growth}}×. The coverage collapse in Figure 1(b) is therefore driven entirely by
growing error against a fixed σ.

---

## 5. Defects in the released pipeline

**5.1 Ten unmarked episode boundaries.** §2. The window builder reads a termination column that is
identically zero, so it marks all {{win_naive}} windows valid.

**5.2 Training and evaluation disagree on action alignment, and evaluation is the broken one.**
Row *t* holds the action that *produced* state *t*. The training path pairs states and actions
index-for-index, which is causally correct. The evaluation path feeds the action from *t−1* to
predict state *t* — stale by one step. Scored correctly the released checkpoint is materially
better than its own released evaluation reports.

**5.3 No held-out evaluation.** Evaluation trajectories are drawn from training data. For the
released checkpoint, trained on the entire file, no held-out measurement is possible at all.

**5.4 What the spliced windows cost: nothing measurable.** We trained a contaminated arm on
{{arm_contam_windows}} windows — the clean {{arm_clean_windows}} plus {{arm_splices}} splices — and,
because that confounds *content* with *count*, a duplication control adding the same
{{arm_splices}} windows as exact copies of windows already present.

The arm's contamination rate is {{arm_contam_pct}}%, against the reference pipeline's
{{contam_pct}}%. It is deliberately lower: we splice only boundaries whose *both* sides are
training episodes, because four of the reference's nine put held-out rows into training. That is a
leakage problem rather than a physics one, and including it would have invalidated our own
comparison. So this experiment measures the cost of training on physically impossible transitions,
and not the reference's full exposure.

Training loss over the final 250 iterations: duplication costs {{dup_cost_pct}}%, splicing costs
{{contam_cost_pct}}%. The bootstrap interval on duplicated − clean is
[{{dup_ci_lo}}, {{dup_ci_hi}}], including zero. So the rise is caused by splice content, not by
dataset size — a control we ran only because the first version of this finding inferred the
mechanism without it.

In rollout, across {{tw_cells}} cells (two arenas × two trajectory lengths × two checkpoints × two
horizons × two metrics), contamination hurts in **{{tw_cc_cluster_hurt}}** of {{tw_cells}} and
helps in {{tw_cc_cluster_helped}} (Figure 5a). The control is inert, differing from clean in
{{tw_dc_cluster_helped}} cells. **The unmarked boundaries remain a real defect on leakage grounds;
what is now measured is that the physically-impossible-transition component costs nothing
detectable at this rate.**

---

## 6. The released checkpoint cannot have come from the released recipe

The collapse rate is a clock. Fitting it across our runs and extrapolating to the released
checkpoint's σ state implies **{{implied_iters}}** optimisation steps at the configured learning
rate. The refit from our 10,000-iteration runs gives {{q4_implied_A}} and {{q4_implied_B}},
spreading {{implied_spread_pct}}% across the three fits — a linear extrapolation
validated over a fourfold extension.

The released configuration says 500 iterations. The paper says 2,500. The checkpoint is tagged
5,000. A second, independent parameter on a slower gradient path implies the same order. And under
`gaussian_nll` the implied count is *negative*, which identifies the branch the checkpoint was
trained with.

---

## 7. Method

**An append-only ledger.** Every claim in this work has a permanent identifier, an evidence class
(source, data, run, external, inference) and a status, in `FINDINGS_LEDGER.md`
({{n_entries}} entries). Claims are never edited in place. A claim that turns out to be wrong is
marked superseded, with a pointer to what replaced it, and kept.

**Pre-registration, and one failure of it.** Decision rules were committed to git before the data
that tested them — with one exception, which we report below. Figure 4 shows the lead time for
each, computed from commit timestamps: the A/B rule by {{lead_m16}}, the flip-pattern rule by
{{lead_flip}}, the difficulty-bias rule by {{lead_m22}}, the long-horizon rule by {{lead_m23}}.

The fifth bar is negative. The rule for the duplication control (§5.4) was stated in conversation
before the runs but reached git **{{lead_task3}} after the runs finished**, and we found this only by
auditing our own `git log`. The measurement stands — the arm was built and run without reference
to its outcome — but the claim that it was pre-registered does not, and we withdraw it. We report
it because a discipline that is only checked when it succeeds is not a discipline.

**{{n_retractions_word}} retractions on our own evidence**, out of {{n_superseded}} superseded claims
kept in the record. In order: a premise about forecast decay that turned out not to exist in the
code; a framing of the released checkpoint as "clearly informative" that rested on an n=10 estimate
we ourselves showed to be biased low; an aggregation artifact that inverted a published-model
comparison in our favour, withdrawn when the gating checks we had written refuted it; a
per-dimension comparison that turned out to be unmatched; and the claim that σ is input-independent
"in all four models", made against a table holding three. The pre-registration claim above is a
sixth, retracting a framing rather than a number.

**A statistic that was resampling the wrong unit.** Our bootstrap pooled three training seeds over
a shared set of evaluation trajectories and resampled the pooled vector, while reporting the
independent-trajectory count. Each trajectory appeared three times. Resampling trajectories
correctly — carrying all seeds with each draw — widens intervals by a mean factor of
{{bu_mean_ratio}}× (range {{bu_min_ratio}}–{{bu_max_ratio}}) and changes {{bu_changes}} of
{{bu_cells}} verdicts, in an h = 8 cell already recorded as unresolvable. Every long-horizon
verdict survives. Both units are reported.

**Reproducibility.** `./reproduce.sh --quick --force` regenerates {{ver_files}} artifact files and
{{ver_values}} numeric values from a clean clone, {{ver_identical}} of them bitwise identical
({{ver_pct}}%), {{ver_differing}} differing. Timing fields and one whole host-measurement artifact
are excluded and reported separately.

---

## 8. Limitations

**Effective sample size bounds every long-horizon claim.** The out-of-sample arena has
{{m23_nind}} independent 400-step trajectories. That is the binding constraint on §3, and no
amount of trajectory oversampling changes it.

**Ensemble size.** Our main experiment runs at ensemble size 1 against the reference's 5, for CPU
budget, so our own arms have no epistemic component — it is identically zero by construction at
ensemble size 1. The epistemic measurement in §4.2 is therefore made on the released checkpoint
only, and we cannot say how ensemble disagreement would behave in a model we trained.

**One dataset, one gait, one terrain.** All commands are drawn from one bounded box and the gait
is a single trot throughout. "Generalisation" here means across velocity commands, not across
gaits or terrain.

**Two of our headline analyses rest on a single training seed**, because only one
10,000-iteration run per arm exists. This is recorded in the artifacts themselves.

**We did not reproduce the policy-learning results** of either paper. This is a dynamics-model
reproduction only.

---

## 9. Conclusion

The Robotic World Model's central training claim reproduces, and the margin is large. Neither
uncertainty output of the follow-up that adds them reports what a reader would take it to report.
The aleatoric σ is {{cal_rel_ratio}}× smaller than its own error, and the cause is that the
objective's optimum is σ = 0 with the term that should prevent this cancelling out of the
gradient. The epistemic term the method actually penalises with is better by two orders of
magnitude and still {{b2_epi_ratio_h368}}× overconfident where it is used.

The more useful finding is that ranking survives where scale does not, in both components. The
teacher-forced arm has input-dependent σ and good ordering; the epistemic term ranks better still,
at {{b2_epi_npos_h368}} of {{b2_epi_ndim_h368}} dimensions positively correlated with realised
error. Neither yields a usable interval. Uncertainty in this family of models should be reported
as an ordering, or fixed at the objective, but not read as a scale.

---

## Data and code

The full repository — code, every artifact under `results/`, and `FINDINGS_LEDGER.md` with the
complete claim record including the retractions — accompanies this submission as anonymised
supplementary material, and will be released under a permanent archival identifier on
acceptance. Neither upstream repository is redistributed; `setup.sh` fetches both at pinned
commits and verifies two SHA-256 hashes.

The pre-registration argument in §7 rests on commit timestamps. The supplementary material
includes an anonymised `git log` covering every commit cited here, so the ordering in Figure 4 is
checkable at review time; the archival identifier, which is not author-settable, is disclosed on
acceptance.

## References

1. C. Li, A. Krause, M. Hutter. *Robotic World Model: A Neural Network Simulator for Robust Policy
   Optimization in Robotics.* arXiv:2501.10100, 2025.
2. C. Li, A. Krause, M. Hutter. *Uncertainty-Aware Robotic World Model Makes Offline Model-Based
   Reinforcement Learning Work on Real Robots.* arXiv:2504.16680, 2025.

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

`--force` matters: a clean clone already contains each stage's declared output, so without it
every stage skips. Training stages are excluded by `--quick`; a full run is roughly 22 hours on
two CPU cores.
