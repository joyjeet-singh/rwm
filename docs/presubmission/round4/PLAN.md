# Pre-submission plan, round 4 — RWM reproduction, TMLR

Put this file at `docs/presubmission/round4/PLAN.md`. Every session reads §1, its own section, and only the annexes its section names.

Written on 11 Oct 2026 from:
- a full read of the paper at round 3's final commit `41b73ee` (the 10 Oct PDF: 62 pages, SHA-256 `df9a1288…`);
- round 3's records (`docs/presubmission/round3/`), especially `FINAL_REPORT.md`, `OUT_OF_SCOPE.md` and `DECISIONS.md`;
- `results/action_sensitivity.json` (Appendix V's tables), the ledger entries D-13, D-37, M-70, M-84, M-85, R-79 and S-21, and `docs/presubmission/BASELINE_SPECS.md` rows 33–38.

Numbers below are for orientation. If an artifact disagrees with this file, the artifact wins; log the difference.

---

## 0. For you (the human)

### 0.1 What this round does

1. **Fixes the five items from the 10 Oct evaluation.**
   - **§7.2's paragraph about our own models.** It puts a −0.99% figure (unresolved, from 4 held-out trajectories) next to a +124.6% figure (from 16 training trajectories) with no intervals and no explanation. It is rewritten with intervals for every figure. It also says plainly that a percentage change depends on how accurate the model already is: both models' forecasts shift by about the same amount.
   - **The model card's line on action timing.** It currently suggests the wrong timing is harmless at one step. It is rewritten the same way.
   - **Rule X2's caveat and pass threshold.** Appendix V gains the threshold the rule was committed with, and one sentence saying that "the models use the action" is not the same as "they predict a different action's result correctly".
   - **The abstract's "(one reading unresolved)".** It becomes "no reading puts it ahead of them", which is true for every configuration. The four other places that restate it follow.
   - **The difficulty measure.** It averages the stale and the correct action timing because a script mistook them for two seeds. It is recomputed with the correct timing only.
2. **Tests, on your Mac's CPU, the answers to the objections reviewers are most likely to raise.** Each test is committed to git before it runs, as before.
   - *"Four held-out trajectories are too few."* Retrain both arms with each of the ten episodes held out in turn (**X3**). That gives 20 out-of-sample trajectories, and every episode is tested out-of-sample once. This is the biggest item, at about 18 hours of background training.
   - *"Your transformer baseline is five times smaller than RWM."* Run the size-matched MLP and transformer that were specified but never run (**X4**), about 8 hours.
   - *"You never show what the miscalibration costs."* Use the released code's own reward on the recorded data to check whether the uncertainty penalty is big enough to cover the model's error in predicted reward over 100 steps (**X5**). This only runs if that reward can be computed from the data; the first session in which it appears checks that before anything else. It uses no training.
   - *"The ensemble may be no better than a free signal."* Re-test on more, shorter pieces of the same data (**X6**). No training.
   - *"The recalibration evidence is thin."* Fit on nine episodes and test on the tenth, for each of the ten (**X7**). No training.
   - *"Does the evaluation bug change any conclusion?"* Re-score every comparison with the released evaluation's timing (**X8**). No training.
   - *"The paper is too long and hard to read."* Cut the main text from about 20,700 to about 15,000–16,000 words by moving detail to appendices, never deleting it. Take internal ledger labels out of the main text. Shorten the abstract to about 300 words.
   - *Things a CPU cannot do* (train a policy, test other robots, get more data) are stated plainly, once, in §11.
3. **Clears round 3's leftover items.**
4. **Freezes, re-measures from a clean copy, and verifies.** These steps come last.

**Computer time.** Training totals about 26 hours, capped at 32. It runs in the background while the next three sessions work on text. The inference jobs take a few hours, and each clean copy takes about 2 hours.

### 0.2 Decisions: accept the defaults or change them before F0

F0 copies this block into `docs/presubmission/round4/DECISIONS.md` as your rulings. To disagree with a default, edit its line here before you launch F0.

| # | Question | Default |
|---|---|---|
| W1 | X3, retraining with each episode held out in turn. | **Run it with 3 seeds per arm per fold, at 2,500 iterations** (about 18 CPU-hours). The alternatives are 1 seed (about 6 h) or skipping it. |
| W2 | X4, size-matched baselines. | **Autoregressive MLP and transformer only, 3 seeds** (about 8 h, cap 10). The teacher-forced baselines are 15–145× worse, so matching their size cannot change their sign. The size-matched RSSM is not run (§5.3 already calls the RSSM comparison uninformative). |
| W3 | X5, does the penalty cover the error in predicted reward? | **Run it if F2 finds the reward computable from the recorded data**; otherwise record why not and move on. |
| W4 | X6, X7, X8 (inference only). | **Run all three.** |
| W5 | Item 5, the difficulty measure. | **Recompute with the correct (causal) timing.** Stop with `BLOCKED` if any verdict, or the direction of any reported correlation, changes. |
| W6 | Main-text length. | **At most 16,000 words, aiming for 15,000**, by moving text and never deleting it. The alternative is to stop at round 3's 20,771. |
| W7 | Abstract. | **At most 300 words.** Tighten the abstract cap in `submission_check` C12.1 from 370 to 320 (tightening a check is allowed). |
| W8 | Internal labels in the main text. | **Remove ledger IDs (R-, S-, D-, C-, B- and commit labels) from the main text**; keep a rule's ID (M-xx, X-n) once per section where its verdict is reported. The appendices keep everything. |
| W9 | Training on fewer episodes, to show how the main result changes with the amount of data. | **No.** It can only show the trend towards less data, not more, and it costs 3–6 h. |
| W10 | The total cap on training time. | **32 CPU-hours.** A projection above it means `BLOCKED`. |
| W11 | If X3 does not replicate the headline (NOT RESOLVED or REVERSES). | **Say so in the abstract and contribution 2**, at the same prominence as the headline. |
| W12 | When to re-upload the model card to Hugging Face. | **Right after F4**, because the live card shows figures round 3 found were produced by a scoring bug. Then again after F12. |

### 0.3 Order and launch

Run F0 → F1 → … → F12 strictly in order. Don't start a session until the one before it has written `status: COMPLETE` in `docs/presubmission/round4/SESSION_LOG.md`.

The one exception is waiting. F1 launches the training queue, and F2–F4 work on other things while it runs. **F5 starts only after the queue has finished**; F4's log entry says how to check.

Launch every session in a **fresh terminal** (never `--resume`), from the repository root:

| Kind | Command |
|---|---|
| Opus 5.5, high effort | `CLAUDE_CODE_SUBAGENT_MODEL=claude-sonnet-5-5 claude --model claude-opus-5-5 --effort high` |
| Opus 5.5, default effort | `CLAUDE_CODE_SUBAGENT_MODEL=claude-sonnet-5-5 claude --model claude-opus-5-5` |
| Sonnet 5.5 | `claude --model claude-sonnet-5-5` |

Round 3 ran every session in one conversation. That is not possible here, because the training queue runs for over a day. Set effort at launch; it can't be raised from inside a session.

Then type: `Read docs/presubmission/round4/PLAN.md §1 and the section for session FX, then carry out session FX.`

- **`PARTIAL`** means the session ran low on room. Start a fresh terminal on the same model and type `Resume session FX.`
- **`BLOCKED`** means the session needs a decision. Answer under its question in `DECISIONS.md`, then type `Resume session FX.`

| ID | Model | Effort | Scope | Time |
|---|---|---|---|---|
| F0 | Sonnet 5.5 | default | Branch, round-4 files, rulings, baselines, preflight checks | 45 min |
| F1 | Opus 5.5 | high | Pre-register X3 and X4, timing probes, launch the training queue. No paper edits | 2.5 h |
| F2 | Opus 5.5 | high | X5 feasibility; pre-register and run X5–X8 (inference). No paper edits | 3 h |
| F3 | Opus 5.5 | default | Post hoc N5 (our models' stale-timing figures, with intervals) and N6 (the difficulty fix). No paper edits | 1.5 h |
| F4 | Opus 5.5 | high | Items 1–5 and X5–X8 into the paper, the model card and Appendix V | 2.5 h |
| F5 | Sonnet 5.5 | default | **After the queue finishes:** training gate; X3 and X4 readings; ledger | 1 h |
| F6 | Opus 5.5 | high | X3 and X4 into the paper; abstract and contributions | 2 h |
| F7 | Opus 5.5 | default | Length and readability, part 1: front matter to §5 | 2.5 h |
| F8 | Opus 5.5 | default | Length and readability, part 2: §6 to §13 | 2.5 h |
| F9 | Sonnet 5.5 | default | Pipeline hygiene: `reproduce.sh` wiring, Appendix B rows, round 3's leftovers, typesetting | 1.5 h |
| F10 | Opus 5.5 | high | Fresh-eyes review, reading the whole main text. **New terminal** | 2 h |
| F11 | Opus 5.5 | default | Freeze, claims audit, clean-clone measurement and §8 restatement, bundles, package | 3 h + 2–6 h CPU |
| F12 | Sonnet 5.5 | default | Clean-clone verification and final report. **No edits** | 1 h + 2 h CPU |

### 0.4 Only you can do these

**After F4** (ruling W12): re-upload `MODEL_CARD.md` to the Hugging Face model repository. The live card still shows the figures round 3 withdrew.

**After F12**, in this order:
1. Fast-forward or merge `presubmission4` into GitHub's default branch `main`. It still holds the 29 August state.
2. Re-upload `MODEL_CARD.md` again if F5–F11 changed it.
3. Trigger a Software Heritage archive of the final pushed commit. §13 says the repository was archived before submission; the only recorded visit is 21 August, before rules X1–X8 existed.
4. Send the author query (`docs/presubmission/AUTHOR_QUERY_ALIGNMENT.md`) if it hasn't gone.
5. Upload `PAPER.pdf` and `supplementary_anon.zip`. Check both against the SHA-256s in the refreshed `docs/SUBMISSION_PACKAGE.md` first, and don't rebuild before uploading.

Steps 1–3 push or publish something. Nothing may be pushed once the paper is under double-blind review, so finish steps 1–4 before step 5.

---

## 1. Rules for every session (read in full each time)

### 1.1 Scope
- Do only your own session's items. Log anything else as one line with file:line in `docs/presubmission/round4/OUT_OF_SCOPE.md`, and do not fix it.
- Do not start the next session's work.

### 1.2 Integrity (non-negotiable)
1. **No hand-typed numbers.** Every measured number in the paper, the model card and the README is a `{{key}}` from `scripts/paper_numbers.py` (FILE_MAP §2), read from an artifact under `results/`. Annex 4's draft text shows numbers as artifacts give them today; bind each one, reusing the existing key where there is one.
2. **Edit sources, never outputs.** Paper and docs: `PAPER.template.md`, `README.template.md`, `docs/*.template.md`. Generated text: its generator (`evidence_summary.py`, `build_paper.py`, `build_model_card.py`, `appendix_g_rules.py`, `paper_figures.py`, …).
3. **The ledger (`FINDINGS_LEDGER.md`) is append-only.**
   - New IDs come from `scripts/ledger_check.py`.
   - A correction is a new entry that names the entry it corrects.
   - The one sanctioned in-place edit is a rule's `Status` line at its discharge.
4. **Pre-register before data.** Rules X3–X8 each get a ledger entry with status `PRE-REGISTERED` and their reading script, committed and pushed under a subject starting `PRE-REGISTER`, before any data they read exists.
   - For X3 and X4, the data are the new training runs.
   - For X5–X8, the data are the new inference readings; the weights they read already exist.
   - A script is never changed after its pre-registration commit. If it must change, stop with `BLOCKED`; an amendment is a new rule entry, as M-52 was.
   - Analyses N5 and N6 are labelled **post hoc**. No post hoc work re-opens a discharged rule or changes a verdict.
5. **No reading before its gate (new this round).** No session evaluates a training run from the round-4 queue before F5. F1 may check only that each run started and that its loss is finite.
6. **Verify against source, not config.**
   - Every new analysis script first asserts that it reproduces an existing artifact on the cases they share; each item names its assertion.
   - Every new training variant has a `BASELINE_SPECS.md` row with a citation. An UNVERIFIED row blocks the run.
7. **Citations** are added only through `scripts/t1_bibliography.py`.
8. **Anonymity.** The deny-list scan passes for the paper and both bundles. `docs/presubmission/` (and so `round4/`) is excluded from both bundles; F0 confirms this.
9. **Never loosen a failing check.** Fix the cause, or report the failure. Re-anchor a check only when its text legitimately moves, and log old anchor → new anchor. Never retire a numeric assertion. Tightening a check (ruling W7) is allowed.
10. **Move, never delete.** Text leaving the main text goes to an appendix, or, if it is drafting history, to `docs/BUILD_CHECKS.template.md`'s "Moved from the paper body" list. No result, number, verdict, table or figure may disappear from the paper and its appendices together.
11. **Summaries are checked against every reading** (round 3's rule 10). A sentence in the abstract, the contributions, Appendix D, §9, §11 or §12 that restates a result may claim a direction only if every reading the body reports for that result agrees with it: every arena, horizon and metric, and every configuration when the sentence names several. If the readings split, the summary says so.

### 1.3 Tokens and context
- **Start by reading only:** §1, your own section, the last `SESSION_LOG.md` entry, and the annexes your section names.
- **FILE_MAP** (`docs/presubmission/FILE_MAP.md`): grep it for the rows you need. Never read it whole.
- **Never read whole:** `FINDINGS_LEDGER.md` (about 610 KB), `PAPER.template.md`, `paper_numbers.py`, `paper_numbers.json`, or any artifact under `results/`. Use `grep -n`, then Read with `offset`/`limit`; extract JSON fields with `python -c` or `jq`.
- Send long output to a log file and show `tail -n 40`.
- **Subagents:** at most 2 per session, Explore type, read-only.
  - The launch command makes them Sonnet 5.5; do not pass a `model` argument.
  - Ask for file:line hits and a conclusion of at most 300 words.
  - Never delegate edits.
- **Checkpoint.** If the conversation has been compacted once, or feels heavy: finish the current item, commit, write a `PARTIAL` entry naming the exact next step, and stop.

### 1.4 Protocol
- **Start gate.** The last log entry must be the previous session with `status: COMPLETE`, or this session with `PARTIAL` or `BLOCKED`.
- **Branch and commits.** Branch `presubmission4` (F0 creates it). One commit per item, subject `[FX][item] summary`. Push at the end of every session.
- **End of every session that edits text:**
  1. Run FILE_MAP §3's fast build, then the gates, then the fast build again.
  2. The second build must be byte-identical to the first.
  3. Append the log entry, commit, push.
- **Log entry template:**

```
## FX — YYYY-MM-DD HH:MM — <model, effort> — status: COMPLETE | PARTIAL | BLOCKED
Commits: <hash> <subject>, one per line
Done: …
Build/gates: pass | fail (<which>)
Paper numbers changed: none | <key: old → new, artifact>
New keys: none | <key, artifact>
Re-anchored checks: none | <check: old → new>
CPU jobs over 1 min: none | <what, how long, contended?>
Queue status: not launched | running (<n of m done>, projected finish) | done
Body words (round2/t6_words.py): <n> (F0: <n>)
Abstract words / numerals (C12.1): <n> / <n>
Next: …
Decisions for user: none | DECISIONS.md#<anchor>
```

- **Stop with `BLOCKED`** and write the question to `DECISIONS.md` when:
  - an assertion this plan names fails;
  - a result would change a headline number, a verdict, or an abstract claim beyond what this plan specifies;
  - two artifacts disagree and you can't tell which is current;
  - a projected CPU cost exceeds its cap;
  - this plan says to.

### 1.5 CPU
- **Never two training jobs at once** (8 GB of RAM).
- **Inference while the queue trains** (F2, F3) is allowed: it slows both jobs but changes no number. Log it as contended.
- **Timing probes** (F1) run only on an idle machine, before the queue launches.
- Keep the Mac on mains power. The queue and the clean clones run under `caffeinate -i`.
- Log any job over 1 minute.

---

## 2. Sessions

### F0 — Orientation (Sonnet 5.5)
Reads: §0.2, §1.

1. **Working tree.**
   - `git status`. Expected untracked paths: `docs/presubmission/round4/PLAN.md` only. Record any other path; stop with `BLOCKED` if one is a source (a template, `scripts/`, `src/`, `results/`, `reproduce.sh`) or the ledger.
   - HEAD must be `41b73ee` on `presubmission3`, or a descendant that adds only round-3 records.
   - Tag HEAD `pre-round4`, create branch `presubmission4`, and commit this plan.
2. **Round-4 files.** Create `SESSION_LOG.md`, `DECISIONS.md` (§0.2's table, with "defaults accepted by launching F0, 2026-MM-DD" or the user's edits) and `OUT_OF_SCOPE.md` in `docs/presubmission/round4/`.
3. **Bundle exclusion.** Dry-run both bundle builders' collection and assert that nothing under `round4/` is collected.
4. **Baselines, in `round4/BASELINE_F0.md`:**
   - main-text words by `docs/presubmission/round2/t6_words.py`, in total and per `##`/`###` section;
   - page count, and the page on which References starts;
   - the abstract's word and numeral counts as C12.1 counts them;
   - a count of ledger IDs in the main text, by kind (R-, S-, D-, C-, B-, M-, commit labels);
   - pass/fail for every gate after one fast build.
5. **Preflight checks, in `round4/PREFLIGHT.md`.** Record each as pass/fail with file:line. Any fail means `BLOCKED`, except PF4, which only records.
   - **PF1. Weights.** Record the paths of:
     - Arm A and Arm B at 2,500 iterations for the held-out pair {1, 8}, seeds 0–2;
     - Arm A and Arm B at 10,000;
     - the 9 sweep configurations at 2,500;
     - the 6 baseline families at 2,500;
     - Arm A's three ensemble-5 arms;
     - the released checkpoint.

     Also record which artifact holds Arm B's 2,500-iteration held-out relative-L1 at every horizon (for X3's assertion).
   - **PF2. The train/held-out split.** Record:
     - where the held-out episodes {1, 8} are set (file:line);
     - whether the training driver takes the held-out set as an argument;
     - how training windows are built, and the committed window count for {1, 8} (7,687);
     - how many non-overlapping 400-step trajectories each candidate fold below yields: {0, 2}, {3, 4}, {5, 6}, {7, 9}.
   - **PF3. Size-matched baselines.** Read `BASELINE_SPECS.md` rows 33–38 (matched MLP width 295; matched transformer d_model 160). Record each row's status and its parameter count, computed by building the model.
   - **PF4. Reward computability (records only).**
     - The data columns of the released CSV, by name.
     - Whether commands and contact labels are present.
     - The file:line of every reward term the imagination environment computes (`robotic_world_model_lite`, starting from `envs/base.py:166`, where the penalty is added as `uncertainty_penalty_weight * epistemic_uncertainty * dt`), with each term's inputs.
     - The value of `dt`.
   - **PF5. The action-convention evidence.** Ledger D-13 cites four tests and Isaac Lab's `ActionManager.reset()`, which zeroes the action buffers at `action_manager.py:350-365`, commit `7a4b6d2b`. Record whether the paper's §7.2 or any appendix cites that source line (grep for `ActionManager`).
   - **PF6. Functions to import.** Record the file:line of:
     - the M-64 short-unit index builder;
     - the free-baselines margin and partial (`e7_free_baselines.py`);
     - §6.7's per-horizon fit and score functions (`task_d3_perhorizon.py` or its successor);
     - M-23's three-seed bootstrap;
     - `verdict_mn_sweep.py` and `verdict_baselines.py`'s reading functions;
     - `action_sensitivity.py`'s intervention hook and interval.
   - **PF7. The difficulty measure.** Record:
     - `scripts/a2_trajectory_level_control.py:265-269` and `:304`;
     - the keys of `per_episode_e` in `results/step4_0a_results.json`;
     - every paper key that depends on the averaged measure (`d12_lo`, `d12_hi`, the h = 1 partials, Appendix N's "+0.040 with per-episode difficulty").
   - **PF8. Action offsets in our evaluators.** Record whether the sweep evaluator, the baselines evaluator and the A/B evaluator each accept an action offset (file:line). If one does not, say how its rollout reads actions.
   - **PF9. Disk and memory.** Free disk space and RAM. Estimate the size of 30 new runs' weights and logs.

### F1 — Pre-register and launch the training rules X3 and X4 (Opus 5.5, high)
Reads: §1, F1, Annex 2 (X3, X4), and `round4/PREFLIGHT.md` (PF1–PF3, PF6, PF9).

1. **Fold support.** If the training driver cannot take a held-out set, add an argument whose default reproduces today's {1, 8} exactly. Assert all of these:
   - **(a)** with {1, 8}, the window set is byte-identical to the committed one (hash the index list);
   - **(b)** a 50-iteration run of Arm A, seed 0, on {1, 8} reproduces the committed run's first 50 loss values bitwise, or to 1e-6 if the committed record is rounded. Say which;
   - **(c)** each new fold's training set excludes exactly its two episodes, and its held-out trajectories lie entirely inside them.
2. **Size-matched variants.** Confirm that `BASELINE_SPECS.md` rows 33–34 are complete, with citations, and that each built model is within ±5% of 714,164 parameters. Add any missing row; an UNVERIFIED row blocks the run.
3. **Timing probes.** On an idle machine, run 20 iterations each of:
   - Arm A and Arm B on fold {0, 2};
   - the matched MLP and the matched transformer, autoregressive.

   Record steady seconds per iteration. Project the queue's total time against the caps:
   - X3 ≤ 22 h, else its pre-registered 2-seed fallback;
   - X4 ≤ 10 h, else its 2-seed fallback;
   - the total ≤ 32 h (ruling W10).

   If the fallbacks still exceed the caps, stop with `BLOCKED`.
4. **Reading scripts.** Write `scripts/x3_cross_fold.py` and `scripts/x4_matched_baselines.py` to Annex 2.
   - Both import the statistics named there and never copy them.
   - Each runs its reproduction assertions on existing artifacts before reading anything new.
   - Run the assertions now, and only the assertions.
5. **Pre-register.** Append two ledger entries (next free M-IDs), status `PRE-REGISTERED`. Each contains Annex 2's question, design, statistic, reading, fallback, caveats and the script's SHA-256. Commit with subject `PRE-REGISTER X3 cross-fold replication and X4 size-matched baselines, before their runs exist`, and push.
6. **Launch.**
   - Write `runs/queue_round4.txt` in this order:
     1. X3 seed 0 (8 runs);
     2. X4 seed 0 (2 runs);
     3. X3 seed 1;
     4. X4 seed 1;
     5. X3 seed 2;
     6. X4 seed 2.

     That order gives a balanced picture if the queue stops early.
   - Launch: `nohup caffeinate -i scripts/queue_runner.sh runs/queue_round4.txt > runs/queue_round4.log 2>&1 &`.
   - Confirm that the first run passes 50 iterations with a finite loss.
   - Write `round4/RUN_QUEUE.md`: the runs, the projected finish time, and a one-line status command.
7. **No paper edits.**

### F2 — X5 feasibility; pre-register and run X5–X8 (Opus 5.5, high)
Reads: §1, F2, Annex 2 (X5–X8), and `round4/PREFLIGHT.md` (PF4, PF6, PF8). The training queue is running: log every job here as contended.

1. **X5 feasibility.** Write `round4/X5_FEASIBILITY.md`, one row per reward term the imagination environment computes:
   - term | file:line | inputs | computable from the recorded data? (yes / no / partly) | computable from the model's outputs? | weight | dt-scaled?

   Then decide by Annex 2's X5 gate:
   - if it passes, define the reward subset in the file;
   - if it fails, X5 is **NOT RUN**. Write one ledger entry recording why, with no rule, and go on to step 2.
2. **Scripts.** Write the reading scripts for X5 (if feasible), X6, X7 and X8 to Annex 2, with their reproduction assertions. Run the assertions only.
3. **Pre-register** each rule as its own ledger entry, `PRE-REGISTERED`, with its script's SHA-256. Commit with subject `PRE-REGISTER X5–X8, inference-only rules, before their readings exist`, and push.
4. **Run** them to `results/x5_penalty_vs_return.json`, `results/x6_stepsize_short_units.json`, `results/x7_loeo_recalibration.json` and `results/x8_released_pairing.json`. Use a cap of 4 CPU-hours in total, contended.
5. **Discharge.** For each rule, append a ledger entry with the reading exactly as returned, and update its `Status` line.
6. **No paper edits.**

### F3 — Post hoc N5 and N6 (Opus 5.5, default)
Reads: §1, F3, Annex 3, and `round4/PREFLIGHT.md` (PF6, PF7).

1. **N5**, per Annex 3: our models' stale-timing figures, with intervals at every horizon in both arenas, and the forecast shift Δ. The script is `scripts/n5_stale_armA_ci.py` and its artifact `results/n5_stale_armA_ci.json`. Append one ledger entry, labelled **post hoc**.
2. **N6**, per Annex 3: the difficulty measure at the causal timing only.
   - Fix `scripts/a2_trajectory_level_control.py`'s choice of key and its `difficulty_source` label, then regenerate.
   - List every changed paper key with old → new.
   - Append a correction entry naming D-37 and every entry whose figures change.
   - Ruling W5: if any verdict string, or the sign of any correlation or partial the paper reports, changes, stop with `BLOCKED`.
3. **No paper edits.** The fast build will re-bind changed keys; check that the build and gates pass, and record the changed rendered figures.

### F4 — Items 1–5 and X5–X8 into the paper, the model card and Appendix V (Opus 5.5, high)
Reads: §1, F4, Annex 4 (items 1–5, X5–X8 text, captions), and the fields of the artifacts F2 and F3 wrote (never whole files).

1. **Item 1, §7.2's paragraph on our models** (Annex 4, A1). Also cite Isaac Lab's `ActionManager.reset()` (from D-13) for the reset-zero argument, if PF5 found it uncited.
2. **Item 2, the model card's "Action convention" line** (`scripts/build_model_card.py`, Annex 4, A2).
3. **Item 3, Appendix V's threshold and caveat** (Annex 4, A3).
4. **Item 4, the configuration wording.**
   - Install Annex 4's A4 in the abstract, contribution 3, §12, Appendix D's first-table row and the generated second-table row (`evidence_summary.py`).
   - Add A4b's per-configuration sentence to §5.2's Result paragraph.
5. **Item 5, the difficulty fix**, through N6's keys.
   - Wherever the text describes the measure, say it uses the causal timing.
   - Delete nothing about the earlier mean: the ledger and BUILD_CHECKS keep it.
6. **X5–X8 into the paper**, per Annex 4's placement table, each with its verdict verbatim and its arena, n and checkpoint.
   - Append new appendix sections after V, starting with W.
   - Do not touch the abstract beyond item 4 here; F6 rewrites it once, with every result in hand.
7. **Figure 1's caption.** Add that a lead of a few minutes means the rule was committed just before its runs were launched or its readings computed.
8. **Guards** in `check_comparative_claims.py`, each with a self-test branch:
   - **G7:** any sentence naming our models' stale-timing change must carry an interval key from N5;
   - **G8:** any sentence saying our models "respond to the action" (paper, model card) must have "one policy", or an equivalent caveat key, in the same paragraph;
   - **G9:** no front-matter sentence may pair "one reading unresolved" with a configuration list.
9. **Rule 11 audit** for every sentence installed, in the log.
10. **Log entry.** Tell the user the model card is ready to re-upload (ruling W12), and give the queue's status and its projected finish.

### F5 — Training gate; X3 and X4 readings (Sonnet 5.5) — only after the queue has finished
Reads: §1, F5, Annex 2 (X3, X4: "Reading" and "Gate"), and `round4/RUN_QUEUE.md`.

1. **Gate.** Check that:
   - every queued run is done, at the iterations and seeds queued;
   - the failures file is empty;
   - no loss is NaN;
   - each run's held-out episodes are those its fold names (read from the run record).

   Any failure means `BLOCKED`, with the log tail.
2. **Read.** Run `scripts/x3_cross_fold.py` and `scripts/x4_matched_baselines.py` unchanged; assert each script's SHA-256 equals its pre-registered one first.
3. **Ledger.** Append a discharge entry per rule with the reading exactly as returned, and update the `Status` lines. Write no prose interpretation.
4. **No paper edits.**

### F6 — X3 and X4 into the paper; abstract and contributions (Opus 5.5, high)
Reads: §1, F6, Annex 4 (X3/X4 variants, the abstract skeleton A6), and the fields of the X3 and X4 artifacts.

1. **X3:**
   - one paragraph in §5 (A5, choosing the variant the reading selects);
   - the fold-by-fold table as a new appendix section;
   - one clause in §11, which drops "Effective sample size bounds every long-horizon claim" to what still holds;
   - contribution 2 (ruling W11 if it does not replicate).
2. **X4:** one paragraph in §5.3, replacing "parameter-matched variants were specified but not run", plus rows in §5.3's table or a new appendix table.
3. **The abstract, rewritten once** (A6), to at most 300 words (ruling W7).
   - Tighten C12.1's word cap to 320 in `submission_check.py`, with its self-test.
   - Apply rule 11 to every sentence.
4. **Contributions:** at most 8 bullets of at most 3 sentences each; update bullets 2, 3, 6 and 7 for X3, X4, X7 and X5.
5. **Appendix D's two tables:** rows for the claims X3–X8 bear on, with verdicts verbatim.
6. **Rule 11 audit** in the log, and the abstract's word and numeral counts.

### F7 and F8 — Length and readability (Opus 5.5, default)
- **F7** covers the title page to §5.3.
- **F8** covers §6 to §13, and the appendices only as destinations.

Reads: §1, this section, Annex 5, and `round4/BASELINE_F0.md`.

1. **Target (ruling W6).** Main text ≤ 16,000 words by `round2/t6_words.py`, aiming for 15,000, with no result lost (§1.2 rule 10). F7 makes about 40% of the cut and F8 the rest. Annex 5 lists the moves in priority order, each leaving at most two sentences and a pointer.
2. **Labels (ruling W8).**
   - Replace every R-, S-, D-, C- and B- ledger ID and commit label in your part of the main text with plain words or an appendix pointer.
   - Keep a rule's ID once per section where its verdict is reported.
   - Never remove a "post hoc" or "pre-registered" label.
   - Re-anchor checks that keyed on an ID, and log each.
3. **Sentences.** Split any main-text sentence over about 45 words that carries more than two qualifiers. Keep every qualifier; change only the sentence boundaries.
4. **Process.**
   - Go one section at a time: Read it with offset/limit, move, build, run the gates, and log words before and after in `round4/LENGTH_LOG.md`.
   - Run `xref_sweep.py` after every move; it must report 0 suspect pointers.
   - Renumbering §-subsections is allowed with a pointer map in BUILD_CHECKS. Top-level section numbers stay.
5. **F8 ends by reporting:** the final count against 16,000; the three largest remaining sections; pages before References; and the ID count against F0's.

### F9 — Pipeline hygiene (Sonnet 5.5)
Reads: §1, F9, and `round3/OUT_OF_SCOPE.md`.

- **H1. `reproduce.sh`.** Add stages, with a `NEEDS_WEIGHTS` guard where trained weights are read, for:
  - `x3_cross_fold.py`, `x4_matched_baselines.py`, `x5_penalty_vs_return.py` (if run), `x6_stepsize_short_units.py`, `x7_loeo_recalibration.py`, `x8_released_pairing.py`, `n5_stale_armA_ci.py`;
  - the regenerated `a2_trajectory_level_control.py`.

  Add the full-run block for `runs/queue_round4.txt`. Target: `pipeline_coverage` lists 0 uncovered artifacts, and stage 20n8 lists 0 unclassified discoveries. Stages that load only the released checkpoint must **not** be marked `NEEDS_WEIGHTS` (the round 2 lesson).
- **H2. Appendix B's runtime table.** Add the round-4 runs through its generator. List the contended ones from `runs/queue_round4.log`.
- **H3. Round 3's leftovers.**
  - BUILD_CHECKS' list of claims withdrawn on evidence: generate it from the ledger, as the framings list is, or add a length check to C7.1.
  - Appendix H's R-46 row: make `task2_3_matched_and_trend.py` record n_independent per arena, regenerate, assert that every other field is unchanged, and bind n.
  - §5.2's per-configuration readings are done in F4 (A4b); confirm it.
- **H4. Typesetting.** Long `results/…` file names stretch justified lines (page 50 of the 10 Oct PDF). Let the TeX converter allow breaks inside `\texttt` paths (`md_to_tex.py`), and confirm with `pdf_render_check.py` and a look at every page that has a file name.
- **H5. Bundle self-test** at HEAD; it must detect its planted full hash.

### F10 — Fresh-eyes review (Opus 5.5, high; new terminal)
Reads: §1, F10, Annex 6. Read no earlier log beyond the last entry.

1. **Read the main text in full, once.**
   - Build, then `pdftotext -layout -f 1 -l <page before References> PAPER.pdf round4/body.txt`.
   - Read it in chunks of about 300 lines.
   - Look for a summary stronger than its section, for numbers without intervals, for an arena or n that is not named, and for any internal label left in the main text.
2. **Two Sonnet Explore agents**, read-only.
   - Agent 1 takes Appendices A–M; Agent 2 takes N onward.
   - Each checks every table against every sentence that cites it, and returns only mismatches.
3. **Write `round4/REVIEW.md`:** pass/fail for each item of Annex 6, with file:line, plus every finding from step 1 and step 2.
4. **Verify every finding yourself.** Fix only small items (3 sentences or fewer each); anything larger means `BLOCKED`, with the list.
5. **Write `round4/CONSISTENCY.md`:** one row per front-matter sentence | body anchor | every reading | agrees?

### F11 — Freeze, restatement, bundles, package (Opus 5.5, default)
Reads: §1, F11; round 3's `SESSION_LOG.md` "## R8" entry and round 1's "## S10-fix" entry (the B3 recipe).

1. **Freeze.** From here there are no prose edits except §8's reproduction figures and the documents in step 5.
2. **Regenerate the claims audit** (round 2's ruling U5 stands: regenerate, do not review). Run the fast build and gates, commit and push.
3. **Measure and restate, following round 3's R8:**
   - Clone the pushed HEAD into `/Users/Shared/rwm_verify/r4/M1/`, create a fresh venv from `requirements.txt`, and run `reproduce.sh --quick --force`. Evidence goes to `/Users/Shared/rwm_verify/evidence/R4F11/`.
   - Run the verifier three times; the runs must be byte-identical, with 0 scientific differing values.
   - Restate §8's reproduction figures (`ver_*` keys) from that measurement.
   - Refresh the hand-written copies with `docs/presubmission/s10fix_docs.py`.
   - Clone again and confirm that every reproduction key matches (round 3 needed three clones to reach a fixed point; allow up to three).
   - Push.
4. **Bundles.** Rebuild both on the restated HEAD. The builder scan and the independent deny-list sweep must find 0 hits in both zips and the PDF.
5. **Package documents.**
   - `docs/SUBMISSION_CHECKLIST.md`: the round-4 section.
   - `docs/SUBMISSION_PACKAGE.md`, in full: file sizes, SHA-256s, the abstract, counts, the title.
   - `docs/COVER_STATEMENT.md`: rule count, page count, retraction counts.
   - `round4/OUT_OF_SCOPE.md`: carry forward anything open.

### F12 — Clean-clone verification (Sonnet 5.5) — last; no edits
1. **Clone and adapt the driver.** Clone the pushed `presubmission4` HEAD into `/Users/Shared/rwm_verify/r4/F12/` with a fresh venv. Copy round 3's driver (`/Users/Shared/rwm_verify/evidence/R3R9/r9_driver.zsh`) to `/Users/Shared/rwm_verify/evidence/R4F12/` and adapt its branch, paths and references.
2. **Run, in order:**
   1. `./setup.sh`;
   2. `./reproduce.sh --quick --force`;
   3. the verifier three times against a pristine reference;
   4. the full paper build and every gate;
   5. both bundles and the deny-list sweep;
   6. the PDF comparison.
3. **Criteria:**
   - scientific differing values = **0**;
   - `part_f_gate` fails exactly as §8 publishes it;
   - every reproduction figure the paper prints equals what the clone measures;
   - the PDF equals the committed one after blanking dates and ID;
   - 0 deny-list hits in the rebuilt and the committed upload files;
   - `submission_check` returns what `SUBMISSION_CHECKLIST.md` records;
   - every new round-4 stage runs or skips as designed.
4. **Write `round4/FINAL_REPORT.md`:** pages, main-text words, abstract words, and every gate against F0, plus the upload files' SHA-256s.
5. **On any failure:** no fixes. Stop with `BLOCKED` and the logs; the user runs "F11-fix" on Opus, then F12 again.
6. **Log entry:** list §0.4's steps as reminders.

---

## Annex 1 — Likely objections, and what this round does about each

| # | Objection a TMLR reviewer is likely to raise | What can be done on CPU | Where |
|---|---|---|---|
| O1 | The long-horizon claims rest on 4 independent held-out trajectories, and one of them carries much of the effect | Retrain both arms with each episode held out in turn: 20 out-of-sample trajectories, and a per-episode sign test that is genuinely out-of-sample | X3 (F1, F5, F6) |
| O2 | The baselines differ in size from RWM: the transformer has 132,148 parameters to RWM's 714,164 | Run the size-matched MLP and transformer (`BASELINE_SPECS.md` rows 33–34), autoregressive, 3 seeds | X4 (F1, F5, F6) |
| O3 | Miscalibration is shown, but not what it costs; no policy is trained | Without a policy: does the applied penalty cover the model's error in predicted reward over the method's 100-step horizon, on recorded actions? This moves past M-70's penalty-only proxy if the reward is computable from the data | X5 (F2, F4) |
| O4 | The ensemble's advantage over the free step-size signal is unresolved at n = 20 | Re-test on shorter, non-overlapping units at h = 100 and h = 32 (about 70 units), as M-64 did for one step | X6 (F2, F4) |
| O5 | The per-horizon recalibration rests on 2 folds of 2 trajectories | Fit on 9 episodes and score on the 10th, for each of the 10 (still unseen by the multiplier only, not by the model) | X7 (F2, F4) |
| O6 | Does the evaluation bug change any comparison the paper (or the original) reports? | Re-score the sweep, the baselines and the A/B comparison with the released evaluation's timing, and report any verdict that would change | X8 (F2, F4) |
| O7 | §7.2 compares percentage changes across models and arenas without intervals | N5 gives intervals at every horizon in both arenas, plus the forecast shift Δ | N5 (F3, F4) |
| O8 | "Responds to the action" is read as "fit for control" | Text: the caveat and threshold | Item 3 (F4) |
| O9 | A covariate in the difficulty control mixes the two timings | Recompute at the causal timing | N6 (F3, F4) |
| O10 | The evaluation-bug claim rests on an inference about how the data were logged | Text: cite Isaac Lab's `ActionManager.reset()`, which zeroes the action buffers (ledger D-13), beside the reset-row argument | F4 |
| O11 | Many pre-registration lead times are minutes | Text: Figure 1's caption says what a short lead means | F4 |
| O12 | The paper is too long, dense and full of internal labels | Main text to 15,000–16,000 words; ledger IDs out of the main text; long sentences split; abstract ≤ 300 words | F7, F8, F6 |
| O13 | One robot, gait and terrain; no policy; 0.133% of the data; the released checkpoint has no held-out data | Not addressable on CPU. §11 says so once, plainly, and nothing else claims otherwise | F8 |

---

## Annex 2 — The rules X3–X8

All relative-L1 and nRMSE figures are cumulative over steps 1..h, as in §3.1. **No shared bootstrap function exists** (FILE_MAP §7): each rule imports the one used by the result it extends, named below, and never writes its own. "Interval" means a 95% cluster bootstrap over whole units:
- exact over all ordered resamples at n = 4;
- otherwise 20,000 Monte Carlo draws with generator seed 0, seeds pooled inside each draw.

Each rule is exploratory and re-opens no discharged rule.

### X3 — Does the base claim replicate when each episode is held out in turn? (training)
- **Folds.** {1, 8} (the existing runs) and four new ones: {0, 2}, {3, 4}, {5, 6}, {7, 9} (the remaining episodes, paired in index order). Every episode is out-of-sample in exactly one fold.
- **Runs.** For each new fold: Arm A and Arm B, seeds 0–2, 2,500 iterations. The configuration is identical to the existing 2,500-iteration Arm A and Arm B runs except for the held-out set. That is 24 runs.
- **Fallback, fixed now.** If F1's projection exceeds 22 h, run seeds 0–1 only and read the two-seed mean with the same thresholds.
- **Arena.** Each fold's held-out pair, as non-overlapping 400-step trajectories (PF2 records the count), pooled across the 5 folds (n ≈ 20).
- **Statistic.** Per trajectory, the gap = (seed-mean relative-L1 of Arm B) − (seed-mean relative-L1 of Arm A) at h = 368. Read its mean over trajectories, with an interval (M-23's three-seed bootstrap, imported).
- **Reading:**
  - **REPLICATES ACROSS FOLDS** if the interval's lower bound > 0;
  - **REVERSES** if the upper bound < 0;
  - **NOT RESOLVED** otherwise.
- **Part of the rule, reported verbatim, no verdict of its own:**
  - the per-episode sign test: for each of the 10 episodes, the sign of its mean gap at h = 368, the count positive and an exact two-sided binomial P;
  - each fold's gap with its exact interval.
- **Alongside:**
  - h = 100, with the same statistic;
  - h = 1 on M-64's 33-row units pooled over folds: the teacher-forcing lead, with an interval;
  - the A/B ratio of means at each horizon.
- **Assertions:**
  - F1's (a)–(c);
  - fold {1, 8}'s readings reproduce the committed 2,500-iteration held-out relative-L1 for Arm A (`mn_compute_matched.json` 2,500 block) and Arm B (PF1's artifact) at every horizon, to 1e-6.
- **Gate.** No evaluation before F5 (§1.2 rule 5).
- **Caveats in the entry.** At 2,500 iterations, not 10,000; the 4.61× headline is at 10,000 on fold {1, 8} and is not re-read.

### X4 — Is RWM still ahead of size-matched baselines? (training)
- **Variants.** `BASELINE_SPECS.md` row 33 (MLP, width 295) and row 34 (transformer, d_model 160, learned positions), each within ±5% of 714,164 parameters, trained autoregressively, otherwise exactly as M-76.
- **Runs.** Seeds 0–2, 2,500 iterations, held-out {1, 8}: 6 runs.
- **Fallback, fixed now.** If F1's projection exceeds 10 h, seeds 0–1 only.
- **Statistic and reading.** M-76's, imported from `verdict_baselines.py`: relative-L1 at h = 368, the baseline minus RWM (Arm A at 2,500), exact bootstrap at n = 4, Holm over the family of 2. The verdict labels are those `verdict_baselines.overall` returns for a family of 2. Assert in F1 that it returns a defined label for every combination of the two outcomes.
- **Alongside:** h = 100 and h = 32; cost per iteration from F1's probes.
- **Assertion.** The evaluator, run on the original-size autoregressive baselines, reproduces `baselines_eval.json` to 1e-6.
- **Caveat.** Matching parameter count is one axis; the shapes and settings stay our reading of Table S7.

### X5 — Does the applied penalty cover the model's error in predicted return? (inference; feasibility-gated)
- **Gate (F2 step 1).** X5 runs only if every term of a **reward subset** is computable from both the recorded data and the model's outputs. The subset must include at least the command-tracking terms (linear and angular velocity tracking) and is otherwise every term that qualifies; it is named in `X5_FEASIBILITY.md` before pre-registration. If the tracking terms do not qualify, X5 is NOT RUN.
- **Model.** The released checkpoint, ensemble of 5, as released.
- **Units.** Non-overlapping 132-row windows (32 of history and 100 forecast steps, the method's imagination length) inside each of the ten episodes, with the causal pairing.
- **Per unit:**
  - **R:** the subset's reward summed over the 100 recorded steps;
  - **R̂:** the same function summed over the model's open-loop forecast, driven by the recorded actions and commands;
  - **P:** the penalty as `envs/base.py:166` applies it (`uncertainty_penalty_weight × epistemic_uncertainty × dt`, with the released weight), summed over the same steps;
  - **P_c**, alongside only: the same with each step's u multiplied by X7's per-horizon multiplier for that unit's held-out episode.
- **Statistic.** K = mean P ÷ mean |R̂ − R|, a ratio of means, with an interval over units.
- **Reading:**
  - **PENALTY COVERS RETURN ERROR** if K's lower bound ≥ 1;
  - **PENALTY SMALLER THAN RETURN ERROR** if K's upper bound < 1;
  - **UNRESOLVED** otherwise.
- **Alongside:**
  - the mean of R̂ − R (is the model optimistic?) and of R̂ − P − R, each with an interval;
  - the fraction of units with R̂ − P ≤ R;
  - K_c, using P_c;
  - the Spearman correlation of R̂ − P with R, against that of R̂ with R.
- **Assertions:**
  - the per-step u equals `rollout_uncertainty`'s on the same windows to 1e-9;
  - R, recomputed through the imagination environment's own reward function on recorded states, equals X5's implementation to 1e-9 for every term in the subset.
- **Caveats in the entry, and every sentence that reports it:**
  - open-loop, with the recorded policy's actions, not the policy's closed-loop imagination;
  - the reward subset only;
  - training data for this checkpoint;
  - λ was tuned for policy learning, not to bound error, so K < 1 is a statement about scale, not about harm;
  - M-70's bound is untouched.

### X6 — Does disagreement beat predicted step size on more, shorter units? (inference)
- **Model.** The released checkpoint.
- **Units.** All ten episodes, non-overlapping units of 32 + h rows within each episode, built with M-64's index builder, at h ∈ {32, 100}. h = 100 governs.
- **Statistic.** M-51/M-52's margin, r(disagreement, |error|) − r(step size, |error|), on the applied scalar, imported from `e7_free_baselines.py`. It is paired, with an interval over units.
- **MDE.** Before reading, record its estimate by M-51's method at this n.
- **Reading at h = 100:**
  - **DISAGREEMENT BEATS STEP SIZE** if the lower bound > 0;
  - **STEP SIZE BEATS DISAGREEMENT** if the upper bound < 0;
  - **NOT RESOLVED** otherwise.
- **Alongside:** h = 32, and the partial r(disagreement | step size) at both horizons.
- **Assertion.** On the 400-step unit at h = 368, the imported functions reproduce `e7_free_baselines.json`'s r values and the +0.1357 margin to 1e-9.

### X7 — Per-horizon recalibration, fitted on nine episodes and scored on the tenth (inference)
- **Model.** The released checkpoint. Epistemic governs; aleatoric is alongside.
- **Design.** For each episode e, fit the per-horizon multiplier c_h on the other nine episodes' non-overlapping 400-step trajectories with §6.7's fitting function (imported). Score ±1σ coverage on e's trajectories. Pool the scored coverage over all 20 trajectories; each trajectory is scored once, by a multiplier not fitted on it.
- **Per-horizon reading** (h ∈ {1, 8, 32, 100, 128, 368}):
  - **WITHIN BAND** if the coverage interval lies inside [58.27%, 78.27%];
  - **OUTSIDE BAND** if it lies wholly outside it;
  - **UNRESOLVED** otherwise.
- **Governing summary.** "WITHIN BAND AT k OF 6 HORIZONS" for the epistemic term.
- **Alongside:** the constant-multiplier version of the same design, and the spread of fitted c_h across the ten folds.
- **Assertion.** §6.7's two-fold design, rerun through the imported functions, reproduces the committed cells to 1e-9.
- **Caveat.** Unseen by the multiplier, not by the model (the in-sample caveat of §3).

### X8 — Would any verdict change under the released evaluation's timing? (inference)
- **Re-score with action offset 0, using each rule's own evaluator and statistic:**
  - M-74's sweep (9 configurations × 3 seeds at 2,500);
  - M-75 and M-76's baselines (6 families × 3 seeds);
  - the A/B comparison at 10,000 (three seeds; M-23's statistic at h = 368, and the by-horizon table's).
- **Reading, per rule:** **SAME VERDICT** or **VERDICT WOULD CHANGE TO ⟨label⟩**, plus, alongside, every reading in the rule's alongside set that changes.
- **Assertion.** Offset 1 through the same code reproduces the committed evaluation artifacts to 1e-6. Where an evaluator has no offset argument (PF8), add one whose default is today's behaviour, and assert that.
- **Caveat.** Our models under the released pairing; it says nothing direct about the original's printed numbers.

---

## Annex 3 — Post hoc analyses N5 and N6

### N5 — Our models' stale-timing figures, with intervals
- **Models and arenas.** Arm A and Arm B at 2,500 and 10,000, seeds 0–2, plus the released checkpoint. Use each model's own training arena (16 trajectories for ours, 20 for the released checkpoint) and the held-out pair (4).
- **Horizons:** all six, {1, 8, 32, 100, 128, 368}.
- **Measures:**
  - E for the stale timing, with an interval, by X2's machinery imported from `action_sensitivity.py`;
  - Δ, the forecast shift: relative-L1 of the stale-timing forecast against the causal one, which is 0 for a model that ignores the action;
  - each model's baseline error at the causal timing.
- **Assertions:**
  - E at h ≤ 100 equals `action_sensitivity.json`'s stale-action cells to 1e-9;
  - Δ at h = 8 equals its Δ table;
  - Arm A's three-seed means equal `alignment_by_horizon.json`'s corrected `arm_a` block (R-79) at every horizon to 1e-6.
- **Expected orientation**, from Appendix V. Arm A at 10,000, stale timing:
  - training arena: +124.6% [+75.8, +201.9] at h = 1 and +209.3% [+167.3, +257.6] at h = 100;
  - held-out pair: −1.0% [−6.1, +27.7] at h = 1 and +16.6% [+1.9, +72.6] at h = 100.

  Δ at h = 8 on each model's own training data is 0.200 for Arm A at 10,000 and 0.204 for the released checkpoint.

### N6 — The difficulty measure at the causal timing
- In `scripts/a2_trajectory_level_control.py`, use `per_episode_e["1"]` (the causal timing) in place of the mean of keys "0" and "1". Rename `difficulty_source` to say so, and regenerate `results/a2_trajectory_level_control.json`.
- D-37 already records the causal range as 0.523 to 1.585 (against the averaged 0.562 to 1.591), with the spread 3.03-fold and the correlation with commanded speed +0.088.
- **Assert** that every field not derived from the difficulty measure is unchanged to 1e-12.
- **List** every changed key and its rendered figure, including Appendix N's "+0.040 with per-episode difficulty" and the h = 1 partials.
- **Ledger.** One correction entry naming D-37 and each entry whose figures change. It states that the paper now uses the causal timing, and why.
- **Ruling W5.** A changed verdict string, or a changed sign of any reported correlation or partial, means `BLOCKED`.

---

## Annex 4 — Edit targets and draft text

Anchors are phrases from the 10 Oct PDF; grep loosely. Bind every number. Tighten wording freely, but never strengthen a claim.

**A1. §7.2, our models.**
- **Replace** the sentences from "Our own Arm A checkpoints at 10,000 iterations, trained under the causal pairing, change by -0.99% at h = 1 and +22.67% at h = 368" to "and a swap by 1.44."
- **With:**
  > For models trained under the causal pairing, the stale one also raises error, and how much depends on the arena. On their own training episodes' 16 trajectories it raises our 10,000-iteration Arm A's relative-L1 error by +124.6% [+75.8, +201.9] at h = 1 and +209.3% [+167.3, +257.6] at h = 100; on the held-out pair's 4 it changes it by −1.0% [−6.1, +27.7] at h = 1, which those trajectories cannot resolve, and by +16.6% [+1.9, +72.6] at h = 100 (results/n5_stale_armA_ci.json; these figures replace ones an earlier version computed with a scoring bug, which the record keeps). A percentage change depends on how accurate the model already is as much as on how much the action matters: measured as the shift in the forecast itself, the stale action moves our model's 8-step forecast by 0.200 and the released checkpoint's by 0.204 on their own training data (Appendix V), so the two respond about equally, and our model's larger percentages reflect its smaller error there. Our models do use the action: given another trajectory's actions, their error at h = 8 rises by +676.3% [+454.8, +1060.0] (rule X2, RESPONDS TO THE ACTION at both checkpoints). That shows the forecasts depend on the action, not that they predict a different action's consequences correctly: every action in the data comes from one policy.
- If the 10 Oct sentence on the one-step shift (0.32 of the action's spread) and the swap (1.44) does not fit, move it to Appendix V.

**A2. Model card** (`build_model_card.py`, the "Action convention" line).
> **Action convention.** Row *t* holds the action that *produced* state *t*; these checkpoints are trained and evaluated with that pairing. Do not score them with the reference evaluation script's pairing, which is one step stale: on their own training episodes it raises the `autoregressive-10k` checkpoints' error by +124.6% [+75.8, +201.9] at 1 step and +209.3% [+167.3, +257.6] at 100 steps (three-seed mean, relative-L1). On the two held-out episodes the change is smaller and, at 1 step, not resolved: −1.0% [−6.1, +27.7], and +16.6% [+1.9, +72.6] at 100 steps. The forecasts depend on the action (rule X2), but every action in the training data comes from one policy, so their accuracy under actions that policy would not take is untested.

**A3. Appendix V, after "The readings are Arm A's, under the swap at h = 8 on its in-sample arena: …".**
> The criterion was fixed in the rule before any reading existed (M-84): RESPONDS TO THE ACTION if the swap raises error at h = 8 by at least 10% with an interval whose lower bound is above zero; ERROR FALLS WITH WRONG ACTIONS if the interval lies below zero; DOES NOT RESPOND MEASURABLY if its upper bound is below 10%; otherwise UNRESOLVED. The bar is deliberately low: the one-step-stale action alone raises the released checkpoint's error at h = 8 by 54.4% over all ten episodes. What the rule establishes is that our forecasts depend on the action. It does not establish that they depend on it correctly: every action in the data comes from one policy, so a forecast under an action that policy would not take has no recorded outcome to check it against.

Read the thresholds from M-84's entry, not from this plan. If they differ, use M-84's and log the difference.

**A4. The configuration wording** (rule 11). The source is round 3's `OUT_OF_SCOPE.md` R6 item: at 2,500 iterations, no reading the rule reports puts the centre ahead of any of the four winners. Re-check this against `mn_sweep_verdict.json` and `pooled_nrmse_alongside.json` before installing.
- **Abstract:**
  > On accuracy alone, two shorter histories and both longer training forecasts beat the original's setting at our budget, and no reading puts it ahead of them; trained longer, it passes each on some reading (post hoc), so the ranking depends on the training budget.
- **Contribution 3.** Replace "(the rule's verdict holds on every reading it reports but held-out nRMSE at h = 1, which is unresolved)" with "(no reading the rule reports puts the centre ahead of any of them)".
- **§12, Appendix D's two tables, and `evidence_summary.py`:** the same replacement for "every reading the rule reports returns but one, which is unresolved" and its variants.

**A4b. §5.2's Result paragraph, a new sentence after "…which returns CANNOT BE DISTINGUISHED."**
> Per configuration, no reading puts the centre ahead of any of the four winners, though several leave a winner unresolved: all four at h = 1 on the held-out pair in both metrics, the two longer forecasts also at h = 8, and (2, 8) on held-out nRMSE at h = 368, (8, 8) on in-sample relative-L1 at h = 368 and (32, 32) on in-sample nRMSE at h = 100.

Bind each figure from the artifacts, and re-derive the list rather than copying it.

**A5. X3 in §5**, after "What is small, and where it resolves" (variant by reading):
- **REPLICATES ACROSS FOLDS:**
  > Held out in turn, every episode tests the claim out of sample once. Retraining both arms for each of five such splits (rule X3, committed before the runs; 2,500 iterations, 3 seeds), the gap at h = 368 over all {{x3_n}} out-of-sample trajectories is {{x3_gap}} {{x3_ci}}, favouring autoregressive training, and {{x3_eps_pos}} of 10 episodes favour it (P = {{x3_p}}). The four trajectories of §5's arena are no longer the only out-of-sample evidence.
- **NOT RESOLVED / REVERSES:** state the reading, the interval and the sign count with the same prominence. Name which folds go the other way.

§11's sample-size paragraph becomes:
> The headline magnitudes rest on the held-out pair; the direction is re-tested on all ten episodes, each out of sample once (X3).

**A5c. X4 in §5.3**, replacing "Their sizes are Table S7's, not matched to RWM's; parameter-matched variants were specified but not run":
> Matched to RWM's parameter count (rule X4), the autoregressive MLP and transformer {verdict}: at h = 368 they trail RWM by {{…}} and {{…}}.

**A6. Abstract skeleton** (F6; at most 300 words). Each finding keeps its sentence, and only wording tightens. Order:
1. the rebuild;
2. the base claim and the X3 clause;
3. the baselines and the X4 clause;
4. the configuration sentence (A4);
5. the scope;
6. uncertainty: order right, size wrong (the X5 clause, if run, joins it);
7. the free signal (the X6 clause);
8. trunk-sharing;
9. σ → 0;
10. per-horizon rescaling (the X7 clause);
11. the action-timing clause;
12. "We train no policy".

X8 is mentioned only if a verdict would change. Each clause is at most 25 words and carries one figure.

**Placement of X5–X8** (F4):

| rule | main text | appendix |
|---|---|---|
| X5 | one paragraph in §6.2 after "A constant scale error would not matter, and this one is not constant", and one clause in §10 and §11 (replacing "We did not measure what the miscalibration costs" only as far as the reading allows) | new section with the per-unit table |
| X6 | one paragraph in §6.6 after the free-baselines table; §11's "The ranking claim is not established as needing an ensemble" updated to the reading | new section |
| X7 | one paragraph in §6.7, replacing its "Three cautions" only where X7 answers them | new section |
| X8 | one sentence in §7.2 | new section, with a table per rule |

---

## Annex 5 — Length moves, in priority order (F7, F8)

Each move leaves at most two sentences and a pointer. Measure after every move.

| Section (10 Oct words) | Leaves in the main text | To |
|---|---|---|
| §2 Related work (≈1,200) | ≈700: the direct precedent, the PETS lineage in two sentences, one line each for the rest | a new "Related work in full" appendix |
| §3 Setup and §3.1 (≈2,000) | the data, arenas, effective sample size, relative-L1 and nRMSE in words, and which metric each headline uses; coverage and the overconfidence factor defined in one sentence each | the formulas and "checked rather than assumed" to an appendix |
| §5 (≈2,100) | the rule, the result, the by-horizon table, the h = 1 reversal, the floor in two sentences, and X3 | "Seeds, and what four trajectories can show" and "What is small" to Appendix L |
| §5.1 (≈350) | two sentences: 7,991 transitions, 0.133% | the rest to Appendix L |
| §6.2 (≈1,400) | the h = 1 and h = 100 rows, why h = 1 comes first, and the constant-scale paragraph | the ensemble-5 arms' table and the permutation note to Appendix M |
| §6.3–§6.4 (≈1,300) | the derivation, the synthetic-noise verdict, and the 89.15% sharing with its mechanism | code line walkthroughs and run counts to Appendix J |
| §6.5 (≈1,100) | the claim paragraph and the "structural excuse" result | both tables to Appendix K |
| §6.6 (≈1,500) | the counter table's key row, the free-baselines verdict, and X6 | r_dd's table and M-43 to Appendix N |
| §6.7–§6.8 (≈1,700) | the verdicts, X7, and the independence factor | tables to Appendices T, O and P |
| §7 (≈1,000 after F4) | 7.1–7.5, one paragraph each | X8 detail and per-trajectory values to their appendices |
| §11 (≈750) | ≈450: only what is not stated where it bites, plus O13 | Appendix R |
| §12 (≈600) | ≈400 | Appendix S |

**Keep in the main text whatever the count:** §9 (the lessons), every verdict, every number the abstract cites, and the tables §3.2 points to.

---

## Annex 6 — Checklist for F10

1. **Items 1–5.**
   - §7.2 gives every figure for our models with an interval and arena, and the Δ comparison; no "−0.99%" stands without its interval.
   - The model card matches A2.
   - Appendix V states the threshold and the caveat.
   - Every configuration summary uses A4's wording.
   - The difficulty measure is causal-only, and N6's entry exists.
2. **X3–X8.**
   - Each was pre-registered before its data: commit order checkable in `git log`, and the script's SHA-256 equal to the artifact's.
   - Each verdict is verbatim, with arena, n and checkpoint.
   - The variants installed match the readings.
   - Every X5 sentence carries its caveats.
   - X5 NOT RUN, if so, is stated once with its reason.
3. **Rule 11.** `CONSISTENCY.md` covers every front-matter sentence, with every reading.
4. **Length and readability.**
   - Main text ≤ 16,000 words, or the shortfall is reported.
   - No R-/S-/D-/C-/B- ID or commit label in the main text.
   - No result lost: diff the template's `{{keys}}` against F0's, and justify every removed key.
   - `xref_sweep` reports 0 suspect pointers.
5. **Front matter.**
   - Abstract ≤ 300 words, and C12.1 at 320 passes.
   - At most 8 bullets of at most 3 sentences.
   - The title, abstract and conclusion agree.
6. **Captions.** Every table and figure carries its arena, n_independent and checkpoint, including the new appendix sections.
7. **Public-facing text.** README, model card and cover statement are no stronger than the paper, with no unbound number.
8. **Anonymity.** Commit labels are anonymous everywhere, and the deny-list scan passes.
