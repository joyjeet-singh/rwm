# RWM Reproduction — Findings Ledger

**Target.** Li, Krause, Hutter, *Robotic World Model*, arXiv 2501.10100.
**Reproduction scope.** Proprioceptive dynamics model only. No vision, no exteroception, no hardware.
**Reference artifacts.**

| Item | Identifier |
|---|---|
| `robotic_world_model_lite` | commit `13a798e9d35dabf12c0e6e02977b25ec64dfb2bd` |
| `rsl_rl_rwm` | commit `18eebcdd7145284c8d5eed5d8ed1a4b96c649693` |
| `state_action_data_0.csv` | sha256 `1b2e00b8…9e78921` |
| `pretrain_rnn_ens.pt` | sha256 `2ac8686c…52c6e5a` |
| Licence | Apache 2.0, both repos |

**Status.** Steps 0–3.5 complete. Step 4 (trainer) unblocked. Last updated: 16 Aug 2026.
**Environment.** Intel Mac x86_64, CPU only, torch 2.2.2, numpy 1.26.4, Python 3.11.15. Neither repo installed (`setup.py` pins torch ≥ 2.7 + CUDA); config and modules loaded via `importlib`.

---

## How to use this file

**Claim IDs are permanent.** Once assigned, an ID is never reused and never edited in place. If a claim turns out to be wrong, set its status to `SUPERSEDED`, add a pointer to the ID that replaces it, and write the replacement as a new entry. The record of having been wrong is part of the research output.

**Prefixes**

| Prefix | Meaning |
|---|---|
| `D-` | Property of the dataset |
| `C-` | Gap between what the paper says and what the code does |
| `B-` | Defect in the reference implementation |
| `M-` | Methodological finding about how to evaluate this |
| `R-` | Measured result |
| `O-` | Open question |
| `X-` | Deviation we deliberately introduced |
| `S-` | Superseded claim, retained for the record |

**Evidence classes**

| Class | Meaning |
|---|---|
| `SRC` | Read directly from reference source; file and line recorded |
| `DATA` | Measured from the CSV by our own script |
| `RUN` | Produced by our own evaluation run; artifact recorded |
| `EXT` | External corroboration (upstream docs, another codebase) |
| `INFER` | Reasoned, not directly measured. **Never promote to a paper claim without a `SRC`, `DATA`, or `RUN` entry backing it** |

**Paper relevance**

| Tag | Meaning |
|---|---|
| `CONTRIB` | Candidate contribution of the reproduction paper |
| `METHOD` | Belongs in the methods section |
| `CONTEXT` | Background; probably a footnote |
| `INTERNAL` | Project hygiene; not for publication |

---

## Step 3.5 changes at a glance

| ID | Was | Now |
|---|---|---|
| O-01 | OPEN | **RESOLVED — k = −1** (D-13) |
| O-02 | OPEN | **RESOLVED** — convention mismatch (R-09) |
| O-03 | OPEN | **RESOLVED** — bitwise identical (R-11) |
| O-04 | OPEN | **RESOLVED** — units established; R-08 explained by C-10 |
| O-05 | OPEN | **RESOLVED** — causal, not leakage (D-13) |
| O-07 | OPEN | **PARTIALLY RESOLVED** — M-07, R-10 |
| M-02 | PENDING VERIFICATION | **CONFIRMED** (R-12) |
| M-07 | PENDING VERIFICATION | **CONFIRMED** (R-10) |
| M-08 | CONFIRMED (defect in our harness) | **FIXED** (R-12) |
| C-08 | UNVERIFIED | **SUPERSEDED by C-09** |
| B-05 open note | ambiguous | **closed** — training alignment is the causal one |
| — | — | **New:** D-13, C-09, C-10, M-09–M-11, R-09–R-13, X-05, S-07, S-08 |

---

## A. Dataset findings

### D-01 — Column layout confirmed
Columns 0–2 base linear velocity, 3–5 base angular velocity, 6–8 projected gravity, 9–20 joint positions, 21–32 joint velocities, 33–44 joint torques, 45–56 actions, 57–64 contacts, 65 termination.
**Evidence** `SRC` `train.py:54-58`; `DATA` ‖gravity‖ deviates from 1 by at most 6.2e-07 across all 10,000 rows.
**Status** CONFIRMED · **Relevance** METHOD

### D-02 — Contact channel ordering
Columns 57–60 are **thigh** contacts, 61–64 are **foot** contacts.
**Evidence** `SRC` `anymal_d_flat.py:84`.
**Status** CONFIRMED · **Relevance** METHOD
**Note** An earlier working assumption of "knee then foot" was wrong; corrected before any use.

### D-03 — The termination column is identically zero
Zero terminations across 200 seconds. The ten resets are 20-second time-limit truncations, not failures. The robot never falls in this recording.
**Evidence** `DATA` column 65 all-zero, asserted on every load.
**Status** CONFIRMED · **Relevance** CONTRIB
**Consequence** The termination head cannot be trained on this data — see X-04.

### D-04 — Ten unmarked episode boundaries
Resets at rows 999, 1999, 2999 … 9999. Segments: 999 rows, then nine of 1000, then a one-row stub at 9999 which is discarded.
**Evidence** `DATA` derived structurally, re-derived and asserted on every load.
**Status** CONFIRMED · **Relevance** CONTRIB

### D-05 — Reset fingerprint
At every boundary row, all 12 joint velocities, the 4 HAA joint positions, and all 12 actions are **exactly** zero. This combination occurs at those ten rows and nowhere else in 10,000. Within-episode maximum adjacent-row joint change is 0.253 rad (p99 0.171); every reset-crossing pair exceeds it, maximum 0.676.
**Evidence** `DATA`; `INFER` consistent with Isaac Lab's zero joint-velocity reset range and zero HAA default.
**Status** CONFIRMED · **Relevance** METHOD
**Extended by D-13** — the exactly-zero *action* at these rows turned out to be the decisive evidence for the action convention.

### D-06 — Usable window count
9,609 valid 40-step windows once episode resets are respected, against 9,961 if the termination column is trusted. The 352 difference are windows that splice one episode's end onto another's start.
**Evidence** `DATA`.
**Status** CONFIRMED · **Relevance** CONTRIB

