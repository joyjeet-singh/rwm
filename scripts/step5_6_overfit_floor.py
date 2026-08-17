"""
Step 5.6 -- was the overfit plateau the sampling floor, or a genuine failure to fit?

The 1e-4 acceptance threshold was unreachable in principle. The state loss is squared
error on a reparameterised sample, so

    E[ sum_d (mu_d + sigma_d*eps_d - y_d)^2 ] = sum_d (mu_d - y_d)^2 + sum_d sigma_d^2

The second term does not vanish. At iteration 2000 the collapse monitor still read
exp(log_delta) ~ 0.25, so sigma was nowhere near zero, and noise injected at each of the
eight forecast steps also propagates into the next step's input. The objective has a floor.

This test needs no retraining. Load the converged weights and evaluate the same batch twice:

    L_det    randn_like patched to zeros, so sample == mean
    L_stoch  real sampling, averaged over N draws

plus sum_d sigma_d^2 at the final weights as the analytic single-step lower bound.

    L_det << L_stoch ~ 0.028  ->  the plateau is the sampling floor; the model memorised
    L_det ~= 0.028            ->  the model genuinely did not fit the batch
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               os.pardir, "src"))

import numpy as np
import torch

import rwm_data as R
import rollout_eval as E
import rwm_model as M
import rwm_train as T

N_DRAWS = 100


class Zeros:
    """Patch torch.randn_like to return zeros, making the sample equal the mean."""

    def __enter__(self):
        self._orig = torch.randn_like
        torch.randn_like = lambda x, *a, **k: torch.zeros_like(x)
        return self

    def __exit__(self, *e):
        torch.randn_like = self._orig


def main():
    here = R.RESULTS
    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    data, episode_id = R.load_data(paths["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(here, "step0_strat.json"),
                         verbose=False)
    weights = cfg["loss_weights"]

    wpath = os.path.join(here, "overfit_weights_b32lr1e3.pt")
    assert os.path.exists(wpath), f"missing {R.rel(wpath)} -- rerun the overfit first"
    ck = torch.load(wpath, map_location="cpu")

    print("=" * 82)
    print("STEP 5.6 -- IS THE OVERFIT PLATEAU THE SAMPLING FLOOR?")
    print("=" * 82)
    print(f"  loaded {R.rel(wpath)}  ({ck['iterations']} iterations, "
          f"batch {ck['config']['batch']}, lr {ck['config']['lr']})")

    model = M.build_from_config(cfg, ensemble_size=ck["config"]["ensemble"])
    model.load_state_dict(ck["model_state_dict"], strict=True)
    model.eval()

    ds = T.WindowDataset(data, episode_id, split["train_episodes"], cfg)
    batch = ds.batch(ck["batch_idx"])
    state, action, ext, contact, term = batch
    print(f"  same batch as training: {state.shape[0]} windows")

    # ---- L_det -----------------------------------------------------------
    with torch.no_grad(), Zeros():
        model.reset()
        det = model.compute_loss(state, action, ext, contact, term)
    L_det = float(det[0])

    # ---- L_stoch ---------------------------------------------------------
    draws = []
    with torch.no_grad():
        for i in range(N_DRAWS):
            torch.manual_seed(10_000 + i)
            model.reset()
            draws.append(float(model.compute_loss(state, action, ext, contact, term)[0]))
    draws = np.array(draws)
    L_stoch = float(draws.mean())

    # ---- the analytic single-step floor ----------------------------------
    sig2 = model.sigma_sq_sum(state, action)
    cs = model.collapse_stats()

    reported = json.load(open(os.path.join(here, "step4_4_overfit_b32lr1e3.json")))
    L_train = reported["last"]["state"]

    print(f"\n  {'quantity':<44s} {'value':>14s}")
    print("  " + "-" * 60)
    print(f"  {'L_train  (final training iteration, 1 draw)':<44s} {L_train:>14.6f}")
    print(f"  {'L_stoch  (real sampling, mean of ' + str(N_DRAWS) + ' draws)':<44s} "
          f"{L_stoch:>14.6f}")
    print(f"  {'         (std over draws)':<44s} {draws.std():>14.6f}")
    print(f"  {'         (min / max over draws)':<44s} "
          f"{str(round(draws.min(),4)) + ' / ' + str(round(draws.max(),4)):>14s}")
    print(f"  {'L_det    (sample = mean)':<44s} {L_det:>14.6f}")
    print(f"  {'sum_d sigma_d^2 (single-step floor)':<44s} {sig2:>14.6f}")
    print(f"  {'exp(log_delta_logstd) at final weights':<44s} "
          f"{cs['exp_log_delta_logstd_mean']:>14.6f}")
    print(f"  {'exp(min_logstd) at final weights':<44s} "
          f"{cs['exp_min_logstd_mean']:>14.3e}")

    ratio = L_stoch / L_det if L_det > 0 else float("inf")
    print(f"\n  L_stoch / L_det = {ratio:.1f}x")
    print(f"  L_det as a fraction of L_stoch = {100*L_det/L_stoch:.2f}%")
    print(f"  sum_d sigma_d^2 accounts for {100*sig2/L_stoch:.1f}% of L_stoch"
          f" at the FIRST forecast step alone;")
    print(f"  the objective averages 8 steps and the injected noise also propagates into")
    print(f"  each next step's input, so the realised floor is larger than that.")

    verdict = "PASS" if ratio > 5.0 else "GENUINE MISFIT"
    print("\n" + "=" * 82)
    if verdict == "PASS":
        print("  VERDICT: the plateau is the SAMPLING FLOOR. The model DID memorise.")
        print(f"  With the sample forced to the mean the deterministic error is {L_det:.6f},")
        print(f"  {ratio:.0f}x below the stochastic loss the training curve reported. The")
        print("  residual is variance the objective injects on purpose, not error the model")
        print("  failed to remove.  OVERFIT TEST PASSES.")
    else:
        print("  VERDICT: L_det is comparable to L_stoch, so the plateau is NOT the sampling")
        print("  floor -- the model genuinely did not fit the batch. Residual optimisation")
        print("  difficulty. Report it; it does not block the runs.")
    print("=" * 82)

    out = {"L_det": L_det, "L_stoch": L_stoch, "L_stoch_std": float(draws.std()),
           "L_stoch_min": float(draws.min()), "L_stoch_max": float(draws.max()),
           "L_train_final": L_train, "sigma_sq_sum_first_step": sig2,
           "ratio_stoch_over_det": ratio, "n_draws": N_DRAWS,
           "collapse_at_final_weights": cs, "verdict": verdict}
    with open(os.path.join(here, "step5_6_overfit_floor.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(f"\n  wrote {R.rel(os.path.join(here, 'step5_6_overfit_floor.json'))}")
    return out


if __name__ == "__main__":
    main()
