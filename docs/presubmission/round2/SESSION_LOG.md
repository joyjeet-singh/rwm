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
