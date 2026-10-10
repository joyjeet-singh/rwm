"""Round 3, R8 step 5 (round 2 T11's t11_package.py, adapted): write docs/SUBMISSION_PACKAGE.md in full,
from the files it describes.

Every figure is computed here, from PAPER.pdf, PAPER.md, PAPER.tex, both zips, MODEL_CARD.md inside the
uploaded zip, results/paper_numbers.json, results/supplementary_manifest.json,
results/task_c1_claims_audit.json and the R8 evidence logs. None is typed. Every structural statement
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
# supplementary.zip stores every member under a top-level supplementary/ folder; compare the paths below it.
SP = {(x.split("/", 1)[1] if x.startswith("supplementary/") else x): x for x in S.namelist()}
assert len(SP) == len(S.namelist())
an, sn = set(A.namelist()), set(SP)
only_anon, only_supp = sorted(an - sn), sorted(sn - an)
assert sn < an and not only_supp, "supplementary.zip is no longer a strict subset of the anonymised bundle"
figs = [f for f in only_anon if re.fullmatch(r"figures/[^/]+\.png", f)]
all_figs = sorted(f for f in os.listdir("figures") if f.endswith(".png"))
assert len(figs) == len(all_figs), (figs, all_figs)
tex_figs = sorted(set(re.findall(r"figures/([\w.-]+\.png)", open("PAPER.tex").read())))
assert all(f"figures/{f}" in figs for f in tex_figs), tex_figs
top = ["README.md", "LICENSE", "MODEL_CARD.md", "CITATION.cff", "NOTICE"]
assert all(t in only_anon for t in top), [t for t in top if t not in only_anon]
shared_diff = sorted(m for m in sn if A.getinfo(m).CRC != S.getinfo(SP[m]).CRC)
# Round 3, R8: the manifest describes the archive it sits in, so its byte count cannot always be exact inside
# supplementary.zip (it alternated by one byte across builds). It may differ in that field alone; the uploaded
# bundle's copy must equal the committed manifest, and that must equal supplementary.zip's size on disk.
MAN = "results/supplementary_manifest.json"
assert set(shared_diff) <= {"GIT_LOG_ANONYMISED.txt", MAN} and "GIT_LOG_ANONYMISED.txt" in shared_diff, shared_diff
_ma, _ms = json.loads(A.read(MAN)), json.loads(S.read(SP[MAN]))
_mt = json.load(open(MAN))
assert _ma == _mt and _mt["bytes"] == os.path.getsize("supplementary.zip"), (_ma, _mt)
man_off = abs(_ms["bytes"] - _ma["bytes"]) if MAN in shared_diff else 0
assert MAN not in shared_diff or ([k for k in _ma if _ma[k] != _ms[k]] == ["bytes"] and man_off <= 8), (_ma, _ms)
_la = [l for l in A.read("GIT_LOG_ANONYMISED.txt").decode().splitlines() if l and not l.startswith("#")]
_ls = [l for l in S.read(SP["GIT_LOG_ANONYMISED.txt"]).decode().splitlines() if l and not l.startswith("#")]
assert len(_la) == len(_ls), (len(_la), len(_ls))     # the same commits; only the headers' lengths differ
_subj_diff = sum(1 for a, b in zip(_la, _ls) if a != b)
assert _subj_diff >= 1 and all("the first author" in a for a, b in zip(_la, _ls) if a != b)
shipped_pre = sorted(x for x in an if x.startswith("docs/presubmission/"))
assert shipped_pre and all(x in sn for x in shipped_pre), shipped_pre
SWH = json.load(open("results/swh_visit_check.json"))
swh_last = max(v["date_utc"] for v in SWH["visits"])[:10]
mc = A.read("MODEL_CARD.md").decode()
mc_sha = sorted(set(re.findall(r"\b[0-9a-f]{64}\b", mc)))

# ---- the paper -------------------------------------------------------------------------------------
md = open("PAPER.md").read()
title = re.search(r"^# (.+)$", md, re.M).group(1).strip()
abstract = " ".join(re.search(r"##\s*Abstract\s*\n+(.+?)\n\s*---", md, re.S).group(1).split())
ab_words = abstract.split()

# ---- the evidence --------------------------------------------------------------------------------
sweep = open(SWEEP).read()
m = re.search(r"TOTAL HITS ACROSS ALL TARGETS:\s*(\d+)", sweep)
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
# Round 3, R5 (H6): the manifest's two counts are counted, and the stage reports are gitignored.
_log_n = sum(1 for l in S.read(SP["GIT_LOG_ANONYMISED.txt"]).decode().splitlines() if l and not l.startswith("#"))
assert man["files"] == len(S.namelist()) and man["commits_in_log"] == _log_n, (man, len(S.namelist()), _log_n)
assert untracked == [], untracked
n_ret, n_fram = str(v("n_retractions_word")).lower(), str(v("n_retract_framing_word"))
fig_list = ", ".join(f"`{f.replace('.png', '')}`" for f in tex_figs)

L = f"""# Submission package

