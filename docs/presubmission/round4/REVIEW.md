# Round 4, F10: fresh-eyes review

**How it ran.**
- **The main text, read in full, once:** `round4/body.txt`, extracted with `pypdf` (pdftotext is not installed here), pages 1–26 and page 27 up to "Data and code", 1,207 lines, read in chunks of about 300.
- **Two read-only Explore reviewers**, as workplan §2 allows: one for Appendices A–M (`PAPER.md` l. 1185–2078) and one for N–Z (l. 2079–2968). Each was given only its range and the artifacts its sentences cite. Each checked every table against every sentence citing it, and every table's arena, n and checkpoint, and returned mismatches only.
- **Verification:** every finding was checked against the paper and its artifact before anything changed. All 11 reviewer findings were real, and so were the main-text items marked fixed.
- **Fixes:** only items of three sentences or fewer were fixed, in commits `f2997f0` and `1e3753d`. Nothing larger was found, so F10 is not BLOCKED.

## Annex 6 checklist

| # | item | result | where |
|---|---|---|---|
| 1a | §7.2 gives our models' figures with interval and arena, and the Δ comparison; no "−0.99%" stands without its interval | **pass.** F8 moved the figures to Appendix V, which prints every model at every horizon with its interval (`n5_appV_table`). §7.2 states the post hoc result and the Δ comparison in words, with pointers. "−0.99%" appears nowhere: its key, `stale_armA_rel_h1`, was retired in F4 for N5's `n5_ho_h1` and its interval. C28.1 holds | PAPER.md l. 942–946; Appendix V |
| 1b | the model card matches A2 | **pass**, and fuller: it gives each arena's trajectory count, the artifact and X2's verdict | MODEL_CARD.md:256 |
| 1c | Appendix V states the threshold and the caveat | **pass.** A3's text, with M-84's thresholds, "The bar is deliberately low", and the one-policy caveat (C28.2) | Appendix V |
| 1d | every configuration summary uses A4's wording | **pass.** The abstract uses its 300-word form, "no reading favouring it"; contribution 3, §12, both of Appendix D's tables and the README carry the full form. C28.3 scans all of them | PAPER.md l. 20, 77, 1088; Appendix D; README |
| 1e | the difficulty measure is causal-only, and N6's entry exists | **pass.** D-39; `a2_trajectory_level_control.py` reads `per_episode_e["1"]` alone | FINDINGS_LEDGER.md:9528 |
| 2a | X3–X8 pre-registered before their data: commit order in git, script SHA-256 equal to the artifact's | **pass.** X5 was not run. For each of X3, X4, X6, X7 and X8: the SHA-256 is in its ledger entry and equals the artifact's; the script is unchanged since its PRE-REGISTER commit (`5f0acd4`, `df0f2fa`); the artifact was first committed after it; and it ran at a descendant | `/Users/Shared/rwm_verify/evidence/R4F10/prereg_check.txt` |
| 2b | each verdict verbatim, with arena, n and checkpoint | **pass.** X3: all ten episodes, 20, 2,500 iterations. X4: held-out pair, 4, 2,500. X6: 70 units of 132 rows, released, its training data. X7: all ten, 20, released. X8: held-out pair, 4, 2,500 and 10,000 (arena and checkpoints restored in F8's review) | §5 l. 388; §5.3; §6.6 l. 818; §6.7 l. 875; §7.2 l. 946 |
| 2c | the variants installed match the readings | **pass.** A5's REPLICATES variant for X3; A5c's PARTIAL for X4 | §5, §5.3 |
| 2d | every X5 sentence carries its caveats; NOT RUN stated once with its reason | **pass.** Appendix W states it once, with its reason. §11 now gives the reason beside its pointer (fix F4 below) | Appendix W; §11 |
| 3 | rule 11: `CONSISTENCY.md` covers every front-matter sentence, with every reading | **pass.** 71 rows covering 74 sentences and table rows, all agreeing; one row fixed (E18) | `round4/CONSISTENCY.md` |
| 4a | main text ≤ 16,000 words, or the shortfall reported | **shortfall reported.** 17,804 after F10's fixes (17,790 at F8). The user accepted the count on 16 Oct: `DECISIONS.md#F8-length`, option 1 | LENGTH_LOG.md |
| 4b | no R-/S-/D-/C-/B- ID or commit label in the main text | **pass.** 0. The main text has 51 labels: M- 26 and X-rule labels 25, against F0's 59 | `R4F8/move/id_count.py` |
| 4c | no result lost: the template's keys diffed against F0's, every removed key justified | **pass.** 8 F0 keys are gone, all retired in F4 and each replaced by a bound key that prints the same quantity or a finer one:<br>• `stale_armA_rel_h1`, `stale_armA_rel_h368`, `x2_E_stale_10k_ins_h1`, `x2_ci_stale_10k_ins_h1` → N5's `n5_*` keys, with intervals at every horizon (N5 asserts equality to X2's cells, so the values are identical);<br>• `x2_ctx_stale`, `x2_ctx_swap` → X2's per-arena `x2_ctx_{ins,ho,ten}_*`;<br>• `mn_fm_exception`, `mn_fm_n_unres_word` → A4's wording (G9/C28.3 forbid the old one).<br>Since F7: the 350 keys that left the main text are all in an appendix | f0_template_keys.txt; F8's check |
| 4d | `xref_sweep` reports 0 suspect pointers | **pass** (5 classes, 0 suspect). It cannot see "the table above" pointers, which the reviewers found (fixes A9, A12) | results/xref_sweep.json |
| 5a | abstract ≤ 300 words; C12.1 at 320 passes | **pass.** 300 words, 19 numerals | C12.1 |
| 5b | at most 8 bullets of at most 3 sentences | **pass.** 8 bullets of 3, 3, 3, 2, 3, 3, 3 and 2 sentences | §1 |
| 5c | title, abstract and conclusion agree | **pass.** "Right Order, Wrong Size"; the abstract's "gets the order right and the size wrong"; §12's "gets the order right and the size wrong", scoped to the scalar | l. 7, 23, 1098–1099 |
| 6 | every table and figure carries its arena, n_independent and checkpoint, including the new appendix sections | **pass after fixes.**<br>• **Main text:** every table and figure does, except Figure 1 (git timestamps) and Figure 4 (training curves), which have none to carry.<br>• **Appendices:** five titled sections F7–F8 moved there lacked one. Fixed: Appendix N's X6 and M-43 passages, T's constant scalar, R's M-49 and P's bootstrap unit | fixes A10–A15 |
| 7 | README, model card and cover statement no stronger than the paper, with no unbound number | **README: pass after fixes**: it now gives X3, X6's two scopes and X7, and its M-49 pointer is fixed. **Model card: pass.** **Cover statement: not stronger than the paper, but stale.** It says 23 rules and 62 pages (now 28 and 75), and its typed counts are the hand-written copies F11 refreshes (step 5: "rule count, page count, retraction counts"). It omits round 4's results; recommended for F11's package step, not a correctness defect | README.template.md; docs/COVER_STATEMENT.md |
| 8 | commit labels anonymous everywhere; the deny-list scan passes | **pass at F9** (`make_anon_bundle.py` at 9281201: probe and full hash detected, 566 files, 0 residual hits). `part_f_gate` check 2 (the PDF's text, raw bytes, metadata and figures) passes in this session's run. The submitted paper and bundle replace commit identifiers with stable labels (Data and code). F11 rebuilds and rescans both bundles | R4F9/h5_bundle.log |

## Findings, and what was done

**From the main-text read (step 1).**
- **F1. §6.2:** "On the released 5-member checkpoint over all 10 episodes, n_independent = 20 non-overlapping 400-step trajectories." has no verb. **Fixed:** "It is measured on …".
- **F2. §6.2, after F8's trim:** "Whatever compounding does at depth, it did not do that" lost its antecedent. **Fixed:** "… it did not produce that row".
- **F3. §3.1:** "Each metric is stated as implemented, with the `file:line` of its implementation" holds only for relative-L1; the coverage paragraphs never had one. **Fixed:** the clause is dropped. Appendix G holds the formulas.
- **F4. §11:** "rule X5, could not be run (Appendix W)" gave no reason. **Fixed:** "… because the released data do not record the velocity command its reward terms score against", which is Appendix W's reason. Nothing is inferred from velocity.
- **O1, recorded, not changed.** §6.2 and §9 give the released checkpoint's held-out-pair ratio, 25.7×, with no interval: `task_b2_epistemic.json` stores none, and computing one would be a new measurement. The comparison it supports stands, since the ensemble-5 arms' interval [9.0, 11.5] excludes it.
- **O2, accepted.** §1's opening ratios (1,827× to 20,669×; 8.3× to 34.4×) carry no interval. They summarise §6.2's table, where each has its interval; an introduction summary is not a reading.
- **O3, accepted.** The main text reads as one argument from the problem to the takeaways. On TMLR's clear-writing criterion: §1 says what was found and why it matters; §3–§3.2 state the setup and what each claim rests on; §9 gives the lessons; §11 states the limits once (O13). The heaviest passages for a first reader are §5.2's per-configuration list and §6.6's paired-test paragraph. Both are results the plan keeps in the main text.

**Reviewer, Appendices A–M (3 findings, all real).**
- **A1. Appendix L:** "The table above, at 10,000 iterations …" and "the three-seed table" point to §5's table, which F7's move left behind in §5. **Fixed:** "§5's by-horizon table", "§5's three-seed table".
- **A2. Appendix G, M-65's sentence**, moved from §3.1 in F7, so it had stood in the main text since round 2: "lands coverage at or above 68.27% in every one of 48 cells, with 0 below it". Two cells are below 68.27%, Arm A ens-5 epistemic on the held-out pair: 67.82% at h = 32 and 66.75% at h = 368. Both are inside the rule's band; the "0" counted cells below the heavy-tail bound. **Fixed:** the sentence states the bound (63.27%, a new key) and the two counts (15 in band, 33 above; new keys, asserted to sum to 48). **Ledger:** M-96 corrects M-65's discharge wording, which said the same. M-65 is not edited, and no verdict moves.
- **A3. Appendix E's M-65 verdict** printed GAUSSIAN NOMINAL ADEQUATE, the first branch its rule defines. Its discharge line "**It returns NOT HEAVY-TAILED, in / every one of 48 …**" wraps a line, which `appendix_g_rules.py`'s pattern could not cross. **Fixed:** the pattern reads across one line break. Stage 21a was regenerated; only M-65's verdict changed, to "NOT HEAVY-TAILED, in every one of 48 model x horizon cells".

**Reviewer, Appendices N–Z (8 findings, all real).**
- **A4. Appendix S:** "where a global multiplier manages 2 of them" read as X7's six horizons; it meant §6.7's 2 of 12 cells, and X7's constant multiplier manages 1 of 6. **Fixed:** the clause now sits with the 12 cells, and X7 is its own sentence.
- **A5. Appendix N:** "differs from the one above" (F8's move) pointed at nothing. **Fixed:** "differs from M-45's in §6.6, [+0.318, +0.576]".
- **A6. Appendix P:** "same bootstrap unit as the table above" (F8's move). **Fixed:** "the same bootstrap unit, whole trajectories, as Appendix O's table" (`design.bootstrap_unit` in both artifacts).
- **A7. Appendix N, X6's alongside readings:** began "and the margin …" with no arena or unit (an F8 slip). **Fixed:** names the released checkpoint's 70 units of 132 rows over all ten episodes, its training data, at h = 100.
- **A8–A9. Appendix N, M-43:** the moved passage and N's own M-43 section gave no iteration count. **Fixed:** "2,500 training iterations" in both, and "scored on the held-out pair" in the first.
- **A10. Appendix T, the constant scalar:** no arena, n or checkpoint. **Fixed:** "On the released checkpoint, each scalar fitted on one held-out episode's 2 trajectories and scored on the other's".
- **A11. Appendix R, M-49:** no arena, n or checkpoint. **Fixed:** "It scores them on the held-out pair's 4 400-step trajectories, every model at 2,500 training iterations."

**Also found and fixed in F10.**
- **B1. README.** Finding 1 lacked X3, finding 3 gave the step-size comparison without X6's short-unit scope (the locked framing requires both), and finding 4 lacked X7. Each gained one sentence. Finding 6's pointer "(rule M-49, §11)" now says §6.8.
- **B2. Appendix D's second table**, the matched-capacity row, said "(§11)". **Fixed:** "(§6.8)" (`evidence_summary.py`).

All fixes were rebuilt and checked by every gate: 68/68 claims, 68/68 corruptions, `xref_sweep` 0 suspect, the typed-numeral audit, 0 warnings.
