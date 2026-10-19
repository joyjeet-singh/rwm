"""GT1 item 4: append the pre-registrations of X11a-X11d (PROTOCOLS.md §4) to FINDINGS_LEDGER.md as M-97 to M-100,
and move RESULTS.md's M- row. Round 4's f1_write_prereg.py, adapted.

Every figure quoted is read from an artifact; every SHA-256 is computed from the file as it stands. Writes a .bak copy
outside the repository, refuses to run twice, and asserts that no X11 run or reading exists yet: no ensemble-5 fold
run record or weights, no single-model seed-3 or seed-4 fold run, and no X11 reading. It also asserts that the
--assert-only and dry-run logs in the evidence folder name each script's current SHA-256 and report passing.
Run from the repository root:  $PY docs/presubmission/round5/gt1_write_prereg.py
"""
import glob
import hashlib
import json
import os
import re
import shutil

L, RES = "FINDINGS_LEDGER.md", "RESULTS.md"
EV = "/Users/Shared/rwm_verify/evidence/R5GT1"
COMMON, XA = "scripts/x11_common.py", "scripts/x11a_fold_ens5_calibration.py"
RULES = {
    "M-97": ("X11a", XA, "results/x11a_fold_ens5_calibration.json", (XA, COMMON)),
    "M-98": ("X11b", "scripts/x11b_fold_m43.py", "results/x11b_fold_m43.json", ("scripts/x11b_fold_m43.py", XA, COMMON)),
    "M-99": ("X11c", "scripts/x11c_fold_recalibration.py", "results/x11c_fold_recalibration.json",
             ("scripts/x11c_fold_recalibration.py", COMMON)),
    "M-100": ("X11d", "scripts/x11d_fold_m44.py", "results/x11d_fold_m44.json", ("scripts/x11d_fold_m44.py", XA, COMMON)),
}
data = (glob.glob("results/x3_run_armA_ho*_ens5.json") + glob.glob("runs/x3_armA_ho*_ens5")
        + glob.glob("results/x3_run_armA_ho*_seed[34].json") + glob.glob("runs/x3_armA_ho*_seed[34]")
        + glob.glob("results/x11[abcd]_*.json*"))
assert not data, f"X11 data exist: {data}"
led = open(L, encoding="utf-8").read()
nm = max(int(n) for n in re.findall(r"^### M-(\d+) ", led, re.M)) + 1
assert nm == 97, nm
assert "PRE-REGISTERED rule X11" not in led
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
J = lambda p: json.load(open(p))
for rid, (name, script, out, frozen) in RULES.items():
    src = open(script).read()
    assert re.search(rf'^RULE_ID = "{rid}"$', src, re.M), (rid, script)
    assert re.search(r"^FROZEN = " + re.escape(repr(tuple(frozen))) + "$", src, re.M), (rid, script)
    log = open(os.path.join(EV, os.path.basename(script)[:-3] + "_assert_only.log"), encoding="utf-8").read()
    assert f"script SHA-256 {sha(script)}" in log and f"x11_common SHA-256 {sha(COMMON)}" in log, script
    assert "FAIL" not in log and log.rstrip().endswith("exit 0"), script
dry = open(os.path.join(EV, "x11_dryrun.log"), encoding="utf-8").read()
for rid, (name, script, out, frozen) in RULES.items():
    assert f"== {os.path.basename(script)[:-3]} {sha(script)}" in dry, f"no dry run of the current {script}"
fs = J("docs/presubmission/round5/gt1_fold_support.json")
assert fs["a"]["pass"] and fs["b"]["pass"] and fs["c"]["pass"]
pw = J("results/x11_power.json")
assert all(v["pass"] for v in pw["assertions"].values())
tm = J("results/round5_queue_timing.json")
assert not tm["blocked"]
probes = sorted(os.path.basename(p) for p in glob.glob("runs/timing_probe_round5/*.json"))
assert not glob.glob("runs/timing_probe_round5/**/*.pt", recursive=True), "a timing probe saved a checkpoint"
for p in glob.glob("runs/timing_probe_round5/*.json"):
    a = J(p)
    assert a["hyperparameters"]["iterations"] == 20 and not a["evaluations"], f"{p} is not a 20-iteration, no-evaluation probe"
t43, b44 = J("results/task_d3_ens5.json")["m43_verdict"], J("results/r2_independent_ensemble.json")["m44"]
t3b = J("results/task_d3b_ens5_power.json")["power_summary"]
m43n, m44n = pw["m43"], pw["m44"]["n20"]["binding_cross_architecture"]
x7 = J("results/x7_loeo_recalibration.json")["reading"]["summary"]
d3 = J("results/task_d3_perhorizon.json")["quantities"]["epistemic"]["verdict"]
SH = lambda paths: ", ".join(f"`{p}` `{sha(p)}`" for p in paths)

