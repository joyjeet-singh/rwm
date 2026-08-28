"""
C3 -- the ledger entries for revision 2, and the one summary that had gone stale.

Every fix in this revision that changed a CLAIM gets an entry here. Fixes that
changed only presentation (a rounding that made two parts not sum to their total,
a wrapped line that rendered as a table) are recorded in the entries that describe
the checks now guarding them, not as retractions: this project's retraction record
is load-bearing and inflating it with typography would devalue it.

Three sentences in the 24 August draft were false, and those are retractions.

Entries are appended, never edited in place. The one exception is the "Candidate
paper contributions" SUMMARY at the tail, which is not a claim entry: it still
asserted, as contribution 4, the sentence §8 withdraws, and carried figures from
before the three-seed and n=20 recomputations. A summary that contradicts the
entries it summarises is worse than no summary, so it is corrected and the
correction is stated in place.

Run with --write.
"""
import difflib
import re
import shutil
import sys

LEDGER = "FINDINGS_LEDGER.md"
ANCHOR = "## Candidate paper contributions"

NEW_ENTRIES = r"""
### R-70 — The h=100 re-anchoring left the prose behind, in 22 sentences · **NEW**
The paper re-anchored from h=368 to h=100 (X-13, V2): h=368 is the upstream's open-loop
**diagnostic** length and h=100 is the method's own imagination rollout length. The tables
followed. Parts of the prose did not.

**The measurement.** `scripts/horizon_sweep.py` walks `PAPER.template.md`, resolves every
placeholder to the artifact cell it came from, and compares that cell's horizon against the
horizon the surrounding text names. A calibration figure — an overconfidence ratio or a coverage
— must name its horizon in its own sentence; every other horizon-indexed value must name it in
the enclosing paragraph. On the 24 August draft it returns **28 findings across 20 distinct
locations**: 11 calibration figures unscoped at sentence level and 17 other values unscoped at
paragraph level. Re-derivable —
`git show <24-aug-rev>:PAPER.template.md > /tmp/pre.md && python scripts/horizon_sweep.py --file /tmp/pre.md`.

**Eight of the eleven sentence-level findings had been found by hand** in the second review brief,
which is a good rate for a manual pass over a thirty-page paper and is also the argument for not
relying on one: three calibration figures and all seventeen paragraph-level ones had not been
found, and one that the brief did find (§6.6's "39.7× overconfident") this scanner passes, because
the sentence names two horizons and the scanner cannot tell which the ratio belongs to. Manual
reading and the scanner miss different things; both were used.

**Why no existing check saw them.** Every numeral involved was correct and every one came from a
named artifact, so `build_paper.py`'s provenance gate passed. Provenance says where a number came
from; it says nothing about whether the sentence around it is scoped to that number's horizon.

**Two of the 22 were substantive rather than merely unlabelled.** §6.10 wrote the σ-gain range as
"1.56–1.81× at every horizon" — the h=1 and h=8 values standing in for a range that does not span
h=368's 1.49×. And §6.2's summary paired the h=368 ratio between the two uncertainty terms (600×)
with h=100 figures in the same sentence; that ratio is itself horizon-dependent and is 349× at
h=100 (S-18).

**Now zero, and kept there.** The sweep runs on every build as the `horizon-consistency` check
and the build fails on any finding.
**Evidence** `RUN` `results/horizon_sweep.json` `scripts/horizon_sweep.py`.
**Status** CONFIRMED · **Relevance** METHOD


### M-46 — M-23 is anchored at the diagnostic horizon, not the deployment one · **NEW**
**The rule is untouched and its verdict stands as returned.** This entry records what the rule's
anchor is now known to be, which is not the same thing as changing it.

M-23 (commit `efc35b8`) tests the autoregressive-versus-teacher-forcing gap at h=368, and §5's
header described that as "the horizons the method deploys at". V2 establishes that h=368 is the
upstream's open-loop **diagnostic** length and that the method's own imagination rollouts run to
h=100 — so the header named the wrong regime for the horizon the rule actually uses. §3.1 already
says h=368 "is not a deployment horizon"; §5 had not followed.

**This is the third instance of the M-24 pattern** — a decision rule anchored without regard to
the regime it would be applied in. M-24 was the first (a rule at h=8, the training horizon, for a
claim about long horizons). M-43 was the second (a rule committed without a power check, returning
DOES NOT GENERALISE at a sample size that could not resolve its own criterion). M-23 is the third,
and it is the mildest of the three: the rule's regime is *longer* than the deployment horizon
rather than shorter, so it is if anything a harder test.

**What changes in the paper.** §5's header names the open-loop diagnostic horizon. The same A/B
comparison is reported at h=100 beside the pre-registered h=368 figure, and the two differ
materially — 4.61× against 2.58× — so a reader cannot assume the headline transfers to the
horizon §6 is anchored to. **Nothing discharges or re-opens M-23.**
**Evidence** `RUN` `results/task_d1_threeseed.json` `results/v2_deployment_horizon.json`.
**Status** CONFIRMED · **Relevance** METHOD


### X-16 — RWM-O and RWM-U are one model renamed, verified by occurrence count · **NEW**
The reference list and Appendix F both state that arXiv:2504.16680 renamed its model from RWM-O to
RWM-U between v1 and v3. That claim was challenged on the reading that the public v3 contains
**both** names — RWM-U in the abstract and RWM-O in the experiments — which would make them two
variants rather than one rename, in a paper whose premise is checking claims against sources.

**Checked by counting rather than by reading**, on the rendered HTML of all three versions,
28 August 2026:

| version | RWM-O | RWM-U |
|---|---|---|
| v1 | 39 | 0 |
| v2 | 0 | 43 |
| v3 | 0 | 43 |

The two names never co-occur. The introducing sentence is otherwise word-for-word identical:
v1 "To this end, we introduce **Offline** Robotic World Model (RWM-O), where we explicitly
incorporate uncertainty quantification"; v3 the same with "**Uncertainty-Aware**". What changed is
the expansion of the letter, not the model — the architecture tables and Eq. 4 are unchanged
(V4).

**The claim stands.** The expansions and the counts are now recorded, so the next reader can check
it in one grep rather than by re-reading the paper.
**Evidence** `EXT` `results/original_paper_figures.json`.
**Status** CONFIRMED · **Relevance** CONTEXT


### X-17 — M-44's contrast differs in capacity as well as in independence · **NEW**
§6.10 compares five independently-initialised full models against five heads on one shared trunk.
§12 recorded two respects in which the two arms differ besides the one under test: initialisation
and data ordering. There is a third, and it is the one a reader of §6.10 will find first.

**Capacity.** Measured from the checkpoints' own tensors, the state pathway — the parameters that
produce the mean predictions whose spread *is* the epistemic term — carries **3,570,820**
parameters in the independent arm against **1,024,132** in the shared-trunk arm, a factor of
**3.49**. Each independent member brings its own trunk.

**Why it matters specifically here.** The overconfidence factor is error over σ, and greater
capacity can raise σ as well as lower error. σ is the column the mechanism claim rests on.
§6.10's decomposition separates the σ gain from the accuracy gain; it does **not** separate
capacity from independence, and nothing in this project does.

**What would settle it:** five trunks at one fifth the width each, matched on total state-pathway
capacity, with five independent recurrent states. That is a different architecture and a different
training run, and it is out of scope here.

**M-44's verdict is unaffected and its text is not edited.** M-44 was committed before the runs
and states its own limitation on two axes; this is a third axis, found afterwards, and it is
recorded here rather than written back into a pre-registered rule. §12 names all three.
**Evidence** `RUN` `results/v1_ensemble_topology.json`.
**Status** CONFIRMED · **Relevance** METHOD


### M-47 — Four check kinds, and the two ways the checker was not checking · **NEW**
`scripts/check_comparative_claims.py` had eight enumerated kinds and none of them could have
caught four of the defect classes the second review found. Four kinds were added:

- **`horizon-consistency`** — every horizon-indexed figure in the prose names its horizon, and
  names the one its artifact cell came from (R-70). Catches the whole class.
- **`arithmetic`** — a stated total equals the sum of its stated parts. Appendix B read
  "46 hours … 20 for the six 10,000-iteration runs and 27 for the remaining 20"; 20 + 27 = 47.
  All three came from `wall_clock_s` and none was typed; each was rounded to whole hours on its
  own.
- **`kind-count`** — the number of kinds §9 claims, the number Appendix D enumerates and the
  number the checker registers at run time are one number. They had drifted seven apart, inside
  the appendix about count consistency.
- **`scope-consistency`** — a universal quantifier in the body is checked against the set it
  quantifies over. §4 said the eight untested claims were "without exception" about policy
  learning or hardware; Appendix E prices two of them as CPU-affordable (S-17).

**`count-consistency` was extended to numeric-string variants.** It caught a count stated in two
different sizes and could not see a constant spelled two different ways: 68.3 against the derived
68.27, in §6.8, Figure 1's caption and its axis label; and +0.917 against +0.918, two sections
apart, for one bootstrap of one statistic quoted from two different artifacts.

**Two failures of coverage rather than of arithmetic, both in the checker.** One assertion could
not be corrupted at all — the `orders` check quoting a ratio directly had no stated order to
perturb, so the self-test skipped it and reported 31 of 31 caught beside a claim count of 32. And
the `sign` kind, which exists precisely to catch a stated direction that is not the measured one,
had no claim attached to §6.8's "opposite directions" sentence (S-16). A kind with no claim
attached guards nothing, and no self-test can report that, because there is nothing to corrupt.
Both are now entries in Appendix D's list of defects the self-test found in the checker itself,
which is generated from the checker rather than typed.

**Every claim is now corrupted on every build with no exemptions**: 44 of 44 caught against 44
claims across 19 kinds.
**Evidence** `RUN` `results/comparative_claims.json` `scripts/check_comparative_claims.py`.
**Status** CONFIRMED · **Relevance** METHOD


### S-16 — "The two largest held-out deviations are in opposite directions" · **NEW**
**Retracts** — a framing, not a numbered claim; the two coverage figures it names are correct
**What is retracted:** §6.8's description of the two largest deviations from nominal coverage
across the per-horizon recalibration's held-out cells as being "both at h=100 on the aleatoric
term, **in opposite directions** (77.48% and 76.55%)".

**Why it is wrong, in two ways.** Both figures are **above** the 68.27% target, so they are not in
opposite directions; and the second is at **h=128**, not h=100. The earlier draft's pair —
76.55% and 60.18% — *was* in opposite directions, and the sentence survived the recomputation
that changed which two cells were largest.

**What is not retracted:** the coverage figures themselves, the identification of the largest
deviation, and the conclusion of §6.8. Both cells are still the two largest and the per-horizon
multiplier still lands every held-out cell within tolerance. The corrected reading is *milder*
than the retracted one: the multiplier is slightly conservative at the long horizons rather than
unstable in both directions.

**Who found it:** the second pre-submission review, from the shipped PDF. **Why no check caught
it:** the `sign` kind existed and no claim used it on this sentence (M-47). Two now do.
**Evidence** `RUN` `results/task_d3_perhorizon.json`.
**Status** RETRACTED · **Relevance** METHOD


### S-17 — "The eight untested claims are, without exception, about policy learning or hardware" · **NEW**
**Retracts** — a framing, not a numbered claim; the list of untested claims is unchanged
**What is retracted:** §4's universal quantifier. Of the eight claims of the two originals that
this work did not test, **six** need a simulator, an RL loop and an ANYmal. The other **two** —
the M=32/N=8 configuration sweep and the MLP/RSSM/transformer baseline comparison — need none of
that, and Appendix E says so two pages later, pricing both within the CPU budget this project
already spent.

**What is not retracted:** that we did not test them, or the reason. They are unrun for want of
time, which §4 now says plainly instead of attributing them all to hardware we do not have.

**Why it survived.** The claim and its counter-example were in the same document, two appendices
apart, and nothing compared them. The `scope-consistency` check now reads the quantifier in §4
against the enumeration in Appendix E, and both counts in that paragraph are derived from those
two tables rather than typed.
**Evidence** `RUN` `PAPER.template.md, Appendix E + F tables`.
**Status** RETRACTED · **Relevance** METHOD


### S-18 — "The per-member σ is worse by three orders of magnitude" · **NEW**
**Retracts** — a framing, not a numbered claim; both underlying ratios are correct
**What is retracted:** the abstract's description of the gap between the two uncertainty terms as
"three orders of magnitude". At the horizon the abstract is anchored to — h=100, the method's own
imagination rollout length — the ratio between the aleatoric and epistemic overconfidence factors
is **349×**, which is two and a half orders. The "three orders" phrasing described the h=368
figure of 600× and was not re-anchored with the rest of the sentence.

**The underlying cause is that the ratio is itself horizon-dependent and only the h=368 form
existed as a key.** It is now generated at every horizon, so a sentence can quote the one it is
scoped to, and the abstract quotes the factor rather than an order of magnitude.

**This is a recurrence, not a new class.** Appendix D already lists "two prose descriptions of one
ratio that disagree" among the failure modes a provenance gate cannot see, and this is the same
defect surviving a change of anchor. The `orders` check now asserts that a directly-quoted ratio
appears in the sentence that quotes it, at the horizon that sentence names, and that assertion is
itself corruptible for the first time (M-47).
**Evidence** `RUN` `results/task_d_nind20.json`.
**Status** RETRACTED · **Relevance** METHOD


### S-19 — "The released checkpoint cannot have come from the released recipe" · **NEW**
**Retracts** — a framing, not a numbered claim; the three extrapolations it rested on all stand
**What is retracted:** the inference from three independent implied-iteration estimates to the
conclusion that the released checkpoint is inconsistent with its own released recipe. §8 of the
paper narrowed this before submission and the narrowing was never entered here, so the claim went
on standing in the ledger's contributions summary and in the public README after the paper had
withdrawn it. That is the failure this entry exists to close, and it is the same one M-28 and the
README regeneration were written for: a claim withdrawn in one document and left asserted in
another.

**The defensible claim** is that **no constant-rate run from the released initialisation at the
configured learning rate reaches this checkpoint's variance state in 500, 2,500 or 5,000
iterations**. The extrapolation assumes the released initialisation and learning rate. The first
author's account is that "the checkpoint was released after a few iterations of the repo than the
setup I used for the submission" — so a warm start, or a `log_delta_logstd` initialised
differently, would explain the gap with no inconsistency at all, and §8's own table records that
neither can be excluded by the second parameter.

**What is not retracted:** the arithmetic. The collapse rate, the `min_logstd` clock and the
negative implied count under `gaussian_nll` are unchanged and are what let the gap be detected.
What changes is what they license: a documentation gap between a release and a run, which is
common and worth recording, rather than an inconsistency in the release.

**Who found it:** raised in correspondence with the first author, 21 August 2026; the ledger
summary and the public README were found still asserting it by the second pre-submission review.
**Evidence** `RUN` `results/step6_analysis.json` · `EXT` first-author correspondence.
**Status** RETRACTED · **Relevance** METHOD


"""

