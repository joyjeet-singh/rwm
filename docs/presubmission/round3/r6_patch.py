"""R6: the template edits (PLAN round 3, R6). The matcher, the exactly-once assertions and the .bak discipline are
r2_patch.py's, imported. Usage, from the repository root:  $PY docs/presubmission/round3/r6_patch.py <item>
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r2_patch import apply, insert_after  # noqa: E402

T = "PAPER.template.md"
BAK = "/Users/Shared/rwm_verify/evidence/R3R6"
TABLE = ("| claim (§) | arena (n_independent) | checkpoint | in-sample for the model measured? | verdict | "
         "survives multiplicity correction? |\n|---|---|---|---|---|---|\n{{evidence_table}}")
ITEMS = {
    # Item 1, ruling V5: §3.2's table becomes Appendix D's second table; §3.2 keeps its paragraph and a pointer.
    "1": {"edits": [(
        "number of training iterations. The table is generated from the artifacts each claim is computed from, so "
        "no arena label, sample size or checkpoint in it is typed by hand. " + TABLE,
        "number of training iterations. Appendix D's second table, \"What each tested claim rests on\", gives each "
        "claim's arena, sample size, checkpoint and verdict. It is generated from the artifacts each claim is "
        "computed from, so no arena label, sample size or checkpoint in it is typed by hand."),
        ("The body's §4 summarises this table. It is here in full",
         "The body's §4 summarises the first table. It is here in full")],
        "after": [(
            "Our findings bound what the quantity *reports*, not what it *costs* (§11) |",
            "\n\n**What each tested claim rests on.** The second table is §3.2's: one row per headline claim of this "
            "paper, with the section that owns it. Each row gives its own arena and number of independent units, its "
            "checkpoint, whether that arena is in-sample for the model measured, the verdict as its rule or analysis "
            "returned it, and whether it survives multiplicity correction. It is generated from the artifacts each "
            "claim is computed from (`results/evidence_summary.json`).\n\n" + TABLE)]},
    # Item 3, rule 10: front-matter wording, each made to say what every reading the body reports says
    # (round3/CONSISTENCY.md gives the readings row by row).
    "3": {"edits": [
        # Abstract: the one-step reading is resolved on M-64's short units only; the configuration verdict holds on
        # every reading the rule reports but one, unresolved; the alignment rise is relative-L1's. Words cut to stay
        # inside C12.1's budget: "proprioceptive", "from scratch", "here", "Separately", and "so" (a colon).
        ("We rebuild the proprioceptive dynamics model", "We rebuild the dynamics model"),
        ("(arXiv:2504.16680v1) from scratch on CPU,", "(arXiv:2504.16680v1) on CPU,"),
        ("{{d1_ratio_h100}}× at {{v2_deploy_h}}, though teacher forcing leads at one step.",
         "{{d1_ratio_h100}}× at {{v2_deploy_h}}, though on short windows teacher forcing leads at one step."),
        ("beat the original's setting at our budget; trained longer, it passes each on some reading (post hoc), so the "
         "ranking depends on training budget. Its trade-off with training time is untested here.",
         "beat the original's setting at our budget ({{mn_fm_n_unres_word}} reading unresolved); trained longer, it "
         "passes each on some reading (post hoc): the ranking depends on training budget. Its trade-off with training "
         "time is untested."),
        ("Separately, the released evaluation pairs each prediction with the previous step's action; over all ten "
         "episodes this raises the checkpoint's short-horizon error,",
         "The released evaluation pairs each prediction with the previous step's action; over all ten episodes this "
         "raises the checkpoint's short-horizon relative-L1 error,"),
        # Contribution 3: the configuration verdict's one unresolved reading
        ("{{mn_n_short_better_word}} shorter histories at under half its cost per iteration and "
         "{{mn_better_long_phrase}} at more, but trained longer",
         "{{mn_n_short_better_word}} shorter histories at under half its cost per iteration and "
         "{{mn_better_long_phrase}} at more (every reading its rule reports returns that verdict but "
         "{{mn_fm_exception}}, which is unresolved), but trained longer"),
        # Section 9: the two overconfidence factors are from different arenas; name both
        ("{{d1n_epi_ratio_h100}}× [{{d1n_epi_ratio_ci_h100}}] on the released checkpoint and {{e5_ratio_h100}}× "
         "[{{e5_ratio_ci_h100}}] on the ensemble-5 arms we trained.",
         "{{d1n_epi_ratio_h100}}× [{{d1n_epi_ratio_ci_h100}}] on the released checkpoint over all ten episodes, and on "
         "the held-out pair {{e5_ratio_h100}}× [{{e5_ratio_ci_h100}}] on the ensemble-5 arms we trained against its "
         "{{b2_epi_ratio_h100}}×."),
        # Section 12: the one-step reading, and the configuration verdict's unresolved reading
        ("large there, though teacher forcing leads at one step. RWM is",
         "large there, though on the short windows built for one step teacher forcing leads there. RWM is"),
        ("beat its chosen ones at our budget, a ranking that changes",
         "beat its chosen ones at our budget, on every reading the rule reports but one, which is unresolved, a "
         "ranking that changes"),
        # Appendix D, the originals' claims: Arm B and the floor depend on the unit; the configuration verdict's
        # unresolved reading; the baselines' verdicts are the rules' at h = 368, and the readings split below.
        ("reproduces, and more strongly: Arm B is worse than the hold-last floor, and",
         "reproduces, and more strongly: on the 400-step unit Arm B is worse than the hold-last floor at every "
         "horizon (on M-64's shorter units only at the longest they reach), and"),
        ("{{mn_better_list}} beat it at our budget, but the ranking depends on training length:",
         "{{mn_better_list}} beat it at our budget (every reading its rule reports returns that verdict but "
         "{{mn_fm_exception}}, which is unresolved), but the ranking depends on training length:"),
        ("which compares architectures at one training regime rather than testing this claim (§5.3).",
         "which compares architectures at one training regime rather than testing this claim (§5.3). Both are "
         "the rules' verdicts at h = {{v2_diag_h}}; every reading the rules report returns them from h = "
         "{{bl_tf_from_h}} and h = {{bl_ar_from_h}} respectively, and at shorter horizons the readings split."),
    ]},
    # Item 3, wording of item 3's own insertions: the qualifier attaches to the rule's verdict, as section 5.2 attaches
    # it, and section 12's one-step clause reads in order.
    "3b": {"edits": [
        ("{{mn_better_long_phrase}} at more (every reading its rule reports returns that verdict but "
         "{{mn_fm_exception}}, which is unresolved), but trained longer",
         "{{mn_better_long_phrase}} at more (the rule's verdict holds on every reading it reports but "
         "{{mn_fm_exception}}, which is unresolved), but trained longer"),
        ("though on the short windows built for one step teacher forcing leads there. RWM is",
         "though teacher forcing leads at one step on the short windows built for it. RWM is"),
        ("beat its chosen ones at our budget, on every reading the rule reports but one, which is unresolved, a "
         "ranking that changes",
         "beat its chosen ones at our budget, a verdict every reading the rule reports returns but one, which is "
         "unresolved, and a ranking that changes"),
    ]},
    # Item 3: the baselines sentence shared two generic words with X2's sentence in section 7.2, so the restatement
    # check read X2's typed "h = 8" as a stale copy of {{bl_tf_from_h}}; the same statement, worded without them.
    "3c": {"edits": [
        ("Both are the rules' verdicts at h = {{v2_diag_h}}; every reading the rules report returns them from h = "
         "{{bl_tf_from_h}} and h = {{bl_ar_from_h}} respectively, and at shorter horizons the readings split.",
         "Both are the rules' verdicts at h = {{v2_diag_h}}; from h = {{bl_tf_from_h}} and h = {{bl_ar_from_h}} "
         "respectively, every reading the rules report gives them, and at shorter horizons they split."),
    ]},
    # Item 3: section 9's "its" could be read as the arms'; name the checkpoint.
    "3d": {"edits": [
        ("on the ensemble-5 arms we trained against its {{b2_epi_ratio_h100}}×.",
         "on the ensemble-5 arms we trained, against the released checkpoint's {{b2_epi_ratio_h100}}× there."),
    ]},
}

if __name__ == "__main__":
    item = sys.argv[1]
    os.makedirs(BAK, exist_ok=True)
    text = open(T, encoding="utf-8").read()
    new = apply(text, ITEMS[item].get("edits", []))      # asserts each match exactly once before anything is written
    for anchor, addition in ITEMS[item].get("after", []):
        new = insert_after(new, anchor, addition)
    shutil.copy(T, f"{BAK}/PAPER.template.md.{item}.bak")
    open(T, "w", encoding="utf-8").write(new)
    print(f"item {item}: applied; backup {BAK}/PAPER.template.md.{item}.bak")
