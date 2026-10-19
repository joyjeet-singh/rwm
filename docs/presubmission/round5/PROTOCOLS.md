# Round 5 — analysis protocols (G2, 2026-10-19)

**Status.** §2 (X9) and §3 (X10) are **pre-registered rule text**, committed before any of their data exist: on
the day of this commit there was no `results/x9_*`, `results/x10_*`, `scripts/x9_*`, `scripts/x10_*` or `cache/x9_*`
file, and no N7–N14 artifact. G3 adds each rule's ledger entry (status `PRE-REGISTERED`) and its frozen reading
script under a commit subject containing `PRE-REGISTER`, **before** the first reading (PLAN §1.2 rule 4). After
that commit the script is never changed; if it must change, the session stops `BLOCKED`.
§4 (X11) is a skeleton that GT1 completes. §5 (N7–N14) are **post hoc** specifications for G4: each is its own
script, artifact, `reproduce.sh` stage and ledger entry, is labelled post hoc everywhere, and never changes a
discharged verdict.

Changes from PLAN Annex 2 are listed in §7. Each one tightens a rule or fills a value; none loosens one.

Paths are relative to `rwm_repro/`. `PY` is `$HOME/Downloads/PDM/.venv-rwm311/bin/python`. "Upstream" files are
read from the pinned copies `../robotic_world_model_lite/` and `../rsl_rl_rwm/`, which `CROSSWALK.md` §code shows
are also the current code.

---

## 1. Shared definitions, from the existing code

Everything below is read from the code; a new script reuses these and does not re-derive them.

