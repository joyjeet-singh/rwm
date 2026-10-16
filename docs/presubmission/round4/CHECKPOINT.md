# Round-4 checkpoint (workplan §2): F10 → F11, 2026-10-16

**State.** Branch `presubmission4`, last log entry **F10 — COMPLETE**. All commits since `110ecd7` are local; never push, merge, upload or submit (workplan §6). The tree is clean.
- **Text:** body 17,804 words, accepted by the user (`DECISIONS.md#F8-length`); abstract 300 words / 19 numerals.
- **PDF:** 75 pages, 0 warnings. References start on page 27.
- **Review:** REVIEW.md passes every Annex 6 item, with two qualifications: length (accepted) and the cover statement (F11 step 5). CONSISTENCY.md: 71 rows, all agree.
- **Ledger:** 288 entries. M-96 is the newest; it corrects M-65's discharge wording.

**Read first, nothing else.**
1. `round4/PLAN.md`: §1, the section "F11 — Freeze, restatement, bundles, package", round 3's `SESSION_LOG.md` "## R8" entry, and round 1's "## S10-fix" entry (the B3 recipe), as F11's section names them.
2. The last entry of `round4/SESSION_LOG.md`.
3. `round4/TMLR_CODEX_WORKPLAN.md` §4D, §6 and §8 (F11's TMLR check), and `../CLAUDE.md`'s round-4 section.

**Exact next action: F11.**
- **No push (workplan §6 overrides PLAN F11's "push" in steps 2 and 3).** Clone the local repository at HEAD (`git clone <local path> /Users/Shared/rwm_verify/r4/M1/`), not a pushed one. The clone's `origin` then points at the local path.
1. **Freeze.** No prose edits except §8's reproduction figures and the step-5 documents.
2. **Regenerate the claims audit** (`task_c1_claims_audit.py`, ruling U5), then the fast build and gates, and commit.
3. **Measure and restate** (round 3's R8). Make a fresh venv from `requirements.txt` in the clone and run `reproduce.sh --quick --force`. Run the verifier three times: the runs must be byte-identical, with 0 scientific differing values. Then:
   - restate the `ver_*` keys;
   - refresh the hand-written copies with `docs/presubmission/s10fix_docs.py`;
   - re-clone until every reproduction key matches (up to three times).

   Evidence goes to `R4F11/`.
4. **Bundles.** Rebuild both (`make_anon_bundle.py --zip`, `build_supplementary.py`). The builder scan and the independent deny-list sweep must find 0 hits in both zips and the PDF. `part_f_gate` 4b should then pass.
5. **Package documents:**
   - `SUBMISSION_CHECKLIST.md`, round-4 section;
   - `SUBMISSION_PACKAGE.md`, in full;
   - `COVER_STATEMENT.md`: rule count 28, page count, retraction counts. REVIEW.md item 7 also recommends adding round 4's results: X3–X8 and N5–N6;
   - `round4/OUT_OF_SCOPE.md`: carry forward anything open.
6. **TMLR recheck** (workplan §8): the live Author Guidelines and the OpenReview form, in a browser; also whether `tex/tmlr.sty` is the official, unmodified file. Record it in `round4/TMLR_CHECK.md`.

**Tools.**
- Interpreter: the absolute path in `../CLAUDE.md`'s hard rule 2.
- End of session: `/Users/Shared/rwm_verify/evidence/R4F10/build/run.sh`, copied to `R4F11/` with its paths changed by sed.
- Stage 21a: `./reproduce.sh --quick --force --stage 21a`, then remove `results/_regenerated.txt`.

**Traps.**
- `make_anon_bundle.py` rewrites `docs/COMMIT_LABEL_MAP.json`, adding labels for new commits and changing none. In F11 the rewrite is wanted.
- A clean clone carries `results/` in. Partition on `results/_regenerated.txt` (M-28).
- `pdftotext` is not installed; use `pypdf`, and `sips` to render pages.
- `runs/` and `*.pt` are not in a clone: stages that need them skip (`NEEDS_WEIGHTS`); X6 and X7 run without them.
- Commit labels in the PDF and bundle must be the anonymised ones (Data and code).

**Blockers:** none.

**Open (user):**
- Re-upload the model card to Hugging Face after F12 (ruling W12).
- Check every author's remaining TMLR submission quota.
- Publishing: push, merge, archive and submit.
