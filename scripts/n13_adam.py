"""
N13 (round 5; POST HOC) -- the optimiser: Adam's settings, the measured collapse rate against the learning rate, Kingma and
Ba's step bound, and §7.5's reachability argument redone under it. docs/presubmission/round5/PROTOCOLS.md §5 N13 is the
specification; this is a summary. It re-opens no rule (S-19's retraction of the variance-state claim stands) and changes no
verdict.

FACTS, quoted with file:line: every training path's Adam call; none passes betas or eps, so the defaults apply -- read at run
time from inspect.signature(torch.optim.Adam.__init__), with torch.__version__; learning rate and weight decay from the
reference config.
RATE. collapse_fit.rate_over_lr over every results/*.json with a top-level collapse_fit: n, min, quartiles, max, overall and
by loss_type and arm.
BOUND (Kingma and Ba 2015, sec. 2.1): |step| <= alpha (1 - beta1) / sqrt(1 - beta2) when 1 - beta1 > sqrt(1 - beta2), else
<= alpha; "typical" |step| ~ alpha.
REACHABILITY. Delta = |CKPT_LOG_DELTA - the initialisation of log_delta_logstd|; CKPT_LOG_DELTA read from the checkpoint and
asserted to equal -14.4629 (scripts/step6_analyse.py:38) within 5e-5; the initialisation from a freshly built MLPStateHead,
asserted to equal the runs' iteration-0 log entry within one worst-case step. Iterations needed: Delta / alpha (typical) and
Delta / bound (worst case), against 500, 2,500 and 5,000.
SIGMA'S TRAJECTORY (Figure 4): per run, min_logstd_mean and log_delta_logstd_mean from `collapse`, and the implied sigma bounds
exp(min) and exp(min + exp(log_delta)). ASSERTION: for every saved checkpoint of every run whose results record exists and
carries a `collapse` log, RWMEnsemble.collapse_stats() on the weights equals the logged entry at that iteration within one
worst-case step; directories without such a record (baselines, timing probes, runs still training) are listed and skipped.
Writes results/n13_adam.json. Run from the repository root.
"""
import copy
import glob
import inspect
import json
import math
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import torch  # noqa: E402
import rwm_data as R  # noqa: E402
import rwm_model as M  # noqa: E402
import x11_common as C  # noqa: E402

OUT = os.path.join(R.RESULTS, "n13_adam.json")
UP = os.path.join(C.ROOT, os.pardir)
CKPT_STORED = -14.4629          # the project's typed constant, recorded as a defect (DECISIONS.md#G4-n13-ckpt)
C10_VALUE = -14.463             # FINDINGS_LEDGER.md C-10, to 3 dp
COUNTS = (500, 2500, 5000)
# The X11 queue (round 5, GT1): ensemble-5 fold runs and single-model seeds 3-4 on the four new folds
X11_RUN = re.compile(r"x3_(run_)?armA_ho(02|34|56|79)_seed([34]|\d+_ens5)")
MODULES = ("scripts/n13_adam.py", "src/rwm_model.py", "src/rwm_train.py", "scripts/x11_common.py")


def quote(path, a, b):
    L = open(path, encoding="utf-8").read().split("\n")
    return {"file": os.path.relpath(os.path.abspath(path), C.ROOT), "lines": f"{a}-{b}", "text": [L[i - 1].rstrip() for i in range(a, b + 1)]}


def record_of(run_dir):
    """The results record for a runs/ directory, by the drivers' naming (step5_train.py:194-198, 400-403)."""
    d = os.path.basename(run_dir)
    m = re.fullmatch(r"mn_M(\d+)_N(\d+)_seed(\d+)", d)
    if m:
        return os.path.join(R.RESULTS, f"mn_sweep_run_M{m[1]}_N{m[2]}_seed{m[3]}.json")
    m = re.fullmatch(r"x3_(arm[AB]_ho\d\d_seed\d+(?:_ens5)?)", d)
    if m:
        return os.path.join(R.RESULTS, f"x3_run_{m[1]}.json")
    if re.fullmatch(r"arm[AB]_seed\d+.*", d):
        return os.path.join(R.RESULTS, f"step5_{d}.json")
    return None


def quartiles(v):
    v = np.asarray(v, dtype=np.float64)
    return {"n": int(len(v)), "min": float(v.min()), "q1": float(np.percentile(v, 25)), "median": float(np.median(v)),
            "q3": float(np.percentile(v, 75)), "max": float(v.max())}