**Data and windows.** 50 Hz (`src/rwm_data.py:42`, `DT = 0.02`), 45 state dimensions (`:34-36`): base linear
velocity 0–2, angular velocity 3–5, gravity 6–8, joint positions 9–20 (`JOINT_POS`, `:25`), joint velocities 21–32,
joint torques 33–44; actions are columns 45–56. A *trajectory* is a non-overlapping 400-row window
(`MET.non_overlapping_starts`, `src/rwm_metrics.py:100`): rows 0–31 are history (`E.START_STEP` = 32) and rows
32–399 are 368 forecast steps. "Horizon h" always means **cumulative over forecast steps 1..h**, i.e. array slice
`[START : START + h]` (`scripts/task_d_nind20.py:227`) or `[:, :h]` on arrays that already start at `START`
(the `cache/` files, `MN.metrics`). States are in the config-normalised space (`R.normalise_state` with the
reference config's `state_data_mean`, `state_data_std`).

**Action alignment.** Every calibration artifact this round reuses was made at `action_offset = 1`, the causal
pairing: `task_d_nind20.py:175`, `task_d3_ens5.py:124-126`, `task_d3_perhorizon.py:54`,
`r2_independent_ensemble.py:64,208`; `x7_loeo_recalibration.py` through `TD3.episode_rollout`; `m65` through the
cache files that those scripts wrote. `mn_sweep_eval.score` (`scripts/mn_sweep_eval.py:105`) defaults to
`action_offset = 1` and `_pairing` (`:231`) returns the arrays unchanged at 1. Every new rollout here uses 1.

**Rollouts that exist.**
- Shared-trunk ensembles (the released checkpoint and our ensemble-5 arms) are run through
  `S.ReferenceRWM` (`src/score_reference.py:45`). `step` (`:88-125`) runs one trunk (`state_base`) on the batch,
  applies every head to the same trunk output, and returns the **ensemble mean** (`means.mean(0)`, `:121`,
  mirroring `system_dynamics.py:114`); it stores the per-dimension aleatoric σ (`last_sigma`, mean over heads of
  each head's σ, `:114`) and the per-dimension epistemic spread (`last_epistemic = means.std(0)`, `:118`, PyTorch's
  default `unbiased=True`, i.e. **ddof = 1**). `rollout_uncertainty` (`:127-156`) feeds the ensemble mean back as
  the next input through **one** recurrent state. Our arms are loaded into the same class
  (`task_d3_ens5.py:117-119`), which is asserted against our trainer's forward to < 1e-5 (`:122-128`).
- Independent members: `rollout_independent` (`scripts/r2_independent_ensemble.py:64-107`) steps each
  `S.ReferenceRWM(sd, ensemble=1)` member (`load_ens1`, `:110-126`) with **its own** recurrent state but feeds the
  **ensemble mean** back to every member; spread is `M.std(0)` across members (ddof = 1, `:104`).
- Single models through our trainer's class: `rwm_model.RWMEnsemble.rollout_full`
  (`src/rwm_model.py:206`, signature `rollout_full(self, state, action, start_step, action_offset=1)`) and
  `rollout` (`:228`); `MN.score` uses `rollout`.

**Which path the release uses (PREMISES B2).** With `model_ids=None` the released `system_dynamics.forward`
returns the ensemble mean (`system_dynamics.py:112-115`); that is the evaluation path
(`robotic_world_model_lite/scripts/model_training.py:133`, `rsl_rl_rwm/.../mbpo_ppo.py:291`) and it is what
`ReferenceRWM.rollout_uncertainty` implements. The released **imagination** env instead draws one member per
environment (`scripts/envs/base.py:54,68,142`; `system_dynamics.py:116-121`) and feeds back that member's
prediction; its epistemic term is still the spread of all heads at that one member's history.

**Calibration statistics that exist** (the existing code's "per-dimension handling").
`task_d_nind20.block` (`:113-152`) and `r2_independent_ensemble.block` (`:129-134`): with e = |prediction −
truth| and s the per-dimension σ, pooled over (trajectory, step ≤ h, dimension):
ρ = nanmean(e) / nanmean(s); ±1σ coverage = nanmean(e ≤ s); ±2σ coverage = nanmean(e ≤ 2s). Intervals:
`cluster_ci_from_per_traj` (`task_d_nind20.py:87-110`) resamples whole trajectories with
`default_rng(0).integers(0, n, (20000, n))` and takes the ratio of the resampled per-trajectory means; the
percentile interval drops non-finite draws and reports how many were finite. The ensemble-5 arms pool three seeds
as `task_d3_ens5.py:243-278` does: the point value is the **mean over seeds of each seed's ρ**; the interval
averages each trajectory's numerator and denominator over seeds, then resamples trajectories with
`default_rng(0).integers(0, 4, (20000, 4))`.

**Stored per-step values.** `cache/{model_id}__{slug}__u400.npz` (gitignored; written when `STORE_PER_TRIPLE=1`;
keys `err` (signed), `sig_aleatoric`, `sig_epistemic`, `traj_to_episode`, `traj_start_row`, `meta`;
`src/per_triple_cache.py:14-71`) exists for `released_ckpt_ens5` (all ten episodes; held-out pair) and
`armA_ens5_seed{0,1,2}`, `armA_faithful_mse_seed*`, `armA_corrected_nll_seed*`, `armB_teacher_forced_seed*`
(held-out pair). Per-trajectory values in `results/*.json`: `a1_ab_by_horizon` (`gap_per_trajectory`,
`A_per_trajectory`, `B_per_trajectory`), `x3_cross_fold` (`per_trajectory.{fold,start_row,episode,
armA_per_seed_l1,armB_per_seed_l1}`, by horizon, seed and trajectory), `r2_independent_ensemble`,
`r2_combined_arm`, `m49_capacity_matched` (`comparison.per_shared_seed.*.{log_ratio,ratio,
coverage_diff_pts}_per_trajectory`), `mn_sweep_verdict`, `baselines_verdict`, `x4_matched_baselines`
(`per_traj`), `alignment_defect_ci` (`arenas.*.per_trajectory`). Everything else stores summaries.

**Weights.** Released: `../robotic_world_model_lite/assets/models/pretrain_rnn_ens.pt`
(`system_dynamics_state_dict`). Ensemble-5 arms: `runs/armA_seed{0,1,2}_ens5/weights_2500.pt`
(`task_d3_ens5.py:117`). Independent members, fold {1, 8}: `runs/armA_seed{0..4}/weights_2500.pt`
(`r2_independent_ensemble.py:119`, `INDEP_SEEDS` `:45`). X3 folds: `x3_cross_fold.weights_path`
(`scripts/x3_cross_fold.py:121-124`): `runs/armA_seed{s}/weights_2500.pt` for {1, 8}, otherwise
`runs/x3_armA_ho{fold}_seed{s}/weights_2500.pt`, folds `((1,8),(0,2),(3,4),(5,6),(7,9))` (`:94`). All 23 files
were present on 19 Oct 2026 (checked with `ls`, nothing loaded).

**Calibrated reference values.** For a Gaussian error with the right scale, E|e|/σ = √(2/π)
(`results/m65_gaussian_nominal.json` `calibrated_ratio_sqrt_2_over_pi`, the value 0.7978845608028654 used
everywhere below, written as √(2/π)); ±1σ coverage 68.27%, ±2σ 95.45% (`m65` `targets`). X7's band is
[58.27%, 78.27%] (`results/x7_loeo_recalibration.json` `design.band`), the target ± `CM.TOL` = 0.10.

**Gaussian scores**, used by X9 and N9, with z = e/s on each element (e ≥ 0, s > 0):
CRPS = s·[z(2Φ(z) − 1) + 2φ(z) − 1/√π], NLL = ½ ln(2π s²) + e²/(2s²), in nats per (step·dimension). Φ is computed as
½(1 + erf(z/√2)) with `torch.special.erf` in float64 (numpy has no `erf` and scipy is not installed; none is to be
installed). Elements with s ≤ 0 or non-finite are excluded from every statistic and counted.

**Timing (every script below).** Wrap the work in `time.perf_counter()` and write
`timing: {wall_clock_s, torch_threads: torch.get_num_threads(), cpu_count: os.cpu_count(), platform:
platform.platform()}` into the artifact. Do not call `torch.set_num_threads`. The session logs every job over one
minute (PLAN §1.5). Before a run projected over 10 minutes, probe on an idle machine and record the projection.

---

## 2. X9 — Does propagating each member on its own predictions make the spread track accumulated error?

*Inference only; pre-registered by this commit.*

**Why.** RWM-U's current abstract says uncertainty is "effectively propagated over long horizons" (PREMISES P8).
The released evaluation rollout feeds the ensemble mean to every head through one recurrent state, so the spread
at step *t* is a one-step spread at one shared state history.

**What it contrasts (PREMISES B2).** MEAN is the release's **evaluation** path (`model_ids=None`,
`system_dynamics.py:112-115`), which is what our §6.4 measured. X9 does **not** test the imagination env's
one-member-per-environment rollout (`envs/base.py:54,68,142`): there every head is still evaluated at one shared
history, so its spread is again a one-step spread, and PER-MEMBER is the only mode in which the members' histories
differ. That the imagination path is not tested is stated wherever X9 is reported.

### 2.1 Models and arenas (all exist; no training)

| tag | model | arena | n | batching |
|---|---|---|---|---|
| (a) `rel` | released checkpoint, 5 shared-trunk heads | all ten episodes, 20 non-overlapping 400-step trajectories, built as `task_d_nind20.py:162-176` | 20 | one batch of 20 |
| (b) `e5` | Arm A ensemble-5 arms, seeds 0–2, 2,500 iterations, each a 5-head shared trunk | held-out pair {1, 8}, 4 trajectories, built as `task_d3_ens5.py:86-95` | 4 | one batch of 4 per seed |
| (c) `ind` | independent ensemble, Arm A single models seeds 0–4, 2,500 iterations | held-out pair, 4 trajectories | 4 | one batch of 4 |
| (c3) `ind3` | (c)'s members seeds 0–2 only | held-out pair | 4 | one batch of 4 |
| (d) `fold` | per X3 fold, a three-member independent ensemble of that fold's Arm A seeds 0–2 (`x3_cross_fold.weights_path("A", fold, s)`) | each fold's own held-out pair: `MN.arena(ep, fold, 32)["starts"]`, windows from `MN.window_arrays(data, cfg, starts, 32, 32)` and `MN._pairing(..., 1)`, pooled over the five folds in `FOLDS` order | 20 (each episode held out once) | one batch of 4 per fold, as `MN.score` |

(a) is "in-sample" only if the checkpoint trained on this recording, which is an assumption (PREMISES P20); X9
reports (a) as "all ten episodes" with that caveat and draws no in-sample/held-out contrast from it. (c3) is
reported beside (c) on fold {1, 8} to show what the member count alone does (three members are not five, and a
small ensemble's spread is biased low); it carries no verdict.

### 2.2 Two propagation modes

- **MEAN** (the released evaluation protocol). Computed by **calling the existing functions unchanged**:
  `ReferenceRWM.rollout_uncertainty(st.clone(), ac, 32, action_offset=1)` for (a) and (b);
  `r2_independent_ensemble.rollout_independent(models, st.clone(), ac, 32, 1)` for (c), (c3) and (d). No
  reimplementation of MEAN is allowed.
- **PER-MEMBER** (TS∞ in Chua et al. 2018's terms). Member *k* receives its own previous prediction at every step
  after the first, through its own recurrent state; at forecast step 1 every member receives the same true
  32-step history. For a shared-trunk model this means the trunk is run **once per member**, on that member's own
  input, with MEAN's batch shape (B trajectories per call, not K·B), so float32 rounding matches MEAN's at step 1.
  Implementation: a new function `step_heads(m, s_in, a_in, h_state)` that copies `ReferenceRWM.step` lines
  `:94-105` verbatim and returns the per-head means `(E, B, 45)` and per-head σ `(E, B, 45)` instead of their
  mean; member *k*'s step uses only head *k* of the trunk output computed from member *k*'s input and member *k*'s
  hidden state. For independent members each member is stepped with `m.step` exactly as `rollout_independent`
  does, but with its own prediction fed back. Index arithmetic for `s_in`, `a_in` is copied from
  `score_reference.py:141-149`. The auxiliary trunk is not run (`want_aux=False`, as MEAN).
- **Statistics** for both modes, at each forecast step: prediction ȳ = mean over members of the members'
  predictions (under MEAN this is the fed-back mean itself); e = |ȳ − truth| per dimension; s = standard deviation
  across members per dimension, ddof = 1 (as `means.std(0)`).
- **Per-member σ** (the aleatoric head). The per-member predicted σ has collapsed (§6.3). Record its size beside
  the error's: `alea_mean` = mean over (trajectory, step ≤ h, dimension) of the mean over members of each member's
  σ, beside mean e, for both modes. It enters no statistic.

### 2.3 Statistics, by horizon

Horizons h ∈ {1, 8, 32, 100, 128, 368}, cumulative over steps 1..h, pooled over (trajectory, step, dimension)
exactly as §1's `block`. Per model, arena and mode: ρ = mean e / mean s; ±1σ and ±2σ coverage; mean Gaussian
CRPS and NLL with scale s (§1); mean e, mean s, `alea_mean`, and the count of excluded elements. For (b) every
quantity is computed per seed and pooled as §1 says (mean over seeds of per-seed values).

**Fraction of the gap closed**, primary horizon h = 100, also reported at every horizon:
f = ln(ρ_MEAN / ρ_PER) / ln(ρ_MEAN / √(2/π)).
f = 0: no change; f = 1: per-member propagation brings ρ to its calibrated value; f < 0: per-member propagation
widens the gap; f > 1: it overshoots into under-confidence. f is undefined when ρ_MEAN ≤ √(2/π); then the
verdict is NO CLEAR CHANGE and the reason is recorded.

**Per-trajectory values** (used by the n = 4 tests and stored for N7): for trajectory t, ρ_t,mode =
mean_t e / mean_t s over (step ≤ h, dimension), f_t from ρ_t,MEAN and ρ_t,PER, and cov1_t,mode. For (b), each
trajectory's value is the mean over the three seeds of the per-seed value ("seeds averaged within trajectory",
M-27).

### 2.4 Intervals

- **(a) and (d), n = 20.** Paired bootstrap over trajectories: one draw matrix
  `default_rng(0).integers(0, 20, (20000, 20))`, the matrix `cluster_ci_from_per_traj` uses; in each draw both
  modes are recomputed from the drawn trajectories' per-trajectory means (numerator and denominator resampled
  together, as `cluster_ci_from_per_traj`), and f* is computed from that draw's ρ*_MEAN and ρ*_PER. Interval: 2.5th
  and 97.5th percentiles (`np.percentile`, default method) of the finite draws; the number of finite draws is
  recorded. Intervals are reported for ρ (both modes), ±1σ coverage (both modes), f, and the PER − MEAN differences
  in CRPS and NLL. (d) resamples the 20 trajectories regardless of fold, as X3 does.
- **(b), (c), (c3), n = 4.** Descriptive only. Exact two-sided sign-flip test on the four per-trajectory f_t
  (seed-averaged for (b)): statistic T = mean(f_t); over all 16 sign vectors ε, p = #{ε : |mean(ε·f)| ≥ |T| −
  1e-12} / 16, so the smallest attainable p is 0.125. Report p, "k of 4" (the number of f_t > 0), and the same test
  on the per-trajectory log-ratios ln(ρ_t,MEAN / ρ_t,PER). For (b), also report each seed's own k of 4.

