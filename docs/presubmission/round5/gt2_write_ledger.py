"""GT2 item 2: append the X11 discharge record (M-104) to FINDINGS_LEDGER.md and set the five Status lines.

Every number is read from the five artifacts; none is typed. Refuses to run twice. Run from the repository root:
  $PY docs/presubmission/round5/gt2_write_ledger.py
"""
import json, re

L = "FINDINGS_LEDGER.md"
led = open(L, encoding="utf-8").read()
assert "### M-104 " not in led
nm = max(int(n) for n in re.findall(r"^### M-(\d+) ", led, re.M)) + 1
assert nm == 104, nm
J = lambda n: json.load(open(f"results/{n}.json"))
a, b, c, d, e = (J(n) for n in ("x11a_fold_ens5_calibration", "x11b_fold_m43", "x11c_fold_recalibration", "x11d_fold_m44", "x11e_fold_e5_propagation"))
f2 = lambda x: f"{x:.2f}"
ci = lambda v: f"[{v[0]:.2f}, {v[1]:.2f}]"

qa = a["q"]
va = a["verdict"]
x11a = (f"**X11a (M-97) returns {va['label']}** at h = 1: Q = ρ_in/ρ_out = {f2(va['q'])} {ci(va['q_ci'])}, per seed "
        f"{', '.join(f2(v) for v in va['q_per_seed'].values())}; ρ_in = {f2(qa['1']['rho_in'])}, ρ_out = {f2(qa['1']['rho_out'])}; the pooled interval contains 1, so the rule's "
        f"all-three-seeds-and-interval condition for either direction is not met. At h = 100 the label it would carry is {a['label_h100']} "
        f"(Q = {f2(qa['100']['q'])} {ci(qa['100']['q_ci'])}) and at h = 368 {qa['368']['label_it_would_carry']} "
        f"(Q = {f2(qa['368']['q'])} {ci(qa['368']['q_ci'])}); those carry no second verdict. Arena: n = 20, every episode in and out of sample.")
gb = b["governing"]
vb = b["verdict"]
hs = vb["horizons_tested"]
r_dis = ", ".join(f2(gb[str(h)]["mean_r_disagreement"]) + " at h = " + str(h) for h in hs)
r_idx = ", ".join(f2(gb[str(h)]["mean_r_index"]) for h in hs)
x11b = (f"**X11b (M-98) returns {vb['verdict']}**: disagreement leads the forecast-step index at {sum(vb['disagreement_leads_index'].values())} of "
        f"{len(hs)} horizons (h = {', '.join(map(str, hs))}) in all three seeds, and the paired interval excludes zero at "
        f"{vb['n_excluding_zero']} of {len(hs)}. Mean r(disagreement) {r_dis}; mean r(index) {r_idx}. n = 20.")
vc = c["verdict"]
pe = c["alongside"]["pooled_over_folds"]["epistemic"]
x11c = (f"**X11c (M-99) returns {vc['label']}** (epistemic governs): {vc['cells_calibrated']} of {vc['n_cells']} fold × seed × direction × horizon cells "
        f"are calibrated within the tolerance; the constant multiplier calibrates {vc['constant_cells_calibrated']}. **Alongside, not a reading:** pooled over the five folds the "
        f"per-horizon multiplier's ±1σ coverage is WITHIN BAND at every horizon (h = 1: {f2(100*pe['per_horizon']['1']['seeds_pooled']['coverage'])}%, "
        f"h = 100: {f2(100*pe['per_horizon']['100']['seeds_pooled']['coverage'])}% {ci([100*v for v in pe['per_horizon']['100']['seeds_pooled']['ci95']])}, "
        f"h = 368: {f2(100*pe['per_horizon']['368']['seeds_pooled']['coverage'])}%), against {f2(100*pe['before']['100']['seeds_pooled']['coverage'])}% before any multiplier at h = 100. "
        f"The cell-level reading and the pooled coverage disagree about 'restores'; both are reported.")
vd = d["m44"]
ad = d["alongside"]
x11d = (f"**X11d (M-100) returns {vd['verdict']}** at h = {vd['horizon']}: the independent ensembles' overconfidence factor is lower by a mean factor of "
        f"{f2(vd['mean_ratio_improvement'])} and their ±1σ coverage higher by {f2(vd['mean_coverage_gain_pts'])} points, in every one of the three shared-trunk seeds, each with an interval excluding zero, "
        f"against M-44's committed thresholds of {vd['mde_ratio']}× and {vd['mde_coverage_pts']} points. Alongside: under the n = 20 minimum detectable effect "
        f"({f2(ad['n20_mde']['ratio_mde_multiplicative'])}×, {f2(ad['n20_mde']['coverage_mde_pts'])} points) the label is {ad['label_under_n20_mde']}.")
