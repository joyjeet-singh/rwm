# Pre-submission plan — RWM reproduction, TMLR

Place this file at `docs/presubmission/PLAN.md` in the repository. Every session reads §1 plus its own section, and nothing else from this file unless its section names an appendix.

Numbers quoted below were read from the paper PDF of 28 Sep 2026. Where an artifact under `results/` disagrees, the artifact wins; log the difference.

---

## 0. For the human — how to run this

**Order.** Run the sessions strictly in this order: S0 → S1 → S2a → S2b → S3 → S4 → S5 → S6 → S7 → S8 → S9 → S10 → S11. Don't start a session until the previous one has written `status: COMPLETE` in `docs/presubmission/SESSION_LOG.md`.

**Starting a session.** Use a fresh terminal each time. Don't use `--resume`, which reloads the whole old transcript and wastes tokens. Opus 5.5 needs Claude Code v2.1.280 or later; run `claude update` once first.

| Kind | Launch command |
|---|---|
| Opus, high effort | `CLAUDE_CODE_SUBAGENT_MODEL=sonnet claude --model claude-opus-5-5 --effort high` |
| Opus, default effort | `CLAUDE_CODE_SUBAGENT_MODEL=sonnet claude --model claude-opus-5-5` |
| Sonnet | `claude --model claude-sonnet-5` |

Then type:

`Read docs/presubmission/PLAN.md §1 and the section for session SX, then carry out session SX.`

**If a session stops early:**
- `PARTIAL` means it ran low on room. Launch the same model in a fresh terminal and type `Resume session SX.`
- `BLOCKED` means it needs a decision from you. Answer in `docs/presubmission/DECISIONS_FOR_USER.md`, then type `Resume session SX.`

**Training.** Runs of about 35–45 CPU-hours start in S2a and continue in the background.
- Keep the Mac plugged in. The queue runs under `caffeinate -i` so the machine won't idle-sleep.
- S3–S7 only edit text, so they can run while training runs.
- S8 waits for the queue to finish.

**Only you can do these:**
1. Send the author query after S3. The draft is in `docs/presubmission/AUTHOR_QUERY_ALIGNMENT.md`.
2. Trigger a fresh Software Heritage archive of the final pushed branch after S11.
3. Update the Hugging Face model card title, if you want it to match the paper.

| ID | Model | Effort | Scope | Rough time |
|---|---|---|---|---|
| S0 | Sonnet 5 | default | Orientation, file map, branch, record the current build status | 30 min |
| S1 | Opus 5.5 | high | Extract the original's specs; pre-register the sweep and baseline rules with power checks | 1–2 h |
| S2a | Opus 5.5 | high | M/N sweep plumbing, common-window evaluator, verdict script; launch the queue | 1–2 h |
| S2b | Opus 5.5 | high | MLP, transformer and RSSM baselines, verification ladder, verdict script; add them to the queue | 2–3 h |
| S3 | Opus 5.5 | high | Fix items 1, 2 and 4 | 1–2 h |
| S4 | Opus 5.5 | default | Fix items 3, 5 and 6; install the new title and abstract | 1 h |
| S5 | Sonnet 5 | default | Fix item 8; consistency sweep; new build checks | 45 min |
| S6 | Opus 5.5 | default | Item 7, part 1: title page to end of §5 | 1–2 h |
| S7 | Opus 5.5 | default | Item 7, part 2: §6–§13 | 1–2 h |
| S8 | Sonnet 5 | default | Check the queue finished; evaluate new runs; run the verdict scripts (no interpretation) | 1 h + eval |
| S9 | Opus 5.5 | high | Write the new results into the paper | 1–2 h |
| S10 | Opus 5.5 | high | Fresh-eyes review against Appendix E; small fixes only | 1 h |
| S11 | Sonnet 5 | default | Clean-clone verification and final report. No edits. | 1 h + CPU |

---

## 1. Rules for every session (read in full each time)

### 1.1 Scope
- Do only your session's tasks. Anything else you notice goes in `docs/presubmission/OUT_OF_SCOPE.md` as one line with file:line. Do not fix it, even if the fix is quick.
- Don't start the next session's work.

### 1.2 Integrity (non-negotiable)
1. **No hand-typed numbers.** Every measured number in the paper is bound to an artifact under `results/` through the existing substitution step (`paper_numbers.py`; path in FILE_MAP). New numbers get new keys read from artifacts.
2. **Edit sources, not outputs.** Edit the paper's source or template, never a rendered file.
3. **The ledger is append-only.** Never edit a ledger entry in place, and never change a discharged rule's verdict. A correction is a new entry that supersedes the old one and points to it. New IDs come from `scripts/ledger_check.py`.
4. **Pre-register before data.** A rule that governs new data is committed and pushed before that data exists, with a commit subject starting `PRE-REGISTER`. The script that computes the verdict is committed before the runs too.
5. **Verify against source, not config** (standing project rule):
   - Every implementation choice for new models gets a row in a deviations table: match / deviation / UNVERIFIED, each with a citation.
   - Any UNVERIFIED row blocks launching runs.
   - Data contracts are asserted before training.
6. **New citations** go only through the existing bibliography-verification pipeline (the producer of `results/t1_bibliography_verified.json`). No unverified entry.
7. **Anonymity.** The deny-list scan must pass for the paper and the bundle.
8. **Never loosen a failing check.** Fix the cause or report it; never add a tolerance or delete a check to make it pass. A check may be re-anchored when its text legitimately moves; log each re-anchor.

