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
| Licence | `robotic_world_model_lite` Apache 2.0; `rsl_rl_rwm` **BSD 3-Clause** (ETH Zurich, NVIDIA) |

**Resolving `SRC` citations.** Entries below cite upstream source by bare filename. The names are
ambiguous across two repositories, so:

| name in a citation | actual path, at the commit above |
|---|---|
| `system_dynamics.py` | `rsl_rl_rwm/rsl_rl/modules/system_dynamics.py` |
| `mlp.py` | `rsl_rl_rwm/rsl_rl/modules/architectures/mlp.py` |
| `rnn.py` | `rsl_rl_rwm/rsl_rl/modules/architectures/rnn.py` |
| `train.py` | `robotic_world_model_lite/scripts/train.py` |
| `model_training.py` | `robotic_world_model_lite/scripts/model_training.py` |
| `base_cfg.py` | `robotic_world_model_lite/scripts/configs/base_cfg.py` |
| `anymal_d_flat.py` | `robotic_world_model_lite/scripts/envs/anymal_d_flat.py` |
| `anymal_d_flat_cfg.py` | `robotic_world_model_lite/scripts/configs/anymal_d_flat_cfg.py` |

**Status.** Steps 0–5 complete; 17 training runs. **M-23 returns REPRODUCES AT LONG HORIZON (R-40)** under a rule committed to git before the runs existed (`efc35b8`). A full review of the repository is folded in at M-26 to M-31, S-12, S-13 and X-09 — including four retractions of this project's own claims. Last updated: 20 Aug 2026.
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
R-50, R-51, R-52, R-53, R-54, C-14, C-15, R-58, R-59. These concern the variance head, its collapse, and the
calibration of the uncertainty output; none of them is a claim about the base paper.

**`[BASE]`** — M-16, M-23, M-24, R-19, R-22, R-23, R-35, R-36, R-37, R-40, R-42, R-45, R-46,
R-47, R-55, R-56, R-60, and the A/B comparison generally; plus the loss-assembly discrepancies C-01,
C-02, C-05, C-09
and the defects B-01 to B-05.

**`[BOTH]`** — D-01 to D-13 (the dataset is shared), C-03, C-07, C-12, C-13, R-01, R-11, R-14,
and the evaluation-methodology entries M-09, M-12, M-17, M-19, M-20, M-25, M-26, M-27, M-28, M-29, M-30, M-31, M-32, M-33, which apply to any
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

**Correction** These three numbers were stated in the README, RESULTS.md and here with no artifact behind them — the generated claims map recorded this entry's artifacts as `—`, which is precisely the gap the project's own rule forbids. `scripts/step0_velocity_regimes.py` now derives them into `window_accounting` and they are re-derived on every run.
**Evidence** `DATA` `results/step0_regimes.json` (`window_accounting`).
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

### D-10 — Twenty-one commanded-velocity regime segments, not one
Two commands per episode — one change at the midpoint of every one of the ten episodes, each held ~500 steps (10 s) — **plus one extra segment in episode 7**, a short high-variance excursion the detector calls a borderline case (row 7149). Regimes per episode `[2,2,2,2,2,2,2,3,2,2]`. All **21** distinct at 0.10 m/s tolerance, spanning roughly [−0.95, +0.90] × [−0.97, +0.87] m/s.

**Correction** This entry read "Twenty ... All 20 regimes distinct" until the review. Its own evidence file said 21 in three places, and `regimes per episode` printed the 3 for episode 7. The script hard-typed "TWENTY ... two per episode" as a literal; it now derives the count, and `results/step0_report.txt` has been regenerated. Nothing downstream depended on 20 rather than 21 — the consequence below is unchanged — but the number was wrong against the file it cited.
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
| `base_cfg.py` `ModelTrainingConfig.max_iterations` | **500** — the author confirms this is a **typo** (X-10) |
| Paper, Table S7 | **2500** |
| `pretrain_rnn_ens.pt`, `iter` key in the checkpoint | **5000** — the author's own recollection (X-10) |

None of the three is consistent with the released checkpoint's variance state (O-12), so this
is not merely a documentation mismatch — the largest of the three still falls ~6 orders of
magnitude short of explaining the weights that shipped.
**Evidence** `SRC` `base_cfg.py:97`; `EXT` paper Table S7; `DATA` checkpoint `iter` field,
read in R-01.
**Status** CONFIRMED · **Relevance** CONTRIB
**Decision for Step 5** Train to 2500 to match the paper and checkpoint at 500 as well, so
both documented numbers can be reported from one run at no extra cost.


### C-14 — The method penalises EPISTEMIC uncertainty; the aleatoric head is discarded before use · `[RWM-U]` · **NEW**
`pretrain_rnn_ens.pt` carries two uncertainty outputs, and the released method consumes only one
of them. Established from the paper and the code independently, and they agree.

**The paper** (arXiv:2504.16680). Eq. 4 defines the penalised quantity as the variance across
ensemble members, `u_{t+1} = Var_b[μ_b]` — epistemic. Eq. 5 applies it as a reward penalty,
`r̃ = r − λ·u`. The per-member predicted variance enters the training objective (Eq. 1) and
nothing downstream.

**The code**, in order:

| step | site | what happens |
|---|---|---|
| define | `rsl_rl_rwm/rsl_rl/modules/system_dynamics.py:125` | `aleatoric = state_stds.mean(0).sum(-1)` |
| define | `system_dynamics.py:126` | `epistemic = state_means.std(0).sum(-1)` |
| **discard** | `robotic_world_model_lite/scripts/envs/base.py:142` | aleatoric is bound to a local that is never read again; epistemic is stored on `self` |
| return | `envs/base.py:158` | only `self.epistemic_uncertainty` reaches the policy loop |
| **apply** | `envs/base.py:166` | `rewards += uncertainty_penalty_weight * self.epistemic_uncertainty * dt` |
| configure | `scripts/configs/anymal_d_flat_cfg.py:30` | `uncertainty_penalty_weight = -1.0` |

`rsl_rl/algorithms/mbpo_ppo.py:253` and `:259` unpack both uncertainties into `_`; that path is
model evaluation rather than policy training, so it is not the operative site.

**Consequence.** The aleatoric head — the one the state loss and bound loss actually shape, and
the one C-10, C-11 and R-48 to R-54 analyse — is computed on every imagination step and thrown
away. Any claim that "the released checkpoint's uncertainty output" is unusable must say which
output it means. See S-14.
**Confirmed by the author (X-10):** "The aleatoric term is not used in downstream training. It is
reported in Fig. 3 (right) as an analysis of the model behavior." So the discard is intended
design, not an implementation slip.
**Evidence** `SRC` `rsl_rl_rwm/rsl_rl/modules/system_dynamics.py:125-126`,
`robotic_world_model_lite/scripts/envs/base.py:142,158,166`,
`robotic_world_model_lite/scripts/configs/anymal_d_flat_cfg.py:30`;
`EXT` arXiv:2504.16680 Eq. 4-5; `EXT` personal communication, C. Li, 21 August 2026.
**Status** CONFIRMED · **Relevance** CONTRIB


### C-15 — Eq. 4 defines the penalty on variance; the code computes a standard deviation · `[RWM-U]` · **NEW**
Eq. 4 of arXiv:2504.16680 gives `u_{t+1} = Var_b[μ_b]`. `system_dynamics.py:126` computes
`state_means.std(dim=0).sum(dim=1)` — a standard deviation, not a variance, and summed over the
45 state dimensions rather than left per-dimension. With λ = 1.0 the two differ by a square, so
the penalty the released configuration actually applies is not the one the paper writes down.

**Answered by the author (X-10).** Asked which form was intended, the first author replied that
"the lambda is applied to the standard deviation in the implementation as intended, in contrast to
Eq. 4 being more of a high-level explanation." So the code is operative and Eq. 4 is a high-level
description. This is a **notational gap in the paper, not an implementation error**, and it is
recorded as such rather than as a defect. R-58 measures the code's quantity, which is now known to
be the intended one.
**Evidence** `SRC` `rsl_rl_rwm/rsl_rl/modules/system_dynamics.py:126`; `EXT` arXiv:2504.16680 Eq. 4;
`EXT` personal communication, C. Li, 21 August 2026.
**Status** RESOLVED — the code is intended · **Relevance** CONTRIB


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
**Correction** The convention stated here is right; the code that implemented it resampled the
pooled seed x trajectory vector instead of the trajectories. See M-27, which measures the
effect and restates the affected counts.
**Evidence** `RUN` Task 4's floor instability; adopted as convention.
**Status** ADOPTED · **Relevance** METHOD


### M-26 — A pre-registered rule must be anchored to an adequately powered statistic · **NEW**
M-24 recorded that a pre-registered rule must be anchored to the *regime* the claim is about.
This is the same lesson in a second dimension, and it was learned the same way — by watching a
rule return the wrong answer for a reason that had nothing to do with the hypothesis.

Task 3's expectation named a threshold on the training loss "at 2500". (That expectation was
not committed before the runs — S-12 withdraws the pre-registration framing. The estimator
lesson below stands independently of that.) The quantity that phrase resolved
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


### M-27 — The bootstrap was resampling the wrong unit · **NEW**
M-25 adopted the right convention — "resample the **independent trajectories** with
replacement" — and the code did not implement it.

`scripts/task5_2_bootstrap.py:44-46` and `scripts/task4_contamination_analysis.py:44-45` both
build the sample as `np.concatenate([per_traj(model(seed=s), ...) for s in SEEDS])`, so the
vector handed to the resampler has length **3 x n_traj** while the record written beside it
reports `n_independent = n_traj` and `task5_2_report.txt` describes the interval as being over
independent trajectories. Each trajectory appears three times, once per training seed, and those
three values share the same held-out rows. Resampling them independently breaks the clustering
and can only narrow the interval.

**Measured, across the 16 A/B cells** (`results/review_bootstrap_unit.json`): the correct
cluster bootstrap — resample trajectories, carry all three seeds — widens the interval by a mean
factor of **1.42x** (range 0.96x to
1.69x). That is close to the sqrt(3) = 1.73 expected when between-seed
variation is small against between-trajectory variation, which is exactly what M-25 itself
predicted when it noted seed spreads of 0.003–0.031 against trajectory-driven swings ten times
larger.

**1 of 16 verdicts change**, all in the same direction
(significant becomes non-significant): `out-of-sample|200|2500|h8`.
It is an h=8 cell, in the regime M-24 and R-42 already record as unresolvable out-of-sample.
Every h=368 long-horizon verdict survives.

**Convention.** Where a statistic pools several training seeds over a shared set of evaluation
trajectories, the bootstrap resamples **trajectories**, carrying every seed with each draw.
Reporting `n_independent` next to an interval resampled over `3 x n_independent` values
misstates the interval. Both units are reported in `results/task3_three_way.json` so the
previously published counts stay traceable.
**Evidence** `RUN` `results/review_bootstrap_unit.json`, `results/task3_three_way.json`;
`SRC` `scripts/task5_2_bootstrap.py:28-32,44-46`, `scripts/task4_contamination_analysis.py:27-29,44-45`.
**Status** ADOPTED · **Relevance** METHOD


### M-28 — The clean-clone test was counting files the clone carried in · **NEW**
The headline reproducibility claim — "a clean-clone run of `reproduce.sh --quick` regenerates
**258,700 numeric values bitwise**" — was measuring something other than what it said, and the
mechanism could not have measured the right thing.

**Where 258,700 came from.** `results/` is committed, so a clean clone already contains every
artifact. `verify_reproduction.py` compared the clone's directory against the committed one and
counted every numeric value in every file — including the ~44 files the run never rewrote, which
compare identical because `git clone` put them there. Reconstructed at the commit that published
the figure (`0519916`): 258,704 numeric values across 37 JSON files, minus the 4 documented NaNs
= **258,700 exactly**, and the timing count matches its documented 1,439 exactly. The arithmetic
was right; the label was wrong.

**What `--quick --force` actually regenerates**, measured from a real clean clone with the upstreams symlinked in: **19 files, 4,804 numeric values, 4,804 bitwise identical (100.00%), 0 differing**, and **0 keys lost**. Excluded and reported separately: 2,362 timing fields and 22 values in `step4_5_timing.json`, which is wholly a measurement of the host — its projected runtimes, peak RSS and repeat-to-repeat standard deviation are all machine-dependent, and the key-level timing filter did not catch them. The other 424,883 values sit in files the clone carried in.

