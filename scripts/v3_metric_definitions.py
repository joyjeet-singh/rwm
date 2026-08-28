"""
V3 -- write down, from the implementation, what every metric in this paper means.

The paper reports "normalised error 0.3582" and never defines the metric. It
names relative-L1 and nRMSE and gives the formula for neither. "Coverage" is
never defined operationally: pooled over which axes, in what order, against
which nominal.

That is not a presentational gap in this particular project. Two metrics here
disagree in DIRECTION at h=1 (R-20), and an aggregation choice -- pooling before
dividing versus dividing before pooling -- once inverted a published-model
comparison (R-27). A reader who cannot see the denominator cannot check the
headline, and cannot tell which of the two aggregations a number came from.

So each definition below is emitted with:
  - the formula as a LaTeX string, which renders into a new 2.1 Metrics;
  - the file:line of the implementation, read back and fingerprinted;
  - where the constants in the denominator come from, and over what data;
  - for coverage, the pooling axes IN ORDER, and the nominal it is judged against.

Nothing here recomputes a result. It is a statement of what the existing
numbers mean, checked against the code that produced them.
"""
import ast
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, os.pardir))
PDM = os.path.abspath(os.path.join(REPO, os.pardir))
RWML = os.path.join(PDM, "robotic_world_model_lite")


def cite(path, line, must_contain, note=""):
    """
    Cite path:line, verified by reading the line back.

    Two regimes, because two kinds of file are being cited and they fail
    differently.

    UPSTREAM files are pinned at a commit. A citation that no longer matches
    means the PIN MOVED, which is a fact about the world that must fail loudly --
    so the line number is asserted exactly.

    OUR OWN files change whenever we edit them, and a line number is the most
    fragile possible reference into a file under active development. Adding the
    A1 bootstrap block to task1_calibration.py moved its z statistic from line 65
    to line 78 and broke four citations here, which the clean-clone run caught.
    So for repo-local files the fingerprint is LOCATED and its current line is
    reported: the citation cannot go stale, and it still fails if the line it
    names disappears entirely or stops being unique.
    """
    with open(path) as f:
        lines = f.read().split("\n")
    local = os.path.abspath(path).startswith(REPO + os.sep)
    if local:
        hits = [i + 1 for i, t in enumerate(lines) if must_contain in t]
        assert hits, (f"citation lost at {os.path.relpath(path, PDM)}: no line contains "
                      f"{must_contain!r} — the code it names is gone or was reworded")
        assert len(hits) == 1, (
            f"ambiguous citation in {os.path.relpath(path, PDM)}: {must_contain!r} "
            f"occurs on lines {hits}; make the fingerprint unique")
        line = hits[0]
    else:
        assert 1 <= line <= len(lines), f"{path}:{line} past end of file"
        assert must_contain in lines[line - 1], (
            f"citation drift at {path}:{line} — the upstream pin moved\n"
            f"  expected: {must_contain!r}\n  actual:   {lines[line - 1].strip()!r}")
    return {"cite": f"{os.path.relpath(path, PDM)}:{line}",
            "text": lines[line - 1].strip(), "note": note}


