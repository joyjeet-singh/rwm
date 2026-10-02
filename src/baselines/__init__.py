"""
The architecture baselines of rules M-75 and M-76 (FINDINGS_LEDGER.md), and the one place
that builds them. docs/presubmission/BASELINE_SPECS.md records every choice with its source.

  build(arch, spec, cfg)   arch in {"mlp", "transformer", "rssm"};
                           spec "s7"      = the original's Table S7 sizes (governing);
                           spec "matched" = PLAN S2b as written, parameter-matched to RWM's
                                            ensemble-1 state pathway within +-5% (reported
                                            alongside only, and only if the cap allows).
"""
from baselines.common import n_params
from baselines.mlp import MLPBaseline
from baselines.rssm import RSSMBaseline
from baselines.transformer import TransformerBaseline

HISTORY = 32                 # "the same context" as RWM (ORIGINAL_SPECS b.5)
RWM_STATE_PATHWAY = 714164   # results/p2_capacity_power.json's method, recomputed in the ladder

# The parameter-matched sizes, found by scripts/baseline_verification.py's search and
# asserted there to land within +-5% of RWM_STATE_PATHWAY.
MATCHED = {"mlp": {"width": 295}, "transformer": {"d_model": 160}, "rssm": {"width": 256}}


def build(arch, spec, cfg):
    if arch == "mlp":
        w = 256 if spec == "s7" else MATCHED["mlp"]["width"]
        return MLPBaseline(HISTORY, cfg, base_shape=(w, w))
    if arch == "transformer":
        if spec == "s7":
            return TransformerBaseline(HISTORY, cfg, d_model=64, n_heads=8, n_layers=2,
                                       positions="sinusoidal")
        return TransformerBaseline(HISTORY, cfg, d_model=MATCHED["transformer"]["d_model"],
                                   n_heads=8, n_layers=2, positions="learned")
    if arch == "rssm":
        if spec == "s7":
            return RSSMBaseline(HISTORY, cfg, latent="categorical", deter=256, hidden=256,
                                gru_layers=2, n_vars=64, n_classes=32, act="elu",
                                kl_balance=0.8, free_nats=0.0, kl_scale=0.1)
        if spec in ("x1v1", "x1v2"):
            # rule X1's Part C (ledger M-80): the Table S7 RSSM with one setting changed.
            # V1, PlaNet's KL settings: weight 1.0, 3 free nats, no balancing (BASELINE_SPECS row 36).
            # V2, DreamerV2's layer-normalised GRU (BASELINE_SPECS row 22).
            kw = dict(latent="categorical", deter=256, hidden=256, gru_layers=2, n_vars=64, n_classes=32,
                      act="elu", kl_balance=0.8, free_nats=0.0, kl_scale=0.1)
            kw.update(dict(kl_balance=None, free_nats=3.0, kl_scale=1.0) if spec == "x1v1" else dict(gru_norm=True))
            return RSSMBaseline(HISTORY, cfg, **kw)
        w = MATCHED["rssm"]["width"]
        return RSSMBaseline(HISTORY, cfg, latent="gaussian", deter=w, hidden=w, gru_layers=1,
                            stoch=30, act="relu", kl_balance=None, free_nats=3.0,
                            kl_scale=1.0, min_std=0.1)
    raise ValueError(arch)


__all__ = ["build", "n_params", "HISTORY", "RWM_STATE_PATHWAY", "MATCHED",
           "MLPBaseline", "TransformerBaseline", "RSSMBaseline"]
