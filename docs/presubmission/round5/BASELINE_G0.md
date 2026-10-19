# G0 baseline (round 5)

Measured from the files committed at `796a026` (round 4's frozen paper; the paper, templates, scripts and `results/`
are unchanged since: `git diff 796a026 HEAD` touches only round-4 records). Built with FILE_MAP §3's fast build,
which reproduced `PAPER.md`, `PAPER.tex`, `MODEL_CARD.md`, `README.md` and `docs/BUILD_CHECKS.md` with no diff
against the committed files; only `PAPER.pdf` changed (dates), and was restored with `git restore PAPER.pdf`.
The measuring script was a scratch file outside the repository (`PAPER.md`, `PAPER.pdf`, `paper_numbers.json`
read-only); definitions are given with each line so a later session can re-measure the same way.

## Build and gates (all run once, at this baseline)

| Step | Result |
|---|---|
| fast build (`paper_numbers`, `build_paper`, `build_model_card`, `build_readme`, `compile_paper`) | pass; PDF check: 0 errors, 0 overfull/underfull boxes, 0 LaTeX warnings |
| `ledger_check.py` | PASS |
| `check_comparative_claims.py --self-test` | pass, 68/68 corruptions caught |
| `typed_numeral_audit.py`, `restatement_index.py`, `horizon_sweep.py`, `xref_sweep.py`, `check_scope_audit.py`, `pdf_render_check.py` | all exit 0 |

(Two things not to repeat: in zsh an unquoted `$g` holding "script --flag" is not word-split, which gave one false
exit 2 for the self-test; the re-run passed. `pdftotext`/`pdfinfo` are not installed; page figures use `pypdf`.)

## Pages

```
total pages 75
References page 27 y 152.42299999999994 height 792.0
```

- Total pages: 75. References starts on page 27, at about 88% of that page's text block (heading baseline y = 152 pt;
  text block runs from y = 74 to 700 pt on every page). **Main-content pages, title to the last line before
  References: about 26.9** (26 full pages plus 0.88). PLAN §2 calls it "26"; this is the same count to one decimal.
  The plan's 12-page target (Y1) therefore needs a cut of about 14.9 pages.

## Words

