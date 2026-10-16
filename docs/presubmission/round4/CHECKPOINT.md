# Round-4 checkpoint (workplan §2): F7 → F8, 2026-10-16

**State.** Branch `presubmission4`, last log entry **F7 — COMPLETE**. All commits since `110ecd7` are local; never push, merge, upload or submit (workplan §6). The tree is clean. The body is 20,585 words (`docs/presubmission/round2/t6_words.py`; it was 22,313 at F7's start). The abstract is 300 words / 19 numerals. The PDF is 72 pages, 0 overfull, 0 warnings. TMLR sets no length limit (`round4/TMLR_CHECK.md`), so W6's ≤16,000 is editorial.

**Read first, nothing else.**
1. `round4/PLAN.md`: §1, the section "F7 and F8 — Length and readability", and Annex 5 (its rows from §6.2 down).
2. `round4/TMLR_CODEX_WORKPLAN.md`: §2, §3 and §4C.
3. The last entry of `round4/SESSION_LOG.md`, and `round4/LENGTH_LOG.md`'s "F7 end" paragraph.
4. `../CLAUDE.md`'s round-4 section.

**Exact next action: F8**, covering §6 to §13, with the appendices only as destinations.
1. Apply Annex 5's rows for §6.2, §6.3–6.4, §6.5, §6.6, §6.7–6.8, §7, §11 and §12 in full, moving text verbatim and never deleting it. **At least 4,585 words must come from 12,849** for ≤16,000, and 5,585 for 15,000. Keep §9, every verdict, every number the abstract cites, and X6/X7/X8's locked framing.
2. W8 in that range: replace R-/S-/D-/C-/B- IDs and commit labels with plain words, keeping a rule ID once per section where its verdict is reported. Generated text carries IDs too (e.g. `paper_numbers.py`'s sentences, `build_paper.py`'s captions): grep the rendered `PAPER.md`.
3. Split sentences of over about 45 words with more than two qualifiers.
4. Report: the final count against 16,000; the three largest remaining sections; pages before References; and the ID count against F0's (`round4/BASELINE_F0.md`).

**Tools.**
- Interpreter: the absolute path in `../CLAUDE.md`'s hard rule 2 (`.venv-rwm311/bin/python` under the PDM directory).
- After each move: `/Users/Shared/rwm_verify/evidence/R4F7/move/move.sh`, copied to `R4F8/` with its paths changed by sed. It runs one fast build, the eight gates and the word count.
- End of session: `R4F7/build/run.sh`, copied the same way.
- F7's move scripts are in `/Users/Shared/rwm_verify/evidence/R4F7/move/` (`m1_related.py` … `m6_detail.py`, `s3_split.py`). Pattern: find each passage by exact anchors, assert it occurs once, write the summary, move the text verbatim under a bold-titled section of the destination appendix, and retitle the appendix if needed.

**Traps.**
- **No new appendix:** LaTeX's letters end at Z. Use titled sections inside an existing one.
- **C19.1 (restatement):** the same numeral printed with two units in one section fails, e.g. "1.16 to 1.27×" beside "1.16×". Give both ends of a range their unit, or write "times".
- **Typed numerals:** a bare "1" or "10" in new prose fails `typed_numeral_audit`, and `paper_numbers` then fails on its stale record. Rerun the audit first, then the build.
- **C10.5:** a BUILD_CHECKS sentence naming an S- entry must name its class ("framing" or "withdrawn on evidence").
- **`build_paper.check_h8_gap_labels`:** any §5 sentence printing an h = 8 gap key needs an iteration or checkpoint key.
- `compile_paper` fails on any LaTeX warning. A `---` directly under a paragraph makes it a heading.
- Patch with the whitespace-tolerant matcher and assert one match.

**Blockers:** none.

**Open:**
- README "What this found" lacks X3, X6 and X7 (F10).
- `part_f_gate` 4b fails until F11 rebuilds the bundles.
- F11 rechecks TMLR's OpenReview form in a browser and whether `tex/tmlr.sty` is the official, unmodified file.
