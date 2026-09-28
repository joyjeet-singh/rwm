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

## S2a — 2026-09-28 15:12 — Opus 5.5 (session effort could not be raised from inside the session; one reviewer on Sonnet 5) — status: COMPLETE
Commits: bda0ebb [S2a][item 1] Configurable M and N for rule M-74, with a bitwise differential test
cb9204c [S2a][items 2-3] Common-window evaluator, and the centre re-scored on it
51c3d7f [S2a][item 4] Verdict script for rule M-74, committed before any sweep run
2097c9b [S2a][items 5-6] Queue runner, and the timing probe against the cap (pushed before launch)
ae7a7fe [S2a][item 7] Queue launched: RUN_QUEUE.md, the launch record, and unbuffered run logs
(the commit carrying this entry) [S2a] Session log: S2a complete
Done:
- Item 1: `scripts/step5_train.py --sweep --history M --forecast N` builds windows of M + N rows and sets the config's horizons. Nothing else changes.
  - Artifacts go to `results/mn_sweep_run_M*_N*_seed*.json`, weights to `runs/mn_M*_N*_seed*/`, both outside every `results/step5_*` glob the paper reads.
  - The window count is asserted against the episode lengths in every run.
  - `scripts/mn_sweep_differential.py` checks bitwise identity to Arm A seed 0's stored trace, first 20 iterations, all six terms. Both the new path at (32, 8) and the edited default path pass (`results/mn_sweep_differential.json`).
  - Training-window counts: (32,8) 7,687; (32,32) 7,495; (16,8) 7,815; (32,16) 7,623; (8,8) 7,879; (32,2) 7,735; (32,1) 7,743; (2,8) 7,927; (1,8) 7,935.
- Items 2–3: `scripts/mn_sweep_eval.py`, the common-window evaluator.
  - The held-out windows are §5's four trajectories (starts 999, 1399, 7999, 8399; asserted), with `n_independent = 4`; the in-sample arena has 16.
  - For every configuration, the history is the M rows before the same 368 target rows.
  - The centre, Arm A seeds 0–2 at 2,500 iterations, was re-scored by inference only (`results/mn_sweep_centre.json`). It reproduces the head-to-head table to 3.9e-8.
- Item 4: `scripts/verdict_mn_sweep.py` implements M-74 exactly.
  - It uses the exact 256-resample bootstrap imported from `p5_sweep_power.py`, Holm with ties broken by M-74's grid order (validated against the grid), the four branches, and the failure path.
  - `--self-test` passes 23 checks: every branch, the sign structure, Holm stops, ties and drops, 300 random families, and 5 end-to-end cases.
  - One adversarial reviewer (Sonnet) found 1 blocker (tie-break order taken from the queue unvalidated) and 2 should-fix items; all were fixed and reconfirmed PASS.
  - Committed and **pushed (2097c9b) before launch**.
- Items 5–6: `scripts/queue_runner.sh` (never edited while running) and `scripts/queue_run.py` (arch dispatch plus a check of every finished artifact). The runner was tested on a dry queue: skipping, an unknown arch, a failed check, and the success branch of the check.
  - The timing probe, calibrated against Arm A's own wall clock, projects **19.53 CPU-hours** against the 25-hour cap, so nothing is dropped and no ledger entry is needed.
  - The queue holds 24 runs, written in M-74's priority order.
- Item 7: **launched 14:51:27 +0530** with the plan's `nohup caffeinate -i` command. The first run, (32, 32) seed 0, has passed 500 iterations, with every parameter finite at 250 and 500.
  - Its log stays empty until it ends, because of Python output buffering. `queue_run.py` now starts later runs unbuffered, a logging-only change.
  - `docs/presubmission/RUN_QUEUE.md` records the runs, the projection, a finish at about 2026-09-29 10:23 +0530, and the status command.
