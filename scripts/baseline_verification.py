"""
The verification ladder for the architecture baselines (PLAN S2b step 5; rules M-75, M-76).
Run BEFORE any baseline is trained for real. Every rung must pass, for every baseline, or no
baseline run is queued.

  1  parameter count. RWM's ensemble-1 state pathway is recounted with the same function
     results/p2_capacity_power.json uses; the parameter-matched variants must land within
     +-5% of it. The Table S7 sizes are the original's and are recorded, not matched.
  2  zero delta is hold-last. With the state head's final mean layer zeroed, the residual
     head returns its last input state, so a whole rollout must equal the hold-last
     prediction to <= 1e-6 -- the baselines' version of the harness check that pins RWM's
     residual (scripts/task3_harness_hardening.py, 3c).
  3  memorisation. On one fixed batch of 32 windows, Adam at 1e-3 (the precedent of
     results/step4_4_overfit_b32lr1e3.json), the state loss must fall at least 100x within
     the iteration budget. Every regime of every Table S7 baseline; the tf regime of every
     parameter-matched variant.
  4  determinism. Two fresh builds with seed 0 give bitwise-identical first 10 losses.
  5  action alignment, shared with the RWM harness: with every action row set to its own row
     index, the newest action a baseline consumes when predicting state row r must be row r
     -- in training (both regimes) and in rollout. This is the causal pairing
     (D-13, X-05) and the baselines' version of the harness's 3a/3b checks.

Writes results/baseline_verification.json.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import torch  # noqa: E402

import baselines as BL  # noqa: E402
import train_baseline as TB  # noqa: E402
import rwm_data as R  # noqa: E402
import rwm_metrics as MET  # noqa: E402
import rollout_eval as E  # noqa: E402

MEM_BATCH, MEM_LR, MEM_ITERS, MEM_FACTOR = 32, 1e-3, 3000, 100.0
DET_ITERS = 10
ARCHS = ("mlp", "transformer", "rssm")


def zero_delta_is_hold_last(model, data, cfg, episode_id, split):
    starts = MET.non_overlapping_starts(episode_id, split["holdout_episodes"], 400)
    idx = np.asarray(starts)[:, None] + np.arange(400)[None, :]
    raw = data[idx]
    st = torch.as_tensor(R.normalise_state(raw[:, :, R.STATE_COLS], cfg["state_data_mean"],
                                           cfg["state_data_std"]), dtype=torch.float32)
    ac = torch.as_tensor(raw[:, :, R.ACTION_COLS], dtype=torch.float32)
    last = model.head.state_mean_layers[-1]
    with torch.no_grad():
        last.weight.zero_()
        last.bias.zero_()
    model.eval()
    pred = model.rollout(st.clone(), ac, BL.HISTORY, action_offset=1)
    hold = st[:, BL.HISTORY - 1:BL.HISTORY].expand(-1, 400 - BL.HISTORY, -1)
    return float((pred[:, BL.HISTORY:] - hold).abs().max())


def memorise(arch, spec, regime, cfg, ds):
    torch.manual_seed(0)
    model = BL.build(arch, spec, cfg)
    opt = torch.optim.Adam(model.parameters(), lr=MEM_LR, weight_decay=cfg["weight_decay"])
    batch = ds.sample(MEM_BATCH, torch.Generator().manual_seed(0))
    w = TB.loss_weights(model, cfg)
    first, t0 = None, time.perf_counter()
    for it in range(MEM_ITERS):
        model.train()
        opt.zero_grad(set_to_none=True)
        s, b, k = model.compute_state_loss(batch[0], batch[1], regime)
        (w["state"] * s + w["bound"] * b + w["kl"] * k).backward()
        opt.step()
        v = float(s)
        if not np.isfinite(v):
            return {"reached": False, "diverged_at": it, "first": first}
        first = v if first is None else first
        if first / max(v, 1e-12) >= MEM_FACTOR:
            return {"reached": True, "iterations": it + 1, "first": first, "last": v,
                    "factor": first / v, "seconds": time.perf_counter() - t0}
    return {"reached": False, "iterations": MEM_ITERS, "first": first, "last": v,
            "factor": first / v, "seconds": time.perf_counter() - t0}


def determinism(arch, spec, regime):
    runs = []
    for _ in range(2):
        cfg, data, ep, split, ds, model, opt, gen, _ = TB.build_everything(arch, spec, 0)
        h = TB.train_iterations(model, opt, ds, gen, 256, DET_ITERS, regime,
                                TB.loss_weights(model, cfg))
        runs.append(h["total"])
    return {"identical": runs[0] == runs[1], "first_losses": runs[0]}


def alignment(arch, spec, cfg):
    """The newest action consumed for state row r must be action row r."""
    torch.manual_seed(0)
    model = BL.build(arch, spec, cfg)
    B, Tw = 2, 40
    st = torch.randn(B, Tw, 45)
    ac = torch.arange(Tw, dtype=torch.float32)[None, :, None].expand(B, Tw, 12).clone()
    seen = []
    if arch == "rssm":
        orig = model._transition
        model._transition = lambda hs, z, a: (seen.append(float(a[0, 0])), orig(hs, z, a))[1]
        expect = {"tf": list(range(Tw)), "ar": list(range(Tw))}
        roll_expect = list(range(400))
    else:
        orig = model.encode
        model.encode = lambda xs, xa: (seen.append(float(xa[0, -1, 0])), orig(xs, xa))[1]
        expect = {r: list(range(BL.HISTORY, Tw)) for r in ("tf", "ar")}
        roll_expect = list(range(BL.HISTORY, 400))
    out = {}
    for regime in ("tf", "ar"):
        seen.clear()
        with torch.no_grad():
            model.compute_state_loss(st, ac, regime)
        out[regime] = seen == [float(x) for x in expect[regime]]
    seen.clear()
    st2 = torch.randn(B, 400, 45)
    ac2 = torch.arange(400, dtype=torch.float32)[None, :, None].expand(B, 400, 12).clone()
    model.rollout(st2, ac2, BL.HISTORY, action_offset=1)
    out["rollout"] = seen == [float(x) for x in roll_expect]
    return out


def main():
    # One thread: the M-74 sweep queue owns the two cores (PLAN §1.5), and this halves
    # the contention. Determinism is compared within this process, at this setting.
    torch.set_num_threads(1)
    import p2_capacity_power as P2
    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    data, episode_id = R.load_data(paths["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"),
                         verbose=False)
    ds = __import__("rwm_train").WindowDataset(data, episode_id, split["train_episodes"], cfg)
    rwm_sp = P2.state_pathway_params(cfg, 256, 1)
    assert rwm_sp == BL.RWM_STATE_PATHWAY, f"RWM state pathway {rwm_sp} != {BL.RWM_STATE_PATHWAY}"

    t_all = time.perf_counter()
    res, ok = {}, True
    print("=" * 96)
    print("BASELINE VERIFICATION LADDER (PLAN S2b step 5)")
    print("=" * 96)
    print(f"  RWM ensemble-1 state pathway: {rwm_sp:,} parameters")
    for spec in ("s7", "matched"):
        for arch in ARCHS:
            key = f"{arch}_{spec}"
            torch.manual_seed(0)
            model = BL.build(arch, spec, cfg)
            n = BL.n_params(model)
            r = {"n_params": n, "ratio_to_rwm": n / rwm_sp}
            if spec == "matched":
                r["within_5pct"] = abs(n / rwm_sp - 1) <= 0.05
                ok &= r["within_5pct"]
            r["zero_delta_max_abs"] = zero_delta_is_hold_last(model, data, cfg, episode_id, split)
            r["zero_delta_ok"] = r["zero_delta_max_abs"] <= 1e-6
            regimes = ("tf", "ar") if spec == "s7" else ("tf",)
            r["memorise"] = {g: memorise(arch, spec, g, cfg, ds) for g in regimes}
            r["determinism"] = {g: determinism(arch, spec, g) for g in regimes}
            r["alignment"] = alignment(arch, spec, cfg)
            passed = (r["zero_delta_ok"] and all(m["reached"] for m in r["memorise"].values())
                      and all(d["identical"] for d in r["determinism"].values())
                      and all(r["alignment"].values())
                      and (spec == "s7" or r["within_5pct"]))
            r["passed"] = bool(passed)
            ok &= passed
            res[key] = r
            mem = "; ".join(f"{g} {m['first']:.2f}->{m.get('last', float('nan')):.4f} "
                            f"({m.get('factor', 0):.0f}x in {m.get('iterations')} it)"
                            for g, m in r["memorise"].items())
            print(f"  {key:<18} {n:>9,} params ({n / rwm_sp:.3f}x)  zero-delta "
                  f"{r['zero_delta_max_abs']:.1e}  memorise {mem}  determinism "
                  f"{all(d['identical'] for d in r['determinism'].values())}  alignment "
                  f"{r['alignment']}  -> {'PASS' if passed else 'FAIL'}", flush=True)
    out = {"purpose": "PLAN S2b step 5: the verification ladder, every baseline, before any run",
           "rwm_state_pathway_params": rwm_sp, "memorise": {"batch": MEM_BATCH, "lr": MEM_LR,
                                                           "max_iterations": MEM_ITERS,
                                                           "required_factor": MEM_FACTOR},
           "determinism_iterations": DET_ITERS, "baselines": res, "all_passed": bool(ok),
           "wall_seconds": time.perf_counter() - t_all,
           "note": "run while the M-74 sweep queue was training; the wall-clock of the sweep "
                   "run it overlapped is inflated accordingly"}
    json.dump(out, open(os.path.join(R.RESULTS, "baseline_verification.json"), "w"), indent=2)
    print(f"  ALL PASSED: {ok}   ({(time.perf_counter() - t_all) / 60:.1f} min)")
    print("  wrote results/baseline_verification.json")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