### 2.5 Verdict, per model and arena, at h = 100

Exactly one of:
- **PROPAGATION CLOSES THE GAP** — the per-member ±1σ coverage is inside X7's band [58.27%, 78.27%]: for n = 20,
  its whole 95% interval lies inside the band (X7's own `WITHIN BAND` convention); for n = 4, the pooled value
  **and** each of the four per-trajectory values (seed-averaged for (b)) lie inside the band.
- **PROPAGATION NARROWS THE GAP** — not the above, and for n = 20 the lower end of f's paired interval is above 0;
  for n = 4, f_t > 0 on 4 of 4 trajectories (reported with its exact p).
- **PROPAGATION WIDENS THE GAP** — for n = 20 the upper end of f's interval is below 0; for n = 4, f_t < 0 on 4 of 4.
- **NO CLEAR CHANGE** — otherwise, or when f is undefined, or when fewer than 19,000 of the 20,000 draws of f are
  finite (n = 20).

Verdicts are issued for (a), (b), (c) and (d). (c3) and every horizon other than 100 are reported without a verdict.
The n = 4 verdicts are labelled descriptive: no n = 4 result can reach p < 0.125.

### 2.6 Assertions, all before any PER-MEMBER number is computed or printed

The script computes and checks every MEAN quantity first, writes the assertion block, and exits `BLOCKED` (writing
`results/x9_per_member_propagation.json.blocked`, no reading) if any fails.

1. **(i) MEAN reproduces the existing artifacts**, relative difference ≤ 1e-6 (relative to max(1e-12, |stored|)),
   at every horizon:
   (a) `results/task_d_nind20.json` `d1_by_horizon[h].epistemic.{ratio_err_over_sigma, coverage_pm1,
   coverage_pm2, mean_sigma, mean_abs_err}` and the intervals `ratio_err_over_sigma_ci`, `coverage_pm1_ci`,
   `coverage_pm2_ci` (same draw matrix); and `results/m65_gaussian_nominal.json` case
   `released_ckpt_ens5 [epistemic] all ten episodes`, `by_horizon[h].rho_err_over_sigma` and
   `coverage_pm1_observed_pct` / 100;
   (b) `results/task_d3_ens5.json` `calibration[h].per_seed[s].{ratio_err_over_sigma, coverage_pm1,
   coverage_pm2}`, `mean_ratio`, `mean_cov1`, `mean_cov2`, `ratio_ci`, `cov1_ci`, `cov2_ci` (with
   `task_d3_ens5.py:242`'s draw matrix);
   (c) `results/r2_independent_ensemble.json` `independent[h].{ratio_err_over_sigma, coverage_pm1,
   coverage_pm2, mean_sigma, mean_abs_err}`.
2. **(ii) The two modes agree at h = 1.** For every model, the step-1 predictions of every member and every
   statistic at h = 1 are identical under MEAN and PER-MEMBER: maximum absolute difference exactly 0.0.
3. **(iii) For (d), a one-member "ensemble" reproduces X3.** Each fold member alone, through the new PER-MEMBER
   code with K = 1 and `MN`'s input construction, (1) reproduces our trainer's rollout of the same weights
   (`x3_cross_fold.load(cfg, w)` then `.rollout(..., 32, action_offset=1)`) to a maximum absolute difference
   < 1e-5 (the tolerance `task_d3_ens5.py:127-128` sets for the same class comparison), and (2) gives per-trajectory
   relative-L1 (`MN.metrics(pred[:, 32:] − truth, truth, scale)[str(h)]["l1"]`) equal to
   `results/x3_cross_fold.json` `per_trajectory.armA_per_seed_l1[str(h)][s][t]` within 1e-5 absolute at every
   horizon, after asserting that the trajectory order matches `per_trajectory.fold` and `per_trajectory.start_row`.
   Batching: one call per fold with that fold's four trajectories, as `MN.score`; at h = 368 batching alone moves
   values by about 1e-2 (round 4 OUT_OF_SCOPE F2), so no other batching is allowed.
4. **(iv) Inputs.** The trajectory start rows of (a) equal the union of (b)'s held-out starts and X10's 16
   in-sample starts; every weight file's SHA-256 is recorded, and for (d) it equals `x3_cross_fold.json`
   `weights_sha256[fold]["A{s}"]`; every prediction and spread is finite; s > 0 for every member count ≥ 2.

The maximum observed difference for each assertion is written to the artifact whether it passes or fails.

### 2.7 Outputs

- Script `scripts/x9_per_member_propagation.py`; artifact `results/x9_per_member_propagation.json` with `rule`,
  `ledger`, `script_sha256`, `code_sha256` (this script, `score_reference.py`, `r2_independent_ensemble.py`,
  `mn_sweep_eval.py`, `x3_cross_fold.py`, `rwm_data.py`, `rwm_metrics.py`), `git_head`, `assertions`, `design`,
  per (model, arena, mode, horizon) the §2.3 statistics, per-trajectory values, intervals, the sign-flip tests,
  `verdict` per model, `scope` (the sentence below), `timing`.
- Stage `20v1 "X9 — per-member propagation against the released mean protocol"`, `NEEDS_WEIGHTS`, runtime from G3's
  probe.
- Keys (G3 adds them to `scripts/paper_numbers.py`): for arena tag A ∈ {rel, e5, ind, ind3, fold} and mode
  M ∈ {mean, per}: `x9_{A}_{M}_rho_h100`, `x9_{A}_{M}_rho_h368`, `x9_{A}_{M}_cov1_h100`, `x9_{A}_{M}_cov1_h368`;
  `x9_{A}_f_h100`, `x9_{A}_f_h368`; for A ∈ {rel, fold}: `x9_{A}_f_h100_ci`, `x9_{A}_per_cov1_h100_ci`; for A ∈
  {e5, ind, ind3}: `x9_{A}_k4_h100`, `x9_{A}_p_h100`; for A ∈ {rel, e5, ind, fold}: `x9_{A}_verdict`; and
  `x9_alea_over_err_max` (the largest `alea_mean` / mean e over every cell).

**Scope sentence (locked).** Per-member propagation is not the released method. MEAN tests "effectively
propagated" as the release's evaluation path does it; PER-MEMBER asks whether the ensemble's information would
propagate if the members were rolled out separately. The release's imagination path, which propagates one member
per environment, is not tested.

---

## 3. X10 — Does measuring on training data flatter an ensemble's calibration?

*Inference only; pre-registered by this commit.*

**Models.** Arm A's ensemble-5 arms, seeds 0–2, 2,500 iterations (`runs/armA_seed{s}_ens5/weights_2500.pt`), loaded
as `task_d3_ens5.py:117-119`. Their training split is recorded, so X10 does not depend on PREMISES P20.

**Arenas.** In-sample: `MET.non_overlapping_starts(ep, split["train_episodes"], 400)` with the default split
(`E.make_split(seed=0, strat_path=results/step0_strat.json)`), expected 16 trajectories, n_independent 16, from
episodes {0, 2, 3, 4, 5, 6, 7, 9}. Held-out: the pair {1, 8}, 4 trajectories, exactly `task_d3_ens5.py:86-95`.
In-sample is rolled out as one batch of 16, held-out as one batch of 4. Mode: MEAN only
(`rollout_uncertainty`, `action_offset=1`).

**Statistic.** Per seed s, arena and horizon h ∈ {1, 8, 32, 100, 128, 368}: ρ, ±1σ and ±2σ coverage of the
epistemic spread, by `task_d3_ens5.py:254-271`'s lines (copied verbatim, with the file:line cited in the script).
Q_s(h) = ρ_in,s(h) / ρ_out,s(h). Pooled as `task_d3_ens5.py` pools: ρ_arena(h) = mean over seeds of ρ_s; Q(h) =
ρ_in(h) / ρ_out(h). Primary h = 1; also h = 100; every horizon reported.

**Interval for Q.** Independent bootstraps of each arena's trajectories from one generator: `rng = default_rng(0)`;
`I_in = rng.integers(0, 16, (20000, 16))`, then `I_out = rng.integers(0, 4, (20000, 4))`, in that order. In draw b,
each arena's ρ* is computed as `task_d3_ens5._ci` does (seed-mean per-trajectory error means over the drawn
trajectories, divided by the seed-mean per-trajectory σ means), and Q* = ρ*_in / ρ*_out. Interval: 2.5th and 97.5th
percentiles of the finite draws. (The point value is a mean of per-seed ratios and the interval a ratio of
seed-pooled means, as in `task_d3_ens5.py`; this is copied, not changed.)

**Verdict at h = 1.**
- **IN-SAMPLE FLATTERS** — Q_s(1) < 1 for all 3 seeds and the pooled interval lies below 1;
- **IN-SAMPLE IS WORSE** — Q_s(1) > 1 for all 3 seeds and the pooled interval lies above 1;
- **MIXED** — otherwise.

h = 100 is reported with the same three labels, as "the label it would carry", not a second verdict.

**Caveat (locked).** The arenas differ in episodes as well as in training status, and per-episode difficulty varies
threefold (D-12), so this bounds the in-sample effect rather than isolating it. X11, if run, measures it with every
episode in both roles.

**Assertions, before any in-sample number is computed or printed.**
1. The held-out arm reproduces `results/task_d3_ens5.json` at every horizon, relative difference ≤ 1e-6:
   `calibration[h].per_seed[s].{ratio_err_over_sigma, coverage_pm1, coverage_pm2}`, `mean_ratio`, `mean_cov1`,
   `mean_cov2`, and `ratio_ci`, `cov1_ci`, `cov2_ci` recomputed with `task_d3_ens5.py:242`'s own draw matrix.
2. For each seed, `results/step5_armA_seed{s}_ens5.json`'s recorded `train_episodes` equal the in-sample episodes
   and its `holdout_episodes` equal [1, 8].
3. The in-sample arena has 16 trajectories, n_independent 16, two per training episode; its starts are disjoint
   from the held-out starts, and their union equals `MET.non_overlapping_starts(ep, range(10), 400)`.
4. For the in-sample batch, the harness agrees with our trainer's forward (`M.build_from_config(cfg,
   ensemble_size=5)`, `rollout_full`) to < 1e-5, as `task_d3_ens5.py:122-128` checks for the held-out batch.

**Outputs.** Script `scripts/x10_insample_vs_heldout.py`; artifact `results/x10_insample_vs_heldout.json` (with the
same provenance fields as X9); stage `20v2 "X10 — in-sample against held-out calibration, ensemble-5 arms"`,
`NEEDS_WEIGHTS`. Keys: `x10_q_h1`, `x10_q_h1_ci`, `x10_q_h1_seed{0,1,2}`, `x10_q_h100`, `x10_q_h100_ci`,
`x10_rho_in_h1`, `x10_rho_out_h1`, `x10_cov1_in_h1`, `x10_cov1_out_h1`, `x10_n_in`, `x10_verdict`,
`x10_label_h100`.

---

## 4. X11 — the ensemble experiments on X3's folds (skeleton; GT1 completes it)

Y5 is **(B)** (`DECISIONS.md#G0-rulings`), so X11 runs and X12 does not. GT1 fills every `‹GT1›` and commits the
completed rule and the queue under a `PRE-REGISTER` subject before the first run starts.

