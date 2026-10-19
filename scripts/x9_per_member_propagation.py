"""
Rule X9 (round 5; PRE-REGISTERED, inference only) -- does propagating each ensemble member on its own predictions make
the spread track accumulated error? And, with --x11e, rule X11e: the same on X3's folds' ensemble-5 arms (GT2).

The rule is docs/presubmission/round5/PROTOCOLS.md §2 (X9) and §4.2 (X11e); this docstring is a summary of it.
It never re-opens a discharged rule, and nothing it returns changes a verdict.

TWO MODES. MEAN is the release's evaluation path (system_dynamics.py:112-115, model_ids=None): every member receives
the ensemble mean through its recurrent state. It is computed by calling the existing functions UNCHANGED --
ReferenceRWM.rollout_uncertainty (score_reference.py:127-156) for a shared-trunk model and
r2_independent_ensemble.rollout_independent (:64-107) for independent members. PER-MEMBER (TS-infinity, Chua et al.
2018): member k receives its own previous prediction after the first forecast step, through its own recurrent state;
a shared trunk is run once per member on that member's input, at MEAN's batch shape. step_heads() is
ReferenceRWM.step's lines 94-105 verbatim, returning the per-head means and sigmas instead of their mean. The release's
imagination path (one member per environment, envs/base.py:54,68,142) is not tested.

MODELS AND ARENAS. (a) rel: the released checkpoint on all ten episodes' 20 trajectories (one batch of 20; in-sample
only if it trained on this recording, PREMISES P20). (b) e5: Arm A ensemble-5 seeds 0-2 on the held-out pair (batch 4).
(c) ind: Arm A single models seeds 0-4 as an independent ensemble on the held-out pair; (c3) ind3: seeds 0-2.
(d) fold: per X3 fold, its Arm A seeds 0-2 as a three-member independent ensemble on its own held-out pair, inputs built
by mn_sweep_eval's window_arrays and _pairing, one batch of 4 per fold, pooled to 20. X11e: per fold, its three
ensemble-5 arms on its held-out pair, pooled as (b), n = 20.

STATISTICS, h in {1, 8, 32, 100, 128, 368}, cumulative over forecast steps 1..h, pooled over (trajectory, step,
dimension): e = |members' mean - truth|, s = the across-member standard deviation (ddof = 1); rho = mean e / mean s;
+-1 and +-2 sigma coverage; Gaussian CRPS and NLL with scale s; elements with s <= 0 or non-finite excluded and counted.
f = ln(rho_MEAN / rho_PER) / ln(rho_MEAN / sqrt(2/pi)). Intervals: n = 20, a paired bootstrap over trajectories
(default_rng(0), 20,000 draws); n = 4, the exact sign-flip test over 16 sign vectors. VERDICT at h = 100: PROPAGATION
CLOSES THE GAP / NARROWS THE GAP / WIDENS THE GAP / NO CLEAR CHANGE (PROTOCOLS §2.5).

ASSERTIONS, before any per-member number beyond forecast step 1: (i) MEAN reproduces task_d_nind20.json and
m65_gaussian_nominal.json for (a), task_d3_ens5.json for (b), r2_independent_ensemble.json for (c), relative 1e-6;
(ii) the modes agree exactly (0.0) at forecast step 1; (iii) for (d), each fold member alone through the PER-MEMBER
code reproduces our trainer's rollout to < 1e-5 and x3_cross_fold.json's per-trajectory relative-L1 to 1e-5;
(iv) inputs: the trajectory sets, the weights' SHA-256s, finiteness, s > 0.

  --assert-only   (i)-(iv) only, and print pass or fail; no per-member number.
  --x11e          rule X11e (GT2): needs X11's fold ensemble-5 runs.
Writes results/x9_per_member_propagation.json (X9) or results/x11e_fold_e5_propagation.json (X11e).
Run from the repository root.
"""
import argparse
import json
import math
import os
import subprocess
import sys
import time
import warnings

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import torch  # noqa: E402
from torch import nn  # noqa: E402
import rwm_data as R  # noqa: E402
import rollout_eval as E  # noqa: E402
import rwm_metrics as MET  # noqa: E402
import score_reference as S  # noqa: E402
import mn_sweep_eval as MN  # noqa: E402
import task_d_nind20 as TDN  # noqa: E402
import r2_independent_ensemble as R2  # noqa: E402
import x11_common as C  # noqa: E402
import x11a_fold_ens5_calibration as XA  # noqa: E402

