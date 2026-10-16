> **In the repository from 16 October 2026.** The user's handoff file, copied verbatim with two edits: the
> interpreter's absolute path is replaced (no account name or home path in `docs/`), and the PLAN.md link is made
> relative to this folder. It lives under `docs/presubmission/`, which both bundle builders exclude.

# Codex handoff: finish the TMLR revision

**Prepared:** 14 October 2026  
**Project:** `rwm_repro`, branch `presubmission4`  
**Goal:** finish and verify the current TMLR submission package, carrying out the already approved round-4 work and only adding bounded CPU analyses where they close a documented research gap.

This file is the handoff prompt and execution map. The detailed, pre-registered protocol remains [`docs/presubmission/round4/PLAN.md`](PLAN.md); follow its exact decision rules. This handoff does not amend them.

## 1. Start with the live state

The paper reviewed in the attached `10octPAPER.pdf` was the 62-page version. The repository has since advanced: its current generated `PAPER.pdf` is 67 pages and includes F4's X5–X8, N5/N6, and wording changes. The PDF in the repository is generated from `PAPER.template.md`; it is not the source to edit. Treat the current repository and latest round-4 artifacts as authoritative over old review notes and handoff summaries.

At the 14 October snapshot:

- The branch is `presubmission4` at `110ecd7`, with no tracked modifications and 26 untracked result JSON files from the round-4 queue. Preserve them. Do not run `git clean`, reset, discard, or overwrite existing results, `runs/`, weights, or logs.
- The round-4 training queue recorded 26 of 30 jobs complete and zero failed; no queue runner or trainer was active. The four remaining jobs are X3 Arm A and B on fold `{7,9}`, seed 2, and X4 matched MLP and transformer, seed 2. Their original total projection was about 4.24 CPU-hours. Recheck; this is a dated snapshot, not a live guarantee.
- `supplementary.zip` and `supplementary_anon.zip` predate F4 and are stale. F11 must rebuild them from the frozen final state.
- The latest session log is F4 COMPLETE. X5 is NOT RUN because the recorded data omit the command needed for the command-tracking reward terms. X6–X8, N5 and N6 are complete and integrated. F5 is the next planned session and cannot begin until the queue gate passes.

First read the repo-level `../CLAUDE.md`. It gives important local rules: use the project interpreter, `.venv-rwm311/bin/python` beside the repository (its absolute path is in the repo-level CLAUDE.md), edit source templates and generators rather than generated outputs, bind every paper number to a result artifact, preserve the append-only findings ledger, and never edit a running shell script. Then read only:

1. `docs/presubmission/round4/PLAN.md` §1 and the section for the active phase;
2. the **last** entry in `docs/presubmission/round4/SESSION_LOG.md`;
3. only the annexes and files named by that phase;
4. `docs/presubmission/round4/RUN_QUEUE.md` when working on the queue.

Use the latest session log, ledger, result artifacts and current generated paper to resolve conflicts. Older summaries such as `docs/CLOSING_BRIEF.md` and `docs/handoff/REVISION_SUMMARY.md` are historical context, not state authority. Never read the entire `FINDINGS_LEDGER.md`, paper template, paper-number generator, or a large JSON artifact into the context; use targeted ranges and extract requested JSON fields.

## 2. Context and delegation limits

Run the work in the existing F0–F12 order. For each fresh Codex phase, provide only this handoff, `PLAN.md` §1, that phase's section, the latest session-log entry, and its named annexes. At phase boundaries, leave a short checkpoint of at most 1,000 tokens with the exact next action, state, blockers, and relevant file paths. If context is getting large, complete the current item, write the required PARTIAL log entry, and continue in a fresh context; do not re-read completed history.

Do not delegate routine reading, queue management, training, measurements, edits, or decisions. F10 is the sole planned multi-agent review: at most two read-only reviewers, one assigned Appendices A–M and one Appendices N onward. Give each reviewer only its assigned appendix range plus the cited result artifacts needed to check it. Ask for mismatches only, with file/line and a response of at most 300 words. Do not send the full repository, full ledger, entire paper history, or irrelevant prior sessions. Verify every reported finding yourself. If another narrowly scoped review is useful, use one read-only reviewer with the same limits.

## 3. Locked research decisions and accurate framing

The primary target is TMLR. Do not divert the manuscript to another OpenReview venue. The repository's `docs/SUBMISSION_VENUE.md` records that the MLRC 2026 routes are past; recheck only if the user later changes the target.

Preserve these conclusions and their scopes when revising summaries:

