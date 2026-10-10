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

