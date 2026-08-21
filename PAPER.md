<!-- GENERATED FILE — do not edit.
     Prose lives in PAPER.template.md; every number is substituted from
     results/paper_numbers.json by scripts/build_paper.py. Edit the template,
     then run: python scripts/build_paper.py
     186 values substituted from 28 artifacts. -->

# What a world model's uncertainty outputs actually report: an independent reproduction of the Robotic World Model

---

## Abstract

We independently reproduce the proprioceptive dynamics model of Li, Krause and Hutter
(*Robotic World Model*, arXiv:2501.10100) and its uncertainty-aware follow-up
(arXiv:2504.16680), building the model from scratch on CPU and verifying it against the released
reference at the level of outputs, losses and gradients before training anything.

The base paper's central claim reproduces, and by a wide margin: trained autoregressively, the
model reaches normalised error 0.3509 at a 368-step horizon on held-out episodes against
1.5540 for teacher forcing, a factor of 4.4×, with a bootstrap interval of
[0.56, 2.05] excluding zero and the gap positive on all
10 of 10 episodes. That verdict was fixed by a decision
rule committed to git before the runs that tested it existed.

Neither of the follow-up's uncertainty outputs survives contact with a calibration measurement.
The checkpoint emits a per-member **aleatoric** σ and an **epistemic** ensemble disagreement, and
the method penalises rewards with the second while discarding the first. We measure both. The
aleatoric σ is **7,878× smaller than its own mean absolute error**
(0.56% coverage at ±1σ against a calibrated 68.3%), and we show analytically why: the
state loss is squared error on a reparameterised sample with no log-σ term, minimised at σ = 0,
with the bound term that should oppose this cancelling algebraically. Running the correction —
the authors' own unused `gaussian_nll` branch — fails differently rather than succeeding, at
10.9× overconfidence. The epistemic term, the one the method actually consumes, is
two orders of magnitude better and still **39.7× overconfident at the deployment
horizon**, with 3.76% coverage.

