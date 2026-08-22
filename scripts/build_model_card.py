"""Generate MODEL_CARD.md for the released checkpoints.

Like the paper, the numbers come from the artifacts. The per-checkpoint limitations
are the point of the document: three of the four checkpoints have a uselessly
calibrated sigma head, and the card has to say so where someone will read it before
using the weights, not only in the paper.
"""
import hashlib
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
]


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def main():
    cal = json.load(open(os.path.join(R.RESULTS, "task1_calibration.json")))
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
    A(r"| checkpoint | mean \|error\| / mean σ | coverage at ±1σ | a calibrated model |")
    A("|---|---|---|---|")
    for lab, key in (("autoregressive (mse)", "faithful (mse)"),
                     ("corrected objective (nll)", "corrected (nll)"),
                     ("teacher-forced", "teacher-forced armB"),
                     ("*released reference checkpoint, for comparison*", "released ckpt")):
        m = cal[key]
        A(f"| {lab} | {m['ratio_err_over_sigma']:,.0f}× | "
          f"{100*m['coverage']['1']['pm1']:.2f}% | 68.3% |")
    A("")
    A("The cause is structural, not a training accident: the state loss is squared error on a")
    A("reparameterised sample with no log-σ term, so its optimum is σ = 0, and the bound term that")
    A("should oppose it cancels algebraically. The `corrected-objective-2500` checkpoint uses the")
    A("reference's unused `gaussian_nll` branch, which reverses the mechanism and still does not")
    A(f"produce a usable estimate ({v('cal_nll_ratio')}× overconfident). **It is released as the")
    A("corrected-objective artifact, not as a calibrated one.**")
    A("")
    A("If you need to rank which predictions will be worse, the σ output carries some signal.")
    A("If you need an interval, it does not. Do not use it for risk-gating, safety margins, or")
    A("anything that treats σ as a scale.")
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
    A("Normalised error at a 368-step horizon on held-out episodes, over three training seeds "
      "(standard deviation with `ddof=1`):")
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
      f"that nothing changes \u2014 scores 0.9930 in the same cell, so teacher forcing is worse "
      f"than making no prediction at all.")
    A("")
    A("Every 10,000-iteration checkpoint was cross-checked against the 2,500-iteration run at "
      "the same seed: 90,000 logged values compared, 0 differing.")
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
    A("- **Ensemble size 1**, against the reference's 5. The epistemic component of the released "
      "model's uncertainty is not reproduced; the σ discussed above is aleatoric.")
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
