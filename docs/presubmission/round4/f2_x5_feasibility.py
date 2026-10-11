"""F2 item 1: rule X5's feasibility table and gate (PLAN round 4, F2 item 1 and Annex 2 X5), written to
docs/presubmission/round4/X5_FEASIBILITY.md.

One row per reward term the imagination environment computes (lite/scripts/envs/anymal_d_flat.py's
_compute_imagination_reward_terms, which round4/PREFLIGHT.md PF4 records), plus the penalty. For each:
its line, its inputs, whether it can be computed from the recorded data and from the model's outputs, its
weight, and whether base.py scales it by dt. Line numbers and weights are read from the files.

THE GATE (Annex 2 X5): X5 runs only if every term of a reward subset is computable from both the recorded
data and the model's outputs; the subset must include at least the command-tracking terms
(track_lin_vel_xy_exp and track_ang_vel_z_exp) and is otherwise every term that qualifies. If the tracking
terms do not qualify, X5 is NOT RUN.

What "the recorded data" means: the 66 columns of the released CSV (src/rwm_data.py's column map), which this
script asserts hold no command. What "the model's outputs" means: the forecast state (45 columns) and the
contact and termination heads, driven by the recorded actions. The command the tracking terms read is the
environment's own sampled state (base_velocity), neither recorded nor forecast.
Run from the repository root:  $PY docs/presubmission/round4/f2_x5_feasibility.py
"""
import os
import re
import sys

sys.path.insert(0, "src")
import rwm_data as R  # noqa: E402

LITE = "../robotic_world_model_lite/scripts"
ENV, BASE, ECFG = f"{LITE}/envs/anymal_d_flat.py", f"{LITE}/envs/base.py", f"{LITE}/configs/anymal_d_flat_cfg.py"
OUT = "docs/presubmission/round4/X5_FEASIBILITY.md"


def at(path, needle):
    hits = [i + 1 for i, l in enumerate(open(path, encoding="utf-8")) if needle in l]
    assert hits, (path, needle)
    return hits[0]


env = open(ENV, encoding="utf-8").read()
wtxt = open(ECFG, encoding="utf-8").read()
weights = dict(re.findall(r'"(\w+)": (-?[0-9.e-]+)', wtxt.split("reward_term_weights")[1].split("})")[0]))
pen_w = re.search(r"uncertainty_penalty_weight: float = (-?[0-9.]+)", wtxt).group(1)
# the terms base.py sums: every key of the weights dict, plus "uncertainty"
CMD = "the command (`base_velocity`), which the environment samples and the data do not hold"
# term -> (needle, inputs, data, model, why)
T = {
    "track_lin_vel_xy_exp": ("track_lin_vel_xy_exp = ", "command xy against base linear velocity xy",
                             "no", "no", f"needs {CMD}"),
    "track_ang_vel_z_exp": ("track_ang_vel_z_exp = ", "command yaw rate against base angular velocity z",
                            "no", "no", f"needs {CMD}"),
    "lin_vel_z_l2": ("lin_vel_z_l2 = ", "base linear velocity z", "yes", "yes", "state columns only"),
    "ang_vel_xy_l2": ("ang_vel_xy_l2 = ", "base angular velocity xy", "yes", "yes", "state columns only"),
    "dof_torques_l2": ("dof_torques_l2 = ", "joint torques", "yes", "yes", "state columns only"),
    "dof_acc_l2": ("dof_acc_l2 = ", "joint velocity minus the previous observation's columns 12:24 (joint positions), over dt",
                   "partly", "partly", "the previous observation carries the environment's observation noise, so only a "
                   "noise-free version is computable; the upstream subtraction mixes velocity and position (OUT_OF_SCOPE, F0)"),
    "action_rate_l2": ("action_rate_l2 = ", "the previous action against the current one", "yes", "yes",
                       "recorded actions; the forecast does not enter"),
    "feet_air_time": ("feet_air_time = torch.sum", "foot contacts, environment-held air and contact timers, gated by the command's xy norm",
                      "partly", "partly", f"contacts and timers are computable, the gate needs {CMD}"),
    "undesired_contacts": ("undesired_contacts = ", "thigh contacts", "yes", "yes", "contact labels; the contact head"),
    "stand_still": ("stand_still = ", "joint positions, gated by the command's norm", "partly", "partly", f"the gate needs {CMD}"),
    "flat_orientation_l2": ("flat_orientation_l2 = ", "projected gravity xy", "yes", "yes", "state columns only"),
    "dof_pos_limits": ("dof_pos_limits = ", "none (identically zero)", "yes", "yes", "a constant"),
}
assert set(T) == set(weights), (sorted(T), sorted(weights))
dt_line = at(BASE, "rewards += self.reward_term_weights[term] * term_value * self._step_dt")
pen_line = at(BASE, "rewards += self.uncertainty_penalty_weight * self.epistemic_uncertainty * self._step_dt")
n_cols = R.load_data(R.repo_paths()["csv"], verbose=False)[0].shape[1]
mapped = sorted(set(R.STATE_COLS) | set(R.ACTION_COLS) | set(R.CONTACTS) | {R.TERMINATION})
assert mapped == list(range(n_cols)), "the column map does not cover every column: a command column could hide"

