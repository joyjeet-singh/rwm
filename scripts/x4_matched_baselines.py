"""
Rule X4 (ledger M-87; PRE-REGISTERED, exploratory) -- is RWM still ahead of baselines matched to its size? Round 4,
PLAN Annex 2 X4 (ruling W2).

It never re-opens M-75, M-76 or any discharged rule, and nothing it returns changes a verdict.

VARIANTS. docs/presubmission/BASELINE_SPECS.md row 33 (MLP, width 295) and row 34 (transformer, d_model 160,
learned positions), built by src/baselines' build(arch, "matched", cfg): 713,171 and 686,196 parameters against RWM's
714,164-parameter state pathway, within +-5% (asserted). Trained autoregressively (regime ar), otherwise exactly as
M-76: scripts/train_baseline.py, held-out {1, 8}, 2,500 iterations, the seeds results/round4_queue_timing.json queued
(0-2). The matched RSSM is not run (ruling W2).

STATISTIC AND TEST, M-76's, imported from scripts/verdict_baselines.py: per baseline b, D_b = the mean over section 5's
four held-out trajectories of [3-seed mean relative-L1 of b - 3-seed mean relative-L1 of RWM] at h = 368, RWM being
Arm A (32, 8) at 2,500 iterations, seeds 0-2 (verdict_baselines.differences); the exact 256-resample cluster bootstrap
and two-sided p, and Holm at alpha = 0.05 over the family of two, MLP before transformer (verdict_baselines.family).
Scoring is scripts/baselines_eval.py's evaluate(), imported: the same windows, metrics and rollout as M-75/M-76.

READING. The label verdict_baselines.overall returns for the family of two, with X4's names:
  1 A MATCHED BASELINE AHEAD   any baseline BASELINE BETTER
  2 RWM AHEAD OF BOTH          both RWM BETTER
  3 PARTIAL                    one RWM BETTER and the other CANNOT BE SETTLED
  4 CANNOT BE SETTLED          neither resolves
M-76's names say "A BASELINE AHEAD" and "RWM AHEAD OF ALL THREE"; for two size-matched baselines the first gains
"MATCHED" and "ALL THREE" becomes "BOTH". The function, the order of outcomes and the other two labels are M-76's.
The self-test asserts a defined label for every one of the nine combinations of two per-baseline results.
ALONGSIDE, never governing: the same test at h = 100 and h = 32 (relative-L1); the four per-trajectory differences;
each run's wall clock and s/iter, the parameter counts, and today's probe cost per iteration
(results/round4_queue_timing.json).

ASSERTIONS, before any reading:
  (a) baselines_eval.evaluate, run on the original-size autoregressive baselines (mlp, rssm, transformer, ar, s7),
      reproduces results/baselines_eval.json on every per-trajectory value they share (both arenas, every horizon,
      both metrics, every seed, and RWM's), to 1e-6;
  (b) verdict_baselines.family, run on that output with M-76's names, reproduces results/baselines_verdict.json's M-76
      governing verdict and its per-baseline D, p and interval, to 1e-12;
  (c) each matched model, as built, is within +-5% of RWM's state pathway, and BASELINE_SPECS.md rows 33 and 34 are
      not UNVERIFIED;
  (d) every matched run's record says arch, regime ar, spec matched, 2,500 iterations, its seed, the built parameter
      count and finite losses, and its weights exist.
(a)-(c) need no new run; --assert-only runs them and reads nothing. A non-finite score (verdict_baselines raises
CannotDischarge, M-76's failure clause) or any internal check failing stops the run with
results/x4_matched_baselines.json.blocked and no reading. The run records of the matched baselines say rule M-76, the
trainer's label for regime ar (scripts/train_baseline.py), and the evaluator's file says M-75 and M-76; both are X4's
runs. The script runs from the repository root wherever it is started.

  python scripts/x4_matched_baselines.py --self-test     # synthetic values: the labels, the family of two
  python scripts/x4_matched_baselines.py --assert-only   # assertions (a)-(c); no matched run is loaded
  python scripts/x4_matched_baselines.py                 # self-test, assertions, then the rule (refuses unless
                                                         # ledger M-87 records this file's SHA-256)
Writes results/x4_matched_baselines.json and the evaluator's scores, results/x4_matched_baselines_eval.json.
NEEDS_WEIGHTS: the runs are gitignored.
"""
import argparse
import hashlib
import itertools
import json
import math
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402

import baselines as BL  # noqa: E402
import baselines_eval as BE  # noqa: E402
import rwm_data as R  # noqa: E402
import verdict_baselines as VB  # noqa: E402

