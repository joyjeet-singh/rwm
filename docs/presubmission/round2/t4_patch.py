"""Round 2, T4: install the section 5.2 / 5.3 rewrite, the abstract and contribution 3 (Annex 2 E2, E3, E6,
E7; Annex 3). Whitespace-tolerant, each match asserted exactly once, nothing written before every assert
passes, a .bak beside each file. Usage: t4_patch.py ITEM [ITEM ...] (items, in order: e2 e3 e6 e7 abstract appd)."""
import re
import shutil
import sys

SCRATCH_ABSTRACT = sys.argv[sys.argv.index("--abstract") + 1] if "--abstract" in sys.argv else None


def pat(old):
    return re.compile(r"\s+".join(re.escape(w) for w in old.split()))


ITEMS = {}

# ---- E2: section 5.2 ----------------------------------------------------------------------------
ITEMS["e2"] = [("PAPER.template.md", [
("""| (M, N) | relative-L1, h = {{v2_deploy_h}} | relative-L1, h = {{v2_diag_h}} | difference from the centre [95% interval] | result | hours per run |""",
 """| (M, N) | relative-L1, h = {{v2_deploy_h}} | relative-L1, h = {{v2_diag_h}} | difference from the centre [95% interval] | result | cost per iteration, relative to the centre |"""),
("""(`results/mn_sweep_verdict.json`). Hours are wall clock per run (`results/presubmission_runtime.json`);
{{mn_n_overlapped}} of the {{rt_sweep_runs}} sweep runs overlapped other logged CPU work, which
inflates their hours and changes no weight (Appendix B). The hold-last floor""",
 """(`results/mn_sweep_verdict.json`). The last column is a configuration's steady training time per
iteration over the centre's, timed without contention (`results/mn_compute_matched.json`); hours per
run, and the {{mn_n_overlapped}} of {{rt_sweep_runs}} sweep runs that overlapped other logged CPU work,
are in Appendix B. The hold-last floor"""),
("""The original's direction on N holds. The shortest forecasts are far worse, which is §5's
teacher-forcing result again, and the longest are better. Its direction on M holds only in part. The
original's error falls steeply from M = 1 to M = 8 and then flattens (`ORIGINAL_SPECS.md` a.5). On
the governing reading ours does not fall at all: {{mn_mvar_better_list}} beat the centre and no
shorter history is resolvably worse, though other readings the rule reports put
shorter histories behind it: {{mn_mvar_other_worse}}. The centre's tie with its longest-forecast neighbour becomes a loss.""",
 """**The history length departs furthest from the original.** The original's error falls steeply
from M = 1 to M = 8 and then flattens (`ORIGINAL_SPECS.md` a.5). On the governing reading ours does
not fall at all: {{mn_mvar_better_list}}, histories shorter than the centre's, beat it, and no
shorter history is resolvably worse, though other readings the rule reports put shorter histories
behind it: {{mn_mvar_other_worse}}. The original's direction on N holds: the shortest forecasts
are far worse, which is §5's teacher-forcing result again, and the longest are better, so the
centre's tie with its longest-forecast neighbour becomes a loss.

**Accuracy at equal compute (post hoc; ledger R-78).** A longer training forecast costs more per
iteration, {{n3_cost_M32_N16}}× the centre's for {{n3_lf_label}} and {{n3_cost_M32_N32}}× for {{mn_best_config}}, so at
a given iteration count those also had more computation; the shorter histories that win cost less,
{{n3_cost_M8_N8}}× and {{n3_cost_M2_N8}}×. Training the centre longer controls for this
(`results/mn_compute_matched.json`; differences signed as in the table). At {{n3_k_mid}} iterations
the centre has had {{n3_best_over_mid}}× the computation of {{mn_best_config}} at {{iters_main}}, and
{{mn_best_config}} is still ahead at h = {{v2_diag_h}}, a difference of {{n3_best_D_mid}}
{{n3_best_ci_mid}}, so its advantage is not an artefact of extra computation per iteration. That is
as far as it goes. At {{iters_long}} iterations, {{n3_best_over_long}}× the computation, the
difference is {{n3_best_D_long}} {{n3_best_ci_long}}, not resolved; on the in-sample arena the centre
at {{n3_k_mid}} already draws level with {{mn_best_config}} ({{n3_best_ins_D_mid}} {{n3_best_ins_ci_mid}})
and passes {{n3_lf_label}} ({{n3_lf_ins_D_mid}} {{n3_lf_ins_ci_mid}}); and at {{iters_long}} it passes
both shorter histories, {{n3_sh_long_clause}}. None of this re-opens rule M-74."""),
("""no further: a larger one may favour a longer history. With {{mn_nind}} independent trajectories, the rule's minimum detectable effect at h = {{v2_diag_h}},
the difference its first Holm step would usually detect, is about {{mn_mde_h368}}% of the centre's
error.""",
 """no further: a larger one may favour a longer history. All {{tail_n}} runs at {{iters_main}} iterations,
the sweep's, the baselines' and both arms', are still lowering their training loss at the end, with slopes
from {{tail_slope_lo}} to {{tail_slope_hi}} per thousand iterations (`results/training_tail_slopes.json`,
post hoc), so the ranking is at this budget, not at convergence. With {{mn_nind}} independent trajectories, the rule's minimum detectable effect at h = {{v2_diag_h}},
the difference its first Holm step would usually detect, is about {{mn_mde_h368}}% of the centre's
error."""),
])]

