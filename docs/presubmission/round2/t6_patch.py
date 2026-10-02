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

# ---- §6.3: the synthetic-noise experiment (rule M-50) -> Appendix J -------------------------------------
ITEMS["s63_noise"] = [("move",
    "**The derivation says the collapse happens on any dataset, and that is testable.**",
    "We predicted the collapse from this algebra",
    """**The derivation says the collapse happens on any dataset, and that is testable.** On the
released data, "small stochasticity in the environment" and our reading are observationally
identical, so under a rule committed before the runs (rule M-50, Appendix E) we trained the released
head, unmodified, on synthetic data whose known noise varies {{e5s_span}}× across the input range.
**Under the implemented objective σ sits {{e5s_mse_under}}× below the true noise and does not track
it at all**, while under the authors' unused likelihood branch, same data and same head, it recovers
the true level to a median ratio of {{e5s_nll_ratio}}, seed-variably. The rule returns
**{{e5s_verdict}}**: the experiment establishes the contrast, not the size of the recovery
(Appendix J).

""",
    "## Appendix J — the synthetic-noise test of the σ = 0 optimum (rule M-50)"),
    # the pointer "§6.3 explains the aleatoric column and leaves the epistemic one open" (xref_sweep) is
    # true of §6.3's first sentence; say it in those words, since the moved block carried them
    ("sub", """This subsection explains the aleatoric column and only that column; ensemble disagreement is not
shaped by the mechanism below,""",
     """This subsection explains the aleatoric column and only that column, and leaves the epistemic one
open: ensemble disagreement is not shaped by the mechanism below,""")]

# ---- §6.6: the per-dimension permutation machinery -> Appendix K -----------------------------------------
_K = "## Appendix K — the per-dimension permutation tests behind §6.6"
ITEMS["s66_perm"] = [
    ("move", "**The P column is a permutation P, not a binomial one**", "So σ *collapsing in magnitude* is objective-driven",
     """**The P column is a permutation P**, which pairs each trajectory's σ with a different trajectory's
realised error and so keeps the coupling between dimensions and the growth of error with depth that
every trajectory shares. The binomial P-values an earlier draft attached to these counts are
withdrawn (`S-15`), and the correction is large (Appendix K).

""", _K),
    ("move", "**The larger arenas agree with each other against the smallest.**", "So this section's claim is:",
     """**Across arenas, and after correction for multiplicity.** The two larger arenas put the epistemic
ordering's strength at *short* horizon. At long horizon the forecast-depth trend every trajectory
shares lifts the null until a full count is close to chance, which is what motivates §6.7's index
control, and the out-of-sample arena, at {{perm_oos_nind}} trajectories, cannot reach significance
at any horizon. Nothing here survives Holm–Bonferroni in any of the three arenas (Appendix K).

""", _K),
    # a pointer in §6.7's footnote described the machinery that moved (xref_sweep)
    ("sub", "structurally the same problem §6.6 spends a page correcting for the 45 coupled state dimensions.",
     "structurally the same problem that §6.6's permutation null corrects for across the 45 coupled state dimensions (Appendix K)."),
]

# ---- §5: the long-horizon cell counts, multiplicity and the head-to-head table -> Appendix L ------------
_L = "## Appendix L — section 5's long-horizon cells, multiplicity, and the reimplementation beside the released checkpoint"
_SEEDS_TAIL = """§6.10's and §11's paired contrasts at the same n store their four
per-trajectory values in `results/r2_independent_ensemble.json` and
`results/m49_capacity_matched.json`; §6.2's two held-out tables, at n_independent = {{b2_nind}},
give intervals only, coarse for the same reason."""
ITEMS["s5_detail"] = [
    ("move", "At long horizons the pattern is consistent across the design.", "### 5.1 ",
     """At long horizons the out-of-sample gap excludes zero in **{{ab_long_excl}} of {{ab_long_cells}}**
cells, both trajectory lengths crossed with the {{bu_ckpts}}-iteration checkpoints, and Holm–Bonferroni
over the family of {{c3_family}} out-of-sample comparisons still rejects **{{c3_holm_rejected}} of
{{c3_long}}** (Appendix L). Beside the artifact it reimplements, at {{iters_main}} iterations, both
metrics put the released checkpoint first at {{h2h_released_sweeps_at}} and an Arm A variant ahead of
it at {{h2h_armA_sweeps_at}}, on an arena that is out-of-sample for our arms and in-sample for the
checkpoint (Appendix L).

""", _L),
    ("sub", "At h = {{v2_deploy_h}} the four\nare {{a1_gap_traj_h100}}. " + _SEEDS_TAIL,
     "At h = {{v2_deploy_h}} the four\nare {{a1_gap_traj_h100}}."),
    ("append", "*Stored per-trajectory values elsewhere.* " + _SEEDS_TAIL, _L),
]

# ---- relative references in moved text that now sit in an appendix --------------------------------------
ITEMS["appx_refs"] = [
    ("sub", "Holm–Bonferroni rejects **{{c3_holm_rejected}} of {{c3_long}}**. The sign\ntest above is unaffected either way.",
     "Holm–Bonferroni rejects **{{c3_holm_rejected}} of {{c3_long}}**. §5's sign\ntest is unaffected either way."),
    ("sub", "**How good the reimplementation is as a model, next to the artifact it reimplements.**\nThe tables above compare two training rules",
     "**How good the reimplementation is as a model, next to the artifact it reimplements.**\n§5's tables compare two training rules"),
    ("sub", "**The P column is a permutation P, not a binomial one**, and the binomial P-values an earlier draft attached to these counts",
     "**§6.6's P column is a permutation P, not a binomial one**, and the binomial P-values an earlier draft attached to its counts"),
]


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
                assert t.rstrip().endswith("---"), "the template no longer ends with an appendix rule"
                t = "\n".join(L[:si[0]]) + "\n" + summary + "\n".join(L[ei[0]:])
                if heading in t:
                    # a second block for the appendix just created: it must be the last one
                    assert t.rindex("\n## Appendix") == t.index("\n" + heading), f"{it}: {heading[:40]!r} is not the last appendix"
                    t = t.rstrip("\n")[:-3].rstrip("\n") + "\n\n" + block + "\n\n---\n"
                else:
                    t = t.rstrip("\n") + "\n\n" + heading + "\n\n" + block + "\n\n---\n"
            elif op[0] == "append":
                _, text, heading = op
                assert t.rindex("\n## Appendix") == t.index("\n" + heading), f"{it}: {heading[:40]!r} is not the last appendix"
                t = t.rstrip("\n")[:-3].rstrip("\n") + "\n\n" + text.strip("\n") + "\n\n---\n"
            else:
                raise ValueError(op[0])
    shutil.copy(F, F + ".bak")
    open(F, "w").write(t)
    print("patched", F, sys.argv[1:])


if __name__ == "__main__":
    main()
