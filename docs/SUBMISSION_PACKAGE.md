# Submission package

Everything needed to upload this submission, and nothing else. **Written for a person at a
browser.** Every figure here was read from the file it describes, at commit `419c17c`, by
`docs/presubmission/round5/f17_package.py`, which also asserts each statement below about the two
bundles before writing it; the checksums were computed for this document rather than copied from an
earlier session. This replaces round 4's version.

**Before uploading, four things must be done, in this order.** Nothing in "Open items" (§8) blocks the
upload, but these do:

1. **The clean-clone verification (round 5, G18) must pass.** The reproduction figures the paper's
   reproducibility statement prints come from a clean clone of an earlier commit, and a clone of this one is predicted to measure
   them exactly; G18 measures it. If G18 stops, do not upload.
2. **The steps in `docs/presubmission/round5/PLAN.md` §0.5, "After G18", 1:** bring the GitHub default
   branch up to date with `presubmission5`; re-upload `MODEL_CARD.md` to the Hugging Face model repository (it has changed since round 3);
   **trigger a Software Heritage archive of the final pushed commit**. The archive is not optional: the
   paper's reproducibility record and the supplement say the repository was archived by a third-party
   archive before submission, and the latest visit recorded in the repository
   (`results/swh_visit_check.json`) is of 2026-08-21. These pushes must happen before the upload, because
   §9 forbids pushing once the paper is under review. Rounds 4 and 5 were committed locally; nothing has
   been pushed since round 3.
3. **TMLR's author rules (`docs/presubmission/round5/TMLR_CHECK.md`).** Every author must have
   submission quota left for 2026 and a complete, active OpenReview profile. The quota is checked by
   each author with TMLR's `coauthor_counts.py` (github.com/JmlrOrg/tmlr, `src/`), which needs that
   author's own OpenReview login, and the calculator at `cs.cmu.edu/~nihars/quota/author.html`. The
   author list cannot change after submission. **The TMLR blog could not be read by fetch** (Medium
   returned 403): look at it in a browser for anything posted after 15 October.
4. **The form (§7).** Choose "Regular submission", paste the competing-interests text of §7, human
   subjects "N/A", and suggest action editors.

Then upload the two files in §1, checking their checksums first.

---

## 1. The files to upload

| file | what it is | size | SHA-256 |
|---|---|---|---|
| `PAPER.pdf` | the submission, 55 pages, TMLR submission mode | 1,306,055 bytes | `4ebb2cedad1a4925c1f613e2fd9853e84cc9ecca3d6e1107f908e875a38ca147` |
| `supplementary_anon.zip` | the anonymised supplementary bundle, 630 members | 28,884,293 bytes | `f94f454c6e4211e28908be92b54ce96fd0d20e2b0159092976187b424e7a64ba` |

**`supplementary.zip` is NOT uploaded — and not because it is unsafe.** Both bundles are anonymised:
each is built by a script that refuses to write the archive if any staged file carries the author
name or a repository URL, and an independent sweep of both returns 0 hits (§5). The reason is
narrower. It is gitignored, so unlike the two files above it is not tracked at any commit; its
604 members are a strict subset of the anonymised bundle's 630, with 0 files
unique to it; and the 26 the anonymised bundle alone carries include all 15
figures — among them the 8 the paper's LaTeX names (`paper_fig1_calibration`, `paper_fig2_sigma_profile`, `paper_fig3_collapse`, `paper_fig4_prereg_timeline`, `paper_fig5_three_way`, `paper_fig6_ab_by_horizon`, `paper_fig7_findings`, `paper_fig8_sigma_adam`) — plus `README.md`,
`LICENSE`, `MODEL_CARD.md`, `CITATION.cff` and `NOTICE`. One shared member differs in content.
`GIT_LOG_ANONYMISED.txt` differs in its header, and in 2 commit subjects where the anonymised builder
replaces the name of the original paper's correspondent with "the first author". Neither copy
identifies the submitting author. Uploading it would therefore ship less, not more, and the checksum table
above covers the anonymised bundle.

