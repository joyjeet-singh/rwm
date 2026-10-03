"""Round 2, T11 step 5: refresh docs/COVER_STATEMENT.md beyond section 8's figures (which
docs/presubmission/s10fix_docs.py refreshes) — the page count, the rule counts, the retraction counts,
M-49's verdict, and three statements that had drifted stronger than the paper.

Every figure is read from results/paper_numbers.json; none is typed. Each pattern must match exactly
once (whitespace-tolerant), and nothing is written until all have. Run from the repository root after
the final build.
"""
import json
import re
import sys

F = "docs/COVER_STATEMENT.md"
N = json.load(open("results/paper_numbers.json"))
v = lambda k: N[k]["value"] if isinstance(N[k], dict) else N[k]  # noqa: E731
WORDS = {13: "Thirteen"}

n_rules, n_pos = int(v("appG_n_lead")), int(v("appG_n_positive"))
assert n_rules - n_pos == 1, (n_rules, n_pos)          # the sentence names exactly one negative lead
n_claims = {"seven": 7}[str(v("n_retractions_word")).lower()]
n_fram = {"six": 6}[str(v("n_retract_framing_word")).lower()]

EDITS = [
    ("page count",
     "current at 48 pages, the",
     f"current at {v('pdf_pages')} pages, the"),
    ("verification figures",
     "losses and gradients match to `0.000e+00` across 7 terms and 106 tensors",
     f"losses and gradients match to `{v('diff_grad_max')}` across {v('diff_terms')} terms and "
     f"{v('diff_n_params')} tensors"),
    ("rule counts",
     "**Eighteen pre-registered decision rules, with git lead times.** Each names its conditions and "
     "thresholds before its data existed, and Appendix E gives all eighteen with the lead time computed "
     "from git. Seventeen have a positive lead and are a difference of two commit timestamps; the "
     "eighteenth is negative and is not,",
     f"**{n_rules} pre-registered decision rules, with git lead times.** Each names its conditions and "
     f"thresholds before its data existed, and Appendix E gives all {n_rules} with the lead time computed "
     f"from git. {n_pos} have a positive lead and are a difference of two commit timestamps; the "
     f"remaining one is negative and is not,"),
    ("M-49's verdict verbatim",
     "`M-49` returns `UNDER-POWERED`,",
     f"`M-49` returns `{v('m49_verdict')}`,"),
    ("M-64's units",
     "resolved as real under a second pre-registered rule at 60 units.",
     f"resolved as real under a second pre-registered rule at {v('m64_h1_n')} units."),
    ("the synthetic sweep",
     "clears its own slope threshold on only 11 of 20 seeds.",
     f"clears its own slope threshold on only {v('e5s_corrob_clearing')} of {v('e5s_corrob_seeds')} seeds."),
    ("retraction counts (ruling U1)",
     "**Twelve retractions kept in the record** — six that withdraw numbers and six that withdraw framings —",
     f"**{WORDS[n_claims + n_fram]} withdrawals kept in the record** — {v('n_retractions_word').lower()} "
     f"claims withdrawn on evidence and {v('n_retract_framing_word')} framings withdrawn —"),
    ("the worst factor",
     "including one wrong by about a factor of 10¹³",
     "including one wrong by about a factor of "
     + str(v("perm_worst_factor")).replace("10^13", "10¹³")),
    ("the constant rescale",
     "grows by a factor of 4 across the rollout.",
     f"grows by a factor of {v('m65_c_growth')} across the rollout."),
    ("the per-horizon multiplier, scoped as section 6.7 and the README state it",
     "brings every held-out coverage estimate within 10 points of nominal, though no single cell is "
     "resolvable at this arena.",
     f"brings every coverage estimate of the released checkpoint within {v('d3_tol')} points of nominal, "
     f"though no single cell is resolvable at this arena and those cells are unseen only by the multiplier, "
     f"since the checkpoint trained on both episodes; on Arm A, whose model never saw them, its own "
     f"multipliers manage {v('d3x_own_epi_ok')} of {v('d3x_own_epi_cells')} epistemic cells."),
    ("the comparator of the independent ensemble (section 6.8)",
     "| an independent-ensemble contrast | five separately trained models against the released "
     "shared-trunk ensemble, testing the mechanism rather than asserting it |",
     "| an independent-ensemble contrast | five separately trained models against our own shared-trunk "
     "ensembles of the released architecture, testing the mechanism rather than asserting it |"),
    ("the capacity-matched verdict",
     "| a capacity-matched re-test | the same contrast with parameter count held fixed, so capacity is "
     "not the explanation |",
     f"| a capacity-matched re-test | the same contrast with parameter count held fixed: rule M-49 returns "
     f"`{v('m49_verdict')}`, so capacity does not explain the effect away, and how much of it capacity "
     f"accounts for is not resolved |"),
    ("the repair, with its evidence",
     "| a working repair | the per-horizon multiplier, evaluated only on held-out folds |",
     f"| a candidate repair, with mixed evidence | the per-horizon multiplier, fitted on one episode and "
     f"scored on the other: the released checkpoint's cells within {v('d3_tol')} points (no cell resolvable "
     f"at this arena), {v('d3x_own_epi_ok')} of {v('d3x_own_epi_cells')} epistemic cells on Arm A |"),
]


def main():
    s = open(F).read()
    plan = []
    for name, old, new in EDITS:
        pat = re.compile(r"\s+".join(re.escape(w) for w in old.split()))
        hits = pat.findall(s)
        if len(hits) != 1:
            sys.exit(f"STOP: '{name}' matched {len(hits)} times")
        plan.append((name, pat, new))
    for name, pat, new in plan:
        s = pat.sub(lambda _: new, s, count=1)
        print(f"  applied: {name}")
    open(F, "w").write(s)


if __name__ == "__main__":
    main()
