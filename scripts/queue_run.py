"""
Run ONE line of runs/queue.txt, then check what it wrote. Called by
scripts/queue_runner.sh; exits 0 only if the run finished AND its artifact is right.

    python scripts/queue_run.py <id> <arch> <M> <N> <seed> <iterations>

WHY A PYTHON DISPATCHER. The queue runner is a bash script that stays running for days,
and bash reads a running script by byte offset: editing it mid-run destroyed a driver once
(M-30; CLAUDE.md rule 7). So the runner does nothing but walk the queue, and everything
that may need to grow lives here, in a file Python reads afresh for every run. S2b adds
its baseline architectures to TRAINERS below between runs; it never touches the runner.
(Done in S2b: the twelve arch-regime-spec strings, e.g. 'mlp-tf-s7'.)

WHAT IS CHECKED after every run (PLAN S8's gate, applied as each run ends rather than
all at once at the end):
  the artifact exists and records the queued iterations, M, N, arch and seed;
  the width is the released 256 (rnn_hidden_size);
  wall_clock_s is present;
  no loss trace holds a NaN or an infinity;
  the 2,500-iteration weights exist.
A run that trains but fails a check is a FAILED run, and M-74 then cannot be discharged
as written -- which is the point: the failure surfaces at once, not in S8.

Thread settings: none are set, exactly as every existing run (FILE_MAP.md §5).
"""
import json
import math
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))


def rwm(run_id, m, n, seed, iters):
    """Rule M-74's sweep: Arm A at (M, N), everything else as the centre."""
    cmd = [sys.executable, os.path.join(ROOT, "scripts", "step5_train.py"), "--arm", "A",
           "--seed", str(seed), "--iters", str(iters), "--sweep", "--history", str(m),
           "--forecast", str(n)]
    artifact = os.path.join(ROOT, "results", f"mn_sweep_run_M{m}_N{n}_seed{seed}.json")
    weights = os.path.join(ROOT, "runs", f"mn_M{m}_N{n}_seed{seed}", f"weights_{iters}.pt")
    expect = {"iterations": iters, "history_horizon (M)": m, "forecast_horizon (N)": n,
              "arch": "rwm", "seed": seed, "rnn_hidden_size (width)": 256}
    return cmd, artifact, weights, expect


def baseline(arch, regime, spec):
    """Rules M-75 (tf) and M-76 (ar): one architecture baseline (S2b)."""
    def trainer(run_id, m, n, seed, iters):
        assert (m, n) == (32, 8), "the baselines train on Arm A's (32, 8) windows"
        cmd = [sys.executable, os.path.join(ROOT, "scripts", "train_baseline.py"), "--arch",
               arch, "--regime", regime, "--spec", spec, "--seed", str(seed), "--iters",
               str(iters)]
        tag = f"{arch}_{regime}_{spec}"
        artifact = os.path.join(ROOT, "results", f"baseline_run_{tag}_seed{seed}.json")
        weights = os.path.join(ROOT, "runs", f"baseline_{tag}_seed{seed}", f"weights_{iters}.pt")
        sys.path.insert(0, os.path.join(ROOT, "src"))
        import rwm_data as R
        import baselines as BL
        n_par = BL.n_params(BL.build(arch, spec, R.load_reference_config(R.repo_paths()["lite"])))
        expect = {"iterations": iters, "history_horizon (M)": m, "forecast_horizon (N)": n,
                  "arch": arch, "regime": regime, "spec": spec, "seed": seed,
                  "n_params (width)": n_par}
        return cmd, artifact, weights, expect
    return trainer


TRAINERS = {"rwm": rwm}
for _a in ("mlp", "rssm", "transformer"):
    for _r in ("tf", "ar"):
        for _s in ("s7", "matched"):
            TRAINERS[f"{_a}-{_r}-{_s}"] = baseline(_a, _r, _s)

FIELDS = {"iterations": lambda a, hp: hp.get("iterations"),
          "history_horizon (M)": lambda a, hp: hp.get("history_horizon"),
          "forecast_horizon (N)": lambda a, hp: hp.get("forecast_horizon"),
          "arch": lambda a, hp: a.get("arch"), "regime": lambda a, hp: a.get("regime"),
          "spec": lambda a, hp: a.get("spec"), "seed": lambda a, hp: a.get("seed"),
          "rnn_hidden_size (width)": lambda a, hp: hp.get("rnn_hidden_size"),
          "n_params (width)": lambda a, hp: hp.get("n_params")}


def check(artifact, weights, expect):
    bad = []
    if not os.path.exists(artifact):
        return [f"artifact missing: {artifact}"]
    a = json.load(open(artifact))
    hp = a.get("hyperparameters", {})
    for field, want in expect.items():
        got = FIELDS[field](a, hp)
        if got != want:
            bad.append(f"{field}: queued {want}, artifact {got}")
    if not isinstance(a.get("wall_clock_s"), (int, float)):
        bad.append("wall_clock_s missing")
    for k, v in a.get("curves", {}).items():
        if any(not math.isfinite(x) for x in v):
            bad.append(f"non-finite value in loss trace '{k}'")
    if not a.get("curves"):
        bad.append("no loss traces recorded")
    if not os.path.exists(weights):
        bad.append(f"weights missing: {weights}")
    return bad


def main():
    run_id, arch, m, n, seed, iters = sys.argv[1:7]
    m, n, seed, iters = int(m), int(n), int(seed), int(iters)
    if arch not in TRAINERS:
        print(f"queue_run: no trainer for arch '{arch}' (known: {sorted(TRAINERS)})")
        sys.exit(1)
    cmd, artifact, weights, expect = TRAINERS[arch](run_id, m, n, seed, iters)
    if os.path.exists(artifact):
        print(f"queue_run: {artifact} already exists; refusing to overwrite a finished run")
        sys.exit(1)
    print(f"queue_run: {run_id}: {' '.join(os.path.relpath(c, ROOT) if c.startswith(ROOT) else c for c in cmd[1:])}",
          flush=True)
    # Unbuffered, so runs/queue_logs/<id>.log shows progress while the run is live. The
    # first queued run (mn_M32_N32_s0) started before this line existed: its log fills
    # only when it ends. Logging only; no number a run computes depends on it.
    env = {**os.environ, "PYTHONUNBUFFERED": "1"}
    rc = subprocess.run(cmd, cwd=ROOT, env=env).returncode
    if rc != 0:
        print(f"queue_run: {run_id}: trainer exited {rc}")
        sys.exit(1)
    bad = check(artifact, weights, expect)
    for b in bad:
        print(f"queue_run: {run_id}: CHECK FAILED — {b}")
    if bad:
        sys.exit(1)
    print(f"queue_run: {run_id}: finished and checked")


if __name__ == "__main__":
    main()
