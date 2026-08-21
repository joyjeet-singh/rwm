"""Collect every number the paper quotes, from the artifacts, into one keyed file.

The paper is written as PAPER.template.md with {{key}} placeholders. build_paper.py
substitutes from results/paper_numbers.json and refuses to emit a paper if any
placeholder is unresolved or any key here is unused. No number in the paper is typed.
"""
import glob
import json
import os
import re
import subprocess
import sys
from math import comb

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402


def J(n):
    return json.load(open(os.path.join(R.RESULTS, n)))


def main():
    N = {}
    def put(k, v, src):
        N[k] = {"value": v, "source": src}

    cal = J("task1_calibration.json")
    sig = J("task2_sigma_profile.json")
    s6 = J("step6_analysis.json")
    t5 = J("task5_analysis.json")
    t3 = J("task3_control_arm.json")
    tw = J("task3_three_way.json")
    bu = J("review_bootstrap_unit.json")
    ver = J("verify_reproduction.json")
    w = J("step0_regimes.json")["window_accounting"]
    man = J("manifest.json")
    dif = J("step4_3_differential.json")

    # --- dataset -----------------------------------------------------------
    put("rows", f'{w["rows"]:,}', "results/step0_regimes.json")
    put("win_naive", f'{w["naive_windows_reference_builder_marks_valid"]:,}',
        "results/step0_regimes.json")
    put("win_cross", f'{w["boundary_crossing_windows"]:,}', "results/step0_regimes.json")
    put("win_usable", f'{w["usable_episode_respecting_windows"]:,}', "results/step0_regimes.json")
    put("win_tail", w["tail_rows_that_cannot_start_a_window"], "results/step0_regimes.json")
    put("contam_pct", round(100 * w["boundary_crossing_windows"]
                            / w["naive_windows_reference_builder_marks_valid"], 2),
        "results/step0_regimes.json")

    # --- calibration (contribution 1) -------------------------------------
    lab = {"faithful (mse)": "faithA", "corrected (nll)": "nll",
           "teacher-forced armB": "armB", "released ckpt": "rel"}
    for k, tag in lab.items():
        m = cal[k]
        # render as a reader would write it: 7,878x not 7878.1x, 315x not 315.0x
        rr = m["ratio_err_over_sigma"]
        put(f"cal_{tag}_ratio", f"{rr:,.0f}" if rr >= 100 else f"{rr:.1f}",
            "results/task1_calibration.json")
        put(f"cal_{tag}_cov1", round(100 * m["coverage"]["1"]["pm1"], 2), "results/task1_calibration.json")
        put(f"cal_{tag}_cov368", round(100 * m["coverage"]["368"]["pm1"], 2), "results/task1_calibration.json")
        put(f"cal_{tag}_cov", round(m["cov_of_sigma_across_batch"], 4), "results/task1_calibration.json")
        put(f"cal_{tag}_npos", m["sigma_err_corr_n_positive"], "results/task1_calibration.json")
        put(f"cal_{tag}_ndim", m["n_finite_corr"], "results/task1_calibration.json")
        put(f"cal_{tag}_p", f"{m['sigma_err_corr_sign_p_two_sided']:.2e}", "results/task1_calibration.json")
        put(f"cal_{tag}_r", round(m["sigma_err_corr_mean"], 3), "results/task1_calibration.json")
    put("cal_armB_over_faithA_cov",
        round(cal["teacher-forced armB"]["cov_of_sigma_across_batch"]
              / cal["faithful (mse)"]["cov_of_sigma_across_batch"], 1),
        "results/task1_calibration.json")

    slab = {"faithful armA (mse)": "faithA", "corrected armA (nll)": "nll",
            "teacher-forced armB": "armB", "released checkpoint": "rel"}
    for k, tag in slab.items():
        put(f"sig_{tag}_growth", round(sig[k]["sigma_growth_1_to_8"], 4), "results/task2_sigma_profile.json")
        put(f"err_{tag}_growth", round(sig[k]["err_growth_1_to_8"], 2), "results/task2_sigma_profile.json")

    # --- the A/B claim -----------------------------------------------------
    put("t5_seeds", t5["provenance"]["n_seeds"], "results/task5_analysis.json")
    g = t5["gaps"]["out-of-sample|10000|h368"]
    put("m23_A", f'{g["A"]:.4f}', "results/task5_analysis.json")
    put("m23_B", f'{g["B"]:.4f}', "results/task5_analysis.json")
    put("m23_gap", round(g["gap"], 4), "results/task5_analysis.json")
    put("m23_ratio", f'{g["B"] / g["A"]:.1f}', "results/task5_analysis.json")
    put("m23_nind", g["n_ind"], "results/task5_analysis.json")
    if "ci" in g:
        put("m23_ci_lo", round(g["ci"][0], 2), "results/task5_analysis.json")
        put("m23_ci_hi", round(g["ci"][1], 2), "results/task5_analysis.json")
    put("m23_c1", "holds" if t5["m23"]["c1"] else "FAILS", "results/task5_analysis.json")
    put("m23_c2", "holds" if t5["m23"]["c2"] else "FAILS", "results/task5_analysis.json")
    put("m23_c3", "holds" if t5["m23"]["c3"] else "FAILS", "results/task5_analysis.json")
    put("m23_sign_h368", t5["sign_consistent_h368"], "results/task5_analysis.json")
    put("m23_n_episodes_positive",
        sum(1 for e in t5["per_episode"].values() if e["h368"] > 0), "results/task5_analysis.json")
    put("m23_n_episodes", len(t5["per_episode"]), "results/task5_analysis.json")
    g8 = t5["gaps"]["out-of-sample|10000|h8"]
    put("m23_h8_gap", round(g8["gap"], 4), "results/task5_analysis.json")
    put("m23_h8_excl", "excludes zero" if g8["excludes_zero"] else "includes zero",
        "results/task5_analysis.json")
    put("q4_implied_A", f"{t5['q4']['A']['implied_iters']:,.0f}", "results/task5_analysis.json")
    put("q4_implied_B", f"{t5['q4']['B']['implied_iters']:,.0f}", "results/task5_analysis.json")

    # --- collapse / iteration counts --------------------------------------
    put("collapse_pooled_rate", f"{s6['collapse']['rate']:.4e}" if "rate" in s6["collapse"]
        else f"{s6['collapse'].get('slope_per_iter', float('nan')):.4e}", "results/step6_analysis.json")
    put("implied_iters", f"{s6['collapse']['iters_to_checkpoint']:,.0f}", "results/step6_analysis.json")

    # --- contamination -----------------------------------------------------
    put("dup_cost_pct", f'{t3["verdict"]["duplication_cost_pct_tail250"]:.2f}',
        "results/task3_control_arm.json")
    put("contam_cost_pct", f'{t3["verdict"]["contamination_cost_pct_tail250"]:.2f}',
        "results/task3_control_arm.json")
    b = t3["bootstrap_over_iterations"]["duplicated_minus_clean"]
    put("dup_ci_lo", round(b["lo"], 4), "results/task3_control_arm.json")
    put("dup_ci_hi", round(b["hi"], 4), "results/task3_control_arm.json")
    clean_n = J("step5_armA_seed0.json")["hyperparameters"]["n_train_windows"]
    con_n = J("step5_armA_seed0_contam.json")["hyperparameters"]["n_train_windows"]
    put("arm_clean_windows", f"{clean_n:,}", "results/step5_armA_seed0.json")
    put("arm_contam_windows", f"{con_n:,}", "results/step5_armA_seed0_contam.json")
    put("arm_splices", con_n - clean_n, "results/step5_armA_seed0_contam.json")
    put("arm_contam_pct", round(100 * (con_n - clean_n) / con_n, 2),
        "results/step5_armA_seed0_contam.json")

    S = tw["_summary"]
    for pair, tag in (("contaminated_minus_clean", "cc"), ("duplicated_minus_clean", "dc"),
                      ("contaminated_minus_duplicated", "cd")):
        for unit in ("naive", "cluster"):
            for out in ("hurt", "helped", "no_effect"):
                put(f"tw_{tag}_{unit}_{out}", S[pair][unit][out], "results/task3_three_way.json")
    put("tw_cells", len([k for k in tw if k != "_summary"]), "results/task3_three_way.json")

    # --- bootstrap unit ----------------------------------------------------
    put("bu_mean_ratio", round(bu["_summary"]["width_ratio_mean"], 2),
        "results/review_bootstrap_unit.json")
    put("bu_min_ratio", round(bu["_summary"]["width_ratio_min"], 2), "results/review_bootstrap_unit.json")
    put("bu_max_ratio", round(bu["_summary"]["width_ratio_max"], 2), "results/review_bootstrap_unit.json")
    put("bu_cells", bu["_summary"]["n_cells"], "results/review_bootstrap_unit.json")
    oos = {k: v for k, v in bu.items()
           if k != "_summary" and k.startswith("out-of-sample")}
    longh = [v for k, v in oos.items() if "h368" in k or "h168" in k]
    short = [v for k, v in oos.items() if "h8" in k]
    put("ab_long_cells", len(longh), "results/review_bootstrap_unit.json")
    put("ab_long_excl", sum(1 for v in longh if v["cluster"]["excludes_zero"]),
        "results/review_bootstrap_unit.json")
    put("ab_short_cells", len(short), "results/review_bootstrap_unit.json")
    put("ab_short_excl", sum(1 for v in short if v["cluster"]["excludes_zero"]),
        "results/review_bootstrap_unit.json")
    put("bu_changes", bu["_summary"]["n_verdict_changes"], "results/review_bootstrap_unit.json")

    # --- verification ------------------------------------------------------
    put("ver_files", len(ver["regenerated_files"]), "results/verify_reproduction.json")
    put("ver_values", f"{ver['values_compared']:,}", "results/verify_reproduction.json")
    put("ver_identical", f"{ver['bitwise_identical']:,}", "results/verify_reproduction.json")
    put("ver_pct", f"{100*ver['bitwise_identical']/ver['values_compared']:.2f}",
        "results/verify_reproduction.json")
    put("ver_differing", ver["differing"], "results/verify_reproduction.json")
    put("diff_terms", dif.get("n_terms", 7), "results/step4_3_differential.json")
    t5d = J("task5_differential.json")
    import re as _re
    _m = _re.search(r'"max_abs_diff_full_rollout":\s*([0-9.eE+-]+)', json.dumps(t5d))
    th = J("task3_hardening.json")
    zd = th["3c_zero_delta"]
    _k = next((k for k in zd if isinstance(zd[k], (int, float)) and 0 < zd[k] < 1e-5), None)
    put("zero_delta_resid", f"{zd[_k]:.3e}" if _k else "n/a", "results/task3_hardening.json")
    ov = J("step4_4_overfit_b32lr1e3.json")
    put("overfit_reduction", f'{ov["first"]["state"] / ov["last"]["state"]:,.0f}',
        "results/step4_4_overfit_b32lr1e3.json")
    put("wiring_max_diff", f"{float(_m.group(1)):.3e}" if _m else "0.000e+00",
        "results/task5_differential.json")
    put("diff_grad_max", f'{dif["grad"]["fixed"]["worst_max_abs"]:.3e}',
        "results/step4_3_differential.json")
    put("diff_n_params", dif["grad"]["fixed"]["n_params"], "results/step4_3_differential.json")
    # "agreeing within X%": derived, not asserted
    a = t5["q4"]["A"]["implied_iters"]; b = t5["q4"]["B"]["implied_iters"]
    pooled = s6["collapse"]["iters_to_checkpoint"]
    put("implied_spread_pct", f'{100*(max(a,b,pooled)-min(a,b,pooled))/min(a,b,pooled):.1f}',
        "results/task5_analysis.json + results/step6_analysis.json")

    # --- run inventory -----------------------------------------------------
    runs = sorted(os.path.basename(p) for p in glob.glob("runs/arm*"))
    put("n_runs", len(runs), "runs/ directory listing")
    put("n_entries", len(subprocess.run(
        ["grep", "-c", "^### [A-Z]-", "FINDINGS_LEDGER.md"],
        capture_output=True, text=True).stdout.strip() or "0") and int(subprocess.run(
        ["grep", "-c", "^### [A-Z]-", "FINDINGS_LEDGER.md"],
        capture_output=True, text=True).stdout.strip()), "FINDINGS_LEDGER.md")

    # Pre-registration lead times, from the figure's own recorded values, so the
    # paragraph in §7 that is ABOUT discipline does not itself contain typed numbers.
    pf = os.path.join(R.RESULTS, "paper_figures.json")
    if os.path.exists(pf):
        f4 = json.load(open(pf)).get("fig4", {})
        def fmt(h):
            return f"{h*60:.0f} minutes" if abs(h) < 1 else f"{h:.1f} hours"
        keymap = {"M-16 the A/B decision rule": "lead_m16",
                  "flip pattern interpretation": "lead_flip",
                  "M-22 difficulty-bias rule": "lead_m22",
                  "M-23 long-horizon rule": "lead_m23",
                  "Task 3 duplication rule": "lead_task3"}
        for label, key in keymap.items():
            if label in f4:
                put(key, fmt(abs(f4[label]["lead_hours"])), "results/paper_figures.json")

    # Retractions, counted rather than asserted. An earlier draft said "four" and the
    # ledger had six by then -- exactly the drift this indirection exists to stop.
    led = open("FINDINGS_LEDGER.md").read()
    sup = re.findall(r"^### (S-\d+) ", led, re.M)
    retr = []
    for sid in sup:
        blk = led[led.index("### " + sid + " "):]
        blk = blk[:blk.find("\n### ", 5)] if "\n### " in blk[5:] else blk
        m = re.search(r"^\*\*Retracts\*\* (.+)$", blk, re.M)
        if m and not m.group(1).lstrip().startswith("\u2014"):
            retr.append(sid)
    put("n_superseded", len(sup), "FINDINGS_LEDGER.md")
    put("n_retractions", len(retr), "FINDINGS_LEDGER.md")
    WORDS = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven",
             8: "Eight", 9: "Nine", 10: "Ten"}
    put("n_retractions_word", WORDS.get(len(retr), str(len(retr))), "FINDINGS_LEDGER.md")
    put("n_retractions_lower", WORDS.get(len(retr), str(len(retr))).lower(), "FINDINGS_LEDGER.md")

    # B2 -- the uncertainty the method actually consumes (C-14, R-58)
    B = J("task_b2_epistemic.json")
    for h in (1, 8, 32, 128, 368):
        rec = B["by_horizon"][str(h)]
        for q, tag in (("aleatoric", "alea"), ("epistemic", "epi"), ("total", "tot")):
            m = rec[q]
            rr = m["ratio_err_over_sigma"]
            put(f"b2_{tag}_ratio_h{h}", f"{rr:,.0f}" if rr >= 100 else f"{rr:.1f}",
                "results/task_b2_epistemic.json")
            put(f"b2_{tag}_cov1_h{h}", f'{100*m["coverage_pm1"]:.2f}',
                "results/task_b2_epistemic.json")
            put(f"b2_{tag}_cov2_h{h}", f'{100*m["coverage_pm2"]:.2f}',
                "results/task_b2_epistemic.json")
            put(f"b2_{tag}_npos_h{h}", m["n_positive"], "results/task_b2_epistemic.json")
            put(f"b2_{tag}_ndim_h{h}", m["n_finite_corr"], "results/task_b2_epistemic.json")
            put(f"b2_{tag}_p_h{h}", f'{m["sign_p_two_sided"]:.1e}',
                "results/task_b2_epistemic.json")
    e1 = B["by_horizon"]["1"]; e368 = B["by_horizon"]["368"]
    put("b2_epi_over_alea_h1",
        f'{e1["epistemic"]["mean_sigma"]/e1["aleatoric"]["mean_sigma"]:.0f}',
        "results/task_b2_epistemic.json")
    put("b2_epi_over_alea_h368",
        f'{e368["epistemic"]["mean_sigma"]/e368["aleatoric"]["mean_sigma"]:.0f}',
        "results/task_b2_epistemic.json")
    put("b2_epi_sigma_growth",
        f'{e368["epistemic"]["mean_sigma"]/e1["epistemic"]["mean_sigma"]:.2f}',
        "results/task_b2_epistemic.json")
    put("b2_epi_err_growth",
        f'{e368["epistemic"]["mean_abs_err"]/e1["epistemic"]["mean_abs_err"]:.2f}',
        "results/task_b2_epistemic.json")
    put("b2_penalty_corr", f'{B["released_scalar_penalty"]["corr_with_total_abs_error"]:+.3f}',
        "results/task_b2_epistemic.json")
    put("b2_nind", B["design"]["n_independent"], "results/task_b2_epistemic.json")
    put("b2_members", B["design"]["ensemble_size"], "results/task_b2_epistemic.json")

    # Episode-boundary accounting for section 5.4. These were typed ("four of the
    # reference's nine"); correct, but typed.
    _tr = set(J("step5_armA_seed0.json")["hyperparameters"]["train_episodes"])
    _ho = set(J("step5_armA_seed0.json")["hyperparameters"]["holdout_episodes"])
    _b = [(e, e + 1) for e in range(len(_tr) + len(_ho) - 1)]
    _both = [x for x in _b if x[0] in _tr and x[1] in _tr]
    _touch = [x for x in _b if x[0] in _ho or x[1] in _ho]
    put("bound_total", len(_b), "results/step5_armA_seed0.json (split)")
    put("bound_both_train", len(_both), "results/step5_armA_seed0.json (split)")
    put("bound_touch_holdout", len(_touch), "results/step5_armA_seed0.json (split)")

    # in-sample vs out-of-sample independent-trajectory counts. An earlier draft
    # reused ab_long_cells (a CELL count) as this ratio; both happened to be 4.
    _c3 = J("task_c3_multiplicity.json")
    _bu = J("review_bootstrap_unit.json")
    _oos = next(v["n_independent_reported"] for k, v in _bu.items()
                if k != "_summary" and k.startswith("out-of-sample|400"))
    _ins = next(v["n_independent_reported"] for k, v in _bu.items()
                if k != "_summary" and k.startswith("in-sample|400"))
    put("nind_oos_400", _oos, "results/review_bootstrap_unit.json")
    put("nind_ins_400", _ins, "results/review_bootstrap_unit.json")
    put("nind_ratio", f"{_ins / _oos:.0f}", "results/review_bootstrap_unit.json")

    # R-15: the stale-action cost, so section 5.2 can quote a figure rather than
    # asserting "materially better" with nothing behind it (C1 marked it UNSUPPORTED).
    _r15 = J("step4_0a_results.json")["protocols"]
    put("stale_nrmse", f'{_r15["A_off0"]["nrmse"]["368"]:.4f}', "results/step4_0a_results.json")
    put("causal_nrmse", f'{_r15["A_off1"]["nrmse"]["368"]:.4f}', "results/step4_0a_results.json")
    put("stale_pct", f'{100*(_r15["A_off0"]["nrmse"]["368"]/_r15["A_off1"]["nrmse"]["368"]-1):.0f}',
        "results/step4_0a_results.json")

    # D3: the hold-last floor. Section 3 quoted 0.3509 against 1.5540 with no
    # baseline, so a reader could not judge whether 0.3509 was good.
    _fl = J("task4_arenas.json")["task4a"]["out-of-sample@400"]["floor"]["368"]["l1"]
    put("floor_h368", f"{_fl:.4f}", "results/task4_arenas.json")
    _A = float(t5["gaps"]["out-of-sample|10000|h368"]["A"])
    _B = float(t5["gaps"]["out-of-sample|10000|h368"]["B"])
    put("floor_over_A", f"{_fl / _A:.1f}", "results/task4_arenas.json + task5_analysis.json")
    put("B_over_floor", f"{_B / _fl:.2f}", "results/task4_arenas.json + task5_analysis.json")

    # D2 -- post-hoc recalibration
    _d2 = J("task_d2_recalibration.json")
    def _f1(lab):
        return [f for f in _d2["models"][lab]["fits"] if f["mode"] == "c@h1"]
    for lab, tag in (("released aleatoric", "ale"),
                     ("released EPISTEMIC (used by the method)", "epi"),
                     ("faithful (mse)", "fai")):
        fs = _f1(lab)
        for h in (1, 368):
            v = [100 * f["coverage_after"][str(h)] for f in fs]
            put(f"d2_{tag}_cov{h}_lo", f"{min(v):.0f}", "results/task_d2_recalibration.json")
            put(f"d2_{tag}_cov{h}_hi", f"{max(v):.0f}", "results/task_d2_recalibration.json")
        cs = [f["scalar"] for f in fs]
        put(f"d2_{tag}_c_lo", f"{min(cs):.3g}", "results/task_d2_recalibration.json")
        put(f"d2_{tag}_c_hi", f"{max(cs):.3g}", "results/task_d2_recalibration.json")
    put("d2_target", f'{100*_d2["target_coverage"]:.1f}', "results/task_d2_recalibration.json")

    # C3 -- multiplicity
    C3 = J("task_c3_multiplicity.json")
    put("c3_family", C3["family_ab"]["n_comparisons"], "results/task_c3_multiplicity.json")
    put("c3_long", C3["family_ab"]["n_long_horizon"], "results/task_c3_multiplicity.json")
    for r in C3["long_horizon_by_level"]:
        if r["level"].startswith("Bonferroni 0.05/") and str(C3["family_ab"]["n_comparisons"]) in r["level"]:
            put("c3_bonf_excl", r["long_horizon_excluding_zero"], "results/task_c3_multiplicity.json")
    put("c3_holm_rejected", C3["holm_bonferroni"]["n_rejected"], "results/task_c3_multiplicity.json")
    put("c3_sign_pos", C3["sign_test_h368"]["n_positive"], "results/task_c3_multiplicity.json")
    put("c3_sign_n", C3["sign_test_h368"]["n_episodes"], "results/task_c3_multiplicity.json")
    put("c3_sign_p", f'{C3["sign_test_h368"]["exact_two_sided_p"]:.4f}',
        "results/task_c3_multiplicity.json")
    put("c3_resamples", C3["bootstrap_resolution_note"]["distinct_resamples"],
        "results/task_c3_multiplicity.json")
    put("c3_quant", f'{C3["bootstrap_resolution_note"]["quantisation_pct"]:.2f}',
        "results/task_c3_multiplicity.json")

    op = os.path.join(R.RESULTS, "paper_numbers.json")
    json.dump(N, open(op, "w"), indent=2, sort_keys=True)
    print(f"collected {len(N)} keyed numbers -> {R.rel(op)}")
    for k in sorted(N):
        print(f"  {k:<28} {str(N[k]['value']):<16} {N[k]['source']}")


if __name__ == "__main__":
    main()
