---
license: apache-2.0
library_name: pytorch
tags:
  - robotics
  - world-models
  - model-based-rl
  - reproduction
  - uncertainty-quantification
  - legged-robotics
pipeline_tag: robotics
---

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

If you need to rank which predictions will be worse, the σ output carries some signal —
but treat that as directional, not established. Converting per-dimension sign counts to
P-values against an independent-trials null overstates the evidence badly: the 45 state
dimensions are physically coupled and share a forecast-depth trend, so a σ that grows with
depth correlates with any trajectory's error. Under a permutation test over whole
trajectories, no such count in our paper survives multiplicity correction.

If you need an interval, the raw σ will not give you one. Do not use it for risk-gating,
safety margins, or anything that treats σ as a scale.

**There is a remedy, and it is cheap.** A single multiplier does not work, because the
miscalibration grows with forecast horizon. One multiplier *per horizon*, fitted on held-out
data, does: on the released reference checkpoint it restored ±1σ coverage to within
10 points of nominal on 10 of 10 held-out cells,
where a single global multiplier managed 2. We measured that on the
reference checkpoint rather than on these arms, and on two episodes only, so refit it on your
own data rather than copying our constants.

## The ensemble-5 checkpoints, and what they are for

Six of the nine checkpoints here run at **ensemble size 1**, where the epistemic
term -- the disagreement across ensemble members -- is *identically zero by
construction*. Nothing about ensemble disagreement can be reproduced from them.

The three `autoregressive-ens5-*` checkpoints exist for that reason. On them:

- ensemble disagreement correlates with realised error in 12 of
  12 seed-horizon cells more strongly than the forecast step index does,
  which is the property our paper argues makes it a usable ranking signal;
- the epistemic term is **13.0x** smaller than the realised error at a
  368-step horizon, with 6.30% coverage at +-1 sigma against a calibrated
  68.3%. Better than the released reference checkpoint, and still not an interval;
- it is input-dependent, CoV 0.379-0.395 across a batch.

**The pre-registered rule governing this replication returned DOES NOT GENERALISE**, on its
second condition: the paired difference against the index excludes zero at 1
of 4 horizons, not a majority. The direction replicated everywhere; the
separation did not, on the four independent trajectories our held-out arena has. Treat the
ranking property as supported on these checkpoints and established only on the released
reference one.

## Checkpoints

### `autoregressive-10k-seed0`

Autoregressive training — the arm the base paper's claim is about. Seed 0 of three at 10,000 iterations; scores 0.3894 normalised error at a 368-step horizon on held-out episodes (arm mean 0.3582 ± 0.0283 over three seeds).

- source: `runs/armA_seed0_10k/weights_10000.pt`
- size: 5,683,412 bytes
- sha256: `4dbb6871f69e6b7a3e7014fb0ae7effb8366860f6bd0c84af717c10ea64c6625`
- σ calibration, measured at iteration 2,500 (this arm; not re-measured at 10,000): 52× overconfident, coverage 11.67% at ±1σ (h=1)

### `autoregressive-10k-seed1`

Autoregressive training — the arm the base paper's claim is about. Seed 1 of three at 10,000 iterations; scores 0.3509 normalised error at a 368-step horizon on held-out episodes (arm mean 0.3582 ± 0.0283 over three seeds).

- source: `runs/armA_seed1_10k/weights_10000.pt`
- size: 5,683,412 bytes
- sha256: `c88b20a136c7364475e1bf74b3919b33de1ebad9293de521cfe259ed8474ee6e`
- σ calibration, measured at iteration 2,500 (this arm; not re-measured at 10,000): 52× overconfident, coverage 11.67% at ±1σ (h=1)

### `autoregressive-10k-seed2`

Autoregressive training — the arm the base paper's claim is about. Seed 2 of three at 10,000 iterations; scores 0.3341 normalised error at a 368-step horizon on held-out episodes (arm mean 0.3582 ± 0.0283 over three seeds).

- source: `runs/armA_seed2_10k/weights_10000.pt`
- size: 5,683,412 bytes
- sha256: `d8e3f43edf8a6f76c25e34d814a7a7c4c35779bbb7ec90e76c5f49a9ec2a192c`
- σ calibration, measured at iteration 2,500 (this arm; not re-measured at 10,000): 52× overconfident, coverage 11.67% at ±1σ (h=1)

### `teacher-forced-10k-seed0`

Teacher forcing — the comparison arm. Released so the central claim can be checked rather than taken on trust. Seed 0 of three at 10,000 iterations; scores 1.9710 normalised error at a 368-step horizon on held-out episodes (arm mean 1.6497 ± 0.2858 over three seeds).

