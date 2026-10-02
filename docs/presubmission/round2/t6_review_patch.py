"""Round 2, T6: the length review's fixes (evidence R2T6/t6_review.md). Whitespace-tolerant, each match
asserted exactly once, nothing written before every assert passes, a .bak beside each file."""
import re
import shutil

EDITS = {"PAPER.template.md": [
# F1: §6.6's second summary (and F14: at most two sentences)
("""**Across arenas, and after correction for multiplicity.** The two larger arenas put the epistemic
ordering's strength at *short* horizon. At long horizon the forecast-depth trend every trajectory
shares lifts the null until a full count is close to chance, which is what motivates §6.7's index
control, and the out-of-sample arena, at {{perm_oos_nind}} trajectories, cannot reach significance
at any horizon. Nothing here survives Holm–Bonferroni in any of the three arenas (Appendix K).""",
 """**Across arenas, and after correction for multiplicity.** The two larger arenas, which are nested
(every in-sample trajectory is among the all-ten ones), put the epistemic ordering's strength at
*short* horizon, because at long horizon the forecast-depth trend every trajectory shares lifts the
null until a full count is close to chance, which is what motivates §6.7's index control. Nothing
here survives Holm–Bonferroni in any of the three arenas, and out of sample at the 400-step unit
nothing could, since its smallest attainable P already exceeds the smallest Holm threshold
(Appendix K)."""),
# F2, F4: §6.2's summary of M-62 and M-63
("""Resampling whole
episodes rather than 400-step trajectories changes no verdict (rule M-62: **{{m62_verdict}}**), and the
one-step failure is spread across the {{d1n_epi_ndim_h1}} state dimensions rather than carried by a few
(rule M-63: **{{m63_verdict}}**), which is what §6.3's mechanism predicts.""",
 """Resampling whole
episodes rather than 400-step trajectories changes no verdict in the one arena with the power to
show it, the out-of-sample cells being uninformative by design (rule M-62: **{{m62_verdict}}**), and
the epistemic term's one-step coverage failure is spread across the {{d1n_epi_ndim_h1}} state
dimensions rather than carried by a few (rule M-63: **{{m63_verdict}}**)."""),
# F4: the same claim in the moved text (M-63 measures the epistemic term, which §6.3 does not explain)
("""**No channel is exempt**, which is what §6.3's mechanism predicts: an objective whose optimum is σ = 0 has no reason to spare any dimension.""",
 """**No channel is exempt.**"""),
# F3: §1, the conditional restored
("""a margin {{q2_n_req}} independent trajectories would
  resolve, against the {{e7_nind}} here (§11).""",
 """a margin {{q2_n_req}} independent trajectories would
  resolve if it is real, against the {{e7_nind}} here (§11)."""),
# F12: §1, the deleted sentence restored, the multiplier bullet's meaning restored, Appendix E's descriptor
("""Three things distinguish this from a re-run of the authors' code.""",
 """This is a reproduction in the stronger sense: the contribution is not that the numbers came out
the same, but what re-measuring the method reveals about where it is robust and where it is not.
Three things distinguish it from a re-run of the authors' code."""),
("""every pre-registered rule is in Appendix E).""",
 """every pre-registered rule, with its lead time and verdict, is in Appendix E)."""),
("""where a global one does not, though no single cell is resolvable and the checkpoint trained on
  both episodes (§6.8);""",
 """where a global one does not, though no single cell is resolvable and the cells are unseen only by
  the multiplier, since the checkpoint trained on both episodes (§6.8);"""),
# F5: §11's pointer to the short-unit counts
("""a shorter unit gives {{m64_oos_n_h100}} independent units at h = {{v2_deploy_h}} where the 400-step unit gives {{perm_oos_nind}} (§6.6), and we did not rerun""",
 """a shorter unit gives {{m64_oos_n_h100}} independent units at h = {{v2_deploy_h}} where the 400-step unit gives {{perm_oos_nind}} (Appendix K), and we did not rerun"""),
# F6: pointers to figures now in Appendix K
("""and the in-sample permutation test agrees (§6.6).""", """and the in-sample permutation test agrees (Appendix K)."""),
("""in our tables by up to {{perm_worst_factor}}× (§6.6).""", """in our tables by up to {{perm_worst_factor}}× (§6.6, Appendix K)."""),
("""§6.6 explains why a binomial null is inadmissible here.""", """Appendix K explains why a binomial null is inadmissible here."""),
# F7: Appendix J's relative references
("""**The derivation says the collapse happens on any dataset, and that is testable.** It matters""",
 """**§6.3's derivation says the collapse happens on any dataset, and that is testable.** It matters"""),
("""**What this does that the derivation alone could not.**""", """**What this does that §6.3's derivation alone could not.**"""),
("""We predicted the collapse from this algebra before training, then observed it. Three run counts""",
 """We predicted the collapse from §6.3's algebra before training, then observed it. Three run counts"""),
("""excluded from every rate quoted here (Appendix B).""", """excluded from every rate §6.3 quotes (Appendix B)."""),
("""so the scatter and the quoted statistic describe""", """so the scatter and §6.3's quoted statistic describe"""),
# F8: Appendix L
("""At long horizons the pattern is consistent across the design. Under the cluster bootstrap,""",
 """At long horizons §5's pattern is consistent across the design. Under the cluster bootstrap,"""),
("""*Stored per-trajectory values elsewhere.* §6.10's and §11's paired contrasts at the same n store their four""",
 """*Stored per-trajectory values elsewhere.* §6.10's and §11's paired contrasts at §5's n = {{m23_nind}} store their four"""),
("""give intervals only, coarse for the same reason.""",
 """give intervals only, coarse for the same reason (the n = {{m23_nind}} caveat of §3)."""),
("""At h = {{v2_deploy_h}} the four
are {{a1_gap_traj_h100}}.""",
 """At h = {{v2_deploy_h}} the four
are {{a1_gap_traj_h100}}; Appendix L notes where other sections store theirs."""),
# F9: Appendix C, one account and no circular pointer (the moved addresses join the sentence that was already there)
("""The code that generates data is in
neither repository this reproduction pins: the lite release only reads its dataset, and its
readme places collection in a third repository, the authors' Isaac Lab extension, which this reproduction does not pin (§3, ledger `D-36`).""",
 """The code that generates data is in
neither repository this reproduction pins: the only code that touches the file reads it
(`train.py:44` in the lite release), the lite release's environment rolls the learned model forward
rather than physics, and its readme places collection in a third repository, the authors' Isaac Lab
extension (`readme.md:13`), which this reproduction does not pin and which would need Isaac Lab and
an RTX-class GPU (ledger `D-36`)."""),
("""*Why more data cannot be generated.* No repository this reproduction pins can generate data. Neither contains code that
writes a dataset: the only code that touches the file reads it (`train.py:44` in the lite release),
and the lite release's environment rolls the learned model forward rather than physics. Its readme
sends anyone wanting simulator-based collection to the authors' Isaac Lab extension
(`readme.md:13`), which we do not pin and which would need Isaac Lab and an RTX-class GPU.

""", ""),
# F10: §2, the clamp is what is inherited
("""**Where the parameterisation comes from.** The bounded log-σ head whose optimum §6.3 shows is
σ = 0 is inherited, line for line,""",
 """**Where the parameterisation comes from.** The clamp of the bounded log-σ head whose optimum §6.3
shows is σ = 0 is inherited, line for line,"""),
# F11: §5's summary of the head-to-head table
("""Beside the artifact it reimplements, at {{iters_main}} iterations, both
metrics put the released checkpoint first at {{h2h_released_sweeps_at}} and an Arm A variant ahead of
it at {{h2h_armA_sweeps_at}}, on an arena that is out-of-sample for our arms and in-sample for the
checkpoint (Appendix L).""",
 """Beside the artifact it reimplements, on {{h2h_nind}} independent trajectories with our arms at
{{iters_main}} iterations over {{h2h_nseeds}} seeds, relative-L1 and nRMSE both put the released checkpoint
first at {{h2h_released_sweeps_at}} and an Arm A variant ahead of it at {{h2h_armA_sweeps_at}}, a reading that
flatters the checkpoint, since the arena is out-of-sample for our arms and in-sample for it (Appendix L)."""),
# F13: §5 sign test, descriptive
("""It needs no bootstrap or multiplicity correction,""", """It uses no bootstrap or multiplicity correction,"""),
# F14: §5 M-64, the dangling participle
("""Rebuilt under a rule committed before the index was built (rule M-64, Appendix E) at
{{m64_h1_unit}} rows, 32 of history and one forecast step, non-overlapping within an episode, the
same two episodes yield {{m64_h1_n}} units.""",
 """Under a rule committed before the index was built (rule M-64, Appendix E), we rebuilt it at
{{m64_h1_unit}} rows, 32 of history and one forecast step, non-overlapping within an episode:
{{m64_h1_n}} units on the same two episodes."""),
# F14: §6.3's summary of the synthetic test, two sentences, and its setting stated
("""**The derivation says the collapse happens on any dataset, and that is testable.** On the
released data, "small stochasticity in the environment" and our reading are observationally
identical, so under a rule committed before the runs (rule M-50, Appendix E) we trained the released
head, unmodified, on synthetic data whose known noise varies {{e5s_span}}× across the input range.
**Under the implemented objective σ sits {{e5s_mse_under}}× below the true noise and does not track
it at all**, while under the authors' unused likelihood branch, same data and same head, it recovers
the true level to a median ratio of {{e5s_nll_ratio}}, seed-variably. The rule returns
**{{e5s_verdict}}**: the experiment establishes the contrast, not the size of the recovery
(Appendix J).""",
 """**The derivation says the collapse happens on any dataset, and that is testable.** Under a rule
committed before the runs (rule M-50, Appendix E) we trained the released head, unmodified but over a
one-dimensional state with no recurrent trunk, on synthetic data whose known noise varies
{{e5s_span}}× across the input range: **under the implemented objective σ sits {{e5s_mse_under}}× below
the true noise and does not track it at all**, while under the authors' unused likelihood branch it
recovers the true level to a median ratio of {{e5s_nll_ratio}}, seed-variably. The rule returns
**{{e5s_verdict}}**, which establishes the contrast and not the size of the recovery (Appendix J)."""),
], "docs/BUILD_CHECKS.template.md": [
# F4: the withdrawn clause, kept in the moved-from-body list
("""- **[§6.2]** At n_independent = {{b2_nind}} the short-horizon epistemic ordering looked like chance,""",
 """- **[§6.2]** An earlier draft said rule M-63's finding, that no state dimension is exempt from the
  one-step coverage failure, "is what §6.3's mechanism predicts: an objective whose optimum is σ = 0
  has no reason to spare any dimension". M-63 decomposes the epistemic term's coverage, and §6.3
  explains only the aleatoric head, so the clause is withdrawn (round 2, T6 review).
- **[§6.2]** At n_independent = {{b2_nind}} the short-horizon epistemic ordering looked like chance,"""),
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
