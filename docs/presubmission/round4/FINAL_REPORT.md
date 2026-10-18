# Round 4 — final report (F12, clean-clone verification)

**Result: PASS.** Every F12 criterion holds on a clean clone of `presubmission4` at `796a026`, the final local HEAD.

**How it ran.**
- The plan assigns F12 to Sonnet 5.5. It ran on Opus 5.5, in the same conversation as F0–F11, at the user's "Start F12".
- **The clone is of the local repository, not of a pushed branch.** Workplan §6 forbids pushing before the user's own steps, so the clone was taken through a `file://` URL: a real clone with its own object store, not the working copy.
- **The driver** is round 3's R9 driver, copied and adapted (`/Users/Shared/rwm_verify/evidence/R4F12/f12_driver.zsh`):
  - the branch, and the local URL in place of `git ls-remote`;
  - paths, with the clone's origin path redacted in its records;
  - F11's M3 as the stage-tally reference;
  - round 4's F0 base (`18cc54f`) for the word count.
- **No edits.** The repository's status and HEAD were unchanged at the end, and a sweep of every record the driver wrote found no identity string.
- **Where:** the clone is at `/Users/Shared/rwm_verify/r4/F12/`, with a fresh venv from `requirements.txt`. All evidence is in `/Users/Shared/rwm_verify/evidence/R4F12/`.
- **Timing:** started 2026-10-18 18:03 +0530, ended 21:16.

## The criteria

| criterion | result | evidence (`evidence/R4F12/`) |
|---|---|---|
| scientific differing values = 0 | **pass**: 0. Of 16,405 regenerated values, 16,402 are bitwise identical (99.98%) and 3 differ. All 3 are in `results/supplementary_manifest.json` (bytes, uncompressed, commits_in_log), which a clone's longer git log changes. 1 key lost (`anon_bundle.json` zip_bytes) | `verify_1.log`; `verify_agree.txt`: v1 = v2 = v3, byte-identical |
| `part_f_gate` fails exactly as §8 publishes it | **pass**: 7/8, check 4 alone (the clean-clone check, which requires no regenerated value to differ), both on the reference and in the clone. With the identity strings and no clone results: 7/7, 1 not run | `g_part_f_gate_ref.log`, `g_part_f_gate_clonecfg.log`, `g_part_f_gate_s0cfg.log` |
| every reproduction figure the paper prints equals what the clone measures | **pass**: 17 of 17 keys (`ver_*`). No other paper-number key differs between the commit's record and the reference built on the clone's measurement | `fixedpoint.txt` |
| the PDF equals the committed one after blanking dates and ID | **pass**: identical after blanking CreationDate, ModDate and ID (1,208,426 bytes each); 75 pages each (pypdf) | `pdf_compare.txt` |
| 0 deny-list hits in the rebuilt and the committed upload files | **pass**: 0 in the rebuilt `supplementary_anon.zip`, `supplementary.zip` and `PAPER.pdf`, and 0 in the committed `supplementary_anon.zip` and `PAPER.pdf` | `deny_list_sweep.log`, `deny_list_sweep_committed.log` |
| `submission_check` returns what `SUBMISSION_CHECKLIST.md` records | **pass**: 21/22, with C1 (the claims audit) pending by ruling U5, as the checklist's round-4 section records | `g_submission_check.log` |
| every new round-4 stage runs or skips as designed | **pass**: 20u3 (X6) and 20u4 (X7) OK. 20u1 (X3), 20u2 (X4), 20u5 (X8) and 20u6 (N5) SKIP: "needs trained weights in runs/ (gitignored, not in a clean clone)". Stage 11k, the round-4 training queue, is skipped by `--quick` with the other training stages | `reproduce.log`, `stages.json` |

**Stage tally.** `reproduce.sh --quick --force` took 8,017 s. Of its 118 stages, 64 were OK, 50 skipped and 4 failed (20q1, 20n2, 29a, 29). That is identical to F11's three clean clones (M1, M2, M3): no stage changed status, and none regressed.

**Builds in the clone.**
- The two fast builds are byte-identical.
- `PAPER.md`, `PAPER.tex`, `README.md`, `docs/BUILD_CHECKS.md` and `docs/APPENDIX_G_VARIANCE_ARITHMETIC.md` equal the committed files.
- `MODEL_CARD.md` equals the committed file once `runs/` is linked, because it records checkpoint hashes.
- `results/paper_numbers.json` differs only in three host-sourced keys that the verifier excludes by provenance and that nothing prints: `time_rel_hi`, `time_rel_lo` and `ver_tb_ran`.
- The compiled PDF has 0 overfull boxes and 0 LaTeX warnings.

**The rebuilt anonymised bundle** has the same 566 members as the committed one, and 16 of them differ in bytes. All 16 are the clone's own regenerated records:
- host and timing records (`step4_5_timing.json`, `step4_5_report.txt`, the two `step4_4_overfit_*` records and their figure);
- `manifest.json`;
- `v3_metric_definitions.json`, which embeds the checkout folder's name;
- the PDF channel records;
- `paper_numbers.json`'s three host keys;
- the bundle bookkeeping files and the anonymised git log;
- X6's and X7's artifacts, which record the clone's commit in their `git_head` string.

That is round 3's 14 plus the two round-4 stages that regenerate without weights. The upload is the committed bundle, whose checksum is verified below.

## Against F0

