<!-- GENERATED FILE — do not edit. Edit docs/BUILD_CHECKS.template.md and run:
     python scripts/build_paper.py -->

# Build checks — the registry, the self-test, and what it caught in itself

Supplementary to the paper's Appendix C, which keeps the part that generalises: the failure
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

## The build gate: four refusals added for converter damage

`scripts/build_paper.py` already refused four shapes — an unresolved `{{`-delimited
placeholder, a pipe-led line with no separator row beneath it, a single-braced token naming a
real key, and a key resolving to an empty or null value. All four look at the resolved text or
at the brace syntax, and a further three classes of damage reached the compiled PDF past them,
with every placeholder resolved. Four more refusals were added, each with the instance that
motivated it:

- **a bare numeral opening a list under an unfinished equation** — section 6.2 wrapped as
  "at n_independent =" then "20." on its own line; the converter read the numeral as an
  ordered-list marker and ate it, so the PDF gave the sentence no sample size at all.
- **an ordered-list marker interrupting a paragraph** — the same damage in section 6.7, where
  "M-43's own" then "4." lost the horizon count. There is no equals sign to spot it by, so the
  rule is the general one: a marker opens a list only after a blank line, or where a numbered
  item is already open in the same block.
- **a Markdown footnote token surviving into the LaTeX** — `[^stepcount]` set as literal text
  in a table cell of section 6.7 and its definition as a literal paragraph, because the
  converter had no footnote rule. It now renders the reference as a superscript number and
  leaves the definition's wording untouched; `\footnote` is not usable at that site, which is
  inside a `tabular` inside a `\resizebox`.
- **a capitalised number-word substituted mid-sentence** — counts render through a capitalised
  word map for sentence-initial use, and dropping one into running prose produced "then named
  Five" in section 4 and "the Four defects it has found" in Appendix C. The rule reads the
  substitution site rather than the output, so the fix has to be a lower-cased key and cannot
  be undone by the next build.

Each of the four is run against a deliberately corrupted input on every build and must fire,
on the same grounds as the self-test above: a refusal that has quietly stopped being able to
refuse reads as coverage and is not.

---

## Exclusions from the numeric comparison: the mechanism

*One wall-clock-bounded diagnostic.* {{ver_timebound}} stops after {{ver_tb_budget}} seconds
rather than at its {{ver_tb_cap}}-iteration cap, so it reaches a different iteration count on
every machine — three different values across the three hosts we have run it on. Its iteration
count and terminal losses are therefore a property of the host, and we do not quote any of them
here: a number the build declares host-dependent has no business being printed as a result. **Its
sibling from the same script is not excluded**: that run reaches its cap, and reproduces bitwise.
Excluding by filename rather than by stopping rule would have dropped the reproducible one along
with it, so the verifier decides from the artifact — a run that stopped short of its own cap was
time-bounded.

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

They are recorded as a count in Appendix C rather than enumerated there, because the count is
the argument and the enumeration is this page.

---

## The negative lead-time bar, and the timezone it used to depend on

Moved verbatim from section 8, which keeps one sentence and this pointer.

The log records wall clock with no date and no offset, so both are taken from the commit that introduced that line — which makes the figure reproducible outside this machine's timezone, and it was not: the same arithmetic gave a different answer in every timezone until the offset stopped coming from the reader's clock.

---

## The glob collision, and the sweep of every pattern-based input discovery

Moved verbatim from Appendix B, which keeps one sentence and this pointer.

it did neither until the first
capacity-matched run walked into the family through a glob. **That fix reached
`paper_numbers.py` and `paper_figures.py` and not every script**: a second unguarded glob
survived in the ensemble-5 comparison until this revision found it, moving two published
values (`M-66`). A sweep of all {{audit_n_hits}} pattern-based input discoveries in
`scripts/` and `src/` now classifies each as an open population or frozen at write time;
{{audit_n_frozen}} was frozen, and artifacts that discover their inputs now record the
file list they were computed over.
