"""S1 -- write the three pre-registered rules into FINDINGS_LEDGER.md.

Every number in the rule texts that comes from a measurement is READ from
results/p5_sweep_power.json or results/p6_baseline_power.json here, never typed. The
only numerals typed are the original's printed values (ORIGINAL_SPECS a.5, cited there),
configuration labels, horizons, seeds and iteration counts, which are design, not data.

The ledger is appended to, never edited: the script asserts that M-74, M-75 and M-76 do
not exist yet, that the ledger's last M- entry is M-73, and that RESULTS.md's M- count
still reads 73, and only then writes. It updates that one count cell, which
scripts/ledger_check.py requires to match the ledger.

    python docs/presubmission/s1_write_rules.py
"""
import json
import os
import re
import shutil
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
LEDGER = os.path.join(ROOT, "FINDINGS_LEDGER.md")
RESULTS_MD = os.path.join(ROOT, "RESULTS.md")
P5 = json.load(open(os.path.join(ROOT, "results", "p5_sweep_power.json")))
P6 = json.load(open(os.path.join(ROOT, "results", "p6_baseline_power.json")))


def pct(x):
    return f"{x:.1f}%"


def lv(x):
    return f"{x:.5f}"


def pv(x):
    return "p = 0" if x == 0 else f"p = {x:.4f}"


# ------------------------------------------------------------- values read, not typed
e5 = P5["estimates"]
m5 = P5["m"]
holm5 = P5["holm_levels"]
t34_5 = P5["three_of_four_rejectable_at_holm_step"]
minp = P5["min_p_by_sign_pattern"]
p34 = minp["3 of 4 share a sign"]
p24 = minp["2 of 4 share a sign"]
grid = P5["grid_priority_order"]
assert [tuple(g) for g in grid] == [(32, 32), (16, 8), (32, 16), (8, 8), (32, 2), (32, 1),
                                    (2, 8), (1, 8)], grid
assert P5["anchor_horizon"] == 368 and P5["reported_horizon"] == 100
assert P5["traj_start_row"] == [999, 1399, 7999, 8399] and P5["n_independent"] == 4


def mde5(key):
    e = e5[key]
    return pct(e["binding_mde_pct_of_centre"]), e["binding_from"]


r6 = P6["rules"]
m6 = P6["m"]
holm6 = P6["holm_levels"]
t34_6 = P6["three_of_four_rejectable_at_holm_step"]
assert P6["traj_start_row"] == P5["traj_start_row"]


def mde6(rid, key):
    e = r6[rid]["estimates"][key]
    return pct(e["binding_mde_pct_of_centre"]), e["binding_from"]


def contrast(rid, key, slug):
    c = r6[rid]["estimates"][key]["observed_real_contrast"][slug]
    return c["n_positive"], c["p_exact"], c["mean"]


cfg_list = ", ".join(f"({a}, {b})" for a, b in grid)
M74_L1_368, M74_FROM_368 = mde5("l1_h368")
M74_L1_100, M74_FROM_100 = mde5("l1_h100")
M74_NR_368, _ = mde5("nrmse_h368")
M74_NR_100, _ = mde5("nrmse_h100")
M74_EX_STEPS = ", ".join(f"step {x['step']}: {x['delta80_pct']:.1f}%"
                         for x in e5["l1_h368"]["exact_mde_by_holm_step"])
M75_L1_368, M75_FROM_368 = mde6("M-75", "l1_h368")
M75_L1_100, M75_FROM_100 = mde6("M-75", "l1_h100")
M76_L1_368, M76_FROM_368 = mde6("M-76", "l1_h368")
M76_L1_100, M76_FROM_100 = mde6("M-76", "l1_h100")
B_POS, B_P, B_MEAN = contrast("M-75", "l1_h368", "armB_teacher_forced")
N_POS, N_P, N_MEAN = contrast("M-76", "l1_h368", "armA_corrected_nll")
E_POS, E_P, E_MEAN = contrast("M-76", "l1_h368", "armA_ens5")