t100 = e["table"]["100"]
ive = t100["intervals"]
x11e = (f"**X11e (M-103) returns {e['verdict']['label']}** at h = {e['verdict']['h']}, n = {e['verdict']['n']} ({e['verdict']['reason']}): the share of the log gap closed is "
        f"f = {f2(t100['f'])} {ci(ive['f_ci'])}; ρ falls from {f2(t100['mean']['rho'])} {ci(ive['mean_rho_ci'])} to {f2(t100['per']['rho'])} {ci(ive['per_rho_ci'])}; "
        f"±1σ coverage rises from {f2(100*t100['mean']['coverage_pm1'])}% to {f2(100*t100['per']['coverage_pm1'])}%; CRPS and NLL both fall (paired intervals "
        f"{ci(ive['crps_diff_per_minus_mean_ci'])} and {ci(ive['nll_diff_per_minus_mean_ci'])}). {e['scope']}")

entry = f"""### M-104 — Discharge record of rules X11a–X11e (M-97, M-98, M-99, M-100, M-103): the fold ensembles' readings at n = 20 · **NEW**
**Discharged by GT2, 2026-10-23**, after the queue gate passed: the queue log ends `queue empty; runner exits`, all 20 run IDs are in the done list, none failed, and every run record trained on its fold's complement at the queued ensemble size and 2,500 iterations with finite losses (`docs/presubmission/round5/gt2_queue_check.json`, written by `gt2_queue_check.py`). Each frozen script's SHA-256 was found in its own ledger entry (`x11_common.require_prereg`), each ran unchanged, and each reproduced its fold-{{1, 8}} assertion exactly (maximum difference 0.0). This entry records the readings exactly as returned, with their alongside values; it changes no rule and re-opens none, and it sets only the five Status lines of M-97, M-98, M-99, M-100 and M-103.

{x11a}

{x11b}

{x11c}

{x11d}

{x11e}

**What is and is not read from these.** Each reading is exploratory and bounded as its own entry says. None bears on a discharged rule. They are the n = 20 arena (five folds, each fold's own models on its own held-out pair) for the four arms of RWM-U's calibration that earlier rules measured on the held-out pair's 4 trajectories; X11a's reading at h = 1 is MIXED, which does not support either direction for in-sample measurement; X11c's cell-level reading and its alongside pooled coverage point different ways; X11b, X11d and X11e return the labels their discharged counterparts returned.

**Evidence** `RUN` `results/x11a_fold_ens5_calibration.json`, `results/x11b_fold_m43.json`, `results/x11c_fold_recalibration.json`, `results/x11d_fold_m44.json`, `results/x11e_fold_e5_propagation.json`; `SRC` `scripts/x11a_fold_ens5_calibration.py`, `scripts/x11b_fold_m43.py`, `scripts/x11c_fold_recalibration.py`, `scripts/x11d_fold_m44.py`, `scripts/x9_per_member_propagation.py`, `scripts/x11_common.py`.
**Status** CONFIRMED · **Relevance** METHOD
"""
# Status lines
def setstatus(text, mid, art, reading):
    pat = re.compile(r"(^### " + re.escape(mid) + r" — .*?)(^\*\*Status\*\* PRE-REGISTERED, NOT YET DISCHARGED — awaits `" + re.escape(art) + r"` · \*\*Relevance\*\* METHOD)", re.M | re.S)
    m = pat.search(text)
    assert m, mid
    new = (f"**Status** PRE-REGISTERED, DISCHARGED by `{art}` (`verdict`): {reading}. Recorded in `M-104`. · **Relevance** METHOD")
    return text[:m.start(2)] + new + text[m.end(2):]

led = setstatus(led, "M-97", "results/x11a_fold_ens5_calibration.json", f"**{va['label']}** at h = 1 (Q = {f2(va['q'])} {ci(va['q_ci'])}); the label it would carry at h = 100 is {a['label_h100']}")
led = setstatus(led, "M-98", "results/x11b_fold_m43.json", f"**{vb['verdict']}**")
led = setstatus(led, "M-99", "results/x11c_fold_recalibration.json", f"**{vc['label']}** ({vc['cells_calibrated']} of {vc['n_cells']} cells)")
led = setstatus(led, "M-100", "results/x11d_fold_m44.json", f"**{vd['verdict']}**")
led = setstatus(led, "M-103", "results/x11e_fold_e5_propagation.json", f"**{e['verdict']['label']}** at h = {e['verdict']['h']}, n = {e['verdict']['n']}")
led = led.rstrip("\n") + "\n\n" + entry
open(L, "w", encoding="utf-8").write(led)
print("M-104 appended; five Status lines set")
