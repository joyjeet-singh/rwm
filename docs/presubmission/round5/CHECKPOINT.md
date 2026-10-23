# Round-5 checkpoint — after G14 (2026-10-24)

**State.** Branch `presubmission5`. Last log entry: **G14 — COMPLETE**. Nothing pushed. **Main content 11.25 pages (limit 12)**, abstract 207/5.

**Next action.** `docs/presubmission/round5/go.zsh G15` (Opus 5.5, medium): the appendices, standalone A–O. Appendices are still the earlier A–Z (letters, titles and contents unchanged except pointers); G15 re-letters them to OUTLINE's A–O, writes each opener, folds in the "stood there as follows" evidence, and moves G10's figure anchors with the appendices.

**G14 did.** New §6 (defects), §7 (lessons and limitations), §8 (conclusion, with Table 4, the claim table); old §7, §9, §11, §12 are supplementary S28–S31. The body is now §1–§8 plus "Reproducibility and data". Rule-10 audit of every summary site is in the log; contribution 4 and §1 now scope the rescaling claim.

**For the user.** (1) Y10: the alignment query is still an unsent draft, so §6 says it was not reported before submission; send it before submission and the sentence changes. (2) Figure 3 (σ-coverage by horizon) is undrawn; room exists (0.75 page).

**What G15–G17 must know.** The body's pointers use final numbering (§1–§8); appendix pointers use OUTLINE's letters (A–O) and today's letters coexist until G15 re-letters, so `pdf_render_check` check 1 only sees today's letters. The README template still points at the old section numbers (G17). `scripts/a1_consent_letter.py`'s fallback rewrites no longer match (G15, OUT_OF_SCOPE). Keys that leave the paper on purpose go into `RETIRED_KEYS.md`. `typed_numeral_audit`: cite "Name (year)", `$\rho$`, no bare numerals; `{{key|s2}}` on a text key fails. `pdftoppm` is absent: G16 must open the figure pages by eye. Table numbers: 1 arenas, 2 baselines, 3 ensembles, 4 claims.

**Blockers.** None.