Build/checks: pass. The fast build, all 8 checks and gates, and a second build ran before launch, and every generated output was byte-identical to the committed tree; S2a changes nothing the paper reads. The build was not re-run after launch, so as not to take CPU from the first run. Nothing that feeds the paper changed after that check.
Paper numbers changed: none
CPU jobs over 1 min: all before launch — the differential test (45 s, then 60 s), the timing probe (3.4 min, then 3.4 min), and one build-and-check pass (about 50 s). After launch: one checkpoint-finiteness check (under 5 s), overlapping the first run.
Next: S2b (Opus 5.5, high effort). Read `PLAN.md` §1 and S2b, `ORIGINAL_SPECS.md` §(b), rules **M-75 and M-76** (ledger entries only) and `FILE_MAP.md`. The rules govern where they differ from PLAN S2b: Table S7 architectures, both regimes, 18 governing runs, parameter-matched variants only within the 20 CPU-hour cap.
- Add each baseline trainer to `TRAINERS` in `scripts/queue_run.py`, with its checks. **Never edit `scripts/queue_runner.sh`.**
- Name baseline artifacts outside `results/step5_*`, append the runs to `runs/queue.txt` after the sweep lines, and update `RUN_QUEUE.md`.
- If the runner has already exited when the runs are appended, relaunch it with the same command. It skips done and failed ids.
- Timing probes during S2b compete with the running queue: log them.
Decisions for user: none.

## S2b — 2026-09-28 19:00 — Opus 5.5 (session effort could not be raised from inside the session; one reviewer on Sonnet 5) — status: BLOCKED
Commits: c3273be [S2b][item 1] State-only check, and the baselines' specifications with their sources
520b59e [S2b][items 2-4] The three baselines and their trainer
2a834ad [S2b][item 5] Verification ladder: every baseline passes every rung
5785260 [S2b][item 6] Evaluator and verdict script for rules M-75 and M-76, before any baseline run (pushed)
(the commit carrying this entry) [S2b] BLOCKED at the baseline cap: timing record, queue dispatcher, log
Done:
- Item 1: RWM's state prediction does not read its auxiliary branch (`BASELINE_SPECS.md` §1).
  - The pinned upstream ships an MLP base and its autoregressive path, so the MLP baseline is a port of the authors' own code.
  - The 38-row deviations table has no UNVERIFIED rows.
  - The RSSM's settings come from DreamerV2 and PlaNet, both verified against the arXiv API page by page (`results/baseline_citations_verified.json`).
- Items 2–4: `src/baselines/` holds the MLP, transformer and RSSM at Table S7 sizes (610,484 / 132,148 / 3,180,468 parameters), plus parameter-matched variants within 5% of 714,164.
  - All reuse RWM's state head, objective and causal slicing, in both regimes.
  - `scripts/train_baseline.py` keeps Arm A's pipeline.
- Item 5: the ladder passes for all six variants (`results/baseline_verification.json`). Rung results:
  - zero delta is exactly hold-last;
  - memorisation reaches at least 100×;
  - the first 10 losses are bitwise-deterministic;
  - action alignment holds in both regimes and in rollout.
- Item 6: `scripts/baselines_eval.py` (it reuses the sweep evaluator; RWM reproduces the head-to-head table) and `scripts/verdict_baselines.py` (M-75 and M-76 exactly; 19-check self-test).
  - One Sonnet reviewer found 0 blockers, 1 should-fix and 1 minor; both were fixed and reconfirmed.
  - Committed and **pushed before any baseline run**.
- Item 7: **BLOCKED.** The timing probe projects the 18 governing Table S7 runs at 22.01 CPU-hours against the 20-hour cap, so nothing is queued (`DECISIONS_FOR_USER.md#S2b-baseline-cap`). The parameter-matched variants would bring every baseline run to 46.07 h, so they are not run.
  - `scripts/queue_run.py` already dispatches all twelve arch-regime-spec strings. Its sweep path was re-checked on two finished sweep runs.