RULE_ID, RULE_ID_X11E = "M-101", "M-103"
FROZEN = ("scripts/x9_per_member_propagation.py", "scripts/x11a_fold_ens5_calibration.py", "scripts/x11_common.py")
HORIZONS = (1, 8, 32, 100, 128, 368)
H_VERDICT = 100
START, LEN, N_BOOT = E.START_STEP, 400, 20000
CALIB = json.load(open(os.path.join(R.RESULTS, "m65_gaussian_nominal.json")))["calibrated_ratio_sqrt_2_over_pi"]
BAND = tuple(json.load(open(os.path.join(R.RESULTS, "x7_loeo_recalibration.json")))["design"]["band"])
TOL_I, TOL_III_PRED, TOL_III_L1 = 1e-6, 1e-5, 1e-5
LABELS = ("PROPAGATION CLOSES THE GAP", "PROPAGATION NARROWS THE GAP", "PROPAGATION WIDENS THE GAP", "NO CLEAR CHANGE")
OUT = os.path.join(R.RESULTS, "x9_per_member_propagation.json")
OUT_X11E = os.path.join(R.RESULTS, "x11e_fold_e5_propagation.json")
MODULES = FROZEN + ("src/score_reference.py", "scripts/r2_independent_ensemble.py", "scripts/task_d_nind20.py",
                    "scripts/mn_sweep_eval.py", "scripts/x3_cross_fold.py", "scripts/task_d3_ens5.py",
                    "src/rwm_data.py", "src/rwm_metrics.py", "src/rollout_eval.py", "src/rwm_model.py")
SCOPE = ("Per-member propagation is not the released method. MEAN tests \"effectively propagated\" as the release's "
         "evaluation path does it; PER-MEMBER asks whether the ensemble's information would propagate if the members "
         "were rolled out separately. The release's imagination path, which propagates one member per environment, "
         "is not tested.")


# ------------------------------------------------------------------ rollouts
@torch.no_grad()
def step_heads(m, state_seq, action_seq, h_state):
    """ReferenceRWM.step, score_reference.py:94-105 verbatim; returns per-head means and sigmas, (E, B, 45) each."""
    x = torch.cat([state_seq, action_seq], dim=-1)
    out, h_state = m.state_base(x, h_state)
    h = out[:, -1]
    last = state_seq[:, -1]

    means = torch.stack([mm(h) + last for mm in m.state_mean_layers])
    logstd = torch.stack([mm(h) for mm in m.state_logstd_layers])
    mx = m.state_min_logstd + torch.exp(m.state_log_delta_logstd)
    logstd = mx - nn.functional.softplus(mx - logstd)
    logstd = m.state_min_logstd + nn.functional.softplus(
        logstd - m.state_min_logstd)
    stds = torch.exp(logstd)
    return means, stds, h_state


def _inputs(pred, action, i, start_step, action_offset):
    """score_reference.py:142-149, the index arithmetic of every existing rollout."""
    if i > start_step:
        s_in = pred[:, i - 1:i]
        a_in = action[:, i - 1 + action_offset:i + action_offset]
    else:
        s_in = pred[:, i - start_step:i]
        a_in = action[:, i - start_step + action_offset:i + action_offset]
    if a_in.shape[1] != s_in.shape[1]:
        a_in = action[:, -s_in.shape[1]:]
    return s_in, a_in


@torch.no_grad()
def per_member_shared(m, state, action, start_step=START, action_offset=1, stop=None):
    """PER-MEMBER for a shared trunk: member k is head k on its own trunk pass and hidden state."""
    B, T, D = state.shape
    T = T if stop is None else stop
    K = m.ensemble
    preds = [state.clone() for _ in range(K)]
    acc = _Acc(state)
    hs = [None] * K
    for i in range(start_step, T):
        mu, sg = [], []
        for k in range(K):
            s_in, a_in = _inputs(preds[k], action, i, start_step, action_offset)
            means, stds, hs[k] = step_heads(m, s_in, a_in, hs[k])
            preds[k][:, i] = means[k]
            mu.append(means[k])
            sg.append(stds[k])
        acc.put(i, mu, sg)
    return acc


@torch.no_grad()
def per_member_indep(models, state, action, start_step=START, action_offset=1, stop=None):
    """PER-MEMBER for independent models: each model's own prediction fed back to it, its own hidden state."""
    B, T, D = state.shape
    T = T if stop is None else stop
    preds = [state.clone() for _ in models]
    acc = _Acc(state)
    h, ha = [None] * len(models), [None] * len(models)
    warnings.filterwarnings("ignore", message="std\\(\\): degrees of freedom is <= 0")
    for i in range(start_step, T):
        mus, sgs = [], []
        for j, m in enumerate(models):
            s_in, a_in = _inputs(preds[j], action, i, start_step, action_offset)
            mu, _, _, _, h[j], ha[j] = m.step(s_in, a_in, h[j], ha[j], False)
            preds[j][:, i] = mu
            mus.append(mu)
            sgs.append(m.last_sigma)
        acc.put(i, mus, sgs)
    acc.members = torch.stack(preds)
    return acc


def mean_shared(m, st, ac):
    pred, alea, epi, _, _ = m.rollout_uncertainty(st.clone(), ac, START, action_offset=1)
    return {"err": (pred - st).abs().numpy().astype(np.float64), "s": epi.numpy().astype(np.float64),
            "alea": alea.numpy().astype(np.float64), "pred": pred}


def mean_indep(models, st, ac):
    pred, alea, epi, _, _ = R2.rollout_independent(models, st.clone(), ac)
    return {"err": (pred - st).abs().numpy().astype(np.float64), "s": epi.numpy().astype(np.float64),
            "alea": alea.numpy().astype(np.float64), "pred": pred}


