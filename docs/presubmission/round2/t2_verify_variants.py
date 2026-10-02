"""T2, rule X1 Part C: verify the two training variants before any of them trains (round2 PLAN §1.2.5).
(1) the existing Table S7 RSSMs are untouched by the code change: their checkpoints load strictly and
    reproduce results/baselines_eval.json exactly; (2) LNGRUCell equals an independent NumPy transcription of
    danijar/dreamerv2 common/nets.py:334-347 (07d906e9) on random inputs; (3) V1's unbalanced KL equals the plain
    KL value and passes gradient to both prior and posterior, where the balanced form's value is the same;
    (4) both variants build, and a training step's losses are finite. Writes nothing. Run from the repo root."""
import json, os, sys
sys.path.insert(0, "src"); sys.path.insert(0, "scripts")
import numpy as np, torch
import baselines as BL, mn_sweep_eval as MN, rollout_eval as E, rwm_data as R, rwm_metrics as MET
from baselines.rssm import LNGRUCell

ok = {}
paths = R.repo_paths(); cfg = R.load_reference_config(paths["lite"])
data, ep = R.load_data(paths["csv"], verbose=False)
split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"), verbose=False)
scale = MET.training_scale(data, ep, split["train_episodes"], cfg["state_data_mean"], cfg["state_data_std"])
starts = MN.arena(ep, split["holdout_episodes"], 32)["starts"]
ev = json.load(open("results/baselines_eval.json"))
d1 = 0.0
for regime in ("tf", "ar"):
    for s in (0, 1, 2):
        m = BL.build("rssm", "s7", cfg)
        m.load_state_dict(torch.load(f"runs/baseline_rssm_{regime}_s7_seed{s}/weights_2500.pt", map_location="cpu")["model_state_dict"], strict=True)
        m.eval()
        sc = MN.score(m, data, cfg, scale, starts, 32, 32)
        for h, v in sc.items():
            d1 = max(d1, max(abs(a - b) for a, b in zip(v["l1"], ev["configs"][f"rssm_{regime}_s7"]["seeds"][str(s)]["held_out"][h]["l1"])))
ok["1_existing_rssm_unchanged"] = d1 == 0.0

torch.manual_seed(0)
cell = LNGRUCell(7, 5).double()
with torch.no_grad():
    cell.norm.weight.uniform_(0.5, 1.5); cell.norm.bias.uniform_(-0.2, 0.2)
x, h = torch.randn(3, 7, dtype=torch.float64), torch.randn(3, 5, dtype=torch.float64)
W, b = cell.layer.weight.detach().numpy(), cell.layer.bias.detach().numpy()
g, be = cell.norm.weight.detach().numpy(), cell.norm.bias.detach().numpy()
def dreamer(x, h):                                       # nets.py:336-346, in NumPy
    parts = np.concatenate([x, h], -1) @ W.T + b         # tfkl.Dense(3 * size, use_bias=True)
    mu = parts.mean(-1, keepdims=True); var = parts.var(-1, keepdims=True)
    parts = (parts - mu) / np.sqrt(var + 1e-3) * g + be  # tfkl.LayerNormalization(), epsilon 1e-3
    reset, cand, update = np.split(parts, 3, -1)
    reset = 1 / (1 + np.exp(-reset))
    cand = np.tanh(reset * cand)
    update = 1 / (1 + np.exp(-(update - 1)))
    return update * cand + (1 - update) * h
d2 = float(np.abs(cell(x, h).detach().numpy() - dreamer(x.numpy(), h.numpy())).max())
ok["2_lngru_matches_dreamerv2"] = d2 < 1e-12

v1 = BL.build("rssm", "x1v1", cfg); s7 = BL.build("rssm", "s7", cfg)
post = torch.randn(4, 64, 32, requires_grad=True); prior = torch.randn(4, 64, 32, requires_grad=True)
def plain(lp, lq):
    p = torch.softmax(lp, -1); return (p * (torch.log_softmax(lp, -1) - torch.log_softmax(lq, -1))).sum((-1, -2))
k1 = v1._kl(post, prior)                      # free nats 3: clamp at 3
ref = torch.clamp(plain(post, prior), min=3.0)
gp, gq = torch.autograd.grad(k1.sum(), [post, prior])
ok["3_v1_kl_plain_value"] = torch.allclose(k1, ref) and v1.kl_balance is None and v1.free_nats == 3.0 and v1.kl_scale == 1.0
ok["3_v1_kl_gradient_both_sides"] = bool(gp.abs().sum() > 0 and gq.abs().sum() > 0)
ok["3_balanced_value_equals_plain"] = torch.allclose(s7._kl(post, prior), plain(post, prior))

for spec in ("x1v1", "x1v2"):
    torch.manual_seed(0)
    m = BL.build("rssm", spec, cfg)
    stb = torch.randn(8, 40, 45) * 0.1; acb = torch.randn(8, 40, 12) * 0.1
    losses = m.compute_state_loss(stb, acb, "tf")
    ok[f"4_{spec}_builds_and_losses_finite"] = all(torch.isfinite(l).item() for l in losses)
    print(f"  {spec}: {BL.n_params(m):,} parameters (s7 {BL.n_params(s7):,}); spec {m.spec}")
print("  checks:", {k: bool(v) for k, v in ok.items()}, f"| d1 {d1:.1e}  d2 {d2:.1e}")
sys.exit(0 if all(ok.values()) else 1)
