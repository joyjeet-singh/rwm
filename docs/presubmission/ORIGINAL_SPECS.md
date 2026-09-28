# Original specifications — the M/N claim and the architecture baselines

Written by S1 on 2026-09-28 from the original paper, arXiv 2501.10100: v1 (17 Jan 2025,
Roman-numeral sections, the numbering the paper cites) and v2 (23 Apr 2025, which renumbers to
Arabic and moves §IV-C to Appendix A.4.1). Local copies (PDF and HTML) are in `sources/`, which is
git-ignored; `verify_original_specs.py` downloads them if absent.

**How the original is cited here.** The paper is under arXiv's non-exclusive licence, not a
Creative Commons one, so this file does not reproduce its sentences. Each item gives the version,
section, PDF page, figure or table, and the **anchor**: the ID of a supporting sentence, whose
position and 16-hex-digit fingerprint are listed in `verify_original_specs.py`. Running that
script confirms all 31 anchors and the figure image (31 of 31 at S1). Numbers the original prints
in a table or inside figure cells are facts and are recorded as printed. **Nothing here is read off
a plot axis.**

---

## (a) §IV-C, the history and forecast horizons (v1 p. 7; v2 Appendix A.4.1, pp. 17–18)

| Item | What the original states | Where | Anchor |
|---|---|---|---|
| a.1 Configurations evaluated | A 5 × 5 grid: M ∈ {1, 2, 8, 16, 32} × N ∈ {1, 2, 8, 16, 32}, 25 configurations. **Not stated in the text.** The grid is given only by Fig. 6's categorical tick labels, and every cell prints its value (a.5), so no value is read off an axis. | v1 Fig. 6, p. 7; v2 Fig. S8, p. 18 (the same image file in both renderings, SHA-256 `20b746abe09a811b…`) | a1, a1v2 |
| a.2 Metric behind "optimal" | The relative autoregressive prediction error e, shown per (M, N) in the left heatmap. **Its formula is not stated anywhere in the paper.** Our reading is the upstream's relative-L1 (`src/rollout_eval.py:139`), as §3.1 of our paper already states. | v1 §IV-C, p. 7 | a2 |
| a.3 Horizon behind "optimal" | **Not stated.** Neither the text nor the caption says over how many steps e is computed. So, as the plan directs, h = 368 governs and h = 100 is reported, matching M-23. | — | — |
| a.4 The claim | That moderate M and N give an **optimal trade-off between prediction accuracy and training efficiency**, with (M, N) = (32, 8) offered as an instance that achieves strong autoregressive performance at a manageable training time. The same sentences appear in v2. **The claim is a trade-off, not "lowest error"**: the text also says that extending either horizon improves accuracy (a.5). The accuracy half is testable on CPU; the training-time half is not the same quantity on a CPU, and rule M-74 reports it without governing. | v1 §IV-C, p. 7; v2 A.4.1, p. 17 | a4, a4b, a4v2, a4bv2 |
| a.5 The directional claims, and the printed values | Longer M lowers the error; the gain in M plateaus beyond some point; longer N improves long-horizon accuracy at a cost in training time; extending both improves accuracy. **Printed e (left heatmap), the centre's row and column:** N = 8: M = 1 → 10.58, 2 → 4.57, 8 → 0.54, 16 → 0.50, **32 → 0.47**. M = 32: N = 1 → 3.99, 2 → 1.91, **8 → 0.47**, 16 → 0.53, 32 → 0.47. **(32, 8) is tied lowest with (32, 32)** among the printed values, and the printed N sequence at M = 32 is not monotone (16 prints above 8). **Printed training hours (right heatmap), M = 32:** N = 1 → 0.62, 2 → 1.05, 8 → 1.07, 16 → 1.58, 32 → 2.27. | v1 §IV-C and Fig. 6, p. 7 | a5M, a5P, a5N, a5B, a5Bv2 |
| a.6 How N = 1 is defined | Teacher forcing *is* the special case of autoregressive training with forecast horizon N = 1, which parallelises training. §IV-C adds that N = 1 trains fastest and predicts poorly. The heatmap's N = 1 row is therefore the teacher-forced configuration. | v1 §III-B, p. 4, and Fig. 1 caption; v1 §IV-C, p. 7 | a6, a6f, a6t, a6p |
| a.7 How training windows are built | By sliding a window of size M + N over the collected trajectories. So N = 1 means (M + 1)-row windows with one target each. | v1 §III-B, p. 4 | a7 |
| a.8 Training budget and objective | **The ablation's own budget is not stated.** The general RWM settings (Table S9, v1 p. 15; Table S10, v2 p. 18) are 2,500 iterations, batch 1,024, learning rate 1e-4, weight decay 1e-5, forecast decay α = 1.0, about 1 training hour, and 5 seeds. The loss is Eq. 2 (v1 §III-B, p. 4): the mean over the N forecast steps of α^k-weighted observation and privileged-information losses. The right heatmap's 1.07 h at (32, 8) matches Table S9's "about 1 h", but that the ablation used the same iterations or seeds is **not stated**. | v1 Table S9, p. 15; Eq. 2, p. 4 | a8T, a8L |
| a.9 Evaluation data for the ablation | **Not stated.** §IV-A evaluates on ANYmal D hardware trajectories; the ablation does not say what it scores. | — | — |
| a.10 Seeds, intervals, significance for the ablation | **Not stated.** The heatmap prints one value per cell, with no spread. | — | — |