### D-07 — Actions are not joint targets in radians
No action scale exists anywhere in either repo; it lives in the upstream Isaac Lab environment and was never recorded. Empirically the action leads joint position by 4 steps (80 ms, r ≈ 0.74–0.85) with median gain 0.35, swinging about 2.9× wider than the joint motion it produces. Per-column raw standard deviations range 0.244 to 0.598.
**Evidence** `DATA`; `SRC` absence confirmed by search across both repos.
**Status** CONFIRMED · **Relevance** CONTRIB
**Consequence** Interacts with C-07 — the noise sweep perturbs actions and states on incomparable scales. Also the root cause of M-10, and it now has a recovered numeric estimate: see D-13's implied scale ≈ 0.46.

### D-08 — A single gait throughout
Clean trot: diagonal pairs in antiphase, diagonal co-contact at 1.7× chance and all non-diagonal pairings suppressed to 0.28–0.35×. Stride 27 steps (0.54 s, 1.85 Hz), identical across all four feet. Duty factor 52.6–55.2%, two feet down 84.4% of the time.
**Evidence** `DATA`.
**Status** CONFIRMED · **Relevance** CONTEXT

### D-09 — One thigh contact in the entire file
Column 59, row 7039 (t = 140.78 s): right-front thigh, one step, all four feet also down, no termination. A scuff. Thigh contact is a reward penalty in this environment, not a termination condition.
**Evidence** `DATA`; `SRC` `anymal_d_flat.py`.
**Status** CONFIRMED · **Relevance** CONTEXT

### D-10 — Twenty commanded-velocity regimes, not one
Two commands per episode, each held ~500 steps (10 s), changing at the midpoint of every one of the ten episodes. All 20 regimes distinct at 0.10 m/s tolerance, spanning roughly [−0.95, +0.90] × [−0.97, +0.87] m/s.
**Evidence** `DATA` change-point detection on stride-smoothed velocity, W=150, threshold 0.25 m/s; `EXT` matches Isaac Lab's default `resampling_time_range` of 10 s for velocity commands with a 20 s episode length.
**Status** CONFIRMED · **Relevance** CONTRIB
**Consequence** A held-out episode is **not** a near-duplicate of a training episode. The split tests generalisation across velocity commands — though within one gait and one terrain only.

### D-11 — The config's resample interval does not describe this data
`command_resample_interval_range = [100, 120]` in `anymal_d_flat_cfg.py` implies a command change every 2–2.4 s. The observed interval is ~500 steps. That field belongs to the imagination environment used for model-based policy training, not to whatever recorded the CSV.
**Evidence** `SRC` + `DATA`.
**Status** CONFIRMED · **Relevance** METHOD

### D-12 — Per-episode difficulty varies threefold and is not explained by speed
Rollout error by episode spans 0.601 to 1.674 (mean 1.097), measured with 20 trajectories per episode under an identical protocol. Correlation with mean commanded speed: r = +0.00.
**Evidence** `RUN` `step3_report.txt`.
**Status** CONFIRMED · **Relevance** CONTRIB
**Consequence** Stratifying a split by commanded speed does not balance difficulty. See M-05.

### D-13 — Row *t* holds the action that **produced** state[*t*] (k = −1) · **NEW**
The recorded action in row *t* is not the action applied at *t*; it is the action responsible for the state in row *t*. Equivalently, row *t* = (post-step observation, action buffer).

Four tests were run; three could not separate the hypotheses and the fourth is decisive.

| Test | Method | Peak | Strength |
|---|---|---|---|
| 1 | ridge `a[t] ~ s[t+k]`, k ∈ {−2…+2}, 8 train episodes → held-out R² on {1,8}, alpha swept 1e−3…1e4 | k = **+1** (0.9691) | **Confounded** — neither hypothesis. See M-10 |
| 1b | PD law `tau[t] ~ a[t+m], q[t], qdot[t]`, per joint | m = **−1** (0.898 vs 0.869) | Weak — gap 0.029; ANYmal uses a learned actuator net, so a linear PD is misspecified |
| 1c | the checkpoint's own actor, obs layout from `anymal_d_flat.py:53` | k = **−1** (0.486 vs 0.391) | Weak — the actor is not the collection policy (R-13) |
| 1d | **refutation from the reset rows** | k = **−1** | **Decisive** |

The decisive argument: reset rows carry the *post-reset* state (D-05) and their action columns are bitwise 0.0 — the only 10 such rows in 10,000. Under k = 0 the row would have to contain π(post-reset state); a continuous MLP with biases cannot emit bitwise 0.0 on 12 outputs at 10 different randomised reset states (the available actor emits mean |π| = 0.547 there, smallest single output 4.9e-03). **k = 0 is refuted.** Under k = −1 the reset row holds the action that produced the reset state — none did, and Isaac Lab zeroes the action buffer on reset. Consistent.

Byproduct: test 1b recovers an implied action scale of **0.461 ± 0.013** across the 12 joints (from −c₁/c₂), the first numeric estimate of the quantity D-07 records as unrecorded. Close to Isaac Lab's ANYmal default of 0.5.

**Evidence** `DATA` `task1_action_convention.py`, `task1b_pd_law.py`, `task1c_policy_test.py`, `task1d_reset_argument.py`; `SRC` `anymal_d_flat.py:53`, `base_cfg.py:118-120`.
**Status** CONFIRMED · **Relevance** CONTRIB
**Resolves** O-01, O-05. **Refutes** the leakage reading — see S-07. **Determines** X-05.

---

## B. Defects in the reference implementation

### B-01 — The window builder cannot see the episode resets
`train.py:134` derives `reset_indices` from `termination_data.nonzero()`. Because column 65 is identically zero (D-03), that comes back empty, the guard is always False, and all 9,961 windows are marked valid — including the 352 that splice episodes. The released pipeline, run on the released data, trains on physically impossible transitions.
**Evidence** `SRC` `train.py:134-144`; `DATA` D-06.
**Status** CONFIRMED · **Relevance** CONTRIB
**Impact** Not yet quantified. Measuring the effect of the 352 contaminated windows on final model quality is a candidate experiment for Step 6 (O-06).

### B-02 — Latent falsy-index bug in the same guard
`any(reset_indices[mask])` tests the *values* for truthiness rather than whether any indices matched. A reset at timestep 0 has value 0, which is falsy, so it would be missed even in a dataset that did mark terminations.
**Evidence** `SRC` `train.py:141`.
**Status** CONFIRMED · **Relevance** CONTRIB
**Note** Latent here — this dataset has no reset at index 0 — but it would bite any dataset that does.
**Line-number correction (Step 3.5)** The `any(...)` call is at **`train.py:143`**, not 141; 141 is `valid_indices = []`. The claim is unaffected. Re-read and confirmed at commit `13a798e9`.

