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
{{pdf_pages}} pages, {{pdf_overfull}} overfull boxes, {{pdf_warnings}} LaTeX warnings
(`results/compile_paper.json`). The checkpoints are described in [`MODEL_CARD.md`](MODEL_CARD.md).

**Every claim lives in [`FINDINGS_LEDGER.md`](FINDINGS_LEDGER.md)** — {{n_entries}} entries, each
with an ID, a status, an evidence class, and the `file:line` or run artifact it came from. Claims
are never edited in place: {{n_superseded}} are marked `SUPERSEDED` and kept, {{n_retractions_word}}
of them retractions of our own numbered claims on evidence this project produced.

## What this found

**1 — The base paper's central training claim reproduces.** Autoregressive training beats teacher
forcing by a factor of **{{d1_ratio}}×** on the reference's own relative-L1 error at the
{{v2_diag_h}}-step open-loop horizon, over {{d1_seeds}} seeds on held-out episodes
({{d1_A_mean}} against {{d1_B_mean}}), under a decision rule committed to git before the runs that
tested it existed.

**2 — Neither uncertainty output of the follow-up is usable as an interval.** At
h = {{v2_deploy_h}} — the horizon the method's own imagination rollouts run to — the ensemble
disagreement it penalises rewards with is **{{d1n_epi_ratio_h100}}×
[{{d1n_epi_ratio_ci_h100}}]** smaller than the realised error, covering
{{d1n_epi_cov1_h100}}% at ±1σ where a calibrated Gaussian covers {{v3_cov_nominal1}}%. The
per-member σ is {{d1n_alea_ratio_h100}}× out, and that one is derived rather than observed: the
implemented objective is squared error on a sampled prediction, whose optimum is σ = 0.

**3 — As a ranking it survives adversarial testing.** Ensemble disagreement beats the forecast
step index — a free counter neither original paper compared against — at every horizon. With both
the rollout and the forecast depth held constant it still correlates **{{a2_rdd}}
{{a2_rdd_ci}}** with realised error, so it is not merely reporting which episode is hard.

**4 — The interval is repairable.** One multiplier per forecast horizon, fitted on one held-out
episode and scored on the other, restores nominal coverage on every held-out cell; a single global
multiplier manages {{d3_epi_const_ok}} of them.

**And {{n_defects}} defects in the released pipeline**, plus evidence that the released
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
| **Objective** | **losses and gradients match** | **{{diff_grad_max}} across {{diff_terms}} loss terms, {{diff_n_params}} parameter tensors** |

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

A clean-clone run of `reproduce.sh --quick --force` regenerates **{{ver_files}} artifact files and
{{ver_values}} numeric values, {{ver_identical}} of them bitwise identical ({{ver_pct}}%),
{{ver_differing}} differing**, with 0 keys lost (`results/verify_reproduction.json`).

**A note on what that number is not.** An earlier version of this section counted every numeric
value in the committed `results/` directory. Because `results/` is committed, a clean clone
already contains all of it, so files the run never rewrote compared identical and were counted as
regenerated — inflating the figure by about fiftyfold. `reproduce.sh` now records what it actually
regenerates and the verifier partitions on that (`M-28`, `M-29`).

`step4_5_timing.json` is excluded wholesale: it measures the host, not the model.

## The build checks its own prose

Verifying that every numeral came from an artifact says nothing about the sentence built around
it. The build therefore also verifies **{{cc_n}} comparative claims** across {{cc_kinds}} kinds,
each pinning a fragment of the paper's own text *and* a relation recomputed from the artifacts.
Every one is run against a deliberately corrupted expectation on each build and must fail:
{{cc_st_caught}} of {{cc_st_n}} caught.

```bash
python scripts/check_comparative_claims.py --self-test
python scripts/ledger_check.py
```

## Environment

Intel Mac x86_64, CPU only, Python 3.11.15, torch 2.2.2, numpy 1.26.4.
{{n_runs}} training runs, all on CPU.
Reference commits: `robotic_world_model_lite` `13a798e9`, `rsl_rl_rwm` `18eebcdd`.

## Licence and attribution

Apache 2.0 — see [`LICENSE`](LICENSE). The upstreams are under different licences:
`robotic_world_model_lite` is Apache 2.0, `rsl_rl_rwm` is BSD 3-Clause. Neither is redistributed
here. Attribution and the independence statement are in [`NOTICE`](NOTICE). This is an independent
reproduction and is not endorsed by the original authors.
