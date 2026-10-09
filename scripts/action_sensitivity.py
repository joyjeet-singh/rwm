"""
Rule X2 (ledger M-84; PRE-REGISTERED, exploratory) -- do our trained models condition their forecasts on the
action they are given?

It never re-opens M-23, M-64 or M-74..M-76, and nothing it returns changes a verdict.

MODELS (inference only, existing weights)
  arm_a     our Arm A (autoregressive), seeds 0-2, at 2,500 and 10,000 iterations: the 10k runs' checkpoints
            runs/armA_seed{s}_10k/weights_{2500,10000}.pt. Their 2,500 files are byte-identical to the 2,500-iteration
            runs' (asserted). THIS MODEL GETS THE READINGS.
  arm_b     our Arm B (teacher-forced), the same seeds and checkpoints. Reported alongside only.
  released  the released checkpoint (setup.sh's pretrain_rnn_ens.pt). Reported alongside only.

ARENAS (400-step trajectories: 32 history rows, then 368 forecast rows)
  in_sample_n16   mn_sweep_eval.arena() over the eight training episodes: 16 independent trajectories (arm_a, arm_b)
  held_out_n4     section 5's held-out pair: 4 (all three models)
  all_ten_n20     all ten episodes: 20 (released only; its own training data)
Horizons {1, 8, 32, 100}, cumulative over forecast steps 1..h.

THE ROLLOUT is alignment_defect_ci.rollout(), imported: it calls model.rollout(st, ac, START_STEP,
action_offset=...). An intervention wraps model.rollout and transforms the action array `ac` before it reaches the
model. Under offset 1 (training's causal pairing), forecast step i reads action rows [i-31, i+1) at i = 32 (the
whole history window, whose last row is row 32) and row i at every later step: src/rwm_model.py and
src/score_reference.py, the two `a_in = action[...]` lines of rollout(). So the forecast steps read rows 32..399 of
each window, and only those rows are transformed. The history pairs (rows 1..31) are untouched, so the recurrent
state that meets the first forecast action is identical across interventions. Assertion (c) checks this against the
actions the model actually received.

INTERVENTIONS
  I0 true    offset 1, the reference
  I1 stale   offset 0, round 2's N1 (alignment_by_horizon.py)
  I2 swap    offset 1; trajectory i takes the actions of trajectory (i + 1) mod n of the same arena, in its start
             order, at the same forecast rows
  I3 mean    offset 1; each action dimension at the forecast rows is replaced by its mean over the model's own
             training rows: every row of the eight training episodes for arm_a and arm_b, every row of all ten
             episodes for the released checkpoint
  I4 noise   offset 1; the true actions plus e ~ N(0, (k sigma_d)^2) at the forecast rows, k in {0.1, 0.5}, sigma_d
             that dimension's standard deviation (ddof 0) over the same training rows. 8 draws per arena: one array
             z = numpy default_rng(0).standard_normal((8, n, 368, 12)) per arena, shared by every model and both k,
             e = k sigma z. A trajectory's I4 error is its mean over the 8 draws.

MEASURES, per model x checkpoint x arena x horizon x intervention
  E      err(I) / err(I0) - 1, in percent, with err alignment_defect_ci.stats()'s relative-L1 over the trajectories
         of a draw: N1's overstatement with I in place of offset 0. For arm_a and arm_b, E is the mean over the three
         seeds of each seed's E, as N1's three-seed mean is. 95% interval: percentiles 2.5 and 97.5 over whole-
         trajectory resamples, the same resample applied to all three seeds and to both interventions inside each
         draw: exact over all 256 at n = 4; 20,000 Monte Carlo draws, numpy default_rng(0).integers(0, n, (20000, n)),
         at n = 16 and n = 20 (alignment_defect_ci's own recipe). The per-draw statistic is computed from per-
         trajectory means, asserted equal to alignment_defect_ci.stats() on every point estimate.
  Delta  (descriptive) relative-L1 of the intervened forecast against the I0 forecast, rollout_eval.relative_error()
         with the I0 forecast as target, over steps 1..h; mean over draws for I4 and over seeds for arm_a/arm_b.
         0 for a model that ignores the action.
  context (descriptive, per arena, over the forecast rows): the fraction of steps with a_t != a_{t-1} in any
         dimension; mean |a_t - a_{t-1}| / mean |a_t - abar|, abar the per-dimension mean over the arena's forecast
         rows (how large a one-step shift is beside the action's spread); the same ratio for the swap,
         mean |a_swap,t - a_t| / mean |a_t - abar|.

ASSERTIONS, before any reading
  (a) I0 and I1 reproduce results/alignment_by_horizon.json: the released checkpoint to 1e-9 (both arenas), arm_a
      to 1e-6 (held-out pair, every seed, both checkpoints), on every field the two share. On the in-sample arena,
      arm_a's I0 reproduces results/mn_compute_matched.json three_seed_mean_l1.in_sample (and .held_out) at 2,500 and
      10,000, h in {1, 8, 32, 100}, to 1e-6. Also, to 1e-6: arm_b's I0 per seed at 2,500 (held-out, h in {1, 8, 100})
      against results/head_to_head_accuracy.json, arm_b's at 10,000 (held-out, h = 100) against
      results/task_d1_threeseed.json, and the released checkpoint's I0 (held-out, h in {1, 8, 100}) against
      results/head_to_head_accuracy.json.
  (b) The offset is applied: under I1, for every model and every window, the action tensor the model received differs
      from I0's at one forecast step or more, and the forecast differs (max |difference| > 0). The fraction of forecast
      steps whose input differs is recorded.
  (c) Each intervention reaches exactly the forecast steps: under I0 the model receives row 32 + j at forecast step j
      (as the docstring's reading of rollout() says), and under I2, I3 and I4 the history pairs it receives are I0's
      while every forecast-step action is the transformed row.
  A failure stops the run before any reading is computed.

THE READING, for arm_a at 2,500 and for arm_a at 10,000: E under I2 (swap), h = 8, in_sample_n16, three-seed mean
and its interval. The first matching outcome applies:
  1 RESPONDS TO THE ACTION            the interval's lower bound > 0 and the point estimate >= +10%
  2 ERROR FALLS WITH WRONG ACTIONS    the interval's upper bound < 0
  3 DOES NOT RESPOND MEASURABLY       the interval's upper bound < +10%
  4 UNRESOLVED                        otherwise
arm_b (in_sample_n16) and the released checkpoint (all_ten_n20, its own training data) get the same statistic and the
label it would carry, marked "alongside, not a reading".

CAP: 30 projected CPU-minutes, projected after the first model of each phase (phase 1: I0 and I1 for every model,
then assertions; phase 2: I2-I4). Beyond it the run stops before writing readings.

  python scripts/action_sensitivity.py --self-test     # synthetic data, untrained weights: no reading
  python scripts/action_sensitivity.py --assert-only   # assertion (a) on the cases that reproduce existing artifacts
  python scripts/action_sensitivity.py                 # self-test, then the rule (refuses unless its ledger entry
                                                       # records this file's SHA-256)
Writes results/action_sensitivity.json.
"""
import argparse
import hashlib
import itertools
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import torch  # noqa: E402

