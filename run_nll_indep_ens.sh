#!/usr/bin/env bash
# M-68 -- the combined arm. Two more Arm A ens1 seeds under gaussian_nll, so five
# independently-initialised models trained under the corrected objective can be
# scored together as an ensemble at evaluation time.
#
# Why two and not five: seeds 0, 1 and 2 already exist under gaussian_nll
# (results/step5_armA_seed{0,1,2}_nll.json, runs/armA_seed{0,1,2}_nll/), trained
# by run_nll.sh through the SAME entry point and the SAME arguments this file
# uses -- --arm A --iters 2500 --loss-type gaussian_nll --tag _nll. The trainer
# is deterministic under a fixed seed, so retraining them would reproduce the
# checkpoints already on disk at a cost of about 42 minutes each and change
# nothing. Section 6.10's independent-ensemble arm was assembled the same way
# (run_indep_ens.sh) and M-68 states the reuse in advance rather than discovering
# it afterwards.
#
# Every setting matches seeds 0-2. The comparison is only interpretable if
# nothing else moved, which is also why this is a NEW file rather than an edit to
# run_nll.sh or run_indep_ens.sh: M-30 records a driver destroyed mid-run because
# bash reads a script by byte offset and an edit shifted the bytes under it.
#
# Idempotent: a seed whose result json already exists is skipped, exactly as
# run_indep_ens.sh does. Governed by M-68, committed before this file was run.
# Round 3, R5 (H1): a failed training run makes this driver exit 1, after the remaining runs, so the
# reproduce.sh stage that drives it reports the failure rather than OK.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")"
V="${PY:-$(command -v python3.11 || command -v python3)}"
SEEDS="${SEEDS:-3 4}"
fail=0
for seed in $SEEDS; do
  out="results/step5_armA_seed${seed}_nll_report.txt"
  if [ -e "results/step5_armA_seed${seed}_nll.json" ]; then
    echo "=== skip seed ${seed} -- results/step5_armA_seed${seed}_nll.json exists ==="
    continue
  fi
  echo "=== $(date +%H:%M:%S) starting armA seed ${seed} ens1 gaussian_nll ==="
  $V -u scripts/step5_train.py --arm A --seed "$seed" --iters 2500 \
     --loss-type gaussian_nll --tag _nll > "$out" 2>&1
  rc=$?
  echo "=== $(date +%H:%M:%S) finished armA seed ${seed} ens1 gaussian_nll (exit $rc) ==="
  [ "$rc" -eq 0 ] || fail=1
done
if [ "$fail" -ne 0 ]; then echo "COMBINED-ARM RUNS FAILED"; exit 1; fi
echo "COMBINED-ARM RUNS COMPLETE"
