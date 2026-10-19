# Pre-submission plan, round 5 — RWM reproduction, TMLR: applying the 19 October review

This file lives at `docs/presubmission/round5/PLAN.md`. Every session reads §1, its own section in §2,
and only the annexes and files its section names. Find line ranges with
`grep -n '^## \|^### ' docs/presubmission/round5/PLAN.md` and read with offset/limit.

Written on 19 Oct 2026 from:
- the review, kept at `round5/REVIEW_2026-10-19.md`, verbatim but for its byline (only G1 opens it; every
  other session finds the review text it needs quoted in its own section);
- round 4's records: `FINAL_REPORT.md`, `CHECKPOINT.md`, `DECISIONS.md`, `TMLR_CHECK.md`, `OUT_OF_SCOPE.md`,
  the F10–F12 log entries and `PLAN.md` §0–§1;
- the paper at `796a026` (75 pages; main text on pages 1–26; References on page 27; 17,804 body words);
- spot checks of `results/insample_framing.json`, `r2_independent_ensemble.json`, `task_d3_ens5.json`,
  `m65_gaussian_nominal.json`, `x7_loeo_recalibration.json`, `e4_sigma_gradients.json`,
  `q1_pets_descendants.json`, `v3_metric_definitions.json`, the run records' `collapse_fit` field, and the
  arXiv and venue pages of both original papers;
- Claude Code's documentation (models, effort, subagents, CLAUDE.md loading), read on 19 Oct 2026.

Numbers here are for orientation. If an artifact disagrees with this file, the artifact wins; log the difference.

---

## 0. For you (the human)

### 0.1 What this round does

The review judges the paper in scope and unusually careful, but expects "substantial revision", possibly
"reject, resubmit", for two reasons: presentation, which at TMLR is part of the evidence criterion, and five or
six technical points an expert in model-based RL or uncertainty would raise. TMLR's own figures sharpen the
first: about 53% of submissions are now desk-rejected, mostly for claims or evidence that are not clear from
the writing, and since October every submission also gets an AI review of soundness (`round4/TMLR_CHECK.md`,
F11's reading of the 15 Oct post).

This round:
1. **Cuts the paper to what a TMLR reviewer needs.** Main content from 26 pages to at most 12, which puts it
   on TMLR's two-week review track; an abstract of about 200 words with at most five numbers; no internal
   identifiers in the body; each result stated once, with its scope; two significant figures in the body;
   appendices that stand alone; a first figure that shows a finding. Process and audit material leaves the PDF
   for a generated supplementary document inside the anonymised ZIP, and a gate proves that no result leaves
   the record.
2. **Corrects the record where the review is right.** M-65 read the tails backwards (a retraction); the σ
   collapse rate is Adam's step size, not a property of the objective; nRMSE's floor is not 1.0; ranking claims
   need a rank correlation; "too small by" has two meanings; three wordings in §6.3; reference 2; Table S8; and
   what the originals actually say about the aleatoric term and the shared trunk.
3. **Runs the analyses the review asks for, all inference-only.** Each ensemble member rolled out on its own
   predictions (rule X9); in-sample against held-out calibration for the same models (X10); exact tests beside
   every four-trajectory interval; ±2σ coverage and a proper scoring rule under recalibration; the naive floors;
   rank correlations; the released checkpoint's provenance; and the Adam bound (post hoc analyses N7–N14).
4. **If you approve it (ruling Y5), trains ensembles on X3's folds** (rule X11, about 25 CPU-hours in the
   background), so the held-out calibration claims rest on 20 trajectories instead of 4.
5. **Rewrites §5 to lead with X3, and §6 around the review's three gaps**, compresses §5.2, §5.3, §7.4 and
   §7.5, and adds the missing related work.
6. **Freezes, re-measures from a clean clone, packages and verifies**, as rounds 3 and 4 did.

### 0.2 What the review gets wrong or understates (checked on 19 Oct)

G1 re-verifies each of these before anything relies on it.
- **"Versions of record."** Both papers were presented as **workshop posters**: RWM at the NeurIPS 2025 workshop
  *Embodied World Models for Decision Making*, RWM-U at the ICLR 2026 *2nd Workshop on World Models* (the venues'
  own pages). Whether either workshop is archival is not yet known. The current arXiv texts are
  **2501.10100v5 (14 Dec 2025)** and **2504.16680v3 (8 Jan 2026)**; reference 1 describes only v1 and v2. The
  crosswalk is still needed: it is RWM-U's current arXiv abstract that says uncertainty is "effectively
  propagated over long horizons". The paper should call each version what it is.
- **M-65 is worse than the review says.** In its governing row (the released checkpoint's disagreement over all
  ten episodes), ±2σ coverage under M-65's own mean-matching is 93.8%, 88.8% and 84.3% at h = 1, 100 and 368,
  against 95.45%, so the tails are heavy at h = 368 as well, where ±1σ looks Gaussian. M-65's committed branch
  name, OVER-DISPERSED, is itself the heavy-tail signature. M-65 is not edited; a new entry withdraws its reading.
- **The ranking statistic was pre-registered.** M-45, M-51/M-52 and X6 were committed with Pearson, so their
  verdicts cannot move. Spearman and Kendall are added as post hoc companions, which round 4's workplan (§5,
  item 3) had already scoped and not run.
- **The four held-out trajectories come from two episodes.** An exact sign-flip test on four trajectories cannot
  go below two-sided p = 0.125; at the level of episodes, two units, no test is possible (minimum p = 0.5). The
  paper should say both.
- **The Adam point needs one more step.** Every run record already stores `collapse_fit.rate_over_lr` (about
  0.94), uninterpreted. Adam moves a parameter by about the learning rate per step when its gradient keeps one
  sign, but Kingma and Ba's worst-case bound with the default β's is lr·(1−β1)/√(1−β2), about 3.2·lr. §7.5's
  reachability argument must hold under the worst case, or say "typically". A first look at one run record
  (Arm A, seed 0) suggests it holds: its stored rate puts the checkpoint's variance state about 154,000 iterations
  away, and even the worst-case bound would need about 46,000. N13 checks every run and every stated iteration
  count.
- **The review's in-sample comparison crosses models**: the released checkpoint's in-sample 8.3× against our
  arms' held-out 2.1×. It is suggestive; X10 is the within-model test.
- **App. R.** The review says it states that the heads differ only in initialisation; the template's nearest
  sentences are §6.4's "only the output heads differ" and App. T's note on Arm A seeds. The question behind the
  remark, whether the code resamples data per head, still needs an answer (G1).
- **The PETS survey.** The artifact records 10 repositories "examined", all 10 carrying the construction, which is
  circular because examination is defined by carrying it. The review's "13 inspected" has to come from the
  search records (G1).
- **Two of the review's fixes are either/or.** For §5.2 and §5.3 it offers more training, or a shorter section
  with a weaker label. The default here (Y6) is the second.
- **The fold extension is new training**, which your 16 Oct ruling forbids without a written protocol and an
  explicit ruling. That is Y5.
- **The upstream report** is a fact only you know. `docs/presubmission/AUTHOR_QUERY_ALIGNMENT.md` exists, and
  round 4's last checkpoint lists sending it as your step "if it has not gone" (Y10).

### 0.3 Decisions: accept the defaults or change them before G0

G0 copies this table into `round5/DECISIONS.md` as your rulings. To disagree with a default, edit its line here
before launching G0.