### B-03 — Train/test split leaks
`model_training.py:33` calls `random_split` over the **window** dataset. Adjacent windows share 39 of their 40 rows, so the test set is almost entirely contained in the training set.
**Evidence** `SRC` `model_training.py:33`.
**Status** CONFIRMED · **Relevance** CONTRIB

### B-04 — Evaluation trajectories are drawn from training data
`train.py:109` builds the eval trajectory config from the full `state_data` before any split, and samples start points with `randint` over all 10,000 rows. So eval trajectories sit inside the training set and cross episode resets freely.
**Evidence** `SRC` `train.py:81-97, 109`; `RUN` 5 of 10 protocol-B trajectories crossed a reset.
**Status** CONFIRMED · **Relevance** CONTRIB
**Consequence** There is no held-out evaluation anywhere in the released repository.

### B-05 — Training and evaluation use different action alignments
Training pairs `(s[t], a[t+1]) → s[t+1]`; evaluation pairs `(s[t], a[t]) → s[t+1]`. The released checkpoint was fit under one convention and is scored under the other.
**Evidence** `SRC` `system_dynamics.py:196-200` and `model_training.py:131-132`, both read directly.
**Status** CONFIRMED · **Relevance** CONTRIB
**Open** ~~Which convention is causally correct is O-01. Under one reading the training convention leaks the target; under the other it is correct and the evaluation convention is stale by a step.~~
**CLOSED at Step 3.5 by D-13.** The **training** alignment is the causal one; the **evaluation** alignment is stale by one step. The defect is therefore in the evaluation path, not the training path: the released checkpoint is scored on an input it was never trained to use, and the reported autoregressive error is correspondingly pessimistic (R-09). This *strengthens* B-05 as a contribution — it is not merely an inconsistency, it is a measurable understatement of the released model's quality.

---

## C. Paper-versus-code gaps

### C-01 — The loss has seven terms, not two
Equation 2 of the paper shows an observation term and a contact term. The code computes state, sequence, bound, KL, extension, contact and termination losses, weighted 1.0 / 1.0 / 1.0 / 0.1 / 1.0 / 1.0 / 1.0.
**Evidence** `SRC` `system_dynamics.py` loss assembly; `base_cfg.py` weights.
**Status** CONFIRMED · **Relevance** CONTRIB

### C-02 — The mean head is residual
`state_mean = self.state_mean_layers(x) + x_state_batch[:, -1]`. The network predicts a **delta** from the last observed state, not the absolute next state. The paper does not mention this.
**Evidence** `SRC` `mlp.py:88`, read directly.
**Status** CONFIRMED · **Relevance** CONTRIB
**Consequence** The hold-last baseline is not an arbitrary floor — it is exactly this model with its delta head zeroed. See M-02, now verified by R-12c.

### C-03 — Two GRU trunks, not one
`state_base` and `auxiliary_base` are separate two-layer GRUs, each taking the same 57-dim input. Table S7 of the paper describes a single base.
**Evidence** `SRC` checkpoint tensor inventory; `system_dynamics.py:95`.
**Status** CONFIRMED · **Relevance** CONTRIB

### C-04 — The "ensemble of 5" shares both trunks
Only the output heads are duplicated. Epistemic uncertainty therefore measures head disagreement over identical features, not deep-ensemble diversity.
**Evidence** `SRC` checkpoint inventory — `state_base` and `auxiliary_base` appear once, heads appear five times; `system_dynamics.py:114`.
**Status** CONFIRMED · **Relevance** CONTRIB

### C-05 — Training samples, inference takes the mean
Training uses a reparameterised sample (`randn_like(mean) * std + mean`, `system_dynamics.py:215`). Inference returns `state_means.mean(0)` and feeds that back. The two paths differ and the paper describes neither.
**Evidence** `SRC` `system_dynamics.py:114, 215`.
**Status** CONFIRMED · **Relevance** CONTRIB
**Note (Step 3.5)** C-10 makes this asymmetry almost inconsequential in practice: the sampled noise at training time has σ ≈ 6e-5 per dimension, so the "sample" is numerically almost the mean anyway.

### C-06 — Learnable bounded log-standard-deviation
`max = min_logstd + exp(log_delta_logstd)`, then `logstd = max − softplus(max − logstd)`, then `logstd = min + softplus(logstd − min)`. Both bounds are learned parameters, regularised by the bound loss. Absent from the paper.
**Evidence** `SRC` `mlp.py:91-93, 97`.
**Status** CONFIRMED · **Relevance** CONTRIB
**Consequence discovered at Step 3.5** This mechanism has collapsed in the released checkpoint — see C-10.

### C-07 — Actions are not normalised
`action_data_mean` is all zeros and `action_data_std` all ones, so actions pass into the network raw while states are normalised by real per-dimension constants.
**Evidence** `SRC` `anymal_d_flat_cfg.py`.
**Status** CONFIRMED · **Relevance** CONTRIB
**Consequence** With D-07, a noise scale of *s* perturbs actions by *s* in raw units while perturbing states by *s* in units of each state's own standard deviation. The noise sweep is not comparable across the two.

### C-08 — Forecast decay is inert
The paper's loss includes a decay factor α over the forecast horizon. The configured value is 1.0, so the term has no effect in the released setup.
**Evidence** `INFER` from an early read of the paper's Table S7.
**Status** **SUPERSEDED BY C-09** — the premise was wrong. There is no decay parameter to configure.

### C-09 — There is no forecast decay factor in the implementation at all · **NEW**
The forecast loop accumulates one unweighted loss per forecast step and reduces with a plain mean: `state_loss = torch.mean(torch.cat(state_losses, dim=0), dim=0)`. No α, no per-step weight, no configurable decay exists anywhere in `system_dynamics.py`, `base_cfg.py` or `anymal_d_flat_cfg.py`. The only matches for "decay" in the configs are `weight_decay` (optimizer L2) and `gamma` (the PPO discount) — neither is the paper's α.

So the correct statement is not "α is configured to 1.0"; it is that **the term is absent**. Numerically the released behaviour is the same as α = 1, which is why C-08 was plausible, but the paper describes a hyperparameter the code does not have.
**Evidence** `SRC` `system_dynamics.py:186-215` (loop) and `:227-231` (reduction); exhaustive grep across both config files.
**Status** CONFIRMED · **Relevance** CONTRIB
**Supersedes** C-08.

### C-10 — The aleatoric variance head has collapsed to a constant · **NEW**
In the released checkpoint the learned bounding interval for the log-standard-deviation has closed to zero width. For all 5 heads and all 45 dimensions:

