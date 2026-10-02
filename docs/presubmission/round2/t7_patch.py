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


# ---- §7.4 and §7.5: two sentences each -------------------------------------------------------------------
_Q = "## Appendix Q — what the spliced windows cost: the contaminated arm and the duplication control (§7.4)"
_F = "## Appendix F — the variance-state arithmetic behind §7.5"
ITEMS["s7_45"] = [
    ("move", "**7.4 What the spliced windows cost: nothing measurable.**", "**7.5 The released artifacts do not reproduce",
     """**7.4 What the spliced windows cost: nothing measurable in rollout.** A contaminated arm trained with
{{arm_splices}} spliced windows added, at {{arm_contam_pct}}% contamination (below the pipeline's
{{contam_pct}}%, by design, so that no held-out row leaks), raises training loss by
{{contam_cost_pct}}% where a duplication control adding the same number of exact copies raises it by
{{dup_cost_pct}}%, and in rollout it is hurt in {{tw_cc_cluster_hurt}} of {{tw_cells}} cells and helped
in {{tw_cc_cluster_helped}} (Figure 6a), the signature of regularisation. At this rate the splices do
not harm rollout; the unmarked boundaries remain a real defect on leakage grounds (Appendix Q).

---

""", _Q),
    ("move", "**7.5 The released artifacts do not reproduce", "## 8. ",
     """**7.5 The released artifacts do not reproduce the released checkpoint's variance state.** Read as a
clock, §6.3's collapse rate puts the checkpoint's variance state out of reach of a constant-rate run
from the released initialisation at every iteration count the release, the paper and the checkpoint
tag state. The first author's account, that the release is several revisions removed from the setup
that trained it, supplies a mechanism, a warm start or a different initialisation, so this is a
documentation gap between a release and a run rather than an inconsistency (Appendix F and the
supplementary `docs/APPENDIX_G_VARIANCE_ARITHMETIC.md`).

---

""", _F),
    # the moved blocks carried the rule that followed them; collapse runs of consecutive rules into one
    ("fn", lambda t: __import__("re").sub(r"(\n---\n)(?:\n---\n)+", r"\1", t)),
    # the moved blocks' own numbered leads would duplicate the body's §7.4 and §7.5 leads
    ("sub", "**7.4 What the spliced windows cost: nothing measurable.** We trained a contaminated arm",
     "**The design.** We trained a contaminated arm"),
    ("sub", "**7.5 The released artifacts do not reproduce the released checkpoint's variance state.**\nThe σ collapse is linear",
     "**§7.5's argument in full.** The σ collapse is linear"),
]


