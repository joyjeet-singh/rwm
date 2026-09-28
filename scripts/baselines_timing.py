"""
Rules M-75 and M-76 -- the timing probe for the architecture baselines, the projection against
PLAN Appendix C's 20 CPU-hour cap, and the queue lines, before any baseline run.

Every baseline (MLP, RSSM, transformer x regimes tf, ar x specs s7, matched) is run for 20
iterations, and so is RWM's centre (32, 8) through step5_train.py's --sweep path as the
calibration point, exactly as scripts/mn_sweep_timing.py calibrates the sweep. These probes
run while the M-74 sweep trains, so every probe is slowed by the same contention; the
calibration factor (the mean recorded wall_clock_s of Arm A seeds 0-2 over 2,500 x the
centre probe's steady cost) carries that contention through, and it also carries RWM's
checkpoint evaluations, which the baselines do not run -- so the projection is conservative.

THE CAP, as the rules state it:
  * the Table S7 arms of both rules govern and are never dropped: if they project above
    20 CPU-hours, S2b stops for the user (BLOCKED), and nothing is queued;
  * the parameter-matched variants are queued only if EVERY baseline run, of both specs and
    both rules, projects within the cap; otherwise none of them is;
  * a probe that diverges or produces a non-finite loss is BLOCKED with its evidence.

Writes results/baselines_timing.json and, with --write-queue, appends the runs to
runs/queue.txt after the sweep: governing first (M-75 then M-76, each in priority order
MLP, RSSM, transformer, seeds 0-2), then the matched variants if they fit.
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

ARCHS = ("mlp", "rssm", "transformer")          # the rules' priority order
REGIMES = ("tf", "ar")                          # M-75, then M-76
SPECS = ("s7", "matched")
SEEDS = (0, 1, 2)
PROBE_ITERS, ITERS, CAP_H = 20, 2500, 20.0   # PLAN Appendix C: baselines <= 20 CPU-hours
PROBE_DIR = os.path.join(R.REPO_ROOT, "runs", "baselines_probe")


def steady(log):
    first, last = log[0], log[-1]
    assert first["iter"] == 0 and last["iter"] == PROBE_ITERS - 1
    return (last["wall_clock_s"] - first["wall_clock_s"]) / (last["iter"] - first["iter"])


def run(cmd, log):
    with open(log, "w") as f:
        return subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, cwd=R.REPO_ROOT).returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-queue", action="store_true")
    args = ap.parse_args()
    if os.path.isdir(PROBE_DIR):
        shutil.rmtree(PROBE_DIR)
    os.makedirs(PROBE_DIR)
    py = sys.executable
    t0 = time.time()

    rc = run([py, "scripts/step5_train.py", "--arm", "A", "--seed", "0", "--iters",
              str(PROBE_ITERS), "--sweep", "--history", "32", "--forecast", "8", "--out-dir",
              PROBE_DIR], os.path.join(PROBE_DIR, "centre.log"))
    assert rc == 0, "centre probe failed"
    c = json.load(open(os.path.join(PROBE_DIR, "mn_sweep_run_M32_N8_seed0.json")))
    centre = steady([{"iter": x["iter"], "wall_clock_s": x["wall_clock_s"]} for x in c["collapse"]])
    full = [json.load(open(os.path.join(R.RESULTS, f"step5_armA_seed{s}.json")))["wall_clock_s"]
            for s in SEEDS]
    factor = (sum(full) / len(full)) / (centre * ITERS)

    rows, blocked = [], []
    for spec in SPECS:
        for regime in REGIMES:
            for arch in ARCHS:
                name = f"{arch}_{regime}_{spec}"
                rc = run([py, "scripts/train_baseline.py", "--arch", arch, "--regime", regime,
                          "--spec", spec, "--seed", "0", "--iters", str(PROBE_ITERS),
                          "--out-dir", PROBE_DIR], os.path.join(PROBE_DIR, f"{name}.log"))
                if rc != 0:
                    blocked.append(f"{name}: probe exited {rc}")
                    continue
                a = json.load(open(os.path.join(PROBE_DIR, f"baseline_run_{name}_seed0.json")))
                finite = all(math.isfinite(x) for v in a["curves"].values() for x in v)
                if not finite:
                    blocked.append(f"{name}: non-finite loss in the probe")
                s = steady(a["wall_clock_log"])
                rows.append({"arch": arch, "regime": regime, "spec": spec,
                             "governs": spec == "s7", "steady_s_per_iter": s,
                             "projected_h_per_run": factor * s * ITERS / 3600,
                             "projected_h_3_seeds": 3 * factor * s * ITERS / 3600,
                             "probe_losses_finite": finite,
                             "probe_first_total": a["curves"]["total"][0],
                             "probe_last_total": a["curves"]["total"][-1],
                             "n_params": a["hyperparameters"]["n_params"]})
    gov_h = sum(r["projected_h_3_seeds"] for r in rows if r["governs"])
    all_h = sum(r["projected_h_3_seeds"] for r in rows)
    if gov_h > CAP_H:
        blocked.append(f"the Table S7 arms project {gov_h:.2f} CPU-hours, above the "
                       f"{CAP_H:.0f}-hour cap; no baseline may be dropped (PLAN S2b)")
    matched_fit = all_h <= CAP_H
    queued = [[r["arch"], r["regime"], r["spec"]] for r in rows
              if r["governs"] or matched_fit] if not blocked else []

    print("=" * 96)
    print("BASELINES TIMING PROBE — 20 iterations each, calibrated as the sweep's, against the cap")
    print("=" * 96)
    print(f"  centre probe {centre:.3f} s/iter (contended); factor {factor:.3f}")
    for r in rows:
        print(f"  {r['arch']:<12} {r['regime']} {r['spec']:<8} {r['steady_s_per_iter']:.3f} s/iter "
              f"-> {r['projected_h_per_run']:.2f} h/run, {r['projected_h_3_seeds']:.2f} h for 3 seeds"
              f"  losses {r['probe_first_total']:.2f} -> {r['probe_last_total']:.2f}")
    print(f"  Table S7 (governing): {gov_h:.2f} h; all specs: {all_h:.2f} h; cap {CAP_H:.0f} h; "
          f"matched variants {'QUEUED' if matched_fit and not blocked else 'NOT RUN'}")
    for b in blocked:
        print(f"  BLOCKED: {b}")
    out = {"rules": ["M-75", "M-76"], "probe_iterations": PROBE_ITERS,
           "calibration": {"centre_probe_s_per_iter": centre,
                           "centre_full_runs_wall_clock_s": full, "factor": factor,
                           "note": "probes ran while the M-74 sweep trained; the factor carries "
                                   "the contention and RWM's checkpoint evaluations, so the "
                                   "projection is conservative"},
           "configs": rows, "cap_hours": CAP_H, "projected_governing_hours": gov_h,
           "projected_all_hours": all_h, "matched_variants_fit": matched_fit,
           "queued": queued, "blocked": blocked, "probe_wall_minutes": (time.time() - t0) / 60}
    json.dump(out, open(os.path.join(R.RESULTS, "baselines_timing.json"), "w"), indent=2)
    print("  wrote results/baselines_timing.json")
    if blocked:
        sys.exit(3)
    if args.write_queue:
        qp = os.path.join(R.REPO_ROOT, "runs", "queue.txt")
        text = open(qp).read()
        assert "bl_" not in text, "baseline lines are already queued"
        with open(qp, "a") as f:
            f.write("# --- rules M-75 (tf) and M-76 (ar): architecture baselines, Table S7 first\n")
            for arch, regime, spec in queued:
                for s in SEEDS:
                    f.write(f"bl_{arch}_{regime}_{spec}_s{s} {arch}-{regime}-{spec} 32 8 {s} {ITERS}\n")
        print(f"  appended {len(queued) * len(SEEDS)} runs to runs/queue.txt")


if __name__ == "__main__":
    main()