| | F0 (`18cc54f` / `4fce5a1`, round 3's final text) | F12 (`796a026`) |
|---|---:|---:|
| pages | 62 | 75 |
| "Data and code" and References start on page | 32 | 27 |
| main text, "1. Introduction" to "Data and code" (ruling W6's measure; `round2/t6_words.py`) | 20,745 | 17,804 |
| main text to "References" | 21,230 | 18,289 |
| abstract words / numerals (C12.1; caps then 370 / 26, now 320 / 26) | 370 / 23 | 300 / 19 |
| comparative claims verified, and corruptions caught | 65/65, 65/65 | 68/68, 68/68 |
| check kinds (`check_scope_audit`), unclassified | 32, 0 | 35, 0 |
| `ledger_check` | PASS | PASS (288 entries) |
| typed-numeral audit | pass (self-test caught) | pass (self-test caught) |
| restatement index | CLEAN, 0 typed restatements | CLEAN, 0 typed restatements, 0 ambiguous numerals |
| horizon sweep | 0 findings | 0 findings |
| xref sweep: semantic / artifact / repo / upstream / new-docs, suspect | 15 / 45 / 3 / 20 / 2, 0 | 39 / 51 / 3 / 20 / 2, 0 |
| rendered-PDF check | PASS | PASS (5/5) |
| `part_f_gate` (identity configured, no clone results) | 7/7, 1 not run | 7/7, 1 not run |
| `part_f_gate` (with a clean clone's results) | not run at F0 | 7/8, check 4 alone |
| `submission_check` | 21/22 (C1) | 21/22 (C1) |
| reproduction figures (§8): values; identical; differing; scientific | 15,652; 15,649; 3; 0 | 16,405; 16,402; 3; 0 |

The main text is 17,804 words against ruling W6's target of at most 16,000. The user ruled the target editorial and accepted 17,804 (`DECISIONS.md#F8-length`). TMLR sets no length limit, and this is a long submission (`TMLR_CHECK.md`).

## The upload files

Verified in the clone against the committed files, and equal to `docs/SUBMISSION_PACKAGE.md`:

| file | size | SHA-256 |
|---|---:|---|
| `PAPER.pdf` | 1,208,426 bytes, 75 pages | `4dbc6ac09ebdaf7dd2d6bd85d1e12c7257f13c26f0f188978255d2e50537633f` |
| `supplementary_anon.zip` | 24,671,492 bytes, 566 members | `9967128e593fd3d01670a9c425a712eb6c3b365f778a3022a27c70698e7989b8` |

Do not rebuild before uploading: every build re-stamps the PDF's date, which changes its checksum. Both files are within the submission form's limits (PDF 50 MB, supplement 100 MB, one ZIP).

## Round 4 in summary (workplan §7)

- **Manuscript and bundles:** `PAPER.pdf` and `supplementary_anon.zip` at the repository root (`supplementary.zip` is built but not uploaded; `docs/SUBMISSION_PACKAGE.md` says why).
- **TMLR format:** the official style files are unmodified (byte-identical to the official repository's `main`), the submission is anonymous, of any length, and a "Long submission". Main text 17,804 words; abstract 300 words.
- **The rules, as the locked framing states them:**
  - **X3:** `REPLICATES ACROSS FOLDS`, +2.2275 [+1.3683, +3.5053] at h = 368 over 20 trajectories, at 2,500 iterations rather than 10,000.
  - **X4:** `PARTIAL`, on parameter count only. The MLP stays behind, and the transformer cannot be told apart.
  - **X5:** not run, and never pre-registered. The released data do not record the velocity command its reward terms score against (D-38).
  - **X6:** `DISAGREEMENT BEATS STEP SIZE` on 70 shorter units at h = 100, +0.2816 [+0.1978, +0.3896]. The h = 368 margin is not re-tested.
  - **X7:** `WITHIN BAND AT 6 OF 6 HORIZONS`. This is pooled epistemic coverage over 20 trajectories, on a checkpoint that trained on all ten episodes.
  - **X8:** `SAME VERDICT` for its four rules only; 22 of their alongside readings change.
  - **N5 and N6:** post hoc.
- **CPU:**
  - the round-4 training queue: 30 runs, 26.5 h (X3 24 runs, 17.7 h; X4 6 runs, 8.8 h; Appendix B);
  - F11's three clean clones: about 2 h 15 min each;
  - F12's: about 3 h 15 min with the bundles and sweeps.

  The workplan's three optional inference-only sensitivities (§5) were not run: they are exploratory and not required.
- **Clean clone and anonymity:** above. 0 scientific differences, and 0 deny-list hits.

## What round 4 leaves open

`round4/OUT_OF_SCOPE.md` holds eight items, none of which blocks the upload; the checklist's round-4 section lists each. Round 3's four items are closed.

## What only the user can do (PLAN §0.4, "After F12"), in this order

1. **Merge.** Fast-forward or merge `presubmission4` into GitHub's default branch `main`, and push. The user approved this on 17 October. Round 4's commits exist only locally until then. Two tracked internal files carry a local home path (`OUT_OF_SCOPE.md`, F7), which a push publishes in the repository, though not in the submission.
2. **Re-upload `MODEL_CARD.md`** to the Hugging Face model repository. It has changed since round 3, and the user approved this on 17 October.
3. **Archive.** Trigger a Software Heritage archive of the final pushed commit. The paper says the repository was archived before submission, and the latest visit the repository records is of 2026-08-21.
4. **Author query.** Send it (`docs/presubmission/AUTHOR_QUERY_ALIGNMENT.md`) if it has not gone.
5. **Quota and profiles.** Every author checks their remaining 2026 TMLR quota (TMLR's `coauthor_counts.py`, with that author's own OpenReview login, then the calculator) and completes their OpenReview profile.
6. **Upload** `PAPER.pdf` and `supplementary_anon.zip`, checking both against the SHA-256s above first. On the form, choose "Long submission"; competing interests and human-subjects reporting are required fields.

Steps 1–3 push or publish. Nothing may be pushed once the paper is under double-blind review, so steps 1–5 come before step 6.
