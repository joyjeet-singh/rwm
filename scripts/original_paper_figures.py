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
        "original_figure": None,
        "original_states": (
            "the estimated epistemic uncertainty (dark blue) closely follows the trend of the "
            "prediction error, demonstrating that RWM-O effectively captures uncertainty in "
            "regions where the model generalization deteriorates. ... The strong correlation "
            "between epistemic uncertainty and model prediction error justifies its role as a "
            "trust metric for policy optimization."),
        "form": "qualitative; shown in Figure 2 (right)",
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
        "original_figure": None,
        "original_states": (
            "the aleatoric uncertainty (light blue) remains low, reflecting small stochasticity "
            "in the environment."),
        "form": "qualitative; shown in Figure 2 (right)",
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
               "recorded for every claim."),
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
    json.dump(out, open(op, "w"), indent=2)
    print(f"\n  wrote {R.rel(op)}")


if __name__ == "__main__":
    main()
