# Session 5a — appendices

**Ran** 2026-08-31. Branch `main`. Appendices, front matter and generators only. **The body cut
is 5b.**

**Page count: 44 → 41.** Compile PASSES with 0 errors and 0 overfull boxes.

---

## The paper did not compile when 5a began

Before anything else: `compile_paper.py` was **FAILING**. Four `! LaTeX Error: Unicode character
≤ (U+2264)`, introduced by my own Session 4a text and by `M-64`'s ledger title, which Appendix G
quotes verbatim.

Two fixes, both at the right level:

- The two in the template prose became "h = 128 and below". **These are the only body lines this
  session touched**, and they are a build fix rather than a cut — 5a could not have reported a
  page count without them.
- The one from the ledger is not fixable in the ledger: `M-64`'s title is permanent committed
  text, and Appendix G quotes rule titles verbatim. So `scripts/md_to_tex.py` now sets `≤`, `≥`
  and `≠` as maths. The converter has to set what the ledger says.

## B.1 — the generator emits two products

`scripts/appendix_g_rules.py` now writes both:

- **body** — the table only: rule, what it governs, commit, lead time, tested by, verdict.
- **supplementary** — `docs/APPENDIX_G_RULES.md`, every rule's committed text **in full**.

**No ellipsis anywhere**, asserted by the generator rather than hoped for.

Removing the truncation alone would have been the obvious fix and the wrong one: at fifteen
rules it would have grown the appendix this session exists to shrink. Appendix G is now **40
template lines**.

One thing the literal reading would have missed. "In full" first produced entries that still
ended mid-sentence — `M-16` stopped at *"and at the 2500"* — because the generator's cue regexes
match only some rules and the rest fell through to a five-line head slice. That is exactly how a
quotation ends mid-sentence, ellipsis or no ellipsis. The supplementary now carries the **whole
committed entry** minus its heading, so there is nothing left to cut.

## B.2 — Appendix D, and where I stopped

`docs/BUILD_CHECKS.md` now carries the 21-kind registry, the self-test mechanics, the checker's
own defects and the exclusion mechanism. It is **generated** from
`docs/BUILD_CHECKS.template.md` by `build_paper.py`, from the same `paper_numbers.json` the
paper uses — a supplementary document quoting `{{cc_kinds}}` as a raw placeholder would be both
unreadable and unable to satisfy the re-pointed check.

The two lines replacing it say the count, not the list, and end with the evidence the addendum
asked for: the comparative checks caught **three defects in text written during this revision** —
two calibration figures naming no horizon, one numeral quoted three ways in a sentence. Not
enumerated in the body; the enumeration is in `BUILD_CHECKS.md`.

**Appendix D is 109 lines, down from 149, and that is where I stopped rather than reaching
≤ 1 page.** What remains is the addendum's own keep-list and nothing else: the six failure modes
that survived provenance checking, the two exclusions from the numeric comparison, the generated
retraction list, and the paragraph reporting that one of the build's own gates fails and is
published as failing. Cutting further would remove a caveat, and §A says to leave the pages when
that is the choice. **Reporting the target as missed rather than meeting it by cutting evidence
is the intended behaviour**, not an oversight.

## B.3 — figures at first reference

`build_paper.py` now inserts each figure immediately after the paragraph that first refers to it
by number, and the LaTeX float hint is `[!ht]` rather than `[htbp]` — "p", a float page of its
own at the end, is what carried them past §14. **Appendix C is retired**, not left as an empty
heading.

The placement is asserted, not assumed: a figure whose number appears nowhere in the prose has
no home, and the build fails rather than silently appending it. That assert fired immediately on
`paper_fig5_three_way.png` — because the prose refers to "Figure 5**a**", and my first pattern
required a word boundary after the digit. The pattern now allows a sub-panel letter while still
refusing to let a search for Figure 1 match Figure 15.

## B.4 — both checks re-pointed, neither relaxed

