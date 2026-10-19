"""
Round 5, rule X11 -- the timing probes, the projection against the cap, and the queue, before launch
(PLAN round 5, GT1 items 5 and 6). scripts/round4_queue_timing.py's method, for X11's two kinds of run.

PROBES, 20 iterations each, into runs/timing_probe_round5/ (gitignored), on an idle machine, fold {0, 2}:
  ensemble-5 Arm A, seed 0      scripts/step5_train.py --holdout 0,2 --ensemble 5
  single-model Arm A, seed 3    scripts/step5_train.py --holdout 0,2
No probe reaches a checkpoint (500 is the first), so none evaluates anything. The steady cost per iteration is
taken between the first and the last logged iteration, so start-up is excluded (round4_queue_timing.py).

PROJECTION. As round 4: a run projects to the mean recorded wall clock of finished 2,500-iteration runs of the
same kind -- ensemble-5: results/step5_armA_seed{0,1,2}_ens5.json; single model: X3's twelve Arm A fold runs,
results/x3_run_armA_ho<ab>_seed{0,1,2}.json. Added in round 5: the probe is compared with those runs' own steady
rate (from their `collapse` logs, iterations 0-475, where no checkpoint evaluation falls); if today's machine is
slower by more than 10%, the projection is scaled up by the ratio (never down).

CAP (DECISIONS.md#GT1-cap, the user's ruling of 2026-10-19 amending Y5's 30 CPU-hours): the cap is
1.10 x the projection, rounded up to the next whole hour; the record states both. The session stops BLOCKED if
a re-probe's projection exceeds a cap already recorded (`--cap H` checks against H).

QUEUE (runs/queue_round5.txt, "id arch M N seed iterations"): ensemble-5 seed 0 on the four folds, single
seed 3 on the four, ensemble-5 seed 1, single seed 4, ensemble-5 seed 2; folds in X3's order.

  python scripts/round5_queue_timing.py                       # probe, project, write the record
  python scripts/round5_queue_timing.py --cap 63              # ... and stop if the projection exceeds 63 h
  python scripts/round5_queue_timing.py --queue-from-record   # write the queue from the committed record
Writes results/round5_queue_timing.json.
"""
import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402

PROBE_ITERS, ITERS = 20, 2500
FOLDS = ((0, 2), (3, 4), (5, 6), (7, 9))
PROBE_FOLD = (0, 2)
SLOWER_TOL = 1.10
CAP_MARGIN = 1.10
PROBE_DIR = os.path.join(R.REPO_ROOT, "runs", "timing_probe_round5")
OUT = os.path.join(R.RESULTS, "round5_queue_timing.json")
QUEUE = os.path.join(R.REPO_ROOT, "runs", "queue_round5.txt")
PY = sys.executable
ORDER = (("e5", 0), ("single", 3), ("e5", 1), ("single", 4), ("e5", 2))


def _finite(curves):
    return all(math.isfinite(x) for v in curves.values() for x in v)


def steady(collapse, last_iter):
    c = [x for x in collapse if x["iter"] <= last_iter]
    return (c[-1]["wall_clock_s"] - c[0]["wall_clock_s"]) / (c[-1]["iter"] - c[0]["iter"])


def probe(kind):
    extra, seed = (["--ensemble", "5"], 0) if kind == "e5" else ([], 3)
    cmd = [PY, os.path.join(R.REPO_ROOT, "scripts", "step5_train.py"), "--arm", "A", "--seed", str(seed),
           "--iters", str(PROBE_ITERS), "--holdout", ",".join(map(str, PROBE_FOLD)), "--out-dir", PROBE_DIR] + extra
    with open(os.path.join(PROBE_DIR, f"probe_{kind}.log"), "w") as f:
        rc = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, cwd=R.REPO_ROOT).returncode
    assert rc == 0, f"probe {kind} exited {rc}"
    name = f"x3_run_armA_ho{''.join(map(str, PROBE_FOLD))}_seed{seed}{'_ens5' if kind == 'e5' else ''}.json"
    a = json.load(open(os.path.join(PROBE_DIR, name)))
    c = a["collapse"]
    assert c[0]["iter"] == 0 and c[-1]["iter"] == PROBE_ITERS - 1
    assert a["hyperparameters"]["holdout_episodes"] == list(PROBE_FOLD)
    assert a["hyperparameters"]["ensemble"] == (5 if kind == "e5" else 1)
    return {"kind": kind, "seed": seed, "fold": list(PROBE_FOLD), "steady_s_per_iter": steady(c, PROBE_ITERS - 1),
            "probe_wall_clock_s": a["wall_clock_s"], "n_train_windows": a["hyperparameters"]["n_train_windows"],
            "losses_finite": _finite(a["curves"]), "rule": a.get("rule")}