### 1.3 Tokens and context
- **Read narrowly.** Start by reading only: this §1, your session section, the last entry of `SESSION_LOG.md`, `FILE_MAP.md`, and any appendix of this file your section names.
- **Never read `FINDINGS_LEDGER.md` (about 510 KB) or the paper source whole.** Use `grep -n` for anchors, then Read with `offset`/`limit` around them.
- **Never print a whole JSON artifact.** Extract the fields you need with `python -c` or `jq`.
- **Keep command output short.** Send long output to a log file and show `tail -n 40`.
- **Delegate broad searches** ("every place X appears") to one Explore subagent with `model: "sonnet"`. Ask it for file:line hits and a conclusion of at most 300 words.
  - At most 2 subagents per session.
  - Never delegate edits.
- **Checkpoint when running low.** If the conversation has been compacted once, or feels heavy:
  1. finish the current item;
  2. commit;
  3. write a `PARTIAL` log entry with the exact next step;
  4. stop.

### 1.4 Session protocol
**Start gate.** The last `SESSION_LOG.md` entry must be the previous session with `status: COMPLETE`, or this session with `PARTIAL` or `BLOCKED` when resuming. Otherwise stop and say why.

**Branch and commits.** Work on branch `presubmission`, created in S0. Make one commit per item, with subject `[SX][item N] summary` (or `[SX] summary`).

**End of session:**
1. Run the fast paper build and its prose checks (command in FILE_MAP).
2. Append a `SESSION_LOG.md` entry using the template below.
3. Commit.
4. Push.

```
## SX — YYYY-MM-DD HH:MM — <model> — status: COMPLETE | PARTIAL | BLOCKED
Commits: <short hash> <subject>   (one per line)
Done: …
Build/checks: pass | fail (<which>)
Paper numbers changed: none | <old → new, key, artifact>
CPU jobs over 1 min: none | <what, how long>
Next: …
Decisions for user: none | DECISIONS_FOR_USER.md#<anchor>
```

**Stop with `BLOCKED`** and write to `DECISIONS_FOR_USER.md` when:
- a fix would change a headline number, a verdict, or an abstract claim beyond what this plan specifies;
- two artifacts disagree and you can't tell which one is current;
- a pre-registered rule can't be applied as written;
- the queue has a failed run;
- this plan says to.

### 1.5 CPU while training runs
From S2a until S8, the training queue owns the two cores.
- Other sessions may run the paper build and short scripts, each under about 10 CPU-minutes.
- No training, no full `reproduce.sh`, and no evaluation job longer than that.
- Log any job over 1 minute, so Appendix B's wall-clock figures can be qualified if needed.
- The machine has 8 GB of RAM: never run two training jobs at once.

---

## 2. Sessions

### S0 — Orientation (Sonnet 5)
Reads: §1 only.

1. **Branch.** Check the working tree is clean; if it isn't, stop with BLOCKED. Tag HEAD `pre-presubmission`, then create branch `presubmission`.
2. **Create files.** In `docs/presubmission/`, create `SESSION_LOG.md`, `DECISIONS_FOR_USER.md`, `OUT_OF_SCOPE.md` and `FILE_MAP.md`. Add `docs/presubmission/sources/` to `.gitignore`.
3. **Write `FILE_MAP.md`**, one line per entry: path, purpose, and the command where relevant.
   - paper source and templates, rendered outputs, TMLR style file;
   - `paper_numbers.py` and how a new key is added;
   - the fast paper-build command; where prose checks and assertions are registered (`docs/BUILD_CHECKS.md` and the scripts behind it);
   - `setup.sh` and `reproduce.sh` stages;
   - the training entry point, the config, the rollout/evaluation harness, `src/rwm_model.py`, the existing run drivers, and how a run records `wall_clock_s`, width and iterations;
   - where stored rollouts live; the naming convention under `results/`;
   - `FINDINGS_LEDGER.md`, `scripts/ledger_check.py`, and the next free M-, S- and R- IDs;
   - the bibliography-verification script;
   - the anonymised-bundle builder and the deny-list;
   - the generators for Appendix E, Figure 1, §3.2's claims table, Appendix B's runtime assertion, and Appendix D's classification tags;
   - the shared cluster-bootstrap function used by existing rules;
   - local copies of arXiv 2501.10100 and 2504.16680, if any.
4. **Section map.** List every heading of the paper source with its line number. Record the body (§1–§13) word count and the total word count as the "before" figures for item 7.
5. **Baseline build.** Run the fast paper build and checks once. Record pass/fail per check. Fix nothing.

Done when: FILE_MAP is complete, the baseline is recorded, and the log entry says COMPLETE.

### S1 — Original specs and pre-registration (Opus 5.5, high)
Reads: §1, S1, Appendix C, FILE_MAP.

1. **Extract the original's specs.** Write `docs/presubmission/ORIGINAL_SPECS.md` from arXiv 2501.10100v1, and from v2's Appendix A.4.1 where §IV-C moved. Give a page, figure or table reference for each item, plus a short verbatim phrase (under 15 words).
   - (a) §IV-C: the exact M/N configurations evaluated; the metric and horizon behind "optimal"; the training budget; how N = 1 is defined.
   - (b) §IV-D: the MLP, RSSM and transformer baselines — architecture, size, training regime (teacher-forced or autoregressive; M; N), loss, metric, horizon, environments.
   - (c) Anything not stated: write "not stated". Never read values off plot axes.
   - Use the local copies if FILE_MAP lists them. Otherwise download into `docs/presubmission/sources/`, which is git-ignored.
