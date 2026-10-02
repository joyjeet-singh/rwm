"""Round 2, T7: the length review's fixes (evidence R2T7/t7_review.md). Whitespace-tolerant, each match
asserted exactly once, nothing written before every assert passes, a .bak beside each file."""
import re
import shutil

EDITS = {"PAPER.template.md": [
# R1: the roadmap's range, collapsed by the renumbering
("§6.3–§6.3 examine why each output fails;", "§6.3–§6.4 examine why each output fails;"),
# R2: Appendix N's heading (the renumbering matched only "§")
("## Appendix N — section 6.7's robustness checks:", "## Appendix N — section 6.6's robustness checks:"),
# R3: §12, the qualifier restored
("""and per dimension no ordering reaches significance once the coupling between
dimensions is respected (§6.5).""",
 """and per dimension no ordering reaches significance after multiplicity correction once the
coupling between dimensions is respected (§6.5)."""),
# R4: §11, not every rule was committed before its data (S-12)
("""each committed before its data and
reported against its own thresholds;""",
 """each reported against the thresholds it was committed with (one, `S-12`, is withdrawn as a
pre-registration because it reached git after its data, §8);"""),
# R5: §11, the hypothesis's second condition restored
("""hypothesis is well-founded only for one that makes the same substitution, and is untested for any""",
 """hypothesis is well-founded only for one that makes the same substitution and leaves nothing pushing
its floor back up, and is untested for any"""),
# R6: §6.8, M-49's verdict with its figure
("""at matched capacity the improvement falls to {{m49_ratio_gain}}× (rule M-49,
§11).""",
 """at matched capacity the improvement falls to {{m49_ratio_gain}}× against a minimum detectable effect
of {{m49_mde_ratio}}×, so that rule returns **{{m49_verdict_short}}** (rule M-49, §11)."""),
# R7: §6.8, the multiplier's qualifier restored
("""estimates all land within the band, and only on the released checkpoint.""",
 """estimates all land within the band, though only on the released checkpoint and with no single cell
resolvable at this arena."""),
# R8: §6.5, the larger arena is now quoted in Appendix S
("§12 quotes the larger arena.", "Appendix S quotes the larger arena."),
# R9: §6.6, the pooled interval is now in Appendix N
("as the pooled interval above does from §6.2's {{d4_ci}}.", "as Appendix N's pooled interval does from §6.2's {{d4_ci}}."),
# R11: §11, the per-dimension power limit's scope
("""**The per-dimension ordering tests are underpowered at every sample size we can reach** (§6.5,
Appendix K).""",
 """**The per-dimension ordering tests are underpowered at every sample size we can reach** at
h = {{v2_diag_h}} (§6.5, Appendix K); at h = 128 and below a shorter unit would raise the count, a
rerun we did not do."""),
# R12: §6.8, "do not add" as Appendix P bounds it
("""**The two fixes do not add**, and once stated that is no surprise: the objective governs the
aleatoric head,""",
 """**The two fixes do not add**: the objective's separate contribution is at most small, which the
design can bound but not establish as zero. Once stated that is no surprise: the objective governs
the aleatoric head,"""),
# R13: §7.4 and §7.5
("""and in rollout it is hurt in {{tw_cc_cluster_hurt}} of {{tw_cells}} cells and helped""",
 """and in rollout, over {{tw_cells}} cells ({{tw_design}}), it is hurt in {{tw_cc_cluster_hurt}} and helped"""),
("""puts the checkpoint's variance state out of reach of a constant-rate run
from the released initialisation at every iteration count""",
 """puts the checkpoint's variance state out of reach of a constant-rate run
from the released initialisation at the configured learning rate, at every iteration count"""),
# R14: references in moved text and in the kept caption
("""§6.4 establishes the topology as a fact and the mechanism as a hypothesis. This subsection tests
the hypothesis, under a rule""",
 """§6.4 establishes the topology as a fact and the mechanism as a hypothesis. Rule M-44 tests
the hypothesis, under a rule"""),
("""This subsection
runs the combination, under a rule""", """Rule M-68
runs the combination, under a rule"""),
("*The same σ-versus-accuracy split §6.8 uses,", "*The same σ-versus-accuracy split Appendix O uses for rule M-44,"),
("same bootstrap unit as §6.8, every model", "same bootstrap unit as the table above, every model"),
("*A note on the `undefined` cell in §6.6's table of free baselines.*",
 "*Why the within-step control is undefined for the forecast index.*"),
# R16: M-69's cells are not independent tests; §12's margin is unresolved
("""the arena can resolve: {{d3x_n_out}} of {{d3x_ncells}} governing cells have an interval wholly outside""",
 """the arena can resolve: {{d3x_n_out}} of {{d3x_ncells}} governing cells, which are not independent tests, have an interval wholly outside"""),
("""predicted step size, ranks error nearly as well ({{e7_verdict}}).""",
 """predicted step size, ranks error nearly as well, by a margin this sample cannot resolve
({{e7_verdict}})."""),
], "docs/BUILD_CHECKS.template.md": [
# R15: historical notes on the ranking section
("""the same damage in section 6.7, where""", """the same damage in the ranking section (now 6.6), where"""),
("""in a table cell of section 6.7 and its definition""", """in a table cell of the ranking section (now 6.6) and its definition"""),
], "docs/presubmission/round2/t7_patch.py": [
("_N = \"## Appendix N — section 6.7's robustness checks:", "_N = \"## Appendix N — section 6.6's robustness checks:"),
]}


def main():
    plan = {}
    for f, edits in EDITS.items():
        t = open(f).read()
        for old, new in edits:
            p = re.compile(r"\s+".join(re.escape(w) for w in old.split()))
            n = len(p.findall(t))
            assert n == 1, f"{f}: {n} matches for {old[:70]!r}"
            t = p.sub(lambda _: new, t, count=1)
        plan[f] = t
    for f, t in plan.items():
        shutil.copy(f, f + ".bak")
        open(f, "w").write(t)
        print("patched", f)


if __name__ == "__main__":
    main()
