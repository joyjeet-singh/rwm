"""Round 2, T11 step 5: write docs/SUBMISSION_PACKAGE.md in full, from the files it describes.

Every figure is computed here, from PAPER.pdf, PAPER.md, PAPER.tex, both zips, MODEL_CARD.md inside the
uploaded zip, results/paper_numbers.json, results/supplementary_manifest.json,
results/task_c1_claims_audit.json and the T11 evidence logs. None is typed. Every structural statement
the document makes about the bundles is asserted first, so a statement that has stopped being true
stops the script instead of being written. Run from the repository root, after the bundles are built
and committed.

    usage: t11_package.py <sweep-log> <gate-log> <submission-check-log> <clone-status-file>
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import zipfile

from pypdf import PdfReader

SWEEP, GATE, SUBCHECK, CLONE_STATUS = sys.argv[1:5]
OUT = "docs/SUBMISSION_PACKAGE.md"
N = json.load(open("results/paper_numbers.json"))
v = lambda k: N[k]["value"] if isinstance(N[k], dict) else N[k]  # noqa: E731
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()  # noqa: E731
HEAD = subprocess.run(["git", "rev-parse", "--short=7", "HEAD"], capture_output=True, text=True).stdout.strip()
assert not subprocess.run(["git", "status", "--porcelain", "--", "PAPER.pdf", "supplementary_anon.zip"],
                          capture_output=True, text=True).stdout.strip(), "PAPER.pdf or the zip is not committed"

# ---- the files -----------------------------------------------------------------------------------
pdf_pages = len(PdfReader("PAPER.pdf").pages)
assert pdf_pages == int(v("pdf_pages")), (pdf_pages, v("pdf_pages"))
A, S = zipfile.ZipFile("supplementary_anon.zip"), zipfile.ZipFile("supplementary.zip")
an, sn = set(A.namelist()), set(S.namelist())
only_anon, only_supp = sorted(an - sn), sorted(sn - an)
assert sn < an and not only_supp, "supplementary.zip is no longer a strict subset of the anonymised bundle"
figs = [f for f in only_anon if re.fullmatch(r"figures/[^/]+\.png", f)]
all_figs = sorted(f for f in os.listdir("figures") if f.endswith(".png"))
assert len(figs) == len(all_figs), (figs, all_figs)
tex_figs = sorted(set(re.findall(r"figures/([\w.-]+\.png)", open("PAPER.tex").read())))
assert all(f"figures/{f}" in figs for f in tex_figs), tex_figs
top = ["README.md", "LICENSE", "MODEL_CARD.md", "CITATION.cff", "NOTICE"]
assert all(t in only_anon for t in top), [t for t in top if t not in only_anon]
shared_diff = sorted(m for m in sn if A.getinfo(m).CRC != S.getinfo(m).CRC)
mc = A.read("MODEL_CARD.md").decode()
mc_sha = sorted(set(re.findall(r"\b[0-9a-f]{64}\b", mc)))

# ---- the paper -------------------------------------------------------------------------------------
md = open("PAPER.md").read()
title = re.search(r"^# (.+)$", md, re.M).group(1).strip()
abstract = " ".join(re.search(r"##\s*Abstract\s*\n+(.+?)\n\s*---", md, re.S).group(1).split())
ab_words = abstract.split()

# ---- the evidence --------------------------------------------------------------------------------
sweep = open(SWEEP).read()
m = re.search(r"TOTAL[^\n]*?(\d+)\s*hits?", sweep)
assert m and int(m.group(1)) == 0, "the independent sweep did not report 0 hits"
gate = open(GATE).read()
g = re.search(r"(\d+)/(\d+) checks pass", gate)
g_fail = re.findall(r"^\s+FAIL\s+(\S+)", gate, re.M)
assert g and g_fail == ["4."], (g, g_fail)            # check 4 alone, as section 8 publishes it
sub = open(SUBCHECK).read()
sc = re.search(r"(\d+)\s*/\s*(\d+)", sub.split("\n")[-2] if sub.strip() else "")
assert int(v("ver_part_sci")) == 0, "section 8 would not be all bookkeeping"
C1 = json.load(open("results/task_c1_claims_audit.json"))
c1n, c1v = C1["n_claims"], C1["by_verdict"]
man = json.load(open("results/supplementary_manifest.json"))
untracked = [l.split()[-1].replace("results/", "") for l in open(CLONE_STATUS).read().splitlines()
             if l.startswith("??")]
n_ret, n_fram = str(v("n_retractions_word")).lower(), str(v("n_retract_framing_word"))
fig_list = ", ".join(f"`{f.replace('.png', '')}`" for f in tex_figs)

L = f"""# Submission package

