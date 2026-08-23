#!/usr/bin/env bash
# Phase 2 / R1 -- two more Arm A ens1 seeds, so five independently-initialised
# models can be scored together as an ensemble at evaluation time.
#
# Why this and not a genuinely independent 5-model ensemble: training one would
# cost roughly 17 CPU-hours across three seeds. We already have Arm A ens1 at
# seeds 0, 1, 2. Adding seeds 3 and 4 costs about 1.2 h each and gives exactly
# the contrast M-44 asks for -- five full models that share NO parameters, against
# five heads that share a trunk -- with no new training code and no new
# architecture.
#
# Every setting matches seeds 0-2. The comparison is only interpretable if
# nothing else moved, which is also why this is a new file rather than an edit to
# run_ens5.sh: M-30 destroyed a driver mid-run by editing it while bash was
# reading it by byte offset.
#
# Governed by M-44, committed before this file was run.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")"
V="${PY:-$(command -v python3.11 || command -v python3)}"
SEEDS="${SEEDS:-3 4}"
for seed in $SEEDS; do
  out="results/step5_armA_seed${seed}_report.txt"
  if [ -e "results/step5_armA_seed${seed}.json" ]; then
    echo "=== skip seed ${seed} -- results/step5_armA_seed${seed}.json exists ==="
    continue
  fi
  echo "=== $(date +%H:%M:%S) starting armA seed ${seed} ens1 ==="
  $V -u scripts/step5_train.py --arm A --seed "$seed" > "$out" 2>&1
  echo "=== $(date +%H:%M:%S) finished armA seed ${seed} ens1 (exit $?) ==="
done
echo "INDEPENDENT-INIT RUNS COMPLETE"
