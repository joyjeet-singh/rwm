"""Part B — replace the binomial sign-test P-values with a permutation test.

The paper converts per-dimension sign counts (39/45, 45/45, ...) into P-values by
treating the 45 state dimensions as independent Bernoulli trials. They are not:
joint position, velocity and torque for one joint are physically coupled, and base
linear and angular velocity are coupled through the gait. The arithmetic is right
and the model is wrong, in the direction that overstates the evidence.

THE TEST. The null is "sigma carries no information about realised error". To draw
from it while preserving cross-dimension dependence, permute WHOLE TRAJECTORIES:
pair each trajectory's sigma with another trajectory's error. Within-trajectory
temporal structure and all cross-dimension coupling survive; only the sigma-error
association is broken. Recompute the per-dimension correlations, count positives,
and compare the observed count against that null distribution.

Where a model has three seeds the SAME trajectory permutation is applied to every
seed, so the unit of resampling is the trajectory, not the (seed, trajectory) pair.
Permuting the latter would inflate the effective sample size -- the same error M-27
records for the bootstrap.

RESOLUTION. With n trajectories there are n! pairings, so the smallest attainable
P-value is about 1/n!. At n=4 that is 1/24 = 0.042, and no permutation test on the
held-out arena can report anything below it however large the effect. The in-sample
arena (n=16) is run alongside for that reason and both are reported.

Writes results/task_b_permutation.json.
"""
import json
import math
import os
import sys
from itertools import permutations

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import torch  # noqa: E402
import rwm_data as R  # noqa: E402
import rollout_eval as E  # noqa: E402
import rwm_metrics as MET  # noqa: E402
import rwm_model as M  # noqa: E402
import score_reference as S  # noqa: E402

START, LEN = E.START_STEP, 400
# The paper's horizon grid (3.1). h=100 -- the method's own imagination rollout
# length -- carries the abstract and 6.2's headline, and was the one horizon with
# no permutation test: its cell printed "--" while the prose called the column
# "five tests on one family" and corrected over 25 cells. Six horizons make it
# 30, and the Holm thresholds below follow the family size rather than a typed one.
HORIZONS = (1, 8, 32, 100, 128, 368)
SEEDS = (0, 1, 2)
N_PERM = 20000
GROUPS = {"base lin vel": (0, 3), "base ang vel": (3, 6), "proj gravity": (6, 9),
          "joint pos": (9, 21), "joint vel": (21, 33), "joint torque": (33, 45)}

paths = R.repo_paths()
cfg = R.load_reference_config(paths["lite"])
data, ep = R.load_data(paths["csv"], verbose=False)
split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"), verbose=False)
ARENAS = {"out-of-sample": list(split["holdout_episodes"]),
          "in-sample": list(split["train_episodes"]),
          # All ten. The released checkpoint trained on all of them, so this is
          # the arena section 5.2 quotes for that model (D1); its permutation
          # P-values have to come from the same arena as its counts.
          "all-episodes": sorted(set(split["train_episodes"]) | set(split["holdout_episodes"]))}


def rollout(kind, starts):
    """Returns err, sig shaped (n_seed, n_traj, T, D)."""
    idx = np.asarray(starts)[:, None] + np.arange(LEN)[None, :]
    raw = data[idx]
    st = torch.as_tensor(R.normalise_state(raw[:, :, R.STATE_COLS],
                                           cfg["state_data_mean"], cfg["state_data_std"]),
                         dtype=torch.float32)
    ac = torch.as_tensor(raw[:, :, R.ACTION_COLS], dtype=torch.float32)
    if kind.startswith("released"):
        sd = torch.load(paths["ckpt"], map_location="cpu")["system_dynamics_state_dict"]
        m = S.ReferenceRWM(sd); m.eval()
        pred, alea, epi, _, _ = m.rollout_uncertainty(st.clone(), ac, START, action_offset=1)
        sig = alea if kind.endswith("aleatoric") else epi
        return (pred - st).abs().numpy()[None], sig.numpy()[None]
    errs, sigs = [], []
    for s in SEEDS:
        tag = "_nll" if kind == "nll" else ""
        arm = "B" if kind == "armB" else "A"
        m = M.build_from_config(cfg, ensemble_size=1)
        m.load_state_dict(torch.load(f"runs/arm{arm}_seed{s}{tag}/weights_2500.pt",
                                     map_location="cpu")["model_state_dict"], strict=True)
        m.eval()
        p, sg = m.rollout_full(st.clone(), ac, START, action_offset=1)
        errs.append((p - st).abs().numpy()); sigs.append(sg.numpy())
    return np.stack(errs), np.stack(sigs)