# ---- E6: the pooled nRMSE sentence in section 5.2's arena paragraph; the head-to-head table ------
ITEMS["e6"] = [("PAPER.template.md", [
("""The hold-last floor is {{mn_floor_h100}} at h = {{v2_deploy_h}} and {{mn_floor_h368}} at h = {{v2_diag_h}}.

**Result: {{mn_verdict}}.**""",
 """The hold-last floor is {{mn_floor_h100}} at h = {{v2_deploy_h}} and {{mn_floor_h368}} at h = {{v2_diag_h}}.
The rules' evaluator averaged nRMSE per trajectory, where §3.1 pools it. The nRMSE readings quoted
alongside the rules here and in §5.3 are pooled, recomputed afterwards (post hoc; ledger R-77,
`results/pooled_nrmse_alongside.json`), and return what the averaged ones did everywhere except
{{n2_n_changed_word}} in-sample readings of §5.3's rules: {{n2_changed_list}}.

**Result: {{mn_verdict}}.**"""),
] + [(f"| {name}, {regname} (§5.3) | — | {{{{h2h_bl_{a}_{r}_l1_h1}}}} | — | {{{{h2h_bl_{a}_{r}_l1_h8}}}} | — | {{{{h2h_bl_{a}_{r}_l1_h100}}}} | — | {{{{h2h_bl_{a}_{r}_l1_h368}}}} |",
      f"| {{{{h2h_bl_{a}_{r}_label}}}} | {{{{h2h_bl_{a}_{r}_nrmse_h1}}}} | {{{{h2h_bl_{a}_{r}_l1_h1}}}} | {{{{h2h_bl_{a}_{r}_nrmse_h8}}}} | {{{{h2h_bl_{a}_{r}_l1_h8}}}} | {{{{h2h_bl_{a}_{r}_nrmse_h100}}}} | {{{{h2h_bl_{a}_{r}_l1_h100}}}} | {{{{h2h_bl_{a}_{r}_nrmse_h368}}}} | {{{{h2h_bl_{a}_{r}_l1_h368}}}} |")
     for a, name in (("mlp", "MLP"), ("rssm", "RSSM"), ("transformer", "transformer"))
     for r, regname in (("tf", "teacher-forced"), ("ar", "autoregressive"))] + [
("""Both
aggregations for those, relative-L1 alone for §5.3's architecture baselines, and one arena:""",
 """Both
aggregations, for those and for §5.3's architecture baselines, and one arena:"""),
("""The architecture-baseline rows (§5.3) come from
their own evaluator on the same four trajectories, whose relative-L1 reproduces the Arm A row
exactly; its nRMSE is aggregated per trajectory rather than pooled, so it is not shown here.""",
 """The architecture-baseline rows (§5.3) come from
their own evaluator on the same four trajectories, whose relative-L1 reproduces the Arm A row
exactly; their nRMSE is pooled as §3.1 defines it, recomputed afterwards from the same rollouts
(post hoc, `results/pooled_nrmse_rescore.json`), and † marks a diverged row (§5.3)."""),
])]

