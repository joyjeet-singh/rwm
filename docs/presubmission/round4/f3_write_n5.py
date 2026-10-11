"""F3 item 1: the ledger entry for N5 (post hoc), the next R- entry, and RESULTS.md's R- row. Every figure is read from
results/n5_stale_armA_ci.json. Writes .bak copies outside the repository and refuses to run twice."""
import json, os, re, shutil
L, RES, BAK = "FINDINGS_LEDGER.md", "RESULTS.md", "/Users/Shared/rwm_verify/evidence/R4F3"
art = "results/n5_stale_armA_ci.json"
N = json.load(open(art)); r = N["results"]
assert N["post_hoc"] and all(v["pass"] for v in N["assertions"].values())
led = open(L, encoding="utf-8").read()
nr = max(int(n) for n in re.findall(r"^### R-(\d+) ", led, re.M)) + 1
RID = f"R-{nr}"
assert RID == "R-80" and "N5 (post hoc)" not in led
cell = lambda k, a, h: r[k][a]["by_horizon"][str(h)]
fe = lambda c: f"{c['E_pct']:+.1f}% [{c['ci95_pct'][0]:+.1f}, {c['ci95_pct'][1]:+.1f}]"
line = lambda k, a: "; ".join(f"h = {h} {fe(cell(k, a, h))}" for h in N["horizons"])
entry = f"""
### {RID} — N5 (post hoc): our models' error under the stale action timing, with intervals at every horizon in both arenas, and the forecast shift · **NEW**
**Post hoc.** Computed after the data existed, as round 4's remedy for §7.2, which set a −0.99% (held-out, unresolved) beside a
+124.6% (training episodes) with no intervals and no explanation (PLAN round 4, item 1 and Annex 3). It re-opens no rule and
changes no verdict. Rule X2's machinery is imported from `scripts/action_sensitivity.py`: its models, arenas, rollout hook,
per-trajectory errors, Δ and interval. N5 extends X2's horizons from h ≤ 100 to all six.

**Assertions:** at h ≤ 100, every model's and arena's E, interval and Δ equal X2's stale-action cells in
`results/action_sensitivity.json` ({N['assertions']['a']['n_cells']} cells, maximum difference {N['assertions']['a']['max_abs_diff']:.1e}).
Arm A's three-seed E on the held-out pair, and the released checkpoint's E and interval, equal `results/alignment_by_horizon.json`
(R-79's corrected block and the released block) at every horizon ({N['assertions']['b']['max_abs_diff']:.1e}).

**E** = err(stale) / err(causal) − 1, relative-L1 cumulative over steps 1..h. For our arms it is the mean over seeds 0-2 of each seed's
E. The interval is 95% over whole trajectories: exact at n = 4, 20,000 Monte Carlo draws at n = 16 and 20.
- **Arm A, 10,000 iterations, its own training episodes (16 trajectories):** {line('arm_a_10000', 'in_sample_n16')}.
- **Arm A, 10,000, the held-out pair (4):** {line('arm_a_10000', 'held_out_n4')}.
- Arm A, 2,500, training episodes: {line('arm_a_2500', 'in_sample_n16')}; held-out pair: {line('arm_a_2500', 'held_out_n4')}.
- Arm B, 10,000, training episodes: {line('arm_b_10000', 'in_sample_n16')}; held-out pair: {line('arm_b_10000', 'held_out_n4')}.
- Arm B, 2,500, training episodes: {line('arm_b_2500', 'in_sample_n16')}; held-out pair: {line('arm_b_2500', 'held_out_n4')}.
- The released checkpoint, all ten episodes (its own training data, 20): {line('released', 'all_ten_n20')}; held-out pair:
  {line('released', 'held_out_n4')}.

**The forecast shift Δ** is the relative-L1 of the stale-timing forecast against the causal one, which is 0 for a model that ignores the
action. At h = 8, on each model's own training data, it is {cell('arm_a_10000', 'in_sample_n16', 8)['delta']:.3f} for Arm A at 10,000 and
{cell('released', 'all_ten_n20', 8)['delta']:.3f} for the released checkpoint. Their errors at the causal timing there are
{cell('arm_a_10000', 'in_sample_n16', 8)['err_causal']:.3f} and {cell('released', 'all_ten_n20', 8)['err_causal']:.3f}. Every model's Δ and
causal error, at every horizon and arena, are in the artifact.
**Evidence** `RUN` `{art}`; `SRC` `scripts/n5_stale_armA_ci.py`, `scripts/action_sensitivity.py`.
**Status** CONFIRMED · **Relevance** CONTRIB
"""
R_ = open(RES, encoding="utf-8").read()
row = re.search(r"^\| `R-` measured results \| (\d+) \|", R_, re.M)
assert row and int(row.group(1)) == nr - 1, row
R_ = R_.replace(row.group(0), f"| `R-` measured results | {nr} |", 1)
os.makedirs(BAK, exist_ok=True)
shutil.copy(L, os.path.join(BAK, "FINDINGS_LEDGER.md.n5.bak")); shutil.copy(RES, os.path.join(BAK, "RESULTS.md.n5.bak"))
open(L, "w", encoding="utf-8").write(led.rstrip("\n") + "\n" + entry)
open(RES, "w", encoding="utf-8").write(R_)
print(f"appended {RID}; RESULTS.md R- {nr - 1} -> {nr}")
