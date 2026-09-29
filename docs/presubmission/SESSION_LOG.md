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

## S5 — 2026-09-29 00:15 — Opus 5.5 (the plan assigns Sonnet 5; subagents Sonnet 5) — status: COMPLETE
Commits:
- d60da15 [S5] Neither bundle ships docs/presubmission/
- 45ede7e [S5][item 8] One vocabulary for withdrawals, bound ranges for orders of magnitude, and the sweep
- (the next commit) [S5] C7.5 names both places it checks (review nit)
- (the commit carrying this entry) [S5] COMPLETE: session log
Done:
- **Step 1, the sweep.** One Explore agent (Sonnet) swept the paper, README, model card, captions and docs for all five patterns; every hit it cited was re-read before any edit.
- **Step 2, retraction counts.**
  - One vocabulary: claims withdrawn on evidence (6), framings withdrawn (7), superseded entries (20). The remaining 7 are early hypotheses closed as housekeeping.
  - `scripts/ledger_check.py` classifies every S- entry, refuses any that fits no class, and writes the classes to `results/claims_to_evidence.json`. `paper_numbers.py` reads them from there, with a staleness assert, instead of classifying again.
  - The introduction (which printed a combined 13), §8, the README and BUILD_CHECKS now use the vocabulary. The README's typed "four" is now bound.
  - New gate `check_retraction_counts` in `build_paper.py`: the introduction and §8 must each state all three counts after their own keys, and neither may print the old total. It is in the self-test (7 of 7) and documented in BUILD_CHECKS.
- **Re-anchors (§1.2.8), each logged in the check:**
  - C7.1 (2 → 3 sites) and C7.2 (2 → 3 sites);
  - C7.5, from the retired total to the superseded count (1 → 2 sites);
  - C10.5: `says` moved, and its evidence-class recogniser gains "withdrawn on evidence";
  - C11.1: `n_retractions_word` → `n_retractions_lower`, plus `n_superseded` (6 → 7 keys);
  - C11.3: +8 keys (15 → 23). None is weaker; the review confirmed this.
- **Step 3, orders of magnitude.** Each decision, with its data:
  - intro "three to four" (σ) → bound range: 10^3.26–10^4.32, `d1n_alea_ratio_h1`–`h368`;
  - intro "one to two" (disagreement) → bound range: 10^0.92–10^1.54, `d1n_epi_ratio_h1`–`h368`. Both ends are the true minimum and maximum over horizons, and both are scoped "on data it trained on";
  - §6.2 "three to four orders too small" → the same σ range, bound;
  - §6.3 "an order of magnitude closer" → dropped, "closer": 33.4 / 10.5 ≈ 3.2×;
  - Appendix G "differ in scale by orders of magnitude" → "differ widely in scale": the form-2 denominators span about 48× in the units the error is computed in, and no artifact holds them;
  - Figure 2's caption, "grows by an order of magnitude" → bound range 1.79–6.11× over steps 1–8, new keys `err_growth_lo` / `err_growth_hi`;
  - kept, exactly true: §6.2's "between one and four orders" (the four models' aleatoric ratios are 10^1.04–10^3.90) and "error grows by an order of magnitude" (×11.35, h = 1 → 368);
  - kept, records: BUILD_CHECKS' quotation of a historical defect and self-test prose, `docs/APPENDIX_G_RULES.md:472` (pre-registered rule text), and `docs/C1_REVIEW_CHECKLIST.md` / `CLAIMS_AUDIT.md` (dated audit records).
- **Step 4, old title.** It is gone from the paper (since S4) and from the bundle. The ruling "Exclude the directory (Recommended)" (`DECISIONS_FOR_USER.md#S5-bundle-presubmission`) removes `docs/presubmission/` from both builders. A dry run gives 459 files, none holding the old title. The README never mirrored the title.
- **The consistency sweep beyond item 8:**
  - the README's "interval is repairable", the model card's remedy and `docs/EXTERNAL_READ_BRIEF.md` now carry S4 item 3's caveat and the 17 / 36. The model card's own ensemble-5 checkpoints are the Arm A models that manage it;
  - the brief no longer presents 75% / 9.5% as a finding. It names them withdrawn (S-20) and gives the independent figures and the new counts.