# ---- E7 + E3: section 5.3 ------------------------------------------------------------------------
ITEMS["e2"][0][1].extend([
("""| model | parameters | relative-L1, h = {{v2_deploy_h}} | relative-L1, h = {{v2_diag_h}} | difference from RWM [95% interval] | result | hours per run |""",
 """| model | parameters | relative-L1, h = {{v2_deploy_h}} | relative-L1, h = {{v2_diag_h}} | difference from RWM [95% interval] | result | cost per iteration, relative to RWM |"""),
("""positive when RWM is better, and "result" is after Holm (`results/baselines_verdict.json`); hours
are as in §5.2.""",
 """positive when RWM is better, and "result" is after Holm (`results/baselines_verdict.json`). The last
column is timed beside RWM in one sitting (`results/mn_compute_matched.json`); hours per run are in
Appendix B."""),
("""which inflates their wall clock and changes no weight; the artifact lists each overlap.""",
 """which inflates their wall clock and changes no weight; the artifact lists each overlap. Per run family,
every run at {{iters_main}} iterations (the sweep's centre is §5's Arm A, whose runs are counted above):

| run family | runs | hours per run, mean | runs that overlapped other CPU work |
|---|---|---|---|
{{rt_pre_table}}"""),
])

# ---- E7: the diverged-rollout flag in section 5.3's caption (the head-to-head rows carry it in their keys)
ITEMS["e7"] = [("PAPER.template.md", [
("""column is timed beside RWM in one sitting (`results/mn_compute_matched.json`); hours per run are in
Appendix B.""",
 """column is timed beside RWM in one sitting (`results/mn_compute_matched.json`); hours per run are in
Appendix B. † marks a diverged row, one where any seed's mean relative-L1 at h = {{v2_diag_h}} exceeds
{{div_factor}}× the hold-last floor's (`results/pooled_nrmse_rescore.json`, post hoc). Run-away
rollouts dominate those {{div_n_word}} rows' means; per seed they are {{div_per_seed}}. No verdict
depends on that magnitude, only on the sign: each such row's four per-trajectory differences from
RWM are all positive, so every bootstrap resample favours RWM whatever their size."""),
])]