SHARED_TEST = f"""**The test, stated exactly.** At `n_independent = 4` the cluster bootstrap over whole
trajectories has exactly `4**4 = 256` equally likely ordered resamples, so it is **evaluated
exactly**, with no Monte Carlo draw and no generator seed: for each resample the statistic is
recomputed as the mean of the resampled per-trajectory differences, seeds pooled inside the draw
and never resampled (M-27). The two-sided p-value is `p = min(1, 2 · min(P*(D* ≤ 0),
P*(D* ≥ 0)))` over those 256 values. Holm's step-down procedure at family-wise `α = 0.05`
orders the p-values ascending, breaking exact ties by the priority order of this rule, and
rejects the k-th smallest while `p_(k) ≤ α / (m − k + 1)`, stopping at the first that fails. A
difference **excludes zero in RWM's (or the centre's) favour** when it is rejected and its point
estimate is positive, and **in the other arm's favour** when it is rejected and its point estimate
is negative. "A Holm-adjusted interval excludes zero" means exactly this rejection. The 95%
percentile interval of the 256-point distribution is reported beside each difference and governs
nothing.

**What n = 4 permits, stated in advance** (`results/p5_sweep_power.json`,
`min_p_by_sign_pattern`). When all four per-trajectory differences share a sign, `p = 0`. When
three of four do, `p ≥ {p34}`: the one draw of the minority trajectory four times always crosses
zero. When two of four do, `p ≥ {p24}`, and that difference can never be rejected."""