Body = Introduction to the line before "Data and code", by `docs/presubmission/round2/t6_words.py` (counts
whitespace-separated tokens of `PAPER.md`): **17,804** (matches PLAN's G0 figure). Per section and per appendix:

```
body (Introduction to Data and code): 17,804
     303  (tables     0)  ## Abstract
   1,337  (tables     0)  ## 1. Introduction
     821  (tables     0)  ## 2. Related work
     519  (tables     0)  ## 3. Setup
     578  (tables     0)  ### 3.1 Metrics
     106  (tables     0)  ### 3.2 What each claim rests on
     352  (tables     0)  ## 4. What the original papers claim, and which claims we test
   1,606  (tables   198)  ## 5. The base paper's central claim reproduces
      92  (tables     0)  ### 5.1 The data budget, which is the one part of the sample-efficiency claim we can measu
   1,173  (tables   184)  ### 5.2 The configuration claim: history and forecast horizons
   1,146  (tables   209)  ### 5.3 The architecture claim: MLP, RSSM and transformer baselines
      56  (tables     0)  ## 6. Neither of the checkpoint's uncertainty outputs is usable as an interval
     392  (tables     0)  ### 6.1 Which quantity the method actually uses
   1,218  (tables    77)  ### 6.2 The measurement
     689  (tables     0)  ### 6.3 Why the aleatoric head collapses: the optimum is σ = 0
     468  (tables     0)  ### 6.4 Why the epistemic term may be miscalibrated: the members are not independent model
     478  (tables     0)  ### 6.5 The failure is one of magnitude; the ordering is weaker than it looks
   1,431  (tables   197)  ### 6.6 Ensemble disagreement beats the trivial baseline
   1,059  (tables     0)  ### 6.7 One constant scalar does not fix it; a per-horizon one lands within the band, thou
     515  (tables     0)  ### 6.8 Testing the mechanism: an ensemble that shares nothing, alone and with the correct
   1,049  (tables     0)  ## 7. Defects in the released pipeline
     479  (tables     0)  ## 8. Method
     816  (tables     0)  ## 9. Actionable lessons
     207  (tables     0)  ## 10. Broader impact
     647  (tables     0)  ## 11. Limitations
     570  (tables     0)  ## 12. Conclusion
     485  (tables     0)  ## Data and code
     649  (tables     0)  ## References
     111  (tables    90)  ## Appendix A — verification chain
     760  (tables   273)  ## Appendix B — reproducing
     648  (tables   305)  ## Appendix C — what testing the untested claims would require
   2,452  (tables 2,171)  ## Appendix D — every claim of the originals, and what we did with it
   1,556  (tables 1,093)  ## Appendix E — every pre-registered rule, its lead time and its verdict
     258  (tables     0)  ## Appendix F — the variance-state arithmetic behind §7.5
     740  (tables     0)  ## Appendix G — the metrics' formulas, the two nRMSE aggregations, and the comparison one 
   1,252  (tables   964)  ## Appendix H — findings not in the main text
   1,335  (tables     0)  ## Appendix I — related work in full, the PETS lineage of the bounded σ head, and how ofte
   1,768  (tables   386)  ## Appendix J — the σ = 0 optimum: the synthetic-noise test (rule M-50), the term-by-term 
   1,553  (tables   139)  ## Appendix K — section 6.5's two tables, and the per-dimension permutation tests behind t
   2,737  (tables   400)  ## Appendix L — section 5 in detail: the floor, seeds and short horizon, the data budget, 
   1,286  (tables   370)  ## Appendix M — section 6.2 in detail: every horizon, the held-out-pair version, the ensem
   2,064  (tables   263)  ## Appendix N — section 6.6 in detail and its robustness checks: r_dd per horizon, the fre
     945  (tables   182)  ## Appendix O — rule M-44 in full: an ensemble that shares nothing
   1,278  (tables   212)  ## Appendix P — rule M-68 in full: both fixes on the same models
     314  (tables     0)  ## Appendix Q — what the spliced windows cost: the contaminated arm and the duplication co
   2,152  (tables     0)  ## Appendix R — the limitations in full (§11)
     927  (tables     0)  ## Appendix S — the conclusion's discussion of the ranking, the scale, the per-dimension e
   1,106  (tables   105)  ## Appendix T — section 6.7 in detail: the constant scalar, the per-horizon table, and whe
     958  (tables   348)  ## Appendix U — the settings sweep at equal training compute
   2,993  (tables 1,899)  ## Appendix V — rule X2, and section 7.2's figures for our models: whether they respond to
     171  (tables     0)  ## Appendix W — rule X5, which could not be run: the penalty against the model's error in 
     340  (tables    74)  ## Appendix X — rule X6: disagreement against predicted step size on shorter units
     531  (tables   204)  ## Appendix Y — rule X7: the per-horizon recalibration, fitted on nine episodes and scored
   2,225  (tables 1,656)  ## Appendix Z — rule X8: our rules' verdicts under the released evaluation's timing
```

## Abstract, as C12.1 counts it

(C12.1 `abstract-budget`: the text between `## Abstract` and `## 1.`, `---` lines removed, `arXiv:` identifiers and
`§n` references dropped before counting numerals.)

- abstract words 300 numerals 19
- Against Y2's target (at most 210 words, at most 5 numerals): over by 90 words and 14 numerals.

## Main text (title to before References): labels and precision

Counted over `PAPER.md` up to its `## References` heading. Patterns are in the scratch script; they are
approximate (they can over-count a stray token such as "X1" used as a variable) and are a baseline for G6's gates, not
the gates themselves.

    ledger/rule IDs:
      M-: 26 occurrences, 18 distinct
      S-: 0 occurrences, 0 distinct
      X: 25 occurrences, 8 distinct
      C: 0 occurrences, 0 distinct
      N: 0 occurrences, 0 distinct
      W: 0 occurrences, 0 distinct
      E-: 0 occurrences, 0 distinct
      H-: 0 occurrences, 0 distinct
      T: 0 occurrences, 0 distinct
      D-: 0 occurrences, 0 distinct
      F: 0 occurrences, 0 distinct
      R: 0 occurrences, 0 distinct
    commit labels (7+ hex): 0 ;  [Xn]-style tags: 0
    capitalised verdict labels: 8 {'PARTIAL': 7, 'SUPPORTED': 1}
    decimals with >2 sig figs: 514
    interval-valued keys in main text, top 20: [('x6_ci', 5), ('a2_rdd_ci', 3), ('ad20_rel_ci', 2), ('ad_rel_ci', 2), ('adh20_rel_ci_h1', 2), ('adh20_rel_ci_h100', 2), ('adh20_rel_ci_h32', 2), ('d2_epi_ci_h1', 2), ('d2p_ci_h100', 2), ('d2p_ci_h128', 2), ('d4_ci', 2), ('m64_h1_ci', 2), ('x3_ci', 2), ('a1_gap_ci_h1', 1), ('a1_gap_ci_h100', 1), ('a1_gap_ci_h128', 1), ('a1_gap_ci_h32', 1), ('a1_gap_ci_h368', 1), ('a1_gap_ci_h8', 1), ('ad20_nrmse_ci', 1)] (of 59 )

"Interval-valued key" = a key in `results/paper_numbers.json` whose value contains a bracketed or ± interval; 59 such
keys are used in the main text, and the 20 most repeated are listed above with their counts in `PAPER.template.md`
before References. Every one appears at most 5 times.

## Figures (file → number in the paper, from `build_paper.py`'s `INTEXT`)

| File | Figure |
|---|---|
| `figures/paper_fig4_prereg_timeline.png` | 1 |
| `figures/paper_fig6_ab_by_horizon.png` | 2 |
| `figures/paper_fig1_calibration.png` | 3 |
| `figures/paper_fig3_collapse.png` | 4 |
| `figures/paper_fig2_sigma_profile.png` | 5 |
| `figures/paper_fig5_three_way.png` | 6 |

## Base key set

`round5/base_keys.txt`: 1,489 distinct `{{key}}` names printed by `PAPER.template.md` (1,432),
`docs/BUILD_CHECKS.template.md` (73) and `docs/APPENDIX_G_VARIANCE_ARITHMETIC.template.md` (5), unioned; the layout
marker `{{FIGURES}}` is excluded because it is not a value. All 1,489 exist in `results/paper_numbers.json`. Keys
that reach the paper only inside a whole-table substitution (`{{evidence_table}}`, `{{appG_table}}`) are not in the
list. There is no `docs/SUPPLEMENT.template.md` yet (G6 creates it). `README.template.md` is outside `docs/` and so
outside PLAN's definition of the set.
