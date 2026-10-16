# Round-4 session log

One entry per session, in the template of PLAN.md §1.4. The start gate for each session is the last entry here.

## F0 — 2026-10-11 00:58 — Opus 5.5 (the plan assigns Sonnet 5.5, default effort) — status: BLOCKED
Commits:
18cc54f [F0][1] Round-4 plan, copied verbatim from the instruction file
e6e294b [F0][2] Round-4 files: session log, decisions (defaults accepted), out-of-scope list
a031531 [F0][3] Bundle exclusion dry-run: neither builder collects docs/presubmission/round4/
4fce5a1 [F0][4] Baselines: 20,745 main-text words, 62 pages (References p. 32), abstract 370/23, 59 labels in the main text; every gate passes
6b62f9c [F0][5] Preflight PF1-PF9: PF1 FAILS (no committed Arm B 2,500-iteration reference at h = 128 on §5's arena); the rest pass, PF4 records
17a36b0 [F0][4-fix] Baseline: list only files the build changed; name submission_check's outstanding C1 (ruling U5)
(the commit carrying this entry, the decision question and one out-of-scope line follows)
Done:
- **How this session ran.** On Opus 5.5 at the user's request ("please follow instructions as stated in PLAN4.md"); the plan assigns Sonnet 5.5. Both permitted Explore agents were used, read-only: a locator for PF4, PF6 and PF8, and an auditor of every F0 record. The workflow records both as running on Opus 5.5, not on the Sonnet 5.5 the launch command's `CLAUDE_CODE_SUBAGENT_MODEL` names; that variable did not reach workflow agents.
- **Item 1.** HEAD was `173f349` = `41b73ee` plus round-3 records only (`git diff --stat`: `round3/FINAL_REPORT.md` and `round3/SESSION_LOG.md`). The only untracked path was `round4/PLAN.md`, byte-identical to the instruction file. Tagged `pre-round4` (local, not pushed, as in rounds 1-3); branch `presubmission4`.
- **Item 2.** `SESSION_LOG.md`, `DECISIONS.md` (§0.2's table, defaults accepted), `OUT_OF_SCOPE.md`.
- **Item 3.** Neither bundle builder collects anything under `round4/` (`f0_bundle_exclusion.py`, which first asserts that its copy of `build_supplementary`'s loop is the one `main()` holds). The only `docs/presubmission/` files either collects are its three `SHIP_FROM_EXCLUDED` files.
- **Item 4.** `BASELINE_F0.md` (`f0_baseline.py`):
  - main text 20,745 words to "Data and code" and 21,230 to "References";
  - 62 pages, References on page 32;
  - abstract 370 words (cap 370) and 23 numerals (cap 26);
  - internal labels in the main text: M- 40, R- 6, S- 7, rule labels X1-X8 5, commit labels 1; B-, C-, D-, O- and X- none; none in the front matter;
  - 1,340 template keys, listed in `f0_template_keys.txt` for Annex 6 item 4;
  - every gate passes after one fast build; `submission_check` 21/22 with C1 outstanding by round 2's ruling U5, as known.
- **Item 5.** `PREFLIGHT.md` (`f0_preflight.py`): PF2, PF3, PF5, PF6, PF7, PF8 and PF9 PASS; PF4 recorded; **PF1 FAIL**.
  - PF1: every weight file PF1 lists is present (61 entries, 58 distinct files: the sweep's centre is Arm A's 2,500-iteration run). The released checkpoint matches `setup.sh`, and the 45 sweep and baseline files match their evaluation artifacts' SHA-256s. But no committed artifact holds Arm B's 2,500-iteration held-out relative-L1 at h = 128 on §5's four trajectories, which X3's named assertion needs. Question: `DECISIONS.md#F0-armB-2500-h128`.
  - For F1: the training driver takes no held-out argument. Each fold gives 4 independent trajectories (n = 20 pooled); {0, 2} and {3, 4} each hold two episodes from the same speed half. The matched baselines were ladder-verified teacher-forced only. M-23's three-seed bootstrap is inline, but `review_bootstrap_unit.boot_cluster` reproduces it, and it is Monte Carlo at n = 4.
  - For F2: velocity commands are not in the data, so the two tracking terms X5's gate requires have no recorded counterpart (PF4 records only; F2 decides). None of the three evaluators takes an offset, and the baselines assert offset 1.
- **Audit.** One read-only Explore agent audited `PREFLIGHT.md`, `BASELINE_F0.md` and the decision question. Verdict PASS-WITH-FIXES: seven findings, all applied (two wrong, two misleading, three imprecise); no check's result changed. It found the `step5_armB` run records (h = 128 on a different arena) and the stored per-trajectory rollouts, which now give option (B). The locator's one error, "thigh labels all 0" (one cell of 40,000 is 1), was caught by the generator, which reads the data.
- **Differences from the plan.** The main text was 20,745 words, not round 3's 20,771 (R7 reached 20,745). PF7's keys print in Appendix N (`PAPER.template.md:1842` and `:1866-1868`), not in §6.7. The penalty line is `lite/scripts/envs/base.py:166`, as the plan says.
Build/gates: pass (one fast build plus every gate, at `a031531` and again at `4fce5a1`; the build changed only `PAPER.pdf`'s timestamps, restored). No paper text edited, so no second build was required.
Paper numbers changed: none
New keys: none
Re-anchored checks: none
CPU jobs over 1 min: the baseline (fast build plus all gates), twice, about 3 min each; the locator agent, about 5 min; the audit agent, about 13 min. No training job ran, so none was contended.
Queue status: not launched
Body words (round2/t6_words.py): 20,745 (F0: 20,745)
Abstract words / numerals (C12.1): 370 / 23
Next: the user rules on `DECISIONS.md#F0-armB-2500-h128`; then F0 records the ruling, re-runs `f0_preflight.py` and writes COMPLETE; then F1 (Opus 5.5, high effort, fresh terminal, idle machine for its timing probes).
Decisions for user: DECISIONS.md#F0-armB-2500-h128

## F0 — 2026-10-11 01:00 — Opus 5.5 (the plan assigns Sonnet 5.5, default effort) — status: COMPLETE
Commits (resumed in the same conversation after the ruling):
b5ff8e7 [F0] BLOCKED: session log; decision F0-armB-2500-h128 (X3's Arm B reference at h = 128); one out-of-scope line
c1634b3 [F0][fix] Ruling (B) recorded: F1 builds X3's Arm B reference from the stored rollouts; preflight re-run, PF1-PF9 pass (PF4 records)
(the commit carrying this entry)
Done:
- **The ruling.** Asked in chat, answered 2026-10-11: option (B) of `DECISIONS.md#F0-armB-2500-h128`. Before X3's pre-registration, F1 builds a six-horizon reference for Arm B at 2,500 iterations from the stored rollouts behind `head_to_head_accuracy.json`. It first asserts that a new horizons argument's default reproduces that artifact byte-identically, and that the reference equals it at h = 1, 8, 100 and 368 and `action_sensitivity.json` at h = 32. X3's assertion then runs at every horizon, as Annex 2 words it.
- **Preflight re-run** (`f0_preflight.py` reads the ruling from `DECISIONS.md`): PF1, PF2, PF3, PF5, PF6, PF7, PF8 and PF9 PASS; PF4 recorded. PF1 passes because the stored rollouts exist, match their recorded SHA-256s and hold all 368 steps. Nothing else in `PREFLIGHT.md` changed.
- Everything else is as in the BLOCKED entry above.
Build/gates: pass (unchanged since the BLOCKED entry; no source, template or artifact was touched after it).
Paper numbers changed: none
New keys: none
Re-anchored checks: none
CPU jobs over 1 min: none since the BLOCKED entry.
Queue status: not launched
Body words (round2/t6_words.py): 20,745 (F0: 20,745)
Abstract words / numerals (C12.1): 370 / 23
Next: F1 (Opus 5.5, high effort), in a fresh terminal on an idle machine. Its timing probes run before the queue launches. Beyond PLAN F1, it carries out ruling (B) before X3's pre-registration. It reads `PREFLIGHT.md`'s notes for F1: the driver has no held-out argument; the matched baselines were ladder-verified teacher-forced only; `review_bootstrap_unit.boot_cluster` is the importable three-seed bootstrap, Monte Carlo at n = 4, so per-fold exact intervals need `action_sensitivity.draws_for`.
Decisions for user: none

## F1 — 2026-10-11 10:41 — Opus 5.5 (the plan assigns high effort, fresh terminal) — status: COMPLETE
Commits:
7bcbf52 [F1][1] Fold support for X3: step5_train --holdout via rollout_eval.fold_split (appended; no cited line moves); queue_run's x3 trainers
b729204 [F1][3] Timing probes on an idle machine: X3 23.83 h at three seeds (cap raised 22 -> 24 h by ruling F1-x3-cap), X4 6.75 h, 30.58 h in all (cap 32)
a770c98 [F1][1b] Ruling (B): X3's Arm B reference at six horizons, from the stored rollouts
5f0acd4 PRE-REGISTER X3 cross-fold replication and X4 size-matched baselines, before their runs exist
d9fb4de [F1][6] Launch: 30 runs queued at 10:36 (+0530), projected 30.58 CPU-hours, finish about 2026-10-12 17:10; the first run passed 50 iterations with a finite loss
b175e54 [F1] Build and gates after the pre-registration: n_entries 274 -> 276, ledger_kb 593 -> 609; no paper edits
(the commit carrying this entry)
Done:
- **How this session ran.** In the same conversation as F0, at the user's request ("carry out session F1"); the plan assigns a fresh terminal at high effort. The session restarted once, between items 4 and 5 ("resume"); the tree was checked unchanged before it went on. The one permitted Explore agent ran on Opus 5.5 (its workflow record), not Sonnet 5.5.
- **Item 1, fold support.** `scripts/step5_train.py --holdout a,b` takes its split from `src/rollout_eval.py`'s new `fold_split`. Without the flag the driver calls `make_split(seed=0)` as before. Runs and records are named `x3_…`, outside every `results/step5_*.json` glob the paper reads. `scripts/queue_run.py` gained the eight `x3-<arm>-<fold>` trainers, which check each record's held-out episodes. Assertions (`round4/f1_fold_support.json`):
  - (a) the {1, 8} window list is byte-identical through the new path (SHA-256 both ways), and its length equals the committed `n_train_windows`;
  - (b) a 50-iteration Arm A seed-0 run reproduces the committed first 50 values of all six loss traces **bitwise**, through `--holdout 1,8` and through the default path (the committed curves are full precision);
  - (c) each new fold excludes exactly its two episodes, and its four held-out trajectories lie inside them.
  - Trap caught and avoided: a first version edited `make_split` itself. That shifted every later line of `src/rollout_eval.py`, whose lines the ledger, `docs/APPENDIX_G_RULES.md` and two artifacts cite. It was reverted, and `fold_split` was appended before the main guard instead. No cited line moved (checked line by line).
- **Item 1b, ruling (B).** `scripts/head_to_head_accuracy.py`'s `main()` is now `compute(horizons)` plus a writer, and its default rebuilds the artifact byte-identically. `scripts/x3_armB_reference.py` writes `results/x3_armB_2500_reference.json` from the stored rollouts at all six horizons. It equals `head_to_head_accuracy.json` on every shared cell (difference 0.0) and `action_sensitivity.json`'s rollout at h = 32 to 8.5e-9.
- **Item 2.** `BASELINE_SPECS.md` rows 33-34 are complete with citations. The built models are 713,171 and 686,196 parameters (0.999 and 0.961 of 714,164), as PF3 recorded. Nothing was added. The ladder's teacher-forced-only check of the matched variants is noted in M-87.
- **Item 3, timing.** `scripts/round4_queue_timing.py` (`results/round4_queue_timing.json`) probes 20 iterations of Arm A and Arm B on {0, 2} and of the matched MLP and transformer. To calibrate the matched models it also probes their Table S7 counterparts, which have finished runs, as `mn_sweep_timing.py` does. The first probe projected X3 at 23.83 h at three seeds, over the plan's 22 h, so the two-seed fallback would have applied. **The user ruled (chat, `DECISIONS.md#F1-x3-cap`): raise X3's cap to 24 h and run three seeds.** Re-probed under it: X3 23.83 h, X4 6.75 h, 30.58 h in all against the 32-hour cap. The first probe's output is transcribed in the evidence folder; its record was overwritten.
- **Item 4, the reading scripts.** `scripts/x3_cross_fold.py` and `scripts/x4_matched_baselines.py`, to Annex 2. Every statistic is imported:
  - X3: `mn_sweep_eval.arena`/`score`; `review_bootstrap_unit.boot_cluster` at a1's 20,000 draws and seed 0 (M-23's three-seed bootstrap, which is inline in a1); `a1_ab_by_horizon.sign_p`; `p5_sweep_power.boot_ci` for the exact per-fold intervals; M-64's functions for h = 1.
  - X4: `baselines_eval.evaluate`, `verdict_baselines.differences`/`family`/`overall`.
  - Assertions on existing artifacts, all passing: X3 (a)-(g) (Arm A to 0.0, Arm B to 8.2e-8, M-64 cell C to 0.0); X4 (a)-(c) (baselines_eval and M-76's verdict reproduced to 0.0).
  - Dry runs of each `reading()` on untrained weights ran from harnesses outside the repository; a non-finite score stops each one.
- **Review before the freeze.** One read-only Explore agent reviewed both scripts and the entry text. Verdict FIX-FIRST: nothing blocking, four should-fix items, six nits, all applied:
  - a non-finite score now stops each script with a `.blocked` record;
  - the entries now name the 20-iteration probes, where they had said nothing had trained;
  - the claims about what ran are checked by the writer against the saved logs, which name each script's SHA-256;
  - smaller fixes: the ratio's direction, `os.chdir` to the root, M-76's record labels, and "within 1e-6" in place of "equal".
  - One more trap, my own: the failure clause's backticked `.blocked` path would have been parsed by `ledger_check` as an artifact the rule needs at discharge. It was reworded before the commit.
- **Item 5, pre-registration.** Ledger **M-86 (X3)** and **M-87 (X4)**, status PRE-REGISTERED, written by `round4/f1_write_prereg.py` with every motivation figure read from artifacts.
  - Script SHA-256s: `e8422bb6…` and `9e7ca635…`, each found by its own script's `ledger_hashes`.
  - Committed as `5f0acd4` under the plan's subject and pushed before the queue launched; RESULTS.md M- 85 → 87.
  - X4's labels are "A MATCHED BASELINE AHEAD" and "RWM AHEAD OF BOTH" (M-76's say "A BASELINE AHEAD" and "ALL THREE"), stated as a deviation.
- **Item 6, launch.** `runs/queue_round4.txt` was written from the committed record (`--queue-from-record`) and launched at 10:36:10 (+0530) under `nohup caffeinate -i`, on AC power. The first run, `x3_A_02_s0`, passed 50 iterations with a finite loss on 7,688 windows from episodes 1 and 3-9; only its iteration-0, 25 and 50 lines were read. `round4/RUN_QUEUE.md` records the runs, the projection and a status command that reads no checkpoint line.
- **Item 7.** No paper edits. The fast build after the ledger append moved only `n_entries` and `ledger_kb`.
Build/gates: pass. Fast build, every gate, build again: byte-identical, and a third build too. ledger_check PASS (M-86 and M-87 pending); 65/65 claims and 65/65 corruptions; 0 suspect pointers.
Paper numbers changed: n_entries 274 → 276; ledger_kb 593 → 609 (FINDINGS_LEDGER.md)
New keys: none
Re-anchored checks: none
CPU jobs over 1 min:
- the fold-support assertion (b), run twice (two 50-iteration runs each, about 2.2 min wall each time);
- the timing probes, twice (about 3.2 min each, idle machine, before launch);
- the review agent (about 16 min);
- the build and gates after launch (about 1.5 min, contended with the queue's first run).
The --assert-only runs and dry runs took under 1 min each.
Queue status: running (0 of 30 done at 10:41; projected finish about 2026-10-12 17:10 +0530)
Body words (round2/t6_words.py): 20,745 (F0: 20,745)
Abstract words / numerals (C12.1): 370 / 23
Next: F2, in a fresh terminal (Opus 5.5, high effort). It runs while the queue trains, and every job it runs is logged as contended. It must not read any per-run log line except through RUN_QUEUE.md's filtered status command. F5 starts only when RUN_QUEUE.md's status command shows 30 done and 0 failed.
Decisions for user: none (rulings this session: DECISIONS.md#F1-x3-cap)

## F2 — 2026-10-11 12:31 — Opus 5.5 (the plan assigns high effort, fresh terminal) — status: COMPLETE
Commits:
bb3ae3a [F2][1] X5 feasibility: the tracking terms need the environment's sampled command, which the data do not hold; X5 NOT RUN (ledger D-38)
2d6212f [F2][2a] Default-preserving arguments for X6 and X8: e7 load_panel(starts, length); mn_sweep_eval.score(action_offset); baselines_eval.evaluate(action_offset)
df0f2fa PRE-REGISTER X5–X8, inference-only rules, before their readings exist
0147bd6 [F2][4] Rules X6-X8 run as committed: X6 DISAGREEMENT BEATS STEP SIZE; X7 WITHIN BAND AT 6 OF 6 HORIZONS; X8 SAME VERDICT for M-74, M-75, M-76 and the A/B comparison
40981f7 [F2][5] Discharge X6-X8: M-91 records DISAGREEMENT BEATS STEP SIZE; M-92 WITHIN BAND AT 6 OF 6 HORIZONS (epistemic); M-93 SAME VERDICT for M-74, M-75, M-76 and the A/B comparison
868eefe [F2] Build and gates after the ledger entries: n_entries 276 -> 283, ledger_kb 609 -> 643; no paper edits
(the commit carrying this entry and one out-of-scope line)
Done:
- **How this session ran.** In the same conversation as F0 and F1, at the user's request ("start F2"); the plan assigns a fresh terminal at high effort. The training queue ran throughout, so every job here was contended. One of the two permitted Explore agents was used, as the pre-freeze reviewer; its workflow record shows Opus 5.5.
- **Item 1, X5 feasibility** (`round4/X5_FEASIBILITY.md`, `f2_x5_feasibility.py`). The imagination reward has twelve terms plus the penalty. Both command-tracking terms score the forecast against the environment's sampled command, which none of the CSV's 66 columns holds and the model does not output. **X5 is NOT RUN**, by Annex 2's gate; ledger `D-38` records why, with no rule.
- **Item 2, scripts.** `scripts/x6_stepsize_short_units.py`, `scripts/x7_loeo_recalibration.py` and `scripts/x8_released_pairing.py`, written to Annex 2.
  - Three producers gained default-preserving arguments (`2d6212f`), and each rewrites its committed artifact byte-identically: `e7_free_baselines.load_panel(starts, length)`, `mn_sweep_eval.score(action_offset)` and `baselines_eval.evaluate(action_offset)`.
  - X8's offset 0 moves every action one row later, the first repeated, and rolls out causally (`mn_sweep_eval._pairing`). For RWM this equals the native offset 0 exactly, and reproduces the committed stale-pairing ratios to 1.6e-7.
  - Trap caught before the freeze: per-episode gaps at h = 368 depend on how trajectories are batched, by up to about 1e-2 for Arm B. X8 rolls each episode as its own batch, as a1 and task5 do (OUT_OF_SCOPE).
  - Every `--assert-only` assertion passes on the final bytes. Each script's whole `main()` was dry-run on synthetic data; for X8, "offset 0" was scored at offset 1 and returned SAME VERDICT with no alongside change.
- **Review before the freeze.** Verdict FIX-FIRST, one blocking finding: X8's alongside sets were smaller than the rules' own, missing the per-episode signs of M-74, M-75 and M-76 and M-23's conditions at h = 8, on nRMSE and in-sample. Added; M-23's h = 168 on 200-step trajectories is stated as not computed. Every other finding was applied:
  - X6 computes its MDE before the reading;
  - X8 writes its offset-0 baseline file only after every check passes;
  - the deviations are stated, the module lists completed, and each entry records its imports' SHA-256s.
- **Item 3, pre-registration** (`df0f2fa`, pushed before any reading). M-88 (X6), M-89 (X7) and M-90 (X8), each recording its script's SHA-256: `47f2a13f…`, `6f032605…` and `22059a0b…`. M-90 states that M-86 and M-87 import the edited functions at their unchanged defaults.
- **Item 4, the runs** (`0147bd6`), each at `df0f2fa` with its pre-registered SHA-256, every assertion passing first:
  - **X6: DISAGREEMENT BEATS STEP SIZE.** The released checkpoint at h = 100, 70 units: margin +0.2816 [+0.1978, +0.3896], against an MDE of 0.1713 computed before the reading. Alongside, h = 32 (150 units): +0.2393 [+0.0950, +0.3131].
  - **X7: WITHIN BAND AT 6 OF 6 HORIZONS** (epistemic, ten leave-one-episode-out folds, 20 trajectories). Every interval lies inside [58.27%, 78.27%]. Alongside: the aleatoric term is within the band at 3 of 6 horizons; a constant multiplier at 1 of 6 (epistemic) and 0 of 6 (aleatoric).
  - **X8: SAME VERDICT** for M-74, M-75, M-76 and the A/B comparison (M-23's conditions, three seeds). The alongside changes are recorded in M-93. They are mostly short-horizon branches and per-episode signs, M-23's conditions at h = 8 (REPRODUCES → FAILS TO REPRODUCE), and the by-horizon table's h = 1 and h = 8 intervals.
- **Item 5, discharges** (`40981f7`). M-91, M-92 and M-93 record each reading exactly as returned, with its alongside values. M-88, M-89 and M-90's Status lines are set. RESULTS.md M- 87 → 93, D- 37 → 38.
- **Item 6.** No paper edits. `appendix_g_rules.py` (stage 21a) was not regenerated, so Appendix E still lists the 23 rules from before round 4. F4 regenerates it when X5-X8 go into the paper.
- **Note for F4:** per Annex 4 A6, X8 appears in the abstract only if a verdict would change; none does.
Build/gates: pass. Fast build, every gate, build again: byte-identical. ledger_check PASS (M-86 and M-87 pending); 65/65 claims and 65/65 corruptions.
Paper numbers changed: n_entries 276 → 283; ledger_kb 609 → 643 (FINDINGS_LEDGER.md)
New keys: none
Re-anchored checks: none
CPU jobs over 1 min, all contended with the training queue:
- the producers' default re-runs (about 4 min);
- X8's `--assert-only`, three times (about 4 min each);
- X8's dry run, twice (about 9 min each);
- the rules themselves: X6 3.0, X7 0.9 and X8 11.4 CPU-min, about 15 in all against F2's cap of 4 CPU-hours;
- the review agent (about 14 min);
- the build (about 1 min).
Queue status: running (1 of 30 done at 12:31; the second run at about its projected length; the projected finish of about 2026-10-12 17:10 +0530 may slip by the contention)
Body words (round2/t6_words.py): 20,745 (F0: 20,745)
Abstract words / numerals (C12.1): 370 / 23
Next: F3, the post hoc analyses N5 and N6 (Opus 5.5, default effort). It runs while the queue trains, contended; it reads no per-run log except through RUN_QUEUE.md's status command.
Decisions for user: none

## F3 — 2026-10-11 15:30 — Opus 5.5 (the plan assigns default effort, fresh terminal) — status: COMPLETE
Commits:
b950cff [F3][1] N5 (post hoc): our models' stale-timing error with intervals at all six horizons in both arenas, and the forecast shift (ledger R-80)
9857c5d [F3][1-fix] results/claims_to_evidence.md gains R-80's CONTRIB row (ledger_check wrote it with N5; it was left unstaged)
c8cb88b [F3][2] N6 (post hoc): per-episode difficulty at the causal action timing alone; D-39 corrects D-37 (and R-69's, M-62's figures)
3340c95 [F3] Build and gates after N5 and N6: d12_lo 0.562 -> 0.523, d12_hi 1.591 -> 1.585, a2_h1_diff_r +0.040 -> +0.027, n_entries 283 -> 285, ledger_kb 643 -> 651; no paper edits
(the commit carrying this entry and the `paper_numbers.py` comment fix)
Done:
- **How this session ran.** In the same conversation as F0–F2, at the user's request ("continue", then "resume"); the plan assigns a fresh terminal at default effort. The training queue ran throughout, so every job here was contended. No agent was used.
- **Item 1, N5** (`scripts/n5_stale_armA_ci.py` → `results/n5_stale_armA_ci.json`; ledger `R-80`, post hoc). It imports rule X2's machinery from `action_sensitivity.py` and covers all six horizons, both arenas, Arm A and Arm B at 2,500 and 10,000 (seeds 0–2), and the released checkpoint.
  - Assertion (a): E, its interval and Δ at h ≤ 100 equal `action_sensitivity.json`'s stale-action cells, Δ at h = 8 among them. 40 cells, maximum difference 0.0.
  - Assertion (b): Arm A's three-seed E on the held-out pair equals `alignment_by_horizon.json`'s corrected `arm_a` block (R-79) at every horizon; the released checkpoint's E and interval equal its released block. Maximum difference 6.6e-14.
  - Arm A at 10,000, stale timing:
    - training arena: +124.6% [+75.8, +201.9] at h = 1, +209.3% [+167.3, +257.6] at h = 100;
    - held-out pair: −1.0% [−6.1, +27.7] at h = 1, +16.6% [+1.9, +72.6] at h = 100.
    All four equal Annex 3's expected orientation.
  - Δ at h = 8 on each model's own training data: 0.200 for Arm A at 10,000 and 0.204 for the released checkpoint, as Annex 3 states.
  - RESULTS.md R- 79 → 80. `ledger_check` wrote R-80's row into `results/claims_to_evidence.md`, which the first commit left unstaged; `9857c5d` adds it.
- **Item 2, N6** (ledger `D-39`, post hoc).
  - **The fix.** `scripts/a2_trajectory_level_control.py` reads `per_episode_e["1"]` (the causal timing) in place of the mean of offsets 0 and 1, and `difficulty_source` says so. Four lines are edited in place; the line count is unchanged. Regenerated by `./reproduce.sh --quick --force --stage 20o`, then `results/_regenerated.txt` was removed.
  - **The assertion** (`round4/f3_n6_check.py` → `f3_n6_check.json`): of 194 fields, every one not derived from the measure is unchanged to 1e-12. `f3_write_n6.py` asserts that the new range equals `d12_retest["1"]` in `results/step4_0a_results.json`.
  - **Ruling W5: PASS.** No verdict string changes (`collapses` stays false), and no correlation or partial changes sign.
  - **The fields that moved, old → new:**

    | Field | Old | New |
    |---|---|---|
    | Difficulty range | 0.562 to 1.591 | 0.523 to 1.585 |
    | r(disagreement, difficulty) | +0.0403 | +0.0273 |
    | r(error, difficulty) | +0.0855 | +0.0717 |
    | Partial on difficulty alone | +0.99492 | +0.99489 (interval [+0.892, +0.999] both times) |
    | Partial on difficulty and speed | +0.99503 | +0.99497 |
    | Shrinkage | −0.00100 | −0.00097 |

  - **The ledger.** D-39 corrects D-37 and names R-69 ("+0.040 with per-episode difficulty") and M-62 ("spans 0.562 to 1.591"). None of the three is edited. RESULTS.md D- 38 → 39.
  - **Other readers of the artifact** (PF7): `evidence_summary.py` and `m62_episode_clustering.py` read no difficulty field.
  - **A stale comment.** The comment on `d12_lo` and `d12_hi` in `scripts/paper_numbers.py` (lines 3091–3094) described the averaged measure. It is rewritten in place, four lines for four. The build output is byte-identical before and after.
- **Item 3.** No paper edits. The changed paper keys, as rendered, all in Appendix N:

  | Key | Old | New | Rendered in |
  |---|---|---|---|
  | `d12_lo` | 0.562 | 0.523 | "Per-episode difficulty spans … to …" |
  | `d12_hi` | 1.591 | 1.585 | the same sentence |
  | `a2_h1_diff_r` | +0.040 | +0.027 | "+0.006 with commanded speed and … with per-episode difficulty" |
  | `a2_h1_partial_both` | +0.995 | +0.995 | unchanged as rendered |

  The partial on difficulty alone is bound to no key.
- **Notes for F4, item 5:**
  - The sentence binding `d12_lo` and `d12_hi` continues "and is uncorrelated with commanded speed". At the causal timing that correlation is +0.088 over ten episodes, against +0.004 at the stale one (D-37, `d12_retest`). It is no key; F4 judges whether the wording holds.
  - `docs/APPENDIX_G_RULES.md` (stage 21a) quotes M-62's "0.562 to 1.591". M-62 is not edited, so regenerating keeps it. F4 decides whether Appendix E should point to D-39.
Build/gates: pass. Fast build, every gate, build again: byte-identical, after N6 and again after the comment fix (both builds changed only `PAPER.pdf`'s timestamps, restored). `ledger_check` PASS (M-86 and M-87 pending); 65/65 claims and 65/65 corruptions; `pdf_render_check` 5/5.
Paper numbers changed: d12_lo 0.562 → 0.523; d12_hi 1.591 → 1.585; a2_h1_diff_r +0.040 → +0.027 (results/a2_trajectory_level_control.json); n_entries 283 → 285; ledger_kb 643 → 651 (FINDINGS_LEDGER.md)
New keys: none
Re-anchored checks: none
CPU jobs over 1 min, all contended with the training queue:
- N5: 1.8 CPU-min, 1.4 min wall;
- N6's regeneration (stage 20o), whose duration was not recorded;
- the build and gates, three times, about 1.5 min each.
Queue status: running (6 of 30 done, 0 failed, at 15:28; the seventh run started at 15:03; the projected finish of about 2026-10-12 17:10 +0530 may slip by the contention)
Body words (round2/t6_words.py): 20,745 (F0: 20,745)
Abstract words / numerals (C12.1): 370 / 23
Next: F4, items 1–5 and X5–X8 into the paper, the model card and Appendix V (Opus 5.5, high effort), in a fresh terminal. It runs while the queue trains, contended, and reads no per-run log except through RUN_QUEUE.md's status command. F5 starts only when that command shows 30 done and 0 failed.
Decisions for user: none

## F4 — 2026-10-11 16:50 — Opus 5.5 (the plan assigns high effort, fresh terminal) — status: COMPLETE
Commits:
595ad41 [F4][1] Section 7.2: our models' stale-timing change with intervals in both arenas, the forecast shift, the one-policy caveat (A1); Isaac Lab's ActionManager.reset() cited (PF5); N5's table in Appendix V
05586d4 [F4][2] Model card's Action convention line (A2): N5's figures with intervals in both arenas, and the one-policy caveat
741732b [F4][3] Appendix V: rule X2's criterion, read from M-84 and the artifact's reading_rule (threshold key x2_thr_pct), and the one-policy caveat (A3)
dce6e2c [F4][4] Configuration wording (A4, A4b): no reading the rule reports puts the centre ahead of any winner, in the abstract, contribution 3, section 12 and both Appendix D tables; section 5.2 lists, per configuration, the readings that leave a winner unresolved
2cfc774 [F4][5] The difficulty measure, through N6's keys: Appendix N says it is the causal timing and prints its correlation with speed (+0.088); BUILD_CHECKS keeps the earlier mean's range
2e3890d [F4][6] X5-X8 into the paper: X6 in 6.6, X7 in 6.7, X8 in 7.2, X5 pointer in 11; Appendices W (X5, not run), X (X6), Y (X7), Z (X8, a table per rule); Appendix E and Figure 1 regenerated
0555fda [F4][7] Figure 1's caption: a lead of a few minutes means the rule was committed just before its runs were launched or its readings computed; caption and in-figure title now say 'whose data exist'
81fa338 [F4][8] Guards G7-G9 in check_comparative_claims.py, each with a self-test that plants the 10 Oct wording it exists to catch
be6af66 [F4][6-fix] The paper compiles with 0 overfull lines again; the scope audit classifies G7-G9
a526dfa [F4][review] Review fixes: A4's meaning in the abstract, X6 scoped to h = 100, X7 to pooled epistemic coverage, X8 to its four rules; guards G7-G9 and C27.2 catch the variants the review built
b153cea [F4][review] G9 also scans evidence_summary.py, the generator of Appendix D's second table (the review's variants re-tested inline: all caught)
36c0b03 [F4] Build and gates after items 1-8 and the review: 60 new keys; cc 65 -> 68 claims (35 kinds); Appendix E 23 -> 28 rules (26 with data); 62 -> 67 pages
(the commit carrying this entry and two out-of-scope lines)
Done:
- **How this session ran.** In the same conversation as F0–F3, at the user's request ("start F4"). The plan assigns a fresh terminal at high effort, and the conversation had been compacted once, before F3 ended. The training queue ran throughout, so every job was contended. Both permitted Explore agents were used, as one two-reviewer workflow after items 1–8.
- **Item 1, §7.2 (A1).** Our models' stale-timing change is given with intervals in both arenas, from new keys `n5_*` (`results/n5_stale_armA_ci.json`, post hoc). The paragraph adds the forecast shift Δ and the one-policy caveat. Isaac Lab's `ActionManager.reset()` is cited for the reset-zero argument (PF5).
  - The old held-out h = 368 figure (+22.67%) moves to a new N5 table in Appendix V, which shows every model at every horizon (rule 10).
  - The action-spread clause was already in Appendix V, as `x2_ctx_ins_*`.
- **Item 2, model card (A2).** Installed with the N5 keys. The X2 key it needs (C27.2) is the verbatim reading.
- **Item 3, Appendix V (A3).** M-84's thresholds equal the plan's draft, so no difference was logged. The 10% threshold is bound from the artifact's `reading_rule` (`x2_thr_pct`).
- **Item 4, configuration wording (A4, A4b).** Re-checked against `mn_sweep_verdict.json` and `pooled_nrmse_alongside.json` first, for every winner:
  - on all 16 metric readings no interval and no point estimate is on the centre's side;
  - the per-episode signs favour every winner.

  Both are asserted in `paper_numbers.py` and `evidence_summary.py`. A4b's list is generated (`mn_winner_unres_clause`) and equals the plan's; §5.2 also lists the episodes where the centre is ahead (`mn_winner_episode_clause`).
  - The abstract says "no reading favouring it" for A4's "and no reading puts it ahead of them", within C12.1's 370 words. One "exactly" (outputs, losses and gradients "exactly" before training) was dropped to make room.
- **Item 5, difficulty.** Appendix N says the measure is the causal timing and prints its correlation with commanded speed, +0.088 (`d12_speed_r`); "uncorrelated" became "barely correlated". BUILD_CHECKS keeps the earlier mean's range (`d12_mean_lo`/`hi`).
- **Item 6, X5–X8.** Each verdict is verbatim, with its arena, n and checkpoint:

  | Rule | Where | Reading | Arena and checkpoint |
  |---|---|---|---|
  | X6 | §6.6, Appendix X | DISAGREEMENT BEATS STEP SIZE | released checkpoint, 70 units, h = 100 |
  | X7 | §6.7, Appendix Y | WITHIN BAND AT 6 OF 6 HORIZONS | released, 20 trajectories, epistemic |
  | X8 | one sentence in §7.2, Appendix Z | SAME VERDICT for its four rules | held-out pair, n = 4, three seeds |
  | X5 | Appendix W, with a §11 pointer | NOT RUN, stated once with its reason | — |

  X8's tables bold all 21 changed table cells, matched to the artifact's change list by identity; the 22nd change, the trend reading, is quoted under the last table. Rule 11 required splits in §9, §11, §12, Appendix R and Appendix S (audit below).
  - **Appendix E (stage 21a)** now has 28 rules. X3 and X4 are "not yet discharged", with their pre-registration commit and no lead time. The title stripper had turned M-89's "§6.7's" into "'s"; fixed.
  - **Figure 1 (stage 22)** leaves out a rule with no lead time, asserting it is undischarged. §8 and §11's counts say "whose data exist" and "once its data exist".
- **Item 7.** Figure 1's caption gains the few-minutes sentence.
- **Item 8, guards.** G7 (C28.1, stale-interval), G8 (C28.2, action-caveat) and G9 (C28.3, config-unresolved).
  - **Self-tests.** Each plants the 10 Oct wording plus the variants the review built (4, 3 and 3), and every planted paragraph must be caught.
  - **C27.2** now needs an X2 *response* key, because the new N5 sentences carry `x2_n_ins` as a count. It plants a second paragraph.
  - **Appendix D's kind descriptions** were added without moving any `paper_numbers.py` line: they are merged on line 777 from a table at the file's end.
- **Compile.** Appendix E's new rows overran two columns by about 0.6 pt (32 overfull lines). Fixed at the input:
  - `md_to_tex` may now break a file name before its extension (floors only fall; numbers never split);
  - the pending rules' lead time prints "—";
  - Appendix X's label moved to its caption.

  The paper is at 0 overfull lines, 67 pages.
- **Review.** Two read-only Explore agents in one workflow.
  - **Honesty reviewer: 17 findings, 3 blocking.** The abstract's "never trailing it" (M-74's per-episode signs); §11's "28 of them with per-rule verdicts"; §12's "free-baseline margin … open". All fixed, as were its 7 should-fix findings: X6's margin is at h = 100 and the h = 368 one is not re-tested; "about equally" holds at h = 8 only; X8 re-scores four rules; X7 is pooled epistemic coverage; "narrows" replaces "answers"; Appendix S.
  - **Mechanics reviewer: 12 findings.** All six guard findings are fixed, and every bypass string it built is now caught (re-run inline). Rule 10 holds: all 8 keys the template no longer uses are accounted for. No ledger citation moved.
  - **Reconfirmation** was done inline: a workflow's agents cannot be resumed by SendMessage, and the cap of two was spent.
- **Rule 11 audit, every sentence installed in a summary site:**
  - abstract (A4), contribution 3, §12's configuration clause, and both Appendix D tables: every M-74 reading (16 metric readings and the per-episode signs) favours each winner → **agree**;
  - §9 lesson 1, §11 and Appendix R's ranking paragraphs, §12's X6 clause and "open rather than settled", Appendix S: the margin is unresolved on 400-step trajectories at h = 368 and resolved on short units at h = 100; each sentence states both → **agree (split stated)**;
  - §9 lesson 2, §11's opener, Appendix R's recalibration paragraph, §12's X7 clause, Appendix S: no cell is resolvable on the two-episode design, while X7 is within the band at 6 of 6 epistemic horizons on 20 trajectories; both stated → **agree (split stated)**;
  - §11's X5 pointer and the §8/§11 rule counts → **agree**.
- **Not compliant, and assigned to F6 by the plan:**
  - the abstract's "margin unresolved" (X6) and "(no cell resolvable)" (X7);
  - contribution 1's margin clause (X6) and the recalibration bullet (X7);
  - Appendix D's rows for the ranking claim (template line ~1474) and the recalibration, and `evidence_summary.py`'s rows for both.
- **Notes for F5 and F6:**
  - After X3 and X4 are discharged, regenerate Appendix E (stage 21a) and then Figure 1 (stage 22, `paper_figures.py`), so both include them.
  - `part_f_gate` 4b fails until F11 rebuilds the bundles.
  - The abstract is at C12.1's cap (370 words, 23 numerals).
- **Model card (ruling W12).** `MODEL_CARD.md` has a new Action convention line and is ready to re-upload to the model host. That is the user's step.
Build/gates: pass. Evidence summary (stage 21b), fast build, every gate, `part_f_gate`, fast build again: byte-identical. `ledger_check` PASS (M-86 and M-87 pending); 68/68 claims and 68/68 corruptions; 35 kinds, 0 unclassified; xref 0 suspect; typed numerals 0 unclassified; compile 0 overfull. `part_f_gate` 6/7, 1 not run: 4b fails on the bundles, check 6 passes.
Paper numbers changed: appG_n_rules 23 → 28; appG_n_lead 23 → 26; appG_n_positive 22 → 25 (results/appendix_g_rules.json); cc_n, cc_pass, cc_st_n, cc_st_caught 65 → 68; cc_kinds 32 → 35 (results/comparative_claims.json); f1_n_cited 35 → 37; f1_n_kept 33 → 35 (results/paper_figures.json); pdf_pages 62 → 67; tn_typed 914 → 974; appG_table, cc_kind_list and evidence_table regenerated
New keys: 60, all from results/ —
- `n5_*` (16), from n5_stale_armA_ci.json;
- `x6_*` (20), `x7_*` (10) and `x8_*` (8), from the X6–X8 artifacts;
- `mn_winner_unres_clause` and `mn_winner_episode_clause`, from mn_sweep_verdict.json and pooled_nrmse_alongside.json;
- `d12_speed_r`, `d12_mean_lo` and `d12_mean_hi`, from step4_0a_results.json;
- `x2_thr_pct`, from action_sensitivity.json.
Re-anchored checks: C27.2 "They respond to the action" → "Our models do use the action"; its key match widened to `n5_ins_*`/`n5_ho_*`, and its X2 requirement narrowed to a response key (`x2_reading`, `x2_E_swap_*`, `x2_ci_swap_*`). Coverage is the same 2 paragraphs, with a second plant.
CPU jobs over 1 min, all contended with the training queue:
- the review workflow, 2 agents, 12.4 min wall;
- about eight fast builds with gates, about 1.5 min each;
- `paper_figures.py`, about 11 s each time, so under a minute.
Queue status: running (7 of 30 done, 0 failed, at 16:43; the eighth, X3 Arm B fold {7, 9} seed 0, started at 15:57; RUN_QUEUE's projected finish is about 2026-10-12 17:10 +0530, which contention may push later)
Body words (round2/t6_words.py): 21,787 (F0: 20,745)
Abstract words / numerals (C12.1): 370 / 23
Next: F5 (Sonnet 5.5), in a fresh terminal, only when RUN_QUEUE.md's status command shows 30 done, 0 failed and "queue empty; runner exits". Until then no session reads a run.
Decisions for user: none

## F5 — 2026-10-16 11:55 — Opus 5.5 (the plan assigns Sonnet 5.5, fresh terminal) — status: COMPLETE
Commits:
669d630 [handoff] Adopt the user's TMLR completion workplan (14 Oct) for F5-F12: copied into round4/, home path removed; one out-of-scope line on the queue's restart and log overwrite
d7cac21 [handoff] Workplan addendum (user ruling, 16 Oct): the 16,000-word target is editorial, not a TMLR cap (a 14 Oct reading of the author guidelines, rechecked at F7 and F11); the stray docs/handoff variant moved to the Trash
3000b00 [F5][1] Training gate PASS: 30 of 30 runs done, 0 failed; iterations, seeds, arms, folds and parameter counts as queued; no NaN; weights present; one data hash
faf56c0 [F5][2] X3 and X4 read by their frozen scripts (SHA-256 e8422bb6..., 9e7ca635... as pre-registered at 5f0acd4): X3 REPLICATES ACROSS FOLDS; X4 PARTIAL
6aee77b [F5][3] Discharge X3 and X4: M-94 records REPLICATES ACROSS FOLDS, M-95 records PARTIAL, exactly as returned; M-86 and M-87's Status lines set; RESULTS.md M- 93 -> 95
(the build commit after these, and the commit carrying this entry)
Done:
- **How this session ran.** In the same conversation as F0–F4, at the user's request ("start F5"); the plan assigns Sonnet 5.5 in a fresh terminal. No agent was used. The user's TMLR completion workplan (`round4/TMLR_CODEX_WORKPLAN.md`, adopted before this session, with its 16 Oct addendum) governs process from here. It forbids pushing, so every commit since `110ecd7` is local.
- **Queue.** Finished 2026-10-15 05:04: "queue empty; runner exits", 30 done, 0 failed. Another session resumed it at 2026-10-14 22:26 and overwrote its log (OUT_OF_SCOPE); the interrupted `x3_A_79_s2` re-ran from its start with no collision. No per-run log was read.
- **Item 1, gate** (`round4/f5_gate.py` → `f5_gate.json`). It uses `queue_run.py`'s own trainer map and `check()`, then checks independently, for all 30 runs:
  - each is in the done list, and the failed list is empty;
  - iterations, seed, arm and fold are the queued ones;
  - for X3, the held-out episodes are the fold its id names; for X4, they are {1, 8}, with the parameter count within 5% of 714,164 (MLP 713,171; transformer 686,196);
  - training and held-out episodes partition the ten;
  - every loss trace and final term is finite, the weights exist and are not empty, and all runs share one data hash.

  **PASS.** Wall-clock hours from the records: X3 17.68 of its 24, X4 8.81 of its 10, 26.48 of 32 (projected 23.83, 6.75, 30.58). The interrupted first attempt at `x3_A_79_s2` left no record, so its time is not in the sum.
- **Item 2, the readings.** Both scripts' SHA-256 equal M-86's and M-87's, and neither file has changed since `5f0acd4`. Run unchanged, one after the other, on battery power under `caffeinate`, with no training job running; every self-test and assertion passed first.
  - **X3: REPLICATES ACROSS FOLDS.** Gap (B − A) +2.2275 [+1.3683, +3.5053] at h = 368 over 20 trajectories, five folds, 2,500 iterations, three seeds. 10 of 10 episodes are positive (P = 0.002), and every fold's exact interval is above zero.
  - **X4: PARTIAL.** At h = 368 on the held-out pair, n = 4: the matched MLP is RWM BETTER (D +0.8840) and the matched transformer CANNOT BE SETTLED (D +0.2055, p 0.625).
  - Runtimes: 41 s and 35 s wall; 0.88 and 1.04 CPU-min.
- **Item 3, ledger.** M-94 (X3) and M-95 (X4) record each reading as returned, with its part-of-rule and alongside values and caveats, and no interpretation (`round4/f5_write_discharges.py`). M-86's and M-87's Status lines are set. RESULTS.md M- 93 → 95. `ledger_check` PASS.
- **Item 4.** No paper edits. Appendix E (stage 21a) and Figure 1 (stage 22) still show X3 and X4 as pending; F6 regenerates both, now that both rules are discharged.
Build/gates: pass. Fast build, every gate, build again: byte-identical. `ledger_check` PASS; 68/68 claims and 68/68 corruptions. `part_f_gate` 6/7 with 1 not run; 4b fails on the bundles, as known.
Paper numbers changed: n_entries 285 → 287; ledger_kb 651 → 657 (FINDINGS_LEDGER.md)
New keys: none
Re-anchored checks: none
CPU jobs over 1 min: none (the readings, 41 s and 35 s; the build and gates, about 1.5 min, uncontended)
Queue status: done (30 of 30, 0 failed; finished 2026-10-15 05:04 +0530)
Body words (round2/t6_words.py): 21,787 (F0: 20,745)
Abstract words / numerals (C12.1): 370 / 23
Next: F6 (Opus 5.5, high), in a fresh terminal. It puts X3 into §5, an appendix table, §11 and contribution 2 (variant REPLICATES ACROSS FOLDS), and X4 into §5.3 (PARTIAL, with its caveat). It rewrites the abstract once, to at most 300 words, with C12.1's cap tightened to 320 and rule 11 applied, including F4's open items. It also covers contributions and Appendix D's rows, and regenerates Appendix E and Figure 1. Commits stay local (workplan §6).
Decisions for user: none

## F6 — 2026-10-16 13:40 — Opus 5.5 (the plan assigns high effort, fresh terminal) — status: COMPLETE
Commits:
c448d7d [F6][1] X3 into the paper: section 5 (A5, the REPLICATES ACROSS FOLDS variant), Appendix L's fold-by-fold table, section 11 and Appendix R's sample-size paragraphs narrowed to the magnitudes, contribution 2
bc40528 [F6][2] X4 into the paper: section 5.3 (A5c) in place of 'parameter-matched variants were specified but not run', two size-matched rows in its table, contribution 3, and section 12's baseline sentence (rule 11)
be7715a [F6][3] The abstract, rewritten once along A6's skeleton: 300 words, 18 numerals (from 370 and 23); C12.1's word cap tightened from 370 to 320 (W7)
80555f3 [F6][4] Contributions: bullet 1 gains X6's split (unresolved over whole trajectories at h = 368, disagreement ahead on shorter units at h = 100), bullet 6 gains X7; 8 bullets of at most 3 sentences
705b369 [F6][5] Appendix D's two tables: rows for the claims X3-X8 bear on, verdicts verbatim
97057d0 [F6][E] Appendix E (stage 21a) and Figure 1 (stage 22) regenerated after X3 and X4's discharge: 28 rules, all 28 with a lead time and a verdict
73271e3 [F6][rule 11] Section 9: the held-out count bounds every long-horizon magnitude, not every long-horizon claim; the direction is re-tested on all ten episodes (X3)
ad934af [F6][review] Review fixes: every X3 and X4 sentence carries its verdict and its rule's caveats (2,500 iterations, not 10,000; fixed folds; size is one axis); the abstract keeps 'on short windows'; X3 trained four new folds beside section 5's
ba78d5d [F6][fix] Figure 1 at 0.21 in per bar (was 0.27): with 29 bars it filled a page and LaTeX warned 'Text page 3 contains only floats', failing compile_paper; only its PNG changes
3dcb8c6 [F6] Build and gates after items 1-5, Appendix E and Figure 1, and the review: 31 new keys; abstract 300 words / 19 numerals; 69 pages
(the commit carrying this entry)
Done:
- **How this session ran.** In the same conversation as F0–F5, at the user's request ("start F6"); the plan assigns a fresh terminal at high effort. The workplan (`round4/TMLR_CODEX_WORKPLAN.md` §2) caps delegation outside F10 at one narrowly scoped read-only reviewer, and that cap overrides ultracode's default: one Explore agent was used, through the Agent tool so that it could be asked to reconfirm. All commits are local (workplan §6).
- **Item 1, X3** (keys `x3_*`, `results/x3_cross_fold.json`, M-94).
  - **§5 (A5, the REPLICATES variant).** Pooled gap, interval, all ten episodes positive, every fold's own interval above zero, and teacher forcing's one-step lead on short units. Caveats: 2,500 iterations, not 10,000; four new folds beside §5's own; fixed folds; seeds carried. All asserted in `paper_numbers.py`.
  - **The fold-by-fold table** is a titled section of Appendix L, not a new appendix: LaTeX's appendix letters end at Z, so a 27th appendix cannot compile.
  - **§11 and Appendix R:** "Effective sample size bounds the long-horizon magnitudes"; the direction is re-tested on all ten episodes. Contribution 2 carries X3's reading and caveats.
- **Item 2, X4** (keys `x4_*`, M-95). §5.3's sentence that variants were "specified but not run" is replaced by A5c: **PARTIAL**; the MLP is RWM BETTER, and the transformer CANNOT BE SETTLED (p = 0.625). The same per-baseline results at h = 100 and 32 are asserted, and "size is one axis" is stated wherever it is reported.
  - §5.3's table gains the two size-matched rows in its own format. RWM's row equals X4's evaluator to 1e-6 (asserted).
  - Contribution 3 and §12's baseline sentence carry X4, the latter by rule 11.
- **Item 3, the abstract** (A6 order). 370 → **300 words**, 23 → **19 numerals**, every clause within A6's 25 words. C12.1's word cap goes 370 → 320 (W7); its numeral cap is left at 26, since W7 does not tighten it.
  - Every guard's abstract anchor is kept except C9.1, re-anchored (below). `part_f_gate` check 6 passes: every abstract key is in the body.
  - One residual, the reviewer's optional point: with "released" dropped to hold the 25-word clause, the abstract's first "checkpoint" is unqualified. Left for F7/F10.
- **Item 4, contributions.** Bullet 1 gains X6's split, bullet 6 X7; 2 and 3 took X3 and X4. There are 8 bullets of at most 3 sentences. X5 was not run, so no bullet changes for it.
- **Item 5, Appendix D.**
  - **First table:** the RWM-AR row gains X3 and X8, the baselines row X4 and X8, the configuration row X8, the epistemic row X6's split, and the penalty row X5's pointer.
  - **Second table** (`evidence_summary.py`): new rows for X3 (all ten episodes, 20), X4 (held-out pair, 4), X6 (all ten episodes, 70 units) and X7 (all ten episodes, 20). X8's reading joins the four rows it re-scored, on their own arenas.
  - C24.1 confirms all 20 rows' arenas and n_independent against their sections.
- **Appendix E and Figure 1** (stages 21a, 22): 28 rules, all 28 with lead times; M-86 and M-87 at +121.16 h each, by the same computation as every rule. Figure 1 is re-drawn at 0.21 in per bar: with 29 bars at 0.27 in it filled a float-only page, and the resulting LaTeX warning failed the compile.
- **Review.** One read-only reviewer, scoped to F6's diff, the rendered snapshot, the X3–X8 artifacts, M-86/M-87/M-94/M-95 and rule 11 / A5 / A5c / A6. It reported 10 findings, none numeric:
  - X3 and X4 sentences lacked their verdicts and the caveats M-86 and M-87 require;
  - the abstract had dropped "on short windows" (on 400-step units the one-step gap spans zero);
  - "retraining … five splits" (four were new);
  - a caption rendered as a heading.

  All 10 were fixed, and the reviewer reconfirmed them, finding nothing new.
- **Rule 11 audit, every sentence F6 installed or changed in a summary site:**
  - **Abstract:**
    - base claim with one-step qualifier → agrees: three-seed 368-step gap; teacher forcing ahead only on short windows;
    - X3 → agrees: REPLICATES at h = 368; alongside, h = 100 replicates and h = 1 is teacher forcing's, as the previous clause says;
    - baselines → agrees at 368, scoped; X4 PARTIAL stated;
    - configuration → unchanged from F4;
    - scope "magnitudes rest on 4" → agrees, since X3 is the direction;
    - X6 → split stated;
    - X7 → epistemic within the band at every horizon on training episodes left out of each fit, with Arm A's 17 of 36 → split stated;
    - alignment → scoped to short horizons;
    - policy.
  - **Contributions:** 1 (X6 split stated), 2 (X3), 3 (X4, size one axis), 6 (X7 split stated) → agree.
  - **Appendix D:** each row now carries every reading the rules bear on → agree.
  - **§9** count paragraph (magnitudes; X3 direction), **§11** sample-size paragraph and opener, **§12** baselines (X4), margin and recalibration → agree, splits stated.
  - **Outside rule 11's sites, for F10's public-facing check:** README's "What this found" still lacks X3, X6 and X7, though it is no stronger than the paper.
Build/gates: pass. Evidence summary, fast build, every gate, `part_f_gate`, fast build again: byte-identical. 68/68 claims and 68/68 corruptions; C24.1 20/20; compile 0 overfull, 0 warnings. `part_f_gate` 6/7, 1 not run: 4b fails on the bundles (F11), check 6 passes.
Paper numbers changed: appG_n_lead 26 → 28; appG_n_positive 25 → 27 (results/appendix_g_rules.json); f1_n_cited 37 → 39; f1_n_kept 35 → 37 (results/paper_figures.json); pdf_pages 67 → 69; tn_typed 974 → 990; appG_table and evidence_table regenerated
New keys: 31, all from results/:
- `x3_*` (19), from x3_cross_fold.json;
- `x4_*` (12), from x4_matched_baselines.json and its evaluator output.
Re-anchored checks: C9.1 "A per-horizon rescaling brings the released checkpoint's coverage within" → "A per-horizon rescaling brings the checkpoint's coverage within" (the abstract's rewrite; scan unchanged). C12.1 cap tightened, 370 → 320 words (W7).
CPU jobs over 1 min: the review agent (about 5.5 min, then 1 min); fast builds with gates, about 1.5 min each. None contended (no training).
Queue status: done (30 of 30, 0 failed; finished 2026-10-15 05:04 +0530)
Body words (round2/t6_words.py): 22,313 (F0: 20,745)
Abstract words / numerals (C12.1): 300 / 19
Next: F7 (Opus 5.5, default), in a fresh terminal. Length and readability by Annex 5's moves, never deleting: the body is 22,313 words against W6's editorial ≤16,000 (aim 15,000; workplan addendum: no TMLR cap). It removes ledger IDs from the main text (W8), verifies the TMLR author instructions first (workplan §4C), and looks at the abstract's unqualified "checkpoint". Commits stay local.
Decisions for user: none

## F7 — 2026-10-16 13:05 — Opus 5.5 (the plan assigns default effort, fresh terminal) — status: COMPLETE
Commits:
ff9ce8c [F7][0] TMLR author instructions read (workplan §4C): no length limit, so W6's target stays editorial; the length log opened at 22,313 body words
da49bd9 [F7][1] Section 2: seven related-work paragraphs moved verbatim to Appendix I's new 'Related work in full'; section 2 keeps the precedent, what is new, the PETS lineage and one sentence for each (1,123 -> 821 words)
1fd37ce [F7][2] Section 3.1: the metrics' formulas and the coverage-nominal check moved verbatim to Appendix G; section 3.1 states each metric in words (739 -> 582 words)
4215d2e [F7][3] Section 5: the floor paragraph, 'Seeds, and what four trajectories can show' and 'What is small' moved verbatim to Appendix L; section 5 keeps two sentences of each and every verdict (2,089 -> 1,628 words)
30b57de [F7][4] Section 5.1 to two sentences (the transition count, the ratio, the percentage); its four paragraphs moved verbatim to Appendix L (305 -> 93 words)
203ae2e [F7][5] Sections 5.2 and 5.3: the equal-compute paragraph to Appendix U, the pooled-nRMSE passage and the RSSM paragraph to Appendix L, verbatim; summaries keep every verdict, both changed readings and X1's two readings (2,847 -> 2,422 words)
bdd37ee [F7][W8] Ledger IDs and commit labels out of the main text from the title page to section 5.3 (S-17, S-12 in Figure 1's caption, R-60, M-23's commit label); the abstract says 'released checkpoint' (C9.1 re-anchored, 300 words unchanged)
2cec225 [F7][6] Five detail passages from sections 4-5.3 moved verbatim to Appendices L and U (the two definitions of teacher forcing, the alongside nRMSE, the loss slopes, the diverged rows); each keeps a sentence and a pointer
8b5bccb [F7][3] Sentences: 22 main-text sentences of over about 45 words with more than two qualifiers split at clause boundaries, title page to section 5.3; qualifiers unchanged; the contributions left at Annex 6's three sentences a bullet
4dd4ff4 [F7] Build and gates after the length moves, W8 and the sentence splits: body 22,313 -> 20,585 words; abstract 300 words / 19 numerals; 72 pages, 0 warnings; byte-identical rebuild
(the commit carrying this entry)
Done:
- **How this session ran.** In the same conversation as F0–F6, after a compaction, at the user's request ("start F7"); the plan assigns a fresh terminal. No subagent was used. All commits are local (workplan §6). Two subjects carry "[F7][3]": 4215d2e is the third length move (PLAN item 1), and 8b5bccb is PLAN item 3, the sentences.
- **TMLR check first** (workplan §4C, `round4/TMLR_CHECK.md`). TMLR's Author Guidelines, read today, still set no length limit: unusually long papers, appendices not counted, are "likely to result in reviewing delays". Its Reviewer Guide gives 4 weeks above 12 main-content pages. The template is the TMLR style file; review is double-blind; the supplement may be up to 100 MB, PDF or ZIP. The quota post requires every author to have budget left (the user's check). OpenReview's page did not render without JavaScript, so F11 reads it in a browser. W6's target stays editorial (the 16 Oct ruling).
- **Item 1, length** (`round4/LENGTH_LOG.md`, one row per move). Every move was verbatim to an appendix that already held its subject, since LaTeX's letters end at Z: Appendix I gained "Related work in full", G "The metrics' formulas", L five titled sections (it is now "section 5 in detail"), and U two. I, G and L are retitled to name what they gained. Annex 5's four rows for F7's range are done (§2, §3.1, §5, §5.1). §5.2 and §5.3, which Annex 5 does not list, gave three more passages; §4 and §5 gave the two notes on teacher forcing's definitions.
  - **Kept in the main text:** every verdict (M-16, M-23, M-74, M-75, M-76, X1's two readings, X3, X4), every number the abstract cites, and the tables §3.2 points to.
  - **Not copied:** §5's long-horizon paragraph (111 words). Appendix L already stated each of its clauses: the 4-of-4 cells, the Bonferroni and Holm results, and the reimplementation reading. §5 keeps its cell count.
  - **Result:** 22,313 → **20,585** body words (F7's range 9,464 → 7,736). `xref_sweep.py` reported 0 suspect pointers after every move, and every gate passed after each one. This is 27% of the cut to 16,000, short of the plan's "about 40%". The contributions (about 950 words) were left whole, as a summary that five rule-11 guards scan. F8 needs at least 4,585 words from §6–§12 (12,849), i.e. 36%; the length log has the arithmetic.
- **Item 2, labels (W8).** Removed from the main text: S-17 (§4), Figure 1's caption S-12, R-60, and M-23's commit label. S-17's history went to BUILD_CHECKS' moved list, named a withdrawn framing as C10.5 requires; Appendix E's commit column carries the label, and the R-60 date stays bound. Also left the main text with their moved passages: R-77, R-78, M-80, M-81, and the generated Part C sentence's "(ledger M-83)". Rule IDs (M-xx, X-n) stay where their verdicts are reported. No "post hoc" or "pre-registered" label was removed. The abstract's only "checkpoint" now reads "released checkpoint". To keep the clause's length, "A" was dropped, so the abstract is still 300 words.
- **Item 3, sentences.** 22 sentences split at clause boundaries, with every qualifier kept. A clause that became a sentence gained a subject or a joining word, and three changed clause order (the length log lists them). The contributions are exempt, because each bullet already has the three sentences Annex 6 allows.
- **Rule 11.** Summary sites touched: the abstract only (one word changed, one dropped), and the reading is unchanged. The contributions, Appendix D, §9, §11 and §12 were not edited.
- **Small fixes the gates asked for, in moved or new text.** "not 1" set as $\rho = 1$ (typed numeral). "1.16 to 1.27×" became "1.16× to 1.27×" and "{{div_factor}}×" became "times" (C19.1: same numeral, two units, one appendix). §5's "N = 1" set in math (the slot check matched it to a count). §4's "None of them is typed" became "so none of them is typed".
Build/gates: pass. Evidence summary (unchanged), fast build, every gate, `part_f_gate`, fast build again: byte-identical. 68/68 claims and 68/68 corruptions; compile 0 overfull, 0 warnings. `part_f_gate` 6/7, 1 not run: 4b fails on the bundles (F11), check 6 passes.
Paper numbers changed: pdf_pages 69 → 72 (the appendices hold the moved text); tn_typed 990 → 1052 (results/typed_numerals.json; §2's one-line citations keep their years beside the moved paragraphs')
New keys: none (§5.3 now also prints the existing `x1_final_reading`)
Re-anchored checks: C9.1 "A per-horizon rescaling brings the checkpoint's coverage within" → "Per-horizon rescaling brings the released checkpoint's coverage within" (item 2's "released"; scan unchanged)
CPU jobs over 1 min: fast builds with gates, about 1.5 min each (about 10); the end-of-session run, about 3 min. None contended.
Queue status: done (30 of 30; no training this round after F5)
Body words (round2/t6_words.py): 20,585 (F0: 20,745)
Abstract words / numerals (C12.1): 300 / 19
Next: F8 (Opus 5.5, default), §6 to §13 with the appendices only as destinations: Annex 5's rows for §6.2–§12 in full, W8 and the sentence splits in that range, then the end-of-range report (final count against 16,000, the three largest remaining sections, pages before References, the ID count against F0's). It needs ≥4,585 words from 12,849. F6's header time (13:40) is not its commit time (75ee7a9, 12:23). Commits stay local.
Decisions for user: none

## F8 — 2026-10-16 17:30 — Opus 5.5 (the plan assigns default effort, fresh terminal) — status: COMPLETE
Commits:
855a40f [F8][1] Section 6.2: the full released-checkpoint table, the held-out-pair comparison, the larger-sample note, the ensemble-5 arms' table and the permutation note moved verbatim to Appendix M; section 6.2 keeps the h = 1 and h = 100 rows (1,791 -> 1,433 words)
8854338 [F8][2] Sections 6.3-6.4: the term-by-term and run-count summaries, the corrected objective's permutation detail and the two code walkthroughs moved verbatim to Appendix J; the derivation, the synthetic-noise verdict and the sharing stay
929ef72 [F8][3] Section 6.5: both tables and their explanatory paragraphs moved verbatim to Appendix K; section 6.5 keeps the teacher-forced arm's and the epistemic term's findings, its claim and the structural-excuse result (1,001 -> 438 words)
b422e7a [F8][4] Section 6.6: r_dd's table, rule M-43's paragraph, the expectation, the free baselines' cost and two alongside notes moved verbatim to Appendix N; the counter table, the free-baselines verdict and X6 stay (1,744 -> 1,429 words)
b65b257 [F8][5] Sections 6.7-6.8: section 6.7's constant-scalar detail, table and M-69 detail to Appendix T, section 6.8's two tables to Appendices O and P, verbatim; every verdict, X7, the cautions and the independence factor stay (2,145 -> 1,573 words)
13dc31e [F8][6] Section 7: 7.2's N5 figures, forecast-shift discussion and per-trajectory values to Appendix V, X8's detail to Appendix Z, its drafting-history sentence to BUILD_CHECKS; 7.2 split into paragraphs, every verdict and caveat kept (1,172 -> 1,024 words)
99f6ad2 [F8][7] Section 11: what is stated beside its result, or in full in Appendix R, leaves; O13 is said once, plainly; S-12 to plain words; six pointers repointed to Appendix R (864 -> 628 words)
41d3a17 [F8][8] Section 12: 'What should travel' moved verbatim to Appendix S, two sentences kept; the conclusions stay, the long baselines sentence split (754 -> 563 words)
344b753 [F8][9] Sections 6.1, 6.2, 6.6 and 8: the correspondence passages to Appendix H, the four-model table to Appendix M, the paired-test note to Appendix N, the reproducibility detail to BUILD_CHECKS, verbatim; S-12 and S-15 out of sections 8 and 9
63e7b1d [F8][10] Section 6.7's X7 alongside readings to Appendix Y; two in-section restatements of section 6.2's one-step figure removed (the figure stands above them)
8229b30 [F8][W8] Sections 6-12: no R-/S-/D-/C-/B- IDs or commit labels left; rule IDs kept once per section where the verdict is reported (M-65, M-44, M-68, M-84 and three X7s to plain words)
7020528 [F8][3] Sentences: 24 main-text sentences in sections 6-12 split at clause boundaries; qualifiers unchanged
dc6314c [F8][review] Eight qualifiers and scopes the summaries dropped, restored from their moved originals (one read-only reviewer, every finding verified, reconfirmed); section 6.5 states its power limit
b42ead7 [F8] Build and gates after the length moves, W8, the sentence splits and the review: body 20,585 -> 17,790 words (W6's editorial 16,000 not reached; DECISIONS.md#F8-length); References on page 27; 75 pages, 0 warnings; byte-identical rebuild
(the commit carrying this entry)
Done:
- **How this session ran.** In the same conversation as F0–F7, at the user's request ("start F8"), with ultracode on. The workplan (§2) limits delegation outside F10 to one narrowly scoped read-only reviewer, and that limit overrides ultracode's workflow default, so the moves were made inline and one Explore agent reviewed them. All commits are local (workplan §6). Two subjects carry "[F8][3]": 929ef72 is the third move (item 1), and 7020528 is PLAN item 3.
- **Item 1, length** (`round4/LENGTH_LOG.md`, one row per move; scripts in `/Users/Shared/rwm_verify/evidence/R4F8/move/`). Annex 5's rows for §6.2, §6.3–6.4, §6.5, §6.6, §6.7–6.8, §7, §11 and §12 are all applied. Each moved passage went verbatim to the appendix that holds its subject: H, J, K, M, N, O, P, S, T, U, V, Y or Z, as titled sections, several of them retitled. In §11, the six paragraphs that left were already stated in full in Appendix R, which a script asserted key by key, so they were not copied twice. F8 also moved passages Annex 5 does not list, from §6.1, §6.2, §6.6 and §8.
  - **O13** is said once, plainly, in §11's new "What this study cannot address".
  - **Kept:** §9, every verdict with its arena and horizon, every number the abstract cites, and X6/X7/X8's locked scopes.
  - **Result: 20,585 → 17,790**, F8's range 12,849 → 10,054. **W6's ≤16,000 is not reached**, 1,790 over. The rest is what Annex 5 and the locked framing keep, plus the contributions list in F7's range: see `DECISIONS.md#F8-length`. I recommend accepting the count; the other options cut the contributions, §9's figures, or §5's per-reading clauses.
  - **No loss:** the 350 keys that left the main text since F7's start are all printed in an appendix, and all 1,418 template keys survive.
  - **Pointers:** `xref_sweep` 0 suspect after every move. Pointers into a §11 paragraph that left now name Appendix R.
- **Item 2, labels (W8).** No R-, S-, D-, C- or B- IDs and no commit labels remain anywhere in the main text: `S-12` ×2 and `S-15` ×3 went with their passages, or became plain words in §8 and §9. In §6–§12 a rule ID is now kept once per section, where its verdict is reported: M-65, M-44, M-68 and M-84, and X7 three times, became words elsewhere. The main text's count is 51 (M- 26, X-rule labels 25), against F0's 59 (M- 40, R- 6, S- 7, X- 5, commit 1). Repeats left in §5–§5.3 (F7's range) are logged in `OUT_OF_SCOPE.md`.
- **Item 3, sentences.** 24 sentences split in §6–§12, in the main text only, every qualifier kept.
- **Gate fixes on the way, in new or moved text:**
  - typed numerals ("ensemble size 5" kept on one line; a typed "89.15%" bound to its key);
  - C20.1, a unit for n_independent;
  - C24.1, §6.8's arena size;
  - C27.1 ("all ten episodes" in the held-out-pair paragraph);
  - C27.2 and C28.2 (Appendix V's moved N5 passage gains X2's reading and its one-policy caveat);
  - C14.1, a horizon for the per-trajectory values;
  - `xref_sweep` (§6.6's expectation keeps the nouns §5's pointer names);
  - `build_paper`, a blank line under a moved table's title.
- **Review.** One read-only Explore agent compared every F8 summary in §6–§12 with the original it replaced, checked the locked scopes and checked F8's pointers. It reported eight dropped qualifiers or scopes; I checked each against the moved original, and all eight were real. All eight are restored (LENGTH_LOG, "review (F8)"). On reconfirmation the reviewer found one only partly fixed: §6.5 now states its power limit itself.
- **Rule 11 audit, summary sites F8 touched:**
  - **§9:** labels only;
  - **§11:**
    - the ranking limit keeps both of X6's scopes;
    - the cost paragraph keeps the policy caveat, X5 and M-70's verdict with its qualifiers;
    - the effective-sample-size paragraph is unchanged;
    - O13 claims no direction;
  - **§12:**
    - its two conclusion paragraphs are kept, with one sentence split into three;
    - "What should travel" keeps its three kinds, and the σ = 0 optimum elsewhere is called a hypothesis untested outside this codebase;
  → agree. The abstract, the contributions and Appendix D were not edited.
Build/gates: pass. Evidence summary (unchanged), fast build, every gate, `part_f_gate`, fast build again: byte-identical. 68/68 claims and 68/68 corruptions; compile 75 pages, 0 overfull, 0 warnings. `part_f_gate` 6/7, 1 not run: 4b fails on the bundles (F11).
Paper numbers changed: pdf_pages 72 → 75; tn_typed 1052 → 1141 (results/typed_numerals.json; summaries name their horizons, and moved passages keep theirs)
New keys: none
Re-anchored checks: none
CPU jobs over 1 min: fast builds with gates, about 1.5 min each (about 25); two end-of-session runs, about 3 min each; the review agent, about 5.5 min and then 40 s. None contended (no training).
Queue status: done (30 of 30)
Body words (round2/t6_words.py): 17,790 (F0: 20,745)
Abstract words / numerals (C12.1): 300 / 19
Next: F9 (Sonnet 5.5): pipeline hygiene, H1–H5. Commits stay local.
Decisions for user: DECISIONS.md#F8-length (W6's editorial target missed by 1,790 words; accept, recommended, or authorise one of three further cuts)

## F9 — 2026-10-16 23:20 — Opus 5.5 (the plan assigns Sonnet 5.5, fresh terminal) — status: COMPLETE
Commits:
75ac187 [F9][0] DECISIONS.md#F8-length: the user accepts 17,790 main-text words (option 1)
9513ce3 [F9][H3a] C7.1 checks the length of BUILD_CHECKS' typed list of claims withdrawn on evidence, not only the count beside it (round 3's OUT_OF_SCOPE R0); a planted dropped item is caught
040bf5d [F9][H1] reproduce.sh: stages 20u1-20u6 for X3, X4, X6, X7, X8 and N5 (NEEDS_WEIGHTS only where our trained models are read: X6 and X7 run without runs/), and stage 11k, round 4's training queue from its committed record; pipeline_coverage 0 uncovered, 20n8 0 unclassified
5cddce0 [F9][H2] s8_runtime.py records round 4's queue (rules X3 and X4, 30 runs, 26.48 h) beside the other two, with its overlaps against round 4's sessions' CPU work (f9_cpu_jobs.json, from their evidence files); every field it wrote before is unchanged
5a4d77d [F9][H3b] task2_3_matched_and_trend.py records each trend cell's n_independent (4 held-out, 16 in-sample); stage 15 regenerated, every other field and the report unchanged (round 3's OUT_OF_SCOPE R7)
3aaf1c4 [F9][H2,H3b] Appendix B's runtime table gains round 4's runs (rt_r4_*, four rows, which runs overlapped logged work and how each was timed); Appendix H's R-46 row names its arenas' n_independent (r46_o_nind, r46_i_nind)
9281201 [F9][H4] md_to_tex.py: a path in a code span may break after a slash or underscore and before its extension, as table cells could; stretched lines with underfull reporting on fall from 12 to 2, and none holds a path
5ccad00 [F9] Build and gates after H1-H5: 11 new keys (rt_r4_*, r46_*_nind); body 17,790 unchanged; 75 pages, 0 warnings; byte-identical rebuild
(the commit carrying this entry)
Done:
- **How this session ran.** In the same conversation as F0–F8, at the user's request ("Accept 17790. … start F9"). The plan assigns Sonnet 5.5 in a fresh terminal; this ran on Opus 5.5. No subagent was used. All commits are local (workplan §6). The user's ruling is recorded first: `DECISIONS.md#F8-length` is option 1, 17,790 words accepted.
- **H1, `reproduce.sh`.**
  - **Re-run first.** Before adding the stages, each script was re-run once, uncontended (`/Users/Shared/rwm_verify/evidence/R4F9/rerun/`). Every artifact reproduced its committed copy leaf for leaf except `git_head` and N5's own `cpu_s`/`wall_s`: X3 999 leaves, X4 160 (and its evaluator's 2,558), X6 103, X7 384, X8 907, N5 644. The committed artifacts were then restored, since the ledger cites the commits they ran at.
  - **New stages 20u1–20u6.** X6 and X7 also ran with `runs/` moved aside and reproduced, so they are not `NEEDS_WEIGHTS`; X3, X4, X8 and N5 read our trained models and are. X5 has no stage (not run, D-38). The rule scripts refuse to run unless their ledger entries record their SHA-256, so a stage can only re-run the pre-registered reading.
  - **New stage 11k, the full-run block.** It writes `runs/queue_round4.txt` from `results/round4_queue_timing.json` (`--queue-from-record`), byte-identical to the queue that ran (checked with the original moved aside), then runs the queue.
  - **Wiring:** `./reproduce.sh --quick --force --stage 20u3` and `--stage 20u1` both ran through `reproduce.sh` and passed.
  - **Targets met:** `pipeline_coverage` 0 uncovered (it was 7), and stage 20n8 0 unclassified.
- **H2, Appendix B's runtime table.** `s8_runtime.py` gains `round4_queue`: 30 runs, 26.48 h (X3 24 runs, 17.7 h; X4 6 runs, 8.8 h), matching F5's gate. Every field it wrote before is unchanged (asserted on the regenerated JSON).
  - **How runs are timed:** `runs/queue_round4.log` lost the first runner's lines (OUT_OF_SCOPE), so it times only 4 runs; the other 26 are timed by their weights files (end = modification time, start = end − `wall_clock_s`). Those windows abut within seconds, start at the logged 10:36 launch, and agree with the log to the minute where both exist.
  - **Overlaps:** against `docs/presubmission/round4/f9_cpu_jobs.json` (new, from `f9_cpu_jobs.py`). It holds each session F1–F4's window, from the first to the last of its evidence files inside the queue's windows. Grouping into separate jobs was tried and dropped: it misses one-file jobs, such as X8's 9-minute dry runs.
  - **Result:** 4 runs overlapped logged work (x3 A/B fold {0, 2} seed 0, x3 A/B fold {7, 9} seed 0). The resumed runner's runs overlap none, because that session logged nothing; Appendix B says so.
  - **In the paper:** Appendix B's prose and four new table rows, 11 new keys.
- **H3, round 3's leftovers.**
  - (a) C7.1 now also counts the items of BUILD_CHECKS' typed list of claims withdrawn on evidence (8, the count). A planted dropped item is caught, and 68/68 corruptions are still caught.
  - (b) `task2_3_matched_and_trend.py` records each trend cell's n_independent, asserted constant across checkpoints. Stage 15 was regenerated: every other field is unchanged, the report is byte-identical, and Appendix H's R-46 row now names n_independent = 4 (400-step trajectories) and 16. `r46_o_nind` is asserted equal to `m23_nind`.
  - (c) §5.2's per-configuration readings are confirmed in place (F4, A4b): the "Per configuration … Per episode …" sentences, guarded by C28.3.
  - Round 3's R5 (a2's difficulty mean over two action offsets) was handled in F3 (N6, D-39).
- **H4, typesetting.** `md_to_tex.py` lets a code-span path break after "/" and "_" and before its extension, as table cells could; doubled break marks in cells are collapsed. Measured by compiling a copy with underfull reporting on (`\hbadness` lowered from the paper's 10000; `R4F9/h4/stretch.py`): stretched lines fall from 12 to 2, those holding a path from 1 to 0, and the page count stays 75. Page 53, where the one stretched path line was, was rendered before and after and looked at: the line now sets normally. `pdf_render_check` 5/5.
- **H5, bundle self-test at HEAD** (9281201). `make_anon_bundle.py` planted its probe, including HEAD's latest full commit hash, and detected it (9 hits; its assertion on the hash pattern passed); 566 files staged, 0 residual identifying hits (`R4F9/h5_bundle.log`). The run also rewrites `docs/COMMIT_LABEL_MAP.json` (99 labels added, none changed) and `results/anon_bundle.json` (no ZIP written). Both were restored, because F11 rebuilds the bundles.
Build/gates: pass. Evidence summary (unchanged), fast build, every gate, `part_f_gate`, fast build again: byte-identical. 68/68 claims and 68/68 corruptions; compile 75 pages, 0 overfull, 0 warnings. `part_f_gate` 6/7, 1 not run: 4b fails on the bundles (F11).
Paper numbers changed: tn_typed 1141 → 1144 (results/typed_numerals.json)
New keys: 11, from results/: `rt_r4_runs`, `rt_r4_hours`, `rt_r4_x3_runs`, `rt_r4_x3_hours`, `rt_r4_x4_runs`, `rt_r4_x4_hours`, `rt_r4_overlapped`, `rt_r4_by_log`, `rt_r4_table` (presubmission_runtime.json); `r46_o_nind`, `r46_i_nind` (task2_3_matched_trend.json)
Re-anchored checks: none (C7.1 tightened: it also checks the enumeration's length)
CPU jobs over 1 min: the six re-runs, uncontended (X3 46 s, X4 40 s, X6 92 s, X7 38 s, N5 41 s, X8 259 s), then X6 and X7 again without runs/; stage 15 (about 3 min); two diagnostic compiles; the bundle self-test (over 5 min); fast builds with gates, about 1.5 min each. None contended (no training).
Queue status: done (30 of 30)
Body words (round2/t6_words.py): 17,790 (F0: 20,745; accepted, DECISIONS.md#F8-length)
Abstract words / numerals (C12.1): 300 / 19
Next: F10 (Opus 5.5, high), the fresh-eyes review: read the main text once from `pdftotext` (References start on page 27), two read-only reviewers for Appendices A–M and N onward, REVIEW.md and CONSISTENCY.md. Note that `pdftotext` is not installed here; pypdf extracts text. Commits stay local.
Decisions for user: none
