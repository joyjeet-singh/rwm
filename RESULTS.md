# Results

**Two papers are in scope.** The released checkpoint `pretrain_rnn_ens.pt` is the five-member
**RWM-U** configuration of [arXiv:2504.16680](https://arxiv.org/abs/2504.16680); the
autoregressive-versus-teacher-forcing claim `M-23` tested is from the base
[arXiv:2501.10100](https://arxiv.org/abs/2501.10100). Every ledger entry is tagged `[BASE]`,
`[RWM-U]` or `[BOTH]`.

## The headline finding — the uncertainty output is unusable `[RWM-U]`

The released checkpoint's predicted σ is **7,878× smaller than its own mean absolute error**:
0.14% coverage at ±1σ, against 68.3% for a calibrated Gaussian. At a predicted 99.7% (±3σ) the
observed frequency is 0.1%.

This is not a training failure. The state loss is squared error on a reparameterised sample with
no log-σ term, so it is minimised at σ = 0; the bound loss pushes the same way; and `min_logstd`
cancels out of the bound loss entirely, making the ratchet one-way. Running **the authors' own
unused `gaussian_nll` branch** reverses the mechanism — and still does not produce a usable
estimate: magnitude improves to 10.9× overconfident, σ remains input-independent (CoV 0.0059
while the permitted interval allows a 3.0× spread), and the faint ordering signal the faithful
arm had is destroyed (39/45 positive, P = 5.4e-07 → 21/45, chance). Measured across
all four models (`R-57`) the failure is one of magnitude: Arm B has the best-ordered σ (45/45)
and is still 315× overconfident.

σ is flat even across forecast steps 1–8, the window the loss actually optimises, while realised
error grows 3.4×. There is no structural excuse. (`R-48`–`R-54`, `O-12`, `O-13`)

An independent reproduction of the proprioceptive dynamics model from
Li, Krause & Hutter, *Robotic World Model* (arXiv:2501.10100). This page is the outcome;
[`FINDINGS_LEDGER.md`](FINDINGS_LEDGER.md) is the evidence.

## The base paper's central claim `[BASE]`

**The paper's central claim — that the autoregressive training objective beats teacher
forcing — REPRODUCES at long horizon.**

Decision rule `M-23`, committed in `efc35b8` **before either run that tested it existed**:

| condition | result |
|---|---|
| 1. Arm A leads Arm B at the 2500 **and** 10,000 checkpoints | **met** — gaps +6.7455, +1.2033 |
| 2. 95% bootstrap CI on the gap excludes zero at 10,000 | **met** — [+0.5606, +2.0467] |
| 3. per-episode sign consistent across all ten episodes | **met** — all positive, +0.418 to +1.826 |

## The headline comparison

Relative-L1, 400-step trajectories, form-1 pooled aggregation, independent trajectories only.
`n_ind` is the number of **mutually non-overlapping** trajectories — the statistic that actually
bounds these estimates.

| arena | n_ind | ckpt | h | Arm A | Arm B | gap | 95% CI |
|---|---|---|---|---|---|---|---|
| out-of-sample | 4 | 2500 | 368 | 0.5922 | 7.3325 | +6.7455 | [+1.1094, +16.9030] |
| out-of-sample | 4 | 10000 | 368 | **0.3509** | 1.5540 | +1.2033 | [+0.5606, +2.0467] |
| in-sample | 16 | 10000 | 368 | **0.1002** | 0.9723 | +0.8719 | [+0.6711, +1.0920] |
| out-of-sample | 4 | 10000 | 8 | 0.3414 | 0.3495 | +0.0080 | [-0.1316, +0.1243] **spans zero** |
| in-sample | 16 | 10000 | 8 | **0.0862** | 0.1349 | +0.0486 | [+0.0284, +0.0705] |

**Power caveat, stated where the verdict is:** the governing row rests on `n_ind = 4`. A
bootstrap over four points cannot characterise a distribution — it can only say all four lie one
side by a margin. The verdict's credibility comes from the in-sample arena at `n_ind = 16`
returning the same answer with a tighter interval, from the per-episode sign holding on all ten
episodes independently, and from an effect size of 4.4–9.7×.

## The claim's history, in three lines

1. **Asserted** at h=8 in Step 5, under seed-spread statistics and overlapping trajectories.
2. **Withdrawn** when corrected measurement returned *cannot be settled* in all eight
   arena/length/metric combinations — the rule had been anchored to the training forecast
   horizon rather than to the horizon the claim is about (`M-24`).
3. **Re-tested** at h=368 under `M-23`, committed before the data existed → **reproduces**.

Two headline claims were formed, promoted and then **retracted on this project's own evidence**
(`S-10`, `S-11`). Section H of the ledger keeps them.

## Discrepancies found

| kind | count | with measured cost |
|---|---|---|
| `C-` paper says one thing, code does another | 15 | see the variance collapse (`C-10`, `C-11`) and the absent decay factor (`C-09`) |
| `B-` defects in the released pipeline | 5 | `B-01`'s cost measured by the contamination arm and its duplication control (`R-56`) |
| `D-` dataset properties | 13 | — |
| `M-` methodological findings | 39 | — |
| `R-` measured results | 66 | — |
| `O-` open questions | 14 | — |
| `X-` deliberate deviations | 10 | — |
| `S-` superseded, retained | 15 | — |

Highlights: the released data has **ten episode boundaries its own termination column does not
mark**, so the reference builder trains on 352 spliced windows (`B-01`, `D-03`). Training and
evaluation **disagree on action alignment**, and the evaluation side is stale by one step
(`B-05`, `D-13`). The predicted variance **collapses because that is the objective's optimum**,
not a training accident (`C-10`, `C-11`), and the released checkpoint's collapse depth implies
~158,000 optimisation steps against a config saying 500 and a paper saying 2500 (`O-12`).
That figure is the refit from the 10,000-iteration runs (158,003 Arm B / 158,319 Arm A, `R-43`);
the pooled fit over the six 2,500-iteration runs gives 153,270 (`results/step6_analysis.json`).
They are different estimators of the same quantity, agreeing within 3%, not competing claims.

## Reproducing

```bash
./setup.sh              # clone upstreams at pinned commits, verify SHA-256
./reproduce.sh --quick --force  # everything except training, minutes
```

Verified from a genuine clean clone: **19 artifact files, 4,804 numeric values,
4,804 bitwise identical (100.00%), 0 differing, 0 keys lost**
(`results/verify_reproduction.json`). An earlier figure of 258,700 counted files a clone carries
in rather than regenerates; see `M-28`.

## Links

- [`FINDINGS_LEDGER.md`](FINDINGS_LEDGER.md) — every claim, with evidence class and status
- [`results/claims_to_evidence.md`](results/claims_to_evidence.md) — the machine-generated map
- [`LOSS_ASSEMBLY.md`](LOSS_ASSEMBLY.md) — line-by-line extraction of the reference loss
- [`PAPER.md`](PAPER.md) — the paper; [`PAPER.tex`](PAPER.tex) for submission
- [`MODEL_CARD.md`](MODEL_CARD.md) — the four checkpoints, with per-checkpoint limits
- Model checkpoints — released at `huggingface.co/Joyjeetsingh/rwm-reproduction` with sha256s
  in `checkpoint_manifest.json`; the local `runs/` tree stays gitignored and is regenerable
  via `./reproduce.sh`
