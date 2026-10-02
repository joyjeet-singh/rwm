# Round-2 decisions

## T0-rulings

PLAN.md §0.2, copied verbatim. **Defaults accepted by launching T0, 2026-10-02**: the user asked for the plan to be carried out as stated and edited no line.

| # | Question | Default |
|---|---|---|
| U1 | S-20 withdrew the 75% / 9.5% figures because new evidence contradicted them, but the ledger files it as a *framing*, not a *claim withdrawn on evidence*. | **Reclassify** through a new ledger entry (append-only), so the counts become 7 claims and 6 framings. `ledger_check.py` learns to read reclassification entries. |
| U2 | Allow up to 10 CPU-hours of RSSM retraining if the diagnostic (rule X1) points to training settings? | **Yes**, gated exactly as X1 says. |
| U3 | Length target. Round 1 accepted −1.3%; this ruling supersedes D7. | **Body ≤ 19,000 words** (FILE_MAP §13's command, "to Data and code"), reached by moving detail to appendices and never by deleting a result. Report a shortfall rather than force it. |
| U4 | The abstract's alignment sentence. | **One clause, no numbers**: the defect exists, and its cost is small and not consistent in sign. The numbers stay in the contributions and §7.2. |
| U5 | The claims audit (`submission_check` C1). | **Regenerate it after the text freezes (T11). Do not review** the unreviewed claims; that is recorded as known. |
| U6 | §6 has eleven subsections. | **Merge or move within §6 only.** Renumbering §6.x is allowed with a pointer map; top-level numbers (§7 onward) stay. |
