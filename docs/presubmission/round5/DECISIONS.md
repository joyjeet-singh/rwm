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