def main():
    ro = os.path.join(REPO, "src", "rollout_eval.py")
    me = os.path.join(REPO, "src", "rwm_metrics.py")
    ca = os.path.join(REPO, "scripts", "task1_calibration.py")
    dn = os.path.join(REPO, "scripts", "task_d_nind20.py")
    mt = os.path.join(RWML, "scripts", "model_training.py")

    out = {"metrics": {}, "coverage": {}, "constants": {}, "which_is_headline": {}}

    # ------------------------------------------------------- relative L1
    out["metrics"]["relative_l1"] = {
        "name": "relative-L1",
        "what_it_is": "the reference metric, reproduced verbatim in behaviour so our "
                      "numbers are comparable to the upstream's printed one",
        "latex_per_step":
            r"r_t \;=\; \frac{\sum_{d=1}^{45}\bigl|\hat{s}_{t,d}-s_{t,d}\bigr|}"
            r"{\sum_{d=1}^{45}\bigl|s_{t,d}\bigr|}",
        "latex_aggregate":
            r"e \;=\; \frac{1}{B\,(T-t_0)}\sum_{b=1}^{B}\sum_{t=t_0+1}^{T} r_{t}^{(b)}",
        "space": "normalised state space: both numerator and denominator are in the "
                 "config-normalised units, not physical units",
        "denominator": "the TRUE state at the same timestep, summed over all 45 "
                       "dimensions. It is recomputed at every timestep and is not a "
                       "constant.",
        "start": "t_0 = history_horizon = 32; the first 32 steps are teacher-forced "
                 "and excluded from the metric",
        "known_pathology":
            "the denominator is a 45-term sum in normalised space and can pass through "
            "zero, which is why relative-L1 goes non-finite on low-dimensional state "
            "groups (M-09: `inf` on base angular velocity from h>=8, an 11.4% blow-up "
            "rate on projected gravity at h=368). This is the reason a second metric "
            "exists.",
        "citations": [
            cite(ro, 143, "r_t = sum_d |pred[t,d] - true[t,d]| / sum_d |true[t,d]|",
                 "the formula, as documented"),
            cite(ro, 149, "num = (pred[:, start_step:] - true[:, start_step:]).abs().sum(dim=-1)",
                 "numerator"),
            cite(ro, 150, "den = true[:, start_step:].abs().sum(dim=-1)", "denominator"),
            cite(ro, 152, "return float(r.mean().item()), r", "the aggregate is a flat mean"),
            cite(mt, 203, "traj_autoregressive_error = ((state_traj_pred[:, self.start_step:]",
                 "the upstream line this reproduces, verbatim in behaviour"),
            cite(mt, 201, "self.start_step = self.history_horizon", "where t_0 comes from"),
        ],
    }

    # ------------------------------------------------------------- nRMSE
    out["metrics"]["nrmse_pooled"] = {
        "name": "nRMSE (form 1, pooled) -- THE PRIMARY AGGREGATION",
        "what_it_is": "normalised RMSE with a denominator fixed once over the training "
                      "episodes, so it cannot approach zero",
        "latex":
            r"\mathrm{nRMSE}_t \;=\; \frac{\sqrt{\dfrac{1}{45}\sum_{d=1}^{45}"
            r"\mathrm{MSE}_{t,d}}}{\dfrac{1}{45}\sum_{d=1}^{45}\sigma^{\mathrm{tr}}_{d}}"
            r"\quad\text{with}\quad "
            r"\mathrm{MSE}_{t,d}=\frac{1}{B}\sum_{b=1}^{B}\bigl(\hat{s}^{(b)}_{t,d}-s^{(b)}_{t,d}\bigr)^{2}",
        "aggregation_form": "form 1: POOL over dimensions, then divide. A ratio of "
                            "means, not a mean of ratios.",
        "why_form_1": "form 2 (mean over d of RMSE_d / scale_d) is a mean of ratios and "
                      "gives whichever dimension has the smallest scale unbounded "
                      "leverage. The choice between them once inverted a comparison "
                      "against the released model (M-19, R-27, R-29). Form 2 is "
                      "retained only for continuity with numbers reported before M-19.",
        "reading": "1.0 means no better than predicting the training mean; below 1.0 "
                   "means the model carries information",
        "citations": [
            cite(me, 119, "sqrt( mean over dims of MSE_d ) / mean over dims of scale_d",
                 "the formula, as documented"),
            cite(me, 133, "return float((_np.sqrt(mse.mean(axis=1)) / sc.mean()).mean())",
                 "form 1, the primary aggregation"),
            cite(me, 144, "return float((_np.sqrt(mse) / sc).mean())",
                 "form 2, retained for continuity only"),
        ],
    }

    out["metrics"]["nrmse_form2"] = {
        "name": "nRMSE (form 2) -- reported only for continuity",
        "latex":
            r"\mathrm{nRMSE}^{(2)}_t \;=\; \frac{1}{45}\sum_{d=1}^{45}"
            r"\frac{\sqrt{\mathrm{MSE}_{t,d}}}{\sigma^{\mathrm{tr}}_{d}}",
        "aggregation_form": "form 2: divide per dimension, then average. A mean of ratios.",
        "status": "superseded as the primary aggregation by form 1 at Task 3d",
        "citations": [cite(me, 137, "FORM 2, retained for continuity")],
    }

    # -------------------------------------------------- the scale constant
    scale = json.load(open(os.path.join(R.RESULTS, "step4_0a_results.json")))["nrmse_scale"]
    out["constants"]["nrmse_scale"] = {
        "symbol": r"\sigma^{\mathrm{tr}}_{d}",
        "definition": "the standard deviation of config-normalised state dimension d, "
                      "taken over the rows belonging to TRAINING episodes only",
        "latex":
            r"\sigma^{\mathrm{tr}}_{d} \;=\; \operatorname{sd}\bigl(\{\,\tilde{s}_{i,d}"
            r"\;:\; \mathrm{episode}(i)\in\mathcal{E}_{\mathrm{train}}\,\}\bigr)",
        "n_dims": len(scale),
        "min": min(scale), "max": max(scale),
        "mean": sum(scale) / len(scale),
        "stored_at": "results/step4_0a_results.json -> nrmse_scale",
        "properties": [
            "computed ONCE and stored; never recomputed per timestep",
            "never derived from held-out data, so the metric's denominator carries no "
            "information about the arena it is scored on",
            "strictly positive by assertion, so the metric cannot go non-finite",
        ],
        "citations": [
            cite(me, 39, "scale = norm.std(axis=0)", "the computation"),
            cite(me, 37, "rows = np.isin(episode_id, list(train_episodes))",
                 "training rows only"),
            cite(me, 41, 'assert np.all(scale > 0)', "the positivity assertion"),
        ],
    }
    out["constants"]["config_normalisation"] = {
        "definition": "the config's own per-dimension mean and std, applied before any "
                      "metric is taken, so every quantity here lives in the space the "
                      "model predicts in",
        "citations": [
            cite(os.path.join(RWML, "scripts", "configs", "anymal_d_flat_cfg.py"), 47,
                 "state_data_mean: List[float]", "the means"),
            cite(os.path.join(RWML, "scripts", "configs", "anymal_d_flat_cfg.py"), 55,
                 "state_data_std: List[float]", "the stds"),
        ],
    }

    # ------------------------------------------------------------ coverage
    out["coverage"] = {
        "name": "coverage at +-k sigma",
        "definition_in_words":
            "the fraction of scalar (trajectory, forecast step, state dimension) "
            "triples whose absolute realised error is at most k times the sigma "
            "predicted for that same triple",
        "latex":
            r"\mathrm{cov}_{\pm k\sigma}(h) \;=\; \frac{1}{B\,h\,45}"
            r"\sum_{b=1}^{B}\sum_{t=t_0+1}^{t_0+h}\sum_{d=1}^{45}"
            r"\mathbf{1}\!\left[\;\frac{\bigl|\hat{s}^{(b)}_{t,d}-s^{(b)}_{t,d}\bigr|}"
            r"{\sigma^{(b)}_{t,d}} \;\le\; k \;\right]",
        "z_statistic": r"z^{(b)}_{t,d} = \bigl|\hat{s}^{(b)}_{t,d}-s^{(b)}_{t,d}\bigr| "
                       r"/ \max(\sigma^{(b)}_{t,d}, 10^{-30})",
        "pooling_axes_in_order": [
            "axis 0: trajectory (and, where several seeds are scored together, seeds "
            "are CONCATENATED onto this same axis before pooling -- see the caution "
            "below)",
            "axis 1: forecast step, taken cumulatively over steps 1..h so coverage at "
            "h is an average over the whole rollout up to h, not the value AT step h",
            "axis 2: state dimension, all 45",
        ],
        "aggregation": "an unweighted mean over the flattened array; every triple "
                       "carries equal weight, so a horizon-h figure is dominated by "
                       "the deepest steps only in as much as they are more numerous, "
                       "which they are not -- each step contributes equally",
        "cumulative_not_pointwise":
            "IMPORTANT. cov(h) averages steps 1..h. It is not the coverage at step h. "
            "The same convention is used for the err/sigma ratio and for every "
            "horizon-indexed quantity in the paper.",
        "nominal": {
            "pm1": 0.6826894921370859,
            "pm2": 0.9544997361036416,
            "why": "z is built from an ABSOLUTE error, so z <= k is the two-sided event "
                   "and the nominal is erf(k/sqrt(2)): 68.27% at k=1, 95.45% at k=2. "
                   "The paper quotes these to two decimals throughout -- 68.27% and 95.45% -- "
                   "rather than the 68.3/95.4 rounding, which once had the same "
                   "constant appearing in two numeric spellings across a figure "
                   "caption and the section that derives it.",
        },
        "which_sigma": {
            "aleatoric": "the mean over ensemble members of each member's predicted "
                         "per-dimension sigma (system_dynamics.py:125)",
            "epistemic": "the per-dimension standard deviation across members' mean "
                         "predictions. NOTE the scalar the METHOD applies is this "
                         "summed over dimensions (system_dynamics.py:126); for a "
                         "per-dimension coverage the per-dimension form is the only "
                         "one that types.",
        },
        "caution_seeds_are_not_trajectories":
            "in task1_calibration.py the per-seed error and sigma arrays are "
            "concatenated along axis 0 before pooling, so seeds enter the coverage "
            "average as if they were extra trajectories. That is fine for a point "
            "estimate -- it is a mean of means over a balanced design -- but it is "
            "NOT a valid resampling unit. Every interval in this paper resamples "
            "whole trajectories; pooling seed x trajectory and resampling the pooled "
            "vector narrows intervals by about sqrt(3) (M-27).",
        "citations": [
            cite(ca, 65, "z=err/np.maximum(sig,1e-30)", "the z statistic"),
            cite(ca, 73, "c1=float((z[:,:h]<=1).mean()); c2=float((z[:,:h]<=2).mean())",
                 "the coverage itself: cumulative over steps 1..h, flat mean over all axes"),
            cite(ca, 64, "err=np.concatenate(E_,0); sig=np.concatenate(SG,0)",
                 "where seeds join the trajectory axis"),
            cite(ca, 74, 'rec["coverage"][h]={"pm1":c1,"pm2":c2,"dev1":c1-0.683',
                 "the nominal it is judged against"),
        ],
    }

    # ------------------------------------------------- the overconfidence ratio
    out["metrics"]["overconfidence_factor"] = {
        "name": "overconfidence factor (mean |error| / mean sigma)",
        "what_it_is": "the headline calibration number: how many times larger the "
                      "typical realised error is than the typical predicted sigma",
        "latex":
            r"\rho(h) \;=\; \frac{\operatorname{mean}_{b,t\le h,d}"
            r"\bigl|\hat{s}^{(b)}_{t,d}-s^{(b)}_{t,d}\bigr|}"
            r"{\operatorname{mean}_{b,t\le h,d}\ \sigma^{(b)}_{t,d}}",
        "it_is_a_ratio_of_means":
            "NOT a mean of ratios. mean|error| and mean sigma are each averaged over "
            "the same pooled axes first, and the ratio is taken once at the end. The "
            "mean-of-ratios form is unbounded whenever a single sigma is near zero, "
            "which is exactly the regime 5.3 puts these models in.",
        "reads_as": "rho = 1 is not calibration -- a calibrated Gaussian has "
                    "mean|error| / sigma = sqrt(2/pi) = 0.7979. rho is reported as a "
                    "magnitude of miscalibration, and coverage is the calibrated "
                    "reading. Both are given everywhere for that reason.",
        "calibrated_value_of_rho": 0.7978845608028654,
        "citations": [
            cite(ca, 67, '"ratio_err_over_sigma":float(err.mean()/sig.mean())',
                 "ratio of means, computed once"),
        ],
    }

    # ------------------------------------------- which metric each headline uses
    out["which_is_headline"] = {
        "A_over_B_training_claim": {
            "metric": "relative-L1",
            "why": "it is the upstream's own metric; the claim is about reproducing "
                   "the upstream's comparison",
            "must_be_named_in": ["abstract", "4"],
        },
        "calibration_claims": {
            "metric": "overconfidence factor and coverage at +-1 sigma",
            "why": "a calibration claim is about sigma against realised error, and "
                   "neither relative-L1 nor nRMSE involves sigma",
            "must_be_named_in": ["abstract", "5.2", "12"],
        },
        "ranking_claims": {
            "metric": "Pearson r between the applied scalar penalty and total "
                      "absolute error over a rollout",
            "why": "a ranking claim is about order, not scale",
            "must_be_named_in": ["abstract", "5.6"],
        },
    }

    # the LaTeX strings are what render into 2.1; a malformed one is a build failure
    # later and a silent garble in the PDF, so check them here while there is context
    for section in ("metrics", "constants", "coverage"):
        blocks = out[section] if section == "coverage" else out[section]
        items = [blocks] if section == "coverage" else list(blocks.values())
        for it in items:
            for key in ("latex", "latex_per_step", "latex_aggregate", "z_statistic"):
                if key in it:
                    s = it[key]
                    assert s.count("{") == s.count("}"), f"unbalanced braces in {key}: {s}"
                    assert "\\frac" in s or "\\sum" in s or "\\operatorname" in s \
                        or "\\sqrt" in s or "\\mathbf" in s or "\\bigl" in s, \
                        f"{key} does not look like a formula: {s}"

    n_cites = sum(len(v.get("citations", []))
                  for sec in ("metrics", "constants") for v in out[sec].values())
    n_cites += len(out["coverage"]["citations"])
    out["n_citations_verified"] = n_cites

    dst = os.path.join(R.RESULTS, "v3_metric_definitions.json")
    with open(dst, "w") as f:
        json.dump(out, f, indent=2, sort_keys=True)
    print(f"metrics defined:  {', '.join(sorted(out['metrics']))}")
    print(f"constants:        {', '.join(sorted(out['constants']))}")
    print(f"coverage pooled over {len(out['coverage']['pooling_axes_in_order'])} axes, "
          f"nominal +-1s = {out['coverage']['nominal']['pm1']:.4f}")
    print(f"{n_cites} implementation citations read back and verified")
    print(f"\nwrote {dst}")


if __name__ == "__main__":
    main()
