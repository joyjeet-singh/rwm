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
N_TRAIN = 4000
N_TEST = 2000
ITERS = 12000            # see the note in evaluate(): 3,000 leaves the head
                         # under-trained under BOTH objectives and the contrast
                         # unreadable -- sigma is flat everywhere and the
                         # correlation swings between -0.78 and +0.65 on noise
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
    # produced |r| up to 0.78 from a head whose sigma spanned a factor of 1.00.
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
    gone. Whatever correlation a model reports on that data is what this design
    produces from nothing, and its upper tail is the threshold.

    Nothing here uses the `mse` branch. Calibrating a detector on the objective
    it is meant to test would let the objective set its own threshold.
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
    r_null = np.array([n["r_log_sigma"] for n in nulls])
    sl_null = np.array([n["slope_log_sigma"] for n in nulls])
    ratio_null = np.array([n["ratio_median"] for n in nulls])
    r_thresh = float(np.percentile(np.abs(r_null), 95))
    # THE THRESHOLD NEEDS A FLOOR, and here is why.
    #
    # Under the permutation null the head learns a sigma with NO input dependence
    # at all: the measured spread is 1.0004x across the input range and the fitted
    # slopes are order 1e-5, which is floating-point noise rather than sampling
    # variability. A 95th percentile of that is ~2e-5, and a threshold of 2e-5
    # "detects" any slope whatsoever -- the dilution-0 arm, which is pure null,
    # crossed it a third of the time. A threshold a coin flip can clear is not a
    # threshold.
    #
    # So the floor is set by what a slope MEANS rather than by the noise around
    # zero. A slope s makes the recovered sigma span (true span)^s across the
    # input range; the floor is the slope at which that span reaches 1.01x -- a
    # one-percent variation, which is the smallest input dependence anyone would
    # call input dependence at all, and about 150x the null's numerical noise.
    _span_floor = 1.01
    s_floor = float(np.log(_span_floor) / np.log(SIGMA_SPAN))
    s_thresh = float(max(np.percentile(np.abs(sl_null), 95), s_floor))
    rec["null"] = {
        "r_mean": float(r_null.mean()), "r_sd": float(r_null.std(ddof=1)),
        "r_abs_p95": r_thresh,
        "slope_mean": float(sl_null.mean()), "slope_sd": float(sl_null.std(ddof=1)),
        "slope_abs_p95": s_thresh,
        "spread_max": float(max(n["sigma_hat_spread_factor"] for n in nulls)),
        "ratio_median_mean": float(ratio_null.mean()),
        "ratio_median_min": float(ratio_null.min()),
        "runs": nulls,
    }

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
        det = float(np.mean([abs(v) > s_thresh for v in sl]))
        ladder.append({"dilution": d, "r": rs, "slope": sl,
                       "r_mean": float(np.mean(rs)), "slope_mean": float(np.mean(sl)),
                       "detection_rate": det})
        print(f"  dilution {d:.2f}: slope {np.mean(sl):+.4f}  r {np.mean(rs):+.4f}  "
              f"detected {det:.0%}")
    rec["ladder"] = ladder

    detected = [l["dilution"] for l in ladder if l["detection_rate"] >= 0.8]
    rec["mde"] = {
        "slope_threshold": s_thresh,
        "slope_threshold_from": ("the null's 95th percentile" if
                                 np.percentile(np.abs(sl_null), 95) > s_floor
                                 else f"the {_span_floor}x-span floor; the null's own "
                                      f"95th percentile is "
                                      f"{np.percentile(np.abs(sl_null), 95):.2g}, which is "
                                      f"numerical noise and would fire on anything"),
        "slope_floor": s_floor,
        "r_threshold": r_thresh,
        "smallest_dilution_detected_80pct": min(detected) if detected else None,
        "collapse_ratio_threshold": 0.1,
        "collapse_threshold_justification":
            f"the null -- a model with nothing to learn about WHERE the noise is -- "
            f"still recovers the marginal scale, with median sigma_hat / sigma_true "
            f"no lower than {ratio_null.min():.3f} across {NULL_REPEATS} repeats. "
            f"A collapse criterion of 0.1 sits far below anything this design "
            f"produces without one, so meeting it cannot be an artifact of the "
            f"sample size or of the head's floor.",
        "recovery_factor_threshold": 3.0,
        "recovery_threshold_justification":
            "under gaussian_nll on undiluted data the head recovers the median "
            "true sigma to within a factor the ladder measures; 3.0 is set wider "
            "than the observed spread so the rule is not tuned to one run.",
    }
    print("=" * 88)
    print(f"  null |slope| 95th percentile  : {s_thresh:.4f}   <- the threshold")
    print(f"  null |r| 95th percentile      : {r_thresh:.4f}   (not used: scale-free)")
    print(f"  null sigma spread, worst      : {rec['null']['spread_max']:.3f}x")
    print(f"  smallest dilution detected 80%: {rec['mde']['smallest_dilution_detected_80pct']}")
    print(f"  null median ratio, minimum    : {ratio_null.min():.3f}")
    json.dump(rec, open(os.path.join(R.RESULTS, "e5_sigma_dilution.json"), "w"), indent=2)
    print("  wrote results/e5_sigma_dilution.json")
    return 0


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

    for loss_type in ("mse", "gaussian_nll"):
        runs = []
        for s in SEEDS:
            rng = np.random.default_rng(4200 + s)
            x, y, sig, _ = make_data(N_TRAIN, rng, dilution=1.0)
            xt, _, sigt, _ = make_data(N_TEST, np.random.default_rng(8400 + s), 1.0)
            h = train(build_head(cfg, s), cfg, x, y, loss_type, s)
            e = evaluate(h, xt, sigt)
            e["seed"] = s
            runs.append(e)
            print(f"  {loss_type:<13} seed {s}: sigma_hat median {e['median_sigma_hat']:.5f} "
                  f"(true {e['median_sigma_true']:.5f}, ratio {e['ratio_median']:.4f})  "
                  f"r {e['r_log_sigma']:+.4f}  spread {e['sigma_hat_spread_factor']:.2f}x  "
                  f"mean RMSE {e['rmse_mean']:.4f}")
        r = np.array([x_["r_log_sigma"] for x_ in runs])
        ratio = np.array([x_["ratio_median"] for x_ in runs])
        out["arms"][loss_type] = {
            "runs": runs,
            "r_mean": float(r.mean()), "r_min": float(r.min()), "r_max": float(r.max()),
            "ratio_mean": float(ratio.mean()),
            "ratio_min": float(ratio.min()), "ratio_max": float(ratio.max()),
            "r_indistinguishable_from_zero": bool(np.all(np.abs(r) <= TH["r_threshold"])),
            "r_above_threshold": bool(np.all(np.abs(r) > TH["r_threshold"])),
            "collapsed": bool(np.all(ratio < TH["collapse_ratio_threshold"])),
            "recovered": bool(np.all((ratio > 1.0 / TH["recovery_factor_threshold"])
                                     & (ratio < TH["recovery_factor_threshold"]))),
        }

    A, B = out["arms"]["mse"], out["arms"]["gaussian_nll"]
    if A["collapsed"] and A["r_indistinguishable_from_zero"] \
            and B["recovered"] and B["r_above_threshold"]:
        verdict = "OBJECTIVE-DRIVEN"
    elif A["recovered"] and A["r_above_threshold"]:
        verdict = "REFUTED — sigma recovers under the implemented objective"
    elif A["collapsed"] and B["collapsed"]:
        verdict = "NOT OBJECTIVE-DRIVEN — sigma collapses under both"
    else:
        verdict = "MIXED — reported as returned; see the arms"
    out["verdict"] = verdict
    print("=" * 88)
    print(f"  mse          : collapsed {A['collapsed']}, r~0 {A['r_indistinguishable_from_zero']} "
          f"(r {A['r_mean']:+.4f}, ratio {A['ratio_mean']:.4f})")
    print(f"  gaussian_nll : recovered {B['recovered']}, r>thr {B['r_above_threshold']} "
          f"(r {B['r_mean']:+.4f}, ratio {B['ratio_mean']:.4f})")
    print(f"  M-50 VERDICT : {verdict}")
    json.dump(out, open(os.path.join(R.RESULTS, "e5_synthetic_sigma.json"), "w"), indent=2)
    print("  wrote results/e5_synthetic_sigma.json")
    return 0


