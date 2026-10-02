# Pre-submission plan, round 2 — RWM reproduction, TMLR

Put this file at `docs/presubmission/round2/PLAN.md`. Every session reads §1, its own section, and only the annexes its section names.

Written on 30 Sep 2026 from:
- the paper as of commit `30910fb` (49 pages, identical to `PAPER.pdf` in the working tree; the branch head adds only round 1's closing log);
- round 1's records (`docs/presubmission/`);
- the ledger, `results/` and `runs/`.

Numbers below are for orientation. If an artifact disagrees with this file, the artifact wins; log the difference.

---

## 0. For you (the human)

### 0.1 What this round does

1. **Fixes the seven review items and the smaller points** from the 30 Sep review.
2. **Runs five small new analyses.** Four use weights already on disk (no training):
   - what the alignment defect costs at each horizon;
   - nRMSE aggregated the way §3.1 defines it, for the sweep and the baselines;
   - the sweep compared at equal training compute;
   - why our RSSM fails.
   The fifth, only if the RSSM diagnosis points to training settings, is at most 10 CPU-hours of RSSM retraining in the background.
3. **Adds an appendix of findings that never reached the paper.** The ledger holds 102 contribution-tagged findings; about 15 are not in the paper (§2's T5 lists the candidates).
4. **Cuts the main text by about 30%** by moving detail to appendices. TMLR's guide says unusually long papers "(not counting any Appendices)" are likely to delay review, and reviewers read appendices at their discretion.
5. **Clears round 1's leftover items:**
   - the E7 check;
   - the stale claims audit;
   - the bundle self-test probe;
   - unwired `reproduce.sh` stages;
   - figure label overlaps;
   - the model card's untested sentence and README's ambiguous parenthetical.
6. **Restates §8 from a clean clone, then verifies a second clean clone.** Both happen last.

### 0.2 Decisions: accept the defaults or change them before T0

T0 copies this block into `docs/presubmission/round2/DECISIONS.md` as your rulings. Edit a line here first if you disagree.

| # | Question | Default |
|---|---|---|
| U1 | S-20 withdrew the 75% / 9.5% figures because new evidence contradicted them, but the ledger files it as a *framing*, not a *claim withdrawn on evidence*. | **Reclassify** through a new ledger entry (append-only), so the counts become 7 claims and 6 framings. `ledger_check.py` learns to read reclassification entries. |
| U2 | Allow up to 10 CPU-hours of RSSM retraining if the diagnostic (rule X1) points to training settings? | **Yes**, gated exactly as X1 says. |
| U3 | Length target. Round 1 accepted −1.3%; this ruling supersedes D7. | **Body ≤ 19,000 words** (FILE_MAP §13's command, "to Data and code"), reached by moving detail to appendices and never by deleting a result. Report a shortfall rather than force it. |
| U4 | The abstract's alignment sentence. | **One clause, no numbers**: the defect exists, and its cost is small and not consistent in sign. The numbers stay in the contributions and §7.2. |
| U5 | The claims audit (`submission_check` C1). | **Regenerate it after the text freezes (T11). Do not review** the unreviewed claims; that is recorded as known. |
| U6 | §6 has eleven subsections. | **Merge or move within §6 only.** Renumbering §6.x is allowed with a pointer map; top-level numbers (§7 onward) stay. |

### 0.3 Order and launch

Run T0 → T1 → … → T12 strictly in order. Don't start a session until the one before it has written `status: COMPLETE` in `docs/presubmission/round2/SESSION_LOG.md`.

Launch every session in a **fresh terminal** (never `--resume`), from the repository root:

| Kind | Command |
|---|---|
| Opus 5.5, high effort | `CLAUDE_CODE_SUBAGENT_MODEL=claude-sonnet-5-5 claude --model claude-opus-5-5 --effort high` |
| Opus 5.5, default effort | `CLAUDE_CODE_SUBAGENT_MODEL=claude-sonnet-5-5 claude --model claude-opus-5-5` |
| Sonnet 5.5 | `claude --model claude-sonnet-5-5` |

Round 1's log says effort could not be raised from inside a session, so set it at launch.

Then type: `Read docs/presubmission/round2/PLAN.md §1 and the section for session TX, then carry out session TX.`

- **`PARTIAL`** means the session ran low on room. Start a fresh terminal on the same model and type `Resume session TX.`
- **`BLOCKED`** means the session needs a decision. Answer under its question in `DECISIONS.md`, then type `Resume session TX.`

| ID | Model | Effort | Scope | Time |
|---|---|---|---|---|
| T0 | Sonnet 5.5 | default | Branch, round-2 files, rulings, baseline measurements, preflight assertions | 45 min |
| T1 | Opus 5.5 | high | New analyses N1–N3 (inference only) and their ledger entries | 2 h |
| T2 | Opus 5.5 | high | Pre-register X1; RSSM diagnostics; launch retraining if X1 says so | 1.5 h |
| T3 | Opus 5.5 | high | Alignment demotion, M-23 labelling, Arm B definition, §3.2 generator, small fixes | 2 h |
| T4 | Opus 5.5 | high | §5.2 and §5.3 rewritten with N2, N3 and X1; abstract; contributions; the paper's Appendix D rows | 2 h |
| T5 | Opus 5.5 | default | Coverage audit of the 102 contribution-tagged findings; new Appendix H | 1.5 h |
| T6 | Opus 5.5 | default | Length pass 1: §1–§6.6 | 2 h |
| T7 | Opus 5.5 | default | Length pass 2: §6.7–§12 and the appendices | 2 h |
| T8 | Sonnet 5.5 | default | Retraining gate and evaluation (if run); pipeline hygiene; figure labels | 1.5 h |
| T9 | Opus 5.5 | high | Retraining result into §5.3 (if any); front-matter consistency | 1 h |
| T10 | Opus 5.5 | high | Fresh-eyes review against Annex 4's checklist; small fixes only | 1.5 h |
| T11 | Opus 5.5 | default | Claims-audit regeneration; clean-clone measurement; §8 restatement; bundles; package documents | 3 h + 2 h CPU |
| T12 | Sonnet 5.5 | default | Clean-clone verification and final report. **No edits.** | 1 h + 2 h CPU |

**CPU.** Inference in T1–T2 totals about 1–2 hours. RSSM retraining, if X1 allows it, is at most 10 hours and runs in the background from T2 to T8; T3–T7 edit text only. Each clean clone's `reproduce.sh` takes about 2 hours.

### 0.4 Only you can do these, after T12

1. **Update GitHub's default branch.** `main` is still the 29 Aug state, and its `PAPER.md` prints the withdrawn "overstates its own model's error by 75%". Fast-forward or merge `presubmission2` into `main`.
2. **Re-upload `MODEL_CARD.md` to the Hugging Face model repo.** The live card still says the multiplier was "fitted on held-out data" with no in-sample caveat, and that a consumer "will get materially worse numbers" with the stale pairing, which was never measured for these checkpoints. T1 measures it and T8 rewrites the sentence.
3. **Trigger a Software Heritage archive** of the final pushed commit; §13's timestamp argument relies on it.
4. **Send the author query** (`docs/presubmission/AUTHOR_QUERY_ALIGNMENT.md`) if it has not gone. It is already restated on the independent figures.
5. **Upload** `PAPER.pdf` and `supplementary_anon.zip` using the checksums in the refreshed `docs/SUBMISSION_PACKAGE.md`.

---

## 1. Rules for every session (read in full each time)

### 1.1 Scope
- Do only your own session's items. Log anything else as one line with file:line in `docs/presubmission/round2/OUT_OF_SCOPE.md`, and do not fix it.
- Do not start the next session's work.

### 1.2 Integrity (non-negotiable)
1. **No hand-typed numbers.** Every measured number in the paper is a `{{key}}` from `scripts/paper_numbers.py` (FILE_MAP §2), read from an artifact under `results/`. Model cards and READMEs follow the same rule through their builders.
2. **Edit sources, never outputs.**
   - Paper and docs: `PAPER.template.md`, `README.template.md`, `docs/*.template.md`.
   - Generated text: the generator scripts, for example `evidence_summary.py`, `build_paper.py` captions, `build_model_card.py` and `appendix_g_rules.py`.
3. **The ledger (`FINDINGS_LEDGER.md`) is append-only.** New IDs come from `scripts/ledger_check.py`. A correction is a new entry that names the entry it corrects. The one sanctioned in-place edit is round 1's: a rule's `Status` line at its discharge.
4. **Pre-register before data.** A rule that governs new data (X1 only in this round) is committed and pushed, with a commit subject starting `PRE-REGISTER`, before the data exists, together with the script that computes its reading.
   - An analysis that is not pre-registered is labelled **post hoc** in its ledger entry and in the paper.
   - Post hoc work never re-opens a discharged rule (M-23, M-64, M-74, M-75, M-76, …) and never changes a verdict.
5. **Verify against source, not config** (the project's standing rule).
   - Any new training variant gets a row in `docs/presubmission/BASELINE_SPECS.md`'s deviations table, with a citation. An UNVERIFIED row blocks the run.
   - Every new analysis script asserts that it reproduces an existing artifact on the overlapping cases before producing anything new (each item names its assertion).
6. **Citations** are added only through `scripts/t1_bibliography.py`.
7. **Anonymity.** The deny-list scan passes for the paper and both bundles. `docs/presubmission/` is excluded from both bundles by `EXCLUDE_DIRS`. `round2/` sits inside it and is pruned with it; T0 confirms this.
8. **Never loosen a failing check.**
   - Fix the cause, or report the failure.
   - A check may be re-anchored when its text legitimately moves. Log every re-anchor as old anchor → new anchor.
   - Never retire a numeric assertion.
9. **Move, never delete.** Text leaving the body goes to an appendix, or, if it is drafting history, to `docs/BUILD_CHECKS.template.md`'s "Moved from the paper body" list. No result, number, verdict, table or figure may disappear from the paper and its appendices together.

### 1.3 Tokens and context
- **Start by reading only:** §1, your own section, the last `SESSION_LOG.md` entry, and the annexes your section names.
- **FILE_MAP (`docs/presubmission/FILE_MAP.md`, 38 KB): grep it for the rows you need. Never read it whole.**
- Never read the whole of `FINDINGS_LEDGER.md` (565 KB), `PAPER.template.md` (198 KB) or `paper_numbers.py` (182 KB). Use `grep -n`, then Read with `offset`/`limit`.
- Never print a whole JSON artifact; extract fields with `python -c` or `jq`.
- Send long output to a log file and show `tail -n 40`.
- **Subagents:** at most 2 per session, Explore type, read-only. The launch command's `CLAUDE_CODE_SUBAGENT_MODEL` makes them Sonnet 5.5, so do not pass a `model` argument (an alias there would override the pinned version). Ask them for file:line hits and a conclusion of at most 300 words. Never delegate edits.
- **Checkpoint.** If the conversation has been compacted once, or feels heavy: finish the current item, commit, write a `PARTIAL` entry naming the exact next step, and stop.

### 1.4 Protocol
- **Start gate.** The last log entry must be the previous session with `status: COMPLETE`, or this session with `PARTIAL` or `BLOCKED`.
- **Branch and commits.** Branch `presubmission2` (T0 creates it). One commit per item, subject `[TX][item] summary`. Push at the end of every session.
- **End of every session that edits text:**
  1. Run FILE_MAP §3's fast build, then the gates, then the fast build again.
  2. The second build must be byte-identical to the first (FILE_MAP §3, "Build-order lag").
  3. Append the log entry, commit, push.
- **Log entry template:**

```
## TX — YYYY-MM-DD HH:MM — <model, effort> — status: COMPLETE | PARTIAL | BLOCKED
Commits: <hash> <subject>, one per line
Done: …
Build/gates: pass | fail (<which>)
Paper numbers changed: none | <key: old → new, artifact>
New keys: none | <key, artifact>
Re-anchored checks: none | <check: old → new>
CPU jobs over 1 min: none | <what, how long>
Body words (FILE_MAP §13 command): <n> (T0: <n>)
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
- While RSSM retraining runs (T2–T8), other sessions may run builds and scripts of up to about 10 CPU-minutes each.
- Log any job over 1 minute.
- Never run two training jobs at once (8 GB of RAM).
- Keep the Mac on mains power. The queue runs under `caffeinate -i`, as in round 1.

---

## 2. Sessions

### T0 — Orientation (Sonnet 5.5)
Reads: §0.2, §1.

1. **Working tree.** Check `git status`: the only permitted untracked path is `docs/presubmission/round2/PLAN.md`; anything else means stop with `BLOCKED`. Then:
   - tag HEAD `pre-round2`;
   - create branch `presubmission2` from `presubmission`;
   - commit this plan.
2. **Round-2 files.** Create `SESSION_LOG.md`, `DECISIONS.md` (copy §0.2's table with the note "defaults accepted by launching T0, 2026-MM-DD" or the user's edits), and `OUT_OF_SCOPE.md` in `docs/presubmission/round2/`.
3. **Bundle exclusion.** Dry-run the collection function of both bundle builders (as S5 did) and assert that nothing under `docs/presubmission/round2/` is collected.
4. **Baselines, in `round2/BASELINE_T0.md`:**
   - body words by FILE_MAP §13's command, to "Data and code" and to "References";
   - the same count per `##`/`###` section;
   - page count;
   - pass/fail for every gate after one fast build.
5. **Preflight assertions, in `round2/PREFLIGHT.md`.** Record each as pass/fail; any fail means `BLOCKED`.
   - **P1.** These weights exist:
     - `runs/armA_seed{0,1,2}_10k/weights_{2500,5000,7500,10000}.pt`;
     - `runs/mn_*_seed{0,1,2}/weights_2500.pt` (8 configs);
     - `runs/baseline_*_s7_seed{0,1,2}/weights_2500.pt` (6 families);
     - `runs/armA_seed{0,1,2}/weights_2500.pt`;
     - the released checkpoint, fetched by `setup.sh`.
   - **P2.** Arena identity. Compare §5's by-horizon table (`results/a1_ab_by_horizon.json`), the head-to-head table (`results/head_to_head_accuracy.json`) and the sweep and baseline evaluators (`results/mn_sweep_eval.json`, `results/baselines_eval.json`). Assert their held-out 400-step trajectory start rows (4) are the same rows, or record exactly how they differ.
   - **P3.** The M/N timing probes in `results/mn_sweep_timing.json` were uncontended. Check that their timestamps precede the queue launch (14:51:27, 2026-09-28, `RUN_QUEUE.md`) and that no job in `docs/presubmission/s8_cpu_jobs.json` overlaps them. Record which probes, if any, were contended.
   - **P4.** The M-23 rule's seed-1 values sit at `results/task5_analysis.json` → `gaps["out-of-sample|10000|h368"]`: A = 0.3509, B = 1.5540, gap +1.2033 [0.5606, 2.0467].

### T1 — New analyses N1–N3, inference only (Opus 5.5, high)
Reads: §1, T1, Annex 1 (N1–N3).

Carry out Annex 1's N1, N2 and N3 exactly. For each:
1. write the script under `scripts/` and assert its named reproduction check;
2. run it;
3. commit the artifact;
4. append one ledger entry labelled **post hoc**, with evidence and status.

No paper edits in this session. If any reproduction assertion fails, stop with `BLOCKED`.

Done when the artifacts are committed:
- `results/alignment_by_horizon.json`;
- `results/pooled_nrmse_rescore.json` and `results/pooled_nrmse_alongside.json`;
- `results/mn_compute_matched.json`;
- `results/training_tail_slopes.json`.

Three ledger entries (N1, N2, N3), with the next free IDs.

### T2 — RSSM diagnostics (Opus 5.5, high)
Reads: §1, T2, Annex 1 (X1), `docs/presubmission/BASELINE_SPECS.md` rows 21–38.

1. **Pre-register.** Enter X1 (Annex 1) in the ledger as `PRE-REGISTERED`, with its script `scripts/rssm_diagnostics.py`. Commit with subject `PRE-REGISTER RSSM diagnostic X1, before its readings exist`, and push.
2. **Part A and Part B.** Run them; write `results/rssm_diagnostics.json`. Record Part A's reading in a new ledger entry, exactly as the script returns it.
3. **Part C** runs only if Part A returns NOT EVALUATION-LIMITED **and** ruling U2 allows it.
   - Add the two variants' rows to BASELINE_SPECS (V1, V2: match or deviation, with citation).
   - Run a 20-iteration timing probe on an idle machine and project the hours; if the projection exceeds 10 hours, stop with `BLOCKED`.
   - Append to `runs/queue_round2.txt` and launch it with round 1's runner, as in round 1: `nohup caffeinate -i scripts/queue_runner.sh runs/queue_round2.txt > runs/queue_round2.log 2>&1 &`. Adapt the runner to take a queue file argument, and keep its default behaviour unchanged.
   - Confirm the first run passes 50 iterations. Write `round2/RUN_QUEUE.md` with the runs, the projected finish time and a status command.
4. **No paper edits.**

### T3 — Paper edits, group 1 (Opus 5.5, high)
Reads: §1, T3, Annex 2 (E1, E4, E5), Annex 3 (the abstract's alignment sentence, contributions 2 and 6, the §5 rule paragraph, §7.2's closing sentences), `results/alignment_by_horizon.json` (fields only).

1. **Item 1: the alignment finding becomes minor**, per Annex 2, E1.
2. **Item 4: say what the rule actually ran on**, per Annex 2, E4.
3. **Item 5: say what teacher forcing means next to the headline**, per Annex 2, E5.
4. **§3.2's generator** (`scripts/evidence_summary.py`):
   - (a) Released-checkpoint rows whose arena is the held-out pair are labelled `held-out pair (4)`, not `out-of-sample (4)`. Their in-sample column already says "yes". Currently this affects the §6.8 and §7.2 rows; find any others.
   - (b) The alignment row's verdict text: `defect confirmed in the code; its cost in error is small and not consistent in sign`.
   - (c) Returned verdicts are printed verbatim, in the case the rule returned them. "RWM AHEAD OF ALL THREE" is not lowercased, and "UNDER-POWERED" stays as M-49 returned it. No generated label is re-cased.
5. **Figure 1's caption** (`scripts/build_paper.py`, "Calibration of all four models on the held-out arena"): add that the released checkpoint trained on those episodes (the in-sample caveat of §3). Round 1 left this open.
6. **Retraction counts per ruling U1.** Add the reclassification entry, teach `ledger_check.py` to read it, and regenerate. The introduction and §8 keep reading the same generated keys.
7. **Guard it.** Register two new comparative-claims checks in `check_comparative_claims.py`, including their self-test branches:
   - any sentence citing `d1_ratio` or its `a1_*_h368` cells within 2 lines of "rule" or "pre-register" must also carry `m23_seed`, or name the three-seed extension;
   - no sentence may pair "overstat" with an alignment figure without naming the sign reversal within the same paragraph.

### T4 — Paper edits, group 2: §5.2, §5.3, abstract, contributions (Opus 5.5, high)
Reads: §1, T4, Annex 2 (E2, E3, E6, E7), Annex 3 (whole), the fields of `results/mn_compute_matched.json`, `results/pooled_nrmse_alongside.json`, `results/rssm_diagnostics.json`, `results/training_tail_slopes.json`, and `docs/presubmission/ORIGINAL_SPECS.md` a.4–a.6 and b.4.

1. **Item 2: the configuration claim becomes an accuracy-only statement**, per Annex 2, E2.
2. **Item 3: the architecture claim is softened; RSSM**, per Annex 2, E3. If X1's Part C is still running, write the RSSM paragraph from Parts A and B, and leave the one sentence Part C would fill as a `{{rssm_partc_sentence}}` key whose value reads "Retraining variants are running (X1 Part C)." T9 replaces it, and T10's checklist fails if it survives.
3. **Item 6: nRMSE**, per Annex 2, E6.
4. **The diverged-rollout flag**, per Annex 2, E7.
5. **Abstract and contributions.**
   - Install Annex 3's abstract (choose the configuration sentence variant N3's reading selects) and contribution bullets 2, 3 and 6.
   - Title unchanged. At most 8 bullets, each at most 3 sentences.
   - The abstract must pass C12.1: word cap 370, numeral cap unchanged. Aim for ≤ 350 words; trim wording, not findings.
6. **The paper's Appendix D rows** for the configuration and architecture claims, updated to the new statements.
7. **§3.2 rows** for §5.2 and §5.3: their verdict cells stay verbatim. Add nothing beyond what the generator prints.

### T5 — Coverage audit and Appendix H (Opus 5.5, default)
Reads: §1, T5, `results/claims_to_evidence.md` (102 rows).

1. **Build `round2/COVERAGE.md`**, one row per contribution-tagged ledger entry:
   - its ID and title;
   - **covered** / **partly covered** / **absent**, with the paper line.
2. **How to classify:**
   - (a) An entry is covered if an artifact it names is the `source` of a `paper_numbers` key used in the template. Compute this mechanically.
   - (b) Otherwise, grep the template for its distinguishing phrase or number.
   - (c) Use one Sonnet Explore subagent for (b) if it is long.
3. **Start from these candidates, found absent or near-absent on 30 Sep:**
   - B-02 (falsy-index guard); B-03 (train/test split leak);
   - C-05 (training samples, inference takes the mean); C-07 (actions not normalised); C-09 (no forecast decay factor α in the code); C-11 (`state_min_logstd` gets no gradient from the bound loss); C-13 (three iteration counts: 500, 2,500, 5,000); M-13 (auxiliary branch teacher-forced, state branch autoregressive);
   - D-07 (actions are not joint targets; the action scale was never recorded); D-10 (21 commanded-velocity segments);
   - R-26 (neither arm converged at 2,500); R-29 (the released checkpoint loses to hold-last on 7 of 45 dimensions); R-30 (the long-horizon "heavy tail" is two short regions); R-39 (the h = 368 magnitude rests on an episode-1 outlier, the direction does not); R-45 (matched per-dimension comparison); R-46 (the absolute A/B gap closes with training, the relative advantage does not).
4. **Before including an entry, read it** (grep its heading, then read about 40 lines). Include it only if its status is CONFIRMED and it is not superseded in part without a replacement.
5. **Write Appendix H, "Findings not in the main text":**
   - a compact table with columns finding | evidence (ledger ID, artifact) | bearing on the paper;
   - every number bound to a key (new keys allowed);
   - grouped as *paper-versus-code gaps*, *pipeline defects* and *measurements*.
6. **A pointer in §3 or §7:** one sentence pointing to Appendix H. For R-26, also give one sentence in §5.2's Limits (T4 may already have done this with N3's tail slopes; do not duplicate).
7. **Log omissions.** Record every absent entry you chose to leave out, with its reason, in COVERAGE.md.

### T6 and T7 — Length (Opus 5.5, default)
- **T6** covers the title page to §6.6.
- **T7** covers §6.7 to §12 and the appendices.

Reads: §1, this section, `round2/BASELINE_T0.md`.

**Target (ruling U3).** Body ≤ 19,000 words by FILE_MAP §13's command, to "Data and code", with no result lost (§1.2.9). T6 aims for about 45% of the total cut and T7 for the rest.

**Moves, in priority order. Each leaves at most two sentences and a pointer.**

| From | Leaves in body | To |
|---|---|---|
| §2's survey of public PETS descendants (Q1, R-75, M-72) | the hypothesis and the count | a new appendix |
| §6.3's synthetic-noise experiment details | the derivation and the headline ratio | an appendix |
| §6.5 and §6.9 (113 and 139 words) | — | merged into the subsections they support, chosen by content (for example §6.5, the corrected objective, into §6.3). Renumber §6.x with a pointer map, per ruling U6 |
| §6.6's per-dimension permutation machinery | its conclusion and the reconciliation with §6.7 | an appendix |
| §6.7's robustness checks (the four strengthenings of the index control; the trajectory-level control) | the main table and the step-size result | an appendix |
| §6.10 and §6.11 | one ~700-word section: design, both verdicts, the matched-capacity caveat | detail to an appendix |
| §7.4 (contamination) and §7.5 (variance state) | two sentences each | an appendix (§7.5 already points to Appendix F) |
| §11 (1,900 words) | only limitations not already stated where they bite; ~900 words | cross-references for the rest |
| §12 (900 words) | the three-kind "what should travel" paragraph; ~500 words | — |
| §5 (2,000 words) | the sign test, the seeds paragraph and the "what is small" paragraph, tightened; ~1,500 words | — |
| §1 | ~750 words | — |

**Keep in the body, whatever the count:**
- §9 (the lessons);
- every table §3.2 cites;
- the abstract's numbers;
- every verdict.

**Process:**
- Go one section at a time: Read it with offset/limit, move, build, run the gates, and log words before and after.
- Re-anchor checks that follow text into appendices (log each).
- Run `xref_sweep.py` after every renumbering; it must report 0 suspect pointers.
- If a check's guarded text moves to BUILD_CHECKS, point the check there.
- **T7 ends by reporting:** the final body count against 19,000; the three largest remaining sections; and pages before References.

### T8 — Retraining gate, hygiene, figures (Sonnet 5.5)
Reads: §1, T8, Annex 1 (X1 Part C), `round2/RUN_QUEUE.md` if it exists.

1. **Retraining gate (skip if X1 Part C did not run).**
   - Every queued run is done; the failures file is empty; there are no NaNs; the iterations and seeds are as queued.
   - Evaluate with `scripts/rssm_diagnostics.py --part c`.
   - Record X1's final reading in a new ledger entry, exactly as returned. No prose.
2. **`reproduce.sh` wiring** (no training is executed; verify with the stage listing and `--quick` dry runs). Add `--quick` stages, with a `NEEDS_WEIGHTS` guard where weights are read, for:
   - `alignment_defect_ci.py`, `alignment_by_horizon.py`;
   - `mn_sweep_eval.py`, `verdict_mn_sweep.py`, `baselines_eval.py`, `verdict_baselines.py`;
   - `p5_sweep_power.py`, `p6_baseline_power.py`;
   - `pooled_nrmse_rescore.py`, `mn_compute_matched.py`, `rssm_diagnostics.py`;
   - `docs/presubmission/s8_runtime.py` (move it to `scripts/` and leave a stub that execs the new path).

   Also:
   - stage 21 declares `results/claims_to_evidence.json` as its output;
   - the full-run block drives the drivers round 1 found undriven (`run_10k_d1.sh`, `run_indep_ens.sh`, `run_m49_matched.sh`, `run_nll.sh`, `run_nll_indep_ens.sh`) and the pre-submission queues;
   - classify `paper_numbers.py`'s `step5_arm*` glob for stage 20n8.

   Target: `pipeline_coverage` lists 0 uncovered artifacts, and 20n8 lists 0 unclassified discoveries.
3. **The E7 check.** Apply `/Users/Shared/rwm_verify/evidence/S25F/e7_fix.patch`, test it both ways as its note describes, and commit. If it no longer applies, re-implement the same logic: the check finds `step4_5_timing.json` named in BUILD_CHECKS as well as in the template.
4. **The bundle self-test** (`make_anon_bundle.py`) plants the newest commit's full 40-character hash instead of its 7-character prefix (round 1's OUT_OF_SCOPE). Run the self-test at the current HEAD.
5. **Backups.**
   - `git rm --cached PAPER.template.md.appbak`.
   - Add `*.appbak` and `*.d1bak` to `.gitignore`.
   - Add `.appbak`, `.c2bak`, `.d1bak` and `.rev2bak` to `SKIP_SUFFIX` in both bundle builders.
6. **README's lost-value parenthetical** (round 1's OUT_OF_SCOPE): reword it so it names the recording file and, separately, the file whose value is lost.
7. **Model card.** In `build_model_card.py`, replace "A consumer feeding actions the other way will get materially worse numbers" with N1's measured sensitivity of our Arm A to the stale pairing, bound from `results/alignment_by_horizon.json`, at h = 1 and h = 368, with the arena.
8. **Figures.** Fix the label overlaps round 1 deferred: PDF Figures 1, 2 and 5, and the referee's R5 notes (value labels on bars; the annotation over Figure 2(b)'s zero line).
   - Regenerate through `paper_figures.py`.
   - View each PNG before and after with Read.
   - No data change.

