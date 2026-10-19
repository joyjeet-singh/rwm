# Round-5 checkpoint — after G1 (2026-10-19)

**State.** Branch `presubmission5`. Last log entry: **G1 — COMPLETE**. Nothing pushed. Y1–Y13 defaults stand.

**Next action.** Start G2 in a fresh terminal: `docs/presubmission/round5/go.zsh G2` (Opus 5.5, high). G2 reads
PLAN §1, its section, `PREMISES.md` (esp. B2 and P12, P20), `CROSSWALK.md`. It does not open the review.

**What G1 produced.** `round5/PREMISES.md` (P1–P40 + B1–B3), `round5/CROSSWALK.md` (incl. §code),
`scripts/version_crosswalk.py` → `results/version_crosswalk.json` (not a stage; needs network + gitignored
`docs/presubmission/sources/g1/`), six lines in `OUT_OF_SCOPE.md`, a FILE_MAP row.

**Facts G2/G3 must not lose.** (1) Both upstream repos: 0 commits since the pins; clones in
`/Users/Shared/rwm_verify/upstream_latest/`. (2) Imagination env picks one random member per env; the
evaluation path (`model_ids=None`) returns the ensemble mean — X9 must name its baseline path. (3) Per-head
bootstrap exists only in `rsl_rl_rwm`'s MBPO-PPO update. (4) "Checkpoint trained on all ten episodes" is an
assumption (P20) — X10 should say so. (5) RWM v1 has no 6M/250M table (B1; fix owner G12/G15).

**Blockers.** None. OpenReview workshop PDFs unreachable (browser challenge); record as not compared. Y5 queue not launched.

**Files.** `round5/{PREMISES,CROSSWALK,OUT_OF_SCOPE,SESSION_LOG,CHECKPOINT}.md`, `scripts/version_crosswalk.py`,
`results/version_crosswalk.json`, `docs/presubmission/FILE_MAP.md`.
