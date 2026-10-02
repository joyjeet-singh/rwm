"""
Round 2, N3 parts 1-3 (post hoc) -- the M/N sweep compared at equal training compute.

PLAN round2 Annex 1, N3. Nothing here is pre-registered; M-74's verdict (M-77) is not
re-opened, no Holm step is applied, and no verdict is returned.

PART 1, relative cost per iteration.
  sweep      steady_s_per_iter from results/mn_sweep_timing.json over the centre probe's. The
             preflight (round2 PREFLIGHT.md, P3) found every one of those probes uncontended, so
             none is re-probed.
  baselines  their round-1 probes ran while the sweep trained (contended), so the six Table S7
             families are re-probed here for 50 iterations each through train_baseline.py,
             beside a 50-iteration centre probe through step5_train.py --sweep in the same idle
             sitting; steady seconds per iteration by baselines_timing.steady (first to last
             iteration of the run's wall-clock log). Also the time per rollout step at inference
             for each family and for RWM: model.rollout on the held-out arena (4 windows, 368
             forecast steps), median of 3 timed calls, divided by 368.
PART 2, the centre at more compute. Arm A's 10k runs (seeds 0-2) at 2,500, 5,000, 7,500 and
  10,000 iterations, scored with mn_sweep_eval.score on its held-out and in-sample arenas.
  ASSERTED: the 2,500 checkpoint reproduces the sweep's centre row (per-trajectory relative-L1
  at every horizon and arena, seeds 0-2) to 1e-6, as the 10k runs replicate the 2,500 runs.
PART 3, the reading. For (32, 16), (32, 32), (8, 8) and (2, 8), and k in {2,500, 5,000,
  10,000}: per-trajectory differences of 3-seed means, err(config @ 2,500) - err(centre @ k),
  relative-L1, h = 100 and 368, with M-74's statistic and interval (p5_sweep_power.boot_p and
  boot_ci, exact over 256 resamples, held-out n = 4); the in-sample arena alongside with the
  verdict's Monte Carlo draws (20,000, seed 0). Negative favours the configuration. Each
  comparison carries two compute ratios: the configuration's cost per iteration relative to
  the centre's, and its total training compute relative to the centre's at k.
  ANNEX 3's variant: (a) if, for the best neighbour at h = 368 (most negative M-74 D), the
  held-out interval of err(neighbour @ 2,500) - err(centre @ 5,000) excludes zero in the
  neighbour's favour; otherwise (b).

  python scripts/mn_compute_matched.py            # probes, then parts 2-3
  python scripts/mn_compute_matched.py --no-probe # reuse runs/round2_probe/ from an earlier run

Writes results/mn_compute_matched.json; probe runs under runs/round2_probe/ (gitignored).
"""
import argparse
import json
import os
import shutil
import statistics
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, os.pardir, "src"))
import numpy as np  # noqa: E402
import torch  # noqa: E402

import baselines as BL  # noqa: E402
import baselines_timing as BT  # noqa: E402
import mn_sweep_eval as MN  # noqa: E402
import p5_sweep_power as P5  # noqa: E402
import rollout_eval as E  # noqa: E402
import rwm_data as R  # noqa: E402
import rwm_metrics as MET  # noqa: E402
import rwm_model as M  # noqa: E402
import verdict_mn_sweep as VMN  # noqa: E402

PROBE_ITERS = 50
PROBE_DIR = os.path.join(R.REPO_ROOT, "runs", "round2_probe")
CONFIGS = ((32, 16), (32, 32), (8, 8), (2, 8))
KS = (2500, 5000, 10000)
CKPTS = (2500, 5000, 7500, 10000)
SEEDS = ("0", "1", "2")
READ_H = ("100", "368")
TOL = 1e-6


