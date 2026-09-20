# Submission package

Everything needed to upload this submission, and nothing else. **Written for a person at a
browser.** Every figure here was read from the file it describes, at commit `e38a10e`, and the
checksums were computed for this document rather than copied from an earlier session.

**The upload is blocked on one ruling.** See "Open items" below: the bare `swh:1:` occurrences
have not been ruled on. Nothing else stands in the way.

---

## 1. The files to upload

| file | what it is | size | SHA-256 |
|---|---|---|---|
| `PAPER.pdf` | the submission, 49 pages, TMLR submission mode | 1,022,372 bytes | `36753353466c675d384784a6eec8b2f41811b9ad169c4920f5229c4a3fa67f66` |
| `supplementary_anon.zip` | the anonymised supplementary bundle, 411 members | 12,420,192 bytes | `ecfa0f84236db4b042311cb0c59be34efcb904891b61034db82dbb80712401e8` |

**`supplementary.zip` is NOT uploaded — and not because it is unsafe.** Both bundles are
anonymised: each is built by a script that refuses to write the archive if any staged file carries
the author name or a repository URL, and a sweep of the working-tree copy returns 0 hits, as §5
records. The reason is narrower. It is gitignored, so unlike the two files above it is not tracked
at any commit; its 387 members are a strict subset of the anonymised bundle's 411, with 0 files
unique to it; and the 24 the anonymised bundle alone carries include all 13 figures — among them
the 6 the paper's LaTeX names — plus `README.md`, `LICENSE`, `MODEL_CARD.md`, `CITATION.cff` and
`NOTICE`. Only two shared members differ in content at all, `results/supplementary_manifest.json`
and `GIT_LOG_ANONYMISED.txt`, and neither difference is identifying. Uploading it would therefore
ship less, not more, and the checksum table above covers the anonymised bundle.

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

and confirm the two lines match the table above. If they do not, the working tree is not at
`e38a10e` or something has rebuilt an artifact; do not upload until they match.

## 2. Title

A one-step evaluation misalignment and a σ = 0 optimum: an independent reproduction of a released robotic world model

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
`/Users/Shared/rwm_verify/evidence/S28/abstract.txt`, outside the repository
(219 words). It begins "We rebuild the proprioceptive dynamics model of the
*Robotic World Model*" and ends "...brings every held-out coverage estimate near nominal, though no
cell is individually resolvable." Re-extract it from `PAPER.md` if in doubt; it is not retyped
anywhere.

## 4. Keywords and one-sentence summary

Suggested keywords, drawn from the paper's own contributions: *reproduction study; model-based
reinforcement learning; world models; uncertainty calibration; ensemble disagreement;
pre-registration*.

One-sentence summary: an independent reproduction of a released robotic world model that
reproduces its central training claim, and finds its evaluation misaligned by one step and the
uncertainty it penalises with miscalibrated as a scale that worsens with rollout depth.

## 5. Anonymity confirmation

Swept on 2026-09-19 at commit `e38a10e`, twice and independently: by the builders' own scans, whose
planted probe fired on every run, and by sweep code written separately for the verification. The
channels covered were member paths, member text in several encodings, archive and member comments,
extra fields, nested archives, PNG text chunks, PDF text, the Info dictionary, XMP, link
annotations and inflated PDF streams. Terms: the author's name and its variants, the GitHub handle,
the git-log e-mail, both repository URLs, the Hugging Face URL, full archival identifiers, and any
7- to 40-character hexadecimal token resolving to a commit of this repository, of the pre-purge
backup, or of the Hugging Face repository.

**Result: 0 hits, in `PAPER.pdf` and in both bundles.** The reviewing sweep proved itself live with
twelve planted probes, all twelve caught, including one identity fragmented across a string
concatenation and one buried inside a nested archive.

## 6. What this submission says about itself

A reviewer should meet these in the paper rather than discover them:

- **A build gate is published as failing.** `part_f_gate` requires that no regenerated value differ
  between the repository and a clean clone. 314 do, so it fails, and §8 says so. None of them is a
  measurement, a statistic or the verdict of a test; all are bookkeeping, and §8 names each kind.
  A reviewer who runs the gate in a pristine clone will see 5 of 8 checks pass, not 7: check 2 needs
  identifying strings supplied from outside the archive, and check 4b needs a gitignored archive
  that a clone does not carry. Both are stated in `docs/SUBMISSION_CHECKLIST.md`.
- **The reproduction figures cover what a clean-clone run rewrites**, which is 0.98% of the values
  under `results/`, not the whole directory. Counting the carried-in values would multiply the
  denominator about 102-fold. §8 gives both.
- **The paper retracts twelve of its own claims** — six that withdraw numbers and six that
  withdraw framings — and keeps each in the ledger with the evidence that withdrew it, including
  its own claim to have pre-registered a rule it had not.

## 7. Reproducibility certification

The cover statement requests it explicitly. TMLR's certifications and the mechanism for requesting
them must be read off OpenReview at submission time rather than taken from this file: the names and
the request flow change between cycles, and nothing here has been checked against the live site.

## 8. Open items — the upload is blocked on the first

1. **The bare `swh:1:` prefix has not been ruled on.** It occurs twice in each bundle, in
   `FINDINGS_LEDGER.md` and in `scripts/part_f_gate.py`, with no 40-character object name after
   either, so no occurrence resolves to an archival identifier. The reading proposed — that these
   are therefore not archival identifiers — is **unconfirmed**. Nothing was scrubbed and no deny
   list was changed. **Decide this before uploading.**
2. `results/supplementary_manifest.json` records 386 files where the archive holds 387, and 200 log
   commits where its log holds 199. It ships inside both bundles. No number the paper prints comes
   from it. Fixing it would rewrite a compared artifact and require another clean-clone measurement.
3. `results/task_c1_claims_audit.json` is stale and accounts for 304 of the 314 differing values.
   Regenerating it would move a review finding, not merely refresh bookkeeping.
4. Figure-internal labels overlap bars or lines in Figures 1, 2, 5 and 6: a bar's value label, an
   annotation struck through by a dashed line, a legend entry struck through by a dashed line, and a
   legend drawn over the bars it describes. Cosmetic; regenerating those figures would move
   artifacts that §8 counts. `docs/SUBMISSION_CHECKLIST.md` still lists three of the four.

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
