"""Round 2, T7: move detail out of §6.7–§12 (PLAN T6/T7, ruling U3), one item at a time.

Reuses round2/t6_patch.py's operations: `move` (a block cut verbatim to a new or existing appendix, a
summary left in its place), `sub` (whitespace-tolerant, exactly one match), `insert` and `append` (verbatim
text cut by a preceding `sub`, placed in a named appendix). Nothing is written before every assert passes.
Usage: t7_patch.py ITEM [ITEM ...]"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import t6_patch as E  # noqa: E402

E.ITEMS.clear()
ITEMS = E.ITEMS

# ---- §6.7: the robustness checks of the ranking claim -> Appendix N --------------------------------------
_N = "## Appendix N — section 6.7's robustness checks: depth controls, the decomposition, rule M-43, and the within-step control"
ITEMS["s67_robust"] = [
    ("move", "**What survives removing each confound.**", "**Per horizon, on the same",
     """**What survives removing each confound** (Appendix N). Across {{d2r_ncontrols}} models of how far
into the rollout a step is, the weakest figure is {{d2r_weakest}}, so disagreement is not
re-encoding the clock; but the pooled figure is in large part a between-rollout effect, so the
statistic that matters holds both the rollout and the depth constant. Pre-registered as rule M-45,
it gives {{a2_rdd}} {{a2_rdd_ci}} at n_independent = {{a2_nind}} 400-step trajectories, and the rule returns
**{{m45_verdict}}**: disagreement still tracks error rather than merely reporting which episode is
hard.

""", _N),
    ("move", "Two qualifications go with that.", "**Does it hold on a model we trained?**",
     """The within-rollout effect is materially smaller than the pooled figure and not established at short
horizon; at h = 1 the correlation ranks whole rollouts, on {{a2_h1_npoints}} trajectory-level points
(Appendix N).

""", _N),
    ("move", "**Does it hold on a model we trained?**", "**We ran the baseline test expecting it to go the other way.**",
     """**Does it hold on a model we trained?** Three Arm A arms at ensemble size 5, under a rule
committed before the runs (rule M-43, Appendix E), lead the index in **{{e5_lead_cells}} of
{{e5_total_cells}}** seed-horizon cells, but the paired difference excludes zero at only
{{e5_n_excl}} of {{e5_n_horizons}} horizons, so the rule returns **{{e5_verdict}}**. At
n_independent = {{e5_nind}} 400-step trajectories it was under-powered, which we measured after the fact and should have
checked before committing it (Appendix N).

""", _N),
    ("move", "*A note on the `undefined` cell.*", "### 6.8 ", "", _N),
    # relative references in the moved text now name §6.7
    ("sub", "part of what this section reports is a between-rollout effect.", "part of what §6.7 reports is a between-rollout effect."),
    ("sub", "**Does it hold on a model we trained?** Everything above is measured on the released checkpoint,",
     "**Does it hold on a model we trained?** Everything else in §6.7 is measured on the released checkpoint,"),
    ("sub", "The released checkpoint's table above follows the six-horizon", "§6.7's released-checkpoint table follows the six-horizon"),
    ("sub", "*A note on the `undefined` cell.*", "*A note on the `undefined` cell in §6.7's table of free baselines.*"),
]

if __name__ == "__main__":
    E.main()
