# Round-5 checkpoint — after G8 (2026-10-19)

**State.** Branch `presubmission5`. Last log entry: **G8 — COMPLETE**. Nothing pushed. The X11 queue is running (runner PID
14182; 1 of 20 done at 22:54; projected finish about **2026-10-22 00:15**). **The machine was on battery through G5–G7; on mains at 22:54: keep it
on mains power**, or the run in progress is lost (PLAN §1.5).

**Next action.** **Blocked on the user:** `DECISIONS.md#G8-outline` must be approved before G9 (Sonnet 5.5, medium) runs
`docs/presubmission/round5/go.zsh G9`, which moves the 13 items of `round5/OUTLINE.md` §supplement-migration. G10 onwards
build to OUTLINE.md. GT2 only after the queue finishes.

**G8 added** `round5/OUTLINE.md`: the 11.5-page plan, one home per result (H1–H21), figures, appendices A–O, G9's list,
the title recommendation ("Right Ranking, Wrong Scale"), the abstract (210 words, 5 numerals) and contributions in keys,
and the rule-10 table. Its **[X11 slot]** marks are where GT2's readings may land; nothing anticipates them.

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

**Blockers.** `DECISIONS.md#G8-outline` (user approval) before G9.