### T9 — Late results and front-matter consistency (Opus 5.5, high)
Reads: §1, T9, Annex 3, the X1 artifacts.

1. **The RSSM sentence.** If X1 Part C ran, replace `{{rssm_partc_sentence}}` with a bound sentence reporting X1's final reading verbatim. If it did not run, the sentence states that no retraining was done and why.
2. **Check the abstract, contributions, §3.2, §4, §9, §11 and §12 against the body after the length pass.** Each number must appear in the body, and each claim must be stated no more strongly than where its evidence sits. Fix only wording.
3. **Budgets.** The abstract stays within C12.1; the contributions stay within ≤ 8 bullets of ≤ 3 sentences.

### T10 — Fresh-eyes review (Opus 5.5, high; new terminal)
Reads: §1, T10, Annex 4.

1. **Write `round2/REVIEW.md`:** pass/fail for every item of Annex 4's checklist, each with file:line.
2. **Two Sonnet Explore agents,** read-only.
   - Agent 1 takes §5 (including §5.2 and §5.3) and the front matter. Agent 2 takes §6–§7 and the new appendices.
   - Each reads every table and every sentence that cites it, and returns only mismatches.
3. **Verify every finding yourself** before acting on it.
4. **Fix only small items** (3 sentences or fewer each). Anything larger means stop with `BLOCKED` and the list.

