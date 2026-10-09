"""R1 item 4: discharge rule X2. Appends the next M- entry recording each Arm A reading exactly as
scripts/action_sensitivity.py returned it, with the alongside values and no interpretation; sets M-84's Status line (the
one sanctioned in-place edit); moves RESULTS.md's M- row. Every figure is read from results/action_sensitivity.json.
Writes .bak copies first and refuses to run twice. Run from the repository root.
"""
import json
import re
import shutil
import subprocess

L, RES, ART = "FINDINGS_LEDGER.md", "RESULTS.md", "results/action_sensitivity.json"
led = open(L, encoding="utf-8").read()
nm = max(int(n) for n in re.findall(r"^### M-(\d+) ", led, re.M)) + 1
MID = f"M-{nm:02d}"
assert MID == "M-85", MID
assert "Rule X2 (M-84)" not in led
O = json.load(open(ART))
assert O["ledger"] == "M-84" and O["script_sha256"] in led            # the pre-registered script ran
prereg = subprocess.run(["git", "log", "--format=%h", "-S", "### M-84 ", "--", L],
                        capture_output=True, text=True).stdout.split()[-1]
rd, al, A_ = O["readings"], O["alongside"], O["assertions"]
labels = {rd[k]["reading"] for k in rd}
assert len(labels) == 1, labels                     # the Status line below names one outcome for both checkpoints
verdict = labels.pop()
f = lambda x: f"{x['E_pct']:+.2f}% [{x['ci95_pct'][0]:+.2f}, {x['ci95_pct'][1]:+.2f}]"
b_ok = all(v["every_window_input_differs"] and v["every_window_later_step_input_differs"]
           and v["every_window_forecast_differs"] and v["later_steps_read_the_offset_rows"] for v in A_["b"].values())
assert A_["a"]["passed"] and b_ok and all(A_["c"].values())
names = {"arm_b_2500": "Arm B, 2,500 iterations", "arm_b_10000": "Arm B, 10,000 iterations",
         "released": "the released checkpoint"}
arena = {"in_sample_n16": "in-sample arena, n = 16", "all_ten_n20": "all ten episodes, n = 20"}

entry = f"""
### {MID} — Rule X2 (M-84): `{ART}` returns {verdict} at 2,500 and at 10,000 iterations · **NEW**
**Records** M-84's two readings exactly as `scripts/action_sensitivity.py` returned them, as committed before any reading
existed (commit `{prereg}`). The artifact records the script's SHA-256, which equals M-84's, and the commit it ran at
(`{O['git_head'][:7]}`). Discharges M-84. Exploratory; M-23, M-64 and M-74-M-76 are unchanged.

**Assertions, before any reading:**
- (a) passed, {A_['a']['n_checks']} comparisons;
- (b) passed in all {len(A_['b'])} model × arena cases;
- (c) passed in all {len(A_['c'])} cases.

CPU: {O['cpu']['total_cpu_s'] / 60:.1f} min against the cap of {O['cpu']['cap_cpu_min']:.0f}. The projections after the first
model were {O['cpu']['projection_after_first_model_cpu_min']['phase1']:.1f} (phase 1) and
{O['cpu']['projection_after_first_model_cpu_min']['phase2']:.1f} (phase 2) CPU-min.

**The readings:** E under I2 (swap), h = 8, in-sample arena (n = 16), Arm A three-seed mean, 95% interval:
- Arm A, 2,500 iterations: E = {f(rd['arm_a_2500'])}, which returns **{rd['arm_a_2500']['reading']}**;
- Arm A, 10,000 iterations: E = {f(rd['arm_a_10000'])}, which returns **{rd['arm_a_10000']['reading']}**.

**Alongside, not readings** (the same statistic, and the label it would carry):
""" + "\n".join(f"- {names[k]} ({arena[v['arena']]}): E = {f(v)}, would carry {v['label_it_would_carry']};"
                 for k, v in al.items()).rstrip(";") + f""".

Every other cell (interventions I1-I4, horizons 1, 8, 32 and 100, both arenas, with Δ and the context figures) is in the
artifact's `results`, `per_seed` and `context`.
**Evidence** `RUN` `{ART}`; `SRC` `scripts/action_sensitivity.py`.
**Status** CONFIRMED · **Relevance** METHOD
"""

start = led.index("### M-84 — ")
end = led.find("\n### ", start + 5)
end = len(led) if end < 0 else end
blk = led[start:end]
old_st = f"**Status** PRE-REGISTERED, NOT YET DISCHARGED — awaits `{ART}` · **Relevance** METHOD"
assert blk.count(old_st) == 1
new_st = (f"**Status** PRE-REGISTERED, DISCHARGED by `{ART}`. **It returns {verdict} at 2,500 and at 10,000 "
          f"iterations.** Recorded in `{MID}`. · **Relevance** METHOD")
new_led = led[:start] + blk.replace(old_st, new_st) + led[end:]
new_led = new_led.rstrip("\n") + "\n" + entry

R = open(RES, encoding="utf-8").read()
row = re.search(r"^\| `M-` methodological findings \| (\d+) \|", R, re.M)
assert row and int(row.group(1)) == nm - 1
R = R.replace(row.group(0), f"| `M-` methodological findings | {nm} |", 1)
shutil.copy(L, "/Users/Shared/rwm_verify/evidence/R3R1/FINDINGS_LEDGER.md.discharge.bak")
shutil.copy(RES, "/Users/Shared/rwm_verify/evidence/R3R1/RESULTS.md.discharge.bak")
open(L, "w", encoding="utf-8").write(new_led)
open(RES, "w", encoding="utf-8").write(R)
print(f"appended {MID}; M-84 Status -> DISCHARGED ({verdict}); RESULTS.md M- {nm - 1} -> {nm}")