COMMON_TEXT = (
    "**Entered before any of its data exists.** No X11 run has been trained: no `results/x3_run_armA_ho*_ens5.json`, "
    "no `runs/x3_armA_ho*_ens5`, no single-model seed-3 or seed-4 fold run, and no X11 reading exists. The only training "
    f"on a new fold so far is GT1's two 20-iteration timing probes on fold {{0, 2}} (`runs/timing_probe_round5/`: "
    f"{', '.join('`' + p + '`' for p in probes)}), which saved no checkpoint and evaluated nothing, and the training-"
    "support runs of `docs/presubmission/round5/gt1_fold_support.json`, which trained 50 iterations on fold {1, 8} only. "
    "Its frozen files are committed in the same commit as this text, whose subject begins `PRE-REGISTER`; the script "
    "refuses to compute the reading unless this entry records the SHA-256 of every one of them "
    "(`scripts/x11_common.py` `require_prereg`). Before that commit, on these bytes, each ran only its `--assert-only` "
    "mode, which loads fold {1, 8}'s existing weights and computes no reading (it passed, maximum difference 0.0), and a "
    "dry run of `reading()` from a harness outside the repository with every fold's weights replaced by fold {1, 8}'s, "
    "whose numbers are a code test and are not recorded; the logs naming these SHA-256s are in the session's evidence "
    "folder. The ordering can be checked from `git log`. Round 5's rule X11 (PLAN Annex 2; "
    "`docs/presubmission/round5/PROTOCOLS.md` §4, which governs where this text is shorter).\n\n"
    "**Runs** (shared by X11a-X11d). Arm A, 2,500 iterations, on X3's folds {0, 2}, {3, 4}, {5, 6}, {7, 9}: ensemble-5 "
    "seeds 0-2 (12 runs, `scripts/step5_train.py --holdout a,b --ensemble 5`) and single-model seeds 3-4 (8 runs, "
    "`--holdout a,b`), queued one at a time through `scripts/queue_runner.sh` (`runs/queue_round5.txt`, "
    "`docs/presubmission/round5/RUN_QUEUE.md`); with fold {1, 8}'s existing runs, every fold has three ensemble-5 arms "
    "and five single models. Cap: the user's ruling `docs/presubmission/round5/DECISIONS.md#GT1-cap`, "
    f"`results/round5_queue_timing.json` (projected {tm['projected_total_h']:.1f} CPU-hours, cap {tm['cap_h']} h). "
    "Training support: `docs/presubmission/round5/gt1_fold_support.json` (a)-(c) passed, (b) bitwise.\n\n"
    "**Arena.** Each fold's four held-out non-overlapping 400-row trajectories, scored by that fold's models, one batch "
    "of 4 per fold, pooled over the five folds: **n = 20**, each episode's two once.\n\n")

GATE = ("**Gate.** No session reads a queue run's evaluation before GT2 (PLAN GT1 item 6). The training driver evaluates "
        "its own checkpoints at 500 and 2,500 iterations and each run's log prints them; those lines are not read "
        "before GT2.\n\n"
        "**What the discharging session may and may not do.** GT2, after the queue has finished and its gate has "
        "passed, runs the script unchanged, records the reading exactly as returned, with its alongside values, in a "
        "new ledger entry, and changes only this entry's Status line. Not: change the folds, models, seeds, iterations, "
        "arena, horizons, statistics, intervals, thresholds or labels; add a reading; or read any number here as "
        "bearing on a discharged rule.\n\n")

