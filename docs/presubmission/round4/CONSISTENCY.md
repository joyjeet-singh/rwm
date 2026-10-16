# Round 4, F10 item 5: front-matter consistency (PLAN §1.2 rule 11)

One row per sentence in the abstract, the contributions, Appendix D's two tables, §9, §11 and §12 that restates a
result. Sentences that state no result (method, motivation, scope) are not listed.

**How each row was checked.** Round 3's method is used (`round3/CONSISTENCY.md`).
- **Body anchor:** the section that states the result in full. Line numbers are those of `PAPER.md` as built after F10's fixes, the build committed beside this file.
- **Readings:** every reading the body reports for that result: arena, n_independent, horizon, metric, and its direction or verdict.
- **A reading** *agrees* if it resolves the summary's direction. It is *unresolved* if its interval spans zero or its rule returns CANNOT BE SETTLED, CANNOT BE DISTINGUISHED, PARTIAL or UNDER-POWERED. It *reverses* if it resolves the other way.
- **A summary** may claim a direction only where no reading reverses it, and must state any unresolved reading or the scope its readings resolve.

Rows for round 4's rules (X3, X4, X6, X7, X8) also carry their locked framing (workplan §3):
- X3 is the direction across folds, at 2,500 iterations;
- X4 matches size only;
- X6 is the short-unit h = 100 result, which does not settle h = 368;
- X7 is pooled epistemic coverage on a checkpoint that trained on all ten episodes;
- X8 covers four rules only.

## Abstract (300 words; C12.1 passes at 320)

