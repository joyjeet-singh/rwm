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

**Status.** Steps 0–5 complete. **M-23 returns REPRODUCES AT LONG HORIZON (R-40)** under a rule pre-registered before the runs existed. Last updated: 19 Aug 2026.
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

## Step 4 changes at a glance

| ID | Was | Now |
|---|---|---|
| D-13 | CONFIRMED, premise uncited | **CONFIRMED, premise cited** — `SRC`/`EXT` (0c) |
| O-08 | OPEN | **PARTIALLY RESOLVED** — collapse reproduced on one batch (R-17) |
| R-02, R-04, R-06, R-07 | headline figures | **superseded as headline by R-15**; retained as what the released code reports |
| M-03 | aggregate-only caveat | companion metric added (M-12) |
| — | — | **New:** C-11, C-12, M-12, M-13, R-14–R-17, O-10, O-11, X-06 |

## Step 5 changes at a glance

| ID | Was | Now |
|---|---|---|
| R-17 | INCOMPLETE (memorisation) | **superseded as the trainer test by R-18** — decisive |
| O-08 | PARTIALLY RESOLVED | **RESOLVED** — collapse reproduced at two learning rates, rate ∝ lr (R-18) |
| C-12 | ~155k iterations vs 500/2500 | **refined by O-12** — the checkpoint's own iteration tag makes it sharper |
| — | — | **New:** C-13, R-18, O-12, plus repository licensing and reproducibility scaffolding |

---

## Which paper each claim addresses

**Two papers are in scope and they must not be conflated.** `pretrain_rnn_ens.pt` is a
five-member ensemble with an epistemic/aleatoric decomposition — the **RWM-U** configuration of
*Uncertainty-Aware Robotic World Model* (arXiv **2504.16680**). The autoregressive-versus-teacher-forcing
claim that M-23 tested is from the **base RWM** paper (arXiv **2501.10100**).

| tag | meaning |
|---|---|
| `[BASE]` | bears on arXiv 2501.10100 — the dynamics model and its training objective |
| `[RWM-U]` | bears on arXiv 2504.16680 — the uncertainty-aware follow-up |
| `[BOTH]` | bears on both, usually because it concerns shared code or shared data |

**`[RWM-U]`** — C-04, C-06, C-10, C-11, O-08, O-12, O-13, R-08, R-24, R-25, R-43, R-48, R-49,
R-50, R-51, R-52, R-53, R-54. These concern the variance head, its collapse, and the
calibration of the uncertainty output; none of them is a claim about the base paper.

**`[BASE]`** — M-16, M-23, M-24, R-19, R-22, R-23, R-35, R-36, R-37, R-40, R-42, R-45, R-46,
R-47, R-55, and the A/B comparison generally; plus the loss-assembly discrepancies C-01,
C-02, C-05, C-09
and the defects B-01 to B-05.

**`[BOTH]`** — D-01 to D-13 (the dataset is shared), C-03, C-07, C-12, C-13, R-01, R-11, R-14,
and the evaluation-methodology entries M-09, M-12, M-17, M-19, M-20, M-25, M-26, which apply
to any
measurement made on this data.

Recorded now rather than during writing: a reviewer who notices the conflation before it is
named will read it as carelessness rather than as a two-paper result.


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
**Premise cited at Step 4 (0c).** The refutation rests on Isaac Lab zeroing the action
buffer on reset, which was previously asserted without a source. It is
`ActionManager.reset()`, `source/isaaclab/isaaclab/managers/action_manager.py:350-365`,
commit `7a4b6d2be5823d03f91a448751947a68add0a285`:

```python
self._prev_action[env_ids] = 0.0    # line 364
self._action[env_ids] = 0.0         # line 365
```

with both buffers initialised to zeros at lines 215-216. Evidence class upgraded from
`DATA` + `INFER` to `DATA` + `SRC`/`EXT`. No downgrade required.
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

### C-11 — `state_min_logstd` receives no gradient from the bound loss · **NEW (Step 4)**
Sharpens C-10's mechanism. The bound loss is

```
mean(max_logstd) - mean(min_logstd) = mean(min_logstd + exp(log_delta_logstd)) - mean(min_logstd)
                                    = mean(exp(log_delta_logstd))
```

so `state_min_logstd` **cancels algebraically** and takes no gradient from that term.
Confirmed empirically: in the gradient differential test under zero-noise sampling, exactly
25 of 106 parameter tensors have an identically zero gradient, and they are precisely the
five heads' `state_logstd_layers` (20 tensors) plus their `state_min_logstd` (5). Both
implementations agree on the set.

The consequence is a one-way ratchet. `log_delta_logstd` has a constant-sign gradient and
falls steadily; `min_logstd` is reachable only through the sigma path in the state loss,
whose gradient vanishes as sigma shrinks. So once the interval starts closing, the floor it
closes onto freezes, and nothing can reopen it.
**Evidence** `SRC` `system_dynamics.py:301-302`, `mlp.py:91`; `RUN` `step4_3_differential.json`.
**Status** CONFIRMED · **Relevance** CONTRIB

### C-12 — The released checkpoint's collapse implies ~155,000 iterations, not 500 or 2500 · **NEW (Step 4)**
Measured on a fresh model (R-17): `log_delta_logstd` falls at **−9.318e-05 per iteration**,
which is 0.93× the configured learning rate of 1e-4 — exactly the Adam behaviour expected
when a gradient holds its sign, since Adam's step size is ~lr regardless of gradient
magnitude.

Extrapolating to the released checkpoint's value of −14.463 (C-10):

| Iterations | resulting `exp(log_delta_logstd)` |
|---|---|
| 500 (`base_cfg.py` `max_iterations`) | 0.9545 |
| 2500 (paper Table S7) | 0.7922 |
| **~155,000** | **5.23e-07 — the released value** |

Neither documented iteration count can produce the released checkpoint's variance state at
the configured learning rate. Following the released recipe as written yields a model whose
uncertainty head is essentially untouched, not one whose interval has closed by seven orders
of magnitude.
**Evidence** `RUN` `step4_4_overfit_ens1.json`, linear fit over 18 collapse samples; `SRC`
`base_cfg.py` lr and max_iterations.
**Status** CONFIRMED · **Relevance** CONTRIB
**Refined by O-12 (Step 5)**, which adds a second rate measurement at lr 1e-3 and compares against the checkpoint's own iteration tag of 5000 rather than only against 500 and 2500.
**Caveat** Measured at ensemble 1 on a single fixed batch (X-06). The rate is set by the
optimiser and the bound-loss gradient sign, neither of which depends on batch content, so
it should carry — but this is an extrapolation over three orders of magnitude and is
labelled as one. Opens O-10.


### C-13 — Three different iteration counts are in play · **NEW (Step 5)**
The reproduction target does not state one training length; it states three, and they
disagree by an order of magnitude.

| Source | Iterations |
|---|---|
| `base_cfg.py` `ModelTrainingConfig.max_iterations` | **500** |
| Paper, Table S7 | **2500** |
| `pretrain_rnn_ens.pt`, `iter` key in the checkpoint | **5000** |

None of the three is consistent with the released checkpoint's variance state (O-12), so this
is not merely a documentation mismatch — the largest of the three still falls ~6 orders of
magnitude short of explaining the weights that shipped.
**Evidence** `SRC` `base_cfg.py:97`; `EXT` paper Table S7; `DATA` checkpoint `iter` field,
read in R-01.
**Status** CONFIRMED · **Relevance** CONTRIB
**Decision for Step 5** Train to 2500 to match the paper and checkpoint at 500 as well, so
both documented numbers can be reported from one run at no extra cost.


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
**CROSS-VALIDATION DECISION (5.4), now resolved.** Deferred pending M-23, and its condition was:
if M-23 settles with per-episode sign consistent at ten of ten, the direction is established
without CV and the magnitude is reported as a range with the outlier named; otherwise the twelve
hours are justified. **M-23 settled and the sign is consistent at ten of ten (R-40), so
cross-validation does NOT run.** The long-horizon magnitude is reported as a range across
episodes — gap +0.418 to +1.826 at 10,000 — with episode 1 named as the high outlier per R-39.
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

### M-12 — Normalised RMSE with a fixed denominator · **NEW (Step 4)**
Added alongside the relative-L1 metric, never replacing it. The relative-L1 exists to
compare against the paper; this exists to reason with.

```
nrmse[d] = RMSE(pred[..., d], true[..., d]) / scale[d]
scale[d] = std of normalised dimension d over the TRAINING episodes, computed once
```

Fixed, not per-timestep, is the whole point: the denominator cannot approach zero, so the
M-09 failure modes cannot occur. Reading is direct — 1.0 means "no better than predicting
the training mean", below 1.0 means the model carries information.

The stored scale spans 0.0292 to 1.3873. Its smallest entry is the gravity z-component,
where the config's `state_data_std` of 0.04 overestimates the actual spread by ~34×, so
normalised g_z is very nearly constant. This also refines M-09: the gravity blow-ups are
driven by g_x and g_y, which are near-zero-mean with unit spread, and not by g_z, which
contributes almost nothing to the denominator.

First application (R-15) immediately paid for itself: at h=368 protocol A scores nRMSE
**1.3228 under the released evaluation convention and 0.7572 under the causal one**. That is
the difference between "worse than predicting the training mean" and "clearly informative",
and the relative-L1 metric (0.7672 vs 0.7008) does not show it.
**Evidence** `RUN` `rwm_metrics.py`, `step4_0a_results.json`.
**Status** CONFIRMED · **Relevance** METHOD

### M-13 — The auxiliary branch is teacher-forced; the state branch is not · **NEW (Step 4)**
In `compute_state_loss` the trunk is fed its own reparameterised sample at each forecast
step (`system_dynamics.py:216`). In `compute_auxiliary_loss` it is fed the **true** next
state (`:264`). So the contact and termination heads never see the model's own rollout
error during training, while the state head does.

At inference both branches consume predicted states, so the auxiliary heads are evaluated
under a distribution they were never trained on. Reproduced faithfully; flagged because it
is invisible from the paper and is a plausible source of auxiliary-head degradation in long
rollouts.
**Evidence** `SRC` `system_dynamics.py:216, 264`.
**Status** CONFIRMED · **Relevance** CONTRIB


### M-14 — The overfit acceptance threshold was unreachable, and the reason is not the one assumed · **NEW (Step 5)**
The 1e-4 threshold on the state loss could not be met by construction, because the loss is
squared error on a reparameterised sample:

```
E[ sum_d (mu_d + sigma_d*eps_d - y_d)^2 ] = sum_d (mu_d - y_d)^2 + sum_d sigma_d^2
```

The second term does not vanish, so the objective has a floor and an acceptance threshold has
to be derived from it rather than assumed. That is the methodological lesson worth keeping.

**But the floor is not what explains the observed plateau.** Measured on the converged R-18
weights, same batch, no retraining:

| quantity | value | share of L_stoch |
|---|---|---|
| `L_stoch` (real sampling, mean of 100 draws, sd 0.000324) | 0.031860 | 100% |
| `L_det` (randn_like patched to zeros, sample = mean) | **0.027737** | **87.1%** |
| measured sampling contribution, `L_stoch − L_det` | 0.004123 | 12.9% |
| `sum_d sigma_d^2` at the first forecast step | 0.000976 | 3.1% |

`L_stoch / L_det = 1.1x`, not the ≫5× that a floor-dominated plateau would give. So by the
pre-stated rule the plateau is **residual mean error, not the sampling floor**.

**Where the assumption went wrong.** The expectation that "sigma was nowhere near zero"
read `exp(log_delta_logstd) ≈ 0.25` as a standard deviation. It is not: it is the *width of
the bounding interval in log space* (C-06). With `min_logstd ≈ log(4.638e-3) = −5.37`, the
clamp gives `logstd ∈ [−5.37, −5.13]`, i.e. `sigma ≈ 4.6e-3 to 5.9e-3`. Summed over 45
dimensions that is ~1e-3, which is 3% of the loss, not most of it. The measured 12.9% is
larger than the single-step 3.1% because injected noise also propagates into each subsequent
step's input — a ~4× amplification across the eight steps, which is itself a clean
measurement of how much the autoregressive rollout amplifies its own injected noise.

**This does not overturn R-18 and does not block the runs.** `L_det = 0.027737` over 45
summed dimensions is a per-dimension RMSE of **0.0248 normalised sd** — a good fit in
absolute terms, on a curve still descending when the run hit its cap. The accurate statement
is neither "the floor explains it" nor "the model failed to fit": the model fitted the batch
to ~2.5% of a standard deviation per dimension, the residual is genuine mean error rather
than injected variance, and it had not converged.
**Evidence** `RUN` `results/step5_6_overfit_floor.json`; `SRC` `system_dynamics.py:270-289`,
`mlp.py:78-79, 91-93`.
**Status** CONFIRMED · **Relevance** METHOD

### M-15 — The reference does not clip gradients in the world-model path · **NEW (Step 5)**
`READ AND REPORT` (5.7a). Searched `system_dynamics.py`, `model_training.py`, `base_cfg.py`,
`anymal_d_flat_cfg.py` and `train.py` for `clip_grad_norm_`, `clip_grad_value_`,
`max_grad_norm` and equivalents.

**Absent from the world-model path.** `model_training.py:74-75` runs `loss.backward()`
directly into `self.optimizer.step()` with nothing between, and `ModelOptimizerConfig`
carries only `learning_rate` and `weight_decay`.

**Present in the policy path**, which makes the absence a choice rather than an oversight:
`PolicyAlgorithmConfig.max_grad_norm = 1.0` (`base_cfg.py:140`) is applied via
`nn.utils.clip_grad_norm_(self.policy.parameters(), self.max_grad_norm)` at `ppo.py:380`. The
codebase knows the idiom and applies it to PPO but not to the dynamics model.

**Decision: do not add it.** Clipping would be an undocumented deviation and would alter
exactly the dynamic under study — gradient behaviour through the recurrent autoregressive
rollout. Gradient norm is instead logged every iteration, with a spike detector at 5x the
trailing 50-iteration median (5.7c). Should a main run diverge, clipping becomes a deviation
with a stated reason and a new `X-` entry, but not before.
**Evidence** `SRC` `model_training.py:74-75`, `base_cfg.py:87-93` (ModelOptimizerConfig),
`base_cfg.py:140`, `ppo.py:380`.
**Status** CONFIRMED · **Relevance** METHOD

### M-16 — PRE-REGISTERED decision rule for the Arm A / Arm B comparison · **NEW (Step 5)**
**Entered before any main-run result exists.** Committed prior to launching Arm A seed 0; the
git history is the timestamp. A rule chosen after seeing numbers is not a rule.

**The claim reproduces, or fails to, and can be reported** only if BOTH hold:
1. the A-versus-B ordering at h = 8 is the **same** at the 500 checkpoint and at the 2500
   checkpoint, **and**
2. the difference between arms **exceeds** the seed spread within arms.

**The claim cannot be settled at this budget** if EITHER:
1. the ordering **flips** between the two checkpoints, **or**
2. the difference between arms falls **inside** the seed spread.

In that case the report states that the comparison is not converged, and gives the slope of
the training loss over the final 250 iterations as evidence. Given M-04 — protocol A varies
by ±0.053 over evaluation seeds alone, before any training-seed variance — that outcome is
entirely possible and is a legitimate result, not a failure.

The follow-up, if it lands there, is a higher-learning-rate pair rather than more seeds, and
it is not to be run without reporting first.

**ANNOTATION, pre-registered separately and before any Arm B result exists.** This does NOT
modify the rule above; the rule stands exactly as written, including its verdict of "cannot be
settled at this budget" for *any* flip in the ordering.

What it adds is an interpretation of one specific flip pattern, entered now so that it cannot
be chosen after seeing the numbers:

> If the ordering flips such that **B leads at 500 and A leads at 2500**, that specific
> pattern is consistent with teacher forcing converging faster early and generalising worse
> under rollout. M-16's verdict of "cannot be settled" still holds — but this pattern is to be
> reported alongside it as a distinct observation, not folded into the null result. Any other
> flip pattern carries no such reading.

The reasoning, also recorded in advance: R-19 shows Arm A at 500 iterations is worse than the
hold-last floor at every horizon beyond h=4, so both arms will be deep in the transient at
that checkpoint. Teacher forcing optimises an easier objective — it never has to consume its
own error — so faster early fitting followed by worse rollout behaviour is the textbook
signature rather than a surprise. The reverse pattern (A ahead at 500, B ahead at 2500) has no
such mechanism behind it and is to be reported as an unexplained flip.

**SUPERSEDED AS THE GOVERNING VERDICT BY R-35.** Under independent trajectories and pooled
aggregation the rule returns **cannot be settled at this budget** in all eight arena/length/
metric combinations — out-of-sample failing condition 2 (arms not separated at h=8) and
in-sample failing condition 1 (ordering flips). The verdict below stands as what the
reference's own overlapping-trajectory protocol yields, and is retained on that basis.

**OUTCOME (Step 6, R-22), on the reference protocol: SETTLED, on both metrics, with the two metrics agreeing.**
Arm A leads at h=8 at both checkpoints under relative-L1 (0.4022→0.3263 vs B 0.4254→0.3915)
and under nRMSE (0.3648→0.2805 vs B 0.3991→0.3210). Condition 1 holds: no flip. Condition 2
holds: |A−B| is 0.0652 against a max within-arm seed sd of 0.0150 (relative-L1), and 0.0405
against 0.0183 (nRMSE). The rule therefore returns a reportable result, and the annotation
above did not fire because there was no flip.
**Evidence** `RUN` `results/step6_analysis.json`.
**Status** SETTLED — rule pre-registered in `84ff01b`, annotation in `0fe2bca`, both before any
Arm B result existed · **Relevance** METHOD


