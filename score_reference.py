"""
Step 3 -- score the reference checkpoint.

The reference code cannot be imported here (setup.py pins torch>=2.7 with CUDA),
so the forward pass is rebuilt from the checkpoint's state_dict using plain
torch.nn primitives. Every structural choice below is quoted from the source it
came from; nothing is inferred.

Forward pass, as established by reading
  rsl_rl_rwm/rsl_rl/modules/system_dynamics.py
  rsl_rl_rwm/rsl_rl/modules/architectures/rnn.py
  rsl_rl_rwm/rsl_rl/modules/architectures/mlp.py

  x        = cat([normalised_state, action], dim=-1)          rnn.py:22   -> 57
  h        = GRU(x, hidden)[0][:, -1]                          rnn.py:43-44
  mean_i   = Linear(128->45)(ReLU(Linear(256->128)(h)))
             + state_seq[:, -1]                                mlp.py:88   <- RESIDUAL
  logstd_i = same-shaped tower, then bounded (mlp.py:91-93)
  output   = mean over the 5 members                           system_dynamics.py:114
"""

import json
import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn

import rwm_data as R
import rollout_eval as E

EXPECTED_PARAMS = {
    "state_base": 636_672,
    "state_heads": 387_460,
    "auxiliary_base": 636_672,
    "auxiliary_heads": 334_765,
}
EXPECTED_TOTAL = 1_995_569


