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



# ---- §6: merges (ruling U6) — §6.5 into §6.3, §6.9 into §6.6, §6.11 into §6.10 ---------------------------
def _section(t, heading_prefix):
    """(start, end) line indices of a ### subsection: its heading line to the line before the next heading."""
    L = t.split("\n")
    s = [i for i, x in enumerate(L) if x.startswith(heading_prefix)]
    assert len(s) == 1, (heading_prefix, len(s))
    e = next(i for i in range(s[0] + 1, len(L)) if L[i].startswith("## ") or L[i].startswith("### "))
    return L, s[0], e


def _fold(src, dst, lead):
    """Remove subsection `src`, turning its heading into the bold lead `lead`, and append its body verbatim
    at the end of subsection `dst`."""
    def f(t):
        L, s, e = _section(t, src)
        body = "\n".join(L[s + 1:e]).strip("\n")
        assert body, src
        t = "\n".join(L[:s] + L[e:])
        L, s, e = _section(t, dst)
        k = e
        while k > s and L[k - 1].strip() in ("", "---"):
            k -= 1
        block = [""] + (lead + " " + body.lstrip()).split("\n")
        return "\n".join(L[:k] + block + L[k:])
    return f


ITEMS["s6_fold"] = [
    ("fn", _fold("### 6.5 ", "### 6.3 ", "**The correction fails differently rather than succeeding.**")),
    ("fn", _fold("### 6.9 ", "### 6.6 ", "**The structural excuse does not survive.**")),
]

_O = "## Appendix O — rule M-44 in full: an ensemble that shares nothing"
_P = "## Appendix P — rule M-68 in full: both fixes on the same models"
_S610_BODY = """### 6.10 Testing the mechanism: an ensemble that shares nothing, alone and with the corrected objective

§6.4 establishes the topology as a fact and the mechanism as a hypothesis. Two rules committed to git
before any of their artifacts existed test it, each with a minimum detectable effect estimated in
advance (Appendix E). Rule M-44 scores {{r2_n_indep}} independently initialised full models, Arm A at
ensemble size 1 trained at {{r2_n_indep}} seeds, together as an ensemble at evaluation time: each
member keeps its own recurrent hidden state and the ensemble mean is fed back to all of them, so the
rollout differs from the shared-trunk one only in what is under test. Rule M-68 repeats it with every
member trained under `gaussian_nll`, so the two fixes are measured on the same models. Both are scored
on the held-out pair against each of the shared-trunk seeds separately.

{{S610_TABLE1}}

**Rule M-44 returns {{m44_verdict}}.** All {{m44_n_conditions_met}} of its {{m44_n_conditions}}
conditions hold against every one of the {{r2_n_shared}} shared-trunk seeds: at h = {{v2_deploy_h}}
the overconfidence factor improves **{{m44_ratio_gain}}×** against a minimum detectable effect of
{{m44_mde_ratio}}×, coverage rises a mean of {{m44_cov_gain}} points against {{m44_mde_cov}}, and every
paired interval excludes zero. σ itself grows {{r2_sigma_x_h100}}× there, **{{r2_from_sigma_h100}}%**
of the improvement, so the trunk-sharing mechanism is the larger part of the effect where the method
operates; at h = {{v2_diag_h}}, {{r2_from_acc_h368}}% is the ensemble simply predicting better
(Appendix O).

{{S610_TABLE2}}

**Rule M-68 returns {{m68_verdict}}**, branch {{m68_branch}} of the four it names: all
{{m68_n_conditions_met}} of its {{m68_n_conditions}} conditions hold, a **{{m68_ratio_gain}}×**
improvement against a minimum detectable effect of {{m68_mde_ratio}}×. That is essentially what
independence gave alone. Against the independent arm, which differs in the loss and nothing else,
switching to `gaussian_nll` multiplies the overconfidence factor by {{m68_vs_mse_ratio}}×
{{m68_vs_mse_ratio_ci}}, slightly the wrong way and below what the design can resolve (Appendix P).
**The two fixes do not add**, and once stated that is no surprise: the objective governs the
aleatoric head, and the epistemic term is a spread across members the loss never sees.

**What the arms bound, and what they do not repair.** Independently seeded runs differ in data
ordering as well as initialisation, and the independent members carry {{v1_cap_ratio}}× the
shared-trunk arms' state-pathway parameters, so these comparisons bound the architectural effect
rather than isolating it; at matched capacity the improvement falls to {{m49_ratio_gain}}× (rule M-49,
§11). Neither arm is an interval: at h = {{v2_deploy_h}} the independent ensemble is
{{r2_indep_ratio_h100}}× overconfident with {{r2_indep_cov1_h100}}% coverage and the combined arm
{{m68_indep_ratio_h100}}× with {{m68_indep_cov1_h100}}%, where a calibrated Gaussian gives
{{v3_cov_nominal1}}%. §6.8's per-horizon multiplier remains the only correction in this paper whose
estimates all land within the band, and only on the released checkpoint.

"""


def _s610(t):
    """Merge §6.10 and §6.11 into one section. The two main tables (each backs a §3.2 row) and their
    captions stay in the body; every other paragraph moves verbatim, in order, §6.10's to Appendix O and
    §6.11's to Appendix P (one appendix each, so no section prints two quantities as one numeral)."""
    L = t.split("\n")
    s = [i for i, x in enumerate(L) if x.startswith("### 6.10 ")]
    e = [i for i, x in enumerate(L) if x.startswith("## 7. ")]
    assert len(s) == 1 and len(e) == 1
    seg = "\n".join(L[s[0]:e[0]])
    paras = [p for p in seg.split("\n\n")]
    def find(pred, what):
        k = [i for i, p in enumerate(paras) if pred(p)]
        assert len(k) == 1, (what, len(k)); return k[0]
    c1 = find(lambda p: p.lstrip().startswith("*Same trajectories (the held-out pair)"), "M-44 caption")
    c2 = find(lambda p: p.lstrip().startswith("*Same trajectories, same harness, same bootstrap unit as §6.10"), "M-68 caption")
    t1, t2 = c1 - 1, c2 - 1
    assert paras[t1].lstrip().startswith("|") and paras[t2].lstrip().startswith("|"), "a caption is not preceded by its table"
    keep = {t1, c1, t2, c2}
    body = (_S610_BODY.replace("{{S610_TABLE1}}", paras[t1].strip("\n") + "\n\n" + paras[c1].strip("\n"))
            .replace("{{S610_TABLE2}}", paras[t2].strip("\n") + "\n\n" + paras[c2].strip("\n")))
    moved, cur = {_O: [], _P: []}, None
    for i, p in enumerate(paras):
        q = p.strip("\n")
        if q.startswith("### 6.10 "):
            cur = _O; continue
        if q.startswith("### 6.11 "):
            cur = _P; continue
        if i in keep or not q.strip() or q.strip() == "---":
            continue
        moved[cur].append(q)
    rest = "\n".join(L[e[0]:])
    head = "\n".join(L[:s[0]])
    t = head + "\n" + body + "---\n\n" + rest
    assert t.rstrip().endswith("---")
    for h in (_O, _P):
        t = t.rstrip("\n") + "\n\n" + h + "\n\n" + "\n\n".join(moved[h]) + "\n\n---\n"
    return t


ITEMS["s610_merge"] = [("fn", _s610)]


if __name__ == "__main__":
    E.main()
