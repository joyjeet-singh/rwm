# Referee questions — the evidence

What Phase A found, with the evidence beside each finding. One section per referee question.
This file records the evidence; block B3 writes the findings into the paper. Nothing here is
softened to fit the paper's existing framing, and where a finding runs against the paper's
convenience it is marked as such.

Ledger entries: `D-36` (Q4), `R-74` (Q2). Both appended in the block that wrote this file.

---

## Q4 — Is the released training data exhausted by these ten episodes, or does the upstream pipeline generate more on demand?

**The referee's stake in it.** If the pipeline generates more, the paper's largest scope caveat —
that the released checkpoint trained on all ten episodes and so has no held-out arena in this
dataset at all — is a choice rather than a constraint, and a reviewer is entitled to ask why the
choice was made.

**Answer: the generator is not in either released repository.** Of the three answers this
question admits — more data is obtainable on this hardware; more data needs a GPU and a
simulator; the generator is not in the released repositories — the evidence gives the third, and
the third implies the second.

### The evidence, file and line

Both upstreams read-only at their pinned commits: `robotic_world_model_lite` at
`13a798e9d35dabf12c0e6e02977b25ec64dfb2bd`, `rsl_rl_rwm` at
`18eebcdd7145284c8d5eed5d8ed1a4b96c649693`.

| # | what | where |
|---|---|---|
| 1 | The only code that touches `state_action_data_*.csv` **reads** it: `pd.read_csv` | `robotic_world_model_lite/scripts/train.py:44`, in `_load_data` (defined at `:34`) |
| 2 | When the file is missing or short it prints `Waiting for new data`, sleeps 1 s and retries inside a `while True` — a loop written for a *separate producer* appending files as it runs | `robotic_world_model_lite/scripts/train.py:46` and `:50`, loop opened at `:41` |
| 3 | **Neither repository contains a dataset write path.** A search of both for `to_csv`, `savetxt`, `np.save`, `to_parquet`, `csv.writer`, `DictWriter` and `open(..., 'w')` returns nothing. The file writes that do exist are four `torch.save` checkpoints, one git-diff text dump and tensorboard/wandb event files — none of them a dataset | `robotic_world_model_lite/scripts/policy_training.py:243` and `scripts/model_training.py:237`; `rsl_rl_rwm/rsl_rl/runners/on_policy_runner.py:301` and `mbpo_on_policy_runner.py:328`; the dump at `rsl_rl_rwm/rsl_rl/utils/utils.py:164` (mode `"x"`); events at `on_policy_runner.py:446-458` |
| 4 | The default data configuration is the **online** one: `dataset_root="logs/online"`, `dataset_folder="train"`, `batch_data_size=50000` | `robotic_world_model_lite/scripts/configs/base_cfg.py:33-36` |
| 5 | The shipped task **overrides** it to the one recording, and lowers the requirement to exactly that recording's row count: `dataset_root="assets"`, `dataset_folder="data"`, `batch_data_size=10000` | `robotic_world_model_lite/scripts/configs/anymal_d_flat_cfg.py:36-38` |
| 6 | The lite repository describes itself as being for training "from offline data ... without the need to set up a full robotics simulator like Isaac Lab" | `robotic_world_model_lite/readme.md:8` |
| 7 | It directs anyone wanting "online simulator-based data collection" to a **third** repository, the Isaac Lab RWM Extension at `github.com/leggedrobotics/robotic_world_model` | `robotic_world_model_lite/readme.md:13` |
| 8 | That repository is not one of the two this reproduction pins and is not present in this workspace | checked by directory search; only `robotic_world_model_lite` is present |
| 9 | The shipped environment cannot substitute: it rolls the **learned** dynamics, not physics. Every method is an imagination method; the dynamics are injected with `set_system_dynamics` | `robotic_world_model_lite/scripts/envs/anymal_d_flat.py` (methods `_init_additional_imagination_attributes`, `get_imagination_observation`, `_parse_imagination_states`, `_compute_imagination_reward_terms`) and `scripts/envs/base.py:40` |
| 10 | The entry point defaults to `--device cuda` and is titled "Online learning training" | `robotic_world_model_lite/scripts/train.py:341-344` |
| 11 | The released CSV: 10,000 rows × 66 columns, ten episodes plus a one-row stub, `file_data_size` in the config is 10,000 and the file holds exactly 10,000 | measured via `src/rwm_data.py` `load_data`; sha256 `1b2e00b8a2bc10dc9b5f62840de72410adb448a57a9a2f6adbcd735be9e78921` |
| 12 | The readme also describes the CSV as "Initial states for imagination rollout" — the shipped pipeline uses it both as the training recording and as rollout seeds (`init_data_ratio`) | `robotic_world_model_lite/readme.md:117`, `scripts/configs/base_cfg.py:44` |