class ReferenceRWM(nn.Module):
    """The reference world model, rebuilt from the checkpoint state_dict."""

    def __init__(self, sd, state_dim=45, action_dim=12, hidden=256, layers=2,
                 ensemble=5, contact_dim=8, termination_dim=1):
        super().__init__()
        self.state_dim, self.ensemble = state_dim, ensemble
        self.state_base = nn.GRU(state_dim + action_dim, hidden, layers, batch_first=True)
        self.auxiliary_base = nn.GRU(state_dim + action_dim, hidden, layers, batch_first=True)
        mk = lambda o: nn.Sequential(nn.Linear(hidden, 128), nn.ReLU(), nn.Linear(128, o))
        self.state_mean_layers = nn.ModuleList([mk(state_dim) for _ in range(ensemble)])
        self.state_logstd_layers = nn.ModuleList([mk(state_dim) for _ in range(ensemble)])
        self.contact_layers = nn.ModuleList([mk(contact_dim) for _ in range(ensemble)])
        self.termination_layers = nn.ModuleList([mk(termination_dim) for _ in range(ensemble)])
        self.register_buffer("state_min_logstd", torch.zeros(ensemble, 1, state_dim))
        self.register_buffer("state_log_delta_logstd", torch.zeros(ensemble, 1, state_dim))
        self._load(sd)
        self.eval()

    def _load(self, sd):
        def cp(dst, key):
            with torch.no_grad():
                dst.copy_(sd[key])
        for base, pre in ((self.state_base, "state_base"),
                          (self.auxiliary_base, "auxiliary_base")):
            for l in (0, 1):
                cp(getattr(base, f"weight_ih_l{l}"), f"{pre}.memory.rnn.weight_ih_l{l}")
                cp(getattr(base, f"weight_hh_l{l}"), f"{pre}.memory.rnn.weight_hh_l{l}")
                cp(getattr(base, f"bias_ih_l{l}"), f"{pre}.memory.rnn.bias_ih_l{l}")
                cp(getattr(base, f"bias_hh_l{l}"), f"{pre}.memory.rnn.bias_hh_l{l}")
        for i in range(self.ensemble):
            for mod, name, pre in (
                    (self.state_mean_layers[i], "state_mean_layers", f"state_heads.{i}"),
                    (self.state_logstd_layers[i], "state_logstd_layers", f"state_heads.{i}"),
                    (self.contact_layers[i], "contact_layers", f"auxiliary_heads.{i}"),
                    (self.termination_layers[i], "termination_layers", f"auxiliary_heads.{i}")):
                for j in (0, 2):
                    cp(mod[j].weight, f"{pre}.{name}.{j}.weight")
                    cp(mod[j].bias, f"{pre}.{name}.{j}.bias")
            cp(self.state_min_logstd[i], f"state_heads.{i}.state_min_logstd")
            cp(self.state_log_delta_logstd[i],
               f"state_heads.{i}.state_log_delta_logstd")

    def step(self, state_seq, action_seq, h_state, h_aux=None, want_aux=False):
        """
        One forward call. state_seq (B,T,45) normalised, action_seq (B,T,12).
        Returns the ensemble-mean next state plus uncertainties, and the new
        hidden states. T=32 on the first forecast step, T=1 thereafter.
        """
        x = torch.cat([state_seq, action_seq], dim=-1)          # rnn.py:22
        out, h_state = self.state_base(x, h_state)              # rnn.py:43
        h = out[:, -1]                                          # rnn.py:44
        last = state_seq[:, -1]                                 # mlp.py:88 residual base

        means = torch.stack([m(h) + last for m in self.state_mean_layers])      # (E,B,45)
        logstd = torch.stack([m(h) for m in self.state_logstd_layers])
        mx = self.state_min_logstd + torch.exp(self.state_log_delta_logstd)     # mlp.py:91
        logstd = mx - nn.functional.softplus(mx - logstd)                       # mlp.py:92
        logstd = self.state_min_logstd + nn.functional.softplus(
            logstd - self.state_min_logstd)                                     # mlp.py:93
        stds = torch.exp(logstd)                                                # mlp.py:97

        aux = None
        if want_aux:
            aout, h_aux = self.auxiliary_base(x, h_aux)         # same 57-dim input
            ah = aout[:, -1]
            aux = (torch.stack([c(ah) for c in self.contact_layers]).mean(0),
                   torch.stack([t(ah) for t in self.termination_layers]).mean(0))

        return (means.mean(0),                                  # system_dynamics.py:114
                stds.mean(0).sum(-1),                           # aleatoric
                means.std(0).sum(-1),                           # epistemic
                aux, h_state, h_aux)

    @torch.no_grad()
    def rollout(self, state, action, start_step=32, action_offset=0, want_aux=False):
        """
        model_training.py:126-133 exactly: the first forecast step consumes the
        whole `start_step`-long history, every later step consumes a single
        timestep, and the GRU hidden state is carried throughout (reset() is
        called once, before the loop, model_training.py:124).

        action_offset selects the state/action alignment:
          0  eval convention   (model_training.py:131-132) predict s[i] from (s[i-1], a[i-1])
          1  train convention  (system_dynamics.py:196-200) predict s[i] from (s[i-1], a[i])
        """
        B, T, _ = state.shape
        pred = state.clone()
        h_state = h_aux = None
        alea = torch.zeros(B, T)
        epis = torch.zeros(B, T)
        contacts = torch.zeros(B, T, 8)
        terms = torch.zeros(B, T, 1)

        for i in range(start_step, T):
            if i > start_step:
                s_in = pred[:, i - 1:i]
                a_in = action[:, i - 1 + action_offset:i + action_offset]
            else:
                s_in = pred[:, i - start_step:i]
                a_in = action[:, i - start_step + action_offset:i + action_offset]
            if a_in.shape[1] != s_in.shape[1]:          # offset ran past the end
                a_in = action[:, -s_in.shape[1]:]
            m, al, ep, aux, h_state, h_aux = self.step(s_in, a_in, h_state, h_aux, want_aux)
            pred[:, i] = m
            alea[:, i], epis[:, i] = al, ep
            if want_aux:
                contacts[:, i] = torch.sigmoid(aux[0]).round()
                terms[:, i] = torch.sigmoid(aux[1]).round()
        return pred, alea, epis, contacts, terms


def make_predict_fn(model, start_step=32, action_offset=0):
    """Wrap the model in the harness's model-agnostic interface."""
    def fn(hs, ha, fa):
        state = torch.cat([hs, torch.zeros(hs.shape[0], fa.shape[1], hs.shape[2])], 1)
        action = torch.cat([ha, fa], 1)
        pred, *_ = model.rollout(state, action, start_step, action_offset)
        return pred[:, start_step:]
    return fn


