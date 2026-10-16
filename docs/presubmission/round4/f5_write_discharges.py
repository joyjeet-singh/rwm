"""F5 item 3: discharge rules X3 and X4 (ledger M-86, M-87). For each, append a new entry recording the reading exactly as
its script returned it, with the part-of-rule and alongside values and no interpretation, and set the pre-registered
entry's Status line (the one sanctioned in-place edit, PLAN §1.2 rule 3). Every figure is read from the artifacts; each
artifact's script SHA-256 is asserted equal to the pre-registered one, and its commit to descend from the pre-registration.
Writes .bak copies outside the repository and refuses to run twice. Run from the repository root:
  $PY docs/presubmission/round4/f5_write_discharges.py
"""
import json
import os
import re
import shutil
import subprocess

L, RES, BAK = "FINDINGS_LEDGER.md", "RESULTS.md", "/Users/Shared/rwm_verify/evidence/R4F5"
J = lambda p: json.load(open(p))
RULES = {"M-86": ("X3", "results/x3_cross_fold.json", "scripts/x3_cross_fold.py"),
         "M-87": ("X4", "results/x4_matched_baselines.json", "scripts/x4_matched_baselines.py")}
led = open(L, encoding="utf-8").read()
prereg = subprocess.run(["git", "log", "--format=%h", "-1", "--grep=^PRE-REGISTER X3"], capture_output=True,
                        text=True).stdout.strip()
assert prereg, "no PRE-REGISTER X3/X4 commit"
for mid, (rule, art, scr) in RULES.items():
    a = J(art)
    m = re.search(rf"^### {mid} — .*?(?=^### |\Z)", led, flags=re.M | re.S)
    assert m and a["script_sha256"] in m.group(0), f"{mid}: the artifact's script SHA-256 is not the pre-registered one"
    assert subprocess.run(["git", "merge-base", "--is-ancestor", prereg, a["git_head"]]).returncode == 0, mid
    assert all(v["pass"] for v in a["assertions"].values()), f"{mid}: an assertion did not pass"
    assert "NOT YET DISCHARGED" in m.group(0), f"{mid} is already discharged"
nm = max(int(n) for n in re.findall(r"^### M-(\d+) ", led, re.M)) + 1
D = {"X3": f"M-{nm}", "X4": f"M-{nm + 1}"}
assert D == {"X3": "M-94", "X4": "M-95"}, D
f4 = lambda x: f"{x:+.4f}"
ci4 = lambda c: f"[{c[0]:+.4f}, {c[1]:+.4f}]"
e1 = lambda x: f"{x:.1e}"
head = lambda mid, scr, a: (
    f"**Records** {mid}'s reading exactly as `{scr}` returned it, as committed before any of its data existed (commit "
    f"`{prereg}`). The artifact records the script's SHA-256, which equals {mid}'s, and the commit it ran at "
    f"(`{a['git_head'][:7]}`, after F5's training gate, `docs/presubmission/round4/f5_gate.json`). Discharges {mid}. "
    f"Exploratory; no discharged rule is re-opened.")

