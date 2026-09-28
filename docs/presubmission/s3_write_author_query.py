"""S3 item 4 -- fill PLAN Appendix D's author query and write AUTHOR_QUERY_ALIGNMENT.md.

Nothing in the letter is typed. The commits are read from the two upstream checkouts and asserted
to be the pinned ones; each cited line is asserted to hold the slice the letter describes; the
reset-row claim is re-checked against the data; every figure is read from
results/alignment_defect_ci.json. The letter is a draft: the user sends it, and no paper sentence
may say the author was asked or confirmed (PLAN S3 item 4).

    python docs/presubmission/s3_write_author_query.py
"""
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
sys.path.insert(0, os.path.join(ROOT, "src"))
import numpy as np  # noqa: E402

import rwm_data as R  # noqa: E402

LITE = os.path.join(ROOT, os.pardir, "robotic_world_model_lite")
RSL = os.path.join(ROOT, os.pardir, "rsl_rl_rwm")
PIN = {"lite": "13a798e9", "rsl": "18eebcdd"}          # PDM/CLAUDE.md
TRAIN = ("rsl_rl/modules/system_dynamics.py", 195, 200,
         {196: "action_batch[:, self.history_horizon + i:self.history_horizon + i + 1]",
          200: "action_batch[:, i + 1:self.history_horizon + i + 1]",
          181: "x_state_batch = state_batch[:, :self.history_horizon]"})
EVAL = ("scripts/model_training.py", 127, 132,
        {128: "state_traj_pred[:, i - 1:i]", 129: "action_traj_pred[:, i - 1:i]",
         131: "state_traj_pred[:, i - self.start_step:i]",
         132: "action_traj_pred[:, i - self.start_step:i]"})