2. **Arm B check.** Is the existing Arm B exactly the reference's (M = 32, N = 1) configuration? Answer from the training code path, with file:line citations, and record the answer in ORIGINAL_SPECS.
3. **Power checks**, which M-43 lacked.
   - Use existing Arm A seeds 0–2 at 2,500 iterations, held-out arena, n_independent = 4.
   - Estimate the minimum detectable effect of each paired statistic in Appendix C, at the anchor horizon and at h = 100.
   - Use the same dilution/subsampling method used for M-44 and M-49.
   - Write `results/p5_sweep_power.json` and `results/p6_baseline_power.json`.
4. **Finalise the two rules** in Appendix C.
   - Fill in the anchor horizon from 1(a) and 1(b). If it is unstated, h = 368 governs and h = 100 is reported, matching M-23.
   - Fill in the grid (Appendix C's grid, moved toward the original's where the compute cap allows), the MDEs, and the IDs.
   - Enter each rule as a ledger entry with status PRE-REGISTERED.
   - Commit with subject `PRE-REGISTER the M/N sweep and architecture-baseline rules, before the runs exist`. Push immediately; the push is a timestamp outside your control.

Done when: ORIGINAL_SPECS, both power artifacts, and both rules are committed and pushed.

### S2a — Sweep plumbing and launch (Opus 5.5, high)
Reads: §1, S2a, rule MN (grep its ID in the ledger; read only that entry), FILE_MAP.

1. **Configurable M and N.** Make M (history length) and N (forecast length) configurable end to end: window builder, training, rollout. The default stays (32, 8).
   - Differential test: at (32, 8), the new path must reproduce an existing Arm A seed-0 loss trace bitwise for the first 20 iterations.
   - Assert the episode-respecting training-window count for every config and record it.
2. **Common-window evaluator.** Every config is scored on identical forecast target rows.
   - Held-out episodes 1 and 8, two non-overlapping windows per episode, so n_independent = 4.
   - History is the M rows immediately before each window.
   - Place the windows so the longest history (64) fits.
   - Build an in-sample variant on the eight training episodes (n_independent = 16).
   - Assert n_independent per arena, and store the window start rows in the artifact.
3. **Re-score the centre.** Re-evaluate the existing (32, 8) Arm A seeds 0–2 at 2,500 iterations on the common windows. This is inference only, and it gives the centre config.
4. **Verdict script.** Write `scripts/verdict_mn_sweep.py` so it implements rule MN exactly.
   - Reuse the shared cluster-bootstrap function, with a fixed seed.
   - Output `results/mn_sweep_verdict.json`: verdict, per-config paired intervals, the four per-trajectory differences, per-episode sign counts, Holm details.
   - Unit-test every branch on synthetic inputs.
   - Commit before launching.
5. **Queue runner.**
   - `runs/queue.txt`: one run per line — arm id, arch, M, N, seed, iterations.
   - `scripts/queue_runner.sh`: runs lines in order, with the same thread settings and artifact fields as existing runs (`wall_clock_s`, width, iterations, M, N, arch).
   - Finished ids append to `runs/queue_done.txt`; failures append to `runs/queue_failed.txt` and the queue carries on.
   - Launch with `nohup caffeinate -i scripts/queue_runner.sh > runs/queue.log 2>&1 &`.
6. **Time before launching.**
   - Run a 20-iteration timing probe per new config and project the total hours.
   - Order the queue by Appendix C's priority list.
   - If the projection exceeds the cap, drop whole configs from the bottom of the list. Record the drop as a new ledger entry before launching.
7. **Confirm and record.** Confirm the first run passes 50 iterations cleanly. Write `docs/presubmission/RUN_QUEUE.md`: runs, projected finish time, and one command to check status.

Done when: the sweep queue is running and its verdict script was committed before launch.

### S2b — Architecture baselines (Opus 5.5, high)
Reads: §1, S2b, ORIGINAL_SPECS §(b), rule BASE (ledger entry only), FILE_MAP.

1. **Confirm the comparison is state-only.** From source, confirm that the RWM state prediction does not depend on the auxiliary contact/termination branch; cite file:line. If it does depend on it, stop with BLOCKED.
2. **Implement three baselines** in `src/baselines/mlp.py`, `transformer.py` and `rssm.py`.
   - Use the same interface as the RWM state pathway: inputs are the M-step state and action history; the output is the next-state mean through the same residual connection, plus the same bounded log-σ head.
   - Exclude the auxiliary heads.
   - Follow ORIGINAL_SPECS wherever it states something. Where it doesn't, match the RWM ensemble-1 state pathway's parameter count (714,164 = 636,672 trunk + 77,492 head; verify) within ±5%.
   - Record every choice in the deviations table of `docs/presubmission/BASELINE_SPECS.md`.
3. **Architecture details:**
   - **MLP:** takes the flattened M-step history. It rolls out by sliding its input window forward over its own predictions.
   - **Transformer:** a causal decoder over M tokens, with a state+action embedding and learned positions. It predicts from the last token and rolls out by appending predictions, with the context capped at M.
   - **RSSM:** a deterministic GRU state, a Gaussian stochastic latent (prior and posterior), and a decoder to the state.
     - Trained with reconstruction plus KL. Take the free-nats and balancing settings from the paper that introduced the RSSM (PlaNet, Hafner et al., ICML 2019); cite them through the verification pipeline.
     - History steps use the posterior; forecast steps use the prior, open loop.
