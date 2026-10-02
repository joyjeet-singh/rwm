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
