# Claims-to-evidence map

One row per CONTRIB ledger entry.

| ID | Claim | Evidence | Status | Artifacts |
|---|---|---|---|---|
| `D-03` | The termination column is identically zero | `DATA` | CONFIRMED | — |
| `D-04` | Ten unmarked episode boundaries | `DATA` | CONFIRMED | — |
| `D-06` | Usable window count | `DATA` | CONFIRMED | `results/step0_regimes.json`, `scripts/step0_velocity_regimes.py` |
| `D-07` | Actions are not joint targets in radians | `DATA`, `SRC` | CONFIRMED | — |
| `D-10` | Twenty-one commanded-velocity regime segments, not one | `DATA`, `EXT` | CONFIRMED | `results/step0_report.txt` |
| `D-12` | Per-episode difficulty varies threefold and is not explained by speed | `RUN` | CONFIRMED | — |
| `D-13` | Row *t* holds the action that **produced** state[*t*] (k = −1) | `DATA`, `EXT`, `INFER`, `SRC` | CONFIRMED | — |
| `B-01` | The window builder cannot see the episode resets | `DATA`, `SRC` | CONFIRMED | — |
| `B-02` | Latent falsy-index bug in the same guard | `SRC` | CONFIRMED | — |
| `B-03` | Train/test split leaks | `SRC` | CONFIRMED | — |
| `B-04` | Evaluation trajectories are drawn from training data | `RUN`, `SRC` | CONFIRMED | — |
| `B-05` | Training and evaluation use different action alignments | `SRC` | CONFIRMED | — |
| `C-01` | The loss has seven terms, not two | `SRC` | CONFIRMED | — |
| `C-02` | The mean head is residual | `SRC` | CONFIRMED | — |
| `C-03` | Two GRU trunks, not one | `SRC` | CONFIRMED | — |
| `C-04` | The "ensemble of 5" shares both trunks | `SRC` | CONFIRMED | — |
| `C-05` | Training samples, inference takes the mean | `SRC` | CONFIRMED | — |
| `C-06` | Learnable bounded log-standard-deviation | `SRC` | CONFIRMED | — |
| `C-07` | Actions are not normalised | `SRC` | CONFIRMED | — |
| `C-09` | There is no forecast decay factor in the implementation at all | `SRC` | CONFIRMED | — |
| `C-10` | The aleatoric variance head has collapsed to a constant | `DATA`, `SRC` | CONFIRMED | — |
| `C-11` | `state_min_logstd` receives no gradient from the bound loss | `RUN`, `SRC` | CONFIRMED | — |
| `C-12` | The released checkpoint's collapse implies ~155,000 iterations, not 500 or 2500 | `RUN`, `SRC` | CONFIRMED | — |
| `C-13` | Three different iteration counts are in play | `DATA`, `EXT`, `SRC` | CONFIRMED | — |
| `C-14` | The method penalises EPISTEMIC uncertainty; the aleatoric head is discarded before use | `EXT`, `SRC` | CONFIRMED | — |
| `C-15` | Eq. 4 defines the penalty on variance; the code computes a standard deviation | `EXT`, `SRC` | RESOLVED — the code is intended | — |
| `M-02` | The hold-last floor is the zero-delta model | `INFER`, `RUN` | **CONFIRMED** (was PENDING VERIFICATION) | — |
| `M-04` | Ten trajectories is not enough to support a gap claim | `RUN` | CONFIRMED | — |
| `M-13` | The auxiliary branch is teacher-forced; the state branch is not | `SRC` | CONFIRMED | — |
| `M-17` | nRMSE is a TAIL statistic and is biased low at small n; relative-L1 is not | `RUN` | CONFIRMED | `results/task3b_convergence.json` |
| `M-19` | Aggregating nRMSE as a mean of per-dimension ratios is wrong when scales span decades | `RUN` | CONFIRMED (aggregation); Jensen mechanis | `results/taskAB_gate_r27.json` |
| `M-20` | Effective sample size, and what actually drives long-horizon verdicts | `RUN`, `SRC` | CONFIRMED | `results/batch1_post_retraction.json`, `src/rwm_metrics.py` |
| `M-24` | A pre-registered rule must be anchored to the regime the claim is about | `RUN`, `SRC` | CONFIRMED | `results/task4_arenas.json` |
| `R-02` | Protocol A and B, clean | `RUN` | CONFIRMED | `results/manifest.json`, `results/step3_report.txt` |
| `R-03` | Hold-last floor | `RUN` | CONFIRMED | `results/step2_acceptance.json` |
| `R-04` | Error by forecast horizon, protocol A clean | `RUN` | CONFIRMED | `results/step3_report.txt` |
| `R-05` | Boundary crossing does not inflate error | `RUN` | CONFIRMED | `results/step3_report.txt` |
| `R-06` | Convention swap is worth 0.066 | `RUN` | CONFIRMED | `results/step3_report.txt` |
| `R-07` | Protocol B's noise sweep is non-monotonic | `RUN` | CONFIRMED | `results/step3_report.txt` |
| `R-08` | Epistemic uncertainty dwarfs aleatoric | `RUN` | CONFIRMED as a measurement | `results/step3_report.txt` |
| `R-09` | Error by forecast horizon under the causal convention | `RUN` | CONFIRMED | `results/task2_4_results.json` |
| `R-15` | Step 3 results restated under the causal convention | `RUN` | SUPERSEDED IN PART by S-09 — the numbers | — |
| `R-17` | Overfit one batch: partial, and the collapse prediction confirmed | `RUN` | CONFIRMED (collapse) | `figures/step4_overfit_ens1.png` |
| `R-19` | Arm A (autoregressive, faithful), seed 0 | `RUN` | CONFIRMED | `results/step5_armA_seed0.json`, `results/step5_armA_seed0_report.txt` |
| `R-20` | The two metrics disagree in DIRECTION at h=1 | `RUN` | CONFIRMED | `results/step5_armA_seed0.json` |
| `R-22` | The paper's central claim REPRODUCES: autoregressive beats teacher forcing | `RUN` | CONFIRMED as measurements under the refe | `figures/step6_arms_comparison.png`, `results/step6_analysis.json` |
| `R-23` | Teacher forcing reaches a 3× lower training loss and a 4× worse rollout | `RUN` | CONFIRMED | `results/step6_analysis.json` |
| `R-24` | Pooled collapse fit across six independent runs | `RUN` | CONFIRMED | `results/step6_analysis.json` |
| `R-25` | `min_logstd` gives O-12 a second, slower, independent axis | `DATA`, `RUN`, `SRC` | CONFIRMED | `results/step6_3_min_logstd.json` |
| `R-26` | Neither arm has converged at the paper's own iteration count | `RUN` | CONFIRMED | `results/step6_analysis.json` |
| `R-28` | Re-evaluation at 100 trajectories: M-16 unchanged, M-04 revised | `RUN` | CONFIRMED | `results/task3_4_power_ddof.json` |
| `R-29` | The released checkpoint loses on 7 of 45 dimensions, and one of them carries R-27 | `RUN` | CONFIRMED | `results/taskAB_gate_r27.json` |
| `R-30` | The "heavy tail" is two short regions, not a property of the model | `RUN` | CONFIRMED | `results/taskAB_gate_r27.json` |
| `R-31` | M-16 is robust to the aggregation choice | `RUN` | CONFIRMED | `results/taskAB_gate_r27.json` |
| `R-32` | The retraction's arithmetic, verified | `RUN` | CONFIRMED | `results/batch1_post_retraction.json` |
| `R-33` | The Jensen mechanism is SUPPORTED at 40 seeds | `RUN` | SUPPORTED | `results/batch1_post_retraction.json` |
| `R-34` | The released checkpoint characterised on all ten episodes, independent trajectories | `RUN` | CONFIRMED | `results/batch1_post_retraction.json` |
| `R-35` | M-16 re-evaluated in both arenas: CANNOT BE SETTLED, in all eight combinations | `RUN` | CONFIRMED | `results/task4_arenas.json` |
| `R-36` | The pre-registered teacher-forcing flip pattern FIRES, in the in-sample arena | `RUN` | CONFIRMED | `results/task4_arenas.json` |
| `R-37` | Per-episode A/B gap: sign-consistent at h=368, reverses at h=8 | `RUN` | CONFIRMED | `results/task4_arenas.json` |
| `R-38` | Long-horizon A/B figures from the existing six runs | `RUN` | CONFIRMED as measurements, NOT PRE-REGIS | `results/task4_arenas.json` |
| `R-39` | The h=368 magnitude rests on an episode-1 outlier; the direction does not | `RUN` | CONFIRMED | `results/task4_arenas.json` |
| `R-40` | M-23: the claim REPRODUCES AT LONG HORIZON | `RUN` | CONFIRMED | `results/task5_analysis.json` |
| `R-41` | A from-scratch model does NOT develop the released checkpoint's failure pattern | `RUN` | SUPERSEDED IN PART by S-11 and R-45 — th | `results/task5_analysis.json` |
| `R-42` | The A/B gap across five checkpoints: persists everywhere, resolves in-sample at h=8 | `RUN` | CONFIRMED | `results/task5_analysis.json` |
| `R-43` | The collapse rate stays linear to 10,000; the pre-registered prediction lands | `RUN` | CONFIRMED | `results/task5_analysis.json` |
| `R-44` | The central claim's full history, with commit timestamps | `RUN` | CONFIRMED | `results/task5_analysis.json` |
| `R-45` | Matched per-dimension comparison: released checkpoint vs Arm A | `RUN` | CONFIRMED | `results/task2_3_matched_trend.json` |
| `R-46` | The gap-narrowing trend: absolute gap closes, relative advantage does not | `RUN` | CONFIRMED | `results/task2_3_matched_trend.json` |
| `R-47` | The spliced windows cost nothing measurable, and if anything help | `RUN` | CONFIRMED | `results/task4_contamination.json` |
| `R-48` | The corrected objective reverses the collapse mechanism but produces no usable uncertain | `RUN` | CONFIRMED | `results/task1_calibration.json` |
| `R-49` | The released checkpoint's uncertainty output is worthless, quantified | `RUN` | SUPERSEDED IN PART by S-14 — the numbers | `results/task1_calibration.json` |
| `R-50` | Under `gaussian_nll` the released checkpoint's variance state is unreachable at any iter | `RUN` | CONFIRMED | `results/task1_calibration.json` |
| `R-51` | All four models are catastrophically overconfident | `RUN` | CONFIRMED | `results/task1_calibration.json`, `results/task2_sigma_profile.json` |
| `R-53` | The correction improved magnitude and destroyed what ordering signal existed | `RUN` | CONFIRMED | `results/task1_calibration.json` |
| `R-54` | σ is flat *inside* the trained horizon, which removes the structural excuse | `RUN` | CONFIRMED | `results/task2_sigma_profile.json` |
| `R-55` | The duplication control: R-47's mechanism survives, its statistic does not | `RUN` | CONFIRMED | `results/task3_control_arm.json` |
| `R-56` | The three-way comparison: the control is inert, contamination still costs nothing | `RUN` | CONFIRMED | `results/task3_three_way.json` |
| `R-57` | All four models, measured on one table | `RUN` | CONFIRMED | `results/task1_calibration.json`, `scripts/task1_calibration.py` |
| `R-58` | The uncertainty the method actually uses is also uncalibrated | `RUN` | CONFIRMED | `results/task_b2_epistemic.json` |
| `R-59` | One scalar cannot fix it, and the way it fails is the horizon | `RUN` | CONFIRMED | `results/task_d2_recalibration.json` |
| `R-60` | The headline over three seeds | `RUN` | CONFIRMED | `results/task_d1_threeseed.json`, `scripts/task_d1_threeseed.py` |
| `O-12` | The released checkpoint's variance collapse is inconsistent with the released configurat | `DATA`, `RUN`, `SRC` | OPEN — the discrepancy is measured and c | `results/step4_4_overfit_b32lr1e3.json`, `results/step4_4_overfit_ens1.json` |