class _Acc:
    """Per step, the members' mean, spread (ddof = 1) and mean sigma, each from torch.stack of that step's (B, 45)
    member tensors -- MEAN's own operation (r2_independent_ensemble.py:100-104; score_reference.py:99, 121), so that
    float32 rounding matches MEAN's exactly (PROTOCOLS §2.2; DECISIONS.md#G3-assert-ii)."""
    def __init__(self, state):
        self.ybar = state.clone()
        self.s = torch.zeros_like(state)
        self.alea = torch.zeros_like(state)
        self.members = None

    def put(self, i, mus, sgs):
        M = torch.stack(mus)
        self.ybar[:, i] = M.mean(0)
        self.s[:, i] = M.std(0)
        self.alea[:, i] = torch.stack(sgs).mean(0)


def from_members(acc, st):
    """A per-member rollout -> the members' mean, its error, the across-member spread (ddof = 1), the mean sigma."""
    return {"err": (acc.ybar - st).abs().numpy().astype(np.float64), "s": acc.s.numpy().astype(np.float64),
            "alea": acc.alea.numpy().astype(np.float64), "pred": acc.ybar}


# ------------------------------------------------------------------ statistics
def phi_cdf(z):
    return 0.5 * (1.0 + torch.special.erf(torch.from_numpy(z) / math.sqrt(2.0)).numpy())


def cell(r, h):
    """PROTOCOLS §2.3 at horizon h: pooled values and per-trajectory means over the valid elements."""
    sl = slice(START, START + h)
    # C-contiguous copies, so that numpy reduces every mode's arrays in the same order (DECISIONS.md#G3-assert-ii)
    e, s, a = (np.ascontiguousarray(r[k][:, sl]) for k in ("err", "s", "alea"))
    v = np.isfinite(s) & (s > 0) & np.isfinite(e)
    z = np.where(v, e / np.where(v, s, 1.0), 0.0)
    crps = np.where(v, s * (z * (2 * phi_cdf(z) - 1) + 2 * np.exp(-0.5 * z * z) / math.sqrt(2 * math.pi)
                            - 1 / math.sqrt(math.pi)), np.nan)
    nll = np.where(v, 0.5 * np.log(2 * math.pi * np.where(v, s, 1.0) ** 2) + 0.5 * z * z, np.nan)
    ev, sv = np.where(v, e, np.nan), np.where(v, s, np.nan)
    ax = (1, 2)
    pt = {"e": np.nanmean(ev, axis=ax), "s": np.nanmean(sv, axis=ax),
          "cov1": np.nanmean(np.where(v, e <= s, np.nan), axis=ax),
          "cov2": np.nanmean(np.where(v, e <= 2 * s, np.nan), axis=ax),
          "crps": np.nanmean(crps, axis=ax), "nll": np.nanmean(nll, axis=ax)}
    pt["rho"] = pt["e"] / pt["s"]
    pooled = {"rho": float(np.nanmean(ev) / np.nanmean(sv)), "coverage_pm1": float(np.nanmean(np.where(v, e <= s, np.nan))),
              "coverage_pm2": float(np.nanmean(np.where(v, e <= 2 * s, np.nan))), "crps": float(np.nanmean(crps)),
              "nll": float(np.nanmean(nll)), "mean_abs_err": float(np.nanmean(ev)), "mean_sigma": float(np.nanmean(sv)),
              "alea_mean": float(np.nanmean(np.where(v, a, np.nan))), "n_excluded": int((~v).sum()),
              "n_elements": int(v.size)}
    return pooled, pt


def f_of(rm, rp):
    if not (np.isfinite(rm) and np.isfinite(rp)) or rm <= CALIB or rp <= 0:
        return float("nan")
    return float(math.log(rm / rp) / math.log(rm / CALIB))


def sign_flip(d):
    d = np.asarray(d, dtype=np.float64)
    n = len(d)
    T = float(d.mean())
    eps = np.array([[1 if (b >> j) & 1 else -1 for j in range(n)] for b in range(2 ** n)], dtype=np.float64)
    stats = np.abs((eps * d).mean(1))
    return {"T": T, "p": float((stats >= abs(T) - 1e-12).sum() / 2 ** n), "k_positive": int((d > 0).sum()),
            "k_negative": int((d < 0).sum()), "n": n, "p_min": 2.0 / 2 ** n}


def pct(x):
    x = x[np.isfinite(x)]
    return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))], int(len(x))


def in_band(x):
    return BAND[0] <= x <= BAND[1]