# ---- E3: section 5.3's result and the RSSM paragraph ----------------------------------------------
ITEMS["e3"] = [("PAPER.template.md", [
("""**Result: {{bl_tf_verdict}} with the baselines teacher-forced, and {{bl_ar_verdict}} with them
trained autoregressively.** All {{bl_n_rows_word}} comparisons favour RWM, with intervals that
exclude zero, and every baseline row is above the hold-last floor at h = {{v2_diag_h}}, which RWM is
below. The second verdict compares architectures at one training regime and is not a verdict on the
original's claim, which the first carries. The lead is a long-horizon one.
At h = 1 both rules return {{bl_tf_h1}}, and the teacher-forced RSSM's error, {{h2h_bl_rssm_tf_l1_h1}},
is below RWM's {{h2h_armA_l1_h1}} without being resolvable. At h = 8 both return {{bl_tf_h8}}.

**Where ours departs.** The original adds that an RSSM trained autoregressively
performs comparably to RWM. Ours does not: {{h2h_bl_rssm_ar_l1_h368}} against RWM's
{{bl_rwm_l1_h368}} at h = {{v2_diag_h}}. That may be our RSSM rather than the architecture: Table
S7's latent is ambiguous, and we read it in DreamerV2's naming, without its layer-normalised
recurrent cell (`BASELINE_SPECS.md`, the RSSM rows).""",
 """**Result: {{bl_tf_verdict}} with the baselines teacher-forced, and {{bl_ar_verdict}} with them
trained autoregressively.** RWM is ahead of baselines built to our reading of Table S7 and trained
with RWM's settings for {{iters_main}} iterations: all {{bl_n_rows_word}} comparisons favour it, with
intervals that exclude zero. That says less than it seems at h = {{v2_diag_h}}, where every baseline
row, in both regimes, is above the hold-last floor and RWM is below it: no baseline beats predicting
no change. The second verdict compares architectures at one training regime and is not a verdict on
the original's claim, which the first carries. The lead is a long-horizon one, and the rules'
relative-L1 readings at other horizons say where it starts. Teacher-forced, the baselines fall
resolvably behind from {{bl_tf_lead_from}} (the transformer from {{bl_tf_tr_lead_from}}).
Trained autoregressively, the RSSM falls behind from {{bl_ar_rssm_lead_from}}, but the MLP and the transformer only from {{bl_ar_lead_from}}, the method's own horizon, where they trail by
{{bl_ar_mlp_D_h100}} {{bl_ar_mlp_ci_h100}}, about {{bl_ar_mlp_pct_h100}}% of RWM's
{{h2h_armA_l1_h100}}, and {{bl_ar_tr_D_h100}} {{bl_ar_tr_ci_h100}}. Before those horizons a baseline
cannot be told apart from RWM: at h = 1 both rules return {{bl_tf_h1}}, and at h = 8 both return
{{bl_tf_h8}}.

**Our RSSM is not an informative comparison.** Teacher-forced, it is the most accurate model here one
step ahead, {{h2h_bl_rssm_tf_l1_h1}} against RWM's {{h2h_armA_l1_h1}} and the floor's {{x1_floor_h1}},
though not resolvably, and it has collapsed open-loop by h = 32, where its {{x1_tf_mode_h32}} is above
the floor's {{x1_floor_h32}}. The original adds that an RSSM trained autoregressively performs
comparably to RWM; ours does not, {{h2h_bl_rssm_ar_l1_h368}} against RWM's {{bl_rwm_l1_h368}} at
h = {{v2_diag_h}}. A diagnostic committed before its readings existed (rule X1, ledger M-80;
exploratory, it re-opens neither rule) asks why. Its Part A reads the forecast differently, feeding
the prior's expected or sampled latent in place of its most likely one: the error at h = 32 falls to
{{x1_tf_exp_h32}} and {{x1_tf_samp_h32}}, still above the floor, so it returns **{{x1_reading_a}}**
(M-81). Its Part B is descriptive: over the history, the teacher-forced RSSM's one-step error from its
prior is {{x1b_tf_ratio_lo}} to {{x1b_tf_ratio_hi}}× its error from its posterior at the same
recurrent state (the autoregressive one's at most {{x1b_ar_ratio_hi}}×), with {{x1b_kl_lo}} to
{{x1b_kl_hi}} nats of KL divergence between them per step. {{rssm_partc_sentence}} The failure may be
our RSSM rather than the architecture: Table S7's latent is ambiguous, and we read it in DreamerV2's
naming, without its layer-normalised recurrent cell (`BASELINE_SPECS.md`, the RSSM rows). Until X1
says otherwise, the architecture claim rests on the MLP and the transformer."""),
])]

