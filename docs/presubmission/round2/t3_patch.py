"""T3's source edits (round2/PLAN.md T3; Annex 2 E1, E4, E5; Annex 3; ruling DECISIONS.md#T3-alignment-framing).

    python docs/presubmission/round2/t3_patch.py ITEM      # ITEM in: e1, e4, e5

Whitespace-tolerant matching (a phrase may wrap across lines); every match must occur exactly once, and nothing
is written until every assertion for the item has passed. Each edited file gets a .bak first; the diff is shown and
the .bak removed. Run from the repository root.
"""
import os, re, shutil, subprocess, sys

def pat(old):
    return re.compile(r"\s+".join(re.escape(w) for w in old.split()))

T, BC = "PAPER.template.md", "docs/BUILD_CHECKS.template.md"

E1 = [
    # the abstract: one clause, no numbers (ruling U4 as amended by DECISIONS.md#T3-alignment-framing)
    (T, "Separately, the released evaluation pairs each prediction with the previous action, overstating the "
        "checkpoint's error on the same trajectories at {{v2_diag_h}} steps by {{ad_nrmse}}% {{ad_nrmse_ci}} in nRMSE "
        "and {{ad_rel}}% {{ad_rel_ci}} in relative-L1; across its ten training episodes the sign reverses.",
     "Separately, the released evaluation pairs each prediction with the previous step's action; this inflates the "
     "checkpoint's error most at short horizons, and at the longest horizon the cost is small and not consistent in sign."),
    # contribution 6 (Annex 3, with the ruling's lead)
    (T, "- **The released evaluation is misaligned by one step, and what that costs is small.** Evaluation feeds the "
        "action from *t−1* where training pairs states and actions index-for-index. On {{ad_nind}} independent "
        "trajectories this overstates the checkpoint's error at h = {{v2_diag_h}} by {{ad_rel}}% {{ad_rel_ci}} on "
        "relative-L1 and {{ad_nrmse}}% {{ad_nrmse_ci}} in nRMSE, and over all ten episodes the sign reverses (§7.2); "
        "shifting evaluation's action index by one step fixes it.",
     "- **The released evaluation is misaligned by one step; the cost is concentrated at short horizons, and at\n"
     "  h = {{v2_diag_h}} it is small and not consistent in sign.** Evaluation feeds the action from *t−1* where\n"
     "  training pairs states and actions index-for-index, and shifting its action index by one step fixes it. On\n"
     "  {{ad_nind}} independent held-out trajectories the stale action raises the checkpoint's error by\n"
     "  {{adh_rel_h1}}% {{adh_rel_ci_h1}} at h = 1, and at h = {{v2_diag_h}} by {{ad_rel}}% {{ad_rel_ci}} on\n"
     "  relative-L1 and {{ad_nrmse}}% {{ad_nrmse_ci}} in nRMSE; over all ten episodes the sign at h = {{v2_diag_h}}\n"
     "  reverses (§7.2)."),
    # §7.2's lead sentence
    (T, "What the stale pairing costs is small, and its sign is not consistent. On the held-out pair's",
     "What the stale pairing costs is concentrated at short horizons; at h = {{v2_diag_h}} it is small, and its\n"
     "sign is not consistent. On the held-out pair's"),
    # §7.2's closing sentences: N1's horizon and sensitivity sentences (Annex 3 variant (a): the h = 1 interval
    # excludes zero); the withdrawn-figures sentence moves to BUILD_CHECKS (below)
    (T, "Every arena here is in-sample for this checkpoint, which trained on all ten episodes. The {{stale_pct}}% "
        "(nRMSE) and {{stale_pct_rel}}% (relative-L1) this paper reported before came from {{ad_pa_n}} overlapping "
        "windows sampled as the upstream samples them, one of which (starting at row {{ad_pa_out_row}}) carries most "
        "of the effect; they are withdrawn (S-20).",
     "Every arena here is in-sample for this checkpoint, which trained on all ten episodes. One step ahead, where a\n"
     "stale action should matter most, it changes the checkpoint's error by {{adh_rel_h1}}% {{adh_rel_ci_h1}} on the\n"
     "same {{ad_nind}} trajectories (`results/alignment_by_horizon.json`). Our own Arm A checkpoints at {{iters_long}}\n"
     "iterations, trained under the causal pairing, change by {{stale_armA_rel_h1}}% at h = 1 and\n"
     "{{stale_armA_rel_h368}}% at h = {{v2_diag_h}} when fed the stale one."),
    (BC, "- **[§7.4]** The duplication control was run only because the first version of the splice finding",
     "- **[§7.2]** The {{stale_pct}}% (nRMSE) and {{stale_pct_rel}}% (relative-L1) this paper reported before came\n"
     "  from {{ad_pa_n}} overlapping windows sampled as the upstream samples them, one of which (starting at row\n"
     "  {{ad_pa_out_row}}) carries most of the effect; they are withdrawn (S-20).\n"
     "- **[§7.4]** The duplication control was run only because the first version of the splice finding"),
    # §3's effective sample size
    (T, "differ. Later sections refer back to this as the n = {{m23_nind}} caveat of §3.",
     "differ. Later sections refer back to this as the n = {{m23_nind}} caveat of §3. One trajectory can carry\n"
     "much of a long-horizon effect: a one-step shift of the action moves single trajectories' {{v2_diag_h}}-step\n"
     "error by anywhere from {{ad20_traj_lo}}% to {{ad20_traj_hi}}% (§7.2), which is why {{m23_nind}} trajectories\n"
     "bound every long-horizon claim."),
    # §3.1's metric paragraph
    (T, "§7.2's alignment defect is given in both metrics side by side, each at h = {{v2_diag_h}} on the same "
        "{{ad_nind}} independent trajectories: {{ad_rel}}% {{ad_rel_ci}} on relative-L1 and {{ad_nrmse}}% "
        "{{ad_nrmse_ci}} in nRMSE.",
     "§7.2's alignment defect is given in both metrics side by side at h = {{v2_diag_h}}, on the same\n"
     "{{ad_nind}} independent trajectories: {{ad_rel}}% {{ad_rel_ci}} on relative-L1 and {{ad_nrmse}}%\n"
     "{{ad_nrmse_ci}} in nRMSE; its larger cost at short horizons is given on relative-L1, at h = 1."),
]

