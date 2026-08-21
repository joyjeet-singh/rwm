# Claims-versus-evidence audit (C1)

One row per declarative claim in the paper. Claims are enumerated mechanically from
`PAPER.template.md` by `scripts/task_c1_claims_audit.py`; the verdict column is the
only judgement, and is keyed to the claim's text so that rewording a claim resets it
to UNREVIEWED rather than carrying a stale verdict forward.

**62 claims.** OVERSTATED: 3, SUPPORTED: 52, UNREVIEWED: 6, UNSUPPORTED: 1

| # | § | claim | backed by | verdict |
|---|---|---|---|---|
| 1 | Abstract | The base paper's central claim reproduces, and by a wide margin: trained autoregressively, the model reaches normalised error {{m23_A}} at a 368-step … | `task5_analysis.json` | **OVERSTATED** |
| 2 | Abstract | The aleatoric σ is **{{cal_rel_ratio}}× smaller than its own mean absolute error** ({{cal_rel_cov1}}% coverage at ±1σ against a calibrated 68.3%), and… | `task1_calibration.json` | **SUPPORTED** |
| 3 | Abstract | Running the correction — the authors' own unused `gaussian_nll` branch — fails differently rather than succeeding, at {{cal_nll_ratio}}× overconfidenc… | `task1_calibration.json` | **SUPPORTED** |
| 4 | Abstract | The epistemic term, the one the method actually consumes, is two orders of magnitude better and still **{{b2_epi_ratio_h368}}× overconfident at the de… | `task_b2_epistemic.json` | **SUPPORTED** |
| 5 | Abstract | The teacher-forced arm has the most input-dependent σ ({{cal_armB_over_faithA_cov}}× the autoregressive arm's) and the strongest σ-versus-error orderi… | `task1_calibration.json` | **SUPPORTED** |
| 6 | Abstract | We also report four defects in the released pipeline, evidence that the released checkpoint cannot have come from the released recipe, and {{n_retract… | `FINDINGS_LEDGER.md` | **SUPPORTED** |
| 7 | 1. Introduction | A world model that reports its own uncertainty is more useful than one that does not, and the uncertainty-aware Robotic World Model reports one. | — | **SUPPORTED** |
| 8 | 1. Introduction | But the same rebuild made a second question cheap to ask, because we had a from-scratch model, the released checkpoint, and a harness that could score… | — | **OVERSTATED** |
| 9 | 1. Introduction | We rebuilt rather than imported.** The forward pass, the loss and the training step are written from scratch and then checked against the reference: o… | `step4_3_differential.json` | **SUPPORTED** |
| 10 | 1. Introduction | We retract our own findings when they fail.** {{n_retractions_word}} claims in this work are withdrawn on evidence this project produced, and the retr… | `FINDINGS_LEDGER.md` | **SUPPORTED** |
| 11 | 2. Setup | Data.** The released dataset is {{rows}} rows of ANYmal D proprioceptive state and policy actions at 50 Hz. | `step0_regimes.json` | **SUPPORTED** |
| 12 | 2. Setup | The reference window builder therefore marks all {{win_naive}} windows valid, including {{win_cross}} that splice one episode's end onto the next one'… | `step0_regimes.json` | **SUPPORTED** |
| 13 | 2. Setup | The usable, episode-respecting count is {{win_usable}} — {{rows}} rows, less {{win_tail}} that cannot start a full window, less {{win_cross}} that cro… | `step0_regimes.json` | **SUPPORTED** |
| 14 | 2. Setup | The contamination rate is {{contam_pct}}%. | `step0_regimes.json` | **SUPPORTED** |
| 15 | 2. Setup | The paper describes two loss terms; the implementation has {{diff_terms}}. | `step4_3_differential.json` | **SUPPORTED** |
| 16 | 2. Setup | Two 400-step trajectories whose spans overlap are not independent evidence, and the out-of-sample arena contains only {{m23_nind}} mutually non-overla… | `task5_analysis.json` | **SUPPORTED** |
| 17 | 3. The base paper's centra | Three conditions, all required: the out-of-sample gap at h = 368 excludes zero under a bootstrap over independent trajectories; the sign is consistent… | — | **SUPPORTED** |
| 18 | 3. The base paper's centra | Result.** Every condition {{m23_c1}}. | `task5_analysis.json` | **SUPPORTED** |
| 19 | 3. The base paper's centra | The sign test, which does not depend on n.* At h = 368 the per-episode gap favours autoregressive training on **{{c3_sign_pos}} of {{c3_sign_n}}** epi… | `task_c3_multiplicity.json` | **UNREVIEWED** |
| 20 | 3. The base paper's centra | The in-sample arena, where the sample is larger.* The same comparison on the eight training episodes has {{ab_long_cells}}× more independent trajector… | `review_bootstrap_unit.json` | **UNREVIEWED** |
| 21 | 3. The base paper's centra | The out-of-sample effect size, reported last and with its limitation stated.* Autoregressive training reaches **{{m23_A}}** against teacher forcing's … | `task5_analysis.json` | **UNREVIEWED** |
| 22 | 3. The base paper's centra | That interval should not be read as an ordinary one:** four trajectories admit {{c3_resamples}} distinct resamples, so any bootstrap tail is quantised… | `task_c3_multiplicity.json` | **UNREVIEWED** |
| 23 | 3. The base paper's centra | What does not hold, and we say so.** At h = 8 — the horizon the model is trained on — the same comparison out-of-sample gives a gap of {{m23_h8_gap}} … | `task5_analysis.json` | **SUPPORTED** |
| 24 | 3. The base paper's centra | Under the correct cluster bootstrap, the out-of-sample gap excludes zero in **{{ab_long_excl}} of {{ab_long_cells}}** long-horizon cells — both trajec… | `review_bootstrap_unit.json` | **SUPPORTED** |
| 25 | 3. The base paper's centra | Multiplicity.** Those {{ab_long_cells}} cells sit in a family of {{c3_family}} out-of-sample comparisons, so we state the correction rather than leavi… | `review_bootstrap_unit.json`, `task_c3_multiplicity.json` | **UNREVIEWED** |
| 26 | 3. The base paper's centra | All {{c3_bonf_excl}} of {{c3_long}} still exclude zero at a Bonferroni level of 0.05/{{c3_family}}, and Holm–Bonferroni rejects **{{c3_holm_rejected}}… | `task_c3_multiplicity.json` | **UNREVIEWED** |
| 27 | 4.2 The measurement | Every model is overconfident by between one and four orders of magnitude (Figure 1). | — | **OVERSTATED** |
| 28 | 4.2 The measurement | The quantity the method does use is also uncalibrated.** On the released {{b2_members}}-member checkpoint, out-of-sample, n = {{b2_nind}} independent … | `task_b2_epistemic.json` | **SUPPORTED** |
| 29 | 4.2 The measurement | Epistemic is two orders of magnitude better than aleatoric — {{b2_epi_over_alea_h1}}× larger at h=1, {{b2_epi_over_alea_h368}}× at h=368 — and still w… | `task_b2_epistemic.json` | **SUPPORTED** |
| 30 | 4.2 The measurement | The scalar penalty as actually applied — `means.std(0).sum(-1)` at `envs/base.py:166` — correlates {{b2_penalty_corr}} with total absolute error over … | `task_b2_epistemic.json` | **SUPPORTED** |
| 31 | 4.3 Why the aleatoric head | Across all {{n_runs}} runs the collapse is linear in iteration count and its rate is nearly identical (Figure 3a). | ` directory listing` | **SUPPORTED** |
| 32 | 4.4 The correction fails d | Running it reverses the collapse and improves the magnitude from {{cal_faithA_ratio}}× to {{cal_nll_ratio}}× overconfident. | `task1_calibration.json` | **SUPPORTED** |
| 33 | 4.4 The correction fails d | It does not produce a usable estimate, and it destroys something the faithful arm had: the σ-versus-error ordering falls from {{cal_faithA_npos}}/{{ca… | `task1_calibration.json` | **SUPPORTED** |
| 34 | 4.5 The failure is one of  | Arm B's σ is {{cal_armB_over_faithA_cov}}× more input-dependent than the faithful arm's, and its ordering is the strongest of the four by a wide margi… | `task1_calibration.json` | **SUPPORTED** |
| 35 | 4.5 The failure is one of  | It is still {{cal_armB_ratio}}× overconfident. | `task1_calibration.json` | **SUPPORTED** |
| 36 | 4.5 The failure is one of  | The same pattern holds for the quantity the method uses, with the strongest evidence in this paper.** At h=128 and h=368 the epistemic term correlates… | `task_b2_epistemic.json` | **SUPPORTED** |
| 37 | 4.5 The failure is one of  | And it fails the horizon test the same way: σ grows {{b2_epi_sigma_growth}}× from h=1 to h=368 while error grows {{b2_epi_err_growth}}×. | `task_b2_epistemic.json` | **SUPPORTED** |
| 38 | 4.6 The structural excuse  | The faithful arm's σ *declines* ({{sig_faithA_growth}}×) while its error grows {{err_faithA_growth}}×. | `task2_sigma_profile.json` | **SUPPORTED** |
| 39 | 5. Defects in the released | The window builder reads a termination column that is identically zero, so it marks all {{win_naive}} windows valid. | `step0_regimes.json` | **SUPPORTED** |
| 40 | 5. Defects in the released | Scored correctly the released checkpoint is materially better than its own released evaluation reports. | — | **UNSUPPORTED** |
| 41 | 5. Defects in the released | 5.4 What the spliced windows cost: nothing measurable.** We trained a contaminated arm on {{arm_contam_windows}} windows — the clean {{arm_clean_windo… | `step5_armA_seed0.json`, `step5_armA_seed0_contam.json` | **SUPPORTED** |
| 42 | 5. Defects in the released | The arm's contamination rate is {{arm_contam_pct}}%, against the reference pipeline's {{contam_pct}}%. | `step0_regimes.json`, `step5_armA_seed0_contam.json` | **SUPPORTED** |
| 43 | 5. Defects in the released | It is deliberately lower: we splice only the {{bound_both_train}} boundaries whose *both* sides are training episodes, because {{bound_touch_holdout}}… | `step5_armA_seed0.json (split)` | **SUPPORTED** |
| 44 | 5. Defects in the released | That is a leakage problem rather than a physics one, and including it would have invalidated our own comparison. | — | **SUPPORTED** |
| 45 | 5. Defects in the released | Training loss over the final 250 iterations: duplication costs {{dup_cost_pct}}%, splicing costs {{contam_cost_pct}}%. | `task3_control_arm.json` | **SUPPORTED** |
| 46 | 5. Defects in the released | The bootstrap interval on duplicated − clean is [{{dup_ci_lo}}, {{dup_ci_hi}}], including zero. | `task3_control_arm.json` | **SUPPORTED** |
| 47 | 5. Defects in the released | In rollout, across {{tw_cells}} cells (two arenas × two trajectory lengths × two checkpoints × two horizons × two metrics), contamination hurts in **{… | `task3_three_way.json` | **SUPPORTED** |
| 48 | 5. Defects in the released | The control is inert, differing from clean in {{tw_dc_cluster_helped}} cells. | `task3_three_way.json` | **SUPPORTED** |
| 49 | 6. The released checkpoint | Fitting it across our runs and extrapolating to the released checkpoint's σ state implies **{{implied_iters}}** optimisation steps at the configured l… | `step6_analysis.json` | **SUPPORTED** |
| 50 | 6. The released checkpoint | The refit from our 10,000-iteration runs gives {{q4_implied_A}} and {{q4_implied_B}}, spreading {{implied_spread_pct}}% across the three fits — a line… | `task5_analysis.json`, `step6_analysis.json` | **SUPPORTED** |
| 51 | 7. Method | An append-only ledger.** Every claim in this work has a permanent identifier, an evidence class (source, data, run, external, inference) and a status,… | `FINDINGS_LEDGER.md` | **SUPPORTED** |
| 52 | 7. Method | Figure 4 shows the lead time for each, computed from commit timestamps: the A/B rule by {{lead_m16}}, the flip-pattern rule by {{lead_flip}}, the diff… | `paper_figures.json` | **SUPPORTED** |
| 53 | 7. Method | The rule for the duplication control (§5.4) was stated in conversation before the runs but reached git **{{lead_task3}} after the runs finished**, and… | `paper_figures.json` | **SUPPORTED** |
| 54 | 7. Method | {{n_retractions_word}} retractions on our own evidence**, out of {{n_superseded}} superseded claims kept in the record. | `FINDINGS_LEDGER.md` | **SUPPORTED** |
| 55 | 7. Method | The pre-registration claim above retracts a framing rather than a number and is counted separately. | — | **SUPPORTED** |
| 56 | 7. Method | Resampling trajectories correctly — carrying all seeds with each draw — widens intervals by a mean factor of {{bu_mean_ratio}}× (range {{bu_min_ratio}… | `review_bootstrap_unit.json` | **SUPPORTED** |
| 57 | 7. Method | Reproducibility.** `./reproduce.sh --quick --force` regenerates {{ver_files}} artifact files and {{ver_values}} numeric values from a clean clone, {{v… | `verify_reproduction.json` | **SUPPORTED** |
| 58 | 8. Limitations | Effective sample size bounds every long-horizon claim.** The out-of-sample arena has {{m23_nind}} independent 400-step trajectories. | `task5_analysis.json` | **SUPPORTED** |
| 59 | 9. Conclusion | The aleatoric σ is {{cal_rel_ratio}}× smaller than its own error, and the cause is that the objective's optimum is σ = 0 with the term that should pre… | `task1_calibration.json` | **SUPPORTED** |
| 60 | 9. Conclusion | The epistemic term the method actually penalises with is better by two orders of magnitude and still {{b2_epi_ratio_h368}}× overconfident where it is … | `task_b2_epistemic.json` | **SUPPORTED** |
| 61 | 9. Conclusion | The more useful finding is that ranking survives where scale does not, in both components. | — | **SUPPORTED** |
| 62 | 9. Conclusion | The teacher-forced arm has input-dependent σ and good ordering; the epistemic term ranks better still, at {{b2_epi_npos_h368}} of {{b2_epi_ndim_h368}}… | `task_b2_epistemic.json` | **SUPPORTED** |
