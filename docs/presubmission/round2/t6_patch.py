"""Round 2, T6: move detail out of the body (PLAN T6/T7, ruling U3), one item at a time.

A `move` cuts a block from PAPER.template.md VERBATIM, from the line that starts with `start` up to (not
including) the line that starts with `end`, puts `summary` in its place, and appends the block to the end of
the template under a new appendix heading (move, never delete: PLAN 1.2.9). A `sub` is a whitespace-tolerant
replacement asserted to match exactly once. Nothing is written before every assert passes; a .bak is kept.
Usage: t6_patch.py ITEM [ITEM ...]"""
import re
import shutil
import sys

F = "PAPER.template.md"
ITEMS = {}


def pat(old):
    return re.compile(r"\s+".join(re.escape(w) for w in old.split()))


# ---- §2: the PETS lineage and the survey of public descendants -> Appendix I -----------------------
ITEMS["s2_pets"] = [("move",
    "**Where the parameterisation comes from.**", "**The method's family.**",
    """**Where the parameterisation comes from.** The bounded log-σ head whose optimum §6.3 shows is
σ = 0 is inherited, line for line, from the probabilistic ensembles of Chua, Calandra, McAllister
and Levine (PETS, NeurIPS 2018), but the objective is not: the released code replaces PETS's
likelihood with squared error on a sampled prediction and ties the upper bound to the floor, so
**a descendant of this lineage that made the same substitution, and left nothing pushing its
variance floor back up, would inherit the same optimum**, a hypothesis about mechanism untested in
any other descendant (§11). Of {{q1_n_examined}} public repositories examined, {{q1_n_carry}} carry
the construction and {{q1_n_inherit}} of those trains it against a sampled squared error, only in
an optional mode, so on this sample of convenience the substitution is rare (Appendix I).

""",
    "## Appendix I — the PETS lineage of the bounded σ head, and how often its descendants substitute the objective")]


def main():
    t = open(F).read()
    for it in sys.argv[1:]:
        for op in ITEMS[it]:
            if op[0] == "sub":
                _, old, new = op
                n = len(pat(old).findall(t))
                assert n == 1, f"{it}: {n} matches for {old[:60]!r}"
                t = pat(old).sub(lambda _: new, t, count=1)
            elif op[0] == "move":
                _, start, end, summary, heading = op
                L = t.split("\n")
                si = [i for i, x in enumerate(L) if x.startswith(start)]
                assert len(si) == 1, f"{it}: start {start!r} found {len(si)} times"
                ei = [i for i, x in enumerate(L) if x.startswith(end) and i > si[0]]
                assert ei, f"{it}: end {end!r} not found after start"
                block = "\n".join(L[si[0]:ei[0]]).strip("\n")
                assert heading not in t, f"{it}: {heading[:40]!r} already present"
                assert t.rstrip().endswith("---"), "the template no longer ends with an appendix rule"
                t = "\n".join(L[:si[0]]) + "\n" + summary + "\n".join(L[ei[0]:])
                t = t.rstrip("\n") + "\n\n" + heading + "\n\n" + block + "\n\n---\n"
            else:
                raise ValueError(op[0])
    shutil.copy(F, F + ".bak")
    open(F, "w").write(t)
    print("patched", F, sys.argv[1:])


if __name__ == "__main__":
    main()