import alignment_defect_ci as ADC  # noqa: E402
import mn_sweep_eval as MSE  # noqa: E402
import rollout_eval as E  # noqa: E402
import rwm_data as R  # noqa: E402
import rwm_metrics as MET  # noqa: E402
import rwm_model as M  # noqa: E402
import score_reference as S  # noqa: E402

RULE_ID = "M-84"
HORIZONS = (1, 8, 32, 100)
SEEDS = (0, 1, 2)
CHECKPOINTS = (2500, 10000)
WEIGHTS = "runs/arm{arm}_seed{s}_10k/weights_{it}.pt"
NOISE_K = (0.1, 0.5)
NOISE_DRAWS = 8
NOISE_SEED = 0
INTERVENTIONS = ("I1_stale", "I2_swap", "I3_mean", "I4_noise_k0.1", "I4_noise_k0.5")
READING = {"intervention": "I2_swap", "h": 8, "arena": "in_sample_n16",
           "models": ("arm_a_2500", "arm_a_10000"),
           "alongside": {"arm_b_2500": "in_sample_n16", "arm_b_10000": "in_sample_n16", "released": "all_ten_n20"}}
THRESHOLD_PCT = 10.0
TOL_RELEASED, TOL_ARM = 1e-9, 1e-6
CAP_CPU_MIN = 30.0
F0, F1 = E.START_STEP, E.LEN_TRAJ          # the forecast rows read under offset 1: 32 .. 399
OUT = os.path.join(R.RESULTS, "action_sensitivity.json")
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
MODULES = ("scripts/action_sensitivity.py", "scripts/alignment_defect_ci.py", "scripts/mn_sweep_eval.py",
           "src/rollout_eval.py", "src/rwm_data.py", "src/rwm_metrics.py", "src/rwm_model.py", "src/score_reference.py")


def blocked(reason, **detail):
    json.dump({"BLOCKED": reason, **detail}, open(OUT + ".blocked", "w"), indent=1, default=str)
    raise SystemExit(f"BLOCKED: {reason} (results/action_sensitivity.json.blocked); no reading written")


# ------------------------------------------------------------------------------------------- the reading
def label(point, lo, hi):
    assert np.isfinite([point, lo, hi]).all(), (point, lo, hi)
    if lo > 0 and point >= THRESHOLD_PCT:
        return "RESPONDS TO THE ACTION"
    if hi < 0:
        return "ERROR FALLS WITH WRONG ACTIONS"
    if hi < THRESHOLD_PCT:
        return "DOES NOT RESPOND MEASURABLY"
    return "UNRESOLVED"


# ------------------------------------------------------------------------------------------- interventions
def t_swap(ac):
    out = ac.clone()
    perm = torch.as_tensor([(i + 1) % ac.shape[0] for i in range(ac.shape[0])])
    out[:, F0:F1] = ac[perm, F0:F1]
    return out


def t_mean(mu):
    def f(ac):
        out = ac.clone()
        out[:, F0:F1] = torch.as_tensor(mu, dtype=ac.dtype)
        return out
    return f


def t_noise(eps):
    def f(ac):
        out = ac.clone()
        out[:, F0:F1] = ac[:, F0:F1] + torch.as_tensor(eps, dtype=ac.dtype)
        return out
    return f


class Hook:
    """Wraps model.rollout so alignment_defect_ci.rollout's call passes through a transform of its action array, and
    records every action slice the model receives (forward() for our models, step() for the released checkpoint)."""

    def __init__(self, model):
        self.model, self._rollout = model, model.rollout
        self.entry = "step" if isinstance(model, S.ReferenceRWM) else "forward"
        self._entry = getattr(model, self.entry)
        self.transform, self.fed, self.ac = None, [], None
        model.rollout = self._hooked_rollout
        setattr(model, self.entry, self._hooked_entry)

    def _hooked_rollout(self, st, ac, start, action_offset):
        self.fed, self.true_ac = [], ac
        self.ac = ac if self.transform is None else self.transform(ac)
        return self._rollout(st, self.ac, start, action_offset=action_offset)

    def _hooked_entry(self, s_in, a_in, *a, **k):
        self.fed.append(a_in.detach().clone())
        return self._entry(s_in, a_in, *a, **k)

    def run(self, data, cfg, idx, offset, transform=None):
        self.transform = transform
        try:
            pred, true = ADC.rollout(self.model, data, cfg, idx, offset)
        finally:
            self.transform = None
        return {"pred": pred, "true": true, "fed": self.fed, "ac": self.ac, "true_ac": self.true_ac}


# ------------------------------------------------------------------------------------------- statistics
def traj_means(run, h):
    """Per-trajectory relative-L1 over forecast steps 1..h: alignment_defect_ci.stats()'s rel_l1 is their mean."""
    e = (run["pred"] - run["true"])[:, F0:F0 + h]
    t = run["true"][:, F0:F0 + h]
    return (np.abs(e).sum(-1) / np.abs(t).sum(-1)).mean(1)


def adc_rel(run, scale, h):
    ADC.H = h
    try:
        return ADC.stats(run["pred"] - run["true"], run["true"], scale, np.arange(len(run["pred"])))["rel_l1"]
    finally:
        ADC.H = 368


