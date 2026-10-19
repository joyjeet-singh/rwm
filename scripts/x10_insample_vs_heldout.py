"""
Rule X10 (round 5; PRE-REGISTERED, inference only) -- does measuring on training data flatter an ensemble's calibration?

The rule is docs/presubmission/round5/PROTOCOLS.md §3; this docstring is a summary of it. It never re-opens a
discharged rule, and nothing it returns changes a verdict.

MODELS. Arm A's ensemble-5 arms, seeds 0-2, 2,500 iterations (runs/armA_seed<s>_ens5/weights_2500.pt), loaded as
task_d3_ens5.py:117-119. Their training split is recorded, so X10 does not depend on PREMISES P20.
ARENAS. In-sample: the default split's training episodes {0, 2, 3, 4, 5, 6, 7, 9}, 16 non-overlapping 400-row
trajectories, one batch of 16. Held-out: the pair {1, 8}, 4 trajectories, one batch of 4, exactly task_d3_ens5.py:86-95.
MEAN mode only (rollout_uncertainty, action_offset = 1).
STATISTIC. Per seed, arena and horizon h in {1, 8, 32, 100, 128, 368}: rho, +-1 and +-2 sigma coverage of the
epistemic spread, by task_d3_ens5.py:243-278's lines (x11a_fold_ens5_calibration.calibration, the frozen verbatim
copy). Q_s(h) = rho_in,s / rho_out,s. Pooled as task_d3_ens5 pools: rho_arena = mean over seeds; Q = rho_in / rho_out.
INTERVAL for Q: rng = default_rng(0); I_in = rng.integers(0, 16, (20000, 16)), then I_out = rng.integers(0, 4, (20000, 4));
in each draw each arena's rho* is task_d3_ens5._ci's ratio of seed-mean per-trajectory means; Q* = rho*_in / rho*_out;
2.5th and 97.5th percentiles of the finite draws.
VERDICT at h = 1: IN-SAMPLE FLATTERS (Q_s < 1 for all three seeds and the interval below 1); IN-SAMPLE IS WORSE (Q_s > 1
for all three and the interval above 1); MIXED otherwise. h = 100: the label it would carry.
CAVEAT (locked): the arenas differ in episodes as well as in training status, and per-episode difficulty varies
threefold (D-12), so this bounds the in-sample effect rather than isolating it.
ASSERTIONS, before any in-sample statistic: (1) the held-out arm reproduces task_d3_ens5.json calibration at every
horizon, intervals included, relative 1e-6; (2) each arm's run record trained on the in-sample episodes and held out
[1, 8]; (3) the in-sample arena has 16 trajectories, n_independent 16, two per training episode, disjoint from the
held-out starts, their union all ten episodes' 20; (4) on the in-sample batch the harness agrees with our trainer's
forward to < 1e-5.

  --assert-only   (1)-(4) only; prints pass or fail; no in-sample statistic.
Writes results/x10_insample_vs_heldout.json. Run from the repository root.
"""
import argparse
import json
import os
import statistics
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import torch  # noqa: E402
import rwm_data as R  # noqa: E402
import rollout_eval as E  # noqa: E402
import rwm_metrics as MET  # noqa: E402
import x11_common as C  # noqa: E402
import x11a_fold_ens5_calibration as XA  # noqa: E402

RULE_ID = "M-102"
FROZEN = ("scripts/x10_insample_vs_heldout.py", "scripts/x11a_fold_ens5_calibration.py", "scripts/x11_common.py")
HORIZONS = (1, 8, 32, 100, 128, 368)
START, LEN, N_BOOT = E.START_STEP, 400, 20000
TOL_REPRO, TOL_HARNESS = 1e-6, 1e-5
LABELS = ("IN-SAMPLE FLATTERS", "IN-SAMPLE IS WORSE", "MIXED")
OUT = os.path.join(R.RESULTS, "x10_insample_vs_heldout.json")
MODULES = FROZEN + ("scripts/task_d3_ens5.py", "src/score_reference.py", "src/rwm_model.py", "src/rwm_data.py",
                    "src/rwm_metrics.py", "src/rollout_eval.py")
CAVEAT = ("the arenas differ in episodes as well as in training status, and per-episode difficulty varies threefold "
          "(D-12), so this bounds the in-sample effect rather than isolating it. X11, if run, measures it with every "
          "episode in both roles.")


