"""F2 item 5: discharge rules X6, X7 and X8 (ledger M-88, M-89, M-90). For each, append a new entry recording the reading
exactly as its script returned it, with the alongside values and no interpretation, and set the pre-registered entry's
Status line (the one sanctioned in-place edit, PLAN §1.2 rule 3). Every figure is read from the artifacts; each artifact's
SHA-256 and commit are asserted equal to the pre-registration's. Writes .bak copies outside the repository and refuses to
run twice. Run from the repository root:  $PY docs/presubmission/round4/f2_write_discharges.py
"""
import json
import os
import re
import shutil
import subprocess

L, RES, BAK = "FINDINGS_LEDGER.md", "RESULTS.md", "/Users/Shared/rwm_verify/evidence/R4F2"
J = lambda p: json.load(open(p))
RULES = {"M-88": ("X6", "results/x6_stepsize_short_units.json", "scripts/x6_stepsize_short_units.py"),
         "M-89": ("X7", "results/x7_loeo_recalibration.json", "scripts/x7_loeo_recalibration.py"),
         "M-90": ("X8", "results/x8_released_pairing.json", "scripts/x8_released_pairing.py")}
led = open(L, encoding="utf-8").read()
prereg = subprocess.run(["git", "log", "--format=%h", "-1", "--grep=^PRE-REGISTER X5"], capture_output=True, text=True).stdout.strip()
assert prereg, "no PRE-REGISTER X5-X8 commit"
for mid, (rule, art, scr) in RULES.items():
    a = J(art)
    m = re.search(rf"^### {mid} — .*?(?=^### |\Z)", led, flags=re.M | re.S)
    assert m and a["script_sha256"] in m.group(0), f"{mid}: the artifact's script SHA-256 is not the pre-registered one"
    assert a["git_head"].startswith(prereg) or subprocess.run(["git", "merge-base", "--is-ancestor", prereg, a["git_head"]]).returncode == 0
    assert "NOT YET DISCHARGED" in m.group(0), f"{mid} is already discharged"
nm = max(int(n) for n in re.findall(r"^### M-(\d+) ", led, re.M)) + 1
D = {"X6": f"M-{nm}", "X7": f"M-{nm + 1}", "X8": f"M-{nm + 2}"}
assert D == {"X6": "M-91", "X7": "M-92", "X8": "M-93"}, D
f4 = lambda x: f"{x:+.4f}"
ci4 = lambda c: f"[{c[0]:+.4f}, {c[1]:+.4f}]"
pc = lambda x: f"{100 * x:.2f}%"
cip = lambda c: f"[{100 * c[0]:.2f}, {100 * c[1]:.2f}]"
head = lambda mid, rule, art, scr, a: (
    f"**Records** {mid}'s reading exactly as `{scr}` returned it, as committed before any reading existed (commit `{prereg}`). "
    f"The artifact records the script's SHA-256, which equals {mid}'s, and the commit it ran at (`{a['git_head'][:7]}`). "
    f"Discharges {mid}. Exploratory; no discharged rule is re-opened.")

# ---------------------------------------------------------------- X6
x6 = J(RULES["M-88"][1]); r6, a6 = x6["reading"], x6["alongside"]
u6 = x6["design"]["units"]
e6 = f"""
### {D['X6']} — Rule X6 (M-88): `{RULES['M-88'][1]}` returns {r6['label']} · **NEW**
{head('M-88', 'X6', RULES['M-88'][1], RULES['M-88'][2], x6)}

**Assertions, before any reading:** (a) {x6['assertions']['a']['max_abs_diff']:.1e}, (b) {x6['assertions']['b']['max_abs_diff']:.1e} and
(c) {x6['assertions']['c']['max_abs_diff']:.1e} maximum difference, all passed; (d) passed at both horizons
({u6['32']['n_units']} units at h = 32 and {u6['100']['n_units']} at h = 100, over {u6['100']['n_episodes']} episodes, counted two ways).

**MDE, computed before the reading** (M-51's method, the margin over the forecast index): {x6['mde_recorded_before_the_reading']['100']['mde_80pct_power']['margin']:.4f}
at h = 100 and {x6['mde_recorded_before_the_reading']['32']['mde_80pct_power']['margin']:.4f} at h = 32.

**The reading**, released checkpoint, h = 100, {r6['n_units']} units: margin r(disagreement, |error|) − r(step size, |error|) =
{f4(r6['margin'])} {ci4(r6['ci95'])}, which returns **{r6['label']}**.

**Alongside, not readings:**
- h = 32, {u6['32']['n_units']} units: margin {f4(a6['h32']['margin'])} {ci4(a6['h32']['margin_ci'])}, would carry {a6['h32_label_it_would_carry']};
- the correlations: at h = 100, r(disagreement, |error|) {f4(a6['h100_correlations']['r_disagreement_error'])} and r(step size, |error|)
  {f4(a6['h100_correlations']['r_step_size_error'])}; at h = 32, {f4(a6['h32']['r_disagreement_error'])} and {f4(a6['h32']['r_step_size_error'])};
- the partial r(disagreement, |error| | step size): {f4(a6['partial_disagreement_given_step_size']['100']['value'])}
  {ci4(a6['partial_disagreement_given_step_size']['100']['ci95'])} at h = 100 and {f4(a6['partial_disagreement_given_step_size']['32']['value'])}
  {ci4(a6['partial_disagreement_given_step_size']['32']['ci95'])} at h = 32;
- the step-size margin's own bootstrap SD (after the reading): {a6['step_size_margin_sd']['100']['bootstrap_se']:.4f} at h = 100 and
  {a6['step_size_margin_sd']['32']['bootstrap_se']:.4f} at h = 32.

Caveats, as M-88 states them: every unit is in the released checkpoint's training data; the units share the ten episodes and the
interval resamples units, not episodes; the statistic is a correlation over (unit, step) cells.
**Evidence** `RUN` `{RULES['M-88'][1]}`; `SRC` `{RULES['M-88'][2]}`.
**Status** CONFIRMED · **Relevance** METHOD
"""

