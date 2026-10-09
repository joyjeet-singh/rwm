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
the verdict of a test is {{ver_part_sci}}.**
`./reproduce.sh --quick --force` regenerates {{ver_files}} artifact files and {{ver_values}}
numeric values from a clean clone: {{ver_identical}} bitwise identical ({{ver_pct}}%),
{{ver_close}} equal to within the verifier's floating-point tolerance but not bitwise, and
{{ver_differing}} differing. Those
three account for the {{ver_values}} exactly. Regeneration does not reproduce {{ver_keys_lost}} of the committed values, in
{{ver_keys_lost_files}} of the files; that count is kept separate, because a value that is not
produced twice cannot be compared twice.
The {{ver_differing}} differing values are partitioned by cause from the per-file record in
`results/verify_reproduction.json`: {{ver_part_index}} are in the document-line index
(`results/restatement_index.json`), {{ver_part_dilution}} in the stochastic dilution study
(`results/e5_sigma_dilution.json`), and {{ver_part_else}} elsewhere. The document-line index records where each
numeral sits in this paper's source and what it renders to. A clone checks out the same source, so
every position reproduces; the only values it can disagree on are this paper's own statements about
this comparison, which is why the committed index is regenerated whenever those figures are restated. Whether a differing value carries
a scientific result is decided value by value, not file by file: it does only if the value is
itself a measurement, a statistic or the verdict of a test, and a value does not qualify merely
because the file holding it also holds results. `scripts/paper_numbers.py` applies that rule in
code, counts any differing value it does not recognise as scientific, and places these outside the
scientific class: {{ver_book_named}}. **`part_f_gate` still fails.** Its clean-clone check requires
that no regenerated value differ; {{ver_differing}} do, and it is published as failing, with no
tolerance added.
**The claim is narrower than the percentage makes it sound, and we would rather state its size than
have a reader derive it.** A clean clone already contains every committed artifact, so the only
honest test is the subset the run actually rewrites: {{ver_values}} values, or {{ver_claim_pct}}% of the {{ver_all}} numeric values under `results/` that the comparison counts. The other {{ver_copied}} are carried in, prove
nothing about reproduction, and are never folded into the figure; counting them would overstate the result by about {{ver_overstate}}-fold. **What "every numeral" means is itself checked.** A paper cannot substitute a section number or an arXiv identifier, so the claim is partitioned: every *measurement* is substituted, and each of the {{tn_typed}} numerals that is not one is classified as an address, a horizon label or a declared constant — {{tn_classes}} classes and {{tn_exceptions}} declared exceptions, with the build failing on anything left over (`results/typed_numerals.json`). That audit exists because the abstract used to claim no number here was typed, which was false; the count was printed on every build and asserted by nothing. Verifying that every numeral came from an artifact says nothing about the sentence built around it, and defects of exactly that kind sit downstream of correct numerals. The build therefore also verifies **{{cc_n}} comparative claims** across {{cc_kinds}} kinds; all pass, and each is run against a deliberately corrupted expectation on every build and must fail, {{cc_st_caught}} of {{cc_st_n}} caught. **The next section gives the failure modes those checks exist for and the two exclusions from the numeric comparison; the sections after it give the registry, the self-test and the {{cc_selfdefects_lower}} defects the self-test has found in the checker itself.**

---

## Verifying the paper's own claims

*Formerly the paper's Appendix C, moved here in the referee revision. The text is as it stood
there; only headings and cross-references that now point the other way were changed.*

