# Round-4 checkpoint (workplan §2): F9 → F10, 2026-10-16

**State.** Branch `presubmission4`, last log entry **F9 — COMPLETE**. All commits since `110ecd7` are local; never push, merge, upload or submit (workplan §6). The tree is clean.
- **Body:** 17,790 words, accepted by the user (`DECISIONS.md#F8-length`, option 1); no further length cuts.
- **Abstract:** 300 words / 19 numerals.
- **PDF:** 75 pages, 0 overfull, 0 warnings. References start on page 27.
- **Pipeline:** `pipeline_coverage` 0 uncovered.
- **Main-text labels:** 51 (M- 26, X-rule labels 25), with no R-, S- or commit labels.

**Read first, nothing else.**
1. `round4/PLAN.md`: §1, the section "F10 — Fresh-eyes review", and Annex 6.
2. The last entry of `round4/SESSION_LOG.md`. Read no earlier entry (F10's rule).
3. `round4/TMLR_CODEX_WORKPLAN.md` §2 (the two-reviewer limit) and §4C (F10's bullet and the clear-writing standard), and `../CLAUDE.md`'s round-4 section.

**Exact next action: F10.**
1. Build, then extract the main text, pages 1–26, to `round4/body.txt`. `pdftotext` is not installed, so use `pypdf` (`.venv-rwm311`), page by page. Read it once, in chunks of about 300 lines. Look for:
   - a summary stronger than its section;
   - a number without an interval;
   - an unnamed arena or n;
   - an internal label;
   - clarity, against TMLR's 28 Aug 2026 criterion: what was found, why it matters, what readers learn.
2. Two read-only Explore reviewers (workplan §2: no more), one for Appendices A–M and one for N onward. Each gets only its range and the artifacts it cites, checks every table against every sentence citing it, and returns mismatches only (file:line, ≤300 words). Verify every finding yourself.
3. `round4/REVIEW.md`: pass/fail for each Annex 6 item, with file:line, and every finding.
4. Fix only items of 3 sentences or fewer; anything larger is `BLOCKED`, with the list.
5. `round4/CONSISTENCY.md`: one row per front-matter sentence, with its body anchor, every reading, and whether they agree.

**Carried in for F10:**
- README "What this found" lacks X3, X6 and X7 (the public-facing check).
- Rule IDs repeat within §5 (M-23, M-64), §5.2 (M-74) and §5.3 (M-75, M-76) (`OUT_OF_SCOPE.md`). W8 keeps one per section.
- The contributions list is untouched since F6.

**Tools.**
- Interpreter: the absolute path in `../CLAUDE.md`'s hard rule 2.
- End of session: `/Users/Shared/rwm_verify/evidence/R4F9/build/run.sh`, copied to `R4F10/` with its paths changed by sed.

**Traps.**
- `compile_paper` fails on any LaTeX warning.
- Rewording breaks `check_comparative_claims` anchors: re-anchor only for a legitimate move, and log old → new.
- Rerun `typed_numeral_audit` before `paper_numbers` when a numeral changes; "round 4" typed in prose fails it.
- C24.1 needs each section to keep its arena and n_independent.
- C27.2 and C28.2 pair `{{x2_reading}}` with "one policy".
- Summaries drop qualifiers: compare any edited summary with its body.

**Blockers:** none.

**Open:**
- `part_f_gate` 4b fails until F11 rebuilds the bundles.
- F11 rechecks TMLR's OpenReview form in a browser and the `tex/tmlr.sty` provenance.
