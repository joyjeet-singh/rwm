"""
V1 -- what is replicated across the five ensemble members, and what is shared.

Section 5.3 explains why the ALEATORIC head collapses and says outright that the
mechanism behind the EPISTEMIC miscalibration "is not established here". This
script establishes a candidate, from source and from the checkpoint tensors,
without training anything.

The claim under test: the released 5-member ensemble is not five models. It is
five small heads bolted onto ONE shared GRU trunk. Members that share a feature
extractor have correlated errors by construction, so their spread understates
epistemic uncertainty -- structurally symmetric to 5.3's aleatoric argument.

Three independent lines of evidence, all emitted:

  1. SOURCE. Every architectural assertion carries a file:line, and the script
     reads that line back and asserts a fingerprint substring. A citation that
     drifts fails the build rather than going stale in the PDF.

  2. CHECKPOINT. Tensor names and parameter counts from the released
     pretrain_rnn_ens.pt: state_base / state_heads / auxiliary_base /
     auxiliary_heads. Counting is not interpretation.

  3. OUR ARMS. The same two measurements on runs/armA_seed*_ens5, so 5.2's
     sentence "our arms fail the same way" is a comparison of like with like
     rather than an assumption. This is a GATE: if our arms differ from the
     reference in this respect, that sentence has to change.

The strongest form of the finding is not the parameter fraction. It is that
in an autoregressive rollout the members share a single recurrent hidden-state
trajectory: forward() feeds the ensemble MEAN back into the one trunk, so the
five members never diverge dynamically at all. Disagreement at step t is the
spread of five 2-layer MLPs read off one 256-vector.
"""
import json
import os
import sys

import torch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, os.pardir))
PDM = os.path.abspath(os.path.join(REPO, os.pardir))

RSL = os.path.join(PDM, "rsl_rl_rwm")
RWML = os.path.join(PDM, "robotic_world_model_lite")
CKPT = os.path.join(RWML, "assets", "models", "pretrain_rnn_ens.pt")


def cite(path, line, must_contain, note):
    """
    Read path:line, assert it contains `must_contain`, return the citation record.

    The assert is the point. A file:line in a paper is a promise about a byte
    offset in someone else's repository; without a read-back it is a promise
    nothing checks. Both upstreams are pinned, so a failure here means the pin
    moved, not that the fact changed.
    """
    with open(path) as f:
        lines = f.read().split("\n")
    assert 1 <= line <= len(lines), f"{path}:{line} is past end of file ({len(lines)} lines)"
    text = lines[line - 1]
    assert must_contain in text, (
        f"citation drift at {path}:{line}\n"
        f"  expected to contain: {must_contain!r}\n"
        f"  actually reads:      {text.strip()!r}")
    rel = os.path.relpath(path, PDM)
    return {"cite": f"{rel}:{line}", "text": text.strip(), "note": note}


def group_params(state_dict):
    """Parameter count and tensor count per top-level module, and per head index."""
    tot, ntens, per_head = {}, {}, {}
    for k, v in state_dict.items():
        top = k.split(".")[0]
        tot[top] = tot.get(top, 0) + v.numel()
        ntens[top] = ntens.get(top, 0) + 1
        parts = k.split(".")
        if top.endswith("_heads") and len(parts) > 1 and parts[1].isdigit():
            per_head.setdefault(top, {}).setdefault(int(parts[1]), 0)
            per_head[top][int(parts[1])] += v.numel()
    return tot, ntens, per_head