def summarise(mean_runs, per_runs, n):
    """mean_runs / per_runs: a list of per-seed rollout dicts (one entry when there are no seeds). Returns the
    pooled table by horizon and mode, per-trajectory values (seed-averaged), f, intervals or tests, the verdict."""
    out = {}
    draws = np.random.default_rng(0).integers(0, n, (N_BOOT, n)) if n == 20 else None
    for h in HORIZONS:
        modes = {}
        for name, runs in (("mean", mean_runs), ("per", per_runs)):
            cells = [cell(r, h) for r in runs]
            pooled = {k: float(np.mean([c[0][k] for c in cells])) for k in cells[0][0]}
            pooled["per_seed"] = [c[0] for c in cells] if len(cells) > 1 else None
            modes[name] = {"pooled": pooled, "pt_seeds": [c[1] for c in cells]}
        rm, rp = modes["mean"]["pooled"]["rho"], modes["per"]["pooled"]["rho"]
        rec = {"mean": modes["mean"]["pooled"], "per": modes["per"]["pooled"], "f": f_of(rm, rp)}
        # per trajectory: per seed, then averaged over seeds
        f_t = np.mean([[f_of(a, b) for a, b in zip(pm["rho"], pp["rho"])]
                       for pm, pp in zip(modes["mean"]["pt_seeds"], modes["per"]["pt_seeds"])], 0)
        lr_t = np.mean([np.log(pm["rho"] / pp["rho"]) for pm, pp in zip(modes["mean"]["pt_seeds"], modes["per"]["pt_seeds"])], 0)
        c1_t = np.mean([pp["cov1"] for pp in modes["per"]["pt_seeds"]], 0)
        rec["per_trajectory"] = {"f": f_t.tolist(), "log_ratio": lr_t.tolist(), "per_cov1": c1_t.tolist(),
                                 "mean_rho": np.mean([p["rho"] for p in modes["mean"]["pt_seeds"]], 0).tolist(),
                                 "per_rho": np.mean([p["rho"] for p in modes["per"]["pt_seeds"]], 0).tolist()}
        if len(modes["mean"]["pt_seeds"]) > 1:
            rec["per_trajectory"]["f_per_seed"] = [[f_of(a, b) for a, b in zip(pm["rho"], pp["rho"])]
                                                  for pm, pp in zip(modes["mean"]["pt_seeds"], modes["per"]["pt_seeds"])]
        if n == 20:
            sm = lambda mode, k: np.mean([p[k] for p in modes[mode]["pt_seeds"]], 0)
            rM = sm("mean", "e")[draws].mean(1) / sm("mean", "s")[draws].mean(1)
            rP = sm("per", "e")[draws].mean(1) / sm("per", "s")[draws].mean(1)
            with np.errstate(divide="ignore", invalid="ignore"):
                fd = np.where((rM > CALIB) & (rP > 0), np.log(rM / rP) / np.log(rM / CALIB), np.nan)
            ci_f, nf = pct(fd)
            rec["intervals"] = {
                "f_ci": ci_f, "f_n_finite": nf,
                "mean_rho_ci": pct(rM)[0], "per_rho_ci": pct(rP)[0],
                "mean_cov1_ci": pct(sm("mean", "cov1")[draws].mean(1))[0],
                "per_cov1_ci": pct(sm("per", "cov1")[draws].mean(1))[0],
                "crps_diff_per_minus_mean_ci": pct((sm("per", "crps") - sm("mean", "crps"))[draws].mean(1))[0],
                "nll_diff_per_minus_mean_ci": pct((sm("per", "nll") - sm("mean", "nll"))[draws].mean(1))[0],
                "bootstrap": "paired, whole trajectories, default_rng(0), 20000 draws; seeds pooled inside each draw"}
        else:
            rec["tests"] = {"f": sign_flip(f_t), "log_ratio": sign_flip(lr_t)}
            if "f_per_seed" in rec["per_trajectory"]:
                rec["tests"]["k_of_4_per_seed"] = [int((np.asarray(x) > 0).sum()) for x in rec["per_trajectory"]["f_per_seed"]]
        out[str(h)] = rec
    return out


def verdict(tab, n):
    r = tab[str(H_VERDICT)]
    f = r["f"]
    if n == 20:
        ci = r["intervals"]["per_cov1_ci"]
        if BAND[0] <= ci[0] and ci[1] <= BAND[1]:
            return LABELS[0], "per-member +-1 sigma coverage interval inside X7's band"
        if not np.isfinite(f):
            return LABELS[3], "f undefined"
        if r["intervals"]["f_n_finite"] < 19000:
            return LABELS[3], f"only {r['intervals']['f_n_finite']} of 20000 draws of f finite"
        lo, hi = r["intervals"]["f_ci"]
        if lo > 0:
            return LABELS[1], "f's paired interval lies above 0"
        if hi < 0:
            return LABELS[2], "f's paired interval lies below 0"
        return LABELS[3], "f's interval spans 0"
    pc = r["per"]["coverage_pm1"]
    if in_band(pc) and all(in_band(x) for x in r["per_trajectory"]["per_cov1"]):
        return LABELS[0], "pooled and all four per-trajectory per-member coverages inside X7's band"
    if not np.isfinite(f):
        return LABELS[3], "f undefined"
    ft = r["per_trajectory"]["f"]
    if all(x > 0 for x in ft):
        return LABELS[1], f"f > 0 on 4 of 4 trajectories (exact p = {r['tests']['f']['p']})"
    if all(x < 0 for x in ft):
        return LABELS[2], f"f < 0 on 4 of 4 trajectories (exact p = {r['tests']['f']['p']})"
    return LABELS[3], f"f > 0 on {sum(x > 0 for x in ft)} of 4"


# ------------------------------------------------------------------ arenas and models
def released():
    sd = torch.load(R.repo_paths()["ckpt"], map_location="cpu")["system_dynamics_state_dict"]
    m = S.ReferenceRWM(sd)
    m.eval()
    return m