Build/checks: not re-run at this stop. No file the paper reads has changed since S2a's pre-launch pass; src/baselines and the new scripts are read by nothing in the build.
Paper numbers changed: none
CPU jobs over 1 min: all overlapped the M-74 sweep and inflate its `wall_clock_s`.
- **Verification ladder:** 59 min on one thread, 17:47–18:46, overlapping `mn_M32_N32_s2`. This is well over PLAN §1.5's "about 10 CPU-minutes"; it was the necessary S2b step, run on one thread to halve the contention.
- **Timing probe:** 12.1 min, 18:48–19:00, overlapping `mn_M16_N8_s0`.
- **Smaller jobs:** the evaluator self-test (about 2 min, twice), the verdict self-tests (about 1 min each) and the 3-iteration smoke tests (about 2 min).
Next: the user answers `DECISIONS_FOR_USER.md#S2b-baseline-cap`, then `Resume session S2b.` The remaining S2b work is to append the Table S7 runs to `runs/queue.txt` (`scripts/baselines_timing.py --write-queue` refuses while blocked, so the resume follows the ruling), update `RUN_QUEUE.md`, log COMPLETE and push. The sweep keeps running meanwhile (3 of 24 runs done at 18:48).
Decisions for user: DECISIONS_FOR_USER.md#S2b-baseline-cap

## S2b — 2026-09-28 19:10 — Opus 5.5 (resumed in the same session after the ruling) — status: COMPLETE
Commits: c030999 [S2b] BLOCKED at the baseline cap: timing record, queue dispatcher, log
(the commit carrying this entry) [S2b][item 7] Baselines queued under the user's cap ruling
Done:
- The user ruled in chat, "Raise cap; queue all 18", recorded verbatim at `DECISIONS_FOR_USER.md#S2b-baseline-cap`. The baseline cap is now 23 CPU-hours, covering the 22.01-hour projection.
- `scripts/baselines_timing.py --from-record-cap 23 --ruling …` queued from the committed probe record, with no re-probe. The record keeps the original block beside the ruling (`blocked_before_ruling`, `cap_hours_before_ruling`).
- **18 Table S7 runs appended to `runs/queue.txt`** after the 24 sweep lines: M-75 (tf) then M-76 (ar), each MLP, RSSM, transformer, seeds 0–2. The parameter-matched variants (46.07 h in all) do not fit and are not run, as M-75 and M-76 require.
- The baseline dispatch was tested end to end (MLP, 3 iterations): every field check passed, and the only failure was the expected missing checkpoint. The test files were removed.
- `RUN_QUEUE.md` updated. The projected finish of the whole queue is about 2026-09-30 08:23 +0530.
- The rules text needed no ledger entry: M-75 and M-76 pre-registered that S2b stops for the user's decision, and the decision is recorded and pushed before any baseline data exists.
- The ladder passes for all three baselines; the deviations table has no UNVERIFIED rows; the verdict script was committed and pushed before any baseline run (5785260).
Build/checks: not re-run. Nothing the paper reads has changed since S2a's pre-launch pass, which had every check passing.
Paper numbers changed: none
CPU jobs over 1 min: see the BLOCKED entry above. Since then, only the 3-iteration dispatch test (about 15 s).
Next: S3 (Opus 5.5, high effort). Items 1, 2 and 4: text only, so it can run while the queue trains. It is limited to jobs under about 10 CPU-minutes, each logged if over 1 minute. S3's item 4 computes `results/alignment_defect_ci.json`, which is inference on the released checkpoint: keep it short. Check the queue with `RUN_QUEUE.md`'s command.
Decisions for user: none open (S2b-baseline-cap answered).

## S3 — 2026-09-28 19:30 — Opus 5.5 (session effort could not be raised from inside the session) — status: BLOCKED
Commits: 12e9da6 [S3][items 1-2] §5 names the setting of every h = 8 figure, and every arm table names its checkpoint
(the commit carrying this entry) [S3] BLOCKED at item 4: the alignment defect's 75% does not survive independent trajectories
Done:
- Item 1: every h = 8 statement is traced (`docs/presubmission/S3_ITEM1_TRACE.md`).
  - The plan's lead was wrong. The prose's 0.008 is M-23's single-seed estimate at the table's own 10,000-iteration checkpoint; "0 of 4" counts three-seed cells at 500 and 2,500.
  - Case (a): each figure now names its setting through bound keys. The advantage is described as small at the training horizon and large beyond it. Figure 2's caption names its checkpoint.
  - Guard: `check_h8_gap_labels`.
  - R-42's single-seed interpretation, now contradicted, goes to OUT_OF_SCOPE for the user.