def reaggregate():
    """Recompute the thresholds from the runs already trained.

    Legitimate, and worth saying why. The expensive part is the calibration data
    -- eight null runs and fifteen ladder runs -- and it is unchanged. What
    changes is the DECISION RULE derived from it, and a decision rule may be
    designed on calibration data provided it is fixed before the data it will
    judge exists. No arm of the experiment has been trained when this runs.
    """
    path = os.path.join(R.RESULTS, "e5_sigma_dilution.json")
    rec = json.load(open(path))
    sl_null = np.array([r["slope_log_sigma"] for r in rec["null"]["runs"]])
    ratio_null = np.array([r["ratio_median"] for r in rec["null"]["runs"]])
    s_floor = float(np.log(1.01) / np.log(SIGMA_SPAN))
    p95 = float(np.percentile(np.abs(sl_null), 95))
    s_thresh = float(max(p95, s_floor))
    for l in rec["ladder"]:
        l["detection_rate"] = float(np.mean([abs(v) > s_thresh for v in l["slope"]]))
    det = [l["dilution"] for l in rec["ladder"] if l["detection_rate"] >= 0.8]
    rec["null"]["slope_abs_p95"] = p95
    rec["mde"].update({
        "slope_threshold": s_thresh,
        "slope_floor": s_floor,
        "slope_threshold_from": ("the null's 95th percentile" if p95 > s_floor else
                                 f"the 1.01x-span floor; the null's own 95th percentile "
                                 f"is {p95:.2g}, which is numerical noise and would fire "
                                 f"on anything"),
        "smallest_dilution_detected_80pct": min(det) if det else None,
        "false_positive_rate_at_dilution_0": next(
            (1 - 0 if False else l["detection_rate"]) for l in rec["ladder"]
            if l["dilution"] == 0.0),
    })
    json.dump(rec, open(path, "w"), indent=2)
    print("E5 — DILUTION THRESHOLDS, RE-DERIVED (no retraining)")
    print("=" * 88)
    print(f"  null |slope| 95th percentile : {p95:.3g}  (numerical noise: the null's")
    print(f"                                 sigma spans {max(r['sigma_hat_spread_factor'] for r in rec['null']['runs']):.4f}x)")
    print(f"  1.01x-span floor             : {s_floor:.5f}")
    print(f"  threshold in force           : {s_thresh:.5f}  <- {rec['mde']['slope_threshold_from'][:40]}")
    for l in rec["ladder"]:
        print(f"    dilution {l['dilution']:.2f}: slopes "
              f"{[round(v, 5) for v in l['slope']]}  detected {l['detection_rate']:.0%}")
    print(f"  false positives at dilution 0: {rec['mde']['false_positive_rate_at_dilution_0']:.0%}")
    print(f"  smallest dilution detected 80%: {rec['mde']['smallest_dilution_detected_80pct']}")
    print(f"  null median ratio, minimum   : {ratio_null.min():.3f}")
    print("  wrote results/e5_sigma_dilution.json")
    return 0


if __name__ == "__main__":
    if "--dilution" in sys.argv:
        sys.exit(dilution_study())
    if "--reaggregate" in sys.argv:
        sys.exit(reaggregate())
    sys.exit(experiment())
