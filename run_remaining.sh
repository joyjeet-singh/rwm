#!/usr/bin/env bash
# The six main runs, sequentially (2 cores; parallel would contend and distort
# the timing measurements).
#
# This trained five of them for most of the project's life: arm A seed 0 was run
# by hand before this driver existed, so a clean clone reproduced only five and
# then failed at stages 12-15, which iterate SEEDS=(0,1,2) over both arms. A 0 is
# now first in the list. Existing runs are skipped, so re-running is cheap.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")"
V="${PY:-$(command -v python3.11 || command -v python3)}"
for spec in "A 0" "A 1" "A 2" "B 0" "B 1" "B 2"; do
  set -- $spec
  arm=$1; seed=$2
  out="results/step5_arm${arm}_seed${seed}_report.txt"
  if [ -e "results/step5_arm${arm}_seed${seed}.json" ]; then
    echo "=== skip arm ${arm} seed ${seed} -- results/step5_arm${arm}_seed${seed}.json exists ==="
    continue
  fi
  echo "=== $(date +%H:%M:%S) starting arm ${arm} seed ${seed} ==="
  $V -u scripts/step5_train.py --arm "$arm" --seed "$seed" > "$out" 2>&1
  echo "=== $(date +%H:%M:%S) finished arm ${arm} seed ${seed} (exit $?) ==="
done
echo "ALL SIX MAIN RUNS COMPLETE"
