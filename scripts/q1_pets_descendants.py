"""
Q1 -- how far does the sigma = 0 optimum reach? A survey of public descendants.

WHY. §6.3 derives the aleatoric collapse from an objective, not from a bug: the bounded
log-sigma head is inherited line-for-line from PETS (Chua et al., NeurIPS 2018), and what
this codebase changed is the LOSS -- squared error on a reparameterised sample where PETS
used a likelihood. §2 states, explicitly as an UNTESTED hypothesis, that any descendant
which made the same substitution inherits the same optimum. A referee asked for a count.

WHAT THIS IS AND IS NOT. It is a count over repositories EXAMINED under a protocol fixed
before the search, recorded at /Users/Shared/rwm_verify/evidence/A2/protocol.md. It is not
a census, not a sample of a defined population, and supports no claim about what fraction
of the field does anything. Search engines rank and truncate; what was found is a sample
of convenience and the protocol says so.

THE INCLUSION TEST, BOTH PARTS REQUIRED.
  (a) the repository carries the double-softplus bounded log-sigma construction:
        logvar = max_logvar - softplus(max_logvar - logvar)
        logvar = min_logvar + softplus(logvar - min_logvar)
      in either log-variance or log-standard-deviation form; and
  (b) it trains that head against a squared error on a SAMPLED prediction -- a
      reparameterised draw mu + sigma*eps scored by MSE or L2 -- rather than against a
      likelihood.

Part (b) is the one that matters and the one that takes reading. A repository carrying the
construction with a proper Gaussian NLL does NOT inherit the optimum, because the log-sigma
term opposes sigma -> 0; it is recorded as DOES NOT INHERIT and is NOT dropped.

A NOTE ON WHAT MSE-ON-THE-MEAN IS NOT. Several repositories offer an `inc_var_loss=False`
or `deterministic=True` path that scores MSE against the predicted MEAN. That is a
different thing and does not satisfy (b): squaring the mean's error gives sigma no gradient
at all, so sigma is untrained rather than driven to zero, and in the deterministic branches
surveyed here the bounded construction is not even applied. Only a squared error on a DRAW
carries the optimum §6.3 derives.

HOW TO RE-RUN. The verdicts are readings of source and no script can re-derive them. What a
script can do is check that every citation still says what it was recorded as saying, which
is what --verify does: it re-fetches each cited file AT ITS CITED COMMIT and confirms the
recorded line still contains the recorded text. A citation that has drifted is reported and
the run fails. The default path writes the artifact from the stored record without touching
the network, and carries the last --verify run's record (RECORDED_VERIFICATION) only while the
citations are exactly the ones it covered. reproduce.sh runs the default path (stage 20s1).

    python scripts/q1_pets_descendants.py            write the artifact
    python scripts/q1_pets_descendants.py --verify   re-fetch every citation and check it

Writes results/q1_pets_descendants.json.
"""
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402

SEARCH_DATE = "2026-09-20"
PROTOCOL = "/Users/Shared/rwm_verify/evidence/A2/protocol.md"
PROTOCOL_SHA256 = "44c654ff2ef16acc6e91a83f6b9b898ff5ca48dd114d3f87e6a9a2367459975c"
RAW = "https://raw.githubusercontent.com/{repo}/{commit}/{path}"

# The subject of this paper, recorded separately and NEVER counted as reach: it is the
# thing §6.3 measured, so counting it as evidence that the result travels would be circular.
SUBJECT = {
    "repo": "leggedrobotics/rsl_rl_rwm (the fork this paper pins)",
    "commit": "18eebcdd7145284c8d5eed5d8ed1a4b96c649693",
    "construction": "rsl_rl/modules/architectures/mlp.py:92-93",
    "loss": "rsl_rl/modules/system_dynamics.py:283",
    "verdict": "INHERITS",
    "note": "The subject of this reproduction, not a survey result. Listed so the reader "
            "can see the reference case the inclusion test was written against.",
}

