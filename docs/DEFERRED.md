# Deferred defects

Found during the paper revision programme, outside the scope of the session that
found them. Format: `[date] [session N] <file:line or section> — <what is wrong>`.

[2026-09-04] [session 1] scripts/pdf_render_check.py check 2 — the rendered-PDF pass compares only the SET of figure numbers appearing in source and PDF, so the committed PAPER.pdf, built before this session and still carrying the old figure references, passes all five checks unchanged.
