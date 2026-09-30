# Decisions for the user — pre-submission programme

A session that stops with `BLOCKED` writes its question here under its own anchor
(`## SX-<short-name>`), with the evidence and the options. The user answers under the question,
then launches the same session with `Resume session SX.`

Nothing is decided here by a session. An answer is recorded verbatim, with its date.

---

## S1-original-vs-plan

Asked in chat by S1 on 2026-09-28, before the pre-registration commit, because extracting the
original's specs (`ORIGINAL_SPECS.md`) showed three places where the plan's drafts depart from
what the original states.

1. **Rule BASE, training regime.** The original trains its baselines with teacher forcing
   (2501.10100v1 §IV-D, p. 8) and compares them against RWM-AR; PLAN S2b trains the MLP and the
   transformer autoregressively over N = 8.
   **Answer (verbatim, 2026-09-28):** "Both regimes"
2. **Baseline architectures.** The original's Table S7 (v1 p. 15) against PLAN S2b's Gaussian RSSM
   (PlaNet), learned positions and ±5% parameter matching.
   **Answer (verbatim, 2026-09-28):** "Both if possible. Otherwise original table S7"
3. **Rule MN, grid.** The original's one-factor neighbours of (32, 8) in its Fig. 6 grid, against
   the plan's grid, which includes (64, 8) and (32, 4).
   **Answer (verbatim, 2026-09-28):** "Original's neighbours (8)"

**How S1 applies the answers:**
- Answer 1 gives two pre-registered verdicts, each with Holm's correction across its three baselines: M-75 for teacher-forced baselines (the claim as the original makes it) and M-76 for autoregressive baselines (architecture with the training regime held fixed).
- Answer 2: Table S7 architectures govern both verdicts. The parameter-matched variants of PLAN S2b run only if S2b's timing probe projects every baseline run, both specs, within the 20 CPU-hour cap. If run, they are reported alongside and never govern.
- Answer 3 fixes the grid in M-74.

## S2b-baseline-cap

S2b stopped BLOCKED on 2026-09-28 at 19:00, before queueing any baseline run.
- **The block:** the 18 governing Table S7 baseline runs (rules M-75 and M-76: MLP, RSSM and transformer × tf and ar × seeds 0–2) project **22.01 CPU-hours** against PLAN Appendix C's **20-hour** baseline cap. PLAN S2b says: "If the baselines project above their cap, stop with BLOCKED. Never drop a baseline yourself." M-75 and M-76 say the same.
- **Evidence:** `results/baselines_timing.json` (`scripts/baselines_timing.py`). All 13 probes ran 20 iterations with every loss finite and falling; nothing diverged.

| Table S7 arm | projected CPU-hours, 3 seeds |
|---|---:|
| MLP tf / ar | 0.21 / 0.30 |
| RSSM tf / ar | 8.43 / 6.85 |
| transformer tf / ar | 3.09 / 3.14 |

**Why the projection is conservative:**
- The probes ran while the M-74 sweep trained. The calibration factor (0.737) carries that contention through; it also carries RWM's checkpoint evaluations at 500 and 2,500 iterations, which the baselines never run.
- Scaling instead by the measured contention alone (the centre probe took 1.98 s/iter contended, against 1.07 uncontended) gives roughly 16 hours. That figure is an estimate, not the rule's projection.

**What else is true:**
- The sweep (19.53 h projected) plus these baselines (22.01 h) totals 41.5 h, inside PLAN Appendix C's 45-hour cap on all new runs.
- The parameter-matched variants would bring every baseline run to 46.07 h, so under M-75 and M-76 they are **not run** (the transformer at d_model 160 costs 9.8 h per regime).
- The RSSM at the original's Table S7 size (3.18 million parameters) is 15.3 of the 22 hours.

**Options:**
1. **Raise the baseline cap to cover the 22.01 h projection** (for example to 23 h). Queue all 18 Table S7 runs after the sweep. The matched variants stay unrun. Recommended: nothing is dropped, and the all-new total stays within 45 h.
2. **Keep the cap and re-probe once the sweep has finished**, on an idle machine. That delays queueing the baselines until the sweep ends, around 2026-09-29 10:30.
3. **Another decision**, such as fewer seeds or a smaller RSSM. That would change M-75 and M-76, which fix three seeds and Table S7 sizes, and would need a new ledger entry.

**Answer (verbatim, asked in chat, 2026-09-28):** "Raise cap; queue all 18"

