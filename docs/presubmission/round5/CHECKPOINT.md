# Round-5 checkpoint — after GT1 (2026-10-19)

**State.** Branch `presubmission5`. Last log entry: **GT1 — COMPLETE**. Nothing pushed. Y5 = B with the cap raised to 62
CPU-hours (`DECISIONS.md#GT1-cap`). **The X11 training queue is running in the background**: launched 2026-10-19 16:44:57
(+0530), runner PID 14182, 20 runs, projected 55.5 CPU-h, finish about **2026-10-22 00:15**.

**Next action.** G3 (Opus 5.5, high): `docs/presubmission/round5/go.zsh G3`. X9 and X10 per `PROTOCOLS.md` §2–§3. **Also**: X9's
script must carry X11e's arena (`fold_e5`, `PROTOCOLS.md` §4.2) and be frozen, with X11e's ledger entry, in G3's PRE-REGISTER
commit. G3 runs beside the queue (inference only; log jobs as contended). Then G4. GT2 only after the queue finishes.

**Queue status** (repository root; reads no reading):
`echo "done $(wc -l < runs/queue_round5_done.txt) of 20; failed $(wc -l < runs/queue_round5_failed.txt)"; tail -n 2 runs/queue_round5.log`.
If the runner has stopped (`pgrep -f queue_runner`), relaunch per `round5/RUN_QUEUE.md`. Never read `[checkpoint …]` lines before GT2.

**Facts later sessions must not lose.** (1) X11a–d are frozen (M-97–M-100 record their SHA-256s); GT2 runs them unchanged and changes
only those entries' Status lines. (2) A missing run record stops a reading with `FileNotFoundError` (no output), not `.blocked`.
(3) The scripts print nothing from fold runs until GT2. (4) G2's facts still hold (CHECKPOINT history in SESSION_LOG).

**Blockers.** None.

**Files.** `round5/{PROTOCOLS,DECISIONS,RUN_QUEUE,SESSION_LOG,CHECKPOINT}.md`, `round5/gt1_*`, `scripts/x11*.py`,
`scripts/round5_queue_timing.py`, `scripts/step5_train.py`, `scripts/queue_run.py`, `results/{x11_power,round5_queue_timing}.json`.
