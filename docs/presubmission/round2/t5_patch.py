"""Round 2, T5: Appendix H (item 5) and its pointer in section 7 (item 6). Whitespace-tolerant, each match
asserted exactly once, nothing written before every assert passes, a .bak beside the file.
Usage: t5_patch.py appH | pointer"""
import re
import shutil
import sys

F = "PAPER.template.md"

APPENDIX_H = """
## Appendix H — findings not in the main text

The ledger tags some of its entries as contributions of this project. These are the confirmed ones the
body does not state, or uses without stating the finding itself, each checked against its ledger entry.
Code facts are cited by file and line at the pinned upstream commits; every measurement is read from
the artifact named. Measurements are at {{iters_main}} training iterations unless a row says otherwise.

| finding | evidence (ledger ID, artifact) | bearing on the paper |
|---|---|---|
| ***Paper-versus-code gaps*** | | |
| No forecast decay factor exists: the training loss averages every forecast step with equal weight, though the paper describes a decay | C-09; `system_dynamics.py:186-231` and both config files | Our training does the same, so the released behaviour is an undecayed loss on both sides of every comparison |
| The auxiliary heads (contact and termination) are trained on true next states, the state head on its own samples | M-13; `system_dynamics.py:216, 264` | In a rollout the auxiliary heads read predicted states they never trained on; this paper compares states only (§5.3) and does not measure them |
| Training feeds back a reparameterised sample, inference the mean | C-05; `system_dynamics.py:114, 215` | With the per-member σ collapsed (§6.3) the sample is numerically the mean, so no result here depends on the difference |
| Actions enter the network raw (the config's action mean and standard deviation are zeros and ones), and no action scale is recorded in either repository, so they are not joint targets in radians | C-07, D-07; `anymal_d_flat_cfg.py` | A perturbation of one size means different things for actions and for states; nothing here perturbs either |
| The release's configuration, the paper (Table S7, {{iters_main}}) and the checkpoint's own tag state three different training lengths; the first author confirms the configuration's is a typo | C-13; `base_cfg.py:97`, the checkpoint's `iter` field | §7.5: none of them reaches the released variance state at a constant rate |
| ***Pipeline defects*** | | |
| The reset guard tests index *values* for truthiness, so a reset at the first row would be missed | B-02; `train.py:143` | Latent twice over: this dataset has no reset at its first row and marks none at all (§7.1) |
| The train/test split draws windows at random, and adjacent windows share all but one of their {{win_len}} rows, so the released test loss is not held out | B-03; `model_training.py:33` | The held-out arena (§3) is built from whole episodes and does not use this split |
| ***Measurements*** | | |
| The data hold {{d10_n_regimes}} commanded-velocity segments, {{d10_per_ep_word}} per episode with a third in episode {{d10_extra_ep}} | D-10; `results/step0_regimes.json` | A held-out episode is not a near-duplicate of a training one: the held-out pair tests generalisation across velocity commands, within one gait and terrain |
| `state_min_logstd`, on the slower gradient path C-11 identifies, drifts {{o12_rate_ratio}}× slower than `log_delta_logstd`; extrapolated, the two imply {{r25_implied_ld}} and {{r25_implied_min}} iterations for the released variance state | R-25; `results/step6_3_min_logstd.json` | §7.5's conclusion does not rest on one parameter |
| Over overlapping trajectories, the released checkpoint's worst twentieth carry {{r30_tail_share}}% of its squared error at h = {{v2_diag_h}} on the held-out pair, but they fall in {{r30_n_regions_word}} short stretches of data, one per episode; on the {{r30_n_nonoverlap}} non-overlapping trajectories the largest is {{r30_maxmed}}× the median, and the checkpoint beats the floor | R-30; `results/taskAB_gate_r27.json` | A tail measured on overlapping trajectories can be one short stretch of data, which a count of independent trajectories (§3) exposes |
| The A/B relative-L1 gap at h = {{v2_diag_h}} is positive on all {{r39_n_eps_word}} episodes, from {{r39_gap_lo}} up; episode {{r39_ep}}, one of the held-out pair, gives {{r39_ep_gap}}, {{r39_ep_over_next}}× the next largest, so the pair's {{r39_gap_holdout}} is {{r39_ho_over_other}}× the other {{r39_n_other_word}} episodes' {{r39_gap_other}} | R-39; `results/task4_arenas.json` | The direction is robust across episodes; a magnitude read from the held-out pair overstates the typical episode |
| Per state dimension, the released checkpoint loses to the hold-last floor on {{r45_rel_all}} of {{r45_n_dims}} across all ten episodes ({{r45_nind_all}} independent {{h2h_unit}}-step trajectories) and on {{r45_rel_ho}} on the held-out pair ({{r45_nind_ho}}), including all three components of the gravity vector; Arm A at {{iters_long}} iterations loses on {{r45_A_n}} in each, {{r45_A_dim}} | R-45, and R-29 on overlapping trajectories; `results/task2_3_matched_trend.json` | Per dimension, a model trained from scratch fails far less often, even on the pair the checkpoint trained on and Arm A did not; one seed (seed {{r45_seed}}, §11) |
| Over {{r46_n_ck_word}} checkpoints up to {{iters_long}} iterations, the absolute A/B gap at h = {{v2_diag_h}} narrows as both arms improve (held-out pair {{r46_o_gap0}} to {{r46_o_gap1}}, in-sample {{r46_i_gap0}} to {{r46_i_gap1}}), while the ratio does not shrink ({{r46_o_ratio0}}× to {{r46_o_ratio1}}×, in-sample {{r46_i_ratio0}}× to {{r46_i_ratio1}}×) | R-46; `results/task2_3_matched_trend.json` | An absolute effect quoted early overstates what remains, a ratio does not, and §5 reports ratios at {{iters_long}} iterations; one seed (seed {{r45_seed}}, §11) |

---
"""

ITEMS = {
    "appH": None,
    "pointer": [("""## 7. Defects in the released pipeline

**7.1 Ten unmarked episode boundaries.**""",
                 """## 7. Defects in the released pipeline

Appendix H lists the ledger's other confirmed findings that the body does not state, among them
latent defects in the released data pipeline and departures of the released code from the paper's
description.

**7.1 Ten unmarked episode boundaries.**""")],
}


def main():
    t = open(F).read()
    for it in sys.argv[1:]:
        if it == "appH":
            assert "## Appendix H" not in t
            assert t.rstrip().endswith("---"), "the template no longer ends with Appendix G's rule"
            t = t.rstrip("\n") + "\n" + APPENDIX_H
            continue
        for old, new in ITEMS[it]:
            p = re.compile(r"\s+".join(re.escape(w) for w in old.split()))
            n = len(p.findall(t))
            assert n == 1, f"{it}: {n} matches for {old[:60]!r}"
            t = p.sub(lambda _: new, t, count=1)
    shutil.copy(F, F + ".bak")
    open(F, "w").write(t)
    print("patched", F, sys.argv[1:])


if __name__ == "__main__":
    main()
