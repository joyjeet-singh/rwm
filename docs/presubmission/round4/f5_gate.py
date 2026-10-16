"""F5 item 1: the training gate for rules X3 (M-86) and X4 (M-87), from each run's own record.

For every id in runs/queue_round4.txt, through scripts/queue_run.py's own trainer map and check() (the checks the queue
applied as each run ended), and then independently:
  - the id is in runs/queue_round4_done.txt, and runs/queue_round4_failed.txt is empty;
  - iterations and seed are the queued ones; for X3 the arm is the queued arm and the held-out episodes are the fold its
    id names, disjoint from its training episodes, the ten episodes between them; for X4 the parameter count is the
    queued one (within 5% of RWM's 714,164, rows 33 and 34 of BASELINE_SPECS.md) and the held-out episodes are {1, 8};
  - every loss trace and final term is finite (no NaN), and the weights file exists and is not empty;
  - every run read the same data (data_sha256).
Reads no reading: no checkpoint evaluation, no rollout error. Records each run's wall-clock time, summed per rule against
the caps (X3 24 h, X4 10 h, 32 h in all), with the queue's projection beside it.
Writes docs/presubmission/round4/f5_gate.json; exits 1 if any check fails.
  $PY docs/presubmission/round4/f5_gate.py
"""
import json
import math
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "src"))
os.chdir(ROOT)
import queue_run as Q  # noqa: E402

OUT = "docs/presubmission/round4/f5_gate.json"
QUEUE, DONE, FAILED = "runs/queue_round4.txt", "runs/queue_round4_done.txt", "runs/queue_round4_failed.txt"
RWM_PARAMS, TOL = 714164, 0.05
CAPS = {"X3": 24.0, "X4": 10.0, "all": 32.0}

rows = [ln.split() for ln in open(QUEUE) if ln.strip() and not ln.startswith("#")]
done = [ln.strip() for ln in open(DONE) if ln.strip()]
failed = [ln.strip() for ln in open(FAILED) if ln.strip()]
proj = json.load(open("results/round4_queue_timing.json"))
problems, runs, shas = [], [], set()
if len(rows) != 30:
    problems.append(f"queue holds {len(rows)} runs, not 30")
if failed:
    problems.append(f"failed list not empty: {failed}")
if sorted(done) != sorted(r[0] for r in rows) or len(done) != len(set(done)):
    problems.append(f"done list differs from the queue: {sorted(set(done) ^ set(r[0] for r in rows))}")
for run_id, arch, m, n, seed, iters in rows:
    m, n, seed, iters = int(m), int(n), int(seed), int(iters)
    _, artifact, weights, expect = Q.TRAINERS[arch](run_id, m, n, seed, iters)
    bad = Q.check(artifact, weights, expect)
    a = json.load(open(artifact)) if os.path.exists(artifact) else {}
    hp = a.get("hyperparameters", {})
    rule = "X3" if arch.startswith("x3-") else "X4"
    if hp.get("iterations") != iters or a.get("seed") != seed:
        bad.append(f"iterations/seed {hp.get('iterations')}/{a.get('seed')}, queued {iters}/{seed}")
    ho, tr = hp.get("holdout_episodes"), hp.get("train_episodes")
    if rule == "X3":
        fold = sorted(int(c) for c in arch.split("-")[2])
        if a.get("arm") != arch.split("-")[1] or ho != fold or hp.get("holdout_fold") != fold:
            bad.append(f"arm/holdout {a.get('arm')}/{ho}/{hp.get('holdout_fold')}, id names {arch.split('-')[1]}/{fold}")
    else:
        npar = hp.get("n_params")
        if not (isinstance(npar, int) and abs(npar / RWM_PARAMS - 1) <= TOL):
            bad.append(f"n_params {npar} not within {TOL:.0%} of {RWM_PARAMS}")
        if ho != [1, 8]:
            bad.append(f"holdout {ho}, not [1, 8]")
        if a.get("spec") != "matched" or a.get("regime") != "ar":
            bad.append(f"spec/regime {a.get('spec')}/{a.get('regime')}")
    if not (isinstance(tr, list) and isinstance(ho, list) and not set(tr) & set(ho)
            and sorted(tr + ho) == list(range(10))):
        bad.append(f"train {tr} and held-out {ho} do not partition the ten episodes")
    for k, v in a.get("final_terms", {}).items():
        if not (isinstance(v, (int, float)) and math.isfinite(v)):
            bad.append(f"final term {k} = {v}")
    if not (os.path.exists(weights) and os.path.getsize(weights) > 0):
        bad.append(f"weights missing or empty: {weights}")
    shas.add(a.get("data_sha256"))
    runs.append({"id": run_id, "rule": rule, "artifact": os.path.relpath(artifact, ROOT),
                 "weights": os.path.relpath(weights, ROOT), "weights_bytes": os.path.getsize(weights) if os.path.exists(weights) else None,
                 "iterations": hp.get("iterations"), "seed": a.get("seed"), "holdout_episodes": ho,
                 "n_params": hp.get("n_params"), "wall_clock_h": (a.get("wall_clock_s") or 0) / 3600, "problems": bad})
    problems += [f"{run_id}: {b}" for b in bad]
if len(shas) != 1:
    problems.append(f"runs read different data: {sorted(map(str, shas))}")
hours = {r: sum(x["wall_clock_h"] for x in runs if x["rule"] == r) for r in ("X3", "X4")}
hours["all"] = hours["X3"] + hours["X4"]
over = [r for r in CAPS if hours[r] > CAPS[r]]
if over:
    problems.append(f"wall-clock hours over cap: {[(r, round(hours[r], 2), CAPS[r]) for r in over]}")
rec = {"what": "F5 item 1: the training gate for X3 and X4, from each run's record; no reading is read",
       "n_queued": len(rows), "n_done": len(done), "n_failed": len(failed), "data_sha256": sorted(map(str, shas)),
       "wall_clock_hours": {k: round(v, 3) for k, v in hours.items()}, "caps_hours": CAPS,
       "projected_hours": {"X3": proj["x3"]["projected_h"], "X4": proj["x4"]["projected_h"], "all": proj["projected_total_h"]},
       "note_on_hours": ("sums of each record's wall_clock_s, the runs' own timing; the first attempt at x3_A_79_s2, "
                         "interrupted on 2026-10-12, left no record, so its time is not in this sum"),
       "runs": runs, "problems": problems, "gate": "PASS" if not problems else "BLOCKED"}
json.dump(rec, open(OUT, "w"), indent=1)
print(f"  {len(rows)} queued, {len(done)} done, {len(failed)} failed; data {len(shas)} sha")
print(f"  wall-clock hours: X3 {hours['X3']:.2f} (cap 24), X4 {hours['X4']:.2f} (cap 10), all {hours['all']:.2f} (cap 32)")
for p in problems[:20]:
    print("  !!", p)
print(f"  gate: {rec['gate']}  -> {OUT}")
sys.exit(0 if not problems else 1)
