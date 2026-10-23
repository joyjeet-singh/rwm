# Round 5 — the new readings, in plain words (G5, 2026-10-19)

For the rewrite sessions (G8, G11–G15). Each reading names its keys (`results/paper_numbers.json`), its ledger entry
and its scope. Numbers appear here only as key names, so this file cannot disagree with the artifacts. Post hoc
analyses are labelled post hoc; none changes a discharged verdict.

## Pre-registered rules read this round

**X9, per-member propagation (M-101).** The released rollout feeds every ensemble member the ensemble's mean through
one recurrent state, so its spread at a deep step is a one-step spread at one shared history. Rolling each member out
on its own predictions instead **narrows the gap between spread and accumulated error at h = 100 in all four models**
(`x9_rel_verdict`, `x9_e5_verdict`, `x9_ind_verdict`, `x9_fold_verdict`). The share of the log gap closed is
`x9_rel_f_h100` `x9_rel_f_h100_ci` on the released checkpoint and `x9_fold_f_h100` `x9_fold_f_h100_ci` on the fold
ensembles. The ensemble-5 and independent readings rest on 4 trajectories and are descriptive (`x9_e5_p_h100`). ±1σ
coverage rises from `x9_rel_mean_cov1_h100`% to `x9_rel_per_cov1_h100`% but stays below X7's band (`x9_band_lo`–
`x9_band_hi`%), so it does not close the gap. CRPS and NLL improve too (`x9_rel_{mean,per}_crps_h100`), so the effect
is not just a wider spread. **Scope, every time:** `x9_scope`. Per-member propagation is not the released method, and
the release's own imagination rollout (one member per environment) is not tested. **Story:** "effectively
propagated" fails as the release does it; most of the ensemble's information would propagate if the members were
rolled out separately. This is the paper's most actionable result.

**X10, in-sample against held-out (M-102).** The reading **splits by horizon**. At h = 1 the ensemble-5 arms' error
to spread ratio is *higher* on their own training episodes, ratio `x10_q_h1` `x10_q_h1_ci`, all three seeds above
1 (`x10_verdict`). At h = 100 and h = 368 the label it would carry is the opposite (`x10_label_h100`,
`x10_label_h368`; `x10_q_h100` `x10_q_h100_ci`). At h = 1 the two statistics also disagree: the ratio is worse
in-sample (`x10_rho_in_h1` against `x10_rho_out_h1`), but ±1σ coverage is about the same (`x10_cov1_in_h1`,
`x10_cov1_out_h1`). **Scope:** `x10_caveat`. The arenas differ in episodes as well as in training status. **Story:**
§6.2's sentence "in-sample measurement biases toward better calibration, so the `d1n_epi_ratio_h1`× is if anything flattering"
(`PAPER.template.md:585`) is not supported at h = 1 and must go. A summary may only say the effect depends on the
horizon.

**X11 (M-97–M-100, M-103).** Pre-registered in GT1 and G3; the training queue runs until about 22 October. The
readings arrive in GT2. No sentence may anticipate them.

## Post hoc analyses (G4)

**N8, the tails (R-81) → S-22.** Every cell of M-65's test is non-Gaussian. `n8_n_heavy` of `n8_n_cells` are
heavy-tailed: they over-cover at ±1σ and under-cover at ±2σ once σ is rescaled to the right mean. The rest are mixed
(`n8_n_mixed`), and `n8_n_near` are near-Gaussian. **"Too small by", Y7's single meaning, is the coverage-matching
multiplier**, the factor on σ that restores 68.27% ±1σ coverage: on the released checkpoint, epistemic, all ten
episodes, `n8_k_rel_epi_h1`, `n8_k_rel_epi_h8`, `n8_k_rel_epi_h32`, `n8_k_rel_epi_h100`, `n8_k_rel_epi_h128`,
`n8_k_rel_epi_h368` at h = 1, 8, 32, 100, 128, 368. On the ensemble-5 arms (held-out pair) it is `n8_k_e5_epi_h*`.
Under it, ±2σ coverage is only `n8_cov2_at_k_rel_epi_h*`%. The error-to-spread ratio ρ is reported beside its
calibrated value `m65_calib_ratio` and is never called "too small by". **Story:** the shortfall is partly shape; the Gaussian
nominal is not defended.

**N7, exact tests at n = 4 (R-82).** At four trajectories the smallest attainable two-sided p is `n7_p_min_n4`, so
**no comparison the paper reports at n = 4 can be significant**. No Holm family could reject anything
(`n7_sweep_can_reject`, `n7_baselines_can_reject`, `n7_x4_can_reject`). `n7_n_4of4` of `n7_n_n4` reach that minimum.
X3's episode-level test is the exception that holds (`n7_x3_ep_p_h368`). **Story:** every n = 4 interval is reported
with its exact p and "k of 4", and nothing at n = 4 is called resolved.