4. **Training setup.** MLP and transformer train autoregressively over N = 8, exactly as Arm A; RSSM trains with its own objective. Everything else is shared: data windows, split, batch, optimiser, learning rate, 2,500 iterations, seeds 0–2, and the causal action alignment.
5. **Verification ladder.** For each baseline, write results to `results/baseline_verification.json`:
   - parameter count;
   - a zero-delta output equals hold-last to ≤ 1e-6;
   - memorises a single batch (loss reduction ≥ 100×);
   - the same seed gives identical first 10 losses;
   - the action-alignment assertion shared with the RWM harness.
6. **Verdict script.** Write `scripts/verdict_baselines.py` implementing rule BASE exactly. Unit-test every branch, and commit before any baseline run.
7. **Queue.** Run a timing probe, append the 9 runs to `runs/queue.txt` after the sweep, and update RUN_QUEUE.md.
   - If the baselines project above their cap, stop with BLOCKED. Never drop a baseline yourself.
   - If a baseline diverges or produces NaN in the probe, don't tune it freely. Stop with BLOCKED and the evidence; the user decides whether to pre-register a fallback.

Done when: the ladder passes for all three, the deviations table has no UNVERIFIED rows, the verdict script is committed, and the runs are queued.

### S3 — Items 1, 2 and 4 (Opus 5.5, high)
Reads: §1, S3, Appendix D, Appendix E (items 1, 2, 4), FILE_MAP.

**Item 1 — §5 contradicts its own table at h = 8.**

The table row reads +0.0485 [+0.0271, +0.0844], "yes", 10/10. The prose says the h = 8 gap is 0.008 with an interval including zero, and that the gap excludes zero "in 0 of 4" h = 8 cells. It also says "The advantage is a long-horizon phenomenon."

- **Trace every statement.** For each h = 8 statement in §5, Figure 2's caption and the base-claim contribution bullet, find its `paper_numbers` key and its artifact. Log for each: checkpoint (iterations), trajectory length, metric and aggregation, bootstrap unit, and whether it is cumulative or per-step.
- **A likely lead:** the head-to-head table at 2,500 iterations gives Arm A 0.3289 against Arm B 0.3392 at h = 8, so the prose probably describes the 2,500 checkpoint. Confirm it rather than assuming.
- **Resolve** by the first case that applies:
  - (a) Both figures are current but come from different settings. Label the setting in each place and rewrite the prose so it no longer contradicts the table. For example: "At 2,500 iterations, where M-16 was evaluated, the h = 8 gap is inside the noise; at 10,000 it excludes zero (table above). The advantage is small at the training horizon and large beyond it." Replace "a long-horizon phenomenon" to match.
  - (b) The prose comes from a superseded artifact or estimator. Rebind it to the current artifact and add a supersession ledger entry.
  - (c) The table is the stale one. Stop with BLOCKED, because the table feeds Figure 2 and the abstract.
- **Guard it.** Add a prose check: any h = 8 gap figure in §5 must either use the table's key or carry an explicit checkpoint label.
- The M-16 and M-23 verdicts are untouched.

**Item 2 — label the checkpoint on every table.**
- **Caption rule.** Every table with an Arm A, Arm B or ensemble row states the training iterations in its caption, bound from the run artifact's iterations field. This covers §5's main table, the head-to-head accuracy table, §6.2, §6.6, §6.10, §6.11 and §7.4.
- **Head-to-head caption.** Add one sentence explaining that §5's table is at 10,000 iterations (verify) and this one at 2,500. That is why Arm A at h = 368 reads 0.3582 there and 0.5856 here; bind both numbers.
- **Guard it.** Add a build check: a table containing an arm row without an iteration count in its caption fails the build.

**Item 4 — the one-step alignment defect.**
- **Compute intervals.** Use the arena the current figures use: the released checkpoint on the held-out pair, n_independent = 4. Write `results/alignment_defect_ci.json` containing:
  - per-trajectory errors under both pairings;
  - the overstatement ratio at h = 368 in nRMSE (form 1) and in relative-L1, each with a 95% cluster bootstrap over whole trajectories, with both pairings inside each draw;
  - the four per-trajectory ratios, printed as §5 does;
  - a companion computed on all ten episodes, n_independent = 20.
- **Stop conditions:**
  - If the n = 4 point estimates don't reproduce 75% and 9.5% at the printed precision, stop with BLOCKED.
  - If the n = 20 companion differs in direction, or by more than 2×, stop with BLOCKED. Don't change the headline yourself.
- **§7.2 evidence.** Add 2–3 sentences on why the convention is what the paper says. At every reset row all 12 actions are bitwise zero. A policy network with biases cannot emit exact zeros, so those zeros mark the absence of a producing action. Therefore row t records the action that produced state t. Cite the ledger entry that settled this (grep "reset row", "k = −1", "k=-1") and the artifact.
- **Where both numbers go.** In §7.2, §3.1 ("Which metric each headline uses") and the contribution bullet, give nRMSE and relative-L1 side by side, each with its interval and each naming h = 368. The n = 20 companion appears in §7.2 only.
- **Author query.** Fill in the draft from Appendix D and save it as `docs/presubmission/AUTHOR_QUERY_ALIGNMENT.md`.
  - Verify its file:line references against the pinned upstream commit.
  - Do not send it.
  - Do not add any sentence to the paper saying the author was asked or confirmed.

### S4 — Items 3, 5, 6 and the new title and abstract (Opus 5.5)
Reads: §1, S4, Appendices A and B, Appendix E (items 3, 5, 6).

