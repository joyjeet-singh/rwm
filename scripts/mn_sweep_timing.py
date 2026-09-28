"""
M-74 -- the timing probe, the projection against the cap, and the queue, before launch.

For every configuration in rule M-74's grid, and for the centre (32, 8) as a calibration
point, the --sweep path is run for 20 iterations (PLAN S2a step 6). The steady cost per
iteration is taken between the first and the last logged iteration, so the first
iteration's start-up is excluded.

PROJECTION. A 2,500-iteration run costs more than 2,500 steady iterations: it also
evaluates its checkpoints at 500 and 2,500 and writes rolling checkpoints. So the probe is
CALIBRATED against the centre's own finished runs: the factor is the mean recorded
wall_clock_s of Arm A seeds 0-2 at 2,500 iterations (results/step5_armA_seed{0,1,2}.json)
over 2,500 x the centre probe's steady cost. Every configuration's projection is
factor x its steady cost x 2,500 x 3 seeds.

THE CAP. PLAN Appendix C caps the sweep at 25 projected CPU-hours. If the projection
exceeds it, whole configurations are dropped from the BOTTOM of M-74's priority order until
it fits; M-74 requires the drop to be recorded as a new ledger entry before launch, and
this script refuses to write the queue while a drop is unrecorded.

Writes results/mn_sweep_timing.json and, with --write-queue, runs/queue.txt: one line per
run, whole configurations in priority order, seeds 0, 1, 2 within each.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402

GRID = ((32, 32), (16, 8), (32, 16), (8, 8), (32, 2), (32, 1), (2, 8), (1, 8))  # M-74
CENTRE = (32, 8)
PROBE_ITERS = 20
ITERS = 2500
SEEDS = (0, 1, 2)
CAP_H = 25.0
PROBE_DIR = os.path.join(R.REPO_ROOT, "runs", "timing_probe")


def probe(m, n):
    cmd = [sys.executable, os.path.join(R.REPO_ROOT, "scripts", "step5_train.py"), "--arm",
           "A", "--seed", "0", "--iters", str(PROBE_ITERS), "--sweep", "--history", str(m),
           "--forecast", str(n), "--out-dir", PROBE_DIR]
    log = os.path.join(PROBE_DIR, f"probe_M{m}_N{n}.log")
    with open(log, "w") as f:
        rc = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, cwd=R.REPO_ROOT).returncode
    assert rc == 0, f"probe ({m}, {n}) exited {rc}; see {R.rel(log)}"
    a = json.load(open(os.path.join(PROBE_DIR, f"mn_sweep_run_M{m}_N{n}_seed0.json")))
    c = a["collapse"]
    first, last = c[0], c[-1]
    assert first["iter"] == 0 and last["iter"] == PROBE_ITERS - 1
    steady = (last["wall_clock_s"] - first["wall_clock_s"]) / (last["iter"] - first["iter"])
    return {"M": m, "N": n, "window": m + n, "steady_s_per_iter": steady,
            "probe_wall_clock_s": a["wall_clock_s"],
            "n_train_windows": a["hyperparameters"]["n_train_windows"]}


def main():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import p5_sweep_power as P5
    assert GRID == P5.GRID, "this script's grid is not M-74's (p5_sweep_power.GRID)"
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-queue", action="store_true")
    ap.add_argument("--drop-recorded-in", default=None,
                    help="ledger ID recording a drop, required when the grid exceeds the cap")
    args = ap.parse_args()
    if os.path.isdir(PROBE_DIR):
        shutil.rmtree(PROBE_DIR)
    os.makedirs(PROBE_DIR)

    t0 = time.time()
    centre = probe(*CENTRE)
    rows = [probe(m, n) for m, n in GRID]
    probe_minutes = (time.time() - t0) / 60

    full = [json.load(open(os.path.join(R.RESULTS, f"step5_armA_seed{s}.json")))["wall_clock_s"]
            for s in SEEDS]
    factor = (sum(full) / len(full)) / (centre["steady_s_per_iter"] * ITERS)
    for r in rows:
        r["projected_h_per_run"] = factor * r["steady_s_per_iter"] * ITERS / 3600
        r["projected_h_config"] = r["projected_h_per_run"] * len(SEEDS)
    kept, dropped = list(rows), []
    while sum(r["projected_h_config"] for r in kept) > CAP_H:
        dropped.insert(0, kept.pop())
    total = sum(r["projected_h_config"] for r in kept)

    print("=" * 90)
    print("M-74 TIMING PROBE — 20 iterations per configuration, projected against the cap")
    print("=" * 90)
    print(f"  centre (32, 8) probe {centre['steady_s_per_iter']:.3f} s/iter; Arm A seeds 0-2 "
          f"ran {', '.join(f'{x / 3600:.2f}' for x in full)} h -> calibration factor {factor:.3f}")
    for r in rows:
        tag = "DROPPED" if r in dropped else ""
        print(f"  ({r['M']:>2}, {r['N']:>2})  window {r['window']:>3}  {r['steady_s_per_iter']:.3f} s/iter"
              f"  -> {r['projected_h_per_run']:.2f} h/run, {r['projected_h_config']:.2f} h for 3 seeds  {tag}")
    print(f"  projected total {total:.2f} CPU-hours against the {CAP_H:.0f}-hour cap; "
          f"{len(kept)} of {len(rows)} configurations kept")

    out = {"rule": "M-74", "probe_iterations": PROBE_ITERS, "calibration": {
               "centre_probe": centre, "centre_full_runs_wall_clock_s": full,
               "factor": factor,
               "what": "mean wall_clock_s of Arm A seeds 0-2 at 2,500 iterations over "
                       "2,500 x the centre probe's steady s/iter; covers checkpoint "
                       "evaluations and rolling checkpoints"},
           "configs": rows, "cap_hours": CAP_H, "projected_total_hours": total,
           "queued_configs": [[r["M"], r["N"]] for r in kept],
           "dropped_configs": [[r["M"], r["N"]] for r in dropped],
           "drop_recorded_in": args.drop_recorded_in, "seeds": list(SEEDS),
           "iterations": ITERS, "probe_wall_minutes": probe_minutes,
           "threads": "none set, as every existing run (FILE_MAP.md §5)"}
    json.dump(out, open(os.path.join(R.RESULTS, "mn_sweep_timing.json"), "w"), indent=2)
    print("  wrote results/mn_sweep_timing.json")

    if args.write_queue:
        assert not dropped or args.drop_recorded_in, \
            "configurations were dropped: record the drop in the ledger first (M-74), then " \
            "pass --drop-recorded-in <ID>"
        qp = os.path.join(R.REPO_ROOT, "runs", "queue.txt")
        assert not os.path.exists(qp), f"{R.rel(qp)} exists; the queue is written once"
        with open(qp, "w") as f:
            f.write("# PRE-SUBMISSION training queue (PLAN S2a/S2b). One run per line:\n"
                    "# id arch M N seed iterations. Written by scripts/mn_sweep_timing.py;\n"
                    "# S2b appends its baselines after these lines.\n"
                    "# --- rule M-74: the M/N sweep, whole configurations in priority order\n")
            for r in kept:
                for s in SEEDS:
                    f.write(f"mn_M{r['M']}_N{r['N']}_s{s} rwm {r['M']} {r['N']} {s} {ITERS}\n")
        print(f"  wrote {R.rel(qp)}: {len(kept) * len(SEEDS)} runs")


if __name__ == "__main__":
    main()