Everything needed to upload this submission, and nothing else. **Written for a person at a
browser.** Every figure here was read from the file it describes, at commit `{HEAD}`, by
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
   recorded in the repository (`results/swh_visit_check.json`) is of {swh_last}, before round 3's commits
   existed. These pushes must happen before the upload, because §9 forbids pushing once the paper is
   under review.

Then upload the two files in §1, checking their checksums first.

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
`LICENSE`, `MODEL_CARD.md`, `CITATION.cff` and `NOTICE`. {'Two shared members differ' if man_off else 'One shared member differs'} in content.
`GIT_LOG_ANONYMISED.txt` differs in its header, and in {_subj_diff} commit subjects where the anonymised builder
replaces the name of the original paper's correspondent with "the first author". Neither copy
identifies the submitting author.{(' `results/supplementary_manifest.json` differs in its byte count alone, by ' + str(man_off) + ' byte' + ('' if man_off == 1 else 's') + ': it describes the archive it sits in, so the copy inside `supplementary.zip` records that archive' + "'" + 's previous build, while the copy in the uploaded bundle, like the committed one, records it exactly.') if man_off else ''} Uploading it would therefore ship less, not more, and the checksum table
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

At `{HEAD}` it is {len(ab_words)} words by a whitespace split, within the 370-word cap the paper's own
check C12.1 enforces. It begins "{' '.join(ab_words[:10])}" and ends
"...{' '.join(ab_words[-10:])}". It is not retyped anywhere.

## 4. Keywords and one-sentence summary

Suggested keywords, drawn from the paper's own contributions: *reproduction study; model-based
reinforcement learning; world models; uncertainty calibration; ensemble disagreement;
pre-registration*.

One-sentence summary: an independent reproduction of a released robotic world model that
reproduces its central training claim, and finds its evaluation misaligned by one step and the
uncertainty it penalises with miscalibrated as a scale that worsens with rollout depth.

## 5. Anonymity confirmation

Swept at commit `{HEAD}`, twice and independently: by the builders' own scans (the anonymised
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
  between the repository and a clean clone. {v('ver_differing')} of {v('ver_values')} do, so it fails,
  and §8 says so. None of them is a measurement, a statistic or the verdict of a test; all are
  bookkeeping, and the build-checks supplementary (`docs/BUILD_CHECKS.md`) names each kind. With the identity strings supplied from outside the archive
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
4. **The claims audit was regenerated on the frozen text (round 3, R8; ruling U5) and is not
   reviewed.** It extracts {c1n} claims, {c1v.get('SUPPORTED', 0)} marked supported and
   {c1v.get('UNREVIEWED', 0)} unreviewed. The ruling records the unreviewed claims as known.
5. **`results/supplementary_manifest.json` is now exact** (round 3, R5): it records
   {man.get('files')} files for an archive of {len(sn)} members and {man.get('commits_in_log')} commits for
   a log of {_log_n}, both counted rather than derived. No number the paper prints comes from it.
6. **Figure-internal label overlaps were fixed in round 2, T8** (rendered Figures 2(a), 5 and 6; no
   plotted value changed). The PDF still prints the step-size quantity as the literal text
   `‖µ_t − µ_{{t−1}}‖`; cosmetic.
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
  appear in no bundle. `docs/presubmission/` is internal too, except the {len(shipped_pre)} records the
  paper cites, which both bundles ship deliberately ({', '.join(f'`{x.split("/")[-1]}`' for x in shipped_pre)}).
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
      f"anon-only {len(only_anon)}; shared differing {shared_diff} (manifest off by {man_off}); model-card sha256 {len(mc_sha)}; "
      f"abstract {len(ab_words)} words; gate {g.group(0)}; manifest exact; untracked none")
