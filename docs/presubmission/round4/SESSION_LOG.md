# Round-4 session log

One entry per session, in the template of PLAN.md §1.4. The start gate for each session is the last entry here.

## F0 — 2026-10-11 00:58 — Opus 5.5 (the plan assigns Sonnet 5.5, default effort) — status: BLOCKED
Commits:
18cc54f [F0][1] Round-4 plan, copied verbatim from the instruction file
e6e294b [F0][2] Round-4 files: session log, decisions (defaults accepted), out-of-scope list
a031531 [F0][3] Bundle exclusion dry-run: neither builder collects docs/presubmission/round4/
4fce5a1 [F0][4] Baselines: 20,745 main-text words, 62 pages (References p. 32), abstract 370/23, 59 labels in the main text; every gate passes
6b62f9c [F0][5] Preflight PF1-PF9: PF1 FAILS (no committed Arm B 2,500-iteration reference at h = 128 on §5's arena); the rest pass, PF4 records
17a36b0 [F0][4-fix] Baseline: list only files the build changed; name submission_check's outstanding C1 (ruling U5)
(the commit carrying this entry, the decision question and one out-of-scope line follows)
Done:
- **How this session ran.** On Opus 5.5 at the user's request ("please follow instructions as stated in PLAN4.md"); the plan assigns Sonnet 5.5. Both permitted Explore agents were used, read-only: a locator for PF4, PF6 and PF8, and an auditor of every F0 record. The workflow records both as running on Opus 5.5, not on the Sonnet 5.5 the launch command's `CLAUDE_CODE_SUBAGENT_MODEL` names; that variable did not reach workflow agents.
- **Item 1.** HEAD was `173f349` = `41b73ee` plus round-3 records only (`git diff --stat`: `round3/FINAL_REPORT.md` and `round3/SESSION_LOG.md`). The only untracked path was `round4/PLAN.md`, byte-identical to the instruction file. Tagged `pre-round4` (local, not pushed, as in rounds 1-3); branch `presubmission4`.
- **Item 2.** `SESSION_LOG.md`, `DECISIONS.md` (§0.2's table, defaults accepted), `OUT_OF_SCOPE.md`.
- **Item 3.** Neither bundle builder collects anything under `round4/` (`f0_bundle_exclusion.py`, which first asserts that its copy of `build_supplementary`'s loop is the one `main()` holds). The only `docs/presubmission/` files either collects are its three `SHIP_FROM_EXCLUDED` files.
- **Item 4.** `BASELINE_F0.md` (`f0_baseline.py`):
  - main text 20,745 words to "Data and code" and 21,230 to "References";
  - 62 pages, References on page 32;
  - abstract 370 words (cap 370) and 23 numerals (cap 26);
  - internal labels in the main text: M- 40, R- 6, S- 7, rule labels X1-X8 5, commit labels 1; B-, C-, D-, O- and X- none; none in the front matter;
  - 1,340 template keys, listed in `f0_template_keys.txt` for Annex 6 item 4;
  - every gate passes after one fast build; `submission_check` 21/22 with C1 outstanding by round 2's ruling U5, as known.
- **Item 5.** `PREFLIGHT.md` (`f0_preflight.py`): PF2, PF3, PF5, PF6, PF7, PF8 and PF9 PASS; PF4 recorded; **PF1 FAIL**.
  - PF1: every weight file PF1 lists is present (61 entries, 58 distinct files: the sweep's centre is Arm A's 2,500-iteration run). The released checkpoint matches `setup.sh`, and the 45 sweep and baseline files match their evaluation artifacts' SHA-256s. But no committed artifact holds Arm B's 2,500-iteration held-out relative-L1 at h = 128 on §5's four trajectories, which X3's named assertion needs. Question: `DECISIONS.md#F0-armB-2500-h128`.
  - For F1: the training driver takes no held-out argument. Each fold gives 4 independent trajectories (n = 20 pooled); {0, 2} and {3, 4} each hold two episodes from the same speed half. The matched baselines were ladder-verified teacher-forced only. M-23's three-seed bootstrap is inline, but `review_bootstrap_unit.boot_cluster` reproduces it, and it is Monte Carlo at n = 4.
  - For F2: velocity commands are not in the data, so the two tracking terms X5's gate requires have no recorded counterpart (PF4 records only; F2 decides). None of the three evaluators takes an offset, and the baselines assert offset 1.
- **Audit.** One read-only Explore agent audited `PREFLIGHT.md`, `BASELINE_F0.md` and the decision question. Verdict PASS-WITH-FIXES: seven findings, all applied (two wrong, two misleading, three imprecise); no check's result changed. It found the `step5_armB` run records (h = 128 on a different arena) and the stored per-trajectory rollouts, which now give option (B). The locator's one error, "thigh labels all 0" (one cell of 40,000 is 1), was caught by the generator, which reads the data.
- **Differences from the plan.** The main text was 20,745 words, not round 3's 20,771 (R7 reached 20,745). PF7's keys print in Appendix N (`PAPER.template.md:1842` and `:1866-1868`), not in §6.7. The penalty line is `lite/scripts/envs/base.py:166`, as the plan says.
Build/gates: pass (one fast build plus every gate, at `a031531` and again at `4fce5a1`; the build changed only `PAPER.pdf`'s timestamps, restored). No paper text edited, so no second build was required.
Paper numbers changed: none
New keys: none
Re-anchored checks: none
CPU jobs over 1 min: the baseline (fast build plus all gates), twice, about 3 min each; the locator agent, about 5 min; the audit agent, about 13 min. No training job ran, so none was contended.
Queue status: not launched
Body words (round2/t6_words.py): 20,745 (F0: 20,745)
Abstract words / numerals (C12.1): 370 / 23
Next: the user rules on `DECISIONS.md#F0-armB-2500-h128`; then F0 records the ruling, re-runs `f0_preflight.py` and writes COMPLETE; then F1 (Opus 5.5, high effort, fresh terminal, idle machine for its timing probes).
Decisions for user: DECISIONS.md#F0-armB-2500-h128
