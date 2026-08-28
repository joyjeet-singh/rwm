<!-- Source for README.md. Do not edit README.md — it is generated.
     Every number below is a placeholder substituted from results/paper_numbers.json
     by scripts/build_readme.py, the same machinery that builds the paper. The README
     drifted materially behind the paper once — a retracted claim stood here for weeks
     after §8 withdrew it — and this is the fix. -->

# RWM reproduction — proprioceptive dynamics model

An independent reproduction of the proprioceptive dynamics model from Li, Krause & Hutter,
*Robotic World Model* ([arXiv:2501.10100v1](https://arxiv.org/abs/2501.10100)), and the
uncertainty-aware follow-up ([arXiv:2504.16680v1](https://arxiv.org/abs/2504.16680)) — built from
scratch on CPU and verified against the released reference at the level of outputs, losses and
gradients before anything was trained.

**The paper is [`PAPER.md`](PAPER.md)** (LaTeX: [`PAPER.tex`](PAPER.tex)). It is generated, not
typed: every number is substituted from an artifact under `results/` by `scripts/build_paper.py`,
which refuses to emit a paper if any placeholder is unresolved. This README is generated the same
way, from the same file, so the two cannot disagree. `PAPER.tex` compiles clean under pdfTeX —
34 pages, 0 overfull boxes, 0 LaTeX warnings
(`results/compile_paper.json`). The checkpoints are described in [`MODEL_CARD.md`](MODEL_CARD.md).

**Every claim lives in [`FINDINGS_LEDGER.md`](FINDINGS_LEDGER.md)** — 201 entries, each
with an ID, a status, an evidence class, and the `file:line` or run artifact it came from. Claims
are never edited in place: 19 are marked `SUPERSEDED` and kept.
Six of those are retractions of our own **numbered claims** on evidence this
project produced, and six withdraw **framings** — a sentence the paper
asserted that turned out to be false, rather than a number that turned out to be wrong. The two
counts are separate and the paper keeps them separate; four of the framing retractions were
entered by the second pre-submission review, and one of those is the record of a claim §8 had
already narrowed in the paper while the ledger and this README went on asserting it.

## What this found

**1 — The base paper's central training claim reproduces, and the advantage grows with horizon.**
Autoregressive training beats teacher forcing by a factor of **4.61×** on the reference's
own relative-L1 error at the 368-step open-loop horizon, over 3 seeds on
held-out episodes (0.3582 against 1.6497), under a decision rule committed to git
before the runs that tested it existed. Across the whole horizon grid the ratio rises
monotonically to that figure — **2.58×** at h = 100, the horizon the
method deploys at — and the gap excludes zero at 5 of 6 horizons,
spanning it only at h=1. Only the h = 368 figure is pre-registered;
the rest were computed after the data existed and are marked as such.

**2 — Neither uncertainty output of the follow-up is usable as an interval.** At
h = 100 — the horizon the method's own imagination rollouts run to — the ensemble
disagreement it penalises rewards with is **33.4×
[28.7, 39.0]** smaller than the realised error, covering
4.61% at ±1σ where a calibrated Gaussian covers 68.27%. The
per-member σ is 11,683× out, and that one is derived rather than observed: the
implemented objective is squared error on a sampled prediction, whose optimum is σ = 0.

**3 — As a ranking it survives adversarial testing.** Ensemble disagreement beats the forecast
step index — a free counter neither original paper compared against — at every horizon. With both
the rollout and the forecast depth held constant it still correlates **+0.419
[+0.318, +0.576]** with realised error, so it is not merely reporting which episode is hard.

**4 — The interval is repairable.** One multiplier per forecast horizon, fitted on one held-out
episode and scored on the other, restores nominal coverage on every held-out cell; a single global
multiplier manages 2 of them.

**5 — The released five-member ensemble is not five models.** One GRU trunk, one recurrent hidden
state, and 89.15% of each member's state-prediction parameters numerically identical
across members — measured from the checkpoint's own tensors and from source (§6.4). Members that
share a feature extractor have correlated errors by construction, so their spread is a lower bound
on epistemic uncertainty by design rather than by accident.

**6 — That mechanism is tested, not merely asserted, and it holds.** Five independently
initialised full models, sharing nothing, scored together as an ensemble are
**2.03×** better calibrated than the shared-trunk arms at h = 100 —
against a minimum detectable effect of 1.45× fixed before the runs existed. σ is
larger by 1.65×, which is 71% of the improvement there, and the
split reverses at the 368-step diagnostic horizon. The rule (M-44) returns
**MECHANISM SUPPORTED**. It is still 5.2× overconfident: building the ensemble
properly is worth doing and is not sufficient (§6.10).

**And four defects in the released pipeline**, plus evidence that the released
checkpoint's variance state is not reachable from the released artifacts at the iteration count
its author recalls — which the first author attributes to the repository having moved on between
training and release. **The released artifacts do not reproduce the released checkpoint's
variance state**; that is the claim, and it is narrower than the one an earlier version of this
README made.

## Scope, stated plainly

This reproduces the **dynamics model** only. The hardware-transfer, sample-efficiency and
policy-learning results of both papers are **not tested**: they need a simulator, an RL loop and
an ANYmal, none of which this reproduction has. No policy is trained anywhere in this work. The
paper's §4 and Appendix F give the claim-by-claim breakdown.

## Verification chain

| Level | Claim | Result |
|---|---|---|
| Shapes | parameter counts match | exact |
| Wiring | inference outputs match the reference module | **0.000e+00**, bitwise |
| Indexing | the harness feeds the actions it claims | bitwise against the raw CSV |
| Residual | zero-delta model is the hold-last floor | 1.19e-07 |
| **Objective** | **losses and gradients match** | **0.000e+00 across 7 loss terms, 106 parameter tensors** |

Everything from Step 5 onward inherits all five.

## Layout

```
FINDINGS_LEDGER.md    every claim, with evidence and status — start here
PAPER.template.md     the paper's prose; PAPER.md is generated from it
README.template.md    this file's source; README.md is generated from it
LOSS_ASSEMBLY.md      line-by-line extraction of the reference loss
src/                  importable modules
scripts/              one script per investigation, each self-documenting
results/              JSON and text artifacts backing the ledger's RUN evidence
figures/              plots
docs/                 correspondence, archival identifiers, claims audit
setup.sh              fetch upstreams at pinned commits, verify artifact hashes
```

| Module | Purpose |
|---|---|
| `src/rwm_data.py` | Loading, episode structure, config import, assertions |
| `src/rwm_model.py` | The model — inference and training paths, from scratch |
| `src/rwm_train.py` | Data pipeline, optimizer, train step, hyperparameters |
| `src/rwm_metrics.py` | Normalised RMSE with a fixed denominator |
| `src/rollout_eval.py` | Model-agnostic evaluation harness + acceptance tests |
| `src/score_reference.py` | Scores the released checkpoint |

## Reproducing

```bash
./setup.sh                      # clones both upstreams at the pinned commits,
                                # verifies the two artifact SHA-256 hashes
python3.11 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
./reproduce.sh --quick --force  # everything except the training arms
```

`setup.sh` does **not** install either upstream: their `setup.py` pins `torch>=2.7` with CUDA,
which would replace the pins in `requirements.txt`. Only their source is read. `torch 2.2.2` is
the last release with Intel-Mac wheels and is built against NumPy 1.x, so the NumPy pin is
required rather than cosmetic.

**The `--force` flag matters.** A clean clone already contains `results/`, so every stage's
declared output exists and `--quick` alone skips all of them.

## Determinism and regeneration

Training is bitwise reproducible under a fixed seed: the 10,000-iteration run reproduces the
existing 2,500-iteration run exactly at every logged iteration, and `weights_2500.pt` is
byte-identical between them.

A clean-clone run of `reproduce.sh --quick --force` regenerates **36 artifact files and
6,819 numeric values, 6,818 of them bitwise identical (99.99%),
1 differing**, with 0 keys lost (`results/verify_reproduction.json`).

**A note on what that number is not.** An earlier version of this section counted every numeric
value in the committed `results/` directory. Because `results/` is committed, a clean clone
already contains all of it, so files the run never rewrote compared identical and were counted as
regenerated — inflating the figure by about fiftyfold. `reproduce.sh` now records what it actually
regenerates and the verifier partitions on that (`M-28`, `M-29`).

`step4_5_timing.json` is excluded wholesale: it measures the host, not the model.

## Every figure names its horizon

The paper reports two load-bearing horizons and they are not interchangeable.
**h = 100** is the method's own imagination rollout length — the horizon the
uncertainty-penalised policy loop actually runs this model over. **h = 368** is the
upstream's open-loop *diagnostic* length, 3.68× longer, and it is not a deployment
horizon; an earlier draft of the paper called it one and that label is withdrawn.

Re-anchoring the tables from one to the other left prose behind: sentences quoting a correct,
provenanced h = 368 figure sat beside h = 100 tables saying nothing about
it. No provenance check can see that. `scripts/horizon_sweep.py` walks the template, resolves
every numeral to the artifact cell it came from, and reports that cell's horizon against the
horizon the sentence names — a calibration ratio or coverage must name it in its own sentence,
everything else horizon-indexed in its own paragraph. It runs on every build as the
`horizon-consistency` check and the build fails on any finding.

## The build checks its own prose

Verifying that every numeral came from an artifact says nothing about the sentence built around
it. The build therefore also verifies **49 comparative claims** across 20 kinds,
each pinning a fragment of the paper's own text *and* a relation recomputed from the artifacts.
Every one is run against a deliberately corrupted expectation on each build and must fail:
49 of 49 caught.

```bash
python scripts/check_comparative_claims.py --self-test
python scripts/ledger_check.py
```

## Environment

Intel Mac x86_64, CPU only, Python 3.11.15, torch 2.2.2, numpy 1.26.4.
26 training runs, all on CPU.
Reference commits: `robotic_world_model_lite` `13a798e9`, `rsl_rl_rwm` `18eebcdd`.

## Licence and attribution

Apache 2.0 — see [`LICENSE`](LICENSE). The upstreams are under different licences:
`robotic_world_model_lite` is Apache 2.0, `rsl_rl_rwm` is BSD 3-Clause. Neither is redistributed
here. Attribution and the independence statement are in [`NOTICE`](NOTICE). This is an independent
reproduction and is not endorsed by the original authors.