# Every repository examined. A repository where the construction is absent is NOT examined
# for this count -- the question is about descendants of this construction -- but the ones
# looked at and excluded are recorded below under `construction_absent` so the reader can
# see what was rejected and why.
EXAMINED = [
    {
        "repo": "kchua/handful-of-trials",
        "url": "https://github.com/kchua/handful-of-trials",
        "commit": "77fd8802cc30b7683f0227c90527b5414c0df34c",
        "what": "PETS, the original. TensorFlow.",
        "construction": {"path": "dmbrl/modeling/models/BNN.py", "line": 414,
                         "expect": "max_logvar - tf.nn.softplus"},
        "loss": {"path": "dmbrl/modeling/models/BNN.py", "line": 440,
                 "expect": "tf.square(mean - targets) * inv_var"},
        "verdict": "DOES NOT INHERIT",
        "why": "_compile_losses with inc_var_loss=True (its default) is the Gaussian NLL: "
               "squared error weighted by inv_var plus a var_losses term. The log-sigma term "
               "is present and opposes sigma -> 0. The inc_var_loss=False branch is MSE on "
               "the MEAN and is compiled as the held-out metric, not the training objective.",
    },
    {
        "repo": "quanvuong/handful-of-trials-pytorch",
        "url": "https://github.com/quanvuong/handful-of-trials-pytorch",
        "commit": "672d32f9fadf52862e7c6ee73a45f31e89d7d5ba",
        "what": "Unofficial PyTorch port of PETS.",
        "construction": {"path": "config/halfcheetah.py", "line": 86,
                         "expect": "max_logvar - F.softplus"},
        "loss": {"path": "MPC.py", "line": 237,
                 "expect": "inv_var + logvar"},
        "verdict": "DOES NOT INHERIT",
        "why": "train_losses = ((mean - targ) ** 2) * inv_var + logvar, the Gaussian NLL "
               "written out. The sampling at MPC.py:380 is rollout prediction, not the "
               "training loss.",
    },
    {
        "repo": "Xingyu-Lin/mbpo_pytorch",
        "url": "https://github.com/Xingyu-Lin/mbpo_pytorch",
        "commit": "fe3c78c474d188c16a026051b92f8a2e84fa9387",
        "what": "PyTorch replication of MBPO.",
        "construction": {"path": "model.py", "line": 142,
                         "expect": "max_logvar - F.softplus"},
        "loss": {"path": "model.py", "line": 168,
                 "expect": "torch.pow(mean - labels, 2) * inv_var"},
        "verdict": "DOES NOT INHERIT",
        "why": "loss(..., inc_var_loss=True) by default: inverse-variance-weighted squared "
               "error plus a var_loss term, the Gaussian NLL. The inc_var_loss=False branch "
               "is MSE on the mean and is used for the holdout score.",
    },
    {
        "repo": "facebookresearch/mbrl-lib",
        "url": "https://github.com/facebookresearch/mbrl-lib",
        "commit": "3f93cccfc8d635f74e335a2f07aab6e9a48fc021",
        "what": "Facebook Research's model-based RL library; ships PETS, MBPO, PlaNet.",
        "construction": {"path": "mbrl/models/gaussian_mlp.py", "line": 152,
                         "expect": "max_logvar - F.softplus"},
        "loss": {"path": "mbrl/models/gaussian_mlp.py", "line": 300,
                 "expect": "gaussian_nll"},
        "verdict": "DOES NOT INHERIT",
        "why": "loss() dispatches to _nll_loss, which calls mbrl.util.math.gaussian_nll and "
               "adds the PETS bound regulariser. The alternative _mse_loss branch runs only "
               "when deterministic=True, and in that mode forward() returns before the "
               "construction is applied and predicts no logvar at all -- so the bounded head "
               "is never trained against a squared error here, on either branch.",
    },
    {
        "repo": "nirbhayjm/va_mbpo",
        "url": "https://github.com/nirbhayjm/va_mbpo",
        "commit": "203ea3e5bdbcc153bd38f0ec18b2085d36089fed",
        "what": "Value-aware model learning with MBPO; a fork of mbrl-lib that adds a "
                "value-aware loss.",
        "construction": {"path": "mbrl/models/gaussian_mlp.py", "line": 158,
                         "expect": "max_logvar - F.softplus"},
        "loss": {"path": "mbrl/models/gaussian_mlp.py", "line": 340,
                 "expect": "rsample()"},
        "verdict": "INHERITS",
        "why": "The one in this survey that makes the substitution. With deterministic=False "
               "-- the branch in which the bounded construction IS applied -- and "
               "model_loss_type='va', _va_loss builds Normal(mean, exp(0.5*logvar)) from the "
               "bounded head, draws a REPARAMETERISED sample with rsample(), and scores it "
               "with F.mse_loss on the reward dimension and a squared model-advantage through "
               "the critic on the state dimensions. There is no log-sigma term anywhere in "
               "that objective. That is the construction §6.3 shows has its optimum at "
               "sigma = 0.",
        "qualification": "It inherits IN ITS VALUE-AWARE MODE, which is an option and not the "
                         "default: model_loss_type defaults to 'mle' throughout, and the "
                         "value is threaded from cfg.overrides.model_loss_type in "
                         "mbrl/algorithms/mbpo.py. Under 'mle' the same file uses the "
                         "Gaussian NLL and does not inherit. The count below states this "
                         "rather than rounding it to a plain yes.",
    },
    {
        "repo": "Shylock-H/COMBO_Offline_RL",
        "url": "https://github.com/Shylock-H/COMBO_Offline_RL",
        "commit": "239cce768bbc2ffd1c978e91efc3cbb4abb7c149",
        "what": "PyTorch implementation of COMBO.",
        "construction": {"path": "dynamic/ensemble_dynamics.py", "line": 139,
                         "expect": "max_logvar - F.softplus"},
        "loss": {"path": "dynamic/transition_model.py", "line": 103,
                 "expect": "train_mse_loss + train_var_loss"},
        "verdict": "DOES NOT INHERIT",
        "why": "train_transition_loss = train_mse_loss + train_var_loss, with inc_var_loss "
               "defaulting to True: the Gaussian NLL. Its vendored TensorFlow BNN is PETS's "
               "and behaves the same way.",
    },
    {
        "repo": "yihaosun1124/pytorch-mopo",
        "url": "https://github.com/yihaosun1124/pytorch-mopo",
        "commit": "33a81aae8b221de01007e7b27a8a02ee19c27eb3",
        "what": "PyTorch re-implementation of MOPO.",
        "construction": {"path": "models/tf_dynamics_models/bnn.py", "line": 647,
                         "expect": "max_logvar - tf.nn.softplus"},
        "loss": {"path": "models/tf_dynamics_models/bnn.py", "line": 688,
                 "expect": "tf.square(mean - targets) * inv_var"},
        "verdict": "DOES NOT INHERIT",
        "why": "The probabilistic branch compiles _compile_losses with inc_var_loss=True — "
               "the Gaussian NLL, plus the PETS bound regulariser. The inc_var_loss=False "
               "compilation four lines later is the training loss of the DETERMINISTIC "
               "branch and scores MSE against the predicted MEAN, which does not satisfy "
               "part (b); the held-out mse_loss is compiled separately two lines after "
               "that.",
    },
    {
        "repo": "junming-yang/mopo",
        "url": "https://github.com/junming-yang/mopo",
        "commit": "2c9431e44b84472006319aa12951f17f837c4fd9",
        "what": "MOPO re-implemented in PyTorch.",
        "construction": {"path": "models/ensemble_dynamics.py", "line": 138,
                         "expect": "max_logvar - F.softplus"},
        "loss": {"path": "models/transition_model.py", "line": 123,
                 "expect": "torch.pow(pred_means - groundtruths, 2) * inv_var"},
        "verdict": "DOES NOT INHERIT",
        "why": "inv_var-weighted squared error plus var_losses over pred_logvars: the "
               "Gaussian NLL.",
    },
    {
        "repo": "yihaosun1124/OfflineRL-Kit",
        "url": "https://github.com/yihaosun1124/OfflineRL-Kit",
        "commit": "3962aa8709887695a136349a3a86ab7242740668",
        "what": "Offline RL library; ships MOPO, COMBO, RAMBO and others.",
        "construction": {"path": "offlinerlkit/modules/dynamics_module.py", "line": 25,
                         "expect": "softplus"},
        "loss": {"path": "offlinerlkit/dynamics/ensemble_dynamics.py", "line": 192,
                 "expect": "torch.pow(mean - targets_batch, 2) * inv_var"},
        "verdict": "DOES NOT INHERIT",
        "why": "loss = mse_loss_inv.sum() + var_loss.sum(), with mse_loss_inv weighted by "
               "inv_var: the Gaussian NLL.",
    },
    {
        "repo": "polixir/OfflineRL",
        "url": "https://github.com/polixir/OfflineRL",
        "commit": "ea1a446b210d3782e61e559b68306b15b349e9ef",
        "what": "A collection of offline RL algorithms: MOPO, COMBO, BREMEN, MAPLE, RAMBO.",
        "construction": {"path": "offlinerl/outside_utils/modules/dynamics_module.py",
                         "line": 25, "expect": "softplus"},
        "loss": {"path": "offlinerl/algo/modelbase/model_base.py", "line": 325,
                 "expect": "torch.pow(mean - targets_batch, 2) * inv_var"},
        "verdict": "DOES NOT INHERIT",
        "why": "dynamics_learn takes a logvar_loss_coef and forms "
               "mse_loss_inv.sum() + var_loss.sum(): the Gaussian NLL. Its other model-based "
               "algorithms train the dynamics with -dist.log_prob(...), also a likelihood.",
    },
]