def draws_for(n):
    if n == 4:
        return np.array(list(itertools.product(range(4), repeat=4)))
    return np.random.default_rng(ADC.MC_SEED).integers(0, n, size=(ADC.MC_N, n))


def e_with_ci(c_int, c_ref, D):
    """c_int, c_ref: lists over seeds of per-trajectory means. E = mean over seeds of 100 (err_I / err_0 - 1)."""
    point = float(np.mean([100 * (ci.mean() / cr.mean() - 1) for ci, cr in zip(c_int, c_ref)]))
    boot = np.mean([100 * (ci[D].mean(1) / cr[D].mean(1) - 1) for ci, cr in zip(c_int, c_ref)], axis=0)
    return point, [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))], boot


def delta(run, ref, h):
    p = torch.as_tensor(run["pred"][:, :F0 + h])
    q = torch.as_tensor(ref["pred"][:, :F0 + h])
    return E.relative_error(p, q, F0)[0]


def summarise(run, ref):
    """What the measures need from a run: per-trajectory errors and Delta against the I0 run, at every horizon."""
    return {"c": {h: traj_means(run, h) for h in HORIZONS}, "delta": {h: delta(run, ref, h) for h in HORIZONS}}


def close(a, b, tol):
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(close(a[k], b[k], tol) for k in a)
    if isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(close(x, y, tol) for x, y in zip(a, b))
    if isinstance(a, (int, float, np.floating)):
        return abs(float(a) - float(b)) <= tol
    return a == b


# ------------------------------------------------------------------------------------------- assertions (b), (c)
def check_b(r0, r1):
    """Under I1 against I0, per window: the forecast steps whose input differs (the first step, which reads the whole
    history window, reported apart from the later ones), whether the forecast differs, and whether every later step
    read the row the offset says (row 32 + j under I0, row 32 + j - 1 under I1), checked against the data's actions."""
    n = r0["pred"].shape[0]
    assert len(r0["fed"]) == len(r1["fed"]) == F1 - F0
    diff = np.array([[not torch.equal(a[w], b[w]) for a, b in zip(r0["fed"], r1["fed"])] for w in range(n)])
    fdiff = np.abs(r1["pred"][:, F0:] - r0["pred"][:, F0:]).reshape(n, -1).max(1)
    rows_ok = all(torch.equal(r0["fed"][j][:, 0], r0["true_ac"][:, F0 + j]) and
                  torch.equal(r1["fed"][j][:, 0], r1["true_ac"][:, F0 + j - 1]) for j in range(1, F1 - F0))
    return {"every_window_input_differs": bool(diff.any(1).all()),
            "every_window_later_step_input_differs": bool(diff[:, 1:].any(1).all()),
            "every_window_forecast_differs": bool((fdiff > 0).all()),
            "later_steps_read_the_offset_rows": bool(rows_ok),
            "first_step_input_differs": [bool(x) for x in diff[:, 0]],
            "fraction_of_later_forecast_steps_input_differs": [float(x) for x in diff[:, 1:].mean(1)],
            "min_max_abs_forecast_difference": float(fdiff.min())}


def b_passes(v):
    return (v["every_window_input_differs"] and v["every_window_later_step_input_differs"]
            and v["every_window_forecast_differs"] and v["later_steps_read_the_offset_rows"])


def expected(iname, true_ac, mu=None, eps=None):
    """The transformed action array, built independently of t_swap / t_mean / t_noise, from the data's actions."""
    out = true_ac.clone()
    if iname == "I2_swap":
        out[:, F0:F1] = torch.roll(true_ac, shifts=-1, dims=0)[:, F0:F1]
    elif iname == "I3_mean":
        out[:, F0:F1] = torch.as_tensor(np.broadcast_to(mu, out[:, F0:F1].shape).copy(), dtype=true_ac.dtype)
    elif iname.startswith("I4"):
        out[:, F0:F1] = true_ac[:, F0:F1] + torch.as_tensor(eps, dtype=true_ac.dtype)
    return out


def check_c(r0, ri=None, exp=None):
    """I0: the first step receives the data's rows 1..32 and forecast step j row 32 + j. An intervention: the array the
    model was given equals the independently built one, differs from the data somewhere in the forecast rows and nowhere
    in the history, the history pairs received are I0's, and every forecast step received the transformed row."""
    r = r0 if ri is None else ri
    ok = torch.equal(r0["fed"][0], r0["true_ac"][:, 1:F0 + 1])                   # I0's first step: rows 1..32
    ok &= torch.equal(r["ac"][:, :F0], r["true_ac"][:, :F0])                     # history rows untouched
    ok &= torch.equal(r["fed"][0][:, :-1], r0["fed"][0][:, :-1])                  # history pairs as I0's
    ok &= torch.equal(r["fed"][0][:, -1], r["ac"][:, F0])                         # first forecast step: row 32
    ok &= all(torch.equal(r["fed"][j][:, 0], r["ac"][:, F0 + j]) for j in range(1, F1 - F0))
    if ri is not None:
        ok &= exp is not None and torch.equal(r["ac"], exp)
        ok &= not torch.equal(r["ac"][:, F0:F1], r["true_ac"][:, F0:F1])
    return bool(ok)


# ------------------------------------------------------------------------------------------- setup
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(paths, cfg, kind, it=None, s=None):
    if kind == "released":
        m = S.ReferenceRWM(torch.load(paths["ckpt"], map_location="cpu")["system_dynamics_state_dict"])
    else:
        m = M.build_from_config(cfg, ensemble_size=1)
        w = WEIGHTS.format(arm=kind[-1].upper(), s=s, it=it)
        m.load_state_dict(torch.load(w, map_location="cpu")["model_state_dict"], strict=True)
    m.eval()
    return m


