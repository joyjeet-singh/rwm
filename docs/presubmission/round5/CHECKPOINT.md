# Round-5 checkpoint — after G15-fix (2026-10-24)

**State.** Branch `presubmission5`. Last log entry: **G15-fix — COMPLETE** (ruling A of `DECISIONS.md#G16R-blocked`). Nothing pushed. Main content 11.67 of 12 pages, abstract 210/5, every gate blocking and clean, the last two fast builds byte-identical. PDF 56 pages.

**Done in G15-fix.** G16R's 19 stale appendix pointers, plus 60 more found by checking all 203 section references and 49 appendix-letter pointers in Apps A–O against their targets; two pointers in `scripts/evidence_summary.py` (artifact regenerated, pointer strings only). No number, key, verdict or scope changed (`rwm-checker`: 0 mismatches). Details in `REVIEW.md`, G15-fix.

**Next action.** G17's steps 3–5 only: (3) clean clones and the restatement; (4) both bundles with the builder scan and the independent deny-list sweep; (5) the package documents. Then G18. The paper, the PDF, bundled scripts (`paper_numbers.py`, `build_paper.py`, `md_to_tex.py`, `e4_sigma_gradients.py`, `evidence_summary.py`) and bundled results changed after G17's freeze, so `docs/SUBMISSION_PACKAGE.md`'s PDF size and SHA-256 (55 pages) and `supplementary_anon.zip` are stale. `go.zsh` does not know a "G17 steps 3–5" session; start it by name in a new terminal, as the G15-fix prompt was.

**Blockers.** None.

**Open, for a session allowed to change scope wording** (`OUT_OF_SCOPE.md`, G15-fix lines): six appendix sentences (H:646, L:1323, N:1414/1434/1454/1469) call all ten episodes the released checkpoint's training data, against §3.2; "33 runs for §4.1–§6" (J:907, K:1022) excludes the fold runs.

**Open, unchanged.** The alignment query's date; the TMLR blog since 15 October (read it in a browser); the 358 unreviewed claims (ruled known, U5); the figure pages, which no one has seen rendered.