### T11 — Freeze, restatement, bundles, package (Opus 5.5, default)
Reads: §1, T11; round 1's `SESSION_LOG.md` "## S10-fix" entry (the B3 recipe) and "## S11 (second run)".

1. **Freeze.** From here there are no prose edits except §8's reproduction figures and the documents in step 5.
2. **Regenerate the claims audit** (ruling U5: `task_c1_claims_audit.py` → `results/task_c1_claims_audit.json` and `docs/CLAIMS_AUDIT.md`), then run the fast build and gates. Commit and push.
3. **Measure and restate, following round 1's B3 recipe:**
   - Clone the pushed HEAD into `/Users/Shared/rwm_verify/r2/M1/`, with a fresh venv from `requirements.txt`, and run `reproduce.sh --quick --force`. Evidence goes to `/Users/Shared/rwm_verify/evidence/R2T11/`.
   - Run the verifier three times; the runs must be byte-identical, with 0 scientific differing values.
   - Restate §8's reproduction figures (`ver_*` keys) from that measurement.
   - Refresh the hand-written copies with `docs/presubmission/s10fix_docs.py`.
   - Simulate a clean clone of the restated tree and predict that all reproduction keys match.
   - Push.
4. **Bundles.** Rebuild both bundles on the restated HEAD. The builder scan and the independent deny-list sweep must both find 0 hits in both zips and the PDF.
5. **Package documents.** Refresh `docs/SUBMISSION_CHECKLIST.md`'s known-items section (E7 fixed in T8; C1 regenerated and still unreviewed, per ruling U5). Refresh `docs/SUBMISSION_PACKAGE.md` in full: file sizes and SHA-256s of `PAPER.pdf` and `supplementary_anon.zip`; the abstract; the counts; the title. Refresh the rest of `docs/COVER_STATEMENT.md` (retraction counts, page count). Remove the "pre-edit" banner only when every item is current.

