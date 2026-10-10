"""
Round 4, rules X3 and X4 -- the timing probes, the projection against the caps, and the queue,
before launch (PLAN round 4, F1 item 3 and item 6).

PROBES, 20 iterations each, into runs/timing_probe_round4/ (gitignored), on an idle machine:
  x3 Arm A and Arm B on fold {0, 2}            scripts/step5_train.py --holdout 0,2
  x4 the matched MLP and transformer, ar       scripts/train_baseline.py --spec matched --regime ar
  calibration: the Table S7 MLP and transformer, ar, which have finished 2,500-iteration runs.
No probe reaches a checkpoint (500 is the first), so none evaluates anything.
The steady cost per iteration is taken between the first and the last logged iteration, as
scripts/mn_sweep_timing.py takes it, so the first iteration's start-up is excluded.

PROJECTION, mn_sweep_timing.py's calibration applied per kind of run. A 2,500-iteration run
costs more than 2,500 steady iterations (checkpoint evaluations for RWM, checkpoint writes,
whatever else the machine was doing), so each probe is calibrated against finished runs of the
same kind: factor = mean recorded wall_clock_s of the finished runs / (2,500 x today's probe).
  Arm A: results/step5_armA_seed{0,1,2}.json, against today's Arm A probe (fold {0, 2} has 7,688
         training windows to {1, 8}'s 7,687, and the cost per iteration is set by the batch).
  Arm B: results/step5_armB_seed{0,1,2}.json, against today's Arm B probe.
  matched MLP / transformer: results/baseline_run_<arch>_ar_s7_seed{0,1,2}.json, against today's
         Table S7 probe of the same architecture; projected = factor x matched probe x 2,500.
So an X3 run projects to the finished runs' mean wall clock, and an X4 run to its Table S7
counterpart's, scaled by today's measured cost ratio.

CAPS AND FALLBACKS (PLAN F1 item 3; Annex 2 X3 and X4, fixed before this probe ran):
  X3 <= 24 h with seeds 0-2 (22 h in the plan; DECISIONS.md#F1-x3-cap), else seeds 0-1;  X4 <= 10 h with seeds 0-2, else seeds 0-1;
  the total <= 32 h (ruling W10). If a rule exceeds its cap even at two seeds, or the total
  exceeds 32 h, nothing is queued: the session stops BLOCKED.

QUEUE (runs/queue_round4.txt, scripts/queue_runner.sh's format "id arch M N seed iterations"):
  X3 seed 0 (8 runs), X4 seed 0 (2), X3 seed 1, X4 seed 1, X3 seed 2, X4 seed 2, dropping the
  seeds a fallback removes. Within a seed, the folds in Annex 2's order, Arm A before Arm B.

  python scripts/round4_queue_timing.py                 # probe, project, write the record
  python scripts/round4_queue_timing.py --write-queue   # ... and runs/queue_round4.txt
  python scripts/round4_queue_timing.py --queue-from-record   # the queue from the committed record
Writes results/round4_queue_timing.json.
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

PROBE_ITERS = 20
ITERS = 2500
SEEDS = (0, 1, 2)
FALLBACK_SEEDS = (0, 1)
FOLDS = ((0, 2), (3, 4), (5, 6), (7, 9))          # Annex 2 X3, in its order
PROBE_FOLD = (0, 2)
X4_ARCHS = ("mlp", "transformer")                  # Annex 2 X4 / ruling W2: no matched RSSM
# X3's cap was 22 h in PLAN F1 item 3; raised to 24 h by the user's ruling before X3's pre-registration
# (docs/presubmission/round4/DECISIONS.md#F1-x3-cap), after the first probe projected 23.83 h at three seeds.
CAP_X3_H, CAP_X4_H, CAP_TOTAL_H = 24.0, 10.0, 32.0
PROBE_DIR = os.path.join(R.REPO_ROOT, "runs", "timing_probe_round4")
OUT = os.path.join(R.RESULTS, "round4_queue_timing.json")
QUEUE = os.path.join(R.REPO_ROOT, "runs", "queue_round4.txt")
PY = sys.executable


def _run(cmd, log):
    with open(log, "w") as f:
        rc = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, cwd=R.REPO_ROOT).returncode
    assert rc == 0, f"probe exited {rc}; see {R.rel(log)}"


def _finite(curves):
    return all(math.isfinite(x) for v in curves.values() for x in v)


def probe_rwm(arm):
    cmd = [PY, os.path.join(R.REPO_ROOT, "scripts", "step5_train.py"), "--arm", arm, "--seed", "0",
           "--iters", str(PROBE_ITERS), "--holdout", ",".join(map(str, PROBE_FOLD)), "--out-dir", PROBE_DIR]
    _run(cmd, os.path.join(PROBE_DIR, f"probe_x3_arm{arm}.log"))
    a = json.load(open(os.path.join(PROBE_DIR, f"x3_run_arm{arm}_ho{''.join(map(str, PROBE_FOLD))}_seed0.json")))
    c = a["collapse"]
    first, last = c[0], c[-1]
    assert first["iter"] == 0 and last["iter"] == PROBE_ITERS - 1
    assert a["hyperparameters"]["holdout_episodes"] == list(PROBE_FOLD)
    return {"kind": f"x3_arm{arm}", "fold": list(PROBE_FOLD),
            "steady_s_per_iter": (last["wall_clock_s"] - first["wall_clock_s"]) / (last["iter"] - first["iter"]),
            "probe_wall_clock_s": a["wall_clock_s"], "n_train_windows": a["hyperparameters"]["n_train_windows"],
            "losses_finite": _finite(a["curves"])}


def probe_baseline(arch, spec):
    cmd = [PY, os.path.join(R.REPO_ROOT, "scripts", "train_baseline.py"), "--arch", arch, "--regime", "ar",
           "--spec", spec, "--seed", "0", "--iters", str(PROBE_ITERS), "--out-dir", PROBE_DIR]
    _run(cmd, os.path.join(PROBE_DIR, f"probe_{arch}_ar_{spec}.log"))
    a = json.load(open(os.path.join(PROBE_DIR, f"baseline_run_{arch}_ar_{spec}_seed0.json")))
    w = a["wall_clock_log"]
    first, last = w[0], w[-1]
    assert first["iter"] == 0 and last["iter"] == PROBE_ITERS - 1
    return {"kind": f"{arch}_ar_{spec}", "steady_s_per_iter": (last["wall_clock_s"] - first["wall_clock_s"])
            / (last["iter"] - first["iter"]), "probe_wall_clock_s": a["wall_clock_s"],
            "n_params": a["hyperparameters"]["n_params"], "losses_finite": _finite(a["curves"])}


def queue_lines(x3_seeds, x4_seeds):
    lines = []
    for s in SEEDS:
        if s in x3_seeds:
            lines.append(f"# --- rule X3, seed {s}: Arm A and Arm B, each fold held out in turn")
            for fold in FOLDS:
                f = "".join(map(str, fold))
                for arm in ("A", "B"):
                    lines.append(f"x3_{arm}_{f}_s{s} x3-{arm}-{f} 32 8 {s} {ITERS}")
        if s in x4_seeds:
            lines.append(f"# --- rule X4, seed {s}: the parameter-matched baselines, autoregressive")
            for arch in X4_ARCHS:
                lines.append(f"x4_{arch}_s{s} {arch}-ar-matched 32 8 {s} {ITERS}")
    return lines


def write_queue(x3_seeds, x4_seeds):
    assert not os.path.exists(QUEUE), f"{R.rel(QUEUE)} exists; the queue is written once"
    lines = queue_lines(x3_seeds, x4_seeds)
    with open(QUEUE, "w") as f:
        f.write("# ROUND 4 training queue (rules X3 and X4). One run per line: id arch M N seed iterations.\n"
                "# Written by scripts/round4_queue_timing.py from results/round4_queue_timing.json.\n")
        f.write("\n".join(lines) + "\n")
    print(f"  wrote {R.rel(QUEUE)}: {sum(1 for l in lines if not l.startswith('#'))} runs")


def queue_from_record():
    t = json.load(open(OUT))
    assert not t["blocked"], "the record is BLOCKED: nothing may be queued"
    write_queue(t["x3"]["seeds"], t["x4"]["seeds"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-queue", action="store_true")
    ap.add_argument("--queue-from-record", action="store_true")
    args = ap.parse_args()
    if args.queue_from_record:
        return queue_from_record()
    if os.path.isdir(PROBE_DIR):
        shutil.rmtree(PROBE_DIR)
    os.makedirs(PROBE_DIR)
    load_before = os.getloadavg()
    t0 = time.time()
    probes = {p["kind"]: p for p in [probe_rwm("A"), probe_rwm("B")]
              + [probe_baseline(a, s) for a in X4_ARCHS for s in ("matched", "s7")]}
    probe_minutes = (time.time() - t0) / 60
    load_after = os.getloadavg()
    assert all(p["losses_finite"] for p in probes.values()), "a probe's loss went non-finite"

    cal = {}
    for arm in ("A", "B"):
        full = [json.load(open(os.path.join(R.RESULTS, f"step5_arm{arm}_seed{s}.json")))["wall_clock_s"] for s in SEEDS]
        st = probes[f"x3_arm{arm}"]["steady_s_per_iter"]
        cal[f"x3_arm{arm}"] = {"finished_runs": [f"results/step5_arm{arm}_seed{s}.json" for s in SEEDS],
                               "finished_wall_clock_s": full, "probe_steady_s_per_iter": st,
                               "factor": (sum(full) / len(full)) / (st * ITERS)}
    for arch in X4_ARCHS:
        full = [json.load(open(os.path.join(R.RESULTS, f"baseline_run_{arch}_ar_s7_seed{s}.json")))["wall_clock_s"]
                for s in SEEDS]
        st = probes[f"{arch}_ar_s7"]["steady_s_per_iter"]
        cal[f"{arch}_ar_matched"] = {"finished_runs": [f"results/baseline_run_{arch}_ar_s7_seed{s}.json" for s in SEEDS],
                                     "finished_wall_clock_s": full, "calibration_probe": f"{arch}_ar_s7",
                                     "probe_steady_s_per_iter": st, "factor": (sum(full) / len(full)) / (st * ITERS)}
    per_run_h = {"x3_armA": cal["x3_armA"]["factor"] * probes["x3_armA"]["steady_s_per_iter"] * ITERS / 3600,
                 "x3_armB": cal["x3_armB"]["factor"] * probes["x3_armB"]["steady_s_per_iter"] * ITERS / 3600}
    for arch in X4_ARCHS:
        per_run_h[f"{arch}_ar_matched"] = (cal[f"{arch}_ar_matched"]["factor"]
                                           * probes[f"{arch}_ar_matched"]["steady_s_per_iter"] * ITERS / 3600)
    x3_seed_h = len(FOLDS) * (per_run_h["x3_armA"] + per_run_h["x3_armB"])
    x4_seed_h = sum(per_run_h[f"{a}_ar_matched"] for a in X4_ARCHS)
    x3_full, x4_full = x3_seed_h * len(SEEDS), x4_seed_h * len(SEEDS)
    x3_seeds = SEEDS if x3_full <= CAP_X3_H else FALLBACK_SEEDS
    x4_seeds = SEEDS if x4_full <= CAP_X4_H else FALLBACK_SEEDS
    x3_h, x4_h = x3_seed_h * len(x3_seeds), x4_seed_h * len(x4_seeds)
    blocked = []
    if x3_h > CAP_X3_H:
        blocked.append(f"X3 projects {x3_h:.2f} h at seeds {list(x3_seeds)}, over its {CAP_X3_H:g} h cap")
    if x4_h > CAP_X4_H:
        blocked.append(f"X4 projects {x4_h:.2f} h at seeds {list(x4_seeds)}, over its {CAP_X4_H:g} h cap")
    if x3_h + x4_h > CAP_TOTAL_H:
        blocked.append(f"the queue projects {x3_h + x4_h:.2f} h, over the {CAP_TOTAL_H:g} h total cap (ruling W10)")

    print("=" * 92)
    print("ROUND 4 TIMING PROBE -- 20 iterations each, projected against the caps")
    print("=" * 92)
    for k, p in probes.items():
        print(f"  {k:<26} steady {p['steady_s_per_iter']:.4f} s/iter  (probe {p['probe_wall_clock_s']:.1f} s)")
    for k, c in cal.items():
        print(f"  calibration {k:<22} finished runs {', '.join(f'{x / 3600:.2f}' for x in c['finished_wall_clock_s'])} h"
              f" -> factor {c['factor']:.3f}")
    for k, v in per_run_h.items():
        print(f"  projected {k:<24} {v:.3f} h per run")
    print(f"  X3: {x3_full:.2f} h at 3 seeds (cap {CAP_X3_H:g}) -> seeds {list(x3_seeds)}, {x3_h:.2f} h")
    print(f"  X4: {x4_full:.2f} h at 3 seeds (cap {CAP_X4_H:g}) -> seeds {list(x4_seeds)}, {x4_h:.2f} h")
    print(f"  total {x3_h + x4_h:.2f} h (cap {CAP_TOTAL_H:g})" + ("" if not blocked else "  BLOCKED: " + "; ".join(blocked)))

    out = {"rules": ["X3", "X4"], "probe_iterations": PROBE_ITERS, "iterations": ITERS, "probes": probes,
           "calibration": cal, "calibration_what": "factor = mean wall_clock_s of finished 2,500-iteration runs of "
           "the same kind / (2,500 x today's probe of that kind); projected per run = factor x probe x 2,500",
           "projected_h_per_run": per_run_h,
           "x3": {"cap_h": CAP_X3_H, "projected_h_three_seeds": x3_full, "seeds": list(x3_seeds),
                  "fallback_applied": x3_seeds != SEEDS, "projected_h": x3_h, "folds": [list(f) for f in FOLDS],
                  "n_runs": 2 * len(FOLDS) * len(x3_seeds)},
           "x4": {"cap_h": CAP_X4_H, "projected_h_three_seeds": x4_full, "seeds": list(x4_seeds),
                  "fallback_applied": x4_seeds != SEEDS, "projected_h": x4_h, "archs": list(X4_ARCHS),
                  "n_runs": len(X4_ARCHS) * len(x4_seeds)},
           "cap_total_h": CAP_TOTAL_H, "projected_total_h": x3_h + x4_h, "blocked": blocked,
           "queue": queue_lines(x3_seeds, x4_seeds), "probe_wall_minutes": probe_minutes,
           "loadavg_before": list(load_before), "loadavg_after": list(load_after),
           "threads": "none set, as every existing run (FILE_MAP.md §5)"}
    json.dump(out, open(OUT, "w"), indent=2)
    print(f"  wrote {R.rel(OUT)}")
    if blocked:
        sys.exit(2)
    if args.write_queue:
        write_queue(x3_seeds, x4_seeds)


if __name__ == "__main__":
    main()