### M-17 — nRMSE is a TAIL statistic and is biased low at small n; relative-L1 is not · **NEW (batch 1)**
The single most consequential methodological finding in the project, because it inverts an
answer that had already been reported.

`nrmse_per_step` takes the RMSE **across trajectories** at each forecast step. RMSE is
dominated by its tail, and a world-model rollout has a heavy one: a minority of trajectories
diverge and contribute most of the squared error. A 10-trajectory sample frequently fails to
draw one, so **small-n nRMSE is biased low, not merely noisy.** relative-L1 averages
per-timestep ratios and has no such sensitivity.

Released checkpoint at h=368, varying only the trajectory count (8 eval seeds for n ≤ 100,
4 for n > 100):

| n | e model | e floor | model beats floor | nRMSE model | nRMSE floor | model beats floor |
|---|---|---|---|---|---|---|
| 10 | 0.6402 ± 0.0714 | 0.9585 ± 0.0589 | **100%** | 1.0406 ± 0.4349 | 1.0497 ± 0.0749 | **62%** |
| 25 | 0.6400 ± 0.0454 | 0.9759 ± 0.0453 | 100% | 1.1645 ± 0.3635 | 1.0959 ± 0.0313 | 38% |
| 50 | 0.6423 ± 0.0171 | 0.9937 ± 0.0446 | 100% | 1.6209 ± 0.2461 | 1.1253 ± 0.0245 | **0%** |
| 100 | 0.6381 ± 0.0150 | 0.9641 ± 0.0168 | 100% | 1.6918 ± 0.2267 | 1.1189 ± 0.0218 | 0% |
| 200 | 0.6456 ± 0.0149 | 0.9636 ± 0.0072 | 100% | 1.8072 ± 0.3185 | 1.1154 ± 0.0219 | 0% |
| 400 | 0.6456 ± 0.0116 | 0.9618 ± 0.0078 | 100% | 1.8872 ± 0.2112 | 1.1127 ± 0.0018 | 0% |

The model's nRMSE climbs monotonically from 1.04 to 1.89 and has still not plateaued at n=400.
The **floor's** nRMSE is stable (1.05 → 1.11) because the hold-last predictor has a bounded,
well-behaved error distribution and no diverging tail. That asymmetry is the whole mechanism.

**Practical rule, adopted from here on:** relative-L1 has converged by n=25; nRMSE requires
n ≥ 50 and should be quoted with the n it was measured at. Any nRMSE in this ledger measured
at n=10 is biased low and is flagged accordingly.
**Evidence** `RUN` `results/task3b_convergence.json`.
**Status** CONFIRMED · **Relevance** CONTRIB

### M-18 — Spread convention: `ddof=1` throughout · **NEW (batch 1)**
All spreads over seeds are now reported with the sample standard deviation (`ddof=1`). With
n=3 the difference from `ddof=0` is 22%, and M-16's condition 2 compares an arm difference
against exactly that quantity, so the convention has to be stated rather than assumed.

| | mean | sd (ddof=0) | sd (ddof=1) |
|---|---|---|---|
| Arm A, relative-L1 h=8 @2500 | 0.3263 | 0.0074 | **0.0091** |
| Arm B, relative-L1 h=8 @2500 | 0.3915 | 0.0150 | **0.0184** |
| Arm A, nRMSE h=8 @2500 | 0.2805 | 0.0075 | **0.0091** |
| Arm B, nRMSE h=8 @2500 | 0.3210 | 0.0183 | **0.0224** |
| Arm A, relative-L1 h=368 @2500 | 0.9333 | 0.0988 | **0.1209** |
| Arm B, relative-L1 h=368 @2500 | 4.0171 | 0.3022 | **0.3701** |

**M-16's verdict survives the stricter convention**: 0.0652 > 0.0184 on relative-L1 and
0.0405 > 0.0224 on nRMSE, both at h=8.
**Evidence** `RUN` `results/task3_4_power_ddof.json`.
**Status** CONFIRMED · **Relevance** METHOD


### M-19 — Aggregating nRMSE as a mean of per-dimension ratios is wrong when scales span decades · **NEW**
The methodological lesson from R-29, and it is about our own analysis rather than the paper's.

M-12 introduced nRMSE with a fixed denominator to cure relative-L1's per-timestep fragility
(M-09). It did cure that. But the **aggregation** chosen — form 2, `mean_d (RMSE_d / scale_d)` —
reintroduced a different fragility: a mean of ratios is dominated by whichever ratio has the
smallest denominator. With scales spanning 0.0292 to 1.3873, a 47× range, one near-constant
dimension can carry a 45-term average on its own, and here it does: `g_z` contributes 52.3.

**Form 1, `sqrt(mean_d MSE_d) / mean_d(scale_d)`, pools before dividing and does not have this
property.** It is adopted as the primary aggregation from here on, with form 2 retained and
labelled where it has already been reported.

**R-21 anticipated exactly this** — "read per-dimension there… neither metric is trustworthy for
projected gravity" — and R-27 was promoted to contribution #1 without heeding it. Recorded
because the failure was not the metric; it was not applying a caveat already in this ledger.

**On the estimator, separately from the aggregation.** The brief's proposed Jensen mechanism —
`E[sqrt(MSE_n)] < sqrt(E[MSE_n])`, gap growing with `Var(MSE_n)` — predicts three behaviours.
Measured over 8 eval seeds with nested subsamples:

| n | mean_s MSE (should be flat) | sqrt(mean_s MSE) (flat) | mean_s sqrt(MSE) (rises) | bias |
|---|---|---|---|---|
| 10 | 151.93 | 1.8815 | 1.3332 | 0.5483 |
| 25 | 132.76 | 2.0266 | 1.5487 | 0.4779 |
| 50 | 103.31 | 1.8720 | 1.5198 | 0.3522 |
| 100 | 100.33 | 1.8931 | 1.6525 | 0.2406 |
| 400 | 99.04 | 1.9583 | 1.8654 | 0.0929 |

Rows 2 and 3 behave as predicted — row 3 rises monotonically toward row 2 and the bias falls
monotonically from 0.548 to 0.093. **Row 1 does not**: it varies 1.53× rather than staying
flat. So the Jensen mechanism is **consistent with the data but not proven**, because with 8
seeds and a per-trajectory max/median of 2,893× the MSE estimate is itself too noisy to
establish that row 1 is flat. Reported as consistent-with rather than proven.

The pooled estimator — pool squared errors across trajectories and seeds, then take the root —
is adopted regardless, since it is unbiased by construction whatever the mechanism.
**Evidence** `RUN` `results/taskAB_gate_r27.json`.
**Status** CONFIRMED (aggregation); Jensen mechanism CONSISTENT BUT UNPROVEN · **Relevance** CONTRIB


### M-20 — Effective sample size, and what actually drives long-horizon verdicts · **NEW**
Every long-horizon figure now carries `n_independent` alongside `n_trajectories`: two
trajectories whose 400-step spans overlap at all count as one. Helpers
`n_independent()` and `non_overlapping_starts()` are in `src/rwm_metrics.py`; the convention is
recorded in the manifest.

The counts are sobering. **Only four strictly non-overlapping 400-step trajectories exist in the
two held-out episodes** (starts 999, 1399, 7999, 8399). Every long-horizon number reported in
this project before now — including at "n=100" — rests on `n_independent = 4`. The reference's
protocol has the same property and does not mention it.

**But independence turned out not to be the binding constraint. Episode composition is.**
Decomposed at h=368, relative-L1, released checkpoint:

| evaluation set | n | n_indep | model | floor | verdict |
|---|---|---|---|---|---|
| held-out pair, 100 overlapping | 100 | 4 | 0.6193 | 0.9724 | beats |
| held-out pair, independent only | 4 | 4 | **0.6041** | 0.9930 | beats |
| all ten episodes, independent | 20 | 20 | **1.3157** | 1.0817 | loses |
| the eight training episodes, independent | 16 | 16 | 1.4936 | 1.1039 | loses |

Going from 100 overlapping to 4 independent trajectories on the same episodes changes the model
figure by 2% (0.6193 → 0.6041). Going from those two episodes to all ten more than doubles it.

**Per-episode model/floor ratio at h=368** (2 independent trajectories each): ep7 0.50, ep8
**0.60**, ep1 **0.61**, ep2 0.79, ep5 1.11, ep6 1.48, ep0 1.69, ep3 1.90, ep9 2.01, ep4 2.05.
The checkpoint beats the floor on **4 of 10 episodes and loses on 6**, and the seed-0 split
holds out two of the three it does best on.

**This revises M-05.** M-05 recorded the composition bias but argued the *ratio* was safe
because "the model and the floor are evaluated on the same trajectories, so the ratio is a
controlled comparison". That reasoning is wrong: the ratio itself ranges from 0.50 to 2.05
across episodes, so which episodes are evaluated determines whether the model beats the floor at
all. Same-trajectory evaluation controls for trajectory difficulty in the *numerator and
denominator*, not for the fact that the model's advantage over a constant predictor is itself
episode-dependent.

**Adopted for all future reporting** (Task 3c/3d): pooled form 1 as the primary aggregate,
per-dimension always available with a win/loss count, per-group as secondary with the
near-constant-dimension caveat, relative-L1 throughout for comparability, `n_independent`
printed everywhere, and an explicit caveat wherever it falls below ~10.
**Evidence** `RUN` `results/batch1_post_retraction.json`; `SRC` `src/rwm_metrics.py`.
**Status** CONFIRMED · **Relevance** CONTRIB


### M-21 — The arms cannot be evaluated on all ten episodes; the released checkpoint can · **NEW**
A trap worth documenting precisely because the released-checkpoint case makes it look safe.

R-34 evaluates the released checkpoint on all ten episodes, and that is correct: the authors
trained it on the entire CSV, so there is no clean subset left to protect and restricting it to
two episodes buys nothing while costing five-sixths of the independent samples.

**The same move does not transfer to Arms A and B.** They trained on episodes 0, 2, 3, 4, 5, 6,
7, 9. An all-ten aggregate would be **80% training data**, would flatter both arms, and would
stop being a generalisation measure. It was proposed after M-20 showed composition drives the
verdict, and it conflates two separate problems — sample size and composition — which are
addressed separately below.

**Standing convention adopted: two arenas, never one aggregate.**

| arena | episodes | independent @400 | independent @200 |
|---|---|---|---|
| **out-of-sample** | 1, 8 | 4 | 10 |
| **in-sample** | 0, 2, 3, 4, 5, 6, 7, 9 | 16 | 40 |

Both are legitimate and they answer different questions. Out-of-sample is the generalisation
claim and remains the governing one for M-16, which was pre-registered on it. In-sample is a
fair comparison of fit quality between two arms that saw identical data, at four times the
power. Every table carries its arena label and its `n_independent`. **They are never combined**
— aggregation is always available afterwards, decomposition is not.
**Evidence** `SRC` split definition; `RUN` M-20's decomposition.
**Status** CONFIRMED · **Relevance** METHOD

### M-22 — PRE-REGISTERED rule for whether episode difficulty biases the A/B comparison · **NEW**
**Entered before Task 4b runs.** Committed prior to computing any per-episode gap; the git
history is the timestamp, as it was for M-16.

The concern: every A/B number rests on episodes 1 and 8, which are the first and third easiest
of ten by D-12 (pair mean 0.694 against a population mean of 1.097). The test: compute the
Arm A minus Arm B gap per episode on independent trajectories within that episode, and regress
it on D-12's per-episode difficulty.

> **If the correlation between gap and difficulty is weak** — |r| < 0.4, or its confidence
> interval spans zero — the held-out pair's easiness does not bias the comparison. M-16's
> verdict stands as measured and no retraining is warranted.
>
> **If the gap grows with difficulty** (r positive and material), the out-of-sample estimate is
> conservative: the effect is larger on representative episodes than on the easy pair. The
> finding strengthens; report the direction and the size of the understatement.
>
> **If the gap shrinks with difficulty** (r negative and material), the easy held-out pair
> inflates the result. Cross-validation becomes necessary rather than optional, and Task 4c
> runs: five folds of two episodes, every episode held out exactly once, ~12 h.
>
> In all three cases, report whether the **sign** of the gap is consistent across all ten
> episodes. A gap that reverses sign on any episode is a more serious problem than any
> correlation, and is reportable regardless of r.

**OUTCOME (R-37): BRANCH 1 — WEAK.** Governing metric relative-L1 at h=8, where M-16 was
pre-registered: **r = −0.464, 95% CI [−0.851, +0.141], which spans zero.** The rule's first
branch fires: the held-out pair's easiness does not demonstrably bias the comparison, M-16
stands as measured, and **Task 4c (cross-validation, ~12 h) does NOT run.**

Recorded per the brief so the omission is a decision rather than a gap: cross-validation over
five folds was considered, its trigger was a materially negative correlation between the A/B
gap and episode difficulty, and that trigger was not met — the point estimate is negative and
|r| exceeds 0.4, but the confidence interval includes zero at n=10 episodes, so the evidence
does not support it.

**But the rule's third requirement is violated and outranks the correlation.** The sign of the
gap is **not** consistent across all ten episodes at h=8: it is negative on episodes 0, 1 and 3
on both metrics (R-37). At h=368 it is positive on all ten. Reported as M-22 requires.
**Evidence** `RUN` `results/task4_arenas.json`.
**Status** RESOLVED — branch 1, 4c not run · **Relevance** METHOD


### M-24 — A pre-registered rule must be anchored to the regime the claim is about · **NEW**
The methodological lesson from M-16, and it is about the rule's *design*, not its execution.

M-16 was pre-registered at **h=8** because that is the training forecast horizon — a landmark
in the training configuration, and a defensible-looking choice. But the paper's claim concerns
**long-horizon rollout fidelity**. h=8 sits one step past the objective's own horizon, before
the autoregressive and teacher-forced regimes have diverged, and the effect there is small
enough to be indistinguishable from noise (R-35: gap 0.0035–0.0205 against a spread of
0.0229–0.0308).

At h=368 the same comparison is unambiguous — a factor of 6–8× in every arena, sign-consistent
across all ten episodes (R-37). **The rule was well-formed and evaluated at a horizon that could
not test the claim it was written for.**

The lesson generalises: choose the horizon or regime from the claim, not from a convenient
landmark in the training setup. A rule anchored to the wrong regime returns "cannot be settled"
on data that in fact settles the question decisively somewhere else — and pre-registration
discipline then correctly forbids moving the goalposts after the fact. The remedy is to
pre-register the *right* measurement in advance, which is what M-23 does.
**Evidence** `RUN` `results/task4_arenas.json`; `SRC` M-16's own text.
**Status** CONFIRMED · **Relevance** CONTRIB


### M-23 — PRE-REGISTERED decision rule for the 10,000-iteration comparison · **NEW**
**Entered before any 10,000-iteration result exists.** Committed on its own, before the runs are
launched; the git history is the timestamp, as for M-16 and the `0fe2bca` annotation.

Written to correct M-24's design flaw: this rule is anchored to the horizon the paper's claim is
actually about, not to the training configuration's forecast horizon.

**Governing measurement:** relative-L1 at **h=368**, **out-of-sample** arena (episodes 1 and 8),
400-step trajectories, **form 1 pooled** aggregation, with a **95% bootstrap CI over independent
trajectories** (10,000 resamples), per M-25.

> **The claim reproduces at long horizon** if all three hold:
> 1. Arm A leads Arm B at the 2500 **and** 10,000 checkpoints;
> 2. the 95% bootstrap CI on the A/B gap **excludes zero** at 10,000;
> 3. the sign of the per-episode gap is **consistent across all ten episodes**.
>
> **The claim fails to reproduce** if Arm A does not lead at 10,000.
>
> **Cannot be settled** if the ordering holds but the CI spans zero, or the per-episode sign is
> inconsistent.

**Reported alongside, never as the governing verdict:** the same three conditions evaluated at
h=8; at h=168 on 200-step trajectories; on nRMSE; and in the in-sample arena. **If the governing
verdict and any secondary verdict disagree, both are reported and the disagreement is the
result.**

**On the h=8 question, raised before the runs: no expectation is stated.** Both arms were still
descending at 2500 (slopes −6.5e-04 and −2.1e-04) and whether the h=8 gap separates by 10,000 is
open. It will be answered by condition 1 evaluated at h=8 as a secondary, and recording "no
expectation" now is deliberate — a prediction invented afterwards would have no standing.
**OUTCOME (R-40): REPRODUCES AT LONG HORIZON.** All three conditions hold — Arm A leads at both
2500 and 10,000 (gaps +6.7455, +1.2033), the 95% bootstrap CI excludes zero at 10,000
([+0.5606, +2.0467]), and the per-episode sign is positive on all ten episodes (+0.418 to
+1.826). Governing and secondary verdicts agree in direction; the only measurement spanning zero
is h=8 out-of-sample at n_independent = 4.

**On the h=8 question, for which no expectation was recorded:** it does not resolve
out-of-sample even at 10,000 iterations (R-42), and it resolves cleanly in-sample where there
are four times the independent samples. The limit is sample size, not convergence.
**Evidence** `RUN` `results/task5_analysis.json`.
**Status** RESOLVED — reproduces at long horizon · **Relevance** METHOD

### M-25 — Bootstrap CIs over independent trajectories replace the seed-spread statistic · **NEW**
M-16's condition 2 compared the arm gap against the spread over three training seeds. Task 5
runs one seed per arm, so that statistic does not exist — and running three seeds to 10,000
iterations to manufacture it would cost over thirty hours for a statistic that was never the
right one.

