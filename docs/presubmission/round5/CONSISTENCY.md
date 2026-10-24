# Round-5 consistency table (G16, 2026-10-24)

Every front-matter sentence that summarises a result, its body anchor, every reading that bears on it, and whether they
agree (rule 10). Readings are named in plain words; numbers live in `results/paper_numbers.json`. "X11" readings are in ledger M-104.

| Front-matter sentence | Body anchor | Every reading | Agrees? |
|---|---|---|---|
| Abstract: the rebuild matches the release's gradients | §3.1, App. A | gradient-level equivalence at every term and tensor | yes |
| Abstract and contribution 1: rollout training wins on every episode at the pre-registered horizon; loses at one step on short windows | §4.1 | fold replication, episode level 10 of 10 at h = 368 (8 of 10 at h = 8, so no "every horizon"); short-window gap at one step favours teacher forcing; episode-level sign at h = 1 is 6 of 10 (unresolved); held-out pair at 10,000 iterations 4 of 4 | yes: the abstract names the horizon, and "on short windows" |
| Abstract and contribution 4: disagreement ranks error better than the forecast step (Spearman) | §5.6 | Spearman lead resolved at every horizon from h = 8; at h = 1 the index is constant; Pearson verdicts agree in direction; fold arms at n = 20 lead at 4 of 4 horizons; held-out-pair rule at n = 4 inconclusive | yes, stated with the horizons |
| Abstract and contribution 2: in every ensemble measured, error exceeds what the spread implies even at one step | §5.2, Table 3 | R above one with interval for three ensembles; fold ensembles' error-to-spread ratio far above the calibrated value; independent fold members not measured at one step | yes: "measured" is the three R readings plus the fold ratio; unmeasured cells say so |
| Abstract and §1: the release feeds every member the ensemble mean, so the spread does not track accumulated error; per-member rollout raises coverage | §5.4 | released checkpoint, fold shared-trunk ensembles, fold independent ensembles all close a share of the log gap above one half; held-out pair at n = 4 descriptive; coverage rises but stays below the band | yes: "partly repairs", never "closes" |
| Abstract and contribution 3: the implemented loss is minimised at zero; collapse approached at Adam's ordinary step | §5.5, App. J | derivation; synthetic test; every logged run; the rate is Adam's; only the sign flip speaks to the objective | yes |
| Abstract, contribution 4 and §1: per-horizon rescaling restores one-sigma, not two-sigma coverage on the released checkpoint; mixed on unseen episodes | §5.7, App. M | nine-episode fit within band at every horizon; ±2σ below nominal; own multipliers on unseen episodes calibrate 17 of 36; fold cell-level reading does not restore (72 of 180); pooled fold coverage within band (alongside) | yes: every site scopes "on the released checkpoint" and gives the mixed reading |
| §1, §7, §8: measuring on training data | §5.2 | X10 at four held-out trajectories: worse at one step; X11a at twenty: mixed at one step, flatters at long horizons | yes: no site gives a fixed sign at one step |
| §1 and §6: two pipeline defects with fixes | §6 | stale action raises error up to h = 32 on all ten episodes, unresolved from h = 100; held-out pair raises it at every horizon; spliced windows do no measurable harm | yes: existence and fix, with the cost by horizon in §6 only |
| §7 lessons and limitations | §5, §6 | each lesson restates a direction in words; X5 not run with its reason; policy cost untested | yes |
| §8 conclusion and Table 4 | §4, §5 | Table 4 rows agree with §4.1–§4.3 and §5.2–§5.6; the collapse row rests on our runs, the synthetic test and the checkpoint's σ | yes |
| Locked framing: X3 in abstract and contribution 1 at headline prominence; X4 as a parameter-count test; X5 not run; X6 the 70-unit h = 100 result; X7 on the released checkpoint's released episodes; X8 and N5, N6 not summarised | §4.1, §4.3, §5.6, §5.7, App. D, E | as stated | yes |

## G16R additions (2026-10-24)

Rows G16's table did not have, or had as agreeing where a reading disagreed. Each is now fixed in the template.

| Front-matter sentence | Body anchor | Every reading | Agrees? |
|---|---|---|---|
| Contribution 4: ahead of the model's step size (was: only "the pre-registered linear test could not resolve") | §5.6, App. L | whole trajectories, h = 368: Pearson margin unresolved (pre-registered), Spearman margin resolved (exploratory); 70 shorter units, h = 100: resolved (X6, pre-registered) | **was no** (X6 omitted while the unresolved test was stated); now names both, X6 with its scope |
| Lesson 1: step size "ranks nearly as well on whole trajectories" | §5.6 | Spearman 0.91 against 0.60 on whole trajectories, margin resolved; Pearson margin unresolved; X6 resolved | **was no**; now "ahead on shorter units and under ranks; the linear whole-trajectory margin not resolved" |
| §8: the baselines "never beat even the training mean" | §4.3, Table 2 | at h = 368 none does; at h = 1–32 all six do; at h = 100 the rollout-trained MLP and transformer do | **was no** (unscoped); now "at h = 368" |
| Abstract, §1, §7, §8: rescaling restores one-sigma, "not two-sigma" | §5.7, App. M | ±2σ under the per-horizon multiplier 83.5–86.3% at every horizon, every interval below 95.45% | yes; the body printed h = 100 only, App. M now prints all six |
| §7 lesson: measuring on training data flatters at long horizons | §5.2 | X11a at h = 100 and h = 368 (0.65, 0.70, both intervals below one); X10 at both (0.72, 0.73) | yes |
| Abstract: Spearman +0.90 | §5.6 | released checkpoint, ten released episodes, h = 100 | yes; the abstract now names the horizon |