BODY = {
    "M-97": (
        "**Exploratory, and bounded.** It never re-opens M-43, M-44, X10 or any discharged rule.\n\n"
        "**Known before this rule:** the ensemble-5 arms' held-out calibration rests on 4 trajectories "
        "(`results/task_d3_ens5.json`, `design.n_independent`); X10 (round 5, G3) compares in- and out-of-sample on "
        "disjoint arenas.\n\n"
        "**Statistic**, copied from `task_d3_ens5.py:243-278` with only the arena changed: per seed, ρ = mean|error| / "
        "mean σ_epistemic, ±1σ and ±2σ coverage and the count of dimensions with r > 0, pooled over (trajectory, step ≤ h, "
        "dimension), h ∈ {1, 8, 32, 100, 128, 368}; pooled = mean over seeds; interval resamples whole trajectories with "
        "the seeds pooled inside each draw (20,000 draws, `default_rng(0)`). X10's Q(h) = ρ_in/ρ_out with every episode in "
        "both roles: each fold's arms also scored on its 16 training trajectories; each trajectory's in-sample value is "
        "the mean over the four folds that trained on it; the interval is a paired bootstrap over the 20 trajectories "
        "(a change from X10, which resampled two disjoint arenas independently).\n\n"
        "**Reading**, at h = 1: **IN-SAMPLE FLATTERS** if Q < 1 for all three seeds and the pooled interval lies below 1; "
        "**IN-SAMPLE IS WORSE** if Q > 1 for all three and the interval lies above 1; **MIXED** otherwise. h = 100 carries "
        "the label it would carry, not a second verdict.\n\n"
        "**Assertions:** (a) every run record trained on its fold's complement at ensemble 5 and 2,500 iterations with "
        "finite losses; (b) on fold {1, 8} the code reproduces `results/task_d3_ens5.json` `calibration`, intervals "
        "included, within 1e-12; (c) for every arm and both arenas the harness agrees with our trainer's forward to < 1e-5.\n\n"),
    "M-98": (
        "**Exploratory, and bounded.** It never re-opens M-43, whose verdict "
        f"({t43['verdict']}, at n = 4, `results/task_d3_ens5.json`) stands.\n\n"
        f"**Known before this rule:** at n = 4 the criterion fired on {100 * t3b['mean_power_at_n4']:.0f}% of draws on "
        f"average and {100 * t3b['worst_power']:.0f}% at h = {t3b['worst_horizon']} (`results/task_d3b_ens5_power.json`, an "
        "upper bound). At n = 20, by the same code with draws taken with replacement (`results/x11_power.json` `m43`), "
        f"it fires on {100 * m43n['n20_mean_power']:.0f}% on average and {100 * m43n['n20_worst_power']:.0f}% at worst over "
        "seeds and horizons, again an upper bound: the pool is in-sample for our arms.\n\n"
        "**Statistic, thresholds and branches**, copied from `task_d3_ens5.py:160-231` with only the arena changed: per "
        "seed and horizon, r(index, |error|), r(disagreement, |error|), the partial, and the paired difference with "
        "`task_d3_ens5.cluster_boot` (`default_rng(0)`, 20,000 draws over 20 trajectories).\n\n"
        "**Reading** (M-43's): **GENERALISES** if disagreement leads the index in all three seeds at every h ∈ {8, 32, "
        "128, 368} and the paired interval excludes zero in all three seeds at more than 2 of the 4; **DOES NOT "
        "GENERALISE** otherwise.\n\n"
        "**Assertions:** (a) as M-97; (b) on fold {1, 8} the code reproduces `results/task_d3_ens5.json` `governing` and "
        "`m43_verdict` within 1e-12.\n\n"),
    "M-99": (
        "**Exploratory, and bounded.** It never re-opens M-69, M-70, M-89 or the D3 per-horizon reading.\n\n"
        f"**Known before this rule:** on the released checkpoint the per-horizon scalar was calibrated in "
        f"{d3['per_horizon_cells_calibrated']} of {d3['n_cells']} held-out cells (`results/task_d3_perhorizon.json`), and "
        f"fitted on nine episodes it returned {x7} (`results/x7_loeo_recalibration.json`); both on a checkpoint that may "
        "have trained on every episode it was scored on.\n\n"
        "**Statistic, thresholds and branches**, copied from `task_d3_perhorizon.py:44-56, 85-127` with only the arena and "
        "the models changed: for each fold, seed and quantity, both directions (fit on one held-out episode, score on the "
        "other), the per-horizon scalar and the constant (fitted at h = 1), on that fold's ensemble-5 arms. A cell is "
        "calibrated iff its ±1σ coverage is within 0.10 of 68.27%.\n\n"
        "**Reading** (epistemic governs): **PER-HORIZON SCALAR RESTORES CALIBRATION** iff all 180 epistemic cells (5 "
        "folds × 2 directions × 6 horizons × 3 seeds) are calibrated; **PER-HORIZON SCALAR DOES NOT RESTORE CALIBRATION** "
        "otherwise. Counts of calibrated cells for both scalars reported. Alongside, not a reading: the coverage pooled "
        "over the ten test episodes (20 trajectories), per seed and seeds pooled, with X7's interval (20,000 draws, "
        "`default_rng(0)`) and band labels.\n\n"
        "**Assertions:** (a) as M-97; (b) the released checkpoint on fold {1, 8} through this code reproduces "
        "`results/task_d3_perhorizon.json` `quantities` within 1e-9 (a scalar relative to max(1, |c|)).\n\n"),
    "M-100": (
        "**Exploratory, and bounded.** It never re-opens M-44 "
        f"({b44['verdict']}, at n = 4, `results/r2_independent_ensemble.json`), M-49 or M-68.\n\n"
        "**Known before this rule:** M-44's binding MDE at n = 4 was 1.45× on the overconfidence ratio and 2.26 points on "
        "coverage (`results/p1_power_check.json`). By the same code at n = 20 (`results/x11_power.json` `m44`) it is "
        f"{m44n['ratio_mde_multiplicative']:.2f}× and {m44n['coverage_mde_pts']:.2f} points, a lower bound (in-sample "
        "pool).\n\n"
        "**Models**, per fold: the five single models (seeds 0-4) as an independent ensemble "
        "(`r2_independent_ensemble.rollout_independent`) against that fold's three ensemble-5 arms.\n\n"
        "**Statistic, thresholds and branches**, copied from `r2_independent_ensemble.py:211-389` with only the arena "
        "changed: at h = 100 (`results/v2_deployment_horizon.json`), per shared-trunk seed, the log ratio of "
        "overconfidence factors and the ±1σ coverage difference, each with `cboot_paired` (`default_rng(100 + s)`, "
        "`default_rng(200 + s)`, 20,000 draws over 20 trajectories); the decomposition into spread and accuracy.\n\n"
        "**Reading** (M-44's, every condition against every shared-trunk seed, M-44's committed thresholds 1.45× and "
        "2.26 points unchanged): **MECHANISM SUPPORTED** iff the independent ensemble's overconfidence is lower, its "
        "interval excludes zero, the improvement is at least 1.45×, its coverage is higher, that interval excludes zero, "
        "and the shift is at least 2.26 points; **UNRESOLVABLE** if the two quantities disagree in direction; **MECHANISM "
        "NOT SUPPORTED** otherwise. Alongside, not a reading: the label under the n = 20 MDE above.\n\n"
        "**Design limitation, as M-44's:** independently seeded runs differ in initialisation and data order, the "
        "shared-trunk heads in head initialisation only; this bounds the effect rather than isolating it.\n\n"
        "**Assertions:** (a) every ensemble-5 and single-model record trained on its fold's complement with finite "
        "losses; (b) on fold {1, 8} the code reproduces `results/r2_independent_ensemble.json` within 1e-12.\n\n"),
}
TITLES = {"M-97": "the ensemble-5 arms' held-out calibration at n = 20, and in-sample against held-out with every episode in both roles",
          "M-98": "M-43's disagreement-against-index comparison on X3's five folds",
          "M-99": "the per-horizon recalibration on episodes the ensemble-5 arms never saw",
          "M-100": "M-44's independent-against-shared-trunk comparison on X3's five folds"}

