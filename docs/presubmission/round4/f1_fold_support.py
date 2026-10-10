"""F1 item 1: fold support for rule X3, and its three assertions (PLAN F1 item 1).

The training driver gained `--holdout a,b` (scripts/step5_train.py), which takes its split from
src/rollout_eval.py's new fold_split() (appended at the end of the file, so no cited line moves).
Without it the driver calls make_split(seed=0) exactly as before, {1, 8}.
  (a) With {1, 8}, the training window set is byte-identical to the default path's: the
      SHA-256 of the int64 index list, both ways, and its length against the committed run
      records' n_train_windows (results/step5_arm{A,B}_seed0.json).
  (b) A 50-iteration run of Arm A, seed 0, reproduces the committed run's first 50 values of
      every loss trace in results/step5_armA_seed0.json `curves` (state, bound, contact,
      termination, total, grad_norm). The committed record holds full-precision floats, so the
      test is BITWISE (==), not to a tolerance. It is run twice: through `--holdout 1,8` and
      through the default path, each into a scratch --out-dir, so nothing committed is touched.
  (c) Each new fold's training set excludes exactly its two episodes; no training window
      touches a row of them; and its held-out trajectories (scripts/mn_sweep_eval.py's arena,
      400 rows each) lie entirely inside them.
Writes docs/presubmission/round4/f1_fold_support.json. Run from the repository root:
  $PY docs/presubmission/round4/f1_fold_support.py [--skip-b]
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, "scripts")
sys.path.insert(0, "src")
import numpy as np  # noqa: E402

import mn_sweep_eval as MN  # noqa: E402
import rollout_eval as E  # noqa: E402
import rwm_data as R  # noqa: E402
import rwm_train as T  # noqa: E402

OUT = "docs/presubmission/round4/f1_fold_support.json"
SCRATCH = os.environ.get("F1_SCRATCH", "/Users/Shared/rwm_verify/evidence/R4F1/fold_b")
FOLDS = ([0, 2], [3, 4], [5, 6], [7, 9])
TRACES = ("state", "bound", "contact", "termination", "total", "grad_norm")
STRAT = os.path.join(R.RESULTS, "step0_strat.json")


def starts_of(data, ep, cfg, split):
    ds = T.WindowDataset(data, ep, split["train_episodes"], cfg)
    s = np.asarray(ds.starts, dtype=np.int64)
    return s, hashlib.sha256(s.tobytes()).hexdigest()


def check_a(data, ep, cfg):
    d = E.make_split(seed=0, strat_path=STRAT, verbose=False)
    f = E.fold_split([1, 8], strat_path=STRAT)
    sd, hd = starts_of(data, ep, cfg, d)
    sf, hf = starts_of(data, ep, cfg, f)
    committed = {a: json.load(open(f"results/step5_arm{a}_seed0.json"))["hyperparameters"]["n_train_windows"] for a in "AB"}
    ok = (d["train_episodes"] == f["train_episodes"] and d["holdout_episodes"] == f["holdout_episodes"] == [1, 8]
          and hd == hf and np.array_equal(sd, sf) and all(v == len(sd) for v in committed.values()))
    return {"pass": bool(ok), "default_split": {k: d[k] for k in ("train_episodes", "holdout_episodes", "method")},
            "fold_split": {k: f[k] for k in ("train_episodes", "holdout_episodes", "method")},
            "n_windows": int(len(sd)), "sha256_default": hd, "sha256_holdout_1_8": hf,
            "committed_n_train_windows": committed}


def run_b(label, extra):
    out_dir = os.path.join(SCRATCH, label)
    os.makedirs(out_dir, exist_ok=True)
    cmd = [sys.executable, "scripts/step5_train.py", "--arm", "A", "--seed", "0", "--iters", "50",
           "--out-dir", out_dir] + extra
    t0 = time.time()
    with open(os.path.join(out_dir, "run.log"), "w") as f:
        rc = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT).returncode
    assert rc == 0, f"(b) {label}: the 50-iteration run exited {rc}; see {out_dir}/run.log"
    art = [x for x in os.listdir(out_dir) if x.endswith(".json")]
    assert len(art) == 1, art
    a = json.load(open(os.path.join(out_dir, art[0])))
    ref = json.load(open("results/step5_armA_seed0.json"))["curves"]
    per = {}
    for k in TRACES:
        got, want = a["curves"][k][:50], ref[k][:50]
        per[k] = {"n": len(got), "bitwise_equal": got == want,
                  "max_abs_diff": float(max(abs(x - y) for x, y in zip(got, want)))}
    return {"label": label, "command": " ".join(cmd[1:]), "artifact": art[0], "wall_s": time.time() - t0,
            "train_episodes": a["hyperparameters"]["train_episodes"],
            "holdout_episodes": a["hyperparameters"]["holdout_episodes"],
            "n_train_windows": a["hyperparameters"]["n_train_windows"], "traces": per,
            "pass": all(v["bitwise_equal"] and v["n"] == 50 for v in per.values())}


def check_c(data, ep, cfg):
    rows = []
    for fold in FOLDS:
        s = E.fold_split(fold, strat_path=STRAT)
        excl = sorted(set(range(R.N_EPISODES)) - set(s["train_episodes"]))
        ds = T.WindowDataset(data, ep, s["train_episodes"], cfg)
        idx = np.asarray(ds.starts)[:, None] + np.arange(T.WINDOW)[None, :]
        touches = int(np.isin(ep[idx], fold).sum())
        ar = MN.arena(ep, fold, 32)
        inside = all(set(ep[st:st + 32 + MN.FORECAST].tolist()) <= set(fold) for st in ar["starts"])
        one_ep = all(len(set(ep[st:st + 32 + MN.FORECAST].tolist())) == 1 for st in ar["starts"])
        rows.append({"fold": fold, "holdout_episodes": s["holdout_episodes"], "excluded_from_training": excl,
                     "n_train_windows": int(len(ds)), "window_rows_in_fold": touches,
                     "heldout_starts": ar["starts"], "n_independent": ar["n_independent"],
                     "heldout_inside_fold": bool(inside), "each_heldout_in_one_episode": bool(one_ep),
                     "pass": bool(excl == sorted(fold) and s["holdout_episodes"] == sorted(fold) and touches == 0
                                  and inside and one_ep and ar["n_independent"] == 4)})
    return {"pass": all(r["pass"] for r in rows), "folds": rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-b", action="store_true", help="(a) and (c) only; no training")
    args = ap.parse_args()
    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    data, ep = R.load_data(paths["csv"], verbose=False)
    out = {"what": "F1 item 1: fold support for rule X3 and its assertions (a)-(c)",
           "a": check_a(data, ep, cfg), "c": check_c(data, ep, cfg)}
    print(f"(a) {'PASS' if out['a']['pass'] else 'FAIL'}: {out['a']['n_windows']} windows, sha256 {out['a']['sha256_default'][:12]} both ways")
    print(f"(c) {'PASS' if out['c']['pass'] else 'FAIL'}: " + "; ".join(
        f"{r['fold']} windows {r['n_train_windows']} touching {r['window_rows_in_fold']}, held-out n {r['n_independent']}" for r in out["c"]["folds"]))
    if not args.skip_b:
        out["b"] = {"comparison": "bitwise (==): results/step5_armA_seed0.json curves hold full-precision floats",
                    "runs": [run_b("holdout_1_8", ["--holdout", "1,8"]), run_b("default", [])]}
        out["b"]["pass"] = all(r["pass"] for r in out["b"]["runs"])
        for r in out["b"]["runs"]:
            print(f"(b) {r['label']}: {'PASS' if r['pass'] else 'FAIL'} " + ", ".join(
                f"{k} {'==' if v['bitwise_equal'] else 'max |d| %.1e' % v['max_abs_diff']}" for k, v in r["traces"].items())
                  + f" ({r['wall_s']:.0f} s)")
        json.dump(out, open(OUT, "w"), indent=1)
        print("wrote", OUT)
    ok = out["a"]["pass"] and out["c"]["pass"] and out.get("b", {}).get("pass", True)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
