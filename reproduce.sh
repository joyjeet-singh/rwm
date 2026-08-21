#!/usr/bin/env bash
# Regenerate every number in the paper from a clean clone.
#
#   ./reproduce.sh --quick     everything except the training arms (minutes)
#   ./reproduce.sh             the full pipeline, including ~20 h of training
#   ./reproduce.sh --stage N   run one stage only
#
# Each stage skips cleanly if its outputs already exist, so a reviewer can
# regenerate one table without repeating the training. Use --force to override.
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
PY="${PY:-$(command -v python3.11 || command -v python3)}"
QUICK=0; FORCE=0; ONLY=""
for a in "$@"; do
  case "$a" in
    --quick) QUICK=1 ;;
    --force) FORCE=1 ;;
    --stage) ONLY="NEXT" ;;
    *) [ "$ONLY" = "NEXT" ] && ONLY="$a" ;;
  esac
done
FAIL=0
# Stages marked NEEDS_WEIGHTS load runs/*/weights_*.pt. Those are gitignored --
# they are ~5.7 MB each and regenerable -- so a clean clone cannot run them. In
# --quick mode they are skipped with their committed JSON verified instead, which
# is what --quick is for. --force does not override that; there is nothing to force.
# REPORT=<file> before a stage call captures that stage's stdout to results/<file>,
# so the committed *_report.txt artifacts are regenerable. Without this every report
# was a hand-captured stdout from some earlier run and drifted from its own script.
stage() {  # [REPORT=x] stage <n> <name> <runtime> <output-to-check> [NEEDS_WEIGHTS] <cmd...>
  local n="$1" name="$2" rt="$3" out="$4"; shift 4
  # capture and clear immediately: the skip paths below return early, and a leaked
  # REPORT would redirect the NEXT stage's stdout into this stage's report file.
  local rep="${REPORT:-}"; unset REPORT
  local needs=0
  if [ "${1:-}" = "NEEDS_WEIGHTS" ]; then needs=1; shift; fi
  [ -n "$ONLY" ] && [ "$ONLY" != "$n" ] && return 0
  echo ""
  echo "───────────────────────────────────────────────────────────────────────"
  echo " STAGE $n — $name"
  echo "   expected runtime: $rt"
  if [ "$needs" -eq 1 ] && [ ! -d runs ]; then
    if [ -e "$out" ]; then
      echo "   SKIP — needs trained weights in runs/ (gitignored, not in a clean clone)."
      echo "          Its committed result is present: $out"
    else
      echo "   FAILED — needs runs/ and $out is absent. Run without --quick to train."
      FAIL=1
    fi
    return 0
  fi
  if [ -n "$out" ] && [ -e "$out" ] && [ "$FORCE" -eq 0 ]; then
    echo "   SKIP — $out already exists (use --force to regenerate)"
    return 0
  fi
  echo "   running: $*"
  local rc=0
  if [ -n "$rep" ]; then
    "$@" > "results/$rep" 2>&1 || rc=$?
    [ $rc -eq 0 ] && echo "   OK (stdout -> results/$rep)"
  else
    "$@" || rc=$?
    [ $rc -eq 0 ] && echo "   OK"
  fi
  if [ $rc -eq 0 ]; then
    # record what this stage actually regenerated, so verify_reproduction.py can tell
    # a rewritten file from one the clone merely carried in.
    [ -n "$out" ] && [ -e "$out" ] && basename "$out" >> results/_regenerated.txt
  else echo "   FAILED (exit $rc)"; FAIL=1; fi
}
# Only a whole-pipeline run starts a fresh list; --stage N appends to the existing
# one, so re-running a single stage does not erase what the full run recorded.
[ -z "$ONLY" ] && rm -f results/_regenerated.txt
echo "RWM reproduction — full pipeline"
echo "  mode: $([ $QUICK -eq 1 ] && echo '--quick (no training)' || echo 'full')"
echo "  python: $PY"
# M13: the pipeline recorded torch/numpy versions into artifacts but never checked
# them, and verify_reproduction.py cannot compare them because they are strings.
# A mismatch here invalidates bitwise comparison, so fail loudly and early.
"$PY" - <<'ENVCHECK' || { echo "  ENVIRONMENT MISMATCH — see requirements.txt"; exit 2; }
import sys
want = {"torch": "2.2.2", "numpy": "1.26.4"}
bad = []
for mod, exp in want.items():
    try:
        got = __import__(mod).__version__
    except Exception as e:
        bad.append(f"{mod}: not importable ({e})"); continue
    if got.split("+")[0] != exp:
        bad.append(f"{mod}: {got}, expected {exp}")
if bad:
    print("  " + "\n  ".join(bad)); sys.exit(1)
print(f"  env OK: torch {want['torch']}, numpy {want['numpy']}, python {sys.version.split()[0]}")
ENVCHECK