- **`kind-count`** reads the enumeration from `docs/BUILD_CHECKS.md`. It **PASSES: registered 21,
  §8 claims 21, `BUILD_CHECKS.md` enumerates 21**, and its self-test corruption is still caught.
- **`retraction-consistency` needed the same treatment, and the reason is worth recording.** It
  never named Appendix D — it scanned `PAPER.template.md` whole, and Appendix D was inside it.
  Moving that text out of the paper moved it out of the scan, creating a reader-facing surface
  where a retracted claim could survive unnoticed. `docs/BUILD_CHECKS.template.md` is now in all
  four of its file lists. This is the same shape as the addendum's §D point about the Hugging
  Face model card, and S-19's own lesson.

## B.5 — abstract

**369 → 347 words** against an unchanged 370 cap, so 6.3 has 23 words of headroom when it
rewords. Slightly above the ~340 asked. The last cut merged a genuine redundancy — the opening
named the same quantity twice, as "the quantity the method penalises with" and then as "the
trust metric the follow-up applies" — and I stopped there rather than start removing the limits
clause, which is a caveat.

## Exit criteria

| # | criterion | status |
|---|---|---|
| 1 | Generator emits table-to-body, full-text-to-supplementary; no ellipsis | met, asserted |
| 2 | Appendix D ≤ 1 page, two-line note, no enumeration | **partly** — 149 → 109 lines; see B.2 |
| 3 | `docs/BUILD_CHECKS.md` exists and carries what moved | met, and generated |
| 4 | Figures near first reference; Appendix C no longer empty | met — Appendix C retired |
| 5 | `kind-count` re-pointed and passing, not deleted or relaxed | met — 21 = 21 = 21 |
| 6 | Abstract ~340, cap unchanged | met at 347, cap still 370 |
| 7 | Body untouched | met but for two U+2264 compile fixes, named above |
| 8 | Page count before and after | met — **44 → 41** |
| 9 | `SESSION_5A.md` written | met |

`check_comparative_claims.py` **49/52**, self-test **52/52**. The three failures are the
`cross-artifact-sync` ones deferred to 6.3. `ledger_check.py` PASS.

---

## 5b's exact first action

**Start with §6.7's restructure**, the largest single body item, and do it before the retraction
cut so the cut is applied to the section's final shape rather than twice.

Rebuild §6.7 as: one primary table (baseline, correlation, margin, partial, verdict), one
controls table with a column stating what each control removes and what remains, and one verdict
paragraph — disagreement ranks error, the within-rollout effect is +0.419, and a free
subtraction comes close enough that this sample cannot separate them. The `M-43` replication and
the h=1 caveat stay but compress.

Then, in order:

- **§8 to ≤ 1 page.** Keep the append-only ledger, pre-registration with lead times including
  the negative bar, the third-party archival with its precise scope, the failing gate published
  as failing, and the 0.90% partition. The check-kind list and self-test description are already
  gone to `BUILD_CHECKS.md`, so §8's paragraph on them is now a pointer and should read as one.
- **Retraction narration to ≤ 4 instances**, by the `SESSION_2_ADDENDUM.md` §E criterion: keep a
  retraction in the body only if it changes how a reader reads a number still in the paper.
  `S-15` and `S-12` pass. Most "an earlier draft said" asides do not.
- **The two near-verbatim duplications** `SESSION_3_ADDENDUM.md` §C identifies, worth about a
  page at no cost to content: §2's "§6.4's mechanism is known, and we say so" against §6.4's
  "The effect is known and we are not claiming it", and §2's Malik paragraph against §6.8's
  opening. Keep the full treatment in §2 where related work belongs; reduce each §6 instance to
  one sentence pointing at it.

Two things 5b must not do. Do not touch the failing clean-clone gate paragraph or the exclusions
— they are caveats, and §A governs. And do not cut §5's h=1 reversal or the 20-seed
qualification; both run against this paper's own arms and both are load-bearing.
