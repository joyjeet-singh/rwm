# Round 5 — final report (G18, clean-clone verification)

**Result: PASS.** Every G18 criterion holds on a clean clone of `presubmission5` at `3ebf338`, the local HEAD when G18
started (G17b's last commit). The commits after it add only this report, the session log entry and the checkpoint;
none of them is a member of either zip, and none changes the paper or the upload files.

**How it ran.**
- The plan assigns G18 to Sonnet 5.5. It ran on Opus 5.5, in the same conversation as G15-fix and G17b, at the user's
  "then start G18 after step 5".
- **The clone is of the local repository, not of a pushed branch** (nothing is pushed before §0.5's after-G18 steps):
  a `file://` clone with its own object store, not the working copy.
- **The driver** is round 4's F12 driver, copied and adapted (`/Users/Shared/rwm_verify/evidence/R5G18/g18_driver.zsh`):
  - the branch `presubmission5`, and paths under `r5/G18` and `evidence/R5G18`;
  - G17b's N3 as the stage-tally reference;
  - round 5's G0 base (`796a026`) for the word count;
  - the printed-against-measured check over every `ver_*` key either side holds, not round 4's fixed list of 17;
  - the round-5 gates after the second build: `round5_gates.py`, its `--self-test`, `supplement_selftest.py`,
    `placeholders.py --self-test`;
  - `docs/SUPPLEMENT.md` swept beside both zips and the PDF, rebuilt and committed (PLAN G17 step 4), and hashed with
    the other built documents.
- **No edits.** The repository's status and HEAD were unchanged at the end, and a sweep of every record the driver
  wrote found no identity string.
- **Where:** the clone is at `/Users/Shared/rwm_verify/r5/G18/`, with a fresh venv from `requirements.txt`. All
  evidence is in `/Users/Shared/rwm_verify/evidence/R5G18/`.
- **Timing:** started 2026-10-24 23:17 +0530, ended 2026-10-25 02:47; `reproduce.sh` took 7,816 s, the two sweeps
  2,070 s and 1,064 s. Nothing else ran on the machine.

## The criteria

| criterion | result | evidence (`evidence/R5G18/`) |
|---|---|---|
| scientific differing values = 0 | **pass**: 0. Of 18,327 regenerated values, 18,324 are bitwise identical (99.98%) and 3 differ, all in `results/supplementary_manifest.json` (bytes, uncompressed, commits_in_log), which a clone's longer git log changes. 1 key lost (`anon_bundle.json` zip_bytes). The record is byte-identical to G17b's N2 and N3 | `verify_1.log`; `verify_agree.txt`: v1 = v2 = v3, byte-identical |
| every reproduction figure the paper prints equals what the clone measures | **pass**: 31 of 31 `ver_*` keys. No other paper-number key differs between the commit's record and the reference built on the clone's measurement | `fixedpoint.txt` |
| the PDF equals the committed one after blanking dates and ID | **pass**: identical after blanking CreationDate, ModDate and ID (1,308,073 bytes each); 56 pages each (pypdf) | `pdf_compare.txt` |
| 0 deny-list hits | **pass**: 0 in the rebuilt `supplementary_anon.zip`, `supplementary.zip`, `PAPER.pdf` and `docs/SUPPLEMENT.md`, and 0 in the committed `supplementary_anon.zip`, `PAPER.pdf` and `docs/SUPPLEMENT.md` (hit set: 9 named terms, 729 author-controlled commit ids) | `deny_list_sweep.log`, `deny_list_sweep_committed.log` |
| every round-5 stage runs or skips as designed | **pass**: of the 16 stages round 5 added, 20w9 (N9) and 20w10 (N10) OK; 20v0–20v7 (X9–X11) and 20w7, 20w8, 20w11–20w14 (N7, N8, N11–N14) SKIP: "needs trained weights in runs/ (gitignored, not in a clean clone)" | `reproduce.log`, `stages.json` |
| every round-5 gate passes | **pass**: pages 11.67/12, abstract 210/5, ids 0, once 0, sig 0, keys missing 0; the gates' self-test PASS; the supplement self-test PASS (every planted violation caught, every touched file restored byte-identically); placeholders 20/20 | `g_round5_gates.log`, `g_round5_gates_selftest.log`, `g_supplement_selftest.log`, `g_placeholders_selftest.log` |
| `part_f_gate` fails exactly as §8 publishes it | **pass**: 7/8, check 4 alone (the clean-clone check, which requires no regenerated value to differ), on the reference and in the clone. With the identity strings and no clone results: 7/7, 1 not run | `g_part_f_gate_ref.log`, `g_part_f_gate_clonecfg.log`, `g_part_f_gate_s0cfg.log` |
| `submission_check` returns what `SUBMISSION_CHECKLIST.md` records | **pass**: 21/22, C1 (the claims audit: 387 claims, 29 supported, 358 unreviewed) pending by ruling U5, as the checklist's round-5 section records | `g_submission_check.log` |

**Stage tally.** Of 134 stages, 66 were OK, 64 skipped and 4 failed (20q1, 20n2, 29a, 29). That is identical to G17b's
three clean clones (N1–N3) and to G17's M3: no stage changed status, and none regressed. The four failures are the
ones every final report since round 2 records. 29a and 29 are `part_f_gate` and `submission_check`, failing as above.
20q1's fallback pattern no longer occurs in the template (`OUT_OF_SCOPE.md`, G13). 20n2 is round 3's known failure.

**Builds in the clone.**
- The two fast builds are byte-identical.
- `PAPER.md`, `PAPER.tex`, `README.md`, `docs/BUILD_CHECKS.md`, `docs/SUPPLEMENT.md` and
  `docs/APPENDIX_G_VARIANCE_ARITHMETIC.md` equal the committed files.
- `MODEL_CARD.md` equals the committed file once `runs/` is linked, because it records checkpoint hashes.
- `results/paper_numbers.json` differs only in three host-sourced keys that the verifier excludes by provenance and that
  no built document prints: `time_rel_hi`, `time_rel_lo` and `ver_tb_ran` (as in round 4).
- The compiled PDF: 0 errors, 0 overfull boxes, 0 LaTeX warnings.

**The rebuilt anonymised bundle** has the same 630 members as the committed one, and 18 of them differ in bytes. All
18 are the clone's own regenerated records: round 4's 16 (host and timing records, `manifest.json`,
`v3_metric_definitions.json`, the PDF channel records, `paper_numbers.json`'s three host keys, the bundle bookkeeping
and the anonymised git log, X6's and X7's `git_head`) and N9's and N10's artifacts, the two round-5 stages that
regenerate without weights. The upload is the committed bundle, whose checksum is verified below.

## Against G0

G0 measured round 4's frozen paper at `796a026` (`BASELINE_G0.md`). Round 4's F12 ran the gates on the same commit;
its figures fill the G0 column where `BASELINE_G0.md` reports only "pass".

| | G0 (`796a026`) | G18 (`3ebf338`) |
|---|---:|---:|
| pages | 75 | 56 |
| References start on page | 27 | 12 |
| main-content pages (`round5_gates.py`'s measure; Y1 caps it at 12) | 26.9 | 11.67 |
| body words, title to "References" (`LENGTH_LOG.md`'s measure) | 18,644 | 7,659 |
| body words, "1. Introduction" to "References" | 18,289 | 7,393 |
| abstract words / numerals (C12.1; Y2 caps them at 210 / 5) | 300 / 19 | 210 / 5 |
| `ids`: ledger and rule IDs in the body | 51 (26 M-, 25 X) | 0 |
| `ids`: capitalised verdict labels | 8 | 0 |
| `sig`: decimals with more than two significant figures | 514 | 0 |
| `once`: over-repeated interval and numeric keys | not gated (59 interval keys, up to 5 times each) | 0 |
| `keys`: base keys missing (of 1,489) | — | 0 |
| comparative claims verified, and corruptions caught | 68/68, 68/68 | 68/68, 68/68 |
| check kinds (`check_scope_audit`), unclassified | 35, 0 | 35, 0 |
| `ledger_check` | PASS (288 entries) | PASS (310 entries, 117 CONTRIB) |
| typed-numeral audit | pass (self-test caught) | pass (self-test caught) |
| restatement index | CLEAN, 0 typed restatements, 0 ambiguous numerals | CLEAN, 0 typed restatements, 0 ambiguous numerals |
| horizon sweep | 0 findings | 0 findings |
| xref sweep: semantic / artifact / repo / upstream / new-docs, suspect | 39 / 51 / 3 / 20 / 2, 0 | 37 / 38 / 3 / 21 / 2, 0 (9 semantic pointers reviewed) |
| rendered-PDF check | PASS (5/5) | PASS (5/5) |
| `part_f_gate` (identity configured, no clone results) | 7/7, 1 not run | 7/7, 1 not run |
| `part_f_gate` (with a clean clone's results) | 7/8, check 4 alone | 7/8, check 4 alone |
| `submission_check` | 21/22 (C1) | 21/22 (C1) |
| reproduction figures (§8): values; identical; differing; scientific | 16,405; 16,402; 3; 0 | 18,327; 18,324; 3; 0 |

G0's 17,804 body words used round 2's `t6_words.py` (Introduction to "Data and code"); the round-5 paper has no "Data
and code" heading (it moved to the supplement), so that script cannot count it, and the rows above use the two
measures that apply to both.

## The upload files

Verified in the clone against the committed files, and equal to `docs/SUBMISSION_PACKAGE.md`:

| file | size | SHA-256 |
|---|---:|---|
| `PAPER.pdf` | 1,308,073 bytes, 56 pages | `34a975ebfe9bd9b0bb7ec2335a79dfdd41fe1057171cdf9183c2c5cc48c617d0` |
| `supplementary_anon.zip` | 28,890,722 bytes, 630 members | `61fcbb84bc39e293890daa46178d9a57e5ead202da0ee1c70809e9e6e30f50f8` |

Do not rebuild before uploading: every build re-stamps the PDF's date, which changes its checksum.

## What round 5 leaves open

`round5/OUT_OF_SCOPE.md` holds 24 items, none of which changes what is uploaded; the checklist's round-5 section lists
each. Among them, for a session allowed to change scope wording: six appendix sentences (H, L, N) that call all ten
episodes the released checkpoint's training data, against §3.2, and "33 runs for §4.1–§6" (Apps J, K), which excludes
the fold runs. Also open: the 358 unreviewed claims (ruling U5); the TMLR blog since 15 October, unread (Medium
answered 403; read it in a browser); the alignment query's date, if the paper is to give one.

## What only the user can do (PLAN §0.5, "After G18"), in this order

1. **Merge, push, re-upload, archive.** Fast-forward or merge `presubmission5` into `main` and push, if you still
   want the repository's state public before review. Then re-upload `MODEL_CARD.md` to Hugging Face, and trigger a
   Software Heritage archive of the pushed commit: the paper says the repository was archived before submission.
2. **Quota and profiles.** Every author checks their remaining 2026 TMLR quota and completes their OpenReview profile
   (`round4/TMLR_CHECK.md` gives the procedure).
3. **The form.** The title and abstract from `docs/SUBMISSION_PACKAGE.md`; **"Regular submission"** (main content
   11.67 pages, at most 12); competing interests from G17's draft (Y11, in `docs/SUBMISSION_PACKAGE.md`); human
   subjects "N/A"; suggested action editors.
4. **Upload** `PAPER.pdf` and `supplementary_anon.zip` last, after checking both against the SHA-256s above, without
   rebuilding them.

Nothing is pushed once the paper is under double-blind review, so step 1 comes before step 4.
