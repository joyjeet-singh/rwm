#!/bin/zsh
# Round 2, T6/T7: quick check after a move. Numbers, paper, then the text-level gates; prints failures only.
cd /Users/joyjeetsingh/Downloads/PDM/rwm_repro
P=/Users/joyjeetsingh/Downloads/PDM/.venv-rwm311/bin/python
S=${TMPDIR:-/tmp}/rwm_t6_qc; mkdir -p $S
for s in evidence_summary typed_numeral_audit paper_numbers build_paper check_comparative_claims xref_sweep restatement_index horizon_sweep check_scope_audit; do
  $P scripts/$s.py > $S/qc_$s.log 2>&1 || { echo "FAIL $s"; grep -E "FAIL|Error|assert|NOT COVERED|SUSPECT|suspect" $S/qc_$s.log | head -8 | cut -c1-300; }
done
grep -h "comparative claims verified\|corruptions caught" $S/qc_check_comparative_claims.log
grep -h -i "suspect" $S/qc_xref_sweep.log | grep -v " 0 suspect"
$P docs/presubmission/round2/t6_words.py | head -1
