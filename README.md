# RWM reproduction — proprioceptive dynamics model

An independent reproduction of the proprioceptive dynamics model from
Li, Krause & Hutter, *Robotic World Model* ([arXiv:2501.10100](https://arxiv.org/abs/2501.10100)),
built from scratch on CPU and verified against the released reference at the level of
outputs, losses and gradients.

**Every claim in this repository lives in [`FINDINGS_LEDGER.md`](FINDINGS_LEDGER.md)** with an
ID, a status, its evidence class, and the file:line or run artifact it came from. Claims are
never edited in place; wrong turns are marked `SUPERSEDED` and kept.

## Status

Steps 0–4 complete. No long training run has been performed yet — Step 4 ends at the
timing measurement, which decides where Step 5 runs.

## What has been established

Three findings drive the rest of the work:

1. **The released data has ten unmarked episode boundaries.** The termination column is
   identically zero, so the reference window builder marks all 9,961 windows valid,
   including 352 that splice the end of one episode onto the start of another. The real
   usable count is 9,609. (`D-03`, `D-04`, `B-01`)

2. **Training and evaluation disagree on action alignment, and the evaluation side is the
   broken one.** Row *t* holds the action that *produced* state *t*, so the reference's
   training pairing is causal and its evaluation pairing is stale by one step. Scored
   correctly the checkpoint is materially better than the released evaluation reports —
   24% lower one-step error. (`D-13`, `B-05`, `R-09`)

3. **The variance head has collapsed, and that is the objective's optimum, not an
   accident.** The state loss is squared error on a reparameterised sample with no
   log-sigma term, so `E[(mu + sigma*eps - y)^2] = (mu - y)^2 + sigma^2` is minimised at
   sigma = 0. In the released checkpoint the learned interval has closed to 5.23e-07.
   (`C-06`, `C-10`, `O-08`)

The verification chain: outputs bitwise identical to the reference module (`R-11`), harness
indexing pinned by direct assertion against the raw CSV (`R-12`), and losses **and
gradients** matching to 0.000e+00 across all seven terms and all 106 parameter tensors
(`R-14`).

## Layout

| File | Purpose |
|---|---|
| `FINDINGS_LEDGER.md` | Every claim, with evidence and status. Start here. |
| `rwm_data.py` | Loading, episode structure, config import, assertions |
| `rwm_model.py` | The model — inference and training paths, from scratch |
| `rwm_train.py` | Data pipeline, optimizer, train step, hyperparameters |
| `rwm_metrics.py` | Normalised RMSE with a fixed denominator |
| `rollout_eval.py` | Model-agnostic evaluation harness + acceptance tests |
| `score_reference.py` | Scores the released checkpoint |
| `step0_*`, `step4_*`, `task1*`–`task5*` | One script per investigation, each self-documenting |
| `figures/` | Plots |
| `*_report.txt`, `*.json` | Run artifacts backing the ledger's `RUN` evidence |

## Reproducing

Needs the two upstream repositories, which are **not** vendored here:

```bash
git clone https://github.com/leggedrobotics/robotic_world_model_lite
git clone https://github.com/leggedrobotics/rsl_rl_rwm
```

Place both beside this directory. Do **not** run `pip install -e .` in either — their
`setup.py` pins `torch>=2.7` with CUDA. The modules themselves import fine on CPU.

```bash
python3.11 -m venv .venv && . .venv/bin/activate
pip install "torch==2.2.2" "numpy==1.26.4" "pandas==2.2.3" "matplotlib==3.8.4" gitpython tensordict
```

`torch 2.2.2` is the last release with Intel-Mac wheels and is built against NumPy 1.x, so
the NumPy pin is required. `gitpython` and `tensordict` are only needed to import the
reference package cleanly for the differential tests.

Then, in dependency order:

```bash
python step0_velocity_regimes.py      # command regimes; writes the split key
python rollout_eval.py                # harness + six acceptance tests
python score_reference.py             # scores the released checkpoint
python step4_3_differential.py        # the acceptance gate: losses and gradients
python step4_5_timing.py              # CPU budget
```

## Environment

Intel Mac x86_64, CPU only, Python 3.11.15, torch 2.2.2, numpy 1.26.4.
Reference commits: `robotic_world_model_lite` `13a798e9`, `rsl_rl_rwm` `18eebcdd`.
Both upstream repositories are Apache 2.0.