def main():
    os.chdir(C.ROOT)
    t0 = time.perf_counter()
    cfg = R.load_reference_config(R.repo_paths()["lite"])
    sig = inspect.signature(torch.optim.Adam.__init__).parameters
    defaults = {k: sig[k].default for k in ("lr", "betas", "eps", "weight_decay", "amsgrad")}
    b1, b2 = defaults["betas"]
    alpha = float(cfg["learning_rate"])
    facts = {"calls": [quote(os.path.join(UP, "rsl_rl_rwm", "rsl_rl", "algorithms", "mbpo_ppo.py"), 54, 54),
                       quote(os.path.join(UP, "rsl_rl_rwm", "rsl_rl", "algorithms", "mbpo_ppo.py"), 102, 102),
                       quote(os.path.join(UP, "robotic_world_model_lite", "scripts", "train.py"), 224, 228),
                       quote("src/rwm_train.py", 60, 63), quote("scripts/step5_train.py", 244, 244)],
             "torch_version": torch.__version__,
             "adam_defaults_read_at_run_time": {"betas": [b1, b2], "eps": defaults["eps"], "weight_decay": defaults["weight_decay"],
                                                "amsgrad": defaults["amsgrad"]},
             "configured": {"learning_rate": alpha, "weight_decay": cfg["weight_decay"]}}
    passes_betas = any("betas" in " ".join(q["text"]) or "eps=" in " ".join(q["text"]) for q in facts["calls"])
    facts["any_call_passes_betas_or_eps"] = passes_betas

    worst = alpha * (1 - b1) / math.sqrt(1 - b2) if (1 - b1) > math.sqrt(1 - b2) else alpha
    bound = {"typical": alpha, "worst_case": worst, "worst_over_lr": worst / alpha,
             "condition": f"1 - beta1 = {1 - b1:.6g} {'>' if (1 - b1) > math.sqrt(1 - b2) else '<='} sqrt(1 - beta2) = {math.sqrt(1 - b2):.6g}",
             "source": "Kingma and Ba (2015), sec. 2.1"}

    # rate_over_lr, every record with a top-level collapse_fit
    recs = []
    for p in sorted(glob.glob(os.path.join(R.RESULTS, "*.json"))):
        try:
            a = json.load(open(p))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if X11_RUN.search(os.path.basename(p)):
            continue                                          # the X11 queue (GT2), excluded so this artifact stays fixed
        if isinstance(a, dict) and isinstance(a.get("collapse_fit"), dict):
            hp = a.get("hyperparameters", {})
            recs.append({"file": os.path.relpath(p, C.ROOT), "rate_over_lr": a["collapse_fit"]["rate_over_lr"],
                         "slope_per_iter": a["collapse_fit"]["slope_per_iter"], "loss_type": hp.get("loss_type"),
                         "arm": a.get("arm"), "ensemble": hp.get("ensemble"), "iterations": hp.get("iterations")})
    rate = {"overall": quartiles([r["rate_over_lr"] for r in recs]), "by_loss_type": {}, "by_arm": {}}
    for key, field in (("by_loss_type", "loss_type"), ("by_arm", "arm")):
        for v in sorted({str(r[field]) for r in recs}):
            rate[key][v] = quartiles([r["rate_over_lr"] for r in recs if str(r[field]) == v])

    # reachability
    sd = torch.load(R.repo_paths()["ckpt"], map_location="cpu")["system_dynamics_state_dict"]
    vals = [sd[k] for k in sd if re.fullmatch(r"state_heads\.\d+\.state_log_delta_logstd", k)]
    ckpt_ld = float(torch.cat([v.flatten() for v in vals]).mean())
    torch.manual_seed(0)
    fresh = M.build_from_config(cfg, ensemble_size=1)
    init_ld = float(fresh.state_heads[0].state_log_delta_logstd.mean())
    init_min = float(fresh.state_heads[0].state_min_logstd.mean())
    it0 = [json.load(open(os.path.join(C.ROOT, r["file"])))["collapse"][0] for r in recs[:10]]
    d_init = max(abs(x["log_delta_logstd_mean"] - init_ld) for x in it0)
    # DECISIONS.md#G4-n13-ckpt: asserted against ledger C-10's recorded -14.463 at C-10's own precision; the project's typed
    # -14.4629 is recorded beside it as a defect, not asserted
    A = {"ckpt_log_delta": {"pass": bool(abs(ckpt_ld - C10_VALUE) < 5e-4), "value": ckpt_ld, "against": C10_VALUE,
                            "source": "FINDINGS_LEDGER.md C-10 (-14.463, uniform to 3 dp)",
                            "typed_constant": CKPT_STORED, "typed_constant_minus_checkpoint": CKPT_STORED - ckpt_ld,
                            "typed_constant_where": ["scripts/step5_train.py (since 84ff01b)", "scripts/step6_analyse.py:38",
                                                     "scripts/step6_3_min_logstd.py:32"]},
         "initialisation": {"pass": bool(d_init <= worst), "value": init_ld, "max_abs_diff_vs_iteration0_logs": d_init,
                            "tolerance": worst}}
    delta = abs(ckpt_ld - init_ld)
    reach = {"delta": delta, "iterations_typical": delta / alpha, "iterations_worst_case": delta / worst,
             "iterations_at_measured_rate": delta / (alpha * rate["overall"]["median"]),
             "counts": {str(c): {"reachable_typical": bool(c >= delta / alpha), "reachable_worst_case": bool(c >= delta / worst)}
                        for c in COUNTS}}

    # sigma's trajectory, and the checkpoint assertion
    traj, checked, skipped, dmax = {}, [], [], 0.0
    for r in recs:
        a = json.load(open(os.path.join(C.ROOT, r["file"])))
        c = a["collapse"]
        traj[r["file"]] = {"iter": [x["iter"] for x in c], "min_logstd_mean": [x["min_logstd_mean"] for x in c],
                           "log_delta_logstd_mean": [x["log_delta_logstd_mean"] for x in c],
                           "sigma_lower": [math.exp(x["min_logstd_mean"]) for x in c],
                           "sigma_upper": [math.exp(x["min_logstd_mean"] + math.exp(x["log_delta_logstd_mean"])) for x in c]}
    for rd in sorted(glob.glob(os.path.join(C.ROOT, "runs", "*"))):
        if not os.path.isdir(rd):
            continue
        rp = record_of(rd)
        if X11_RUN.search(os.path.basename(rd)):
            skipped.append({"dir": os.path.relpath(rd, C.ROOT), "reason": "X11 queue run (GT2)"})
            continue
        cks = sorted(glob.glob(os.path.join(rd, "weights_*.pt")) + glob.glob(os.path.join(rd, "rolling_*.pt")))
        if not cks:
            continue
        if rp is None or not os.path.exists(rp):
            skipped.append({"dir": os.path.relpath(rd, C.ROOT), "reason": "no results record (baseline, probe or still training)"})
            continue
        a = json.load(open(rp))
        if not isinstance(a.get("collapse"), list):
            skipped.append({"dir": os.path.relpath(rd, C.ROOT), "reason": "record has no collapse log"})
            continue
        hp = a["hyperparameters"]
        c2 = copy.deepcopy(cfg)
        if hp.get("rnn_hidden_size"):
            c2["architecture_config"]["rnn_hidden_size"] = hp["rnn_hidden_size"]
        log = {x["iter"]: x for x in a["collapse"]}
        for ck in cks:
            obj = torch.load(ck, map_location="cpu")
            it = obj.get("iter", int(re.search(r"_(\d+)\.pt$", ck)[1]))
            m = M.build_from_config(c2, ensemble_size=hp["ensemble"])
            m.load_state_dict(obj["model_state_dict"], strict=True)
            cs = m.collapse_stats()
            key = it if it in log else min(log, key=lambda k: abs(k - it))
            d = max(abs(cs["log_delta_logstd_mean"] - log[key]["log_delta_logstd_mean"]),
                    abs(cs["min_logstd_mean"] - log[key]["min_logstd_mean"]))
            dmax = max(dmax, d)
            checked.append({"checkpoint": os.path.relpath(ck, C.ROOT), "iter": int(it), "log_iter": int(key), "max_abs_diff": d})
    A["checkpoints_vs_logs"] = {"pass": bool(checked and dmax <= worst), "n_checked": len(checked), "max_abs_diff": dmax,
                                "tolerance": worst, "n_dirs_skipped": len(skipped)}
    for k, v in A.items():
        print(f"  assertion {k}: {'PASS' if v['pass'] else 'FAIL'}  {v.get('max_abs_diff', v.get('value'))}")
    if not all(v["pass"] for v in A.values()):
        C.blocked(OUT, "an assertion failed", assertions=A)
    out = {"analysis": "N13", "post_hoc": True,
           "never_reopens": "S-19 (the retracted variance-state claim stays retracted), M-24 or any rule; nothing here changes a verdict",
           "script": "scripts/n13_adam.py", "script_sha256": C.sha256("scripts/n13_adam.py"),
           "facts": facts, "bound": bound, "rate_over_lr": rate, "runs": recs, "reachability": reach,
           "initialisation": {"log_delta_logstd": init_ld, "min_logstd": init_min}, "ckpt_log_delta": ckpt_ld,
           "assertions": A, "checkpoints_checked": checked, "dirs_skipped": skipped, "sigma_trajectory": traj,
           "code_sha256": {p: C.sha256(p) for p in MODULES},
           "git_head": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
           "timing": {"wall_clock_s": time.perf_counter() - t0, "cpu_count": os.cpu_count()}}
    json.dump(out, open(OUT, "w"), indent=1, default=str)
    print(f"  betas {b1}, {b2}; eps {defaults['eps']}; bound/lr {worst / alpha:.3f}; rate/lr {rate['overall']}")
    print(f"  delta {delta:.4f}: typical {delta / alpha:,.0f} iterations, worst case {delta / worst:,.0f}")
    print(f"  wrote {R.rel(OUT)}")


if __name__ == "__main__":
    main()
