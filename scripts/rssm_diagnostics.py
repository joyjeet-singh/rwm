"""
Rule X1 (FINDINGS_LEDGER.md) -- the RSSM diagnostic: is our RSSM's long-horizon failure a
matter of how we read its forecast, of its training settings, or of neither setting we can test
from its source papers?

Committed and pushed, with the rule, before any reading exists (PLAN round 2, T2 step 1).
Exploratory: it never re-opens M-75 or M-76, whose rows and verdicts are unchanged.

ARENA (section 5.2's): the held-out pair, the 4 non-overlapping 400-step trajectories
(mn_sweep_eval.arena; starts 999, 1399, 7999, 8399), 32 history rows then 368 forecast rows,
relative-L1 per trajectory (mn_sweep_eval.metrics, the sweep and baseline evaluators' own), at
horizons {1, 8, 32, 100, 368}. The hold-last floor is the baseline evaluator's per-trajectory
floor (results/baselines_eval.json "floor"), whose means are the floor in
results/baselines_verdict.json (asserted).

PART A -- the read-out, existing weights: the six Table S7 RSSM runs at 2,500 iterations
(rssm_tf_s7 and rssm_ar_s7, seeds 0-2). The history is filtered as the rollout filters it (the
posterior's mode). In the forecast steps, three read-outs of the prior's categorical latent:
  mode      as run (BASELINE_SPECS row 31): the one-hot argmax; the decoded mean is fed back.
  expected  the class probabilities fed in place of the one-hot; the decoded mean fed back.
  sampled   16 rollouts per window, each drawing its latent from the prior at every forecast
            step (torch.multinomial with a torch.Generator seeded 0 for each model) and feeding
            back its own decoded mean; the read-out is the mean decoded state over the 16.
  ASSERTED: the mode read-out reproduces results/baselines_eval.json to 1e-6, and equals the
  model's own rollout() bitwise.
  READING, teacher-forced RSSM, 3-seed mean (per trajectory, the mean over seeds 0-2):
    EVALUATION-LIMITED      the expected or the sampled read-out is below the floor at h = 32
                            (mean over the 4 trajectories) and all four per-trajectory
                            differences from the floor are negative;
    NOT EVALUATION-LIMITED  otherwise.
  The autoregressive RSSM is reported alongside, with no reading.

PART B -- descriptive, no reading. Over the 32 history steps of each held-out window, at 2,500
and at 500 iterations: the one-step decoded error (relative-L1, residual base the true previous
row) from the prior's mode latent and from the posterior's mode latent, at the same GRU state;
and KL(posterior || prior) per step (the value, without balancing or free nats).

PART C -- only if Part A returns NOT EVALUATION-LIMITED and ruling U2 allows it (it does). Two
training variants, teacher-forced, seed 0, 2,500 iterations, everything else as M-75:
  V1  PlaNet's KL settings: weight 1.0, 3 free nats, no balancing (BASELINE_SPECS row 36);
  V2  DreamerV2's layer-normalised GRU (row 22).
  Run directories runs/baseline_rssm_tf_x1v1_seed{s}/ and runs/baseline_rssm_tf_x1v2_seed{s}/.
  A variant RESCUES on seed 0 if its mode read-out is below the floor at h = 32 with all four
  per-trajectory differences negative. For a variant that rescues, seeds 1-2 run, and the
  3-seed mean is read with the same criterion. Cap: 10 projected CPU-hours.
FINAL READING, exactly one of:
  EVALUATION-LIMITED; SETTING-LIMITED (V1), (V2) or (V1, V2) if a variant rescues on 3 seeds;
  NOT RESCUED BY THE SETTINGS TRIED; NOT RUN (ruling U2).

  python scripts/rssm_diagnostics.py --self-test     # every branch on synthetic inputs
  python scripts/rssm_diagnostics.py --part ab       # Parts A and B (T2)
  python scripts/rssm_diagnostics.py --part c        # Part C's reading, after its runs (T8)

Writes results/rssm_diagnostics.json (Part C adds its section to the same file).
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, os.pardir, "src"))
import numpy as np  # noqa: E402
import torch  # noqa: E402
import torch.nn.functional as Fn  # noqa: E402

import baselines as BL  # noqa: E402
import mn_sweep_eval as MN  # noqa: E402
import rollout_eval as E  # noqa: E402
import rwm_data as R  # noqa: E402
import rwm_metrics as MET  # noqa: E402

HORIZONS = ("1", "8", "32", "100", "368")
READ_H = "32"
SEEDS = (0, 1, 2)
N_SAMPLES, SAMPLE_SEED = 16, 0
M_HIST = 32
TOL = 1e-6
OUT = os.path.join(R.RESULTS, "rssm_diagnostics.json")
VARIANTS = {"V1": "x1v1", "V2": "x1v2"}


# ------------------------------------------------------------------ the criterion
def below_floor(per_traj, floor_traj):
    """Below the floor at the reading horizon: the mean below the floor's and all four
    per-trajectory differences negative. per_traj, floor_traj: (4,) relative-L1."""
    d = np.asarray(per_traj, dtype=np.float64) - np.asarray(floor_traj, dtype=np.float64)
    return bool(np.mean(per_traj) < np.mean(floor_traj) and np.all(d < 0)), d.tolist()


def part_a_reading(expected_tf, sampled_tf, floor):
    """EVALUATION-LIMITED if the expected or the sampled read-out (3-seed mean per trajectory)
    is below the floor at h = 32; NOT EVALUATION-LIMITED otherwise."""
    e, _ = below_floor(expected_tf, floor)
    s, _ = below_floor(sampled_tf, floor)
    return "EVALUATION-LIMITED" if (e or s) else "NOT EVALUATION-LIMITED"


def final_reading(part_a, u2_allows, part_c):
    """part_c: {"V1": {"seed0": bool, "three_seed": bool or None}, "V2": ...} or None."""
    if part_a == "EVALUATION-LIMITED":
        return "EVALUATION-LIMITED"
    if not u2_allows:
        return "NOT RUN (ruling U2)"
    if part_c is None:
        return None                          # Part C pending
    rescued = [v for v in ("V1", "V2") if part_c[v]["seed0"] and part_c[v]["three_seed"]]
    pending = [v for v in ("V1", "V2") if part_c[v]["seed0"] and part_c[v]["three_seed"] is None]
    if pending:
        return None
    return f"SETTING-LIMITED ({', '.join(rescued)})" if rescued else "NOT RESCUED BY THE SETTINGS TRIED"


# ------------------------------------------------------------------ the read-outs
def readout(model, st, ac, m, how, gen=None):
    """The RSSM's rollout with the forecast latent read out as `how`; the history is
    filtered exactly as RSSMBaseline.rollout filters it."""
    B, T, _ = st.shape
    pred = st.clone()
    hstate, z = model._init(B, st.device)
    with torch.no_grad():
        for t in range(m):
            h, hstate, _ = model._transition(hstate, z, ac[:, t])
            z = model._sample(model._posterior(h, st[:, t]), mode=True)
        prev = st[:, m - 1]
        for t in range(m, T):
            h, hstate, prior = model._transition(hstate, z, ac[:, t])
            if how == "mode":
                z = model._sample(prior, mode=True)
            elif how == "expected":
                z = torch.softmax(prior, -1).flatten(1)
            elif how == "sampled":
                probs = torch.softmax(prior, -1)
                idx = torch.multinomial(probs.reshape(-1, model.n_classes), 1, generator=gen).view(probs.shape[:-1])
                z = Fn.one_hot(idx, model.n_classes).to(probs.dtype).flatten(1)
            else:
                raise ValueError(how)
            mean, _ = model._decode(h, z, prev)
            pred[:, t] = mean
            prev = mean
    return pred


def score_readouts(model, data, cfg, scale, starts):
    st_np, ac_np = MN.window_arrays(data, cfg, starts, M_HIST, M_HIST)
    st, ac = torch.as_tensor(st_np), torch.as_tensor(ac_np)
    truth = st_np[:, M_HIST:]
    out = {}
    mode = readout(model, st.clone(), ac, M_HIST, "mode")
    own = model.rollout(st.clone(), ac, M_HIST, action_offset=1)
    assert torch.equal(mode, own), "the mode read-out is not the model's own rollout"
    out["mode"] = MN.metrics(mode.numpy()[:, M_HIST:] - truth, truth, scale)
    out["expected"] = MN.metrics(readout(model, st.clone(), ac, M_HIST, "expected").numpy()[:, M_HIST:] - truth, truth, scale)
    g = torch.Generator().manual_seed(SAMPLE_SEED)
    rep = lambda x: x.repeat_interleave(N_SAMPLES, dim=0)
    smp = readout(model, rep(st).clone(), rep(ac), M_HIST, "sampled", gen=g)
    smp = smp.view(len(starts), N_SAMPLES, *smp.shape[1:]).mean(1)
    out["sampled"] = MN.metrics(smp.numpy()[:, M_HIST:] - truth, truth, scale)
    return out


def history_diagnostics(model, data, cfg, starts):
    """Part B: per history step, one-step decoded relative-L1 from the prior's and the posterior's
    mode latents at the same GRU state, and KL(posterior || prior); steps 1..31 for the errors
    (row 0 has no previous row), 0..31 for the KL."""
    st_np, ac_np = MN.window_arrays(data, cfg, starts, M_HIST, M_HIST)
    st, ac = torch.as_tensor(st_np), torch.as_tensor(ac_np)
    B = st.shape[0]
    hstate, z = model._init(B, st.device)
    err_prior, err_post, kl = [], [], []
    rel = lambda pred, t: ((pred - st[:, t]).abs().sum(-1) / st[:, t].abs().sum(-1)).numpy()
    with torch.no_grad():
        for t in range(M_HIST):
            h, hstate, prior = model._transition(hstate, z, ac[:, t])
            post = model._posterior(h, st[:, t])
            p = torch.softmax(post, -1)
            kl.append((p * (torch.log_softmax(post, -1) - torch.log_softmax(prior, -1))).sum((-1, -2)).numpy())
            zq, zp = model._sample(post, mode=True), model._sample(prior, mode=True)
            if t >= 1:
                err_post.append(rel(model._decode(h, zq, st[:, t - 1])[0], t))
                err_prior.append(rel(model._decode(h, zp, st[:, t - 1])[0], t))
            z = zq
    err_prior, err_post, kl = np.stack(err_prior, 1), np.stack(err_post, 1), np.stack(kl, 1)   # (B, steps)
    return {"one_step_rel_l1_prior_per_step": err_prior.mean(0).tolist(),
            "one_step_rel_l1_posterior_per_step": err_post.mean(0).tolist(),
            "kl_per_step": kl.mean(0).tolist(),
            "mean_over_steps": {"one_step_rel_l1_prior": float(err_prior.mean()),
                                "one_step_rel_l1_posterior": float(err_post.mean()),
                                "prior_over_posterior": float(err_prior.mean() / err_post.mean()),
                                "kl": float(kl.mean())}}


def load(spec, regime, seed, iters, cfg):
    model = BL.build("rssm", spec, cfg)
    w = os.path.join("runs", f"baseline_rssm_{regime}_{spec}_seed{seed}", f"weights_{iters}.pt")
    model.load_state_dict(torch.load(w, map_location="cpu")["model_state_dict"], strict=True)
    model.eval()
    assert model.latent == "categorical"
    return model, w


def setup():
    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    data, ep = R.load_data(paths["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"), verbose=False)
    scale = MET.training_scale(data, ep, split["train_episodes"], cfg["state_data_mean"], cfg["state_data_std"])
    starts = MN.arena(ep, split["holdout_episodes"], M_HIST)["starts"]
    ev = json.load(open(os.path.join(R.RESULTS, "baselines_eval.json")))
    bv = json.load(open(os.path.join(R.RESULTS, "baselines_verdict.json")))
    assert starts == ev["arenas"]["held_out"]["starts"] == MN.HELD_OUT_STARTS
    floor = {h: ev["floor"]["held_out"][h]["l1"] for h in HORIZONS}
    for h in ("100", "368"):
        assert abs(np.mean(floor[h]) - bv["hold_last_floor_l1"]["held_out"][h]) < 1e-12, "floor disagrees with baselines_verdict.json"
    return cfg, data, scale, starts, ev, floor


def three_seed(per_seed, how, h):
    return np.mean([np.asarray(per_seed[str(s)][how][h]["l1"], dtype=np.float64) for s in SEEDS], 0)


def part_ab():
    cfg, data, scale, starts, ev, floor = setup()
    part_a, part_b, maxd = {}, {}, 0.0
    for regime in ("tf", "ar"):
        per_seed = {}
        for s in SEEDS:
            model, w = load("s7", regime, s, 2500, cfg)
            sc = score_readouts(model, data, cfg, scale, starts)
            committed = ev["configs"][f"rssm_{regime}_s7"]["seeds"][str(s)]["held_out"]
            for h in HORIZONS:
                d = max(abs(a - b) for a, b in zip(sc["mode"][h]["l1"], committed[h]["l1"]))
                maxd = max(maxd, d)
                assert d < TOL, f"mode read-out, rssm_{regime} seed {s} h={h}: differs from baselines_eval by {d}"
            per_seed[str(s)] = {"weights": w, **{how: {h: {"l1": sc[how][h]["l1"]} for h in HORIZONS} for how in sc}}
            m500, w500 = load("s7", regime, s, 500, cfg)
            part_b[f"rssm_{regime}_s7|seed{s}"] = {"2500": history_diagnostics(model, data, cfg, starts),
                                                   "500": history_diagnostics(m500, data, cfg, starts),
                                                   "weights_500": w500}
        mean = {how: {h: three_seed(per_seed, how, h).tolist() for h in HORIZONS} for how in ("mode", "expected", "sampled")}
        part_a[f"rssm_{regime}_s7"] = {
            "per_seed": per_seed, "three_seed_per_traj": mean,
            "three_seed_mean": {how: {h: float(np.mean(mean[how][h])) for h in HORIZONS} for how in mean},
            "below_floor_at_h32": {how: dict(zip(("below", "per_traj_minus_floor"),
                                                 below_floor(mean[how][READ_H], floor[READ_H]))) for how in mean}}
    tf = part_a["rssm_tf_s7"]["three_seed_per_traj"]
    reading = part_a_reading(tf["expected"][READ_H], tf["sampled"][READ_H], floor[READ_H])
    out = {"rule": "X1", "exploratory": True, "never_reopens": ["M-75", "M-76"],
           "arena": {"name": "held-out pair", "starts": starts, "n_independent": 4, "history_rows": M_HIST,
                     "forecast_rows": MN.FORECAST, "metric": "relative-L1 per trajectory (mn_sweep_eval.metrics)",
                     "horizons": list(HORIZONS)},
           "floor_l1_per_traj": floor,
           "floor_mean": {h: float(np.mean(floor[h])) for h in HORIZONS},
           "sampled": {"n_samples": N_SAMPLES, "generator_seed": SAMPLE_SEED},
           "part_a": part_a,
           "part_a_mode_reproduces_baselines_eval": {"max_abs_diff": maxd, "tolerance": TOL},
           "part_a_reading": reading,
           "part_a_reading_rule": "teacher-forced RSSM, 3-seed mean: EVALUATION-LIMITED if the expected or the sampled read-out is "
                                  "below the floor at h = 32 with all four per-trajectory differences negative; NOT EVALUATION-LIMITED otherwise",
           "part_b": part_b,
           "u2_allows_part_c": True,
           "final_reading": final_reading(reading, True, None),
           "part_c": None}
    json.dump(out, open(OUT, "w"), indent=2)
    print("=" * 96)
    print("X1 — RSSM diagnostic, Parts A and B")
    print("=" * 96)
    print(f"  mode read-out reproduces baselines_eval.json: max |diff| {maxd:.2e}")
    print(f"  floor (hold-last) mean relative-L1: " + "  ".join(f"h={h} {np.mean(floor[h]):.4f}" for h in HORIZONS))
    for k, v in part_a.items():
        for how in ("mode", "expected", "sampled"):
            print(f"  {k:<12} {how:<9} " + "  ".join(f"h={h} {v['three_seed_mean'][how][h]:.4f}" for h in HORIZONS)
                  + f"   below floor at h=32: {v['below_floor_at_h32'][how]['below']}")
    for k, v in part_b.items():
        a, b = v["2500"]["mean_over_steps"], v["500"]["mean_over_steps"]
        print(f"  B {k:<20} 2500: prior/post one-step {a['prior_over_posterior']:.2f}  KL {a['kl']:.2f}   500: {b['prior_over_posterior']:.2f}  KL {b['kl']:.2f}")
    print(f"  PART A READING: {reading}")
    print(f"  wrote {R.rel(OUT)}")


def part_c():
    cfg, data, scale, starts, ev, floor = setup()
    out = json.load(open(OUT))
    assert out["part_a_reading"] == "NOT EVALUATION-LIMITED", "Part C runs only after NOT EVALUATION-LIMITED"
    res = {}
    for v, spec in VARIANTS.items():
        per_seed = {}
        for s in SEEDS:
            w = os.path.join("runs", f"baseline_rssm_tf_{spec}_seed{s}", "weights_2500.pt")
            if not os.path.exists(w):
                continue
            model, _ = load(spec, "tf", s, 2500, cfg)
            per_seed[str(s)] = {"weights": w, "mode": MN.score(model, data, cfg, scale, starts, M_HIST, M_HIST)}
        assert "0" in per_seed, f"{v}: seed 0 has not run"
        s0, d0 = below_floor(per_seed["0"]["mode"][READ_H]["l1"], floor[READ_H])
        three = None
        if s0 and all(str(s) in per_seed for s in SEEDS):
            mean = np.mean([per_seed[str(s)]["mode"][READ_H]["l1"] for s in SEEDS], 0)
            three = below_floor(mean, floor[READ_H])[0]
        res[v] = {"spec": spec, "seed0": s0, "seed0_per_traj_minus_floor": d0, "three_seed": three,
                  "per_seed_mean_l1": {s: {h: float(np.mean(r["mode"][h]["l1"])) for h in HORIZONS} for s, r in per_seed.items()},
                  "per_seed": {s: {"weights": r["weights"], **{h: r["mode"][h]["l1"] for h in HORIZONS}} for s, r in per_seed.items()}}
    out["part_c"] = res
    out["final_reading"] = final_reading(out["part_a_reading"], out["u2_allows_part_c"], res)
    json.dump(out, open(OUT, "w"), indent=2)
    print(f"  X1 Part C: {json.dumps({v: {'seed0': r['seed0'], 'three_seed': r['three_seed']} for v, r in res.items()})}")
    print(f"  X1 FINAL READING: {out['final_reading']}")


# ------------------------------------------------------------------ self-test
def self_test():
    f = [1.0, 1.0, 1.0, 1.0]
    ok = []
    ok.append(below_floor([0.5, 0.5, 0.5, 0.5], f)[0] is True)
    ok.append(below_floor([0.5, 0.5, 0.5, 1.2], f)[0] is False)       # mean below, one trajectory above
    ok.append(below_floor([1.5, 1.5, 1.5, 1.5], f)[0] is False)
    ok.append(below_floor([1.0, 0.5, 0.5, 0.5], f)[0] is False)       # a tie is not below
    ok.append(part_a_reading([0.5] * 4, [2.0] * 4, f) == "EVALUATION-LIMITED")
    ok.append(part_a_reading([2.0] * 4, [0.5] * 4, f) == "EVALUATION-LIMITED")
    ok.append(part_a_reading([2.0] * 4, [2.0] * 4, f) == "NOT EVALUATION-LIMITED")
    ok.append(final_reading("EVALUATION-LIMITED", True, None) == "EVALUATION-LIMITED")
    ok.append(final_reading("NOT EVALUATION-LIMITED", False, None) == "NOT RUN (ruling U2)")
    ok.append(final_reading("NOT EVALUATION-LIMITED", True, None) is None)
    no = {"seed0": False, "three_seed": None}
    ok.append(final_reading("NOT EVALUATION-LIMITED", True, {"V1": no, "V2": no}) == "NOT RESCUED BY THE SETTINGS TRIED")
    ok.append(final_reading("NOT EVALUATION-LIMITED", True, {"V1": {"seed0": True, "three_seed": True}, "V2": no}) == "SETTING-LIMITED (V1)")
    ok.append(final_reading("NOT EVALUATION-LIMITED", True, {"V1": {"seed0": True, "three_seed": False}, "V2": no}) == "NOT RESCUED BY THE SETTINGS TRIED")
    ok.append(final_reading("NOT EVALUATION-LIMITED", True, {"V1": {"seed0": True, "three_seed": True}, "V2": {"seed0": True, "three_seed": True}}) == "SETTING-LIMITED (V1, V2)")
    ok.append(final_reading("NOT EVALUATION-LIMITED", True, {"V1": {"seed0": True, "three_seed": None}, "V2": no}) is None)
    print(f"  X1 self-test: {sum(ok)}/{len(ok)} branches correct")
    return all(ok)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--part", choices=["ab", "c"])
    a = ap.parse_args()
    if a.self_test:
        sys.exit(0 if self_test() else 1)
    if not self_test():
        sys.exit("self-test failed")
    if a.part == "ab":
        part_ab()
    elif a.part == "c":
        part_c()
    else:
        ap.error("give --self-test, --part ab or --part c")


if __name__ == "__main__":
    main()