### T12 — Clean-clone verification (Sonnet 5.5) — last; no edits
1. **Clone and rebuild.** Clone the pushed `presubmission2` HEAD into a fresh directory with a fresh venv, using round 1's driver copied to `/Users/Shared/rwm_verify/evidence/R2T12/`.
2. **Run, in order:**
   1. `./setup.sh` (pinned hashes);
   2. `./reproduce.sh --quick --force`;
   3. the full paper build and every gate;
   4. both bundles and the independent deny-list sweep;
   5. the PDF in TMLR anonymous mode.
3. **Criteria:**
   - scientific differing values = **0**;
   - `part_f_gate` fails exactly as §8 publishes it;
   - every reproduction figure the paper prints equals what the clone measures;
   - the PDF equals the committed one after blanking dates and ID;
   - 0 deny-list hits;
   - `submission_check` returns what `SUBMISSION_CHECKLIST.md` records.
4. **Write `round2/FINAL_REPORT.md`:** pages; body words against T0; every gate against T0.
5. **On any failure:** no fixes. Stop with `BLOCKED` and the logs; the user runs "T11-fix" on Opus, then T12 again.
6. **Log entry:** list §0.4's five user steps as reminders.

---

## Annex 1 — The new analyses

All run on existing weights; none trains a model except X1 Part C. Relative-L1 and nRMSE are cumulative over steps 1..h, as in §3.1. **No shared bootstrap function exists** (FILE_MAP §7): each analysis imports the one used by the result it extends, named below, and never writes its own.