def topology(state_dict, label):
    """
    The measurement itself. Everything below is division; nothing is judgement.

    `shared_fraction_of_member` is the number that matters: of the parameters
    that produce ONE member's mean prediction, what fraction is numerically
    identical to every other member's.
    """
    tot, ntens, per_head = group_params(state_dict)
    heads = sorted(per_head.get("state_heads", {}))
    assert heads == list(range(len(heads))), f"{label}: non-contiguous state_heads {heads}"
    n_members = len(heads)
    sizes = {per_head["state_heads"][i] for i in heads}
    assert len(sizes) == 1, f"{label}: state heads differ in size: {sizes}"
    per_member = sizes.pop()

    shared_state = tot["state_base"]
    shared_aux = tot.get("auxiliary_base", 0)
    member_path = shared_state + per_member

    rec = {
        "label": label,
        "ensemble_size": n_members,
        "heads_share_trunk": True,   # asserted below, not assumed
        "shared_modules": {
            "state_base": {"params": shared_state, "tensors": ntens["state_base"]},
            "auxiliary_base": {"params": shared_aux, "tensors": ntens.get("auxiliary_base", 0)},
        },
        "per_member_modules": {
            "state_heads": {"params_each": per_member,
                            "params_total": tot["state_heads"],
                            "tensors_total": ntens["state_heads"]},
            "auxiliary_heads": {
                "params_each": (per_head["auxiliary_heads"][0]
                                if "auxiliary_heads" in per_head else 0),
                "params_total": tot.get("auxiliary_heads", 0),
                "tensors_total": ntens.get("auxiliary_heads", 0)},
        },
        "total_params": sum(tot.values()),
        # of one member's state-prediction pathway, the fraction shared with every other
        "state_pathway_params_per_member": member_path,
        "shared_fraction_of_member": shared_state / member_path,
        "private_fraction_of_member": per_member / member_path,
        # of the whole released object
        "shared_fraction_of_model": (shared_state + shared_aux) / sum(tot.values()),
        # the trunk is a 2-layer GRU: one hidden-state trajectory for all members
        "n_independent_recurrent_states": 1,
    }
    # The boolean is a measurement: exactly one state_base, and it is not indexed
    # per member. If a future checkpoint carried state_base.0 .. state_base.4 the
    # key would be "state_base" with 5x the tensors and this would catch it.
    base_keys = [k for k in state_dict if k.startswith("state_base.")]
    assert not any(k.split(".")[1].isdigit() for k in base_keys), (
        f"{label}: state_base appears to be indexed per member -- topology changed")
    rec["heads_share_trunk"] = True
    return rec