def prepare(err, sig):
    """Flatten seed+time per trajectory and precompute what a permutation needs.

    corr_d under a trajectory pairing pi has numerator
        sum_i <sig_pi(i), err_i>_d  -  N * mean(sig_d) * mean(err_d)
    and a denominator that does not depend on pi, because both marginals are
    unchanged by re-pairing. So the SIGN of the correlation -- all the count needs
    -- follows from the cross term alone.
    """
    ns, nt, T, D = err.shape
    # float64 throughout. The raw-cross-product form of the numerator,
    #     <sig, err> - N * mean(sig) * mean(err),
    # is catastrophically cancelling in float32: for a dimension whose true
    # correlation is near zero the two terms agree to ~7 significant figures and
    # the difference is noise. That flipped exactly one dimension of the
    # corrected (nll) arm (20 vs task1's 21) before this was fixed.
    e = np.transpose(err, (1, 0, 2, 3)).reshape(nt, ns * T, D).astype(np.float64)
    s = np.transpose(sig, (1, 0, 2, 3)).reshape(nt, ns * T, D).astype(np.float64)
    finite = np.isfinite(e) & np.isfinite(s)
    e = np.where(finite, e, 0.0); s = np.where(finite, s, 0.0)
    N = nt * e.shape[1]
    mean_e = e.reshape(-1, D).mean(0); mean_s = s.reshape(-1, D).mean(0)
    # Centre once. Re-pairing trajectories leaves both marginal means unchanged
    # (every trajectory contributes the same number of points), so the centred
    # cross-product IS the covariance numerator for any pairing -- no subtraction
    # afterwards, hence no cancellation.
    ec = e - mean_e; sc = s - mean_s
    cross = np.einsum('itd,jtd->ijd', sc, ec)        # cross[i,j,d] = cov-numerator
    var_s = (sc.reshape(-1, D) ** 2).sum(0)
    var_e = (ec.reshape(-1, D) ** 2).sum(0)
    valid = (var_s > 0) & (var_e > 0)
    return cross, N, mean_s, mean_e, valid


def count_for(perm, cross, N, mean_s, mean_e, valid, cols=None):
    num = cross[list(perm), range(cross.shape[1])].sum(0)   # already centred
    v = valid if cols is None else (valid & np.isin(np.arange(len(valid)), cols))
    return int(((num > 0) & v).sum()), int(v.sum())


def run(err, sig, rng):
    cross, N, ms, me, valid = prepare(err, sig)
    n = cross.shape[0]
    obs, ndim = count_for(range(n), cross, N, ms, me, valid)
    if n <= 7:
        perms = [p for p in permutations(range(n)) if list(p) != list(range(n))]
        exact = True
    else:
        perms = [tuple(rng.permutation(n)) for _ in range(N_PERM)]
        exact = False
    null = np.array([count_for(p, cross, N, ms, me, valid)[0] for p in perms])
    p_raw = float((null >= obs).mean())
    floor = 1.0 / (len(null) + 1)
    grp = 0
    for _, (a, b) in GROUPS.items():
        c, tot = count_for(range(n), cross, N, ms, me, valid, cols=list(range(a, b)))
        if tot and c > tot / 2:
            grp += 1
    k = obs
    tail = (sum(math.comb(ndim, i) for i in range(k, ndim + 1)) if 2 * k >= ndim
            else sum(math.comb(ndim, i) for i in range(0, k + 1)))
    return {"observed": obs, "n_dims": ndim, "n_traj": n, "n_null": len(null),
            "exact_enumeration": exact, "p_permutation": max(p_raw, floor),
            "p_floor": floor, "at_floor": bool(p_raw < floor),
            "null_mean": float(null.mean()), "null_max": int(null.max()),
            "p_binomial_two_sided": min(1.0, 2.0 * tail / 2 ** ndim),
            "group_count": grp, "n_groups": len(GROUPS)}


