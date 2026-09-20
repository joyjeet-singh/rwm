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
