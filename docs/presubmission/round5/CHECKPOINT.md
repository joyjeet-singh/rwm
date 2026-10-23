# Round-5 checkpoint — after G9 (2026-10-23)

**State.** Branch `presubmission5`. Last log entry: **G9 — COMPLETE**. Nothing pushed. Pages 26.3/12 (the rewrite sessions bring this down).
The X11 queue was projected to finish about 2026-10-22 00:15: check it (below) before GT2; its state was not looked at in G9.

**Next action.** `docs/presubmission/round5/go.zsh G10` (Sonnet 5.5, high): figures, to OUTLINE.md. GT2 only after the queue finishes.

**G9 did.** All 13 migration items are in S1–S12 of `docs/SUPPLEMENT.template.md` or BUILD_CHECKS "Moved from the paper body";
headings and one pointer sentence stay in the paper for G15 (App. C, R, S, I, H, W) . Bundle dry runs pass. Added `aangelopoulos` to
`SAFE_ORGS` in `build_supplementary.py` and `make_anon_bundle.py` (a cited paper's own code link, from G7's bibliography record).

**Queue status** (repository root): `echo "done $(wc -l < runs/queue_round5_done.txt) of 20; failed $(wc -l < runs/queue_round5_failed.txt)"; tail -n 2 runs/queue_round5.log`.
Never read `[checkpoint …]` lines or X11 run records' evaluations before GT2; `results/x3_run_*_ens5.json` and `x3_run_*_seed*.json` stay uncommitted until GT2.
Keep the machine on mains power while the queue runs.

**Facts later sessions must not lose.** (1) M-97–M-100 and M-103 are discharged in GT2 by frozen scripts. (2) GT2 adds the X11 stages.
(3) `round5/READINGS.md` is the rewrite sessions' source for every new reading. (4) A key that leaves the paper on purpose goes into
`round5/RETIRED_KEYS.md` with a reason, or the `keys` gate fails at G16. (5) `LENGTH_LOG.md` counts words as whitespace tokens
from the title to `## References` (18,114 now); G0's 17,804 used an unrecorded method. (6) Build ends dirty on `PAPER.pdf` only: `git restore` it.

**Blockers.** None.
