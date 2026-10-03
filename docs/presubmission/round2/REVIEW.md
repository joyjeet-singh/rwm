# Round 2, T10 — fresh-eyes review against Annex 4

Reviewed at `ff7b845`. Lines are `PAPER.template.md` lines after T10's fixes unless another file is named.

Each item is given a status:
- **PASS**: it held as found.
- **FIXED**: it failed as found and was fixed in T10. Every fix is three sentences or fewer (PLAN T10 item 4).
- **PASS (as ruled)**: it follows a user ruling that superseded the anchor's wording.

The two read-only Explore agents' findings are listed after the checklist. Each was verified before acting.

## 1. Alignment

| check | status | where |
|---|---|---|
| The abstract has one alignment clause with no numbers | PASS | 21 |
| §3.2's alignment row reads "defect confirmed in the code; its cost in error is small and not consistent in sign" | PASS (as ruled) | `scripts/evidence_summary.py` row 12. Ruling A (`round2/DECISIONS.md#T3-alignment-framing`) replaced the anchor wording with "defect confirmed in the code; its cost is concentrated at short horizons, and at h = 368 is small and not consistent in sign" |
| No sentence pairs "overstat…" with a figure without the reversal | PASS | 1163 (§7.2's 7.9% / 6.6%) has the all-ten-episodes reversal three lines below. §3.2's claim cell carries no figure. The other "overstat" uses are unrelated |
| §7.2 has no "reported before" sentence and carries N1's horizon and sensitivity sentences | PASS | 1173-1177. The withdrawn sentence is in `docs/BUILD_CHECKS.template.md:430-432` |

## 2. Configuration

| check | status | where |
|---|---|---|
| "trade-off" and "accuracy alone" wherever the verdict is stated (abstract, contributions, §3.2 claim text, Appendix D) | FIXED | Abstract 11-12 and contribution 3 69-74 passed. §3.2's row lacked "accuracy alone" (T9, `evidence_summary.py`). Appendix D lacked it too (T9) |
| The centre's cost cell is filled | PASS | §5.2 table, the centre row's "1.00" |
| The equal-compute paragraph is labelled post hoc | PASS | 538 |
| Tail slopes are in Limits | PASS | 555-558 |

## 3. Architecture

| check | status | where |
|---|---|---|
| Every statement of the verdict mentions RWM's settings and that the baselines are worse than no change at h = 368 | FIXED | The abstract (10), contribution 3 (67-69), §5.3 (593-598), §12 and Appendix D passed. §3.2's two architecture rows had neither; they now carry both, with the floor fact asserted in `evidence_summary.py` |
| The h = 100 reading is bound | PASS | 603-604 (`bl_ar_*_h100`) |
| The RSSM paragraph states X1's reading verbatim | PASS | 620 (`rssm_partc_sentence`): NOT RESCUED BY THE SETTINGS TRIED |
| "Retraining variants are running" does not survive | PASS | absent from the paper; the T9 assertion stops the build if it would return |

## 4. M-23

| check | status | where |
|---|---|---|
| Every place that ties `d1_ratio` to the rule says seed 1 and the three-seed extension (abstract, contribution 2, §5, Figure 2 caption, §11) | FIXED | Contribution 2 (65), §5 (381, 401-403, 426), Figure 2's caption (`build_paper.py`) and §11 (1290) passed. The abstract said "one seed per arm" and now says "seed {{m23_seed}} of each arm", word-neutrally (370 words). §5.1 now says "over 3 seeds (the rule ran on seed 1)" |
| The table row is labelled "the rule's horizon" | PASS | 420 |

## 5. Teacher forcing

| check | status | where |
|---|---|---|
| §5 has E5's sentence next to the first 4.61× | PASS | 403 |

## 6. nRMSE

| check | status | where |
|---|---|---|
| §5.2 and §5.3 cite pooled readings | PASS | 519 ("here and in §5.3"); 588 |
| The head-to-head baseline nRMSE cells are filled | PASS | Appendix L table, every baseline cell filled |
| N2's ledger entry exists | PASS | `FINDINGS_LEDGER.md` `R-77` |

## 7. Small points

| check | status | where |
|---|---|---|
| Verdicts are verbatim in their returned case | FIXED | M-16 was fixed in T9. M-45 printed SUPPORTED, from the artifact's boolean; it now prints DISAGREEMENT CARRIES WITHIN-ROLLOUT INFORMATION (`paper_numbers.py`). M-49 printed UNDER-POWERED; it now prints the full string in §6.8, §11 and Appendix R. A mechanical search of every upper-case verdict string found no other case changes |
| Released-checkpoint rows on the held-out pair are labelled "held-out pair" | FIXED | §6.2 said "the held-out arena". §6.5's table and its σ-growth table said "out-of-sample". Appendix L's arena line said "out-of-sample held-out pair" without "in-sample for the released checkpoint" |
| Figure 1's caption carries the in-sample caveat | PASS | `paper_fig1_calibration` (the plan's Figure 1 by filename; rendered Figure 3) says so. Rendered Figure 1, the pre-registration timeline, has no arena |
| † flags are defined and captioned | PASS | §5.3 (the † definition below its table); Appendix L's arena paragraph |
| Retraction counts follow ruling U1 and are identical in the introduction and §8 | PASS | 50 and 1209: seven claims withdrawn on evidence, six framings withdrawn |