**Item 3 — the per-horizon fix is tested mostly on a model that has already seen the data.**
- **Define two terms once in §6.8** and use them consistently everywhere:
  - *unseen by the multiplier*: fitted on one episode, scored on the other;
  - *unseen by the model*: never in the model's training data.
- **Say it plainly.** The released checkpoint trained on both held-out episodes, so its 12/12 is unseen-by-the-multiplier only.
- **Add the harder test to the table.** Add a row or column to §6.8's table for the same test on our ensemble-5 Arm A, where the episodes are unseen by the model: 17/36 cells for disagreement and 10/36 for the aleatoric σ. Bind these; if no key exists, compute them from the artifact behind §6.8's cross-model paragraph.
- **Rewrite each of these** to carry the caveat in at most one extra sentence:
  - the contribution bullet "A candidate repair";
  - §6.8's closing "So the accurate form…";
  - the closing references in §6.10 and §6.11 ("remains the only correction…");
  - §9's lesson "If you need the interval…";
  - §11's recalibration limitation;
  - §12's "it looks repairable" — for example, "the scale may be repairable per horizon, but on a model that has not seen the test episodes the evidence is mixed";
  - the verdict cell in §3.2's claims table.

**Item 5 — title and contributions.**
- Install Appendix A's title.
- **Reorder the contributions** so they lead with what the title names:
  1. order right, size wrong (merge the "first calibration measurement", ranking and free-baseline bullets);
  2. the base claim reproduces, and reverses at one step;
  3. the σ = 0 optimum;
  4. trunk-sharing, tested;
  5. per-horizon recalibration, with item 3's caveat;
  6. the evaluation misalignment, with item 4's two numbers;
  7. the verified reimplementation.
- At most 7 bullets, at most 3 sentences each. A number may leave the contributions only if it still appears in the body.
- Adjust the introduction's first two paragraphs so they fit the new title. No new claims.

**Abstract.**
- Replace it with Appendix A's text and bind every number listed there.
- Fill in the two alignment intervals from S3's artifact.
- If a bound value differs from the draft, use the artifact's value and log it.
- Keep it at 330 words or fewer.

**Item 6.** Replace §10 (Broader impact) with Appendix B's text, with its numbers bound.

### S5 — Item 8 and consistency sweep (Sonnet 5)
Reads: §1, S5, Appendix E (item 8).

1. **Find the occurrences.** Use one Explore subagent (`model: "sonnet"`). Across the paper source, README and supplementary docs, ask for file:line of every:
   - "order(s) of magnitude";
   - count next to "retraction", "retracted" or "superseded";
   - leftover of the old title;
   - "held-out" within 2 lines of "multiplier";
   - "75%" and "9.5%".
2. **Retraction counts.** Fix one vocabulary: claims withdrawn on evidence, framings withdrawn, and total superseded entries.
   - All three counts come from `scripts/ledger_check.py` output and are bound through `paper_numbers.py`.
   - The introduction and §8 use the same words and the same generated counts.
   - Add a check asserting the introduction's count equals §8's.
3. **Orders of magnitude.** Where a statement is not exactly true, replace it with bound ranges: the per-member σ at 1,827–20,669× and ensemble disagreement at 8.3–34.4× (verify the keys). Leave statements that are exactly true, and log each decision.
4. **Old title.** None may remain in the paper or the bundle. Change the README only if it mirrors the paper title.
5. The build and all checks pass.

### S6 and S7 — Item 7: length and self-narration (Opus 5.5)
- S6 covers the title page to the end of §5, including §5.1.
- S7 covers §6–§13, and trims appendix prose only where it narrates drafting.

Reads: §1, this section, the section map in FILE_MAP.

**Goal.** After S7, the body (§1–§13) is at least 30% shorter in words than S0's "before" count. No claim, number, verdict, table or figure is lost.

**Style rules:**
- **Move drafting history; don't delete it.** Move all drafting history out of the body into `docs/BUILD_CHECKS.md`, under the heading "Moved from the paper body (pre-submission edit)", each item labelled with its former section.
  - What moves: "an earlier draft said…", "found by the horizon sweep", descriptions of build gates, selector or glob bugs, commit-amend timings, and the history of how a check came to exist.
- **Retractions.** Keep one sentence per retraction that changed a claim, citing its ledger ID.
- **Rule IDs.** Give a rule's ID at its first mention in each section: "(rule M-23, Appendix E)". Elsewhere describe the rule in words. Remove R-, D-, X- and O- IDs from running prose; keep them in footnotes only where the evidence pointer matters.
- **State each caveat once**, where it carries weight, then refer back to it (for example, "the n = 4 caveat of §3"). Candidates:
  - 256 resamples and quantisation;
  - in-sample vs out-of-sample for the released checkpoint;
  - "not 12 independent successes";
  - "bounds what it reports, not what it costs".
- **Plain words.** Prefer plain wording, and define each technical term at first use.
- **Tables and figures stay.** Captions may shorten but must keep the arena, n_independent and the checkpoint.

**Process:**
- Go section by section: one Read with offset/limit per section. Run the checks after each section. Log words before and after per section.
- If a check fails because text moved, re-anchor it. If the text it guards moved to BUILD_CHECKS.md, point the check there, or retire it with a logged reason. Never retire a numeric assertion.
- At the end, S7 reports the final body word count against the target. If the cut is under 30%, list the largest remaining sections and stop; don't force cuts.

### S8 — Queue gate and evaluation (Sonnet 5)
Reads: §1, S8, RUN_QUEUE.md.

