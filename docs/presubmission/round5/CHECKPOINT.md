# Round-5 checkpoint — after G16 (2026-10-24)

**State.** Branch `presubmission5`. Last log entry: **G16 — COMPLETE**. Nothing pushed. Main content 11.67 pages (limit 12), abstract 209/5. **The round-5 gates are blocking**: `ids`, `once`, `sig` 0; `keys` 0 missing.

**Next action.** `docs/presubmission/round5/go.zsh G17` (Opus 5.5, medium): the TMLR recheck, freeze, measurements and packaging (RV44 draft: the conflict-of-interest text for the OpenReview form, Y11; RV45). Then G18 (Sonnet 5.5, medium): the clean-clone verification, last, no edits.

**G16 did.** Applied your three directives (Y10 sentence, README pointers, Figure 3 not drawn); read the body once; referee ×1 and checkers ×2 (partial); fixed every verified finding; made the gates clean and blocking; wrote `REVIEW.md` and `CONSISTENCY.md`.

**For G17 and the user.** (1) **Residual risk:** the checkers did not reach Appendix O's code citations, Appendix N's two pipeline rows, Appendix H's head-to-head and compute-matched tables, and a few artifact tables (list in `REVIEW.md`); consider two more checker reads. (2) Y10's query has no recorded date: add it to the paper only if you give it. (3) The pages gate has 0.33 page of margin: any text added in G17 needs a build and a `pages` read. (4) `pdftoppm` is absent: **no one has looked at the rendered pages**; open pages 2, 9 and the pages with Figures 3–8 by eye before submission. (5) `scripts/a1_consent_letter.py`'s fallback rewrites no longer match (OUT_OF_SCOPE). (6) Y12: no merge, push, upload or archive until after G18.

**Carried facts.** `typed_numeral_audit`: cite "Name (year)", `$\rho$`, no bare numerals in prose; `{{key|s2}}` on a text key fails; exact n = 4 p-values use the `_frac` keys. `pdf_render_check` needs a heading for every section number and appendix letter pointed at. Keys that leave the paper on purpose go into `RETIRED_KEYS.md`. Table numbers: 1 arenas, 2 baselines, 3 ensembles, 4 claims. Figures: 1 findings, 2 σ and Adam, 3 lead times (E), 4 advantage by horizon (G), 5 calibration and 6 σ profile (I), 7 collapse (J), 8 contamination (N).

**Blockers.** None.