**One linkage ships with the bundle that is uploaded, knowingly.** `MODEL_CARD.md` is in the
anonymised bundle and not in the other, and it carries 13 checkpoint `sha256` values, two of
which are published LFS blob hashes in the author's public Hugging Face repository — that last point
is recorded in `docs/DEFERRED.md` from a check made against the live repository in session 20 and is
not re-derivable offline. They are searchable and cannot be paraphrased away. The user ruled on
2026-09-18 that they ship; `docs/DEFERRED.md` records it as an accepted linkage rather than a
defect.

Verify before uploading, from the repository root:

```
shasum -a 256 PAPER.pdf supplementary_anon.zip
```

and confirm the two lines match the table above. If they do not, something has rebuilt one of them
since `419c17c`; do not upload until they match. Every build recompiles `PAPER.pdf` with a new date
and ID, so a rebuild alone changes its checksum.

## 2. Title

Right Ranking, Wrong Scale: Reproducing the Robotic World Model's Dynamics Model and Testing the Uncertainty of Its Follow-up

## 3. Abstract

Extract it from the paper rather than retyping it, with

```
python3 - <<'EOF'
import re
md = open("PAPER.md").read()
print(" ".join(re.search(r"##\s*Abstract\s*\n+(.+?)\n\s*---", md, re.S).group(1).split()))
EOF
```

At `419c17c` it is 209 words by a whitespace split, within the 210-word cap the paper's own
check C12.1 enforces, and 1,318 characters, within the submission form's 5,000. The
title is 125 characters, within the form's 250. It begins "We reimplement the dynamics model of the Robotic World Model" and ends
"...defects. One robot, gait and dataset; no policy is trained.". It is not retyped anywhere.

## 4. Keywords and one-sentence summary

Suggested keywords, drawn from the paper's own contributions: *reproduction study; model-based
reinforcement learning; world models; uncertainty calibration; ensemble disagreement;
pre-registration*.

One-sentence summary: an independent reproduction of a released robotic world model, whose central
training claim holds on held-out episodes, and a test of its follow-up's ensemble uncertainty, which ranks
error well and sizes it wrongly, at one step and increasingly with the horizon.

## 5. Anonymity confirmation

Swept at commit `419c17c`, twice and independently: by the builders' own scans (the anonymised
bundle's builder also plants a probe, now a full commit hash since round 2, T8, which fired on every
run; the supplementary builder's scan has no probe), and by sweep code written separately for
verification. The channels covered were member paths, member text
in several encodings, archive and member comments, extra fields, nested archives, PNG text chunks,
PDF text, the Info dictionary, XMP, link annotations and inflated PDF streams. Terms: the author's
name and its variants, the GitHub handle, the git-log e-mail, both repository URLs, the Hugging Face
URL, full archival identifiers, and any 7- to 40-character hexadecimal token resolving to a commit of
this repository.

**Result: 0 hits, in `PAPER.pdf` and in both bundles.**

## 6. What this submission says about itself

A reviewer should meet these in the paper rather than discover them:

- **A build gate is published as failing.** `part_f_gate` requires that no regenerated value differ
  between the repository and a clean clone. 3 of 18,299 do, so it fails,
  and the paper's reproducibility statement says so. None of them is a measurement, a statistic or the verdict of a test; all are
  bookkeeping, and the build-checks supplementary (`docs/BUILD_CHECKS.md`) names each kind. With the identity strings supplied from outside the archive
  and a clean clone's results, 7 of 8 checks pass, check 4 alone failing. A
  reviewer who runs it in a pristine clone without those inputs will see fewer pass: check 2 needs
  the identity strings, and check 4b needs the gitignored `supplementary.zip`.
- **The reproduction figures cover what a clean-clone run regenerates and compares**, which the reproducibility statement gives
  as 0.68% of the numeric values under `results/` that the comparison counts, not the
  whole directory. Counting the values a clone merely carries in would overstate the result about
  147-fold, as the build-checks supplementary says.
- **The paper withdraws nine of its own claims on evidence and eight framings**, and keeps each
  in the ledger with the evidence that withdrew it, including its own claim to have pre-registered a
  rule it had not.

