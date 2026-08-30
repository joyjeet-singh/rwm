# Session 3 — M-64 discharged, and the 20-seed corroboration qualifies rather than confirms

**Ran** 2026-08-31. Branch `main`. Session 3 under `SESSION_3_ADDENDUM.md`.

All six exit criteria met. **Every pre-registered rule in this project is now discharged.**

---

## A.1 — the free gate, run before any statistic

**PASS: 30 comparisons, 30 bitwise identical, 0 differing** (`results/m64_free_gate.json`).

The first short unit of each cached 400-step rollout is an exact slice — same start row, same
32-row teacher-forced prefix, same deterministic mean feedback — so forecast steps 1..h of the
cache must equal a fresh 32+h unit bitwise. Six model × arena combinations × five horizons were
checked against the Session 2 cache before any short-unit statistic existed. The new rollout
machinery is verified against a known-good side rather than against itself.

## A.3 — M-64 discharged over all five committed horizons: **MOVES**, at one cell

**The counts held both ways at every horizon**, so the measurement did not stop, and M-64's
predictions — written down before the index was built — are exactly what the index produced:

| arena | h=1 | h=8 | h=32 | h=100 | h=128 |
|---|---|---|---|---|---|
| out-of-sample (2 episodes) | 60 | 50 | 30 | **14** | 12 |
| in-sample (8 episodes) | 240 | **199** | 120 | 56 | 48 |
| all ten (10 episodes) | 300 | 249 | 150 | 70 | 60 |

The off-by-one the rule predicted appears where it said it would: the in-sample arena contains
ep0 and gives **199** at h=8, being 24 + 7×25. Out-of-sample gives **14** at h=100 against the
present 4 — the figure M-64 wrote down in advance.

**The move: §5's A/B gap at h=1, out-of-sample.** At 400 steps with n=4 the gap is −0.0128,
[−0.0329, +0.0013], spanning zero. At 32+1 with n=60 it is −0.0194, [−0.0310, −0.0093],
excluding zero. The sign is unchanged and negative, so **teacher forcing beats autoregressive
training at one step**, now resolved rather than merely visible. Robust to clustering: the
episode-level footnote interval is [−0.0372, −0.0016] and also excludes zero.

This **narrows §5 against us**. §5 already reported the direction at h=1 — 0.91×, 3 of 10
episodes, the floor beating both arms — and called the advantage a long-horizon phenomenon.
The extra power converts "not better at one step" into "worse at one step". The 400-step figure
is not withdrawn; both appear, each naming its unit, arena and `n_independent`.

**What did not move, and where the extra units help.** §6.7's paired difference excludes zero at
every horizon at both units, with every short-unit interval narrower:

| h | 400-step, n=20 | short unit | n |
|---|---|---|---|
| 8 | [+0.2409, +0.6794] | [+0.5899, +0.7585] | 249 |
| 32 | [+0.2983, +0.6740] | [+0.3426, +0.6155] | 150 |
| 100 | [+0.0339, +0.3621] | [+0.1550, +0.3836] | 70 |
| 128 | [+0.0107, +0.3242] | [+0.1480, +0.3512] | 60 |

**h=128 is the cell §6.7 calls its weakest** — "+0.011 is the smallest lower bound in the table
and we would not rest anything on that horizon alone". At 60 units its lower bound is +0.148.

**One self-correction, recorded because the rule's own requirement caught it.** A first pass
compared the all-ten 400-step paired difference against the *out-of-sample* short-unit figure
and reported two further moves at h=100 and h=128. Those were an arena change wearing a unit
change's clothes. Every comparison is now matched to the artifact holding its own 400-step
figure — cell C against `a1_ab_by_horizon.json` (out-of-sample), cell B against
`task_d_nind20.json` (all ten) — and the spurious moves disappear.

## A.2 — episode-level demoted to a footnote

Computed for every figure and stored in `footnote_episode_level` beside it. M-62 returned NO
MOVE, so it corroborates rather than competes, and it is not a second column in the paper.

## A.5 — the 20-seed corroboration **qualifies rather than confirms**

M-50's keys are intact: `config`, `arms` and `verdict` are bit-identical to the committed
artifact, `config.seeds` is still `[0, 1, 2]`, and the verdict is still OBJECTIVE-DRIVEN. The
20-seed figures live in a new `corroboration_20_seeds` block beside them.

**But the 20-seed arms would return MIXED, not OBJECTIVE-DRIVEN, and saying otherwise would be
false.** The `gaussian_nll` arm's `tracking_above_threshold` flag flips: the criterion is
all-seeds, `np.all(|slope| > slope_threshold)`, and over twenty seeds the recovering arm's
slopes run from 0.0004 to 0.354 with a median of 0.0037, with **9 of 20 below the 0.00309
threshold**. The three seeds M-50 drew all cleared it.