| # | sentence (abridged) | body anchor | readings | agrees? |
|---|---|---|---|---|
| A1 | rebuilt …, matching the released code's outputs, losses and gradients | §3 (l. 186); Appendix A | outputs bitwise; losses and gradients to 0.000e+00 over 7 terms and 106 tensors | agrees |
| A2 | central claim reproduces under a rule committed in advance (seed 1): over 3 seeds … 4.61× at 368 steps, though not at one step on short windows | §5 (l. 304–372) | M-23 (seed 1, held-out pair, 4, h = 368): every condition holds. 3 seeds at 10,000: gap excludes zero at h = 8–368, spans it at h = 1 (400-step unit); sign test 10 of 10 at h = 368 and 100, 3 of 10 at h = 1. M-64's 33-row units (60): h = 1 gap excludes zero for teacher forcing | agrees: the one-step reversal is stated, on its unit |
| A3 | Retrained on fixed folds holding out each episode once (2,500 iterations, not 10,000), its direction REPLICATES ACROSS FOLDS (20 trajectories) | §5 (l. 384–389); Appendix L | X3, all ten episodes (20), h = 368: gap +2.2275 [+1.3683, +3.5053]; 10 of 10 episodes; every fold's interval above zero; h = 100 alongside replicates; h = 1 on short units teacher forcing leads (stated in A2) | agrees; X3 framing held (direction, iterations stated) |
| A4 | At 368 steps RWM beats MLP, RSSM and transformer baselines …, all worse than predicting no change; matched only in size, the transformer is unresolved (PARTIAL) | §5.3 (l. 495–540) | M-75 REPRODUCES and M-76 RWM AHEAD OF ALL THREE at h = 368 (held-out, 4); below h = 32 / h = 128 readings split (outside "at 368 steps"); every baseline above the floor at h = 368. X4: MLP RWM BETTER, transformer CANNOT BE SETTLED at 368, 100 and 32 | agrees; X4 framing held ("matched only in size") |
| A5 | two shorter histories and both longer training forecasts beat the original's setting at our budget, no reading favouring it; trained longer, it passes each on some reading (post hoc): the ranking depends on training budget | §5.2 (l. 437–466); Appendix U | M-74 NOT OPTIMAL (held-out, 4, h = 368, Holm); per configuration no reading puts the centre ahead of any winner (several unresolved); at 5,000 the readings split, at 10,000 the centre passes each on at least one reading | agrees (C26.1, C28.3) |
| A6 | Magnitudes rest on 4 held-out trajectories, 0.133% of the reference's data, one robot, gait and terrain | §3, §5.1, §11 | as stated | agrees |
| A7 | uncertainty gets the order right and the size wrong: disagreement correlates +0.605 with error but is 33.4× too small at 100 steps on training data | §6.2 (l. 590–636); §6.6 | released, all ten (20): scalar r = +0.605 [+0.545, +0.694]; epistemic 33.4× [28.7, 39.0] at h = 100, overconfident at every horizon; per-dimension ordering not established after correction (§6.5), not restated here | agrees (the scalar; §12 names the per-dimension caveat) |
| A8 | Predicted step size ranks error nearly as well over whole trajectories, worse on shorter units at 100 steps | §6.6 (l. 808–826) | M-51/52: +0.4697 against +0.6053, margin below the MDE at h = 368 (20), SURVIVES entry-res ONLY; X6: 70 units, h = 100, margin +0.2816 [+0.1978, +0.3896], the checkpoint's training data | agrees; X6's two scopes stated |
| A9 | Members share 89.15% of parameters; independent models are 2.03× better calibrated, still overconfident | §6.4; §6.8 (l. 896–920) | M-44 (held-out, 4, h = 100, 2,500 iterations): MECHANISM SUPPORTED, 2.03× against MDE 1.45×; still 5.2×; M-49 at matched capacity: same direction, every paired interval excludes zero, 1.79× below its MDE 2.00× (UNDER-POWERED) | agrees in direction; the capacity bound is in contribution 5 and §6.8, not the abstract (as in round 3, A9) |
| A10 | The implemented loss provably drives the discarded per-member σ to zero | §6.3 (l. 643–667) | derivation; M-50 OBJECTIVE-DRIVEN | agrees |
| A11 | Per-horizon rescaling brings the released checkpoint's coverage within 10 points … for disagreement at every horizon on training episodes left out of each fit; on episodes our ensembles never saw, only 17 of 36 cells | §6.7 (l. 852–882) | X7, released, all ten (20), epistemic: WITHIN BAND AT 6 OF 6; aleatoric alongside 3 of 6 (abstract scoped "for disagreement"); two-episode version 12/12, unpowered; Arm A (held-out, 2,500): 17 of 36 epistemic | agrees; X7 framing held ("training episodes left out of each fit") |
| A12 | The released evaluation is one step stale; over all ten episodes this raises the checkpoint's short-horizon relative-L1 error | §7.2 (l. 932–947) | all ten (20), relative-L1: rise resolved at h = 1, 8, 32; unresolved from h = 100. nRMSE: resolved at 8 and 32, not at 1. Held-out pair (4): rises at every horizon | agrees (metric and horizon named; C27.1, C25.2) |
| A13 | We train no policy: we bound what the uncertainty reports, not its cost | §11 | scope | agrees |

## Contributions (8 bullets, each at most 3 sentences)

