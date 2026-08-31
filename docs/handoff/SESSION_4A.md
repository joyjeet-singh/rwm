# Session 4a — the body

**Ran** 2026-08-31. Branch `main`. Prose only; **the paper was not rebuilt** (exit criterion 5).

All six 4a exit criteria met. The front matter — title, abstract, contributions — is 4b, which
follows immediately and carries the first rebuild.

---

## §B — read, not inferred

`results/m64_short_units.json` contains **no permutation P-values, no per-dimension sign counts
and no Holm correction**. Session 3 computed three cells only: §6.2's calibration table, §6.7's
ranking statistics, and §5's A/B gap.

So §6.6 takes the addendum's **second branch**. The rewrite scopes the design claim by horizon
and says plainly that the test was not re-run at the shorter unit. The out-of-sample arena's
blindness is now stated as a property of the 400-step unit rather than of the arena: it is
demonstrably underpowered at h = 368, which needs the full 400 rows, and is no longer
demonstrably underpowered at h ≤ 128, where the same two episodes admit 60 units at h = 1 and 14
at h = 100. **Running the permutation family there is one pass over stored rollouts and we did
not do it.** That sentence is in the paper.

## §C — every row applied, each as a replacement

| row | edit | where |
|---|---|---|
| Figure 6 caption | "nominally ahead" → "ahead — a lead a shorter evaluation unit resolves as real, not nominal" | `build_paper.py:154` |
| §5 prose | the count claim now names its unit ("Over 400-step trajectories…") | §5 |
| §5 table | h=1 row untouched; the short-unit interval is prose beside it | §5 |
| §6.7 | original sentence kept, +0.148 companion added after it | §6.7 |
| §6.3 | "every seed's slope clears" → clears on all 3 M-50 was discharged over; 11 of 20 at twenty | §6.3 |
| §11 | "needs more episodes… not a better test" → scoped to h = 368 | §11 |
| §8 | lead-time sentence: all fifteen now carry one; Figure 4's set is not re-drawn, and why | §8 |
| contributions | **deferred to 4b** — it is front matter | — |

**Figure 6 keeps one series.** Only the caption changed.

## Brief tasks

- **4.1** — λ paragraph in §6.2, **leading with the measurement** per addendum §E: the best
  constant rescale needs 10.4 at h=1 and 43.2 at h=368, a factor of 4, fitted and scored on the
  same data so it is an upper bound on what any constant achieves. The horizon-dependence
  mechanism follows as the explanation, and §11's limit is restated in the same breath. A
  matching sentence is in §10. **The scoping guard held**: the statistic is cited, and nothing
  says M-65 returns anything about λ — its verdict stays the Gaussian-nominal one it was
  committed as.
- **4.2** — one sentence in §6.2: the h=1 row is measured on 10 of 10 episodes the checkpoint
  trained on, which biases toward better calibration, so 8.3× is flattering.
- **4.3** — one sentence in §6.1 stating the first author's permission to quote.
- **4.4** — one paragraph in §11: fifteen pre-registered rules, per-rule verdicts, no family-wide
  correction, and why pre-registration licenses that.
- **4.6** — M-62 and M-63 as one paragraph each in §6.2; M-64 in §5, §6.6 and §6.7; M-65 in §3.1
  and the λ paragraph; M-66 as a clause in Appendix B.
- **4.5** — deferred to 4b, per the addendum's ordering correction.

## §D — replace, do not append

**50 insertions, 14 deletions, net +36 source lines.** Every new sentence that supersedes an old
one deleted it in the same edit. The sharpest cases were the three the addendum named: §6.3's
"every seed's slope clears the threshold", §6.6's "cannot distinguish… at any horizon", and
§11's "needs more episodes… not a better test" — all replaced in place rather than corrected
after.

New material sits inside the §C allocation. No new subsections, no new appendix.

## Two results reported at full strength

Neither is softened, per §C:

- **§5's h=1 gap now excludes zero against our own arm.** It is in §5 as a finding, not a
  footnote: the gap is −0.0194 [−0.0310, −0.0093] at 60 units, so autoregressive training is
  *worse* at one step, not merely "not better". It goes into the contributions list in 4b.
- **The 20-seed corroboration returns MIXED**, framed as the vindication it is: `M-50` said
  before the runs that the recovering arm is seed-variable and that the experiment establishes
  the contrast rather than the magnitude. Twenty seeds show 11 of 20 clear the slope threshold
  where all 3 did. The contrast is intact — the MSE arm never tracks — so the abstract's claim,
  which concerns the MSE arm, does not move.

## Keys

Every new number is read from an artifact; none is typed. `paper_numbers.py` gained keys from
`m62_episode_clustering.json`, `m63_per_dimension_coverage.json`, `m64_short_units.json`,
`m64_free_gate.json`, `m65_gaussian_nominal.json`, `e5_synthetic_sigma.json`'s corroboration
block, `insample_framing.json` and `input_set_audit.json`.

**Verified without rebuilding**: every `{{placeholder}}` in the template resolves against a
generated `paper_numbers.json`, with one pre-existing exception, `{{FIGURES}}`, which is a build
directive rather than a value and was already there. `results/paper_numbers.json` was then
restored to its committed state, so this commit carries source and template only.

## Exit criteria

| # | criterion | status |
|---|---|---|
| 1 | Every §C row applied as a replacement | met (contributions row is 4b) |
| 2 | §6.6 written against what the artifact contains | met — second branch |
| 3 | Brief 4.1–4.4 and 4.6 complete; 4.5 deferred | met |
| 4 | New material within allocation; no new subsections | met — net +36 lines |
| 5 | Paper not yet rebuilt | met |
| 6 | `SESSION_4A.md` written | met |

## First action for 4b

Rewrite the title and abstract to lead with the epistemic term, three findings rather than
fifteen numbers, and fix the coverage-percentage-to-ratio unit switch. Update the contributions
list, **including the h=1 reversal** — the bullet at "a gap that spans zero at h=1" is the one to
replace.

Then the first rebuild. **`scripts/appendix_g_rules.py` must run before `paper_numbers.py`**, or
`{{appG_n_rules}}` stays at its stale 11 — the generator has not run since Session 1 added four
rules. Expect on rebuild:

1. `{{n_entries}}` → 244
2. `{{appG_n_rules}}` → 15, and Appendix G gains four rows
3. `e5_collapse_pct` → +0.08 (M-66; **does not self-heal**, and the body must say so)
