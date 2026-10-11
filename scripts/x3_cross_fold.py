"""
Rule X3 (ledger M-86; PRE-REGISTERED, exploratory) -- does the base claim replicate when each episode is held out
in turn? Round 4, PLAN Annex 2 X3.

It never re-opens M-23 or any discharged rule, and nothing it returns changes a verdict. The 4.61x headline is at
10,000 iterations on fold {1, 8} and is not re-read here.

FOLDS. {1, 8} (the existing runs: runs/arm{A,B}_seed<s>/weights_2500.pt) and {0, 2}, {3, 4}, {5, 6}, {7, 9}, the
remaining episodes paired in index order (runs/x3_arm{A,B}_ho<ab>_seed<s>/weights_2500.pt, trained by
scripts/step5_train.py --holdout). Every episode is out of sample in exactly one fold. Arm A and Arm B, 2,500
iterations, the seeds results/round4_queue_timing.json queued (0-2, by ruling F1-x3-cap). Each fold's configuration
is the existing 2,500-iteration runs' except the held-out pair.

ARENA. Each fold's held-out pair as non-overlapping 400-step trajectories (scripts/mn_sweep_eval.py's arena(): 32
history rows, then 368 forecast rows; 4 per fold), pooled over the five folds: n = 20 independent trajectories.
Scoring is mn_sweep_eval.score(), imported: the rollout at the causal pairing and section 3.1's relative-L1,
cumulative over forecast steps 1..h, h in {1, 8, 32, 100, 128, 368}.

STATISTIC. Per trajectory, gap = (seed-mean relative-L1 of Arm B) - (seed-mean relative-L1 of Arm A) at h = 368.
Its mean over the 20 trajectories, with a 95% interval from M-23's three-seed bootstrap, imported:
review_bootstrap_unit.boot_cluster (whole trajectories resampled, every seed carried, seeds pooled inside each draw),
at a1_ab_by_horizon's N_BOOT = 20,000 Monte Carlo draws and BOOT_SEED = 0. Assertion (e) shows that this function at
those settings reproduces the committed three-seed intervals.

READING, at h = 368:
  REPLICATES ACROSS FOLDS   the interval's lower bound > 0
  REVERSES                  the interval's upper bound < 0
  NOT RESOLVED              otherwise
PART OF THE RULE, reported verbatim, with no verdict of its own:
  the per-episode sign test: for each of the ten episodes, the sign of its mean gap at h = 368 (the mean of its two
    trajectories' gaps), the count positive and the exact two-sided binomial P (a1_ab_by_horizon.sign_p, imported);
  each fold's gap at h = 368 with its exact interval over all 256 ordered resamples of its four trajectories
    (p5_sweep_power.boot_ci, imported).
ALONGSIDE, never governing:
  h = 100, the same statistic and interval, with the label it would carry;
  h = 1 on M-64's 33-row units pooled over the five folds' held-out episodes: the A/B gap as M-64 defines it
    (B - A, so negative is teacher forcing ahead), with M-64's unit-level interval and its episode-level footnote
    (m64_short_units.build_index, unit_rollout, rel_l1 and boot_ci, imported);
  the A/B ratio of means (mean of Arm B's seed means over mean of Arm A's) at every horizon.

ASSERTIONS, before any reading of a new fold (a failure stops the run; nothing is read):
  (a) with {1, 8}, rollout_eval.fold_split() gives the same training windows as make_split(seed=0): the SHA-256 of
      the int64 index list, both ways, and its length equals the committed n_train_windows;
  (b) F1's 50-iteration reproduction (docs/presubmission/round4/f1_fold_support.json) recorded PASS, where present;
  (c) each new fold's training set excludes exactly its two episodes, no training window touches them, and its four
      held-out trajectories lie inside them;
  (d) fold {1, 8}'s readings reproduce the committed 2,500-iteration held-out relative-L1 at every horizon, to 1e-6:
      Arm A per seed and per trajectory against results/mn_compute_matched.json (part2_centre_at_more_compute
      per_seed["2500"] and three_seed_mean_l1["2500"]); Arm B per seed against results/x3_armB_2500_reference.json;
  (e) boot_cluster at N_BOOT and BOOT_SEED, fed results/a1_ab_by_horizon.json's per-trajectory values, reproduces its
      gap_ci at every horizon to 1e-6;
  (f) M-64's machinery, imported, reproduces results/m64_short_units.json cell C (held-out pair, h = 1, 10,000
      iterations): its means, gap, unit-level interval and episode-level interval, to 1e-9;
  (g) p5_sweep_power.boot_ci reproduces results/baselines_verdict.json's M-76 exact intervals, and
      a1_ab_by_horizon.sign_p its sign-test P values, to 1e-12;
  (h) every new run's record says rule X3, 2,500 iterations, its fold's held-out pair and finite losses, and its
      weights exist (F5's gate checks the queue; this checks each record the reading uses).
(a)-(g) need no new run; --assert-only runs them and reads nothing. A non-finite score anywhere the reading uses, or
any internal check failing, stops the run with results/x3_cross_fold.json.blocked and no reading (M-76's failure
clause). The script runs from the repository root wherever it is started.

  python scripts/x3_cross_fold.py --self-test     # synthetic values only: the statistic, the labels, the tests
  python scripts/x3_cross_fold.py --assert-only   # assertions (a)-(g); no new run is loaded
  python scripts/x3_cross_fold.py                 # self-test, assertions, then the rule (refuses unless ledger
                                                  # M-86 records this file's SHA-256 and every queued run checks out)
Writes results/x3_cross_fold.json. NEEDS_WEIGHTS: the runs are gitignored.
"""
import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import torch  # noqa: E402

