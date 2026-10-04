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

