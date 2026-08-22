#!/usr/bin/env bash
# Part D: Arm A at ensemble size 5, three seeds, 2,500 iterations.
#
# Every setting other than --ensemble matches the existing ens1 Arm A runs, which
# is the point: the comparison is only interpretable if nothing else moved.
# Sequential, like run_remaining.sh -- two cores, and parallel runs would contend
# and distort the wall clocks Appendix B quotes.
#
# Governed by M-43, committed before this file was run.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")"
V="${PY:-$(command -v python3.11 || command -v python3)}"
SEEDS="${SEEDS:-0 1 2}"
for seed in $SEEDS; do
  out="results/step5_armA_seed${seed}_ens5_report.txt"
  if [ -e "results/step5_armA_seed${seed}_ens5.json" ]; then
    echo "=== skip seed ${seed} -- results/step5_armA_seed${seed}_ens5.json exists ==="
    continue
  fi
  echo "=== $(date +%H:%M:%S) starting armA seed ${seed} ens5 ==="
  $V -u scripts/step5_train.py --arm A --seed "$seed" --ensemble 5 --tag _ens5 > "$out" 2>&1
  echo "=== $(date +%H:%M:%S) finished armA seed ${seed} ens5 (exit $?) ==="
done
echo "ENS5 RUNS COMPLETE"
