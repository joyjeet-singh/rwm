# S11 final report — clean-clone verification of `presubmission` at 30910fb

**Status: COMPLETE.** This is the second S11 pass, written 2026-09-30. The first pass verified
c3b7e9d and was BLOCKED; its report is this file at commit 9bcb4a6. The fix session S10-fix then
resolved its four items B1–B4 (`DECISIONS_FOR_USER.md#S11-clean-clone-blocked`, `SESSION_LOG.md`
"## S10-fix").

This pass made no fixes. Every figure below was read from a file in the evidence directory
`/Users/Shared/rwm_verify/evidence/PS11b/` (outside the repository), which also holds the driver,
every log and the audit output (`workflow_result.json`).

**How it ran.**
- A mechanical driver (`s11b_driver.zsh`) ran PLAN S11 step 2 and the comparison on the pushed
  HEAD, 30910fb. It cloned from the public remote into a fresh directory and built a fresh venv
  from `requirements.txt`.
- The audit and an independent adversarial re-derivation ran on Sonnet 5.5, as two read-only agents
  within §1.3's cap. The adversarial pass confirmed all 21 items it re-derived. Its notes were
  minor, and they are included below.
- The repository was not touched (`repo_status_before.txt` equals `repo_status_after.txt`).

## 1. S11's criteria

| Criterion | Result | Source |
|---|---|---|
| Regenerated values that differ and are measurements, statistics or verdicts | **0** | `ver_part_sci` in `ref_paper_numbers.json`; independently, all 364 differing keys match a named bookkeeping pattern in `paper_numbers.py`'s `_BOOK` |
| Total differing values | **364** | `v1.json` |
| `part_f_gate` fails the same way it is published as failing | **yes**: 7/8, check 4 alone, on 364 differing; check 6 passes | `g_part_f_gate_ref.log`, `pfg_R_fresh.json`, against the committed `results/part_f_gate.json` |
| The paper prints what a clean clone measures | **17 of 17** reproduction figures, and all 2,178 `paper_numbers` keys | `fixedpoint.txt` |
| The verifier is deterministic | three runs byte-identical | `verify_agree.txt` |

The 364 differing values, by file, are all bookkeeping about this repository's own documents and
archives:

| File | Differing | What differs |
|---|---:|---|
| `task_c1_claims_audit.json` | 355 | claim counts per sentence of this document |
| `supplementary_manifest.json` | 4 | the archive's files, bytes and log commits |
| `anon_bundle.json` | 2 | files staged and scrubbed |
| `paper_numbers.json` | 2 | the build's input-audit counts |
| `t5_anon_transcript.json` | 1 | quotations used in the paper |

**Also outside the 364.**
- A further 13 differing values sit in carried-in files that failing stages rewrite, and they are
  held out of the claim: `input_set_audit.json` 10 and `part_f_gate.json` 3.
- One committed key is absent after regeneration: `anon_bundle.json`'s `.zip_bytes`, which only
  `make_anon_bundle.py --zip` writes.

## 2. Page count and length

- **Pages: 49** (S0: 48). 0 errors, 0 overfull, 0 underfull and 0 LaTeX warnings in both builds.
  Evidence: `b1_compile_paper.log`, `b2_compile_paper.log`. (`pdf_compare.txt`'s "0 0" page line
  is a defect in the driver's regex.)
- **Body words.** FILE_MAP §13's command, `wordcount.txt`, whose "c3b7e9d" label is inherited
  text; the figures are this clone's:
  - **27,039 to References, against S0's 27,387: −348 words (−1.27%).**
  - To "Data and code": 26,526 against 26,874.
  - The 30% target of at most 19,170 words is missed.
  - The user accepted the shortfall as D7 on the figure 26,900 (−1.8%). The body has since grown
    139 words, 4 of them in S10-fix's denominator wording.

## 3. Every check with its status

S0 is from `BASELINE_S0.md`. "Now" is this pass, in the plan's environment (`requirements.txt`
only, which now pins `pypdf`).

| Check | S0 | Now | Status |
|---|---|---|---|
| `paper_numbers.py` | exit 0; byte-identical | exit 0; after `reproduce.sh`, 6 of 2,178 keys differ from committed: 2 input-audit counts (recorded as rebuilding differently in a clean clone) and 4 host-timing values | changed, benign |
| `build_paper.py` | exit 0; self-test 4/4; 132 typed | exit 0; self-test 7/7; 148 typed; `PAPER.md`, `PAPER.tex` byte-identical to committed | changed, benign |
| `build_model_card.py` | exit 0; byte-identical (local `runs/`) | exit 0; differs without `runs/`; byte-identical with `runs/` linked | same |
| `build_readme.py` | exit 0; byte-identical | exit 0; byte-identical | same |
| `compile_paper.py` (TMLR) | PASS; 48 pages; 0 errors, overfull, underfull, warnings | PASS; 49 pages; 0 errors, overfull, underfull, warnings; `\usepackage{tmlr}`, anonymous; `/Author` empty | changed, benign |
| `ledger_check.py` | PASS; 254 entries, 99 CONTRIB | PASS; 261 entries, 102 CONTRIB; 0 lacking evidence; 0 undischarged rules | changed, benign |
| `check_comparative_claims.py --self-test` | PASS; 60/60, 60/60 caught | PASS; 60/60, 60/60 caught | same |
| `typed_numeral_audit.py` | PASS; 686 typed | PASS; 711 typed; planted 12.7 caught | changed, benign |
| `restatement_index.py` | PASS | PASS | same |
| `horizon_sweep.py` | PASS; 0 findings | PASS; 0 findings | same |
| `xref_sweep.py` | PASS; 63 pointers, 0 suspect | PASS; 65 pointers, 0 suspect | changed, benign |
| `check_scope_audit.py` | PASS; 27 kinds, 0 unclassified | PASS; 27 kinds, 0 unclassified | same |
| `pdf_render_check.py` | PASS 5/5 | PASS 5/5 | same |
| `part_f_gate.py`, S0's configuration | 7/7 run pass; check 4 not run | 7/7 run pass; check 4 not run | same |
| `part_f_gate.py`, on the fresh measurement | (published record: check 4 alone) | 7/8; check 4 alone, 364 differing | same way |
| `submission_check.py` | 20/22 (E7, C1 known) | 20/22 (E7, C1 known); A1 passes | same |
| `verify_reproduction.py` ×3 | — | byte-identical; 364 differing, 0 scientific | holds |
| Anonymised bundle, builder scan and self-test | — | 503 files staged; 0 residual; planted probe caught (9 hits) | pass |
| Deny-list sweep, independent | — | 0 hits in both zips and the PDF, over 9 named terms and 322 commit IDs | pass |