# ---------------------------------------------------------------- X7
x7 = J(RULES["M-89"][1]); r7, a7 = x7["reading"], x7["alongside"]
rows7 = "\n".join(f"| {h} | {pc(v['coverage'])} {cip(v['ci95'])} | {v['label']} | "
                  f"{pc(a7['aleatoric']['per_horizon'][h]['coverage'])} {cip(a7['aleatoric']['per_horizon'][h]['ci95'])}, "
                  f"{a7['aleatoric']['per_horizon'][h]['label']} | "
                  f"{pc(a7['epistemic_constant_multiplier']['per_horizon'][h]['coverage'])}, "
                  f"{a7['epistemic_constant_multiplier']['per_horizon'][h]['label']} | "
                  f"{pc(a7['epistemic_before_any_multiplier'][h]['coverage'])} | "
                  f"{a7['epistemic_c_spread_across_folds'][h]['max_over_min']:.3f} |"
                  for h, v in r7["per_horizon"].items())
e7 = f"""
### {D['X7']} — Rule X7 (M-89): `{RULES['M-89'][1]}` returns {r7['summary']} (epistemic) · **NEW**
{head('M-89', 'X7', RULES['M-89'][1], RULES['M-89'][2], x7)}

**Assertions, before any reading:** (a) {x7['assertions']['a']['max_abs_diff']:.1e} and (b) {x7['assertions']['b']['max_abs_diff']:.1e} maximum
difference, both passed; (c) passed (two 400-step trajectories in every episode, {x7['design']['n_trajectories']} in all).

**The reading**, released checkpoint, epistemic term, ten folds (fit on nine episodes, score the tenth), {x7['design']['n_trajectories']}
trajectories, band [58.27%, 78.27%]: **{r7['summary']}**.

| h | epistemic coverage [95%] | reading | alongside: aleatoric | alongside: constant multiplier | alongside: before any multiplier | alongside: c_h max/min over folds |
|---:|---|---|---|---|---:|---:|
{rows7}

Alongside summaries: the aleatoric term {a7['aleatoric']['summary']}; the constant multiplier lands within the band at
{a7['epistemic_constant_multiplier']['n_within']} of 6 horizons (epistemic) and {a7['aleatoric']['constant_multiplier']['n_within']} of 6 (aleatoric).

Caveat, as M-89 states it: unseen by the multiplier, not by the model; the released checkpoint trained on all ten episodes.
**Evidence** `RUN` `{RULES['M-89'][1]}`; `SRC` `{RULES['M-89'][2]}`.
**Status** CONFIRMED · **Relevance** METHOD
"""

# ---------------------------------------------------------------- X8
x8 = J(RULES["M-90"][1]); rd8 = x8["readings"]
ab = "A/B (M-23's conditions, three seeds)"


def chg(v):
    if not v["alongside_changes"]:
        return "  - none."
    return "\n".join(f"  - {k}: {json.dumps(x[0]) if not isinstance(x[0], str) else x[0]} → "
                     f"{json.dumps(x[1]) if not isinstance(x[1], str) else x[1]};" for k, x in v["alongside_changes"].items())


