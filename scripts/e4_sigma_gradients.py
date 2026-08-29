"""
E4 -- all seven loss terms, and what each does to sigma. Measured, not asserted.

WHY. §6.3's derivation addresses two of the seven configured loss terms: the state
term, whose optimum is sigma = 0, and the bound term. Its completeness rests on the
other five being inert with respect to sigma, and the reader has to take that on
trust. It is a load-bearing assumption -- if any of the other five pushed sigma up,
the collapse would have a competing explanation -- and it is cheap to measure.

WHAT IS MEASURED. Each of the seven terms is computed on its own on one real batch
from the released CSV, with the released architecture and the released weights
config, and back-propagated ALONE. For each we record:

  live        whether the term is identically zero under the released configuration
  weight      its configured weight in the total
  dL/dsigma   the gradient norm reaching the log-sigma tower's parameters
  dL/ddelta   the gradient on state_log_delta_logstd, the parameter that sets the
              width of the bounded interval sigma lives in
  dL/dmin     the gradient on state_min_logstd, the interval's floor
  file:line   where the term is computed in the reference

A term that is inert with respect to sigma produces exactly zero on all three. That
is a stronger statement than "we read the code and think it does not matter", and it
is what §6.3 needs.

Writes results/e4_sigma_gradients.json.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import torch  # noqa: E402
import rwm_data as R  # noqa: E402
import rwm_model as MDL  # noqa: E402
import rwm_train as T  # noqa: E402
import rollout_eval as E  # noqa: E402

OUT = "e4_sigma_gradients.json"

# Where the reference computes each term. Paths as LOSS_ASSEMBLY.md fixes them.
WHERE = {
    "state":       ("system_dynamics.py:270-289", "squared error on a reparameterised SAMPLE"),
    "sequence":    ("system_dynamics.py:274-277", "guarded by prediction_type == 'sequence'"),
    "bound":       ("system_dynamics.py:301-302", "mean(max_logstd) - mean(min_logstd)"),
    "kl":          ("system_dynamics.py:223", "rssm branch only"),
    "extension":   ("system_dynamics.py:233-268", "auxiliary head, extension_dim = 0"),
    "contact":     ("system_dynamics.py:233-268", "auxiliary head, contact_dim = 8"),
    "termination": ("system_dynamics.py:233-268", "auxiliary head, termination_dim = 1"),
}


def main():
    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    data, episode_id = R.load_data(paths["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"),
                         verbose=False)
    ds = T.WindowDataset(data, episode_id, split["train_episodes"], cfg)
    torch.manual_seed(0)
    model = MDL.build_from_config(cfg, ensemble_size=5)
    gen = torch.Generator().manual_seed(0)
    state, action, ext, contact, term = ds.sample(64, gen)

    head = model.state_heads[0]
    logstd_params = list(head.state_logstd_layers.parameters())
    W = cfg["loss_weights"]

    def terms_for():
        """Every term, computed the way the training step computes them.

        model.compute_loss is the assembly the reference uses and the one Step 5
        trains through; taking the terms from it rather than re-deriving them here
        is what makes this a measurement of the real objective rather than of a
        reconstruction of it.
        """
        model.reset()
        vals = model.compute_loss(state, action, ext, contact, term,
                                  teacher_forcing=False, loss_type="mse")
        return dict(zip(MDL.TOTAL_WEIGHT_KEYS, vals))

    rows = []
    for name in MDL.TOTAL_WEIGHT_KEYS:
        model.zero_grad(set_to_none=True)
        torch.manual_seed(7)
        val = terms_for()[name]
        live = bool(torch.is_tensor(val) and val.requires_grad and float(val) != 0.0) \
            or (torch.is_tensor(val) and val.requires_grad)
        gsig = gdelta = gmin = 0.0
        if torch.is_tensor(val) and val.requires_grad:
            val.backward(retain_graph=False)
            gsig = float(sum((p.grad ** 2).sum() for p in logstd_params
                             if p.grad is not None) ** 0.5)
            gdelta = float(head.state_log_delta_logstd.grad.abs().sum()
                           if head.state_log_delta_logstd.grad is not None else 0.0)
            gmin = float(head.state_min_logstd.grad.abs().sum()
                         if head.state_min_logstd.grad is not None else 0.0)
        where, note = WHERE[name]
        rows.append({
            "term": name,
            "value": float(val) if torch.is_tensor(val) else float(val),
            "identically_zero": bool(float(val) == 0.0),
            "differentiable": bool(torch.is_tensor(val) and val.requires_grad),
            "weight": W[name],
            "grad_logstd_tower_norm": gsig,
            "grad_log_delta_logstd_abs": gdelta,
            "grad_min_logstd_abs": gmin,
            "touches_sigma": bool(gsig > 0 or gdelta > 0 or gmin > 0),
            "where": where, "note": note,
        })

    live = [r for r in rows if not r["identically_zero"]]
    touch = [r for r in rows if r["touches_sigma"]]

    print("E4 — WHAT EACH LOSS TERM DOES TO SIGMA")
    print("=" * 104)
    print(f"  {'term':<12} {'weight':>7} {'value':>12} {'dL/dsigma':>12} "
          f"{'dL/ddelta':>12} {'dL/dmin':>10}  touches sigma")
    for r in rows:
        print(f"  {r['term']:<12} {r['weight']:>7.2f} {r['value']:>12.5g} "
              f"{r['grad_logstd_tower_norm']:>12.4g} {r['grad_log_delta_logstd_abs']:>12.4g} "
              f"{r['grad_min_logstd_abs']:>10.4g}  "
              f"{'YES' if r['touches_sigma'] else 'no'}")
    print("=" * 104)
    print(f"  {len(live)} of {len(rows)} terms are live under the released configuration")
    print(f"  {len(touch)} of {len(rows)} carry any gradient to sigma: "
          f"{', '.join(r['term'] for r in touch)}")
    print(f"  the other {len(rows) - len(touch)} are inert with respect to sigma, "
          f"measured rather than argued")

    json.dump({"n_terms": len(rows), "n_live": len(live), "n_touching_sigma": len(touch),
               "touching": [r["term"] for r in touch],
               "batch_size": int(state.shape[0]),
               "terms": rows}, open(os.path.join(R.RESULTS, OUT), "w"), indent=2)
    print(f"  wrote results/{OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
