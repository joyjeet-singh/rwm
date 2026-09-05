"""
R2 -- five independently-initialised models scored as an ensemble, and M-44's verdict.

X-12 established that the released ensemble is five heads on ONE GRU trunk:
89.15% of every member's state-prediction pathway is numerically identical to
every other's, and an autoregressive rollout feeds the ensemble mean back into a
single hidden state, so the members never diverge dynamically. That is a
candidate mechanism for the epistemic miscalibration 6.3 leaves unexplained.

Whether it is THE mechanism is what M-44 tests, and M-44 was committed to git
before any of the artifacts below existed.

THE CHEAP CONTRAST. Training a genuinely independent five-model ensemble the
usual way would cost roughly 17 CPU-hours across three seeds. Instead: Arm A at
ensemble size 1 already exists at seeds 0, 1 and 2; seeds 3 and 4 were added at
about 1.2 h each, and the five are scored together as an ensemble AT EVALUATION
TIME. No new training code, no new architecture, and the disagreement across five
independently-initialised full models is exactly the contrast we want against
five heads on a shared trunk.

THE ROLLOUT PROTOCOL, which has to mirror the shared-trunk one or the comparison
means nothing. At each forecast step every member sees the same input state, each
maintains ITS OWN recurrent hidden state, and the ensemble MEAN is fed back to all
five. That is identical to the shared-trunk protocol in every respect except the
one under test: here the trunk is replicated five times instead of shared, so the
members' hidden states can diverge.

Writes results/r2_independent_ensemble.json, which discharges M-44.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import warnings  # noqa: E402
import numpy as np  # noqa: E402
import torch  # noqa: E402
import rwm_data as R  # noqa: E402
import rollout_eval as E  # noqa: E402
import rwm_metrics as MET  # noqa: E402
import score_reference as S  # noqa: E402

HORIZONS = (1, 8, 32, 100, 128, 368)
START, LEN, N_BOOT = E.START_STEP, 400, 20000
INDEP_SEEDS = (0, 1, 2, 3, 4)          # the five independent ens1 models
SHARED_SEEDS = (0, 1, 2)               # the shared-trunk ens5 arms

# M-44's thresholds, quoted from the committed rule. The cross-architecture
# (conservative) calibration is the binding one, as the rule states.
MDE_RATIO = 1.45       # results/p1_power_check.json
MDE_COV_PTS = 2.26
MDE_SOURCE = "results/p1_power_check.json, cross-architecture calibration"


def cboot_paired(fn, n, rng, n_boot=N_BOOT):
    v = [x for x in (fn(rng.integers(0, n, n)) for _ in range(n_boot))
         if x is not None and np.isfinite(x)]
    if len(v) < 2:
        return None, None, 0
    return float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5)), len(v)


@torch.no_grad()
def rollout_independent(models, state, action, start_step=START, action_offset=1):
    """
    Drive N independent models in lockstep, feeding the ensemble MEAN back.

    Mirrors ReferenceRWM.rollout_uncertainty exactly, except that the per-member
    recurrent state is per MEMBER rather than shared. Returns the same tuple.

    ReferenceRWM.step computes means.std(0) internally for its own epistemic
    term. With ensemble=1 that is a std over one element: NaN, with a warning.
    We never read it -- the whole point here is that the spread is taken across
    the five MODELS, below -- so the warning is noise about an unused value. It
    is suppressed narrowly, and every output is asserted finite by the caller.
    """
    B, T, D = state.shape
    pred = state.clone()
    alea = torch.zeros(B, T, D)
    epi = torch.zeros(B, T, D)
    epi_s = torch.zeros(B, T)
    alea_s = torch.zeros(B, T)
    h = [None] * len(models)
    ha = [None] * len(models)
    warnings.filterwarnings("ignore", message="std\\(\\): degrees of freedom is <= 0")
    for i in range(start_step, T):
        if i > start_step:
            s_in = pred[:, i - 1:i]
            a_in = action[:, i - 1 + action_offset:i + action_offset]
        else:
            s_in = pred[:, i - start_step:i]
            a_in = action[:, i - start_step + action_offset:i + action_offset]
        if a_in.shape[1] != s_in.shape[1]:
            a_in = action[:, -s_in.shape[1]:]
        means, sigmas = [], []
        for j, m in enumerate(models):
            mu, _, _, _, h[j], ha[j] = m.step(s_in, a_in, h[j], ha[j], False)
            means.append(mu)
            sigmas.append(m.last_sigma)
        M = torch.stack(means)                      # (n_members, B, 45)
        Sg = torch.stack(sigmas)
        pred[:, i] = M.mean(0)
        alea[:, i] = Sg.mean(0)                     # system_dynamics.py:125
        epi[:, i] = M.std(0)                        # system_dynamics.py:126, per-dim
        epi_s[:, i] = M.std(0).sum(-1)              # the scalar envs/base.py:166 applies
        alea_s[:, i] = Sg.mean(0).sum(-1)
    return pred, alea, epi, alea_s, epi_s


def load_ens1(seed, tag="", hidden=256):
    """One ens1 model.

    `tag` and `hidden` exist so that M-49's capacity-matched arm can be scored by
    THIS code rather than by a copy of it. The comparison is only interpretable if
    the rollout protocol, the bootstrap, the horizons and the arena are identical
    between the two arms, and the surest way to guarantee that is one
    implementation. Defaults reproduce M-44's discharged run exactly.
    """
    w = f"runs/armA_seed{seed}{tag}/weights_2500.pt"
    assert os.path.exists(w), (
        f"missing {w} — run "
        f"{'./run_m49_matched.sh' if tag else './run_indep_ens.sh'}")
    sd = torch.load(w, map_location="cpu")["model_state_dict"]
    m = S.ReferenceRWM(sd, ensemble=1, hidden=hidden)
    m.eval()
    return m


def block(err, sig, sl):
    e, g = err[:, sl], sig[:, sl]
    return {"ratio_err_over_sigma": float(np.nanmean(e) / np.nanmean(g)),
            "coverage_pm1": float(np.nanmean(e <= g)),
            "coverage_pm2": float(np.nanmean(e <= 2 * g)),
            "mean_sigma": float(np.nanmean(g)), "mean_abs_err": float(np.nanmean(e))}


def main(tag="", hidden=256, out_name="r2_independent_ensemble.json",
         rule="M-44", mde_ratio=None, mde_cov=None, mde_source=None):
    # mde_source travels WITH the thresholds. It was hardcoded to M-44's power
    # file while mde_ratio and mde_cov were already parameters, so an arm scored
    # against another rule's MDE recorded the wrong provenance for it -- the same
    # shape of defect the mde_ratio comment above records.
    mde_ratio = MDE_RATIO if mde_ratio is None else mde_ratio
    mde_cov = MDE_COV_PTS if mde_cov is None else mde_cov
    mde_source = MDE_SOURCE if mde_source is None else mde_source
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

    print(f"R2 — THE INDEPENDENT-INITIALISATION ENSEMBLE, AND {rule}'s VERDICT"
          + (f"   [capacity-matched, hidden {hidden}]" if hidden != 256 else "")
          + ("   [combined arm: gaussian_nll members]" if rule == "M-68" else ""))
    print("=" * 104)
    print(f"  out-of-sample, episodes {hold}, {n_traj} trajectories, "
          f"n_independent = {n_ind}\n")

    out = {"design": {
        "arena": "out-of-sample held-out pair", "holdout_episodes": hold,
        "n_trajectories": n_traj, "n_independent": n_ind,
        "independent_seeds": list(INDEP_SEEDS), "shared_trunk_seeds": list(SHARED_SEEDS),
        "iterations": 2500, "traj_len": LEN, "start_step": START, "action_offset": 1,
        "n_boot": N_BOOT, "bootstrap_unit": "whole trajectory (M-27)",
        "protocol": "every member sees the same input state and keeps its own recurrent "
                    "hidden state; the ensemble mean is fed back to all members. "
                    "Identical to the shared-trunk protocol except that the trunk is "
                    "replicated rather than shared.",
        "mde_ratio": mde_ratio, "mde_coverage_pts": mde_cov,
        # NOT "rule": the m44 block already has that key and it holds a sentence
        # ("M-44, committed 2026-08-23 before any artifact here existed"). The
        # first version of this parameterisation overwrote it with a bare
        # identifier -- a record destroyed to make room for a label.
        "governing_rule": rule, "arm_tag": tag or "(released width)",
        "hidden_size": hidden,
        "mde_source": mde_source,
    }, "independent": {}, "shared_trunk": {}, "comparison": {}, "m44": {}}

    # --------------------------------------------- the independent ensemble
    models = [load_ens1(s, tag, hidden) for s in INDEP_SEEDS]
    print(f"  loaded {len(models)} independently-initialised ens1 models: "
          f"seeds {list(INDEP_SEEDS)}")
    pred, alea, epi, alea_s, epi_s = rollout_independent(models, st.clone(), ac)
    err_i = (pred - st).abs().numpy().astype(np.float64)
    epi_i = epi.numpy().astype(np.float64)
    epis_i = epi_s.numpy().astype(np.float64)
    # A five-member independent ensemble MUST have a non-zero spread; a zero would
    # mean the five models are the same object and the whole contrast is void.
    assert epi_i[:, START:].mean() > 0, "the independent ensemble has zero spread"
    assert np.isfinite(err_i[:, START:]).all(), "non-finite error in the independent rollout"
    assert np.isfinite(epi_i[:, START:]).all(), "non-finite spread in the independent rollout"

    # ------------------------------------------------ the shared-trunk arms
    shared = {}
    for s in SHARED_SEEDS:
        w = f"runs/armA_seed{s}_ens5/weights_2500.pt"
        m = S.ReferenceRWM(torch.load(w, map_location="cpu")["model_state_dict"])
        m.eval()
        p, a, e, _, es = m.rollout_uncertainty(st.clone(), ac, START, action_offset=1)
        shared[s] = {"err": (p - st).abs().numpy().astype(np.float64),
                     "epi": e.numpy().astype(np.float64),
                     "epi_s": es.numpy().astype(np.float64)}
    print(f"  loaded {len(shared)} shared-trunk ens5 arms: seeds {list(SHARED_SEEDS)}\n")

    # -------------------------------------------------------- the table
    print("  Independent-init ensemble against the shared-trunk arms, same trajectories")
    print(f"    {'h':>5} {'independent err/σ':>22} {'shared-trunk err/σ':>22} "
          f"{'ratio':>8} {'indep ±1σ':>11} {'shared ±1σ':>11}")
    print("    " + "-" * 92)
    rng = np.random.default_rng(0)
    for h in HORIZONS:
        sl = slice(START, START + h)
        bi = block(err_i, epi_i, sl)
        bs = [block(shared[s]["err"], shared[s]["epi"], sl) for s in SHARED_SEEDS]
        mean_ratio_s = float(np.mean([b["ratio_err_over_sigma"] for b in bs]))
        mean_cov_s = float(np.mean([b["coverage_pm1"] for b in bs]))
        out["independent"][str(h)] = bi
        out["shared_trunk"][str(h)] = {
            "per_seed": {str(s): b for s, b in zip(SHARED_SEEDS, bs)},
            "mean_ratio": mean_ratio_s, "mean_cov1": mean_cov_s,
            "mean_cov2": float(np.mean([b["coverage_pm2"] for b in bs]))}
        print(f"    {h:>5} {bi['ratio_err_over_sigma']:>22,.1f} {mean_ratio_s:>22,.1f} "
              f"{bi['ratio_err_over_sigma'] / mean_ratio_s:>8.3f} "
              f"{100 * bi['coverage_pm1']:>10.2f}% {100 * mean_cov_s:>10.2f}%")

    # ------------------------------- the paired comparison at the deployment horizon
    DEPLOY = json.load(open(os.path.join(R.RESULTS, "v2_deployment_horizon.json"))
                       )["verdict"]["deployment_horizon_is"]
    sl = slice(START, START + DEPLOY)
    print(f"\n  M-44's governing comparison at h = {DEPLOY}, paired over the same "
          f"trajectories")
    print(f"    {'vs seed':>9} {'ratio (indep/shared)':>22} {'95% CI':>26} "
          f"{'Δcoverage pts':>15} {'95% CI':>26}")
    print("    " + "-" * 102)

    def rho(e, g, i):
        ms = np.nanmean(g[i, sl])
        return float(np.nanmean(e[i, sl]) / ms) if ms > 0 else np.nan

    def cov(e, g, i):
        return float(np.nanmean(e[i, sl] <= g[i, sl]))

    per_pair = {}
    for s in SHARED_SEEDS:
        es, gs = shared[s]["err"], shared[s]["epi"]
        full = np.arange(n_traj)
        lr = float(np.log(rho(err_i, epi_i, full) / rho(es, gs, full)))
        dc = 100 * (cov(err_i, epi_i, full) - cov(es, gs, full))
        lo1, hi1, _ = cboot_paired(
            lambda i: np.log(rho(err_i, epi_i, i) / rho(es, gs, i)), n_traj,
            np.random.default_rng(100 + s))
        lo2, hi2, _ = cboot_paired(
            lambda i: 100 * (cov(err_i, epi_i, i) - cov(es, gs, i)), n_traj,
            np.random.default_rng(200 + s))
        # E8. The FOUR trajectory values each interval is computed from.
        #
        # A cluster bootstrap over four units has 4**4 = 256 distinct resamples,
        # quantised tails and poor coverage. The paper says so and prints the
        # interval anyway. Printing the underlying values costs nothing, is more
        # informative, and pre-empts the objection -- and §5 asserts that wherever
        # this paper reports an interval at n_independent = 4 the underlying
        # values are in the artifact it came from. That sentence was FALSE when
        # written: only a1_ab_by_horizon.json carried them.
        _per_traj_lr = [float(np.log(rho(err_i, epi_i, [t]) / rho(es, gs, [t])))
                        for t in range(n_traj)]
        _per_traj_dc = [float(100 * (cov(err_i, epi_i, [t]) - cov(es, gs, [t])))
                        for t in range(n_traj)]
        per_pair[str(s)] = {
            "log_ratio_per_trajectory": _per_traj_lr,
            "ratio_per_trajectory": [float(np.exp(x)) for x in _per_traj_lr],
            "coverage_diff_pts_per_trajectory": _per_traj_dc,
            "log_ratio": lr, "ratio": float(np.exp(lr)),
            "log_ratio_ci": [lo1, hi1],
            "ratio_ci": [float(np.exp(lo1)), float(np.exp(hi1))],
            "ratio_excludes_zero": bool(hi1 < 0 or lo1 > 0),
            "ratio_improves": bool(lr < 0),
            # mde_ratio, NOT the module constant. These read MDE_RATIO and
            # MDE_COV_PTS -- M-44's thresholds -- so when main() was parameterised
            # for M-49 the verdict was computed against the WRONG RULE's minimum
            # detectable effect. M-49's is 2.004x and M-44's is 1.45x, and the
            # observed improvement is 1.79x: it passes one and fails the other,
            # and the printed conditions said "yes" beside a mean the same block
            # printed as below threshold. Same shape as M-53 -- a rule naming one
            # statistic and the code applying another.
            "ratio_beats_mde": bool(np.exp(-lr) >= mde_ratio),
            "coverage_diff_pts": dc, "coverage_ci_pts": [lo2, hi2],
            "coverage_excludes_zero": bool(lo2 > 0 or hi2 < 0),
            "coverage_improves": bool(dc > 0),
            "coverage_beats_mde": bool(abs(dc) >= mde_cov),
        }
        print(f"    {s:>9} {np.exp(lr):>22.3f} "
              f"{f'[{np.exp(lo1):.3f}, {np.exp(hi1):.3f}]':>26} {dc:>15.2f} "
              f"{f'[{lo2:.2f}, {hi2:.2f}]':>26}")
    # WHERE THE IMPROVEMENT COMES FROM.
    #
    # rho = mean|error| / mean sigma, so a lower rho can mean a larger sigma OR a
    # smaller error, and only the first is the trunk-sharing mechanism. Five
    # independent models also DENOISE better than five heads on one trunk, which
    # is an ordinary ensembling effect and not the thing under test. Splitting the
    # log improvement into the two additive parts is the only honest way to
    # report it, and it changes the reading at long horizon.
    decomp = {}
    for h in HORIZONS:
        i = out["independent"][str(h)]
        sd_ = out["shared_trunk"][str(h)]["per_seed"].values()
        se = float(np.mean([x["mean_abs_err"] for x in sd_]))
        ss = float(np.mean([x["mean_sigma"] for x in sd_]))
        sig_r = i["mean_sigma"] / ss                 # >1 means a larger sigma
        err_r = se / i["mean_abs_err"]               # >1 means a smaller error
        tot = sig_r * err_r
        lt = np.log(tot)
        decomp[str(h)] = {
            "sigma_ratio_indep_over_shared": sig_r,
            "error_ratio_shared_over_indep": err_r,
            "total_rho_improvement": float(tot),
            "share_from_sigma": float(np.log(sig_r) / lt) if lt > 0 else None,
            "share_from_accuracy": float(np.log(err_r) / lt) if lt > 0 else None,
            "indep_mean_sigma": i["mean_sigma"], "shared_mean_sigma": ss,
            "indep_mean_abs_err": i["mean_abs_err"], "shared_mean_abs_err": se,
        }
    out["decomposition"] = decomp
    print(f"\n  Where the improvement comes from — rho is error over sigma, so both "
          f"can move")
    print(f"    {'h':>5} {'sigma x':>10} {'accuracy x':>12} {'total x':>10} "
          f"{'from sigma':>12} {'from accuracy':>15}")
    for h in HORIZONS:
        d_ = decomp[str(h)]
        print(f"    {h:>5} {d_['sigma_ratio_indep_over_shared']:>10.3f} "
              f"{d_['error_ratio_shared_over_indep']:>12.3f} "
              f"{d_['total_rho_improvement']:>10.3f} "
              f"{100 * d_['share_from_sigma']:>11.1f}% "
              f"{100 * d_['share_from_accuracy']:>14.1f}%")

    out["comparison"] = {"horizon": DEPLOY, "per_shared_seed": per_pair}

    # --------------------------------------------------------- M-44's verdict
    # Applied exactly as committed. The all-three convention is the one M-43 used:
    # a condition holds only if it holds against every shared-trunk seed. That is
    # stricter than pooling and cannot be gamed by a favourable seed.
    P = list(per_pair.values())
    ratio_better = all(p["ratio_improves"] for p in P)
    ratio_excl = all(p["ratio_excludes_zero"] for p in P)
    ratio_mde = all(p["ratio_beats_mde"] for p in P)
    cov_better = all(p["coverage_improves"] for p in P)
    cov_excl = all(p["coverage_excludes_zero"] for p in P)
    cov_mde = all(p["coverage_beats_mde"] for p in P)

    supported = ratio_better and ratio_excl and ratio_mde and cov_better and cov_excl and cov_mde
    # "the two quantities disagree in direction" -> unresolvable
    unresolvable = (ratio_better != cov_better) and not supported

    # M-49 DEFINES ITS OWN THREE OUTCOMES and they are not M-44's.
    #
    # M-44 asks whether trunk-sharing is the mechanism and answers SUPPORTED /
    # NOT SUPPORTED / UNRESOLVABLE. M-49 asks whether that survives capacity
    # matching and answers MECHANISM SURVIVES CAPACITY MATCHING / CAPACITY
    # EXPLAINS IT / UNDER-POWERED -- and it defines the third branch explicitly,
    # because its MDE is almost exactly the size of the effect it re-tests and it
    # said so before the runs.
    #
    # Emitting M-44's vocabulary here would have published "MECHANISM NOT
    # SUPPORTED" for a result in which the matched ensemble is better on every
    # pair, every interval excludes zero, and coverage clears its own MDE --
    # failing only the ratio limb, by 1.79x against 2.004x. That is far more
    # damning than the truth and it is not the verdict the rule defines.
    verdict = ("MECHANISM SUPPORTED" if supported
               else "UNRESOLVABLE — the two quantities disagree in direction" if unresolvable
               else "MECHANISM NOT SUPPORTED")

    out["m44"] = {
        "rule": "M-44, committed 2026-08-23 before any artifact here existed",
        "horizon": DEPLOY,
        "convention": "a condition holds only if it holds against EVERY shared-trunk "
                      "seed, the same all-three convention M-43 used",
        "conditions": {
            "overconfidence_lower_in_all": ratio_better,
            "overconfidence_interval_excludes_zero_in_all": ratio_excl,
            "overconfidence_improvement_at_least_mde": ratio_mde,
            "coverage_higher_in_all": cov_better,
            "coverage_interval_excludes_zero_in_all": cov_excl,
            "coverage_shift_at_least_mde": cov_mde,
        },
        "mde_ratio": mde_ratio, "mde_coverage_pts": mde_cov,
        "mde_source": mde_source,
        # NOT "rule": the m44 block already has that key and it holds a sentence
        # ("M-44, committed 2026-08-23 before any artifact here existed"). The
        # first version of this parameterisation overwrote it with a bare
        # identifier -- a record destroyed to make room for a label.
        "governing_rule": rule, "arm_tag": tag or "(released width)",
        "hidden_size": hidden,
        "supported": supported, "unresolvable": unresolvable, "verdict": verdict,
        "mean_ratio_improvement": float(np.exp(-np.mean([p["log_ratio"] for p in P]))),
        "mean_coverage_gain_pts": float(np.mean([p["coverage_diff_pts"] for p in P])),
        "design_limitation": (
            "independently-seeded runs differ in BOTH initialisation and data ordering, "
            "whereas the shared-trunk heads differ only in head initialisation. This "
            "comparison therefore conflates trunk-sharing with data-order diversity and "
            "BOUNDS the effect rather than isolating it. If the overconfidence factor "
            "barely moves despite that generous handicap, the finding is strong in the "
            "direction of 'architecture is not the explanation'. If it moves a lot, the "
            "design flaw is identified but not cleanly attributed."),
    }
    if rule == "M-49":
        if supported:
            verdict = "MECHANISM SURVIVES CAPACITY MATCHING"
        elif ratio_better and cov_better and (ratio_excl or cov_excl):
            verdict = "UNDER-POWERED — favours the matched ensemble by less than the MDE"
        else:
            verdict = "CAPACITY EXPLAINS IT"
        out["m44"]["verdict"] = verdict

    # M-68 DEFINES FOUR BRANCHES, APPLIED IN ORDER, FIRST MATCH WINS.
    #
    # They are not M-44's and not M-49's, so they are computed here rather than
    # squeezed into the vocabulary above. Everything below reads the rule as
    # committed at 68bb683 and nothing here was added or loosened after the data
    # existed.
    #
    # WHICH SIGMA. `epi` is the standard deviation ACROSS the five members' mean
    # predictions -- the epistemic term -- not the aleatoric head's output. That
    # is what block() divides the error by and what coverage_pm1 counts against,
    # and it is what M-68 names ("rho = mean |error| / mean sigma_epistemic").
    # The combined arm is the first arm here that carries both, so the artifact
    # says so rather than leaving it to be inferred.
    #
    # CONDITION (e). The rule's Governing statistics block states globally that
    # "a condition holds only if it holds against every one of the three
    # shared-trunk seeds". (e) is a condition, so a horizon counts only when BOTH
    # statistics improve there against ALL THREE seeds. The looser per-seed
    # reading -- four horizons for seed 0, a different four for seed 1 -- is not
    # applied.
    if rule == "M-68":
        dir_h = {}
        for h in HORIZONS:
            bi_ = out["independent"][str(h)]
            ps_ = out["shared_trunk"][str(h)]["per_seed"]
            r_all = all(bi_["ratio_err_over_sigma"] < ps_[str(s)]["ratio_err_over_sigma"]
                        for s in SHARED_SEEDS)
            c_all = all(bi_["coverage_pm1"] > ps_[str(s)]["coverage_pm1"]
                        for s in SHARED_SEEDS)
            dir_h[str(h)] = {
                "overconfidence_lower_vs_all_three": bool(r_all),
                "coverage_higher_vs_all_three": bool(c_all),
                "both_improve_vs_all_three": bool(r_all and c_all),
            }
        n_dir = sum(1 for v in dir_h.values() if v["both_improve_vs_all_three"])
        cond_e = bool(n_dir >= 4)

        # (a)-(d) at the governing horizon, against every shared-trunk seed.
        cond_a = ratio_mde                       # improvement factor >= mde_ratio
        cond_b = ratio_excl
        cond_c = all(p["coverage_diff_pts"] >= mde_cov for p in P)
        cond_d = cov_excl

        # Branch 3: the whole interval sits BELOW the horizon's MDE. The interval
        # on the improvement factor is [exp(-hi), exp(-lo)] because log_ratio is
        # indep-over-shared and improvement is its reciprocal.
        ratio_ci_below = any(float(np.exp(-p["log_ratio_ci"][0])) < mde_ratio for p in P)
        cov_ci_below = any(p["coverage_ci_pts"][1] < mde_cov for p in P)

        if not (ratio_better and cov_better):
            branch, verdict = 1, "THE COMBINATION DOES NOT IMPROVE CALIBRATION"
        elif cond_a and cond_b and cond_c and cond_d and cond_e:
            branch, verdict = 2, "THE COMBINATION IMPROVES CALIBRATION"
        elif ratio_ci_below or cov_ci_below:
            branch, verdict = 3, "THE COMBINATION DOES NOT IMPROVE CALIBRATION"
        else:
            branch, verdict = 4, "UNDERPOWERED"
        out["m68"] = {
            "rule": "M-68, committed 68bb683 2026-09-05T21:49:41+05:30, before "
                    "runs/armA_seed3_nll and runs/armA_seed4_nll existed",
            "horizon": DEPLOY,
            "sigma_used_for_coverage":
                "the standard deviation across the five members' mean predictions, "
                "taken per state dimension, rather than the aleatoric head's output",
            "condition_e_reading":
                "global all-three convention: a horizon counts only when BOTH "
                "statistics improve there against ALL THREE shared-trunk seeds",
            "conditions": {
                "a_overconfidence_improvement_at_least_mde": bool(cond_a),
                "b_overconfidence_interval_excludes_zero": bool(cond_b),
                "c_coverage_gain_at_least_mde": bool(cond_c),
                "d_coverage_interval_excludes_zero": bool(cond_d),
                "e_both_improve_at_four_of_six_horizons": cond_e,
            },
            "direction_by_horizon": dir_h,
            "n_horizons_both_improve_vs_all_three": n_dir,
            "branch1_wrong_direction_at_governing_horizon":
                bool(not (ratio_better and cov_better)),
            "branch3_interval_wholly_below_mde": {
                "overconfidence": bool(ratio_ci_below), "coverage": bool(cov_ci_below)},
            "branch": branch, "verdict": verdict,
            "mde_ratio": mde_ratio, "mde_coverage_pts": mde_cov,
            "mde_source": mde_source,
        }

        # THE OBJECTIVE ISOLATED — WITH AN INTERVAL, AND AGAINST THIS DESIGN'S MDE.
        #
        # M-68 scores this arm against the SHARED-TRUNK arms, so its verdict
        # measures the two fixes TOGETHER. The comparison that isolates the
        # objective is against 6.10's independent-`mse` arm, which differs from
        # this one in the loss type and in nothing else: the same five seeds, the
        # same rollout protocol, the same trajectories, this same function. It is
        # reported alongside and cannot move the verdict.
        #
        # It was first published as a bare point estimate, and two readers flagged
        # the same overclaim: 1.044x and +0.22 points were being read as "the
        # objective contributes nothing" when both sit far BELOW the minimum
        # detectable effect this design fixed in advance (1.218x, 2.50 points).
        # A sub-MDE point estimate licenses "not detectable at n_independent = 4",
        # never "absent" -- M-24 and M-43 are this project's own records of that
        # error, and M-68 branch 4 exists to say UNDERPOWERED rather than NULL. So
        # the comparison now carries the SAME 95% cluster bootstrap over WHOLE
        # TRAJECTORIES (M-27; never trajectory x step) that every governing
        # comparison above uses, and the artifact states whether it can resolve
        # the effect rather than leaving the reader to assume it did.
        mse_models = [load_ens1(s, "", 256) for s in INDEP_SEEDS]
        pm, _, epm, _, _ = rollout_independent(mse_models, st.clone(), ac)
        err_m = (pm - st).abs().numpy().astype(np.float64)
        epi_m = epm.numpy().astype(np.float64)
        assert np.isfinite(err_m[:, START:]).all(), "non-finite error in the mse rollout"
        allt = np.arange(n_traj)
        o_lr = float(np.log(rho(err_i, epi_i, allt) / rho(err_m, epi_m, allt)))
        o_dc = float(100 * (cov(err_i, epi_i, allt) - cov(err_m, epi_m, allt)))
        o_lo1, o_hi1, _ = cboot_paired(
            lambda i: np.log(rho(err_i, epi_i, i) / rho(err_m, epi_m, i)), n_traj,
            np.random.default_rng(300))
        o_lo2, o_hi2, _ = cboot_paired(
            lambda i: 100 * (cov(err_i, epi_i, i) - cov(err_m, epi_m, i)), n_traj,
            np.random.default_rng(400))
        # E8 again: the four trajectory values each interval is built from, in the
        # artifact, because 5 asserts that of every interval this paper prints at
        # n_independent = 4.
        o_ratio_mag = float(max(np.exp(o_lr), np.exp(-o_lr)))
        out["m68"]["objective_isolated"] = {
            "against": "results/r2_independent_ensemble.json — the same five seeds "
                       "under mse, same protocol, same trajectories, same script",
            "horizon": DEPLOY,
            "governing": False,
            "ratio_multiplicative": float(np.exp(o_lr)),
            "ratio_ci": [float(np.exp(o_lo1)), float(np.exp(o_hi1))],
            "ratio_ci_excludes_one": bool(o_hi1 < 0 or o_lo1 > 0),
            "ratio_improves": bool(o_lr < 0),
            "ratio_magnitude_vs_mde": o_ratio_mag,
            "ratio_below_mde": bool(o_ratio_mag < mde_ratio),
            "coverage_diff_pts": o_dc,
            "coverage_ci_pts": [o_lo2, o_hi2],
            "coverage_ci_excludes_zero": bool(o_lo2 > 0 or o_hi2 < 0),
            "coverage_below_mde": bool(abs(o_dc) < mde_cov),
            "log_ratio_per_trajectory":
                [float(np.log(rho(err_i, epi_i, [t]) / rho(err_m, epi_m, [t])))
                 for t in range(n_traj)],
            "coverage_diff_pts_per_trajectory":
                [float(100 * (cov(err_i, epi_i, [t]) - cov(err_m, epi_m, [t])))
                 for t in range(n_traj)],
            "mde_ratio": mde_ratio, "mde_coverage_pts": mde_cov,
            "mde_source": mde_source,
            "resolvable": bool(o_ratio_mag >= mde_ratio or abs(o_dc) >= mde_cov),
            "reading": (
                "BOTH EFFECTS BELOW THE MDE — the objective's own contribution is "
                "not resolvable at this n_independent; the point estimate is in the "
                "direction of worse calibration, not better"
                if o_ratio_mag < mde_ratio and abs(o_dc) < mde_cov else
                "at least one effect reaches the MDE"),
        }
        print(f"\n  The objective isolated — the same five seeds under mse, h = {DEPLOY}")
        print(f"    overconfidence factor x {np.exp(o_lr):.3f} "
              f"[{np.exp(o_lo1):.3f}, {np.exp(o_hi1):.3f}]  (MDE {mde_ratio}×, "
              f"{'BELOW' if o_ratio_mag < mde_ratio else 'clears'})")
        print(f"    coverage {o_dc:+.2f} points "
              f"[{o_lo2:.2f}, {o_hi2:.2f}]  (MDE {mde_cov} points, "
              f"{'BELOW' if abs(o_dc) < mde_cov else 'clears'})")
        print(f"    {out['m68']['objective_isolated']['reading']}")

        out["m44"]["verdict"] = verdict
        print(f"\n  M-68 direction condition (e), both statistics against all three seeds")
        for h in HORIZONS:
            d_ = dir_h[str(h)]
            print(f"    h={h:>3}  rho lower {'yes' if d_['overconfidence_lower_vs_all_three'] else 'NO '}"
                  f"   coverage higher {'yes' if d_['coverage_higher_vs_all_three'] else 'NO '}"
                  f"   both {'yes' if d_['both_improve_vs_all_three'] else 'NO '}")
        print(f"    {n_dir} of {len(HORIZONS)} horizons -> (e) "
              f"{'holds' if cond_e else 'FAILS'}")
        print(f"\n  M-68 BRANCH {branch}: {verdict}")
        for k, v in out["m68"]["conditions"].items():
            print(f"    {'yes' if v else 'NO ':>4}  {k}")
    print(f"\n  {rule} VERDICT: {verdict}")
    for k, v in out["m44"]["conditions"].items():
        print(f"    {'yes' if v else 'NO ':>4}  {k}")
    print(f"    mean overconfidence improvement "
          f"{out['m44']['mean_ratio_improvement']:.2f}× (MDE {mde_ratio}×)")
    print(f"    mean coverage gain {out['m44']['mean_coverage_gain_pts']:+.2f} points "
          f"(MDE {mde_cov})")

    dst = os.path.join(R.RESULTS, out_name)
    with open(dst, "w") as f:
        json.dump(out, f, indent=2, sort_keys=True)
    print(f"\n  wrote {R.rel(dst)}")


if __name__ == "__main__":
    # M-49 runs the SAME code on the capacity-matched arm. One implementation,
    # because the comparison is only interpretable if the rollout protocol, the
    # bootstrap, the horizons and the arena are identical between the two arms,
    # and two copies of a script drift.
    if "--m49" in sys.argv:
        import json as _j
        _P2 = _j.load(open(os.path.join(R.RESULTS, "p2_capacity_power.json")))
        _w = _P2["capacity"]["matched_hidden_size"]
        _m = _P2["mde_80pct_power"]
        sys.exit(main(tag=f"_m49h{_w}", hidden=_w,
                      out_name="m49_capacity_matched.json", rule="M-49",
                      mde_ratio=round(_m["overconfidence_ratio_multiplicative"], 3),
                      mde_cov=round(_m["coverage_pts"], 2),
                      mde_source="results/p2_capacity_power.json"))
    # M-68 runs the SAME code again on the combined arm -- five independently
    # initialised full models trained under gaussian_nll. Same protocol, same
    # bootstrap, same horizons, same arena; only the weights and the rule differ.
    if "--m68" in sys.argv:
        import json as _j
        _P3 = _j.load(open(os.path.join(R.RESULTS, "p3_combined_arm_power.json")))
        _b = _P3["binding_mde"]["100"]          # h = 100 is M-68's governing horizon
        sys.exit(main(tag="_nll", hidden=256,
                      out_name="r2_combined_arm.json", rule="M-68",
                      mde_ratio=round(_b["ratio_multiplicative"], 3),
                      mde_cov=round(_b["coverage_pts"], 2),
                      mde_source="results/p3_combined_arm_power.json, binding_mde at "
                                 "h = 100 (largest of the four calibrations)"))
    main()