**Replacement: resample the independent trajectories with replacement, 10,000 draws, and report
a 95% CI on the A/B gap.** Better on two counts:

- it measures the uncertainty that actually dominates. `n_independent` ranges 4 to 39, while
  training-seed spreads contributed only 0.003 to 0.031 (R-35). Task 4 showed the 400-step
  out-of-sample **floor** moving from 0.3298 to 0.5372 between two trajectory samples at the
  same horizon — trajectory sampling, not seed variation, is the dominant term;
- it exists for a single run.

Reported alongside `n_independent` in every table. Where `n_independent` = 4 the CI will be very
wide, and that is the correct message rather than a defect of the method. The existing six-run
tables are recomputed under bootstrap CIs so the comparison is like for like.
**Evidence** `RUN` Task 4's floor instability; adopted as convention.
**Status** ADOPTED · **Relevance** METHOD


### M-26 — A pre-registered rule must be anchored to an adequately powered statistic · **NEW**
M-24 recorded that a pre-registered rule must be anchored to the *regime* the claim is about.
This is the same lesson in a second dimension, and it was learned the same way — by watching a
rule return the wrong answer for a reason that had nothing to do with the hypothesis.

Task 3's rule named a threshold on the training loss "at 2500". The quantity that phrase resolved
to on disk is `final_terms.state`, which is `curves.state[-1]` — **one 256-window minibatch
draw**. Its standard deviation is 0.1769. The effect the rule was written to
detect is 0.0143. The estimator therefore carries
**12.4× more noise than its own signal** and could never have decided the
question, in either direction.

Read literally the rule fired and would have retracted R-47 (R-55). Every adequately powered
estimator says the opposite, and says it consistently.

**What makes this recoverable rather than a free hand.** The estimator was changed *after* seeing
the result, and the change moved the verdict from *refutes the prior finding* to *confirms the
prior finding* — the direction that deserves the least trust. Two things carry the argument
instead of that judgement: the noise-to-signal calculation is computable without knowing which
arm is which, and the verdict is invariant across every tail length from 50 to 1000 iterations
and across a bootstrap that makes no tail choice at all.

**Convention adopted.** A pre-registered threshold on a training-loss quantity must name a
*windowed* statistic and its window, never an endpoint. Where an existing rule named an endpoint,
report both and show the noise-to-signal ratio, as R-55 does.
**Evidence** `RUN` `results/task3_control_arm.json`.
**Status** ADOPTED · **Relevance** METHOD


---

## E. Measured results

Steps 0–3 from `results/step3_report.txt` and `results/manifest.json`; Step 3.5 from
`results/task*_report.txt` and `results/task*.json`. torch 2.2.2, CPU. Step 3 wall clock 43.7 s.

*Every entry below carries its own `**Evidence**` line. R-01 to R-09 originally inherited it
from this header; the release consistency check (`scripts/ledger_check.py`) flagged that as
unverifiable per-entry and they were made explicit. No evidence was added that the header did
not already declare.*

### R-01 — Checkpoint inventory
1,995,569 parameters: `state_base` 636,672, `state_heads` 387,460, `auxiliary_base` 636,672, `auxiliary_heads` 334,765. Checkpoint iteration 5000. Loads under torch 2.2.2 with no fallback.
**Status** CONFIRMED · **Relevance** METHOD

### R-02 — Protocol A and B, clean
Seed 0: A = 0.7672, B = 1.2728. Seed-averaged over 20 seeds: A = 0.709 ± 0.053, B = 1.026 ± 0.184.
**Evidence** `RUN` `results/step3_report.txt`, `results/manifest.json`
**Status** CONFIRMED · **Relevance** CONTRIB
**Caveat** Read with M-06. The gap is episode sampling, not leakage.

**Superseded as headline by R-15 (Step 4)** — these are offset-0 figures, i.e. what the released evaluation code reports. Retained deliberately: that is itself the finding. Causal-convention figures are in R-15.

### R-03 — Hold-last floor
e = 1.0070, median r = 0.9649.
**Evidence** `RUN` `results/step2_acceptance.json`
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

**Evidence** `RUN` `results/step3_report.txt`
**Status** CONFIRMED · **Relevance** CONTRIB
**Note** The model is worse than the hold-last floor at one step, best at h=16, and converges back toward the floor thereafter. The h=1 result was the subject of O-02 — **now explained, see R-09.** These numbers remain correct for the stale convention; R-09 supersedes them as the headline figures.

### R-05 — Boundary crossing does not inflate error
Of 10 protocol-B trajectories, 5 crossed a reset. Crossing trajectories averaged 0.947; non-crossing averaged 1.599. The crossing trajectories scored **better**.
**Evidence** `RUN` `results/step3_report.txt`
**Status** CONFIRMED · **Relevance** CONTRIB
**Note** This refutes S-03. Recorded because a stated prediction being falsified by measurement is itself a result.

### R-06 — Convention swap is worth 0.066
Protocol A: 0.7672 under the evaluation convention, 0.7008 under the training convention.
**Evidence** `RUN` `results/step3_report.txt`
**Status** CONFIRMED · **Relevance** CONTRIB
**Caveat** ~~Not yet interpretable — see O-01 and O-05.~~ **Interpretable as of D-13:** the training alignment is causal, so the 0.066 is the cost the reference evaluation pays for feeding a stale action. It is a measurement of the B-05 defect, not evidence of leakage.

**Superseded as headline by R-15 (Step 4)**, which measures the same swap on both protocols, both metrics and a 20-seed spread.

### R-07 — Protocol B's noise sweep is non-monotonic
Protocol A rises cleanly with noise: 0.767, 0.886, 1.005, 1.220, 1.255, 1.381. Protocol B does not: 1.273, 1.229, 1.230, 0.977, 1.030, 1.213.
**Evidence** `RUN` `results/step3_report.txt`
**Status** CONFIRMED · **Relevance** CONTRIB
**Note** Most likely sampling variance swamping the effect, consistent with M-04's ±0.184 on protocol B. Not yet tested.

**Retested at Step 4 (R-15): still non-monotonic under both conventions**, so the convention is not the explanation. M-04 sampling variance remains the leading one.

### R-08 — Epistemic uncertainty dwarfs aleatoric
One-step check on a held-out window: aleatoric 0.003, epistemic 0.276, roughly a hundredfold ratio.
**Evidence** `RUN` `results/step3_report.txt`
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

**Evidence** `RUN` `results/task2_4_results.json`
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

### R-14 — Losses and gradients match the reference exactly · **NEW (Step 4) — THE ACCEPTANCE GATE**
One fixed batch of 16 held-out windows, both models loaded from `pretrain_rnn_ens.pt`,
`torch.randn_like` monkeypatched globally so both implementations draw identical samples.

| | zeros mode | fixed mode |
|---|---|---|
| all seven loss terms, max relative diff | **0.000e+00** | **0.000e+00** |
| weighted total | 0.000e+00 | 0.000e+00 |
| gradients, worst max-abs over 106 tensors | **0.000e+00** | **0.000e+00** |
| gradients, worst max-relative | 0.000e+00 | 0.000e+00 |

Thresholds were 1e-6 relative on losses and 1e-5 on gradients; the achieved value is exactly
zero in every cell.

**Non-vacuity checks**, because a comparison of two all-zero gradient sets would pass
trivially: in `fixed` mode 106/106 tensors carry a non-zero gradient (max magnitude 2.334);
in `zeros` mode 81/106 do, and the 25 exceptions are exactly the set C-11 predicts. The two
implementations agree on **which** parameters receive gradient, not merely on the values.

Import: `from rsl_rl.modules import SystemDynamicsEnsemble` now succeeds directly after
installing `gitpython` and `tensordict` (both pure-Python, neither disturbs the torch pin),
so no stubs were needed — an improvement on the `importlib` route R-11 had to use.
**Evidence** `RUN` `step4_3_differential.json`.
**Status** CONFIRMED · **Relevance** METHOD
**Consequence** The trainer optimises the same objective as the reference. Step 5 onward is
on solid ground.

### R-15 — Step 3 results restated under the causal convention · **NEW (Step 4)**
The offset-0 column is what the released evaluation code reports; the offset-1 column is
what the checkpoint can actually do; the gap is the measured cost of B-05. Both are real and
both are retained.

| | offset 0 (released eval) | offset 1 (causal) | delta |
|---|---|---|---|
| A clean, relative-L1 | 0.7672 | **0.7008** | −0.0664 |
| B clean, relative-L1 | 1.2728 | **1.2046** | −0.0682 |
| A clean, **nRMSE @368** | 1.3228 | **0.7572** | −0.5656 |
| B clean, nRMSE @368 | 5.6959 | 5.4008 | −0.2951 |
| A, 20-seed | 0.7088 ± 0.0526 | **0.6499 ± 0.0586** | −0.0589 |
| B, 20-seed | 1.0256 ± 0.1840 | **0.9878 ± 0.1987** | −0.0378 |

Noise sweep A (clean → 0.8): offset 1 gives 0.7008, 0.8141, 0.9841, 1.2036, 1.2409, 1.3737.

**Qualitative conclusions all survive the convention change:**
- **R-05 survives.** Crossing trajectories still score *better* than non-crossing under both
  conventions (0.890 vs 1.519 at offset 1). Boundary crossing still does not explain the A/B gap.
- **D-12 survives.** Per-episode difficulty spans 0.523–1.585, a 3.0× ratio (was 2.8×), and
  remains uncorrelated with commanded speed (r = +0.09, was +0.00). The held-out pair is
  still on the easy side, 0.626 against a population mean of 1.017.
- **R-07 survives.** Protocol B's noise sweep remains non-monotonic under both conventions;
  protocol A remains monotonic under both. Consistent with M-04 sampling variance.
- **M-04 survives.** A–B separation is 1.6σ at offset 1 (was 1.7σ). Still underpowered.

**Evidence** `RUN` `step4_0a_results.json`.
**Status** CONFIRMED · **Relevance** CONTRIB

### R-16 — CPU timing · **NEW (Step 4)**
20 timed iterations after 3 warm-up, per configuration.

| ensemble | batch | s/iter | 500 iters | 2500 iters | peak RSS |
|---|---|---|---|---|---|
| 1 | 1024 | 4.623 ± 0.523 | 38.5 min | 3.2 h | 1.7 GB |
| 1 | 256 | 1.659 ± 0.527 | 13.8 min | 1.2 h | 1.7 GB |
| **5** | **1024** | **37.179 ± 5.316** | **5.2 h** | **1.1 days** | **4.8 GB** |
| 5 | 256 | 5.926 ± 0.318 | 49.4 min | 4.1 h | 4.8 GB |

The reference configuration (ensemble 5, batch 1024) scales **superlinearly**: 8.0× the
ensemble-1 cost for 5× the heads, against 3.6× at batch 256. Per sample that is 36.3 ms at
batch 1024 versus 23.2 ms at batch 256, so the large batch is 1.56× *less* efficient. With
4.8 GB peak RSS this is memory pressure on a 2-core machine, not compute.

Step 6 five-fold cross-validation (M-05) at the reference configuration: **1.1 days** at 500
iterations per fold, 5.4 days at 2500.
**Evidence** `RUN` `step4_5_timing.json`.
**Status** CONFIRMED · **Relevance** INTERNAL
**Recommendation** Single runs local (5.2 h each, overnight). For the Step 6 five-fold sweep,
either drop to batch 256 — which is faster per epoch anyway — or rent. Do not run five folds
at batch 1024 locally.

### R-17 — Overfit one batch: partial, and the collapse prediction confirmed · **NEW (Step 4)**
Ensemble 1, batch 1024, fresh random init, one fixed batch, 451 iterations in 2708 s before
the wall-clock cap (X-06).

**Memorisation: INCOMPLETE, not failed.** State loss fell 49.227 → 4.124, a 91.6% reduction,
monotonically and still falling. It did not reach the 1e-4 threshold; 4.124 summed over 45
dimensions is a per-dimension RMSE of 0.303 in normalised units, so the batch is not
memorised. Nothing indicates a bug — the curve is smooth and monotone — but the test as
specified (2000 iterations) was not completed within the CPU budget and **must not be
recorded as passed**.

**All active terms moved; all inert terms stayed exactly zero:**

| term | first | last | moved |
|---|---|---|---|
| state | 4.923e+01 | 4.124e+00 | yes |
| sequence | 0 | 0 | no — inert, prediction_type "single" |
| bound | 1.000e+00 | 9.587e-01 | yes |
| kl | 0 | 0 | no — inert, rssm only |
| extension | 0 | 0 | no — inert, extension_dim 0 |
| contact | 6.866e-01 | 5.163e-02 | yes |
| termination | 7.040e-01 | 4.360e-04 | yes |

The termination term collapsed to 4.4e-04 within ~50 iterations, confirming rather than
assuming the D-03/X-04 expectation that an all-zero target drives its logits to −∞.

**Collapse monitor — prediction CONFIRMED.** `exp(log_delta_logstd)` fell monotonically from
0.9999 to 0.9607 across all 18 samples, with no reversal. The 1b prediction was made from
the objective's algebra before running, and it holds on a single batch from random init.
The rate feeds C-12.
**Evidence** `RUN` `step4_4_overfit_ens1.json`, `figures/step4_overfit_ens1.png`.
**Status** CONFIRMED (collapse) · **INCOMPLETE** (memorisation) · **Relevance** CONTRIB


### R-18 — Overfit one batch, rerun: the trainer is proven · **NEW (Step 5)**
R-17 was inconclusive because of its own configuration, not a defect: batch 1024 with an
8-step autoregressive objective at the reference's full-dataset learning rate of 1e-4. Rerun
with the confounds removed — **batch 32, lr 1e-3, 2000 iterations, no wall-clock cap**,
everything else identical, ensemble 1 as in X-06.

| | R-17 (batch 1024, lr 1e-4) | **R-18 (batch 32, lr 1e-3)** |
|---|---|---|
| iterations | 451 (capped) | **2001** |
| s/iter | 6.00 | **0.229** |
| state loss | 49.227 → 4.124 | **41.871 → 0.027802** |
| reduction | 91.6% | **99.93%, a factor of 1506** |
| per-dim RMSE equivalent | 0.303 sd | **0.0249 sd** |
| contact | 6.87e-01 → 5.16e-02 | **6.86e-01 → 4.50e-05** |
| termination | 7.04e-01 → 4.36e-04 | **7.07e-01 → 1.01e-06** |

**Verdict: decisive.** The literal 1e-4 threshold was not reached, but that threshold is a
*sum over 45 dimensions* — it demands a per-dimension RMSE of 0.0015 normalised sd, which is
far below what "can this code memorise" requires. What was reached is a per-dimension error
of 2.5% of a standard deviation, with the contact term at 4.5e-05 and the termination term at
1.0e-06.

The run was **still descending at the cap**, not plateaued: block means fall monotonically
across all ten 200-iteration blocks (4.101, 0.535, 0.252, 0.160, 0.107, 0.135, 0.057, 0.067,
0.037, 0.033), and iterations 1500–1999 average 2.62× lower than 1000–1499. So there is no
structural limit of the kind 5.1 asked to watch for. The trainer memorises; Step 5 may
proceed.

The three inert terms (`sequence`, `kl`, `extension`) stayed exactly zero throughout, as
C-09/M-07 predict; every live term moved in the right direction.

**Reproducibility check:** the run was executed twice — once to measure and once to regenerate
the report after the repository restructure — and produced bitwise-identical loss values
(41.871338, 7.060672, 3.942659, …). The trainer is deterministic under a fixed seed.
**Evidence** `RUN` `results/step4_4_overfit_b32lr1e3.json`,
`figures/step4_overfit_b32lr1e3.png`.
**Status** CONFIRMED · **Relevance** METHOD
**Supersedes** R-17 as the trainer-validity test. R-17 is retained: its 45-minute cost at the
reference configuration is what R-16's timing predicted, and that agreement is its own
small confirmation.


### R-19 — Arm A (autoregressive, faithful), seed 0 · **NEW (Step 5)**
The first of the six main runs, run alone per the staged launch. 2500 iterations, ensemble 1,
batch 256, lr 1e-4, weight decay 1e-5, causal alignment, 7,687 training windows, no gradient
clipping (M-15). **1.28 h wall clock at 1.850 s/iter**, against a 1.2 h projection — 7% over,
within R-16's measured variance.

**Training health.** `state` 47.64 → 1.559; `contact` 6.87e-01 → 9.97e-03; `termination`
7.04e-01 → 2.91e-06; `bound` 1.000 → 0.791. Block means over 250-iteration windows fall
monotonically throughout: 19.25, 7.74, 4.97, 3.74, 3.07, 2.60, 2.26, 2.01, 1.79, 1.60. Slope
over the final 250 iterations **−7.59e-04 per iteration — still falling steeply**, so 2500
iterations is not convergence.

**Gradient norms and spikes.** Mean 11.28, median 10.73, p5–p95 8.01–15.75, p99 23.79, max
53.09 at iteration 0 (48.09 excluding it). **Zero spikes** above 5× the trailing 50-iteration
median. The excursions seen in the R-18 overfit were an artifact of its lr 1e-3; at the
reference lr 1e-4 the run is quiet, and the decision not to add clipping (X-08) cost nothing.

**Evaluation, protocol A clean, offset 1, held-out episodes:**