### Cross-check against Appendix D

Appendix D (*what testing the untested claims would require*, `PAPER.md:1919-1953`) is **accurate
in its table and overstated in its lead**, and separately **incomplete** in one respect this
question makes precise. All three points are for block B3; Phase A may not touch the paper.

**Its lead overstates, and its own table is the contradiction.** `PAPER.md:1925` opens "Everything
below needs what this reproduction did not have: a simulator", and continues "Every untested claim
needs *interaction*". Two of the eight rows say otherwise in their own words — the MLP/RSSM/
transformer baseline comparison and the M=32,N=8 sweep are both priced at "no simulator needed"
(`:1939`, `:1940`) — and the appendix's own closing paragraph says "**The two at the bottom are
within reach of this setup**" (`:1942`). Two further rows price the binding constraint as hardware
access rather than compute — "not GPU hours" verbatim at `:1935`, and "hardware access again" at
`:1937`. So the table is right and the lead sentence describing
it is not.

**It is incomplete about where the collection code lives.** Appendix D locates the constraint in
the hardware and the simulator. The source locates it one step further out: the collection code is
in neither repository this reproduction pins. It is in a third repository the lite readme names at
`readme.md:13`. A reproducer who had the RTX GPU and Isaac Lab installed would still have to
obtain a repository outside the pinned set, at a commit this work never fixed. That is a sharper
statement of the constraint than "you need a simulator", and it is the statement a referee asking
this question is owed.

**What this does and does not license.** It does **not** license softening the scope caveat: more
data is not obtainable on this hardware, so the caveat is a constraint and not a choice, and the
paper's framing survives. It does oblige the paper to say *why* — because the generator is absent
from the released code, not merely because a GPU is absent from this desk.

---

## Q2 — How many independent trajectories would settle the free-baseline margin?

**The referee's stake in it.** §11 calls settling the step-size comparison "the cheapest open
question here for anyone with a second dataset". A number turns that from a gesture into an
invitation.

**Answer: 25 independent 400-step trajectories**, against the 20 this arena has —
1.25× the current sample — under the assumption stated at the end of this section.

### Two numbers, because there are two questions, and the first draft of this block conflated them

This is recorded rather than quietly corrected, because the conflation is instructive and a
reviewer caught it.

`M-51` fixed **one** threshold, 0.2891, before either new baseline existed. It had to be
estimated from the **forecast-index** margin, since step-size and entry-res did not yet exist to be
bootstrapped. That is correct pre-registration. But the index margin and the step-size margin are
different statistics with different sampling variability — 1.94× different.

**Why they differ, measured rather than assumed.** The obvious explanation is that disagreement is
correlated with step-size and not with the forecast index, so the first difference varies less.
**That explanation is false**, and an earlier draft of this document asserted it: the pooled
correlation of disagreement with the forecast index is +0.1377, not zero, against
+0.3227 with step-size. What actually drives the ratio is that the forecast index's *own*
correlation with error is far more variable across resampled trajectories than step-size's is —
sd 0.0836 against 0.0476, a factor of 1.76. Zeroing both covariance terms still
leaves a ratio of 1.52; the covariances, which have *opposite* signs across draws
(+0.21 for step-size against -0.38 for the index), widen it to 1.93. The
decomposition is stored under `empirical_check.variance_decomposition`, and it closes exactly: the
variances and covariances reproduce both standard errors to the last digit.

**Two ratios appear above and they are not the same quantity.** The 1.94× that the reported
answers rest on divides M-51's standard error by the interval-implied 0.053171; the 1.93 the
decomposition closes on divides it by the direct-bootstrap 0.053591, because the algebra must use
the standard error the same draws produced. The two differ by the 0.79% recorded below, and each
is used where it belongs.

The first draft of `scripts/q2_free_baseline_power.py` took the stored `bootstrap_se_margin` — the
index margin's — and applied it to the step-size margin's effect, inflating the requirement
3.64-fold. Both numbers are now reported, each against its own question:

| question | standard error used | threshold at n = 20 | n required |
|---|---|---|---|
| **(a) How many trajectories would resolve this margin?** — the referee's question | the step-size margin's own, 0.0532 | 0.1490 | **25** |
| (b) At what n would `M-51`'s protocol, re-run as pre-registered, fire on a margin this size? | the forecast-index margin's, 0.1032 | 0.2891 | 91 |

### The published verdict does not move, and this block does not move it

+0.1357 is below **both** thresholds, so §6.7's `SURVIVES entry-res ONLY` stands exactly as
published and no paper claim is affected. What changes is the distance. Against `M-51`'s
pre-registered threshold the margin reads as 47% of what the sample resolves; against its own
statistic's it is 91%. **`M-51`'s threshold is conservative when applied to this baseline**,
and that is a property of the pre-registered design worth stating rather than hiding — it means
the step-size comparison is much closer to resolving than the published figures imply.

### What is the same in both, and where (a)'s standard error comes from

The construction `M-51` used, unchanged:

    MDE = (Z95 + Z80) · se        Z95 = 1.959963985  (two-sided, α = 0.05)
                                  Z80 = 0.8416212336 (80% power)

with `se` a bootstrap standard error over **whole 400-step trajectories**, 4,000 replicates,
the statistic a difference of two correlations with realised error. Only `n` moves, as
se(n) = se(n₀)·√(n₀/n).

(a)'s standard error needs no rollout: `e7_free_baselines.py`'s `main` bootstraps **each
baseline's own margin** with the same unit and the same 4,000 replicates and stores a 2.5/97.5
percentile interval as `margin_ci`. For step-size that is [0.0425, 0.2509]; halving its width
and dividing by Z95 recovers 0.053171 under approximate normality of the bootstrap
distribution.

### The curve

| n | threshold (own statistic) | resolvable? |
|---|---|---|
| 20 | 0.1490 | no |
| 24 | 0.1360 | no |
| 25 | 0.1332 | yes |
| 30 | 0.1216 | yes |
| 40 | 0.1053 | yes |
| 50 | 0.0942 | yes |
| 100 | 0.0666 | yes |
| 200 | 0.0471 | yes |

### Checked rather than assumed

Running with `--empirical` bootstraps the step-size margin **directly** from the same panel with
E7's own seed and replicate count, and carries a control:

| quantity | direct bootstrap | from the artifact |
|---|---|---|
| step-size margin se | 0.053591 | 0.053171 (from `margin_ci`) |
| forecast-index margin se — **control** | 0.103195 | 0.103195 (stored) |

The interval-implied standard error agrees with the direct bootstrap to 0.79%, and the
control reproduces E7's stored value **exactly**, which is what establishes that the same panel,
unit, seed and replicate count are in play. The script asserts the control and refuses to report
if it fails.

**What the script's own self-check does not do.** `_check_same_construction` pins the two Z
constants and the multiplication — nothing more. It cannot see which baseline a standard error
belongs to, so it would **not** have caught the first draft's defect. The guard against that is
structural instead: (a) takes its effect and its standard error from the same baseline row, and
`--empirical` re-derives the standard error by bootstrap.

### The assumption, which is the whole of this number's epistemic status

**Both figures are required-sample-size estimates under an assumed effect.** They assume the
margin's true value is the observed +0.1357 and that further 400-step trajectories would
resemble these twenty in variability. Neither is a guarantee. If the true margin is smaller than
observed, the requirement rises as its inverse square:

| assumed true margin | n (own statistic) | n (`M-51`'s threshold) |
|---|---|---|
| +0.1357 | 25 | 91 |
| +0.1200 | 31 | 117 |
| +0.1000 | 45 | 168 |
| +0.0800 | 70 | 262 |
| +0.0700 | 91 | 342 |
| +0.0500 | 178 | 669 |

That is why the artifact stores curves and a sensitivity table rather than a number, and why any
sentence the paper writes from this must quote the assumption alongside the figure. The tables here
are read from `results/q2_free_baseline_power.json`.

### The binding test is the margin, not the partial

`e7_free_baselines.py` records a baseline as beaten only if **both** its margin and its partial
correlation clear their thresholds. For step-size the partial already clears at n = 20 —
+0.5430 against 0.1131 — and only the margin does not. So the quantity a larger
sample would have to settle is the raw margin, and that is the one inverted here.

---

## Q1 — How many public repositories carry the construction *and* train it against a sampled squared error?

**The referee's stake in it.** §6.3 derives the σ = 0 optimum from an objective rather than a bug,
and §2 states as an **untested hypothesis** that any descendant of the PETS parameterisation which
replaced the likelihood with a sampled squared error inherits the same optimum. The referee asked
for a count, noting it would widen the result's reach at almost no cost.

**It does not widen it. It narrows it, and that is the finding.**

> Of **10** repositories examined on 2026-09-20 under the protocol in
> `/Users/Shared/rwm_verify/evidence/A2/protocol.md`, **10** carry the
> construction and **1** of those trains it against a sampled squared error.

The protocol was written and frozen **before the search**, precisely so that this number could
not be improved by widening the criteria once the answer was visible. Its sha256 is recorded
beside it in `evidence/A2/protocol.sha256`, in the block's `STATE.json`, and in
`results/q1_pets_descendants.json` itself; if the file and that hash disagree, the survey is
void.

### What was examined, and what each does with the head

| repository | commit read | construction | loss | verdict |
|---|---|---|---|---|
| `kchua/handful-of-trials` | `77fd8802cc` | `dmbrl/modeling/models/BNN.py:414` | `dmbrl/modeling/models/BNN.py:440` | **DOES NOT INHERIT** |
| `quanvuong/handful-of-trials-pytorch` | `672d32f9fa` | `config/halfcheetah.py:86` | `MPC.py:237` | **DOES NOT INHERIT** |
| `Xingyu-Lin/mbpo_pytorch` | `fe3c78c474` | `model.py:142` | `model.py:168` | **DOES NOT INHERIT** |
| `facebookresearch/mbrl-lib` | `3f93cccfc8` | `mbrl/models/gaussian_mlp.py:152` | `mbrl/models/gaussian_mlp.py:300` | **DOES NOT INHERIT** |
| `nirbhayjm/va_mbpo` | `203ea3e5bd` | `mbrl/models/gaussian_mlp.py:158` | `mbrl/models/gaussian_mlp.py:340` | **INHERITS** |
| `Shylock-H/COMBO_Offline_RL` | `239cce768b` | `dynamic/ensemble_dynamics.py:139` | `dynamic/transition_model.py:103` | **DOES NOT INHERIT** |
| `yihaosun1124/pytorch-mopo` | `33a81aae8b` | `models/tf_dynamics_models/bnn.py:647` | `models/tf_dynamics_models/bnn.py:688` | **DOES NOT INHERIT** |
| `junming-yang/mopo` | `2c9431e44b` | `models/ensemble_dynamics.py:138` | `models/transition_model.py:123` | **DOES NOT INHERIT** |
| `yihaosun1124/OfflineRL-Kit` | `3962aa8709` | `offlinerlkit/modules/dynamics_module.py:25` | `offlinerlkit/dynamics/ensemble_dynamics.py:192` | **DOES NOT INHERIT** |
| `polixir/OfflineRL` | `ea1a446b21` | `offlinerl/outside_utils/modules/dynamics_module.py:25` | `offlinerl/algo/modelbase/model_base.py:325` | **DOES NOT INHERIT** |

Nine of the ten keep PETS's Gaussian negative log-likelihood, whose log-σ term is exactly what
opposes σ → 0. `COULD NOT DETERMINE` was available as a verdict and was not needed: every loss
was locatable in source.

### The one that inherits, and the qualification it carries

`nirbhayjm/va_mbpo` at `203ea3e5bd` is a fork of `mbrl-lib` adding a value-aware loss.
With `deterministic=False` — the branch in which the bounded construction *is* applied — and
`model_loss_type='va'`, `_va_loss` builds `Normal(mean, exp(0.5*logvar))` from the bounded head,
draws a **reparameterised** sample with `rsample()`, and scores it with `F.mse_loss` on the reward
dimension and a squared model-advantage through the critic on the state dimensions. **There is no
log-σ term anywhere in that objective** — the construction §6.3 shows has its optimum at σ = 0.

**The qualification, which the count must carry:** it inherits *in its value-aware mode*, which is
an option and not the default. `model_loss_type` defaults to `'mle'` throughout and is threaded
from `cfg.overrides.model_loss_type` in `mbrl/algorithms/mbpo.py`; under `'mle'` the same file
uses the Gaussian NLL and does not inherit.

### The trap this survey had to avoid, because it would have inverted the answer

Several of these repositories offer an `inc_var_loss=False` or `deterministic=True` path that
scores MSE **against the predicted mean**. That does *not* satisfy the inclusion test, and the
distinction is the whole content of §6.3: squaring the *mean's* error gives σ no gradient at all,
so σ is merely untrained, whereas squaring a *draw's* error makes σ = 0 the optimum. In
`mbrl-lib`'s deterministic branch `forward()` returns before the construction is even applied. A
survey matching on "MSE" alone would have counted most of this list as inheriting.

### Looked at and excluded because the construction is absent

| repository | commit read | why |
|---|---|---|
| `johannesnauta/pytorch-pne` | `c3eacc0b01` | Uses softplus to make a variance positive (models/pnn.py), not the double-softplus clamp between two LEARNABLE bounds. Different construction. |
| `leggedrobotics/robotic_world_model` | `14dbfe9da3` | The Isaac Lab extension of the paper under reproduction. No softplus appears in any of its 44 Python files: the dynamics head lives in its rsl_rl dependency, not in this repository. Relevant to referee Q4 as well, and consistent with what block A1 found there. |
| `leggedrobotics/rsl_rl` | `857de6165c` | Mainline rsl_rl. Its only softplus use is a Beta policy distribution in rsl_rl/modules/distribution.py. The bounded log-sigma dynamics head exists in the rwm FORK this paper pins, not in the mainline library -- which narrows the construction's reach rather than widening it. |

The third is worth a sentence in its own right: **the bounded log-σ dynamics head is not in
mainline `rsl_rl`.** It exists in the RWM fork this paper pins. Mainline's only `softplus` is a
Beta policy distribution. That narrows the construction's reach rather than widening it. The
second is the Isaac Lab extension block A1 identified for Q4, and it carries no `softplus` in any
of its 44 Python files.

The subject of this reproduction — the pinned `rsl_rl_rwm` fork — inherits by construction and is
recorded in the artifact **separately and not counted**: counting the thing §6.3 measured as
evidence that the result travels would be circular.

### What this licenses the paper to say, and what it does not

**It does not touch §2's hypothesis as a statement of mechanism.** §2 asserts a conditional — that
a descendant *which made the substitution* inherits the optimum — and this survey tested no
mechanism in any repository. What it bears on is **reach**: how often the antecedent holds. The
honest reading is that the substitution is **rare** in this lineage rather than common, so a
reader of §2 who infers broad reach is inferring more than the evidence supports, and §2 should
say so.

**And it must be stated as a count over what was examined, never over a population.** No claim is
made about how many such repositories exist or what fraction of the field they are. GitHub code
search and web search rank and truncate; this is a sample of convenience, capped at 25 by the
protocol and stopped at 10.

### Re-running it

`scripts/q1_pets_descendants.py --verify` re-fetches every cited file **at its cited commit** and
confirms the recorded line still contains the recorded text. All 20 citations
verified on 2026-09-20; the artifact records the run under `verification`, with `citations_checked`
and `citations_still_valid`, so a reader can see whether the copy they hold was produced by a
verifying run or not. The verdicts themselves are readings of source and no script can
re-derive them; what a script can check is that the citations have not drifted, and that is what
it checks.

---

## Q3 — Is there a cheaper proxy for the downstream cost, one that needs no policy?

**The referee's stake in it.** §11 says this work cannot state what the miscalibration costs
downstream, because no policy is trained and Appendix D prices the penalty ablation as needing a
simulator. The referee asked whether a proxy exists that needs no policy at all — for instance
the fraction of candidate actions whose ranking changes under the corrected penalty.

**One does, it was pre-registered before it was computed, and it returns
`DOES NOT REORDER` — worth exactly what its bound says it is worth and not a point more.** The
rule is `M-70`, committed in `6b87e325d6` before any
part of the statistic existed; the block that computed it set that entry's `Status` line and
changed nothing else.

### The trap the rule was written against

Within a single horizon the correction is `u → c·u` with `c > 0`, a monotone transform, which
cannot change any ranking. **A proxy comparing states at the same rollout depth is therefore
guaranteed to find nothing**, and finding nothing there would mean the measurement was ill-posed
rather than that the correction is harmless. What the correction changes is the relative weight
*across* depths, so the statistic is the penalty accumulated *along* a rollout:

    P_raw(i)  = Σ_{t=1..368} u_i(t)
    P_corr(i) = Σ_{t=1..368} c_out(i)(band(t)) · u_i(t)

with `u` the scalar epistemic term the penalty actually consumes, and `c_out(i)` the multipliers
fitted on the fold **not** containing trajectory `i`. A pair reorders when the two orderings
disagree, and `f` is the fraction of the `C(4,2) = 6` pairs that do.

### What was returned

Every figure in this section is read from `results/q3_penalty_reordering.json`, written by
`scripts/q3_penalty_reordering.py`, with a plain-text copy in
`results/q3_penalty_reordering_report.txt`.

| episode | P_raw | P_corr |
|---|---|---|
| 1 | 138.9085 | 4933.8594 |
| 1 | 193.1991 | 6837.8999 |
| 8 | 223.2785 | 8626.9130 |
| 8 | 205.9811 | 8188.6766 |

**6 pairs defined, 0 undefined,
0 reordering. f = 0.0**, with a 95% cluster-bootstrap interval
over whole trajectories of [0.0000,
0.0000] at n_independent =
4. That is branch 2 of the rule's three, returned as the rule words it.

**That interval is degenerate by construction and is not corroboration.** Resampling
trajectories creates no new pairs — every pair from a resample is one of the original six,
with its reorder flag already fixed — so with none reordering, no resample can return a
non-zero `f`. Exhaustively: of all 256 resamples 4 are discarded and **all 252 admissible
ones return `f = 0`**. The interval condition in the rule's two directional branches can
therefore never fail, and branch 2 reduces to `f = 0` alone. It is also *narrower* than
`M-70`'s own design table predicted — `[0.0000, 0.4593]` for 0 of 6, which the rule said
would itself understate the true width. The verdict is unaffected; the interval simply
carries no information. It is not a further way the null could have been forced — `f = 0` was
already fixed by the six pairs before any resampling — but a condition that could not have
failed, reported as though it could. The defect is recorded at ledger entry `M-71`.

### The correction is not flat, so that route to a hollow null is closed

`M-70` requires the spread of the multipliers beside the verdict, because if the six barely
differed across bands then this branch would be close to forced and its licence would read as a
finding. They differ by **9.31×** across
horizons. The design could have produced reordering and did not.

### But the null is partly structural, and a reader must be told so

*The diagnostic in this subsection was **not** required by `M-70`. It was computed after the
verdict, changes no branch and no figure, and is reported because it cuts against the finding
rather than for it.*

The `c` spread is not the only way a null here could be hollow. The six horizons partition the
rollout very unevenly, and the accumulated penalty is dominated by the longest band:

| band | steps | share of the raw penalty | share of the corrected penalty |
|---|---|---|---|
| 1 | 1 | 0.17% | 0.02% |
| 8 | 7 | 1.21% | 0.25% |
| 32 | 24 | 4.59% | 1.62% |
| 100 | 68 | 16.85% | 10.35% |
| 128 | 28 | 8.88% | 6.40% |
| 368 | 240 | 68.31% | 81.35% |

**81.35% of the corrected penalty sits in the single band
h = 368**, which holds
240 of the
368 steps — and the overall ordering of `P_corr` is **exactly** that
band's ordering. So both orderings are largely that band's ordering, and the per-horizon
variation acts mostly on bands carrying less than a fifth of the mass. The verdict is what the
rule returned and it stands exactly as stated; what is narrower than
it first reads is what the result licenses about the correction's **power** to reorder — this
arena gave the per-horizon weights little room to act, so the null is weaker evidence of
harmlessness than the bare verdict suggests. The paper must say so.

### The bound, which binds this verdict as `M-70` binds every branch

**No reward function is available in this work.** `Σ_t u(t)` is the **penalty component alone**,
not the penalised return `r̃ = r − λu`. Whether a changed ordering of the penalty component
changes the ordering of the return depends on the scale of `r` relative to `λu`, and this project
has neither `r` nor a tuned `λ`. **This verdict is therefore a bound on what the correction could
do downstream, never a measurement of what it costs**, and it licenses no statement about policy
performance, about learned behaviour, or about the size of any downstream effect.

### What was recomputed, and under what permission

`u` is stored nowhere: §6.8's own script computes it and discards it. `M-70` carries a permission,
ruled on 2026-09-20 before the rule was committed, for **one deterministic re-derivation** —
one `rollout_uncertainty` call per held-out episode on the released checkpoint at
`start_step = 32`, `action_offset = 1`, batched exactly as §6.8 batches it. Nothing was trained or
fitted; the multipliers were read from `results/task_d3_perhorizon.json`.