| # | sentence (abridged) | body anchor | readings | agrees? |
|---|---|---|---|---|
| C1a | order right, size wrong, the first calibration measurement we know of for this checkpoint | §2, §6.2 | as A7 | agrees |
| C1b | correlating +0.419 with rollout and depth held fixed; 8.3× at h = 1 and 33.4× at h = 100 on training data | §6.6 (l. 791–798); §6.2 | M-45 pooled r_dd +0.419 [+0.318, +0.576] (20): DISAGREEMENT CARRIES WITHIN-ROLLOUT INFORMATION; per horizon not established at short horizon (Appendix N); ratios with intervals | agrees (the governing pooled reading, as in round 3) |
| C1c | beats 1 of the 2 free baselines; step size +0.4697 against +0.6053, unresolved at h = 368, while on 70 shorter units at h = 100 rule X6 finds disagreement ahead | §6.6 | as A8 | agrees; X6 scopes stated |
| C2a | a rule on seed 1 found 4.43× at h = 368; 3 seeds at 10,000: 4.61×, and 2.58× at h = 100, on the held-out pair's 4; retrained on fixed folds the direction replicates, +2.2275 [CI] at h = 368 over 20 trajectories at 2,500 iterations (X3) | §5 | as A2, A3 | agrees; X3 in contribution 2 (W11) |
| C2b | at one step a second rule, on 60 33-row units, finds teacher forcing ahead | §5 (l. 356–362) | as A2 | agrees |
| C3a | RWM ahead at h = 368 of the baselines, both regimes, though every baseline is worse than predicting no change; size-matched, the MLP stays behind and the transformer cannot be told apart (X4: PARTIAL; size is one axis); X1: NOT RESCUED BY THE SETTINGS TRIED | §5.3 | as A4; X1 Part A and Part C | agrees |
| C3b | four of eight neighbours beat (32, 8) … (no reading puts the centre ahead), but trained longer the centre passes each on at least one reading (post hoc) | §5.2 | as A5 | agrees |
| C4 | the implemented state loss is minimised at σ = 0 | §6.3 | as A10 | agrees |
| C5 | 89.15%; 5 independent models 2.03× better calibrated against MDE 1.45×, still 5.2× at h = 100; differ in capacity and data order, so this bounds the effect | §6.4, §6.8 | as A9 | agrees |
| C6a | one multiplier per horizon … near nominal where a global one does not, though no single cell is resolvable and the cells are unseen only by the multiplier; Arm A 17 of 36 | §6.7 | two-episode version 12/12 epistemic and aleatoric, unpowered; constant 2 of 12; Arm A 17 of 36 | agrees |
| C6b | fitted on nine, scored on the tenth, disagreement's coverage over all 20 trajectories within the band at every horizon (X7), again on episodes the checkpoint trained on | §6.7 (l. 869–878) | as A11 | agrees; X7 framing held |
| C7 | misaligned by one step; over all ten episodes raises relative-L1 up to h = 32, unresolved from h = 100; 55.0% [CI] at h = 1 …; on the held-out pair's 4 it raises it at every horizon | §7.2 | as A12 | agrees |
| C8 | reimplementation verified at the gradient level | Appendix A | as A1 | agrees |

## Appendix D, first table (the originals' claims; tested rows)