**Runs (training).** Through the round-4 queue mechanism, one job at a time (PLAN §1.5), 2,500 iterations, Arm A
configuration, on folds {0, 2}, {3, 4}, {5, 6}, {7, 9}:
- ensemble-5, seeds 0–2: 12 runs, `runs/x3_armA_ho{fold}_seed{s}_ens5/weights_2500.pt`, records
  `results/x3_run_armA_ho{fold}_seed{s}_ens5.json`;
- single model, seeds 3–4: 8 runs, `runs/x3_armA_ho{fold}_seed{s}/weights_2500.pt`, records
  `results/x3_run_armA_ho{fold}_seed{s}.json` (seeds 0–2 already exist from X3).
With fold {1, 8}'s existing runs, every fold then has three ensemble-5 arms and five independent members.
CPU: ‹GT1: probe one ensemble-5 and one single-model run for 50 iterations on an idle machine; project; cap 30 CPU-h
(Y5)›. Queue file, driver, sentinel and log: ‹GT1›. Training data assertion for each run: its recorded
`train_episodes` and `n_train_windows` equal X3's for that fold (`x3_cross_fold.json` assertions a–c).

**Readings** (each its own frozen script, committed before the queue finishes; statistics, thresholds and
branches copied from the discharged rule, with only the arena changed to the five folds' 20 held-out trajectories,
each fold's models scored on its own held-out pair; n = 20; paired bootstrap as X9 §2.4):
- **X11a** — held-out ensemble-5 calibration by horizon (statistics of `task_d3_ens5.py` §2), and X10's Q with every
  episode both in and out of sample (each fold's arms on its own 16 training trajectories against its own 4
  held-out). Verdict labels: X10's. ‹GT1: script name, keys›
- **X11b** — M-43's comparison of disagreement with the forecast-step index (`task_d3_ens5.py:160-231`): per seed,
  horizons {8, 32, 128, 368}, "leads at every horizon" and "paired interval excludes zero at a majority", labels
  GENERALISES / DOES NOT GENERALISE. ‹GT1›
- **X11c** — the per-horizon recalibration on episodes the model never saw: `task_d3_perhorizon.py`'s "fit on one
  held-out episode, score on the other" protocol, per fold and pooled over the five folds; X7's band and labels.
  ‹GT1›
- **X11d** — M-44's comparison of independent members with the shared trunk (`r2_independent_ensemble.py`'s `m44`
  block): h = 100, MDE thresholds 1.45 (ratio) and 2.26 points (coverage) from `results/p1_power_check.json`, a
  condition holds only against every shared-trunk seed. ‹GT1›