def setting():
    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    data, ep = R.load_data(paths["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"), verbose=False)
    scale = MET.training_scale(data, ep, split["train_episodes"], cfg["state_data_mean"], cfg["state_data_std"])
    ins = MSE.arena(ep, split["train_episodes"], 32)
    ho = MSE.arena(ep, split["holdout_episodes"], 32)
    s20 = MET.non_overlapping_starts(ep, list(range(10)), E.LEN_TRAJ)
    assert ins["n_independent"] == 16 and ho["n_independent"] == 4 and MET.n_independent(s20, E.LEN_TRAJ) == 20
    assert ho["starts"] == MSE.HELD_OUT_STARTS
    arenas = {"in_sample_n16": [int(x) for x in ins["starts"]], "held_out_n4": [int(x) for x in ho["starts"]],
              "all_ten_n20": [int(x) for x in s20]}
    mk = lambda st: np.asarray(st)[:, None] + np.arange(E.LEN_TRAJ)[None, :]
    rows_tr = np.isin(ep, split["train_episodes"])
    acts = {"arm": data[rows_tr][:, R.ACTION_COLS], "released": data[np.isin(ep, list(range(10)))][:, R.ACTION_COLS]}
    norm = {k: (v.mean(0), v.std(0)) for k, v in acts.items()}
    return paths, cfg, data, ep, split, scale, arenas, mk, norm


def model_plan():
    plan = []
    for arm in ("arm_a", "arm_b"):
        for it in CHECKPOINTS:
            for s in SEEDS:
                plan.append({"key": f"{arm}_{it}", "kind": arm, "it": it, "seed": s,
                             "arenas": ("in_sample_n16", "held_out_n4"), "norm": "arm"})
    plan.append({"key": "released", "kind": "released", "it": None, "seed": None,
                 "arenas": ("all_ten_n20", "held_out_n4"), "norm": "released"})
    return plan


def interventions(norm_key, norm, Z):
    """{name: [(transform, expectation-builder)]}: one pair per draw (8 for I4, 1 otherwise)."""
    mu, sd = norm[norm_key]
    mu32 = mu.astype(np.float32)
    out = {"I2_swap": [(t_swap, lambda tac: expected("I2_swap", tac))],
           "I3_mean": [(t_mean(mu32), lambda tac: expected("I3_mean", tac, mu=mu32))]}
    for k in NOISE_K:
        pairs = []
        for d in range(NOISE_DRAWS):
            eps = (k * sd[None, None, :] * Z[d]).astype(np.float32)
            pairs.append((t_noise(eps), (lambda e: lambda tac: expected("I4", tac, eps=e))(eps)))
        out[f"I4_noise_k{k}"] = pairs
    return out


def a_in_lines():
    """file:line of the two `a_in = action[...]` lines of each rollout(), read from the source as it stands."""
    out = []
    for f, cls in (("src/rwm_model.py", "RWMEnsemble"), ("src/score_reference.py", "ReferenceRWM")):
        lines = open(f, encoding="utf-8").read().splitlines()
        start = next(i for i, l in enumerate(lines) if re.match(rf"class {cls}\b", l))
        ro = next(i for i in range(start, len(lines)) if re.match(r"\s+def rollout\(", lines[i]))
        hits = [i + 1 for i in range(ro, len(lines)) if "a_in = action[" in lines[i]][:2]
        assert len(hits) == 2, (f, hits)
        out += [f"{f}:{h}: {lines[h - 1].strip()}" for h in hits]
    return out


def context(ac, perm_ac):
    a, ap = ac[:, F0:F1].double(), ac[:, F0 - 1:F1 - 1].double()
    spread = (a - a.reshape(-1, a.shape[-1]).mean(0)).abs().mean()
    return {"fraction_of_steps_with_changed_action": float((a != ap).any(-1).double().mean()),
            "one_step_shift_over_spread": float((a - ap).abs().mean() / spread),
            "swap_over_spread": float((perm_ac[:, F0:F1].double() - a).abs().mean() / spread)}