| # | row and verdict cell (abridged) | body anchor | readings | agrees? |
|---|---|---|---|---|
| D1 | RWM-AR outperforms RWM-TF: reproduces at long horizon; X3 REPLICATES ACROSS FOLDS (2,500, not 10,000); X8 SAME VERDICT for M-23 | §5; Appendices L, Z | as A2, A3; X8 on M-23's statistic | agrees |
| D2 | teacher forcing "poor": on the 400-step unit Arm B is worse than the floor at every horizon (on M-64's units only at the longest they reach); (32, 1) 6.35× the centre at h = 368 | §5 (l. 363–368); §5.2 | 400-step unit: B above the floor at every horizon; M-64's units: B beats it at h = 1, 8, 32 and 100 | agrees |
| D3 | (32, 8) optimal: NOT OPTIMAL AT OUR BUDGET; no reading puts the centre ahead; ranking depends on training length; X8 SAME VERDICT | §5.2; Appendices U, Z | as A5 | agrees |
| D4 | beats the baselines: REPRODUCES / RWM AHEAD OF ALL THREE at h = 368; from h = 32 and h = 128 every reading gives them, below that they split; every baseline worse than the floor; X1 NOT RESCUED | §5.3 | as A4 | agrees |
| D5 | epistemic "closely follows the trend": supported as a scalar ranking …, not the step-size counter over whole trajectories at h = 368, which on 70 shorter units at h = 100 it does beat (X6); 5 controls; weaker per dimension; not supported as a scale | §6.2, §6.5–§6.7 | as A7, A8, A11 | agrees; X6 scopes stated |
| D6 | aleatoric "remains low": the observation holds; the explanation does not | §6.2, §6.3 | the σ head orders of magnitude below error at every horizon | agrees |

## Appendix D, second table ("What each tested claim rests on")

Every row names its arena, n_independent and checkpoint. `check_comparative_claims` C24.1 confirms each arena and n
against its own section (20 of 20). The rows are generated by `scripts/evidence_summary.py`.

| # | row (abridged) | body anchor | readings | agrees? |
|---|---|---|---|---|
| E1 | AR beats TF at h = 368; out-of-sample (4); 10,000; gap excludes zero (X8: SAME VERDICT) | §5 | as A2 | agrees |
| E2 | reverses at h = 1 on M-64's unit; out-of-sample (60) | §5 | as A2 | agrees |
| E3 | X3; all ten episodes (20); 2,500; REPLICATES ACROSS FOLDS, 10 of 10 | §5 | as A3 | agrees |
| E4 | (32, 8) optimal; out-of-sample (4); 2,500; NOT OPTIMAL AT OUR BUDGET; no reading puts the centre ahead; ranking depends on training length (X8 SAME VERDICT) | §5.2 | as A5 | agrees |
| E5–E6 | baselines, teacher-forced and autoregressive; REPRODUCES / RWM AHEAD OF ALL THREE; every reading from h = 32 / h = 128, split below; every baseline worse than the floor at h = 368 | §5.3 | as A4 | agrees |
| E7 | size-matched; out-of-sample (4); 2,500; PARTIAL: MLP RWM BETTER, transformer CANNOT BE SETTLED | §5.3 | X4 | agrees |
| E8–E10 | disagreement smaller than error at h = 1 and 100; σ collapsed; all ten (20); released; ratio interval excludes 1 | §6.2 | as stated | agrees |
| E11 | beats the step index at h = 100; paired difference excludes zero | §6.6 | 5 of 5 index-defined horizons | agrees |
| E12 | better than step size over whole trajectories; SURVIVES entry-res ONLY | §6.6 | as A8 | agrees |
| E13 | X6, shorter units at h = 100; all ten (70); DISAGREEMENT BEATS STEP SIZE | §6.6 | X6 | agrees |
| E14 | rollout and depth held constant; interval excludes zero, clears the MDE | §6.6 | M-45 | agrees |
| E15 | per-horizon multiplier; held-out pair (4); released; within tolerance, unpowered; Arm A 17 of 36 | §6.7 | as C6a | agrees |
| E16 | X7; all ten (20); WITHIN BAND AT 6 OF 6 (disagreement); aleatoric 3 of 6 alongside | §6.7 | X7 | agrees |
| E17 | shares no trunk; out-of-sample (4); 2,500; MECHANISM SUPPORTED | §6.8 | M-44 | agrees |
| E18 | matched capacity; UNDER-POWERED | §6.8 (l. 912–916); Appendix R | M-49 | **fixed (F10)**: the row pointed to §11, which F8 moved to Appendix R; it now points to §6.8 |
| E19 | the combination; THE COMBINATION IMPROVES CALIBRATION | §6.8 | M-68 | agrees |
| E20 | stale pairing; all ten (20); raises error up to h = 32 on relative-L1; not resolved from h = 100 | §7.2 | as A12 | agrees |

## §9 Actionable lessons

| # | sentence (abridged) | body anchor | readings | agrees? |
|---|---|---|---|---|
| L1a | at one step +0.994 [CI] across the 20 trajectories; over the full rollout +0.605 [CI] | §6.6 | released, all ten (20) | agrees |
| L1b | beats the step index at every horizon tested, 5 of 5, retains +0.596 | §6.6 | as E11 | agrees |
| L1c | on whole trajectories not clearly beating step size, +0.4697 against +0.6053 below the 0.2891 MDE; on 70 shorter units at h = 100 X6 resolves it, training data only; h = 368 not re-tested; retains +0.5430; +0.419 with depth and rollout held | §6.6 | as A8 | agrees; X6 scopes stated |
| L1d | 33.4× [CI] over all ten; on the held-out pair 10.5× [CI] on the ensemble-5 arms against the released checkpoint's 25.7× | §6.2 (l. 627–633); Appendix M | 25.7× has no interval in `results/task_b2_epistemic.json`. The arms' interval [9.0, 11.5] excludes it | agrees (REVIEW.md, observation O1) |
| L2 | per horizon within 10 points, no cell resolvable; X7 within the band at every horizon; a global multiplier 2 of 12; Arm A 17 of 36; multipliers span 9.31× | §6.7 | as A11, C6a | agrees |
| L3 | the independent-trials null wrong by up to 10^13× | §6.5; Appendix K | binomial against permutation P | agrees |
| L4 | 4 independent 400-step trajectories bound every long-horizon magnitude, though §5's direction is re-tested on all ten (X3); pooled resampling narrows by 1.42× | §3, §5, §8 | as A3 | agrees |
| L5 | the first rule, anchored at h = 8, returned CANNOT BE SETTLED AT THIS BUDGET | §5; Appendix E | M-16 | agrees |
| L6 | 7 loss terms; σ 11,683× at h = 100 and 20,669× at h = 368 | §6.2, §6.3 | released, all ten (20) | agrees |

## §11 Limitations

| # | sentence (abridged) | body anchor | readings | agrees? |
|---|---|---|---|---|
| M1 | what this study cannot address (O13): one robot, gait and terrain; no policy; 0.133%; no held-out arena for the released checkpoint | §3, §5.1, §7.3 | scope | agrees |
| M2 | the headline magnitudes rest on 4 independent trajectories; the direction is re-tested on all ten (X3) | §3, §5 | as A3 | agrees |
| M3 | step size ranks error nearly as well at h = 368 (20); settling it needs 25; X6 finds disagreement ahead at h = 100 on 70 units of training data; h = 368 not re-tested | §6.6; Appendices R, X | as A8 | agrees |
| M4 | 33.4× at h = 100; X5 not run (no recorded velocity command); M-70 DOES NOT REORDER, none of 6 pairs, a proxy of the penalty alone, partly structural null, degenerate interval | §6.2; Appendices R, W | as stated | agrees (F10 added X5's reason) |
| M5 | 28 rules, none corrected family-wide; one withdrawn as a pre-registration | Appendix E; §8 | as stated | agrees |
| M6 | other PETS descendants untested | §2; Appendix I | as stated | agrees |

## §12 Conclusion

| # | sentence (abridged) | body anchor | readings | agrees? |
|---|---|---|---|---|
| K1 | the central claim reproduces at long horizons …, though teacher forcing leads at one step on the short windows built for it | §5 | as A2 | agrees |
| K2 | RWM ahead at h = 368 of the baselines, none beating no change; size-matched, the transformer cannot be told apart (X4: PARTIAL) | §5.3 | as A4 | agrees |
| K3 | four other lengths beat its chosen ones at our budget, no reading putting the chosen ones ahead, in a ranking that changes when the chosen setting trains longer | §5.2 | as A5 | agrees |
| K4 | at h = 100 the aleatoric σ 11,683× …; the epistemic 349× better and still 33.4× [CI], on the 20 trajectories of the checkpoint's training episodes | §6.2 | as stated | agrees |
| K5 | ranking survives: beats the step index at every horizon and, rollout and depth held, +0.419 [CI]; step size nearly as well, unresolved at h = 368 (SURVIVES entry-res ONLY); on 70 shorter units at h = 100 disagreement ahead (X6) | §6.6 | as A8, E11, E14 | agrees; X6 scopes stated |
| K6 | scale may be repairable per horizon on the released checkpoint (X7 6 of 6), mixed on a model that never saw the test episodes; per dimension nothing survives correction | §6.5, §6.7 | as A11 | agrees |
| K7 | what should travel: the objective's property, a hypothesis §2 leaves untested elsewhere; the artifact's properties to check; the dataset's limits | §2, §6.3, Appendix S | as stated | **fixed (F8 review)**: the hypothesis qualifier, which F8's summary had dropped, is restored |

## What changed in F10, and what did not

- **Fixed (F10):** E18, whose pointer to §11 F8 had left stale; it now points to §6.8 (`scripts/evidence_summary.py`). M4 gained X5's reason, which is wording only.
- **Recorded, not changed:** L1d's 25.7× has no interval in its artifact, and computing one would be a new measurement (REVIEW.md, observation O1).
- **No sentence claims a direction that a reading reverses.** Every unresolved reading is stated or scoped, and the locked framing for X3–X8 holds in every row that summarises them.
