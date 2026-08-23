"""D3 — the five ensemble-5 measurements, and M-43's verdict.

Every epistemic measurement in this paper is otherwise made on ONE released
checkpoint. Section 5.6 -- the only finding here that strengthens an original
claim -- rests entirely on it, so a property of the method and a property of that
one artifact cannot currently be told apart. These runs are the discriminator.

M-43 was committed before any ens5 result existed. Its rule is evaluated here
exactly as written, by code, and printed whichever way it falls:

  GENERALISES      disagreement leads the index at EVERY horizon tested
                   AND the paired difference excludes zero at a MAJORITY
  DOES NOT         the index leads at ANY horizon
                   OR the paired difference spans zero at a majority

"Every horizon tested" is the set on which the index is defined. At h=1 a rollout
has one forecast step, the index is constant, and its correlation does not exist
-- so h=1 cannot be a horizon at which the index leads or fails to. It is
reported, and excluded from the verdict, and this paragraph is the pre-commitment
to that reading rather than a choice made after seeing the numbers.

The five measurements:
  1  M-43's governing table: r(index), r(disagreement), partial, paired difference
  2  calibration of the epistemic term, comparable to section 5.2's table
  3  the aleatoric collapse rate against the ens1 runs
  4  input-dependence (CoV) and horizon-flatness, comparable to section 5.8
  5  ens1 against ens5 on prediction accuracy at h=8 and h=368

Writes results/task_d3_ens5.json.
"""
import glob
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import torch  # noqa: E402
import rwm_data as R  # noqa: E402
import rollout_eval as E  # noqa: E402
import rwm_metrics as MET  # noqa: E402
import rwm_model as M  # noqa: E402
import score_reference as S  # noqa: E402

HORIZONS = (1, 8, 32, 100, 128, 368)
INDEX_DEFINED = (8, 32, 128, 368)      # h=1 has a single forecast step
START, LEN, SEEDS, N_BOOT = E.START_STEP, 400, (0, 1, 2), 20000


def pooled_corr(x, y):
    a, b = x.ravel(), y.ravel()
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 3 or a[m].std() == 0 or b[m].std() == 0:
        return None
    return float(np.corrcoef(a[m], b[m])[0, 1])


def partial_corr(x, y, z):
    a, b, c = x.ravel(), y.ravel(), z.ravel()
    m = np.isfinite(a) & np.isfinite(b) & np.isfinite(c)
    a, b, c = a[m], b[m], c[m]
    if len(a) < 4 or a.std() == 0 or b.std() == 0 or c.std() == 0:
        return None
    ra = a - np.polyval(np.polyfit(c, a, 1), c)
    rb = b - np.polyval(np.polyfit(c, b, 1), c)
    return None if ra.std() == 0 or rb.std() == 0 else float(np.corrcoef(ra, rb)[0, 1])


def cluster_boot(fn, n, rng, n_boot=N_BOOT):
    v = [x for x in (fn(rng.integers(0, n, n)) for _ in range(n_boot))
         if x is not None and np.isfinite(x)]
    return ((float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5)), len(v))
            if v else (None, None, 0))