1. **Gate.** All of the following must hold; otherwise stop with BLOCKED and the list:
   - every line of `queue.txt` is in `queue_done.txt`;
   - `queue_failed.txt` is empty;
   - every artifact has the expected iterations, width, M, N or arch, and seed;
   - no loss trace contains a NaN.
2. **Evaluate.** Run the evaluators from S2a and S2b on every new run, in both arenas. Then run `scripts/verdict_mn_sweep.py` and `scripts/verdict_baselines.py`. Outputs: `results/mn_sweep_eval.json`, `results/baselines_eval.json`, and the two verdict files.
3. **Discharge.** Discharge both rules as new ledger entries, with the verdict exactly as the scripts return it. Commit as `[S8] discharge …`.
4. **Runtime inputs.** Update Appendix B's runtime inputs (the per-run `wall_clock_s`), not its prose. Note any run that overlapped a logged CPU job.
5. **No paper prose edits in this session.**

### S9 — Write the results in (Opus 5.5, high)
Reads: §1, S9, the two verdict artifacts, ORIGINAL_SPECS.md, BASELINE_SPECS.md.

1. **Two new sections.**
   - §5.2, "The configuration claim (M = 32, N = 8)", and §5.3, "The architecture claim (MLP, RSSM, transformer)".
   - Each is about 500 words or fewer, with one table and optionally one figure, in S6/S7's lean style.
   - Each gives: the claim as the original states it; what was run; the verdict as returned; values at h = 100 and h = 368; the hold-last floor; n_independent; and what the result does not show. The limits to state: one factor varied at a time, so no interactions; our data budget; baselines matched to our reading of the original where it is silent.
   - Call these "architecture baselines" throughout, so readers don't confuse them with §6.7's "free baselines".
2. **Head-to-head table.** Add baseline rows if they share its checkpoint and arena.
3. **Update everything generated from counts or tables:**
   - §4's tested/untested counts and lists (4 → 6 tested), through Appendix D's classification tags;
   - Appendix D's rows;
   - Appendix C: remove the two CPU rows; its "within reach" paragraph becomes history;
   - Appendix E (generated);
   - Appendix B's totals and their sum assertion;
   - §3.2's claims table;
   - §11's sentence about the two unrun claims;
   - §12's "what should travel", if affected.
4. **Contributions and abstract.** Add one contribution bullet, and at most one abstract sentence, only for a verdict that resolves (anything other than "cannot be settled/distinguished"). Otherwise mention the results only in §4 and §5.
5. **New citations** go through the verification pipeline.
6. The build and all checks pass.

### S10 — Fresh-eyes review (Opus 5.5, high)
Run this in a new terminal with nothing carried over from earlier sessions.
Reads: §1, S10, Appendix E's checklist.

1. **Write `docs/presubmission/REVIEW.md`.** Give pass/fail for every checklist item, each backed by file:line.
2. **Spot-check tables against prose.** Use up to two Sonnet Explore subagents, one for §5 and one for §6–§7. Each one reads every table and every sentence that cites it, and returns only the mismatches.
3. **Check the front matter.**
   - Every number in the abstract and contributions must appear in the body.
   - The title, abstract and conclusion must agree.
   - Every caption must carry its arena, n_independent and checkpoint.
4. **Fix size limit.** Fix only small issues (3 sentences or fewer each). Anything larger: stop with BLOCKED and the list.

### S11 — Clean-clone verification (Sonnet 5) — last; no edits
1. **Push and clone.** Push `presubmission`, then clone it into a fresh temporary directory (not the working copy).
2. **Rebuild from scratch.** In the clone, run each of these in order:
   1. `./setup.sh` (it verifies the two pinned upstream hashes);
   2. create a venv and run `pip install -r requirements.txt`;
   3. `./reproduce.sh --quick --force`;
   4. the full paper build and every check;
   5. the anonymised bundle build and the deny-list scan;
   6. render the PDF with the TMLR style.
3. **Compare with S0's baseline.**
   - Regenerated values that differ and are measurements, statistics or verdicts must number 0, the paper's current standard.
   - Report the total number of differing values.
   - Confirm `part_f_gate` fails the same way it did before (it is published as failing), not in a new way.
4. **Final report.** Write `docs/presubmission/FINAL_REPORT.md`: page count, body word count against S0, and every check with its status.
5. **On any failure:** make no fixes. Stop with BLOCKED, including the failure and its log. The user runs an Opus fix session ("S10-fix"), then S11 again.
6. **Reminders.** In the log entry, remind the user:
   - send the author query if it hasn't gone yet;
   - trigger a fresh Software Heritage archive of the final pushed state. §13's timestamp argument now needs it to cover the new pre-registrations.

---

## Appendix A — Title and abstract (for S4)

**Title (primary):** Right Order, Wrong Size: A Verified Reproduction of the Robotic World Model and the Uncertainty It Reports

**Title (alternate, if the user prefers):** Ranks but Does Not Measure: Ensemble Disagreement in a Released Robotic World Model

**Abstract:**