RULE_ID = "M-87"
ARCHS = ("mlp", "transformer")                     # Holm order: MLP before transformer, as M-76's priority order
NAMES = ("A MATCHED BASELINE AHEAD", "RWM AHEAD OF BOTH", "PARTIAL", "CANNOT BE SETTLED")
RESULTS = ("RWM BETTER", "BASELINE BETTER", "CANNOT BE SETTLED")
H_READ, H_ALONG = "368", ("100", "32")
ITERS = 2500
TOL, TOL_EXACT = 1e-6, 1e-12
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
OUT = os.path.join(R.RESULTS, "x4_matched_baselines.json")
EVAL_OUT = os.path.join(R.RESULTS, "x4_matched_baselines_eval.json")
SPECS = os.path.join(ROOT, "docs", "presubmission", "BASELINE_SPECS.md")
MODULES = ("scripts/x4_matched_baselines.py", "scripts/baselines_eval.py", "scripts/verdict_baselines.py",
           "scripts/verdict_mn_sweep.py", "scripts/p5_sweep_power.py", "scripts/mn_sweep_eval.py",
           "src/baselines/__init__.py", "src/baselines/common.py", "src/baselines/mlp.py", "src/baselines/transformer.py")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def blocked(reason, **detail):
    json.dump({"BLOCKED": reason, **detail}, open(OUT + ".blocked", "w"), indent=1, default=str)
    raise SystemExit(f"BLOCKED: {reason} (results/x4_matched_baselines.json.blocked); no reading written")


def keys(spec):
    return {a: BE.key(a, "ar", spec) for a in ARCHS}


def test(ev, metric, h):
    """M-76's statistic and test for the family of two (verdict_baselines.differences and family, imported)."""
    return VB.family(VB.differences(ev, keys("matched"), "held_out", metric, h), ARCHS, NAMES)


def self_test():
    fails = []

    def check(name, cond):
        if not cond:
            fails.append(name)
    combos = {}
    for r in itertools.product(RESULTS, repeat=len(ARCHS)):
        combos[r] = VB.overall(dict(zip(ARCHS, r)), NAMES)
    check("a defined label for all nine combinations", len(combos) == 9 and all(v in NAMES for v in combos.values()))
    check("any baseline better -> A MATCHED BASELINE AHEAD",
          all(v == NAMES[0] for r, v in combos.items() if "BASELINE BETTER" in r))
    check("both RWM better -> RWM AHEAD OF BOTH", combos[("RWM BETTER", "RWM BETTER")] == NAMES[1])
    check("one RWM better, one unsettled -> PARTIAL", combos[("RWM BETTER", "CANNOT BE SETTLED")] == NAMES[2]
          and combos[("CANNOT BE SETTLED", "RWM BETTER")] == NAMES[2])
    check("neither -> CANNOT BE SETTLED", combos[("CANNOT BE SETTLED", "CANNOT BE SETTLED")] == NAMES[3])
    up = np.array([0.6, 0.5, 0.55, 0.7])
    noisy = np.array([0.6, -0.5, 0.05, -0.1])
    r1 = VB.family({"mlp": up, "transformer": up}, ARCHS, NAMES)
    check("a clear positive pair: RWM AHEAD OF BOTH", r1["verdict"] == NAMES[1] and r1["m"] == 2)
    r2 = VB.family({"mlp": -up, "transformer": noisy}, ARCHS, NAMES)
    check("a clear negative: A MATCHED BASELINE AHEAD", r2["verdict"] == NAMES[0])
    r3 = VB.family({"mlp": up, "transformer": noisy}, ARCHS, NAMES)
    check("one clear, one noisy: PARTIAL", r3["verdict"] == NAMES[2])
    check("the family is Holm over two", sorted(v["rank"] for v in r1["per_baseline"].values()) == [1, 2])
    h1 = "d" * 64
    fake = f"### M-86 — x\n`{'e' * 64}`\n### {RULE_ID} — PRE-REGISTERED rule X4\n`{h1}`\n### M-88 — y\n"
    check("ledger: the entry's own hash only", ledger_hashes(fake) == [h1])
    check("ledger: another entry's hash does not count", ledger_hashes(fake.replace(f"### {RULE_ID} ", "### M-99 ")) == [])
    print(f"  self-test: {'PASS' if not fails else 'FAIL ' + str(fails)} (synthetic values; no reading)")
    return not fails


def ledger_hashes(text):
    """Every 64-hex-digit token in backticks inside the ledger entry headed `### M-87 — `, lower-cased."""
    m = re.search(rf"^### {RULE_ID} — .*?(?=^### |\Z)", text, flags=re.M | re.S)
    return [] if not m else [h.lower() for h in re.findall(r"`([0-9a-fA-F]{64})`", m.group(0))]