M74 = f"""### M-74 — PRE-REGISTERED decision rule for the configuration claim: is (M, N) = (32, 8) optimal? · **NEW**
**Entered before any sweep run exists.** No model has been trained at any configuration in the
grid below, and `results/mn_sweep_eval.json` and `results/mn_sweep_verdict.json` do not exist.
The power artifact this rule quotes, `results/p5_sweep_power.json`, was written first from runs
that already exist, and is committed in the same commit as this text, whose subject begins
`PRE-REGISTER`. The script that computes the verdict, `scripts/verdict_mn_sweep.py`, is committed
before the first sweep run starts (PLAN S2a). The ordering can be checked from `git log`, as it can
for M-16, M-23 and M-44.

**The claim, as the original makes it.** 2501.10100v1 §IV-C (p. 7; v2 Appendix A.4.1) reports a
sweep over the history horizon M and the forecast horizon N. It says that moderate values give an
optimal **trade-off between accuracy and training time**, offers (32, 8) as an instance, and adds
that longer M lowers error until it plateaus and that longer N improves long-horizon accuracy
(`docs/presubmission/ORIGINAL_SPECS.md` a.4–a.5, located by fingerprint, not quoted).
The heatmap prints the error e of every cell. On the centre's row and column (M = 32 or N = 8),
it prints 0.47 for the centre and **0.47 for (32, 32)**, 0.50 for (16, 8), 0.53 for (32, 16) and
0.54 for (8, 8), then 1.91 for (32, 2), 3.99 for (32, 1), 4.57 for (2, 8) and 10.58 for (1, 8).
**This rule tests the accuracy half only:** whether the centre's error is the lowest of its
one-factor neighbours at our budget. Training time on two CPU cores is not the quantity the
original timed on a GPU. It is reported beside the verdict (`wall_clock_s` per run) and governs
nothing.

**The arms.** The centre is the existing Arm A: (32, 8), `runs/armA_seed{{0,1,2}}/weights_2500.pt`,
already trained, re-scored here and not re-trained. The grid is the original's own one-factor
neighbours of (32, 8) in its Fig. 6 grid, in this **priority order**: {cfg_list}. That is
`m = {m5}` configurations, each trained for 2,500 iterations with seeds 0, 1 and 2. Every setting
is the centre's except M and N: ensemble size 1, `rnn_hidden_size` 256, batch 256, the
reference configuration's learning rate and weight decay, the faithful sampled-MSE objective, the state
branch fed back its own sample, the causal action alignment, the seed-0 split (episodes 1 and 8
held out), and episode-respecting training windows of M + N rows. At N = 1 the loop runs once, so
"autoregressive" and "teacher-forced" coincide and (32, 1) is one arm. **The existing Arm B is not
(32, 1)**: it trains on 40-row windows with eight teacher-forced targets each
(`docs/presubmission/ORIGINAL_SPECS.md` §2). So (32, 1) is trained here. One factor is varied at
a time, so **no interaction between M and N is tested.**

**If the grid does not fit.** Before any sweep data exists, S2a's timing probe projects the
grid's CPU-hours. If the projection exceeds PLAN Appendix C's 25-hour cap, **whole configurations
are dropped from the bottom of the priority order** until it fits, and the drop is recorded as a
new ledger entry before launch. `m` is then the number of configurations actually run. The MDE
below is quoted at `m = {m5}`, the strictest, and holds conservatively for any smaller `m`. **If any
run fails, this rule cannot be discharged as written**: the discharging session stops and reports,
and no configuration is scored on fewer than three seeds.

**The arena: common forecast windows, identical for every configuration.** Held-out episodes 1
and 8. The four non-overlapping 400-row trajectories of §5 start at rows 999, 1399, 7999 and 8399.
The forecast targets are rows `s + 32 … s + 399`, 368 steps for every configuration. The history
is **the M rows immediately before the first target**, `s + 32 − M … s + 31`. Because the longest
history in the grid is 32, these windows are §5's own trajectories. `n_independent = 4`, asserted,
and the window start rows are stored in the artifact. The rollout is the existing harness's:
autoregressive from the history, hidden state carried, `action_offset = 1`.

**The metric.** **Relative-L1** is primary: the upstream's own metric, computed as
`scripts/head_to_head_accuracy.py` computes it, in config-normalised state. It is the mean over
forecast steps 1…h of the ratio of summed absolute error to summed absolute truth. **nRMSE form 1**
is secondary: `rwm_metrics.nrmse_pooled` per trajectory, with the training-episode scale. Both are
cumulative, at h = 1, 8, 32, 100, 128 and 368. **h = 368 governs.** The original never states the
horizon behind its error e (`ORIGINAL_SPECS.md` a.3), so the rule anchors where M-23 did, and
**h = 100 is reported**.

**The statistic.** For each non-centre configuration c,
`D_c = mean over the 4 trajectories of [ 3-seed mean err_c(traj) − 3-seed mean err_centre(traj) ]`,
in relative-L1 at h = 368.

{SHARED_TEST} Here `m = {m5}` and the Holm levels are {", ".join(lv(x) for x in holm5)}. **So a
three-of-four difference can be rejected only from Holm step {t34_5[0]} onward**, once at least
{t34_5[0] - 1} other configurations have been rejected. Before that, only a difference whose four
trajectories all share a sign is rejected. That is what the plan's draft meant by "essentially only
when all four share a sign", and the exact statement replaces it.

**Minimum detectable effect, estimated before the data** (`results/p5_sweep_power.json`,
`estimates`). The estimate is the larger of two, as a percentage of the centre's error. One is
M-44's formula (`(z + z) × SE` under the same-configuration null of Arm A's seed pairs). The other
is the rule's own exact test, applied to a proportional effect diluted toward zero with Arm A's
seed noise added. The two percentages measure slightly different things. The exact-test figure
is an effect of that size on every trajectory, relative to each trajectory's own centre error. The
formula figure is a mean difference relative to the centre's mean error. Relative-L1: **{M74_L1_368} at h = 368** ({M74_FROM_368}) and **{M74_L1_100} at
h = 100** ({M74_FROM_100}), at Holm step 1. nRMSE: {M74_NR_368} and {M74_NR_100}. By Holm step at
h = 368 (exact test): {M74_EX_STEPS}. The cross-configuration contrast available, Arm B against
Arm A, is enormous and uneven, so it cannot calibrate the MDE. It is used as a check that the exact
test detects a real change of configuration, and it does (the artifact's `observed_real_contrast`).

**What that MDE means for the verdict, stated before the data.** The original's own printed values
put (32, 32) level with the centre and (16, 8), (32, 16) and (8, 8) close to it (above). **If our
sweep reproduced the original's pattern exactly, those four differences would sit near or below this
rule's MDE**, and only (32, 2), (32, 1), (2, 8) and (1, 8) would be reliably resolvable. So
**REPRODUCES, RESOLVED is not the outcome the original's own figure predicts here.** And because
the original prints (32, 32) level with the centre, a true tie there gives a `D_c` point estimate
at or below zero about half the time. The original's own pattern therefore predicts **CONSISTENT
WITH OPTIMAL and CANNOT BE DISTINGUISHED about equally often**, and neither would count against it.
The branch that would count against the claim is NOT OPTIMAL AT OUR BUDGET.

**The rule, decided in advance. Four branches, applied in this order; the first that matches is the
verdict; they are exhaustive and mutually exclusive.** "The centre has the lowest error" means
every `D_c` point estimate is strictly positive.

1. **NOT OPTIMAL AT OUR BUDGET.** Some `D_c` excludes zero in c's favour. **Licenses the paper to
   say** that at our data budget, on this arena, those configurations predict better than (32, 8) at
   h = 368, and to name **every** c for which this holds.
2. **REPRODUCES, RESOLVED.** The centre has the lowest error, and every `D_c` excludes zero in the
   centre's favour. **Licenses the paper to say** that (32, 8) beats every one-factor neighbour
   tested, on this arena.
3. **CONSISTENT WITH OPTIMAL.** The centre has the lowest error and no `D_c` excludes zero in c's
   favour, but not every `D_c` excludes zero in the centre's favour. **Licenses the paper to say**
   that no neighbour beats (32, 8), and to name the neighbours this arena cannot separate from it,
   each with the MDE.
4. **CANNOT BE DISTINGUISHED.** Anything else: some `D_c ≤ 0`, but none excludes zero in c's
   favour. **Licenses the paper to say** only which configurations had lower point estimates, and
   that none is resolvable at the MDE above.

**Reported alongside, never governing:**
- h = 100, all six horizons, and nRMSE, each with the same test;
- the four per-trajectory differences of every configuration;
- the in-sample arena: the eight training episodes, two non-overlapping 400-row windows each,
  `n_independent = 16`. Every configuration saw these episodes, so the comparison is paired and
  fair. It uses a Monte Carlo cluster bootstrap of 20,000 resamples with generator seed 0, as
  `scripts/a1_ab_by_horizon.py:52-53`;
- the per-episode sign of each difference over all ten episodes;
- the training-window count of every configuration;
- `wall_clock_s` of every run;
- the hold-last floor.

**What this rule does not claim.** It says nothing about M above 32 or N above 32, nor about any
interaction between them. It says nothing about the training-time half of the original's
trade-off, or about the original's other robots and terrains. Our data budget is §5.1's, not the
original's, and our batch is 256, not 1,024. A verdict here is about (32, 8) on one robot, one
gait and one terrain, over four held-out trajectories.

**What the discharging session may and may not do.** It computes the verdict with
`scripts/verdict_mn_sweep.py` exactly as committed before the runs. It records the verdict in a
new ledger entry naming this one (PLAN §1.2.3). Whether it also sets this entry's `Status` line,
as every earlier rule's was set and as `scripts/appendix_g_rules.py` reads, it settles under that
section. **It may not change one character of the rule text above.** A result that falls between
branches is a defect in this rule and is reported as one, not resolved by choosing.

**Evidence** `RUN` `results/p5_sweep_power.json` — the power estimate. `SRC` `docs/presubmission/ORIGINAL_SPECS.md` — the claim. Discharged by `results/mn_sweep_verdict.json`, from `scripts/verdict_mn_sweep.py`, neither of which exists yet.
**Status** PRE-REGISTERED, NOT YET DISCHARGED — awaits `results/mn_sweep_verdict.json` · **Relevance** METHOD
"""


