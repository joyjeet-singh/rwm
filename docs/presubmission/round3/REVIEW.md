# Round 3, R7 — fresh-eyes review

**How it was run, and where it departs from the plan.**
- **Session.** R7 ran in the same session as R0–R6, at the user's instruction ("Start R7"), not in a new terminal. The reviewer had written R6's front-matter edits, so this is not a fresh pair of eyes.
- **Independence kept where possible.**
  - Step 1 read the main text from the extracted PDF, not from memory of the source.
  - Step 2's two read-only Explore agents had no context from earlier sessions.
- **Extraction.** `pdftotext` is not installed. Step 1 used `pypdf` in layout mode on the committed build's `PAPER.pdf`, pages 1–31 (References begin on page 32). The output, `round3/body.txt`, keeps every glyph but loses most word spaces; it was read in chunks of about 300 lines.

Line numbers are `PAPER.md`'s before R7's fixes unless a row says otherwise. Every finding was checked against the source before any edit (step 4). Every fix is three sentences or fewer (step 5), and the fixes are listed at the end of this file.

## Step 1 — the whole read: summaries stronger than their sections

| # | where | says | the section says | verified | action |
|---|---|---|---|---|---|
| B1 | §1, second paragraph (`PAPER.md` 39) | "test the central training claim, which holds" | §5: it holds at long horizons and reverses at one step (l. 412–419); contribution 2's lead says so | yes | fixed: "which holds at long horizons" |
| B2 | §2, "§6.4's mechanism is known" (l. 178) | "the cost measured at 2.03× (§6.8)" | §6.8 (l. 1118) and §11 (l. 1289–1297): the independent members also differ in capacity and data order, so the comparison bounds the sharing effect rather than isolating it; at matched capacity it is 1.79× against an MDE of 2.00× | yes | fixed: "its cost bounded by the 2.03× an independent ensemble gains" |
| B3 | §6.4, first paragraph (l. 808) | "the cost measured at 2.03× on the overconfidence factor (§6.8)" | as B2 | yes | fixed: as B2 |
| B4 | §6.1, last paragraph (l. 655) | "the epistemic ordering is real and strong" | §6.5's heading and claim: "the ordering is weaker than it looks", no per-dimension cell survives correction; §6.6: a free signal ranks error nearly as well | yes | fixed: "real (§6.6), though weaker per dimension than it looks (§6.5)" |
| B5 | §5, after the by-horizon table (l. 406) | "the claim is weakest exactly where the model is trained" | the same paragraph calls h = 8 "the horizon the model is trained on" (l. 445), and there the gap excludes zero; the unresolved point is h = 1, inside that horizon | yes | fixed: "weakest inside the horizon the model is trained on" |
| B6 | §10, last paragraph (l. 1240) | the policy-free test "found that correcting the scale per horizon leaves every pairwise ordering … unchanged" | §11 (l. 1271–1277) and Appendix R: rule M-70's null is partly structural and its interval degenerate | yes | fixed: adds "a test whose null is partly structural (§11)" |

Read and found consistent with their sections, so not findings:
- §5.1's restatement of the A/B factors.
- §6.6's closing paragraph, which already carries its qualification.
- §6.8's "the trunk-sharing mechanism is the larger part of the effect where the method operates" (l. 1090). The same section's next paragraph says the arms bound the effect rather than isolate it.
- §7, §8 and §9 as they stood after R6.

## Step 2 — the two agents (appendix tables against every sentence that cites them)

