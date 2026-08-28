"""Generate MODEL_CARD.md for the released checkpoints.

Like the paper, the numbers come from the artifacts. The per-checkpoint limitations
are the point of the document: three of the four checkpoints have a uselessly
calibrated sigma head, and the card has to say so where someone will read it before
using the weights, not only in the paper.
"""
import hashlib
import re
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402

CKPTS = [
    # The paper's headline is a three-seed mean, so all three seeds of each arm ship.
    ("armA_seed0_10k/weights_10000.pt", "autoregressive-10k-seed0", "faithful (mse)", None),
    ("armA_seed1_10k/weights_10000.pt", "autoregressive-10k-seed1", "faithful (mse)", None),
    ("armA_seed2_10k/weights_10000.pt", "autoregressive-10k-seed2", "faithful (mse)", None),
    ("armB_seed0_10k/weights_10000.pt", "teacher-forced-10k-seed0", "teacher-forced armB", None),
    ("armB_seed1_10k/weights_10000.pt", "teacher-forced-10k-seed1", "teacher-forced armB", None),
    ("armB_seed2_10k/weights_10000.pt", "teacher-forced-10k-seed2", "teacher-forced armB", None),
    ("armA_seed0/weights_2500.pt", "autoregressive-2500", "faithful (mse)",
     "Arm A at the paper's stated iteration count, for comparison with the released checkpoint."),
    ("armA_seed0_nll/weights_2500.pt", "corrected-objective-2500", "corrected (nll)",
     "Trained with the reference's unused `gaussian_nll` branch. This is the CORRECTED-OBJECTIVE "
     "artifact, not a calibrated one \u2014 see the limitation above."),
    # Ensemble 5. These are the only checkpoints here with a non-zero EPISTEMIC
    # term -- at ensemble size 1 it is identically zero by construction, so the
    # other six cannot be used to reproduce anything in section 5.6 at all.
    ("armA_seed0_ens5/weights_2500.pt", "autoregressive-ens5-seed0", "faithful (mse)",
     "Ensemble size 5. The only checkpoints here with a non-zero epistemic term; the others "
     "have exactly zero by construction. See the ensemble-5 block below."),
    ("armA_seed1_ens5/weights_2500.pt", "autoregressive-ens5-seed1", "faithful (mse)",
     "Ensemble size 5, seed 1."),
    ("armA_seed2_ens5/weights_2500.pt", "autoregressive-ens5-seed2", "faithful (mse)",
     "Ensemble size 5, seed 2."),
    # C6(rev2), 6.2. 6.10 scores seeds 0-4 of Arm A together as a genuinely
    # independent five-model ensemble, and the two seeds that experiment added
    # were not released. A reader cannot reproduce the strongest new result in
    # the paper without them.
    ("armA_seed3/weights_2500.pt", "autoregressive-ens1-seed3", None,
     "Arm A at ensemble size 1, seed 3. Trained for the independent-ensemble test: seeds 0-4 "
     "of this arm are scored together as a five-model ensemble that shares nothing (§6.10). "
     "Not part of the three-seed headline. **No per-arm σ calibration is quoted below**: "
     "`task1_calibration.py` measures seed 0 only, and pasting seed 0's figure onto this "
     "checkpoint is exactly the mis-attribution this card was corrected for elsewhere. What "
     "was measured on this checkpoint is its contribution to the ensemble above."),
    ("armA_seed4/weights_2500.pt", "autoregressive-ens1-seed4", None,
     "Arm A at ensemble size 1, seed 4. The second of the two seeds added for the "
     "independent-ensemble test, and the same caveat applies: no individually measured σ "
     "calibration exists for it, only its contribution to the five-model ensemble above."),
]


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def main():
    cal = json.load(open(os.path.join(R.RESULTS, "task1_calibration.json")))
    _e5 = json.load(open(os.path.join(R.RESULTS, "task_d3_ens5.json")))
    E5A = _e5.get("aleatoric_calibration")
    E5E = _e5.get("calibration")
    # C3(rev2), 3.9. This rounded to one decimal while the paper derives and
    # quotes 68.27 everywhere, so the card and the paper disagreed about a
    # constant. count-consistency now forbids the 68.3 spelling in this file.
    NOM1 = f'{100 * json.load(open(os.path.join(R.RESULTS, "v3_metric_definitions.json")))["coverage"]["nominal"]["pm1"]:.2f}'
    DEPLOY_H = json.load(open(os.path.join(R.RESULTS, "v2_deployment_horizon.json"))
                         )["verdict"]["deployment_horizon_is"]
    N = json.load(open(os.path.join(R.RESULTS, "paper_numbers.json")))
    v = lambda k: N[k]["value"]  # noqa: E731

    d1 = json.load(open(os.path.join(R.RESULTS, "task_d1_threeseed.json")))
    AG = d1["aggregate"]

    def default_blurb(name, calkey):
        arm = "A" if "autoregressive" in name else "B"
        seed = name[-1]
        if not name.endswith(("0", "1", "2")) or "10k" not in name:
            return ""
        v = AG[arm]["per_seed"].get(seed)
        role = ("Autoregressive training \u2014 the arm the base paper's claim is about."
                if arm == "A" else
                "Teacher forcing \u2014 the comparison arm. Released so the central claim can be "
                "checked rather than taken on trust.")
        return (f"{role} Seed {seed} of three at 10,000 iterations; scores {v:.4f} normalised "
                f"error at a 368-step horizon on held-out episodes "
                f"(arm mean {AG[arm]['mean']:.4f} \u00b1 {AG[arm]['sd_ddof1']:.4f} over three seeds).")

    rows, present = [], []
    for path, name, calkey, blurb in CKPTS:
        blurb = blurb or default_blurb(name, calkey)
        full = os.path.join("runs", path)
        if not os.path.exists(full):
            rows.append((name, path, None, None, calkey, blurb))
            continue
        present.append(name)
        rows.append((name, path, os.path.getsize(full), sha256(full), calkey, blurb))

    L = []
    A = L.append
    # HuggingFace requires YAML front matter in the repo card; without it the Hub
    # shows "empty or missing yaml metadata in repo card".
    A("---")
    A("license: apache-2.0")
    A("library_name: pytorch")
    A("tags:")
    for t in ("robotics", "world-models", "model-based-rl", "reproduction",
              "uncertainty-quantification", "legged-robotics"):
        A(f"  - {t}")
    A("pipeline_tag: robotics")
    A("---")
    A("")
    A("# Model card — RWM reproduction checkpoints")
    A("")
    A("Independent reproduction of the proprioceptive dynamics model of Li, Krause & Hutter,")
    A("*Robotic World Model* (arXiv:2501.10100) and *Uncertainty-Aware RWM* (arXiv:2504.16680).")
    A("Not affiliated with, endorsed by, or reviewed by the original authors.")
    A("")
    A("Code, evidence and the full claim record: https://github.com/joyjeet-singh/rwm")
    A("")
    A("## Read this before using the σ output")
    A("")
    A("**These models' predicted standard deviation is not a usable uncertainty estimate.**")
    A("It is not a matter of degree. Measured against realised error on held-out episodes:")
    A("")
    A(r"| checkpoint | mean \|error\| / mean σ [95% CI] | coverage at ±1σ [95% CI] "
      r"| a calibrated model |")
    A("|---|---|---|---|")
    for lab, key in (("autoregressive (mse)", "faithful (mse)"),
                     ("corrected objective (nll)", "corrected (nll)"),
                     ("teacher-forced", "teacher-forced armB"),
                     ("*released reference checkpoint, for comparison*", "released ckpt")):
        m = cal[key]
        rc = m["ratio_err_over_sigma_ci"]
        cc = m["coverage"]["1"]["pm1_ci"]
        A(f"| {lab} | {m['ratio_err_over_sigma']:,.0f}× "
          f"[{rc[0]:,.0f}, {rc[1]:,.0f}] | "
          f"{100*m['coverage']['1']['pm1']:.2f}% "
          f"[{100*cc[0]:.2f}, {100*cc[1]:.2f}] | {NOM1}% |")
    A("")
    A(f"Those are the ALEATORIC term, at one forecast step. The quantity the follow-up's method "
      f"actually penalises rewards with is the EPISTEMIC one, and on the released "
      f"{v('b2_members')}-member checkpoint it is {v('d1n_epi_ratio_h100')}× "
      f"[{v('d1n_epi_ratio_ci_h100')}] out at h = {DEPLOY_H} — the horizon the method's own "
      f"imagination rollouts run to — with {v('d1n_epi_cov1_h100')}% coverage at ±1σ. Our "
      f"ensemble-5 arms reach {v('e5_ratio_h100')}× [{v('e5_ratio_ci_h100')}] on the same "
      f"measurement. Better, and not calibrated.")
    A("")
    A("The cause is structural, not a training accident: the state loss is squared error on a")
    A("reparameterised sample with no log-σ term, so its optimum is σ = 0, and the bound term that")
    A("should oppose it cancels algebraically. The `corrected-objective-2500` checkpoint uses the")
    A("reference's unused `gaussian_nll` branch, which reverses the mechanism and still does not")
    A(f"produce a usable estimate ({v('cal_nll_ratio')}× overconfident). **It is released as the")
    A("corrected-objective artifact, not as a calibrated one.**")
    A("")
    A("If you need to rank which predictions will be worse, the σ output carries some signal —")
    A("but treat that as directional, not established. Converting per-dimension sign counts to")
    A("P-values against an independent-trials null overstates the evidence badly: the 45 state")
    A("dimensions are physically coupled and share a forecast-depth trend, so a σ that grows with")
    A("depth correlates with any trajectory's error. Under a permutation test over whole")
    A("trajectories, no such count in our paper survives multiplicity correction.")
    A("")
    A("If you need an interval, the raw σ will not give you one. Do not use it for risk-gating,")
    A("safety margins, or anything that treats σ as a scale.")
    A("")
    A("**There is a remedy, and it is cheap.** A single multiplier does not work, because the")
    A("miscalibration grows with forecast horizon. One multiplier *per horizon*, fitted on held-out")
    A(f"data, does: on the released reference checkpoint it restored ±1σ coverage to within")
    A(f"{v('d3_tol')} points of nominal on {v('d3_epi_ok')} of {v('d3_epi_cells')} held-out cells,")
    A(f"where a single global multiplier managed {v('d3_epi_const_ok')}. We measured that on the")
    A("reference checkpoint rather than on these arms, and on two episodes only, so refit it on your")
    A("own data rather than copying our constants.")
    A("")
    A("## The ensemble-5 checkpoints, and what they are for")
    A("")
    _n_ens1 = sum(1 for _, n, _, _ in CKPTS if "ens5" not in n)
    _n_ens5 = sum(1 for _, n, _, _ in CKPTS if "ens5" in n)
    _W = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven",
          8: "Eight", 9: "Nine", 10: "Ten", 11: "Eleven", 12: "Twelve", 13: "Thirteen"}
    A(f"{_W.get(_n_ens1, _n_ens1)} of the {_W.get(len(CKPTS), len(CKPTS)).lower()} checkpoints "
      "here run at **ensemble size 1**, where the")
    A("epistemic term -- the disagreement across ensemble members -- is *identically zero by")
    A("construction*. Nothing about ensemble disagreement can be reproduced from one of them")
    A("alone; the block above says what to do with five of them.")
    A("")
    A(f"The {_W.get(_n_ens5, _n_ens5).lower()} `autoregressive-ens5-*` checkpoints carry it "
      "directly. On them:")
    A("")
    A(f"- ensemble disagreement correlates with realised error in {v('e5_lead_cells')} of")
    A(f"  {v('e5_total_cells')} seed-horizon cells more strongly than the forecast step index does,")
    A("  which is the property our paper argues makes it a usable ranking signal;")
    A(f"- the epistemic term is **{v('e5_ratio_h100')}x** smaller than the realised error at")
    A(f"  h={DEPLOY_H} -- the horizon the method's own imagination rollouts run to -- with")
    A(f"  {v('e5_cov1_h100')}% coverage at +-1 sigma against a calibrated {NOM1}%, and")
    A(f"  {v('e5_ratio_h368')}x with {v('e5_cov1_h368')}% at the {v('v2_diag_h')}-step open-loop")
    A("  diagnostic horizon. Better than the released reference checkpoint, and still not an")
    A("  interval;")
    A(f"- it is input-dependent, CoV {v('e5_cov_lo')}-{v('e5_cov_hi')} across a batch.")
    A("")
    A("**The pre-registered rule governing this replication returned "
      f"{v('e5_verdict')}**, on its")
    A(f"second condition: the paired difference against the index excludes zero at {v('e5_n_excl')}")
    A(f"of {v('e5_n_horizons')} horizons, not a majority. The direction replicated everywhere; the")
    A("separation did not, on the four independent trajectories our held-out arena has. Treat the")
    A("ranking property as supported on these checkpoints and established only on the released")
    A("reference one.")
    A("")
    A("## Scoring five of these together: the independent-ensemble result")
    A("")
    A("**If you download the ensemble-size-1 autoregressive checkpoints, score them as an")
    A("ensemble.** The paper's §6.10 takes seeds 0-4 of Arm A -- five separately initialised,")
    A("separately trained models, sharing no parameters and no recurrent state -- and scores")
    A("their disagreement the way the method scores its own. That is the contrast the released")
    A("five-member checkpoint cannot provide, because its five members share one GRU trunk and")
    A(f"one hidden state: {v('v1_shared_pct')}% of each member's state-pathway parameters are")
    A("numerically identical to every other member's.")
    A("")
    A(f"- **The independent ensemble is {v('m44_ratio_gain')}x better calibrated** than the")
    A(f"  shared-trunk `autoregressive-ens5-*` arms at h={DEPLOY_H}, against a pre-registered")
    A(f"  minimum detectable effect of {v('m44_mde_ratio')}x. Coverage is {v('m44_cov_gain')}")
    A(f"  points higher, against an MDE of {v('m44_mde_cov')} points. The rule (M-44, committed")
    A(f"  before the runs) returns **{v('m44_verdict')}**.")
    A(f"- **It is still not an interval.** {v('r2_indep_ratio_h100')}x overconfident at")
    A(f"  h={DEPLOY_H} with {v('r2_indep_cov1_h100')}% coverage at +-1 sigma, against a")
    A(f"  calibrated {NOM1}%. Building the ensemble properly is worth doing and is not")
    A("  sufficient.")
    A(f"- **What the gain is made of.** sigma larger by {v('r2_sigma_x_h100')}x --")
    A(f"  {v('r2_from_sigma_h100')}% of the improvement at h={DEPLOY_H} -- and the rest ordinary")
    A(f"  ensembling accuracy. At the {v('v2_diag_h')}-step diagnostic horizon the split reverses:")
    A(f"  {v('r2_from_acc_h368')}% of it is the ensemble simply predicting better.")
    A(f"- **What it does not isolate.** Five independent models differ from five shared heads in")
    A(f"  initialisation, in data ordering AND in capacity: {v('v1_cap_indep')} state-pathway")
    A(f"  parameters against {v('v1_cap_shared')}, a factor of {v('v1_cap_ratio')}. The comparison")
    A("  bounds the trunk-sharing effect rather than isolating it.")
    A("")
    A("## Checkpoints")
    A("")
    for name, path, size, digest, calkey, blurb in rows:
        A(f"### `{name}`")
        A("")
        A(blurb)
        A("")
        if size is None:
            A(f"- source: `runs/{path}` — **not present in this working tree**")
        else:
            A(f"- source: `runs/{path}`")
            A(f"- size: {size:,} bytes")
            A(f"- sha256: `{digest}`")
        # The ens5 arms get their OWN aleatoric calibration, not the ens1 arm's.
        #
        # All three autoregressive-ens5-* entries used to carry "52x overconfident,
        # coverage 11.67%" -- the ens1 Arm A figure pasted onto three different
        # models, and unlike the 10k entries it carried no "not re-measured"
        # caveat. task_d3_ens5.py now measures each arm's own aleatoric sigma on
        # the same rollouts it already computes, so the number is measured rather
        # than inherited or caveated.
        seed = None
        if "_ens5" in path:
            seed = int(re.search(r"seed(\d+)_ens5", path).group(1))
        if seed is not None and E5A:
            r1 = next(r for r in E5A["1"]["per_seed"] if r["seed"] == seed)
            rD = next(r for r in E5A[str(DEPLOY_H)]["per_seed"] if r["seed"] == seed)
            A(f"- σ calibration (aleatoric), measured on THIS arm at iteration 2,500: "
              f"{r1['ratio_err_over_sigma']:,.1f}× overconfident with "
              f"{100*r1['coverage_pm1']:.2f}% coverage at ±1σ (h=1), and "
              f"{rD['ratio_err_over_sigma']:,.1f}× with "
              f"{100*rD['coverage_pm1']:.2f}% at h={DEPLOY_H}")
            e1 = E5E["1"]["per_seed"]; eD = E5E[str(DEPLOY_H)]["per_seed"]
            q1 = next(r for r in e1 if r["seed"] == seed)
            qD = next(r for r in eD if r["seed"] == seed)
            A(f"- σ calibration (epistemic — the quantity the method penalises with): "
              f"{q1['ratio_err_over_sigma']:,.1f}× at h=1 and "
              f"{qD['ratio_err_over_sigma']:,.1f}× at h={DEPLOY_H}, coverage "
              f"{100*qD['coverage_pm1']:.2f}% at ±1σ")
        else:
            m = cal.get(calkey)
            if m:
                # task1_calibration.py measures weights_2500.pt. Attaching that figure to a
                # 10,000-iteration checkpoint would mis-attribute it, so say which it is.
                at = "2,500" if "2500" in path else "2,500 (this arm; not re-measured at 10,000)"
                A(f"- σ calibration, measured at iteration {at}: "
                  f"{m['ratio_err_over_sigma']:,.0f}× overconfident, "
                  f"coverage {100*m['coverage']['1']['pm1']:.2f}% at ±1σ (h=1)")
        A("")
    A("## The result these support")
    A("")
    A(f"Normalised error at a {v('v2_diag_h')}-step horizon on held-out episodes, over three "
      "training seeds (standard deviation with `ddof=1`). That is the horizon the paper's "
      f"pre-registered rule names; at h={DEPLOY_H}, the method's own rollout length, the same "
      f"comparison gives {v('d1_ratio_h100')}\u00d7.")
    A("")
    A("| arm | seed 0 | seed 1 | seed 2 | mean \u00b1 sd |")
    A("|---|---|---|---|---|")
    for arm, lab in (("A", "autoregressive"), ("B", "teacher forcing")):
        g = AG[arm]
        A(f"| {lab} | {g['per_seed']['0']:.4f} | {g['per_seed']['1']:.4f} | "
          f"{g['per_seed']['2']:.4f} | **{g['mean']:.4f} \u00b1 {g['sd_ddof1']:.4f}** |")
    A("")
    A(f"Autoregressive training is better by a factor of "
      f"**{AG['ratio_B_over_A']:.2f}\u00d7**. For reference the hold-last floor \u2014 predicting "
      f"that nothing changes \u2014 scores {v('floor_h368')} in the same cell, so teacher forcing "
      f"is worse "
      f"than making no prediction at all.")
    A("")
    A("Every 10,000-iteration checkpoint was cross-checked against the 2,500-iteration run at "
      f"the same seed: {v('d1_xc_values')} logged values compared, {v('d1_xc_diff')} differing.")
    A("")
    A("## What these are")
    A("")
    A("- **Architecture.** GRU trunk, ensemble size 1, mean head plus bounded log-σ head, "
      "auxiliary contact and termination heads. Rebuilt from scratch, verified against the "
      f"reference at {v('diff_grad_max')} on losses and gradients across {v('diff_terms')} terms "
      f"and {v('diff_n_params')} parameter tensors before training.")
    A(f"- **Data.** The released ANYmal D dataset: {v('rows')} rows at 50 Hz, ten 20-second "
      f"episodes. Trained on {v('arm_clean_windows')} episode-respecting windows from eight "
      "episodes; two held out.")
    A("- **Action convention.** Row *t* holds the action that *produced* state *t*. These models "
      "are trained and evaluated under that causal pairing. The reference's *evaluation* path "
      "uses a stale action; ours does not. A consumer feeding actions the other way will get "
      "materially worse numbers.")
    A("- **Normalisation.** States are normalised with the reference's stored mean and std. "
      "Actions are not normalised, matching the reference.")
    A("")
    A("## Intended use")
    A("")
    A("Reproduction, verification and further study of the claims in the two papers above. These "
      "are CPU-trained research artifacts on one dataset, one gait and one terrain. They are not "
      "intended for deployment on hardware.")
    A("")
    A("## Limitations")
    A("")
    A("- **Most of these run at ensemble size 1**, against the reference's 5. On those the "
      "epistemic term is identically zero and the σ discussed above is aleatoric. The "
      "`ens5` arms and the five-seed independent ensemble cover the epistemic term.")
    A("- **One gait, one terrain, one command distribution.** Generalisation here means across "
      "velocity commands only.")
    A(f"- **Long-horizon claims rest on {v('m23_nind')} independent 400-step trajectories** in the "
      "held-out arena. That is the binding statistical constraint.")
    A("- **The 10k checkpoints are one seed per arm.** Recorded in the artifacts.")
    A("- **No policy learning.** Dynamics model only.")
    A("")
    A("## Licence and attribution")
    A("")
    A("Apache 2.0. Upstream: `robotic_world_model_lite` (Apache 2.0) and `rsl_rl_rwm` "
      "(BSD 3-Clause, ETH Zurich and NVIDIA); neither is redistributed here.")
    A("")
    A("## Citation")
    A("")
    A("See `CITATION.cff` in the repository.")

    open("MODEL_CARD.md", "w").write("\n".join(L) + "\n")
    print("MODEL CARD")
    print("=" * 70)
    print(f"  checkpoints described : {len(rows)}  (present in tree: {len(present)})")
    for name, path, size, digest, _, _ in rows:
        print(f"    {name:<26} {'MISSING' if size is None else f'{size:,} B  {digest[:16]}…'}")
    print(f"  wrote MODEL_CARD.md")


if __name__ == "__main__":
    main()
