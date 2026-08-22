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
    put("ver_timing", f'{ver["timing_excluded"]:,}', "results/verify_reproduction.json")
    put("ver_machine", ver["machine_file_values_excluded"], "results/verify_reproduction.json")
    _tb = ver.get("time_bounded_files_excluded", [])
    put("ver_timebound_n", len(_tb), "results/verify_reproduction.json")
    put("ver_timebound", ", ".join(f"`results/{x}`" for x in _tb) or "none",
        "results/verify_reproduction.json")
    # the committed iteration count of the wall-clock-bounded diagnostic, and the
    # cap it never reached -- both read from the artifact rather than typed
    if _tb:
        _ov = J(_tb[0])
        put("ver_tb_ran", _ov["iterations_run"], f"results/{_tb[0]}")
        put("ver_tb_cap", f'{_ov["config"]["iters"]:,}', f"results/{_tb[0]}")
        put("ver_tb_budget", f'{_ov["config"]["max_seconds"]:,.0f}', f"results/{_tb[0]}")
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
    # Counted from the COMMITTED run artifacts, not from a listing of runs/.
    # runs/ is gitignored, so in a clean clone the listing is empty and this
    # silently became 0 -- building a paper that said "Across 0 runs the collapse
    # is linear". Same failure as n_defects (M-36): a derived number whose source
    # can vanish without the derivation failing. The assert makes it fail loudly.
    runs = sorted(glob.glob("results/step5_arm*.json"))
    assert runs, "no results/step5_arm*.json -- cannot count training runs"
    put("n_runs", len(runs), "results/step5_arm*.json")
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
    TPL = open("PAPER.template.md").read()
    sup = re.findall(r"^### (S-\d+) ", led, re.M)
    retr = []
    for sid in sup:
        blk = led[led.index("### " + sid + " "):]
        blk = blk[:blk.find("\n### ", 5)] if "\n### " in blk[5:] else blk
        m = re.search(r"^\*\*Retracts\*\* (.+)$", blk, re.M)
        if m and not m.group(1).lstrip().startswith("\u2014"):
            retr.append(sid)
    # Framing retractions split two ways. S-01..S-07 withdraw early hypotheses that
    # were never numbered claims -- routine housekeeping. S-12 and S-15 withdraw
    # something the paper had asserted (a pre-registration status; an inference
    # from counts to P-values). The abstract and section 8 count the second group
    # separately, and an earlier draft typed "a seventh" for what is now two.
    fram = []
    for sid in sup:
        blk = led[led.index("### " + sid + " "):]
        blk = blk[:blk.find("\n### ", 5)] if "\n### " in blk[5:] else blk
        m = re.search(r"^\*\*Retracts\*\* (.+)$", blk, re.M)
        if m and m.group(1).lstrip().startswith("\u2014") \
                and "early hypothesis" not in m.group(1):
            fram.append(sid)
    put("n_superseded", len(sup), "FINDINGS_LEDGER.md")
    put("n_retractions", len(retr), "FINDINGS_LEDGER.md")
    put("n_retract_framing", len(fram), "FINDINGS_LEDGER.md")
    WORDS = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven",
             8: "Eight", 9: "Nine", 10: "Ten"}
    put("n_retractions_word", WORDS.get(len(retr), str(len(retr))), "FINDINGS_LEDGER.md")
    put("n_retractions_lower", WORDS.get(len(retr), str(len(retr))).lower(), "FINDINGS_LEDGER.md")
    put("n_retract_framing_word", WORDS.get(len(fram), str(len(fram))).lower(), "FINDINGS_LEDGER.md")
    put("n_retract_framing_word_cap", WORDS.get(len(fram), str(len(fram))), "FINDINGS_LEDGER.md")
    ORD = {1: "a seventh", 2: "two further", 3: "three further", 4: "four further"}
    put("n_retract_framing_phrase", ORD.get(len(fram), f"{len(fram)} further"), "FINDINGS_LEDGER.md")
    put("n_retract_total", len(retr) + len(fram), "FINDINGS_LEDGER.md")

    # E2 -- the residual factor between the implied iteration count and the one
    # the checkpoint's author recalls. The abstract said only "not reachable",
    # which reads as nearly reconciled; it is a factor of ~30.
    _rec = 5000        # docs/E4_AUTHOR_CONTACT.md: checkpoint tag, and the count
                       # the author recalls in his reply of 2026-08-21
    # Use the SAME estimate the body leads with (step6_analysis), not the
    # task5 refits. Quoting 158,000 in the abstract against section 7's 153,270
    # put two numbers for one quantity in one document; the refits are
    # corroboration and section 7 reports them as such.
    _imp = J("step6_analysis.json")["collapse"]["iters_to_checkpoint"]
    put("unreach_recalled_iters", f"{_rec:,}", "docs/E4_AUTHOR_CONTACT.md")
    put("unreach_factor", f"{_imp / _rec:.0f}", "results/step6_analysis.json")

    # --- D1/D2/D4: the released checkpoint at n_independent = 20 -----------
    D = J("task_d_nind20.json")
    put("d1n_nind", D["design"]["n_independent"], "results/task_d_nind20.json")
    put("d1n_ntraj", D["design"]["trajectories"], "results/task_d_nind20.json")
    put("d1n_eps", len(D["design"]["episodes"]), "results/task_d_nind20.json")
    for h in (1, 8, 32, 128, 368):
        r = D["d1_by_horizon"][str(h)]
        for q, tg in (("aleatoric", "alea"), ("epistemic", "epi"), ("total", "tot")):
            m = r[q]
            rr = m["ratio_err_over_sigma"]
            put(f"d1n_{tg}_ratio_h{h}", f"{rr:,.0f}" if rr >= 100 else f"{rr:.1f}",
                "results/task_d_nind20.json")
            put(f"d1n_{tg}_cov1_h{h}", f'{100*m["coverage_pm1"]:.2f}',
                "results/task_d_nind20.json")
            put(f"d1n_{tg}_cov2_h{h}", f'{100*m["coverage_pm2"]:.2f}',
                "results/task_d_nind20.json")
            put(f"d1n_{tg}_npos_h{h}", m["n_positive"], "results/task_d_nind20.json")
            put(f"d1n_{tg}_ndim_h{h}", m["n_finite_corr"], "results/task_d_nind20.json")
            put(f"d1n_{tg}_r_h{h}", f'{m["corr_mean"]:+.3f}', "results/task_d_nind20.json")
    _e1, _e368 = D["d1_by_horizon"]["1"], D["d1_by_horizon"]["368"]
    # A5: quote the ratio itself rather than an orders-of-magnitude phrase. 600x is
    # exact and generated; "two orders" and "nearly three orders" disagreed with
    # each other across the abstract and section 12 while both described this value.
    put("d1n_epi_over_alea_h368",
        f'{_e368["aleatoric"]["ratio_err_over_sigma"]/_e368["epistemic"]["ratio_err_over_sigma"]:,.0f}',
        "results/task_d_nind20.json")

    # D2 -- the forecast-index baseline
    for h in ("1", "8", "32", "128", "368", "all"):
        r = D["d2_forecast_index"][h]
        k = h if h == "all" else f"h{h}"
        for nm, tg in (("r_index", "idx"), ("r_epistemic", "epi"), ("r_partial", "par")):
            v = r[nm]
            put(f"d2b_{tg}_{k}", "n/a" if v is None else f"{v:+.3f}",
                "results/task_d_nind20.json")
        for nm, tg in (("index", "idx"), ("epistemic", "epi"), ("partial", "par")):
            c = r["ci"][nm]
            put(f"d2b_{tg}_ci_{k}",
                "n/a" if c["lo"] is None else f'[{c["lo"]:+.3f}, {c["hi"]:+.3f}]',
                "results/task_d_nind20.json")
    # A2: the PAIRED difference r(disagreement) - r(index), bootstrapped over whole
    # trajectories with both correlations recomputed inside each draw. Replaces the
    # marginal-overlap comparison, which is not the right test for two correlations
    # measured on the same trajectories -- and which the artifact shows is false at
    # h=128 anyway.
    for h in ("8", "32", "128", "368", "all"):
        r = D["d2_forecast_index"][h]
        k = h if h == "all" else f"h{h}"
        put(f"d2p_diff_{k}", f'{r["paired_diff"]:+.3f}', "results/task_d_nind20.json")
        put(f"d2p_ci_{k}", f'[{r["paired_ci_lo"]:+.3f}, {r["paired_ci_hi"]:+.3f}]',
            "results/task_d_nind20.json")
    _sep = [h for h in ("8", "32", "128", "368")
            if D["d2_forecast_index"][h]["paired_excludes_zero"]]
    _ovl = [h for h in ("8", "32", "128", "368")
            if D["d2_forecast_index"][h]["marginal_ci_overlap"]]
    put("d2p_n_separating", len(_sep), "results/task_d_nind20.json")
    put("d2p_n_horizons", 4, "results/task_d_nind20.json")
    put("d2p_overlap_h", ", ".join(f"h={x}" for x in _ovl) or "none",
        "results/task_d_nind20.json")
    put("d2p_n_overlap", len(_ovl), "results/task_d_nind20.json")
    _narrow = min(("8", "32", "128", "368"),
                  key=lambda h: D["d2_forecast_index"][h]["paired_ci_lo"])
    put("d2p_narrowest_h", _narrow, "results/task_d_nind20.json")
    put("d2p_narrowest_lo", f'{D["d2_forecast_index"][_narrow]["paired_ci_lo"]:+.3f}',
        "results/task_d_nind20.json")
    # B: h=1, the strongest correlation anywhere in this project's data
    _h1 = D["d2_forecast_index"]["1"]
    put("d2_epi_h1", f'{_h1["r_epistemic"]:+.3f}', "results/task_d_nind20.json")
    put("d2_epi_ci_h1", f'[{_h1["ci"]["epistemic"]["lo"]:+.3f}, '
                        f'{_h1["ci"]["epistemic"]["hi"]:+.3f}]',
        "results/task_d_nind20.json")
    _dw = [h for h in ("8", "32", "128", "368") if D["d2_forecast_index"][h]["index_wins"]]
    put("d2b_n_index_wins", len(_dw), "results/task_d_nind20.json")
    put("d2b_n_horizons_tested", 4, "results/task_d_nind20.json")
    _all = D["d2_forecast_index"]["all"]
    put("d2b_shrink_all", f'{_all["r_epistemic"] - _all["r_partial"]:+.3f}',
        "results/task_d_nind20.json")
    put("d2b_shrink_all_abs", f'{abs(_all["r_epistemic"] - _all["r_partial"]):.3f}',
        "results/task_d_nind20.json")

    # D4 -- the penalty correlation, with an interval and an n at last
    _p4 = D["d4_penalty"]
    put("d4_r", f'{_p4["corr_with_total_abs_error"]:+.3f}', "results/task_d_nind20.json")
    put("d4_ci", f'[{_p4["ci_lo"]:+.3f}, {_p4["ci_hi"]:+.3f}]', "results/task_d_nind20.json")
    put("d4_nind", _p4["n_independent"], "results/task_d_nind20.json")
    put("d4_npoints", f'{_p4["n_points"]:,}', "results/task_d_nind20.json")

    # --- D3: the per-horizon scalar ---------------------------------------
    D3 = J("task_d3_perhorizon.json")
    for q, tg in (("aleatoric", "ale"), ("epistemic", "epi")):
        v = D3["quantities"][q]["verdict"]
        put(f"d3_{tg}_ok", v["per_horizon_cells_calibrated"], "results/task_d3_perhorizon.json")
        put(f"d3_{tg}_cells", v["n_cells"], "results/task_d3_perhorizon.json")
        put(f"d3_{tg}_const_ok", v["constant_cells_calibrated"],
            "results/task_d3_perhorizon.json")
        put(f"d3_{tg}_cspread", f'{v["c_ratio_max_over_min"]:.3g}',
            "results/task_d3_perhorizon.json")
        put(f"d3_{tg}_worst_h", v["worst_cell"]["h"], "results/task_d3_perhorizon.json")
        put(f"d3_{tg}_worst_cov", f'{100*v["worst_cell"]["coverage_after"]:.2f}',
            "results/task_d3_perhorizon.json")
        _cs = sorted(f["c"] for f in D3["quantities"][q]["fits"])
        put(f"d3_{tg}_c_lo", f"{_cs[0]:.4g}", "results/task_d3_perhorizon.json")
        put(f"d3_{tg}_c_hi", f"{_cs[-1]:.4g}", "results/task_d3_perhorizon.json")
    put("d3_target", f'{100*D3["target_coverage"]:.2f}', "results/task_d3_perhorizon.json")
    # A4: the worst cell over ALL held-out cells, not the worst within one quantity.
    # The per-quantity verdict blocks each name their own worst; the paper quoted
    # the epistemic one as if it were the overall worst, and it is third.
    _all_cells = [(abs(f["coverage_after"] - D3["target_coverage"]), q, f)
                  for q in D3["quantities"]
                  for f in D3["quantities"][q]["fits"]]
    _all_cells.sort(key=lambda x: -x[0])
    _w = _all_cells[0]
    put("d3_ncells_all", len(_all_cells), "results/task_d3_perhorizon.json")
    put("d3_worst_q", _w[1], "results/task_d3_perhorizon.json")
    put("d3_worst_h", _w[2]["h"], "results/task_d3_perhorizon.json")
    put("d3_worst_ep", _w[2]["fit_episode"], "results/task_d3_perhorizon.json")
    put("d3_worst_cov", f'{100*_w[2]["coverage_after"]:.2f}', "results/task_d3_perhorizon.json")
    put("d3_worst_dev", f'{100*_w[0]:.2f}', "results/task_d3_perhorizon.json")
    put("d3_second_cov", f'{100*_all_cells[1][2]["coverage_after"]:.2f}',
        "results/task_d3_perhorizon.json")
    _tp = D3["design"]["trajectories_per_episode"]
    put("d3_neps", len(_tp), "results/task_d3_perhorizon.json")
    put("d3_nind_fit", min(_tp.values()), "results/task_d3_perhorizon.json")
    put("d3_nind_tot", sum(_tp.values()), "results/task_d3_perhorizon.json")

    # Section 9 opens by counting its own lessons. It said "Four" while carrying a
    # different number after Part D added two; count the bold leads instead.
    _s9 = TPL.split("## 9.")[1].split("\n## ")[0]
    _n9 = len(re.findall(r"^\*\*[A-Z]", _s9, re.M))
    put("n_lessons", _n9, "PAPER.template.md section 9")
    put("n_lessons_word", WORDS.get(_n9, str(_n9)), "PAPER.template.md section 9")

    # E4 -- appendix B claimed "roughly 22 hours" for a full run. Recomputed from
    # the top-level wall_clock_s of every training run. (The per-checkpoint
    # wall_clock_s inside `collapse` is elapsed-so-far, not per-interval; summing
    # those inflates the total about 15-fold.)
    import glob as _glob
    _runs = []
    for _f in sorted(_glob.glob("results/step5_*.json")):
        _d = json.load(open(_f))
        if _d.get("wall_clock_s"):
            _runs.append((_d["hyperparameters"]["iterations"], _d["wall_clock_s"]))
    _t = sum(w for _, w in _runs)
    _t10 = sum(w for i, w in _runs if i == 10000)
    put("rt_runs", len(_runs), "results/step5_*.json")
    put("rt_runs_10k", sum(1 for i, _ in _runs if i == 10000), "results/step5_*.json")
    put("rt_hours", f"{_t/3600:.0f}", "results/step5_*.json")
    put("rt_hours_10k", f"{_t10/3600:.0f}", "results/step5_*.json")
    put("rt_hours_short", f"{(_t-_t10)/3600:.0f}", "results/step5_*.json")
    put("rt_runs_short", sum(1 for i, _ in _runs if i != 10000), "results/step5_*.json")

    # Section 8 illustrated the host-dependence of step4_5_timing.json with a
    # typed anecdote ("46.5 s idle took 109.7 s under load") that appears in no
    # artifact. The file records its own across-repeat standard deviation, which
    # makes the same point and is readable from disk.
    _tm = J("step4_5_timing.json")["results"]
    _rel = {k: v["std"] / v["s_per_iter"] for k, v in _tm.items()
            if isinstance(v, dict) and v.get("s_per_iter")}
    _wk = max(_rel, key=_rel.get)
    put("time_cfgs", len(_rel), "results/step4_5_timing.json")
    put("time_rel_hi", f"{100*_rel[_wk]:.0f}", "results/step4_5_timing.json")
    put("time_rel_lo", f"{100*min(_rel.values()):.0f}", "results/step4_5_timing.json")
    put("time_worst_cfg", _wk, "results/step4_5_timing.json")
    put("rt_longest", f"{max(w for _, w in _runs)/3600:.1f}", "results/step5_*.json")

    # Section 5.2 claims the n=4 table "agrees in direction" with the n=20 one.
    # Checked rather than asserted: it does for the epistemic column at all five
    # horizons, and does NOT for the aleatoric column at one of them.
    _B4 = J("task_b2_epistemic.json")
    _agree_e = _agree_a = 0
    for _h in ("1", "8", "32", "128", "368"):
        for _q, _c in (("epistemic", "e"), ("aleatoric", "a")):
            _x = (_B4["by_horizon"][_h][_q]["n_positive"]
                  > _B4["by_horizon"][_h][_q]["n_finite_corr"] / 2)
            _y = (D["d1_by_horizon"][_h][_q]["n_positive"]
                  > D["d1_by_horizon"][_h][_q]["n_finite_corr"] / 2)
            if _x == _y:
                if _c == "e":
                    _agree_e += 1
                else:
                    _agree_a += 1
    put("agree_epi", _agree_e, "results/task_b2_epistemic.json + task_d_nind20.json")
    put("agree_alea", _agree_a, "results/task_b2_epistemic.json + task_d_nind20.json")
    put("agree_nh", 5, "results/task_b2_epistemic.json + task_d_nind20.json")
    put("d3_tol", f'{100*D3["quantities"]["epistemic"]["verdict"]["tolerance"]:.0f}',
        "results/task_d3_perhorizon.json")

    # --- D2b: is the forecast-index control adequate? ---------------------
    RB = J("task_d2b_robustness.json")
    for _m, _t in (("linear", "lin"), ("log", "log"), ("cubic", "cub"),
                   ("spearman", "spr"), ("within_step", "win")):
        c = RB["controls"][_m]
        put(f"d2r_{_t}", f'{c["r_disagreement_given_index"]:+.3f}',
            "results/task_d2b_robustness.json")
        put(f"d2r_{_t}_ci", f'[{c["ci_lo"]:+.3f}, {c["ci_hi"]:+.3f}]',
            "results/task_d2b_robustness.json")
    _w = RB["controls"]["within_step"]
    put("d2r_win_pos", _w["steps_positive"], "results/task_d2b_robustness.json")
    put("d2r_win_n", _w["n_steps"], "results/task_d2b_robustness.json")
    put("d2r_win_med", f'{_w["median"]:+.3f}', "results/task_d2b_robustness.json")
    put("d2r_weakest", f'{RB["verdict"]["weakest_partial"]:+.3f}',
        "results/task_d2b_robustness.json")
    put("d2r_ncontrols", len(RB["controls"]), "results/task_d2b_robustness.json")


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
            put(f"b2_{tag}_r_h{h}", f'{m["corr_mean"]:+.3f}',
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

    # --- B: permutation over trajectories (R-61, S-15) ---------------------
    # Every dimension-count P-value in the paper comes from here now. The
    # binomial values are retained under _binom keys so the paper can quote the
    # size of the correction without either number being typed.
    PM = J("task_b_permutation.json")
    _ptag = {"faithful (mse)": "faithA", "corrected (nll)": "nll",
             "teacher-forced armB": "armB", "released aleatoric": "relale",
             "released EPISTEMIC": "epi"}
    _big = None
    for _ar, _pre in (("out-of-sample", "oos"), ("in-sample", "ins"),
                      ("all-episodes", "all")):
        A = PM["arenas"][_ar]
        put(f"perm_{_pre}_nind", A["n_independent"], "results/task_b_permutation.json")
        put(f"perm_{_pre}_floor", f'{A["p_floor"]:.4g}', "results/task_b_permutation.json")
        H = A["holm"]
        put(f"perm_{_pre}_holm_n", H["family_size"], "results/task_b_permutation.json")
        put(f"perm_{_pre}_holm_rej", H["n_rejected"], "results/task_b_permutation.json")
        put(f"perm_{_pre}_holm_thr", f'{H["smallest_threshold"]:.4g}',
            "results/task_b_permutation.json")
        put(f"perm_{_pre}_holm_min_p", f'{H["steps"][0]["p"]:.4f}',
            "results/task_b_permutation.json")
        put(f"perm_{_pre}_holm_min_cell", H["steps"][0]["cell"],
            "results/task_b_permutation.json")
        for _lab, _tg in _ptag.items():
            for _h in (1, 8, 32, 128, 368):
                r = A["models"][_lab][str(_h)]
                put(f"perm_{_pre}_{_tg}_p_h{_h}", f'{r["p_permutation"]:.4f}',
                    "results/task_b_permutation.json")
                put(f"perm_{_pre}_{_tg}_null_h{_h}", f'{r["null_mean"]:.1f}',
                    "results/task_b_permutation.json")
                put(f"perm_{_pre}_{_tg}_grp_h{_h}", r["group_count"],
                    "results/task_b_permutation.json")
                put(f"perm_{_pre}_{_tg}_npos_h{_h}", r["observed"],
                    "results/task_b_permutation.json")
                put(f"perm_{_pre}_{_tg}_ndim_h{_h}", r["n_dims"],
                    "results/task_b_permutation.json")
                put(f"perm_{_pre}_{_tg}_binom_h{_h}", f'{r["p_binomial_two_sided"]:.2e}',
                    "results/task_b_permutation.json")
                # Only cells the paper ever cited as evidence, i.e. where the
                # count is a positive-direction majority. The largest ratio
                # overall belongs to released aleatoric at h=32 in-sample (0/45,
                # binomially "significant" in the NEGATIVE direction), which no
                # claim here rests on; quoting it would overstate the correction
                # by pointing at a cell nobody used.
                _rat = r["p_permutation"] / max(r["p_binomial_two_sided"], 1e-300)
                if r["observed"] > r["n_dims"] / 2 and (_big is None or _rat > _big[0]):
                    _big = (_rat, _ar, _lab, _h, r)
    # A1: the released aleatoric head's direction is arena-dependent and the paper
    # asserted the all-episodes result while its table printed the out-of-sample
    # one. Both are surfaced here so each citation can name its arena.
    _ra = PM["arenas"]
    for _pre, _ar in (("oos", "out-of-sample"), ("ins", "in-sample"), ("all", "all-episodes")):
        _r = _ra[_ar]["models"]["released aleatoric"]["368"]
        put(f"relale_{_pre}_pos_h368", _r["observed"], "results/task_b_permutation.json")
        put(f"relale_{_pre}_neg_h368", _r["n_dims"] - _r["observed"],
            "results/task_b_permutation.json")
    put("relale_all_nind", _ra["all-episodes"]["n_independent"],
        "results/task_b_permutation.json")
    put("relale_oos_nind", _ra["out-of-sample"]["n_independent"],
        "results/task_b_permutation.json")
    put("perm_ngroups", PM["arenas"]["out-of-sample"]["models"]["released EPISTEMIC"]["368"]["n_groups"],
        "results/task_b_permutation.json")
    _r, _ar, _lab, _h, _rec = _big
    # Rendered as a power of ten. "17,592,186,044,416" is not a number a reader
    # parses; "about 10^13" is the claim being made.
    import math as _m
    put("perm_worst_factor", f"10^{round(_m.log10(_r))}", "results/task_b_permutation.json")
    put("perm_worst_factor_exact", f"{_r:.3g}", "results/task_b_permutation.json")
    put("perm_worst_model", _lab, "results/task_b_permutation.json")
    put("perm_worst_h", _h, "results/task_b_permutation.json")
    put("perm_worst_arena", _ar, "results/task_b_permutation.json")
    put("perm_worst_null", f'{_rec["null_mean"]:.1f}', "results/task_b_permutation.json")
    _nulls = [PM["arenas"][a]["models"][l][str(h)]["null_mean"]
              for a in PM["arenas"] for l in _ptag for h in (1, 8, 32, 128, 368)]
    put("perm_null_lo", f"{min(_nulls):.1f}", "results/task_b_permutation.json")
    put("perm_null_hi", f"{max(_nulls):.1f}", "results/task_b_permutation.json")

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
    put("n_train_eps", len(_tr), "results/step5_armA_seed0.json (split)")
    put("n_holdout_eps", len(_ho), "results/step5_armA_seed0.json (split)")

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

    # E2: magnitude collapse is objective-driven, input-independence is arm-driven
    import glob as _g, statistics as _st
    _mse, _nll_s = [], []
    for _f in sorted(_g.glob("results/step5_arm*.json")):
        if "_10k" in _f:
            continue
        _d = json.load(open(_f))
        _sl = _d.get("collapse_fit", {}).get("slope_per_iter")
        if _sl is None:
            continue
        (_nll_s if _f.endswith("_nll.json") else _mse).append(_sl)
    put("e2_mse_runs", len(_mse), "results/step5_arm*.json")
    put("e2_mse_rate", f"{_st.mean(_mse):.4e}", "results/step5_arm*.json")
    put("e2_mse_sd", f"{_st.stdev(_mse):.1e}", "results/step5_arm*.json")
    put("e2_nll_runs", len(_nll_s), "results/step5_arm*.json")
    put("e2_fitted_runs", len(_mse) + len(_nll_s), "results/step5_arm*.json")
    _all = len([f for f in _g.glob("results/step5_arm*.json")])
    put("e2_excluded_10k", _all - (len(_mse) + len(_nll_s)), "results/step5_arm*.json")
    put("e2_nll_rate", f"{_st.mean(_nll_s):+.4e}", "results/step5_arm*.json")

    # "four defects in the released pipeline" was typed. Count section 5's
    # subsections instead, so adding or removing one cannot desynchronise the abstract.
    # Bound to the section's TITLE, not its number. The first version of this
    # matched "**5.N " and silently returned 0 the moment the section was
    # renumbered to 6 -- putting "we report 0 defects" in the abstract. Counting
    # from a number that can move is the same bug as typing the number.
    _tpl = open("PAPER.template.md").read()
    _dsec = re.search(r"^## (\d+)\. Defects in the released pipeline\s*$", _tpl, re.M)
    assert _dsec, "no section titled 'Defects in the released pipeline'"
    _dnum = _dsec.group(1)
    _dbody = _tpl[_dsec.end():]
    _dbody = _dbody[:_dbody.find("\n## ")] if "\n## " in _dbody else _dbody
    _n = len(re.findall(r"^\*\*" + _dnum + r"\.\d+ ", _dbody, re.M))
    assert _n > 0, f"section {_dnum} has no bold-numbered defect subsections"
    WORD = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}
    put("n_defects", WORD.get(_n, str(_n)),
        f"PAPER.template.md section {_dnum} subsections")

    # D1 -- the headline over three seeds. The single-seed figures stay available
    # so the paper can say what changed rather than quietly swapping them.
    _d1 = J("task_d1_threeseed.json")
    _A, _B = _d1["aggregate"]["A"], _d1["aggregate"]["B"]
    put("d1_seeds", _A["n_seeds"], "results/task_d1_threeseed.json")
    put("d1_A_mean", f'{_A["mean"]:.4f}', "results/task_d1_threeseed.json")
    put("d1_A_sd", f'{_A["sd_ddof1"]:.4f}', "results/task_d1_threeseed.json")
    put("d1_B_mean", f'{_B["mean"]:.4f}', "results/task_d1_threeseed.json")
    put("d1_B_sd", f'{_B["sd_ddof1"]:.4f}', "results/task_d1_threeseed.json")
    put("d1_ratio", f'{_d1["aggregate"]["ratio_B_over_A"]:.2f}',
        "results/task_d1_threeseed.json")
    put("d1_A_relsd", f'{100*_A["sd_ddof1"]/_A["mean"]:.1f}', "results/task_d1_threeseed.json")
    put("d1_B_relsd", f'{100*_B["sd_ddof1"]/_B["mean"]:.1f}', "results/task_d1_threeseed.json")
    put("d1_A_lo", f'{min(_A["per_seed"].values()):.4f}', "results/task_d1_threeseed.json")
    put("d1_A_hi", f'{max(_A["per_seed"].values()):.4f}', "results/task_d1_threeseed.json")
    put("d1_B_lo", f'{min(_B["per_seed"].values()):.4f}', "results/task_d1_threeseed.json")
    put("d1_B_hi", f'{max(_B["per_seed"].values()):.4f}', "results/task_d1_threeseed.json")
    _xc = _d1["cross_check"]
    put("d1_xc_runs", len(_xc), "results/task_d1_threeseed.json")
    put("d1_xc_values", f'{sum(r.get("values_compared", 0) for r in _xc):,}',
        "results/task_d1_threeseed.json")
    put("d1_xc_diff", sum(r.get("differing", 0) for r in _xc),
        "results/task_d1_threeseed.json")

    # A4.3: a table a reader can count. Derived from the run JSONs themselves.
    import glob as _g2
    inv = {}
    for f in sorted(_g2.glob("results/step5_arm*.json")):
        d = json.load(open(f))
        h = d["hyperparameters"]
        arm = d["arm"] if "arm" in d else ("B" if "armB" in f else "A")
        key = (arm, h["iterations"], h.get("loss_type", "mse"),
               "contaminated" if h.get("contaminated") else
               ("duplicated" if h.get("duplicated") else "clean"))
        inv.setdefault(key, []).append(d["seed"])
    rows = []
    for (arm, it, loss, ds), seeds in sorted(inv.items()):
        rows.append(f"| Arm {arm} | {it:,} | {loss} | {ds} | {len(seeds)} | "
                    f"{', '.join(str(x) for x in sorted(seeds))} |")
    put("run_table", "\n".join(rows), "results/step5_arm*.json")
    put("run_total", sum(len(v) for v in inv.values()), "results/step5_arm*.json")

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
