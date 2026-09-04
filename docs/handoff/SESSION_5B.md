# Session 5b — the body

**Ran** 2026-08-31. Branch `main`.

**Compile PASSES, 0 errors, 0 overfull boxes. 41 → 40 pages.** Checks 49/52 with self-test
52/52; the three failures are the `cross-artifact-sync` ones deferred to 6.3.

Per §A there was no page target, and one page is what the cuts yielded. The cuts themselves are
the deliverable.

---

## B — the coverage audit, run before any text moved

`results/check_scope_audit.json`. All **21** check kinds classified by how they select input:
**14 whole-file, 3 named-region, 4 artifact-only, 0 unclassified**. An unclassified kind fails
the script, on the same principle as `input_set_audit.py`.

**It found a real gap, and it was not the one 5a fixed.** `count-consistency` — which scans
reader-facing files for near-miss spellings of a canonical value — named `PAPER.md`, `README.md`
and `MODEL_CARD.md`, and not `docs/BUILD_CHECKS.md`. Same class as the `retraction-consistency`
gap 5a caught, in a different check, and it would have gone on reading as protection. Both of its
claims now name the new file.

One correction to the audit itself: the first gap detector required `docs/BUILD_CHECKS.template.md`
of every whole-file scanner, and reported `count-consistency` as still broken after it had been
fixed. The two checks work at different tiers — `retraction-consistency` scans templates,
`count-consistency` scans built files — so the detector is now tier-aware and requires the right
name of each. A detector that reports a gap that is not there is as useless as one that misses one.

## C.1 — §6.7 restructured, and asserted presentation-only

Five controls described in prose, plus a separate variance-decomposition table, plus the r_dd
verdict paragraph, are now **one controls table** — with a column saying what each control removes
and what survives it — plus **one verdict paragraph**. The six-horizon primary table is unchanged.

**The claim set is asserted identical, not assumed:** 141 distinct placeholders before, 141 after,
none lost and none invented. 38 paragraphs → 33; 18,750 chars → 17,983.

All three required survivals confirmed present: `M-43`'s verdict key, `M-45`'s, `M-51`/`M-52`'s,
Session 3's h=128 companion, and the withdrawal of "the decisive one" as a description of the
within-step control.

**Honest note: this bought almost nothing in length.** The section is 172 → 171 lines. The
content of §6.7 is its numbers, and a restructure that preserves every one of them cannot be much
shorter. It is a better-organised section, not a smaller one.

## C.2 — retraction narration at four

By grep-and-classify against the criterion, not by reading the paper end to end. **21 lines
carrying retraction phrasing → 9, grouping into exactly four distinct retractions**, each kept
because a figure still printed reads differently without it:

| retraction | why it stays |
|---|---|
| the withdrawn "deployment horizon" label for h = 368 | every h = 368 figure reads differently |
| `S-15`, binomial → permutation | every P-value in §6.6 reads differently |
| the withdrawal of "the decisive one" | how the within-step control's figure is read |
| `S-12`, the withdrawn pre-registration | Figure 4's negative bar and §8's lead-time count |

Twelve cuts, each a process aside whose superseded value is no longer in the paper: the
single-seed figures §5 once quoted, the artifact-values claim, the dash in one permutation row,
the correlation once quoted without an interval, the overlap assertion, the "opposite" deviations,
the capacity over-claim, the framing this paper once used, the long-horizon reading, the
six-defects aside, "narrower than an earlier draft made it", and `M-28`'s fiftyfold, which §8 now
**states plainly** rather than narrating — which is what 5.1 asked for.

The count is by the addendum's own grep phrasings. One sentence sits outside them — §8's "the
abstract used to claim no number here was typed, which was false" — and it is left, because the
audit it explains is still in the paper.

## C.3 — §8

§8 is 26 lines and unchanged in length, because what 5a moved out of it had already gone. What
was left was **wrong**: its closing sentence still said *"Appendix D gives the argument, the
kinds, the self-test, the defects the self-test has found in the checker itself"* — and Appendix
D gives none of those any more. It now points at Appendix D for the failure modes and the
exclusions, and at `docs/BUILD_CHECKS.md` for the registry, the self-test and the checker's own
defects.

The same sentence duplicated Appendix D's description of what each check pins; that clause is cut
from §8, which keeps the count and the pointer.