- `state_log_delta_logstd` = **−14.463** (uniform to 3 dp across every head and every dimension)
- interval width `exp(log_delta_logstd)` = **5.23e-07**, so `max_logstd − min_logstd ≈ 0`
- `min_logstd` ≈ −9.8, hence σ ≈ 5.6e-05 per dimension

Because the double softplus in C-06 clamps the network's logstd output into `[min, max]`, and that interval has zero width, **the predicted standard deviation is a learned constant independent of the input**. The variance head does no work. Summing over 45 dimensions gives 0.0026, which is exactly the aleatoric value observed in R-08 (0.003) — that number is the bound, not a prediction.

Mechanism: `compute_bound_loss` returns `mean(max_logstd) − mean(min_logstd) = mean(exp(log_delta_logstd))`, weighted 1.0 in the total loss. Its gradient w.r.t. `log_delta_logstd` is uniform across entries, and the parameter is initialised to a constant 0.0 (`mlp.py:79`) — which is exactly why all 225 entries decayed to the identical value. Nothing opposes this term once the state loss stops caring about σ.

**Evidence** `DATA` direct inspection of `pretrain_rnn_ens.pt`; `SRC` `mlp.py:78-79, 91-93`, `system_dynamics.py:301-302` (`compute_bound_loss`), `base_cfg.py` bound weight 1.0.
**Status** CONFIRMED · **Relevance** CONTRIB
**Consequence** RWM-**U**'s uncertainty story rests on the epistemic term alone in this checkpoint; the aleatoric channel is degenerate. Combined with C-04 (shared trunks), *both* halves of the uncertainty estimate are weaker than the paper implies. Closes O-04 together with the unit definitions below.
**Step 4 action** Either reduce the bound-loss weight or re-parameterise the interval, and monitor `exp(log_delta_logstd)` during training as a collapse detector.

---

## D. Methodological findings

### M-01 — Episode identity must be carried explicitly
Because of D-03, episode structure cannot be recovered from the data's own termination signal. Every consumer — window builder, split, trajectory sampler — must read a separately derived `episode_id` array.
**Evidence** `DATA` + `SRC`.
**Status** CONFIRMED · **Relevance** METHOD

### M-02 — The hold-last floor is the zero-delta model
A direct consequence of C-02. "Model versus floor" therefore measures exactly one thing: whether the learned delta helps.
**Evidence** ~~`INFER` from C-02. Verification pending as Step 3.5 Task 3c.~~ `RUN` **verified** — zeroing the final Linear of all five `state_mean_layers` heads reproduces the hold-last predictor to 1.192e-07 over 165,600 values, 0 steps above 1e-6. See R-12c.
**Status** **CONFIRMED** (was PENDING VERIFICATION) · **Relevance** CONTRIB

### M-03 — The metric is stable on this data
The relative-L1 denominator was a fragility concern: a normalised true state near zero would make the ratio explode. Not observed. `frac(r > 10)` is 0.0000 in every condition run so far; maximum `r` is about 5.
**Evidence** `RUN` `step3_report.txt`, all 13 conditions.
**Status** CONFIRMED **for the 45-dimensional aggregate only** · **Relevance** METHOD
**Scope narrowed by M-09** — at per-group granularity the metric is *not* stable, and S-04's original concern was correct at that granularity.

### M-04 — Ten trajectories is not enough to support a gap claim
Over 20 seeds: protocol A gives 0.709 ± 0.053, protocol B gives 1.026 ± 0.184. Separation 0.317 against pooled spread 0.191, i.e. 1.7 sigma.
**Evidence** `RUN` `manifest.json`, `seed_averaged`.
**Status** CONFIRMED · **Relevance** CONTRIB
**Consequence** Any single-seed comparison in this project must be reported with a seed sweep behind it.

### M-05 — Speed stratification does not balance difficulty
Follows from D-12. The seed-0 split holds out two of the easiest episodes (pair mean 0.694 against population mean 1.097), so protocol A reads optimistic for reasons unrelated to protocol.
**Evidence** `RUN`.
**Status** CONFIRMED · **Relevance** METHOD
**Decision** The split was deliberately **not** re-picked, because choosing a held-out set by measured error selects on the test signal. Step 6 will use five-fold cross-validation over episode pairs, so every episode is held out exactly once.

### M-06 — Protocol B as defined cannot isolate leakage
The reference checkpoint was trained on the entire CSV, so protocol A's held-out episodes were in its training data. For this checkpoint, protocol A is not a generalisation measure and the A/B gap measures episode sampling, not leakage.
**Evidence** `RUN` + `INFER`.
**Status** CONFIRMED · **Relevance** METHOD
**Decision** For Step 6, redefine protocol B as *trajectories drawn from training episodes only*. A versus B then becomes a clean held-out-versus-seen comparison on a model whose training set we control.

### M-07 — The aggregate metric hides per-group behaviour
Summing absolute error over all 45 dimensions and dividing by summed absolute truth is dominated by whichever group carries the largest normalised magnitude, and saturates near 1.0 at long horizon.
**Evidence** ~~`INFER` from the metric definition plus R-04's compression at long horizon. Measurement pending as Step 3.5 Task 4.~~ `RUN` **measured** — see R-10 for the full table.
**Status** **CONFIRMED** (was PENDING VERIFICATION) · **Relevance** METHOD
**Result** Joint positions carry 42.6–45.0% of the denominator at every horizon (mean |denominator| 13.6 against 1.0–1.5 for the base groups); joint torques carry 25.4–44.7% of the numerator. The aggregate is substantially *"predict joint positions, be graded on torque error."*

### M-08 — The oracle acceptance test passes under any consistent off-by-one
The oracle returns `true_states[:, start_step:]` and the metric compares against the same tensor with the same indices. It verifies arithmetic, not alignment.
**Evidence** `SRC` our own `rollout_eval.py:249-253`.
**Status** **FIXED** (was CONFIRMED) · **Relevance** INTERNAL
**Fix** Step 3.5 Tasks 3a and 3b, both passing — see R-12a, R-12b. Alignment is now pinned by direct index assertion against the raw CSV rather than inferred.

### M-09 — The metric *is* fragile at per-group granularity · **NEW**
Restricting the relative-L1 metric to one state group shrinks the denominator from 45 dimensions to 3 or 12, and the fragility M-03 did not see in the aggregate appears immediately:

| Group | Symptom |
|---|---|
| base angular velocity | mean is **`inf`** from h ≥ 8; 0.9–3.1% of timesteps exceed r > 10 |
| projected gravity | **11.4%** of timesteps exceed r > 10 at h = 368 |
| joint positions / velocities / torques | stable, 0% blow-up at every horizon |

