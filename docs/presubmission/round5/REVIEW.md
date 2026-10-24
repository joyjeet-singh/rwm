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

---

# G16R — independent re-review (2026-10-24; G16 itself was committed on 23 October, `98bbde8`)

Run at the user's request after G17 (`DECISIONS.md#G16R-ruling`) by a session that wrote none of G11–G17. Method: build;
main text re-extracted from the PDF to `round5/body.txt` (pages 1–12 up to "References"; G16's copy predated its own
fixes) and read once in full; `rwm-referee` ×1 on `body.txt`; `rwm-checker` ×2 (A–H, I–O), each given G16's unchecked
parts first; every gate's **printed output** read, not only its exit status; every finding verified by hand against its
artifact, the pinned upstream or the downloaded originals.

## Annex 6

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Gates, blocking | **PASS** | printed output read: `ledger_check` PASS; comparative claims 68/68 verified, 68/68 corruptions caught; typed numerals 0 not covered (paper and supplement); restatement 0; horizon sweep 0 findings; `xref_sweep` 0 suspect, 9 reviewed (all nine in supplement passages marked "section numbers in this passage are the earlier paper's"; checked); scope audit 0 unclassified; render check 5/5; round-5 gates pages 11.67/12, abstract 210/5, ids 0, once 0, sig 0, keys 0 missing; supplement self-test PASS; placeholders 20/20; `submission_check` 21/22 (C1 pending, as ruled). Two fast builds byte-identical at the end |
| 2 | Annex 1 | **PASS with fixes; one class open** | below |
| 3 | Rule 10 | **FAIL → fixed** | three summary sentences contradicted a reading (below); `CONSISTENCY.md` G16R rows |
| 4 | Scope | **PASS after fixes** | the abstract's Spearman figure now names its horizon; one n = 4 interval labelled descriptive; four appendix arena lines no longer assert the released checkpoint trained on the held-out pair |
| 5 | Locked framing | **PASS** | X3 in abstract and contribution 1 unchanged; X6 now summarised with its scope in contribution 4 (shorter units at the method's horizon); X7 "the released checkpoint, on its ten released episodes": App. L and App. M said "its training data" and "which trained on all ten episodes" (the wording G8's ruling retired), fixed |
| 6 | First page | **PASS** | abstract and §1 unchanged in substance |
| 7 | Tone | **PASS** | headings neutral; no priority claim |
| 8 | Anonymity | **PASS for the PDF** (`submission_check` A1: text hits none, `/Author` empty); the bundles must be rebuilt and swept by G17 step 4 |
| 9 | Praised items | **PASS** | K1 §3.1 + App. A; K2 §3.4; K3 §5.5; K4 §5.6; K5 §6 (code lines checked against the pinned upstream: `system_dynamics.py:125-126`, `envs/base.py:142,158,166`, `model_training.py:129,132,203`); K6 §3.4 + App. E |

## Annex 1 (rows G16R checked again; the others hold as G16 recorded them)

