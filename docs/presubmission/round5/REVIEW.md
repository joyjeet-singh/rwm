# Round-5 fresh-eyes review (G16, 2026-10-24)

Method: build; main text extracted from the PDF to `round5/body.txt` (pages 1–12, 6,977 words) and read once; `rwm-referee` read
`body.txt` only; `rwm-checker` read Appendices A–H and I–O (each stopped at its turn limit and delivered what it had found:
**partial coverage**, listed below); every finding checked by hand against its artifact.

## Annex 6

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Gates, all blocking | **PASS** | `round5_gates.py` (blocking since this session, FILE_MAP §3): pages 11.67/12, abstract 209/5, `ids` 0, `once` 0, `sig` 0, `keys` 0 missing; `ledger_check.py` PASS; the eight prose checks, `xref_sweep` 0 suspect, `pdf_render_check` 5/5, supplement self-test PASS; two builds byte-identical |
| 2 | Annex 1 | **PASS with notes** | table below |
| 3 | Rule 10 | **PASS** | `CONSISTENCY.md` |
| 4 | Scope | **PASS after fixes** | the referee found numbers without scope; fixed (below). Every body number now names or inherits arena, n, checkpoint and horizon |
| 5 | Locked framing | **PASS** | `CONSISTENCY.md`, last row |
| 6 | First page | **PASS** | abstract and §1: what was found, why it matters (a penalty's two jobs), Figure 1 |
| 7 | Tone | **PASS** | neutral headings throughout (`PAPER.md:17–250`); the originals' documented designs credited (shared trunk, §5.1/§5.3; variance claim quoted, §5.1); no priority claims (grep "first" = 0 in claims) |
| 8 | Anonymity | **PASS** | deny-list sweep of both bundles and `docs/SUPPLEMENT.md`; PDF channels clean (see the log; re-run after the last build) |
| 9 | What the review praised | **PASS** | K1 §3.1 + App. A; K2 §3.4 + App. C; K3 §5.5; K4 §5.6; K5 §6; K6 §3.4 + App. E |

## Annex 1 (RV and K rows)

| RV | Result | Where |
|---|---|---|
| 01 | pass | `pages` gate, 11.67 |
| 02 | pass | abstract 209 words, 5 numerals; the referee read it cold and flagged only "sizes them wrong" as a fairness point (answered in §5.1/§5.7) |
| 03, 23 | pass | `ids` gate 0; verdict labels verbatim in App. E only |
| 04 | pass | `once` gate 0 |
| 05 | pass | `sig` gate 0 (exact n = 4 p-values print as fractions, 1/8 and 7/8) |
| 06 | pass | no "stood there as follows" in the PDF (grep 0); each appendix opens with its purpose |
| 07 | pass | Figure 1 shows two findings; the timeline is Figure 3 in App. E |
| 08 | pass | grep of `body.txt` for queue, CPU, history rewrite = 0 (the hits are "non-overlapping"); present in supplement S7–S9, S11 |
| 09 | pass | App. D "Versions" paragraph; `version_crosswalk` keys |
| 10 | pass | references 1 and 2 (`PAPER.md:254–`) |
| 11 | pass | §5.1 quotes RWM-U's variance claim |
| 12, 13 | pass | §5.3, App. O (decay row corrected; bootstrap row) |
| 14, 15, 16, 17 | pass | §5 structure (5.2 leads); X9 and X11e (§5.4); X10 and X11a (§5.2); N12 sentence (§3.2) |
| 18, 19, 20, 21, 22 | pass | §4.1 leads with X3; exact p beside every n = 4 interval (fractions); X11 at n = 20; §4.2 one paragraph; §4.3 "consistent, but a weak test" with floors |
| 24, 25, 26, 27, 28, 29, 30, 31 | pass | §5.7 and App. M; §5.5 and Figure 2; "too small by" defined once (§3.3) and used as k; App. F; Spearman headline; "no gradient from the bound term"; "optimum is σ = 0" with pathway caveat; PETS counts |
| 32–36, 46 | pass | §2 and the reference list |
| 37 | pass | title |
| 38 | pass | grep "first … aware" = 0 |
| 39 | **fixed** | App. O's row named "Table S9" for the follow-up's training table; now "its Table S8 in the first version" |
| 40 | pass | §6: the alignment query was sent before submission and had no reply (user's statement; no date recorded: the paper gives none) |
| 41 | pass | §8's reproducibility statement, 3 values |
| 42 | pass | CRPS beside coverage (§5.4, §5.7) |
| 43 | pass | headings |
| 44, 45 | open | G17 |
| K1–K6 | pass | as Annex 6 item 9 |

## Findings and their dispositions

**Referee (13 points; all verified).** Fixed in text: (1) fairness of "sizes them wrong": §5.1 now says RWM-U claims no calibrated interval and that a penalty weight absorbs a constant factor, and §5.7 says the finding is the growth with horizon; (2) Table 4's collapse row no longer rests on the checkpoint alone; (3) the Spearman unit is stated and the h = 1 index limit named; (4) the "band" is the ten-point band around the target; (5) R, the ratio and k are reconciled in one sentence; (6) per-fold gaps are "positive on each of four trajectories (descriptive)"; (7) the factor's driver is shown: teacher forcing is worse than the training-mean floor, rollout training better; (8) §4.2 and Table 4 wording now agree; Holm is "within each family, not across rules"; run counts (28, 75, 81) are explained; the released checkpoint's provenance sentence names its groups and allows "some"; (9) "signature of regularisation" became "consistent with regularisation and not with harm"; (10) terms glossed at first use (cell, log Δ, minimum detectable effect, share of the log gap, "both readings", the copies control); (11) "an afternoon's reading" removed. Not changed, with reasons: the retraction disclosures (load-bearing, CLAUDE.md); file:line citations in §5.1 and §6 (the line-level fixes are a K5 strength); the bitwise tally in the reproducibility statement (Y/PLAN item 5 asks for it); the abstract's lack of the exchangeability caveat (it names the horizon and "held-out", and §4.1 states the caveat).

**rwm-checker, Appendices I–O (partial: I–M and N's X2 and splice parts checked; O's code-line citations and N's pipeline rows not reached).** Verified and fixed: App. L's decomposition table had its two row labels swapped (+0.470 is the within-trajectory correlation, +0.878 the trajectory means); App. I's "flipping sign … close to chance" misdescribed a count-based agreement test (now "differs at"); App. J's "kl is zero because its dimension is" (kl belongs to the RSSM branch only; only extension has dimension 0); App. M's "still falling short at the far end" (the whole-rollout fit's far-end coverage is 65–72% depending on the fit episode). **Not checked:** the Appendix O code citations against the pinned upstream, N's two pipeline rows, the figure-caption interval count, `n13_adam.json`, `n9_recalibration_scores.json` and `e7_free_baselines.json` tables.

**rwm-checker, Appendices A–H (partial: A–G checked, H partly).** One wording fix: Appendix D's "beats the forecast-index counter at every horizon" now reads "from h = 8 (the index is constant at h = 1)". **Not checked:** the Appendix H head-to-head and compute-matched tables cell by cell, the training-tail slopes, the data-budget source fields, the "4 of 8 neighbours" alongside readings, part of `original_paper_figures.json`.

## For G17 and the user
- **The unchecked parts above** are the review's residual risk; they could be given to fresh checkers, but each rests on tables the build substitutes from artifacts and the gates read.
- Y10: the sent query has no date or reply in the record; the paper states neither.
- Figure 3 (σ-coverage by horizon) is **not drawn**: TMLR does not require it, §5.7's numbers are in prose, and drawing it would renumber the appendix figures; OUTLINE's Figure 3 slot is dropped.
