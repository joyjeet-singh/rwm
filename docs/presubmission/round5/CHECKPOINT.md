# Round-5 checkpoint — after G16R (2026-10-24)

**State.** Branch `presubmission5`. Last log entry: **G16R — BLOCKED**, ruled A (an independent re-review the user ordered after G17; `DECISIONS.md#G16R-ruling`). Nothing pushed. Main content 11.67 of 12 pages, abstract 210/5, every gate blocking and clean, two fast builds byte-identical. The PDF is now 56 pages.

**Done in G16R.** Review again from scratch, with fixes in sources (`REVIEW.md`, G16R section; `CONSISTENCY.md`, G16R rows). Log header times corrected (14 entries; a dated correction note in `SESSION_LOG.md`). Figure 3 dropped from OUTLINE, with its evidence now in Appendix M's two tables (`DECISIONS.md#G16R-figure3`).

**Ruling.** The user chose option A (`DECISIONS.md#G16R-blocked`, "RULED A"): a fix session, **G15-fix**, rewrites the stale appendix pointers. The brief is under that anchor. `go.zsh` does not know the name, so start it in a new terminal from the repository root with:

```
claude --model claude-opus-5-5 --effort high --name round5-G15-fix --settings '{"claudeMdExcludes":["'"$HOME"'/Downloads/CLAUDE.md"]}' "Read docs/presubmission/round5/PLAN.md §1, docs/presubmission/round5/DECISIONS.md#G16R-blocked (its G15-fix brief), the G16R section of docs/presubmission/round5/REVIEW.md and docs/presubmission/round5/CHECKPOINT.md, then carry out session G15-fix. The start gate is overridden by the user's ruling A."
```

**After G15-fix.** G17's steps 3–5 only (clean clones and restatement, both bundles with the builder scan and the independent deny-list sweep, the package documents), then G18. The paper, the PDF, four bundled scripts and bundled results changed after G17's freeze, so `docs/SUBMISSION_PACKAGE.md`'s PDF size and SHA-256 (55 pages) and `supplementary_anon.zip` are stale.

**Files.** `PAPER.template.md`; `scripts/paper_numbers.py` (`ver_diff_plain`; the `h2h_bl_*_label` section), `scripts/build_paper.py:414`, `scripts/md_to_tex.py` (unnumbered headings), `scripts/e4_sigma_gradients.py:44-47` with `results/e4_sigma_gradients.json`; `round5/REVIEW.md`, `CONSISTENCY.md`, `DECISIONS.md`, `OUT_OF_SCOPE.md` (four new lines), `OUTLINE.md`, `SESSION_LOG.md`.

**Open, unchanged.** The alignment query's date; the TMLR blog since 15 October (read it in a browser); the 356 unreviewed claims (ruled known); the figure pages, which no one has seen rendered.