def probes():
    """Part 1's re-probes, on an idle machine, through the training scripts' own --iters path."""
    if os.path.isdir(PROBE_DIR):
        shutil.rmtree(PROBE_DIR)
    os.makedirs(PROBE_DIR)
    py = sys.executable
    BT.PROBE_ITERS = PROBE_ITERS                    # baselines_timing.steady asserts the probe length
    load_before = os.getloadavg()
    rc = BT.run([py, "scripts/step5_train.py", "--arm", "A", "--seed", "0", "--iters", str(PROBE_ITERS),
                 "--sweep", "--history", "32", "--forecast", "8", "--out-dir", PROBE_DIR],
                os.path.join(PROBE_DIR, "centre.log"))
    assert rc == 0, "centre probe failed"
    c = json.load(open(os.path.join(PROBE_DIR, "mn_sweep_run_M32_N8_seed0.json")))
    centre = BT.steady([{"iter": x["iter"], "wall_clock_s": x["wall_clock_s"]} for x in c["collapse"]])
    fams = {}
    for arch, regime, spec in [tuple(q) for q in json.load(open(os.path.join(R.RESULTS, "baselines_timing.json")))["queued"]]:
        name = f"{arch}_{regime}_{spec}"
        rc = BT.run([py, "scripts/train_baseline.py", "--arch", arch, "--regime", regime, "--spec", spec,
                     "--seed", "0", "--iters", str(PROBE_ITERS), "--out-dir", PROBE_DIR],
                    os.path.join(PROBE_DIR, f"{name}.log"))
        assert rc == 0, f"{name} probe failed"
        a = json.load(open(os.path.join(PROBE_DIR, f"baseline_run_{name}_seed0.json")))
        fams[name] = BT.steady(a["wall_clock_log"])
    return {"probe_iterations": PROBE_ITERS, "centre_steady_s_per_iter": centre, "baselines_steady_s_per_iter": fams,
            "loadavg_before": list(load_before), "loadavg_after": list(os.getloadavg()),
            "torch_threads": torch.get_num_threads()}


def rollout_step_time(model, data, cfg, starts, m):
    st, ac = MN.window_arrays(data, cfg, starts, m, 32)
    ts = []
    for _ in range(3):
        t0 = time.perf_counter()
        with torch.no_grad():
            model.rollout(torch.as_tensor(st).clone(), torch.as_tensor(ac), m, action_offset=1)
        ts.append(time.perf_counter() - t0)
    return statistics.median(ts) / MN.FORECAST


