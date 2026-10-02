"""
Rule X1, Part C (ledger M-80) -- the timing probe and the projection against the 10 CPU-hour cap,
before any variant trains.

Each variant (V1 = spec x1v1, V2 = spec x1v2; teacher-forced RSSM) is run for 20 iterations
through train_baseline.py, beside a 20-iteration centre probe through step5_train.py --sweep in
the same sitting, exactly as scripts/baselines_timing.py probes the baselines (its run() and
steady() are imported). Projected hours per 2,500-iteration run = factor x steady s/iter x 2,500,
where the factor is baselines_timing's calibration: the mean recorded wall_clock_s of Arm A seeds
0-2 over 2,500 x the same-sitting centre probe's steady cost.

  committed  the two seed-0 runs Part C queues now;
  worst      plus seeds 1-2 of every variant, as if both rescued on seed 0 (M-80).
M-80's cap is 10 projected CPU-hours. If the committed projection exceeds it, the session stops
BLOCKED and nothing is queued. Seeds 1-2 of a rescuing variant are queued only after its seed-0
reading, and only if the committed runs' measured hours plus theirs stay within the cap.

  python scripts/x1_partc_timing.py               # probe and project
  python scripts/x1_partc_timing.py --write-queue # and append the seed-0 runs to runs/queue_round2.txt

Writes results/x1_partc_timing.json; probe runs under runs/round2_x1probe/ (gitignored).
"""
import argparse
import json
import math
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, os.pardir, "src"))
import baselines_timing as BT  # noqa: E402
import rwm_data as R  # noqa: E402

CAP_H, ITERS, PROBE_ITERS = 10.0, 2500, 20
VARIANTS = {"V1": "x1v1", "V2": "x1v2"}
PROBE_DIR = os.path.join(R.REPO_ROOT, "runs", "round2_x1probe")
QUEUE = os.path.join(R.REPO_ROOT, "runs", "queue_round2.txt")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-queue", action="store_true")
    a = ap.parse_args()
    if os.path.isdir(PROBE_DIR):
        shutil.rmtree(PROBE_DIR)
    os.makedirs(PROBE_DIR)
    BT.PROBE_ITERS = PROBE_ITERS
    py = sys.executable
    load_before = os.getloadavg()
    assert BT.run([py, "scripts/step5_train.py", "--arm", "A", "--seed", "0", "--iters", str(PROBE_ITERS), "--sweep",
                   "--history", "32", "--forecast", "8", "--out-dir", PROBE_DIR], os.path.join(PROBE_DIR, "centre.log")) == 0
    c = json.load(open(os.path.join(PROBE_DIR, "mn_sweep_run_M32_N8_seed0.json")))
    centre = BT.steady([{"iter": x["iter"], "wall_clock_s": x["wall_clock_s"]} for x in c["collapse"]])
    full = [json.load(open(os.path.join(R.RESULTS, f"step5_armA_seed{s}.json")))["wall_clock_s"] for s in (0, 1, 2)]
    factor = (sum(full) / len(full)) / (centre * ITERS)
    rows = {}
    for v, spec in VARIANTS.items():
        name = f"rssm_tf_{spec}"
        assert BT.run([py, "scripts/train_baseline.py", "--arch", "rssm", "--regime", "tf", "--spec", spec, "--seed", "0",
                       "--iters", str(PROBE_ITERS), "--out-dir", PROBE_DIR], os.path.join(PROBE_DIR, f"{name}.log")) == 0, f"{v} probe failed"
        art = json.load(open(os.path.join(PROBE_DIR, f"baseline_run_{name}_seed0.json")))
        finite = all(math.isfinite(x) for vals in art["curves"].values() for x in vals)
        s = BT.steady(art["wall_clock_log"])
        rows[v] = {"spec": spec, "steady_s_per_iter": s, "projected_h_per_run": factor * s * ITERS / 3600,
                   "probe_losses_finite": finite}
    committed = sum(r["projected_h_per_run"] for r in rows.values())
    worst = committed + 2 * committed
    within = committed <= CAP_H and all(r["probe_losses_finite"] for r in rows.values())
    out = {"rule": "X1 (ledger M-80), Part C", "probe_iterations": PROBE_ITERS, "iterations": ITERS, "cap_hours": CAP_H,
           "calibration": {"centre_probe_steady_s_per_iter": centre, "arm_a_full_wall_clock_s": full, "factor": factor},
           "variants": rows, "projected_hours_committed_seed0_runs": committed,
           "projected_hours_worst_case_all_seeds": worst,
           "committed_within_cap": within,
           "loadavg_before": list(load_before), "loadavg_after": list(os.getloadavg()),
           "queued": [], "queue_file": "runs/queue_round2.txt"}
    if a.write_queue:
        assert within, "the committed projection exceeds the cap or a probe diverged: BLOCKED, nothing queued"
        lines = [f"x1_{spec}_s0 rssm-tf-{spec} 32 8 0 {ITERS}" for spec in VARIANTS.values()]
        existing = open(QUEUE).read().split("\n") if os.path.exists(QUEUE) else []
        with open(QUEUE, "a") as f:
            for ln in lines:
                if ln not in existing:
                    f.write(ln + "\n")
        out["queued"] = lines
    json.dump(out, open(os.path.join(R.RESULTS, "x1_partc_timing.json"), "w"), indent=2)
    print(f"  centre probe {centre:.3f} s/iter; factor {factor:.3f}")
    for v, r in rows.items():
        print(f"  {v} ({r['spec']}): {r['steady_s_per_iter']:.3f} s/iter -> {r['projected_h_per_run']:.2f} h per run; finite {r['probe_losses_finite']}")
    print(f"  projected: seed-0 runs {committed:.2f} h; worst case, all seeds {worst:.2f} h; cap {CAP_H} h -> "
          f"{'WITHIN' if within else 'EXCEEDS: BLOCKED'}")
    if out["queued"]:
        print(f"  appended to runs/queue_round2.txt: {out['queued']}")


if __name__ == "__main__":
    main()