Everything needed to upload this submission, and nothing else. **Written for a person at a
browser.** Every figure here was read from the file it describes, at commit `{HEAD}`, by
`docs/presubmission/round2/t11_package.py`, which also asserts each statement below about the two
bundles before writing it; the checksums were computed for this document rather than copied from an
earlier session. This replaces the round-1 version, which predated the pre-submission edit.

**Nothing blocks the upload.** Every item that needed a ruling has one; the items that remain under
"Open items" below are recorded, and none of them changes what is uploaded.

---

## 1. The files to upload

| file | what it is | size | SHA-256 |
|---|---|---|---|
| `PAPER.pdf` | the submission, {pdf_pages} pages, TMLR submission mode | {os.path.getsize('PAPER.pdf'):,} bytes | `{sha('PAPER.pdf')}` |
| `supplementary_anon.zip` | the anonymised supplementary bundle, {len(an)} members | {os.path.getsize('supplementary_anon.zip'):,} bytes | `{sha('supplementary_anon.zip')}` |

**`supplementary.zip` is NOT uploaded — and not because it is unsafe.** Both bundles are anonymised:
each is built by a script that refuses to write the archive if any staged file carries the author
name or a repository URL, and an independent sweep of both returns 0 hits (§5). The reason is
narrower. It is gitignored, so unlike the two files above it is not tracked at any commit; its
{len(sn)} members are a strict subset of the anonymised bundle's {len(an)}, with {len(only_supp)} files
unique to it; and the {len(only_anon)} the anonymised bundle alone carries include all {len(figs)}
figures — among them the {len(tex_figs)} the paper's LaTeX names ({fig_list}) — plus `README.md`,
`LICENSE`, `MODEL_CARD.md`, `CITATION.cff` and `NOTICE`. {len(shared_diff)} shared members differ in
content ({', '.join(f'`{x}`' for x in shared_diff) or 'none'}), each a record of the build that wrote
it, and none identifying. Uploading it would therefore ship less, not more, and the checksum table
above covers the anonymised bundle.

**One linkage ships with the bundle that is uploaded, knowingly.** `MODEL_CARD.md` is in the
anonymised bundle and not in the other, and it carries {len(mc_sha)} checkpoint `sha256` values, two of
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
since `{HEAD}`; do not upload until they match. Every build recompiles `PAPER.pdf` with a new date
and ID, so a rebuild alone changes its checksum.

## 2. Title

{title}

## 3. Abstract

Extract it from the paper rather than retyping it, with

```
python3 - <<'EOF'
import re
md = open("PAPER.md").read()
print(" ".join(re.search(r"##\\s*Abstract\\s*\\n+(.+?)\\n\\s*---", md, re.S).group(1).split()))
EOF
```

At `{HEAD}` it is {len(ab_words)} words by a whitespace split (the paper's own check, C12.1, counts
{v('ab_words') if 'ab_words' in N else 'within its 370-word cap'}). It begins "{' '.join(ab_words[:10])}" and ends
"...{' '.join(ab_words[-10:])}". It is not retyped anywhere.

## 4. Keywords and one-sentence summary

Suggested keywords, drawn from the paper's own contributions: *reproduction study; model-based
reinforcement learning; world models; uncertainty calibration; ensemble disagreement;
pre-registration*.

One-sentence summary: an independent reproduction of a released robotic world model that
reproduces its central training claim, and finds its evaluation misaligned by one step and the
uncertainty it penalises with miscalibrated as a scale that worsens with rollout depth.

