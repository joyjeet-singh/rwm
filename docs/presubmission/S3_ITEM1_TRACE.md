# S3, item 1 — every h = 8 statement in §5, traced to its source

Written by S3 on 2026-09-28. The contradiction: §5's by-horizon table printed an h = 8 gap that
excludes zero, and the prose beside it said the h = 8 gap was 0.008 with an interval including
zero, and that the gap excluded zero in "0 of 4" h = 8 cells.

| Statement (before S3) | Key | Artifact | Checkpoint | Seeds | Trajectory | Metric, aggregation | Bootstrap unit | Cumulative? | h = 8 result |
|---|---|---|---|---|---|---|---|---|---|
| Table row, h = 8 | `a1_gap_h8`, `a1_gap_ci_h8`, `a1_excl_h8` | `results/a1_ab_by_horizon.json` | 10,000 (`weights_10000.pt`) | 3, pooled inside each draw | 400-step, held-out, n_independent 4 | relative-L1, mean over steps 1..h | whole trajectories, one draw shared across arms | cumulative | +0.0485 [+0.0271, +0.0844], **excludes zero** |
| "a gap of 0.008 whose interval includes zero" | `m23_h8_gap`, `m23_h8_excl` | `results/task5_analysis.json`, `out-of-sample\|10000\|h8` | 10,000 | **1** (seed 1; the artifact's provenance says "single-seed by necessity", M-25) | 400-step, held-out | relative-L1, mean over steps 1..h | trajectories | cumulative | +0.0080 [−0.1316, +0.1243], includes zero |
| "in 0 of 4 at h = 8" | `ab_short_excl`, `ab_short_cells` | `results/review_bootstrap_unit.json`, out-of-sample h8 cells | **500 and 2,500** | 3, pooled ("carrying all three seeds with each draw") | 400- and 200-step | relative-L1 | whole trajectories (cluster) | cumulative | 0 of 4 exclude zero |
| "An earlier rule of ours, anchored at h = 8" | — | FINDINGS_LEDGER.md M-16 | 500 and 2,500 | — | — | — | — | — | "cannot be settled at this budget" |
| Figure 2's caption, "spans zero only at h = 1" | (caption in `scripts/build_paper.py`) | `results/a1_ab_by_horizon.json` | 10,000 | 3 | 400-step | relative-L1 | whole trajectories | cumulative | consistent with the table; the caption named no checkpoint |
| The base-claim contribution bullet | `d1_ratio`, `d1_ratio_h100` | `results/task_d1_threeseed.json` | 10,000 | 3 | 400-step | relative-L1 | — | cumulative | makes no h = 8 statement |

**The plan's lead was wrong.** It suggested the prose described the 2,500-iteration checkpoint. The
0.008 is the same 10,000-iteration checkpoint as the table, with **one seed instead of three**.
Only "0 of 4" is at other checkpoints.

**Resolution: case (a).** Every figure is current, and each is correct for its own setting (seed
count, or checkpoint). None is stale, and none of the source artifacts is superseded. So each
statement now names its setting: the table's checkpoint, the single seed, and the 500- and
2,500-iteration checkpoints, all bound from their artifacts (keys `iters_long`, `iters_main`,
`m23_seed`, `bu_ckpts`). The prose now says what the data show. At h = 8 the advantage is small
and resolves only at 10,000 iterations with three seeds pooled. It never resolves at 500 or 2,500,
nor with one seed. "The advantage is a long-horizon phenomenon" is replaced by "The advantage is
small at the training horizon and large beyond it." M-16's and M-23's verdicts are untouched.

**Left for the user (OUT_OF_SCOPE.md).** Ledger R-42 concludes, from seed 1 alone, that the
out-of-sample h = 8 ambiguity "does not resolve with more training out-of-sample — it is a
sample-size limit". The three-seed estimate at 10,000 iterations resolves it. R-42 remains true as
a single-seed statement, but its interpretation is now contradicted. Whether that needs a
supersession entry is a judgment about the ledger that S3's scope does not cover.

**Guards added** (`scripts/build_paper.py`, registered in `docs/BUILD_CHECKS.template.md`):
- `check_h8_gap_labels`: every §5 sentence with an h = 8 gap key must use the table's key or a
  bound checkpoint key.
- `check_arm_table_captions` (item 2).

Both are in the gate's self-test, which catches 6 of 6.
