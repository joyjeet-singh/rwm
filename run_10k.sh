#!/usr/bin/env bash
set -u
V=../.venv-rwm311/bin/python
for spec in "A 1" "B 1"; do
  set -- $spec; arm=$1; seed=$2
  echo "=== $(date +%H:%M:%S) starting arm${arm} seed${seed} 10k ==="
  $V -u scripts/step5_train.py --arm "$arm" --seed "$seed" --iters 10000 --tag _10k \
     > "results/step5_arm${arm}_seed${seed}_10k_report.txt" 2>&1
  echo "=== $(date +%H:%M:%S) finished arm${arm} seed${seed} 10k (exit $?) ==="
done
echo "BOTH 10K RUNS COMPLETE"