# M12: stage 1's output-check was the CSV itself, so once setup.sh had run once the
# stage skipped -- and with it the two SHA-256 checks whose failure message says
# results from different bytes "are not comparable". Passing an empty output-check
# makes it run every time; setup.sh is idempotent and re-verifies the hashes.
stage 1 "Fetch upstreams and verify artifact hashes" "2 min" \
      "" ./setup.sh
REPORT=step0_report.txt stage 2 "Data checks and velocity regimes" "20 s" \
      results/step0_strat.json $PY scripts/step0_velocity_regimes.py
stage 3 "Harness acceptance tests (6 tests)" "30 s" \
      results/step2_acceptance.json $PY src/rollout_eval.py
stage 4 "Score the released checkpoint" "60 s" \
      results/manifest.json $PY src/score_reference.py
REPORT=step4_3_report.txt stage 5 "Acceptance gate: losses and gradients" "90 s" \
      results/step4_3_differential.json $PY scripts/step4_3_differential.py
stage 6 "Differential test vs the reference module" "60 s" \
      results/task5_differential.json $PY scripts/task5_differential.py
REPORT=taskAB_report.txt stage 7 "Released checkpoint under nRMSE, all aggregations" "5 min" \
      results/taskAB_gate_r27.json $PY scripts/taskAB_gate_r27.py
REPORT=batch1_post_retraction_report.txt stage 8 "Effective sample size and the 20-trajectory characterisation" "8 min" \
      results/batch1_post_retraction.json $PY scripts/batch1_retract_jensen_char.py


# --- pre-training analysis that later stages consume -------------------------
# step4_0a_results.json holds the nRMSE scale vector that stage 14 and
# task2_reference_nrmse both load. It was outside the pipeline entirely.
stage 8a "Step 3 results restated under the causal convention" "2 min" \
      results/step4_0a_results.json $PY scripts/step4_0a_restate.py
stage 8b "Action convention: the ridge test and its refutation" "90 s" \
      results/task1_action_convention.json $PY scripts/task1_action_convention.py
stage 8c "The PD law behind the action convention" "60 s" \
      results/task1b_pd_law.json $PY scripts/task1b_pd_law.py
stage 8d "Is the checkpoint actor the data-collection policy?" "60 s" \
      results/task1c_policy.json $PY scripts/task1c_policy_test.py
stage 8e "The reset-row argument for k = -1" "30 s" \
      results/task1d_reset.json $PY scripts/task1d_reset_argument.py
stage 8f "Harness hardening checks" "60 s" \
      results/task3_hardening.json $PY scripts/task3_harness_hardening.py
stage 8g "Released checkpoint under nRMSE at n=10" "2 min" \
      results/task2_reference_nrmse.json $PY scripts/task2_reference_nrmse.py
stage 8h "Per-horizon, per-group breakdown" "3 min" \
      results/task2_4_results.json $PY scripts/task2_4_horizon_groups.py
stage 8i "Evaluation power and the ddof convention" "4 min" \
      results/task3_4_power_ddof.json NEEDS_WEIGHTS $PY scripts/task3_4_power_and_ddof.py
stage 8j "Convergence of the metric with trajectory count" "3 min" \
      results/task3b_convergence.json $PY scripts/task3b_convergence.py
# Flags read from each artifact's own `config` block, not guessed. Run bare, this
# script writes untagged files that are not committed and leaves
# results/overfit_weights_b32lr1e3.pt -- stage 8l's input -- absent.
stage 8k "Overfit one batch, batch 32 / lr 1e-3 (R-18)" "8 min" \
      results/step4_4_overfit_b32lr1e3.json $PY scripts/step4_4_overfit.py \
      --iters 2000 --batch 32 --ensemble 1 --lr 1e-3 --max-seconds 100000 --tag _b32lr1e3
# X-06: this one terminates on the 2700 s wall-clock cap, not on convergence --
# 451 of 2000 iterations on the reference machine. A faster host runs further and
# its numbers will differ; that is documented, not a regression.
stage 8k2 "Overfit one batch, ensemble 1 / batch 1024 (R-17, cap-terminated)" "45 min" \
      results/step4_4_overfit_ens1.json $PY scripts/step4_4_overfit.py \
      --iters 2000 --batch 1024 --ensemble 1 --max-seconds 2700 --tag _ens1
stage 8l "Deterministic-vs-stochastic loss floor at the overfit weights" "30 s" \
      results/step5_6_overfit_floor.json $PY scripts/step5_6_overfit_floor.py
REPORT=step4_5_report.txt stage 8m "CPU timing budget" "5 min" \
      results/step4_5_timing.json $PY scripts/step4_5_timing.py

if [ $QUICK -eq 0 ]; then
  stage 9 "TRAINING — six main runs, 2500 iters" "6 h" \
        results/step5_armB_seed2.json ./run_remaining.sh
  stage 10 "TRAINING — two convergence runs, 10000 iters" "8 h" \
        results/step5_armB_seed1_10k.json ./run_10k.sh
  stage 11 "TRAINING — contamination and corrected-objective arms" "6 h" \
        results/step5_armA_seed2_nll.json ./run_tasks45.sh
  stage 11b "TRAINING — duplication control arm" "2 h" \
        results/step5_armA_seed2_dup.json ./run_control.sh
