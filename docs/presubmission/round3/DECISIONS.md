# Round-3 decisions

## R0-rulings

PLAN.md §0.2, copied verbatim. **Defaults accepted by launching R0, 2026-10-04**: the user asked for the plan to be carried out as written ("Please read the instructions in PLAN3.md thoroughly and carry out the work as per instructions") and edited no line; `PLAN.md` here is byte-identical to the instruction file.

| # | Question | Default |
|---|---|---|
| V1 | Rule X2's design and thresholds (Annex 1). | **As written.** |
| V2 | What happens if X2 finds that our models barely respond to the action. | **Report it fully:** one clause in the abstract, a lesson in §9, a limitation in §5 and §11, and a caveat in the model card. |
| V3 | The abstract's sentence on history and forecast lengths. | **Annex 3's version.** It drops "even when that setting trains twice as long" and says that which setting wins depends on how long each is trained. |
| V4 | The abstract's sentence on action timing. | **One clause, with no effect sizes, describing all ten episodes:** the bug raises error at short horizons, and from the method's 100-step horizon the change is not resolved. |
| V5 | §3.2's table (about 3 pages). | **Move it into Appendix D as a second table.** §3.2 keeps its opening paragraph and a pointer, and every caption keeps its own arena, sample size and checkpoint. |
| V6 | Figure 1 plots 8 of the 22 rules, but its caption says "each decision rule". | **Redraw it over every rule**, from `results/appendix_g_rules.json`. The alternative is to fix the caption only. |
| V7 | §13's paragraph "On anonymity, stated rather than implied" says a reviewer "who chooses to look can identify the author". | **Shorten it to two sentences.** Keep the facts (the code is public, the submission bundle is scrubbed, and the reasoning is in `docs/DOUBLE_BLIND_DECISION.md`) and drop the invitation. The alternatives are to keep it as it is or remove it. |
| V8 | Length. | **Main text no longer than round 2's final count, 20,771 words** (FILE_MAP §13's command), and aim for 20,000 or fewer. Get there by moving text, never deleting it, and report any shortfall. |
| V9 | Add a §5.3 limitation that the RSSM was never tried with PlaNet's "latent overshooting", a training method aimed at exactly the long-range collapse ours shows? | **Yes, one clause, if the attribution checks out against PlaNet's own text** (through `t1_bibliography.py`). Otherwise skip it and log why. |
| V10 | Five training scripts report success even when training fails (round 2 OUT_OF_SCOPE, B8). | **Fix them to report failure.** No training is run to test this. |


## R0-arm-a-rollout-defect

**Raised by R0, 2026-10-09. Needed before R1.** Evidence: `PREFLIGHT.md` P2, "the Arm A half"; `r0_defect_check.py` and its output `r0_defect_check.json`.

**What R0 found.** `scripts/alignment_defect_ci.py:66` unpacks `pred, *_ = model.rollout(...)`. That is right for the released checkpoint, whose rollout returns a tuple. Our models' rollout returns the prediction tensor itself, so the line keeps only the first trajectory's forecast, and numpy compares that one forecast with all four trajectories' truths. Round 2's N1 (`scripts/alignment_by_horizon.py`) scored Arm A through this path. So every Arm A figure in `results/alignment_by_horizon.json` (both checkpoints, every horizon, both metrics) is void. Three of the four units are unrelated pairs, and their mismatch swamps any effect of the action.
- Through the committed path, Arm A's error is 0.92 to 1.40 at every cell. `results/mn_compute_matched.json`, computed correctly, gives 0.06 to 0.48.
- With the tensor taken whole, the same imported functions reproduce `mn_compute_matched.json` to 1.1e-8.
- R0 used the causal pairing only. **No corrected stale-action figure for Arm A exists yet**, so how much our models respond to the one-step shift is unknown.

**What rests on it.**
- `results/alignment_by_horizon.json` `arm_a`.
- Keys `stale_armA_rel_h1` and `stale_armA_rel_h368` (−0.22% and +0.15%), printed in:
  - §7.2's sentence (`PAPER.template.md:1176-1178`);
  - the model card's "Action convention" line (`scripts/build_model_card.py:328-340`). That line is also on the live Hugging Face card, uploaded 2026-10-04.
