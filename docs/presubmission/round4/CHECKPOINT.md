# Round-4 checkpoint (workplan §2): F8 → F9, 2026-10-16

**State.** Branch `presubmission4`, last log entry **F8 — COMPLETE**. All commits since `110ecd7` are local; never push, merge, upload or submit (workplan §6). The tree is clean.
- **Body:** 17,790 words (`round2/t6_words.py`). That is over W6's editorial 16,000, and `DECISIONS.md#F8-length` holds the user's choice, which is open.
- **Abstract:** 300 words / 19 numerals.
- **PDF:** 75 pages, 0 overfull, 0 warnings. References start on page 27.
- **Main-text labels:** 51, with no R-, S- or commit labels.

**Read first, nothing else.**
1. `round4/PLAN.md`: §1 and the section "F9 — Pipeline hygiene".
2. `round3/OUT_OF_SCOPE.md`, as F9's section names it.
3. The last entry of `round4/SESSION_LOG.md`.
4. `round4/TMLR_CODEX_WORKPLAN.md` §4C (its F9 bullet), and `../CLAUDE.md`'s round-4 section.

**Exact next action: F9**, H1–H5. No paper prose moves in F9.
- **H1.** Add `reproduce.sh` stages, with `NEEDS_WEIGHTS` only where trained weights are read, for:
  - `x3_cross_fold.py`, `x4_matched_baselines.py`, `x6_stepsize_short_units.py`, `x7_loeo_recalibration.py`, `x8_released_pairing.py`, `n5_stale_armA_ci.py`, and the regenerated `a2_trajectory_level_control.py`;
  - not X5, which was not run (D-38; Appendix W).

  Add the full-run block for `runs/queue_round4.txt`. Target: `pipeline_coverage` 0 uncovered, stage 20n8 0 unclassified.
- **H2.** Appendix B's runtime table gains the round-4 runs, through its generator.
- **H3.** BUILD_CHECKS' list of claims withdrawn on evidence is generated from the ledger, or C7.1 checks its length. Appendix H's R-46 row records n_independent per arena. Confirm §5.2's per-configuration readings (F4, A4b).
- **H4.** Breaks inside `\texttt` paths. F4 added `_EXT_BREAK` in `md_to_tex.py` for file extensions. Check `pdf_render_check.py`, and every page with a file name.
- **H5.** The bundle self-test at HEAD detects its planted full hash.

**Tools.**
- Interpreter: the absolute path in `../CLAUDE.md`'s hard rule 2.
- End of session: `/Users/Shared/rwm_verify/evidence/R4F8/build/run.sh`, copied to `R4F9/` with its paths changed by sed. It runs the evidence summary, the fast build, eight gates, `part_f_gate` (it restores the gate's record), the build again, and the byte-identity check.
- Stage 21a: `./reproduce.sh --quick --force --stage 21a`, then remove `results/_regenerated.txt`.

**Traps.**
- **H2's contended runs:** `runs/queue_round4.log` was overwritten when another session resumed the queue on 14 Oct (`OUT_OF_SCOPE.md`). The first runner's lines survive only in `runs/queue_round4_done.txt` and in the F1–F4 log entries. Say so rather than inferring them.
- **Never edit a running shell script.** `reproduce.sh` is not running now; check before every edit.
- `paper_numbers.py` lines ≤2871 are cited elsewhere: add code only at the end of main().
- `compile_paper` fails on any LaTeX warning. Rerun `typed_numeral_audit` before `paper_numbers` when a numeral changes.
- A `NEEDS_WEIGHTS` guard on a stage that loads only the released checkpoint is wrong (round 2's lesson).

**Blockers:** none.

**Open:**
- `DECISIONS.md#F8-length` (user).
- README "What this found" lacks X3, X6 and X7 (F10).
- Rule IDs repeat in §5–§5.3 (`OUT_OF_SCOPE.md`; F10).
- `part_f_gate` 4b fails until F11 rebuilds the bundles.
- F11 rechecks TMLR's OpenReview form and the `tmlr.sty` provenance.