# Looked at and excluded because the construction is absent. Recorded so the reader can see
# what was rejected rather than having to trust a bare denominator.
CONSTRUCTION_ABSENT = [
    {"repo": "johannesnauta/pytorch-pne",
     "commit": "c3eacc0b017846e092bc75325041ff1b541bb142",
     "why": "Uses softplus to make a variance positive (models/pnn.py), not the "
            "double-softplus clamp between two LEARNABLE bounds. Different construction."},
    {"repo": "leggedrobotics/robotic_world_model",
     "commit": "14dbfe9da3f2246448cccee2873b9817603d5ae5",
     "why": "The Isaac Lab extension of the paper under reproduction. No softplus appears in "
            "any of its 44 Python files: the dynamics head lives in its rsl_rl dependency, "
            "not in this repository. Relevant to referee Q4 as well, and consistent with "
            "what block A1 found there."},
    {"repo": "leggedrobotics/rsl_rl",
     "commit": "857de6165c5fd479726ec8ac5c9303a497766f30",
     "why": "Mainline rsl_rl. Its only softplus use is a Beta policy distribution in "
            "rsl_rl/modules/distribution.py. The bounded log-sigma dynamics head exists in "
            "the rwm FORK this paper pins, not in the mainline library -- which narrows the "
            "construction's reach rather than widening it."},
]


