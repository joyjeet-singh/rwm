# Round 5 — crosswalk from the v1 text we read to the current versions (G1)

Source: `results/version_crosswalk.json`, written by `scripts/version_crosswalk.py` (25 claims; every fragment
asserted present in the local text of the version it is attributed to). It covers all 12 rows of Appendix D, every
passage the paper quotes from either original, and the statements the review raised about RWM-U's variance, shared
trunk, rollout and "propagated" claim. It needs the network (`--fetch`) and the gitignored downloads, so it is
not a `reproduce.sh` stage. RWM = arXiv 2501.10100 (v1 17 Jan 2025 … v5 14 Dec 2025); RWM-U = arXiv 2504.16680
(v1 23 Apr 2025, v2 7 Jan 2026, v3 8 Jan 2026). Labels: **no 12, moved 7, reworded 3, new 3, removed 0.**

**Workshop versions: not compared.** The two OpenReview forums (`u76d3gBWCX`, `mcwLgO93ym`) answered with a
browser challenge (HTTP 403) and were not bypassed. No workshop text was read, so "where the workshop version
differs" is unknown for every claim, not "no difference". The venue pages (read through a summarising tool) list
both papers as workshop posters; see `PREMISES.md` P6.

## What changed that matters

**RWM-U (the follow-up).** The rollout is not changed. Eq. 4 (`o′ = E_b[μ_b]`, `u = Var_b[μ_b]`), "the ensemble
mean is used as the predicted next observation", the shared recurrent feature extractor and the sentence "The
learned variance component captures aleatoric uncertainty effectively" are word-for-word the same in v1, v2 and
v3 (`rwmu_mean_fed_forward`, `rwmu_shared_trunk`, `rwmu_variance_effective`: `no`). What v2 *added* is a claim:
the abstract, §4.1's closing paragraph and the conclusion say uncertainty is "effectively propagated over long
horizons" (`rwmu_propagated`: `new`; first in v2), and the figure caption now says the estimate "aligns with the
long-horizon prediction error" (`rwmu_epistemic_aligns`: `new`). So the review's worry — "if v3 changed the rollout
instead, your pinned code isn't the method of record" — does not arise from the paper's text: the method is
described identically; only the claim made for it grew. **A test of the "propagated" claim must score the
propagated spread against accumulated error** (the review's TS∞ check, X9), because the paper offers no
evidence for it beyond the figure v1 already had (v1 Fig. 2 right; v3 Fig. 3 right). The title and name changed
(`rwmu_title_name`: `reworded`, RWM-O → RWM-U, the model unchanged) and the real-robot abstract sentence was
rewritten (`rwmu_real_robots`: `reworded`). The trust-metric and aleatoric-low sentences, and "closely follows the
trend of the prediction error", are unchanged (`no`) and sit in §5.1 in both versions.

**RWM (the base paper).** The tested claims are unchanged where they stand: AR beats TF, the lowest errors
across all environments, SHAC and Dreamer failing, "generalization and robustness" (`no`). Two moved from the
main text into Appendix A.4.1 at v2 — "poor autoregressive performance" and "an optimal trade-off emerges"
(`rwm_tf_poor`, `rwm_mn_optimal`: `moved`; v1 IV-C → v2+ A.4.1). Zero-shot hardware transfer gained a second robot
in v4 (`rwm_zero_shot`: `reworded`; "ANYmal D and Unitree G1").

**A premise of our own Appendix D is wrong.** The "~6M against ~250M state transitions" table is **not in v1.**
It is Table 1 in §5 Limitations from v2 on (`rwm_sample_efficiency`: `new`, first in v2). v1's Limitations section is
prose only. `results/original_paper_figures.json` (`sample_efficiency.where_v1`), `PAPER.template.md:1243` and
`:1779` call it v1's "Table I". The numbers and what the paper does with them (not tested) are unaffected;
the citation needs to name v2+. It was found by this session's own check, which is why the crosswalk records
absence from v1 as an assertion (`v1: null`).

**Training tables** moved with the revisions (RWM: v1 Table S9 → v2+ Table S10; RWM-U: v1 Table S8 → v3 Table S10)
and their values did not: forecast decay α = 1.0, 2,500 iterations, learning rate 1e−4, in both papers and every
version (`rwm_table_*`, `rwmu_table_*`: `moved` = renumbered). In RWM Eq. 2, "α denotes a decay factor" is in all five
versions, so the paper *names* a decay factor and *sets it to no decay*. Appendix H's C-09 therefore records a
word, not a gap between paper and code (`PREMISES.md` P14–P15).

## What a test must now say

| Claim | Test must now say |
|---|---|
| "uncertainty effectively propagated over long horizons" (RWM-U v2+) | Test against the published text of v2/v3, not v1: v1 never says it. Score the spread of a per-member rollout against accumulated error (X9); report the one-step spread separately. |
| the 6M/250M table | Cite RWM v2 or later (Table 1, §5 Limitations); say v1 lacks it. |
| the trust-metric figure | Cite Fig. 2 (right) in v1 and Fig. 3 (right) in v3; the claim is unchanged. |
| the learned variance "captures aleatoric uncertainty effectively" | Quote it (v1 §4.1; unchanged in v2, v3). §6.3 refutes it; §6.1 should say the follow-up claims it. |

## §code — the upstream repositories since the pins

Cloned read-only on 2026-10-19 into `/Users/Shared/rwm_verify/upstream_latest/`; neither pinned copy under
`PDM/` was touched, and `diff -r` shows the clones equal the pinned copies apart from `__pycache__`.
`git ls-remote` agrees with the clones.

| Repository | Pin | Remote HEAD | Commits since the pin |
|---|---|---|---|
| `robotic_world_model_lite` (master) | `13a798e9` (2026-04-08) | `13a798e9` | **0** |
| `rsl_rl_rwm` (main) | `18eebcdd` (2026-01-10) | `18eebcdd` | **0** |

So there is no diff of the rollout, ensemble, loss or data code to report, and **the pinned code is the current
code.** The review's "if v3 changed the rollout" is moot for the code too (v3 is 8 Jan 2026; `rsl_rl_rwm`'s
"init uncertainty-aware robotic world model" commit is 10 Jan 2026 and is the pin). Three facts from reading
the code that the paper does not state (details and line numbers in `PREMISES.md` P12 and B2):

1. **Per-head bootstrap resampling exists.** `rsl_rl_rwm/rsl_rl/modules/system_dynamics.py:129-140` gives each
   head its own with-replacement resample of the batch when `bootstrap=True`; `mbpo_ppo.py:213` sets it in the
   MBPO-PPO model update. The offline pipeline (`robotic_world_model_lite/scripts/model_training.py:68,159`) does
   not, so there the heads see identical batches. "Bootstrap" is a paper-code gap for the offline path only.
2. **The imagination rollout picks one member per environment** (`scripts/envs/base.py:54,68,142`;
   `system_dynamics.py:116-121`), unlike Eq. 4's mean, which is what the evaluation path (`model_ids=None`) does
   and what our §6.4 and X9's baseline describe.
3. **Adam with default betas** in every training path (`PREMISES.md` P30).

Which path trained the released checkpoint is not recorded anywhere in the repositories.
