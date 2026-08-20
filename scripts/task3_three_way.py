"""Task 3 -- the three-way rollout comparison: clean, duplicated, contaminated.

R-47 measured contaminated against clean over 32 cells and found no harm. The
duplication control (R-55) adds the arm that separates "195 more windows" from
"195 spliced windows". This runs all three arms through the identical 32-cell
evaluation.

It also reports TWO bootstraps per cell, because the review found that the
existing task4/task5_2 bootstraps resample the pooled (seed x trajectory)
vector while reporting n_independent = n_trajectories:

  naive   -- resample all 3*n_traj values independently (as previously published)
  cluster -- resample TRAJECTORIES, carrying all three seeds (correct unit)

The cluster interval is primary. The naive one is kept so the published R-47
numbers remain traceable.

Writes results/task3_three_way.json and results/task3_three_way_report.txt.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import torch  # noqa: E402
import rwm_data as R  # noqa: E402
import rollout_eval as E  # noqa: E402
import rwm_metrics as MET  # noqa: E402
import rwm_model as M  # noqa: E402

START = E.START_STEP
SEEDS, CKPTS = (0, 1, 2), (500, 2500)
ARMS = {"clean": "", "duplicated": "_dup", "contaminated": "_contam"}
N_BOOT = 10000

paths = R.repo_paths()
cfg = R.load_reference_config(paths["lite"])
data, ep = R.load_data(paths["csv"], verbose=False)
split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"),
                     verbose=False)
scale = MET.training_scale(data, ep, split["train_episodes"],
                           cfg["state_data_mean"], cfg["state_data_std"])
ARENAS = {"out-of-sample": list(split["holdout_episodes"]),
          "in-sample": list(split["train_episodes"])}


def load(tag, s, c):
    m = M.build_from_config(cfg, ensemble_size=1)
    sd = torch.load(f"runs/armA_seed{s}{tag}/weights_{c}.pt", map_location="cpu")
    m.load_state_dict(sd["model_state_dict"], strict=True)
    m.eval()
    return m


def rollout_once(model, starts, L):
    """One rollout per (model, arena, L); both horizons and both metrics slice from it."""
    idx = np.asarray(starts)[:, None] + np.arange(L)[None, :]
    raw = data[idx]
    st = torch.as_tensor(R.normalise_state(raw[:, :, R.STATE_COLS],
                                           cfg["state_data_mean"], cfg["state_data_std"]),
                         dtype=torch.float32)
    ac = torch.as_tensor(raw[:, :, R.ACTION_COLS], dtype=torch.float32)
    p = model.rollout(st.clone(), ac, START, action_offset=1)
    return p, st


def metric_at(p, st, h, metric):
    if metric == "l1":
        nu = (p[:, START:START + h] - st[:, START:START + h]).abs().sum(-1)
        de = st[:, START:START + h].abs().sum(-1)
        return (nu / de).mean(1).numpy()
    sq = ((p[:, START:START + h] - st[:, START:START + h]) ** 2).numpy()
    return np.array([MET.nrmse_pooled(sq[i:i + 1], scale) for i in range(len(sq))])


def boot_naive(A, B, n=N_BOOT, seed=0):
    rng = np.random.default_rng(seed)
    k = len(A)
    i = rng.integers(0, k, size=(n, k))
    d = B[i].mean(1) - A[i].mean(1)
    return float(d.mean()), float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))


def boot_cluster(Am, Bm, n=N_BOOT, seed=0):
    rng = np.random.default_rng(seed)
    t = Am.shape[1]
    idx = rng.integers(0, t, size=(n, t))
    d = np.empty(n)
    for i in range(n):
        c = idx[i]
        d[i] = Bm[:, c].mean() - Am[:, c].mean()
    return float(d.mean()), float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))


def main():
    out = {}
    rows = []
    for arena, eps in ARENAS.items():
        for L, hs in ((400, (8, 368)), (200, (8, 168))):
            st_ = MET.non_overlapping_starts(ep, eps, L)
            ni = MET.n_independent(st_, L)
            for c in CKPTS:
                # one rollout per model, reused for both h and both metrics
                roll = {}
                for name, tag in ARMS.items():
                    for s in SEEDS:
                        roll[(name, s)] = rollout_once(load(tag, s, c), st_, L)
                for h in hs:
                    for metric in ("l1", "nrmse"):
                        V = {name: np.stack([metric_at(*roll[(name, s)], h, metric)
                                             for s in SEEDS]) for name in ARMS}
                        cell = f"{arena}|{L}|{c}|h{h}|{metric}"
                        rec = {"n_trajectories": int(V["clean"].shape[1]),
                               "n_independent": int(ni),
                               "n_pooled": int(V["clean"].size),
                               "means": {k: float(v.mean()) for k, v in V.items()}}
                        for a, b in (("clean", "duplicated"), ("clean", "contaminated"),
                                     ("duplicated", "contaminated")):
                            dn, lon, hin = boot_naive(V[a].reshape(-1), V[b].reshape(-1))
                            dc, loc, hic = boot_cluster(V[a], V[b])
                            rec[f"{b}_minus_{a}"] = {
                                "naive": {"diff": dn, "ci": [lon, hin],
                                          "significant": bool(lon > 0 or hin < 0)},
                                "cluster": {"diff": dc, "ci": [loc, hic],
                                            "significant": bool(loc > 0 or hic < 0)},
                            }
                        out[cell] = rec
                        rows.append((cell, rec))
                        print(f"  {cell}")

    def tally(pair, unit):
        hurt = sum(1 for _, r in rows
                   if r[pair][unit]["significant"] and r[pair][unit]["diff"] > 0)
        help_ = sum(1 for _, r in rows
                    if r[pair][unit]["significant"] and r[pair][unit]["diff"] < 0)
        return hurt, help_, len(rows) - hurt - help_

    summary = {}
    for pair in ("duplicated_minus_clean", "contaminated_minus_clean",
                 "contaminated_minus_duplicated"):
        summary[pair] = {u: dict(zip(("hurt", "helped", "no_effect"), tally(pair, u)))
                         for u in ("naive", "cluster")}
    out["_summary"] = summary

    op = os.path.join(R.RESULTS, "task3_three_way.json")
    json.dump(out, open(op, "w"), indent=2)

    L_ = []
    A_ = L_.append
    A_("TASK 3 -- THREE-WAY ROLLOUT COMPARISON: CLEAN / DUPLICATED / CONTAMINATED")
    A_("=" * 88)
    A_("")
    A_(f"  {len(rows)} cells = 2 arenas x 2 trajectory lengths x 2 checkpoints x 2 horizons")
    A_("            x 2 metrics.  POSITIVE diff = the second arm is WORSE.")
    A_("")
    A_("  Two resampling units are reported. 'cluster' resamples trajectories carrying all")
    A_("  three seeds and is the correct unit; 'naive' resamples the pooled seed x trajectory")
    A_("  vector and is what R-47's published counts used.")
    A_("")
    for pair, label in (("duplicated_minus_clean", "duplicated vs clean"),
                        ("contaminated_minus_clean", "contaminated vs clean"),
                        ("contaminated_minus_duplicated", "contaminated vs duplicated")):
        A_(f"  -- {label} " + "-" * (68 - len(label)))
        for u in ("naive", "cluster"):
            s = summary[pair][u]
            A_(f"     {u:<8} hurt {s['hurt']:>2} / helped {s['helped']:>2} / "
               f"no effect {s['no_effect']:>2}   (of {len(rows)})")
    A_("")
    A_("  -- cells where contamination HURT under the cluster unit --")
    bad = [c for c, r in rows
           if r["contaminated_minus_clean"]["cluster"]["significant"]
           and r["contaminated_minus_clean"]["cluster"]["diff"] > 0]
    A_("     " + (", ".join(bad) if bad else "NONE"))
    A_("")
    A_(f"  written: {R.rel(op)}")
    rp = os.path.join(R.RESULTS, "task3_three_way_report.txt")
    open(rp, "w").write("\n".join(L_) + "\n")
    print()
    print("\n".join(L_))


if __name__ == "__main__":
    main()