| h | e@500 | e@2500 | floor | ratio@2500 | nRMSE@500 | nRMSE@2500 | nRMSE floor |
|---|---|---|---|---|---|---|---|
| 1 | 0.1515 | 0.1579 | 0.1107 | 1.427 | 0.1848 | **0.1486** | 0.2214 |
| 4 | 0.3003 | 0.2645 | 0.2407 | 1.099 | 0.2887 | 0.2187 | 0.4187 |
| 8 | 0.3995 | **0.3163** | 0.3603 | 0.878 | 0.3643 | **0.2700** | 0.5585 |
| 16 | 0.4710 | 0.3761 | 0.5309 | 0.708 | 0.4646 | 0.3777 | 0.7107 |
| 32 | 0.5348 | 0.4020 | 0.5733 | 0.701 | 0.5524 | 0.4192 | 0.6802 |
| 64 | 0.6699 | 0.4747 | 0.6787 | 0.699 | 0.7331 | 0.4881 | 0.7409 |
| 128 | 0.8985 | 0.5915 | 0.7542 | 0.784 | 1.1268 | 0.7009 | 0.8224 |
| 256 | 1.7512 | 0.7444 | 0.9369 | 0.795 | 2.0510 | 0.9436 | 0.9031 |
| 368 | 2.5589 | **0.7938** | 1.0070 | 0.788 | 3.5351 | **1.0460** | 0.9601 |

At 500 iterations the model is worse than the hold-last floor at every horizon beyond h=4 and
badly so at long horizon (e@368 2.56 against a floor of 1.01). By 2500 it beats the floor from
h=8 outward. For scale: the released checkpoint scores e@8 0.1310 and e@368 0.7008 (R-09), so
2500 iterations from random init reaches the reference's long-horizon number (0.794 vs 0.701)
while remaining far behind at short horizon (0.316 vs 0.131) — consistent with C-13/O-12's
conclusion that the released checkpoint saw far more optimisation than any documented count.

Noise sweep at 2500 is nearly flat and non-monotonic in the low scales (0.785, 0.784, 0.842,
0.862, 0.944 for 0.1–0.8), i.e. the model's clean error already dominates the injected noise.
**Evidence** `RUN` `results/step5_armA_seed0.json`, `results/step5_armA_seed0_report.txt`.
**Status** CONFIRMED · **Relevance** CONTRIB
**Note** Arms B and the remaining seeds are not yet run, so no A-versus-B statement is made
here. M-16's rule governs that and remains unevaluated.
**Headline framing SUPERSEDED by R-35.** This entry's evaluation figures were computed at
n=10 overlapping trajectories with form-2 aggregation; they stand as measurements under the
reference protocol. Any "the claim reproduces" reading built on them is withdrawn.

### R-20 — The two metrics disagree in DIRECTION at h=1 · **NEW (Step 5)**
From R-19's 2500 checkpoint:

| | model | hold-last floor | verdict |
|---|---|---|---|
| relative-L1 e@1 | 0.1579 | 0.1107 | model **1.43x worse** |
| nRMSE@1 | 0.1486 | 0.2214 | model **0.67x, i.e. better** |

Not a small disagreement in magnitude — an inversion of the ordering. The cause is the one
M-09 identified: relative-L1 divides by `sum_d |true[t,d]|` recomputed at every timestep, so
timesteps whose normalised state passes near zero dominate the average; nRMSE divides by a
fixed per-dimension training-set scale and does not.

This matters for the Step 5 deliverable, because h=1 and h=8 are exactly where the pre-registered
rule (M-16) is evaluated. At h=8 both metrics agree that the model beats the floor (0.878 and
0.483 respectively), so the rule is safe there — but the h=1 inversion is a concrete
demonstration that a paper reporting only relative-L1 can state a short-horizon ordering
backwards.
**Evidence** `RUN` `results/step5_armA_seed0.json`.
**Status** CONFIRMED · **Relevance** CONTRIB

### R-21 — nRMSE caveat: a near-constant dimension inflates its group · **NEW (Step 5)**
The projected-gravity group's nRMSE at h=368 reads 7.61 while its relative-L1 median reads
1.06. A fixed denominator cannot blow up per timestep, which was the point of M-12, but it can
still be *small*: the stored scale for the gravity z-component is 0.0292, because the config's
`state_data_std` of 0.04 overestimates that dimension's true spread by ~34x (M-12). Dividing
by 0.0292 amplifies any error in that one dimension, and it dominates the three-dimensional
group mean.

So nRMSE is the right instrument for the aggregate and for well-scaled groups, and it should
be read per-dimension rather than per-group where a group contains a near-constant dimension.
Neither metric is trustworthy for projected gravity; that limitation belongs to the
normalisation, not to either metric.
**Evidence** `RUN` `results/step5_armA_seed0.json`; `DATA` M-12's stored scale vector.
**Status** CONFIRMED · **Relevance** METHOD


### R-22 — The paper's central claim REPRODUCES: autoregressive beats teacher forcing · **NEW (Step 6)**
Six runs, three seeds per arm, 2500 iterations each, 5.96 h total wall clock. Configuration
identical across arms and differing in exactly one line — the state branch's feedback.
**Zero gradient spikes in any of the six runs.**

**relative-L1 e** (mean ± sd over 3 seeds; hold-last floor beside):

| | Arm A autoregressive | Arm B teacher forcing | floor |
|---|---|---|---|
| h=8 @500 | **0.4022 ± 0.0107** | 0.4254 ± 0.0344 | 0.3603 |
| h=8 @2500 | **0.3263 ± 0.0074** | 0.3915 ± 0.0150 | 0.3603 |
| h=368 @500 | **2.0576 ± 0.3555** | 6.1592 ± 1.2868 | 1.0070 |
| h=368 @2500 | **0.9333 ± 0.0988** | 4.0171 ± 0.3022 | 1.0070 |

**nRMSE:**

| | Arm A | Arm B | floor |
|---|---|---|---|
| h=8 @500 | **0.3648 ± 0.0283** | 0.3991 ± 0.0153 | 0.5585 |
| h=8 @2500 | **0.2805 ± 0.0075** | 0.3210 ± 0.0183 | 0.5585 |
| h=368 @500 | **2.6776 ± 0.6896** | 7.1737 ± 0.5970 | 0.9601 |
| h=368 @2500 | **1.1580 ± 0.1148** | 4.5621 ± 0.4582 | 0.9601 |

**M-16 evaluated, both metrics separately (6.4):**

| | relative-L1 | nRMSE |
|---|---|---|
| leader @500, h=8 | A | A |
| leader @2500, h=8 | A | A |
| condition 1, ordering same | **True** | **True** |
| \|A−B\| @2500 | 0.0652 | 0.0405 |
| max within-arm seed sd | 0.0150 | 0.0183 |
| condition 2, difference exceeds spread | **True** | **True** |
| **verdict** | **SETTLED** | **SETTLED** |

**The two metrics agree.** Both pre-registered conditions hold under both, so the rule returns
a reportable result rather than "cannot be settled". The autoregressive objective — the one the
reference implements and the paper argues for — is better, and the margin at long horizon is
not marginal: **4.3× on relative-L1 and 3.9× on nRMSE at h=368**.

**The 6.1 pre-registered flip interpretation does not apply: there was no flip.** Arm A leads
at both checkpoints under both metrics. That annotation is left in place unused, which is the
correct outcome for a pre-registration that did not fire.

Worth recording against the reasoning behind it: the textbook expectation was that teacher
forcing would fit *faster early* and generalise worse later. The second half held emphatically;
the first did not. At h=8 @500 Arm A already leads (0.4022 vs 0.4254), so teacher forcing never
led at any measured point.
**Evidence** `RUN` `results/step6_analysis.json`, `results/step5_arm{A,B}_seed{0,1,2}.json`,
`figures/step6_arms_comparison.png`.
**Status** CONFIRMED as measurements under the reference protocol · **Relevance** CONTRIB
**"The paper's central claim reproduces" framing WITHDRAWN, superseded by R-35.** Under
independent trajectories and pooled aggregation M-16 returns *cannot be settled* in all eight
arena/length/metric combinations. The h=8 numbers here rest on `n_independent = 4` (M-20). The
long-horizon separation survives and is recorded as R-38, explicitly NOT pre-registered.

### R-23 — Teacher forcing reaches a 3× lower training loss and a 4× worse rollout · **NEW (Step 6)**
The mechanism behind R-22, and the cleanest single measurement in the project.

| | Arm A autoregressive | Arm B teacher forcing |
|---|---|---|
| final training `state` loss | 1.4956 – 1.5588 | **0.4415 – 0.5119** |
| gradient norm, median | 10.73 – 10.91 | **2.15 – 2.26** |
| gradient norm, max | 49.2 – 53.1 | 7.6 – 9.8 |
| rollout e @h=368 | **0.9333** | 4.0171 |

Arm B optimises its own objective roughly **3× better** — lower loss, gradients 5× smaller,
a visibly easier problem — and then rolls out **4.3× worse**. This is exposure bias measured
end to end on the released architecture: the objective teacher forcing minimises is not the
objective that matters, and its apparent training advantage is precisely what makes it worse
at deployment.

It also explains why Arm B never led even at 500 iterations. Teacher forcing does not converge
faster *toward the rollout objective*; it converges faster toward a different one.
**Evidence** `RUN` `results/step6_analysis.json`.
**Status** CONFIRMED · **Relevance** CONTRIB

### R-24 — Pooled collapse fit across six independent runs · **NEW (Step 6)**
| run | rate/iter | stderr | rate/lr | exp(log_delta)@2500 |
|---|---|---|---|---|
| A seed 0 | −9.3641e-05 | 2.64e-08 | 0.936 | 0.791385 |
| A seed 1 | −9.3589e-05 | 2.60e-08 | 0.936 | 0.791434 |
| A seed 2 | −9.3621e-05 | 2.61e-08 | 0.936 | 0.791399 |
| B seed 0 | −9.5107e-05 | 7.53e-08 | 0.951 | 0.788186 |
| B seed 1 | −9.5099e-05 | 7.50e-08 | 0.951 | 0.788199 |
| B seed 2 | −9.5117e-05 | 7.57e-08 | 0.951 | 0.788168 |

**Pooled: −9.4362e-05 ± 3.33e-07** (sem over 6 runs). Run-to-run sd 8.168e-07 — **0.87% of the
mean**. Six independent trajectories agree to within 1%, and the three seeds within each arm
agree to five significant figures. This is no longer an estimate from heterogeneous runs; it is
a pinned constant.

Placed beside the earlier measurements: overfit 451 iters at lr 1e-4 gave 0.93; overfit 2000
iters at lr 1e-3 gave 0.70; the pooled six give **0.9436**. `rate ≈ lr` holds tightly at the
reference learning rate and degrades as lr grows.

Small systematic detail worth recording: the arms differ, 0.936 versus 0.951, far outside the
within-arm spread. The bound-loss gradient on `log_delta_logstd` is identical in both arms, so
the difference must come from the state loss's σ path, which teacher forcing changes. A 1.6%
effect, but a real one.

**From the pooled fit, not by extrapolation:** reaching the released checkpoint's −14.4629
requires **153,270 iterations** at lr 1e-4, or **lr 3.07e-03 — 31× the configured value** — to
arrive within its own tagged 5000.
**Evidence** `RUN` `results/step6_analysis.json`.
**Status** CONFIRMED · **Relevance** CONTRIB

### R-25 — `min_logstd` gives O-12 a second, slower, independent axis · **NEW (Step 6)**
The released checkpoint's `state_min_logstd` mean is **−9.8128** (σ = 5.475e-05), tight across
heads (−9.783, −9.814, −9.814, −9.831, −9.822), against an initialisation of −5.0
(`mlp.py:78`). It has travelled **−4.813 in log space**, shrinking σ by a factor of 0.008.

Arm A's measured drift for the same parameter is **−1.797e-05 per iteration**, which is
**5.2× slower** than `log_delta_logstd`'s −9.364e-05 — exactly what C-11 predicts, since
`min_logstd` cancels out of the bound loss and moves only through the weaker σ path.

Order-of-magnitude implication (explicitly *not* a fitted count: `min_logstd`'s gradient depends
on σ, which is itself shrinking, so its drift is not expected to stay linear):

| parameter | gradient path | implied iterations |
|---|---|---|
| `log_delta_logstd` | bound loss, constant sign | **1.5e5** |
| `min_logstd` | state-loss σ term only | **2.7e5** |

**Two variance parameters, on different gradient paths, drifting at rates 5× apart,
independently imply order-1e5 optimisation steps.** Against a config saying 500, a paper saying
2500, and a checkpoint tagged 5000. One parameter admits several escape hatches; two agreeing
across a 5× rate difference narrows them considerably.
**Evidence** `RUN` `results/step6_3_min_logstd.json`; `DATA` released checkpoint; `SRC`
`mlp.py:78`.
**Status** CONFIRMED · **Relevance** CONTRIB

### R-26 — Neither arm has converged at the paper's own iteration count · **NEW (Step 6)**
State-loss slope over the final 250 iterations, all six runs:

| run | A seed 0 | A seed 1 | A seed 2 | B seed 0 | B seed 1 | B seed 2 |
|---|---|---|---|---|---|---|
| slope/iter | −7.59e-04 | −6.54e-04 | −3.89e-04 | −2.54e-04 | −2.10e-04 | −1.15e-04 |

**Every run is still descending at 2500**, the count the paper's Table S7 states. Arm A is
falling 2–3× faster than Arm B at the cap, so the R-22 margin is if anything conservative —
extending the budget would be expected to widen it, not close it.

This is reported alongside R-22 rather than as a caveat that weakens it: M-16's conditions were
met at this budget, so the comparison stands, and the non-convergence says the *absolute*
numbers are not the reference's and were never going to be. It connects directly to O-12 and
C-13 — 2500 iterations is not where this objective settles.
**Evidence** `RUN` `results/step6_analysis.json`.
**Status** CONFIRMED · **Relevance** CONTRIB


### R-27 — The released checkpoint under nRMSE: it LOSES to the hold-last floor at long horizon · **NEW (batch 1)**
The question this batch was built to answer, and the answer reverses once the evaluation is
properly powered.

Released checkpoint, protocol A, held-out episodes, `action_offset=1`, fixed training-episode
scale vector (verified bitwise identical to the stored one):

| h | e model | e floor | ratio | nRMSE model | nRMSE floor | ratio |
|---|---|---|---|---|---|---|
| 1 | 0.0915 | 0.1107 | 0.827 | 0.1084 | 0.2214 | 0.490 |
| 8 | 0.1310 | 0.3603 | 0.364 | 0.1299 | 0.5585 | 0.233 |
| 32 | 0.2609 | 0.5733 | 0.455 | 0.2254 | 0.6802 | 0.331 |
| 128 | 0.5096 | 0.7542 | 0.676 | 0.5211 | 0.8224 | 0.634 |
| 368 | 0.7008 | 1.0070 | 0.696 | 0.7572 | 0.9601 | 0.789 |

At **n=10 — the reference's own protocol** — the checkpoint appears to beat the floor under
both metrics at every horizon. **That conclusion does not survive M-17.** At n=100:

| | model | floor | verdict |
|---|---|---|---|
| relative-L1 @368 | 0.6193 | 0.9724 | **beats the floor by 36%** |
| nRMSE @368 | **1.4268** | **1.1087** | **LOSES to the floor by 29%** |

and at n=400 the gap widens to 1.8872 against 1.1127. The model beats the floor in **100% of
eval seeds under relative-L1 at every n**, and loses in **100% of seeds under nRMSE for n ≥ 50**.

**So the two metrics disagree in direction about the released artifact itself, robustly, at
long horizon.** This is not a statement about our training budget — it is measured on the
authors' own released weights. Under the paper's metric the checkpoint is clearly better than
assuming nothing changes; under a fixed-denominator metric that is sensitive to diverging
rollouts, it is worse. Both are defensible metrics; they disagree because a minority of
rollouts diverge badly and relative-L1's per-timestep normalisation hides that.

Per-group at h=368 shows where it comes from: projected gravity nRMSE 3.0962 against a floor
of 0.7914, and base linear velocity 0.7604 against 0.6762, while joint positions (0.4493 vs
0.9849), velocities (0.4116 vs 0.9379) and torques (0.7645 vs 1.0930) are all far better than
the floor. The checkpoint models the joints well and the base badly, and nRMSE weights the
base failure more heavily.
**Evidence** `RUN` `results/task2_reference_nrmse.json`, `results/task3_4_power_ddof.json`,
`results/task3b_convergence.json`.
**Status** CONFIRMED · **Relevance** CONTRIB
**Correction** An earlier statement of this result, computed at n=10, reported the opposite
("BELOW the floor — it beats it by 21.1%"). That was an artifact of the reference's
10-trajectory protocol; see M-17 and S-09.

### R-28 — Re-evaluation at 100 trajectories: M-16 unchanged, M-04 revised · **NEW (batch 1)**
Every checkpoint re-evaluated at 100 trajectories instead of 10. No retraining.

**M-16 re-evaluated at n=100 with `ddof=1`:**

| | relative-L1 | nRMSE |
|---|---|---|
| leader @500 / @2500, h=8 | A / A | A / A |
| A@2500 | 0.2645 ± 0.0105 | 0.3121 ± 0.0100 |
| B@2500 | 0.3124 ± 0.0172 | 0.3534 ± 0.0092 |
| \|A−B\| vs max sd | 0.0479 > 0.0172 | 0.0414 > 0.0100 |
| **verdict** | **SETTLED** | **SETTLED** |

**Unchanged from the 10-trajectory evaluation, on both metrics, and the metrics still agree.**
The central claim (R-22) is robust to the power fix — which is worth stating precisely because
R-27 shows another conclusion in this project was not.

**M-04 revised.** Evaluation-seed spread over 20 seeds, released checkpoint:

| n | relative-L1 | nRMSE |
|---|---|---|
| 10 | 0.6499 ± 0.0601 | 1.0636 ± 0.3912 |
| 100 | 0.6430 ± 0.0186 | 1.6333 ± 0.2639 |