def assert_a_b():
    committed = json.load(open(os.path.join(R.RESULTS, "baselines_eval.json")))
    queued = [(a, "ar", "s7") for a in ("mlp", "rssm", "transformer")]
    with tempfile.TemporaryDirectory() as td:
        ev = BE.evaluate(queued, os.path.join(ROOT, "runs"), R.RESULTS, ITERS, os.path.join(td, "eval.json"))
    d, n = 0.0, 0
    for k in ["rwm"] + [BE.key(*q) for q in queued]:
        for s, rec in ev["configs"][k]["seeds"].items():
            for ar in ("held_out", "in_sample"):
                for h, mv in rec[ar].items():
                    for mt, vals in mv.items():
                        for x, y in zip(vals, committed["configs"][k]["seeds"][s][ar][h][mt]):
                            d, n = max(d, abs(x - y)), n + 1
    a = {"pass": bool(d <= TOL and n > 0), "max_abs_diff": d, "n_values": n, "against": "results/baselines_eval.json"}
    bv = json.load(open(os.path.join(R.RESULTS, "baselines_verdict.json")))["rules"]["M-76"]["governing"]
    g = VB.family(VB.differences(ev, {x: BE.key(x, "ar", "s7") for x in VB.ORDER}, "held_out", "l1", "368"),
                  VB.ORDER, VB.RULES["M-76"]["names"])
    db = max(abs(g["per_baseline"][x][f] - bv["per_baseline"][x][f]) for x in VB.ORDER for f in ("D", "p"))
    db = max([db] + [abs(u - v) for x in VB.ORDER for u, v in zip(g["per_baseline"][x]["ci95"], bv["per_baseline"][x]["ci95"])])
    b = {"pass": bool(g["verdict"] == bv["verdict"] and db <= TOL_EXACT), "verdict": g["verdict"],
         "committed_verdict": bv["verdict"], "max_abs_diff": db, "against": "results/baselines_verdict.json rules.M-76.governing"}
    return a, b


def assert_c(cfg):
    counts = {a: BL.n_params(BL.build(a, "matched", cfg)) for a in ARCHS}
    rows = {}
    for l in open(SPECS, encoding="utf-8"):
        m = re.match(r"\| (33|34) \| ([^|]+)\| ([^|]+)\| ([^|]+)\|", l)
        if m:
            rows[int(m.group(1))] = m.group(4).strip()
    ok = (sorted(rows) == [33, 34] and not any("UNVERIFIED" in v.upper() for v in rows.values())
          and all(abs(c / BL.RWM_STATE_PATHWAY - 1) <= 0.05 for c in counts.values()))
    return {"pass": bool(ok), "n_params": counts, "rwm_state_pathway": BL.RWM_STATE_PATHWAY,
            "ratio": {a: c / BL.RWM_STATE_PATHWAY for a, c in counts.items()}, "baseline_specs_status": rows}


def assert_d(cfg, seeds):
    bad, runs = [], {}
    for a in ARCHS:
        n_par = BL.n_params(BL.build(a, "matched", cfg))
        for s in seeds:
            p = BE.run_artifact(R.RESULTS, a, "ar", "matched", s)
            w = BE.weights_path(os.path.join(ROOT, "runs"), a, "ar", "matched", s, ITERS)
            if not os.path.exists(p) or not os.path.exists(w):
                bad.append(f"{a} seed {s}: record or weights missing")
                continue
            r = json.load(open(p))
            hp = r["hyperparameters"]
            if ((r["arch"], r["regime"], r["spec"], r["seed"]) != (a, "ar", "matched", s) or hp["iterations"] != ITERS
                    or hp["n_params"] != n_par or hp["holdout_episodes"] != [1, 8]
                    or any(not math.isfinite(x) for v in r["curves"].values() for x in v)):
                bad.append(f"{a} seed {s}: record does not match the queued run")
            runs[f"{a}_seed{s}"] = {"wall_clock_s": r["wall_clock_s"], "s_per_iter": r["s_per_iter"], "n_params": hp["n_params"]}
    return {"pass": not bad, "problems": bad}, runs