- Item 2: all seven arm tables name their training iterations, bound (`iters_main` / `iters_long`). The head-to-head caption explains 0.5856 against 0.3582.
  - Guard: `check_arm_table_captions`.
  - §7.4 has no table, as recorded in OUT_OF_SCOPE.
- Items 1–2 checks: all pass; the gate self-test catches 6 of 6; two consecutive builds are byte-identical.
- Item 4: **BLOCKED** (`DECISIONS_FOR_USER.md#S3-alignment-defect`). `results/alignment_defect_ci.json` reproduces the published 75% and 9.5% exactly, but only on Protocol A's ten overlapping sampled windows, where one trajectory makes the 75%.
  - On §5's four independent held-out trajectories: relative-L1 7.9% [3.1, 13.0], nRMSE form 1 6.6% [1.0, 8.0].
  - On all twenty: the sign reverses, with intervals spanning zero.
  - The §7.2 evidence and the author query both depend on the ruling and are not done.
Build/checks: pass, after items 1–2. The item 4 work so far adds a script and an artifact that nothing in the build reads.
Paper numbers changed: `pdf_pages` 48 → 49 and `tn_typed` 686 → 691 (both generated). Added keys: `iters_main`, `iters_long`, `m23_seed`, `bu_ckpts`.
CPU jobs over 1 min, all overlapping the queue's runs:
- build-and-check passes: 1 min 8 s, then 2 × about 1 min;
- `alignment_defect_ci.py`: 3 min 39 s, twice.
Next: the user answers `DECISIONS_FOR_USER.md#S3-alignment-defect`, then `Resume session S3.` Item 4 then continues under the ruling:
- the text in §7.2, §3.1 and the contribution bullet;
- the reset-row evidence in §7.2;
- the author query.
Decisions for user: DECISIONS_FOR_USER.md#S3-alignment-defect

## S3 — 2026-09-28 19:55 — Opus 5.5 — status: COMPLETE
Commits:
- a1eb779 [S3][item 4] `scripts/alignment_defect_ci.py` and `results/alignment_defect_ci.json` (before the block)
- f08ac92 [S3][item 4] Ledger S-20: the alignment defect's 75% / 9.5% framing withdrawn. It is committed on its own, because `paper_numbers.py` asserts that a commit introduces each S- heading.
- 798a362 [S3][item 4] The alignment defect restated on independent trajectories
- (the commit carrying this entry) [S3] COMPLETE: the author query draft and this entry
Done:
- Item 4, under the ruling "Restate on independent":
  - §7.2 gives the four-trajectory figures in both metrics with intervals, the per-trajectory values, the twenty-trajectory reversal, the reset-row evidence for the convention, and the statement that every arena is in-sample for this checkpoint.
  - §3.1 and the contribution bullet give both metrics side by side at h = 368.
  - "Materially better" is gone. 75% and 9.5% are named once, in §7.2, with S-20.
  - Every figure is bound from `results/alignment_defect_ci.json`.
- The abstract carries one metric, nRMSE form 1 with its interval. Both metrics put it at 20 numerals against C12.1's 18; the check was not loosened. `DECISIONS_FOR_USER.md` records this under "How S3 applies it".
- A defect the build did not catch: S-20 made the paper say "the second pre-submission review entered one more framing retractions", and BUILD_CHECKS say "would have said seven and enumerated two".
  - Cause: the framing-cohort keys meant "the latest cohort".
  - Fix: they are now pinned to the last cohort committed before `PLAN.md` was added. The new key `n_framing_through_review_word` holds the counterfactual.
  - An assert requires every cohort to be accounted for. Both sentences read four and six again.
