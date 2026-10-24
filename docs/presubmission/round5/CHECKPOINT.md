# Round-5 checkpoint — after G16R (2026-10-24)

**State.** Branch `presubmission5`. Last log entry: **G16R — BLOCKED** (an independent re-review the user ordered after G17; `DECISIONS.md#G16R-ruling`). Nothing pushed. Main content 11.67 of 12 pages, abstract 210/5, every gate blocking and clean, two fast builds byte-identical. The PDF is now 56 pages.

**Done in G16R.** Review again from scratch, with fixes in sources (`REVIEW.md`, G16R section; `CONSISTENCY.md`, G16R rows). Log header times corrected (14 entries; a dated correction note in `SESSION_LOG.md`). Figure 3 dropped from OUTLINE, with its evidence now in Appendix M's two tables (`DECISIONS.md#G16R-figure3`).

**Blocker.** About twenty sentences in Appendices D and H–M describe body content by the earlier paper's structure (for example "§5.2's released-checkpoint table", "§5.6's P column", and "the abstract and §8 use 33.4×"). That is more than G16's three-sentence fix limit. They are listed by `PAPER.template.md` line in `REVIEW.md` (G16R, "Open"). The question is `DECISIONS.md#G16R-blocked`: (A, recommended) a "G15-fix" session rewrites them; (B) accept them as known; (C) G16R resumes under a waiver.

**Next action (after the user's answer).** Whichever option is chosen, **G17's steps 3–5 must run again before G18**: clean clones and the restatement, both bundles with the builder scan and the independent deny-list sweep, and the package documents. The paper, the PDF, four bundled scripts and bundled results changed after G17's freeze. `docs/SUBMISSION_PACKAGE.md`'s PDF size and SHA-256 (55 pages) are stale, and so is `supplementary_anon.zip`. G16R did not run those steps. G18 comes after them.

**Files.** `PAPER.template.md`; `scripts/paper_numbers.py` (`ver_diff_plain`; the `h2h_bl_*_label` section), `scripts/build_paper.py:414`, `scripts/md_to_tex.py` (unnumbered headings), `scripts/e4_sigma_gradients.py:44-47` with `results/e4_sigma_gradients.json`; `round5/REVIEW.md`, `CONSISTENCY.md`, `DECISIONS.md`, `OUT_OF_SCOPE.md` (four new lines), `OUTLINE.md`, `SESSION_LOG.md`.

**Open, unchanged.** The alignment query's date; the TMLR blog since 15 October (read it in a browser); the 356 unreviewed claims (ruled known); the figure pages, which no one has seen rendered.
