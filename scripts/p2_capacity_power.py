"""
P2 -- what a CAPACITY-MATCHED trunk-sharing test can detect, measured before it runs.

WHY THIS EXISTS. §6.10 compares five independently-initialised full models against
five heads on one shared trunk and finds the independent ensemble better calibrated.
X-17 records that the two arms differ in capacity as well as in independence:
3,570,820 state-pathway parameters against 1,024,132, a factor of 3.49. σ is the
column the mechanism claim rests on, and capacity can raise σ. §6.10 bounds the
architectural effect; it does not isolate it, and that is the one limitation in §12
a reviewer can call cheap to fix.

M-49 fixes it: five independent members at reduced width, matched on total
state-pathway capacity. This script estimates what that comparison can detect, at
the sample size it will actually face, BEFORE the rule is committed and before any
of the five models exist.

That ordering is the whole point. M-43 was committed without it and returned a
verdict it was under-powered to return; the ledger records that as the second
instance after M-24, and the standing rule since is that no new rule enters git
without this estimate in its own text.

WHAT IS ESTIMATED, and by what.

  the width      the hidden size at which five independent members carry the same
                 state-pathway capacity as the shared-trunk arm. Searched over the
                 real constructor, not computed from a formula, because the head's
                 parameter count is a property of the released architecture config.

  the MDE        by SUBSAMPLING. Four trajectories are drawn at a time from the
                 twenty-trajectory in-sample pool, the paired log-ratio and the
                 paired coverage difference are recomputed on each draw, and the
                 spread across draws is the sampling variability the rule faces.
                 This is the same design M-43's post-hoc power check used and the
                 same one §6.7 reports, so the two are comparable.

  the caution    the twenty-trajectory pool is IN-SAMPLE for our arms, which
                 trained on eight of the ten episodes. Any power figure taken from
                 it and applied to a held-out comparison is an UPPER bound. P1
                 states this for M-44 and it is no less true here. It is written
                 into the rule.

The pairs used are cross-architecture -- the released checkpoint against our ens5
arms -- because that is the kind of contrast M-49 makes: two different ensemble
constructions whose errors decorrelate across trajectories, so less cancels in the
paired statistic and the SE is larger. Same-architecture seed pairs would give a
smaller, flattering number.

Writes results/p2_capacity_power.json.
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import torch  # noqa: E402
import rwm_data as R  # noqa: E402
import rwm_model as MDL  # noqa: E402
import rollout_eval as E  # noqa: E402
import rwm_metrics as MET  # noqa: E402
import score_reference as S  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p1_power_check as P1  # noqa: E402

OUT = "p2_capacity_power.json"
N_SUB = 4000            # subsample draws
SEEDS = (0, 1, 2)
DEPLOY_H = 100


def state_pathway_params(cfg, hidden, ensemble):
    c = copy.deepcopy(cfg)
    c["architecture_config"]["rnn_hidden_size"] = hidden
    m = MDL.build_from_config(c, ensemble_size=ensemble)
    return (sum(p.numel() for p in m.state_base.parameters())
            + sum(p.numel() for p in m.state_heads.parameters()))


def find_width(cfg, target, n_members, lo=32, hi=256):
    """The hidden size at which n_members independent models match `target`."""
    best = None
    for h in range(lo, hi + 1):
        tot = n_members * state_pathway_params(cfg, h, 1)
        if best is None or abs(tot - target) < abs(best[1] - target):
            best = (h, tot)
    return best


def main():
    rng = np.random.default_rng(20260829)
    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    ac = cfg["architecture_config"]

    # ---------------------------------------------------------- the width
    shared = state_pathway_params(cfg, ac["rnn_hidden_size"], 5)
    indep_full = 5 * state_pathway_params(cfg, ac["rnn_hidden_size"], 1)
    width, matched = find_width(cfg, shared, 5)
    per_member = matched // 5

    print("P2 — CAPACITY-MATCHED POWER, BEFORE THE RUNS")
    print("=" * 88)
    print(f"  shared-trunk arm, state pathway   : {shared:,} params "
          f"(1 trunk @ {ac['rnn_hidden_size']} + 5 heads)")
    print(f"  independent arm as run (§6.10)    : {indep_full:,} "
          f"({indep_full / shared:.2f}x — X-17's confound)")
    print(f"  capacity-matched width            : {width} hidden units")
    print(f"  five members at that width        : {matched:,} "
          f"({matched / shared:.4f}x the shared-trunk arm)")

    # ---------------------------------------------------------- the pools
    split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"),
                         verbose=False)
    pool20 = P1.load_pool(list(range(10)), "all ten episodes (in-sample; UPPER bound)")
    pool4 = P1.load_pool(sorted(split["holdout_episodes"]), "held-out pair (the real arena)")
    n20, n4 = pool20["n_traj"], pool4["n_traj"]

    ref = S.ReferenceRWM(torch.load(paths["ckpt"], map_location="cpu")
                         ["system_dynamics_state_dict"])
    ref.eval()
    models = {}
    for sd in SEEDS:
        w = f"runs/armA_seed{sd}_ens5/weights_2500.pt"
        if not os.path.exists(w):
            print(f"  MISSING {w} — cannot estimate; run stage 20h first")
            return 1
        m = S.ReferenceRWM(torch.load(w, map_location="cpu")["model_state_dict"])
        m.eval()
        models[f"ens5_seed{sd}"] = P1.score(m, pool20)
    models["released"] = P1.score(ref, pool20)

    sl = slice(P1.START, P1.START + DEPLOY_H)

    def rho(sc, i):
        e, s = sc["abs_err"][i, sl], sc["epi"][i, sl]
        ms = np.nanmean(s)
        return float(np.nanmean(e) / ms) if ms > 0 else np.nan

    def cov1(sc, i):
        e, s = sc["abs_err"][i, sl], sc["epi"][i, sl]
        return float(np.nanmean(e <= s))

    # ------------------------------------------------- subsampling estimate
    #
    # Draw n4 trajectories WITHOUT replacement from the twenty, recompute the
    # paired statistic, and take the spread across draws. Without replacement,
    # because the rule will face four distinct trajectories -- resampling with
    # replacement inside a draw would model a different design.
    cross = [(a, b) for a in models for b in models
             if a < b and ("released" in (a, b))]
    rows = []
    for a, b in cross:
        A, B = models[a], models[b]
        lr, cv = [], []
        for _ in range(N_SUB):
            i = rng.choice(n20, size=n4, replace=False)
            ra, rb = rho(A, i), rho(B, i)
            if np.isfinite(ra) and np.isfinite(rb) and ra > 0 and rb > 0:
                lr.append(np.log(ra / rb))
                cv.append(cov1(A, i) - cov1(B, i))
        lr, cv = np.asarray(lr), np.asarray(cv)
        rows.append({
            "pair": f"{a} vs {b}",
            "n_draws": int(len(lr)),
            "log_ratio_sd_across_subsamples": float(lr.std(ddof=1)),
            "coverage_diff_sd_pts": float(100 * cv.std(ddof=1)),
            "ratio_mde_multiplicative": float(np.exp(P1.mde(lr.std(ddof=1)))),
            "coverage_mde_pts": float(100 * P1.mde(cv.std(ddof=1))),
        })
        print(f"  subsample {a} vs {b}: ratio MDE {rows[-1]['ratio_mde_multiplicative']:.3f}x, "
              f"coverage MDE {rows[-1]['coverage_mde_pts']:.2f} pts")

    mde_ratio = float(max(r["ratio_mde_multiplicative"] for r in rows))
    mde_cov = float(max(r["coverage_mde_pts"] for r in rows))

    # The observed §6.10 effect, for comparison: is the rule powered to see an
    # effect the size of the one it is asked to re-test with capacity held fixed?
    R2 = json.load(open(os.path.join(R.RESULTS, "r2_independent_ensemble.json")))
    observed = float(R2["comparison"]["m44"]["ratio_gain"]) \
        if "ratio_gain" in R2["comparison"].get("m44", {}) else None
    if observed is None:
        observed = float(json.load(open(os.path.join(R.RESULTS, "paper_numbers.json")))
                         ["m44_ratio_gain"]["value"])

    print("=" * 88)
    print(f"  MDE at n_independent = {n4}, cross-architecture, by subsampling:")
    print(f"    overconfidence ratio : {mde_ratio:.3f}x")
    print(f"    +-1 sigma coverage   : {mde_cov:.2f} percentage points")
    print(f"  §6.10 observed, capacity UNMATCHED: {observed:.2f}x")
    print(f"  the rule is {'powered' if observed > mde_ratio else 'NOT powered'} "
          f"to see an effect the size of the one it re-tests")
    print(f"  CAUTION: the pool is in-sample for our arms; this is an UPPER bound "
          f"on power, so the MDE is a LOWER bound.")

    rec = {
        "committed_before": "any capacity-matched training run",
        "purpose": "M-49 — isolate trunk-sharing from capacity, which X-17 records "
                   "as the third axis M-44's contrast confounds",
        "capacity": {
            "shared_trunk_state_pathway_params": shared,
            "independent_as_run_params": indep_full,
            "independent_as_run_ratio": indep_full / shared,
            "matched_hidden_size": width,
            "reference_hidden_size": ac["rnn_hidden_size"],
            "matched_total_params": matched,
            "matched_per_member_params": per_member,
            "matched_ratio": matched / shared,
        },
        "arena": "out-of-sample held-out pair",
        "n_independent_faced": n4,
        "horizon": DEPLOY_H,
        "method": "subsampling without replacement, %d draws of %d trajectories "
                  "from the %d-trajectory pool" % (N_SUB, n4, n20),
        "pairs": rows,
        "mde_80pct_power": {
            "overconfidence_ratio_multiplicative": mde_ratio,
            "coverage_pts": mde_cov,
            "which": "cross-architecture, the largest across pairs (conservative)",
        },
        "observed_unmatched_ratio_gain": observed,
        "powered_for_observed_effect": bool(observed > mde_ratio),
        "caution": "the twenty-trajectory pool is IN-SAMPLE for our arms, which "
                   "trained on eight of the ten episodes. Power taken from it and "
                   "applied to the held-out arena is an UPPER bound, so this MDE "
                   "is a LOWER bound. Stated in M-49's own text.",
    }
    json.dump(rec, open(os.path.join(R.RESULTS, OUT), "w"), indent=2)
    print(f"\n  wrote results/{OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
