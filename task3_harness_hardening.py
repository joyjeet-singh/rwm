"""
Task 3 -- harden the harness against alignment errors.

Acceptance test 1 (oracle -> e = 0) is weaker than it looks: the oracle returns
true_states[:, start_step:] and the metric compares against the same tensor with
the same indices, so it passes under ANY consistent off-by-one. It verifies
arithmetic, not alignment. These three checks pin the alignment itself.

  3a  the future-action tensor the harness hands the model really is the CSV
      action at row start+32 (exact equality; actions are unnormalised)
  3b  a lag-1 oracle must tie the hold-last predictor at forecast step 1, since
      both predict s[31] for s[32]
  3c  zeroing the delta head turns the model INTO the hold-last predictor,
      because the mean head is residual (mlp.py:88). This is the strongest
      available check that the residual is wired correctly.
"""

import copy
import json
import os

import numpy as np
import torch

import rwm_data as R
import rollout_eval as E
import score_reference as S


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    data, episode_id = R.load_data(paths["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(here, "step0_strat.json"),
                         verbose=False)
    base_cfg = E.build_base_config(cfg, seed=0)
    ecfg = {**base_cfg, "episode_id": episode_id, "noise_scales": []}

    print("=" * 78)
    print("TASK 3 -- HARNESS HARDENING")
    print("=" * 78)
    results = {}

    idx = E.sample_trajectories(episode_id, split["holdout_episodes"],
                                seed=base_cfg["seed"])
    start_rows = idx[:, 0]

    # ---------------------------------------------------------------- 3a
    print("\n  [3a] the future-action tensor is indexed correctly")
    captured = {}

    def debug_predictor(hs, ha, fa):
        captured["fa"] = fa.clone()
        captured["ha"] = ha.clone()
        return hs[:, -1:].expand(-1, fa.shape[1], -1).clone()

    E.evaluate(debug_predictor, data, split, ecfg)
    fa, ha = captured["fa"], captured["ha"]
    # The harness casts the float64 CSV to float32, so the exact-equality check
    # is against the float32 image of the CSV value, not the float64 original.
    # Comparing against float64 would only be measuring that cast (~5e-8).
    def csv_f32(rows, offset):
        return np.stack([data[r + offset][R.ACTION_COLS] for r in rows]).astype(np.float32)

    exp_fa0, exp_ha0, exp_fal = csv_f32(start_rows, E.START_STEP), \
        csv_f32(start_rows, 0), csv_f32(start_rows, 399)
    got_fa0, got_ha0, got_fal = fa[:, 0].numpy(), ha[:, 0].numpy(), fa[:, -1].numpy()
    exact_fa = bool(np.array_equal(got_fa0, exp_fa0))
    exact_ha = bool(np.array_equal(got_ha0, exp_ha0))
    exact_fal = bool(np.array_equal(got_fal, exp_fal))
    d_fa = float(np.abs(got_fa0 - exp_fa0).max())
    d_ha = float(np.abs(got_ha0 - exp_ha0).max())
    d_fal = float(np.abs(got_fal - exp_fal).max())
    d_fa64 = float(np.abs(got_fa0.astype(np.float64) -
                          np.stack([data[r + E.START_STEP][R.ACTION_COLS]
                                    for r in start_rows])).max())

    print(f"       fa shape {tuple(fa.shape)}, ha shape {tuple(ha.shape)}")
    print(f"       fa[b,0]  vs float32(CSV row start+32) : diff {d_fa:.1e}"
          f"  bitwise equal={exact_fa}")
    print(f"       ha[b,0]  vs float32(CSV row start+0)  : diff {d_ha:.1e}"
          f"  bitwise equal={exact_ha}")
    print(f"       fa[b,-1] vs float32(CSV row start+399): diff {d_fal:.1e}"
          f"  bitwise equal={exact_fal}")
    print(f"       (against the float64 CSV the residual is {d_fa64:.1e}, which is")
    print(f"        exactly the float64->float32 cast the harness performs, not a")
    print(f"        misalignment: a one-row error would be O(0.1) here)")
    ok3a = exact_fa and exact_ha and exact_fal
    print(f"       -> {'PASS' if ok3a else 'FAIL'}")
    results["3a_index_assertion"] = {"bitwise_equal_fa0": exact_fa,
                                     "bitwise_equal_ha0": exact_ha,
                                     "bitwise_equal_fa_last": exact_fal,
                                     "residual_vs_float64_csv": d_fa64, "pass": ok3a}
    assert ok3a, "3a failed: the harness is not handing the model the actions it claims"

    # ---------------------------------------------------------------- 3b
    print("\n  [3b] lag-1 oracle ties hold-last at forecast step 1")
    raw = data[idx]
    true_states = torch.as_tensor(
        R.normalise_state(raw[:, :, R.STATE_COLS], cfg["state_data_mean"],
                          cfg["state_data_std"]), dtype=torch.float32)

    def lag1_oracle(hs, ha, fa):
        return true_states[:, E.START_STEP - 1:-1].clone()

    r_lag = E.evaluate(lag1_oracle, data, split, ecfg)
    r_hold = E.evaluate(E.hold_last_predictor(), data, split, ecfg)
    c_lag = r_lag["clean"]["per_step_mean"]
    c_hold = r_hold["clean"]["per_step_mean"]
    d1 = float(abs(c_lag[0] - c_hold[0]))
    ok3b = c_lag[0] == c_hold[0]
    print(f"       lag-1 oracle r_t at step 1 : {c_lag[0]:.17g}")
    print(f"       hold-last    r_t at step 1 : {c_hold[0]:.17g}")
    print(f"       difference                 : {d1:.3e}  (required exactly 0)")
    print(f"       (they diverge later, as they must: lag-1 keeps tracking the truth,")
    print(f"        hold-last freezes -- e {r_lag['clean']['e']:.4f} vs "
          f"{r_hold['clean']['e']:.4f})")
    print(f"       -> {'PASS' if ok3b else 'FAIL'}")
    results["3b_lag1_oracle"] = {"lag1_step1": float(c_lag[0]),
                                 "holdlast_step1": float(c_hold[0]),
                                 "difference": d1, "pass": bool(ok3b),
                                 "lag1_e": r_lag["clean"]["e"],
                                 "holdlast_e": r_hold["clean"]["e"]}
    assert ok3b, "3b failed: indexing is inconsistent between predictors"

    # ---------------------------------------------------------------- 3c
    print("\n  [3c] zero-delta model IS the hold-last predictor (residual check)")
    sd = torch.load(paths["ckpt"], map_location="cpu")["system_dynamics_state_dict"]
    model = S.ReferenceRWM(sd)
    zero = copy.deepcopy(model)
    with torch.no_grad():
        for head in zero.state_mean_layers:
            head[2].weight.zero_()
            head[2].bias.zero_()
    print(f"       zeroed the final Linear of all {len(zero.state_mean_layers)}"
          f" state_mean_layers heads")

    pred_zero, *_ = zero.rollout(true_states.clone(),
                                 torch.as_tensor(raw[:, :, R.ACTION_COLS],
                                                 dtype=torch.float32),
                                 E.START_STEP)
    hold = true_states[:, E.START_STEP - 1:E.START_STEP].expand(
        -1, true_states.shape[1] - E.START_STEP, -1)
    diff = (pred_zero[:, E.START_STEP:] - hold).abs()
    maxd = float(diff.max())
    per_step_max = diff.amax(dim=(0, 2))
    ok3c = maxd < 1e-6
    print(f"       max abs diff over all {diff.numel()} values"
          f" ({diff.shape[0]} traj x {diff.shape[1]} steps x {diff.shape[2]} dims):"
          f" {maxd:.3e}")
    print(f"       worst single step: {int(per_step_max.argmax())+1}"
          f" (max {float(per_step_max.max()):.3e})")
    print(f"       steps with any diff > 1e-6: "
          f"{int((per_step_max > 1e-6).sum())} of {len(per_step_max)}")
    print(f"       -> {'PASS' if ok3c else 'FAIL'}  (tolerance 1e-6, float32)")
    results["3c_zero_delta"] = {"max_abs_diff": maxd, "tolerance": 1e-6,
                                "n_steps_over_tol": int((per_step_max > 1e-6).sum()),
                                "pass": bool(ok3c)}
    assert ok3c, ("3c failed: the residual connection is not wired correctly and the "
                  "Step 3 numbers need rerunning")

    allp = all(v["pass"] for v in results.values())
    print("\n" + "-" * 78)
    for k, v in results.items():
        print(f"  {'PASS' if v['pass'] else 'FAIL'}  {k}")
    print(f"\n  ALL THREE {'PASS' if allp else 'FAIL'}")
    print("  The rebuilt forward pass and the harness indexing are both confirmed;")
    print("  the Step 3 numbers stand.")
    with open(os.path.join(here, "task3_hardening.json"), "w") as f:
        json.dump(results, f, indent=2)
    return results


if __name__ == "__main__":
    main()
