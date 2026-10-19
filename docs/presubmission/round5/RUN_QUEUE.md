# Round-5 run queue — rule X11 (ledger M-97 to M-100)

Launched by GT1 on 2026-10-19 at 16:44:57 (+0530), from the repository root, on mains power, with:

```
nohup caffeinate -i scripts/queue_runner.sh runs/queue_round5.txt > runs/queue_round5.log 2>&1 &
```

Runner PID 14182 at launch. `runs/` is gitignored, so this file is the committed record of what the queue holds. The
queue file was written from the committed record by `scripts/round5_queue_timing.py --queue-from-record`
(`results/round5_queue_timing.json`), after the pre-registration commit `1a2f021`. One run at a time (8 GB of RAM).

**The runs**, in queue order: 12 ensemble-5 runs (`scripts/step5_train.py --holdout a,b --ensemble 5`, trainer
`x11-e5-<fold>`) and 8 single-model runs (`--holdout a,b`, X3's trainer `x3-A-<fold>`), Arm A, 2,500 iterations each.

| id | kind | fold held out | seed | projected hours | projected finish (+0530) |
|---|---|---|---:|---:|---|
| `x11_e5_02_s0` | ensemble-5 | {0, 2} | 0 | 4.13 | 2026-10-19 20:52 |
| `x11_e5_34_s0` | ensemble-5 | {3, 4} | 0 | 4.13 | 2026-10-20 01:00 |
| `x11_e5_56_s0` | ensemble-5 | {5, 6} | 0 | 4.13 | 2026-10-20 05:08 |
| `x11_e5_79_s0` | ensemble-5 | {7, 9} | 0 | 4.13 | 2026-10-20 09:16 |
| `x11_A_02_s3` | single model | {0, 2} | 3 | 0.74 | 2026-10-20 10:00 |
| `x11_A_34_s3` | single model | {3, 4} | 3 | 0.74 | 2026-10-20 10:45 |
| `x11_A_56_s3` | single model | {5, 6} | 3 | 0.74 | 2026-10-20 11:29 |
| `x11_A_79_s3` | single model | {7, 9} | 3 | 0.74 | 2026-10-20 12:13 |
| `x11_e5_02_s1` | ensemble-5 | {0, 2} | 1 | 4.13 | 2026-10-20 16:21 |
| `x11_e5_34_s1` | ensemble-5 | {3, 4} | 1 | 4.13 | 2026-10-20 20:29 |
| `x11_e5_56_s1` | ensemble-5 | {5, 6} | 1 | 4.13 | 2026-10-21 00:37 |
| `x11_e5_79_s1` | ensemble-5 | {7, 9} | 1 | 4.13 | 2026-10-21 04:45 |
| `x11_A_02_s4` | single model | {0, 2} | 4 | 0.74 | 2026-10-21 05:29 |
| `x11_A_34_s4` | single model | {3, 4} | 4 | 0.74 | 2026-10-21 06:14 |
| `x11_A_56_s4` | single model | {5, 6} | 4 | 0.74 | 2026-10-21 06:58 |
| `x11_A_79_s4` | single model | {7, 9} | 4 | 0.74 | 2026-10-21 07:42 |
| `x11_e5_02_s2` | ensemble-5 | {0, 2} | 2 | 4.13 | 2026-10-21 11:50 |
| `x11_e5_34_s2` | ensemble-5 | {3, 4} | 2 | 4.13 | 2026-10-21 15:58 |
| `x11_e5_56_s2` | ensemble-5 | {5, 6} | 2 | 4.13 | 2026-10-21 20:06 |
| `x11_e5_79_s2` | ensemble-5 | {7, 9} | 2 | 4.13 | 2026-10-22 00:14 |

**Projection:** 55.49 CPU-hours against the 62-hour cap (`DECISIONS.md#GT1-cap`; the user's
ruling raised Y5's 30). **Projected finish: about 2026-10-22 00:14 (+0530)**, if nothing else uses the CPU.
Sessions G3 and G4 run inference while the queue trains (PLAN §1.5), which slows both, so the finish may slip; they log
their jobs as contended.

**Outputs:** `results/x3_run_armA_ho<ab>_seed<s>_ens5.json` and `runs/x3_armA_ho<ab>_seed<s>_ens5/weights_2500.pt`
(ensemble-5, seeds 0-2); `results/x3_run_armA_ho<ab>_seed<s>.json` and `runs/x3_armA_ho<ab>_seed<s>/weights_2500.pt`
(single model, seeds 3-4). Each run's output goes to `runs/queue_logs/<id>.log`; done and failed ids go to
`runs/queue_round5_done.txt` and `runs/queue_round5_failed.txt`. `scripts/queue_run.py` checks each record as it
ends (iterations, seed, width, held-out episodes, arm, ensemble size for the ensemble-5 runs, finite losses, weights
present) and marks a run that fails a check as failed.

**Status command** (from the repository root). It reads only the runner's own log and the done and failed lists,
which hold no reading:

```
echo "done $(wc -l < runs/queue_round5_done.txt) of 20; failed $(wc -l < runs/queue_round5_failed.txt)"; tail -n 2 runs/queue_round5.log
```

**Do not read the per-run logs' checkpoint lines before GT2** (PLAN GT1 item 6). Each run evaluates its own checkpoints
at 500 and 2,500 iterations on its fold's held-out episodes and prints `[checkpoint …]` lines with those figures.
G3 and G4 may check only that each run started and that its loss is finite, through a filter:
`grep -v checkpoint runs/queue_logs/<id>.log | tail -n 3`.

**If the runner stops** (machine restart, crash; check with `pgrep -f queue_runner`): relaunch the same command. The
runner re-reads the queue file and skips every id in the done or failed list. A run that was interrupted has no
record in `results/` (the driver writes it at the end) and restarts from iteration 0; delete nothing in its
`runs/` directory by hand. A run in the failed list is not retried automatically: read its log through the filter
above, record the failure in the session log, and stop `BLOCKED` with a question in `DECISIONS.md`. Never edit
`scripts/queue_runner.sh` while it runs (CLAUDE.md rule 7); `scripts/queue_run.py` is read afresh per run.

**Check at launch (GT1):** the first run, `x11_e5_02_s0`, passed 50 iterations with a finite loss, on 7,688 training
windows from episodes [1, 3, 4, 5, 6, 7, 8, 9] (fold {0, 2} excluded). Only its iteration-0, -25 and -50 loss lines
were read.

**GT2 starts only when** the status command shows 20 done, 0 failed, and the runner's log ends "queue empty; runner
exits". G3 must also have committed X9's script with X11e (`fold_e5`) under its `PRE-REGISTER` subject first.
