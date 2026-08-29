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
  stage 11c "TRAINING — ensemble-5 arms (M-43)" "13 h" \
        results/step5_armA_seed2_ens5.json ./run_ens5.sh
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
# Part B and Part D. These were added during submission hardening and must run
# before stage 23 collects the paper's numbers, because the paper quotes them.
# Only the permutation test loads runs/ (it scores our own arms alongside the
# released checkpoint), so only it is NEEDS_WEIGHTS. The other three need the
# released checkpoint alone, which setup.sh fetches, so they DO run in a clean
# clone and their values count toward the regenerated set. Marking all four
# NEEDS_WEIGHTS would have skipped three stages that work, and understated
# reproducibility. Leaving them out of this file would have
# been worse than it looks: a clean clone CARRIES their outputs in, so
# verify_reproduction.py would have scored them as copied rather than
# regenerated and the reproducibility figure would have silently excluded the
# paper's newest results.
REPORT=task_b_permutation_report.txt stage 20d "Permutation test over trajectories (R-61)" "12 min" \
      results/task_b_permutation.json NEEDS_WEIGHTS $PY scripts/task_b_permutation.py
REPORT=task_d_nind20_report.txt stage 20e "Epistemic table at n=20, forecast-index baseline, penalty CI (R-62, R-63, R-65)" "6 min" \
      results/task_d_nind20.json $PY scripts/task_d_nind20.py
REPORT=task_d2b_robustness_report.txt stage 20f "Forecast-index control, four stronger forms (R-66)" "5 min" \
      results/task_d2b_robustness.json $PY scripts/task_d2b_robustness.py
REPORT=task_d3_perhorizon_report.txt stage 20g "Per-horizon recalibration (R-64)" "3 min" \
      results/task_d3_perhorizon.json $PY scripts/task_d3_perhorizon.py
REPORT=task_d3_ens5_report.txt stage 20h "Ensemble-5 replication and M-43's verdict (R-67)" "8 min" \
      results/task_d3_ens5.json NEEDS_WEIGHTS $PY scripts/task_d3_ens5.py
REPORT=task_d3b_ens5_power_report.txt stage 20i "Ensemble-5 companion and power at n=4 (R-67)" "6 min" \
      results/task_d3b_ens5_power.json NEEDS_WEIGHTS $PY scripts/task_d3b_ens5_power.py
# ------------------------------------------------------------------------
# Six analyses that the paper's numbers depend on and that this pipeline never
# ran. Between them they produce about 300 of the paper's ~1,600 substituted
# values -- §5's whole by-horizon table (a1), the epistemic table §6.2 leads
# with (b2), §5's three-seed headline (d1), §6.8's recalibration (d2), §6.6's
# multiplicity correction (c3) and what the originals report (original_paper).
#
# A clean clone CARRIED THEM IN and verify_reproduction.py counted them as
# copied rather than regenerated, which it reports honestly -- but the paper's
# reproduction claim reads as broader than the test, and the fix is to widen
# the test rather than narrow the claim. Found by auditing every artifact
# paper_numbers.py reads against the scripts this file actually invokes; the
# first two audits of it were themselves wrong, matching declared outputs and
# then matching mere mentions of a filename.
# ------------------------------------------------------------------------
REPORT=task_b2_epistemic_report.txt stage 20j1 "B2 — the epistemic table §6.2 leads with" "4 min" \
      results/task_b2_epistemic.json NEEDS_WEIGHTS $PY scripts/task_b2_epistemic.py
REPORT=a1_ab_by_horizon_report.txt stage 20j2 "A1 — the A/B result at every horizon (§5's table)" "10 min" \
      results/a1_ab_by_horizon.json NEEDS_WEIGHTS $PY scripts/a1_ab_by_horizon.py
REPORT=task_d1_threeseed_report.txt stage 20j3 "D1 — §5's headline over three seeds" "6 min" \
      results/task_d1_threeseed.json NEEDS_WEIGHTS $PY scripts/task_d1_threeseed.py
REPORT=task_d2_recalibration_report.txt stage 20j4 "D2 — the single-multiplier recalibration" "4 min" \
      results/task_d2_recalibration.json NEEDS_WEIGHTS $PY scripts/task_d2_recalibration.py
REPORT=task_c3_multiplicity_report.txt stage 20j5 "C3 — multiplicity correction over the A/B cells" "3 min" \
      results/task_c3_multiplicity.json NEEDS_WEIGHTS $PY scripts/task_c3_multiplicity.py
stage 20j6 "What the original papers report, claim by claim" "10 s" \
      results/original_paper_figures.json $PY scripts/original_paper_figures.py