def base_rule(rid, regime_title, regime_text, arms_extra, mde368, from368, mde100, from100,
              real_text, predicted, names, licence, not_claim, verdict_file):
    n_rwm, n_base, n_part, n_none = names
    return f"""### {rid} — PRE-REGISTERED decision rule for the architecture claim, baselines {regime_title} · **NEW**
**Entered before any baseline model exists.** No baseline has been implemented, trained or scored,
and `results/baselines_eval.json` and `{verdict_file}` do not exist. The power artifact this rule
quotes, `results/p6_baseline_power.json`, was written first from runs that already exist, and is
committed in the same commit as this text, under a subject beginning `PRE-REGISTER`. The verdict
script, `scripts/verdict_baselines.py`, is committed before any baseline run (PLAN S2b). This rule
and {"M-76" if rid == "M-75" else "M-75"} are the two halves of one question, split by the user's
ruling of 2026-09-28 (`docs/presubmission/DECISIONS_FOR_USER.md#S1-original-vs-plan`).

**The claim, as the original makes it.** 2501.10100v1 §IV-D (pp. 7–8; v2 §4.3) states that RWM
trained autoregressively achieves the lowest autoregressive prediction error in every environment
against MLP, RSSM and transformer baselines, with no number in text, caption or table. It also
states that **those baselines were trained with teacher forcing**, the traditional way, and that an
**autoregressively trained RSSM performs comparably to RWM** (`docs/presubmission/ORIGINAL_SPECS.md`
b.4, b.10). {regime_text}

**The arms.** RWM is the existing Arm A, 2,500 iterations, seeds 0–2,
`runs/armA_seed{{0,1,2}}/weights_2500.pt`: not re-trained. The baselines are an **MLP, an RSSM and a
transformer at the original's Table S7 sizes** (`ORIGINAL_SPECS.md` b.2), in this **priority order**,
which breaks exact ties in the Holm ordering below:
- MLP: 256 × 256, ReLU;
- RSSM: a GRU of 256 units in 2 layers, latent dimension 64, a categorical prior with 32 categories;
- transformer: a decoder with dimension 64, 8 heads, 2 layers, context 32, sinusoidal positions.

Each predicts only the next state, through the same residual connection and bounded log-σ head as
RWM's state pathway, with no auxiliary heads. Each is trained {arms_extra}. Every baseline trains
for 2,500 iterations with seeds 0, 1 and 2, on the same seed-0 split and the same 40-row training
windows as Arm A, with batch 256, Adam at the reference configuration's learning rate and weight
decay, and the causal action alignment. Every implementation choice the original leaves open is fixed in
`docs/presubmission/BASELINE_SPECS.md` before any baseline run, each row marked match, deviation or
UNVERIFIED with a citation. **Any UNVERIFIED row blocks the runs** (PLAN §1.2.5). This rule's
verdict logic depends on none of those choices. **Parameter-matched variants** follow PLAN S2b as
written: a Gaussian-latent RSSM, learned positions, and each baseline within ±5% of RWM's
state-pathway parameter count. They are trained **only if** S2b's timing probe projects every
baseline run, of both specifications and both rules, within PLAN Appendix C's 20 CPU-hour cap. If
trained, they are **reported alongside and never govern**.

**If the arms do not fit, or a run fails.** If S2b's timing probe projects the Table S7 arms of
both rules above the 20 CPU-hour cap, **no baseline is dropped**: S2b stops for the user's decision
(PLAN S2b), before any baseline data exists. If any governing run fails, or diverges and cannot be
trained as specified, this rule cannot be discharged as written. The discharging session stops and
reports, and no baseline is scored on fewer than three seeds.

**The arena, metric and horizons are M-74's.** The four held-out trajectories of §5 (rows 999,
1399, 7999, 8399), 32 history rows each, and 368 forecast steps rolled out autoregressively by
every arm; `n_independent = 4`, asserted. Relative-L1 is primary and nRMSE form 1 secondary, both
cumulative. **h = 368 governs; h = 100 is reported.**

**The statistic.** For each baseline b,
`D_b = mean over the 4 trajectories of [ 3-seed mean err_b(traj) − 3-seed mean err_RWM(traj) ]`,
relative-L1, h = 368.

{SHARED_TEST} Here `m = {m6}`, one family of three baselines for this rule alone, and the Holm levels
are {", ".join(lv(x) for x in holm6)}. **Every level is at least {p34}, so a three-of-four
difference can be rejected at every Holm step** ({", ".join(str(x) for x in t34_6)}).

**Minimum detectable effect, estimated before the data** (`results/p6_baseline_power.json`,
`rules.{rid}`), by the same two estimates as M-74: **{mde368} of RWM's error at h = 368**
({from368}) and **{mde100} at h = 100** ({from100}), at Holm step 1, relative-L1. The noise model is
Arm A's seed noise. **A baseline whose seed-to-seed spread is larger makes the MDE a lower bound for
it.** {real_text}

**What that means for the verdict, stated before the data.** {predicted}

**The rule, decided in advance.** Each baseline gets one of three results. **RWM BETTER**: `D_b`
excludes zero in RWM's favour. **BASELINE BETTER**: `D_b` excludes zero in the baseline's favour.
**CANNOT BE SETTLED**: anything else, reported with the MDE. The overall verdict is the first of
these four branches that matches; they are exhaustive and mutually exclusive:

1. **{n_base}** — any baseline is BASELINE BETTER.
2. **{n_rwm}** — all three are RWM BETTER.
3. **{n_part}** — at least one is RWM BETTER, and the rest are CANNOT BE SETTLED.
4. **{n_none}** — none resolves.

{licence}

**Reported alongside, never governing:**
- h = 100, all six horizons, and nRMSE, each with the same test;
- the four per-trajectory differences of every baseline;
- the hold-last floor;
- the in-sample arena (`n_independent = 16`, Monte Carlo cluster bootstrap of 20,000 resamples,
  generator seed 0);
- the per-episode sign of each difference over all ten episodes;
- `wall_clock_s` of every run;
- the parameter count of every arm;
- the parameter-matched variants, if run.

**What this rule does not claim.** {not_claim} The baselines follow the original where it states
something and our reading where it is silent (`ORIGINAL_SPECS.md` §(c)). Nothing here covers the
original's manipulation and humanoid environments: this is one robot, one gait and one terrain, over
four held-out trajectories.

**What the discharging session may and may not do.** As for M-74: `scripts/verdict_baselines.py` as
committed before the runs; the verdict recorded in a new ledger entry naming this one; the `Status`
line settled under PLAN §1.2.3; **not one character of the rule text changed.** A result between
branches is a defect in this rule and is reported as one.

**Evidence** `RUN` `results/p6_baseline_power.json` — the power estimate. `SRC` `docs/presubmission/ORIGINAL_SPECS.md` — the claim. Discharged by `{verdict_file}`, from `scripts/verdict_baselines.py`, neither of which exists yet.
**Status** PRE-REGISTERED, NOT YET DISCHARGED — awaits `{verdict_file}` · **Relevance** METHOD
"""


