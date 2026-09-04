# Deferred defects

Found during the paper revision programme, outside the scope of the session that
found them. Format: `[date] [session N] <file:line or section> — <what is wrong>`.

[2026-09-04] [session 1] scripts/pdf_render_check.py check 2 — the rendered-PDF pass compares only the SET of figure numbers appearing in source and PDF, so the committed PAPER.pdf, built before this session and still carrying the old figure references, passes all five checks unchanged.
[2026-09-04] [session 2] README.md:188 — README states 54 comparative claims across 22 kinds while the checker registry, PAPER.tex and docs/BUILD_CHECKS.md all state 55 across 23; running scripts/build_readme.py regenerates the file with the larger figures, so the committed README is stale relative to its own generator.
[2026-09-04] [session 2] PAPER.template.md:1631 — Appendix D says "The gate now refuses three further shapes as well as unresolved braces" and enumerates three; the build gate refuses seven shapes after this session, so the sentence's enumeration is complete only for the shapes added in the earlier revision.
[2026-09-04] [session 3] scripts/check_comparative_claims.py:20 — the module docstring introduces the check kinds as "the five failures they were written for" and enumerates five, while the file registers 24 kinds; the authoritative enumeration is generated into docs/BUILD_CHECKS.md, so the docstring is stale rather than contradicted by a check.