import a1_ab_by_horizon as A1  # noqa: E402
import m64_short_units as M64  # noqa: E402
import mn_sweep_eval as MN  # noqa: E402
import p5_sweep_power as P5  # noqa: E402
import review_bootstrap_unit as RB  # noqa: E402
import rollout_eval as E  # noqa: E402
import rwm_data as R  # noqa: E402
import rwm_metrics as MET  # noqa: E402
import rwm_model as M  # noqa: E402
import rwm_train as T  # noqa: E402

RULE_ID = "M-86"
FOLDS = ((1, 8), (0, 2), (3, 4), (5, 6), (7, 9))
HS = tuple(MN.HORIZONS)                     # (1, 8, 32, 100, 128, 368)
H_READ, H_ALONG = 368, 100
ITERS = 2500
M_HIST = 32
TOL, TOL_M64, TOL_EXACT = 1e-6, 1e-9, 1e-12
LABELS = ("REPLICATES ACROSS FOLDS", "REVERSES", "NOT RESOLVED")
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
OUT = os.path.join(R.RESULTS, "x3_cross_fold.json")
STRAT = os.path.join(R.RESULTS, "step0_strat.json")
MODULES = ("scripts/x3_cross_fold.py", "scripts/mn_sweep_eval.py", "scripts/review_bootstrap_unit.py",
           "scripts/a1_ab_by_horizon.py", "scripts/p5_sweep_power.py", "scripts/m64_short_units.py",
           "src/rollout_eval.py", "src/rwm_data.py", "src/rwm_metrics.py", "src/rwm_model.py", "src/rwm_train.py")


def fid(fold):
    return "".join(map(str, fold))


def label(lo, hi):
    if lo > 0:
        return LABELS[0]
    if hi < 0:
        return LABELS[1]
    return LABELS[2]


def weights_path(arm, fold, s, runs="runs"):
    if tuple(fold) == (1, 8):
        return os.path.join(runs, f"arm{arm}_seed{s}", f"weights_{ITERS}.pt")
    return os.path.join(runs, f"x3_arm{arm}_ho{fid(fold)}_seed{s}", f"weights_{ITERS}.pt")


