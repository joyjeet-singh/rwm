"""
Round 5, rule X11: the loaders and arenas the four X11 reading scripts share (x11a, x11b, x11c, x11d).

Nothing here computes a statistic. It names X11's weights and run records, builds each fold's
trajectories the way the discharged scripts build the held-out pair's, loads the models into the
same harness class they used, and checks a run's record before its weights are read. One copy, so
the four readings cannot drift apart on which model or which rows they mean.

  arena(fold)        task_d3_ens5.py:86-95 with the held-out pair replaced by the fold: the fold's
                     non-overlapping 400-row trajectories (MET.non_overlapping_starts), the same starts
                     as mn_sweep_eval.arena(ep, fold, 32), which X3 scored.
  in_sample(fold)    the same construction over the fold's eight training episodes.
  ens5 / single      task_d3_ens5.py:117-119 and r2_independent_ensemble.py:110-126 for the paths and
                     the harness; X3's weights_path (x3_cross_fold.py:121-124) for the single models.
"""
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import torch  # noqa: E402
import rwm_data as R  # noqa: E402
import rollout_eval as E  # noqa: E402
import rwm_metrics as MET  # noqa: E402
import rwm_model as M  # noqa: E402
import score_reference as S  # noqa: E402
import x3_cross_fold as X3  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
FOLDS = tuple(tuple(f) for f in X3.FOLDS)            # ((1, 8), (0, 2), (3, 4), (5, 6), (7, 9))
ENS5_SEEDS = (0, 1, 2)
SINGLE_SEEDS = (0, 1, 2, 3, 4)
ITERS = 2500
START, LEN = E.START_STEP, 400
STRAT = os.path.join(R.RESULTS, "step0_strat.json")


def fid(fold):
    return "".join(map(str, fold))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def blocked(out_path, reason, **detail):
    json.dump({"BLOCKED": reason, **detail}, open(out_path + ".blocked", "w"), indent=1, default=str)
    raise SystemExit(f"BLOCKED: {reason} ({R.rel(out_path)}.blocked); no reading written")


def ledger_hashes(rule_id, text):
    """Every 64-hex-digit token in backticks inside the ledger entry headed `### <rule_id> — ` (x3_cross_fold.py:323)."""
    m = re.search(rf"^### {re.escape(rule_id)} — .*?(?=^### |\Z)", text, flags=re.M | re.S)
    return [] if not m else [h.lower() for h in re.findall(r"`([0-9a-fA-F]{64})`", m.group(0))]


def require_prereg(rule_id, frozen, out_path):
    """Refuse to compute a reading unless the rule's ledger entry records the SHA-256 of every frozen file."""
    reg = ledger_hashes(rule_id, open(os.path.join(ROOT, "FINDINGS_LEDGER.md"), encoding="utf-8").read())
    missing = [p for p in frozen if sha256(p) not in reg]
    if missing:
        blocked(out_path, f"ledger {rule_id} does not record the SHA-256 of {missing}: the rule is not pre-registered as run")
    return {p: sha256(p) for p in frozen}


# ------------------------------------------------------------------ names
def ens5_weights(fold, s):
    if tuple(fold) == (1, 8):
        return os.path.join("runs", f"armA_seed{s}_ens5", f"weights_{ITERS}.pt")
    return os.path.join("runs", f"x3_armA_ho{fid(fold)}_seed{s}_ens5", f"weights_{ITERS}.pt")


def ens5_record(fold, s):
    if tuple(fold) == (1, 8):
        return os.path.join(R.RESULTS, f"step5_armA_seed{s}_ens5.json")
    return os.path.join(R.RESULTS, f"x3_run_armA_ho{fid(fold)}_seed{s}_ens5.json")


def single_weights(fold, s):
    return X3.weights_path("A", fold, s)


def single_record(fold, s):
    return X3.run_record("A", fold, s)


