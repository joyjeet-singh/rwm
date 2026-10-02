"""Round 2, T5: the Appendix H review's fixes (evidence R2T5/t5_review.md). Whitespace-tolerant, each match
asserted exactly once, nothing written before every assert passes, a .bak beside the file."""
import re
import shutil

F = "PAPER.template.md"
EDITS = [
# A14: the pointer
("""Appendix H lists the ledger's other confirmed findings that the body does not state, among them
latent defects in the released data pipeline and departures of the released code from the paper's
description.""",
 """Appendix H lists the ledger's other confirmed contributions that the body does not state, among
them defects in the released data pipeline and departures of the released code from the paper's
description."""),
# A11: the caption
("""Measurements are at {{iters_main}} training iterations unless a row says otherwise.""",
 """Measurements are at {{iters_main}} training iterations unless a row says otherwise or concerns the
released checkpoint."""),
# A6: C-09's bearing
("""| Our training does the same, so the released behaviour is an undecayed loss on both sides of every comparison |""",
 """| Our training does the same, so the loss is undecayed in the released code and in ours |"""),
# A1: M-13's addresses
("""| M-13; `system_dynamics.py:216, 264` |""", """| M-13; `system_dynamics.py:217, 261` |"""),
# A1, A3: C-05's addresses and bearing
("""| C-05; `system_dynamics.py:114, 215` | With the per-member σ collapsed (§6.3) the sample is numerically the mean, so no result here depends on the difference |""",
 """| C-05; `system_dynamics.py:115, 217` | Our arms train and roll out the same way; for the released checkpoint, whose per-member σ has collapsed (§6.3), the sample is numerically the mean |"""),
# A13, A7: C-07/D-07
("""and no action scale is recorded in either repository, so they are not joint targets in radians | C-07, D-07; `anymal_d_flat_cfg.py` | A perturbation of one size means different things for actions and for states; nothing here perturbs either |""",
 """and no action scale is recorded in either repository; measured against joint motion, they are not joint targets in radians | C-07, D-07; `anymal_d_flat_cfg.py` | A perturbation of one size means different things for actions and for states; no reported result perturbs either |"""),
# A2, A15: C-13
("""The release's configuration, the paper (Table S7, {{iters_main}}) and the checkpoint's own tag state three different training lengths; the first author confirms the configuration's is a typo |""",
 """The release's configuration, the paper (Table S9, {{iters_main}}) and the checkpoint's own tag state three different training lengths; the first author believes the configuration's is a typo |"""),
# A12: D-10
("""| The data hold {{d10_n_regimes}} commanded-velocity segments, {{d10_per_ep_word}} per episode with a third in episode {{d10_extra_ep}} |""",
 """| The data hold {{d10_n_regimes}} plateaus of achieved base velocity, {{d10_per_ep_word}} per episode with a third in episode {{d10_extra_ep}}; the command itself is not recorded, and the plateaus match the simulator's command resampling |"""),
# A4: R-25
("""extrapolated, the two imply {{r25_implied_ld}} and {{r25_implied_min}} iterations for the released variance state |""",
 """extrapolated from one Arm A run's rates, the two imply about {{r25_implied_ld}} and {{r25_implied_min}} iterations for the released variance state, an order of magnitude rather than a fitted count |"""),
# A5: R-30
("""| Over overlapping trajectories, the released checkpoint's worst twentieth carry {{r30_tail_share}}% of its squared error at h = {{v2_diag_h}} on the held-out pair, but they fall in {{r30_n_regions_word}} short stretches of data, one per episode; on the {{r30_n_nonoverlap}} non-overlapping trajectories the largest is {{r30_maxmed}}× the median, and the checkpoint beats the floor |""",
 """| Over overlapping trajectories on the held-out pair, which the released checkpoint trained on, its worst twentieth carry {{r30_tail_share}}% of its squared error at h = {{v2_diag_h}} as each dimension's own scale weights it (form 2, which `g_z` dominates; Appendix G), and they start within {{r30_n_regions_word}} short ranges of rows, one per episode; on the {{r30_n_nonoverlap}} non-overlapping trajectories the largest is {{r30_maxmed}}× the median |"""),
# A10: R-39
("""| The A/B relative-L1 gap at h = {{v2_diag_h}} is positive on all {{r39_n_eps_word}} episodes, from {{r39_gap_lo}} up;""",
 """| The A/B relative-L1 gap at h = {{v2_diag_h}} (teacher forcing's error minus autoregressive training's, over {{r39_n_per_ep}} independent trajectories per episode) is positive on all {{r39_n_eps_word}} episodes, from {{r39_gap_lo}} up;"""),
# A8: R-45
("""| Per state dimension, the released checkpoint loses to the hold-last floor on {{r45_rel_all}} of {{r45_n_dims}}""",
 """| Per state dimension, over the whole {{v2_diag_h}}-step forecast, the released checkpoint loses to the hold-last floor on {{r45_rel_all}} of {{r45_n_dims}}"""),
("""| Per dimension, a model trained from scratch fails far less often, even on the pair the checkpoint trained on and Arm A did not; one seed (seed {{r45_seed}}, §11) |""",
 """| Per dimension, a model trained from scratch fails far less often, even on the pair the checkpoint trained on and Arm A did not. In aggregate it does not: on the held-out pair the released checkpoint is ahead at h = 8 and level at h = {{v2_diag_h}} (R-45). One seed (seed {{r45_seed}}, §11) |"""),
# A9: R-46
("""while the ratio does not shrink ({{r46_o_ratio0}}× to {{r46_o_ratio1}}×, in-sample {{r46_i_ratio0}}× to {{r46_i_ratio1}}×) |""",
 """while the ratio does not shrink ({{r46_o_ratio0}}× to {{r46_o_ratio1}}×, in-sample {{r46_i_ratio0}}× to {{r46_i_ratio1}}×). The held-out values are not monotone: both peak at the {{r46_pk_ord}} checkpoint ({{r46_o_gap_pk}}, {{r46_o_ratio_pk}}×), one anomalous Arm B value |"""),
]


def main():
    t = open(F).read()
    for old, new in EDITS:
        p = re.compile(r"\s+".join(re.escape(w) for w in old.split()))
        n = len(p.findall(t))
        assert n == 1, f"{n} matches for {old[:70]!r}"
        t = p.sub(lambda _: new, t, count=1)
    shutil.copy(F, F + ".bak")
    open(F, "w").write(t)
    print("patched", F, len(EDITS), "edits")


if __name__ == "__main__":
    main()