## 7. The submission form, and the Reproducibility Certification

Read from the live form on 24 October 2026 (`docs/presubmission/round5/TMLR_CHECK.md`; the invitation was
last modified on 19 October). Main content is 11.67 pages, so choose
**"Regular submission (no more than 12 pages of main content)"**. Competing interests and human-subjects
reporting are required fields. The PDF limit is 50 MB and the supplementary limit 100 MB,
one ZIP or PDF; both files above are far below them. The form has no field for requesting a certification
and none for a cover letter. TMLR's Editorial Policies say action editors nominate the Reproducibility
Certification, which `docs/COVER_STATEMENT.md` asks for; how that statement reaches the action editor is the
authors' call.

**Competing interests (paste into the form; ruling Y11).** One author corresponded with the first author of
the reproduced papers before submission, about the released code, the penalised quantity in the follow-up and
the action alignment in the released evaluation, and asked the first author's permission to quote that
correspondence. The first author therefore knows this work exists and who wrote to them. The correspondence is
quoted in the supplement in anonymised form. No author has a financial interest in the outcome, and none is
affiliated with the authors of the reproduced papers. **Human-subjects reporting:** N/A.

## 8. Open items — nothing here blocks the upload

1. **Figure 3 of the outline was not drawn** (round5/REVIEW.md): TMLR does not require it, and §5.7's numbers are
   in prose.
2. **The alignment query was sent and has no reply.** The paper says so (§6) without a date. If a reply
   arrives before submission, §6 and the supplement need an update; after submission nothing changes.
3. **The claims audit was regenerated on the frozen text** (ruling U5) and is not reviewed: 384 claims,
   31 marked supported and 353 unreviewed.
4. **The review's residual risk** (`round5/REVIEW.md`): two checker reads stopped at their turn limits, so
   Appendix O's code citations against the pinned upstream, Appendix N's two pipeline rows and a few tables
   of Appendices H and L were checked only by the build's own gates.
5. **No one has looked at the rendered PDF pages** (`pdftoppm` is not installed on the build machine):
   open the pages with Figures 1 to 8 and the 35-row table of Appendix E by eye before uploading.
6. **`results/supplementary_manifest.json` is exact** (round 3, R5): it records 604 files for
   an archive of 604 members and 664 commits for a log of 664, both counted.
7. **`scripts/a1_consent_letter.py`'s fallback rewrites no longer match the paper's text**
   (round5/OUT_OF_SCOPE.md); no gate runs it and the primary path, the quotation extractor, is checked.
8. **Rounds 4 and 5's logged items** are in `docs/presubmission/round4/OUT_OF_SCOPE.md` and
   `docs/presubmission/round5/OUT_OF_SCOPE.md`. Two tracked files under `docs/presubmission/`, which no
   bundle ships, carry a local home path, so a push publishes it in the repository, not in the submission.

## 9. What must not happen

- **Nothing is pushed to the remote while this is under double-blind review.** The repository has a
  public origin under the author's account; a push during review would de-anonymise the submission.
- `docs/SUBMISSION_CHECKLIST.md`, `docs/DEFERRED.md` and `docs/COMMIT_LABEL_MAP.json` are internal and
  appear in no bundle. `docs/presubmission/` is internal too, except the 3 records the
  paper cites, which both bundles ship deliberately (`BASELINE_SPECS.md`, `ORIGINAL_SPECS.md`, `verify_original_specs.py`).
- The commit identifiers in the bundles are rendered as labels, not real hashes. Do not replace them
  by hand.

## 10. After acceptance

- **MLRC 2026 is closed to this paper**, and `docs/SUBMISSION_VENUE.md` records why: the
  expression-of-interest deadline passed on 4 June 2026, and self-nomination requires a TMLR
  acceptance recorded by 30 September 2026. Self-nomination reopens for a later cycle.
- The camera-ready is de-anonymised, which means the render-time commit labels become real
  identifiers again. Rebuild the bundle for it rather than swapping in `supplementary.zip`: that
  archive is itself anonymised and is a strict subset of the one uploaded, so it is neither the
  de-anonymised bundle nor the complete one.