def reading(ev):
    """Everything main() computes from the evaluator's output: the reading and the alongside values."""
    gov = test(ev, "l1", H_READ)
    return {"reading": {"h": int(H_READ), "metric": "l1", "label": gov["verdict"], "per_baseline": gov["per_baseline"]},
            "alongside": {f"l1_h{h}": {**test(ev, "l1", h), "status": "alongside, not a reading"} for h in H_ALONG}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--assert-only", action="store_true")
    args = ap.parse_args()
    os.chdir(ROOT)                         # baselines_eval's RWM weights path is relative to the repository root
    ok = self_test()
    if args.self_test or not ok:
        sys.exit(0 if ok else 1)
    me = sha256(os.path.abspath(__file__))
    print(f"  script SHA-256 {me}")
    timing = json.load(open(os.path.join(R.RESULTS, "round4_queue_timing.json")))
    seeds = tuple(timing["x4"]["seeds"])
    if timing["blocked"] or seeds != BE.SEEDS:
        blocked(f"the timing record is blocked or queued seeds {seeds}, not M-76's three ({BE.SEEDS})")
    if not args.assert_only:
        reg = ledger_hashes(open(os.path.join(ROOT, "FINDINGS_LEDGER.md"), encoding="utf-8").read())
        if me not in reg:
            blocked(f"ledger {RULE_ID} does not record this script's SHA-256 {me}: the rule is not pre-registered as run",
                    recorded=reg)
    cfg = R.load_reference_config(R.repo_paths()["lite"])
    try:
        a, b = assert_a_b()
        asserts = {"a": a, "b": b, "c": assert_c(cfg)}
    except (AssertionError, VB.CannotDischarge) as e:
        blocked(f"an internal check failed during the assertions: {e}")
    for k, v in asserts.items():
        print(f"  assertion ({k}): {'PASS' if v['pass'] else 'FAIL'}  " + ", ".join(
            f"{x} {y:.1e}" for x, y in v.items() if isinstance(y, float)))
    failed = [k for k, v in asserts.items() if not v["pass"]]
    if failed:
        blocked(f"assertion(s) {failed} failed", assertions=asserts)
    if args.assert_only:
        print("  --assert-only: assertions (a)-(c) pass; no matched run was loaded and nothing was read")
        return
    asserts["d"], runs = assert_d(cfg, seeds)
    if not asserts["d"]["pass"]:
        blocked("a matched run's record does not check out (assertion d)", assertions=asserts)

    try:
        ev = BE.evaluate([(x, "ar", "matched") for x in ARCHS], os.path.join(ROOT, "runs"), R.RESULTS, ITERS, EVAL_OUT)
        rd = reading(ev)
    except (AssertionError, VB.CannotDischarge) as e:
        blocked(f"the reading stopped: {e}", assertions=asserts)
    out = {
        "rule": "X4", "ledger": RULE_ID, "script": "scripts/x4_matched_baselines.py", "script_sha256": me,
        "exploratory": True, "never_reopens": "M-75, M-76 or any discharged rule; nothing here changes a verdict",
        "design": {"variants": {a: f"BASELINE_SPECS.md row {33 + i}" for i, a in enumerate(ARCHS)}, "regime": "ar",
                   "spec": "matched", "iterations": ITERS, "seeds": list(seeds), "rwm": "Arm A (32, 8), 2,500 iterations",
                   "arena": "section 5's held-out pair, 4 non-overlapping 400-step trajectories",
                   "n_independent": ev["arenas"]["held_out"]["n_independent"],
                   "statistic": "D_b = mean over trajectories of [3-seed mean err_b - 3-seed mean err_RWM], relative-L1, h = 368",
                   "test": "exact 256-resample cluster bootstrap and two-sided p; Holm over the family of two (MLP, transformer)",
                   "names": list(NAMES)},
        "assertions": asserts, **rd,
        "runs": runs,
        "probe_s_per_iter": {a: timing["probes"][f"{a}_ar_matched"]["steady_s_per_iter"] for a in ARCHS},
        "n_params": asserts["c"]["n_params"],
        "caveats": ["matching the parameter count is one axis; the shapes and settings stay our reading of Table S7",
                    "the matched RSSM is not run (ruling W2)",
                    "M-76's own Licenses line holds: architecture at a fixed regime, not the original's claim",
                    "the matched runs' records say rule M-76 (the trainer's label for regime ar); they are X4's runs"],
        "evaluator_output": "results/x4_matched_baselines_eval.json",
        "code_sha256": {p: sha256(os.path.join(ROOT, p)) for p in MODULES},
        "git_head": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()}
    json.dump(out, open(OUT, "w"), indent=2)
    print(f"  X4 returns: {rd['reading']['label']}")
    for x, v in rd["reading"]["per_baseline"].items():
        print(f"    {x:<12} D {v['D']:+.4f}  p {v['p']:.5f}  Holm rank {v['rank']}  {v['result']}")
    print(f"  wrote {R.rel(OUT)}")


if __name__ == "__main__":
    main()