def run_record(arm, fold, s, results=R.RESULTS):
    if tuple(fold) == (1, 8):
        return os.path.join(results, f"step5_arm{arm}_seed{s}.json")
    return os.path.join(results, f"x3_run_arm{arm}_ho{fid(fold)}_seed{s}.json")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def blocked(reason, **detail):
    json.dump({"BLOCKED": reason, **detail}, open(OUT + ".blocked", "w"), indent=1, default=str)
    raise SystemExit(f"BLOCKED: {reason} (results/x3_cross_fold.json.blocked); no reading written")


def load(cfg, path):
    m = M.build_from_config(cfg, ensemble_size=1)
    m.load_state_dict(torch.load(path, map_location="cpu")["model_state_dict"], strict=True)
    m.eval()
    return m


def split_of(fold):
    return (E.make_split(seed=0, strat_path=STRAT, verbose=False) if tuple(fold) == (1, 8)
            else E.fold_split(fold, strat_path=STRAT))


# ------------------------------------------------------------------ the statistics, all imported
def pooled(Am, Bm):
    """Am, Bm: (n_seed, n_traj) relative-L1. The rule's statistic and its interval (boot_cluster, imported)."""
    gap = Bm.mean(0) - Am.mean(0)
    _, lo, hi = RB.boot_cluster(Am, Bm, n=A1.N_BOOT, seed=A1.BOOT_SEED)
    return {"gap": float(gap.mean()), "ci95": [float(lo), float(hi)], "n_trajectories": int(gap.size),
            "label": label(lo, hi), "per_trajectory_gap": [float(x) for x in gap]}


def sign_test(gap, episode_of_traj):
    per_ep = {}
    for g, e in zip(gap, episode_of_traj):
        per_ep.setdefault(int(e), []).append(float(g))
    means = {str(e): float(np.mean(v)) for e, v in sorted(per_ep.items())}
    k = sum(1 for v in means.values() if v > 0)
    return {"per_episode_mean_gap": means, "n_episodes": len(means), "n_positive": k,
            "n_negative": sum(1 for v in means.values() if v < 0), "exact_two_sided_p": A1.sign_p(k, len(means))}


def per_fold_exact(gap_fold):
    return {"gap": float(np.mean(gap_fold)), "ci95_exact": P5.boot_ci(gap_fold), "n_trajectories": len(gap_fold),
            "per_trajectory_gap": [float(x) for x in gap_fold]}


# ------------------------------------------------------------------ scoring
def score_fold(cfg, data, ep, fold, seeds, runs="runs"):
    split = split_of(fold)
    assert split["holdout_episodes"] == sorted(fold)
    scale = MET.training_scale(data, ep, split["train_episodes"], cfg["state_data_mean"], cfg["state_data_std"])
    ar = MN.arena(ep, list(fold), M_HIST)
    assert ar["n_independent"] == 4 and len(ar["starts"]) == 4, ar
    per, sha = {}, {}
    for arm in ("A", "B"):
        for s in seeds:
            w = weights_path(arm, fold, s, runs)
            sha[f"{arm}{s}"] = sha256(w)
            per[(arm, s)] = MN.score(load(cfg, w), data, cfg, scale, ar["starts"], M_HIST, M_HIST)
    return {"arena": ar, "per": per, "weights_sha256": sha}


def m64_units(cfg, data, folds, seeds, paths_of):
    """h = 1 on M-64's 33-row units over the folds' held-out episodes: per unit, A and B seed means."""
    st_all, ep_all, A_all, B_all, counts = [], [], [], [], {}
    for fold in folds:
        st, ue, from_len, n_built = M64.build_index(list(fold), 1)
        assert from_len == n_built, (fold, from_len, n_built)
        counts[fid(fold)] = int(n_built)
        vals = {}
        for arm in ("A", "B"):
            vals[arm] = np.stack([M64.rel_l1(*M64.unit_rollout(load(cfg, paths_of(arm, fold, s)), data, cfg, st, 1,
                                                                False)[3:5]) for s in seeds]).mean(0)
        st_all.append(st); ep_all.append(ue); A_all.append(vals["A"]); B_all.append(vals["B"])
    A, B, ue = np.concatenate(A_all), np.concatenate(B_all), np.concatenate(ep_all)
    gap = B - A
    gu, ge = M64.boot_ci(gap, None, ue)
    return {"A_mean": float(A.mean()), "B_mean": float(B.mean()), "ratio_B_over_A": float(B.mean() / A.mean()),
            "gap": float(gap.mean()), "gap_ci_unit_level": gu, "gap_excludes_zero": M64.excl0(gu),
            "footnote_episode_level": {"gap_ci": ge, "excludes_zero": M64.excl0(ge)},
            "n_units": int(gap.size), "units_per_fold": counts, "unit_length": M64.START + 1,
            "sign_convention": "B - A, as M-64 defines it: negative is teacher forcing (Arm B) ahead"}


