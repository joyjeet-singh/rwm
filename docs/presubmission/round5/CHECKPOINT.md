# Round-5 checkpoint — after G7 (2026-10-19)

**State.** Branch `presubmission5`. Last log entry: **G7 — COMPLETE**. Nothing pushed. The X11 queue is running (runner PID
14182; 1 of 20 done at 22:33; projected finish about **2026-10-22 00:15**). **The machine was on battery through G5, G6 and G7 (30% at 22:33): keep it
on mains power**, or the run in progress is lost (PLAN §1.5).

**Next action.** G8 (Opus 5.5, high): `docs/presubmission/round5/go.zsh G8` — outline, page budget and abstract; needs
`DECISIONS.md#G8-outline` approved before G9. GT2 only after the queue finishes.

**G7 added** (FILE_MAP): `t1_bibliography.py` verifies DOI (Crossref) and proceedings-page records, `--verify --only`, a
network `--self-test`, and references 1–2 in `ORIGINALS` (keys `ref1_*`, `ref2_*`). The fifteen new entries are in the
reference list but **cited nowhere yet**: G11–G15 add the sentences, each with a fragment wherever it attributes a claim.

**Tooling G6 added** (FILE_MAP §3): `docs/SUPPLEMENT.template.md` → `docs/SUPPLEMENT.md`, read by every prose check;
`{{key|sN}}` (`scripts/placeholders.py`); `scripts/round5_gates.py --report` (pages, abstract, ids, once, sig, keys);
`scripts/supplement_selftest.py`. Run both after the eight gates. Current report: pages 26.88/12, abstract 300/19, ids 93,
once 33, sig 510, keys missing 0.

**Queue status** (repository root): `echo "done $(wc -l < runs/queue_round5_done.txt) of 20; failed $(wc -l < runs/queue_round5_failed.txt)"; tail -n 2 runs/queue_round5.log`.
Never read `[checkpoint …]` lines or X11 run records' evaluations before GT2; `results/x3_run_*_ens5.json` stay uncommitted until GT2.

**Facts later sessions must not lose.** (1) M-97–M-100 and M-103 are discharged in GT2 by frozen scripts. (2) GT2 adds the X11 stages.
(3) `round5/READINGS.md` is the rewrite sessions' source for every new reading. (4) A key that leaves the paper on purpose goes into
`round5/RETIRED_KEYS.md` with a reason from its vocabulary, or the `keys` gate fails at G16.

**Blockers.** None.
