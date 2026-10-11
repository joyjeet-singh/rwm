"""F1 item 6: docs/presubmission/round4/RUN_QUEUE.md, the committed record of the round-4 queue (runs/ is gitignored).
Every figure is read from results/round4_queue_timing.json and runs/queue_round4.log (the launch line); projected finishes
are the launch time plus the cumulative projected hours. Run from the repository root:
  $PY docs/presubmission/round4/f1_run_queue.py
"""
import datetime
import json
import re

T = json.load(open("results/round4_queue_timing.json"))
log = open("runs/queue_round4.log").read()
m = re.search(r"^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) queue runner start, pid (\d+)", log, re.M)
assert m, "no launch line in runs/queue_round4.log"
start = datetime.datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")
per = T["projected_h_per_run"]
first = open("runs/queue_logs/x3_A_02_s0.log").read()
w = re.search(r"(\d+) training windows from episodes (\[[^\]]*\])", first)
assert w and all(re.search(rf"^ +{i} +[-0-9.]", first, re.M) for i in (0, 25, 50)), "first run has not reached 50 iterations"
kind = lambda arch: ("x3_armA" if arch.startswith("x3-A") else "x3_armB" if arch.startswith("x3-B")
                     else arch.replace("-ar-matched", "_ar_matched"))
rows, t = [], start
for line in T["queue"]:
    if line.startswith("#"):
        continue
    rid, arch, mm, nn, seed, iters = line.split()
    h = per[kind(arch)]
    t = t + datetime.timedelta(hours=h)
    rule = "X3" if arch.startswith("x3") else "X4"
    what = (f"Arm {arch[3]}, held out {{{arch[5]}, {arch[6]}}}" if rule == "X3"
            else f"matched {arch.split('-')[0]}, autoregressive")
    rows.append(f"| `{rid}` | {rule} | {what} | {seed} | {h:.2f} | {t:%Y-%m-%d %H:%M} |")
md = f"""# Round-4 run queue — rules X3 (ledger M-86) and X4 (ledger M-87)

Launched by F1 on {start:%Y-%m-%d} at {start:%H:%M:%S} (+0530), from the repository root, with the plan's command:

```
nohup caffeinate -i scripts/queue_runner.sh runs/queue_round4.txt > runs/queue_round4.log 2>&1 &
```

`runs/` is gitignored, so this file is the committed record of what the queue holds. The queue file was written from the
committed record by `scripts/round4_queue_timing.py --queue-from-record` (`results/round4_queue_timing.json`), after the
pre-registration commit of both rules. One run at a time (8 GB of RAM).

**The runs**, in queue order: X3 seed 0, X4 seed 0, X3 seed 1, X4 seed 1, X3 seed 2, X4 seed 2. {T['x3']['n_runs']} X3 runs
(`scripts/step5_train.py --holdout`) and {T['x4']['n_runs']} X4 runs (`scripts/train_baseline.py --spec matched --regime ar`),
2,500 iterations each.

| id | rule | run | seed | projected hours | projected finish (+0530) |
|---|---|---|---:|---:|---|
""" + "\n".join(rows) + f"""

**Projection:** {T['projected_total_h']:.2f} CPU-hours in all against the {T['cap_total_h']:g}-hour cap (ruling W10): X3
{T['x3']['projected_h']:.2f} h against its {T['x3']['cap_h']:g} (raised from 22 by `DECISIONS.md#F1-x3-cap`), X4
{T['x4']['projected_h']:.2f} h against its {T['x4']['cap_h']:g}. **Projected finish: about {t:%Y-%m-%d %H:%M} (+0530)**, if
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
echo "done $(wc -l < runs/queue_round4_done.txt) of {T['x3']['n_runs'] + T['x4']['n_runs']}; failed $(wc -l < runs/queue_round4_failed.txt)"; tail -n 2 runs/queue_round4.log
```

**Do not read the per-run logs before F5** (PLAN §1.2 rule 5). The X3 runs evaluate their own checkpoints at 500 and 2,500
iterations on their fold's held-out episodes and print `[checkpoint …]` lines with those figures. If a run's progress must be
looked at, filter them out: `grep -v checkpoint runs/queue_logs/<id>.log | tail -n 3`.

**Check at launch (F1):** the first run, `x3_A_02_s0`, passed 50 iterations with a finite loss, on {int(w.group(1)):,} training windows from
episodes {w.group(2)} (fold {{0, 2}} excluded). Only its iteration-0, -25 and -50 loss lines were read.

**F5 starts only when** the status command shows {T['x3']['n_runs'] + T['x4']['n_runs']} done, 0 failed, and the runner's log
ends "queue empty; runner exits".
"""
open("docs/presubmission/round4/RUN_QUEUE.md", "w", encoding="utf-8").write(md)
print(f"wrote docs/presubmission/round4/RUN_QUEUE.md: {len(rows)} runs, projected finish {t:%Y-%m-%d %H:%M}")