entries = []
for rid, (name, script, out, frozen) in RULES.items():
    e = (f"### {rid} — PRE-REGISTERED rule {name}: {TITLES[rid]} · **NEW**\n" + COMMON_TEXT + BODY[rid]
         + f"**Frozen files and their SHA-256:** {SH(frozen)}.\n\n" + GATE
         + f"**Evidence** `SRC` `{script}`, `scripts/x11_common.py`, `scripts/step5_train.py` (`--ensemble 5` with "
           f"`--holdout`), `scripts/queue_run.py`, `results/x11_power.json`, `results/round5_queue_timing.json`;\n"
           f"`RUN` `{out}` (awaited).\n"
         + f"**Status** PRE-REGISTERED, NOT YET DISCHARGED — awaits `{out}` · **Relevance** METHOD\n")
    entries.append(e)

os.makedirs(EV, exist_ok=True)
shutil.copy(L, os.path.join(EV, "FINDINGS_LEDGER.md.bak"))
shutil.copy(RES, os.path.join(EV, "RESULTS.md.bak"))
with open(L, "a", encoding="utf-8") as f:
    f.write(("\n" if not led.endswith("\n\n") else "") + "\n".join(entries))
res = open(RES, encoding="utf-8").read()
old = "| `M-` methodological findings | 96 |"
assert res.count(old) == 1
open(RES, "w", encoding="utf-8").write(res.replace(old, "| `M-` methodological findings | 100 |"))
print("appended", ", ".join(RULES), "; RESULTS.md M- 96 -> 100")
for rid, (name, script, out, frozen) in RULES.items():
    print(f"  {rid} {name}: " + ", ".join(f"{os.path.basename(p)} {sha(p)[:12]}" for p in frozen))