def _fetch(repo, commit, path):
    url = RAW.format(repo=repo, commit=commit, path=path)
    req = urllib.request.Request(url, headers={"User-Agent": "rwm-repro-q1-survey"})
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read().decode("utf-8", "replace").split("\n")


CITATIONS_PER_REPO = 2  # the construction and the loss

# The record of the last run that re-fetched every citation (--verify). The network is
# not available to a clean clone, and reproduce.sh must not need it, so the plain path
# CARRIES this record -- the same arrangement as T1's bibliography (stage 20p). It carries
# it only for the citations that run covered: their fingerprint is pinned here, and if any
# repository, commit, file or line changes, the plain path refuses and --verify must be
# re-run and this record updated. The plain path never claims a check it did not make:
# it prints that the record is carried, and from which date.
RECORDED_VERIFICATION = {
    "verified_on": "2026-09-20",
    "citations_sha256": "c7d7253fedceba000a0091e5df9e861d7b214b5d99dfd63b8e31af0b1cdf5429",
    "citations_still_valid": True,
}


def citations_fingerprint():
    """sha256 over every citation the verification covers, in survey order."""
    cites = [(e["repo"], e["commit"], e["construction"], e["loss"]) for e in EXAMINED]
    return hashlib.sha256(json.dumps(cites, sort_keys=True).encode()).hexdigest()


def verify():
    """Re-fetch every citation at its cited commit and confirm it still says what we recorded."""
    bad, checked = [], 0
    for e in EXAMINED:
        for which in ("construction", "loss"):
            c = e[which]
            checked += 1
            try:
                lines = _fetch(e["repo"], e["commit"], c["path"])
            except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
                bad.append(f"{e['repo']} {which}: fetch failed, {exc}")
                continue
            # Accept the cited line or its immediate neighbours: a citation is to a
            # construct, and a one-line drift is a citation to fix, not a finding to lose.
            window = lines[max(0, c["line"] - 3): c["line"] + 2]
            if not any(c["expect"] in ln for ln in window):
                bad.append(f"{e['repo']} {which}: {c['path']}:{c['line']} no longer contains "
                           f"{c['expect']!r}")
    print(f"  citations checked: {checked}")
    if bad:
        print(f"  DRIFTED: {len(bad)}")
        for b in bad:
            print(f"    !! {b}")
        return False
    print("  every citation still says what it was recorded as saying")
    return True


