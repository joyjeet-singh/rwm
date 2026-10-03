# Round 2 — final report (T12)

Clean-clone verification of the pushed `presubmission2` HEAD, `8c2c903`, on 2026-10-04.

- **Method.** Round 1's verification driver, copied and adapted as `evidence/R2T12/t12_driver.zsh`: branch, paths, the stage-tally reference and the word-count baseline. The evidence is outside the repository, in the session evidence folder `R2T12/`.
- **The run.** Two fresh clones from the public remote and a fresh venv from `requirements.txt`. Then, in order:
  1. `setup.sh`;
  2. `reproduce.sh --quick --force`;
  3. the verifier three times against a pristine reference;
  4. the full paper build and every gate;
  5. both bundles and the independent deny-list sweep;
  6. the PDF comparison.
- **Who ran it.** Run on Opus 5.5, where the plan assigns Sonnet 5.5, in the same conversation as T3–T11 at the user's request.
- **No edits.** T12 changed nothing in the repository except this report and its log entry. The driver confirmed the repository's status and HEAD unchanged.

## Verdict: PASS — all six criteria

| criterion (PLAN T12 item 3) | result | evidence |
|---|---|---|
| scientific differing values = 0 | **PASS**. The three verifier runs are byte-identical: 56 files, 15,521 values, 15,516 bitwise identical (99.97%), 0 within tolerance, 5 differing. All 5 are bundle bookkeeping (`supplementary_manifest.json` 4, `anon_bundle.json` 1); scientific: **0** | `verify_agree.txt`, `v1.json`, `ref_paper_numbers.json` |
| `part_f_gate` fails exactly as §8 publishes it | **PASS**. On the fresh measurement (the run in the pristine reference, right after the verifier) it gives 7/8, with check 4 (clean-clone identity) alone failing. In T0's configuration (identity supplied, no clone results) it gives 7/7, with 1 not run | `g_part_f_gate_ref.log`; `g_part_f_gate_s0cfg.log`; `g_part_f_gate_clonecfg.log` repeats the first in the clone |
| every reproduction figure the paper prints equals what the clone measures | **PASS**. Printed equals measured on **17 of 17** reproduction keys, and all 2,320 `paper_numbers` keys equal the reference build's. This is the commit T11 predicted would reproduce, now measured | `fixedpoint.txt` (the 17); `fullkeys.txt` (all keys; the driver's own comparison skips the other `ver_*` keys) |
| the PDF equals the committed one after blanking dates and ID | **PASS**. The clone's PDF is byte-identical to the committed one after blanking: 57 pages, 1,064,242 bytes each | `pdf_compare.txt` (blanked identity; its regex page counter reads 0 and is wrong); `pdf_pages_pypdf.txt` (57 and 57) |
| 0 deny-list hits | **PASS**. 0 hits in the bundles and PDF the clone rebuilt (`supplementary_anon.zip`, `supplementary.zip`, `PAPER.pdf`), with the anonymised builder's planted probe detected and its scan passing. 0 hits, too, in the committed files that are uploaded, swept directly: `supplementary_anon.zip` (SHA-256 a712eddf…) and `PAPER.pdf` (50df8761…) | `deny_list_sweep.log`, `bundle_anon.log`; `sweep_committed.log` |
| `submission_check` returns what `SUBMISSION_CHECKLIST.md` records | **PASS**. 21/22, with only C1 pending (526 claims: 59 supported, 467 unreviewed, by ruling U5). E7 passes | `g_submission_check.log` |

**Also confirmed:**

- **Stage tally.** `reproduce.sh` ran 111 stages: 62 OK, 45 skipped (weights absent) and the 4 known failures (20q1, 20n2, 29a, 29), the same tally as T11's M3.
- **Builds.** The clone's two builds are byte-identical. PAPER.md, PAPER.tex, README.md, BUILD_CHECKS.md and the variance-arithmetic supplementary equal the committed files. MODEL_CARD.md equals the committed one once weights are present: a clone has none, and the card records their absence.
- **The clone's own `paper_numbers.json`** differs from the committed one in 4 keys, all host timing (`time_rel_hi`, `time_rel_lo`, `time_worst_cfg`, `ver_tb_ran`). None is printed.
- **A bundle rebuilt in the clone** has 519 members against the committed 515: the clone's 4 untracked reports. Of the members both share, 14 differ: build records, the anonymised git log, host-timing outputs and one time-bounded figure. It has 0 identifying strings. The file to upload is the committed `supplementary_anon.zip`, whose checksum `docs/SUBMISSION_PACKAGE.md` records.

## Pages and words

| | T0 (`6bee218`) | now (`8c2c903`) | change |
|---|---:|---:|---:|
| PDF pages | 49 | 57 | +8 (T4 +1, before any new appendix; T5–T7 +7, as Appendices H–T were written) |
| body, Introduction to "Data and code" (FILE_MAP §13) | 26,526 | 20,771 | −5,755 (−21.7%) |
| body, Introduction to References | 27,039 | 21,284 | −5,755 |