def finished(kind):
    if kind == "e5":
        paths = [f"results/step5_armA_seed{s}_ens5.json" for s in (0, 1, 2)]
    else:
        paths = [f"results/x3_run_armA_ho{''.join(map(str, f))}_seed{s}.json" for f in FOLDS for s in (0, 1, 2)]
    recs = [json.load(open(os.path.join(R.REPO_ROOT, p))) for p in paths]
    return {"runs": paths, "wall_clock_s": [r["wall_clock_s"] for r in recs],
            "steady_s_per_iter_0_475": [steady(r["collapse"], 475) for r in recs]}


def queue_lines():
    lines = []
    for kind, s in ORDER:
        lines.append(f"# --- rule X11, {'ensemble-5' if kind == 'e5' else 'single model'} seed {s}, each new fold")
        for fold in FOLDS:
            f = "".join(map(str, fold))
            lines.append(f"x11_e5_{f}_s{s} x11-e5-{f} 32 8 {s} {ITERS}" if kind == "e5"
                         else f"x11_A_{f}_s{s} x3-A-{f} 32 8 {s} {ITERS}")
    return lines


def queue_from_record():
    t = json.load(open(OUT))
    assert not t["blocked"], "the record is BLOCKED: nothing may be queued"
    assert not os.path.exists(QUEUE), f"{R.rel(QUEUE)} exists; the queue is written once"
    lines = queue_lines()
    with open(QUEUE, "w") as f:
        f.write("# ROUND 5 training queue (rule X11). One run per line: id arch M N seed iterations.\n"
                "# Written by scripts/round5_queue_timing.py --queue-from-record from results/round5_queue_timing.json.\n")
        f.write("\n".join(lines) + "\n")
    print(f"  wrote {R.rel(QUEUE)}: {sum(1 for x in lines if not x.startswith('#'))} runs")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cap", type=float, default=None, help="a cap already recorded; stop if the projection exceeds it")
    ap.add_argument("--queue-from-record", action="store_true")
    args = ap.parse_args()
    if args.queue_from_record:
        return queue_from_record()
    if os.path.isdir(PROBE_DIR):
        shutil.rmtree(PROBE_DIR)
    os.makedirs(PROBE_DIR)
    load_before = os.getloadavg()
    t0 = time.time()
    probes = {k: probe(k) for k in ("e5", "single")}
    probe_minutes = (time.time() - t0) / 60
    load_after = os.getloadavg()
    assert all(p["losses_finite"] for p in probes.values()), "a probe's loss went non-finite"
    per_run = {}
    for k in ("e5", "single"):
        fin = finished(k)
        base_h = sum(fin["wall_clock_s"]) / len(fin["wall_clock_s"]) / 3600
        fin_rate = sum(fin["steady_s_per_iter_0_475"]) / len(fin["steady_s_per_iter_0_475"])
        slow = probes[k]["steady_s_per_iter"] / fin_rate
        per_run[k] = {"finished": fin, "finished_mean_h": base_h, "finished_steady_s_per_iter": fin_rate,
                      "probe_over_finished": slow, "scaled": bool(slow > SLOWER_TOL),
                      "projected_h": base_h * (slow if slow > SLOWER_TOL else 1.0)}
    n = {"e5": 12, "single": 8}
    total = sum(per_run[k]["projected_h"] * n[k] for k in n)
    cap = math.ceil(CAP_MARGIN * total)
    blocked = args.cap is not None and total > args.cap
    out = {"rule": "X11 (round 5) queue timing", "probe_iterations": PROBE_ITERS, "probes": probes,
           "probe_minutes": probe_minutes, "load_before": load_before, "load_after": load_after,
           "per_run": per_run, "n_runs": n, "projected_total_h": total,
           "cap_rule": "DECISIONS.md#GT1-cap: 1.10 x the projection, rounded up to the next whole hour",
           "cap_h": cap if args.cap is None else args.cap, "cap_checked_against": args.cap,
           "blocked": bool(blocked), "queue_order": [list(x) for x in ORDER],
           "queue_lines": [x for x in queue_lines() if not x.startswith("#")]}
    json.dump(out, open(OUT, "w"), indent=1)
    for k, v in per_run.items():
        print(f"  {k}: probe {probes[k]['steady_s_per_iter']:.3f} s/iter, finished {v['finished_steady_s_per_iter']:.3f} "
              f"(x{v['probe_over_finished']:.3f}); projected {v['projected_h']:.2f} h per run")
    print(f"  projected {total:.2f} CPU-h for 20 runs; cap {out['cap_h']} h; load {load_before} -> {load_after}"
          + ("  BLOCKED" if blocked else ""))
    print(f"  wrote {R.rel(OUT)}")
    sys.exit(1 if blocked else 0)


if __name__ == "__main__":
    main()
