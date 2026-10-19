# Round-5 checkpoint — after G2 (2026-10-19)

**State.** Branch `presubmission5`. Last log entry: **G2 — COMPLETE**. Nothing pushed. Y1–Y13 defaults stand (Y5 = B).

**Next action.** Y5 is B, so the next session is **GT1** (Opus 5.5, high): `docs/presubmission/round5/go.zsh GT1`.
GT1 completes `round5/PROTOCOLS.md` §4 (every ‹GT1›), probes one ensemble-5 and one single-model run on an idle machine,
projects against the 30 CPU-h cap, commits the X11 rule and queue under a `PRE-REGISTER` subject, and launches the queue
in the background. After GT1: G3 (X9, X10).

**What G2 produced.** `round5/PROTOCOLS.md` (commit 2d71330): X9 and X10 pre-registered rule text (§2, §3), X11 skeleton
(§4), N7–N14 specifications (§5), summary table (§6), changes from Annex 2 (§7). Two lines in `OUT_OF_SCOPE.md`.

**Facts later sessions must not lose.** (1) G3 must commit X9's and X10's ledger entries (`PRE-REGISTERED`, IDs from
`ledger_check.py`) and their scripts under a `PRE-REGISTER` subject **before** the first reading; the scripts are then
frozen. (2) X9's MEAN must call `rollout_uncertainty` / `rollout_independent` unchanged; assertions run before any
per-member number. (3) X9 (d) batches four trajectories per fold through `MN`'s input construction (batching moves
h = 368 values by ~1e-2). (4) N10's seasonal period is written into the script in its own commit before any scoring.
(5) The correspondence lives outside the repo (`../rwm_private/`); quote only what App. F quotes.

**Blockers.** None.

**Files.** `round5/{PROTOCOLS,OUT_OF_SCOPE,SESSION_LOG,CHECKPOINT}.md`.