**How S2b applies it:** the baseline cap becomes 23 CPU-hours, covering the 22.01-hour projection. All 18 Table S7 runs are appended after the sweep, in the rules' order: M-75 (tf) then M-76 (ar), MLP, RSSM, transformer, seeds 0–2. The parameter-matched variants (46.07 h in all) do not fit and are not run. The projected all-new total is 19.53 + 22.01 = 41.5 h, within Appendix C's 45.

## S3-alignment-defect

S3 stopped BLOCKED on 2026-09-28 at 19:30, at item 4. **Both of the plan's stop conditions fired:**
- the n = 4 point estimates do not reproduce 75% and 9.5%;
- the n = 20 companion differs in direction.

**Evidence:** `results/alignment_defect_ci.json` (`scripts/alignment_defect_ci.py`). It uses the released checkpoint, rolled out exactly as `scripts/step4_0a_restate.py` rolls it out, and gives the overstatement at h = 368 as err(released pairing, offset 0) / err(causal pairing, offset 1) − 1.

| Arena | Trajectories | nRMSE, as published (per-step, mean of ratios) | nRMSE form 1 | relative-L1 |
|---|---|---|---|---|
| **Protocol A**, where the published figures come from: 10 windows sampled (seed 0) from episodes 1 and 8, **overlapping** | 10, not independent | **74.70%** (the paper's 75%) | 23.51% | **9.48%** (the paper's 9.5%) |
| §5's held-out arena: 4 non-overlapping | n_independent 4 | 10.73% [4.98, 12.84] | **6.55% [0.95, 7.97]** | **7.88% [3.11, 13.02]** |
| All ten episodes, 20 non-overlapping (in-sample for the checkpoint) | n_independent 20 | −3.97% [−16.97, 5.48] | −2.14% [−9.97, 3.95] | −4.64% [−13.36, 3.17] |

The intervals are 95% cluster bootstraps over whole trajectories, with both pairings inside each draw (exact over 256 resamples at n = 4; 20,000 at n = 20).

**What the evidence says:**
1. **The script reproduces the published figures exactly on their own arena** (74.70% and 9.48%, identical at printed precision). The computation is right; the arena and the estimator are the issue.
2. **One trajectory makes the 75%.** In Protocol A's ten overlapping windows, the window starting at row 8,375 (episode 8) is overstated by +110.7% (nRMSE) and +81.3% (relative-L1); the other nine range from −1.8% to +10.6%. The published nRMSE takes the RMSE across trajectories at each step and averages ratios over dimensions, which lets that one trajectory dominate. Form 1 on the same ten windows gives 23.5%.
3. **On the paper's own standard, independent trajectories with a cluster bootstrap:**
   - on the held-out pair, the overstatement is about **7–8%** (relative-L1 7.9% [3.1, 13.0]; nRMSE form 1 6.6% [1.0, 8.0]), and all four trajectories are positive;
   - **across all ten episodes it reverses sign** (−4.6% and −2.1%), with intervals spanning zero and per-trajectory values from −47% to +35%.
4. **D-13 stands.** Row t holds the action that produced state t, and the all-zero actions at every reset row say so. The released evaluation's pairing is still one step stale. **What does not stand is the size, and the consistency of sign, of what that costs in error.**

**Where 75% and 9.5% appear:**
- the abstract (`PAPER.template.md:13`);
- the contribution bullet "the checkpoint is materially better than its own evaluation reports" (`:65-69`);
- §3.1 (`:383-384`);
- §7.2 (`:1448`);
- PLAN Appendix A's new abstract, which S4 installs.

The source is `results/step4_0a_results.json` via ledger R-15.

**Options:**
1. **Restate on independent trajectories.** Recommended: it is the paper's own standard, and the only one the 75% fails.
   - §7.2, §3.1 and the contribution bullet give the held-out n = 4 figures with intervals, relative-L1 7.9% [3.1, 13.0] and nRMSE form 1 6.6% [1.0, 8.0], both at h = 368.
   - §7.2 adds the n = 20 companion, which reverses sign.
   - "Materially better" and the 75% go. The defect stays a correctness defect, a one-step stale pairing, with a small error cost that is not consistent in sign.
   - A supersession ledger entry records it. The abstract sentence (current and Appendix A) is rewritten to match.