### N1 — Alignment cost by horizon, and our models' sensitivity to the stale pairing (post hoc)

**Script:** `scripts/alignment_by_horizon.py` → `results/alignment_by_horizon.json`. Reuse `alignment_defect_ci.py`'s `rollout` and statistics by importing them, not by copying.

1. **The released checkpoint.**
   - Horizons {1, 8, 32, 100, 128, 368}; arenas `held_out_n4` and `all_ten_n20`.
   - Overstatement = err(offset 0) / err(offset 1) − 1, in relative-L1 and nRMSE form 1, each with the same interval as `alignment_defect_ci.py`: exact over 256 resamples at n = 4, and 20,000 Monte Carlo resamples at n = 20, seed 0.
   - **Assert** that the h = 368 values equal `alignment_defect_ci.json` to 1e-9.
2. **Our Arm A** (seeds 0–2, at 2,500 and at 10,000), all trained with offset 1.
   - The same ratio: err(offset 0) / err(offset 1) − 1, held-out arena, all six horizons, 3-seed mean with the per-seed values.
   - This answers the model card's untested sentence.
3. **Store the per-trajectory values.** The paper's sentence on sensitivity (Annex 2, E1) uses them.

### N2 — nRMSE as §3.1 defines it, for the sweep and the baselines (post hoc)

**Script:** `scripts/pooled_nrmse_rescore.py` → `results/pooled_nrmse_rescore.json` and `results/pooled_nrmse_alongside.json`.

