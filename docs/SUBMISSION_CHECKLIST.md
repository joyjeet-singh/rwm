# Submission checklist

Final verification over commit `c16267c`, run in the verification tail (blocks S25 to S27) of the
referee-revision programme. No content changes: S25 and S26 write this file and nothing else, and
S27 commits it. Each line records what the step actually returned, not what it was supposed to
return. The previous pass, over commit `426fe35` on 2026-09-19, is kept below as the dated record of
what that pass found; it describes a paper and a tree that have since changed, and the only edit to
it is the level of its "Open items" heading.

*[2026-09-30, pre-submission S10-fix] The clean-clone figures in both passes below describe the commits they name. The paper, `docs/BUILD_CHECKS.md` and `README.md` now print a later clean-clone measurement, restated after S11's findings (`docs/DEFERRED.md`, 2026-09-30). The section 8 denominator that the pass over `c16267c` records as "not fixed, by ruling" was reworded on 2026-09-30 by the user's later ruling, so that status is historical too.*

## Round 3, over `6e98860` — the known items now

*[2026-10-10, pre-submission round 3, R8]
The sections below describe earlier commits and are kept as dated records. This section is the current
list, written by `docs/presubmission/round3/r8_checklist.py` from the files it names. Section 8's figures
come from M3, a clean clone of `fd279d7`; a clean clone of the commits after it is predicted to
measure the printed figures on all 17 reproduction keys. That is a prediction, not a measurement; round 3's
R9 measures it.*

### Open items

- **The bare `swh:1:` prefix — ruled 2026-09-20, closed.** No occurrence is followed by an object name.
- **`submission_check` returns 21 of 22** in the working tree. The one pending
  criterion is C1: the claims audit, regenerated on the frozen text by ruling U5 (round 3, R8), extracts
  550 claims, 58 supported and
  492 unreviewed; the ruling leaves them unreviewed and records it.
  E7 passes.
- **`part_f_gate` fails, and the paper publishes it as failing.** 7 of 8 checks
  pass with the identity strings supplied and a clean clone's results; check 4 alone fails because
  3 of 15,652 regenerated values differ, all of them bookkeeping in
  1 bundle records (`results/supplementary_manifest.json` (3)), none of them a measurement, a
  statistic or a verdict.
- **The supplementary manifest is exact — fixed in round 3, R5.** It records 493 files for an
  archive of 493 members, and 473 commits for a log of 473; both are
  counted, and asserted, rather than derived.
- **No report `reproduce.sh` writes is left untracked and unignored — fixed in round 3, R5.** The nine
  that nothing reads are gitignored and excluded by both bundlers; a clean clone's status after
  `reproduce.sh` lists no untracked file.
- **Figure-internal label overlaps — fixed in round 2, T8** (rendered Figures 2(a), 5 and 6; no plotted
  value changed). The earlier passes below still list them as deferred, and each such line now says it
  was fixed. The PDF prints the step-size quantity as LaTeX math since round 3, R4.
- **Four items are logged, not fixed** (`docs/presubmission/round3/OUT_OF_SCOPE.md`):
  - BUILD_CHECKS' list of claims withdrawn on evidence has no length guard (R0);
  - §6.7's per-episode difficulty averages the stale and causal action offsets, a question for the user (R5);
  - §5.2 gives rule M-74's alongside readings at the verdict level only (R6);
  - Appendix H's R-46 row has no recorded n_independent (R7).
- **Clean-clone runs share one private folder by default** (`scripts/t5_anon_transcript.py`); set
  `RWM_PRIVATE_DIR` per clone. **`results/v3_metric_definitions.json` embeds the checkout folder's
  name** in its citation strings; text only, ignored by the verifier.
- **What the reproduction evidence covers.** Repeatability on one host, one interpreter and one set
  of hash-verified inputs, not portability: no second machine has produced these figures.

## Round 2, over `c35c62e` — the known items now

*[2026-10-04, pre-submission round 2, T11]
The passes below describe round 1's commits and are kept as dated records. This section is the current
list, written by `docs/presubmission/round2/t11_checklist.py` from the files it names; section 8's figures come from M3, a clean clone of `5e7969c`. The commits after it carry M3's own verification record, which has the same 411 values as the record M3 carried in, so a clean clone of them is predicted to measure the printed figures on all 17 reproduction keys (`evidence/R2T11/predict_final`). That is a prediction, not a measurement; round 2's T12 measures it.*

### Open items

- **The bare `swh:1:` prefix — ruled 2026-09-20, closed.** No occurrence is followed by an object name.
- **`submission_check` returns 21 of 22** in the working tree. The one pending
  criterion is C1: the claims audit, regenerated on the frozen text by ruling U5, extracts
  526 claims, 59 supported and
  467 unreviewed; the ruling leaves them unreviewed and records it.
  **E7 passes**: fixed in round 2, T8, the check reads the build-checks supplementary as well as the
  template. A3 needs the gitignored `supplementary.zip`, which a pristine clone does not carry.
- **`part_f_gate` fails, and the paper publishes it as failing.** 7 of 8 checks
  pass with the identity strings supplied and a clean clone's results; check 4 alone fails because
  5 of 15,521 regenerated values differ, all of them bookkeeping in
  2 bundle records (`results/supplementary_manifest.json` (4), `results/anon_bundle.json` (1)), none of them a measurement, a
  statistic or a verdict.