# ---- abstract and contribution 3 ----------------------------------------------------------------
ITEMS["abstract"] = [("PAPER.template.md", [
("""- **Two more of the base paper's claims, tested under rules committed before the runs.** Its
  architecture claim holds: RWM is ahead at h = {{v2_diag_h}} of MLP, RSSM and transformer baselines
  built to our reading of its specification and teacher-forced as it trains them, and stays ahead
  when they are trained autoregressively, a comparison of architectures at one training regime
  rather than a test of the claim (§5.3). Its chosen history and forecast lengths,
  {{mn_centre_label}}, are not optimal at our budget: {{mn_n_better_word}} of their
  {{mn_n_configs_word}} one-factor neighbours beat them, the best reaching {{mn_best_l1_h368}}
  against {{mn_centre_l1_h368}} in relative-L1 at h = {{v2_diag_h}} (§5.2).""",
 """- **Two more of the base paper's claims, tested under rules committed before the runs.** RWM is
  ahead at h = {{v2_diag_h}} of MLP, RSSM and transformer baselines built to our reading of its
  specification and trained with RWM's settings, whether teacher-forced as the original trains them
  or autoregressively, though every baseline is worse there than predicting no change and our RSSM's
  open-loop collapse is not a matter of how its forecast is read (§5.3). On accuracy alone,
  {{mn_n_better_word}} of the {{mn_n_configs_word}} one-factor neighbours of the original's
  {{mn_centre_label}} beat it at our budget — {{mn_better_long_phrase}}, and the
  {{mn_n_short_better_word}} shorter histories {{mn_mvar_better_list}}, although the original's error
  falls steeply as the history grows to M = 8 — the best of them even when the centre trains longer;
  the original chose the centre as a trade-off with training time, which we do not test (§5.2)."""),
])]

# ---- the paper's Appendix D rows ------------------------------------------------------------------
ITEMS["appd"] = [("PAPER.template.md", [
("""| **{{mn_verdict}}** on the accuracy half (§5.2): {{mn_better_list}} beat it. Training time is reported, not tested |""",
 """| **{{mn_verdict}}** on the accuracy half (§5.2): {{mn_better_list}} beat it at our budget, the best of them even when the centre trains longer (post hoc). The trade-off with training time is not tested |"""),
("""**{{bl_tf_verdict}}** with the baselines teacher-forced, as the original trains them, and **{{bl_ar_verdict}}** with them trained autoregressively, which compares architectures at one training regime rather than testing this claim (§5.3). One robot where the original has several |""",
 """**{{bl_tf_verdict}}** with the baselines teacher-forced, as the original trains them, and **{{bl_ar_verdict}}** with them trained autoregressively, which compares architectures at one training regime rather than testing this claim (§5.3). The baselines are built to our reading of Table S7 and trained with RWM's settings; at h = {{v2_diag_h}} every one is worse than predicting no change, and the RSSM comparison is uninformative (rule X1), so the claim rests on the MLP and the transformer. One robot where the original has several |"""),
])]


def main():
    items = [a for a in sys.argv[1:] if not a.startswith("--") and a != SCRATCH_ABSTRACT]
    plan = {}
    for it in items:
        for f, edits in ITEMS[it]:
            t = plan.get(f) or open(f).read()
            for old, new in edits:
                m = pat(old).findall(t)
                assert len(m) == 1, f"{it}: {f}: {len(m)} matches for {old[:70]!r}"
                t = pat(old).sub(lambda _: new, t, count=1)
            plan[f] = t
    if SCRATCH_ABSTRACT:
        f = "PAPER.template.md"
        t = plan.get(f) or open(f).read()
        a, b = t.index("## Abstract\n\n") + len("## Abstract\n\n"), t.index("\n\n---\n\n## 1. Introduction")
        plan[f] = t[:a] + open(SCRATCH_ABSTRACT).read().rstrip("\n") + t[b:]
    for f, t in plan.items():
        shutil.copy(f, f + ".bak")
        open(f, "w").write(t)
        print("patched", f)


if __name__ == "__main__":
    main()