else
  echo ""
  echo " STAGES 9-11 (training, ~20 h) SKIPPED in --quick mode."
  echo "   Their outputs are committed as results/step5_*.json and are consumed below."
fi

REPORT=task4_report.txt stage 12 "Two-arena analysis and M-16" "3 min" \
      results/task4_arenas.json NEEDS_WEIGHTS $PY scripts/task4_arenas_and_difficulty.py
REPORT=task5_2_report.txt stage 13 "Bootstrap CIs on the six runs" "4 min" \
      results/task5_2_bootstrap.json NEEDS_WEIGHTS $PY scripts/task5_2_bootstrap.py
REPORT=task5_analysis_report.txt stage 14 "Task 5 analysis and M-23's verdict" "6 min" \
      results/task5_analysis.json NEEDS_WEIGHTS $PY scripts/task5_analyse.py
REPORT=task2_3_report.txt stage 15 "Matched per-dimension comparison and the trend fit" "3 min" \
      results/task2_3_matched_trend.json NEEDS_WEIGHTS $PY scripts/task2_3_matched_and_trend.py

# Stages 16-20 were outside the pipeline until the review. Between them they carry
# R-22, R-23, R-24, R-26 (step6_analysis.json), the whole of contribution 1
# (task1_calibration.json), and R-54, R-55 and R-56.
REPORT=step6_analysis_report.txt stage 16 "Six-run A/B analysis and the pooled collapse fit" "2 min" \
      results/step6_analysis.json NEEDS_WEIGHTS $PY scripts/step6_analyse.py
REPORT=task1_calibration_report.txt stage 17 "Calibration of all four models" "10 min" \
      results/task1_calibration.json NEEDS_WEIGHTS $PY scripts/task1_calibration.py
REPORT=task2_sigma_profile_report.txt stage 18 "Sigma profile across forecast steps" "6 min" \
      results/task2_sigma_profile.json NEEDS_WEIGHTS $PY scripts/task2_sigma_profile.py
REPORT=task3_control_arm_report.txt stage 19 "Duplication control: the training-loss discriminator" "5 s" \
      results/task3_control_arm.json $PY scripts/task3_control_arm.py
REPORT=task3_three_way_report.txt stage 20 "Three-way rollout comparison, both resampling units" "12 min" \
      results/task3_three_way.json NEEDS_WEIGHTS $PY scripts/task3_three_way.py
REPORT=task4_report_contamination.txt stage 20a "Contamination comparison, 32 cells" "12 min" \
      results/task4_contamination.json NEEDS_WEIGHTS $PY scripts/task4_contamination_analysis.py
stage 20b "min_logstd: O-12's second axis" "20 s" \
      results/step6_3_min_logstd.json NEEDS_WEIGHTS $PY scripts/step6_3_min_logstd.py
REPORT=review_bootstrap_unit_report.txt stage 20c "Bootstrap resampling unit (M-27)" "8 min" \
      results/review_bootstrap_unit.json NEEDS_WEIGHTS $PY scripts/review_bootstrap_unit.py
stage 21 "Ledger consistency check and claims-to-evidence map" "5 s" \
      "" $PY scripts/ledger_check.py

# The paper is generated, not written by hand: paper_numbers.py collects every value
# it quotes from the artifacts, build_paper.py substitutes them into PAPER.template.md
# and fails if any placeholder is unresolved.
stage 22 "Paper figures" "40 s" \
      figures/paper_fig1_calibration.png NEEDS_WEIGHTS $PY scripts/paper_figures.py
stage 23 "Collect the paper's numbers from the artifacts" "5 s" \
      results/paper_numbers.json $PY scripts/paper_numbers.py
stage 24 "Build PAPER.md and PAPER.tex" "5 s" \
      "" $PY scripts/build_paper.py
stage 25 "Build MODEL_CARD.md (checkpoint sha256s and per-checkpoint limits)" "10 s" \
      "" $PY scripts/build_model_card.py
# Compiles PAPER.tex and fails on errors, overfull boxes, LaTeX warnings or stray
# markdown emphasis. Skips loudly, not silently, where no TeX is installed.
stage 26 "Compile PAPER.tex" "30 s" \
      "" $PY scripts/compile_paper.py
stage 27 "Claims-versus-evidence audit" "10 s" \
      results/task_c1_claims_audit.json $PY scripts/task_c1_claims_audit.py
# Refuses to write the ZIP if any file in it carries the author or a repository
# under their account; third-party upstreams are allowlisted.
stage 28 "Assemble the anonymised supplementary archive" "20 s" \
      "" $PY scripts/build_supplementary.py

echo ""
echo "───────────────────────────────────────────────────────────────────────"
if [ $FAIL -eq 0 ]; then echo " PIPELINE COMPLETE — no stage failed"; else
  echo " PIPELINE FINISHED WITH FAILURES — see above"; fi
exit $FAIL
