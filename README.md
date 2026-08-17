# RWM reproduction — proprioceptive dynamics model

An independent reproduction of the proprioceptive dynamics model from
Li, Krause & Hutter, *Robotic World Model* ([arXiv:2501.10100](https://arxiv.org/abs/2501.10100)),
built from scratch on CPU and verified against the released reference at the level of
outputs, losses and gradients.

**Every claim in this repository lives in [`FINDINGS_LEDGER.md`](FINDINGS_LEDGER.md)** with an
ID, a status, its evidence class, and the file:line or run artifact it came from. Claims are
never edited in place; wrong turns are marked `SUPERSEDED` and kept.

## Status

**Steps 0–4 complete. Step 5 in progress: 1 of 6 main runs finished.**

The trainer is verified against the reference at the gradient level and proven by an overfit
test. Arm A (autoregressive, faithful) seed 0 has trained to 2500 iterations; Arm A seeds 1–2
and Arm B (teacher forcing) seeds 0–2 are outstanding. The autoregressive-versus-teacher-forcing
comparison is therefore **not yet answered**, and its decision rule is pre-registered in the
ledger (`M-16`) rather than chosen after the fact.

Note on Arm A seed 0: at 2500 iterations — the count the paper states — the training loss is
still falling steeply, at −7.59e-04 per iteration over the final 250. Neither arm will be
converged at this budget, which is itself part of the result.

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

4. **The released checkpoint cannot have come from the released recipe.** Its collapse depth
   implies either ~155,000 iterations at the configured learning rate, or a learning rate
   30–40× larger than configured. The checkpoint is tagged iteration 5000, the config says
   500, and the paper says 2500 — three numbers, none of which fit. (`C-12`, `C-13`, `O-10`)

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

## Environment

Intel Mac x86_64, CPU only, Python 3.11.15, torch 2.2.2, numpy 1.26.4.
Reference commits: `robotic_world_model_lite` `13a798e9`, `rsl_rl_rwm` `18eebcdd`.

## Licence and attribution

Apache 2.0 — see [`LICENSE`](LICENSE). Both upstream repositories are Apache 2.0; attribution
and the independence statement are in [`NOTICE`](NOTICE). This is an independent
reproduction, not affiliated with or endorsed by the original authors.