e8 = f"""
### {D['X8']} — Rule X8 (M-90): `{RULES['M-90'][1]}` returns SAME VERDICT for M-74, M-75, M-76 and the A/B comparison · **NEW**
{head('M-90', 'X8', RULES['M-90'][1], RULES['M-90'][2], x8)}

**Assertions, before any reading:** (a) passed ({x8['assertions']['a']['sweep_n_values']:,} sweep and {x8['assertions']['a']['baselines_n_values']:,}
baseline values reproduced to {max(x8['assertions']['a']['sweep_max_abs_diff'], x8['assertions']['a']['baselines_max_abs_diff']):.1e}, and the
committed verdicts, alongside branches and per-episode signs exactly); (b) passed ({x8['assertions']['b']['max_rel_diff']:.1e} relative);
(c) passed ({x8['assertions']['c']['max_abs_diff']:.1e}); (d) passed (native {x8['assertions']['d']['native_max_abs_diff']:.1e}; the stale-pairing
ratio {x8['assertions']['d']['stale_ratio_max_abs_diff']:.1e}); before the reading, the native check for the sweep configurations with M < 32
passed ({x8['assertions']['d_sweep']['n_models']} models, {x8['assertions']['d_sweep']['max_abs_diff']:.1e}).

**The readings**, our models scored at the released evaluation's pairing (offset 0):
- **M-74:** committed {rd8['M-74']['committed']}; at offset 0 {rd8['M-74']['offset_0']}. **{rd8['M-74']['reading']}.**
- **M-75:** committed {rd8['M-75']['committed']}; at offset 0 {rd8['M-75']['offset_0']}. **{rd8['M-75']['reading']}.**
- **M-76:** committed {rd8['M-76']['committed']}; at offset 0 {rd8['M-76']['offset_0']}. **{rd8['M-76']['reading']}.**
- **The A/B comparison** (M-23's three conditions, three seeds): at offset 1 {rd8[ab]['offset_1']}; at offset 0 {rd8[ab]['offset_0']}.
  **{rd8[ab]['reading']}.**

**Alongside, the readings in each rule's alongside set that change** (offset 1 → offset 0):
- M-74:
{chg(rd8['M-74'])}
- M-75:
{chg(rd8['M-75'])}
- M-76:
{chg(rd8['M-76'])}
- The A/B comparison:
{chg(rd8[ab])}

Every reading of every alongside set, at both offsets, is in the artifact's `detail`; the offset-0 scores are in
`results/x8_sweep_eval_offset0.json` and `results/x8_baselines_eval_offset0.json`.

Caveat, as M-90 states it: our models under the released pairing; it says nothing direct about the original papers' printed numbers.
**Evidence** `RUN` `{RULES['M-90'][1]}`, `results/x8_sweep_eval_offset0.json`, `results/x8_baselines_eval_offset0.json`; `SRC` `{RULES['M-90'][2]}`.
**Status** CONFIRMED · **Relevance** METHOD
"""

# ---------------------------------------------------------------- the Status lines (the sanctioned in-place edit)
returns = {"M-88": r6["label"], "M-89": f"{r7['summary']} (epistemic)",
           "M-90": "SAME VERDICT for M-74, M-75, M-76 and the A/B comparison"}
new = led
for mid, (rule, art, scr) in RULES.items():
    old = f"**Status** PRE-REGISTERED, NOT YET DISCHARGED — awaits `{art}` · **Relevance** METHOD"
    assert new.count(old) == 1, (mid, new.count(old))
    rec = {"M-88": D["X6"], "M-89": D["X7"], "M-90": D["X8"]}[mid]
    new = new.replace(old, f"**Status** PRE-REGISTERED, DISCHARGED by `{art}`. **It returns {returns[mid]}.** Recorded in `{rec}`. · **Relevance** METHOD")
Rt = open(RES, encoding="utf-8").read()
row = re.search(r"^\| `M-` methodological findings \| (\d+) \|", Rt, re.M)
assert row and int(row.group(1)) == nm - 1, row
Rt = Rt.replace(row.group(0), f"| `M-` methodological findings | {nm + 2} |", 1)
os.makedirs(BAK, exist_ok=True)
shutil.copy(L, os.path.join(BAK, "FINDINGS_LEDGER.md.discharge.bak")); shutil.copy(RES, os.path.join(BAK, "RESULTS.md.discharge.bak"))
open(L, "w", encoding="utf-8").write(new.rstrip("\n") + "\n" + e6 + e7 + e8)
open(RES, "w", encoding="utf-8").write(Rt)
print(f"appended {D['X6']}, {D['X7']}, {D['X8']}; Status lines of M-88, M-89, M-90 set; RESULTS.md M- {nm - 1} -> {nm + 2}")