| agent | appendices | tables | citing sentences | mismatches |
|---|---|---|---|---|
| 2 | M–V | 7 (N, O, P, U, and V's three) | 72 | 0 |
| 1 | A–L | 11 | about 120 | 7, all verified and fixed (one in part) |

**Agent 2's notes, checked.** Two points needed a second look:
- Appendix O at h = 32, where 1.68 × 1.08 against 1.83 "fits at the edge of rounding". It does: 1.685 × 1.085 = 1.828, inside [1.825, 1.835].
- Appendix N's pooled interval and its r_dd interval, which differ from §6.2's and §6.6's in the third decimal. The text says so at l. 942.

**Agent 1 (A–L): 11 tables (A, B, C, D ×2, E, H, J ×3, L), about 120 citing sentences, 7 findings.** Each was checked against
the template and the scripts before any edit; all 7 hold.

| # | where | finding | verified | action |
|---|---|---|---|---|
| A1 | Appendix B (l. 1452) | "the 28 runs §6.3 fits the σ-collapse rate over": the rate is fitted on 22 of the 28 (§6.3, Appendix J) | yes | fixed: "the 28 runs of §6.3's σ-collapse family"; "that rate" became "§6.3's rate" so the clause keeps its antecedent |
| A2 | §6.3 (l. 782) | "across all 28 runs … the collapse is linear … and its rate is nearly identical": the 5 gaussian_nll runs among the 28 rise (§6.3; Figure 4: "one falling and one rising") | yes | fixed: "the log-σ range moves linearly … at a nearly identical rate within each objective, falling under sampled MSE and rising under the corrected one" |
| A3 | Appendix J (l. 1846) | the same sentence | yes | fixed: as A2 |
| A4 | Appendix C (l. 1507) | "one world-model training run each at our 49.8 h scale": 49.8 h is all 33 runs (Appendix B); the longest is 4.4 h | yes | fixed: "a world-model training campaign each on the scale of ours, 33 runs in 49.8 h" |
| A5 | Appendix E caption (l. 1589) | "resolved by commit *subject* … hashes did not survive it": Data and code says 33 of the 35 cited commits kept their hashes; `appendix_g_rules.py` resolves the later rules by the commit that introduced their ledger heading | yes | fixed: the caption says which rules are found which way, with the count from `f1_n_moved_word` |
| A6 | Appendix H caption (l. 1682) and rows R-46, M-84 | the caption gives a checkpoint but no arena or n; R-46 and M-84 give no n_independent | yes | fixed: the caption says each row names its arena, and M-84's row gives its 16 trajectories (`x2_n_ins`). R-46's n is not recorded by its artifact: OUT_OF_SCOPE |
| A7 | Appendix D, first table (l. 1529) | no caption arena, n or checkpoint, though its verdict cells quote measured values | yes | fixed: one sentence says each verdict cell's figures are those of the section it cites, on that section's arena, n_independent and checkpoint, and that the second table gives them claim by claim |

Agent 1's note, not counted among the findings, also holds. With two tables, three pointers became ambiguous: §4's "Appendix D's verdict column" and "Appendix D gives the full table", and Appendix C's "Appendix D's table". **Fixed**: each now names the first table.

Agent 1 also confirmed, without a finding:
- Appendix L's cells against §5, §5.2 and §5.3;
- the second table against the body;
- Appendix E's verdicts and counts (23 rules, 22 positive, S-12 at −2.9 h);
- Appendix B's arithmetic (19.7 + 30.1 = 49.8 h);
- Appendix J's 21.7× and term counts;
- Appendix H's R-39 and M-84 figures.

## Step 3 — Annex 4's checklist

| item | check | result | evidence |
|---|---|---|---|
| 1 | no rendered file contains "trains twice as long" | pass | `grep -il` over `PAPER.md`, `PAPER.tex`, `README.md`, `MODEL_CARD.md`, `docs/*.md`: no hit; C26.1's forbidden half passes |
| 1 | every statement of the verdict outside §5.2 carries "at our budget" and "depends on the training budget" or an equivalent | pass after fix | abstract l. 17, contribution 3 l. 75, §12 l. 1312 and Appendix D's claims row l. 1547 carry both. Appendix D's second table, row l. 1564, lacked the second: **fixed** in `evidence_summary.py`, which now adds "the ranking depends on training length (Appendix U)". Appendix E's verdict column (l. 1611) prints each rule's returned string verbatim by design (`appendix_g_rules.py`), and "AT OUR BUDGET" is in the string itself; it is left as a record. README, model card and cover statement do not state this verdict |
| 1 | §5.2's equal-compute paragraph reports all four readings at 5,000 iterations and the 10,000 summary | pass | `PAPER.md` 525 |
| 1 | Appendix U exists, is generated and is labelled post hoc | pass | l. 2326–2329; `appendix_u_table`, built by `paper_numbers.py` |
| 1 | the original's hours are bound | pass | `PAPER.template.md` 468: `{{orig_h_32_8}}`, `{{orig_h_32_32}}` |
| 1 | §5.2's lead "At our budget, shorter histories win." | pass | l. 517 |
| 2 | contribution 7, §3.1, the Appendix D row, §7.2 and the abstract describe all ten episodes first | pass | contribution 7 l. 87; §3.1 l. 300; Appendix D l. 1577 "all ten episodes (20)"; §7.2 l. 1145; abstract l. 26 |
| 2 | no sentence gives the held-out pair's h = 100 figure without the all-ten figure beside it | pass | the only one, §7.2 l. 1145, puts "where the larger arena resolves no change" beside it, after the all-ten figures in the same paragraph |
| 2 | the row's claim text no longer says "overstates" | pass | l. 1577; `grep -i overstat` finds no alignment row |
| 2 | G2 passes | pass | C27.1 PASS (re-anchored in R6) |
| 3 | pre-registered before its readings, checkable in `git log` | pass | `738bc91` "PRE-REGISTER action-sensitivity rule X2" (13:12:25, with `scripts/action_sensitivity.py`) precedes `104a8e6`, which adds `results/action_sensitivity.json` (13:19:25) |
| 3 | the discharge entry is verbatim | pass | ledger M-85, written by `round3/r1_write_discharge.py` from the artifact |
| 3 | Appendix V exists | pass | l. 2360 |
| 3 | §7.2's sensitivity sentence carries X2's figure (G3) | pass | l. 1145, "+676.3% [+454.8, +1060.0]"; C27.2 PASS |
| 3 | the variant installed matches the reading | pass | RESPONDS TO THE ACTION; `paper_numbers.py` asserts `x2_reading` before it puts it |
| 3 | Appendix E and Figure 1 include X2 | pass | Appendix E row M-84 (l. 1615); §8 "Figure 1 and Appendix E give the lead time for all 23" |
| 3 | the model card is updated | pass | `MODEL_CARD.md` 256 |
| 4 | §5.2's caption has one clause about M-74 | pass | l. 507–509 |
| 4 | §5.3 names the baselines that moved, with signed figures | pass | l. 587 |
| 5 | S1–S17 done, or logged with a reason | pass | `SESSION_LOG.md`, R4 entry: all done; S15 needed no change |
| 6 | H1–H7 done | pass | `SESSION_LOG.md`, R5 entry |
| 6 | round 2's OUT_OF_SCOPE lines each closed or carried forward | pass | see the table below |
| 7 | main text at or below 20,771 | pass | 20,745 after R7's fixes (`round2/t6_words.py`) |
| 7 | no result lost: template keys against R0's, every removal justified | pass | removals since R0 are R2's and R4's, each justified in its entry (`SESSION_LOG.md` l. 210 and l. 321); R5, R6 and R7 removed none |
| 7 | `xref_sweep` 0 suspect | pass | build log |
| 8 | `CONSISTENCY.md` has a row for every restating sentence, with every reading | pass | R6; E3's quoted wording now matches the row, which said "agrees" until this session's fix |
| 8 | the abstract passes C12.1 | pass | 370 / 23 |
| 8 | at most 8 bullets of at most 3 sentences | pass | 8 bullets; at most 3 sentences each, counting each bold lead |
| 8 | the title, abstract and conclusion agree | pass | title "Right Order, Wrong Size"; abstract "gets the order right and the size wrong"; §12 "As the scalar the method applies, ensemble disagreement gets the order right and the size wrong" |
| 9 | every table and figure caption carries its arena, n_independent and checkpoint | pass | body tables and figures read in step 1: §5, §5.2, §5.3, §6.2 ×3, §6.5, §6.6 ×3, §6.7, §6.8 ×2, Figures 2, 3, 5 and 6. Figures 1 and 4 plot no evaluation (lead times; training curves). The moved table carries all three per row (Appendix D's lead, l. 1558). Appendices A–V are step 2's |
| 10 | README, model card and cover statement: no claim stronger than the paper's | pass after fix | see P1–P4 below; the cover statement's claims are qualified as the paper's are |
| 10 | … and no unbound number | README and model card pass; cover statement → R8 | README and model card are built from templates through `paper_numbers.json`. `docs/COVER_STATEMENT.md` is hand-kept, and its counts are stale: 57 pages, 22 rules, 21 positive, seven claims withdrawn on evidence. PLAN R8 item 5 refreshes its "rule count, page count and retraction counts" |
| 11 | §13's paragraph follows ruling V7 | pass after fix | it was four sentences and kept "a reviewer who chooses to look can identify the author". **Fixed**: two sentences, the facts kept (code public; bundle scrubbed and deny-list clean; reasoning in `docs/DOUBLE_BLIND_DECISION.md`). The cut sentence is in BUILD_CHECKS' moved list (rule 9) |
| 11 | commit labels anonymous everywhere, including Appendix E's column | pass | `part_f_gate` check 2 (PDF text, bytes, metadata, figures) PASS in R6; Appendix E's column prints labels in the submission build (R4 S6) |
| 11 | the deny-list scan passes | pass | `part_f_gate` check 2; `make_anon_bundle.py` self-test and scan PASS at R5 |

**Round 2's OUT_OF_SCOPE lines** (`docs/presubmission/round2/OUT_OF_SCOPE.md`):

| line | status |
|---|---|
| T5, D-12's range against the paper's | closed: R5 H3, ledger D-37 |
| T5, R-28 SETTLED against §5's CANNOT BE SETTLED | closed by its own reading: different units, the paper's is the governing one |
| T5, C-13's Table S7 | closed: R5 H3, ledger C-16 |
| T7, Appendix R's "as §6.8 said before the runs" | closed: Appendix R now reads "as rule M-49's own text said before the runs (ledger `M-49`)" (l. 2289) |
| T7, §6.5's orphaned bold line | closed: it sits in §6.5's claim paragraph (`PAPER.template.md` 861) |
| T8, the package documents' stale figure-overlap lines | carried forward: PLAN R8 item 5 |
| T8, B8, the training drivers' exit status | closed: R5 H1 |
| T8, B9, float-shaped 7-character prefixes | carried forward by design: the scrub covers them, and the self-test plants a full hash (R5 H7) |
| T8, B11, stages 20t1 and 20t4 read `cache/` behind NEEDS_WEIGHTS | carried forward: the cache readers' convention, and they skip correctly in a clean clone |
| T10, `trend.reading` | closed: R5 H2 |

## Public-facing text (Annex 4 item 10)

| # | file | says | the paper says | action |
|---|---|---|---|---|
| P1 | README finding 1 | "The base paper's central training claim reproduces, and the advantage grows with horizon." | contribution 2: "reproduces, and reverses at one step" | fixed: the heading names long horizons and the reversal, and one clause gives M-64's short-window result from its keys |
| P2 | README finding 3 | "As a ranking it survives adversarial testing." | §6.6: it survives the counter, not the free step-size signal (SURVIVES entry-res ONLY) | fixed: one sentence gives the step-size figures and the unresolved margin, from `e7_*` keys |
| P3 | README finding 6 | "That mechanism is tested, not merely asserted, and it holds." | §6.8 and §11: it bounds the sharing effect rather than isolating it; at matched capacity, 1.79× against an MDE of 2.00× | fixed: the heading says "is supported", and one sentence gives the bound and M-49's figures from keys |
| P4 | model card, "The result these support" | "Normalised error at a 368-step horizon" | the table is relative-L1 (§3.1, §5); "normalised" reads as nRMSE | fixed in `build_model_card.py`: "Relative-L1 error, the reference's own metric" |

## The fixes (step 5)

All are wording only, each three sentences or fewer:
- `round3/r7_patch.py` items:
  - `body`: B1–B6 and ruling V7;
  - `agents`, `agents2` and `agents3`: A1–A7 and the three pointers;
  - `readme`: P1–P3;
  - `card`: P4;
  - `moved`: rule 9, for V7's cut sentence.
- `scripts/evidence_summary.py`, for item 1's second-table row.

Logged rather than fixed, in `round3/OUT_OF_SCOPE.md`: R-46's n_independent, which its artifact does not record.

No key was added or removed; every figure the new sentences print comes from an existing key (`m64_h1_*`, `e7_*`, `m49_*`, `x2_n_ins`, `rt_runs`, `f1_n_moved_word`). Nothing reached the size that would mean stopping with `BLOCKED`.
