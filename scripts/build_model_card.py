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
    ("armA_seed1_10k/weights_10000.pt", "autoregressive-10k",
     "faithful (mse)", "The main result. Arm A trained autoregressively for 10,000 iterations. "
     "Use this one if you want the model the base paper's claim is about."),
    ("armB_seed1_10k/weights_10000.pt", "teacher-forced-10k",
     "teacher-forced armB", "The comparison arm. Trains to a lower loss and rolls out far worse; "
     "released so the central claim can be checked rather than taken on trust."),
    ("armA_seed0/weights_2500.pt", "autoregressive-2500",
     "faithful (mse)", "Arm A at the paper's stated iteration count."),
    ("armA_seed0_nll/weights_2500.pt", "corrected-objective-2500",
     "corrected (nll)", "Trained with the reference's unused `gaussian_nll` branch. This is the "
     "CORRECTED-OBJECTIVE artifact, not a calibrated one — see the limitation below."),
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

    rows, present = [], []
    for path, name, calkey, blurb in CKPTS:
        full = os.path.join("runs", path)
        if not os.path.exists(full):
            rows.append((name, path, None, None, calkey, blurb))
            continue
        present.append(name)
        rows.append((name, path, os.path.getsize(full), sha256(full), calkey, blurb))

    L = []
    A = L.append
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
            A(f"- overconfidence: {m['ratio_err_over_sigma']:,.0f}×, "
              f"coverage {100*m['coverage']['1']['pm1']:.2f}% at ±1σ (h=1)")
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
