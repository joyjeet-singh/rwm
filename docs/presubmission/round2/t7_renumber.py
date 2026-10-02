"""Round 2, T7: renumber §6 once, after the merges (ruling U6: merge or move within §6 only; renumber with a
pointer map; top-level numbers stay).

Old -> new. §6.5 folded into §6.3, §6.9 into §6.6 (now §6.5), §6.11 into §6.10 (now §6.8):
  6.5 -> 6.3   6.6 -> 6.5   6.7 -> 6.6   6.8 -> 6.7   6.9 -> 6.5   6.10 -> 6.8   6.11 -> 6.8
One simultaneous substitution per file, so no number is rewritten twice. What is renumbered: the paper's
headings and every §6.N reference in the reader-facing sources; the section keys §3.2's generator uses; the
model card's references; the captions' \\S6.N; and the comparative-claims checker's `where` labels. What is
not: the ledger and the rule texts quoted from it (quotations, which docs/APPENDIX_G_RULES.md says), code
comments and the scripts of analyses already run (historical). The pointer map goes into the supplementary
docs/BUILD_CHECKS.md and the preamble of docs/APPENDIX_G_RULES.md."""
import re
import shutil

MAP = {"6.5": "6.3", "6.6": "6.5", "6.7": "6.6", "6.8": "6.7", "6.9": "6.5", "6.10": "6.8", "6.11": "6.8"}
HEAD = {"6.6": "6.5", "6.7": "6.6", "6.8": "6.7", "6.10": "6.8"}     # headings that still exist
NUM = r"6\.(?:1[01]|[5-9])(?![\d])"


def sub_refs(t, prefix):
    return re.sub(prefix + "(" + NUM + ")", lambda m: m.group(0)[:-len(m.group(1))] + MAP[m.group(1)], t)


def paper(t):
    t = re.sub(r"^### (6\.(?:10|[678])) ", lambda m: f"### {HEAD[m.group(1)]} ", t, flags=re.M)
    return sub_refs(t, "§")


EDITS = {
    "PAPER.template.md": paper,
    "README.template.md": lambda t: sub_refs(t, "§"),
    "docs/BUILD_CHECKS.template.md": lambda t: sub_refs(t, "§"),
    "docs/EXTERNAL_READ_BRIEF.md": lambda t: sub_refs(t, "§"),
    "scripts/build_model_card.py": lambda t: sub_refs(t, "§"),
    "scripts/build_paper.py": lambda t: re.sub(r'(\\\\S)(' + NUM + ')', lambda m: m.group(1) + MAP[m.group(2)], t),
    "scripts/evidence_summary.py": lambda t: re.sub(r'("section": ")(' + NUM + ')(")', lambda m: m.group(1) + MAP[m.group(2)] + m.group(3), t),
    "scripts/check_comparative_claims.py": lambda t: re.sub(r'("where": "[^"]*")',
        lambda m: re.sub(r"(?<![\d.])(" + NUM + ")", lambda k: MAP[k.group(1)], m.group(1)), t),
}

POINTER_MAP = ("§6.5 → §6.3 (folded in), §6.6 → §6.5, §6.7 → §6.6, §6.8 → §6.7, §6.9 → §6.5 (folded in), "
               "§6.10 → §6.8, §6.11 → §6.8 (merged; the detail of both rules is in Appendices O and P)")


def main():
    plan = {}
    for f, fn in EDITS.items():
        t = open(f).read()
        n = fn(t)
        plan[f] = n
        print(f"  {f}: {sum(1 for a, b in zip(t.split(chr(10)), n.split(chr(10))) if a != b)} lines changed")
    # the pointer map, in the two supplementary documents that quote or describe the old numbering
    b = plan["docs/BUILD_CHECKS.template.md"]
    anchor = "## Moved from the paper body (pre-submission edit)"
    assert b.count(anchor) == 1
    plan["docs/BUILD_CHECKS.template.md"] = b.replace(anchor,
        "## Section numbers before round 2 (ruling U6)\n\nRound 2 merged three subsections of §6 and renumbered it; "
        "§1–§5 and §7 onward are unchanged. The ledger, the rule texts in `docs/APPENDIX_G_RULES.md` and every "
        "document written before round 2 use the old numbers. Old → new: " + POINTER_MAP + ".\n\n" + anchor)
    g = open("scripts/appendix_g_rules.py").read()
    o = ('"governs \\"the within-trajectory control on section 5.6\\", which is now "\n'
         '                 "section 6.7. Renumbering a quotation')
    assert g.count(o) == 1, "appendix_g_rules preamble"
    g = g.replace(o, '"governs \\"the within-trajectory control on section 5.6\\", which is now "\n'
                     '                 "section 6.6. Round 2 renumbered section 6 (old → new: ' + POINTER_MAP.replace('"', '\\"') + '). Renumbering a quotation')
    g = g.replace("M-45\n        # reads \"the within-trajectory control on §5.6\", which is now §6.7", "M-45\n        # reads \"the within-trajectory control on §5.6\", which is now §6.6")
    plan["scripts/appendix_g_rules.py"] = g
    for f, t in plan.items():
        shutil.copy(f, f + ".bak")
        open(f, "w").write(t)
    print("renumbered")


if __name__ == "__main__":
    main()
