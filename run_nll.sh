#!/usr/bin/env bash
set -u
cd "$(dirname "${BASH_SOURCE[0]}")"
V="${PY:-$(command -v python3.11 || command -v python3)}"
for s in 0 1 2; do
  echo "=== $(date +%H:%M:%S) Task5 gaussian_nll seed $s ==="
  $V -u scripts/step5_train.py --arm A --seed $s --iters 2500 --loss-type gaussian_nll --tag _nll \
     > results/step5_armA_seed${s}_nll_report.txt 2>&1
  echo "=== $(date +%H:%M:%S) done seed $s (exit $?) ==="
done
echo "TASK 5 COMPLETE"