M75 = base_rule(
    "M-75", "teacher-forced, as the original trains them",
    "**This rule tests the claim as made:** baselines teacher-forced, RWM autoregressive. So it cannot "
    "separate architecture from training regime, and neither could the original. M-76 does.",
    "**teacher-forced, as Arm B is** (each of a window's eight targets predicted from true inputs; "
    "for the RSSM, its standard objective of reconstruction plus a KL term with the posterior "
    "filtering true observations)",
    M75_L1_368, M75_FROM_368, M75_L1_100, M75_FROM_100,
    f"The exact test detects the one real contrast of this rule's kind that already exists, RWM "
    f"teacher-forced (Arm B) against RWM autoregressive (Arm A): {B_POS} of 4 trajectories "
    f"positive, exact {pv(B_P)}.",
    "Arm B, which is RWM itself trained by teacher forcing, is already far worse than Arm A on every "
    "held-out trajectory at h = 368 (above). **If the teacher-forced baselines behave like teacher-"
    "forced RWM, REPRODUCES is the expected verdict**, and it would say more about the training "
    "regime than about the architectures. That is written here so that a REPRODUCES cannot be read "
    "afterwards as evidence for RWM's GRU architecture.",
    ("REPRODUCES", "DOES NOT REPRODUCE", "PARTIAL", "CANNOT BE SETTLED"),
    "**Licenses the paper to say**, for REPRODUCES, that the original's comparison is reproduced on "
    "this arena, as the original ran it: autoregressive RWM against teacher-forced baselines. "
    "DOES NOT REPRODUCE names **every** baseline that beats RWM. PARTIAL names which baselines RWM beats "
    "and which this arena cannot separate from it. CANNOT BE SETTLED says only that none is "
    "resolvable at the MDE.",
    "It does not separate architecture from training regime; that is M-76.",
    "results/baselines_verdict.json")