> We rebuild the proprioceptive dynamics model of the Robotic World Model (arXiv:2501.10100) and of its uncertainty-aware follow-up (arXiv:2504.16680) from scratch on CPU. Before any training, outputs match the released implementation bitwise, and losses and gradients match exactly. The base paper's central training claim reproduces: training on the model's own rollouts beats teacher forcing by 4.61× at 368 steps and 2.58× at 100, under a rule committed before the runs, though teacher forcing is ahead at one step. This uses 0.133% of the reference's world-model data and one robot, gait and terrain, and it rests on 4 independent held-out trajectories. The follow-up's uncertainty gets the order right and the size wrong. Ensemble disagreement, the quantity the method subtracts from reward, correlates +0.605 with realised error, and +0.419 with the rollout and the forecast depth both held fixed. Yet on data the checkpoint trained on, it is 8.3× smaller than that error at one step and 33.4× at the method's 100-step imagination horizon. Because the shortfall grows with depth, no single penalty weight absorbs it. A free signal, the model's own predicted step size, ranks error nearly as well (+0.470), and this sample cannot resolve the margin. The five members share 89% of their parameters; five independent models are 2.03× better calibrated and still 5.2× overconfident. The per-member σ, which the method discards, is driven to zero by the implemented loss; we derive this and confirm it on data with known noise. A per-horizon rescaling brings the released checkpoint's coverage within 10 points of nominal on episodes it trained on, though no single cell is resolvable. For our own ensembles, on episodes they never saw, it does so in only 17 of 36 disagreement cells: a recipe to refit, not a demonstrated fix. Separately, the released evaluation pairs each prediction with the previous step's action. At 368 steps this overstates the checkpoint's error by 75% in nRMSE [95% CI from S3] and by 9.5% in the upstream's own relative-L1 [95% CI from S3]. We train no policy, so we bound what the uncertainty reports, not what its miscalibration costs.

**Numbers to bind** (each through `paper_numbers.py`):

| Number | Source |
|---|---|
| 4.61× and 2.58× | §5 table; verify the 10,000-iteration checkpoint |
| "teacher forcing ahead at one step" | the short-unit result, −0.0194 [−0.0310, −0.0093] |
| 0.133% | data-budget artifact |
| 4 | n_independent |
| +0.605 and +0.419 | pooled and double-demeaned correlations |
| 8.3× and 33.4× | epistemic err/σ at h = 1 and h = 100, 20 trajectories |
| +0.470 | step-size baseline (+0.4697) |
| 89% | 89.15% shared parameters |
| 2.03× and 5.2× | §6.10 |
| 10 points | tolerance band around 68.27% |
| 17 of 36 | Arm A ensemble-5 cells in band, from item 3 |
| 75%, 9.5% and the two intervals | `results/alignment_defect_ci.json` |

## Appendix B — Replacement for §10, Broader impact (for S4)

> This is a reproduction of a dynamics model on public simulation data. It creates no new capability, uses no personal data and deploys nothing.
>
> The findings bear on one practice, and it is not the one the original method uses. The follow-up applies ensemble disagreement as a reward penalty. For that use, our measurements support its ordering (§6.7), with the qualification that a free signal ranks error nearly as well. A different use is reading the same number as an error bar, a safety margin, or a trigger for handing control to a fallback controller. The original papers neither make nor recommend that use, and it is the use our measurements rule out. At the method's own 100-step horizon, the disagreement is 33.4× smaller than realised error and covers 4.61% of outcomes where 68.27% is expected. We say this because the released checkpoint exposes the quantity, and it is easy to read as an interval.
>
> We do not claim the original method is unsafe. No policy is trained here. The one policy-free test we ran found that correcting the scale per horizon leaves every pairwise ordering of accumulated penalty unchanged on the available trajectories (§11).

## Appendix C — Draft rules for S1 to finalise

**Compute caps (projected CPU-hours):**
- Sweep ≤ 25.
- Baselines ≤ 20; if exceeded, stop with BLOCKED. Baselines are never dropped.
- New total ≤ 45, against the existing project total of 49.8.

