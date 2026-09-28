# Session log — pre-submission programme

One entry per session, appended at the end of the session, in the template of `PLAN.md` §1.4.
The last entry is the start gate for the next session: it must be the previous session with
`status: COMPLETE`, or the same session with `PARTIAL` or `BLOCKED` when resuming.

---

## S0 — 2026-09-28 13:22 — Opus 5.5 (the plan assigns Sonnet 5) — status: COMPLETE
Commits: 39e0d8c [S0][item 2] Create the pre-submission programme files and ignore sources/
862e562 [S0][items 3-4] File map and section map
4da0dff [S0][item 5] Record the baseline build and checks
(the commit carrying this entry) [S0] Session log: S0 complete
Done:
- Item 1: working tree clean at da74907; tagged `pre-presubmission` (local only); created branch `presubmission`.
- Item 2: `SESSION_LOG.md`, `DECISIONS_FOR_USER.md`, `OUT_OF_SCOPE.md` and `FILE_MAP.md` created; `PLAN.md` placed here as its preamble directs (byte-identical to the supplied copy); `docs/presubmission/sources/` git-ignored (verified with `git check-ignore`).
- Item 3: `FILE_MAP.md` covers every entry S0 lists. Two read-only Explore agents (Sonnet; the plan's limit is two) gathered them; every cited file:line was then re-read, and four wrong line numbers were corrected.
- Item 4: section map of all 42 headings, with per-heading word counts, in `FILE_MAP.md` §13. Before figures for item 7: `PAPER.md` body (§1 to "Data and code", which is §13 in the PDF) **27,387 words**, total **31,825**. The template has 25,880 and 29,340. The count command is in `FILE_MAP.md` §13.
- Item 5: baseline recorded in `BASELINE_S0.md`. Nothing fixed.
- Findings later sessions need, all in `FILE_MAP.md`:
  - **No shared cluster-bootstrap function exists** (23 scripts define their own). S1's rule text and S2a must name the one they use; the precedent is `scripts/a1_ab_by_horizon.py:118-134`.
  - No local copies of arXiv 2501.10100 or 2504.16680 exist, so S1 downloads them.
  - `step5_train.py` has no M or N flag, and `WINDOW = 40` sits at `src/rwm_train.py:23`.
  - No thread settings exist anywhere (torch default; the timing artifact records 2).
  - Early `step5_*.json` artifacts lack the width field.
  - Appending a ledger entry requires updating `RESULTS.md`'s count table in the same commit.
  - Both bundle builders ship `docs/presubmission/` (`OUT_OF_SCOPE.md`, first line). This matters for S3's author query and S11's deny-list scan.
Build/checks: pass. The fast build, 8 prose checks and gates, and a second build ran at the start and again at the end; every generated text output was byte-identical to the committed tree both times, and the PDF differs only in its date and /ID. `submission_check` 20/22 (E7 and C1, known). `part_f_gate` passes the 7 checks it runs; check 4 needs a clone, and the committed record keeps it failing on 365, as published.
Paper numbers changed: none
CPU jobs over 1 min: none (each build-and-check pass took about 50 s)
Next: S1 (Opus 5.5, high effort). Read `PLAN.md` §1, S1 and Appendix C, plus `FILE_MAP.md`. Next free ledger IDs: M-74, S-20, R-76.
Decisions for user: none. Push ruling given in chat on 2026-09-28: "Push the branch now" (branch `presubmission` only; tag `pre-presubmission` stays local).

## S1 — 2026-09-28 14:12 — Opus 5.5 (session effort could not be raised to high from inside the session; subagent Sonnet 5) — status: COMPLETE
Commits: 09e6d36 [S1][items 1-2] Original specs for the M/N and baseline claims, and the Arm B check
3df0e55 PRE-REGISTER the M/N sweep and architecture-baseline rules, before the runs exist (pushed immediately; commit time 1790584927)
(the commit carrying this entry) [S1] Session log: S1 complete
Done:
- Item 1: `ORIGINAL_SPECS.md` from arXiv 2501.10100 v1 and v2, with local copies in `sources/` (git-ignored).
  - The file cites by location and sentence fingerprint, not verbatim phrases. The paper carries arXiv's non-exclusive licence, and `verify_original_specs.py` checks all 31 fingerprints and the heatmap image.
  - The ablation grid is M, N ∈ {1, 2, 8, 16, 32}. e is printed in every cell; (32, 8) is tied lowest with (32, 32).
  - The claim is an accuracy/training-time trade-off.
  - The horizon behind e is not stated, so h = 368 governs.
  - The baselines were **teacher-forced**. Table S7 gives their architectures (categorical RSSM, sinusoidal transformer).
- Item 2: **Arm B is not (32, 1).** It uses 40-row windows with eight teacher-forced targets each, against 33-row windows with one target (7,687 against 7,743 training windows). File:line citations are in `ORIGINAL_SPECS.md` §2, and (32, 1) is trained as its own arm.
- Item 3: `results/p5_sweep_power.json` and `results/p6_baseline_power.json`, from `scripts/p5_sweep_power.py` and `scripts/p6_baseline_power.py`. Both are built from Arm A seeds 0–2 at 2,500 iterations, read from stored rollouts, on the held-out arena with n_independent = 4, and both regenerate byte-identically.
  - Method: M-44's formula MDE under the same-configuration null, plus an exact-test dilution of a proportional effect. Binding MDEs are M-74 relative-L1 14.5% of the centre's error at h = 368 and 17.2% at h = 100; M-75/M-76 12.0% and 15.6%.
  - Deviation, stated in the scripts: P1's cross-architecture calibration was not used. The only real cross-configuration contrast, Arm B against Arm A, is enormous and uneven, so its SE measures effect size, not noise. It is reported as a detection check instead.
- Item 4: three rules, not two, per the user's rulings (`DECISIONS_FOR_USER.md#S1-original-vs-plan`, asked in chat):
  - **M-74**: the M/N sweep, over the original's 8 one-factor neighbours;
  - **M-75**: baselines teacher-forced, the claim as made;
  - **M-76**: baselines autoregressive.
  - Every rule uses the **exact 256-resample bootstrap**, not a Monte Carlo draw. `FILE_MAP.md` §7 found no shared bootstrap function, so each rule defines its test in full.
  - One adversarial reviewer (Sonnet) found no blocker. Its 2 should-fix and 2 minor findings were applied and reconfirmed PASS before the commit.
- Out of scope, recorded in `OUT_OF_SCOPE.md`:
  - the paper's Appendix D rows misdescribe §IV-C (no numbers, "optimal configuration") and §IV-D (omits teacher forcing);
  - p5 and p6 have no `reproduce.sh` stage;
  - Appendix E and Figure 1 do not list M-74 to M-76 until S9 regenerates them.
Build/checks: pass. After the ledger append, the fast build, all 8 prose checks and gates, and a second build all exit 0: ledger_check PASS (257 entries, 3 rules pending), 60/60 claims and 60/60 corruptions, 0 unclassified numerals, 0 suspect pointers, 27 kinds with 0 unclassified, pdf_render 5/5, 0 horizon findings. Build 1 equals build 2 byte for byte.
Paper numbers changed: `n_entries` 254 → 257 and `ledger_kb` 510 → 541 (`results/paper_numbers.json`, both from `FINDINGS_LEDGER.md`). They print in the ledger descriptions of §8, Appendix E and the README. Nothing else moved.
CPU jobs over 1 min: none (p5 14 s, p6 32 s, each build-and-check pass about 50 s).
Next: S2a (Opus 5.5, high effort). Read `PLAN.md` §1 and S2a, rule **M-74** (grep `^### M-74 ` in the ledger and read only that entry) and `FILE_MAP.md`. Where M-74 differs from PLAN S2a, M-74 governs:
- the grid is 8 configurations in M-74's priority order, not Appendix C's 6;
- the longest history is 32, so the common windows ARE §5's four held-out trajectories (starts 999, 1399, 7999, 8399) and no 432-row windows are needed;
- the verdict script implements the exact 256-resample bootstrap and Holm as M-74 states them;
- there are no baseline runs in S2a.
Then S2b follows M-75/M-76: Table S7 architectures, both regimes, 18 governing runs, and the parameter-matched variants only within the cap.
FILE_MAP §8's next-free IDs are superseded: next free **M-77**, S-20, R-76.
Decisions for user: DECISIONS_FOR_USER.md#S1-original-vs-plan (three questions, answered 2026-09-28).
