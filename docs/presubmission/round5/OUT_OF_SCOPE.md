# Out of scope (logged, not fixed)

One line each, with file:line. Do not fix in round 5.

- `PDM/CLAUDE.md` (Style section): says "five retractions", while the ledger's counts differ. The user's file; not this round's to fix. (Seeded by G0.)
- `results/original_paper_figures.json` (`sample_efficiency.where_v1`), `PAPER.template.md:1243` and `:1779`: the 6M-against-250M table is cited as v1's "Table I (Limitations)"; v1 has no such table, it is Table 1 in v2+ (`results/version_crosswalk.json`, `rwm_sample_efficiency`). Fix the generator's citation. (G1; owner G12 or G15.)
- `PAPER.template.md:689` and `:1563-1568` (§6.4): "feeds the ensemble **mean** back" is true of the evaluation path only; the released imagination env (`scripts/envs/base.py:54,68,142`) feeds one random member per environment. State both. (G1; owner G13; X9's design in G2.)
- `PAPER.template.md:1397` (App. H, C-09): "though the paper describes a decay"; both originals set α = 1.0 (no decay), so this is a naming difference, not a gap. (G1; owner G15.)
- `PAPER.template.md:1401` (App. H): "Table S9" for the training length does not say which paper; right for RWM v1, wrong for RWM-U v1 (S8) and v3 (S10). (G1; owner G15.)
- `PAPER.template.md:2353` and `:689`: "heads differ only in initialisation" omits that `rsl_rl_rwm`'s MBPO-PPO update resamples the batch per head (`system_dynamics.py:129-140`, `mbpo_ppo.py:213`); true of the offline path. (G1; owner G13/G15.)
- `scripts/insample_framing.py:37`: "the released ckpt trained on all ten" is an assumption; no record in either repository says which rows the checkpoint trained on. (G1; owner G3 for X10, G13/G14 for the wording.)
- `docs/APPENDIX_G_VARIANCE_ARITHMETIC.template.md:70-72` (and its generated copy): the first author is referred to as "He"/"his"/"he"; the author's pronouns are not stated in the record, so the neutral "they" is safer. (G2; owner G9 or G15, whichever moves this text.)
- `docs/presubmission/FILE_MAP.md`: no row yet for `round5/PROTOCOLS.md` (G2 added only the protocols file). (G2; owner G6 or G17.)
- `scripts/step5_train.py:334-335,384` (`-14.4629`), `scripts/step6_analyse.py:38`, `scripts/step6_3_min_logstd.py:32`, `scripts/task1_calibration.py:189-194`, `scripts/task5_analyse.py:146-150`: the checkpoint's `log_delta_logstd` is typed as −14.4629; the checkpoint holds −14.463197 (`results/n13_adam.json` `ckpt_log_delta`). Off by 3.0e-4 (0.002%), so every "iterations implied" figure is off by the same fraction. A typed derived number (CLAUDE.md rule 4). (G4; owner G13 or G15, through the generators.)