**The {{n_retractions_word_lower}} claims withdrawn on evidence, in order.** In order: a premise about forecast decay that turned out not to exist in the code; a framing of the released checkpoint as "clearly informative" that rested on an n=10 estimate we ourselves showed to be biased low; an aggregation artifact that inverted a published-model comparison in our favour, withdrawn when the gating checks we had written refuted it; a per-dimension comparison that turned out to be unmatched; the claim that σ is input-independent "in all four models", made against a table holding three; the phrase "the released checkpoint's uncertainty output", singular, when the checkpoint emits two and we had measured the one the method discards; the size of the released evaluation's one-step action misalignment, measured on overlapping windows one of which carried most of the effect, withdrawn when intervals over independent trajectories made it small and its sign reversed across the ten episodes (S-20, reclassified by M-82 as withdrawn on evidence); and the claim that our own checkpoints barely feel that misalignment, computed through a rollout that scored one trajectory's forecast against every trajectory's truth, withdrawn when the corrected measurement showed their error rising with the stale action at long horizons (S-21, withdrawn on evidence). **The {{n_retract_framing_word}} framings withdrawn**, as stated claims rather
than as numbers, and generated from the ledger rather than listed here — a typed
enumeration beside a generated count is the same defect as a typed count. This one was typed
with {{n_framing_before_last_word}} entries at a time when the ledger held
{{n_framing_before_last_word}}, and the revision that added {{n_framing_last_cohort_word}} more
replaced it with a generated list in the same commit, so it never actually stood wrong. It
appears here as a note rather than above as an entry for that reason, and the reason is luck:
nothing compared the typed enumeration against the count beside it, and had the two changes
landed in separate commits the paper would have said {{n_framing_through_review_word}} and enumerated
{{n_framing_before_last_word}}. All {{n_retract_framing_word}}, generated:{{n_retract_framing_list}}

The second pre-submission review entered {{n_framing_last_cohort_word}} of them, in a
single commit — which is how that count is established rather than recalled.
{{framing_last_cohort_ids_but_last}}
are sentences of the 24 August draft that were false. {{framing_last_cohort_final}} is different in kind and worse
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
  epistemic at h=1, which is third; the largest deviation is {{d3_worst_q}} at
  h={{d3_worst_h}}. **This one has now been wrong twice as well**, and the second time was
  here rather than in §6.7. This sentence named h=128, which was the extremum before h = 100
  entered the evaluation grid; §6.7 was re-derived when the grid changed and the sentence
  describing the *correction* was not. Both now read the same key, and the `extremum` kind
  covers this record and not only the section that computes it;
- **a stated change with the wrong sign** — "a change of **+**0.010", where partialling the
  forecast index out *reduces* the correlation;
- **two prose descriptions of one ratio that disagree** — "nearly three orders of magnitude" in
  the abstract against "two orders" in §12, of the same {{d1n_epi_over_alea_h368}}× at
  h = {{v2_diag_h}};
- **a count attributed to the wrong evaluation arena** — 0 of 45 over all ten episodes asserted
  where the table beside it printed the held-out arena's 20 of 45.

None is a numeral. None appears in `results/paper_numbers.json`. Each was typed.

**A sixth failure mode is not a relation at all, and it defeated the gate rather than
evading it.** `build_paper.py` asserted that no `{{`-delimited placeholder survived
substitution, and none did — while a sentence of §6.6 reached the PDF as an empty
one-column table. The sentence contained `|r_dd|`, the line wrapped so that the pipe began a
line, and the Markdown-to-LaTeX converter read a leading pipe as a table row. Every numeral
in it was correct and provenanced. The gate now refuses three further shapes as well as
unresolved braces: a pipe-led line with no separator row beneath it, a single-braced token
that names a real key, and any key resolving to an empty or null value. The converter
requires the separator row before it will build a table.

