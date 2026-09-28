<!-- GENERATED FILE — do not edit. Edit docs/BUILD_CHECKS.template.md and run:
     python scripts/build_paper.py -->

# Build checks — the registry, the self-test, and what it caught in itself

Supplementary to the paper's §8. It carries the build's accounting, the paper's record of
verifying its own claims, and the machinery behind both.

Moved here in the revision that cut the paper from 44 pages, on the grounds that a reader
deciding whether to trust the numbers needs the failure modes and the exclusions, and a reader
wanting to run or extend the checks needs what is below. Nothing was deleted. The referee
revision moved the rest: section 8's reproducibility block and all of the paper's former Appendix C are
the first two sections below, and nothing was deleted from them either.

This file is GENERATED from `docs/BUILD_CHECKS.template.md` by `scripts/build_paper.py`,
from the same `results/paper_numbers.json` the paper is built from. A figure quoted here
therefore cannot disagree with the one the paper prints, and the `kind-count` check reads
the enumeration below to assert exactly that.

---

## Reproducibility, and a build that checks its own prose

*Moved from §8 of the paper in the referee revision. The text is as it stood there; only headings
and cross-references that now point the other way were changed.*

**The number of regenerated values that differ and are themselves a measurement, a statistic or
the verdict of a test is 0.**
`./reproduce.sh --quick --force` regenerates 49 artifact files and 9,598
numeric values from a clean clone: 9,233 bitwise identical (96.20%),
0 equal to within the verifier's floating-point tolerance but not bitwise, and
365 differing. Those
three account for the 9,598 exactly. Regeneration does not reproduce 1 of the committed values, in
1 of the files; that count is kept separate, because a value that is not
produced twice cannot be compared twice.
The 365 differing values are partitioned by cause from the per-file record in
`results/verify_reproduction.json`: 0 are in the document-line index
(`results/restatement_index.json`), 0 in the stochastic dilution study
(`results/e5_sigma_dilution.json`), and 365 elsewhere. The document-line index records where each
numeral sits in this paper's source and what it renders to. A clone checks out the same source, so
every position reproduces; the only values it can disagree on are this paper's own statements about
this comparison, which is why the committed index is regenerated whenever those figures are restated. Whether a differing value carries
a scientific result is decided value by value, not file by file: it does only if the value is
itself a measurement, a statistic or the verdict of a test, and a value does not qualify merely
because the file holding it also holds results. `scripts/paper_numbers.py` applies that rule in
code, counts any differing value it does not recognise as scientific, and places these outside the
scientific class: 353 in `results/task_c1_claims_audit.json` (how many substituted numbers each audited sentence of this document holds); 3 in `results/task_c1_claims_audit.json` (how many of this document's sentences the claims audit found, by review status); 1 in `results/anon_bundle.json` (how many of the anonymised bundle's files the scrubber rewrote); 1 in `results/anon_bundle.json` (the anonymised bundle's file count `n_files_staged`); 1 in `results/paper_numbers.json` (the build's input-audit count `audit_n_frozen`); 1 in `results/paper_numbers.json` (the build's input-audit count `audit_n_hits`); 1 in `results/supplementary_manifest.json` (how many commits the archive's anonymised git log carries); 1 in `results/supplementary_manifest.json` (the supplementary archive's own size and file count `bytes`); 1 in `results/supplementary_manifest.json` (the supplementary archive's own size and file count `files`); 1 in `results/supplementary_manifest.json` (the supplementary archive's own size and file count `uncompressed`); 1 in `results/t5_anon_transcript.json` (how many correspondence quotations this document uses). **`part_f_gate` still fails.** Its clean-clone check requires
that no regenerated value differ; 365 do, and it is published as failing, with no
tolerance added.
**The claim is narrower than the percentage makes it sound, and we would rather state its size than
have a reader derive it.** A clean clone already contains every committed artifact, so the only
honest test is the subset the run actually rewrites: 9,598 values, or 1.01%
of the 950,503 numeric values under `results/`. The other 940,905 are carried in, prove
nothing about reproduction, and are never folded into the figure; counting them would overstate the result by about 99-fold. **What "every numeral" means is itself checked.** A paper cannot substitute a section number or an arXiv identifier, so the claim is partitioned: every *measurement* is substituted, and each of the 693 numerals that is not one is classified as an address, a horizon label or a declared constant — 18 classes and 23 declared exceptions, with the build failing on anything left over (`results/typed_numerals.json`). That audit exists because the abstract used to claim no number here was typed, which was false; the count was printed on every build and asserted by nothing. Verifying that every numeral came from an artifact says nothing about the sentence built around it, and defects of exactly that kind sit downstream of correct numerals. The build therefore also verifies **60 comparative claims** across 27 kinds; all pass, and each is run against a deliberately corrupted expectation on every build and must fail, 60 of 60 caught. **The next section gives the failure modes those checks exist for and the two exclusions from the numeric comparison; the sections after it give the registry, the self-test and the four defects the self-test has found in the checker itself.**

---

## Verifying the paper's own claims

*Formerly the paper's Appendix C, moved here in the referee revision. The text is as it stood
there; only headings and cross-references that now point the other way were changed.*

**The six numbered retractions, in order.** In order: a premise about forecast decay that turned out not to exist in the code; a framing of the released checkpoint as "clearly informative" that rested on an n=10 estimate we ourselves showed to be biased low; an aggregation artifact that inverted a published-model comparison in our favour, withdrawn when the gating checks we had written refuted it; a per-dimension comparison that turned out to be unmatched; the claim that σ is input-independent "in all four models", made against a table holding three; and the phrase "the released checkpoint's uncertainty output", singular, when the checkpoint emits two and we had measured the one the method discards. **The seven framing retractions**, withdrawn as stated claims rather
than as numbers, and generated from the ledger rather than listed here — a typed
enumeration beside a generated count is the same defect as a typed count. This one was typed
with two entries at a time when the ledger held
two, and the revision that added four more
replaced it with a generated list in the same commit, so it never actually stood wrong. It
appears here as a note rather than above as an entry for that reason, and the reason is luck:
nothing compared the typed enumeration against the count beside it, and had the two changes
landed in separate commits the paper would have said six and enumerated
two. All seven, generated:

- **Task 3's duplication rule was pre-registered** (`S-12`).

- **The binomial P-values attached to every dimension count** (`S-15`).

- **The two largest held-out deviations are in opposite directions** (`S-16`).

- **The eight untested claims are, without exception, about policy learning or hardware** (`S-17`).

- **The per-member σ is worse by three orders of magnitude** (`S-18`).

- **The released checkpoint cannot have come from the released recipe** (`S-19`).

- **The released evaluation overstates its own model's error by 75%** (`S-20`).

The second pre-submission review entered four of them, in a
single commit — which is how that count is established rather than recalled.
`S-16`, `S-17` and `S-18`
are sentences of the 24 August draft that were false. `S-19` is different in kind and worse
in one respect: §7.5 had already narrowed that claim in the paper, and the narrowing was never
entered in the ledger, so the withdrawn version went on standing in the ledger's own
contributions summary and in the public README after the paper had withdrawn it. A
retraction that holds in one document and not in the repository is not a retraction, and
the `retraction-consistency` check now reads all five reader-facing files rather than
three. Each is an entry in `FINDINGS_LEDGER.md` with its evidence and its successor.

`build_paper.py` asserts that every printed number came from a named artifact. That is a
guarantee about *provenance*, and it is silent about *relations between* provenanced numbers.
Six failure modes survive it, and all six occurred in this paper. Five are relations between provenanced numbers; the sixth is not a relation at all and is set out after the list:

- **an interval relation that is not the one asserted** — "the intervals do not overlap",
  where at h=128 they overlap across 0.604–0.643. **This one has now been wrong twice.**
  The correction said the distinction mattered "at exactly one place"; adding h = 100 to
  the grid made it two, and the sentence recording the first error carried the second. A
  stated *frequency* — "at exactly one place", "in all four", "the only" — is a claim
  about a count, and no kind bound one to a recomputed count until `frequency-consistency`;
- **an extremum that is not the extremum** — the worst-calibrated held-out cell named as
  epistemic at h=1, which is third; the largest deviation is aleatoric at
  h=100. **This one has now been wrong twice as well**, and the second time was
  here rather than in §6.8. This sentence named h=128, which was the extremum before h = 100
  entered the evaluation grid; §6.8 was re-derived when the grid changed and the sentence
  describing the *correction* was not. Both now read the same key, and the `extremum` kind
  covers this record and not only the section that computes it;
- **a stated change with the wrong sign** — "a change of **+**0.010", where partialling the
  forecast index out *reduces* the correlation;
- **two prose descriptions of one ratio that disagree** — "nearly three orders of magnitude" in
  the abstract against "two orders" in §12, of the same 600× at
  h = 368;
- **a count attributed to the wrong evaluation arena** — 0 of 45 over all ten episodes asserted
  where the table beside it printed the held-out arena's 20 of 45.

None is a numeral. None appears in `results/paper_numbers.json`. Each was typed.

**A sixth failure mode is not a relation at all, and it defeated the gate rather than
evading it.** `build_paper.py` asserted that no `{{`-delimited placeholder survived
substitution, and none did — while a sentence of §6.7 reached the PDF as an empty
one-column table. The sentence contained `|r_dd|`, the line wrapped so that the pipe began a
line, and the Markdown-to-LaTeX converter read a leading pipe as a table row. Every numeral
in it was correct and provenanced. The gate now refuses three further shapes as well as
unresolved braces: a pipe-led line with no separator row beneath it, a single-braced token
that names a real key, and any key resolving to an empty or null value. The converter
requires the separator row before it will build a table.

**The machinery, and the two lines that matter about it.** `scripts/check_comparative_claims.py`
verifies 60 claims across 27 kinds, each pinning a fragment of this paper's text
and a relation recomputed from the artifacts, and each run against a deliberately corrupted
expectation on every build so that a check which can no longer fail is caught. The registry, the
self-test's mechanics and the four defects it has found in the checker itself
are in the sections below. **The evidence that any of it is
load-bearing is one sentence**: the comparative checks caught three defects in text written
during this revision — two calibration figures that named no horizon, and one numeral quoted
three ways in a single sentence — none of which a human reader had noticed.
**Two exclusions from the numeric comparison**, on the same principle in both cases: the number
measures the machine, not the model. A third category is not an exclusion but a partition, and it
bounds everything in this record: of the 950,503 numeric values under `results/`, a clean
clone regenerates 9,598 and carries in 940,905. The reproducibility claim covers
1.01% of the directory and is silent about the rest. We state that fraction because a
reviewer who computes it and finds we did not will reasonably discount everything around it.

*The CPU budget.* `results/step4_5_timing.json` measures the machine, not the model: projected
runtimes for configurations we did not run, peak resident memory, and the standard deviation of
seconds-per-iteration across repeats. None of it can reproduce bitwise on another machine, or on
this one under different load, so the numeric comparison leaves the whole file out, together with
every field elsewhere whose name marks it as a wall-clock timing. The file also records its own
variability, and **we quote none of it**: a sentence arguing that host-dependent numbers should not
be printed as results cannot quietly print its own as though they were stable, and on a second host
the same run reported a different spread on a different worst configuration. For the same reason we
do not print how many values this exclusion sets aside. That count is not a property of the timing
file alone: it also takes in the values of the wall-clock-bounded diagnostic described below, and
the entries of `results/paper_numbers.json` that are read from either of those files or from the
comparison's own record, so it changes from one clean-clone run to the next with that diagnostic's
iteration count. Read `results/step4_5_timing.json` as one machine's account of itself, not as a
property of the code.

**One of the build's own gates fails, and we report it rather than retire it.** The clean-clone
check in `part_f_gate` requires that *no* regenerated value differ. 365 do, so the
check fails, and it is published as failing. We did not give it a tolerance. The differences sit in 5 artifacts, counted from the per-file record in
`results/verify_reproduction.json`: `results/task_c1_claims_audit.json` (356), `results/supplementary_manifest.json` (4), `results/anon_bundle.json` (2), `results/paper_numbers.json` (2), `results/t5_anon_transcript.json` (1). The stochastic dilution study differs in
0, and the number of differing values that are a measurement, a statistic or a
test verdict, under the rule the previous section states, is 0 — but a partition we believe is benign
is a reason to read the check's output, not to move its threshold. A gate that passes because its criterion was relaxed
tells a reader strictly less than one that fails and says where.

*One wall-clock-bounded diagnostic.* `results/step4_4_overfit_ens1.json` stops on a time budget rather than at its
iteration cap, so its iteration count and terminal losses are a property of the host and none of
them is quoted here; the section on exclusions below gives the mechanism and why
its sibling from the same script is not excluded.

---

## The check kinds and the self-test

**The check kinds.** `scripts/check_comparative_claims.py` verifies 60 claims across
27 kinds: *abstract-budget* (the abstract stays inside its word and numeral budget), *arena_consistency* (every row of section 3.2's evidence table names an arena and an n_independent that the section owning that claim also states), *arithmetic* (a stated total equals the sum of its stated parts), *cell* (a k-of-45 count is the arena and horizon the text names), *compare* (a stated ordering between two scalars), *count-consistency* (one count asserted in several places, in words, numerals or numeric-string variants, agrees everywhere), *count-dependence* (a clean k-of-k count carries an interval or a not-independent note), *cross-artifact-sync* (the README and model card carry the paper's headline values), *extremum* (a named cell is the max or min of its family), *figure_reference* (every in-text figure number names a figure that exists, and no more distinct figure numbers are cited than the document has figures), *frequency-consistency* (a frequency stated in words -- "at every horizon", "at exactly one place" -- matches a count recomputed from the artifacts), *horizon-consistency* (every horizon-indexed figure in the prose names its horizon, and names the one its artifact cell came from), *horizon-forbidden* (a withdrawn horizon label appears nowhere in the paper), *horizon-label* (a phrase naming a horizon resolves to the horizon the artifact says it is, and the numbers beside it are that horizon's), *interval-required* (a quoted ratio or coverage is accompanied by its interval), *kind-count* (the number of kinds the build accounting claims, this file enumerates and the checker registers are one number), *orders* (a stated count of orders of magnitude matches `round(log10(ratio))`, or a ratio quoted directly appears in the sentence that quotes it), *overlap* (two intervals do or do not overlap), *population_partition* (the run populations the paper quotes against one another partition -- the run table's row counts sum to the stated total, every row states the width it trained at, and the collapse family plus the runs excluded from it equal the total), *relvar* (a stated ratio of relative variabilities), *restatement* (no sentence restates a quantity another section owns -- no numeral is typed into the slot a substituted one fills elsewhere, and no section prints two different quantities as the same numeral), *retraction-consistency* (a claim the ledger marks superseded is asserted nowhere reader-facing), *retraction_class_consistency* (every retraction identifier a reader-facing file names resolves to exactly one class, and to the class the ledger gives it), *scope-consistency* (a universal quantifier is checked against the set it quantifies over), *sign* (a stated rise or fall matches the direction of the difference), *table_renders* (every table in the source reaches the LaTeX as a table, with at least one row separator per source row), and *unit-consistency* (every n_independent figure names the evaluation unit it counts -- the revision introduced a second unit length, and 60 units of 33 rows and 4 of 400 are both "n_independent").

That list is generated from the checker's own registry rather than written here. It was
written here, and §8 quoted a generated count beside it; the two had drifted seven kinds
apart, inside the appendix whose subject is count consistency. The `kind-count` check now
asserts that the number the reproducibility section above claims, the number this list enumerates and the number the
checker registers at run time are one number.

Each entry pins two things and requires both: a **fragment of the paper's own text**, so that
rewording a sentence fails the check rather than silently detaching it from the claim it guards,
and a **relation recomputed from the artifacts**. A check that only re-asserts an artifact fact
guards nothing; a check that only matches text guards nothing either.

**The self-test.** Every assertion is run against a deliberately corrupted expectation on each
build and must fail: the interval relation inverted, the extremum replaced by the *runner-up*
rather than an absent label, the sign flipped, the order of magnitude and the dimension counts
moved by one. 60 of 60 are caught. An assertion that has quietly stopped
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
carries at least one claim, and every claim is corrupted on every build: 60 of
60 caught against 60 claims, with no exemptions. This list is generated from
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
  Five" in section 4 and "the Four defects it has found" in the former Appendix C (the claim-verification
  section above). The rule reads the
  substitution site rather than the output, so the fix has to be a lower-cased key and cannot
  be undone by the next build.