# ---- §11: limitations not already stated where they bite; the full text -> Appendix R ------------------
_R = "## Appendix R — the limitations in full (§11)"
_S11 = """## 11. Limitations

Limits that belong to one result are stated beside it: the budget and our reading of Table S7
(§5.2, §5.3), the mechanism of §6.4 as a hypothesis, and the recalibration's two episodes (§6.7).
Appendix R gives every limitation below in full.

**Effective sample size bounds every long-horizon claim.** The out-of-sample arena has
{{m23_nind}} independent 400-step trajectories (the n = {{m23_nind}} caveat of §3), the binding
constraint on §5, and a larger dataset cannot be generated here (Appendix C), so the released
checkpoint's lack of a held-out arena is a constraint, not a choice.

**One dataset, one gait, one terrain.** All commands are drawn from one bounded box and the gait is
a single trot, so "generalisation" here means across velocity commands only.

**Single seeds.** The long-horizon trend fit and the per-dimension matched comparison rest on seed 1
alone (Appendix H), and the headline A/B verdict on seed {{m23_seed}}, the one its rule ran on; the
magnitudes beside it are three-seed means with per-seed values (§5).

**Ensemble size: supported, not established.** Our ensemble-5 arms reproduce the direction of §6.6's
ranking finding and the calibration failure, but rule M-43 returns **{{e5_verdict}}** on their
{{e5_nind}} independent 400-step trajectories (§6.6). So that finding is established on the released
checkpoint and supported but not established on a model we trained.

**The ranking claim is not established as needing an ensemble.** The model's own predicted step
size ranks error nearly as well, by a margin this sample cannot resolve (§6.6). If the observed
margin is the true one, settling it needs {{q2_n_req}} independent 400-step trajectories where all ten
episodes provide {{e7_nind}}, a required-sample-size estimate under an assumed effect (Appendix R).

**We did not measure what the miscalibration costs.** The penalty the follow-up applies is
miscalibrated as a scale, {{d1n_epi_ratio_h100}}× overconfident at h = {{v2_deploy_h}}, the horizon its
own imagination rollouts run to, but the method's only use of that quantity is to shape policy
learning, and we did not train a policy. **The finding bounds what the quantity reports, not what it
costs**, and the ratio is not a measure of harm. Other sections refer back to this as the policy
caveat of §11. A proxy that needs no policy, the ordering of the penalty accumulated along whole
rollouts before and after the per-horizon correction, finds none of the {{q3_n_pairs}} pairs reordered
(rule M-70: **{{q3_verdict}}**), but it orders the penalty alone, not the penalised return, and its
null is partly structural (Appendix R).

**The per-dimension ordering tests are underpowered at every sample size we can reach** (§6.5,
Appendix K). This limits the per-dimension evidence only; the aggregate scalar the method applies is
one test, not forty-five coupled ones (§6.6).

**No family-wide correction is applied across our own pre-registered rules.** There are
{{appG_n_rules}} of them with per-rule verdicts (Appendix E), each committed before its data and
reported against its own thresholds; a reader who prefers a corrected family threshold can apply it
from that count.

**The independent-ensemble comparison bounds the trunk-sharing effect rather than isolating it.**
Independent members differ from shared-trunk heads in data ordering and in capacity as well as in
sharing. Rule M-49 (Appendix E) holds capacity fixed, at {{m49_matched_params}} state-pathway
parameters, a ratio of {{m49_matched_ratio}}: the independent ensemble is still better calibrated on
every shared-trunk seed, every paired interval excludes zero and its coverage gain of
{{m49_cov_gain}} points clears its own MDE, but the overconfidence improvement falls from
{{m44_ratio_gain}}× to **{{m49_ratio_gain}}×** against an MDE of {{m49_mde_ratio}}×, so the rule returns
**{{m49_verdict_short}}**. Capacity does not explain the effect away; how much of it capacity accounts
for, this design cannot say (Appendix R).

**Deliberately out of scope.** No policy-learning result of either paper is reproduced or tested,
the sample-efficiency comparison is not tested for the same reason, and nothing here uses a GPU. We
did not test whether the σ = 0 optimum affects other descendants of the PETS parameterisation: the
hypothesis is well-founded only for one that makes the same substitution, and is untested for any
(§2, Appendix I).

"""


def _s11(t):
    L = t.split("\n")
    a = [i for i, x in enumerate(L) if x.startswith("## 11. ")]
    b = [i for i, x in enumerate(L) if x.startswith("## 12. ")]
    assert len(a) == 1 and len(b) == 1
    old = "\n".join(L[a[0] + 1:b[0]]).strip("\n")
    assert old.endswith("---")
    old = old[:-3].rstrip("\n")
    t = "\n".join(L[:a[0]]) + "\n" + _S11 + "---\n\n" + "\n".join(L[b[0]:])
    return t.rstrip("\n") + "\n\n" + _R + "\n\n" + old + "\n\n---\n"


ITEMS["s11"] = [("fn", _s11)]


# ---- §12: the opening, one paragraph for the middle, and the three-kind paragraph -> ~500 words --------
_S = "## Appendix S — the conclusion's discussion of the ranking, the scale and the per-dimension evidence (§12)"
ITEMS["s12"] = [
    ("move", "The more useful finding is asymmetric, and it cuts both ways.", "**What should travel from this paper",
     """The ranking use the follow-up claims survives a real test. Ensemble disagreement beats the forecast
step index at every horizon and, with both the rollout and the depth held constant, still correlates
{{a2_rdd}} {{a2_rdd_ci}} with realised error (§6.6), though a free subtraction, the model's own
predicted step size, ranks error nearly as well ({{e7_verdict}}). The scale may be repairable per
horizon on the released checkpoint, but on a model that never saw the test episodes the evidence is
mixed (§6.7), and per dimension no ordering reaches significance once the coupling between
dimensions is respected (§6.5). As the scalar the method applies, ensemble disagreement gets the
order right and the size wrong: it should not be read as a scale, and a ranking use deserves its own
validation on the deployment distribution (Appendix S).

""", _S),
]


if __name__ == "__main__":
    E.main()