**M-50's verdict is unchanged and stays as returned over its own three seeds** — brief §2 rule 4,
the same logic that kept M-43's denominator at four horizons. What changes is how the
corroboration reads. M-50 wrote, before these runs existed, that *"the recovering arm is itself
seed-variable at this training budget, so the CONTRAST is what this experiment establishes, not
the magnitude of the recovery."* Twenty seeds confirm that warning more sharply than three
could. The contrast is untouched — `mse` stays collapsed and non-tracking, `gaussian_nll` stays
`recovered`, at both seed counts — and §6.3's mechanism claim rests on the contrast.

**Session 4 must not report this as clean corroboration.**

### One incidental staleness, resolved by the regeneration

`e5_synthetic_sigma.json` carried `thresholds.span_floor = null` while its source
`e5_sigma_dilution.json` has `1.01`; git confirms the synthetic artifact predates M-61's fix to
the dilution artifact. **No published number is affected** — `paper_numbers.py:344` reads
`e5s_span_floor` from the dilution artifact, not this one, so the stale copy was a carried
duplicate nothing reads. Regenerating brought it into sync. Recorded here rather than in
`ANOMALIES.md` because it is neither open nor out of scope: it was found inside A.5's own task
and closed by it.

---

## Exit criteria

| # | criterion | status |
|---|---|---|
| 1 | Free gate run before any statistic; recorded either way | met — PASS, 30/30 |
| 2 | M-64 discharged over all five committed horizons | met — MOVES at one cell |
| 3 | Episode-level computed and stored as a footnote field | met |
| 4 | 3.2 at 20 seeds; M-50's keys and verdict intact | met — and the corroboration is qualified |
| 5 | Paper not rebuilt | met — `build_paper.py` never run |
| 6 | Handoff naming Session 4's first action, §6.6 flagged as a rewrite | met — this file |

`ledger_check.py` PASS. **Pre-registered rules not yet discharged: 0.**

### Drift on the next `--force`

1. `{{n_entries}}` → 244. Placeholder; resolves correctly.
2. `{{appG_n_rules}}` → 15. Placeholder. Appendix G gains four rows.
3. **`e5_collapse_ens1` / `e5_collapse_pct` (M-66).** Not a placeholder, **does not self-heal**.
4. **`thresholds.span_floor` in `e5_synthetic_sigma.json`** — now corrected; affects nothing published.
5. Lead times: 15 rules now all discharged, so the §D pending state resolves. It should settle at
   15 rules, 15 lead times, 14 positive and 1 negative.

---

## Session 4's exact first action

**Read `docs/handoff/SESSION_2B.md` and this file, then start with §6.6 — and budget it as a
rewrite, not an insertion.**

§6.6 currently says the out-of-sample arena "cannot reject at any effect size whatever", because
4 independent trajectories admit a smallest attainable P of 0.04167 against a Holm threshold of
0.001667. **M-64 changes that at h ≤ 128**: the out-of-sample arena now admits 60, 50, 30, 14 and
12 units at h = 1, 8, 32, 100 and 128. That paragraph is rewritten rather than appended to, and
§11's "resolving this needs more episodes than the released dataset contains, not a better test"
must be revisited alongside it — that sentence is now true only at h = 368.

### The allocation, decided in the addendum rather than during the writing

| item | where | budget |
|---|---|---|
| M-62 | one paragraph in §6.2 or §3.1 — verdict, the 27% width change, no over-reading | ≤ 6 lines |
| M-63 | one paragraph in §6.2, framed as corroborating §6.3's mechanism | ≤ 8 lines |
| M-65 | one sentence on the nominal in §3.1; the oracle-growth statistic in §6.2's λ paragraph | ≤ 4 lines |
| M-66 | one clause narrowing Appendix B's claim | ≤ 3 lines |
| M-64 | table in §6.6, subset per A.3 | ≤ 12 lines |
| the class audit | ledger only | 0 |

**No new subsections. No new appendix.** The paper has gained five ledger entries while trying
to lose ten pages.

**On which cells to print.** M-64 is discharged over all five horizons and the artifact holds all
five. The paper prints h = 1, 8 and 100 — h=1 and h=100 carry the argument and §6.6 locates the
strongest short-horizon effect at h=8. h = 32 and h = 128 stay in the artifact. **State the
distinction between the set a rule is discharged over and the cells printed once in the body**, or
it reads as selective reporting.

**Two results Session 4 should not soften.** §5's h=1 gap now excludes zero *against* Arm A, and
the 20-seed synthetic corroboration returns MIXED. Both cut against this paper's own arms, and
both are load-bearing for its epistemic argument.

### Session 5 is split (addendum §D)

- **5a — appendices only.** Appendix D → `docs/BUILD_CHECKS.md`; Appendix G quotations →
  supplementary in full; Appendix C figure placement. Re-point `kind-count` at the end. Body
  untouched, mechanical, low judgment.
- **5b — body only.** §8 trim, retraction narration to ≤ 4 by the `SESSION_2_ADDENDUM.md` §E
  criterion, §6.7 restructure. High judgment, contained scope.

Each half ends buildable. Session 6 is unchanged and follows 5b.