def arenas():
    """(a)'s 20 starts as task_d_nind20.py:155-163, (b)/(c)'s 4 as task_d3_ens5.py:82-88, X10's 16 for assertion (iv)."""
    cfg, data, ep = C.data()
    split = E.make_split(seed=0, strat_path=C.STRAT, verbose=False)
    allep = sorted(set(split["train_episodes"]) | set(split["holdout_episodes"]))
    s20 = MET.non_overlapping_starts(ep, allep, LEN)
    s4 = MET.non_overlapping_starts(ep, list(split["holdout_episodes"]), LEN)
    s16 = MET.non_overlapping_starts(ep, sorted(split["train_episodes"]), LEN)
    return s20, s4, s16


def fold_inputs(fold):
    """mn_sweep_eval.score's input construction (:105-108) for a fold's held-out pair."""
    cfg, data, ep = C.data()
    ar = MN.arena(ep, list(fold), 32)
    st, ac = MN._pairing(MN.window_arrays(data, cfg, ar["starts"], 32, 32), 1)
    return ar, torch.as_tensor(st), torch.as_tensor(ac)


def max_rel(pairs):
    d = 0.0
    for got, want in pairs:
        if want is None or got is None:
            if want != got:
                return float("inf")
            continue
        d = max(d, abs(float(got) - float(want)) / max(1e-12, abs(float(want))))
    return d


