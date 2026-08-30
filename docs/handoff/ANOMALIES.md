# ANOMALIES

Things found outside the current session's task list. Per `REVISION_BRIEF.md` §2 rule 8
these are logged and **not acted on**.

---

## A-01 — `results/task_d3_ens5.json` no longer reproduces from its own script, and two published numbers move

**Found** Session 2, half one, 2026-08-30, while adding the per-triple cache path to
`scripts/task_d3_ens5.py`. **Status** OPEN. **Not fixed** — the Session 2 addendum §B
requires the session to stop here rather than repair it.

### What happens

Running `scripts/task_d3_ens5.py` unmodified rewrites `results/task_d3_ens5.json` with
two values different from the committed ones, and two extra array entries:

| key | committed | on re-run |
|---|---|---|
| `collapse/ens1_mean` | `-9.36169189585799e-05` | `-9.360240346686157e-05` |
| `collapse/relative_difference` | `0.0009670032949881033` | `0.0008120771963740544` |
| `collapse/ens1_slopes` | 3 entries | **5 entries** |

507 flattened keys become 509. Everything else is identical.

### Why

`scripts/task_d3_ens5.py:299` discovers its ensemble-size-1 comparison set by globbing
the results directory rather than by naming the seeds:

```python
e1 = [... for f in sorted(glob.glob("results/step5_armA_seed?.json"))]
```

When the artifact was written that glob matched three files, seeds 0–2. It now matches
five. `results/step5_armA_seed3.json` and `results/step5_armA_seed4.json` were added in
commit `d88a106` — "Phase 2: M-44 returns MECHANISM SUPPORTED" — which is §6.10's
independent-ensemble work, and which says in the paper's own words that Arm A at
ensemble size 1 "already existed at seeds 0, 1 and 2; we added two more".

So the artifact is not wrong about anything it measured. Its **input set grew
underneath it**, and nothing recomputed it. This is the same shape as `M-61`: one
artifact, two states, and only a re-run can see the difference.

### Blast radius — two numbers the paper prints

Both changed keys are cited, so this is not confined to an intermediate:

- `scripts/paper_numbers.py:715` → `e5_collapse_ens1` from `collapse/ens1_mean`
- `scripts/paper_numbers.py:716` → `e5_collapse_pct` from `100 × collapse/relative_difference`

On the next `./reproduce.sh --quick --force`, `e5_collapse_pct` moves from about
`+0.10%` to about `+0.08%`. This is a **third** source of paper drift, and it is not
one of the two the addendum's §D says to expect. Unlike `{{n_entries}}` and
`{{appG_n_rules}}`, which are placeholders that resolve correctly at build time and
settle on their own, this one is a stale *input set* and does not self-heal.

### Why the session stopped rather than fixing it

Addendum §B: a gate failure for any reason other than a traced reduction-order
difference stops the session. This is not reduction order — the arithmetic is
identical and the number of inputs changed. Three further reasons not to touch it here:

1. It is `M-43`'s discharging artifact. Brief §1 forbids re-anchoring, re-scoping or
   re-denominating a discharged rule, and silently recomputing the artifact a rule was
   discharged over is exactly that.
2. Whether the comparison *should* be 3 seeds or 5 is a real question with a real
   answer, and it is not this session's to decide. Three keeps the artifact as
   discharged; five uses all the evidence that now exists. Either way the change is
   reportable, and picking one quietly would be the `S-12` failure mode.
3. Fixing it changes two published numbers, which is Session 4 or Session 6 work with
   the ledger entry that has to accompany it.

### What it blocks

The ensemble-5 out-of-sample cache, which `M-63` names as its second arena and which
`M-65` needs for those arms. There is no trustworthy known-good artifact to gate that
family against until this is resolved.

It does **not** affect the two families already gated and committed: the released
checkpoint over all ten episodes (`results/task_d_nind20.json`) and §6.2's four models
out-of-sample (`results/task1_calibration.json`). Both reproduce byte-identically from
their own scripts, verified this session, before and after the cache path was added.

### Suggested resolution, for whoever picks it up

Decide the seed set explicitly and name it in the script rather than globbing, so the
artifact cannot drift again. Record which set was chosen and why, and if the published
figures move, say so in the body rather than letting a rebuild change them silently.
The prepared cache patch for this script is at
`scratchpad/ens5_patched.py` from the Session 2 run and can be reapplied once the
comparison set is pinned.
