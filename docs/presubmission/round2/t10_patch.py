"""Round 2, T10: the small fixes from REVIEW.md and the two fresh-eyes agents (evidence R2T10).

Each fix is three sentences or fewer (PLAN T10 item 4). Wording only: every number stays a {{key}},
no claim is strengthened, nothing leaves the paper. Matched whitespace-tolerantly, each exactly once,
and nothing is written until every edit has matched.
"""
import re
import shutil
import sys

T = "PAPER.template.md"
BAK = "/Users/Shared/rwm_verify/evidence/R2T10/bak/PAPER.template.md.t10patch"

EDITS = [
    # ---- checklist item 4 (M-23): the abstract names seed 1, word-neutrally (370 words) ---------
    ("item 4 abstract: seed 1",
     "reproduces under a rule committed in advance, run on one seed per arm; {{d1_seeds}} seeds extend it:",
     "reproduces under a rule committed in advance, run on seed {{m23_seed}} of each arm; {{d1_seeds}} seeds extend it:"),
    ("item 4 abstract: the word that pays for it",
     "beat the original's chosen setting at",
     "beat the original's setting at"),
    ("item 4 section 5.1: the 4.61x is the three-seed extension",
     "still reproduces the training result, {{d1_ratio}}× at h = {{v2_diag_h}} and {{d1_ratio_h100}}× at h = {{v2_deploy_h}},",
     "still reproduces the training result, {{d1_ratio}}× at h = {{v2_diag_h}} and {{d1_ratio_h100}}× at h = {{v2_deploy_h}} over {{d1_seeds}} seeds (the rule ran on seed {{m23_seed}}),"),

    # ---- agent 1 ----------------------------------------------------------------------------
    ("A1-M1 section 5: the floor pointed so on the 400-step unit",
     "the direction the sign test and the hold-last floor already pointed.",
     "the direction the sign test and, on the 400-step unit, the hold-last floor already pointed."),
    ("A1-M1 section 5: teacher forcing against the floor, by unit",
     "predicts the future worse than a model that makes no prediction, at {{a1_B_worse_than_floor_at}} we measured.",
     "predicts the future worse than a model that makes no prediction, at {{a1_B_worse_than_floor_at}} we measured on the 400-step unit. On M-64's shorter units, at the same checkpoint and on the same two episodes, it beats the floor at h = {{m64_B_beats_floor_at}} and loses to it at h = {{m64_B_loses_floor_at}}."),
    ("A1-M1 section 5: the autoregressive arm against the floor, by unit",
     "the only horizon where the autoregressive arm loses to predicting no change.",
     "the only horizon where the autoregressive arm loses to predicting no change on the 400-step unit; on the {{m64_h1_unit}}-row unit both arms beat the floor at h = 1 ({{m64_A_h1}} and {{m64_B_h1}} against {{m64_floor_h1}})."),
    ("A1-M2 section 5: the four gaps are behind the three-seed table",
     "The four per-trajectory gaps behind it (Arm B minus Arm A, three seeds pooled, at h = {{v2_diag_h}}) are",
     "The four per-trajectory gaps behind the three-seed table (Arm B minus Arm A, three seeds pooled, at h = {{v2_diag_h}}) are"),
    ("A1-M3 section 5: the sign test is over episodes",
     "are positive, which is the sign test,",
     "are positive, the direction of the sign test's {{c3_sign_pos}} of {{c3_sign_n}} episodes,"),
    ("A1-M4 section 5: Holm ran over the long-horizon cells; the family of 8 is Bonferroni's",
     "and Holm–Bonferroni over the family of {{c3_family}} out-of-sample comparisons still rejects **{{c3_holm_rejected}} of {{c3_long}}** (Appendix L).",
     "and each still excludes zero at a Bonferroni level of 0.05/{{c3_family}} over the family of {{c3_family}} out-of-sample comparisons, where Holm–Bonferroni over the {{c3_long}} long-horizon cells rejects **{{c3_holm_rejected}} of {{c3_long}}** (Appendix L)."),
    ("A1-M7 section 5.1: the draws are a 2,500-iteration run's",
     "window draws a run makes",
     "window draws a {{iters_main}}-iteration run makes"),

    # ---- agent 2 ----------------------------------------------------------------------------
    ("B-M2 section 6.8: M-49's verdict verbatim",
     "so that rule returns **{{m49_verdict_short}}** (rule M-49, §11).",
     "so that rule returns **{{m49_verdict}}** (rule M-49, §11)."),
    ("B-M2 section 11: M-49's verdict verbatim",
     "**{{m49_verdict_short}}**. Capacity does not explain the effect away;",
     "**{{m49_verdict}}**. Capacity does not explain the effect away;"),
    ("B-M3 section 6.3: the 28 runs, as Appendix J counts them",
     "{{n_runs}} runs at the released width the collapse is linear in iteration count",
     "{{n_runs}} runs at the released width outside §5.2's sweep the collapse is linear in iteration count"),
    ("B-M6 section 6.2: like with like, on the same arena",
     "{{e5_ratio_h100}}× overconfident at h = {{v2_deploy_h}} against its {{d1n_epi_ratio_h100}}×,",
     "{{e5_ratio_h100}}× overconfident at h = {{v2_deploy_h}} against its {{b2_epi_ratio_h100}}× on the same held-out pair ({{d1n_epi_ratio_h100}}× over all ten episodes),"),
    ("B-M7 section 6.5: the released checkpoint's held-out pair is in-sample for it",
     "gives P = {{perm_oos_epi_p_h368}} out of sample and {{perm_ins_epi_p_h368}} in sample,",
     "gives P = {{perm_oos_epi_p_h368}} on the held-out pair and {{perm_ins_epi_p_h368}} on the training episodes, both in-sample for the checkpoint,"),
    ("B-M7 / item 7 section 6.5 table: 'held-out pair', true of every row",
     "| dims with r(σ, error) > 0 at h={{v2_diag_h}}, out-of-sample | perm P at h={{v2_diag_h}}, out-of-sample | perm P at h={{v2_diag_h}}, in-sample |",
     "| dims with r(σ, error) > 0 at h={{v2_diag_h}}, held-out pair | perm P at h={{v2_diag_h}}, held-out pair | perm P at h={{v2_diag_h}}, training episodes |"),
    ("B-M7 Appendix K: the epistemic term exists only on the released checkpoint",
     "At n_independent = {{perm_oos_nind}} 400-step trajectories out of sample,",
     "At n_independent = {{perm_oos_nind}} 400-step trajectories on the held-out pair, in-sample for the checkpoint,"),
    ("B-M8 section 6.5: the direction, model by model, as Appendix S has it",
     "the ordering is directionally consistent across every model and horizon we measured, and is not established",
     "the ordering points the right way for the epistemic term and the faithful and teacher-forced arms, not for the corrected arm or the released aleatoric head (Appendix S), and is not established"),
    ("B-M9 section 6.7 table: the transfer column scores both models",
     "| same, per-horizon c fitted on a *different model* (unpowered) |",
     "| per-horizon c fitted on the *other* model, both models scored (unpowered) |"),
    ("B-M10 Appendix J: only one seed is at 1.02x",
     "and two of {{e5s_seeds}} seeds recover a σ spread of only {{e5s_nll_spread_lo}}× against the truth's {{e5s_span}}×.",
     "and its {{e5s_seeds}} seeds recover σ spreads of only {{e5s_nll_spread_range}}× against the truth's {{e5s_span}}×."),
    ("B-M11 Appendix O: the hours are the runs Appendix B times",
     "against the {{rt_hours}} h Appendix B gives for all of §5–§7's runs",
     "against the {{rt_hours}} h Appendix B gives for the {{run_total}} runs of §5–§7 it times (§5.2's sweep and §5.3's baselines are counted apart)"),
    ("B-M12 Appendix M: one uninformative cell has no interval at all",
     "where an episode bootstrap has n = {{m62_n_ep_oos}} and three distinct resamples;",
     "where an episode bootstrap has n = {{m62_n_ep_oos}} and three distinct resamples, or, for the per-horizon multiplier cell, one episode per direction and no interval at all;"),

    # ---- checklist item 7: released-checkpoint rows on the held-out pair ------------------------
    ("item 7 section 6.2: 'held-out pair'",
     "**All four rows are the held-out arena**",
     "**All four rows are the held-out pair**"),
    ("item 7 section 6.5: the sigma-growth table's released row is in-sample",
     "(Figure 5; {{sig_arena}}, n_independent = {{sig_nind}} 400-step trajectories;",
     "(Figure 5; {{sig_arena}}, n_independent = {{sig_nind}} 400-step trajectories, in-sample for the released checkpoint;"),
    ("item 7 Appendix L: the arena line, for the released row",
     "{{h2h_ntraj}} non-overlapping {{h2h_unit}}-step trajectories, n_independent = {{h2h_nind}}.**",
     "{{h2h_ntraj}} non-overlapping {{h2h_unit}}-step trajectories, n_independent = {{h2h_nind}}; in-sample for the released checkpoint.**"),

    # ---- checklist item 11: captions carry arena, n_independent and checkpoint -----------------
    ("item 11 section 6.6 r_dd table",
     "**Per horizon, on the same {{a2_nind}} trajectories and the same kind of cluster bootstrap:**",
     "**Per horizon, on the same {{a2_nind}} trajectories (the released checkpoint over all ten episodes) and the same kind of cluster bootstrap:**"),
    ("item 11 section 6.6 free-baseline table",
     "*r(disagreement, error) = {{e7_r_dis}} on the released checkpoint at n_independent = {{e7_nind}} 400-step trajectories.",
     "*r(disagreement, error) = {{e7_r_dis}} on the released checkpoint over all ten episodes, n_independent = {{e7_nind}} 400-step trajectories."),
    ("item 11 section 6.8 combined-arm table",
     "*Same trajectories, same harness, same bootstrap unit as the table above,",
     "*Same trajectories (the held-out pair, n_independent = {{m68_nind}}), same harness, same bootstrap unit as the table above,"),
    ("item 11 Appendix N table",
     "of ranks rather than of values, so its being larger than the pooled figure says nothing about how much depth explains.",
     "of ranks rather than of values, so its being larger than the pooled figure says nothing about how much depth explains. Every row is the released checkpoint over all ten episodes, n_independent = {{a2_nind}} 400-step trajectories."),
    ("item 11 Appendix O table",
     "*Shares are of the log improvement, so they add to 100%.",
     "*On the held-out pair's {{r2_nind}} independent trajectories, independent against shared-trunk ensembles, all at {{iters_main}} iterations. Shares are of the log improvement, so they add to 100%."),
    ("item 11 Appendix P table",
     "*The same σ-versus-accuracy split Appendix O uses for rule M-44,",
     "*On the held-out pair, n_independent = {{m68_nind}}, every model at {{iters_main}} iterations: the same σ-versus-accuracy split Appendix O uses for rule M-44,"),
]


def main():
    s = open(T).read()
    plan = []
    for name, old, new in EDITS:
        pat = re.compile(r"\s+".join(re.escape(w) for w in old.split()))
        hits = pat.findall(s)
        if len(hits) != 1:
            sys.exit(f"STOP: '{name}' matched {len(hits)} times")
        plan.append((name, pat, new))
    shutil.copy(T, BAK)
    for name, pat, new in plan:
        s = pat.sub(lambda _: new, s, count=1)
        print(f"  applied: {name}")
    open(T, "w").write(s)
    print(f"  {len(plan)} edits; old template saved to {BAK}")


if __name__ == "__main__":
    main()
