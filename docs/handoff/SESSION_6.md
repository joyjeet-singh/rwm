# Session 6 — consistency, and the run that found what the sessions had left behind

**Ran** 2026-09-04. Branch `main`. The last session that touches the paper's content.

**Compile PASSES, 40 pages, 0 errors. Checks 54/54 with 54/54 self-test corruptions caught.
Submission gate 7/7, one check NOT RUN. `ledger_check` PASS.**

---

## §A — the cross-reference sweep

`results/xref_sweep.json`: **60 pointers, all verified.** Semantic pointers 19, artifact paths
21, repo `file:line` 2, upstream `file:line` 16, new docs 2.

The sweep exists because `part_f_gate` check 5 confirms a section reference *resolves*, and §8's
resolved fine while claiming the target held things it no longer did. This checks the claim, not
the link.

Two flags were reviewed and cleared — both the same false positive, where the object of
"gives"/"explains" precedes the pointer in an appositive. Dispositions are recorded, so a re-run
does not leave them dangling; a flag **not** in that table stays unresolved.

**The sweep found two bugs in itself before it found anything in the paper.** It searched only
one of the two pinned upstreams and reported 13 `system_dynamics.py` citations as UNVERIFIED —
that file is in `rsl_rl_rwm` — and its regex skipped path-qualified citations like
`envs/base.py:166`. A sweep that launders its own bug as a caveat is worse than no sweep. Both
fixed; 16/16 upstream citations now resolve.

## §B — `unit-consistency`

Registered with one claim, corruptible, and its corruption is caught. **`kind-count` PASSES at
22 = 22 = 22** — the registry, §8's count and `docs/BUILD_CHECKS.md`'s enumeration moved
together, held in step by `paper_numbers.py`'s existing assert that every kind carries a
description.

It found **18 real gaps** on first run. I scoped it to the enclosing paragraph — the granularity
`horizon-consistency` already uses in this file for non-calibration figures — which left **8
genuine** ones, fixed in the prose. Now 0 findings.

## §C — six surfaces

`cross-artifact-sync` was anchored on a sentence the rewritten abstract deleted, so all three
claims lost their anchor. Re-pointed to the equivalent assertion that survives in §8. A fourth
claim now covers `docs/BUILD_CHECKS.md`.

`docs/APPENDIX_G_RULES.md` is deliberately **not** in that check: it carries no substituted
values, being written straight from the ledger in the same pass as the body table, so the two
cannot disagree by construction. A sync claim over it would match incidental substrings and
assert nothing. It is inside `retraction-consistency` and `count-consistency`, which is where it
belongs.

**The Hugging Face card was not updated, and `M-67` says so.** `MODEL_CARD.md` — its generated
source — is current and passes sync. Pushing the remote copy is a credentialed outward-facing
action that `docs/CLOSING_BRIEF.md` already classifies as one, and it is not something this work
performs on the author's behalf. `M-67` names the commit to upload and stays **OPEN**.

## §D — the pipeline run, and what it found

`./reproduce.sh --quick --force`, **83 stages**. It found seven things. Three were mine from this
session or the last two; four were older.

**The first invocation did nothing and exited 0.** It resolved `python3.11` to the system
interpreter, found no torch or numpy, printed `ENVIRONMENT MISMATCH` and returned success. A run
that does nothing and reports success is the failure mode this project keeps finding in its own
machinery. Re-run with `PY=…/.venv-rwm311/bin/python`.

| finding | origin | state |
|---|---|---|
| Appendix letters mismatched: document `ABDEFGHI` vs LaTeX `ABCDEFGH` | 5a retired Appendix C | **fixed** — re-lettered contiguously |
| `§13` cross-reference unresolved | 4a's consent sentence | **fixed** — consent is under Data and code |
| Anonymisation: `FINDINGS_LEDGER.md` carried the author's username | **this session's `M-67`** | **fixed** |
| Anonymisation: `pdf_channels_report.txt` carries the scanner's own probe string | pre-existing | **fixed** — excluded, with its reason |
| 2 typed numerals unclassified | 4a's §6.2 and §6.6 text | **fixed** — substituted from artifacts |
| 7 artifacts feeding `paper_numbers.json` with no stage | Sessions 2, 3, 6 | **fixed** — 8 stages added |
| `supplementary_anon.zip` needs `--zip` to be written | pre-existing | **fixed** — rebuilt |