- **X3** is pre-registered and tests the A/B comparison across five two-episode folds, including existing fold `{1,8}`. If it passes, it covers 20 independent 400-step trajectories, with each of the ten episodes held out in one fold. The governing comparison is at `h=368`; the 4.61× result at 10,000 iterations is not re-read. X3's outcome must appear in the abstract and contribution 2 with the prominence required by W11, even if it is NOT RESOLVED or REVERSES.
- **X4** is pre-registered: matched autoregressive MLP and transformer, 3 seeds, 2,500 iterations, evaluated at `h=368` against Arm A at 2,500 iterations. It tests parameter count as one axis; it does not make architecture or training settings identical.
- **X5 is NOT RUN.** Do not infer the missing command from measured velocity, construct a reward subset without command-tracking terms, or claim a reward-cost result. The missing command makes that calculation circular/unavailable in this dataset.
- **X6** says disagreement beats the free predicted-step-size signal on the short-unit `h=100` analysis (70 units). That does not settle the comparison on the original long 400-step units at `h=368`. State both scopes wherever summarized.
- **X7** reports pooled epistemic coverage within band at 6 of 6 horizons across 20 trajectories. Its multipliers are fit leaving out one episode, but the released checkpoint itself was trained on all ten episodes. Do not call this out-of-sample model generalization or overstate it as a per-cell guarantee.
- **X8** reports the same verdict for the four rules it re-scores. It is not a blanket validation of every result in the paper.
- N5/N6 are post hoc. Keep that label. X3/X4 never reopen earlier discharged claims. Do not change any pre-registered script, statistic, threshold, family, or verdict after looking at results. A failure of a frozen assertion means BLOCKED and a log; it does not authorize a replacement analysis.

The study remains limited to one robot, gait, terrain and recorded dataset; there is no trained policy evaluation. Cross-fold training improves episode-level held-out evidence within this dataset; it does not supply a new environment or independent data collection. Keep the paper's scope and limitations explicit.

## 4. Execute the approved CPU work in order

### A. Recover and finish the X3/X4 queue

1. Check for active runner/trainer processes and run the exact status command in `RUN_QUEUE.md`. Do not start a second runner if one is active.
2. Require the queue log to end with `queue empty; runner exits`, all 30 IDs in the done list, and zero failures. Follow PLAN §1.2's rule against reading per-run checkpoint results before F5.
3. If the runner is stopped and the queue is incomplete, inspect the queue runner's control files and only the non-checkpoint runner log as needed. Preserve all outputs. `queue_runner.sh` skips IDs already marked done or failed; `queue_run.py` refuses collisions with existing output. Resume only through the existing queue runner and exact committed queue. Do not delete partial JSON or weights to make a run restart. If an unfinished run has a partial/colliding artifact, a failed ID, ambiguous state, or a process still active, stop and record the evidence; do not edit scripts or force-overwrite it.
4. Use the absolute project interpreter and one run at a time as the queue specifies. Do not add training or change the 32 CPU-hour total cap. Do not modify the queue, its runner, or analysis code while it is running.
5. Do not proceed to F5 until the explicit queue gate passes. If the 32-hour cap would be exceeded, stop BLOCKED and report actual elapsed/projected hours.

The exact training jobs are the 24 X3 held-out Arm A/B runs and six X4 size-matched baseline runs in `runs/queue_round4.txt`, each at 2,500 iterations and seeds 0–2. The queue is already pre-registered; do not create a new training design in its place.

### B. F5: discharge the frozen readings

Follow F5 in `PLAN.md` exactly. Verify all queue records, iterations, seeds, held-out episodes, finite losses and weights; verify no failed IDs. Check the SHA-256 recorded in the ledger for `scripts/x3_cross_fold.py` and `scripts/x4_matched_baselines.py`, then run those scripts unchanged. Preserve their assertion and failure behavior. Append the exact returned readings to the ledger and update status lines. F5 makes no paper edits.

### C. F6–F10: revise, shorten, and review the manuscript

