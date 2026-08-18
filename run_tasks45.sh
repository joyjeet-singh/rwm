#!/usr/bin/env bash
set -u
V=/Users/joyjeetsingh/Downloads/PDM/.venv-rwm311/bin/python
for s in 0 1 2; do
  echo "=== $(date +%H:%M:%S) Task4 contamination seed $s ==="
  $V -u scripts/step5_train.py --arm A --seed $s --iters 2500 --contaminated --tag _contam \
     > results/step5_armA_seed${s}_contam_report.txt 2>&1
done
for s in 0 1 2; do
  echo "=== $(date +%H:%M:%S) Task5 gaussian_nll seed $s ==="
  $V -u scripts/step5_train.py --arm A --seed $s --iters 2500 --loss-type gaussian_nll --tag _nll \
     > results/step5_armA_seed${s}_nll_report.txt 2>&1
done
echo "TASKS 4 AND 5 COMPLETE"
