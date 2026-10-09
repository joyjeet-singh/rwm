#!/usr/bin/env bash
# M-49 -- five independently-initialised members at the capacity-matched width.
#
# §6.10's independent arm carries 3,570,820 state-pathway parameters against the
# shared-trunk arm's 1,024,132 (X-17). Five members at rnn_hidden_size 124 carry
# 1,023,880: 0.9998x. Everything else matches the runs of 6.10 exactly.
#
# Governed by M-49, committed together with results/p2_capacity_power.json before
# this file was run. The MDE is in the rule's own text and says what the rule can
# and cannot resolve.
#
# A NEW FILE rather than an edit to run_indep_ens.sh: M-30 destroyed a driver
# mid-run by editing it while bash was reading it by byte offset.
# Round 3, R5 (H1): a failed training run makes this driver exit 1, after the remaining runs, so the
# reproduce.sh stage that drives it reports the failure rather than OK.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")"
V="${PY:-$(command -v python3.11 || command -v python3)}"
SEEDS="${SEEDS:-0 1 2 3 4}"
HIDDEN="${HIDDEN:-124}"
TAG="_m49h${HIDDEN}"
fail=0
for seed in $SEEDS; do
  out="results/step5_armA_seed${seed}${TAG}_report.txt"
  if [ -e "results/step5_armA_seed${seed}${TAG}.json" ]; then
    echo "=== skip seed ${seed} -- already done ==="
    continue
  fi
  echo "=== $(date +%H:%M:%S) starting armA seed ${seed} ens1 hidden ${HIDDEN} ==="
  $V -u scripts/step5_train.py --arm A --seed "$seed" --ensemble 1 \
      --hidden "$HIDDEN" --tag "$TAG" > "$out" 2>&1
  rc=$?
  echo "=== $(date +%H:%M:%S) finished armA seed ${seed} (exit $rc) ==="
  [ "$rc" -eq 0 ] || fail=1
done
if [ "$fail" -ne 0 ]; then echo "M-49 CAPACITY-MATCHED RUNS FAILED"; exit 1; fi
echo "M-49 CAPACITY-MATCHED RUNS COMPLETE"