**The machinery, and the two lines that matter about it.** `scripts/check_comparative_claims.py`
verifies {{cc_n}} claims across {{cc_kinds}} kinds, each pinning a fragment of this paper's text
and a relation recomputed from the artifacts, and each run against a deliberately corrupted
expectation on every build so that a check which can no longer fail is caught. The registry, the
self-test's mechanics and the {{cc_selfdefects_lower}} defects it has found in the checker itself
are in the sections below. **The evidence that any of it is
load-bearing is one sentence**: the comparative checks caught three defects in text written
during this revision — two calibration figures that named no horizon, and one numeral quoted
three ways in a single sentence — none of which a human reader had noticed.
**Two exclusions from the numeric comparison**, on the same principle in both cases: the number
measures the machine, not the model. A third category is not an exclusion but a partition, and it
bounds everything in this record: of the {{ver_all}} numeric values under `results/` that the comparison counts, a clean clone regenerates {{ver_values}} and carries in {{ver_copied}}. The reproducibility claim covers {{ver_claim_pct}}% of that counted set and is silent about the rest. We state that fraction because a
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
check in `part_f_gate` requires that *no* regenerated value differ. {{ver_differing}} do, so the
check fails, and it is published as failing. We did not give it a tolerance. The differences sit in {{ver_diff_nfiles}} artifacts, counted from the per-file record in
`results/verify_reproduction.json`: {{ver_diff_by_file}}. The stochastic dilution study differs in
{{ver_part_dilution}}, and the number of differing values that are a measurement, a statistic or a
test verdict, under the rule the previous section states, is {{ver_part_sci}} — but a partition we believe is benign
is a reason to read the check's output, not to move its threshold. A gate that passes because its criterion was relaxed
tells a reader strictly less than one that fails and says where.

*One wall-clock-bounded diagnostic.* {{ver_timebound}} stops on a time budget rather than at its
iteration cap, so its iteration count and terminal losses are a property of the host and none of
them is quoted here; the section on exclusions below gives the mechanism and why
its sibling from the same script is not excluded.

---

## The check kinds and the self-test

**The check kinds.** `scripts/check_comparative_claims.py` verifies {{cc_n}} claims across
{{cc_kinds}} kinds: {{cc_kind_list}}.

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
- **an ordered-list marker interrupting a paragraph** — the same damage in the ranking section (now 6.6), where
  "M-43's own" then "4." lost the horizon count. There is no equals sign to spot it by, so the
  rule is the general one: a marker opens a list only after a blank line, or where a numbered
  item is already open in the same block.
- **a Markdown footnote token surviving into the LaTeX** — `[^stepcount]` set as literal text
  in a table cell of the ranking section (now 6.6) and its definition as a literal paragraph, because the
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

## A third refusal: the ledger's withdrawals, counted one way

The introduction said there were thirteen "retractions of our own claims". Section 8 said "six
retractions on our own evidence ... plus seven that withdraw framings" out of twenty superseded
claims. Both were true, both were generated from the ledger, and they counted the same entries in
two vocabularies, so a reader comparing them could not tell whether the paper had retracted six
claims or thirteen.

There is now one vocabulary and one source:
- **claims withdrawn on evidence** ({{n_retractions}});
- **framings withdrawn** ({{n_retract_framing}});
- **superseded entries** ({{n_superseded}}), which also include the early hypotheses closed as
  housekeeping.

`scripts/ledger_check.py` classifies every S- entry into exactly one class and refuses to pass if
any entry fits none. `scripts/paper_numbers.py` reads the three counts from its output
(`results/claims_to_evidence.json`) rather than classifying again, and refuses a stale output.

`scripts/build_paper.py` now refuses to build when **the introduction and section 8 do not each
state all three counts, each phrase directly after the key that counts it, or when either prints
the old combined total** (`check_retraction_counts`). It joins the gate's self-test with a
corrupted introduction.

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
discipline the {{ver_files}}-file figure in the reproducibility section above rests on, since a silent exclusion is exactly how an
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
values (`M-66`). A sweep of the pattern-based input discoveries in `scripts/` and `src/`
classifies each as an open population or frozen at write time. It found {{audit_n_retired}}
frozen, the ensemble-5 glob, since replaced by an explicit seed list and retired from the sweep;
of the {{audit_n_hits}} discoveries in the code now, {{audit_n_frozen}} are frozen. Artifacts that
discover their inputs now record the file list they were computed over.

*Round 2, T8: from "A sweep" to "frozen." this is no longer verbatim. It read "A sweep of all
N … M was frozen", filled from the audit's live counts, so once the audit began retiring fixed
discoveries (`results/input_set_audit.json`, `retired`) it read as if the sweep had found none.*

