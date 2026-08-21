#!/usr/bin/env bash
# D1 -- the four remaining 10,000-iteration runs, making the headline a
# three-seed result. Arm A seeds 0 and 2, Arm B seeds 0 and 2, flags identical
# to run_10k.sh which produced the existing seed-1 pair.
#
# Written as a NEW file rather than editing run_10k.sh: bash reads a running
# script by byte offset, and editing one under itself destroyed a driver once
# (M-30).
#
# Skips a run whose JSON already exists, so this is safe to relaunch.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")"
V="${PY:-$(command -v python3.11 || command -v python3)}"
LOG=results/d1_driver.log
: > "$LOG"
for spec in "A 0" "A 2" "B 0" "B 2"; do
  set -- $spec; arm=$1; seed=$2
  out="results/step5_arm${arm}_seed${seed}_10k.json"
  if [ -e "$out" ]; then
    echo "=== skip arm${arm} seed${seed} 10k -- $out exists ===" | tee -a "$LOG"
    continue
  fi
  echo "=== $(date +%H:%M:%S) starting arm${arm} seed${seed} 10k ===" | tee -a "$LOG"
  $V -u scripts/step5_train.py --arm "$arm" --seed "$seed" --iters 10000 --tag _10k \
     > "results/step5_arm${arm}_seed${seed}_10k_report.txt" 2>&1
  rc=$?
  echo "=== $(date +%H:%M:%S) finished arm${arm} seed${seed} 10k (exit $rc) ===" | tee -a "$LOG"
done
echo "D1: ALL FOUR 10K RUNS COMPLETE" | tee -a "$LOG"
