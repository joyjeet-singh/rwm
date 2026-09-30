# S11 final report — clean-clone verification of `presubmission` at c3b7e9d

**Status: BLOCKED.** Written 2026-09-30 by session S11. S11 made no fixes. Every figure below
was read from a file in the S11 evidence directory, `/Users/Shared/rwm_verify/evidence/PS11/`
(outside the repository), and each carries its source. That directory also holds the
driver script, every log and the full audit output (`workflow_result.json`).

**How it ran.**
- A mechanical driver (`s11_driver.zsh`) ran PLAN S11 step 2 and the comparison in one pass. It
  did not stop on a failing step. It wrote every exit code to `steps.tsv` and every output to a
  log.
- The audit and an independent adversarial re-derivation of every figure ran on Sonnet 5.5, as
  two read-only agents within §1.3's cap. The session itself ran on Opus 5.5.
- The adversarial pass confirmed 46 of 50 items. It corrected two wordings, and neither changed
  a figure or the verdict. It left 2 items unverifiable; they are marked where they appear.
- The repository was not touched: its status and HEAD were the same before and after
  (`repo_status_before.txt`, `repo_status_after.txt`).

## 1. Why S11 is blocked

1. **`part_f_gate` does not fail the same way it is published as failing.**
   - The published record (`results/part_f_gate.json`) fails check 4 alone.
   - Run with `pypdf` available, the gate now fails **checks 4 and 6**. Check 6 ("numeric
     consistency, abstract vs body") reports `asserted-but-absent-from-body ['v1_shared_pct0']`
     (`d_part_f_gate_ref.log:17-18`).
   - The abstract prints `{{v1_shared_pct0}}` = 89 (`PAPER.template.md:18`, "share 89% of their
     parameters"). The body prints only `v1_shared_pct` = 89.15 (for example `PAPER.md:98`).
   - The key entered in S4, and no session after S0 re-ran this gate. The fast build does not
     include it, and its committed record still says 48 pages and 12 abstract keys.
   - The defect is in the pushed template. It does not depend on the environment.
   - In the plan's environment the gate cannot run at all (item 3).
2. **The reproduction figures the paper prints disagree with what a clean clone measures.**
   - 10 of the 17 `ver_*` keys differ in the plan's environment, and 13 of 17 with `pypdf`
     (§3).
   - The paper says a quick run "rewrites 1.01% of the numeric values" and that "365 do"
     differ (`PAPER.md:1575`, `:1579`). This clone measures 0.59% and 364.
   - The printed figures are C3's measurement: `results/verify_reproduction.json` is unchanged
     since c16267c. Since then the pre-submission sessions added result files, and every one of
     them is carried into a clone (940,905 → 1,649,323 carried-in values).
   - This is a disagreement between two artifacts, a stop under §1.4.
3. **`pypdf` is imported by five scripts and is missing from `requirements.txt`.**
   - The five importers are `f5_pdf_channels.py:43`, `pdf_render_check.py:31`,
     `part_f_gate.py:74`, `submission_check.py:51` and `baseline_citations.py:65`.
     `requirements.txt` was last changed at db1c148 (2026-08-20).
   - A venv built as the README says produces four new failures:
     - stage 28b1, OK → FAILED;
     - `pdf_render_check.py` crashes;
     - `part_f_gate.py` crashes (in all three configurations, and in stage 29a);
     - `submission_check.py` has A1 PENDING (19/22 against S0's 20/22).
   - A diagnostic venv, identical except for `pypdf==6.16.1` (the project venv's version),
     clears all four (§6). It was a measurement, not a fix.

## 2. What holds

- **Measurements, statistics and verdicts that differ: 0.** 364 regenerated values differ, and
  every one is bookkeeping (`ver_part_sci` = 0, `ref_paper_numbers.json`). The audit also
  classified all 364 against `paper_numbers.py`'s `_BOOK` table independently: 0 unmatched.
  The adversarial pass re-derived both figures.

  | File | Differing | What differs |
  |---|---:|---|
  | `task_c1_claims_audit.json` | 355 | claim counts per sentence of this document |
  | `supplementary_manifest.json` | 4 | the archive's files, bytes and log commits |
  | `anon_bundle.json` | 2 | files staged and scrubbed |
  | `paper_numbers.json` | 2 | the build's input-audit counts |
  | `t5_anon_transcript.json` | 1 | quotations used in the paper |

- **The verifier is deterministic.** Three runs against a pristine reference clone, restored
  before each run, returned byte-identical JSON (`verify_agree.txt`). Its exit 1 means
  "differences found", as in every earlier clone.
- **Setup.** `setup.sh` fetched both upstreams at their pinned commits (13a798e9…, 18eebcdd…)
  and verified both reference artifacts by SHA-256 (`setup.log`).
- **The build.**
  - `PAPER.md`, `PAPER.tex`, `README.md` and `docs/APPENDIX_G_VARIANCE_ARITHMETIC.md` rebuild
    byte-identical to the committed files. So does `MODEL_CARD.md` once `runs/` is linked in.
  - Build 1 equals build 2 (`sha_*.txt`).
  - The PDF equals the committed one after its dates and ID are blanked (1,022,834 bytes each,
    `pdf_compare.txt`).
- **Anonymity.**
  - The anonymised bundle's own scan finds 0 residual hits, and its self-test catches the
    planted probe (`bundle_anon.log`).
  - The independent sweep finds 0 hits in `supplementary_anon.zip`, `supplementary.zip` and
    `PAPER.pdf`, over 9 named terms and 310 author-controlled commit IDs (`deny_list_sweep.log`).
  - The PDF text layer was scanned with `pypdf` in the diagnostic (`d_f5_pdf_channels.log`),
    and was clean.

## 3. Printed against measured

"Printed" is the committed `results/paper_numbers.json`. "Measured" is `paper_numbers.py` run in
the reference clone holding this clone's verification, taken right after `reproduce.sh`
(`ref_paper_numbers.json`). "With pypdf" is the diagnostic, taken after the build and bundle
steps (`ref_paper_numbers_diag.json`).

| Key | Printed | Measured | With pypdf |
|---|---:|---:|---:|
| `ver_files` | 49 | 48 | 49 |
| `ver_values` | 9,598 | 9,717 | 9,723 |
| `ver_identical` | 9,233 | 9,353 | 9,356 |
| `ver_pct` | 96.20 | 96.25 | 96.23 |
| `ver_close` | 0 | 0 | 0 |
| `ver_differing` | 365 | 364 | 367 |
| `ver_keys_lost` | 1 | 1 | 0 |
| `ver_keys_lost_files` | 1 | 1 | 0 |
| `ver_part_index` | 0 | 0 | 0 |
| `ver_part_dilution` | 0 | 0 | 0 |
| `ver_part_else` | 365 | 364 | 367 |
| `ver_part_sci` | 0 | 0 | 1 |
| `ver_copied` | 940,905 | 1,649,323 | 1,649,318 |
| `ver_all` | 950,503 | 1,659,040 | 1,659,041 |
| `ver_claim_pct` | 1.01 | 0.59 | 0.59 |
| `ver_overstate` | 99 | 171 | 171 |
| `ver_diff_nfiles` | 5 | 5 | 6 |

Where the stale figures are printed:
- `PAPER.md:1575` and `:1579`;
- `docs/BUILD_CHECKS.md:29-54`, `:147-149` and `:168`;
- `README.md:154-162`;
- the hand-written `docs/COVER_STATEMENT.md:50-54` and `docs/SUBMISSION_CHECKLIST.md:18-22`, `:59`,
  `:145`, `:175-184` and `:214-218`.

The "with pypdf" column is not the plan's measurement. The build and bundle steps had rewritten
some clone files before it ran. Its 1 in `ver_part_sci` is `anon_bundle.json`'s `.zip_bytes`,
the anonymised zip's size in bytes. `reproduce.sh`'s stage 28b does not write that key (it is
the key "lost" in the measured column). `make_anon_bundle.py --zip` does write it, and `_BOOK`
names no pattern for it. So a restatement must say which state it measures.

## 4. Every check with its status

S0 is from `BASELINE_S0.md`. "S11" is the plan's environment (`requirements.txt` only). "With
pypdf" is the diagnostic.

| Check | S0 | S11 | With pypdf | Status |
|---|---|---|---|---|
| `paper_numbers.py` | exit 0; byte-identical | exit 0; 6 of 2,178 keys differ from committed: 2 input-audit counts, 4 host-timing values | — | changed, benign |
| `build_paper.py` | exit 0; self-test 4/4; 132 typed | exit 0; self-test 7/7; 148 typed; `PAPER.md`, `PAPER.tex` byte-identical | — | changed, benign |
| `build_model_card.py` | exit 0; byte-identical (local `runs/`) | exit 0; differs without `runs/`; byte-identical with `runs/` linked | — | same |
| `build_readme.py` | exit 0; byte-identical | exit 0; byte-identical | — | same |
| `compile_paper.py` (TMLR) | PASS; 48 pages; 0 errors, overfull, underfull, warnings | PASS; **49 pages**; 0 errors, overfull, underfull, warnings; `\usepackage{tmlr}`, anonymous | — | changed, benign |
| `ledger_check.py` | PASS; 254 entries, 99 CONTRIB | PASS; 261 entries, 102 CONTRIB; 0 lacking evidence, 0 missing artifacts, 0 undischarged rules | — | changed, benign |
| `check_comparative_claims.py --self-test` | PASS; 60/60, 60/60 caught | PASS; 60/60, 60/60 caught | — | same |
| `typed_numeral_audit.py` | PASS; 686 typed | PASS; 711 typed; planted 12.7 caught | — | changed, benign |
| `restatement_index.py` | PASS | PASS | — | same |
| `horizon_sweep.py` | PASS; 0 findings | PASS; 0 findings | — | same |
| `xref_sweep.py` | PASS; 63 pointers, 0 suspect | PASS; 65 pointers, all ok, 0 suspect | — | changed, benign |
| `check_scope_audit.py` | PASS; 27 kinds, 0 unclassified | PASS; 27 kinds, 0 unclassified | — | same |
| `pdf_render_check.py` | PASS 5/5 | **exit 1**: no module `pypdf` | PASS 5/5 | **new failure** |
| `part_f_gate.py` | 7/7 run pass; check 4 not run | **exit 1**: no module `pypdf` (3 configurations) | **6/8: checks 4 and 6 fail** | **new failure** |
| `submission_check.py` | 20/22 (E7, C1 known) | 19/22 (**A1** `PYPDF_UNAVAILABLE`, E7, C1) | 20/22 (E7, C1) | **new failure** |
| `verify_reproduction.py` ×3 | — | byte-identical; 364 differing, 0 scientific | 367 differing, 1 at `.zip_bytes` (after the bundle steps) | holds |
| Anonymised bundle, builder scan and self-test | — | PASS; 0 residual; probe caught | — | pass |
| Deny-list sweep, independent | — | 0 hits in 3 targets | PDF text layer clean | pass |

Evidence for the table: `steps.tsv`; `b1_*`, `b2_*`, `g_*` and `d_*` logs;
`sha_model_card_runs_linked.txt`.

**Warning.** `pfg_C_s0cfg.json`, `pfg_C_clonecfg.json` and `pfg_R_fresh.json` are copies of the
committed record, made because the gate crashed before writing. They are not measurements. Only
`pfg_R_diag.json` and `pfg_C_diag.json` are real gate runs.

## 5. Page count, length, stages

- **Pages: 49** (S0: 48). Evidence: `b1_compile_paper.log`, `b2_compile_paper.log`.
  `pdf_compare.txt`'s "0 0" page line is a defect in the driver's regex, not a page count.
- **Body words.** FILE_MAP §13's command, `wordcount.txt`:
  - **27,035 to References, against S0's 27,387: −352 words (−1.29%).**
  - To "Data and code": 26,522 against 26,874.
  - The 30% target (at most 19,170 words) is missed by 7,865 words. The user accepted the
    shortfall as D7 on the figure 26,900. The body has grown 135 words since, in the resumed S10's
    edits, so `REVIEW.md` and D7 slightly understate it.
- **`reproduce.sh --quick --force`**: exit 1, 7,228 s. 97 stages: 54 OK, 36 skipped, 7 failed
  (S24T's clone of C3: 55 / 36 / 6; `stage_changes.txt`).

  | Stage | Before (S24T) | Now | Cause |
  |---|---|---|---|
  | 28b1 PDF channels | OK | **FAILED** | no module `pypdf` (new) |
  | 29a Part F gate | FAILED: check 2 not configured, check 4 not run | FAILED: crash on the `pypdf` import | known failure, new cause |
  | 29 readiness gate | FAILED 20/22 | FAILED 19/22 (A1) | known failure; A1 is new |
  | 28a3 pipeline coverage | FAILED: 1 uncovered | FAILED: 8 uncovered | known class, grown by 7 pre-submission artifacts |
  | 20n8 input discovery | FAILED: 15 unclassified | FAILED: 16 unclassified | known class; the new one is `paper_numbers.py:153`'s `step5_arm*` glob |
  | 20q1, 20n2 | FAILED | FAILED | same assertion and the same missing cache as before |

## 6. The pypdf diagnostic

A second venv, `requirements.txt` plus `pypdf==6.16.1`, re-ran:
- stage 28b1: OK;
- `pdf_render_check`: 5/5;
- `submission_check`: 20/22, as at S0;
- `part_f_gate`: it runs, and scores 6/8.

So the missing pin is the whole cause of the four environment failures. It is not the cause of
check 6, nor of the stale printed figures. Neither was measured, but by the audit's reading two
things would still stand with `pypdf` installed:
- Stage 29a would still fail check 2, because `reproduce.sh` runs it without `RWM_IDENT`. That
  is the known-by-ruling status.
- `submission_check.py:50` would still hard-code a `/tmp/pdfvenv/lib/python3.14/site-packages`
  path before its import.

## 7. Other findings a fix session needs

None of these blocks S11 alone. Each was recorded here rather than fixed.
- **Committed reports are stale against the pushed paper.** The verifier does not compare text
  reports. The clone regenerates:
  - `typed_numerals_report.txt`: 711 against the committed 686;
  - `appendix_g_rules_report.txt`: M-16 "SETTLED" against the returned "CANNOT BE SETTLED AT
    THIS BUDGET", and M-74 to M-76 absent;
  - `t1_bibliography_report.txt`: 16 against 18 entries;
  - `restatement_index_report.txt`;
  - `comparative_claims_report.txt`.

  Also stale: `results/pdf_channels.json` (48 pages) and `results/part_f_gate.json` (48 pages,
  12 abstract keys). The reports ship in both bundles. By the operational rule, `REPORT=` stages
  are regenerated with `./reproduce.sh --quick --force --stage N`.
- **The committed bundle records are one commit behind.** `supplementary_anon.zip`,
  `anon_bundle.json` and `supplementary_manifest.json` were built at 040d54c (499, 474 and 276);
  the clone builds 503, 478 and 278.
- **The four extra members are the known "four untracked reports".** A rebuilt anonymised zip
  carries `evidence_summary_report.txt`, `input_set_audit_report.txt`,
  `insample_framing_report.txt` and `m62_episode_clustering_report.txt`. They are neither
  committed nor ignored.
- **Stage 28a3's two artifacts with "writers none detected" do have writers.** They are
  `ledger_check.py` (`claims_to_evidence.json`) and `docs/presubmission/s8_runtime.py`
  (`presubmission_runtime.json`); the coverage script does not detect them.
- **Seven transitive packages float against the project venv.** They are filelock 4.0.6 against
  3.32.3, fonttools, fsspec, kiwisolver, pyparsing, pytz and tzdata (`venv_freeze.txt` against
  `projvenv_freeze.txt`). No measurement differs, so none has a visible effect. The six direct
  pins held.
- **`part_f_gate` reads the verification record of its own working directory.** Run inside a
  used clone, it reads the carried-in C3 file and prints "PREDATES". Its check 4 is meaningful
  only in the tree the verifier wrote into, with `CLONE_RESULTS` set.
- **Existing rulings bear on the restatement.** `docs/DEFERRED.md:181-191` and
  `docs/SUBMISSION_CHECKLIST.md:176-190` record, as known:
  - the 1.01% denominator;
  - the four untracked reports;
  - check 4's "PREDATES" inside a clone;
  - the input-audit counts rebuilding differently in a clean clone.

## 8. What the fix session ("S10-fix") has to settle, then S11 again

1. Pin `pypdf` in `requirements.txt`. The project venv has 6.16.1.
2. Resolve check 6 without loosening it:
   - the abstract can print `{{v1_shared_pct}}` (89.15%), as the body does;
   - or the body can carry the rounded figure.
3. Decide which state to restate §8 and its copies from:
   - after `reproduce.sh`, with `pypdf` installed, which will read 49 files;
   - and whether `.zip_bytes` belongs in `_BOOK`, as a property of an archive.
4. Restate the 17 `ver_*` keys by the restatement ordering:
   - make every prose edit first;
   - then measure a clean clone of the fixed commit;
   - then substitute, and regenerate the document-line index;
   - refresh the hand-written `COVER_STATEMENT.md` and `SUBMISSION_CHECKLIST.md` figures too.
5. Regenerate the stale `REPORT=` reports and gate records.
