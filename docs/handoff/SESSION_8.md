# Session 8 — submission mechanics. The last session.

**Ran** 2026-09-04. Branch `main`. Nothing here changed a claim.

**Compile PASSES, 40 pages, 0 errors, 0 overfull boxes. 54/54 comparative claims, 54/54
self-test. Rendered-PDF pass 5/5. Submission gate 7 of 8 — the eighth is the clean-clone gate,
which now runs and fails by design. `ledger_check` PASS.**

---

## §A — the rendered-PDF pass

`results/pdf_render_check.json`, **5/5 PASS**. A one-time check, not registered as a kind: it
exists because text moved through a transformation layer in 5a and 6, and those moves are done.

| # | check | result |
|---|---|---|
| 1 | appendix letters resolve | headings `ABCDEFGH`, contiguous, no dangling reference |
| 2 | figure numbers match their references | 1–6 in both source and PDF |
| 3 | table headers survive rendering | 21 tables, every header cell present |
| 4 | every numeral the source states survives | 763 distinct, none lost |
| 5 | section cross-references resolve | 24 references, 24 headings, none unresolved |

**It found no defect in the paper. Every failure it reported was in itself**, four rounds of it:
a regex requiring no space in "Figure 6"; a caption detector expecting a colon that extraction
drops; header cells split on an *escaped* pipe, producing fragments that then read as absent;
and numerals from the generated HTML comment LaTeX never sees. The instrument had to be fixed
four times before it could say anything about the paper. The appendix re-lettering Session 6
applied holds in the rendered PDF.

**What it cannot do, recorded in the artifact rather than implied.** Extracted text loses layout.
It sees that header cells are present and that references resolve; it cannot see a column
rendered too narrow or a float landing pages from its reference. §F.2 is what covers those.

## §B — the environment no-op, backward

**No earlier session reported a clean build that was a no-op**, and the check corrected a claim
in Session 6's own report.

- Sessions 1, 2, 2B, 3 and 4a explicitly recorded **paper not rebuilt**. No build was claimed.
- 4b, 5a and 5b invoked `build_paper.py` and `compile_paper.py` **directly, with the absolute
  venv interpreter**. The no-op path exists only in `reproduce.sh`'s `PATH` lookup, so those
  sessions could not have hit it — and each reported artifact-specific values a no-op cannot
  produce.
- Session 6 ran `reproduce.sh` and caught the mismatch itself.

**The correction.** Session 6's handoff said the first invocation "exited 0" and "returned
success". That is wrong: `reproduce.sh:80` exits **2** on an environment mismatch, verified by
running it against the system interpreter and reading the status. The exit 0 came from the
background wrapper reporting its own status, not the script's. The environment gate works; the
report of it did not. `SESSION_6.md` now carries the correction marked as one rather than
silently edited.

## §C — anonymisation, on the assembled bundle

Run against the **final** tree, after every Session 8 change. **0 residual identifying hits**,
and **22 of 22 files the paper cites by name are present in the bundle**.

The deny-list covers everything §C names: the author's given name, surname and combined forms,
the GitHub username and URL, the Hugging Face username and URL, e-mail addresses, ORCID
identifiers by regex, absolute home-directory paths, and resolvable Software Heritage
identifiers. The scrubber plants a known string on every run to prove its own scan still
detects one.

Two absences from the bundle, both deliberate and now recorded as decisions:

- **`PAPER.pdf`** — it is the submission, not supplementary evidence. It is separately scrubbed
  by gate check 2, over its text, its raw bytes, its metadata and its figures.
- **`docs/COVER_STATEMENT.md`** — editor-facing correspondence, not evidence. **The two bundles
  disagreed about this**: `build_supplementary.py` excluded it and `make_anon_bundle.py` did
  not, so the reviewer's copy carried a file the supplementary archive did not. Both exclude it
  now, and the reason is in both files.

## §D — the clean-clone check, run once with `CLONE_RESULTS`

A real clean clone, the upstreams linked at their pinned commits, `reproduce.sh --quick --force`
run inside it (91 stages), and the gate pointed at its results.

**The number changed, and it is reported rather than tolerated.**

| | published before | measured now |
|---|---|---|
| files regenerated | 47 | **46** |
| values compared | 8,186 | **9,090** |
| bitwise identical | 7,981 (97.50%) | **9,022 (99.25%)** |
| **differing** | **178** | **68** |
| share of `results/` | 0.90% of 905,391 | **1.00% of 908,630** |

The 178 was carried from an earlier comparison; this is the first time the check has been run
end to end. More values are compared because Session 6 gave seven previously stage-less
artifacts a stage. **No tolerance was applied.** The gate fails, it says where, and it now fails
on a current measurement. The check no longer reads NOT RUN.

`README.md` and `MODEL_CARD.md` were regenerated so the headline values agree — `cross-artifact-sync`
caught the staleness immediately, which is what it is for.