# The tail summary. Not a claim entry -- a summary of them -- and it had gone
# stale in the one way that matters: it asserted the sentence 8 withdraws.
SUMMARY_EDITS = [
    ("contributions 4: the claim 8 narrowed was still asserted here as a contribution",
     """4. **The released checkpoint cannot have come from the released recipe, on three independent
   measures** `[BOTH]` (C-12, C-13, O-12, R-24, R-25, R-41, R-50). Collapse rate implies
   ~158,000 iterations against a tag of 5,000; `min_logstd` on a 5× slower clock implies order
   2.7e5; and under `gaussian_nll` the implied count is **negative**, so the branch it was
   trained with is identifiable.""",

     """4. **The released artifacts do not reproduce the released checkpoint's variance state**
   `[BOTH]` (C-12, C-13, O-12, R-24, R-25, R-41, R-50, S-19). Collapse rate implies ~158,000
   iterations against a tag of 5,000; `min_logstd` on a 5× slower clock implies order 2.7e5; and
   under `gaussian_nll` the implied count is **negative**, so the branch it was trained with is
   identifiable. **This claim is narrower than the one it replaces.** It read "cannot have come
   from the released recipe, on three independent measures" until §8 withdrew that: the
   extrapolation assumes the released initialisation and learning rate, and the first author's
   account is that the repository moved on between the training run and the release. A warm start
   or a changed initialisation explains the gap with no inconsistency, and neither can be
   excluded. What is measured is a documentation gap between a release and a run."""),
]


