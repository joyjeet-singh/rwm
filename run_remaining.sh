#!/usr/bin/env bash
# Step 6.2 -- the remaining five runs, sequentially (2 cores; parallel would
# contend and distort the timing measurements).
set -u
V=../.venv-rwm311/bin/python
for spec in "A 1" "A 2" "B 0" "B 1" "B 2"; do
  set -- $spec
  arm=$1; seed=$2
  out="results/step5_arm${arm}_seed${seed}_report.txt"
  echo "=== $(date +%H:%M:%S) starting arm ${arm} seed ${seed} ==="
  $V -u scripts/step5_train.py --arm "$arm" --seed "$seed" > "$out" 2>&1
  echo "=== $(date +%H:%M:%S) finished arm ${arm} seed ${seed} (exit $?) ==="
done
echo "ALL FIVE RUNS COMPLETE"
