"""
Rule X11b (round 5; PRE-REGISTERED, exploratory) -- M-43's comparison of ensemble disagreement with the
forecast-step index, on the ensemble-5 arms of X3's five folds, n_independent = 20.

It never re-opens M-43, whose verdict (DOES NOT GENERALISE, at n = 4) stands; nothing here changes a verdict.
PROTOCOLS.md §4 holds the rule.

MODELS AND ARENA: as X11a (x11_common): each fold's three ensemble-5 arms on that fold's four held-out
trajectories, pooled over the five folds to 20; per seed, the 20 trajectories come from that seed's arm of each fold.

STATISTICS, THRESHOLDS AND BRANCHES copied from task_d3_ens5.py lines 160-231 with only the arena changed:
per seed and horizon, r(index, |error|), r(disagreement, |error|), the partial r(disagreement, |error| . index),
and the paired difference r(disagreement) - r(index) with its cluster-bootstrap interval over whole
trajectories (task_d3_ens5.cluster_boot, default_rng(0), 20,000 draws). Error is the summed absolute error over
the 45 dimensions; disagreement is the summed epistemic sigma (the scalar envs/base.py:166 applies). The verdict
is M-43's, per seed: GENERALISES iff disagreement leads the index at every horizon in {8, 32, 128, 368} in all
three seeds AND the paired interval excludes zero in all three seeds at a majority (more than 2) of those
horizons; otherwise DOES NOT GENERALISE.

ASSERTIONS (before any reading): (a) as X11a; (b) the same code on fold {1, 8} alone reproduces
results/task_d3_ens5.json `governing` and `m43_verdict` within 1e-12.

  --assert-only   (b) only, on fold {1, 8}; writes docs/presubmission/round5/gt1_x11b_assert.json.
Writes results/x11b_fold_m43.json. Run from the repository root.
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
import task_d3_ens5 as TD  # noqa: E402
import x11_common as C  # noqa: E402
import x11a_fold_ens5_calibration as XA  # noqa: E402

RULE = "X11b"
RULE_ID = "M-98"
FROZEN = ('scripts/x11b_fold_m43.py', 'scripts/x11a_fold_ens5_calibration.py', 'scripts/x11_common.py')
HORIZONS, INDEX_DEFINED = TD.HORIZONS, TD.INDEX_DEFINED
START, TOL_REPRO = C.START, 1e-12
OUT = os.path.join(R.RESULTS, "x11b_fold_m43.json")
ASSERT_OUT = os.path.join(C.ROOT, "docs", "presubmission", "round5", "gt1_x11b_assert.json")
MODULES = ("scripts/x11b_fold_m43.py", "scripts/x11a_fold_ens5_calibration.py", "scripts/x11_common.py",
           "scripts/task_d3_ens5.py", "scripts/x3_cross_fold.py", "src/score_reference.py", "src/rwm_model.py",
           "src/rwm_data.py", "src/rwm_metrics.py", "src/rollout_eval.py")


def roll(m, ar):
    pred, _, _, _, epi_s = m.rollout_uncertainty(ar["st"].clone(), ar["ac"], START, action_offset=1)
    return {"err": (pred - ar["st"]).abs().numpy().astype(np.float64), "epi_s": epi_s.numpy().astype(np.float64)}


def governing(R5, n_traj):
    """task_d3_ens5.py:165-202 (the table) and :205-231 (the verdict), verbatim but for the printing."""
    gov = {}
    for h in HORIZONS:
        per_seed_rows = []
        for s in sorted(R5):
            err = R5[s]["err"][:, START:START + h].sum(-1)
            dis = R5[s]["epi_s"][:, START:START + h]
            T = err.shape[1]
            fi = np.broadcast_to(np.arange(T, dtype=np.float64), err.shape).copy()
            r_i = TD.pooled_corr(fi, err) if h > 1 else None
            r_d = TD.pooled_corr(dis, err)
            r_p = TD.partial_corr(dis, err, fi) if h > 1 else None
            if h > 1:
                f = lambda i: (None if (TD.pooled_corr(dis[i], err[i]) is None
                                        or TD.pooled_corr(fi[i], err[i]) is None)
                               else TD.pooled_corr(dis[i], err[i]) - TD.pooled_corr(fi[i], err[i]))
                d_obs = r_d - r_i
                lo, hi, nb = TD.cluster_boot(f, n_traj, np.random.default_rng(0))
            else:
                d_obs = lo = hi = None
                nb = 0
            per_seed_rows.append({"seed": s, "r_index": r_i, "r_disagreement": r_d, "r_partial": r_p,
                                  "paired_diff": d_obs, "paired_ci_lo": lo, "paired_ci_hi": hi,
                                  "paired_n_boot": nb})
        gov[str(h)] = {"per_seed": per_seed_rows}
        idxs = [r["r_index"] for r in per_seed_rows if r["r_index"] is not None]
        diss = [r["r_disagreement"] for r in per_seed_rows]
        gov[str(h)]["disagreement_leads_all_seeds"] = bool(idxs) and all(d > i for d, i in zip(diss, idxs))
        los = [r["paired_ci_lo"] for r in per_seed_rows if r["paired_ci_lo"] is not None]
        gov[str(h)]["paired_excludes_zero_all_seeds"] = bool(los) and all(lo_ > 0 for lo_ in los)
        gov[str(h)]["mean_r_index"] = statistics.mean(idxs) if idxs else None
        gov[str(h)]["mean_r_disagreement"] = statistics.mean(diss)
    leads = {h: gov[str(h)]["disagreement_leads_all_seeds"] for h in INDEX_DEFINED}
    excl = {h: gov[str(h)]["paired_excludes_zero_all_seeds"] for h in INDEX_DEFINED}
    leads_everywhere = all(leads.values())
    n_excl = sum(excl.values())
    majority = n_excl > len(INDEX_DEFINED) / 2
    verdict = "GENERALISES" if (leads_everywhere and majority) else "DOES NOT GENERALISE"
    v = {"horizons_tested": list(INDEX_DEFINED),
         "disagreement_leads_index": {str(h): leads[h] for h in INDEX_DEFINED},
         "leads_at_every_horizon": leads_everywhere,
         "paired_excludes_zero": {str(h): excl[h] for h in INDEX_DEFINED},
         "n_excluding_zero": n_excl, "majority_required": len(INDEX_DEFINED) / 2,
         "majority_met": majority, "verdict": verdict}
    return gov, v


def assert_fold18():
    ar = C.arena((1, 8))
    R5 = {s: roll(C.load_ens5(C.ens5_weights((1, 8), s))[0], ar) for s in C.ENS5_SEEDS}
    gov, v = governing(R5, 4)
    want = json.load(open(os.path.join(R.RESULTS, "task_d3_ens5.json")))
    d = max(XA.max_diff(gov, want["governing"]),
            XA.max_diff(v, {k: want["m43_verdict"][k] for k in v}))
    return {"b": {"pass": bool(d <= TOL_REPRO), "max_abs_diff": d, "tolerance": TOL_REPRO,
                  "against": "results/task_d3_ens5.json governing and m43_verdict"}}


def reading():
    t0 = time.perf_counter()
    frozen = C.require_prereg(RULE_ID, FROZEN, OUT)
    bad = {f"{C.fid(f)}_s{s}": C.check_record(C.ens5_record(f, s), f, 5) for f in C.FOLDS for s in C.ENS5_SEEDS}
    bad = {k: v for k, v in bad.items() if v}
    if bad:
        C.blocked(OUT, "assertion (a): a run record is wrong", problems=bad)
    a18 = assert_fold18()
    if not a18["b"]["pass"]:
        C.blocked(OUT, "assertion (b) failed", b=a18["b"])
    parts, sha, order = {s: [] for s in C.ENS5_SEEDS}, {}, []
    for f in C.FOLDS:
        ar = C.arena(f)
        order += [{"fold": C.fid(f), "start_row": a, "episode": b} for a, b in zip(ar["starts"], ar["episode"])]
        for s in C.ENS5_SEEDS:
            w = C.ens5_weights(f, s)
            sha[f"{C.fid(f)}_s{s}"] = C.sha256(w)
            parts[s].append(roll(C.load_ens5(w)[0], ar))
    R5 = {s: {k: np.concatenate([p[k] for p in parts[s]], 0) for k in ("err", "epi_s")} for s in C.ENS5_SEEDS}
    for s, r in R5.items():
        if not (np.isfinite(r["err"][:, START:]).all() and np.isfinite(r["epi_s"][:, START:]).all()):
            C.blocked(OUT, f"non-finite rollout, seed {s}")
    gov, v = governing(R5, 20)
    out = {"rule": RULE, "ledger": RULE_ID, "frozen_sha256": frozen, "script": "scripts/x11b_fold_m43.py", "script_sha256": C.sha256("scripts/x11b_fold_m43.py"),
           "exploratory": True, "never_reopens": "M-43 or any discharged rule; nothing here changes a verdict",
           "design": {"folds": [list(f) for f in C.FOLDS], "seeds": list(C.ENS5_SEEDS), "n_trajectories": 20,
                      "n_independent": 20, "trajectories": order, "n_boot": TD.N_BOOT,
                      "copied_from": "scripts/task_d3_ens5.py:160-231, arena changed only"},
           "assertions": {"a": {"pass": True}, **a18}, "governing": gov, "verdict": v,
           "weights_sha256": sha, "code_sha256": {p: C.sha256(p) for p in MODULES},
           "git_head": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
           "timing": {"wall_clock_s": time.perf_counter() - t0, "torch_threads": torch.get_num_threads(),
                      "cpu_count": os.cpu_count()}}
    json.dump(out, open(OUT, "w"), indent=1)
    print(f"  X11b: {v['verdict']} (leads everywhere {v['leads_at_every_horizon']}, "
          f"excludes zero at {v['n_excluding_zero']} of {len(INDEX_DEFINED)})")
    print(f"  wrote {R.rel(OUT)}")


def main():
    os.chdir(C.ROOT)
    ap = argparse.ArgumentParser()
    ap.add_argument("--assert-only", action="store_true")
    args = ap.parse_args()
    if args.assert_only:
        a = assert_fold18()
        json.dump({"rule": RULE, "script_sha256": C.sha256("scripts/x11b_fold_m43.py"), **a},
                  open(ASSERT_OUT, "w"), indent=1)
        for k, val in a.items():
            print(f"  assertion {k}: {'PASS' if val['pass'] else 'FAIL'} (max diff {val['max_abs_diff']})")
        sys.exit(0 if all(val["pass"] for val in a.values()) else 1)
    reading()


if __name__ == "__main__":
    main()