## (b) §IV-D, the baselines (v1 pp. 7–8 and Table S7, p. 15; v2 §4.3, pp. 7–8, Table S8, p. 17)

| Item | What the original states | Where | Anchor |
|---|---|---|---|
| b.1 Which baselines | MLP, a recurrent state-space model (RSSM), and transformer-based architectures, plus RWM trained by teacher forcing (RWM-TF) alongside RWM-AR. | v1 §IV-D, p. 7 | b1 |
| b.2 Architecture | **Table S7 (v1 p. 15) = Table S8 (v2 p. 17):** MLP hidden shape 256, 256 with ReLU. RSSM of type GRU, hidden size 256, 2 layers, latent dimension 64, **categorical** prior, 32 categories. Transformer of type **decoder**, dimension 64, 8 heads, 2 layers, context length 32, **sinusoidal** positional encoding. The text says training parameters are "detailed in" A-B2, but A-B2 holds this table only. | v1 Table S7, p. 15 | b2, b5 |
| b.3 Size (parameter count) | **Not stated.** Only the shapes in b.2 are given. Whether "latent dimension 64 … 32 categories" means 64 variables of 32 classes each, or a 64-dimensional latent built from 32-way categoricals, is **ambiguous**. | — | — |
| b.4 Training regime | **Teacher forcing**: the baselines are trained with teacher forcing, as such models traditionally are. By a.6, that is N = 1. The original adds two qualitative statements: an autoregressively trained RSSM performs **comparably** to RWM, and autoregressive training of the transformer does not scale on GPU memory. Neither comes with a figure. | v1 §IV-D, p. 8; v2 §4.3, p. 8 | b3, b3v2, b9, b10 |
| b.5 History M; forecast N | All models get the **same context** during training and evaluation, which Table S7's transformer context of 32 fits. The baselines' M is therefore 32 by inference; **it is not stated as a number**. N is 1 by b.4. | v1 §IV-D, p. 7 | b4 |
| b.6 Loss | **Not stated** for any baseline. | — | — |
| b.7 Iterations, batch, optimiser, seeds | **Not stated** for any baseline. | — | — |
| b.8 Metric | The relative autoregressive prediction error e (as a.2), plotted per environment in Fig. 7. **The horizon is not stated.** | v1 §IV-D and Fig. 7, pp. 7–8 | b6 |
| b.9 Environments | Manipulation, quadruped and humanoid locomotion tasks. The individual environments appear only as figure labels. **Ours is one: ANYmal D, flat terrain.** | v1 §IV-D, p. 7 | b7 |
| b.10 The claim | RWM-AR achieves the lowest prediction error in every environment, and the gap is largest in dynamic tasks such as legged velocity tracking. **No number is given in text, caption or table.** | v1 §IV-D, p. 8 | b8 |
| b.11 A separate MLP comparison | §IV-B's noise experiment (Fig. 5) uses an MLP trained **autoregressively** with the same history and forecast horizon as RWM. It is distinct from §IV-D's teacher-forced baselines. | v1 §IV-B, p. 6 | b11 |

