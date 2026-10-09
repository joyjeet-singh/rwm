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
