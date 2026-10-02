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
