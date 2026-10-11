"""
Rule X6 (ledger M-88; PRE-REGISTERED, exploratory, inference only) -- does ensemble disagreement beat the model's own
predicted step size as a ranking signal for error, on more, shorter units? Round 4, PLAN Annex 2 X6 (objection O4).

It never re-opens M-51, M-52, M-64 or any discharged rule, and nothing it returns changes a verdict.

MODEL. The released checkpoint (setup.sh's pretrain_rnn_ens.pt), ensemble of 5, as released.
UNITS. All ten episodes, non-overlapping units of 32 + h rows within each episode, built by M-64's index builder
(m64_short_units.build_index, imported), at h in {32, 100}. h = 100 governs.
THE PANEL is e7_free_baselines.load_panel(starts, length), imported: the rollout at the causal pairing from 32 history
rows, |error| as the per-step sum over the 45 state dimensions, disagreement as the applied epistemic scalar, and
e7_free_baselines.baselines()'s step size, ||mu_t - mu_(t-1)||.
STATISTIC. M-51/M-52's margin, r(disagreement, |error|) - r(step size, |error|), each a Pearson correlation over every
(unit, step) cell (e7_free_baselines._corr, imported). Paired: both correlations are recomputed on the same resampled
units. 95% interval over whole units, Annex 2's recipe: 20,000 Monte Carlo resamples of the units with replacement,
numpy default_rng(0), the statistic recomputed on each, percentiles 2.5 and 97.5. The resampling loop is
e7_free_baselines' own (a closure inside its main(), so not importable); assertion (b) shows this script's copy of it,
at e7's settings, reproduces e7's committed intervals.
MDE, computed and printed before the reading: M-51's method (e7_free_baselines --power) at this n, from disagreement,
|error| and the forecast index only -- the bootstrap SD of the margin over the forecast index, r(disagreement, |error|)
- r(index, |error|), from 4,000 resamples at seed 20260829, times z_0.975 + z_0.80. The same SD for the step-size margin
itself is reported alongside, after the reading.

READING, at h = 100:
  DISAGREEMENT BEATS STEP SIZE   the interval's lower bound > 0
  STEP SIZE BEATS DISAGREEMENT   the interval's upper bound < 0
  NOT RESOLVED                   otherwise
ALONGSIDE, never governing: h = 32 with the label it would carry; the partial r(disagreement, |error| | step size)
(e7_free_baselines._partial) at both horizons, with the same interval; both correlations; the counts.

ASSERTIONS, before any reading (a failure stops the run; nothing is read):
  (a) on the 400-step unit at h = 368, the imported functions reproduce results/e7_free_baselines.json's r values for
      every baseline and the step-size margin, to 1e-9; load_panel(starts, length) given the default starts equals the
      default call bitwise;
  (b) this script's resampling loop at e7's settings (4,000 resamples, default_rng(20260829), shared in e7's order)
      reproduces e7's step-size margin_ci and partial_ci, to 1e-9;
  (c) the MDE computation at M-51's settings reproduces results/e7_free_baselines_power.json, to 1e-9;
  (d) at each h, M-64's two unit counts agree (from the episode lengths and from the built index), and every unit lies
      inside one episode.
A non-finite value in the reading, or any internal check failing, stops the run with a .blocked record and no reading.

  python scripts/x6_stepsize_short_units.py --self-test     # synthetic values only
  python scripts/x6_stepsize_short_units.py --assert-only   # assertions (a)-(c), on the 400-step unit only
  python scripts/x6_stepsize_short_units.py                 # self-test, assertions, then the rule (refuses unless
                                                            # ledger M-88 records this file's SHA-256)
Writes results/x6_stepsize_short_units.json.
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

import e7_free_baselines as E7  # noqa: E402
import m64_short_units as M64  # noqa: E402
import rwm_data as R  # noqa: E402

RULE_ID = "M-88"
HS = (32, 100)
H_READ = 100
N_BOOT, BOOT_SEED = 20000, 0                     # Annex 2's interval
E7_SEED = 20260829                               # e7_free_baselines' own resampling seed
LABELS = ("DISAGREEMENT BEATS STEP SIZE", "STEP SIZE BEATS DISAGREEMENT", "NOT RESOLVED")
TOL = 1e-9
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
OUT = os.path.join(R.RESULTS, "x6_stepsize_short_units.json")
MODULES = ("scripts/x6_stepsize_short_units.py", "scripts/e7_free_baselines.py", "scripts/m64_short_units.py",
           "src/score_reference.py", "src/rwm_data.py", "src/rollout_eval.py", "src/rwm_metrics.py")


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
    raise SystemExit(f"BLOCKED: {reason} (results/x6_stepsize_short_units.json.blocked); no reading written")


def label(lo, hi):
    if lo > 0:
        return LABELS[0]
    if hi < 0:
        return LABELS[1]
    return LABELS[2]


def boot(fn, n, n_boot, rng):
    """e7_free_baselines' resampling loop (main()'s closure), with its generator passed in: whole units resampled with
    replacement, the statistic recomputed, non-finite draws dropped, percentiles 2.5 and 97.5."""
    v = [fn(rng.integers(0, n, n)) for _ in range(n_boot)]
    v = np.array([x for x in v if np.isfinite(x)])
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))], int(len(v))


def margin_of(dis, step, err):
    return lambda i: E7._corr(dis[i], err[i]) - E7._corr(step[i], err[i])


def mde(D, rng_seed=E7_SEED, n_boot=E7.N_BOOT):
    """M-51's method (e7_free_baselines.power), at this panel, from disagreement, |error| and the forecast index only --
    the step size is not touched, so this is recorded before the reading: the bootstrap SD of the margin over the
    forecast index and of the partial given it, times z_0.975 + z_0.80."""
    err, dis, fidx, n = D["err"], D["dis"], D["fidx"], D["n_traj"]
    rng = np.random.default_rng(rng_seed)
    vd = [E7._corr(dis[i], err[i]) - E7._corr(fidx[i], err[i]) for i in (rng.integers(0, n, n) for _ in range(n_boot))]
    vp = [E7._partial(dis[i], err[i], fidx[i]) for i in (rng.integers(0, n, n) for _ in range(n_boot))]
    vd = np.array([v for v in vd if np.isfinite(v)])
    vp = np.array([v for v in vp if np.isfinite(v)])
    se_d, se_p = float(vd.std(ddof=1)), float(vp.std(ddof=1))
    z = E7.Z95 + E7.Z80
    return {"method": "M-51's (e7_free_baselines --power): (z_0.975 + z_0.80) x bootstrap SD, "
                      f"{n_boot} resamples, default_rng({rng_seed}); disagreement, |error| and the forecast index only",
            "bootstrap_se_margin_over_index": se_d, "bootstrap_se_partial_given_index": se_p,
            "mde_80pct_power": {"margin": z * se_d, "partial": z * se_p}}


def step_margin_sd(D, step, rng_seed=E7_SEED, n_boot=E7.N_BOOT):
    """Alongside, after the reading: the same bootstrap SD for the step-size margin itself, and its MDE."""
    err, dis, n = D["err"], D["dis"], D["n_traj"]
    rng = np.random.default_rng(rng_seed)
    vs = np.array([x for x in (margin_of(dis, step, err)(rng.integers(0, n, n)) for _ in range(n_boot)) if np.isfinite(x)])
    return {"bootstrap_se": float(vs.std(ddof=1)), "mde": (E7.Z95 + E7.Z80) * float(vs.std(ddof=1))}


def panel(h):
    starts, eps, from_len, n_built = M64.build_index(list(range(R.N_EPISODES)), h)
    spans = {e: (s, n) for e, s, n in M64.episode_spans()}
    inside = all(spans[e][0] <= s and s + M64.START + h <= spans[e][0] + spans[e][1] for s, e in zip(starts, eps))
    D = E7.load_panel(starts=starts, length=M64.START + h)
    assert D["T"] == h and D["n_traj"] == n_built, (D["T"], D["n_traj"], n_built)
    return D, {"h": h, "unit_length": int(M64.START + h), "n_units": int(n_built), "n_from_episode_lengths": int(from_len),
               "counts_agree": bool(from_len == n_built), "units_inside_episodes": bool(inside),
               "n_independent_unit_level": int(D["n_ind"]), "n_episodes": int(len(set(eps.tolist())))}


def read_h(D):
    B = E7.baselines(D)
    err, dis, step, n = D["err"], D["dis"], B["step-size"], D["n_traj"]
    for name, a in (("error", err), ("disagreement", dis), ("step size", step)):
        if not np.all(np.isfinite(a)):
            raise NonFinite(f"non-finite {name} in the panel")
    rng = np.random.default_rng(BOOT_SEED)
    m_ci, m_n = boot(margin_of(dis, step, err), n, N_BOOT, rng)
    p_ci, p_n = boot(lambda i: E7._partial(dis[i], err[i], step[i]), n, N_BOOT, rng)
    r_dis, r_step = E7._corr(dis, err), E7._corr(step, err)
    if not all(np.isfinite([r_dis, r_step, *m_ci, *p_ci])):
        raise NonFinite("a non-finite correlation or interval")
    return {"r_disagreement_error": r_dis, "r_step_size_error": r_step, "margin": r_dis - r_step,
            "margin_ci": m_ci, "margin_label": label(*m_ci), "n_finite_draws_margin": m_n,
            "partial_disagreement_given_step_size": E7._partial(dis, err, step), "partial_ci": p_ci,
            "n_finite_draws_partial": p_n, "step_size_margin_sd": step_margin_sd(D, step)}


# ------------------------------------------------------------------ assertions on the 400-step unit
def assertions():
    committed = json.load(open(os.path.join(R.RESULTS, "e7_free_baselines.json")))
    power = json.load(open(os.path.join(R.RESULTS, "e7_free_baselines_power.json")))
    D = E7.load_panel()
    D2 = E7.load_panel(starts=E7.MET.non_overlapping_starts(*_ep_and_allep(), E7.LEN), length=E7.LEN)
    same = all(np.array_equal(D[k], D2[k]) for k in ("P", "S", "err", "dis", "fidx", "entry_res"))
    B = E7.baselines(D)
    B["forecast-index"] = D["fidx"]
    rows = {r["baseline"]: r for r in committed["baselines"]}
    d_r = max(max(abs(E7._corr(B[k], D["err"]) - rows[k]["r_baseline_error"]),
                  abs(E7._corr(D["dis"], D["err"]) - rows[k]["r_disagreement_error"]),
                  abs(E7._corr(D["dis"], D["err"]) - E7._corr(B[k], D["err"]) - rows[k]["margin"])) for k in rows)
    a = {"pass": bool(same and d_r <= TOL), "max_abs_diff": d_r, "default_starts_bitwise": bool(same),
         "step_size_margin": E7._corr(D["dis"], D["err"]) - E7._corr(B["step-size"], D["err"]),
         "against": "results/e7_free_baselines.json"}
    rng = np.random.default_rng(E7_SEED)
    n = D["n_traj"]
    m_ci, _ = boot(margin_of(D["dis"], B["step-size"], D["err"]), n, E7.N_BOOT, rng)
    p_ci, _ = boot(lambda i: E7._partial(D["dis"][i], D["err"][i], B["step-size"][i]), n, E7.N_BOOT, rng)
    d_b = max(abs(x - y) for x, y in zip(m_ci + p_ci, rows["step-size"]["margin_ci"] + rows["step-size"]["partial_ci"]))
    b = {"pass": bool(d_b <= TOL), "max_abs_diff": d_b, "settings": f"{E7.N_BOOT} resamples, default_rng({E7_SEED})"}
    md = mde(D)
    d_c = max(abs(md["bootstrap_se_margin_over_index"] - power["bootstrap_se_margin"]),
              abs(md["bootstrap_se_partial_given_index"] - power["bootstrap_se_partial"]),
              abs(md["mde_80pct_power"]["margin"] - power["mde_80pct_power"]["margin"]),
              abs(md["mde_80pct_power"]["partial"] - power["mde_80pct_power"]["partial"]))
    c = {"pass": bool(d_c <= TOL), "max_abs_diff": d_c, "against": "results/e7_free_baselines_power.json"}
    return {"a": a, "b": b, "c": c}


def _ep_and_allep():
    _, ep = R.load_data(R.repo_paths()["csv"], verbose=False)
    return ep, list(range(R.N_EPISODES))


def ledger_hashes(text):
    """Every 64-hex-digit token in backticks inside the ledger entry headed `### M-88 — `, lower-cased."""
    m = re.search(rf"^### {RULE_ID} — .*?(?=^### |\Z)", text, flags=re.M | re.S)
    return [] if not m else [x.lower() for x in re.findall(r"`([0-9a-fA-F]{64})`", m.group(0))]


def self_test():
    fails = []

    def check(name, cond):
        if not cond:
            fails.append(name)
    check("label lower > 0", label(0.01, 0.2) == LABELS[0])
    check("label upper < 0", label(-0.2, -0.01) == LABELS[1])
    check("label spans zero", label(-0.1, 0.1) == LABELS[2] and label(0.0, 0.1) == LABELS[2])
    rng = np.random.default_rng(3)
    err = rng.normal(size=(40, 20))
    dis = err + 0.1 * rng.normal(size=err.shape)
    step = rng.normal(size=err.shape)
    ci, _ = boot(margin_of(dis, step, err), 40, 500, np.random.default_rng(0))
    check("a strong signal against noise: disagreement beats", label(*ci) == LABELS[0])
    ci2, _ = boot(margin_of(step, dis, err), 40, 500, np.random.default_rng(0))
    check("swapped: step size beats", label(*ci2) == LABELS[1])
    ci3, _ = boot(margin_of(dis, dis, err), 40, 500, np.random.default_rng(0))
    check("identical signals: the margin is exactly zero", ci3 == [0.0, 0.0] and label(*ci3) == LABELS[2])
    h1 = "f" * 64
    fake = f"### M-87 — x\n`{'e' * 64}`\n### {RULE_ID} — PRE-REGISTERED rule X6\n`{h1}`\n### M-89 — y\n`{'d' * 64}`\n"
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
        asserts = assertions()
    except AssertionError as e:
        blocked(f"an internal check failed during the assertions: {e}")
    for k, v in asserts.items():
        print(f"  assertion ({k}): {'PASS' if v['pass'] else 'FAIL'}  max_abs_diff {v['max_abs_diff']:.1e}")
    if not all(v["pass"] for v in asserts.values()):
        blocked("assertion(s) failed", assertions=asserts)
    if args.assert_only:
        print("  --assert-only: assertions (a)-(c) pass; no short unit was rolled out and nothing was read")
        return
    try:
        units, panels, mdes, readings = {}, {}, {}, {}
        for h in HS:
            panels[h], u = panel(h)
            if not (u["counts_agree"] and u["units_inside_episodes"]):
                blocked(f"assertion (d) failed at h = {h}", units=u)
            units[str(h)] = u
        for h in HS:                       # the MDE, from disagreement, error and the index only, before any reading
            mdes[str(h)] = mde(panels[h])
            print(f"  MDE at h = {h} ({units[str(h)]['n_units']} units): margin {mdes[str(h)]['mde_80pct_power']['margin']:.4f}")
        for h in HS:
            readings[str(h)] = read_h(panels[h])
    except (AssertionError, NonFinite) as e:
        blocked(f"the reading stopped: {e}", assertions=asserts)
    asserts["d"] = {"pass": True, "units": units}
    g = readings[str(H_READ)]
    out = {"rule": "X6", "ledger": RULE_ID, "script": "scripts/x6_stepsize_short_units.py", "script_sha256": me,
           "exploratory": True, "never_reopens": "M-51, M-52, M-64 or any discharged rule; nothing here changes a verdict",
           "design": {"model": "the released checkpoint, ensemble of 5", "units": units, "horizons": list(HS),
                      "governing_h": H_READ, "panel": "e7_free_baselines.load_panel(starts, length)",
                      "statistic": "r(disagreement, |error|) - r(step size, |error|), Pearson over every (unit, step) cell",
                      "interval": f"{N_BOOT} Monte Carlo resamples of whole units, default_rng({BOOT_SEED}), paired"},
           "assertions": asserts,
           "mde_recorded_before_the_reading": mdes,
           "reading": {"h": H_READ, "label": g["margin_label"], "margin": g["margin"], "ci95": g["margin_ci"],
                       "n_units": units[str(H_READ)]["n_units"]},
           "alongside": {"h32": {k: readings["32"][k] for k in ("margin", "margin_ci", "r_disagreement_error",
                                                                "r_step_size_error")},
                         "h32_label_it_would_carry": readings["32"]["margin_label"],
                         "partial_disagreement_given_step_size": {str(h): {"value": readings[str(h)]["partial_disagreement_given_step_size"],
                                                                           "ci95": readings[str(h)]["partial_ci"]} for h in HS},
                         "h100_correlations": {k: g[k] for k in ("r_disagreement_error", "r_step_size_error")},
                         "step_size_margin_sd": {str(h): readings[str(h)]["step_size_margin_sd"] for h in HS},
                         "status": "alongside, not a reading"},
           "caveats": ["the released checkpoint trained on all ten episodes: every unit is in its training data",
                       "units are non-overlapping within an episode but not independent across the ten episodes; "
                       "the interval resamples units, not episodes",
                       "a correlation over (unit, step) cells, not a ranking of units"],
           "code_sha256": {p: sha256(os.path.join(ROOT, p)) for p in MODULES},
           "git_head": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()}
    json.dump(out, open(OUT, "w"), indent=2)
    print(f"  X6 returns: {g['margin_label']}  margin {g['margin']:+.4f} [{g['margin_ci'][0]:+.4f}, {g['margin_ci'][1]:+.4f}]"
          f" over {units[str(H_READ)]['n_units']} units")
    print(f"  wrote {R.rel(OUT)}")


if __name__ == "__main__":
    main()
