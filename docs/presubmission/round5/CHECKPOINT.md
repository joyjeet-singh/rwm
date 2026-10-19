# Round-5 checkpoint — after G3 (2026-10-19)

**State.** Branch `presubmission5`. Last log entry: **G3 — COMPLETE**. Nothing pushed. The X11 training queue is running
(launched 2026-10-19 16:44:57, runner PID 14182; projected finish about **2026-10-22 00:15**; 0 of 20 done at 18:50).

**Next action.** G4 (Sonnet 5.5, high): `docs/presubmission/round5/go.zsh G4` — N7–N14 per `PROTOCOLS.md` §5, post hoc,
beside the queue (log jobs as contended). Then G5. GT2 only after the queue finishes.

**Readings G5 must carry, with their scope** (keys in `results/paper_numbers.json`):
- X9 (M-101): PROPAGATION NARROWS THE GAP for all four models at h = 100 (`x9_*_verdict`; e5 and ind at n = 4, descriptive).
  The share of the gap closed (`x9_*_f_h100`) is 0.71–0.88. Coverage stays below X7's band. Carry the locked scope sentence (`x9_scope`).
- X10 (M-102): IN-SAMPLE IS WORSE at h = 1, but IN-SAMPLE FLATTERS at h = 100 and h = 368 (`x10_label_h*`). At h = 1 the ratio and the
  coverage disagree. The reading splits; a summary must say so. Carry the caveat (`x10_caveat`).

**Queue status** (repository root; reads no reading):
`echo "done $(wc -l < runs/queue_round5_done.txt) of 20; failed $(wc -l < runs/queue_round5_failed.txt)"; tail -n 2 runs/queue_round5.log`.
Never read `[checkpoint …]` lines before GT2.

**Facts later sessions must not lose.** (1) M-103 (X11e) is discharged in GT2 by `scripts/x9_per_member_propagation.py --x11e`,
unchanged. (2) X11a–d (M-97–M-100) are frozen; a missing run record stops a reading with `FileNotFoundError`, not `.blocked`.
(3) GT2 must add the X11 stages (training queue and readings) to `reproduce.sh`. (4) Stages 20v0–20v2 are all NEEDS_WEIGHTS.

**Blockers.** None.

**Files.** `round5/{PROTOCOLS,DECISIONS,RUN_QUEUE,SESSION_LOG,CHECKPOINT}.md`, `scripts/x9_per_member_propagation.py`,
`scripts/x10_insample_vs_heldout.py`, `results/x9_per_member_propagation.json`, `results/x10_insample_vs_heldout.json`.