M76 = base_rule(
    "M-76", "trained autoregressively, as RWM is",
    "**This rule is not the original's comparison.** It holds the training regime fixed, with every "
    "arm autoregressive, so that what remains is architecture. For the RSSM the original itself "
    "predicts a tie (above).",
    "**autoregressively, as Arm A is.** The MLP slides its input window over its own sampled "
    "predictions. The transformer appends its own sampled predictions, with context capped at 32. The "
    "RSSM filters the 32 history rows with its posterior, then rolls its prior open-loop over the 8 "
    "forecast rows, feeding back its own samples; its loss is the same sampled squared error on the "
    "decoded forecasts, plus its KL term on the history rows",
    M76_L1_368, M76_FROM_368, M76_L1_100, M76_FROM_100,
    f"Real contrasts of this rule's kind, between autoregressive models of different construction, "
    f"already exist and are small. Arm A with the corrected Gaussian NLL against Arm A: {N_POS} of "
    f"4 trajectories positive, mean {N_MEAN:+.4f}, exact {pv(N_P)}, which this rule "
    f"{'WOULD' if N_P <= holm6[0] else 'would NOT'} reject at its first Holm level. Arm A as an "
    f"ensemble of 5 against Arm A: {E_POS} of 4 positive, mean {E_MEAN:+.4f}, exact {pv(E_P)}, "
    f"which it {'WOULD' if E_P <= holm6[0] else 'would NOT'} reject. **A difference of that size is "
    f"detected sometimes, not reliably.** The MDE above is the size detected 80% of the time.",
    "The original predicts an autoregressive RSSM comparable to RWM. If it is, the RSSM's result "
    "here is CANNOT BE SETTLED, and **RWM AHEAD OF ALL THREE is then unreachable**. The likeliest "
    "verdicts are PARTIAL or CANNOT BE SETTLED, and either would be consistent with the original's "
    "own qualification. A BASELINE AHEAD would go beyond anything the original reports.",
    ("RWM AHEAD OF ALL THREE", "A BASELINE AHEAD", "PARTIAL", "CANNOT BE SETTLED"),
    "**Licenses the paper to say**, for each branch, only what it names about architecture at a "
    "fixed, autoregressive training regime; A BASELINE AHEAD names **every** baseline ahead. It is "
    "**never** a verdict on the original's claim, which M-75 carries.",
    "It is not the original's comparison and cannot overturn M-75's verdict on it.",
    "results/baselines_verdict.json")