# ------------------------------------------------------------------ assertions
def assert_a(data, ep, cfg):
    def starts(split):
        s = np.asarray(T.WindowDataset(data, ep, split["train_episodes"], cfg).starts, dtype=np.int64)
        return s, hashlib.sha256(s.tobytes()).hexdigest()
    sd, hd = starts(E.make_split(seed=0, strat_path=STRAT, verbose=False))
    sf, hf = starts(E.fold_split([1, 8], strat_path=STRAT))
    committed = [json.load(open(run_record(a, (1, 8), 0)))["hyperparameters"]["n_train_windows"] for a in "AB"]
    ok = hd == hf and all(c == len(sd) for c in committed)
    return {"pass": bool(ok), "sha256": hd, "n_windows": int(len(sd)), "committed_n_train_windows": committed}


def assert_b():
    p = os.path.join(ROOT, "docs", "presubmission", "round4", "f1_fold_support.json")
    if not os.path.exists(p):
        return {"pass": True, "note": "f1_fold_support.json is not in this copy (docs/presubmission ships in no bundle)"}
    b = json.load(open(p)).get("b", {})
    return {"pass": bool(b.get("pass")), "source": "docs/presubmission/round4/f1_fold_support.json",
            "runs": [r["label"] for r in b.get("runs", [])]}


def assert_c(data, ep, cfg):
    rows = []
    for fold in FOLDS[1:]:
        s = E.fold_split(fold, strat_path=STRAT)
        excl = sorted(set(range(R.N_EPISODES)) - set(s["train_episodes"]))
        ds = T.WindowDataset(data, ep, s["train_episodes"], cfg)
        idx = np.asarray(ds.starts)[:, None] + np.arange(T.WINDOW)[None, :]
        ar = MN.arena(ep, list(fold), M_HIST)
        inside = all(set(ep[st:st + M_HIST + MN.FORECAST].tolist()) <= set(fold) for st in ar["starts"])
        rows.append({"fold": list(fold), "pass": bool(excl == sorted(fold) and not np.isin(ep[idx], fold).any()
                                                      and inside and ar["n_independent"] == 4)})
    return {"pass": all(r["pass"] for r in rows), "folds": rows}


def assert_d(fold18, seeds):
    mc = json.load(open(os.path.join(R.RESULTS, "mn_compute_matched.json")))["part2_centre_at_more_compute"]
    ref = json.load(open(os.path.join(R.RESULTS, "x3_armB_2500_reference.json")))
    dA = max(abs(float(v) - w) for s in seeds for h in HS
             for v, w in zip(fold18["per"][("A", s)][str(h)]["l1"], mc["per_seed"]["2500"][str(s)]["held_out"][str(h)]))
    dA3 = max(abs(float(np.mean([np.mean(fold18["per"][("A", s)][str(h)]["l1"]) for s in seeds]))
                  - mc["three_seed_mean_l1"]["2500"]["held_out"][str(h)]) for h in HS)
    dB = max(abs(float(np.mean(fold18["per"][("B", s)][str(h)]["l1"]))
                 - ref["armB"]["per_model"][f"armB_teacher_forced_seed{s}"][str(h)]["l1"]) for s in seeds for h in HS)
    starts_ok = fold18["arena"]["starts"] == ref["traj_start_row"] == list(MN.HELD_OUT_STARTS)
    return {"pass": bool(max(dA, dA3, dB) <= TOL and starts_ok and sorted(ref["arm_seeds"]) == sorted(seeds)
                         and [int(h) for h in ref["horizons"]] == list(HS)),
            "armA_per_trajectory_max_abs_diff": dA, "armA_three_seed_max_abs_diff": dA3,
            "armB_per_seed_max_abs_diff": dB, "tolerance": TOL, "horizons": list(HS),
            "against": ["results/mn_compute_matched.json", "results/x3_armB_2500_reference.json"]}