# E4/E5/E7. Three measurements the revision added, each governed by a rule
# committed before its data existed.
#
# E4 back-propagates each of the seven loss terms ALONE and records the gradient
# reaching sigma. §6.3's derivation covers two of them and its completeness rested
# on the other five being inert, which was asserted and is now measured.
REPORT=e4_sigma_gradients_report.txt stage 20j7 "E4 — what each loss term does to sigma" "2 min" \
      results/e4_sigma_gradients.json $PY scripts/e4_sigma_gradients.py
# E5 (M-50). The dilution study calibrates the thresholds and MUST run first; the
# experiment reads them. Both are cheap and neither needs trained weights: the
# head is built from the released architecture config and trained on synthetic
# data whose true noise is known.
REPORT=e5_sigma_dilution_report.txt stage 20j8 "E5 — dilution study, the thresholds M-50 quotes" "35 min" \
      results/e5_sigma_dilution.json $PY scripts/e5_synthetic_sigma.py --dilution
REPORT=e5_synthetic_sigma_report.txt stage 20j9 "E5 — sigma recovery against known noise (M-50)" "20 min" \
      results/e5_synthetic_sigma.json $PY scripts/e5_synthetic_sigma.py
# E7 (M-51/M-52). Same ordering: the power run fixes the MDE from quantities that
# already exist, before either new baseline is computed.
REPORT=e7_power_report.txt stage 20ja "E7 — power for M-51, before the baselines exist" "3 min" \
      results/e7_free_baselines_power.json NEEDS_WEIGHTS $PY scripts/e7_free_baselines.py --power
REPORT=e7_free_baselines_report.txt stage 20jb "E7 — three free ranking baselines (M-51)" "3 min" \
      results/e7_free_baselines.json NEEDS_WEIGHTS $PY scripts/e7_free_baselines.py
REPORT=task_c2_data_budget_report.txt stage 20j "Data budget against the reference (C2)" "10 s" \
      results/task_c2_data_budget.json $PY scripts/task_c2_data_budget.py
# ---------------------------------------------------------------------------
# Pre-submission revision. V1-V4 and P1 are Phase 0: they establish facts the
# rest depends on, and P1's power check is committed together with the two rules
# it governs, before either was tested.
# ---------------------------------------------------------------------------
# Reads the pinned upstreams and the released checkpoint's tensors. Every
# file:line it cites is read back and fingerprinted, so a citation that drifts
# fails here rather than going stale in the PDF.
stage 20k "V1 — ensemble topology: what is shared across the five members" "10 s" \
      results/v1_ensemble_topology.json NEEDS_WEIGHTS $PY scripts/v1_ensemble_topology.py
stage 20l "V2 — which horizon is the deployment horizon" "5 s" \
      results/v2_deployment_horizon.json $PY scripts/v2_deployment_horizon.py
stage 20m "V3 — metric and coverage definitions, from the implementation" "5 s" \
      results/v3_metric_definitions.json $PY scripts/v3_metric_definitions.py
# P1 estimates what M-44 and M-45 can detect at the sample sizes they face. M-43
# was committed without this check and returned DOES NOT GENERALISE partly
# because of it; so did M-24 before that.
REPORT=p1_power_check_report.txt stage 20n "P1 — power check for M-44 and M-45" "12 min" \
      results/p1_power_check.json NEEDS_WEIGHTS $PY scripts/p1_power_check.py
# A2 discharges M-45.
REPORT=a2_trajectory_level_control_report.txt stage 20o "A2 — the trajectory-level control, and M-45's verdict" "14 min" \
      results/a2_trajectory_level_control.json $PY scripts/a2_trajectory_level_control.py
# T1's bibliography. --verify needs the network and a clean clone must not, so
# the recorded verification is what the build reads; refresh it with --verify.
REPORT=t1_bibliography_report.txt stage 20p "T1 — the section 2 bibliography, verified" "5 s" \
      results/t1_bibliography_verified.json $PY scripts/t1_bibliography.py
# T5's anonymised correspondence transcript, generated from the ledger so the two
# cannot drift, with every quotation the paper uses asserted present.
stage 20q "T5 — anonymised correspondence transcript" "5 s" \
      results/t5_anon_transcript.json $PY scripts/t5_anon_transcript.py
# A1. The consent letter, and the rewrite that runs if consent is refused. Both
# generated, and placed here because 20q writes the transcript this reads.
#
# The fragment list is EXTRACTED from PAPER.template.md rather than typed:
# consent obtained for a list that does not match what the paper prints is not
# informed consent. Every fragment is then checked verbatim against the
# transcript, and 20q's own quote list is derived from the same extractor -- it
# was a typed list of six of which two were not in the paper.
#
# Nothing here sends anything. The letter is a draft for a person to send.
stage 20q1 "A1 — consent letter and the no-quotation fallback" "5 s" \
      results/a1_consent_letter.json $PY scripts/a1_consent_letter.py
