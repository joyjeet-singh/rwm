"""Round 2, T4: the wording review's fixes (evidence R2T4/t4_review.json). Whitespace-tolerant, each match
asserted exactly once, nothing written before every assert passes, .bak beside the file."""
import re
import shutil

F = "PAPER.template.md"
EDITS = [
# F1, F8: the abstract
("""the *Robotic World Model* (arXiv:2501.10100v1)
and its uncertainty-aware follow-up""",
 """the *Robotic World Model* (RWM; arXiv:2501.10100v1)
and its uncertainty-aware follow-up"""),
("""exactly before training. With {{c2_pct}}% of the
reference's world-model data, one robot, gait and terrain, and {{nind_oos_400}} independent
held-out trajectories, the base paper's central training claim reproduces""",
 """exactly before training. The base paper's central training claim reproduces"""),
("""RWM is ahead of MLP, RSSM and transformer baselines built to our reading of the original and
trained like it, though at {{v2_diag_h}} steps each does worse than predicting no change.
On accuracy alone, {{mn_better_kinds}} beat the original's chosen setting at
our budget, the best even when that setting trains longer; it was chosen as a trade-off with training time,
which we do not test.""",
 """RWM beats MLP, RSSM and transformer baselines built to our reading of the original and
trained with RWM's settings, though at {{v2_diag_h}} steps each does worse than predicting no change.
On accuracy alone, {{mn_better_kinds}} beat the original's chosen setting at
our budget, the best even when that setting trains {{n3_mid_factor_word}} as long (post hoc); it was chosen as a
trade-off with training time, which we do not test. These rest on {{c2_pct}}% of the reference's
world-model data, one robot, gait and terrain, and {{nind_oos_400}} independent held-out trajectories."""),
("""ranks error nearly as well ({{e7_step_r}}), by an unresolved margin.""",
 """ranks error nearly as well ({{e7_step_r}}; margin unresolved)."""),
# F1, F2: contribution 3
("""though every baseline is worse there than predicting no change and our RSSM's
  open-loop collapse is not a matter of how its forecast is read (§5.3).""",
 """though every baseline is worse there than predicting no change, and reading our RSSM's
  forecast from its prior's expected or sampled latent does not remove its open-loop collapse
  (exploratory; §5.3)."""),
("""falls steeply as the history grows to M = 8 — the best of them even when the centre trains longer;""",
 """falls steeply as the history grows to M = 8 — the best of them even when the centre trains
  {{n3_mid_factor_word}} as long (post hoc);"""),
# F9
("""On the governing reading ours does
not fall at all:""",
 """On the governing reading ours does
not fall steeply:"""),
# F3
("""and at {{iters_long}} it passes
both shorter histories, {{n3_sh_long_clause}}.""",
 """and at {{iters_long}}, on the held-out pair, it passes
both shorter histories, {{n3_sh_long_clause}}."""),
# note: verdict level, not configuration level
("""and return what the averaged ones did everywhere except
{{n2_n_changed_word}} in-sample readings of §5.3's rules: {{n2_changed_list}}.""",
 """and return the same verdict as the averaged ones everywhere except
{{n2_n_changed_word}} in-sample readings of §5.3's rules (which configurations a reading resolves can
shift; the artifact lists each): {{n2_changed_list}}."""),
# notes: the head-to-head caption
("""Both
aggregations, for those and for §5.3's architecture baselines, and one arena:""",
 """Both
aggregations, for these models and for §5.3's architecture baselines, on one arena:"""),
("""their nRMSE is pooled as §3.1 defines it, recomputed afterwards from the same rollouts
(post hoc,""",
 """their nRMSE is pooled as §3.1 defines it, recomputed afterwards with the same evaluator
(post hoc,"""),
# note: the per-trajectory count is bound
("""each such row's four per-trajectory differences from
RWM are all positive""",
 """each such row's {{mn_nind}} per-trajectory differences from
RWM are all positive"""),
# F7
("""and the rules'
relative-L1 readings at other horizons say where it starts.""",
 """and the rules'
relative-L1 readings at other horizons on the held-out pair say where it starts."""),
("""Before those horizons a baseline
cannot be told apart from RWM:""",
 """Before those horizons, on the held-out pair, a baseline
cannot be told apart from RWM:"""),
# F5
("""it is the most accurate model here one
step ahead,""",
 """it is the most accurate of this section's models one
step ahead,"""),
# F1, F10: Appendix D
("""the best of them even when the centre trains longer (post hoc).""",
 """the best of them even when the centre trains {{n3_mid_factor_word}} as long (post hoc, §5.2)."""),
("""and the RSSM comparison is uninformative (rule X1), so the claim rests on the MLP and the transformer.""",
 """and until rule X1 says otherwise the RSSM comparison is uninformative, so the claim rests on the MLP and the transformer."""),
# F4: the Conclusion
("""Its
architecture claim also holds against baselines we built, while its chosen history and forecast
lengths are beaten at our budget (§5.2, §5.3).""",
 """RWM is
ahead of the baselines we built to our reading of it, though at h = {{v2_diag_h}} none of them beats
predicting no change, and on accuracy alone {{mn_n_better_word}} other history and forecast lengths beat
its chosen ones at our budget, which it chose as a trade-off with training time (§5.2, §5.3)."""),
]


def main():
    t = open(F).read()
    for old, new in EDITS:
        p = re.compile(r"\s+".join(re.escape(w) for w in old.split()))
        n = len(p.findall(t))
        assert n == 1, f"{n} matches for {old[:70]!r}"
        t = p.sub(lambda _: new, t, count=1)
    shutil.copy(F, F + ".bak")
    open(F, "w").write(t)
    print("patched", F, len(EDITS), "edits")


if __name__ == "__main__":
    main()
