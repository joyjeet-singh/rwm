"""
Step 4 / 3 -- the acceptance gate: differential test on losses AND gradients.

Parameter counts constrain shapes. Matching outputs constrains wiring (done in
R-11). Matching gradients constrains the OBJECTIVE. Step 5 onward is only
trustworthy if this passes.

Determinism: the reparameterised sample makes the loss stochastic, so
torch.randn_like is monkeypatched globally -- both implementations call it, so
one patch covers both. Two runs:
  zeros  -- sample == mean, isolating everything except the sigma path
  fixed  -- a seeded tensor, exercising the sigma path

Thresholds: 1e-6 relative on losses, 1e-5 relative on gradients. A gradient
mismatch beyond that means the trainer optimises something other than what the
reference optimises, and we stop.
"""

import json
import os
import sys

import numpy as np
import torch

import rwm_data as R
import rollout_eval as E
import rwm_model as M

WEIGHT_KEYS = M.TOTAL_WEIGHT_KEYS
BATCH = 16
LOSS_TOL = 1e-6
GRAD_TOL = 1e-5


def import_reference(rsl_repo):
    """Clean package import; gitpython + tensordict installed to make it work (3d)."""
    if rsl_repo not in sys.path:
        sys.path.insert(0, rsl_repo)
    from rsl_rl.modules import SystemDynamicsEnsemble
    return SystemDynamicsEnsemble


class DeterministicRandn:
    """Monkeypatch torch.randn_like. Same values for both implementations."""

    def __init__(self, mode, seed=1234):
        self.mode, self.seed, self.calls = mode, seed, 0
        self._orig = torch.randn_like

    def __enter__(self):
        def patched(x, *a, **k):
            self.calls += 1
            if self.mode == "zeros":
                return torch.zeros_like(x)
            g = torch.Generator().manual_seed(self.seed + self.calls)
            return torch.randn(x.shape, generator=g, dtype=x.dtype)
        torch.randn_like = patched
        return self

    def __exit__(self, *exc):
        torch.randn_like = self._orig

    def rewind(self):
        self.calls = 0


