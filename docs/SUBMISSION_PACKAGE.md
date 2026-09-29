# Submission package

Everything needed to upload this submission, and nothing else. **Written for a person at a
browser.** Every figure here was read from the file it describes, at commit `aaf629c`, and the
checksums were computed for this document rather than copied from an earlier session. The two files
to upload are unchanged since `c16267c`, the commit the final verification covered.

**Nothing blocks the upload.** Every item that needed a ruling has one: whether the bare `swh:1:`
occurrences count as archival identifiers (ruled 2026-09-20), and, from the final verification,
`submission_check`'s criterion E7 and the wording of §8's denominator (both ruled 2026-09-27); see
"Open items" below. The items that remain there are recorded, and the user confirmed on 2026-09-27
that none of them blocks the upload.

---

## 1. The files to upload

| file | what it is | size | SHA-256 |
|---|---|---|---|
| `PAPER.pdf` | the submission, 48 pages, TMLR submission mode | 1,024,202 bytes | `2e2b0bf7dc5832cd9b989529a755e19b7e7eee6739cdeb9d12e268a361c49974` |
| `supplementary_anon.zip` | the anonymised supplementary bundle, 420 members | 12,523,111 bytes | `69f94d647dc329bbe119ffbb46167378a20a1ef2603e6b7db3ec8b99c0aab7af` |

**`supplementary.zip` is NOT uploaded — and not because it is unsafe.** Both bundles are anonymised:
each is built by a script that refuses to write the archive if any staged file carries the author
name or a repository URL, and a sweep of the working-tree copy returns 0 hits, as §5 records. The
reason is narrower. It is gitignored, so unlike the two files above it is not tracked at any commit;
its 396 members are a strict subset of the anonymised bundle's 420, with 0 files unique to it; and
the 24 the anonymised bundle alone carries include all 13 figures — among them the 6 the paper's
LaTeX names — plus `README.md`, `LICENSE`, `MODEL_CARD.md`, `CITATION.cff` and `NOTICE`. Only two
shared members differ in content at all, `GIT_LOG_ANONYMISED.txt` and `results/anon_bundle.json`,
and neither difference is identifying. Uploading it would therefore ship less, not more, and the
checksum table above covers the anonymised bundle.

**One linkage ships with the bundle that is uploaded, knowingly.** `MODEL_CARD.md` is in the
anonymised bundle and not in the other, and it carries 13 checkpoint `sha256` values, two of which
are published LFS blob hashes in the author's public Hugging Face repository — that last point is
recorded in `docs/DEFERRED.md` from a check made against the live repository in session 20 and is
not re-derivable offline. They are searchable and cannot be paraphrased away. The user ruled on
2026-09-18 that they ship; `docs/DEFERRED.md` records it as an accepted linkage rather than a
defect. It is restated here because it is a property of the file being uploaded, not of the one
being withheld.

Verify before uploading, from the repository root:

```
shasum -a 256 PAPER.pdf supplementary_anon.zip
```

and confirm the two lines match the table above. If they do not, something has rebuilt one of them
since `c16267c`; do not upload until they match.

## 2. Title

Right Order, Wrong Size: A Verified Reproduction of the Robotic World Model and the Uncertainty It Reports

*Title updated in pre-submission S10 (user ruling D6, `docs/presubmission/DECISIONS_FOR_USER.md#S10-review-blocked`).
The rest of this document (abstract, counts, SHA-256s) predates the pre-submission edit and is refreshed
once the paper is frozen.*

## 3. Abstract

Extract it from the paper rather than retyping it, with

```
python3 - <<'EOF'
import re
md = open("PAPER.md").read()
print(" ".join(re.search(r"##\s*Abstract\s*\n+(.+?)\n\s*---", md, re.S).group(1).split()))
EOF
```

A copy made that way during verification is also at
`/Users/Shared/rwm_verify/evidence/S28T/abstract.txt`, outside the repository (227 words). It begins
"We rebuild the proprioceptive dynamics model of the *Robotic World Model*" and ends "...brings
every held-out coverage estimate near nominal, though no cell is individually resolvable."
Re-extract it from `PAPER.md` if in doubt; it is not retyped anywhere.

## 4. Keywords and one-sentence summary

Suggested keywords, drawn from the paper's own contributions: *reproduction study; model-based
reinforcement learning; world models; uncertainty calibration; ensemble disagreement;
pre-registration*.

One-sentence summary: an independent reproduction of a released robotic world model that
reproduces its central training claim, and finds its evaluation misaligned by one step and the
uncertainty it penalises with miscalibrated as a scale that worsens with rollout depth.

## 5. Anonymity confirmation

Swept on 2026-09-27 at commit `c16267c`, twice and independently: by the builders' own scans, whose
planted probe fired on every run, and by sweep code written separately for the verification. The
channels covered were member paths, member text in several encodings, archive and member comments,
extra fields, nested archives, PNG text chunks, PDF text, the Info dictionary, XMP, link
annotations and inflated PDF streams. Terms: the author's name and its variants, the GitHub handle,
the git-log e-mail, both repository URLs, the Hugging Face URL, full archival identifiers, and any
7- to 40-character hexadecimal token resolving to a commit of this repository, of the pre-purge
backup, or of the Hugging Face repository.

