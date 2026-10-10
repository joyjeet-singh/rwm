# Round-4 decisions

## F0-rulings

PLAN.md §0.2, copied verbatim. **Defaults accepted by launching F0, 2026-10-11**: the user asked for the plan to be carried out as written ("please follow instructions as stated in PLAN4.md") and edited no line; `PLAN.md` here is byte-identical to the instruction file (SHA-256 compared before the first commit).

| # | Question | Default |
|---|---|---|
| W1 | X3, retraining with each episode held out in turn. | **Run it with 3 seeds per arm per fold, at 2,500 iterations** (about 18 CPU-hours). The alternatives are 1 seed (about 6 h) or skipping it. |
| W2 | X4, size-matched baselines. | **Autoregressive MLP and transformer only, 3 seeds** (about 8 h, cap 10). The teacher-forced baselines are 15–145× worse, so matching their size cannot change their sign. The size-matched RSSM is not run (§5.3 already calls the RSSM comparison uninformative). |
| W3 | X5, does the penalty cover the error in predicted reward? | **Run it if F2 finds the reward computable from the recorded data**; otherwise record why not and move on. |
| W4 | X6, X7, X8 (inference only). | **Run all three.** |
| W5 | Item 5, the difficulty measure. | **Recompute with the correct (causal) timing.** Stop with `BLOCKED` if any verdict, or the direction of any reported correlation, changes. |
| W6 | Main-text length. | **At most 16,000 words, aiming for 15,000**, by moving text and never deleting it. The alternative is to stop at round 3's 20,771. |
| W7 | Abstract. | **At most 300 words.** Tighten the abstract cap in `submission_check` C12.1 from 370 to 320 (tightening a check is allowed). |
| W8 | Internal labels in the main text. | **Remove ledger IDs (R-, S-, D-, C-, B- and commit labels) from the main text**; keep a rule's ID (M-xx, X-n) once per section where its verdict is reported. The appendices keep everything. |
| W9 | Training on fewer episodes, to show how the main result changes with the amount of data. | **No.** It can only show the trend towards less data, not more, and it costs 3–6 h. |
| W10 | The total cap on training time. | **32 CPU-hours.** A projection above it means `BLOCKED`. |
| W11 | If X3 does not replicate the headline (NOT RESOLVED or REVERSES). | **Say so in the abstract and contribution 2**, at the same prominence as the headline. |
| W12 | When to re-upload the model card to Hugging Face. | **Right after F4**, because the live card shows figures round 3 found were produced by a scoring bug. Then again after F12. |


## F0-armB-2500-h128

**Raised by F0, 2026-10-11. Needed before F1.** Evidence: `PREFLIGHT.md` PF1, "Arm B's 2,500-iteration held-out relative-L1, at every horizon". The finding and the options below were checked by a read-only audit agent, and reworded where it found them imprecise.

**What F0 found.** Annex 2 X3 names this assertion (PLAN.md, X3, "Assertions"): fold {1, 8}'s readings reproduce "the committed 2,500-iteration held-out relative-L1 for Arm A (`mn_compute_matched.json` 2,500 block) and Arm B (PF1's artifact) at every horizon, to 1e-6". Arm A is covered at all six horizons. For Arm B on §5's four non-overlapping held-out trajectories, no committed artifact covers all six:
- `results/head_to_head_accuracy.json` (`rows.armB`) has h = 1, 8, 100 and 368, as each seed's mean and the three-seed mean;
- `results/action_sensitivity.json` (`per_seed[...].I0_per_trajectory_err`) has h = 1, 8, 32 and 100, per trajectory and seed;
- the two agree where both exist, and both use the statistic of `mn_compute_matched.json` (PREFLIGHT PF1 gives the agreement);
- **h = 128 is in neither.** `results/step5_armB_seed<s>.json` do hold Arm B at h = 128, but on Protocol A's 10 randomly drawn, overlapping trajectories, a different arena that gives different numbers. Everything else a scan finds at h = 128 for Arm B is a coverage, calibration or permutation figure.

The assertion cannot be run as written at h = 128, so F1 would have to stop `BLOCKED` on it (§1.4, "an assertion this plan names fails"), after its idle-machine timing probes. That is why F0 asks now.

**Options.**
- **(A) Amend X3's named assertion.** Narrow it to the horizons the committed artifacts share for Arm B (h = 1, 8, 32, 100 and 368), which is §1.2 rule 6's minimum ("on the cases they share"). Arm A stays at all six. This narrows an assertion the plan names, so it is an amendment: X3's pre-registration entry would carry the narrowed assertion verbatim and name h = 128 as unasserted for Arm B. It costs nothing. What it gives up: a defect touching only Arm B's h = 128 column would not be caught.
- **(B) Make the missing reference from the stored rollouts (recommended).** The rollouts behind `head_to_head_accuracy.json` hold all 368 forecast steps for Arm B's three seeds on exactly §5's four trajectories: `cache/armB_teacher_forced_seed<s>__out-of-sample_held-out_pair__u400.npz`, git-ignored, whose SHA-256s equal those `head_to_head_accuracy.json` records. Before X3's pre-registration, F1 adds a horizons argument to `scripts/head_to_head_accuracy.py` and asserts that its default reproduces today's artifact byte-identically. F1 then writes a separate six-horizon Arm B reference artifact from the same caches, asserting it equals the existing artifact at h = 1, 8, 100 and 368 and `action_sensitivity.json` at h = 32. X3 then asserts at every horizon, as written. No rollout and seconds of CPU; the reference comes through a code path independent of X3's (stored rollouts that `gate_per_triple.py` verifies). It costs one small artifact, and F9 gives it a `reproduce.sh` stage marked like `head_to_head_accuracy.py`'s. F1 must not just widen `HORIZONS` in place: its leader lists would gain horizons, and `scripts/paper_numbers.py:2163` binds the paper key `h2h_released_sweeps_at` from one of them (`released_leads_both_metrics_at`), which the paper prints (`PAPER.template.md:446` and `:1790`).
- **(C) Make the missing reference with a fresh rollout.** As (B), but F1 scores Arm B's committed 2,500-iteration weights on {1, 8} through `scripts/mn_sweep_eval.py`'s `score`, the path `mn_compute_matched.json` used for Arm A. A few CPU-minutes on an idle machine, before the queue launches.
- **(D) Something else.**

F0 is otherwise complete: every other check passes or records as designed. When the ruling is in, F0 records it here, re-runs `f0_preflight.py` and writes its `COMPLETE` entry.

**Ruling, 2026-10-11: (B).** Asked in chat; the user chose "Stored rollouts (Recommended)". So F1, before X3's pre-registration:
1. adds a horizons argument to `scripts/head_to_head_accuracy.py` and asserts that its default reproduces `results/head_to_head_accuracy.json` byte-identically;
2. writes a separate six-horizon reference artifact for Arm B at 2,500 iterations on §5's four held-out trajectories, from the same stored rollouts. It asserts that artifact equal to `head_to_head_accuracy.json` at h = 1, 8, 100 and 368, and to `action_sensitivity.json` at h = 32, before writing it;
3. names that artifact as "PF1's artifact" in X3's assertion, which then runs at every horizon, as Annex 2 words it.

The stored rollouts are git-ignored, so F9 gives the new stage the same `NEEDS_WEIGHTS` marking as `head_to_head_accuracy.py`'s. F0 re-ran `f0_preflight.py` after this ruling; PF1 passes on it.