- **The claims audit is current.** It was regenerated in round 2, T11, so it no longer accounts for
  any differing value (round 1's 355 of 364).
- **`results/supplementary_manifest.json` is still off by one in two counts:** it records
  490 files for an archive of 491 members, and 392 commits
  for a log of 391, the builder arithmetic recorded below. No number the paper prints comes from
  it.
- **4 reports `reproduce.sh` writes are neither committed nor gitignored**
  (`evidence_summary_report.txt`, `input_set_audit_report.txt`, `insample_framing_report.txt`, `m62_episode_clustering_report.txt`). They are why a clone's archive holds more files than the
  tree's, and so part of the bundle bookkeeping above.
- **Figure-internal label overlaps — fixed in round 2, T8** (rendered Figures 2(a), 5 and 6; no plotted
  value changed). The PDF still prints the step-size quantity as the literal text `‖µ_t − µ_{t−1}‖`;
  cosmetic.
- **`results/p4_transfer_power.json` now has a stage** (20r3a, round 2, T8), and stage 28a3 passes.
- **Clean-clone runs share one private folder by default** (`scripts/t5_anon_transcript.py`); set
  `RWM_PRIVATE_DIR` per clone. **`results/v3_metric_definitions.json` embeds the checkout folder's
  name** in its citation strings; text only, ignored by the verifier.
- **What the reproduction evidence covers.** Repeatability on one host, one interpreter and one set
  of hash-verified inputs, not portability: no second machine has produced these figures.

## This pass, over `c16267c`

1. [2026-09-27] Clean clone, `./reproduce.sh --quick --force` — PASS: two independent clones of this
   commit, at `/Users/Shared/rwm_verify/cloneD` and `/Users/Shared/rwm_verify/cloneE`, each made
   from the repository and run one after the other, never together. The clone root carries no
   account name, so the clones measure what a reviewer measures. Both runs: 97 stages, 55 OK, 36
   skipped as `NEEDS_WEIGHTS` (a clean clone has no `runs/`), 6 failed (20q1, 20n2, 20n8, 28a3, 29a,
   29), pipeline exit 1; 49 files regenerated. `scripts/verify_reproduction.py`, run three times per
   clone against a pristine reference restored before each run: 9,598 values compared, 9,233 bitwise
   identical (96.20%), 0 equal within tolerance but not bitwise, 365 differing, 1 value present in
   the committed artifacts and absent after regeneration, in 1 file; 940,905 values carried in,
   950,503 in all, the compared set being 1.01% of the directory. Partitioned by cause: 0 in the
   document-line index, 0 in the stochastic dilution study, 365 elsewhere, and **0 in any artifact
   carrying a scientific result**, across 5 files. All six verifier outputs, three runs in each
   clone, are byte-identical to one another, and the two clones agree on every one of the 135 per-file records, which name the values that differ and the keys that are lost file by file, and on their lists of regenerated files, not only on the totals. The values themselves differ between the clones in one place, the bundle manifest's two size totals, which differ from the committed values in both. Every verifier figure above is what §8 and its accounting in `docs/BUILD_CHECKS.md` print; the stage tally and the count of per-file records are the runs' own records. This commit is the fixed point of a loop that restated §8 three times
   (`docs/DEFERRED.md`). One gap, found by the review of the clones' independence: both runs wrote
   stage 20q's private transcript to one folder outside the clones. Each wrote its own copy before
   reading it, and the transcript result is byte-identical in both.
2. [2026-09-27] Comparative-claim registry, `check_comparative_claims.py --self-test` — PASS: 60 of
   60 claims verified across 27 distinct kinds, every kind exercised, and 60 of 60 deliberately
   corrupted expectations caught. The rewritten `results/comparative_claims.json` is byte-identical
   to the committed one.
3. [2026-09-27] Numeral audit, retraction consistency, ledger and the remaining gates — PASS, with
   `part_f_gate` failing by design and one exception recorded by ruling (`submission_check`, below):
   `typed_numeral_audit.py` finds 686 typed numerals, 0 unclassified, 18 classes and 23 declared
   exceptions, and its self-test catches the planted 12.7; the rewritten
   `results/typed_numerals.json` is byte-identical to the committed one. Retraction consistency
   C10.1 to C10.4 finds each retracted assertion absent from the files it reads, 6 for C10.1, which
   also reads the ledger's own summary, and 5 for the rest; C10.5 resolves 19 namings of 19 ledger
   retractions to their class. `ledger_check.py` PASS (254 entries, 99 tagged CONTRIB, 0 named
   artifacts missing), run twice: on the gitignored `results/*.pt` that the clone's own stages 8k
   and 8k2 wrote, and again with the repository's copied in, the clone's own restored afterwards.
   `PAPER.md`, `PAPER.tex`, `README.md`, `docs/BUILD_CHECKS.md` and `results/paper_numbers.json`
   rebuild byte-identically from the committed artifacts in a pristine clone; `MODEL_CARD.md` does
   so once the gitignored `runs/` is linked in, and differs without it because it records checkpoint
   hashes. `compile_paper` PASS: 48 pages, 0 errors, 0 overfull boxes, 0 underfull boxes, 0 LaTeX
   warnings. `pdf_render_check` 5/5. `xref_sweep` 63 pointers, 61 ok, 2 reviewed, 0 unverified, 0
   suspect. `check_scope_audit` 27 kinds, 0 unclassified. **`submission_check` did not return what
   this block predicted.** It returns 20 of 22 in the clone, pending E7 and C1 (458 claims, 173
   supported, 285 unreviewed, the clone having regenerated the claims audit), and 19 of 22 in a
   pristine clone, pending A3 (the gitignored `supplementary.zip` is absent), E7 and C1 (431 claims,
   196 supported, 235 unreviewed). E7 requires `step4_5_timing.json`, the one artifact excluded from
   numeric verification, to be named in `PAPER.template.md`. The referee revision moved both namings
   into the build-checks supplementary with §8's reproducibility block, and the check did not move
   with them; it has been pending since that commit, unseen because stage 29 already failed on C1.
   The script ships in neither bundle, so no referee can run it. By the user's ruling of 2026-09-27
   it is recorded as known rather than fixed, so that the commit two clones verified stays the one
   submitted; a repair, tested both ways, is kept outside the repository at
   `/Users/Shared/rwm_verify/evidence/S25F/e7_fix.patch`. `part_f_gate.py` is the committed script
   and carries no tolerance; run against clone D it **fails check 4 on exactly the 365 differing
   values §8 prints**, in every configuration: 7 of 8 with `RWM_IDENT` and `RWM_IDENT_REPO` exported
   and the gitignored `supplementary.zip` present; 6 of 8 without the archive, check 4b failing; 6
   of 8 without the variables, check 2 failing "NOT CONFIGURED"; and 5 of 8 in a pristine clone, both failing. Three of those four runs were made inside clone D, whose own `results/verify_reproduction.json` is the committed copy, checked out before its run: there the gate also reports that record as predating the clone's regeneration marker, which on its own would fail check 4 even with nothing differing. In the pristine reference, whose record was restored after the run, it post-dates the marker, and check 4 fails on the 365 differing values alone, as §8 says; the S27 reviewer's own tree, checked out after the run, returns the same (line 8). No gate record or log written here contains an identity string.
4. [2026-09-27] Three bundles built fresh — PASS: built twice, independently, in two clones of this
   commit that had never run `reproduce.sh` (`cloneH`, `cloneH2`), each given its own private folder
   for the correspondence transcript, holding a copy of the one the committed bundle was built from.
   `compile_paper.py`, `build_supplementary.py`, `make_anon_bundle.py --zip` and
   `f5_pdf_channels.py` all exit 0 in both. `supplementary.zip` 396 members, 10,649,542 bytes;
   `supplementary_anon.zip` 420 members, 12,523,126 bytes; `PAPER.pdf` 48 pages, 1,024,202 bytes.
   The two builds produce identical member lists with **byte-identical member contents**, and their
   archives differ only in member timestamps: every other header field agrees, and with every
   timestamp fixed the two archives are byte-identical. The two PDFs, and the committed one, are
   identical once their dates and identifier are blanked. The committed `supplementary_anon.zip`
   (420 members, 12,523,111 bytes) differs from a fresh build in three self-referential members only
   (`GIT_LOG_ANONYMISED.txt`, `results/anon_bundle.json`, `results/supplementary_manifest.json`),
   because an archive's own git log cannot contain the commit that adds it and its own records
   describe the build before it; the channel record, which the previous pass found stale in the same
   way, now matches. The gitignored `supplementary.zip` in the repository was last rebuilt, at this
   commit's content, in the reverted S25F block (`scripts/submission_check.py`, the one file that
   block changed, is in neither bundle): its contents equal a fresh build's, and it is 13 bytes
   larger than the committed `results/supplementary_manifest.json` records, because that manifest
   describes the build one commit earlier. `docs/SUBMISSION_CHECKLIST.md`, `docs/DEFERRED.md` and
   `docs/COMMIT_LABEL_MAP.json` are in neither archive. The four author-contact documents excluded
   on the user's ruling (`docs/E4_AUTHOR_CONTACT.md`, `docs/E4_REPLY_DRAFT.md`,
   `docs/E6_ARCHIVAL.md`, `scripts/e4_reply_draft.py`) are absent from the anonymised bundle, and
   the four that ruling kept, scrubbed (`MODEL_CARD.md`, `CITATION.cff`, `NOTICE`,
   `scripts/build_model_card.py`), are present.
