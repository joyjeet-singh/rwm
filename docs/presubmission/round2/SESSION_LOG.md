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
