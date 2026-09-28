# Baseline specifications — the MLP, RSSM and transformer of rules M-75 and M-76

Written by S2b on 2026-09-28, before any baseline run. The code is `src/baselines/`; training
is `scripts/train_baseline.py`; the verification ladder is `scripts/baseline_verification.py`
(results in `results/baseline_verification.json`); the sources for the RSSM's settings are
verified in `results/baseline_citations_verified.json` (`scripts/baseline_citations.py`).

**Status vocabulary.** *match*: as the cited source states it. *deviation*: the source says
otherwise, or says nothing and we chose; the reason is given. *UNVERIFIED*: a claim not
checked against its source. **There are no UNVERIFIED rows** (PLAN §1.2.5: any would block the
runs). Rules M-75 and M-76 govern wherever they pin a choice.

## 1. The comparison is state-only (PLAN S2b step 1)

RWM's state prediction does not depend on its auxiliary (contact, termination) branch, so a
baseline with no auxiliary heads is compared like with like:

- The two branches are separate modules with disjoint parameters. `state_base` and
  `state_heads` are at `src/rwm_model.py:164-165`; `auxiliary_base` and `auxiliary_heads` are at
  `:168-169`. The upstream builds them the same way (`system_dynamics.py:34-54` at 18eebcdd).
- The state mean comes from `state_base` and the state heads alone (`src/rwm_model.py:182`,
  upstream `system_dynamics.py:87`). The auxiliary branch is computed separately
  (`src/rwm_model.py:191`, upstream `:97`), and its outputs are returned beside the state and
  never enter it.
- Rollout keeps only the state mean (`m, *_ = self.forward(...)`, `src/rwm_model.py:248`).
- Training does not couple them either:
  - the state loss reads only `state_base` and a state head (`src/rwm_model.py:317`);
  - the auxiliary loss reads only `auxiliary_base` (`:356`);
  - Adam updates each parameter from its own gradient;
  - the auxiliary loss draws no random numbers (the only `randn_like` calls are in the state
    loss, `:264`, `:329`), so it cannot even shift the state loss's random stream.

## 2. Parameter counts (from the ladder)

RWM's ensemble-1 state pathway has **714,164** parameters, recounted by the ladder with
`scripts/p2_capacity_power.py`'s function.

| Baseline | Table S7 (governs) | Ratio to RWM | Parameter-matched (reported only) | Ratio |
|---|---:|---:|---:|---:|
| MLP | 610,484 | 0.855 | width 295 | 0.999 |
| transformer | 132,148 | 0.185 | d_model 160, learned positions | 0.961 |
| RSSM | 3,180,468 | 4.453 | Gaussian, width 256, 1 GRU layer | 1.023 |

## 3. Deviations table