**N9, the per-horizon recalibration scored (R-83).** It restores ±1σ at every horizon, but ±2σ stays at
`n9_epi_perh_cov2_h100`% `n9_epi_perh_cov2_h100_ci` at h = 100 (95.45% nominal). CRPS improves
(`n9_epi_{before,perh}_crps_h*`), NLL falls by orders of magnitude, and the interval widens (`n9_epi_perh_width_h*`).
**Story:** recalibration fixes the scale, not the shape.

**N10, floors (R-84).** **Predicting the training mean is a stronger floor than holding the last state at h = 368**
on every arena and both metrics (`n10_mean_nrmse_heldout_h368` against `n10_hold_nrmse_heldout_h368`; also the
`_fold_` and `_all10_` keys). **Exception:** at h = 100 on the held-out pair's relative-L1, hold-last is lower
(`n10_hold_l1_heldout_h100` against `n10_mean_l1_heldout_h100`). Seasonal-naive, with its period fixed from training
data (`n10_period_default`, `n10_period_s` s), is no better than hold-last. nRMSE's denominator is the mean
per-dimension σ (`src/rwm_metrics.py:115-133`); using the RMS of σ multiplies every value by `n10_kappa_heldout`, so
it changes no comparison. **Story:** the long-horizon tables gain a training-mean row, and "beats the floor" is
re-read against it.

**N11, rank correlations (R-85).** Under Spearman, disagreement ranks error more strongly at every h ≥ 8
(`n11_d2_sp_epi_h*`), and its lead over the forecast index is resolved at each of them (`n11_d2_sp_diff_h*` `_ci`).
**Not at h = 1:** there Pearson is the higher (`d2_epi_h1` against `n11_d2_sp_epi_h1`). On the 20 whole trajectories,
the step-size margin that fell below M-51's minimum detectable effect under Pearson has an interval above zero under
ranks (`n11_e7_sp_step_margin` `n11_e7_sp_step_margin_ci`). M-51's verdict stands (Y8). **Story:** by Y8, Spearman is
the headline ranking statistic, with each verdict's Pearson statistic named.

**N12, provenance (R-86).** **The checkpoint-provenance sentence N12 supports:** "No file in either released
repository records which rows trained the released checkpoint, and the checkpoint stores no data statistic, hash or
path (`n12_ckpt_has_data_stats`; tagged iteration `n12_ckpt_iter`). Its one-step error shows no in-sample/held-out gap
across the episode groups where our own model shows one (`n12_rel_l1_h1_released_on_train` against
`n12_rel_l1_h1_released_on_heldout`; ours `n12_rel_l1_h1_armA_in` against `n12_rel_l1_h1_armA_out`). That is consistent
with its having trained on all ten episodes, or on none, and the data cannot tell which." `n12_n_artifacts_role_change`
artifacts carry "in-sample" wording for the checkpoint; each is held-out if the CSV is a separate recording.

**N13, Adam (R-87).** Every path uses Adam's defaults (`n13_beta1`, `n13_beta2`, `n13_eps`). The collapse moves log
δ at a median `n13_rate_over_lr_median` learning rates per iteration (`n13_n_runs` runs): the ordinary Adam step. Even
at the largest step Adam can take (`n13_bound_over_lr` × the learning rate), the checkpoint's variance state needs
`n13_iters_worst` iterations from the released initialisation (`n13_iters_typical` at a typical step), against 500,
2,500 and 5,000. **Story:** §7.5 recast as Adam's bound, worst case included. The project's typed −14.4629 is a
defect; use `n13_ckpt_log_delta` (OUT_OF_SCOPE).

**N14, one-step accounting (R-88).** Even at one step no ensemble's spread accounts for its error: mean squared error
is `n14_R_rel` times what the spread predicts for the released checkpoint, `n14_R_e5` for the ensemble-5 arms and
`n14_R_ind` for the independent ensemble. All intervals lie above 1 (`n14_R_*_ci`). **Story:** this is the
"residual one-step miscalibration" gap, and §6 leads with it (PLAN G13).

## Withdrawn or corrected in the record (G5)

- **S-22** withdraws M-65's reading "NOT HEAVY-TAILED in every cell", its "Gaussian nominal is defensible", and its
  "no single λ repairs" argument; M-65 and M-96 are marked. Replaced by R-81.
- **S-23** withdraws C-04's framing of the shared state trunk as undisclosed: RWM-U v1 §4.1 states it. Credit it.
- **S-24** withdraws C-11's "the floor freezes, and nothing can reopen it". Write "no gradient from the bound term"
  instead.