5. [2026-09-27] Anonymity sweep on exactly the committed bundles — PASS, 0 hits, from two
   independent passes. The builders' own scans, on each fresh build: the anonymiser's planted probe
   is detected (9 hits, so the scan is live), 0 residual identifying hits, 394 files scanned for
   identity, the anonymised git log CLEAN over 218 commits, and `f5_pdf_channels` reports no
   identifying string on any of the PDF's three channels against 10 patterns. The programme's own
   sweep, independent of the builders, over member paths, member text in three encodings, archive
   and member comments, extra fields, nested archives, PNG text chunks, PDF text, the Info
   dictionary, XMP, link annotations and inflated streams, against 9 name terms (the author's name
   and its variants, the handle, the git-log email, both repository URLs, the Hugging Face URL, full
   archival identifiers) and any 7- to 40-character hex token resolving to one of 249 commits the
   author controls: **0 hits in the committed `supplementary_anon.zip`, `supplementary.zip` and
   `PAPER.pdf`**, and 0 in the fresh builds. The bare prefix `swh:1:` occurs 3 times in the
   anonymised bundle and 3 in the full one, once each in `FINDINGS_LEDGER.md`,
   `GIT_LOG_ANONYMISED.txt`, `scripts/part_f_gate.py`, and 0 times in the PDF, with no object name
   after any of them. By the user's ruling of 2026-09-20 a bare prefix is not an archival
   identifier; the occurrences are recorded, not counted and not scrubbed, and no deny list changed.
