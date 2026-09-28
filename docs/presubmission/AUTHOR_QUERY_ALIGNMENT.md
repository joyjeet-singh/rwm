# Author query — action alignment (DRAFT, NOT SENT)

Filled in by S3 from PLAN Appendix D, by `docs/presubmission/s3_write_author_query.py`, which
typed none of it. **The user sends it; nothing here has been sent.** No paper sentence says the
author was asked or confirmed, and none may until a reply exists.

> Subject: RWM-U release — action alignment in the evaluation script
>
> Dear [first author],
>
> Thank you again for your help in August with Eq. 4 and the aleatoric term. We have one more question, about the lite release at commit 13a798e9 (with rsl_rl_rwm at 18eebcdd).
>
> In training (`rsl_rl/modules/system_dynamics.py:195-200`), the state at step t+1 is paired with the action in the same row. In evaluation (`scripts/model_training.py:127-132`), it is paired with the action one row earlier. Our reading of the dataset is that row t holds the action that produced state t. At all ten episode resets the twelve actions are exactly zero, which a policy network with biases would not output. Under that reading the training pairing is the intended one, and the evaluation pairing is one step stale. On four non-overlapping 400-step trajectories, the released checkpoint's error over a 368-step horizon is 6.6% [1.0, 8.0] higher in nRMSE and 7.9% [3.1, 13.0] higher in relative-L1 under the evaluation pairing than under the training pairing (95% intervals from a bootstrap over whole trajectories). Across twenty such trajectories drawn from all ten episodes the difference reverses sign (−2.1% and −4.6%, both intervals spanning zero), so we read the cost in error as small. Our question is about the alignment itself.
>
> Could you confirm which pairing is intended? And, as with the earlier exchange, may we quote your reply?
>
> Best regards,
> [name]

## Where each filled value comes from

| Placeholder | Filled with | Source |
|---|---|---|
| [pinned hash] | lite `13a798e9d35dabf12c0e6e02977b25ec64dfb2bd`, rsl_rl_rwm `18eebcdd7145284c8d5eed5d8ed1a4b96c649693` | `git rev-parse HEAD` in each upstream checkout, asserted equal to the pins in the project's working rules |
| [file:line], training | `rsl_rl_rwm/rsl_rl/modules/system_dynamics.py:195-200` | :181 takes states from rows 0..H−1, :200 actions from rows 1..H, and the target is row H. The recurrent branch (:196, after the first step) takes the target's own row. |
| [file:line], evaluation | `robotic_world_model_lite/scripts/model_training.py:127-132` | :131-132 slice states and actions over the same rows i−H..i−1 to predict row i. The recurrent branch (:128-129, after the first step) takes row i−1 for both. |
| "all ten episode resets" | rows 999 … 9,999 | `results/step0_regimes.json` `window_accounting.reset_rows`; every action at those rows re-checked as exactly zero against the data |
| [X], nRMSE | 6.6% [1.0, 8.0] | `results/alignment_defect_ci.json` `arenas.held_out_n4`, nRMSE form 1 (§3.1's primary) |
| [Y], relative-L1 | 7.9% [3.1, 13.0] | the same, `rel_l1` |
| the reversal | −2.1%, −4.6% | the same, `arenas.all_ten_n20` |

**Changed from Appendix D's wording, and why:**
- **"[X]% lower" is now "[X]% higher under the evaluation pairing".** The paper's figure is
  err(evaluation pairing) / err(training pairing) − 1. Written as "lower", the same number would
  be a different quantity.
- **The ten-episode reversal is added.** The user's ruling (`DECISIONS_FOR_USER.md#S3-alignment-defect`)
  restates the defect on independent trajectories. The reversal is part of what those show, and
  a letter quoting only the positive arena would overstate the cost.
- **Appendix D's single [pinned hash] names both repositories**, because the training line
  is in rsl_rl_rwm and the evaluation line is in lite.
- **Every arena is in-sample for the released checkpoint.** It trained on every episode. The
  letter says "trajectories", not "held-out".

[first author] and [name] stay placeholders. The first author's name is on the anonymity
deny-list, and the user fills it in on sending.