- **X11e** — X9's per-member propagation (§2, unchanged) on the fold ensemble-5 arms, verdict as §2.5 at n = 20.
  ‹GT1›

---

## 5. Post hoc analyses N7–N14 (G4)

Common to all eight:
- Each is labelled **post hoc** in its artifact (`"post_hoc": true`, `"never_reopens": "<the rules it reads>;
  nothing here changes a verdict"`), its ledger entry, the paper and the supplement.
- The first thing each script does is its **reproduction assertion**; a failure writes `<artifact>.blocked` and
  exits non-zero with no reading (PLAN §1.2 rule 5). Tolerances are fixed here and are never adjusted after seeing
  a new number.
- Provenance fields as X9 (`script_sha256`, `code_sha256`, `git_head`, `timing`).
- Stage IDs `20w7`…`20w14` in `reproduce.sh`, after `20v2`. Keys are prefixed `n7_`…`n14_`.
- No new dependency. numpy, torch and the standard library only.

### N7 — exact randomisation tests where the paper reports n = 4 with a bootstrap interval

**Inputs** (stored per-trajectory values; no rollout):
1. `results/a1_ab_by_horizon.json` `by_horizon[h]`, h ∈ {1, 8, 32, 100, 128, 368}: `gap_per_trajectory` (already
   the seed-mean B − A per trajectory); stored interval `gap_ci`.
2. `results/mn_sweep_verdict.json`: every node `…/per_config/<config>` under `governing`, `alongside.<metric_h>`
   (held-out): `per_traj` (seed-averaged, `verdict_mn_sweep.py:102-124`), stored `ci95` and `p`.
3. `results/baselines_verdict.json` `rules.{M-75,M-76}`: every `…/per_baseline/<baseline>` node under `governing`
   and `alongside.<metric_h>`: `per_traj`, `ci95`, `p`.
4. `results/x4_matched_baselines.json`: `reading.per_baseline.*`, `alongside.{l1_h100,l1_h32}.per_baseline.*`:
   `per_traj`, `ci95`.
5. `results/r2_independent_ensemble.json`, `results/r2_combined_arm.json`, `results/m49_capacity_matched.json`:
   `comparison.per_shared_seed.{0,1,2}`: `log_ratio_per_trajectory`, `coverage_diff_pts_per_trajectory`; and
   `r2_combined_arm.json` `m68.objective_isolated`.
6. `results/alignment_defect_ci.json` `arenas.held_out_n4`: per-trajectory difference
   `per_trajectory.offset0.<m> − per_trajectory.offset1.<m>` for m ∈ {rel_l1, nrmse_form1}; stored `ci95_pct` is
   for the overstatement percentage, so the test is also run on `per_trajectory_overstatement_pct.<m>`.
7. `results/task_d3_ens5.json` M-43 (`governing[h].per_seed`, h ∈ {8, 32, 128, 368}): per-trajectory values are
   not stored and the statistic is a correlation pooled over trajectories, which has no per-trajectory
   decomposition. N7 uses the **within-trajectory** difference d_t = r_t(disagreement, error) − r_t(index, error)
   (`task_d3_ens5.py:52-58`'s `pooled_corr` applied to trajectory t alone, i.e. the `f([t])` of `:179-182`),
   computed from a re-roll through `task_d3_ens5.py:116-127`'s code. It is labelled a different, within-trajectory
   estimand, reported beside the stored pooled difference.
8. The 20-unit arenas: `results/x3_cross_fold.json` (per trajectory, gap = seed-mean B − seed-mean A from
   `per_trajectory.armA_per_seed_l1`, `armB_per_seed_l1`, every horizon); `results/a1_ab_by_horizon.json`
   `sign_test[h].per_episode_gap` (10 episodes); and, once G3 has run, X9 (a) and (d)'s per-trajectory f_t and
   log-ratios.

**Unit and seeds.** The unit is the trajectory (n = 4) and, for 20-trajectory arenas, the episode: an episode's
value is the mean of its two trajectories' values (n = 10). Seeds are averaged within trajectory before any test,
never pooled as seed × trajectory (M-27). Where an artifact reports a comparison per shared seed (item 5), N7 tests
each seed's row as stored **and** a seed-averaged row (the mean over the three shared seeds of each trajectory's
value).

**Test.** For n values d_1..d_n: T = mean(d); over all 2ⁿ sign vectors ε (16 at n = 4; 1,024 at the 10-episode
level), two-sided p = #{ε : |mean(ε·d)| ≥ |T| − 1e-12} / 2ⁿ; "k of n" = the number of d_u with the sign of T (zeros
count for neither). Report p, k of n, the smallest attainable p (2/2ⁿ), the stored bootstrap p where one exists, and
for each Holm family in items 2–4 (m = 8, 3, 2) whether any member could be rejected at its Holm level with p ≥
2/16 = 0.125 (`can_any_reject`). Add the note: at the episode level of the held-out pair (2 units) the smallest
attainable p is 0.5, so no test is possible.

