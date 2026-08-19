# RWM reproduction — proprioceptive dynamics model

An independent reproduction of the proprioceptive dynamics model from
Li, Krause & Hutter, *Robotic World Model* ([arXiv:2501.10100](https://arxiv.org/abs/2501.10100)),
built from scratch on CPU and verified against the released reference at the level of
outputs, losses and gradients.

**Every claim in this repository lives in [`FINDINGS_LEDGER.md`](FINDINGS_LEDGER.md)** with an
ID, a status, its evidence class, and the file:line or run artifact it came from. Claims are
never edited in place; wrong turns are marked `SUPERSEDED` and kept.

## Status

**Steps 0–5 complete. Fourteen training runs. Two papers in scope, and the headline finding is
about the follow-up rather than the base paper.**

**1 — The uncertainty output is unusable, and that is a property of the objective**
([arXiv:2504.16680](https://arxiv.org/abs/2504.16680), the RWM-U follow-up). The released
checkpoint's predicted σ is **7,878× smaller than its own mean absolute error**, giving 0.14%
coverage at ±1σ where a calibrated Gaussian gives 68.3%. This is derived analytically, confirmed
across fourteen runs, extrapolated with 3% accuracy over a fourfold extension, and tested with a
corrective experiment using **the authors' own unused `gaussian_nll` branch** — which reverses
the collapse mechanism and still does not produce a usable estimate (`R-48`–`R-54`).

**2 — The base paper's central claim REPRODUCES at long horizon**
([arXiv:2501.10100](https://arxiv.org/abs/2501.10100)), under a decision rule committed to git
before the runs that tested it existed. At h=368 out-of-sample after 10,000 iterations from
scratch: autoregressive **0.3509** against teacher forcing's **1.5540**, a factor of **4.4×**,
95% bootstrap CI [+0.56, +2.05] excluding zero, per-episode gap positive on **all ten episodes**.
All three of `M-23`'s pre-registered conditions hold (`R-40`), rule committed in `efc35b8`.

Stated alongside, because the discipline is the point:

- an earlier rule (`M-16`) returned **"cannot be settled"** — anchored at h=8, the training
  forecast horizon rather than the horizon the claim is about (`M-24`). `M-23` corrected it, in
  advance.
- **three findings have been retracted** on this project's own evidence (`S-09`, `S-10`,
  `S-11`), each after a plausible first reading failed a gating check.
- the h=8 ambiguity **never resolves** out-of-sample, even at 10,000 iterations, because only
  four independent 400-step trajectories exist there (`R-42`, `M-20`).

## What has been established

Four findings drive the rest of the work:

1. **The released data has ten unmarked episode boundaries.** The termination column is
   identically zero, so the reference window builder marks all 9,961 windows valid,
   including 352 that splice the end of one episode onto the start of another. The real
   usable count is 9,609. (`D-03`, `D-04`, `B-01`)

2. **Training and evaluation disagree on action alignment, and the evaluation side is the
   broken one.** Row *t* holds the action that *produced* state *t*, so the reference's
   training pairing is causal and its evaluation pairing is stale by one step. Scored
   correctly the checkpoint is materially better than the released evaluation reports: at
   h=368 it goes from nRMSE 1.3228 — worse than predicting the training mean — to 0.7572.
   (`D-13`, `B-05`, `R-09`, `R-15`)

3. **The variance head collapse is the objective's optimum, not an accident.** The state
   loss is squared error on a reparameterised sample with no log-sigma term, so
   `E[(mu + sigma*eps - y)^2] = (mu - y)^2 + sigma^2` is minimised at sigma = 0; the bound
   loss pushes the same way; and `min_logstd` cancels out of it entirely, making it a
   one-way ratchet. Predicted from the algebra, then reproduced on a fresh model.
   (`C-06`, `C-10`, `C-11`, `R-17`, `R-18`)

4. **The released checkpoint cannot have come from the released recipe — on two independent
   parameters.** The collapse rate pooled over six runs is −9.4362e-05 ± 3.33e-07, a
   run-to-run spread of 0.87%, implying ~153,000 iterations at the configured learning rate or
   one 31× larger. `min_logstd`, on a different gradient path and a 5× slower clock,
   independently implies order 2.7e5. The checkpoint is tagged iteration 5000, the config says
   500, the paper says 2500. (`C-12`, `C-13`, `O-12`, `R-24`, `R-25`)

5. **Teacher forcing trains better and deploys worse, measured end to end.** Arm B reaches a
   3× lower training loss with 5× smaller gradient norms, then rolls out 4.3× worse at h=368.
   The objective it minimises is not the objective that matters. (`R-22`, `R-23`)

6. **A from-scratch model does not develop the released checkpoint's failure pattern.** After
   10,000 iterations Arm A loses to the hold-last floor on **1 of 45** dimensions — `g_z`, the
   one weighted 1/1174 by a mis-specified normalisation constant — against the released
   checkpoint's **7**, with a Jaccard overlap of 0.14. The released weights' extra weaknesses
   are specific to that checkpoint, not implied by the objective. (`R-41`)

## Verification chain

What any downstream number rests on:

| Level | Claim | Result |
|---|---|---|
| Shapes | parameter counts match | `R-01`, exact |
| Wiring | inference outputs match the reference module | `R-11`, **0.000e+00** bitwise |
| Indexing | the harness feeds the actions it claims | `R-12a`, bitwise vs raw CSV |
| Residual | zero-delta model is the hold-last floor | `R-12c`, 1.19e-07 |
| **Objective** | **losses and gradients match** | **`R-14`, 0.000e+00 across 7 terms, 106 tensors** |
| Trainer | can memorise a batch | `R-18`, 1506× loss reduction |

## Layout

```
FINDINGS_LEDGER.md    every claim, with evidence and status — start here
LOSS_ASSEMBLY.md      line-by-line extraction of the reference loss
src/                  importable modules
scripts/              one script per investigation, each self-documenting
results/              JSON and text artifacts backing the ledger's RUN evidence
figures/              plots
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
```

`setup.sh` does **not** install either upstream: their `setup.py` pins `torch>=2.7` with
CUDA, which would replace the pins in `requirements.txt`. Only their source is read.
`torch 2.2.2` is the last release with Intel-Mac wheels and is built against NumPy 1.x, so
the NumPy pin is required rather than cosmetic.

Then, in dependency order:

```bash
python scripts/step0_velocity_regimes.py   # command regimes; writes the split key
python src/rollout_eval.py                 # harness + six acceptance tests
python src/score_reference.py              # scores the released checkpoint
python scripts/step4_3_differential.py     # acceptance gate: losses and gradients
python scripts/step4_5_timing.py           # CPU budget
```

## Determinism

Training is bitwise reproducible under a fixed seed: the 10,000-iteration run reproduces the
existing 2,500-iteration run exactly at every logged iteration, and `weights_2500.pt` is
byte-identical between them.

A clean-clone run of `reproduce.sh --quick` regenerates **258,700 numeric values bitwise**, with
zero differing. Two categories are excluded from that count and are documented here rather than
left for a reader to find:

- **Timing fields** (`wall_clock_seconds`, `s_per_iter`, `elapsed_s`) — 1,439 values. These
  measure the machine, not the model. Magnitude of the variation: a stage timed at 46.5 s on an
  idle machine took 109.7 s while training ran concurrently, i.e. up to ~2.4×.
- **Four NaN values** — the `base ang vel` group ratio at h = 8/32/128/368 in
  `task2_4_results.json`. These are `inf/inf`, a documented failure of the relative-L1 metric at
  group granularity (`M-09`), and are NaN in both the committed and regenerated files.

## Environment

Intel Mac x86_64, CPU only, Python 3.11.15, torch 2.2.2, numpy 1.26.4.
Reference commits: `robotic_world_model_lite` `13a798e9`, `rsl_rl_rwm` `18eebcdd`.

## Licence and attribution

Apache 2.0 — see [`LICENSE`](LICENSE). Both upstream repositories are Apache 2.0; attribution
and the independence statement are in [`NOTICE`](NOTICE). This is an independent
reproduction, not affiliated with or endorsed by the original authors.