- Author query: `docs/presubmission/AUTHOR_QUERY_ALIGNMENT.md`, generated by `s3_write_author_query.py`. That script asserts the pinned upstream heads and the cited lines, re-checks the reset-row actions against the data, and reads every figure from the artifact.
  - Four changes from Appendix D's wording, with reasons in the file: "higher under the evaluation pairing" rather than "lower"; the reversal is added; both repositories are named; and the arena is described as trajectories, not "held-out".
  - [first author] and [name] stay placeholders. It is **not sent**, and no paper sentence says the author was asked.
Build/checks: all pass. 60/60 comparative claims are verified and 60/60 corruptions caught. The gate self-test catches 6 of 6; no typed numeral is unclassified; C12.1 has 17 numerals against a limit of 18. Two consecutive build-and-check passes are byte-identical, and the deny-list scan of every new file gives 0 hits.
Paper numbers changed (all generated):
- `n_superseded` 19 → 20, `n_retract_framing` 6 → 7 (and its word forms, ids and list), `n_retract_total` 12 → 13;
- `n_entries` 257 → 258, `ledger_kb` 541 → 543, `n_framing_cohorts` 3 → 4, `tn_typed` 691 → 694.
- Added: `ad_nind`, `ad_rel`, `ad_rel_ci`, `ad_nrmse`, `ad_nrmse_ci`, `ad_rel_traj`, `ad_nrmse_traj`, `ad_pa_n`, `ad_pa_out_row`, `ad20_nind`, `ad20_rel`, `ad20_rel_ci`, `ad20_nrmse`, `ad20_nrmse_ci`, `ad20_traj_lo`, `ad20_traj_hi`, `n_framing_through_review_word`.
CPU jobs over 1 min, all overlapping the queue: four double build-and-check passes of about 2 min each. The queue stands at 4 done, 0 failed.
Next:
- S4. **Install PLAN Appendix A's abstract with its alignment sentence rewritten to the independent figure**: keys `ad_nind`, `ad_nrmse` and `ad_nrmse_ci`, not 75% and 9.5%. Keep it within C12.1's 18 numerals.
- S5's "75%" sweep:
  - must fix `docs/EXTERNAL_READ_BRIEF.md:51-52`, which still gives 75% / 9.5% as a finding. C11.3 keeps it synced with `stale_pct`, so the fix is to its framing, not to the number.
  - `docs/CLAIMS_AUDIT.md:308` also quotes "materially better". It is a dated audit record, so it is left as history unless S5 rules otherwise.
- `make_anon_bundle.py` walks `docs/`, including `docs/presubmission/`, which holds this programme's records and the query draft. The bundle session should decide whether that directory ships.
Decisions for user: none new. Sending `AUTHOR_QUERY_ALIGNMENT.md` is the user's (PLAN, "After S3").

## S4 — 2026-09-28 23:45 — Opus 5.5 — status: COMPLETE
Commits:
- 4a71b31 [S4] Record the abstract-budget and title rulings
- 8e26f38 [S4][item 6] Broader impact replaced with PLAN Appendix B
- 9753713 [S4][item 3] The per-horizon fix: unseen by the multiplier, not by the model
- 18a0f67 [S4][item 5] Title "Right Order, Wrong Size", seven contributions, and the introduction
- ca4087d [S4] Abstract replaced with PLAN Appendix A, every number bound
- dabb268 [S4] Abstract: the ten-episode reversal is scoped to training data
- (the commit carrying this entry) [S4] COMPLETE: session log
Done:
- **Rulings, asked in chat before any edit** (`DECISIONS_FOR_USER.md#S4-abstract-budget`):
  - "Full Appendix A; raise cap". Appendix A measured 347 words and 23 numerals under C12.1's own counter; restated on S3's independent alignment figures it needed 26, against a cap of 18.
  - "Right Order, Wrong Size (Recommended)".
