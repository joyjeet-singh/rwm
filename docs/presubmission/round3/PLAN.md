# Pre-submission plan, round 3 — RWM reproduction, TMLR

Put this file at `docs/presubmission/round3/PLAN.md`. Every session reads §1, its own section, and only the annexes its section names.

Written on 4 Oct 2026 from:
- a full fresh read of the paper at commit `8c2c903` (the 4 Oct draft: 57 pages, `PAPER.pdf` SHA-256 `50df8761…`);
- round 2's records (`docs/presubmission/round2/`), especially `OUT_OF_SCOPE.md`, `DECISIONS.md` and `FINAL_REPORT.md`;
- the artifacts `results/mn_compute_matched.json`, `results/alignment_by_horizon.json`, `results/pooled_nrmse_alongside.json` and `results/q1_pets_descendants.json`;
- `docs/presubmission/ORIGINAL_SPECS.md` a.4–a.8.

Numbers below are for orientation. If an artifact disagrees with this file, the artifact wins; log the difference.

---

## 0. For you (the human)

### 0.1 What this round does

1. **Fixes four real problems found by reading the 4 Oct draft again from the start.**
   - **The summaries overstate the "equal training time" result.** The abstract, contribution 3 and Appendix D say the best of the longer-forecast settings beats the original's setting "even when that setting trains twice as long". The paper's own body says something narrower. Give the original's setting about the same total compute and the four measurements split: one still favours the longer forecast, one favours the original's setting, and two can't tell them apart.
     - The §5.2 heading "The history length departs furthest from the original" has a related problem. Shorter histories win at our training length, but the original's setting overtakes them when trained four times as long.
     - The cause is round 2's own plan. Its rule for choosing the abstract's wording (round 2 Annex 3, variant (a) or (b)) looked at only one of the four measurements.
     - This round replaces that rule with a general one (§1.2, rule 10): a summary may claim a direction only if every measurement the body reports agrees with it.
   - **The cost of the action-timing bug is described from 4 trajectories when 20 exist.** The released model trained on all ten episodes, so the larger set (20 trajectories) describes it better. On those 20 trajectories:
     - the wrong timing clearly raises error up to 32 steps ahead on the paper's main measure;
     - on the second measure, the one-step rise can't be told apart from noise;
     - at the method's 100-step horizon, the change can't be told apart from noise either.

     The draft quotes "+22.5% at the method's own horizon" from the 4-trajectory set alone.
   - **Our own models hardly notice the timing bug, and nobody has checked why.** Given the action one step late, the released model's error rises by about a third, while ours changes by 0.2%. There are two possible explanations: consecutive actions are almost identical, or our models barely use the action at all. The second would matter a great deal, because a world model that ignores actions can't be used to train a robot's policy.
     - A new small test (**rule X2**) settles which explanation holds. Its pass/fail thresholds are committed to git before it runs.
     - It uses weights already on disk: minutes of computer time and no training.
     - Its answer decides one sentence in the abstract and a few elsewhere.
   - **A note in §5.2 belongs in §5.3.** Two changed readings of the second error measure (nRMSE) are about §5.3's comparison with other model designs, not §5.2's settings sweep. The note doesn't say which designs moved.
2. **Makes about 20 smaller clarity fixes** (session R4 lists them).
3. **Clears round 2's leftover items:** its `OUT_OF_SCOPE.md` and the open items in its final report.
4. **Stops the main text from growing.** §3.2's three-page table moves into Appendix D.
5. **Rebuilds, re-measures from a clean copy, and verifies.** These steps come last.

### 0.2 Decisions: accept the defaults or change them before R0

R0 copies this block into `docs/presubmission/round3/DECISIONS.md` as your rulings. To disagree with a default, edit its line here before you launch R0.

| # | Question | Default |
|---|---|---|
| V1 | Rule X2's design and thresholds (Annex 1). | **As written.** |
| V2 | What happens if X2 finds that our models barely respond to the action. | **Report it fully:** one clause in the abstract, a lesson in §9, a limitation in §5 and §11, and a caveat in the model card. |
| V3 | The abstract's sentence on history and forecast lengths. | **Annex 3's version.** It drops "even when that setting trains twice as long" and says that which setting wins depends on how long each is trained. |
| V4 | The abstract's sentence on action timing. | **One clause, with no effect sizes, describing all ten episodes:** the bug raises error at short horizons, and from the method's 100-step horizon the change is not resolved. |
| V5 | §3.2's table (about 3 pages). | **Move it into Appendix D as a second table.** §3.2 keeps its opening paragraph and a pointer, and every caption keeps its own arena, sample size and checkpoint. |
| V6 | Figure 1 plots 8 of the 22 rules, but its caption says "each decision rule". | **Redraw it over every rule**, from `results/appendix_g_rules.json`. The alternative is to fix the caption only. |
| V7 | §13's paragraph "On anonymity, stated rather than implied" says a reviewer "who chooses to look can identify the author". | **Shorten it to two sentences.** Keep the facts (the code is public, the submission bundle is scrubbed, and the reasoning is in `docs/DOUBLE_BLIND_DECISION.md`) and drop the invitation. The alternatives are to keep it as it is or remove it. |
| V8 | Length. | **Main text no longer than round 2's final count, 20,771 words** (FILE_MAP §13's command), and aim for 20,000 or fewer. Get there by moving text, never deleting it, and report any shortfall. |
| V9 | Add a §5.3 limitation that the RSSM was never tried with PlaNet's "latent overshooting", a training method aimed at exactly the long-range collapse ours shows? | **Yes, one clause, if the attribution checks out against PlaNet's own text** (through `t1_bibliography.py`). Otherwise skip it and log why. |
| V10 | Five training scripts report success even when training fails (round 2 OUT_OF_SCOPE, B8). | **Fix them to report failure.** No training is run to test this. |

### 0.3 Order and launch

Run R0 → R1 → … → R9 strictly in order. Don't start a session until the one before it has written `status: COMPLETE` in `docs/presubmission/round3/SESSION_LOG.md`.

Launch every session in a **fresh terminal** (never `--resume`), from the repository root:

| Kind | Command |
|---|---|
| Opus 5.5, high effort | `CLAUDE_CODE_SUBAGENT_MODEL=claude-sonnet-5-5 claude --model claude-opus-5-5 --effort high` |
| Opus 5.5, default effort | `CLAUDE_CODE_SUBAGENT_MODEL=claude-sonnet-5-5 claude --model claude-opus-5-5` |
| Sonnet 5.5 | `claude --model claude-sonnet-5-5` |

Round 2 ran its Opus sessions at `--effort xhigh`, and that is fine here too. Effort can't be raised from inside a session, so set it at launch.

Then type: `Read docs/presubmission/round3/PLAN.md §1 and the section for session RX, then carry out session RX.`

- **`PARTIAL`** means the session ran low on room. Start a fresh terminal on the same model and type `Resume session RX.`
- **`BLOCKED`** means the session needs a decision. Answer under its question in `DECISIONS.md`, then type `Resume session RX.`

