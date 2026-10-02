# Round-2 session log

One entry per session, in PLAN.md §1.4's template. The start gate is the last entry.

## T0 — 2026-10-02 11:42 — Opus 5.5, default effort (the plan assigns Sonnet 5.5) — status: COMPLETE
Commits:
a987ec5 [T0][item 1] Round-2 pre-submission plan
e084425 [T0][item 2] Round-2 session log, decisions (defaults accepted) and out-of-scope list
5a310c4 [T0][items 3-4] Bundle exclusion dry-run and the round-2 baseline
a325d5e [T0][item 5] Preflight assertions P1-P4: all PASS
(the commit carrying this entry) [T0] COMPLETE: session log
Done:
- Item 1. The working tree held only `docs/presubmission/round2/PLAN.md` untracked, identical to the user's PLAN2.md. Tagged `pre-round2` (6bee218, local), created `presubmission2` from `presubmission`, committed the plan.
- Item 2. SESSION_LOG.md, DECISIONS.md (§0.2 verbatim; defaults accepted by launching T0, 2026-10-02) and OUT_OF_SCOPE.md.
- Item 3. Neither bundle builder collects anything under `round2/` (`t0_bundle_exclusion.py`; result in BASELINE_T0.md).
- Item 4. BASELINE_T0.md (`t0_baseline.py`): body 26,526 words to "Data and code", 27,039 to References; per-section counts; 49 pages; every gate passes after one fast build; `part_f_gate` 7/7 run (check 4 not run) and `submission_check` 20/22, as at S0.
- Item 5. PREFLIGHT.md (`t0_preflight.py`): P1, P2, P3, P4 all PASS.
Build/gates: pass (BASELINE_T0.md). T0 edits no paper text.
Paper numbers changed: none
New keys: none
Re-anchored checks: none
CPU jobs over 1 min: the baseline pass (one fast build and the gates), about 2 min, run three times while the script was corrected.
Body words (FILE_MAP §13 command): 26,526 to "Data and code" (T0: 26,526)
Next: T1, new analyses N1-N3 (inference only).
Decisions for user: none

## T1 — 2026-10-02 12:12 — Opus 5.5, default effort (the plan assigns high) — status: COMPLETE
Commits:
8fb6ed3 [T1][N1] Alignment defect by horizon, and Arm A's sensitivity to the stale pairing (post hoc)
79f7aae [T1][N2] nRMSE pooled across trajectories for the sweep and baselines; alongside readings side by side (post hoc)
27ee458 [T1][N3] The sweep at equal training compute, and tail slopes (post hoc)
1c3083c [T1][ledger] R-76, R-77, R-78: the post hoc entries for N1, N2 and N3
(the commit carrying this entry) [T1] COMPLETE: session log and a decision for T3
Done: Annex 1's N1, N2 and N3, each with its named reproduction assertion passing before anything new was written. Artifacts: `results/alignment_by_horizon.json`, `results/pooled_nrmse_rescore.json`, `results/pooled_nrmse_alongside.json`, `results/mn_compute_matched.json`, `results/training_tail_slopes.json`. Ledger R-76, R-77 and R-78, each labelled post hoc.
- **N1.**
  - `alignment_defect_ci.py`'s arena() was imported with its horizon set per h. At h = 368 it reproduces `alignment_defect_ci.json` to 1e-9 in both arenas.
  - On the held-out pair, the released checkpoint's relative-L1 overstatement interval excludes zero at every horizon; it is largest at h = 32. Over all ten episodes it is resolved at h ≤ 32, and its point estimates are negative at h ≥ 128.
  - Our Arm A is within 0.93% of zero at every horizon, at both 2,500 and 10,000 iterations.