# ---------------------------------------------------------------- X3
x3 = J(RULES["M-86"][1]); r3, p3, a3, s3 = x3["reading"], x3["part_of_rule"], x3["alongside"], x3["assertions"]
st = p3["per_episode_sign_test_h368"]
folds = p3["per_fold_h368"]
fold_name = lambda k: "{" + ", ".join(k) + "}"
h1 = a3["h1_m64_units"]
x3_entry = f"""
### {D['X3']} — Rule X3 (M-86): `results/x3_cross_fold.json` returns {r3['label']} · **NEW**
{head('M-86', RULES['M-86'][2], x3)}

**Assertions, before any reading:** all passed. (a) `fold_split` on {{1, 8}} gives `make_split`'s {s3['a']['n_windows']} training
windows (SHA-256 both ways); (b) F1's bitwise reproduction, read from `{s3['b']['source']}`; (c) every new fold's training set
excludes exactly its two episodes; (d) fold {{1, 8}} reproduces the committed held-out relative-L1, maximum difference
{e1(s3['d']['armA_per_trajectory_max_abs_diff'])} (Arm A per trajectory), {e1(s3['d']['armA_three_seed_max_abs_diff'])} (Arm A three-seed) and
{e1(s3['d']['armB_per_seed_max_abs_diff'])} (Arm B per seed), against {e1(s3['d']['tolerance'])}; (e) `boot_cluster` reproduces
`results/a1_ab_by_horizon.json`'s intervals, {e1(s3['e']['max_abs_diff'])}; (f) M-64's machinery reproduces its cell C,
{e1(s3['f']['max_abs_diff'])}; (g) `boot_ci` and `sign_p`, {e1(s3['g']['boot_ci_max_abs_diff'])} and {e1(s3['g']['sign_p_max_abs_diff'])};
(h) every run's record as queued.

**The reading**, h = {r3['h']}, the five folds' held-out pairs pooled, {r3['n_trajectories']} non-overlapping 400-step trajectories,
Arm A and Arm B at {x3['design']['iterations']:,} iterations, seeds {', '.join(map(str, x3['design']['seeds']))}: gap (seed-mean Arm B − seed-mean
Arm A, relative-L1) = {f4(r3['gap'])} {ci4(r3['ci95'])}, which returns **{r3['label']}**.

**Part of the rule, reported verbatim, no verdict of its own:**
- the per-episode sign test at h = {r3['h']}: {st['n_positive']} of {st['n_episodes']} episodes positive, {st['n_negative']} negative,
  exact two-sided P = {st['exact_two_sided_p']:.9g}. Per-episode mean gaps: {'; '.join(f"{e} {f4(v)}" for e, v in sorted(st['per_episode_mean_gap'].items(), key=lambda t: int(t[0])))};
- each fold's gap at h = {r3['h']} with its exact interval over its {folds['18']['n_trajectories']} trajectories:
  {'; '.join(f"{fold_name(k)} {f4(v['gap'])} {ci4(v['ci95_exact'])}" for k, v in folds.items())}.

**Alongside, never governing:**
- h = 100: gap {f4(a3['h100']['gap'])} {ci4(a3['h100']['ci95'])} over {a3['h100']['n_trajectories']} trajectories, would carry
  {a3['h100']['label_it_would_carry']};
- h = 1 on M-64's {h1['unit_length']}-row units, {h1['n_units']} units ({', '.join(f"{fold_name(k)} {v}" for k, v in h1['units_per_fold'].items())}):
  gap (B − A, negative is teacher forcing ahead) {f4(h1['gap'])} {ci4(h1['gap_ci_unit_level'])} at the unit level; the
  episode-level footnote interval is {ci4(h1['footnote_episode_level']['gap_ci'])};
- the ratio of means, Arm B's over Arm A's: {'; '.join(f"h = {h} {v:.3f}" for h, v in a3['ratio_B_over_A'].items())}.

Caveats, as M-86 states them: {'; '.join(x3['caveats'])}.
**Evidence** `RUN` `results/x3_cross_fold.json`; `SRC` `scripts/x3_cross_fold.py`.
**Status** CONFIRMED · **Relevance** METHOD
"""

# ---------------------------------------------------------------- X4
x4 = J(RULES["M-87"][1]); r4, a4, s4 = x4["reading"], x4["alongside"], x4["assertions"]
pb = lambda b: (f"{b['result']}, D {f4(b['D'])} {ci4(b['ci95'])}, p {b['p']:.4g}, Holm rank {b['rank']} at level "
                f"{b['level']:g}")