## C.4 — the §2/§6 duplications

Both reduced to one sentence pointing at §2, with the full treatment kept there:

- §6.4's "The effect is known and we are not claiming it" no longer restates §2's four citations
  in the same order. It keeps what is ours — the sharing quantified, the cost measured.
- §6.8's opening no longer restates §2's Kuleshov/Malik framing. It keeps "what is new here".

## C.5 — checked, and no fix needed

The body table's "what it governs" column does **not** come from the cue-regex parse that was
producing head slices in the supplementary. It comes from the entry's heading line
(`appendix_g_rules.py:116-130`). **0 of 15 titles carry an ellipsis**, longest 121 characters. The
descriptions shipping in the paper were never truncated. Verified rather than assumed.

## D — compile is build status

Reported above and from here on. 4b reported a clean rebuild on a paper that did not compile;
that will not recur.

## Exit criteria

| # | criterion | status |
|---|---|---|
| 1 | `check_scope_audit.json` before any move; scanners confirmed | met — and it found a gap |
| 2 | §6.7 restructured; claim set asserted identical; three survivals | met — 141 = 141 |
| 3 | Retraction narration ≤ 4 in the body | met — exactly 4 |
| 4 | §8 trimmed; no duplication with `BUILD_CHECKS.md` | met — and a wrong pointer fixed |
| 5 | §2/§6 duplications to one sentence each | met |
| 6 | Appendix G body table checked against C.5 | met — no truncation, no fix needed |
| 7 | Compile PASSES; checks reported; page count not a target | met — PASS, 49/52, 41 → 40 pp |
| 8 | `SESSION_5B.md` written | met |

`ledger_check.py` PASS.

---

## Session 6's first action

**6.1 — re-point what 5a and 5b broke.** Only `cross-artifact-sync` is still failing, on three
files, and it is failing for the right reason: the rewritten abstract no longer contains
*"recomputed each build against a corrupted expectation"*, which `README.md`, `MODEL_CARD.md` and
`docs/EXTERNAL_READ_BRIEF.md` each assert it does. `kind-count`, `retraction-consistency` and
`count-consistency` are already re-pointed and passing.

Then 6.2 (`unit-consistency`, the one new kind), 6.3 (cross-artifact sync across all five
reader-facing files), 6.4 (`./reproduce.sh --quick --force`), 6.5 (`REVISION_SUMMARY.md`).

Two things 6.3 must not miss:

- **The Hugging Face model card is a sixth reader-facing surface and no check reads it**, because
  it is not in the tree. §13's own discipline applies — a retraction that holds in one document
  and not another is not a retraction, which is `S-19`'s lesson. Update it by hand and record
  that it was updated.
- **`docs/BUILD_CHECKS.md` and `docs/APPENDIX_G_RULES.md` are new reader-facing surfaces.** Both
  are now inside `retraction-consistency` and `count-consistency`; confirm they are inside 6.3's
  sync as well.

`e5_collapse_pct` is still the drift source that does not self-heal: `+0.10` → `+0.08` from
`M-66`. 6.4's rebuild must not let it pass silently.

## Session 8 — the one the plan is missing

`REVISION_BRIEF.md` ends at Session 6 plus the optional full reproduce, and nothing covers what
it takes to submit. Scheduled as **Session 8**, after 6 and independent of 7:

- **Anonymisation.** Verify the deny-list assertion runs and passes on the *final* bundle, not an
  earlier one. The August prescreening risk was a repository URL carrying the author's username.
- **Style file.** Confirm the compiled PDF uses the TMLR style and that no local modification has
  crept in.
- **Supplementary bundle.** `docs/BUILD_CHECKS.md`, `docs/APPENDIX_G_RULES.md`,
  `SUPPLEMENTARY_CORRESPONDENCE.md`, the anonymised git log, `FINDINGS_LEDGER.md` and `results/`.
  Assemble, scrub, verify.
- **Reproducibility Certification.** Request it explicitly.
- **Cover statement.** State the claims-versus-evidence case directly: gradient-level
  verification, fifteen pre-registered rules with lead times, verdicts reported as returned
  including two that run against this paper's own arms, and a failing gate published as failing.

Session 8 is the last. Nothing after it changes the paper.