- **N2.**
  - Asserts: the centre equals the head-to-head table (0 difference); the per-trajectory values equal the committed evaluators' (0 difference); the fast pooled form equals `nrmse_pooled` (within 1e-12); and the reading machinery reproduces all 32 committed alongside nRMSE readings exactly.
  - RWM at h = 368 is 0.5425 pooled against 0.4911 averaged.
  - No held-out alongside reading changes under pooling. Two in-sample readings change (M-75 nRMSE at h = 1; M-76 nRMSE at h = 100). Reported only, never substituted.
  - Rows flagged diverged (E7): MLP-tf, transformer-tf and RSSM-ar.
- **N3.**
  - The 10k runs' 2,500 checkpoint reproduces the sweep's centre exactly.
  - Annex 3's variant is **(a)**: (32, 32) at 2,500 beats the centre at 5,000, the interval excluding zero at h = 368.
  - Against the centre at 10,000, (32, 32) and (32, 16) are not resolved, and the centre is ahead of (8, 8) and (2, 8).
  - The baselines were re-probed for 50 iterations beside a same-sitting centre probe.
  - All 48 runs are still falling at 2,500 iterations, as are 5 of the 6 Arm A and Arm B runs at 10,000.
- **Method note, recorded in R-77 and the artifact.** Annex 1 asks for the rules' reading functions to be called on data "whose nRMSE fields hold the pooled values". The rules' `family()` takes per-trajectory differences, and pooled nRMSE has none. So each reading keeps the rule's resamples, p, interval, Holm and branch functions, and changes only the statistic.
Build/gates: pass. Fast build, the 8 gates, fast build: byte-identical; `ledger_check` PASS with 105 CONTRIB rows.
Paper numbers changed: `n_entries` 261 → 264 and the ledger size 552 → 561 KB (`FINDINGS_LEDGER.md`). No paper text was edited.
New keys: none
Re-anchored checks: none
CPU jobs over 1 min: N1 8.4 min; N2 3.9 min; N3 9.2 min (including the 50-iteration probes of the centre and six baseline families); two build-and-gate passes, about 3 min each.
Body words (FILE_MAP §13 command): 26,526 (T0: 26,526)
Next: T2, the RSSM diagnostics (pre-register X1, then Parts A and B).
Decisions for user: DECISIONS.md#T3-alignment-framing. Needed before T3; it does not block T2.

## T2 — 2026-10-02 12:32 — Opus 5.5, default effort (the plan assigns high) — status: COMPLETE
Commits:
2433f44 PRE-REGISTER RSSM diagnostic X1, before its readings exist
acf5eec [T2][Part A] X1 Parts A and B run as committed; Part A returns NOT EVALUATION-LIMITED (ledger M-81)
0734bfd [T2][Part C] Rule X1's variants V1 and V2: code, deviations rows 39-47, verification
b90008b [T2][Part C] Timing probe within the cap; queue runner takes a queue file
(the commit carrying this entry) [T2] COMPLETE: RUN_QUEUE.md and session log
Done:
- **Item 1.** X1 entered as ledger **M-80** (PRE-REGISTERED, NOT YET DISCHARGED) with `scripts/rssm_diagnostics.py`. It was committed and pushed (2433f44, 12:17:08) before `results/rssm_diagnostics.json` existed. Before the commit, the script ran only its synthetic self-test (15/15) and a smoke test of its code paths on an untrained model.
- **Item 2.** Parts A and B ran as committed. The mode read-out reproduces `baselines_eval.json` exactly. **Part A returns NOT EVALUATION-LIMITED**: the teacher-forced RSSM's expected and sampled read-outs lower its error but stay above the hold-last floor at h = 32. This is recorded in ledger **M-81**, exactly as returned; M-80 stays undischarged.
- **Item 3, Part C** (U2 allows it).
  - V1 (PlaNet's KL settings) and V2 (DreamerV2's layer-normalised GRU) were implemented as opt-in specs `x1v1` and `x1v2`, teacher-forced only.
  - BASELINE_SPECS rows 39-47 were added, with no UNVERIFIED row. V2's cell is transcribed from `danijar/dreamerv2` `common/nets.py:317-347` at 07d906e9, with Keras's layer-norm defaults (`layer_normalization.py:151-155`, v2.6.0).
  - Verified before any training (`round2/t2_verify_variants.py`): the Table S7 RSSMs reproduce `baselines_eval.json` exactly; the cell matches a NumPy transcription to 5.6e-16; V1's KL is the plain clamped KL, with gradient to both sides; both variants train finitely.
  - The 20-iteration probe projects 6.31 CPU-hours for the two seed-0 runs, against the 10-hour cap (`results/x1_partc_timing.json`).
  - `queue_runner.sh` now takes a queue file, with its default unchanged. The queue launched at 12:27:21 with the plan's command, and the first run passed iteration 50 at 171 s with no NaN.
  - `round2/RUN_QUEUE.md` gives the runs, the projected finish (about 18:45) and the status command.
