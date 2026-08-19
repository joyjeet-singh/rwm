#!/usr/bin/env bash
set -u
cd "$(dirname "${BASH_SOURCE[0]}")"
V="${PY:-$(command -v python3.11 || command -v python3)}"
for s in 0 1 2; do
  echo "=== $(date +%H:%M:%S) control (duplicated) seed $s ==="
  $V -u scripts/step5_train.py --arm A --seed $s --iters 2500 --duplicated --tag _dup \
     > results/step5_armA_seed${s}_dup_report.txt 2>&1
  echo "=== $(date +%H:%M:%S) done seed $s (exit $?) ==="
done
echo "CONTROL ARM COMPLETE"