**Shared settings for all new runs:** 2,500 iterations; seeds 0, 1, 2; ensemble size 1; width 256; batch 256; learning rate 1e-4; the faithful sampled-MSE objective (except RSSM's own); the existing split (held-out episodes 1 and 8).

**Sweep grid, one factor at a time around the centre (32, 8).** Priority order, highest first:

| Priority | (M, N) | Note |
|---|---|---|
| 1 | (64, 8) | |
| 2 | (32, 16) | |
| 3 | (16, 8) | |
| 4 | (32, 4) | |
| 5 | (8, 8) | |
| 6 | (32, 1) | Reuse Arm B instead if S1 finds it identical |

Move the grid toward the original's grid only within the cap. Interactions between M and N are not tested; the rule says so.

**Rule MN (draft).**
- **Claim:** the original's §IV-C statement that M = 32, N = 8 is the optimal configuration (quote it from ORIGINAL_SPECS).
- **Evaluation:**
  - arena: common forecast windows, held-out episodes 1 and 8, n_independent = 4;
  - horizons: {1, 8, 32, 100, 128, 368}, cumulative;
  - metrics: relative-L1 is primary; nRMSE form 1 is secondary.
- **Governing statistic:**
  - For each non-centre config c: D_c = err(c) − err(32, 8) at the anchor horizon, taking the 3-seed mean per trajectory.
  - Interval: a 95% cluster bootstrap over the 4 trajectories, with seeds pooled inside each draw.
  - Multiple testing: Holm across the non-centre configs.
  - Stated in advance: at n = 4, a Holm-adjusted interval excludes zero essentially only when all four per-trajectory differences share a sign.
- **Branches:**
  - **REPRODUCES, RESOLVED:** the centre has the lowest mean error, and every D_c excludes zero in the centre's favour.
  - **CONSISTENT WITH OPTIMAL:** the centre has the lowest mean error, and no D_c excludes zero in c's favour.
  - **NOT OPTIMAL AT OUR BUDGET:** some D_c excludes zero in c's favour.
  - **CANNOT BE DISTINGUISHED:** anything else, reported with its MDE.
- **Reported alongside, not governing:** the in-sample arena (n_independent = 16; every config sees the same training episodes, so the comparison is paired and fair), per-episode sign counts over the 10 episodes, h = 100 when the anchor is h = 368, and training-window counts.

**Rule BASE (draft).**
- **Claim:** the original's §IV-D statement that RWM outperforms the MLP, RSSM and transformer baselines (quote it).
- **Arms:**
  - RWM: the existing Arm A at 2,500 iterations, seeds 0–2.
  - Baselines: parameter-matched within ±5% unless ORIGINAL_SPECS says otherwise; same data, windows, iterations, batch and optimiser; 3 seeds each.
  - The existing §5 evaluation windows (400 steps, n_independent = 4).
- **Governing statistic:** for each baseline b, D_b = err(b) − err(RWM) at the anchor horizon, with a paired cluster bootstrap and Holm across the three baselines.
- **Per-baseline branches:**
  - **RWM BETTER:** the interval excludes zero with D_b > 0.
  - **BASELINE BETTER:** the interval excludes zero with D_b < 0.
  - **CANNOT BE SETTLED:** anything else, reported with its MDE.
- **Overall verdict:**
  - **REPRODUCES:** RWM BETTER for all three.
  - **DOES NOT REPRODUCE:** any BASELINE BETTER.
  - **PARTIAL:** some RWM BETTER and the rest CANNOT BE SETTLED.
  - **CANNOT BE SETTLED:** none resolves.
- **Reported alongside, not governing:** the in-sample arena (n_independent = 16), all horizons, the hold-last floor, and per-episode sign counts.

## Appendix D — Author query draft (S3 fills it in; the user sends it)

> Subject: RWM-U release — action alignment in the evaluation script
>
> Dear [first author],
>
> Thank you again for your help in August with Eq. 4 and the aleatoric term. We have one more question, about the lite release at commit [pinned hash].
>
> In training ([file:line]), the state at step t+1 is paired with the action in the same row. In evaluation ([file:line]), it is paired with the action one row earlier. Our reading of the dataset is that row t holds the action that produced state t. At all ten episode resets the twelve actions are exactly zero, which a policy network with biases would not output. Under that reading the training pairing is the intended one, and the evaluation pairing is one step stale. Scored with the training pairing, the released checkpoint's error at 368 steps is [X]% lower in nRMSE and [Y]% lower in relative-L1.
>
> Could you confirm which pairing is intended? And, as with the earlier exchange, may we quote your reply?
>
> Best regards,
> [name]

## Appendix E — Anchors and review checklist

The anchor phrases come from the rendered PDF. The source may differ in dashes, quotes, spacing and math markup, so grep case-insensitively with loose patterns.

**Item 1:**
- "What does not hold, and we say so"
- "gap of 0.008"
- "The pattern is consistent across the design"
- "0 of 4 at h = 8"
- "long-horizon phenomenon"
- "spans zero only at h = 1"
- "weakest exactly where the model is trained"
- the base-claim contribution bullet

**Item 2:**
- "0.3582"
- "0.5856"
- "How good the reimplementation is as a model"
- "weights_2500"
- every table caption containing "Arm"

**Item 3:**
- "fitted on one held-out episode"
- "A candidate repair"
- "So the accurate form of this section"
- "remains the only correction"
- "rescale per horizon"
- "fitted and tested on two episodes only"
- "looks repairable"
- "17 of 36"

**Item 4:**
- "overstates its own model's error by 75%"
- "9.5% on relative-L1"
- "disagree on action alignment"
- "Which metric each headline uses"

**Item 5:**
- the old title "What a released robotic world model's uncertainty is worth"
- "Contributions."

**Item 6:**
- "Broader impact"
- "conservative controller"

**Item 8:**
- "12 retractions"
- "Six retractions on our own evidence"
- "one to four orders of magnitude"
- "by one to two"
- "three to four orders of magnitude"

**Checklist for S10:**
1. §5 prose and table agree at h = 8, and every h = 8 figure names its checkpoint.
2. Every table with an arm row names its iterations; the 0.3582 / 0.5856 difference is explained where both appear.
3. "Unseen by the multiplier" and "unseen by the model" are used consistently. The 17/36 and 10/36 results appear in §6.8. The abstract, contributions, §9, §11 and §12 carry the caveat, and "looks repairable" is gone.
4. The alignment defect is stated with both metrics and both intervals everywhere it appears. §7.2 contains the reset-row evidence. No sentence claims the author confirmed it.
5. The new title is installed and the old one appears nowhere. The contributions lead with order-right, size-wrong, with ≤ 7 bullets of ≤ 3 sentences.
6. Broader impact matches Appendix B, with numbers bound.
7. The body is at least 30% shorter than S0's count, or the shortfall is reported. Drafting history is in BUILD_CHECKS.md. No numeric assertion was retired.
8. Retraction counts are generated and identical in the introduction and §8. No "orders of magnitude" phrase is inaccurate.
9. §5.2 and §5.3 report their pre-registered verdicts exactly as returned, and both rules were committed before their runs (check the lead times in Appendix E).
10. §4, Appendices B–E, §3.2 and §11 reflect six tested claims. The term "architecture baselines" is never confused with "free baselines".
11. Every number in the abstract and contributions appears in the body and is bound to an artifact.