Each of the four is run against a deliberately corrupted input on every build and must fire,
on the same grounds as the self-test above: a refusal that has quietly stopped being able to
refuse reads as coverage and is not.

## Two refusals added in the pre-submission edit: a checkpoint on every figure that needs one

Both answer one defect, which reached a finished draft. §5 printed an h = 8 gap from one setting
(a single seed) beside a table from another (three seeds pooled), with no label on either, and
the two contradicted each other. Separately, no table said which training checkpoint its arms
were at, so §5's by-horizon table and the head-to-head accuracy table printed different numbers
for the same arm with nothing to say why. `scripts/build_paper.py` now refuses to build when:

- **an h = 8 gap figure in §5 is unlabelled.** Every §5 sentence that prints an h = 8 gap key
  either uses the table's own key, or names its checkpoint with a bound iteration or checkpoint
  key (`check_h8_gap_labels`);
- **a table with an arm row names no training iterations.** Every table with an Arm A, Arm B,
  ensemble or combined-arm row or column must carry a bound iteration or checkpoint key in the
  caption paragraph beside it, or an iterations column (`check_arm_table_captions`). Tables
  generated from a placeholder are expanded before the check, so none escapes. Tables of the
  originals' claims are not arm tables.

Both join the gate's self-test, and each is fed a corrupted input on every build and must fire.