1. **The problem.** The sweep and baseline evaluators average nRMSE per trajectory, but §3.1's form 1 pools across trajectories, as `head_to_head_accuracy.py` does. On RWM at h = 368 that is 0.4911 against 0.5425. The stored per-trajectory values cannot be converted (checked on 30 Sep: √(mean of squares) gives 0.5162), so re-run the rollouts.
2. **Score every model with pooled form 1:** the sweep configs and the centre (2,500 weights) and the 6 baseline families × 3 seeds, in both arenas, at all six horizons. Use each evaluator's own rollout code (import it) and `rwm_metrics.nrmse_pooled`.
3. **Assert:**
   - (a) RWM's pooled nRMSE equals `head_to_head_accuracy.json`'s Arm A values at h ∈ {1, 8, 100, 368} to 1e-6;
   - (b) every model's relative-L1 equals the committed evaluator artifacts to 1e-6.
4. **Recompute each rule's alongside nRMSE readings** (M-74, M-75, M-76) by calling the verdict scripts' own reading functions on a copy of the evaluation data whose nRMSE fields hold the pooled values. **Never edit the committed eval or verdict artifacts.** Record, per reading, the committed and the pooled values side by side.
5. **Ledger entry.**
   - The evaluators deviated from §3.1's aggregation.
   - Governing verdicts use relative-L1 and are unaffected.
   - List the alongside readings whose result changed, if any. A change is reported, never substituted into a discharged rule.

### N3 — The sweep at equal training compute, and non-convergence (post hoc)

**Scripts:** `scripts/mn_compute_matched.py` → `results/mn_compute_matched.json`; `scripts/training_tail_slopes.py` → `results/training_tail_slopes.json`.

1. **Relative cost per iteration.** `steady_s_per_iter` from `results/mn_sweep_timing.json`, divided by the centre probe's (1.069 s). About 1.35× for (32, 16), 1.81× for (32, 32), 0.40× for (8, 8) and 0.26× for (2, 8).
   - Use only probes that preflight P3 found uncontended.
   - Re-probe any contended config for 50 iterations on an idle machine.
   - Re-probe the six baseline families likewise, because their round-1 probes ran contended. Also record time per rollout step at inference for each family.
2. **The centre at more compute.** Score the Arm A 10k runs' checkpoints at 2,500, 5,000, 7,500 and 10,000 iterations (seeds 0–2) with the sweep evaluator's code, on its held-out and in-sample arenas.
   - **Assert** that the 2,500 checkpoint reproduces the sweep's centre row exactly (relative-L1 at every horizon to 1e-6). The 10k runs replicate the 2,500 runs bitwise (`task_d1_threeseed.json` cross-check), so this must hold; if it does not, stop with `BLOCKED`.
3. **The reading** (post hoc, not a rule): the paired difference err(config @ 2,500) − err(centre @ k) at h = 100 and h = 368, with M-74's statistic and interval imported from `scripts/verdict_mn_sweep.py`, and no Holm verdict.
   - Configs: (32, 16), (32, 32), (8, 8) and (2, 8).
   - k ∈ {2,500, 5,000, 10,000}.
   - Label each comparison with both compute ratios. The centre at 5,000 has 2.00× the centre-at-2,500 compute, which exceeds every winner's cost at 2,500.
   - **Declare post hoc** in the ledger: §5 already printed the centre at 10,000 on (P2 permitting) the same four trajectories, 0.3582 at h = 368, against (32, 32)'s 0.2987 at 2,500.
4. **Tail slopes.** The training-loss slope over the final 250 iterations for every sweep run, every baseline run and Arm A/B at 2,500 and 10,000. Use the run artifacts' `state_loss_tail_slope_250` where present; otherwise compute it from `curves.state` with the same definition, and assert that definition reproduces the stored slope on the runs that have one.

### X1 — RSSM diagnostic (PRE-REGISTERED in T2 before any reading exists; exploratory; never re-opens M-75 or M-76)

**Question.** Is our RSSM's long-horizon failure a matter of how we read its forecast, of its training settings, or of neither setting we can test from its source papers?

**Arena.** §5.2's: held-out pair, 4 non-overlapping 400-step trajectories, relative-L1. Horizons {1, 8, 32, 100, 368}. The hold-last floor comes from `baselines_verdict.json`.

**Part A — read-out (existing weights; 6 RSSM runs at 2,500).** In the forecast steps, three read-outs of the prior's categorical latent:
- **mode:** as run, BASELINE_SPECS row 31;
- **expected:** class probabilities fed in place of the one-hot;
- **sampled:** the mean decoded state over 16 sampled rollouts, generator seed 0.

**Assert** that the mode read-out reproduces `baselines_eval.json` to 1e-6.

Reading (teacher-forced RSSM, 3-seed mean):
- **EVALUATION-LIMITED** if the expected or the sampled read-out is below the floor at h = 32 and all four per-trajectory differences from the floor are negative;
- **NOT EVALUATION-LIMITED** otherwise.

The autoregressive RSSM is reported alongside.

**Part B — descriptive, no reading.** Over the 32 history steps of each held-out window:
- the one-step decoded error of the prior against the posterior;
- the KL per step;
- the same quantities at the 500-iteration checkpoint.

**Part C — only if Part A is NOT EVALUATION-LIMITED and ruling U2 allows it.** Two training variants, teacher-forced, seed 0, 2,500 iterations, everything else as M-75:
- **V1:** PlaNet's KL settings (weight 1.0, 3 free nats, no balancing; BASELINE_SPECS row 36);
- **V2:** DreamerV2's layer-normalised GRU (row 22).

A variant **RESCUES** on seed 0 if its mode read-out is below the floor at h = 32 with all four per-trajectory differences negative. For a variant that rescues, seeds 1–2 run, and the 3-seed mean is read with the same criterion.

**Cap:** 10 projected CPU-hours; stop with `BLOCKED` beyond it.

**Final reading, exactly one of:**
- **EVALUATION-LIMITED**;
- **SETTING-LIMITED (V1 | V2)**, if a variant rescues on 3 seeds;
- **NOT RESCUED BY THE SETTINGS TRIED**;
- **NOT RUN (ruling U2)**.

**Reported in** §5.3 (one paragraph) and in an exploratory table in an appendix. M-75/M-76 rows and verdicts are unchanged.

---

## Annex 2 — What each paper edit must achieve

Anchors are phrases from the 30 Sep PDF. The source may differ in dashes, quotes and math markup, so grep loosely.

### E1 — The alignment finding becomes minor (review item 1)
- **§3.2's row:** T3 item 4(b).
- **The abstract:** per ruling U4, one clause with no numbers (Annex 3). "on the same trajectories" goes.
- **Contribution bullet 6:** Annex 3's text.
- **§7.2:**
  - Move "The … (nRMSE) and … (relative-L1) this paper reported before came from … they are withdrawn (S-20)" to BUILD_CHECKS' moved-from-body list. §8's retraction count already carries S-20.
  - Add one sentence from N1 on horizon dependence. If h = 1's interval on the held-out pair excludes zero, say the stale action matters most where the model is trained; if not, say that even at one step the cost is not resolvable on four trajectories. Use whichever is true, with the bound figures.
  - Add one sentence on our models' sensitivity (N1 part 2).