(The first honest measurement gave 8 files and 1,129 values. M-29's thirteen added stages raised genuine coverage 4.3× — the pipeline now regenerates far more of what it claims to, which is the point of having staged them.)

So the determinism result is real and perfect **within its true scope**, and that scope is
1.9% of what was claimed — not the ~100% the prose implied.

**A second defect the same run exposed.** Regenerating `manifest.json` from a clean clone
**deleted three whole blocks** — `statistics_convention`, `evaluation_power` and
`aggregation_convention`. No script wrote them; they had been added to the artifact by hand after
`score_reference.py` produced it, so the documented pipeline destroyed them. And
`verify_reproduction.py` could not see the loss: it iterated the committed keys and skipped any
with no counterpart in the regenerated file, so a **deletion always looked like a match**.

**Fixes, all three mechanical.** `reproduce.sh` records each output it regenerates in a
transient `_regenerated.txt` manifest beside them (gitignored — it describes one run, not the
repository); `verify_reproduction.py` partitions regenerated from carried-in files,
reports deletions as failures, and writes `results/verify_reproduction.json` so the claim cites an
artifact instead of prose; `score_reference.py` emits the three convention blocks so the manifest
is wholly script-generated. Verified: the manifest now regenerates with only its timing field
differing.
**Evidence** `RUN` `results/verify_reproduction.json`;
`SRC` `scripts/verify_reproduction.py`, `reproduce.sh`, `src/score_reference.py`.
**Status** ADOPTED · **Relevance** METHOD


### M-29 — Most of the pipeline was not in the pipeline · **NEW**
`reproduce.sh` opens "Regenerate every number in the paper from a clean clone". It had 16 stages
covering 11 of 31 scripts. Twenty were outside it, and between them they produced the evidence for
the project's two headline contributions:

- `results/step6_analysis.json` — the sole cited artifact for **R-22, R-23, R-24, R-26**,
  including the base paper's central A/B reproduction — was produced by `step6_analyse.py`, which
  no stage ran.
- `results/task1_calibration.json` — the sole cited artifact for the whole of **contribution 1** —
  was produced by `task1_calibration.py`, which no stage ran.
- `results/step4_0a_results.json`, which holds the nRMSE scale vector that **stage 14 loads**, was
  produced by a script outside the pipeline. The pipeline consumed an artifact it could not make.

**And a full run could not have completed.** `run_remaining.sh` trained five runs — A1, A2, B0,
B1, B2 — while stages 12–15 iterate `SEEDS=(0,1,2)` over both arms. `armA_seed0` was run by hand
before that driver existed and is recorded in no driver log; its `s_per_iter` of 1.850 against
`armA_seed1`'s 1.165 is a 59% outlier that no other run explains. A clean clone would have
trained five runs and then failed looking for the sixth.

**Fixed.** 38 stages now cover every script whose artifact any ledger entry cites — the
sole exception being `verify_reproduction.py`, which runs *against* a regenerated tree rather than
inside it. `run_remaining.sh` trains A0 first and skips runs whose JSON already exists, so
re-running is cheap. `run_control.sh` is stage 11b.
**The new stages were themselves wrong, and a clean-clone run caught them.** Two of the
thirteen added stages failed on first execution from an empty clone:
`task3_4_power_and_ddof.py` loads `runs/armA_seed0/weights_500.pt` and had been staged without
`NEEDS_WEIGHTS`; and `step4_4_overfit.py` had been staged bare, so it wrote untagged files that
are not committed and left `results/overfit_weights_b32lr1e3.pt` — stage 8l's input — absent. The
correct flags were recoverable from each artifact's own `config` block
(`--batch 32 --ensemble 1 --lr 1e-3 --tag _b32lr1e3`, and `--batch 1024 --ensemble 1
--max-seconds 2700 --tag _ens1`), which is the one thing this repository had done right there.
Recorded because it is the first evidence that the clean-clone test has teeth: before M-28 it
would have reported success on both.

**Evidence** `SRC` `reproduce.sh`, `run_remaining.sh`.
**Status** ADOPTED · **Relevance** METHOD


### M-30 — A driver corrupted itself mid-run, and the ledger did not record it · **NEW**
`results/tasks45_driver.log` shows the three contamination runs starting, then:

```
./run_tasks45.sh: line 9: d2_contam_report.txt: command not found
./run_tasks45.sh: line 10: syntax error near unexpected token `done'
```

That is the signature of a running bash script being edited in place: bash reads the file by byte
offset as it executes, so an edit shifts the bytes under it. The three contamination runs survived
because they had already been dispatched; the `gaussian_nll` half of the loop never ran and was
relaunched as `run_nll.sh`. The log records no exit status for the three contamination runs, unlike
`run_nll.sh` and `run_control.sh`, which record one per run.

Two things follow. The on-disk `run_tasks45.sh` is **not the script that produced the contaminated
runs**, so `reproduce.sh` stage 11 points at a file that never ran to completion in that form. And
for a project whose thesis is an append-only record of every wrong turn, an aborted driver and a
replacement script created in response to it had no D-, M- or O- entry until this one.

**Convention adopted.** Never edit a shell script while it is executing; copy, edit the copy, and
relaunch. Every driver records a per-run exit status, as `run_nll.sh` and `run_control.sh` do.
**Evidence** `RUN` `results/tasks45_driver.log`, `results/nll_driver.log`, `results/control_driver.log`.
**Status** ADOPTED · **Relevance** METHOD


### M-31 — R-33's verdict turns on a criterion that changed between the two scripts · **NEW**
`scripts/taskAB_gate_r27.py:145-147` states the Jensen test as **three** conditions, all required:

```
mean_MSE          max/min < 1.05
sqrt_of_mean_MSE  max/min < 1.05
mean_of_sqrt_MSE  last > first x 1.20
```

`scripts/batch1_retract_jensen_char.py:102` states it as **two**, with both thresholds relaxed:

```
sqrt_of_mean_MSE  max/min < 1.10        (was 1.05)
mean_of_sqrt_MSE  last > first x 1.15   (was 1.20)
```

The `mean_MSE` flatness condition was dropped entirely.

**On batch1's own 40-seed numbers** the two criteria disagree, and the dropped condition is the
one that fails: v1 = **1.1159** (needed < 1.05), v2 = 1.0434, v3 = 1.6243. Under the
original three-condition criterion the verdict is **NOT established**; under the revised
two-condition one it is **SUPPORTED**. So R-33's "SUPPORTED at 40 seeds" is carried by the
criterion change, not by the extra seeds.

**In fairness, two things.** The artifact does not conceal it — `mean_MSE_flat` is recorded as
`False` in `results/batch1_post_retraction.json`, and the script prints a note that
mean MSE still varies 1.12× at 40 seeds. And dropping that condition is *defensible on
theory*: Jensen's inequality does not require `mean_MSE` to be flat across n. E[√X] < √E[X]
whatever E[X] does; flatness of the mean was never part of the mechanism, only a convenient proxy
for "the sampling distribution has settled".

**What is not defensible is doing it silently.** The criterion was written down, the data were
seen, the criterion was changed, and the entry recording the result says none of that — the
report states the test in words with no thresholds at all. That is the same failure S-12 records
for Task 3 and M-26 for the estimator: a rule stated in advance loses its force the moment it is
revised after the answer is visible, however good the reason.

**Convention.** Where a later script restates an earlier script's acceptance criterion, it prints
both, evaluates both, and the ledger entry records the disagreement if there is one.
**Evidence** `RUN` `results/batch1_post_retraction.json`, `results/taskAB_gate_r27.json`;
`SRC` `scripts/taskAB_gate_r27.py:145-147`, `scripts/batch1_retract_jensen_char.py:102`.
**Status** ADOPTED · **Relevance** METHOD


### M-32 — Measure the quantity the method consumes, not the one that is easiest to reach · **NEW**
R-48 to R-54 measured the aleatoric head because it is the head the training objective shapes,
and because the analysis of that objective was already in hand. That made it the natural thing to
measure and the wrong thing to measure alone: C-14 shows the released method discards it and
penalises ensemble disagreement instead.

The finding survived — R-58 shows the consumed quantity is also uncalibrated — but it survived on
the evidence, not by design. Had epistemic been adequately calibrated, the project's headline
claim would have been about a component nothing uses.

**Convention.** Before measuring a model's output, trace it to the site that consumes it and
record that site. Where a claim is about a method rather than a checkpoint, the quantity measured
must be the quantity the method reads.
**Evidence** `SRC` `robotic_world_model_lite/scripts/envs/base.py:142,166`;
`RUN` `results/task_b2_epistemic.json`.
**Status** ADOPTED · **Relevance** METHOD


### M-33 — Decisions this project cannot take on its own · **NEW**
Recorded so they are not revisited under time pressure, and so a reader can see they were
considered rather than missed.

**Venue timing (A6).** MLRC 2026 requires *acceptance* to TMLR between 20 June 2025 and
30 September 2026. TMLR targets a two-month review and does not guarantee it; with rebuttal and
revision, six weeks is not achievable. **Decision: publish to TMLR on its own timeline and do not
compress the work to chase MLRC.** Nothing in this brief was scoped down for a deadline.

**Author contact (E4). DONE — 21 August 2026.** §6 states that the released checkpoint's variance
state is unreachable at any of the three iteration counts its own artifacts give. A warm start or
a different initialisation of `log_delta_logstd` would explain it with no inconsistency, and
neither is visible from the released files. **Dr Chenhao Li, the first author, was written to on
2026-08-21** with that question, plus C-15's variance-versus-standard-deviation discrepancy and
C-14's discarded aleatoric term. No response as of writing. If a warm start or a changed
initialisation is confirmed, §6 becomes a documentation gap rather than an inconsistency and
should shrink accordingly.

**Archival timestamp (E6). DONE — 21 August 2026.** Commit timestamps are settable with
`git commit --date`, and §7 rests on them. The repository is now archived at Software Heritage,
whose visit timestamp is not author-controllable:

Visit date, third-party stamped: **2026-08-21T13:24:43Z**, `visit_status: full`. Verified that the
archived release resolves to exactly the local `v1.0.0` commit.

The identifiers themselves are held in `docs/ARCHIVAL_IDENTIFIERS.md`, which is **excluded from
the supplementary archive**. A SWHID is opaque but resolvable: pasting one into the Software
Heritage UI returns the origin URL, which carries the author's name. So it de-anonymises exactly
as a link would, and the anonymisation check now treats it that way.

**What this does and does not establish, stated precisely.** It does **not** prove that any
individual commit date is genuine — `--date` can still have been used. It proves that the
repository, with the whole pre-registration history in the form the paper cites, existed no later
than 2026-08-21T13:24:43Z, by a party with no interest in the claim. Since submission follows that
moment, nothing in the record can have been back-dated after it. That converts §7 from
self-reported to bounded, which is the strongest thing an archive can do here and is weaker than
proof.

The identifiers are **not** cited in the anonymous submission: they resolve to a named
repository. They are disclosed on acceptance.

**Anonymity tension (A1).** The archival identifier resolves to a named repository, so it cannot
appear in a double-blind submission. The chosen resolution is an anonymised `git log` in the
supplementary material for review, with the identifier disclosed on acceptance. That is the
weakest of the three options the brief lists and it is chosen knowingly: an anonymised git mirror
would change the commit hashes the paper cites, and `anonymous.4open.science` was not relied on
because whether it preserves commit history could not be established without uploading the
repository, which is itself an outward-facing action.
**Evidence** `EXT` TMLR author guidelines; MLRC 2026 eligibility window; Software Heritage API.
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
**Status** SUPERSEDED IN PART by S-09 — the numbers stand as measured, but both were taken
at n=10 and are biased low (M-17); the framing "the difference between worse than predicting
the training mean and clearly informative" is withdrawn. · **Relevance** CONTRIB

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
**Status** **SUPERSEDED BY S-10** — refuted by its own gating checks. The loss holds under
one of four aggregations; under the pooled form the model **beats** the floor (1.1103 vs
1.1750), it loses on only 7 of 45 dimensions (R-29), and the heavy tail the mechanism
required is two short regions sampled repeatedly through trajectory overlap (R-30). The
first artifact cited above records `below_nrmse_floor_at_368 = true`, which is the
generating script's flag for the model BEATING the floor — the citation contradicted the
claim from the outset. · **Relevance** METHOD — retained as the worked example behind
contribution 3, not as a result.
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
**Criterion** This verdict uses a two-condition test; `taskAB_gate_r27.py` had stated a
three-condition one, and on these same numbers the dropped condition fails (v1 = 1.1159 against a
required < 1.05). Under the original criterion the verdict is NOT established. See M-31 — the
change is defensible on theory and was not disclosed.
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
**Unit** The 32 counts above use the naive bootstrap; under the correct cluster unit (M-27)
they become 0 hurt / 9 helped / 23 no effect. The headline — no cell shows harm — is
unchanged (R-56).
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
**Status** SUPERSEDED IN PART by S-14 — the numbers stand; the phrase "the uncertainty
output" does not, because the checkpoint has two and this measured the one the released
method discards (C-14). Replaced in scope by R-58. · **Relevance** CONTRIB

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
**Quantity** Aleatoric — the per-member predicted σ. The released method discards it and penalises ensemble disagreement instead (C-14); R-58 measures that.
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
**Quantity** Aleatoric — the per-member predicted σ. The released method discards it and penalises ensemble disagreement instead (C-14); R-58 measures that.
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
**Status** SUPERSEDED BY S-13 — the quantifier was wrong: Arm B had not been measured on this
axis, and when measured its σ is an order of magnitude more input-dependent than the others.
Replaced by R-57. · **Relevance** METHOD

### R-53 — The correction improved magnitude and destroyed what ordering signal existed · `[RWM-U]` · **NEW**
**Quantity** Aleatoric — the per-member predicted σ. The released method discards it and penalises ensemble disagreement instead (C-14); R-58 measures that.
σ-versus-realised-error correlation, per dimension, pooled across seeds:

| model | mean r | median r | dims with r > 0 | under a coin-flip null |
|---|---|---|---|---|
| faithful Arm A (mse) | **+0.034** | +0.029 | **39 / 45** | P = **5.42e-07** — real |
| corrected Arm A (nll) | **-0.004** | -0.009 | **21 / 45** | P = 0.77 — chance |
| teacher-forced Arm B | **+0.257** | +0.254 | **45 / 45** | P = **5.7e-14** — strongest of the four |
| released checkpoint | +0.001 | −0.010 | 20 / 45 | P = 0.55 — chance |

The faithful arm's correlation is *small but genuine*: 39 of 45 dimensions positive has
probability 5.42e-07 under a fair-coin null, so the constant-σ head
nonetheless carried a faint ordering signal. The corrected arm scores 21 of 45 —
indistinguishable from chance.

**Amended after the review (R-57).** The Arm B row was added later; it was missing when this
entry was written, and it is the strongest ordering signal of the four. The P-values are now
computed by the script rather than quoted; the figure previously given here as 1.4e-06 is the
value for 38 of 45, not 39. Neither change affects the comparison this entry is about — the
correction still removes the faithful arm's ordering — but the table was incomplete.

So the correction **improved the magnitude** (10.9× overconfident against 52.2×) and
**removed the ordering**. An uncertainty estimate that is better scaled but no longer ranks
which predictions are worse is not obviously an improvement for any downstream use.
**P-values retracted.** The binomial P-values in this entry assume the 45 state dimensions are independent. They are not; see S-15 for the retraction and R-61 for the permutation replacement. Every *count* in this entry stands, and no magnitude result here depends on that null.

**Evidence** `RUN` `results/task1_calibration.json`.
**Status** CONFIRMED · **Relevance** CONTRIB

### R-54 — σ is flat *inside* the trained horizon, which removes the structural excuse · `[RWM-U]` · **NEW**
**Quantity** Aleatoric — the per-member predicted σ. The released method discards it and penalises ensemble disagreement instead (C-14); R-58 measures that.
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

**On the statistic the expectation named, the rule fires.** `final_terms.state`, mean of 3 seeds:
clean 1.5364, duplicated 1.7338, contaminated
1.8301 — duplication apparently explaining
67.2% of the rise. Taken literally this retracts
R-47's mechanism.

**It does not, because that statistic is one minibatch.** (The expectation was never committed to git before
the runs; see S-12, which withdraws the pre-registration framing without disturbing the
measurement.) Its sd is 0.1769
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


### R-56 — The three-way comparison: the control is inert, contamination still costs nothing · **NEW**
Completes Task 3. All three arms — clean, duplicated, contaminated — through the identical
32-cell evaluation (2 arenas x 2 trajectory lengths x 2 checkpoints x 2 horizons x 2 metrics),
under both resampling units (M-27). Positive difference means the second arm is worse.

| comparison | unit | hurt | helped | no effect |
|---|---|---|---|---|
| duplicated − clean | cluster | **0** | 2 | 30 |
| contaminated − clean | naive (as published in R-47) | **0** | 10 | 22 |
| contaminated − clean | cluster | **0** | 9 | 23 |
| contaminated − duplicated | cluster | 2 | 8 | 22 |

**R-47 reproduces exactly.** Under the naive unit the contaminated-versus-clean counts are
0 hurt / 10 helped / 22 no effect — the published
figures, regenerated from the weights.

**The headline survives the unit correction.** Under the correct cluster bootstrap contamination
hurts in **0 of 32** cells. One "helped" cell drops to non-significant
(`in-sample|400|500|h8|nrmse`); nothing moves the other way.

**The control is inert in rollout**, as it should be: duplicated differs from clean in
2 of 32 cells, both marginal in-sample 168-step cells. Duplicating
existing windows changes the training loss by 0.90% (R-55) and changes rollout behaviour
essentially not at all.

**Where contamination does look worse than the size-matched control.** Against duplicated rather
than clean, contamination is significantly worse in 2 of 32 cells:
`out-of-sample|400|500|h368|l1`, `out-of-sample|400|500|h368|nrmse`. Both sit in the **four-trajectory** arena at the
**500-iteration** checkpoint — the lowest-power cell in the design, at the earliest checkpoint —
and 32 comparisons at 95% produce about 1.6 false positives by chance. This is not a signal, and
it is recorded here rather than omitted because it is the only place in the design where
contamination looks harmful at all.
**Evidence** `RUN` `results/task3_three_way.json`.
**Status** CONFIRMED · **Relevance** CONTRIB


### R-57 — All four models, measured on one table · **NEW**
R-52 and R-53 were each written against a three-model artifact. Arm B is now measured on the same
axes, at the same checkpoint, pooled over the same three seeds.

| model | err / σ | ±1σ coverage at h=1 | CoV(σ) across batch | dims with r > 0 | P (two-sided, exact) |
|---|---|---|---|---|---|
| faithful Arm A (mse) | 52.2× | 11.67% | 0.0076 | 39/45 | 5.42e-07 |
| corrected Arm A (nll) | 10.9× | 42.78% | 0.0059 | 21/45 | 7.66e-01 |
| teacher-forced Arm B | 315.0× | 12.96% | 0.1188 | 45/45 | 5.68e-14 |
| released checkpoint | 7878.1× | 0.56% | 0.0177 | 20/45 | 5.51e-01 |

**The headline is unaffected and if anything strengthened.** Every model is overconfident by
between one and four orders of magnitude. Arm B — the arm that trains best — is
315× overconfident.

**Two supporting claims were wrong, and in opposite directions.**

*Input-independence (S-13).* Arm B's σ is
16× more variable across inputs
than the faithful arm's, and 6.7x the next highest of the four. σ collapsing to a constant is a property of the **autoregressive** arms
and the released checkpoint, not of the objective in general.

*Ordering.* R-53 read the faithful arm's 39/45 as
"a faint ordering signal" that the correction destroyed. Arm B, absent from that table, scores
**45/45**, P = 5.7e-14
— the strongest σ-versus-error ordering of the four, by a wide margin.

**Which makes the finding sharper rather than weaker.** Arm B has the most input-dependent σ *and*
the best-ordered σ, and is still 315× overconfident. So the failure is
specifically one of **magnitude calibration**: these models can learn which predictions will be
worse, and cannot learn how wrong they will be. A downstream user who needs a ranking might be
served; one who needs an interval is not, under any of the four.

Also corrected here: the P-values are now computed by `scripts/task1_calibration.py` as exact
two-sided binomial tails. R-53 quoted "P ≈ 1.4e-06" for 39/45; the
true value is 5.418e-07 (2.6×
larger than quoted, and 1.4e-06 is the figure for 38/45). The companion "P ≈ 0.66" for 21/45 is
0.766. No conclusion turns on either.
**P-values retracted.** The binomial P-values in this entry assume the 45 state dimensions are independent. They are not; see S-15 for the retraction and R-61 for the permutation replacement. Every *count* in this entry stands, and no magnitude result here depends on that null.

**Evidence** `RUN` `results/task1_calibration.json`.
**Status** CONFIRMED · **Relevance** CONTRIB


### R-58 — The uncertainty the method actually uses is also uncalibrated · `[RWM-U]` · **NEW**
C-14 established that the method penalises epistemic uncertainty and discards the aleatoric head.
This measures the quantity that is used. Released checkpoint, 5 members,
out-of-sample episodes [1, 8], `n_independent` = 4, action
offset 1. Our own arms are ensemble size 1, where epistemic is identically zero by construction
(`system_dynamics.py:126`), so this is possible only on the released checkpoint.

| h | aleatoric err/σ | epistemic err/σ | epi ±1σ | epi ±2σ | dims r>0 | P |
|---|---|---|---|---|---|---|
| 1 | 597× | 4.7× | 17.78% | 37.22% | 23/45 | 1.0e+00 |
| 8 | 802× | 6.3× | 12.15% | 25.14% | 25/45 | 5.5e-01 |
| 32 | 1,530× | 11.1× | 8.70% | 17.66% | 34/45 | 8.2e-04 |
| 128 | 5,132× | 28.4× | 5.42% | 10.95% | 45/45 | 5.7e-14 |
| 368 | 7,878× | 39.7× | 3.76% | 7.69% | 45/45 | 5.7e-14 |

Calibrated reference: 68.3% at ±1σ, 95.4% at ±2σ.

**Epistemic is far better than aleatoric and still badly wrong.** It is 126× to
198× larger than the aleatoric σ across horizons — independently reproducing R-08's
hundredfold estimate and sharpening it — which puts its overconfidence at
**4.7×** at one step rather than 597×.
But ±1σ coverage is **17.78%** at h=1 against a calibrated 68.3%, falling
to **3.76%** at h=368, where overconfidence reaches
**39.7×**.

**Total is indistinguishable from epistemic.** Because σ_epi exceeds σ_alea by two orders of
magnitude, `sqrt(alea² + epi²)` equals the epistemic value to four significant figures at every
horizon measured.

**The magnitude-not-ordering finding extends to it, with the strongest evidence in the project.**
At h=128 and h=368 epistemic correlates positively with realised error on **45
of 45** dimensions, P = 5.7e-14. The ranking is
excellent; the scale is wrong by 40×.

**And the same horizon mechanism applies.** σ_epi grows
1.59× from h=1 to h=368 while realised error grows
13.33×. Ensemble disagreement does not track error
growth either.

**The scalar penalty as applied.** `means.std(0).sum(-1)`, the quantity at `envs/base.py:166`,
correlates +0.3480 with total absolute error over the rollout, mean
0.5172.

**Scope, stated carefully.** This does **not** extend C-06/C-10/C-11's objective argument to the
epistemic term. That argument explains why a *per-member* σ collapses to zero under a sampled-MSE
loss. Ensemble disagreement is not shaped by that mechanism, and why it is miscalibrated is not
established here.
**P-values retracted.** The binomial P-values in this entry assume the 45 state dimensions are independent. They are not; see S-15 for the retraction and R-61 for the permutation replacement. Every *count* in this entry stands, and no magnitude result here depends on that null.

**Evidence** `RUN` `results/task_b2_epistemic.json`.
**Status** CONFIRMED · **Relevance** CONTRIB


### R-59 — One scalar cannot fix it, and the way it fails is the horizon · `[RWM-U]` · **NEW**
The constructive question a reader asks next: if σ has the right shape and the wrong scale, one
multiplier fixes it. It does not, and the failure mode is informative.

A single scalar `c` was fitted on **one** held-out episode and evaluated on the **other**, in both
directions, so it is never fitted on its own test set. Two fits per model: `c@h1` matches ±1σ
coverage to 68.3% at one step, `c@all` matches it over the whole 368-step rollout.

**Fitting at h=1 works at h=1 and fails everywhere else.** For the released checkpoint, on the
epistemic term the method actually uses, `c` = 5.08–5.82 brings one-step coverage to
63–74% — essentially calibrated — and the same scalar leaves h=368 at 17–21%
against a target of 68.3%. On the aleatoric term, `c` = 593–611 gives 64–70% at h=1 and
11–15% at h=368.

**Fitting over the whole rollout fails at both ends.** `c@all` drives one-step coverage to 100% —
an interval so wide it is vacuous where the model is accurate — while still falling short at
h=368.

**Why, and it is the same mechanism as R-54 and R-58.** A constant multiplier cannot track an
error that grows while σ does not. R-58 measured that directly for the epistemic term: σ grows
1.59× from h=1 to h=368 while error grows 13.33×. No scalar reconciles those.

**A second failure, on top of the horizon one.** For the trained arms the scalar does not
transfer between the two held-out episodes even at h=1. The faithful arm fitted on episode 1 and
tested on episode 8 reaches 91.9% coverage; fitted on
episode 8 and tested on episode 1 it reaches 41.9%. With
only two held-out episodes we cannot separate episode difficulty from a genuine failure to
generalise, and we do not claim to.

**What this rules out.** "The head learns the right shape and the wrong scale" is the charitable
reading of R-51 and R-58, and it is wrong. A per-horizon or input-dependent correction might
still work; a constant one does not. That makes the failure structural rather than a units
problem, which is the harder of the two possible outcomes for the method.
**Evidence** `RUN` `results/task_d2_recalibration.json`.
**Status** CONFIRMED · **Relevance** CONTRIB


### R-60 — The headline over three seeds · `[BASE]` · **NEW**
R-40 and the paper's abstract rested on **one** training seed per arm, because only one
10,000-iteration run per arm existed. Four more were run — Arm A seeds 0 and 2, Arm B seeds 0 and
2 — with flags identical to the existing pair.

**Cross-check first, because the aggregate is worthless without it.** A 10,000-iteration run and
the 2,500-iteration run at the same seed share their first 2,500 iterations exactly. All six
pairs agree: **90,000 logged values compared across six
curves, 0 differing, worst absolute difference 0.000e+00.**
`scripts/task_d1_threeseed.py` refuses to form the aggregate if any pair disagrees.

**h = 368, out-of-sample, n_independent = 4:**

| arm | seed 0 | seed 1 | seed 2 | mean ± sd (ddof=1) | relative sd |
|---|---|---|---|---|---|
| A, autoregressive | 0.3894 | 0.3509 | 0.3341 | **0.3582 ± 0.0283** | 7.9% |
| B, teacher forcing | 1.9710 | 1.5540 | 1.4241 | **1.6497 ± 0.2858** | 17.3% |

**Ratio 4.61×**, against 4.4× from the single seed.

**The claim survives and the seed that was quoted was a flattering one — in both directions at
once.** Seed 1 gave Arm A 0.3509 against a three-seed mean of 0.3582
(better than average) and Arm B 1.5540 against 1.6497 (worse than
average). Those errors happened to cancel in the numerator and denominator, so the single-seed
ratio understated rather than overstated the effect. That is luck, not method, and it is exactly
why C1 marked the figure OVERSTATED rather than wrong.

**Teacher forcing is more than twice as seed-variable as autoregressive training** at this
horizon — 17.3% against 7.9% relative.
A single-seed comparison of these two arms is therefore unreliable in a direction a reader cannot
predict, and the paper now says so.
**Evidence** `RUN` `results/task_d1_threeseed.json`,
`results/step5_arm{A,B}_seed{0,1,2}_10k.json`.
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


### O-14 — What the original papers claim, and which claims this work tests · **NEW**
Recorded because the paper had no table of the originals' claims, and a reproduction that does
not say which claims it leaves alone invites the reader to assume it tested all of them.

| # | claim, and where | tested here | verdict |
|---|---|---|---|
| 1 | RWM-AR consistently outperforms RWM-TF; lowest prediction errors across environments (2501.10100 §IV-D, Fig. 6) | **yes** | **REPRODUCES** at long horizon (R-40, R-22) |
| 2 | Teacher forcing gives "poor autoregressive performance" (§IV-C) | **yes** | **REPRODUCES**, and more strongly than stated: Arm B is worse than the hold-last floor (R-58 floor comparison) |
| 3 | M = 32, N = 8 is the optimal configuration (§IV-C) | no | not tested — we use the released configuration and did not sweep it |
| 4 | RWM-AR beats MLP, RSSM and transformer baselines (§IV-D) | no | not tested — the lite release ships only the RNN variant |
| 5 | Zero-shot hardware transfer with minimal sim-to-real loss (§IV-E) | no | not tested — no hardware, and this is a dynamics-model reproduction |
| 6 | MBPO-PPO beats SHAC and Dreamer (§IV-E) | no | not tested — no policy learning reproduced |
| 7 | Generality across quadruped, humanoid and manipulation (§IV-D) | no | not tested — one released dataset, ANYmal D flat |
| 8 | Epistemic uncertainty "closely follows the trend of the prediction error" and justifies "its role as a trust metric" (2504.16680 §5.1) | **yes** | **SUPPORTED as a scalar ranking, against a real baseline** — the applied scalar correlates +0.605 [+0.545, +0.694] with realised error at n_independent = 20, beats the forecast-index counter at every horizon and retains +0.596 after partialling it out (R-63). **Weaker per-dimension than R-58 reported**: the 45/45 count gives a permutation P of 0.0435 out-of-sample and 0.0823 over all ten episodes, and no cell survives multiplicity correction (R-61, S-15). NOT supported as a scale: 34.4x overconfident, though repairable per horizon (R-64) |
| 9 | Aleatoric uncertainty "remains low, reflecting small stochasticity in the environment" (§5.1) | **yes** | **the observation holds, the explanation does not** — it is low because sigma = 0 is the objective's optimum (C-06, C-10, C-11), not because the environment is nearly deterministic |
| 10 | Offline MBRL working on real robots (2504.16680) | no | not tested |
| 11 | Policies transfer to hardware from ~6M state transitions against ~250M for the model-free baseline (§IV-E) — the base paper's headline sample-efficiency result | no | **not tested.** It is a claim about policy learning and hardware deployment: it needs the RL loop, a simulator and an ANYmal. No policy is trained anywhere in this work, so no transition count of ours is comparable. Added in the submission-hardening review; its absence from this table was an omission, since it is the result the base paper leads with |
| 12 | Penalising rewards by ensemble disagreement improves the learned policy (2504.16680 Eq. 4-5, §5) — the follow-up's core method claim | no | **not tested.** We measure the penalty quantity itself — what it is (C-14), how well it tracks error (R-63), whether it is calibrated (R-58, R-62) — but never train a policy with or without it. Our findings bound what the quantity *reports*, not what it *costs*; a miscalibrated scale entering as a relative penalty across candidate actions may cost little or much, and we cannot distinguish those |

**The honest position on 8, revised.** The follow-up does not claim its uncertainty is a calibrated
interval. It claims correlation with prediction error and a role as a trust metric, and our
measurement **supports that claim**. What this work adds is that the quantity is not usable as a
scale, that the aleatoric head is discarded before use (C-14), and that no single scalar repairs
either (R-59). Framing §4 as refuting a calibration claim the authors did not make would be
misattribution.
**Evidence** `EXT` arXiv:2501.10100 §IV-C to §IV-E; arXiv:2504.16680 §5.1, Eq. 4-5;
`RUN` `results/task_b2_epistemic.json`, `results/task5_analysis.json`.
**Status** OPEN — claims 3 to 7 and 10 remain untested here and are the obvious extensions.


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

### X-09 — The earliest analysis lives outside this repository, and everything in it was carried forward · **NEW**
`../rwm_analysis/` holds the first work on this dataset — `analyze_state_action_data.py`,
`diagnose_jump.py`, `verify_resets.py`, a 210-line `report.txt` and four figures — written before
`rwm_repro` existed. It is not tracked by this repository (0 files), so a clone does not receive
it. Recorded here so its absence is deliberate rather than an oversight, and audited so the
absence is safe.

**Audited against the ledger. Nothing in it is contradicted, and nothing substantive is stranded:**

| early finding | where it lives now |
|---|---|
| 10 unmarked resets at rows 999, 1999 … 9999; reset fingerprint | `D-04`, `D-05` |
| 9,961 naive / 352 crossing / 9,609 usable | `D-06`, now derived into `results/step0_regimes.json` |
| assertion 3 fails over all adjacent rows, passes within episodes | `D-04`'s origin |
| action leads position by 4 steps (80 ms), median gain 0.350, ~2.9× wider swing | `D-07`, `task1b_pd_law.py` |
| trot at 1.85 Hz, diagonal co-contact 1.7× chance, duty 52.6–55.2%, two feet down 84.4% | `D-08` |
| one thigh contact, row 7039, RF, no termination | `D-09` |
| column 65 identically zero | `D-03` |

**One derivation step was missing until now.** The early report decomposes the window count as
`10000 rows − 39 tail = 9961 − 352 crossing = 9609`. The ledger carried the three totals but not
the 39-row tail term, which is what makes 9,961 comprehensible rather than arbitrary.
`step0_velocity_regimes.py` now emits the whole chain.

**One cosmetic defect in the early report, not carried forward:** its duty-factor block prints
"thigh channels are nonzero -- check" while listing every thigh duty factor as 0.0%. Both are
true — one contact step in 10,000 rounds to 0.0% — but the line reads as a warning about a
problem that does not exist.
**Evidence** `DATA` `../rwm_analysis/report.txt`; `RUN` `results/step0_regimes.json`.
**Status** CONFIRMED · **Relevance** METHOD


### X-10 — Author correspondence, 21 August 2026 · **NEW**
The first author of both papers, written to on 21 August 2026 (E4), replied the same day. Recorded
here because it settles two open items, softens a third, and supplies one fact not obtainable from
the released artifacts. Quoted with the sender's words; permission to cite has been requested and
this entry will be updated with the outcome.

**1. The aleatoric head is not used downstream — CONFIRMED by the author.**
> "The aleatoric term is not used in downstream training. It is reported in Fig. 3 (right) as an
> analysis of the model behavior."

C-14 was established independently from the paper and the code. It is now confirmed by the person
who wrote both, and the intent is explicit: the head exists to shape training and to be reported,
not to be consumed. That removes any reading of C-14 as an implementation slip.

**2. The standard deviation is intended; Eq. 4 is a simplification — RESOLVES C-15.**
> "The lambda is applied to the standard deviation in the implementation as intended, in contrast
> to Eq. 4 being more of a high-level explanation."

C-15 asked which of the two forms was meant. The answer is the code. Eq. 4 is a high-level
description rather than the operative definition, so this is a notational gap in the paper and not
an implementation error. C-15 is restated accordingly.

**3. The iteration count — `max_iterations: 500` is a typo, and the released repo is not the
training repo.**
> "I could not really remember how I obtained the checkpoint. But I do think it is likely that it
> was trained for 5000 iterations as I always did. I believe the released config with
> max_iterations: 500 is a typo. Please forgive me that the checkpoint was released after a few
> iterations of the repo than the setup I used for the submission."

Three things follow, and only the first two are settled. The `500` is a **typo**, so C-13's
three-way disagreement is really a two-way one. The author's belief is **5,000**, consistent with
the checkpoint tag. And — the fact not otherwise obtainable — **the released repository is several
revisions removed from the setup that produced the checkpoint.**

That last point matters more than the first two. §6 extrapolates from *the released
initialisation* at *the configured learning rate*. If the training setup differed from the
released one, the initialisation and the learning rate the extrapolation assumes may not be the
ones used, and E5 already lists a different `log_delta_logstd` initialisation as the assumption it
cannot rule out. The author does not recall a warm start and does not rule one out either.

**What is NOT settled.** The arithmetic stands: at the released initialisation and learning rate,
the checkpoint's variance state is unreachable in 5,000 iterations. What the reply supplies is a
plausible and author-supplied mechanism for why the released artifacts would not reproduce it — a
drifted repository — rather than a confirmation that they should. §6 is narrowed again to say so,
and its framing moves from an inconsistency in the release to a documentation gap between the
release and the run.
**Evidence** `EXT` personal communication, C. Li, 21 August 2026.
**Status** CONFIRMED · **Relevance** CONTEXT — a source record, not a contribution. The findings it
bears on (C-13, C-14, C-15, O-12) carry their own measured evidence, and correspondence is `EXT`:
it cannot substitute for a measurement, only corroborate or explain one.


---

## H. Superseded claims

Retained deliberately. A reproduction that never records its wrong turns is not showing its work.

### S-01 — "The lite repo may not ship training data"
**Retracts** — an early hypothesis, never a numbered claim
Stated during target selection. **Wrong.** `assets/data/state_action_data_0.csv` ships 10,000 rows of real ANYmal D data.
**Superseded by** D-01.

### S-02 — "The checkpoint is ~1.25M parameters per ensemble member"
**Retracts** — an early hypothesis, never a numbered claim
Derived by dividing total file size by five. **Wrong** — the file also contains optimizer state and an unrelated actor/critic policy.
**Superseded by** R-01. Correct figures: 1,995,569 total, ~1,417,789 for a single-member configuration.

### S-03 — "Boundary crossings inflate protocol B"
**Retracts** — an early hypothesis, never a numbered claim
Stated as the expected explanation for the A/B gap. **Refuted by measurement** — crossing trajectories scored better (0.947) than non-crossing (1.599).
**Superseded by** R-05, D-12.

### S-04 — "The relative-L1 denominator will be numerically fragile here"
**Retracts** — an early hypothesis, never a numbered claim
Anticipated but not observed on this data.
**Superseded by** M-03.
**Partially reinstated at Step 3.5 by M-09** — the concern was correct, just not at the 45-dimensional aggregate where M-03 tested it. At per-group granularity the denominator does collapse: base angular velocity produces `inf`, projected gravity blows up on 11.4% of timesteps at h=368. Recorded here rather than by editing S-04 or M-03, both of which stand as written within their scope.

### S-05 — "The ten episodes may be ten repetitions of one command"
**Retracts** — an early hypothesis, never a numbered claim
Raised as a risk to the value of any held-out split. **Refuted** — twenty distinct commanded-velocity regimes.
**Superseded by** D-10.

### S-06 — "Contacts are four knee then four foot"
**Retracts** — an early hypothesis, never a numbered claim
Working assumption during Step 1. **Corrected** to thigh then foot before any downstream use.
**Superseded by** D-02.

### S-07 — "The training convention leaks the target" · **NEW**
**Retracts** — an early hypothesis, never a numbered claim
Carried as the leading reading of B-05 from Step 2 onward, and stated outright in the Step 3 report, which described the training alignment as "non-causal" on the grounds that `a[t+1]` is the policy's response to `s[t+1]` and therefore leaks it. The Step 3.5 brief's own decision table encoded the same reading as the `k = 0` branch.

**Refuted.** D-13 establishes k = −1: row *t* holds the action that *produced* state[*t*], so `a[t+1]` is the action that produced `s[t+1]` — a genuinely causal input. The training alignment is correct and the *evaluation* alignment is the defective one.
**Superseded by** D-13, and its consequences by R-06's revised reading and R-09.
**Note** R-06 (the training convention scores 0.066 better) was measured before the convention was known and was explicitly flagged as uninterpretable at the time. That caution was the right call: the same measurement supports the opposite conclusion once D-13 fixes the direction.

### S-08 — "Forecast decay is inert because it is configured to 1.0" · **NEW**
**Retracts** C-08
Recorded as C-08 with status UNVERIFIED and an explicit instruction to reconfirm before use. **The premise was wrong**: there is no decay parameter in the implementation to configure. The forecast loop applies a plain unweighted mean over forecast steps.
**Superseded by** C-09.
**Note** The UNVERIFIED flag did its job — the claim was never promoted to a result. This is the `INFER` evidence class working as intended.

### S-09 — "Under nRMSE the released checkpoint at offset 1 is clearly informative (below 1.0)" · **NEW (batch 1)**
**Retracts** R-15
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
**Retracts** R-27
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
**Retracts** R-41
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



### S-12 — "Task 3's duplication rule was pre-registered" · **NEW**
**Retracts** — a framing, not a numbered claim; the wording was corrected in place
**What is retracted:** the description of the Task 3 decision rule as *pre-registered*, in the
sense this project has used that word everywhere else — a rule committed to git before the data
testing it exists (M-16, M-23, R-44).

**The timeline, from `git log` and `results/control_driver.log`:**

| when | what |
|---|---|
| 2026-08-19 05:17:57 | `731748f` puts 1.5364 and 1.8301 into R-47 as observations |
| 2026-08-19 19:24:18 | the three control runs start |
| 2026-08-19 19:26:59 | `6fdbd22` — machinery only (`run_control.sh`, `--duplicated`, `n_extra`); **no threshold** |
| 2026-08-19 21:37:51 | the runs finish; the answer exists |
| 2026-08-20 00:34:03 | `3ee9d97` — the **first** commit containing the decision rule |

The rule was stated in conversation before launch and written into the ledger after the answer
was known. Compare M-16, registered 80 minutes before its first data, and M-23, registered 3
minutes before its runs were launched. This one has no such lead, and a `git log -S` for any
threshold keyed to those numbers returns nothing before `3ee9d97`.

**Why it matters more here than it looks.** The result went the way the un-committed rule
predicted, *and* the estimator was changed after the fact (M-26). Those two facts together are
exactly the configuration pre-registration exists to rule out. Nothing in the git record
distinguishes what happened from post-hoc construction.

**What survives.** The control is still a control: the duplicated arm was built and run without
reference to its outcome, its dataset differs from the contaminated arm's in content only, and
the analysis script asserts arm comparability from the run files themselves. The
*measurement* stands; only the claim about its epistemic status is withdrawn.

**Replaces** the word "pre-registered" in R-55 and M-26 with the accurate description: an
expectation stated in advance but not committed.
**Evidence** `RUN` `git log`, `results/control_driver.log`.
**Status** RETRACTED · **Relevance** METHOD

### S-13 — "σ is input-independent in all four models" (R-52) · **NEW**
**What is retracted:** R-52's quantifier. When it was written, `results/task1_calibration.json`
held **three** models — faithful, corrected and released. The teacher-forced Arm B had no
coefficient-of-variation measurement anywhere in `results/`, so "all four" was asserted for a
model that had not been measured on this axis. The review caught the arithmetic mismatch between
the claim and its sole cited artifact.

Arm B has since been measured. Its σ varies across the batch with **CoV
0.1188**, against 0.0076 for the
faithful arm — **16× more
input-dependent**, and 6.7x above the next highest (released ckpt, 0.0177). The claim is false for
the fourth model, not merely unevidenced.

**What survives:** R-51. All four models remain catastrophically overconfident, Arm B included —
315× at h=1 with 12.96% coverage
against a calibrated 68.3%. Input-independence was a supporting observation, not the finding.
**Replaced by** R-57.
**Retracts** R-52
**Evidence** `RUN` `results/task1_calibration.json`.
**Status** RETRACTED · **Relevance** METHOD


### S-14 — "The released checkpoint's uncertainty output is worthless" (R-49) · **NEW**
**What is retracted:** the definite article. R-49 is titled "the released checkpoint's uncertainty
output", singular and unqualified. The checkpoint emits **two** uncertainty quantities
(`system_dynamics.py:125-126`), and R-49 measured the aleatoric one — which C-14 shows the
released method computes and discards at `envs/base.py:142`.

**What survives, unchanged:** every number in R-49. The aleatoric σ is 7,878× smaller than the
realised error and its ±1σ coverage is 0.04% at h=368. Those were measured correctly and are
reproduced independently by R-58's aleatoric column.

**What replaces it:** R-58, which measures the quantity the method actually penalises and finds it
also uncalibrated — 4.7× at h=1 rising to 39.7× at h=368, with 3.76% coverage. The conclusion is
therefore unchanged in direction and stronger in scope: both of the checkpoint's uncertainty
outputs are unusable as intervals. What was wrong was implying, by omission, that the measured one
was the operative one.
**Retracts** R-49
**Evidence** `SRC` `robotic_world_model_lite/scripts/envs/base.py:142`;
`RUN` `results/task_b2_epistemic.json`.
**Status** RETRACTED · **Relevance** METHOD



### R-61 — The dimension-count P-values assumed independence the data does not have · `[RWM-U]` `[BASE]` · **NEW**
Every "39 of 45" and "45 of 45" in this paper was converted to a P-value by a two-sided exact
binomial against a fair-coin null. That null says: absent any association between σ and error,
each of the 45 state dimensions independently has probability ½ of showing a positive
correlation. **The 45 dimensions are not independent**, and the resulting P-values are wrong by
up to **10^13×** on the cells this paper cited as evidence.

Two distinct dependencies break the assumption:

1. **Physical coupling.** Position, velocity and torque for the same joint move together; base
   linear and angular velocity are coupled through the gait. The 45 dimensions carry far fewer
   than 45 independent signs.
2. **Shared forecast-depth trend.** Every trajectory's error grows with rollout step, and any σ
   that also grows with rollout step correlates with *any* trajectory's error — including a
   trajectory it was never paired with. This one is the larger effect and it is not obvious.

**The replacement.** `scripts/task_b_permutation.py` permutes **whole trajectories**: the null
pairs each trajectory's σ with another trajectory's realised error, leaving both marginals and
the entire cross-dimension dependence structure intact, and destroying only the pairing. The
observed count is referred to that null. Whole trajectories move together, so coupling is
preserved by construction rather than modelled.

The observed counts reproduce `results/task1_calibration.json` and
`results/task_b2_epistemic.json` **exactly, on all nine cells they share** — the statistic is the
same one, only the reference distribution changed.

**How wrong the binomial null was.** It centres the count at 22.5 of 45. The
dependence-preserving null centres it between 5.4 and 43.8
depending on model, horizon and arena.

**The worst affected cell is the one the paper leaned on hardest.** Teacher-forced Arm B at
h=368 in the in-sample arena moves from 5.68e-14 to
**0.5656** — a factor of 9.95e+12, about
10^13 — because a random re-pairing already yields
**43.8 of 45** positive on average. Observing 45/45
against a null that expects 43.8 is close to unremarkable.

A larger ratio exists in the table — released aleatoric at h=32 in-sample, 0/45, where the
binomial is "significant" in the *negative* direction and the permutation P is 1.0000 — but no
claim in this paper ever rested on that cell, and quoting it as the headline correction would
overstate the damage by pointing at evidence nobody used.

**Out-of-sample arena, n_independent = 4, attainable P floor
0.04167:**

| model | h | count | binomial P | permutation P | null mean | state groups + |
|---|---|---|---|---|---|---|
| faithful (mse) | 1 | 36/45 | 6.57e-05 | **0.2174** | 16.7 | 6/6 |
| faithful (mse) | 8 | 33/45 | 2.46e-03 | **0.2174** | 11.4 | 6/6 |
| faithful (mse) | 32 | 30/45 | 3.57e-02 | **0.0435** | 8.8 | 5/6 |
| faithful (mse) | 128 | 26/45 | 3.71e-01 | **0.0435** | 5.4 | 5/6 |
| faithful (mse) | 368 | 39/45 | 5.42e-07 | **0.0417** *(at floor)* | 7.8 | 6/6 |
| corrected (nll) | 1 | 16/45 | 7.25e-02 | **1.0000** | 24.6 | 2/6 |
| corrected (nll) | 8 | 20/45 | 5.51e-01 | **1.0000** | 26.4 | 2/6 |
| corrected (nll) | 32 | 19/45 | 3.71e-01 | **1.0000** | 21.7 | 0/6 |
| corrected (nll) | 128 | 26/45 | 3.71e-01 | **1.0000** | 26.0 | 3/6 |
| corrected (nll) | 368 | 21/45 | 7.66e-01 | **1.0000** | 21.8 | 2/6 |
| teacher-forced armB | 1 | 33/45 | 2.46e-03 | **0.2174** | 22.0 | 5/6 |
| teacher-forced armB | 8 | 39/45 | 5.42e-07 | **0.2174** | 22.7 | 5/6 |
| teacher-forced armB | 32 | 14/45 | 1.61e-02 | **0.3478** | 14.3 | 1/6 |
| teacher-forced armB | 128 | 36/45 | 6.57e-05 | **0.3043** | 26.0 | 6/6 |
| teacher-forced armB | 368 | 45/45 | 5.68e-14 | **0.2609** | 29.3 | 6/6 |
| released aleatoric | 1 | 20/45 | 5.51e-01 | **0.6087** | 22.9 | 2/6 |
| released aleatoric | 8 | 15/45 | 3.57e-02 | **0.7391** | 19.8 | 0/6 |
| released aleatoric | 32 | 7/45 | 3.12e-06 | **0.9565** | 17.5 | 0/6 |
| released aleatoric | 128 | 29/45 | 7.25e-02 | **0.7391** | 29.8 | 4/6 |
| released aleatoric | 368 | 20/45 | 5.51e-01 | **0.6957** | 24.4 | 2/6 |
| released EPISTEMIC | 1 | 23/45 | 1.00e+00 | **0.4348** | 22.8 | 2/6 |
| released EPISTEMIC | 8 | 25/45 | 5.51e-01 | **0.3043** | 22.6 | 3/6 |
| released EPISTEMIC | 32 | 34/45 | 8.24e-04 | **0.2174** | 31.4 | 4/6 |
| released EPISTEMIC | 128 | 45/45 | 5.68e-14 | **0.0417** *(at floor)* | 38.2 | 6/6 |
| released EPISTEMIC | 368 | 45/45 | 5.68e-14 | **0.0435** | 33.7 | 6/6 |

**In-sample arena, n_independent = 16, attainable P floor 5e-05:**

| model | h | count | binomial P | permutation P | null mean | state groups + |
|---|---|---|---|---|---|---|
| faithful (mse) | 1 | 45/45 | 5.68e-14 | **0.0106** | 14.9 | 6/6 |
| faithful (mse) | 8 | 41/45 | 9.33e-09 | **0.0882** | 16.9 | 5/6 |
| faithful (mse) | 32 | 44/45 | 2.61e-12 | **0.0633** | 20.2 | 6/6 |
| faithful (mse) | 128 | 43/45 | 5.89e-11 | **0.0293** | 24.3 | 6/6 |
| faithful (mse) | 368 | 42/45 | 8.65e-10 | **0.0232** | 26.6 | 6/6 |
| corrected (nll) | 1 | 25/45 | 5.51e-01 | **1.0000** | 25.6 | 4/6 |
| corrected (nll) | 8 | 28/45 | 1.35e-01 | **0.9744** | 28.0 | 4/6 |
| corrected (nll) | 32 | 29/45 | 7.25e-02 | **0.6750** | 28.5 | 3/6 |
| corrected (nll) | 128 | 23/45 | 1.00e+00 | **0.9651** | 23.0 | 3/6 |
| corrected (nll) | 368 | 27/45 | 2.33e-01 | **0.8734** | 26.9 | 4/6 |
| teacher-forced armB | 1 | 45/45 | 5.68e-14 | **0.0150** | 14.4 | 6/6 |
| teacher-forced armB | 8 | 39/45 | 5.42e-07 | **0.0575** | 10.5 | 5/6 |
| teacher-forced armB | 32 | 44/45 | 2.61e-12 | **0.0249** | 12.7 | 6/6 |
| teacher-forced armB | 128 | 44/45 | 2.61e-12 | **0.0027** | 18.0 | 6/6 |
| teacher-forced armB | 368 | 45/45 | 5.68e-14 | **0.5656** | 43.8 | 6/6 |
| released aleatoric | 1 | 7/45 | 3.12e-06 | **0.6854** | 16.7 | 0/6 |
| released aleatoric | 8 | 25/45 | 5.51e-01 | **0.3085** | 16.7 | 3/6 |
| released aleatoric | 32 | 0/45 | 5.68e-14 | **1.0000** | 21.1 | 0/6 |
| released aleatoric | 128 | 29/45 | 7.25e-02 | **0.4345** | 25.3 | 3/6 |
| released aleatoric | 368 | 3/45 | 8.65e-10 | **0.9738** | 20.4 | 0/6 |
| released EPISTEMIC | 1 | 44/45 | 2.61e-12 | **0.0060** | 16.0 | 6/6 |
| released EPISTEMIC | 8 | 45/45 | 5.68e-14 | **0.0084** | 16.2 | 6/6 |
| released EPISTEMIC | 32 | 45/45 | 5.68e-14 | **0.0349** | 16.1 | 6/6 |
| released EPISTEMIC | 128 | 45/45 | 5.68e-14 | **0.3804** | 42.7 | 6/6 |
| released EPISTEMIC | 368 | 45/45 | 5.68e-14 | **0.0758** | 34.9 | 6/6 |

**Nothing survives multiplicity correction in either arena.** Holm–Bonferroni over the
25 cells of each arena at α = 0.05 rejects
**0** out-of-sample and **0** in-sample. Out of
sample this is a design limit rather than a result: the P floor 0.04167 exceeds the
smallest Holm threshold 0.002, so that arena **cannot** reject at
any effect size. In sample it is a real miss — the smallest P in the family is
teacher-forced armB h=128 at 0.0027 against a threshold of
0.00200.

**The two arenas disagree about where the epistemic effect lives, and that disagreement is the
finding.** Out of sample the released checkpoint's epistemic term looks strongest at long horizon
(0.0417 at h=128,
0.0435 at h=368) and unremarkable at short
(0.4348 at h=1). In sample, with four times the
resolution, it is the **opposite**: 0.0060 at h=1 and
0.0084 at h=8, against
0.3804 at h=128. The mechanism is visible in the null
means: at long horizon the shared forecast-depth trend inflates the null to
42.7 of 45, so 45/45 says little; at short horizon the
null sits near 16.0 and the same count is surprising.

**What this costs the paper.** The claim that Arm B shows "the strongest ordering signal of the
four" does not survive: its 45/45 at h=368 is P = 0.2609
out of sample and 0.5656 in sample — not significant
anywhere, against a null mean of 43.8 of 45. The
epistemic ordering that supports the follow-up's trust-metric claim is marginal at best and its
horizon dependence points in opposite directions in the two arenas.

**What survives.** The **magnitude** findings are untouched — every overconfidence ratio, every
coverage figure, R-51, R-57's ratios and R-58's 39.7× rest on no independence assumption at all.
The direction of every count is also unchanged. What is withdrawn is the strength of evidence
claimed for the *ordering*, and with it the phrase "strongest evidence in this paper".

A coarser fallback is reported alongside: aggregating to the **six state groups** rather than 45
dimensions, which is closer to the number of genuinely independent signals. Those counts appear in
the last column of both tables.
**Evidence** `RUN` `results/task_b_permutation.json`; `scripts/task_b_permutation.py`.
**Status** CONFIRMED · **Relevance** CONTRIB



### R-62 — The epistemic table at n_independent = 20, and a short-horizon result that reverses our own · `[RWM-U]` · **NEW**
R-58 measured the released checkpoint on the **4** independent
trajectories the held-out pair admits. That restriction buys nothing here: **the released
checkpoint trained on all ten episodes**, so there is no held-out arena for it at all, and
confining it to two episodes costs four fifths of the sample for no gain in independence. This
repeats the table on all 10 episodes —
**20 mutually non-overlapping 400-step trajectories**,
n_independent = 20.

| h | aleatoric err/σ | epistemic err/σ | ±1σ | ±2σ | dims r>0 | mean r | permutation P |
|---|---|---|---|---|---|---|---|
| 1 | 1,827× | 8.3× | 16.22% | 30.11% | 44/45 | +0.662 | 0.0060 |
| 8 | 3,034× | 15.1× | 9.99% | 19.76% | 45/45 | +0.427 | 0.0085 |
| 32 | 4,525× | 22.6× | 6.95% | 13.68% | 45/45 | +0.426 | 0.0355 |
| 128 | 14,934× | 34.2× | 4.37% | 8.75% | 45/45 | +0.338 | 0.3725 |
| 368 | 20,669× | 34.4× | 3.59% | 7.19% | 45/45 | +0.298 | 0.0823 |

**The direction of every finding survives.** The epistemic term remains uncalibrated by more than
an order of magnitude at every horizon, reaching
34.4× with
3.59% coverage at ±1σ against a calibrated 68.3%.

**One result reverses, and it is one of ours.** At n=4 the epistemic ordering read as chance at
short horizon — 23/45 at h=1 — and R-58 described
the ordering as a long-horizon property. At n=20 it is
**44/45 at h=1**, with mean r =
+0.662, the *highest* of any horizon, and permutation
P = 0.0060. The in-sample arena (R-61) says
the same independently. **The short-horizon null was an artifact of four trajectories.** It is
recorded here rather than quietly dropped because the horizon story it supported was the more
interesting one, and it was ours.
**Evidence** `RUN` `results/task_d_nind20.json`; `scripts/task_d_nind20.py`.
**Status** CONFIRMED · **Relevance** CONTRIB


### R-63 — Ensemble disagreement beats the free baseline, and that is the one claim we strengthen · `[RWM-U]` · **NEW**
arXiv:2504.16680 justifies ensemble disagreement as a trust metric because it "closely follows the
trend of the prediction error". Neither original paper asks whether it beats a trivial competitor.

**The trivial competitor is the forecast step index.** Error grows with rollout depth, so a counter
— no ensemble, no second forward pass, no model — already tracks error. If the counter ranks as
well, the ensemble is not earning its cost and the trust-metric claim is close to vacuous.

Measured on the scalar the method actually applies, `means.std(0).sum(-1)` at `envs/base.py:166`,
against total absolute error, over n_independent = 20 trajectories,
95% intervals from a bootstrap over **whole trajectories** (M-27):

| h | r(step index, error) | r(disagreement, error) | partial r(disagreement, error · index) |
|---|---|---|---|
| 8 | +0.181 [+0.108, +0.349] | **+0.738 [+0.537, +0.807]** | +0.757 [+0.540, +0.822] |
| 32 | +0.174 [+0.131, +0.336] | **+0.735 [+0.577, +0.823]** | +0.756 [+0.604, +0.841] |
| 128 | +0.526 [+0.421, +0.643] | **+0.671 [+0.604, +0.846]** | +0.617 [+0.534, +0.812] |
| 368 | +0.269 [+0.106, +0.431] | **+0.605 [+0.545, +0.694]** | +0.596 [+0.526, +0.687] |

**Disagreement wins at every horizon tested, with non-overlapping intervals.** The index leads in
0 of 4.

**The partial correlation is what settles it.** Partialling the step index out of both variables
leaves disagreement at +0.596, against +0.605 raw — a change of
+0.010. Essentially none of what disagreement knows is a
re-encoding of how deep into the rollout you are. It carries information about *this* rollout.

**This was run expecting the opposite.** The brief that commissioned it named a null result as the
most valuable possible output and instructed that it lead the report. It is not a null. On this
axis **the follow-up's claim survives adversarial testing against a real baseline**, and this is
the only claim of either original paper that this reproduction strengthens rather than qualifies.

**It does not contradict R-61.** R-61 concerns per-dimension *sign counts* across 45 coupled
dimensions at small n; this concerns the aggregate *scalar* the method applies, with a cluster
bootstrap at n=20. The scalar is what `base.py:166` consumes. Both can
hold, and do: the quantity is a usable ranking signal and is not an interval.
**Evidence** `RUN` `results/task_d_nind20.json`;
`SRC` `robotic_world_model_lite/scripts/envs/base.py:166`.
**Status** CONFIRMED · **Relevance** CONTRIB


### R-64 — A per-horizon scalar restores calibration where a constant one cannot · `[RWM-U]` · **NEW**
R-59 showed one global multiplier on σ fails, and the paper then said a per-horizon or
input-dependent correction "might still work". That was a promissory note. This tests it.

One multiplier **per horizon**, fitted on one held-out episode and evaluated on the **other**, in
both directions, so no multiplier is ever scored on the episode that produced it. Target ±1σ
coverage 68.27%, tolerance
10 points.

| quantity | held-out cells calibrated, per-horizon c | same, constant c | range of fitted c |
|---|---|---|---|
| aleatoric | **10 / 10** | 2 / 10 | 592.6 – 7782 (13.1×) |
| epistemic | **10 / 10** | 2 / 10 | 5.082 – 47.33 (9.31×) |

**Every held-out cell lands within tolerance, for both quantities.** The constant scalar manages
2 of
10, and those are the h=1 cells it was fitted
at. The fitted multipliers span
9.31× across horizons on the
epistemic term, which is exactly why one number cannot serve.

**Two cautions, both stated in the paper.** The per-horizon scalar has five free parameters against
the constant one's one, so it must fit its own episode better; only the held-out column is
evidence, and only the held-out column is reported. And it is a calibration patch, not a fix — σ
carries no more information afterwards, it is merely rescaled by forecast depth. It is still enough
to make the interval mean what it says, and it costs one lookup table.

**This converts R-59 from a negative result into a bounded one:** the interval is broken as
shipped, and repairable without retraining.
**Evidence** `RUN` `results/task_d3_perhorizon.json`; `scripts/task_d3_perhorizon.py`.
**Status** CONFIRMED · **Relevance** CONTRIB


### R-65 — The penalty correlation, with the interval and the n it never had · `[RWM-U]` · **NEW**
R-58 reported the correlation between the applied scalar penalty and total absolute error as a bare
number with no interval and no sample size. It is the correlation of the exact quantity
`envs/base.py:166` applies with the error it is meant to track, so it carries more weight than any
other single number in that section and it was the least qualified.

**r = +0.605**, 95% CI
[+0.545, +0.694], n_independent = 20,
20 trajectories, 7,360 pooled trajectory-step points.

The interval resamples **whole trajectories**. Resampling trajectory-step pairs would narrow it by
about the square root of the rollout length and produce a spuriously tight figure — the error M-27
records.

The interval excludes zero comfortably and its lower bound
(+0.545) still exceeds the forecast-index baseline's point estimate
(+0.269), which is the comparison that matters (R-63).
**Evidence** `RUN` `results/task_d_nind20.json`.
**Status** CONFIRMED · **Relevance** CONTRIB



### M-35 — The committed PDF was not built by the build · **NEW**
`scripts/compile_paper.py` compiled `PAPER.tex` inside a temporary directory, read the page count
and the error list out of the log, reported PASS — and **deleted the PDF with the directory**. The
`PAPER.pdf` at the repository root was therefore whatever had last been copied there by hand.

It had gone stale by a wide margin. The committed file was **9 pages** against the current
document's 17, predated the anonymisation work, and its text layer contained the author's name,
surname and the repository host — every string the submission is required not to carry.

**Every anonymisation check passed throughout.** `scripts/submission_check.py` builds its own PDF
in a temp directory and greps that; it was correct about the document it built and blind to the
one in the tree. The defect was invisible to the check designed to catch exactly this, because
both used the same discarded-output pattern.

**Found by** Part F's check 2, which specifies grepping the built PDF *and* running metadata
extraction over the PDF and every figure — the figure sweep is what forced a scan of files on disk
rather than of a freshly built temp copy.

**Fix:** `compile_paper.py` now copies the PDF out to `PAPER.pdf` when the compile has no errors.
The rebuilt file is 17 pages, `/Author` empty, and contains none of the identifying strings in
either its text layer or its raw bytes.

**The rule:** a build artifact that is committed must be written by the build. If a check and the
artifact it certifies are produced by two different paths, the check certifies nothing.
**Evidence** `RUN` `scripts/compile_paper.py`, `results/compile_paper.json`.
**Status** CONFIRMED · **Relevance** METHOD


### M-36 — A derived count broke silently when the section it counted was renumbered · **NEW**
The abstract's "{n} defects in the released pipeline" was made indirect precisely so it could not
drift: `scripts/paper_numbers.py` counted the bold-numbered subsections rather than trusting a
typed figure. It counted them with the pattern `^\*\*5\.\d+ `.

Part A renumbered that section from 5 to 6. The pattern matched nothing, the count became **0**,
and the abstract read **"We also report 0 defects in the released pipeline"** — in a paper whose
§6 is titled "Defects in the released pipeline" and lists four.

**The no-hand-typed-numbers check could not see it**, because 0 is a legitimately generated value.
Nothing was typed; the generator was simply asking the wrong question.

**The lesson is narrower than "check your regexes".** Deriving a number from a *position* — a
section number, a row index, a line offset — is only as stable as that position. Bind it to
something that does not move. The counter now locates the section by its **title**, reads its
number from the heading, and asserts the count is non-zero, so the same renumbering produces the
right answer and any future mismatch fails the build instead of printing zero.

Found by the C1 claims audit, which prints each claim with its placeholders resolved. "0 defects"
is obvious on sight and invisible in a template.
**Evidence** `RUN` `scripts/paper_numbers.py`, `results/paper_numbers.json`.
**Status** CONFIRMED · **Relevance** METHOD


### M-37 — What the claims audit caught that the build checks could not · **NEW**
The build refuses to emit a paper with an unresolved placeholder, and every number is read from an
artifact. That guarantees the *numbers* are right. It says nothing about whether the *sentence
around them* is true. Reviewing all 158 claims with their placeholders resolved found
**eight assertions that were false or misleading while every number in them was correct**:

| the claim | why it was wrong |
|---|---|
| "we report **0** defects in the released pipeline" | M-36: the generator counted a section number that had moved |
| the aleatoric ratio in the abstract vs §5.2's table | the same quantity on two different arenas (n=4 and n=20), the first unlabelled — both correct, together a contradiction |
| "agrees in direction at **every** cell" | the aleatoric column flips sign at h=8 |
| "a better ranking than **any** aleatoric head here" | Arm B's aleatoric head has the higher mean correlation (+0.257 against +0.151) |
| "**every model** we measured orders its own errors better than chance" | the released checkpoint's aleatoric head ranks backwards on all 45 dimensions |
| "Figure 3(a) shows all 21 **trajectories**" | 21 is a count of runs |
| §11's overconfidence ratio | still the n=4 figure after the rest of the paper moved to n=20 |
| Appendix B's "roughly 22 hours" | E4: the true total is 32 hours; the figure predated six 10,000-iteration runs |

Five of the eight are **quantifier errors** — "every", "any", "all" — attached to a correct number.
No number-checking discipline catches those, because the number is not what is wrong.

**The mechanism that worked** was rendering every claim with its placeholders substituted and
reading them as a list, out of the flow of the prose. A false universal quantifier is obvious
beside the table that refutes it and invisible three paragraphs away from it.
**Evidence** `RUN` `results/task_c1_claims_audit.json`, `docs/CLAIMS_AUDIT.md`.
**Status** CONFIRMED · **Relevance** METHOD



### M-38 — Eight numbered figure references, and no numbered figures · **NEW**
The body refers to "Figure 1", "Figure 2", "Figure 3(a)", "Figure 3b", "Figure 4" and "Figure 5a"
in eight places. The Markdown-to-LaTeX converter emitted each figure as a bare
`\includegraphics` inside a `figure` environment and **discarded the alt text**. Without a
`\caption`, LaTeX assigns no number, so none of those eight references resolved to anything a
reader could find, and the figures arrived unlabelled and unexplained.

It survived every check because no check looked. The compile reported zero errors — a figure
without a caption is valid LaTeX. The cross-reference check (Part F, item 5) scans `§` references,
not `Figure` ones. And in `PAPER.md` the images render in order, so the Markdown reads correctly
while the PDF does not.

**Fix:** `build_paper.py` now carries a caption per figure and asserts that every figure it emits
has one, so adding a figure without a caption fails the build. `md_to_tex.py` converts the alt
text into `\caption{...}`. The rebuilt PDF numbers Figures 1–5 and all eight references resolve.

**The general form of M-35, M-36 and M-38 is the same:** each was a defect in the *presentation*
of correct data, in a project whose entire verification apparatus is pointed at whether the data
are correct. Checking that a number came from a file does not check that a reader can find the
figure it refers to, that the section it cites exists, or that the PDF on disk is the one the
check certified.
**Evidence** `RUN` `scripts/build_paper.py`, `scripts/md_to_tex.py`, `results/compile_paper.json`.
**Status** CONFIRMED · **Relevance** METHOD



### R-66 — The forecast-index control was too weak to be believed, so we strengthened it four ways · `[RWM-U]` · **NEW**
R-63's partial correlation regresses the forecast step index out of both variables **linearly**.
Error does not grow linearly with rollout depth. A control that under-fits the index leaves
index-driven variance in the residual and inflates what disagreement appears to contribute — and
R-63 is the one result in this paper that *strengthens* an original claim, so it is the one that
most deserves an attempt to break it.

Four stronger controls, same rollouts, n_independent = 20:

| control | what it removes | r(disagreement, error · index) |
|---|---|---|
| linear (R-63) | a straight-line trend in depth | +0.596 [+0.526, +0.688] |
| log | a logarithmic trend | +0.589 [+0.512, +0.688] |
| cubic | any degree-3 polynomial trend | +0.582 [+0.495, +0.676] |
| rank (Spearman) | **any monotone** dependence on depth | +0.906 [+0.856, +0.921] |
| **within-step** | **the index entirely, by construction** | **+0.739 [+0.711, +0.852]** |

**The within-step control settles it.** Correlating disagreement with error *across trajectories at
a fixed forecast step*, then averaging over steps, holds depth exactly constant — the index cannot
contribute anything, and no functional form for the index-error relationship has to be assumed. It
gives **+0.739**, positive at
**368 of 368** forecast steps, median +0.737.

The weakest figure across all 5 controls is +0.582, against a raw
+0.605. **The finding does not merely survive; the two strongest
controls raise it**, because removing the shared depth trend removes a source of common variance
that was diluting the association rather than creating it.

**What this closes.** The obvious objection to R-63 — "disagreement grows with depth, error grows
with depth, so of course they correlate" — is now excluded by measurement rather than by argument.
At a fixed depth, ensemble disagreement still identifies which rollouts are going wrong.
**Evidence** `RUN` `results/task_d2b_robustness.json`; `scripts/task_d2b_robustness.py`.
**Status** CONFIRMED · **Relevance** CONTRIB



### M-39 — The anonymisation checker de-anonymised the submission · **NEW**
`scripts/part_f_gate.py` was written to satisfy Part F's check 2: grep the built PDF and every
figure for the author's name and repository URL. To do that it held the strings to search for as
literals:

```
IDENT = ["<given name>", ..., "/Users/<given name><surname>"]
REPO  = "github.com/<given name>-<surname>"
```
(elided here for the same reason — this ledger ships in the archive too, and quoting
the literals verbatim in the entry that describes them would reintroduce them a third
time. The archive builder caught that as well.)

**That script ships inside `supplementary.zip`.** A checker for identifying strings had become the
only file in the archive that contained one — and it contained the full set.

Then, once the literals were split into fragments, its **output** leaked them again: the check-4
detail line reported the absolute path of the file it had read, and an absolute path on this
machine contains the home directory, which contains the author's name. That string was written
into `results/part_f_gate.json`, which also ships in the archive.

Both were caught by `scripts/build_supplementary.py`, which scans every candidate file before
writing the zip and refuses to write one that carries an identifying string. It rejected the
archive twice in a row and named the offending file and pattern each time.

**Fixes:** the search strings are assembled from fragments at import, with a comment saying why
they must not be written out; and the gate reports `os.path.basename(vp)` plus a description of
which tree it read, never an absolute path.

**What this says about the check that caught it.** Part F item 2 as specified — grep the *built
PDF* and the *figures* — would never have found either of these, because neither is in the PDF or
a figure. The archive scanner found them because it scans **everything that leaves the machine**,
which is the right unit. Anonymisation is a property of the artifact set that is transmitted, not
of the document.

Compare M-35: the same shape again. A check that inspects a narrower object than the one actually
shipped certifies the wrong thing.
**Evidence** `RUN` `scripts/build_supplementary.py`, `scripts/part_f_gate.py`.
**Status** CONFIRMED · **Relevance** METHOD



### M-40 — Four new measurements, none of them in the pipeline that claims to regenerate everything · **NEW**
Parts B and D added four measurement scripts — `task_b_permutation.py`, `task_d_nind20.py`,
`task_d2b_robustness.py`, `task_d3_perhorizon.py` — whose outputs the paper quotes throughout §5.2,
§5.5, §5.6 and §5.7. **None of them was added to `reproduce.sh`.**

Nothing failed. Every artifact existed, every number resolved, the paper built, and the
reproducibility figure in §8 stayed green.

**Why that is worse than an ordinary omission.** A clean clone of this repository *already
contains* `results/`. `verify_reproduction.py` handles that by partitioning on
the run's `_regenerated.txt` manifest — files a run actually rewrote are compared as regenerated, files
carried in by the clone are held out and counted separately. A script that is not in
`reproduce.sh` never appears in `_regenerated.txt`, so its outputs fall silently into the
carried-in partition. The paper's newest and most consequential results would have been excluded
from the reproducibility claim **without the claim changing at all** — the figure would still read
"N files, 0 differing", over a set that no longer contained them.

This is M-28's trap approached from the other side. M-28 was carried-in files being *counted* as
regenerated, which inflated the figure. This is regenerable files being *silently dropped* from
it, which does not move the figure at all and is therefore harder to see.

**Fix:** stages 20d–20g run the four scripts before stage 23 collects the paper's numbers, and
stage 29a runs the Part F gate. Only 20d carries `NEEDS_WEIGHTS`: it is the only one that loads
`runs/`. The other three need the released checkpoint alone, which `setup.sh` fetches, so they run
in a clean clone and their values count toward the regenerated set. Marking all four
`NEEDS_WEIGHTS` — the lazy choice — would have skipped three working stages and understated
reproducibility instead.

**The rule:** a script whose output the paper cites belongs in `reproduce.sh` in the same change
that writes the script. The check that would have caught this does not exist yet; the nearest
approximation is that every `results/*.json` a paper number cites should be declared by some stage,
and `paper_numbers.py` already knows the full list of artifacts it reads.
**Evidence** `RUN` `reproduce.sh`, `scripts/verify_reproduction.py`.
**Status** CONFIRMED · **Relevance** METHOD



### M-41 — What the clean clone found that the working tree could not · **NEW**
Part F's check 4 is the only check in this project that runs the code somewhere the author's
machine state cannot help it. Run properly — clone at a commit, `./reproduce.sh --quick --force`,
compare against **that commit's** `results/`, not the working tree — it found two things nothing
else could.

**1. A clean clone built a paper that said "Across 0 runs the collapse is linear."**
`n_runs` was counted from a listing of `runs/`. `runs/` is gitignored. In the working tree the
directory is full and the count is 21; in a clone it is empty and the count is **0**, and the
sentence built cleanly around it. No placeholder was unresolved, no assertion fired, the paper
compiled, and every gate passed — on a machine where the directory happened to exist.

This is the third instance of one bug. `n_defects` counted a section number that moved (M-36);
`n_runs` counted a directory that is not shipped. In both cases the *derivation* succeeded and
returned a wrong answer, which no number-provenance discipline detects, because the number does
have a provenance — it is just the wrong one. **The rule that follows: a derived count must be
read from something the repository actually contains.** `n_runs` now counts
`results/step5_arm*.json`, which is committed, and asserts the list is non-empty.

**2. One artifact does not reproduce, for a reason worth stating rather than suppressing.**
`step4_4_overfit_ens1.json` stops on a wall-clock budget of 2,700 seconds rather than at
its 2,000-iteration cap. It reached
451 iterations on the machine that produced the committed copy and 514 on the one that
regenerated it, so its iteration count and every terminal loss below it differ.

**The tempting fix is wrong.** Adding `step4_4_overfit_*.json` to the excluded-files list would
also have dropped `step4_4_overfit_b32lr1e3.json` — the sibling the paper actually cites, which
was given a 100,000-second budget, reached its cap at 2,001 iterations, and reproduces **bitwise**.
Excluding by filename would have silently removed a reproducible result to hide an irreproducible
one. The verifier now decides from the artifact instead: a run whose `iterations_run` is below its
own `config.iters` was time-bounded, and only that run is excluded.

**Result after both fixes:** 27 files regenerated,
**5,928 values, 5,928 bitwise identical (100.00%), 0
differing, 0 deletions**, with 3,972 timing fields, 584
values of the CPU-budget file and one wall-clock-bounded diagnostic excluded and named.

**Why the count rose from 19 to 27:** M-40 added the four Part B and D
scripts to `reproduce.sh`, three of which run in a clean clone.
**Evidence** `RUN` `results/verify_reproduction.json`, `scripts/verify_reproduction.py`,
`scripts/paper_numbers.py`.
**Status** CONFIRMED · **Relevance** METHOD



### X-11 — What the original papers report for the claims we tested: nothing quantitative · **NEW**
A reproduction that reports 4.61× without saying what the authors reported leaves a reader
unable to place it. So, for every claim §3's table marks as tested, this records the figure the
original gives.

**All 4 are stated with no quantitative figure at all.**

| claim | where (v1) | what the original gives |
|---|---|---|
| RWM-AR consistently outperforms RWM-TF | 2501.10100v1 IV-D (Generality across Robotic Environments) | qualitative; shown in Figure 4 |
| Teacher forcing gives "poor autoregressive performance" | 2501.10100v1 IV-C (Dual-autoregressive Mechanism) | qualitative |
| Epistemic uncertainty "closely follows the trend of the prediction err | 2504.16680v1 5.1 | qualitative; shown in Figure 2 (right) |
| Aleatoric uncertainty "remains low, reflecting small stochasticity" | 2504.16680v1 5.1 | qualitative; shown in Figure 2 (right) |

Each is asserted qualitatively and shown in a plot. None is given a number in running text, in a
caption, or in a table.

**What follows for this paper.** Our 4.61× for the autoregressive-versus-teacher-forcing gap
neither confirms nor contradicts a published figure, because there is no published figure. It is
the first number attached to the claim. The same holds for the follow-up's "strong correlation"
between ensemble disagreement and prediction error: the phrase appears with no coefficient, no
interval and no sample size, and R-63's +0.605  at n_independent = 20 appears to be the
first coefficient anyone has attached to it.

**Where a magnitude is legible only from a plotted curve we say so** rather than estimating it
from the axis. Figure 4 of 2501.10100 plots the AR-versus-TF gap across environments and the
magnitude could be eyeballed; we decline to, because an eyeballed value would be indistinguishable
in the text from a value the authors stated.

**One table of numbers exists in either paper** — Table I of 2501.10100, on sample efficiency:
6M state transitions against
250M at equal real tracking reward
(0.90 +- 0.04 against
0.90 +- 0.03). We did not test it — it needs
policy learning and hardware — and the table now cites it rather than leaving the cell empty.

**A versioning note that affects every section reference in this paper.** Our references use
**v1** (17 Jan 2025), which uses Roman-numeral sectioning. **v2** (23 Apr 2025) renumbered to
Arabic and moved IV-C's material into Appendix A.4.1, so a reader who opens the current arXiv
version will not find a §IV-C at all. Both locations are recorded per claim. The references were
correct when written and are correct for the version named; they were one arXiv revision away
from being unresolvable, which is worth a sentence in any paper that cites section numbers.
**Evidence** `EXT` arXiv:2501.10100v1 §IV-C, §IV-D, Table I; arXiv:2501.10100v2 §4.3, §A.4.1;
arXiv:2504.16680v1 §5.1, Figs. 2-3, read 2026-08-22;
`RUN` `results/original_paper_figures.json`.
**Status** CONFIRMED · **Relevance** CONTEXT



### M-42 — The numeral check could not see any of the six interpretive defects · **NEW**
Every generated numeral in this paper was correct. A review that traced each one back to
`results/` found no defect in any of them. **Six defects were found anyway**, all in hand-written
sentences that interpret those numerals:

| defect | the numerals were | the sentence said |
|---|---|---|
| A1 | 0/45 all-episodes, 20/45 out-of-sample | asserted one arena while the table printed the other, naming neither |
| A2 | two correct CIs | "the intervals do not overlap" — at h=128 they do, across 0.604-0.643 |
| A3 | 0.60534 and 0.59571 | "a change of **+**0.010" — the change is negative |
| A4 | every coverage figure correct | named the third-largest deviation as the largest |
| A5 | 20,668.6 and 34.45 | "two orders of magnitude" in §12, "nearly three" in the abstract, of the same ratio |
| A6 | our 4.61x correct | implied a comparison with an original figure that does not exist |

**The pattern.** `build_paper.py` asserts that every printed number came from a named artifact.
That is a guarantee about *provenance*, and it is silent about *relations between* provenanced
numbers. "Do not overlap", "backwards", "the worst is" and "orders of magnitude" are not numerals
and appear nowhere in `results/paper_numbers.json`; they were typed, and five of the six were
wrong.

**The fix is a second checker, not a stricter first one.**
`scripts/check_comparative_claims.py` verifies 19 comparative claims across 7 kinds — interval
overlap, extremum identification, the sign of a stated change, orders-of-magnitude
descriptions, the arena and horizon a count came from, a stated ordering between two
scalars, and a stated ratio of relative variabilities. Each entry pins two things and requires both:

- a **fragment of the paper's own text**, so rewording the sentence fails the check rather than
  silently detaching it from the claim it was written to guard; and
- a **relation recomputed from the artifacts**.

A check that only re-asserts an artifact fact guards nothing, and a check that only matches text
guards nothing either. Demonstrated: rewording "the marginal intervals *do* overlap" to "are not
disjoint" — same meaning — fails C1.1.

**Every assertion is run against a deliberately corrupted expectation on each build** and must
fail: the interval relation inverted, the extremum replaced by the **runner-up** rather than an
absent label, the sign flipped, the order of magnitude and the dimension counts moved by one.
18 of 18 corruptions are caught.

**The self-test found its own bug first.** Its first version applied a fixed corruption per kind —
`expect: "disjoint"` to every overlap check, `expect: "rise"` to every sign check. For claims that
already expected those, the corruption was a no-op, and two of eleven assertions reported as
MISSED. They were not missed; nothing had been corrupted. The corruption now inverts relative to
each claim's own expectation. A later extension hit the same class again: a label
helper prefixed "h=" to family keys that were already free-form model names, so two checks failed on
extrema that were in fact correct. Both were checker bugs, not paper defects, and both surfaced
because the checks were run rather than assumed. **An assertion that has quietly stopped being able to fail is worth
less than no assertion**, because it reads as coverage, and this is the mechanism that finds out.

One check has nothing to corrupt: A5's ratio is now quoted as 600x directly rather than as a count
of orders, which is why the self-test marks it n/a. That is the stronger fix — an exact generated
ratio cannot drift out of agreement with itself the way two prose descriptions of it did.
**Evidence** `RUN` `results/comparative_claims.json`; `scripts/check_comparative_claims.py`.
**Status** CONFIRMED · **Relevance** METHOD



### M-43 — PRE-REGISTERED decision rule for the ensemble-5 replication · **NEW**
*The brief commissioning this work labelled it M-24. That identifier was allocated in this ledger
on 2026-08-14 to a different finding and claim IDs here are permanent, so it is entered as M-43.
Nothing else about the rule is changed.*

**Entered before any ensemble-5 result exists.** No `runs/armA_seed*_ens5` directory existed when
this was committed; the commit containing it precedes the launch of the runs it governs, and that
ordering is checkable from `git log` exactly as M-16's and M-23's are.

**Why the rule is needed.** §11 concedes that our own arms run at ensemble size 1, where the
epistemic term is identically zero by construction, so **every epistemic measurement in this paper
is made on a single released checkpoint.** §5.6 — the one finding here that *strengthens* an
original claim — rests entirely on that one artifact. A property of the method and a property of
one checkpoint are currently indistinguishable.

**Governing measurement.** On the ensemble-5 Arm A checkpoints at 2,500 iterations: the
correlation between ensemble disagreement and realised absolute error, against the forecast step
index, over independent trajectories in the out-of-sample arena, using the paired-difference
bootstrap of §5.6.

**§5.6's finding GENERALISES beyond the released checkpoint** if disagreement leads the index at
every horizon tested **and** the paired difference excludes zero at a majority of them.

**It DOES NOT generalise** if the index leads at any horizon, **or** the paired difference spans
zero at a majority of them.

**Reported alongside, not governing:** whether the aleatoric collapse rate matches the ens1 runs;
whether epistemic is input-dependent and horizon-flat as it is in the released checkpoint; the
calibration ratio at each horizon; and the ens1-versus-ens5 comparison on prediction accuracy.

**Our expectation, recorded as an expectation only.** We expect the replication to succeed. That
is a belief, not a pre-registration, and it carries none of the weight one does — the same
distinction §5.6 draws about its own forecast-index baseline, and the one S-12 was written to
retract when this project failed to observe it. The rule above is what governs; the expectation
is recorded so that a reader can see it was held in advance and can judge accordingly if the
result agrees with it.
**Outcome: DOES NOT GENERALISE.** The runs were launched after this entry reached git and the rule was applied by code, exactly as written. R-67 reports the result and the power the rule turned out to have.
**Evidence** `RUN` `results/task_d3_ens5.json`.
**Status** PRE-REGISTERED, DISCHARGED · **Relevance** METHOD


### R-67 — The ensemble-5 replication: the direction holds, the pre-registered rule does not · `[RWM-U]` · **NEW**
**Retracts nothing; it bounds R-63.** Three Arm A arms at ensemble size 5, seeds 0/1/2, 2,500
iterations, every other setting identical to the ens1 arms. Governed by M-43, committed before
the runs existed.

**M-43 returns DOES NOT GENERALISE.**

| condition | result |
|---|---|
| disagreement leads the index at every horizon tested | **TRUE** — 12 of 12 seed-horizon cells |
| paired difference excludes zero at a majority | **FALSE** — 1 of 4 |

The rule is applied per seed: a horizon counts as leading only if disagreement leads in all three
seeds, and as excluding zero only if the interval excludes zero in all three. That is stricter
than pooling and cannot be carried by one favourable seed.

**The two conditions diverge, and the reason is measurable.** Every paired point estimate is
positive, +0.204 to +0.545.
What fails is separation on 4 independent trajectories — the held-out
pair is the only genuine out-of-sample arena our own arms have, where R-63's finding was measured
at 20.

**The power the rule actually had.** Subsampling 4 trajectories at a
time from a 20-trajectory pool, M-43's criterion fires on 75% of
draws on average and on only 24% at h=8. **That is an
upper bound**: the pool is in-sample for these arms, where the effect is
+0.425 to +0.790 against
+0.204 to +0.545 on the
held-out pair. So the rule was under-powered where it was applied, decisively at one horizon.
**We do not claim it could not have passed** — at three of four horizons it had 85-96% power
against the in-sample effect — only that it was committed without anyone checking what it could
detect at n=4.

**That is the same failure M-24 records**, committed by the same project that wrote M-24 down: a
pre-registered rule anchored without regard to the regime it would be applied in. M-24's version
anchored to the wrong horizon; this one to a sample size whose power nobody computed.

**Companion, in-sample, non-governing.** On all ten episodes (n_independent =
20, of which eight are training data for these arms) the same
measurement excludes zero at 4 of
4 horizons and would have satisfied both conditions. It
cannot discharge M-43 and is recorded only so the comparison with R-63's arena is like for like.

**The four non-governing measurements, all confirmatory:**

| measurement | ens5 | reference |
|---|---|---|
| epistemic err/σ at h=368 | 13.0× | released checkpoint 34.4× |
| ±1σ coverage at h=368 | 6.30% | calibrated 68.3% |
| aleatoric collapse rate | -9.3526e-05 | ens1 -9.3617e-05, +0.10% |
| epistemic CoV across batch | 0.379–0.395 | released checkpoint 0.0177 |

Our arms are **better calibrated than the released checkpoint and fail the same way**, their
collapse rate is unchanged by ensemble size as the objective predicts, and their epistemic term is
far more input-dependent than any aleatoric head measured here. Prediction accuracy at ensemble 5
is better at h=8 (0.878× the error) and marginally
worse at h=368 (1.044×).

**What this settles and what it leaves open.** R-63 is established on the released checkpoint and
**supported but not established** on a model we trained. The distinction is the whole point of
running these arms, and reporting the rule's verdict rather than the direction it points is the
only way the distinction survives.
**Evidence** `RUN` `results/task_d3_ens5.json`, `results/task_d3b_ens5_power.json`;
`scripts/task_d3_ens5.py`, `scripts/task_d3b_ens5_power.py`.
**Status** CONFIRMED · **Relevance** CONTRIB

### S-15 — The binomial P-values attached to every dimension count · **NEW**
**Retracts** — a shared inference, not a numbered claim; the counts it was computed from all stand
**What is retracted:** the step from a sign count to a P-value under a fair-coin binomial null,
wherever it appears — R-53's table, R-57's last column, R-58's per-horizon table and claims-table
row, and the abstract, §5.2, §5.4, §5.5, §9 and §12 of the paper. Specifically the values
5.42e-07 for 39/45 and 5.68e-14 for 45/45.

**Why it is wrong:** the 45 state dimensions are physically coupled, and error and σ share a
forecast-depth trend that produces positive correlations under re-pairing. R-61 gives the
dependence-preserving replacement and shows the true null mean reaching
43.8 of 45 where the binomial
assumed 22.5.

**What is not retracted:** the counts themselves. 39/45, 45/45, 21/45, 23/45 are all reproduced
exactly by the permutation code on the cells the two share. Nor is any magnitude result affected —
the overconfidence ratios and coverage figures never used this null.

**Who found it:** the submission-hardening review, before submission and before any reviewer saw
it. **Superseded by** R-61.
**Evidence** `RUN` `results/task_b_permutation.json`.
**Status** RETRACTED · **Relevance** METHOD


### M-34 — The permutation test's first implementation was numerically wrong, and the existing pipeline caught it · **NEW**
The permutation numerator was first written in the raw cross-product form,
`<σ, err> − N · mean(σ) · mean(err)`, in float32 — the textbook catastrophic-cancellation shape.
For a dimension whose true correlation is near zero the two terms agree to about seven significant
figures and their difference is rounding noise.

It flipped exactly one dimension. The corrected (nll) arm at h=368 came out **20 of 45** where
`results/task1_calibration.json` had long said **21 of 45**.

**The disagreement was one dimension out of 45, in the least interesting model in the table, on a
cell whose P-value is 1.0 either way.** It changed no conclusion. It was caught only because the
counts were cross-checked against the two artifacts that already contained them, cell by cell,
instead of being accepted as new measurements of a new statistic.

**The fix** centres σ and error once, in float64, before forming the cross-product. Re-pairing
trajectories leaves both marginal means unchanged, so the centred cross-product *is* the
covariance numerator for every permutation, with no subtraction and therefore no cancellation. All
nine shared cells then agreed exactly.

**The rule this earns:** a new statistic that overlaps an existing artifact must be made to
reproduce it on the overlap before its novel cells are believed. The overlap is free validation
and this project has now twice found real defects in it (compare S-11).
**Evidence** `RUN` `results/task_b_permutation.json`, `results/task1_calibration.json`;
`scripts/task_b_permutation.py`.
**Status** CONFIRMED · **Relevance** METHOD


### M-44 — PRE-REGISTERED decision rule for the trunk-sharing mechanism · **NEW**

**Entered before any independent-init ensemble exists.** No `runs/armA_seed3` or `runs/armA_seed4`
directory existed when this was committed, and no scoring of an independently-initialised ensemble
had been run. The commit containing this entry precedes both, and the ordering is checkable from
`git log` exactly as M-16's, M-23's and M-43's are.

**Why the rule is needed.** §5.3 explains why the *aleatoric* head collapses and then says outright
that the mechanism behind the *epistemic* miscalibration "is not established here". X-12 now
supplies a candidate from source: the released five-member ensemble is not five models. One GRU
trunk of 636,672 parameters is shared by all five, and each member owns only a 77,492-parameter
output head — **89.15% of every member's state-prediction pathway is numerically identical to every
other member's**, and in an autoregressive rollout the members share a single recurrent hidden-state
trajectory, because the ensemble *mean* is what gets fed back. Member disagreement is therefore head
disagreement over identical features. Members that share a feature extractor have correlated errors
by construction and their spread understates epistemic uncertainty. That is a mechanism structurally
symmetric to §5.3's, and it is either the explanation or it is not.

**Governing measurement.** Arm A at seeds 0–4, ensemble size 1, 2,500 iterations, clean dataset,
identical in every other setting, **scored together as a five-member ensemble at evaluation time** —
the epistemic term being the standard deviation across the five models' mean predictions. Compared
against the shared-trunk `armA_seed{0,1,2}_ens5` arms on the **same** out-of-sample trajectories,
through the **same** harness, at **h = 100**, the method's own imagination rollout length
(`results/v2_deployment_horizon.json`). Two quantities:

- the **overconfidence factor**, mean |error| / mean σ_epistemic;
- **coverage at ±1σ**.

Both with a cluster bootstrap over whole trajectories (M-27), n_independent = 4.

**The mechanism is SUPPORTED** if the independent ensemble's overconfidence factor is lower than the
shared-trunk arms' by at least the minimum detectable effect **and** the 95% paired interval on the
log ratio excludes zero, **and** its ±1σ coverage is higher by at least the minimum detectable
effect with its paired interval excluding zero.

**The mechanism is NOT SUPPORTED** if the independent ensemble is not materially better calibrated —
that is, if either paired interval spans zero, or the point estimates move by less than the minimum
detectable effect. Explicitly, and stated as a condition rather than as an outcome: *if the
independent ensemble is not materially better calibrated, the mechanism is not supported and the
paper says so.*

**The result is UNRESOLVABLE** if the two quantities disagree in direction — overconfidence improves
while coverage worsens, or the reverse — in which case the paper reports both and claims neither.

**What this rule can and cannot settle, measured before it was tested.** `results/p1_power_check.json`
estimates the minimum detectable effect at the n_independent = 4 this rule actually faces, by cluster
bootstrap over the held-out pair, calibrated two ways. Against same-architecture seed pairs, which
differ only in seed and cancel almost all between-trajectory variation, the MDE is 1.05× on the
overconfidence ratio and 0.72 coverage points — optimistic. Against cross-architecture pairs, which
is the kind of contrast this rule makes, the MDE is **1.45× on the overconfidence ratio and 2.26
coverage points**, and those are the figures this rule is written against. So:

- an improvement of **1.45× or more** in the overconfidence factor is detectable here;
- an improvement smaller than that is **not**, and this rule cannot settle it either way;
- at n_independent = 4 the bootstrap has 4⁴ = 256 distinct resamples, so every interval is quantised
  at that resolution, exactly as §4 already states for the A/B interval.

This is the check M-43 was committed without, and M-24 before it. It is recorded here so that a
result near the threshold is read as near the threshold rather than as a finding.

**A limitation of the design, stated in advance and repeated in §11.** Independently-seeded runs
differ in **both** initialisation and data ordering, whereas the shared-trunk heads differ only in
head initialisation. The comparison therefore conflates trunk-sharing with data-order diversity and
**bounds** the effect rather than isolating it. If the overconfidence factor barely moves despite
that generous handicap, the finding is strong in the direction of "architecture is not the
explanation". If it moves a lot, the design flaw is identified but not cleanly attributed. Whichever
the data gives is what gets written.

**Our expectation, recorded as an expectation only.** We expect the independent ensemble to be better
calibrated but not calibrated — a partial mechanism rather than the whole one. That is a belief, not
a pre-registration, and it carries none of the weight one does; the same distinction §5.6 draws about
its own forecast-index baseline and the one S-12 exists to retract.

**Outcome: MECHANISM SUPPORTED.** The runs were launched after this entry reached git and the
rule was applied by code, exactly as written. All six conditions hold against all three
shared-trunk seeds. R-68 reports the result, including the decomposition that keeps it from being
overstated.
**Evidence** `RUN` `results/r2_independent_ensemble.json`.
Power: `results/p1_power_check.json`. Mechanism: `results/v1_ensemble_topology.json`.
**Status** PRE-REGISTERED, DISCHARGED · **Relevance** METHOD

> **Addendum, 2026-08-28 — not part of the pre-registered text, and deliberately below it.**
> A third respect in which the two arms differ was found after this rule was discharged:
> **capacity**. The independent arm carries 3,570,820 state-pathway parameters against the
> shared-trunk arm's 1,024,132, a factor of 3.49, because each member brings its own trunk
> (**X-17**). The rule's text above is unchanged and its verdict is unaffected — the rule was
> committed before the runs and states its own limitation on two axes; this is a third, found
> afterwards, and writing it into the rule would make a pre-registration say something it did not
> say. §12 names all three. This addendum is a pointer, not an amendment, which is why it is
> quoted rather than inlined.


### M-45 — PRE-REGISTERED decision rule for the within-trajectory control on §5.6 · **NEW**

**Entered before the statistic was computed.** No `results/a2_trajectory_level_control.json` existed
when this was committed, and the double-demeaned correlation had not been evaluated. The ordering is
checkable from `git log`.

**Why the rule is needed.** §5.6 controls for the forecast-index confound five ways and that is the
strongest part of this paper. Every one of those controls removes **depth**. **None removes
trajectory difficulty.** Per-episode difficulty in this dataset spans 0.601 to 1.674 (D-12) and is
uncorrelated with commanded speed, so the units being correlated differ a great deal in level. Harder
trajectories plausibly have both larger realised error and larger disagreement, which would produce
the observed correlation with disagreement carrying no within-rollout information at all. Two
symptoms point at exactly this: r = +0.994 at h=1 on twenty points is not the shape of a genuine
per-step signal, and the within-step figure (+0.739) being *higher* than the pooled one (+0.605) is
the signature of a between-unit effect.

**Governing statistic.** On the pooled (trajectory, step) panel from the released checkpoint over all
ten episodes, n_independent = 20: subtract **both** the trajectory mean and the step mean from each of
disagreement and |error| — a two-way additive removal — and correlate the residuals. Call it r_dd.
95% interval from a cluster bootstrap over whole trajectories. This asks the only question that
matters for a practitioner mid-rollout: *at a given depth, in a given rollout, does disagreement
know?*

**Disagreement CARRIES WITHIN-ROLLOUT INFORMATION** if r_dd is positive and its 95% cluster-bootstrap
interval excludes zero.

**Disagreement is LARGELY REPORTING WHICH EPISODE IS HARD** if r_dd's interval includes zero, or r_dd
is negative.

**What the paper says under each outcome — pre-written here so there is nothing to negotiate later.**

*Under the supporting branch:* §5.6 keeps its current strength and gains a sixth control, the only
one that removes trajectory difficulty rather than depth. §12 leans on this one rather than on the
within-step figure. The sentence is: *with both the rollout and the depth held constant,
disagreement still tracks error, so it is not merely reporting which episode is hard.*

*Under the non-supporting branch:* the honest sentence is that **disagreement mostly identifies which
rollouts will go wrong rather than when within a rollout**. That is still a usable ranking signal for
a practitioner choosing between candidate trajectories, and it is materially weaker than the claim
§5.6, §9 and §12 currently make. §9's "very nearly a perfect ranking" for the h=1 figure goes, and
§12's sentence is rewritten to the between-rollout form. The abstract's ranking claim is qualified to
"between rollouts".

**Reported alongside, not governing:** the variance decomposition of the pooled +0.605 into
between-trajectory and within-trajectory components; the partial correlation controlling for
per-trajectory mean |error| at each horizon; and the h=1 diagnostic, in which disagreement is
correlated against commanded speed and against per-episode difficulty (D-12) and each is partialled
out of the disagreement–error correlation. If the h=1 figure of +0.994 collapses under that, it is
reported as collapsing.

**What this rule can and cannot settle, measured before it was tested.**
`results/p1_power_check.json` estimates the minimum detectable effect at the n_independent = 20 this
rule faces. The cluster-bootstrap standard error of r_dd gives an MDE of **|r_dd| ≥ 0.183** at 80%
power, two-sided α = .05. A dilution study — replacing disagreement by a weighted mix of itself and a
within-step permutation of itself, which preserves the depth profile and every marginal and destroys
only the pairing — puts the detection threshold between a true r_dd of 0.086 (not detected) and 0.172
(detected), consistent with that MDE. So:

- an effect of **|r_dd| ≥ 0.183** is detectable here;
- an effect below about 0.1 is **not**, and a null result at that magnitude would be an
  under-powered null rather than evidence of absence — the paper says so if it lands there;
- the same statistic at n_independent = 4 would have an MDE of 0.444, which is why this rule is
  stated over the released checkpoint's twenty trajectories and not over our own arms' four.

**Our expectation, recorded as an expectation only.** We expect r_dd to be positive and materially
smaller than the pooled +0.605, because some of the pooled correlation is certainly between-trajectory.
That is a belief and not a pre-registration.

**Outcome: DISAGREEMENT CARRIES WITHIN-ROLLOUT INFORMATION.** r_dd = +0.419
[+0.318, +0.576] at n_independent = 20, comfortably above the rule's own MDE of 0.183. The
supporting branch applies and 6.7 keeps its strength. R-69 reports the result, and the part the
rule did not anticipate: the control it replaces was itself a between-trajectory statistic.
**Evidence** `RUN` `results/a2_trajectory_level_control.json`.
Power: `results/p1_power_check.json`.
**Status** PRE-REGISTERED, DISCHARGED · **Relevance** METHOD


### X-12 — The five ensemble members share a trunk, a hidden state, and 89% of their parameters · **NEW**

Established from pinned upstream source, from the released checkpoint's tensors, and from our own
ensemble-5 arms. Nothing here is trained and nothing is inferred.

**The construction.** `system_dynamics.py:34` builds **one** `state_base`. `system_dynamics.py:35-41`
replicates the *heads* `ensemble_size` times, and only the heads. `system_dynamics.py:44` does the
same for the auxiliary pathway. In the forward pass `system_dynamics.py:87` evaluates the trunk
**once** and `:90` hands the identical feature vector to every head. `system_dynamics.py:126` then
computes the epistemic term as the standard deviation *across those heads*.

**The counts, from `assets/models/pretrain_rnn_ens.pt`.** The state pathway is a 636,672-parameter
two-layer GRU trunk plus five 77,492-parameter heads. Per member, 636,672 of 714,164 parameters —
**89.15%** — are numerically identical to every other member's. Across the whole object, both trunks
together are 1,273,344 of 1,995,569 parameters, 63.81%.

**The stronger form, which is not about parameter counts.** The trunk owns a single recurrent hidden
state (`rnn.py:40`), and an autoregressive rollout feeds the ensemble **mean** back into it
(`system_dynamics.py:115`, and `src/rwm_model.py:223` in our reimplementation). So the five members
do not roll out independently at all: there is one hidden-state trajectory, and disagreement at step
t is the spread of five 256→128→45 MLPs read off one 256-vector. The members cannot express
uncertainty the shared trunk does not already carry.

**Our own ens5 arms are identical in this respect** — `src/rwm_model.py:164-167, 182, 185, 200` —
with the same 636,672 / 77,492 split and the same 1,995,569 total. §5.2's "our arms fail the same way"
is therefore a comparison of like with like, not an assumption.

**Status of the mechanism claim.** This is a *candidate* explanation for the epistemic
miscalibration §5.3 leaves unexplained, established structurally. Whether it is *the* explanation is
what M-44 tests. The two are kept separate deliberately: the topology is a fact, the mechanism is a
hypothesis about that fact.
**Evidence** `SRC` `results/v1_ensemble_topology.json`; `scripts/v1_ensemble_topology.py`.
**Status** CONFIRMED · **Relevance** CONTRIB


### X-13 — h=368 is the upstream's open-loop diagnostic length, not a deployment horizon · **NEW**

The paper calls h=368 "the deployment horizon" and puts the numbers measured there in the abstract.
Nothing defended the label, and it is wrong in both directions.

**Where 368 comes from.** `base_cfg.py:46` sets `len_eval_trajectory = 400`; `mbpo_ppo.py:61` carries
the same 400; `mbpo_ppo.py:284` starts the autoregressive forecast *after* the `history_horizon = 32`
teacher-forced prefix (`anymal_d_flat_cfg.py:68`). 400 − 32 = 368. It is the length of the upstream's
own **open-loop diagnostic** — the curve the follow-up plots as its uncertainty figure — and our
h=368 inherits it because our harness reproduces that evaluation.

**What the method actually rolls out over.** 100 steps. arXiv:2504.16680 Table S9 (v1) / Table S11
(v3) gives "imagination steps per iteration = 100", unchanged between versions, and v3 adds the same
figure in prose: "propagate and manage uncertainty over 100-step episodic rollouts". The shipped
`lite` release instead caps an imagined episode at 256 (`base_cfg.py:20`, enforced at
`envs/base.py:174`) and collects 24 steps per iteration (`base_cfg.py:147`); those are the reduced
release's defaults and the published table governs. Neither is 368.

**The consequence.** h=368 is 3.68× the method's own rollout length. h=100 is added to the evaluation
grid — the per-step curves already ran to 368, so measuring the method's own horizon exactly costs a
cumulative mean — and the headline re-anchors there. Every h=368 row is kept and relabelled as the
open-loop diagnostic horizon.

**An observation about the original, not a defect.** The follow-up's uncertainty evidence is itself
gathered at the 368-step diagnostic horizon, 3.68× the one its method deploys at. A diagnostic may
legitimately run past the deployment horizon. What it means for us is that our h=368 is comparable to
the original's *figure* and our h=100 is comparable to the original's *method*, and the paper now
says which is which.
**Evidence** `SRC` `results/v2_deployment_horizon.json`; `scripts/v2_deployment_horizon.py`.
**Status** CONFIRMED · **Relevance** CONTRIB


### X-14 — The metrics were never defined, in a paper whose metrics have twice changed a verdict · **NEW**

The paper reported "normalised error 0.3582" and never defined the metric; it named relative-L1 and
nRMSE and gave the formula for neither; "coverage" was never defined operationally. In this project
specifically that is not a presentational gap. Two metrics here disagree in **direction** at h=1
(R-20), and the choice between pooling-before-dividing and dividing-before-pooling once **inverted**
a comparison against the released model (R-27, M-19, R-29). A reader who cannot see the denominator
cannot check the headline and cannot tell which aggregation produced it.

`results/v3_metric_definitions.json` now carries, for each of relative-L1, nRMSE form 1 (the primary
pooled aggregation), nRMSE form 2 (retained only for continuity), the overconfidence factor and
coverage: the formula as LaTeX, the implementation's `file:line` read back and fingerprinted, the
denominator and where its constants come from, and — for coverage — the pooling axes in order and the
nominal it is judged against. Twenty implementation citations are verified on every run.

**Three things the definitions make visible that the prose did not.** Coverage at h is *cumulative*
over steps 1..h, not the value at step h, and the same convention governs every horizon-indexed
quantity in the paper. The overconfidence factor is a **ratio of means**, not a mean of ratios, and
its calibrated value is √(2/π) = 0.798 rather than 1. And in `task1_calibration.py:64` seeds are
concatenated onto the trajectory axis before pooling — fine for a point estimate over a balanced
design, and *not* a valid resampling unit, which is M-27 restated where a reader can see it.
**Evidence** `SRC` `results/v3_metric_definitions.json`; `scripts/v3_metric_definitions.py`.
**Status** CONFIRMED · **Relevance** METHOD


### X-15 — The follow-up moved to v3 and every figure reference in our paper went stale · **NEW**

Our paper pins section numbering for `arXiv:2501.10100v1` and records v2's renumbering. It did not do
this for `arXiv:2504.16680`, whose §5.1 and Eq. 4–5 it cites repeatedly. That paper is now at **v3**,
last revised **8 January 2026** and substantially expanded — a Related Work section, a training
diagram, a results table and two further deployment figures.

**What did not move**, checked against both HTML renderings: §5.1 keeps its number and both quoted
sentences are in it; Eq. 4 (`u = Var_b[μ^b]`) and Eq. 5 (`r̃ = r − λu`) keep their numbers and render
character-identically. So every **section** and **equation** reference in our paper resolves in v3
unchanged.

**What moved:** the uncertainty-estimation figure our §5.1, §5.2 and §5.6 discuss is **Figure 2
(right) in v1 and Figure 3 (right) in v3**; the MOPO-PPO training figure is **Figure 3 → Figure 4**;
the episodic-rewards figure **Figure 4 → Figure 5**; the MOPO-PPO hyperparameter table, which is where
the 100-step imagination horizon lives, is **Table S9 → Table S11**; the architecture table **S6 →
S7**; the training-parameter table **S8 → S10**. The model was renamed **RWM-O → RWM-U**, and our
paper quotes v1 sentences containing "RWM-O".

Recorded in `results/original_paper_figures.json` under `followup_version_map`, the same treatment
2501.10100 already had. Every in-text citation of the follow-up now names the version it was read
from.

**A pipeline defect found while doing this.** `scripts/original_paper_figures.py` rewrote that JSON
wholesale and silently dropped the `verification` block that `scripts/verify_original_quotes.py`
writes into the same file — the record that all four EXT quotations were matched as substrings of the
published HTML. Since the quote checker needs the network it is deliberately not a `reproduce.sh`
stage, so it could not simply re-run afterwards: any regeneration of the figures artifact turned four
verified quotations into four asserted ones, with nothing reporting it. The generator now carries the
block forward and says so on every run.
**Evidence** `EXT` `results/original_paper_figures.json`; `scripts/original_paper_figures.py`.
**Status** CONFIRMED · **Relevance** METHOD



### R-68 — Trunk-sharing is part of why the epistemic spread is too small · `[RWM-U]` · **NEW**

M-44's verdict, applied by code, exactly as the rule was committed.

**The contrast.** Arm A at ensemble size 1, seeds 0–4, scored **together as a five-member
ensemble at evaluation time** — five models sharing no parameters and no recurrent state —
against the three shared-trunk `armA_seed{0,1,2}_ens5` arms, on the same four out-of-sample
trajectories, through the same harness, with each member keeping its own hidden state and the
ensemble mean fed back to all. Seeds 3 and 4 were trained for this at about 1.2 h each; seeds 0–2
already existed. The protocol differs from the shared-trunk one in exactly the property under
test.

**The verdict: MECHANISM SUPPORTED.** All six conditions hold against all three shared-trunk
seeds. At h = 100 — the deployment horizon X-13 establishes — the independent ensemble's
overconfidence factor is 0.485–0.503× the shared-trunk arms', a **2.03× improvement** against a
minimum detectable effect of 1.45× fixed in advance; ±1σ coverage is **+6.69 to +7.33 points**,
mean +7.12 against an MDE of 2.26. Every paired cluster-bootstrap interval excludes zero.

**What keeps this from being overstated, and it is the part worth reading.** The overconfidence
factor is error over σ, so it improves if σ grows *or* if error shrinks, and only the first is the
mechanism. Five independent models also denoise better than five heads on one trunk — an ordinary
ensembling effect, not an architectural one. Decomposed multiplicatively:

| h | σ larger by | error smaller by | total | from σ | from accuracy |
|---|---|---|---|---|---|
| 1 | 1.56× | 0.97× | 1.52× | 106% | −6% |
| 8 | 1.81× | 1.02× | 1.84× | 97% | 3% |
| 32 | 1.68× | 1.08× | 1.83× | 87% | 13% |
| **100** | **1.65×** | 1.23× | 2.03× | **71%** | 29% |
| 128 | 1.62× | 1.29× | 2.09× | 65% | 35% |
| 368 | 1.49× | 1.70× | 2.53× | 43% | **57%** |

σ is larger at **every** horizon, by 1.49–1.81×, which is the direction trunk-sharing predicts.
At the deployment horizon it is 71% of the effect. At the open-loop diagnostic horizon of 368 the
split reverses and most of the apparent gain is the ensemble simply predicting better — so
quoting the 2.53× there as an architectural effect would overstate it, and 6.10 reports both
columns for that reason.

**What it licenses.** That the released ensemble's disagreement understates epistemic uncertainty
**partly because its members are not independent models**, with a measured size at the horizon
that matters. It does **not** license attributing the whole gap to trunk-sharing: independently
seeded runs differ in both initialisation and data ordering, so the comparison bounds the
architectural effect rather than isolating it, and the bound is generous to the mechanism by
construction. M-44 stated that limitation before the runs and §12 repeats it.

**And it does not repair the interval.** The independent ensemble is still 5.2× overconfident at
h = 100 with 15.31% coverage against a calibrated 68.27%. Building the ensemble properly is worth
doing and it is not sufficient.
**Evidence** `RUN` `results/r2_independent_ensemble.json`; `scripts/r2_independent_ensemble.py`.
Topology: `results/v1_ensemble_topology.json`. Power: `results/p1_power_check.json`.
**Status** CONFIRMED · **Relevance** CONTRIB


### R-69 — The within-rollout signal survives, and the control it replaces was measuring something else · `[RWM-U]` · **NEW**

M-45's verdict, applied by code, exactly as the rule was committed.

**The verdict: DISAGREEMENT CARRIES WITHIN-ROLLOUT INFORMATION.** Double-demeaning the
(trajectory, step) panel — removing the trajectory mean *and* the step mean from both variables —
and correlating the residuals gives **r_dd = +0.419, 95% CI [+0.318, +0.576]** over a cluster
bootstrap on n_independent = 20. The interval excludes zero and the effect is well above the
rule's own minimum detectable effect of 0.183, which a dilution study placed between a true 0.086
(undetected) and 0.172 (detected). §6.7's supporting branch applies.

**The part the rule did not anticipate, and it matters more than the verdict.** Splitting the
pooled +0.605 shows the between-trajectory correlation is **+0.878**, carrying 51.7% of the
pooled covariance. And §6.7's existing "decisive" control — the within-step one at +0.739 — is
**itself a between-trajectory statistic**: `task_d2b_robustness.py:84` correlates *across
trajectories* at each fixed step and averages, which removes forecast depth completely and removes
trajectory difficulty not at all. That is why it reads **above** the pooled figure rather than
below it, which was the symptom that prompted this analysis.

So A2 does not merely add a sixth control. **It reinterprets the fifth**, and the description
"the decisive one" is withdrawn. r_dd is the first statistic in this paper that isolates
within-rollout information, and §13 now leans on it.

**Two qualifications carried into the paper.** The within-rollout effect is materially smaller
than the pooled figure — +0.419 against +0.605 — so disagreement separates *rollouts* better than
it separates *moments within a rollout*. And it is **not established at short horizon**: r_dd's
interval excludes zero at h = 100, 128 and 368 and spans zero at h = 8 and 32, where too few steps
exist to demean against. That inverts the shape one might expect and is reported as measured.

**The h=1 figure does not collapse, and it is not what it looked like.** The pre-registered
diagnostic tested whether trajectory difficulty manufactures the +0.994: disagreement correlates
+0.006 with commanded speed and +0.040 with per-episode difficulty (D-12), and partialling both
out of the disagreement–error correlation leaves +0.995. It does not move. The figure is real. It
is nevertheless a correlation over **twenty trajectory-level points** — at h=1 the panel has one
column, so nothing within a rollout is being tested at all — and §10 now says that rather than
calling it a ranking of realised error without qualification.
**Evidence** `RUN` `results/a2_trajectory_level_control.json`;
`scripts/a2_trajectory_level_control.py`. Power: `results/p1_power_check.json`.
**Status** CONFIRMED · **Relevance** CONTRIB



---

### R-70 — The h=100 re-anchoring left the prose behind, in 22 sentences · **NEW**
The paper re-anchored from h=368 to h=100 (X-13, V2): h=368 is the upstream's open-loop
**diagnostic** length and h=100 is the method's own imagination rollout length. The tables
followed. Parts of the prose did not.

**The measurement.** `scripts/horizon_sweep.py` walks `PAPER.template.md`, resolves every
placeholder to the artifact cell it came from, and compares that cell's horizon against the
horizon the surrounding text names. A calibration figure — an overconfidence ratio or a coverage
— must name its horizon in its own sentence; every other horizon-indexed value must name it in
the enclosing paragraph. On the 24 August draft it returns **28 findings across 20 distinct
locations**: 11 calibration figures unscoped at sentence level and 17 other values unscoped at
paragraph level. Re-derivable —
`git show <24-aug-rev>:PAPER.template.md > /tmp/pre.md && python scripts/horizon_sweep.py --file /tmp/pre.md`.

**Eight of the eleven sentence-level findings had been found by hand** in the second review brief,
which is a good rate for a manual pass over a thirty-page paper and is also the argument for not
relying on one: three calibration figures and all seventeen paragraph-level ones had not been
found, and one that the brief did find (§6.6's "39.7× overconfident") this scanner passes, because
the sentence names two horizons and the scanner cannot tell which the ratio belongs to. Manual
reading and the scanner miss different things; both were used.

**Why no existing check saw them.** Every numeral involved was correct and every one came from a
named artifact, so `build_paper.py`'s provenance gate passed. Provenance says where a number came
from; it says nothing about whether the sentence around it is scoped to that number's horizon.

**Two of the 22 were substantive rather than merely unlabelled.** §6.10 wrote the σ-gain range as
"1.56–1.81× at every horizon" — the h=1 and h=8 values standing in for a range that does not span
h=368's 1.49×. And §6.2's summary paired the h=368 ratio between the two uncertainty terms (600×)
with h=100 figures in the same sentence; that ratio is itself horizon-dependent and is 349× at
h=100 (S-18).

**Now zero, and kept there.** The sweep runs on every build as the `horizon-consistency` check
and the build fails on any finding.
**Evidence** `RUN` `results/horizon_sweep.json` `scripts/horizon_sweep.py`.
**Status** CONFIRMED · **Relevance** METHOD


### M-46 — M-23 is anchored at the diagnostic horizon, not the deployment one · **NEW**
**The rule is untouched and its verdict stands as returned.** This entry records what the rule's
anchor is now known to be, which is not the same thing as changing it.

M-23 (commit `efc35b8`) tests the autoregressive-versus-teacher-forcing gap at h=368, and §5's
header described that as "the horizons the method deploys at". V2 establishes that h=368 is the
upstream's open-loop **diagnostic** length and that the method's own imagination rollouts run to
h=100 — so the header named the wrong regime for the horizon the rule actually uses. §3.1 already
says h=368 "is not a deployment horizon"; §5 had not followed.

**This is the third instance of the M-24 pattern** — a decision rule anchored without regard to
the regime it would be applied in. M-24 was the first (a rule at h=8, the training horizon, for a
claim about long horizons). M-43 was the second (a rule committed without a power check, returning
DOES NOT GENERALISE at a sample size that could not resolve its own criterion). M-23 is the third,
and it is the mildest of the three: the rule's regime is *longer* than the deployment horizon
rather than shorter, so it is if anything a harder test.

**What changes in the paper.** §5's header names the open-loop diagnostic horizon. The same A/B
comparison is reported at h=100 beside the pre-registered h=368 figure, and the two differ
materially — 4.61× against 2.58× — so a reader cannot assume the headline transfers to the
horizon §6 is anchored to. **Nothing discharges or re-opens M-23.**
**Evidence** `RUN` `results/task_d1_threeseed.json` `results/v2_deployment_horizon.json`.
**Status** CONFIRMED · **Relevance** METHOD


### X-16 — RWM-O and RWM-U are one model renamed, verified by occurrence count · **NEW**
The reference list and Appendix F both state that arXiv:2504.16680 renamed its model from RWM-O to
RWM-U between v1 and v3. That claim was challenged on the reading that the public v3 contains
**both** names — RWM-U in the abstract and RWM-O in the experiments — which would make them two
variants rather than one rename, in a paper whose premise is checking claims against sources.

**Checked by counting rather than by reading**, on the rendered HTML of all three versions,
28 August 2026:

| version | RWM-O | RWM-U |
|---|---|---|
| v1 | 39 | 0 |
| v2 | 0 | 43 |
| v3 | 0 | 43 |

The two names never co-occur. The introducing sentence is otherwise word-for-word identical:
v1 "To this end, we introduce **Offline** Robotic World Model (RWM-O), where we explicitly
incorporate uncertainty quantification"; v3 the same with "**Uncertainty-Aware**". What changed is
the expansion of the letter, not the model — the architecture tables and Eq. 4 are unchanged
(V4).

**The claim stands.** The expansions and the counts are now recorded, so the next reader can check
it in one grep rather than by re-reading the paper.
**Evidence** `EXT` `results/original_paper_figures.json`.
**Status** CONFIRMED · **Relevance** CONTEXT


### X-17 — M-44's contrast differs in capacity as well as in independence · **NEW**
§6.10 compares five independently-initialised full models against five heads on one shared trunk.
§12 recorded two respects in which the two arms differ besides the one under test: initialisation
and data ordering. There is a third, and it is the one a reader of §6.10 will find first.

**Capacity.** Measured from the checkpoints' own tensors, the state pathway — the parameters that
produce the mean predictions whose spread *is* the epistemic term — carries **3,570,820**
parameters in the independent arm against **1,024,132** in the shared-trunk arm, a factor of
**3.49**. Each independent member brings its own trunk.

**Why it matters specifically here.** The overconfidence factor is error over σ, and greater
capacity can raise σ as well as lower error. σ is the column the mechanism claim rests on.
§6.10's decomposition separates the σ gain from the accuracy gain; it does **not** separate
capacity from independence, and nothing in this project does.

**What would settle it:** five trunks at one fifth the width each, matched on total state-pathway
capacity, with five independent recurrent states. That is a different architecture and a different
training run, and it is out of scope here.

**M-44's verdict is unaffected and its text is not edited.** M-44 was committed before the runs
and states its own limitation on two axes; this is a third axis, found afterwards, and it is
recorded here rather than written back into a pre-registered rule. §12 names all three.
**Evidence** `RUN` `results/v1_ensemble_topology.json`.
**Status** CONFIRMED · **Relevance** METHOD


### M-47 — Four check kinds, and the two ways the checker was not checking · **NEW**
`scripts/check_comparative_claims.py` had eight enumerated kinds and none of them could have
caught four of the defect classes the second review found. Four kinds were added:

- **`horizon-consistency`** — every horizon-indexed figure in the prose names its horizon, and
  names the one its artifact cell came from (R-70). Catches the whole class.
- **`arithmetic`** — a stated total equals the sum of its stated parts. Appendix B read
  "46 hours … 20 for the six 10,000-iteration runs and 27 for the remaining 20"; 20 + 27 = 47.
  All three came from `wall_clock_s` and none was typed; each was rounded to whole hours on its
  own.
- **`kind-count`** — the number of kinds §9 claims, the number Appendix D enumerates and the
  number the checker registers at run time are one number. They had drifted seven apart, inside
  the appendix about count consistency.
- **`scope-consistency`** — a universal quantifier in the body is checked against the set it
  quantifies over. §4 said the eight untested claims were "without exception" about policy
  learning or hardware; Appendix E prices two of them as CPU-affordable (S-17).

**`count-consistency` was extended to numeric-string variants.** It caught a count stated in two
different sizes and could not see a constant spelled two different ways: 68.3 against the derived
68.27, in §6.8, Figure 1's caption and its axis label; and +0.917 against +0.918, two sections
apart, for one bootstrap of one statistic quoted from two different artifacts.

**Two failures of coverage rather than of arithmetic, both in the checker.** One assertion could
not be corrupted at all — the `orders` check quoting a ratio directly had no stated order to
perturb, so the self-test skipped it and reported 31 of 31 caught beside a claim count of 32. And
the `sign` kind, which exists precisely to catch a stated direction that is not the measured one,
had no claim attached to §6.8's "opposite directions" sentence (S-16). A kind with no claim
attached guards nothing, and no self-test can report that, because there is nothing to corrupt.
Both are now entries in Appendix D's list of defects the self-test found in the checker itself,
which is generated from the checker rather than typed.

**Every claim is now corrupted on every build with no exemptions**: 44 of 44 caught against 44
claims across 19 kinds.
**Evidence** `RUN` `results/comparative_claims.json` `scripts/check_comparative_claims.py`.
**Status** CONFIRMED · **Relevance** METHOD


### S-16 — "The two largest held-out deviations are in opposite directions" · **NEW**
**Retracts** — a framing, not a numbered claim; the two coverage figures it names are correct
**What is retracted:** §6.8's description of the two largest deviations from nominal coverage
across the per-horizon recalibration's held-out cells as being "both at h=100 on the aleatoric
term, **in opposite directions** (77.48% and 76.55%)".

**Why it is wrong, in two ways.** Both figures are **above** the 68.27% target, so they are not in
opposite directions; and the second is at **h=128**, not h=100. The earlier draft's pair —
76.55% and 60.18% — *was* in opposite directions, and the sentence survived the recomputation
that changed which two cells were largest.

**What is not retracted:** the coverage figures themselves, the identification of the largest
deviation, and the conclusion of §6.8. Both cells are still the two largest and the per-horizon
multiplier still lands every held-out cell within tolerance. The corrected reading is *milder*
than the retracted one: the multiplier is slightly conservative at the long horizons rather than
unstable in both directions.

**Who found it:** the second pre-submission review, from the shipped PDF. **Why no check caught
it:** the `sign` kind existed and no claim used it on this sentence (M-47). Two now do.
**Evidence** `RUN` `results/task_d3_perhorizon.json`.
**Status** RETRACTED · **Relevance** METHOD


### S-17 — "The eight untested claims are, without exception, about policy learning or hardware" · **NEW**
**Retracts** — a framing, not a numbered claim; the list of untested claims is unchanged
**What is retracted:** §4's universal quantifier. Of the eight claims of the two originals that
this work did not test, **six** need a simulator, an RL loop and an ANYmal. The other **two** —
the M=32/N=8 configuration sweep and the MLP/RSSM/transformer baseline comparison — need none of
that, and Appendix E says so two pages later, pricing both within the CPU budget this project
already spent.

**What is not retracted:** that we did not test them, or the reason. They are unrun for want of
time, which §4 now says plainly instead of attributing them all to hardware we do not have.

**Why it survived.** The claim and its counter-example were in the same document, two appendices
apart, and nothing compared them. The `scope-consistency` check now reads the quantifier in §4
against the enumeration in Appendix E, and both counts in that paragraph are derived from those
two tables rather than typed.
**Evidence** `RUN` `PAPER.template.md, Appendix E + F tables`.
**Status** RETRACTED · **Relevance** METHOD


### S-18 — "The per-member σ is worse by three orders of magnitude" · **NEW**
**Retracts** — a framing, not a numbered claim; both underlying ratios are correct
**What is retracted:** the abstract's description of the gap between the two uncertainty terms as
"three orders of magnitude". At the horizon the abstract is anchored to — h=100, the method's own
imagination rollout length — the ratio between the aleatoric and epistemic overconfidence factors
is **349×**, which is two and a half orders. The "three orders" phrasing described the h=368
figure of 600× and was not re-anchored with the rest of the sentence.

**The underlying cause is that the ratio is itself horizon-dependent and only the h=368 form
existed as a key.** It is now generated at every horizon, so a sentence can quote the one it is
scoped to, and the abstract quotes the factor rather than an order of magnitude.

**This is a recurrence, not a new class.** Appendix D already lists "two prose descriptions of one
ratio that disagree" among the failure modes a provenance gate cannot see, and this is the same
defect surviving a change of anchor. The `orders` check now asserts that a directly-quoted ratio
appears in the sentence that quotes it, at the horizon that sentence names, and that assertion is
itself corruptible for the first time (M-47).
**Evidence** `RUN` `results/task_d_nind20.json`.
**Status** RETRACTED · **Relevance** METHOD


### S-19 — "The released checkpoint cannot have come from the released recipe" · **NEW**
**Retracts** — a framing, not a numbered claim; the three extrapolations it rested on all stand
**What is retracted:** the inference from three independent implied-iteration estimates to the
conclusion that the released checkpoint is inconsistent with its own released recipe. §8 of the
paper narrowed this before submission and the narrowing was never entered here, so the claim went
on standing in the ledger's contributions summary and in the public README after the paper had
withdrawn it. That is the failure this entry exists to close, and it is the same one M-28 and the
README regeneration were written for: a claim withdrawn in one document and left asserted in
another.

**The defensible claim** is that **no constant-rate run from the released initialisation at the
configured learning rate reaches this checkpoint's variance state in 500, 2,500 or 5,000
iterations**. The extrapolation assumes the released initialisation and learning rate. The first
author's account is that "the checkpoint was released after a few iterations of the repo than the
setup I used for the submission" — so a warm start, or a `log_delta_logstd` initialised
differently, would explain the gap with no inconsistency at all, and §8's own table records that
neither can be excluded by the second parameter.

**What is not retracted:** the arithmetic. The collapse rate, the `min_logstd` clock and the
negative implied count under `gaussian_nll` are unchanged and are what let the gap be detected.
What changes is what they license: a documentation gap between a release and a run, which is
common and worth recording, rather than an inconsistency in the release.

**Who found it:** raised in correspondence with the first author, 21 August 2026; the ledger
summary and the public README were found still asserting it by the second pre-submission review.
**Evidence** `RUN` `results/step6_analysis.json` · `EXT` first-author correspondence.
**Status** RETRACTED · **Relevance** METHOD

### M-48 — The correspondence transcript was published on a named repository for 46 minutes · **NEW**
**What happened.** `docs/SUPPLEMENTARY_CORRESPONDENCE.md` was committed on 23 August (`7859309`)
and pushed to `github.com/<author>/rwm` on **2026-08-28 at 11:46:49 +0530**, in the push that
brought the public repository up to date for submission. The history was rewritten to purge it and
force-pushed at **16:47 +0530 the same day**. **Exposure window: 2026-08-28, 11:46 to 16:47
+0530 — five hours**, on a public repository under the author's own name, in full.

**What the purge does and does not achieve, stated precisely because the difference matters.** A
fresh clone from GitHub after the force-push carries zero commits and zero blobs with that path,
which is checkable and was checked. It does **not** reach two things. Unreachable objects survive
on GitHub's side until GitHub garbage-collects them, so for some period the blob may still be
fetchable by hash by anyone who recorded one; asking GitHub Support to run `gc` on the repository
is the only way to force that, and it is a human action. And anyone who cloned, forked or fetched
during the five-hour window holds a complete copy that no rewrite can reach. Neither is likely for
a repository with no announced release; neither is impossible; and this entry says so rather than
implying the removal was total.

**What the file is.** The verbatim exchange with the first author of both papers under
reproduction, anonymised as to both parties but not consented to. The paper's own header on that
file reads `CONSENT NOT YET RECORDED`, and states that if it still reads that at submission the
quotations must come out of the paper.

**Two consequences, neither repairable by editing prose.**

1. *The offer in the letter.* The reply drafted for the first author asks permission to quote
   three fragments and offers to withdraw any of them the same day. That offer cannot be honoured
   for an exchange already published. If he opened the repository link in that letter during the
   window, he would have found the whole exchange there.
2. *The submission's anonymity, not merely the file's.* §6.1 and §8 cite the transcript as
   **anonymised** supplementary material. A reviewer, or anyone, searching a quoted sentence
   during the window would have reached a repository under the author's name — which
   de-anonymises the whole submission, not one file.

**What was done.** The transcript is now generated OUTSIDE the repository tree by
`scripts/t5_anon_transcript.py`, gitignored inside it, and copied into the anonymised bundle and
the supplementary archive — where reviewers need it and where it is not public. `submission_check`
gained **A0**, a public-tree gate that fails the build if a never-publish path appears in the
working tree, in git's index, in HEAD, or in reachable history. The history check is the one that
matters: a deletion commit satisfies the other three and leaves the file recoverable from the
public repository forever.

**What was not done, and is not this script's to do.** Consent has still not been given. The
window above is what a reader of this ledger needs if it is refused.

**The judgement that produced it, recorded because it is the useful part.** The exposure was not
an accident of tooling. The risk was identified before the push, in writing, and the decision to
push anyway was taken deliberately and then reversed. `.gitignore` would not have prevented it —
the file was already tracked, and an ignore rule does not apply to a tracked path. Only A0's
history check would have.
**Evidence** `INFER` `results/anon_bundle.json` `scripts/submission_check.py`.
**Status** CONFIRMED · **Relevance** METHOD

## Candidate paper contributions

Ordered by how completely evidenced each is, with the paper it bears on tagged. Two papers are
in scope; see the scope note at the top.

1. **The uncertainty output is unusable, and that is a property of the objective, not of the
   training run** `[RWM-U]` (C-06, C-10, C-11, R-48–R-54, O-12, O-13). The most completely
   evidenced claim here, and **novel rather than confirmatory**. Analytic derivation —
   `E[(mu + sigma·eps − y)²] = (mu − y)² + sigma²` is minimised at sigma = 0, and `min_logstd`
   cancels out of the bound loss so the ratchet is one-way. Empirical confirmation across
   **17 training runs**. A linear extrapolation validated to 3% over a fourfold extension.
   A corrective experiment using **the authors' own unused `gaussian_nll` branch**. And
   calibration measured against a known reference: the released checkpoint's predicted sigma is
   **7,878× smaller than its own mean absolute error**, giving 0.14% coverage at ±1σ against a
   calibrated 68.3%. The correction reverses the mechanism and still fails — magnitude improves
   to 10.9×, while the faint ordering signal the faithful arm had (39/45 dimensions positive,
   P = 5.4e-07) is **destroyed** (21/45, chance). Measured across all four models (R-57), the
   failure is specifically one of **magnitude**: Arm B has the most input-dependent σ and the
   best-ordered σ (45/45, P = 6e-14) and is still 315× overconfident. σ is flat even inside the 8-step trained
   horizon while error grows 3.4×, so no structural excuse survives.

2. **The paper's central claim reproduces, and the margin is large** `[BASE]` (R-22, R-23, M-23,
   R-40, R-42). Confirmatory rather than novel, but stress-tested harder than anything else in
   the project: SETTLED under four independent metric/aggregation variants, at 10 and 100
   trajectories, on a rule committed to git before the runs that tested it existed, with Arm A
   leading 4.4–9.7× at h=368 and the per-episode sign positive on all ten episodes.

3. **Aggregation and evaluation power can invert a published-model comparison — including one
   this project published** `[BOTH]` (R-29, R-30, M-19, S-10, S-11, M-17). Reported as a worked
   example with the retraction attached.

4. **The released artifacts do not reproduce the released checkpoint's variance state**
   `[BOTH]` (C-12, C-13, O-12, R-24, R-25, R-41, R-50, S-19). Collapse rate implies ~158,000
   iterations against a tag of 5,000; `min_logstd` on a 5× slower clock implies order 2.7e5; and
   under `gaussian_nll` the implied count is **negative**, so the branch it was trained with is
   identifiable. **This claim is narrower than the one it replaces.** It read "cannot have come
   from the released recipe, on three independent measures" until §8 withdrew that: the
   extrapolation assumes the released initialisation and learning rate, and the first author's
   account is that the repository moved on between the training run and the release. A warm start
   or a changed initialisation explains the gap with no inconsistency, and neither can be
   excluded. What is measured is a documentation gap between a release and a run.

5. **The released pipeline trains on spliced episodes, and the cost is now measured** `[BASE]`
   (B-01, D-03, D-06, R-47, R-55, R-56). Zero of 32 comparisons show harm under either
   resampling unit; a duplication control confirms the training-loss rise is caused by splice
   content rather than by window count, and the control is inert in rollout.

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
