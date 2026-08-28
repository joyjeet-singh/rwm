"""A6 — what the original papers actually report for each claim we tested.

A reproduction that reports 4.61x without saying what the authors reported leaves
a reader unable to tell whether that is consistent with, larger than, or smaller
than the original result. This records, for every claim our section 3 table marks
as tested, the quantitative figure the original gives -- or, where none is given,
says so, which is itself informative about the original.

Sources are the arXiv HTML renderings, read on 2026-08-22:
  arXiv:2501.10100v1 (17 Jan 2025)  -- Roman-numeral sectioning, the version our
                                       section references (IV-C, IV-D, IV-E) match
  arXiv:2501.10100v2 (23 Apr 2025)  -- renumbered to Arabic; IV-C's material moved
                                       to Appendix A.4.1. Recorded so a reader who
                                       opens the current version can still find it.
  arXiv:2504.16680v1 (23 Apr 2025)

This file is hand-entered from the sources rather than computed, and is marked as
such: `evidence: EXT`. Every entry quotes the sentence it rests on so a reader can
check it against the paper without trusting this transcription.

Writes results/original_paper_figures.json.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402

READ_ON = "2026-08-22"

CLAIMS = [
    {
        "key": "ar_beats_tf",
        "claim": "RWM-AR consistently outperforms RWM-TF",
        "where_v1": "2501.10100v1 IV-D (Generality across Robotic Environments)",
        "where_v2": "2501.10100v2 4.3 (same title)",
        "original_figure": None,
        "original_states": (
            "RWM-AR significantly outperforms its teacher-forcing counterpart (RWM-TF), "
            "underscoring the importance of autoregressive training in mitigating compounding "
            "prediction errors over long rollouts."),
        "form": "qualitative; shown in Figure 4",
        "numeral_in_text": False,
        "note": ("Figure 4 plots autoregressive prediction error for RWM-AR against RWM-TF and "
                 "the MLP, RSSM and transformer baselines across environments. No numeral for "
                 "the AR-vs-TF gap appears in the running text, the caption, or any table. The "
                 "magnitude is legible only from the plotted curves, and we do not estimate it "
                 "from the axis."),
    },
    {
        "key": "tf_poor",
        "claim": 'Teacher forcing gives "poor autoregressive performance"',
        "where_v1": "2501.10100v1 IV-C (Dual-autoregressive Mechanism)",
        "where_v2": "2501.10100v2 Appendix A.4.1 (same title)",
        "original_figure": None,
        "original_states": (
            "Interestingly, when the forecast horizon N=1 (teacher-forcing), training can be "
            "highly parallelized, resulting in minimal training time. However, this setting "
            "leads to poor autoregressive performance, as the model lacks exposure to "
            "long-horizon prediction during training and fails to effectively handle "
            "compounding errors."),
        "form": "qualitative",
        "numeral_in_text": False,
        "note": ("The only numeral in the passage is the configuration N=1, which names the "
                 "teacher-forcing setting rather than measuring its cost."),
    },
    {
        "key": "epistemic_trust",
        "claim": ('Epistemic uncertainty "closely follows the trend of the prediction error", '
                  'justifying "its role as a trust metric"'),
        "where_v1": "2504.16680v1 5.1",
        "where_v2": None,
        "where_v3": "2504.16680v3 5.1 (section number unchanged; the figure moved, "
                    "see followup_version_map)",
        "original_figure": None,
        "original_states": (
            "the estimated epistemic uncertainty (dark blue) closely follows the trend of the "
            "prediction error, demonstrating that RWM-O effectively captures uncertainty in "
            "regions where the model generalization deteriorates. ... The strong correlation "
            "between epistemic uncertainty and model prediction error justifies its role as a "
            "trust metric for policy optimization."),
        "form": "qualitative; shown in Figure 2 (right) [v1] = Figure 3 (right) [v3]",
        "numeral_in_text": False,
        "note": ('The paper asserts a "strong correlation" and gives no correlation coefficient, '
                 "no interval and no sample size. Our +0.605 [+0.545, +0.694] at n_independent "
                 "= 20 appears to be the first number attached to this claim."),
    },
    {
        "key": "aleatoric_low",
        "claim": 'Aleatoric uncertainty "remains low, reflecting small stochasticity"',
        "where_v1": "2504.16680v1 5.1",
        "where_v2": None,
        "where_v3": "2504.16680v3 5.1 (section number unchanged; the figure moved, "
                    "see followup_version_map)",
        "original_figure": None,
        "original_states": (
            "the aleatoric uncertainty (light blue) remains low, reflecting small stochasticity "
            "in the environment."),
        "form": "qualitative; shown in Figure 2 (right) [v1] = Figure 3 (right) [v3]",
        "numeral_in_text": False,
        "note": ('"Low" is relative to the plotted epistemic curve on the same axes; no absolute '
                 "value, ratio or comparison against realised error is given."),
    },
]

# The one place either paper does give numbers for something we discuss, even
# though we did not test it -- recorded so the table's sample-efficiency row can
# cite the original rather than leave the cell empty.
SAMPLE_EFFICIENCY = {
    "where_v1": "2501.10100v1 Table I (Limitations)",
    "figures": {"RWM pretraining state transitions": "6M",
                "PPO state transitions": "250M",
                "RWM pretraining time": "50 min",
                "MBPO-PPO training time": "5 min",
                "PPO training time": "10 min",
                "MBPO-PPO real tracking reward": "0.90 +- 0.04",
                "PPO real tracking reward": "0.90 +- 0.03"},
    "note": ("The only table of numbers in either paper. It reports parity on the real tracking "
             "reward at a ~42x reduction in state transitions."),
}


# V4 — the follow-up is version-pinned the way 2501.10100 already was.
#
# We read 2504.16680 at v1 (23 Apr 2025). It is now at v3, last revised 8 Jan
# 2026 and substantially expanded: a Related Work section, a new training
# diagram, a results table and two more deployment figures. A reviewer opening
# the current version will not find our figure references where we put them.
#
# What did NOT move, checked against both HTML renderings: section 5.1 keeps its
# number, and Eq. 4 (u = Var_b[mu_b]) and Eq. 5 (r~ = r - lambda u) keep theirs
# and are character-identical. So every SECTION and EQUATION reference in our
# paper resolves in v3 unchanged. What moved is every FIGURE and every appendix
# TABLE, and the model was renamed RWM-O -> RWM-U.
FOLLOWUP_VERSIONS = {
    "arxiv_id": "2504.16680",
    "we_read": "v1",
    "we_read_dated": "23 Apr 2025",
    "current": "v3",
    "current_dated": "8 Jan 2026",
    "all_versions": [
        {"version": "v1", "date": "23 Apr 2025", "size_kb": 7854},
        {"version": "v2", "date": "7 Jan 2026", "size_kb": 38854},
        {"version": "v3", "date": "8 Jan 2026", "size_kb": 38854},
    ],
    "checked_on": "2026-08-23",
    "method": "both HTML renderings fetched and compared: figure and table captions "
              "enumerated from <figcaption>, equations located by their rendered "
              "bodies, section headings enumerated from the document outline",
    "unchanged": [
        {"what": "section 5.1", "v1": "5.1 Autoregressive Uncertainty Estimation",
         "v3": "5.1 Autoregressive Uncertainty Estimation",
         "note": "both quoted sentences are in it in both versions"},
        {"what": "Eq. 4", "v1": "Eq. 4", "v3": "Eq. 4",
         "body": "u_{t+1} = u_{p_phi}(...) = Var_b[mu^b_{o_{t+1}}]",
         "note": "character-identical rendering in both"},
        {"what": "Eq. 5", "v1": "Eq. 5", "v3": "Eq. 5",
         "body": "r~(o_t,a_t) = r_t(o_t,a_t) - lambda u_{p_phi}(...)",
         "note": "character-identical rendering in both"},
        {"what": "imagination steps per iteration", "v1": "100 (Table S9)",
         "v3": "100 (Table S11)",
         "note": "the value is unchanged; only the table number moved. v3 adds the "
                 "same figure in prose: '100-step episodic rollouts'"},
    ],
    "moved": [
        {"what": "uncertainty estimation figure — the one our 5.1, 5.2 and 5.6 discuss",
         "v1": "Figure 2 (right)", "v3": "Figure 3 (right)",
         "caption_v3_adds": "The epistemic uncertainty estimate by RWM-U aligns with the "
                            "long-horizon prediction error and thus sets a reliable metric "
                            "in policy training."},
        {"what": "epistemic uncertainty under three penalty weights during MOPO-PPO "
                 "training — where our section 3 table says the aleatoric term is reported",
         "v1": "Figure 3 (right)", "v3": "Figure 4 (right)"},
        {"what": "normalised episodic rewards across environments",
         "v1": "Figure 4", "v3": "Figure 5"},
        {"what": "MOPO-PPO training hyperparameters, including the imagination horizon",
         "v1": "Table S9", "v3": "Table S11"},
        {"what": "world-model architecture table", "v1": "Table S6 (RWM-O architecture)",
         "v3": "Table S7 (RWM-U architecture)"},
        {"what": "world-model training parameters", "v1": "Table S8", "v3": "Table S10"},
        # C4(rev2), 4.4. This claim was challenged: a reviewer read the public v3
        # as containing BOTH names -- RWM-U in the abstract and RWM-O in the
        # experiments -- which would make them two variants rather than one
        # rename. Re-checked against the rendered HTML of all three versions on
        # 28 Aug 2026, by counting occurrences rather than by reading:
        #
        #   v1  RWM-O x39   RWM-U x0
        #   v2  RWM-O x0    RWM-U x43
        #   v3  RWM-O x0    RWM-U x43
        #
        # The two names are disjoint across versions, and the introducing
        # sentence is otherwise word-for-word identical in v1 and v3. What
        # changed is the EXPANSION of the O/U: "Offline" became
        # "Uncertainty-Aware". It is a rename of one model, the claim stands,
        # and the expansions are recorded here because they are what makes it
        # checkable rather than asserted.
        {"what": "the model's name", "v1": "RWM-O", "v3": "RWM-U",
         "v1_expansion": "Offline Robotic World Model",
         "v3_expansion": "Uncertainty-Aware Robotic World Model",
         "v1_sentence": "To this end, we introduce Offline Robotic World Model (RWM-O), "
                        "where we explicitly incorporate uncertainty quantification",
         "v3_sentence": "To this end, we introduce Uncertainty-Aware Robotic World Model "
                        "(RWM-U), where we explicitly incorporate uncertainty quantification",
         "occurrences": {"v1": {"RWM-O": 39, "RWM-U": 0},
                         "v2": {"RWM-O": 0, "RWM-U": 43},
                         "v3": {"RWM-O": 0, "RWM-U": 43}},
         "occurrences_checked_on": "2026-08-28",
         "occurrences_method": "arxiv.org/html/2504.16680v{1,2,3} fetched and the two "
                               "strings counted; no version contains both",
         "note": "a rename, not a different model, and the two names never co-occur: v1 "
                 "uses RWM-O throughout and v2/v3 use RWM-U throughout. The introducing "
                 "sentence is identical but for the expansion, and the architecture tables "
                 "and Eq. 4 are unchanged. Our paper quotes v1 sentences containing "
                 "'RWM-O'."},
    ],
    "consequence": "every in-text citation of 2504.16680 in this paper names the version "
                   "it was read from, and the reference-list entry pins v1 with the v3 "
                   "revision date recorded. Section and equation references resolve in "
                   "both; figure references need the map above, which is why it is here.",
}


def main():
    out = {"read_on": READ_ON,
           "sources": ["arXiv:2501.10100v1 (17 Jan 2025)",
                       "arXiv:2501.10100v2 (23 Apr 2025)",
                       "arXiv:2504.16680v1 (23 Apr 2025)"],
           "evidence_class": "EXT — transcribed from the published papers, not computed",
           "version_note": (
               "Our section references use v1's Roman-numeral sectioning (IV-C, IV-D, IV-E). "
               "v2 renumbered to Arabic and moved IV-C's material into Appendix A.4.1, so a "
               "reader opening the current arXiv version will not find IV-C. Both locations are "
               "recorded for every claim. The follow-up 2504.16680 gets the same treatment in "
               "followup_version_map: we read v1, it is now at v3, sections and equations are "
               "unchanged and every figure and appendix table has moved."),
           "followup_version_map": FOLLOWUP_VERSIONS,
           "claims": CLAIMS,
           "sample_efficiency": SAMPLE_EFFICIENCY,
           "n_tested_claims": len(CLAIMS),
           "n_with_quantitative_figure": sum(1 for c in CLAIMS if c["numeral_in_text"]),
           "n_without": sum(1 for c in CLAIMS if not c["numeral_in_text"])}

    print("A6 — WHAT THE ORIGINALS REPORT FOR EACH CLAIM WE TESTED")
    print("=" * 100)
    for c in CLAIMS:
        print(f"\n  {c['claim']}")
        print(f"    {c['where_v1']}" + (f"   ({c['where_v2']} in v2)" if c["where_v2"] else ""))
        print(f"    figure given : {c['original_figure'] or 'NONE — ' + c['form']}")
        print(f"    states       : \"{c['original_states'][:120]}...\"")
    print(f"\n  {out['n_without']} of {out['n_tested_claims']} tested claims are stated with no "
          f"quantitative figure at all.")
    op = os.path.join(R.RESULTS, "original_paper_figures.json")

    # verify_original_quotes.py writes a `verification` block into this same file
    # -- the record that every EXT quotation was matched as a substring of the
    # published HTML. It needs the network, so it is not a reproduce.sh stage and
    # cannot simply be re-run after this one. This script used to rewrite the file
    # wholesale and silently drop that block, which is the difference between a
    # verified quotation and an asserted one. Carry it forward.
    if os.path.exists(op):
        prev = json.load(open(op))
        if "verification" in prev:
            out["verification"] = prev["verification"]
            print(f"\n  carried forward the verification block "
                  f"({prev['verification'].get('n_verbatim')} of "
                  f"{prev['verification'].get('n_checked')} quotations verbatim, "
                  f"checked {prev['verification'].get('date')})")
        else:
            print("\n  NOTE: no verification block to carry forward. Run "
                  "scripts/verify_original_quotes.py to add one.")

    json.dump(out, open(op, "w"), indent=2)
    print(f"\n  wrote {R.rel(op)}")


if __name__ == "__main__":
    main()