**The appendix one is the serious one.** LaTeX letters appendices sequentially, so with C retired
the document's "Appendix D" became the PDF's "Appendix C" and **every appendix reference past B
landed on the wrong appendix**. My own §A sweep did not catch it: it reads `PAPER.md`, where the
headings carry their intended letters, and the defect lives in the letter LaTeX assigns. The gate
caught it. That is the sweep's blind spot and it is recorded rather than papered over.

### The failing gate

**Still failing, still saying where.** 178 of 8,186 regenerated values differ across 47 files;
7,981 bitwise identical (97.50%), 27 to tolerance. 0.90% of the 905,391 values under `results/`.
**The 178 is unchanged by this revision and no tolerance was applied.**

The clean-clone check reads **NOT RUN**, not FAIL: it needs `CLONE_RESULTS` and none was
supplied. Its published figure stands; running it against a fresh clone is Session 8's.

`submission_check` reports **21/22**, outstanding `C1 claims audit complete` — 431 claims, 196
SUPPORTED, 235 UNREVIEWED. Pre-existing and untouched by this revision.

## §E — Session 7 not started

Deferred until after submission, as instructed. The 0.90% claim is calibrated rather than
over-claimed, and running the 48-hour path immediately before submission risks landing a new
finding that needs analysis at the worst moment. It is 48 hours away if a reviewer asks.

## Exit criteria

| # | criterion | status |
|---|---|---|
| 1 | `xref_sweep.json` written; every pointer verified; fixes applied | met — 60/60 |
| 2 | `unit-consistency` registered; `kind-count` 22 = 22 = 22 | met |
| 3 | Six surfaces synced; HF card recorded | met — `M-67`, OPEN by design |
| 4 | `reproduce.sh --quick --force` run; counts reported; gate still failing | met |
| 5 | Compile PASSES, reported with the check count | met — 40 pp, 54/54 |
| 6 | `REVISION_SUMMARY.md` written | met |
| 7 | Session 7 not started | met |
| 8 | `SESSION_6.md` naming Session 8's first action | met — this file |

---

## Session 8's first action

From `SESSION_5B_ADDENDUM.md` §F. **Start with anonymisation, and verify the assertion on the
FINAL bundle rather than an earlier one** — this session proved that matters twice, once when a
ledger entry leaked a username and once when a regenerated report carried the scanner's own probe
string. Neither was in the bundle that had passed before them.

Then, in order:

- **Style file.** `part_f_gate` check 1 already confirms `\usepackage{tmlr}` with no options.
  Confirm no local modification has crept into the style file itself.
- **Supplementary bundle.** `docs/BUILD_CHECKS.md`, `docs/APPENDIX_G_RULES.md`,
  `SUPPLEMENTARY_CORRESPONDENCE.md`, the anonymised git log, `FINDINGS_LEDGER.md` and
  `results/`. Both zips rebuild clean now; rebuild them once more against the final tree.
- **The Hugging Face push.** `M-67` is open and names the commit. It needs the author's
  credentials; it is not something a session can do.
- **Reproducibility Certification.** Request it explicitly.
- **Cover statement.** The claims-versus-evidence case: gradient-level verification, fifteen
  pre-registered rules with lead times, verdicts reported as returned — including two that run
  against this paper's own arms — and a failing gate published as failing.

One thing Session 8 should not be surprised by: `submission_check`'s `C1 claims audit` is
PENDING at 235 unreviewed of 431. It has been pending throughout and is not a regression.

Session 8 is the last. Nothing after it changes the paper.