def check_record(path, fold, ensemble):
    """The run trained on the fold's complement, at the queued size and length, with finite losses."""
    a = json.load(open(path))
    hp = a["hyperparameters"]
    want_train = sorted(set(range(R.N_EPISODES)) - set(fold))
    bad = []
    if sorted(hp["holdout_episodes"]) != sorted(fold):
        bad.append(f"holdout {hp['holdout_episodes']}")
    if sorted(hp["train_episodes"]) != want_train:
        bad.append(f"train {hp['train_episodes']}")
    if hp["ensemble"] != ensemble:
        bad.append(f"ensemble {hp['ensemble']}")
    if hp["iterations"] != ITERS:
        bad.append(f"iterations {hp['iterations']}")
    if a.get("arm") != "A":
        bad.append(f"arm {a.get('arm')}")
    if any(not np.isfinite(x) for v in a["curves"].values() for x in v):
        bad.append("non-finite loss")
    return bad


# ------------------------------------------------------------------ data
_D = {}


def data():
    if not _D:
        paths = R.repo_paths()
        _D["cfg"] = R.load_reference_config(paths["lite"])
        _D["data"], _D["ep"] = R.load_data(paths["csv"], verbose=False)
    return _D["cfg"], _D["data"], _D["ep"]


def tensors(starts):
    """task_d3_ens5.py:94-95 for a given list of start rows."""
    cfg, dat, _ = data()
    idx = np.asarray(starts)[:, None] + np.arange(LEN)[None, :]
    raw = dat[idx]
    st = torch.as_tensor(R.normalise_state(raw[:, :, R.STATE_COLS], cfg["state_data_mean"], cfg["state_data_std"]),
                         dtype=torch.float32)
    ac = torch.as_tensor(raw[:, :, R.ACTION_COLS], dtype=torch.float32)
    return st, ac


def split_of(fold):
    return (E.make_split(seed=0, strat_path=STRAT, verbose=False) if tuple(fold) == (1, 8)
            else E.fold_split(list(fold), strat_path=STRAT))


def arena(fold):
    _, _, ep = data()
    sp = split_of(fold)
    assert sorted(sp["holdout_episodes"]) == sorted(fold), sp
    starts = MET.non_overlapping_starts(ep, sorted(fold), LEN)
    assert len(starts) == 4 and int(MET.n_independent(starts, LEN)) == 4, starts
    st, ac = tensors(starts)
    return {"fold": tuple(fold), "starts": [int(s) for s in starts], "episode": [int(ep[s]) for s in starts],
            "st": st, "ac": ac}


def in_sample(fold):
    _, _, ep = data()
    sp = split_of(fold)
    starts = MET.non_overlapping_starts(ep, sorted(sp["train_episodes"]), LEN)
    assert len(starts) == 16 and int(MET.n_independent(starts, LEN)) == 16, starts
    st, ac = tensors(starts)
    return {"fold": tuple(fold), "starts": [int(s) for s in starts], "episode": [int(ep[s]) for s in starts],
            "st": st, "ac": ac}


# ------------------------------------------------------------------ models
def load_ens5(path):
    sd = torch.load(path, map_location="cpu")["model_state_dict"]
    m = S.ReferenceRWM(sd)
    m.eval()
    return m, sd


def harness_check(sd, st, ac):
    """task_d3_ens5.py:122-128: the harness must agree with our trainer's forward."""
    cfg, _, _ = data()
    own = M.build_from_config(cfg, ensemble_size=5)
    own.load_state_dict(sd, strict=True)
    own.eval()
    with torch.no_grad():
        p_own, _ = own.rollout_full(st.clone(), ac, START, action_offset=1)
    return p_own


def load_single(path):
    """r2_independent_ensemble.load_ens1 (lines 110-126), with the path given."""
    assert os.path.exists(path), f"missing {path}"
    sd = torch.load(path, map_location="cpu")["model_state_dict"]
    m = S.ReferenceRWM(sd, ensemble=1, hidden=256)
    m.eval()
    return m