| # | Item | Choice | Status | Citation or reason |
|---|---|---|---|---|
| 1 | Input per time row | normalised state (45) and unnormalised action (12) | match | RWM's own input (`src/rwm_model.py:52-53`; C-07) |
| 2 | History M | 32 rows for every baseline | match | "same context" as RWM (ORIGINAL_SPECS b.5); Table S7's transformer context 32 |
| 3 | Training windows | 40-row windows, seed-0 split, 7,687 of them | deviation | the original states none (b.7). Arm A's, pinned by M-75/M-76 and PLAN Appendix C |
| 4 | Teacher-forced regime (M-75) | each of the window's 8 targets predicted from true inputs, as Arm B; the RSSM uses its own objective | deviation | the original trains baselines by teacher forcing (b.4) and defines it as N = 1 (a.6). The window and target count are pinned by M-75 |
| 5 | Autoregressive regime (M-76) | own reparameterised sample fed back, as Arm A | match | the upstream MLP path (`system_dynamics.py:216-224`). For the other two it is pinned by M-76 |
| 6 | State head | RWM's `MLPStateHead`: residual on the last input state, bounded double-softplus log-σ, mean and log-σ towers [128] | deviation | not stated for baselines. PLAN S2b's interface; the same head as RWM's (Table S7's RWM heads) |
| 7 | Auxiliary heads | none | deviation | PLAN S2b. The comparison is state-only (§1) |
| 8 | Objective | RWM's sampled squared error plus bound loss, config weights 1.0 and 1.0; the RSSM adds its KL (rows 27–28) | deviation | the original states no baseline loss (b.6). The faithful objective of PLAN Appendix C |
| 9 | Optimiser | Adam, learning rate 1e-4, weight decay 1e-5, no clipping | deviation | not stated for baselines (b.7). Arm A's, from the reference config |
| 10 | Batch, iterations, seeds | 256, 2,500, seeds 0–2 | deviation | not stated for baselines (b.7). Arm A's (PLAN Appendix C). The original's RWM batch was 1,024 (Table S9), an existing deviation |
| 11 | Action alignment | state row t paired with action row t + 1, so the newest action for target r is row r | match | RWM's training slicing (`system_dynamics.py:196-200`; D-13, X-05). Asserted by ladder rung 5 in training and rollout |
| 12 | Evaluation rollout | 32 history rows, then autoregressive, mean fed back, `action_offset = 1` | match | RWM's rollout (`src/rwm_model.py:228-250`). The upstream evaluation's offset 0 is the documented defect (§7.2) |
| 13 | Ensemble size | 1 | match | Arm A's ensemble-1 centre (PLAN Appendix C) |
| 14 | MLP base | Linear+ReLU of widths [256, 256] over the flattened 32 × 57 history | match | Table S7 (v1 p. 15); upstream `mlp.py:16-29` and `base_cfg.py:61-63` |
| 15 | MLP rollout | sliding window of the last 32 predicted means | match | upstream `model_training.py:126-132` (the MLP branch), with the causal offset (row 12) |
| 16 | Transformer type and size | decoder, dimension 64, 8 heads, 2 layers, context 32, sinusoidal positions | match | Table S7 (v1 p. 15) |
| 17 | Transformer tokens | one token per row: Linear(57 → 64) of (state, action), plus the position code for its place in the window | deviation | not stated (b.2–b.3). Our choice |
| 18 | Transformer internals | causal mask; pre-norm layers (`norm_first`), final LayerNorm; feed-forward 4 × d; ReLU; dropout 0; prediction from the last token | deviation | not stated. Our choice, the conventional decoder-only block |
| 19 | Sinusoidal code | sine and cosine of geometrically spaced frequencies, base 10,000 | match | "sinusoidal" (Table S7), in its standard form |
| 20 | Transformer rollout | append the prediction, drop the oldest row; context capped at 32 | match | PLAN S2b |
| 21 | RSSM recurrent state | PyTorch GRU, 256 units, 2 layers | match | Table S7 |
| 22 | RSSM GRU normalisation | none | deviation | DreamerV2 uses a layer-normalised GRU (p. 18); Table S7 says only "GRU" |
| 23 | RSSM latent | categorical, **64 variables × 32 classes** | deviation | Table S7's "latent dimension 64, categories 32" is ambiguous (ORIGINAL_SPECS b.3). We read it in DreamerV2's own naming, where "discrete latent dimensions 32, classes 32" (Table, p. 19) means 32 variables of 32 classes |
| 24 | Categorical sampling | straight-through gradients | match | DreamerV2 (p. 18) |
| 25 | RSSM activations | ELU | match | DreamerV2, all components (p. 4) |
| 26 | RSSM MLP widths | encoder, input, prior and posterior layers of 256 | deviation | not stated. Table S7's 256 reused |
| 27 | KL balancing, free nats | α = 0.8; no free nats | match | DreamerV2 (Table p. 19; balancing is used instead of free nats, p. 18) |
| 28 | KL scale | 0.1 | match | DreamerV2 β = 0.1 (Table p. 19); the upstream config's own `kl` weight is also 0.1 (`base_cfg.py`) |
| 29 | RSSM decoder | RWM's state head on [h_t, z_t], residual on the previous state | deviation | DreamerV2 decodes images. PLAN S2b's interface |
| 30 | RSSM objectives | tf: posterior filters all 40 rows, reconstruction of rows 1–39 plus KL on every row. ar: posterior filters 32 rows (KL), then the prior runs open-loop over 8 with own samples fed back (sampled squared error) | deviation | pinned by M-75 and M-76. Row 0 has no previous state and so no reconstruction |
| 31 | RSSM rollout | posterior mode over the history, prior mode over the forecast, mean fed back | deviation | our choice: the deterministic analogue of RWM's mean feedback |
| 32 | RSSM initial state | h = 0, z = 0 | deviation | our choice |
| 33 | Matched MLP | width 295 | deviation | PLAN S2b: within ±5% of 714,164 |
| 34 | Matched transformer | d_model 160, learned positions, otherwise row 18 | deviation | PLAN S2b (learned positions; ±5%) |
| 35 | Matched RSSM latent | 30-dimensional diagonal Gaussian | match | PlaNet (p. 12) |
| 36 | Matched RSSM settings | ReLU; 3 free nats; no KL scaling (weight 1.0); no balancing | match | PlaNet (p. 12). Balancing did not exist before DreamerV2 |
| 37 | Matched RSSM size | 1 GRU layer, width 256 | deviation | parameter-matched (PLAN S2b) |
| 38 | Matched RSSM std | softplus + 0.1 | deviation | not stated in PlaNet's paper. Our choice |

## 4. Sources

DreamerV2 (Hafner, Lillicrap, Norouzi, Ba; ICLR 2021; arXiv 2010.02193) and PlaNet (Hafner et
al.; ICML 2019; arXiv 1811.04551) were verified as `scripts/t1_bibliography.py` verifies the
paper's references. The title and full author list were checked against the arXiv API, and every
value used above was located on its stated page. They are **not yet** in `t1_bibliography.ENTRIES`,
because that list is the paper's reference list; S9 adds them when §5.3 cites them.