- **For T8.** If either variant rescues on seed 0, M-80 needs seeds 1-2 of it, which would take Part C to about 12.6 h, past the cap. T8 then stops BLOCKED for a ruling before queueing them (RUN_QUEUE.md).
- No paper edits.
Build/gates: pass. Fast build, the 8 gates, fast build: byte-identical (PAPER.pdf restored; it differs only by its compile date).
Paper numbers changed: `n_entries` 264 → 266 and the ledger size 561 → 569 KB (M-80, M-81; generated). Appendix G now lists rule X1 (M-80) as pending.
New keys: none
Re-anchored checks: none
CPU jobs over 1 min: X1 Parts A and B, 40 s; the Part C timing probe (centre, V1 and V2, 20 iterations each), about 4 min; three build-and-gate passes, about 3 min each. In the background since 12:27, the Part C queue: two runs of about 3.2 h each.
Body words (FILE_MAP §13 command): 26,526 (T0: 26,526)
Next: T3, paper edits group 1. It needs the ruling at DECISIONS.md#T3-alignment-framing first.
Decisions for user: DECISIONS.md#T3-alignment-framing (open, raised in T1; needed before T3).

## T3 — 2026-10-02 12:34 — Opus 5.5, default effort (the plan assigns high) — status: COMPLETE
Commits:
4376bcf [T3] Record the ruling on the alignment framing (option A)
e1e8e0a [T3][item 1] The alignment finding becomes minor (E1, ruling A)
4792f61 [T3][item 2, part] Figure 2's caption says what rule M-23 ran on (E4)
b3248b0 [T3][item 2] Say what rule M-23 actually ran on (E4)
dc9429c [T3][item 3] Say what teacher forcing means next to the headline (E5)
681748c [T3] Rebuild after items 1-3 (fast build, gates, fast build: byte-identical)
a8ef867 [T3][item 4] Section 3.2's generator: held-out pair labels, the alignment verdict, verdicts verbatim
a0c8fa4 [T3][item 5] Figure 1's caption carries the in-sample caveat
9749754 [T3][item 6] Ruling U1: S-20 counted as a claim withdrawn on evidence (ledger M-82)
2342f08 [T3][item 7] Guard it: two new comparative-claims checks, with self-test branches
a983ac1 [T3][review] Fix the wording review's findings F1-F10 and what they exposed
(the commit carrying this entry) [T3] COMPLETE: session log
Done:
- **Item 1 (E1, ruling A).** The alignment finding is demoted to minor. The abstract keeps one clause, with no numbers: the cost "is concentrated at short horizons, and at the longest horizon … is small and not consistent in sign". This uses "the longest horizon" rather than the method's own horizon, because at h = 100 the cost is +22.5% and resolved. Contribution 6 and §7.2 lead with the same wording and give the h = 1 figure. §7.2 also gives our Arm A's sensitivity to the stale pairing.
- **Item 2 (E4).** Rule M-23 is stated as run on one seed per arm (seed `m23_seed`, `m23_ratio`×). The three-seed figures, including `d1_ratio`× at h = 368, are an extension carrying none of its weight. This is said in the abstract, contribution 2, §5 and §11, and in the Figure 2 caption.
- **Item 3 (E5).** Next to the headline, the paper says what teacher forcing means here and how the original's N = 1 version compares.
- **Item 4.** The §3.2 generator now:
  - labels the released checkpoint's out-of-sample rows "held-out pair";
  - derives the alignment row's verdict from `alignment_by_horizon.json`;
  - prints the M-74/75/76 verdicts verbatim.
