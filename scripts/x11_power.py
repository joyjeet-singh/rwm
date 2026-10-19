"""
X11 (round 5, GT1 item 1): what M-43's and M-44's criteria can detect at n_independent = 20,
computed with the code that computed it at n = 4, BEFORE any X11 fold run exists.

X11 re-runs two discharged rules on X3's five folds, whose held-out trajectories pool to 20
(each of the ten episodes held out once). Their power was measured at n = 4; this measures it at
the n the replications will face.

  M-43  (scripts/task_d3b_ens5_power.py). Power = how often the paired-difference interval on
        r(disagreement, error) - r(index, error) excludes zero, over 400 draws of n trajectories from
        the 20-trajectory all-episodes pool. At n = 4 the draws were without replacement. At n = 20 the
        pool IS the sample, so the draws are with replacement (a bootstrap estimate of power at n = 20);
        that is the only change. Assertion: the n = 4 path, replayed with the original generator,
        reproduces results/task_d3b_ens5_power.json `power` exactly.
  M-44  (scripts/p1_power_check.py). MDE = (z_.975 + z_.80) x the cluster-bootstrap SE of the paired
        statistic (log overconfidence ratio; +-1 sigma coverage difference) at h = 100, from the same
        model pairs (the three ensemble-5 seeds and the released checkpoint), binding = the
        cross-architecture pairs. At n = 20 the pool is the all-ten-episodes arena. Assertion: on the
        held-out pair (n = 4) every pair's observed log-ratio and coverage difference equal
        results/p1_power_check.json `m44.pairs` within 1e-12, and the recomputed binding MDEs are within
        5% of the stored ones (p1 drew its bootstrap from a generator it shared with M-45, so its draws
        cannot be replayed without re-running M-45; the tolerance was fixed in GT1 before this ran).

CAUTION (both): the 20-trajectory pool is IN-SAMPLE for our arms, which trained on eight of its ten
episodes, so every n = 20 figure here is an UPPER BOUND on power and a LOWER bound on the MDE, exactly
as the n = 4 originals say of themselves.

Writes results/x11_power.json. Run from the repository root.
"""
import hashlib
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
import torch  # noqa: E402
import rwm_data as R  # noqa: E402
import rollout_eval as E  # noqa: E402
import rwm_metrics as MET  # noqa: E402
import score_reference as S  # noqa: E402
import task_d3b_ens5_power as TDB  # noqa: E402
import p1_power_check as P1  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
OUT = os.path.join(R.RESULTS, "x11_power.json")
START, LEN, SEEDS = E.START_STEP, 400, (0, 1, 2)
H_M44 = P1.DEPLOY_H
MDE_TOL = 0.05
MODULES = ("scripts/x11_power.py", "scripts/task_d3b_ens5_power.py", "scripts/p1_power_check.py",
           "src/score_reference.py", "src/rwm_data.py", "src/rwm_metrics.py", "src/rollout_eval.py")


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def pool(episodes):
    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    data, ep = R.load_data(paths["csv"], verbose=False)
    starts = MET.non_overlapping_starts(ep, episodes, LEN)
    idx = np.asarray(starts)[:, None] + np.arange(LEN)[None, :]
    raw = data[idx]
    st = torch.as_tensor(R.normalise_state(raw[:, :, R.STATE_COLS], cfg["state_data_mean"], cfg["state_data_std"]),
                         dtype=torch.float32)
    ac = torch.as_tensor(raw[:, :, R.ACTION_COLS], dtype=torch.float32)
    return {"st": st, "ac": ac, "starts": [int(s) for s in starts], "n_traj": len(starts),
            "n_ind": int(MET.n_independent(starts, LEN))}


def roll(m, pl):
    pred, alea, epi, alea_s, epi_s = m.rollout_uncertainty(pl["st"].clone(), pl["ac"], START, action_offset=1)
    err = (pred - pl["st"]).abs().numpy().astype(np.float64)
    return {"err": err, "epi": epi.numpy().astype(np.float64), "epi_s": epi_s.numpy().astype(np.float64)}


def models():
    out = {}
    for s in SEEDS:
        w = f"runs/armA_seed{s}_ens5/weights_2500.pt"
        m = S.ReferenceRWM(torch.load(w, map_location="cpu")["model_state_dict"]); m.eval()
        out[f"ens5_seed{s}"] = m
    m = S.ReferenceRWM(torch.load(R.repo_paths()["ckpt"], map_location="cpu")["system_dynamics_state_dict"]); m.eval()
    out["released"] = m
    return out


# ------------------------------------------------------------------ M-43
def m43_panel(sc, h):
    err = sc["err"][:, START:START + h].sum(-1)
    dis = sc["epi_s"][:, START:START + h]
    fi = np.broadcast_to(np.arange(err.shape[1], dtype=np.float64), err.shape).copy()
    return dis, err, fi