# ------------------------------------------------------------------------------------------- self-test
def self_test():
    """Synthetic data in the CSV's layout, untrained weights: the hook, the three checks, the statistic, the
    interval and every branch of the reading. Produces no reading of any trained model."""
    torch.manual_seed(0)
    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    n, ncol = 4, 66
    rng = np.random.default_rng(1)
    data = np.zeros((n * E.LEN_TRAJ, ncol))
    data[:, R.ACTION_COLS] = rng.normal(0, 0.5, (n * E.LEN_TRAJ, 12))
    data[:, R.STATE_COLS] = R.denormalise_state(rng.normal(0, 1, (n * E.LEN_TRAJ, 45)),
                                                cfg["state_data_mean"], cfg["state_data_std"])
    idx = np.arange(n)[:, None] * E.LEN_TRAJ + np.arange(E.LEN_TRAJ)[None, :]
    # the truth is the model's own causal forecast plus a little noise, so err(I0) is small
    responds = M.build_from_config(cfg, ensemble_size=1).eval()
    hook = Hook(responds)
    r = hook.run(data, cfg, idx, 1)
    st = r["pred"].copy()
    st[:, F0:] += rng.normal(0, 1e-3, st[:, F0:].shape)
    data[idx.reshape(-1)[:, None], np.asarray(R.STATE_COLS)[None, :]] = R.denormalise_state(
        st.reshape(-1, 45), cfg["state_data_mean"], cfg["state_data_std"])
    deaf = M.build_from_config(cfg, ensemble_size=1).eval()
    deaf.load_state_dict(responds.state_dict())
    with torch.no_grad():                                  # the action columns of both GRUs' input weights
        for base in (deaf.state_base, deaf.auxiliary_base):
            base.memory.rnn.weight_ih_l0[:, 45:] = 0
    scale = np.ones(45)
    mu, sd = data[:, R.ACTION_COLS].mean(0), data[:, R.ACTION_COLS].std(0)
    Z = np.random.default_rng(NOISE_SEED).standard_normal((NOISE_DRAWS, n, F1 - F0, 12))
    D = draws_for(n)
    out = {}
    for name, hk in (("responds", hook), ("deaf", Hook(deaf))):
        r0, r1 = hk.run(data, cfg, idx, 1), hk.run(data, cfg, idx, 0)
        assert check_c(r0), "self-test: I0 does not read rows 32..399 at the forecast steps"
        b = check_b(r0, r1)
        tr, okc = {}, True
        for k, pairs in interventions("arm", {"arm": (mu, sd)}, Z).items():
            tr[k] = []
            for f, ex in pairs:
                x = hk.run(data, cfg, idx, 1, f)
                okc &= check_c(r0, x, ex(x["true_ac"]))
                tr[k].append(x)
        assert okc, "self-test: (c) fails on a true transform"
        assert b_passes(b) if name == "responds" else not b["every_window_forecast_differs"]
        # (c) must catch a transform of the history, a no-op, and a swap in the wrong direction
        bad = hk.run(data, cfg, idx, 1, lambda ac: ac + 1.0)
        assert not check_c(r0, bad, bad["ac"]), "self-test: (c) missed a transform of the history rows"
        noop = hk.run(data, cfg, idx, 1, lambda ac: ac.clone())
        assert not check_c(r0, noop, expected("I2_swap", noop["true_ac"])), "self-test: (c) missed a no-op"
        def rev(ac):
            out = ac.clone()
            out[:, F0:F1] = torch.roll(ac, shifts=1, dims=0)[:, F0:F1]
            return out
        rv = hk.run(data, cfg, idx, 1, rev)
        assert not check_c(r0, rv, expected("I2_swap", rv["true_ac"])), "self-test: (c) missed a reversed swap"
        c0 = traj_means(r0, 8)
        assert abs(c0.mean() - adc_rel(r0, scale, 8)) < 1e-12
        ci_ = traj_means(tr["I2_swap"][0], 8)
        p, (lo, hi), boot = e_with_ci([ci_], [c0], D)
        # the vectorised interval equals alignment_defect_ci.stats() draw by draw
        for sel in D[:20]:
            ADC.H = 8
            try:
                a = ADC.stats(tr["I2_swap"][0]["pred"] - tr["I2_swap"][0]["true"], tr["I2_swap"][0]["true"], scale, sel)["rel_l1"]
                z = ADC.stats(r0["pred"] - r0["true"], r0["true"], scale, sel)["rel_l1"]
            finally:
                ADC.H = 368
            assert abs(100 * (a / z - 1) - 100 * (ci_[sel].mean() / c0[sel].mean() - 1)) < 1e-9
        out[name] = {"b": b, "E_swap_h8": p, "ci": [lo, hi], "label": label(p, lo, hi),
                     "delta_swap_h8": delta(tr["I2_swap"][0], r0, 8)}
    assert b_passes(out["responds"]["b"])
    assert out["responds"]["label"] == "RESPONDS TO THE ACTION", out["responds"]
    assert out["deaf"]["E_swap_h8"] == 0.0 and out["deaf"]["delta_swap_h8"] == 0.0, out["deaf"]
    assert out["deaf"]["label"] == "DOES NOT RESPOND MEASURABLY", out["deaf"]
    assert not out["deaf"]["b"]["every_window_forecast_differs"]      # (b) would stop a run on a deaf model
    # an offset that is never applied: (b) must fail
    ign = M.build_from_config(cfg, ensemble_size=1).eval()
    ign.load_state_dict(responds.state_dict())
    hi_ = Hook(ign)
    orig = hi_._rollout
    hi_._rollout = lambda st, ac, start, action_offset: orig(st, ac, start, action_offset=1)
    assert not b_passes(check_b(hi_.run(data, cfg, idx, 1), hi_.run(data, cfg, idx, 0)))
    # the ledger check: a pre-registration naming this file's hash passes, any other text does not
    h1, h2 = "a" * 64, "b" * 64
    fake = (f"### M-83 — x\nSHA-256 `{h2}`\n\n### {RULE_ID} — PRE-REGISTERED rule X2: t · **NEW**\n(sha-256 `{h1}`)\n"
            f"### M-85 — y\nSHA-256 `{h2}`\n")
    assert ledger_hashes(fake) == [h1], ledger_hashes(fake)
    assert ledger_hashes(fake.replace(f"### {RULE_ID} ", "### M-99 ")) == []
    # every branch of the reading
    assert label(25.0, 3.0, 60.0) == "RESPONDS TO THE ACTION"
    assert label(9.0, 1.0, 20.0) == "UNRESOLVED"                       # lower bound > 0 but point below +10%
    assert label(-5.0, -9.0, -1.0) == "ERROR FALLS WITH WRONG ACTIONS"
    assert label(2.0, -3.0, 8.0) == "DOES NOT RESPOND MEASURABLY"
    assert label(12.0, -3.0, 30.0) == "UNRESOLVED"
    assert label(10.0, 0.5, 9.9) == "RESPONDS TO THE ACTION"           # first match wins
    print("self-test: passed — hook, (b), (c), the statistic, the interval and all four outcomes "
          f"(responds: E = {out['responds']['E_swap_h8']:+.1f}%; deaf: E = {out['deaf']['E_swap_h8']:+.1f}%)")
    return out


# ------------------------------------------------------------------------------------------- the rule
def ledger_hashes(text):
    """Every 64-hex-digit token in backticks inside the ledger entry headed `### M-84 — `, lower-cased."""
    m = re.search(rf"^### {RULE_ID} — .*?(?=^### |\Z)", text, re.M | re.S)
    return [h.lower() for h in re.findall(r"`([0-9a-fA-F]{64})`", m.group(0))] if m else []


def phase1(paths, cfg, data, scale, arenas, mk, assert_only, log):
    """I0 and I1 for every model and arena (for assert-only: the cases that reproduce committed artifacts)."""
    runs, cpu0, wall0, proj = {}, time.process_time(), time.time(), None
    for k, spec in enumerate(model_plan()):
        model = load(paths, cfg, spec["kind"], spec["it"], spec["seed"])
        hook = Hook(model)
        tag = (spec["key"], spec["seed"])
        runs[tag] = {}
        for ar in spec["arenas"]:
            idx = mk(arenas[ar])
            need_i1 = not assert_only or spec["kind"] == "released" or (spec["kind"] == "arm_a" and ar == "held_out_n4")
            runs[tag][ar] = {"I0": hook.run(data, cfg, idx, 1)}
            if need_i1:
                runs[tag][ar]["I1_stale"] = hook.run(data, cfg, idx, 0)
        if k == 0:
            per = (time.process_time() - cpu0) / (2 * sum(len(arenas[a]) for a in spec["arenas"]))
            ntraj = sum(len(arenas[a]) for s in model_plan() for a in s["arenas"])
            proj = per * (2 + 2 + 2 * NOISE_DRAWS) * ntraj / 60
            log(f"  projection after the first model (phase 1): {proj:.1f} CPU-min for the whole rule "
                f"(cap {CAP_CPU_MIN:.0f})")
            if proj > CAP_CPU_MIN and not assert_only:
                blocked("projected CPU exceeds the cap after the first model of phase 1", projection_cpu_min=proj)
    return runs, {"cpu_s": time.process_time() - cpu0, "wall_s": time.time() - wall0, "projection_cpu_min": proj}