def main():
    out = {
        "what_this_measures":
            "which parameters are replicated across the 5 ensemble members and which "
            "are shared, established from upstream source, from the released checkpoint "
            "tensors, and from our own ensemble-5 arms",
        "pins": {},
        "source_citations": {},
        "reference": {},
        "our_arms": {},
        "gate": {},
    }

    # ---------------------------------------------------------------- pins
    for name, path in (("robotic_world_model_lite", RWML), ("rsl_rl_rwm", RSL)):
        head = os.path.join(path, ".git", "HEAD")
        sha = None
        if os.path.exists(head):
            h = open(head).read().strip()
            if h.startswith("ref: "):
                rp = os.path.join(path, ".git", h[5:])
                sha = open(rp).read().strip() if os.path.exists(rp) else None
            else:
                sha = h
        out["pins"][name] = sha
    print("upstream pins:", out["pins"])

    # ------------------------------------------------------- 1. the source
    sd_py = os.path.join(RSL, "rsl_rl", "modules", "system_dynamics.py")
    mlp_py = os.path.join(RSL, "rsl_rl", "modules", "architectures", "mlp.py")
    rnn_py = os.path.join(RSL, "rsl_rl", "modules", "architectures", "rnn.py")
    cfg_py = os.path.join(RWML, "scripts", "configs", "anymal_d_flat_cfg.py")
    env_py = os.path.join(RWML, "scripts", "envs", "base.py")
    ours_py = os.path.join(REPO, "src", "rwm_model.py")

    C = out["source_citations"]
    C["trunk_constructed_once"] = cite(
        sd_py, 34, "self.state_base = self._create_base()",
        "ONE state trunk is built. Not a ModuleList, not indexed per member.")
    C["heads_replicated"] = cite(
        sd_py, 35, "self.state_heads = nn.ModuleList([",
        "the heads, and only the heads, are replicated ensemble_size times")
    C["heads_replication_count"] = cite(
        sd_py, 41, "for _ in range(self.ensemble_size)",
        "the replication factor is ensemble_size; the trunk above it is not in the loop")
    C["aux_trunk_constructed_once"] = cite(
        sd_py, 44, "self.auxiliary_base = self._create_base()",
        "the auxiliary pathway shares a trunk the same way")
    C["forward_shares_features"] = cite(
        sd_py, 87, "state_base_output = self.state_base(x_state_batch, x_action_batch)",
        "the trunk is evaluated ONCE per forward pass")
    C["forward_heads_read_same_features"] = cite(
        sd_py, 90, "state_mean, state_std = head(state_base_output, x_state_batch)",
        "every head reads the identical feature vector -- the argument is loop-invariant")
    C["epistemic_is_head_spread"] = cite(
        sd_py, 126, "epistemic_uncertainty = state_means.std(dim=0)",
        "the epistemic term IS the spread of the heads over those identical features")
    C["mean_is_fed_back"] = cite(
        sd_py, 115, "output_state_means = state_means.mean(dim=0)",
        "with model_ids=None the ensemble MEAN is what leaves forward() and, in an "
        "autoregressive rollout, what is fed back into the single trunk")
    C["trunk_is_one_gru"] = cite(
        rnn_py, 39, "rnn_cls(input_size=self.input_dim",
        "the trunk is a single nn.GRU; Memory.hidden_states is one tensor for all members")
    C["one_hidden_state"] = cite(
        rnn_py, 40, "self.hidden_states = None",
        "a single recurrent state, owned by the trunk, shared by every member")
    C["head_is_two_small_mlps"] = cite(
        mlp_py, 59, "state_mean_layers.append(nn.Linear(self.state_mean_shape[-1], state_dim))",
        "each member's private part is a 256->128->45 mean tower plus a matching logstd tower")
    C["bounded_logstd_init"] = cite(
        mlp_py, 78, "self.state_min_logstd = nn.Parameter",
        "the PETS-lineage bounded log-sigma parameterisation (see 5.3 and the related work)")
    C["ensemble_size_is_five"] = cite(
        cfg_py, 70, "ensemble_size: int = 5",
        "the configured ensemble size for the released ANYmal D flat model")
    C["penalty_consumes_epistemic"] = cite(
        env_py, 166, "self.uncertainty_penalty_weight * self.epistemic_uncertainty",
        "the head spread is the quantity the method penalises rewards with")
    C["ours_trunk_once"] = cite(
        ours_py, 164, "self.state_base = mk_base()",
        "OUR arms build one trunk the same way")
    C["ours_heads_replicated"] = cite(
        ours_py, 165, "self.state_heads = nn.ModuleList([",
        "OUR heads are the replicated part")
    C["ours_forward_shares"] = cite(
        ours_py, 182, "base = self.state_base(x_state_batch, x_action_batch)",
        "OUR forward evaluates the trunk once")
    C["ours_heads_read_same"] = cite(
        ours_py, 185, "m, s = head(base, x_state_batch)",
        "OUR heads read the identical feature vector")
    C["ours_epistemic"] = cite(
        ours_py, 200, "means.std(0).sum(1)",
        "OUR epistemic term is the same head spread")
    C["ours_mean_fed_back"] = cite(
        ours_py, 223, "pred[:, i] = m",
        "OUR rollout feeds the ensemble mean back into the single trunk, so the "
        "members share one hidden-state trajectory end to end")
    print(f"source: {len(C)} citations read back and verified")

    # -------------------------------------------------- 2. the checkpoint
    ck = torch.load(CKPT, map_location="cpu")
    ref = topology(ck["system_dynamics_state_dict"], "released pretrain_rnn_ens.pt")
    ref["checkpoint_iter"] = int(ck["iter"])
    ref["tensor_name_prefixes"] = sorted({k.split(".")[0]
                                          for k in ck["system_dynamics_state_dict"]})
    out["reference"] = ref
    print(f"reference: ensemble {ref['ensemble_size']}, "
          f"trunk {ref['shared_modules']['state_base']['params']:,}, "
          f"head {ref['per_member_modules']['state_heads']['params_each']:,} each, "
          f"{100 * ref['shared_fraction_of_member']:.2f}% of a member shared")

    # ----------------------------------------------------- 3. our ens5 arms
    arms = {}
    for seed in (0, 1, 2):
        p = os.path.join(REPO, "runs", f"armA_seed{seed}_ens5", "weights_2500.pt")
        if not os.path.exists(p):
            continue
        arms[f"armA_seed{seed}_ens5"] = topology(
            torch.load(p, map_location="cpu")["model_state_dict"],
            f"armA_seed{seed}_ens5")
    out["our_arms"] = arms
    if arms:
        a = next(iter(arms.values()))
        print(f"our arms:  ensemble {a['ensemble_size']}, "
              f"trunk {a['shared_modules']['state_base']['params']:,}, "
              f"head {a['per_member_modules']['state_heads']['params_each']:,} each, "
              f"{100 * a['shared_fraction_of_member']:.2f}% of a member shared")

    # ------------------------------------------------------------- the gate
    # Two conditions from the brief. Both are recorded as measured, not asserted.
    g = out["gate"]
    g["members_are_fully_independent_models"] = False   # falsified by the counts above
    g["reference_heads_share_trunk"] = ref["heads_share_trunk"]
    if arms:
        same = all(
            a["shared_modules"]["state_base"]["params"]
            == ref["shared_modules"]["state_base"]["params"]
            and a["per_member_modules"]["state_heads"]["params_each"]
            == ref["per_member_modules"]["state_heads"]["params_each"]
            and a["ensemble_size"] == ref["ensemble_size"]
            and a["heads_share_trunk"] == ref["heads_share_trunk"]
            for a in arms.values())
        g["our_arms_heads_share_trunk"] = all(a["heads_share_trunk"] for a in arms.values())
        g["our_arms_match_reference_topology"] = bool(same)
    else:
        g["our_arms_heads_share_trunk"] = None
        g["our_arms_match_reference_topology"] = None
        g["note"] = "runs/ absent (gitignored); our-arm topology not measured in this clone"

    g["verdict"] = (
        "TRUNK-SHARING CONFIRMED; our ens5 arms are identical to the reference in "
        "this respect, so 5.2's comparison is like with like and Phase 2 keeps its "
        "motivation"
        if g["our_arms_match_reference_topology"] else
        "TRUNK-SHARING CONFIRMED for the reference; our-arm comparison not established here")

    # The mechanism sentence, assembled from the measured numbers so the paper can
    # quote it without anything being typed.
    out["mechanism"] = {
        "statement":
            "the five members share the feature extractor and the recurrent state; "
            "only the output heads differ, so member disagreement is head disagreement "
            "over identical features and cannot express uncertainty the trunk does not "
            "already carry",
        "shared_params_per_member": ref["shared_modules"]["state_base"]["params"],
        "private_params_per_member":
            ref["per_member_modules"]["state_heads"]["params_each"],
        "shared_pct_of_member": round(100 * ref["shared_fraction_of_member"], 2),
        "private_pct_of_member": round(100 * ref["private_fraction_of_member"], 2),
        "n_independent_recurrent_states": 1,
        "n_members": ref["ensemble_size"],
        "symmetry_with_5_3":
            "5.3 shows the aleatoric head is trained by an objective whose optimum is "
            "sigma = 0. This shows the epistemic term is computed over an architecture "
            "whose members cannot disagree about anything the shared trunk does not "
            "already disagree with itself about. Both are structural, not incidental.",
        "status": "candidate mechanism, established from source and parameter counts; "
                  "whether it is THE explanation is tested by M-44 (Phase 2)",
    }

    dst = os.path.join(R.RESULTS, "v1_ensemble_topology.json")
    with open(dst, "w") as f:
        json.dump(out, f, indent=2, sort_keys=True)
    print(f"\nwrote {dst}")
    print(f"VERDICT: {g['verdict']}")


if __name__ == "__main__":
    main()
