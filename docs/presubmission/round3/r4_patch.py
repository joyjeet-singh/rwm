"""R4: the template edits for the small items, one item at a time (PLAN round 3, R4, S1-S17).

The matcher, the exactly-once assertions and the .bak discipline are r2_patch.py's, imported. Usage, from the
repository root:  $PY docs/presubmission/round3/r4_patch.py <item>
"""
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r2_patch import apply, insert_after  # noqa: E402

T = "PAPER.template.md"
BAK = "/Users/Shared/rwm_verify/evidence/R3R4"
ITEMS = {
    # S4: the introduction understated the negative verdicts
    "s4": {"edits": [("one returned \"cannot be settled\", and we report it.",
                      "several returned verdicts against the original or could not settle the question, and we "
                      "report each (Appendix E).")]},
    # S7: Appendix F said the same thing twice; one paragraph, nothing dropped (the pointer to the supplementary
    # arithmetic is already in the appendix's first paragraph)
    "s7": {"edits": [(
        "We report the arithmetic because it is what let us detect the gap at all, not as a charge against the work. "
        "**§7.5's argument in full.** The σ collapse is linear in iteration count and its rate is nearly identical "
        "across our runs (§6.3), which makes it a clock, and read as a clock it puts the checkpoint's variance state "
        "out of reach of a constant-rate run from the released initialisation at the configured learning rate, at "
        "every iteration count the release, the paper and the checkpoint tag state. The first author's account is that "
        "the released repository is several revisions removed from the setup that trained the checkpoint, which "
        "supplies a mechanism, a warm start or a different `log_delta_logstd` initialisation, that would explain it "
        "with no inconsistency at all. So this is a **documentation gap between a release and a run**: common, worth "
        "recording, and much less interesting than an inconsistency. `docs/APPENDIX_G_VARIANCE_ARITHMETIC.md`, shipped "
        "as supplementary, gives the arithmetic and the five assumptions it rests on.",
        "The σ collapse is linear in iteration count and its rate is nearly identical across our runs (§6.3), which "
        "makes it a clock, and read as a clock it puts the checkpoint's variance state out of reach of a constant-rate "
        "run from the released initialisation at the configured learning rate, at every iteration count the release, "
        "the paper and the checkpoint tag state. The first author's account is that the released repository is several "
        "revisions removed from the setup that trained the checkpoint, which supplies a mechanism, a warm start or a "
        "different `log_delta_logstd` initialisation, that would explain it with no inconsistency at all. We report the "
        "arithmetic because it is what let us detect the gap at all, not as a charge against the work."),
        ("That is a documentation gap between a release and a run — common, worth recording, and much less "
         "interesting than an inconsistency.",
         "That is a **documentation gap between a release and a run**: common, worth recording, and much less "
         "interesting than an inconsistency.")]},
    # S9: Appendix E's M-69 note, two sentences: the two timestamps, and that both are positive
    "s9": {"edits": [(
        "`M-69`'s discharge commit was amended {{m69_amend_min}} minutes after it was created, so the rule's lead time "
        "depends on which timestamp is read: {{m69_lead_author}} by that commit's author time, {{m69_lead_regen}} by its "
        "committer time. The table above renders {{m69_lead_pub}}, the value `results/appendix_g_rules.json` holds; a "
        "clean rebuild regenerates that file from git and may store either reading. Both readings are positive, so the "
        "rule reached git before the data that tested it existed on either one, which is what a lead time is here to "
        "establish.",
        "`M-69`'s discharge commit was amended {{m69_amend_min}} minutes after it was created, so its lead time is "
        "{{m69_lead_author}} by that commit's author time and {{m69_lead_regen}} by its committer time. Both are "
        "positive, so the rule reached git before its data on either reading.")]},
    # S10: 8 episodes have 7 internal boundaries; the subtraction is one row per episode
    "s10": {"edits": [("less one per episode boundary ({{c2_bounds}} of them),",
                       "less one per episode ({{c2_bounds}} of them), since an episode's first row has no "
                       "predecessor,")]},
    # S11: several long-horizon verdicts are "not resolved"; the bootstrap computes them, it does not pass them
    "s11": {"edits": [("Every long-horizon verdict in this paper survives a bootstrap over independent trajectories,",
                       "Every long-horizon verdict in this paper is computed with a bootstrap over independent "
                       "trajectories,")]},
    # S16: the orphaned bold line joins the paragraph it concludes
    "s16": {"edits": [("once the dependence between dimensions is respected.** **The failure is specifically "
                       "magnitude calibration, in both components.**",
                       "once the dependence between dimensions is respected. The failure is specifically magnitude "
                       "calibration, in both components.**")]},
    # S5: the main text's one commit identifier (rule M-23's), glossed where it appears. PAPER.md keeps the real hash
    # and the submitted PDF prints its anonymous label, so the gloss is worded to be true in both renderings, and points
    # to the unnumbered "Data and code" section by name.
    "s5": {"edits": [("(rule M-23, Appendix E; commit `efc35b8`)",
                      "(rule M-23, Appendix E; commit `efc35b8`, in the submitted paper an anonymised commit label; "
                      "see Data and code)")]},
}


def run(item):
    spec = ITEMS[item]
    text = open(T, encoding="utf-8").read()
    new = apply(text, spec.get("edits", []))
    for anchor, add in spec.get("inserts", []):
        new = insert_after(new, anchor, add)
    if spec.get("append_before_final_rule"):
        assert new.rstrip().endswith("\n---"), new[-40:]
        new = new.rstrip()[:-3].rstrip("\n") + "\n" + spec["append_before_final_rule"] + "\n---\n"
    kb = set(re.findall(r"\{\{([A-Za-z0-9_]+)\}\}", text))
    ka = set(re.findall(r"\{\{([A-Za-z0-9_]+)\}\}", new))
    os.makedirs(BAK, exist_ok=True)
    shutil.copy(T, f"{BAK}/PAPER.template.md.{item}.bak")
    open(T, "w", encoding="utf-8").write(new)
    print(f"{item}: keys removed {sorted(kb - ka)}; added {sorted(ka - kb)}")
    subprocess.run(["git", "--no-pager", "diff", "--stat", T])


if __name__ == "__main__":
    for it in sys.argv[1:]:
        run(it)
