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

**The check kinds.** `scripts/check_comparative_claims.py` verifies {{cc_n}} claims across
{{cc_kinds}} kinds: {{cc_kind_list}}.

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
moved by one. {{cc_st_caught}} of {{cc_st_n}} are caught. An assertion that has quietly stopped
being able to fail is worth less than no assertion, because it reads as coverage.

**{{cc_selfdefects_word}} defects the self-test has found in the checker itself**, rather
than in the paper. Each surfaced because the checks were run rather than assumed, and the
last two are the ones a reader should weigh, because both are failures of *coverage* rather
than of arithmetic — an assertion that cannot fail, and a kind with no assertion attached,
both of which read as protection and are not:{{cc_selfdefect_list}}

Corruptions now invert relative to each claim's own expectation, every registered kind
carries at least one claim, and every claim is corrupted on every build: {{cc_st_caught}} of
{{cc_st_n}} caught against {{cc_n}} claims, with no exemptions. This list is generated from
the checker rather than written here, so a fourth entry cannot be forgotten.

---

## Exclusions from the numeric comparison: the mechanism

**Excluding a file is not sufficient on its own.** `results/paper_numbers.json` records the
*source* of every value it holds, and it had copied that diagnostic's iteration count into a key
of its own — so the host-dependence leaked through a file that was not excluded, and the clean
clone duly differed on it. The verifier now drops any key whose recorded source is an excluded
artifact ({{ver_hostkeys}} of them), which follows the provenance the file already carries rather
than requiring anyone to remember.

**One further class, excluded by the same mechanism and worth naming because it sounds like an
excuse.** {{ver_selfref}} keys in `paper_numbers.json` are sourced from
`verify_reproduction.json` — that is, they are this paper's statements *about this very
comparison*: how many files it regenerated, how many values matched, how many differed. A clean
clone necessarily carries in the **previous** run's figures and is then compared against a tree
holding the **current** run's, so they cannot agree: writing a result into the tree changes the
thing the next run measures. There is no fixed point to converge to, and treating it as a
reproducibility failure would make the reported figure oscillate rather than settle. They are
dropped by provenance like the others and counted in the output rather than hidden — the same
discipline §8's own {{ver_files}}-file figure rests on, since a silent exclusion is exactly how an
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