- **C-17** corrects C-09: both papers set the decay factor to 1.0, which is what the code computes. It is a naming
  difference, not a gap. The training length is in RWM v1 Table S9 and RWM-U v1 Table S8.
- **C-18**: per-head bootstrap resampling exists in the online (MBPO-PPO) path and not in the offline path our arms
  follow.
- **R-89** corrects R-75's circular survey count to three counts: `q1_*` keys to add in G13 from
  `results/q1_pets_descendants.json` `counts` (looked at = `examined` + `construction_absent_and_so_out_of_scope`; implement = `carry_the_construction`; optionally trains = `inherits`).

**Wording changes with no ledger entry** (the rewrite removes or reframes them; line numbers as of this commit):
"provably drives … to zero" (`PAPER.template.md:19`) becomes "the objective's optimum is σ = 0", with the pathway
caveat; "the first calibration measurement we are aware of" (`:59`) is removed; the λ argument read as a calibration
failure (`:595`), and "deep-rollout states are under-penalised" wherever it appears, go: the penalty's job is to
bound one-step error at visited states; "freezes" (`:632`) becomes "receives no gradient from the bound term"; the
in-sample sentence (`:585`) goes, per X10.

---

## Addendum, GT2 (2026-10-23): X11, read at n = 20 on the five folds

For G13 onwards. Ledger `M-104` records the readings; keys are `x11a_*` … `x11e_*` (`results/paper_numbers.json`). The queue gate
passed (`round5/gt2_queue_check.json`). Each reading is exploratory, bounded, and re-opens no discharged rule. **Scope every
time:** each fold's own ensemble-5 arms on that fold's own held-out pair, 20 trajectories from ten episodes held out once;
the models of different folds share most training episodes.

**X11a, in-sample against held-out (M-97): MIXED at h = 1** (`x11a_verdict`; `x11a_q_h1` `x11a_q_h1_ci`: all three seeds below
1, the pooled interval contains 1). At h = 100 and h = 368 the label it would carry is IN-SAMPLE FLATTERS
(`x11a_label_h100`, `x11a_label_h368`). So X10's h = 1 reading (IN-SAMPLE IS WORSE, 16 against 4 trajectories) **does not
hold at n = 20**; the rule-10 row on in-sample measurement now reads: no direction at h = 1, flattering at long horizons.
**Story:** a summary may say the effect depends on the horizon and that the h = 1 sign is not stable across arenas; it may
not say in-sample is worse at one step.

**X11b, disagreement against the forecast-step index (M-98): GENERALISES** (`x11b_verdict`): disagreement leads at
`x11b_n_leads` of `x11b_n_horizons` horizons and the paired interval excludes zero at `x11b_n_excl`; r values `x11b_r_dis_h*`
against `x11b_r_idx_h*`. Supports contribution 4's ranking claim at n = 20 for the ensemble-5 arms.

**X11c, per-horizon recalibration on unseen episodes (M-99): DOES NOT RESTORE CALIBRATION** (`x11c_verdict`):
`x11c_cells_cal` of `x11c_n_cells` cells calibrated, the constant multiplier `x11c_const_cal`. **Alongside only:** the pooled
±1σ coverage is WITHIN BAND at every horizon (`x11c_pooled_cov1_h*`, `x11c_pooled_label_h*`) against `x11c_before_cov1_h*`
before any multiplier. **Story:** the sentence "rescaling restores one-sigma coverage" holds for the released checkpoint
(X7) and, pooled, for the fold arms, but the pre-registered cell-level reading on unseen episodes says no. This is the
**[X11c]** row of OUTLINE's rule-10 table: §5.7 must give both, and no summary may drop "on the released checkpoint" without
the cell-level reading beside it.

**X11d, independent against shared trunk (M-100): MECHANISM SUPPORTED** (`x11d_verdict`): `x11d_ratio_gain`× lower
overconfidence and `x11d_cov_gain` points more ±1σ coverage at h = 100, against M-44's committed thresholds; the n = 20
label is the same (`x11d_label_n20`). §5.3's sharing claim now rests on n = 20 as well as n = 4; members still differ in
capacity and data order.

**X11e, per-member propagation on the fold arms (M-103): PROPAGATION NARROWS THE GAP** (`x11e_verdict`) at h = 100, n = 20:
`x11e_f_h100` `x11e_f_h100_ci`; ρ `x11e_mean_rho_h100` → `x11e_per_rho_h100`; ±1σ `x11e_mean_cov1_h100`% →
`x11e_per_cov1_h100`%. Same direction as X9; `x9_scope` applies.

**Slots.** OUTLINE's **[X11 slot]** marks fill as: H7 (Table 3) gains the fold ensembles' X11a calibration row; H11 the X11d
reading; H12 the X11e reading; H16 the X11c reading with both of its faces; H9 the X11a reading above.