# R1/R2: the independent-initialisation contrast M-44 governs. R1 is the two extra
# Arm A ens1 seeds (./run_indep_ens.sh, ~1.2 h each); R2 scores seeds 0-4 together
# as an ensemble and returns M-44's verdict.
REPORT=r2_independent_ensemble_report.txt stage 20r "R2 — the independent-init ensemble, and M-44's verdict" "10 min" \
      results/r2_independent_ensemble.json NEEDS_WEIGHTS $PY scripts/r2_independent_ensemble.py
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
# C2: the README is generated from the same paper_numbers.json the paper is, so
# the two cannot drift. It had drifted materially -- including a claim section 8
# had explicitly withdrawn, still standing here as a finding.
stage 25a "Build README.md from its template" "5 s" \
      "" $PY scripts/build_readme.py
# Compiles PAPER.tex and fails on errors, overfull boxes, LaTeX warnings or stray
# markdown emphasis. Skips loudly, not silently, where no TeX is installed.
stage 26 "Compile PAPER.tex" "30 s" \
      "" $PY scripts/compile_paper.py
stage 27 "Claims-versus-evidence audit" "10 s" \
      results/task_c1_claims_audit.json $PY scripts/task_c1_claims_audit.py
# Refuses to write the ZIP if any file in it carries the author or a repository
# under their account; third-party upstreams are allowlisted.
# The declared output is the manifest, not the ZIP. It was "" -- no declared
# output -- which meant supplementary_manifest.json never entered
# results/_regenerated.txt even on the runs where this stage passed, so
# verify_reproduction.py counted it as a file the clone carried in rather than
# one the pipeline rewrote. Combined with this stage failing outright on the
# SWH checker's identity hits, the published 100.00% came from a regenerated
# set that silently omitted it: the M-28 shape, inside the claim M-28 is about.
stage 28 "Assemble the anonymised supplementary archive" "20 s" \
      results/supplementary_manifest.json $PY scripts/build_supplementary.py
# The numeral check guarantees every printed number came from an artifact. It
# cannot see a sentence that takes correct numbers and asserts a wrong relation
# between them -- six such defects shipped before anyone looked. --self-test runs
# every assertion against a deliberately corrupted expectation on every build, so
# an assertion that has stopped being able to fail is caught here rather than
# quietly passing forever.
REPORT=comparative_claims_report.txt stage 28a "Comparative-claim check, with self-test" "10 s" \
      results/comparative_claims.json $PY scripts/check_comparative_claims.py --self-test
# B8. The abstract used to claim "No number here is typed". It was false and it
# was unenforced: build_paper.py PRINTED the count of typed numerals every run
# and asserted nothing about them. This classifies every one against a narrow
# class or a declared exception, and fails on anything left over -- a measurement
# in prose. --self-test plants one and requires it to be caught.
REPORT=typed_numerals_report.txt stage 28a1 "Typed-numeral audit, with self-test" "5 s" \
      results/typed_numerals.json $PY scripts/typed_numeral_audit.py
# C1. The kind that would have caught the four defects an hour of reading found
# and twenty-two check kinds did not: a sentence restating a quantity another
# section owns. --acceptance re-runs it against the drafts each defect actually
# stood in and asserts it fires, then asserts it is silent on this tree.
REPORT=restatement_index_report.txt stage 28a2 "Restatement index over the paper's own numerals" "10 s" \
      results/restatement_index.json $PY scripts/restatement_index.py
# The h=100 sweep. Registered as the `horizon-consistency` kind above and run
# again here on its own, because its report is the useful artifact when it
# fails: it names every sentence, the horizon its numbers came from, and the
# horizon the sentence claims. The re-anchoring from h=368 left 28 findings
# across 20 locations in the 24 August draft, and no provenance check could see
# one of them.
REPORT=horizon_sweep_report.txt stage 28c "Horizon sweep over the paper's own prose" "5 s" \
      results/horizon_sweep.json $PY scripts/horizon_sweep.py
# C3: stages an anonymised copy, scrubbing by SUBSTITUTION rather than exclusion,
# checks file paths as well as contents, and plants a deny-list string on every
# run to prove the scan is still live.
stage 28b "Anonymised submission bundle, with its self-test" "40 s" \
      results/anon_bundle.json $PY scripts/make_anon_bundle.py
stage 29a "Part F submission gate, six checks" "30 s" \
      results/part_f_gate.json $PY scripts/part_f_gate.py
stage 29 "Submission readiness gate" "40 s" \
      "" $PY scripts/submission_check.py

echo ""
echo "───────────────────────────────────────────────────────────────────────"
if [ $FAIL -eq 0 ]; then echo " PIPELINE COMPLETE — no stage failed"; else
  echo " PIPELINE FINISHED WITH FAILURES — see above"; fi
exit $FAIL