def three_seed(recs, arena, h):
    return np.mean([np.asarray(recs[s][arena][h]["l1"], dtype=np.float64) for s in SEEDS], 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-probe", action="store_true")
    args = ap.parse_args()

    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    data, ep = R.load_data(paths["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"), verbose=False)
    scale = MET.training_scale(data, ep, split["train_episodes"], cfg["state_data_mean"], cfg["state_data_std"])
    arenas = {"held_out": MN.arena(ep, split["holdout_episodes"], 32),
              "in_sample": MN.arena(ep, split["train_episodes"], 32)}
    ev = json.load(open(os.path.join(R.RESULTS, "mn_sweep_eval.json")))
    timing = json.load(open(os.path.join(R.RESULTS, "mn_sweep_timing.json")))
    assert arenas["held_out"]["starts"] == ev["arenas"]["held_out"]["starts"]

    # ---- part 1 -----------------------------------------------------------------------------
    centre_probe = timing["calibration"]["centre_probe"]["steady_s_per_iter"]
    sweep_cost = {f"M{c['M']}_N{c['N']}": {"steady_s_per_iter": c["steady_s_per_iter"],
                                           "relative_to_centre": c["steady_s_per_iter"] / centre_probe}
                  for c in timing["configs"]}
    sweep_cost["M32_N8"] = {"steady_s_per_iter": centre_probe, "relative_to_centre": 1.0}
    if args.no_probe:
        pr = json.load(open(os.path.join(PROBE_DIR, "probes.json")))
    else:
        pr = probes()
        json.dump(pr, open(os.path.join(PROBE_DIR, "probes.json"), "w"), indent=2)
    bl_cost = {k: {"steady_s_per_iter": v, "relative_to_same_sitting_centre": v / pr["centre_steady_s_per_iter"],
                   "relative_to_round1_centre_probe": v / centre_probe}
               for k, v in pr["baselines_steady_s_per_iter"].items()}

    step_time = {}
    m0 = M.build_from_config(cfg, ensemble_size=1)
    m0.load_state_dict(torch.load(MN.weights_path(32, 8, 0), map_location="cpu")["model_state_dict"], strict=True)
    m0.eval()
    step_time["rwm"] = rollout_step_time(m0, data, cfg, arenas["held_out"]["starts"], 32)
    for name in pr["baselines_steady_s_per_iter"]:
        arch, regime, spec = name.split("_")
        b = BL.build(arch, spec, cfg)
        b.load_state_dict(torch.load(os.path.join("runs", f"baseline_{name}_seed0", "weights_2500.pt"),
                                     map_location="cpu")["model_state_dict"], strict=True)
        b.eval()
        step_time[name] = rollout_step_time(b, data, cfg, arenas["held_out"]["starts"], 32)

    # ---- part 2 -----------------------------------------------------------------------------
    centre_k = {}
    for it in CKPTS:
        recs = {}
        for s in SEEDS:
            w = f"runs/armA_seed{s}_10k/weights_{it}.pt"
            assert os.path.exists(w), f"missing {w}"
            model = M.build_from_config(cfg, ensemble_size=1)
            model.load_state_dict(torch.load(w, map_location="cpu")["model_state_dict"], strict=True)
            model.eval()
            recs[s] = {"weights": w, **{a: MN.score(model, data, cfg, scale, arenas[a]["starts"], 32, 32) for a in arenas}}
        centre_k[str(it)] = recs
    d2 = max(abs(x - y) for s in SEEDS for a in arenas for h in map(str, MN.HORIZONS)
             for x, y in zip(centre_k["2500"][s][a][h]["l1"], ev["configs"]["M32_N8"]["seeds"][s][a][h]["l1"]))
    assert d2 < TOL, f"the 10k runs' 2,500 checkpoint does not reproduce the sweep's centre row: {d2}"

    # ---- part 3 -----------------------------------------------------------------------------
    mc = np.random.default_rng(VMN.MC_SEED).integers(0, 16, size=(VMN.MC_N, 16))
    readings = {}
    for m, n in CONFIGS:
        key = f"M{m}_N{n}"
        cseeds = ev["configs"][key]["seeds"]
        for k in KS:
            ratio = {"config_cost_per_iter_over_centre": sweep_cost[key]["relative_to_centre"],
                     "config_total_compute_over_centre_at_k": sweep_cost[key]["relative_to_centre"] * 2500 / k,
                     "centre_at_k_over_centre_at_2500": k / 2500}
            rec = {"config": key, "config_iterations": 2500, "centre_iterations": k, "compute_ratios": ratio}
            for h in READ_H:
                d = three_seed(cseeds, "held_out", h) - three_seed(centre_k[str(k)], "held_out", h)
                di = three_seed(cseeds, "in_sample", h) - three_seed(centre_k[str(k)], "in_sample", h)
                b = di[mc].mean(1)
                rec[f"h{h}"] = {"held_out": {"D": float(d.mean()), "per_traj": [float(x) for x in d],
                                             "ci95": P5.boot_ci(d), "p": P5.boot_p(d)},
                                "in_sample": {"D": float(di.mean()),
                                              "ci95": [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))],
                                              "p": float(min(1.0, 2 * min(np.mean(b <= 0), np.mean(b >= 0))))}}
            readings[f"{key}|centre@{k}"] = rec

    gov = json.load(open(os.path.join(R.RESULTS, "mn_sweep_verdict.json")))["governing"]["per_config"]
    best = min((c for c in gov if c in {f"M{m}_N{n}" for m, n in CONFIGS}), key=lambda c: gov[c]["D"])
    r5 = readings[f"{best}|centre@5000"]["h368"]["held_out"]
    variant = "a" if r5["ci95"][1] < 0 else "b"

    centre_rows = {it: {a: {h: float(np.mean(three_seed(centre_k[it], a, h))) for h in map(str, MN.HORIZONS)} for a in arenas}
                   for it in centre_k}
    out = {"purpose": "round 2 N3 (post hoc): the M/N sweep at equal training compute",
           "post_hoc": True,
           "never_reopens": "M-74's verdict (M-77) is unchanged; no Holm step, no verdict",
           "part1_relative_cost_per_iteration": {
               "sweep": sweep_cost, "sweep_source": "results/mn_sweep_timing.json (uncontended: round2 PREFLIGHT.md P3)",
               "baselines": bl_cost, "baselines_probe": pr,
               "inference_s_per_rollout_step": step_time,
               "inference_note": "model.rollout on the held-out arena (a batch of 4 windows), median of 3 calls / 368 steps"},
           "part2_centre_at_more_compute": {
               "runs": "runs/armA_seed{0,1,2}_10k/weights_{2500,5000,7500,10000}.pt, scored with mn_sweep_eval.score",
               "reproduces_sweep_centre_at_2500": {"max_abs_diff": d2, "tolerance": TOL},
               "three_seed_mean_l1": centre_rows,
               "per_seed": {it: {s: {a: {h: v[a][h]["l1"] for h in map(str, MN.HORIZONS)} for a in arenas}
                                 for s, v in recs.items()} for it, recs in centre_k.items()}},
           "part3_readings": {"statistic": "mean over trajectories of [3-seed mean err(config @ 2,500) - 3-seed mean err(centre @ k)], "
                                           "relative-L1; negative favours the configuration",
                              "interval": "held-out: p5_sweep_power.boot_ci / boot_p, exact 256; in-sample: Monte Carlo 20,000, seed 0",
                              "readings": readings},
           "annex3_variant": {"best_neighbour_at_h368": best, "its_M74_D": gov[best]["D"],
                              "neighbour_minus_centre_at_5000_h368_held_out": r5,
                              "variant": variant,
                              "rule": "(a) if that interval excludes zero in the neighbour's favour, otherwise (b)"},
           "section5_already_printed": "the centre at 10,000 on the same four trajectories (round2 PREFLIGHT.md P2): 0.3582 at h = 368, "
                                       "against (32, 32)'s 0.2987 at 2,500"}
    op = os.path.join(R.RESULTS, "mn_compute_matched.json")
    json.dump(out, open(op, "w"), indent=2)

    print("=" * 100)
    print("N3 (post hoc) — the sweep at equal training compute")
    print("=" * 100)
    print(f"  centre probe (round 1) {centre_probe:.3f} s/iter; same-sitting centre {pr['centre_steady_s_per_iter']:.3f} s/iter")
    for k_, v in sweep_cost.items():
        print(f"    {k_:<8} {v['relative_to_centre']:.2f}x")
    for k_, v in bl_cost.items():
        print(f"    {k_:<20} {v['steady_s_per_iter']:.3f} s/iter  {v['relative_to_same_sitting_centre']:.2f}x (same sitting)  "
              f"inference {1e3 * step_time[k_]:.2f} ms/step")
    print(f"    rwm inference {1e3 * step_time['rwm']:.2f} ms/step")
    print(f"  the 10k runs' 2,500 checkpoint reproduces the sweep's centre: max |diff| {d2:.2e}")
    for it, v in centre_rows.items():
        print(f"  centre @ {it:>5}  held-out rel-L1  h=100 {v['held_out']['100']:.4f}  h=368 {v['held_out']['368']:.4f}")
    for key_, r in readings.items():
        a = r["h368"]["held_out"]
        print(f"  {key_:<18} compute {r['compute_ratios']['config_total_compute_over_centre_at_k']:.2f}x  "
              f"h=368 D {a['D']:+.4f} [{a['ci95'][0]:+.4f}, {a['ci95'][1]:+.4f}]  h=100 D {r['h100']['held_out']['D']:+.4f}")
    print(f"  Annex 3 variant: ({variant}) — best neighbour {best}, vs centre @ 5,000 at h=368: {r5['D']:+.4f} {r5['ci95']}")
    print(f"  wrote {R.rel(op)}")


if __name__ == "__main__":
    main()
