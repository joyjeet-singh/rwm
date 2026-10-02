# Round-2 run queue — rule X1, Part C (ledger M-80)

Launched by T2 on 2026-10-02 at 12:27:21 (+0530) with the plan's command:

```
nohup caffeinate -i scripts/queue_runner.sh runs/queue_round2.txt > runs/queue_round2.log 2>&1 &
```

**The runs** (`runs/queue_round2.txt`), teacher-forced RSSM, seed 0, 2,500 iterations each, one at a time:

| id | variant | spec | projected hours | projected finish (+0530) |
|---|---|---|---:|---|
| `x1_x1v1_s0` | V1, PlaNet's KL settings (BASELINE_SPECS rows 39-42) | `x1v1` | 3.16 | 2026-10-02 15:36 |
| `x1_x1v2_s0` | V2, DreamerV2's layer-normalised GRU (rows 43-47) | `x1v2` | 3.15 | 2026-10-02 18:45 |

From `results/x1_partc_timing.json`: 6.31 projected CPU-hours against M-80's cap of 10, calibrated as
`scripts/baselines_timing.py` calibrates (factor 1.251). Sessions T3-T7 edit text only and keep other jobs under
about 10 CPU-minutes (PLAN §1.5), so the finish may slip somewhat.

**The cap, if a variant rescues.** M-80 says a variant that rescues on seed 0 then runs seeds 1-2. For one variant
that is about 6.3 more CPU-hours, taking Part C to about 12.6 h, past the cap. So if
`scripts/rssm_diagnostics.py --part c` (T8) finds a rescue on seed 0, T8 stops BLOCKED for the user's ruling before
queueing those seeds. The worst case, both variants rescuing, projects 18.9 h.

**Outputs:** `results/baseline_run_rssm_tf_x1v1_seed0.json`, `results/baseline_run_rssm_tf_x1v2_seed0.json`;
weights in `runs/baseline_rssm_tf_x1v{1,2}_seed0/weights_2500.pt` (gitignored). Done and failed ids go to
`runs/queue_round2_done.txt` and `runs/queue_round2_failed.txt`.

**Status command** (from the repository root):

```
tail -3 runs/queue_round2.log; cat runs/queue_round2_done.txt runs/queue_round2_failed.txt 2>/dev/null; grep -hE "^ +[0-9]+ +state" runs/queue_logs/x1_*.log | tail -2
```