E4 = [
    (T, "the effect survives at 10,000 iterations rather than only at the paper's 2,500.",
     "the effect survives at 10,000 iterations rather than only at the paper's 2,500. The rule was run on\n"
     "seed {{m23_seed}} of each arm: autoregressive {{m23_A_s1}} against teacher forcing {{m23_B_s1}} at\n"
     "h = {{v2_diag_h}}, {{m23_ratio}}×, gap interval [{{m23_ci_lo}}, {{m23_ci_hi}}]. Seeds {{m23_other_seeds}}\n"
     "were trained after the verdict (ledger R-60, {{r60_date}}), so the three-seed figures below extend it\n"
     "and carry none of its weight."),
    (T, "| **{{v2_diag_h}}** *(pre-registered)* |", "| **{{v2_diag_h}}** *(the rule's horizon)* |"),
    (T, "**Only the h = {{v2_diag_h}} row is pre-registered.** Every other row was computed after the data existed, "
        "so by this paper's own standard (§8) it carries none of a pre-registration's weight, the same treatment §6.7 "
        "gives the expectation we held about the counter-baseline, and nothing in the table discharges or re-opens the rule.",
     "**Only the h = {{v2_diag_h}} row is the rule's horizon, and the rule ran on seed {{m23_seed}} alone.** Every\n"
     "value in the table is a three-seed mean computed after the data existed, so by this paper's own standard (§8)\n"
     "none carries a pre-registration's weight, the same treatment §6.7 gives the expectation we held about the\n"
     "counter-baseline, and nothing in the table discharges or re-opens the rule."),
    (T, "The headline A/B result is not among them: it is a three-seed mean with per-seed values reported (§5).",
     "The headline A/B verdict rests on one seed too, seed {{m23_seed}}, the one its rule ran on; the magnitudes\n"
     "beside it are three-seed means with per-seed values (§5)."),
    (T, "The base paper's central training claim reproduces under a rule committed in advance: training on the "
        "model's own rollouts beats teacher forcing by {{d1_ratio}}× at {{v2_diag_h}} steps and {{d1_ratio_h100}}× "
        "at {{v2_deploy_h}}, though teacher forcing leads at one step.",
     "The base paper's central training claim reproduces under a rule committed in advance and run on one seed\n"
     "per arm; over {{d1_seeds}} seeds, training on the model's own rollouts beats teacher forcing by {{d1_ratio}}× at\n"
     "{{v2_diag_h}} steps and {{d1_ratio_h100}}× at {{v2_deploy_h}}, though teacher forcing leads at one step."),
    (T, "- **The base paper's central training claim reproduces, and reverses at one step.** Under a rule committed "
        "before the runs, training on the model's own rollouts beats teacher forcing, by {{d1_ratio}}× on relative-L1 "
        "at h = {{v2_diag_h}} over {{d1_seeds}} seeds and by {{d1_ratio_h100}}× at h = {{v2_deploy_h}} (§5). At one "
        "step, a second pre-registered rule with {{m64_h1_n}} independent {{m64_h1_unit}}-row units, where the 400-step "
        "unit gives {{a1_nind}}, finds a gap of {{m64_h1_gap}} {{m64_h1_ci}}, in favour of **teacher forcing** (§5).",
     "- **The base paper's central training claim reproduces, and reverses at one step.** A rule committed before\n"
     "  the runs, run on one seed per arm, found autoregressive training ahead by {{m23_ratio}}× at\n"
     "  h = {{v2_diag_h}}; over {{d1_seeds}} seeds the factor is {{d1_ratio}}×, and {{d1_ratio_h100}}× at\n"
     "  h = {{v2_deploy_h}} (§5). At one step a second pre-registered rule, on {{m64_h1_n}} independent\n"
     "  {{m64_h1_unit}}-row units, finds a gap of {{m64_h1_gap}} {{m64_h1_ci}} in favour of **teacher forcing** (§5)."),
    ("scripts/build_paper.py", '"(\\\\S5, M-64). Only the h = 368 figure is pre-registered (M-23); the rest were "\n'
                               '            "computed after the data existed.",',
     '"(\\\\S5, M-64). Rule M-23 was run at h = 368 on seed " + str(N["m23_seed"]["value"])\n'
     '            + " of each arm; these three-seed values, and every other horizon, were computed afterwards.",'),
]