def m43_power(SC, n_sub, replace, rng, seed_used):
    """task_d3b_ens5_power.py's POWER loop (lines 186-197), with n and replacement as arguments."""
    out = {}
    for h in TDB.HORIZONS:
        dis, err, fi = m43_panel(SC[f"ens5_seed{seed_used}"], h)
        n = dis.shape[0]
        full, _, _ = TDB.paired_ci(dis, err, fi, np.random.default_rng(0))
        fires = 0
        for _ in range(TDB.N_DRAWS):
            sub = rng.choice(n, n_sub, replace=replace)
            _, lo, _ = TDB.paired_ci(dis[sub], err[sub], fi[sub], np.random.default_rng(0), n_boot=1000)
            fires += bool(lo is not None and lo > 0)
        out[str(h)] = {"effect_at_n20": full, "power": fires / TDB.N_DRAWS, "n_draws": TDB.N_DRAWS,
                       "subsample_n": n_sub, "with_replacement": replace, "seed_used": seed_used}
    return out


# ------------------------------------------------------------------ M-44
def m44_mde(SC, n, rng):
    """p1_power_check.py's M-44 block (lines 280-350): pairs, SEs, both calibrations."""
    sl = slice(START, START + H_M44)

    def rho(sc, i):
        e, s = sc["err"][i, sl], sc["epi"][i, sl]
        ms = np.nanmean(s)
        return float(np.nanmean(e) / ms) if ms > 0 else np.nan

    def cov1(sc, i):
        e, s = sc["err"][i, sl], sc["epi"][i, sl]
        return float(np.nanmean(e <= s))

    names = sorted(SC)
    pairs, same = [], []
    full = np.arange(n)
    for a in range(len(names)):
        for b in range(a + 1, len(names)):
            A, B = SC[names[a]], SC[names[b]]
            se_lr, lo_lr, hi_lr, _ = P1.boot_se(lambda i, A=A, B=B: np.log(rho(A, i) / rho(B, i)), n, rng)
            se_cv, lo_cv, hi_cv, _ = P1.boot_se(lambda i, A=A, B=B: cov1(A, i) - cov1(B, i), n, rng)
            rec = {"pair": f"{names[a]} vs {names[b]}", "same_architecture": "released" not in (names[a], names[b]),
                   "log_ratio_observed": float(np.log(rho(A, full) / rho(B, full))),
                   "coverage_diff_observed_pts": 100 * (cov1(A, full) - cov1(B, full)),
                   "log_ratio_se": se_lr, "coverage_diff_se_pts": 100 * se_cv,
                   "ratio_mde_multiplicative": float(np.exp(P1.mde(se_lr))), "coverage_mde_pts": 100 * P1.mde(se_cv)}
            pairs.append(rec)
    cross = [p for p in pairs if not p["same_architecture"]]
    nul = [p for p in pairs if p["same_architecture"]]
    se_lr_x = float(np.mean([p["log_ratio_se"] for p in cross]))
    se_cv_x = float(np.mean([p["coverage_diff_se_pts"] for p in cross])) / 100
    se_lr_n = float(np.mean([p["log_ratio_se"] for p in nul]))
    se_cv_n = float(np.mean([p["coverage_diff_se_pts"] for p in nul])) / 100
    return {"n_trajectories": n, "horizon": H_M44, "pairs": pairs,
            "binding_cross_architecture": {"ratio_mde_multiplicative": float(np.exp(P1.mde(se_lr_x))),
                                           "coverage_mde_pts": 100 * P1.mde(se_cv_x)},
            "optimistic_same_architecture": {"ratio_mde_multiplicative": float(np.exp(P1.mde(se_lr_n))),
                                             "coverage_mde_pts": 100 * P1.mde(se_cv_n)}}


