"""F3 item 2: the ledger correction entry for N6 (post hoc), the next D- entry, and RESULTS.md's D- row. Every figure is
read from results/a2_trajectory_level_control.json, docs/presubmission/round4/f3_n6_check.json (old -> new for every
difficulty-derived field), results/step4_0a_results.json and results/paper_numbers.json against PRE (the commit before N6).
Writes .bak copies outside the repository and refuses to run twice."""
import json, os, re, shutil, subprocess
L, RES, BAK = "FINDINGS_LEDGER.md", "RESULTS.md", "/Users/Shared/rwm_verify/evidence/R4F3"
PRE = "9857c5d"
A2, CHK, S4, PN = ("results/a2_trajectory_level_control.json", "docs/presubmission/round4/f3_n6_check.json",
                   "results/step4_0a_results.json", "results/paper_numbers.json")
a = json.load(open(A2))["h1_diagnostic"]
c = json.load(open(CHK))
retest = json.load(open(S4))["d12_retest"]
assert c["non_derived_unchanged"] and c["ruling_W5_passes"] and not c["sign_flips"] and not c["verdict_changes"]
assert "causal" in a["difficulty_source"] and a["collapses"] is False
lo, hi = a["episode_difficulty_range"]
assert abs(lo - retest["1"]["min"]) < 1e-12 and abs(hi - retest["1"]["max"]) < 1e-12, "range is not d12_retest['1']"
ch = c["derived_changes"]
D = "h1_diagnostic/confounders/episode_difficulty_D12/"
old = lambda p: ch[p][0]
new = lambda p: ch[p][1]
pn_old = json.loads(subprocess.run(["git", "show", f"{PRE}:{PN}"], capture_output=True, text=True, check=True).stdout)
pn_new = json.load(open(PN))
pv = lambda d, k: (d.get("numbers", d)[k]["value"] if isinstance(d.get("numbers", d)[k], dict) else d.get("numbers", d)[k])
KEYS = ("d12_lo", "d12_hi", "a2_h1_diff_r", "a2_h1_partial_both")
keys = {k: (pv(pn_old, k), pv(pn_new, k)) for k in KEYS}
assert keys["d12_lo"][1] == f"{lo:.3f}" and keys["a2_h1_diff_r"][1] == f"{new(D + 'r_disagreement_vs_confounder'):+.3f}"
led = open(L, encoding="utf-8").read()
nd = max(int(n) for n in re.findall(r"^### D-(\d+) ", led, re.M)) + 1
DID = f"D-{nd}"
assert DID == "D-39" and "N6 (post hoc)" not in led
for e in ("D-37", "R-69", "M-62"):
    assert re.search(rf"^### {e} ", led, re.M), e
