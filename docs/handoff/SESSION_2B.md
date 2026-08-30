# Session 2B — A-01 settled, its class audited, half two complete

**Ran** 2026-08-31. Branch `main`. Commits `88fb1ec` (part A) and this note's commit.

Session 2B under `SESSION_2B_ADDENDUM.md`. All eight exit criteria met. `M-62`, `M-63` and
`M-65` are discharged; `M-64` remains open and is Session 3's.

---

## A — A-01 settled

**Reframed, not rediscovered.** Appendix B already records this defect class: the collapse
family is selected by the recorded width field *"rather than by filename — it did neither
until the first capacity-matched run walked into the family through a glob"*. That fix
landed in `paper_numbers.py` (the `_width` predicate) and `paper_figures.py`. It never
reached `task_d3_ens5.py:299`. `M-66` says that, not "a glob matched more files".

**The confirmation ran before anything changed.** Every moving key sits under `collapse/`,
and **all 187 of `M-43`'s keys are frozen**, checked key by key. The stop condition was set
in advance and was not triggered.

**The decision.** The ens1 comparison is now an explicit five-seed list — 0, 1, 2, 3, 4 —
with each member asserted at 2,500 iterations and the released width by the same predicate
`paper_numbers.py` uses. Holding at three would need a principle, and "that is what existed
when the file was written" is an accident of timing.

**The disclosure is first in the entry, not last.** The choice that follows the paper's own
principle also *improves* the number: `e5_collapse_pct` moves +0.10% → +0.08%, making the
two collapse rates look **more** nearly identical, which is what §6.3 claims. A reader who
finds that independently is entitled to ask whether the principle was chosen for the
outcome. Disclosure is the defence.

**The class, not the instance.** `scripts/input_set_audit.py` sweeps `scripts/` and `src/`
for `glob`/`listdir`/`walk` discovery: **21 hits, 20 open population, 1 frozen, 0
unclassified**, written to `results/input_set_audit.json` with a `file:line` and reason for
each. An unclassified hit fails the script rather than passing silently. The run-artifact
globs elsewhere are open because they are *guarded* to the released width.

One observation logged without a fix, per A.3's "fix only what affects a published number":
`paper_numbers.py:1592`'s run-inventory table omits width from its row key, so M-49's
width-124 runs share a row with released-width runs of the same shape. No number it
produces is wrong — `run_total` is 31 and matches Appendix B.

**Input sets are now data.** `task_d3_ens5.json` records `ens1_input_files`, `ens1_seeds`,
`ens1_selection` and `released_width`. A stale set now shows up in a `reproduce.sh` diff on
its own. **No check kind was added**, per A.4.

---

## B — half two

**2.1 was never blocked by A-01.** `M-62`'s committed cell list does not name ens5. The
previous session's exit report was wrong about that and the addendum was right to say so.

### M-62 — **NO MOVE**

| statistic | trajectory level, n=20 | episode level, n=10 | width | moved |
|---|---|---|---|---|
| pooled r | [+0.5446, +0.6940] | [+0.5254, +0.7157] | ×1.27 | no |
| r_dd | [+0.3155, +0.5749] | [+0.3197, +0.5730] | ×0.98 | no |

Both still exclude zero. **The episode-level interval on `r_dd` is marginally narrower, not
wider** — a coarser cluster level is not guaranteed to widen an interval, and here it does
not. The other four cells returned what the rule said in advance: cells 1, 2 and 4 are
NOT INFORMATIVE at n=2 with their full three-value distributions printed rather than a
percentile interval; cell 5 is NOT BOOTSTRAPPABLE at n=1 per direction.

### M-63 — **UNIFORM**

Governing arena, released checkpoint, all ten episodes, h=1, n=20: IQR **10.00 points**
(threshold 15), pooled 16.22% inside it. The five worst dimensions carry only **14.6%** of
the shortfall, well under the half that would make it CONCENTRATED. **The h=1 coverage
failure is a property of the whole state vector, not of a few channels.**

Quantisation is 5.00 points, so the reading is coarse by construction — stated in advance.
The IQR test was applied only to this arena; the ensemble-5 distribution is descriptive
only, as committed. Overlap with `R-29`'s seven floor-losing dimensions is `v_z`, `w_y` at
h=1 and `g_x`, `g_y`, `w_x` at h=100, reported as suggestive with no P-value.

### M-65 — **NOT HEAVY-TAILED, in all 48 model × horizon cells**

15 cells inside the committed ±5-point band, 33 above it, **zero below**. Under an oracle
rescale coverage lands at or above 68.27% everywhere. So the Gaussian nominal is defensible
and the paper's attribution of the shortfall to scale rather than shape is a measurement
rather than an assumption.

