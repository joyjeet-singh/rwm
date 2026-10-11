# Round-4 run queue — rules X3 (ledger M-86) and X4 (ledger M-87)

Launched by F1 on 2026-10-11 at 10:36:10 (+0530), from the repository root, with the plan's command:

```
nohup caffeinate -i scripts/queue_runner.sh runs/queue_round4.txt > runs/queue_round4.log 2>&1 &
```

`runs/` is gitignored, so this file is the committed record of what the queue holds. The queue file was written from the
committed record by `scripts/round4_queue_timing.py --queue-from-record` (`results/round4_queue_timing.json`), after the
pre-registration commit of both rules. One run at a time (8 GB of RAM).

**The runs**, in queue order: X3 seed 0, X4 seed 0, X3 seed 1, X4 seed 1, X3 seed 2, X4 seed 2. 24 X3 runs
(`scripts/step5_train.py --holdout`) and 6 X4 runs (`scripts/train_baseline.py --spec matched --regime ar`),
2,500 iterations each.

| id | rule | run | seed | projected hours | projected finish (+0530) |
|---|---|---|---:|---:|---|
| `x3_A_02_s0` | X3 | Arm A, held out {0, 2} | 0 | 1.01 | 2026-10-11 11:37 |
| `x3_B_02_s0` | X3 | Arm B, held out {0, 2} | 0 | 0.97 | 2026-10-11 12:35 |
| `x3_A_34_s0` | X3 | Arm A, held out {3, 4} | 0 | 1.01 | 2026-10-11 13:36 |
| `x3_B_34_s0` | X3 | Arm B, held out {3, 4} | 0 | 0.97 | 2026-10-11 14:34 |
| `x3_A_56_s0` | X3 | Arm A, held out {5, 6} | 0 | 1.01 | 2026-10-11 15:35 |
| `x3_B_56_s0` | X3 | Arm B, held out {5, 6} | 0 | 0.97 | 2026-10-11 16:33 |
| `x3_A_79_s0` | X3 | Arm A, held out {7, 9} | 0 | 1.01 | 2026-10-11 17:34 |
| `x3_B_79_s0` | X3 | Arm B, held out {7, 9} | 0 | 0.97 | 2026-10-11 18:32 |
| `x4_mlp_s0` | X4 | matched mlp, autoregressive | 0 | 0.08 | 2026-10-11 18:37 |
| `x4_transformer_s0` | X4 | matched transformer, autoregressive | 0 | 2.18 | 2026-10-11 20:47 |
| `x3_A_02_s1` | X3 | Arm A, held out {0, 2} | 1 | 1.01 | 2026-10-11 21:48 |
| `x3_B_02_s1` | X3 | Arm B, held out {0, 2} | 1 | 0.97 | 2026-10-11 22:46 |
| `x3_A_34_s1` | X3 | Arm A, held out {3, 4} | 1 | 1.01 | 2026-10-11 23:47 |
| `x3_B_34_s1` | X3 | Arm B, held out {3, 4} | 1 | 0.97 | 2026-10-12 00:46 |
| `x3_A_56_s1` | X3 | Arm A, held out {5, 6} | 1 | 1.01 | 2026-10-12 01:46 |
| `x3_B_56_s1` | X3 | Arm B, held out {5, 6} | 1 | 0.97 | 2026-10-12 02:45 |
| `x3_A_79_s1` | X3 | Arm A, held out {7, 9} | 1 | 1.01 | 2026-10-12 03:45 |
| `x3_B_79_s1` | X3 | Arm B, held out {7, 9} | 1 | 0.97 | 2026-10-12 04:44 |
| `x4_mlp_s1` | X4 | matched mlp, autoregressive | 1 | 0.08 | 2026-10-12 04:48 |
| `x4_transformer_s1` | X4 | matched transformer, autoregressive | 1 | 2.18 | 2026-10-12 06:59 |
| `x3_A_02_s2` | X3 | Arm A, held out {0, 2} | 2 | 1.01 | 2026-10-12 08:00 |
| `x3_B_02_s2` | X3 | Arm B, held out {0, 2} | 2 | 0.97 | 2026-10-12 08:58 |
| `x3_A_34_s2` | X3 | Arm A, held out {3, 4} | 2 | 1.01 | 2026-10-12 09:59 |
| `x3_B_34_s2` | X3 | Arm B, held out {3, 4} | 2 | 0.97 | 2026-10-12 10:57 |
| `x3_A_56_s2` | X3 | Arm A, held out {5, 6} | 2 | 1.01 | 2026-10-12 11:58 |
| `x3_B_56_s2` | X3 | Arm B, held out {5, 6} | 2 | 0.97 | 2026-10-12 12:56 |
| `x3_A_79_s2` | X3 | Arm A, held out {7, 9} | 2 | 1.01 | 2026-10-12 13:57 |
| `x3_B_79_s2` | X3 | Arm B, held out {7, 9} | 2 | 0.97 | 2026-10-12 14:55 |
| `x4_mlp_s2` | X4 | matched mlp, autoregressive | 2 | 0.08 | 2026-10-12 15:00 |
| `x4_transformer_s2` | X4 | matched transformer, autoregressive | 2 | 2.18 | 2026-10-12 17:10 |

**Projection:** 30.58 CPU-hours in all against the 32-hour cap (ruling W10): X3
23.83 h against its 24 (raised from 22 by `DECISIONS.md#F1-x3-cap`), X4
6.75 h against its 10. **Projected finish: about 2026-10-12 17:10 (+0530)**, if
nothing else uses the CPU. Sessions F2 and F3 run inference while the queue trains (PLAN §1.5), which slows both, so the
finish may slip; they log their jobs as contended.

**Outputs:** `results/x3_run_arm<A|B>_ho<ab>_seed<s>.json` and `runs/x3_arm<A|B>_ho<ab>_seed<s>/weights_2500.pt` for X3;
`results/baseline_run_<mlp|transformer>_ar_matched_seed<s>.json` and `runs/baseline_<arch>_ar_matched_seed<s>/weights_2500.pt`
for X4. Each run's output goes to `runs/queue_logs/<id>.log`; done and failed ids go to `runs/queue_round4_done.txt` and
`runs/queue_round4_failed.txt`. `scripts/queue_run.py` checks each run's record as it ends (iterations, seed, width or
parameter count, held-out episodes for X3, finite losses, weights present) and marks a run that fails a check as failed.

**Status command** (from the repository root). It reads only the runner's own log and the done and failed lists, which hold
no reading:

```
echo "done $(wc -l < runs/queue_round4_done.txt) of 30; failed $(wc -l < runs/queue_round4_failed.txt)"; tail -n 2 runs/queue_round4.log
```

**Do not read the per-run logs before F5** (PLAN §1.2 rule 5). The X3 runs evaluate their own checkpoints at 500 and 2,500
iterations on their fold's held-out episodes and print `[checkpoint …]` lines with those figures. If a run's progress must be
looked at, filter them out: `grep -v checkpoint runs/queue_logs/<id>.log | tail -n 3`.

**Check at launch (F1):** the first run, `x3_A_02_s0`, passed 50 iterations with a finite loss, on 7,688 training windows from
episodes [1, 3, 4, 5, 6, 7, 8, 9] (fold {0, 2} excluded). Only its iteration-0, -25 and -50 loss lines were read.

**F5 starts only when** the status command shows 30 done, 0 failed, and the runner's log
ends "queue empty; runner exits".