Root cause for gravity specifically: `state_data_std` = (0.02, 0.02, 0.04) about a mean of (0, 0, −1), so in **normalised** space — the only space this metric lives in — gravity is a near-zero-mean quantity with unit spread and carries the smallest denominator of any group (1.361, against 7.290 for torque).
**Evidence** `RUN` `task2_4_results.json`.
**Status** CONFIRMED · **Relevance** METHOD
**Consequence** Any per-group number must be reported as a **median** with a blow-up rate beside it. S-04's concern was right, just at a granularity M-03 never tested.
**Second consequence** The brief's expectation that hold-last should be *strong* on projected gravity is **neither confirmed nor refuted**: measured floor is 1.5473 for gravity against 0.9728 for torque, which inverts the expectation, but that is the normalisation, not the physics. In raw units gravity *is* nearly constant; this metric cannot show it.

### M-10 — Regressing the action on the state cannot identify the recording convention · **NEW**
The prescribed test for O-01 — ridge `a[t] ~ s[t+k]`, peak location decides — is confounded, and its failure mode is instructive. The action is a joint **position target** (D-07), so the joints move toward it and the action necessarily resembles *future* joint states regardless of which convention holds. Twelve of the 45 regressors are joint positions, and D-07 already measured the action leading joint position by ~4 steps at r ≈ 0.74–0.85. That relationship swamps the policy-map signal the test is trying to read.

Observed: the peak lands at **k = +1**, which is neither hypothesis, with a gap to second place of 0.0149 against an alpha-spread of 0.2723. Adding the previous action as a regressor (the prescribed robustness check) does not move the peak — it is confounded, not under-specified.
**Evidence** `RUN` `task1_action_convention.json`.
**Status** CONFIRMED · **Relevance** METHOD
**Generalisation** For position-controlled robots, correlational tests between actions and states cannot establish recording alignment. Use a structural constraint instead (M-11).

### M-11 — Refutation on structural invariants beats correlation for alignment questions · **NEW**
Three statistical tests (M-10, plus the PD-law and policy variants in D-13) all failed to separate the two conventions, each for a different reason. The question was settled by a single **refutation** on an exact structural fact: 120 action values that are bitwise zero at the reset rows, which one hypothesis makes impossible.

The general lesson, and the one worth carrying into Step 4: where a dataset contains exactly-zero or otherwise degenerate rows, those rows encode the recording loop's structure and are often the only assumption-free evidence available. They cost nothing to check and outrank any amount of curve fitting.
**Evidence** `INFER` from D-13's test history.
**Status** CONFIRMED · **Relevance** METHOD

---

## E. Measured results

Steps 0–3 from `step3_report.txt` and `manifest.json`; Step 3.5 from `task*_report.txt` and `task*.json`. torch 2.2.2, CPU. Step 3 wall clock 43.7 s; all Step 3.5 tasks together well under the ten-minute budget.

### R-01 — Checkpoint inventory
1,995,569 parameters: `state_base` 636,672, `state_heads` 387,460, `auxiliary_base` 636,672, `auxiliary_heads` 334,765. Checkpoint iteration 5000. Loads under torch 2.2.2 with no fallback.
**Status** CONFIRMED · **Relevance** METHOD

### R-02 — Protocol A and B, clean
Seed 0: A = 0.7672, B = 1.2728. Seed-averaged over 20 seeds: A = 0.709 ± 0.053, B = 1.026 ± 0.184.
**Status** CONFIRMED · **Relevance** CONTRIB
**Caveat** Read with M-06. The gap is episode sampling, not leakage.

### R-03 — Hold-last floor
e = 1.0070, median r = 0.9649.
**Status** CONFIRMED · **Relevance** CONTRIB
**Note** Convention-independent — the predictor uses no actions — so it is reused unchanged in R-09.

### R-04 — Error by forecast horizon, protocol A clean
Under the **evaluation** convention (`action_offset=0`).

| h | model | floor | ratio |
|---|---|---|---|
| 1 | 0.1209 | 0.1107 | **1.093** |
| 4 | 0.1612 | 0.2407 | 0.670 |
| 8 (training horizon) | 0.1806 | 0.3603 | 0.501 |
| 16 | 0.2279 | 0.5309 | 0.429 |
| 32 | 0.3150 | 0.5733 | 0.549 |
| 64 | 0.4467 | 0.6787 | 0.658 |
| 128 | 0.5522 | 0.7542 | 0.732 |
| 256 | 0.6732 | 0.9369 | 0.719 |
| 368 | 0.7672 | 1.0070 | 0.762 |

**Status** CONFIRMED · **Relevance** CONTRIB
**Note** The model is worse than the hold-last floor at one step, best at h=16, and converges back toward the floor thereafter. The h=1 result was the subject of O-02 — **now explained, see R-09.** These numbers remain correct for the stale convention; R-09 supersedes them as the headline figures.

### R-05 — Boundary crossing does not inflate error
Of 10 protocol-B trajectories, 5 crossed a reset. Crossing trajectories averaged 0.947; non-crossing averaged 1.599. The crossing trajectories scored **better**.
**Status** CONFIRMED · **Relevance** CONTRIB
**Note** This refutes S-03. Recorded because a stated prediction being falsified by measurement is itself a result.

### R-06 — Convention swap is worth 0.066
Protocol A: 0.7672 under the evaluation convention, 0.7008 under the training convention.
**Status** CONFIRMED · **Relevance** CONTRIB
**Caveat** ~~Not yet interpretable — see O-01 and O-05.~~ **Interpretable as of D-13:** the training alignment is causal, so the 0.066 is the cost the reference evaluation pays for feeding a stale action. It is a measurement of the B-05 defect, not evidence of leakage.

### R-07 — Protocol B's noise sweep is non-monotonic
Protocol A rises cleanly with noise: 0.767, 0.886, 1.005, 1.220, 1.255, 1.381. Protocol B does not: 1.273, 1.229, 1.230, 0.977, 1.030, 1.213.
**Status** CONFIRMED · **Relevance** CONTRIB
**Note** Most likely sampling variance swamping the effect, consistent with M-04's ±0.184 on protocol B. Not yet tested.

