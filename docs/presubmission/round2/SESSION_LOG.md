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

## T4 — 2026-10-02 17:00 — Opus 5.5, xhigh effort (the plan assigns high) — status: COMPLETE
Commits:
7ea674b [T4][keys] Keys and assertions for sections 5.2 and 5.3 from N2, N3 and X1
659d475 [T4][item 1] The configuration claim becomes an accuracy-only statement (E2): cost per iteration, equal compute, history length, still learning; hours to Appendix B
2c0f002 [T4][item 2] The architecture claim is softened and the RSSM diagnosed (E3): where the lead begins, h = 100, X1 Parts A and B
2d5e38d [T4][item 3] nRMSE as section 3.1 defines it (E6): pooled alongside readings and the head-to-head table's baseline cells
ba5fa10 [T4][item 4] The diverged-rollout flag (E7): dagger rows, per-seed values, sign-only verdicts
0138946 [T4][item 5] Abstract and contribution 3 (Annex 3, variant (a) by N3's reading)
a08b506 [T4][item 6] Appendix D rows for the configuration and architecture claims
80dc072 [T4] Rebuild after items 1-6 (fast build, gates, fast build: byte-identical)
ace7220 [T4][review] Fix the wording review's findings: scope, arena and post hoc labels
(the commit carrying this entry) [T4] COMPLETE: session log
Done:
- **How this session ran.** T4 ran in the same conversation as T3, continuing after a context compaction, because the user asked for that in chat. §0.3 asks for a fresh terminal: the `claude` CLI is not on PATH on this machine, so the user chose the in-app session. At their request, `CLAUDE_CODE_SUBAGENT_MODEL=claude-sonnet-5-5` now sits in the `env` block of the user's Claude settings for later sessions. This session predates that, so its one subagent was given Sonnet by alias.
- **Item 1 (E2).**
  - §5.2's table: "hours per run" becomes "cost per iteration, relative to the centre", from N3 part 1; the centre's cell is 1.00.
  - Hours per run move to a new Appendix B table, one row per run family, with overlap counts (`rt_pre_table`); §5.3's column moves the same way.
  - The history-length finding leads its paragraph.
  - New paragraph, "Accuracy at equal compute (post hoc; ledger R-78)". N3 selects **variant (a)**: at 5,000 iterations, with 1.11× the computation, the centre is still behind (32, 32), −0.2031 [−0.5033, −0.0275]. The same paragraph says where it stops: not resolved at 10,000 iterations, level in-sample at 5,000, and the shorter histories pass the centre at 10,000.
  - The Limits gain the training-loss slopes: all 48 runs at 2,500 iterations are still falling.
- **Item 2 (E3).**
  - §5.3's Result: RWM leads baselines built to our reading of Table S7 and trained with RWM's settings, and every baseline is worse than the floor at h = 368.
  - Where the lead begins, from the rules' held-out relative-L1 readings: teacher-forced from h = 32, the transformer from h = 8; autoregressive RSSM from h = 8, MLP and transformer from h = 100, bound with their intervals.
  - "Where ours departs" is replaced by an RSSM paragraph:
    - it is the most accurate of §5.3's models at h = 1 and has collapsed by h = 32;
    - X1 Part A (**NOT EVALUATION-LIMITED**, M-81) and Part B (descriptive) are reported as returned;
    - the Part C sentence is a placeholder: "Retraining variants are running (X1 Part C): both have trained, and neither is scored yet." The build fails once `part_c` exists until T9 writes it.
  - The architecture claim now rests on the MLP and the transformer.
- **Item 3 (E6).**
  - The M-74 alongside clauses read N2's pooled readings.
  - One sentence in §5.2 says the pooled readings return the same verdict everywhere except two in-sample readings of §5.3's rules (R-77). Those two are named from `readings_whose_result_changed`.
  - The head-to-head table's baseline nRMSE cells are filled from `pooled_nrmse_rescore.json`, and the "not shown here" sentence goes.
- **Item 4 (E7).** N2's flag marks MLP-tf, transformer-tf and RSSM-ar with † in both tables. The caption gives the per-seed values and says verdicts depend on sign only, which is asserted: every flagged row's four per-trajectory differences are positive.
- **Item 5.**
  - Abstract: Annex 3's base-claim sentence (installed in T3), the baselines sentence, and the configuration sentence in variant (a). The winners' description, "two shorter histories and both longer training forecasts", is generated from the M-74 verdict.
  - Contribution 3 rewritten. There are 7 bullets, each at most 3 sentences; the title is unchanged.
  - The abstract is **368 words, 21 numerals** (caps 370/26). The plan's aim of ≤ 350 was not reached by trimming wording alone, and no finding was cut to reach it.
- **Item 6.** The paper's Appendix D rows for the configuration and architecture claims carry the new statements.
- **Item 7.** No edit needed: the §3.2 generator prints the §5.2 and §5.3 verdicts verbatim and nothing beyond them.
- **Review.** A Sonnet 5.5 subagent (read-only Explore, one of two allowed) recomputed every T4 number and found all sound (`evidence/R2T4/t4_review.md`). Its verdict was PASS-WITH-FIXES, with four fix-now findings, six minor ones and notes. All were fixed in ace7220. F4 was the Conclusion's stale "architecture claim also holds … beaten at our budget", an Annex 2 anchor outside the named sections.
Build/gates: pass. Two build-gates-build passes, 8/8 gates, 62/62 claims, 62/62 corruptions caught, byte-identical, and the second pass equal to the first (`t4rev_1`, `t4rev_2`). PDF: 50 pages (was 49).
Paper numbers changed: `mn_table` and `bl_table`: the last column is cost per iteration (results/mn_compute_matched.json), and three `bl_table` rows carry †. `pdf_pages` 49 → 50. `tn_typed` 717 → 725 (generated).
New keys (85; artifacts results/mn_compute_matched.json, pooled_nrmse_rescore.json, pooled_nrmse_alongside.json, rssm_diagnostics.json, training_tail_slopes.json, baselines_verdict.json, presubmission_runtime.json):
- n3_*, mn_better_kinds, mn_better_long_phrase, mn_n_short_better_word, tail_n, tail_slope_lo/hi;
- h2h_bl_*_nrmse_h{1,8,100,368}, h2h_bl_*_label, n2_n_changed_word, n2_changed_list;
- div_factor, div_n_word, div_per_seed;
- bl_tf_lead_from, bl_tf_tr_lead_from, bl_ar_lead_from, bl_ar_rssm_lead_from, bl_ar_{mlp,tr}_{D,ci}_h100, bl_ar_mlp_pct_h100;
- x1_*, x1b_*, rssm_partc_sentence, rt_pre_table.
Re-anchored checks: none.
CPU jobs over 1 min: 7 build-and-gate passes, about 3-4 min each. No training.
Body words (FILE_MAP §13 command): 27,671 (T0: 26,526). The equal-compute, RSSM and nRMSE text Annex 2 requires adds about 830; U3's target of ≤ 19,000 is T6 and T7's.
Next: T5, the coverage audit and Appendix H (Opus 5.5, default effort), in a fresh session. X1 Part C's two seed-0 runs have finished training (`results/baseline_run_rssm_tf_x1v{1,2}_seed0.json`, untracked) and wait for T8 to score them.
Decisions for user: none.

## T5 — 2026-10-02 17:50 — Opus 5.5, xhigh effort (the plan assigns default) — status: COMPLETE
Commits:
de0bb1e [T5][items 1, 2, 4, 7] COVERAGE.md: every contribution-tagged entry, classified
044e60b [T5][keys] Keys and assertions for Appendix H's measurement rows
79d88a0 [T5][item 5] Appendix H: findings not in the main text
cde74f4 [T5][item 6] Section 7 points to Appendix H
9a30565 [T5] Rebuild after items 5-6 (fast build, gates, fast build: byte-identical)
54e7b1e [T5][review] Fix the Appendix H review's findings: addresses, table, scope, metric
(the commit carrying this entry) [T5] COMPLETE: session log
Done:
- **How this session ran.** T5 ran in the same conversation as T3 and T4, at the user's request in chat.
- **Items 1, 2 and 7.** `round2/COVERAGE.md` has one row per contribution-tagged entry. There are 105 such entries: the plan's 102 plus T1's R-76 to R-78.
  - **(a) Mechanically** (`round2/t5_coverage.py`, on the template at d0c6451, before T5): 49 entries are covered by an artifact-sourced key the paper uses.
  - **(b) By phrase:** the other 56, plus candidate R-39, were checked by one Sonnet 5.5 Explore subagent. Its output is kept verbatim in `round2/t5_coverage_md.py`.
  - **Before T5:** 65 covered, 26 partly covered, 14 absent.
  - **Left out:** 6 absent entries, each with its reason.
    - R-02: superseded as headline by R-15.
    - R-05 and R-07: ten overlapping trajectories under the released protocol.
    - R-28: an overlapping-window count, not a sample size.
    - M-17: narrowed by R-30 and M-19, and replaced by Appendix G.
    - R-33: status SUPPORTED, not CONFIRMED.
  - Every partly covered entry without an Appendix H row says why the body's statement suffices.
- **Item 4.** All 16 plan candidates were read in full. All are CONFIRMED and none is superseded in part without a replacement.
- **Item 5.** Appendix H, "Findings not in the main text", has 15 entries in one compact table, grouped as follows.
  - *Paper-versus-code gaps:* C-09; M-13; C-05; C-07 with D-07; C-13.
  - *Pipeline defects:* B-02; B-03.
  - *Measurements:* D-10; R-25; R-30; R-39; R-45 with R-29; R-46.
  - Code facts are cited by file and line at the pinned commits. Every measurement is a key, and each row's claim is asserted in `paper_numbers.py`.
  - No artifact records the configuration's 500 or the checkpoint tag's 5,000, so C-13's row states the finding without those numbers.
- **Item 6.**
  - One sentence at the head of §7 points to Appendix H.
  - R-26 gets no new sentence: T4's §5.2 Limits already says every run at 2,500 iterations, both arms included, is still learning.
- **Review.** A second Sonnet 5.5 subagent (`evidence/R2T5/t5_review.md`) reproduced every measurement row. Its verdict was PASS-WITH-FIXES, all fixed in 54e7b1e:
  - stale `system_dynamics.py` addresses copied from the ledger, re-read at 18eebcd;
  - "Table S7" should be Table S9;
  - three unscoped bearings;
  - R-25 shown as an order of magnitude;
  - R-30's share is form 2, which `g_z` dominates (now asserted);
  - qualifiers on R-39, R-45, R-46 and D-10.
- **OUT_OF_SCOPE.md** gains three lines:
  - D-12's span differs between the paper and the ledger (two artifacts);
  - R-28's SETTLED is at 100 overlapping windows;
  - the ledger's C-13 says Table S7 for Table S9 (needs an append-only correction).
Build/gates: pass. Two build-gates-build passes, 8/8 gates, 62/62 claims, 62/62 corruptions caught, byte-identical, and the second pass equal to the first (`t5rev_1`, `t5rev_2`). PDF: 52 pages (was 50).
Paper numbers changed: `pdf_pages` 50 → 52; `tn_typed` 725 → 763 (generated: Appendix H's code addresses, all classified).
New keys (39):
- `d10_*` (results/step0_regimes.json);
- `r25_*` (step6_3_min_logstd.json);
- `r30_*` (taskAB_gate_r27.json);
- `r39_*` (task4_arenas.json);
- `r45_*` and `r46_*` (task2_3_matched_trend.json; `r45_n_dims` from taskAB_gate_r27.json).
Re-anchored checks: none.
CPU jobs over 1 min: 5 build-and-gate passes, about 3-4 min each. No training.
Body words (FILE_MAP §13 command): 27,703 (T0: 26,526). Appendix H sits after "Data and code"; only the §7 pointer counts.
Next: T6, length pass 1 (§1–§6.6) (Opus 5.5, default effort). The body must come down from 27,703 to U3's ≤ 19,000 across T6 and T7. The abstract is at 368 of 370 words.
Decisions for user: none.

## T6 — 2026-10-02 19:10 — Opus 5.5, xhigh effort (the plan assigns default) — status: COMPLETE
Commits:
6beab8f [T6][s2] Section 2's PETS lineage and survey move to Appendix I
e1fbfac [T6][s6.3] Section 6.3's synthetic-noise experiment moves to Appendix J
c9affa1 [T6][s6.6] Section 6.6's permutation machinery moves to Appendix K
1f1cee6 [T6][s5] Section 5's long-horizon detail and the head-to-head table move to Appendix L
d27285d [T6][s6.2] Section 6.2's two reading checks and the permutation column's note move to Appendix M
469ffa3 [T6][s1] Section 1 tightened, wording only
e4fafda [T6][s5] Section 5 tightened, wording only
1eff373 [T6][s6.3] Section 6.3's gradient check and run table join Appendix J
fa49754 [T6][s3] Section 3's account of why no more data can be generated joins Appendix C
15badef [T6] Rebuild after the moves (fast build, gates, fast build: byte-identical)
7718ae5 [T6][review] Fix the length review's findings: qualifiers, pointers, references
(the commit carrying this entry) [T6] COMPLETE: session log
Done:
- **How this session ran.** In the same conversation as T3–T5, at the user's request.
- **Every move is in `round2/t6_patch.py`, one ITEM each.**
  - Each move cuts a block verbatim and appends it to an appendix, or inserts it into one.
  - Each was replayed from the previous commit and committed alone.
  - The words before and after every move are in `round2/LENGTH_LOG.md`.
  - The quick check after each move (`round2/t6_qc.zsh`: numbers, paper, claims, xref, restatement, horizon, scope, typed numerals) passed with 0 suspect pointers each time.
- **New appendices.**
  - I: §2's PETS lineage and survey of descendants.
  - J: §6.3's synthetic-noise test (M-50), term-by-term gradient check and the runs behind the collapse rate.
  - K: §6.6's permutation machinery.
  - L: §5's long-horizon cells, multiplicity and the head-to-head accuracy table.
  - M: §6.2's reading checks (M-62, M-63) and the permutation column's note.
  - One block joined the existing Appendix C (from §3).
- **The body keeps everything the plan names**: §9; every table §3.2 cites; the abstract's numbers; every verdict.
- **Nothing left the paper, checked mechanically.** All 1,257 keys the template used at T5's end, every table row, every ledger ID and every `results/` path are still in it.
- **Not done, with reasons.**
  - **§6.5's merge into §6.3 is left to T7.** It needs §6 renumbered (U6), and T7 must renumber anyway for §6.9 and §6.10–§6.11. One renumbering, with one pointer map, avoids doing about 280 cross-file references twice. §6.5 is 122 words.
  - **§1 is at 1,049, not ~750.** Bullets 2, 3 and 6 are Annex 3's text, and the others are the paper's claims with their figures.
- **Review.** A Sonnet 5.5 subagent (read-only, the session's one) returned PASS-WITH-FIXES (`evidence/R2T6/t6_review.md`), all fixed in 7718ae5.
  - Summaries had dropped qualifiers (F1–F3, F11).
  - §1 had lost a sentence (F12).
  - Pointers needed re-aiming at Appendix K (F5–F6).
  - Relative references in J, L and C needed their sections named (F7–F9).
  - A clause, already in the text before T6, attributed rule M-63's uniformity to §6.3's mechanism. M-63 measures the epistemic term, so the clause was withdrawn and recorded in BUILD_CHECKS' moved-from-body list (F4).
  - Restoring qualifiers cost 109 words.
Build/gates: pass. Two build-gates-build passes after the review, 8/8 gates, 62/62 claims, 62/62 corruptions caught, byte-identical, and the second pass equal to the first (`t6rev_1`, `t6rev_2`). The rendered-PDF check is 5/5, with appendices I–M lettered as in the source. PDF: 54 pages (was 52).
Paper numbers changed: `pdf_pages` 52 → 54, and generated counts only (`tn_typed`).
New keys: none
Re-anchored checks: none. Anchors that moved with their text (C3.5 into Appendix K, C22.1 into Appendix J) are still found, because those checks read the whole paper. One xref pointer was reworded rather than re-anchored: §6.3's first sentence now says it "leaves the epistemic one open", the words the pointer in §6.4 uses.
CPU jobs over 1 min: 5 build-and-gate passes, about 3-4 min each, and 13 quick checks, about 1 min each.
Body words (FILE_MAP §13 command): 24,719 (T0: 26,526; T5's end: 27,703). T6 cut 2,984 from the body (34% of the 8,703 needed) against the plan's aim of 45%. T6's range is 16,080 → 13,090 words.
Next: T7 (§6.7–§12 and the appendices; Opus 5.5, default effort).
- **Starting point.** T7's range holds 11,629 words, and reaching 19,000 needs 5,719 of them, about half.
- **Its own moves:**
  - §6.7's robustness checks;
  - §6.10–§6.11 to about 700 words;
  - §7.4 and §7.5 to two sentences each;
  - §11 to about 900;
  - §12 to about 500;
  - the §6.9 merge.
- **Inherited from T6:** §6.5's merge into §6.3 and a single §6 renumbering, with a pointer map (U6).
- **Expected outcome.** These are likely to leave a shortfall. U3 says to report it rather than force it.
- **Tools.** T7 can reuse `round2/t6_patch.py` (`move`, `sub`, `insert`, `append` operations), `t6_words.py`, `t6_anchors.py` and `t6_qc.zsh`.
Decisions for user: none.

## T7 — 2026-10-02 20:30 — Opus 5.5, xhigh effort (the plan assigns default) — status: COMPLETE
Commits:
5b5a1a5 [T7][s6.7] Section 6.7's robustness checks move to Appendix N
f73b499 [T7][s6.5, s6.9] Fold sections 6.5 and 6.9 into the subsections they support (ruling U6)
b8bfb1c [T7][s6.10] Sections 6.10 and 6.11 become one section; their detail moves to Appendices O and P
adf9f4e [T7][renumber] Renumber section 6 once, with a pointer map (ruling U6)
5ee21e4 [T7][s7.4, s7.5] Sections 7.4 and 7.5 to a summary each; their detail to Appendices Q and F
8906190 [T7][s11] Section 11 keeps the limitations not stated where they bite; the full text moves to Appendix R
d0effd6 [T7][s12] Section 12's middle paragraphs condense to one; their text moves to Appendix S
ce15edf [T7][s6.7] The multiplier section's cross-model test (rule M-69) moves to Appendix T
211ac21 [T7] Rebuild after the moves and the renumbering (fast build, gates, fast build: byte-identical)
b66d9e9 [T7][review] Fix the length review's findings: qualifiers, renumbering misses, pointers
(the commit carrying this entry) [T7] COMPLETE: session log
Done:
- **How this session ran.** In the same conversation as T3–T6, at the user's request. Ultracode was on, but the plan's §1.3 limits a session to two read-only subagents and forbids delegating edits, so the edits were made in session and one subagent reviewed them.
- **Every move is in `round2/t7_patch.py`**, which reuses T6's engine with a new `fn` operation for restructuring. The words before and after each move are in `round2/LENGTH_LOG.md`.
- **Moves, with section numbers as they were before the renumbering.**
  - **§6.7's robustness checks** go to Appendix N: the depth controls and decomposition, the within-rollout qualifications and the h = 1 reading, M-43's power analysis and companion arena, and the note on the undefined cell. The body keeps the main table, the per-horizon r_dd table (it backs a §3.2 row), M-45's statistic and verdict (the abstract's +0.419), M-43's verdict and the step-size result.
  - **§6.5 and §6.9 are folded** into §6.3 and §6.6, which they support. §6.9 is placed after §6.3 so the figure order holds.
  - **§6.10 and §6.11 become one section** of about 700 words. It keeps the design of both rules, both main tables, both verdicts, the share that is σ, "the two fixes do not add", the capacity and data-order caveat with M-49's matched verdict, and that neither arm is an interval. Their other paragraphs go verbatim to Appendices O (M-44) and P (M-68).
  - **§7.4 and §7.5** become summaries; their text goes to Appendices Q and F.
  - **§11** is rewritten to the limitations not stated where they bite, keeping M-43's, M-70's and M-49's verdicts and the policy caveat that other sections cite. The original goes to Appendix R.
  - **§12's middle paragraphs** condense to one; their text goes to Appendix S. The three-kind "what should travel" paragraph is intact.
  - **Rule M-69's cross-model transfer test** (§6.7, the multiplier section) goes to Appendix T.
- **The renumbering** (`round2/t7_renumber.py`) is one simultaneous substitution. Old → new: 6.5 → 6.3, 6.6 → 6.5, 6.7 → 6.6, 6.8 → 6.7, 6.9 → 6.5, 6.10 → 6.8, 6.11 → 6.8.
  - Applied to: the paper, the README, BUILD_CHECKS, the external brief, the model card, §3.2's section keys and the checker's labels.
  - Not applied to the ledger or to the rule texts quoted from it.
  - The pointer map is in `docs/BUILD_CHECKS.md` and in the preamble of `docs/APPENDIX_G_RULES.md`.
  - §1–§5 and §7 onward keep their numbers.
- **Nothing left the paper, checked mechanically.**
  - Every key, ledger ID and `results/` path present at T5's end is still in it.
  - The two table rows that changed are Appendix D rows whose §6 references were renumbered.
- **Review.** A Sonnet 5.5 subagent (`evidence/R2T7/t7_review.md`) returned PASS-WITH-FIXES, all fixed in b66d9e9.
  - Everything checked out: every move was faithful, all 172 §6 references but two were right, and the figures are in order.
  - The ten fix-now defects were in the new connecting prose: dropped qualifiers in summaries, three renumbering misses (including the unregenerated `docs/APPENDIX_G_RULES.md`) and two stale pointers.
  - Two pre-existing items went to OUT_OF_SCOPE.md.
- **What T7 reports (PLAN T6/T7).**
  - **Final body count:** 20,166 words against the 19,000 target, a shortfall of 1,166 (6%). Reported rather than forced, per U3.
    - T6 and T7 together cut 7,537 words, 87% of what was needed (body 27,703 → 20,166).
    - Every move the plan lists is done. Cutting further would mean removing the argument in §5, §6.2 and §6.6, not detail.
  - **Three largest remaining sections:** §6.2 The measurement (1,771); §5 (to §5.1: 1,731); §6.6 Ensemble disagreement beats the trivial baseline (1,516). By top-level section: §6 (7,963), §5 (4,231), §3 (1,903).
  - **Pages before References:** 32. "Data and code" is on page 32 and References begins on page 33, of 57 pages in all.
Build/gates: pass. Three build-gates-build passes after the review, 8/8 gates, 62/62 claims, 62/62 corruptions caught, byte-identical, and the second pass equal to the third (`t7rev_2`, `t7rev_3`). The rendered-PDF check is 5/5, with appendices N–T lettered as in the source.
Paper numbers changed: `pdf_pages` 54 → 57; generated counts only.
New keys: none
Re-anchored checks:
- `restatement_index` ACCEPTED_AMBIGUOUS: ("6.10 Testing the mechanism: an ensemble that shares nothing", "3") → ("Appendix O — rule M-44 in full: an ensemble that shares nothing", "3"). The decomposition table it accepts moved verbatim.
- The checker's `where` labels and §3.2's section keys were renumbered with the paper (U6); no check's logic changed.
CPU jobs over 1 min: 6 build-and-gate passes, about 3-4 min each, and about 12 quick checks, about 1 min each.
Body words (FILE_MAP §13 command): 20,166 (T0: 26,526; T6's end: 24,719).
Next: T8 (Sonnet 5.5): the retraining gate and X1 Part C's scoring (`rssm_diagnostics.py --part c` on the two finished seed-0 runs), pipeline hygiene and figure labels. The §6.8 and §5.3 numbers and section references T8 or T9 touch are now in the renumbered scheme.
Decisions for user: none (the shortfall is reported under U3, not raised as a decision).

## T8 — 2026-10-03 12:02 — Opus 5.5, xhigh effort (the plan assigns Sonnet 5.5, default) — status: COMPLETE
Commits:
18f9818 [T8][item 1] Retraining gate passed; X1 Part C scored: NOT RESCUED BY THE SETTINGS TRIED (ledger M-83)
a65e981 [T8][item 2] reproduce.sh drives every writer the paper reads; 0 uncovered, 0 unclassified
82d34e2 [T8][item 3] The E7 check reads BUILD_CHECKS as well as the template (round 1's S25F patch)
44c95d8 [T8][item 4] The bundle self-test plants the newest commit's full hash, not its 7-character prefix
1482df9 [T8][item 5] Untrack the two committed template backups; ignore and skip the four backup suffixes
942e68a [T8][item 6] README names the file that lost a value separately from the file that records the count
c89e5a5 [T8][item 7] Model card: the stale-action sentence quotes N1's measurement instead of 'materially worse'
00cbd93 [T8][item 8] Figures: clear the label and legend collisions round 1 left open; no plotted value changes
24f478a [T8][item 2-fix] BUILD_CHECKS no longer reads the retired glob as 'the sweep found none'
b6030bb [T8] Rebuild after items 1-8 (fast build, gates, fast build: byte-identical, twice)
fe16247 [T8][review A] Part C's sentence states the registered test; the pending-X1 prose is rewritten for its discharge
ba14bcf [T8][review B] Stage 21's gate runs again; the training queues come from the committed records
1aceee3 [T8][review] Rebuild after the review fixes (fast build, gates, fast build: byte-identical, twice)
(the commit carrying this entry) [T8] COMPLETE: session log
Done:
- **How this session ran.** In the same conversation as T3–T7, at the user's request, on Opus 5.5 at xhigh effort where the plan assigns Sonnet 5.5. Ultracode was on; within the plan's §1.3 limit, the review was one workflow of two read-only Explore subagents, and every edit was made in session.
- **Item 1, the retraining gate and X1 Part C.**
  - Gate passed: both queued runs done, the failures file empty, 2,500 iterations at seed 0 under specs x1v1 and x1v2, finite curves, weights present.
  - `rssm_diagnostics.py --part c`, as committed in 2433f44, returns **NOT RESCUED BY THE SETTINGS TRIED**. Neither variant meets the criterion on seed 0: at h = 32, three of V1's four trajectories and two of V2's are above the hold-last floor. So no further seeds ran. Part C used 4.2 measured CPU-hours of the 10-hour cap (U2).
  - Ledger `M-83` records it from the artifact; `M-80`'s Status line changed at discharge; RESULTS.md's M count is 83.
  - **This session wrote T9's item 1.** T4's guard fails the build once Part C has a reading and the placeholder still stands, so §5.3's sentence had to be replaced here to keep the build passing.
    - It is generated from the artifact (key `rssm_partc_sentence`, final reading verbatim), and the build asserts the no-rescue case it describes.
    - The review (A1) caught the first wording stating M-80's test wrongly. It now reads: the variants score 1.2588 and 1.4685 at h = 32 against the floor's 0.5950, with 3 and 2 of the 4 trajectories above their own floor value; a rescue needs the mean below the floor's and every trajectory below its own.
    - The pending-X1 prose after it, and Appendix D's row, are rewritten for the discharge (A2).
    - T9 owns this wording, and should read it with the front matter, since the abstract, §1 and §12 speak of the RSSM comparison.
  - Appendix E: `M-80` now has a lead time of +3 min. Rule commit 2433f44 is at 12:17:08; acf5eec, the first commit holding `results/rssm_diagnostics.json` (Parts A and B), is at 12:20:28. Appendix E counts 22 rules with a lead and 21 positive.
- **Item 2, reproduce.sh.**
  - New stages: 11d–11j (the five remaining training drivers and both queues), 20r3a (P4) and 20t1–20t13. Stage 21 declares `claims_to_evidence.json`.
  - `s8_runtime.py` moved to `scripts/`, with a stub at its old path.
  - `pipeline_coverage`: 0 uncovered (it listed 14). `input_set_audit`, keyed by each line's source text rather than its line number: 26 discoveries, 0 unclassified (it listed 20), and A-01 recorded as retired.
  - Verified in a runs-free worktree (`evidence/R2T8/item2_dry_runs.md`): every weight-free new stage regenerates its artifact byte-identically.
  - **The audit change broke a BUILD_CHECKS sentence**, which then said "0 was frozen" after telling how the sweep found the ensemble-5 glob. Fixed in 24f478a with a bound `audit_n_retired` and a dated not-verbatim note; the review (A3) corrected the note's quotation.
  - **Two defects the review caught (B1, B2), both fixed in ba14bcf:**
    - Stage 21's new declared output is committed, so the ledger gate skipped without `--force`. That was a loosened check, now back to M12's empty output-check.
    - Stage 11i could not have completed: `--from-record-cap` refuses the ruled record, and the sweep's `--write-queue` re-probed and rewrote a record the paper reads. The training block now writes both queues with a new `--queue-from-record` in all three timing scripts; checked byte-identical to the queues that ran, with the records unchanged.
    - The runner also gets PY and logs where `s8_runtime.py` reads.
  - The text-keyed audit now lets a classification cover one line (B5); a duplicate is unclassified, shown to fire.
- **Item 3.** Round 1's `e7_fix.patch` applied: E7 reads the template plus `docs/BUILD_CHECKS.template.md`.
- **Item 4.** The self-test plants the full 40-character hash.
  - Run at HEAD 82d34e2, it PASSES: the probe was detected (9 hits) and no identifying strings were found (`evidence/R2T8/item4_selftest.log`).
  - On round 1's float-shaped 5e30429, the detector misses the 7-character prefix and catches the full hash.
  - The run rewrote `results/anon_bundle.json` and `docs/COMMIT_LABEL_MAP.json`. Both were restored to their committed versions with `git checkout`, for T11's bundle rebuild.
  - 44c95d8's message gives the wrong reason, "the run was without --zip": the script rewrites the record on every run (review B10).
- **Item 5.** `git rm --cached PAPER.template.md.appbak`, and also `.d1bak`, committed with it in d6fe07d: a `.gitignore` line does nothing for a tracked file. Both stay on disk. `*.appbak` and `*.d1bak` are now ignored, and the four suffixes are in both builders' SKIP_SUFFIX.
- **Item 6.** README: "A further 1 value is in the committed artifacts and absent after regeneration: `results/anon_bundle.json` (key `.zip_bytes`). All of these counts are recorded in `results/verify_reproduction.json`." The file and key are bound from the artifact (new keys `ver_keys_lost_noun`, `ver_keys_lost_where`).
- **Item 7.** The model card now quotes N1: fed the stale action, the three `autoregressive-10k` checkpoints' relative-L1 error changes by -0.22% at h = 1 and +0.15% at h = 368. That is their mean on the two held-out episodes' 4 trajectories (`results/alignment_by_horizon.json`), and the card says the figure covers those three only. The numbers come from the keys §7.2 prints.
  - c89e5a5's message says seven autoregressive checkpoints ship; it is nine (review A5).
  - The card's pre-existing "The 10k checkpoints are one seed per arm" is now "3 seeds per arm", counted from CKPTS (review A4).
- **Item 8, figures.**
  - Placement only, in `paper_figures.py`:
    - rendered Figure 2(a): value labels and "no difference";
    - Figure 5(a): the legend off the dashed line;
    - Figure 6: both legends off the bars.
  - Figure 6 is not in the plan's "1, 2 and 5", but it is the fourth figure DEFERRED.md recorded as open, and that file itself said the "1, 2 and 5" list was short by one.
  - With unchanged code, regeneration was byte-identical. After the edit, `results/paper_figures.json` is byte-identical and only the three PNGs differ.
  - That file records summaries, so the claim that no plotted value changed rests on the code diff: placement, legends, limits and ticks only. DEFERRED.md carries a correction (review B7).
  - Every figure was viewed before and after (`evidence/R2T8/figs_before`, `figs_after`).
  - R5's two items, fixed in round 1's B1, hold.
  - DEFERRED.md gains a RESOLVED line. The checklist's stale overlap lines go to T11 (OUT_OF_SCOPE).
- **Review.** One workflow of two Explore subagents (`evidence/R2T8/t8_review.md`). Lens A (claims and wording) and lens B (pipeline, hygiene, figures) both returned PASS-WITH-FIXES.
  - Every finding was verified before acting.
  - Fixed: A1–A4 and B1–B7.
  - Recorded in OUT_OF_SCOPE: B8, B9 and B11. The drivers exit 0 whatever training does; ten float-shaped short hashes are left to the scrub; cache readers carry NEEDS_WEIGHTS.
  - Corrected here: A5 and B10, the commit-message errors.
Build/gates: pass. After the review: 8/8 gates on two consecutive passes (`t8rev1`, `t8rev2`), each build pair byte-identical and the passes identical; 57 pages; 62/62 comparative claims, 62/62 corruptions caught. Before it: the same on `t8p1`–`t8p4`.
Paper numbers changed: `rssm_partc_sentence` (the Part C reading); `n_entries` 267 → 268 and `ledger_kb` 570 → 571 (M-83); `appG_n_lead` 21 → 22, `appG_n_positive` 20 → 21 and `appG_table` (M-80's row); `audit_n_hits` 21 → 26 and `audit_n_frozen` 1 → 0 (BUILD_CHECKS only).
New keys: `x1_final_reading`, `ver_keys_lost_noun`, `ver_keys_lost_where`, `audit_n_retired`.
Re-anchored checks: `input_set_audit`'s classification key changed from line number to line text (item 2), with a one-line-per-classification guard added (review B5). Stage 21's gate was briefly loosened by item 2 and restored (review B1).
CPU jobs over 1 min: `rssm_diagnostics.py --part c`; the item 2 worktree dry runs; the bundle self-test; six build-and-gate passes (about 1 min each); four quick checks; the review workflow (two read-only agents, about 10 min). The Part C training itself (4.2 CPU-hours) ran before T8.
Body words (FILE_MAP §13 command): 20,240 (T7's end: 20,166; +74, the Part C sentence and the discharged-X1 wording).
Next: T9 (Opus 5.5, high): its item 1 is already in place (above) and needs only reading. Then front-matter consistency, including how the abstract, contributions, §11 and §12 describe the RSSM comparison now that X1 has its final reading.
Decisions for user: none.

## T9 — 2026-10-03 12:40 — Opus 5.5, xhigh effort (the plan assigns high) — status: COMPLETE
Commits:
347892d [T9][item 2, numbers] Every number in the contributions now appears in the body
6561e14 [T9][item 1] The RSSM sentence: in place since T8; an artifact without Part C now stops the build
e36a68e [T9][item 2, wording] Front matter no stronger than the body: horizons, arenas, comparators, X1's final reading
2f0b987 [T9][item 2, check 6] The abstract's phrase for the four winners is stated in section 5.2
5e5d5d6 [T9] Rebuild after items 1-3 (fast build, gates, fast build: byte-identical, twice)
(the commit carrying this entry) [T9] COMPLETE: session log
Done:
- **How this session ran.** In the same conversation as T3–T8, at the user's request. §1.3's checkpoint rule asks a compacted conversation to stop with PARTIAL; this one was compacted once, before T8, and continued because the user asked for T9 here. Ultracode was on. Within §1.3's limit, the audit was one workflow of two read-only Explore subagents, and every edit was made in session. No subagent review followed the fixes, since the cap was spent; T10 is the fresh-eyes review.
- **Item 1, the RSSM sentence.** It was installed in T8, forced by T4's build guard, and reworded after T8's review. Read again here: §5.3 states X1's final reading verbatim.
  - The pre-discharge branch that would print "Retraining variants are running" whenever the artifact lacks Part C is now an assertion, so a stale artifact stops the build.
  - The placeholder survives only in the plan and the log.
- **Item 2, the numbers.** `round2/t9_frontmatter.py` (read-only) checks every key and rendered numeral of the abstract, contributions, §3.2, §4, §9, §11 and §12 against the body (§2, §3, §3.1, §5–§8, §10, Data and code), then the appendices.
  - Two of the contributions' numbers were not in the body:
    - the verification figures, only in Appendix A, now in §3's Model paragraph;
    - the required sample size, only in §11 and Appendix R, now in §6.6.
  - What remains are phrase keys read off §5.2's explicit list and its 5,000 / 2,500 iteration counts.
  - **`part_f_gate` check 6** (not in the fast build) had failed since T4 on `mn_better_kinds`, the abstract's phrase for the four winners. §5.2's result now states it, and check 6 PASSES with its exemption list unchanged. `results/part_f_gate.json` was restored after each run, for T11.
- **Item 2, the wording.** The audit (`evidence/R2T9/t9_audit.md`) returned PASS-WITH-FIXES on both lenses. 25 edits are in `round2/t9_patch.py`, plus four rows of `evidence_summary.py`. The substantive ones:
  - **The equal-compute reading holds at h = 368 only.** At h = 100 it is unresolved held out (−0.0918 [−0.1901, +0.0065]), and in-sample the centre is ahead (+0.0454). It now carries its horizon in the abstract, contribution 3 and Appendix D.
  - **The abstract's 2.03× had no comparator.** It is now "than our shared-trunk ones", quoting M-44's own statistic; `r2_total_x_h100` was a different statistic equal to two decimals.
  - **Contribution 3 now reports X1's final reading** (Parts A and C), not Part A alone.
  - **§11's M-70 summary** regained its arena, its in-sample status and its degenerate interval.
  - **§3.2:**
    - the intro now names the arenas §3 defines and gives units;
    - the step-size row quotes M-51's verdict verbatim;
    - the multiplier row names Arm A at 2,500 iterations;
    - both architecture rows carry "the RSSM comparison uninformative, rule X1".
  - **Smaller fixes:**
    - arenas, iterations and seed 1 in contributions 2, 3 and 5, and contribution 5's bounding qualifier;
    - the lead's horizon and the in-sample scope in §12;
    - M-16's verdict verbatim in §5 and §9;
    - §9's epistemic-only figures labelled as such;
    - two stale Appendix R pointers, one of them T7's out-of-scope M-49 pointer.
  - **Not changed:**
    - The title, which was the user's S4 ruling.
    - The abstract's RSSM caveat, which would exceed C12.1; the caveat is in contribution 3, §3.2, §5.3 and Appendix D.
    - The abstract still says "one seed per arm" (Annex 3's wording), not "seed 1", for the same reason. Contribution 2, §5, Figure 2's caption and §11 name seed 1.
- **Item 3, budgets.** The abstract is 370 of 370 words and 22 of 26 numerals (C12.1 PASS, with no word to spare). The contributions are 8 bullets of 2–3 sentences each.
- **No key left the template**, checked by diffing key sets against c385c60. `{{m16_verdict}}` is newly used in the text.
Build/gates: pass. 8/8 gates on two consecutive passes (`t9p3`, `t9p4`), each build pair byte-identical and the passes identical; 57 pages; 62/62 comparative claims, 62/62 corruptions caught; `part_f_gate` check 6 PASS.
Paper numbers changed: `evidence_table` (the four §3.2 rows above); `tn_typed` 845 → 849 (typed section numbers in the new pointers; its gate passes).
New keys: none.
Re-anchored checks: none. `paper_numbers.py`'s Part C branch became an assertion, which makes it stricter.
CPU jobs over 1 min: four build-and-gate passes (about 1 min each); three quick checks; `part_f_gate` twice; the audit workflow (two read-only agents, about 13 min).
Body words (FILE_MAP §13 command): 20,472 (T0: 26,526; T8's end: 20,240; +232, almost all restored qualifiers).
Next: T10 (Opus 5.5, high), **in a new terminal**, as the plan says: a fresh-eyes review against Annex 4's checklist. This conversation has carried T3–T9 and is not fresh eyes. Note for T10: Annex 4 item 1's §3.2 alignment anchor predates ruling A (DECISIONS.md#T3-alignment-framing); the row follows the ruling.
Decisions for user: none.
