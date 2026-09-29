# S10 — fresh-eyes review

Written 2026-09-29 by S10, against PLAN Appendix E's "Checklist for S10".
By the ruling `DECISIONS_FOR_USER.md#S10-fresh-terminal`, S10 ran in the conversation that had just run S9. The fresh eyes were two read-only agents (Sonnet 5.5, Explore), given only:
- PLAN's S10 text;
- Appendix E's checklist;
- the file locations.

This session then:
1. verified every finding against the files;
2. fixed the small ones (commit `040f336`, item 4);
3. listed the rest below.

Line numbers are `PAPER.template.md` after `040f336`, unless another file is named.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | §5 prose and table agree at h = 8; every h = 8 figure names its checkpoint | **pass** after fixes | h = 8 paragraph `:507-517` (seed 1 and all three seeds at 10,000 iterations; the 500 and 2,500 checkpoints); `:513` now names the arena of the 0-of-4 cells; `:439` names the in-sample exception (fixed: "same direction at every horizon and checkpoint" was false at h = 8 after 500 iterations, `results/review_bootstrap_unit.json`); §8 `:1503` names the changed cell (`bu_change_cell`). Anchors: "weakest exactly where the" `:463` present; "long-horizon phenomenon" and "What does not hold" absent. |
| 2 | Every table with an arm row names its iterations; the 0.3582 / 0.5856 difference explained where both appear | **pass** after fixes | Explained at `:554`, the only place both appear. §6.2's ensemble-5 table now names 2,500 iterations `:778` (asserted against `results/task_d3_ens5.json`). The build gate `check_arm_table_captions` (`scripts/build_paper.py:145`) covers every other arm table. |
| 3 | "Unseen by the multiplier/model" used consistently; 17/36 and 10/36 in §6.8; caveat in abstract, contributions, §9, §11, §12; "looks repairable" gone | **pass** after fix | Defined `:98`, §6.8 `:1188-1221`; 17/36 at `:22`, `:99`, `:1211-1221`. "looks repairable" appears nowhere. Appendix D's epistemic row `:1865` said "repairable per horizon" with no caveat; it now carries the 17-of-36 caveat. |
| 4 | Alignment defect with both metrics and intervals everywhere; §7.2 reset-row evidence; no author-confirmation sentence | **pass** | Both metrics and both intervals at `:26`, `:104`, `:363` and `:1433`. Reset-row evidence at `:1425`. The 75% / 9.5% figures appear only as withdrawn (`S-20`, `:1444`). No sentence says the author confirmed the alignment. |
| 5 | New title installed, old one nowhere; contributions lead with order-right/size-wrong, ≤ 7 bullets of ≤ 3 sentences | **partial** | New title `:1`; the paper, `.tex` and PDF carry no old title. Contributions `:61` lead with order-right/size-wrong. **8 bullets**, allowed by the user's S9 ruling (`DECISIONS_FOR_USER.md#S9-contributions-abstract`). Each is at most 3 sentences. **The old title survives outside the paper:** `docs/SUBMISSION_PACKAGE.md:54`, and the tracked, already-pushed `supplementary_anon.zip` (built 2026-09-27, before S3). See D6 below. |
| 6 | Broader impact matches Appendix B, numbers bound | **pass** | §10 `:1546` is PLAN Appendix B word for word, with 100, 33.4×, 4.61% and 68.27% bound (`v2_deploy_h`, `d1n_epi_ratio_h100`, `d1n_epi_cov1_h100`, `v3_cov_nominal1`). One reviewer observation, not changed because the text is the approved one: the 33.4× does not name its arena (the released checkpoint on all ten episodes, which it trained on); the abstract does. |
| 7 | Body ≥ 30% shorter than S0, or the shortfall reported; drafting history in BUILD_CHECKS; no numeric assertion retired | **fail on length, reported** | **Body:** 26,900 words to "## References" against S0's 27,387 (−1.8%), or 26,387 to "## Data and code" against 26,874, the same −1.8%. The target of 19,170 is missed by 7,730. S7 reported a shortfall of 5,583; S8 and S9 added the §5.2/§5.3 results since. S9's log compared its "Data and code" count with S7's "References" count; the like-for-like figures are the ones here. **Drafting history:** 28 items in BUILD_CHECKS' moved section (S7's log said 29). **Assertions:** none retired; the comparative-claims registry keeps the same 60 ids as at S0. See D7. |
| 8 | Retraction counts generated and identical in introduction and §8; no inaccurate "orders of magnitude" | **pass** after fix | Introduction `:56` and §8 use the same keys (20 superseded, six withdrawn on evidence, seven framings). "12 retractions" and "Six retractions on our own evidence" are gone. The magnitude phrases hold. The sentence at `:771` said σ "is nearly flat", but epistemic σ grows 2.74× over the rollout; it now says σ "grows far more slowly than error". |
| 9 | §5.2/§5.3 report verdicts exactly as returned; both rules committed before their runs | **pass** | `:600` NOT OPTIMAL AT OUR BUDGET and `:646` REPRODUCES / RWM AHEAD OF ALL THREE, verbatim from `results/mn_sweep_verdict.json` and `results/baselines_verdict.json`. Appendix E gives M-74, M-75 and M-76 lead times of +29.4 h. PRE-REGISTER commit `3df0e55` precedes the first sweep run and the first baseline run. |
| 10 | §4, Appendices B–E, §3.2, §11 reflect six tested claims; "architecture" vs "free" baselines never confused | **pass** after fix | §4 `:393`; Appendix B `:1793`; Appendix C `:1803`; Appendix D (six **yes** rows); Appendix E (21 rules); §3.2 `:376` (the 5.2/5.3 rows); §11 `:1638`. "architecture baselines" is defined at `:622`, and "free baselines" is used only for §6.7's `:69`, `:670` and `:1149`. Appendix C's "§4's table marks" (§4 has no table) now reads "Appendix D's table marks". |
| 11 | Every number in abstract and contributions appears in the body and is bound | **pass** after fixes | Every measured number is a `{{key}}`. Three gaps were fixed:<br>• the abstract's +0.470 appeared in the body only as +0.4697 (the body's +0.470 is a different statistic), so the abstract now prints `e7_step_r`;<br>• "1 of the 2 free baselines" now appears in §6.7 `:1149`;<br>• "one line fixes it" had no body support and is not literally true (the upstream loop slices actions in two places), so it now reads "shifting evaluation's action index by one step fixes it", supported in §7.2 `:1435`. |

