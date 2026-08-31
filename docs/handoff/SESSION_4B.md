# Session 4b — front matter, and the first rebuild

**Ran** 2026-08-31. Branch `main`. Follows 4a in the same session. All four 4b exit criteria met.

---

## Title

Retitled to lead with the epistemic term rather than with "neither output", which was true but
soft:

> **Ensemble disagreement is miscalibrated as a scale, by a factor that grows with rollout
> depth: an independent reproduction of a released robotic world model**

The aleatoric σ = 0 result is the *mechanistic* finding and now reads as one — it explains the
second half of the epistemic story rather than sharing the headline.

## Abstract — three findings, and half the numerals

Rewritten to the brief's spine. **369 words (cap 370) and 11 numerals, down from 18** — the
budget was not raised; the abstract carries fewer numbers than before, which was the point.

1. **The quantity the method penalises with is miscalibrated as a scale, by a factor that grows
   with depth.** The h = 1 row does the work: nothing has accumulated, the input is the true
   state, and it is already an order of magnitude out — so this is not accumulated rollout
   error. Then the λ argument: the best constant rescale, fitted and scored on the same data and
   so an upper bound on any constant, grows by a factor of 4 across the rollout.
2. **The base training claim reproduces and the advantage grows with horizon — and at one step
   it reverses.**
3. **The released evaluation understates its own checkpoint.**

Ranking and repair are one sentence each, as the brief specifies.

**The unit switch is fixed.** The old abstract ran "16.22% … deteriorating to 33.4×", moving
from a coverage percentage to a ratio mid-sentence. The miscalibration is now carried in one
unit throughout — the ratio, 8.3× at h = 1 and 33.4× at h = 100 — and coverage is not quoted in
the abstract at all.

## Contributions

The bullet ending "a gap that spans zero at h=1" is gone. In its place, the reversal as its own
contribution:

> **At one step the comparison reverses, and we report it against our own arm.** A second
> pre-registered rule rebuilds the evaluation at a 33-row unit, giving 60 independent units
> where the 400-step unit gives 4. The gap becomes −0.0194 [−0.0310, −0.0093] — it excludes zero
> in favour of **teacher forcing**.

## The first rebuild

`scripts/appendix_g_rules.py` → `paper_numbers.py` → `build_paper.py`, in that order, because
Appendix G's generator had not run since Session 1 and `{{appG_n_rules}}` would otherwise have
stayed at its stale 11.

**Every placeholder resolved.** PAPER.md and PAPER.tex both rebuilt.

### The three drift sources, as they now yield

| source | before | now | behaviour |
|---|---|---|---|
| `{{n_entries}}` | 239 | **244** | placeholder; resolved correctly |
| `{{appG_n_rules}}` | 11 | **15** | placeholder; Appendix G gained four rows |
| `e5_collapse_pct` | +0.10 | **+0.08** | **not a placeholder; did not self-heal** (M-66) |

The §D pending state resolved too: Appendix G reports **15 rules, 15 with a computed lead time**.
Figure 4 still plots its own 8 and the body now says why it is not re-drawn.

## Checks: 49 of 52, and what the three failures are

`check_comparative_claims.py`: **49/52 verified, 52/52 self-test corruptions caught.**

Four failures were found and **three of them were defects in my own new text**, caught by the
checks that exist for exactly that:

- **`horizon-consistency`** flagged two calibration figures that named no horizon — one in the
  new abstract, one in the new §6.2 in-sample sentence. Both now name theirs. This is the defect
  class the paper spends a section on, and it caught me twice in one session.
- **`restatement`** flagged an ambiguous `15` in the new M-63 paragraph, which quoted a 15-point
  threshold, a 15.0% median and a 15% share within one sentence. The paragraph is tightened; the
  median and the explicit share are gone and the verdict claim is unchanged. It is shorter than
  it was, which Session 5 will not object to.

**The three that remain are `cross-artifact-sync`, and they are Session 6's by the brief's own
§4 table.** `README.md`, `MODEL_CARD.md` and `docs/EXTERNAL_READ_BRIEF.md` each assert a
sentence the rewritten abstract no longer contains ("recomputed each build against a corrupted
expectation"). The brief anticipates this exactly — *"cross-artifact-sync | abstract headline
values change | update README + model cards"* — and assigns it to 6.3. Not fixed here.

`ledger_check.py` PASS.

## Exit criteria

| # | criterion | status |
|---|---|---|
| 7 | Title and abstract lead with the epistemic term; three findings; unit switch fixed | met — 369 words, 11 numerals |
| 8 | Contributions updated, including the h=1 reversal | met |
| 9 | First rebuild; placeholders resolve; drift reported | met — table above |
| 10 | `SESSION_4B.md` written, naming Session 5a's first action | met — this file |

---

## Session 5a's exact first action

**5a is appendices only. The body is not touched.** Mechanical, low judgment, and it must end
buildable.

Start by moving Appendix D's machinery to a new `docs/BUILD_CHECKS.md`: the 21-kind registry,
the self-test mechanics, the four checker defects, and the wall-clock-bounded diagnostic
discussion. **Keep in Appendix D** the six failure modes that survived provenance checking and
the two exclusions from the numeric comparison — that list is the part that generalises past
this paper.

Then:

- **Appendix G**: move the quoted rule texts to supplementary **in full**. Nine of them are
  currently truncated mid-sentence with an ellipsis, produced at
  `scripts/appendix_g_rules.py:63`. **Fix it at the generator, not in the prose** — and note the
  count is now 15 rules, so more quotations are affected than when the brief was written.
- **Appendix C**: fix the float placement so figures sit near their first reference.
- **Re-point `kind-count` at the end of 5a**, once Appendix D's enumeration has moved. It
  currently asserts §8's count, Appendix D's enumeration and the checker's registry are one
  number, and it passes at 21; after the move it must read `docs/BUILD_CHECKS.md`. Re-point it,
  do not delete it.

**Do not attempt the body cut in 5a.** §8, the retraction narration and the §6.7 restructure are
5b, and the split exists so that running out of budget mid-cut leaves a buildable paper rather
than a half-trimmed one.

One thing 5b will need and 5a should not disturb: the retraction-cut criterion from
`SESSION_2_ADDENDUM.md` §E — keep a retraction in the body only if it changes how a reader reads
a number that is still in the paper. S-15 and S-12 pass it; most "an earlier draft said" asides
do not.