### R-08 — Epistemic uncertainty dwarfs aleatoric
One-step check on a held-out window: aleatoric 0.003, epistemic 0.276, roughly a hundredfold ratio.
**Status** CONFIRMED as a measurement · **Relevance** CONTRIB
**Caveat** ~~Units and normalisation of the two quantities not yet established. Do not interpret until O-04 is closed.~~ **O-04 closed.** Both are sums over the 45 normalised state dimensions and are directly comparable: aleatoric = `state_stds.mean(0).sum(1)`, epistemic = `state_means.std(0).sum(1)` (`system_dynamics.py:126-127`). The ratio is real, but the reason is C-10: the aleatoric figure is the collapsed lower bound (Σ exp(min_logstd) = 0.0026 ≈ the 0.003 observed), not a learned prediction.

### R-09 — Error by forecast horizon under the causal convention · **NEW**
Protocol A, clean, `action_offset=1` (the training alignment, established causal by D-13). Floor reused from R-03.

| h | eval conv (R-04) | ratio | **train conv** | **ratio** | floor |
|---|---|---|---|---|---|
| 1 | 0.1209 | 1.093 | **0.0915** | **0.827** | 0.1107 |
| 4 | 0.1612 | 0.670 | 0.1144 | 0.475 | 0.2407 |
| 8 | 0.1806 | 0.501 | 0.1310 | 0.364 | 0.3603 |
| 16 | 0.2279 | 0.429 | 0.1808 | **0.341** | 0.5309 |
| 32 | 0.3150 | 0.549 | 0.2609 | 0.455 | 0.5733 |
| 64 | 0.4467 | 0.658 | 0.3751 | 0.553 | 0.6787 |
| 128 | 0.5522 | 0.732 | 0.5096 | 0.676 | 0.7542 |
| 256 | 0.6732 | 0.719 | 0.6387 | 0.682 | 0.9369 |
| 368 | 0.7672 | 0.762 | **0.7008** | 0.696 | 1.0070 |

**Status** CONFIRMED · **Relevance** CONTRIB
**Resolves O-02.** The h=1 ratio falls from 1.093 to **0.827**, a 24% drop in one-step error. The model beats the floor at **every** horizon under the causal alignment. The anomaly was the convention mismatch, not a model defect — the released checkpoint is better than the released evaluation reports.
**Note** Best ratio is still at h=16 (0.341), and convergence toward the floor at long horizon persists under both conventions, so O-07 is only partly a convention artefact.

### R-10 — Per-state-group breakdown · **NEW**
Protocol A, clean, causal convention. Blow-up rates and medians per M-09; `inf` entries are real, not formatting.

**h = 8 (training horizon)**

| Group | model | floor | ratio | med ratio | num share | den share |
|---|---|---|---|---|---|---|
| base lin vel | 0.6778 | 0.2706 | 2.505 | 0.666 | 4.6% | 2.9% |
| base ang vel | inf | inf | — | 0.386 | 8.7% | 2.8% |
| proj gravity | 0.1798 | 0.4978 | 0.361 | 0.258 | 6.4% | 6.2% |
| joint pos | 0.0566 | 0.1934 | 0.293 | 0.143 | 16.0% | 45.3% |
| joint vel | 0.4616 | 0.8620 | 0.535 | 0.341 | 27.9% | 13.5% |
| joint torque | 0.1751 | 0.4442 | 0.394 | 0.494 | 36.3% | 29.4% |

**h = 368**

| Group | model | floor | ratio | med ratio | num share | den share | r>10 |
|---|---|---|---|---|---|---|---|
| base lin vel | 1.9600 | 1.4614 | 1.341 | 0.905 | 5.9% | 4.0% | 1.8% |
| base ang vel | inf | inf | — | 1.445 | 8.1% | 2.9% | 1.1% |
| proj gravity | 5.1869 | 1.5473 | 3.352 | 2.733 | 21.7% | 5.0% | 11.4% |
| joint pos | 0.4561 | 0.9365 | 0.487 | **0.346** | 22.5% | 42.6% | 0% |
| joint vel | 0.7872 | 1.8161 | 0.433 | 0.485 | 16.5% | 17.0% | 0% |
| joint torque | 0.6317 | 0.9728 | 0.649 | 0.772 | 25.4% | 28.5% | 0% |

**Status** CONFIRMED · **Relevance** METHOD, CONTRIB
**Reading** By median ratio at h=368 the model beats the floor most on joint positions (0.346) and least on projected gravity (2.733) — but the gravity figure is a metric artefact (M-09), not a modelling failure. **Base linear velocity is the one group where the model genuinely fails to beat the floor at long horizon** (ratio 1.341, median 0.905), which is consistent with the Step 1 observation that base velocity is the group the model tracks worst one-step.
**Bears on O-07** — the long-horizon compression is partly real (base velocity, joint torque) and partly metric saturation (gravity, angular velocity).

### R-11 — The rebuilt forward pass is bitwise identical to the reference module · **NEW**
`from rsl_rl.modules import SystemDynamicsEnsemble` fails with `ModuleNotFoundError: No module named 'git'` (GitPython, pulled in by the package `__init__`). Loading `rsl_rl/modules/system_dynamics.py` and its `architectures` package directly with `importlib` **succeeds**, and `load_state_dict(strict=True)` reports all keys matched.

| Comparison | Max absolute difference |
|---|---|
| single forward, predicted mean | **0.000e+00** |
| aleatoric / epistemic | 0.000e+00 / 0.000e+00 |
| contact + termination logits | 0.000e+00 |
| full 368-step protocol A rollout, 165,600 values | **0.000e+00** |
| `e` (0.767216 both) | 0.000e+00 |

Threshold was 1e-5; actual is exactly zero.
**Constructor** `(state_dim, action_dim, extension_dim, contact_dim, termination_dim, device, ensemble_size=1, history_horizon=1, architecture_config=None, freeze_auxiliary=False)` — built from `anymal_d_flat_cfg.py` values, not hand-typed.
**Evidence** `RUN` `task5_differential.json`; `SRC` `system_dynamics.py:6-17`.
**Status** CONFIRMED · **Relevance** METHOD
**Resolves O-03 and retires the risk on X-03.** Every Step 3 number rested on this and now has a differential test behind it. Step 4 can be verified the same way.

### R-12 — Harness hardening · **NEW**
All three assertions pass.

- **R-12a — direct index assertion.** `fa[b,0]`, `ha[b,0]` and `fa[b,-1]` are **bitwise equal** to float32(CSV rows start+32, start+0, start+399). The 5.3e-08 residual against the float64 CSV is exactly the harness's float64→float32 cast; a one-row error would be O(0.1). Alignment is now pinned rather than assumed.
- **R-12b — lag-1 oracle.** Its step-1 error equals the hold-last predictor's to **0.000e+00** (0.11066164821386337 both), as required since both predict s[31] for s[32]. They diverge thereafter as they must (e 0.1522 vs 1.0070).
- **R-12c — zero-delta equivalence.** Zeroing the final Linear of all five `state_mean_layers` heads reproduces the hold-last predictor to **1.192e-07** over 165,600 values, with 0 of 368 steps above 1e-6.