def rel_diff(got, want):
    if isinstance(want, dict):
        return max([rel_diff(got.get(k) if isinstance(got, dict) else None, v) for k, v in want.items()] or [0.0])
    if isinstance(want, list):
        if not isinstance(got, list) or len(got) != len(want):
            return float("inf")
        return max([rel_diff(g, w) for g, w in zip(got, want)] or [0.0])
    if isinstance(want, (bool, str)) or want is None:
        return 0.0 if got == want else float("inf")
    return abs(float(got) - float(want)) / max(1e-12, abs(float(want)))


def roll(m, st, ac):
    pred, _, epi, _, _ = m.rollout_uncertainty(st.clone(), ac, START, action_offset=1)
    return pred, {"err": (pred - st).abs().numpy().astype(np.float64), "epi": epi.numpy().astype(np.float64)}


def label(qs, ci):
    if all(q < 1 for q in qs) and ci[1] < 1:
        return LABELS[0]
    if all(q > 1 for q in qs) and ci[0] > 1:
        return LABELS[1]
    return LABELS[2]


def run(assert_only):
    t0 = time.perf_counter()
    frozen = None if assert_only else C.require_prereg(RULE_ID, FROZEN, OUT)
    cfg, data, ep = C.data()
    split = E.make_split(seed=0, strat_path=C.STRAT, verbose=False)
    train, hold = sorted(split["train_episodes"]), list(split["holdout_episodes"])
    s_out = MET.non_overlapping_starts(ep, hold, LEN)
    s_in = MET.non_overlapping_starts(ep, train, LEN)
    s_all = MET.non_overlapping_starts(ep, list(range(R.N_EPISODES)), LEN)
    st_o, ac_o = C.tensors(s_out)
    st_i, ac_i = C.tensors(s_in)
    a = {}
    # (2) the recorded training split
    recs = {s: json.load(open(C.ens5_record((1, 8), s)))["hyperparameters"] for s in C.ENS5_SEEDS}
    a["2"] = {"pass": all(sorted(r["train_episodes"]) == train and sorted(r["holdout_episodes"]) == [1, 8]
                          for r in recs.values()), "train_episodes": train, "holdout_episodes": sorted(hold)}
    # (3) the arenas
    per_ep = {e: sum(1 for s in s_in if ep[s] == e) for e in train}
    a["3"] = {"pass": bool(len(s_in) == 16 and int(MET.n_independent(s_in, LEN)) == 16 and all(v == 2 for v in per_ep.values())
                           and not set(s_in) & set(s_out) and sorted(list(s_in) + list(s_out)) == sorted(s_all)),
              "n_in": len(s_in), "n_out": len(s_out), "per_episode": {str(k): v for k, v in per_ep.items()}}
    # (1) held-out reproduction, and (4) the harness on the in-sample batch
    held, ins, hd, sha = {}, {}, {}, {}
    for s in C.ENS5_SEEDS:
        w = C.ens5_weights((1, 8), s)
        sha[f"s{s}"] = C.sha256(w)
        m, sd = C.load_ens5(w)
        _, held[s] = roll(m, st_o, ac_o)
        p_in, ins[s] = roll(m, st_i, ac_i)
        hd[s] = float((C.harness_check(sd, st_i, ac_i) - p_in).abs().max())
    got = XA.strip(XA.calibration(held, np.random.default_rng(0).integers(0, 4, (N_BOOT, 4))))
    want = json.load(open(os.path.join(R.RESULTS, "task_d3_ens5.json")))["calibration"]
    d1 = rel_diff(got, want)
    a["1"] = {"pass": bool(d1 <= TOL_REPRO), "max_rel_diff": d1, "tolerance": TOL_REPRO,
              "against": "results/task_d3_ens5.json calibration, intervals included"}
    a["4"] = {"pass": bool(max(hd.values()) < TOL_HARNESS), "max_abs_diff": {str(k): v for k, v in hd.items()},
              "tolerance": TOL_HARNESS}
    for k in ("1", "2", "3", "4"):
        print(f"  assertion ({k}): {'PASS' if a[k]['pass'] else 'FAIL'}  "
              f"{ {kk: vv for kk, vv in a[k].items() if kk not in ('pass', 'against')} }")
    ok = all(v["pass"] for v in a.values())
    if assert_only:
        sys.exit(0 if ok else 1)
    if not ok:
        C.blocked(OUT, "an assertion failed", assertions=a)
    for s in C.ENS5_SEEDS:
        if not (np.isfinite(ins[s]["err"][:, START:]).all() and np.isfinite(ins[s]["epi"][:, START:]).all()):
            C.blocked(OUT, f"non-finite in-sample rollout, seed {s}")

    # ---------------- the reading ----------------
    rng = np.random.default_rng(0)
    I_in = rng.integers(0, 16, (N_BOOT, 16))
    I_out = rng.integers(0, 4, (N_BOOT, 4))
    cal_in = XA.calibration(ins, I_in)
    cal_out = XA.calibration(held, I_out)
    q = {}
    for h in HORIZONS:
        ci_, co_ = cal_in[str(h)], cal_out[str(h)]
        qs = {str(s): ci_["per_seed"][j]["ratio_err_over_sigma"] / co_["per_seed"][j]["ratio_err_over_sigma"]
              for j, s in enumerate(C.ENS5_SEEDS)}
        pin, pout = ci_["_per_traj"], co_["_per_traj"]
        rin = pin["err"].mean(0)[I_in].mean(1) / pin["sig"].mean(0)[I_in].mean(1)
        rout = pout["err"].mean(0)[I_out].mean(1) / pout["sig"].mean(0)[I_out].mean(1)
        qd = rin / rout
        qd = qd[np.isfinite(qd)]
        ci = [float(np.percentile(qd, 2.5)), float(np.percentile(qd, 97.5))]
        q[str(h)] = {"q": ci_["mean_ratio"] / co_["mean_ratio"], "q_ci": ci, "q_per_seed": qs, "n_boot_finite": int(len(qd)),
                     "rho_in": ci_["mean_ratio"], "rho_out": co_["mean_ratio"],
                     "cov1_in": ci_["mean_cov1"], "cov1_out": co_["mean_cov1"],
                     "cov2_in": ci_["mean_cov2"], "cov2_out": co_["mean_cov2"],
                     "label_it_would_carry": label(list(qs.values()), ci)}
    out = {"rule": "X10", "ledger": RULE_ID, "frozen_sha256": frozen, "script": "scripts/x10_insample_vs_heldout.py",
           "script_sha256": C.sha256("scripts/x10_insample_vs_heldout.py"), "exploratory": True,
           "never_reopens": "any discharged rule; nothing here changes a verdict",
           "design": {"models": "Arm A ensemble-5, seeds 0-2, 2,500 iterations", "in_sample_episodes": train,
                      "held_out_episodes": sorted(hold), "n_in": 16, "n_out": 4, "mode": "MEAN",
                      "in_sample_starts": [int(x) for x in s_in], "held_out_starts": [int(x) for x in s_out],
                      "interval": "independent bootstraps of each arena from one default_rng(0): I_in (20000, 16) then I_out (20000, 4)",
                      "horizons": list(HORIZONS)},
           "assertions": a, "calibration_in": XA.strip(cal_in), "calibration_out": XA.strip(cal_out), "q": q,
           "verdict": {"h": 1, "label": q["1"]["label_it_would_carry"], "q": q["1"]["q"], "q_ci": q["1"]["q_ci"],
                       "q_per_seed": q["1"]["q_per_seed"]},
           "label_h100": q["100"]["label_it_would_carry"], "caveat": CAVEAT, "weights_sha256": sha,
           "code_sha256": {p: C.sha256(p) for p in MODULES},
           "git_head": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
           "timing": {"wall_clock_s": time.perf_counter() - t0, "torch_threads": torch.get_num_threads(),
                      "cpu_count": os.cpu_count()}}
    json.dump(out, open(OUT, "w"), indent=1)
    print(f"  X10: Q(h=1) = {q['1']['q']:.4f} {q['1']['q_ci']} per seed {q['1']['q_per_seed']} -> {out['verdict']['label']}")
    print(f"  wrote {R.rel(OUT)}")


def main():
    os.chdir(C.ROOT)
    ap = argparse.ArgumentParser()
    ap.add_argument("--assert-only", action="store_true")
    run(ap.parse_args().assert_only)


if __name__ == "__main__":
    main()
