# Round-5 session log

Entries follow PLAN §1.4's template, newest last.

## G0 — 2026-10-19 — Sonnet 5.5, medium — status: COMPLETE
Commits: 2b5206a [G0][1] Round-5 plan and the 19 Oct review (verbatim, byline removed)
         defce9c [G0][2-3] Round-5 files, four subagents, launcher; settings.local.json ignored
         (final [G0][4-8] commit: baselines, base_keys, CLAUDE.md round-4 section copy, this entry)
Review items closed: none
Done: Start gate passed: only `round5/` was untracked; HEAD 3869f97 descends from 796a026 and adds only round-4
  records (CHECKPOINT, FINAL_REPORT, SESSION_LOG); no source or ledger changes. Tagged `pre-round5`, created
  `presubmission5`. Created SESSION_LOG, DECISIONS (§0.3 table byte-identical to PLAN lines 101–115; "defaults
  accepted by launching G0, 2026-10-19"), OUT_OF_SCOPE (seeded), CHECKPOINT, LENGTH_LOG, RETIRED_KEYS, the four
  subagents, `go.zsh` (chmod +x, `zsh -n` clean), `.claude/settings.local.json` (ignored via `.gitignore`; it was
  already ignored globally too). `PDM/CLAUDE.md`: the "Finishing round 4" section copied verbatim to
  `round5/CLAUDE_md_round4_section.md` and replaced by Annex 5's round-5 block (that file is outside the repository);
  other lines unchanged. Bundle dry-run: both collectors (`build_supplementary`'s walk, `make_anon_bundle.collect()`)
  collect nothing under `round5/` or `.claude/` (540 and 564 files); `docs/presubmission` is an excluded directory
  and `.claude` is not in `INCLUDE_DIRS`. Baselines in `BASELINE_G0.md`, `base_keys.txt` (1,489 keys).
Environment: `claude --version` = 2.1.299 (≥ 2.1.271), so the subagents' `omitClaudeMd` is honoured.
  `~/Downloads/CLAUDE.md` is NOT in this session's context (only `PDM/CLAUDE.md` was loaded). You can confirm in a
  new session with `/memory`; `go.zsh` and `settings.local.json` both exclude it.
Build/gates: pass (fast build; ledger_check PASS; self-test 68/68; the six sweeps/audits exit 0). Built files
  reproduced the committed ones; PAPER.pdf restored with `git restore`.
Round-5 gates (report mode until G16): not yet available (G6 adds `round5_gates.py`); baseline: pages 75 total /
  ~26.9 main, abstract 300 words / 19 numerals, main-text rule IDs 26 M- + 25 X (distinct 18 + 8), commit labels 0,
  capitalised verdict labels 8 (PARTIAL ×7, SUPPORTED ×1), keys base 1,489
Paper numbers changed: none
New keys: none
Ledger: none
Re-anchored checks: none
CPU jobs over 1 min: none (build 11 s)
Queue (Y5): not launched (Y5 default B; GT1 will pre-register and launch)
Body words / main-content pages: 17,804 / 26.9 (G0: 17,804 / 26)
Subagents: none
Next: G1 (`docs/presubmission/round5/go.zsh G1`).
Decisions for user: none. Notes: (1) the abstract is 300 words/19 numerals vs Y2's 210/5. (2) I counted main-content
  pages as 26.9 (heading position on page 27), PLAN says 26. (3) Several round-4 commits and this round's are local only.

## G1 — 2026-10-19 — Sonnet 5.5, high — status: COMPLETE
Commits: e2b0e89 [G1][2-3] Version crosswalk: script, artifact (25 claims, RWM v1-v5, RWM-U v1-v3), FILE_MAP row
         7fcf186 [G1][1,4] Premises P1-P40, crosswalk summary with upstream-code section, six out-of-scope lines
         (final [G1][5] commit: this entry and the checkpoint)
Review items closed: evidence gathered for RV09–RV13, RV31, RV39 (`PREMISES.md`, `CROSSWALK.md`); no review item is fixed (no paper edits).
Done: Start gate passed (G0 COMPLETE). Read the review. `PREMISES.md`: 40 premises — TRUE 32 (P15, P20, P39 with a qualification), PARTLY 8 (P2, P3, P6, P12, P22,
  P23, P28, P40), FALSE 0 — plus three findings the review did not raise (B1–B3). Downloaded RWM v1–v5 and RWM-U v1–v3 (PDF,
  HTML, abstract page) to `docs/presubmission/sources/g1/` (gitignored; SHA-256 in the artifact). **OpenReview forums `u76d3gBWCX` and `mcwLgO93ym`
  could not be fetched** (browser challenge, HTTP 403; not bypassed), so no workshop text exists locally. `scripts/version_crosswalk.py` →
  `results/version_crosswalk.json` (25 claims; no 12, moved 7, reworded 3, new 3, removed 0; deterministic on re-run). Upstream: cloned both to
  `/Users/Shared/rwm_verify/upstream_latest/`; **0 commits since either pin**, clones equal the pinned copies.
Findings that matter downstream:
  1. RWM v1 has no 6M-against-250M table; it is Table 1 in v2+. The paper and `results/original_paper_figures.json` call it v1's "Table I" (B1).
  2. The released imagination env feeds back one random member per environment; the paper (and X9's baseline) describe only the ensemble-mean path (B2). X9 in G2/G3 must say which it contrasts.
  3. `rsl_rl_rwm` does per-head bootstrap resampling in the MBPO-PPO update (`bootstrap=True`); the offline `robotic_world_model_lite` path does not (P12).
  4. Both papers set forecast decay α = 1.0; C-09 is a naming difference, not a gap (P14–P15). v3 of RWM-U changed no rollout text; it added the "effectively propagated" claim (P8).
  5. Both follow-ups are workshop posters on the venue pages, archival status unstated (P6; the venue pages were read through a summarising fetch, so quotations are as returned).
  6. The claim that the released checkpoint trained on exactly our ten episodes is an assumption (`scripts/insample_framing.py:37`) (P20).
  7. P22: 25 CPU-h needs one ensemble-5 seed per fold; stored ensemble-5 runs cost 4.0–4.4 h each, so three seeds is about 50 h. GT1 must project from probes.
Build/gates: pass (fast build, ledger_check PASS, self-test, typed_numeral_audit, restatement_index, horizon_sweep, xref_sweep, check_scope_audit, pdf_render_check all exit 0); no tracked paper file changed; `PAPER.pdf` (date only) restored with `git restore`. Second build not needed: nothing changed.
Round-5 gates (report mode until G16): not available until G6
Paper numbers changed: none
New keys: none
Ledger: none
Re-anchored checks: none
CPU jobs over 1 min: none (the crosswalk check takes about 1 min including PDF text extraction; no training)
Queue (Y5): not launched
Body words / main-content pages: unchanged (17,804 / 26.9)
Subagents: rwm-sources × 2 (venue pages and OpenReview; TMLR and MLRC policy pages). Both read through a summarising fetch tool; the results are recorded in `PREMISES.md` as such.
Next: G2 (Opus 5.5, high) — analysis protocols committed before any data. Read PREMISES B2 and P12 before specifying X9.
Decisions for user: none required. Optional: the venue question in P6 (what the paper may call the two follow-ups) can wait for G7/G14.

## G2 — 2026-10-19 — Opus 5.5, high — status: COMPLETE
Commits: 2d71330 [G2] PRE-REGISTER (rule text) X9 and X10; specifications for N7–N14
         (final [G2] commit: this entry, the checkpoint and two out-of-scope lines)
Review items closed: design of RV15–RV17, RV19, RV20, RV24–RV28, RV42 (Annex 1) in `round5/PROTOCOLS.md`; no measurement yet.
Done: Start gate passed (G1 COMPLETE). One `rwm-reader` call located the scorers, builders, bootstraps, cache keys, action
  offsets and weight paths; I verified every cited file:line before committing (several were corrected by 1–3 lines,
  and the trainer class is `RWMEnsemble`). Before the commit there was no `x9_*`, `x10_*` or `n7_*`–`n14_*` file in
  `results/`, `scripts/` or `cache/`, and all 23 weight files X9/X10 need exist. `PROTOCOLS.md` holds: X9 (MEAN = the
  release's evaluation path, called through the existing functions unchanged; PER-MEMBER = TS∞ with one trunk pass per
  member at MEAN's batch shape; four verdict labels, adding WIDENS THE GAP; assertions (i)–(iv)); X10 (Q = ρ_in/ρ_out,
  draw order fixed, training split asserted from the run records); X11 skeleton for GT1 (Y5 = B, so no X12); N7–N14 with
  inputs, formulas, tolerances, assertions, outputs, keys, stages 20v1–20v2 and 20w7–20w14. Thresholds fixed here: N8
  ±2σ tolerance 2.5 points; N10 period window [10, 100] steps with a two-commit procedure; N11 Kendall as point estimates
  only (no scipy in the venv; none added). §7 lists the 11 changes from Annex 2; each tightens or fills, none loosens.
Findings that matter downstream:
  1. N7: the stored n = 4 tests are exact *bootstrap* tests (`P5.boot_p`), whose smallest p is 2/256; an exact sign-flip
     test's smallest p is 0.125, above every Holm level in the sweep, baseline and X4 families. N7 records `can_any_reject`.
  2. N10: nRMSE divided by the RMS of σ is form 1 times a constant κ = mean σ / RMS σ, so model rows need no re-roll.
  3. M-43's statistic is a pooled correlation with no per-trajectory decomposition; N7 tests a within-trajectory
     estimand and labels it so.
  4. X9 (d)'s one-member check must compare our trainer's class with `ReferenceRWM`; tolerance 1e-5, the precedent
     `task_d3_ens5.py:127-128` set.
Build/gates: not run (no text, number or generator changed); `ledger_check.py` PASS.
Round-5 gates (report mode until G16): not available until G6
Paper numbers changed: none
New keys: none (keys are specified in PROTOCOLS.md for G3/G4)
Ledger: none (G3 adds X9 and X10's PRE-REGISTERED entries with their scripts)
Re-anchored checks: none
CPU jobs over 1 min: none
Queue (Y5): not launched (GT1)
Body words / main-content pages: unchanged (17,804 / 26.9)
Subagents: rwm-reader × 1
Next: GT1 (Y5 = B; Opus 5.5, high) — complete PROTOCOLS.md §4, probe, pre-register and launch the queue. Then G3.
Decisions for user: none

## GT1 — 2026-10-19 16:55 — Opus 5.5, high — status: COMPLETE
Commits: dbecbf0 [GT1][3] Training support for X11: step5_train --holdout with --ensemble 5 (five lines changed in place, none moved); queue_run's x11-e5 trainers; fold checks (a)-(c) pass, (b) bitwise
         e1a92d0 [GT1][1] X11 power before any fold run: M-43's criterion and M-44's MDE at n = 20 by the n = 4 code (results/x11_power.json); n = 4 reproductions pass
         99f6bd2 [GT1][5] Timing probe on an idle machine: 55.5 CPU-h projected for 20 runs; cap 62 h by ruling GT1-cap
         1a2f021 [GT1] PRE-REGISTER X11a-X11d (M-97 to M-100) and the X11 rule text, before any X11 run exists
         bcc3f6e [GT1][6] Launch: 20 X11 runs queued at 16:44:57 (+0530), projected 55.5 CPU-h against the 62 h cap, finish about 2026-10-22 00:15
         21d0a3d [GT1] Build and gates after the pre-registration: n_entries 288 -> 292, ledger_kb 658 -> 679; no paper edits
         (final [GT1][close] commit: this entry and the checkpoint)
Review items closed: RV20 (launch) (Annex 1).
Done:
- **How this session ran.** In the same conversation as G2, at the user's request ("Start GT1. Raise the 30 CPU-hour cap if
  needed"); the plan assigns a fresh terminal (Y13). Recorded in `DECISIONS.md#GT1-cap`. No subagent.
- **Cap ruling.** The user raised Y5's 30 CPU-hours. Recorded before the probe as 1.10 × the probe's projection, rounded up;
  set after it at **62 h** (projected 55.5 h). The stored run records had already put it near 56 h, so B's 30 h was never reachable.
- **Item 3, training support.** `scripts/step5_train.py --holdout` now takes `--ensemble 5` for Arm A. Five lines changed in place,
  none moved; the eight cited lines (`:64`, `:122-147`, `:138`, `:173`, `:184`, `:205`, `:244`, `:289-321`) stay put; nothing hashes the
  file. `scripts/queue_run.py` gained `x11-e5-<fold>` and an `ensemble` check. `round5/gt1_fold_support.json`:
  - (a) windows per fold equal every committed run's `n_train_windows`, and {1, 8} has round 4's SHA-256;
  - (b) three 50-iteration runs reproduce the committed loss traces **bitwise**: ensemble-5 via `--holdout 1,8` and via the
    default path, and single-model seed 3 via `--holdout`;
  - (c) every fold excludes exactly its two episodes.
- **Item 1, the rules.** `PROTOCOLS.md` §4 is complete: runs, readings, MDEs and seven listed changes from the discharged rules.
  `scripts/x11_power.py` → `results/x11_power.json`, written before any fold run. Assertions: M-43's n = 4 power was replayed exactly;
  M-44's n = 4 per-pair values match to 1e-12, and its binding MDE is within 5% (the draws can't be replayed, because they share a
  generator with M-45). At n = 20, on an in-sample pool (so upper bounds), M-43's criterion fires on most draws; M-44's binding MDE
  barely shrinks (`m44.n20`).
- **Item 2, reading scripts.** `scripts/x11{a,b,c,d}_*.py` plus `scripts/x11_common.py`, one per rule, each copying the discharged
  code with file:line. Each `--assert-only` reproduces its fold-{1, 8} artifact with maximum difference **0.0**
  (`task_d3_ens5.json` calibration, governing and M-43 verdict; `task_d3_perhorizon.json`; `r2_independent_ensemble.json`).
  Dry runs of every `reading()` on substituted weights ran end to end from a harness in the scratchpad; their numbers are a code test
  and are not recorded. Each reading refuses to run unless its ledger entry records the SHA-256 of its frozen files; tested both ways.
  A missing run record stops a reading with `FileNotFoundError` (no output written), not a `.blocked` record.
- **Item 4, ledger.** M-97 (X11a), M-98 (X11b), M-99 (X11c), M-100 (X11d), PRE-REGISTERED, written by `round5/gt1_write_prereg.py`.
  Every figure in them is read from an artifact; the writer checks that the evidence logs name each frozen file's current SHA-256.
  RESULTS.md M- 96 → 100. IDs are max + 1, as round 4 did; `ledger_check.py` has no allocator.
- **X11e** (X9 on the fold ensemble-5 arms): rule text in §4. **Its script is G3's**: arena tag `fold_e5` inside
  `scripts/x9_per_member_propagation.py`, frozen in G3's PRE-REGISTER commit, before GT2. Its ledger entry is also G3's.
- **Item 5, timing.** `scripts/round5_queue_timing.py` → `results/round5_queue_timing.json`, on mains power with nothing else
  running. Ensemble-5 4.13 h per run, single model 0.74 h.
- **Item 6, launch.** `runs/queue_round5.txt` was written from the record and launched at 16:44:57 under `nohup caffeinate -i`.
  Runner PID 14182; log `runs/queue_round5.log`; sentinel: the log's last line "queue empty; runner exits" with 20 done, 0 failed.
  The first run passed 50 iterations with finite losses (iteration-0, 25 and 50 lines only). `round5/RUN_QUEUE.md` has the status
  command and the restart procedure.
- The machine was on battery earlier in the session; it was on AC power for the probe and the launch.
Build/gates: pass. Fast build, all eight gates, fast build again: PAPER.md, PAPER.tex, MODEL_CARD.md, README.md and docs/BUILD_CHECKS.md byte-identical; ledger_check PASS (M-97 to M-100 pending).
Round-5 gates (report mode until G16): not available until G6
Paper numbers changed: n_entries 288 → 292; ledger_kb 658 → 679 (FINDINGS_LEDGER.md)
New keys: none
Ledger: M-97, M-98, M-99, M-100 (PRE-REGISTERED)
Re-anchored checks: none
CPU jobs over 1 min:
- fold support (b), three 50-iteration runs, about 12 min (contended with x11_power);
- x11_power, twice, about 2 min each;
- x11b `--assert-only`, about 4.6 min, twice;
- the dry runs, twice, about 20–25 min each;
- the timing probe, 2.2 min (idle);
- build and gates, 96 s (contended with the queue's first run).
Queue (Y5): running (0 of 20 done at 16:50; projected finish about 2026-10-22 00:15 +0530)
Body words / main-content pages: unchanged (17,804 / 26.9)
Subagents: none
Next: G3 (Opus 5.5, high) — X9 (with X11e's `fold_e5` arena in the same frozen script) and X10. It runs while the queue trains;
  log every job as contended, and read no queue-run log except through RUN_QUEUE.md's filter.
Decisions for user: none (ruling this session: DECISIONS.md#GT1-cap)

## G3 — 2026-10-19 18:50 — Opus 5.5, high — status: COMPLETE
Commits: 8a34451 [G3] PRE-REGISTER X9 and X10: ledger entries and scripts (M-101 X9, M-102 X10, M-103 X11e)
         5b9dc56 [G3][4-5] Run and discharge X9 and X10: X9 PROPAGATION NARROWS THE GAP for all four models at h = 100 (two at n = 4, descriptive); X10 IN-SAMPLE IS WORSE at h = 1 (IN-SAMPLE FLATTERS at h = 100)
         9ea6d42 [G3][6] Stages 20v0-20v2 (all NEEDS_WEIGHTS: X9's frozen script reads our arms with the released checkpoint), 184 keys for X9 and X10 with intervals; build and gates pass, second build byte-identical
         (final [G3][close] commit: this entry and the checkpoint)
Review items closed: RV15, RV16 (data) (Annex 1).
Done:
- **How this session ran.** In the same conversation as G2 and GT1, at the user's request ("Start G3"); the plan assigns a fresh
  terminal (Y13). No subagent. Evidence: `/Users/Shared/rwm_verify/evidence/R5G3/`.
- **Item 1, scripts.** `scripts/x9_per_member_propagation.py` and `scripts/x10_insample_vs_heldout.py`, to PROTOCOLS §2–§3.
  - MEAN calls `rollout_uncertainty` and `rollout_independent` unchanged.
  - PER-MEMBER runs one trunk pass per member at MEAN's batch shape (`step_heads` = `score_reference.py:94-105`).
  - X11e's arena is the `--x11e` mode, written to its own artifact, `results/x11e_fold_e5_propagation.json`.
  - Both scripts carry the ledger-hash guard.
  - Deviation: PLAN's file name `x9_ts_inf_propagation` was not used; PROTOCOLS, committed first, names
    `x9_per_member_propagation`.
- **Item 2, assertions.**
  - X9's (ii) failed on the first run (6.4e-7), then by 7.1e-15. The cause was located on step-1 values only: the members' mean and
    the statistics were reduced on arrays of a different shape or memory layout than MEAN's, so they differed in the last place.
    Every head output and the spread were bitwise identical, and no per-member number had been computed.
  - **The user ruled "Fix and re-assert"** (`DECISIONS.md#G3-assert-ii`). The mean and spread are now taken per step with MEAN's own
    `torch.stack(...).mean(0)`, on C-contiguous arrays. The tolerance stayed 0.0.
  - Then all passed: X9 (i) 0.0 relative on all three artifacts, (ii) 0.0, (iii) predictions 0.0 and relative-L1 1.2e-7, (iv) pass;
    X10 (1) 0.0, (2)–(3) pass, (4) 0.0.
  - Dry runs of both readings on **untrained random weights** (code test only; numbers meaningless and not recorded).
- **Item 3, ledger.** M-101 (X9), M-102 (X10), M-103 (X11e), with rule text verbatim from PROTOCOLS. Two mechanical changes: bold
  subheadings, and one `.blocked` path split. Written by `round5/g3_write_prereg.py`. RESULTS.md M- 100 → 103.
- **Item 4, readings** (contended with the queue: X10 21 s, X9 91 s). Per-trajectory timing was not probed separately, since the
  untrained dry runs showed minutes.
  - **X9, h = 100: PROPAGATION NARROWS THE GAP for rel, e5, ind and fold** (e5 and ind at n = 4, descriptive, p = 0.125).
  - Fraction of the gap closed, f: rel 0.75 [0.69, 0.82]; fold 0.71 [0.67, 0.76]; e5 0.80; ind 0.88. Per-member ±1σ coverage is 33–60%,
    still below X7's band. CRPS and NLL improve as well. At h = 368 the n = 4 ensembles overshoot (f > 1, ρ below √(2/π)).
    The per-member aleatoric σ is at most 0.12 of the error (`x9_alea_over_err_max`).
  - **X10: IN-SAMPLE IS WORSE at h = 1**: Q = 1.79 [1.06, 2.65], all three seeds above 1. **At h = 100 and h = 368 the label it would carry
    is IN-SAMPLE FLATTERS** (Q 0.72 and 0.73, intervals below 1).
  - At h = 1 the ratio and the ±1σ coverage disagree: ρ 3.80 in against 2.13 out, coverage 35.0% against 35.9%. **The reading splits by
    horizon and by statistic; any summary must say so (PLAN rule 10).** The §6.2 framing "in-sample flatters" is G5's to withdraw or qualify.
- **Item 5, discharge.** Verdicts verbatim in M-101's and M-102's Status lines; M-103 pending, awaiting GT2.
- **Item 6, stages and keys.**
  - Stages: 20v0 (GT1's `x11_power`, which had none), 20v1 (X9) and 20v2 (X10).
  - Deviation: all three stages are NEEDS_WEIGHTS. X9's frozen script reads the released checkpoint and our arms in one run, so its
    released part cannot be a separate stage without changing a pre-registered script.
  - 184 keys `x9_*` and `x10_*`, intervals included, appended after the last block of `paper_numbers.py`. No cited line moved;
    the highest cited line is 2871.
Build/gates: pass. Fast build, all eight gates, fast build again: PAPER.md, PAPER.tex, MODEL_CARD.md, README.md, docs/BUILD_CHECKS.md byte-identical; ledger_check PASS (M-97–M-100, M-103 pending); pipeline_coverage pass.
Round-5 gates (report mode until G16): not available until G6
Paper numbers changed: n_entries 292 → 295; ledger_kb 679 → 702 (FINDINGS_LEDGER.md)
New keys: 184 (`x9_*`, `x10_*`; results/x9_per_member_propagation.json, results/x10_insample_vs_heldout.json)
Ledger: M-101, M-102 (PRE-REGISTERED → DISCHARGED); M-103 (PRE-REGISTERED)
Re-anchored checks: none
CPU jobs over 1 min: X9 --assert-only ×4 (about 1 min each); the untrained dry runs (about 5 min); X9 reading (91 s); build and gates (88 s). All contended with the X11 queue.
Queue (Y5): running (0 of 20 done at 18:50; the first run at iteration 1,325 with finite loss; projected finish about 2026-10-22 00:15)
Body words / main-content pages: unchanged (17,804 / 26.9)
Subagents: none
Next: G4 (Sonnet 5.5, high) — post hoc N7–N14 per PROTOCOLS §5. N7 item 8 can now include X9's (a) and (d) per-trajectory values. Beside the queue.
Decisions for user: none (ruling this session: DECISIONS.md#G3-assert-ii)

## G4 — 2026-10-19 21:10 — Opus 5.5 (the plan assigns Sonnet 5.5), high — status: COMPLETE
Commits: 302e66d [G4][N8] The tails (post hoc, R-81): 30 of 48 M-65 cells heavy-tailed, 18 mixed, 0 near-Gaussian; coverage-matching multiplier per cell; stage
         0f049b5 [G4][N7] Exact sign-flip tests (post hoc, R-82): 260 comparisons, 228 at n = 4 (154 at the minimum p = 0.125); no Holm family can reject under
         f880529 [G4][N9] The per-horizon recalibration scored (post hoc, R-83): +-1 sigma restored, +-2 sigma 84-86% against 95%, CRPS and NLL improve, interv
         a54d5c5 [G4][N10] Floors script with --period and PERIODS unset (commit A, before any period or score exists); ruling G4-n10-pooled
         be19443 [G4][N10] Fix the seasonal periods from training episodes
         bd4c27f [G4][N10] Floors (post hoc, R-84): the training mean is a stronger floor than hold-last at long horizon on every arena; seasonal-naive no bett
         eb21e80 [G4][N11] Rank correlations (post hoc, R-85): from h = 8 on, Spearman disagreement-error 0.82-0.92 and its lead over the index resolved at eve
         39042d8 [G4][N12] Provenance (post hoc, R-86): the checkpoint stores no data statistic, hash or path; its one-step error shows no in-sample/held-out g
         b87abbf [G4][N13] Adam (post hoc, R-87): default betas, collapse at a median 0.936 learning rates per iteration, variance state unreachable even at th
         7a326c3 [G4][N14] One-step accounting (post hoc, optional, R-88): no ensemble's spread accounts for its one-step error; released R = 174, ensemble-5 7
         3571e0f [G4] Build and gates after N7-N14: n_entries 295 -> 303; no paper edits; second build byte-identical
         (final [G4][close] commit: this entry and the checkpoint)
Review items closed: data for RV17, RV19, RV24, RV25, RV27, RV28, RV42; inputs to RV26 (Annex 1).
Done:
- **How this session ran.** In the same conversation as G2, GT1 and G3, at the user's request ("Start G4"). The plan assigns
  Sonnet 5.5 in a fresh terminal. No subagent. Taken in the plan's order: N8, N7, N9, N10, N11, N12, N13, N14 (N14 kept by
  PROTOCOLS). Each has its own script, artifact (`post_hoc: true`, `never_reopens`), ledger entry, stage and keys.
  Evidence: `/Users/Shared/rwm_verify/evidence/R5G4/`.
- **N8 (R-81).** 30 of M-65's 48 cells are heavy-tailed (±1σ over, ±2σ under), 18 mixed, 0 near-Gaussian.
  - Every OVER-DISPERSED cell is heavy-tailed or over-covers at ±1σ only.
  - All 15 "adequate" cells under-cover at ±2σ.
  - The coverage-matching multiplier is per cell; at h = 1 on the released checkpoint it is 6.6 (`n8_k_rel_epi_h1`).
- **N7 (R-82).** 260 comparisons; 228 at n = 4, of which 154 reach the minimum p = 0.125.
  - No Holm family (sweep, M-75, M-76, X4) could reject anything under an exact test.
  - X3's episode-level test at h = 368: p = 0.0020.
- **N9 (R-83).** The per-horizon multiplier restores ±1σ at every horizon, but ±2σ reaches only about 84–86% against 95.45%.
  CRPS improves and NLL falls by orders of magnitude; the intervals widen many-fold.
- **N10 (R-84).** Periods fixed from training episodes in their own commit (`be19443`): 26–27 steps; no fallback was needed.
  - The training-mean predictor is a stronger floor than hold-last at h = 368 on every arena and metric.
  - **At h = 100 on the held-out pair's relative-L1, hold-last is lower (0.756 against 0.838).** R-84's "at long horizon" means
    h = 368. The ledger is append-only, so not edited; G5's summary must state this.
  - κ = 0.957; seasonal-naive is no better than hold-last.
- **N11 (R-85).** The ranking findings are stronger under ranks from h = 8 on (Spearman disagreement–error 0.82–0.92), and the lead
  over the index is resolved at every h ≥ 8.
  - At h = 1, Pearson (0.994) is higher than Spearman (0.829).
  - The e7 step-size margin, below M-51's MDE under Pearson, has an interval above zero under ranks. M-51's verdict stands (Y8).
  - **A first draft of R-85 said "every horizon"; that was false at h = 1.** Caught before commit, the ledger restored from the
    helper's backup, and re-appended correctly, with the claims now asserted in code. The draft never reached git.
  - Runtime about 40 minutes.
- **N12 (R-86).** The checkpoint stores no data statistic, hash or path (`iter` 5,000, `infos` None); the upstream repository has no tags.
  - Arm A's one-step error: 0.075 in-sample against 0.117 held-out (intervals disjoint).
  - The released checkpoint: 0.083 against 0.085 on the same episode groups (intervals overlapping). That is consistent with it
    training on all ten episodes, or on none.
  - 14 artifacts carry in-sample wording. A bug in the data-key filter (it matched network weights) was fixed before recording.
- **N13 (R-87).** Adam defaults are β = (0.9, 0.999), ε = 1e-8. The collapse moves at a median 0.936 learning rates per iteration;
  the worst-case Adam step is 3.16× the learning rate.
  - The variance state needs 144,632 iterations at a typical step and 45,737 at the worst case, against the stated 500, 2,500 and 5,000.
  - 342 checkpoints match their logs within one step.
  - The typed −14.4629 is a defect (the checkpoint holds −14.463197); recorded, with a line in OUT_OF_SCOPE.
  - The X11 queue's records are excluded, so the artifact stays fixed at the 81 records PROTOCOLS named.
- **N14 (R-88).** At one step no ensemble's spread accounts for its error: released R = 174 [82, 255], ensemble-5 7.6, independent 2.6.
- **Assertion failures and rulings:**
  - N7's a1 point check (float32): ruling `DECISIONS.md#G4-n7-a1`.
  - N10's pooled convention on the fold arena, asked before any scoring: `#G4-n10-pooled`.
  - N10's own added floor check (float32 against float64): recorded, not a ruling, `#G4-n10-floorcheck`.
  - N13's checkpoint constant: `#G4-n13-ckpt`.
  - Every `.blocked` first-run record is kept in the evidence folder.
- **Power.** The machine was on battery for about an hour mid-session (down to 51%); back on AC by N9. The queue was not interrupted.
Build/gates: pass. Pipeline coverage, fast build, all eight gates, fast build again: PAPER.md, PAPER.tex, MODEL_CARD.md, README.md, docs/BUILD_CHECKS.md byte-identical; ledger_check PASS.
Round-5 gates (report mode until G16): not available until G6
Paper numbers changed: n_entries 295 → 303; ledger_kb 702 → 725 (FINDINGS_LEDGER.md)
New keys: 618 (`n7_*`–`n14_*`, from results/n7_exact_tests.json … results/n14_one_step_accounting.json)
Ledger: R-81 (N8), R-82 (N7), R-83 (N9), R-84 (N10), R-85 (N11), R-86 (N12), R-87 (N13), R-88 (N14), all post hoc, CONFIRMED, CONTRIB; RESULTS.md R- 80 → 88
Re-anchored checks: none
CPU jobs over 1 min: N7 (about 6 min, twice); N9 (about 1 min); N11 (about 40 min, background); N13 (about 1 min, three times); build and gates (95 s). All contended with the X11 queue.
Queue (Y5): running (1 of 20 done at 21:05: `x11_e5_02_s0`; the second started 20:51; projected finish about 2026-10-22 00:15)
Body words / main-content pages: unchanged (17,804 / 26.9)
Subagents: none
Next: G5 (Opus 5.5, medium) — readings into the record. It must carry R-84's h = 100 exception and X10's horizon split into READINGS.md.
Decisions for user: none pending (rulings this session: DECISIONS.md#G4-n7-a1, #G4-n10-pooled, #G4-n13-ckpt)

## G5 — 2026-10-19 21:32 — Opus 5.5 (the plan assigns medium effort), high — status: COMPLETE
Commits: dc0d0a0 [G5][1-3] Readings into the record: S-22, S-23, S-24, C-17, C-18, R-89; M-65, M-96, C-04, C-11 Status lines
         c39d6b8 [G5][4] READINGS.md
         dc5ec61 [G5][5] Build and gates: retraction counts re-derived; BUILD_CHECKS' enumeration gains S-22; the external brief's counts
         (final [G5][close] commit: this entry and the checkpoint)
Review items closed: RV12, RV13, RV24, RV26 (record); inputs to RV14 and RV17 (Annex 1).
Done:
- **How this session ran.** In the same conversation as G2–G4, at the user's request ("Start G5"). No subagent.
- **Item 1, M-65.** S-22 (evidence class) withdraws M-65's reading "NOT HEAVY-TAILED in every one of 48 cells", its "Gaussian
  nominal is defensible", and its "no single lambda repairs" argument, with **Retracts** `M-65` and `M-96` (M-96's sentence that
  the reading stands). It points at R-81, and states the coverage-matching multiplier as Y7's "too small by".
  - M-65's Status is now "… its returned reading SUPERSEDED by `S-22`"; M-96 is "SUPERSEDED IN PART". Neither was CONTRIB.
  - No check asserted the withdrawn reading (grep of `check_comparative_claims.py` and every template), so no expectation changed.
- **Item 2.**
  - C-17 corrects C-09. Both papers set α = 1.0 (RWM v1 Table S9, RWM-U v1 Table S8), so it is a naming difference, not a gap;
    PLAN's withdrawal condition ("RWM's own paper sets none") is false. The same entry covers Table S8 for the training length.
  - C-18 (new): per-head bootstrap resampling exists in the MBPO-PPO path, not in the offline path our arms follow
    (`step5_train.py:259` passes no `bootstrap`).
  - S-23 (framing) withdraws C-04's presentation of the shared state trunk as undisclosed (RWM-U v1 §4.1 states it). C-04 is
    marked SUPERSEDED IN PART; its facts and X-12 stand.
  - R-89 corrects R-75's circular count to three counts read from the artifact.
- **Item 3, framings, grepped first.**
  - S-24 withdraws C-11's "the floor freezes, and nothing can reopen it": `step6_3_min_logstd.json` shows the floor moving at
    5.2× slower than log δ. C-11 is marked SUPERSEDED IN PART.
  - "No single λ" lived only in M-65 and goes with S-22.
  - "In-sample flatters calibration", "under-penalised", "provably" and "aware of" appear in no ledger entry. They are wording
    changes; READINGS.md lists their template lines (19, 59, 585, 595, 632).
- **Item 4.** `round5/READINGS.md`, 1,370 words. Every reading has its keys and scope: Y7's factor per horizon is `n8_k_rel_epi_h*`,
  and N12's provenance sentence is in it. Every number in it is a key name; three typed numbers caught and replaced before commit.
- **Item 5.** Two gates failed on the first pass, both stale counts the new S-22 exposed:
  - C7.1: `BUILD_CHECKS.template.md`'s typed enumeration listed 8 evidence retractions. S-22 was added.
  - C11.3: `docs/EXTERNAL_READ_BRIEF.md`'s sentence had been stale since before this round ("20 … seven … six"). Its counts are
    now written from the keys.
  - No check loosened. Then all passed.
Build/gates: pass. Fast build, all eight gates, fast build again: PAPER.md, PAPER.tex, MODEL_CARD.md, README.md, docs/BUILD_CHECKS.md byte-identical; ledger_check PASS (retraction classes 9 evidence, 8 framing, 7 early hypotheses; 24 superseded).
Round-5 gates (report mode until G16): not available until G6
Paper numbers changed: n_entries 303 → 309; ledger_kb 725 → 734; n_superseded 21 → 24; n_retractions 8 → 9 (and its word forms); n_retract_framing 6 → 8 (and word forms); n_retract_total 14 → 17; n_framing_cohorts 3 → 4 (ledger_check's classification, results/claims_to_evidence.json)
New keys: none
Ledger: S-22, S-23, S-24, C-17, C-18, R-89 (new); M-65 SUPERSEDED (its reading), M-96, C-04, C-11 SUPERSEDED IN PART
Re-anchored checks: none
CPU jobs over 1 min: build and gates, twice (about 70 s each; contended with the queue)
Queue (Y5): running (1 of 20 done at 21:32; the second, x11_e5_34_s0, started 20:51). The machine was on battery at the end of the session.
Body words / main-content pages: unchanged (17,804 / 26.9)
Subagents: none
Next: G6 (Sonnet 5.5, high) — tooling for a short paper.
Decisions for user: none

## G6 — 2026-10-19 21:55 — Opus 5.5 (the plan assigns Sonnet 5.5), high — status: COMPLETE
Commits: a77b262 [G6][1-2] Supplement and display precision; every prose check reads the supplement; scope audit fails on a per-claim gap
         a85d49e [G6][3-4] scripts/round5_gates.py with self-tests; remaining gate scripts recognise {{key|sN}}; FILE_MAP §3, BUILD_CHECKS
         (final [G6][close] commit: this entry and the checkpoint)
Review items closed: the tooling for RV01–RV05 and RV08 (Annex 1).
Done:
- **How this session ran.** In the same conversation as G2–G5, at the user's request ("Start G6"). No subagent.
- **Item 1, the supplement.** `docs/SUPPLEMENT.template.md` → `docs/SUPPLEMENT.md` is rendered in `build_paper.py`'s docs loop
  (`placeholders.DOC_TEMPLATES`).
  - Both bundle builders ship it: `make_anon_bundle.collect()` lists both files, `build_supplementary.py` walks `docs/` and
    excludes neither, and the anonymised build's `scan_tree` reads every staged file.
  - These read it: the comparative-claims checker (every `files` list naming a BUILD_CHECKS file now also names the supplement
    of the same tier, edited on the same line); the typed-numeral audit (scanned and failing like the template, counted apart so
    the paper's `{{tn_typed}}` is unchanged); the restatement index, horizon sweep and xref sweep (through
    `placeholders.with_supplement`).
  - `check_scope_audit.py` now requires the supplement per claim, not only per kind, and requires each sweep to name its
    supplement read. A gap now fails the audit, which is a tightening (0 gaps before and after).
  - `scripts/supplement_selftest.py` plants a violation in the supplement for all six tools; every one is caught, and every
    touched file is restored (SHA-256 verified).
- **Item 2, display precision.** `scripts/placeholders.py`: `{{key|sN}}` rounds every decimal to N significant figures,
  decimal half-up on the stored digits. Signs, brackets, %, ×, words, integers, versions and identifiers are unchanged.
  - The unit test passes 20 of 20 cases.
  - `build_paper.py`, `build_readme.py` and every gate script (`check_comparative_claims`, `typed_numeral_audit`,
    `restatement_index`, `horizon_sweep`, `part_f_gate`, `task_c1_claims_audit`, `c1_preflags`, `c1_diff_report`) recognise
    the form. All edits are in place, so no cited line moved. `e4_reply_draft.py` is left as it is: a correspondence generator
    with its own `|lower`.
- **Item 3, `scripts/round5_gates.py`.** pages, abstract, ids, once, sig, keys, each a pure function with corrupt-and-catch
  self-tests (all pass), run in `--report` mode. The definitions are in its docstring.
  - **The `once` gate's setting-key exemptions are a name pattern** (`SETTING_KEY`); the artifact lists those it applied
    (17 at this baseline).
  - **The `ids` gate's verdict vocabulary is harvested** from the bold capitalised runs in the ledger and PROTOCOLS, less acronyms.
  - Both are heuristics fixed here and open to G16's review.
  - The paragraph "The gates for a short paper" in `BUILD_CHECKS.template.md` names the gates without typed limits (it cites
    rulings Y1–Y3), so it adds no numeral and no key.
- **Item 4, against BASELINE_G0.**
  - Pages 26.87 (G0 "about 26.9"; same measurement, References at page 27, y = 152.4).
  - Abstract 300 words, 19 numerals (same).
  - Keys missing 0 (same: all 1,489 printed).
  - **ids 93, against G0's approximate counts** of 26 ledger IDs, 25 rule IDs and 8 verdict labels. Mine gives the same 26 and
    25 but 34 verdict labels: the harvested vocabulary also catches multi-word labels such as DOES NOT GENERALISE and MECHANISM
    SUPPORTED, which G0's pattern missed. It adds 8 code names used as labels (`entry-res`, `step-size`), which G0 did not count.
  - **sig 510, against G0's 514:** the gate exempts section, figure and table numbers, code in backticks, arXiv identifiers and
    versions.
  - once 33: G0 listed repeat counts but no violation count.
Build/gates: pass. Fast build, all eight gates, round5_gates --report, the supplement self-test, the placeholder unit test, fast build again: PAPER.md, PAPER.tex, MODEL_CARD.md, README.md, docs/BUILD_CHECKS.md, docs/SUPPLEMENT.md byte-identical. PAPER.pdf (date only) restored.
Round-5 gates (report mode until G16): pages 26.87/12, abstract 300/19, ids 93, once 33, sig 510, keys missing 0
Paper numbers changed: none
New keys: none
Ledger: none
Re-anchored checks: none (check_comparative_claims' file lists extended, check_scope_audit tightened)
CPU jobs over 1 min: the supplement self-test (about 50 s, twice); build and gates (152 s); contended with the queue.
Queue (Y5): running (1 of 20 done at 21:55; x11_e5_34_s0 started 20:51). The machine was on battery throughout this session.
Body words / main-content pages: 17,804 / 26.87
Subagents: none
Next: G7 (Sonnet 5.5, medium) — bibliography.
Decisions for user: none

## G7 — 2026-10-19 21:58 — Opus 5.5 (the plan assigns Sonnet 5.5, medium) — status: COMPLETE
Commits: [G7][1-3] scripts/t1_bibliography.py verifies DOI and proceedings-page records; fifteen entries; references 1 and 2 from the crosswalk
         (final [G7][close] commit: this entry and the checkpoint)
Review items closed: RV10, RV32–RV36 and RV46 at the reference list. The citations enter the text in G11–G15.
Done:
- **How this session ran.** In the same conversation as G2–G6, at the user's request ("Start G7"). One `rwm-sources`
  subagent (read-only) identified candidate records for the review's works. Every field it reported was then re-read by the
  tool itself; the subagent's report is not evidence.
- **Item 1, `scripts/t1_bibliography.py`.** An entry may now carry a `doi` (title, ordered full author list, venue and year
  from the Crossref record) or a proceedings `url` (from the page's citation meta tags or, on a volume page with none, from
  the page text, each field matched as whole words). An arXiv entry keeps arXiv as the source of title and authors, and may
  add a DOI or page to have its venue and year checked there, or a `venue_comment` matched in the arXiv comment. Absent
  fields leave the fingerprint unchanged, so all eighteen earlier entries still match their pins.
  - **`--verify --only k1,k2`** verifies only those entries and prints their records for pasting; it writes nothing.
  - **`--self-test`** (network) corrupts one field of each record kind and requires rejection: 10 of 10 caught, uncorrupted
    all pass. Two weaknesses it found were fixed before pinning. A prefix of a true name (Bagnel inside Bagnell) passed the
    PDF check, and a truncated title or editor name passed the volume-page check. Both are now whole-word matches.
  - `fetch()` retries a timeout or a 429/5xx twice. One live run timed out mid-session; nothing was pinned from it.
- **Item 2, fifteen entries** (`CHECKED_ON_G7`), all verified live and pinned:
  - venkatraman2015, bengio2015, talvitie2017, lambert2021, angelopoulos2021, stankeviciute2021, lindemann2023,
    osband2016, osband2018, agarwal2021, henderson2018, cameron2008, kingma2015, prereg2020, prereg2021.
  - **prereg2021 is added beyond the PLAN's list** because the review names "the NeurIPS 2020–21 pre-registration
    workshops" (RV36), and PMLR 181 is the 2021 volume.
  - **Venkatraman et al.: the publisher's record has a defect.** Crossref and the AAAI page both print the third author as
    "J.. Bagnell"; the paper's first page reads "J. Andrew Bagnell". The entry gives the paper's spelling. A pinned
    `record_spelling` maps it to the record's, and the display name is checked against the PDF.
  - **Lambert et al. (2021): the review gives no title.** The entry is the CDC 2021 paper on long-term dynamics for
    model-based RL; its `establishes` field says it was chosen by search.
  - **Stankevičiūtė is spelt as the record gives it**, "Stankeviciute".
  - No new entry carries a fragment. `establishes` says only why the work is listed (the review item that names it), not
    what it shows. A fragment is added with the sentence that attributes a claim.
- **Item 3, references 1 and 2.** New `ORIGINALS` record (`verify_originals()`, pinned in `_ORIGINALS_PINNED`, checked at
  build): titles of v1 and of the current version from each version's arXiv abstract page, the current version from the API
  against `results/version_crosswalk.json`, and the workshop poster from the venue's own page. **The venue pages answered
  directly this time**, so P6's summarised read is now a raw-text check. Neither page mentions archival status, and the build
  asserts that, because the template says so.
  - Reference 2 now gives v1's title, "Offline Robotic World Model: …", with the current v3 (8 January 2026) and its new
    title beside it (RV10).
  - Reference 1 adds v5 (14 December 2025).
  - Both name the presentation as a workshop poster: NeurIPS 2025, *Embodied World Models for Decision Making*; ICLR 2026,
    *The 2nd Workshop on World Models: Understanding, Modelling and Scaling*.
  - Every field is a key (`ref1_*`, `ref2_*`). The rewrite is line-preserving (7 lines for 7), so no cited template line
    moved.
  - The References note now says entries without an arXiv id are checked against Crossref or the proceedings page.
- **Renderer** (`paper_numbers.py`): DOI and page entries print `doi:` or the URL; editors print "(eds.)"; a surname
  particle stays with the surname ("B. Van Roy", "M. van der Schaar").
Build/gates: pass. Fast build twice, all eight gates, round5_gates --report, the supplement self-test, the placeholder unit test, the bibliography self-test, fast build again: PAPER.md, PAPER.tex, MODEL_CARD.md, README.md, docs/BUILD_CHECKS.md, docs/SUPPLEMENT.md byte-identical. The first rebuild's README lagged one compile behind on the page count (75 → 76); it converged on the next build.
Round-5 gates (report mode until G16): pages 26.88/12, abstract 300/19, ids 93, once 33, sig 510, keys missing 0
Paper numbers changed: t1_n_refs and t1_n_verified 18 → 33; t1_last_entry_n and t1_refs_after 20 → 35; t1_reference_list; pdf_pages 75 → 76
New keys: ref1_{title_read,title_current,read,read_date,current,current_date,conf,workshop,v2_date}, ref2_{same, less v2_date}
Ledger: none
Re-anchored checks: none
CPU jobs over 1 min: build and gates (about 150 s, twice); contended with the queue.
Queue (Y5): running (1 of 20 done; x11_e5_34_s0 started 20:51). The machine was on battery through this session (30% at 22:33); the user chose to continue.
Body words / main-content pages: unchanged prose; pages 26.88 (the reference list)
Subagents: rwm-sources ×1 (record identification; read-only)
Next: G8 (Opus 5.5, high) — outline, page budget and abstract.
Decisions for user: none

## G8 — 2026-10-19 22:36 — Opus 5.5, high — status: COMPLETE
Commits: 1dfac17 [G8][1-2] round5/OUTLINE.md, with the rwm-referee read answered
         (final [G8][close] commit: the approval question, this entry and the checkpoint)
Review items closed: the decisions for RV01, RV04, RV07, RV14, RV18 and RV37 (OUTLINE §review-items maps all of Annex 1).
Done:
- **How this session ran.** In the same conversation as G2–G7, at the user's request ("Start G8"). One `rwm-referee` read.
- **Item 1, `round5/OUTLINE.md`.**
  - **The plan:** 11.5 pages and about 5,560 body words, three figures and three tables; §5 in G13's order, leading
    with the one-step gap.
  - **The homes:** one home per result (H1–H21), each with its scope sentence, keys and display precision.
  - **Figures:** Figure 1 is (a) the base claim held out episode by episode and (b) the error-to-spread ratio by
    horizon under both rollouts.
  - **Appendices:** A–O at about 12,000 words.
  - **G9's migration list:** 13 items by exact anchor. Item 13 moves only the drafting-history framings; the evidence
    they introduce stays.
  - **Front matter:** the title recommendation, the abstract and four contributions in keys.
  - **Checks:** the rule-10 table of summary claims against their readings, and how every Annex 1 item lands.
  - Every key the outline names exists, except `n7_p_min_n4_frac`, which it asks G12 to add (the exact minimum p at
    n = 4, 0.125, which `s2` would misprint as 0.13).
- **Item 2, the referee.** Thirteen points; answers in OUTLINE §Referee.
  - **One found a real scope problem.** At one step X3's episode-level sign agrees on only 6 of 10 episodes
    (N7, p ≈ 0.2), so "it loses at one step" holds on short windows only. The abstract, contribution 1 and the
    rule-10 table now say so.
  - **Abstract.** X3's exact p moved to §4.1, where its exchangeability assumption can be stated; per-member
    propagation is now given as coverage before and after, against nominal; the rescaling split is named; the
    zero-variance optimum is explained (squared error on a sampled prediction).
  - **Title.** "Right Ranking, Wrong Scale" is recommended, since "order" reads as order of magnitude.
  - **Two points answered rather than taken.** The page budget is checked against G0's measured 662 words a page:
    8.4 pages of text, about 10.5 with every float added on top. The per-episode figure the referee asked for is
    already Figure 1a, which it was not shown.
- The `ids` gate counts "RWM-U" as a verdict label (OUT_OF_SCOPE, owner G16).
- **Item 3.** The approval question is at `DECISIONS.md#G8-outline`. It covers the plan, the scope wording that
  replaces the locked "trained on all ten episodes" (N12), the title, and G9's list.
Build/gates: not run (no text, number or generator changed; OUTLINE.md, OUT_OF_SCOPE.md and DECISIONS.md are records)
Round-5 gates (report mode until G16): pages 26.88/12, abstract 300/19, ids 93, once 33, sig 510, keys missing 0 (unchanged since G7)
Paper numbers changed: none
New keys: none (n7_p_min_n4_frac is G12's)
Ledger: none
Re-anchored checks: none
CPU jobs over 1 min: none
Queue (Y5): running (1 of 20 done; x11_e5_34_s0 started 20:51); on mains power at 22:54.
Body words / main-content pages: 17,804 / 26.88 (unchanged)
Subagents: rwm-referee ×1
Next: G9 (Sonnet 5.5, medium), only after DECISIONS.md#G8-outline is approved.
Decisions for user: DECISIONS.md#G8-outline

## G9 — 2026-10-23 12:40 — Sonnet 5.5, medium — status: COMPLETE
Commits:
dea227c [G9][1] Appendix C to supplementary S1
f5a9d7d [G9][2] Appendix R to S2
08d6205 [G9][3] Appendix S to S3
721ee24 [G9][4] App. I related work to S4
a7c26e0 [G9][5] App. H §6.1 in full to S5
d133386 [G9][6] App. H Measurements rows to S6
9c6ad9e [G9][7] App. B runtime, M-49 width, pre-submission runs to S7
69d714a [G9][8-11] Data-and-code history paragraphs, §10, §8 reproducibility paragraph to S8–S11
4efad15 [G9][12] App. W body to S12
effbb1a [G9][13] Drafting-history framings to BUILD_CHECKS
(the closing commit, [G9][close], follows this entry: it holds the SAFE_ORGS fix, regenerated bundle records, this log and the checkpoint)
Review items closed: RV06, RV08 (the bulk moves; G14 and G15 finish the appendices)
Done:
- **All 13 items of OUTLINE §supplement-migration**, cut verbatim with keys intact into S1–S12 or the BUILD_CHECKS "Moved from the paper body" list. Each item was built and gated before its commit.
- **How this session ran.** It spanned two conversations: the first did items 1–13 (commits above); this one found the checkpoint still reading "after G8", did the step 3 bundle checks and closed the session.
- **Step 3.** `build_supplementary.py` first refused: `github.com/aangelopoulos/conformal-prediction` appeared in `results/t1_bibliography_verified.json` and `scripts/t1_bibliography.py`. It is the cited Angelopoulos & Bates tutorial's own code link, stored verbatim from its arXiv comment field by G7's verification, so it identifies them, not us. Added `aangelopoulos` to `SAFE_ORGS` in both `build_supplementary.py` and `make_anon_bundle.py` (the `martius-lab` precedent, kept in step as FILE_MAP §10 says). Both then pass: supplementary 597 files scanned, git log clean, zip written (599 entries, 26.8 MB, under TMLR's 100 MB); anon bundle `PASS — zero identifying strings`. `docs/SUPPLEMENT.md` is in `docs/`, which both include (`supplementary.zip` lists it). `f5_pdf_channels.py`: no identifying strings on three channels. This widened an anonymity allow-list, so it is flagged for you.
- `supplementary_anon.zip` was not rewritten (dry run, no `--zip`).
Build/gates: pass (fast build → eight prose checks, round-5 gates, supplement self-test, placeholders → fast build; `PAPER.md`, `PAPER.tex`, `MODEL_CARD.md`, `README.md`, `BUILD_CHECKS.md`, `SUPPLEMENT.md` byte-identical across the second and third build). `xref_sweep` 0 suspect; `keys` 0 missing.
Round-5 gates (report mode until G16): pages 26.3/12, abstract 300/19, ids 93, once 33, sig 507, keys missing 0
Paper numbers changed: none
New keys: none
Ledger: none
Re-anchored checks: C15.1, C15.2, C15.5 (item 7), C5.1, C10.2 (item 3) to the supplement through their surface field, a1_consent_letter's passage (item 5) to the supplement template; expectations unchanged. Earlier log lines for items 1–13 are in the commit messages.
CPU jobs over 1 min: the two bundle builds, about 6 min each (contended with the X11 queue)
Queue (Y5): not checked this session (no CPU contention measured beyond the above)
Body words / main-content pages: 18,114 / 26.3 (see LENGTH_LOG for the counting method)
Subagents: none
Next: G10 (Sonnet 5.5, high): figures.
Decisions for user: none (the SAFE_ORGS addition is reported above for your awareness)

## G10 — 2026-10-23 14:10 — Sonnet 5.5, high — status: COMPLETE
Commits:
(one commit, [G10][1-3], follows this entry)
Review items closed: RV07; the figure half of RV25
Done:
- **Item 1, two new figures** drawn from artifacts only through `scripts/paper_figures.py` (new functions `fig7_findings`, `fig8_sigma_adam`; values recorded in `results/paper_figures.json`).
  - **Figure 1** (`paper_fig7_findings.png`): (a) X3's per-fold exact intervals and per-episode gaps at h = 368, with the pooled interval, from `results/x3_cross_fold.json`; (b) error-to-spread ρ by horizon for the released checkpoint and the fold ensembles under the released and per-member rollouts, with the calibrated line, from `results/x9_per_member_propagation.json`.
  - **Figure 2** (`paper_fig8_sigma_adam.png`): the lower and upper σ bounds per logged iteration, and the change in log Δ per iteration over the learning rate with the typical and worst-case Adam bounds, from `results/n13_adam.json`. The 75 runs of 2,500 iterations; the 10,000-iteration runs are left out so the axes match. Sign flip (+0.3 under gaussian_nll, −0.94 under sampled MSE) and the Adam signature are both visible.
  - **Departure from OUTLINE:** it asks for "measured σ at the saved checkpoints". N13 stores only the logged values and the maximum difference between them and the 342 checkpoints (all within tolerance), not σ read off each checkpoint. The caption says that and no checkpoint markers are drawn.
- **Item 2, renumbering.** `build_paper.py` now places each figure at the first "Figure N" at or after an anchor heading, so a moved figure lands in its appendix. Numbers follow document order: 1 findings (§1), 2 σ and Adam (§6.3), 3 pre-registration lead time (App. E), 4 collapse (App. J), 5 σ profile (App. K), 6 advantage by horizon (App. L), 7 calibration (App. M), 8 contamination control (App. Q). Every reference in the three templates was remapped (24 sites); a pointer sentence was added to §1, §6.3, App. L and App. M, since each figure needs a first reference where it lands. **The anchors use today's appendix letters, not OUTLINE's final A–O:** G15 re-letters and moves them with the appendices.
- **Item 3, captions.** The two new figures' captions are three lines in the PDF and name arena, n, checkpoint and horizon. The six moved figures keep their old, longer captions: PLAN does not name them and G15 owns the appendices.
- **Limits of my check.** `pdftoppm` is not installed, so I could not look at the rendered PDF pages. I looked at both new PNGs, and checked placement, numbering and caption length from the PDF text (`pypdf`, layout mode). `pdf_render_check.py` passes. G16 should open pages 2, 14, 37, 42, 45, 47, 50 and 58 by eye.
Build/gates: pass (fast build → gates → fast build; `PAPER.md`, `PAPER.tex`, `MODEL_CARD.md`, `README.md`, `BUILD_CHECKS.md`, `SUPPLEMENT.md` identical across the last two builds); `xref_sweep` 0 suspect; `keys` 0 missing.
Round-5 gates (report mode until G16): pages 24.0/12, abstract 300/19, ids 90, once 33, sig 505, keys missing 0
Paper numbers changed: none
New keys: fig8_n_runs (results/paper_figures.json)
Ledger: none
Re-anchored checks: C21.1's quoted sentence "Figure 1 plots" → "Figure 3 plots" (the pre-registration figure's new number); expectation unchanged.
CPU jobs over 1 min: none
Queue (Y5): done (20 of 20 by the runner's file at the start of this session; GT2 reads it)
Body words / main-content pages: 17698 / 24.0
Subagents: none
Next: G11 (Opus 5.5, high). GT2 runs after G12 (PLAN §0.4); the queue already shows 20 of 20.
Decisions for user: none

## G11 — 2026-10-23 17:30 — Opus 5.5, high (a Sonnet 5.5 session ran it) — status: COMPLETE
Commits:
86633cd [G11][1] Title and abstract
(one more commit, [G11][2-6], follows this entry: §1, §2, §3, the reproducibility statement and the closing record)
Review items closed: RV02, RV28 (rationale), RV30 (abstract), RV32–RV36 (citations, §2), RV37, RV38, RV41; contributes to RV01, RV03–RV05
Done:
- **Title and abstract** from OUTLINE (item 1): "Right Ranking, Wrong Scale: …"; 207 words, 5 numerals, no capitalised verdict labels. Two wording changes from the OUTLINE draft, both forced by checks: the Spearman figure no longer says "at 100 steps" (that would be a sixth numeral) and the coverage sentence says "at {{v2_deploy_h}} steps" (the horizon sweep requires a calibration figure to name its horizon). Rechecked against READINGS (rule 10): every clause agrees with its readings; X11 slots untouched.
- **§1** (item 2, 730 words, outline 680): the question, the findings in plain words with direction only, Figure 1, four contributions (bullets from OUTLINE, no priority claim), a one-line map. RWM-U's shared trunk is credited to its authors (S-23).
- **§2** (item 3, 525 words): RWM and RWM-U with MOPO's penalty read as a one-step bound at visited states; multi-step training (the prior for §4, stated only as what those methods aim at); shared-trunk ensembles; Lu et al. as the closest precedent; calibration and conformal prediction (resemblance only, no guarantee claimed); evaluation statistics; the PETS lineage in one sentence. Every attribution rests on a fragment already verified in G7's record or on the record's own `establishes` line; the fifteen G7 entries that carry no fragment are cited by topic only.
- **§3** (item 4, 1,063 words with the table, outline 760): 3.1 the rebuild; 3.2 data, Table 1 (arenas, the held-out pair's four trajectories coming from two episodes) and N12's provenance sentence; 3.3 metrics with nRMSE's floor corrected (a value of one is not the training-mean floor), ρ beside 0.80, "too small by" as Y7 defines it, Spearman's rationale as Y8 sets it, horizons; 3.4 the statistical protocol, exact tests and why n = 4 cannot go below p = 0.125, Holm, permutation nulls, pre-registration with the two workshops cited, the one rule that failed it, and the ledger's three withdrawal counts.
- **Reproducibility and data** (item 5, 85 words): a clean clone reproduces every scientific value; the 3 values that differ are the supplementary archive's own size and commit count, all from keys.
- **Moves, verbatim, to supplementary S13–S18:** the earlier title and abstract, §1, §2, §3, §8 (Method) and the rest of Data and code. Headings became bold run-ins carrying "was §N", so xref_sweep's section map cannot collide with the paper's. Pointers to the old §8 now read §3.4 (the paper's appendices and two figure captions).
- **Departures, for you to see:** (a) Table 1 is the arenas table (PLAN item 4), not OUTLINE's claim-to-verdict table; that one needs the final verdicts and is G14's (OUT_OF_SCOPE). (b) §1, §3 run over their word budgets; G14 trims. (c) Pointers into §4.x–§7 and Appendices C, J, L, O use OUTLINE's numbering and resolve only after G12–G15.
- **Bundles:** `build_supplementary.py` (597 files scanned, git log clean, zip 26.8 MB) and `make_anon_bundle.py` (zero identifying strings) both pass; `docs/SUPPLEMENT.md` is under `docs/`, which both include; `f5_pdf_channels.py` clean on all three channels.
Build/gates: pass (fast build → gates → fast build; the last two builds byte-identical); `xref_sweep` 0 suspect; `keys` 0 missing. Stage 1 was one build and one commit; items 2–5 went in one build and one commit, as G9's items 8–11 did, because the withdrawal-count gate needed §3.4 to exist before it could pass.
Round-5 gates (report mode until G16): pages 21.92/12, abstract 207/5, ids 86, once 19, sig 461, keys missing 0
Paper numbers changed: none
New keys: none
Ledger: none
Re-anchored checks (rule 8): C9.1, C26.1, C27.1, C28.3 (old abstract and contributions → supplement S13, S14, through `surface`); C7.1, C7.2, C7.5, C10.5 (old §1 and §8 → S14, S17); C24.1 (old §3.2 → S16); C28.3's region end marker (`## Data and code` → `## Reproducibility and data`); `check_retraction_counts` in `build_paper.py` (the introduction's and §8's statements → §3.4, its self-test input likewise); two figure captions' "§8" → "§3.4". Expectations unchanged. **Tightened:** C12.1's caps from 320 words and 26 numerals to Y2's 210 and 5, anchored to the new abstract. **Added** to `typed_numeral_audit.py`: a `table-ref` class for "Table N" as an address, like `figure-ref`.
CPU jobs over 1 min: the two bundle builds, about 6 min each (X11 queue finished; no contention)
Queue (Y5): done (20 of 20, none failed, as the runner's files showed at the start of the session); GT2 follows G12
Body words / main-content pages: 15,975 / 21.92 (LENGTH_LOG)
Subagents: none (PLAN's G11 names none)
Next: G12 (Opus 5.5, high).
Decisions for user: none

## G12 — 2026-10-23 20:30 — Opus 5.5, high (a Sonnet 5.5 session ran it) — status: COMPLETE
Commits:
(one commit, [G12][1-4], follows this entry)
Review items closed: RV18, RV19 (this section), RV21, RV22, RV23 (this section), RV27 (this section)
Done:
- **§4.1** leads with the fold replication: every episode held out once, the direction in all ten episodes with its exact p, the fold range, and the exchangeability caveat from OUTLINE §Referee 2; then the one-step reversal on short windows (unsurprising, since teacher forcing trains that target; unresolved episode by episode), with the pre-registered 60-unit reading beside it; then the 10,000-iteration held-out factor as supporting evidence with its exact p printed as stored (0.125: `s2` would print 0.13) and the two-episode caveat.
- **§4.2** one paragraph (Y6): the accuracy half only, no comparison can be significant at four trajectories, the ranking depends on the training budget, the training-time trade-off is untested.
- **§4.3** "consistent, but a weak test": Table 2 (nRMSE at h = 368 for RWM and six baselines, with k of 4 and the exact p, beside the three floors); no baseline beats even the training mean; the size-matched baselines as a parameter-count test only; the RSSM in two sentences.
- **Plain words:** no rule or ledger IDs; rules are "a rule committed before its runs".
- **Moves, verbatim:** the old §4 (what we tested and left untested) and old §5 (with 5.1–5.3) to supplementary S19. Nothing that left carries a result the paper no longer shows: every key is in the supplement.
- **Pointers:** 66 references to the old §5, §5.1–5.3 in the rest of the template now read §4.1, §3.2 (the data budget, H18), §4.2, §4.3; `evidence_summary.py`'s section fields likewise. The uncertainty section (old §6) is still numbered 6 and now sits under an interim **"## 5."** heading that G13 replaces; without it `pdf_render_check` fails on §5 pointers from §1–§3.
- **Departures to see:** (a) §4 is 915 words, over the outline's 780 (G14 trims). (b) Table 2 has no size-matched rows because the X4 artifact holds no nRMSE: those are in the text. (c) The old §4's claim-count paragraph (tested n, left untested) is not in §4; the claim table (G14) and §7 limitations take it.
Build/gates: pass (fast build → gates → fast build; last two builds byte-identical); `xref_sweep` 0 suspect; `keys` 0 missing.
Round-5 gates (report mode until G16): pages 18.25/12, abstract 207/5, ids 58, once 17, sig 264, keys missing 0
Paper numbers changed: none
New keys: n7_bl_{mlp,rssm,transformer}_{tf,ar}_nrmse_h368_{k,p} (12), n7_x4_{mlp,transformer}_{k,p} (4), all from results/n7_exact_tests.json
Ledger: none
Re-anchored checks (rule 8): C10.4, C15.3, C15.4, C17.1, C25.1 (old §4 and §5 → supplement S19, through `surface`; C17.1's section anchor now the supplement's S19 heading); C24.1 via `evidence_summary.py`'s section fields; expectations unchanged.
CPU jobs over 1 min: none
Queue (Y5): done (20 of 20); GT2 is next
Body words / main-content pages: see LENGTH_LOG
Subagents: none
Next: GT2 (Sonnet 5.5, medium), then G13.
Decisions for user: none

## GT2 — 2026-10-23 21:30 — Sonnet 5.5, medium — status: COMPLETE
Commits:
(one commit, [GT2][1-3], follows this entry)
Review items closed: RV20 (data)
Done:
- **Item 1, the gate.** `round5/gt2_queue_check.py` → `gt2_queue_check.json`: the queue log ends `queue empty; runner exits`; all 20 IDs are in the done list; none failed; every run record has the right fold complement, ensemble size, seed and 2,500 iterations, finite losses, and a non-empty weights file. PASS.
- **Item 2, the readings.** Each frozen script found its SHA-256 in its own ledger entry, ran unchanged, and reproduced its fold-{1, 8} assertion exactly (difference 0.0). As returned:
  - **X11a (M-97): MIXED** at h = 1 (Q = 0.92 [0.81, 1.07]); IN-SAMPLE FLATTERS at h = 100 and 368 (as the label it would carry).
  - **X11b (M-98): GENERALISES** (leads at 4 of 4 horizons, interval excludes zero at 4 of 4).
  - **X11c (M-99): PER-HORIZON SCALAR DOES NOT RESTORE CALIBRATION** (72 of 180 cells; constant 17). Alongside only: pooled ±1σ coverage is within band at every horizon.
  - **X11d (M-100): MECHANISM SUPPORTED** (1.82× lower overconfidence, +6.0 points).
  - **X11e (M-103): PROPAGATION NARROWS THE GAP** (f = 0.72 [0.67, 0.76] at h = 100, n = 20).
  `round5/gt2_write_ledger.py` appended **M-104** (the discharge record, every number read from the artifacts) and set the five Status lines. `RESULTS.md`'s M- count is 104; `ledger_check.py` passes.
- **Two results change what the paper may say** (rule 10, recorded in READINGS' addendum): (a) X10's "in-sample is worse at h = 1" does not hold at n = 20 (MIXED); (b) the pre-registered cell-level reading on unseen episodes says per-horizon rescaling does not restore calibration, while the alongside pooled coverage is within band. G13 must give both for §5.7 and the h = 1 in-sample sentence.
- **Item 3.** Stages: training 11l and readings 20v3 to 20v7 in `reproduce.sh` (all `NEEDS_WEIGHTS`). 45 keys `x11a_*` … `x11e_*`. READINGS addendum (458 words). No paper text was edited; the paper's numbers did not change.
- **A process slip to know about.** Round 5's rule was that the fifteen `results/x3_run_*_ens5.json` and `_seed3/4.json` records stay uncommitted until GT2. My commit `86633cd` (G11) ran `git add … results` and swept them in. Nothing read them: no session opened a run record's evaluation before the frozen scripts did, and the scripts' own gate was unaffected. Now moot, as GT2 has run, and recorded here.
Build/gates: pass (fast build → gates → fast build; last two byte-identical); `keys` 0 missing.
Round-5 gates (report mode until G16): pages 18.25/12, abstract 207/5, ids 58, once 17, sig 265, keys missing 0
Paper numbers changed: none
New keys: x11a_* (verdict, q, ci, label, rho at h = 1, 100, 368), x11b_*, x11c_*, x11d_*, x11e_* (results/x11*.json)
Ledger: M-104 (new); Status lines of M-97, M-98, M-99, M-100, M-103 set to DISCHARGED
Re-anchored checks: none
CPU jobs over 1 min: the five readings, 11 min in all (x11b 7 min), idle machine
Queue (Y5): done (20 of 20), discharged
Body words / main-content pages: unchanged (see LENGTH_LOG)
Subagents: none
Next: G13 (Opus 5.5, high).
Decisions for user: none

## G13 — 2026-10-23 23:30 — Opus 5.5, high (a Sonnet 5.5 session ran it) — status: COMPLETE
Commits:
(one commit, [G13][1-8], follows this entry)
Review items closed: RV11, RV12, RV14, RV15–RV17 (text), RV19 and RV23 (this section), RV24–RV26, RV28 (this section), RV29–RV31, RV33 (framing), RV42, RV43 (this section)
Done:
- **New §5 in OUTLINE's order** (2,366 words; outline 1,700), replacing G12's interim heading and the old §6:
  - **5.1** quotes what RWM-U claims (aleatoric "captures … effectively", the trend, "effectively propagated over long horizons") and what the code computes (the discard; Eq. 4's variance against the code's standard deviation); credits the shared trunk to the original; names MOPO's one-step job and the three gaps.
  - **5.2 (the lead)** Table 3: R, k at h = 1 and 100 and per-member coverage for five ensembles, "not measured" where an artifact holds nothing; the folds' one-step ρ; X11a read as MIXED at h = 1 and flattering at h = 100, with X10's earlier worse-at-h = 1 reading beside it.
  - **5.3** Abbas et al. on model inadequacy; the shared trunk measured; independent members at n = 4 and n = 20 as a bound, not an isolation; Osband et al.; the "bootstrap" paper–code difference.
  - **5.4** the trend claim tested against accumulated error and why that is not a calibration failure; X9 and X11e, scope sentence once.
  - **5.5** the σ = 0 optimum (per step, second pathway not isolated, the bound term gives the floor no gradient), the synthetic test, Adam's step (Kingma and Ba), PETS and the survey counts; Figure 2.
  - **5.6** Spearman as headline, Pearson verdicts named as pre-registered, X6 with its scope, M-43 inconclusive at n = 4 beside X11b resolved at n = 20.
  - **5.7** per-horizon rescaling as split conformal with the exchangeability condition and the nine-episode requirement; X7's units' scope; ±2σ and CRPS from N9; M-65's withdrawn reading; X11c's two faces together.
- **rwm-checker (one read):** no numeric mismatch; Table 3 matches row by row. It reported four wording problems and one minor; I checked each against its artifact and fixed all five: (1) "the shared-trunk ensembles account for the least" was wrong for the released checkpoint (R = 174), now "the independently trained members come closest"; (2) "the constant that calibrates" used the mean-matching constant (10.4, 43.2), whose coverage is 81% and 69%; it now gives Y7's coverage-matching k (6.6, 42); (3) "own training episodes" contradicted §3.2's provenance statement, now "ten released episodes"; (4) the 30-of-48 count covers all cells of the tails analysis, not only the released checkpoint's, and says so; (5) the synthetic ratio 0.98 is a mean over seeds of per-seed medians, and says "averaged over seeds".
- **Moves, verbatim:** the old §6 to supplementary S20–S27, one section per old subsection (so the restatement check keeps its per-section scope).
- **Pointers:** 111 references to the old §6.x in the rest of the template now read §5.x; `evidence_summary.py`'s section fields, the model card builder and one `a1_consent_letter.py` passage follow. §1's pointers to the defects section use words, since no section 6 exists until G14.
- **Departures to see:** (a) §5 is 2,366 words, over the outline's 1,700 (G14 trims). (b) **Figure 3 (σ-coverage by horizon, OUTLINE §figures) is not drawn**: neither G10's nor G13's items name it, and drawing it renumbers every appendix figure again; the figure has no home until you or G14 decide. (c) The floor's "5.2× slower" drift is not stated because no key holds it. (d) The App. E commit-subject column now prints "section" for "§", so quoted subjects do not read as pointers into this paper.
Build/gates: pass (fast build → gates → fast build; last two byte-identical); `xref_sweep` 0 suspect; `keys` 0 missing; both bundles pass the deny-list scan; PDF channels clean.
Round-5 gates (report mode until G16): pages 13.1/12, abstract 207/5, ids 35, once 6, sig 87, keys missing 0
Paper numbers changed: none
New keys: none
Ledger: none
Re-anchored checks (rule 8): C1.1, C2.2, C2.4, C3.1, C3.2, C4.1, C7.4, C8.1, C18.2 (old §6.2, §6.6 sentences → supplement, through `surface`); C24.1 via `evidence_summary.py`; the h = 8 gap-label gate in `build_paper.py` (read the old §5, now §4); the figure anchor for Figure 2 (§5.5); `a1_consent_letter.py`'s first passage (→ the supplement). Expectations unchanged.
CPU jobs over 1 min: the two bundle builds, about 6 min each
Queue (Y5): done and discharged (GT2)
Body words / main-content pages: 8,919 / 13.1
Subagents: rwm-checker ×1
Next: G14 (Opus 5.5, medium).
Decisions for user: Figure 3 (see above): draw it in G14, or drop it from OUTLINE.

## G14 — 2026-10-24 01:00 — Opus 5.5, medium (a Sonnet 5.5 session ran it) — status: COMPLETE
Commits:
(one commit, [G14][1-5], follows this entry)
Review items closed: RV01 (the budget: main content 11.25 pages against Y1's 12), RV25 (the variance state as Adam's bound), RV40 (the upstream report's status), RV43; the summaries for everything
Done:
- **§6 Defects** (four bold-led paragraphs): unmarked boundaries with the spliced windows' cost in one sentence; the stale action with its line-level fix and its cost at h = 1, 32 and 100 on all ten released episodes (`adh20_*` keys) and the held-out pair; evaluation on training data; the variance state as Adam's per-step bound with N13's worst case, plus the first author's account.
- **§7 Lessons and limitations**: seven lessons, each in words with a section pointer (no numbers: each result is stated once, in its home); limitations updated for this round (one robot, gait, terrain and dataset; no policy, with the reason the one-step shortfall bears on MOPO's penalty; X5 not run and why; the two-episode held-out pair; unrecorded provenance; untuned baselines; no cross-rule correction; PETS descendants).
- **§8 Conclusion** with **Table 4**, the claim-to-verdict table the referee asked for (six tested claims, evidence, plain-words standing, section); it replaces the table OUTLINE had put in §3.2 (which G11 made the arenas table).
- **Upstream report (Y10):** `docs/presubmission/AUTHOR_QUERY_ALIGNMENT.md` is still marked DRAFT, NOT SENT and no reply exists, so §6 says "We have not reported this to the authors before submission." **If you send it before submission, §6 and the reply must be updated.**
- **Moves, verbatim:** the old §7, §9, §11, §12 to supplementary S28–S31 (one section each).
- **Pointers:** 22 references in the appendices to the old §7.x, §9, §11, §12 now read §6, §7, §8; `evidence_summary.py`'s defect row points at §6; §1's pointers to §6–§8 are numbers again.
- **Rule-10 audit of every summary site** (against READINGS' addendum, OUTLINE's table and ledger M-104):
  - *Abstract:* every clause agrees with every reading it covers. Rescaling is stated for the released checkpoint only, which X7 supports; X11c's cell-level reading on unseen episodes splits, and the abstract does not claim for those. No sentence says in-sample is better or worse.
  - *Contribution 4:* **changed**: it said rescaling fixes one-sigma coverage; it now says "on the released checkpoint" and that on unseen episodes the evidence is mixed.
  - *§1 findings:* **changed** likewise (the mixed clause added).
  - *Contribution 2 and the abstract's "in every ensemble measured … even at one step":* agree (N14 for three ensembles; the folds' ρ is above its calibrated value).
  - *Contribution 1:* "on every episode" holds at h = 368 only (h = 8 is 8 of 10) and says so by naming the horizon; the one-step loss is "on short windows".
  - *§7 lessons:* in-sample reads neither-flatters-nor-worsens at one step (X11a MIXED) and flatters at long horizons; X9 and X11e agree; ranking claims name Spearman and the step-size caveat; rescaling says mixed on unseen episodes.
  - *§7 limitations, §8 and Table 4:* agree; X5 stays "not run"; X6 is the shorter-unit h = 100 result; X7 is the released checkpoint's ten released episodes.
- **Checks re-anchored (rule 8):** C4.3, C3.6, C18.1, C25.2, C27.2 (old §9, §12, §7.2 sentences → supplement); C9.1's section list (old §9 and §12 → the new §7 and §8); C26.1's front-matter region marker; `typed_numeral_audit.py`'s self-test plant (now before "Lessons and limitations"); `paper_numbers.py`'s `n_lessons` (counts S29's bold leads) and `n_defects` (counts §6's bold leads); the model-card builder was not touched. Expectations unchanged.
- **Not done, for you:** Figure 3 (σ-coverage by horizon, OUTLINE §figures) is still undrawn. It would add a figure and renumber the appendix figures once more; with 0.75 page spare it would fit.
Build/gates: pass (fast build → gates → fast build; last two byte-identical); `xref_sweep` 0 suspect; `keys` 0 missing; both bundles pass; PDF channels clean.
Round-5 gates (report mode until G16): pages 11.25/12, abstract 207/5, ids 21, once 1, sig 6, keys missing 0
Paper numbers changed: none
New keys: none
Ledger: none
Re-anchored checks: see above
CPU jobs over 1 min: the two bundle builds, about 6 min each
Queue (Y5): done and discharged (GT2)
Body words / main-content pages: 7,295 / 11.25
Subagents: none (PLAN names none for G14)
Next: G15 (Opus 5.5, medium).
Decisions for user: Y10 (send the alignment query before submission or accept the "not reported" sentence); Figure 3.

## G15 — 2026-10-24 03:00 — Opus 5.5, medium (a Sonnet 5.5 session ran it) — status: COMPLETE
Commits:
(one commit, [G15][1-4], follows this entry)
Review items closed: RV06, RV09 (App. D), RV12–RV13 and RV39 (App. O), RV24 (App. M), RV25 (App. J), RV27 (App. F); RV03 and RV05 in the appendices
Done:
- **Re-lettered A–Z to the outline's A–O**, each opening with one or two sentences saying what it holds and which main-text claim it supports. Old to new: A→A; B (+ the pointer stub C)→B; new C (statistical methods); D→D; E and Z→E; G→F; L→G and H (split at its §4.3 passages); U→H; M and K→I; J, F and I→J; O and P→K; N and X→L; T and Y→M; V and Q→N; H's rows→O and N. The stubs R, S, W and the old C are gone: their text is supplementary S1, S2, S3 and S12.
- **New text:** App. B's windows-and-compute paragraph; **App. C**, the procedures behind every interval and test (cluster bootstrap, exact sign-flip tests and why n = 4 cannot go below p = 0.125, Holm, permutation nulls that keep dimensions together); App. D's **version crosswalk** and the X5 sentence; App. O's corrected row: the papers name a forecast decay and set it to one (C-17 corrects C-09), the training tables, and the bootstrap-ensemble difference (C-18).
- **Pointers:** every "Appendix X" and "Appendices X and Y" inside the moved text was remapped by context (a letter that split, such as L, K, I, H, was resolved from the words around it); figure numbers follow the new document order (3 pre-registration lead time, 4 advantage by horizon, 5 calibration, 6 σ profile, 7 collapse, 8 contamination control), and `build_paper.py`'s figure anchors follow (E, G, I, I, J, N). §6's variance-state pointer now reads Appendix J.
- **Prose that restated the main text or explained why an appendix existed** (three paragraphs) moved verbatim to supplementary S32. The two paragraphs on the trunk's source and our own arms moved from J to K, where they belong.
- **Retractions kept:** the appendix passages that disclose the withdrawn binomial P-values stay; only revision-history lead phrases ("as §5.7 stated them", "as §6 stated it") were rewritten.
- **Departure to see:** the outline planned about 12,000 appendix words; the appendices render to about 27,000. They hold the tables and per-horizon detail at full precision (PLAN item 3), and cutting more would move results out of the paper, the supplement and the ledger together. G16's referee and G17 decide whether that is acceptable.
Build/gates: pass (fast build → gates → fast build; the last two byte-identical); `xref_sweep` 0 suspect; `keys` 0 missing; both bundles pass the deny-list scan.
Round-5 gates (report mode until G16): pages 11.25/12, abstract 207/5, ids 21, once 1, sig 6, keys missing 0
Paper numbers changed: none
New keys: none
Ledger: none
Re-anchored checks (rule 8): `restatement_index.py`'s accepted-ambiguity registry (the appendix that held rule M-44's table is now K; two new entries for the merged H and J, each with its reason); `evidence_summary.py`'s "Appendix U" → H; the horizon sweep's episode-level sentence now names its horizon. Expectations unchanged.
CPU jobs over 1 min: the two bundle builds, about 6 min each
Queue (Y5): done and discharged (GT2)
Body words / main-content pages: see LENGTH_LOG / 11.25
Subagents: none
Next: G16 (Opus 5.5, high; a new terminal): the fresh-eyes review.
Decisions for user: none new (Y10 and Figure 3 stand from G14).

## G16 — 2026-10-24 06:00 — Opus 5.5, high (a Sonnet 5.5 session ran it in the same terminal; no new terminal could be opened) — status: COMPLETE
Commits:
(one commit, [G16][1-5], follows this entry)
Review items closed: verifies every item in Annex 1 (`round5/REVIEW.md`)
Done:
- **User directives applied first.** (a) **Y10:** the query was sent and has no reply, so §6 now reads "We sent this to the first author before submission and had no reply when we submitted" (no date is recorded; the paper gives none) and `AUTHOR_QUERY_ALIGNMENT.md`'s header says so. (b) **README pointers:** the README template's seven section pointers now read §6, §5.3, §5.6, §5.7 and "§4, Table 4 and Appendix D". (c) **Figure 3:** judged not necessary for TMLR; not drawn, OUTLINE's slot dropped (recorded in `REVIEW.md`).
- **Review.** `body.txt` (pages 1–12, 6,977 words) read once; `rwm-referee` ×1 (13 points, all verified); `rwm-checker` ×2 (each hit its 60-turn limit and delivered a partial report, which I asked for; coverage and the unchecked parts are listed in `REVIEW.md`). Fixes: eleven wording and scope points from the referee (fairness of "sizes them wrong", Spearman's unit, the band, three scales for the released checkpoint, per-fold intervals, the factor's driver against the floors, term glosses, and others, each listed in `REVIEW.md`); four from the checkers (a swapped row-label pair in App. L, a misdescribed count in App. I, a wrong clause in App. J, a wrong clause in App. M) and one wording in App. D; RV39's "Table S9" → the follow-up's Table S8.
- **Gates now clean and blocking.** `ids` was 19 (all "RWM-U", the follow-up's name, a false positive logged since G8: now in the gate's acronym list); `once` was 1 (the coverage nominal's 68% in four prose places: now words in three); `sig` was 13 (the calibrated 0.80 in Figure 1's caption, the 3.68 ratio, and exact p-values 0.125 and 0.875): exact n = 4 p-values now print as fractions through a `_frac` twin of every `n7_*` exact-p key and `x9_e5_p_h100`. FILE_MAP §3 and the gate list now run `round5_gates.py` without `--report`.
- **`CONSISTENCY.md`** (front-matter sentence | body anchor | every reading | agrees) written; every row agrees.
Build/gates: pass (fast build → gates → fast build; last two byte-identical); both bundles pass; PDF channels clean.
Round-5 gates (blocking): pages 11.67/12, abstract 209/5, ids 0, once 0, sig 0, keys missing 0
Paper numbers changed: none
New keys: `n7_*_p_frac` twins and `x9_e5_p_h100_frac` (read from the same artifacts)
Ledger: none
Re-anchored checks: none new (the gate's acronym list gained "RWM-U", the false positive of G8)
CPU jobs over 1 min: the two bundle builds, about 6 min each
Queue (Y5): done and discharged
Body words / main-content pages: see LENGTH_LOG / 11.67
Subagents: rwm-referee ×1, rwm-checker ×2
Next: G17 (Opus 5.5, medium).
Decisions for user: none new. The unchecked parts of the appendices (REVIEW.md) are the residual risk.