- **Item 5.** Figure 1's caption says the held-out arena is in-sample for the released checkpoint.
- **Item 6 (U1).** Ledger M-82 reclassifies S-20 as a claim withdrawn on evidence. `ledger_check.py` applies the **Reclassifies** line, and the classes are now 7 withdrawn on evidence, 6 framings withdrawn and 7 early hypotheses, with 20 superseded in all.
- **Item 7.** There are two new check kinds:
  - C25.1 `rule-seed-scope`: a three-seed figure near "rule" names the seed or calls itself the extension.
  - C25.2 `overstat-reversal`: no "overstates" beside an alignment figure unless its paragraph names the reversal.

  Each has a verification branch, a corruption, a scope-audit entry and a kind description.
- **Review.** A Sonnet 5.5 wording review returned PASS-WITH-FIXES, with five fix-now findings, five minor and three notes (`evidence/R2T2/t3_review.json`). F1-F10 were fixed in a983ac1; notes F11-F13 were left as the review allowed.
  - F2: the C25.1 marker had passed the very text it was written to catch. It was tightened, and both C25 self-tests now plant the real old wording from git history and must catch every planted paragraph.
  - The tighter marker caught one more paragraph, §5's effect-size paragraph, which now names the extension.
  - **Fixes the review exposed:**
    - C10.5 never applied a **Reclassifies** line, so it still read S-20 as a framing. It now uses `ledger_check.py`'s pattern.
    - That made `S-17` ambiguous in a paragraph naming both classes. It is now called the framing the ledger says it is.
    - `pdf_render_check.py` read a page break inside "(Figure 2)" as a Figure 10. It now strips each page's running header and page number, and asserts that both are present on every page.
Build/gates: pass. Final state: two build-gates-build passes, 8/8 gates, 62/62 claims, 62/62 corruptions caught, byte-identical, and the second pass identical to the first (`t3rev_2`, `t3rev_3`). Abstract: 333 words, 20 numerals (caps 370/26). PDF: 49 pages.
Paper numbers changed: `m23_ratio` 4.4 → 4.43 (now two decimals). Retraction counts: evidence six → seven, framings seven → six, framing cohorts 4 → 3; S-20 left the framing list. `cc_kinds` 27 → 29, `cc_n` 60 → 62. `n_entries` 266 → 267, `ledger_kb` 569 → 570 (M-82). `tn_typed` 711 → 717 (generated). In the §3.2 table, the alignment row's verdict and three verdicts' capitalisation changed, and the §6.8 row's arena reads "held-out pair (4)".
New keys: m23_A_s1, m23_B_s1, m23_other_seeds, r60_date, adh_rel_h1, adh_rel_ci_h1, adh_rel_h100, adh_rel_ci_h100, stale_armA_rel_h1, stale_armA_rel_h368
Re-anchored checks: none. C10.5 now reads reclassifications, which is a correction to agree with the ledger, not a re-anchor. C25.1's marker was tightened, never loosened.
CPU jobs over 1 min: 15 build-and-gate passes, about 3-4 min each. In the background, the X1 Part C queue finished both seed-0 runs, V1 at 14:34 and V2 at 16:40, with no failures. Their artifacts stay uncommitted until T8 scores them.
Body words (FILE_MAP §13 command): 26,840 (T0: 26,526)
Next: T4, paper edits group 2 (§5.2/§5.3 with N2, N3 and X1; abstract; contribution 3; Appendix D rows). Part C has finished, so no placeholder is needed for it, but its verdict is T8's to read under M-80.
Decisions for user: none.