f3 = lambda x: f"{x:+.3f}"
f5 = lambda x: f"{x:+.5f}"
rng = lambda p0, p1: f"{p0:.3f} to {p1:.3f}"
entry = f"""
### {DID} — N6 (post hoc): the paper's per-episode difficulty is now measured at the causal action timing alone (corrects D-37) · **NEW**
**Corrects** D-37, whose last paragraph records that the paper's per-episode difficulty is the mean of two measurements of
the released checkpoint, one at the stale action timing and one at the causal timing, and R-69 and M-62, which quote figures
from that mean. None of the three is edited.

**What changed.** `scripts/a2_trajectory_level_control.py` built each episode's difficulty as the mean of
`per_episode_e["0"]` and `per_episode_e["1"]` in `results/step4_0a_results.json`, and its comment called the two keys seeds.
They are the two action offsets (D-37). The script now reads `per_episode_e["1"]`, the causal timing, alone, and the
artifact's `difficulty_source` says so. Four lines are edited, in place (265, 268, 304 and 305); the line count is
unchanged, so no cited line moves.

**Why the causal timing.** The measure is meant to describe how hard each episode is to forecast. The stale timing is the
released evaluation code's pairing, which pairs each predicted state with the action one step before the one that produced it
(B-05, D-13). Averaging it in mixed that evaluation defect into what should be a property of the episode. The causal timing is
the pairing D-13 establishes as correct and the one the released checkpoint was trained under. Round 4 (PLAN objection O9)
recomputes the measure at it; this is post hoc, re-opens no rule and changes no verdict.

**What moved** (`docs/presubmission/round4/f3_n6_check.json`, the regenerated artifact against its committed predecessor,
{c['n_leaves']} fields). Every field not built from the difficulty measure is unchanged to 1e-12. At h = 1, over
{a['n_points']} trajectories:
- the range across the ten episodes: {rng(*[old(f'h1_diagnostic/episode_difficulty_range[{i}]') for i in (0, 1)])} →
  {rng(lo, hi)}, which is `d12_retest["1"]` in `results/step4_0a_results.json` ({retest['1']['ratio']:.2f}-fold, as D-37 recorded);
- the correlation of disagreement with difficulty: {f3(old(D + 'r_disagreement_vs_confounder'))} → {f3(new(D + 'r_disagreement_vs_confounder'))};
- the correlation of error with difficulty: {f3(old(D + 'r_error_vs_confounder'))} → {f3(new(D + 'r_error_vs_confounder'))};
- the disagreement–error correlation with difficulty partialled out: {f5(old(D + 'partial_r'))} → {f5(new(D + 'partial_r'))}, interval
  [{old(D + 'partial_ci[0]'):+.3f}, {old(D + 'partial_ci[1]'):+.3f}] → [{new(D + 'partial_ci[0]'):+.3f}, {new(D + 'partial_ci[1]'):+.3f}];
- with difficulty and commanded speed both partialled out: {f5(old('h1_diagnostic/partial_on_both'))} → {f5(new('h1_diagnostic/partial_on_both'))};
- the shrinkage from partialling difficulty: {f5(old(D + 'shrinkage'))} → {f5(new(D + 'shrinkage'))}.

**Ruling W5** (PLAN round 4): no verdict changes (`collapses` stays {a['collapses']}), and no correlation or partial changes
sign. It passes.

**Entries whose figures change.**
- D-37: "the paper uses their mean" no longer holds. The paper uses the causal range D-37 records, {rng(lo, hi)}.
- R-69: "+0.040 with per-episode difficulty (D-12)" is now {f3(new(D + 'r_disagreement_vs_confounder'))}. "Partialling both out
  … leaves +0.995" is unchanged at three decimals. Its conclusion, that the h = 1 figure does not collapse, stands.
- M-62: "spans 0.562 to 1.591 across the dataset" is now {rng(lo, hi)}. The range only motivates M-62's question; its design,
  its cells and `scripts/m62_episode_clustering.py` do not read it.

**Paper keys** (`results/paper_numbers.json`, re-bound by the fast build; the template is not edited in this session). All
four are in Appendix N:
- `d12_lo` {keys['d12_lo'][0]} → {keys['d12_lo'][1]} and `d12_hi` {keys['d12_hi'][0]} → {keys['d12_hi'][1]} ("Per-episode difficulty spans … to …");
- `a2_h1_diff_r` {keys['a2_h1_diff_r'][0]} → {keys['a2_h1_diff_r'][1]} ("… with per-episode difficulty");
- `a2_h1_partial_both` {keys['a2_h1_partial_both'][0]} → {keys['a2_h1_partial_both'][1]}.

The partial on difficulty alone is bound to no key (`docs/presubmission/round4/PREFLIGHT.md`, PF7).
**Evidence** `RUN` `results/a2_trajectory_level_control.json`, `results/step4_0a_results.json`, `results/paper_numbers.json`; `SRC` `scripts/a2_trajectory_level_control.py`, `scripts/paper_numbers.py`.
**Status** CONFIRMED · **Relevance** METHOD
"""
R_ = open(RES, encoding="utf-8").read()
row = re.search(r"^(\| `D-` dataset properties and paper-verification findings \| )(\d+)( \|)", R_, re.M)
assert row and int(row.group(2)) == nd - 1, row
R_ = R_.replace(row.group(0), f"{row.group(1)}{nd}{row.group(3)}", 1)
os.makedirs(BAK, exist_ok=True)
shutil.copy(L, os.path.join(BAK, "FINDINGS_LEDGER.md.n6.bak")); shutil.copy(RES, os.path.join(BAK, "RESULTS.md.n6.bak"))
open(L, "w", encoding="utf-8").write(led.rstrip("\n") + "\n" + entry)
open(RES, "w", encoding="utf-8").write(R_)
print(f"appended {DID}; RESULTS.md D- {nd - 1} -> {nd}")
for k, (o, n) in keys.items():
    print(f"  {k}: {o} -> {n}")