- source: `runs/armB_seed0_10k/weights_10000.pt`
- size: 5,683,412 bytes
- sha256: `a8e20cf9ef3f0ed0380ba031559fdd497f9e2a0a3a681ce0de39820b4e66f0c1`
- σ calibration, measured at iteration 2,500 (this arm; not re-measured at 10,000): 315× overconfident, coverage 12.96% at ±1σ (h=1)

### `teacher-forced-10k-seed1`

Teacher forcing — the comparison arm. Released so the central claim can be checked rather than taken on trust. Seed 1 of three at 10,000 iterations; scores 1.5540 normalised error at a 368-step horizon on held-out episodes (arm mean 1.6497 ± 0.2858 over three seeds).

- source: `runs/armB_seed1_10k/weights_10000.pt`
- size: 5,683,412 bytes
- sha256: `b473bd70d5afdcbb1065e7ef49e32e85d4941719ec1bf290e4a91a09b8165754`
- σ calibration, measured at iteration 2,500 (this arm; not re-measured at 10,000): 315× overconfident, coverage 12.96% at ±1σ (h=1)

### `teacher-forced-10k-seed2`

Teacher forcing — the comparison arm. Released so the central claim can be checked rather than taken on trust. Seed 2 of three at 10,000 iterations; scores 1.4241 normalised error at a 368-step horizon on held-out episodes (arm mean 1.6497 ± 0.2858 over three seeds).

- source: `runs/armB_seed2_10k/weights_10000.pt`
- size: 5,683,412 bytes
- sha256: `2431bc1ba09229d305d364abb53d422ef79d39a7299f8c3692f1fb743c8240a2`
- σ calibration, measured at iteration 2,500 (this arm; not re-measured at 10,000): 315× overconfident, coverage 12.96% at ±1σ (h=1)

### `autoregressive-2500`

Arm A at the paper's stated iteration count, for comparison with the released checkpoint.

- source: `runs/armA_seed0/weights_2500.pt`
- size: 5,683,374 bytes
- sha256: `bc4e0dfbcff28b994e3acabbae2d6f1d833331dc5bfad5cc9aa8f410385bd4b0`
- σ calibration, measured at iteration 2,500: 52× overconfident, coverage 11.67% at ±1σ (h=1)

### `corrected-objective-2500`

Trained with the reference's unused `gaussian_nll` branch. This is the CORRECTED-OBJECTIVE artifact, not a calibrated one — see the limitation above.

- source: `runs/armA_seed0_nll/weights_2500.pt`
- size: 5,683,374 bytes
- sha256: `a1a339b27b077712b0a87b4df4718437933db3e6a370b8b08f941fab30129367`
- σ calibration, measured at iteration 2,500: 11× overconfident, coverage 42.78% at ±1σ (h=1)

### `autoregressive-ens5-seed0`

Ensemble size 5. The only checkpoints here with a non-zero epistemic term; the others have exactly zero by construction. See the ensemble-5 block below.

- source: `runs/armA_seed0_ens5/weights_2500.pt`
- size: 8,020,484 bytes
- sha256: `923e3a0b935cff3cb611cf6b35eea83701df4a78f02a22e3f10a6a2e945b9496`
- σ calibration, measured at iteration 2,500: 52× overconfident, coverage 11.67% at ±1σ (h=1)

### `autoregressive-ens5-seed1`

Ensemble size 5, seed 1.

- source: `runs/armA_seed1_ens5/weights_2500.pt`
- size: 8,020,484 bytes
- sha256: `e756ca16fe2cd4e1615ca27b47d9bb519dd0d4da6dfe263758b1d5bbdaabeaaa`
- σ calibration, measured at iteration 2,500: 52× overconfident, coverage 11.67% at ±1σ (h=1)

### `autoregressive-ens5-seed2`

Ensemble size 5, seed 2.

- source: `runs/armA_seed2_ens5/weights_2500.pt`
- size: 8,020,484 bytes
- sha256: `2688b16030a57b4b4201bc844a9e1b3607df8734e7b62b1f7b7efb11ed5d9652`
- σ calibration, measured at iteration 2,500: 52× overconfident, coverage 11.67% at ±1σ (h=1)

## The result these support

Normalised error at a 368-step horizon on held-out episodes, over three training seeds (standard deviation with `ddof=1`):

| arm | seed 0 | seed 1 | seed 2 | mean ± sd |
|---|---|---|---|---|
| autoregressive | 0.3894 | 0.3509 | 0.3341 | **0.3582 ± 0.0283** |
| teacher forcing | 1.9710 | 1.5540 | 1.4241 | **1.6497 ± 0.2858** |

Autoregressive training is better by a factor of **4.61×**. For reference the hold-last floor — predicting that nothing changes — scores 0.9930 in the same cell, so teacher forcing is worse than making no prediction at all.

Every 10,000-iteration checkpoint was cross-checked against the 2,500-iteration run at the same seed: 90,000 logged values compared, 0 differing.

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