---

## Exclusions from the numeric comparison: the mechanism

*One wall-clock-bounded diagnostic.* `results/step4_4_overfit_ens1.json` stops after 2,700 seconds
rather than at its 2,000-iteration cap, so it reaches a different iteration count on
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
artifact (32 of them), which follows the provenance the file already carries rather
than requiring anyone to remember.

**One further class, excluded by the same mechanism and worth naming because it sounds like an
excuse.** 25 keys in `paper_numbers.json` are sourced from
`verify_reproduction.json` — that is, they are this paper's statements *about this very
comparison*: how many files it regenerated, how many values matched, how many differed. A clean
clone necessarily carries in the **previous** run's figures and is then compared against a tree
holding the **current** run's, so they cannot agree: writing a result into the tree changes the
thing the next run measures. There is no fixed point to converge to, and treating it as a
reproducibility failure would make the reported figure oscillate rather than settle. They are
dropped by provenance like the others and counted in the output rather than hidden — the same
discipline the 49-file figure in the reproducibility section above rests on, since a silent exclusion is exactly how an
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

They are recorded as a count in the claim-verification section above rather than enumerated
there, because the count is the argument and the enumeration is this page.

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
values (`M-66`). A sweep of all 21 pattern-based input discoveries in
`scripts/` and `src/` now classifies each as an open population or frozen at write time;
1 was frozen, and artifacts that discover their inputs now record the
file list they were computed over.
