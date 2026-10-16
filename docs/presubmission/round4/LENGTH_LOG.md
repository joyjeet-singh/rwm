# Length log, F7 and F8 (PLAN F7/F8 item 4; Annex 5)

Body words by `docs/presubmission/round2/t6_words.py` (Introduction to "Data and code", tables included). W6's target is
≤16,000, aiming for 15,000; it is editorial, not a TMLR cap (`TMLR_CHECK.md`). Text is moved, never deleted (§1.2 rule
10): each row names what left, where it went, and the section's words before and after.

**F7 start (2026-10-16):** 22,313. F7's range, the Introduction to §5.3: 9,464 (§1 1,333; §2 1,123; §3 519; §3.1 739;
§3.2 104; §4 405; §5 2,089; §5.1 305; §5.2 1,362; §5.3 1,485).

| # | Section | Moved | To | Section words | Body words |
|---|---|---|---|---|---|
| 1 | §2 Related work | Seven paragraphs, verbatim (the method's family, deep ensembles, the three sources of uncertainty, miscalibration, recalibration, trunk sharing, the objective's neighbour, 676 words); §2 keeps one sentence for each, the direct precedent, what is new, and the PETS lineage's two sentences | Appendix I, new titled section "Related work in full (§2)", retitled to name it. Not a new appendix: the letters end at Z | 1,123 → 821 | 22,313 → 22,011 |
| 2 | §3.1 Metrics | The four metric paragraphs with their six display formulas, and "That nominal is checked rather than assumed" (M-65's sentence), verbatim (432 words); §3.1 keeps relative-L1 and nRMSE in words, one or two sentences each for coverage and ρ (the nominal stays, since §6.2 points to §3.1 for it), the cumulative convention (now in "Horizons"), and "Which metric each headline uses" unchanged | Appendix G, new titled section "The metrics' formulas (§3.1)", retitled to name it | 739 → 582 | 22,011 → 21,854 |
| 3 | §5 | The floor paragraph, "Seeds, and what four trajectories can show" and "What is small", verbatim (559 words); §5 keeps two sentences of each, the seed-variance sentence (C6.1's anchor) joining the paragraph under the table. The long-horizon paragraph (111 words) is not copied: Appendix L already states each of its clauses, in its opening (the 4 of 4 cells), "Multiplicity" (Bonferroni and Holm) and the reimplementation reading under its table; §5 keeps its cell count | Appendix L, new titled section "Three passages of §5 in full", retitled to name it | 2,089 → 1,628 | 21,854 → 21,393 |
| 4 | §5.1 | Its four paragraphs, verbatim (288 words): the transition count's derivation, what it is not, the reproduction on that budget, and "Three limits"; §5.1 keeps two sentences with the transition count, the ratio and the percentage the abstract cites | Appendix L, new titled section "The data budget (§5.1)"; L retitled | 305 → 93 | 21,393 → 21,181 |
| 5 | §5.2, §5.3 (beyond Annex 5, which lists no row for them) | §5.2's "Accuracy at equal compute" (230 words) → Appendix U, titled "§5.2's reading, in full"; §5.2 keeps three sentences. §5.3's pooled-nRMSE passage (128) and "Our RSSM is not an informative comparison" (257, with rule X1's generated Part C sentence) → Appendix L, titled "Two passages of §5.3 in full"; §5.3 keeps summaries that state both rules' changed readings and both of X1's verdicts. W8 in passing: "ledger R-77" and "ledger R-78" leave the main text. In the moved RSSM text, "1.16 to 1.27×" became "1.16× to 1.27×": beside §5's 1.16× in the same appendix the bare numeral was ambiguous (C19.1) | Appendices U and L | 5.2: 1,362 → 1,221; 5.3: 1,485 → 1,201 | 21,181 → 20,756 |
| W8 | §4, §5, Figure 1's caption, the abstract | Labels, not text: §4's "(`S-17`)" clause (its history to BUILD_CHECKS' moved list, naming it a withdrawn framing, as C10.5 requires); §5's commit label (Appendix E's commit column gives it) and "ledger R-60" (the date stays, bound); Figure 1's "(S-12)" (now §7.4's duplication control and §8). The abstract's only "checkpoint" becomes "released checkpoint", "A" dropped to keep the clause at its length; C9.1 re-anchored | BUILD_CHECKS (S-17's history) | — | 20,756 → 20,744 |
| 6 | §4, §5, §5.2, §5.3 | Five detail passages, verbatim (276 words): §4's and §5's notes on the two definitions of teacher forcing, and §5.3's diverged-row note → Appendix L ("Teacher forcing's two definitions", "The diverged baseline rows"); §5.2's note on how its alongside nRMSE was computed and its training-loss slopes → Appendix U. Each section keeps a sentence and a pointer. Two wording changes for C19.1: §5's "N = 1" set in math (the slot check matched it to a count), and the moved "{{div_factor}}×" written "times" (beside X3's "10 of 10" in the same appendix) | Appendices L, U | §4 405 → 352 (with W8); §5 1,628 → 1,603 (with W8); §5.2 1,221 → 1,174; §5.3 1,201 → 1,147 | 20,744 → 20,581 |
| item 3 | §1–§5.3 | No text moved: 22 sentences of over about 45 words with more than two qualifiers split at their clause boundaries, every qualifier kept; where a clause became a sentence it gained a subject or a joining word ("So", "That is", "Each is also", "It", "it is"), and in three the clause order changed (X3's "Both arms were trained … Over the 20 … trajectories, the gap", §5's h = 8 checkpoint sentence, §5.2's "Other readings …, though,"). The contributions are left whole: each of the eight bullets already has the three sentences Annex 6 allows, bold lead included, so a split would break that limit; F10 checks them as a whole | — | — | 20,581 → 20,585 |

**F7 end (2026-10-16):** 20,585 body words, 1,728 fewer than at F7's start (22,313). F7's range, the Introduction to §5.3,
went from 9,464 to 7,736: §1 1,337; §2 821; §3 519; §3.1 584; §3.2 106; §4 352; §5 1,606; §5.1 92; §5.2 1,173; §5.3 1,146.
The appendices grew by the moved text, so the PDF goes from 69 to 72 pages. `xref_sweep.py` reported 0 suspect pointers
after every move, and every gate passed after each one.

**Against the plan's split.** F7 made 1,728 of the 6,313 words needed for 16,000 (27%), or of the 7,313 for 15,000 (24%),
short of the plan's "about 40%". Annex 5's rows for F7's range are done. The largest block left in that range is the
contributions list, about 950 words. F6 fixed it at 8 bullets of at most 3 sentences, and five guards scan it for rule
11 (C25.1, C25.2, C26.1, C27.1, C28.3). It is a summary of every reading, not detail to move, so F7 left it
alone. **F8 therefore needs at least 4,585 words from its range** (12,849 words at F7's end, §6 to §12) for 16,000, and
5,585 for 15,000: 36% to 43% of it. Annex 5's F8 rows leave each section with its verdicts and key rows, which is a cut
of about that size if all of them are applied in full.

**F8 start (2026-10-16):** 20,585 body words; F8's range, §6 to §12, 12,849.

| # | Section | Moved | To | Section words | Body words |
|---|---|---|---|---|---|
| F8-1 | §6.2 | Verbatim (569 words): the released checkpoint's table at every horizon (§6.2 keeps its h = 1 and h = 100 rows, as Annex 5 says, with a one-line note), the held-out-pair version's comparison, "The larger sample changes one thing materially", the ensemble-5 arms' table with its paragraph (§6.2 keeps two sentences and the headline figures), and the permutation note (quoted in Appendix M's opening, whose third paragraph already states it in full). Kept: why h = 1 comes first, the constant-scale paragraph, M-62 and M-63's verdicts, h = 100, the applied scalar's correlation. Two gate fixes in the new and moved text: "ensemble size 5" kept on one line (the typed-numeral class matches it only so), and the held-out-pair note gains "400-step trajectories" (C20.1: an n_independent names its unit) | Appendix M, new opening and four titled sections; retitled "section 6.2 in detail" | 1,791 → 1,433 | 20,585 → 20,227 |