# ------------------------------------------------------------------ X9
def x9(assert_only):
    t0 = time.perf_counter()
    frozen = None if assert_only else C.require_prereg(RULE_ID, FROZEN, OUT)
    s20, s4, s16 = arenas()
    st20, ac20 = C.tensors(s20)
    st4, ac4 = C.tensors(s4)
    A = {}
    sha = {}
    asr = {}

    # ---------------- MEAN, and assertion (i) ----------------
    rel = released()
    sha["released"] = C.sha256(R.repo_paths()["ckpt"])
    mean_a = mean_shared(rel, st20, ac20)
    tdn = json.load(open(os.path.join(R.RESULTS, "task_d_nind20.json")))["d1_by_horizon"]
    m65 = json.load(open(os.path.join(R.RESULTS, "m65_gaussian_nominal.json")))["cases"][
        "released_ckpt_ens5 [epistemic] all ten episodes"]["by_horizon"]
    pa = []
    for h in HORIZONS:
        sl = slice(START, START + h)
        b = TDN.block(mean_a["err"][:, sl], mean_a["s"][:, sl], rng=np.random.default_rng(0))
        w = tdn[str(h)]["epistemic"]
        for k in ("ratio_err_over_sigma", "coverage_pm1", "coverage_pm2", "mean_sigma", "mean_abs_err"):
            pa.append((b[k], w[k]))
        for k in ("ratio_err_over_sigma_ci", "coverage_pm1_ci", "coverage_pm2_ci"):
            pa += list(zip(b[k], w[k]))
        pa.append((b["ratio_err_over_sigma"], m65[str(h)]["rho_err_over_sigma"]))
        pa.append((b["coverage_pm1"], m65[str(h)]["coverage_pm1_observed_pct"] / 100))
    asr["i_a"] = max_rel(pa)

    e5 = {}
    for s in C.ENS5_SEEDS:
        w = C.ens5_weights((1, 8), s)
        sha[f"e5_s{s}"] = C.sha256(w)
        e5[s] = C.load_ens5(w)[0]
    mean_b = {s: mean_shared(e5[s], st4, ac4) for s in C.ENS5_SEEDS}
    got = XA.strip(XA.calibration({s: {"err": mean_b[s]["err"], "epi": mean_b[s]["s"]} for s in C.ENS5_SEEDS},
                                  np.random.default_rng(0).integers(0, 4, (N_BOOT, 4))))
    want = json.load(open(os.path.join(R.RESULTS, "task_d3_ens5.json")))["calibration"]
    pb = []
    for h in HORIZONS:
        g, w = got[str(h)], want[str(h)]
        for gs, ws in zip(g["per_seed"], w["per_seed"]):
            pb += [(gs[k], ws[k]) for k in ("ratio_err_over_sigma", "coverage_pm1", "coverage_pm2")]
        pb += [(g[k], w[k]) for k in ("mean_ratio", "mean_cov1", "mean_cov2")]
        for k in ("ratio_ci", "cov1_ci", "cov2_ci"):
            pb += list(zip(g[k], w[k]))
    asr["i_b"] = max_rel(pb)

    ind = {}
    for s in C.SINGLE_SEEDS:
        w = C.single_weights((1, 8), s)
        sha[f"ind_s{s}"] = C.sha256(w)
        ind[s] = C.load_single(w)
    mean_c = mean_indep([ind[s] for s in C.SINGLE_SEEDS], st4, ac4)
    mean_c3 = mean_indep([ind[s] for s in (0, 1, 2)], st4, ac4)
    r2 = json.load(open(os.path.join(R.RESULTS, "r2_independent_ensemble.json")))["independent"]
    pc = []
    for h in HORIZONS:
        b = R2.block(mean_c["err"], mean_c["s"], slice(START, START + h))
        pc += [(b[k], r2[str(h)][k]) for k in ("ratio_err_over_sigma", "coverage_pm1", "coverage_pm2", "mean_sigma",
                                               "mean_abs_err")]
    asr["i_c"] = max_rel(pc)

    # ---------------- (d): MEAN, and assertion (iii) ----------------
    x3 = json.load(open(os.path.join(R.RESULTS, "x3_cross_fold.json")))
    cfg, data, ep = C.data()
    order, dfold, iii_pred, iii_l1, sha_mismatch = [], [], 0.0, 0.0, []
    for f in C.FOLDS:
        ar, st, ac = fold_inputs(f)
        order += list(zip([C.fid(f)] * 4, ar["starts"]))
        sp = C.split_of(f)
        scale = MET.training_scale(data, ep, sp["train_episodes"], cfg["state_data_mean"], cfg["state_data_std"])
        members = []
        for s in (0, 1, 2):
            w = C.single_weights(f, s)
            sha[f"fold{C.fid(f)}_s{s}"] = C.sha256(w)
            if sha[f"fold{C.fid(f)}_s{s}"] != x3["weights_sha256"][C.fid(f)][f"A{s}"]:
                sha_mismatch.append(w)
            m = C.load_single(w)
            members.append(m)
            p1 = per_member_indep([m], st, ac).members[0]
            own = X3load(cfg, w).rollout(st.clone(), ac, 32, action_offset=1)
            iii_pred = max(iii_pred, float((p1 - own).abs().max()))
            mt = MN.metrics((p1[:, 32:] - st[:, 32:]).numpy(), st[:, 32:].numpy(), scale)
            fi = C.FOLDS.index(f)
            for h in HORIZONS:
                for j in range(4):
                    iii_l1 = max(iii_l1, abs(mt[str(h)]["l1"][j] - x3["per_trajectory"]["armA_per_seed_l1"][str(h)][s][4 * fi + j]))
        dfold.append({"fold": f, "st": st, "ac": ac, "members": members, "mean": mean_indep(members, st, ac)})
    order_ok = ([a for a, _ in order] == x3["per_trajectory"]["fold"]
                and [b for _, b in order] == x3["per_trajectory"]["start_row"])
    asr["iii"] = {"pass": bool(order_ok and iii_pred < TOL_III_PRED and iii_l1 < TOL_III_L1 and not sha_mismatch),
                  "trajectory_order_matches": bool(order_ok), "max_abs_diff_prediction": iii_pred,
                  "max_abs_diff_rel_l1": iii_l1, "tolerances": [TOL_III_PRED, TOL_III_L1],
                  "weights_sha256_mismatch": sha_mismatch}

    # ---------------- assertion (ii): the modes at forecast step 1 ----------------
    stop = START + 1
    d2 = 0.0
    pairs2 = [("a", per_member_shared(rel, st20, ac20, stop=stop), mean_a, st20)]
    pairs2 += [(f"b{s}", per_member_shared(e5[s], st4, ac4, stop=stop), mean_b[s], st4) for s in C.ENS5_SEEDS]
    pairs2 += [("c", per_member_indep([ind[s] for s in C.SINGLE_SEEDS], st4, ac4, stop=stop), mean_c, st4),
               ("c3", per_member_indep([ind[s] for s in (0, 1, 2)], st4, ac4, stop=stop), mean_c3, st4)]
    pairs2 += [(f"d{C.fid(x['fold'])}", per_member_indep(x["members"], x["st"], x["ac"], stop=stop), x["mean"], x["st"])
               for x in dfold]
    for name, acc, mr, st in pairs2:
        pr = from_members(acc, st)
        d2 = max(d2, float((pr["pred"][:, START] - mr["pred"][:, START]).abs().max()),
                 float(np.abs(pr["s"][:, START] - mr["s"][:, START]).max()))
        pp, _ = cell(pr, 1)
        mm, _ = cell(mr, 1)
        d2 = max(d2, max(abs(pp[k] - mm[k]) for k in ("rho", "coverage_pm1", "coverage_pm2", "crps", "nll")))
    asr["ii"] = {"pass": bool(d2 == 0.0), "max_abs_diff": d2}

    # ---------------- assertion (iv): inputs ----------------
    fin = all(np.isfinite(r["err"][:, START:]).all() and np.isfinite(r["s"][:, START:]).all()
              for r in [mean_a, mean_c, mean_c3] + list(mean_b.values()) + [x["mean"] for x in dfold])
    spos = all((r["s"][:, START:] > 0).all() for r in [mean_a, mean_c, mean_c3] + list(mean_b.values())
               + [x["mean"] for x in dfold])
    sets = sorted(s20) == sorted(list(s4) + list(s16)) and len(s20) == 20 and len(s4) == 4 and len(s16) == 16
    asr["iv"] = {"pass": bool(fin and spos and sets and not sha_mismatch), "finite": bool(fin), "s_positive": bool(spos),
                 "trajectory_sets": bool(sets), "weights_sha256": sha}
    assertions = {"i": {"pass": bool(max(asr["i_a"], asr["i_b"], asr["i_c"]) <= TOL_I), "tolerance_relative": TOL_I,
                        "a_max_rel_diff": asr["i_a"], "b_max_rel_diff": asr["i_b"], "c_max_rel_diff": asr["i_c"],
                        "against": ["results/task_d_nind20.json d1_by_horizon[h].epistemic",
                                    "results/m65_gaussian_nominal.json released_ckpt_ens5 [epistemic] all ten episodes",
                                    "results/task_d3_ens5.json calibration", "results/r2_independent_ensemble.json independent"]},
                  "ii": asr["ii"], "iii": asr["iii"], "iv": asr["iv"]}
    for k, v in assertions.items():
        extra = {kk: vv for kk, vv in v.items() if kk not in ("pass", "weights_sha256", "against")}
        print(f"  assertion ({k}): {'PASS' if v['pass'] else 'FAIL'}  {extra}")
    ok = all(v["pass"] for v in assertions.values())
    if assert_only:
        sys.exit(0 if ok else 1)
    if not ok:
        C.blocked(OUT, "an assertion failed", assertions=assertions)

    # ---------------- PER-MEMBER (only after every assertion passed) ----------------
    timing = {}
    t = time.perf_counter()
    per_a = from_members(per_member_shared(rel, st20, ac20), st20)
    timing["a_per_member_s"] = time.perf_counter() - t
    t = time.perf_counter()
    per_b = {s: from_members(per_member_shared(e5[s], st4, ac4), st4) for s in C.ENS5_SEEDS}
    timing["b_per_member_s"] = time.perf_counter() - t
    per_c = from_members(per_member_indep([ind[s] for s in C.SINGLE_SEEDS], st4, ac4), st4)
    per_c3 = from_members(per_member_indep([ind[s] for s in (0, 1, 2)], st4, ac4), st4)
    per_d = [from_members(per_member_indep(x["members"], x["st"], x["ac"]), x["st"]) for x in dfold]
    for r in [per_a, per_c, per_c3] + list(per_b.values()) + per_d:
        if not (np.isfinite(r["err"][:, START:]).all() and np.isfinite(r["s"][:, START:]).all()):
            C.blocked(OUT, "non-finite per-member rollout")
    cat = lambda rs: {k: np.concatenate([r[k] for r in rs], 0) for k in ("err", "s", "alea")}
    tables = {"rel": summarise([mean_a], [per_a], 20),
              "e5": summarise([mean_b[s] for s in C.ENS5_SEEDS], [per_b[s] for s in C.ENS5_SEEDS], 4),
              "ind": summarise([mean_c], [per_c], 4), "ind3": summarise([mean_c3], [per_c3], 4),
              "fold": summarise([cat([x["mean"] for x in dfold])], [cat(per_d)], 20)}
    verdicts = {}
    for a, n in (("rel", 20), ("e5", 4), ("ind", 4), ("fold", 20)):
        lab, why = verdict(tables[a], n)
        verdicts[a] = {"label": lab, "reason": why, "h": H_VERDICT, "n": n, "descriptive": n == 4}
    alea_ratio = max(r[m]["alea_mean"] / r[m]["mean_abs_err"] for tb in tables.values() for r in tb.values()
                     for m in ("mean", "per"))
    out = {"rule": "X9", "ledger": RULE_ID, "frozen_sha256": frozen, "script": "scripts/x9_per_member_propagation.py",
           "script_sha256": C.sha256("scripts/x9_per_member_propagation.py"), "exploratory": True,
           "never_reopens": "any discharged rule; nothing here changes a verdict",
           "design": {"arenas": {"rel": "released checkpoint, all ten episodes, 20 trajectories, one batch of 20",
                                 "e5": "Arm A ensemble-5 seeds 0-2, held-out pair, 4 trajectories",
                                 "ind": "Arm A single models seeds 0-4 as an independent ensemble, held-out pair",
                                 "ind3": "the same, seeds 0-2 (reported beside ind; no verdict)",
                                 "fold": "per X3 fold, its Arm A seeds 0-2 as an independent ensemble, own held-out pair, pooled to 20"},
                      "fold_trajectories": [{"fold": a, "start_row": b} for a, b in order],
                      "modes": {"mean": "the release's evaluation path, existing functions unchanged",
                                "per": "PER-MEMBER (TS-infinity): each member fed its own prediction, own recurrent state"},
                      "horizons": list(HORIZONS), "verdict_horizon": H_VERDICT, "calibrated_rho": CALIB, "band": list(BAND),
                      "n_boot": N_BOOT, "action_offset": 1, "start_step": START},
           "assertions": assertions, "tables": tables, "verdict": verdicts, "alea_over_err_max": alea_ratio,
           "scope": SCOPE,
           "caveats": ["rel: all ten episodes, in-sample for the released checkpoint only if it trained on this recording "
                       "(PREMISES P20); no in-sample/held-out contrast is drawn from it",
                       "n = 4 results are descriptive: no n = 4 test can reach p < 0.125",
                       "ind3 and fold have three members; a small ensemble's spread is biased low"],
           "code_sha256": {p: C.sha256(p) for p in MODULES},
           "git_head": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
           "timing": {"wall_clock_s": time.perf_counter() - t0, **timing, "torch_threads": torch.get_num_threads(),
                      "cpu_count": os.cpu_count()}}
    json.dump(out, open(OUT, "w"), indent=1, default=float)
    for a, v in verdicts.items():
        r = tables[a][str(H_VERDICT)]
        print(f"  {a}: rho MEAN {r['mean']['rho']:.3f} PER {r['per']['rho']:.3f}, f {r['f']:.3f}, "
              f"cov1 PER {r['per']['coverage_pm1']:.4f} -> {v['label']}")
    print(f"  wrote {R.rel(OUT)}")