The target was a body of at most 19,000 words (ruling U3); the shortfall of 1,771 words is reported, not forced. In the body: T3–T5 added 1,177 words (mainly T4's text for the new analyses, +831); T6–T7 cut 7,537 by moving detail into appendices; T8–T10 added 605 (T8 74, the X1 Part C sentence and its discharge; T9 232, mostly restored qualifiers; T10 299, scoping qualifiers). Net −5,755.

## Every gate, against T0

| gate | T0 (`BASELINE_T0.md`) | now, in the clean clone |
|---|---|---|
| `ledger_check.py` | PASS, 0 rows out of date | PASS, 0 rows out of date |
| `check_comparative_claims.py --self-test` | 60/60 claims, 60/60 corruptions caught | **62/62** claims, **62/62** corruptions caught |
| `typed_numeral_audit.py` | self-test passed | self-test passed |
| `restatement_index.py` | CLEAN: 0 typed restatements, 0 ambiguous | CLEAN: 0 typed restatements, 0 ambiguous |
| `horizon_sweep.py` | 0 findings | 0 findings |
| `xref_sweep.py` | semantic 10, artifact 33, repo 3, all ok, 0 suspect | semantic 13, artifact 43, repo 3, all ok, **0 suspect** |
| `check_scope_audit.py` | 27 kinds, 0 unclassified | 29 kinds, 0 unclassified |
| `pdf_render_check.py` | RENDERED-PDF PASS | RENDERED-PDF PASS |
| `part_f_gate.py` (T0's configuration) | 7/7, 1 not run | 7/7, 1 not run |
| `part_f_gate.py` (against a clone's results) | not run at T0 | 7/8, check 4 alone, as §8 publishes |
| `submission_check.py` | 20/22 | **21/22** (E7 fixed in T8; C1 pending by U5) |
| clean-clone reproduction | round 1: 364 of 9,717 differing (S11 second run) | **5 of 15,521** differing, 0 scientific; printed = measured, 17/17 |

## What round 2 did

- **New analyses, post hoc (T1).** The alignment cost by horizon (N1), nRMSE pooled as §3.1 defines it (N2), and the sweep at equal training compute (N3).
- **Rule X1 (T2, T8).** It was pre-registered before its data and discharged with **NOT RESCUED BY THE SETTINGS TRIED** (ledger M-83).
- **Front-matter claims (T3–T4, T9).** Rewritten to the evidence: the alignment cost, the configuration and architecture verdicts, the M-23 seed, and every qualifier the T9 audit found missing except the abstract's RSSM caveat, which C12.1's word cap keeps in contribution 3, §3.2, §5.3 and Appendix D.
- **Appendix H (T5).** It covers 15 contribution-tagged findings that had not reached the main text. The 6 absent entries left out are listed with reasons in `round2/COVERAGE.md`.
- **The length pass (T6–T7).** It moved detail into new Appendices I–T and the existing C and F, and §6 was renumbered once.
- **Pipeline hygiene, the model card and figure label collisions (T8).** The review caught and reverted a gate that T8 had loosened.
- **Fresh-eyes review (T10).** It fixed 19 mismatches (tables against sentences, captions and verdict strings) and every failing Annex 4 checklist item. The most substantive was §5's floor claims, which hold only on the 400-step unit.
- **Freeze, measurement and restatement (T11).** The claims audit was regenerated, and stale records were regenerated before measuring. §8 was restated from a clean clone, to the fixed point that this report confirms by measurement. The bundles and the package documents are current.

## Before the upload — the user's steps (PLAN §0.4)

1. **Update GitHub's default branch** (`main`) from `presubmission2`.
2. **Re-upload `MODEL_CARD.md`** to the Hugging Face model repository.
3. **Trigger a Software Heritage archive of the final pushed commit.** The paper says the repository was archived before submission, and the only recorded visit is 2026-08-21, before round 2's pre-registrations.
4. **Send the author query** (`docs/presubmission/AUTHOR_QUERY_ALIGNMENT.md`) if it has not gone.
5. **Upload `PAPER.pdf` and `supplementary_anon.zip`**, checking both against the SHA-256s in `docs/SUBMISSION_PACKAGE.md` first. Do not rebuild before uploading: every build re-stamps the PDF's date, which changes its checksum.

Steps 1–3 push or publish, and nothing may be pushed once the paper is under double-blind review; do all four before step 5, as `docs/SUBMISSION_PACKAGE.md` requires.

## Open items (none blocks the upload)

The current list is `docs/SUBMISSION_CHECKLIST.md`'s round-2 section. In brief:

- C1's 467 unreviewed claims, by ruling U5.
- The supplementary manifest is off by one in two counts.
- Four reports `reproduce.sh` writes are neither committed nor gitignored.
- The literal `‖µ_t − µ_{t−1}‖` in the PDF.
- The private folder clean-clone runs share.
- The checkout folder's name inside one artifact's citations.
- Repeatability on one host rather than portability.

Round 2's deferred items are in `round2/OUT_OF_SCOPE.md`.