- **Review** (subagent 2 of 2, Sonnet, read-only): PASS, with one NIT, fixed (C7.5's `where`).
- **OUT_OF_SCOPE**, three lines: the stale submission documents (`SUBMISSION_PACKAGE.md`, `COVER_STATEMENT.md`, stale in title, counts, the multiplier claim and checksums); §6.2's "σ nearly flat" (it grows 2.74×); and `docs/E4_REPLY_DRAFT.md`'s stale counts.
Build/checks: pass.
- 60/60 comparative claims verified and 60/60 corruptions caught; the gate self-test catches 7 of 7.
- 0 unclassified typed numerals; 0 scope findings; `ledger_check` PASS with the retraction classes.
- Two consecutive build-and-check passes are byte-identical.
Paper numbers changed (all generated): `tn_typed` 688 → 690. Added: `err_growth_lo` (1.79) and `err_growth_hi` (6.11). Ten count keys now name `results/claims_to_evidence.json (scripts/ledger_check.py)` as their source; their values are unchanged.
CPU jobs over 1 min, all overlapping the queue:
- four double build-and-check passes and one single pass, about 2 min each;
- one per-dimension scale computation, a few seconds.
The queue stands at 12 done, 0 failed.
Next:
- S6 (item 7, part 1). The body is longer than at S0 after S3–S5's additions; S6 and S7 measure against `BASELINE_S0.md`.
- The submission documents in OUT_OF_SCOPE need a refresh once the paper is frozen.
Decisions for user: DECISIONS_FOR_USER.md#S5-bundle-presubmission (answered)

## S6 — 2026-09-29 00:50 — Opus 5.5 — status: COMPLETE
Commits:
- 1b7131e [S6][item 7] §1-§4 shortened, their drafting history moved to BUILD_CHECKS
- aba094a [S6][item 7] §5 and §5.1 shortened; rule IDs at first mention; §5's history moved
- (the commit before this entry) [S6][item 7] Restore what the cut lost (independent audit)
- (the commit carrying this entry) [S6] COMPLETE: session log
Done:
- **Item 7, part 1, from the title page to the end of §5.1.** Words are counted with S0's convention (FILE_MAP §13) on the rendered `PAPER.md`, before → after:

  | section | before | after |
  |---|---:|---:|
  | §1 | 1,023 | 879 |
  | §2 | 2,093 | 1,613 |
  | §3 | 530 | 505 |
  | §3.1 | 851 | 708 |
  | §3.2 | 569 | 551 (a generated table) |
  | §4 | 488 | 378 |
  | §5 | 2,403 | 2,011 |
  | §5.1 | 317 | 289 |
  | **range** | **8,274** | **6,934** (−16.2%) |

  The body (§1 to "Data and code") went from 27,921 at S6's start to 26,581. S0's baseline was 27,387; S3–S5 had added 534.
- **Drafting history moved, not deleted,** to `docs/BUILD_CHECKS.md` under "Moved from the paper body (pre-submission edit)". There are 8 items, labelled [§3.1], [§4] and [§5]:
  - the every-build citation check;
  - why §3.1 exists;
  - the coverage properties earlier drafts omitted;
  - the withdrawn "deployment horizon" label;
  - §4's untested-count history (the paper keeps one sentence citing `S-17`);
  - the M-46 note;
  - why §5 states the h = 1 floor result;
  - the M-16 → M-23 re-anchoring history.
- **Rule IDs.** Each is given once per section, at first mention, as "(rule M-23, Appendix E)", and likewise for M-64 and M-16; all three are confirmed rows in Appendix E. R-75, X-13, D-35 and D-36 are removed from running prose, and their artifacts stay cited.
- **Caveats stated once.** The in-sample caveat for the released checkpoint and the n = 4 / 256-resample caveat are now in §3, and §5 refers back to both. S7 can point §6's repetitions at the same two.
- **Every key is kept.** A replacer asserted it section by section. Two keys left the paper and are printed in the moved section: `v3_n_citations` and `appF_n_polhw_lower`. Both tables in §5 are byte-identical except one row label ("(M-23)" → "(pre-registered)").
- **Checks.** None was re-anchored or retired. C19.1 fired once, because a list of moved items read as one sentence holding a typed "h = 1" beside "correction" and "horizon"; that was fixed by rewording the moved text.
- **Review** (subagent 1 of 1, Sonnet, read-only claim-by-claim audit): FAIL with 2 SHOULD-FIX (§1's "stronger sense" framing and §5's "the split is ours", both lost) and 2 NITs. All four were restored, and the counts above include them.
Build/checks: pass.
- 60/60 comparative claims verified, and the gate self-test catches 7 of 7.
- 0 unclassified typed numerals; 0 scope findings.
- Two consecutive build-and-check passes are byte-identical.
Paper numbers changed: none measured. `tn_typed` and `pdf_pages` move with the text; all are generated.
CPU jobs over 1 min, all overlapping the queue: nine single build-and-check passes, about 1 min each. The queue stands at 13 done, 0 failed.
Next:
- **S7: §6–§13 and appendix drafting-prose.**
  - S7 needs the body at or below 19,170 to meet the 30% target, a cut of 7,411 words (about 38%) from §6–§13, which now hold about 19,650. S6's range, which is mostly results, gave 16%.
  - Per the plan, S7 reports the shortfall and lists the largest remaining sections rather than forcing cuts.
  - The moved-text section is ready to extend, and the replacer and check scripts are in the scratchpad (not committed).
- **Trap for S7:** C19.1 (the typed-restatement check) scans the paper plus BUILD_CHECKS as one text, and a markdown bullet list reads as one sentence. Moved items must not put a typed horizon beside words another sentence shares with a bound horizon.
Decisions for user: none

## S7 — 2026-09-29 01:40 — Opus 5.5 — status: COMPLETE
Commits:
- 3c1ae49 [S7][item 7] §6 lead-in to §6.3 shortened; caveats point back to §3 and §11
- b17be21 [S7][item 7] §6.4-§6.7 shortened; drafting history moved; S-15 cited once
- f27025f [S7][item 7] §6.8-§6.11 shortened; unpowered and independence caveats stated once
- 2dffcda [S7][item 7] §7-§12 and appendix drafting prose; S-12 and S-15 cited once each
- 978a6a0 [S7][item 7] Restore what the cut lost (independent audit)
- (the commit carrying this entry) [S7] COMPLETE: session log
Done:
- **Item 7, part 2: §6–§13, plus the appendix prose that narrated drafting.** Rendered `PAPER.md`, S0's convention, before (9ad4c24) → after:

  | section | before | after | | section | before | after |
  |---|---:|---:|---|---|---:|---:|
  | §6 lead-in | 73 | 56 | | §6.9 | 192 | 192 |
  | §6.1 | 548 | 488 | | §6.10 | 966 | 887 |
  | §6.2 | 2,205 | 1,968 | | §6.11 | 1,278 | 1,226 |
  | §6.3 | 1,828 | 1,729 | | §7 (7.1–7.5) | 888 | 827 |
  | §6.4 | 626 | 512 | | §8 | 596 | 518 |
  | §6.5 | 122 | 122 | | §9 | 769 | 687 |
  | §6.6 | 1,363 | 1,225 | | §10 | 200 | 200 (S4's text) |
  | §6.7 | 2,791 | 2,549 | | §11 | 2,186 | 1,854 |
  | §6.8 | 1,585 | 1,416 | | §12 | 918 | 850 |
  | | | | | Data and code | 513 | 513 (disclosures) |

  The range went from 19,647 to 17,819 (−9.3%).
- **Final report against the target (the plan's S7 duty).**
  - The body (§1 to Data and code) is **24,753 words** against S0's 27,387, a cut of **2,634 words (9.6%)**.
  - The target was ≤ 19,170 (30%). **The shortfall is 5,583 words.** Per the plan, the cut is under 30%, so no cuts were forced.
  - **The largest remaining sections:** §6.7 2,549; §5 2,011; §6.2 1,968; §11 1,854; §6.3 1,729; §2 1,613; §6.8 1,416; §6.11 1,226; §6.6 1,225; §6.10 887; §1 879; §12 850.
  - What is left is results, tables and the qualifications S3–S5 required; the drafting history is out. Reaching 30% would mean removing measured content or moving whole analyses to the supplement, which is a decision for the user, not a style edit.
- **Drafting history moved, not deleted.** 21 items went to BUILD_CHECKS' "Moved from the paper body (pre-submission edit)", labelled [§6.2], [§6.3], [§6.4], [§6.6], [§6.7], [§6.10], [§7.4], [§8], [Appendix B], [Appendix D] and [Appendix E]. With S6's 8, the section holds 29.
- **Rule IDs.** Each rule is named once per section at first mention, as "(rule M-xx, Appendix E)"; all were checked against Appendix E's 17 rules. The ledger notes M-24, M-54 and M-71 stay as plain pointers. D-13 is removed from prose.
- **Retractions.** One sentence per retraction that changed a claim: `S-15` in §6.6, §9 and §12; `S-12` in §8; `S-20` in §7.2.
- **Caveats stated once and referred back:**
  - the in-sample and n = 4 / 256-resample caveats (§3);
  - "not N independent successes" (the §6.8 caution);
  - "bounds what it reports, not what it costs" (the policy caveat of §11);
  - "unpowered" (once in §6.8).
- **Nothing lost mechanically.** Every table is byte-identical, spliced in rather than retyped. The replacer asserted per section that no key vanished: those that left a section are printed elsewhere or in the moved section (`v1_n_citations`, `n_framing_last_cohort_word`).
- **No numeric assertion was retired. Re-anchors, each logged beside the check:**
  - `scripts/a1_consent_letter.py`'s §6.1 closing marker; it extracts the same five quoted fragments as before;
  - C22.1's `says`;
  - C3.4's `says`.
  C2.2's phrase was restored in the text instead.
- **Two traps met.**
  - C19.1's sentence splitter breaks only at ". ". A line break straight after a period, and markdown bullet lists, join sentences, so a typed horizon can collide with a bound one. It was fixed each time by rewording, never by changing the check.
  - C14.1 scans BUILD_CHECKS too, so moved text must bind its horizons.
- **Audit** (subagent 1 of 1, Sonnet, claim by claim against 9ad4c24): FAIL with 1 BLOCKER (§9's "an interval beside a trajectory count overstates precision", lost), 1 SHOULD-FIX (§6.2's reason h = 100 is tested) and 1 NIT. All three were restored, and the counts above include them.
Build/checks: pass.
- 60/60 comparative claims verified, and the gate self-test catches 7 of 7.
- 0 unclassified typed numerals; 0 scope findings.
- Two consecutive build-and-check passes are byte-identical.
Paper numbers changed: none measured. `tn_typed` and `pdf_pages` move with the text; all are generated.
CPU jobs over 1 min, all overlapping the queue: about 16 single build-and-check passes, about 1 min each. The queue stands at 14 done, 0 failed.
Next:
- S8 (queue gate and evaluation). The queue is projected to finish around 2026-09-30 08:23; S8 must not start before it finishes.
- For S10's checklist item 7: the body is 24,753 against a target of 19,170, and the shortfall is reported here with the largest sections listed.
Decisions for user: none raised. Whether to move whole analyses to the supplement to reach 30% is open for the user; S7 did not force it.

## S8 — 2026-09-29 19:45 — Opus 5.5 (the plan assigns Sonnet 5) — status: COMPLETE
Commits:
- 9f5656f [S8] Queue gate, evaluation and runtime inputs for the 42 pre-submission runs
- 5d9e28d [S8] discharge M-74, M-75 and M-76 as M-77, M-78 and M-79
- (the commit carrying this entry) [S8] COMPLETE: session log
Done:
- **Step 1, the gate: PASS** (`docs/presubmission/s8_gate.py`). The queue finished at 19:11:02 on 2026-09-29 with 42 queued, 42 done and 0 failed. Every artifact has the expected iterations, M, N, arch/regime/spec, seed and width (RWM `rnn_hidden_size` 256; each baseline the parameter count its spec builds). Every loss trace, final term and `wall_clock_s` is finite, and the weights exist.
- **Step 2, evaluation.** The S2a and S2b evaluators, unchanged since their pre-run commits, were run in both arenas:
  - `results/mn_sweep_eval.json`: the 24 sweep runs plus the centre;
  - `results/baselines_eval.json`: the 18 baseline runs plus RWM.
  In both, RWM reproduces `results/head_to_head_accuracy.json` to 3.9e-08. The verdict scripts are unchanged since their pre-run commits (51c3d7f, 5785260), and their self-tests pass.
- **Step 3, discharge.** By the ruling "New entries + Status line (Recommended)" (`DECISIONS_FOR_USER.md#S8-discharge-status`):
  - **M-74 → `M-77`: NOT OPTIMAL AT OUR BUDGET.**
    - (32, 32), (32, 16), (8, 8) and (2, 8) exclude zero in their own favour.
    - (32, 2) and (32, 1) exclude zero in the centre's favour.
    - (16, 8) and (1, 8) are not rejected.
  - **M-75 → `M-78`: REPRODUCES.** RWM beats the teacher-forced MLP, RSSM and transformer.
  - **M-76 → `M-79`: RWM AHEAD OF ALL THREE**, against the autoregressive baselines.
  - Only each rule's Status line changed, and the writer asserts that. `ledger_check` PASS, with 0 rules undischarged.
- **Step 4, runtime inputs** (`results/presubmission_runtime.json`, from `docs/presubmission/s8_runtime.py`):
  - The 42 runs took 28.3 h: the sweep 13.4 h, the teacher-forced baselines 7.9 h, the autoregressive baselines 7.0 h.
  - New keys `rt_pre_*`, `rt_sweep_*`, `rt_bl_tf_*` and `rt_bl_ar_*` sit beside Appendix B's `rt_*`, which are unchanged. Appendix B's prose describes the step5 runs, and its remainder is released-width hours, which the baselines are not.
  - **8 runs overlapped a CPU job a session logged:**
    - `mn_M32_N32_s2`: 59 min, S2b's verification ladder;
    - `mn_M16_N8_s0`: S2b's timing probe, S3's `alignment_defect_ci.py` window, and builds;
    - `mn_M16_N8_s1`, `mn_M32_N16_s0`, `mn_M8_N8_s2`, and `mn_M32_N2_s0`/`s1`/`s2`: S3–S7 build passes.
  - Every logged job and its basis (exact, logged, or window only) is in `docs/presubmission/s8_cpu_jobs.json`. No baseline run overlapped one.
- **Step 5.** No paper prose was edited; templates are unchanged.
Build/checks: pass.
- 60/60 comparative claims verified, and the gate self-test catches 7 of 7.
- Two consecutive build-and-check passes are byte-identical.
Paper numbers changed (all generated): `n_entries` 258 → 261, `ledger_kb` 543 → 552. Added: `rt_pre_runs` 42, `rt_pre_hours` 28.3, `rt_sweep_runs`/`_hours` 24 / 13.4, `rt_bl_tf_runs`/`_hours` 9 / 7.9, `rt_bl_ar_runs`/`_hours` 9 / 7.0, and `rt_pre_overlapped` 8.
CPU jobs over 1 min: none. The evaluators and verdicts took about 2 min in all, after the queue had finished.
Next:
- **S9 writes the new results into the paper**: §5.2 (M/N sweep), §5.3 (baselines), and §4, Appendices B–E, §3.2 and §11 moving from 4 to 6 tested claims.
- For S9:
  - `results/appendix_g_rules.json` (Appendix E's table and lead times) has not been regenerated since M-74–M-76 were discharged; it is a reproduce stage, not the fast build. Figure 1's lead times and `appG_*` / `f4_*` will move when it is.
  - Appendix B's prose needs the new runtime keys.
  - Appendix C's rows for the sweep and the baselines still say they are unrun.
  - `src/baselines` is ours. OUT_OF_SCOPE already records that the paper's "lite ships only the RNN variant" is wrong (S2b).
Decisions for user: DECISIONS_FOR_USER.md#S8-discharge-status (answered)

## S9 — 2026-09-29 22:10 — Opus 5.5 — status: COMPLETE
Commits:
- 8f1fa20 [S9] Write M-74, M-75 and M-76 into the paper: §5.2, §5.3, and everything generated from the claim counts
- (the commit carrying this entry) [S9] COMPLETE: session log
Done:
- **Item 1, two new sections.**
  - §5.2, the configuration claim: **NOT OPTIMAL AT OUR BUDGET**. (32, 32), (32, 16), (8, 8) and (2, 8) beat the centre; (32, 2) and (32, 1) are worse; (1, 8) and (16, 8) are unresolved. The original's direction on N holds, and its direction on M holds only in part. On the governing reading no shorter history is worse; the in-sample readings put (1, 8) behind the centre at h = 368, and held-out nRMSE puts (16, 8) behind it. The prose names both, generated as `mn_mvar_other_worse`.
  - §5.3, the architecture claim: **REPRODUCES** (M-75, teacher-forced baselines) and **RWM AHEAD OF ALL THREE** (M-76, autoregressive). Following M-76's own "Licenses" line, the paper calls M-76 a comparison of architectures at one training regime, not a verdict on the original's claim. The original's statement that an autoregressive RSSM is comparable to RWM is reported as not reproduced, with our RSSM reading as a possible cause.
  - Word counts, placeholders counted as one word: §5.2 525, §5.3 514. Rendered: 760 and 661, because generated lists, captions and clauses expand. The overrun on PLAN's "about 500" comes from the review corrections below; nothing was cut to meet it.
  - "Architecture baselines" is used throughout and defined at first use. Both sections cite `ORIGINAL_SPECS.md` and `BASELINE_SPECS.md`.
- **Item 2, head-to-head table.** Six baseline rows, relative-L1 only. The baseline evaluator's relative-L1 reproduces Arm A's row to 1e-6 (asserted), but its nRMSE is averaged per trajectory while the table pools it, so those cells are "—" and the caption says why (OUT_OF_SCOPE). The released checkpoint still leads at h = 1 and h = 8.
- **Item 3, everything generated from counts.**
  - §4 moves to six tested and six untested claims, through Appendix D's tags. A new assertion checks that no untested row is tagged `cpu`, which is what makes "every one of the six we did not test needs a simulator or hardware" true. The review caught the first wording ("needs a simulator"): the offline-MBRL-on-real-robots row needs hardware, not a simulator.
  - `orig_n_without` 4 → 5 and `orig_n_with` 0 → 1: the configuration claim's heatmap prints its values.
  - Appendix C: the two CPU rows are removed. The "within reach" paragraph becomes history, and the row-count history moved to BUILD_CHECKS.
  - Appendix D: both rows are marked tested, with their verdicts; the baselines row cites Fig. 7.
  - Appendix E regenerated: 18 → 21 rules. Figure 1 is unchanged; the paper already says Appendix E adds every rule since.
  - Appendix B: a paragraph on the 42 runs (28.3 h), asserted to sum by rule. It states that 8 runs overlapped logged CPU work, and §5.2's caption now says so too.
  - §3.2: three rows from `scripts/evidence_summary.py`.
  - §11: one paragraph on the scope of the two verdicts. §12: one sentence in the opening and one in "what should travel".
- **Item 4.** An 8th contribution bullet, per the ruling raising the cap to 8. One numeral-free abstract sentence; trims elsewhere keep the abstract at 330 words, with C12.1 unchanged and passing. The only content removed from the abstract is the sentence "Because the shortfall grows with depth, no single penalty weight absorbs it", which §6.8 still states.
- **Item 5, citations.** DreamerV2 (2010.02193, ICLR 2021 from its arXiv comment) and PlaNet (1811.04551) are verified by `t1_bibliography.py`'s own `verify()`, restricted to the two entries, and pinned with their fingerprints: 18 of 18 metadata-verified. PlaNet's arXiv record has no journal_ref and its comment names no venue. Its venue, ICML 2019 (PMLR 97), is from the paper's own first page, and the paper's two bibliography notes now say venues come from the record or the first page.
- **Bundles.** Both builders ship `ORIGINAL_SPECS.md`, `BASELINE_SPECS.md` and `verify_original_specs.py` and still exclude the rest of `docs/presubmission/`. `make_anon_bundle.py` (no zip): PASS, 0 residual identifying hits. Its side-effect files (`docs/COMMIT_LABEL_MAP.json`, `results/anon_bundle.json`) were restored, not committed.
- **Review** (PLAN §1.3's cap: two subagents). The first, on Sonnet 5.5, stopped on a rate limit before producing anything. The second ran as a one-agent workflow on Opus 5.5. It recomputed every table value and list, and found 0 wrong numbers and 9 wording issues, all fixed:
  - the M-direction reading held only on the governing reading;
  - §12 filed a resolved verdict under "limits, not findings";
  - §4's "needs a simulator" was untrue for the hardware row;
  - "error falling steeply as M grows" left out the original's own plateau;
  - §5.2's hours column did not mention the 8 overlapped runs;
  - "the RSSM takes DreamerV2's settings" was too broad;
  - the bullet said "built to its specification" rather than "our reading of" it;
  - "smallest resolvable difference" was used for what is a minimum detectable effect;
  - the bullet counted M-76 toward the original's claim.
Build/checks: pass.
- 60/60 comparative claims verified, and the gate self-test catches 7 of 7.
- Two consecutive build-and-check passes are byte-identical.
- **Re-anchored (logged per §1.2.8):**
  - C15.3 "of the claims we did test, the original reports no quantitative" → "claims we tested, the original reports no quantitative". The arithmetic is unchanged: `appF_n_claims` 12 = 6 + 6.
  - C17.1 "within reach of the CPU budget this project already spent" → "we did not test needs a simulator or hardware we do not have". Its forbid list and self-test are unchanged, and the universal it now anchors is backed by the new no-`cpu`-row assertion.
- New assertions in `paper_numbers.py`:
  - §5.2/§5.3's arena equals §5's (episodes, `n_independent`, 400-row units);
  - every quantifier in §5.2 and §5.3;
  - the Appendix B sum;
  - no untested `cpu` row.
Paper numbers changed (all generated):
- `orig_n_tested` 4 → 6; `n_untested` 8 → 6; `appE_n_cpu` 2 → 0.
- `appG_n_rules` 18 → 21; `t1_n_refs` 16 → 18.
- `pdf_pages` 45 → 48; `tn_typed` 646 → 694.
- About 70 keys added (`mn_*`, `bl_*`, `h2h_bl_*`, `orig_n_*_word`).
- The body is 26,203 words (S7: 24,753).
CPU jobs over 1 min: build-and-check passes only (about 3 min each); no training.
Scratchpad: the session scratchpad was cleared externally mid-session. The check runner was recreated verbatim; the HF upload tooling is gone, and that upload had already completed.
Next:
- **S10, fresh-eyes review.** OUT_OF_SCOPE items addressed to S10:
  - the Fig. 4 → Fig. 7 citation in the AR-versus-TF and generality rows of Appendix D and in `original_paper_figures.py` `ar_beats_tf`;
  - `tf_poor`'s "no quantitative figure", although Fig. 6's N = 1 row prints values;
  - "the cheapest of the four" in Appendix C.
- S2b's OUT_OF_SCOPE item ("the lite release ships only the RNN variant") is resolved: the sentence is gone, and §5.3 says the pinned code has an MLP, which ours follows.
Decisions for user: DECISIONS_FOR_USER.md#S9-contributions-abstract (answered, three rulings)
