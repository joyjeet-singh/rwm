"""R5: the template edits (PLAN round 3, R5). The matcher, the exactly-once assertions and the .bak discipline are
r2_patch.py's, imported. Usage, from the repository root:  $PY docs/presubmission/round3/r5_patch.py <item>
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r2_patch import apply  # noqa: E402

T = "PAPER.template.md"
BAK = "/Users/Shared/rwm_verify/evidence/R3R5"
ITEMS = {
    # H4: Appendix B's runtime table gains rule X1's Part C runs; the prose says where they are counted
    "h4": {"edits": [(
        "the artifact lists each overlap. Per run family, every run at {{iters_main}} iterations",
        "the artifact lists each overlap. Rule X1's Part C (§5.3) ran {{rt_x1c_runs}} more teacher-forced RSSM "
        "runs from a second queue, {{rt_x1c_hours}} hours, which are in neither total; {{rt_x1c_overlapped}} of "
        "them overlapped CPU work a session logged. They are the table's last rows. Per run family, every run at "
        "{{iters_main}} iterations")]},
}

if __name__ == "__main__":
    item = sys.argv[1]
    text = open(T, encoding="utf-8").read()
    new = apply(text, ITEMS[item]["edits"])          # asserts each match exactly once before anything is written
    shutil.copy(T, f"{BAK}/PAPER.template.md.{item}.bak")
    open(T, "w", encoding="utf-8").write(new)
    print(f"{item}: {len(ITEMS[item]['edits'])} edit(s) applied; backup {BAK}/PAPER.template.md.{item}.bak")