## 8. Appendix H

| check | status | where |
|---|---|---|
| Appendix H exists; COVERAGE.md accounts for all 102 entries; every absent entry is in Appendix H or listed with a reason | PASS | 1663; `round2/COVERAGE.md` has 105 rows (the 102, plus R-76 to R-78), and its 6 left-out entries each have a reason |

## 9. Length

| check | status | where |
|---|---|---|
| Body ≤ 19,000 words, or the shortfall reported | PASS (shortfall reported) | 20,771 after T10. Reported under U3 in T7, T9 and T10 |
| No result lost: the template's `{{keys}}` diffed against T0's, every removed key justified | PASS | 4 keys left the template after `6bee218`: `ad_pa_n`, `ad_pa_out_row`, `stale_pct`, `stale_pct_rel`. All 4 went in T3's `e1e8e0a`, which moved §7.2's withdrawn-figures sentence (S-20) to BUILD_CHECKS' moved-from-body list (`docs/BUILD_CHECKS.template.md:430-432`), where they still render. Justified in the T10 log |
| §9 is intact | PASS | 1226-; six lessons. Wording fixed in T9 |
| `xref_sweep` finds 0 suspect pointers | PASS | build gate |

## 10. Front matter

| check | status | where |
|---|---|---|
| Every number in the abstract and contributions appears in the body, bound | PASS | T9 (`round2/t9_frontmatter.py`; `part_f_gate` check 6 PASS, rerun after T10's abstract edit) |
| The title, abstract and conclusion agree | PASS | T9 audit lens 1 (e) |
| The abstract passes C12.1 | PASS | 370 words (max 370), 23 numerals (max 26) |
| ≤ 8 bullets of ≤ 3 sentences | PASS | 8 bullets, each of 2-3 sentences |

## 11. Captions

| check | status | where |
|---|---|---|
| Every table and figure caption carries its arena, n_independent and checkpoint | FIXED | Of 28 tables, 6 are not measurements on an arena: Appendix A, B, C and E, and J's synthetic and loss-term tables. Six measurement tables lacked an explicit arena or n: the §6.6 r_dd and free-baseline tables, the §6.8 combined-arm table, and the tables in Appendices N, O and P. Captions with gaps: Figure 2 (no n), Figure 3 (no n, no checkpoint), Figure 6 (none, and panel (b) is a different family). All fixed |

## 12. Public-facing text

| check | status | where |
|---|---|---|
| README and model card carry no unscoped multiplier claim | FIXED | `README.template.md` said the per-horizon multiplier "restores nominal coverage on every cell". It now says "brings every cell within 10 points of nominal, though at two episodes no single cell is resolvable" and gives the global multiplier's 2 as "of the 12 epistemic ones". The model card gains the same resolvability clause |
| No unmeasured "materially worse" sentence | PASS | Fixed in T8 (`build_model_card.py`); README's only "materially" is in a source comment |

## The agents' findings

Agent 1 covered §5 and the front matter; agent 2 covered §6, §7 and Appendices H-T. Both read `ff7b845`. Their raw returns are in the session evidence (`R2T10/t10_agents_raw.txt`). Every finding below was verified against the artifact named before acting, and every one was real.

| id | finding | verified | fix |
|---|---|---|---|
| A1-M1 (agent: large) | §5 said teacher forcing is worse than no prediction "at every horizon we measured", and that h = 1 is "the only horizon where the autoregressive arm loses". Both hold only on the 400-step unit. On M-64's short units, with the same arms, checkpoint and episodes, the floor is worse than both arms at h = 1, and teacher forcing beats it at h = 1, 8, 32 and 100 | yes: `m64_short_units.json`; same `weights_10000.pt` (`m64_short_units.py:312`) | three sentences scoped to the 400-step unit, with the short unit's readings bound (`m64_floor_h1`, `m64_A_h1`, `m64_B_h1`, `m64_B_beats_floor_at`). Small, so not BLOCKED. h = 368, where §5's headline floor comparison sits, is not on the short unit |
| A1-M2 | "the four per-trajectory gaps behind it" pointed at seed 1's interval | yes | "behind the three-seed table" |
| A1-M3 | "All 4 of 4 are positive, which is the sign test" (the sign test is over 10 episodes) | yes | "the direction of the sign test's 10 of 10 episodes" |
| A1-M4 | Holm "over the family of 8"; the artifact ran Holm over 4 | yes: `task_c3_multiplicity.json` n = 4 | Bonferroni at 0.05/8 over the 8; Holm over the 4 long-horizon cells |
| A1-M5 | §3.2 row 1, 10,000 iterations, says it survives a correction computed at 500 and 2,500 | yes | the cell now names those checkpoints |
| A1-M6 | Figure 2's caption gave no n_independent | yes | added |
| A1-M7 | "640,000 window draws a run makes" sits beside 10,000-iteration results | yes: 2,500 × 256 | "a 2,500-iteration run" |
| B-M1 | M-45 printed SUPPORTED; the rule returns DISAGREEMENT CARRIES WITHIN-ROLLOUT INFORMATION | yes: ledger M-45 and the artifact | key value is now the artifact's verdict, asserted against its boolean; Appendix E follows |
| B-M2 | M-49's verdict was truncated | yes | full string in §6.8, §11 and Appendix R |
| B-M3 | Figure 4 and §6.3: the 28 runs are "every run of §5-§7 at the released width", but §5.2's 24 sweep runs are also at that width | yes | "outside §5.2's sweep (Appendix J)", the convention Appendix J already uses |
| B-M4 | Figure 3's caption gave no n_independent or iteration count | yes | added |
| B-M5 | Figure 6's panel (b) is §5's A/B gap (`review_bootstrap_unit.json`), not the contamination cells; neither panel had an arena, n or checkpoint | yes: `paper_figures.py` | caption names both families with their arenas, n and checkpoints (bound) |
| B-M6 | §6.2 set our arms' held-out 10.5× against the checkpoint's all-ten-episodes 33.4× as "like with like" | yes: the same-arena figure is 25.7× (`task_b2_epistemic.json`) | uses 25.7× on the same held-out pair, with 33.4× over all ten |
| B-M7 | §6.5 and Appendix K called the released checkpoint's epistemic P values "out of sample" | yes | "on the held-out pair … both in-sample for the checkpoint"; the table headers became "held-out pair" and "training episodes" |
| B-M8 | §6.5's "directionally consistent across every model and horizon" contradicts its own table and Appendix S | yes | names the arms whose ordering points the right way and the two that do not, as Appendix S does |
| B-M9 | §6.7's "different model" column pools both scored models under a released-checkpoint heading | yes: `task_d3_cross_model.json` counts 72 = both directions | header: "fitted on the other model, both models scored" |
| B-M10 | Appendix J: "two of 3 seeds recover a σ spread of only 1.02×" (they are 3.67, 1.14, 1.02) | yes | "its 3 seeds recover σ spreads of only 1.02–3.67×" (bound range) |
| B-M11 | Appendix O: 49.8 h "for all of §5-§7's runs" | yes: Appendix B times 33; 42 more are counted apart | "for the 33 runs of §5-§7 it times" |
| B-M12 | Appendix M: all four uninformative cells have n = 2; one has a single episode per direction and no interval | yes: `m62_episode_clustering.json` | names that cell |

Noted by agent 1 and left: `a1_ab_by_horizon.json`'s `trend.reading` text still says h = 8 is not established. That is an artifact note the paper does not print, and the paper matches the table. Recorded in OUT_OF_SCOPE.