## §E — style file and bundle

**`tex/tmlr.sty` was added in exactly one commit (`9919c4c`) and has never been modified since**
— verified from git history, not asserted. `part_f_gate` check 1 confirms the PDF is built with
`\usepackage{tmlr}` and no options, which is submission mode.

One caveat stated rather than glossed: "unmodified **relative to upstream**" rests on the
vendoring commit and `tex/README.md`'s provenance note. No hash of the official file is recorded
in this repository, so a byte comparison against `JmlrOrg/tmlr-style-file` has not been made
here.

Both bundles rebuilt against the final tree: `supplementary.zip` 366 entries, 10.0 MB;
`supplementary_anon.zip` 395 entries. Under the 100 MB limit.

## §F.2 — reading the paper, which found what no check could

The abstract's emphasis matches the body's: both lead with the miscalibration as a
depth-dependent scale, and §6.2's λ paragraph lands as the measurement it now is — objection,
then the constant that would repair it and the factor of 4 it moves by, then *"No single λ is
both of those"*, then the mechanism, then the limit in the same breath.

**§6.7 was not more legible after the restructure, and that is a defect Session 5b introduced.**
The heading read "**Six controls**" over a **ten-row** table, because the restructure merged the
depth controls with the variance decomposition — two things that answer different questions —
and a reader counting rows against the heading gets a mismatch. Worse, the rank partial sat at
+0.906 against a pooled +0.605 with nothing explaining why *removing* something raised the
number: it is a correlation of ranks, a different statistic.

Fixed by naming the table's two halves and stating the incomparability outright. The claim set
is unchanged — 141 distinct placeholders before and after — and 54/54 checks still pass.

This is exactly the class the addendum predicted: the checks verify relations between numerals,
and clarity is a different property.

## §G — the cover statement

`docs/COVER_STATEMENT.md`. Makes the case directly on both TMLR questions: claims-and-evidence
(gradient-level verification, fifteen pre-registered rules with lead times, verdicts reported as
returned including `DOES NOT GENERALISE` and `UNDER-POWERED`, twelve retractions — six of
numbers and six of framings — and a gate published as failing), and interest under the
reproducibility carve-out. Reproducibility Certification is requested explicitly, with the seven
additions that support the criterion listed.

Every figure in it was checked against `results/paper_numbers.json` rather than typed.

## Exit criteria

| # | criterion | status |
|---|---|---|
| 1 | `pdf_render_check.json`; all five §A checks pass | met — 5/5 |
| 2 | Backward environment check recorded | met — and it corrected a false claim |
| 3 | Anonymisation scrub on the assembled bundle | met — 0 hits, 22/22 cited files present |
| 4 | Clean-clone check with `CLONE_RESULTS`; number reported; not toleranced | met — 178 → **68** |
| 5 | TMLR style confirmed unmodified; bundle assembled and verified | met, with the upstream caveat stated |
| 6 | Cover statement drafted | met |
| 7 | `M-67` still OPEN — Claude Code does not close it | met — untouched |
| 8 | `SESSION_8.md` listing what remains manual | met — this file |

---

## What remains manual

Everything below needs a person. Nothing below is blocked on further analysis.

1. **Push the Hugging Face model card.** `M-67` is OPEN and names the commit to sync against.
   `MODEL_CARD.md` — its generated source — is current and passes every check. The remote copy
   is publicly visible, linked from a repository §13 admits is findable, and still asserts a
   sentence the rewritten abstract dropped. **Do this before submission, not after**: the
   paper's own discipline is that a retraction holding in one document and not another is not a
   retraction. Close `M-67` with the commit it was synced against.

2. **Read the compiled PDF end to end.** §F.2 read the abstract, the λ paragraph and §6.7, and
   found a real defect in the third. The rest has not been read as a reader. Layout in
   particular is unchecked: the render pass explicitly cannot see a column rendered too narrow
   or a float landing pages from its reference.

3. **Submit.** Upload `PAPER.pdf`, attach `supplementary_anon.zip` as the reviewer's copy, paste
   `docs/COVER_STATEMENT.md` into the submission form, and request Reproducibility Certification
   on the form as well as in the statement.

4. **`submission_check`'s C1 claims audit is PENDING** at 235 unreviewed of 431. It has been
   pending throughout the revision and is not a regression. It is a review backlog, not a defect,
   and it does not gate submission.

5. **Session 7** — the full 48-hour `reproduce.sh` — stays deferred until after submission, per
   `SESSION_6_ADDENDUM.md` §E. It would raise the 1.00% figure. It also carries a real chance
   that the 31 training runs do not reproduce bitwise on CPU, which would land a new finding
   needing analysis at the worst possible moment. If a reviewer asks, it is 48 hours away.

Nothing after this changes the paper.