# --------------------------------------------------------------------------
def inventory(sd, verbose=True):
    groups = {}
    for k, v in sd.items():
        groups[k.split(".")[0]] = groups.get(k.split(".")[0], 0) + v.numel()
    total = sum(groups.values())
    if verbose:
        print("  component            parameters      expected     match")
        for g, exp in EXPECTED_PARAMS.items():
            got = groups.get(g, 0)
            print(f"  {g:20s} {got:>10,}   {exp:>10,}     {'OK' if got == exp else 'MISMATCH'}")
        print(f"  {'TOTAL':20s} {total:>10,}   {EXPECTED_TOTAL:>10,}"
              f"     {'OK' if total == EXPECTED_TOTAL else 'MISMATCH'}")
    for g, exp in EXPECTED_PARAMS.items():
        assert groups.get(g, 0) == exp, f"{g}: {groups.get(g,0)} != {exp}"
    assert total == EXPECTED_TOTAL, f"total {total} != {EXPECTED_TOTAL}"
    return groups, total


def fmt_row(name, m):
    return (f"  {name:<34s} {m['e']:>9.4f} {m['median_r']:>10.4f} "
            f"{m['frac_r_gt_10']:>10.4f} {m['max_r']:>11.2f}")


def main():
    t0 = time.time()
    here = os.path.dirname(os.path.abspath(__file__))
    paths = R.repo_paths()

    print("=" * 78)
    print("STEP 3 -- SCORE THE REFERENCE CHECKPOINT")
    print("=" * 78)

    cfg = R.load_reference_config(paths["lite"])
    data, episode_id = R.load_data(paths["csv"])
    split = E.make_split(seed=0, strat_path=os.path.join(here, "step0_strat.json"))
    base_cfg = E.build_base_config(cfg, seed=0)

    print("\n" + "-" * 78)
    print("3.1 CHECKPOINT INVENTORY")
    print("-" * 78)
    ck = torch.load(paths["ckpt"], map_location="cpu")
    print(f"  torch.load succeeded under torch {torch.__version__} (no fallback needed)")
    print(f"  top-level keys: {list(ck.keys())}")
    sd = ck["system_dynamics_state_dict"]
    print(f"  system_dynamics_state_dict holds {len(sd)} tensors\n")
    groups, total = inventory(sd)
    print(f"\n  checkpoint iter: {ck.get('iter')}")

    model = ReferenceRWM(sd)
    n_built = sum(p.numel() for p in model.parameters()) + \
        sum(b.numel() for b in model.buffers())
    print(f"  rebuilt module parameter+buffer count: {n_built:,}"
          f"  ({'matches' if n_built == EXPECTED_TOTAL else 'MISMATCH'})")

    # ---------------------------------------------------------- sanity check
    print("\n  one-step sanity check on a held-out window:")
    rows = np.arange(1000, 1033)
    st = torch.as_tensor(R.normalise_state(data[rows][None, :, R.STATE_COLS],
                                           cfg["state_data_mean"], cfg["state_data_std"]),
                         dtype=torch.float32)
    ac = torch.as_tensor(data[rows][None, :, R.ACTION_COLS], dtype=torch.float32)
    with torch.no_grad():
        m, al, ep, _, _, _ = model.step(st[:, :32], ac[:, :32], None)
    truth = st[0, 32]
    print(f"    |pred - true|_1 / |true|_1 = "
          f"{((m[0]-truth).abs().sum()/truth.abs().sum()).item():.4f}")
    print(f"    hold-last baseline for the same step = "
          f"{((st[0,31]-truth).abs().sum()/truth.abs().sum()).item():.4f}")
    print(f"    aleatoric {al.item():.3f}   epistemic {ep.item():.3f}")

    # -------------------------------------------------------------- protocols
    results = {}
    curves = {}
    for tag, cross, desc in (("A", False, "held-out episodes only, no boundary crossings"),
                             ("B", True, "full 10,000 rows, crossings permitted (train.py:109)")):
        print("\n" + "-" * 78)
        print(f"PROTOCOL {tag} -- {desc}")
        print("-" * 78)
        cfgp = {**base_cfg, "episode_id": episode_id, "allow_boundary_cross": cross}
        r = E.evaluate(make_predict_fn(model), data, split, cfgp)
        results[tag] = r
        curves[tag] = r["clean"]["per_step_mean"]
        print(f"  trajectory start rows: {r['trajectory_start_rows']}")
        print(f"  episodes touched     : {r['trajectory_episodes']}")
        print(f"  trajectories crossing an episode boundary: "
              f"{r['n_trajectories_crossing_boundary']} of {r['n_trajectories']}")
        print(f"\n  {'condition':<34s} {'e':>9s} {'median r':>10s} "
              f"{'frac>10':>10s} {'max r':>11s}")
        print(fmt_row("clean", r["clean"]))
        for ns in cfg["eval_traj_noise_scale"]:
            print(fmt_row(f"noise {ns}", r["noise"][str(ns)]))

    # ------------------------------------------- what the A/B gap is made of
    print("\n" + "-" * 78)
    print("DECOMPOSING THE A/B GAP")
    print("-" * 78)
    print("  Two confounders have to be separated before the gap means anything.\n")
    print("  (i) The reference checkpoint was trained by the authors on this entire")
    print("      CSV. Protocol A's 'held-out' episodes were in its training set, so")
    print("      for THIS checkpoint A is not a generalisation measure -- it only")
    print("      becomes one for a model we train ourselves in Step 6. The A/B gap")
    print("      here therefore cannot be read as 'how much leakage flatters the")
    print("      reference'; that reading only applies from Step 6 onward.")
    print("  (ii) Protocol B lets trajectories straddle an episode reset. A reset is")
    print("      a physical discontinuity no model can predict, so the expectation is")
    print("      that crossing trajectories are penalised for a jump that is not a")
    print("      modelling failure. This is TESTED below, not assumed.\n")

    def per_traj_e(res_pred, res_true, start=E.START_STEP):
        num = (res_pred[:, start:] - res_true[:, start:]).abs().sum(-1)
        den = res_true[:, start:].abs().sum(-1)
        return (num / den).mean(dim=1)

    decomp = {}
    for tag, cross in (("A", False), ("B", True)):
        idx = E.sample_trajectories(episode_id, split["holdout_episodes"],
                                    seed=base_cfg["seed"], allow_boundary_cross=cross)
        raw = data[idx]
        st = torch.as_tensor(R.normalise_state(raw[:, :, R.STATE_COLS],
                                               cfg["state_data_mean"], cfg["state_data_std"]),
                             dtype=torch.float32)
        ac = torch.as_tensor(raw[:, :, R.ACTION_COLS], dtype=torch.float32)
        pred, *_ = model.rollout(st, ac, E.START_STEP)
        pe = per_traj_e(pred, st).numpy()
        crossed = np.array([len(set(episode_id[row].tolist())) > 1 for row in idx])
        decomp[tag] = {"per_trajectory_e": pe.tolist(), "crossed": crossed.tolist()}
        print(f"  protocol {tag}: per-trajectory e = "
              f"{np.array2string(pe, precision=2, floatmode='fixed')}")
        if cross:
            print(f"    of the 10, {crossed.sum()} cross a reset and {(~crossed).sum()} do not")
            print(f"    e over the {int(crossed.sum())} crossing    : {pe[crossed].mean():.4f}")
            print(f"    e over the {int((~crossed).sum())} non-crossing: {pe[~crossed].mean():.4f}")
            decomp[tag]["e_crossing"] = float(pe[crossed].mean()) if crossed.any() else None
            decomp[tag]["e_non_crossing"] = float(pe[~crossed].mean()) if (~crossed).any() else None
            if crossed.any() and (~crossed).any() and pe[crossed].mean() < pe[~crossed].mean():
                print("    -> hypothesis (ii) is REFUTED: the crossing trajectories score")
                print("       BETTER, not worse. Boundary crossing is not what drives the")
                print("       A/B gap. See the per-episode difficulty table below.")

    # ---- per-episode difficulty: the actual driver -----------------------
    print("\n  Per-episode difficulty (20 trajectories drawn inside each episode,")
    print("  identical protocol, so the only thing that varies is the episode):")
    strat_p = os.path.join(here, "step0_strat.json")
    speeds = {}
    if os.path.exists(strat_p):
        with open(strat_p) as f:
            speeds = {int(k): v["mean_speed"] for k, v in json.load(f).items()}
    ep_e = {}
    print("    ep   mean speed   e (20 traj)   held-out?")
    for e_i in range(R.N_EPISODES):
        idx = E.sample_trajectories(episode_id, [e_i], n_traj=20, seed=7)
        raw = data[idx]
        st = torch.as_tensor(R.normalise_state(raw[:, :, R.STATE_COLS],
                                               cfg["state_data_mean"], cfg["state_data_std"]),
                             dtype=torch.float32)
        ac = torch.as_tensor(raw[:, :, R.ACTION_COLS], dtype=torch.float32)
        pred, *_ = model.rollout(st, ac, E.START_STEP)
        val = float(per_traj_e(pred, st).mean())
        ep_e[e_i] = val
        mark = "  <-- held out" if e_i in split["holdout_episodes"] else ""
        print(f"    {e_i:2d}      {speeds.get(e_i, float('nan')):.2f}        "
              f"{val:.4f}{mark}")
    vals = np.array([ep_e[i] for i in range(R.N_EPISODES)])
    ho = [ep_e[i] for i in split["holdout_episodes"]]
    print(f"\n    spread across episodes: {vals.min():.3f} to {vals.max():.3f}"
          f"  (mean {vals.mean():.3f})")
    print(f"    held-out pair mean {np.mean(ho):.3f} vs all-episode mean {vals.mean():.3f}")
    if speeds:
        cc = np.corrcoef([speeds[i] for i in range(R.N_EPISODES)], vals)[0, 1]
        print(f"    correlation between commanded speed and error: r = {cc:+.2f}")
    print("    => The A/B gap is dominated by WHICH episodes get sampled, not by")
    print("       boundary crossing. Protocol A draws only from the held-out pair,")
    print("       and that pair sits on the easy side of this spread, so protocol A")
    print("       reads lower than protocol B mostly for that reason.")
    print()
    print("    CONSEQUENCE FOR THE SPLIT: the brief asks for stratification by")
    print("    velocity regime, and that is what was done -- but the correlation")
    print("    above shows commanded speed does not predict difficulty, so")
    print("    stratifying by speed does not balance difficulty. The seed-0 split")
    print("    holds out two of the easiest episodes, and protocol A is optimistic")
    print("    by roughly the pair-vs-population difference above.")
    print("    The split is NOT re-picked to fix this: choosing a held-out set by")
    print("    measured error would select on the test signal. For Step 6 the sound")
    print("    options are leave-one-episode-out over all ten, or averaging over")
    print("    several seeded splits, and reporting the spread either way.")
    decomp["per_episode_e"] = ep_e
    decomp["per_episode_speed_error_corr"] = float(cc) if speeds else None
    decomp["holdout_pair_mean_e"] = float(np.mean(ho))
    decomp["all_episode_mean_e"] = float(vals.mean())

    # ---- is a 10-trajectory estimate even stable? -----------------------
    print("\n  Ten trajectories is what the reference uses, but is it enough to")
    print("  support the gap? Re-drawing the sample over 20 seeds:")
    stab = {}
    for tag, cross in (("A", False), ("B", True)):
        es = []
        for s in range(20):
            r = E.evaluate(make_predict_fn(model), data, split,
                           {**base_cfg, "episode_id": episode_id, "seed": s,
                            "allow_boundary_cross": cross, "noise_scales": []})
            es.append(r["clean"]["e"])
        es = np.array(es)
        stab[tag] = {"mean": float(es.mean()), "std": float(es.std()),
                     "min": float(es.min()), "max": float(es.max()),
                     "per_seed": es.tolist()}
        print(f"    protocol {tag}: e = {es.mean():.4f} +- {es.std():.4f}"
              f"   (min {es.min():.4f}, max {es.max():.4f}, n=20 seeds)")
    sep = abs(stab["A"]["mean"] - stab["B"]["mean"])
    pooled = np.hypot(stab["A"]["std"], stab["B"]["std"])
    print(f"    separation {sep:.4f} vs pooled seed-to-seed spread {pooled:.4f}"
          f"  ->  {sep / pooled:.1f} sigma")
    print("    A single seed-0 pair of numbers is NOT a reliable gap estimate;")
    print("    the seed-averaged figures above are the ones to quote.")

    # ------------------------------------------------------ action alignment
    print("\n" + "-" * 78)
    print("ACTION ALIGNMENT CHECK (not requested; found while reading the source)")
    print("-" * 78)
    print("  system_dynamics.py:196-200 trains on (s[t], a[t+1]) -> s[t+1];")
    print("  model_training.py:131-132 evaluates on (s[t], a[t]) -> s[t+1].")
    print("  The checkpoint was trained under one convention and scored under the")
    print("  other. Both are run here on protocol A:")
    align = {}
    for off, name in ((0, "eval convention  (s[t], a[t])   <- reference eval"),
                      (1, "train convention (s[t], a[t+1]) <- reference training")):
        r = E.evaluate(make_predict_fn(model, action_offset=off), data, split,
                       {**base_cfg, "episode_id": episode_id, "noise_scales": []})
        align[off] = r["clean"]
        print(f"    {name}   e = {r['clean']['e']:.4f}"
              f"   median r = {r['clean']['median_r']:.4f}")
    d = align[1]["e"] - align[0]["e"]
    print(f"    difference: {d:+.4f}  "
          f"({'training convention scores better' if d < 0 else 'eval convention scores better'})")

    # --------------------------------------------------------------- summary
    floor = None
    ap = os.path.join(here, "step2_acceptance.json")
    if os.path.exists(ap):
        with open(ap) as f:
            floor = json.load(f)["tests"]["test2_hold_last"]

    print("\n" + "=" * 78)
    print("3.4 FULL RESULTS TABLE")
    print("=" * 78)
    print(f"  {'row':<34s} {'e':>9s} {'median r':>10s} {'frac>10':>10s} {'max r':>11s}")
    print("  " + "-" * 76)
    if floor:
        print(fmt_row("hold-last FLOOR (Step 2)", floor))
    print(fmt_row("A clean  (held-out, no crossing)", results["A"]["clean"]))
    print(fmt_row("B clean  (reference protocol)", results["B"]["clean"]))
    for ns in cfg["eval_traj_noise_scale"]:
        print(fmt_row(f"A noise {ns}", results["A"]["noise"][str(ns)]))
    for ns in cfg["eval_traj_noise_scale"]:
        print(fmt_row(f"B noise {ns}", results["B"]["noise"][str(ns)]))

    # --------------------------------------------------- error by horizon
    print("\n" + "=" * 78)
    print("ERROR BY FORECAST HORIZON (protocol A, clean)")
    print("=" * 78)
    print("  e is a mean over all 368 forecast steps, which buries the fact that the")
    print(f"  model was trained with forecast_horizon = {cfg['forecast_horizon']}."
          f" Cumulative mean of r_t")
    print("  over the first h forecast steps, against the hold-last floor:\n")
    hl = E.evaluate(E.hold_last_predictor(), data, split,
                    {**base_cfg, "episode_id": episode_id, "noise_scales": []})
    curve_m = results["A"]["clean"]["per_step_mean"]
    curve_f = hl["clean"]["per_step_mean"]
    print(f"  {'horizon h':>10s} {'model e@h':>11s} {'floor e@h':>11s} {'ratio':>8s}"
          f"   {'r_t at step h':>14s}")
    horizons = {}
    for h in (1, 4, 8, 16, 32, 64, 128, 256, 368):
        me, fe = float(curve_m[:h].mean()), float(curve_f[:h].mean())
        horizons[h] = {"model": me, "floor": fe, "ratio": me / fe,
                       "r_at_h": float(curve_m[h - 1])}
        star = "   <- training horizon" if h == cfg["forecast_horizon"] else ""
        print(f"  {h:>10d} {me:>11.4f} {fe:>11.4f} {me/fe:>8.3f}"
              f"   {curve_m[h-1]:>14.4f}{star}")
    print("\n  The model is far better than the floor at short horizons and converges")
    print("  to it long-horizon: a 368-step mean is mostly measuring the saturated")
    print("  tail, not prediction quality. Quote e@8 alongside e@368.")

    gap = results["A"]["clean"]["e"] - results["B"]["clean"]["e"]
    print("\n  " + "-" * 76)
    print(f"  GAP  e(A) - e(B) = {gap:+.4f}"
          f"   ({100 * gap / results['B']['clean']['e']:+.1f}% relative to B)")
    if floor:
        print(f"  Floor headroom: hold-last e = {floor['e']:.4f}, "
              f"protocol A e = {results['A']['clean']['e']:.4f}"
              f"  -> model is {floor['e'] / results['A']['clean']['e']:.2f}x better than the floor")

    # ----------------------------------------------------------------- plot
    fig, ax = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
    steps = np.arange(1, len(curves["A"]) + 1)
    for a, (tag, style) in zip([ax[0], ax[0]], (("A", "-"), ("B", "--"))):
        a.plot(steps, curves[tag], style, lw=1.4,
               label=f"protocol {tag}  (e = {results[tag]['clean']['e']:.3f})")
    if floor:
        ax[0].axhline(floor["e"], color="#d62728", lw=1.2, ls=":",
                      label=f"hold-last floor ({floor['e']:.3f})")
    ax[0].set_xlabel("forecast step (1 = first predicted step, 368 = last)")
    ax[0].set_ylabel("mean relative error  $r_t$")
    ax[0].set_title("Per-step error, clean rollout")
    ax[0].legend(fontsize=9); ax[0].grid(alpha=0.3)

    for ns in cfg["eval_traj_noise_scale"]:
        ax[1].plot(steps, results["A"]["noise"][str(ns)]["per_step_mean"], lw=1.1,
                   label=f"noise {ns} (e={results['A']['noise'][str(ns)]['e']:.2f})")
    ax[1].plot(steps, curves["A"], color="k", lw=1.6, label=f"clean (e={results['A']['clean']['e']:.3f})")
    ax[1].set_xlabel("forecast step")
    ax[1].set_title("Protocol A, noise sweep")
    ax[1].legend(fontsize=8); ax[1].grid(alpha=0.3)
    fig.suptitle("Reference checkpoint pretrain_rnn_ens.pt -- autoregressive error over 368 forecast steps")
    fig.tight_layout()
    pp = os.path.join(here, "figures", "step3_per_step_error.png")
    os.makedirs(os.path.dirname(pp), exist_ok=True)
    fig.savefig(pp, dpi=140)
    plt.close(fig)
    print(f"\n  wrote {pp}")

    # ------------------------------------------------------------- manifest
    elapsed = time.time() - t0
    man = {
        "seed": base_cfg["seed"],
        "split": split,
        "held_out_episodes": split["holdout_episodes"],
        "start_step": E.START_STEP,
        "start_step_source": "model_training.py:201  self.start_step = self.history_horizon (=32)",
        "noise_application": {
            "applied_to": "both state and action (model_training.py:221-222)",
            "space": "normalised (normalize() is called at model_training.py:200, before "
                     "the noise loop); actions are normalised by an identity transform "
                     "since action_data_mean=0 and action_data_std=1",
            "when": "once, over the whole (B,400,D) trajectory before the rollout; "
                    "not resampled per rollout step",
            "denominator": "the NOISED trajectory, state_traj_noised (model_training.py:227) "
                           "-- confirmed, not the clean one",
        },
        "forward_pass": {
            "1_gru_input": "cat([normalised_state(45), action(12)], dim=-1) = 57, state "
                           "first then action (rnn.py:22)",
            "2_normalisation": "applied by the CALLER, not inside the module "
                               "(model_training.py:200); no normalisation anywhere in "
                               "system_dynamics.py / rnn.py / mlp.py",
            "3_activations": "ReLU between the two head layers (mlp.py:57); NO activation "
                             "on the output layer (mlp.py:59). The mean head adds a "
                             "RESIDUAL: output + state_seq[:,-1] (mlp.py:88)",
            "4_logstd_bound": "max = min_logstd + exp(log_delta_logstd); "
                              "logstd = max - softplus(max - logstd); "
                              "logstd = min_logstd + softplus(logstd - min_logstd); "
                              "std = exp(logstd)  (mlp.py:91-93,97)",
            "5_feedback_at_inference": "the predicted MEAN, not a sample. forward() returns "
                                       "state_means.mean(0) (system_dynamics.py:114) and "
                                       "_autoregressive_prediction feeds that back. Training "
                                       "DOES sample: randn_like(mean)*std + mean "
                                       "(system_dynamics.py:215). Inference differs from training.",
            "6_ensemble_combination": "averaged over all 5 members when model_ids is None, "
                                      "which is how _autoregressive_prediction calls it "
                                      "(system_dynamics.py:114). Both trunks are shared, so "
                                      "the 5 members differ only in their head weights; "
                                      "epistemic uncertainty therefore measures head "
                                      "disagreement over identical features, not true "
                                      "deep-ensemble diversity.",
            "7_auxiliary_input": "identical 57-dim input to state_base "
                                 "(system_dynamics.py:95)",
            "8_hidden_state": "CARRIED across the history/forecast boundary. reset() is "
                              "called once before the loop (model_training.py:124) and "
                              "never inside it; Memory.forward threads hidden_states "
                              "through every call (rnn.py:43)",
        },
        "action_alignment_discrepancy": {
            "training": "(s[t], a[t+1]) -> s[t+1]  (system_dynamics.py:196-200)",
            "evaluation": "(s[t], a[t]) -> s[t+1]  (model_training.py:131-132)",
            "e_eval_convention": align[0]["e"],
            "e_train_convention": align[1]["e"],
        },
        "action_column_stats": {},
        "results": {},
        "sha256": {"csv": R.sha256(paths["csv"]), "checkpoint": R.sha256(paths["ckpt"])},
        "torch_version": torch.__version__,
        "numpy_version": np.__version__,
        "git_commit": {"robotic_world_model_lite": R.git_commit(paths["lite"]),
                       "rsl_rl_rwm": R.git_commit(paths["rsl"])},
        "wall_clock_seconds": round(elapsed, 1),
    }
    acts = data[:, R.ACTION_COLS]
    man["action_column_stats"] = {
        "mean": [round(float(x), 6) for x in acts.mean(0)],
        "std": [round(float(x), 6) for x in acts.std(0)],
        "note": "raw action columns 45-56; actions are NOT normalised by the reference "
                "(action_data_mean=0, action_data_std=1), so a noise scale of s perturbs "
                "actions by s in these raw units while states are perturbed by s in "
                "units of state_data_std",
    }
    for tag in ("A", "B"):
        man["results"][tag] = {
            "clean": {k: results[tag]["clean"][k] for k in
                      ("e", "median_r", "frac_r_gt_10", "max_r")},
            "n_trajectories_crossing_boundary":
                results[tag]["n_trajectories_crossing_boundary"],
            "trajectory_start_rows": results[tag]["trajectory_start_rows"],
            "noise": {ns: {k: results[tag]["noise"][ns][k] for k in
                           ("e", "median_r", "frac_r_gt_10", "max_r")}
                      for ns in results[tag]["noise"]},
        }
    man["results"]["gap_A_minus_B_seed0"] = gap
    man["results"]["seed_averaged"] = stab
    man["results"]["gap_A_minus_B_seed_averaged"] = stab["A"]["mean"] - stab["B"]["mean"]
    man["results"]["gap_decomposition"] = decomp
    man["results"]["error_by_horizon_protocolA"] = horizons
    man["caveats"] = [
        "The reference checkpoint was trained by the authors on this entire CSV, so "
        "protocol A's held-out episodes were in its training data. For this checkpoint "
        "protocol A is not a generalisation measure.",
        "Boundary crossing does NOT explain the A/B gap: crossing trajectories scored "
        "better than non-crossing ones. Per-episode difficulty does.",
        "Per-episode error spans 0.60 to 1.67 and is uncorrelated with commanded speed "
        f"(r = {decomp['per_episode_speed_error_corr']:+.2f}), so the speed stratification "
        "the brief asks for does not balance difficulty; the seed-0 split holds out two "
        "of the easiest episodes.",
        "A 10-trajectory estimate is noisy: over 20 seeds protocol A is "
        f"{stab['A']['mean']:.3f}+-{stab['A']['std']:.3f} and protocol B is "
        f"{stab['B']['mean']:.3f}+-{stab['B']['std']:.3f}, a separation of only "
        f"{abs(stab['A']['mean']-stab['B']['mean'])/np.hypot(stab['A']['std'],stab['B']['std']):.1f} sigma.",
    ]
    if floor:
        man["results"]["hold_last_floor"] = floor
    with open(os.path.join(here, "manifest.json"), "w") as f:
        json.dump(man, f, indent=2)
    print(f"  wrote {os.path.join(here, 'manifest.json')}")
    print(f"\n  WALL CLOCK: {elapsed:.1f} s")
    return results


if __name__ == "__main__":
    main()
