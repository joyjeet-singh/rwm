# Round-4 checkpoint (workplan §2): F6 → F7, 2026-10-16

**State.** Branch `presubmission4`, last log entry **F6 — COMPLETE**. All commits since `110ecd7` are local; never push, merge, upload or submit (workplan §6). The tree is clean. Queue done (30/30). Discharged: X3 REPLICATES ACROSS FOLDS (M-94), X4 PARTIAL (M-95), X5 NOT RUN (D-38), X6–X8 (M-91–93). Abstract 300 words / 19 numerals (C12.1 cap 320). Body 22,313 words (`docs/presubmission/round2/t6_words.py`). PDF 69 pages, 0 overfull, 0 warnings.

**Read first, nothing else.**
1. `round4/PLAN.md`: §1, the section "F7 and F8 — Length and readability", and Annex 5.
2. `round4/TMLR_CODEX_WORKPLAN.md`: §2, §3, §4C, §8 and its addendum. The ≤16,000-word target is editorial, not a TMLR cap.
3. The last entry of `round4/SESSION_LOG.md`.
4. `../CLAUDE.md`'s round-4 section.

**Exact next action: F7.**
1. Verify the current TMLR author instructions (workplan §4C and §8 links) and record them.
2. Apply Annex 5's moves in priority order, moving text and never deleting it. Moved drafting history goes to `docs/BUILD_CHECKS.template.md`'s "Moved from the paper body" list. Log word counts after every move.
3. Remove R-/S-/D-/C-/B- IDs and commit labels from the main text (W8). Keep a rule's ID (M-xx, X-n) once per section where its verdict is reported.
4. Optionally qualify the abstract's first "checkpoint" as "released", within its 25-word clause.

**Tools.**
- Interpreter: `/Users/joyjeetsingh/Downloads/PDM/.venv-rwm311/bin/python`.
- End-of-session runner: copy `/Users/Shared/rwm_verify/evidence/R4F6/build/run.sh` to `R4F7/` (sed its paths). It runs: evidence summary, fast build, eight gates, `part_f_gate` (restores its record), build again, byte-identity.

**Traps.**
- `compile_paper` fails on ANY LaTeX warning; read its RESULT line.
- A `---` directly under a paragraph makes that paragraph a heading.
- Rewording breaks `check_comparative_claims` anchors ("says"/"sites"). Re-anchor only for a legitimate move, log old → new, and never shrink coverage.
- There are no new appendices: LaTeX's letters stop at Z.
- `paper_numbers.py` lines ≤2871 are cited; add code only at the end of main().
- `evidence_summary.py` (stage 21b) and `appendix_g_rules.py` (21a) are outside the fast build.
- Patch with the whitespace-tolerant matcher; assert one match.

**Blockers:** none.

**Open:**
- README "What this found" lacks X3, X6 and X7 (F10, public-facing check).
- `part_f_gate` 4b fails until F11 rebuilds the bundles.