- **Item 6.** §10 is Appendix B's text, with four bound numbers: `v2_deploy_h`, `d1n_epi_ratio_h100`, `d1n_epi_cov1_h100`, `v3_cov_nominal1`.
- **Item 3.**
  - §6.8 defines "unseen by the multiplier" and "unseen by the model" once, and says every released-checkpoint cell is the first kind only.
  - The table gains an Arm A column: `d3x_own_epi_ok` / `d3x_own_epi_cells` = 17 / 36 and `d3x_own_ale_ok` / `d3x_own_ale_cells` = 10 / 36. It names `{{iters_main}}` iterations, and `paper_numbers.py` asserts the cross-model artifact is at it.
  - The caveat, in at most one extra sentence each, is in: the contribution bullet, §2 (twice), §6.8's lead and closing, §6.10, §6.11, §9, §11 and §12. "Looks repairable" is gone.
  - The §3.2 verdict cell (`scripts/evidence_summary.py`, rerun) carries the Arm A count.
- **Item 5.**
  - Title installed.
  - Eleven bullets became seven, in the plan's order, each at most three sentences. Every number that left the contributions is still in the body; `e7_n_new` and `e7_n_beaten` exist nowhere else, so they stay.
  - The introduction's first two paragraphs state the title's answer, with no new claim.
- **Abstract.**
  - Appendix A, every listed number bound, and the alignment sentence on S3's independent figures in both metrics with both intervals.
  - 330 words and 26 numerals. Trimmed from 352 words without dropping a claim or a number.
- **Checks changed.**
  - C12.1's `max_numerals` 18 → 26, set at the installed count, with the ruling recorded beside the three earlier raises. The word cap is unchanged at 370.
  - **Re-anchor:** C9.1's `says` moved to the new abstract's per-horizon sentence; its k-of-k scan is unchanged.
- **Values that differ from Appendix A's draft, with the artifact's value used:**
  - 75% [CI] / 9.5% [CI] → 6.6% [1.0, 8.0] nRMSE and 7.9% [3.1, 13.0] relative-L1, on the same four trajectories, by S3's ruling.
  - +0.470 and 89% are the draft's roundings of the body's +0.4697 (`e7_step_r`) and 89.15% (`v1_shared_pct`), printed through the new keys `e7_step_r3` and `v1_shared_pct0` from the same artifacts. S10's checklist item 11 should read them as the same numbers.
  - 2.03× is bound to `r2_total_x_h100` (h = 100). "At 100 steps" was added so the 5.2× names its horizon.
  - The arXiv version tags (v1) are kept.
- **Review** (subagent 2 of 2, Sonnet 5, read-only): 1 SHOULD-FIX, fixed in dabb268 (the reversal is now scoped to training data), and 1 NIT, fixed. Subagent 1 was the Explore sweep for item 3.
- **OUT_OF_SCOPE**, four new lines:
  - `README.template.md:57-59` and `scripts/build_model_card.py:177` state the multiplier result unscoped; S5's '"held-out" near "multiplier"' sweep owns them.
  - Figure 1's caption (`scripts/build_paper.py:337`) and §6.6 (`PAPER.template.md:1000-1002`) apply "held-out" to the released checkpoint.
Build/checks: pass.
- 60/60 comparative claims verified and 60/60 corruptions caught; the gate self-test catches 6 of 6.
- 0 unclassified typed numerals; 0 scope findings; `ledger_check` PASS.
- C12.1: 330 words, 26 numerals.
- Two consecutive build-and-check passes are byte-identical.
- Deny-list: 0 hits in every file S4 changed. MODEL_CARD.md's hits predate S4; that file is scrubbed by the bundle builder by design.
Paper numbers changed (all generated): `tn_typed` 694 → 688; `evidence_table` (the §6.8 row). Added: `e7_step_r3`, `v1_shared_pct0`.
CPU jobs over 1 min, all overlapping the queue: seven double build-and-check passes and one single pass, about 2 min each. The queue stands at 11 done, 0 failed.
Next:
- S5.
  - Its '"held-out" within 2 lines of "multiplier"' sweep should take the README and model-card lines above.
  - "Orders of magnitude" remain in the introduction's second paragraph, for item 8.
  - The old title remains in `docs/SUBMISSION_PACKAGE.md`, and in `docs/presubmission/PLAN.md` / `FILE_MAP.md`, which are records.
  - `docs/EXTERNAL_READ_BRIEF.md`'s 75% is still S5's, from S3.
Decisions for user: DECISIONS_FOR_USER.md#S4-abstract-budget (answered)
