"""S8 step 1 -- the queue gate (PLAN S8).

Independent of scripts/queue_run.py, which checked each run as it ended: this re-reads every
line of runs/queue.txt, re-derives what each run should be, and checks the artifact it left.
All four conditions must hold, or S8 stops BLOCKED with the list:

  1. every line of queue.txt is in queue_done.txt;
  2. queue_failed.txt is empty;
  3. every artifact has the expected iterations, width (RWM: rnn_hidden_size 256; baselines:
     the parameter count of the model the spec builds), M, N, arch (and regime, spec), seed;
  4. no loss trace contains a NaN (every curve, final term, and wall_clock_s is finite), and
     the 2,500-iteration weights exist.

    python docs/presubmission/s8_gate.py
"""
import json
import math
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
sys.path.insert(0, os.path.join(ROOT, "src"))
import baselines as BL  # noqa: E402
import rwm_data as R  # noqa: E402

RUNS, RES = os.path.join(ROOT, "runs"), os.path.join(ROOT, "results")


def finite_all(x):
    if isinstance(x, (int, float)) and not isinstance(x, bool):
        return math.isfinite(x)
    if isinstance(x, list):
        return all(finite_all(v) for v in x)
    if isinstance(x, dict):
        return all(finite_all(v) for v in x.values())
    return True


def main():
    lines = [l.split() for l in open(os.path.join(RUNS, "queue.txt"))
             if l.strip() and not l.startswith("#")]
    done = {l.strip() for l in open(os.path.join(RUNS, "queue_done.txt")) if l.strip()}
    failed = [l.strip() for l in open(os.path.join(RUNS, "queue_failed.txt")) if l.strip()]
    cfg = R.load_reference_config(R.repo_paths()["lite"])
    bad, n_par_cache = [], {}

    missing = [l[0] for l in lines if l[0] not in done]
    if missing:
        bad.append(f"not in queue_done.txt: {missing}")
    if failed:
        bad.append(f"queue_failed.txt is not empty: {failed}")

    for rid, arch, m, n, seed, iters in lines:
        m, n, seed, iters = int(m), int(n), int(seed), int(iters)
        if arch == "rwm":
            art = os.path.join(RES, f"mn_sweep_run_M{m}_N{n}_seed{seed}.json")
            wts = os.path.join(RUNS, f"mn_M{m}_N{n}_seed{seed}", f"weights_{iters}.pt")
        else:
            a, regime, spec = arch.split("-")
            art = os.path.join(RES, f"baseline_run_{a}_{regime}_{spec}_seed{seed}.json")
            wts = os.path.join(RUNS, f"baseline_{a}_{regime}_{spec}_seed{seed}", f"weights_{iters}.pt")
        if not os.path.exists(art):
            bad.append(f"{rid}: artifact missing {os.path.relpath(art, ROOT)}")
            continue
        A = json.load(open(art))
        hp = A.get("hyperparameters", {})
        got = {"iterations": hp.get("iterations"), "M": hp.get("history_horizon"),
               "N": hp.get("forecast_horizon"), "seed": A.get("seed")}
        want = {"iterations": iters, "M": m, "N": n, "seed": seed}
        if arch == "rwm":
            got.update(arch=A.get("arch"), width=hp.get("rnn_hidden_size"), ensemble=hp.get("ensemble"))
            want.update(arch="rwm", width=256, ensemble=1)
        else:
            if (a, spec) not in n_par_cache:
                n_par_cache[(a, spec)] = BL.n_params(BL.build(a, spec, cfg))
            got.update(arch=A.get("arch"), regime=A.get("regime"), spec=A.get("spec"),
                       width=hp.get("n_params"))
            want.update(arch=a, regime=regime, spec=spec, width=n_par_cache[(a, spec)])
        diff = {k: (got[k], want[k]) for k in want if got[k] != want[k]}
        if diff:
            bad.append(f"{rid}: {diff}")
        curves = A.get("curves", {})
        if not curves or not finite_all(curves):
            bad.append(f"{rid}: a loss trace is missing or non-finite")
        if not finite_all(A.get("final_terms", {})) or not math.isfinite(A.get("wall_clock_s", float("nan"))):
            bad.append(f"{rid}: final_terms or wall_clock_s non-finite")
        if not os.path.exists(wts):
            bad.append(f"{rid}: weights missing {os.path.relpath(wts, ROOT)}")

    print(f"S8 GATE: {len(lines)} queued, {len(done & {l[0] for l in lines})} done, "
          f"{len(failed)} failed, {len(bad)} problem(s)")
    for b in bad:
        print("  !!", b)
    print("  RESULT:", "PASS" if not bad else "BLOCKED")
    sys.exit(0 if not bad else 1)


if __name__ == "__main__":
    main()