6. [2026-09-27] The PDF read by eye, all 48 pages — PASS: every page rendered and inspected, and the
   text layer checked alongside. No `??`, no literal footnote token, no unconverted `**`, no stray
   `Figure ?` or `Table ?` and no orphan list marker anywhere. Figures land on pages 2, 12, 16, 20,
   29, 33, and every figure, section and appendix reference resolves, including every appendix
   pointer after the referee revision's renumbering. The appendices begin on pages A p42, B p42, C
   p42, D p44, E p45, F p48, G p48; C, D and E, the three the previous pass knew as D, E and F,
   render as tables. The abstract's first finding is the one-step misalignment. The converter fixes
   hold: §6.2's formula renders `r̃ = r − λu` and `λ/c` with their Greek letters and tilde rather
   than `?` (pages 15, 17); inline `./reproduce.sh --quick --force` shows two hyphens on each flag,
   where it breaks across pages 34 and 35 as well as on page 42, so a reader copying it gets valid
   flags; and `10¹³` renders as a superscript (pages 23, 35, 39). The caption fixes hold: Figure 6's
   panel title "the wrong unit narrows 15 of 16 intervals" and its caption, "Resampling pooled seed
   × trajectory values rather than whole trajectories narrows 15 of the 16 intervals", agree on the
   count and the unit; Figure 3's caption describes panel (c) and its sentence about the curves
   follows panel (b), the panel they are in; Appendix G, the previous pass's H, gives the two
   definitions and the inversion and claims only what it shows; and §6.8's pointer names "this
   section's table … its *different model* column" rather than a position. DEFERRED, not defects:
   figure-internal labels overlap in Figure 2 (panel (a)'s point labels near h = 100 to 128) and
   Figure 5 (panel (a)'s legend over a line), with Figure 1's labels clear at this resolution; and
   on page 27 the step-size quantity prints as the literal text `‖µ_t − µ_{t−1}‖`, its underscores
   and braces not typeset as subscripts, readable and unambiguous. *[The label overlaps were fixed in round 2, T8, and the step-size quantity is typeset as math since round 3, R4; see the round-3 section.]*
7. [2026-09-27] TMLR style — PASS: `PAPER.tex` loads `\usepackage{tmlr}` once, with no option; there
   is no system `tmlr.sty` at all — `kpsewhich` finds none — and the compile's log loads
   `./tmlr.sty`, the vendored `tex/tmlr.sty` (6,560 bytes, sha1
   13864927f73946b0b18efd1248bfe375fa51ad64) copied in by `compile_paper.py`; page 1 renders "Under
   review as submission to TMLR", "Anonymous authors" and "Paper under double-blind review".
   Compiled exactly as `compile_paper.py` compiles it, keeping the log: 48 pages, 1,024,202 bytes,
   the committed PDF's size; **0 errors, 0 LaTeX warnings, 0 overfull and 0 underfull horizontal
   boxes**, and the build's own stray-markdown-emphasis check is clean. The gate counts horizontal
   boxes only: the raw log also carries 17 `Underfull \vbox` messages (0 overfull) and 3 hyperref
   "Token not allowed in a PDF string" warnings, from the σ in §6.3's heading, which a PDF bookmark
   cannot carry. Neither puts anything in a margin, and neither is counted by the gate.
8. [2026-09-27] Two independent reviewers over the whole pass. Neither had seen this work; each
   re-derived its half rather than checking mine, and each wrote its verdict to
   `/Users/Shared/rwm_verify/evidence/S27T/`. **Reviewer A, reproduction and gates** (Claude Opus
   5.5), returned FAIL on one clause of line 3, now fixed (line 9), and confirmed everything else.
   It re-ran the verifier three times against each clone, into a reference of its own restored
   before every run, and derived every figure in lines 1 to 3 with its own code, re-implementing the
   partition rules rather than calling `scripts/paper_numbers.py`: all match. Clone E's output is
   byte-identical to the recorded runs and to the committed record; clone D's now differs in the
   carried-in partition only, because S25 ran its gates inside clone D after the measurement. It
   re-ran every gate of lines 2 and 3 in its own clone and confirmed each count, and `part_f_gate`
   failing on 365 = `ver_differing` in all 7 of its configurations. **Was any gate weakened? No.**
   `scripts/verify_reproduction.py` is byte-identical to commit `2424af8`. `scripts/part_f_gate.py`
   changed in one commit, `e18b75d`, in check 2 only: the identity strings moved out of the file
   into `RWM_IDENT` and `RWM_IDENT_REPO`, because the file ships inside the archive, and the check
   now fails when they are unset; no operator is relaxed, no tolerance added, and check 4 is
   untouched. `scripts/check_comparative_claims.py` changed in one commit, `c3a8090`, which lets six
   claims and three whole-paper sweeps read the text the referee revision moved into the
   build-checks supplementary and repairs one check that could not fail: it checks more, not less.
   The bookkeeping classification in `scripts/paper_numbers.py` was widened once, in `52c0110`, to
   archive values; the reviewer judged it legitimate for every value it covers in this run's 365,
   each a size or count of an archive rather than a measurement, a statistic or a test verdict, and
   noted that it was added after those values were seen and is disclosed value by value. **Reviewer
   B, bundles and PDF** (Claude Sonnet 5; the first reviewer for this lens was stopped twice by the
   account's usage limit before it reported, and the user ruled to replace it), PASS: it built both
   archives and the PDF in its own clone with its own private folder, matched every figure in line
   4, and found the member contents byte-identical to both of the author's builds and the archives
   differing only in timestamps; wrote its own sweep from scratch, proved it live with a marker
   caught in all 25 planted locations, a nested archive and the PDF's metadata among them, and
   returned **0 hits** on the three committed artifacts, with the bare `swh:1:` prefix in the same
   three places; read all 48 pages and confirmed every fix and both deferred items by sight; and
   reproduced the compile log's figures exactly. **The re-check of reviewer A's findings** (Claude
   Sonnet 5, standing in by the user's ruling because the usage limit kept reviewer A from running
   again) read the fixed line 3 against every gate log, recomputed the §8 figures and the clones'
   differing values itself, and confirmed lines 8 and 9, the open items and the appended
   `docs/DEFERRED.md` lines: PASS (`lensA_recheck.md`). Reviewer B then confirmed lines 8 and 9 on
   its own review: PASS. Both lenses therefore PASS.
9. [2026-09-27] Findings adjudicated — 1 blocking, in this checklist's own text, fixed; 1 a possible
   content defect, confirmed, ruled by the user and recorded; the rest recorded. **Line 3
   incomplete: confirmed, fixed.** Three of its four `part_f_gate` configurations ran inside clone
   D, where the gate's record is the committed copy and predates the run, so check 4 would have
   failed there even with nothing differing; line 3 now says so, and that check 4 fails on the 365
   alone in a tree whose record post-dates the run. **Line 1 loose: confirmed, fixed.** It said
   every figure above is what §8 prints, where §8 prints three of them and the rest are in its
   build-checks accounting; and it said the clones agree on every per-file record without saying
   that those records name values rather than hold them. **§8's denominator: a real, small
   inaccuracy in the paper's text; not fixed, by ruling.** §8 says the quick run "rewrites 1.01% of
   the numeric values under `results/`", and the build-checks supplementary says "of the 950,503
   numeric values under `results/`". The directory holds 956,435; 950,503 is the set the comparison
   counts after the two exclusions the same supplementary states. So the 9,598 compared values are
   1.01% of the counted set and 1.00% of every value, and the 49 files the run rewrites hold 1.08%.
   No other figure moves. The user ruled on 2026-09-27 to record it rather than fix it, because a
   fix changes prose and reruns the restatement loop, and this is the commit two clones verified.
   **Recorded, not defects in the work:** clone D is no longer in its measured state; check 2's deny
   list is now whatever the environment supplies, narrower in the configuration used than the file's
   old list, with 0 hits for the old terms today; values in files that failing stages rewrite sit
   outside the 365, and the supplementary's input-audit counts rebuild differently on a clean clone;
   check 4 reads only the committed record; the byte-identical rebuild needs `setup.sh`'s two
   upstream checkouts beside the clone; and the ledger entry the `52c0110` widening called for was
   never written. Reviewer B's two notes concern its own method: its raw `swh:1:` count doubles the
   three occurrences across two encodings, and its probes used synthetic markers so that no identity
   string was written to disk.

### Open items

Known and recorded. None is fixed in this pass: each is ruled by the user, ruled out of scope by the
instruction files, or would need a change that reopens the clean-clone measurement.

- **The bare `swh:1:` prefix — ruled 2026-09-20, closed.** It occurs three times in each bundle, in
  `FINDINGS_LEDGER.md`, `GIT_LOG_ANONYMISED.txt` and `scripts/part_f_gate.py`, never followed by an
  object name, so no occurrence resolves to an archival identifier. The occurrences stay as they
  are.
- **`submission_check` returns 20 of 22 in a clone and 19 of 22 in a pristine one.** A3: the
  gitignored `supplementary.zip` is absent from a pristine clone. C1: 235 of 431 claims are
  unreviewed in the committed audit (285 of 458 when a clone regenerates it); auditing them is out
  of scope by the instruction file. E7: the naming of `step4_5_timing.json` moved to the
  build-checks supplementary in the referee revision, and the check still reads only
  `PAPER.template.md`; ruled known on 2026-09-27; a fix, tested both ways, is at
  `/Users/Shared/rwm_verify/evidence/S25F/e7_fix.patch`; the script ships in neither bundle.
- **`part_f_gate` fails, and the paper publishes it as failing.** Check 4 requires that no
  regenerated value differ; 365 do, none of them a measurement, a statistic or a test verdict. This
  is deliberate and §8 states it.
- **§8's denominator** (line 9): 1.01% is of the values the comparison counts, not of every value
  under `results/`; ruled known on 2026-09-27.
- **`results/task_c1_claims_audit.json` is stale**, and is 356 of the 365 differing values.
  Regenerating it is not a refresh: it moves a review finding, from 196 supported and 235 unreviewed
  of 431 claims to 173 and 285 of 458. That belongs to a block that takes it deliberately.
- **`results/supplementary_manifest.json` is off by one in two counts.** A fresh build at this
  commit records 395 files for an archive of 396 members and 218 commits for a log of 217, because
  `scripts/build_supplementary.py` adds one to the file count and subtracts 7 from an 8-line log
  header. It ships in both bundles; no number the paper prints comes from it.
- **Four reports `reproduce.sh` writes are neither committed nor gitignored**
  (`evidence_summary_report.txt`, `input_set_audit_report.txt`, `insample_framing_report.txt`,
  `m62_episode_clustering_report.txt`). They are why a clone's archive holds more files than the
  tree's, which keeps three of the manifest's differing values differing; committing them could move
  the fixed point, so doing so needs a new measurement.
- **Cosmetic, deferred:** figure-internal labels overlap in Figures 2 and 5, and page 27 prints the
  step-size quantity as the literal text `‖µ_t − µ_{t−1}‖`. Fixing either changes a figure or the
  paper's text. *[The label overlaps were fixed in round 2, T8, and the step-size quantity is typeset as math since round 3, R4; see the round-3 section.]*
- **Clean-clone runs share one private folder by default:** `scripts/t5_anon_transcript.py` writes
  the correspondence transcript two levels above the clone. Set `RWM_PRIVATE_DIR` per clone. It
  caused no contamination here.
- **`results/v3_metric_definitions.json` embeds the checkout folder's name** in its citation
  strings. Text only; the verifier ignores it and no account name appears.
- **`results/p4_transfer_power.json` is written by no stage**, so stage 28a3 fails on it.
- **What the reproduction evidence covers.** Independent clean clones of this commit agree on every
  figure and every per-file record, on one host, one interpreter and one set of hash-verified
  inputs. That is repeatability. It is not portability: no second machine has produced these
  figures.

## The previous pass, over `426fe35`, kept unchanged

Final verification over commit `426fe35`, run across sessions 25 to 27 of the road to submission.
No content changes: sessions 25 and 26 write this file and nothing else, and session 27 commits it.
Each line records what the step actually returned, not what it was supposed to return. The record
of the earlier stopped pass (session 18, over commit 2424af8) is preserved verbatim in
`/Users/Shared/rwm_verify/JOURNAL.md` and is not repeated here; every defect it found has since
been fixed or is carried in `docs/DEFERRED.md`.

1. [2026-09-19] Clean clone, `./reproduce.sh --quick --force` — PASS: two independent clones of
   this commit, at `/Users/Shared/rwm_verify/cloneF` and `/Users/Shared/rwm_verify/cloneG`. The
   clone root deliberately carries no account name: stage 28 refuses to write its archive when an
   account name appears inside a results file, so a clone reached from the author's home directory
   does not measure what a reviewer measures. Both runs: 94 stages, 52 OK, 36 skipped as
   `NEEDS_WEIGHTS` (a clean clone has no `runs/`), 6 failed (20q1, 20n2, 20n8, 28a3, 29a, 29),
   pipeline exit 1; 46 files regenerated. `scripts/verify_reproduction.py`, run three times per
   clone against a pristine reference restored before each run: 9,308 values compared, 8,994
   bitwise identical (96.63%), 0 equal within tolerance but not bitwise, 314 differing, 1 value
   present in the committed artifacts and absent after regeneration, in 1 file; 940,893 values
   carried in, 950,201 in all, the compared set being 0.98% of the directory. Partitioned by cause:
   0 in the document-line index, 0 in the stochastic dilution study, 314 elsewhere, and **0 in any
   artifact carrying a scientific result**, across 6 files. All six verifier outputs — three runs in
   each clone — are byte-identical to one another, and the two clones agree on every per-file
   differing and keys-lost count, not only on the totals. Every figure above is what §8 prints.
2. [2026-09-19] Comparative-claim registry, `check_comparative_claims.py --self-test` — PASS: 60 of
   60 claims verified across 27 distinct kinds, every kind exercised, and 60 of 60 deliberately
   corrupted expectations caught. The rewritten `results/comparative_claims.json` is byte-identical
   to the committed one.
3. [2026-09-19] Numeral audit, retraction consistency, ledger and the remaining gates — PASS, with
   `part_f_gate` failing by design: `typed_numeral_audit.py` finds 659 typed numerals, 0
   unclassified, 18 classes and 23 declared exceptions, and its self-test catches the planted 12.7.
   Retraction consistency C10.1 to C10.4 finds each retracted assertion absent from the five
   reader-facing files, C10.1 checking six because it also reads the ledger's own summary, and C10.5 resolves 19 namings of 19 ledger retractions to their class.
   `ledger_check.py` PASS, with the gitignored `results/*.pt` copied into the clone; it reports
   BLOCKER without them, which is a property of a clean clone rather than of the ledger.
   `PAPER.md`, `PAPER.tex`, `README.md` and `results/paper_numbers.json` rebuild byte-identically
   from the committed artifacts in a pristine clone; `MODEL_CARD.md` does so once the gitignored
   `runs/` is linked in, and differs without it because it records checkpoint hashes. `compile_paper`
   PASS: 49 pages, 0 errors, 0 overfull boxes, 0 LaTeX warnings. `pdf_render_check` 5/5.
   `xref_sweep` 71 pointers, 69 ok, 2 reviewed, 0 unverified, 0 suspect. `check_scope_audit` 22
   kinds, 0 unclassified. `submission_check` 20 of 22, the two pending being A3 (the gitignored
   `supplementary.zip` is absent from a pristine clone) and C1 (431 claims, 196 supported, 235
   unreviewed) — both known, both out of scope by the instruction file. `part_f_gate.py` is
   byte-identical to the commit and carries no tolerance; run against the clean clone it **fails
   check 4 on exactly the 314 differing values §8 prints**, in every configuration. The other counts
   depend on what the environment supplies, and a referee will meet the last of these: 7 of 8 with
   `RWM_IDENT` and `RWM_IDENT_REPO` exported and the gitignored `supplementary.zip` present; 6 of 8
   with those variables but no archive, check 4b failing because the archive is not there; and 5 of
   8 in a genuinely pristine clone, where check 2 also fails "NOT CONFIGURED" because **no file in
   the repository supplies those variables**. Check 2 failing closed is deliberate — the gate ships
   inside the archive, so the strings it scans for are supplied from outside it — and both
   limitations are recorded in `docs/DEFERRED.md`.
4. [2026-09-19] Three bundles built fresh — PASS: built twice, independently, in two clones that
   had never run `reproduce.sh` (`cloneH`, `cloneH2`). `compile_paper.py`, `build_supplementary.py`,
   `make_anon_bundle.py --zip` and `f5_pdf_channels.py` all exit 0 in both. `supplementary.zip`
   387 members, 10,555,396 bytes; `supplementary_anon.zip` 411 members, 12,420,209 bytes;
   `PAPER.pdf` 49 pages, 1,022,372 bytes. Those are the sizes of a FRESH build. The bundles
   committed in this repository, which are the files that would be uploaded, are 10,555,377 and
   12,420,192 bytes: they differ from a fresh build in five self-referential members only
   (`GIT_LOG_ANONYMISED.txt`, `results/anon_bundle.json`, `results/pdf_channels.json`,
   `results/pdf_channels_report.txt`, `results/supplementary_manifest.json`), because an archive's
   own git log cannot contain the commit that adds it and its own records describe the build before
   it. Both the committed and the freshly built pair were swept, and both are clean. The two builds produce identical member lists with
   **byte-identical member contents** — 0 members differ — and the archives' SHA-256 differ only
   through zip member timestamps, the PDF's only through its dates and identifier (the differing
   bytes are confined to `/CreationDate`, `/ModDate` and `/ID`). `docs/SUBMISSION_CHECKLIST.md`,
   `docs/DEFERRED.md` and `docs/COMMIT_LABEL_MAP.json` are in none of the three. The four
   author-contact documents excluded on the user's ruling — `docs/E4_AUTHOR_CONTACT.md`,
   `docs/E4_REPLY_DRAFT.md`, `docs/E6_ARCHIVAL.md` and `scripts/e4_reply_draft.py` — are absent
   from the anonymised bundle, and `MODEL_CARD.md`, `CITATION.cff`, `NOTICE` and
   `scripts/build_model_card.py`, which that ruling kept, are present.
5. [2026-09-19] Anonymity sweep on exactly the committed bundles — PASS, 0 hits, from two
   independent passes. The builders' own scans: the anonymiser's planted probe is detected (9
   hits, so the scan is live), 0 residual identifying hits across 385 scanned files, the
   anonymised git log CLEAN over 201 commits, and `f5_pdf_channels` reports no identifying strings
   on any of the PDF's three channels against 10 patterns. An independent sweep written for this
   programme, over member paths, member text in three encodings, archive and member comments,
   extra fields, nested archives, PNG text chunks, PDF text, the Info dictionary, XMP, link
   annotations and inflated streams, against the author's name and its variants, the handle, the
   git-log email, both repository URLs, the Hugging Face URL, full archival identifiers and any 7-
   to 40-character hex token resolving to a commit of this repository, of the pre-purge backup or
   of the Hugging Face repository: **0 hits in `supplementary_anon.zip`, 0 in `supplementary.zip`,
   0 in `PAPER.pdf`**. OPEN ITEM, deliberately not resolved here: the bare prefix `swh:1:` occurs
   twice per bundle, in `FINDINGS_LEDGER.md` and `scripts/part_f_gate.py`, with no 40-character
   object name after either, so no occurrence resolves to an archival identifier. Whether that
   counts as an identifier has not been ruled on; the occurrences are left exactly as they are and
   no deny list was changed. **Ruled on 2026-09-20, after this pass**: a bare prefix with no
   object name is not an archival identifier. The occurrences stay as they are and no deny list
   changed; this record stands as the dated account of what the pass found.
6. [2026-09-19] The PDF read by eye, all 49 pages — PASS: every page rendered and inspected.
   No `??`, no literal footnote token, no unconverted `**`, no stray `Figure ?` or `Table ?`
   anywhere in the document. Figures land on pages 2, 11, 15, 19, 28 and 32, and every figure,
   section and appendix reference resolves. Appendices D (p44), E (p45–46) and F (p47–48) render as
   tables. The abstract's first finding is the one-step misalignment. The converter fixes hold:
   the §6.2 formula on p16 renders `r̃ = r − λu` and `λ/c` with their Greek letters and tilde rather
   than `?`; inline `./reproduce.sh --quick --force` shows two hyphens on p33 and p41, so a reader
   copying it gets valid flags; and `10¹³` renders as a superscript on p22. The caption fixes hold:
   Figure 6's caption on p32 reads "Resampling pooled seed × trajectory values rather than whole
   trajectories narrows 15 of the 16 intervals", agreeing with the count and the unit its own
   figure uses; Figure 3's caption describes panel (c) and its closing sentence about the curves
   sits after panel (b), the panels it is about; Appendix H claims only what it shows; and the §6.8
   pointer names "this section's table … its *different model* column" rather than a position.
   DEFERRED, not a defect: figure-internal labels overlap bars or lines in Figures 1 and 2. *[Fixed in round 2, T8; see the round-3 section.]*
7. [2026-09-19] TMLR style — PASS: `PAPER.tex` loads `\usepackage{tmlr}` with no option;
   there is no system `tmlr.sty` at all — `kpsewhich` finds none — so the file the compile loads
   is necessarily the vendored `tex/tmlr.sty` (6,560 bytes, sha1
   13864927f73946b0b18efd1248bfe375fa51ad64); page 1
   renders "Under review as submission to TMLR", "Anonymous authors" and "Paper under double-blind
   review". The compile reports 49 pages, 1,022,372 bytes, **0 errors, 0 overfull hboxes, 0
   underfull hboxes and 0 LaTeX warnings**, and the build's own stray-markdown-emphasis check is
   clean. The gate counts horizontal boxes only: the raw LaTeX log also emits 18 `Underfull \vbox`
   messages and 3 hyperref "token not allowed in a PDF string" warnings, the latter from the sigma
   in §6.3's heading. Neither puts anything in a margin, and neither is counted by the gate.
8. [2026-09-19] Two independent reviewers over the whole pass — BOTH PASS. Neither had seen this
   work; each re-derived its half rather than checking mine. **Reviewer A, reproduction and gates:**
   re-ran the verifier three times against a restored reference and reproduced every figure in
   steps 1 to 3 byte for byte, derived the partition and the outcome classes from the raw artifact
   rather than from `scripts/paper_numbers.py`, and answered the question this pass exists to ask —
   was any gate weakened to make it pass? **No.** `scripts/verify_reproduction.py` and
   `scripts/check_comparative_claims.py` are byte-identical to commit `2424af8`, so every exclusion
   and the single pre-existing tolerance (`rel_tol=1e-9`, which caught 0 values here) are unchanged
   character for character. `scripts/part_f_gate.py` changed in one commit, `e18b75d`, in one check:
   the strings check 2 scans for moved out of the file into the environment, because the file ships
   inside the archive and the previous in-file form still handed a reader the author's name. It
   relaxes no operator, adds no tolerance, widens no exclusion, and fails closed when unconfigured.
   Reviewer A also surfaced, unprompted, the one genuine widening in this programme: the bookkeeping
   classification table in `scripts/paper_numbers.py` went from 11 entries to 14 in commit
   `52c0110`, and against this run's 314 values the old table would report 5 scientific differences
   where the new reports 0. It judged the widening legitimate — the five values are an archive's
   member count, its compressed and uncompressed sizes, its anonymised log's commit count and a
   scrubber's rewrite count, none of them a measurement, a statistic or the verdict of a test, and
   all five entered the compared set for the first time when the archive stage began producing
   bundles — and §8 both enumerates all 314 by kind and states that an unrecognised value counts as
   scientific. **Reviewer B, bundles and PDF:** built both archives twice in its own clones,
   confirmed identical member lists with byte-identical contents, verified the exclusion ruling by
   executing the shipped `reproduce.sh` inside an extracted bundle (stage 25 OK, stage 28a OK with
   C11.2 passing on the model card), wrote its own sweep from scratch and proved it live with 12
   planted probes — all 12 caught, including one fragmented across a string concatenation and one
   inside a nested archive — and returned **0 hits on all five artifacts**, the committed and freshly
   built bundles and both PDFs. It then read all 49 pages rendered at 4x and confirmed every
   converter and caption fix by sight, and found no number in the PDF that disagrees with the
   artifact beside it.
9. [2026-09-19] Findings adjudicated — 2 raised as possible content defects, both resolved without
   changing content; 8 recorded. **Figure 3's caption says "all four models on the held-out arena"
   while the body says the released checkpoint has no held-out arena in this dataset: NOT a defect.**
   The paper names that arena two lines above the figure as "the two episodes withheld from our own
   arms", and the paragraph immediately below the figure is headed "so the next table does not read
   as a contradiction" and ends "Neither is a held-out measurement *of the released checkpoint*,
   which has no held-out arena in this dataset". The reading the reviewer tested is the one the
   paper anticipates and answers in the adjacent sentence. **`results/supplementary_manifest.json`
   records 386 files where the archive holds 387, and 200 log commits where the log holds 199: a
   real defect in a shipped artifact, but not a claim of the paper.** §8 names that file only in its
   accounting of differing values; no printed number is sourced from it. Its cause is recorded twice
   in `docs/DEFERRED.md`: the builder credits the git log but not the correspondence transcript, and
   subtracts 7 from an 8-line header. Fixing it would rewrite a compared artifact and so require
   another clean-clone measurement, which is why it is carried as an open item rather than fixed in
   a verification block.

### Open items

These are known and recorded. The first has since been ruled and is closed, and is kept here with
its resolution rather than deleted; the rest are not fixed, each either ruled out of scope by the
instruction files or needing a decision that a verification pass is the wrong place to take.

- **The bare `swh:1:` prefix — RULED 2026-09-20, no longer open.** It occurs twice in each bundle,
  in `FINDINGS_LEDGER.md` and in a comment in `scripts/part_f_gate.py`, with no 40-character
  object name after either, so no occurrence resolves to an archival identifier. The user ruled
  that a bare prefix with no object name is not one. The occurrences stay exactly as they are, no
  deny list was changed, and no artifact or checksum moved.
- **`submission_check` reports 20 of 22.** A3 is pending because the gitignored `supplementary.zip`
  is absent from a pristine clone; C1 is pending because 235 of 431 claims in the review checklist
  remain unreviewed. Auditing those claims is ruled out of scope by the instruction file, and the
  count itself moves between clone runs.
- **`part_f_gate` fails, and the paper publishes it as failing.** Check 4 requires that no
  regenerated value differ; 314 do, all of them bookkeeping, none of them a measurement, a statistic
  or a verdict. This is deliberate and §8 states it.
- **`results/supplementary_manifest.json` is off by one**, in both the file count and the log's
  commit count, as line 9 records. It ships inside both bundles. No number the paper prints comes
  from it.
- **`results/task_c1_claims_audit.json` is stale**, last regenerated in an early session, and is
  301 of the 314 differing values. Regenerating it is not a refresh: it would move a review
  finding, taking SUPPORTED from 196 to 177 and UNREVIEWED from 235 to 284 over 431 claims rising
  to 461. That belongs to a block that takes it deliberately, not to a numbers restatement.
- **Figure-internal labels overlap** bars or lines in Figures 1, 2 and 5. Cosmetic, deferred, and
  regenerating those figures would move artifacts that §8 counts. *[Fixed in round 2, T8; see the round-3 section.]*
- **What the reproduction evidence covers.** Two independent clean clones of this commit agree on
  every figure and every per-file count, on one host, one interpreter and one set of hash-verified
  inputs, surviving an 8% throughput difference between the runs. That is repeatability. It is not
  portability: no second machine has produced these figures.