**Evidence** `RUN` `task3_hardening.json`.
**Status** CONFIRMED · **Relevance** INTERNAL (R-12c also CONTRIB, as it verifies C-02/M-02)
**Consequence** The residual connection is correctly wired and the harness indexing is correct. **The Step 3 numbers stand.**

### R-13 — The checkpoint's actor is not the data-collection policy · **NEW**
`model_state_dict` in `pretrain_rnn_ens.pt` is an ActorCritic with a 48→128→128→128→12 ELU actor, matching `observation_dim = 48` and `actor_hidden_dims = [128,128,128]`. Fed the observation layout from `anymal_d_flat.py:53`, it reproduces the recorded actions with a best mean R² of only **0.486** (at k = −1; 0.391 at k = 0), and negative R² on two individual joints.

A policy evaluated on its own observation should be near-deterministic, so this is not the policy that generated the CSV — it is the model-based policy trained afterwards in imagination, shipped in the same file.
**Evidence** `RUN` `task1c_policy.json`; `SRC` `anymal_d_flat.py:53`, `base_cfg.py:114-120`.
**Status** CONFIRMED · **Relevance** CONTEXT
**Consequence** The released artifact does not contain the behaviour policy, so the dataset's actions cannot be regenerated or verified against their source. Relevant to any claim about reproducing the data-collection stage.

---

## F. Open questions

### O-01 — Which action convention is causally correct
Does row *t* hold the action applied at *t*, or the action that produced the state at *t*? Determines whether B-05's training convention leaks the target or is the correct pairing.
**Test** Step 3.5 Task 1 — ridge regression predicting `a[t]` from `s[t+k]`, peak location decides.
**Blocks** The entire Step 4 trainer design.
**Status** **RESOLVED at Step 3.5 → k = −1, row *t* holds the action that produced state[*t*].** See D-13. The prescribed ridge test did not settle it (M-10); the reset-row refutation did. Step 4 is unblocked — see X-05.

### O-02 — Why is the model worse than the floor at one step
R-04 h=1 ratio is 1.093. A world model that cannot beat "assume nothing changes" at 20 ms is suspicious.
**Hypothesis** The convention mismatch of B-05 — the model is handed `a[31]` when trained on `a[32]`, and at h=1 that mismatch is the entire signal.
**Test** Step 3.5 Task 2 — rerun with `action_offset=1` and check whether the ratio drops below 1.0.
**Status** **RESOLVED — hypothesis confirmed.** Ratio 1.093 → 0.827 (R-09). Not a model defect.

### O-03 — Does our rebuilt forward pass match the reference exactly
Parameter counts match, but output equivalence has never been checked. All Step 3 numbers rest on this.
**Test** Step 3.5 Task 5 — import `SystemDynamicsEnsemble` directly and compare outputs.
**Status** **RESOLVED — bitwise identical, 0.000e+00 on every comparison.** See R-11.

### O-04 — Units and calibration of the uncertainty outputs
R-08 cannot be interpreted without knowing what the two quantities are measured in and whether they are comparable.
**Status** **RESOLVED.** Both are sums over the 45 **normalised** state dimensions and are directly comparable: aleatoric = `state_stds.mean(0).sum(1)`, epistemic = `state_means.std(0).sum(1)` (`system_dynamics.py:126-127`). The hundredfold ratio in R-08 is real but is explained by C-10 — the aleatoric term is a collapsed constant at its learned lower bound, not a calibrated prediction.

### O-05 — Is the training convention's advantage causal or leakage
R-06 shows the training convention scores better. If row *t* holds `a[t]`, then `a[t+1]` is computed from the target and the advantage is spurious. Resolved by O-01.
**Status** **RESOLVED — causal, not leakage.** Row *t* holds `a[t−1]` in the brief's labelling (D-13), so `a[t+1]` is the action that produced `s[t+1]`: a legitimate input. See S-07.

### O-06 — What does the 352-window contamination actually cost
B-01 is confirmed as a defect but its effect on trained model quality is unmeasured. Candidate Step 6 experiment: train identical models with and without the spliced windows.
**Status** OPEN. Unchanged by Step 3.5.

### O-07 — Is the long-horizon convergence to the floor real or a metric artifact
R-04 shows the ratio compressing from 0.43 at h=16 to 0.76 at h=368. Some of that is genuine degradation and some may be the metric saturating. M-07's per-group breakdown is the first evidence.
**Status** **PARTIALLY RESOLVED.** R-10 separates the two: genuine degradation on base linear velocity (ratio 1.341 at h=368) and joint torque (0.649); metric saturation on projected gravity and base angular velocity, both of which blow up for denominator reasons (M-09). Joint positions and velocities stay strong throughout (0.487, 0.433). Compression persists under the causal convention too (R-09), so it is not a convention artefact. Remaining question: how much of the base-velocity failure is intrinsic to open-loop rollout without command input.

### O-08 — Does the variance collapse reproduce when we train from scratch · **NEW**
C-10 shows the released checkpoint's log-standard-deviation interval has closed to 5.23e-07. Unknown whether this is inevitable given the bound loss at weight 1.0, or an artifact of the authors' particular schedule.
**Test** Step 4 — log `exp(state_log_delta_logstd)` every iteration; sweep the bound-loss weight if it collapses.
**Blocks** Any claim about RWM-U's uncertainty quantification.

### O-09 — Is the reference evaluation's understatement material to the paper's reported numbers · **NEW**
B-05 + R-09 show the released evaluation feeds a stale action, costing 0.066 aggregate and 24% at one step. The paper's reported autoregressive errors were presumably produced by this same code path.
**Test** Compare our R-09 numbers against the paper's Table values on the matching configuration.
**Relevance** Would upgrade B-05 from "internal inconsistency" to "published numbers understate the released model".

---

## G. Deliberate deviations from the reference

### X-01 — Episode-aware split
The reference has no held-out evaluation (B-03, B-04). We introduced an episode-level split, seeded and recorded.
**Justification** Without it, no number in this project would measure generalisation.

### X-02 — No boundary-crossing windows
Training windows and evaluation trajectories are constrained to lie within a single episode.
**Justification** B-01. Note R-05 showed crossings did not hurt evaluation error, but a splice is still a physically impossible transition to train on.