relative-L1's spread shrinks 3.23×, almost exactly the √10 = 3.16 of pure sampling noise, and
its mean barely moves. nRMSE's spread shrinks only 1.48× **and its mean moves by 54%** — the
signature of bias rather than noise, exactly as M-17 describes.
**Evidence** `RUN` `results/task3_4_power_ddof.json`.
**Status** CONFIRMED · **Relevance** CONTRIB
**Note** The 10-trajectory numbers are retained throughout the ledger: they are what the
reference protocol yields, and the difference between the two is itself the result.


### R-29 — The released checkpoint loses on 7 of 45 dimensions, and one of them carries R-27 · **NEW**
The gate on R-27. Per-dimension nRMSE at h=368, pooled over 3,200 trajectories (8 eval seeds x
400), released checkpoint against the hold-last floor.

**The model loses on 7 of 45 dimensions**: `v_z`, `w_x`, `w_y`, `g_x`, `g_y`, `g_z`,
`tau_RF_HAA`. It wins on the other 38, several by a wide margin (`q_RH_HAA` 0.642 vs 1.533,
`qd_RH_HAA` 0.684 vs 1.531).

One dimension dominates everything:

| dim | stored scale | model | floor | ratio |
|---|---|---|---|---|
| `g_z` | **0.0292** | **52.3101** | 0.4386 | **119×** |
| `g_y` | 0.9046 | 5.3002 | 1.1209 | 4.7× |
| `g_x` | 0.9418 | 1.9372 | 1.1099 | 1.7× |
| `v_x` | 1.1846 | 0.3054 | 0.6116 | 0.50 |

**How the aggregate is computed matters enormously, and this was never stated before:**

| aggregation | model | floor | verdict |
|---|---|---|---|
| **form 2**, mean over dims of `RMSE_d/scale_d`, all 45 — *as implemented, and used in R-27* | 1.9583 | 1.1169 | model **loses** |
| form 2, 42 dims, gravity excluded | **0.6804** | 1.1331 | model **beats by 40%** |
| **form 1**, `sqrt(mean_d MSE_d) / mean(scale)`, all 45 | **1.1103** | 1.1750 | model **beats** |
| form 1, 42 dims, gravity excluded | 0.6702 | 1.1647 | model **beats by 42%** |

R-27's conclusion holds under exactly one of the four, and that one is a mean of ratios in
which a single dimension whose scale is a normalisation artifact contributes 52.3 out of a
45-term average. `g_z`'s scale is 0.0292 because the config's `state_data_std` of 0.04
overestimates that dimension's true spread by ~34× (M-12) — the dimension is near-constant, so
any error in it is amplified by a factor the physics does not justify.
**Evidence** `RUN` `results/taskAB_gate_r27.json`.
**Status** CONFIRMED · **Relevance** CONTRIB
**Consequence** R-27 is refuted; see S-10. What survives is narrower and still worth reporting:
the released checkpoint models the **joints** well and the **base orientation and angular
velocity** poorly, losing to a constant predictor on `v_z`, `w_x`, `w_y` and the gravity vector.

### R-30 — The "heavy tail" is two short regions, not a property of the model · **NEW**
The second gate on R-27, and it fails too. Per-trajectory normalised squared error at h=368
over 3,200 overlapping trajectories: the worst 5% carry **92.6%** of the total, and
max/median is 2,893×. That looks like a severe heavy tail — until the trajectories are
checked for independence.

The 100–400 trajectories are drawn from ~600 valid start points per held-out episode, so they
overlap heavily. Clustering the tail trajectories by start row with a 400-row separation:

| region | rows | episode | tail trajectories |
|---|---|---|---|
| 1 | 1469–1597 | 1 | 113 |
| 2 | 8414–8593 | 8 | 47 |

**Two distinct regions**, together spanning ~310 of 2,000 held-out rows. The effective sample
size behind the tail is 2, not 400.

Restricted to strictly **non-overlapping** trajectories — 4 exist at 400 steps (starts 999,
1399, 7999, 8399) — the tail disappears entirely: per-trajectory totals 5,195 / 27,651 /
32,785 / 25,624, max/median **1.2×**. And on those four the model **beats** the floor
(nRMSE 0.7323 vs 0.9813).

So the divergence is real but localised: two short stretches of ANYmal data on which the
released checkpoint's rollout diverges. That is a finding about those stretches, not about the
model's error distribution in general, and it cannot support a claim of the form "the model's
rollout error is heavy-tailed".
**Evidence** `RUN` `results/taskAB_gate_r27.json`.
**Status** CONFIRMED · **Relevance** CONTRIB
**Consequence** M-17's mechanism is narrowed — see M-19.

### R-31 — M-16 is robust to the aggregation choice · **NEW**
The correction to R-27 raises the obvious question of whether the central claim rests on the
same flaw. It does not. Arm A vs Arm B at h=368, n=100, `ddof=1`, under four variants:

| metric | Arm A | Arm B | \|A−B\| vs sd | floor | A vs floor |
|---|---|---|---|---|---|
| relative-L1 | 0.5953 ± 0.0589 | 2.7210 ± 0.2488 | 2.126 > 0.249 | 0.9724 | **beats** |
| nRMSE form 2, all 45 | 0.9540 ± 0.1322 | 4.0593 ± 0.3427 | 3.105 > 0.343 | 1.1087 | **beats** |
| nRMSE form 2, no gravity | 0.5606 ± 0.0423 | 2.5065 ± 0.1259 | 1.946 > 0.126 | 1.1234 | **beats** |
| nRMSE form 1, all 45 | 0.5965 ± 0.0543 | 2.7613 ± 0.2695 | 2.165 > 0.270 | 1.1731 | **beats** |

**SETTLED under all four**, with Arm A leading by 4–5× and beating the floor in every case.

This also refutes a claim carried since R-22: that Arm A **fails** the nRMSE floor at h=368 in
all three seeds. That was measured at n=10 (1.1580 vs 0.9601); at n=100 Arm A beats the floor
under every aggregation. The motivation for Task D's undertraining question was therefore
partly built on an n=10 artifact.
**Evidence** `RUN` `results/taskAB_gate_r27.json` and the M-16 aggregation check.
**Status** CONFIRMED · **Relevance** CONTRIB


### R-32 — The retraction's arithmetic, verified · **NEW**
Pooled over the entire held-out pool of 1,202 start points in one pass.

- form-2 sum over 45 dimensions = **88.16**; `g_z` alone contributes **52.49 (60%)**, all three
  gravity dimensions **59.68 (68%)**. A 45-term average in which one term is 60% of the total.
- the model loses on **7 of 45** dimensions: `v_z`, `w_x`, `w_y`, `g_x`, `g_y`, `g_z`, `tau_RF_HAA`.

**The narrow claim that survives, stated as narrow.** On `g_z` — the most nearly-constant
dimension in the state vector — the released checkpoint scores **52.49 against a floor of
0.4392, a ratio of 119.5×**. The floor is strong there precisely because the dimension barely
moves; the learned delta actively degrades it. That is a real, specific defect and it is not an
aggregation artifact — it is a per-dimension number.

**And the config explains it.** `state_data_std[g_z] = 0.04`, while the measured normalised
spread is 0.0292, so the true raw spread is 0.04 × 0.0292 = **0.001168** and the constant
overestimates it by **34.3×**. The training loss is a sum of squared errors in normalised
space, so this dimension is weighted **1/1174** — about **3.1 orders of magnitude** — below a
correctly scaled one. The model has almost no incentive to fit `g_z`, and it does not. Defect
and cause, connected.
**Evidence** `RUN` `results/batch1_post_retraction.json`.
**Status** CONFIRMED · **Relevance** CONTRIB

### R-33 — The Jensen mechanism is SUPPORTED at 40 seeds · **NEW**
Rerun with 40 evaluation seeds, resampled from a single stored rollout of all 1,202 held-out
start points, so the resampling is exact.

| n | mean_s MSE (should be flat) | sqrt(mean_s MSE) (flat) | mean_s sqrt(MSE) (rises) | bias | mean n_independent |
|---|---|---|---|---|---|
| 10 | 98.97 | 1.9681 | 1.1526 | 0.8156 | 3.0 |
| 25 | 107.62 | 2.0503 | 1.4131 | 0.6372 | 3.9 |
| 50 | 100.93 | 1.9678 | 1.5138 | 0.4540 | 4.0 |
| 100 | 103.35 | 2.0280 | 1.6915 | 0.3366 | 4.0 |
| 400 | 96.44 | 1.9649 | 1.8721 | 0.0929 | 4.0 |

`sqrt(mean_s MSE)` is flat to **1.043×** and `mean_s sqrt(MSE)` rises **1.624×** monotonically
toward it, with the bias falling from 0.816 to 0.093. **Verdict: SUPPORTED.**

`mean_s MSE` still varies 1.116× — improved from 1.534× at 8 seeds but not flat to 5%. As the
brief anticipated, it is not diagnostic: it is the mean of a quantity whose per-trajectory
max/median is ~2,900×, so its own standard error stays large at any feasible seed count. The
criterion is therefore the two rows that bear on the mechanism.

The estimator conclusion is independent of the mechanism and stands: per-seed-averaged nRMSE at
n=10 is **41% below** the pooled form. Pooled is adopted.
**Evidence** `RUN` `results/batch1_post_retraction.json`.
**Status** SUPPORTED · **Relevance** CONTRIB

### R-34 — The released checkpoint characterised on all ten episodes, independent trajectories · **NEW**
Twenty non-overlapping 400-step trajectories, two per episode, `n_independent = 20` by
construction. Justified because the checkpoint was trained on the entire CSV, so restricting it
to the held-out pair buys nothing.

