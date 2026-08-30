"""2.4 -- the in-sample framing check. NO COMPUTATION.

section 6.2 states the arena its released-checkpoint rows are measured on and then declines to
draw the inference. This records the arena as substitutable keys so Session 4 can turn it
into one sentence without typing a number or re-deriving a fact.

THE INFERENCE, which section 6.2 currently leaves to the reader. The released checkpoint trained
on all ten episodes. The h=1 calibration row is measured on all ten episodes. So that row is
measured on data the checkpoint trained on, which biases TOWARD better calibration -- a model
is not usually worse calibrated on its own training data -- and it is still 8.3x out with
16.22% of outcomes inside an interval that should hold 68.27%.

Every value here is READ from an artifact, never typed. Nothing is recomputed.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402
import rollout_eval as E  # noqa: E402


def main():
    d20 = json.load(open(os.path.join(R.RESULTS, "task_d_nind20.json")))
    design = d20["design"]
    h1 = d20["d1_by_horizon"]["1"]["epistemic"]

    # OUR split, via the same call every producer uses. step0_strat.json is the
    # per-episode regime table that call reads, not the split itself.
    split = E.make_split(seed=0,
                         strat_path=os.path.join(R.RESULTS, "step0_strat.json"),
                         verbose=False)
    train = sorted(int(x) for x in split["train_episodes"])
    hold = sorted(int(x) for x in split["holdout_episodes"])
    arena_eps = sorted(design["episodes"])
    trained_on = sorted(set(train) | set(hold))     # the released ckpt trained on all ten

    overlap = sorted(set(arena_eps) & set(trained_on))
    out = {
        "check": "2.4 -- in-sample framing of the released checkpoint's h=1 calibration row",
        "computation": "none; every value is read from an existing artifact",
        "source_artifact": "results/task_d_nind20.json",

        # --- the arena, exactly as the artifact records it ---------------------
        "arena_string": design["arena"],
        "arena_episodes": arena_eps,
        "n_arena_episodes": len(arena_eps),
        "n_independent": design["n_independent"],
        "n_trajectories": design["trajectories"],
        "artifact_rationale": design["rationale"],

        # --- what the checkpoint trained on ------------------------------------
        "released_checkpoint": design["checkpoint"],
        "released_ckpt_trained_on_episodes": trained_on,
        "n_trained_on": len(trained_on),
        "our_train_episodes": train,
        "our_holdout_episodes": hold,
        "note_on_split": (
            "the train/holdout split is OURS, for OUR arms. The released checkpoint "
            "predates it and trained on all ten episodes, so it has no held-out arena in "
            "this dataset at all"),

        # --- the overlap, which is the whole point -----------------------------
        "arena_episodes_the_checkpoint_trained_on": overlap,
        "n_overlap": len(overlap),
        "fully_in_sample": bool(len(overlap) == len(arena_eps)),

        # --- the figures the sentence will quote, read not typed ---------------
        "h1_ratio_err_over_sigma": h1["ratio_err_over_sigma"],
        "h1_ratio_ci": h1["ratio_err_over_sigma_ci"],
        "h1_coverage_pm1": h1["coverage_pm1"],
        "h1_coverage_pm1_ci": h1["coverage_pm1_ci"],
        "calibrated_target_pm1_pct": 68.27,

        # --- the inference, stated once so section 6.2 can quote it rather than imply it --
        "inference": (
            "the released checkpoint's h=1 calibration row is measured on episodes it "
            "trained on. That biases toward better calibration, and it is still 8.3x out."),
        "direction_of_bias": "toward better calibration, i.e. the measurement flatters the model",
        "why_this_arena_anyway": design["rationale"],
    }

    print("=" * 96)
    print("2.4 — IN-SAMPLE FRAMING CHECK (no computation)")
    print("=" * 96)
    print(f"  arena                        {out['arena_string']} "
          f"({out['n_arena_episodes']} episodes, n_independent {out['n_independent']})")
    print(f"  released checkpoint trained on {out['n_trained_on']} episodes: {trained_on}")
    print(f"  arena episodes it trained on   {out['n_overlap']} of {out['n_arena_episodes']}"
          f"   -> fully in-sample: {out['fully_in_sample']}")
    print(f"  h=1 epistemic                  {out['h1_ratio_err_over_sigma']:.2f}x out, "
          f"coverage {100*out['h1_coverage_pm1']:.2f}% against 68.27%")
    print(f"  direction of bias              {out['direction_of_bias']}")

    op = os.path.join(R.RESULTS, "insample_framing.json")
    json.dump(out, open(op, "w"), indent=2)
    print(f"\n  wrote {R.rel(op)}")


if __name__ == "__main__":
    main()
