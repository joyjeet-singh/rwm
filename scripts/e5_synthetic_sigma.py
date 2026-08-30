"""
E5 -- does the implemented objective's optimum really put sigma at the floor?
      Demonstrated against ground truth, on data whose noise level is known.

WHY THIS EXISTS. §6.3 derives that under the implemented state loss --
E[(mu + sigma*eps - y)^2] = (mu - y)^2 + sigma^2, minimised at sigma = 0 -- the
predicted standard deviation has no reason to track anything. The derivation is
sound and the paper shows the collapse happening in training. But §6.3 also
asserts that this would hold "on any dataset, stochastic or not", and that
assertion is what refutes the follow-up's own reading, which attributes the low
aleatoric term to "small stochasticity in the environment".

An assertion is not a test. On the released CSV the two explanations are
observationally identical: the data may simply be nearly deterministic. The only
way to separate them is data whose true, input-dependent noise is KNOWN and large.

WHAT IS RUN. Data with a noise level that varies by more than an order of
magnitude across the input range, and a true mean function that is not constant.
The SAME bounded log-sigma head as the released model -- src/rwm_model.py
MLPStateHead, unmodified, including the double-softplus clamp, the learnable
state_min_logstd and state_log_delta_logstd, and the bound loss at its configured
weight -- trained under each objective in turn:

  mse           the implemented branch: a reparameterised SAMPLE enters the
                squared error (system_dynamics.py:270-289).
  gaussian_nll  the authors' own branch, reached by nothing in the repository:
                the predicted MEAN enters a Gaussian NLL.

Nothing else differs. Same data, same head, same optimiser, same iterations, same
seeds.

WHAT WOULD FALSIFY §6.3. If sigma recovers the true noise under the implemented
objective, the derivation is wrong or incomplete. If sigma collapses under BOTH,
the objective is not the cause. Either would be reported as returned.

    python scripts/e5_synthetic_sigma.py --dilution   the power study (run FIRST)
    python scripts/e5_synthetic_sigma.py              the experiment

The dilution study and M-50 are committed before the experiment runs.
Writes results/e5_sigma_dilution.json and results/e5_synthetic_sigma.json.
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import torch  # noqa: E402
import torch.nn as nn  # noqa: E402
import rwm_data as R  # noqa: E402
import rwm_model as MDL  # noqa: E402

SIGMA_SPAN = 25.0        # the factor true sigma spans across x in [-1, 1]
SPAN_FLOOR = 1.01        # the smallest recovered-sigma spread that counts as
                         # input dependence at all; sets the detection floor
N_TRAIN = 4000
N_TEST = 2000
ITERS = 12000            # see the note in evaluate(): 3,000 leaves the head
                         # under-trained under BOTH objectives and the contrast
                         # unreadable -- sigma is flat everywhere and the
                         # correlation swings on noise (measured at |r| up to 0.24 under the
                         # permutation null; the -0.78/+0.65 an earlier comment gave
                         # came from the superseded 3,000-iteration run)
BATCH = 256
SEEDS = (0, 1, 2)
NULL_REPEATS = 8           # permutation-null repeats for the dilution study
DILUTIONS = (0.0, 0.25, 0.5, 0.75, 1.0)


# ------------------------------------------------------------------ the data
def truth(x):
    """Mean and true noise level at x.

    sigma spans 0.02 to 0.50 across x in [-1, 1] -- a factor of 25, comfortably
    the "at least 10x" the brief asks for, and large enough that a model which
    reports a constant sigma is wrong somewhere by more than an order of
    magnitude whatever constant it picks.
    """
    mu = np.sin(3.0 * x) + 0.3 * x
    sigma = 0.02 * SIGMA_SPAN ** ((x + 1.0) / 2.0)
    return mu, sigma


def make_data(n, rng, dilution=1.0):
    """(x, y, sigma_true). `dilution` mixes the true x->sigma pairing with a
    permuted one, so 0.0 leaves the same MARGINAL noise distribution and destroys
    only the association a model could learn."""
    x = rng.uniform(-1.0, 1.0, size=(n, 1))
    mu, sig = truth(x)
    perm = rng.permutation(n)
    sig_used = np.exp((1.0 - dilution) * np.log(sig[perm]) + dilution * np.log(sig))
    y = mu + sig_used * rng.standard_normal((n, 1))
    return x, y, sig, sig_used


# ------------------------------------------------------------------ the model
def build_head(cfg, seed):
    torch.manual_seed(seed)
    ac = cfg["architecture_config"]
    # The released head, unmodified. input_dim 1 because there is no trunk here:
    # the question is about the HEAD's objective, and interposing a GRU would add
    # a confound rather than remove one.
    return MDL.MLPStateHead(1, 1, ac["state_mean_shape"], ac["state_logstd_shape"])


def train(head, cfg, x, y, loss_type, seed, iters=ITERS, with_bound=True):
    rng = np.random.default_rng(seed)
    opt = torch.optim.AdamW(head.parameters(), lr=cfg["learning_rate"],
                            weight_decay=cfg["weight_decay"])
    X = torch.as_tensor(x, dtype=torch.float32)
    Y = torch.as_tensor(y, dtype=torch.float32)
    zeros = torch.zeros(len(x), 1, 1)                 # the residual input, held at 0
    w = cfg["loss_weights"]
    torch.manual_seed(seed)
    for _ in range(iters):
        i = rng.integers(0, len(x), BATCH)
        mean, std = head(X[i], zeros[i])
        # system_dynamics.py:270-289, verbatim in both branches
        if loss_type == "mse":
            pred = torch.randn_like(mean) * std + mean
            state_loss = torch.sum(torch.square(pred - Y[i]), dim=1).mean(dim=0)
        else:
            state_loss = nn.GaussianNLLLoss()(mean, Y[i], std ** 2)
        loss = w["state"] * state_loss
        if with_bound:
            loss = loss + w["bound"] * MDL.RWMEnsemble.compute_bound_loss(head)
        opt.zero_grad(); loss.backward(); opt.step()
    return head


def evaluate(head, x, sigma_true):
    with torch.no_grad():
        mean, std = head(torch.as_tensor(x, dtype=torch.float32),
                         torch.zeros(len(x), 1, 1))
    s = std.numpy().ravel().astype(np.float64)
    st = np.asarray(sigma_true).ravel()
    ok = np.isfinite(s) & (s > 0)
    r = float(np.corrcoef(np.log(s[ok]), np.log(st[ok]))[0, 1]) if ok.sum() > 3 else np.nan
    # THE statistic, and why it is not the correlation.
    #
    # A correlation is scale-free, so a sigma_hat that is essentially CONSTANT
    # still returns a large one off its own numerical noise: the permutation null
    # produced |r| up to 0.24 from a head whose sigma spanned a factor of 1.0004
    # (results/e5_sigma_dilution.json; 0.78 was the superseded 3,000-iteration run).
    # The slope of log sigma_hat on log sigma_true is not scale-free. Perfect
    # recovery is 1; a constant sigma_hat is 0, whatever its correlation does.
    slope = float(np.polyfit(np.log(st[ok]), np.log(s[ok]), 1)[0]) if ok.sum() > 3 else np.nan
    return {
        "r_log_sigma": r,
        "slope_log_sigma": slope,
        "median_sigma_hat": float(np.median(s)),
        "median_sigma_true": float(np.median(st)),
        "ratio_median": float(np.median(s) / np.median(st)),
        "sigma_hat_range": [float(s.min()), float(s.max())],
        "sigma_true_range": [float(st.min()), float(st.max())],
        "sigma_hat_spread_factor": float(s.max() / s.min()) if s.min() > 0 else np.inf,
        "rmse_mean": float(np.sqrt(np.mean(
            (mean.numpy().ravel() - truth(x)[0].ravel()) ** 2))),
    }


# ------------------------------------------------------------------ dilution
def dilution_study():
    """The null and the detection curve, at the sample size the experiment faces.

    NULL. The x -> sigma pairing is permuted, so the marginal noise distribution
    and the mean function are unchanged and only the learnable association is
    gone. Whatever a model reports on that data is what this design produces from
    nothing.

    Nothing here uses the `mse` branch. Calibrating a detector on the objective it
    is meant to test would let the objective set its own threshold.

    Thresholds and detection rates come from derive_mde(), which --reaggregate
    also calls, so the two paths cannot write different shapes into one artifact.
    They did, and only the clean-clone gate could find it.
    """
    cfg = R.load_reference_config(R.repo_paths()["lite"])
    rec = {"n_train": N_TRAIN, "n_test": N_TEST, "iters": ITERS,
           "null_repeats": NULL_REPEATS, "dilutions": list(DILUTIONS),
           "calibrated_on": "gaussian_nll",
           "why": "the null and the ladder are built under the objective that CAN "
                  "recover sigma; calibrating on the objective under test would let "
                  "it set its own threshold"}
    print("E5 — DILUTION STUDY (run before the rule is committed)")
    print("=" * 88)

    nulls = []
    for k in range(NULL_REPEATS):
        rng = np.random.default_rng(9000 + k)
        x, y, sig, _ = make_data(N_TRAIN, rng, dilution=0.0)
        xt, _, sigt, _ = make_data(N_TEST, np.random.default_rng(19000 + k), 1.0)
        h = train(build_head(cfg, k), cfg, x, y, "gaussian_nll", k)
        e = evaluate(h, xt, sigt)
        nulls.append(e)
        print(f"  null {k:>2}: slope {e['slope_log_sigma']:+.4f}  r {e['r_log_sigma']:+.4f}  "
              f"ratio {e['ratio_median']:.3f}  spread {e['sigma_hat_spread_factor']:.2f}x")
    rec["null"] = {"runs": nulls}

    ladder = []
    for d in DILUTIONS:
        rs, sl = [], []
        for sd in SEEDS:
            rng = np.random.default_rng(int(1000 * d) + 100 + sd)
            x, y, sig, _ = make_data(N_TRAIN, rng, dilution=d)
            xt, _, sigt, _ = make_data(N_TEST, np.random.default_rng(500 + sd), 1.0)
            h = train(build_head(cfg, sd), cfg, x, y, "gaussian_nll", sd)
            e = evaluate(h, xt, sigt)
            rs.append(e["r_log_sigma"]); sl.append(e["slope_log_sigma"])
        ladder.append({"dilution": d, "r": rs, "slope": sl,
                       "r_mean": float(np.mean(rs)), "slope_mean": float(np.mean(sl))})
    rec["ladder"] = ladder

    rec = derive_mde(rec)
    M, NUL = rec["mde"], rec["null"]
    for l in rec["ladder"]:
        print(f"  dilution {l['dilution']:.2f}: slope {l['slope_mean']:+.4f}  "
              f"r {l['r_mean']:+.4f}  detected {l['detection_rate']:.0%}")
    print("=" * 88)
    print(f"  null |slope| 95th percentile  : {NUL['slope_abs_p95']:.3g}")
    print(f"  {SPAN_FLOOR}x-span floor             : {M['slope_floor']:.5f}")
    print(f"  threshold in force            : {M['slope_threshold']:.5f}")
    print(f"  null |r| 95th percentile      : {NUL['r_abs_p95']:.4f}   (not used: scale-free)")
    print(f"  null sigma spread, worst      : {NUL['spread_max']:.4f}x")
    print(f"  false positives at dilution 0 : {M['false_positive_rate_at_dilution_0']:.0%}")
    print(f"  smallest dilution detected 80%: {M['smallest_dilution_detected_80pct']}")
    print(f"  null median ratio, minimum    : {NUL['ratio_median_min']:.3f}")
    json.dump(rec, open(os.path.join(R.RESULTS, "e5_sigma_dilution.json"), "w"), indent=2)
    print("  wrote results/e5_sigma_dilution.json")
    return 0



# ---------------------------------------------------------------- experiment


def summarise(runs, TH):
    """Apply M-50's criteria to a set of runs.

    THE STATISTIC IS THE SLOPE. M-50 says so, at length and with the reason: a
    correlation is scale-free, so a sigma-hat that is essentially constant returns
    a large one off its own numerical noise. The first version of this function
    applied the CORRELATION anyway -- the field was there, it was the obvious one,
    and the rule it was implementing said something else three paragraphs up.

    It produced exactly the failure M-50 predicted. The mse arm's sigma spans a
    factor of 1.002 and its correlations across three seeds were +0.63, -0.03 and
    +0.88, so the "indistinguishable from zero" test failed on noise and the
    verdict came out MIXED when both arms had in fact behaved as the rule
    describes. A rule and the code that applies it must name the same quantity,
    and nothing here checked that they did.
    """
    sl = np.array([r["slope_log_sigma"] for r in runs])
    ratio = np.array([r["ratio_median"] for r in runs])
    r = np.array([r["r_log_sigma"] for r in runs])
    return {
        "runs": runs,
        "slope_mean": float(sl.mean()), "slope_min": float(sl.min()),
        "slope_max": float(sl.max()),
        "ratio_mean": float(ratio.mean()),
        "ratio_min": float(ratio.min()), "ratio_max": float(ratio.max()),
        "spread_max": float(max(x["sigma_hat_spread_factor"] for x in runs)),
        # the correlation is REPORTED and not used, so a reader can see why
        "r_mean_reported_not_used": float(r.mean()),
        "r_min_reported_not_used": float(r.min()),
        "r_max_reported_not_used": float(r.max()),
        "tracking_indistinguishable_from_zero":
            bool(np.all(np.abs(sl) <= TH["slope_threshold"])),
        "tracking_above_threshold":
            bool(np.all(np.abs(sl) > TH["slope_threshold"])),
        "collapsed": bool(np.all(ratio < TH["collapse_ratio_threshold"])),
        "recovered": bool(np.all((ratio > 1.0 / TH["recovery_factor_threshold"])
                                 & (ratio < TH["recovery_factor_threshold"]))),
    }


def verdict_of(arms, TH):
    A, B = arms["mse"], arms["gaussian_nll"]
    if A["collapsed"] and A["tracking_indistinguishable_from_zero"] \
            and B["recovered"] and B["tracking_above_threshold"]:
        return "OBJECTIVE-DRIVEN"
    if A["recovered"] and A["tracking_above_threshold"]:
        return "REFUTED — sigma recovers under the implemented objective"
    if A["collapsed"] and B["collapsed"]:
        return "NOT OBJECTIVE-DRIVEN — sigma collapses under both"
    return "MIXED — reported as returned; see the arms"


def reverdict():
    """Re-apply M-50's criteria to the runs already trained.

    The runs are the data and they are unchanged; only the aggregation was wrong,
    and it was wrong by using a field the rule does not name. Retraining to fix
    an aggregation would change the data under a committed rule, which is worse.
    """
    path = os.path.join(R.RESULTS, "e5_synthetic_sigma.json")
    out = json.load(open(path))
    TH = out["thresholds"]
    for k in out["arms"]:
        out["arms"][k] = summarise(out["arms"][k]["runs"], TH)
    out["verdict"] = verdict_of(out["arms"], TH)
    json.dump(out, open(path, "w"), indent=2)
    _report(out, TH)
    return 0


def _report(out, TH):
    A, B = out["arms"]["mse"], out["arms"]["gaussian_nll"]
    print("=" * 88)
    print(f"  tracking threshold (M-50): {TH['slope_threshold']:.5f}   "
          f"collapse < {TH['collapse_ratio_threshold']}   "
          f"recovery within {TH['recovery_factor_threshold']}x")
    print(f"  mse          : collapsed {A['collapsed']}, tracking~0 "
          f"{A['tracking_indistinguishable_from_zero']}  "
          f"(slope {A['slope_mean']:+.6f}, ratio {A['ratio_mean']:.4f}, "
          f"spread {A['spread_max']:.3f}x)")
    print(f"  gaussian_nll : recovered {B['recovered']}, tracking>thr "
          f"{B['tracking_above_threshold']}  "
          f"(slope {B['slope_mean']:+.6f}, ratio {B['ratio_mean']:.4f}, "
          f"spread {B['spread_max']:.3f}x)")
    print(f"  M-50 VERDICT : {out['verdict']}")


# ---------------------------------------------------------------- experiment
def experiment():
    cfg = R.load_reference_config(R.repo_paths()["lite"])
    D = json.load(open(os.path.join(R.RESULTS, "e5_sigma_dilution.json")))
    TH = D["mde"]
    print("E5 — SYNTHETIC SIGMA RECOVERY, AGAINST GROUND TRUTH")
    print("=" * 88)
    print(f"  true sigma spans {0.02:.3f} to {0.02 * SIGMA_SPAN:.3f} across x in "
          f"[-1, 1] (a factor of {SIGMA_SPAN:.0f})")
    print(f"  rule M-50, thresholds from results/e5_sigma_dilution.json:")
    print(f"    |r| indistinguishable from zero below {TH['r_threshold']:.4f}")
    print(f"    collapse if median sigma_hat / sigma_true < {TH['collapse_ratio_threshold']}")
    print(f"    recovery if within a factor of {TH['recovery_factor_threshold']}")

    out = {"config": {"n_train": N_TRAIN, "n_test": N_TEST, "iters": ITERS,
                      "seeds": list(SEEDS), "batch": BATCH,
                      "true_sigma_span_factor": SIGMA_SPAN,
                      "head": "src/rwm_model.py MLPStateHead, unmodified",
                      "bound_loss": "applied at its configured weight, as in the "
                                    "released training path"},
           "thresholds": TH, "arms": {}}

    # 3.2 -- the corroboration seeds, ADDITIVE. M-50 was discharged over SEEDS and its
    # verdict stands as returned over those three; more seeds do not re-open a discharged
    # rule (REVISION_BRIEF.md §2 rule 4), exactly as M-43's denominator stayed at four
    # horizons. So `arms` and `verdict` below are computed from SEEDS alone and are
    # unchanged, and the 20-seed figures land in their own block beside them.
    #
    # Each run depends only on its own seed, so running 0..19 once and slicing the first
    # three gives the SAME three runs the 3-seed path produces. Nothing is recomputed
    # differently; the 3-seed keys the paper cites are bit-identical.
    CORROB_SEEDS = tuple(range(20))
    assert tuple(SEEDS) == CORROB_SEEDS[:len(SEEDS)], \
        "the corroboration set must extend SEEDS, not replace it"

    all_runs = {}
    for loss_type in ("mse", "gaussian_nll"):
        runs = []
        for s in CORROB_SEEDS:
            rng = np.random.default_rng(4200 + s)
            x, y, sig, _ = make_data(N_TRAIN, rng, dilution=1.0)
            xt, _, sigt, _ = make_data(N_TEST, np.random.default_rng(8400 + s), 1.0)
            h = train(build_head(cfg, s), cfg, x, y, loss_type, s)
            e = evaluate(h, xt, sigt)
            e["seed"] = s
            runs.append(e)
            if s in SEEDS:
                print(f"  {loss_type:<13} seed {s}: sigma_hat median {e['median_sigma_hat']:.5f} "
                      f"(true {e['median_sigma_true']:.5f}, ratio {e['ratio_median']:.4f})  "
                      f"r {e['r_log_sigma']:+.4f}  spread {e['sigma_hat_spread_factor']:.2f}x  "
                      f"mean RMSE {e['rmse_mean']:.4f}")
        all_runs[loss_type] = runs
        out["arms"][loss_type] = summarise(runs[:len(SEEDS)], TH)

    out["verdict"] = verdict_of(out["arms"], TH)

    out["corroboration_20_seeds"] = {
        "status": "CORROBORATION, NOT A DISCHARGE",
        "why": ("M-50 is discharged over the three seeds in `config.seeds` and its verdict "
                "stands as returned there. More seeds do not re-open a discharged rule "
                "(REVISION_BRIEF.md §2 rule 4); the same logic kept M-43's denominator at "
                "four horizons. These figures corroborate and are labelled as such."),
        "seeds": list(CORROB_SEEDS),
        "n_seeds": len(CORROB_SEEDS),
        "same_generator_head_iterations_objectives": True,
        "config_identical_to_3_seed_run_except_seed_count": True,
        "arms": {lt: summarise(all_runs[lt], TH) for lt in all_runs},
        "verdict_if_evaluated_at_20_seeds": verdict_of(
            {lt: summarise(all_runs[lt], TH) for lt in all_runs}, TH),
        "note_on_that_verdict": (
            "IT DOES NOT RETURN THE SAME WORD, and that is the finding. At three seeds "
            "M-50 returns OBJECTIVE-DRIVEN; evaluated over twenty it would return MIXED. "
            "M-50's verdict is unchanged and stays as returned over its own three seeds "
            "(REVISION_BRIEF.md §2 rule 4) -- more seeds do not re-open a discharged rule. "
            "But this is a qualification of the corroboration, not a confirmation of it, "
            "and reporting it as clean corroboration would be false."),
        "which_criterion_flips": {
            "arm": "gaussian_nll",
            "flag": "tracking_above_threshold",
            "at_3_seeds": True,
            "at_20_seeds": False,
            "why": ("the criterion is ALL-seeds -- np.all(|slope| > slope_threshold) -- "
                    "and the recovering arm is strongly seed-variable at this training "
                    "budget. The three seeds M-50 drew all cleared the threshold; over "
                    "twenty, several do not."),
            "unaffected_flags": ("mse stays collapsed and indistinguishable-from-zero at "
                                 "both seed counts, and gaussian_nll stays `recovered` at "
                                 "both. The CONTRAST between the arms -- which is what "
                                 "M-50 says the experiment establishes -- is unchanged."),
        },
        "reading": (
            "M-50 wrote, before these runs existed, that 'the recovering arm is itself "
            "seed-variable at this training budget, so the CONTRAST is what this "
            "experiment establishes, not the magnitude of the recovery.' Twenty seeds "
            "confirm that warning more sharply than three could: the magnitude of the "
            "recovery's input-dependence does not survive an all-seeds threshold, while "
            "the contrast between the two objectives does. §6.3's mechanism claim rests "
            "on the contrast."),
        "slope_distribution": {
            lt: {"min": float(min(r["slope_log_sigma"] for r in all_runs[lt])),
                 "median": float(sorted(r["slope_log_sigma"] for r in all_runs[lt])
                                 [len(all_runs[lt]) // 2]),
                 "max": float(max(r["slope_log_sigma"] for r in all_runs[lt])),
                 "n_below_slope_threshold": int(sum(
                     abs(r["slope_log_sigma"]) <= TH["slope_threshold"]
                     for r in all_runs[lt])),
                 "n_seeds": len(all_runs[lt]),
                 "slope_threshold": TH["slope_threshold"]}
            for lt in all_runs},
        "per_seed": {lt: [{"seed": r["seed"], "ratio_median": r["ratio_median"],
                           "r_log_sigma": r["r_log_sigma"],
                           "slope_log_sigma": r.get("slope_log_sigma"),
                           "sigma_hat_spread_factor": r["sigma_hat_spread_factor"]}
                          for r in all_runs[lt]] for lt in all_runs},
    }
    verdict = out["verdict"]
    _report(out, TH)
    json.dump(out, open(os.path.join(R.RESULTS, "e5_synthetic_sigma.json"), "w"), indent=2)
    print("  wrote results/e5_synthetic_sigma.json")
    return 0


def derive_mde(rec):
    """Thresholds, detection rates and the null summary, from the runs in `rec`.

    ONE implementation, called by both the dilution run and --reaggregate.
    They had two, and the two wrote DIFFERENT SHAPES into the same artifact:
    `false_positive_rate_at_dilution_0` and `null.r_abs_max` existed only on the
    --reaggregate path. This tree had them because --reaggregate had been run
    here; a clean clone runs --dilution and never does, so stage 23 died on a
    KeyError that could not occur on the machine the artifact was made on.

    Found by the clean-clone gate, which is the only thing that could have found
    it: every check here reads the artifact this tree has.
    """
    sl_null = np.array([r["slope_log_sigma"] for r in rec["null"]["runs"]])
    r_null = np.array([r["r_log_sigma"] for r in rec["null"]["runs"]])
    ratio_null = np.array([r["ratio_median"] for r in rec["null"]["runs"]])
    p95 = float(np.percentile(np.abs(sl_null), 95))
    s_floor = float(np.log(SPAN_FLOOR) / np.log(SIGMA_SPAN))
    s_thresh = float(max(p95, s_floor))
    for l in rec["ladder"]:
        l["detection_rate"] = float(np.mean([abs(v) > s_thresh for v in l["slope"]]))
    det = [l["dilution"] for l in rec["ladder"] if l["detection_rate"] >= 0.8]
    fp = next((l["detection_rate"] for l in rec["ladder"] if l["dilution"] == 0.0), None)
    rec["null"].update({
        "slope_abs_p95": p95,
        "r_abs_p95": float(np.percentile(np.abs(r_null), 95)),
        "r_abs_max": float(np.abs(r_null).max()),
        "spread_max": float(max(r["sigma_hat_spread_factor"] for r in rec["null"]["runs"])),
        "ratio_median_min": float(ratio_null.min()),
    })
    rec["mde"] = {
        "slope_threshold": s_thresh,
        "slope_floor": s_floor,
        "span_floor": SPAN_FLOOR,
        "slope_threshold_from": ("the null's 95th percentile" if p95 > s_floor else
                                 f"the {SPAN_FLOOR}x-span floor; the null's own 95th "
                                 f"percentile is {p95:.2g}, which is numerical noise "
                                 f"and would fire on anything"),
        "r_threshold": float(np.percentile(np.abs(r_null), 95)),
        "smallest_dilution_detected_80pct": min(det) if det else None,
        "false_positive_rate_at_dilution_0": fp,
        "collapse_ratio_threshold": 0.1,
        "collapse_threshold_justification":
            f"the null -- a model with nothing to learn about WHERE the noise is -- "
            f"still recovers the marginal scale, with median sigma_hat / sigma_true "
            f"no lower than {ratio_null.min():.3f} across {len(sl_null)} repeats. "
            f"A collapse criterion of 0.1 sits far below anything this design "
            f"produces without one, so meeting it cannot be an artifact of the "
            f"sample size or of the head's floor.",
        "recovery_factor_threshold": 3.0,
        "recovery_threshold_justification":
            "under gaussian_nll on undiluted data the head recovers the median "
            "true sigma to within a factor the ladder measures; 3.0 is set wider "
            "than the observed spread so the rule is not tuned to one run.",
    }
    return rec


def reaggregate():
    """Re-derive the thresholds from the runs already trained.

    Legitimate, and worth saying why. The expensive part is the calibration data
    -- the null runs and the ladder -- and it is unchanged. What changes is the
    DECISION RULE derived from it, and a decision rule may be designed on
    calibration data provided it is fixed before the data it will judge exists.

    It calls derive_mde(), which the dilution run also calls, so the two cannot
    write different shapes into the same artifact. They did: this path added
    `false_positive_rate_at_dilution_0` and `null.r_abs_max` and the dilution
    path did not, so a clean clone -- which only ever runs the dilution path --
    died on a KeyError this machine could not reproduce.
    """
    path = os.path.join(R.RESULTS, "e5_sigma_dilution.json")
    rec = derive_mde(json.load(open(path)))
    json.dump(rec, open(path, "w"), indent=2)
    M = rec["mde"]
    print("E5 — DILUTION THRESHOLDS, RE-DERIVED (no retraining)")
    print("=" * 88)
    print(f"  null |slope| 95th percentile : {rec['null']['slope_abs_p95']:.3g}")
    print(f"  {SPAN_FLOOR}x-span floor             : {M['slope_floor']:.5f}")
    print(f"  threshold in force           : {M['slope_threshold']:.5f}")
    for l in rec["ladder"]:
        print(f"    dilution {l['dilution']:.2f}: slopes "
              f"{[round(v, 5) for v in l['slope']]}  detected {l['detection_rate']:.0%}")
    print(f"  false positives at dilution 0: {M['false_positive_rate_at_dilution_0']:.0%}")
    print(f"  smallest dilution detected 80%: {M['smallest_dilution_detected_80pct']}")
    print("  wrote results/e5_sigma_dilution.json")
    return 0


if __name__ == "__main__":
    if "--dilution" in sys.argv:
        sys.exit(dilution_study())
    if "--reaggregate" in sys.argv:
        sys.exit(reaggregate())
    if "--reverdict" in sys.argv:
        sys.exit(reverdict())
    sys.exit(experiment())