x4_entry = f"""
### {D['X4']} — Rule X4 (M-87): `results/x4_matched_baselines.json` returns {r4['label']} · **NEW**
{head('M-87', RULES['M-87'][2], x4)}

**Assertions, before any reading:** all passed. (a) `baselines_eval.evaluate` on the original-size autoregressive baselines
reproduces `results/baselines_eval.json`, {s4['a']['n_values']} values, maximum difference {e1(s4['a']['max_abs_diff'])}; (b)
`verdict_baselines.family` reproduces M-76's governing verdict ({s4['b']['verdict']}), {e1(s4['b']['max_abs_diff'])}; (c) each
matched model is within ±5% of RWM's {s4['c']['rwm_state_pathway']:,}-parameter state pathway (MLP {x4['n_params']['mlp']:,},
transformer {x4['n_params']['transformer']:,}); (d) every matched run's record as queued.

**The reading**, h = {r4['h']}, relative-L1, {x4['design']['arena']} (n_independent = {x4['design']['n_independent']}), matched
baselines trained autoregressively, {x4['design']['iterations']:,} iterations, seeds {', '.join(map(str, x4['design']['seeds']))}, against
{x4['design']['rwm']}: **{r4['label']}**.
- MLP (BASELINE_SPECS.md row 33): {pb(r4['per_baseline']['mlp'])};
- transformer (row 34): {pb(r4['per_baseline']['transformer'])}.

D is the baseline's error minus RWM's (positive: RWM better). Per-trajectory differences: MLP
{', '.join(f4(v) for v in r4['per_baseline']['mlp']['per_traj'])}; transformer {', '.join(f4(v) for v in r4['per_baseline']['transformer']['per_traj'])}.

**Alongside, never governing:**
- h = 100: {a4['l1_h100']['verdict']}; MLP {pb(a4['l1_h100']['per_baseline']['mlp'])}; transformer {pb(a4['l1_h100']['per_baseline']['transformer'])};
- h = 32: {a4['l1_h32']['verdict']}; MLP {pb(a4['l1_h32']['per_baseline']['mlp'])}; transformer {pb(a4['l1_h32']['per_baseline']['transformer'])};
- each run's wall clock and seconds per iteration: {'; '.join(f"{k} {v['wall_clock_s'] / 3600:.2f} h, {v['s_per_iter']:.3f} s" for k, v in x4['runs'].items())};
  F1's probes: MLP {x4['probe_s_per_iter']['mlp']:.3f} s and transformer {x4['probe_s_per_iter']['transformer']:.3f} s per iteration.

Caveats, as M-87 states them: {'; '.join(x4['caveats'])}.
**Evidence** `RUN` `results/x4_matched_baselines.json`, `results/x4_matched_baselines_eval.json`; `SRC` `scripts/x4_matched_baselines.py`.
**Status** CONFIRMED · **Relevance** METHOD
"""

# ---------------------------------------------------------------- the Status lines (the sanctioned in-place edit)
new = led.rstrip("\n") + "\n" + x3_entry + x4_entry
returns = {"M-86": r3["label"], "M-87": r4["label"]}
for mid, (rule, art, scr) in RULES.items():
    old = f"**Status** PRE-REGISTERED, NOT YET DISCHARGED — awaits `{art}` · **Relevance** METHOD"
    assert new.count(old) == 1, (mid, new.count(old))
    rec = D[rule]
    new = new.replace(old, f"**Status** PRE-REGISTERED, DISCHARGED by `{art}`. **It returns {returns[mid]}.** Recorded in `{rec}`. · **Relevance** METHOD")
R_ = open(RES, encoding="utf-8").read()
row = re.search(r"^(\| `M-` methodological findings \| )(\d+)( \|)", R_, re.M)
assert row and int(row.group(2)) == nm - 1, row
R_ = R_.replace(row.group(0), f"{row.group(1)}{nm + 1}{row.group(3)}", 1)
os.makedirs(BAK, exist_ok=True)
shutil.copy(L, os.path.join(BAK, "FINDINGS_LEDGER.md.discharge.bak")); shutil.copy(RES, os.path.join(BAK, "RESULTS.md.discharge.bak"))
open(L, "w", encoding="utf-8").write(new)
open(RES, "w", encoding="utf-8").write(R_)
print(f"appended {D['X3']} ({r3['label']}), {D['X4']} ({r4['label']}); Status lines of M-86, M-87 set; RESULTS.md M- {nm - 1} -> {nm + 1}")