def assert_e():
    a1 = json.load(open(os.path.join(R.RESULTS, "a1_ab_by_horizon.json")))
    d = 0.0
    for h, b in a1["by_horizon"].items():
        _, lo, hi = RB.boot_cluster(np.array(b["A_per_trajectory"])[None], np.array(b["B_per_trajectory"])[None],
                                    n=A1.N_BOOT, seed=A1.BOOT_SEED)
        d = max(d, abs(lo - b["gap_ci"][0]), abs(hi - b["gap_ci"][1]))
    return {"pass": bool(d <= TOL), "max_abs_diff": d, "n_boot": A1.N_BOOT, "seed": A1.BOOT_SEED,
            "against": "results/a1_ab_by_horizon.json by_horizon[*].gap_ci"}


def assert_f(cfg, data, seeds):
    c = json.load(open(os.path.join(R.RESULTS, "m64_short_units.json")))["cells"]["C_section_5_ab_gap"]
    c = c["out-of-sample held-out pair"]["1"]
    got = m64_units(cfg, data, [(1, 8)], seeds,
                    lambda arm, fold, s: os.path.join("runs", f"arm{arm}_seed{s}_10k", "weights_10000.pt"))
    pairs = [(got["A_mean"], c["A_mean"]), (got["B_mean"], c["B_mean"]), (got["gap"], c["gap"])] + \
        list(zip(got["gap_ci_unit_level"], c["gap_ci_unit_level"])) + \
        list(zip(got["footnote_episode_level"]["gap_ci"], c["footnote_episode_level"]["gap_ci"]))
    d = max(abs(a - b) for a, b in pairs)
    return {"pass": bool(d <= TOL_M64 and got["n_units"] == c["n_independent_unit_level"]), "max_abs_diff": d,
            "n_units": got["n_units"], "against": "results/m64_short_units.json cells.C_section_5_ab_gap, held-out pair, h = 1"}


def assert_g():
    bv = json.load(open(os.path.join(R.RESULTS, "baselines_verdict.json")))["rules"]["M-76"]["governing"]["per_baseline"]
    d1 = max(abs(a - b) for v in bv.values() for a, b in zip(P5.boot_ci(v["per_traj"]), v["ci95"]))
    st = json.load(open(os.path.join(R.RESULTS, "a1_ab_by_horizon.json")))["sign_test"]
    d2 = max(abs(A1.sign_p(v["n_positive"], v["n_episodes"]) - v["exact_two_sided_p"]) for v in st.values())
    return {"pass": bool(max(d1, d2) <= TOL_EXACT), "boot_ci_max_abs_diff": d1, "sign_p_max_abs_diff": d2}


def assert_h(seeds, runs="runs", results=R.RESULTS):
    bad = []
    for fold in FOLDS[1:]:
        for arm in ("A", "B"):
            for s in seeds:
                p, w = run_record(arm, fold, s, results), weights_path(arm, fold, s, runs)
                if not os.path.exists(p) or not os.path.exists(w):
                    bad.append(f"{arm} {fid(fold)} seed {s}: record or weights missing")
                    continue
                a = json.load(open(p))
                hp = a["hyperparameters"]
                if (a.get("rule") != "X3" or hp["iterations"] != ITERS or hp["holdout_episodes"] != sorted(fold)
                        or a["seed"] != s or a["arm"] != arm
                        or any(not math.isfinite(x) for v in a["curves"].values() for x in v)):
                    bad.append(f"{arm} {fid(fold)} seed {s}: record does not match the queued run")
    return {"pass": not bad, "problems": bad}


