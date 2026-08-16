"""
Task 5 -- differential test of the rebuilt forward pass against the reference module.

Matching parameter counts (Step 3) is weak evidence: it constrains shapes, not
wiring. This runs the authors' own SystemDynamicsEnsemble and the rebuilt one on
identical input and compares outputs.

The CUDA pin lives in setup.py, not in the modules, so the modules themselves may
import on CPU. Import is attempted in three escalating ways and whatever happens
is reported verbatim -- an honest failure here is more useful than a workaround,
because it tells us whether Step 4 can be verified this way at all.
"""

import importlib.util
import json
import os
import sys
import traceback

import numpy as np
import torch

import rwm_data as R
import rollout_eval as E
import score_reference as S


def try_import(rsl_repo):
    """Return (module, how, traceback_or_None)."""
    if rsl_repo not in sys.path:
        sys.path.insert(0, rsl_repo)

    # 1. the straightforward package import the brief asks for
    try:
        from rsl_rl.modules import SystemDynamicsEnsemble  # noqa
        return SystemDynamicsEnsemble, "from rsl_rl.modules import SystemDynamicsEnsemble", None
    except Exception:
        tb_pkg = traceback.format_exc()

    # 2. the submodule directly, bypassing rsl_rl/modules/__init__.py
    try:
        import rsl_rl.modules.system_dynamics as sdmod
        return sdmod.SystemDynamicsEnsemble, "import rsl_rl.modules.system_dynamics", tb_pkg
    except Exception:
        tb_sub = traceback.format_exc()

    # 3. load the file with importlib, same pattern rwm_data.py uses for configs
    try:
        arch_dir = os.path.join(rsl_repo, "rsl_rl", "modules", "architectures")
        spec_a = importlib.util.spec_from_file_location(
            "_arch", os.path.join(arch_dir, "__init__.py"),
            submodule_search_locations=[arch_dir])
        arch = importlib.util.module_from_spec(spec_a)
        sys.modules["_arch"] = arch
        sys.modules["rsl_rl.modules.architectures"] = arch
        spec_a.loader.exec_module(arch)

        path = os.path.join(rsl_repo, "rsl_rl", "modules", "system_dynamics.py")
        spec = importlib.util.spec_from_file_location("_sysdyn", path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["_sysdyn"] = mod
        spec.loader.exec_module(mod)
        return mod.SystemDynamicsEnsemble, "importlib direct file load", tb_pkg + "\n" + tb_sub
    except Exception:
        return None, None, tb_pkg + "\n" + tb_sub + "\n" + traceback.format_exc()


def reference_rollout(ref, state, action, start_step, len_traj):
    """model_training.py:124-133, driving the authors' module directly."""
    pred = state.clone()
    ref.reset()
    with torch.no_grad():
        for i in range(start_step, len_traj):
            if i > start_step:
                s_in, a_in = pred[:, i - 1:i], action[:, i - 1:i]
            else:
                s_in, a_in = pred[:, i - start_step:i], action[:, i - start_step:i]
            m, _, _, _, _, _ = ref.forward(s_in, a_in)
            pred[:, i] = m
    return pred


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])

    print("=" * 78)
    print("TASK 5 -- DIFFERENTIAL TEST AGAINST THE REFERENCE MODULE")
    print("=" * 78)

    cls, how, tb = try_import(paths["rsl"])
    out = {"import_succeeded": cls is not None, "import_method": how}
    if cls is None:
        print("\n  IMPORT FAILED. Verbatim traceback:\n")
        print(tb)
        out["traceback"] = tb
        with open(os.path.join(here, "task5_differential.json"), "w") as f:
            json.dump(out, f, indent=2)
        return out
    print(f"\n  import OK via: {how}")
    if tb:
        print("  (earlier attempts failed; last error from those was:")
        print("   " + tb.strip().splitlines()[-1] + ")")

    # ---------------------------------------------- READ AND REPORT: signature
    import inspect
    sig = inspect.signature(cls.__init__)
    print("\n  READ AND REPORT -- constructor signature (system_dynamics.py:6-17):")
    for name, p in sig.parameters.items():
        if name == "self":
            continue
        d = "required" if p.default is inspect.Parameter.empty else f"default={p.default!r}"
        ann = getattr(p.annotation, "__name__", p.annotation)
        ann = "" if ann is inspect.Parameter.empty else f": {ann}"
        print(f"    {name}{ann}   ({d})")
    out["constructor_signature"] = str(sig)

    kwargs = dict(
        state_dim=45, action_dim=12,
        extension_dim=0,
        contact_dim=cfg["contact_dim"],
        termination_dim=cfg["termination_dim"],
        device="cpu",
        ensemble_size=cfg["ensemble_size"],
        history_horizon=cfg["history_horizon"],
        architecture_config=cfg["architecture_config"],
    )
    print("\n  built from anymal_d_flat_cfg.py values (not hand-typed):")
    for k, v in kwargs.items():
        print(f"    {k:<22s} {v}")
    out["constructor_kwargs"] = {k: (v if not isinstance(v, dict) else dict(v))
                                 for k, v in kwargs.items()}

    ref = cls(**kwargs)
    sd = torch.load(paths["ckpt"], map_location="cpu")["system_dynamics_state_dict"]
    missing, unexpected = ref.load_state_dict(sd, strict=True), None
    print(f"\n  load_state_dict(strict=True) -> {missing}")
    ref.eval()
    mine = S.ReferenceRWM(sd)
    mine.eval()
    torch.manual_seed(0)

    n_ref = sum(p.numel() for p in ref.parameters())
    n_mine = sum(p.numel() for p in mine.parameters()) + \
        sum(b.numel() for b in mine.buffers())
    print(f"  reference module parameters: {n_ref:,}")
    print(f"  rebuilt module params+buffers: {n_mine:,}")

    # ------------------------------------------------------------- test data
    data, episode_id = R.load_data(paths["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(here, "step0_strat.json"),
                         verbose=False)
    idx = E.sample_trajectories(episode_id, split["holdout_episodes"], seed=0)
    raw = data[idx]
    state = torch.as_tensor(R.normalise_state(raw[:, :, R.STATE_COLS],
                                              cfg["state_data_mean"], cfg["state_data_std"]),
                            dtype=torch.float32)
    action = torch.as_tensor(raw[:, :, R.ACTION_COLS], dtype=torch.float32)

    # ------------------------------------------------- 1. single forward call
    print("\n" + "-" * 78)
    print("  1. single forward call on a (B, 32, 45) / (B, 32, 12) held-out batch")
    print("-" * 78)
    ref.reset()
    with torch.no_grad():
        m_ref, al_ref, ep_ref, _, c_ref, t_ref = ref.forward(state[:, :32], action[:, :32])
        m_mine, al_mine, ep_mine, aux, _, _ = mine.step(state[:, :32], action[:, :32],
                                                        None, None, want_aux=True)
    d_mean = float((m_ref - m_mine).abs().max())
    d_alea = float((al_ref - al_mine).abs().max())
    d_epis = float((ep_ref - ep_mine).abs().max())
    print(f"     predicted mean   max abs diff : {d_mean:.3e}")
    print(f"     aleatoric  (mean of stds)     : {d_alea:.3e}")
    print(f"     epistemic  (std of means)     : {d_epis:.3e}")
    print(f"     mean magnitude for scale      : {m_ref.abs().mean():.4f}")
    if c_ref is not None:
        print(f"     contact logits max abs diff   : "
              f"{float((c_ref - aux[0]).abs().max()):.3e}")
        print(f"     termination logits max diff   : "
              f"{float((t_ref - aux[1]).abs().max()):.3e}")

    # -------------------------------------------------- 2. full 368-step rollout
    print("\n" + "-" * 78)
    print("  2. full 368-step protocol A rollout")
    print("-" * 78)
    p_ref = reference_rollout(ref, state, action, E.START_STEP, state.shape[1])
    p_mine, *_ = mine.rollout(state.clone(), action, E.START_STEP)
    diff = (p_ref[:, E.START_STEP:] - p_mine[:, E.START_STEP:]).abs()
    d_roll = float(diff.max())
    per_step = diff.amax(dim=(0, 2))
    print(f"     max abs diff over {diff.numel()} values"
          f" ({diff.shape[0]} traj x {diff.shape[1]} steps x {diff.shape[2]} dims):"
          f" {d_roll:.3e}")
    print(f"     worst step: {int(per_step.argmax()) + 1}"
          f"   diff at final step: {float(per_step[-1]):.3e}")
    print(f"     steps with diff > 1e-5: {int((per_step > 1e-5).sum())} of {len(per_step)}")

    e_ref, _ = E.relative_error(p_ref, state)
    e_mine, _ = E.relative_error(p_mine, state)
    print(f"     e from reference module : {e_ref:.6f}")
    print(f"     e from rebuilt module   : {e_mine:.6f}")
    print(f"     difference in e         : {abs(e_ref - e_mine):.3e}")

    ok = d_mean < 1e-5 and d_roll < 1e-5
    print("\n" + "=" * 78)
    print(f"  threshold 1e-5 (float32)")
    print(f"  single forward : {d_mean:.3e}   {'PASS' if d_mean < 1e-5 else 'FAIL'}")
    print(f"  full rollout   : {d_roll:.3e}   {'PASS' if d_roll < 1e-5 else 'FAIL'}")
    print(f"  -> {'PASS' if ok else 'FAIL'}: the rebuilt forward pass is"
          f" {'confirmed against' if ok else 'NOT equivalent to'} the reference module.")

    out.update({"max_abs_diff_single_forward_mean": d_mean,
                "max_abs_diff_single_forward_aleatoric": d_alea,
                "max_abs_diff_single_forward_epistemic": d_epis,
                "max_abs_diff_full_rollout": d_roll,
                "e_reference_module": e_ref, "e_rebuilt_module": e_mine,
                "threshold": 1e-5, "pass": bool(ok)})
    with open(os.path.join(here, "task5_differential.json"), "w") as f:
        json.dump(out, f, indent=2)
    return out


if __name__ == "__main__":
    main()
