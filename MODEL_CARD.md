# Model card — RWM reproduction checkpoints

Independent reproduction of the proprioceptive dynamics model of Li, Krause & Hutter,
*Robotic World Model* (arXiv:2501.10100) and *Uncertainty-Aware RWM* (arXiv:2504.16680).
Not affiliated with, endorsed by, or reviewed by the original authors.

Code, evidence and the full claim record: https://github.com/joyjeet-singh/rwm

## Read this before using the σ output

**These models' predicted standard deviation is not a usable uncertainty estimate.**
It is not a matter of degree. Measured against realised error on held-out episodes:

| checkpoint | mean \|error\| / mean σ | coverage at ±1σ | a calibrated model |
|---|---|---|---|
| autoregressive (mse) | 52× | 11.67% | 68.3% |
| corrected objective (nll) | 11× | 42.78% | 68.3% |
| teacher-forced | 315× | 12.96% | 68.3% |
| *released reference checkpoint, for comparison* | 7,878× | 0.56% | 68.3% |

The cause is structural, not a training accident: the state loss is squared error on a
reparameterised sample with no log-σ term, so its optimum is σ = 0, and the bound term that
should oppose it cancels algebraically. The `corrected-objective-2500` checkpoint uses the
reference's unused `gaussian_nll` branch, which reverses the mechanism and still does not
produce a usable estimate (10.9× overconfident). **It is released as the
corrected-objective artifact, not as a calibrated one.**

If you need to rank which predictions will be worse, the σ output carries some signal.
If you need an interval, it does not. Do not use it for risk-gating, safety margins, or
anything that treats σ as a scale.

## Checkpoints

### `autoregressive-10k`

The main result. Arm A trained autoregressively for 10,000 iterations. Use this one if you want the model the base paper's claim is about.

- source: `runs/armA_seed1_10k/weights_10000.pt`
- size: 5,683,412 bytes
- sha256: `c88b20a136c7364475e1bf74b3919b33de1ebad9293de521cfe259ed8474ee6e`
- overconfidence: 52×, coverage 11.67% at ±1σ (h=1)

### `teacher-forced-10k`

The comparison arm. Trains to a lower loss and rolls out far worse; released so the central claim can be checked rather than taken on trust.

- source: `runs/armB_seed1_10k/weights_10000.pt`
- size: 5,683,412 bytes
- sha256: `b473bd70d5afdcbb1065e7ef49e32e85d4941719ec1bf290e4a91a09b8165754`
- overconfidence: 315×, coverage 12.96% at ±1σ (h=1)

### `autoregressive-2500`

Arm A at the paper's stated iteration count.

- source: `runs/armA_seed0/weights_2500.pt`
- size: 5,683,374 bytes
- sha256: `bc4e0dfbcff28b994e3acabbae2d6f1d833331dc5bfad5cc9aa8f410385bd4b0`
- overconfidence: 52×, coverage 11.67% at ±1σ (h=1)

### `corrected-objective-2500`

Trained with the reference's unused `gaussian_nll` branch. This is the CORRECTED-OBJECTIVE artifact, not a calibrated one — see the limitation below.

- source: `runs/armA_seed0_nll/weights_2500.pt`
- size: 5,683,374 bytes
- sha256: `a1a339b27b077712b0a87b4df4718437933db3e6a370b8b08f941fab30129367`
- overconfidence: 11×, coverage 42.78% at ±1σ (h=1)

## What these are

- **Architecture.** GRU trunk, ensemble size 1, mean head plus bounded log-σ head, auxiliary contact and termination heads. Rebuilt from scratch, verified against the reference at 0.000e+00 on losses and gradients across 7 terms and 106 parameter tensors before training.
- **Data.** The released ANYmal D dataset: 10,000 rows at 50 Hz, ten 20-second episodes. Trained on 7,687 episode-respecting windows from eight episodes; two held out.
- **Action convention.** Row *t* holds the action that *produced* state *t*. These models are trained and evaluated under that causal pairing. The reference's *evaluation* path uses a stale action; ours does not. A consumer feeding actions the other way will get materially worse numbers.
- **Normalisation.** States are normalised with the reference's stored mean and std. Actions are not normalised, matching the reference.

## Intended use

Reproduction, verification and further study of the claims in the two papers above. These are CPU-trained research artifacts on one dataset, one gait and one terrain. They are not intended for deployment on hardware.

## Limitations

- **Ensemble size 1**, against the reference's 5. The epistemic component of the released model's uncertainty is not reproduced; the σ discussed above is aleatoric.
- **One gait, one terrain, one command distribution.** Generalisation here means across velocity commands only.
- **Long-horizon claims rest on 4 independent 400-step trajectories** in the held-out arena. That is the binding statistical constraint.
- **The 10k checkpoints are one seed per arm.** Recorded in the artifacts.
- **No policy learning.** Dynamics model only.

## Licence and attribution

Apache 2.0. Upstream: `robotic_world_model_lite` (Apache 2.0) and `rsl_rl_rwm` (BSD 3-Clause, ETH Zurich and NVIDIA); neither is redistributed here.

## Citation

See `CITATION.cff` in the repository.
