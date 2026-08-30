# Session 2 — half one complete, stopped at the gate before half two

**Ran** 2026-08-30. Commits `c19ed8b`, `2d8e17d`, and this note. Branch `main`.

Session 2 under `REVISION_BRIEF.md` as amended by `SESSION_2_ADDENDUM.md`. The addendum
splits the session in two with a hard stop between them. **Half one is complete and its
gate passed. Half two was not started**, because building the last cache family surfaced
a failure the addendum says to stop on: `A-01` in `docs/handoff/ANOMALIES.md`.

---

## What ran

| step | outcome |
|---|---|
| Determinism baseline on `task_d_nind20.py` before any edit | reproduces `task_d_nind20.json` byte-identically, md5 `50db6beb` |
| Cache path added to `task_d_nind20.py`, flag off | still `50db6beb` |
| Same, flag on | still `50db6beb`, cache written |
| Cache path added to `task1_calibration.py`, flag off | still `30dfdbfc` |
| Same, flag on | still `30dfdbfc`, 10 objects written |
| Cache path added to `task_d3_ens5.py`, **flag off** | **artifact changed** — see `A-01` |
| Differential gate | **PASS** — 255 figures, 249 bitwise, 6 traced, 0 unexplained |

## Artifacts

- `src/per_triple_cache.py` — the cache. Signed residuals; aleatoric and epistemic kept
  apart; residual space recorded rather than assumed; upstream pins embedded.
- `scripts/gate_per_triple.py` — the differential gate.
- `results/m62_65_cache_gate.json` — the gate result, recorded either way as §F.2 requires.
- `cache/` — 11 objects, gitignored. Not under `results/`, so the 905,391 denominator
  §8 and Appendix D cite is untouched.

## The gate, as returned

**255 figures recomputed from the cache, 249 bitwise identical, 6 traced to reduction
order, 0 unexplained. No tolerance applied anywhere.**

It did not pass first time and the failures were the useful part.

1. **14 figures differed, all routed through the summed epistemic scalar.** Traced: the
   45-term sum is performed by torch in float32 at `src/score_reference.py:119`, not by
   numpy. The per-dimension term it sums is `:118`, which is what the cache stores.
   Re-summing identical values in numpy reduces in a different order. Reconstructing the
   sum the way the model defines it reproduces all 14 bitwise.
2. **§6.2's family differed on every figure.** Two causes, both traced. The producer
   keeps float32 and reduces in float32 while the cache stores float64 — a lossless
   widening, verified by a bit-identical round trip — so reducing in the producer's dtype
   recovered `sigma_mean` and every coverage cell. What remained was stranger: identical
   bytes, different means. The producer's concatenated residual is **non-contiguous** and
   numpy reduces it by a different path. Demonstrated in-process: `pe.tobytes() ==
   pc.tobytes()` is True while `pe.mean() != pe.copy().mean()`, and `pe.copy().mean()`
   is the cache's value.

Because a statistic-level comparison cannot settle that family, the gate now checks the
property that actually matters and checks it exactly: it re-runs the rollouts and
compares **arrays**. 20 compared, 20 bitwise identical. The 6 remaining statistic
differences are recorded as traced-to-reduction-order and are explained *only* by that
array check passing — if any array differed they would be unexplained and the gate fails.

## Why half two did not start

Adding the cache path to `scripts/task_d3_ens5.py` and running it **with the flag off**
changed its committed artifact. That is not possible from a guarded additive edit, and it
is not. The script does not reproduce its own artifact: `task_d3_ens5.py:299` globs
`results/step5_armA_seed?.json` for its ensemble-size-1 comparison, that glob matched
three files when the artifact was written and matches five now, and seeds 3 and 4 arrived
in `d88a106` — §6.10's independent-ensemble work. Two values move, and the paper cites
both (`paper_numbers.py:715-716`).

Addendum §B: a gate failure for any reason other than a traced reduction-order difference
stops the session and does not proceed to 2.1. This is not reduction order — the input
set changed. Full write-up, blast radius and suggested resolution in
`docs/handoff/ANOMALIES.md` as `A-01`.

Everything was restored: `scripts/task_d3_ens5.py` and `results/task_d3_ens5.json` are
back at their committed state (`edbfee88`), and no ens5 cache object was written. The
prepared patch for that script is kept at `scratchpad/ens5_patched.py`.

## Exit criteria, as returned

| # | criterion | status |
|---|---|---|
| 1 | Per-triple cache in `cache/`, gitignored, every §B field present | **met**, 11 objects |
| 2 | Gate passed bitwise, or difference traced with a `file:line`; recorded either way | **met** — PASS, recorded in `results/m62_65_cache_gate.json` |
| 3 | `results/` count unchanged except new derived artifacts | **met** — one added, `m62_65_cache_gate.json`; no existing artifact altered |
| 4 | M-62, M-63, M-65 discharged | **not met** — half two blocked by `A-01` |
| 5 | 2.4's arena confirmed and stored as a substitutable key | **not met** — half two |
| 6 | Paper not rebuilt | **met** — `build_paper.py` never run |
| 7 | Handoff naming the first action | **met** — this file |

Four of seven met. The three unmet are all half two and all sit behind `A-01`.

## Coverage the cache already has

| model | arena | n_ind | seeds | epistemic |
|---|---|---|---|---|
| `released_ckpt_ens5` | all ten episodes | 20 | — | yes |
| `released_ckpt_ens5` | out-of-sample | 4 | — | no, NaN (`rollout_full`) |
| `armA_faithful_mse` | out-of-sample | 4 | 0,1,2 | no, NaN |
| `armA_corrected_nll` | out-of-sample | 4 | 0,1,2 | no, NaN |
| `armB_teacher_forced` | out-of-sample | 4 | 0,1,2 | no, NaN |

Missing: `armA_ens5` out-of-sample, which is `M-63`'s second arena. Blocked by `A-01`.

## Exact first action for Session 3

**Resolve `A-01` first — do not start 2.1 or 3.1 before it is settled.** It is a decision,
not a repair: pin `task_d3_ens5.py`'s ensemble-size-1 comparison to an explicit seed list
rather than a glob, and decide on the record whether that list is the three seeds the
artifact was discharged over or the five that now exist. `M-43` was discharged over that
artifact, so brief §1 applies — the choice gets a ledger entry, and if the two published
figures move, the body says so rather than letting a rebuild change them quietly.

Then, in order:

```
git -C rwm_repro log --oneline -3
python scripts/gate_per_triple.py
```

The gate must still return PASS on the two committed families before anything is built on
top of them. Then apply `scratchpad/ens5_patched.py` to add the third family, gate it,
and only then start 2.1.

Two things already established that half two should not rediscover:

- **`M-62`'s cells are reachable.** §5's per-trajectory values are already in
  `results/a1_ab_by_horizon.json` as `gap_per_trajectory`; §6.7's episode map is in
  `results/a2_trajectory_level_control.json` as `design/trajectory_episode`; §6.10's are
  in `results/r2_independent_ensemble.json`. Only §6.2's needed the cache, and it has it.
- **The scalar penalty reconstructs exactly** from the cached per-dimension epistemic
  term, because `epi_s` is `means.std(0).sum(-1)` and `epi` is `means.std(0)`
  (`src/score_reference.py:118-119`) — summed in torch, per the gate's own trace.

Read `M-62`, `M-63` and `M-65` in `FINDINGS_LEDGER.md` before computing anything. Every
threshold, arena restriction and refusal-to-report is fixed there.
