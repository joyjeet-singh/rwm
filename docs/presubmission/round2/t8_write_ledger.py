"""Round 2, T8 item 1: record rule X1's final reading (ledger M-80) in a new entry, exactly as
scripts/rssm_diagnostics.py --part c returned it, with every figure read from results/rssm_diagnostics.json;
change M-80's Status line at discharge (PLAN 1.2.3's one sanctioned in-place edit); keep RESULTS.md's
per-prefix count row in step (ledger_check.py requires it). Asserts before writing; .bak beside each file."""
import json
import re
import shutil

D = json.load(open("results/rssm_diagnostics.json"))
assert D["final_reading"] and D["part_c"], "Part C has not run"
L = open("FINDINGS_LEDGER.md").read()
nums = [int(x) for x in re.findall(r"^### M-(\d+) ", L, re.M)]
NEW = f"M-{max(nums) + 1}"
assert NEW == "M-83", NEW
H = D["arena"]["horizons"]
f = lambda x: f"{x:.4f}"
rows = []
for v, r in D["part_c"].items():
    m = r["per_seed_mean_l1"]["0"]
    rows.append(f"| {v} (`{r['spec']}`) | " + " | ".join(f(m[h]) for h in H) + " | " +
                ", ".join(f"{x:+.4f}" for x in r["seed0_per_traj_minus_floor"]) + f" | {'yes' if r['seed0'] else 'no'} |")
floor = "| hold-last floor | " + " | ".join(f(D["floor_mean"][h]) for h in H) + " | | |"
entry = f"""
### {NEW} — Rule X1 (M-80), Part C and final reading: `results/rssm_diagnostics.json` returns {D["final_reading"]} · **NEW**
**Records** M-80's Part C reading and its final reading, exactly as `scripts/rssm_diagnostics.py --part c` returned them, as
committed before any reading existed (commit `2433f44`). Discharges M-80. Exploratory; M-75 and M-76 are unchanged.

**Part C.** Teacher-forced RSSM, seed 0, 2,500 iterations; held-out pair, relative-L1, mode read-out; the reading horizon is
h = {D["arena"]["horizons"][2]}.

| variant | {" | ".join(f"h = {h}" for h in H)} | per-trajectory minus floor at h = {H[2]} | rescues on seed 0 |
|---|{"---|" * len(H)}---|---|
{chr(10).join(rows)}
{floor}

**Final reading: {D["final_reading"]}.**
**Evidence** `RUN` `results/rssm_diagnostics.json`, `results/baseline_run_rssm_tf_x1v1_seed0.json`, `results/baseline_run_rssm_tf_x1v2_seed0.json`; `SRC` `scripts/rssm_diagnostics.py`.
**Status** CONFIRMED · **Relevance** METHOD
"""
old_status = "**Status** PRE-REGISTERED, NOT YET DISCHARGED — awaits `results/rssm_diagnostics.json` · **Relevance** METHOD"
assert L.count(old_status) == 1
new_status = (f"**Status** PRE-REGISTERED, DISCHARGED by `results/rssm_diagnostics.json`. **It returns "
              f"{D['final_reading']}.** Recorded in `{NEW}`. · **Relevance** METHOD")
L2 = L.replace(old_status, new_status).rstrip("\n") + "\n" + entry
R = open("RESULTS.md").read()
row = "| `M-` methodological findings | 82 |"
assert R.count(row) == 1
R2 = R.replace(row, "| `M-` methodological findings | 83 |")
shutil.copy("FINDINGS_LEDGER.md", "FINDINGS_LEDGER.md.bak"); shutil.copy("RESULTS.md", "RESULTS.md.bak")
open("FINDINGS_LEDGER.md", "w").write(L2)
open("RESULTS.md", "w").write(R2)
print(f"wrote {NEW}; M-80 discharged: {D['final_reading']}")