| ID | Model | Effort | Scope | Time |
|---|---|---|---|---|
| R0 | Sonnet 5.5 | default | Branch, round-3 files, rulings, baseline measurements, preflight checks | 45 min |
| R1 | Opus 5.5 | high | Pre-register rule X2, run it (inference only), record its reading. No paper edits | 1.5 h |
| R2 | Opus 5.5 | high | The configuration claim at equal compute (E1); the nRMSE note moved to §5.3 (E4); the RSSM clause (E5); abstract sentence, contribution 3, Appendix D, §12; guard G1 | 2 h |
| R3 | Opus 5.5 | high | Action timing on all ten episodes (E2); X2 into the paper and the model card (E3); abstract and contribution 7; guards G2–G3 | 2 h |
| R4 | Opus 5.5 | default | The small items S1–S17, including Figure 1 | 2 h |
| R5 | Sonnet 5.5 | default | Pipeline hygiene H1–H7: training scripts, ledger corrections, `reproduce.sh` wiring, stale artifact prose | 1.5 h |
| R6 | Opus 5.5 | default | Length (§3.2's table into Appendix D) and front-matter consistency | 1.5 h |
| R7 | Opus 5.5 | high | Fresh-eyes review against Annex 4. Reads the main text in full. **New terminal** | 2 h |
| R8 | Opus 5.5 | default | Freeze; claims audit; clean-clone measurement and §8 restatement; bundles; package documents | 3 h + 2 h CPU |
| R9 | Sonnet 5.5 | default | Clean-clone verification and final report. **No edits** | 1 h + 2 h CPU |

**CPU.** R1's inference is capped at 30 CPU-minutes. Every other session before R8 runs builds and scripts only. Each clean clone's `reproduce.sh` takes about 2 hours.

### 0.4 Only you can do these, after R9

Round 2's five steps still apply, because nothing has been uploaded or published yet. Round 3 replaces their checksums.

1. **Update GitHub's default branch.** Fast-forward or merge `presubmission3` into `main`; `main` still holds the 29 Aug state.
2. **Re-upload `MODEL_CARD.md` to the Hugging Face model repo.** It gains X2's result in R3.
3. **Trigger a Software Heritage archive of the final pushed commit.** §13 says the repository was archived before submission. The only recorded archive visit is 21 Aug, which is before rules X1 and X2 existed.
4. **Send the author query** (`docs/presubmission/AUTHOR_QUERY_ALIGNMENT.md`) if it hasn't gone.
5. **Upload `PAPER.pdf` and `supplementary_anon.zip`.** Check both against the SHA-256s in the refreshed `docs/SUBMISSION_PACKAGE.md` first. Don't rebuild before uploading: every build re-stamps the PDF's date, which changes its checksum.

Steps 1–3 push or publish something. Nothing may be pushed once the paper is under double-blind review, so finish steps 1–4 before step 5.

---

## 1. Rules for every session (read in full each time)

### 1.1 Scope
- Do only your own session's items. Log anything else as one line with file:line in `docs/presubmission/round3/OUT_OF_SCOPE.md`, and do not fix it.
- Do not start the next session's work.

### 1.2 Integrity (non-negotiable)
1. **No hand-typed numbers.** Every measured number in the paper is a `{{key}}` from `scripts/paper_numbers.py` (FILE_MAP §2), read from an artifact under `results/`.
   - Model cards and READMEs follow the same rule through their builders.
   - Annex 3's draft text shows numbers as the 4 Oct PDF prints them. Bind each one: reuse the existing key (grep `results/paper_numbers.json` for the value), or add a new key from the artifact named.
2. **Edit sources, never outputs.**
   - Paper and docs: `PAPER.template.md`, `README.template.md`, `docs/*.template.md`.
   - Generated text: the generator scripts, for example `evidence_summary.py`, `build_paper.py` captions, `build_model_card.py`, `appendix_g_rules.py` and `paper_figures.py`.
3. **The ledger (`FINDINGS_LEDGER.md`) is append-only.**
   - New IDs come from `scripts/ledger_check.py`.
   - A correction is a new entry that names the entry it corrects.
   - The one sanctioned in-place edit is a rule's `Status` line at its discharge.
4. **Pre-register before data.** A rule that governs new data (X2, the only one this round) is committed and pushed before that data exists, with a commit subject starting `PRE-REGISTER`. Its reading script is committed with it.
   - Analysis that is not pre-registered is labelled **post hoc** in its ledger entry and in the paper.
   - Post hoc work never re-opens a discharged rule (M-23, M-64, M-74, M-75, M-76, M-80, …) and never changes a verdict.
5. **Verify against source, not config.**
   - Every new analysis script asserts that it reproduces an existing artifact on the cases they share before it produces anything new. Each item names its assertion.
   - A claim about another paper's method is checked against that paper's text.
6. **Citations** are added only through `scripts/t1_bibliography.py`.
7. **Anonymity.** The deny-list scan passes for the paper and both bundles. `docs/presubmission/` is excluded from both bundles by `EXCLUDE_DIRS`. `round3/` sits inside it; R0 confirms it is excluded.
8. **Never loosen a failing check.**
   - Fix the cause, or report the failure.
   - A check may be re-anchored when its text legitimately moves. Log every re-anchor as old anchor → new anchor.
   - Never retire a numeric assertion.
9. **Move, never delete.**
   - Text leaving the main text goes to an appendix. Drafting history goes to `docs/BUILD_CHECKS.template.md`'s "Moved from the paper body" list instead.
   - No result, number, verdict, table or figure may disappear from the paper and its appendices together.
10. **Summaries are checked against every reading (new this round).** A sentence in the abstract, the contributions, Appendix D, §9, §11 or §12 that restates a result may claim a direction only if every reading the body reports for that result agrees: every arena, every horizon and both metrics, where the body reports them. If the readings split, the summary says so ("the readings split", "on some readings", "depends on …").
    - Round 2's Annex 3 broke this rule by choosing the abstract's equal-compute variant from one held-out reading.
    - Never select summary wording from a subset of readings.

### 1.3 Tokens and context
- **Start by reading only:** §1, your own section, the last `SESSION_LOG.md` entry, and the annexes your section names.
- **FILE_MAP** (`docs/presubmission/FILE_MAP.md`): grep it for the rows you need. Never read it whole.
- **Never read whole:** `FINDINGS_LEDGER.md` (over 570 KB), `PAPER.template.md`, `paper_numbers.py`, `paper_numbers.json`. Use `grep -n`, then Read with `offset`/`limit`.
- Never print a whole JSON artifact; extract fields with `python -c` or `jq`.
- Send long output to a log file and show `tail -n 40`.
- **Subagents:** at most 2 per session, Explore type, read-only.
  - The launch command's `CLAUDE_CODE_SUBAGENT_MODEL` makes them Sonnet 5.5, so do not pass a `model` argument.
  - Ask for file:line hits and a conclusion of at most 300 words.
  - Never delegate edits.
- **Checkpoint.** If the conversation has been compacted once, or feels heavy: finish the current item, commit, write a `PARTIAL` entry naming the exact next step, and stop.

### 1.4 Protocol
- **Start gate.** The last log entry must be the previous session with `status: COMPLETE`, or this session with `PARTIAL` or `BLOCKED`.
- **Branch and commits.** Branch `presubmission3` (R0 creates it). One commit per item, subject `[RX][item] summary`. Push at the end of every session.
- **End of every session that edits text:**
  1. Run FILE_MAP §3's fast build, then the gates, then the fast build again.
  2. The second build must be byte-identical to the first.
  3. Append the log entry, commit, push.
- **Log entry template:**

```
## RX — YYYY-MM-DD HH:MM — <model, effort> — status: COMPLETE | PARTIAL | BLOCKED
Commits: <hash> <subject>, one per line
Done: …
Build/gates: pass | fail (<which>)
Paper numbers changed: none | <key: old → new, artifact>
New keys: none | <key, artifact>
Re-anchored checks: none | <check: old → new>
CPU jobs over 1 min: none | <what, how long>
Body words (round2/t6_words.py): <n> (R0: <n>)
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
- Builds and scripts up to about 10 CPU-minutes each. Log any job over 1 minute.
- Keep the Mac on mains power. Run R1's job and the clean clones under `caffeinate -i`.

---

## 2. Sessions

### R0 — Orientation (Sonnet 5.5)
Reads: §0.2, §1.

1. **Working tree.**
   - Check `git status`. Expected untracked paths are `docs/presubmission/round3/PLAN.md` and the four reports round 2's final report names as neither committed nor gitignored; list them in `BASELINE_R0.md`.
   - Record any other untracked or modified path. Stop with `BLOCKED` if one is a source (a template, `scripts/`, `src/`, `results/`, `reproduce.sh`) or `FINDINGS_LEDGER.md`.
   - HEAD must be `8c2c903` on `presubmission2`, or a descendant that adds only round-2 records. Otherwise, stop with `BLOCKED`.
   - Tag HEAD `pre-round3`, create branch `presubmission3` from it, and commit this plan.
2. **Round-3 files.** Create `SESSION_LOG.md`, `DECISIONS.md` and `OUT_OF_SCOPE.md` in `docs/presubmission/round3/`.
   - `DECISIONS.md` gets §0.2's table, with the note "defaults accepted by launching R0, 2026-MM-DD" or the user's edits.
3. **Bundle exclusion.** Dry-run the collection function of both bundle builders and assert that nothing under `docs/presubmission/round3/` is collected.
4. **Baselines, in `round3/BASELINE_R0.md`:**
   - main-text words by `docs/presubmission/round2/t6_words.py`, to "Data and code" and to "References", in total and per `##`/`###` section;
   - page count;
   - the abstract's word and numeral counts as `submission_check` C12.1 counts them, with the caps it applies;
   - pass/fail for every gate after one fast build.
5. **Preflight checks, in `round3/PREFLIGHT.md`.** Record each as pass/fail; any fail means `BLOCKED`.
   - **P1. Weights for X2.** These must all exist:
     - the released checkpoint (`setup.sh` fetches it);
     - `runs/armA_seed{0,1,2}_10k/weights_{2500,10000}.pt`;
     - Arm B's matching 10k-run checkpoints (find their paths from `results/task_d1_threeseed.json`; record them).
   - **P2. The action-timing figures.** From `results/alignment_by_horizon.json`, record:
     - the released checkpoint's % change (relative-L1 and nRMSE, each with its interval) at every horizon, in both arenas (`held_out_n4`, `all_ten_n20`);
     - Arm A's per-seed and three-seed values at 2,500 and 10,000.

     Compare them with Annex 2 E2's table.
   - **P3. The equal-compute readings.** From `results/mn_compute_matched.json` `part3_readings`, record all 12 config × centre-iteration rows (four cells each) and the compute ratios. Compare them with Annex 2 E1's table.
   - **P4. The changed nRMSE readings.** In `results/pooled_nrmse_alongside.json`, `readings_whose_result_changed` must be exactly `["M-75 in_sample|nrmse_h1", "M-76 in_sample|nrmse_h100"]`. Record:
     - each baseline's D and interval, committed and pooled;
     - the sign convention of D, as `scripts/verdict_baselines.py` defines it (file:line).
   - **P5. The original's printed training hours.** ORIGINAL_SPECS a.5 lists them. Record whether any `results/` artifact holds them, and which one, or "none".
   - **P6. Rules and labels.** Record:
     - the number of rules in `results/appendix_g_rules.json`;
     - the number Figure 1 plots, and the file:line of its generator;
     - the file:line that builds the anonymous commit labels (`C016` and the rest);
     - which rules have "—" in Appendix E's commit column, and why.
   - **P7. Action pairing in code.** Record the file:line where `scripts/alignment_by_horizon.py` applies `action_offset`, for the released checkpoint and for Arm A. Record whether the sweep evaluator's in-sample arena builder (`scripts/mn_sweep_eval.py`) can be imported.

### R1 — Rule X2: do our models respond to the action? (Opus 5.5, high)
Reads: §1, R1, Annex 1, and `round3/PREFLIGHT.md` (P1, P2, P7).

1. **Write `scripts/action_sensitivity.py`** to Annex 1, with its reading function and both assertions.
   - Import rollouts, arenas and interval functions from `alignment_by_horizon.py`, `alignment_defect_ci.py` and `mn_sweep_eval.py`. Never copy them.
2. **Pre-register.** Append a ledger entry with the next free M-ID and status `PRE-REGISTERED`, containing:
   - Annex 1's question, models, arenas, interventions, measures and reading, verbatim in substance;
   - the motivation, labelled as known before the rule: N1's post hoc finding that Arm A's error changes by under 1% with the stale action;
   - the scope note: exploratory; never re-opens M-23, M-64 or M-74–M-76;
   - the script's path and SHA-256.

   Commit with subject `PRE-REGISTER action-sensitivity rule X2, before its readings exist`, and push. Only then run anything that produces a new reading.
3. **Run it** under `caffeinate -i` to `results/action_sensitivity.json`, with a log.
   - The assertions run first; if either fails, stop with `BLOCKED` and do not compute readings.
   - Project the total time after the first model. If the projection exceeds 30 CPU-minutes, stop with `BLOCKED`.
4. **Discharge.**
   - Append a ledger entry with each Arm A checkpoint's reading exactly as the script returns it, plus the alongside values (released checkpoint, Arm B), with no prose interpretation.
   - Update the rule's `Status` line, which is the sanctioned in-place edit.
5. **No paper edits.** Run the fast build and gates anyway.
   - Appendix E's rule count should rise by one through its generator. If the fast build does not regenerate `results/appendix_g_rules.json`, run its script (grep FILE_MAP for it).
   - Record the old and new count, and X2's computed lead time.

Done when the script, the artifact and two ledger entries are committed and pushed.

### R2 — The configuration claim, the nRMSE note, the RSSM clause (Opus 5.5, high)
Reads: §1, R2, Annex 2 (E1, E4, E5), Annex 3 (A1–A6, including A5b), and `round3/PREFLIGHT.md` (P3–P5).

1. **E1, the configuration claim at equal compute**, per Annex 2. This includes:
   - the generated Appendix U table;
   - the original's printed hours, bound (add them to an artifact first if P5 found none);
   - the §5.2 heading and both paragraphs;
   - the Limits clause.
2. **Restatements of E1.**
   - Install Annex 3's configuration sentence in the abstract (ruling V3), the configuration half of contribution 3, Appendix D's configuration row and §12's sentence.
   - Grep `README.template.md`, `build_model_card.py`, `docs/COVER_STATEMENT*.md` and `docs/*.template.md` for "twice as long", "equal compute", "trains longer" and "even when", and fix each occurrence the same way.
3. **E4, the nRMSE note**, moved to §5.3 per Annex 2.
4. **E5, the RSSM clause** (ruling V9).
5. **Guard G1.** Register it in `check_comparative_claims.py`, with its self-test corruption branch:
   - no file the build renders may contain "trains twice as long", or "even when" followed within 12 words by "centre" or "setting";
   - any front-matter sentence (abstract, contributions, Appendix D, §12) that names compute ("compute", "trained longer", "trains longer") must also contain "depends", "changes", "some reading", "at least one reading" or "split".
   - If the first pattern hits a sentence that is not about the configuration claim, narrow the pattern and log the narrowing. Never exempt a configuration sentence.
6. **Rule 10 audit for this session's claims.** For every sentence you installed, list in the log the readings it summarises and confirm that each agrees with it.

### R3 — Action timing, X2, the abstract and contribution 7 (Opus 5.5, high)
Reads: §1, R3, Annex 2 (E2, E3), Annex 3 (A7–A13), the fields of `results/action_sensitivity.json` and `results/alignment_by_horizon.json` (never the whole files), and `round3/PREFLIGHT.md` (P2).

1. **E2, action timing described on all ten episodes**, per Annex 2. The places it touches:
   - contribution 7;
   - §3.1's "Which metric each headline uses";
   - the §3.2 row's claim text, arena and verdict (in `evidence_summary.py`);
   - §7.2's second paragraph.
2. **E3, X2 into the paper**, per Annex 2 and the variant X2's reading selects. The places it touches:
   - Appendix V;
   - §7.2's sensitivity sentence;
   - §5's Limits;
   - §11;
   - §9 (only if the reading calls for it);
   - the model card, through `build_model_card.py`;
   - README, if it says anything about our checkpoints' use for control.
3. **The abstract.**
   - Install the action-timing clause (ruling V4) and, if X2's reading calls for it, the X2 clause (ruling V2).
   - Fix the precision of the pair of correlations (S15, Annex 3 A13).
   - Install the configuration sentence if R2 did not.
   - C12.1 must pass. Aim for 340 words or fewer, reached by trimming wording, never findings. If the numeral cap fails, drop digits from the two new clauses first.
4. **Guards G2 and G3** in `check_comparative_claims.py`, each with a self-test branch:
   - **G2:** any sentence that names the action-timing defect ("stale", "misaligned", "previous step's action" or "alignment") and also says "short horizon(s)", "up to" or "h = 1" must carry an all-ten-episodes key, or the words "all ten episodes", in the same paragraph;
   - **G3:** any sentence that cites Arm A's stale-pairing sensitivity (`stale_armA_*`) must carry an X2 key in the same paragraph.
5. **Rule 10 audit**, as in R2.

### R4 — Small items (Opus 5.5, default)
Reads: §1, R4, the anchors below, and `round3/PREFLIGHT.md` (P6).

Each item is 3 sentences or fewer of change. The anchors are phrases from the 4 Oct PDF; grep loosely, because dashes, quotes and math markup may differ in the source.

- **S1. §3.2's multiplicity column.** The 10,000-iteration A/B row says "yes, at the 500 and 2,500-iteration checkpoints". The row's own checkpoint is 10,000, so make `evidence_summary.py` print what applies to the row (for example "not applicable at 10,000; the 500- and 2,500-iteration cells survive Holm, Appendix L"). Check every other row's column against its checkpoint the same way.
- **S2. Explain "SURVIVES entry-res ONLY" outside §6.6 and Appendices E and K.** The verdict stays verbatim. At its first appearance in each other place (the §3.2 row, §12, and the appendices that repeat it), add a short gloss in parentheses: disagreement beats the one-step error before the window, but not the model's predicted step size.
- **S3. Figure 1** (ruling V6). Regenerate it over every rule in `appendix_g_rules.json`, including X2, with the caption "for every pre-registered rule (Appendix E)".
  - Rewrite §8's "Figure 1 gives the lead time for 8 of them and Appendix E for all 22; 7 of Figure 1's are positive and 1 is not" from generated keys.
  - Recompute §13's "14 of the commits Figure 1 cites keep their identifiers and two do not" for the new set, with the same method round 1 used (find it in BUILD_CHECKS or the ledger), and bind it.
  - View the PNG before and after.
- **S4. Introduction.** "one returned "cannot be settled", and we report it" understates the negative verdicts. Replace it with: several returned verdicts against the original or could not settle the question, and we report each (Appendix E).
- **S5. "commit C016"** in §5. At the first use of a commit label anywhere in the main text, add "(an anonymised commit label; §13)".
- **S6. Appendix E's commit column** shows "—" for M-49 onward (P6).
  - Fill every rule's label from the same label map, extending the map in time order if it predates those commits.
  - If there is a deliberate reason for "—", state it in the caption instead.
  - Labels stay anonymous.
- **S7. Appendix F** says the same thing twice: the paragraph starting "So the finding is not that the release is internally inconsistent" and the one starting "§7.5's argument in full". Merge them into one paragraph.
- **S8. Two bibliography notes.**
  - §2's paragraph "Every entry cited here and in §5.3 was checked …" and the References note "Entries 3–20 are …" say the same thing. Keep one, in the References note, reduced to what was checked and the counts (ledger D-35).
  - Move "a hand-maintained list of what a paper cites drifts … and this one had: six entries …" and §2's paragraph to BUILD_CHECKS' moved list.
- **S9. Appendix E's M-69 note** ("M-69's discharge commit was amended …"). Reduce it to two sentences: the two timestamps, and that both are positive.
- **S10. §5.1:** "less one per episode boundary (8 of them)" is wrong, because 8 episodes have 7 internal boundaries. Change it to "less one per episode (8 of them), since an episode's first row has no predecessor".
- **S11. §3:** "Every long-horizon verdict in this paper survives a bootstrap over independent trajectories" → "is computed with a bootstrap over independent trajectories". Several verdicts are "not resolved".
- **S12. §5's by-horizon table** has opposite conventions: "A vs floor" is floor ÷ A, while "B vs floor" is B ÷ floor.
  - Make both columns error ÷ floor, with "below 1 beats the floor" in the caption, through new keys.
  - Prose that says "beats it by 2.8×" may stay, provided its key is still bound.
- **S13. M-64's units.** Where the text says "on M-64's shorter units" for horizons beyond 1, say that a unit is 32 + h rows. Bind the unit counts (from `results/m64_short_units.json` `index`: 60 at h = 1, 50 at h = 8, …).
- **S14. 13 or 10 repositories.**
  - §2 and Appendix I say "Of 10 public repositories examined", but Appendix I also reports "a further 3 repositories" without the construction, and `q1_pets_descendants.json` counts both.
  - Say that 13 were examined, 10 carry the construction, and 1 of those 10 trains it against a sampled squared error. Bind each count.
  - Adjust "it stopped at 10" to match.
- **S15.** Done in R3 (the abstract's precision). Here, check that contribution 1 pairs +0.6053 with +0.4697 at the same precision.
- **S16. Orphaned line in §6.5.** The bold line "The failure is specifically magnitude calibration, in both components." sits alone before "The structural excuse does not survive." Fold it into the preceding "So this section's claim is:" paragraph.
- **S17. Literal markup in the PDF.** In §6.6 and its table, "‖µ_t − µ_{t−1}‖" prints the braces "µ_{t−1}" literally. Fix the template's math markup so it renders, and confirm in the PDF with `pdf_render_check.py`.

### R5 — Pipeline hygiene (Sonnet 5.5)
Reads: §1, R5, and round 2's `OUT_OF_SCOPE.md` and `FINAL_REPORT.md` "Open items".

- **H1. Training scripts report failure** (ruling V10).
  - `run_10k_d1.sh`, `run_indep_ens.sh`, `run_m49_matched.sh`, `run_nll.sh` and `run_nll_indep_ens.sh` must exit with training's status, not an unconditional `exit 0`.
  - `run_nll.sh` gets the existence check the others have.
  - Test without training: run each with its Python replaced by a stub that exits 1, and assert that the script exits non-zero.
  - Update `reproduce.sh`'s comment to match.
- **H2. Stale prose in an artifact.** `results/a1_ab_by_horizon.json`'s `trend.reading` contradicts the table.
  - Make its script compute that sentence from the table, and regenerate.
  - Assert that every numeric field is unchanged to 1e-12. If any changed, stop with `BLOCKED`.
- **H3. Ledger corrections**, each a new entry naming the one it corrects.
  - **C-13:** the 2,500 iterations are in Table S9 ("RWM training parameters"), not Table S7 (`docs/presubmission/sources/2501.10100v1.txt:818-827`).
  - **D-12:** its range 0.601–1.674 comes from `step3_report.txt` under Step 3's protocol, while the paper's 0.562–1.591 comes from `results/a2_trajectory_level_control.json`. Read both scripts, state each definition, and say which the paper uses.
- **H4. Appendix B's runtime table** omits rule X1's two Part C runs. Add them through the table's generator.
- **H5. `reproduce.sh` wiring.**
  - Add `--quick` stages with a `NEEDS_WEIGHTS` guard for `action_sensitivity.py`, and for R2's equal-compute table generator if it is a separate script.
  - Target: `pipeline_coverage` lists 0 uncovered artifacts, and stage 20n8 lists 0 unclassified discoveries.
- **H6. Round 2's open items.**
  - The supplementary manifest's two off-by-one counts.
  - The four reports `reproduce.sh` writes that are neither committed nor gitignored: gitignore them if nothing under `results/` or `paper_numbers.py` reads them, otherwise commit them through their stage.
  - Record what you did for each.
- **H7. Bundle self-test** at the current HEAD (`make_anon_bundle.py`). It must still detect its planted full hash.

### R6 — Length and front-matter consistency (Opus 5.5, default)
Reads: §1, R6, `round3/BASELINE_R0.md`, and Annex 4 items 1–3, 7 and 8.

1. **§3.2's table into Appendix D** (ruling V5).
   - Move it as Appendix D's second table, "What each tested claim rests on", generated as before.
   - §3.2 keeps its opening paragraph, ending with a pointer to the table.
   - Re-anchor every check that pointed into the table, and log each one.
   - Run `xref_sweep.py`; it must report 0 suspect pointers.
2. **Measure** with `round2/t6_words.py`. If the main text is above 20,771 words (ruling V8), move more, in this order, each leaving at most two sentences and a pointer:
   1. §5.3's X1 Part B numbers (the prior/posterior ratios and nats), to Appendix L or the X1 table's appendix;
   2. §5's floor paragraph detail on M-64's 33-row units, to Appendix L;
   3. §7.4's remaining detail, to Appendix Q.

   Stop at 20,000 or when the list runs out, and report the count.
3. **Front-matter consistency** (rule 10).
   - For every sentence in the abstract, the contributions, Appendix D's two tables, §9, §11 and §12 that restates a result, find the body sentence it restates.
   - Confirm that the restatement has the same arena, sample size, horizon, metric and direction, and is no stronger than the body.
   - Write `round3/CONSISTENCY.md`, one row per sentence: sentence | body anchor | readings | agrees?
   - Fix wording only.
4. **Budgets.** The abstract passes C12.1. The contributions are at most 8 bullets of at most 3 sentences each.

### R7 — Fresh-eyes review (Opus 5.5, high; new terminal)
Reads: §1, R7, Annex 4. Do not read earlier sessions' logs beyond the last entry: the point is fresh eyes.

1. **Read the main text in full, once.**
   - Build, then `pdftotext -layout -f 1 -l <page before References> PAPER.pdf round3/body.txt`.
   - Read it in chunks of about 300 lines.
   - Round 2's review missed a front-matter overstatement that only a whole read catches. Look specifically for any summary that is stronger than its section.
2. **Two Sonnet Explore agents**, read-only.
   - Agent 1 takes Appendices A–L. Agent 2 takes Appendices M–V.
   - Each reads every table and every sentence that cites it, and returns only mismatches: numbers, arenas, n, checkpoints, verdict strings, and pointers.
3. **Write `round3/REVIEW.md`:** pass/fail for every item of Annex 4's checklist, each with file:line, and every finding from step 1 or step 2.
4. **Verify every finding yourself** before acting on it.
5. **Fix only small items** (3 sentences or fewer each). Anything larger means stop with `BLOCKED` and the list.

### R8 — Freeze, restatement, bundles, package (Opus 5.5, default)
Reads: §1, R8; round 2's `SESSION_LOG.md` "## T11" entry and round 1's "## S10-fix" entry (the B3 recipe).

1. **Freeze.** From here there are no prose edits except §8's reproduction figures and the documents in step 5.
2. **Regenerate the claims audit** (round 2's ruling U5 still stands: regenerate, do not review), then run the fast build and gates. Commit and push.
3. **Measure and restate, following round 1's B3 recipe:**
   - Clone the pushed HEAD into `/Users/Shared/rwm_verify/r3/M1/`, create a fresh venv from `requirements.txt`, and run `reproduce.sh --quick --force`. Evidence goes to `/Users/Shared/rwm_verify/evidence/R3R8/`.
   - Run the verifier three times; the runs must be byte-identical, with 0 scientific differing values.
   - Restate §8's reproduction figures (`ver_*` keys) from that measurement.
   - Refresh the hand-written copies with `docs/presubmission/s10fix_docs.py`.
   - Simulate a clean clone of the restated tree and predict that all reproduction keys match. Then push.
4. **Bundles.** Rebuild both bundles on the restated HEAD. The builder scan and the independent deny-list sweep must both find 0 hits in both zips and the PDF.
5. **Package documents.**
   - `docs/SUBMISSION_CHECKLIST.md`: refresh its known-items section, including round 2's stale figure-overlap lines (round 2 OUT_OF_SCOPE, T8).
   - `docs/SUBMISSION_PACKAGE.md`, in full: file sizes and SHA-256s of `PAPER.pdf` and `supplementary_anon.zip`, the abstract, the counts and the title.
   - `docs/COVER_STATEMENT.md`: rule count, page count and retraction counts.
   - Remove a "pre-edit" banner only when every item is current.

### R9 — Clean-clone verification (Sonnet 5.5) — last; no edits
1. **Clone.** Clone the pushed `presubmission3` HEAD into a fresh directory with a fresh venv, using round 2's driver (`/Users/Shared/rwm_verify/evidence/R2T12/t12_driver.zsh`) copied and adapted to `/Users/Shared/rwm_verify/evidence/R3R9/`.
2. **Run, in order:**
   1. `./setup.sh`;
   2. `./reproduce.sh --quick --force`;
   3. the verifier three times against a pristine reference;
   4. the full paper build and every gate;
   5. both bundles and the independent deny-list sweep;
   6. the PDF comparison.
3. **Criteria:**
   - scientific differing values = **0**;
   - `part_f_gate` fails exactly as §8 publishes it;
   - every reproduction figure the paper prints equals what the clone measures;
   - the PDF equals the committed one after blanking dates and ID;
   - 0 deny-list hits in the rebuilt and the committed upload files;
   - `submission_check` returns what `SUBMISSION_CHECKLIST.md` records;
   - X2's `--quick` stage runs or skips as designed.
4. **Write `round3/FINAL_REPORT.md`:** pages, main-text words and every gate against R0, and the upload files' SHA-256s.
5. **On any failure:** no fixes. Stop with `BLOCKED` and the logs; the user runs "R8-fix" on Opus, then R9 again.
6. **Log entry:** list §0.4's five user steps as reminders.

---

## Annex 1 — Rule X2: do our models respond to the action? (PRE-REGISTERED in R1; exploratory; never re-opens M-23, M-64 or M-74–M-76)

**Question.** Do our trained models condition their forecasts on the action they are given?

**Why it matters.**
- N1 (post hoc, `alignment_by_horizon.json`) found that the released checkpoint's error at h = 1 rises by 34.2% [10.6, 75.0] on the held-out pair when it is fed the action one step stale, and by 55.0% [26.3, 92.7] over all ten episodes.
- Our Arm A at 10,000 iterations, trained under the same causal pairing, changes by −0.22% at h = 1 and +0.15% at h = 368.
- Either consecutive actions are nearly equal, or our models barely use the action. A world model that does not respond to actions cannot serve policy optimisation, which is what RWM is for.
- That observation is known before this rule. X2's readings are new.

**Script:** `scripts/action_sensitivity.py` → `results/action_sensitivity.json`.

**Models** (all inference, existing weights):
- **Arm A**, seeds 0–2, at 2,500 and at 10,000 iterations (the 10k runs' checkpoints; the 2,500 one replicates the sweep centre bitwise, per N3). This model gets the **readings**.
- **Arm B**, seeds 0–2, at 2,500 and 10,000. Reported alongside only.
- **The released checkpoint**, with `action_offset = 1`. Reported alongside only.

**Arenas.**
- For Arm A and Arm B:
  - the sweep evaluator's **in-sample arena**: 16 independent 400-step trajectories, built with `mn_sweep_eval.py`'s own builder;
  - the **held-out pair**: 4 trajectories.
- For the released checkpoint:
  - **all ten episodes**: 20 trajectories;
  - the **held-out pair**.
- Horizons {1, 8, 32, 100}, cumulative over steps 1..h, relative-L1 as in §3.1.

**Interventions.** Only the forecast-step actions change; the history window is untouched, so the recurrent state at the forecast's start is identical across interventions.
- The hook transforms the action array passed to `model.rollout(st, ac, E.START_STEP, action_offset=…)` (`alignment_defect_ci.rollout`).
- Read `src/rwm_model.py`'s `rollout` to find which rows of `ac` the forecast steps read under offset 1, and transform only those. Record that file:line in the artifact.
- **I0 true:** offset 1, the reference.
- **I1 stale:** offset 0, N1's.
- **I2 swap:** each trajectory takes the actions of the next trajectory in the arena's order (i → i+1 mod n) at the same forecast positions.
- **I3 mean:** each action dimension is replaced by its mean over the model's own training rows (the eight training episodes for Arm A and B; all ten for the released checkpoint).
- **I4 noise:** true + ε, with ε ~ N(0, (k·σ_a)²) per dimension, k ∈ {0.1, 0.5}. σ_a is that dimension's training standard deviation. Use 8 draws with generator seed 0, averaged inside each trajectory.

**Measures**, per model × checkpoint × arena × horizon × intervention:
- **E** = err(I)/err(I0) − 1, computed per model as round 2's N1 computes its overstatement (`alignment_defect_ci.arena`, with I in place of offset 0).
  - For Arm A and Arm B, E is the mean over the three seeds of each seed's E, as N1's `three_seed_mean_overstatement_pct` is.
  - Its interval resamples whole trajectories, with the same resample applied to all three seeds and both interventions inside each draw. The draws are exact over all 256 at n = 4, and 20,000 Monte Carlo draws (seed 0) at n = 16 and n = 20, as N1 does.
- **Δ** (descriptive): the relative-L1 of the intervened forecast measured against the I0 forecast, using `src/rwm_metrics.py`'s relative-L1 with the I0 forecast as target. It is 0 for a model that ignores the action.
- **Context** (descriptive), over the forecast steps of each arena:
  - the fraction of steps with a_t ≠ a_{t−1};
  - mean |a_t − a_{t−1}| ÷ mean |a_t − ā|, which is how large a one-step shift is relative to the action's spread;
  - the same ratio for the swap.

**Assertions, before any new reading:**
- **(a)** I0 and I1 reproduce `alignment_by_horizon.json`: the released checkpoint to 1e-9, and Arm A to 1e-6 at every shared arena and horizon. On the in-sample arena, I0 also reproduces `mn_compute_matched.json` `three_seed_mean_l1.in_sample` at 2,500 and 10,000, h ∈ {1, 8, 32, 100}, to 1e-6.
- **(b)** The offset is actually applied. Under I1, for every model and every window:
  - the action tensor fed to the model differs from I0's on at least one forecast step;
  - the forecast differs (max |difference| > 0).

  Record the fraction of steps whose input differs. If (b) fails for any model, stop with `BLOCKED`: §7.2's sensitivity sentence would rest on an offset that was never applied.

**Reading.** There is one reading for Arm A at 2,500 and one for Arm A at 10,000. It uses E under I2 (swap), at h = 8, on the in-sample arena (n = 16), three-seed mean. The first matching outcome applies:
1. **RESPONDS TO THE ACTION:** the interval's lower bound > 0 and the point estimate ≥ +10%.
2. **ERROR FALLS WITH WRONG ACTIONS:** the interval's upper bound < 0.
3. **DOES NOT RESPOND MEASURABLY:** the interval's upper bound < +10%.
4. **UNRESOLVED:** otherwise.

**Why these choices.**
- **h = 8:** it is the training forecast length. It is long enough for an action's effect to reach the state, and short enough that open-loop drift does not dominate.
- **The in-sample arena:** whether a model uses its input is a property of the model, not of generalisation, and 16 units give a usable interval.
- **The swap:** it is a realistic action sequence that is wrong for that state.
- **10%:** it is a deliberately low bar, because the one-step-stale action alone raises the released checkpoint's error at h = 8 by 54.4% over all ten episodes.

Arm B and the released checkpoint get the same statistic and the label it would carry, marked "alongside, not a reading".

**Cap:** 30 projected CPU-minutes.

**Reported in:**
- a new Appendix V table: E, with intervals, for I1–I4 at the four horizons, per model and checkpoint, plus Δ and the context figures;
- §7.2, §5's Limits and §11, and §9 and the abstract per ruling V2 (Annex 3, A9–A12).

---

## Annex 2 — What each paper edit must achieve

### E1 — The configuration claim at equal compute (R2)

**The evidence**, from `mn_compute_matched.json`. D = err(config at 2,500) − err(centre at k); negative favours the configuration; 95% intervals. The compute ratio is the centre's total compute ÷ the configuration's.

| config (cost per iteration ÷ centre's) | centre trained to | compute ratio | h=100 held-out (4) | h=100 in-sample (16) | h=368 held-out (4) | h=368 in-sample (16) |
|---|---|---|---|---|---|---|
| (32, 32) (1.81) | 5,000 | 1.11 | −0.0918 [−0.1901, +0.0065] | **+0.0454** [+0.0356, +0.0563] | **−0.2031** [−0.5033, −0.0275] | +0.0084 [−0.0006, +0.0161] |
| (32, 32) | 10,000 | 2.21 | −0.0352 [−0.1142, +0.0438] | **+0.0920** [+0.0770, +0.1068] | −0.0594 [−0.1903, +0.0340] | **+0.0560** [+0.0483, +0.0639] |
| (32, 16) (1.35) | 5,000 | 1.48 | −0.0723 [−0.1466, +0.0020] | **+0.0400** [+0.0326, +0.0481] | **−0.1671** [−0.4301, −0.0117] | **+0.0142** [+0.0068, +0.0205] |
| (8, 8) (0.40) | 2,500 | 2.50 | **−0.0755** | **−0.0142** | **−0.1004** | **−0.0208** |
| (8, 8) | 10,000 | 9.98 | +0.0343 [−0.0198, +0.0719] | **+0.1162** | **+0.1270** [+0.0987, +0.1589] | **+0.1414** |
| (2, 8) (0.26) | 2,500 | 3.78 | **−0.1274** | **−0.0219** | **−0.1139** | **−0.0219** |
| (2, 8) | 10,000 | 15.1 | −0.0176 | **+0.1085** | **+0.1135** [+0.0983, +0.1357] | **+0.1403** |

Bold means the interval excludes zero. Read from it:
- **The shorter histories win on all four readings** at 2,500 iterations, while costing 0.40× and 0.26× per iteration. That part of the verdict needs no compute correction.
- **The longer forecasts' wins are compute-confounded.** At about equal compute (centre at 5,000 = 1.11× (32, 32)'s compute), the four readings split: (32, 32) is ahead on one (held-out, h = 368), the centre is ahead on one (in-sample, h = 100), and two are not resolved. At 2.21×, the centre is ahead on both in-sample readings, and the held-out ones are not resolved.
- **Trained four times as long, the centre passes both shorter histories** on three of four readings, with 10× and 15× their compute.
- **So which setting is most accurate depends on how long each is trained.** M-74's verdict, NOT OPTIMAL AT OUR BUDGET, is unchanged. It is a statement about the 2,500-iteration budget.

**The original's own figures** (ORIGINAL_SPECS a.5, v1 Fig. 6):
- printed error 0.47 for both (32, 8) and (32, 32);
- training hours 1.07 and 2.27, a ratio of 2.12×.

On its own numbers, the centre matches its best neighbour's error at under half the time. Our measured cost per iteration for the same pair is 1.81×. If P5 found no artifact holding the hours, add them (and the printed error row) to `results/original_paper_figures.json`'s `mn_optimal` entry through its generator, as evidence class EXT with page references, and bind them (suggested keys `orig_e_32_8`, `orig_e_32_32`, `orig_h_32_8`, `orig_h_32_32`, `orig_h_ratio`).

**Edits:**
- **§5.2's claim paragraph:** after "level with its longest-forecast neighbour (…a.5)", add Annex 3 A1.
- **The heading "The history length departs furthest from the original."** and its paragraph → Annex 3 A2.
- **"Accuracy at equal compute (post hoc; ledger R-78)"** → Annex 3 A3. It replaces everything from "At 5,000 iterations the centre has had" to "None of this re-opens rule M-74."
- **New Appendix U, "The settings sweep at equal training compute"**: the table above, generated from `mn_compute_matched.json` (all 12 rows of `part3_readings`, four cells each, with the compute ratio), labelled post hoc. No hand-typed cell.
- **§5.2's Limits:** after "so the ranking is at this budget, not at convergence", add "and it changes with training length (Appendix U)".
- **Restatements:** the abstract (A4), contribution 3's second sentence (A5), Appendix D's configuration row and §12's sentence (A6).
- **Anchors:** "even when that setting trains twice as long"; "even when the centre trains twice as long" (two places); "That is as far as it goes"; "The history length departs furthest from the original"; "which it chose as a trade-off".

### E2 — Action timing described on all ten episodes (R3)

**The evidence**, from `alignment_by_horizon.json`: the released checkpoint's % change in error with the stale action.

| h | all ten episodes (20), relative-L1 | all ten (20), nRMSE | held-out pair (4), relative-L1 | held-out pair (4), nRMSE |
|---|---|---|---|---|
| 1 | +55.0 [26.3, 92.7] | +7.4 [−14.8, 87.8] | +34.2 [10.6, 75.0] | +51.0 [11.8, 88.0] |
| 8 | +54.4 [37.5, 82.3] | +31.5 [24.7, 68.2] | +37.2 [7.9, 95.6] | +59.8 [12.4, 97.8] |
| 32 | +37.4 [21.3, 65.4] | +17.4 [7.7, 47.4] | +47.7 [5.8, 131.8] | +99.6 [11.9, 170.5] |
| 100 | +8.2 [−10.4, 24.9] | +7.9 [−18.9, 32.9] | +22.5 [6.3, 41.7] | +27.6 [7.6, 40.9] |
| 128 | −8.8 [−23.8, 4.9] | −8.3 [−30.3, 5.8] | +20.3 [7.0, 35.7] | +21.6 [5.9, 28.7] |
| 368 | −4.6 [−13.4, 3.2] | −2.1 [−10.0, 3.9] | +7.9 [3.1, 13.0] | +6.6 [1.0, 8.0] |

(`released.summary` in the artifact.)

**Why lead with all ten episodes.** Every arena is training data for this checkpoint, so the held-out pair is not more honest here, only smaller.

On all ten episodes:
- the cost is resolved on relative-L1 up to h = 32;
- on nRMSE it is resolved at h = 8 and 32 but not at h = 1;
- from h = 100 it is not resolved in either metric.

The held-out pair's +22.5% at h = 100 must not stand alone.

**Edits:**
- **Contribution 7:** Annex 3 A7.
- **§3.1, "Which metric each headline uses":** replace from "§7.2's alignment defect is given in both metrics side by side at h = 368" to "at h = 1." with A8.
- **§3.2's alignment row** (`evidence_summary.py`):
  - claim text: "The released evaluation pairs states and actions one step stale (§7.2)". Drop "and overstates its own model's error".
  - arena: "all ten episodes (20)";
  - verdict: "defect confirmed in the code; raises error up to h = 32 on relative-L1; not resolved from h = 100".
- **§7.2's second paragraph:**
  - Lead with the all-ten-episodes curve in both metrics (bind new keys, for example `adh20_rel_h{1,8,32,100,368}` and `adh20_nrmse_h{1,8,32,368}` with their intervals).
  - Then give the held-out pair's figures and per-trajectory values, as now.
  - Replace "and by 22.5% [6.3, 41.7] at h = 100, the method's own horizon" with a sentence that gives it beside the all-ten figure at h = 100 (not resolved).
- **The abstract:** A10 (ruling V4).
- **Anchors:** "inflating error mainly at short horizons"; "the cost is concentrated at short"; "What the stale pairing costs is concentrated at short horizons"; "its larger cost at short horizons is given on relative-L1"; "overstates its own model's error".

### E3 — Rule X2 in the paper (R3)

Install the variant that X2's two readings select (Annex 3 A9–A12). The cases are, for Arm A:
- **D:** DOES NOT RESPOND MEASURABLY at both checkpoints;
- **D-2.5k:** DOES NOT RESPOND MEASURABLY at 2,500 only;
- **R:** RESPONDS TO THE ACTION at both;
- **other:** any other combination.

Every case gets:
- **Appendix V:** the X2 table (Annex 1, "Reported in"), with a caption naming the arena, n, checkpoints, and "alongside, not a reading" for Arm B and the released checkpoint;
- **§7.2:** the sensitivity sentence's continuation (A9);
- **Appendix H:** one row.

Cases D and D-2.5k also get:
- §5's Limits sentence (A11);
- §11's sentence;
- §9's lesson (A12);
- the abstract clause (A10, ruling V2);
- the model card's caveat.

### E4 — The nRMSE note moves to §5.3 (R2)

- **§5.2's table caption.** Replace everything from "and return the same verdict as the averaged ones everywhere except two in-sample readings of §5.3's rules" to "RWM AHEAD OF ALL THREE averaged." with one clause: for this section's rule (M-74), the pooled readings return the same verdicts as the averaged ones (ledger R-77).
- **§5.3.** After the sentence ending "at h = 8 both return …" (the paragraph that begins "Before those horizons, on the held-out pair"), add Annex 3 A5b. It covers:
  - the in-sample pooled-nRMSE readings that differ;
  - the baselines that moved, with their D and intervals, signed as `verdict_baselines.py` signs D (positive favours RWM);
  - the link to §5's one-step lead for teacher forcing.

From P4:
- teacher-forced, h = 1, in-sample, pooled: MLP −0.160 [−0.286, −0.002], RSSM −0.186 [−0.328, −0.013], transformer −0.052 [−0.089, −0.005]. All three are rejected, so DOES NOT REPRODUCE, where the averaged reading said CANNOT BE SETTLED.
- autoregressive, h = 100, in-sample, pooled: MLP +0.017 [−0.017, +0.044], not rejected, so PARTIAL, where the averaged reading said RWM AHEAD OF ALL THREE.

### E5 — The RSSM clause (R2, ruling V9)

In §5.3, the sentence that begins "The failure may still be our RSSM rather than the architecture". After "and X1 tried only the two settings above, on one seed", add: ", neither of them PlaNet's latent overshooting, the multi-step training of the prior that targets open-loop prediction directly".
- Add it only if `t1_bibliography.py` verifies the attributed fragment against PlaNet's text (Hafner et al., ICML 2019, already in the bibliography).
- Otherwise log the reason in OUT_OF_SCOPE and skip it.

---

## Annex 3 — Draft text

R2 and R3 install this text. Bind every number, and tighten wording freely, but never strengthen a claim. The numbers shown are the 4 Oct PDF's, or the artifacts'.

**A1. §5.2 claim paragraph, new sentence.**
> Its second heatmap prints training hours: 1.07 for the centre and 2.27 for (32, 32), 2.12×, so on the original's own figures the centre matches its best neighbour's error in under half the time. Our measured cost per iteration for the same pair is 1.81× (the table's last column).

**A2. §5.2, heading and paragraph.** The heading becomes:
> At our budget, shorter histories win.

Then, in the paragraph after "(ORIGINAL_SPECS.md a.5).", replace "On the governing reading ours does not fall steeply: … no shorter history is resolvably worse, though …" with the same facts plus one closing sentence:
> That is a statement about learning speed at this budget, not about converged accuracy: trained four times as long, the centre passes both winning shorter histories (below), so it does not contradict the original's steep fall to M = 8, whose training budget the original does not state.

**A3. §5.2, "Accuracy at equal compute (post hoc; ledger R-78)."**
> A longer training forecast costs more per iteration, 1.35× the centre's for (32, 16) and 1.81× for (32, 32); the shorter histories that win cost less, 0.40× for (8, 8) and 0.26× for (2, 8) (results/mn_compute_matched.json; Appendix U gives every reading, signed as in the table). The shorter histories win on all four readings at 2,500 iterations while using well under half the centre's computation, so that part of the verdict needs no compute correction. The longer forecasts' wins do. Trained to 5,000 iterations, the centre has had 1.11× the computation of (32, 32), and the readings split: (32, 32) is still ahead on the held-out pair at h = 368 (−0.2031 [−0.5033, −0.0275]), the centre is ahead on the in-sample arena at h = 100 (+0.0454 [+0.0356, +0.0563]), and the other two are not resolved. At 10,000 iterations, 2.21× the computation, the centre is ahead on both in-sample readings and neither held-out difference is resolved. Trained that long, it also passes both shorter histories on the held-out pair at h = 368, (2, 8) by +0.1135 [+0.0983, +0.1357] and (8, 8) by +0.1270 [+0.0987, +0.1589], with 15× and 10× their computation. Which setting is most accurate therefore depends on how long each is trained. None of this re-opens rule M-74.

**A4. The abstract, the configuration sentence** (ruling V3). It replaces "On accuracy alone, two shorter histories … untested here."
> On accuracy alone, two shorter histories and both longer training forecasts beat the original's setting at our budget, but trained longer that setting passes each of them on at least one reading (post hoc), so the ranking depends on the training budget; the original chose its setting as a trade-off with training time, untested here.

**A5. Contribution 3, the configuration half.** It replaces "On accuracy alone, four of the eight … which we do not test (§5.2)."
> On accuracy alone at our budget, four of the eight one-factor neighbours of the original's (M, N) = (32, 8) beat it, two shorter histories at under half its cost per iteration and both longer training forecasts at more, but trained longer the centre passes each of them on at least one reading (post hoc), so the ranking depends on the training budget; the original chose (32, 8) as a trade-off with training time, which its own printed hours are consistent with and we do not test (§5.2).

**A5b. §5.3, the in-sample pooled-nRMSE readings.** Use the signs P4 recorded.
> On the in-sample arena's 16 trajectories, with nRMSE pooled as §3.1 defines it (computed afterwards, post hoc; ledger R-77), two readings differ from the per-trajectory average the rules' evaluator used. Teacher-forced, all three baselines are ahead of RWM one step ahead, the MLP by 0.160 [0.002, 0.286], the RSSM by 0.186 [0.013, 0.328] and the transformer by 0.052 [0.005, 0.089], so M-75's reading there is DOES NOT REPRODUCE: the same one-step lead for teacher forcing as §5's. Trained autoregressively, the MLP's deficit at h = 100 is no longer resolved (0.017 [−0.017, 0.044]), so M-76's reading there is PARTIAL. Neither changes a verdict; both rules govern at h = 368 on relative-L1.

**A6. Appendix D's row and §12.**
- **Appendix D.** Replace "the best of them, at h = 368 on the held-out pair, even when the centre trains twice as long (post hoc, §5.2)" with:
  > the ranking depends on training length: trained longer, the centre passes each of them on at least one reading (post hoc, §5.2, Appendix U)

  Then extend "The trade-off with training time is not tested" with "; the original's printed hours are consistent with it".
- **§12.** After "beat its chosen ones at our budget", add:
  > , a ranking that changes when the chosen setting trains longer,

**A7. Contribution 7.**
> **The released evaluation is misaligned by one step; over all ten episodes it raises the checkpoint's error up to 32 steps ahead, and from 100 steps the change is not resolved.** Evaluation feeds the action from t−1 where training pairs states and actions index-for-index, and shifting its action index by one step fixes it. On all ten episodes' 20 independent trajectories, all of them training data for this checkpoint, the stale action raises its relative-L1 error by 55.0% [26.3, 92.7] at h = 1 and 37.4% [21.3, 65.4] at h = 32, changes it by 8.2% [−10.4, 24.9] at h = 100 and −4.6% [−13.4, 3.2] at h = 368; on the held-out pair's 4 it raises it at every horizon reported, by 7.9% [3.1, 13.0] at h = 368 (§7.2).

On 4 Oct every held-out interval excluded zero, in both metrics (E2's table). If the artifact now says otherwise, name only the horizons where it holds.

**A8. §3.1, "Which metric each headline uses," the alignment sentence.**
> §7.2's alignment defect is given in both metrics, over all ten episodes and on the held-out pair. Over all ten episodes the two metrics agree that the stale action raises error at h = 8 and 32 and that from h = 100 the change is not resolved, and they differ at h = 1, where relative-L1 resolves the rise and nRMSE does not.

**A9. §7.2, continuing the sentence "Our own Arm A checkpoints at 10,000 iterations, … when fed the stale one (…)."**
- **R:**
  > They do respond to the action: given another trajectory's actions, their error at h = 8 rises by {{x2_E_swap_10k}} {{ci}} (rule X2, Appendix V), so their indifference to the one-step shift reflects how little the action changes in one step ({{x2_ctx_stale}} of its spread), not inattention to it.
- **D:**
  > That is not robustness to the misalignment. Given another trajectory's actions entirely, their error at h = 8 on their 16 in-sample trajectories changes by {{x2_E_swap_10k}} {{ci}}, where the released checkpoint's rises by {{x2_E_swap_rel}} on all ten episodes (rule X2, Appendix V): at our budget our models forecast the recorded motion largely without using the action, which a model used for policy optimisation cannot do (§5, §11).
- **D-2.5k:** the D text at 2,500 iterations, plus the 10,000-iteration figure and its reading.
- **Other:** state the readings verbatim with their figures and no interpretation.

**A10. The abstract, the action-timing clause** (ruling V4). It replaces "Separately, the released evaluation pairs … not consistent in sign."
> Separately, the released evaluation pairs each prediction with the previous step's action; across all ten episodes this raises the checkpoint's error at short horizons, and from the method's 100-step horizon the change is not resolved.

**X2's abstract clause** (D and D-2.5k only, ruling V2). Place it after the sentence "These rest on …":
> Our own models barely respond to the actions they are given (rule X2), so the training result concerns forecasting the robot's motion, not its response to commands.

For D-2.5k, say "at the 2,500-iteration budget most comparisons use".

**A11. §5's Limits (D and D-2.5k).**
> Rule X2 finds that our autoregressive checkpoints barely respond to the action they are given (§7.2, Appendix V), so this is a comparison of how well each arm forecasts the recorded motion, not of how well it predicts the consequences of a different action, which the original's use of the model, policy optimisation, needs.

**§11 (D and D-2.5k):** one sentence to the same effect, pointing to §5.

**A12. §9 lesson (D and D-2.5k).**
> Check that a world model responds to its actions before reading its accuracy as fitness for control. Ours, trained on one policy's recorded data, forecast that policy's motion well and barely responded when given another trajectory's actions (rule X2).

**Model card (D and D-2.5k).**
> These checkpoints' forecasts barely change when fed another trajectory's actions (rule X2: error at 8 steps changes by {{…}}). Check action response before using them to evaluate or train a policy.

**Model card (R).** One sentence giving X2's figure.

**A13. The abstract's correlations.** Print the step-size correlation at the precision of the disagreement correlation beside it (+0.605 and +0.470), through a key formatted to 3 decimals.

---

## Annex 4 — The checklist for R7

1. **Configuration.**
   - No rendered file contains "trains twice as long".
   - Every statement of the verdict outside §5.2 carries "at our budget" and either "depends on the training budget" or an equivalent.
   - §5.2's equal-compute paragraph reports all four readings at 5,000 iterations and the 10,000 summary.
   - Appendix U exists, is generated and is labelled post hoc.
   - The original's hours are bound.
   - The §5.2 heading is "At our budget, shorter histories win." (or wording no stronger).
2. **Action timing.**
   - Contribution 7, §3.1, the §3.2 (now Appendix D) row, §7.2 and the abstract describe all ten episodes first.
   - No sentence gives the held-out pair's h = 100 figure without the all-ten figure beside it.
   - The row's claim text no longer says "overstates".
   - G2 passes.
3. **X2.**
   - Pre-registered before its readings: the commit order is checkable in `git log`.
   - The discharge entry is verbatim.
   - Appendix V exists.
   - §7.2's sensitivity sentence carries X2's figure (G3).
   - The variant installed matches the reading.
   - Appendix E and Figure 1 include X2.
   - The model card is updated.
4. **nRMSE.**
   - §5.2's caption has one clause about M-74.
   - §5.3 names the baselines that moved, with signed figures.
5. **Small items.** S1–S17 are done, or logged with a reason.
6. **Round 2 leftovers.** H1–H7 are done; `OUT_OF_SCOPE.md`'s round-2 lines are each closed or carried forward with a reason.
7. **Length.** The main text is at or below 20,771 words, or the shortfall is reported.
   - No result is lost: diff the template's `{{keys}}` against R0's, and justify every removed key in the log.
   - `xref_sweep` finds 0 suspect pointers.
8. **Front matter (rule 10).**
   - `CONSISTENCY.md` has a row for every restating sentence, with every reading listed.
   - The abstract passes C12.1.
   - There are at most 8 bullets of at most 3 sentences.
   - The title, abstract and conclusion agree.
9. **Captions.** Every table and figure caption carries its arena, n_independent and checkpoint, including the moved §3.2 table and Appendices U and V.
10. **Public-facing text.** README, the model card and the cover statement carry no claim stronger than the paper's, and no unbound number.
11. **Anonymity.**
    - §13's paragraph follows ruling V7.
    - Commit labels are anonymous everywhere, including Appendix E's newly filled column.
    - The deny-list scan passes.
