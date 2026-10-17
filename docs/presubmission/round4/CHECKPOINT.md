# Round-4 checkpoint (workplan §2): F11 → F12, 2026-10-17

**State.** Branch `presubmission4`, last log entry **F11 — COMPLETE**. Every commit since `110ecd7` is local. The tree is clean.
- **Upload files** (`docs/SUBMISSION_PACKAGE.md`): `PAPER.pdf` 75 pages, 1,208,426 bytes, sha256 `4dbc6ac0…`; `supplementary_anon.zip` 566 members, 24,671,492 bytes, sha256 `9967128e…`.
- **§8** prints M2's record (a clean clone of `0d948df`). M3, a clean clone of `06a2a94`, matched all 17 reproduction keys, and its record is byte-identical to M2's.
- **Text frozen:** body 17,804 words; abstract 300 words, 19 numerals.

**User approval (17 Oct, chat).** Pushing and merging the final output, the model-card re-upload to Hugging Face, and checking every author's quota. All three come after F12 passes, as PLAN §0.4 orders them. F12 itself pushes nothing.

**Read first, nothing else.**
1. `round4/PLAN.md`: §1 and "F12 — Clean-clone verification".
2. The last entry of `round4/SESSION_LOG.md`.
3. `round4/TMLR_CODEX_WORKPLAN.md` §4D, §6 and §7.

**Exact next action: F12 (no edits).**
- **Clone the LOCAL repository's HEAD** (`file://` URL, as `evidence/R4F11/measure.zsh` does) into `/Users/Shared/rwm_verify/r4/F12/`, not a pushed one (workplan §6). Use a fresh venv.
- **Driver.** Copy `evidence/R3R9/r9_driver.zsh` to `evidence/R4F12/` and adapt it:
  - branch `presubmission4`;
  - the local URL in place of `git ls-remote`;
  - the stage reference `evidence/R4F11/M3/stages.json`;
  - the word base: round 4's F0, `18cc54f`, body 20,745.
- **Expect:**
  - 118 stages: 64 OK, 50 skipped, and the four known failures (20q1, 20n2, 29a, 29);
  - round 4's stages: 20u3 and 20u4 OK; 20u1, 20u2, 20u5 and 20u6 skipped (`NEEDS_WEIGHTS`);
  - the verifier ×3 byte-identical: 16,405 values, 16,402 identical, 3 differing (the supplementary manifest's bytes, uncompressed size and commits_in_log), **0 scientific**;
  - printed = measured on all 17 reproduction keys;
  - `part_f_gate` 7/8, check 4 alone;
  - 0 deny-list hits in the rebuilt and the committed upload files;
  - the PDF equal to the committed one after blanking its dates and ID;
  - `submission_check` 21/22 (C1, by ruling U5).
- **Write** `round4/FINAL_REPORT.md`, and stop with `BLOCKED` on any failure.

**Tools.**
- Interpreter: the absolute path in `../CLAUDE.md`'s hard rule 2.
- `evidence/R4F11/`:
  - `pdfcmp.py`, the PDF comparison;
  - `predict.zsh`, now fixed;
  - `measure.zsh`, the local-clone driver.

**Traps.**
- **zsh modifiers:** `$VAR:r…` applies a modifier, so write `${VAR}:results/…`. Round 3's `predict.zsh` had this bug: it overlaid every file and missed a carried-in count.
- **M-28:** partition on `results/_regenerated.txt`.
- **The gate** needs the identity strings derived as in `measure.zsh`.
- **Disk:** about 12 GiB free. The clones in `r4/M1`–`M3` are about 2.5 GB each, and deleting them is the user's call.

**Blockers:** none.

**Open (user, after F12 passes):** PLAN §0.4 "After F12".
- Merge to `main` (approved).
- Re-upload `MODEL_CARD.md` (approved; it changed since round 3).
- Software Heritage archive of the pushed commit.
- The author query, if it hasn't gone.
- Every author's quota check (needs each author's OpenReview login) and complete profiles.
- The upload last, checked against the package's checksums and not rebuilt. Two tracked internal files carry a local home path (`OUT_OF_SCOPE.md`, F7), which a push publishes in the repository.
