# Vendored TMLR style files

`tmlr.sty` and `tmlr.bst` from https://github.com/JmlrOrg/tmlr-style-file (main),
unmodified. TMLR requires submissions to use the official template and treats
non-compliance as grounds for desk rejection at prescreening, so the files are
vendored here rather than assumed present on a builder's machine.

`scripts/build_paper.py` emits `PAPER.tex` against them in **submission mode** —
`\usepackage{tmlr}` with no option. In that mode `tmlr.sty` replaces the author
block with "Anonymous authors / Paper under double-blind review" and sets the
running head to "Under review as submission to TMLR". The `[accepted]` and
`[preprint]` options de-anonymise and must not be used for submission.