**Byte identity.** Evidence: `sha_committed.txt`, `sha_after_reproduce.txt`, `sha_build1.txt`,
`sha_build2.txt`. `PAPER.md`, `PAPER.tex`, `README.md` and `docs/APPENDIX_G_VARIANCE_ARITHMETIC.md`
are identical to the committed files throughout, and build 1 equals build 2 for every file. The
only differences from the committed files are explained:
- `MODEL_CARD.md` needs the gitignored `runs/`;
- `results/paper_numbers.json` and `docs/BUILD_CHECKS.md` differ by the two input-audit counts and
  the host-timing keys.

**PDF.** After its dates and ID are blanked, the clone's PDF is identical to the committed one
(1,022,814 bytes each, `pdf_compare.txt`).

## 4. `reproduce.sh --quick --force`

97 stages: 55 OK, 36 skipped (they need trained weights, which a clean clone lacks) and 6 failed.
That is exact agreement with the last good clean clones of C3 (S24T), and no stage changed state
(`stage_changes.txt`).

Each of the six failures has the same cause as before, as ruled or recorded:

| Stage | Cause |
|---|---|
| 20q1 | the no-quotation fallback's §6.1 pattern |
| 20n2 | the gitignored per-triple cache |
| 20n8 | unclassified pattern-based input discoveries |
| 28a3 | artifacts no `--quick` stage writes |
| 29a | no identity configured, and no clone given |
| 29 | E7 and C1 pending |

Two known failures carry more inside them than at C3. The C3-era counts come from the first S11
pass's report; S24T's log does not hold these stages' report bodies.
- **28a3** lists 8 uncovered artifacts, not 1. The 7 new ones are pre-submission artifacts:
  - five are written by scripts no `--quick` stage runs (the baseline and M/N-sweep evaluators and
    verdict scripts, and the alignment interval);
  - `presubmission_runtime.json` is written by `docs/presubmission/s8_runtime.py`, which is outside
    the stages;
  - `claims_to_evidence.json` *is* written by a stage: stage 21 runs `ledger_check.py`. That stage
    declares no output, so `pipeline_coverage` cannot see it.
- **20n8** has 16 unclassified discoveries, not 15. The new one is `paper_numbers.py:153`'s
  `step5_arm*` glob.

## 5. Environment

- Python 3.11 with a fresh venv. Every pin in `requirements.txt` held, `pypdf` 6.16.1 included,
  and no log shows an import error.
- Seven transitive packages float against the project venv: filelock 4.0.7 against 3.32.3,
  fonttools, fsspec, kiwisolver, pyparsing, pytz and tzdata. No measured value depends on them.
- `setup.sh` fetched both upstreams at their pinned commits and verified both reference artifacts
  by SHA-256.

## 6. Known and recorded; none blocks

- **The committed claims audit is stale against the template.** `results/task_c1_claims_audit.json`
  says 431 claims; a clone regenerates 463. It accounts for 355 of the 364 differing values, and is
  recorded in `docs/DEFERRED.md` and `docs/SUBMISSION_CHECKLIST.md`.
- **The four untracked reports.** A rebuilt anonymised zip has 503 members against the committed
  499, because a clone's `reproduce.sh` writes four reports that are neither committed nor
  ignored.
- **The bundle self-test's float-shaped probe** (`OUT_OF_SCOPE.md`). The pushed HEAD's prefix is
  checked at every push. A reviewer's clone of a commit whose prefix is digits plus one `e` would
  fail stage 28b.
- **README's lost-value parenthetical** (`OUT_OF_SCOPE.md`).
- **`docs/SUBMISSION_PACKAGE.md` is self-declared pre-edit** ("do not upload until they match").
  It still prints the C3 figures, "5 of 8 checks", and checksums of superseded files.
  **Refresh it before uploading.**
- **`docs/COVER_STATEMENT.md` is only partly current.** Its reproduction figures are current. Its
  other items (the retraction counts, "current at 48 pages") are stale, as recorded in
  `OUT_OF_SCOPE.md`. Both documents are excluded from both bundles.

## 7. What remains for the user

1. Send the author query (`docs/presubmission/AUTHOR_QUERY_ALIGNMENT.md`) if it has not gone.
2. Trigger a fresh Software Heritage archive of the final pushed state. §13's timestamp argument
   now needs it to cover the new pre-registrations.
3. Before uploading, refresh `docs/SUBMISSION_PACKAGE.md` against the files you upload: `PAPER.pdf`
   and `supplementary_anon.zip`, their sizes and SHA-256s, the abstract and the counts. Refresh the
   rest of `docs/COVER_STATEMENT.md` too.
4. Decide the `OUT_OF_SCOPE.md` items, among them the bundle self-test fix (plant the full hash).