- **§3 (effective sample size):** add one sentence. A one-step shift of the action moves single trajectories' 368-step error from `{{ad20_traj_lo}}`% to `{{ad20_traj_hi}}`%, which is why four trajectories bound every long-horizon claim.
- **§3.1 "Which metric each headline uses":** match the new framing.
- **Anchors:** "overstating the checkpoint's error on the same trajectories"; "The released evaluation is misaligned by one step"; "this paper reported before"; "confirmed; the released pairing scores worse".

### E2 — The configuration claim becomes an accuracy-only statement (review item 2)
- **Say it once, where the claim is stated:** the original claims an optimal *trade-off* between accuracy and training time, and its own heatmap ties (32, 8) with (32, 32) on accuracy (already in §5.2's first paragraph).
- **The abstract and contribution 3** stop saying "beaten" and "not optimal" without that qualifier (Annex 3).
- **§5.2's table.** Replace "hours per run" with **"cost per iteration, relative to the centre"** (N3 part 1), which fills the centre's blank cell (1.00). Move wall-clock hours to the paper's Appendix B runtime table, with its overlap note.
- **Add a paragraph "Accuracy at equal compute"** from N3's reading, labelled post hoc. Use the Annex 3 variant N3 selects:
  - (a) if the centre at 5,000 iterations is still behind the best neighbour at 2,500 with an interval excluding zero at h = 368, say the win is not an artefact of extra computation per iteration;
  - (b) otherwise, say that at matched compute the difference is not resolved.
- **Emphasise the history-length finding** (currently in "The original's direction on M holds only in part"). On the governing reading, histories of 2 and 8 steps beat 32 at our budget, whereas the original's error falls steeply up to M = 8. Add it to contribution 3 in one clause.
- **Limits** gains one clause from N3 part 4: every run's training loss is still falling at 2,500 iterations (slopes `{{…}}` to `{{…}}`), so the ranking is at this budget, not at convergence.
- **Anchors:** "its chosen history and forecast lengths are beaten at our budget"; "are not optimal at our budget"; "hours per run"; "— (existing runs)".

### E3 — The architecture claim is softened, and the RSSM is diagnosed (review item 3)
- **Abstract, contribution 3, §5.3's Result:**
  - RWM is ahead of baselines built to our reading of Table S7 and trained with RWM's settings, for 2,500 iterations;
  - at h = 368 every baseline, in both regimes, is worse than predicting no change (`bl_table` already shows it);
  - where the lead begins, read from the rules' alongside results in `baselines_verdict.json`, not from this plan. On 30 Sep, the lead over the teacher-forced baselines resolved from h = 32, and the lead over the autoregressive MLP and transformer only from h = 100; before those horizons they cannot be told apart from RWM.
- **Add the h = 100 reading from M-76's alongside results** (already in `baselines_verdict.json`). The autoregressive MLP is behind by 0.060 [0.024, 0.096] (about 12.5% of RWM's 0.4798) and the transformer by 0.102 [0.034, 0.185], still resolved in RWM's favour at the method's own horizon. Bind both.
- **RSSM paragraph** (replacing "Where ours departs" and the RSSM sentences in Limits):
  - its teacher-forced version is the most accurate model at h = 1 (0.0761, below RWM's 0.1232 and the floor's 0.0796, not resolvable);
  - it collapses open-loop by h = 32;
  - X1's Part A and Part B readings, verbatim;
  - the Part C sentence (T9).
  - State plainly that the RSSM comparison is uninformative unless X1 says otherwise, so the architecture claim rests on the MLP and transformer.
- **Anchors:** "architecture claim holds"; "Its architecture claim holds"; "Where ours departs"; "every baseline row is above the hold-last floor".

### E4 — Say what the rule actually ran on (review item 4)
- **New keys** from `task5_analysis.json` `gaps["out-of-sample|10000|h368"]`: `m23_A_s1`, `m23_B_s1` and `m23_ratio` (B/A to 2 decimals, 4.43). `m23_ci_lo/hi` already exist.
- **§5's rule paragraph:** the rule was run on seed `{{m23_seed}}` of each arm; its verdict rests on A `{{m23_A_s1}}` against B `{{m23_B_s1}}` ({{m23_ratio}}×), gap interval [{{m23_ci_lo}}, {{m23_ci_hi}}]. Seeds 0 and 2 were trained afterwards (cite R-60 and its commit date), so the three-seed values carry no pre-registration weight.
- **The table row label** "*(pre-registered)*" becomes "*(the rule's horizon)*", with one caption sentence on seeds.
- **Figure caption** (`build_paper.py`, `paper_fig6_ab_by_horizon.png`): "Only the h = 368 figure is pre-registered (M-23)" becomes "Rule M-23 was run at h = 368 on seed 1 of each arm; these three-seed values, and every other horizon, were computed afterwards."
- **§11** ("The headline A/B result is not among them: it is a three-seed …") says the verdict is single-seed and the magnitudes three-seed.
- **The abstract and contribution 2:** Annex 3's text.

### E5 — Say what teacher forcing means next to the headline (review item 5)
Add one sentence in §5, next to the first `{{d1_ratio}}`: Arm B predicts each of the window's `{{win_fore}}` forecast targets from true inputs, where the original's teacher forcing is N = 1. The sweep's `{{mn_n1_label}}`, trained that way, is `{{mn_tf_ratio}}`× worse than the centre at h = 368 (§5.2), so the claim holds under both definitions. §4's existing sentence stays, shortened to a pointer.

