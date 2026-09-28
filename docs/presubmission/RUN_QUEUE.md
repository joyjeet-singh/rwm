# Run queue — pre-submission programme

Launched by S2a on 2026-09-28 at 14:51:27 (+0530) with the plan's command, from the repository
root:

```
nohup caffeinate -i scripts/queue_runner.sh > runs/queue.log 2>&1 &
```

`runs/` is gitignored, so this file is the committed record of what the queue holds.
`results/mn_sweep_timing.json` is the launch record the projection below is read from.

## What is queued

**Rule M-74, the M/N sweep:** 8 configurations × seeds 0, 1, 2 × 2,500
iterations = 24 runs. Each is Arm A at (M, N), with every other
setting the centre's. They run as whole configurations, in M-74's priority order.

| Priority | (M, N) | Window | Training windows | Probe s/iter | Projected h/run | Projected h, 3 seeds |
|---:|---|---:|---:|---:|---:|---:|
| 1 | (32, 32) | 64 | 7,495 | 1.930 | 1.83 | 5.50 |
| 2 | (16, 8) | 24 | 7,815 | 0.640 | 0.61 | 1.82 |
| 3 | (32, 16) | 48 | 7,623 | 1.445 | 1.37 | 4.11 |
| 4 | (8, 8) | 16 | 7,879 | 0.428 | 0.41 | 1.22 |
| 5 | (32, 2) | 34 | 7,735 | 1.013 | 0.96 | 2.88 |
| 6 | (32, 1) | 33 | 7,743 | 0.871 | 0.83 | 2.48 |
| 7 | (2, 8) | 10 | 7,927 | 0.283 | 0.27 | 0.81 |
| 8 | (1, 8) | 9 | 7,935 | 0.249 | 0.24 | 0.71 |

- **Projection:** 19.53 CPU-hours against the 25-hour
  cap, with nothing dropped.
- **Calibration:** the 20-iteration probes are scaled by factor 1.367.
  That is the ratio of Arm A's own 2,500-iteration wall clock to the centre probe's rate, and it
  covers the checkpoint evaluations at 500 and 2,500 iterations.
- **Projected finish of the sweep: about 2026-09-29 10:23 (+0530)**, if nothing else uses
  the CPU.
- **Baselines:** queued after the sweep by S2b (below).

**Rules M-75 and M-76, the architecture baselines:** added by S2b on 2026-09-28. There are 18
runs: MLP, RSSM and transformer at the original's Table S7 sizes, × teacher-forced (M-75) and
autoregressive (M-76) regimes, × seeds 0–2, at 2,500 iterations each. They are queued in the
rules' order.

| Rule | Baseline | Regime | Parameters | Probe s/iter (contended) | Projected h/run | Projected h, 3 seeds |
|---|---|---|---:|---:|---:|---:|
| M-75 | mlp | tf | 610,484 | 0.139 | 0.07 | 0.21 |
| M-75 | rssm | tf | 3,180,468 | 5.485 | 2.81 | 8.43 |
| M-75 | transformer | tf | 132,148 | 2.010 | 1.03 | 3.09 |
| M-76 | mlp | ar | 610,484 | 0.196 | 0.10 | 0.30 |
| M-76 | rssm | ar | 3,180,468 | 4.459 | 2.28 | 6.85 |
| M-76 | transformer | ar | 132,148 | 2.042 | 1.05 | 3.14 |

- **Projection:** 22.01 CPU-hours, above PLAN Appendix C's
  20-hour baseline cap. S2b stopped BLOCKED, and the user raised
  the cap to 23 hours (`DECISIONS_FOR_USER.md#S2b-baseline-cap`: "Raise cap;
  queue all 18").
- **Why it is conservative:** the projection comes from `results/baselines_timing.json`. The
  probes ran while the sweep trained, and the calibration factor (0.737)
  also carries RWM's checkpoint evaluations, which the baselines never run.
- **Parameter-matched variants:** not run. All specs together project
  46.07 h, over the cap, so under M-75 and M-76 none of them is queued.
- **Projected finish of everything: about 2026-09-30 08:23 (+0530).**
- **Outputs:** each baseline run writes `results/baseline_run_<arch>_<regime>_s7_seed<s>.json`
  and `runs/baseline_<arch>_<regime>_s7_seed<s>/`. `scripts/queue_run.py` checks its
  iterations, M = 32, N = 8, arch, regime, spec, seed, parameter count, `wall_clock_s`, finite
  losses and weights.

Each run writes:
- its artifact to `results/mn_sweep_run_M<M>_N<N>_seed<s>.json`, outside every
  `results/step5_*` glob the paper reads;
- its weights to `runs/mn_M<M>_N<N>_seed<s>/`;
- its log to `runs/queue_logs/<id>.log`.

`scripts/queue_run.py` checks every finished run as it ends. It confirms the iterations, M, N,
arch, seed, width and `wall_clock_s`; that every loss trace is finite; and that the weights exist.
A run that fails any check goes to `runs/queue_failed.txt`, and the queue carries on.

## Status, in one command (from the repository root)

```
tail -n 4 runs/queue.log; echo "done $(wc -l < runs/queue_done.txt), failed $(wc -l < runs/queue_failed.txt), queued $(grep -vc '^#' runs/queue.txt)"
```

## Rules while it runs (PLAN §1.5)

- **The queue owns the two cores until S8.** Other sessions may run the paper build and short
  scripts, each under about 10 CPU-minutes, and must log any job over 1 minute. Every such job
  inflates the `wall_clock_s` of the run it overlaps, and that is the training-time half M-74
  reports.
- **Never run a second training job.** The machine has 8 GB.
- **Never edit `scripts/queue_runner.sh` while it runs** (CLAUDE.md rule 7). New architectures
  go into `scripts/queue_run.py`, which each run reads afresh.
- **A line in `runs/queue_failed.txt` stops S8** with BLOCKED (PLAN S8). M-74 cannot be
  discharged with a configuration short of three seeds.