def main():
    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    data, ep = R.load_data(paths["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"),
                         verbose=False)
    hold = list(split["holdout_episodes"])
    starts = MET.non_overlapping_starts(ep, hold, LEN)
    n_ind, n_traj = int(MET.n_independent(starts, LEN)), len(starts)

    idx = np.asarray(starts)[:, None] + np.arange(LEN)[None, :]
    raw = data[idx]
    st = torch.as_tensor(R.normalise_state(raw[:, :, R.STATE_COLS],
                                           cfg["state_data_mean"], cfg["state_data_std"]),
                         dtype=torch.float32)
    ac = torch.as_tensor(raw[:, :, R.ACTION_COLS], dtype=torch.float32)

    out = {"design": {"arena": "out-of-sample", "holdout_episodes": hold,
                      "n_independent": n_ind, "n_trajectories": n_traj,
                      "seeds": list(SEEDS), "ensemble": 5, "iterations": 2500,
                      "traj_len": LEN, "start_step": START, "action_offset": 1,
                      "n_boot": N_BOOT, "bootstrap_unit": "whole trajectory",
                      "index_defined_at": list(INDEX_DEFINED),
                      "index_undefined_note": (
                          "h=1 has a single forecast step, so the index is constant and its "
                          "correlation undefined; it is reported and excluded from M-43's "
                          "verdict, as M-43's own text sets out")},
           "per_seed": {}, "governing": {}, "calibration": {}, "collapse": {},
           "input_dependence": {}, "accuracy_vs_ens1": {}}

    print("D3 — ENSEMBLE-5 REPLICATION")
    print("=" * 108)
    print(f"  out-of-sample, n_independent = {n_ind}, seeds {list(SEEDS)}, ensemble 5\n")

    # ---- roll out every seed once; everything below reuses these -----------
    R5 = {}
    for s in SEEDS:
        w = f"runs/armA_seed{s}_ens5/weights_2500.pt"
        sd = torch.load(w, map_location="cpu")["model_state_dict"]
        m = S.ReferenceRWM(sd); m.eval()
        # the harness must agree with our own trainer's forward before any number
        # from it is comparable to section 5.2's, which came through the same class
        own = M.build_from_config(cfg, ensemble_size=5)
        own.load_state_dict(sd, strict=True); own.eval()
        p_own, _ = own.rollout_full(st.clone(), ac, START, action_offset=1)
        pred, alea, epi, alea_s, epi_s = m.rollout_uncertainty(st.clone(), ac, START,
                                                               action_offset=1)
        d = float((p_own - pred).abs().max())
        assert d < 1e-5, f"seed {s}: harness disagrees with the trainer's forward by {d:.3e}"
        R5[s] = {"err": (pred - st).abs().numpy().astype(np.float64),
                 "alea": alea.numpy().astype(np.float64),
                 "epi": epi.numpy().astype(np.float64),
                 "epi_s": epi_s.numpy().astype(np.float64),
                 "max_diff_vs_trainer": d}
        print(f"  seed {s}: rolled out, harness vs trainer max |diff| = {d:.3e}")
        out["per_seed"][str(s)] = {"weights": w, "max_diff_vs_trainer": d}

    # ---- 1. M-43's governing measurement -----------------------------------
    print(f"\n  [1] M-43's governing table, per seed and pooled")
    hdr = (f"    {'seed':>5}{'h':>6}{'r(index)':>22}{'r(disagr)':>22}"
           f"{'partial':>22}{'paired diff [95% CI]':>26}")
    print(hdr); print("    " + "-" * (len(hdr) - 4))
    gov = {}
    for h in HORIZONS:
        per_seed_rows = []
        for s in SEEDS:
            err = R5[s]["err"][:, START:START + h].sum(-1)
            dis = R5[s]["epi_s"][:, START:START + h]
            T = err.shape[1]
            fi = np.broadcast_to(np.arange(T, dtype=np.float64), err.shape).copy()
            r_i = pooled_corr(fi, err) if h > 1 else None
            r_d = pooled_corr(dis, err)
            r_p = partial_corr(dis, err, fi) if h > 1 else None
            if h > 1:
                f = lambda i: (None if (pooled_corr(dis[i], err[i]) is None
                                        or pooled_corr(fi[i], err[i]) is None)
                               else pooled_corr(dis[i], err[i]) - pooled_corr(fi[i], err[i]))
                d_obs = r_d - r_i
                lo, hi, nb = cluster_boot(f, n_traj, np.random.default_rng(0))
            else:
                d_obs = lo = hi = None; nb = 0
            per_seed_rows.append({"seed": s, "r_index": r_i, "r_disagreement": r_d,
                                  "r_partial": r_p, "paired_diff": d_obs,
                                  "paired_ci_lo": lo, "paired_ci_hi": hi,
                                  "paired_n_boot": nb})
            fmt = lambda v: "n/a" if v is None else f"{v:+.3f}"
            ci = "n/a" if lo is None else f"{d_obs:+.3f} [{lo:+.3f}, {hi:+.3f}]"
            print(f"    {s:>5}{h:>6}{fmt(r_i):>22}{fmt(r_d):>22}{fmt(r_p):>22}{ci:>26}")
        gov[str(h)] = {"per_seed": per_seed_rows}
        # the seed-level agreement is what the verdict is applied to
        idxs = [r["r_index"] for r in per_seed_rows if r["r_index"] is not None]
        diss = [r["r_disagreement"] for r in per_seed_rows]
        gov[str(h)]["disagreement_leads_all_seeds"] = (
            bool(idxs) and all(d > i for d, i in zip(diss, idxs)))
        los = [r["paired_ci_lo"] for r in per_seed_rows if r["paired_ci_lo"] is not None]
        gov[str(h)]["paired_excludes_zero_all_seeds"] = bool(los) and all(l > 0 for l in los)
        gov[str(h)]["mean_r_index"] = (statistics.mean(idxs) if idxs else None)
        gov[str(h)]["mean_r_disagreement"] = statistics.mean(diss)
    out["governing"] = gov

    # ---- M-43's verdict, applied exactly as written ------------------------
    leads = {h: gov[str(h)]["disagreement_leads_all_seeds"] for h in INDEX_DEFINED}
    excl = {h: gov[str(h)]["paired_excludes_zero_all_seeds"] for h in INDEX_DEFINED}
    leads_everywhere = all(leads.values())
    n_excl = sum(excl.values())
    majority = n_excl > len(INDEX_DEFINED) / 2
    generalises = leads_everywhere and majority
    verdict = "GENERALISES" if generalises else "DOES NOT GENERALISE"
    out["m43_verdict"] = {
        "rule": "M-43, committed before any ens5 result existed",
        "horizons_tested": list(INDEX_DEFINED),
        "disagreement_leads_index": {str(h): leads[h] for h in INDEX_DEFINED},
        "leads_at_every_horizon": leads_everywhere,
        "paired_excludes_zero": {str(h): excl[h] for h in INDEX_DEFINED},
        "n_excluding_zero": n_excl, "majority_required": len(INDEX_DEFINED) / 2,
        "majority_met": majority,
        "verdict": verdict,
        "note": ("applied per seed: a horizon counts as leading only if disagreement leads the "
                 "index in ALL THREE seeds, and as excluding zero only if the paired interval "
                 "excludes zero in all three. That is stricter than pooling and is the reading "
                 "that cannot be gamed by a favourable seed."),
    }
    print(f"\n  M-43 VERDICT: {verdict}")
    print(f"    disagreement leads the index at every horizon tested: {leads_everywhere}  {leads}")
    print(f"    paired difference excludes zero at {n_excl} of {len(INDEX_DEFINED)}: "
          f"majority={majority}  {excl}")

    # ---- 2. calibration ----------------------------------------------------
    print(f"\n  [2] calibration of the epistemic term, comparable to section 5.2, "
          f"with 95% cluster-bootstrap intervals (A1)")
    print(f"    {'h':>5}{'err/sigma [95% CI]':>30}{'+-1 sigma [95% CI]':>28}"
          f"{'+-2 sigma [95% CI]':>28}{'dims r>0':>11}")
    # A1 -- the ens5 table carried bare seed-means. The interval resamples whole
    # TRAJECTORIES and pools the three seeds inside each draw: seeds are not
    # independent evidence about the arena (M-27), they are three measurements of
    # the same four trajectories.
    _bidx = np.random.default_rng(0).integers(0, n_traj, (N_BOOT, n_traj))

    def _ci(per_traj_num, per_traj_den=None):
        """per_traj_*: (n_seeds, n_traj) -> [lo, hi] over resampled trajectories."""
        a = per_traj_num.mean(axis=0)[_bidx].mean(axis=1)
        v = a if per_traj_den is None else a / per_traj_den.mean(axis=0)[_bidx].mean(axis=1)
        v = v[np.isfinite(v)]
        return ([float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]
                if len(v) > 1 else [None, None])

    cal = {}
    for h in HORIZONS:
        rows = []
        pe, pg, p1, p2 = [], [], [], []          # (n_seeds, n_traj) partials
        for s in SEEDS:
            eT = R5[s]["err"][:, START:START + h]        # (n_traj, h, 45)
            gT = R5[s]["epi"][:, START:START + h]
            e, g = eT.reshape(-1, 45), gT.reshape(-1, 45)
            npos = 0
            for d in range(45):
                a, b = g[:, d], e[:, d]
                if a.std() > 0 and b.std() > 0 and np.corrcoef(a, b)[0, 1] > 0:
                    npos += 1
            rows.append({"seed": s,
                         "ratio_err_over_sigma": float(np.nanmean(e) / np.nanmean(g)),
                         "coverage_pm1": float(np.nanmean(e <= g)),
                         "coverage_pm2": float(np.nanmean(e <= 2 * g)),
                         "n_positive": npos})
            pe.append(np.nanmean(eT, axis=(1, 2))); pg.append(np.nanmean(gT, axis=(1, 2)))
            p1.append(np.nanmean(eT <= gT, axis=(1, 2)))
            p2.append(np.nanmean(eT <= 2 * gT, axis=(1, 2)))
        pe, pg, p1, p2 = map(np.asarray, (pe, pg, p1, p2))
        cal[str(h)] = {"per_seed": rows,
                       "mean_ratio": statistics.mean(r["ratio_err_over_sigma"] for r in rows),
                       "mean_cov1": statistics.mean(r["coverage_pm1"] for r in rows),
                       "mean_cov2": statistics.mean(r["coverage_pm2"] for r in rows),
                       "mean_npos": statistics.mean(r["n_positive"] for r in rows),
                       "ratio_ci": _ci(pe, pg), "cov1_ci": _ci(p1), "cov2_ci": _ci(p2),
                       "bootstrap_unit": "whole trajectory, seeds pooled within each draw",
                       "n_independent": n_ind}
        c = cal[str(h)]
        rc, k1, k2 = c["ratio_ci"], c["cov1_ci"], c["cov2_ci"]
        s_ratio = f"{c['mean_ratio']:,.1f} [{rc[0]:,.1f}, {rc[1]:,.1f}]"
        s_cov1 = f"{100 * c['mean_cov1']:.2f}% [{100 * k1[0]:.2f}, {100 * k1[1]:.2f}]"
        s_cov2 = f"{100 * c['mean_cov2']:.2f}% [{100 * k2[0]:.2f}, {100 * k2[1]:.2f}]"
        print(f"    {h:>5}{s_ratio:>30}{s_cov1:>28}{s_cov2:>28}"
              f"{c['mean_npos']:>8.1f}/45")
    out["calibration"] = cal

    # ---- 2b. ALEATORIC calibration of the ens5 arms -------------------------
    # The model card carried the ens1 Arm A aleatoric figure -- 52x, 11.67% -- on
    # all three ens5 entries, pasted across three different models, and unlike the
    # 10k entries it carried no "not re-measured" caveat. The rollouts above
    # already contain each arm's own aleatoric sigma, so measuring it properly
    # costs nothing and is strictly better than caveating a wrong number.
    print(f"\n  [2b] ALEATORIC calibration of the same arms, per seed "
          f"(the model card quotes these)")
    print(f"    {'seed':>5}{'h':>6}{'err/sigma':>16}{'+-1 sigma':>12}{'+-2 sigma':>12}")
    acal = {}
    for h in HORIZONS:
        rows = []
        for s in SEEDS:
            e = R5[s]["err"][:, START:START + h]
            g = R5[s]["alea"][:, START:START + h]
            rows.append({"seed": s,
                         "ratio_err_over_sigma": float(np.nanmean(e) / np.nanmean(g)),
                         "coverage_pm1": float(np.nanmean(e <= g)),
                         "coverage_pm2": float(np.nanmean(e <= 2 * g))})
            if h in (1, 100):
                print(f"    {s:>5}{h:>6}{rows[-1]['ratio_err_over_sigma']:>16,.1f}"
                      f"{100*rows[-1]['coverage_pm1']:>11.2f}%"
                      f"{100*rows[-1]['coverage_pm2']:>11.2f}%")
        acal[str(h)] = {
            "per_seed": rows,
            "mean_ratio": statistics.mean(r["ratio_err_over_sigma"] for r in rows),
            "mean_cov1": statistics.mean(r["coverage_pm1"] for r in rows),
            "mean_cov2": statistics.mean(r["coverage_pm2"] for r in rows),
            "n_independent": n_ind,
        }
    out["aleatoric_calibration"] = acal
    print(f"    -> measured per arm; the model card no longer inherits the ens1 figure")

    # ---- 3. the aleatoric collapse rate ------------------------------------
    e5 = [json.load(open(f"results/step5_armA_seed{s}_ens5.json"))["collapse_fit"]["slope_per_iter"]
          for s in SEEDS]
    e1 = [json.load(open(f))["collapse_fit"]["slope_per_iter"]
          for f in sorted(glob.glob("results/step5_armA_seed?.json"))]
    out["collapse"] = {"ens5_slopes": e5, "ens1_slopes": e1,
                       "ens5_mean": statistics.mean(e5), "ens1_mean": statistics.mean(e1),
                       "relative_difference": (statistics.mean(e5) - statistics.mean(e1))
                                              / abs(statistics.mean(e1))}
    print(f"\n  [3] aleatoric collapse rate")
    print(f"    ens1 mean {out['collapse']['ens1_mean']:.6e}   "
          f"ens5 mean {out['collapse']['ens5_mean']:.6e}   "
          f"{100*out['collapse']['relative_difference']:+.2f}%")

    # ---- 4. input-dependence and horizon-flatness --------------------------
    print(f"\n  [4] input-dependence and horizon-flatness of the epistemic term")
    inp = {}
    for s in SEEDS:
        g = R5[s]["epi"][:, START:]
        e = R5[s]["err"][:, START:]
        cov = float((g.std(axis=0) / np.maximum(g.mean(axis=0), 1e-30)).mean())
        g1, g8 = g[:, :1].mean(), g[:, 7:8].mean()
        e1_, e8 = e[:, :1].mean(), e[:, 7:8].mean()
        inp[str(s)] = {"cov_across_batch": cov,
                       "sigma_growth_1_to_8": float(g8 / g1),
                       "err_growth_1_to_8": float(e8 / e1_)}
        print(f"    seed {s}: CoV {cov:.4f}   sigma growth {g8/g1:.4f}x   "
              f"error growth {e8/e1_:.2f}x")
    out["input_dependence"] = inp

    # ---- 5. ens1 vs ens5 on prediction accuracy ----------------------------
    print(f"\n  [5] prediction accuracy, ens1 against ens5")
    acc = {}
    for h in (8, 368):
        e5v, e1v = [], []
        for s in SEEDS:
            e5v.append(float(R5[s]["err"][:, START:START + h].mean()))
            om = M.build_from_config(cfg, ensemble_size=1)
            om.load_state_dict(torch.load(f"runs/armA_seed{s}/weights_2500.pt",
                                          map_location="cpu")["model_state_dict"], strict=True)
            om.eval()
            p1, _ = om.rollout_full(st.clone(), ac, START, action_offset=1)
            e1v.append(float((p1 - st).abs().numpy()[:, START:START + h].mean()))
        acc[str(h)] = {"ens1_per_seed": e1v, "ens5_per_seed": e5v,
                       "ens1_mean": statistics.mean(e1v), "ens5_mean": statistics.mean(e5v),
                       "ens5_over_ens1": statistics.mean(e5v) / statistics.mean(e1v)}
        a = acc[str(h)]
        print(f"    h={h:<4} ens1 {a['ens1_mean']:.5f}   ens5 {a['ens5_mean']:.5f}   "
              f"ratio {a['ens5_over_ens1']:.4f}x")
    out["accuracy_vs_ens1"] = acc

    op = os.path.join(R.RESULTS, "task_d3_ens5.json")
    json.dump(out, open(op, "w"), indent=2)
    print(f"\n  wrote {R.rel(op)}")


if __name__ == "__main__":
    main()