## (c) Not stated, in one list

a.3 the horizon behind e · a.2 the formula for e · a.1 the grid, stated in the text · a.8 the ablation's own budget · a.9 the ablation's evaluation data · a.10 its seeds or intervals · b.3 the baselines' parameter counts · b.5 the baselines' M as a number · b.6 their loss · b.7 their iterations, batch, optimiser and seeds · b.8 the horizon behind Fig. 7.

---

## 2. Arm B check — is the existing Arm B the original's (M = 32, N = 1)?

**No.** Arm B is (M = 32, N = 8) trained with teacher forcing. The original's (32, 1) is a different configuration, so rule M-74 runs (32, 1) as its own arm (PLAN Appendix C, priority 6: "reuse Arm B instead if S1 finds it identical").

- **Window.** Arm B trains on 40-row windows: `scripts/step5_train.py:184` builds `WindowDataset` with its default `window=WINDOW` (`src/rwm_train.py:28-29`), and `WINDOW = 40` (`src/rwm_train.py:23`). The original's N = 1 uses windows of M + N = 33 rows (a.7).
- **Targets per window.** `src/rwm_model.py:306-307` sets `H = history_horizon` (32) and `forecast_horizon = window − H`, which is 8. The loop at `:311` predicts **eight targets per window** (`:312`); the original's N = 1 predicts one.
- **Context of each target.** With `teacher_forcing` (`scripts/step5_train.py:138`, passed at `:207-208`), each step after the first feeds the true next state as a single row (`src/rwm_model.py:324-326`). The GRU carries its hidden state across calls (`Memory.forward`, `src/rwm_model.py:37-39`, reset only per batch at `scripts/step5_train.py:205`). So targets 2–8 are conditioned on **33–39 true rows**, not 32.
- **Loss weighting.** The state loss is the mean over the eight steps (`src/rwm_model.py:332-333`); at N = 1 it is the single step.
- **Training windows.** On the seed-0 split (training episodes 0, 2–7, 9), 40-row windows give **7,687** and 33-row windows give **7,743**, counted with `src/rwm_data.py:265` `valid_window_starts`.
- **At N = 1, teacher forcing and autoregression coincide.** The loop runs once, so `teacher_forcing` has no effect; (32, 1) is a single well-defined arm.

## 3. What this changes in the plan's drafts (decided by the user, 2026-09-28)

`DECISIONS_FOR_USER.md#S1-original-vs-plan` records the three questions and the answers verbatim.

1. **Rule MN's claim.** The draft tests whether (32, 8) is optimal, meaning lowest error. The original claims a trade-off (a.4). But its own printed values put (32, 8) at the tied lowest error (a.5), so testing the accuracy half is fair. M-74 states that it tests only that half, and reports training time alongside.
2. **Rule MN's grid** moves entirely onto the original's grid (answer 3): the eight one-factor neighbours of (32, 8). (64, 8) and (32, 4) were never tested by the original and are dropped. The longest history is then 32, so the common forecast windows are exactly §5's held-out arena.
3. **Rule BASE** splits in two (answer 1): teacher-forced baselines, as the original trains them (b.4), and autoregressive baselines, as PLAN S2b wrote them. Table S7 architectures govern both (answer 2). PLAN S2b's Gaussian-latent, parameter-matched variants run only if they fit the compute cap, and are reported, not governing. PLAN S2b's specifics (a Gaussian RSSM with PlaNet settings, learned positions) conflict with b.2 wherever b.2 states something.