rows = []
for term, (needle, inp, d, m, why) in T.items():
    rows.append(f"| `{term}` | `anymal_d_flat.py:{at(ENV, needle)}` | {inp} | {d} | {m} | {weights[term]} | yes (`base.py:{dt_line}`) | {why} |")
rows.append(f"| `uncertainty` (the penalty) | `base.py:{pen_line}` | the ensemble's epistemic uncertainty | n/a | yes | {pen_w} | yes | "
            "a model output; X5's P, not part of the reward subset |")
qual = [t for t, v in T.items() if v[2] == "yes" and v[3] == "yes"]
tracking = ("track_lin_vel_xy_exp", "track_ang_vel_z_exp")
runs = all(t in qual for t in tracking)
md = ["# Rule X5 — feasibility (F2 item 1)\n",
      "Generated by `docs/presubmission/round4/f2_x5_feasibility.py`. Line numbers and weights are read from the pinned "
      "`robotic_world_model_lite` (13a798e9). `lite` paths are relative to `robotic_world_model_lite/scripts/`.\n",
      f"**The recorded data** are the released CSV's {n_cols} columns, all of which `src/rwm_data.py`'s column map assigns: "
      f"state (45), actions (12), contact labels (8), termination (1). There is no command column (asserted). "
      f"The environment samples its command at `envs/anymal_d_flat.py:{at(ENV, 'def _init_imagination_command')}` and "
      f"`:{at(ENV, 'def _reset_imagination_command')}`; the repository infers the commanded regimes from achieved velocity "
      f"instead (`scripts/step0_velocity_regimes.py:{at('scripts/step0_velocity_regimes.py', 'commanded velocity is not recorded')}`).\n",
      "**The model's outputs** are the forecast state and the contact and termination heads, driven by the recorded actions. "
      "The command is not an output.\n",
      "| Term | file:line | Inputs | From the recorded data? | From the model's outputs? | Weight | dt-scaled? | Why |",
      "|---|---|---|---|---|---:|---|---|"] + rows + [
      "",
      "## The gate\n",
      f"Annex 2 X5 runs the rule only if the command-tracking terms ({', '.join('`' + t + '`' for t in tracking)}) qualify. "
      f"They do not: each needs {CMD}. "
      + ("**X5 runs.**" if runs else
         "**X5 is NOT RUN.** No reward subset is defined. Inferring the command from the recorded base velocity would not "
         "make it recorded data. It would also make the tracking reward of the recorded trajectory high by construction, "
         "since the command would be fitted to the very velocities the term scores. The terms that would qualify on their "
         "own (" + ", ".join("`" + t + "`" for t in qual) + ") carry none of the reward's purpose, which is to follow the "
         "command, and Annex 2 does not allow a subset without the tracking terms."),
      ""]
open(OUT, "w", encoding="utf-8").write("\n".join(md) + "\n")
print(f"wrote {OUT}: X5 {'RUNS' if runs else 'NOT RUN'}; qualifying terms {qual}")
