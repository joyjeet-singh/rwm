# Round-5 checkpoint — after G5 (2026-10-19)

**State.** Branch `presubmission5`. Last log entry: **G5 — COMPLETE**. Nothing pushed. The X11 queue is running (runner PID
14182; 1 of 20 done at 21:32; projected finish about **2026-10-22 00:15**). **The machine was on battery at 21:32: keep it on mains
power**, or the run in progress is lost (PLAN §1.5).

**Next action.** G6 (Sonnet 5.5, high): `docs/presubmission/round5/go.zsh G6` — tooling for a short paper (`{{key|sN}}` display
precision, `round5_gates.py --report`, the keys gate against `round5/base_keys.txt`, checks reading the supplement). Then G7, G8.
GT2 only after the queue finishes.

**What G5 put in the record.** S-22 (M-65's reading withdrawn on evidence; R-81), S-23 and S-24 (framings), C-17 (C-09 corrected),
C-18 (per-head resampling), R-89 (survey counts). `round5/READINGS.md` holds every new reading with its keys and scope, and the
template lines the rewrite must change (19, 59, 585, 595, 632). Retraction counts are 24 superseded: 9 on evidence, 8 framings,
7 early hypotheses (derived).

**Queue status** (repository root): `echo "done $(wc -l < runs/queue_round5_done.txt) of 20; failed $(wc -l < runs/queue_round5_failed.txt)"; tail -n 2 runs/queue_round5.log`.
Never read `[checkpoint …]` lines or X11 run records' evaluations before GT2; `results/x3_run_*_ens5.json` stay uncommitted until GT2.

**Facts later sessions must not lose.** (1) M-97–M-100 and M-103 are discharged in GT2 by frozen scripts. (2) GT2 adds the X11 stages.
(3) OUT_OF_SCOPE holds the typed −14.4629 defect (G13/G15) and the first-author pronoun line (G9/G15).

**Blockers.** None.