---

## Section numbers before round 2 (ruling U6)

Round 2 merged three subsections of §6 and renumbered it; §1–§5 and §7 onward are unchanged. The ledger, the rule texts in `docs/APPENDIX_G_RULES.md` and every document written before round 2 use the old numbers. Old → new: §6.5 → §6.3 (folded in), §6.6 → §6.5, §6.7 → §6.6, §6.8 → §6.7, §6.9 → §6.5 (folded in), §6.10 → §6.8, §6.11 → §6.8 (merged; the detail of both rules is in Appendices O and P).

## Moved from the paper body (pre-submission edit)

The pre-submission edit cut the paper body by moving its drafting history here rather than
deleting it: what an earlier draft said, how a check came to exist, and what a sweep found. Each
item is labelled with the section it left. Nothing below is a claim the paper no longer makes; the
claims stayed, and only their history moved.

- **[§3.1]** Every `file:line` citation in §3.1 is read back and checked against its own source
  text on every build ({{v3_n_citations}} of them).
- **[§3.1]** The section exists because two metrics in this project once disagreed in *direction*
  at h = 1, and because a choice between two aggregations of the same metric once inverted a
  comparison against the released model (Appendix G).
- **[§3.1]** Three properties of the coverage statistic — pooled over all three axes, cumulative
  over steps 1..h, and two-sided — were missing from the prose until the referee revision.
- **[§3.1]** Earlier drafts called h = {{v2_diag_h}} a "deployment horizon". It is the upstream's
  open-loop diagnostic length, and the label is withdrawn.
- **[§4]** Both counts and both lists of untested claims are generated from a classification tag
  carried in Appendix D's verdict column, so the enumeration cannot disagree with the count beside
  it. It did once: an earlier draft of that sentence, itself the replacement for the withdrawn
  framing `S-17` (a count defect in the same place), said {{appE_n_sim_word}} and then named
  {{appF_n_polhw_lower}}, and called all of them claims about policy learning or hardware when one
  of them is not. The framing `S-17` withdrew a universal quantifier; its replacement got the arithmetic wrong
  instead, the worse failure of the two because the sentence had just been rewritten under
  scrutiny.
- **[§5]** That the rule M-23 is anchored at the diagnostic horizon rather than the deployment one
  is recorded in the ledger as `M-46`; nothing in §5's by-horizon table discharges or re-opens M-23.
- **[§5]** The hold-last floor's win at one step is stated in §5 because an earlier §5 quoted the
  h = {{v2_diag_h}} margin over the floor with no indication that it does not hold everywhere.
- **[§5]** M-23 is anchored at h = {{v2_diag_h}}, where the claim is actually about, because M-16,
  anchored at the training horizon, returned "cannot be settled". That change of anchor was made
  before the runs, not after them (§8).
- **[§6.2]** The epistemic ratio at h = {{v2_diag_h}} ({{d1n_epi_ratio_h368}}×) barely differs
  from the one at h = {{v2_deploy_h}} ({{d1n_epi_ratio_h100}}×). That is why re-anchoring the
  paper's calibration claims from the diagnostic horizon to the deployment one changed the reading
  and not the conclusion.
- **[§6.2]** An earlier draft stated that the one-step row is measured on data the checkpoint
  trained on, and declined to draw the inference that the figure is therefore an upper bound on its
  calibration. The paper now draws it.
- **[§6.2]** An earlier draft said rule M-63's finding, that no state dimension is exempt from the
  one-step coverage failure, "is what §6.3's mechanism predicts: an objective whose optimum is σ = 0
  has no reason to spare any dimension". M-63 decomposes the epistemic term's coverage, and §6.3
  explains only the aleatoric head, so the clause is withdrawn (round 2, T6 review).
- **[§6.2]** At n_independent = {{b2_nind}} the short-horizon epistemic ordering looked like chance,
  and an earlier draft told a more interesting-sounding horizon story from it. At
  n_independent = {{d1n_nind}} that result proved an artifact of four trajectories, and it is
  recorded as one.
