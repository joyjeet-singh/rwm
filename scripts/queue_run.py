"""
Run ONE line of runs/queue.txt, then check what it wrote. Called by
scripts/queue_runner.sh; exits 0 only if the run finished AND its artifact is right.

    python scripts/queue_run.py <id> <arch> <M> <N> <seed> <iterations>

WHY A PYTHON DISPATCHER. The queue runner is a bash script that stays running for days,
and bash reads a running script by byte offset: editing it mid-run destroyed a driver once
(M-30; CLAUDE.md rule 7). So the runner does nothing but walk the queue, and everything
that may need to grow lives here, in a file Python reads afresh for every run. S2b adds
its baseline architectures to TRAINERS below between runs; it never touches the runner.

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
    return cmd, artifact, weights


TRAINERS = {"rwm": rwm}


def check(artifact, weights, arch, m, n, seed, iters):
    bad = []
    if not os.path.exists(artifact):
        return [f"artifact missing: {artifact}"]
    a = json.load(open(artifact))
    hp = a.get("hyperparameters", {})
    for field, want, got in (("iterations", iters, hp.get("iterations")),
                             ("history_horizon (M)", m, hp.get("history_horizon")),
                             ("forecast_horizon (N)", n, hp.get("forecast_horizon")),
                             ("arch", arch, a.get("arch")), ("seed", seed, a.get("seed")),
                             ("rnn_hidden_size (width)", 256, hp.get("rnn_hidden_size"))):
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
    cmd, artifact, weights = TRAINERS[arch](run_id, m, n, seed, iters)
    if os.path.exists(artifact):
        print(f"queue_run: {artifact} already exists; refusing to overwrite a finished run")
        sys.exit(1)
    print(f"queue_run: {run_id}: {' '.join(os.path.relpath(c, ROOT) if c.startswith(ROOT) else c for c in cmd[1:])}",
          flush=True)
    rc = subprocess.run(cmd, cwd=ROOT).returncode
    if rc != 0:
        print(f"queue_run: {run_id}: trainer exited {rc}")
        sys.exit(1)
    bad = check(artifact, weights, arch, m, n, seed, iters)
    for b in bad:
        print(f"queue_run: {run_id}: CHECK FAILED — {b}")
    if bad:
        sys.exit(1)
    print(f"queue_run: {run_id}: finished and checked")


if __name__ == "__main__":
    main()
