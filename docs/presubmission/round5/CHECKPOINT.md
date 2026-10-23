# Round-5 checkpoint — after G15 (2026-10-24)

**State.** Branch `presubmission5`. Last log entry: **G15 — COMPLETE**. Nothing pushed. Main content 11.25 pages (limit 12), abstract 207/5.

**Next action.** `docs/presubmission/round5/go.zsh G16` (Opus 5.5, high, **a new terminal**): the fresh-eyes review (PLAN Annex 6 is its checklist). G17 then rechecks against TMLR, freezes, measures and packages; G18 verifies a clean clone, last, no edits.

**G15 did.** Appendices A–O (outline lettering) with openers; new App. C (statistical methods), App. D's crosswalk, App. O's corrected rows; old Z, Y, X etc. regrouped; restating prose to supplementary S32. Figure order: 1 findings, 2 σ and Adam, 3 pre-registration lead time (E), 4 advantage by horizon (G), 5 calibration and 6 σ profile (I), 7 collapse (J), 8 contamination control (N).

**Open for G16/G17 and the user.** (1) **Figure 3** (σ-coverage by horizon) is undrawn: draw it or drop it from OUTLINE. (2) **Y10:** the alignment query is an unsent draft; §6 says it was not reported before submission. (3) The appendices are about 27,000 rendered words against 12,000 planned (see the log). (4) The README template still points at old section numbers, and the model card builder may too. (5) `scripts/a1_consent_letter.py`'s fallback rewrites no longer match (OUT_OF_SCOPE). (6) `pdftoppm` is absent: G16 must open the figure pages (pages with Figures 1–8) by eye. (7) `round5_gates.py` is still in report mode: its pages, abstract, ids, once and sig gates need G16 to read them as blocking; current report: pages 11.25/12, abstract 207/5, ids 21, once 1, sig 6, keys 0 missing.

**Carried facts.** `typed_numeral_audit`: cite "Name (year)", `$\rho$`, no bare numerals in prose; `{{key|s2}}` on a text key fails. `pdf_render_check` needs a heading for every section number the text points at, and every appendix letter in a pointer. Keys that leave the paper on purpose go into `RETIRED_KEYS.md`. Table numbers: 1 arenas, 2 baselines, 3 ensembles, 4 claims.

**Blockers.** None.