def head(repo):
    return subprocess.run(["git", "-C", repo, "rev-parse", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()


def check_lines(repo, spec):
    path, _, _, want = spec
    lines = open(os.path.join(repo, path), encoding="utf-8").read().split("\n")
    for n, s in want.items():
        assert s in lines[n - 1], f"{path}:{n} no longer holds {s!r}"


def main():
    h_lite, h_rsl = head(LITE), head(RSL)
    assert h_lite.startswith(PIN["lite"]) and h_rsl.startswith(PIN["rsl"]), (h_lite, h_rsl)
    check_lines(RSL, TRAIN)
    check_lines(LITE, EVAL)

    reg = json.load(open(os.path.join(ROOT, "results", "step0_regimes.json")))
    resets = reg["window_accounting"]["reset_rows"]
    data, ep = R.load_data(R.repo_paths()["csv"], verbose=False)
    n_ep = int((np.unique(ep) >= 0).sum())          # the orphan row is labelled -1
    acts = data[np.asarray(resets)][:, R.ACTION_COLS]
    assert (acts == 0).all(), "an action at a reset row is not exactly zero"
    n_reset, n_act = len(resets), len(R.ACTION_COLS)

    A = json.load(open(os.path.join(ROOT, "results", "alignment_defect_ci.json")))
    h4, h20 = A["arenas"]["held_out_n4"], A["arenas"]["all_ten_n20"]
    o4, c4, o20 = h4["overstatement_pct"], h4["ci95_pct"], h20["overstatement_pct"]
    assert all(o4[k] > 0 for k in ("nrmse_form1", "rel_l1")), "the n = 4 sign changed; rewrite"
    assert all(o20[k] < 0 for k in ("nrmse_form1", "rel_l1")), "the n = 20 sign changed; rewrite"
    assert all(h20["ci95_pct"][k][0] < 0 < h20["ci95_pct"][k][1] for k in ("nrmse_form1", "rel_l1"))
    f = lambda x: f"{x:.1f}".replace("-", "−")
    ci = lambda c: f"[{f(c[0])}, {f(c[1])}]"
    words = {4: "four", 10: "ten", 12: "twelve", 20: "twenty"}
    w = lambda n: words.get(n, str(n))

    letter = f"""> Subject: RWM-U release — action alignment in the evaluation script
>
> Dear [first author],
>
> Thank you again for your help in August with Eq. 4 and the aleatoric term. We have one more question, about the lite release at commit {h_lite[:8]} (with rsl_rl_rwm at {h_rsl[:8]}).
>
> In training (`{TRAIN[0]}:{TRAIN[1]}-{TRAIN[2]}`), the state at step t+1 is paired with the action in the same row. In evaluation (`{EVAL[0]}:{EVAL[1]}-{EVAL[2]}`), it is paired with the action one row earlier. Our reading of the dataset is that row t holds the action that produced state t. At all {w(n_reset)} episode resets the {w(n_act)} actions are exactly zero, which a policy network with biases would not output. Under that reading the training pairing is the intended one, and the evaluation pairing is one step stale. On {w(h4['n_trajectories'])} non-overlapping 400-step trajectories, the released checkpoint's error over a {A['horizon']}-step horizon is {f(o4['nrmse_form1'])}% {ci(c4['nrmse_form1'])} higher in nRMSE and {f(o4['rel_l1'])}% {ci(c4['rel_l1'])} higher in relative-L1 under the evaluation pairing than under the training pairing (95% intervals from a bootstrap over whole trajectories). Across {w(h20['n_trajectories'])} such trajectories drawn from all {w(n_ep)} episodes the difference reverses sign ({f(o20['nrmse_form1'])}% and {f(o20['rel_l1'])}%, both intervals spanning zero), so we read the cost in error as small. Our question is about the alignment itself.
>
> Could you confirm which pairing is intended? And, as with the earlier exchange, may we quote your reply?
>
> Best regards,
> [name]
"""

    doc = f"""# Author query — action alignment (DRAFT, NOT SENT)

Filled in by S3 from PLAN Appendix D, by `docs/presubmission/s3_write_author_query.py`, which
typed none of it. **The user sends it; nothing here has been sent.** No paper sentence says the
author was asked or confirmed, and none may until a reply exists.

{letter}
## Where each filled value comes from

| Placeholder | Filled with | Source |
|---|---|---|
| [pinned hash] | lite `{h_lite}`, rsl_rl_rwm `{h_rsl}` | `git rev-parse HEAD` in each upstream checkout, asserted equal to the pins in the project's working rules |
| [file:line], training | `rsl_rl_rwm/{TRAIN[0]}:{TRAIN[1]}-{TRAIN[2]}` | :181 takes states from rows 0..H−1, :200 actions from rows 1..H, and the target is row H. The recurrent branch (:196, after the first step) takes the target's own row. |
| [file:line], evaluation | `robotic_world_model_lite/{EVAL[0]}:{EVAL[1]}-{EVAL[2]}` | :131-132 slice states and actions over the same rows i−H..i−1 to predict row i. The recurrent branch (:128-129, after the first step) takes row i−1 for both. |
| "all {w(n_reset)} episode resets" | rows {resets[0]:,} … {resets[-1]:,} | `results/step0_regimes.json` `window_accounting.reset_rows`; every action at those rows re-checked as exactly zero against the data |
| [X], nRMSE | {f(o4['nrmse_form1'])}% {ci(c4['nrmse_form1'])} | `results/alignment_defect_ci.json` `arenas.held_out_n4`, nRMSE form 1 (§3.1's primary) |
| [Y], relative-L1 | {f(o4['rel_l1'])}% {ci(c4['rel_l1'])} | the same, `rel_l1` |
| the reversal | {f(o20['nrmse_form1'])}%, {f(o20['rel_l1'])}% | the same, `arenas.all_ten_n20` |

**Changed from Appendix D's wording, and why:**
- **"[X]% lower" is now "[X]% higher under the evaluation pairing".** The paper's figure is
  err(evaluation pairing) / err(training pairing) − 1. Written as "lower", the same number would
  be a different quantity.
- **The {w(n_ep)}-episode reversal is added.** The user's ruling (`DECISIONS_FOR_USER.md#S3-alignment-defect`)
  restates the defect on independent trajectories. The reversal is part of what those show, and
  a letter quoting only the positive arena would overstate the cost.
- **Appendix D's single [pinned hash] names both repositories**, because the training line
  is in rsl_rl_rwm and the evaluation line is in lite.
- **Every arena is in-sample for the released checkpoint.** It trained on every episode. The
  letter says "trajectories", not "held-out".

[first author] and [name] stay placeholders. The first author's name is on the anonymity
deny-list, and the user fills it in on sending.
"""
    out = os.path.join(ROOT, "docs", "presubmission", "AUTHOR_QUERY_ALIGNMENT.md")
    open(out, "w", encoding="utf-8").write(doc)
    print(f"wrote {os.path.relpath(out, ROOT)}")


if __name__ == "__main__":
    main()
