# Submission checklist

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
   independent passes. The builders' own scans: the anonymiser's planted probe is detected (9 hits,
   so the scan is live), 0 residual identifying hits across 385 scanned files, the anonymised git
   log CLEAN over 201 commits, and `f5_pdf_channels` reports no identifying strings on any of the
   PDF's three channels against 10 patterns. An independent sweep written for this programme, over
   member paths, member text in three encodings, archive and member comments, extra fields, nested
   archives, PNG text chunks, PDF text, the Info dictionary, XMP, link annotations and inflated
   streams, against the author's name and its variants, the handle, the git-log email, both
   repository URLs, the Hugging Face URL, full archival identifiers and any 7- to 40-character hex
   token resolving to a commit of this repository, of the pre-purge backup or of the Hugging Face
   repository: **0 hits in `supplementary_anon.zip`, 0 in `supplementary.zip`, 0 in `PAPER.pdf`**.
   OPEN ITEM, deliberately not resolved here: the bare prefix `swh:1:` occurs twice per bundle, in
   `FINDINGS_LEDGER.md` and `scripts/part_f_gate.py`, with no 40-character object name after
   either, so no occurrence resolves to an archival identifier. Whether that counts as an
   identifier has not been ruled on; the occurrences are left exactly as they are and no deny list
   was changed.
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
   DEFERRED, not a defect: figure-internal labels overlap bars or lines in Figures 1 and 2.
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

## Open items

These are known, recorded, and not fixed. Each is either ruled out of scope by the instruction
files or needs a decision that a verification pass is the wrong place to take.

- **The bare `swh:1:` prefix, awaiting a ruling.** It occurs twice in each bundle, in
  `FINDINGS_LEDGER.md` and in `scripts/part_f_gate.py`, with no 40-character object name after
  either, so no occurrence resolves to an archival identifier. Whether that counts as one has not
  been ruled on. The occurrences are left exactly as they are and no deny list was changed.
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
  regenerating those figures would move artifacts that §8 counts.
- **What the reproduction evidence covers.** Two independent clean clones of this commit agree on
  every figure and every per-file count, on one host, one interpreter and one set of hash-verified
  inputs, surviving an 8% throughput difference between the runs. That is repeatability. It is not
  portability: no second machine has produced these figures.
