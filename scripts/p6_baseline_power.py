"""
P6 -- what rules M-75 and M-76 (the architecture baselines) can detect, measured
BEFORE any baseline model exists.

Two rules, one statistic. For each baseline b (MLP, RSSM, transformer):

    D_b = mean over the 4 held-out trajectories of
          [ 3-seed mean err_b(traj) - 3-seed mean err_RWM(traj) ]

where RWM is the existing Arm A at 2,500 iterations, seeds 0-2, with Holm's correction
across the three baselines of ONE rule:

  M-75  the baselines TEACHER-FORCED, as the original trains them (2501.10100v1 §IV-D):
        the claim as the original makes it;
  M-76  the baselines AUTOREGRESSIVE over N = 8, as Arm A: the architecture question
        with the training regime held fixed.

Both rules face the same four held-out trajectories as §5 and the sweep, so the
machinery is scripts/p5_sweep_power.py's, imported rather than copied: the exact
256-resample bootstrap, the M-44 formula MDE under the same-configuration null, and the
exact-test dilution of a proportional effect. Only the family size differs (m = 3).

The real-contrast checks differ by rule, because each asks whether the exact test
detects a real change OF THE KIND that rule compares:
  M-75  Arm B (RWM teacher-forced) against Arm A (RWM autoregressive): a teacher-forced
        model against the autoregressive one, which is exactly the shape of M-75's
        contrasts;
  M-76  the corrected-NLL arm and the ensemble-of-5 arm against Arm A: autoregressive
        models of a different construction, as M-76's baselines will be.

CAUTION written into the artifact: the noise model is Arm A's seed noise. A baseline
whose seed-to-seed spread is larger -- plausible for a small transformer -- makes its
contrast noisier, and the MDE here is then a LOWER bound for it.

Reads the stored rollouts in cache/; no model is evaluated. Writes
results/p6_baseline_power.json.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402

import p5_sweep_power as P5  # noqa: E402
import rollout_eval as E  # noqa: E402
import rwm_data as R  # noqa: E402

OUT = "p6_baseline_power.json"
BASELINES = ("MLP", "RSSM", "transformer")
RULES = {
    "M-75": {"regime": "teacher-forced, as the original (2501.10100v1 §IV-D)",
             "real_contrasts": {"armB_teacher_forced": "Arm B, RWM teacher-forced"}},
    "M-76": {"regime": "autoregressive over N = 8, as Arm A",
             "real_contrasts": {"armA_corrected_nll": "Arm A with the corrected Gaussian NLL",
                                "armA_ens5": "Arm A as an ensemble of 5"}},
}


def main():
    T = P5.truth_and_scale()
    assert T["n_ind"] == 4, f"n_independent {T['n_ind']}, the rules are written for 4"
    vc, files = P5.per_traj(P5.CENTRE, P5.SEEDS, T)
    others = {}
    for rule in RULES.values():
        for slug in rule["real_contrasts"]:
            if slug not in others:
                others[slug], f = P5.per_traj(slug, P5.SEEDS, T)
                files += f
    P5.cross_check_head_to_head(vc, others["armB_teacher_forced"])
    m = len(BASELINES)
    levels = P5.holm_levels(m)
    print("=" * 100)
    print("P6 — WHAT RULES M-75 AND M-76 (THE ARCHITECTURE BASELINES) CAN DETECT, BEFORE ANY RUN")
    print("=" * 100)
    print(f"  arena       : {P5.ARENA}, episodes {T['episodes']}, starts {T['starts']}, "
          f"n_independent = {T['n_ind']}")
    print(f"  family      : {', '.join(BASELINES)} (m = {m}); Holm levels "
          + ", ".join(f"{a:.5f}" for a in levels))

    rules_out = {}
    for rid, rule in RULES.items():
        est = {}
        for metric in ("l1", "nrmse"):
            for h in (P5.ANCHOR_H, P5.REPORTED_H):
                # The estimate is P5's, run at m = 3; its real-contrast field is replaced
                # by this rule's own contrasts below.
                r = P5.estimate(vc, others[next(iter(rule["real_contrasts"]))], m, metric, h)
                j = P5.HORIZONS.index(h)
                real = {}
                for slug, label in rule["real_contrasts"].items():
                    d = others[slug][metric][:, :, j].mean(0) - vc[metric][:, :, j].mean(0)
                    real[slug] = {"label": label, "per_traj": d.tolist(),
                                  "mean": float(d.mean()), "n_positive": int((d > 0).sum()),
                                  "p_exact": P5.boot_p(d), "ci95_exact": P5.boot_ci(d)}
                r["observed_real_contrast"] = real
                est[f"{metric}_h{h}"] = r
        rules_out[rid] = {"regime": rule["regime"], "estimates": est}
        print(f"\n  {rid} — baselines {rule['regime']}")
        for key, r in est.items():
            ex = "; ".join(f"Holm {x['step']} {x['delta80_pct']}"
                           for x in r["exact_mde_by_holm_step"])
            fp = r["formula_null"]["mde_pct_by_level"][f"{levels[0]:.6f}"]
            print(f"    {key:<11} BINDING {r['binding_mde_pct_of_centre']:.1f}% of RWM's error "
                  f"({r['binding_from']}); formula Holm 1 {fp:.1f}%; exact {ex}")
            for slug, c in r["observed_real_contrast"].items():
                print(f"      real contrast {slug:<22} mean {c['mean']:+.4f}  "
                      f"{c['n_positive']}/4 positive  exact p {c['p_exact']:.4f}")

    out = {
        "purpose": "rules M-75 and M-76 — the minimum detectable effect of D_b at the n they "
                   "face, estimated before any baseline model exists",
        "method": ("scripts/p5_sweep_power.py's, imported: exact 256-resample cluster "
                   "bootstrap, M-44 formula MDE under the same-configuration null, and an "
                   "exact-test dilution of a proportional effect; binding = the larger at "
                   "Holm's first step"),
        "arena": P5.ARENA, "episodes": T["episodes"], "traj_start_row": T["starts"],
        "n_independent": T["n_ind"], "unit_length": P5.UNIT, "start_step": E.START_STEP,
        "anchor_horizon": P5.ANCHOR_H, "reported_horizon": P5.REPORTED_H,
        "rwm_arm": {"cache_slug": P5.CENTRE, "seeds": list(P5.SEEDS),
                    "checkpoint": "weights_2500.pt"},
        "baselines": list(BASELINES), "m": m, "holm_levels": levels,
        "min_p_by_sign_pattern": P5.min_p_by_sign_pattern(4),
        "three_of_four_rejectable_at_holm_step": [
            k + 1 for k, a in enumerate(levels) if 2 * (1 / 4) ** 4 <= a],
        "input_files": files,
        "rules": rules_out,
        "cautions": [
            "the noise model is Arm A's seed noise; a baseline with a larger seed spread "
            "makes its contrast noisier, and the MDE is then a lower bound for it",
            "the exact MDE is for an effect proportional to RWM's error on every trajectory; "
            "an effect of mixed sign across trajectories is not detectable at n = 4",
        ],
    }
    json.dump(out, open(os.path.join(R.RESULTS, OUT), "w"), indent=2)
    print(f"\n  wrote results/{OUT}")


if __name__ == "__main__":
    main()