| # | Question | Default |
|---|---|---|
| Y1 | Length | **Main content, from the title to the last line before References, at most 12 pages** in the official TMLR template, which is TMLR's two-week review track. If that cannot be met without a result leaving the record, stop at 15 and record why ("Long submission"). Replaces W6. |
| Y2 | Abstract | **About 200 words (check: at most 210) and at most 5 numerals**, no capitalised verdict labels, readable by an ML researcher outside model-based RL. Tighten C12.1 accordingly. Replaces W7. |
| Y3 | Internal labels | **None in the main text**: no ledger or rule IDs, no commit labels, no capitalised verdict labels, no "entry-res"-style variable names. The pre-registration appendix (App. E) maps plain names to IDs and gives every verdict verbatim; other appendices may name a rule by ID; ledger IDs and commit labels appear only in App. E and in `docs/`. Replaces W8. |
| Y4 | Where text that leaves the PDF goes | **Into `docs/SUPPLEMENT.md`**, generated from `docs/SUPPLEMENT.template.md` with the same `{{key}}` machinery and shipped in the anonymised ZIP, or, for drafting history, `docs/BUILD_CHECKS.md`. A key-coverage gate proves that nothing leaves the record. Replaces round 4's rule 10 destination ("an appendix"). |
| Y5 | New computation | **(B), recommended: the inference-only analyses (X9, X10, N7–N14) plus the fold replications X11**: 12 ensemble-5 runs and 8 single-model runs at 2,500 iterations on X3's four new folds, about 25 CPU-hours in the background, cap 30, re-probed in GT1. It amends the 16 Oct "no new training" ruling for these runs only. (A): inference-only; the held-out ensemble-5 numbers stay at n = 4 with exact tests, and the independent-ensemble number moves to n = 20 through X9(d). (C): (B) plus M-68 and M-49 on the folds, about 50 CPU-hours, cap 55. |
| Y6 | §5.2 and §5.3 | **No training.** §5.2 becomes one paragraph ("at small budgets, shorter histories learn faster"; the original's trade-off with training time is not tested). §5.3 says "consistent with the claim, but a weak test" and adds the floors. Alternative: train §5.2's runs to a validation plateau and sweep three learning rates per baseline, under a new pre-registration (budget to be probed). |
| Y7 | "Too small by" | **The coverage-matching factor**, the multiplier on σ that restores 68.27% ±1σ coverage, is the only quantity called "too small by ×k". ρ is reported as the error-to-spread ratio beside its calibrated value of 0.80. Alternative: mean-matching, ρ/0.80. |
| Y8 | Ranking statistic | **Spearman is the headline statistic for every ranking statement**, with Kendall in the appendix; each pre-registered verdict keeps the Pearson statistic it was committed with, and says so. Alternative: Pearson first, rank statistics as a sensitivity. |
| Y9 | Title | **Decided at G8 from the readings.** The leading candidate drops "Verified" and names the scope: "Right Order, Wrong Size: Reproducing the Robotic World Model's Dynamics Model and Testing the Uncertainty It Reports". |
| Y10 | Upstream report of the action misalignment | **You send the alignment report** (`docs/presubmission/AUTHOR_QUERY_ALIGNMENT.md`) through the existing correspondence before G14, and the paper states the date and any reply. If you prefer not to, the paper says it was not reported before submission. |
| Y11 | Competing interests | **Declare it on the OpenReview form**: one author corresponded with the first author of the reproduced papers, who therefore knows that author's identity. G17 drafts the text; you paste it. |
| Y12 | Round 4's own steps | **None of round 4's §0.4 steps now** (merge and push, Hugging Face re-upload, archive). They move to after G18. Round 4's `PAPER.pdf` and `supplementary_anon.zip` are superseded: do not upload them. |
| Y13 | How sessions run | **One fresh terminal per session through `round5/go.zsh`**, with the model and effort §0.4 gives; subagents only where a session's section names them. G0 replaces the "Finishing round 4" section of `PDM/CLAUDE.md` with Annex 5's round-5 block (the old text is kept in `round5/`). |

### 0.4 Order, models and launch

Run the sessions strictly in this order, one at a time. Do not start a session until the one before it has
written `status: COMPLETE` in `round5/SESSION_LOG.md`. The two exceptions are waiting, never overlap:
- **G9 starts only after you approve `round5/OUTLINE.md`** (G8 leaves the question in `DECISIONS.md#G8-outline`).
- **GT2 starts only after GT1's training queue has finished** (if Y5 is B or C). If the queue is still running
  when G12 completes, wait; do not reorder.

| ID | Model | Effort | Scope | Time |
|---|---|---|---|---|
| G0 | Sonnet 5.5 | medium | Branch, round-5 files, subagents and launcher, baselines | 45 min |
| G1 | Sonnet 5.5 | high | Review premises against the artifacts; paper versions and crosswalk; upstream code since the pins | 2 h |
| G2 | Opus 5.5 | high | Protocols for X9, X10 (X11) and specifications for N7–N14, committed before any data | 2 h |
| GT1 | Opus 5.5 | high | **Only if Y5 is B or C.** Pre-register X11 (X12), timing probe, launch the queue | 2 h, then 25–50 CPU-h in the background |
| G3 | Opus 5.5 | high | X9 (per-member propagation) and X10 (in-sample against held-out): scripts, assertions, runs | 2.5 h |
| G4 | Sonnet 5.5 | high | Post hoc N7–N14: scripts, artifacts, stages, ledger entries | 3 h |
| G5 | Opus 5.5 | medium | Readings into the record: the M-65 retraction, the corrections, `READINGS.md` | 1.5 h |
| G6 | Sonnet 5.5 | high | Tooling: supplementary document, two-significant-figure display, the round-5 gates | 2.5 h |
| G7 | Sonnet 5.5 | medium | Bibliography: new entries verified from their records; references 1 and 2 fixed | 1 h |
| G8 | Opus 5.5 | high | `OUTLINE.md`: structure, page budget, one home per result, figures, title, abstract. **Then you approve it** | 2 h |
| G9 | Sonnet 5.5 | medium | Move supplement-bound material out of the PDF | 2 h |
| G10 | Sonnet 5.5 | high | Figures: a new Figure 1, Figure 4 recast, renumbering | 1.5 h |
| G11 | Opus 5.5 | high | Rewrite: title, abstract, §1–§3 | 2.5 h |
| G12 | Opus 5.5 | high | Rewrite: the base paper's claims | 2 h |
| GT2 | Sonnet 5.5 | medium | **Only if Y5 is B or C, after the queue.** Training gate and X11 readings | 1 h |
| G13 | Opus 5.5 | high | Rewrite: the uncertainty section, around three gaps | 3 h |
| G14 | Opus 5.5 | medium | Rewrite: defects, lessons, limitations, conclusion, statements; reach 12 pages | 2 h |
| G15 | Opus 5.5 | medium | Appendices: consolidate into standalone A–O | 3 h |
| G16 | Opus 5.5 | high | Fresh-eyes review, with three subagents. **New terminal** | 2 h |
| G17 | Opus 5.5 | medium | TMLR recheck, freeze, clean-clone measurement, bundles, package | 3 h, plus 2–6 h CPU |
| G18 | Sonnet 5.5 | medium | Clean-clone verification and final report. **No edits** | 1 h, plus 3 h CPU |

**Launch G0 by hand**, from the repository root (it creates the launcher, and this one command keeps
`~/Downloads/CLAUDE.md`, which describes a different project, out of the session's context):

```zsh
cd ~/Downloads/PDM/rwm_repro
claude --model claude-sonnet-5-5 --effort medium --name round5-G0 \
  --settings '{"claudeMdExcludes":["'"$HOME"'/Downloads/CLAUDE.md"]}' \
  "Read docs/presubmission/round5/PLAN.md §1 and the section for session G0, then carry out session G0."
```

**Every later session**, from the repository root, in a fresh terminal:

```zsh
docs/presubmission/round5/go.zsh G1            # start a session
docs/presubmission/round5/go.zsh G1 resume     # after PARTIAL or BLOCKED
```

The launcher sets the model, effort and session name from §0.4's table and passes the first instruction.

- **`PARTIAL`** means the session ran low on room or hit a usage limit. If the terminal is still open after the
  limit resets, type `continue`; otherwise use `go.zsh Gx resume`, which reads `round5/CHECKPOINT.md` first.
- **`BLOCKED`** means a decision is needed. Answer under its question in `round5/DECISIONS.md`, then `go.zsh Gx resume`.

**Keeping within usage limits and context.**
- Opus draws on your plan's allowance faster than Sonnet, and subagents draw on the same allowance as the
  session that starts them. Check `/usage` before an Opus session; if the allowance looks tight, run the next
  Sonnet session first, or wait for the reset.
- Never switch model inside a session with `/model`: it re-sends the whole conversation uncached and saves the
  new model as your default. A different model means a new session.
- Never run two Claude sessions on this repository at once. A background training queue is not a session; the
  text sessions can run while it trains.
- `/context` shows how full a session is. If it passes about 60%, tell the session to finish its current item
  and stop `PARTIAL`; a fresh session that reads the checkpoint costs less than a compacted one and keeps §1
  intact.

### 0.5 Only you can do these

**Before G0:**
1. Read §0.2 and §0.3; edit any default you disagree with.
2. Remove the line `"Bash(rm -rf *)",` from `PDM/.claude/settings.local.json`. It lets any session started in
   `PDM/` delete files without asking, which this round never needs.
3. Do not upload round 4's files, and hold round 4's own §0.4 steps (Y12).

**After G8:** read `round5/OUTLINE.md` (about 15 minutes) and approve or edit it under `DECISIONS.md#G8-outline`.
It fixes what the rewrite sessions write, so it is the cheapest place to change your mind.

**Before G14 (Y10):** send the alignment report through the existing correspondence, or decide not to, and
write the date or the decision under `DECISIONS.md#Y10`.

**After G18, in this order:**
1. Fast-forward or merge `presubmission5` into `main` and push, if you still want the repository's state
   public before review. Then re-upload `MODEL_CARD.md` to Hugging Face, and trigger a Software Heritage archive
   of the pushed commit; the paper says the repository was archived before submission.
2. Every author checks their remaining 2026 TMLR quota and completes their OpenReview profile
   (`round4/TMLR_CHECK.md` gives the procedure).
3. On the form: the title and abstract from `docs/SUBMISSION_PACKAGE.md`; **"Regular submission"** if the main
   content is at most 12 pages; competing interests from G17's draft (Y11); human subjects "N/A"; suggested
   action editors.
4. Upload `PAPER.pdf` and `supplementary_anon.zip` last, after checking both against the SHA-256s in
   `docs/SUBMISSION_PACKAGE.md`, without rebuilding them.

Nothing is pushed once the paper is under double-blind review, so step 1 comes before step 4.

---

## 1. Rules for every session (read in full each time)

### 1.1 Scope
- Do only your own session's items. Log anything else as one line with file:line in `round5/OUT_OF_SCOPE.md`,
  and do not fix it. Do not start the next session's work.
- Your section quotes the review text you need. Do not open `round5/REVIEW_2026-10-19.md` unless you are G1.

### 1.2 Integrity (non-negotiable)
Round 4's rules hold, with the amendments marked.
1. **No hand-typed numbers.** Every measured number in the paper, the supplement, the model card and the README is
   a `{{key}}` from `scripts/paper_numbers.py`, read from an artifact under `results/`. Display precision is the
   `{{key|sN}}` form from G6, which formats the artifact's value; it is never a retyped value.
2. **Edit sources, never outputs.** `PAPER.template.md`, `README.template.md`, `docs/*.template.md` and the
   generators. Never `PAPER.md`, `PAPER.tex`, `docs/SUPPLEMENT.md` or any other generated file.
3. **The ledger is append-only.** New IDs come from `scripts/ledger_check.py`. A correction is a new entry naming
   the entry it corrects. The sanctioned in-place edits are a rule's `Status` line at its discharge and, for a
   claim withdrawn by an `S-` entry, the target's status `SUPERSEDED` with its pointer. `ledger_check.py` must pass.
4. **Pre-register before data.** X9, X10 (and X11, X12) each get their rule text committed before any of their
   data exist (G2, or GT1 for X11 and X12), then a ledger entry with status `PRE-REGISTERED` and its reading
   script, committed under a subject containing `PRE-REGISTER`, before the first reading (G3, GT1).
   A script is never changed after that
   commit; if it must change, stop `BLOCKED`. N7–N14 are **post hoc**: label them so everywhere; they never
   change a discharged verdict.
5. **Verify against source.** Every new analysis script first asserts that it reproduces an existing artifact on
   the cases they share; its specification names the assertion. A failed assertion is `BLOCKED`, never a reason to
   adjust code after seeing a new number.
6. **Citations** are added only through `scripts/t1_bibliography.py`, from the record; never from memory.
7. **Anonymity.** The deny-list scan passes for the PDF, both bundles and `docs/SUPPLEMENT.md`. No absolute home
   path, account name or e-mail address goes into any tracked file; write `$HOME` or a relative path.
8. **Never loosen a failing check.** Fix the cause or report the failure. *Amended:* this round moves most of the
   text, so re-anchoring is expected: re-anchor a check when the sentence it guards legitimately moves (to another
   section, an appendix or the supplement, all of which the checks read after G6) and log old anchor → new anchor.
   When a check guards a claim that an `S-` entry withdraws, its expectation changes in the same commit as the
   `S-` entry, citing it. Never retire a numeric assertion. Tightening a check is always allowed.
9. **Leave the PDF, not the record** (*replaces* round 4's rule 10). Text that leaves the paper goes to
   `docs/SUPPLEMENT.template.md`, or, if it is drafting history, to `docs/BUILD_CHECKS.template.md`'s "Moved from
   the paper body" list. No result, number, verdict, table or figure may leave the paper, the supplement and the
   ledger together; the `keys` gate (G6) enforces this against `round5/base_keys.txt`, and any key that leaves on
   purpose is listed in `round5/RETIRED_KEYS.md` with its reason (superseded by key X; a display variant of key X;
   a restatement removed in favour of key X).
10. **Summaries are checked against every reading** (round 3's rule 10, round 4's rule 11). A sentence in the
    abstract, the contributions, the lessons, the limitations or the conclusion may claim a direction only if
    every reading the body or appendices report for that result agrees with it: every arena, horizon, metric and
    configuration it covers. If the readings split, the summary says so.
11. **Round 4's locked framing still holds** wherever a result is summarised: X3's outcome in the abstract and
    in the contributions, at the headline's prominence (ruling W11); X4 tests parameter count only; X5 stays not
    run, and the command is never inferred from achieved velocity;
    X6 is the 70-unit h = 100 result, not the 400-step h = 368 one; X7 is pooled epistemic
    coverage on a checkpoint that trained on all ten episodes; X8 covers its four rules only; N5 and N6 stay post
    hoc. A result may be left out of a summary, but never stated without its scope.
12. **No destructive git.** Never `git clean`, `reset --hard`, `rebase`, `push` or `merge`, and never discard
    uncommitted work. The one exception: a generated file whose only change is its build date (the PDF) may be
    restored with `git restore`. Never delete or overwrite `runs/`, weights, logs or an existing artifact under
    `results/` unless a section says so.

### 1.3 Context, usage and subagents
- **Start by reading only:** `PDM/CLAUDE.md` (loaded for you), §1, your own section, `round5/CHECKPOINT.md`, the
  last entry of `round5/SESSION_LOG.md`, and the annexes and files your section names.
- **Never read whole:** `FINDINGS_LEDGER.md` (about 670 KB), `PAPER.template.md` (about 290 KB), `PAPER.md`,
  `PAPER.tex`, `scripts/paper_numbers.py` (about 260 KB), `scripts/check_comparative_claims.py` (about 130 KB),
  `results/paper_numbers.json`, any `results/*.json` over 100 KB, `docs/APPENDIX_G_RULES.md`,
  `docs/CLAIMS_AUDIT.md`, `docs/DEFERRED.md`, a downloaded paper, or any earlier round's log. `grep -n` first, then
  Read at most about 200 lines at a time; extract JSON fields with `python3 -c` or the project interpreter.
- Send long output to a log file and show `tail -n 40`.
- **Subagents** are defined in `.claude/agents/` (Annex 5). Use only those your section names, at most three per
  session. Give each the exact files and line ranges it needs and nothing else; ask for at most 300 words (600 for
  `rwm-referee`). Subagents read; they never edit, and they cannot start subagents of their own. Never delegate
  something one `grep` answers.
- **Checkpoint.** At the end of every session, and whenever you stop early, overwrite `round5/CHECKPOINT.md`
  (at most 1,000 tokens): state, the exact next action, blockers, and the files involved. If the conversation has
  been compacted once, or feels heavy, finish the current item, commit, write `PARTIAL` naming the next step, and stop.

### 1.4 Protocol
- **Start gate.** The last log entry must be the previous session in §0.4's order (skipping GT1 and GT2 when Y5 is
  A) with `status: COMPLETE`, or this session with `PARTIAL` or `BLOCKED`. G9 also needs
  `DECISIONS.md#G8-outline` approved; GT2 needs the queue finished; GT1 and GT2 run only if Y5 is B or C.
- **Branch and commits.** Branch `presubmission5` (G0 creates it). One commit per item, subject `[Gx][item] summary`.
  Commit locally; never push (workplan rule, unchanged).
- **End of every session that changes text, numbers or a generator:**
  1. FILE_MAP §3's fast build, then the gates (including `scripts/round5_gates.py --report` once G6 has added it),
     then the fast build again;
  2. the second build must be byte-identical to the first;
  3. append the log entry, overwrite the checkpoint, commit.
- **Log entry template:**

```
## Gx — YYYY-MM-DD HH:MM — <model, effort as run> — status: COMPLETE | PARTIAL | BLOCKED
Commits: <hash> <subject>, one per line
Review items closed: RVnn, … (Annex 1) | none
Done: …
Build/gates: pass | fail (<which>) | not run (no text, number or generator changed)
Round-5 gates (report mode until G16): pages <p>/12, abstract <w>/<n>, ids <n>, once <n>, sig <n>, keys missing <n>
Paper numbers changed: none | <key: old → new, artifact>
New keys: none | <key, artifact>
Ledger: none | <new IDs; statuses changed>
Re-anchored checks: none | <check: old → new>
CPU jobs over 1 min: none | <what, how long, contended?>
Queue (Y5): not applicable | not launched | running (<n of m>, projected finish) | done
Body words / main-content pages: <n> / <p> (G0: 17,804 / 26)
Subagents: none | <name × n>
Next: …
Decisions for user: none | DECISIONS.md#<anchor>
```

- **Stop with `BLOCKED`** and write the question to `DECISIONS.md` when an assertion this plan names fails; a
  review premise turns out false in a way that changes what your section asks; a result would change a headline
  number, a verdict or an abstract claim beyond what this plan specifies; two artifacts disagree and you cannot
  tell which is current; a CPU projection exceeds its cap; a page or word budget cannot be met without a result
  leaving the record; or this plan says to.

### 1.5 CPU and background jobs
- **Never two training jobs at once** (8 GB of RAM). Inference beside the queue is allowed; it slows both and
  changes no number. Log it as contended.
- **Timing probes run on an idle machine.**
- **Background jobs** run as `caffeinate -i nohup <command> > <log> 2>&1 &`, on mains power. Record the PID, the
  log path and the completion sentinel in your log entry. Do not keep a session open to poll a job: end the
  session, and let the next session check the sentinel.
- Log every job over 1 minute.

---

## 2. Sessions

### G0 — Orientation and setup (Sonnet 5.5, medium)
Closes: none; it sets up the round.
Reads: §0.3, §1, Annex 5; `round4/CHECKPOINT.md`; `docs/presubmission/FILE_MAP.md` §1–§3 (grep).

1. **Working tree and branch.**
   - `git status`. Expected untracked paths: `round5/PLAN.md` and `round5/REVIEW_2026-10-19.md` only. Record any
     other; stop `BLOCKED` if a source (a template, `scripts/`, `src/`, `results/`, `reproduce.sh`) or the
     ledger has uncommitted changes.
   - HEAD must be round 4's F12 log commit on `presubmission4`, a descendant of `796a026` that adds only round-4
     records.
   - Tag HEAD `pre-round5`, create branch `presubmission5`, and commit the two files:
     `[G0][1] Round-5 plan and the 19 Oct review (verbatim, byline removed)`.
2. **Round-5 files** in `docs/presubmission/round5/`: `SESSION_LOG.md`; `DECISIONS.md` (§0.3's table under
   `## G0-rulings`, with "defaults accepted by launching G0, <date>" or the user's edits, byte-compared with this
   file's table); `OUT_OF_SCOPE.md`; `CHECKPOINT.md`; `LENGTH_LOG.md`; `RETIRED_KEYS.md` (a header and the reason
   vocabulary of rule 9).
3. **Claude Code files** (Annex 5):
   - the four subagents in `.claude/agents/` and the launcher `round5/go.zsh` (`chmod +x`); commit both;
   - `.claude/settings.local.json` with `claudeMdExcludes` naming `~/Downloads/CLAUDE.md` by absolute path; add
     `.claude/settings.local.json` to `.gitignore`; never commit the settings file;
   - record whether `~/Downloads/CLAUDE.md` is in this session's context (it should not be), and in the log tell
     the user they can confirm with `/memory`;
   - record `claude --version`: the subagents' `omitClaudeMd` field needs v2.1.271 or later. An older version
     ignores the field, so subagents also load the CLAUDE.md files; that costs context but is harmless. Say so in
     the log rather than updating anything.
4. **`PDM/CLAUDE.md`** (outside the repository; nothing to commit there): copy its section "Finishing round 4:
   the TMLR workplan" verbatim into `round5/CLAUDE_md_round4_section.md`, then replace that section with Annex
   5's round-5 block. Leave every other line unchanged.
5. **Bundle exclusion.** Dry-run the collection step of `scripts/build_supplementary.py` and
   `scripts/make_anon_bundle.py`; assert that nothing under `docs/presubmission/round5/` or `.claude/` is collected.
6. **Baselines** in `round5/BASELINE_G0.md`, measured from the committed files. Run FILE_MAP §3's fast build and
   gates once and record pass or fail for each; if the build changed only `PAPER.pdf`'s dates, restore the
   committed PDF with `git restore PAPER.pdf`. Then record:
   - total pages; the page on which References starts; main-content pages to one decimal;
   - body words in total and per section (`docs/presubmission/round2/t6_words.py`);
   - the abstract's words and numerals as C12.1 counts them;
   - in the main text: ledger and rule IDs by kind, commit labels, capitalised verdict labels, decimals with more
     than two significant figures, and how often each interval-valued key appears (the 20 most repeated);
   - words per appendix; the figure list (file → number, from `build_paper.py`'s map);
   - every `{{key}}` that `PAPER.template.md` and `docs/*.template.md` print at `796a026`, one per line, into
     `round5/base_keys.txt` (the `keys` gate's base set).
7. **Seed `OUT_OF_SCOPE.md`** with one line: `PDM/CLAUDE.md`'s style section says "five retractions", while the
   ledger's counts differ (the user's file; not this round's to fix).
8. Log entry, checkpoint. No paper edits.

### G1 — Review premises, paper versions and the upstream code (Sonnet 5.5, high)
Closes: the evidence for RV09–RV13, RV31 and RV39, and the premise check every later session relies on.
Reads: §1, G1, `round5/BASELINE_G0.md`, and the review (the only session that opens it).
Subagents: `rwm-sources`, at most two (bibliographic and venue checks).

1. **Premises.** Write `round5/PREMISES.md`: for each premise below, TRUE, FALSE or PARTLY; the evidence (artifact
   path and JSON key, file:line, or URL with a quoted fragment); and the session it affects. Print stored fields;
   do not recompute what an artifact holds.
   - P1 main content about 26 pages, References on p. 27 · P2 abstract about 320 words and 20 numbers (C12.1) ·
     P3 `+0.2816 [+0.1978, +0.3896]` about ten times and "17 of 36" more often · P4 Figure 1 is the
     pre-registration lead-time figure · P5 capitalised labels such as "SURVIVES entry-res ONLY" in the body.
   - P6 RWM at NeurIPS 2025 and RWM-U at ICLR 2026: main track or workshop, and is either archival ·
     P7 reference 2 pairs v1 with a later title · P8 RWM-U's current abstract says uncertainty is "effectively
     propagated over long horizons" · P9 RWM-U v1 §4.1 says the learned variance "captures aleatoric uncertainty
     effectively" (and v3?) · P10 v1 §4.1 places the ensemble heads after a shared recurrent feature extractor and
     calls them bootstrap ensembles · P11 our App. R says the heads differ only in initialisation · P12 the
     released code does no per-head data resampling.
   - P13 RWM-U v1's world-model training table is Table S8, sets the forecast decay to 1.0 and says 2,500; Table
     S9 is the MOPO-PPO table · P14 whether RWM's own paper (v1, v5) sets a forecast decay · P15 App. H says "the
     paper describes a decay" (C-09) and cites Table S9 for the training length.
   - P16 held-out h = 1: ensemble-5 arms ρ ≈ 2.1 and ±1σ ≈ 36%; the independent ensemble ρ ≈ 1.4 and ≈ 50% ·
     P17 the released checkpoint in-sample at h = 1, ρ ≈ 8.3 · P18 the ensemble-5 arms have 16 in-sample and 4
     held-out non-overlapping 400-step trajectories · P19 §6.2 says in-sample measurement flatters calibration ·
     P20 §7.5 and App. F: the release cannot reproduce the checkpoint, and the first author describes a different
     training setup.
   - P21 X3: 20 trajectories, 10 of 10 episodes, p = 0.002 · P22 App. B's timings imply about 25 CPU-h for M-43,
     the Arm A recalibration and M-44 on X3's folds, about 50 with M-68 and M-49 · P23 §5.2: 2,500 iterations,
     every run still improving, 0.133% of the data, a verdict that reverses with longer training · P24 §5.3's
     baselines use RWM's learning rate and budget; three rows diverge; the RSSM is uninformative; the size-matched
     transformer cannot be told apart · P25 M-43 returned DOES NOT GENERALISE and was under-powered.
   - P26 M-65: 33 of 48 cells over-cover at ±1σ after mean-matching · P27 the mean-matching constant is 10.4 at
     h = 1 and 43.2 at h = 368, the coverage-matching one 6.3–6.8 and 40.3–43.0 (App. Y) · P28 at h = 100,
     ρ = 33.4, mean-matching needs ×42 and coverage-matching ×29–32.
   - P29 Figure 4's rate is −9.39e-5 per iteration with a spread of 6e-7, against a configured learning rate of
     1e-4 (RWM-U v1 Table S8) · P30 the optimiser is Adam, and with which β's (`rsl_rl_rwm` source;
     `scripts/step5_train.py`) · P31 App. J: on log Δ the bound term pushes 0.2 and the state loss 0.05; the state
     loss gives `min_logstd` 0.0703; App. H: `min_logstd` drifts 5.2× slower than log Δ.
   - P32 nRMSE's primary form divides by the mean per-dimension σ (`results/v3_metric_definitions.json`,
     `src/rwm_metrics.py`) · P33 App. L at h = 368: released 0.905, MLP-AR 1.44, transformer-AR 2.01 · P34 §3.1
     justifies Pearson "because a ranking claim is about order" · P35 the PETS survey: how many repositories were
     inspected (the search records), how many carry the bounded head, how many train it on a sampled squared
     error · P36 "we are aware of"-style priority claims in the body.
   - P37 the clean-clone gate fails on 3 values, all bookkeeping (round 4's FINAL_REPORT) · P38 the headings "The
     structural excuse does not survive" and "…evaluation is the broken one" · P39 TMLR: no page limit, reviewer
     deadlines set by 12 main-content pages, double-blind, competing interests reported on the form
     (`round4/TMLR_CHECK.md`) · P40 MLRC 2026 required TMLR submission by 30 Sept 2026 (`docs/SUBMISSION_VENUE.md`).
2. **Paper versions.** Download 2501.10100 v1–v5 and 2504.16680 v1–v3 (PDF and abstract page), and the two
   OpenReview workshop PDFs (forum ids `u76d3gBWCX` and `mcwLgO93ym`), into `docs/presubmission/sources/`
   (gitignored). Extract text with pypdf under the project interpreter; record each file's SHA-256. Grep the text;
   never read a paper whole.
3. **Crosswalk.** Write `scripts/version_crosswalk.py` on the pattern of `scripts/verify_original_quotes.py`. For
   every claim Appendix D lists and every passage the paper quotes from either original, it records: the v1
   location and verbatim fragment; the current version's location and fragment; the workshop version's, where it
   differs; `changed: no | moved | reworded | new | removed`; and, for a changed claim that the paper tests, what
   the test must now say. It writes `results/version_crosswalk.json`; each fragment is asserted present in the
   local text. Summarise in `round5/CROSSWALK.md` (at most 1,200 words). It needs the network, so it is not a
   `reproduce.sh` stage; add a FILE_MAP row saying so.
4. **Upstream code since the pins.** Clone both upstream repositories read-only into
   `/Users/Shared/rwm_verify/upstream_latest/`, never touching `PDM/robotic_world_model_lite/` or
   `PDM/rsl_rl_rwm/`. Record `git log --oneline <pin>..HEAD`, and diff the rollout, ensemble, loss and data code
   between the pin and HEAD; grep both for per-head data resampling. A changed rollout means the pinned code may not
   be the current method: write that into `CROSSWALK.md` §code.
5. Commit the script, the artifact and the two documents. No paper edits.

### G2 — Analysis protocols, committed before any data (Opus 5.5, high)
Closes: the design of RV15–RV17, RV19, RV20, RV24–RV28 and RV42.
Reads: §1, G2, Annex 2, `round5/PREMISES.md`, `CROSSWALK.md` §code, `DECISIONS.md` (Y5–Y8).
Subagents: `rwm-reader`, one.

The review, on what X9 must test: "roll the released checkpoint out PETS-style (TS∞: each head feeds back its own
prediction through its own hidden state; Chua et al., 2018), and score the propagated spread against accumulated
error. That directly tests the 'propagated over long horizons' claim."

1. Ask `rwm-reader` for the file:line of the scoring functions, trajectory builders and bootstrap code in
   `scripts/task_d_nind20.py`, `task_d3_ens5.py`, `r2_independent_ensemble.py`, `x3_cross_fold.py`,
   `x7_loeo_recalibration.py`, `task_d3_perhorizon.py`, `m65_gaussian_nominal.py`, `e7_free_baselines.py`,
   `x6_stepsize_short_units.py`, `a1_ab_by_horizon.py` and `baselines_eval.py`, and of `rollout_full` in
   `src/rwm_model.py`; which per-trajectory or per-step values each artifact or `cache/` file stores; the action
   offset each existing calibration artifact used; and where the X3 fold weights, the ensemble-5 arms and the
   independent members are stored.
2. Write `round5/PROTOCOLS.md`:
   - **X9 and X10**: the final rule text from Annex 2's skeletons. You may tighten a threshold or add an
     assertion; never loosen one. Fill every path, function, unit, tolerance, seed and bootstrap setting.
   - **X11** (and X12 if Y5 is C): the skeleton GT1 completes.
   - **N7–N14**: specifications precise enough that a Sonnet session implements them with no design choice left:
     inputs, formulas, units, intervals, the reproduction assertion, outputs, the keys to add, the stage name, and
     how to time it. Where a specification needs a threshold (N8's signature labels, N10's period search window),
     fix it here.
3. Commit `[G2] PRE-REGISTER (rule text) X9 and X10; specifications for N7–N14` before any of their data exist.
   No scripts, no numbers.

### GT1 — Fold replications: pre-register and launch the queue (Opus 5.5, high) — only if Y5 is B or C
Closes: RV20 (launch). Reads: §1, GT1, Annex 2 (X11), `PROTOCOLS.md` §X11, `round4/RUN_QUEUE.md`, round 4's F1
entry in `round4/SESSION_LOG.md` (the pattern: fold support, timing probe, queue launch).

1. **The rules.** Complete X11 (and X12) in `PROTOCOLS.md`: reuse M-43's, M-44's and the per-horizon
   recalibration's statistics, thresholds and verdict branches verbatim, with only the arena changed to the five
   folds' 20 held-out trajectories, and list every change. Recompute each rule's minimum detectable effect at
   n = 20 with the script that computed it at n = 4, before any run exists.
2. **Reading scripts** for X11 (one per rule; no opaque combined script), frozen, with assertions: on fold {1, 8}
   they reproduce `task_d3_ens5.json`, `r2_independent_ensemble.json` and the per-horizon recalibration artifact
   exactly.
3. **Training support**, as F1 did for X3: (a) each new fold's windows hash to X3's fold windows; (b) a
   50-iteration ensemble-5 run of seed 0 on {1, 8} reproduces the committed ensemble-5 run's first 50 losses
   bitwise, or to 1e-6 if the record is rounded (say which); (c) each fold's training set excludes exactly its two
   episodes.
4. **Ledger entries** (`PRE-REGISTERED`, with the scripts' SHA-256s); commit `[GT1] PRE-REGISTER X11 …`.
5. **Timing probe** on an idle machine; project the queue; above the cap (30 h for B, 55 h for C) stop `BLOCKED`.
6. **Queue**: `runs/queue_round5.txt` with the 20 runs (B) or more (C), run through the existing
   `scripts/queue_runner.sh`, one at a time, under `caffeinate -i`, in the background. Write
   `round5/RUN_QUEUE.md` on the pattern of `round4/RUN_QUEUE.md`: the exact status command, the projected end, and
   what to do if the runner stops. Record the PID and the log in the log entry. End the session; GT2 reads the
   results after the queue has finished. No session reads a queue run's evaluation before GT2; G3 and G4 may check
   only that each run started and that its loss is finite.

### G3 — X9 (per-member propagation) and X10 (in-sample against held-out) (Opus 5.5, high)
Closes: RV15 and RV16 (data). Reads: §1, G3, `PROTOCOLS.md` §X9–X10, `round5/CHECKPOINT.md`, the function
ranges PROTOCOLS names, and the ensemble model in `src/rwm_model.py` (its `forward`, `rollout_full` and `rollout`).

The review: "the ensemble mean is what the model feeds forward as the next observation, so disagreement at step t
is a one-step spread at a shared state … roll the released checkpoint out PETS-style (TS∞: each head feeds back its
own prediction through its own hidden state) … If it closes much of the gap, it becomes your most actionable
result." And: "Heads fitted to the same targets agree most where they were trained … Your ensemble-5 arms let you
check this directly: 16 in-sample versus 4 held-out trajectories."

1. Implement `scripts/x9_ts_inf_propagation.py` and `scripts/x10_insample_vs_heldout.py`, separately and exactly as
   PROTOCOLS specifies. Each takes `--assert-only`, which runs only the reproduction assertions (the existing
   protocol on existing cases) and prints pass or fail. Until step 3's commit, no per-member-propagation number and
   no in-sample number may be computed or printed.
2. Run `--assert-only`. Any failure stops `BLOCKED` with the difference.
3. Ledger entries for X9 and X10 (IDs from `ledger_check.py`): status `PRE-REGISTERED`, rule text verbatim from
   PROTOCOLS, the scripts' SHA-256s. Commit `[G3] PRE-REGISTER X9 and X10: ledger entries and scripts`.
4. Time one trajectory per model; then run both scripts (minutes to an hour; contended if the queue is training).
   Artifacts `results/x9_ts_inf_propagation.json` and `results/x10_insample_vs_heldout.json`, recording the rule,
   ledger ID, script SHA-256, `git_head`, design, assertions, readings and caveats, as round 4's X-rule artifacts do.
5. Discharge: write each verdict verbatim into its entry's `Status` line.
6. `reproduce.sh` stages: the released checkpoint's part is **not** `NEEDS_WEIGHTS` (it ships with `setup.sh`);
   the parts that read our arms are. Add keys for every number the rewrite may print, intervals included. Fast
   build and gates; commit.

### G4 — Post hoc analyses N7–N14 (Sonnet 5.5, high)
Closes: the data for RV17, RV19, RV24, RV25, RV27, RV28 and RV42, and the inputs to RV26.
Reads: §1, G4, `PROTOCOLS.md` §N7–N14, and only the function ranges they name.

Take them in the order N8, N7, N9, N10, N11, N12, N13, N14 (N14 only if PROTOCOLS keeps it). For each:
1. `scripts/n<k>_<name>.py` exactly as specified. It first asserts reproduction of the existing artifact on the
   shared cases its specification names.
2. Run; write `results/n<k>_<name>.json` with `"post_hoc": true` and a `never_reopens` field naming the rules it
   cannot change.
3. A ledger entry: post hoc, its evidence class, and its paper-relevance tag as the specification gives.
4. A `reproduce.sh` stage (`NEEDS_WEIGHTS` only where it reads `runs/`), the keys, a commit `[G4][N<k>] …`.

Never choose a statistic, a family, a unit or a threshold after seeing data. If a specification leaves a choice
open, stop `BLOCKED` with the question.

### G5 — Readings into the record (Opus 5.5, medium)
Closes: RV12, RV13, RV24 and RV26 (record); the inputs to RV14 and RV17.
Reads: §1, G5, `round5/CHECKPOINT.md`, `PREMISES.md`, `CROSSWALK.md`, the G3 and G4 log entries, each new
artifact's `readings` field, and by grep the ledger entries M-65, M-96, C-09 and S-21 (the format of a withdrawal).

1. **M-65.** A new `S-` entry withdraws M-65's reading "NOT HEAVY-TAILED, in every one of 48 model × horizon cells",
   with `**Retracts** M-65`, pointing at N8's entry. Mark M-65 `SUPERSEDED` with that pointer and drop any `CONTRIB`
   tag. The entry says why: matching the mean |error| / σ to a Gaussian's 0.798 makes a heavy-tailed or
   scale-mixture error over-cover at ±1σ and under-cover at ±2σ, so the 33 over-covering cells, which the rule's
   committed branch names OVER-DISPERSED, are that signature; N8's ±2σ column shows the other half.
   Update any check that asserted the withdrawn reading in the same commit (rule 8).
2. **From PREMISES and CROSSWALK:** C-09 (correct it, or withdraw it if RWM-U's table sets the decay to 1.0 and
   RWM's own paper sets none); a new `C-` entry for "bootstrap ensembles" if the code does no per-head
   resampling; the shared trunk as documented in RWM-U v1 §4.1 (withdraw any ledger framing that presents it as a
   discovery); Table S8 for the training length; the PETS survey's three counts.
3. **Framings the review withdraws**, each only where a ledger entry states it (grep first; otherwise it is a
   wording change, for the rewrite): "in-sample measurement flatters calibration" (by X10's reading); "no single λ
   fits" and "deep-rollout states are under-penalised" read as calibration failures; "provably drives σ to zero";
   "the floor freezes"; "the first calibration measurement we are aware of".
4. **`round5/READINGS.md`**, at most 1,500 words: every new reading in plain words, with its key names and its
   scope (arena, n, checkpoint, horizon), and what it changes in the paper's story. Include Y7's "too small by"
   factor per horizon as keys, and the checkpoint-provenance sentence N12 supports.
5. `ledger_check.py` passes; every printed retraction count is derived; `paper_numbers.py` rebuilt (no template
   edits); fast build and gates; commit.

### G6 — Tooling for a short paper (Sonnet 5.5, high)
Closes: the tooling for RV01–RV05 and RV08.
Reads: §1, G6, FILE_MAP §1–§3, and by grep `scripts/build_paper.py`, `typed_numeral_audit.py`,
`restatement_index.py`, `horizon_sweep.py`, `xref_sweep.py`, `check_scope_audit.py`, `submission_check.py`, and
the entry points of `check_comparative_claims.py`.

1. **The supplementary document.** Add `docs/SUPPLEMENT.template.md` → `docs/SUPPLEMENT.md` to `build_paper.py`'s
   docs-template loop, beside `BUILD_CHECKS`. Confirm both bundle builders ship it and the deny-list scan reads
   it. Teach the comparative-claims checks, the typed-numeral audit, the restatement index and the horizon and xref
   sweeps to read it, so a passage moved there stays checked; extend `check_scope_audit.py` so the move cannot
   silently shrink coverage. Self-tests for each.
2. **Display precision.** `{{key|sN}}` renders every decimal in the key's value to N significant figures, keeping
   signs, brackets, %, × and integers unchanged. Unit-test 20 representative values (intervals, percentages,
   p-values, ratios, counts with thousands separators). Every gate recognises the form as a placeholder.
3. **`scripts/round5_gates.py`**, each check with a corrupt-and-catch self-test. "Body" here means everything from
   the title to the last line before References, the abstract included:
   - `pages`: main content at most 12 pages, read from the compiled PDF (the last page holding body text before
     References);
   - `abstract`: C12.1 tightened to 210 words and 5 numerals;
   - `ids`: no ledger or rule IDs, commit labels, capitalised verdict labels, or code-variable names used as
     labels (such as `entry-res`) in the body; file:line pointers into the released code stay allowed; ledger IDs
     and commit labels only in App. E and `docs/`;
   - `once`: an interval-valued key at most once in body prose and at most once in body tables and captions, and
     never in the abstract; any other numeric key at most twice across the abstract and the body's prose. Keys
     that name a setting rather than a result (horizons, iteration counts, episode and trajectory counts, sample
     sizes) are exempt; the gate lists the exemptions it applies;
   - `sig`: no decimal with more than two significant figures in the rendered body, with a short exception list
     (identifiers, version numbers, constants written as symbols);
   - `keys`: every key in `round5/base_keys.txt` is printed by `PAPER.template.md` or a `docs/*.template.md`, or
     listed in `round5/RETIRED_KEYS.md` with a reason.

   They run in `--report` mode until G16 makes them blocking. Add them to FILE_MAP §3 and to BUILD_CHECKS' list
   of check kinds.
4. Fast build twice, byte-identical; commit. The `--report` counts should match BASELINE_G0's measurements; say
   where they differ and why.

### G7 — Bibliography (Sonnet 5.5, medium)
Closes: RV10, RV32–RV36 and RV46. Reads: §1, G7, `CROSSWALK.md` (versions and venues), and
`scripts/t1_bibliography.py` by ranges. Subagents: `rwm-sources`, one.

The review: "Multi-step model training: Venkatraman et al. (2015, DaD), Bengio et al. (2015, scheduled sampling),
Talvitie (2017), Lambert et al. (2021) … Conformal prediction: Angelopoulos & Bates; Stankevičiūtė et al. (NeurIPS
2021…); Lindemann et al. (RA-L 2023…) … Shared-torso RL ensembles: Osband et al. 2016 (Bootstrapped DQN) and 2018
(randomised priors) … RL evaluation statistics: Agarwal et al. 2021; Henderson et al. 2018 … Pre-registration in
ML: the NeurIPS 2020–21 pre-registration workshops." Reference 2 "pairs v1 with a later title".

1. Extend `t1_bibliography.py` for entries with no arXiv id (a DOI record or the proceedings page), keeping its
   rule: title, full author list, venue and year from the record; a fragment only where the text attributes a
   claim.
2. Add and verify those entries, plus the ones the technical fixes cite: Cameron, Gelbach and Miller (2008) on
   cluster bootstraps with few clusters; Kingma and Ba (2015), Adam; and the proceedings of the NeurIPS 2020
   pre-registration workshop. Chua et al. (2018) and Yu et al. (2020) are already in.
3. Fix references 1 and 2 from `CROSSWALK.md`: the version tested (v1, with v1's title), the current version and
   its date, and the workshop presentation, named as what it is.
4. `--verify`, rebuild, commit. The citations themselves enter the text in G11–G15.

### G8 — Outline, page budget and abstract (Opus 5.5, high)
Closes: the decisions for RV01, RV04, RV07, RV14, RV18 and RV37.
Reads: §1, G8, Annexes 3 and 4, `round5/READINGS.md`, the verdict column of `PREMISES.md`, `CROSSWALK.md`'s
summary, `BASELINE_G0.md`, and `PAPER.template.md` from `## Abstract` to `## 2.` (the current abstract and
contributions). Subagents: `rwm-referee`, one.

The review: "Target 12–15 pages. Write a ~200-word abstract with at most five numbers. State each result once with
its scope (arena, n, checkpoint), and cross-reference it after that … Replace Figure 1 with a headline result …
restructure §6 around the three gaps and lead with the third … Lead §5 with X3."

1. Write `round5/OUTLINE.md`:
   - the sections and subsections, with page and word budgets that sum to at most 12 pages (Annex 3 is a
     proposal; change it if the readings argue for it);
   - **one home per result**: its section, its scope sentence, the keys it prints and at what precision, and the
     places that summarise it;
   - the figure plan: what Figure 1 shows (a finding; Annex 3 proposes one), which figures move to appendices;
   - the appendix plan: letters, merges, a word budget for each (Annex 4 proposes one);
   - **the supplement migration list for G9**, by exact anchor;
   - the title (Y9), with one recommendation and a reason;
   - an abstract draft written in `{{keys}}`, at most 200 words and 5 numerals, in which X3's outcome appears
     (locked framing) and no capitalised label does;
   - the contributions: at most four bullets of at most 45 words each, with no priority claim;
   - the rule-10 summary sites, and how each review item in Annex 1 lands.
2. Give `rwm-referee` only the outline's abstract, contributions and section plan, and ask what a TMLR reviewer
   would find unclear or unsupported. Revise; record its points and your answers in `OUTLINE.md` §Referee.
3. Commit. Write the approval question under `DECISIONS.md#G8-outline`. Status `COMPLETE`.

### G9 — Move supplement-bound material out of the PDF (Sonnet 5.5, medium)
Closes: RV06 and RV08 (the bulk moves). Reads: §1, G9, `OUTLINE.md` §supplement-migration, and the template
ranges it lists. Start gate: `DECISIONS.md#G8-outline` approved.

The review: "Several appendices are revision history ('the passages below stood there as follows') … Process detail
belongs in the supplement: queue logs, CPU-overlap counts, the history rewrite, and a clean-clone gate 'published
as failing'."

1. For each item on the list, in order: cut it from `PAPER.template.md` and paste it, verbatim with its keys, into
   `docs/SUPPLEMENT.template.md` under the heading the list gives; drafting history ("stood there as follows"
   passages) goes to `docs/BUILD_CHECKS.template.md`'s "Moved from the paper body" list. Leave nothing behind but
   what the list says stays (at most one pointer sentence).
2. After each item: fast build, the gates, `xref_sweep.py` with 0 suspect pointers, and the `keys` gate with 0
   missing. Re-anchor checks as rule 8 allows; log each.
3. Dry-run both bundles and confirm `docs/SUPPLEMENT.md` is collected; run the deny-list scan on it.
4. Log pages and words before and after in `LENGTH_LOG.md`; commit per item.

### G10 — Figures (Sonnet 5.5, high)
Closes: RV07 and the figure half of RV25. Reads: §1, G10, `OUTLINE.md` §figures, `scripts/paper_figures.py` by
ranges, and the figure map in `scripts/build_paper.py`.

The review: "Figure 1 shows pre-registration lead times. A reader's first figure should be a finding … Plot σ
itself, not only the clamp width."

1. Draw what `OUTLINE.md` specifies, from artifacts only, through `paper_figures.py` (stage 22 reads `runs/`):
   the new Figure 1; Figure 4 recast with σ itself (the bounds `exp(min_logstd)` and `exp(min_logstd + Δ)` per
   logged iteration, and measured σ at the saved checkpoints, from N13) beside the per-iteration change of log Δ
   divided by the learning rate, so the Adam signature (about 0.94 in every run) and the sign flip under the
   corrected objective are both visible.
2. Move the pre-registration lead-time figure to App. E; renumber through `build_paper.py`'s map.
3. Captions at most three lines, each naming arena, n, checkpoint and horizon. `pdf_render_check.py` passes, and
   look at every page that holds a figure. Fast build and gates; commit.

### G11 — Rewrite: title, abstract, §1–§3 (Opus 5.5, high)
Closes: RV02, RV28 (rationale), RV30 (abstract), RV32–RV36 (citations), RV37, RV38, RV41; contributes to RV01,
RV03–RV05. Reads: §1, G11, `OUTLINE.md` for these sections, `READINGS.md`, and the template's current Abstract,
§1–§4 and Data and code by ranges.

The review: "The ~320-word abstract carries nearly twenty numbers and capitalised verdicts. Phrases like 'no
reading favouring it' can't be parsed by a newcomer … 'Verified' can read as verifying the method's results,
whereas you verify the code … 'First we are aware of' claims. Drop them … §3.1 uses Pearson 'because a ranking claim
is about order'. That rationale points to Spearman or Kendall … Clean-clone gate. Explain the three values that
fail it, or drop the gate from the paper."

1. Title (Y9) and abstract from `OUTLINE.md`'s drafts, rechecked against `READINGS.md` (rule 10).
2. §1: what was reproduced and why it matters, the findings in plain words, Figure 1, at most four contributions;
   no priority claims; RWM-U's design credited where the original documents it.
3. §2, background and related work, at most the outline's budget: the method family (MOPO's penalty is meant to
   bound one-step error at visited states), the multi-step training literature (which sets the prior for §4: rollout
   training beating teacher forcing at long horizons, and losing at one step, is well established), shared-torso
   ensembles, calibration and conformal prediction, RL evaluation statistics and pre-registration in ML.
4. §3, setup: the reimplementation and its gradient-level equivalence, in a few sentences (App. A has the rest);
   data, episodes, arenas and n_independent in one table, saying that the four held-out trajectories come from
   two episodes; metrics, with nRMSE as G4 corrected it, ρ beside its calibrated 0.80, "too small by" as Y7
   defines it, and Spearman's rationale as Y8 sets it; the statistical protocol (cluster bootstrap over
   trajectories, exact tests at n = 4 and why they cannot go below p = 0.125, Holm, dimension-preserving
   permutation nulls); pre-registration in one paragraph, pointing at App. E.
5. The reproducibility statement and Data and code at the end of the paper, at most 120 words together: a clean
   clone reproduces every scientific value, and the 3 values that differ are bookkeeping about the archive itself
   (its sizes and its commit count), all from keys, with the accounting in the supplement.
6. Throughout: no internal labels (Y3); `{{key|s2}}` for every body number; each result only in its home.
   Fast build and gates after each section; words and pages into `LENGTH_LOG.md`; commit per section.

### G12 — Rewrite: the base paper's claims (Opus 5.5, high)
Closes: RV18, RV19 (this section), RV21, RV22, RV23 (this section), RV27 (this section).
Reads: §1, G12, `OUTLINE.md` for this section, `READINGS.md` (X3, N7, N10, N11), and the template's §5–§5.3 by ranges.

The review: "With four clusters the percentile bootstrap is unreliable … at n = 4, 'the interval excludes zero' (and
'survives Holm') essentially means 'all four agree in sign'. Lead §5 with X3 (20 trajectories, 10 of 10 episodes,
p = 0.002), and demote the 10k held-out factor to supporting evidence. Report exact randomisation p-values beside
every n = 4 bootstrap … §5.2 tests an unconverged budget … cut it to a paragraph … §5.3's baselines are untuned …
'REPRODUCES' over-reads that … call it consistent but weak … If 1.0 is a constant predictor, every baseline loses to
a constant, which changes how §5.3 reads."

1. The training claim, led by X3: every episode held out once, the direction in all ten (p and the fold range from
   keys), at 2,500 iterations; the one-step reversal on short units, framed against the multi-step literature; the
   10,000-iteration held-out factor as supporting evidence, with its exact p beside its interval and the two-episode
   caveat.
2. The configuration claim (Y6): one paragraph. The architecture claim (Y6): "consistent with the claim, but a weak
   test", with the training-mean, seasonal-naive and hold-last floors from N10 and the corrected nRMSE, the
   size-matched result as a parameter-count test only (locked framing), and the RSSM in one clause.
3. Plain-language verdicts; exact p beside every n = 4 interval kept in the body; the rest to App. G and App. H.
4. Fast build and gates; words and pages; commit.

### GT2 — Training gate and the fold readings (Sonnet 5.5, medium) — only if Y5 is B or C, after the queue
Closes: RV20 (data). Reads: §1, GT2, `PROTOCOLS.md` §X11 (X12), `round5/RUN_QUEUE.md` (written by GT1).

1. The queue log ends with `queue empty; runner exits`, every ID is in the done list, and none failed. Verify
   each run record: iterations, seed, held-out episodes, finite losses, weights present.
2. Check each frozen script's SHA-256 against its ledger entry; run them unchanged; append the exact returned
   readings to the ledger and write the status lines.
3. Stages (`NEEDS_WEIGHTS`), keys, an addendum to `READINGS.md` (at most 500 words). No paper edits. Commit.

### G13 — Rewrite: the uncertainty section, around three gaps (Opus 5.5, high)
Closes: RV11, RV12, RV14, RV15–RV17 (text), RV19 and RV23 (this section), RV24–RV26, RV28 (this section),
RV29–RV31, RV33 (framing), RV42, RV43 (this section).
Reads: §1, G13, `OUTLINE.md` for this section, `READINGS.md`, `CROSSWALK.md` §RWM-U, and the template's §6 by ranges.
Subagents: `rwm-checker`, one, at the end, on the new section against its artifacts.

The review: "'33.4× too small at h = 100' combines: one-step versus accumulated error … epistemic versus total
uncertainty … residual one-step miscalibration on held-out data. This is the number that matters for the penalty's
actual job … MOPO's penalty is meant to bound one-step model error at visited states … so 'no single λ fits' and
'deep-rollout states are under-penalised' don't follow from the horizon curve … Testing the original's trend claim
against accumulated error is legitimate … The problem is reading the resulting ratio as a calibration failure of the
penalty … restructure §6 around the three gaps and lead with the third."

1. **What is claimed, and what the code computes**: quote RWM-U v1 §4.1 on the learned variance capturing aleatoric
   uncertainty (the claim the σ-collapse subsection tests), and §5.1 on disagreement following the error's trend; credit the shared
   recurrent feature extractor to the original; the code's discard of the aleatoric term.
2. **The held-out one-step gap (the review's third, and the lead).** The held-out h = 1 calibration of our
   ensembles (n = 20 from X11 if run, else n = 4 with exact tests, plus the independent ensemble at n = 20 from X9(d));
   X10's in-sample reading; the released checkpoint's in-sample h = 1 figure with N12's provenance statement and
   both readings if provenance is uncertain; CRPS beside coverage.
3. **The epistemic-versus-total gap: what an ensemble can and cannot see.**
   In a near-deterministic simulator one-step error is mostly
   model inadequacy, which ensemble spread does not estimate (Abbas et al.; N14 if kept); the shared trunk as the
   original documents it, with the measured consequence as the contribution (one hidden state fed the ensemble
   mean; the share of shared parameters; independent members' better calibration, which bounds the sharing effect
   rather than isolating it); Osband et al. as the precedent and the remedy; the "bootstrap" paper-code difference,
   pointing to App. O.
4. **The one-step-versus-accumulated gap.** The original's trend claim tested against accumulated
   error, which is legitimate; why that ratio is not a calibration failure of the penalty; then X9: does propagating
   each member on its own predictions make the spread track accumulated error? MEAN is the method as released,
   per-member propagation is what the ensemble's information would give. Say plainly what X9 settles about
   "effectively propagated over long horizons".
5. **Why the per-member σ collapses**: "the objective's optimum is σ = 0" (a per-step derivation; the fed-back
   sample is a second pathway, and the teacher-forced arm's identical rate suggests it does not matter); the floor
   "gets no gradient from the bound term" (it drifts, 5.2× slower, under the state loss); the synthetic test; the
   rate as an Adam property, with only the sign flip speaking to the objective (N13); the PETS survey as "13
   repositories inspected, 10 implement the bounded head, 1 optionally trains it on sampled squared error"
   (counts from G5).
6. **Ranking**: disagreement against the free signals with Spearman as the headline (Y8), the pre-registered
   Pearson verdicts named as such, X6 with both its scopes, and M-43 as inconclusive (the direction held at every
   horizon; the paired interval excluded zero at one of four, short of the pre-registered majority, at n = 4).
7. **Per-horizon recalibration, as split conformal**: a σ-normalised score with one quantile per horizon; the
   finite-sample guarantee needs exchangeable calibration units (episodes, not steps), and coverage then lies
   between 1−α and 1−α+1/(n+1), so a 10-point band needs at least 9 calibration episodes; X7's units are all
   training episodes of the released checkpoint, so its guarantee is for in-sample use (locked framing);
   ±2σ coverage and CRPS under rescaling from N9, with the short-horizon tail shortfall; M-65's withdrawn reading in
   one sentence (pointing at App. M and App. E).
8. Neutral headings; "too small by" only as Y7 defines it; exact p beside every n = 4 interval; each result once.
   `rwm-checker` on the new section; verify each mismatch it reports yourself. Fast build and gates; commit.

### G14 — Rewrite: defects, lessons, limitations, conclusion, statements; reach 12 pages (Opus 5.5, medium)
Closes: RV01 (the budget), RV25 (§7.5), RV40, RV43; the summaries for everything.
Reads: §1, G14, `OUTLINE.md` for these sections, `READINGS.md`, `DECISIONS.md#Y10`, and the template's §7–§12 by ranges.

The review: "Compress §5.2, §5.3, §7.4 and §7.5, and recast Figure 4 and §7.5 around Adam … recast §7.5's 'clock'
as Adam's per-step bound (Kingma & Ba, 2015, §2.1), which is a cleaner argument than a rate fitted on 22 runs …
Upstream report. Say whether you reported the action misalignment upstream, and what came back … Tone. Some
headings read as adversarial … Neutral wording costs nothing with reviewers who may be the original authors."

1. **Defects**: the stale action and the unmarked episode boundaries with their line-level fixes; evaluation on
   training data; the spliced windows' cost (§7.4) in one sentence; the variance state (§7.5) in two, as Adam's
   per-step bound with the worst case from N13; the upstream report's status (Y10).
2. **Lessons for practitioners** and **limitations**, updated for this round's findings (one robot, gait, terrain and
   dataset; no trained policy; the two-episode held-out pair; X5 not run, with its reason).
3. **Conclusion** and the statements: a broader-impact statement only if the outline keeps one.
4. **The budget pass**: build, read the `pages` gate, and cut until main content is at most 12 pages, moving text to
   an appendix or the supplement, never out of the record. If 12 cannot be reached without a result leaving the
   record, stop `BLOCKED` with the three largest sections and the options.
5. Rule-10 audit of every summary site, in the log. Fast build and gates; commit.

### G15 — Appendices: standalone A–O (Opus 5.5, medium)
Closes: RV06, RV09 (App. D), RV12–RV13 and RV39 (App. O), RV24 (App. M), RV25 (App. J), RV27 (App. F); RV03 and
RV05 in the appendices. Reads: §1, G15, `OUTLINE.md` §appendices, `READINGS.md`, `CROSSWALK.md`, and each current
appendix by ranges as you rewrite it.

1. Rebuild the appendices to `OUTLINE.md`'s plan (Annex 4 proposes A–O). Each opens with one or two sentences: what
   it holds and which main-text claim it supports. No revision history (it goes to BUILD_CHECKS); no prose that
   restates the main text.
2. App. D holds the claims of the originals and the version crosswalk. App. E holds every rule with its plain name,
   ID, commit label, lead time and verbatim verdict, the old Figure 1, and X8's re-scoring. App. O, the paper-code
   differences, carries C-09 as corrected, the bootstrap difference, and Table S8.
3. Appendix tables keep full precision; their prose follows Y3's ID policy.
4. Fast build and gates after each appendix; `xref_sweep.py` 0 suspect; `keys` 0 missing; commit per appendix.

### G16 — Fresh-eyes review (Opus 5.5, high; new terminal)
Closes: verifies every item in Annex 1. Reads: §1, G16, Annex 6. Read no log entry but the last.
Subagents: `rwm-referee` once; `rwm-checker` twice.

1. Build; extract the main text (pages 1 to the page before References) to `round5/body.txt` with pypdf; read it
   once in chunks of about 300 lines, looking for a summary stronger than its section, a number without its scope,
   an internal label, and anything a newcomer cannot parse.
2. `rwm-referee` reads `round5/body.txt` only and answers TMLR's two questions (are the claims supported by
   accurate, convincing and clear evidence; would some of TMLR's audience care) as a reviewer and as the venue's
   soundness review would. `rwm-checker` 1 takes Appendices A–H and `rwm-checker` 2 takes I–O, each with the
   artifacts its sentences cite, returning mismatches only.
3. Verify every finding yourself. Fix items of three sentences or fewer; anything larger means `BLOCKED` with the list.
4. Write `round5/REVIEW.md` (pass or fail for each item of Annex 6 and Annex 1, with file:line) and
   `round5/CONSISTENCY.md` (front-matter sentence | body anchor | every reading | agrees?).
5. Once every round-5 gate passes, switch `round5_gates.py` from `--report` to blocking in FILE_MAP §3. Fast build
   and gates; commit.

### G17 — TMLR recheck, freeze, measure, package (Opus 5.5, medium)
Closes: RV44 (draft), RV45, the venue checks behind RV01. Reads: §1, G17; round 4's F11 entry in
`round4/SESSION_LOG.md` (the recipe), `round4/TMLR_CHECK.md`.

1. **TMLR recheck** in a browser or by fetch, into `round5/TMLR_CHECK.md`: the Author Guidelines, the Reviewer
   Guide's 12-page line, the Editorial Policies (LLM use, quotas, competing interests), the OpenReview form's fields
   and limits, and the blog since 15 Oct. If anything changed that affects the package, stop `BLOCKED`.
2. **Freeze**: from here, no prose edits except the reproducibility figures and the step-5 documents. Regenerate
   the claims audit (ruling U5 stands).
3. **Measure and restate** as F11 did: up to three clean clones of the local `presubmission5` (never a push), a fresh
   venv, `reproduce.sh --quick --force`, the verifier three times byte-identically, 0 scientific differing values;
   restate the reproduction figures from the measurement.
4. **Bundles**: rebuild both; the builder scan and the independent deny-list sweep find 0 hits in both zips, the
   PDF and `docs/SUPPLEMENT.md`.
5. **Package**: `docs/SUBMISSION_PACKAGE.md` in full (sizes, SHA-256s, title, abstract, counts, "Regular
   submission" if main content is at most 12 pages); `docs/COVER_STATEMENT.md`; the round-5 section of
   `docs/SUBMISSION_CHECKLIST.md`; the competing-interests text for the form (Y11); `round5/OUT_OF_SCOPE.md`
   carried forward.

### G18 — Clean-clone verification (Sonnet 5.5, medium) — last; no edits
As round 4's F12: clone the local `presubmission5` HEAD into `/Users/Shared/rwm_verify/r5/G18/` with a fresh venv;
copy and adapt round 4's driver (`/Users/Shared/rwm_verify/evidence/R4F12/f12_driver.zsh`) into
`/Users/Shared/rwm_verify/evidence/R5G18/`; run `setup.sh`, `reproduce.sh --quick --force`, the verifier three
times, the full build and every gate, both bundles and the deny-list sweep, and the PDF comparison.
Criteria: 0 scientific differing values; every reproduction figure the paper prints equals what the clone
measures; the PDF equals the committed one after blanking dates and ID; 0 deny-list hits; every round-5 stage runs
or skips as designed; every round-5 gate passes. Write `round5/FINAL_REPORT.md` with pages, main-content pages,
body and abstract words and every gate against G0, and the upload files' SHA-256s. On any failure: no fixes; stop
`BLOCKED`; the user runs "G17-fix" on Opus, then G18 again. The log entry lists §0.5's after-G18 steps.

---

## Annex 1 — Every review item, where it is fixed, and how G16 checks it

"Data" is the session that produces the evidence; "Text" the one that writes it in.

| RV | The review says | Fix, as this plan applies it | Data | Text | G16 checks |
|---|---|---|---|---|---|
| **1. Clarity and length** ||||||
| 01 | Main text about 26 pages; target 12–15 | ≤ 12 main-content pages (Y1) | G0, G6 | G8, G11–G15 | `pages` gate ≤ 12 |
| 02 | Abstract about 320 words, about 20 numbers, capitalised verdicts, unparseable phrases | About 200 words, ≤ 5 numerals, plain words (Y2) | G6 | G8, G11 | `abstract` gate; referee reads it cold |
| 03 | Internal identifiers and labels in the body | None in the body; IDs in App. E (Y3) | G6 | G9–G15 | `ids` gate = 0 |
| 04 | Results recur verbatim with their hedges | One home per result; cross-references elsewhere | G6 | G8, G11–G15 | `once` gate = 0 |
| 05 | Too many significant figures | `{{key\|s2}}` in the body | G6 | G11–G14 | `sig` gate = 0 |
| 06 | Appendices are revision history | Standalone appendices; history to BUILD_CHECKS | — | G9, G15 | no "stood there as follows" in the PDF; each appendix opens with its purpose |
| 07 | Figure 1 is pre-registration lead times | Figure 1 shows a finding; the timeline to App. E | — | G8, G10 | the figure map |
| 08 | Process detail belongs in the supplement | Queue logs, CPU overlap, history rewrite, gate mechanics → `docs/SUPPLEMENT.md` | G6 | G9, G14 | grep of the body for them = 0; present in the supplement |
| **2. The originals' current versions** ||||||
| 09 | Crosswalk to the versions of record; test the published text; "effectively propagated" | Crosswalk v1 → current arXiv and the workshop versions, named accurately; the changed claims tested as now written | G1 | G11, G13, G15 | `version_crosswalk.json`; App. D |
| 10 | Reference 2 pairs v1 with a later title | v1's title for the tested version; the current version and venue beside it | G1 | G7 | the reference list |
| 11 | §6.1 understates the aleatoric claim | Quote RWM-U v1 §4.1 (verified wording) | G1 | G13 | the quotation's crosswalk entry |
| 12 | The shared trunk is documented; "bootstrap" may be a paper-code gap | Credit the design; the measured consequence is the contribution; App. O row if no per-head resampling | G1, G5 | G13, G15 | ledger entries; App. O |
| 13 | C-09 may not be a gap | Corrected or withdrawn from both papers' tables | G1, G5 | G15 | ledger; App. O |
| **3. Three gaps in the calibration headline** ||||||
| 14 | "33.4×" mixes one-step versus accumulated, epistemic versus total, residual one-step miscalibration; lead with the third | §5 rebuilt around the three gaps; the trend claim tested legitimately; "no single λ" and "under-penalised" dropped as calibration claims | G5 | G8, G13 | section structure; rule-10 audit |
| 15 | Run per-member (TS∞) propagation on the released checkpoint | X9, on the released checkpoint and three sets of our models | G2, G3 | G13 | X9's artifact and stage |
| 16 | "In-sample biases toward better calibration" is unsafe | X10, within the same models | G2, G3 | G13 | X10's artifact; the sentence matches its verdict |
| 17 | State that the checkpoint trained on these rows | N12; both readings where provenance is uncertain | G4, G5 | G13 | the provenance sentence and its evidence |
| **4. Inference at n = 4** ||||||
| 18 | Lead §5 with X3 | X3 first; the 10,000-iteration factor as support | — | G8, G12 | section order |
| 19 | Exact randomisation p beside every n = 4 bootstrap | N7; the two-episode caveat | G4 | G12, G13, G15 | every n = 4 interval in the body has its p |
| 20 | Reuse X3's folds for the held-out calibration experiments | X11 if Y5 is B or C; X9(d) either way | GT1, GT2 | G13 | X11's artifacts, or the stated n = 4 limits |
| **5. Weak tests** ||||||
| 21 | §5.2 tests an unconverged budget | One paragraph (Y6) | — | G12 | word count; wording |
| 22 | §5.3's baselines are untuned | "Consistent but weak", with floors (Y6) | G4 | G12 | wording; floors present |
| 23 | Labels read as negative findings ("DOES NOT GENERALISE") | "Inconclusive" in the body; the verbatim label in App. E | — | G12, G13 | `ids` gate; App. E |
| **Technical corrections** ||||||
| 24 | (a) M-65 reads the tails backwards; report ±2σ under rescaling | N8 and N9; the `S-` withdrawal | G4, G5 | G13, G15 | ledger PASS; App. M |
| 25 | (b) The rate is an Adam property; plot σ; recast §7.5 | N13; Figure 4 recast; §7.5 as Adam's bound, worst case included | G4 | G10, G13, G14 | Figure 4; the §6 sentence |
| 26 | (c) "Too small by" has two meanings | One meaning (Y7) throughout | G5 | G11, G13 | grep "too small by" |
| 27 | (d) nRMSE's floor is not 1.0; add the mean and seasonal-naive floors | N10; corrected definition; floors in the long-horizon tables | G4 | G11, G12, G15 | App. F; the tables |
| 28 | (e) Ranking claims need rank correlation | N11; Spearman as the headline, Pearson verdicts named (Y8) | G4 | G11, G13 | §3 rationale; §5 |
| 29 | (f) The floor does not "freeze" | "No gradient from the bound term" | — | G13 | wording |
| 30 | (f) "Provably drives σ to zero" | "The objective's optimum is σ = 0", with the pathway caveat | — | G11, G13 | wording |
| 31 | (f) The PETS survey count is circular | "13 inspected, 10 implement, 1 optionally trains" (counts verified) | G1, G5 | G13, G15 | the counts' keys |
| **Missing related work** ||||||
| 32 | Multi-step model training | DaD, scheduled sampling, Talvitie, Lambert et al. | G7 | G11, G12 | references; §2 and §4 |
| 33 | Conformal prediction | Three references; §5's recalibration framed as split conformal | G7 | G11, G13 | references; §5 |
| 34 | Shared-torso RL ensembles | Osband et al. 2016, 2018 | G7 | G11, G13 | references |
| 35 | RL evaluation statistics | Agarwal et al. 2021; Henderson et al. 2018 | G7 | G11 | references |
| 36 | Pre-registration in ML | The NeurIPS 2020–21 workshops | G7 | G11 | references |
| **Smaller points** ||||||
| 37 | "Verified" in the title | Title names the scope (Y9) | — | G8, G11 | title |
| 38 | "First we are aware of" | Removed | — | G11 | grep = 0 |
| 39 | Table S9 should be S8 | Corrected (verified) | G1 | G15 | App. O |
| 40 | Say whether the misalignment was reported upstream | The date and the reply, or "not reported" (Y10) | you | G14 | §6 |
| 41 | Explain the clean-clone gate's three values or drop it | One sentence; the accounting in the supplement | — | G9, G11 | the reproducibility statement |
| 42 | Add a proper scoring rule | CRPS and Gaussian NLL beside coverage (N9) | G4 | G13 | §5; App. M |
| 43 | Adversarial headings | Neutral wording | — | G11–G14 | headings |
| 44 | Declare the conflict of interest | On the form (Y11) | — | G17 | `SUBMISSION_PACKAGE.md` |
| 45 | MLRC timing | Past; nothing to do; a tight version is what earns the Reproducibility Certification | — | G17 | `SUBMISSION_VENUE.md` |
| 46 | (implied) the methods the fixes rely on | Cameron et al. 2008; Kingma and Ba 2015; Chua et al. 2018; Yu et al. 2020 cited where used | G7 | G11–G13 | references |
| **What the review praises, which the rewrite must keep visible** ||||||
| K1 | Gradient-level equivalence before training | §3 sentence + App. A | — | G11, G15 | present |
| K2 | Statistical discipline (arenas, independent units, permutation nulls, withdrawn P-values) | §3's protocol paragraph | — | G11 | present |
| K3 | §6.3's σ = 0 derivation and the synthetic test | §5's mechanism subsection | — | G13 | present |
| K4 | The free baselines for the trust metric | §5's ranking subsection | — | G13 | present |
| K5 | Two pipeline defects with line-level fixes | §6 | — | G14 | present |
| K6 | The pre-registration record and the kept retraction | One paragraph in §3; App. E | — | G11, G15 | present, briefly |

---

## Annex 2 — Round-5 rules X9–X11 and post hoc analyses N7–N14

G2 turns these skeletons into `round5/PROTOCOLS.md` and may tighten them, never loosen them.

### X9 — Does propagating each member on its own predictions make the spread track accumulated error? (inference; pre-registered)

**Why.** RWM-U's current abstract says uncertainty is "effectively propagated over long horizons". The released
rollout feeds the ensemble mean to every head through one recurrent state (§6.4), so the spread at step *t* is a
one-step spread at a shared state.

**Models and arenas** (all exist; no training):
- (a) the released checkpoint, on all ten episodes' 20 non-overlapping 400-step trajectories (in-sample for it);
- (b) Arm A's three ensemble-5 arms (seeds 0–2, 2,500 iterations), on the held-out pair's 4 trajectories;
- (c) the independent ensemble (Arm A seeds 0–4), on the held-out pair;
- (d) one three-member independent ensemble per X3 fold (Arm A seeds 0–2, 2,500 iterations), each on its own fold's
  held-out trajectories: 20 trajectories, each of the ten episodes held out once. Three members are not five, and a
  small ensemble's spread is biased low; so also report (c)'s three-member subset (seeds 0–2) beside the
  five-member (c) on fold {1, 8}, which shows what the member count alone does.

**Two propagation modes.** MEAN is the released protocol: every member receives the ensemble mean. PER-MEMBER
(TS∞ in Chua et al.'s terms): member *k* receives its own previous prediction throughout, with its own recurrent
state; a shared-trunk model runs its trunk once per member, with MEAN's batch shapes so that float32 rounding
matches. Deterministic: the per-member σ has collapsed (record its size beside the error's).

**Statistics** at h ∈ {1, 8, 32, 100, 128, 368}, cumulative over steps 1..h, with the existing code's per-dimension
handling, action offset and degrees of freedom: error *e* = members' mean − truth; spread *s* = the standard
deviation across members; ρ = mean|e| / mean(s); ±1σ and ±2σ coverage; Gaussian CRPS and NLL with scale *s*.
Primary horizon h = 100; also report 368. The fraction of the gap closed:
f = ln(ρ_MEAN / ρ_PER) / ln(ρ_MEAN / 0.7979).

**Intervals.** (a) and (d): a paired bootstrap over trajectories (both modes recomputed in each draw), 20,000
draws, `default_rng(0)`. (b) and (c): an exact sign-flip test on the four per-trajectory log-ratios (minimum
p = 0.125) and "k of 4"; descriptive only.

**Verdict**, per model and arena, at h = 100:
- **PROPAGATION CLOSES THE GAP**: ±1σ coverage under per-member propagation lies within X7's band [58.27%, 78.27%];
- **PROPAGATION NARROWS THE GAP**: not the above, and f's paired interval excludes 0 (n = 20), or f > 0 on 4 of 4
  trajectories with its exact p (n = 4);
- **NO CLEAR CHANGE**: otherwise.

**Assertions**, before any per-member number is computed: (i) MEAN through the new code reproduces the existing
artifacts' ρ and coverage at every horizon: `task_d_nind20.json`/`m65_gaussian_nominal.json` for (a),
`task_d3_ens5.json` for (b), `r2_independent_ensemble.json` for (c), to 1e-6 relative; (ii) at h = 1 the two modes
are identical; (iii) for (d), a one-member "ensemble" reproduces each seed's held-out relative-L1 in
`results/x3_cross_fold.json` at every horizon, rolled out with X3's own batching (four trajectories per batch; at
h = 368 batching alone can move values by about 1e-2, round 4's OUT_OF_SCOPE F2).

**Scope sentence (locked).** Per-member propagation is not the released method. MEAN tests "effectively propagated"
as the release does it; PER-MEMBER asks whether the ensemble's information would propagate if the members were
rolled out separately.

### X10 — Does measuring on training data flatter an ensemble's calibration? (inference; pre-registered)

**Models**: Arm A's ensemble-5 arms, seeds 0–2, trained on episodes {0, 2, 3, 4, 5, 6, 7, 9}. **Arenas**:
in-sample, the 16 non-overlapping 400-step trajectories of those episodes; held-out, the pair's 4. MEAN mode.
**Statistic**: Q(h) = ρ_in(h) / ρ_out(h), per seed and pooled as `task_d3_ens5.py` pools; intervals from
independent bootstraps of each arena's trajectories, 20,000 draws. Primary h = 1; also 100.
**Verdict at h = 1**: IN-SAMPLE FLATTERS (Q < 1 in 3 of 3 seeds and the pooled interval below 1); IN-SAMPLE IS WORSE
(Q > 1 in 3 of 3 and the interval above 1); MIXED otherwise.
**Caveat (locked)**: the arenas differ in episodes as well as in training status, and per-episode difficulty varies
threefold (D-12), so this bounds the in-sample effect rather than isolating it. X11, if run, measures it with every
episode in both roles. **Assertion**: the held-out arm reproduces `task_d3_ens5.json` at every horizon to 1e-6.

### X11 — The ensemble experiments on X3's folds (training; pre-registered; only if Y5 is B or C)

**Runs**: Arm A ensemble-5 on X3's four new folds, seeds 0–2 (12 runs), and Arm A single models, seeds 3–4, on the
same folds (8 runs), at 2,500 iterations, through the round-4 queue mechanism. With fold {1, 8}'s existing runs,
every fold then has three ensemble-5 arms and five independent members.
**Readings** (each its own frozen script; statistics, thresholds and branches copied from the discharged rule,
with only the arena changed to the five folds' 20 held-out trajectories):
- X11a, held-out ensemble-5 calibration by horizon at n = 20, and X10 with every episode both in and out of sample;
- X11b, M-43's comparison of disagreement with the forecast-step index;
- X11c, the per-horizon recalibration on episodes the model never saw: the existing "fit on one held-out episode,
  score on the other" protocol, applied per fold and pooled;
- X11d, M-44's comparison of independent members with the shared trunk;
- X9's per-member propagation on the fold ensemble-5 arms.

(C adds X12: M-68's combined arm and M-49's capacity-matched arm on the folds.)

### Post hoc analyses (each its own script, artifact, stage and ledger entry; none changes a verdict)

- **N7, exact randomisation tests at n = 4.** For every paired comparison the paper reports at n_independent = 4
  with a bootstrap interval (G2 lists them from `a1_ab_by_horizon`, the sweep and baseline verdicts, `x4`, `r2_*`,
  `m49`, `task_d3_ens5` and `alignment_defect_ci`): the two-sided sign-flip test over all 16 sign assignments of the
  per-trajectory differences, seeds averaged within trajectory first (never seed × trajectory, M-27), with p and
  "k of 4"; a note that at the episode level (2 units) no test is possible. For the 20-trajectory arenas, the
  exact episode-level test (1,024 assignments). Where per-trajectory values are not stored, recompute them through
  the existing scorer and assert that it reproduces the stored interval exactly.
- **N8, the tails, correcting M-65.** From `m65_gaussian_nominal.json` (no new rollout): ±1σ and ±2σ coverage under
  mean-matching for all 48 cells; each cell's signature (±1σ over and ±2σ under: heavy-tailed; the reverse:
  light-tailed; both within G2's tolerance: near-Gaussian); the coverage-matching multiplier (the 68.27% quantile of
  |e|/σ) and its ratio to the mean-matching one, from stored per-step values or a re-roll that reproduces the stored
  coverages exactly.
- **N9, scoring the per-horizon recalibration.** Under X7's leave-one-episode-out multipliers (its fit reused
  exactly, asserted to reproduce X7's ±1σ coverage) and under the single constant: ±2σ coverage, Gaussian CRPS and NLL,
  and mean interval width, before and after rescaling, per horizon.
- **N10, floors.** State nRMSE's definition from `src/rwm_metrics.py`; add the form divided by the RMS of the
  per-dimension σ; score three predictors that use no model on every long-horizon table's arenas and horizons: hold
  the last state (the existing floor), the training mean, and seasonal-naive (repeat the last full gait cycle, its
  period fixed from the training episodes' joint-position autocorrelation and written into the script before any
  held-out scoring).
- **N11, rank correlations.** Spearman and Kendall τ_b beside every Pearson ranking statistic (§6.6's table, the
  within-rollout statistic, the free baselines, X6's short units), on the same units with the same bootstrap; rank
  partial correlations where the paper reports partials. Descriptive.
- **N12, the checkpoint's provenance.** Source evidence: the release's configured data path, any dataset hash or
  metadata in the checkpoint file, its tag and iteration, and what the first author's correspondence says. Data:
  the released checkpoint's one-step error on all ten episodes beside our arms' in-sample and held-out one-step
  errors, same metric. Output: what is known, and which numbers change role (in-sample ↔ held-out) under each reading.
- **N13, Adam.** The optimiser, learning rate, β's, ε and weight decay with file:line in `rsl_rl_rwm` and
  `scripts/step5_train.py`; the distribution of `collapse_fit.rate_over_lr` over every run; Kingma and Ba's §2.1
  bound with those β's, typical (about lr) and worst case (lr·(1−β1)/√(1−β2)); §7.5's reachability argument redone
  under each; σ's trajectory for Figure 4 from the logged bounds and the saved checkpoints.
- **N14 (optional), how much one-step error the ensemble can account for.** At h = 1 on held-out data, E[e²]
  against (1 + 1/K)·E[s²], per model; descriptive.

---

## Annex 3 — Target outline and page budget (a proposal; G8 decides)

About 6,000–7,000 body words with three figures and three tables fit 12 pages of the TMLR template (the current
body runs at about 685 words a page, floats included).

| New section | Pages | Words | Floats | Holds |
|---|---|---|---|---|
| Title, abstract | 0.4 | 200 | | |
| 1 Introduction | 1.6 | 800 | Figure 1 | the question, the findings in plain words, ≤ 4 contributions |
| 2 Background and related work | 1.0 | 550 | | RWM and RWM-U; MOPO's penalty; multi-step training; ensembles and shared torsos; calibration and conformal; RL statistics; pre-registration |
| 3 Setup | 1.6 | 800 | Table 1 | the reimplementation and its equivalence; data, episodes, arenas and n; metrics and floors; the statistical protocol; pre-registration in one paragraph |
| 4 The base paper's claims | 2.0 | 900 | Table 2 or Figure 2 | training on rollouts versus teacher forcing, led by X3; configuration; architecture |
| 5 The follow-up's uncertainty | 3.8 | 1,800 | Figure 3, Table 3 | what is claimed and computed; the three gaps; why σ collapses; ranking; recalibration |
| 6 Defects in the released pipeline | 0.5 | 300 | | stale action; unmarked boundaries; evaluation on training data; the upstream report |
| 7 Lessons and limitations | 0.8 | 450 | | |
| 8 Conclusion; statements | 0.3 | 180 | | reproducibility in one sentence; data and code |
| **Total** | **12.0** | **≈ 6,000** | 3 + 3 | |

**Figure 1 (proposal).** Two panels. (a) Training on the model's own rollouts against teacher forcing at h = 368, one
interval per held-out episode across X3's five folds (the base paper's claim, out of sample). (b) The error-to-spread
ratio by horizon on a log scale, with the calibrated value 0.80 marked: the released checkpoint under MEAN, our
held-out ensembles under MEAN and under per-member propagation. One figure that says what the paper found about
each original.

**Abstract (a sketch of the register, not a draft; G8 writes the real one from `READINGS.md`).** "We reproduce the
dynamics model of the Robotic World Model (RWM) and the uncertainty its follow-up, RWM-U, uses as a reward penalty,
matching the released module's outputs and gradients before training. RWM's central claim, that training on the
model's own rollouts beats teacher forcing at long horizons, holds out of sample: it favours rollout training on each
of ten recorded episodes held out in turn, and reverses at one step. RWM-U's ensemble disagreement ranks error well
but understates it. We separate three gaps: on held-out data the one-step spread is too small by a factor of about
[k]; an ensemble that shares its recurrent trunk cannot see uncertainty the trunk does not carry; and because the
release feeds the ensemble mean through one hidden state, the spread does not grow with accumulated error, which
[per-member propagation result]. The per-member σ collapses because the implemented objective is minimised at σ = 0.
Rescaling σ per horizon restores ±1σ coverage on training episodes, at a cost in ±2σ coverage. We also report two
pipeline defects with fixes. One robot, gait and dataset; no policy is trained."

---

## Annex 4 — Where each current section and appendix goes (a proposal; G8 decides)

| Now | Words | Goes to | Notes |
|---|---|---|---|
| Abstract | 292 | Abstract | rewritten, ≈ 200 |
| §1 | 1,216 | §1 (≈ 800) | contributions from 8 bullets to ≤ 4; ledger mechanics to App. E and the supplement |
| §2 | 817 | §2 (≈ 550) | the PETS lineage to App. J; the full version to the supplement |
| §3, §3.1, §3.2 | 1,184 | §3 (≈ 800) | metric formulas to App. F; "what each claim rests on" becomes Table 1 |
| §4 | 305 | §1 and §3 | the tested-claims list to App. D |
| §5, §5.1 | 1,520 | §4.1 (≈ 600) | X3 first; the 10,000-iteration curve and the short units to App. G |
| §5.2 | 845 | §4.2 (≈ 150) | detail and the equal-compute sweep to App. H |
| §5.3 | 917 | §4.3 (≈ 250) | detail, X4 and the RSSM to App. H |
| §6.1 | 384 | §5.1 (≈ 250) | with RWM-U v1 §4.1's wording |
| §6.2 | 1,085 | §5.2–§5.3 (≈ 700) | per-horizon tables to App. I |
| §6.3 | 561 | §5.5 (≈ 350) | gradient check, runs and the synthetic test to App. J |
| §6.4, §6.8 | 937 | §5.4 (≈ 400) | to App. K |
| §6.5 | 376 | §5.4 and §5.6 (≈ 120) | per-dimension tests to App. C or I |
| §6.6 | 1,385 | §5.6 (≈ 350) | robustness, X6 and rank correlations to App. L |
| §6.7 | 1,020 | §5.7 (≈ 300) | to App. M |
| §7 | 904 | §6 (≈ 300) | §7.2's figures to App. N; §7.4 to App. N; §7.5 to App. J |
| §8 | 464 | §3 (≈ 120) | ledger, retractions, the resampling-unit correction and reproducibility accounting to App. E and the supplement |
| §9 | 799 | §7 (≈ 300) | |
| §10 | 203 | a statement (≤ 60) or the supplement | TMLR asks for one only where there is a significant risk of harm |
| §11 | 636 | §7 (≈ 150) | the full limitations to the supplement |
| §12 | 542 | §8 (≈ 120) | the discussion to the supplement |
| Data and code | 481 | ≤ 60 | the rest to the supplement |

| Appendix now | Words | New appendix |
|---|---|---|
| A verification chain | 105 | **A** Reimplementation and equivalence |
| B reproducing | 503 | **B** Data, arenas and compute (queue logs and overlaps to the supplement) |
| — | — | **C** Statistical methods: small-n bootstraps, exact tests (N7), permutation nulls, Holm, the resampling unit |
| D claims of the originals | 1,397 | **D** Claims of the originals and the version crosswalk (with W's row) |
| E pre-registered rules | 467 + table | **E** The pre-registration record: plain names, IDs, commit labels, lead times, verbatim verdicts, the old Figure 1, Z |
| F variance-state arithmetic | 249 | into **J** |
| G metrics | 700 | **F** Metrics and floors (N10; nRMSE corrected; Y7's definition) |
| H findings not in the main text | 1,239 | the paper-code table to **O**; the rest to the supplement |
| I related work in full | 1,309 | the PETS survey to **J**; the rest to the supplement |
| J σ = 0 optimum | 1,446 | **J** Why the per-member σ collapses (with F, N13, the PETS survey) |
| K per-dimension tests | 1,533 | into **C** and **I** |
| L §5 in detail | 2,409 | **G** Rollout training against teacher forcing in detail |
| M §6.2 in detail | 1,209 | **I** Calibration in detail (with X9, X10, N14, X11) |
| N §6.6 in detail | 1,999 | **L** Ranking against free signals (with X, N11) |
| O M-44, P M-68 | 2,152 | **K** The shared trunk and independent ensembles (with M-49) |
| Q spliced windows | 278 | into **N** |
| R limitations in full | 2,117 | the supplement |
| S the conclusion's discussion | 886 | the supplement |
| T §6.7 in detail, Y X7 | 1,375 | **M** Per-horizon recalibration (with N8, N9; the conformal framing; M-65's withdrawal) |
| U settings sweep | 630 | into **H** |
| V action response | 1,141 | **N** Defects in the released pipeline (with Q) |
| W X5 not run | 151 | a row in **D**; the text to the supplement |
| X X6 | 316 | into **L** |
| Z X8 | 487 | into **E** |
| — | — | **H** Configuration and architecture claims in detail; **O** Paper-code differences |
| C what testing the untested claims needs | 637 | the supplement |

Target: appendices about 12,000 words (round 4: about 27,000). The supplement takes the rest, with its keys.

---

## Annex 5 — Files G0 creates

### `.claude/agents/rwm-reader.md`

```markdown
---
name: rwm-reader
description: Read-only fact finder for the RWM reproduction. Use when a round-5 session section names it, to locate and quote specific facts (file:line, artifact fields) in files the caller names.
tools: Read, Grep, Glob
model: claude-sonnet-5-5
effort: medium
maxTurns: 30
omitClaudeMd: true
---
You extract facts for a caller whose context is limited. Read only the files and line ranges the caller names; if
you need another file, say which and why instead of reading it. Never read whole: FINDINGS_LEDGER.md,
PAPER.template.md, PAPER.md, scripts/paper_numbers.py, scripts/check_comparative_claims.py, or any results/*.json
over 100 KB. Grep first, then read a range.

Return at most 300 words: findings, each with file:line (or artifact path and JSON key) and the exact text or value.
No advice and no summary of anything you were not asked about. If something is not there, say "not found" and
where you looked.
```

### `.claude/agents/rwm-checker.md`

```markdown
---
name: rwm-checker
description: Read-only consistency checker. Use when a round-5 session section names it, to check that every sentence in a given text range agrees with the artifacts it cites. Reports mismatches only.
tools: Read, Grep, Glob, Bash
model: claude-sonnet-5-5
effort: high
maxTurns: 60
omitClaudeMd: true
---
You check text against data. You never edit, move or delete anything. Use Bash only for read-only inspection:
python3 -c to print one JSON field, grep, sed -n, and PDF text extraction to standard output.

For each sentence in the range you are given that states a number, a direction, an arena, a sample size (n), a
horizon (h) or a checkpoint, find what it cites: the artifact, or the {{key}} in PAPER.template.md or
docs/SUPPLEMENT.template.md and that key's source in results/paper_numbers.json. Compare.

Report only mismatches, each as: location (file:line or PDF page) | what the text says | what the artifact says |
artifact path and key. At most 300 words. If there are none, say "0 mismatches" and list the ranges you checked.
```

### `.claude/agents/rwm-referee.md`

```markdown
---
name: rwm-referee
description: Fresh-eyes TMLR reviewer. Use only where a round-5 session section names it. Reads only the text it is given and reports what a TMLR reviewer or action editor would object to.
tools: Read, Grep, Glob
model: claude-opus-5-5
effort: high
maxTurns: 25
omitClaudeMd: true
---
You are reviewing a submission to TMLR (Transactions on Machine Learning Research). TMLR accepts papers whose claims
are supported by accurate, convincing and clear evidence and whose findings some part of its audience would find
interesting; novelty is not required, and reproducibility studies are in scope. You have not seen this paper before
and know nothing of its history. Read only the file the caller names.

Report, in at most 600 words, ranked by how likely each is to change an editor's decision: (1) claims the evidence
shown does not support; (2) passages a researcher in model-based RL or uncertainty quantification would not
understand on first reading; (3) results whose scope (data, sample size, checkpoint, horizon) is unclear; (4) internal
jargon, identifiers or process detail that does not belong in a paper; (5) statistics you believe are misapplied.
Quote the text you object to, with page and line. Suggest a new experiment only if a claim cannot stand without one.
```

### `.claude/agents/rwm-sources.md`

```markdown
---
name: rwm-sources
description: Source verifier for citations and for quotations from external papers. Use when a round-5 session section names it.
tools: Read, Grep, Glob, WebFetch, WebSearch
model: claude-sonnet-5-5
effort: medium
maxTurns: 40
omitClaudeMd: true
---
You verify sources. For each item the caller gives (a reference, or a quotation with the paper version it should
come from), find the authoritative record: the arXiv abstract page of that exact version, the publisher or proceedings
page, OpenReview, or a DOI record. Report the exact title, the full author list, the venue and year as the record
gives them, and the URL you read; for a quotation, whether the fragment appears verbatim, with its surrounding
sentence and its section or page. Never fill a field from memory: if you cannot read the record, report
"unverified" and why. At most 400 words.
```

### `docs/presubmission/round5/go.zsh`

```zsh
#!/bin/zsh
# Round-5 launcher: one fresh Claude Code session per section of PLAN.md.
#   docs/presubmission/round5/go.zsh G3          start session G3
#   docs/presubmission/round5/go.zsh G3 resume   resume a PARTIAL or BLOCKED G3
emulate -L zsh
set -euo pipefail
cd "${0:A:h:h:h:h}"                      # the repository root
sid=${1:?"usage: go.zsh SESSION [resume], e.g. go.zsh G3"}
typeset -A model effort
model=(G0 claude-sonnet-5-5 G1 claude-sonnet-5-5 G2 claude-opus-5-5 GT1 claude-opus-5-5
       G3 claude-opus-5-5 G4 claude-sonnet-5-5 G5 claude-opus-5-5 G6 claude-sonnet-5-5
       G7 claude-sonnet-5-5 G8 claude-opus-5-5 G9 claude-sonnet-5-5 G10 claude-sonnet-5-5
       G11 claude-opus-5-5 G12 claude-opus-5-5 GT2 claude-sonnet-5-5 G13 claude-opus-5-5
       G14 claude-opus-5-5 G15 claude-opus-5-5 G16 claude-opus-5-5 G17 claude-opus-5-5
       G18 claude-sonnet-5-5)
effort=(G0 medium G1 high G2 high GT1 high G3 high G4 high G5 medium G6 high G7 medium
        G8 high G9 medium G10 high G11 high G12 high GT2 medium G13 high G14 medium
        G15 medium G16 high G17 medium G18 medium)
[[ -n ${model[$sid]:-} ]] || { print -u2 "unknown session: $sid"; exit 2; }
plan=docs/presubmission/round5/PLAN.md
if [[ ${2:-} == resume ]]; then
  ask="Read $plan §1, the section for session $sid and docs/presubmission/round5/CHECKPOINT.md, then resume session $sid."
else
  ask="Read $plan §1 and the section for session $sid, then carry out session $sid."
fi
excl='{"claudeMdExcludes":["'"$HOME"'/Downloads/CLAUDE.md"]}'
exec claude --model "${model[$sid]}" --effort "${effort[$sid]}" --name "round5-$sid" \
  --settings "$excl" "$ask"
```

### `.claude/settings.local.json` (never committed)

```json
{ "claudeMdExcludes": ["<absolute path of ~/Downloads/CLAUDE.md>"] }
```

### The block that replaces "Finishing round 4" in `PDM/CLAUDE.md`

```markdown
## Round 5: the TMLR review of 19 Oct 2026

`rwm_repro/docs/presubmission/round5/PLAN.md` governs sessions G0–G18 (and GT1–GT2 if ruling Y5 runs them).
Each session reads PLAN §1, its own section and only what that section names. Where PLAN and round 4's workplan
(`round4/TMLR_CODEX_WORKPLAN.md`) differ, PLAN wins; round 4's locked framing still holds (PLAN §1.2 rule 11).

- **No external actions.** Commit locally. Never push, merge, upload, archive, e-mail or submit.
- **Subagents** only where a session's section names them, from `rwm_repro/.claude/agents/`. They read; they never edit.
- **New training** only as ruling Y5 in `round5/DECISIONS.md` allows, through a pre-registered queue.
- **Length** is ruling Y1 (at most 12 main-content pages), not round 4's word count.
- **Text that leaves the PDF** goes to `docs/SUPPLEMENT.template.md` or `docs/BUILD_CHECKS.template.md`; nothing
  leaves the record.
```

---

## Annex 6 — G16's checklist

1. **Gates, all blocking from now:** `pages` ≤ 12; `abstract` ≤ 210 words and ≤ 5 numerals; `ids`, `once` and
   `sig` 0; `keys` 0 missing; every round-4 gate passes; `ledger_check.py` PASS; two builds byte-identical.
2. **Annex 1:** every row's "G16 checks" holds, with evidence (file:line, key, or page).
3. **Rule 10:** every summary site agrees with every reading (`CONSISTENCY.md`).
4. **Scope:** every number in the body names, or inherits from its paragraph, its arena, n, checkpoint and horizon.
5. **Locked framing** (rule 11) wherever X3–X8, N5 or N6 is summarised.
6. **The first page** says what was found, why it matters and what a reader learns (TMLR's clear-writing criterion).
7. **Tone:** neutral headings; no priority claims; the originals' documented designs credited to them.
8. **Anonymity:** no names, no link to a named repository, model card or archive in the PDF, the ZIP or the
   supplement; the deny-list sweep passes.
9. **What the review praised** (Annex 1, K1–K6) is still visible, and briefly.
