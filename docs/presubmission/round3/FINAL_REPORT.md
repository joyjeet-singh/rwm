# Round 3 — final report (R9, clean-clone verification)

**Result: PASS.** Every R9 criterion holds on a clean clone of the pushed `presubmission3` HEAD `41b73ee`.

**How it ran.**
- The plan assigns R9 to Sonnet 5.5. It ran on Opus 5.5, in the same conversation as R0–R8, at the user's instruction.
- The driver is round 2 T12's, copied and adapted (`/Users/Shared/rwm_verify/evidence/R3R9/r9_driver.zsh`): branch, paths, R8's M3 as the stage-tally reference, R0's base as the word-count baseline, and a deny-list sweep of the committed upload files.
- It made no edit to the repository; the repository's status and HEAD were unchanged at the end.
- Clone at `/Users/Shared/rwm_verify/r3/R9/`, fresh venv from `requirements.txt`. All evidence is in `/Users/Shared/rwm_verify/evidence/R3R9/`.

## The criteria

| criterion | result | evidence (`evidence/R3R9/`) |
|---|---|---|
| scientific differing values = 0 | **pass**: 0. Of 15,652 values regenerated, 15,649 are bitwise identical (99.98%) and 3 differ, all in `results/supplementary_manifest.json` (bytes, uncompressed, commits_in_log, which a clone's longer git log changes); 1 key lost (`anon_bundle.json` zip_bytes) | `verify_1.log`; `verify_agree.txt`: v1 = v2 = v3, byte-identical |
| `part_f_gate` fails exactly as §8 publishes it | **pass**: 7/8, check 4 alone (the clean-clone check, which requires no regenerated value to differ). With the identity strings and no clone results: 7/7, 1 not run | `g_part_f_gate_clonecfg.log`, `g_part_f_gate_ref.log`, `g_part_f_gate_s0cfg.log` |
| every reproduction figure the paper prints equals what the clone measures | **pass**: 17 of 17 keys (`ver_*`); no other paper-number key differs between the commit's record and the reference built on the clone's measurement | `fixedpoint.txt` |
| the PDF equals the committed one after blanking dates and ID | **pass**: identical after blanking CreationDate, ModDate and ID (1,137,559 bytes each); 62 pages each | `pdf_compare.txt` |
| 0 deny-list hits in the rebuilt and the committed upload files | **pass**: rebuilt `supplementary_anon.zip`, `supplementary.zip` and `PAPER.pdf`: 0; committed `supplementary_anon.zip` and `PAPER.pdf`: 0 | `deny_list_sweep.log`, `deny_list_sweep_committed.log` |
| `submission_check` returns what `SUBMISSION_CHECKLIST.md` records | **pass**: 21/22, C1 (the claims audit) pending by ruling U5, as the checklist's round-3 section records | `g_submission_check.log` |
| X2's `--quick` stage runs or skips as designed | **pass**: stage 20t14 SKIP ("needs trained weights in runs/ … Its committed result is present: results/action_sensitivity.json") | `reproduce.log`, `stages.json` |

**Stage tally:** `reproduce.sh --quick --force` took 7,974 s and ran 112 stages: 62 OK, 46 skipped and 4 failed (20q1, 20n2, 29a, 29). That is identical to R8's three clean clones (M1, M2, M3), and no stage changed status.

**Builds in the clone:**
- the two fast builds are byte-identical;
- `PAPER.md`, `PAPER.tex`, `README.md`, `docs/BUILD_CHECKS.md` and `docs/APPENDIX_G_VARIANCE_ARITHMETIC.md` equal the committed files;
- `MODEL_CARD.md` equals the committed file once `runs/` is linked, because it records checkpoint hashes;
- `results/paper_numbers.json` differs only in three host-sourced keys the verifier excludes by provenance (`time_rel_hi`, `time_rel_lo`, `ver_tb_ran`), none of them printed.

**The rebuilt anonymised bundle** has the same 517 members as the committed one, and 14 of them differ in bytes, the same count as round 2's T12. They are the clone's own regenerated host and timing records (`step4_5_timing.json`, `step4_5_report.txt`, the two `step4_4_overfit_*` records and their figure, `manifest.json`, `v3_metric_definitions.json`, which embeds the checkout folder's name), its PDF channel records, `paper_numbers.json`'s three host keys, the bundle bookkeeping files, and the anonymised git log. The upload is the committed bundle, whose checksum is verified below.

## Against R0

| | R0 (`32adcda`, round 2's final) | R9 (`41b73ee`) |
|---|---:|---:|
| pages | 57 | 62 |
| main text, "1. Introduction" to "Data and code" (ruling V8's measure) | 20,771 | 20,745 |
| main text to "References" | 21,284 | 21,230 |
| abstract words / numerals (C12.1; caps 370 / 26) | 370 / 23 | 370 / 23 |
| comparative claims verified, and corruptions caught | 62/62, 62/62 | 65/65, 65/65 |
| check kinds (`check_scope_audit`), unclassified | 29, 0 | 32, 0 |
| `ledger_check` | PASS | PASS |
| typed-numeral audit | pass (self-test caught) | pass (self-test caught) |
| restatement index | CLEAN, 0 typed restatements | CLEAN, 0 typed restatements |
| horizon sweep | 0 findings | 0 findings |
| xref sweep: semantic / artifact / repo / upstream / new-docs, suspect | 13 / 43 / 3 / 20 / 2, 0 | 15 / 45 / 3 / 20 / 2, 0 |
| rendered-PDF check | PASS | PASS |
| `part_f_gate` (identity configured, no clone results) | 7/7, 1 not run | 7/7, 1 not run |
| `part_f_gate` (with a clean clone's results) | not run at R0 | 7/8, check 4 alone |
| `submission_check` | 21/22 (C1) | 21/22 (C1) |
| reproduction figures (§8): values; identical; differing; scientific | 15,521; 15,516; 5; 0 | 15,652; 15,649; 3; 0 |

The main text is 26 words under ruling V8's limit of 20,771. The 20,000-word aim is not met.

## The upload files

Verified in the clone against the committed files, and equal to `docs/SUBMISSION_PACKAGE.md`:

| file | size | SHA-256 |
|---|---:|---|
| `PAPER.pdf` | 1,137,677 bytes, 62 pages | `df9a1288410c4b0d8aa8bc34e3417a34cbba754eee14cc2bb26c3c98c87d41fb` |
| `supplementary_anon.zip` | 19,545,482 bytes, 517 members | `bee2f6ef4639ceb22495ef718bf266108a13d281d42d15a1b3d97714c0b15b94` |

Do not rebuild before uploading: every build re-stamps the PDF's date, which changes its checksum.

## What round 3 leaves open

`round3/OUT_OF_SCOPE.md` holds four items, none of which blocks the upload:
- **R0:** BUILD_CHECKS' list of claims withdrawn on evidence has no length guard.
- **R5:** §6.7's per-episode difficulty averages the stale and causal action offsets. This is a question for the user.
- **R6:** §5.2 gives rule M-74's alongside readings at the verdict level only.
- **R7:** Appendix H's R-46 row has no recorded n_independent.

## What only the user can do (PLAN §0.4), in this order

1. Fast-forward or merge `presubmission3` into GitHub's default branch `main`.
2. Re-upload `MODEL_CARD.md` to the Hugging Face model repository; it gained rule X2's result.
3. Trigger a Software Heritage archive of the final pushed commit. §13 says the repository was archived before submission, and the latest visit the repository records is of 2026-08-21.
4. Send the author query (`docs/presubmission/AUTHOR_QUERY_ALIGNMENT.md`) if it has not gone.
5. Upload `PAPER.pdf` and `supplementary_anon.zip`, checking both against the SHA-256s above first.

Steps 1–3 push or publish. Nothing may be pushed once the paper is under double-blind review, so steps 1–4 come before step 5.