### E6 — nRMSE (review item 6)
- **§5.2 and §5.3's alongside clauses** use N2's pooled readings.
- **The head-to-head table's baseline nRMSE cells** ("—") are filled from `pooled_nrmse_rescore.json`, and the caption sentence "its nRMSE is aggregated per trajectory rather than pooled, so it is not shown here" goes.
- **One sentence in §5.2's arena paragraph:** the rules' evaluator averaged nRMSE per trajectory; the pooled readings were computed afterwards and {agree | differ at …} (cite N2's ledger entry).

### E7 — Runaway rollouts (small point)
- **Define the flag in N2's artifact, before rendering:** a row is *diverged* if any seed's mean relative-L1 at h = 368 exceeds 10× the hold-last floor.
- **Mark flagged rows** in `bl_table` and the head-to-head table with †. The caption says the mean over seeds is dominated by run-away rollouts, gives the per-seed values, and notes that no verdict depends on the magnitude, only on the sign.
- By the 30 Sep numbers this flags MLP-tf (145.2), transformer-tf (15.2) and RSSM-ar (10.6). Report whatever the definition returns.

---

## Annex 3 — Draft text (T3, T4 and T9 install it; bind every key; wording may be tightened, claims may not be strengthened)

**Abstract.** Replace these three sentences and leave the rest unchanged.

- **Base claim:**
  > The base paper's central training claim reproduces under a rule committed in advance and run on one seed per arm; over {{d1_seeds}} seeds, training on the model's own rollouts beats teacher forcing by {{d1_ratio}}× at {{v2_diag_h}} steps and {{d1_ratio_h100}}× at {{v2_deploy_h}}, though teacher forcing leads at one step.

- **Two more claims.** Replaces "The base paper's architecture claim holds … beaten at our budget."
  > RWM is ahead of MLP, RSSM and transformer baselines built to our reading of the original and trained with RWM's settings, though at {{v2_diag_h}} steps every baseline predicts worse than assuming nothing changes.

  Then the variant N3 selects:
  - (a) > On accuracy alone, two shorter histories and both longer training forecasts beat the original's chosen setting at our budget, the best of them even when the original's setting gets more training compute; the original chose its setting as a trade-off with training time, which we do not test.
  - (b) > On accuracy alone at a fixed iteration count, two shorter histories and both longer training forecasts beat the original's chosen setting at our budget; the longer forecasts also cost more computation per iteration, and at matched compute their advantage is not resolved. The original chose its setting as a trade-off with training time, which we do not test.

  N3 selects (a) if, for the best neighbour at h = 368, err(neighbour @ 2,500) − err(centre @ 5,000) has an interval that excludes zero in the neighbour's favour; otherwise (b). If the list of winners in `mn_better_list` is no longer two histories and two forecasts, reword "two shorter histories and both longer training forecasts" to match it.

- **Alignment**, ruling U4. Replaces "Separately, the released evaluation pairs … the sign reverses."
  > Separately, the released evaluation pairs each prediction with the previous step's action; what that costs in error is small and not consistent in sign.

**Contribution 2.**
> **The base paper's central training claim reproduces, and reverses at one step.** A rule committed before the runs, run on one seed per arm, found autoregressive training ahead by {{m23_ratio}}× at h = {{v2_diag_h}}; over {{d1_seeds}} seeds the factor is {{d1_ratio}}×, and {{d1_ratio_h100}}× at h = {{v2_deploy_h}} (§5). At one step a second pre-registered rule, on {{m64_h1_n}} independent {{m64_h1_unit}}-row units, finds a gap of {{m64_h1_gap}} {{m64_h1_ci}} in favour of **teacher forcing**.

**Contribution 3.**
> **Two more of the base paper's claims, tested under rules committed before the runs.** RWM is ahead at h = {{v2_diag_h}} of MLP, RSSM and transformer baselines built to our reading of its specification and trained with its settings, whether teacher-forced as the original trains them or autoregressively, though every baseline is worse there than predicting no change and [X1's reading, one clause] (§5.3). On accuracy alone, {{mn_n_better_word}} of the {{mn_n_configs_word}} one-factor neighbours of the original's {{mn_centre_label}} beat it at our budget — two shorter histories and both longer training forecasts — [N3 clause: "even at equal compute" | "though not resolvably at equal compute"]; the original chose it as a trade-off with training time, which we do not test (§5.2).

**Contribution 6.**
> **The released evaluation is misaligned by one step; what that costs is small and not consistent in sign.** Evaluation feeds the action from *t−1* where training pairs states and actions index-for-index. On {{ad_nind}} independent held-out trajectories this raises the checkpoint's error at h = {{v2_diag_h}} by {{ad_rel}}% {{ad_rel_ci}} on relative-L1 and {{ad_nrmse}}% {{ad_nrmse_ci}} in nRMSE; over all ten episodes the sign reverses (§7.2). Shifting evaluation's action index by one step fixes it.

**§5, the rule paragraph (E4).** Add after "Three conditions, all required: …":
> The rule was run on seed {{m23_seed}} of each arm: autoregressive {{m23_A_s1}} against teacher forcing {{m23_B_s1}} at h = {{v2_diag_h}}, {{m23_ratio}}×, gap interval [{{m23_ci_lo}}, {{m23_ci_hi}}]. Seeds 0 and 2 were trained after the verdict, so the three-seed figures below extend it and carry none of its weight.

**§7.2's closing sentences** replace "The … this paper reported before … (S-20)." Use the variant N1 supports:
- (a) if the h = 1 interval on the held-out pair excludes zero:
  > One step ahead, where a stale action should matter most, it changes the checkpoint's error by {{adh_rel_h1}}% {{adh_rel_ci_h1}} on the same four trajectories.
- (b) otherwise:
  > Even one step ahead, where a stale action should matter most, the change is {{adh_rel_h1}}% {{adh_rel_ci_h1}}, not resolvable on four trajectories.

Then, in both cases:
> Our own checkpoints, trained under the causal pairing, change by {{stale_armA_rel_h1}}% at h = 1 and {{stale_armA_rel_h368}}% at h = {{v2_diag_h}} when fed the stale one.

---

## Annex 4 — Anchors, and the checklist for T10

1. **Alignment.**
   - The abstract has one alignment clause with no numbers.
   - §3.2's alignment row reads "defect confirmed in the code; its cost in error is small and not consistent in sign".
   - No sentence pairs "overstat…" with a figure without the reversal.
   - §7.2 has no "reported before" sentence and carries N1's horizon and sensitivity sentences.
2. **Configuration.**
   - The words "trade-off" and "accuracy alone" appear wherever the verdict is stated in the abstract, contributions, §3.2's claim text and the paper's Appendix D.
   - The centre's cost cell is filled.
   - The equal-compute paragraph is labelled post hoc.
   - Tail slopes are in Limits.
3. **Architecture.**
   - Every statement of the verdict mentions RWM's settings, and that baselines are worse than no change at h = 368.
   - The h = 100 reading is bound.
   - The RSSM paragraph states X1's reading verbatim.
   - The placeholder "Retraining variants are running" does not survive.
4. **M-23.**
   - Every place that ties `d1_ratio` to the rule says seed 1 and the three-seed extension (abstract, contribution 2, §5, the figure caption, §11).
   - The table row is labelled "the rule's horizon".
5. **Teacher forcing.** §5 has E5's sentence next to the first 4.61×.
6. **nRMSE.** §5.2 and §5.3 cite pooled readings; the head-to-head baseline nRMSE cells are filled; N2's ledger entry exists.
7. **Small points.**
   - Verdicts are verbatim in their returned case.
   - Released-checkpoint rows on the held-out pair are labelled "held-out pair".
   - Figure 1's caption carries the in-sample caveat.
   - † flags are defined and captioned.
   - Retraction counts follow ruling U1 and are identical in the introduction and §8.
8. **Appendix H exists.** COVERAGE.md accounts for all 102 entries, and every absent entry is either in Appendix H or listed with a reason.
9. **Length.** The body is ≤ 19,000 words, or the shortfall is reported. No result is lost: diff the set of `{{keys}}` in the template against T0's; every removed key must be justified in the log. §9 is intact. `xref_sweep` finds 0 suspect pointers.
10. **Front matter.**
    - Every number in the abstract and contributions appears in the body, bound.
    - The title, abstract and conclusion agree.
    - The abstract passes C12.1.
    - There are ≤ 8 bullets of ≤ 3 sentences.
11. **Captions.** Every table and figure caption carries its arena, n_independent and checkpoint.
12. **Public-facing text.** README and model card carry no unscoped multiplier claim and no unmeasured "materially worse" sentence.