## S10 item 2 — tables against prose (§5, §6–§7)

The two agents reported 34 mismatches: 13 for §5 and the front matter, 21 for §6–§7 and the captions. Each was re-checked against its artifact before any edit.
- **29 of the 34 reports were confirmed and fixed in `040f336`.** That is 27 distinct issues: two, the ensemble-5 table's iterations and Appendix D's "repairable", were reported by both agents. They include every item folded into the checklist rows above.
- **The other 5 are D1–D4 and D6 below**, because each needs more than a small fix or needs a decision.
- **None was a wrong number.** Every table cell the agents recomputed matched its artifact. The confirmed problems were quantifiers, scopes, pointers and captions.

**Fixed, beyond the checklist rows:**
- §5 said "the 400-step table is what the rule above was discharged over". M-23 was discharged on seed 1 (`results/task5_analysis.json` provenance); it now says the 400-step *unit* is what the rule was discharged on.
- The abstract and contribution 2 attached "under a rule committed in advance" to the three-seed magnitudes; it now qualifies the verdict.
- "the only horizon where a trained model loses to predicting no change": teacher forcing loses at every horizon, so it now says "the autoregressive arm".
- Appendix E printed M-16's Status line ("SETTLED — rule pre-registered") as its verdict, while the text cites what it returned. It now prints CANNOT BE SETTLED AT THIS BUDGET, through the generator's `RETURNED` map.
- Scopes that were stale since S9: "{{run_total}} runs in all" and "{{rt_hours}} h for the whole project" are now scoped to §5–§7; Figure 4's "every run at the released width" becomes "every run of §5–§7".
- §6.2's "tables, at n_independent = 4 in every cell": one of its three tables is at 20.
- "Two independent arenas" were not independent: the 16 in-sample trajectories are among the 20.
- "All figures in this paragraph are the held-out arena": the paragraph also quotes labelled n = 16 and n = 20 figures.
- A 0.98 width ratio was described as "widens".
- The M-45 MDE was credited to the dilution study rather than the bootstrap's standard error.
- Two dangling section pointers (§6.7 for the ensemble-5 CoV; §6.10 for the 3.49 capacity factor).
- §3.2's matched-capacity row pointed to §6.10; the result is in §11.
- The same statistic was printed with third-decimal-different intervals from separate bootstraps, undisclosed; this is now disclosed.
- §7.4's nine boundaries are now said to be "between the ten full episodes" (§7.1's ten includes the orphan row's).
- Captions: §6.7's tables now name the released checkpoint and all ten episodes; §6.10's name the held-out pair; §7.4 names the contamination design.
- Two items addressed to S10 in `OUT_OF_SCOPE.md`:
  - Appendix D and `original_paper_figures.py` cited the original's Fig. 4 (example trajectories) where Fig. 7 is meant;
  - Appendix C's "the cheapest of the four" was ambiguous.

