<!-- GENERATED FILE — do not edit. Edit docs/BUILD_CHECKS.template.md and run:
     python scripts/build_paper.py -->

# Build checks — the registry, the self-test, and what it caught in itself

Supplementary to the paper's Appendix D, which keeps the part that generalises: the failure
modes the checks were built for, and the exclusions from the numeric comparison. This carries
the machinery.

Moved here in the revision that cut the paper from 44 pages, on the grounds that a reader
deciding whether to trust the numbers needs the failure modes and the exclusions, and a reader
wanting to run or extend the checks needs what is below. Nothing was deleted.

This file is GENERATED from `docs/BUILD_CHECKS.template.md` by `scripts/build_paper.py`,
from the same `results/paper_numbers.json` the paper is built from. A figure quoted here
therefore cannot disagree with the one the paper prints, and the `kind-count` check reads
the enumeration below to assert exactly that.

---

## The check kinds and the self-test

**The check kinds.** `scripts/check_comparative_claims.py` verifies 52 claims across
21 kinds: *abstract-budget* (the abstract stays inside its word and numeral budget), *arithmetic* (a stated total equals the sum of its stated parts), *cell* (a k-of-45 count is the arena and horizon the text names), *compare* (a stated ordering between two scalars), *count-consistency* (one count asserted in several places, in words, numerals or numeric-string variants, agrees everywhere), *count-dependence* (a clean k-of-k count carries an interval or a not-independent note), *cross-artifact-sync* (the README and model card carry the paper's headline values), *extremum* (a named cell is the max or min of its family), *frequency-consistency* (a frequency stated in words -- "at every horizon", "at exactly one place" -- matches a count recomputed from the artifacts), *horizon-consistency* (every horizon-indexed figure in the prose names its horizon, and names the one its artifact cell came from), *horizon-forbidden* (a withdrawn horizon label appears nowhere in the paper), *horizon-label* (a phrase naming a horizon resolves to the horizon the artifact says it is, and the numbers beside it are that horizon's), *interval-required* (a quoted ratio or coverage is accompanied by its interval), *kind-count* (the number of kinds section 8 claims, appendix D enumerates and the checker registers are one number), *orders* (a stated count of orders of magnitude matches `round(log10(ratio))`, or a ratio quoted directly appears in the sentence that quotes it), *overlap* (two intervals do or do not overlap), *relvar* (a stated ratio of relative variabilities), *restatement* (no sentence restates a quantity another section owns -- no numeral is typed into the slot a substituted one fills elsewhere, and no section prints two different quantities as the same numeral), *retraction-consistency* (a claim the ledger marks superseded is asserted nowhere reader-facing), *scope-consistency* (a universal quantifier is checked against the set it quantifies over), and *sign* (a stated rise or fall matches the direction of the difference).

That list is generated from the checker's own registry rather than written here. It was
written here, and §8 quoted a generated count beside it; the two had drifted seven kinds
apart, inside the appendix whose subject is count consistency. The `kind-count` check now
asserts that the number §8 claims, the number this list enumerates and the number the
checker registers at run time are one number.

Each entry pins two things and requires both: a **fragment of the paper's own text**, so that
rewording a sentence fails the check rather than silently detaching it from the claim it guards,
and a **relation recomputed from the artifacts**. A check that only re-asserts an artifact fact
guards nothing; a check that only matches text guards nothing either.

**The self-test.** Every assertion is run against a deliberately corrupted expectation on each
build and must fail: the interval relation inverted, the extremum replaced by the *runner-up*
rather than an absent label, the sign flipped, the order of magnitude and the dimension counts
moved by one. 52 of 52 are caught. An assertion that has quietly stopped
being able to fail is worth less than no assertion, because it reads as coverage.

**Four defects the self-test has found in the checker itself**, rather
than in the paper. Each surfaced because the checks were run rather than assumed, and the
last two are the ones a reader should weigh, because both are failures of *coverage* rather
than of arithmetic — an assertion that cannot fail, and a kind with no assertion attached,
both of which read as protection and are not:

- A fixed corruption per kind — `expect: "disjoint"` on every overlap check — which was a no-op for claims that already expected that value, so two of eleven assertions reported as missed when nothing had been corrupted.

- A label helper that prefixed a horizon to family keys already holding model names, producing `h=teacher-forced armB`, which matched nothing and failed two checks whose extrema were correct.

- An assertion that could not be corrupted at all: the `orders` check quoting a ratio directly rather than as an order of magnitude had no `stated_orders` to perturb, so the self-test skipped it and reported 31 of 31 caught beside a claim count of 32. The exemption was real, undocumented, and looked like coverage. A directly-quoted ratio is now asserted to appear in the sentence that quotes it, which is corruptible.

- A `sign` assertion that was never written. §6.8 said the two largest held-out deviations were "in opposite directions" when both are above target; the kind that would have caught it existed and no claim used it. A kind with no claim attached guards nothing, and the self-test cannot report that because there is nothing to corrupt.

Corruptions now invert relative to each claim's own expectation, every registered kind
carries at least one claim, and every claim is corrupted on every build: 52 of
52 caught against 52 claims, with no exemptions. This list is generated from
the checker rather than written here, so a fourth entry cannot be forgotten.

---

## Exclusions from the numeric comparison: the mechanism

**Excluding a file is not sufficient on its own.** `results/paper_numbers.json` records the
*source* of every value it holds, and it had copied that diagnostic's iteration count into a key
of its own — so the host-dependence leaked through a file that was not excluded, and the clean
clone duly differed on it. The verifier now drops any key whose recorded source is an excluded
artifact (18 of them), which follows the provenance the file already carries rather
than requiring anyone to remember.

**One further class, excluded by the same mechanism and worth naming because it sounds like an
excuse.** 11 keys in `paper_numbers.json` are sourced from
`verify_reproduction.json` — that is, they are this paper's statements *about this very
comparison*: how many files it regenerated, how many values matched, how many differed. A clean
clone necessarily carries in the **previous** run's figures and is then compared against a tree
holding the **current** run's, so they cannot agree: writing a result into the tree changes the
thing the next run measures. There is no fixed point to converge to, and treating it as a
reproducibility failure would make the reported figure oscillate rather than settle. They are
dropped by provenance like the others and counted in the output rather than hidden — the same
discipline §8's own 47-file figure rests on, since a silent exclusion is exactly how an
earlier version of this claim was inflated fiftyfold.

---

## What the checks caught in this revision's own text

Three defects, in text written during the revision itself and caught before it shipped:

- **two `horizon-consistency` failures** — a calibration figure in the rewritten abstract and
  another in a new section 6.2 paragraph, each quoted without the horizon it was measured at.
  This is the defect class the paper's own section 3.1 exists to prevent, and it recurred twice in one
  session of writing.
- **one `restatement` failure** — a new paragraph quoted a 15-point threshold, a 15.0% median
  and a 15% share in a single sentence, leaving the bare numeral ambiguous.

They are recorded as a count in Appendix D rather than enumerated there, because the count is
the argument and the enumeration is this page.
