#!/usr/bin/env bash
# The pre-submission training queue (PLAN S2a). Runs runs/queue.txt one line at a time,
# in file order, until no line is left that is neither done nor failed.
#
#   line format:  <id> <arch> <M> <N> <seed> <iterations>      ('#' starts a comment)
#   finished ids -> runs/queue_done.txt; failed ids -> runs/queue_failed.txt, and the
#   queue carries on; each run's output -> runs/queue_logs/<id>.log
#
# Launched as:  nohup caffeinate -i scripts/queue_runner.sh > runs/queue.log 2>&1 &
#
# The queue file is re-read before every run, so lines appended while the queue runs
# (S2b's baselines) are picked up in order. One run at a time: the machine has 8 GB.
#
# NEVER EDIT THIS FILE WHILE IT IS RUNNING. Bash reads a running script by byte offset
# and an edit shifts the bytes under it (M-30; CLAUDE.md rule 7). Everything that may
# need to change -- a new architecture, a new check -- belongs in scripts/queue_run.py,
# which is read afresh for every run.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/.."
PY="${PY:-$(cd .. && pwd)/.venv-rwm311/bin/python}"
Q=runs/queue.txt
DONE=runs/queue_done.txt
FAILED=runs/queue_failed.txt
LOGS=runs/queue_logs
mkdir -p "$LOGS"
touch "$DONE" "$FAILED"
echo "$(date '+%F %T') queue runner start, pid $$"
while :; do
  next=""
  while read -r id arch m n seed iters _rest; do
    [ -z "${id:-}" ] && continue
    case "$id" in \#*) continue ;; esac
    grep -qxF "$id" "$DONE" && continue
    grep -qxF "$id" "$FAILED" && continue
    next="$id $arch $m $n $seed $iters"
    break
  done < "$Q"
  [ -z "$next" ] && break
  set -- $next
  echo "$(date '+%F %T') start $1 (arch $2, M $3, N $4, seed $5, $6 iterations)"
  if "$PY" scripts/queue_run.py "$@" > "$LOGS/$1.log" 2>&1; then
    echo "$1" >> "$DONE"
    echo "$(date '+%F %T') done  $1"
  else
    echo "$1" >> "$FAILED"
    echo "$(date '+%F %T') FAIL  $1 (see $LOGS/$1.log)"
  fi
done
echo "$(date '+%F %T') queue empty; runner exits"
