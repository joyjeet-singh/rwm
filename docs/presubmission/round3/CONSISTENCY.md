# Round 3, R6 item 3 — front-matter consistency (rule 10)

One row per sentence in the abstract, the contributions, Appendix D's two tables, §9, §11 and §12 that restates a
result. Sentences that state no result (method, motivation, scope, the untested claims' rows) are not listed.

**How each row was checked.** The body anchor is the sentence or table in §§1–8 or an appendix other than D that
states the result in full; line numbers are `PAPER.md`'s at commit R6 item 3. The readings are every reading the body
reports for that result: arena, n_independent, horizon, metric, and the direction or verdict of each. A reading
*agrees* if it resolves the summary's direction. It is *unresolved* if its interval spans zero or its rule returns
CANNOT BE SETTLED, CANNOT BE DISTINGUISHED or PARTIAL. It *reverses* if it resolves the other way. A summary may claim a
direction only where no reading reverses it. Where a reading is unresolved, the summary must say so or name the scope
(metric, unit, horizon) that its readings resolve.

**Verdict column.** *Agrees*: same arena, sample size, horizon, metric and direction, and no stronger than the body.
*Fixed (R6)*: the wording was changed in this session so that it agrees; the change is in `round3/r6_patch.py`, items 3
to 3d, and in `scripts/evidence_summary.py`.

Readings were taken from the artifacts named, through `paper_numbers.py` keys where the sentence prints them:
`mn_sweep_verdict.json` (M-74, every reading); `baselines_verdict.json` (M-75 and M-76, every reading; nRMSE as
`pooled_nrmse_alongside.json` pools it); `alignment_by_horizon.json`; `m64_short_units.json`; and §5's own readings.

## Abstract

| # | sentence (abridged) | body anchor | readings | agrees? |
|---|---|---|---|---|
| A1 | rebuilt …, matching the released implementation's outputs, losses and gradients exactly before training | Appendix A; contribution 8 (l. 89) | outputs bitwise; losses and gradients to 0.000e+00 over 7 terms and 106 tensors | agrees |
| A2a | under a rule committed in advance, run on seed 1 …; 3 seeds extend it: … 4.61× at 368 steps and 2.58× at 100 | §5 (l. 380–401; rule M-23 at l. 361) | held-out pair (4), relative-L1, 10,000 iterations: gap excludes zero at h = 368 and 100; sign test 10 of 10 at both; in-sample (16): same direction at every horizon and checkpoint but h = 8 at 500 iterations (l. 374–378) | agrees |
| A2b | though on short windows teacher forcing leads at one step | §5 (l. 412–419) | M-64's 33-row units (60), h = 1: gap excludes zero for teacher forcing; the 400-step unit (4), h = 1: gap spans zero, same sign; sign test 3 of 10, unresolved | **fixed (R6)**: it said "teacher forcing leads at one step" with no unit; the resolved reading is the short unit's |
| A3 | At 368 steps RWM beats MLP, RSSM and transformer baselines …, though each does worse than predicting no change | §5.3 (l. 574–587) | M-75 and M-76 at h = 368: every reading in both arenas and both metrics returns the verdict (`baselines_verdict.json`, pooled nRMSE); every baseline is above the hold-last floor at h = 368 on the held-out pair; the readings split only below h = 32 (teacher-forced) and h = 128 (autoregressive), outside the sentence's scope | agrees |
| A4a | On accuracy alone, two shorter histories and both longer training forecasts beat the original's setting at our budget (one reading unresolved) | §5.2 (l. 511–515); Appendix U | M-74 governing reading (held-out, h = 368, relative-L1, Holm): all four beat the centre; 16 other readings: 15 return NOT OPTIMAL, held-out nRMSE at h = 1 returns CANNOT BE DISTINGUISHED; Appendix U, 2,500 iterations: all four resolved in all four relative-L1 cells | **fixed (R6)**: the unresolved reading was not named |
| A4b | trained longer, it passes each on some reading (post hoc): the ranking depends on training budget | §5.2 (l. 525); Appendix U | at 5,000 the readings split for (32, 32) and (32, 16); at 10,000 the centre passes (2, 8) and (8, 8) on three of four readings | agrees |
| A5 | These rest on 0.133% of the reference's world-model data, … and 4 independent held-out trajectories | §5.1 (l. 466); §3 | 0.133%; held-out pair n_independent = 4 | agrees |
| A6 | The follow-up's uncertainty gets the order right and the size wrong. | §6.2, §6.6; §12 (l. 1322) | the scalar ranks error at every horizon (A7); overconfident at every horizon; per-dimension ordering unresolved after multiplicity correction (§6.5), a separate result the abstract does not restate | agrees: the next sentence names the scalar, and §12 says "as the scalar the method applies" |
| A7 | Ensemble disagreement … correlates +0.605 with realised error (+0.419 with rollout and depth held fixed), yet on the checkpoint's training data is 8.3× smaller … at one step and 33.4× at … 100 | §6.6 (l. 918–937); §6.2 (l. 682, 710) | released checkpoint, all ten episodes (20): r = +0.605 [+0.545, +0.694], partial +0.419 [+0.318, +0.576]; ratio intervals exclude 1 at h = 1 and 100 | agrees |
| A8 | A free signal, the model's predicted step size, ranks error nearly as well (+0.470; margin unresolved) | §6.6 (l. 982–999) | +0.4697 against +0.6053; margin below the MDE; SURVIVES entry-res ONLY | agrees |
| A9 | The members share 89.15% …; at 100 steps, independent models are 2.03× better calibrated …, still 5.2× overconfident | §6.4; §6.8 (l. 1085); §11 (l. 1289–1297) | M-44, held-out pair (4), h = 100: every condition met, MECHANISM SUPPORTED; M-49 at matched capacity: same direction, 1.79× against an MDE of 2.00× (a separate comparison the sentence does not restate) | agrees |
| A10 | The implemented loss provably drives the per-member σ … to zero, as data with known noise confirm | §6.3 (l. 746); Appendix J | derivation; rule M-50's synthetic-noise test | agrees |
| A11 | A per-horizon rescaling brings … within 10 points of nominal on its training episodes (no cell resolvable), and only 17 of 36 … on episodes our ensembles never saw | §6.7 (l. 1043–1060) | released, held-out pair: every point estimate within tolerance, none resolvable; Arm A's own multipliers: 17 of 36 epistemic cells | agrees |
| A12 | … over all ten episodes this raises the checkpoint's short-horizon relative-L1 error, and from 100 steps the change is unresolved | §7.2 (l. 1145–1165); `alignment_by_horizon.json` | all ten (20), relative-L1: rise resolved at h = 1, 8, 32; nRMSE: resolved at 8 and 32, unresolved at h = 1; from h = 100 neither metric resolves; held-out pair (4): rise resolved at every horizon in both metrics | **fixed (R6)**: it said "short-horizon error" with no metric; nRMSE does not resolve the rise at h = 1 |

## Contributions (8 bullets, at most 3 sentences each)

| # | sentence (abridged) | body anchor | readings | agrees? |
|---|---|---|---|---|
| C1 | correlating +0.419 …, 8.3× … at h = 1 and 33.4× at h = 100; beats 1 of the 2 free baselines; step size +0.4697 against +0.6053, a margin 25 trajectories would resolve | §6.2, §6.6, §11 (l. 1266–1269) | as A7 and A8; required sample 25 against 20 | agrees |
| C2a | A rule … on seed 1 … found autoregressive training ahead by 4.43× at h = 368; 3 seeds at 10,000 … 4.61×, and 2.58× at h = 100, on the held-out pair's 4 | §5 (l. 361, 380–401) | as A2a | agrees |
| C2b | At one step a second pre-registered rule, on 60 independent 33-row units, finds a gap … in favour of teacher forcing | §5 (l. 412–419) | as A2b; names the unit | agrees |
| C3a | RWM is ahead at h = 368 of MLP, RSSM and transformer baselines …, though every baseline is worse there than predicting no change, and … rule X1 … NOT RESCUED BY THE SETTINGS TRIED | §5.3 (l. 574–593) | as A3; X1's final reading | agrees |
| C3b | four of the eight one-factor neighbours … beat it, … (the rule's verdict holds on every reading it reports but held-out nRMSE at h = 1, which is unresolved), but trained longer the centre passes each … on at least one reading (post hoc) | §5.2 (l. 511–525); Appendix U | as A4a and A4b; cost per iteration 0.26×, 0.40×, 1.35×, 1.81× | **fixed (R6)**: the unresolved reading was not named |
| C4 | The implemented state loss is minimised at σ = 0 | §6.3 | as A10 | agrees |
| C5 | 89.15%; 5 independently initialised full models are 2.03× better calibrated …, against a pre-registered MDE of 1.45×, and still 5.2× overconfident at h = 100; … bounds the sharing effect | §6.4, §6.8, §11 | as A9 | agrees |
| C6 | One multiplier per horizon … brings every released-checkpoint coverage estimate near nominal …, though no single cell is resolvable …; on Arm A … 17 of 36 | §6.7 | as A11 | agrees |
| C7 | over all ten episodes it raises the checkpoint's relative-L1 error up to h = 32, and from h = 100 the change is not resolved; … 55.0% [26.3, 92.7] at h = 1 … on the held-out pair's 4 it raises it at every horizon reported | §7.2 (l. 1145) | as A12; names the metric (R3) | agrees |
| C8 | Outputs match … bitwise, and losses and gradients match to 0.000e+00 across 7 loss terms and 106 parameter tensors | Appendix A | as A1 | agrees |

## Appendix D, first table (the originals' claims; tested rows)

| # | row and verdict cell (abridged) | body anchor | readings | agrees? |
|---|---|---|---|---|
| D1 | RWM-AR consistently outperforms RWM-TF: **reproduces** at long horizon (§5) | §5 | held-out pair (4): gap excludes zero at h = 100 and 368; in-sample (16): the same direction at every horizon and checkpoint but h = 8 at 500 iterations; reversed at h = 1 on the short unit, outside "long horizon" | agrees |
| D2 | Teacher forcing gives "poor autoregressive performance": on the 400-step unit Arm B is worse than the hold-last floor at every horizon (on M-64's shorter units only at the longest they reach); (32, 1) is 6.35× the centre's error at h = 368 | §5 (l. 421–429); §5.2 | 400-step unit: Arm B above the floor at every horizon; M-64's units: below it at h = 1, 8, 32 and 100, above it only at 128 | **fixed (R6)**: it said "Arm B is worse than the hold-last floor" with no unit |
| D3 | M=32, N=8 optimal trade-off: **NOT OPTIMAL AT OUR BUDGET** on accuracy alone: (32, 32), (32, 16), (8, 8) and (2, 8) beat it at our budget (every reading its rule reports returns that verdict but held-out nRMSE at h = 1, which is unresolved), but the ranking depends on training length | §5.2; Appendix U | as A4a and A4b | **fixed (R6)**: the unresolved reading was not named |
| D4 | Beats MLP, RSSM and transformer baselines: **REPRODUCES** teacher-forced and **RWM AHEAD OF ALL THREE** autoregressively. Both are the rules' verdicts at h = 368; from h = 32 and h = 128 respectively, every reading the rules report gives them, and at shorter horizons they split | §5.3 (l. 574–587) | M-75: every reading in both arenas and both metrics returns REPRODUCES from h = 32; below it CANNOT BE SETTLED and PARTIAL, and in-sample pooled nRMSE at h = 1 returns DOES NOT REPRODUCE. M-76: every reading returns RWM AHEAD OF ALL THREE from h = 128; below it CANNOT BE SETTLED and PARTIAL, including in-sample pooled nRMSE at h = 100 | **fixed (R6)**: the verdicts were stated with no horizon, where the shorter horizons split and one reading reverses |
| D5 | Epistemic "closely follows the trend": supported as a scalar ranking … +0.605 …, beats the forecast-index counter at every horizon, not the step-size counter …, survives 5 controls … +0.419; weaker per-dimension; not supported as a scale: 33.4× at h = 100 … 17 of 36 cells | §6.2, §6.5, §6.6, §6.7 | as A7, A8 and A11; paired test excludes zero at 5 of 5 index-defined horizons (l. 929); per-dimension P not significant and no cell survives correction | agrees |
| D6 | Aleatoric "remains low": the observation holds; the explanation does not (§6.3) | §6.2, §6.3 | the σ head is orders of magnitude below realised error at every horizon | agrees |

## Appendix D, second table ("What each tested claim rests on")

Each row names its own arena, n_independent and checkpoint, so its scope is stated. Rows are generated by
`scripts/evidence_summary.py`.

| # | row (abridged) | body anchor | readings | agrees? |
|---|---|---|---|---|
| E1 | AR beats TF at h = 368; out-of-sample (4); 10,000; gap excludes zero | §5 | as A2a | agrees |
| E2 | reverses at h = 1, at the short unit M-64 built; out-of-sample (60) | §5 | as A2b; names the unit | agrees |
| E3 | (32, 8) optimal on accuracy alone; out-of-sample (4); 2,500; NOT OPTIMAL AT OUR BUDGET; 4 of 8 neighbours beat the centre; every other reading the rule reports returns the same verdict but held-out nRMSE at h = 1, which is unresolved | §5.2 | as A4a | **fixed (R6)**: the unresolved reading was not named |
| E4 | RWM beats the baselines, at h = 368 (teacher-forced); REPRODUCES; every reading the rule reports returns it from h = 32, and below that the readings split | §5.3 | as D4 (M-75) | **fixed (R6)**: no horizon, and the split below h = 32 was not stated |
| E5 | the same, trained autoregressively; RWM AHEAD OF ALL THREE; from h = 128 | §5.3 | as D4 (M-76) | **fixed (R6)**: as E4 |
| E6–E8 | disagreement smaller than error at h = 1 and 100; σ collapsed at h = 1; all ten (20); released; overconfident, ratio interval excludes 1 | §6.2 | as stated | agrees |
| E9 | disagreement beats the forecast step index at h = 100; paired difference excludes zero | §6.6 (l. 929) | resolved at every index-defined horizon | agrees |
| E10 | … better than the model's own predicted step size; SURVIVES entry-res ONLY | §6.6 | as A8 | agrees |
| E11 | rollout and depth held constant; interval excludes zero and clears the MDE | §6.6 (l. 937) | +0.419 [+0.318, +0.576] | agrees |
| E12 | per-horizon multiplier; held-out pair (4); released; within tolerance; Arm A 17 of 36; not resolvable | §6.7 | as A11 | agrees |
| E13 | shares no trunk; out-of-sample (4); MECHANISM SUPPORTED | §6.8 (l. 1085) | as A9 | agrees |
| E14 | matched capacity; UNDER-POWERED — favours the matched ensemble by less than the MDE | §11 (l. 1289–1297); Appendix E | 1.79× against 2.00×; coverage +6.42 points clears its MDE | agrees |
| E15 | independence and the corrected objective; THE COMBINATION IMPROVES CALIBRATION | §6.8 (l. 1106) | M-68's verdict | agrees |
| E16 | stale pairing; all ten (20); raises error up to h = 32 on relative-L1; not resolved from h = 100 | §7.2 | as A12 | agrees |

## §9 Actionable lessons

| # | sentence (abridged) | body anchor | readings | agrees? |
|---|---|---|---|---|
| L1a | on the released checkpoint's own training episodes, at one step +0.994 [+0.918, +0.999] across the 20 trajectories; over the full rollout +0.605 | §6.6 (l. 918) | all ten (20) | agrees |
| L1b | beats the forecast step index at every horizon we tested, …, 5 of the 5 horizons where the index is defined, and retains +0.596 | §6.6 (l. 923–931) | as E9 | agrees |
| L1c | step size +0.4697 against +0.6053, a margin of +0.1357, below the 0.2891 this sample can resolve; retains +0.5430; +0.419 with depth and rollout held | §6.6 (l. 982–999) | as A8 | agrees |
| L1d | at h = 100, 33.4× [28.7, 39.0] on the released checkpoint over all ten episodes, and on the held-out pair 10.5× [9.0, 11.5] on the ensemble-5 arms we trained, against the released checkpoint's 25.7× there | §6.2 (l. 710, 738) | released: 33.4× over all ten, 25.7× on the held-out pair; ensemble-5 arms: 10.5× on the held-out pair | **fixed (R6)**: it set the all-ten figure beside the held-out pair's without naming either arena |
| L2 | one multiplier per horizon … within 10 points …, no single cell resolvable; a global multiplier manages 2 of the 12 epistemic ones; Arm A 17 of 36; multipliers span 9.31× | §6.7 (l. 1014–1060) | as A11 | agrees |
| L3 | the independent-trials null is wrong by up to 10^13× | §6.5; Appendix K | the binomial against the permutation P | agrees |
| L4 | 4 independent 400-step trajectories; pooled resampling narrows intervals by a further 1.42× | §3; §8 (l. 1180) | as stated | agrees |
| L5 | our first pre-registered rule, anchored at h = 8, returned CANNOT BE SETTLED AT THIS BUDGET | §5 (l. 453); Appendix E | as stated | agrees |
| L6 | 7 loss terms; σ 11,683× smaller than its own error at h = 100 and 20,669× at h = 368 | §6.2 (l. 674–709); §6.3 | released, all ten (20) | agrees |

## §11 Limitations

| # | sentence (abridged) | body anchor | readings | agrees? |
|---|---|---|---|---|
| M1 | the out-of-sample arena has 4 independent 400-step trajectories | §3 | as stated | agrees |
| M2 | the trend fit and the per-dimension matched comparison rest on seed 1; the headline A/B verdict on seed 1 | Appendix H; §5 | as stated | agrees |
| M3 | ensemble-5 arms reproduce the direction …; rule M-43 returns DOES NOT GENERALISE on their 4 held-out trajectories, under-powered | §6.6 (l. 963) | as stated | agrees |
| M4 | step size ranks error nearly as well; settling it needs 25 independent trajectories where all ten episodes give 20 | §6.6; Appendix R | as A8 | agrees |
| M5 | 33.4× overconfident at h = 100; rule M-70 DOES NOT REORDER, none of the 6 pairs reordered | §6.2; Appendix R | as stated | agrees |
| M6 | per-dimension tests underpowered at h = 368 | §6.5; Appendix K | as stated | agrees |
| M7 | 23 pre-registered rules; S-12 withdrawn | Appendix E; §8 | as stated | agrees |
| M8 | M-49: 1,023,880 parameters, ratio 0.9998; better calibrated on every seed …; coverage +6.42 clears its MDE; 2.03× → 1.79× against an MDE of 2.00×; UNDER-POWERED | Appendix E; §6.8 | as stated | agrees |

## §12 Conclusion

| # | sentence (abridged) | body anchor | readings | agrees? |
|---|---|---|---|---|
| K1 | the central training claim reproduces at long horizons …, though teacher forcing leads at one step on the short windows built for it | §5 | as A2a and A2b | **fixed (R6)**: as A2b |
| K2 | RWM is ahead at h = 368 of the baselines …, though there none of them beats predicting no change | §5.3 | as A3 | agrees |
| K3 | on accuracy alone four other history and forecast lengths beat its chosen ones at our budget, a verdict every reading the rule reports returns but one, which is unresolved, and a ranking that changes when the chosen setting trains longer | §5.2; Appendix U | as A4a and A4b | **fixed (R6)**: as A4a |
| K4 | at h = 100 the aleatoric σ is 11,683× smaller …; the epistemic term … better by a factor of 349 and still 33.4× [28.7, 39.0] overconfident, both on the 20 trajectories of the checkpoint's own training episodes | §6.2 (l. 709–710) | as stated | agrees |
| K5 | disagreement beats the forecast step index at every horizon and, with rollout and depth held constant, still correlates +0.419; step size +0.470 against +0.605, a margin this sample cannot resolve | §6.6 | as A7, A8, E9 | agrees |
| K6 | the scale may be repairable per horizon on the released checkpoint; on a model that never saw the test episodes the evidence is mixed; per dimension no ordering reaches significance after correction | §6.5, §6.7 | as A11, D5 | agrees |
| K7 | the substitution is present in 1 of the 10 descendants examined, only in a non-default mode | §2; Appendix I (l. 1749) | 13 looked at, 10 examined, 1 | agrees |
| K8 | 11,683× and 33.4× at h = 100 are measurements of one checkpoint; 4 independent trajectories, 20 over all ten | §6.2; §3 | as stated | agrees |
| K9 | §5.2's configuration verdict is resolved, but at our data budget | §5.2 | the governing reading resolves it; K3 states the unresolved reading and the training-length dependence | agrees |

## What was changed, and what was not

- **Fixed (R6):** A2b, A4a, A12, C3b, D2, D3, D4, E3–E5, L1d, K1 and K3. Each fix is wording only.
  - The new phrases are bound to keys computed from the artifacts: `mn_fm_exception`, `mn_fm_n_unres_word`, `bl_tf_from_h` and `bl_ar_from_h` in `paper_numbers.py`, and the same computation in `evidence_summary.py`.
  - Each key asserts the reading pattern its sentence describes.
- **To fit the abstract into C12.1's budget (370 words),** five things were cut, none of them a result: "proprioceptive", "from scratch", "here", "Separately" and "so" (now a colon).
- **Recorded, not changed (OUT_OF_SCOPE).** §5.2 reports M-74's alongside readings at the level of the verdict.
  - Per configuration, the four winners are unresolved on the held-out pair at h = 1 (both metrics) and, for the longer forecasts, at h = 8.
  - On long-horizon readings: (2, 8) is unresolved on held-out nRMSE at h = 368, (8, 8) on in-sample relative-L1 at h = 368, and (32, 32) on in-sample pooled nRMSE at h = 100.
  - No reading puts the centre ahead of any of the four.
  - The front matter's qualifier follows the body's verdict-level statement.