E5 = [
    (T, "a factor of **{{d1_ratio}}×**. At h = {{v2_deploy_h}}, the method's own imagination rollout length",
     "a factor of **{{d1_ratio}}×**. Arm B predicts each of the window's {{win_fore}} forecast targets from\n"
     "true inputs, where the original's teacher forcing is N = 1; the sweep's {{mn_n1_label}}, trained that way, is\n"
     "{{mn_tf_ratio}}× worse than the centre at h = {{v2_diag_h}} (§5.2), so the claim holds under both definitions.\n"
     "At h = {{v2_deploy_h}}, the method's own imagination rollout length"),
    (T, "Our {{d1_ratio}}× compares Arm B, which trains on {{win_fore}} teacher-forced targets per window rather than "
        "one (`docs/presubmission/ORIGINAL_SPECS.md` §2), so it neither confirms nor contradicts that figure.",
     "Our {{d1_ratio}}× uses a different definition of teacher forcing\n"
     "(`docs/presubmission/ORIGINAL_SPECS.md` §2); §5 relates the two."),
]

ITEMS = {"e1": E1, "e4": E4, "e5": E5}
edits = ITEMS[sys.argv[1]]
texts = {}
for f, old, new in edits:
    t = texts.setdefault(f, open(f, encoding="utf-8").read())
    n = len(pat(old).findall(t))
    assert n == 1, f"{f}: {old[:70]!r} matches {n} times"
for f, old, new in edits:
    texts[f] = pat(old).sub(lambda m: new, texts[f], count=1)
for f, t in texts.items():
    shutil.copy(f, f + ".bak")
    open(f, "w", encoding="utf-8").write(t)
    print(subprocess.run(["diff", f + ".bak", f], capture_output=True, text=True).stdout)
    os.remove(f + ".bak")
print(f"applied {len(edits)} edits ({sys.argv[1]}) to {len(texts)} files")