# ------------------------------------------------------------------ the ledger
def ledger_hashes(text):
    """Every 64-hex-digit token in backticks inside the ledger entry headed `### M-86 — `, lower-cased."""
    m = re.search(rf"^### {RULE_ID} — .*?(?=^### |\Z)", text, flags=re.M | re.S)
    return [] if not m else [h.lower() for h in re.findall(r"`([0-9a-fA-F]{64})`", m.group(0))]


def self_test():
    """Synthetic values only; no data, no weights, no reading."""
    fails = []

    def check(name, cond):
        if not cond:
            fails.append(name)
    check("label lower > 0", label(0.1, 0.5) == LABELS[0])
    check("label upper < 0", label(-0.5, -0.1) == LABELS[1])
    check("label spans zero", label(-0.1, 0.5) == LABELS[2])
    check("label touches zero", label(0.0, 0.5) == LABELS[2] and label(-0.5, 0.0) == LABELS[2])
    rng = np.random.default_rng(1)
    A = rng.uniform(0.2, 0.4, (3, 20))
    up = pooled(A, A + 0.5)
    check("a uniform positive gap replicates", up["label"] == LABELS[0] and abs(up["gap"] - 0.5) < 1e-12)
    dn = pooled(A, A - 0.1)
    check("a uniform negative gap reverses", dn["label"] == LABELS[1])
    mix = pooled(A, A + np.where(np.arange(20) % 2 == 0, 1.0, -1.0)[None, :])
    check("an alternating gap is not resolved", mix["label"] == LABELS[2])
    check("the pooled gap is the mean of seed-mean gaps",
          abs(mix["gap"] - float(((A + np.where(np.arange(20) % 2 == 0, 1.0, -1.0)[None, :]).mean(0) - A.mean(0)).mean())) < 1e-12)
    eps = np.repeat(np.arange(10), 2)
    st = sign_test(np.where(eps < 7, 1.0, -1.0), eps)
    check("sign test counts episodes", st["n_positive"] == 7 and st["n_negative"] == 3 and st["n_episodes"] == 10)
    check("sign test P", abs(st["exact_two_sided_p"] - A1.sign_p(7, 10)) < 1e-15)
    pf = per_fold_exact([0.1, 0.2, 0.3, 0.4])
    check("per-fold exact interval inside the data's range", 0.1 <= pf["ci95_exact"][0] <= pf["ci95_exact"][1] <= 0.4)
    h1 = "a" * 64
    fake = (f"### M-85 — x\n`{'b' * 64}`\n### {RULE_ID} — PRE-REGISTERED rule X3\n`{h1}`\n**Status** x\n"
            f"### M-87 — y\n`{'c' * 64}`\n")
    check("ledger: the entry's own hash only", ledger_hashes(fake) == [h1])
    check("ledger: another entry's hash does not count", ledger_hashes(fake.replace(f"### {RULE_ID} ", "### M-99 ")) == [])
    print(f"  self-test: {'PASS' if not fails else 'FAIL ' + str(fails)} (synthetic values; no reading)")
    return not fails


def seeds_queued():
    t = json.load(open(os.path.join(R.RESULTS, "round4_queue_timing.json")))
    assert not t["blocked"], "the timing record is BLOCKED"
    return tuple(t["x3"]["seeds"])


class NonFinite(Exception):
    pass


def finite_or_raise(scores, m64, seeds):
    bad = [f"{fid(f)} arm {arm} seed {s} h {h}" for f, sc in scores.items() for arm in ("A", "B") for s in seeds
           for h in HS if not np.all(np.isfinite(sc["per"][(arm, s)][str(h)]["l1"]))]
    if not all(np.isfinite(m64[k]) for k in ("A_mean", "B_mean", "gap")):
        bad.append("the M-64 h = 1 units")
    if bad:
        raise NonFinite(f"non-finite relative-L1: {bad[:8]}")