**The oracle constant grows with horizon** — about 10.4 at h=1 to 43.2 at h=368 on the
released checkpoint's epistemic term. Because it is fitted and scored on the same data that
is an *upper bound* on what any constant rescale could achieve, so no single λ repairs a
quantity whose required constant moves by a factor of four across the rollout. The rule's
scoping guard is honoured: this is a verdict about the Gaussian nominal, and citing the
constant inside the λ argument is a second use of one measurement, not a re-scoping.

### 2.4 — in-sample framing

No computation. `results/insample_framing.json` records substitutable keys: the arena is all
ten episodes, **10 of 10 of which the released checkpoint trained on**, so `fully_in_sample`
is true. The h=1 epistemic row is 8.30× out with 16.22% coverage. Direction of bias: toward
better calibration.

---

## The gate

Re-run over all three families after the ens5 regeneration: **327 figures, 321 bitwise
identical, 6 traced to reduction order, 0 unexplained.** Array-level check 20 of 20 bitwise.
No tolerance applied anywhere.

An unplanned cross-check fell out of half two: every pooled figure the new scripts
recomputed from the cache reproduces the paper exactly — 16.22%, 4.61%, 35.93%, 8.19% for
coverage, and every ρ in `M-65`'s table (8.3, 15.1, 22.6, 33.4, 34.2, 34.4; 1,827.3 through
20,668.6). That is independent of the gate and agrees with it.

---

## Exit criteria

| # | criterion | status |
|---|---|---|
| 1 | A-01 reframed as an instance of the Appendix B class | met — `M-66` |
| 2 | M-43 frozen; ens1 pinned to five; direction-of-benefit disclosed | met — 187 keys frozen, disclosure first in the entry |
| 3 | `input_set_audit.json` written, every hit classified, frozen hits carry a ledger entry | met — 21 hits, 1 frozen, `M-66` |
| 4 | Artifacts record input file lists; no new check kind | met |
| 5 | Ens5 artifact and cache regenerated; gate re-run and passed | met — 327/321/6/0 |
| 6 | Half two complete; M-62, M-63, M-65 discharged; 2.4 stored | met |
| 7 | Paper not rebuilt; three drift sources named | met — see below |
| 8 | `SESSION_2B.md` written naming Session 3's first action | met — this file |

### The three drift sources

`build_paper.py` was not run. On the next `--force`:

1. `{{n_entries}}` 239 → **244** (`M-66` added one more). A placeholder; resolves correctly;
   moves every session and settles at Session 6.
2. `{{appG_n_rules}}` 11 → 15. Same; a placeholder.
3. **`e5_collapse_ens1` and `e5_collapse_pct` — A-01's.** Not a placeholder problem and
   **does not self-heal**: the input set was stale and is now pinned. Session 4 must say so
   in the body rather than letting a rebuild change the numbers silently.

A fourth, noted in `SESSION_2_ADDENDUM.md` §D and still true: between the first discharge
here and `M-64`'s in Session 3 there are 15 rules with fewer than 15 lead times. The
generator must represent that pending state explicitly rather than emitting a blank or a
zero. It settles at 15 rules, 15 lead times, 14 positive and 1 negative.

---

## Exact first action for Session 3

Build `M-64`'s short units — and **take the free gate the addendum's §C identifies before
computing any short-unit statistic.**

The first short unit of each cached 400-step rollout is an exact slice: same start row, same
32-row teacher-forced prefix, same deterministic mean feedback. So steps 1..h of the cache
must equal a fresh 32+h unit at that row, **bitwise**. That is a differential gate on the
new rollout invocations with the cache as the known-good side, and it costs nothing.

```
python scripts/gate_per_triple.py
```

must return PASS first. Then build the short-unit index, gate the first unit of each
trajectory against the cache, and only then compute. Same stop condition as half one: an
unexplained difference stops the session.

Two things already settled that Session 3 should not rediscover:

- **The full short-unit set cannot be cut from the cached rollouts.** Only the *first* unit
  of each is an exact slice. `rollout_full` teacher-forces to `start_step` then runs
  autoregressively (`src/score_reference.py:165-166`), so the second and later units start
  inside the long rollout's autoregressive region where a fresh unit would teacher-force
  from ground truth. New rollout invocations are needed — same code, new arguments, new
  cache objects keyed by `unit_length`.
- **`M-64` must report at both clustering levels**, per the addendum's §C. That is free: the
  episode map is on every cache object, and `M-62` has now returned NO MOVE at the
  400-step unit, so the short-unit comparison has a baseline to sit against. This is a
  companion reading of `M-64`, not a discharge of `M-62` over new cells — `M-62`'s cells are
  named in its own text and short units are not among them.