def rel(a, b):
    d = abs(a - b)
    s = max(abs(a), abs(b))
    return d / s if s > 0 else d


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    data, episode_id = R.load_data(paths["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(here, "step0_strat.json"),
                         verbose=False)

    print("=" * 82)
    print("STEP 4 / 3 -- DIFFERENTIAL TEST ON LOSSES AND GRADIENTS")
    print("=" * 82)

    cls = import_reference(paths["rsl"])
    print(f"  reference imported cleanly: {cls.__module__}")
    print("  (3d: installed gitpython + tensordict, both pure-Python; no stubs needed)")

    kwargs = dict(state_dim=45, action_dim=12, extension_dim=0,
                  contact_dim=cfg["contact_dim"], termination_dim=cfg["termination_dim"],
                  device="cpu", ensemble_size=cfg["ensemble_size"],
                  history_horizon=cfg["history_horizon"],
                  architecture_config=cfg["architecture_config"])
    ref = cls(**kwargs)
    mine = M.build_from_config(cfg)
    sd = torch.load(paths["ckpt"], map_location="cpu")["system_dynamics_state_dict"]
    print(f"  reference load_state_dict(strict=True): {ref.load_state_dict(sd, strict=True)}")
    print(f"  ours      load_state_dict(strict=True): {mine.load_state_dict(sd, strict=True)}")
    ref.train(); mine.train()

    ref_names = {n for n, _ in ref.named_parameters()}
    my_names = {n for n, _ in mine.named_parameters()}
    print(f"  parameter-name sets identical: {ref_names == my_names}"
          f"  ({len(my_names)} tensors)")
    assert ref_names == my_names, f"name mismatch: {ref_names ^ my_names}"

    # ------------------------------------------------- one fixed held-out batch
    starts = R.valid_window_starts(episode_id, 40)
    starts = np.array([s for s in starts if episode_id[s] in split["holdout_episodes"]])
    rng = np.random.default_rng(0)
    idx = rng.choice(starts, size=BATCH, replace=False)[:, None] + np.arange(40)[None, :]
    raw = data[idx]
    state = torch.as_tensor(R.normalise_state(raw[:, :, R.STATE_COLS],
                                              cfg["state_data_mean"], cfg["state_data_std"]),
                            dtype=torch.float32)
    action = torch.as_tensor(raw[:, :, R.ACTION_COLS], dtype=torch.float32)
    contact = torch.as_tensor(raw[:, :, R.CONTACTS], dtype=torch.float32)
    term = torch.as_tensor(raw[:, :, [R.TERMINATION]], dtype=torch.float32)
    ext = torch.zeros(BATCH, 40, 0)
    print(f"  batch: {BATCH} windows from held-out episodes "
          f"{sorted(set(episode_id[idx[:,0]].tolist()))}, shapes "
          f"state {tuple(state.shape)} action {tuple(action.shape)}")

    weights = cfg["loss_weights"]
    print(f"  loss weights (imported from base_cfg.py): {weights}")

    results = {"loss": {}, "grad": {}}
    all_ok = True

    for mode in ("zeros", "fixed"):
        print("\n" + "-" * 82)
        print(f"  SAMPLING MODE: {mode}"
              + ("   (sample == mean; isolates everything except the sigma path)"
                 if mode == "zeros" else "   (seeded tensor; sigma path exercised)"))
        print("-" * 82)

        # ---- losses -------------------------------------------------------
        with DeterministicRandn(mode) as d:
            ref.reset()
            ref_terms = ref.compute_loss(state, action, None, contact, term)
            d.rewind()
            mine.reset()
            my_terms = mine.compute_loss(state, action, ext, contact, term)

        print(f"\n  {'term':<14s} {'reference':>16s} {'ours':>16s} "
              f"{'abs diff':>12s} {'rel diff':>12s}")
        row = {}
        for k, a, b in zip(WEIGHT_KEYS, ref_terms, my_terms):
            av, bv = float(a), float(b)
            r = rel(av, bv)
            row[k] = {"reference": av, "ours": bv, "abs": abs(av - bv), "rel": r}
            flag = "" if r <= LOSS_TOL else "   <-- MISMATCH"
            print(f"  {k:<14s} {av:>16.8f} {bv:>16.8f} {abs(av-bv):>12.3e} {r:>12.3e}{flag}")
        ref_tot = float(M.weighted_total(ref_terms, weights))
        my_tot = float(M.weighted_total(my_terms, weights))
        rt = rel(ref_tot, my_tot)
        row["TOTAL(weighted)"] = {"reference": ref_tot, "ours": my_tot,
                                  "abs": abs(ref_tot - my_tot), "rel": rt}
        print(f"  {'TOTAL':<14s} {ref_tot:>16.8f} {my_tot:>16.8f} "
              f"{abs(ref_tot-my_tot):>12.3e} {rt:>12.3e}")
        loss_ok = all(v["rel"] <= LOSS_TOL for v in row.values())
        print(f"  losses within {LOSS_TOL:g} relative: {'PASS' if loss_ok else 'FAIL'}")
        results["loss"][mode] = row
        all_ok &= loss_ok

        # ---- gradients ----------------------------------------------------
        ref.zero_grad(set_to_none=True)
        mine.zero_grad(set_to_none=True)
        with DeterministicRandn(mode) as d:
            ref.reset()
            M.weighted_total(ref.compute_loss(state, action, None, contact, term),
                             weights).backward()
            d.rewind()
            mine.reset()
            M.weighted_total(mine.compute_loss(state, action, ext, contact, term),
                             weights).backward()

        rg = dict(ref.named_parameters())
        mg = dict(mine.named_parameters())
        worst_abs = (0.0, None)
        worst_rel = (0.0, None)
        n_none = 0
        per_param = {}
        for n in sorted(my_names):
            a, b = rg[n].grad, mg[n].grad
            if a is None or b is None:
                n_none += 1
                per_param[n] = {"ref_none": a is None, "our_none": b is None}
                continue
            da = float((a - b).abs().max())
            scale = float(torch.maximum(a.abs(), b.abs()).max())
            dr = da / scale if scale > 0 else da
            per_param[n] = {"max_abs": da, "max_rel": dr, "grad_scale": scale}
            if da > worst_abs[0]:
                worst_abs = (da, n)
            if dr > worst_rel[0]:
                worst_rel = (dr, n)
        # Guard against a vacuous pass: if both implementations produced zero
        # gradients everywhere, every difference would be 0 and the gate would
        # pass without testing anything.
        scales = [v["grad_scale"] for v in per_param.values() if "grad_scale" in v]
        n_nonzero = sum(1 for s in scales if s > 0)
        zero_ref = {n for n in my_names if rg[n].grad is not None
                    and float(rg[n].grad.abs().max()) == 0.0}
        zero_mine = {n for n in my_names if mg[n].grad is not None
                     and float(mg[n].grad.abs().max()) == 0.0}
        print(f"\n  gradients compared over {len(my_names) - n_none} tensors"
              f"{f' ({n_none} with a None grad)' if n_none else ''}")
        print(f"    NON-VACUITY CHECK: {n_nonzero}/{len(scales)} tensors have a"
              f" non-zero gradient")
        print(f"      gradient magnitude: max {max(scales):.4e}"
              f"  median {float(np.median(scales)):.4e}")
        print(f"      identically-zero in reference {len(zero_ref)},"
              f" in ours {len(zero_mine)}, sets identical: {zero_ref == zero_mine}")
        if zero_ref:
            groups = sorted({n.split(".")[2] if n.startswith(("state_heads",
                                                              "auxiliary_heads"))
                             else n.split(".")[0] for n in zero_ref})
            print(f"      the zero set is exactly: {groups}")
        assert zero_ref == zero_mine, (
            "the two implementations disagree about which parameters receive "
            "gradient -- that is a structural mismatch even if the values match")
        assert n_nonzero >= 0.5 * len(scales), (
            "over half the gradients are zero -- the comparison would be near-vacuous")
        print(f"    worst max-abs  {worst_abs[0]:.3e}"
              f"{'  (all differences exactly 0)' if worst_abs[1] is None else '  at ' + str(worst_abs[1])}")
        print(f"    worst max-rel  {worst_rel[0]:.3e}"
              f"{'  (all differences exactly 0)' if worst_rel[1] is None else '  at ' + str(worst_rel[1])}")
        results.setdefault("grad_magnitude", {})[mode] = {
            "n_nonzero": n_nonzero, "n_total": len(scales),
            "max": max(scales), "median": float(np.median(scales)), "min": min(scales)}
        grad_ok = worst_rel[0] <= GRAD_TOL
        print(f"    gradients within {GRAD_TOL:g} relative: "
              f"{'PASS' if grad_ok else 'FAIL'}")
        top = sorted(((v.get("max_rel", 0), n) for n, v in per_param.items()),
                     reverse=True)[:5]
        print(f"    five largest relative differences:")
        for v, n in top:
            print(f"      {v:.3e}  {n}")
        results["grad"][mode] = {"worst_max_abs": worst_abs[0],
                                 "worst_max_abs_param": worst_abs[1],
                                 "worst_max_rel": worst_rel[0],
                                 "worst_max_rel_param": worst_rel[1],
                                 "n_params": len(my_names), "n_none": n_none,
                                 "pass": bool(grad_ok)}
        all_ok &= grad_ok
        if not grad_ok:
            print("\n  STOPPING per the brief: a gradient mismatch means the trainer")
            print("  optimises something other than the reference. Nothing downstream")
            print("  would be interpretable.")
            break

    print("\n" + "=" * 82)
    print(f"  ACCEPTANCE GATE: {'PASS' if all_ok else 'FAIL'}")
    print("=" * 82)
    results["pass"] = bool(all_ok)
    results["loss_tol"], results["grad_tol"] = LOSS_TOL, GRAD_TOL
    with open(os.path.join(here, "step4_3_differential.json"), "w") as f:
        json.dump(results, f, indent=2)
    return results


if __name__ == "__main__":
    main()
