# Round 5 — outline, page budget and abstract (G8, 2026-10-19)

The plan the rewrite sessions (G9–G15) build to. Annexes 3 and 4 of `PLAN.md` were proposals; where this file
differs, it says why. Numbers appear only as key names (`results/paper_numbers.json`), so this file cannot disagree
with the artifacts. Nothing here anticipates X11's readings (GT2): every place they may land is marked **[X11 slot]**,
and GT2's addendum to `READINGS.md` decides what fills it.

Contents: §sections (the plan and budgets) · §homes (one home per result) · §figures · §appendices ·
§supplement-migration (G9's list) · §title · §abstract · §contributions · §rule-10 · §review-items · §Referee.

---

## §sections — sections, subsections and budgets

**The measure.** Y1: main content, title to the last line before References, at most 12 pages, read by
`round5_gates.py`'s `pages` gate. The plan below sums to **11.5 pages and about 5,560 body words**, leaving half a page
of margin for G14's budget pass. The density assumed is about 650 words a page of running text (TMLR's single column
with headings and equations), with figures at about 0.4 page and tables at about 0.3. Annex 3's "685 words a page,
floats included" is the current paper's average, which carries fewer floats per page than this plan; G14 calibrates
against the gate, not against this estimate.

| § | Title (neutral, Annex 1 RV43) | Pages | Words | Floats | Holds |
|---|---|---|---|---|---|
| — | Title, abstract | 0.4 | 210 | | §title, §abstract |
| 1 | Introduction | 1.4 | 680 | Figure 1 | the question and why it matters (180); the findings in plain words (300); four contributions (≤ 180); a one-line map |
| 2 | Background and related work | 0.9 | 500 | | RWM and RWM-U, and MOPO's penalty as a bound on one-step error at visited states (130); multi-step model training: DaD, scheduled sampling, Talvitie, Lambert et al., which set the prior for §4 (90); ensembles and shared torsos: deep ensembles, Osband et al. 2016 and 2018 (90); calibration, recalibration and conformal prediction: Kuleshov et al., Malik et al., Angelopoulos and Bates, Stankevičiūtė et al., Lindemann et al. (100); RL evaluation statistics: Henderson et al., Agarwal et al. (60); the PETS lineage of the bounded σ head in one sentence, pointing at App. J (30) |
| 3 | Setup | 1.6 | 760 | Table 1 | 3.1 the reimplementation and its gradient-level equivalence (120); 3.2 data, episodes, arenas and independent units, the checkpoint's provenance, and compute in one sentence pointing at App. B (200); 3.3 metrics and floors (200); 3.4 the statistical protocol, pre-registration with the NeurIPS 2020 and 2021 pre-registration workshops cited, and the deviations from the original setup and from the pre-registration, each pointing at App. O or E (240) |
| 4 | The base paper's claims | 1.8 | 780 | Table 2 | 4.1 training on rollouts against teacher forcing, led by X3 (500); 4.2 the configuration claim, one paragraph (110); 4.3 the architecture claim, "consistent but weak", with floors (170) |
| 5 | The follow-up's uncertainty | 3.7 | 1,700 | Figures 2–3, Table 3 | 5.1 what RWM-U claims and what its code computes (200); 5.2 at one step, the spread already falls short (280); 5.3 what an ensemble can see: the shared trunk (230); 5.4 does the spread accumulate? (300); 5.5 why the per-member variance collapses (250); 5.6 ranking error (230); 5.7 rescaling per horizon (210) |
| 6 | Defects in the released pipeline | 0.6 | 300 | | the stale action and its fix (130); unmarked episode boundaries (50); evaluation on training data (40); the variance state as Adam's per-step bound (40); the correspondence with the first author and the upstream report's status (40, Y10); the spliced windows' cost goes to App. N |
| 7 | Lessons and limitations | 0.8 | 420 | | lessons (220); limitations (200), including that the miscalibration's cost to RWM-U's policies is untested and why the one-step shortfall bears on it (MOPO's penalty bounds one-step error at visited states) |
| 8 | Conclusion; reproducibility; data and code | 0.3 | 210 | | conclusion (90); the reproducibility statement and data and code, at most 120 together (G11 item 5) |
| | **Total** | **11.5** | **≈ 5,560** | 3 figures, 3 tables | |

**Where this differs from Annex 3, and why.**
- **§5 follows G13's order, not Annex 3's.** The review asks §5 to lead with the residual one-step miscalibration,
  so 5.2 is that gap, 5.3 the epistemic-versus-total gap (what a shared-trunk ensemble can see), 5.4 the
  one-step-versus-accumulated gap (X9), and only then the mechanism (5.5), ranking (5.6) and the remedy (5.7).
- **§5 is 0.1 page shorter, and §4 and §1 lose 0.1 each**, to buy the half-page margin. 5.2's table carries the
  numbers that would otherwise be prose.
- **No broader-impact statement.** TMLR asks for one only where there is a significant risk of harm; a
  measurement of a dynamics model's calibration carries none. §10's text moves whole to the supplement (G9 item 10).
  The decision is the user's to overturn (§decisions below).
- **The pre-registration paragraph sits in §3.4**, not in a section of its own (Annex 4's §8 row). It is one
  paragraph: rules committed before the data, the verdicts that went against the original or could not settle it,
  the {{n_superseded}} superseded entries kept, and App. E.

## §homes — one home per result

Each result is stated once, in its home, with its scope sentence (arena, n_independent, models). Every other place
cross-references it ("§4.1") and may restate its direction in words, never its numbers (the `once` gate).
"Precision" is the display form: `s2` is `{{key|s2}}`; "as stored" means integers, words and labels. Exact p-values
print at `s2`, except the attainable minimum at n = 4 (0.125, which `s2` would print as 0.13): G12 adds a key
`n7_p_min_n4_frac` = "1/8" through `paper_numbers.py`, read from `results/n7_exact_tests.json`.

| # | Result | Home | Scope sentence | Keys (precision) | Summarised in |
|---|---|---|---|---|---|
| H1 | The rebuild matches the release at the gradient level | 3.1 | the released module and ours, before any training | `diff_grad_max`, `diff_terms`, `diff_n_params` (as stored) | abstract; contribution 1; App. A |
| H2 | Rollout training beats teacher forcing out of sample (X3) | 4.1, Figure 1a | our Arm A and Arm B models, {{iters_main}} iterations, five folds holding each of the ten episodes out once, {{x3_n}} trajectories, three seeds per arm per fold; the reading at the pre-registered h = {{v2_diag_h}}; the episode-level test is a two-sided sign-flip test over the ten held-out episodes, which treats them as exchangeable although the models of different folds share most of their training episodes (§Referee 2) | `x3_gap`, `x3_ci`, `x3_ratio_h368` (s2); `x3_eps_pos` of `x3_n_eps`, `x3_n_folds_word` (as stored); `n7_x3_ep_p_h368` (s1); `x3_fold_lo`–`x3_fold_hi` (s2) | abstract; §1 findings; contribution 1; §8 |
| H3 | …and loses at one step | 4.1 | the same folds, {{x3_h1_n}} non-overlapping {{x3_h1_unit}}-row units; at the episode level the h = 1 sign agrees on `n7_x3_ep_k_h1` of 10 episodes (`n7_x3_ep_p_h1`), so the reversal is a short-window result | `x3_h1_gap`, `x3_h1_ci` (s2); M-64's pre-registered reading (`m64_h1_gap`, `m64_h1_ci`, `m64_h1_n`) in App. G only | abstract; contribution 1 |
| H4 | The 10,000-iteration factor, as support | 4.1, one sentence | the held-out pair, {{a1_nind}} trajectories from two episodes, {{d1_seeds}} seeds, {{iters_long}} iterations | `d1_ratio` (s2), its exact p from N7 (s2), the two-episode caveat | none (App. G holds the curve) |
| H5 | The configuration claim (Y6) | 4.2 | the held-out pair, {{iters_main}} iterations, one factor at a time | `mn_better_kinds`, `mn_n_better_word`, `mn_n_configs_word` (as stored); no decimals | §7 limitations (budget dependence, in words) |
| H6 | The architecture claim, a weak test (Y6) | 4.3, Table 2 | the held-out pair, {{iters_main}} iterations, our reading of the baselines, RWM's settings untuned | Table 2: `h2h_*_nrmse_h368` (s2) beside the floors `n10_hold_nrmse_heldout_h368`, `n10_mean_nrmse_heldout_h368` and seasonal-naive (s2), each with its N7 p; size-matched transformer as a parameter-count test only (locked framing); RSSM in one clause | contribution 1 (one clause) |
| H7 | At one step, no ensemble's spread accounts for its error (N14) | 5.2, Table 3 | each ensemble's own arena and n: released checkpoint on its ten episodes ({{e7_nind}}); ensemble-5 arms on the held-out pair (4); the independent ensemble on the held-out pair (4) **[X11 slot: fold ensembles, n = 20]** | `n14_R_rel`, `n14_R_e5`, `n14_R_ind` with `_ci` (s2) | abstract; contribution 2; §7 |
| H8 | "Too small by" at one step and at depth (Y7) | 5.2 (h = 1), 5.4 (h = 100, 368), Table 3 | as H7 | `n8_k_rel_epi_h1`, `n8_k_rel_epi_h100`, `n8_k_e5_epi_h1`, `n8_k_e5_epi_h100` (s2); ρ beside its calibrated `m65_calib_ratio` (s2), never called "too small by" | §1 findings (in words) |
| H9 | In-sample against held-out, by horizon (X10) | 5.2 | ensemble-5 arms, {{x10_n_in}} in-sample against {{x10_n_out}} held-out trajectories; `x10_caveat` verbatim in meaning | `x10_q_h1`, `x10_q_h1_ci` (s2) at h = 1, and "the reverse at h = 100" in words with `x10_q_h100` (s2) | none: no summary may say in-sample flatters or worsens without the horizon (READINGS) |
| H10 | Which rows trained the released checkpoint is not recorded (N12) | 3.2 | the release's two repositories and the checkpoint file | `n12_ckpt_has_data_stats`, `n12_ckpt_iter` (as stored); `n12_rel_l1_h1_released_on_train`, `_on_heldout`, `n12_rel_l1_h1_armA_in`, `_out` (s2) | every scope sentence about the released checkpoint says "its ten released episodes", not "trained on" (§decisions, item 2) |
| H11 | The shared trunk, and independent members (M-44, M-68, M-49) | 5.3 | the held-out pair, 4 trajectories; independent members differ in capacity and data order too, so this bounds the sharing effect | `v1_shared_pct` (s2); `m44_ratio_gain`, `m44_mde_ratio`, `r2_indep_ratio_h100` (s2) **[X11 slot: n = 20 on the folds]** | contribution 2 |
| H12 | The spread does not accumulate under the released rollout; per-member rollout narrows the gap (X9) | 5.4, Figure 1b | released checkpoint on its ten episodes (20) and the fold ensembles (20), with paired intervals; ensemble-5 and independent on the held-out pair (4), descriptive with exact p; `x9_scope` every time | `x9_rel_f_h100`, `x9_rel_f_h100_ci`, `x9_fold_f_h100`, `x9_fold_f_h100_ci` (s2); `x9_rel_mean_cov1_h100` → `x9_rel_per_cov1_h100` (s2) against `x9_band_lo`–`x9_band_hi`; `x9_e5_f_h100`, `x9_ind_f_h100` with `x9_e5_p_h100` (s2); CRPS (s2) | abstract; §1; contribution 2; §7 lessons |
| H13 | The per-member variance collapses: the objective's optimum is σ = 0 | 5.5, Figure 2 | every run that logs σ; the synthetic test on known noise | `d1n_alea_ratio_h1` (as stored, an integer-scale ratio); `e5s_verdict` → plain words; `n13_rate_over_lr_median`, `n13_bound_over_lr` (s2); `n13_iters_worst`, `n13_iters_typical` (as stored) | abstract; contribution 3; §6 (the variance state, by cross-reference) |
| H14 | The PETS survey counts | App. J; 5.5 one clause | 13 repositories inspected | `q1_n_looked`, `q1_n_carry`, `q1_n_inherit` (as stored) | none |
| H15 | Disagreement ranks error; the free signals | 5.6 | the released checkpoint on its ten episodes ({{e7_nind}}), whole trajectories and X6's {{x6_n_units}} shorter units | `n11_d2_sp_epi_h1`, `n11_d2_sp_epi_h100` (s2); `n11_e7_sp_step_margin`, `_ci` (s2); the Pearson verdict named as pre-registered, in words; `x6_margin`, `x6_ci` (s2) | abstract; contribution 4; §7 lessons |
| H16 | Per-horizon rescaling: scale, not shape (X7, N8, N9) | 5.7, App. M (Figure 3 dropped, G16R) | released checkpoint, leave-one-episode-out over its ten episodes, {{x7_n_traj}} trajectories; in-sample use only **[X11 slot: held-out folds]** | X7's within-band count in words; `n9_epi_perh_cov2_h100`, `_ci` (s2) against `v3_cov_nominal2`; `n9_epi_before_crps_h100` → `n9_epi_perh_crps_h100` (s2); `n8_n_heavy` of `n8_n_cells` (as stored); Arm A's own multipliers `d3x_own_epi_ok` of `d3x_own_epi_cells` | abstract; contribution 4; §7 lessons |
| H17 | The stale action in the released evaluation | 6 | released checkpoint, all ten episodes ({{ad20_nind}}), and the held-out pair ({{ad_nind}}) | `adh20_rel_h1`, `adh20_rel_ci_h1` (s2); `ad_rel`, `ad_rel_ci` (s2) | abstract ("two defects"); contribution 4 |
| H18 | Data budget | 3.2 | the released dataset against the reference's | `c2_pct` (s2) | §7 limitations |
| H19 | The pre-registration record and the retractions | 3.4 | every rule, App. E | `n_superseded`, `n_retractions_lower` (as stored) | none |
| H20 | X5, not run | App. D row | | | §7 limitations (in words) |
| H21 | X8, our verdicts under the released timing | App. E | | | none |

## §figures

**Figure 1 (§1; new, G10).** Two panels, one finding about each original.
- **(a) The base paper's claim, out of sample.** Teacher forcing's relative-L1 minus rollout training's at
  h = {{v2_diag_h}}, one interval per fold (five folds, each holding out two episodes, each episode out once), with
  each held-out episode's value as a point; zero marked. Source: `results/x3_cross_fold.json` (`per_trajectory`,
  `reading`). Caption: our models, {{iters_main}} iterations, {{x3_n}} trajectories, and the episode-level exact p.
- **(b) Whether the spread accumulates.** The error-to-spread ratio ρ by horizon, log scale, with the calibrated
  value `m65_calib_ratio` drawn as a line: the released checkpoint under the released rollout (ensemble mean fed
  back) and under per-member rollout; the fold ensembles under both. n = 20 models only; the n = 4 ensembles are in
  Table 3 and App. I. Source: `results/x9_per_member_propagation.json` (`tables`). Caption: arena and n per curve,
  and "per-member rollout is not the released method".

**Figure 2 (§5.5; the old Figure 4 recast, G10 item 1).** σ itself: the bounds `exp(min_logstd)` and
`exp(min_logstd + Δ)` per logged iteration with measured σ at the saved checkpoints, beside the per-iteration change of
log Δ over the learning rate, so the Adam signature and the sign flip under the corrected objective both show.
Source: `results/n13_adam.json`.

**Figure 3 (§5.7): dropped by G16R** (`DECISIONS.md#G16R-figure3`); its ±1σ content is Appendix M's X7 table and its ±2σ content Appendix M's ±2σ table. As planned: ±1σ and ±2σ coverage by horizon on the released checkpoint, before rescaling, under the one
constant and under the per-horizon multipliers, with both nominal lines. Source: `results/n9_recalibration_scores.json`
(`scores`) and `results/x7_loeo_recalibration.json`.

**Tables.** Table 1 (§3.2): each tested claim × arena × n_independent × models × the rule's plain name × verdict in plain words ×
home section (the claim-to-verdict summary a reproducibility reviewer looks for, §Referee 13) (replaces §3.2 "what each claim rests on" and the evidence table's body role; the full evidence table stays in
App. D). Table 2 (§4.3): h = {{v2_diag_h}} nRMSE for RWM and each baseline, both training modes, beside the three
floors, with exact p. Table 3 (§5.2): one row per ensemble (released; ensemble-5; independent; **[X11 slot]** folds):
arena, n, one-step R with interval, k at h = 1 and h = {{v2_deploy_h}}, per-member ±1σ coverage at h = {{v2_deploy_h}}.
A cell an artifact does not hold reads "not measured", never a computed stand-in.

**Moved to appendices** (renumbered in `build_paper.py`'s map, G10 item 2): `paper_fig4_prereg_timeline` → App. E;
`paper_fig6_ab_by_horizon` → App. G; `paper_fig1_calibration` → App. I; `paper_fig3_collapse` → replaced by
Figure 2, the old panel kept in App. J; `paper_fig2_sigma_profile` → App. J; `paper_fig5_three_way` → App. L.

## §appendices

Annex 4's letters, with two changes: App. C absorbs the old App. K's permutation tests (its per-dimension tables go
to App. I), and the old App. H's "Measurements" rows go to the supplement rather than to an appendix, because each is a
finding the body does not use. Target **about 12,000 words** (round 4: about 27,000). Each opens with what it holds
and which main-text claim it supports (G15 item 1). Appendix tables keep full precision.

| App. | Title | Words | From |
|---|---|---|---|
| A | Reimplementation and equivalence | 250 | A |
| B | Data, arenas and compute | 500 | B (its runtime paragraphs go to the supplement, G9 item 7) |
| C | Statistical methods | 700 | new: cluster bootstrap over trajectories, exact sign-flip tests (N7) and why n = 4 cannot go below p = 0.125, dimension-preserving permutation nulls (from K), Holm, the resampling-unit correction (old §8) |
| D | Claims of the originals and the version crosswalk | 1,000 | D; W's row; `version_crosswalk.json`'s changed claims |
| E | The pre-registration record | 1,300 | E (plain names → IDs, commits, lead times, verbatim verdicts), the old Figure 1, Z (X8) |
| F | Metrics and floors | 600 | G; N10; nRMSE's definition corrected; Y7's two quantities |
| G | Rollout training against teacher forcing in detail | 1,100 | L; per-fold table; M-64; the old Figure 2 |
| H | Configuration and architecture claims in detail | 900 | L's baseline rows, U, M-75/76, X4, X1 |
| I | Calibration in detail | 1,100 | M; K's per-dimension tables; X9, X10, N14 tables; **[X11 slot]** |
| J | Why the per-member σ collapses | 1,100 | J, F, N13, I's PETS paragraphs and the survey counts |
| K | The shared trunk and independent ensembles | 700 | O, P, M-49 |
| L | Ranking against free signals | 900 | N, X, N11 (Spearman and Kendall) |
| M | Per-horizon recalibration | 800 | T, Y (X7), N8, N9, the split-conformal framing, M-65's withdrawal |
| N | Defects in the released pipeline | 700 | V (X2), Q, §7's detail |
| O | Paper-code differences | 400 | H's paper-code rows; C-09 as corrected (C-17); the bootstrap difference (C-18); Table S8 |
| | **Total** | **12,050** | |

## §supplement-migration — G9's list, in order

Each item is cut from `PAPER.template.md` and pasted verbatim, keys and all, under the heading given in
`docs/SUPPLEMENT.template.md` (or, for drafting history, into `docs/BUILD_CHECKS.template.md`'s "Moved from the paper
body" list). An anchor is a heading or the exact bold lead of a paragraph; a span runs from its first anchor to the
line before the next anchor named, or to the end of the appendix. Line numbers are as of this commit and are only a
guide; the anchor text governs. "Stays" is what G9 leaves, at most one pointer sentence.

| # | Span (exact anchor) | ≈ line | To (supplement heading) | Stays |
|---|---|---|---|---|
| 1 | `## Appendix C — what testing the untested claims would require` (whole) | 1177 | S1 What testing the untested claims would require | nothing; App. D's pointer is G15's |
| 2 | `## Appendix R — the limitations in full (§11)` (whole) | 2287 | S2 The limitations in full | nothing |
| 3 | `## Appendix S — the conclusion's discussion of the ranking, the scale, the per-dimension evidence, and what should travel (§12)` (whole) | 2378 | S3 What should travel, and the conclusion's discussion | nothing |
| 4 | App. I from `**Related work in full (§2).**` to the line before `**Where the parameterisation comes from.**` | 1437 | S4 Related work in full | the heading and the two PETS paragraphs (G15 moves them into App. J) |
| 5 | App. H from `**§6.1 in full: the penalised quantity and the discarded term, from the first author.**` to the end of App. H | 1415 | S5 The penalised quantity and the discarded term, from the first author | nothing |
| 6 | App. H's table rows under `***Measurements***` (the header row through the last row before the paragraph of item 5) | 1405 | S6 Measurements the paper does not use, with their evidence | the rows under `***Paper-versus-code gaps***` and `***Pipeline defects***` (G15: to App. O and App. N) |
| 7 | App. B from `**Runtime.**` to the end of App. B | 1154 | S7 Compute: runtimes, the queues and their overlaps | the reproduce commands and the `--force` sentence |
| 8 | Data and code: `**The repository's history was rewritten once, and §8 depends on that history, so we say what changed.**` paragraph | 1085 | S8 The repository's history | nothing |
| 9 | Data and code: `**On anonymity.**` paragraph | 1112 | S9 Anonymity | nothing |
| 10 | `## 10. Broader impact` (whole) | 988 | S10 Broader impact | nothing (no statement in the paper; §sections) |
| 11 | §8: `**Reproducibility, and a build that checks its own prose.**` paragraph | 950 | S11 Reproducibility accounting and the build's own checks | nothing (G11 writes the ≤ 120-word statement) |
| 12 | App. W, the text after its heading | 2548 | S12 Why X5 could not be run | the heading (G15 turns it into App. D's row) |
| 13 | Drafting-history framings only, the sentences that say what a body section "keeps" or that passages "stood there as follows": the paragraphs led `**What §6.3 and §6.4 keep, and what is here.**` (1548), `**What §6.5 keeps, and what is here.**` (1669), `**What §6.2 keeps, and what is here.**` (1891), `**What §6.6 keeps, and what is here.**` (1944), `**What §6.7 keeps, and what is here.**` (2408), `**What §7.2 keeps, and what is here.**` (2483); the lead sentences `**§6.8's table for rule M-44.**` (2071) and `**§6.8's table for rule M-68.**` (2154); and the "stood there as follows" sentences at 1312, 1741 and 1788 | — | BUILD_CHECKS "Moved from the paper body" | **the content those sentences introduce stays**: it is current evidence, and G15 rewrites each appendix's opener |

Not on G9's list, because the rewrite sessions move them with their own text: §1's ledger mechanics (G11), §2's full
version beyond 540 words (G11, after item 4), §11 and §12's paragraphs (G14), §8's other paragraphs (G11 to §3.4, G15
to App. C and E). After G9 the `keys` gate must read 0 missing, as PLAN G9 item 2 requires.

## §title

**Recommendation (Y9):** *Right Ranking, Wrong Scale: Reproducing the Robotic World Model's Dynamics Model and
Testing the Uncertainty of Its Follow-up*

Why: it drops "Verified" (RV37), which a reader can take as verifying the method's results; "dynamics model" says what
was reproduced, since no policy is trained; and "of its follow-up" puts the uncertainty where it belongs, since the base
paper reports none (the current title and Y9's candidate both say "the uncertainty it reports"). **"Ranking" and
"scale" replace "order" and "size"** on the referee's point that "order" reads as "order of magnitude", the opposite of
what is meant (§Referee 4). The phrase holds on this round's readings: rank correlation is high at every horizon
(`n11_d2_sp_epi_h*`), and the spread falls short at every horizon including one step (`n14_R_*`, `n8_k_*`).
Alternative, keeping the phrase the paper has carried since round 1: *Right Order, Wrong Size: …* with the same
subtitle.

## §abstract

Draft, in keys, revised after §Referee. Measured with `round5_gates.gate_abstract` after substitution: **210 words
(the limit; G11 may trim), 5 numerals** (`n11_d2_sp_epi_h100`, `v2_deploy_h`, `x9_rel_mean_cov1_h100`,
`v3_cov_nominal1`, `x9_rel_per_cov1_h100`); no capitalised verdict label. The `ids` gate flags the name "RWM-U" as a
label (a false positive, logged in `OUT_OF_SCOPE.md`). X3's exact p left the abstract for §4.1, where its
independence assumption can be stated (§Referee 2); "at the original's training length" replaces the iteration count
(RWM v1 Table S9 and RWM-U v1 Table S8 both give {{iters_main}}; PREMISES P13, P15).

> We reimplement the dynamics model of the Robotic World Model (RWM) and test the uncertainty its follow-up, RWM-U,
> uses as a reward penalty in offline policy optimisation. Our rebuild matches the release's gradients. RWM's claim
> that training on its own rollouts, not one-step targets, lowers long-horizon error holds on held-out data: holding
> each of ten episodes out once, at the original's training length, it wins on every one at the pre-registered
> horizon; on short windows at one step it loses. RWM-U's ensemble disagreement ranks errors right but sizes them
> wrong: it ranks them better than the forecast step does (Spearman {{n11_d2_sp_epi_h100|s2}} at {{v2_deploy_h}}
> steps), yet in every ensemble measured, error exceeds what the spread implies even at one step. The release feeds
> every member the ensemble mean, so spread does not track accumulated error: on the released checkpoint at that
> horizon one-sigma coverage is {{x9_rel_mean_cov1_h100|s2}}% against {{v3_cov_nominal1|s2}}%, and rolling each member
> on its own predictions raises it to {{x9_rel_per_cov1_h100|s2}}%. Each member's variance collapses: the implemented
> loss, squared error on a sampled prediction, is minimised at zero. Rescaling the released checkpoint's spread per
> horizon (fitted on nine episodes, scored on the tenth) restores one-sigma coverage, not two-sigma. We fix two
> pipeline defects. One robot, gait and dataset; no policy is trained.

## §contributions

At most four bullets, at most 45 words each (45, 45, 43, 45 rendered), no priority claim. Revised after §Referee: the
defects joined bullet 1, bullet 3 says why the optimum is zero, and bullet 4 labels the rank analysis exploratory.

1. **RWM's claims, tested.** Holding each of the ten episodes out once, rollout training beats teacher forcing at
   {{v2_diag_h}} steps on every episode and loses at one step on short windows (§4.1). The other two claims get weak
   tests (§4.2–4.3); two pipeline defects get fixes (§6).
2. **Three gaps between RWM-U's spread and its error.** Even at one step every ensemble's error exceeds its spread;
   members sharing one trunk can disagree only about what that trunk carries; feeding them the ensemble mean stops
   the spread accumulating, which per-member rollout partly repairs (§5.2–5.4).
3. **Why the discarded per-member variance collapses.** The implemented loss is squared error on a sampled
   prediction, not the Gaussian likelihood, so its optimum is σ = 0: derived, shown against known synthetic noise,
   and approached at an ordinary Adam step per iteration (§5.5).
4. **What the spread is still good for.** It ranks error better than the forecast step (Spearman). Exploratory ranks
   also put it ahead of the model's step size, which the pre-registered linear test could not resolve (§5.6).
   Per-horizon rescaling fixes one-sigma coverage, not the tails (§5.7).

## §rule-10 — summary sites and the readings each must agree with

Rule 10: a summary may claim a direction only if every reading for that result agrees; where readings split, it says
so. Sites: the abstract, the contributions, §1's findings paragraph, §7's lessons and limitations, §8. G14 audits
each against this table, and GT2 re-checks every row marked **[X11]**.

| Summary claim | Readings it must agree with | Status now |
|---|---|---|
| Rollout training beats teacher forcing at the longest horizon on every episode | X3: `x3_eps_pos` of `x3_n_eps` at h = {{v2_diag_h}}; N7's episode-level k at h ≥ 32 is 10 of 10, at h = 8 `n7_x3_ep_k_h8` of 10; the held-out pair at {{iters_long}} | agrees at h = {{v2_diag_h}}; a summary must not say "at every horizon above one step" (h = 8 is 8 of 10) |
| …and loses at one step | `x3_h1_gap` `x3_h1_ci`; M-64 `m64_h1_gap` `m64_h1_ci`; N7's episode-level `n7_x3_ep_k_h1` of 10 (`n7_x3_ep_p_h1`) | the two short-window readings are below zero; the episode-level reading is unresolved, so every summary says "on short windows" |
| Disagreement ranks error well | Spearman `n11_d2_sp_epi_h*` at every horizon; Pearson `d2_epi_h*`; X6 | agrees on direction; "better than step size" splits (Pearson unresolved on whole trajectories, ranks resolved, X6 resolved on short units), so contribution 4 says so |
| No ensemble's spread accounts for its error, even at one step | `n14_R_rel`, `n14_R_e5`, `n14_R_ind` (`n14_R_ind3`), every interval above 1 | agrees **[X11: fold ensembles]** |
| Per-member rollout raises the released checkpoint's coverage (abstract) and partly repairs the gap in every ensemble (contribution 2) | `x9_*_f_h100` for rel, fold, e5, ind, each above one half; verdicts all "narrows" | agrees at h = 100; the n = 4 readings are descriptive (exact p `x9_e5_p_h100`), and the summary must not call them resolved |
| …though none reaches nominal coverage | per-member ±1σ coverage against X7's band: rel and fold below it; the independent ensemble's pooled `x9_ind_per_cov1_h100` is inside the band but its four trajectories are not all inside, so the rule's "closes" fails | agrees with the rule's verdicts; G13 must say the pooled independent figure reaches the band |
| The per-member variance collapses; the objective's optimum is zero | the derivation; M-50 `e5s_verdict`; every logged run (`n13_n_runs`) | agrees; the pathway caveat (the fed-back sample is a second path) goes in §5.5 |
| Per-horizon rescaling restores ±1σ but not ±2σ, on the released checkpoint | X7 within band at every horizon; N9 ±2σ below `v3_cov_nominal2` at all six horizons | agrees for the released checkpoint; **on Arm A's held-out episodes its own multipliers manage only `d3x_own_epi_ok` of `d3x_own_epi_cells`**, so no summary may drop "on the released checkpoint" **[X11c]** |
| In-sample measurement flatters / worsens calibration | X10: worse at h = 1, the reverse at h = 100 and 368 | splits by horizon: summaries either name the horizon or omit it (READINGS) |
| Two pipeline defects with fixes | stale action (all ten episodes raises error up to h = 32, not resolved from h = 100; held-out pair raises it at every horizon); unmarked boundaries | the abstract claims existence and fixes only, not a direction of cost |

**Locked framing (rule 11), checked.** X3's outcome is in the abstract and in contribution 1 at the headline's
prominence. X4 appears only as a parameter-count test (H6). X5 is "not run" (H20). X6 is the {{x6_n_units}}-unit
h = {{v2_deploy_h}} result (H15). X7 is pooled epistemic coverage on the released checkpoint over its ten episodes
(H16; see §decisions item 2 on the words "trained on"). X8 stays in App. E. N5 and N6 stay post hoc.

## §review-items — how each review item lands

| RV | Lands in | Session |
|---|---|---|
| 01 | §sections (11.5 pages planned); G14's budget pass | G8 → G14 |
| 02 | §abstract (204 words, 4 numerals) | G8 → G11 |
| 03 | no IDs in the body: rules by plain name, verdicts in plain words; App. E maps names to IDs | G9–G15 |
| 04 | §homes; the `once` gate | G11–G15 |
| 05 | §homes' precision column; the `sig` gate | G11–G14 |
| 06 | §supplement-migration item 13; G15's openers | G9, G15 |
| 07 | §figures, Figure 1 | G10 |
| 08 | §supplement-migration items 7–11 | G9, G14 |
| 09 | App. D with the crosswalk; 5.1 quotes the current text where it changed | G11, G13, G15 |
| 10 | done in G7 (references 1 and 2) | — |
| 11 | 5.1 quotes RWM-U v1 §4.1's "captures aleatoric uncertainty effectively" (unchanged in v3); 5.5 tests it | G13 |
| 12 | 5.3 credits the shared trunk to the original; App. O's bootstrap row | G13, G15 |
| 13 | App. O: C-09 as corrected | G15 |
| 14 | §5's order (5.2 lead, then 5.3, 5.4) | G13 |
| 15 | H12, Figure 1b | G10, G13 |
| 16 | H9, with the horizon | G13 |
| 17 | H10 in 3.2; scope sentences | G11, G13 |
| 18 | §4.1 leads with X3 (H2) | G12 |
| 19 | exact p beside every n = 4 interval (§homes) | G12, G13, G15 |
| 20 | **[X11 slots]**; X9(d) already at n = 20 | GT2, G13 |
| 21 | H5, one paragraph | G12 |
| 22 | H6, Table 2 with floors | G12 |
| 23 | "inconclusive" in the body; verbatim labels in App. E | G12, G13 |
| 24 | H16, App. M | G13, G15 |
| 25 | H13, Figure 2; §6's variance-state sentence | G10, G13, G14 |
| 26 | H8: k only | G11, G13 |
| 27 | 3.3, App. F, Table 2's floors | G11, G12, G15 |
| 28 | 3.3's rationale (Y8); H15 | G11, G13 |
| 29 | 5.5: "no gradient from the bound term" | G13 |
| 30 | §abstract, 5.5: "the objective's optimum is σ = 0" | G11, G13 |
| 31 | H14 | G13, G15 |
| 32–36 | §2's plan; the references from G7 | G11 (G12 for 32 in §4.1) |
| 37 | §title | G11 |
| 38 | no priority claim (§contributions) | G11 |
| 39 | App. O | G15 |
| 40 | §6 (Y10) | G14 |
| 41 | §8's statement; supplement S11 | G9, G11 |
| 42 | H12, H16: CRPS and NLL beside coverage | G13 |
| 43 | the neutral titles in §sections; headings such as "The structural excuse does not survive" and "…evaluation is the broken one" go | G11–G14 |
| 44, 45 | outside the paper | G17 |
| 46 | the citations in 3.4 (Cameron et al.), 5.5 (Kingma and Ba), 5.1 (Chua et al., Yu et al.) | G11–G13 |
| K1 | 3.1, App. A | G11, G15 |
| K2 | 3.4 | G11 |
| K3 | 5.5 | G13 |
| K4 | 5.6 | G13 |
| K5 | §6 | G14 |
| K6 | 3.4, App. E | G11, G15 |

## §decisions — what the approval at `DECISIONS.md#G8-outline` covers

1. The plan: 11.5 pages, §5 in G13's order, no broader-impact statement, the appendix letters above.
2. **The released checkpoint's scope words.** Rule 11 locks X7 as coverage "on a checkpoint that trained on all ten
   episodes". N12 (R-86) found nothing in the release that records which rows trained it. The outline therefore
   writes "the released checkpoint, on its ten released episodes", and 3.2 states N12's sentence once. The finding is
   unchanged; only the words "trained on" go.
3. The title (§title: "Right Ranking, Wrong Scale", or the alternative keeping "Right Order, Wrong Size") and the abstract
   (§abstract).
4. G9's migration list (§supplement-migration), in particular item 13: the "stood there as follows" framings go to
   BUILD_CHECKS while the evidence they introduce stays in the appendices.

## §Referee

One `rwm-referee` read, given only a rendered copy of the first-draft title, abstract, contributions and section table
(values substituted, internal notes removed), and asked what a TMLR reviewer would find unclear, unsupported or
missing. Its points, condensed, with what was done. "Accepted" means the drafts above already carry the change.

| # | Point | Answer |
|---|---|---|
| 1 | Readers cannot tell whether the rescaling was fitted on the windows it is scored on; say how it differs from split conformal | **Accepted.** The abstract now says "fitted on nine episodes, scored on the tenth" (X7's leave-one-episode-out) and keeps "the released checkpoint". 5.7 frames it as split conformal (G13 item 7), including that the guarantee needs exchangeable episodes and that X7's episodes are all ones released with the checkpoint |
| 2 | "exact p = 0.002" is a sign test over ten episodes whose models share training data; name the test and endpoint, give seeds, say whether the one-step loss holds per episode | **Accepted, and it found a real scope problem.** The p left the abstract; H2's scope sentence names the two-sided sign-flip test, the exchangeability assumption, three seeds per arm per fold and the pre-registered h = {{v2_diag_h}} (M-86). **At one step the episode-level sign agrees on only `n7_x3_ep_k_h1` of 10 (`n7_x3_ep_p_h1`)**: the reversal holds on short windows only, so the abstract and contribution 1 now say "on short windows", and the rule-10 row records the split |
| 3 | "RWM's central claim holds" reads as the policy claim, which is untested | **Accepted.** The abstract names the claim tested: training on its own rollouts lowers long-horizon error |
| 4 | "Order" reads as "order of magnitude" | **Accepted as the recommendation**: "Right Ranking, Wrong Scale"; the old phrase stays as the alternative for the user (§decisions 3) |
| 5 | "No ensemble" / "every ensemble": which ensembles? | **Partly.** The abstract says "every ensemble measured"; there is no room for the list. §1's findings paragraph must name them (the released checkpoint, the three ensemble-5 arms, the independent ensemble, and the fold ensembles where measured), and 5.2's Table 3 has one row each |
| 6 | "Accounts for its error" and "most of that gap" name no quantity | **Accepted.** The abstract now gives the released checkpoint's one-sigma coverage before and after per-member rollout against nominal, at {{v2_deploy_h}} steps; "accounts for" became "error exceeds what the spread implies" (N14's statistic, defined in 3.3) |
| 7 | What does Spearman rank? Ranking by horizon would be trivial; the step-size clause is unparseable | **Answered from the artifact.** From h = 8 the correlation is over (trajectory, step) pairs, and its lead over the forecast-step index has an interval above zero (`results/n11_rank_correlations.json`, `U1_d2_forecast_index`, `sp_diff`), so it is not a horizon effect. The abstract now says "better than the forecast step does". Contribution 4 now says the step-size comparison is resolved only by the exploratory rank analysis, and the pre-registered linear test could not resolve it |
| 8 | Why is the optimum zero, when Gaussian NLL's is the residual variance? | **Accepted.** The abstract and contribution 3 say the implemented loss is squared error on a sampled prediction, not the likelihood. "Adam's step bound" became "an ordinary Adam step" |
| 9 | Two defects in the abstract, five items in §6 | **Partly.** §6 holds two defects with fixes (the stale action, the unmarked boundaries) and observations that are not fixable defects (evaluation on training data; the variance state). The spliced windows' 20 words go to App. N. The variance state stays in §6 as PLAN G14 item 1 specifies, as one sentence that cites 5.5 |
| 10 | Gloss jargon; give the equivalence tolerance; compare the iteration count with the original's; name the robot | **Partly.** "Not one-step targets" glosses teacher forcing; "at the original's training length" replaces the iteration count; "reward penalty in offline policy optimisation" replaces "subtracts from the reward". The tolerance (exact) and the robot's name do not fit in 210 words; 3.1 and §1 give them |
| 11 | Contributions overlap and bundle | **Accepted.** The defects moved into bullet 1; bullet 2 is the three gaps; bullet 4 is what the spread is still good for |
| 12 | 5,555 words plus six floats look like more than 11.5 pages | **Answered with the measurement.** G0 measured 17,804 body words in 26.9 pages with the current figures and body tables: 662 words a page, floats included. At that rate the plan is 8.4 pages; adding all six floats on top, as if the current paper had none, gives about 10.5. The 40 words on the pre-registration workshops moved to 3.4 anyway. G14 calibrates against the `pages` gate |
| 13 | Missing: a claim-to-verdict table, a deviations list, compute, author contact, a per-episode figure, the policy-cost limitation | **Accepted, except one already planned.** Table 1 gains a verdict column; 3.4 names the deviations from the original setup and from the pre-registration (App. O and E); 3.2 has compute in one sentence (App. B); §6 gives the correspondence and the upstream report 40 words (Y10); §7 states that the cost to RWM-U's policies is untested and why the one-step shortfall bears on MOPO's penalty. Figure 1a is already the per-episode figure; the referee was not shown the figure plan |
