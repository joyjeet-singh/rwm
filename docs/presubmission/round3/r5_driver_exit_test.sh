#!/usr/bin/env bash
# R5 item H1: each training driver must exit non-zero when training fails, and zero when it succeeds or
# every artifact exists. Runs each driver from a scratch copy (the drivers cd to their own directory), with
# PY pointed at a stub interpreter, so nothing under the repository is written. Run from the repository root.
set -u
ROOT="$(pwd)"
T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT
printf '#!/usr/bin/env bash\necho "$@" >> "%s/calls"\nexit 1\n' "$T" > "$T/py_fail"
printf '#!/usr/bin/env bash\necho "$@" >> "%s/calls"\nexit 0\n' "$T" > "$T/py_ok"
chmod +x "$T/py_fail" "$T/py_ok"
bad=0
check() {  # driver, stub, expected exit, label, [files to pre-create]
  local d=$1 stub=$2 want=$3 label=$4; shift 4
  rm -rf "$T/w" "$T/calls"; mkdir -p "$T/w/results"; cp "$ROOT/$d" "$T/w/"
  for f in "$@"; do : > "$T/w/results/$f"; done
  PY="$T/$stub" bash "$T/w/$d" > "$T/out" 2>&1
  local got=$?
  local n=0; [ -e "$T/calls" ] && n=$(wc -l < "$T/calls" | tr -d ' ')
  if [ "$got" -eq "$want" ]; then r=PASS; else r=FAIL; bad=1; fi
  echo "$r  $d  $label: exit $got (want $want), training called $n time(s); last line: $(tail -n 1 "$T/out")"
}
for d in run_10k_d1.sh run_indep_ens.sh run_m49_matched.sh run_nll.sh run_nll_indep_ens.sh; do
  check "$d" py_fail 1 "training fails"
  check "$d" py_ok 0 "training succeeds"
done
# Every artifact present: nothing trains, exit 0.
check run_10k_d1.sh py_fail 0 "all present" step5_armA_seed0_10k.json step5_armA_seed2_10k.json step5_armB_seed0_10k.json step5_armB_seed2_10k.json
check run_indep_ens.sh py_fail 0 "all present" step5_armA_seed3.json step5_armA_seed4.json
check run_m49_matched.sh py_fail 0 "all present" step5_armA_seed{0,1,2,3,4}_m49h124.json
check run_nll.sh py_fail 0 "all present" step5_armA_seed{0,1,2}_nll.json
check run_nll_indep_ens.sh py_fail 0 "all present" step5_armA_seed{3,4}_nll.json
# run_nll.sh's new existence check: seed 0 present, seeds 1 and 2 train.
check run_nll.sh py_ok 0 "seed 0 present" step5_armA_seed0_nll.json
[ "$(grep -c -- '--seed 0' "$T/calls")" -eq 0 ] && [ "$(wc -l < "$T/calls" | tr -d ' ')" -eq 2 ] \
  && echo "PASS  run_nll.sh  seed 0 skipped, seeds 1 and 2 trained" || { echo "FAIL  run_nll.sh  skip check"; bad=1; }
[ "$bad" -eq 0 ] && echo "H1 DRIVER EXIT TEST: PASS" || { echo "H1 DRIVER EXIT TEST: FAIL"; exit 1; }