- **F6:** integrate X3/X4, update the abstract once to at most 300 words, contributions and Appendix D. Report all readings accurately. Regenerate Appendix E and Figure 1 after the new X3/X4 discharges.
- **F7/F8:** follow the move-not-delete rule and preserve every result, table, interval and verdict. Remove internal ledger labels from main text as W8 specifies. Log word counts and verify cross-references after every move.
- **TMLR format check before large cuts:** current TMLR policies and submission types can change. Before applying a word-count target as if it were the venue limit, verify the current official author instructions, OpenReview submission type, main-content page limit, supplement size, anonymization and template. The existing round-4 target is ≤16,000 main-text words (aim 15,000), but it may not satisfy a current page limit. If the official submission type imposes a tighter limit, record the requirement, move supporting detail into the supplement while preserving the main evidence chain, and meet the venue limit. Do not silently weaken claims, discard results, or modify TMLR style files to fit. If compliance would require changing the scientific scope rather than moving detail, document the exact conflict and stop at that decision point.
- **TMLR writing standard:** the Editors-in-Chief announced in August 2026 that acceptance criteria explicitly include whether the intended audience can understand the findings, why they matter, and what readers learn. F10 should therefore check the first-page motivation, setup, main takeaways, limitations and evidence chain for clarity, not only grammar and length. Official links are in §8.
- **F9:** wire only the planned reproduction stages and checks, regenerate the appendix runtime table and fix the round-3 leftovers listed in PLAN. Keep `NEEDS_WEIGHTS` accurate. Rebuild rather than hand-edit generated files.
- **F10:** read the complete current main text once, chunked to keep context manageable. Run the two bounded read-only appendix checks described above. Verify every item yourself; write `REVIEW.md` and `CONSISTENCY.md` as PLAN specifies. Do not make large changes during review.

### D. F11/F12: freeze, measure, package, verify

Follow PLAN F11 and F12 in order. F11 freezes prose, regenerates claims audits, runs the documented `--quick --force` clean-clone measurement, restates §8 from measured keys, rebuilds both supplementary bundles, and refreshes package documents. F12 is no-edit verification from a fresh clone. Preserve the published clean-clone result exactly as measured: the earlier check found 68 scientific differences among 9,090, with about 99.25% bitwise identity. The criterion remains zero scientific differing values; do not suppress differences with tolerances, hide them, or report the old smaller count. Investigate only within the failure workflow in PLAN; F12 itself makes no fixes.

The 10 October supplementary bundles are stale. Regenerate `supplementary.zip` and `supplementary_anon.zip` from the final frozen state, run the independent deny-list scan, and record their final hashes. Do not upload or publish them from this handoff.

## 5. Local CPU gap-filling: what is available and what is not

The approved X3/X4 queue is the remaining training. No further model training is authorized by the existing round-4 rulings. Do not run the deferred full 48-hour reproduction or add lower-data training (W9). Any additional model-training proposal needs a new written protocol and explicit user ruling before it starts.

Before adding any analysis, inspect the current paper, `SESSION_LOG.md`, `OUT_OF_SCOPE.md`, artifact metadata and reproduction stages to ensure the gap is still open. Avoid duplicating completed work: N5/N6; X6/X7/X8; episode-clustered, per-dimension, shorter-unit and Gaussian-nominal analyses; and the 20-seed synthetic-noise corroboration are already represented in the existing round artifacts/ledger. Confirm exact status from the files, not this summary.

Two additional inference-only sensitivities are plausible on the local CPU. They are optional and exploratory; do not delay the TMLR package or use them to upgrade a pre-registered verdict.

1. **Batching sensitivity for X3 at long horizons.** `OUT_OF_SCOPE.md` records that X8's per-episode versus grouped-batch rollout can shift `h=368` values through float32 rounding (up to roughly 1e-2 in the noted comparison). X3's frozen rule intentionally uses fold-batched rollouts. After F5, if the required X3 checkpoints and recorded trajectories are available, score the same held-out predictions with both the frozen fold batching and per-episode batching at least at `h=100` and `h=368`. First reproduce the known X8 discrepancy on its original cases as a code-path check. Report per-trajectory value changes, sign changes, aggregate interval/verdict under each batching choice, and resource cost. Keep the preregistered X3 reading untouched; label this as a new post hoc sensitivity with a new ledger ID and separate result/script. If the stored inputs are missing or it cannot be reproduced, log that fact rather than reconstructing or substituting data.
2. **Short-unit sensitivity for per-dimension uncertainty tests.** The prior review noted that the M-51 permutation family may not have been recomputed on M-64's shorter non-overlapping units. Check Appendix K, M-51/M-64 ledger entries and artifacts first. If still open and the saved predictions support it, use the same statistic, null, independent-unit definition and Holm family as M-51, with only the documented M-64 unit construction changed. Report the number of units per horizon, per-dimension outcomes, corrected p-values and comparison with original 400-step units. Do not choose a new family or threshold after seeing the data; create a separate post hoc analysis and artifact, and do not change M-51's original verdict.
3. **Rank-metric sensitivity for the uncertainty association.** If the manuscript continues to use “ranking” for the uncertainty-versus-error result, use the exact X6 units and horizons to compute Spearman and Kendall associations for disagreement and predicted step size against absolute error. Report paired episode/unit bootstrap intervals as descriptive sensitivity results, alongside the Pearson statistic already used by X6. Do not add a new significance claim or choose the metric that looks strongest; retain all metrics and label this post hoc. Skip it if the underlying per-unit predictions are not reproducibly available.