def main():
    rng = np.random.default_rng(0)
    MODELS = [("faithful (mse)", "mse"), ("corrected (nll)", "nll"),
              ("teacher-forced armB", "armB"),
              ("released aleatoric", "released_aleatoric"),
              ("released EPISTEMIC", "released_epistemic")]
    out = {"method": ("trajectory-level permutation; the null pairs each trajectory's sigma "
                      "with another trajectory's error, preserving cross-dimension dependence"),
           "arenas": {}}
    print("PART B — PERMUTATION TEST OVER TRAJECTORIES")
    print("=" * 108)
    for arena, eps in ARENAS.items():
        starts = MET.non_overlapping_starts(ep, eps, LEN)
        n = len(starts)
        floor = 1.0 / (math.factorial(n) if n <= 7 else N_PERM + 1)
        print(f"\n  {arena.upper()}  n_traj={n}  n_independent={MET.n_independent(starts, LEN)}"
              f"  attainable P floor ~{floor:.3g}")
        print(f"    {'model':<22}{'h':>5}{'count':>10}{'binomial P':>13}{'perm P':>10}"
              f"{'null mean':>11}{'groups':>9}{'floor?':>8}")
        A = {}
        for label, kind in MODELS:
            err, sig = rollout(kind, starts)
            per_h = {}
            for h in HORIZONS:
                sl = slice(START, START + h)
                r = run(err[:, :, sl], sig[:, :, sl], rng)
                per_h[str(h)] = r
                print(f"    {label:<22}{h:>5}{r['observed']:>6}/{r['n_dims']:<3}"
                      f"{r['p_binomial_two_sided']:>13.2e}{r['p_permutation']:>10.4f}"
                      f"{r['null_mean']:>11.1f}{r['group_count']:>6}/{r['n_groups']:<2}"
                      f"{'  yes' if r['at_floor'] else '  no':>8}")
            A[label] = per_h
        # Holm-Bonferroni within the arena. The paper quotes many dimension-count
        # cells; they are one family and must be corrected as one. The floor
        # matters here: at n=4 no cell can beat a Holm threshold below 1/4! at
        # all, so an arena can fail the correction by design rather than by
        # evidence. That is reported, not hidden.
        fam = sorted(((f"{lab} h={h}", A[lab][str(h)]["p_permutation"])
                      for lab in A for h in HORIZONS), key=lambda x: x[1])
        msz, steps, still = len(fam), [], True
        for i, (cell, pv) in enumerate(fam):
            thr = 0.05 / (msz - i)
            still = still and pv <= thr
            steps.append({"cell": cell, "p": pv, "holm_threshold": thr, "rejected": still})
        out["arenas"][arena] = {"n_traj": n, "p_floor": floor,
                                "n_independent": int(MET.n_independent(starts, LEN)),
                                "holm": {"family_size": msz, "alpha": 0.05,
                                         "smallest_threshold": 0.05 / msz,
                                         "floor_exceeds_smallest_threshold": bool(floor > 0.05 / msz),
                                         "n_rejected": sum(s["rejected"] for s in steps),
                                         "steps": steps},
                                "models": A}
        h = out["arenas"][arena]["holm"]
        print(f"    Holm-Bonferroni over {msz} cells at alpha=0.05: "
              f"{h['n_rejected']} rejected"
              + ("   [floor %.4g exceeds the smallest threshold %.4g -- this arena "
                 "cannot reject by design]" % (floor, h["smallest_threshold"])
                 if h["floor_exceeds_smallest_threshold"] else "")
              + f"\n      smallest p in family: {fam[0][0]} p={fam[0][1]:.4f} "
                f"(threshold {0.05/msz:.5f})")
    op = os.path.join(R.RESULTS, "task_b_permutation.json")
    json.dump(out, open(op, "w"), indent=2)
    print(f"\n  wrote {R.rel(op)}")


if __name__ == "__main__":
    main()