| RV | Result | Where |
|---|---|---|
| 06 | pass | "stood there as follows" 0 in the PDF |
| 08 | pass | body: one hit, "ran on two CPU cores" (§3.2), a compute statement, not queue or overlap detail |
| 09 | **fixed** | App. D row 6 cited the sample-efficiency table as v1 "§IV-E … Table I" under a v1 header; v1 has no such table (`version_crosswalk.json`; v1's text has no Limitations section). Now "from v2 on; not in v1" |
| 19 | **fixed** | §5.2's earlier X10 comparison at four trajectories, "1.8 [1.1, 2.7]", had no exact p (N7 computed none); now "(descriptive at four)" |
| 26 | pass | "too small by" occurs once, at its definition |
| 27 | **fixed** | App. F said "A value of 1.0 means no better than predicting the training mean", the error RV27 corrected in §3.3; and App. F defined no floor although §3.3 points there. Now App. F defines the three floors (keys from `n10_floors.json`) and its sentence agrees with §3.3 |
| 38, 29, 30 | pass | "first … aware", "freez", "provabl": 0 in the PDF |
| 39 | pass | "Table S8 in the first version" |

## Findings and dispositions

**Fixed, rule 10 (a summary stronger than, or contrary to, a reading).**
- Lesson 1 said step size "ranks nearly as well on whole trajectories"; under ranks disagreement is +0.910 and step size +0.598 there, margin +0.312 [+0.240, +0.396] (`n11_rank_correlations.json`). Now: ahead on shorter units and under ranks; the linear whole-trajectory margin unresolved.
- Contribution 4 named only the pre-registered linear test that could not resolve the step-size margin and left out X6, the pre-registered rule that did (+0.28 on 70 units at h = 100). Now both, with X6's scope.
- The conclusion said the baselines "never beat even the training mean"; at h = 1–32 every baseline beats it and at h = 100 two do (`pooled_nrmse_rescore.json` against `n10_floors.json`). Now "at h = 368".
- The abstract, §1, §7 and §8 say per-horizon rescaling restores one-sigma "not two-sigma" coverage at every horizon; the paper printed ±2σ at h = 100 only. N9's artifact holds all six horizons (83.5–86.3%, every interval below 95.45%), so the summary holds, and App. M now prints them as a table (post hoc, from keys; see `DECISIONS.md#G16R-figure3`).
- §5.6's last sentence did not follow from its readings ("the ensemble is needed" not supported, after two resolved margins in its favour); now states where "better than a free signal" holds and where not.

**Fixed, contradictions and wording (referee and own reading).** §5.7 "the shortfall at one step is not the finding" against the weight §1, §5.2 and §7 give it (now: a constant alone does not show the penalty mis-sized); §5.7 called the pooled figure "not a reading" and then "both readings"; §5.4 "most of what the members know would propagate" (now the log-gap share it measures); "overconfidence factor" in §5.3 undefined in the body (now ρ, §3.3); ρ named in §5.2; §4.3 "the smallest p the sample allows"; §5.2 per-model arenas; §4.1 "grows with depth" and the sign-flip p; §3.3's seasonal floor pointer; the first-rule lesson now points to App. G; abstract Spearman horizon ("at a hundred steps", 210/210 words, 5/5 numerals).

**Fixed, from the record.** §9 named "the PDF's page and text counts" among the 3 differing values; M3's three are the archive's `bytes`, `uncompressed` and `commits_in_log` (`verify_reproduction.json` `per_file`). The phrase is now the key `ver_diff_plain`, built from the record, which fails the build if a differing value has no plain name.

**Fixed, generators.** `e4_sigma_gradients.py` cited `system_dynamics.py:223` for the `kl` term (a bracket; the term is at :205) and :274-277 for `sequence` (:272-279); the artifact was regenerated and differs only in those `where` strings (every number identical). The LaTeX converter numbered "Reproducibility and data" and "References" as sections 9 and 10 while §1 says §8 states what reproduces; unnumbered headings stay unnumbered. App. H's baseline rows said "(§5.3)" (now §4.3); Figure 7's caption said "§5.2's sweep (Appendix J)" (now §4.2's, Appendix H); five App. F and H pointers said §3.1 for the metric definitions (now §3.3).

**Not changed, with reasons.** The abstract's "restores one-sigma coverage" carries no in-sample caveat: it is at 210/210 words, names the released checkpoint and the nine-episode fit, and §5.7 states the guarantee's limit. The run counts 28/75/81/342 in §5.5: each is defined where it appears (G16's disposition stands). Retraction counts, code lines in §5.1/§6, the bitwise tally: load-bearing (CLAUDE.md, K5, PLAN). "Spearman pooled over dependent steps": the lead over the step index is the reported comparison, resolved from h = 8.

**Open: BLOCKED (G16 item 3: more than three sentences).** About twenty sentences in Appendices D, H, I, J, K, L and M describe body content by the earlier paper's structure: the body sections they name hold no such table, column, figure or number. `PAPER.template.md` lines: 332 ("no cell survives multiplicity correction (§5.6)"); 636 and 651 ("§5.2's" rollouts, "§5.2's two held-out tables"); 649 ("§5.3's … paired contrasts"); 724, 750, 754 ("§5.2's released-checkpoint table", "§5.2's numbers", "the last column of §5.2's … table"); 737 ("The ensemble-5 arms (§5.2)", "(§5.6, 3 seeds"); 767 ("Our ensemble-5 arms (§5.6)"); 785 ("§5.2 quotes 34.4× … and the abstract and §8 use 33.4× at h = 100": neither does since RV14); 811 ("§5.6's P column"); 829 ("the trajectory permutation test of §5.6"); 995, 1000 ("§5.2's comparison", "§5.2's 'our arms fail the same way at 10.5×'"); 1114 ("§5.3's table"); 1191 ("§5.2's [+0.545, +0.694]"); 1265, 1293 ("what §5.6 reports", "§5.6's released-checkpoint table"); 1343 ("while σ does not (§5.6)"). Most need the sentence rewritten to point at the appendix's own table or removed, not a number changed; none is a measurement. The question is in `DECISIONS.md#G16R-blocked`.

**Coverage.** Checkers delivered after their turn limit (asked to report at it). A–H: parts 1–5 fully (App. H tables cell by cell, slopes, data budget, "4 of 8 neighbours", App. D), App. D, E, G, H; A–C against keys; **not reached:** the X8 tables against `x8_released_pairing.json` cell by cell; App. F (read by me instead). I–O: App. O's code lines, App. N's pipeline rows and captions, App. J, K, M's X7 table and `p4` MDEs, App. L's X6 and e7 values; **not reached:** App. I against `action_sensitivity.json`, `n5_stale_armA_ci.json`, `task_b2_epistemic.json`, `q1_pets_descendants.json`, the captions of I, K, L, M, App. M's multiplier ratios. `n13_adam.json`, `n9_recalibration_scores.json` and `e7_free_baselines.json` feed no I–O table (G16's list was wrong about that).

# G15-fix — the stale appendix pointers (2026-10-24; ruling A of `DECISIONS.md#G16R-blocked`)

**Item 1, G16R's list.** All 19 lines, 20 replacements (`fc8e2e9`). The abstract-and-§8 clause of App. I goes.
**Item 2, the full sweep.** Every one of the 203 `§n`/`§n.n` references in Apps A–O, their 49 appendix-letter
pointers and the named-section and supplement pointers checked against the body section, appendix or supplement
section named (body read from `body.txt`, which this session did not change). 60 more rewritten (`1b8c289`):
"keeps N sentences" and "in full" headers whose body sentences are gone (G, H); tables that §4.1, §4.2, §5.2, §5.3
and §5.6 no longer have; App. D's X3 cell (G → H) and its "the body's §4" (→ Table 4); App. B cited for run counts it
no longer gives (→ S7); "(Data and code)" (→ S8); App. G's "(Table I)" (→ Table 1, from v2 on, as RV09); App. N's
quotation of a §6 sentence §6 no longer has; ten self-pointers (→ above/below). Generator: the evidence table's
r_dd row now reads "(§5.6, Appendix L)", and its Holm pointer is App. H, not L. 157 references remain.
**Check.** `rwm-checker` ×1 on all 78 changed lines and both generator pointers: 0 mismatches; no number, key or
rule ID changed. One pointer it called thin, L "§5.6 states it that way" (the h = 1 ranking of whole rollouts): §5.6
says the h = 1 correlation is "across trajectories", which is that statement; kept.
**Not changed, logged** (`OUT_OF_SCOPE.md`, G15-fix): six appendix sentences that call all ten episodes the released
checkpoint's training data (scope, not pointer); "{{run_total}} runs for §4.1–§6" (a count's scope); metadata naming
§3.2 as pointing to App. D.