For either analysis: write the protocol and script before computing the result; assert shared cases reproduce the existing artifact; use a distinct artifact under `results/`; record wall and CPU time; add a reproducible stage; and label every claim post hoc. First time one representative case to estimate total runtime. If local inputs are absent, the estimate is beyond the remaining practical CPU budget, or the analysis requires a new training run, stop and report it as out of scope. Do not batch both experiments together in one opaque script.

The dataset cannot locally answer questions needing missing command labels, new robots/terrains, additional physical trials, or closed-loop policy reward. In particular, do not try to rescue X5 by inferring commands from achieved velocity. State those limits once in the paper and retain the exact X5 reason.

## 6. Source control, file integrity and external actions

- Keep the existing branch and run log. Follow the repo plan's itemized commits and session log. Do not rewrite history or amend frozen pre-registration commits.
- Numbers in manuscript, model card and README must be generated from `results/` artifacts through `scripts/paper_numbers.py` or the documented generator. Never type derived numbers into prose or generated output.
- Use `PAPER.template.md` and the proper generator for paper edits. Rebuild `PAPER.md`, `PAPER.tex`, `PAPER.pdf`, `MODEL_CARD.md`, tables and bundles only through their documented build paths.
- Preserve anonymity in the main PDF and both upload bundles. Round-4 planning and private run records stay out of anonymous bundles.
- Do not push, merge, upload to Hugging Face, trigger an archive, send author correspondence, or submit to OpenReview as part of this handoff. Prepare the final files and checklist; leave external publication actions to the user. The old plan's human-only actions include merging, model-card re-upload, Software Heritage archiving and submission.

## 7. Completion report

Finish only when F12 has a written `FINAL_REPORT.md`, every required gate is recorded, and the final PDF and both bundles have matching recorded hashes. The final response should give:

- the exact final manuscript and bundle paths;
- TMLR-format/page-limit status and main-text/abstract counts;
- X3/X4 readings and the scopes of X5–X8;
- CPU hours used and any exploratory analysis run or explicitly left open;
- clean-clone and anonymity-gate outcomes;
- any blockers or human actions remaining.

## 8. Current official venue references to recheck at F7/F11

- [TMLR on OpenReview](https://openreview.net/group?id=TMLR) — live venue and submission workflow.
- [TMLR announcement: increased emphasis on clear writing](https://blog.tmlr.org/2026/increasing-emphasis-on-clear-writing-in-acceptance-criteria/) — published 28 August 2026.
- [TMLR announcement: 2026 author submission quotas](https://blog.tmlr.org/2026/annual-author-submission-quotas-for-tmlr/) — applies to submissions from 1 July 2026; check every author's remaining quota before submission.
- [TMLR Beyond PDF instructions](https://tmlr-beyond-pdf.org/submission-instructions) — only consider if the user chooses that format; do not convert this paper without a decision.

At the time of this handoff, the quota policy says all authors must have remaining quota, and its annual count includes rejected, withdrawn and desk-rejected submissions from 1 January 2026; active TMLR reviewers/action editors receive a larger budget. Verify the current rule and author state directly before submission.

## Addendum: user ruling, 16 October 2026

The user adopted this item from a variant of this workplan that another session wrote on 14 October. The rest of that variant, including its LLM-use footnote, was not adopted. The item is that session's reading of the venue rules, so §4C's check at F7 and F11 still applies to it:

- **TMLR format check:** checked against the current official Author Guidelines on 14 October 2026. TMLR permits submissions of any length; unusually long main bodies may take longer to review, and review guidance distinguishes papers above 12 main-content pages. Thus W6's ≤16,000-word target remains an editorial target, not a hard venue cap. Use the official, unmodified TMLR style file/template, preserve double-blind anonymity, and verify the supplement is under 100 MB and in PDF/ZIP format. Recheck the live guide and OpenReview form at F11.
- [TMLR Author Guidelines](https://www.jmlr.org/tmlr/author-guide.html) — any-length format, official template, anonymity and supplementary limits.