### X-03 — Rebuilt forward pass rather than importing the reference
`setup.py` pins torch ≥ 2.7 with CUDA, which does not install on the target hardware.
**Justification** Necessity. ~~Risk tracked as O-03.~~ **Risk retired** — R-11 shows the rebuild is bitwise identical to the reference module, which we can now load via `importlib` without installing either package.

### X-04 — Termination head retained but degenerate
Kept for architectural parity with the checkpoint, so weights can be loaded for differential testing. Its loss term collapses immediately because the target is all-zero (D-03) and it is excluded from any reported total.
**Justification** D-03. The reference checkpoint acquired this capability from the 6M-transition pretraining, which is not public.

### X-05 — Step 4 trains and evaluates under the causal action alignment · **NEW**
Both our trainer and our harness will use `(s[t], a[t+1]) → s[t+1]` — the training alignment, established causal by D-13 — for training *and* for evaluation. The reference uses this alignment for training only and the stale one for evaluation (B-05).
**Justification** D-13. Feeding an action that has already been superseded is simply wrong, and R-09 measures what it costs.
**Consequence for comparability** Our headline numbers will not be directly comparable to the reference's reported autoregressive error. Both conventions are therefore reported side by side wherever a reference comparison is made, exactly as R-09 does.

---

## H. Superseded claims

Retained deliberately. A reproduction that never records its wrong turns is not showing its work.

### S-01 — "The lite repo may not ship training data"
Stated during target selection. **Wrong.** `assets/data/state_action_data_0.csv` ships 10,000 rows of real ANYmal D data.
**Superseded by** D-01.

### S-02 — "The checkpoint is ~1.25M parameters per ensemble member"
Derived by dividing total file size by five. **Wrong** — the file also contains optimizer state and an unrelated actor/critic policy.
**Superseded by** R-01. Correct figures: 1,995,569 total, ~1,417,789 for a single-member configuration.

### S-03 — "Boundary crossings inflate protocol B"
Stated as the expected explanation for the A/B gap. **Refuted by measurement** — crossing trajectories scored better (0.947) than non-crossing (1.599).
**Superseded by** R-05, D-12.

### S-04 — "The relative-L1 denominator will be numerically fragile here"
Anticipated but not observed on this data.
**Superseded by** M-03.
**Partially reinstated at Step 3.5 by M-09** — the concern was correct, just not at the 45-dimensional aggregate where M-03 tested it. At per-group granularity the denominator does collapse: base angular velocity produces `inf`, projected gravity blows up on 11.4% of timesteps at h=368. Recorded here rather than by editing S-04 or M-03, both of which stand as written within their scope.

### S-05 — "The ten episodes may be ten repetitions of one command"
Raised as a risk to the value of any held-out split. **Refuted** — twenty distinct commanded-velocity regimes.
**Superseded by** D-10.

### S-06 — "Contacts are four knee then four foot"
Working assumption during Step 1. **Corrected** to thigh then foot before any downstream use.
**Superseded by** D-02.

### S-07 — "The training convention leaks the target" · **NEW**
Carried as the leading reading of B-05 from Step 2 onward, and stated outright in the Step 3 report, which described the training alignment as "non-causal" on the grounds that `a[t+1]` is the policy's response to `s[t+1]` and therefore leaks it. The Step 3.5 brief's own decision table encoded the same reading as the `k = 0` branch.

**Refuted.** D-13 establishes k = −1: row *t* holds the action that *produced* state[*t*], so `a[t+1]` is the action that produced `s[t+1]` — a genuinely causal input. The training alignment is correct and the *evaluation* alignment is the defective one.
**Superseded by** D-13, and its consequences by R-06's revised reading and R-09.
**Note** R-06 (the training convention scores 0.066 better) was measured before the convention was known and was explicitly flagged as uninterpretable at the time. That caution was the right call: the same measurement supports the opposite conclusion once D-13 fixes the direction.

### S-08 — "Forecast decay is inert because it is configured to 1.0" · **NEW**
Recorded as C-08 with status UNVERIFIED and an explicit instruction to reconfirm before use. **The premise was wrong**: there is no decay parameter in the implementation to configure. The forecast loop applies a plain unweighted mean over forecast steps.
**Superseded by** C-09.
**Note** The UNVERIFIED flag did its job — the claim was never promoted to a result. This is the `INFER` evidence class working as intended.

---

## Candidate paper contributions

Ordered by how much they would stand on their own, for use when the writeup begins. Every one still needs its impact quantified rather than merely its existence demonstrated.

1. **The released pipeline trains on spliced episodes** (B-01, D-03, D-06). A defect with a clear mechanism, a clean count, and an obvious controlled experiment behind it (O-06).
2. **There is no held-out evaluation in the released repository** (B-03, B-04), plus a demonstration of what a correct one gives (X-01, R-02).
3. **The released evaluation feeds a stale action and understates its own model** (B-05, D-13, R-09). *Promoted from third-with-caveats to a firm result at Step 3.5.* The convention question is settled, the direction is the opposite of what we first assumed (S-07), and the cost is measured: 24% of the one-step error and 0.066 aggregate. The h=1 anomaly that made the released checkpoint look broken was this defect, not the model.
4. **The paper's described model is not the implemented model** (C-01, C-03 through C-07, C-09, C-10). Seven loss terms against two; a residual mean head; two trunks; a shared-trunk ensemble; sample-versus-mean asymmetry; a forecast decay factor the paper specifies and the code does not have; and a variance head that has collapsed to a constant in the released weights.
5. **Both halves of RWM-U's uncertainty estimate are weaker than described** (C-04, C-10, R-08, O-08). The aleatoric channel is degenerate — a learned constant at its own lower bound, σ ≈ 5.6e-05 — and the epistemic channel measures head disagreement over shared features. This is new at Step 3.5 and is the most directly damaging finding for the "-U" contribution specifically.
6. **The released checkpoint is only modestly better than a trivial baseline at long horizon** (R-03, R-09, R-10). Softened by Step 3.5: it is *not* worse at one step once scored correctly, and the per-group breakdown shows the weakness is concentrated in base linear velocity while joint prediction stays strong. The honest version of this claim is narrower than the original.
7. **Evaluation with ten trajectories is underpowered** (M-04, D-12). Methodological, but it undercuts single-seed comparisons in this literature generally.
8. **Correlational tests cannot establish action alignment for position-controlled robots** (M-10, M-11). A small, transferable methods note: the identification has to come from structural invariants such as reset rows, not from fitting.