def reading(cfg, data, ep, seeds, fold18, runs="runs"):
    """Everything main() computes after the assertions: the scores of the new folds, the reading, the part-of-rule and
    alongside values. Separate from main() so that a dry run on untrained weights can exercise it whole."""
    scores = {(1, 8): fold18}
    for fold in FOLDS[1:]:
        scores[fold] = score_fold(cfg, data, ep, fold, seeds, runs)
    m64 = m64_units(cfg, data, FOLDS, seeds, lambda arm, fold, s: weights_path(arm, fold, s, runs))
    finite_or_raise(scores, m64, seeds)
    Am = {h: np.concatenate([np.stack([scores[f]["per"][("A", s)][str(h)]["l1"] for s in seeds]) for f in FOLDS], axis=1)
          for h in HS}
    Bm = {h: np.concatenate([np.stack([scores[f]["per"][("B", s)][str(h)]["l1"] for s in seeds]) for f in FOLDS], axis=1)
          for h in HS}
    traj_ep = [e for f in FOLDS for e in scores[f]["arena"]["episode_of_window"]]
    traj_start = [s for f in FOLDS for s in scores[f]["arena"]["starts"]]
    traj_fold = [fid(f) for f in FOLDS for _ in scores[f]["arena"]["starts"]]
    main_r = pooled(Am[H_READ], Bm[H_READ])
    along100 = pooled(Am[H_ALONG], Bm[H_ALONG])
    gap368 = np.array(main_r["per_trajectory_gap"])
    folds_r = {}
    for f in FOLDS:
        sel = [i for i, x in enumerate(traj_fold) if x == fid(f)]
        folds_r[fid(f)] = per_fold_exact(gap368[sel])
    return {
        "design": {"folds": [list(f) for f in FOLDS], "arms": ["A", "B"], "iterations": ITERS, "seeds": list(seeds),
                   "arena": "each fold's held-out pair, non-overlapping 400-step trajectories (mn_sweep_eval.arena), pooled",
                   "n_trajectories": int(gap368.size),
                   "n_independent": int(sum(scores[f]["arena"]["n_independent"] for f in FOLDS)),
                   "horizons": list(HS), "metric": "relative-L1, cumulative over forecast steps 1..h (mn_sweep_eval.score)",
                   "statistic": "mean over trajectories of (seed-mean Arm B - seed-mean Arm A) at h = 368",
                   "interval": f"review_bootstrap_unit.boot_cluster, {A1.N_BOOT} Monte Carlo draws, seed {A1.BOOT_SEED}, "
                               "whole trajectories, seeds pooled inside each draw (M-23's three-seed bootstrap)"},
        "reading": {"h": H_READ, "label": main_r["label"], "gap": main_r["gap"], "ci95": main_r["ci95"],
                    "n_trajectories": main_r["n_trajectories"]},
        "part_of_rule": {"per_episode_sign_test_h368": sign_test(gap368, traj_ep), "per_fold_h368": folds_r},
        "alongside": {"h100": {**{k: along100[k] for k in ("gap", "ci95", "n_trajectories")},
                               "label_it_would_carry": along100["label"], "status": "alongside, not a reading"},
                      "h1_m64_units": {**m64, "status": "alongside, not a reading"},
                      "ratio_B_over_A": {str(h): float(Bm[h].mean() / Am[h].mean()) for h in HS}},
        "per_trajectory": {"fold": traj_fold, "start_row": traj_start, "episode": traj_ep,
                           "armA_per_seed_l1": {str(h): Am[h].tolist() for h in HS},
                           "armB_per_seed_l1": {str(h): Bm[h].tolist() for h in HS}},
        "weights_sha256": {fid(f): scores[f]["weights_sha256"] for f in FOLDS}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--assert-only", action="store_true")
    args = ap.parse_args()
    os.chdir(ROOT)                         # the run paths are relative to the repository root
    ok = self_test()
    if args.self_test or not ok:
        sys.exit(0 if ok else 1)
    me = sha256(os.path.abspath(__file__))
    print(f"  script SHA-256 {me}")
    try:
        seeds = seeds_queued()
    except AssertionError as e:
        blocked(f"the timing record: {e}")
    if not args.assert_only:
        reg = ledger_hashes(open(os.path.join(ROOT, "FINDINGS_LEDGER.md"), encoding="utf-8").read())
        if me not in reg:
            blocked(f"ledger {RULE_ID} does not record this script's SHA-256 {me}: the rule is not pre-registered as run",
                    recorded=reg)
    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    data, ep = R.load_data(paths["csv"], verbose=False)
    stored = np.array(json.load(open(os.path.join(R.RESULTS, "step4_0a_results.json")))["nrmse_scale"])
    try:
        asserts = {"a": assert_a(data, ep, cfg), "b": assert_b(), "c": assert_c(data, ep, cfg)}
        fold18 = score_fold(cfg, data, ep, (1, 8), seeds)
        asserts["d"] = assert_d(fold18, seeds)
        asserts["e"] = assert_e()
        asserts["f"] = assert_f(cfg, data, seeds)
        asserts["g"] = assert_g()
        split18 = E.make_split(seed=0, strat_path=STRAT, verbose=False)
        assert np.allclose(MET.training_scale(data, ep, split18["train_episodes"], cfg["state_data_mean"],
                                              cfg["state_data_std"]), stored), "nRMSE scale differs from the stored one"
    except AssertionError as e:
        blocked(f"an internal check failed during the assertions: {e}")
    for k, v in asserts.items():
        print(f"  assertion ({k}): {'PASS' if v['pass'] else 'FAIL'}  " + ", ".join(
            f"{x} {y:.1e}" for x, y in v.items() if isinstance(y, float)))
    failed = [k for k, v in asserts.items() if not v["pass"]]
    if failed:
        blocked(f"assertion(s) {failed} failed", assertions=asserts)
    if args.assert_only:
        print("  --assert-only: assertions (a)-(g) pass; no new run was loaded and nothing was read")
        return
    asserts["h"] = assert_h(seeds)
    if not asserts["h"]["pass"]:
        blocked("a queued run's record does not check out (assertion h)", assertions=asserts)
    try:
        rd = reading(cfg, data, ep, seeds, fold18)
    except (AssertionError, NonFinite) as e:
        blocked(f"the reading stopped: {e}", assertions=asserts)
    ratio10k = json.load(open(os.path.join(R.RESULTS, "task_d1_threeseed.json")))["aggregate"]["ratio_B_over_A"]
    out = {"rule": "X3", "ledger": RULE_ID, "script": "scripts/x3_cross_fold.py", "script_sha256": me,
           "exploratory": True, "never_reopens": "M-23 or any discharged rule; nothing here changes a verdict",
           "assertions": asserts, **rd,
           "caveats": [f"2,500 iterations, not 10,000: section 5's {ratio10k:.2f}x headline is at 10,000 on fold {{1, 8}} "
                       "(results/task_d1_threeseed.json) and is not re-read",
                       "the new folds pair episodes in index order; {0, 2} and {3, 4} each hold two episodes from the same "
                       "speed half, unlike make_split's stratified {1, 8}",
                       "the seeds are not independent units: the interval resamples trajectories, carrying every seed"],
           "code_sha256": {p: sha256(os.path.join(ROOT, p)) for p in MODULES},
           "git_head": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip(),
           "torch_threads": torch.get_num_threads()}
    json.dump(out, open(OUT, "w"), indent=2)
    r = out["reading"]
    print(f"  X3 returns: {r['label']}  gap {r['gap']:+.4f} [{r['ci95'][0]:+.4f}, {r['ci95'][1]:+.4f}]"
          f" over {r['n_trajectories']} trajectories")
    print(f"  wrote {R.rel(OUT)}")


if __name__ == "__main__":
    main()
