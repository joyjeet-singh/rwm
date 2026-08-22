"""C2 — the data budget: how many distinct state transitions our arms consume.

The base paper's Table I reports world-model pretraining on 6M state transitions.
That figure sits inside a sample-efficiency claim about POLICY learning, which
this work does not test. But the world-model half of it is a claim about the same
quantity we can measure exactly -- state transitions consumed by dynamics-model
training -- so the comparison is available and is the strongest thing this paper
can say about the base paper's headline result.

The count is of DISTINCT transitions, not training windows. The 7,687 windows the
arms train on overlap heavily: a window is a 33-step slice and consecutive windows
start one row apart, so counting windows would overstate the data by more than an
order of magnitude. A transition is a consecutive (row, row+1) pair within one
episode, so an episode of n rows contributes n-1, and boundaries contribute none.

Writes results/task_c2_data_budget.json.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import rwm_data as R  # noqa: E402
import rollout_eval as E  # noqa: E402

REFERENCE_TRANSITIONS = 6_000_000      # 2501.10100 Table I, "state transitions", RWM pretraining


def main():
    paths = R.repo_paths()
    data, episode_id = R.load_data(paths["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"),
                         verbose=False)
    train = sorted(split["train_episodes"])
    hold = sorted(split["holdout_episodes"])

    per_ep = {}
    for e in sorted(set(episode_id[episode_id >= 0])):
        rows = int((episode_id == e).sum())
        per_ep[int(e)] = {"rows": rows, "transitions": rows - 1}

    train_rows = sum(per_ep[e]["rows"] for e in train)
    train_trans = sum(per_ep[e]["transitions"] for e in train)
    all_rows = sum(v["rows"] for v in per_ep.values())
    all_trans = sum(v["transitions"] for v in per_ep.values())

    # the window count, for contrast: this is what a naive reading would report
    ref = json.load(open(os.path.join(R.RESULTS, "step5_armA_seed0.json")))
    windows = ref["hyperparameters"]["n_train_windows"]

    # what one training run actually draws, which is a third quantity again
    iters = ref["hyperparameters"]["iterations"]
    batch = ref["hyperparameters"]["batch"]

    out = {
        "reference": {"source": "arXiv:2501.10100v1 Table I",
                      "quantity": "state transitions, RWM pretraining",
                      "value": REFERENCE_TRANSITIONS},
        "ours": {
            "train_episodes": train, "holdout_episodes": hold,
            "rows_in_training_episodes": train_rows,
            "distinct_transitions": train_trans,
            "boundaries_excluded": len(train),
            "training_windows": windows,
            "window_draws_per_run": iters * batch,
            "note": ("a transition is a consecutive (row, row+1) pair inside one episode, so an "
                     "episode of n rows gives n-1 and the 8 episode boundaries give none; the "
                     "window count is larger because 33-step windows starting one row apart "
                     "overlap almost completely"),
        },
        "whole_dataset": {"rows": all_rows, "distinct_transitions": all_trans},
        "per_episode": per_ep,
        "ratio_reference_over_ours": REFERENCE_TRANSITIONS / train_trans,
        "ours_as_fraction_of_reference": train_trans / REFERENCE_TRANSITIONS,
    }

    print("C2 — DATA BUDGET")
    print("=" * 92)
    print(f"  training episodes {train}")
    print(f"    rows                      {train_rows:>12,}")
    print(f"    episode boundaries        {len(train):>12,}  (contribute no transition)")
    print(f"    DISTINCT TRANSITIONS      {train_trans:>12,}")
    print(f"    training windows          {windows:>12,}  (overlapping; not a data count)")
    print(f"    window draws per run      {iters*batch:>12,}  (iterations x batch, with replacement)")
    print(f"  whole dataset               {all_trans:>12,} transitions over {all_rows:,} rows")
    print()
    print(f"  reference (Table I)         {REFERENCE_TRANSITIONS:>12,} state transitions")
    print(f"  ratio                       {out['ratio_reference_over_ours']:>12,.0f}x more than ours")
    print(f"  ours as a fraction          {100*out['ours_as_fraction_of_reference']:>12.3f}% of the reference budget")

    op = os.path.join(R.RESULTS, "task_c2_data_budget.json")
    json.dump(out, open(op, "w"), indent=2)
    print(f"\n  wrote {R.rel(op)}")


if __name__ == "__main__":
    main()
