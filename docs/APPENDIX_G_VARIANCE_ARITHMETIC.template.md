<!-- GENERATED FILE — do not edit. Edit docs/APPENDIX_G_VARIANCE_ARITHMETIC.template.md and run:
     python scripts/build_paper.py -->

# The variance-state arithmetic behind §7.5

Supplementary to the paper's §7.5 and Appendix G, which keep the conclusion: the released
artifacts do not reproduce the released checkpoint's variance state, and the author's account is
that the released repository is not the one that trained it. This carries the arithmetic and the
five assumptions it rests on, moved out of the body because the numbered claim it once supported
is retracted (`S-19`). Nothing was deleted: both blocks below left the paper verbatim.

This file is GENERATED from `docs/APPENDIX_G_VARIANCE_ARITHMETIC.template.md` by
`scripts/build_paper.py`, from the same `results/paper_numbers.json` the paper is built from, so
a figure quoted here cannot disagree with the one the paper prints.

---

## Moved verbatim from §7.5

**7.5 The released artifacts do not reproduce the released checkpoint's variance state.**
The σ collapse is linear in iteration count and its rate is nearly identical across our runs
(§6.3), which makes it a clock. Extrapolating it to the released checkpoint's σ state implies
**{{implied_iters}}** optimisation steps at the configured learning rate — against a released
configuration that says 500, a paper that says 2,500 and a checkpoint tagged 5,000. A second
parameter on a slower gradient path implies the same order independently. The defensible claim is
narrower than it first looks: **no
constant-rate run from the released initialisation at the configured learning rate reaches that
variance state at any of the three stated counts.** A warm start or a different
`log_delta_logstd` initialisation would explain it with no inconsistency at all, and we can
exclude neither. The first author's account is that the released repository is several revisions
removed from the setup that trained the checkpoint, which supplies exactly such a mechanism. So
this is a **documentation gap between a release and a run** — common, worth recording, and much
less interesting than an inconsistency. Appendix G gives the arithmetic and the five assumptions
it rests on, because it is what let us detect the gap at all.

---

## Moved verbatim from Appendix G

The collapse rate is a clock. Fitting it across our runs and extrapolating to the released
checkpoint's σ state implies **{{implied_iters}}** optimisation steps at the configured learning
rate. The refit from our 10,000-iteration runs gives {{q4_implied_A}} and {{q4_implied_B}},
spreading {{implied_spread_pct}}% across the three fits — a linear extrapolation
validated over a fourfold extension.

The released configuration says 500 iterations. The paper says 2,500. The checkpoint is tagged
5,000. A second, independent parameter on a slower gradient path implies the same order. And under
`gaussian_nll` the implied count is *negative*, which identifies the branch the checkpoint was
trained with.

**What this extrapolation assumes, and what would falsify it.** It assumes constant-rate Adam at
the configured learning rate from the released initialisation. Five things would break it, and
they are not equally plausible:

| assumption | if violated | ruled out by the second parameter? |
|---|---|---|
| no learning-rate schedule | a decaying schedule inflates the implied count; a warm-up deflates it | **partly** — `min_logstd` and `log_delta_logstd` travel at rates differing by about {{o12_rate_ratio}}×, and a uniform schedule scales both, so a schedule alone cannot reconcile them without also changing their ratio |
| `log_delta_logstd` initialised as released | a different initialisation moves the origin of the fit and rescales the count linearly | **no** — this is the weakest point of the argument |
| no warm start from an earlier checkpoint | a warm start makes the count a lower bound on total optimisation, not an estimate of one run | **no** |
| no gradient clipping in this path | clipping would slow the collapse and inflate the implied count | **partly** — the reference does not clip in the world-model path (X-08), so this is ruled out by source rather than by measurement |
| bound-loss weight as configured | a different weight scales the rate directly | **partly** — same ratio argument as the schedule |

So the defensible claim is narrower than "cannot have come from the released recipe": **no
constant-rate run from the released initialisation at the configured learning rate reaches this
checkpoint's variance state in 500, 2,500 or 5,000 iterations.** A warm start or a different
initialisation would explain the gap without any inconsistency, and we cannot exclude either.

**What the author says.** We wrote to the first author on 21 August 2026 asking exactly this. He
replied the same day; the exchange is reproduced in full, anonymised, in the supplementary
material (`SUPPLEMENTARY_CORRESPONDENCE.md`): the released `max_iterations: 500` is "a typo"; his recollection is 5,000
iterations, "as I always did"; he does not recall how the checkpoint was obtained; and — the part
that matters most — "the checkpoint was released after a few iterations of the repo than the setup
I used for the submission."

That last point reframes this section. The extrapolation above assumes the *released*
initialisation and the *released* learning rate. If the repository drifted between the training
run and the release, those are not necessarily the values that produced the checkpoint — and a
changed `log_delta_logstd` initialisation is precisely the assumption the table above cannot rule
out.
