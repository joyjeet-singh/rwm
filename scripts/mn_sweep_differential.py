"""
M-74 -- differential test of the configurable M/N path, run before any sweep run.

The sweep trains Arm A at other (M, N) through step5_train.py's --sweep path. That path
must be the old path when (M, N) = (32, 8): same windows, same model, same RNG draws,
same losses. So it is run for the first 20 iterations at (32, 8) and every loss term it
records -- state, bound, contact, termination, total and the gradient norm -- is compared
BITWISE (float equality, not a tolerance) with the trace the existing Arm A seed-0 run
stored in results/step5_armA_seed0.json. Any difference fails the test and the sweep
does not launch.

The DEFAULT path of the edited step5_train.py is run and compared the same way, so the
edit is shown to leave every existing run's path unchanged.

It also records the episode-respecting training-window count of every configuration in
rule M-74's grid, counted two independent ways (the builder, and the episode lengths)
and asserted equal -- the same assertion the --sweep path makes inside every run.

Writes results/mn_sweep_differential.json. The 20-iteration run's own files go to
runs/mn_differential/ (gitignored).
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402

import rollout_eval as E  # noqa: E402
import rwm_data as R  # noqa: E402

OUT = "mn_sweep_differential.json"
REF = "step5_armA_seed0.json"
N_IT = 20
KEYS = ("state", "bound", "contact", "termination", "total", "grad_norm")
GRID = ((32, 8), (32, 32), (16, 8), (32, 16), (8, 8), (32, 2), (32, 1), (2, 8), (1, 8))


def main():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import p5_sweep_power as P5
    assert GRID == ((32, 8),) + P5.GRID, "this script's grid is not M-74's"
    py = sys.executable
    outdir = os.path.join(R.REPO_ROOT, "runs", "mn_differential")
    os.makedirs(outdir, exist_ok=True)
    ref = json.load(open(os.path.join(R.RESULTS, REF)))

    def run_and_compare(extra, artifact, label):
        cmd = [py, os.path.join(R.REPO_ROOT, "scripts", "step5_train.py"), "--arm", "A",
               "--seed", "0", "--iters", str(N_IT), "--out-dir", outdir] + extra
        log = os.path.join(outdir, f"train_{label}.log")
        with open(log, "w") as f:
            rc = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT,
                                cwd=R.REPO_ROOT).returncode
        assert rc == 0, f"the {label} run exited {rc}; see {R.rel(log)}"
        got = json.load(open(os.path.join(outdir, artifact)))
        rows, ok = {}, True
        for k in KEYS:
            a, b = got["curves"][k][:N_IT], ref["curves"][k][:N_IT]
            same = [x == y for x, y in zip(a, b)]
            ok &= all(same) and len(a) == N_IT
            rows[k] = {"identical": all(same), "n_compared": len(a),
                       "first_mismatch": None if all(same) else same.index(False),
                       "max_abs_diff": float(np.max(np.abs(np.array(a) - np.array(b))))}
        return got, rows, ok

    # The new path, and the default path in the edited file: both must be the old run.
    new, rows, ok_sweep = run_and_compare(
        ["--sweep", "--history", "32", "--forecast", "8"], "mn_sweep_run_M32_N8_seed0.json",
        "sweep")
    _, rows_default, ok_default = run_and_compare([], "step5_armA_seed0.json", "default")
    identical = ok_sweep and ok_default

    data, ep = R.load_data(R.repo_paths()["csv"], verbose=False)
    split = E.make_split(seed=0, strat_path=os.path.join(R.RESULTS, "step0_strat.json"),
                         verbose=False)
    counts = {}
    for m, n in GRID:
        w = m + n
        built = sum(1 for s in R.valid_window_starts(ep, w) if ep[s] in split["train_episodes"])
        from_lengths = sum(int((ep == e).sum()) - w + 1 for e in split["train_episodes"])
        assert built == from_lengths, f"({m},{n}): builder {built} != lengths {from_lengths}"
        counts[f"M{m}_N{n}"] = {"M": m, "N": n, "window": w, "n_train_windows": built}
    assert counts["M32_N8"]["n_train_windows"] == ref["hyperparameters"]["n_train_windows"]
    assert new["hyperparameters"]["n_train_windows"] == ref["hyperparameters"]["n_train_windows"]

    print("=" * 90)
    print("M-74 DIFFERENTIAL TEST — the --sweep path at (32, 8) against Arm A seed 0")
    print("=" * 90)
    for label, rr in (("--sweep --history 32 --forecast 8", rows), ("default path", rows_default)):
        print(f"  {label}:")
        for k, r in rr.items():
            print(f"    {k:<12} first {N_IT} iterations bitwise identical: {r['identical']}"
                  + ("" if r["identical"] else f"  (first mismatch at {r['first_mismatch']}, "
                                               f"max |diff| {r['max_abs_diff']:.3e})"))
    print("  training windows per configuration (builder == episode lengths):")
    for k, c in counts.items():
        print(f"    {k:<8} window {c['window']:>3}  {c['n_train_windows']:>5}")
    out = {"rule": "M-74", "test": f"the --sweep path at (32, 8), first {N_IT} iterations, "
                                   f"against results/{REF}, compared bitwise",
           "reference": f"results/{REF}", "n_iterations": N_IT, "keys": rows,
           "default_path_keys": rows_default, "default_path_identical": bool(ok_default),
           "sweep_path_identical": bool(ok_sweep),
           "identical": bool(identical), "training_windows": counts,
           "train_episodes": split["train_episodes"], "torch": new["torch"]}
    json.dump(out, open(os.path.join(R.RESULTS, OUT), "w"), indent=2)
    print(f"  RESULT: {'PASS' if identical else 'FAIL'}\n  wrote results/{OUT}")
    sys.exit(0 if identical else 1)


if __name__ == "__main__":
    main()