2. **Keep 75% and 9.5%, labelled as Protocol A**, with the independent-arena figures and the reversal beside them. The headline number stays, qualified.
3. **Withdraw the size claim entirely.** Keep the convention defect (§7.2's alignment argument and the reset-row evidence) with no overstatement figure.

**Answer (verbatim, asked in chat, 2026-09-28):** "Restate on independent"

**How S3 applies it:**
- §7.2, §3.1 and the contribution bullet give the four-trajectory held-out figures with their intervals, in both metrics, at h = 368.
- The current abstract gives one of them, nRMSE form 1 with its interval (the primary metric of §3.1). With both, the abstract held 20 numerals, and the abstract-budget check (C12.1) allows 18. The check was not loosened.
- §7.2 adds the twenty-trajectory companion, which reverses sign, and the reset-row evidence for the convention.
- "75%" and "materially better" go, and the withdrawn figures are named once, with their supersession entry.
- The supersession entry is S-20. It withdraws the 75% / 9.5% framing, which is a framing rather than a numbered claim: R-15's measurements stand as measured.
- **S4 must install PLAN Appendix A's abstract with this sentence rewritten to the same independent figure, not with 75% and 9.5%:** `{{ad_nind}}` trajectories, `{{ad_nrmse}}% {{ad_nrmse_ci}}` in nRMSE, within C12.1's budget. SESSION_LOG's S3 entry says so.

## S4-abstract-budget

Asked in chat by S4 on 2026-09-28, before any S4 edit. **The plan contradicted itself on the abstract:**
- it said to install Appendix A's abstract with every listed number bound, in at most 330 words;
- measured with C12.1's own counter (`scripts/check_comparative_claims.py`, abstract-budget), Appendix A as written is 347 words and 23 numerals;
- restated on the independent alignment figures that S3's ruling requires, in both metrics with both intervals (S10 checklist item 4), it is about 27 numerals;
- C12.1 caps the abstract at 18 numerals, and §1.2.8 says never to loosen a failing check.

**Options put:**
1. Trim to fit C12.1: move six figures to the body and give one alignment metric (recommended).
2. Full Appendix A, alignment on the independent figures in both metrics with both intervals; raise C12.1's cap to fit, with the reason recorded in the check as its three earlier raises were.
3. Full Appendix A with one alignment metric; raise the cap to fit.

**Answer (verbatim):** "Full Appendix A; raise cap"

**Title, asked at the same time.** The options were Appendix A's primary and its alternate. **Answer (verbatim):** "Right Order, Wrong Size (Recommended)"

**How S4 applies it:**
- The abstract gives every number Appendix A lists, bound through `paper_numbers.py`.
- The alignment sentence uses S3's independent figures (`ad_*`) in both metrics with both intervals, and states the ten-episode reversal.
- The wording is trimmed to at most 330 words.
- C12.1's `max_numerals` rises to the count installed. The reason goes beside the three earlier raises and names this ruling as its authority; the word cap stays at 370.

## S5-bundle-presubmission

Asked in chat by S5 on 2026-09-28. **The problem:**
- `scripts/make_anon_bundle.py` walks all of `docs/`, and nothing excluded `docs/presubmission/`.
- So the anonymous bundle would ship this programme's own records: PLAN, SESSION_LOG, DECISIONS_FOR_USER with the user's rulings, the unsent author query, and FILE_MAP.
- PLAN.md and FILE_MAP.md quote the paper's old title, which item 4 keeps out of the bundle.
- S3 had flagged the directory for "the bundle session", but no later session edits the bundle builders, and S11 makes no edits.

**Options put:**
1. Exclude the directory from both builders (recommended).
2. Ship it and scrub the old title from PLAN and FILE_MAP.
3. Leave it for later.

**Answer (verbatim):** "Exclude the directory (Recommended)"

**How S5 applies it:**
- `EXCLUDE_DIRS = ("docs/presubmission",)` prunes the directory from the walk in both `scripts/make_anon_bundle.py` and `scripts/build_supplementary.py`, with the ruling cited beside it.
- PLAN.md and FILE_MAP.md stay as records, unedited.
- A dry run of `collect()` gives 459 files, none under `docs/presubmission/`, and none containing the old title. The gitignored `docs/presubmission/sources/` is no longer walked.

## S8-discharge-status

Asked in chat by S8 on 2026-09-29, after the three verdicts were computed. **The problem:**
- The rules M-74, M-75 and M-76 say the discharging session records the verdict "in a new ledger entry naming this one". They leave whether it also sets the rule's own `Status` line to be "settled under" PLAN §1.2.3, which says never to edit a ledger entry in place.
- Every earlier rule's Status line was set at discharge (for example M-70, "DISCHARGED … returns DOES NOT REORDER"). That line is what `scripts/ledger_check.py` and Appendix E's generator (`scripts/appendix_g_rules.py`) read.

**Options put:**
1. New entries, plus the Status line (recommended).
2. New entries only, leaving the rules' Status lines reading "NOT YET DISCHARGED".

**Answer (verbatim):** "New entries + Status line (Recommended)"

**How S8 applies it:**
- M-77, M-78 and M-79 record the three verdicts exactly as the scripts return them.
- In M-74, M-75 and M-76 only the `Status` line changes, to "PRE-REGISTERED, DISCHARGED by `…`. **It returns X.** Recorded in `M-7x`." No character of any rule's text changes, and `git diff` shows one line per rule.

## S9-contributions-abstract

Asked in chat by S9 on 2026-09-29. **Two plan constraints collided:**
- S9 says "add one contribution bullet" for resolved verdicts, and all three resolve (NOT OPTIMAL AT OUR BUDGET, REPRODUCES, RWM AHEAD OF ALL THREE). But S4 capped the contributions at 7 bullets, and S10's checklist checks "≤ 7".
- S9 allows at most one abstract sentence, and the abstract is exactly at S4's 330-word limit and C12.1's 26-numeral cap.

**Answers (verbatim):**
- "Add an 8th bullet". The ≤ 7 limit (S4; S10 checklist item 5) is raised to 8 by this ruling.
- "No numerals, trim to 330 (Recommended)". One abstract sentence with no numerals, with wording trimmed elsewhere so the abstract stays at ≤ 330 words; C12.1 is unchanged.

**Asked later in S9, 2026-09-29.** §5.2 and §5.3 must cite `ORIGINAL_SPECS.md` (the original's specifications, with page anchors) and `BASELINE_SPECS.md` (the baselines' deviations table, PLAN §1.2.5). Both are in `docs/presubmission/`, which the S5 ruling excludes from both bundles. Options put: ship those two files (recommended); copy them into `docs/`; keep them internal. **Answer (verbatim):** "Ship those two files (Recommended)". Both builders keep excluding `docs/presubmission/`, except `ORIGINAL_SPECS.md`, `BASELINE_SPECS.md` and `verify_original_specs.py`, the anchor checker.

## S10-fresh-terminal

Asked in chat at the start of S10 on 2026-09-29. PLAN's S10 says "Run this in a new terminal with nothing carried over from earlier sessions", and §1.3 says a compacted conversation should checkpoint and stop. The request "Start S10" came in the conversation that had just run S9 (whose §5.2/§5.3 text S10 reviews) and had been compacted once. Options put: a new terminal (recommended); or run it here, with the review done by fresh-context agents. **Answer (verbatim):** "Here, fresh agents review". S10 runs in this session. Its checklist review and table spot-checks are done by two agents given only PLAN's S10 text, Appendix E's checklist and file locations, within §1.3's two-subagent cap. This session verifies their findings, makes the small fixes and writes REVIEW.md.

## S10-review-blocked

S10 stops **BLOCKED** because PLAN's S10 item 4 says anything larger than a small fix stops the session with a list. The fresh-eyes review (`docs/presubmission/REVIEW.md`) confirmed 27 distinct issues; all are fixed in `040f336`, and none was a wrong number. The items below need you:

- **D1. The title against the conclusion.** The title, abstract and contribution 1 say the uncertainty "gets the order right". The conclusion says it "should be read as a weak ordering at best", and reports that the aleatoric head ranks error inversely at h = 368. Keep both, with the conclusion scoped to the per-dimension evidence? Or soften one of them?
- **D2. §3.2's summary table has no checkpoint column.** Its rows mix 10,000-iteration, 2,500-iteration and released-checkpoint results. Add a generated column, or accept that each row's section names its checkpoint?
- **D3. Figure 5's caption names neither arena nor n_independent.** Its artifact, `results/task2_sigma_profile.json`, records neither. Re-run or annotate its producer, or accept?
- **D4. §6.3's loss-term gradient table names no checkpoint or arena.** `results/e4_sigma_gradients.json` records neither. Same choice as D3.
- **D5. `tf_poor` is classed "no quantitative figure".** The original's Fig. 6 prints e for the whole N = 1 (teacher-forced) row. Reclassifying moves §4's count (five of six → four) and qualifies §4's "the first figure attached to the claim". Reclassify, or keep it with a stated reason?
- **D6. The old title in the package and a pushed zip.**
  - `docs/SUBMISSION_PACKAGE.md:54` still carries the old title.
  - The tracked, pushed `supplementary_anon.zip` (2026-09-27) holds the pre-S3 paper. Rebuild it with `scripts/make_anon_bundle.py --zip`, which rewrites a committed public file, and refresh the package doc?
- **D7. Length.** The body is 1.8% shorter than S0, against a 30% target. Accept as reported, or move whole analyses to the supplement?

**Answers (verbatim), 2026-09-29:**
- D1: "the conclusion should be scoped to the per-dimension evidence"
- D2: "add the checkpoint column"
- D3: "re-run/annotate the script and add"
- D4: "the same solution as D3"
- D5: "reclassify changes"
- D6: "rebuild with the new title."
- D7: "Accept as reported"

## S11-clean-clone-blocked

S11 stops **BLOCKED** under PLAN S11 item 5 ("On any failure: make no fixes"). A clean clone of the pushed `presubmission` (c3b7e9d) was rebuilt from scratch, as a reviewer following the README would rebuild it. Three things fail. The full account, with every figure's source, is in `docs/presubmission/FINAL_REPORT.md`; the logs are in the S11 evidence directory it names. What holds: 0 of the 364 differing regenerated values is a measurement, a statistic or a verdict. The verifier's three runs are byte-identical, the paper and PDF rebuild byte-identical, and the anonymity sweeps find 0 hits. PLAN routes the fixes to an Opus "S10-fix" session, then S11 again. Each item below gives a recommendation first.

- **B1. `pypdf` is missing from `requirements.txt`.**
  - Five scripts import it. A fresh venv therefore fails stage 28b1, `pdf_render_check.py` and `part_f_gate.py` (which crashes), and puts `submission_check.py`'s A1 at PENDING.
  - The same venv with `pypdf==6.16.1` added clears all four.
  - Recommended: pin `pypdf==6.16.1`, the project venv's version, in `requirements.txt`.
  - Optional: remove the hard-coded `/tmp/pdfvenv/lib/python3.14/site-packages` path at `scripts/submission_check.py:50`.
- **B2. `part_f_gate` check 6 fails, a new failure.** The published record fails check 4 alone.
  - The abstract prints `{{v1_shared_pct0}}` ("share 89% of their parameters", template line 18). No body sentence prints that key's value; the body prints 89.15% (`v1_shared_pct`).
  - (a) Recommended: print `{{v1_shared_pct}}` (89.15%) in the abstract, as the body does. This is one numeral for one numeral, and it leaves the word count unchanged.
  - (b) Or have the body state the rounded figure.
  - The gate must not be loosened (§1.2.8).
- **B3. The reproduction figures in the paper, BUILD_CHECKS, README, COVER_STATEMENT and SUBMISSION_CHECKLIST are C3's (c16267c).**
  - A clone of c3b7e9d measures 364 differing, not 365, and 0.59%, not 1.01%. 10 of the 17 `ver_*` keys differ, or 13 with `pypdf`.
  - Recommended:
    - after B1 and B2, restate by the restatement ordering: prose edits first, then a clean clone of the fixed commit, measured right after `reproduce.sh` with `pypdf` installed (49 files), then substitution and the document-line index;
    - refresh the hand-written copies from the same measurement;
    - leave `_BOOK` alone, because `.zip_bytes` differs only if the bundle is rebuilt before the verifier runs.
  - Two decisions are yours:
    - Which state to measure: the plan-timed state recommended above, or after the bundle build.
    - Whether the restatement may also reword §8's denominator. The 2026-09-27 ruling recorded the 1.01% denominator as known; fixing it now costs no extra loop, because the restatement reruns it anyway.
- **B4. Not blocking; recommended in the same fix session.** Several committed reports and gate records are stale against the pushed paper, and they ship in both bundles:
  - `typed_numerals_report.txt` says 686 typed numerals, against 711;
  - `appendix_g_rules_report.txt` says M-16 "SETTLED" and lacks M-74 to M-76;
  - `t1_bibliography_report.txt` counts 16 entries, against 18;
  - `results/part_f_gate.json` and `results/pdf_channels.json` say 48 pages.

  Regenerate them with `./reproduce.sh --quick --force --stage N`, then rebuild both bundles.
