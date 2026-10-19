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
