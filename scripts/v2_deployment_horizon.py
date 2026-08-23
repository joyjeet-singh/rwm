"""
V2 -- what "the deployment horizon" actually is, established from configuration.

The paper calls h=368 "the deployment horizon" and puts the numbers measured
there in the abstract. Nothing defends the label. This script finds every
horizon the method configures, from source, and reports which one the method's
own rollouts run to.

The answer is that 368 is not a deployment horizon of any kind. It is the
length of the upstream's OPEN-LOOP DIAGNOSTIC:

    len_eval_trajectory = 400            base_cfg.py:46, mbpo_ppo.py:61
    minus history_horizon = 32           teacher-forced prefix, mbpo_ppo.py:284
    = 368 autoregressive steps

which is exactly the curve the follow-up plots as its uncertainty figure. Our
h=368 inherits that length because our harness reproduces that evaluation. It
is a diagnostic horizon, and calling it a deployment horizon overstates it.

The horizon the METHOD runs its world model over, when it is doing the thing
the method is for -- optimising a policy on uncertainty-penalised imagination
-- is 100 steps: the follow-up's own hyperparameter table, in both the version
we read and the current one. The shipped `lite` release caps an imagined
episode at 256 instead, which is a different default in a reduced release; both
are recorded below and neither is 368.

Consequence, applied in the paper: the headline is re-anchored to h=100, which
is added to the evaluation grid so the method's own horizon is measured
directly rather than approximated by the nearest grid point. The h=368 row
stays in every table, relabelled as the open-loop diagnostic horizon.

The external figures here are transcribed from the published papers (evidence
class EXT) and are verified as substrings of the arXiv HTML by
scripts/verify_original_quotes.py. Everything else is read from pinned source.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402
import rwm_metrics as M  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, os.pardir))
PDM = os.path.abspath(os.path.join(REPO, os.pardir))
RSL = os.path.join(PDM, "rsl_rl_rwm")
RWML = os.path.join(PDM, "robotic_world_model_lite")


def cite(path, line, must_contain, note):
    """Read path:line back and assert a fingerprint. See v1_ensemble_topology.py."""
    with open(path) as f:
        lines = f.read().split("\n")
    assert 1 <= line <= len(lines), f"{path}:{line} past end of file"
    text = lines[line - 1]
    assert must_contain in text, (
        f"citation drift at {path}:{line}\n  expected: {must_contain!r}\n"
        f"  actual:   {text.strip()!r}")
    return {"cite": f"{os.path.relpath(path, PDM)}:{line}",
            "text": text.strip(), "note": note}


def main():
    base = os.path.join(RWML, "scripts", "configs", "base_cfg.py")
    flat = os.path.join(RWML, "scripts", "configs", "anymal_d_flat_cfg.py")
    env = os.path.join(RWML, "scripts", "envs", "base.py")
    poltr = os.path.join(RWML, "scripts", "policy_training.py")
    mbpo = os.path.join(RSL, "rsl_rl", "algorithms", "mbpo_ppo.py")
    runner = os.path.join(RSL, "rsl_rl", "runners", "mbpo_on_policy_runner.py")

    out = {
        "question": "which horizon does the method actually run its world model over, "
                    "and what is h=368",
        "horizons": {},
        "our_grid": {},
        "followup_figure": {},
        "verdict": {},
    }

    H = out["horizons"]

    # ------------------------------------------------ the imagination rollout
    H["imagination_steps_per_iteration_published"] = {
        "value": 100,
        "evidence_class": "EXT",
        "source": "arXiv:2504.16680 Table S9 (v1) / Table S11 (v3), "
                  "'imagination steps per iteration'",
        "note": "identical in both versions; this is the horizon the "
                "uncertainty-penalised policy loop rolls the model over",
    }
    H["episodic_rollout_length_published"] = {
        "value": 100,
        "evidence_class": "EXT",
        "source": "arXiv:2504.16680v3 §1, 'propagate and manage uncertainty over "
                  "100-step episodic rollouts'",
        "note": "prose added in v3 and absent from v1; it states the same figure as "
                "the hyperparameter table, in the form a reader would quote",
    }
    H["imagination_episode_cap_lite_release"] = {
        "value": 256,
        "evidence_class": "SRC",
        "citations": [
            cite(base, 20, "max_episode_length: int = 256",
                 "the shipped default in the reduced `lite` release"),
            cite(env, 174, "time_outs = self.episode_length_buf >= self._max_episode_length",
                 "where the cap is enforced: an imagined episode is reset here"),
        ],
        "note": "the lite release's own cap on an imagined episode. It is NOT the "
                "published figure and it is not 368; the two releases differ and "
                "the published one governs what the method does.",
    }
    H["collection_segment_lite_release"] = {
        "value": 24,
        "evidence_class": "SRC",
        "citations": [
            cite(base, 147, "num_steps_per_env: int = 24",
                 "PPO collection segment per iteration"),
            cite(poltr, 48, "state_history, action_history = self.env.prepare_imagination()",
                 "called ONCE, before the iteration loop"),
            cite(poltr, 59, "for it in range(start_iter, tot_iter):",
                 "the iteration loop it sits outside"),
            cite(poltr, 64, "for i in range(self.num_steps_per_env):",
                 "24 steps per iteration, chained: the imagined trajectory persists "
                 "across iterations and is reset only by termination or the episode cap"),
        ],
        "note": "a segment length, not a rollout length. Recorded so the 24 is not "
                "mistaken for the horizon.",
    }
    H["command_resample_interval"] = {
        "value": [100, 120],
        "evidence_class": "SRC",
        "citations": [cite(flat, 31, "command_resample_interval_range",
                           "resamples the velocity command mid-rollout")],
        "note": "This resamples the COMMAND. It does not reset the rollout and is not "
                "a horizon. Recorded because its range brackets 100 and it is the "
                "obvious thing to mistake for the rollout length.",
    }
    H["runner_knob_not_shipped"] = {
        "value": None,
        "evidence_class": "SRC",
        "citations": [
            cite(runner, 438, 'self.num_imagination_steps = self.imagination_cfg["num_steps_per_env"]',
                 "the published 100 enters here"),
            cite(runner, 439, 'self.max_imagination_episode_length = self.imagination_cfg["max_episode_length"]',
                 "and the episode cap here"),
        ],
        "note": "the full-stack runner reads both from an imagination_cfg that the "
                "released repositories do not ship, so the published table is the "
                "only authority for the values actually used.",
    }

    # ------------------------------------------------- where 368 comes from
    H["open_loop_diagnostic"] = {
        "value": 368,
        "evidence_class": "SRC",
        "citations": [
            cite(base, 46, "len_eval_trajectory: int = 400",
                 "the evaluation trajectory length"),
            cite(mbpo, 61, "system_dynamics_len_eval_trajectory=400",
                 "the same 400 in the algorithm"),
            cite(mbpo, 284, "for i in range(self.system_dynamics.history_horizon, "
                            "self.system_dynamics_len_eval_trajectory)",
                 "the forecast starts AFTER the 32-step teacher-forced prefix, so the "
                 "autoregressive part is 400 - 32 = 368 steps"),
            cite(flat, 68, "history_horizon: int = 32", "the prefix length"),
        ],
        "arithmetic": {"len_eval_trajectory": 400, "history_horizon": 32,
                       "autoregressive_steps": 400 - 32},
        "note": "This is what h=368 is. It is an open-loop diagnostic that the "
                "upstream plots; it is not a horizon the method deploys at.",
    }

    assert H["open_loop_diagnostic"]["arithmetic"]["autoregressive_steps"] == 368

    # ------------------------------------------------------------ our grid
    deployed = H["imagination_steps_per_iteration_published"]["value"]
    old_grid = (1, 8, 32, 128, 368)
    new_grid = tuple(sorted(set(old_grid) | {deployed}))
    at_or_below = [h for h in old_grid if h <= deployed]
    out["our_grid"] = {
        "grid_before": list(old_grid),
        "grid_after": list(new_grid),
        "deployment_horizon": deployed,
        "nearest_measured_at_or_below_before": max(at_or_below) if at_or_below else None,
        "resolution": "h=100 is added to the evaluation grid rather than approximated. "
                      "The per-step curves already run to 368, so measuring the "
                      "method's own horizon exactly costs a cumulative mean and "
                      "removes the need for a 'nearest grid point' argument.",
        "metrics_default_grid": list(M.summarise.__defaults__[0]),
    }
    # the grid in src/rwm_metrics.py must actually carry the new horizon, or the
    # paper would re-anchor to a number nothing computes
    assert deployed in M.summarise.__defaults__[0], (
        f"h={deployed} is not in rwm_metrics.summarise's default grid "
        f"{M.summarise.__defaults__[0]}; add it before re-anchoring the paper")

    # ------------------------------------- what the follow-up's figure plots
    out["followup_figure"] = {
        "v1": {"figure": "Figure 2 (right)", "section": "5.1",
               "model_name": "RWM-O",
               "caption_fragment": "Predictions commence at t=32 using historical "
                                   "observations, with future observations predicted "
                                   "autoregressively by feeding prior predictions back "
                                   "into the model."},
        "v3": {"figure": "Figure 3 (right)", "section": "5.1",
               "model_name": "RWM-U",
               "caption_fragment": "The epistemic uncertainty estimate by RWM-U aligns "
                                   "with the long-horizon prediction error and thus sets "
                                   "a reliable metric in policy training."},
        "horizontal_axis": "time step t, predictions commencing at t=32",
        "plotted_horizon": "not stated numerically in either version; the axis is a "
                           "time index and no rollout length is given in the caption "
                           "or in §5.1",
        "note": "The figure is the open-loop diagnostic, matching the 368-step "
                "construction above -- not the 100-step imagination rollout. So the "
                "follow-up's uncertainty evidence is itself gathered at a horizon "
                "3.68x longer than the one its method deploys at. We report that as an "
                "observation about the original, not as a defect: a diagnostic may "
                "legitimately run past the deployment horizon. What it does mean is "
                "that OUR h=368 is comparable to the original's figure, while our "
                "h=100 is comparable to the original's method.",
        "evidence_class": "EXT",
    }
    out["followup_figure"]["ratio_diagnostic_over_deployed"] = round(368 / deployed, 2)

    # ----------------------------------------------------------- the verdict
    out["verdict"] = {
        "deployment_horizon_is": deployed,
        "h368_is": "the open-loop diagnostic horizon (len_eval_trajectory 400 minus "
                   "the 32-step teacher-forced prefix)",
        "h368_over_deployment": round(368 / deployed, 2),
        "label_change": 'h=368 is relabelled "the open-loop diagnostic horizon, beyond '
                        "the method's own rollout length\"; the headline re-anchors to "
                        "h=100",
        "tables": "every h=368 row is kept",
    }

    dst = os.path.join(R.RESULTS, "v2_deployment_horizon.json")
    with open(dst, "w") as f:
        json.dump(out, f, indent=2, sort_keys=True)
    print(f"deployment horizon (published):        {deployed} steps")
    print(f"imagination episode cap (lite):        "
          f"{H['imagination_episode_cap_lite_release']['value']} steps")
    print(f"open-loop diagnostic (where 368 is):   400 - 32 = 368 steps")
    print(f"368 / deployment:                      {368 / deployed:.2f}x")
    print(f"evaluation grid: {list(old_grid)} -> {list(new_grid)}")
    print(f"\nwrote {dst}")


if __name__ == "__main__":
    main()
