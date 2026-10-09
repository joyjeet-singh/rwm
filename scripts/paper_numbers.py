"""Collect every number the paper quotes, from the artifacts, into one keyed file.

The paper is written as PAPER.template.md with {{key}} placeholders. build_paper.py
substitutes from results/paper_numbers.json and refuses to emit a paper if any
placeholder is unresolved or any key here is unused. No number in the paper is typed.
"""
import glob
import json
import numpy as np
import os
import re
import subprocess
import sys
from math import comb

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402


def J(n):
    return json.load(open(os.path.join(R.RESULTS, n)))


# Number words, at module scope because keys derived near the top of main() need
# them too. This lived inside main() below the ledger block and the first caller
# above it raised UnboundLocalError.
WORDS = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven",
         8: "Eight", 9: "Nine", 10: "Ten", 11: "Eleven", 12: "Twelve", 13: "Thirteen"}


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
    # B6/B7. The window LENGTH -- §5.1 said 33 where the config says 32 history +
    # 8 forecast = 40, which is the only length consistent with 10,000 - 39 =
    # 9,961 -- and the ROW STRUCTURE that makes the counts above derivable. §3
    # said "ten concatenated 20-second episodes"; taken literally that is ten
    # segments of 1,000, which gives 351 crossing and 9,610 usable and makes the
    # paper look off by one.
    put("win_len", w["window"], "results/step0_regimes.json")
    put("win_hist", w["history_horizon"], "results/step0_regimes.json")
    put("win_fore", w["forecast_horizon"], "results/step0_regimes.json")
    put("ep0_rows", f'{w["episode_lengths"][0]:,}', "results/step0_regimes.json")
    put("ep_rest_rows", f'{w["episode_lengths"][1]:,}', "results/step0_regimes.json")
    put("n_ep_rest", len(w["episode_lengths"]) - 1, "results/step0_regimes.json")
    put("n_ep_rest_word", WORDS.get(len(w["episode_lengths"]) - 1,
                                    str(len(w["episode_lengths"]) - 1)).lower(),
        "results/step0_regimes.json")
    put("orphan_rows", w["orphan_rows"], "results/step0_regimes.json")
    put("row_structure", w["row_structure"], "results/step0_regimes.json")
    put("reset_rows_first", f'{w["reset_rows"][0]:,}', "results/step0_regimes.json")
    put("reset_rows_second", f'{w["reset_rows"][1]:,}', "results/step0_regimes.json")
    put("reset_rows_last", f'{w["reset_rows"][-1]:,}', "results/step0_regimes.json")

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
        # A1 -- every ratio and coverage in the 6.2 table now carries a 95%
        # cluster-bootstrap interval over whole trajectories. The paper declares
        # that standard for itself in section 3 and was not applying it here.
        _rc = m["ratio_err_over_sigma_ci"]
        _f = (lambda v: f"{v:,.0f}") if rr >= 100 else (lambda v: f"{v:.1f}")
        put(f"cal_{tag}_ratio_ci", f"{_f(_rc[0])}, {_f(_rc[1])}",
            "results/task1_calibration.json")
        put(f"cal_{tag}_cov100", round(100 * m["coverage"]["100"]["pm1"], 2),
            "results/task1_calibration.json")
        for _h in ("1", "100", "368"):
            _cc = m["coverage"][_h]["pm1_ci"]
            put(f"cal_{tag}_cov{_h}_ci", f"{100*_cc[0]:.2f}, {100*_cc[1]:.2f}",
                "results/task1_calibration.json")
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
    # S5: Figure 2's caption said error "grows by an order of magnitude" over steps 1-8; it
    # grows by the range below across the four models, read rather than typed.
    _eg = [round(sig[k]["err_growth_1_to_8"], 2) for k in slab]
    put("err_growth_lo", min(_eg), "results/task2_sigma_profile.json")
    put("err_growth_hi", max(_eg), "results/task2_sigma_profile.json")

    # --- the A/B claim -----------------------------------------------------
    put("t5_seeds", t5["provenance"]["n_seeds"], "results/task5_analysis.json")
    g = t5["gaps"]["out-of-sample|10000|h368"]
    put("m23_A", f'{g["A"]:.4f}', "results/task5_analysis.json")
    put("m23_B", f'{g["B"]:.4f}', "results/task5_analysis.json")
    put("m23_gap", round(g["gap"], 4), "results/task5_analysis.json")
    put("m23_ratio", f'{g["B"] / g["A"]:.2f}', "results/task5_analysis.json")
    # Round 2, T3 (E4): what rule M-23 actually ran on -- seed 1 of each arm, named as such.
    put("m23_A_s1", f'{g["A"]:.4f}', "results/task5_analysis.json")
    put("m23_B_s1", f'{g["B"]:.4f}', "results/task5_analysis.json")
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
    # Pre-submission S3, items 1-2. A sentence or caption that names a checkpoint or a
    # seed count reads it from the artifact that holds it, never types it. M-23's own
    # analysis ran on one seed (task5_analysis.json provenance); every run artifact
    # records its iteration count, and the two families are asserted uniform.
    assert t5["provenance"]["n_seeds"] == 1 and len(t5["provenance"]["seeds"]) == 1
    put("m23_seed", t5["provenance"]["seeds"][0], "results/task5_analysis.json")
    # Round 2, T3 (E4): the seeds trained after M-23's verdict, and when (R-60's commit).
    _d1seeds = sorted(J("task_d1_threeseed.json")["aggregate"]["A"]["per_seed"], key=int)
    _other = [s for s in _d1seeds if int(s) != int(t5["provenance"]["seeds"][0])]
    put("m23_other_seeds", " and ".join(_other), "results/task_d1_threeseed.json + task5_analysis.json")
    _r60 = subprocess.run(["git", "log", "--format=%cs", "-S", "### R-60 \u2014", "--", "FINDINGS_LEDGER.md"],
                          capture_output=True, text=True).stdout.split()
    assert _r60, "no commit introduces ledger R-60"
    put("r60_date", _r60[-1], "git log -S '### R-60' FINDINGS_LEDGER.md (the commit that entered R-60)")
    _iters = {}
    for _f in sorted(glob.glob("results/step5_arm*.json")):
        _iters.setdefault("long" if _f.endswith("_10k.json") else "main", set()).add(
            J(os.path.basename(_f))["hyperparameters"]["iterations"])
    assert all(len(v) == 1 for v in _iters.values()), _iters
    put("iters_main", f"{next(iter(_iters['main'])):,}",
        "results/step5_arm*.json (every run but the _10k runs)")
    put("iters_long", f"{next(iter(_iters['long'])):,}", "results/step5_arm*_10k.json")
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
    # Figure 6's caption claimed every interval narrows; one cell's cluster-to-naive
    # width ratio is below 1. bu_n_narrowed counts the cells that did narrow, by the
    # same rule the figure's own title uses.
    put("bu_n_narrowed", sum(1 for k, v in bu.items() if k != "_summary"
                             and v["width_ratio_cluster_over_naive"] > 1),
        "results/review_bootstrap_unit.json")
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
    # S3 item 1: the checkpoints those h = 8 cells were computed at, from their own keys
    # ("out-of-sample|<length>|<checkpoint>|h8"), so the prose can say which they are.
    _bu_ck = sorted({int(k.split("|")[2]) for k in oos if k.endswith("|h8")})
    put("bu_ckpts", " and ".join(f"{c:,}" for c in _bu_ck), "results/review_bootstrap_unit.json")
    put("bu_changes", bu["_summary"]["n_verdict_changes"], "results/review_bootstrap_unit.json")

    # --- verification ------------------------------------------------------
    put("ver_files", len(ver["regenerated_files"]), "results/verify_reproduction.json")
    put("ver_values", f"{ver['values_compared']:,}", "results/verify_reproduction.json")
    put("ver_identical", f"{ver['bitwise_identical']:,}", "results/verify_reproduction.json")
    put("ver_pct", f"{100*ver['bitwise_identical']/ver['values_compared']:.2f}",
        "results/verify_reproduction.json")
    put("ver_differing", ver["differing"], "results/verify_reproduction.json")
    put("ver_keys_lost", ver["keys_lost"], "results/verify_reproduction.json")
    # The three outcome classes account for values_compared exactly, so the paper can
    # print them as a partition rather than as five numbers a reader must trust. The
    # near-identical class is the one that was missing: a bitwise-only recount lands on
    # 205 differing because it folds these 27 in, which is what made the figures look
    # as though they did not add up.
    put("ver_close", ver["identical_to_1e-9"], "results/verify_reproduction.json")
    # The size of the claim. A clean clone already contains every committed artifact, so
    # the comparison covers only what the run rewrites. Stating the fraction is cheaper
    # than having a reviewer compute it and conclude we hid it.
    _all = ver["values_compared"] + ver["copied_file_values"]
    put("ver_copied", f"{ver['copied_file_values']:,}", "results/verify_reproduction.json")
    put("ver_all", f"{_all:,}", "results/verify_reproduction.json")
    put("ver_claim_pct", f"{100*ver['values_compared']/_all:.2f}",
        "results/verify_reproduction.json")
    put("ver_overstate", f"{_all/ver['values_compared']:.0f}", "results/verify_reproduction.json")
    put("ver_keys_lost_files", len(ver["keys_lost_files"]),
        "results/verify_reproduction.json")
    # Round 2, T8: the README named only the file that records this count, which read as
    # naming the file that lost the value. Name both, the lost keys from the artifact's
    # per-file record, and check that they account for the count.
    _lost = [(f, ver["per_file"][f]["keys_lost_paths"]) for f in ver["keys_lost_files"]]
    assert sum(len(ps) for _, ps in _lost) == ver["keys_lost"], _lost
    put("ver_keys_lost_noun", "value is" if ver["keys_lost"] == 1 else "values are",
        "results/verify_reproduction.json")
    put("ver_keys_lost_where", "; ".join(
        f"`results/{f}` (key{'s' if len(ps) > 1 else ''} " + ", ".join(f"`{p}`" for p in ps) + ")"
        for f, ps in _lost), "results/verify_reproduction.json")
    put("ver_timing", f'{ver["timing_excluded"]:,}', "results/verify_reproduction.json")
    put("ver_machine", ver["machine_file_values_excluded"], "results/verify_reproduction.json")
    _tb = ver.get("time_bounded_files_excluded", [])
    put("ver_timebound_n", len(_tb), "results/verify_reproduction.json")
    put("ver_timebound", ", ".join(f"`results/{x}`" for x in _tb) or "none",
        "results/verify_reproduction.json")
    put("ver_selfref", len(ver.get("self_referential_keys_excluded", [])),
        "results/verify_reproduction.json")
    put("ver_hostkeys", len(ver.get("host_sourced_keys_excluded", [])),
        "results/verify_reproduction.json")
    # the committed iteration count of the wall-clock-bounded diagnostic, and the
    # cap it never reached -- both read from the artifact rather than typed
    if _tb:
        _ov = J(_tb[0])
        put("ver_tb_ran", _ov["iterations_run"], f"results/{_tb[0]}")
        put("ver_tb_cap", f'{_ov["config"]["iters"]:,}', f"results/{_tb[0]}")
        put("ver_tb_budget", f'{_ov["config"]["max_seconds"]:,.0f}', f"results/{_tb[0]}")

    # Section 8's partition of the differing values, by cause, read from the per-file
    # record in verify_reproduction.json rather than asserted. The rule for what counts
    # as scientific classifies each VALUE, not the file holding it: a differing value
    # carries a scientific result only if it is itself a measurement, a statistic or
    # the verdict of a test. The table below names every kind of value placed outside
    # that class, and why. Anything it does not match is counted as scientific, so an
    # unanticipated difference raises the count rather than disappearing.
    _INDEX, _DILUTION = "restatement_index.json", "e5_sigma_dilution.json"
    _BOOK = [
        (_INDEX, r"\.restatements\[\d+\]\.locations\[\d+\]\.line",
         "line numbers in this document"),
        (_INDEX, r"\.restatements\[\d+\]\.(n_locations|n_substituted|n_typed)",
         "counts of where each repeated numeral appears in this document"),
        (_INDEX, r"\.(n_substituted|n_typed|n_restatements|n_same_quantity_candidates"
                 r"|n_lower_signal)",
         "the index's totals over this document"),
        ("task_c1_claims_audit.json", r"\.claims\[\d+\]\.n_keys",
         "how many substituted numbers each audited sentence of this document holds"),
        ("task_c1_claims_audit.json", r"\.(n_claims|by_verdict\.[A-Z_]+)",
         "how many of this document's sentences the claims audit found, by review status"),
        ("anon_bundle.json", r"\.(n_files_staged|cited_files_checked)",
         "the anonymised bundle's file count `{key}`"),
        # Named when stage 28 began passing again: a clone reached from a path that
        # carries no account name builds the archives, so the two bundle records moved
        # from the carried-in set into the compared one. Every value here is a property
        # of an archive -- how many files it holds, how many bytes it occupies, how many
        # of them the scrubber rewrote, how many commits its anonymised log carries --
        # and none is a measurement, a statistic or the verdict of a test.
        ("anon_bundle.json", r"\.n_files_content_scrubbed",
         "how many of the anonymised bundle's files the scrubber rewrote"),
        ("supplementary_manifest.json", r"\.(files|bytes|uncompressed)",
         "the supplementary archive's own size and file count `{key}`"),
        ("supplementary_manifest.json", r"\.commits_in_log",
         "how many commits the archive's anonymised git log carries"),
        ("appendix_g_rules.json", r"\.rules\[(\d+)\]\.lead_hours",
         "the lead time of rule {rule}, a gap between two git commit timestamps"),
        ("paper_numbers.json", r"\.(audit_n_hits|audit_n_frozen|audit_n_retired)\.value",
         "the build's input-audit count `{key}`"),
        ("pdf_channels.json", r"\.scanned\.text",
         "the amount of PDF text the anonymity scan read"),
        ("pdf_channels.json", r"\.pages",
         "the page count of this document's PDF"),
        ("t5_anon_transcript.json", r"\.n_quotations_used_in_paper",
         "how many correspondence quotations this document uses"),
    ]
    _AGR = J("appendix_g_rules.json")["rules"]
    _pf = {f: v for f, v in ver["per_file"].items() if v["regenerated"]}
    assert sum(v["differing"] for v in _pf.values()) == ver["differing"], \
        "per-file record does not account for every differing value"
    _named, _sci = {}, 0
    for _f in sorted(_pf):
        for _k in _pf[_f]["differing_keys"]:
            for _bf, _rx, _what in _BOOK:
                _m = re.fullmatch(_rx, _k) if _bf == _f else None
                if _m:
                    _what = _what.format(rule=f'`{_AGR[int(_m.group(1))]["id"]}`') \
                        if "{rule}" in _what else _what.format(key=_m.group(1)) \
                        if "{key}" in _what else _what
                    _named[(_f, _what)] = _named.get((_f, _what), 0) + 1
                    break
            else:
                _sci += 1
    _vsrc = "results/verify_reproduction.json"
    _pi = _pf.get(_INDEX, {}).get("differing", 0)
    _pd = _pf.get(_DILUTION, {}).get("differing", 0)
    put("ver_part_index", _pi, _vsrc)
    put("ver_part_dilution", _pd, _vsrc)
    put("ver_part_else", ver["differing"] - _pi - _pd, _vsrc)
    put("ver_part_sci", _sci, _vsrc)
    put("ver_book_named", "; ".join(
        f"{n} in `results/{f}` ({w})"
        for (f, w), n in sorted(_named.items(), key=lambda x: (-x[1], x[0]))), _vsrc)
    _byf = sorted(((v["differing"], f) for f, v in _pf.items() if v["differing"]),
                  key=lambda x: (-x[0], x[1]))
    put("ver_diff_nfiles", len(_byf), _vsrc)
    put("ver_diff_by_file", ", ".join(f"`results/{f}` ({n})" for n, f in _byf), _vsrc)

    # Part C: the count of COMPARATIVE claims verified, reported in section 8
    # beside the numeral count. A build that verifies its own interpretive claims
    # is a stronger reproducibility statement than one that verifies only numerals.
    CC = J("comparative_claims.json")
    put("cc_n", CC["n_claims"], "results/comparative_claims.json")
    put("cc_pass", CC["n_pass"], "results/comparative_claims.json")
    # Assert, do not default. check_comparative_claims.py writes the self_test
    # block only when run with --self-test; running it without leaves the block
    # absent, and .get(..., 0) turned that into "0 of 0 corruptions caught" in the
    # paper -- a sentence claiming the self-test found nothing, which is exactly
    # what it would say if the self-test had silently stopped running. Same shape
    # as M-36's "0 defects". reproduce.sh stage 28a always passes --self-test.
    assert "self_test" in CC, (
        "results/comparative_claims.json has no self_test block: re-run "
        "scripts/check_comparative_claims.py --self-test")
    _st = CC["self_test"]
    assert _st["n"] > 0, "self-test ran zero corruptions"
    put("cc_st_n", _st["n"], "results/comparative_claims.json")
    put("cc_st_caught", _st["caught"], "results/comparative_claims.json")
    put("cc_kinds", len({c["kind"] for c in CC["claims"]}), "results/comparative_claims.json")
    # B8. What the abstract is now allowed to claim about its own numbers, from
    # the audit that enforces it rather than from a sentence that asserted it.
    TN = J("typed_numerals.json")
    assert TN["n_unclassified"] == 0, (
        f"{TN['n_unclassified']} typed numerals are unclassified; the paper may not "
        "claim its numerals are all addresses or declared constants until they are")
    put("tn_typed", TN["n_typed"], "results/typed_numerals.json")

    # D3. Appendix F, generated from the ledger. Ledger identifiers ran through the
    # body with no table behind them, so an identifier was either decoration or an
    # instruction to open a 330 KB file. With the table, the identifier can stay
    # only where a pre-registered verdict is reported and come out elsewhere.
    # E4. All seven loss terms and what each does to sigma, MEASURED. §6.3's
    # derivation addresses two of them; its completeness rests on the other five
    # being inert with respect to sigma, and that was asserted rather than shown.
    E4 = J("e4_sigma_gradients.json")
    put("e4_n_terms", E4["n_terms"], "results/e4_sigma_gradients.json")
    put("e4_n_live", E4["n_live"], "results/e4_sigma_gradients.json")
    put("e4_n_touch", E4["n_touching_sigma"], "results/e4_sigma_gradients.json")
    put("e4_n_inert", E4["n_terms"] - E4["n_touching_sigma"],
        "results/e4_sigma_gradients.json")
    put("e4_touching", " and ".join(f"`{t}`" for t in E4["touching"]),
        "results/e4_sigma_gradients.json")
    def _g(v):
        return "0" if v == 0 else f"{v:.3g}"
    put("e4_table", "".join(
        "| `{t}` | {live} | {w:.2f} | `{where}` | {gs} | {gd} | {gm} |\n".format(
            t=r["term"], live=("live" if not r["identically_zero"] else "**dead**"),
            w=r["weight"], where=r["where"],
            gs=_g(r["grad_logstd_tower_norm"]), gd=_g(r["grad_log_delta_logstd_abs"]),
            gm=_g(r["grad_min_logstd_abs"]))
        for r in E4["terms"]).rstrip(),
        "results/e4_sigma_gradients.json")

    # Appendix F's reason for existing quotes the ledger's size, so it is read
    # from the file rather than typed -- the ledger grows every revision.
    put("ledger_kb", f'{os.path.getsize("FINDINGS_LEDGER.md") / 1024:.0f}',
        "FINDINGS_LEDGER.md, on disk")

    # E5 / M-50 -- the synthetic sigma demonstration.
    E5 = J("e5_synthetic_sigma.json")
    _a5, _b5 = E5["arms"]["mse"], E5["arms"]["gaussian_nll"]
    _t5 = E5["thresholds"]
    put("e5s_verdict", E5["verdict"], "results/e5_synthetic_sigma.json")
    put("e5s_span", f'{E5["config"]["true_sigma_span_factor"]:.0f}',
        "results/e5_synthetic_sigma.json")
    put("e5s_seeds", len(E5["config"]["seeds"]), "results/e5_synthetic_sigma.json")
    put("e5s_iters", f'{E5["config"]["iters"]:,}', "results/e5_synthetic_sigma.json")
    put("e5s_n_train", f'{E5["config"]["n_train"]:,}', "results/e5_synthetic_sigma.json")
    put("e5s_mse_ratio", f'{_a5["ratio_mean"]:.4f}', "results/e5_synthetic_sigma.json")
    # ONE DECIMAL, not zero. At zero it printed 22, and once the combined arm's
    # two runs joined the collapse family e2_fitted_runs printed 22 as well --
    # the same numeral twice in §6.3, once as a factor and once as a count of
    # runs, which is the `restatement` check's ambiguous-numeral kind and the
    # defect it exists to catch (the abstract's 4.61× beside 4.61%). The
    # disambiguation is more precision on the measurement, not a note beside it.
    put("e5s_mse_under", f'{1 / _a5["ratio_mean"]:.1f}', "results/e5_synthetic_sigma.json")
    put("e5s_mse_spread", f'{_a5["spread_max"]:.3f}', "results/e5_synthetic_sigma.json")
    put("e5s_mse_slope", f'{_a5["slope_mean"]:+.6f}', "results/e5_synthetic_sigma.json")
    put("e5s_nll_ratio", f'{_b5["ratio_mean"]:.4f}', "results/e5_synthetic_sigma.json")
    put("e5s_nll_pct_off", f'{abs(1 - _b5["ratio_mean"]) * 100:.0f}',
        "results/e5_synthetic_sigma.json")
    # spread_max is the BEST of three seeds, and using it for the recovering arm
    # while using it for the collapsing arm too is generous in one direction and
    # conservative in the other: the mse spreads are 1.002/1.002/1.003 (max is the
    # worst case for a collapse claim) and the gaussian_nll spreads are
    # 3.668/1.137/1.023 (max is the best case for a recovery claim). The table now
    # prints the RANGE for the recovering arm, so a reader sees that two of three
    # seeds barely clear the 1.01x detection floor.
    _nll_spreads = sorted(r["sigma_hat_spread_factor"] for r in _b5["runs"])
    put("e5s_nll_spread", f'{_b5["spread_max"]:.2f}', "results/e5_synthetic_sigma.json")
    put("e5s_nll_spread_lo", f'{_nll_spreads[0]:.2f}', "results/e5_synthetic_sigma.json")
    put("e5s_nll_spread_range", f'{_nll_spreads[0]:.2f}\u2013{_nll_spreads[-1]:.2f}',
        "results/e5_synthetic_sigma.json")
    _nll_slopes = sorted(r["slope_log_sigma"] for r in _b5["runs"])
    put("e5s_nll_slope_lo", f'{_nll_slopes[0]:.4f}', "results/e5_synthetic_sigma.json")
    put("e5s_nll_slope_range", f'{_nll_slopes[0]:.4f}\u2013{_nll_slopes[-1]:.4f}',
        "results/e5_synthetic_sigma.json")
    put("e5s_nll_slope_spread_factor", f'{_nll_slopes[-1] / _nll_slopes[0]:.0f}',
        "results/e5_synthetic_sigma.json")
    _mse_spreads = sorted(r["sigma_hat_spread_factor"] for r in _a5["runs"])
    put("e5s_mse_spread_range", f'{_mse_spreads[0]:.3f}\u2013{_mse_spreads[-1]:.3f}',
        "results/e5_synthetic_sigma.json")
    put("e5s_nll_slope", f'{_b5["slope_mean"]:+.4f}', "results/e5_synthetic_sigma.json")
    put("e5s_slope_thr", f'{_t5["slope_threshold"]:.5f}', "results/e5_sigma_dilution.json")
    put("e5s_collapse_thr", _t5["collapse_ratio_threshold"], "results/e5_sigma_dilution.json")
    put("e5s_recovery_thr", f'{_t5["recovery_factor_threshold"]:.0f}',
        "results/e5_sigma_dilution.json")
    _D5 = J("e5_sigma_dilution.json")
    put("e5s_fp_rate", f'{_D5["mde"]["false_positive_rate_at_dilution_0"] * 100:.0f}',
        "results/e5_sigma_dilution.json")
    put("e5s_null_slope_p95", f'{_D5["null"]["slope_abs_p95"]:.1g}',
        "results/e5_sigma_dilution.json")
    put("e5s_null_spread", f'{_D5["null"]["spread_max"]:.4f}',
        "results/e5_sigma_dilution.json")
    put("e5s_null_ratio_lo", f'{_D5["null"]["ratio_median_min"]:.3f}',
        "results/e5_sigma_dilution.json")
    put("e5s_null_r_max", f'{_D5["null"]["r_abs_max"]:.2f}', "results/e5_sigma_dilution.json")
    put("e5s_span_floor", f'{_D5["mde"]["span_floor"]}', "results/e5_sigma_dilution.json")

    # E7 / M-51 -- three free ranking baselines.
    E7 = J("e7_free_baselines.json")
    _bl = {r["baseline"]: r for r in E7["baselines"]}
    put("e7_verdict", E7["verdict"], "results/e7_free_baselines.json")
    # Round 3, R4 (S2): what the verdict's label means, for places outside section 6.6 and Appendices E and K.
    _e7b = {b["baseline"]: b for b in J("e7_free_baselines.json")["baselines"]}
    assert E7["verdict"] == "SURVIVES entry-res ONLY", E7["verdict"]
    assert _e7b["entry-res"]["margin_beats_mde"] and not _e7b["step-size"]["margin_beats_mde"]
    put("e7_verdict_gloss", "disagreement beats the one-step error before the window, but not the model's "
                            "predicted step size", "results/e7_free_baselines.json")
    put("e7_nind", E7["design"]["n_independent"], "results/e7_free_baselines.json")
    put("e7_r_dis", f'{_bl["step-size"]["r_disagreement_error"]:+.4f}',
        "results/e7_free_baselines.json")
    put("e7_mde_margin", f'{E7["thresholds"]["margin"]:.4f}',
        "results/e7_free_baselines_power.json")
    put("e7_mde_partial", f'{E7["thresholds"]["partial"]:.4f}',
        "results/e7_free_baselines_power.json")
    # The abstract prints the step-size correlation at the three decimals its neighbours use.
    put("e7_step_r3", f'{_bl["step-size"]["r_baseline_error"]:+.3f}',
        "results/e7_free_baselines.json")

    for _k, _tag in (("step-size", "step"), ("entry-res", "entry"),
                     ("forecast-index", "index")):
        _r = _bl[_k]
        put(f"e7_{_tag}_r", f'{_r["r_baseline_error"]:+.4f}', "results/e7_free_baselines.json")
        put(f"e7_{_tag}_margin", f'{_r["margin"]:+.4f}', "results/e7_free_baselines.json")
        put(f"e7_{_tag}_partial", f'{_r["partial_disagreement_given_baseline"]:+.4f}',
            "results/e7_free_baselines.json")
        put(f"e7_{_tag}_beaten", "yes" if (_r["margin_beats_mde"] and _r["partial_beats_mde"])
            else "no", "results/e7_free_baselines.json")
        _ws = _r["within_step_r_baseline"]
        put(f"e7_{_tag}_ws", "undefined" if not (_ws == _ws) else f"{_ws:+.4f}",
            "results/e7_free_baselines.json")
    put("e7_ws_dis", f'{_bl["step-size"]["within_step_r_disagreement"]:+.4f}',
        "results/e7_free_baselines.json")
    put("e7_n_beaten", E7["n_beaten"], "results/e7_free_baselines.json")
    put("e7_n_new", E7["n_new_baselines"], "results/e7_free_baselines.json")

    # Referee Q2 (R-74) -- how many trajectories would settle the step-size margin.
    # §11 prints these beside e7_* values, so the two artifacts must describe the
    # same comparison or the paragraph would join two different samples.
    Q2 = J("q2_free_baseline_power.json")
    _own, _m51 = Q2["answer_to_the_referee"], Q2["answer_under_m51_as_pre_registered"]
    _pub = Q2["the_published_verdict_does_not_move"]
    assert Q2["observed"]["baseline"] == "step-size", Q2["observed"]["baseline"]
    assert Q2["observed"]["n_independent"] == E7["design"]["n_independent"], "Q2 and E7 arenas differ"
    assert f'{Q2["observed"]["margin"]:+.4f}' == N["e7_step_margin"]["value"], "Q2 margin != E7's"
    assert f'{_pub["threshold_m51_pre_registered"]:.4f}' == N["e7_mde_margin"]["value"], \
        "Q2's M-51 threshold != E7's"
    assert Q2["observed"]["partial_beats_mde_at_n0"] and not Q2["observed"]["margin_beats_mde_at_n0"], \
        "§11 says the margin is the binding test; the artifact no longer says so"
    assert not _pub["resolvable_under_either"], "§11 says the verdict stands on both readings"
    assert Q2["empirical_check"]["control_reproduces"], "Q2's control did not reproduce E7"
    put("q2_n_req", _own["n_independent_required"], "results/q2_free_baseline_power.json")
    put("q2_factor", f'{_own["factor_over_current"]:.2f}', "results/q2_free_baseline_power.json")
    put("q2_n_req_m51", _m51["n_independent_required"], "results/q2_free_baseline_power.json")
    put("q2_se_ratio", f'{Q2["why_the_two_differ"]["se_ratio_prereg_over_own"]:.2f}',
        "results/q2_free_baseline_power.json")
    # One decimal, not none: at none the first prints "91", which is also
    # q2_n_req_m51, and §11 prints both -- the restatement check (C19.1) refused a
    # section printing two different quantities as one numeral.
    put("q2_pct_own", f'{_pub["pct_of_own_threshold"]:.1f}', "results/q2_free_baseline_power.json")
    put("q2_pct_m51", f'{_pub["pct_of_m51_threshold"]:.1f}', "results/q2_free_baseline_power.json")
    # One row of the sensitivity table, chosen by its label, so the paper can show
    # the inverse-square rise rather than only assert it.
    _sens = [r for r in Q2["sensitivity_to_assumed_margin"] if abs(r["assumed_margin"] - 0.10) < 1e-12]
    assert len(_sens) == 1, "Q2's sensitivity table has no +0.10 row"
    assert _sens[0]["assumed_margin"] < Q2["observed"]["margin"] and \
        _sens[0]["n_required_own_statistic"] > _own["n_independent_required"], \
        "§11 says the requirement RISES to this row's n at a smaller margin"
    put("q2_sens_margin", f'{_sens[0]["assumed_margin"]:+.4f}', "results/q2_free_baseline_power.json")
    put("q2_sens_n", _sens[0]["n_required_own_statistic"], "results/q2_free_baseline_power.json")

    # Referee Q1 (R-75) -- how often the substitution behind sigma = 0 is made.
    Q1 = J("q1_pets_descendants.json")
    _c = Q1["counts"]
    assert Q1["verification"]["citations_still_valid"] and "--verify" in Q1["generated_with"], \
        "Q1's artifact was not produced by a verifying run"
    assert _c["inherits"] + _c["does_not_inherit"] + _c["could_not_determine"] == _c["carry_the_construction"]
    assert _c["could_not_determine"] == 0, "§2 says every loss was located; the artifact disagrees"
    # §2 names results/q1_search_protocol.md as the protocol the survey ran under.
    # That is true only if it is byte-for-byte the file whose hash the survey recorded.
    import hashlib as _hl
    assert _hl.sha256(open(os.path.join(R.RESULTS, "q1_search_protocol.md"), "rb").read()
                      ).hexdigest() == Q1["protocol"]["sha256"], \
        "results/q1_search_protocol.md is not the protocol the survey recorded"
    # §2 and R2 say "that one only ... trains it" and "only in a non-default mode":
    # singular, and qualified. Both hold only while there is exactly one INHERITS
    # entry and it carries the non-default-mode qualification.
    _inh = [r for r in Q1["examined"] if r["verdict"] == "INHERITS"]
    assert _c["inherits"] == 1 == len(_inh), "§2's singular 'that one' needs exactly one"
    assert "not the default" in _inh[0].get("qualification", ""), \
        "§2 and R2 say the one inheriting repository does so only in a non-default mode"
    assert _c["construction_absent_and_so_out_of_scope"] == len(Q1["construction_absent"])
    assert "leggedrobotics/rsl_rl" in [r["repo"] for r in Q1["construction_absent"]], \
        "§2 names mainline rsl_rl among the repositories set aside"
    put("q1_n_examined", _c["examined"], "results/q1_pets_descendants.json")
    # Round 3, R4 (S14): every repository the survey looked at. The protocol counts as "examined" only those with the
    # construction (results/q1_search_protocol.md, section 3), so all examined ones carry it, and the rest are set aside.
    assert _c["examined"] == len(Q1["examined"]) == _c["carry_the_construction"], _c
    put("q1_n_looked", _c["examined"] + _c["construction_absent_and_so_out_of_scope"], "results/q1_pets_descendants.json")
    put("q1_n_absent", _c["construction_absent_and_so_out_of_scope"],
        "results/q1_pets_descendants.json")
    put("q1_cap", _c["cap"], "results/q1_pets_descendants.json")
    put("q1_n_carry", _c["carry_the_construction"], "results/q1_pets_descendants.json")
    put("q1_n_inherit", _c["inherits"], "results/q1_pets_descendants.json")
    put("q1_n_keep", _c["does_not_inherit"], "results/q1_pets_descendants.json")
    import datetime as _dt
    _d = _dt.date.fromisoformat(Q1["search_date"])
    put("q1_date", f"{_d.day} {_d:%B %Y}", "results/q1_pets_descendants.json")

    # Referee Q3 (M-70, M-71) -- whether the per-horizon correction reorders the
    # penalty accumulated along a rollout.
    Q3 = J("q3_penalty_reordering.json")
    _s, _st = Q3["statistic"], Q3["is_the_null_structural"]
    assert _s["n_undefined_pairs"] == 0 and _s["n_defined_pairs"] == _s["n_pairs_total"]
    assert _st["ordering_equals_dominant_band_ordering"], \
        "§11 says the overall ordering is exactly the dominant band's"
    _dom = str(_st["dominant_band_after_correction"])
    assert _st["share_of_corrected_penalty_by_band"][_dom] == max(
        _st["share_of_corrected_penalty_by_band"].values())
    assert sum(_st["steps_per_band"].values()) == Q3["arena"]["steps_per_trajectory"]
    assert int(_dom) == max(Q3["arena"]["horizons"]), "§11 calls the dominant band the last"
    assert _st["dominant_band_share"] == _st["share_of_corrected_penalty_by_band"][_dom], \
        "§11 prints the dominant band's share of the CORRECTED penalty"
    # §11's M-71 sentence ("with none reordering, no resample can return anything
    # else") is true only at f = 0; at f = 1 it would need rewording, and between
    # them it is false.
    assert _s["n_reordering_pairs"] == 0, "§11's degenerate-interval sentence assumes f = 0"
    put("q3_verdict", Q3["verdict"], "results/q3_penalty_reordering.json")
    put("q3_n_pairs", _s["n_pairs_total"], "results/q3_penalty_reordering.json")
    put("q3_n_reorder", _s["n_reordering_pairs"], "results/q3_penalty_reordering.json")
    put("q3_nind", Q3["arena"]["n_independent"], "results/q3_penalty_reordering.json")
    put("q3_c_ratio", f'{Q3["spread_of_the_correction"]["c_ratio_max_over_min"]:.2f}',
        "results/q3_penalty_reordering.json")
    put("q3_dom_h", int(_dom), "results/q3_penalty_reordering.json")
    put("q3_dom_steps", _st["steps_per_band"][_dom], "results/q3_penalty_reordering.json")
    put("q3_steps", Q3["arena"]["steps_per_trajectory"], "results/q3_penalty_reordering.json")
    put("q3_dom_share", f'{100 * _st["dominant_band_share"]:.2f}',
        "results/q3_penalty_reordering.json")

    # M-49's design, so §11 can name it rather than describe it.
    P2 = J("p2_capacity_power.json")
    put("m49_width", P2["capacity"]["matched_hidden_size"], "results/p2_capacity_power.json")
    put("m49_matched_params", f'{P2["capacity"]["matched_total_params"]:,}',
        "results/p2_capacity_power.json")
    put("m49_matched_ratio", f'{P2["capacity"]["matched_ratio"]:.4f}',
        "results/p2_capacity_power.json")
    put("m49_mde_ratio", f'{P2["mde_80pct_power"]["overconfidence_ratio_multiplicative"]:.2f}',
        "results/p2_capacity_power.json")
    put("m49_mde_cov", f'{P2["mde_80pct_power"]["coverage_pts"]:.2f}',
        "results/p2_capacity_power.json")

    # M-49 discharged. The capacity-matched arm.
    M49 = J("m49_capacity_matched.json")
    _m49 = M49["m44"]           # the block name is R2's; the rule is M-49's
    put("m49_verdict", _m49["verdict"], "results/m49_capacity_matched.json")
    put("m49_verdict_short", _m49["verdict"].split("\u2014")[0].strip(),
        "results/m49_capacity_matched.json")
    put("m49_ratio_gain", f'{_m49["mean_ratio_improvement"]:.2f}',
        "results/m49_capacity_matched.json")
    put("m49_cov_gain", f'{_m49["mean_coverage_gain_pts"]:+.2f}',
        "results/m49_capacity_matched.json")
    put("m49_n_conditions", len(_m49["conditions"]), "results/m49_capacity_matched.json")
    put("m49_n_conditions_met", sum(1 for v in _m49["conditions"].values() if v),
        "results/m49_capacity_matched.json")
    put("m49_shrink",
        f'{J("r2_independent_ensemble.json")["m44"]["mean_ratio_improvement"] - _m49["mean_ratio_improvement"]:.2f}',
        "results/m49_capacity_matched.json + r2_independent_ensemble.json")

    AG = J("appendix_g_rules.json")
    put("appG_n_rules", AG["n_rules"], "results/appendix_g_rules.json")
    put("appG_n_lead", AG["n_with_lead_time"], "results/appendix_g_rules.json")
    _pos = [r for r in AG["rules"] if (r["lead_hours"] or 0) > 0]
    _neg = [r for r in AG["rules"] if r["lead_hours"] is not None and r["lead_hours"] < 0]
    put("appG_n_positive", len(_pos), "results/appendix_g_rules.json")
    put("appG_n_negative", len(_neg), "results/appendix_g_rules.json")
    def _lead(r):
        if r["lead_hours"] is None:
            return "not computed"
        v = r["lead_hours"]
        return f"{v * 60:+.0f} min" if abs(v) < 1 else f"{v:+.1f} h"
    _rows = "".join(
        "| `{id}` | {title} | {commit} | {lead} | {tested} | {verdict} |\n".format(
            id=r["id"], title=r["title"].replace("|", "/"),
            commit=(f'`{r["rule_commit"]}` {r["commit_subject"]}'
                    if r["rule_commit"] else "—"),
            lead=_lead(r), tested=r["tested_by"] or "—",
            verdict=r["verdict"].replace("|", "/"))
        for r in AG["rules"])
    put("appG_table", _rows.rstrip(), "results/appendix_g_rules.json")
    # M-69's lead time, from git. The commit that first held the data it tested was
    # amended after it was created, so its committer timestamp is later than its
    # author timestamp and the lead differs by which one is read. Both readings are
    # derived here from git, so they are the same in any clone with full history.
    # m69_lead_pub reads the STORED value that the table cell above renders, which a
    # clean rebuild rewrites from git: it equals the author-time reading in a tree
    # whose artifact predates the amend and the committer-time reading in one that
    # regenerated it afterwards. The sentence beneath the table is written so that
    # nothing in it depends on which of the two the stored value happens to be.
    _r69 = next(r for r in AG["rules"] if r["id"] == "M-69")
    _g = lambda *a: subprocess.run(["git", "log", *a], capture_output=True,
                                   text=True).stdout.strip().split("\n")[-1].split("\t")
    _, _d_at, _d_ct = _g("--diff-filter=A", "--format=%H\t%at\t%ct", "--",
                         _r69["tested_by"])
    _, _r_ct = _g("--format=%H\t%ct", "-S", "### M-69 —", "--", "FINDINGS_LEDGER.md")
    _d_at, _d_ct, _r_ct = int(_d_at), int(_d_ct), int(_r_ct)
    _gsrc = "results/appendix_g_rules.json + git log"
    put("m69_lead_pub", _lead(_r69), _gsrc)
    put("m69_lead_author", _lead({"lead_hours": (_d_at - _r_ct) / 3600}), _gsrc)
    put("m69_lead_regen", _lead({"lead_hours": (_d_ct - _r_ct) / 3600}), _gsrc)
    put("m69_amend_min", round((_d_ct - _d_at) / 60), _gsrc)
    # Appendix E's M-69 sentence rests its disclosure on "both readings are positive":
    # the rule reached git before the data on either timestamp. Asserted, not assumed.
    assert _d_at - _r_ct > 0 and _d_ct - _r_ct > 0, (
        "an M-69 lead-time reading is not positive; Appendix E's sentence says both are")
    # B.1: the body no longer carries rule texts. They ship in full in
    # docs/APPENDIX_G_RULES.md, written by scripts/appendix_g_rules.py.
    put("tn_classes", TN["n_classes"], "results/typed_numerals.json")
    put("tn_exceptions", TN["n_exceptions"], "results/typed_numerals.json")
    # C5(rev2), 3.5. Section 8 said "N kinds" from this key while appendix D
    # enumerated eight by hand, and the two had drifted seven apart. The
    # enumeration is generated from the same set the count comes from, so the
    # `kind-count` check has something to compare and the two cannot disagree.
    # The defects the self-test found in the checker rather than in the paper.
    # Appendix C said "Two" and listed two; there are more, and a typed count in
    # the appendix about count consistency is not defensible.
    _cd = CC.get("checker_defects", [])
    put("cc_selfdefects", len(_cd), "results/comparative_claims.json")
    put("cc_selfdefects_word", WORDS.get(len(_cd), str(len(_cd))), "results/comparative_claims.json")
    put("cc_selfdefects_lower",
        WORDS.get(len(_cd), str(len(_cd))).lower(), "results/comparative_claims.json")
    put("cc_selfdefect_list",
        "".join(f"\n\n- {d[0].upper()}{d[1:]}." for d in _cd),
        "results/comparative_claims.json")
    _kinds = sorted({c["kind"] for c in CC["claims"]})
    _blurb = {
        "overlap": "two intervals do or do not overlap",
        "extremum": "a named cell is the max or min of its family",
        "figure_reference": "every in-text figure number names a figure that exists, and no "
                            "more distinct figure numbers are cited than the document has "
                            "figures",
        "sign": "a stated rise or fall matches the direction of the difference",
        "orders": "a stated count of orders of magnitude matches `round(log10(ratio))`, "
                  "or a ratio quoted directly appears in the sentence that quotes it",
        "cell": "a k-of-45 count is the arena and horizon the text names",
        "compare": "a stated ordering between two scalars",
        "relvar": "a stated ratio of relative variabilities",
        "count-consistency": "one count asserted in several places, in words, numerals or "
                             "numeric-string variants, agrees everywhere",
        "horizon-label": "a phrase naming a horizon resolves to the horizon the artifact says "
                         "it is, and the numbers beside it are that horizon's",
        "horizon-forbidden": "a withdrawn horizon label appears nowhere in the paper",
        "horizon-consistency": "every horizon-indexed figure in the prose names its horizon, "
                               "and names the one its artifact cell came from",
        "count-dependence": "a clean k-of-k count carries an interval or a not-independent note",
        "retraction-consistency": "a claim the ledger marks superseded is asserted nowhere "
                                  "reader-facing",
        "retraction_class_consistency": "every retraction identifier a reader-facing file names "
                                        "resolves to exactly one class, and to the class the "
                                        "ledger gives it",
        "cross-artifact-sync": "the README and model card carry the paper's headline values",
        "abstract-budget": "the abstract stays inside its word and numeral budget",
        "interval-required": "a quoted ratio or coverage is accompanied by its interval",
        "arithmetic": "a stated total equals the sum of its stated parts",
        "population_partition": "the run populations the paper quotes against one another "
                                "partition -- the run table's row counts sum to the stated "
                                "total, every row states the width it trained at, and the "
                                "collapse family plus the runs excluded from it equal the "
                                "total",
        "unit-consistency": "every n_independent figure names the evaluation unit it counts -- the revision introduced a second unit length, and 60 units of 33 rows and 4 of 400 are both \"n_independent\"",
        "kind-count": "the number of kinds the build accounting claims, this file enumerates "
                      "and the checker registers are one number",
        "scope-consistency": "a universal quantifier is checked against the set it quantifies "
                             "over",
        "frequency-consistency": "a frequency stated in words -- \"at every horizon\", \"at "
                                 "exactly one place\" -- matches a count recomputed from the "
                                 "artifacts",
        "table_renders": "every table in the source reaches the LaTeX as a table, with at "
                         "least one row separator per source row",
        "arena_consistency": "every row of the evidence table (Appendix D's second) names an arena "
                             "and an n_independent that the section owning that claim also states",
        "restatement": "no sentence restates a quantity another section owns -- no numeral is "
                       "typed into the slot a substituted one fills elsewhere, and no section "
                       "prints two different quantities as the same numeral",
        "rule-seed-scope": "a sentence quoting the three-seed headline or its rule-horizon cells near "
                           "the word rule or pre-register names the one seed the rule ran on, or the "
                           "three-seed extension",
        "overstat-reversal": "no sentence says the released evaluation overstates its error beside an "
                             "alignment figure unless its paragraph names the reversal of sign",
        "alignment-arena": "a sentence naming the action-alignment defect and a short-horizon cost has the "
                           "all-ten-episodes figures, or those words, in its paragraph",
        "action-response": "a paragraph quoting our arms' stale-pairing sensitivity also carries rule X2's figure "
                           "for how they respond to the action",
        "compute-claim": "no rendered file says a setting won even when its rival trained longer, and every "
                         "front-matter sentence that names compute or longer training says the ranking depends "
                         "on it or names the split",
    }
    _missing = [k for k in _kinds if k not in _blurb]
    assert not _missing, f"check kinds with no appendix D description: {_missing}"
    put("cc_kind_list",
        ", ".join(f"*{k}* ({_blurb[k]})" for k in _kinds[:-1])
        + f", and *{_kinds[-1]}* ({_blurb[_kinds[-1]]})",
        "results/comparative_claims.json")
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
    runs_all = sorted(glob.glob("results/step5_arm*.json"))
    assert runs_all, "no results/step5_arm*.json -- cannot count training runs"

    # M-49 added five runs at a REDUCED hidden width, and every consumer of this
    # glob is a claim about the released architecture: §6.3's "the collapse rate
    # is nearly identical across runs", the run table a reader is invited to
    # count, the sigma-collapse rate fits. A different architecture entering any
    # of those through a glob is silent contamination of a headline statistic,
    # and nothing could have caught it because the width was recorded nowhere in
    # the run artifact. It is recorded now (scripts/step5_train.py).
    #
    # Runs written before that change carry no width. They are all at the
    # released width -- --hidden did not exist -- and that is asserted rather
    # than assumed: a run with no recorded width must also carry no M-49 tag.
    _released_w = R.load_reference_config(R.repo_paths()["lite"])[
        "architecture_config"]["rnn_hidden_size"]

    def _width(path):
        h = json.load(open(path)).get("hyperparameters", {})
        w = h.get("rnn_hidden_size")
        if w is None:
            assert "_m49" not in path, (
                f"{path} carries an M-49 tag and no recorded width; it cannot be "
                f"assumed to be the released architecture")
            return _released_w
        return int(w)

    runs = [f for f in runs_all if _width(f) == _released_w]
    runs_offwidth = [f for f in runs_all if _width(f) != _released_w]
    assert runs, "no runs at the released architecture width"
    put("n_runs", len(runs), "results/step5_arm*.json")
    put("n_runs_offwidth", len(runs_offwidth), "results/step5_arm*.json")
    put("released_width", _released_w, "the reference architecture_config")
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
    # S5: the three classes -- claims withdrawn on evidence, framings withdrawn, and
    # early hypotheses closed as housekeeping -- are scripts/ledger_check.py's, read from
    # its output rather than re-derived here, so there is one classification and one set
    # of counts. S-01..S-07 are the early hypotheses; S-12 and S-15 onward the framings.
    # A stale output is refused rather than printed.
    _CLS = J("claims_to_evidence.json")["retraction_classes"]
    assert _CLS["n_superseded"] == len(sup), (
        "results/claims_to_evidence.json is stale against FINDINGS_LEDGER.md: run "
        "scripts/ledger_check.py first", _CLS["n_superseded"], len(sup))
    retr, fram = list(_CLS["evidence"]), list(_CLS["framing"])
    _SRC_CLS = "results/claims_to_evidence.json (scripts/ledger_check.py)"
    put("n_superseded", _CLS["n_superseded"], _SRC_CLS)
    put("n_retractions", len(retr), _SRC_CLS)
    put("n_retract_framing", len(fram), _SRC_CLS)
    # Section 8 and appendix D each ENUMERATED the framing retractions in prose
    # ("the claim that a pre-registration was pre-registered, and the binomial
    # inference of 6.6"). Two more were entered by the second revision and a
    # third recorded a narrowing the paper had made without ever entering it, so
    # a typed enumeration beside a generated count is a count-consistency defect
    # waiting to happen. The list is built from the entry titles.
    def _title(sid):
        blk = led[led.index("### " + sid + " "):]
        line = blk[:blk.find("\n")]
        t = line.split("—", 1)[1] if "—" in line else line
        return t.split("·")[0].strip().strip('"')
    _ftitles = [_title(x) for x in fram]
    put("n_retract_framing_list",
        "".join(f"\n\n- **{t}** (`{sid}`)." for sid, t in zip(fram, _ftitles)),
        "FINDINGS_LEDGER.md")
    put("n_retract_framing_ids", ", ".join(f"`{x}`" for x in fram), "FINDINGS_LEDGER.md")
    put("n_retractions_word", WORDS.get(len(retr), str(len(retr))), _SRC_CLS)
    put("n_retractions_lower", WORDS.get(len(retr), str(len(retr))).lower(), _SRC_CLS)
    put("n_retractions_word_lower", WORDS.get(len(retr), str(len(retr))).lower(), _SRC_CLS)
    put("n_retract_framing_word", WORDS.get(len(fram), str(len(fram))).lower(), _SRC_CLS)
    put("n_retract_framing_word_cap", WORDS.get(len(fram), str(len(fram))), _SRC_CLS)
    ORD = {1: "a seventh", 2: "two further", 3: "three further", 4: "four further"}
    put("n_retract_framing_phrase", ORD.get(len(fram), f"{len(fram)} further"), _SRC_CLS)
    put("n_retract_total", len(retr) + len(fram), _SRC_CLS)

    # B4/B5. Which review entered which framing retraction, from git rather than
    # from memory.
    #
    # §8 said "the second pre-submission review entered three more framing
    # retractions"; appendix D said "The last four were entered by the second
    # pre-submission review", and enumerated four. Both sentences restate a
    # quantity that neither of them computes, and one of them was wrong: the
    # commit that entered S-16, S-17, S-18 and S-19 is a single commit and it
    # entered four.
    #
    # A framing retraction's COHORT is the commit that first introduced its
    # ledger heading. Cohorts are ordered by commit time. Both sentences are about
    # the second pre-submission review's cohort. That was "the last cohort" until
    # the pre-submission programme entered S-20 in a cohort of its own, and every
    # sentence built on these keys went false at once ("the second pre-submission
    # review entered one more"). So the review's cohort is fixed by a boundary in
    # history rather than by position: it is the last cohort committed before the
    # commit that added docs/presubmission/PLAN.md. The `last` in the key names
    # means that. Cohorts after the boundary are the programme's own.
    _sha = {}
    for sid in fram:
        _out = subprocess.run(
            ["git", "log", "--format=%H\t%ct", "-S", "### " + sid + " \u2014",
             "--", "FINDINGS_LEDGER.md"],
            capture_output=True, text=True).stdout.strip().split("\n")
        assert _out and _out[-1], f"no commit introduces the ledger heading for {sid}"
        _h, _t = _out[-1].split("\t")
        _sha[sid] = (_h, int(_t))
    _cohorts = {}
    for sid, (h, t) in _sha.items():
        _cohorts.setdefault(h, {"t": t, "ids": []})["ids"].append(sid)
    _ordered = sorted(_cohorts.values(), key=lambda c: c["t"])
    _plan = subprocess.run(
        ["git", "log", "--diff-filter=A", "--format=%ct", "--",
         "docs/presubmission/PLAN.md"], capture_output=True, text=True).stdout.split()
    assert _plan, "no commit adds docs/presubmission/PLAN.md"
    _before = [c for c in _ordered if c["t"] < int(_plan[-1])]
    _last = _before[-1]["ids"]
    _earlier = [x for c in _before[:-1] for x in c["ids"]]
    _after = [x for c in _ordered[len(_before):] for x in c["ids"]]
    put("n_framing_last_cohort", len(_last), "FINDINGS_LEDGER.md + git log")
    put("n_framing_last_cohort_word", WORDS.get(len(_last), str(len(_last))).lower(),
        "FINDINGS_LEDGER.md + git log")
    put("n_framing_before_last", len(_earlier), "FINDINGS_LEDGER.md + git log")
    put("n_framing_before_last_word", WORDS.get(len(_earlier), str(len(_earlier))).lower(),
        "FINDINGS_LEDGER.md + git log")
    put("n_framing_cohorts", len(_ordered), "FINDINGS_LEDGER.md + git log")
    # What the count read when the review's cohort landed: appendix D's
    # counterfactual ("would have said six and enumerated two").
    _thru = len(_earlier) + len(_last)
    put("n_framing_through_review_word", WORDS.get(_thru, str(_thru)).lower(),
        "FINDINGS_LEDGER.md + git log")
    put("framing_last_cohort_ids", ", ".join(f"`{x}`" for x in sorted(_last)),
        "FINDINGS_LEDGER.md + git log")
    # The last cohort's entries, less the final one, which appendix D describes
    # separately because it is different in kind: "`S-16`, `S-17` and `S-18` are
    # sentences of the 24 August draft that were false. `S-19` is different..."
    put("framing_last_cohort_ids_but_last",
        ", ".join(f"`{x}`" for x in sorted(_last)[:-1][:-1])
        + " and " + f"`{sorted(_last)[:-1][-1]}`" if len(_last) > 2 else "",
        "FINDINGS_LEDGER.md + git log")
    put("framing_last_cohort_final", f"`{sorted(_last)[-1]}`",
        "FINDINGS_LEDGER.md + git log")
    assert len(_last) + len(_earlier) + len(_after) == len(fram)

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

    # --- D3: the ensemble-5 arms (M-43) ------------------------------------
    E5 = J("task_d3_ens5.json")
    P5 = J("task_d3b_ens5_power.json")
    put("e5_nind", E5["design"]["n_independent"], "results/task_d3_ens5.json")
    put("e5_seeds", len(E5["design"]["seeds"]), "results/task_d3_ens5.json")
    put("e5_verdict", E5["m43_verdict"]["verdict"], "results/task_d3_ens5.json")
    put("e5_leads_all", str(E5["m43_verdict"]["leads_at_every_horizon"]).lower(),
        "results/task_d3_ens5.json")
    put("e5_n_excl", E5["m43_verdict"]["n_excluding_zero"], "results/task_d3_ens5.json")
    put("e5_n_horizons", len(E5["m43_verdict"]["horizons_tested"]), "results/task_d3_ens5.json")
    _cells = [(h, r) for h in ("8", "32", "128", "368")
              for r in E5["governing"][h]["per_seed"]]
    put("e5_lead_cells", sum(1 for _, r in _cells if r["r_disagreement"] > r["r_index"]),
        "results/task_d3_ens5.json")
    put("e5_total_cells", len(_cells), "results/task_d3_ens5.json")
    put("e5_diff_lo", f'{min(r["paired_diff"] for _, r in _cells):+.3f}',
        "results/task_d3_ens5.json")
    put("e5_diff_hi", f'{max(r["paired_diff"] for _, r in _cells):+.3f}',
        "results/task_d3_ens5.json")
    for h in (1, 8, 32, 100, 128, 368):
        c = E5["calibration"][str(h)]
        put(f"e5_ratio_h{h}", f'{c["mean_ratio"]:.1f}', "results/task_d3_ens5.json")
        put(f"e5_cov1_h{h}", f'{100*c["mean_cov1"]:.2f}', "results/task_d3_ens5.json")
        put(f"e5_cov2_h{h}", f'{100*c["mean_cov2"]:.2f}', "results/task_d3_ens5.json")
        put(f"e5_npos_h{h}", f'{c["mean_npos"]:.1f}', "results/task_d3_ens5.json")
        put(f"e5_ratio_ci_h{h}", f'{c["ratio_ci"][0]:.1f}, {c["ratio_ci"][1]:.1f}',
            "results/task_d3_ens5.json")
        put(f"e5_cov1_ci_h{h}", f'{100*c["cov1_ci"][0]:.2f}, {100*c["cov1_ci"][1]:.2f}',
            "results/task_d3_ens5.json")
        put(f"e5_cov2_ci_h{h}", f'{100*c["cov2_ci"][0]:.2f}, {100*c["cov2_ci"][1]:.2f}',
            "results/task_d3_ens5.json")
    put("e5_collapse", f'{E5["collapse"]["ens5_mean"]:.4e}', "results/task_d3_ens5.json")
    put("e5_collapse_ens1", f'{E5["collapse"]["ens1_mean"]:.4e}', "results/task_d3_ens5.json")
    put("e5_collapse_pct", f'{100*E5["collapse"]["relative_difference"]:+.2f}',
        "results/task_d3_ens5.json")
    _cov = [v["cov_across_batch"] for v in E5["input_dependence"].values()]
    _sg = [v["sigma_growth_1_to_8"] for v in E5["input_dependence"].values()]
    _eg = [v["err_growth_1_to_8"] for v in E5["input_dependence"].values()]
    put("e5_cov_lo", f"{min(_cov):.3f}", "results/task_d3_ens5.json")
    put("e5_cov_hi", f"{max(_cov):.3f}", "results/task_d3_ens5.json")
    put("e5_sg_lo", f"{min(_sg):.2f}", "results/task_d3_ens5.json")
    put("e5_sg_hi", f"{max(_sg):.2f}", "results/task_d3_ens5.json")
    put("e5_eg_lo", f"{min(_eg):.1f}", "results/task_d3_ens5.json")
    put("e5_eg_hi", f"{max(_eg):.1f}", "results/task_d3_ens5.json")
    for h in (8, 368):
        a_ = E5["accuracy_vs_ens1"][str(h)]
        put(f"e5_acc_h{h}", f'{a_["ens5_over_ens1"]:.3f}', "results/task_d3_ens5.json")
    # power and the in-sample companion
    put("e5_power_mean", f'{100*P5["power_summary"]["mean_power_at_n4"]:.0f}',
        "results/task_d3b_ens5_power.json")
    put("e5_power_worst", f'{100*P5["power_summary"]["worst_power"]:.0f}',
        "results/task_d3b_ens5_power.json")
    put("e5_power_worst_h", P5["power_summary"]["worst_horizon"],
        "results/task_d3b_ens5_power.json")
    put("e5_comp_nind", P5["design"]["n_independent"], "results/task_d3b_ens5_power.json")
    put("e5_comp_excl", P5["companion_summary"]["n_excluding_zero"],
        "results/task_d3b_ens5_power.json")
    put("e5_comp_n", P5["companion_summary"]["n_horizons"], "results/task_d3b_ens5_power.json")
    put("e5_comp_pass", str(P5["companion_summary"]["would_have_passed_m43"]).lower(),
        "results/task_d3b_ens5_power.json")
    _ci = P5["power_summary"]["in_sample_effect_range"]
    _co = P5["power_summary"]["out_of_sample_effect_range"]
    put("e5_eff_ins", f"{_ci[0]:+.3f} to {_ci[1]:+.3f}", "results/task_d3b_ens5_power.json")
    put("e5_eff_oos", f"{_co[0]:+.3f} to {_co[1]:+.3f}", "results/task_d3b_ens5_power.json")

    # --- C2: the data budget ----------------------------------------------
    C2 = J("task_c2_data_budget.json")
    put("c2_trans", f'{C2["ours"]["distinct_transitions"]:,}', "results/task_c2_data_budget.json")
    put("c2_rows", f'{C2["ours"]["rows_in_training_episodes"]:,}',
        "results/task_c2_data_budget.json")
    put("c2_windows", f'{C2["ours"]["training_windows"]:,}', "results/task_c2_data_budget.json")
    put("c2_bounds", C2["ours"]["boundaries_excluded"], "results/task_c2_data_budget.json")
    put("c2_ref", f'{C2["reference"]["value"]:,}', "results/task_c2_data_budget.json")
    put("c2_ratio", f'{C2["ratio_reference_over_ours"]:,.0f}', "results/task_c2_data_budget.json")
    put("c2_pct", f'{100*C2["ours_as_fraction_of_reference"]:.3f}',
        "results/task_c2_data_budget.json")
    put("c2_draws", f'{C2["ours"]["window_draws_per_run"]:,}', "results/task_c2_data_budget.json")

    # --- D1/D2/D4: the released checkpoint at n_independent = 20 -----------
    D = J("task_d_nind20.json")
    put("d1n_nind", D["design"]["n_independent"], "results/task_d_nind20.json")
    put("d1n_ntraj", D["design"]["trajectories"], "results/task_d_nind20.json")
    put("d1n_eps", len(D["design"]["episodes"]), "results/task_d_nind20.json")
    for h in (1, 8, 32, 100, 128, 368):
        r = D["d1_by_horizon"][str(h)]
        for q, tg in (("aleatoric", "alea"), ("epistemic", "epi"), ("total", "tot")):
            m = r[q]
            rr = m["ratio_err_over_sigma"]
            put(f"d1n_{tg}_ratio_h{h}", f"{rr:,.0f}" if rr >= 100 else f"{rr:.1f}",
                "results/task_d_nind20.json")
            put(f"d1n_{tg}_cov1_h{h}", f'{100*m["coverage_pm1"]:.2f}',
                "results/task_d_nind20.json")
            _rc = m["ratio_err_over_sigma_ci"]
            _f = (lambda v: f"{v:,.0f}") if rr >= 100 else (lambda v: f"{v:.1f}")
            put(f"d1n_{tg}_ratio_ci_h{h}", f"{_f(_rc[0])}, {_f(_rc[1])}",
                "results/task_d_nind20.json")
            for _q, _k in (("cov1", "coverage_pm1_ci"), ("cov2", "coverage_pm2_ci")):
                _cc = m[_k]
                put(f"d1n_{tg}_{_q}_ci_h{h}", f"{100*_cc[0]:.2f}, {100*_cc[1]:.2f}",
                    "results/task_d_nind20.json")
            put(f"d1n_{tg}_cov2_h{h}", f'{100*m["coverage_pm2"]:.2f}',
                "results/task_d_nind20.json")
            put(f"d1n_{tg}_npos_h{h}", m["n_positive"], "results/task_d_nind20.json")
            put(f"d1n_{tg}_ndim_h{h}", m["n_finite_corr"], "results/task_d_nind20.json")
            put(f"d1n_{tg}_r_h{h}", f'{m["corr_mean"]:+.3f}', "results/task_d_nind20.json")
    _e1, _e368 = D["d1_by_horizon"]["1"], D["d1_by_horizon"]["368"]
    # A5: quote the ratio itself rather than an orders-of-magnitude phrase. It is
    # exact and generated; "two orders" and "nearly three orders" disagreed with
    # each other across the abstract and section 12 while both described this value.
    #
    # C1(rev2): it is HORIZON-DEPENDENT, and only the h=368 form existed, so the
    # abstract, 6.2 and 13 all paired an h=368 ratio (600x) with an h=100 figure in
    # the same sentence. The ratio at the deployment horizon is 350x. Generated at
    # every horizon so that a sentence can quote the one it is scoped to.
    for _h in (1, 8, 32, 100, 128, 368):
        _r = D["d1_by_horizon"][str(_h)]
        put(f"d1n_epi_over_alea_h{_h}",
            f'{_r["aleatoric"]["ratio_err_over_sigma"]/_r["epistemic"]["ratio_err_over_sigma"]:,.0f}',
            "results/task_d_nind20.json")

    # D2 -- the forecast-index baseline
    #
    # C1(rev2): h=100 was absent from this table while 3.1 declares it part of the
    # grid and the abstract is anchored to it. The rollouts already carried it.
    for h in ("1", "8", "32", "100", "128", "368", "all"):
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
    for h in ("8", "32", "100", "128", "368", "all"):
        r = D["d2_forecast_index"][h]
        k = h if h == "all" else f"h{h}"
        put(f"d2p_diff_{k}", f'{r["paired_diff"]:+.3f}', "results/task_d_nind20.json")
        put(f"d2p_ci_{k}", f'[{r["paired_ci_lo"]:+.3f}, {r["paired_ci_hi"]:+.3f}]',
            "results/task_d_nind20.json")
    # The horizons at which the forecast index is DEFINED. h=1 has one forecast
    # step, so the index is constant there and its correlation does not exist.
    # This set is fixed by M-43's own text and must NOT follow the reporting grid:
    # moving it would retroactively change a discharged pre-registration. It is
    # read from the artifact -- where task_d3_ens5.py records it as
    # index_defined_at -- rather than typed here, so it is derived AND fixed.
    _IDX = [str(h) for h in J("task_d3_ens5.json")["design"]["index_defined_at"]]
    assert all(h in D["d2_forecast_index"] for h in _IDX), \
        "an index-defined horizon is missing from the n=20 table"
    # ...and the RELEASED CHECKPOINT's own table follows the reporting grid, which
    # now carries h=100. These are two different sets and were one key. Keeping
    # them one would have made "N of 4" sit under a five-row table, or -- worse --
    # silently widened a discharged pre-registration to a horizon it never named.
    # Derived from the artifact both times: a horizon is in the released
    # checkpoint's set exactly when its index correlation exists.
    _IDX_REL = [h for h in ("1", "8", "32", "100", "128", "368")
                if D["d2_forecast_index"][h]["r_index"] is not None]
    assert set(_IDX) <= set(_IDX_REL), \
        "M-43's index_defined_at is not a subset of the reporting grid"
    _sep = [h for h in _IDX_REL if D["d2_forecast_index"][h]["paired_excludes_zero"]]
    _ovl = [h for h in _IDX_REL if D["d2_forecast_index"][h]["marginal_ci_overlap"]]
    put("d2p_n_separating", len(_sep), "results/task_d_nind20.json")
    put("d2p_n_horizons", len(_IDX_REL), "results/task_d_nind20.json")
    put("d2p_overlap_h", " and ".join(f"h={x}" for x in _ovl) or "none",
        "results/task_d_nind20.json")
    put("d2p_n_overlap", len(_ovl), "results/task_d_nind20.json")
    _narrow = min(_IDX_REL,
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
    _dw = [h for h in _IDX_REL if D["d2_forecast_index"][h]["index_wins"]]
    put("d2b_n_index_wins", len(_dw), "results/task_d_nind20.json")
    put("d2b_n_horizons_tested", len(_IDX_REL), "results/task_d_nind20.json")
    # The horizon at which the counter is strongest, so 6.7's sentence naming it
    # cannot go stale the way "at h=128 the intervals overlap" did when a second
    # overlapping horizon appeared.
    _idxmax = max(_IDX_REL, key=lambda h: D["d2_forecast_index"][h]["r_index"])
    put("d2b_idx_strongest_h", f"h={_idxmax}", "results/task_d_nind20.json")
    _all = D["d2_forecast_index"]["all"]
    put("d2b_shrink_all", f'{_all["r_epistemic"] - _all["r_partial"]:+.3f}',
        "results/task_d_nind20.json")
    put("d2b_shrink_all_abs", f'{abs(_all["r_epistemic"] - _all["r_partial"]):.3f}',
        "results/task_d_nind20.json")

    # D4 -- the penalty correlation, with an interval and an n at last
    _p4 = D["d4_penalty"]
    put("d4_r", f'{_p4["corr_with_total_abs_error"]:+.3f}', "results/task_d_nind20.json")
    # Round 3 (A13): the abstract and section 12 set e7_step_r3 beside d4_r; e7's own figure for disagreement
    # (e7_r_dis) must be d4_r's number at three decimals, or the pair compares two different quantities.
    assert f'{float(N["e7_r_dis"]["value"]):+.3f}' == N["d4_r"]["value"], (N["e7_r_dis"]["value"], N["d4_r"]["value"])
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
    # C3(rev2), 3.1. 6.8 said the two largest deviations were "both at h=100 on the
    # aleatoric term, in opposite directions". Neither half was true: the second
    # largest is at h=128, and both sit ABOVE the target. The sentence is now
    # assembled from the artifact -- horizon, quantity and side -- so the only way
    # to state it wrongly is for the artifact to be wrong.
    _sd = _all_cells[1]
    put("d3_second_h", _sd[2]["h"], "results/task_d3_perhorizon.json")
    put("d3_second_q", _sd[1], "results/task_d3_perhorizon.json")
    put("d3_second_dev", f'{100*_sd[0]:.2f}', "results/task_d3_perhorizon.json")
    _side = lambda c: "above" if c["coverage_after"] > D3["target_coverage"] else "below"
    put("d3_worst_side", _side(_w[2]), "results/task_d3_perhorizon.json")
    put("d3_second_side", _side(_sd[2]), "results/task_d3_perhorizon.json")
    put("d3_top2_same_side",
        "both above" if _side(_w[2]) == _side(_sd[2]) == "above" else
        ("both below" if _side(_w[2]) == _side(_sd[2]) == "below" else
         "in opposite directions"),
        "results/task_d3_perhorizon.json")
    _tp = D3["design"]["trajectories_per_episode"]
    put("d3_neps", len(_tp), "results/task_d3_perhorizon.json")
    put("d3_nind_fit", min(_tp.values()), "results/task_d3_perhorizon.json")
    put("d3_nind_tot", sum(_tp.values()), "results/task_d3_perhorizon.json")
    # T2.4 -- the "N of N held-out cells" count is horizons x fold directions on
    # the SAME trajectories, not N independent successes. The caption states the
    # decomposition, so the horizon count has to be derived rather than typed.
    _d3h = sorted({f["h"] for f in D3["quantities"]["epistemic"]["fits"]})
    put("d3_nhoriz", len(_d3h), "results/task_d3_perhorizon.json")

    # --- D3 cross-model: does 6.8's lookup table transfer between MODELS? ----
    # M-69, pre-registered in fad7db7 before any of this existed. Section 6.8's
    # own values are read from its own artifact above and are untouched here;
    # everything below comes from the new one.
    DX = J("task_d3_cross_model.json")
    P4 = J("p4_transfer_power.json")
    _vb = DX["verdict"]["both_directions"]
    put("d3x_verdict", _vb["verdict"], "results/task_d3_cross_model.json")
    put("d3x_branch", _vb["branch"], "results/task_d3_cross_model.json")
    put("d3x_ncells", _vb["n_cells"], "results/task_d3_cross_model.json")
    put("d3x_n_out", _vb["n_intervals_outside_band"], "results/task_d3_cross_model.json")
    put("d3x_n_in", _vb["n_intervals_inside_band"], "results/task_d3_cross_model.json")
    put("d3x_n_strad", _vb["n_intervals_straddling_edge"],
        "results/task_d3_cross_model.json")
    put("d3x_worst_delta", f'{_vb["largest_abs_delta_pts"]:.1f}',
        "results/task_d3_cross_model.json")
    for _d, _tg in (("armA_to_released", "a2r"), ("released_to_armA", "r2a")):
        put(f"d3x_verdict_{_tg}", DX["verdict"][_d]["verdict"],
            "results/task_d3_cross_model.json")
        put(f"d3x_n_out_{_tg}", DX["verdict"][_d]["n_intervals_outside_band"],
            "results/task_d3_cross_model.json")
        put(f"d3x_ncells_{_tg}", DX["verdict"][_d]["n_cells"],
            "results/task_d3_cross_model.json")
    for q, tg in (("aleatoric", "ale"), ("epistemic", "epi")):
        put(f"d3x_{tg}_ok", DX["absolute_column"][q]["cells_within_tolerance"],
            "results/task_d3_cross_model.json")
        put(f"d3x_{tg}_cells", DX["absolute_column"][q]["n_cells"],
            "results/task_d3_cross_model.json")
        put(f"d3x_own_{tg}_ok", DX["armA_own_model"][q]["cells_within_tolerance"],
            "results/task_d3_cross_model.json")
        put(f"d3x_own_{tg}_cells", DX["armA_own_model"][q]["n_cells"],
            "results/task_d3_cross_model.json")
    put("d3x_nseeds", len(DX["seeds"]), "results/task_d3_cross_model.json")
    put("d3x_ens", DX["design"]["ensemble"], "results/task_d3_cross_model.json")
    # §6.8's table names Arm A's checkpoint with {{iters_main}}: assert the artifact is at it.
    assert DX["design"]["iterations"] in _iters["main"], (DX["design"]["iterations"], _iters)
    put("d3x_nind", DX["design"]["n_independent"], "results/task_d3_cross_model.json")
    put("d3x_band", f'{DX["band_pts"]:.0f}', "results/task_d3_cross_model.json")
    put("d3x_ratio_lo", f'{DX["multipliers"]["ratio_min"]:.3g}',
        "results/task_d3_cross_model.json")
    put("d3x_ratio_hi", f'{DX["multipliers"]["ratio_max"]:.3g}',
        "results/task_d3_cross_model.json")
    # The MDE the two columns are read against. The paired one governs; the
    # absolute one does not, and its own figures are why.
    _pm = [v for q in P4["paired_binding_mde_pts"].values() for v in q.values()]
    _um = [v for q in P4["binding_mde_pts"].values() for v in q.values()]
    put("d3x_pmde_hi", f"{max(_pm):.2f}", "results/p4_transfer_power.json")
    put("d3x_umde_lo", f"{min(_um):.2f}", "results/p4_transfer_power.json")
    put("d3x_umde_hi", f"{max(_um):.2f}", "results/p4_transfer_power.json")
    put("d3x_tol_res", P4["summary"]["quantity_horizon_pairs_where_tolerance_resolvable"],
        "results/p4_transfer_power.json")
    put("d3x_tol_pairs", P4["summary"]["quantity_horizon_pairs"],
        "results/p4_transfer_power.json")

    # The lessons section opens by counting its own lessons. It said "Four" while
    # carrying a different number after Part D added two; count the bold leads
    # instead.
    #
    # Bound to the section's TITLE, not its number — exactly as n_defects is, and
    # for exactly the same reason. This used to split on the literal "## 9.", and
    # when Related Work was inserted and the section moved to 10, that split
    # silently returned the METHOD section instead and put its bold-lead count in
    # the lessons sentence. It was caught by the same comment n_defects carries,
    # which is the argument for writing such comments down.
    _lsec = re.search(r"^## (\d+)\. Actionable lessons\s*$", TPL, re.M)
    assert _lsec, "no section titled 'Actionable lessons'"
    _s9 = TPL[_lsec.end():]
    _s9 = _s9[:_s9.find("\n## ")] if "\n## " in _s9 else _s9
    _n9 = len(re.findall(r"^\*\*[A-Z]", _s9, re.M))
    assert _n9 > 0, "the lessons section has no bold-led lessons"
    put("n_lessons", _n9, "PAPER.template.md, Actionable lessons")
    put("n_lessons_word", WORDS.get(_n9, str(_n9)), "PAPER.template.md, Actionable lessons")

    # E4 -- appendix B claimed "roughly 22 hours" for a full run. Recomputed from
    # the top-level wall_clock_s of every training run. (The per-checkpoint
    # wall_clock_s inside `collapse` is elapsed-so-far, not per-interval; summing
    # those inflates the total about 15-fold.)
    import glob as _glob
    _runs = []
    _runs_m49 = []
    for _f in sorted(_glob.glob("results/step5_*.json")):
        _d = json.load(open(_f))
        if _d.get("wall_clock_s"):
            _rec = (_d["hyperparameters"]["iterations"], _d["wall_clock_s"])
            _runs.append(_rec)
            # The CPU budget DOES include these -- they are hours this project
            # spent -- but appendix B says how many of them are the capacity-
            # matched arm rather than the main experiment, so the budget and the
            # experiment are not confused for each other.
            if _d["hyperparameters"].get("rnn_hidden_size", _released_w) != _released_w:
                _runs_m49.append(_rec)
    _t = sum(w for _, w in _runs)
    _t10 = sum(w for i, w in _runs if i == 10000)
    put("rt_runs", len(_runs), "results/step5_*.json")
    put("rt_runs_10k", sum(1 for i, _ in _runs if i == 10000), "results/step5_*.json")
    # C3(rev2), 3.4. These were rounded to whole hours independently, and appendix
    # B then read "46 hours ... 20 for the 6 ten-thousand-iteration runs and 27 for
    # the remaining 20". 20 + 27 = 47. Neither figure was typed and neither was
    # wrong; the presentation was. One decimal makes the parts sum to the total,
    # and the `arithmetic` check asserts that they do on every build.
    put("rt_hours", f"{_t/3600:.1f}", "results/step5_*.json")
    put("rt_hours_10k", f"{_t10/3600:.1f}", "results/step5_*.json")
    put("rt_hours_short", f"{(_t-_t10)/3600:.1f}", "results/step5_*.json")
    put("rt_runs_short", sum(1 for i, _ in _runs if i != 10000), "results/step5_*.json")
    put("rt_runs_m49", len(_runs_m49), "results/step5_*.json")
    put("rt_hours_m49", f"{sum(w for _, w in _runs_m49) / 3600:.1f}", "results/step5_*.json")
    # The capacity-matched hours are a SUBSET of the total, not a further part of
    # it, so the only arithmetic that can pin them is total = matched + released.
    # Appendix B stated the total, its iteration-length split and the matched
    # hours as three independent figures, and nothing asserted that the third sat
    # inside the first. The remainder is put here so the `arithmetic` check has
    # both parts of that partition to add up.
    # THE REMAINDER OF THE DISPLAYED TOTAL, not the rounded true remainder. The
    # paper's sentence says the two parts make the total; rounding each of the
    # three independently does not guarantee that, and once the combined arm's
    # two runs were added it stopped being true -- 1.9 + 48.0 = 49.9 against a
    # stated 49.8, an `arithmetic` failure produced by nothing but rounding. The
    # subtraction is done at the precision the paper prints, so the partition it
    # asserts holds by construction rather than by luck.
    put("rt_hours_released",
        f'{float(N["rt_hours"]["value"]) - float(N["rt_hours_m49"]["value"]):.1f}',
        "results/step5_*.json")

    # B8. Three measured quantities that were TYPED in prose, found by classifying
    # every numeral the template carries rather than by reading (see
    # scripts/typed_numeral_audit.py). "roughly 17 CPU-hours" and "about 1.2 h
    # each" describe runs whose wall clock this project records to the second, and
    # the first was not close: five ens-1 seeds at the iteration count R2 uses cost
    # about a fifth of it.
    _R2d = J("r2_independent_ensemble.json")["design"]
    _r2_iters = _R2d["iterations"]
    _r2_seeds = _R2d["independent_seeds"]
    _r2_shared = _R2d["shared_trunk_seeds"]
    _r2_added = [x for x in _r2_seeds if x not in _r2_shared]
    _seed_h = {}
    for _sd in _r2_seeds:
        _f = f"results/step5_armA_seed{_sd}.json"
        _d = json.load(open(_f))
        assert _d["hyperparameters"]["iterations"] == _r2_iters, (
            f"{_f} ran {_d['hyperparameters']['iterations']} iterations; R2's design "
            f"says {_r2_iters}, so its wall clock does not price R2's ensemble")
        _seed_h[_sd] = _d["wall_clock_s"] / 3600.0
    _mean_h = sum(_seed_h.values()) / len(_seed_h)
    put("r2_n_added", len(_r2_added), "results/r2_independent_ensemble.json")
    put("r2_n_added_word", WORDS.get(len(_r2_added), str(len(_r2_added))).lower(),
        "results/r2_independent_ensemble.json")
    put("r2_added_h", f"{sum(_seed_h[s] for s in _r2_added) / len(_r2_added):.1f}",
        "results/step5_armA_seed*.json")
    put("r2_scratch_h", f"{_mean_h * len(_r2_seeds):.1f}", "results/step5_armA_seed*.json")
    put("r2_added_h_total", f"{sum(_seed_h[s] for s in _r2_added):.1f}",
        "results/step5_armA_seed*.json")

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
    # S8: the pre-submission queue's runtime inputs, beside the rt_* keys above rather than
    # folded into them. Those describe the step5 runs, and Appendix B's prose says the rest of
    # their total is released-width hours, which the architecture baselines are not.
    _PR = J("presubmission_runtime.json")
    put("rt_pre_runs", _PR["n_runs"], "results/presubmission_runtime.json")
    put("rt_pre_hours", f'{_PR["wall_clock_s"]/3600:.1f}', "results/presubmission_runtime.json")
    for _r, _tag in (("M-74", "sweep"), ("M-75", "bl_tf"), ("M-76", "bl_ar")):
        put(f"rt_{_tag}_runs", _PR["by_rule"][_r]["n_runs"], "results/presubmission_runtime.json")
        put(f"rt_{_tag}_hours", f'{_PR["by_rule"][_r]["wall_clock_s"]/3600:.1f}',
            "results/presubmission_runtime.json")
    put("rt_pre_overlapped", _PR["n_runs_overlapped"], "results/presubmission_runtime.json")
    # Appendix B prints the three parts beside the total; they must make it.
    _parts = [_PR["by_rule"][r] for r in ("M-74", "M-75", "M-76")]
    assert len(_PR["by_rule"]) == 3 and sum(x["n_runs"] for x in _parts) == _PR["n_runs"]
    assert abs(sum(x["wall_clock_s"] for x in _parts) - _PR["wall_clock_s"]) < 1e-6

    # Section 5.2 claims the n=4 table "agrees in direction" with the n=20 one.
    # Checked rather than asserted: it does for the epistemic column at all five
    # horizons, and does NOT for the aleatoric column at one of them.
    _B4 = J("task_b2_epistemic.json")
    _agree_e = _agree_a = 0
    # Derived from the horizons BOTH artifacts actually carry, not a typed list.
    # The list was hard-coded to the pre-revision grid and did not follow h=100
    # in, so the sentence said "5 of 5" over a six-horizon table.
    _agree_hs = [_h for _h in D["d1_by_horizon"] if _h in _B4["by_horizon"]]
    _agree_hs.sort(key=int)
    for _h in _agree_hs:
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
    put("agree_nh", len(_agree_hs), "results/task_b2_epistemic.json + task_d_nind20.json")
    # Which horizons the aleatoric column disagrees at, so the sentence naming them
    # cannot go stale the way "it flips sign at h=8" did when h=100 was added.
    _dis = []
    for _h in _agree_hs:
        _x = (_B4["by_horizon"][_h]["aleatoric"]["n_positive"]
              > _B4["by_horizon"][_h]["aleatoric"]["n_finite_corr"] / 2)
        _y = (D["d1_by_horizon"][_h]["aleatoric"]["n_positive"]
              > D["d1_by_horizon"][_h]["aleatoric"]["n_finite_corr"] / 2)
        if _x != _y:
            _dis.append(_h)
    put("agree_alea_dis", " and ".join("h=" + x for x in _dis),
        "results/task_b2_epistemic.json + task_d_nind20.json")
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
    for h in (1, 8, 32, 100, 128, 368):
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
        # C2(rev2), 2.3. This was a typed (1, 8, 32, 128, 368) while the artifact
        # carried the grid, so when h=100 -- the horizon the abstract is anchored
        # to -- was added to the measurement, the paper's permutation column would
        # still have printed "--" for it. Follow the artifact.
        _PH = sorted((int(k) for k in A["models"][next(iter(_ptag))]))
        for _lab, _tg in _ptag.items():
            for _h in _PH:
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
    # C5(rev2), 3.3 / scope-consistency. Section 4 said the eight untested claims
    # were "without exception" about policy learning or hardware, while appendix E
    # says of two of them "no simulator needed" and puts both within CPU reach.
    # Both counts are now derived from the two tables that carry them, so the
    # quantifier in 4 cannot outrun the enumeration two appendices later.
    def _table_rows(section_title):
        """The data rows of the first Markdown table under a section heading."""
        m = re.search(r"^## " + re.escape(section_title) + r".*$", TPL, re.M)
        assert m, f"no section titled {section_title!r}"
        body = TPL[m.end():]
        nxt = body.find("\n## ")
        body = body[:nxt] if nxt > 0 else body
        # The FIRST table only: stop at its first non-table line. Round 3, R6 (ruling V5) put a second
        # table in Appendix D, and collecting every table line in the section read its header as a row.
        rows, started = [], False
        for ln in body.split("\n"):
            if ln.strip().startswith("|"):
                started = True
                rows.append(ln.strip())
            elif started:
                break
        # drop the header and the |---| separator
        return [r for r in rows[2:] if set(r.replace("|", "").strip()) - set("-: ")]

    # B4 renumbered the appendices (D->C ... H->G). The keys keep their old letters
    # (appE_*, appF_*) because they are identifiers, not labels; the headings they
    # are read from are the claims table (now D) and the pricing table (now C).
    _appF = _table_rows("Appendix D")
    _appE = _table_rows("Appendix C")
    _f_tested = [r for r in _appF if re.split(r"(?<!\\)\|", r.strip("|"))[1].strip()
                 .lower().strip("* ") == "yes"]
    _f_untested = [r for r in _appF if r not in _f_tested]
    put("appF_n_claims", len(_appF), "PAPER.template.md, Appendix D table")
    put("n_untested", len(_f_untested), "PAPER.template.md, Appendix D table")
    put("n_untested_word", WORDS.get(len(_f_untested), str(len(_f_untested))).lower(),
        "PAPER.template.md, Appendix D table")
    _e_cpu = [r for r in _appE if "no simulator needed" in r]
    put("appE_n_cpu", len(_e_cpu), "PAPER.template.md, Appendix C table")
    put("appE_n_cpu_word", WORDS.get(len(_e_cpu), str(len(_e_cpu))).lower(),
        "PAPER.template.md, Appendix C table")

    # B3. §4 stated a count of six and then ENUMERATED five. The count came from
    # here; the list was typed. That sentence is the replacement for retracted
    # claim S-17, which was itself a count defect in the same place, so a second
    # count defect in the replacement is worse than the first.
    #
    # Both now come from a `[tag]` at the head of each untested row's verdict cell
    # in Appendix E. The tags also settle a question the enumeration was hiding:
    # "generality across quadruped, humanoid, manipulation" is tagged `model`, not
    # `policy` or `hardware`. It needs a simulator and datasets from other robots,
    # but it is a claim about the MODEL, so the sentence saying all six are about
    # policy learning or hardware was false about one of them even once the count
    # was right.
    def _cell(row, i):
        return re.split(r"(?<!\\)\|", row.strip("|"))[i].strip()

    def _tag(row):
        """`[class, class: short name]` at the head of an untested row's verdict.

        The classes drive §4's counts; the short name is what §4 calls the claim.
        Both live beside the claim rather than in prose, so the enumeration and
        the count cannot disagree with the table or with each other.
        """
        m = re.match(r"`\[([^\]]+)\]`", _cell(row, 3))
        if not m:
            return None
        classes, _, name = m.group(1).partition(":")
        return ([c.strip() for c in classes.split(",")], name.strip())

    def _tags(row):
        t = _tag(row)
        return t[0] if t else []

    def _label(row):
        t = _tag(row)
        assert t and t[1], f"no short name in the tag for: {_cell(row, 0)[:60]}"
        return t[1]

    _untagged = [_label(r) for r in _f_untested if not _tags(r)]
    assert not _untagged, (
        "untested Appendix D rows with no `[tag]` in their verdict cell, so §4's "
        f"count and enumeration cannot be derived from them: {_untagged}")
    _f_cpu = [r for r in _f_untested if "cpu" in _tags(r)]
    # S9: the two claims this tag marked (the M/N sweep and the architecture baselines) were
    # run. §4 now says every untested claim needs a simulator or hardware; that is true only while
    # no untested row carries the `cpu` tag.
    assert not _f_cpu, ("an untested Appendix D row is tagged `cpu`, and §4 says every untested "
                        "claim needs a simulator or hardware: " + ", ".join(_label(r) for r in _f_cpu))
    _f_sim = [r for r in _f_untested if "cpu" not in _tags(r)]
    assert len(_f_cpu) == len(_e_cpu), (
        f"Appendix D tags {len(_f_cpu)} untested claims `cpu` while Appendix C "
        f"prices {len(_e_cpu)} as needing no simulator")
    # Appendix D promises a price for EACH untested claim. It listed six of eight.
    assert len(_appE) == len(_f_untested), (
        f"Appendix C prices {len(_appE)} claims; Appendix D marks {len(_f_untested)} "
        "untested, and Appendix C's own opening says it prices each of them")
    _f_polhw = [r for r in _f_sim if {"policy", "hardware"} & set(_tags(r))]
    _f_model = [r for r in _f_sim if not ({"policy", "hardware"} & set(_tags(r)))]
    _n_sim = len(_f_sim)
    assert _n_sim == len(_f_untested) - len(_e_cpu)
    put("appE_n_sim", _n_sim, "PAPER.template.md, Appendix C + D tables")
    put("appE_n_sim_word", WORDS.get(_n_sim, str(_n_sim)).lower(),
        "PAPER.template.md, Appendix C + D tables")
    put("appF_n_polhw", len(_f_polhw), "PAPER.template.md, Appendix D verdict tags")
    put("appF_n_polhw_word", WORDS.get(len(_f_polhw), str(len(_f_polhw))),
        "PAPER.template.md, Appendix D verdict tags")
    # Same count, lower-cased, for the mid-sentence use in S4. WORDS is capitalised
    # for sentence-initial substitution; dropping it into "then named {{...}}" put
    # "named Five" in the PDF, which reads as a proper noun rather than a count.
    put("appF_n_polhw_lower", WORDS.get(len(_f_polhw), str(len(_f_polhw))).lower(),
        "PAPER.template.md, Appendix D verdict tags")
    put("appF_n_model", len(_f_model), "PAPER.template.md, Appendix D verdict tags")

    def _english(items):
        items = list(items)
        if not items:
            return "none"
        if len(items) == 1:
            return items[0]
        return ", ".join(items[:-1]) + " and " + items[-1]

    put("appF_sim_list", _english(_label(r) for r in _f_sim),
        "PAPER.template.md, Appendix D verdict tags")
    put("appF_polhw_list", _english(_label(r) for r in _f_polhw),
        "PAPER.template.md, Appendix D verdict tags")
    put("appF_model_list", _english(_label(r) for r in _f_model),
        "PAPER.template.md, Appendix D verdict tags")
    put("appF_cpu_list", _english(_label(r) for r in _f_cpu),
        "PAPER.template.md, Appendix D verdict tags")

    # A6 -- what the originals report for each claim we tested
    OP = J("original_paper_figures.json")
    put("orig_n_tested", OP["n_tested_claims"], "results/original_paper_figures.json")
    put("orig_n_tested_word", WORDS[OP["n_tested_claims"]].lower(), "results/original_paper_figures.json")
    assert len(_f_tested) == OP["n_tested_claims"], (
        f"Appendix D marks {len(_f_tested)} claims tested; "
        f"original_paper_figures.json says {OP['n_tested_claims']}")
    put("orig_n_without", OP["n_without"], "results/original_paper_figures.json")
    put("orig_n_without_word", WORDS[OP["n_without"]].lower(), "results/original_paper_figures.json")
    put("orig_n_with", OP["n_with_quantitative_figure"], "results/original_paper_figures.json")
    _se = OP["sample_efficiency"]["figures"]
    put("orig_se_rwm", _se["RWM pretraining state transitions"],
        "results/original_paper_figures.json")
    put("orig_se_ppo", _se["PPO state transitions"], "results/original_paper_figures.json")
    put("orig_se_rwm_rew", _se["MBPO-PPO real tracking reward"],
        "results/original_paper_figures.json")
    put("orig_se_ppo_rew", _se["PPO real tracking reward"],
        "results/original_paper_figures.json")
    put("perm_ngroups", PM["arenas"]["out-of-sample"]["models"]["released EPISTEMIC"]["368"]["n_groups"],
        "results/task_b_permutation.json")
    # How many horizons the epistemic permutation column of 6.2 actually reports.
    # 6.2 said "these are five tests on one family" over what is now a six-row
    # column; a typed count under a generated table is the defect this whole
    # build exists to prevent.
    _nperm_h = len(PM["arenas"]["all-episodes"]["models"]["released EPISTEMIC"])
    put("perm_n_tests_col", _nperm_h, "results/task_b_permutation.json")
    put("perm_n_tests_col_word", WORDS.get(_nperm_h, str(_nperm_h)).lower(),
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
    _nulls = [PM["arenas"][a]["models"][l][h]["null_mean"]
              for a in PM["arenas"] for l in _ptag
              for h in PM["arenas"][a]["models"][l]]
    # B8. "rates differing by about 5x" in §8's assumption table was typed; the
    # artifact that computes both rates also computes their ratio.
    put("o12_rate_ratio", f'{J("step6_3_min_logstd.json")["rate_ratio"]:.1f}',
        "results/step6_3_min_logstd.json")
    put("perm_faircoin", f'{PM["arenas"]["in-sample"]["models"]["teacher-forced armB"]["368"]["n_dims"] / 2:g}',
        "results/task_b_permutation.json")
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
    # The SAME comparison under the metric the abstract's other headline uses.
    # §7.2's figure is nRMSE at h = 368 and nothing else -- 50.9% at h = 1, 10.9%
    # at h = 128 -- and the abstract quoted it with neither scope, so a reviewer
    # computing on relative-L1 would have got a number eight times smaller and
    # concluded the abstract was wrong. Both are printed now, in the sentence that
    # claims every abstract headline names its metric.
    put("stale_pct_rel", f'{100*(_r15["A_off0"]["e"]/_r15["A_off1"]["e"]-1):.1f}',
        "results/step4_0a_results.json")

    # Pre-submission S3, item 4 (S-20; ruling "Restate on independent"). The same defect on
    # independent trajectories, with 95% cluster-bootstrap intervals and both pairings inside
    # each draw. stale_pct / stale_pct_rel above now appear only where §7.2 withdraws them.
    _ad = J("alignment_defect_ci.json")["arenas"]
    _h4, _h20, _pa = _ad["held_out_n4"], _ad["all_ten_n20"], _ad["protocol_a"]
    _src = "results/alignment_defect_ci.json"
    _ci = lambda c: f"[{c[0]:.1f}, {c[1]:.1f}]"
    put("ad_nind", _h4["n_trajectories"], _src)
    put("ad20_nind", _h20["n_trajectories"], _src)
    for _tag, _a in (("ad", _h4), ("ad20", _h20)):
        put(f"{_tag}_rel", f'{_a["overstatement_pct"]["rel_l1"]:.1f}', _src)
        put(f"{_tag}_rel_ci", _ci(_a["ci95_pct"]["rel_l1"]), _src)
        put(f"{_tag}_nrmse", f'{_a["overstatement_pct"]["nrmse_form1"]:.1f}', _src)
        put(f"{_tag}_nrmse_ci", _ci(_a["ci95_pct"]["nrmse_form1"]), _src)
    _pt = _h4["per_trajectory_overstatement_pct"]
    put("ad_rel_traj", ", ".join(f"{x:+.1f}%" for x in _pt["rel_l1"]), _src)
    put("ad_nrmse_traj", ", ".join(f"{x:+.1f}%" for x in _pt["nrmse_form1"]), _src)
    _p20 = _h20["per_trajectory_overstatement_pct"]["rel_l1"]
    put("ad20_traj_lo", f"{min(_p20):+.1f}", _src)
    put("ad20_traj_hi", f"{max(_p20):+.1f}", _src)
    _pn = _pa["per_trajectory_overstatement_pct"]["nrmse_form1"]
    _k = max(range(len(_pn)), key=lambda i: _pn[i])
    put("ad_pa_n", _pa["n_trajectories"], _src)
    put("ad_pa_out_row", f'{_pa["starts"][_k]:,}', _src)

    # Round 2, T3 (E1, ruling A; ledger R-76): the defect at h = 1 on the held-out pair, and our
    # Arm A's sensitivity to the stale pairing (10,000 iterations, 3-seed mean, relative-L1).
    _ah = J("alignment_by_horizon.json")
    _src2 = "results/alignment_by_horizon.json"
    _r1 = _ah["released"]["summary"]["held_out_n4"]["1"]["rel_l1"]
    put("adh_rel_h1", f'{_r1["pct"]:.1f}', _src2)
    put("adh_rel_ci_h1", _ci(_r1["ci95_pct"]), _src2)
    # ...and at the method's own horizon, so "concentrated at short horizons" can be checked from
    # the paper (T3 review F8). The horizon is read from the artifact that names it, not typed.
    _hd = str(J("v2_deployment_horizon.json")["verdict"]["deployment_horizon_is"])
    _rd = _ah["released"]["summary"]["held_out_n4"][_hd]["rel_l1"]
    put("adh_rel_h100", f'{_rd["pct"]:.1f}', _src2)
    put("adh_rel_ci_h100", _ci(_rd["ci95_pct"]), _src2)
    _am =_ah["arm_a"]["10000"]["summary_three_seed_mean_pct"]
    put("stale_armA_rel_h1", f'{_am["1"]["rel_l1"]:+.2f}', _src2)
    put("stale_armA_rel_h368", f'{_am["368"]["rel_l1"]:+.2f}', _src2)

    # --- Round 3, R3 (Annex 2 E2): the released checkpoint's stale-action cost over all ten episodes ----------------
    # The h = 368 cells stay ad20_* / ad_* (alignment_defect_ci.json, which N1 reproduces to 1e-9); h = 1..100 are N1's.
    _t20, _h4s = _ah["released"]["summary"]["all_ten_n20"], _ah["released"]["summary"]["held_out_n4"]
    assert _ah["released"]["reproduces_alignment_defect_ci_at_h368"]["all_ten_n20"]["reproduced"]
    assert _hd == "100"
    for _h in ("1", "8", "32", "100"):
        for _m, _tg in (("rel_l1", "rel"), ("nrmse_form1", "nrmse")):
            put(f"adh20_{_tg}_h{_h}", f'{_t20[_h][_m]["pct"]:.1f}', _src2)
            put(f"adh20_{_tg}_ci_h{_h}", _ci(_t20[_h][_m]["ci95_pct"]), _src2)
    # What contribution 7, section 3.1 (A8), section 7.2 and the 3.2 row say, asserted: over all ten episodes
    # relative-L1 resolves a rise at h = 1, 8 and 32 and nothing from h = 100; nRMSE resolves a rise at 8 and 32, not
    # at 1, and nothing from 100; on the held-out pair both metrics resolve a rise at every horizon.
    _exz = lambda c: c[0] > 0 or c[1] < 0
    for _h in map(str, _ah["horizons"]):
        _r, _n = _t20[_h]["rel_l1"]["ci95_pct"], _t20[_h]["nrmse_form1"]["ci95_pct"]
        if int(_h) <= 32:
            assert _r[0] > 0 and (_n[0] > 0) == (_h != "1") and not (_h == "1" and _exz(_n)), _h
        else:
            assert not _exz(_r) and not _exz(_n), _h
        assert all(_h4s[_h][_m]["ci95_pct"][0] > 0 for _m in ("rel_l1", "nrmse_form1")), _h

    # --- Round 3, R3 (Annex 2 E3): rule X2 (M-84, discharged in M-85) -----------------------------------------------
    X2 = J("action_sensitivity.json")
    _x2s = "results/action_sensitivity.json"
    _rdx = X2["readings"]
    assert {v["reading"] for v in _rdx.values()} == {"RESPONDS TO THE ACTION"}, "the text installed is case R"
    put("x2_reading", _rdx["arm_a_10000"]["reading"], _x2s)
    _pc = lambda x: f"{x:+.1f}"
    _pci = lambda c: f"[{c[0]:+.1f}, {c[1]:+.1f}]"
    for _it, _tg in (("2500", "2500"), ("10000", "10k")):
        put(f"x2_E_swap_{_tg}", _pc(_rdx[f"arm_a_{_it}"]["E_pct"]), _x2s)
        put(f"x2_ci_swap_{_tg}", _pci(_rdx[f"arm_a_{_it}"]["ci95_pct"]), _x2s)
    put("x2_n_ins", X2["arenas"]["in_sample_n16"]["n_independent"], _x2s)
    assert X2["arenas"]["held_out_n4"]["starts"] == list(J("alignment_defect_ci.json")["arenas"]["held_out_n4"]["starts"])
    _cx = X2["context"]["in_sample_n16"]
    put("x2_ctx_stale", f'{_cx["one_step_shift_over_spread"]:.2f}', _x2s)
    put("x2_ctx_swap", f'{_cx["swap_over_spread"]:.2f}', _x2s)
    _s1 = X2["results"]["arm_a_10000"]["in_sample_n16"]["1"]["I1_stale"]
    assert _s1["ci95_pct"][0] > 0, "section 7.2 says the in-sample stale cost at h = 1 is a resolved rise"
    put("x2_E_stale_10k_ins_h1", _pc(_s1["E_pct"]), _x2s)
    put("x2_ci_stale_10k_ins_h1", _pci(_s1["ci95_pct"]), _x2s)
    # X2's held-out I1 figures are N1's, re-measured (R-79): the same numbers stale_armA_* print
    assert abs(X2["results"]["arm_a_10000"]["held_out_n4"]["1"]["I1_stale"]["E_pct"] - _am["1"]["rel_l1"]) < 1e-6
    # Appendix V: every cell, generated
    _MODELS = (("arm_a_2500", "Arm A, {}".format(N["iters_main"]["value"])), ("arm_a_10000", "Arm A, {}".format(N["iters_long"]["value"])),
               ("arm_b_2500", "Arm B, {} (alongside)".format(N["iters_main"]["value"])),
               ("arm_b_10000", "Arm B, {} (alongside)".format(N["iters_long"]["value"])),
               ("released", "released checkpoint (alongside)"))
    _INTV = (("I1_stale", "stale action"), ("I2_swap", "another trajectory's actions"), ("I3_mean", "training mean"),
             ("I4_noise_k0.1", "noise, k = 0.1"), ("I4_noise_k0.5", "noise, k = 0.5"))
    _XH = ("1", "8", "32", "100")
    _own = {"arm_a_2500": "in_sample_n16", "arm_a_10000": "in_sample_n16", "arm_b_2500": "in_sample_n16",
            "arm_b_10000": "in_sample_n16", "released": "all_ten_n20"}

    def _x2tab(arena_of):
        rows = []
        for _k, _lab in _MODELS:
            for _i, _il in _INTV:
                cells = []
                for _h in _XH:
                    _c = X2["results"][_k][arena_of(_k)][_h][_i]
                    _s = f'{_pc(_c["E_pct"])} {_pci(_c["ci95_pct"])}'
                    cells.append(f"**{_s}**" if (_k in X2["readings"] and _i == "I2_swap" and _h == "8"
                                                 and arena_of(_k) == "in_sample_n16") else _s)
                rows.append(f"| {_lab} | {_il} | " + " | ".join(cells) + " |")
        return "\n".join(rows)
    put("x2_appV_own", _x2tab(lambda k: _own[k]), _x2s)
    put("x2_appV_ho", _x2tab(lambda k: "held_out_n4"), _x2s)
    _drows = []
    for _k, _lab in _MODELS:
        for _arn, _al in ((_own[_k], "own training data"), ("held_out_n4", "held-out pair")):
            _drows.append(f"| {_lab} | {_al} | " + " | ".join(
                f'{X2["results"][_k][_arn]["8"][_i]["delta"]:.3f}' for _i, _ in _INTV) + " |")
    put("x2_appV_delta", "\n".join(_drows), _x2s)
    # the bootstrap's resample counts, printed in Appendices U and V: N1's own counts, which both artifacts' interval
    # descriptions must state
    _nex = _ah["released"]["full"]["held_out_n4"]["1"]["n_resamples"]
    _nmc = _ah["released"]["full"]["all_ten_n20"]["1"]["n_resamples"]
    assert (_nex, _nmc) == (4 ** 4, 20000), (_nex, _nmc)
    for _desc in (X2["interval"], J("mn_compute_matched.json")["part3_readings"]["interval"]):
        assert f"exact {_nex}" in _desc and f"{_nmc:,}" in _desc, _desc
    put("boot_n_exact4", f"{_nex:,}", _src2)
    put("boot_n_mc", f"{_nmc:,}", _src2)
    _ks = sorted(float(k.split("_k")[1]) for k in X2["interventions"] if k.startswith("I4_noise_k"))
    assert len(_ks) == 2, _ks
    put("x2_k_lo", f"{_ks[0]:g}", _x2s)
    put("x2_k_hi", f"{_ks[1]:g}", _x2s)
    for _arn, _tg in (("in_sample_n16", "ins"), ("held_out_n4", "ho"), ("all_ten_n20", "ten")):
        _c = X2["context"][_arn]
        put(f"x2_ctx_{_tg}_frac", f'{100 * _c["fraction_of_steps_with_changed_action"]:.0f}', _x2s)
        put(f"x2_ctx_{_tg}_stale", f'{_c["one_step_shift_over_spread"]:.2f}', _x2s)
        put(f"x2_ctx_{_tg}_swap", f'{_c["swap_over_spread"]:.2f}', _x2s)

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
    # C3(rev2), 3.9. This printed 68.3 while 3.1 derives and everything else quotes
    # 68.27, so the paper carried two numeric strings for one constant. The
    # recalibration artifact stores its own target to fewer places; assert the two
    # agree and then quote V3's, which is the one 3.1 derives.
    _nom1 = f'{100 * J("v3_metric_definitions.json")["coverage"]["nominal"]["pm1"]:.2f}'
    assert abs(100 * _d2["target_coverage"] - float(_nom1)) < 0.05, \
        "the recalibration target and the derived nominal coverage disagree"
    put("d2_target", _nom1, "results/v3_metric_definitions.json")

    # E2: magnitude collapse is objective-driven, input-independence is arm-driven
    import glob as _g, statistics as _st
    _mse, _nll_s = [], []
    for _f in sorted(_g.glob("results/step5_arm*.json")):
        if "_10k" in _f:
            continue
        # Released architecture only. §6.3 reports one collapse rate and calls it
        # nearly identical across runs; a run at another width is a different
        # experiment and belongs to §6.10, not here.
        if _width(_f) != _released_w:
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
    _all = len([f for f in _g.glob("results/step5_arm*.json")
                if _width(f) == _released_w])
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
    put("d1_rule_h", _d1["rule_horizon"], "results/task_d1_threeseed.json")
    # C1(rev2), 2.2. The A/B comparison at the DEPLOYMENT horizon, beside the
    # pre-registered figure at h=368. M-23 is stated over h=368 and its verdict is
    # untouched; this is the same measurement at the horizon the rest of the paper
    # is anchored to, and it is materially smaller. The abstract quoted 4.61x with
    # no horizon at all, in a revision whose central move was horizon labelling.
    for _hh, _hk in ((_d1["horizons"][0], "h100"),):
        _bh = _d1["by_horizon"][str(_hh)]
        put(f"d1_ratio_{_hk}", f'{_bh["ratio_B_over_A"]:.2f}',
            "results/task_d1_threeseed.json")
        put(f"d1_A_mean_{_hk}", f'{_bh["A"]["mean"]:.4f}', "results/task_d1_threeseed.json")
        put(f"d1_A_sd_{_hk}", f'{_bh["A"]["sd_ddof1"]:.4f}', "results/task_d1_threeseed.json")
        put(f"d1_B_mean_{_hk}", f'{_bh["B"]["mean"]:.4f}', "results/task_d1_threeseed.json")
        put(f"d1_B_sd_{_hk}", f'{_bh["B"]["sd_ddof1"]:.4f}', "results/task_d1_threeseed.json")
    # --- A1: the A/B result across the whole horizon grid --------------------
    # 5 led with h=368 while 3.1 says h=368 is not a deployment horizon, and the
    # same comparison at h=100 is 2.58x. As a line item that reads as horizon
    # shopping; as a curve it is a finding, because the advantage GROWS with
    # horizon and h=368 is the end of a trend. Everything here except h=368 was
    # computed after the data existed and carries no pre-registration weight.
    A1 = J("a1_ab_by_horizon.json")
    _a1h = A1["design"]["horizons"]
    for _h in _a1h:
        _r = A1["by_horizon"][str(_h)]
        put(f"a1_ratio_h{_h}", f'{_r["ratio_B_over_A"]:.2f}', "results/a1_ab_by_horizon.json")
        put(f"a1_A_h{_h}", f'{_r["A"]["mean"]:.4f}', "results/a1_ab_by_horizon.json")
        put(f"a1_A_sd_h{_h}", f'{_r["A"]["sd_ddof1"]:.4f}', "results/a1_ab_by_horizon.json")
        put(f"a1_B_h{_h}", f'{_r["B"]["mean"]:.4f}', "results/a1_ab_by_horizon.json")
        put(f"a1_B_sd_h{_h}", f'{_r["B"]["sd_ddof1"]:.4f}', "results/a1_ab_by_horizon.json")
        put(f"a1_gap_h{_h}", f'{_r["gap"]:+.4f}', "results/a1_ab_by_horizon.json")
        put(f"a1_gap_ci_h{_h}", f'[{_r["gap_ci"][0]:+.4f}, {_r["gap_ci"][1]:+.4f}]',
            "results/a1_ab_by_horizon.json")
        put(f"a1_excl_h{_h}", "yes" if _r["gap_excludes_zero"] else "no",
            "results/a1_ab_by_horizon.json")
        put(f"a1_floor_h{_h}", f'{_r["floor"]:.4f}', "results/a1_ab_by_horizon.json")
        put(f"a1_floor_over_A_h{_h}", f'{_r["floor_over_A"]:.1f}',
            "results/a1_ab_by_horizon.json")
        put(f"a1_B_over_floor_h{_h}", f'{_r["B_over_floor"]:.2f}',
            "results/a1_ab_by_horizon.json")
        # Round 3, R4 (S12): the table states both arms as error / floor (below 1 beats the floor)
        assert abs(_r["A"]["mean"] / _r["floor"] - 1 / _r["floor_over_A"]) < 1e-6, _h  # float32 in the artifact
        assert abs(_r["B"]["mean"] / _r["floor"] - _r["B_over_floor"]) < 1e-6, _h
        put(f"a1_A_over_floor_h{_h}", f'{_r["A"]["mean"] / _r["floor"]:.2f}',
            "results/a1_ab_by_horizon.json")
        _sg = A1["sign_test"][str(_h)]
        put(f"a1_sign_pos_h{_h}", _sg["n_positive"], "results/a1_ab_by_horizon.json")
        put(f"a1_sign_n_h{_h}", _sg["n_episodes"], "results/a1_ab_by_horizon.json")
        put(f"a1_sign_p_h{_h}", f'{_sg["exact_two_sided_p"]:.4f}',
            "results/a1_ab_by_horizon.json")
    # E8. The four trajectory values behind every n_independent = 4 interval.
    #
    # A cluster bootstrap over four units has 256 distinct resamples, quantised
    # tails and poor coverage. The paper says all three and prints the interval
    # anyway, which asks a reader to accept a summary of four numbers instead of
    # the four numbers. They are more informative than the interval -- at
    # h = 368 one trajectory carries most of the gap, which no interval shows --
    # and printing them pre-empts the objection rather than inviting it.
    for _h in _a1h:
        _g = A1["by_horizon"][str(_h)].get("gap_per_trajectory")
        if _g:
            put(f"a1_gap_traj_h{_h}",
                ", ".join(f"{v:+.4f}" for v in sorted(_g, reverse=True)),
                "results/a1_ab_by_horizon.json")
            put(f"a1_gap_traj_max_h{_h}", f"{max(_g):+.4f}",
                "results/a1_ab_by_horizon.json")
            put(f"a1_gap_traj_min_h{_h}", f"{min(_g):+.4f}",
                "results/a1_ab_by_horizon.json")
            put(f"a1_gap_traj_n_positive_h{_h}", sum(1 for v in _g if v > 0),
                "results/a1_ab_by_horizon.json")
            put(f"a1_gap_traj_n_h{_h}", len(_g), "results/a1_ab_by_horizon.json")

    _t = A1["trend"]
    put("a1_monotone", "does" if _t["monotone_increasing"] else "does not",
        "results/a1_ab_by_horizon.json")
    put("a1_n_excl", _t["n_excluding_zero"], "results/a1_ab_by_horizon.json")
    put("a1_n_horizons", _t["n_horizons"], "results/a1_ab_by_horizon.json")
    put("a1_spans_zero_at", " and ".join(f"h={h}" for h in _t["spans_zero_at"]) or "no horizon",
        "results/a1_ab_by_horizon.json")
    put("a1_nind", A1["design"]["n_independent"], "results/a1_ab_by_horizon.json")
    # Where teacher forcing loses to the trivial baseline, and where the trained
    # arm does. The second is the one nobody had looked at: at one step the
    # hold-last floor beats BOTH arms, and 5 quoted the h=368 margin as if it
    # held everywhere.
    _bwf = [h for h in _a1h if A1["by_horizon"][str(h)]["B_worse_than_floor"]]
    _awf = [h for h in _a1h if A1["by_horizon"][str(h)]["floor_over_A"] < 1]
    put("a1_B_worse_than_floor_at",
        "every horizon" if len(_bwf) == len(_a1h)
        else (" and ".join(f"h={h}" for h in _bwf) or "no horizon"),
        "results/a1_ab_by_horizon.json")
    put("a1_A_worse_than_floor_at",
        " and ".join(f"h={h}" for h in _awf) or "no horizon",
        "results/a1_ab_by_horizon.json")
    put("a1_n_A_worse_than_floor", len(_awf), "results/a1_ab_by_horizon.json")

    # Head-to-head absolute accuracy: the released checkpoint against the from-scratch
    # arms, one arena, both aggregations. Every cell of the table is a key here; the
    # verdict keys name horizons rather than restate a comparison, because the two
    # aggregations have inverted a released-checkpoint comparison before (Appendix H).
    H2 = J("head_to_head_accuracy.json")
    _h2src = "results/head_to_head_accuracy.json"
    for _row in H2["rows"]:
        for _h in H2["horizons"]:
            _c = H2["rows"][_row]["cells"][str(_h)]
            put(f"h2h_{_row}_nrmse_h{_h}", f'{_c["nrmse"]:.4f}', _h2src)
            put(f"h2h_{_row}_l1_h{_h}", f'{_c["l1"]:.4f}', _h2src)
    put("h2h_arena", H2["arena"], _h2src)
    put("h2h_episodes", " and ".join(str(e) for e in H2["arena_episodes"]), _h2src)
    put("h2h_ntraj", H2["n_trajectories"], _h2src)
    put("h2h_nind", H2["n_independent"], _h2src)
    put("h2h_unit", H2["unit_length"], _h2src)
    put("h2h_nseeds", len(H2["arm_seeds"]), _h2src)
    put("h2h_arm_ckpt", H2["arm_checkpoint"], _h2src)

    def _hs(hs):
        return " and ".join(f"h = {h}" for h in hs) or "no horizon"
    put("h2h_released_sweeps_at", _hs(H2["released_leads_both_metrics_at"]), _h2src)
    put("h2h_armA_sweeps_at", _hs(H2["armA_leads_both_metrics_at"]), _h2src)
    put("h2h_split_at", _hs(H2["metrics_disagree_at"]), _h2src)
    put("h2h_ckpt_neps_word", WORDS[H2["released_ckpt_trained_on_n_episodes"]].lower(), _h2src)

    # --- S9: rules M-74 (the M/N sweep) and M-75/M-76 (the architecture baselines) ---------
    # Every figure is read from the verdict and evaluation artifacts S8 wrote. The governing
    # statistic is relative-L1 at h = 368 on §5's four held-out trajectories; values are the
    # mean over three seeds of each seed's mean over the four trajectories, which is exactly the
    # head-to-head table's definition -- asserted below on RWM, whose rows must coincide.
    MV, ME = J("mn_sweep_verdict.json"), J("mn_sweep_eval.json")
    BV, BE = J("baselines_verdict.json"), J("baselines_eval.json")
    PR = J("presubmission_runtime.json")
    _mvs, _bvs = "results/mn_sweep_verdict.json", "results/baselines_verdict.json"
    # Round 2, T4 (Annex 2 E2, E6, E7): the tables' cost column is N3's cost per iteration relative to
    # the centre (wall-clock hours move to Appendix B); the nRMSE readings quoted alongside the rules are
    # N2's pooled ones (section 3.1's aggregation); a diverged row is marked by N2's flag.
    N3, N2R, N2A = J("mn_compute_matched.json"), J("pooled_nrmse_rescore.json"), J("pooled_nrmse_alongside.json")
    _n3s, _n2s, _n2as = ("results/mn_compute_matched.json", "results/pooled_nrmse_rescore.json",
                         "results/pooled_nrmse_alongside.json")
    _cost = N3["part1_relative_cost_per_iteration"]
    assert _cost["sweep"]["M32_N8"]["relative_to_centre"] == 1.0
    _div = set(N2R["diverged_flag"]["flagged"])
    assert _div == {k for k, v in N2R["diverged_flag"]["rows"].items() if v["diverged"]}

    def _pooled(rule, arena, key, committed):
        """An nRMSE reading the rule quotes alongside, as N2 pooled it; a relative-L1 one as committed.
        N2 reproduced every committed reading before pooling (its D machinery assert), so only the
        statistic differs."""
        if not key.startswith("nrmse"):
            return committed
        p = N2A["readings"][rule][f"{arena}|{key}"]["pooled"]
        pk = p["per_key"]
        return {"branch": p["result"],
                "conditions": {"configs_excluding_zero_in_their_favour": [c for c, x in pk.items() if x["rejected"] and x["D"] < 0],
                               "configs_excluding_zero_in_centre_favour": [c for c, x in pk.items() if x["rejected"] and x["D"] > 0]}}
    _al74 = {k: _pooled("M-74", "held_out", k, v) for k, v in MV["alongside"].items()}
    _in74 = {k: _pooled("M-74", "in_sample", k, v) for k, v in MV["in_sample"].items()}

    def _m3(cfg, h, m="l1", arena="held_out"):
        return float(np.mean([np.mean(cfg["seeds"][s][arena][str(h)][m]) for s in cfg["seeds"]]))

    for _h in H2["horizons"]:
        _d = abs(_m3(BE["configs"]["rwm"], _h) - H2["rows"]["armA"]["cells"][str(_h)]["l1"])
        assert _d < 1e-6, ("baselines_eval's RWM relative-L1 no longer reproduces the head-to-head "
                           f"table's Arm A row at h={_h}: {_d}")
    assert ME["checkpoint_iterations"] == BE["checkpoint_iterations"] == int(N["iters_main"]["value"].replace(",", ""))
    _cfgname = lambda c: f"({c[1:].split('_N')[0]}, {c.split('_N')[1]})"
    _mg = MV["governing"]
    _order = ["M32_N8", "M1_N8", "M2_N8", "M8_N8", "M16_N8", "M32_N1", "M32_N2", "M32_N16", "M32_N32"]
    assert sorted(_order[1:]) == sorted(_mg["per_config"]), sorted(_mg["per_config"])
    _res = lambda r: ("**configuration better**" if r["rejected"] and r["direction"] == "config"
                      else "centre better" if r["rejected"] else "not resolved")
    _rows = []
    for _c in _order:
        _cf = ME["configs"][_c]
        assert _c not in _div, f"{_c} is flagged diverged; mark it in section 5.2's table"
        _hrs = f'{_cost["sweep"][_c]["relative_to_centre"]:.2f}'
        if _c == "M32_N8":
            _rows.append(f"| **{_cfgname(_c)}**, the centre | {_m3(_cf, 100):.4f} | **{_m3(_cf, 368):.4f}** | — | — | {_hrs} |")
            continue
        _r = _mg["per_config"][_c]
        _rows.append(f"| {_cfgname(_c)} | {_m3(_cf, 100):.4f} | {_m3(_cf, 368):.4f} | "
                     f"{_r['D']:+.4f} [{_r['ci95'][0]:+.4f}, {_r['ci95'][1]:+.4f}] | {_res(_r)} | {_hrs} |")
    put("mn_table", "\n".join(_rows), "results/mn_sweep_eval.json + " + _mvs + " + " + _n3s)
    put("mn_verdict", MV["verdict"], _mvs)
    put("mn_n_configs", _mg["m"], _mvs)
    put("mn_n_configs_word", WORDS[_mg["m"]].lower(), _mvs)
    _eng = lambda xs: (", ".join(xs[:-1]) + " and " + xs[-1]) if len(xs) > 1 else (xs[0] if xs else "none")
    _cond = _mg["conditions"]
    put("mn_better_list", _eng([_cfgname(c) for c in _cond["configs_excluding_zero_in_their_favour"]]), _mvs)
    put("mn_n_better_word", WORDS[len(_cond["configs_excluding_zero_in_their_favour"])].lower(), _mvs)
    put("mn_worse_list", _eng([_cfgname(c) for c in _cond["configs_excluding_zero_in_centre_favour"]]), _mvs)
    _unres = [c for c in _order[1:] if not _mg["per_config"][c]["rejected"]]
    put("mn_unres_list", _eng([_cfgname(c) for c in _unres]), _mvs)
    _l368 = {c: _m3(ME["configs"][c], 368) for c in _order}
    _best = min(_l368, key=_l368.get)
    put("mn_best_config", _cfgname(_best), "results/mn_sweep_eval.json")
    put("mn_best_l1_h368", f"{_l368[_best]:.4f}", "results/mn_sweep_eval.json")
    put("mn_centre_l1_h368", f"{_l368['M32_N8']:.4f}", "results/mn_sweep_eval.json")
    # S10 (user ruling D5): the teacher-forcing claim is quantitative -- Fig. 6 prints its
    # N = 1 row -- so §4 and Appendix D set the original's printed cells beside our sweep's.
    _tfp = next(c for c in J("original_paper_figures.json")["claims"] if c["key"] == "tf_poor")
    assert _tfp["numeral_in_text"] and set(_tfp["printed_e"]) == {"M32_N1", "M32_N8"}
    _ofs = "results/original_paper_figures.json"
    put("orig_tf_e_n1", f'{_tfp["printed_e"]["M32_N1"]:.2f}', _ofs)
    put("orig_tf_e_centre", f'{_tfp["printed_e"]["M32_N8"]:.2f}', _ofs)
    put("orig_tf_ratio", f'{_tfp["printed_e"]["M32_N1"] / _tfp["printed_e"]["M32_N8"]:.1f}', _ofs)
    put("mn_n1_label", _cfgname("M32_N1"), "results/mn_sweep_eval.json")
    assert _l368["M32_N1"] > _l368["M32_N8"], "§4 says the sweep's (32, 1) is worse"
    put("mn_tf_ratio", f"{_l368['M32_N1'] / _l368['M32_N8']:.2f}", "results/mn_sweep_eval.json")
    put("mn_best_D", f"{_mg['per_config'][_best]['D']:+.4f}", _mvs)
    put("mn_best_ci", f"[{_mg['per_config'][_best]['ci95'][0]:+.4f}, {_mg['per_config'][_best]['ci95'][1]:+.4f}]", _mvs)
    put("mn_floor_h100", f'{MV["hold_last_floor_l1"]["held_out"]["100"]:.4f}', _mvs)
    put("mn_floor_h368", f'{MV["hold_last_floor_l1"]["held_out"]["368"]:.4f}', _mvs)
    put("mn_mde_h368", f'{MV["mde_pct_of_centre_holm_step_1"]["l1_h368"]:.1f}', _mvs)
    _lab = lambda k: ("relative-L1" if k.split("_h")[0] == "l1" else "nRMSE") + " at h = " + k.split("_h")[1]
    _other = [f"{_lab(k)}, which returns {v['branch']}" for k, v in _al74.items() if v["branch"] != MV["verdict"]]
    put("mn_alongside_other", _eng(_other), _mvs + " + " + _n2as)
    put("mn_n_alongside", len(MV["alongside"]), _mvs)
    _ins_other = [f"{_lab(k)} ({v['branch']})" for k, v in _in74.items() if v["branch"] != MV["verdict"]]
    put("mn_insample_clause",
        f"all {WORDS[len(_in74)].lower()} readings there return the same verdict"
        if not _ins_other else "the readings there differ at " + _eng(_ins_other), _mvs + " + " + _n2as)
    _al_other = [f"{_lab(k)}, which returns {v['branch']}" for k, v in _al74.items()
                 if v["branch"] != MV["verdict"]]
    put("mn_alongside_clause", "every one agrees" if not _al_other
        else "every one agrees except " + _eng(_al_other), _mvs + " + " + _n2as)
    put("mn_nind", ME["arenas"]["held_out"]["n_independent"], "results/mn_sweep_eval.json")
    put("mn_nind_ins", ME["arenas"]["in_sample"]["n_independent"], "results/mn_sweep_eval.json")
    assert BE["arenas"]["held_out"]["n_independent"] == ME["arenas"]["held_out"]["n_independent"]
    # §5.2 prints the head-to-head table's arena label and episodes for this arena.
    assert sorted(ME["arenas"]["held_out"]["episodes"]) == sorted(H2["arena_episodes"]), "§5.2's arena is not §5's"
    assert sorted(BE["arenas"]["held_out"]["episodes"]) == sorted(H2["arena_episodes"]), "§5.3's arena is not §5's"
    # ... and its trajectory count and unit, which §5.2 and §5.3 print from the h2h keys.
    assert ME["arenas"]["held_out"]["n_independent"] == H2["n_independent"] == len(ME["arenas"]["held_out"]["starts"]) == H2["n_trajectories"]
    assert all(r[1] - s + 1 == H2["unit_length"] for s, r in zip(ME["arenas"]["held_out"]["starts"], ME["arenas"]["held_out"]["forecast_rows"]))
    assert all(r[1] - s + 1 == H2["unit_length"] for s, r in zip(ME["arenas"]["in_sample"]["starts"], ME["arenas"]["in_sample"]["forecast_rows"]))
    put("mn_seeds_word", WORDS[len(ME["seeds"])].lower(), "results/mn_sweep_eval.json")
    _cen = ME["configs"]["M32_N8"]
    _Ms = sorted(ME["configs"][c]["M"] for c in _order[1:] if ME["configs"][c]["N"] == _cen["N"])
    _Ns = sorted(ME["configs"][c]["N"] for c in _order[1:] if ME["configs"][c]["M"] == _cen["M"])
    assert len(_Ms) + len(_Ns) == _mg["m"]
    put("mn_grid_M", _eng([str(x) for x in _Ms]), "results/mn_sweep_eval.json")
    put("mn_grid_N", _eng([str(x) for x in _Ns]), "results/mn_sweep_eval.json")
    put("mn_centre_label", "(M, N) = " + _cfgname("M32_N8"), "results/mn_sweep_eval.json")
    # §5.2's reading in words, each clause asserted: the shortest forecasts are worse, the longest
    # better (so the original's tie with (32, 32) becomes a loss), and no shorter history is worse.
    _worse = set(_cond["configs_excluding_zero_in_centre_favour"])
    _better = set(_cond["configs_excluding_zero_in_their_favour"])
    _nmin = [c for c in _order[1:] if ME["configs"][c]["M"] == _cen["M"] and ME["configs"][c]["N"] < _cen["N"]]
    _nmax = [c for c in _order[1:] if ME["configs"][c]["M"] == _cen["M"] and ME["configs"][c]["N"] > _cen["N"]]
    _mvar = [c for c in _order[1:] if ME["configs"][c]["N"] == _cen["N"]]
    assert set(_nmin) <= _worse and max(_nmax, key=lambda c: ME["configs"][c]["N"]) in _better, "§5.2's N reading"
    assert not (_worse & set(_mvar)), "§5.2 says no shorter history is worse than the centre's"
    # ... on the governing reading. §5.2 names the shorter histories that beat the centre there, and
    # every other reading the rule reports that puts a shorter history behind the centre.
    put("mn_mvar_better_list", _eng([_cfgname(c) for c in _order[1:] if c in _better and c in _mvar]), _mvs)
    _ow = {}
    for _arena, _blk in (("in-sample", _in74), ("held-out", _al74)):
        for _k, _v in _blk.items():
            for _c in _v["conditions"]["configs_excluding_zero_in_centre_favour"]:
                if _c in _mvar:
                    _met, _h = _k.split("_h")
                    _ow.setdefault(_c, {}).setdefault((_arena, _h), []).append(
                        "relative-L1" if _met == "l1" else "nRMSE")
    assert _ow, "§5.2 says other readings put a shorter history behind the centre"
    _owl = [f"{_cfgname(c)} on {' and '.join(f'{a} ' + ' and '.join(ms) + f' at h = {h}' for (a, h), ms in _ow[c].items())}"
            for c in _order[1:] if c in _ow]
    # a serial comma, because each item already contains "and"
    put("mn_mvar_other_worse", (", ".join(_owl[:-1]) + ", and " + _owl[-1]) if len(_owl) > 1 else _owl[0], _mvs)
    _ovl = [r for r in PR["runs"] if r["rule"] == "M-74" and r["overlap_s"] > 0]
    put("mn_n_overlapped", len(_ovl), "results/presubmission_runtime.json")
    put("mn_n_insample", len(MV["in_sample"]), _mvs)

    _brows, _bl_order = [], ["mlp", "rssm", "transformer"]
    _rwm = BE["configs"]["rwm"]
    _brows.append(f"| **RWM** (Arm A, autoregressive) | {_rwm['seeds']['0']['n_params']:,} | "
                  f"{_m3(_rwm, 100):.4f} | **{_m3(_rwm, 368):.4f}** | — | — | 1.00 |")
    for _rule, _reg, _regname in (("M-75", "tf", "teacher-forced"), ("M-76", "ar", "autoregressive")):
        _g = BV["rules"][_rule]["governing"]["per_baseline"]
        for _a in BV["priority_order"]:
            _cf = BE["configs"][f"{_a}_{_reg}_s7"]
            _r = _g[_a]
            _hrs = _cost["baselines"][f"{_a}_{_reg}_s7"]["relative_to_same_sitting_centre"]
            _name = {"mlp": "MLP", "rssm": "RSSM", "transformer": "transformer"}[_a]
            _dag = " †" if f"{_a}_{_reg}_s7" in _div else ""
            _brows.append(f"| {_name}, {_regname}{_dag} | {_cf['seeds']['0']['n_params']:,} | {_m3(_cf, 100):.4f} | "
                          f"{_m3(_cf, 368):.4f} | {_r['D']:+.4f} [{_r['ci95'][0]:+.4f}, {_r['ci95'][1]:+.4f}] | "
                          f"{'RWM better' if _r['result'] == 'RWM BETTER' else _r['result']} | {_hrs:.2f} |")
            for _h in H2["horizons"]:
                put(f"h2h_bl_{_a}_{_reg}_l1_h{_h}", f"{_m3(_cf, _h):.4f}", "results/baselines_eval.json")
    put("bl_table", "\n".join(_brows), "results/baselines_eval.json + " + _bvs + " + " + _n3s + " + " + _n2s)
    put("bl_tf_verdict", BV["rules"]["M-75"]["verdict"], _bvs)
    put("bl_ar_verdict", BV["rules"]["M-76"]["verdict"], _bvs)
    put("bl_rwm_l1_h368", f"{_m3(_rwm, 368):.4f}", "results/baselines_eval.json")
    put("bl_mde_h368", f'{BV["mde_pct_of_rwm_holm_step_1"]["M-75"]["l1_h368"]:.1f}', _bvs)
    for _rule, _tag in (("M-75", "tf"), ("M-76", "ar")):
        _al = BV["rules"][_rule]["alongside"]
        for _k in ("l1_h1", "l1_h8", "l1_h32"):
            put(f"bl_{_tag}_{_k.replace('l1_', '')}", _al[_k]["verdict"], _bvs)
    put("bl_rwm_params", f"{_rwm['seeds']['0']['n_params']:,}", "results/baselines_eval.json")
    _nm = {"mlp": "MLP", "rssm": "RSSM", "transformer": "transformer"}
    put("bl_params_list", _eng([f"{BE['configs'][f'{a}_tf_s7']['seeds']['0']['n_params']:,} ({_nm[a]})"
                                for a in BV["priority_order"]]), "results/baselines_eval.json")
    # §5.3's sentences, each asserted. "All N comparisons favour RWM":
    _all = [(r, b, BV["rules"][r]["governing"]["per_baseline"][b]) for r in ("M-75", "M-76")
            for b in BV["priority_order"]]
    assert all(x["result"] == "RWM BETTER" for _, _, x in _all), "§5.3 says every comparison favours RWM"
    put("bl_n_rows_word", WORDS[len(_all)].lower(), _bvs)
    # "every baseline row is above the hold-last floor at h = 368, which RWM is below":
    _fl = BV["hold_last_floor_l1"]["held_out"]["368"]
    assert all(_m3(BE["configs"][f"{b}_{g}_s7"], 368) > _fl for b in BV["priority_order"] for g in ("tf", "ar"))
    assert _m3(_rwm, 368) < _fl and abs(_fl - MV["hold_last_floor_l1"]["held_out"]["368"]) < 1e-12
    # "At h = 1 both rules return X ... at h = 8 both return Y":
    for _k in ("l1_h1", "l1_h8"):
        assert BV["rules"]["M-75"]["alongside"][_k]["verdict"] == BV["rules"]["M-76"]["alongside"][_k]["verdict"], _k
    # "the teacher-forced RSSM's one-step error is below RWM's without being resolvable":
    assert _m3(BE["configs"]["rssm_tf_s7"], 1) < _m3(_rwm, 1)
    assert BV["rules"]["M-75"]["alongside"]["l1_h1"]["per_baseline"]["rssm"]["result"] == "CANNOT BE SETTLED"
    # "the smallest resolvable difference ... is well below every difference here":
    assert BV["mde_pct_of_rwm_holm_step_1"]["M-75"]["l1_h368"] == BV["mde_pct_of_rwm_holm_step_1"]["M-76"]["l1_h368"]
    assert min(x["D"] for _, _, x in _all) > 2 * BV["mde_pct_of_rwm_holm_step_1"]["M-75"]["l1_h368"] / 100 * _m3(_rwm, 368)
    # "parameter-matched variants were specified but not run":
    assert BV["matched_variants"] == {}

    # --- Round 2, T4: sections 5.2 and 5.3 with N2, N3 and X1 (Annex 2 E2, E3, E6, E7) -----------
    _sd = lambda x: f"{x:+.4f}"
    _sci = lambda c: f"[{c[0]:+.4f}, {c[1]:+.4f}]"
    # Annex 3: the winners described by kind, counted from the verdict rather than typed.
    _bsh = [c for c in _better if ME["configs"][c]["N"] == _cen["N"] and ME["configs"][c]["M"] < _cen["M"]]
    _blf = [c for c in _better if ME["configs"][c]["M"] == _cen["M"] and ME["configs"][c]["N"] > _cen["N"]]
    _alf = [c for c in _order[1:] if ME["configs"][c]["M"] == _cen["M"] and ME["configs"][c]["N"] > _cen["N"]]
    assert len(_bsh) + len(_blf) == len(_better) and _blf, (_bsh, _blf)
    _lfp = ("both" if len(_alf) == 2 else "all") if len(_blf) == len(_alf) else WORDS[len(_blf)].lower()
    put("mn_better_long_phrase", f"{_lfp} longer training forecast{'s' if len(_blf) > 1 else ''}", _mvs)
    put("mn_n_short_better_word", WORDS[len(_bsh)].lower(), _mvs)
    put("mn_better_kinds", f"{WORDS[len(_bsh)].lower()} shorter histor{'ies' if len(_bsh) > 1 else 'y'} and "
                           f"{_lfp} longer training forecast{'s' if len(_blf) > 1 else ''}", _mvs)
    # E2 / N3 part 1: cost per iteration relative to the centre, for the four configurations that beat it.
    for _c in _cond["configs_excluding_zero_in_their_favour"]:
        put(f"n3_cost_{_c}", f'{_cost["sweep"][_c]["relative_to_centre"]:.2f}', _n3s)
    # E2 / N3 parts 2-3: the best neighbour at h = 368 against the centre trained longer (Annex 3 variant).
    _av = N3["annex3_variant"]
    assert _av["best_neighbour_at_h368"] == _best and _av["variant"] == "a", _av
    assert _av["neighbour_minus_centre_at_5000_h368_held_out"]["ci95"][1] < 0, "variant (a) needs the interval below zero"
    _rd = N3["part3_readings"]["readings"]
    assert N3["part2_centre_at_more_compute"]["reproduces_sweep_centre_at_2500"]["max_abs_diff"] <= 1e-6
    _k_mid, _k_long = sorted({v["centre_iterations"] for v in _rd.values()} - {int(N["iters_main"]["value"].replace(",", ""))})
    assert _k_long == int(N["iters_long"]["value"].replace(",", "")), _k_long
    put("n3_k_mid", f"{_k_mid:,}", _n3s)
    _fac_mid = _k_mid / int(N["iters_main"]["value"].replace(",", ""))
    assert _fac_mid in (2, 3, 4), _fac_mid
    put("n3_mid_factor_word", {2: "twice", 3: "three times", 4: "four times"}[int(_fac_mid)], _n3s)
    for _tag, _k in (("mid", _k_mid), ("long", _k_long)):
        _r = _rd[f"{_best}|centre@{_k}"]
        # the centre's compute over the neighbour's: the inverse of the artifact's ratio
        put(f"n3_best_over_{_tag}", f'{1 / _r["compute_ratios"]["config_total_compute_over_centre_at_k"]:.2f}', _n3s)
        put(f"n3_best_D_{_tag}", _sd(_r["h368"]["held_out"]["D"]), _n3s)
        put(f"n3_best_ci_{_tag}", _sci(_r["h368"]["held_out"]["ci95"]), _n3s)
    assert _rd[f"{_best}|centre@{_k_mid}"]["h368"]["held_out"]["ci95"][1] < 0          # still ahead at mid
    _cl = _rd[f"{_best}|centre@{_k_long}"]["h368"]["held_out"]["ci95"]
    assert _cl[0] < 0 < _cl[1], "section 5.2 says the long-centre difference is not resolved"
    # in-sample, the centre at mid draws level with the best and passes (32, 16)
    _bi = _rd[f"{_best}|centre@{_k_mid}"]["h368"]["in_sample"]
    assert _bi["ci95"][0] < 0 < _bi["ci95"][1], "section 5.2 says the centre draws level in-sample"
    put("n3_best_ins_D_mid", _sd(_bi["D"]), _n3s)
    put("n3_best_ins_ci_mid", _sci(_bi["ci95"]), _n3s)
    _lf = [c for c in _cond["configs_excluding_zero_in_their_favour"] if c != _best and ME["configs"][c]["M"] == _cen["M"]]
    assert len(_lf) == 1, _lf
    _li = _rd[f"{_lf[0]}|centre@{_k_mid}"]["h368"]["in_sample"]
    assert _li["ci95"][0] > 0, "section 5.2 says the centre passes the other longer forecast in-sample"
    put("n3_lf_label", _cfgname(_lf[0]), _n3s)
    put("n3_lf_ins_D_mid", _sd(_li["D"]), _n3s)
    put("n3_lf_ins_ci_mid", _sci(_li["ci95"]), _n3s)
    # the shorter histories cost less per iteration than the centre, and fall behind it at the long centre
    _sh = [c for c in _order[1:] if c in _better and c in _mvar]
    assert all(_cost["sweep"][c]["relative_to_centre"] < 1 for c in _sh)
    for _c in _sh:
        _r = _rd[f"{_c}|centre@{_k_long}"]["h368"]["held_out"]
        assert _r["ci95"][0] > 0, f"section 5.2 says {_c} falls behind the centre at {_k_long:,}"
        put(f"n3_sh_D_long_{_c}", _sd(_r["D"]), _n3s)
        put(f"n3_sh_ci_long_{_c}", _sci(_r["ci95"]), _n3s)
    put("n3_sh_long_clause", _eng([f'{_cfgname(c)} by {_sd(_rd[f"{c}|centre@{_k_long}"]["h368"]["held_out"]["D"])} '
                                   f'{_sci(_rd[f"{c}|centre@{_k_long}"]["h368"]["held_out"]["ci95"])}' for c in _sh]), _n3s)
    # --- Round 3, R2 (Annex 2 E1; Annex 3 A1-A3, A6): the settings sweep at equal compute, every reading ---------
    # D = configuration's error minus the centre's; negative favours the configuration, positive the centre.
    _CC = (("h100", "held_out"), ("h100", "in_sample"), ("h368", "held_out"), ("h368", "in_sample"))
    _res = lambda x: x["ci95"][0] > 0 or x["ci95"][1] < 0
    _cen_ahead = lambda x: x["ci95"][0] > 0
    _cfg_ahead = lambda x: x["ci95"][1] < 0
    _im = int(N["iters_main"]["value"].replace(",", ""))
    put("n3_long_factor_word", {2: "twice", 3: "three times", 4: "four times"}[_k_long // _im], _n3s)
    assert _k_long % _im == 0
    put("n3_n_readings_word", WORDS[len(_CC)].lower(), _n3s)
    # "the shorter histories win on all four readings at 2,500 iterations, at well under half the centre's cost"
    for _c in _sh:
        assert all(_cfg_ahead(_rd[f"{_c}|centre@{_im}"][h][a]) for h, a in _CC), _c
        assert _cost["sweep"][_c]["relative_to_centre"] < 0.5, _c
        put(f"n3_sh_label_{_c}", _cfgname(_c), _n3s)
    # the best longer forecast against the centre at the mid budget: one reading each way, the other two unresolved
    _bm = _rd[f"{_best}|centre@{_k_mid}"]
    assert _cfg_ahead(_bm["h368"]["held_out"]) and _cen_ahead(_bm["h100"]["in_sample"])
    assert not _res(_bm["h100"]["held_out"]) and not _res(_bm["h368"]["in_sample"])
    put("n3_best_ins_D_mid_h100", _sd(_bm["h100"]["in_sample"]["D"]), _n3s)
    put("n3_best_ins_ci_mid_h100", _sci(_bm["h100"]["in_sample"]["ci95"]), _n3s)
    # ...at the long budget: the centre ahead on both in-sample readings, neither held-out reading resolved
    _bl = _rd[f"{_best}|centre@{_k_long}"]
    assert _cen_ahead(_bl["h100"]["in_sample"]) and _cen_ahead(_bl["h368"]["in_sample"])
    assert not _res(_bl["h100"]["held_out"]) and not _res(_bl["h368"]["held_out"])
    # the shorter histories against the centre at the long budget: the centre ahead on three of the four readings,
    # and not resolved on the held-out pair at h = 100
    _nsh = set()
    for _c in _sh:
        _r = _rd[f"{_c}|centre@{_k_long}"]
        _nsh.add(sum(_cen_ahead(_r[h][a]) for h, a in _CC))
        assert not _res(_r["h100"]["held_out"]) and all(_cen_ahead(_r[h][a]) for h, a in _CC if (h, a) != ("h100", "held_out"))
        put(f"n3_sh_over_long_{_c}", f'{1 / _r["compute_ratios"]["config_total_compute_over_centre_at_k"]:.0f}', _n3s)
    assert len(_nsh) == 1, _nsh
    put("n3_sh_long_nread_word", WORDS[_nsh.pop()].lower(), _n3s)
    # contribution 3: the shorter histories cost under half the centre's per iteration, the longer forecasts more
    assert all(_cost["sweep"][c]["relative_to_centre"] > 1 for c in _blf), _blf
    # "trained longer, the centre passes each of them on at least one reading": every configuration that beat it
    for _c in _better:
        assert any(_cen_ahead(_rd[f"{_c}|centre@{k}"][h][a]) for k in (_k_mid, _k_long) for h, a in _CC), _c
    # Appendix U: every reading of part 3, generated
    _corder = sorted({v["config"] for v in _rd.values()}, key=lambda c: _order.index(c))
    _cell = lambda x: (f"**{_sd(x['D'])} {_sci(x['ci95'])}**" if _res(x) else f"{_sd(x['D'])} {_sci(x['ci95'])}")
    _urows = []
    for _c in _corder:
        for _k in sorted(v["centre_iterations"] for v in _rd.values() if v["config"] == _c):
            _r = _rd[f"{_c}|centre@{_k}"]
            _urows.append(f"| {_cfgname(_c)} ({_r['compute_ratios']['config_cost_per_iter_over_centre']:.2f}) | {_k:,} | "
                          f"{1 / _r['compute_ratios']['config_total_compute_over_centre_at_k']:.2f} | "
                          + " | ".join(_cell(_r[h][a]) for h, a in _CC) + " |")
    assert len(_urows) == len(_rd)
    put("n3_appU_table", "\n".join(_urows), _n3s)
    put("n3_appU_nrows_word", WORDS.get(len(_urows), str(len(_urows))).lower(), _n3s)
    # A1: the original's own Fig. 6 figures for the centre and the neighbour it ties with (EXT, transcribed)
    _mo = next(c for c in J("original_paper_figures.json")["claims"] if c["key"] == "mn_optimal")
    _pe, _ph = _mo["printed_e"], _mo["printed_hours"]
    assert _pe["M32_N8"] == _pe["M32_N32"], "A1 says the centre matches the neighbour's error"
    assert _ph["M32_N8"] / _ph["M32_N32"] < 0.5, "A1 says the centre takes under half the time"
    put("orig_tied_label", _cfgname("M32_N32"), "results/original_paper_figures.json")
    assert _cfgname("M32_N32") == _cfgname(_best), "A1 compares the original's tie with our best neighbour"
    put("orig_e_32_8", f'{_pe["M32_N8"]:.2f}', "results/original_paper_figures.json")
    put("orig_e_32_32", f'{_pe["M32_N32"]:.2f}', "results/original_paper_figures.json")
    put("orig_h_32_8", f'{_ph["M32_N8"]:.2f}', "results/original_paper_figures.json")
    put("orig_h_32_32", f'{_ph["M32_N32"]:.2f}', "results/original_paper_figures.json")
    put("orig_h_ratio", f'{_ph["M32_N32"] / _ph["M32_N8"]:.2f}', "results/original_paper_figures.json")
    # E2 / N3 part 4: every run at 2,500 iterations is still learning.
    _ts = J("training_tail_slopes.json")
    _t25 = _ts["summary"]["at_2500_all"]
    assert _t25["n_falling"] == _t25["n"] and _t25["n_flat_or_rising"] == 0
    assert _ts["definition_reproduces_stored"]["max_rel_diff"] <= _ts["definition_reproduces_stored"]["tolerance"]
    put("tail_n", _t25["n"], "results/training_tail_slopes.json")
    put("tail_slope_lo", f'{_t25["min"] * 1000:.2f}', "results/training_tail_slopes.json")
    put("tail_slope_hi", f'{_t25["max"] * 1000:.2f}', "results/training_tail_slopes.json")
    # E6 / N2: the baselines' pooled nRMSE in the head-to-head table, and how the pooled readings compare.
    assert N2R["asserts"]["a_centre_matches_head_to_head_pooled"]["max_abs_diff"] <= 1e-6
    for _h in N2R["asserts"]["a_centre_matches_head_to_head_pooled"]["horizons"]:
        assert f'{N2R["three_seed_mean"]["M32_N8"]["held_out"]["pooled_nrmse"][str(_h)]:.4f}' == \
            N[f"h2h_armA_nrmse_h{_h}"]["value"], _h
    _nm2r = {"tf": "teacher-forced", "ar": "autoregressive"}
    for _a in BV["priority_order"]:
        for _reg in ("tf", "ar"):
            _cfn = f"{_a}_{_reg}_s7"
            for _h in H2["horizons"]:
                put(f"h2h_bl_{_a}_{_reg}_nrmse_h{_h}", f'{N2R["three_seed_mean"][_cfn]["held_out"]["pooled_nrmse"][str(_h)]:.4f}', _n2s)
            put(f"h2h_bl_{_a}_{_reg}_label", f'{_nm[_a]}, {_nm2r[_reg]} (§5.3){" †" if _cfn in _div else ""}', _n2s)
    _chg = N2A["readings_whose_result_changed"]
    assert not any(c.startswith("M-74") or "held_out" in c for c in _chg), "a pooled held-out or M-74 reading changed"
    _nm2 = {"M-75": "teacher-forced", "M-76": "autoregressive"}
    _chg_txt = []
    for _c in _chg:
        _rule, _cell = _c.split(" ")
        _arena, _key = _cell.split("|")
        _v = N2A["readings"][_rule][_cell]
        _chg_txt.append(f'with the baselines {_nm2[_rule]}, {_arena.replace("_", "-")} nRMSE at h = '
                        f'{_key.split("_h")[1]} returns {_v["pooled"]["result"]} pooled against '
                        f'{_v["committed"]["result"]} averaged')
    put("n2_n_changed_word", WORDS[len(_chg)].lower(), _n2as)
    put("n2_changed_list", "; ".join(_chg_txt), _n2as)
    # Round 3, R2 (Annex 2 E4, Annex 3 A5b): the two changed in-sample readings, in section 5.3, D signed as
    # verdict_baselines.py signs it (positive favours RWM)
    assert _chg == ["M-75 in_sample|nrmse_h1", "M-76 in_sample|nrmse_h100"], _chg
    _sd3 = lambda x: f"{x:+.3f}"
    _sci3 = lambda c: f"[{c[0]:+.3f}, {c[1]:+.3f}]"
    _r75 = N2A["readings"]["M-75"]["in_sample|nrmse_h1"]
    for _a in ("mlp", "rssm", "transformer"):
        _p = _r75["pooled"]["per_key"][f"{_a}_tf_s7"]
        assert _p["rejected"] and _p["D"] < 0, (_a, _p)          # "all three baselines are ahead of RWM"
        put(f"n2_m75_D_{_a}", _sd3(_p["D"]), _n2as)
        put(f"n2_m75_ci_{_a}", _sci3(_p["ci95"]), _n2as)
    put("n2_m75_pooled", _r75["pooled"]["result"], _n2as)
    put("n2_m75_committed", _r75["committed"]["result"], _n2as)
    _r76 = N2A["readings"]["M-76"]["in_sample|nrmse_h100"]
    _p = _r76["pooled"]["per_key"]["mlp_ar_s7"]
    assert not _p["rejected"] and _p["ci95"][0] < 0 < _p["ci95"][1] and _p["D"] > 0   # "no longer resolved"
    assert _r76["committed"]["per_key"]["mlp_ar_s7"]["rejected"]
    assert _r76["keys_whose_direction_or_rejection_changed"] == ["mlp_ar_s7"]
    put("n2_m76_D_mlp", _sd3(_p["D"]), _n2as)
    put("n2_m76_ci_mlp", _sci3(_p["ci95"]), _n2as)
    put("n2_m76_pooled", _r76["pooled"]["result"], _n2as)
    put("n2_m76_committed", _r76["committed"]["result"], _n2as)
    # E7: the diverged flag, as N2 defines it.
    _dr = N2R["diverged_flag"]["rows"]
    _fac = {round(v["threshold"] / v["floor_l1_h368"], 6) for v in _dr.values()}
    assert len(_fac) == 1, _fac
    put("div_factor", f"{_fac.pop():g}", _n2s)
    _sig = lambda x: f"{x:.0f}" if x >= 100 else f"{x:.1f}" if x >= 10 else f"{x:.2f}"
    _dn = {"mlp_tf_s7": "MLP, teacher-forced", "transformer_tf_s7": "transformer, teacher-forced",
           "rssm_tf_s7": "RSSM, teacher-forced", "mlp_ar_s7": "MLP, autoregressive",
           "transformer_ar_s7": "transformer, autoregressive", "rssm_ar_s7": "RSSM, autoregressive"}
    _dl = [k for k in ("mlp_tf_s7", "rssm_tf_s7", "transformer_tf_s7", "mlp_ar_s7", "rssm_ar_s7", "transformer_ar_s7") if k in _div]
    put("div_n_word", WORDS[len(_dl)].lower(), _n2s)
    put("div_per_seed", "; ".join(f'{_dn[k]}: ' + _eng([_sig(_dr[k]["per_seed_mean_l1_h368"][s]) for s in ("0", "1", "2")])
                                  for k in _dl), _n2s)
    # "no verdict depends on the magnitude, only on the sign": every flagged row's four per-trajectory
    # differences from RWM at h = 368 are positive, so every bootstrap resample's mean is positive
    # whatever their size, and the exact interval and p are those of the sign pattern alone.
    for _k in _dl:
        _a, _reg = _k.split("_")[0], _k.split("_")[1]
        _rule = "M-75" if _reg == "tf" else "M-76"
        assert all(x > 0 for x in BV["rules"][_rule]["governing"]["per_baseline"][_a]["per_traj"]), _k
    # E3: where RWM's lead begins, read from the rules' relative-L1 readings (alongside and governing).
    _hz = [1, 8, 32, 100, 128, 368]

    def _lead_from(rule, a):
        """The shortest horizon from which RWM is resolvably better at every longer one too."""
        ok = [BV["rules"][rule]["alongside"][f"l1_h{h}"]["per_baseline"][a]["result"] == "RWM BETTER" for h in _hz]
        assert ok[-1]
        i = len(ok) - 1
        while i > 0 and ok[i - 1]:
            i -= 1
        # "before those horizons a baseline cannot be told apart from RWM" (T4 review F7)
        assert all(BV["rules"][rule]["alongside"][f"l1_h{h}"]["per_baseline"][a]["result"] == "CANNOT BE SETTLED"
                   for h in _hz[:i]), (rule, a)
        return _hz[i]
    _lf75 = {a: _lead_from("M-75", a) for a in BV["priority_order"]}
    _lf76 = {a: _lead_from("M-76", a) for a in BV["priority_order"]}
    assert _lf75["mlp"] == _lf75["rssm"] and _lf76["mlp"] == _lf76["transformer"], (_lf75, _lf76)
    put("bl_tf_lead_from", f'h = {_lf75["mlp"]}', _bvs)
    put("bl_tf_tr_lead_from", f'h = {_lf75["transformer"]}', _bvs)
    put("bl_ar_lead_from", f'h = {_lf76["mlp"]}', _bvs)
    put("bl_ar_rssm_lead_from", f'h = {_lf76["rssm"]}', _bvs)
    _hdep = J("v2_deployment_horizon.json")["verdict"]["deployment_horizon_is"]
    assert str(_lf76["mlp"]) == str(_hdep), "section 5.3 reads the M-76 h = 100 figures at the lead's start"
    _a100 = BV["rules"]["M-76"]["alongside"][f'l1_h{_hdep}']["per_baseline"]
    for _a, _t in (("mlp", "mlp"), ("transformer", "tr")):
        put(f"bl_ar_{_t}_D_h100", f'{_a100[_a]["D"]:.3f}', _bvs)
        put(f"bl_ar_{_t}_ci_h100", f'[{_a100[_a]["ci95"][0]:.3f}, {_a100[_a]["ci95"][1]:.3f}]', _bvs)
    put("bl_ar_mlp_pct_h100", f'{100 * _a100["mlp"]["D"] / _m3(_rwm, _hdep):.1f}', _bvs + " + results/baselines_eval.json")
    # E3 / X1 (ledger M-80, M-81): the RSSM paragraph.
    X1 = J("rssm_diagnostics.json")
    _x1s = "results/rssm_diagnostics.json"
    assert X1["part_a_mode_reproduces_baselines_eval"]["max_abs_diff"] <= 1e-6
    _xa = X1["part_a"]["rssm_tf_s7"]["three_seed_mean"]
    assert f'{_xa["mode"]["1"]:.4f}' == N["h2h_bl_rssm_tf_l1_h1"]["value"]
    assert _xa["mode"]["1"] < X1["floor_mean"]["1"] and _xa["mode"]["1"] < _m3(_rwm, 1), "most accurate at h = 1"
    assert all(_xa["mode"]["1"] < _m3(BE["configs"][f"{a}_{g}_s7"], 1) for a in BV["priority_order"]
               for g in ("tf", "ar") if (a, g) != ("rssm", "tf")), "the most accurate model at h = 1"
    assert _xa["mode"]["32"] > X1["floor_mean"]["32"], "collapses by h = 32"
    put("x1_floor_h1", f'{X1["floor_mean"]["1"]:.4f}', _x1s)
    put("x1_floor_h32", f'{X1["floor_mean"]["32"]:.4f}', _x1s)
    put("x1_tf_mode_h32", f'{_xa["mode"]["32"]:.4f}', _x1s)
    put("x1_tf_exp_h32", f'{_xa["expected"]["32"]:.4f}', _x1s)
    put("x1_tf_samp_h32", f'{_xa["sampled"]["32"]:.4f}', _x1s)
    put("x1_reading_a", X1["part_a_reading"], _x1s)
    assert X1["part_a_reading"] == "NOT EVALUATION-LIMITED"
    _pb = X1["part_b"]
    _rat = lambda reg: [v[str(int(N["iters_main"]["value"].replace(",", "")))]["mean_over_steps"]["prior_over_posterior"]
                        for k, v in _pb.items() if k.startswith(f"rssm_{reg}_s7|")]
    _kl = [v[str(int(N["iters_main"]["value"].replace(",", "")))]["mean_over_steps"]["kl"]
           for k, v in _pb.items() if k.startswith("rssm_tf_s7|")]
    put("x1b_tf_ratio_lo", f"{min(_rat('tf')):.2f}", _x1s)
    put("x1b_tf_ratio_hi", f"{max(_rat('tf')):.2f}", _x1s)
    put("x1b_ar_ratio_hi", f"{max(_rat('ar')):.2f}", _x1s)
    put("x1b_kl_lo", f"{min(_kl):.1f}", _x1s)
    put("x1b_kl_hi", f"{max(_kl):.1f}", _x1s)
    # Part C's sentence. T9 replaces this with the reading once rssm_diagnostics.py --part c has run;
    # T10's checklist fails if this placeholder survives.
    # E2: the wall-clock hours sections 5.2 and 5.3 printed move to Appendix B, one row per run family,
    # with how many of its runs overlapped other logged CPU work.
    _ovf = {}
    for _r in PR["runs"]:
        _ovf.setdefault(f'{_r["rule"]} {_r["family"]}', 0)
        _ovf[f'{_r["rule"]} {_r["family"]}'] += _r["overlap_s"] > 0
    _rt = []
    for _c in _order[1:]:
        _f = PR["by_family"][f"M-74 {_c}"]
        _rt.append(f'| {_cfgname(_c)} (§5.2) | {_f["n_runs"]} | {_f["mean_s"] / 3600:.2f} | {_ovf[f"M-74 {_c}"]} |')
    for _rule, _reg, _regname in (("M-75", "tf", "teacher-forced"), ("M-76", "ar", "autoregressive")):
        for _a in BV["priority_order"]:
            _f = PR["by_family"][f"{_rule} {_a}_{_reg}_s7"]
            _rt.append(f'| {_nm[_a]}, {_regname} (§5.3) | {_f["n_runs"]} | {_f["mean_s"] / 3600:.2f} | '
                       f'{_ovf[f"{_rule} {_a}_{_reg}_s7"]} |')
    assert len(_rt) == len(PR["by_family"]) and sum(_ovf.values()) == PR["n_runs_overlapped"]
    # Round 3, R5 (H4): rule X1's Part C ran from a second queue and was missing from this table. Its
    # runs are the last rows, outside the totals Appendix B's prose gives for the sweep and the
    # baselines; the prose counts them separately.
    _XC = PR["x1_part_c"]
    _xcn = {"x1v1": "PlaNet's KL settings", "x1v2": "DreamerV2's layer-normalised cell"}
    assert set(_XC["by_family"]) == {f"rssm_tf_{_v}" for _v in _xcn}, _XC["by_family"]
    _xov = {}
    for _r in _XC["runs"]:
        assert J(_r["artifact"].split("/", 1)[1])["hyperparameters"]["iterations"] == \
            int(N["iters_main"]["value"].replace(",", "")), _r["artifact"]      # "every run at" iters_main
        _xov[_r["family"]] = _xov.get(_r["family"], 0) + (_r["overlap_s"] > 0)
    for _v, _vn in _xcn.items():
        _f = _XC["by_family"][f"rssm_tf_{_v}"]
        _rt.append(f'| {_nm["rssm"]}, teacher-forced, {_vn} (rule X1, §5.3) | {_f["n_runs"]} | '
                   f'{_f["mean_s"] / 3600:.2f} | {_xov[f"rssm_tf_{_v}"]} |')
    assert sum(_xov.values()) == _XC["n_runs_overlapped"]
    put("rt_x1c_runs", _XC["n_runs"], "results/presubmission_runtime.json")
    put("rt_x1c_hours", f'{_XC["wall_clock_s"] / 3600:.1f}', "results/presubmission_runtime.json")
    put("rt_x1c_overlapped", _XC["n_runs_overlapped"], "results/presubmission_runtime.json")
    put("rt_pre_table", "\n".join(_rt), "results/presubmission_runtime.json")
    # Round 2, T9: X1 was discharged in T8 (ledger M-83), so an artifact without Part C is stale (for
    # example, rssm_diagnostics.py re-run with --part ab alone). It stops the build rather than putting
    # the pre-discharge placeholder back into section 5.3.
    assert X1["part_c"] is not None, \
        "results/rssm_diagnostics.json has no Part C; X1 was discharged (M-83): re-run --part c"
    # Round 2, T8: Part C has run (ledger M-83). The sentence reports the final reading verbatim and is
    # bound to the artifact; it describes the case where neither variant rescues on seed 0, and asserts
    # it, so any other reading stops the build until the sentence is rewritten for it.
    _pc = X1["part_c"]
    assert set(_pc) == {"V1", "V2"} and not any(r["seed0"] for r in _pc.values()), _pc
    assert X1["final_reading"] == "NOT RESCUED BY THE SETTINGS TRIED", X1["final_reading"]
    _rh = X1["arena"]["horizons"][2]
    put("x1_final_reading", X1["final_reading"], _x1s)
    # The T8 review (A1): the first wording put the criterion where it read as the outcome, and
    # measured every trajectory against the floor's mean. The rule (M-80) and below_floor() test
    # each trajectory against its own floor value, and the mean against the floor's mean.
    _n = X1["arena"]["n_independent"]
    _its = {J(f"baseline_run_rssm_tf_{r['spec']}_seed0.json")["hyperparameters"]["iterations"]
            for r in _pc.values()}
    assert len(_its) == 1, _its
    _m = {v: _pc[v]["per_seed_mean_l1"]["0"][_rh] for v in ("V1", "V2")}
    _up = {v: sum(1 for x in _pc[v]["seed0_per_traj_minus_floor"] if x > 0) for v in ("V1", "V2")}
    assert all(len(_pc[v]["seed0_per_traj_minus_floor"]) == _n for v in _pc), _pc
    assert all(_m[v] > X1["floor_mean"][_rh] and _up[v] > 0 for v in _m), (_m, _up)
    put("rssm_partc_sentence",
        f"Its Part C retrains the teacher-forced RSSM at seed 0 for {next(iter(_its)):,} iterations, "
        f"once with PlaNet's KL settings and once with DreamerV2's layer-normalised recurrent cell. "
        f"Neither rescues it: read from its most likely latent at h = {_rh}, they score "
        f"{_m['V1']:.4f} and {_m['V2']:.4f} against the floor's {X1['floor_mean'][_rh]:.4f}, with "
        f"{_up['V1']} and {_up['V2']} of the {_n} trajectories above their own floor value; a rescue "
        f"needs the mean below the floor's and every trajectory below its own. So rule X1 returns "
        f"**{X1['final_reading']}** (ledger M-83).", _x1s)

    # --- Round 2, T5: Appendix H, the confirmed findings the body does not state ---------------
    # Each row's claim is asserted where its key is made. Rows with no artifact (source-code facts)
    # carry only addresses, which are not measurements.
    # D-10: commanded-velocity segments
    _rg = J("step0_regimes.json")["regimes"]
    _per = {}
    for _x in _rg:
        _per[_x["ep"]] = _per.get(_x["ep"], 0) + 1
    _mode = max(set(_per.values()), key=list(_per.values()).count)
    _odd = [e for e, n in _per.items() if n != _mode]
    assert len(_per) == 10 and len(_odd) == 1 and _per[_odd[0]] == _mode + 1, _per
    put("d10_n_regimes", len(_rg), "results/step0_regimes.json")
    put("d10_per_ep_word", WORDS[_mode].lower(), "results/step0_regimes.json")
    put("d10_extra_ep", _odd[0], "results/step0_regimes.json")
    # R-25: a second variance parameter implies the same order of iterations
    _ml = J("step6_3_min_logstd.json")
    assert _ml["verdict"] == "second axis, agrees" and _ml["rate_ratio"] > 1
    # an order-of-magnitude extrapolation from one Arm A run's rates, not a fitted count
    # (step6_3_min_logstd.py says so), so two significant figures (T5 review A4)
    _2sf = lambda x: f"{float(format(x, '.2g')):,.0f}"
    put("r25_implied_ld", _2sf(_ml["iters_implied_log_delta"]), "results/step6_3_min_logstd.json")
    put("r25_implied_min", _2sf(_ml["iters_implied_min_logstd"]), "results/step6_3_min_logstd.json")
    # R-30: the apparent heavy tail is two short regions
    _g27 = J("taskAB_gate_r27.json")
    _tl = _g27["tail"]
    _pt = sorted(_tl["nonoverlap_per_traj"])
    _med = (_pt[1] + _pt[2]) / 2 if len(_pt) == 4 else float(np.median(_pt))
    assert _tl["n_distinct_regions"] == len(_tl["regions"]) and len({r[2] for r in _tl["regions"]}) == len(_tl["regions"])
    put("r30_tail_share", f'{100 * _tl["worst5pct_share"]:.1f}', "results/taskAB_gate_r27.json")
    put("r30_n_regions_word", WORDS[_tl["n_distinct_regions"]].lower(), "results/taskAB_gate_r27.json")
    put("r30_n_nonoverlap", len(_tl["nonoverlap_starts"]), "results/taskAB_gate_r27.json")
    put("r30_maxmed", f"{max(_pt) / _med:.1f}", "results/taskAB_gate_r27.json")
    # the share is of scale-normalised squared error (form 2), which one dimension dominates (T5 review A5)
    _pd2 = [x * x for x in _g27["per_dim_model"]]
    assert _pd2[_g27["dim_names"].index("g_z")] / sum(_pd2) > 0.5, "R-30's row says g_z dominates form 2"
    # R-39: the held-out pair's h = 368 magnitude rests on episode 1 (three seeds, 2,500 iterations)
    _pe = J("task4_arenas.json")["task4b"]["per_episode"]
    _gp = {int(e): v["l1368"] for e, v in _pe.items()}
    _sg = sorted(_gp.values(), reverse=True)
    _e1 = max(_gp, key=_gp.get)
    _c4 = J("task4_arenas.json")["task4b"]["correlations"]["l1368"]
    assert all(v > 0 for v in _gp.values()) and _c4["gap_holdout"] > _c4["gap_other"]
    assert _e1 in {int(e) for e in H2["arena_episodes"]}, "R-39: the outlier episode is one of the held-out pair"
    assert len({v["n"] for v in _pe.values()}) == 1
    put("r39_n_per_ep", next(iter(_pe.values()))["n"], "results/task4_arenas.json")
    put("r39_ep", _e1, "results/task4_arenas.json")
    put("r39_ep_gap", f"{_gp[_e1]:+.2f}", "results/task4_arenas.json")
    put("r39_ep_over_next", f"{_sg[0] / _sg[1]:.1f}", "results/task4_arenas.json")
    put("r39_gap_lo", f"{min(_gp.values()):+.2f}", "results/task4_arenas.json")
    put("r39_gap_holdout", f'{_c4["gap_holdout"]:+.2f}', "results/task4_arenas.json")
    put("r39_gap_other", f'{_c4["gap_other"]:+.2f}', "results/task4_arenas.json")
    put("r39_ho_over_other", f'{_c4["gap_holdout"] / _c4["gap_other"]:.1f}', "results/task4_arenas.json")
    put("r39_n_eps_word", WORDS[len(_gp)].lower(), "results/task4_arenas.json")
    put("r39_n_other_word", WORDS[len(_gp) - len(H2["arena_episodes"])].lower(), "results/task4_arenas.json")
    # R-45 (with R-29): matched per-dimension comparison, seed 1
    _mt = J("task2_3_matched_trend.json")
    _m10, _m18 = _mt["all ten episodes (as run in Q1)"], _mt["episodes 1 and 8 ONLY"]
    assert _mt["provenance"]["seeds"] == [1]
    assert _m10["shared"] == _m18["shared"] == _m10["armA_lost"] == _m18["armA_lost"], "R-45: Arm A loses on the same one"
    assert {"g_x", "g_y", "g_z"} <= set(_m10["released_lost"]) & set(_m18["released_lost"])
    put("r45_n_dims", len(_g27["dim_names"]), "results/taskAB_gate_r27.json")
    put("r45_rel_all", len(_m10["released_lost"]), "results/task2_3_matched_trend.json")
    put("r45_rel_ho", len(_m18["released_lost"]), "results/task2_3_matched_trend.json")
    put("r45_A_n", len(_m10["armA_lost"]), "results/task2_3_matched_trend.json")
    put("r45_A_dim", "`" + _m10["armA_lost"][0] + "`", "results/task2_3_matched_trend.json")
    put("r45_nind_all", _m10["n_ind"], "results/task2_3_matched_trend.json")
    put("r45_nind_ho", _m18["n_ind"], "results/task2_3_matched_trend.json")
    put("r45_seed", _mt["provenance"]["seeds"][0], "results/task2_3_matched_trend.json")
    # R-46: absolute gap narrows with training, ratio does not (seed 1)
    _tr = _mt["trend"]
    _o, _i = _tr["out-of-sample|h368"], _tr["in-sample|h368"]
    assert _o["gap"][-1] < _o["gap"][0] and _i["gap"][-1] < _i["gap"][0], "R-46: the absolute gap narrows"
    assert _o["ratio"][-1] > _o["ratio"][0] and _i["ratio"][-1] > _i["ratio"][0], "R-46: the ratio does not shrink"
    assert len(_o["gap"]) == len(_i["gap"])
    put("r46_n_ck_word", WORDS[len(_o["gap"])].lower(), "results/task2_3_matched_trend.json")
    _pk = max(range(len(_o["gap"])), key=lambda j: _o["gap"][j])
    assert _pk == max(range(len(_o["ratio"])), key=lambda j: _o["ratio"][j]) and 0 < _pk < len(_o["gap"]) - 1
    put("r46_pk_ord", {1: "second", 2: "third", 3: "fourth"}[_pk], "results/task2_3_matched_trend.json")
    put("r46_o_gap_pk", f'{_o["gap"][_pk]:+.2f}', "results/task2_3_matched_trend.json")
    put("r46_o_ratio_pk", f'{_o["ratio"][_pk]:.2f}', "results/task2_3_matched_trend.json")
    for _tag, _t in (("o", _o), ("i", _i)):
        put(f"r46_{_tag}_gap0", f'{_t["gap"][0]:+.2f}', "results/task2_3_matched_trend.json")
        put(f"r46_{_tag}_gap1", f'{_t["gap"][-1]:+.2f}', "results/task2_3_matched_trend.json")
        put(f"r46_{_tag}_ratio0", f'{_t["ratio"][0]:.2f}', "results/task2_3_matched_trend.json")
        put(f"r46_{_tag}_ratio1", f'{_t["ratio"][-1]:.2f}', "results/task2_3_matched_trend.json")

    # --- S10: keys and assertions behind the fresh-eyes review's fixes ----------------------
    # Appendix E's verdict column for M-16 printed its Status line ("SETTLED — rule
    # pre-registered"), while §5, §8 and the introduction cite what it RETURNED.
    _m16 = {c["verdict"] for c in J("task4_arenas.json")["m16_arenas"].values()}
    assert len(_m16) == 1, _m16
    put("m16_verdict", _m16.pop().upper(), "results/task4_arenas.json")
    # §8 names the one h = 8 cell whose verdict the bootstrap unit changes.
    _bus = J("review_bootstrap_unit.json")
    _chg = _bus["_summary"]["cells_that_change"]
    assert len(_chg) == 1 and _chg[0].endswith("|h8"), _chg
    _ar, _ln, _ck, _ = _chg[0].split("|")
    put("bu_change_cell", f"the {_ar} h = 8 cell at {_ln}-step trajectories and "
                          f"{int(_ck):,} iterations", "results/review_bootstrap_unit.json")
    # §5: the in-sample arena agrees in sign with the held-out one in every bootstrap-unit
    # cell except h = 8 after 500 iterations, where teacher forcing leads in-sample and the
    # interval excludes zero, at both trajectory lengths.
    for _k, _v in _bus.items():
        if _k == "_summary" or not _k.startswith("in-sample"):
            continue
        _g = _v["cluster"]
        if _k.endswith("|500|h8"):
            assert _g["gap"] < 0 and _g["excludes_zero"], _k
            _oos = _bus[_k.replace("in-sample", "out-of-sample")]["cluster"]["gap"]
            assert _oos > 0, _k
        else:
            assert _g["gap"] > 0, _k
    # §6.7's opening names the arena and checkpoint of its tables; §6.10's names its arena;
    # §6.2's ensemble-5 table names its iterations.
    _d20 = J("task_d_nind20.json")["design"]
    assert _d20["arena"] == "all ten episodes" and _d20["checkpoint"].endswith("pretrain_rnn_ens.pt")
    assert J("r2_independent_ensemble.json")["design"]["arena"] == "out-of-sample held-out pair"
    assert J("task_d3_ens5.json")["design"]["iterations"] == int(N["iters_main"]["value"].replace(",", ""))
    # §7.4 names the contamination control's design from its own cell keys.
    _tw = J("task3_three_way.json")
    _twk = [k.split("|") for k in _tw if k != "_summary"]
    assert {k[0] for k in _twk} == {"in-sample", "out-of-sample"}
    _lens = sorted({int(k[1]) for k in _twk})
    _cks = sorted({int(k[2]) for k in _twk})
    _nind = sorted({_tw[k]["n_independent"] for k in _tw if k != "_summary"})
    # D3 and D4 (user rulings): the two producers now record their design, and the
    # captions cite it.
    _sd = J("task2_sigma_profile.json")["_design"]
    assert _sd["our_arms_checkpoint"] == "weights_" + N["iters_main"]["value"].replace(",", "") + ".pt"
    assert _sd["n_independent"] == _sd["n_trajectories"] and _sd["traj_len"] == 400
    put("sig_arena", _sd["arena"], "results/task2_sigma_profile.json")
    put("sig_nind", _sd["n_independent"], "results/task2_sigma_profile.json")
    _e4d = J("e4_sigma_gradients.json")["design"]
    assert _e4d["weights"].startswith("freshly initialised") and "training episodes" in _e4d["data"]
    put("e4_batch", _e4d["batch_size"], "results/e4_sigma_gradients.json")
    put("tw_design", f"the held-out pair and the training episodes, "
                     f"{' and '.join(str(x) for x in _lens)}-step trajectories, the "
                     f"{' and '.join(f'{x:,}' for x in _cks)}-iteration checkpoints, "
                     f"n_independent {_nind[0]} to {_nind[-1]}", "results/task3_three_way.json")

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
        # ensemble is part of the key. Without it the ens1 and ens5 Arm A runs
        # collapsed into one row reading "6 | 0, 0, 1, 1, 2, 2" -- three seeds
        # listed twice, which reads as a duplication bug rather than as two
        # configurations.
        # rnn_hidden_size is part of the key too, for the same reason ensemble is.
        # Without it M-49's five capacity-matched runs at width 124 sat inside the
        # released-width Arm A row, which then read "10 | 0, 0, 1, 1, 2, 2, 3, 3,
        # 4, 4" -- five seeds listed twice, in a table headed "so a reader can
        # count them". Two architectures were presented as one population, in the
        # one place the paper invites a reader to audit the population by hand.
        key = (arm, h["iterations"], h.get("ensemble", 1), h.get("loss_type", "mse"),
               "contaminated" if h.get("contaminated") else
               ("duplicated" if h.get("duplicated") else "clean"), _width(f))
        inv.setdefault(key, []).append(d["seed"])
    rows = []
    for (arm, it, ens, loss, ds, w), seeds in sorted(inv.items()):
        rows.append(f"| Arm {arm} | {it:,} | {ens} | {loss} | {ds} | {w} | {len(seeds)} | "
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

    # ==================================================================
    # Pre-submission revision: V1-V4, P1, A2, T1.
    # ==================================================================

    # --- V1 / X-12: what is shared across the five ensemble members --------
    V1 = J("v1_ensemble_topology.json")
    _ref = V1["reference"]
    _mech = V1["mechanism"]
    put("v1_members", _ref["ensemble_size"], "results/v1_ensemble_topology.json")
    put("v1_shared_params", f'{_mech["shared_params_per_member"]:,}',
        "results/v1_ensemble_topology.json")
    put("v1_private_params", f'{_mech["private_params_per_member"]:,}',
        "results/v1_ensemble_topology.json")
    put("v1_member_params", f'{_ref["state_pathway_params_per_member"]:,}',
        "results/v1_ensemble_topology.json")
    put("v1_shared_pct", f'{_mech["shared_pct_of_member"]:.2f}',
        "results/v1_ensemble_topology.json")
    put("v1_shared_pct0", f'{_mech["shared_pct_of_member"]:.0f}',      # the abstract's rounding
        "results/v1_ensemble_topology.json")
    put("v1_private_pct", f'{_mech["private_pct_of_member"]:.2f}',
        "results/v1_ensemble_topology.json")
    put("v1_shared_pct_model", f'{100 * _ref["shared_fraction_of_model"]:.2f}',
        "results/v1_ensemble_topology.json")
    put("v1_total_params", f'{_ref["total_params"]:,}', "results/v1_ensemble_topology.json")
    put("v1_hidden_states", _ref["n_independent_recurrent_states"],
        "results/v1_ensemble_topology.json")
    # Rendered as a word too: "There is 1 hidden-state trajectory" reads badly and
    # "one" cannot be typed under this paper's own rule. Same pattern as
    # n_retractions_word.
    # WORDS is capitalised for sentence-initial use; both of these render
    # mid-sentence, so lower them.
    put("v1_hidden_states_word",
        WORDS.get(_ref["n_independent_recurrent_states"],
                  str(_ref["n_independent_recurrent_states"])).lower(),
        "results/v1_ensemble_topology.json")
    put("v1_members_word",
        WORDS.get(_ref["ensemble_size"], str(_ref["ensemble_size"])).lower(),
        "results/v1_ensemble_topology.json")
    put("v1_n_citations", len(V1["source_citations"]), "results/v1_ensemble_topology.json")
    put("v1_our_arms_match",
        "yes" if V1["gate"]["our_arms_match_reference_topology"] else "NO",
        "results/v1_ensemble_topology.json")
    put("v1_n_arms_checked", len(V1["our_arms"]), "results/v1_ensemble_topology.json")
    # C4(rev2), 4.3 -- the capacity confound in 6.10's contrast, measured from the
    # checkpoints rather than estimated.
    _cc = V1["capacity_confound"]
    put("v1_cap_shared", f'{_cc["shared_trunk_arm_params"]:,}',
        "results/v1_ensemble_topology.json")
    put("v1_cap_indep", f'{_cc["independent_ensemble_params"]:,}',
        "results/v1_ensemble_topology.json")
    put("v1_cap_ratio", f'{_cc["ratio_independent_over_shared"]:.2f}',
        "results/v1_ensemble_topology.json")

    # --- V2 / X-13: which horizon is the deployment horizon ----------------
    V2 = J("v2_deployment_horizon.json")
    put("v2_deploy_h", V2["verdict"]["deployment_horizon_is"],
        "results/v2_deployment_horizon.json")
    put("v2_diag_h", V2["horizons"]["open_loop_diagnostic"]["value"],
        "results/v2_deployment_horizon.json")
    put("v2_ratio", f'{V2["verdict"]["h368_over_deployment"]:.2f}',
        "results/v2_deployment_horizon.json")
    put("v2_lite_cap", V2["horizons"]["imagination_episode_cap_lite_release"]["value"],
        "results/v2_deployment_horizon.json")
    put("v2_len_eval",
        V2["horizons"]["open_loop_diagnostic"]["arithmetic"]["len_eval_trajectory"],
        "results/v2_deployment_horizon.json")
    put("v2_history",
        V2["horizons"]["open_loop_diagnostic"]["arithmetic"]["history_horizon"],
        "results/v2_deployment_horizon.json")
    put("v2_fig_v1", V2["followup_figure"]["v1"]["figure"],
        "results/v2_deployment_horizon.json")
    put("v2_fig_v3", V2["followup_figure"]["v3"]["figure"],
        "results/v2_deployment_horizon.json")

    # --- V3 / X-14: the metric definitions ---------------------------------
    V3 = J("v3_metric_definitions.json")
    put("v3_n_citations", V3["n_citations_verified"], "results/v3_metric_definitions.json")
    put("v3_rel_l1", V3["metrics"]["relative_l1"]["latex_per_step"],
        "results/v3_metric_definitions.json")
    put("v3_rel_l1_agg", V3["metrics"]["relative_l1"]["latex_aggregate"],
        "results/v3_metric_definitions.json")
    put("v3_nrmse", V3["metrics"]["nrmse_pooled"]["latex"],
        "results/v3_metric_definitions.json")
    put("v3_scale", V3["constants"]["nrmse_scale"]["latex"],
        "results/v3_metric_definitions.json")
    put("v3_coverage", V3["coverage"]["latex"], "results/v3_metric_definitions.json")
    put("v3_rho", V3["metrics"]["overconfidence_factor"]["latex"],
        "results/v3_metric_definitions.json")
    put("v3_rho_calibrated",
        f'{V3["metrics"]["overconfidence_factor"]["calibrated_value_of_rho"]:.4f}',
        "results/v3_metric_definitions.json")
    put("v3_cov_nominal1", f'{100 * V3["coverage"]["nominal"]["pm1"]:.2f}',
        "results/v3_metric_definitions.json")
    put("v3_cov_nominal2", f'{100 * V3["coverage"]["nominal"]["pm2"]:.2f}',
        "results/v3_metric_definitions.json")

    # --- V4 / X-15: the follow-up's version map ----------------------------
    _fv = J("original_paper_figures.json")["followup_version_map"]
    put("v4_read", _fv["we_read"], "results/original_paper_figures.json")
    put("v4_read_date", _fv["we_read_dated"], "results/original_paper_figures.json")
    put("v4_current", _fv["current"], "results/original_paper_figures.json")
    put("v4_current_date", _fv["current_dated"], "results/original_paper_figures.json")
    put("v4_n_moved", len(_fv["moved"]), "results/original_paper_figures.json")
    put("v4_n_unchanged", len(_fv["unchanged"]), "results/original_paper_figures.json")
    # C4(rev2), 4.4. The rename was asserted in two places and challenged as
    # possibly being two model variants. It is a rename: the two names never
    # co-occur in any version, and only the expansion of the letter changed.
    _nm = next(m for m in _fv["moved"] if m["what"] == "the model's name")
    put("v4_name_v1", _nm["v1"], "results/original_paper_figures.json")
    put("v4_name_v3", _nm["v3"], "results/original_paper_figures.json")
    put("v4_exp_v1", _nm["v1_expansion"], "results/original_paper_figures.json")
    put("v4_exp_v3", _nm["v3_expansion"], "results/original_paper_figures.json")
    put("v4_name_n_v1", _nm["occurrences"]["v1"][_nm["v1"]],
        "results/original_paper_figures.json")
    put("v4_name_n_v3", _nm["occurrences"]["v3"][_nm["v3"]],
        "results/original_paper_figures.json")
    assert _nm["occurrences"]["v1"][_nm["v3"]] == 0 and _nm["occurrences"]["v3"][_nm["v1"]] == 0, \
        "the two model names co-occur in a version; the rename claim does not hold"

    # --- P1: what the two new rules can detect -----------------------------
    P1 = J("p1_power_check.json")
    put("p1_m45_n", P1["m45"]["n_independent_faced"], "results/p1_power_check.json")
    put("p1_m45_mde", f'{P1["m45"]["mde_80pct_power"]:.3f}', "results/p1_power_check.json")
    put("p1_m44_n", P1["m44"]["n_independent_faced"], "results/p1_power_check.json")
    put("p1_m44_mde_ratio",
        f'{P1["m44"]["mde_80pct_power"]["overconfidence_ratio_multiplicative"]:.2f}',
        "results/p1_power_check.json")
    put("p1_m44_mde_cov", f'{P1["m44"]["mde_80pct_power"]["coverage_pts"]:.2f}',
        "results/p1_power_check.json")
    put("p1_m44_mde_ratio_opt",
        f'{P1["m44"]["null_calibration_same_architecture"]["mde_ratio_multiplicative"]:.2f}',
        "results/p1_power_check.json")
    put("p1_m44_resamples", P1["m44"]["distinct_bootstrap_resamples"],
        "results/p1_power_check.json")
    # the dilution levels that bracket M-45's detection threshold, read off the
    # curve rather than asserted
    _pc = P1["m45"]["power_curve"]
    _miss = max((c for c in _pc if c["detection_rate"] < 0.5),
                key=lambda c: c["true_effect_mean"])
    _hit = min((c for c in _pc if c["detection_rate"] >= 0.8),
               key=lambda c: c["true_effect_mean"])
    put("p1_m45_undetected", f'{_miss["true_effect_mean"]:.3f}',
        "results/p1_power_check.json")
    put("p1_m45_detected", f'{_hit["true_effect_mean"]:.3f}', "results/p1_power_check.json")

    # --- A2 / M-45: the trajectory-level control ---------------------------
    A2 = J("a2_trajectory_level_control.json")
    _vd, _dd, _h1 = A2["variance_decomposition"], A2["double_demeaning"], A2["h1_diagnostic"]
    _ci = lambda c: f"[{c[0]:+.3f}, {c[1]:+.3f}]"
    put("a2_nind", A2["design"]["n_independent"], "results/a2_trajectory_level_control.json")
    put("a2_r_pooled", f'{_vd["r_pooled"]:+.3f}', "results/a2_trajectory_level_control.json")
    put("a2_r_pooled_ci", _ci(_vd["r_pooled_ci"]), "results/a2_trajectory_level_control.json")
    put("a2_r_between", f'{_vd["r_between_trajectory"]:+.3f}',
        "results/a2_trajectory_level_control.json")
    put("a2_r_between_ci", _ci(_vd["r_between_ci"]),
        "results/a2_trajectory_level_control.json")
    put("a2_r_within", f'{_vd["r_within_trajectory"]:+.3f}',
        "results/a2_trajectory_level_control.json")
    put("a2_r_within_ci", _ci(_vd["r_within_ci"]), "results/a2_trajectory_level_control.json")
    put("a2_share_between", f'{100 * _vd["share_between"]:.1f}',
        "results/a2_trajectory_level_control.json")
    put("a2_share_within", f'{100 * _vd["share_within"]:.1f}',
        "results/a2_trajectory_level_control.json")
    put("a2_rdd", f'{_dd["r_dd"]:+.3f}', "results/a2_trajectory_level_control.json")
    put("a2_rdd_ci", _ci(_dd["ci"]), "results/a2_trajectory_level_control.json")
    put("a2_step_only", f'{_dd["r_step_demeaned_only"]:+.3f}',
        "results/a2_trajectory_level_control.json")
    put("a2_h1_r", f'{_h1["r_h1"]:+.3f}', "results/a2_trajectory_level_control.json")
    put("a2_h1_ci", _ci(_h1["r_h1_ci"]), "results/a2_trajectory_level_control.json")
    put("a2_h1_partial_both", f'{_h1["partial_on_both"]:+.3f}',
        "results/a2_trajectory_level_control.json")
    put("a2_h1_speed_r",
        f'{_h1["confounders"]["commanded_speed"]["r_disagreement_vs_confounder"]:+.3f}',
        "results/a2_trajectory_level_control.json")
    put("a2_h1_diff_r",
        f'{_h1["confounders"]["episode_difficulty_D12"]["r_disagreement_vs_confounder"]:+.3f}',
        "results/a2_trajectory_level_control.json")
    put("a2_h1_npoints", _h1["n_points"], "results/a2_trajectory_level_control.json")
    # The per-episode difficulty range as A2 uses it: per episode, the mean of
    # step4_0a's two action offsets (A2's comment calls them seeds). D-12 quotes
    # Step 3's range, at the stale offset alone, and is therefore wider; this is
    # the quantity 6.7 partials out, so this is the one 6.7 quotes (D-37).
    put("d12_lo", f'{_h1["episode_difficulty_range"][0]:.3f}',
        "results/a2_trajectory_level_control.json")
    put("d12_hi", f'{_h1["episode_difficulty_range"][1]:.3f}',
        "results/a2_trajectory_level_control.json")
    put("a2_win_existing", f'{A2["reconciliation"]["existing_within_step_mean_r"]:+.3f}',
        "results/a2_trajectory_level_control.json")
    _hd = A2["horizon_dependence"]
    put("a2_excl_h", ", ".join(f"h={h}" for h in _hd["r_dd_excludes_zero_at"]),
        "results/a2_trajectory_level_control.json")
    put("a2_spans_h", " and ".join(f"h={h}" for h in _hd["r_dd_spans_zero_at"]),
        "results/a2_trajectory_level_control.json")
    put("a2_n_excl", len(_hd["r_dd_excludes_zero_at"]),
        "results/a2_trajectory_level_control.json")
    # Round 2, T10 review: the rule's own returned case, verbatim, not a word made from its boolean.
    assert A2["m45"]["supported"] == (A2["m45"]["verdict"] == "DISAGREEMENT CARRIES WITHIN-ROLLOUT INFORMATION")
    put("m45_verdict", A2["m45"]["verdict"], "results/a2_trajectory_level_control.json")
    # the per-horizon partial on trajectory level, for the 6.7 table
    for h in (8, 32, 100, 128, 368):
        _p = A2["partial_by_horizon"][str(h)]
        if _p["r_partial_trajectory_level"] is not None:
            put(f"a2_par_h{h}", f'{_p["r_partial_trajectory_level"]:+.3f}',
                "results/a2_trajectory_level_control.json")
            put(f"a2_par_ci_h{h}", _ci(_p["r_partial_ci"]),
                "results/a2_trajectory_level_control.json")
        if _p["r_dd"] is not None:
            put(f"a2_rdd_h{h}", f'{_p["r_dd"]:+.3f}',
                "results/a2_trajectory_level_control.json")
            put(f"a2_rdd_ci_h{h}", _ci(_p["r_dd_ci"]),
                "results/a2_trajectory_level_control.json")

    # --- the compiled PDF, so the README cannot quote a stale page count ----
    # (compile_paper.py runs AFTER this in the pipeline, so on a first-ever build
    # the key is absent; the README's line is optional for that reason.)
    _cp = os.path.join(R.RESULTS, "compile_paper.json")
    if os.path.exists(_cp):
        CP = J("compile_paper.json")
        put("pdf_pages", CP["pages"], "results/compile_paper.json")
        put("pdf_overfull", CP["overfull_hboxes"], "results/compile_paper.json")
        # This put the LIST here, so the README read "0 overfull boxes, [] LaTeX
        # warnings". The sentence wants a count.
        put("pdf_warnings", len(CP["latex_warnings"]), "results/compile_paper.json")

    # --- Figure 4: the pre-registration record -------------------------------
    # Counted from the figure's own data, so the prose cannot describe a bar by a
    # position that moves when a rule is added. "The fifth bar is negative" became
    # wrong the moment M-43, M-44 and M-45 joined the panel.
    _f4 = J("paper_figures.json")["fig4"]
    # M-48: purging the correspondence transcript from history rewrote every
    # commit from the one that introduced it onward, and two of Figure 4's cited
    # identifiers changed with it. The figure resolves them by commit SUBJECT now
    # (subjects survive a path filter, hashes do not), and the paper discloses the
    # rewrite because a reviewer checking those hashes is exactly who would notice.
    _f4c = J("paper_figures.json")["fig4_commits"]
    put("f4_n_commits", len({c["rule_commit"] for c in _f4c}
                            | {c["data_commit"] for c in _f4c}),
        "results/paper_figures.json")
    put("f4_n_rules", len(_f4), "results/paper_figures.json")
    # Round 3, R4 (S3): Figure 1 now plots every rule Appendix E lists (and M-16's annotation); section 13 counts the
    # commits it cites that kept their identifiers through the M-48 history rewrite, by the figure's own record.
    _f1 = J("paper_figures.json")
    _AGr = J("appendix_g_rules.json")
    assert sorted(b["id"] for b in _f1["fig1_bars"] if b["id"] != "M-16 annotation") == sorted(r["id"] for r in _AGr["rules"])
    _cit, _mov = _f1["fig1_commits"]["cited"], _f1["fig1_commits"]["rewritten_by_purge"]
    assert set(_mov) <= set(_cit) and len(_mov) >= 1
    put("f1_n_cited", len(_cit), "results/paper_figures.json")
    put("f1_n_kept", len(_cit) - len(_mov), "results/paper_figures.json")
    put("f1_n_moved_word", WORDS[len(_mov)].lower(), "results/paper_figures.json")
    put("f4_n_positive", sum(1 for v in _f4.values() if v["lead_hours"] > 0),
        "results/paper_figures.json")
    put("f4_n_negative", sum(1 for v in _f4.values() if v["lead_hours"] <= 0),
        "results/paper_figures.json")

    # --- R2 / M-44: the independent-initialisation ensemble ------------------
    R2 = J("r2_independent_ensemble.json")
    _m44, _dec = R2["m44"], R2["decomposition"]
    put("r2_nind", R2["design"]["n_independent"], "results/r2_independent_ensemble.json")
    put("r2_n_indep", len(R2["design"]["independent_seeds"]),
        "results/r2_independent_ensemble.json")
    put("r2_n_shared", len(R2["design"]["shared_trunk_seeds"]),
        "results/r2_independent_ensemble.json")
    put("m44_verdict", _m44["verdict"], "results/r2_independent_ensemble.json")
    put("m44_supported", "yes" if _m44["supported"] else "no",
        "results/r2_independent_ensemble.json")
    put("m44_h", _m44["horizon"], "results/r2_independent_ensemble.json")
    put("m44_ratio_gain", f'{_m44["mean_ratio_improvement"]:.2f}',
        "results/r2_independent_ensemble.json")
    put("m44_cov_gain", f'{_m44["mean_coverage_gain_pts"]:+.2f}',
        "results/r2_independent_ensemble.json")
    put("m44_mde_ratio", f'{_m44["mde_ratio"]:.2f}', "results/r2_independent_ensemble.json")
    put("m44_mde_cov", f'{_m44["mde_coverage_pts"]:.2f}',
        "results/r2_independent_ensemble.json")
    put("m44_n_conditions", len(_m44["conditions"]), "results/r2_independent_ensemble.json")
    put("m44_n_conditions_met", sum(1 for v in _m44["conditions"].values() if v),
        "results/r2_independent_ensemble.json")
    # the paired range across the three shared-trunk seeds
    _pp = list(R2["comparison"]["per_shared_seed"].values())
    put("r2_ratio_lo", f'{min(p["ratio"] for p in _pp):.3f}',
        "results/r2_independent_ensemble.json")
    put("r2_ratio_hi", f'{max(p["ratio"] for p in _pp):.3f}',
        "results/r2_independent_ensemble.json")
    put("r2_cov_lo", f'{min(p["coverage_diff_pts"] for p in _pp):.2f}',
        "results/r2_independent_ensemble.json")
    put("r2_cov_hi", f'{max(p["coverage_diff_pts"] for p in _pp):.2f}',
        "results/r2_independent_ensemble.json")
    _R2H = sorted(int(h) for h in R2["independent"])
    for h in _R2H:
        i = R2["independent"][str(h)]
        sh = R2["shared_trunk"][str(h)]
        d_ = _dec[str(h)]
        put(f"r2_indep_ratio_h{h}", f'{i["ratio_err_over_sigma"]:.1f}',
            "results/r2_independent_ensemble.json")
        put(f"r2_indep_cov1_h{h}", f'{100 * i["coverage_pm1"]:.2f}',
            "results/r2_independent_ensemble.json")
        put(f"r2_indep_cov2_h{h}", f'{100 * i["coverage_pm2"]:.2f}',
            "results/r2_independent_ensemble.json")
        put(f"r2_shared_ratio_h{h}", f'{sh["mean_ratio"]:.1f}',
            "results/r2_independent_ensemble.json")
        put(f"r2_shared_cov1_h{h}", f'{100 * sh["mean_cov1"]:.2f}',
            "results/r2_independent_ensemble.json")
        put(f"r2_sigma_x_h{h}", f'{d_["sigma_ratio_indep_over_shared"]:.2f}',
            "results/r2_independent_ensemble.json")
        put(f"r2_acc_x_h{h}", f'{d_["error_ratio_shared_over_indep"]:.2f}',
            "results/r2_independent_ensemble.json")
        put(f"r2_total_x_h{h}", f'{d_["total_rho_improvement"]:.2f}',
            "results/r2_independent_ensemble.json")
        if d_["share_from_sigma"] is not None:
            put(f"r2_from_sigma_h{h}", f'{100 * d_["share_from_sigma"]:.0f}',
                "results/r2_independent_ensemble.json")
            put(f"r2_from_acc_h{h}", f'{100 * d_["share_from_accuracy"]:.0f}',
                "results/r2_independent_ensemble.json")
    # The RANGE of the sigma gain across horizons. 6.10 wrote it as
    # "{{r2_sigma_x_h1}}-{{r2_sigma_x_h8}}x at every horizon" -- two named
    # horizons standing in for a range they do not span: h=368's 1.49 sits below
    # the stated lower bound. Found by the horizon sweep, which flagged the
    # sentence for carrying h=1 and h=8 figures while naming h=100 and h=368.
    _sx = [R2["decomposition"][str(h)]["sigma_ratio_indep_over_shared"] for h in _R2H]
    put("r2_sigma_x_lo", f"{min(_sx):.2f}", "results/r2_independent_ensemble.json")
    put("r2_sigma_x_hi", f"{max(_sx):.2f}", "results/r2_independent_ensemble.json")
    put("r2_sigma_x_lo_h", min(_R2H, key=lambda h: _sx[_R2H.index(h)]),
        "results/r2_independent_ensemble.json")
    put("r2_sigma_x_hi_h", max(_R2H, key=lambda h: _sx[_R2H.index(h)]),
        "results/r2_independent_ensemble.json")

    # --- M-68: the combined arm ---------------------------------------------
    # Five independently-initialised full models trained under gaussian_nll:
    # 6.10's topology AND the corrected objective on the same models. Same
    # harness, same arena, same bootstrap, same horizon grid as R2 above, so the
    # keys mirror R2's exactly and the two artifacts can be read side by side.
    C = J("r2_combined_arm.json")
    _m68, _cdec = C["m68"], C["decomposition"]
    _CSRC = "results/r2_combined_arm.json"
    put("m68_nind", C["design"]["n_independent"], _CSRC)
    put("m68_n_indep", len(C["design"]["independent_seeds"]), _CSRC)
    put("m68_n_shared", len(C["design"]["shared_trunk_seeds"]), _CSRC)
    put("m68_verdict", _m68["verdict"], _CSRC)
    put("m68_branch", _m68["branch"], _CSRC)
    put("m68_h", _m68["horizon"], _CSRC)
    put("m68_mde_ratio", f'{_m68["mde_ratio"]:.3f}', _CSRC)
    put("m68_mde_cov", f'{_m68["mde_coverage_pts"]:.2f}', _CSRC)
    put("m68_mde_source", _m68["mde_source"], _CSRC)
    put("m68_sigma_used", _m68["sigma_used_for_coverage"], _CSRC)
    put("m68_n_conditions", len(_m68["conditions"]), _CSRC)
    put("m68_n_conditions_met", sum(1 for v in _m68["conditions"].values() if v), _CSRC)
    put("m68_n_dir", _m68["n_horizons_both_improve_vs_all_three"], _CSRC)
    put("m68_n_horizons", len(_m68["direction_by_horizon"]), _CSRC)
    put("m68_ratio_gain", f'{C["m44"]["mean_ratio_improvement"]:.2f}', _CSRC)
    put("m68_cov_gain", f'{C["m44"]["mean_coverage_gain_pts"]:+.2f}', _CSRC)
    _cpp = list(C["comparison"]["per_shared_seed"].values())
    put("m68_ratio_lo", f'{min(p["ratio"] for p in _cpp):.3f}', _CSRC)
    put("m68_ratio_hi", f'{max(p["ratio"] for p in _cpp):.3f}', _CSRC)
    put("m68_cov_lo", f'{min(p["coverage_diff_pts"] for p in _cpp):.2f}', _CSRC)
    put("m68_cov_hi", f'{max(p["coverage_diff_pts"] for p in _cpp):.2f}', _CSRC)
    _C68H = sorted(int(h) for h in C["independent"])
    for h in _C68H:
        i, sh, d_ = C["independent"][str(h)], C["shared_trunk"][str(h)], _cdec[str(h)]
        put(f"m68_indep_ratio_h{h}", f'{i["ratio_err_over_sigma"]:.1f}', _CSRC)
        put(f"m68_indep_cov1_h{h}", f'{100 * i["coverage_pm1"]:.2f}', _CSRC)
        put(f"m68_indep_cov2_h{h}", f'{100 * i["coverage_pm2"]:.2f}', _CSRC)
        put(f"m68_shared_ratio_h{h}", f'{sh["mean_ratio"]:.1f}', _CSRC)
        put(f"m68_shared_cov1_h{h}", f'{100 * sh["mean_cov1"]:.2f}', _CSRC)
        put(f"m68_shared_cov2_h{h}", f'{100 * sh["mean_cov2"]:.2f}', _CSRC)
        put(f"m68_sigma_x_h{h}", f'{d_["sigma_ratio_indep_over_shared"]:.2f}', _CSRC)
        put(f"m68_acc_x_h{h}", f'{d_["error_ratio_shared_over_indep"]:.2f}', _CSRC)
        put(f"m68_total_x_h{h}", f'{d_["total_rho_improvement"]:.2f}', _CSRC)
        if d_["share_from_sigma"] is not None:
            put(f"m68_from_sigma_h{h}", f'{100 * d_["share_from_sigma"]:.0f}', _CSRC)
            put(f"m68_from_acc_h{h}", f'{100 * d_["share_from_accuracy"]:.0f}', _CSRC)
    # THE OBJECTIVE'S OWN CONTRIBUTION, reported alongside and unable to move the
    # verdict. M-68 scores the combined arm against the SHARED-TRUNK arms, so its
    # verdict measures the pair of fixes together. The isolating comparison is
    # against 6.10's independent arm, which differs from this one only in the
    # objective, and both come from the same script on the same trajectories.
    # It is computed here rather than typed.
    _mse_h = R2["independent"][str(_m68["horizon"])]
    _nll_h = C["independent"][str(_m68["horizon"])]
    _both = _CSRC + " + results/r2_independent_ensemble.json"
    put("m68_vs_mse_ratio",
        f'{_nll_h["ratio_err_over_sigma"] / _mse_h["ratio_err_over_sigma"]:.3f}', _both)
    put("m68_vs_mse_cov_pts",
        f'{100 * (_nll_h["coverage_pm1"] - _mse_h["coverage_pm1"]):+.2f}', _both)
    put("m68_vs_mse_sigma_x",
        f'{_nll_h["mean_sigma"] / _mse_h["mean_sigma"]:.3f}', _both)
    # AND ITS INTERVAL, and whether the design can resolve it. The point estimates
    # above were published bare, and read as "the objective contributes nothing" --
    # a null asserted from an effect SMALLER than the minimum detectable effect the
    # same subsection quotes. That is the M-24 / M-43 failure this paper exists to
    # record, so the isolating comparison now carries the same 95% cluster bootstrap
    # over whole trajectories every governing comparison in 6.11 carries, and the
    # artifact says whether the effect clears the MDE.
    _oi = _m68["objective_isolated"]
    assert abs(_oi["ratio_multiplicative"]
               - _nll_h["ratio_err_over_sigma"] / _mse_h["ratio_err_over_sigma"]) < 1e-9
    put("m68_vs_mse_ratio_ci",
        f'[{_oi["ratio_ci"][0]:.3f}, {_oi["ratio_ci"][1]:.3f}]', _CSRC)
    put("m68_vs_mse_cov_ci",
        f'[{_oi["coverage_ci_pts"][0]:+.2f}, {_oi["coverage_ci_pts"][1]:+.2f}]', _CSRC)

    # --- T1: the bibliography ----------------------------------------------
    T1 = J("t1_bibliography_verified.json")

    # The §2 bibliography, GENERATED. It was a hand-typed list in the template and
    # the six entries added in the revision-3 pass never reached it: §2 cited
    # Malik, Lee, Fort, Wen, Havasi and Seitzer in prose, the footnote under the
    # list claimed "16 of 16 entries verified", and the list itself held ten. A
    # reader could not resolve four of the six at all -- they carried only a venue.
    # A hand-maintained list of what a paper cites is the same defect class as a
    # hand-typed count, and it failed the same way: silently, in the direction that
    # flatters.
    def _initials(name):
        parts = [x for x in name.replace(".", " ").split() if x]
        if len(parts) == 1:
            return parts[0]
        return " ".join(p[0] + "." for p in parts[:-1]) + " " + parts[-1]

    _bib = sorted(T1["entries"], key=lambda e: (e["authors"][0].split()[-1].lower(),
                                                e["year"]))
    _lines = []
    for _n, _e in enumerate(_bib, start=3):
        _au = ", ".join(_initials(a) for a in _e["authors"])
        # Two entries have no venue but the arXiv id itself (they are preprints
        # with no recorded journal_ref), and printing both gave
        # "arXiv:1912.02757. arXiv:1912.02757."
        _ven = "" if _e["venue"].replace("arXiv:", "") == _e["arxiv"] \
            else f'{_e["venue"]}. '
        _lines.append(f'{_n}. {_au}. *{_e["title"]}.* {_ven}'
                      f'arXiv:{_e["arxiv"]}, {_e["year"]}.')
    put("t1_reference_list", "\n".join(_lines), "results/t1_bibliography_verified.json")
    put("t1_first_entry_n", 3, "results/t1_bibliography_verified.json")
    put("t1_last_entry_n", len(_bib) + 2, "results/t1_bibliography_verified.json")
    put("t1_n_refs", T1["n_entries"], "results/t1_bibliography_verified.json")
    put("t1_refs_before", T1["n_references_before"], "results/t1_bibliography_verified.json")
    put("t1_refs_after", T1["n_references_after"], "results/t1_bibliography_verified.json")
    put("t1_n_verified", T1["verification"]["n_metadata_verified"],
        "results/t1_bibliography_verified.json")
    put("t1_n_frag", T1["verification"]["n_fragments_checked"],
        "results/t1_bibliography_verified.json")
    put("t1_n_frag_ok", T1["verification"]["n_fragments_verbatim"],
        "results/t1_bibliography_verified.json")
    # D-35: a one-word fragment matched inside a paper about that word is a check
    # that cannot fail. §2's note says how many of the count are of that kind.
    _frags = [f for e in T1["entries"] for f in (e.get("fragments") or [])]
    assert len(_frags) == T1["verification"]["n_fragments_checked"], "fragment count drifted"
    assert T1["verification"]["n_fragments_verbatim"] == len(_frags), \
        "§2 says 'of them' of the verbatim fragments; that needs every fragment verbatim"
    put("t1_n_frag_oneword", sum(1 for f in _frags if len(f.split()) == 1),
        "results/t1_bibliography_verified.json")

    # ------------------------------------------------------------------
    # Sessions 2 and 3: M-62, M-63, M-64, M-65, M-66 and the 20-seed
    # corroboration. Every value is read from its artifact; none is typed.
    # ------------------------------------------------------------------
    M62 = J("m62_episode_clustering.json")
    _c3 = M62["cells"]["3_section_6_7_pooled_and_rdd"]["statistics"]
    put("m62_verdict", M62["verdict"]["result"], "results/m62_episode_clustering.json")
    put("m62_n_traj", M62["design"]["all ten"]["n_trajectory_level"],
        "results/m62_episode_clustering.json")
    put("m62_n_ep", M62["design"]["all ten"]["n_episode_level"],
        "results/m62_episode_clustering.json")
    put("m62_width_pct",
        f'{100 * (_c3["pooled_r"]["width_ratio_episode_over_trajectory"] - 1):.0f}',
        "results/m62_episode_clustering.json")
    put("m62_rdd_width_ratio",
        f'{_c3["r_dd"]["width_ratio_episode_over_trajectory"]:.2f}',
        "results/m62_episode_clustering.json")
    put("m62_n_uninformative", M62["verdict"]["n_uninformative_by_construction"],
        "results/m62_episode_clustering.json")
    # Two numerals §6.2 and §6.6 were typing by hand, caught by the typed-numeral audit:
    # the out-of-sample episode count and the 400-step unit's row count. Both are design
    # facts an artifact already records, so they are read rather than typed (rule 4).
    put("m62_n_ep_oos", M62["design"]["out-of-sample"]["n_episode_level"],
        "results/m62_episode_clustering.json")
    put("long_unit_rows", J("task_d_nind20.json")["design"]["traj_len"],
        "results/task_d_nind20.json")

    M63 = J("m63_per_dimension_coverage.json")
    _g63 = M63["arenas"]["released_ckpt_all_ten_h1"]
    put("m63_verdict", M63["verdict"]["result"], "results/m63_per_dimension_coverage.json")
    put("m63_iqr", f'{_g63["iqr_points"]:.1f}', "results/m63_per_dimension_coverage.json")
    put("m63_iqr_thr", "15", "results/m63_per_dimension_coverage.json")
    put("m63_median", f'{_g63["median_pct"]:.1f}', "results/m63_per_dimension_coverage.json")
    put("m63_worst_share", f'{100 * _g63["five_worst_share_of_shortfall"]:.0f}',
        "results/m63_per_dimension_coverage.json")
    put("m63_quant", f'{_g63["quantisation_points"]:.0f}',
        "results/m63_per_dimension_coverage.json")

    M65 = J("m65_gaussian_nominal.json")
    _g65 = M65["cases"]["released_ckpt_ens5 [epistemic] all ten episodes"]["by_horizon"]
    put("m65_c_h1", f'{_g65["1"]["oracle_constant_c"]:.1f}',
        "results/m65_gaussian_nominal.json")
    put("m65_c_h368", f'{_g65["368"]["oracle_constant_c"]:.1f}',
        "results/m65_gaussian_nominal.json")
    put("m65_c_growth", f'{_g65["368"]["oracle_constant_c"] / _g65["1"]["oracle_constant_c"]:.0f}',
        "results/m65_gaussian_nominal.json")
    put("m65_n_heavy", M65["verdict"]["counts"].get("HEAVY-TAILED", 0),
        "results/m65_gaussian_nominal.json")
    put("m65_n_cells", sum(M65["verdict"]["counts"].values()),
        "results/m65_gaussian_nominal.json")
    put("m65_calib_ratio", f'{M65["calibrated_ratio_sqrt_2_over_pi"]:.4f}',
        "results/m65_gaussian_nominal.json")

    M64 = J("m64_short_units.json")
    _c = M64["cells"]["C_section_5_ab_gap"]["out-of-sample held-out pair"]["1"]
    _b = M64["cells"]["B_section_6_7_ranking"]["all ten episodes"]["128"]
    _oos = M64["index"]["out-of-sample held-out pair"]
    put("m64_verdict", M64["verdict"]["result"], "results/m64_short_units.json")
    put("m64_h1_unit", _c["unit_length"], "results/m64_short_units.json")
    put("m64_h1_n", _c["n_independent_unit_level"], "results/m64_short_units.json")
    put("m64_h1_gap", f'{_c["gap"]:+.4f}', "results/m64_short_units.json")
    put("m64_h1_ci",
        f'[{_c["gap_ci_unit_level"][0]:+.4f}, {_c["gap_ci_unit_level"][1]:+.4f}]',
        "results/m64_short_units.json")
    put("m64_h1_ratio", f'{_c["ratio_B_over_A"]:.2f}', "results/m64_short_units.json")
    # Round 2, T10 review: section 5's floor sentences hold on the 400-step unit only. On M-64's short
    # units (same arms, seeds, 10,000-iteration checkpoint and episodes) the floor is met differently,
    # and section 5 now says so, from these keys.
    _cs = M64["cells"]["C_section_5_ab_gap"]["out-of-sample held-out pair"]
    _hs = sorted(_cs, key=int)
    _bb = [h for h in _hs if _cs[h]["B_mean"] < _cs[h]["hold_last_floor"]]
    _bl = [h for h in _hs if _cs[h]["B_mean"] >= _cs[h]["hold_last_floor"]]
    assert _c["A_mean"] < _c["hold_last_floor"] and _c["B_mean"] < _c["hold_last_floor"], _c
    # "loses to it only at the longest horizon those units reach": no key carries that horizon,
    # which would restate a typed one (C19.1).
    assert len(_bb) >= 2 and _bl == [_hs[-1]], (_bb, _bl)
    put("m64_floor_h1", f'{_c["hold_last_floor"]:.4f}', "results/m64_short_units.json")
    put("m64_A_h1", f'{_c["A_mean"]:.4f}', "results/m64_short_units.json")
    put("m64_B_h1", f'{_c["B_mean"]:.4f}', "results/m64_short_units.json")
    put("m64_B_beats_floor_at", ", ".join(_bb[:-1]) + " and " + _bb[-1], "results/m64_short_units.json")
    # Round 3, R4 (S13): what a "shorter unit" is at each horizon, and how many the held-out pair holds
    _ix = M64["index"]["out-of-sample held-out pair"]
    _hist = {_ix[h]["unit_length"] - int(h) for h in _ix}
    assert len(_hist) == 1 and all(_ix[h]["counts_agree"] for h in _ix), (_hist, _ix)
    put("m64_hist_rows", _hist.pop(), "results/m64_short_units.json")
    _ul = [f'{_ix[h]["n_independent_unit_level"]} at h = {h}' for h in sorted(_ix, key=int)]
    put("m64_units_list", ", ".join(_ul[:-1]) + " and " + _ul[-1], "results/m64_short_units.json")
    put("m64_h128_n", _b["n_independent_unit_level"], "results/m64_short_units.json")
    put("m64_h128_lo", f'{_b["paired_diff_ci_unit_level"][0]:+.3f}',
        "results/m64_short_units.json")
    put("m64_h128_ci",
        f'[{_b["paired_diff_ci_unit_level"][0]:+.3f}, {_b["paired_diff_ci_unit_level"][1]:+.3f}]',
        "results/m64_short_units.json")
    put("m64_gate_n", J("m64_free_gate.json")["n_pass"], "results/m64_free_gate.json")
    for _h in ("1", "8", "32", "100", "128"):
        put(f"m64_oos_n_h{_h}", _oos[_h]["n_units"], "results/m64_short_units.json")

    _corr = J("e5_synthetic_sigma.json")["corroboration_20_seeds"]
    _sd = _corr["slope_distribution"]["gaussian_nll"]
    put("e5s_corrob_seeds", _corr["n_seeds"], "results/e5_synthetic_sigma.json")
    put("e5s_corrob_clearing", _sd["n_seeds"] - _sd["n_below_slope_threshold"],
        "results/e5_synthetic_sigma.json")
    put("e5s_corrob_below", _sd["n_below_slope_threshold"],
        "results/e5_synthetic_sigma.json")

    IFR = J("insample_framing.json")
    put("insample_n_overlap", IFR["n_overlap"], "results/insample_framing.json")
    put("insample_n_arena", IFR["n_arena_episodes"], "results/insample_framing.json")

    # The evidence summary: Appendix D's second table, which 3.2 points to (round 3, R6, ruling V5;
    # it was 3.2's own table). One row per headline claim, generated by
    # scripts/evidence_summary.py so no arena label and no n_independent in that
    # table is typed; the arena_consistency check compares each row against the
    # section that owns the claim.
    put("evidence_table", J("evidence_summary.json")["table_markdown"],
        "results/evidence_summary.json")

    AUD = J("input_set_audit.json")
    put("audit_n_hits", AUD["n_hits"], "results/input_set_audit.json")
    put("audit_n_frozen", AUD["n_frozen"], "results/input_set_audit.json")
    # Round 2, T8: the audit now retires a frozen discovery once its script is fixed, so the
    # one the sweep found (the ensemble-5 glob, M-66) left n_frozen. BUILD_CHECKS names it
    # as that glob, so check that it is.
    _ret = AUD["retired"]
    assert [x["file"] for x in _ret] == ["scripts/task_d3_ens5.py"], _ret
    put("audit_n_retired", len(_ret), "results/input_set_audit.json")

    # ------------------------------------------------------------------
    # Surface every value that is a LITERAL in this file rather than read from
    # an artifact.
    #
    # This revision hit the same defect three times: n_lessons split on the
    # literal "## 9." and silently moved to the Method section; the worst
    # recalibration cell was pinned to h=128 and moved to h=100; and agree_nh was
    # a literal 5 that stayed 5 when the horizon grid grew to six, so the paper
    # said "5 of 5" over a six-row table AND named the wrong horizon.
    #
    # Each was found by a different accident. A literal here is not always wrong
    # -- a tolerance, a nominal, a fixed convention -- but it is always worth
    # LOOKING at, which is what build_paper.py's typed-numeral report does for
    # prose. This does it for the collector, so the class has to be looked at
    # rather than rediscovered.
    import ast as _ast
    _src = _ast.parse(open(__file__).read())
    _lits = []
    for _n in _ast.walk(_src):
        if (isinstance(_n, _ast.Call) and isinstance(_n.func, _ast.Name)
                and _n.func.id == "put" and len(_n.args) >= 2):
            _k, _v = _n.args[0], _n.args[1]
            if isinstance(_v, _ast.Constant) and isinstance(_v.value, (int, float)) \
                    and not isinstance(_v.value, bool) \
                    and isinstance(_k, _ast.Constant):
                _lits.append((_k.value, _v.value, _v.lineno))
    if _lits:
        print(f"\n  LITERAL VALUES ({len(_lits)}) — each is typed here, not read from an "
              f"artifact. Check that none is bound to something that can move:")
        for _k, _v, _ln in sorted(_lits):
            print(f"    line {_ln:>5}  {_k:<24} = {_v}")

    op = os.path.join(R.RESULTS, "paper_numbers.json")
    json.dump(N, open(op, "w"), indent=2, sort_keys=True)
    print(f"collected {len(N)} keyed numbers -> {R.rel(op)}")
    for k in sorted(N):
        print(f"  {k:<28} {str(N[k]['value']):<16} {N[k]['source']}")


if __name__ == "__main__":
    main()
