# Submission package

Everything needed to upload this submission, and nothing else. **Written for a person at a
browser.** Every figure here was read from the file it describes, at commit `4281ae4`, by
`docs/presubmission/round3/r8_package.py`, which also asserts each statement below about the two
bundles before writing it; the checksums were computed for this document rather than copied from an
earlier session. This replaces round 2's version.

**Before uploading, two things must be done, in this order.** Nothing in "Open items" (§8) blocks the
upload, but these do:

1. **The clean-clone verification (round 3, R9) must pass.** The reproduction figures §8 of the paper
   prints come from a clean clone of an earlier commit, and a clone of this one is predicted to measure
   them exactly; R9 measures it. If R9 stops, do not upload.
2. **The user's steps in `docs/presubmission/round3/PLAN.md` §0.4, steps 1-4:** bring the GitHub default
   branch up to date with `presubmission3`; re-upload `MODEL_CARD.md` to the Hugging Face model
   repository (it gained rule X2's result in round 3); **trigger a Software Heritage archive of the final
   pushed commit**; send the author query if it has not gone. The archive is not optional: the paper
   says the repository was archived by a third-party archive before submission, and the latest visit
   recorded in the repository (`results/swh_visit_check.json`) is of 2026-08-21, before round 3's commits
   existed. These pushes must happen before the upload, because §9 forbids pushing once the paper is
   under review.

Then upload the two files in §1, checking their checksums first.

---

## 1. The files to upload

| file | what it is | size | SHA-256 |
|---|---|---|---|
| `PAPER.pdf` | the submission, 62 pages, TMLR submission mode | 1,137,677 bytes | `f964d6b3a178208214908aa6dd2df4a66011403cf96a2a262834b667973c203a` |
| `supplementary_anon.zip` | the anonymised supplementary bundle, 517 members | 19,545,474 bytes | `5ba21134070fcfffbfdf45b7f3a47b9466891e30f65d2d8c782da7e04afbe633` |

**`supplementary.zip` is NOT uploaded — and not because it is unsafe.** Both bundles are anonymised:
each is built by a script that refuses to write the archive if any staged file carries the author
name or a repository URL, and an independent sweep of both returns 0 hits (§5). The reason is
narrower. It is gitignored, so unlike the two files above it is not tracked at any commit; its
493 members are a strict subset of the anonymised bundle's 517, with 0 files
unique to it; and the 24 the anonymised bundle alone carries include all 13
figures — among them the 6 the paper's LaTeX names (`paper_fig1_calibration`, `paper_fig2_sigma_profile`, `paper_fig3_collapse`, `paper_fig4_prereg_timeline`, `paper_fig5_three_way`, `paper_fig6_ab_by_horizon`) — plus `README.md`,
`LICENSE`, `MODEL_CARD.md`, `CITATION.cff` and `NOTICE`. One shared member differs in content,
`GIT_LOG_ANONYMISED.txt`: in its header, and in 2 commit subjects where the anonymised builder
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
since `4281ae4`; do not upload until they match. Every build recompiles `PAPER.pdf` with a new date
and ID, so a rebuild alone changes its checksum.

## 2. Title

Right Order, Wrong Size: A Verified Reproduction of the Robotic World Model and the Uncertainty It Reports

## 3. Abstract

Extract it from the paper rather than retyping it, with

```
python3 - <<'EOF'
import re
md = open("PAPER.md").read()
print(" ".join(re.search(r"##\s*Abstract\s*\n+(.+?)\n\s*---", md, re.S).group(1).split()))
EOF
```

At `4281ae4` it is 370 words by a whitespace split, within the 370-word cap the paper's own
check C12.1 enforces. It begins "We rebuild the dynamics model of the *Robotic World Model*" and ends
"...bound what the uncertainty reports, not what its miscalibration costs.". It is not retyped anywhere.

## 4. Keywords and one-sentence summary

Suggested keywords, drawn from the paper's own contributions: *reproduction study; model-based
reinforcement learning; world models; uncertainty calibration; ensemble disagreement;
pre-registration*.

One-sentence summary: an independent reproduction of a released robotic world model that
reproduces its central training claim, and finds its evaluation misaligned by one step and the
uncertainty it penalises with miscalibrated as a scale that worsens with rollout depth.

## 5. Anonymity confirmation

Swept at commit `4281ae4`, twice and independently: by the builders' own scans (the anonymised
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
  between the repository and a clean clone. 6 of 15,652 do, so it fails,
  and §8 says so. None of them is a measurement, a statistic or the verdict of a test; all are
  bookkeeping, and the build-checks supplementary (`docs/BUILD_CHECKS.md`) names each kind. With the identity strings supplied from outside the archive
  and a clean clone's results, 7 of 8 checks pass, check 4 alone failing. A
  reviewer who runs it in a pristine clone without those inputs will see fewer pass: check 2 needs
  the identity strings, and check 4b needs the gitignored `supplementary.zip`.
- **The reproduction figures cover what a clean-clone run regenerates and compares**, which §8 gives
  as 0.92% of the numeric values under `results/` that the comparison counts, not the
  whole directory. Counting the values a clone merely carries in would overstate the result about
  109-fold, as the build-checks supplementary says.
- **The paper withdraws eight of its own claims on evidence and six framings**, and keeps each
  in the ledger with the evidence that withdrew it, including its own claim to have pre-registered a
  rule it had not.

## 7. Reproducibility certification

The cover statement requests it explicitly. TMLR's certifications and the mechanism for requesting
them must be read off OpenReview at submission time rather than taken from this file: the names and
the request flow change between cycles, and nothing here has been checked against the live site.

## 8. Open items — the rulings first; nothing here blocks the upload

1. **The bare `swh:1:` prefix — RULED 2026-09-20, closed.** Each occurrence in the bundles is a bare
   prefix with no 40-character object name, so none resolves to anything on Software Heritage. The
   user ruled that a bare prefix is not an archival identifier.
2. **`submission_check`'s criterion E7 — FIXED in round 2, T8.** The check now reads the build-checks
   supplementary as well as the template.
3. **§8's denominator — reworded by the user's ruling of 2026-09-30.** §6 above states it exactly.
4. **The claims audit was regenerated on the frozen text (round 3, R8; ruling U5) and is not
   reviewed.** It extracts 550 claims, 58 marked supported and
   492 unreviewed. The ruling records the unreviewed claims as known.
5. **`results/supplementary_manifest.json` is now exact** (round 3, R5): it records
   493 files for an archive of 493 members and 468 commits for
   a log of 468, both counted rather than derived. No number the paper prints comes from it.
6. **Figure-internal label overlaps were fixed in round 2, T8** (rendered Figures 2(a), 5 and 6; no
   plotted value changed). The PDF still prints the step-size quantity as the literal text
   `‖µ_t − µ_{t−1}‖`; cosmetic.
7. **No report `reproduce.sh` writes is left untracked and unignored** (round 3, R5: the nine that
   nothing reads are gitignored, and both bundlers exclude them), so a clone's archive holds the
   tree's files. The private folder clean-clone runs share by default, the checkout folder's name inside
   one artifact's citation strings, and the evidence showing repeatability rather than portability
   are recorded in `docs/SUBMISSION_CHECKLIST.md` and `docs/DEFERRED.md`. None changes what is
   uploaded.

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