- **[§6.3]** That the collapse would happen on any dataset was, until the synthetic experiment,
  only asserted from the derivation; the experiment was run to test it.
- **[§6.4]** Every source citation behind §6.4's topology argument is read back from the pinned
  upstream and checked on every build ({{v1_n_citations}} of them, `results/v1_ensemble_topology.json`).
- **[§6.5]** The teacher-forced arm was trained for §5 but was missing from the first three
  calibration tables of earlier drafts; §6.5 adds it.
- **[§6.5]** The epistemic horizon story an earlier draft told, strongest at long horizon, was
  backwards: it rested on the smallest arena. When h = {{v2_deploy_h}} was added to the evaluation
  grid, its permutation P fell between the neighbouring horizons' values, where the existing reading
  said it should, which was not guaranteed in advance.
- **[§6.5]** The section's claim is narrower than the one first written: the ordering is
  directionally consistent but not established at conventional significance once the dependence
  between dimensions is respected.
- **[§6.6]** An earlier draft described the within-step control as "the decisive one". It is a mean
  of between-trajectory correlations, not a within-rollout test, and that description is withdrawn;
  the double-demeaned statistic is the decisive one.
- **[§6.6]** §9 once called the one-step figure a ranking of realised error without qualification;
  it now says it ranks whole rollouts at one step ahead.
- **[§6.6]** The released checkpoint's six-horizon count and the ensemble-5 rule's five-horizon
  count are kept in separate keys, so the build cannot print one where the other belongs.
- **[§6.8]** An earlier draft gave the range of the σ gain as its values at the two shortest
  horizons, which do not span it: the weakest gain lies at another horizon, below the stated floor.
  The horizon sweep found it, flagging the sentence for carrying two horizons' figures while naming
  two others.
- **[§7.2]** The {{stale_pct}}% (nRMSE) and {{stale_pct_rel}}% (relative-L1) this paper reported before came
  from {{ad_pa_n}} overlapping windows sampled as the upstream samples them, one of which (starting at row
  {{ad_pa_out_row}}) carries most of the effect; they are withdrawn on evidence (S-20, reclassified by M-82).
- **[§7.4]** The duplication control was run only because the first version of the splice finding
  inferred the mechanism (content rather than count) without it.
- **[§8]** The duplication-control rule's lead time is dated from the commit that introduced the
  log line, because the log records wall clock with no date and no offset; that is what makes
  Figure 1 reproducible outside this machine's timezone. Before that change the figure used the
  local timestamp.
- **[§8]** `S-15` was named by position in §8 ("the second framing retraction") until the second
  pre-submission review entered {{n_framing_last_cohort_word}} more framing retractions and moved it.
- **[Appendix B]** The runtime split was rounded to whole hours in an earlier draft, so its parts did
  not sum to the stated total; the `arithmetic` check now asserts that a stated total equals the sum
  of its stated parts. An earlier version of the appendix also gave a longest-run figure that
  predated the ten-thousand-iteration runs added for the three-seed headline.
- **[Appendix B]** `paper_numbers.py` selected the collapse family by filename until the first
  capacity-matched run walked into it through a glob; that collision and the second unguarded glob
  the fix did not reach are recorded above (`M-66`), with the sweep of every pattern-based
  input discovery in `scripts/` and `src/` that followed.
- **[Appendix D]** The epistemic ranking row read "weaker per-dimension than we first reported".
- **[Appendix E]** The table once omitted `M-52`: the selector matched entry titles, and M-52's
  title does not contain the word, so the row a sceptical reader most wants was silently absent.
- **[Appendix C]** The pricing table has one row per untested claim. Until the assertion that counts
  its rows against Appendix D's was written, it listed two fewer, and the two it omitted were the
  two whose cost was hardest to state honestly. Those two (the configuration sweep and the
  architecture baselines) have since been run (§5.2, §5.3).
