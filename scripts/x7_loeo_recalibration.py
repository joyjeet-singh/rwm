"""
Rule X7 (ledger M-89; PRE-REGISTERED, exploratory, inference only) -- §6.7's per-horizon recalibration, fitted on nine
episodes and scored on the tenth, for each of the ten. Round 4, PLAN Annex 2 X7 (objection O5).

It never re-opens M-69, M-70 or any discharged rule, and nothing it returns changes a verdict.

MODEL. The released checkpoint, ensemble of 5, as released. The epistemic term governs; the aleatoric is alongside.
TRAJECTORIES. Each episode's non-overlapping 400-step trajectories (32 history rows, 368 forecast rows), rolled out by
task_d3_perhorizon.episode_rollout, imported: 2 per episode, 20 in all.
DESIGN. For each episode e, fit the per-horizon multiplier c_h on the other nine episodes' 18 trajectories with §6.7's
fitting function (task_d3_perhorizon.fit_scalar, imported: the smallest c reaching 68.27% +-1-sigma coverage, by
bisection in log space), and score +-1-sigma coverage on e's two trajectories. Each trajectory is scored once, by a
multiplier not fitted on it. Coverage is §6.7's (task_d3_perhorizon.cover): every finite, positive-sigma cell over
forecast steps 1..h x 45 state dimensions. Per trajectory it is reduced to (covered, valid) counts and pooled over the
20 trajectories (task_d3_cross_model.counts and pooled, imported, an exact reduction of cover(), asserted).
INTERVAL. 95%, over whole trajectories: 20,000 Monte Carlo resamples of the 20 trajectories, numpy default_rng(0), one
draw shared by every horizon, quantity and variant, the pooled coverage recomputed on each, percentiles 2.5 and 97.5.
This is task_d3_cross_model's recipe, and Annex 2's.

READING, per horizon h in {1, 8, 32, 100, 128, 368}, against the band 68.27% +- 10 points = [58.27%, 78.27%]
(§6.7's target and tolerance, task_d3_perhorizon.TARGET and task_d3_cross_model.TOL):
  WITHIN BAND    the interval lies inside the band
  OUTSIDE BAND   the interval lies wholly outside it
  UNRESOLVED     otherwise
GOVERNING SUMMARY, for the epistemic term: "WITHIN BAND AT k OF 6 HORIZONS".
ALONGSIDE, never governing: the aleatoric term under the same design; the constant-multiplier version of the same
design (one c fitted at h = 1 on the nine episodes, §6.7's constant recipe, scored at every h); the coverage before
any multiplier; and the spread of the fitted c_h across the ten folds.

ASSERTIONS, before any reading (a failure stops the run; nothing is read):
  (a) §6.7's own two-fold design (fit on one of episodes 1 and 8, score on the other), rerun through the imported
      functions, reproduces results/task_d3_perhorizon.json's cells -- every fit's c, coverage after and coverage before,
      per-horizon and constant, both quantities -- to 1e-9;
  (b) counts() pooled over a fold's trajectories equals cover() on them, to 1e-12, in every assertion cell;
  (c) every episode yields two non-overlapping 400-step trajectories, 20 in all.
A non-finite value in the reading, or any internal check failing, stops the run with a .blocked record and no reading.

CAVEAT, in every sentence that reports it: unseen by the multiplier, not by the model. The released checkpoint trained on
all ten episodes, so every scored trajectory is in its training data.

  python scripts/x7_loeo_recalibration.py --self-test     # synthetic values only
  python scripts/x7_loeo_recalibration.py --assert-only   # assertions (a)-(b), on episodes 1 and 8 only
  python scripts/x7_loeo_recalibration.py                 # self-test, assertions, then the rule (refuses unless
                                                          # ledger M-89 records this file's SHA-256)
Writes results/x7_loeo_recalibration.json.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402

import task_d3_cross_model as CM  # noqa: E402
import task_d3_perhorizon as TD3  # noqa: E402
import rwm_data as R  # noqa: E402

RULE_ID = "M-89"
HS = tuple(TD3.HORIZONS)
EPISODES = tuple(range(R.N_EPISODES))
QUANT = {"aleatoric": 1, "epistemic": 2}           # positions in episode_rollout's (err, alea, epi, n)
GOVERNS = "epistemic"
N_BOOT, BOOT_SEED = 20000, 0
LO, HI = TD3.TARGET - CM.TOL, TD3.TARGET + CM.TOL
LABELS = ("WITHIN BAND", "OUTSIDE BAND", "UNRESOLVED")
TOL_A, TOL_B = 1e-9, 1e-12
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
OUT = os.path.join(R.RESULTS, "x7_loeo_recalibration.json")
MODULES = ("scripts/x7_loeo_recalibration.py", "scripts/task_d3_perhorizon.py", "scripts/task_d3_cross_model.py",
           "src/score_reference.py", "src/rwm_data.py", "src/rwm_metrics.py", "src/rollout_eval.py")


class NonFinite(Exception):
    pass


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def blocked(reason, **detail):
    json.dump({"BLOCKED": reason, **detail}, open(OUT + ".blocked", "w"), indent=1, default=str)
    raise SystemExit(f"BLOCKED: {reason} (results/x7_loeo_recalibration.json.blocked); no reading written")


def label(lo, hi):
    if LO <= lo and hi <= HI:
        return LABELS[0]
    if hi < LO or lo > HI:
        return LABELS[1]
    return LABELS[2]


def stack(cache, eps, k):
    return np.concatenate([cache[e][k] for e in eps], axis=0)


def boot_ci(cov, val, draws):
    bd = np.array([CM.pooled(cov, val, i) for i in draws])
    return [float(np.percentile(bd, 2.5)), float(np.percentile(bd, 97.5))]


# ------------------------------------------------------------------ assertions
def assertions(cache):
    d3 = json.load(open(os.path.join(R.RESULTS, "task_d3_perhorizon.json")))
    hold = list(d3["holdout_episodes"])
    da, db = 0.0, 0.0
    for q, k in QUANT.items():
        rec = d3["quantities"][q]
        fits = {(f["fit_episode"], f["h"]): f for f in rec["fits"]}
        cfits = {(f["fit_episode"], f["h"]): f for f in rec["constant_fits"]}
        for fit_ep in hold:
            test_ep = [e for e in hold if e != fit_ep][0]
            fe, fs = cache[fit_ep][0], cache[fit_ep][k]
            te, ts = cache[test_ep][0], cache[test_ep][k]
            c_const = TD3.fit_scalar(fe, fs, 1)
            for h in HS:
                c_h = TD3.fit_scalar(fe, fs, h)
                f, cf = fits[(fit_ep, h)], cfits[(fit_ep, h)]
                da = max(da, abs(c_h - f["c"]) / max(1.0, abs(f["c"])), abs(TD3.cover(te, ts, c_h, h) - f["coverage_after"]),
                         abs(TD3.cover(te, ts, 1.0, h) - f["coverage_before"]), abs(c_const - cf["c"]) / max(1.0, abs(cf["c"])),
                         abs(TD3.cover(te, ts, c_const, h) - cf["coverage_after"]))
                cov, val = CM.counts(te, ts, c_h, h)
                db = max(db, abs(CM.pooled(cov, val) - TD3.cover(te, ts, c_h, h)))
    return {"a": {"pass": bool(da <= TOL_A), "max_abs_diff": da, "note": "c compared relative to max(1, |c|)",
                  "against": "results/task_d3_perhorizon.json, both quantities, fits and constant_fits"},
            "b": {"pass": bool(db <= TOL_B), "max_abs_diff": db}}


# ------------------------------------------------------------------ the reading
def reading(cache):
    n_traj = {e: int(cache[e][3]) for e in EPISODES}
    if any(v != 2 for v in n_traj.values()):
        raise AssertionError(f"assertion (c): trajectories per episode {n_traj}")
    order = [e for e in EPISODES for _ in range(n_traj[e])]
    draws = np.random.default_rng(BOOT_SEED).integers(0, len(order), (N_BOOT, len(order)))
    out = {}
    for q, k in QUANT.items():
        per_h, cons, before, spread = {}, {}, {}, {}
        c_fold = {e: {} for e in EPISODES}
        cc = {}
        for e in EPISODES:
            others = [x for x in EPISODES if x != e]
            fe, fs = stack(cache, others, 0), stack(cache, others, k)
            cc[e] = TD3.fit_scalar(fe, fs, 1)
            for h in HS:
                c_fold[e][h] = TD3.fit_scalar(fe, fs, h)
        for h in HS:
            parts = {"per_horizon": [], "constant": [], "before": []}
            for e in EPISODES:
                te, ts = cache[e][0], cache[e][k]
                for name, c in (("per_horizon", c_fold[e][h]), ("constant", cc[e]), ("before", 1.0)):
                    parts[name].append(CM.counts(te, ts, c, h))
            res = {}
            for name, lst in parts.items():
                cov = np.concatenate([x[0] for x in lst])
                val = np.concatenate([x[1] for x in lst])
                p, ci = CM.pooled(cov, val), boot_ci(cov, val, draws)
                if not all(np.isfinite([p, *ci])):
                    raise NonFinite(f"{q} {name} h = {h}: non-finite coverage")
                res[name] = {"coverage": p, "ci95": ci, "label": label(*ci)}
            per_h[str(h)], cons[str(h)], before[str(h)] = res["per_horizon"], res["constant"], res["before"]
            cs = [c_fold[e][h] for e in EPISODES]
            spread[str(h)] = {"min": float(min(cs)), "max": float(max(cs)), "max_over_min": float(max(cs) / min(cs)),
                              "per_fold": {str(e): float(c_fold[e][h]) for e in EPISODES}}
        k_in = sum(1 for h in HS if per_h[str(h)]["label"] == LABELS[0])
        out[q] = {"per_horizon": per_h, "summary": f"WITHIN BAND AT {k_in} OF {len(HS)} HORIZONS", "n_within": k_in,
                  "constant_multiplier": {"per_horizon": cons, "c_per_fold": {str(e): float(cc[e]) for e in EPISODES},
                                          "n_within": sum(1 for h in HS if cons[str(h)]["label"] == LABELS[0])},
                  "before_any_multiplier": before, "c_spread_across_folds": spread}
    return out, n_traj, order


def ledger_hashes(text):
    """Every 64-hex-digit token in backticks inside the ledger entry headed `### M-89 — `, lower-cased."""
    m = re.search(rf"^### {RULE_ID} — .*?(?=^### |\Z)", text, flags=re.M | re.S)
    return [] if not m else [x.lower() for x in re.findall(r"`([0-9a-fA-F]{64})`", m.group(0))]


def self_test():
    fails = []

    def check(name, cond):
        if not cond:
            fails.append(name)
    check("the band is 58.27% to 78.27%", abs(LO - 0.5827) < 1e-12 and abs(HI - 0.7827) < 1e-12)
    check("inside", label(0.60, 0.75) == LABELS[0])
    check("on the edges counts as inside", label(LO, HI) == LABELS[0])
    check("wholly below", label(0.30, 0.58) == LABELS[1])
    check("wholly above", label(0.80, 0.95) == LABELS[1])
    check("straddles an edge", label(0.55, 0.70) == LABELS[2] and label(0.70, 0.85) == LABELS[2])
    check("wider than the band", label(0.50, 0.90) == LABELS[2])
    cov = np.array([3.0, 5.0, 7.0, 9.0]); val = np.array([10.0, 10.0, 10.0, 10.0])
    check("pooled is a ratio of sums", abs(CM.pooled(cov, val) - 0.6) < 1e-15)
    d = np.random.default_rng(0).integers(0, 4, (200, 4))
    lo, hi = boot_ci(cov, val, d)
    check("the interval brackets the pooled value", lo <= 0.6 <= hi)
    h1 = "c" * 64
    fake = f"### M-88 — x\n`{'b' * 64}`\n### {RULE_ID} — PRE-REGISTERED rule X7\n`{h1}`\n### M-90 — y\n`{'a' * 64}`\n"
    check("ledger: the entry's own hash only", ledger_hashes(fake) == [h1])
    check("ledger: another entry's hash does not count", ledger_hashes(fake.replace(f"### {RULE_ID} ", "### M-99 ")) == [])
    print(f"  self-test: {'PASS' if not fails else 'FAIL ' + str(fails)} (synthetic values; no reading)")
    return not fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--assert-only", action="store_true")
    args = ap.parse_args()
    os.chdir(ROOT)
    ok = self_test()
    if args.self_test or not ok:
        sys.exit(0 if ok else 1)
    me = sha256(os.path.abspath(__file__))
    print(f"  script SHA-256 {me}")
    if not args.assert_only:
        reg = ledger_hashes(open(os.path.join(ROOT, "FINDINGS_LEDGER.md"), encoding="utf-8").read())
        if me not in reg:
            blocked(f"ledger {RULE_ID} does not record this script's SHA-256 {me}: the rule is not pre-registered as run",
                    recorded=reg)
    try:
        hold = json.load(open(os.path.join(R.RESULTS, "task_d3_perhorizon.json")))["holdout_episodes"]
        cache = {e: TD3.episode_rollout(e) for e in (hold if args.assert_only else EPISODES)}
        asserts = assertions(cache)
    except AssertionError as e:
        blocked(f"an internal check failed during the assertions: {e}")
    for k, v in asserts.items():
        print(f"  assertion ({k}): {'PASS' if v['pass'] else 'FAIL'}  max_abs_diff {v['max_abs_diff']:.1e}")
    if not all(v["pass"] for v in asserts.values()):
        blocked("assertion(s) failed", assertions=asserts)
    if args.assert_only:
        print("  --assert-only: assertions (a)-(b) pass; only episodes 1 and 8 were rolled out, and nothing was read")
        return
    try:
        res, n_traj, order = reading(cache)
    except (AssertionError, NonFinite) as e:
        blocked(f"the reading stopped: {e}", assertions=asserts)
    asserts["c"] = {"pass": True, "trajectories_per_episode": {str(e): v for e, v in n_traj.items()}}
    g = res[GOVERNS]
    out = {"rule": "X7", "ledger": RULE_ID, "script": "scripts/x7_loeo_recalibration.py", "script_sha256": me,
           "exploratory": True, "never_reopens": "M-69, M-70 or any discharged rule; nothing here changes a verdict",
           "design": {"model": "the released checkpoint, ensemble of 5", "episodes": list(EPISODES),
                      "n_trajectories": len(order), "fit": "the other nine episodes' 18 trajectories, per horizon",
                      "score": "the held-out episode's 2 trajectories", "horizons": list(HS),
                      "band": [LO, HI], "target": TD3.TARGET,
                      "interval": f"{N_BOOT} Monte Carlo resamples of the {len(order)} trajectories, default_rng({BOOT_SEED}), "
                                  "one draw shared"},
           "assertions": asserts,
           "reading": {"quantity": GOVERNS, "summary": g["summary"], "n_within": g["n_within"],
                       "per_horizon": {h: {"coverage": v["coverage"], "ci95": v["ci95"], "label": v["label"]}
                                       for h, v in g["per_horizon"].items()}},
           "alongside": {"aleatoric": res["aleatoric"], "epistemic_constant_multiplier": g["constant_multiplier"],
                         "epistemic_before_any_multiplier": g["before_any_multiplier"],
                         "epistemic_c_spread_across_folds": g["c_spread_across_folds"],
                         "status": "alongside, not a reading"},
           "caveats": ["unseen by the multiplier, not by the model: the released checkpoint trained on all ten episodes"],
           "code_sha256": {p: sha256(os.path.join(ROOT, p)) for p in MODULES},
           "git_head": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()}
    json.dump(out, open(OUT, "w"), indent=2)
    print(f"  X7 returns: {g['summary']} (epistemic)")
    for h, v in g["per_horizon"].items():
        print(f"    h = {h:>3}  coverage {100 * v['coverage']:6.2f}% [{100 * v['ci95'][0]:6.2f}, {100 * v['ci95'][1]:6.2f}]  {v['label']}")
    print(f"  wrote {R.rel(OUT)}")


if __name__ == "__main__":
    main()
