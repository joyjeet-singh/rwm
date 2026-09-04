# Cover statement — TMLR submission

*Draft. Every figure is substituted from a named artifact by the paper's own build; the
numbers below are quoted from `results/paper_numbers.json` and are current at 40 pages.*

---

## Which acceptance criterion this submission meets

TMLR asks two questions. This submission answers both directly rather than leaving them to be
inferred.

### 1. Are the claims supported by convincing evidence?

The paper is a reproduction whose entire methodological argument is that every number cites a
file on disk. Concretely:

- **Verification before measurement.** The reimplementation is checked against the released
  reference at the gradient level — losses and gradients match to `0.000e+00` across 7 terms and
  106 tensors — before any training run is scored. Shapes, wiring, action indexing and the
  hold-last residual are each verified separately, and every later step inherits all five.

- **Fifteen pre-registered decision rules, with git lead times.** Each names its conditions and
  thresholds before its data existed, and Appendix F gives all fifteen with the lead time
  computed as a difference of commit timestamps. The full committed text of every rule ships in
  the supplementary material, unabridged.

- **Verdicts reported as returned.** Including the ones that are inconvenient: `M-43` returns
  `DOES NOT GENERALISE`, `M-49` returns `UNDER-POWERED`, and `M-51`/`M-52` return
  `SURVIVES entry-res ONLY` — a free baseline comes close enough to ensemble disagreement that
  this sample cannot separate them, which weakens the paper's own strongest positive result.

- **Two results that run against the paper's own arms**, reported at full strength rather than
  buried. At one forecast step, teacher forcing *beats* the autoregressive training this paper
  reproduces — a gap the 400-step unit could only report as spanning zero, resolved as real
  under a second pre-registered rule at 60 units. And the synthetic corroboration returns MIXED
  at twenty seeds where it returned OBJECTIVE-DRIVEN at three, exactly as the rule warned before
  the runs existed.

- **Twelve retractions kept in the record** — six that withdraw numbers and six that withdraw
  framings — with the evidence that withdrew each, including one wrong by about a factor of
  10¹³ and one withdrawal of the paper's own claim to have pre-registered a rule it had not.

- **A build gate published as failing.** The clean-clone check requires that no regenerated value
  differ; 178 of 8,186 do, so it fails, it says where, and it is reported as failing. It was not
  given a tolerance. The reproducibility figure is stated as 0.90% of the values under
  `results/` rather than as the 97.50% a less careful partition would license — an earlier
  version of that claim counted carried-in files and overstated it about fiftyfold.

### 2. Would some individuals in TMLR's audience be interested in the findings?

The reproducibility carve-out asks for work that systematically studies the robustness or
generalizability of existing results and lays out actionable lessons. §9 is written to that
description.

The finding a practitioner can act on is that the uncertainty a deployed robotic world model
penalises with is miscalibrated **as a scale, by a factor that grows with rollout depth** — so it
is not a units problem a tuned coefficient absorbs. The best constant rescale, fitted and scored
on the same data and therefore an upper bound on what any constant achieves, grows by a factor of
4 across the rollout. One repair works and is given: a per-horizon multiplier, fitted on one
held-out episode and scored on the other, restores nominal coverage on every held-out cell.

The lessons in §9 generalise past this checkpoint: do not convert per-dimension sign counts into
P-values when the dimensions are physically coupled; do not resample trajectory-step pairs when
the trajectory is the unit; and price a trust metric against the free alternatives before paying
for an ensemble.

---

## Reproducibility Certification

**We request Reproducibility Certification explicitly.**

The criterion is significant added value through additional baselines, analyses, ablations or
insights beyond reproducing the original results. This work adds:

| addition | what it is |
|---|---|
| three free baselines | the forecast step index, the model's own predicted step size, and its entry residual — none run by either original |
| six controls on the ranking claim | linear, log, cubic and rank partials on depth, a within-step control, and a pre-registered trajectory-difficulty control |
| an independent-ensemble contrast | five separately trained models against the released shared-trunk ensemble, testing the mechanism rather than asserting it |
| a capacity-matched re-test | the same contrast with parameter count held fixed, so capacity is not the explanation |
| a synthetic ground-truth experiment | data whose noise level is known, isolating the objective as the cause of the σ collapse |
| a working repair | the per-horizon multiplier, evaluated only on held-out folds |
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
