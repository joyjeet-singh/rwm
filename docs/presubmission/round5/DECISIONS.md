# Round-5 decisions

## G0-rulings

Defaults accepted by launching G0, 2026-10-19 (no edits to PLAN §0.3's table before launch).

| # | Question | Default |
|---|---|---|
| Y1 | Length | **Main content, from the title to the last line before References, at most 12 pages** in the official TMLR template, which is TMLR's two-week review track. If that cannot be met without a result leaving the record, stop at 15 and record why ("Long submission"). Replaces W6. |
| Y2 | Abstract | **About 200 words (check: at most 210) and at most 5 numerals**, no capitalised verdict labels, readable by an ML researcher outside model-based RL. Tighten C12.1 accordingly. Replaces W7. |
| Y3 | Internal labels | **None in the main text**: no ledger or rule IDs, no commit labels, no capitalised verdict labels, no "entry-res"-style variable names. The pre-registration appendix (App. E) maps plain names to IDs and gives every verdict verbatim; other appendices may name a rule by ID; ledger IDs and commit labels appear only in App. E and in `docs/`. Replaces W8. |
| Y4 | Where text that leaves the PDF goes | **Into `docs/SUPPLEMENT.md`**, generated from `docs/SUPPLEMENT.template.md` with the same `{{key}}` machinery and shipped in the anonymised ZIP, or, for drafting history, `docs/BUILD_CHECKS.md`. A key-coverage gate proves that nothing leaves the record. Replaces round 4's rule 10 destination ("an appendix"). |
| Y5 | New computation | **(B), recommended: the inference-only analyses (X9, X10, N7–N14) plus the fold replications X11**: 12 ensemble-5 runs and 8 single-model runs at 2,500 iterations on X3's four new folds, about 25 CPU-hours in the background, cap 30, re-probed in GT1. It amends the 16 Oct "no new training" ruling for these runs only. (A): inference-only; the held-out ensemble-5 numbers stay at n = 4 with exact tests, and the independent-ensemble number moves to n = 20 through X9(d). (C): (B) plus M-68 and M-49 on the folds, about 50 CPU-hours, cap 55. |
| Y6 | §5.2 and §5.3 | **No training.** §5.2 becomes one paragraph ("at small budgets, shorter histories learn faster"; the original's trade-off with training time is not tested). §5.3 says "consistent with the claim, but a weak test" and adds the floors. Alternative: train §5.2's runs to a validation plateau and sweep three learning rates per baseline, under a new pre-registration (budget to be probed). |
| Y7 | "Too small by" | **The coverage-matching factor**, the multiplier on σ that restores 68.27% ±1σ coverage, is the only quantity called "too small by ×k". ρ is reported as the error-to-spread ratio beside its calibrated value of 0.80. Alternative: mean-matching, ρ/0.80. |
| Y8 | Ranking statistic | **Spearman is the headline statistic for every ranking statement**, with Kendall in the appendix; each pre-registered verdict keeps the Pearson statistic it was committed with, and says so. Alternative: Pearson first, rank statistics as a sensitivity. |
| Y9 | Title | **Decided at G8 from the readings.** The leading candidate drops "Verified" and names the scope: "Right Order, Wrong Size: Reproducing the Robotic World Model's Dynamics Model and Testing the Uncertainty It Reports". |
| Y10 | Upstream report of the action misalignment | **You send the alignment report** (`docs/presubmission/AUTHOR_QUERY_ALIGNMENT.md`) through the existing correspondence before G14, and the paper states the date and any reply. If you prefer not to, the paper says it was not reported before submission. |
| Y11 | Competing interests | **Declare it on the OpenReview form**: one author corresponded with the first author of the reproduced papers, who therefore knows that author's identity. G17 drafts the text; you paste it. |
| Y12 | Round 4's own steps | **None of round 4's §0.4 steps now** (merge and push, Hugging Face re-upload, archive). They move to after G18. Round 4's `PAPER.pdf` and `supplementary_anon.zip` are superseded: do not upload them. |
| Y13 | How sessions run | **One fresh terminal per session through `round5/go.zsh`**, with the model and effort §0.4 gives; subagents only where a session's section names them. G0 replaces the "Finishing round 4" section of `PDM/CLAUDE.md` with Annex 5's round-5 block (the old text is kept in `round5/`). |

## GT1-cap

**User ruling, 2026-10-19 (chat):** "Start GT1. Raise the 30 CPU-hour cap if needed". This amends Y5 (B)'s cap of 30
CPU-hours for X11's queue only; the runs stay the 20 that Y5 (B) names (12 ensemble-5, 8 single-model). GT1 sets the
new cap from its idle-machine probe, as 1.10 × the probe's projection rounded up to the next whole hour, records both
numbers here before launch, and still stops `BLOCKED` if the re-probed projection exceeds that cap. Prior estimate from
the stored run records (not a probe): ensemble-5 at 2,500 iterations took 14,241–15,980 s each
(`results/step5_armA_seed{0,1,2}_ens5.json` `wall_clock_s`), and an X3 single-model run about 3,400 s
(`results/x3_run_armA_ho02_seed0.json`), so about 55–60 CPU-hours for the 20 runs. Also: GT1 runs in the same
conversation as G2, at the user's request, not in a fresh terminal (Y13).

**Set by GT1's probe, 2026-10-19, before launch** (`results/round5_queue_timing.json`): projected **55.5 CPU-hours** for
the 20 runs (`projected_total_h`; per run, `per_run.e5.projected_h` and `per_run.single.projected_h`), so the cap is
**62 CPU-hours** (`cap_h`: 1.10 × 55.5 = 61.0, rounded up). The probe ran with nothing else running (the 1-minute load
average still carried the dry runs that had just ended), on mains power. Today's ensemble-5 probe ran faster than the
finished runs' logged rate (`per_run.e5.probe_over_finished`), so no upward scaling applied. A re-probe is checked
with `scripts/round5_queue_timing.py --cap 62`.

## G3-assert-ii

**User ruling, 2026-10-19 (chat), on G3's first `--assert-only` of `scripts/x9_per_member_propagation.py`:** "Fix and
re-assert". X9's assertion (ii), that MEAN and PER-MEMBER agree exactly (0.0) at forecast step 1, failed by 6.4e-7.
Cause, located on step-1 values only: every head's output and the across-member spread were bitwise identical; the
members' mean ȳ differed by one float32 last-place unit (5.96e-8) because the script averaged the members over the whole
(member, trajectory, time, dimension) array, where MEAN averages a (member, trajectory, dimension) stack at each step,
and PyTorch reduces the two shapes in a different order. No per-member result had been computed. The fix computes ȳ, the
spread and the members' σ at each step from `torch.stack` of that step's member predictions, MEAN's own operation
(`r2_independent_ensemble.py:100-104`; `score_reference.py:99,121`), as PROTOCOLS §2.2 already requires ("MEAN's batch
shapes so that float32 rounding matches"). The tolerance stays 0.0. The script was not yet pre-registered.

*Second instance, same cause, same ruling (2026-10-19).* After the fix, ȳ, the error and the spread were bitwise identical
at step 1, but the CRPS and NLL means differed by 2.8e-17 and 2.2e-16 (assertion (ii) reported 7.1e-15). The per-member
spread array inherited the input tensor's non-contiguous memory layout and MEAN's did not, so numpy summed them in a
different order. `cell()` now reduces C-contiguous copies. The tolerance stays 0.0.

## G4-n7-a1

**User ruling, 2026-10-19 (chat), on N7's first run:** "Use a1's float32 mean". N7's reproduction assertion (item 1) failed:
`results/a1_ab_by_horizon.json`'s stored `gap` differed from the mean of its stored `gap_per_trajectory` by 3.0e-8 against
PROTOCOLS' 1e-12. Cause: a1 averages a float32 array (`scripts/a1_ab_by_horizon.py:156,170`); N7 averaged the same stored
values in float64. Every other N7 assertion passed and no N7 test had been computed (the run stopped with a `.blocked`
record, kept at `/Users/Shared/rwm_verify/evidence/R5G4/`). The fix computes the point as a1 does, the float32 mean of
the stored list; the tolerance stays 1e-12; the interval check is unchanged (`boot_cluster`, 1e-7).

## G4-n10-pooled

**User ruling, 2026-10-19 (chat), before any N10 scoring:** "Mean of per-fold pooled". PROTOCOLS §5 N10 asks for nRMSE in
the pooled convention on X3's five-fold arena, where each fold has its own training scale, so one pooled value over the 20
trajectories is undefined. N10 pools within each fold with that fold's scale and averages the five fold values with equal
weight (each fold has 4 trajectories), labelled as such; the per-trajectory convention is reported as specified.

## G4-n10-floorcheck

*Recorded, not a user ruling (2026-10-19).* N10's first scoring run stopped on a check that is not in PROTOCOLS but was added
by G4: that the script's hold-last forecast equals `mn_sweep_eval.floor` exactly. Every PROTOCOLS assertion passed (stored
floors within 6.0e-8 of 1e-6; scale exact); no N10 number was written or printed. Cause: `MN.floor` subtracts in float32
and the check had cast to float64 first. The check now compares like with like (the float32 difference through
`MN.metrics`) and stays exact, the same treatment as rulings G3-assert-ii and G4-n7-a1. The `.blocked` record is kept at
`/Users/Shared/rwm_verify/evidence/R5G4/`.

## G4-n13-ckpt

**User ruling, 2026-10-19 (chat), on N13's first run:** "Assert vs C-10, log defect". N13's assertion that the checkpoint's
mean `state_log_delta_logstd` equals the project constant −14.4629 within 5e-5 failed: the checkpoint holds −14.463197 (all
225 entries in [−14.46361, −14.46255]). The constant is a typed number with no derivation, first typed in `84ff01b`
(`scripts/step5_train.py`) and copied into `scripts/step6_analyse.py:38` and `scripts/step6_3_min_logstd.py:32`; it is off
by 3.0e-4 (0.002%). N13 now asserts the value read from the checkpoint against ledger C-10's recorded −14.463 at C-10's own
precision (|difference| < 5e-4), records the typed-constant defect in its artifact and ledger entry, and logs it in
OUT_OF_SCOPE. N13's reachability uses the value read from the checkpoint, as PROTOCOLS specified. No N13 reading had been
written (the `.blocked` record is at `/Users/Shared/rwm_verify/evidence/R5G4/`).

## G8-outline

**Approval needed before G9 starts** (PLAN §1.4). `round5/OUTLINE.md` is the plan G9–G15 build to. Approve it as it
stands, or name the changes. Four things in it are choices rather than consequences of the rulings:

1. **The plan.** 11.5 pages of main content (half a page of margin under Y1); §5 in G13's order, leading with the
   one-step gap; three figures and three tables, Figure 1 being two findings (the base claim held out episode by
   episode; whether the spread accumulates); appendices A–O at about 12,000 words. **No broader-impact statement:**
   TMLR asks for one only where there is a significant risk of harm, and §10's text moves to the supplement.
2. **The released checkpoint's scope words.** Rule 11 locks X7 as coverage "on a checkpoint that trained on all ten
   episodes". N12 found that nothing in the release records which rows trained it. The outline writes "the released
   checkpoint, on its ten released episodes" and states N12's sentence once in §3.2. The finding is unchanged; only
   the words "trained on" go. Approving the outline approves this change to the locked wording.
3. **The title.** Recommended: *Right Ranking, Wrong Scale: Reproducing the Robotic World Model's Dynamics Model and
   Testing the Uncertainty of Its Follow-up*. The referee read "order" as "order of magnitude". The alternative keeps
   *Right Order, Wrong Size:* with the same subtitle.
4. **G9's migration list**, in particular item 13: the "what §x keeps" and "stood there as follows" framings go to
   BUILD_CHECKS, while the evidence they introduce stays in the appendices for G15.

The abstract draft (210 words, 5 numerals) and the four contributions (at most 45 words each) are in §abstract and
§contributions; G11 starts from them and rechecks them against the readings (rule 10), including GT2's.

**Status: APPROVED.** User ruling, 2026-10-19 (chat): "I approve all 4 recommendations. Continue". So: (1) the plan as
written, with no broader-impact statement; (2) "the released checkpoint, on its ten released episodes" replaces rule
11's "trained on all ten episodes" for X7 and every released-checkpoint scope sentence; (3) the title *Right Ranking,
Wrong Scale: Reproducing the Robotic World Model's Dynamics Model and Testing the Uncertainty of Its Follow-up*;
(4) G9's migration list, item 13 included.

## G16R-ruling
**Start gate overridden by the user** (PLAN §1.4 would have G18 next, after G17 COMPLETE). User ruling, 2026-10-24
(chat), quoted: "Run an independent fresh-eyes review in a new terminal before G18, including fixing the log
timestamps and deciding Figure 3." So session G16R runs between G17 and G18 in a new terminal, by a session that wrote
none of G11–G17 and treats their checks as unverified. Its items: (1) G16's review again from scratch (G16's
subagents, at most three; the appendix parts `REVIEW.md` lists as unchecked and the `xref_sweep` suspects G17 found go
first; every gate's printed output read, not only its exit status); (2) every round-5 `SESSION_LOG.md` header time
checked against `git log` and each wrong one set to the commit time of that session's last commit, with a dated
correction note; (3) Figure 3 decided (`#G16R-figure3`); (4) the close of §1.4. If the paper, the supplement, the
figures or a bundled file changes, G17's steps 3–5 run again before G18; G16R does not run them.

## G16R-figure3
**Figure 3 (±1σ and ±2σ coverage by horizon on the released checkpoint, OUTLINE §figures) is dropped from OUTLINE.**
Decided by G16R under the user's test: draw it only if it fits within the 12-page limit, no result leaves the record, and
it adds evidence a reviewer needs.
- **Limit.** OUTLINE homes it in §5.7, in the main text. Main content is 11.67 of 12 pages; a two-panel figure with its
  caption takes about a third of a page, and a float that size at the end of §5 would push the main text past 12 or
  force cuts. It does not fit where it was planned.
- **Evidence.** What it would show is now all printed, as numbers with intervals. ±1σ by horizon under no multiplier,
  one constant and per-horizon multipliers is Appendix M's X7 table. ±2σ by horizon was the real gap: the paper printed
  it at h = 100 only, although the abstract, §1, §7 and §8 say "not two-sigma" without a horizon. G16R added it to
  Appendix M as a table (N9, post hoc, read from keys; `n9_recalibration_scores.json` reproduces X7's ±1σ cells
  exactly). Every horizon agrees: 83.5–86.3%, every interval below 95.45%. Figure 1b already shows what no constant can
  absorb, the error-to-spread ratio growing with the horizon.
- **Moved to an appendix instead** it would fit and lose nothing, but it would add only a picture of the two tables,
  renumber Appendix N's Figure 8 and change the placement code after the freeze, for no evidence a table does not give.
- **Record.** Nothing leaves it: the figure was never drawn, and its data are in the two tables and the ledger (R-83).

## G16R-blocked
**Question for the user: how should the stale appendix pointers be fixed before G17's steps 3–5 and G18?**
G16R found about twenty sentences in Appendices D and H–M that describe body content by the earlier paper's structure:
the section they name now holds no such table, column, figure or number (for example "§5.2's released-checkpoint
table", "§5.6's P column", "§5.3's table", "§5.2's 'our arms fail the same way at 10.5×'", and "the abstract and §8 use
33.4× at h = 100", which neither has done since RV14). The full list, by `PAPER.template.md` line, is in `REVIEW.md`
(G16R, "Open"). None is a measurement or a verdict, and every gate passes: they are false descriptions of the paper's own
structure, which a reviewer reading the appendices would meet. G16's rule allows a review to fix items of up to three
sentences; this class is larger and most of it needs sentences rewritten (pointing at the appendix's own table, or
dropped), so G16R stopped.
Options: **(A, recommended)** a fix session ("G15-fix", Opus) that rewrites each listed sentence from the template, with
the same build-gates-build close, then G17's steps 3–5, then G18; **(B)** accept them as known and record them in
`SUBMISSION_PACKAGE.md`'s open items; **(C)** have G16R resume and fix them under an explicit waiver of the
three-sentence rule.

**Status: RULED A.** User ruling, 2026-10-24 (chat), quoted: "Option A - a fix session rewrites them". So a session
**G15-fix** (Opus 5.5, high, new terminal) runs next, from this brief. PLAN.md has no section for it, and `go.zsh` does
not know the name, so the user starts it with the prompt in `CHECKPOINT.md`.

**G15-fix brief.** Reads: PLAN §1; this anchor; `REVIEW.md`'s G16R section ("Open" and "Coverage"); `CHECKPOINT.md`.
Subagents: `rwm-checker` once at most, for item 3.
1. For each sentence on G16R's list (`PAPER.template.md` lines 332, 636, 649, 651, 724, 737, 750, 754, 767, 785, 811,
   829, 995, 1000, 1114, 1191, 1265, 1293, 1343 at commit `07a7770`; locate them by their quoted text, since lines
   move), read the body section it names. Rewrite the sentence so that it points to where the content now lives (usually
   the appendix's own table or figure), or drop the pointer clause. Never change a number, a key, a verdict or a scope.
   Line 785's "the abstract and §8 use 33.4× at h = 100" goes. Edit sources only: the template, or the generator that
   writes a caption or a table label.
2. G16R's list came from a pattern search, so it may be incomplete. Check every `§n` and `§n.n` reference in Appendices
   A–O (about 230) against what the named body section now holds. Fix any further stale ones the same way. Leave the
   supplement's earlier-paper passages alone (they say their numbering is the earlier paper's).
3. Close as PLAN §1.4: regenerate the claims audit (ruling U5), then fast build, gates (read the printed output, not the
   exit status), fast build again, byte-identical. Restore `PAPER.pdf` if only its date changed. One commit per item,
   subject `[G15-fix][n]`; log entry and checkpoint. The page and abstract gates must still pass; nothing leaves the
   record. Any change bigger than a pointer rewrite (a number, a reading, a moved result) is `BLOCKED`.
Next after G15-fix: G17's steps 3–5 only (clean clones and restatement, bundles and sweep, package documents), then G18.
**Done by G15-fix** (2026-10-24): `fc8e2e9` (item 1), `1b8c289` (item 2, 60 further pointers and two in the evidence-table
generator), `c39e6b3` (close); `REVIEW.md`, G15-fix. Nothing BLOCKED. G17's steps 3–5, then G18, are next.