def main():
    if "--verify" in sys.argv:
        print("Q1 — RE-FETCHING EVERY CITATION AT ITS CITED COMMIT")
        print("=" * 88)
        verified = verify()
        print(f"  to carry this run on the plain path, record citations_sha256 = "
              f"{citations_fingerprint()}")
    else:
        fp = citations_fingerprint()
        assert fp == RECORDED_VERIFICATION["citations_sha256"], (
            "the citations differ from those the recorded verification covered; run "
            "--verify and update RECORDED_VERIFICATION before writing the artifact")
        verified = RECORDED_VERIFICATION["citations_still_valid"]
        print(f"Q1 — the network is not used. Carrying the verification recorded on "
              f"{RECORDED_VERIFICATION['verified_on']} (--verify), whose "
              f"{len(EXAMINED) * CITATIONS_PER_REPO} citations match these exactly.")

    n_examined = len(EXAMINED)
    inherits = [e for e in EXAMINED if e["verdict"] == "INHERITS"]
    not_inherits = [e for e in EXAMINED if e["verdict"] == "DOES NOT INHERIT"]
    undetermined = [e for e in EXAMINED if e["verdict"] == "COULD NOT DETERMINE"]
    assert len(inherits) + len(not_inherits) + len(undetermined) == n_examined

    rec = {
        "question": "Referee Q1 — how many public repositories carry the PETS bounded "
                    "log-sigma construction AND train it against a sampled squared error?",
        "search_date": SEARCH_DATE,
        "protocol": {"path": PROTOCOL, "sha256": PROTOCOL_SHA256,
                     "fixed": "before the search, and unchanged afterwards"},
        "finding": (
            f"Of {n_examined} repositories examined on {SEARCH_DATE} under the protocol in "
            f"{PROTOCOL}, {n_examined} carry the construction and {len(inherits)} of those "
            f"train it against a sampled squared error."),
        "counts": {
            "examined": n_examined,
            "carry_the_construction": n_examined,
            "inherits": len(inherits),
            "does_not_inherit": len(not_inherits),
            "could_not_determine": len(undetermined),
            "construction_absent_and_so_out_of_scope": len(CONSTRUCTION_ABSENT),
            "cap": 25,
        },
        "what_this_count_is_not": (
            "It is a count over what was EXAMINED, never over a population. No claim is made "
            "about how many such repositories exist, what fraction of the field they are, or "
            "what the field does in general. GitHub code search and web search rank and "
            "truncate; this is a sample of convenience."),
        "reading": (
            "The substitution §6.3 identifies is RARE among the descendants examined, not "
            "common. Nine of ten kept PETS's likelihood, which is what opposes sigma -> 0, and "
            "the single repository that made the substitution does so only in a non-default "
            "mode. §2's hypothesis — that any descendant replacing the likelihood with a "
            "sampled squared error inherits the optimum — is untouched as a statement of "
            "mechanism: it is a claim about what follows from the substitution, and this "
            "survey did not test the mechanism in any of them. What the survey bears on is "
            "REACH, and the honest reading is that the reach is narrower than a reader of §2 "
            "would assume: the substitution is not a common pattern in this lineage. §2 "
            "should say so."),
        "examined": EXAMINED,
        "construction_absent": CONSTRUCTION_ABSENT,
        "subject_not_counted": SUBJECT,
        "verification": {
            # Always a --verify run's record: this invocation's, or the one carried.
            "mode": "--verify",
            "citations_still_valid": verified,
            "citations_checked": len(EXAMINED) * CITATIONS_PER_REPO,
            "how": "each cited file is re-fetched AT ITS CITED COMMIT from "
                   "raw.githubusercontent.com and the recorded line, or one of its immediate "
                   "neighbours, must still contain the recorded text",
        },
        # The command that produced the verification record the artifact carries.
        "generated_with": "scripts/q1_pets_descendants.py --verify",
    }

    print("\nQ1 — PUBLIC DESCENDANTS OF THE BOUNDED LOG-SIGMA CONSTRUCTION")
    print("=" * 88)
    print(f"  searched {SEARCH_DATE}, protocol fixed beforehand at")
    print(f"  {PROTOCOL}")
    print(f"  sha256 {PROTOCOL_SHA256}\n")
    print(f"  {rec['finding']}\n")
    for e in EXAMINED:
        mark = "INHERITS       " if e["verdict"] == "INHERITS" else "does not       "
        print(f"  {mark} {e['repo']}")
    print(f"\n  construction absent, out of scope: "
          f"{', '.join(c['repo'] for c in CONSTRUCTION_ABSENT)}")
    print(f"\n  A COUNT OVER WHAT WAS EXAMINED, NEVER OVER A POPULATION.")

    json.dump(rec, open(os.path.join(R.RESULTS, "q1_pets_descendants.json"), "w"), indent=2)
    print("\n  wrote results/q1_pets_descendants.json")
    return 0 if verified is not False else 1


if __name__ == "__main__":
    sys.exit(main())
