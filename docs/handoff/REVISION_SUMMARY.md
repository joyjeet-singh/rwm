# Revision summary

What the TMLR revision changed, from `REVISION_BRIEF.md` through Sessions 1–6. Session 7 is
deferred until after submission; Session 8 is submission mechanics.

**Build status: compile PASSES, 40 pages, 0 errors, 0 overfull boxes. 54/54 comparative claims,
54/54 self-test corruptions caught. Submission gate 7/7 with one check NOT RUN.
`ledger_check` PASS.**

---

## Pages

| point | pages |
|---|---|
| before the revision | 42 |
| after Session 4 added the new results | 44 |
| after 5a, appendices | 41 |
| after 5b, body | **40** |

The brief's ≤ 22 target was withdrawn in `SESSION_5_ADDENDUM.md` §A and the ~34 target in
`SESSION_5B_ADDENDUM.md` §A. What governs is the rule that replaced them: **if a cut would
remove a result, a control or a caveat, leave the pages.** Appendix D stopped at 109 lines
rather than reach ≤ 1 page for exactly that reason, and it is reported as missed rather than
met by cutting evidence.

## Verdicts

Four rules were pre-registered in Session 1 before any of their data existed, and one more
entry and one open item followed.

| rule | verdict | what it settles |
|---|---|---|
| `M-62` clustering unit | **NO MOVE** | no verdict changes when the bootstrap resamples episodes rather than 400-step trajectories |
| `M-63` per-dimension coverage | **UNIFORM** | the h=1 coverage failure is a property of the whole state vector, not a few channels |
| `M-64` shorter units | **MOVES**, at one cell | §5's h=1 gap |
| `M-65` Gaussian nominal | **NOT HEAVY-TAILED** in all 48 model × horizon cells | the shortfall is scale, not tail |
| `M-66` | the Appendix B glob defect in a second script | two published values moved |
| `M-67` | **OPEN** | the Hugging Face card is not updated |

## The two results that run against this paper's own arms

Both are reported at full strength and neither was softened.

**§5's h=1 gap now excludes zero against our own arm.** At the 400-step unit with n=4 it was
−0.0128 [−0.0329, +0.0013], spanning zero. At the 33-row unit with n=60 it is
−0.0194 [−0.0310, −0.0093], excluding zero **in favour of teacher forcing**. The h=1 result is
not "no difference" but *autoregressive training is worse at one step*. It is in the
contributions list, not buried in a table.

**The 20-seed synthetic corroboration returns MIXED, not OBJECTIVE-DRIVEN.** `M-50`'s verdict
stands as returned over its own three seeds and is not re-opened. But 11 of 20 seeds clear the
slope threshold where all 3 did, so the corroboration qualifies rather than confirms — which is
what `M-50` predicted in its own committed text before the runs existed. The contrast between
objectives is intact, so the abstract's claim does not move.

## Claims narrowed

- **§5's h=1 row** — narrowed against us, as above. The 400-step figure is not withdrawn; both
  units appear, each naming its unit, arena and `n_independent`.
- **§6.6's design claim** — "cannot reject at any effect size whatever" is now scoped to the
  400-step unit and to h = 368. At h ≤ 128 the same two episodes admit 60/50/30/14/12 units,
  and the paper says plainly that the permutation family was **not** re-run there.
- **§11** — "resolving this needs more episodes than the released dataset contains" is scoped
  the same way.
- **§6.3** — "every seed's slope clears the threshold" is now "every one of the three `M-50` was
  discharged over", with the 20-seed qualification beside it.
- **Appendix B** — the width-predicate fix reached `paper_numbers.py` and `paper_figures.py` and
  **not every script**; a second unguarded glob survived until this revision found it.
- **§8** — its closing sentence pointed at Appendix D for material that had moved. Re-pointed.

## New artifacts

| artifact | what it holds |
|---|---|
| `results/m62_episode_clustering.json` | both cluster levels for every cell `M-62` names |
| `results/m63_per_dimension_coverage.json` | 45 per-dimension coverages, two arenas, two horizons |
| `results/m64_short_units.json` | the short-unit index and every re-run cell |
| `results/m64_free_gate.json` | 30 bitwise comparisons of the first short unit against the cache |
| `results/m65_gaussian_nominal.json` | the oracle rescale for 48 model × horizon cells |
| `results/m62_65_cache_gate.json` | 327 published figures recomputed from the per-triple cache |
| `results/insample_framing.json` | 2.4's arena, as substitutable keys |
| `results/input_set_audit.json` | 21 pattern-based input discoveries, classified |
| `results/check_scope_audit.json` | 22 check kinds classified by how they select input |
| `results/xref_sweep.json` | 60 pointers verified against what they now point at |
| `docs/BUILD_CHECKS.md` | the registry, the self-test, the checker's own defects |
| `docs/APPENDIX_G_RULES.md` | all 15 rules in full, no ellipsis |

`e5_synthetic_sigma.json` gained a 20-seed corroboration block beside its untouched 3-seed keys.

## The failing gate

**It still fails and still says where.** `part_f_gate` check 4 requires that *no* regenerated
value differ. **178 do**, out of 8,186 compared across 47 regenerated files, with 7,981 bitwise
identical (97.50%) and 27 equal to tolerance. That is 0.90% of the 905,391 numeric values under
`results/` — the rest are carried in by a clean clone and prove nothing about reproduction.

**The 178 is unchanged by this revision.** No tolerance was applied and none is proposed.

The gate's clean-clone check reads **NOT RUN** rather than FAIL, because it needs a clone
(`CLONE_RESULTS`) and none was supplied. That is the honest state: the check is armed, its
published figure stands, and running it against a fresh clone is Session 8's.

## What the machinery caught, in text written during the revision

Worth recording, because it is the argument §8 makes about itself:

- **two `horizon-consistency` failures** — a calibration figure in the rewritten abstract and
  another in a new §6.2 paragraph, each quoted without the horizon it was measured at.
- **one `restatement` failure** — a new paragraph quoted a 15-point threshold, a 15.0% median
  and a 15% share in one sentence.
- **two `unit-consistency` classes** — the kind added in 6.2 found 18 figures naming no unit; 8
  survived scoping to the paragraph and were fixed.
- **two check-coverage gaps** — `retraction-consistency` and then `count-consistency`, each
  silently losing a surface when text moved.
- **one anonymisation leak** — a ledger entry written in Session 6 quoted a URL containing the
  author's username, and the bundle scanner refused to write the ZIP.
- **seven artifacts with no pipeline stage** — every one feeding `paper_numbers.json`.
- **an appendix-letter mismatch** — retiring Appendix C left document order `ABDEFGHI` against
  LaTeX's `ABCDEFGH`, so every appendix reference past B landed on the wrong appendix in the
  PDF. Caught by the gate, not by a reader.