**Bootstrap over the 20 trajectories, 10,000 resamples, relative-L1 (the paper's metric):**

| h | model | floor | ratio [95% CI] | P(model loses) |
|---|---|---|---|---|
| 8 | 0.1585 | 0.6564 | **0.241 [0.171, 0.323]** | 0% |
| 32 | 0.2418 | 0.8128 | **0.297 [0.206, 0.401]** | 0% |
| 64 | 0.4322 | 0.8587 | **0.504 [0.368, 0.667]** | 0% |
| 128 | 0.8878 | 0.9743 | 0.911 [0.709, 1.117] | 20% |
| 256 | 1.1965 | 1.0404 | 1.150 [0.893, 1.421] | 87% |
| 368 | 1.3157 | 1.0817 | 1.223 [**0.914, 1.552**] | 91% |

**The defensible statement:** the released checkpoint beats the hold-last floor **decisively out
to ~64 steps (1.3 s)** — ratio 0.24–0.50 with zero bootstrap mass above 1 — is **indistinguishable
from it at ~128 steps**, and **trends worse but is not statistically distinguishable from it** at
256–368 steps, where the confidence interval includes 1.0.

It does **not** support "worse than a constant predictor at long horizon": at 91% the h=368
result falls short of significance. It equally does not support the earlier "beats the floor by
36% at h=368", which was measured on the two easiest episodes.

**The per-trajectory distribution at h=368 is cleanly bimodal** — ten trajectories at ratios
0.29–0.92 and ten at 1.68–2.66, with nothing between. Exactly 10 of 20 lose. The rollout either
tracks or diverges; there is no middle regime.

Aggregation, same 20 trajectories at h=368: relative-L1 1.3157 vs 1.0817; pooled nRMSE (form 1)
3.9642 vs 1.4969; form 1 excluding gravity **1.3132 vs 1.4613 (model beats)**; form 2 5.7973 vs
1.4394. The gravity dimensions continue to dominate any aggregate that includes them (R-29).
**Evidence** `RUN` `results/batch1_post_retraction.json` and the bootstrap.
**Status** CONFIRMED · **Relevance** CONTRIB


### R-35 — M-16 re-evaluated in both arenas: CANNOT BE SETTLED, in all eight combinations · **NEW**
The pre-registered rule, applied to independent trajectories with pooled aggregation, reverses
its own earlier verdict. Reported first because it outranks everything else in this batch.

| arena | steps | metric | leader @500 | @2500 | \|A−B\| | max seed sd | verdict | n_indep |
|---|---|---|---|---|---|---|---|---|
| out-of-sample | 400 | relative-L1 | A | A | 0.0103 | 0.0308 | **cannot be settled** | 4 |
| out-of-sample | 400 | nRMSE | A | A | 0.0035 | 0.0288 | **cannot be settled** | 4 |
| out-of-sample | 200 | relative-L1 | A | A | 0.0205 | 0.0229 | **cannot be settled** | 10 |
| out-of-sample | 200 | nRMSE | A | A | 0.0140 | 0.0231 | **cannot be settled** | 10 |
| in-sample | 400 | relative-L1 | **B** | **A** | 0.0272 | 0.0040 | **cannot be settled** | 16 |
| in-sample | 400 | nRMSE | **B** | **A** | 0.0485 | 0.0199 | **cannot be settled** | 16 |
| in-sample | 200 | relative-L1 | **B** | **A** | 0.0121 | 0.0049 | **cannot be settled** | 39 |
| in-sample | 200 | nRMSE | **B** | **A** | 0.0200 | 0.0145 | **cannot be settled** | 39 |

**All eight agree**, but they fail different conditions, and the distinction matters:

- **Out-of-sample fails condition 2.** The ordering is stable (A leads at both checkpoints) but
  the arm difference at h=8 is 0.0035–0.0205 against a seed spread of 0.0229–0.0308. The arms
  are not separated at h=8 on independent trajectories.
- **In-sample fails condition 1.** The ordering **flips**: Arm B leads at 500, Arm A leads at
  2500, on both lengths and both metrics, with `n_independent` up to 39.

**Why this differs from R-22's SETTLED verdict.** R-22 and R-28 used 10 and 100 *overlapping*
trajectories from the held-out pair with form-2 aggregation. The h=8 arm difference there was
0.0479 against a spread of 0.0172. On independent trajectories the difference falls to
0.0103–0.0205 and the spread rises. The earlier verdict was not wrong arithmetic; it was
computed on a trajectory set whose effective sample size was 4 (M-20).

**What is NOT in doubt.** At h=368 the separation is enormous in every arena — out-of-sample
Arm A 0.5856 vs Arm B 4.5684, in-sample 0.2503 vs 1.5791 — a factor of 6–8×, far outside any
spread. The ambiguity is confined to h=8, which is where M-16 was pre-registered.

**The honest statement is therefore horizon-dependent:** the autoregressive objective beats
teacher forcing decisively at long horizon, and the two are not distinguishable at the
8-step training horizon at this budget.
**Evidence** `RUN` `results/task4_arenas.json`.
**Status** CONFIRMED · **Relevance** CONTRIB
**Supersedes as the governing verdict** R-22's and R-28's SETTLED. Those remain valid for the
reference's own protocol and are retained.

### R-36 — The pre-registered teacher-forcing flip pattern FIRES, in the in-sample arena · **NEW**
Commit `0fe2bca`, entered before any Arm B result existed, recorded that a flip with **B
leading at 500 and A at 2500** would be the textbook teacher-forcing signature — faster early
fit on an easier objective, worse rollout later — and was to be reported as a distinct
observation rather than folded into a null result.

R-22 found no flip on the held-out pair and the annotation went unused. **On the in-sample
arena it fires exactly as written**, on both trajectory lengths and both metrics, with
`n_independent` of 16 and 39:

| | Arm A @500 | Arm B @500 | Arm A @2500 | Arm B @2500 |
|---|---|---|---|---|
| in-sample 400-step, h=8 | 0.3142 | **0.2873** | **0.1768** | 0.2040 |
| in-sample 200-step, h=8 | 0.2686 | **0.2405** | **0.1334** | 0.1454 |

Teacher forcing is genuinely ahead early and behind later, on the episodes both arms trained
on, where the power to see it is four to ten times higher than on the held-out pair. The
annotation's reasoning was right and the earlier report that "teacher forcing never led at any
measured point" (R-22) was an artifact of measuring only on two easy held-out episodes with
`n_independent = 4`.
**Evidence** `RUN` `results/task4_arenas.json`; pre-registration `0fe2bca`.
**Status** CONFIRMED · **Relevance** CONTRIB

### R-37 — Per-episode A/B gap: sign-consistent at h=368, reverses at h=8 · **NEW**
Gap = Arm B − Arm A, so positive means Arm A is better. Two independent 400-step trajectories
per episode, three seeds per arm, 2500 checkpoint.

| ep | difficulty (D-12) | gap h=8 (L1) | gap h=368 (L1) | arena |
|---|---|---|---|---|
| 0 | 1.5084 | **−0.0036** | +1.0005 | in |
| 1 | 0.7285 | **−0.0043** | +6.9746 | **out** |
| 2 | 0.5898 | +0.0407 | +1.1876 | in |
| 3 | 1.5853 | **−0.0105** | +0.9581 | in |
| 4 | 1.4227 | +0.0447 | +1.4242 | in |
| 5 | 0.7682 | +0.0169 | +0.9076 | in |
| 6 | 1.5389 | +0.0100 | +0.7270 | in |
| 7 | 0.6889 | +0.0802 | +2.8376 | in |
| 8 | 0.5225 | +0.0250 | +0.9907 | **out** |
| 9 | 0.8190 | +0.0394 | +1.5881 | in |

**At h=368 the gap is positive on all ten episodes, on both metrics** — Arm A wins everywhere,
without exception. **At h=8 it reverses sign on episodes 0, 1 and 3** on both metrics. M-22
requires this to be reported regardless of any correlation, and it is the sharper statement:
the long-horizon effect is universal across episodes; the short-horizon effect is not even
consistent in direction.

Correlation of gap against D-12 difficulty, with bootstrap CI over episodes:

| metric | r | 95% CI | spans zero |
|---|---|---|---|
| relative-L1 h=8 | −0.464 | [−0.851, +0.141] | yes |
| relative-L1 h=368 | −0.334 | [−0.735, +0.029] | yes |
| nRMSE h=8 | −0.474 | [−0.851, +0.108] | yes |
| nRMSE h=368 | −0.425 | [−0.834, +0.027] | yes |

Held-out pair versus the other eight: at h=8 the held-out pair **understates** the gap
(+0.0103 vs +0.0272); at h=368 it **overstates** it (+3.98 vs +1.33). The bias runs in opposite
directions at the two horizons, which is itself why no single correction would fix it.
**Evidence** `RUN` `results/task4_arenas.json`.
**Status** CONFIRMED · **Relevance** CONTRIB


### R-38 — Long-horizon A/B figures from the existing six runs · **NOT PRE-REGISTERED** · **NEW**
These are the numbers M-16 could not reach because it was anchored at h=8 (M-24). They are
recorded with the label in the entry title, not in a footnote, because no rule governed them
before they were computed.

| **NOT PRE-REGISTERED** — h=368, 2500 checkpoint, form 1 pooled, independent trajectories | Arm A | Arm B | ratio | floor | n_indep |
|---|---|---|---|---|---|
| out-of-sample (episodes 1, 8) | **0.5856** | 4.5684 | **7.8×** | 0.9930 | 4 |
| in-sample (the other eight) | **0.2503** | 1.5791 | **6.3×** | 1.1039 | 16 |

Arm A also beats the hold-last floor in both arenas at h=368, which neither arm does at
h=8 out-of-sample.

Their standing: suggestive, consistent across arenas and with R-37's ten-of-ten sign
consistency, and **not** a pre-registered result. M-23 pre-registers the same measurement on
new data so that a governed verdict exists.
**Evidence** `RUN` `results/task4_arenas.json`.
**Status** CONFIRMED as measurements, NOT PRE-REGISTERED as a verdict · **Relevance** CONTRIB

### R-39 — The h=368 magnitude rests on an episode-1 outlier; the direction does not · **NEW**
At h=368 the held-out pair overstates the A/B gap roughly threefold: **+3.98 against +1.33** on
the other eight episodes. The cause is a single episode.

| ep | difficulty | gap h=368 | |
|---|---|---|---|
| **1** | **0.7285** | **+6.9746** | held out — 2.5× the next largest |
| 7 | 0.6889 | +2.8376 | |
| 9 | 0.8190 | +1.5881 | |
| 8 | 0.5225 | +0.9907 | held out |
| 6 | 1.5389 | +0.7270 | smallest |

**This is not a difficulty effect.** Episode 1's difficulty is a middling 0.7285 — fifth of ten
— against a gap of +6.97, the largest by a factor of 2.5. Task 4b's rule tested the correlation
between gap and difficulty and would not have detected this; **its Branch 1 verdict therefore
stands and is not overridden** (M-22).

**Consequence, precisely scoped:** the *direction* of the A/B effect is robust — positive on ten
of ten episodes, both metrics (R-37). The *magnitude* estimated from the two held-out episodes
is not: it rests on one episode that is anomalous for reasons difficulty does not explain. Any
long-horizon magnitude should be reported as a range across episodes (+0.73 to +6.97) with
episode 1 named, not as a single figure from the held-out pair.
**Evidence** `RUN` `results/task4_arenas.json`.
**Status** CONFIRMED · **Relevance** CONTRIB


### R-40 — M-23: the claim REPRODUCES AT LONG HORIZON · **NEW**
The pre-registered rule (`efc35b8`, committed before either 10,000-iteration run was launched)
evaluated on Arm A seed 1 and Arm B seed 1, from scratch to 10,000 iterations, 7.5 h total,
zero gradient spikes in either.

**Governing measurement** — relative-L1, h=368, out-of-sample, 400-step, form 1 pooled,
95% bootstrap CI over independent trajectories:

| condition | result | |
|---|---|---|
| 1. Arm A leads at 2500 **and** 10,000 | **True** | gaps +6.7455 and +1.2033 |
| 2. 95% bootstrap CI excludes zero at 10,000 | **True** | CI [+0.5606, +2.0467], n_indep = 4 |
| 3. per-episode sign consistent across all ten | **True** | all positive, +0.418 to +1.826 |

**VERDICT: REPRODUCES AT LONG HORIZON.** At 10,000 iterations Arm A scores 0.3509 against Arm
B's 1.5540 out-of-sample — a factor of **4.4×** — and 0.1002 against 0.9723 in-sample, a factor
of **9.7×**.

**Secondaries, reported and not governing:**

| | gap | 95% CI | |
|---|---|---|---|
| h=368 in-sample | +0.8719 | [+0.6711, +1.0920] | A leads, excludes zero |
| h=8 in-sample | +0.0486 | [+0.0284, +0.0705] | A leads, excludes zero |
| **h=8 out-of-sample** | **+0.0080** | **[−0.1316, +0.1243]** | **spans zero** |

The governing verdict and the secondaries **agree in direction everywhere**; the one that spans
zero is h=8 out-of-sample at `n_independent = 4`, which is the measurement M-24 already
identified as anchored to the wrong horizon and the weakest sample in the project.
**Evidence** `RUN` `results/task5_analysis.json`, `results/step5_arm{A,B}_seed1_10k.json`;
pre-registration `efc35b8`.
**Status** CONFIRMED · **Relevance** CONTRIB

### R-41 — A from-scratch model does NOT develop the released checkpoint's failure pattern · **NEW**
The largest result available from these runs, and it answers the question in the **negative**,
which is the opposite of the hypothesis that motivated it.

Per-dimension losses to the hold-last floor, evaluated on 20 independent trajectories across
all ten episodes:

| model | dimensions lost of 45 | overlap with the released 7 |
|---|---|---|
| released checkpoint | **7** | — |
| Arm A @500 | 24 | 3/7 |
| Arm A @2500 | **1** | 1/7 |
| Arm A @5000 | **1** | 1/7 |
| Arm A @7500 | **1** | 1/7 |
| **Arm A @10000** | **1** | **1/7 — Jaccard 0.14** |
| Arm B @10000 | 18 | 4/7 |

**Arm A at 10,000 loses on exactly one dimension: `g_z`** — and `g_z` is the dimension R-32
showed is weighted 1/1174 in the loss by a mis-specified normalisation constant, so no model
trained on this objective has an incentive to fit it. Every other dimension in the released
checkpoint's failure set — `g_x`, `g_y`, `v_z`, `w_x`, `w_y`, `tau_RF_HAA` — is handled fine by
a from-scratch model with **less** training data.

**The inference runs the other way from the hypothesis.** Had the pattern converged, the
weakness would belong to the objective and architecture. It does not converge: the released
checkpoint's six extra failing dimensions are **specific to that checkpoint**, not implied by
the released objective. Taken with C-12, C-13, R-24 and R-25 — which independently place the
released checkpoint at order 1e5 optimisation steps rather than its tagged 5,000 — this is a
third, independent line of evidence that the released weights are not what the released recipe
produces.

**Caveat, stated because it cuts against the finding's convenience:** Arm A trained on 8 of the
10 episodes it is evaluated on, so its evaluation is 80% in-sample. The released checkpoint
trained on **all ten**, so it is 100% in-sample and if anything holds the advantage. The
comparison is conservative in the direction of the conclusion.
**Evidence** `RUN` `results/task5_analysis.json`.
**Status** SUPERSEDED IN PART by S-11 and R-45 — the comparison was against a seven-dimension
set derived from a different evaluation. Matched, the released checkpoint loses on 18 of 45 on
all ten episodes and 8 of 45 on the held-out pair, against Arm A's 1 in both. The directional
conclusion survives and strengthens per-dimension; the aggregate reading does not (R-45).
· **Relevance** CONTRIB

### R-42 — The A/B gap across five checkpoints: persists everywhere, resolves in-sample at h=8 · **NEW**
Bootstrap CIs over independent trajectories, gap = Arm B − Arm A so positive favours Arm A.

**h=368, out-of-sample** (n_indep 4): +3.334, +6.746, +1.459, +1.280, +1.203 at 500 / 2500 /
5000 / 7500 / 10000 — **CI excludes zero at every checkpoint**.
**h=368, in-sample** (n_indep 16): +1.724, +1.699, +0.924, +0.834, +0.872 — excludes zero at
every checkpoint.

The absolute gap **narrows** after 2500 because both arms improve (Arm A 1.4265 → 0.3509, Arm B
4.7589 → 1.5540), but the ratio remains 4.4× out-of-sample and 9.7× in-sample at 10,000, and no
checkpoint is ambiguous.

**h=8 answers Q2 in two different ways depending on arena.** In-sample the gap grows
monotonically and every checkpoint after 500 excludes zero: −0.0255, +0.0291, +0.0393, +0.0442,
**+0.0486**. The negative value at 500 is the R-36 teacher-forcing flip, now confirmed a third
time with a CI that excludes zero. Out-of-sample the gap never separates: +0.0594, +0.0386,
+0.0070, −0.0127, +0.0080, with the CI spanning zero at four of five checkpoints.

So the h=8 ambiguity **does not resolve with more training out-of-sample** — it is a
sample-size limit at `n_independent = 4`, not a convergence limit. In-sample, at four times the
independent samples, it resolves cleanly and widens.
**Evidence** `RUN` `results/task5_analysis.json`.
**Status** CONFIRMED · **Relevance** CONTRIB

### R-43 — The collapse rate stays linear to 10,000; the pre-registered prediction lands · **NEW**
M-23 recorded the expectation that `exp(log_delta_logstd)` should reach ≈0.39 at 10,000 if the
pooled 2,500-iteration rate of −9.4362e-05 held.

| | rate over 10,000 | rate/lr | exp(log_delta) @10,000 | predicted | error |
|---|---|---|---|---|---|
| Arm A | −9.1353e-05 ± 2.63e-08 | 0.91 | **0.400198** | 0.3892 | **+2.8%** |
| Arm B | −9.1536e-05 ± 3.65e-08 | 0.92 | **0.398468** | 0.3892 | **+2.4%** |

The rate slows by ~3% over the 4× longer window (−9.44e-05 → −9.14e-05), and the two arms agree
with each other to 0.2%. **The linearity underpinning O-12 survives a fourfold extrapolation to
within 3%.** Implied iterations to the released checkpoint's −14.4629 move from 153,270 to
**158,319** (Arm A) and **158,003** (Arm B) — the conclusion is unchanged and its uncertainty is
now bounded by measurement rather than by extrapolation.
**Evidence** `RUN` `results/task5_analysis.json`.
**Status** CONFIRMED · **Relevance** CONTRIB


### R-44 — The central claim's full history, with commit timestamps · **NEW**
The methodological spine of the project. This timeline is not reconstructable from any other
repository, and it is the evidence that the surviving claims went through the same filter as the
withdrawn ones.

| when | commit | event |
|---|---|---|
| 17 Aug 18:52 | `84ff01b` | **M-16 pre-registered** at h=8, before any main run |
| 17 Aug 22:42 | `0fe2bca` | **§6.1 flip annotation** pre-registered, before any Arm B result |
| 18 Aug 13:29 | `8385ba1` | **R-27 retracted** by its own gating checks (S-10) |
| 18 Aug 14:08 | `d88e9ff` | **M-16 returns CANNOT BE SETTLED** in all eight combinations |
| 18 Aug 17:59 | `efc35b8` | **M-23 pre-registered** at h=368, before either 10,000-iteration run |
| 19 Aug 01:35 | `8625d32` | **M-23 returns REPRODUCES AT LONG HORIZON** |

The sequence: asserted at h=8 in Step 5 under seed-spread statistics and overlapping
trajectories → withdrawn in Task 4 when corrected measurement returned CANNOT BE SETTLED in all
eight arena/length/metric combinations → re-tested at h=368 under a rule committed before the
data existed → **reproduces at long horizon**. The §6.1 annotation, unused when written, fired
later in the in-sample arena (R-36).

**POWER CAVEAT, stated here and not in a footnote.** M-23's governing verdict rests on
`n_independent = 4`. A bootstrap CI resampling four points cannot characterise a distribution;
it can only say that all four points lie on one side by a margin. The verdict's credibility
comes from three places, not from that interval alone: the **in-sample arena at n_indep = 16
returns the same answer with a tighter interval** ([+0.671, +1.092]); the **per-episode sign is
positive on all ten episodes** independently; and the effect size is 4.4–9.7×, far larger than
any plausible sampling artefact at this n. Quoted without those three supports, the governing
CI would be overstated.
**Evidence** git history; `RUN` `results/task5_analysis.json`.
**Status** CONFIRMED · **Relevance** CONTRIB

### R-45 — Matched per-dimension comparison: released checkpoint vs Arm A · **NEW**
Correcting S-11. Both models scored identically — 400-step, independent trajectories only,
form 1 pooled, `action_offset=1`, same floor.

| evaluation | n_indep | released loses | Arm A @10k loses | shared | Jaccard |
|---|---|---|---|---|---|
| all ten episodes | 20 | **18 / 45** | **1 / 45** | `g_z` | 0.06 |
| episodes 1 and 8 only | 4 | **8 / 45** | **1 / 45** | `g_z` | 0.12 |

**`g_z` is the only shared failure under both matchings** — the dimension R-32 showed is
weighted 1/1174 by a mis-specified normalisation constant.

Aggregate error with bootstrap CIs:

| evaluation | h | released | Arm A | difference | |
|---|---|---|---|---|---|
| all ten | 8 | 0.1584 | 0.1372 | +0.0212 [−0.0720, +0.1016] | spans zero |
| all ten | 368 | 1.3166 | **0.1505** | **+1.1661 [+0.8463, +1.4794]** | **Arm A better** |
| eps 1,8 | 8 | **0.0809** | 0.3418 | **−0.2610 [−0.5006, −0.0205]** | **released better** |
| eps 1,8 | 368 | 0.6044 | 0.3510 | +0.2533 [−0.0267, +0.4395] | spans zero |

**The conclusion is split, and both halves must be stated.**

*Per-dimension*, the result is robust across both matchings: Arm A loses on 1 of 45 in each,
against 18 and 8. That holds even on episodes 1 and 8, which the released checkpoint **trained
on** and Arm A never saw — the handicap runs against Arm A and it wins anyway.

*In aggregate*, it does not. On the strictly out-of-sample pair the released checkpoint is
**significantly better at h=8** and the two are **statistically tied at h=368**. Arm A's large
aggregate advantage appears only on the all-ten arena, where Arm A trained on 8 of the 10
episodes.

So the brief's first outcome — "a from-scratch model outperforms the released weights on
held-out data" — is supported **per-dimension** and **not** in aggregate. The defensible claim is
narrower than R-41 implied: a from-scratch model at 10,000 iterations fails on far fewer state
dimensions than the released checkpoint, on matched data, under a handicap; it does not achieve
lower aggregate error on data it has not seen.
**Evidence** `RUN` `results/task2_3_matched_trend.json`.
**Status** CONFIRMED · **Relevance** CONTRIB

### R-46 — The gap-narrowing trend: absolute gap closes, relative advantage does not · **NEW**
Fitted against iteration count over 500–10,000, both arenas, h=8 and h=368. **Everything past
10,000 below is extrapolation and is labelled as such.**

| arena, h | gap at 500 → 10,000 | gap slope /iter | R² | gap zero at | ratio 500 → 10,000 | ratio trend |
|---|---|---|---|---|---|---|
| out-of-sample, 368 | +3.33 → +1.20 | −4.17e-04 | 0.45 | ~11,800 *(extrap.)* | 3.34× → 4.43× | −2.7e-04, R² **0.07** |
| in-sample, 368 | +1.72 → +0.87 | −1.07e-04 | 0.78 | ~16,500 *(extrap.)* | 2.33× → **9.70×** | **+6.5e-04, R² 0.76** |
| out-of-sample, 8 | +0.059 → +0.008 | −6.31e-06 | 0.71 | ~8,300 *(extrap.)* | 1.18× → 1.02× | declining |
| in-sample, 8 | −0.026 → +0.049 | +6.65e-06 | 0.69 | never | 0.92× → **1.57×** | **growing** |

**The absolute gap narrows in both arenas — but that is both arms improving toward the same
floor, not the advantage disappearing.** The ratio tells the opposite story in-sample, growing
monotonically from 2.33× to 9.70× with R² 0.76.

**Correction to the premise this task was set on.** The out-of-sample ratio does not decline
monotonically from 2500: it runs 3.34, **12.38**, 3.66, 4.43, 4.43. The 12.38 at 2500 is a single
anomalous Arm B value; with it removed the sequence is 3.34, 3.66, 4.43, 4.43 — flat to slightly
**rising**, and the ratio fit has R² 0.07, i.e. no trend at all.

**The honest qualification for a reader:** the autoregressive advantage measured as an absolute
error difference is largest early and shrinks as both arms train, so an effect size quoted at
2,500 iterations overstates what remains at 10,000. Measured as a ratio it does not shrink, and
in-sample it grows. Direction holds at every checkpoint, in both arenas, on all ten episodes.
**Evidence** `RUN` `results/task2_3_matched_trend.json`.
**Status** CONFIRMED · **Relevance** CONTRIB


### R-47 — The spliced windows cost nothing measurable, and if anything help · **NEW**
Closes O-06, open since Step 3.5. B-01 is a confirmed defect whose cost had never been measured.

**Design.** Clean Arm A (7,687 windows) against contaminated Arm A (7,882 = 7,687 + **195**
splices), 3 seeds each, 2500 iterations, identical in every other respect. Only boundaries whose
**both** sides are training episodes are spliced — 2→3, 3→4, 4→5, 5→6, 6→7 — because the other
four touch a held-out episode and would leak. The held-out-row assertion passes. Contamination
rate **2.47%** against the reference pipeline's 3.53%.

**Result over 32 comparisons** (2 arenas × 2 trajectory lengths × 2 checkpoints × 2 horizons ×
2 metrics), diff = contaminated − clean, bootstrap CIs over independent trajectories:

| | count |
|---|---|
| comparisons where contamination **hurt** (CI excludes zero, positive) | **0** |
| comparisons where contamination **helped** (CI excludes zero, negative) | **10** |
| no measurable effect | 22 |

**Not one comparison shows contamination hurting.** The ten significant ones are all negative and
are concentrated where statistical power is highest — in-sample (`n_ind` 16 and 39) and
out-of-sample 200-step (`n_ind` 10). The primary out-of-sample 400-step arena (`n_ind` = 4) shows
no significant effect either way. Effect sizes are small: −0.7% to −6% relative.

**Training loss goes the other way, as it must:** 1.8301 ± 0.0732 contaminated against
1.5364 ± 0.0353 clean. The spliced windows contain physically impossible transitions that cannot
be fit, so they raise the training loss — and rollout error is unchanged or slightly better. The
195 unfittable windows appear to act as a mild regulariser.

**Scope, stated carefully.** This measures the *physics* cost of training on spliced
transitions. It does **not** measure the reference's full exposure, which differs in two ways:
its rate is 3.53% rather than 2.47%, and 4 of its 9 spliced boundaries put **held-out rows into
training** — a leakage problem rather than a physics problem, and one this experiment
deliberately excludes in order to keep its own comparison valid. So B-01 remains a real defect
on leakage grounds; what is now measured is that its *physically-impossible-transition* component
costs nothing detectable at this rate.

**Caveat on multiplicity:** 32 comparisons at 95% would yield ~1.6 false positives by chance, and
these comparisons are not independent — they share runs and nest horizons within trajectories.
Ten significant results all in the same direction is well beyond chance, but the individual
effect sizes should not be quoted as precise.
**Control** The mechanism asserted here — that the rise is caused by unfittable splice
content rather than by the extra window count — was not controlled when this entry was
written. It has since been tested against a duplication arm and **confirmed** (R-55).
The training-loss figures quoted above are single-minibatch draws; see M-26.
**Evidence** `RUN` `results/task4_contamination.json`, `results/step5_armA_seed{0,1,2}_contam.json`.
**Status** CONFIRMED · **Relevance** CONTRIB


### R-48 — The corrected objective reverses the collapse mechanism but produces no usable uncertainty · **NEW**
The measurement the corrected-objective arm was run for, and it returns a **negative** result on
the part that matters. Three seeds at 2500 iterations under the authors' unused `gaussian_nll`
branch, evaluated on the 4 independent held-out 400-step trajectories.

**What reverses.** `log_delta_logstd` moves in the opposite direction: rate **+3.26e-05** per
iteration against the faithful arm's −9.14e-05, and `exp(log_delta)` grows 1.0001 → **1.092**
instead of shrinking to 0.79. Gradient norms are **16× larger** (mean 180 against 11) with
**zero spikes** in any seed. The bound-loss ratchet of C-11 is genuinely broken.

**What does not.** σ remains, in effect, a constant — a larger one.

| | faithful (mse) | corrected (nll) | released ckpt | calibrated |
|---|---|---|---|---|
| mean σ | 6.41e-03 | **2.92e-02** | 5.79e-05 | — |
| mean \|error\| / σ | 52× | **11×** | **7,878×** | 1 |
| ±1σ coverage @h=8 | 4.61% | **19.95%** | 0.14% | **68.3%** |
| ±2σ coverage @h=8 | 9.03% | 34.61% | 0.35% | 95.4% |
| ±1σ coverage @h=368 | 1.75% | 8.57% | 0.04% | 68.3% |
| **CoV of σ across a batch** | 0.0076 | **0.0059** | 0.0177 | — |
| **σ vs \|error\| correlation** | +0.034 | **−0.004** | +0.001 | strongly positive |
| σ growth, late/early forecast step | 0.95× | **1.00×** | 1.01× | >1 |

**The flagged result: σ does not correlate with realised error.** Mean correlation **−0.004**,
median −0.009, positive on 21 of 45 dimensions where chance is ~22.5. The coefficient of
variation across a batch is 0.0059 — *lower* than the faithful arm's. And σ does not grow with
forecast step (1.00×) even though rollout error grows by an order of magnitude over the same
range. A σ that varies neither with input nor with horizon, and does not track error, is no more
useful than the constant it replaced.

**The prediction stated before running was half right.** The faithful arm behaved exactly as
predicted — coverage near zero (4.61% at h=8) and flat in horizon. The NLL arm did *not* land
near 68/95 at short horizon: 42.8% at h=1 and 19.95% at h=8. So by the brief's own third branch,
**the collapse reversed without producing calibration**.

**Mechanism, and it is not the clamp.** At 2500 iterations the NLL arm's bound interval is
`[−4.92, −3.82]`, a width of 1.09 in log space — σ is free to span a factor of e^1.09 ≈ 3.0×.
It uses 0.6% of that freedom. The clamp is not the binding constraint; the `state_logstd_layers`
tower is itself emitting a near-constant output. **Removing the pressure that forces σ to a
constant did not cause the network to learn a varying one.**

**Consequence for the release.** The planned amendment to publish `armA_2500_nll` as "the only
model whose uncertainty output is usable" is **withdrawn** — its condition was calibration and
that condition fails. It may still be published as the corrected-objective artifact, but its
per-checkpoint limitation must say the same thing as the others: do not use the uncertainty.
**Evidence** `RUN` `results/task1_calibration.json`, `results/step5_armA_seed{0,1,2}_nll.json`.
**Status** CONFIRMED · **Relevance** CONTRIB
**Opens O-13.**

### R-49 — The released checkpoint's uncertainty output is worthless, quantified · **NEW**
Not previously measured by anyone, including this project. On held-out data the released
checkpoint's predicted σ is **5.79e-05** against a mean absolute error of **4.56e-01** — the
error is **7,878×** the claimed standard deviation.

±1σ coverage is **0.14%** at h=8 and **0.04%** at h=368, against 68.3% for a calibrated
Gaussian. The reliability curve is flat at the floor: at a predicted coverage of 99.7% (±3σ) the
observed frequency is **0.1%**.

This is the direct empirical consequence of C-10 and it is the number that makes
"uncertainty-aware" checkable. RWM-U's epistemic term is a separate quantity and is not measured
here; this concerns the aleatoric σ the state head emits.
**Evidence** `RUN` `results/task1_calibration.json`.
**Status** CONFIRMED · **Relevance** CONTRIB

### R-50 — Under `gaussian_nll` the released checkpoint's variance state is unreachable at any iteration count · **NEW**
1c. Fitted rate of `log_delta_logstd` under the corrected objective, three seeds:

| seed | rate/iter | implied iterations to −14.4629 |
|---|---|---|
| 0 | **+3.2571e-05** | **−444,049** |
| 1 | +3.1785e-05 | −455,028 |
| 2 | +3.2640e-05 | −443,110 |

The rate is **positive** — the parameter moves *away* from the released checkpoint's value — so
the implied count is negative, mean **−447,396**. No iteration count under this branch reaches
−14.4629, in either direction of training time.

Under sampled MSE the same extrapolation gives **+158,000** and was validated to 3% over a
fourfold extension (R-43). Together these establish something neither shows alone: **the
released checkpoint was trained with the MSE branch**, and its variance state is not merely
far from what the released recipe produces but unreachable under the alternative the authors
also shipped.
**Evidence** `RUN` `results/task1_calibration.json`, `results/step5_armA_seed{0,1,2}_nll.json`.
**Status** CONFIRMED · **Relevance** CONTRIB · **Strengthens O-12.**


### R-51 — All four models are catastrophically overconfident · `[RWM-U]` · **NEW**
Coverage measured on the 4 independent held-out 400-step trajectories, against a calibrated
Gaussian's 68.3% at ±1σ and 95.4% at ±2σ.

| model | mean \|error\| / σ | ±1σ @h=8 | ±2σ @h=8 | ±1σ @h=368 |
|---|---|---|---|---|
| released checkpoint | **7,878×** | **0.14%** | 0.35% | 0.04% |
| faithful Arm A (mse) | 52.2× | 4.61% | 9.03% | 1.75% |
| teacher-forced Arm B | 61.0× | 2.04% | 3.15% | — |
| corrected Arm A (nll) | **10.9×** | **19.95%** | 34.61% | 8.57% |
| *calibrated reference* | *1×* | *68.3%* | *95.4%* | *68.3%* |

The released checkpoint's reliability curve is flat at the floor: at a predicted 99.7% (±3σ) the
observed frequency is **0.1%**. The corrected arm is the least bad by a factor of ~700 and is
still wrong by an order of magnitude.
**Evidence** `RUN` `results/task1_calibration.json`, `results/task2_sigma_profile.json`.
**Status** CONFIRMED · **Relevance** CONTRIB

### R-52 — σ is input-independent in all four models · `[RWM-U]` · **NEW**
Coefficient of variation of the predicted σ across a batch:

| model | CoV of σ | permitted interval width (log space) | fraction of the freedom used |
|---|---|---|---|
| released checkpoint | 0.0177 | 5.2e-07 — closed | n/a, the clamp binds |
| faithful Arm A | 0.0076 | 0.79 | ~1% |
| corrected Arm A (nll) | **0.0059** | **1.09** | **0.6%** |

The corrected arm is the decisive case. Raising `log_delta` to 1.09 widened the permitted
interval so σ could span a factor of e^1.09 ≈ 3.0×, and the head used **0.6%** of it — varying
*less* across a batch than the faithful arm, whose interval is narrower. **The clamp is not what
makes σ constant.** Removing the pressure that forces σ to a constant did not cause the network
to learn a varying one.
**Evidence** `RUN` `results/task1_calibration.json`.
**Status** CONFIRMED · **Relevance** CONTRIB

### R-53 — The correction improved magnitude and destroyed what ordering signal existed · `[RWM-U]` · **NEW**
σ-versus-realised-error correlation, per dimension, pooled across seeds:

| model | mean r | median r | dims with r > 0 | under a coin-flip null |
|---|---|---|---|---|
| faithful Arm A (mse) | **+0.034** | +0.029 | **39 / 45** | P ≈ **1.4e-06** — real |
| corrected Arm A (nll) | **−0.004** | −0.009 | **21 / 45** | P ≈ 0.66 — chance |
| released checkpoint | +0.001 | −0.010 | 20 / 45 | chance |

The faithful arm's correlation is *small but genuine*: 39 of 45 dimensions positive has
probability 1.4e-06 under a fair-coin null, so the constant-σ head nonetheless carried a faint
ordering signal. The corrected arm scores 21 of 45 — indistinguishable from chance.

So the correction **improved the magnitude** (10.9× overconfident against 52.2×) and
**removed the ordering**. An uncertainty estimate that is better scaled but no longer ranks
which predictions are worse is not obviously an improvement for any downstream use.
**Evidence** `RUN` `results/task1_calibration.json`.
**Status** CONFIRMED · **Relevance** CONTRIB

### R-54 — σ is flat *inside* the trained horizon, which removes the structural excuse · `[RWM-U]` · **NEW**
Task 2. The loss trains on exactly 8 forecast steps, so if a model were going to learn
horizon-dependent uncertainty anywhere it would be here. σ across steps 1 → 8, against the
realised error over the same range:

| model | σ growth 1→8 | \|error\| growth 1→8 | ±1σ coverage 1 → 8 |
|---|---|---|---|
| faithful Arm A | **0.924×** (declines) | 3.49× | 11.67% → 1.48% |
| corrected Arm A (nll) | **1.0003×** | 3.41× | 42.78% → 11.48% |
| teacher-forced Arm B | 1.0096× | 6.11× | 12.96% → 2.04% |
| released checkpoint | 1.0007× | 1.79× | 0.56% → 0.00% |

**Reading 2, the stronger negative result.** σ is flat across steps 1–8 in every model — the
faithful arm's actually *declines* — while realised error grows 1.8× to 6.1× over the same
range. The models fail to learn horizon-dependence **even inside the window the loss actually
optimises**.

This removes the structural excuse. One could have argued that an 8-step forecast objective
cannot teach uncertainty about step 368; that argument does not survive, because these models do
not learn it about step 8 either. The coverage decline from step 1 to step 8 is therefore driven
**entirely** by growing error against a fixed σ, not by σ failing to keep pace.

It also narrows O-13: "2500 iterations is too few" and "the task has little heteroscedasticity
to learn" both become harder to sustain, since the error grows 3.4× within the trained window
and σ does not move.
**Evidence** `RUN` `results/task2_sigma_profile.json`.
**Status** CONFIRMED · **Relevance** CONTRIB


### R-55 — The duplication control: R-47's mechanism survives, its statistic does not · **NEW**
R-47 inferred a *mechanism* from a training-loss gap: spliced windows raise the loss **because
they contain physically impossible transitions that cannot be fit**. That inference had a
confound it did not control. The contaminated arm differs from clean in two ways at once — 195
extra windows, and those windows being spliced. Dataset size alone could have produced the rise.

**Design.** A third arm adding 195 windows that are exact duplicates of windows already in
the training set: 7687 → 7882, matching the contaminated arm's count exactly. Duplicated
windows are as fittable as ordinary data and carry zero new information, so they isolate size
from content. 3 seeds, duplication seeds 10000/10001/10002, all windows within-episode, no
held-out rows. The analysis script asserts that **no hyperparameter differs between the three
arms outside the dataset itself**.

**On the pre-registered statistic, the rule fires.** `final_terms.state`, mean of 3 seeds:
clean 1.5364, duplicated 1.7338, contaminated
1.8301 — duplication apparently explaining
67.2% of the rise. Taken literally this retracts
R-47's mechanism.

**It does not, because that statistic is one minibatch.** Its sd is 0.1769
against an effect of 0.0143: 12.4× more noise
than signal (M-26).

**Mean over the final N iterations, for every N tried:**

| tail | clean | duplicated | contaminated | share explained by duplication |
|---|---|---|---|---|
| 50 | 1.5194 | 1.5407 | 1.8444 | +6.6% |
| 100 | 1.5425 | 1.5642 | 1.8709 | +6.6% |
| 150 | 1.5525 | 1.5735 | 1.8964 | +6.1% |
| 250 | 1.5843 | 1.5986 | 1.9261 | +4.2% |
| 400 | 1.6365 | 1.6488 | 1.9800 | +3.6% |
| 600 | 1.7177 | 1.7176 | 2.0579 | -0.0% |
| 1000 | 1.8948 | 1.8876 | 2.2527 | -2.0% |

Duplication never explains more than
6.6% of the rise, and at
longer tails explains none of it.

**Bootstrap over iterations 500 in
2000–2499, which makes no tail choice:**

| difference | value | 95% CI | |
|---|---|---|---|
| duplicated − clean | +0.0077 | [-0.0061, +0.0215] | **includes zero** |
| contaminated − clean | +0.3455 | [+0.3284, +0.3626] | excludes zero |
| contaminated − duplicated | +0.3378 | [+0.3274, +0.3483] | excludes zero |

Duplicated sits below contaminated at **500 of
500** iterations.

**Verdict.** 195 perfectly fittable duplicate windows cost 0.90% of training loss;
195 spliced windows cost 21.57%. The rise is
caused by splice content, not by dataset count. **R-47's mechanism is confirmed**, and its
rollout conclusion — 0 of 32 comparisons showing harm — was never in question here, since this
arm bears only on the training-loss inference.

**What R-47 got wrong.** Not the mechanism, but the evidence offered for it. R-47 quotes
"1.8301 ± 0.0732 contaminated against 1.5364 ± 0.0353 clean" as though the seed spread were the
relevant uncertainty. It is not: those are three single-minibatch draws per arm, and the spread
measures minibatch noise rather than run-to-run variation. The windowed figures are
1.5843 and 1.9261.
**Evidence** `RUN` `results/task3_control_arm.json`, `results/step5_armA_seed{0,1,2}_dup.json`.
**Status** CONFIRMED · **Relevance** CONTRIB


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
**Status** **CLOSED by R-47.** Measured: at 2.47% contamination, 3 seeds, 2500 iterations, the
spliced windows cost nothing detectable — 0 of 32 comparisons show harm and 10 show a small
benefit. The training loss rises as expected (1.83 vs 1.54) because the splices are unfittable;
rollout error does not. That the rise is caused by splice **content** and not by
the added window count is controlled and confirmed in R-55. The leakage component of B-01 is deliberately excluded from this
experiment and remains unmeasured.

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

### O-10 — Was the released checkpoint produced by the released config? · **NEW (Step 4)**
C-12 shows the checkpoint's `log_delta_logstd` of −14.463 implies ~155,000 iterations at the
configured learning rate, against a config that says 500 and a paper that says 2500. Either
the checkpoint was trained far longer than either figure, or with a different learning rate
or schedule, or the unpublished 6M-transition pretraining (X-04) accounts for the difference.
**Why it matters** If the released recipe cannot produce the released checkpoint, then
"reproducing RWM" and "reproducing `pretrain_rnn_ens.pt`" are different tasks, and every
comparison against that checkpoint needs the distinction stated.
**Test** Cheap: run the faithful arm to 2500 iterations and check whether
`exp(log_delta_logstd)` lands near the C-12 prediction of 0.79. If it does, the released
checkpoint did not come from the released recipe.

### O-11 — Does the batch-1024 superlinear penalty survive on other hardware? · **NEW (Step 4)**
R-16 measures 8.0× cost for 5× the heads at batch 1024, versus 3.6× at batch 256, with 4.8 GB
peak RSS. That reads as memory pressure on a 2-core machine rather than anything intrinsic.
**Why it matters** It decides the Step 6 configuration: if the penalty is local, batch 1024
is fine on rented hardware; if it is intrinsic to the per-member Python loop in
`compute_loss`, batch 256 is strictly better everywhere and the reference's own default is a
poor choice.
**Test** Re-time on any machine with more cores and RAM before committing to a Step 6 config.

### O-12 — The released checkpoint's variance collapse is inconsistent with the released configuration · **NEW (Step 5)**
The sharpest quantitative discrepancy found so far, and it now has two independent
measurements of the underlying rate rather than one.

`log_delta_logstd` decays at a rate set by the optimiser, not by the data: Adam's step in a
parameter whose gradient holds its sign is approximately the learning rate, and the bound
loss `mean(exp(log_delta_logstd))` is monotone in this parameter, so the sign never changes.
Measured on fresh models over two learning rates a decade apart:

| run | lr | fitted rate per iteration | rate / lr |
|---|---|---|---|
| R-17 | 1e-4 | −9.318e-05 | 0.93 |
| R-18 | 1e-3 | −7.025e-04 | 0.70 |

The released checkpoint sits at `log_delta_logstd` = **−14.4629** (C-10). Against its own
tagged iteration count of **5000** (C-13):

| | predicted `exp(log_delta_logstd)` |
|---|---|
| 500 iterations at lr 1e-4 (`base_cfg.py`) | 0.955 |
| 2500 iterations at lr 1e-4 (paper Table S7) | 0.792 |
| **5000 iterations at lr 1e-4 (the checkpoint's own tag)** | **≈ 0.63** |
| **observed in the released checkpoint** | **5.234e-07** |

That is a gap of roughly **six orders of magnitude** at the checkpoint's own stated iteration
count. Closing it requires either ≈155,000 iterations at the configured learning rate, or a
learning rate of **3.1e-3 to 4.1e-3** — 31 to 41× the configured 1e-4 — to arrive in 5000.

**Escape hatches, named honestly.** Any of these would explain it, and this entry does not
claim to distinguish them:
- a much larger learning rate during the unpublished 6M-transition pretraining (X-04);
- a different initialisation of `log_delta_logstd` (the released code initialises it to a
  constant 0.0 at `mlp.py:79`, but the pretraining code is not public);
- a different bound-loss weight than the configured 1.0;
- far more optimisation steps than the `iter` tag records — e.g. if the tag counts outer
  iterations and each contains many gradient steps.

**What does NOT explain it:** batch size and ensemble size. Adam's step in this parameter is
~lr regardless of gradient magnitude, and both measurements above confirm that scaling —
R-17 and R-18 differ 32× in batch size and land within 25% of the same rate/lr ratio.
**Evidence** `RUN` `results/step4_4_overfit_ens1.json`,
`results/step4_4_overfit_b32lr1e3.json`; `DATA` C-10; `SRC` `base_cfg.py`, `mlp.py:79`.
**Status** OPEN — the discrepancy is measured and confirmed; its *cause* is not.
**Relevance** CONTRIB
**Test** Cheap, and Step 5.3 supplies it free: the faithful arm runs to 2500 iterations at
lr 1e-4, so read `exp(log_delta_logstd)` at 500 and 2500 and compare against 0.955 and 0.792.
Agreement confirms the model of the mechanism and leaves the checkpoint unexplained.

**TEST PASSED (Step 5, R-19) — prediction confirmed to three decimal places.** Arm A seed 0
provides a third measurement, this time on real data over 2500 iterations rather than a
memorisation batch:

| measurement | lr | iterations | fitted rate/iter | rate ÷ lr |
|---|---|---|---|---|
| R-17 overfit | 1e-4 | 451 | −9.318e-05 | 0.93 |
| R-18 overfit | 1e-3 | 2000 | −7.025e-04 | 0.70 |
| **R-19 Arm A, real data** | **1e-4** | **2500** | **−9.3641e-05 ± 2.64e-08** | **0.936** |

**Predicted `exp(log_delta_logstd)` at 2500 iterations: 0.792. Observed: 0.791385.** The fit
has 101 points and a standard error of 2.64e-08 on the slope, so the rate is now pinned rather
than estimated. `rate ≈ lr` holds at lr 1e-4 in both a memorisation and a real-data setting
(0.93, 0.936); the 0.70 at lr 1e-3 is the outlier, so the proportionality is good near the
reference learning rate and degrades as lr grows.

From the fit rather than by extrapolation: reaching the checkpoint's −14.4629 requires
**154,451 iterations** at lr 1e-4, or **lr 3.09e-03** — 31× the configured value — to arrive
within the checkpoint's own tagged 5000. The mechanism reproduces exactly; the magnitude in
the released checkpoint is not reachable from the released configuration. That is the finding,
and it should be written that way rather than as a failure to reproduce.
**Status** the mechanism is now CONFIRMED and quantified; the checkpoint's provenance remains
OPEN.
**STRENGTHENED A THIRD TIME (R-43).** The linear extrapolation now survives a fourfold test:
both 10,000-iteration runs land at exp(log_delta) 0.3985–0.4002 against a prediction of 0.3892
made from the 2,500-iteration fit — within 3% — and imply 158,003–158,319 iterations rather than
153,270. R-41 adds an independent line: a from-scratch model at 10,000 iterations loses on 1 of
45 dimensions against the released checkpoint's 7, so the released weights are not what this
recipe produces on any of three separate measures.

**STRENGTHENED TWICE at Step 6.** (i) R-24 pools six independent trajectories: the rate is
−9.4362e-05 ± 3.33e-07 with a run-to-run sd of 0.87%, so it is a pinned constant rather than an
estimate, and it implies 153,270 iterations or lr 3.07e-03. (ii) R-25 adds `min_logstd` as a
second axis on a different gradient path and a 5× slower clock, independently implying order
2.7e5 iterations. Two parameters agreeing across a 5× rate difference is much harder to
attribute to any single escape hatch than one parameter was.
**Note on arithmetic** The Step 5 brief quotes −8.859e-05/iteration and ≈163,000 iterations.
That divides the observed log change by the run length (451) rather than by the iteration of
the last collapse sample (425); dividing by 425 gives −9.402e-05 two-point, −9.318e-05
fitted, and ≈155,000 iterations. The conclusion is unaffected.


### O-13 — Why does σ stay constant when the pressure forcing it to be constant is removed? · **NEW**
R-48 shows the `gaussian_nll` arm breaks the bound-loss ratchet — the interval widens to 1.09 in
log space, giving σ room to span ~3× — and the network uses 0.6% of that freedom, with a
σ-versus-error correlation of −0.004.

Candidate explanations, none tested:
- **2500 iterations is too few.** The mean path had 10,000 iterations available and still had not
  converged (R-26); the σ path may simply be slower. Cheap to test: extend one NLL seed to 10,000.
- **The σ gradient is weak relative to the mean gradient.** Under NLL the mean receives a
  1/σ² weighting while σ receives a term of order 1/σ − (err/σ)³; at σ ≈ 0.03 with errors ~0.3
  the mean term dominates by orders of magnitude.
- **The task has little heteroscedasticity to learn** at the 8-step training horizon, so a
  constant σ is close to optimal *for the objective as trained*, even though rollout error at
  h=368 varies enormously.

The third would be the most interesting: it would mean the training horizon, not the objective,
is what prevents a useful uncertainty estimate — which would connect this to M-24's finding that
h=8 is the wrong anchor for everything else about this model too.
**Blocks** any claim that the corrected objective fixes RWM-U's uncertainty.


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

### X-06 — The overfit test ran at ensemble 1 with a wall-clock cap · **NEW (Step 4)**
The brief specifies batch 1024, ensemble 5, 2000 iterations. R-16 measures that at 37.2 s per
iteration, i.e. **20.7 hours** — against a brief that budgets "minutes". Run instead at
ensemble 1, batch 1024 (the specified batch retained), capped at 45 minutes, reaching 451
iterations.
**Justification** The test's purpose is to detect a code defect that prevents learning, and
ensemble members are independent given the shared trunk, so ensemble size does not change
what the test can detect. The batch size, which does affect how hard memorisation is, was
kept at the specified value.
**Consequence** R-17's memorisation result is INCOMPLETE rather than passing, and is recorded
as such. The collapse-monitor result is unaffected — it is a property of the optimiser and
the bound-loss gradient, not of ensemble size.

### X-07 — Step 5's main experiment runs at ensemble size 1, not the reference's 5 · **NEW (Step 5)**
The reference and the released checkpoint use `ensemble_size = 5`. Step 5's six runs use 1.
**Justification** C-04: both trunks are shared across the five members, so the ensemble adds
only head-level diversity and contributes nothing to the autoregressive-versus-teacher-forcing
question under test. R-16 measures the cost of the difference at 3.6x at batch 256 — 4.1 h
versus 1.2 h per run, i.e. the whole six-run matrix moves from 7.2 h to over 24 h for no gain
on the claim.
**Consequence** Absolute error values are not directly comparable with the released
checkpoint's, which is a 5-member ensemble mean. The A-versus-B *comparison* is unaffected,
since both arms use 1. Any later claim about ensemble uncertainty needs its own runs.

### X-08 — No gradient clipping is added · **NEW (Step 5)**
Recorded as a deliberate non-deviation: see M-15. The reference has none in this path, so
none is added, even though the R-18 overfit at lr 1e-3 showed loss excursions correlated
across heads. Gradient norms are logged every iteration instead.

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

### S-09 — "Under nRMSE the released checkpoint at offset 1 is clearly informative (below 1.0)" · **NEW (batch 1)**
R-15 reported the released checkpoint's nRMSE at h=368 as 1.3228 under the released evaluation
convention and 0.7572 under the causal one, and framed that as "the difference between worse
than predicting the training mean and clearly informative". The framing is **refuted**: both
figures were measured at n=10 and are biased low (M-17). Re-measured:

| n | nRMSE offset 0 | nRMSE offset 1 | both above 1.0? |
|---|---|---|---|
| 10 | 1.4251 | 1.0292 | yes |
| 100 | 1.8282 | 1.6182 | yes |
| 400 | 2.1724 | 1.8157 | yes |

**What survives:** offset 1 is better than offset 0 on both metrics at every n, so R-15's
ordering — the measured cost of B-05 — stands unaffected. **What does not:** the claim that
the causal convention takes the checkpoint below the "no better than the training mean"
line. It does not; both conventions sit above it at long horizon.
**Superseded by** R-27, M-17. R-15's relative-L1 column is unaffected throughout.


### S-10 — "The released checkpoint loses to the hold-last floor at h=368 under nRMSE" (R-27) · **NEW**
R-27 was promoted to contribution #1 on the strength of a 29% loss to the floor at n=100. Both
gating checks refute it.

**Gate A1 — aggregation.** The loss holds under one of four aggregations. Under the pooled form
(`sqrt(mean_d MSE_d)/mean(scale)`) the model **beats** the floor, 1.1103 vs 1.1750. Excluding the
three gravity dimensions it beats the floor by 40–42% under both forms. The model loses on only
**7 of 45 dimensions**, and `g_z` alone reads 52.31 against a floor of 0.44 because its stored
scale is 0.0292 — a normalisation artifact, not a physical property (R-29).

**Gate A2 — the tail.** The heavy tail that M-17's mechanism required is **two short regions**
(rows 1469–1597 in episode 1, 8414–8593 in episode 8) sampled repeatedly through trajectory
overlap. On strictly non-overlapping trajectories the tail vanishes (max/median 1.2×) and the
model beats the floor (R-30).

**What is retracted:** that the released checkpoint is worse than a constant predictor at long
horizon; that its rollout error is heavy-tailed as a general property; and the contribution
ranking that put this first.

**What survives, and is now the honest form of it:** the released checkpoint models the joints
well and the base orientation and angular velocity poorly, losing to a constant predictor on
`v_z`, `w_x`, `w_y`, `g_x`, `g_y` and `g_z`; and there exist two short stretches of the
held-out data on which its rollout diverges badly. Both are narrower claims about specific
dimensions and specific regions, not about the model overall.

**Superseded by** R-29, R-30, M-19.
**Note** S-09, which R-27 itself established, is unaffected: R-15's *ordering* still stands and
its "crosses below 1.0" framing is still refuted, now for the additional reason that the
threshold was computed under form-2 aggregation.


### S-11 — R-41's per-dimension comparison was NOT matched · **NEW**
R-41 compared **Arm A at 10,000, evaluated on 20 independent trajectories across all ten
episodes (1 of 45 dimensions lost)** against **the released checkpoint's 7 of 45**. Those seven
came from R-29/R-32, which scored the checkpoint on the *held-out pool of 1,202 overlapping
trajectories in episodes 1 and 8* — a different episode set and a different trajectory
construction.

Scored on the same 20 independent trajectories across all ten episodes, the released checkpoint
loses on **18 of 45**, not 7. The figure was already in the ledger: R-34's Task 3b reported "18
of 45" on exactly that evaluation, and R-41 reached past it to the wrong reference set.

**What changes:** the Jaccard overlap falls from 0.14 to **0.06** and the released checkpoint's
count roughly doubles — so R-41's directional conclusion is *strengthened* on this arena, not
weakened. **What is retracted:** my statement, made when the mismatch was raised, that "Q1 was
already matched". It was not. `task5_analyse.py:49` matched Arm A and the floor to all ten
episodes but compared against a seven-dimension set derived elsewhere.
**Superseded by** R-45, which reports both matchings.


---

## Candidate paper contributions

Ordered by how completely evidenced each is, with the paper it bears on tagged. Two papers are
in scope; see the scope note at the top.

1. **The uncertainty output is unusable, and that is a property of the objective, not of the
   training run** `[RWM-U]` (C-06, C-10, C-11, R-48–R-54, O-12, O-13). The most completely
   evidenced claim here, and **novel rather than confirmatory**. Analytic derivation —
   `E[(mu + sigma·eps − y)²] = (mu − y)² + sigma²` is minimised at sigma = 0, and `min_logstd`
   cancels out of the bound loss so the ratchet is one-way. Empirical confirmation across
   **fourteen training runs**. A linear extrapolation validated to 3% over a fourfold extension.
   A corrective experiment using **the authors' own unused `gaussian_nll` branch**. And
   calibration measured against a known reference: the released checkpoint's predicted sigma is
   **7,878× smaller than its own mean absolute error**, giving 0.14% coverage at ±1σ against a
   calibrated 68.3%. The correction reverses the mechanism and still fails — magnitude improves
   to 10.9×, while the faint ordering signal the faithful arm had (39/45 dimensions positive,
   P = 1.4e-06) is **destroyed** (21/45, chance). σ is flat even inside the 8-step trained
   horizon while error grows 3.4×, so no structural excuse survives.

2. **The paper's central claim reproduces, and the margin is large** `[BASE]` (R-22, R-23, M-23,
   R-40, R-42). Confirmatory rather than novel, but stress-tested harder than anything else in
   the project: SETTLED under four independent metric/aggregation variants, at 10 and 100
   trajectories, on a rule committed to git before the runs that tested it existed, with Arm A
   leading 4.4–9.7× at h=368 and the per-episode sign positive on all ten episodes.

3. **Aggregation and evaluation power can invert a published-model comparison — including one
   this project published** `[BOTH]` (R-29, R-30, M-19, S-10, S-11, M-17). Reported as a worked
   example with the retraction attached.

4. **The released checkpoint cannot have come from the released recipe, on three independent
   measures** `[BOTH]` (C-12, C-13, O-12, R-24, R-25, R-41, R-50). Collapse rate implies
   ~158,000 iterations against a tag of 5,000; `min_logstd` on a 5× slower clock implies order
   2.7e5; and under `gaussian_nll` the implied count is **negative**, so the branch it was
   trained with is identifiable.

5. **The released pipeline trains on spliced episodes, and the cost is now measured** `[BASE]`
   (B-01, D-03, D-06, R-47, R-55). Zero of 32 comparisons show harm, and a duplication control
   confirms the training-loss rise is caused by splice content rather than by window count.

6. **There is no held-out evaluation in the released repository** `[BASE]` (B-03, B-04, X-01).

7. **The released evaluation feeds a stale action and understates its own model** `[BASE]`
   (B-05, D-13, R-09, R-15).

8. **The paper's described model is not the implemented model** `[BASE]` (C-01, C-03, C-05,
   C-07, C-09, M-13).

9. **Effective sample size, not trajectory count, bounds every long-horizon claim** `[BOTH]`
   (M-20, M-04, D-12) — only four independent 400-step trajectories exist in the held-out pair.

10. **Correlational tests cannot establish action alignment for position-controlled robots**
    `[BASE]` (M-10, M-11).

11. **A pre-registered rule must be anchored to the regime the claim is about** `[BOTH]` (M-24).

---

## Verification chain

What any downstream number rests on, in order:

| Level | Claim | Result |
|---|---|---|
| Shapes | parameter counts match | R-01, exact |
| Wiring | inference outputs match the reference module | R-11, **0.000e+00** bitwise |
| Indexing | the harness feeds the actions it claims | R-12a, bitwise vs raw CSV |
| Residual | zero-delta model is the hold-last floor | R-12c, 1.19e-07 |
| **Objective** | **losses and gradients match** | **R-14, 0.000e+00 across 7 terms, 106 tensors** |

Step 5 onward inherits all five.