- Ledger `R-76` (tagged CONTRIB): its title ("our own checkpoints barely feel it") and its Arm A paragraph. Round 2's T3 ruling repeated the claim.
- This plan:
  - §0.1's third problem ("our own models hardly notice the timing bug");
  - Annex 1's motivation and its assertion (a) for Arm A. (a) asks I0 to reproduce both `alignment_by_horizon.json` and `mn_compute_matched.json`, which now disagree by up to 1.31, so it cannot pass with a correct rollout;
  - Annex 3 A9 (both variants presuppose the indifference);
  - guard G3.

**Not affected:**
- the released checkpoint's figures: `alignment_defect_ci.json`, `alignment_by_horizon.json`'s `released` block, and everything E2, contribution 7 and the abstract use;
- every other script, since only `alignment_by_horizon.py` feeds our models to `alignment_defect_ci`.

**Options.**
- **(A) Recommended: fix, correct post hoc, then X2 as ruled.** Done when R0 resumes, before R1:
  1. Make `alignment_defect_ci.rollout` take a returned tensor whole. Assert that `alignment_defect_ci.json` regenerates byte-identical and that `alignment_by_horizon.json`'s `released` block is unchanged.
  2. Regenerate `alignment_by_horizon.json`. Its Arm A block becomes the first correct measurement of our models' stale-action sensitivity. It is post hoc, like the rest of N1, and it exists before X2 is pre-registered, which is when the plan already intended that figure to be known.
  3. Ledger, append-only, classed by the corrected figures under the ledger's own rules:
     - if they still bear out "barely feel it", a new R- entry restating R-76 on the correct measurement, with R-76 marked SUPERSEDED;
     - if not, an S- entry withdrawing the claim, plus the restating R- entry. The count of claims withdrawn on evidence then rises by one, printed in §1, §8 and the README.
  4. Rebuild. §7.2 and the model card print the corrected figures through their existing keys. R3's E3 rewrites §7.2 with X2 as planned.
  5. X2 runs as V1 rules it. Annex 1's motivation figures are read from the corrected artifact, and assertion (a) reproduces both artifacts, now consistent. A9's text is chosen by X2's reading, keeping the "indifference to the one-step shift" clause only if the corrected figures show it.
- **(B) Leave Arm A's stale figure to X2.** Steps 1 and 3 as in (A), except:
  - `alignment_by_horizon.json`'s Arm A block is not regenerated until X2 has run. X2's I1, already one of its interventions, gives the first correct Arm A stale figures as pre-registered readings, and the regenerated N1 artifact is then asserted equal to them.
  - Assertion (a) for Arm A checks I0 against `mn_compute_matched.json` alone, in both arenas.
  - Stronger on pre-registration, but it amends V1's design, and until R1 runs, §7.2 and the model card keep printing the void figures (already public).

Either way, the live Hugging Face card carries the void figures until §0.4 step 2 re-uploads `MODEL_CARD.md` after R9, unless you want that done sooner.

**Answer, 2026-10-09**, asked in chat: "Fix, re-measure, then X2 (Recommended)", option (A). R0 resumes and carries out steps 1–5 before R1.

**The ledger's class, fixed before the corrected figures exist** (committed in this commit, before `alignment_by_horizon.json` is regenerated). R-76's claim is that "every 3-seed mean, in both metrics and at both checkpoints, is within 0.93% of zero: our checkpoints are almost insensitive to the stale pairing", and round 2's T3 ruling restated it as "under 1% at every horizon". The test applies R-76's own standard to the corrected artifact:
- **The claim stands** if every corrected three-seed mean overstatement on the held-out pair (relative-L1 and nRMSE form 1, at 2,500 and 10,000 iterations, at all six horizons) lies within ±1.00% of zero. Then one new R- entry restates R-76 on the correct measurement and names it. No retraction.
- **Otherwise the claim is withdrawn on evidence.** An S- entry retracts R-76's Arm A claim. R-76's Status line becomes SUPERSEDED IN PART, which `ledger_check.py` requires (its released-checkpoint half stands), and this ruling authorises that in-place edit. A new R- entry restates R-76 on the correct measurement.