**Result: 0 hits, in `PAPER.pdf` and in both bundles.** The final pass's second reviewer then wrote
its own sweep from scratch, proved it live with a marker caught in all 25 planted locations, among
them a nested archive and the PDF's metadata, and also returned 0 hits.

## 6. What this submission says about itself

A reviewer should meet these in the paper rather than discover them:

- **A build gate is published as failing.** `part_f_gate` requires that no regenerated value differ
  between the repository and a clean clone. 365 do, so it fails, and §8 says so. None of them is a
  measurement, a statistic or the verdict of a test; all are bookkeeping, and §8 names each kind.
  A reviewer who runs the gate in a pristine clone will see 5 of 8 checks pass, not 7: check 2 needs
  identifying strings supplied from outside the archive, and check 4b needs a gitignored archive
  that a clone does not carry. Both are stated in `docs/SUBMISSION_CHECKLIST.md`.
- **The reproduction figures cover what a clean-clone run regenerates and compares**, which §8 gives
  as 1.01% of the numeric values under `results/`, not the whole directory. That denominator is the
  set the comparison counts after its two stated exclusions: over every numeric value in the
  directory the share is 1.00%, and the 49 files a run rewrites hold 1.08%. The user ruled on
  2026-09-27 to record that wording rather than change the paper (`docs/SUBMISSION_CHECKLIST.md`,
  line 9). Counting the carried-in values would overstate the result about 99-fold, as the
  build-checks supplementary says.
- **The paper retracts twelve of its own claims** — six that withdraw numbers and six that
  withdraw framings — and keeps each in the ledger with the evidence that withdrew it, including
  its own claim to have pre-registered a rule it had not.

## 7. Reproducibility certification

The cover statement requests it explicitly. TMLR's certifications and the mechanism for requesting
them must be read off OpenReview at submission time rather than taken from this file: the names and
the request flow change between cycles, and nothing here has been checked against the live site.

## 8. Open items — the rulings first; nothing here blocks the upload

1. **The bare `swh:1:` prefix — RULED 2026-09-20, closed.** It occurs three times in each bundle: in
   `FINDINGS_LEDGER.md`, where the prose explains what a SWHID pattern needs in order to match; in a
   comment in `scripts/part_f_gate.py`; and in `GIT_LOG_ANONYMISED.txt`, as the subject of the
   commit that recorded this ruling. None is followed by a 40-character object name, so none
   resolves to anything on Software Heritage. The user ruled that a bare prefix with no object name
   is **not** an archival identifier. Nothing is scrubbed, no deny list changes, and the bundles and
   the §1 checksums stand exactly as committed.
2. **`submission_check`'s criterion E7 — RULED 2026-09-27, recorded as known.** It requires the one
   artifact excluded from numeric verification to be named in `PAPER.template.md`; the referee
   revision moved that naming into the build-checks supplementary, and the check did not follow. The
   script ships in neither bundle, so no referee can run it. A tested fix is kept at
   `/Users/Shared/rwm_verify/evidence/S25F/e7_fix.patch`, outside the repository.
3. **§8's denominator — RULED 2026-09-27, recorded as known.** §6 above states it exactly.
4. `results/supplementary_manifest.json` is off by one in two counts: a fresh build at this commit
   records 395 files for an archive of 396 members and 218 commits for a log of 217, a
   builder bug (`scripts/build_supplementary.py`). It ships inside both bundles. No number the paper
   prints comes from it. Fixing it would rewrite a compared artifact and require another clean-clone
   measurement.
5. `results/task_c1_claims_audit.json` is stale and accounts for 356 of the 365 differing values.
   Regenerating it would move a review finding, not merely refresh bookkeeping.
6. Figure-internal labels overlap in Figures 2 and 5, as the final pass's page-by-page read found
   them; earlier passes also recorded Figures 1 and 6. Page 27 prints one quantity's subscripts
   literally. Cosmetic; regenerating the figures would move artifacts that §8 counts, and the text
   is frozen.
7. The final checklist's remaining open items — four reports the pipeline writes that nothing
   tracks, the private folder clean-clone runs share by default, the checkout folder's name inside
   one artifact's citation strings, one artifact no stage writes, and the evidence showing
   repeatability rather than portability — are recorded in `docs/SUBMISSION_CHECKLIST.md` and
   `docs/DEFERRED.md`. None changes what is uploaded.

## 9. What must not happen

- **Nothing is pushed to the remote while this is under double-blind review.** The repository has a
  public origin under the author's account, and `main` is far ahead of it. A push would de-anonymise
  the submission.
- `docs/SUBMISSION_CHECKLIST.md`, `docs/DEFERRED.md` and `docs/COMMIT_LABEL_MAP.json` are internal
  and appear in no bundle. That was verified again in this pass.
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
