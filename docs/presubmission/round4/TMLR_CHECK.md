# TMLR author instructions, as read (workplan §4C and §8)

Workplan §4C asks for this check before any length move is treated as a venue requirement, and again at F11. Each
reading names the page and what it says. Quotation is kept to short phrases.

## F7 — 2026-10-16

| Source | What it says today |
|---|---|
| TMLR Author Guidelines (`jmlr.org/tmlr/author-guide.html`) | No page or word limit: submissions "may be any length", but length "should be justified by its content". Unusually long papers, appendices not counted, are "likely to result in reviewing delays". Submissions are PDFs built with the TMLR LaTeX style file and template; nothing is said about modifying it. Review is double-blind and submissions must be anonymised; a preprint may be posted, provided the submission does not link to a version that names the authors. Supplementary material: up to 100 MB, PDF or ZIP, anonymised. The page lists no submission types and no LLM-use disclosure, and mentions no author quota. A broader-impact statement is required where a work "carries a significant risk of harm". The page shows no last-updated date. |
| TMLR Reviewer Guide (`jmlr.org/tmlr/reviewer-guide.html`) | Length sets the review deadline, not acceptance: 2 weeks for submissions of up to 12 pages of main content before references, 4 weeks above that. This is the source of the addendum's "above 12 main-content pages". |
| Blog, "Increasing emphasis on clear writing" (28 Aug 2026) | The acceptance criterion on whether the audience would be interested now also asks whether the paper communicates its findings clearly: what was found, why it may interest the area, and what readers learn. No length or format rule. F10 checks against this. |
| Blog, "Annual author submission quotas" | The budget is harmonic in the number of coauthors (2 solo papers a year, up to 9 for nine-author papers), doubled for active action editors and reviewers. Every submission counts, accepted, rejected, withdrawn or desk-rejected, from 1 Jan 2026; it is enforced for submissions from 1 Jul 2026, and a submission is permitted only if every author has budget left. Checking the authors' remaining budget is the user's step before submission. |
| TMLR on OpenReview (`openreview.net/group?id=TMLR`) | Rendered as a loading placeholder only (the page needs JavaScript), so it was not read. F11 rechecks the live form in a browser. |

**What follows for F7 and F8.** The ruling of 16 Oct stands: W6's ≤16,000 body words (aim 15,000) is an editorial
target, not a venue cap. No reading above imposes a tighter limit, so no supporting detail has to leave the paper for
the supplement, and no claim is cut to fit. The body, at 22,313 words by `round2/t6_words.py` at F7's start, is far above 12 pages of main
content either way, so the paper takes the 4-week review track. `PAPER.tex` loads `tmlr.sty` from `tex/`, and
`scripts/submission_check.py` and `part_f_gate.py` check that it does. F11 records whether that file is the
official, unmodified one.