## S10 item 3 — front matter

- **Numbers in the abstract and contributions:** see checklist 11; all pass after the fixes.
- **Title, abstract and conclusion:** the conclusion's first sentence stated the base claim without the one-step reversal and the horizon dependence that the abstract carries. It now says "reproduces at long horizons … though teacher forcing leads at one step". One disagreement remains, D1.
- **Captions (arena, n_independent, checkpoint):** fixed where the artifact records all three. D2–D4 remain, where it does not or where the fix is structural.

## Not fixed: larger than S10's size limit, or a decision (→ BLOCKED)

- **D1. "Right order" against "a weak ordering at best".** The title, the abstract and contribution 1 say the uncertainty "gets the order right". The conclusion (`:1668` and nearby) says it "should be read as a weak ordering at best", and reports that the aleatoric head ranks error inversely at h = 368. Reconciling them changes the title's or the conclusion's claim.
- **D2. §3.2's table has no checkpoint column.** It gives arena and n_independent per row, but its rows mix 10,000-iteration, 2,500-iteration and released-checkpoint results. Adding the column changes a generated table (`scripts/evidence_summary.py`) and the checks that read it.
- **D3. Figure 5 names neither arena nor n_independent.** "Why the coverage collapse is a horizon effect" (`scripts/build_paper.py:396`). Its artifact, `results/task2_sigma_profile.json`, records neither, so no bound caption can state them without re-running or annotating its producer.
- **D4. §6.3's loss-term gradient table names no checkpoint or arena.** The table sits around `:820`, and `results/e4_sigma_gradients.json` records neither.
- **D5. `tf_poor` is classed "no quantitative figure".** The original's Fig. 6 prints e for the whole N = 1 row, e.g. 3.99 at (32, 1) against 0.47 at (32, 8) (`ORIGINAL_SPECS.md` a.5). Reclassifying changes §4's count ("five of the six") and bears on §4's statement that our 4.61× "is the first figure attached to the claim". This has been open since S1.
- **D6. The old title in the package and a pushed zip.** `docs/SUBMISSION_PACKAGE.md:54` carries the old title (already in OUT_OF_SCOPE, owner the user). The tracked `supplementary_anon.zip` still holds the pre-S3 paper and needs rebuilding (`scripts/make_anon_bundle.py --zip`) before submission. Rebuilding it rewrites a committed, public file, so it is your call. The gitignored `supplementary.zip` is equally stale.
- **D7. Length.** See checklist 7: the body is 1.8% shorter than S0, not 30%. Reaching 30% means moving whole analyses to the supplement. This is reported, not forced, per PLAN.