## 5. Anonymity confirmation

Swept at commit `{HEAD}`, twice and independently: by the builders' own scans, whose planted probe
fired on every run (the anonymised bundle's probe now plants a full commit hash, round 2 T8), and by
sweep code written separately for verification. The channels covered were member paths, member text
in several encodings, archive and member comments, extra fields, nested archives, PNG text chunks,
PDF text, the Info dictionary, XMP, link annotations and inflated PDF streams. Terms: the author's
name and its variants, the GitHub handle, the git-log e-mail, both repository URLs, the Hugging Face
URL, full archival identifiers, and any 7- to 40-character hexadecimal token resolving to a commit of
this repository.

**Result: 0 hits, in `PAPER.pdf` and in both bundles.**

## 6. What this submission says about itself

A reviewer should meet these in the paper rather than discover them:

- **A build gate is published as failing.** `part_f_gate` requires that no regenerated value differ
  between the repository and a clean clone. {v('ver_differing')} of {v('ver_values')} do, so it fails,
  and §8 says so. None of them is a measurement, a statistic or the verdict of a test; all are
  bookkeeping, and §8 names each kind. With the identity strings supplied from outside the archive
  and a clean clone's results, {g.group(1)} of {g.group(2)} checks pass, check 4 alone failing. A
  reviewer who runs it in a pristine clone without those inputs will see fewer pass: check 2 needs
  the identity strings, and check 4b needs the gitignored `supplementary.zip`.
- **The reproduction figures cover what a clean-clone run regenerates and compares**, which §8 gives
  as {v('ver_claim_pct')}% of the numeric values under `results/` that the comparison counts, not the
  whole directory. Counting the values a clone merely carries in would overstate the result about
  {v('ver_overstate')}-fold, as the build-checks supplementary says.
- **The paper withdraws {n_ret} of its own claims on evidence and {n_fram} framings**, and keeps each
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
4. **The claims audit was regenerated on the frozen text (round 2, T11; ruling U5) and is not
   reviewed.** It extracts {c1n} claims, {c1v.get('SUPPORTED', 0)} marked supported and
   {c1v.get('UNREVIEWED', 0)} unreviewed. The ruling records the unreviewed claims as known.
5. **`results/supplementary_manifest.json`** records {man.get('files')} files for an archive of
   {len(sn)} members and {man.get('commits_in_log')} commits for its log; the builder's arithmetic is
   recorded in `docs/SUBMISSION_CHECKLIST.md`. No number the paper prints comes from it.
6. **Figure-internal label overlaps were fixed in round 2, T8** (rendered Figures 2(a), 5 and 6; no
   plotted value changed). The PDF still prints the step-size quantity as the literal text
   `‖µ_t − µ_{{t−1}}‖`; cosmetic.
7. **{len(untracked)} reports `reproduce.sh` writes are neither committed nor gitignored**
   ({', '.join(f'`{u}`' for u in untracked)}); a clone's archive therefore holds more files than the
   tree's. The private folder clean-clone runs share by default, the checkout folder's name inside
   one artifact's citation strings, and the evidence showing repeatability rather than portability
   are recorded in `docs/SUBMISSION_CHECKLIST.md` and `docs/DEFERRED.md`. None changes what is
   uploaded.

## 9. What must not happen

- **Nothing is pushed to the remote while this is under double-blind review.** The repository has a
  public origin under the author's account; a push during review would de-anonymise the submission.
- `docs/SUBMISSION_CHECKLIST.md`, `docs/DEFERRED.md`, `docs/COMMIT_LABEL_MAP.json` and
  `docs/presubmission/` are internal and appear in no bundle.
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
"""
open(OUT, "w").write(L)
print(f"  wrote {OUT}: PDF {pdf_pages} pages; anon {len(an)} members; supp {len(sn)}; "
      f"anon-only {len(only_anon)}; shared differing {shared_diff}; model-card sha256 {len(mc_sha)}; "
      f"abstract {len(ab_words)} words; gate {g.group(0)}; untracked {untracked}")