def main():
    if "--dry-run" in sys.argv:
        out = sys.argv[sys.argv.index("--dry-run") + 1]
        open(out, "w", encoding="utf-8").write(M74 + "\n" + M75 + "\n" + M76)
        print(f"dry run: wrote the three entries to {out}; the ledger is untouched")
        return 0
    txt = open(LEDGER, encoding="utf-8").read()
    for rid in ("M-74", "M-75", "M-76"):
        assert f"### {rid} " not in txt, f"{rid} already exists; the ledger is append-only"
    ms = [int(x) for x in re.findall(r"^### M-(\d+) ", txt, re.M)]
    assert max(ms) == 73 and len(ms) == 73, f"expected M-1..M-73, found max {max(ms)} of {len(ms)}"
    res = open(RESULTS_MD, encoding="utf-8").read()
    row = re.compile(r"^(\|\s*`M-`[^|]*\|\s*)(\d+)(\s*\|)", re.M)
    hits = row.findall(res)
    assert len(hits) == 1 and hits[0][1] == "73", hits
    bak = os.environ.get("S1_BACKUP_DIR")
    assert bak and os.path.isdir(bak), "set S1_BACKUP_DIR to a scratch directory for the .bak copies"
    shutil.copy(LEDGER, os.path.join(bak, "FINDINGS_LEDGER.md.bak"))
    shutil.copy(RESULTS_MD, os.path.join(bak, "RESULTS.md.bak"))
    add = "\n" + M74 + "\n" + M75 + "\n" + M76
    if not txt.endswith("\n"):
        add = "\n" + add
    with open(LEDGER, "a", encoding="utf-8") as f:
        f.write(add)
    res2 = row.sub(lambda m_: m_.group(1) + str(73 + 3) + m_.group(3), res, count=1)
    open(RESULTS_MD, "w", encoding="utf-8").write(res2)
    print("appended M-74, M-75, M-76; RESULTS.md M- count 73 -> 76")


if __name__ == "__main__":
    sys.exit(main())
