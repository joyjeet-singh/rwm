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

## T3-alignment-framing

**Raised by T1, 2026-10-02. Needed before T3; T1 and T2 are not blocked.**

Ruling U4 and Annex 3 have the abstract, contribution 6 and §3.2's row say the alignment defect's cost is "small and not consistent in sign". N1 (`results/alignment_by_horizon.json`, ledger R-76) measured it at every horizon, and that wording fits only h = 368.

- **On the held-out pair, the released checkpoint's relative-L1 rises at every horizon, and every interval excludes zero.** It is largest at h = 32. At h = 1 the figure is the one Annex 3's §7.2 variant (a) prints (`adh_rel_h1`).
- **Over all ten episodes, the rise is resolved at h ≤ 32.** The point estimates turn negative at h ≥ 128, and those intervals do not exclude zero.
- So the cost is not small at short horizons. "Not consistent in sign" holds only for the long horizons over all ten episodes.
- Our own Arm A barely notices the shift: under 1% at every horizon.

Annex 3 allows tightening the wording but not strengthening the claims. Its sentence as drafted would now understate a measured effect.

Options:
- **(A) Recommended.** Keep U4's form (one clause, no numbers) and make it true at every horizon:
  - Abstract: "Separately, the released evaluation pairs each prediction with the previous step's action; this inflates the checkpoint's error most at short horizons, and at the method's long horizon the cost is small and not consistent in sign."
  - Contribution 6's lead: "The released evaluation is misaligned by one step; the cost is concentrated at short horizons, and at h = 368 it is small and not consistent in sign."
  - §3.2's row: "defect confirmed in the code; its cost is concentrated at short horizons, and at h = 368 is small and not consistent in sign".
- **(B)** Install Annex 3's wording as written, accepting that it understates the short-horizon cost that R-76 records.
- **(C)** Make the abstract clause name the defect and no cost: "Separately, the released evaluation pairs each prediction with the previous step's action." The costs stay in contribution 6 and §7.2.