def assertion_a(runs, scale, arenas, assert_only):
    A = json.load(open(os.path.join(R.RESULTS, "alignment_by_horizon.json")))
    MC = json.load(open(os.path.join(R.RESULTS, "mn_compute_matched.json")))["part2_centre_at_more_compute"]["three_seed_mean_l1"]
    HH = json.load(open(os.path.join(R.RESULTS, "head_to_head_accuracy.json")))["rows"]
    D1 = json.load(open(os.path.join(R.RESULTS, "task_d1_threeseed.json")))["by_horizon"]
    rec, bad = {}, []

    def n1_record(r0, r1, h, n):
        c0, c1 = traj_means(r0, h), traj_means(r1, h)
        p, ci, _ = e_with_ci([c1], [c0], draws_for(n))
        return {"pooled_offset0": float(c1.mean()), "pooled_offset1": float(c0.mean()), "overstatement_pct": p,
                "per_trajectory_offset0": c1.tolist(), "per_trajectory_offset1": c0.tolist(), "ci95_pct": ci,
                "n_resamples": len(draws_for(n))}

    def theirs(full):
        return {"pooled_offset0": full["pooled"]["offset0"]["rel_l1"], "pooled_offset1": full["pooled"]["offset1"]["rel_l1"],
                "overstatement_pct": full["overstatement_pct"]["rel_l1"],
                "per_trajectory_offset0": full["per_trajectory"]["offset0"]["rel_l1"],
                "per_trajectory_offset1": full["per_trajectory"]["offset1"]["rel_l1"],
                "ci95_pct": full["ci95_pct"]["rel_l1"], "n_resamples": full["n_resamples"]}

    # the point estimates are alignment_defect_ci.stats()'s, whatever the per-trajectory route
    for tag, by_ar in runs.items():
        for ar, by_i in by_ar.items():
            for iname, r in by_i.items():
                for h in HORIZONS:
                    if abs(traj_means(r, h).mean() - adc_rel(r, scale, h)) > 1e-12:
                        bad.append(f"{tag} {ar} {iname} h={h}: per-trajectory route differs from ADC.stats")
    # released, both arenas, against N1
    for ar in ("held_out_n4", "all_ten_n20"):
        r0, r1 = runs[("released", None)][ar]["I0"], runs[("released", None)][ar]["I1_stale"]
        for h in HORIZONS:
            mine, ref = n1_record(r0, r1, h, len(arenas[ar])), theirs(A["released"]["full"][ar][str(h)])
            ok = close(mine, ref, TOL_RELEASED) and A["released"]["full"][ar][str(h)]["starts"] == arenas[ar]
            rec[f"released|{ar}|h{h}"] = ok
            if not ok:
                bad.append(f"released {ar} h={h} does not reproduce alignment_by_horizon.json to {TOL_RELEASED}")
    # arm_a, held-out, per seed and the three-seed mean, against N1; in-sample and held-out I0 against N3
    for it in CHECKPOINTS:
        for h in HORIZONS:
            per = []
            for s in SEEDS:
                r = runs[(f"arm_a_{it}", s)]["held_out_n4"]
                mine = n1_record(r["I0"], r["I1_stale"], h, 4)
                per.append(mine["overstatement_pct"])
                ok = close(mine, theirs(A["arm_a"][str(it)]["full"][str(s)][str(h)]), TOL_ARM)
                rec[f"arm_a_{it}|seed{s}|held_out_n4|h{h}"] = ok
                if not ok:
                    bad.append(f"arm_a {it} seed {s} h={h} does not reproduce alignment_by_horizon.json to {TOL_ARM}")
            m3 = A["arm_a"][str(it)]["summary_three_seed_mean_pct"][str(h)]["rel_l1"]
            if abs(np.mean(per) - m3) > TOL_ARM:
                bad.append(f"arm_a {it} h={h}: three-seed mean {np.mean(per)} against {m3}")
            for ar, key in (("in_sample_n16", "in_sample"), ("held_out_n4", "held_out")):
                v = float(np.mean([traj_means(runs[(f"arm_a_{it}", s)][ar]["I0"], h).mean() for s in SEEDS]))
                ok = abs(v - MC[str(it)][key][str(h)]) <= TOL_ARM
                rec[f"arm_a_{it}|{ar}|I0|h{h}|mn_compute_matched"] = ok
                if not ok:
                    bad.append(f"arm_a {it} {ar} h={h}: I0 {v} against mn_compute_matched {MC[str(it)][key][str(h)]}")
    # arm_b and the released checkpoint's I0 against the head-to-head table and task_d1
    for s in SEEDS:
        for h in (1, 8, 100):
            v = float(traj_means(runs[("arm_b_2500", s)]["held_out_n4"]["I0"], h).mean())
            ref = HH["armB"]["per_model"][f"armB_teacher_forced_seed{s}"][str(h)]["l1"]
            rec[f"arm_b_2500|seed{s}|held_out_n4|I0|h{h}|head_to_head"] = abs(v - ref) <= TOL_ARM
            if abs(v - ref) > TOL_ARM:
                bad.append(f"arm_b 2500 seed {s} h={h}: {v} against head_to_head {ref}")
        v = float(traj_means(runs[("arm_b_10000", s)]["held_out_n4"]["I0"], 100).mean())
        ref = D1["100"]["B"]["per_seed"][str(s)]
        rec[f"arm_b_10000|seed{s}|held_out_n4|I0|h100|task_d1"] = abs(v - ref) <= TOL_ARM
        if abs(v - ref) > TOL_ARM:
            bad.append(f"arm_b 10000 seed {s} h=100: {v} against task_d1 {ref}")
    for h in (1, 8, 100):
        v = float(traj_means(runs[("released", None)]["held_out_n4"]["I0"], h).mean())
        ref = HH["released"]["per_model"]["released_ckpt_ens5"][str(h)]["l1"]
        rec[f"released|held_out_n4|I0|h{h}|head_to_head"] = abs(v - ref) <= TOL_ARM
        if abs(v - ref) > TOL_ARM:
            bad.append(f"released h={h}: {v} against head_to_head {ref}")
    return {"passed": not bad, "n_checks": len(rec), "failures": bad, "checks": rec}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--assert-only", action="store_true")
    args = ap.parse_args()
    log = lambda s: print(s, flush=True)
    os.chdir(ROOT)                                        # the weights and results paths are repository-relative
    st = self_test()
    if args.self_test:
        return
    paths, cfg, data, ep, split, scale, arenas, mk, norm = setting()
    for s in SEEDS:                                       # the 10k runs' 2,500 checkpoints are the 2,500 runs'
        for arm in ("A", "B"):
            assert sha256(f"runs/arm{arm}_seed{s}_10k/weights_2500.pt") == sha256(f"runs/arm{arm}_seed{s}/weights_2500.pt")
    me = sha256(os.path.abspath(__file__))
    if not args.assert_only:
        reg = ledger_hashes(open("FINDINGS_LEDGER.md", encoding="utf-8").read())
        assert reg, f"no ledger entry {RULE_ID} records a SHA-256: the rule is not pre-registered"
        assert me in reg, f"this script ({me}) is not the one {RULE_ID} pre-registered ({reg})"
    cpu_start, wall_start = time.process_time(), time.time()
    log("phase 1: I0 and I1" + (" (assert-only: the cases committed artifacts hold)" if args.assert_only else ""))
    runs, p1 = phase1(paths, cfg, data, scale, arenas, mk, args.assert_only, log)
    a = assertion_a(runs, scale, arenas, args.assert_only)
    log(f"assertion (a): {'PASS' if a['passed'] else 'FAIL'} — {a['n_checks']} comparisons" +
        ("" if a["passed"] else "; " + "; ".join(a["failures"][:5])))
    if args.assert_only:
        sys.exit(0 if a["passed"] else 1)
    b, c = {}, {}
    nm = lambda tag: tag[0] if tag[1] is None else f"{tag[0]}|seed{tag[1]}"
    for tag, by_ar in runs.items():
        for ar, by_i in by_ar.items():
            b[f"{nm(tag)}|{ar}"] = check_b(by_i["I0"], by_i["I1_stale"])
            c[f"{nm(tag)}|{ar}|I0"] = check_c(by_i["I0"])
    b_ok = all(b_passes(v) for v in b.values())
    log(f"assertion (b): {'PASS' if b_ok else 'FAIL'}; assertion (c) on I0: {'PASS' if all(c.values()) else 'FAIL'}")
    if not (a["passed"] and b_ok and all(c.values())):
        blocked("an assertion failed before any reading", a=a, b=b, c=c)

    # ---- phase 2: I2-I4, then every measure
    Zs = {ar: np.random.default_rng(NOISE_SEED).standard_normal((NOISE_DRAWS, len(st_), F1 - F0, 12))
          for ar, st_ in arenas.items()}
    cpu2, proj2 = time.process_time(), None
    plan = model_plan()
    sums = {}
    for k, spec in enumerate(plan):
        model = load(paths, cfg, spec["kind"], spec["it"], spec["seed"])
        hook = Hook(model)
        tag = (spec["key"], spec["seed"])
        sums[tag] = {}
        for ar in spec["arenas"]:
            idx = mk(arenas[ar])
            r0 = runs[tag][ar]["I0"]
            sums[tag][ar] = {"I0": [summarise(r0, r0)], "I1_stale": [summarise(runs[tag][ar]["I1_stale"], r0)]}
            for iname, pairs in interventions(spec["norm"], norm, Zs[ar]).items():
                ok, ss = True, []
                for f, ex in pairs:
                    x = hook.run(data, cfg, idx, 1, f)
                    ok &= check_c(r0, x, ex(x["true_ac"]))
                    # the per-trajectory route equals alignment_defect_ci.stats() on the runs that carry the readings too
                    ok &= all(abs(traj_means(x, h).mean() - adc_rel(x, scale, h)) <= 1e-12 for h in HORIZONS)
                    ss.append(summarise(x, r0))
                c[f"{nm(tag)}|{ar}|{iname}"] = ok
                sums[tag][ar][iname] = ss
        del runs[tag]
        if k == 0:
            per = (time.process_time() - cpu2) / (2 * NOISE_DRAWS + 2) / sum(len(arenas[a]) for a in spec["arenas"])
            rest = sum(len(arenas[a]) for s_ in plan[1:] for a in s_["arenas"]) * (2 * NOISE_DRAWS + 2)
            proj2 = (time.process_time() - cpu_start + per * rest) / 60
            log(f"  projection after the first model (phase 2): {proj2:.1f} CPU-min in all (cap {CAP_CPU_MIN:.0f})")
            if proj2 > CAP_CPU_MIN:
                blocked("projected CPU exceeds the cap after the first model of phase 2", projection_cpu_min=proj2)
    if not all(c.values()):
        blocked("assertion (c), or the statistic check, failed on I2-I4", c=c)
    log("assertion (c) on I2-I4: PASS")

    # ---- the measures
    results, per_seed = {}, {}
    for key in dict.fromkeys(s_["key"] for s_ in plan):
        tags = [t for t in sums if t[0] == key]
        results[key] = {}
        for ar in sums[tags[0]]:
            D = draws_for(len(arenas[ar]))
            results[key][ar] = {}
            for h in HORIZONS:
                c0 = [sums[t][ar]["I0"][0]["c"][h] for t in tags]
                cell = {}
                for iname in INTERVENTIONS:
                    ri = [sums[t][ar][iname] for t in tags]
                    cint = [np.mean([x["c"][h] for x in xs], axis=0) for xs in ri]   # mean over the draws
                    p, ci, _ = e_with_ci(cint, c0, D)
                    dl = float(np.mean([np.mean([x["delta"][h] for x in xs]) for xs in ri]))
                    cell[iname] = {"E_pct": p, "ci95_pct": ci, "delta": dl}
                    for t, cs, cr in zip(tags, cint, c0):
                        ps = per_seed.setdefault(f"{nm(t)}|{ar}|h{h}", {"I0_per_trajectory_err": cr.tolist()})
                        ps[iname] = {"E_pct": float(100 * (cs.mean() / cr.mean() - 1)),
                                     "per_trajectory_err": cs.tolist()}
                results[key][ar][str(h)] = cell
    ctx = {}
    for ar, st_ in arenas.items():
        acn = torch.as_tensor(data[mk(st_)][:, :, R.ACTION_COLS], dtype=torch.float32)
        ctx[ar] = context(acn, t_swap(acn))
    readings, alongside = {}, {}
    for key in READING["models"]:
        x = results[key][READING["arena"]][str(READING["h"])][READING["intervention"]]
        readings[key] = {"E_pct": x["E_pct"], "ci95_pct": x["ci95_pct"], "reading": label(x["E_pct"], *x["ci95_pct"]),
                         "interval_excludes_zero": bool(x["ci95_pct"][0] > 0 or x["ci95_pct"][1] < 0),
                         "point_at_least_threshold": bool(x["E_pct"] >= THRESHOLD_PCT)}
    for key, ar in READING["alongside"].items():
        x = results[key][ar][str(READING["h"])][READING["intervention"]]
        alongside[key] = {"arena": ar, "E_pct": x["E_pct"], "ci95_pct": x["ci95_pct"],
                          "label_it_would_carry": label(x["E_pct"], *x["ci95_pct"]),
                          "interval_excludes_zero": bool(x["ci95_pct"][0] > 0 or x["ci95_pct"][1] < 0),
                          "status": "alongside, not a reading"}
    cpu = {"phase1_cpu_s": p1["cpu_s"], "total_cpu_s": time.process_time() - cpu_start,
           "total_wall_s": time.time() - wall_start, "projection_after_first_model_cpu_min": {
               "phase1": p1["projection_cpu_min"], "phase2": proj2}, "cap_cpu_min": CAP_CPU_MIN}
    out = {
        "rule": "X2", "ledger": RULE_ID, "script": "scripts/action_sensitivity.py", "script_sha256": me,
        "exploratory": True, "never_reopens": ["M-23", "M-64", "M-74", "M-75", "M-76"],
        "statistic": "E = err(I) / err(I0) - 1, percent; relative-L1 cumulative over forecast steps 1..h "
                     "(alignment_defect_ci.stats); three-seed mean of per-seed E for arm_a and arm_b",
        "interval": "percentiles 2.5/97.5 over whole-trajectory resamples, one resample for all seeds and both "
                    "interventions per draw: exact 256 at n = 4; 20,000 Monte Carlo draws, default_rng(0), at n = 16, 20",
        "forecast_rows_read_under_offset_1": {
            "rows": [F0, F1 - 1],
            "code": a_in_lines(),
            "checked_by": "assertion (c): under I0 the first step receives the data's rows 1..32 and forecast step j row 32 + j"},
        "arenas": {ar: {"starts": st_, "n_independent": len(st_)} for ar, st_ in arenas.items()},
        "models": {"arm_a": WEIGHTS.replace("{arm}", "A"), "arm_b": WEIGHTS.replace("{arm}", "B"),
                   "released": "setup.sh's pretrain_rnn_ens.pt", "seeds": list(SEEDS), "checkpoints": list(CHECKPOINTS)},
        "interventions": {"I0": "offset 1 (reference)", "I1_stale": "offset 0", "I2_swap": "trajectory i takes (i+1) mod n's forecast-row actions",
                          "I3_mean": "per-dimension mean over the model's training rows",
                          "I4_noise_k0.1": "true + N(0, (0.1 sigma)^2), 8 draws, default_rng(0)",
                          "I4_noise_k0.5": "true + N(0, (0.5 sigma)^2), 8 draws, default_rng(0)"},
        "training_rows": {"arm": "every row of the eight training episodes", "released": "every row of all ten episodes",
                          "mean": {k: v[0].tolist() for k, v in norm.items()}, "sigma": {k: v[1].tolist() for k, v in norm.items()}},
        "self_test": {"synthetic": True, "note": "untrained weights on synthetic data; not a reading of any trained model",
                      "cases": {k: {kk: vv for kk, vv in v.items() if kk != "b"} for k, v in st.items()}},
        "code_sha256": {p: sha256(p) for p in MODULES},
        "git_head": os.popen("git rev-parse HEAD").read().strip(),
        "torch_threads": torch.get_num_threads(),
        "context_definition": "over each arena's forecast rows 32..399: the fraction of steps with a_t != a_(t-1) in any "
                              "dimension; mean |a_t - a_(t-1)| / mean |a_t - abar|; mean |a_swap,t - a_t| / mean |a_t - abar|; "
                              "abar the per-dimension mean over the arena's forecast rows; actions raw, as fed",
        "assertions": {"a": a, "b": b, "c": c},
        "context": ctx,
        "results": results,
        "per_seed": per_seed,
        "readings": readings,
        "alongside": alongside,
        "reading_rule": {"statistic": "E under I2_swap, h = 8, in_sample_n16, three-seed mean, arm_a at 2,500 and at 10,000",
                         "outcomes": ["RESPONDS TO THE ACTION: lower bound > 0 and point >= +10%",
                                      "ERROR FALLS WITH WRONG ACTIONS: upper bound < 0",
                                      "DOES NOT RESPOND MEASURABLY: upper bound < +10%", "UNRESOLVED: otherwise"]},
        "cpu": cpu,
    }
    json.dump(out, open(OUT, "w"), indent=1)
    log("=" * 96)
    log("RULE X2 — do our models respond to the action?  (E under swap, h = 8, in-sample, three-seed mean)")
    for k, v in readings.items():
        log(f"  READING  {k:12s} E = {v['E_pct']:+8.2f}% [{v['ci95_pct'][0]:+8.2f}, {v['ci95_pct'][1]:+8.2f}]  -> {v['reading']}")
    for k, v in alongside.items():
        log(f"  alongside {k:11s} E = {v['E_pct']:+8.2f}% [{v['ci95_pct'][0]:+8.2f}, {v['ci95_pct'][1]:+8.2f}]  "
            f"({v['arena']}; would carry {v['label_it_would_carry']})")
    log(f"  CPU {cpu['total_cpu_s'] / 60:.1f} min, wall {cpu['total_wall_s'] / 60:.1f} min; wrote {R.rel(OUT)}")


if __name__ == "__main__":
    main()
