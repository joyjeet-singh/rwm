"""GT1 item 3: training support for rule X11, and its three assertions (PLAN GT1 item 3).

`scripts/step5_train.py --holdout a,b` now also takes `--ensemble 5` for Arm A (rule X11); the run is named
`x3_armA_ho<ab>_seed<s>_ens5`. The edit changed five lines in place and moved none, so every cited line of
the driver stays where it was. X11's single-model runs (seeds 3 and 4) use the X3 path unchanged.
  (a) For each fold, the training window list built the way the driver builds it (`T.WindowDataset` on
      `E.fold_split(fold)`) has the length every committed X3 run of that fold records (`n_train_windows`,
      `results/x3_run_armA_ho<ab>_seed{0,1,2}.json`, and `step5_armA_seed{0,1,2}.json` for {1, 8}); its
      SHA-256 is recorded, and for {1, 8} it equals round 4's (`round4/f1_fold_support.json` a). The window
      builder does not depend on the ensemble size, so this is the list the ensemble-5 runs train on.
  (b) Fifty-iteration runs reproduce the committed records' first 50 values of all six loss traces, BITWISE
      (the committed curves are full-precision floats): ensemble-5 Arm A seed 0 through `--holdout 1,8
      --ensemble 5` and through the default path (`--ensemble 5 --tag _ens5`), against
      `results/step5_armA_seed0_ens5.json`; and single-model Arm A seed 3 through `--holdout 1,8`, against
      `results/step5_armA_seed3.json` (a seed X3 never ran). Each runs into a scratch --out-dir.
  (c) Each new fold's training set excludes exactly its two episodes, no training window touches a row of
      them, and its four held-out trajectories lie inside them.
Writes docs/presubmission/round5/gt1_fold_support.json. From the repository root:
  $PY docs/presubmission/round5/gt1_fold_support.py [--skip-b]
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

OUT = "docs/presubmission/round5/gt1_fold_support.json"
SCRATCH = os.environ.get("GT1_SCRATCH", "/Users/Shared/rwm_verify/evidence/R5GT1/fold_b")
FOLDS = ([1, 8], [0, 2], [3, 4], [5, 6], [7, 9])
TRACES = ("state", "bound", "contact", "termination", "total", "grad_norm")
STRAT = os.path.join(R.RESULTS, "step0_strat.json")


def record_of(fold, s):
    if fold == [1, 8]:
        return f"results/step5_armA_seed{s}.json"
    return f"results/x3_run_armA_ho{''.join(map(str, fold))}_seed{s}.json"


def check_a(data, ep, cfg):
    f1 = json.load(open("docs/presubmission/round4/f1_fold_support.json"))["a"]["sha256_default"]
    rows = []
    for fold in FOLDS:
        sp = E.fold_split(fold, strat_path=STRAT)
        ds = T.WindowDataset(data, ep, sp["train_episodes"], cfg, window=T.WINDOW)
        st = np.asarray(ds.starts, dtype=np.int64)
        sha = hashlib.sha256(st.tobytes()).hexdigest()
        committed = {s: json.load(open(record_of(fold, s)))["hyperparameters"]["n_train_windows"] for s in (0, 1, 2)}
        ok = all(v == len(st) for v in committed.values()) and (fold != [1, 8] or sha == f1)
        rows.append({"fold": fold, "n_windows": int(len(st)), "sha256": sha,
                     "committed_n_train_windows": committed, "pass": bool(ok)})
    return {"pass": all(r["pass"] for r in rows), "round4_sha256_1_8": f1, "folds": rows}


def run_b(label, extra, ref_path, seed):
    out_dir = os.path.join(SCRATCH, label)
    os.makedirs(out_dir, exist_ok=True)
    for x in os.listdir(out_dir):
        if x.endswith(".json"):
            os.remove(os.path.join(out_dir, x))
    cmd = [sys.executable, "scripts/step5_train.py", "--arm", "A", "--seed", str(seed), "--iters", "50",
           "--out-dir", out_dir] + extra
    t0 = time.time()
    with open(os.path.join(out_dir, "run.log"), "w") as f:
        rc = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT).returncode
    assert rc == 0, f"(b) {label}: the 50-iteration run exited {rc}; see {out_dir}/run.log"
    art = [x for x in os.listdir(out_dir) if x.endswith(".json")]
    assert len(art) == 1, art
    a = json.load(open(os.path.join(out_dir, art[0])))
    ref = json.load(open(ref_path))["curves"]
    per = {}
    for k in TRACES:
        got, want = a["curves"][k][:50], ref[k][:50]
        per[k] = {"n": len(got), "bitwise_equal": got == want,
                  "max_abs_diff": float(max(abs(x - y) for x, y in zip(got, want)))}
    return {"label": label, "command": " ".join(cmd[1:]).replace(SCRATCH, "$GT1_SCRATCH"), "artifact": art[0],
            "against": ref_path, "wall_s": time.time() - t0, "ensemble": a["hyperparameters"]["ensemble"],
            "train_episodes": a["hyperparameters"]["train_episodes"],
            "holdout_episodes": a["hyperparameters"]["holdout_episodes"],
            "n_train_windows": a["hyperparameters"]["n_train_windows"], "rule": a.get("rule"), "traces": per,
            "pass": all(v["bitwise_equal"] and v["n"] == 50 for v in per.values())}


def check_c(data, ep, cfg):
    rows = []
    for fold in FOLDS[1:]:
        s = E.fold_split(fold, strat_path=STRAT)
        excl = sorted(set(range(R.N_EPISODES)) - set(s["train_episodes"]))
        ds = T.WindowDataset(data, ep, s["train_episodes"], cfg)
        idx = np.asarray(ds.starts)[:, None] + np.arange(T.WINDOW)[None, :]
        touches = int(np.isin(ep[idx], fold).sum())
        ar = MN.arena(ep, fold, 32)
        inside = all(set(ep[st:st + 32 + MN.FORECAST].tolist()) <= set(fold) for st in ar["starts"])
        rows.append({"fold": fold, "excluded_from_training": excl, "n_train_windows": int(len(ds)),
                     "window_rows_in_fold": touches, "heldout_starts": ar["starts"],
                     "n_independent": ar["n_independent"], "heldout_inside_fold": bool(inside),
                     "pass": bool(excl == sorted(fold) and s["holdout_episodes"] == sorted(fold) and touches == 0
                                  and inside and ar["n_independent"] == 4)})
    return {"pass": all(r["pass"] for r in rows), "folds": rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-b", action="store_true", help="(a) and (c) only; no training")
    args = ap.parse_args()
    paths = R.repo_paths()
    cfg = R.load_reference_config(paths["lite"])
    data, ep = R.load_data(paths["csv"], verbose=False)
    out = {"what": "GT1 item 3: training support for rule X11 and its assertions (a)-(c)",
           "a": check_a(data, ep, cfg), "c": check_c(data, ep, cfg)}
    print(f"(a) {'PASS' if out['a']['pass'] else 'FAIL'}: " + "; ".join(
        f"{r['fold']} {r['n_windows']} windows {r['sha256'][:10]}" for r in out["a"]["folds"]))
    print(f"(c) {'PASS' if out['c']['pass'] else 'FAIL'}: " + "; ".join(
        f"{r['fold']} touching {r['window_rows_in_fold']}, held-out n {r['n_independent']}" for r in out["c"]["folds"]))
    if not args.skip_b:
        e5 = "results/step5_armA_seed0_ens5.json"
        out["b"] = {"comparison": "bitwise (==): the committed curves hold full-precision floats",
                    "runs": [run_b("e5_holdout_1_8", ["--holdout", "1,8", "--ensemble", "5"], e5, 0),
                             run_b("e5_default", ["--ensemble", "5", "--tag", "_ens5"], e5, 0),
                             run_b("s3_holdout_1_8", ["--holdout", "1,8"], "results/step5_armA_seed3.json", 3)]}
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