Measuring all four models we trained or scored puts the failure precisely. The teacher-forced arm
has the most input-dependent σ (15.6× the autoregressive arm's) and the
strongest σ-versus-error ordering (45 of 45 dimensions positive,
P = 5.68e-14), and is still 315× overconfident. These models can learn *which*
predictions will be worse. They cannot learn *how wrong* they will be. A downstream user who needs
a ranking may be served; one who needs an interval is not, under any of the four.

We also report four defects in the released pipeline, evidence that the released checkpoint's
variance state is unreachable at any of the three iteration counts its own artifacts state, and
six retractions of our own numbered claims —
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
score both: *is the predicted σ calibrated?* Neither of the two the checkpoint emits is — the
per-member σ by three to four orders of magnitude, the ensemble disagreement the method actually
uses by one to two — and for the first of them the reason is structural rather than incidental.

This is a reproduction paper, and we mean the term in its stronger sense: the contribution is not
that the numbers came out the same, but what systematically re-measuring the method reveals about
where it is robust and where it is not. §8 collects the lessons in a form a practitioner can apply
without reading the rest. Three things distinguish the work from a re-run of the authors' code.

**We rebuilt rather than imported.** The forward pass, the loss and the training step are written
from scratch and then checked against the reference: outputs match bitwise, and losses and
gradients match to 0.000e+00 across 7 loss terms and
106 parameter tensors before any training begins
(Appendix A). A discrepancy found later is therefore a property of the method, not of our wiring.

**Decision rules were committed before the data.** The verdicts below were fixed in advance, in
git, with timestamps a reader can check (§7, Figure 4). One of them returned "cannot be settled"
and we report that too.

**We retract our own findings when they fail.** Six claims in this work are
withdrawn on evidence this project produced, and the retractions are kept in the record rather
than deleted. One of them concerns the pre-registration discipline itself.

---

## 2. Setup

**Data.** The released dataset is 10,000 rows of ANYmal D proprioceptive state and policy
actions at 50 Hz. It is not one recording: it is ten concatenated 20-second episodes, and its
termination column is identically zero, so nothing in the file marks the boundaries. The reference
window builder therefore marks all 9,961 windows valid, including 352 that
splice one episode's end onto the next one's start. The usable, episode-respecting count is
9,609 — 10,000 rows, less 39 that cannot start a full window, less
352 that cross a boundary. The contamination rate is 3.53%.

**Model.** A GRU-based ensemble predicting the next proprioceptive state, with a mean head and a
bounded log-σ head, plus auxiliary heads for contact and termination. The paper describes two loss
terms; the implementation has 7.

**Evaluation.** Two arenas, held separate throughout: *out-of-sample*, the two episodes withheld
from training, and *in-sample*, the eight used for it. We report both, because the released
evaluation draws its trajectories from training data and the distinction is invisible in the
original.

**Effective sample size.** Trajectory count is not sample size. Two 400-step trajectories whose
spans overlap are not independent evidence, and the out-of-sample arena contains only
4 mutually non-overlapping 400-step trajectories. Every interval in this paper is a
bootstrap over independent trajectories, and every table reports that count.

---

## 2b. What the original papers claim, and which claims we test

A reproduction that does not say what it left alone invites the reader to assume it tested
everything. It did not.

| claim, and where | tested | verdict |
|---|---|---|
| RWM-AR consistently outperforms RWM-TF (2501.10100 §IV-D) | **yes** | **reproduces** at long horizon (§3) |
| Teacher forcing gives "poor autoregressive performance" (§IV-C) | **yes** | reproduces, and more strongly: Arm B is worse than the hold-last floor |
| M=32, N=8 is the optimal configuration (§IV-C) | no | we use the released configuration and did not sweep it |
| Beats MLP, RSSM and transformer baselines (§IV-D) | no | the lite release ships only the RNN variant |
| Zero-shot hardware transfer (§IV-E) | no | no hardware; this is a dynamics-model reproduction |
| MBPO-PPO beats SHAC and Dreamer (§IV-E) | no | no policy learning reproduced |
| Generality across quadruped, humanoid, manipulation (§IV-D) | no | one released dataset, ANYmal D flat |
| Epistemic "closely follows the trend of the prediction error", justifying "its role as a trust metric" (2504.16680 §5.1) | **yes** | **supported as an ordering** (§4.2); not as a scale |
| Aleatoric "remains low, reflecting small stochasticity" (§5.1) | **yes** | the observation holds; the explanation does not (§4.3) |
| Offline MBRL on real robots (2504.16680) | no | not tested |

---

## 3. The base paper's central claim reproduces

**Claim under test.** Training the dynamics model on its own autoregressive rollouts beats
training it with teacher forcing, at deployment horizons.

**Rule, committed in advance** (commit `efc35b8`, and it names conditions rather than outcomes).
Three conditions, all required: the out-of-sample gap at h = 368 excludes zero
under a bootstrap over independent trajectories; the sign is consistent across episodes; and the
effect survives at 10,000 iterations rather than only at the paper's 2,500.

**Result.** Every condition holds. We give the evidence in order of how little it depends
on the small held-out sample.

*The sign test, which does not depend on n.* At h = 368 the per-episode gap favours
autoregressive training on **10 of 10** episodes — an exact two-sided
binomial test, p = **0.0020**. This is one test on ten paired episodes, it uses no
bootstrap, and no multiplicity correction touches it.

*The in-sample arena, where the sample is larger.* The same comparison on the eight training
episodes has 16 independent 400-step trajectories against the held-out arena's
4 — 4× more — and gives the same direction at every horizon and
checkpoint.

*The out-of-sample effect size, reported last and with its limitation stated.* Autoregressive
training reaches **0.3509** against teacher forcing's **1.5540** — a factor of
**4.4×**, gap 1.2033, 95% bootstrap interval [0.56, 2.05] on
n = 4 independent trajectories.

*Against a baseline, because neither number means anything without one.* The hold-last floor —
predicting that nothing changes — scores **0.9930** in the same cell. Autoregressive
training beats it by **2.8×**. **Teacher forcing is 1.56× worse than
assuming nothing changes at all**, which is the sharper statement of what exposure bias costs
here: the arm that reaches a lower training loss ends up predicting the future worse than a
model that makes no prediction. **That interval should not be read as an ordinary
one:** four trajectories admit 256 distinct resamples, so any bootstrap tail is
quantised to steps of 0.39%, and the interval is coarse by construction. It is offered as
corroboration of the sign test, not as the primary evidence.

**What does not hold, and we say so.** At h = 8 — the horizon the model is trained on — the same
comparison out-of-sample gives a gap of 0.008 whose interval includes zero.
The advantage is a long-horizon phenomenon. An earlier rule of ours, anchored
at h = 8, returned "cannot be settled"; anchoring a rule to the horizon the claim is actually
about was a correction we had to make in advance of the runs, not after them (§7).

The pattern is consistent across the design. Under the correct cluster bootstrap, the
out-of-sample gap excludes zero in **4 of 4** long-horizon cells —
both trajectory lengths crossed with both checkpoints — and in **0 of
4** at h = 8. These figures are relative-L1; the nRMSE aggregation is reported
separately and does not change the direction.

**Multiplicity.** Those 4 cells sit in a family of 8 out-of-sample
comparisons, so we state the correction rather than leaving it to a reader. All
4 of 4 still exclude zero at a Bonferroni level of 0.05/8,
and Holm–Bonferroni rejects **4 of 4**. The sign test above is
unaffected either way.

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

So the aleatoric head — the one the state loss and the bound loss shape, and the one §4.3
explains — is computed on every imagination step and discarded. We report both quantities below.
Our own arms are ensemble size 1, where the epistemic term is identically zero by construction,
so the epistemic measurement is possible only on the released checkpoint.

**What the follow-up does and does not claim, stated before we measure anything.** It does not
claim its uncertainty is a calibrated interval. §5.1 claims the epistemic term "closely follows
the trend of the prediction error" and that this "justifies its role as a trust metric", and of
the aleatoric term it observes only that it "remains low, reflecting small stochasticity in the
environment". Our measurement **supports the first claim** — the epistemic ordering is real and
strong. What follows is therefore not a refutation of a calibration claim nobody made. It is
three things the papers do not address: that the aleatoric head is discarded before use, that
neither quantity is usable as a scale, and that the low aleatoric value has a different cause
than the one offered.

### 4.2 The measurement

For each model we compute the mean predicted σ, the mean absolute realised error, and the fraction
of realised errors falling inside ±1σ. A calibrated Gaussian puts 68.3% inside ±1σ.

| model | mean \|error\| / mean σ | coverage at ±1σ, h=1 | coverage at h=368 |
|---|---|---|---|
| faithful Arm A (sampled MSE) | 52.2× | 11.67% | 1.75% |
| corrected Arm A (`gaussian_nll`) | 10.9× | 42.78% | 8.57% |
| teacher-forced Arm B | 315× | 12.96% | 0.56% |
| released checkpoint | 7,878× | 0.56% | 0.04% |

On the aleatoric head every model is overconfident by between one and four orders of magnitude
(Figure 1) — that is the quantity §4.1 shows the method discards.

**The quantity the method does use is also uncalibrated.** On the released
5-member checkpoint, out-of-sample, n = 4 independent trajectories:

| h | aleatoric err/σ | epistemic err/σ | epistemic ±1σ | epistemic ±2σ | dims r>0 | P |
|---|---|---|---|---|---|---|
| 1 | 597× | **4.7×** | 17.78% | 37.22% | 23/45 | 1.0e+00 |
| 8 | 802× | 6.3× | 12.15% | 25.14% | 25/45 | 5.5e-01 |
| 32 | 1,530× | 11.1× | 8.70% | 17.66% | 34/45 | 8.2e-04 |
| 128 | 5,132× | 28.4× | 5.42% | 10.95% | 45/45 | 5.7e-14 |
| 368 | 7,878× | **39.7×** | 3.76% | 7.69% | 45/45 | 5.7e-14 |

Epistemic is two orders of magnitude better than aleatoric — 126× larger at
h=1, 198× at h=368 — and still wrong by
**4.7×** at one step and **39.7×** at the deployment horizon,
with ±1σ coverage of 3.76% where a calibrated Gaussian gives 68.3%. **Total**
uncertainty, `sqrt(aleatoric² + epistemic²)`, equals the epistemic value to four significant
figures at every horizon, because the aleatoric term is too small to move it.

The scalar penalty as actually applied — `means.std(0).sum(-1)` at `envs/base.py:166` —
correlates +0.348 with total absolute error over the rollout.

### 4.3 Why the aleatoric head collapses: the optimum is σ = 0

This subsection explains the aleatoric column and only that column. Ensemble disagreement is not
shaped by the mechanism below, and why *it* is miscalibrated is not established here.

It also supplies the alternative explanation promised in §4.1. The follow-up reads the low
aleatoric value as reflecting "small stochasticity in the environment". The observation is
correct and the reading is not: σ is low because σ = 0 is the optimum of the loss that trains it,
and it would be low on any dataset, stochastic or not.

The state loss is squared error on a *sample* drawn from the predicted Gaussian, not a likelihood:

$$\mathcal{L} \;=\; \mathbb{E}\big[(\mu + \sigma\varepsilon - y)^2\big] \;=\; (\mu - y)^2 + \sigma^2$$

which is minimised at σ = 0 for any μ. There is no log-σ term to oppose it. The bound term that
appears to oppose it does not, because `max_logstd` is not an independent parameter — it is
constructed as `min_logstd + exp(log_delta_logstd)`, so

$$\overline{\log\sigma_{\max}} - \overline{\log\sigma_{\min}} \;=\; \overline{\exp(\log\Delta_{\log\sigma})}$$

and `min_logstd` cancels algebraically, taking no gradient from that term. The floor the interval
closes onto therefore freezes while the interval closes: a one-way ratchet.

We predicted the collapse from this algebra before training, then observed it. Across all
18 runs the collapse is linear in iteration count and its rate is nearly identical
(Figure 3a). Under the corrected objective the sign flips (Figure 3b) — which is the strongest
evidence that the mechanism is the objective and not the optimiser, the data or the architecture.

**Two different things are being explained here, and §4.5 separates them.** *Magnitude collapse
is objective-driven.* It occurs in all 12 sampled-MSE runs at a rate of
-9.3986e-05 per iteration with a standard deviation of 6.8e-07 — **including the
teacher-forced arm**, which shares the objective — and reverses to +3.2332e-05 in the
3 runs that change it. *Input-independence is not.* That varies by a factor of
15.6 between two arms trained under the same objective, so the objective
cannot be what produces it.

### 4.4 The correction fails differently rather than succeeding

The reference contains an unused `gaussian_nll` branch. Running it reverses the collapse and
improves the magnitude from 52.2× to 10.9× overconfident. It does not
produce a usable estimate, and it destroys something the faithful arm had: the σ-versus-error
ordering falls from 39/45 dimensions positively correlated
(P = 5.42e-07) to 21/45 (P = 7.66e-01, chance).

### 4.5 The failure is one of magnitude, not of ordering

Measuring the teacher-forced arm — which we had trained for §3, and which our own first three
calibration tables omitted — sharpens the finding:

| model | σ variation across inputs (CoV) | dims with r(σ, error) > 0 | P |
|---|---|---|---|
| faithful Arm A | 0.0076 | 39/45 | 5.42e-07 |
| corrected Arm A | 0.0059 | 21/45 | 7.66e-01 |
| **teacher-forced Arm B** | **0.1188** | **45/45** | **5.68e-14** |
| released checkpoint | 0.0177 | 20/45 | 5.51e-01 |

Arm B's σ is 15.6× more input-dependent than the faithful arm's, and its
ordering is the strongest of the four by a wide margin (mean r = 0.257). It is still
315× overconfident.

So σ *collapsing in magnitude* is objective-driven, and σ *becoming input-independent* is not.
The teacher-forced arm collapses in magnitude exactly like the autoregressive ones — same
objective, same rate — while retaining 15.6× more variation across
inputs. Input-independence is a property of the autoregressive arms and the released checkpoint,
and input-dependence and correct ranking are both achievable without the interval becoming
meaningful.

One candidate mechanism, stated as a hypothesis and not a result: autoregressive feedback narrows
the input distribution toward the model's own manifold, leaving a heteroscedastic head less
variation to key on. We have not tested it.

**The same pattern holds for the quantity the method uses, with the strongest evidence in this
paper.** At h=128 and h=368 the epistemic term correlates positively with realised error on
**45 of 45** dimensions, P = 5.7e-14 — a better
ranking than any aleatoric head here — while being 39.7× overconfident. And it
fails the horizon test the same way: σ grows 1.59× from h=1 to h=368 while
error grows 13.33×.

**The failure is specifically magnitude calibration, in both components.**

### 4.6 One scalar does not fix it

If σ had the right shape and the wrong scale, a single multiplier would repair it, and the
finding would be a units problem with a one-line remedy. We tested that. A scalar was fitted on
**one** held-out episode and evaluated on the **other**, in both directions, so it is never
fitted on its own test set.

Fitting at one step works at one step and nowhere else. On the epistemic term — the quantity the
method uses — a scalar of 5.08–5.82 brings h=1 coverage to
63–74%, essentially calibrated against the 68.3% target,
and leaves h=368 at 17–21%. On the aleatoric term a scalar of
593–611 gives 64–70% at h=1 and
11–15% at h=368. Fitting over the whole rollout instead
drives one-step coverage to 100% — an interval wide enough to be vacuous where the model is
accurate — while still falling short at the far end.

The reason is §4.7's mechanism: a constant multiplier cannot track an error that grows while σ
does not. So "right shape, wrong scale" is the charitable reading of these tables and it does not
survive. A per-horizon or input-dependent correction might still work; a constant one does not.

### 4.7 The structural excuse does not survive

One could argue that a model trained on an 8-step horizon cannot be expected to report calibrated
uncertainty about step 368. It cannot report it about step 8 either. Inside the trained horizon,
σ is flat while error grows (Figure 2):

| model | σ growth, step 1 → 8 | error growth, step 1 → 8 |
|---|---|---|
| faithful Arm A | 0.9241× | 3.49× |
| corrected Arm A | 1.0003× | 3.41× |
| teacher-forced Arm B | 1.0096× | 6.11× |
| released checkpoint | 1.0007× | 1.79× |

The faithful arm's σ *declines* (0.9241×) while its error grows
3.49×. The coverage collapse in Figure 1(b) is therefore driven entirely by
growing error against a fixed σ.

---

## 5. Defects in the released pipeline

**5.1 Ten unmarked episode boundaries.** §2. The window builder reads a termination column that is
identically zero, so it marks all 9,961 windows valid.

**5.2 Training and evaluation disagree on action alignment, and evaluation is the broken one.**
Row *t* holds the action that *produced* state *t*. The training path pairs states and actions
index-for-index, which is causally correct. The evaluation path feeds the action from *t−1* to
predict state *t* — stale by one step. Scored correctly the released checkpoint is materially
better than its own released evaluation reports: nRMSE at h = 368 falls from 1.3228
under the released pairing to 0.7572 under the causal one, so the released evaluation
overstates its own model's error by 75%.

**5.3 No held-out evaluation.** Evaluation trajectories are drawn from training data. For the
released checkpoint, trained on the entire file, no held-out measurement is possible at all.

**5.4 What the spliced windows cost: nothing measurable.** We trained a contaminated arm on
7,882 windows — the clean 7,687 plus 195 splices — and,
because that confounds *content* with *count*, a duplication control adding the same
195 windows as exact copies of windows already present.

The arm's contamination rate is 2.47%, against the reference pipeline's
3.53%. It is deliberately lower: we splice only the 5 boundaries whose *both* sides
are training episodes, because 4 of the 9 put held-out rows
into training. That is a
leakage problem rather than a physics one, and including it would have invalidated our own
comparison. So this experiment measures the cost of training on physically impossible transitions,
and not the reference's full exposure.

Training loss over the final 250 iterations: duplication costs 0.90%, splicing costs
21.57%. The bootstrap interval on duplicated − clean is
[-0.0061, 0.0215], including zero. So the rise is caused by splice content, not by
dataset size — a control we ran only because the first version of this finding inferred the
mechanism without it.

In rollout, across 32 cells (two arenas × two trajectory lengths × two checkpoints × two
horizons × two metrics), contamination hurts in **0** of 32 and
helps in 9 (Figure 5a). The control is inert, differing from clean in
2 cells.

**"Costs nothing" is the wrong summary, and we should not use it.** Splicing raises training loss
by 21.57% against duplication's 0.90%, and improves rollout in
9 of 32 cells. Both are measured effects in opposite directions,
which is the signature of regularisation: the spliced windows contain transitions the model
cannot fit, it fits the rest less tightly as a result, and it rolls out slightly better. The
defensible statement is that **at this rate the splices do not harm rollout and appear to help
slightly**, not that they cost nothing. **The unmarked boundaries remain a real defect on leakage grounds;
what is now measured is that the physically-impossible-transition component costs nothing
detectable at this rate.**

---

## 6. The released checkpoint's variance state is unreachable at the stated iteration counts

The collapse rate is a clock. Fitting it across our runs and extrapolating to the released
checkpoint's σ state implies **153,270** optimisation steps at the configured learning
rate. The refit from our 10,000-iteration runs gives 158,319 and 158,003,
spreading 3.3% across the three fits — a linear extrapolation
validated over a fourfold extension.

The released configuration says 500 iterations. The paper says 2,500. The checkpoint is tagged
5,000. A second, independent parameter on a slower gradient path implies the same order. And under
`gaussian_nll` the implied count is *negative*, which identifies the branch the checkpoint was
trained with.

**What this extrapolation assumes, and what would falsify it.** It assumes constant-rate Adam at
the configured learning rate from the released initialisation. Five things would break it, and
they are not equally plausible:

| assumption | if violated | ruled out by the second parameter? |
|---|---|---|
| no learning-rate schedule | a decaying schedule inflates the implied count; a warm-up deflates it | **partly** — `min_logstd` and `log_delta_logstd` travel at rates differing by about 5×, and a uniform schedule scales both, so a schedule alone cannot reconcile them without also changing their ratio |
| `log_delta_logstd` initialised as released | a different initialisation moves the origin of the fit and rescales the count linearly | **no** — this is the weakest point of the argument |
| no warm start from an earlier checkpoint | a warm start makes the count a lower bound on total optimisation, not an estimate of one run | **no** |
| no gradient clipping in this path | clipping would slow the collapse and inflate the implied count | **partly** — the reference does not clip in the world-model path (X-08), so this is ruled out by source rather than by measurement |
| bound-loss weight as configured | a different weight scales the rate directly | **partly** — same ratio argument as the schedule |

So the defensible claim is narrower than "cannot have come from the released recipe": **no
constant-rate run from the released initialisation at the configured learning rate reaches this
checkpoint's variance state in 500, 2,500 or 5,000 iterations.** A warm start or a different
initialisation would explain the gap without any inconsistency, and we cannot exclude either.

**Author contact.** We wrote to the first author on 21 August 2026 asking exactly this — whether
the released checkpoint was warm-started, or `log_delta_logstd` initialised differently, or a
learning-rate schedule used — and had no response as of submission. A warm start or a changed
initialisation would resolve the discrepancy immediately and neither is visible from the released
artifacts, so their answer would very likely settle it. If it is settled after submission we will
say so; the section stands as a bounded observation until then, not as an accusation.

---

## 7. Method

**An append-only ledger.** Every claim in this work has a permanent identifier, an evidence class
(source, data, run, external, inference) and a status, in `FINDINGS_LEDGER.md`
(162 entries). Claims are never edited in place. A claim that turns out to be wrong is
marked superseded, with a pointer to what replaced it, and kept.

**Pre-registration, and one failure of it.** Decision rules were committed to git before the data
that tested them — with one exception, which we report below. Figure 4 shows the lead time for
each, computed from commit timestamps: the A/B rule by 1.3 hours, the flip-pattern rule by
4.8 hours, the difficulty-bias rule by 5 minutes, the long-horizon rule by 2 minutes.

The fifth bar is negative. The rule for the duplication control (§5.4) was stated in conversation
before the runs but reached git **2.9 hours after the runs finished**, and we found this only by
auditing our own `git log`. The measurement stands — the arm was built and run without reference
to its outcome — but the claim that it was pre-registered does not, and we withdraw it. We report
it because a discipline that is only checked when it succeeds is not a discipline.

**Six retractions on our own evidence**, out of 14 superseded claims
kept in the record. In order: a premise about forecast decay that turned out not to exist in the
code; a framing of the released checkpoint as "clearly informative" that rested on an n=10 estimate
we ourselves showed to be biased low; an aggregation artifact that inverted a published-model
comparison in our favour, withdrawn when the gating checks we had written refuted it; a
per-dimension comparison that turned out to be unmatched; and the claim that σ is input-independent
"in all four models", made against a table holding three. The pre-registration claim above retracts a framing rather
than a number and is counted separately.

**A statistic that was resampling the wrong unit.** Our bootstrap pooled three training seeds over
a shared set of evaluation trajectories and resampled the pooled vector, while reporting the
independent-trajectory count. Each trajectory appeared three times. Resampling trajectories
correctly — carrying all seeds with each draw — widens intervals by a mean factor of
1.42× (range 0.96–1.69) and changes 1 of
16 verdicts, in an h = 8 cell already recorded as unresolvable. Every long-horizon
verdict survives. Both units are reported.

**Reproducibility.** `./reproduce.sh --quick --force` regenerates 19 artifact files and
4,804 numeric values from a clean clone, 4,804 of them bitwise identical
(100.00%), 0 differing. Excluded and reported separately: 2,362 timing fields, and the
22 values in `results/step4_5_timing.json`. That file is the CPU budget — projected
runtimes for configurations we did not run, peak resident memory, and the standard deviation
across repeats — and every number in it measures the host rather than the model. It cannot
reproduce bitwise on a different machine, or on the same machine under different load: one stage
timed at 46.5 s idle took 109.7 s with training running concurrently.

---

## 8. Actionable lessons

Four things a practitioner can apply without reading the rest of this paper.

**Report uncertainty in this model family as an ordering, not as a scale.** Both of the released
checkpoint's uncertainty outputs rank which predictions will be worse — the epistemic term at
45 of 45 dimensions, P = 5.7e-14 — and neither is
within an order of magnitude of a usable interval. A ranking use is supported by our measurements
and by the follow-up's own claim. A risk gate, a safety margin, or anything that reads σ as a
distance is not, and no single scalar repairs it (§4.6).

**Count independent trajectories, not trajectories.** Two 400-step windows that overlap at all
are one piece of evidence, not two. The held-out arena here contains 4 independent
400-step trajectories however many windows are drawn from it, and that number — not the window
count — bounds every long-horizon claim. Reporting an interval beside a trajectory count rather
than an independent-trajectory count overstates precision, and resampling pooled seed × trajectory
values instead of trajectories narrows intervals by a further 1.42× (§7).

**Anchor a decision rule to the horizon the claim is about.** Our first pre-registered rule was
anchored at h = 8, the training forecast horizon, and returned "cannot be settled". The claim was
about deployment horizons. The rule was correct in form and pointed at the wrong regime, which is
a failure mode that pre-registration does not protect against on its own.

**Check that the implemented loss is the described loss before reproducing any number from it.**
The paper describes two loss terms; the implementation has 7. The predicted variance
has an optimum at zero under the implemented one, which is why the released checkpoint's σ is
7,878× smaller than its own error. Reading the loss took an afternoon and explained a
result that would otherwise have looked like a training bug.

---

## 9. Broader impact

This is a reproduction of a dynamics model on public simulation data, and the reproduction itself
carries no significant risk of harm: no new capability, no personal data, no deployment.

The finding does bear on safety, in one specific way worth stating. The method this paper examines
uses its uncertainty estimate as a **trust metric** — a reward penalty that steers a policy away
from states the model is unsure about. That use is supported by our measurements. But a downstream
user who reads the same quantity as a *calibrated interval* — a safety margin, a confidence bound,
a gate on when to hand control to a fallback controller — would be materially misled: at the
deployment horizon the released checkpoint's ensemble disagreement is
39.7× smaller than the realised error, giving 3.76% coverage
where 68.3% is expected. On hardware, a margin that is wrong by that factor is the difference
between a conservative controller and one that believes it is safe when it is not.

We think that makes the finding worth publishing rather than the reverse, and it is the reason
§4 reports coverage rather than only correlation.

---

## 10. Limitations

**Effective sample size bounds every long-horizon claim.** The out-of-sample arena has
4 independent 400-step trajectories. That is the binding constraint on §3, and no
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

## 11. Conclusion

The Robotic World Model's central training claim reproduces, and the margin is large. Neither
uncertainty output of the follow-up that adds them reports what a reader would take it to report.
The aleatoric σ is 7,878× smaller than its own error, and the cause is that the
objective's optimum is σ = 0 with the term that should prevent this cancelling out of the
gradient. The epistemic term the method actually penalises with is better by two orders of
magnitude and still 39.7× overconfident where it is used.

The more useful finding is that ranking survives where scale does not, in both components. The
teacher-forced arm has input-dependent σ and good ordering; the epistemic term ranks better still,
at 45 of 45 dimensions positively correlated with realised
error. Neither yields a usable interval. Uncertainty in this family of models should be reported
as an ordering, or fixed at the objective, but not read as a scale.

---

## Data and code

The full repository — code, every artifact under `results/`, and `FINDINGS_LEDGER.md` with the
complete claim record including the retractions — accompanies this submission as anonymised
supplementary material, and will be released under a permanent archival identifier on
acceptance. Neither upstream repository is redistributed; `setup.sh` fetches both at pinned
commits and verifies two SHA-256 hashes.

The pre-registration argument in §7 rests on commit timestamps, and those are author-settable via
`git commit --date`. That matters, because §7 is load-bearing. Two things address it. The
supplementary material includes an anonymised `git log` covering every commit cited here, so the
ordering in Figure 4 is checkable at review time. And **the repository was archived by Software
Heritage on 21 August 2026**, before submission, under a permanent identifier whose visit
timestamp is not author-controllable; the identifier resolves to a named repository and is
therefore disclosed on acceptance rather than here.

What that archive establishes should be stated precisely, because it is easy to overclaim. It
does **not** prove any individual commit date is genuine. It proves that the repository, with the
whole pre-registration history in the form this paper cites, existed no later than that archival
moment, as recorded by a third party with no interest in the claim — so nothing in the record can
have been back-dated afterwards. That bounds §7 rather than proving it, and a reviewer should
read it as such.

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
| wiring | inference outputs match the reference module | **0.000e+00**, bitwise |
| indexing | the harness feeds the actions it claims | bitwise against the raw CSV |
| residual | the zero-delta model is the hold-last floor | 1.192e-07 |
| **objective** | **losses and gradients match** | **0.000e+00 across 7 terms, 106 tensors** |
| trainer | can memorise a single batch | 1,506× loss reduction |

## Appendix B — reproducing

    ./setup.sh                     # clone upstreams at pinned commits
    python3.11 -m venv .venv && . .venv/bin/activate
    pip install -r requirements.txt
    ./reproduce.sh --quick --force # everything except training

`--force` matters: a clean clone already contains each stage's declared output, so without it
every stage skips. Training stages are excluded by `--quick`; a full run is roughly 22 hours on
two CPU cores.

## Figures

![paper_fig1_calibration.png](figures/paper_fig1_calibration.png)

![paper_fig2_sigma_profile.png](figures/paper_fig2_sigma_profile.png)

![paper_fig3_collapse.png](figures/paper_fig3_collapse.png)

![paper_fig4_prereg_timeline.png](figures/paper_fig4_prereg_timeline.png)

![paper_fig5_three_way.png](figures/paper_fig5_three_way.png)