def X3load(cfg, w):
    import x3_cross_fold as X3
    return X3.load(cfg, w)


# ------------------------------------------------------------------ X11e (GT2)
def x11e():
    t0 = time.perf_counter()
    frozen = C.require_prereg(RULE_ID_X11E, FROZEN, OUT_X11E)
    bad = {f"{C.fid(f)}_s{s}": C.check_record(C.ens5_record(f, s), f, 5) for f in C.FOLDS for s in C.ENS5_SEEDS}
    bad = {k: v for k, v in bad.items() if v}
    if bad:
        C.blocked(OUT_X11E, "a run record is wrong", problems=bad)
    # X9's assertion (i)(b): MEAN on fold {1, 8}'s arms reproduces task_d3_ens5.json
    ar18 = C.arena((1, 8))
    mb = {s: mean_shared(C.load_ens5(C.ens5_weights((1, 8), s))[0], ar18["st"], ar18["ac"]) for s in C.ENS5_SEEDS}
    got = XA.strip(XA.calibration({s: {"err": mb[s]["err"], "epi": mb[s]["s"]} for s in C.ENS5_SEEDS},
                                  np.random.default_rng(0).integers(0, 4, (N_BOOT, 4))))
    want = json.load(open(os.path.join(R.RESULTS, "task_d3_ens5.json")))["calibration"]
    d1 = max(XA.max_diff(got, want), 0.0)
    if d1 > TOL_I:
        C.blocked(OUT_X11E, "assertion (i)(b) failed", max_abs_diff=d1)
    means, pers, sha, order, d2 = {s: [] for s in C.ENS5_SEEDS}, {s: [] for s in C.ENS5_SEEDS}, {}, [], 0.0
    for f in C.FOLDS:
        ar = C.arena(f)
        order += [{"fold": C.fid(f), "start_row": a} for a in ar["starts"]]
        for s in C.ENS5_SEEDS:
            w = C.ens5_weights(f, s)
            sha[f"{C.fid(f)}_s{s}"] = C.sha256(w)
            m = C.load_ens5(w)[0]
            mr = mean_shared(m, ar["st"], ar["ac"])
            p1 = from_members(per_member_shared(m, ar["st"], ar["ac"], stop=START + 1), ar["st"])
            d2 = max(d2, float((p1["pred"][:, START] - mr["pred"][:, START]).abs().max()))
            means[s].append(mr)
            pers[s].append(None)
            pers[s][-1] = (m, ar)
    if d2 != 0.0:
        C.blocked(OUT_X11E, "assertion (ii) failed", max_abs_diff=d2)
    cat = lambda rs: {k: np.concatenate([r[k] for r in rs], 0) for k in ("err", "s", "alea")}
    per_full = {s: [from_members(per_member_shared(m, ar["st"], ar["ac"]), ar["st"]) for m, ar in pers[s]]
                for s in C.ENS5_SEEDS}
    for s in C.ENS5_SEEDS:
        for r in per_full[s] + means[s]:
            if not (np.isfinite(r["err"][:, START:]).all() and np.isfinite(r["s"][:, START:]).all()):
                C.blocked(OUT_X11E, "non-finite rollout")
    tab = summarise([cat(means[s]) for s in C.ENS5_SEEDS], [cat(per_full[s]) for s in C.ENS5_SEEDS], 20)
    lab, why = verdict(tab, 20)
    out = {"rule": "X11e", "ledger": RULE_ID_X11E, "frozen_sha256": frozen,
           "script": "scripts/x9_per_member_propagation.py --x11e",
           "script_sha256": C.sha256("scripts/x9_per_member_propagation.py"), "exploratory": True,
           "never_reopens": "X9 or any discharged rule; nothing here changes a verdict",
           "design": {"models": "each X3 fold's three Arm A ensemble-5 arms, 2,500 iterations", "n_trajectories": 20,
                      "trajectories": order, "horizons": list(HORIZONS), "verdict_horizon": H_VERDICT, "band": list(BAND)},
           "assertions": {"i_b": {"pass": True, "max_abs_diff": d1}, "ii": {"pass": True, "max_abs_diff": d2}},
           "table": tab, "verdict": {"label": lab, "reason": why, "h": H_VERDICT, "n": 20}, "scope": SCOPE,
           "weights_sha256": sha, "code_sha256": {p: C.sha256(p) for p in MODULES},
           "git_head": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
           "timing": {"wall_clock_s": time.perf_counter() - t0, "torch_threads": torch.get_num_threads(),
                      "cpu_count": os.cpu_count()}}
    json.dump(out, open(OUT_X11E, "w"), indent=1, default=float)
    print(f"  X11e: {lab} ({why})")
    print(f"  wrote {R.rel(OUT_X11E)}")


def main():
    os.chdir(C.ROOT)
    ap = argparse.ArgumentParser()
    ap.add_argument("--assert-only", action="store_true")
    ap.add_argument("--x11e", action="store_true")
    args = ap.parse_args()
    if args.x11e:
        return x11e()
    x9(args.assert_only)


if __name__ == "__main__":
    main()
