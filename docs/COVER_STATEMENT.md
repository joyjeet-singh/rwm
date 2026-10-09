# Cover statement — TMLR submission

*Draft. Every figure is substituted from a named artifact by the paper's own build; the
numbers below are quoted from `results/paper_numbers.json` and are current at 57 pages, the
length of the compiled submission.*

---

## Which acceptance criterion this submission meets

TMLR asks two questions. This submission answers both directly rather than leaving them to be
inferred.

### 1. Are the claims supported by convincing evidence?

The paper is a reproduction whose entire methodological argument is that every number cites a
file on disk. Concretely:

- **Verification before measurement.** The reimplementation is checked against the released
  reference at the gradient level — losses and gradients match to `0.000e+00` across 7 terms and 106 tensors — before any training run is scored. Shapes, wiring, action indexing and the
  hold-last residual are each verified separately, and every later step inherits all five.

- **22 pre-registered decision rules, with git lead times.** All but one name their conditions and thresholds before their data existed, and Appendix E gives all 22 with the lead time computed from git. 21 have a positive lead and are a difference of two commit timestamps; the remaining one is negative and is not, because its data side is a line in a run log rather than a
  commit — it is the rule this paper withdraws as a pre-registration, and Appendix E says so. The
  full committed text of every rule ships in the supplementary material, unabridged.

- **Verdicts reported as returned.** Including the ones that are inconvenient: `M-43` returns
  `DOES NOT GENERALISE`, `M-49` returns `UNDER-POWERED — favours the matched ensemble by less than the MDE`, and `M-51`/`M-52` return
  `SURVIVES entry-res ONLY` — a free baseline comes close enough to ensemble disagreement that
  this sample cannot separate them, which weakens the paper's own strongest positive result.

- **Two results that run against the paper's own arms**, reported at full strength rather than
  buried. At one forecast step, teacher forcing *beats* the autoregressive training this paper
  reproduces — a gap the 400-step unit could only report as spanning zero, resolved as real under a second pre-registered rule at 60 units. And the synthetic experiment that corroborates the
  collapse clears its own slope threshold on only 11 of 20 seeds. `M-50`'s verdict of
  OBJECTIVE-DRIVEN stands as returned over the 3 seeds it was discharged on and is not re-opened
  by a larger sample; what the wider sweep establishes is that the all-seeds criterion would not
  have held across all 20, so the hedge the rule carried was necessary rather than cautious.

- **Thirteen withdrawals kept in the record** — seven claims withdrawn on evidence and six framings withdrawn — with the evidence that withdrew each, including one wrong by about a factor of 10¹³ and one withdrawal of the paper's own claim to have pre-registered a rule it had not.

- **A build gate published as failing.** The clean-clone check requires that no regenerated value
  differ; 6 of 15,657 do, so it fails, it says where, and it is reported as failing. It was not
  given a tolerance, and none of the 6 is a measurement, a statistic or the verdict of a test. The
  reproducibility figure is stated over the 0.92% of the numeric values under `results/` that a
  clean clone regenerates and the comparison counts, rather than over the whole directory: counting
  the values a clone merely carries in would overstate it about 109-fold, and an earlier version of
  this claim did exactly that.

### 2. Would some individuals in TMLR's audience be interested in the findings?

The reproducibility carve-out asks for work that systematically studies the robustness or
generalizability of existing results and lays out actionable lessons. §9 is written to that
description.

The finding a practitioner can act on is that the uncertainty a deployed robotic world model
penalises with is miscalibrated **as a scale, by a factor that grows with rollout depth** — so it
is not a units problem a tuned coefficient absorbs. The best constant rescale, fitted and scored
on the same data and therefore an upper bound on what any constant achieves, grows by a factor of 4 across the rollout. One candidate repair is given, a recipe to refit rather than a demonstrated fix: a per-horizon multiplier, fitted on one held-out episode and scored on the other, brings every coverage estimate of the released checkpoint within 10 points of nominal, though no single cell is resolvable at this arena and those cells are unseen only by the multiplier, since the checkpoint trained on both episodes; on Arm A, whose model never saw them, its own multipliers manage 17 of 36 epistemic cells, and the cells are not independent trials.

The lessons in §9 generalise past this checkpoint: do not convert per-dimension sign counts into
P-values when the dimensions are physically coupled; count independent trajectories rather than
trajectories, and do not resample pooled seed x trajectory values when the trajectory is the unit;
and price a trust metric against the free alternatives before paying for an ensemble.

---

## Reproducibility Certification

**We request Reproducibility Certification explicitly.**

The criterion is significant added value through additional baselines, analyses, ablations or
insights beyond reproducing the original results. This work adds:

| addition | what it is |
|---|---|
| three free baselines | the forecast step index, the model's own predicted step size, and its entry residual — none run by either original |
| six controls on the ranking claim | linear, log, cubic and rank partials on depth, a within-step control, and a pre-registered trajectory-difficulty control |
| an independent-ensemble contrast | five separately trained models against our own shared-trunk ensembles of the released architecture, testing the mechanism rather than asserting it |
| a capacity-matched re-test | the same contrast with parameter count held fixed: rule M-49 returns `UNDER-POWERED — favours the matched ensemble by less than the MDE`, so capacity does not explain the effect away, and how much of it capacity accounts for is not resolved |
| a synthetic ground-truth experiment | data whose noise level is known, isolating the objective as the cause of the σ collapse |
| a candidate repair, with mixed evidence | the per-horizon multiplier, fitted on one episode and scored on the other: the released checkpoint's cells within 10 points (no cell resolvable at this arena), 17 of 36 epistemic cells on Arm A |
| two evaluation units | 400-step and short-unit figures reported side by side, each naming its unit, arena and `n_independent` |

The base paper's central training claim reproduces, and the advantage grows with horizon. What
the reproduction adds is the measurement of the uncertainty outputs neither original quantifies,
and the negative results that come with measuring them honestly.

---

## Anonymisation

The submission is double-blind. The paper compiles in TMLR submission mode
(`\usepackage{tmlr}` with no options), carries no author block, and the PDF is asserted clean of
identifying strings in its text, its raw bytes, its metadata and its figures. The supplementary
bundle is scrubbed against a deny-list covering the authors' names, both usernames, both
repository URLs, ORCID identifiers, e-mail addresses, absolute home-directory paths, and
resolvable archival identifiers — and the scrubber plants a known string on every run to prove
its own scan still detects one.
