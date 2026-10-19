# Round-5 checkpoint — after G4 (2026-10-19)

**State.** Branch `presubmission5`. Last log entry: **G4 — COMPLETE**. Nothing pushed. The X11 queue is running (runner PID 14182;
1 of 20 done at 21:05; projected finish about **2026-10-22 00:15**). Keep the machine on mains power.

**Next action.** G5 (Opus 5.5, medium): `docs/presubmission/round5/go.zsh G5` — readings into the record (S- entry withdrawing M-65's
reading via N8/R-81; C-09, bootstrap, shared trunk, Table S8, survey counts; framings the review withdraws; `round5/READINGS.md`).
Then G6. GT2 only after the queue finishes.

**Readings G5 must state with their scope** (keys in `results/paper_numbers.json`):
- X9 (M-101): NARROWS at h = 100 for all four models (`x9_*`); scope sentence `x9_scope`.
- X10 (M-102): IN-SAMPLE IS WORSE at h = 1; FLATTERS at h = 100 and 368 (`x10_label_h*`); split by horizon and by statistic.
- N8 (R-81) heavy tails; N7 (R-82) no exact rejection at n = 4; N9 (R-83) ±2σ not restored; N10 (R-84) the training-mean floor
  (**at h = 368; at h = 100 on held-out relative-L1, hold-last is lower**); N11 (R-85) ranks stronger from h = 8 on (not at h = 1);
  N12 (R-86) provenance; N13 (R-87) unreachable even at the worst-case step; N14 (R-88) no ensemble accounts for its one-step error.

**Queue status** (repository root): `echo "done $(wc -l < runs/queue_round5_done.txt) of 20; failed $(wc -l < runs/queue_round5_failed.txt)"; tail -n 2 runs/queue_round5.log`.
Never read `[checkpoint …]` lines or the X11 run records' evaluations before GT2. `results/x3_run_*_ens5.json` files appear as runs
finish; they stay uncommitted until GT2.

**Facts later sessions must not lose.** (1) M-103 (X11e) and M-97–M-100 (X11a–d) are discharged in GT2 by their frozen scripts.
(2) GT2 adds the X11 stages. (3) The typed −14.4629 defect is in OUT_OF_SCOPE (owner G13/G15).

**Blockers.** None.
