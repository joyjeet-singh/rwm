#!/usr/bin/env bash
# Task 5 -- Arm A under gaussian_nll, seeds 0-2. Skips a seed whose JSON already exists, as the
# other drivers do (round 3, R5, H1).
# Round 3, R5 (H1): a failed training run makes this driver exit 1, after the remaining runs, so the
# reproduce.sh stage that drives it reports the failure rather than OK.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")"
V="${PY:-$(command -v python3.11 || command -v python3)}"
fail=0
for s in ${SEEDS:-0 1 2}; do
  if [ -e "results/step5_armA_seed${s}_nll.json" ]; then
    echo "=== skip seed $s -- results/step5_armA_seed${s}_nll.json exists ==="
    continue
  fi
  echo "=== $(date +%H:%M:%S) Task5 gaussian_nll seed $s ==="
  $V -u scripts/step5_train.py --arm A --seed $s --iters 2500 --loss-type gaussian_nll --tag _nll \
     > results/step5_armA_seed${s}_nll_report.txt 2>&1
  rc=$?
  echo "=== $(date +%H:%M:%S) done seed $s (exit $rc) ==="
  [ "$rc" -eq 0 ] || fail=1
done
if [ "$fail" -ne 0 ]; then echo "TASK 5 FAILED"; exit 1; fi
echo "TASK 5 COMPLETE"
