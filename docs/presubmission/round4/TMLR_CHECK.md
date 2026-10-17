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

## F11 — 2026-10-17

Read in a browser on 17 October. Quotation is kept to short phrases.

| Source | What it says today |
|---|---|
| TMLR Author Guidelines (`jmlr.org/tmlr/author-guide.html`) | Unchanged from F7's reading: any length, justified by content, with unusually long main texts likely to delay review; PDFs built with the TMLR style file and template; double-blind and anonymised; supplementary material up to 100 MB, PDF or ZIP, anonymised; preprints allowed if the submission does not link to a named version. It also says all authors need "complete and active" OpenReview profiles, and that the submission asks for suggested action editors, human-subjects (IRB) reporting, funding and competing interests. |
| Submission Guidelines and Editorial Policies (`jmlr.org/tmlr/editorial-policies.html`) | Not read at F7; the Author Guidelines require authors to know it. Reproducibility studies are in scope, and a Reproducibility Certification exists. **LLM use:** LLMs "may be used as general-purpose assistive tools"; authors are fully responsible for the content; no disclosure is required, and LLMs cannot be authors. So the 16 October decision not to add an LLM-use footnote stands with the venue's rule. **Quotas:** the same rule as the blog post below, and "It is the responsibility of the authors" to check every author's remaining budget. **Authorship:** the exact author list is fixed at submission; no author may be added or removed afterwards. |
| OpenReview submission form (`api2.openreview.net`, invitation `TMLR/-/Submission`, last modified 7 Oct 2026) | The venue page (`openreview.net/group?id=TMLR`) did not finish loading in the browser, so the form was read from the invitation's public definition. Fields: title (at most 250 characters), abstract (at most 5,000), authors and their OpenReview profiles, the PDF (at most 50 MB), a submission-length choice, supplementary material (one ZIP or PDF, at most 100 MB, visible to reviewers and the public, anonymised), a previous TMLR submission and changes (optional), competing interests and human-subjects reporting (both required; "N/A" where not applicable). This paper is a **"Long submission (more than 12 pages of main content)"**. The form has no deadline. |
| Blog, "Annual author submission quotas" (17 June 2026, updated 13 July) | As F7 read it: the generalized harmonic rule, N_1 = 2 (an author of solo papers only may submit 2 a year) and N_9 = 9, doubled for active reviewers and action editors; every submission since 1 Jan 2026 counts, whatever its outcome, and a submission needs budget left for every author. **How to check:** each author runs TMLR's `coauthor_counts.py` (github.com/JmlrOrg/tmlr, `src/`), which logs in to OpenReview with that author's email and password and lists the author count of each of their 2026 TMLR submissions, then enters those counts in the calculator at `cs.cmu.edu/~nihars/quota/author.html`. The check needs each author's own login, so it is the authors' step, not this session's. |
| Blog, "Adapting our processes" (15 Oct 2026; new since the workplan) | Desk rejection is now about 53% of submissions, mostly at the Editors-in-Chief's first screening, for claims or evidence that are not clear from the writing, evidence that does not meet the claims, or low interest. From October 2026 every submission also gets one AI review of soundness (whether the claims are met with convincing evidence), which the action editor may use. Attempts to get round the quota (a second account, dropping an author) are penalised. No format rule changes. |
| Blog, "Asking authors about their own papers" (16 Sep 2026; new since the workplan) | An Editor-in-Chief met the authors of ten submissions headed for desk rejection, most of them solo-authored, to ask basic and technical questions about their own papers. The authors of a submission may be asked to explain it before review. No rule changes. |
| `tex/tmlr.sty`, `tex/tmlr.bst` against `github.com/JmlrOrg/tmlr-style-file` (`main`) | **Official and unmodified.** The live files were hashed in the browser and match the vendored copies byte for byte: `tmlr.sty` 6,560 bytes, SHA-256 `816214ff…0002`; `tmlr.bst` 26,969 bytes, SHA-256 `306fd454…5206`. `PAPER.tex` loads `tmlr` with no option, which is the anonymous submission mode. |

**What follows.** Nothing read today changes the package. The paper is any-length-compliant, uses the official style
files unmodified, is anonymised, and its supplement is a ZIP under 100 MB (sizes in `docs/SUBMISSION_PACKAGE.md`). The
abstract fits the form's 5,000 characters. The steps left to the authors are the quota check above, complete OpenReview profiles
for every author, the suggested action editors, competing interests and human-subjects reporting ("N/A"), and choosing
"Long submission" on the form.