def main():
    os.chdir(ROOT)
    t0 = time.perf_counter()
    split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"), verbose=False)
    hold = sorted(split["holdout_episodes"])
    p20, p4 = pool(list(range(R.N_EPISODES))), pool(hold)
    assert p20["n_traj"] == 20 and p20["n_ind"] == 20 and p4["n_traj"] == 4 and p4["n_ind"] == 4
    M = models()
    S20 = {k: roll(m, p20) for k, m in M.items()}
    S4 = {k: roll(m, p4) for k, m in M.items()}

    # ---- assertions on the n = 4 originals -----------------------------------------------
    tdb = json.load(open(os.path.join(R.RESULTS, "task_d3b_ens5_power.json")))["power"]
    ens = {k: v for k, v in S20.items() if k != "released"}
    rep4 = m43_power(ens, TDB.SUB_N, False, np.random.default_rng(0), SEEDS[0])
    a43 = max(max(abs(rep4[h]["power"] - tdb[h]["power_at_n4"]), abs(rep4[h]["effect_at_n20"] - tdb[h]["effect_at_n20"]))
              for h in rep4)
    p1 = json.load(open(os.path.join(R.RESULTS, "p1_power_check.json")))["m44"]
    m4 = m44_mde(S4, 4, np.random.default_rng(20260823))
    stored = {p["pair"]: p for p in p1["pairs"]}
    a44_obs = max(max(abs(p["log_ratio_observed"] - stored[p["pair"]]["log_ratio_observed"]),
                      abs(p["coverage_diff_observed_pts"] - stored[p["pair"]]["coverage_diff_observed_pts"]))
                  for p in m4["pairs"])
    sb = p1["mde_80pct_power"]
    rb = m4["binding_cross_architecture"]
    a44_mde = max(abs(rb["ratio_mde_multiplicative"] - sb["overconfidence_ratio_multiplicative"])
                  / sb["overconfidence_ratio_multiplicative"],
                  abs(rb["coverage_mde_pts"] - sb["coverage_pts"]) / sb["coverage_pts"])
    assertions = {
        "m43_n4_replayed": {"pass": bool(a43 == 0.0), "max_abs_diff": a43,
                            "against": "results/task_d3b_ens5_power.json power[h].{power_at_n4, effect_at_n20}"},
        "m44_n4_observed": {"pass": bool(a44_obs <= 1e-12), "max_abs_diff": a44_obs,
                            "against": "results/p1_power_check.json m44.pairs[*].{log_ratio_observed, coverage_diff_observed_pts}"},
        "m44_n4_binding_mde": {"pass": bool(a44_mde <= MDE_TOL), "max_rel_diff": a44_mde, "tolerance": MDE_TOL,
                               "recomputed": rb, "stored": {"ratio": sb["overconfidence_ratio_multiplicative"],
                                                            "coverage_pts": sb["coverage_pts"]}},
    }
    for k, v in assertions.items():
        print(f"  assertion {k}: {'PASS' if v['pass'] else 'FAIL'}")
    if not all(v["pass"] for v in assertions.values()):
        json.dump({"BLOCKED": "an n = 4 reproduction failed", "assertions": assertions},
                  open(OUT + ".blocked", "w"), indent=1, default=str)
        raise SystemExit("BLOCKED: see results/x11_power.json.blocked; no n = 20 figure written")

    # ---- n = 20 -------------------------------------------------------------------------
    m43 = {f"seed{s}": m43_power(ens, 20, True, np.random.default_rng(0), s) for s in SEEDS}
    m44 = m44_mde(S20, 20, np.random.default_rng(20260823))
    out = {"rule": "X11 (power, before any fold run)", "script": "scripts/x11_power.py",
           "script_sha256": sha256("scripts/x11_power.py"),
           "code_sha256": {p: sha256(p) for p in MODULES},
           "git_head": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
           "caveat": ("the n = 20 pool is all ten episodes, in-sample for our arms (they trained on eight); every "
                      "n = 20 power is an upper bound and every n = 20 MDE a lower bound, as at n = 4"),
           "assertions": assertions,
           "m43": {"criterion": "paired interval on r(disagreement) - r(index) excludes zero (task_d3b_ens5_power.py)",
                   "n4_replayed": rep4, "n20": m43,
                   "n20_mean_power": float(np.mean([v["power"] for s in m43.values() for v in s.values()])),
                   "n20_worst_power": float(min(v["power"] for s in m43.values() for v in s.values())),
                   "change_from_n4": "draws of 20 from the 20-trajectory pool are with replacement; at n = 4 they were without"},
           "m44": {"n4_recomputed": m4, "n20": m44,
                   "verdict_thresholds_unchanged": {"ratio": 1.45, "coverage_pts": 2.26,
                                                    "source": "M-44's committed thresholds (r2_independent_ensemble.py:50-51); X11d keeps them"}},
           "timing": {"wall_clock_s": time.perf_counter() - t0, "torch_threads": torch.get_num_threads(),
                      "cpu_count": os.cpu_count()}}
    json.dump(out, open(OUT, "w"), indent=1)
    print(f"  M-43 n=20 power (seed 0): " + ", ".join(f"h={h} {v['power']:.3f}" for h, v in m43['seed0'].items()))
    print(f"  M-44 n=20 binding MDE: ratio {m44['binding_cross_architecture']['ratio_mde_multiplicative']:.3f}x, "
          f"coverage {m44['binding_cross_architecture']['coverage_mde_pts']:.2f} pts")
    print(f"  wrote {R.rel(OUT)}")


if __name__ == "__main__":
    main()