def patch(text, old, new, label):
    pat = re.compile(r"[\s>]+".join(re.escape(w) for w in old.split()))
    done = list(re.compile(r"[\s>]+".join(re.escape(w) for w in new.split())).finditer(text))
    if done:
        assert len(done) == 1, f"[{label}] replacement present {len(done)} times"
        return text, "already applied"
    hits = list(pat.finditer(text))
    assert len(hits) == 1, f"[{label}] matched {len(hits)}, expected 1"
    return text[:hits[0].start()] + new + text[hits[0].end():], "ok"


def main():
    write = "--write" in sys.argv
    original = open(LEDGER).read()
    text = original

    ids = re.findall(r"^### ([A-Z]-\d+) ", NEW_ENTRIES, re.M)
    already = [i for i in ids if f"\n### {i} " in text]
    if already:
        print(f"  entries already present, not re-appending: {already}")
    else:
        assert ANCHOR in text, "the contributions summary is not where this expects it"
        i = text.index("\n" + ANCHOR)
        text = text[:i] + "\n" + NEW_ENTRIES.strip("\n") + "\n\n" + text[i + 1:]
        print(f"  appended {len(ids)} entries: {', '.join(ids)}")

    for label, old, new in SUMMARY_EDITS:
        text, how = patch(text, old, new, label)
        print(f"  {how:<15} {label}")

    if not write:
        print("  DRY RUN — re-run with --write")
        return
    shutil.copy(LEDGER, LEDGER + ".rev2bak")
    open(LEDGER, "w").write(text)
    d = list(difflib.unified_diff(original.splitlines(), text.splitlines(),
                                  "before", "after", lineterm="", n=0))
    print(f"  wrote {LEDGER} ({len(d)} diff lines)")


if __name__ == "__main__":
    main()