**Reproduction assertion.** For items 1–4: the stored point value equals mean(per_traj) within 1e-12, and the
stored interval and p are reproduced from the stored per-trajectory list by the artifact's own functions:
`P5.boot_ci`, `P5.boot_p` (`scripts/p5_sweep_power.py:124-139`) for items 2–4 and
`review_bootstrap_unit.boot_cluster` (`scripts/review_bootstrap_unit.py:79`) with `a1_ab_by_horizon.N_BOOT`,
`BOOT_SEED` for item 1, within 1e-12 (item 1: within 1e-7, the tolerance X3's assertion (e) met). Item 5:
`ratio_per_trajectory` = exp(`log_ratio_per_trajectory`) within 1e-12, and mean(`coverage_diff_pts_per_trajectory`)
= `coverage_diff_pts` within 1e-9. Item 6: the overstatement percentage per trajectory equals
100·(offset0 − offset1)/offset1 within 1e-9. Item 7: the re-rolled arrays reproduce the stored `r_index`,
`r_disagreement` and `paired_diff` per seed within 1e-9, and `paired_ci_lo/hi` with `cluster_boot` and
`default_rng(0)` within 1e-9. Item 8: x3's stored `reading.gap` and `part_of_rule.per_episode_sign_test_h368`
reproduced within 1e-9.

**Outputs.** `scripts/n7_exact_tests.py`, `results/n7_exact_tests.json` (one row per tested node: source file,
JSON path, n, T, k, p, stored interval, stored p), stage `20w7` (no weights except item 7's re-roll: mark
`NEEDS_WEIGHTS`). Keys: `n7_p_min_n4` (= 0.125, read from the artifact), `n7_n_tested`, `n7_n_4of4`,
`n7_sweep_can_reject`, `n7_baselines_can_reject`, `n7_x4_can_reject`, `n7_a1_p_h{100,368}`, `n7_a1_k_h{100,368}`,
`n7_x3_ep_p_h{100,368}`, `n7_r2_seedavg_p`, `n7_m49_seedavg_p`, `n7_align_p_rel_l1`.

### N8 — the tails, correcting M-65's reading

**Input.** The eight M-65 cases × six horizons = 48 cells, from the cache through `m65_gaussian_nominal.load`
(`scripts/m65_gaussian_nominal.py:55-62`), seeds concatenated as there. No rollout.

**Per cell**, with r = e/σ over the elements with finite σ > 0, N their number:
- mean-matching constant c = ρ/√(2/π) and ±1σ, ±2σ coverage under cσ (M-65's `oracle_constant_c`,
  `coverage_pm1_oracle_pct`, `coverage_pm2_oracle_pct`);
- the **coverage-matching multiplier** k = r₍⌈0.6827·N⌉₎, the smallest k with mean(r ≤ k) ≥ 0.6827 (the value
  `task_d3_perhorizon.fit_scalar`'s bisection converges to); the ratio k/c; and ±2σ coverage under kσ, mean(r ≤
  2k). Per DECISIONS Y7, k is the quantity the paper calls "too small by ×k".
- the **signature**, with tolerances fixed here: ±1σ is *over* if coverage under cσ > 73.27%, *under* if < 63.27%
  (M-65's own band, 68.27 ± 5.0), else *within*; ±2σ is *over* if > 97.95%, *under* if < 92.95% (95.45 ± 2.5), else
  *within*. The ±2σ tolerance is the Gaussian analogue of M-65's ±1σ band: a ±10% scale error moves Gaussian ±1σ
  coverage by about ±4.6 points and ±2σ coverage by +1.8/−2.6 points (arithmetic, Φ(±1.1), Φ(±0.9), Φ(±2.2),
  Φ(±1.8)). Labels: **heavy-tailed** (±1σ over and ±2σ under); **light-tailed** (±1σ under and ±2σ over);
  **near-Gaussian** (both within); otherwise **mixed (±1σ ‹state›, ±2σ ‹state›)**. Labels are lower case.

**Reproduction assertions.** (1) ρ, c, ±1σ and ±2σ coverage under cσ reproduce `m65_gaussian_nominal.json`
`cases[*].by_horizon[h]` for all 48 cells within 1e-12 (same arrays, same arithmetic). (2) For the cell
`released_ckpt_ens5 [epistemic] all ten episodes` at every horizon, k equals `TD3.fit_scalar` applied to the same
arrays (left-padded with 32 NaN columns, since `fit_scalar` slices from `START`), relative difference ≤ 1e-9.

**Reading.** Counts of each signature over the 48 cells, beside M-65's own counts (`verdict.counts`). N8 does not
relabel M-65's verdict; it reports what M-65's "over-dispersed" cells look like at ±2σ.

**Outputs.** `scripts/n8_tails.py`, `results/n8_tails.json`, stage `20w8` (`NEEDS_WEIGHTS`: the cache is regenerated
by stages that need weights). Keys: `n8_n_heavy`, `n8_n_light`, `n8_n_near`, `n8_n_mixed`, `n8_n_cells`;
`n8_k_rel_epi_h{1,100,368}`, `n8_k_over_c_rel_epi_h{1,100,368}`, `n8_k_e5_epi_h{1,100,368}`,
`n8_cov2_at_k_rel_epi_h{1,100,368}`.

### N9 — scoring the per-horizon recalibration

**Input.** X7's leave-one-episode-out fit, reused exactly: `cache = {e: TD3.episode_rollout(e) for e in 0..9}` as
`x7_loeo_recalibration.py` builds it, the per-fold multipliers c_fold[e][h] = `TD3.fit_scalar` on the other nine
episodes and the constant cc[e] = `TD3.fit_scalar(…, 1)`, both as `reading()` (`:140-160`). Quantity: epistemic
(X7's governing quantity); aleatoric also computed, artifact only.

**Per horizon** h ∈ {1, 8, 32, 100, 128, 368} and calibration C ∈ {before (multiplier 1), constant (cc[e]),
per-horizon (c_fold[e][h])}, each episode scored with its own fold's multiplier and the ten episodes pooled by
concatenation as `CM.counts`/`CM.pooled` do, with `TD3.cover`'s mask (finite σ > 0): ±1σ coverage, ±2σ coverage,
mean Gaussian CRPS and NLL with scale Cσ (§1), and mean ±1σ interval width 2Cσ in normalised-state units.
Intervals: X7's draw matrix, `default_rng(0).integers(0, 20, (20000, 20))` over trajectories in X7's order.

**Reproduction assertion.** ±1σ coverage and its interval for all three calibrations at every horizon equal
`x7_loeo_recalibration.json` `reading.per_horizon`, `alongside.epistemic_constant_multiplier.per_horizon` and
`alongside.epistemic_before_any_multiplier` within 1e-12; every c_fold[e][h] equals
`alongside.epistemic_c_spread_across_folds[h].per_fold[e]` and every cc[e] equals
`alongside.epistemic_constant_multiplier.c_per_fold[e]`, within 1e-9 relative.

**Outputs.** `scripts/n9_recalibration_scores.py`, `results/n9_recalibration_scores.json`, stage `20w9` (released
checkpoint only; **not** `NEEDS_WEIGHTS`). Keys: `n9_epi_{before,const,perh}_{cov2,crps,nll,width}_h{1,8,32,100,128,368}`
(72 keys) and `n9_epi_perh_cov2_h100_ci`.

### N10 — floors

**nRMSE as defined** (`src/rwm_metrics.py:115-133`, form 1): for squared errors pooled over the trajectories
passed in, nRMSE(h) = mean over steps t ≤ h of √(mean_d MSE_{t,d}) / mean_d scale_d, with scale_d the standard
deviation of normalised state dimension d over the arena's training-episode rows (`MET.training_scale`, `:30-42`).
`MN.metrics` (`scripts/mn_sweep_eval.py:82-92`) applies it per trajectory and averages; `head_to_head_accuracy`
pools the trajectories. Both conventions are reported, labelled.
**The added form** divides by √(mean_d scale_d²) instead of mean_d scale_d. Because the denominator is constant
across steps, the new form is form 1 times κ = mean_d scale_d / √(mean_d scale_d²) (κ ≤ 1) for any predictor, so a
model's value in the new form is its stored form-1 value times κ; N10 reports κ per arena, and the paper derives
model rows from it by key. Under the training-mean predictor on stationary data the new form is about 1, which is
why it is the natural "no-skill" scale.

**Predictors that use no model**, scored on every arena and horizon below:
1. **hold the last state**: the last history row repeated (`MN.floor`, `scripts/mn_sweep_eval.py:114-118`);
2. **training mean**: the per-dimension mean of normalised state over the arena's training-episode rows (the rows
   `MET.training_scale` uses), constant over the forecast;
3. **seasonal-naive**: repeat the last full gait cycle. With o the last history row and P the period, the forecast
   for step j ≥ 1 is row o − P + 1 + ((j − 1) mod P). If P ≤ 32 these rows lie in the window's history. If P > 32,
   rows before the window are read from the CSV where they belong to the same episode; a trajectory whose cycle
   would cross its episode's first row is scored with hold-last and counted in `n_seasonal_fallback`.

**The period P, fixed before any held-out scoring.** For each training episode and each joint-position dimension
(columns 9–20, `R.JOINT_POS`), x = the normalised series minus its episode mean; ACF(L) = Σ_t x_t x_{t+L} / Σ_t
x_t²; average over the 12 dimensions and the training episodes, equal weight per episode. Search window L ∈
[10, 100] steps (0.2–2.0 s at 50 Hz). P = the smallest L in the window that is a local maximum (ACF(L) ≥ ACF(L −
1) and ACF(L) ≥ ACF(L + 1)) with ACF(L) ≥ 0.8 · max over the window. P is computed for the default split's training
episodes and for each X3 fold's training episodes. **Procedure:** commit A adds the script with a `--period` mode
that prints the periods and with `PERIODS = {…: None}`; run `--period`; write the integers into `PERIODS`; commit B
(`[G4][N10] Fix the seasonal periods from training episodes`) before any scoring. The scoring mode refuses to run if
any period is `None` and asserts that each recomputed period equals its constant.

**Arenas and horizons.** h ∈ {1, 8, 32, 100, 128, 368}; metrics relative-L1 (`MN.metrics` `l1`) and nRMSE form 1
(both conventions) and κ. Arenas: (i) held-out pair, 4 trajectories, default split; (ii) in-sample, the default
split's 16 training trajectories; (iii) X3's five folds pooled, 20 trajectories, each fold with its own training
mean, scale and period; (iv) all ten episodes, 20 trajectories, default split (the released checkpoint's tables).

**Reproduction assertions** (hold-last; float32 provenance in the stored values, hence 1e-6 absolute):
`mn_sweep_verdict.json` `hold_last_floor_l1.{held_out,in_sample}.{100,368}`; `head_to_head_accuracy.json`
`rows.floor.cells.{1,8,100,368}.{l1,nrmse}` (pooled convention); `a1_ab_by_horizon.json`
`by_horizon[h].floor` at every horizon. And: `MET.training_scale` for the default split equals
`results/step4_0a_results.json` `nrmse_scale` (as `mn_sweep_eval.py:133-135` checks).

**Outputs.** `scripts/n10_floors.py`, `results/n10_floors.json`, stage `20w10` (no weights). Keys:
`n10_period_default`, `n10_period_s` (P·DT), `n10_kappa_heldout`, `n10_{hold,mean,seas}_{l1,nrmse}_heldout_h{100,368}`,
`n10_{hold,mean,seas}_{l1,nrmse}_fold_h{100,368}`, `n10_{hold,mean,seas}_nrmse_all10_h368`,
`n10_n_seasonal_fallback`.

### N11 — rank correlations beside every Pearson ranking statistic

**Units** (each recomputed from the same pooled vectors and the same bootstrap draws as the Pearson value it sits
beside):
- U1, §6.6's table: `task_d_nind20.py` D2 (`:244-300`): r(index, error), r(disagreement, error), the partial
  r(disagreement, error · index) and the paired difference, h ∈ {1, 8, 32, 100, 128, 368, all}; inputs as
  `:249-252`; bootstrap `cluster_boot` (`:49`) with a fresh `default_rng(0)` per statistic, 20,000 draws.
- U2, M-43's table on the ensemble-5 arms: `task_d3_ens5.py:170-188`, per seed, its `cluster_boot` (`:73`).
- U3, the within-rollout statistic: `scripts/a2_trajectory_level_control.py` r_dd (`:196`) and per horizon
  (`:238`), its `cboot` (`:95`).
- U4, the free baselines: `scripts/e7_free_baselines.py` (`baselines` `:124`, the statistics and the nested `boot`
  `:209` in `main`, `N_BOOT` = 4000): r(baseline, error), the margin and the partial, for step-size, entry-res and
  the index.
- U5, X6's short units: `scripts/x6_stepsize_short_units.py` (`panel` `:140`, `margin_of` `:110`, `boot` `:102`).
- U6, the per-dimension counts "positively correlated on k of 45 dimensions": `task_d_nind20.block` (`:143-150`)
  and `task_d3_ens5.py:258-262`; Spearman count only, no interval.

**Rank statistics.** Spearman ρ_s = the Pearson correlation of average ranks (ties share the mean rank), computed
on the same finite pairs, **re-ranked inside every bootstrap draw**. Rank partial: rank x, y and z within the
sample, then apply the unit's own partial function to the ranks. Kendall τ_b and Kendall's partial τ
((τ_xy − τ_xz τ_yz) / √((1 − τ_xz²)(1 − τ_yz²))) are reported as **point estimates only**: an exact τ_b on up to
7,360 points per evaluation (U1, h = all: 20 × 368) is too slow to bootstrap 20,000 times without a compiled
library, and none is added. τ_b is computed exactly in numpy (sign products over all pairs, in chunks), with ties
handled by the τ_b formula; a self-test compares it with a brute-force loop on 200 random points with ties, within
1e-12. Per DECISIONS Y8, Spearman is the headline rank statistic and each pre-registered verdict keeps the Pearson
statistic it was committed with.

**Reproduction assertion.** Every Pearson value and interval of U1–U6, recomputed through the imported function (or
the cited lines copied verbatim where the vectors are built inside `main`), equals the stored artifact within 1e-12,
re-rolling through the same rollout function where the vectors came from a rollout. Stored fields:
`task_d_nind20.json` `d2_forecast_index`, `task_d3_ens5.json` `governing`, `a2_trajectory_level_control.json`,
`e7_free_baselines.json`, `x6_stepsize_short_units.json`.

**Timing.** Probe 200 draws of U1 at h = all; if the projection for the whole script exceeds 60 minutes, run it in
the background (PLAN §1.5) and end the session.

**Outputs.** `scripts/n11_rank_correlations.py`, `results/n11_rank_correlations.json`, stage `20w11`
(`NEEDS_WEIGHTS` for U2). Keys: `n11_d2_sp_{idx,epi,par,diff}_{h1,h8,h32,h100,h128,h368,all}` and `_ci`;
`n11_d2_kt_{idx,epi,par}_{h100,h368,all}`; `n11_e5_sp_diff_h{8,32,128,368}_seed{0,1,2}`; `n11_a2_sp_rdd`, `_ci`;
`n11_e7_sp_{step,entry,index}_r`, `n11_e7_sp_step_margin`, `_ci`, `n11_e7_sp_step_partial`, `_ci`;
`n11_x6_sp_margin`, `_ci`; `n11_npos_sp_rel_epi_h368`.

### N12 — the released checkpoint's provenance

**Source evidence** (file:line, quoted): the release's configured data location
(`../robotic_world_model_lite/scripts/configs/anymal_d_flat_cfg.py:36-37`, `dataset_root = "assets"`,
`dataset_folder = "data"`, and `base_cfg.py:33-34`); the README's asset list; the checkpoint file's top-level keys,
`iter`, `infos`, and whether any data statistic, hash or path is stored (load with `map_location="cpu"`; record
SHA-256 and the key list); the upstream tags; and the correspondence as App. F already quotes it (the anonymised
exchange is kept outside the repository, `../rwm_private/SUPPLEMENTARY_CORRESPONDENCE.md`; quote nothing App. F does
not already quote).

**Data.** One-step error, relative-L1 at h = 1 on M-64's short units (`m64_short_units.build_index(episodes, 1)`,
`unit_rollout`, `rel_l1`, as `x3_cross_fold.m64_units` uses them): the released checkpoint on each of the ten
episodes; Arm A seeds 0–2 (2,500 iterations, default split) on each training episode (in-sample) and on each
held-out episode. Report per-episode means, the in-sample and held-out pooled means for the arms, and the released
checkpoint's pooled mean, with unit-level bootstrap intervals (20,000 draws, `default_rng(0)`). Descriptive; no
verdict.

**Reproduction assertion.** Arm A and Arm B seed-mean per-unit values on the held-out pair reproduce
`results/m64_short_units.json` `cells.C_section_5_ab_gap` exactly as `x3_cross_fold.json` assertion (f) does
(maximum absolute difference 0.0).

**Reading.** What is known; and a list, found by `grep` over `results/*.json` for the fields that label the released
checkpoint's arena (`in_sample`, `released_ckpt_arena_is_in_sample`, `rationale`, "trained on all ten"), of every
artifact whose role changes (in-sample ↔ held-out) if the CSV is a separate recording.

**Outputs.** `scripts/n12_provenance.py`, `results/n12_provenance.json`, stage `20w12` (`NEEDS_WEIGHTS`). Keys:
`n12_ckpt_iter`, `n12_ckpt_has_data_stats`, `n12_rel_l1_h1_released`, `n12_rel_l1_h1_armA_in`,
`n12_rel_l1_h1_armA_out`, their `_ci`, `n12_n_artifacts_role_change`.

### N13 — Adam

**Facts, quoted with file:line:** `../rsl_rl_rwm/rsl_rl/algorithms/mbpo_ppo.py:102` and `:54`;
`../robotic_world_model_lite/scripts/train.py:224-228`; `src/rwm_train.py:60-63` (`make_optimizer`), which `scripts/step5_train.py:244` calls. None passes `betas` or `eps`. The defaults are read **at run time** from
`inspect.signature(torch.optim.Adam.__init__)` (β1, β2, ε, `weight_decay`, `amsgrad`, with `torch.__version__`),
not from memory; learning rate and weight decay from `R.load_reference_config`.

**Distribution of `collapse_fit.rate_over_lr`** over every `results/*.json` with a top-level `collapse_fit` (81 files
on 19 Oct 2026): n, min, quartiles, max, overall and grouped by the record's `loss_type` and by arm.

**Bounds.** Kingma and Ba (2015) §2.1 (cited only through `scripts/t1_bibliography.py`): the effective step
|Δθ| ≤ α·(1 − β1)/√(1 − β2) when (1 − β1) > √(1 − β2), and ≤ α otherwise; "typical" |Δθ| ≈ α. Compute both with the
run-time β's and the configured α.

**Reachability, redone under each.** Δ = |`CKPT_LOG_DELTA` − the released initialisation of `log_delta_logstd`|,
with `CKPT_LOG_DELTA` read from the checkpoint (mean over heads of `state_heads.*.state_log_delta_logstd` in
`system_dynamics_state_dict`), asserted to equal −14.4629 (`scripts/step6_analyse.py:38`) within 5e-5, and the
initialisation read from a freshly built `MLPStateHead` (asserted to equal the iteration-0 entry of the runs'
`collapse` logs within one step bound). Minimum iterations to reach the checkpoint's state: Δ/α (typical) and
Δ/bound (worst case); compare with 500, 2,500 and 5,000.

**σ's trajectory for Figure 4.** Per run, from `collapse` (logged every 25 iterations): `min_logstd_mean` and
`log_delta_logstd_mean`, and the implied σ bounds exp(min) and exp(min + exp(log_delta)). Assertion: for every
saved checkpoint in `runs/*/` (`weights_500`, `rolling_2000`, `rolling_2250`, `weights_2500`, and the 10,000-iteration
runs' checkpoints), `RWMEnsemble.collapse_stats()` (`src/rwm_model.py:414-421`) on the loaded weights equals
the logged entry at that iteration within the worst-case one-step bound (it absorbs a one-iteration logging
offset); the maximum difference is recorded.

**Outputs.** `scripts/n13_adam.py`, `results/n13_adam.json`, stage `20w13` (`NEEDS_WEIGHTS`). Keys: `n13_beta1`,
`n13_beta2`, `n13_eps`, `n13_bound_over_lr`, `n13_rate_over_lr_{min,median,max}`, `n13_n_runs`,
`n13_iters_typical`, `n13_iters_worst`.

### N14 (optional) — how much one-step error the ensemble can account for

**Per model**, at forecast step 1 (h = 1), K members: E[e²] = mean over (trajectory, dimension) of (ȳ − y)²; E[s²]
= mean of the across-member sample variance (ddof = 1); R = E[e²] / ((1 + 1/K)·E[s²]). R = 1 if the truth behaves
like one more draw from the members' spread; R > 1 if the ensemble under-accounts. Models: the ensemble-5 arms
(seeds 0–2, held-out pair; per seed and seed-mean), the independent ensemble (K = 5 and K = 3, held-out pair), and
the released checkpoint (all ten episodes, labelled with PREMISES P20's caveat). Rollouts: the full 400-step
rollouts through the existing functions (`rollout_uncertainty`, `rollout_independent`), then index `START`.
Intervals: trajectory bootstrap, 20,000 draws, `default_rng(0)`; descriptive.

**Reproduction assertion.** At h = 1, ρ and ±1σ coverage reproduce `task_d3_ens5.json` `calibration["1"].per_seed`,
`r2_independent_ensemble.json` `independent["1"]` and `task_d_nind20.json` `d1_by_horizon["1"].epistemic` within
1e-6 relative.

**Outputs.** `scripts/n14_one_step_accounting.py`, `results/n14_one_step_accounting.json`, stage `20w14`
(`NEEDS_WEIGHTS`). Keys: `n14_R_e5`, `n14_R_ind`, `n14_R_ind3`, `n14_R_rel`, each with `_ci`.

---

## 6. Summary

| rule | owner | script | artifact | stage | weights | pre-registered |
|---|---|---|---|---|---|---|
| X9 | G3 | `scripts/x9_per_member_propagation.py` | `results/x9_per_member_propagation.json` | 20v1 | yes | yes (this commit) |
| X10 | G3 | `scripts/x10_insample_vs_heldout.py` | `results/x10_insample_vs_heldout.json` | 20v2 | yes | yes (this commit) |
| X11 | GT1, GT2 | ‹GT1› | ‹GT1› | ‹GT1› | yes (training) | in GT1 |
| N7 | G4 | `scripts/n7_exact_tests.py` | `results/n7_exact_tests.json` | 20w7 | item 7 | post hoc |
| N8 | G4 | `scripts/n8_tails.py` | `results/n8_tails.json` | 20w8 | cache | post hoc |
| N9 | G4 | `scripts/n9_recalibration_scores.py` | `results/n9_recalibration_scores.json` | 20w9 | no | post hoc |
| N10 | G4 | `scripts/n10_floors.py` | `results/n10_floors.json` | 20w10 | no | post hoc (period fixed first) |
| N11 | G4 | `scripts/n11_rank_correlations.py` | `results/n11_rank_correlations.json` | 20w11 | U2 | post hoc |
| N12 | G4 | `scripts/n12_provenance.py` | `results/n12_provenance.json` | 20w12 | yes | post hoc |
| N13 | G4 | `scripts/n13_adam.py` | `results/n13_adam.json` | 20w13 | yes | post hoc |
| N14 | G4 | `scripts/n14_one_step_accounting.py` | `results/n14_one_step_accounting.json` | 20w14 | yes | post hoc (optional) |

## 7. Changes from PLAN Annex 2 (all tighten or fill; none loosens)

1. **X9, what MEAN is.** Named as the release's evaluation path, and the untested imagination path stated in the
   scope sentence (PREMISES B2).
2. **X9, MEAN must call the existing functions unchanged**, so assertion (i) tests artifacts rather than a
   reimplementation; assertion (ii) is exact equality (0.0), not a tolerance.
3. **X9, CLOSES THE GAP** for n = 20 requires the whole 95% interval inside X7's band (X7's own convention) rather
   than the point value; for n = 4 the pooled value and each trajectory's value must lie inside it.
4. **X9, NARROWS** requires f's interval to lie **above** 0, not merely to exclude 0; the mirror-image case is a new
   label, **WIDENS THE GAP**, so that a worsening cannot be reported as no change. f undefined, or under 95% finite
   draws, is NO CLEAR CHANGE.
5. **X9, √(2/π)** is used to full precision (m65's stored value) rather than 0.7979.
6. **X9 (iii)'s tolerances** fixed at < 1e-5 on predictions (the precedent `task_d3_ens5.py:127-128` sets for the
   same harness-against-trainer comparison) and 1e-5 absolute on per-trajectory relative-L1, with the trajectory
   order asserted; added assertion (iv) on inputs and weight hashes.
7. **X9 (a)** carries PREMISES P20's caveat and draws no in-sample contrast.
8. **X10**: the generator order for the two arenas' draws, an assertion that the arms' recorded training split is
   the in-sample arena, and the harness check on the in-sample batch.
9. **N8**: the ±2σ tolerance (2.5 points) and the labels are fixed here; the coverage-matching multiplier is defined
   as an order statistic and asserted to equal the existing bisection.
10. **N10**: the period's search window ([10, 100] steps), its selection rule and the two-commit procedure are
    fixed here; the added nRMSE form is shown to be a constant rescaling κ of form 1.
11. **N11**: Kendall τ_b is a point estimate only (no compiled library is added); Spearman carries the intervals.
