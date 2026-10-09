"""R5 item H3: two ledger corrections, each a new entry naming the one it corrects.

  C-13 names Table S7 for the paper's 2,500 iterations; the count is in Table S9.
  D-12 gives 0.601-1.674 where the paper gives 0.562-1.591; the entry states each definition and which the
  paper uses.

Neither corrected entry is edited (the ledger is append-only, and neither is retracted: both claims stand).
Every figure is read from the artifact it describes. Writes .bak copies first, asserts before writing, and
refuses to run twice. Run from the repository root.
"""
import json
import re
import shutil

L, RES = "FINDINGS_LEDGER.md", "RESULTS.md"
BAK = "/Users/Shared/rwm_verify/evidence/R3R5"
SRC_TXT = "docs/presubmission/sources/2501.10100v1.txt"     # gitignored text extraction of the paper
led = open(L, encoding="utf-8").read()
assert "(corrects C-13)" not in led and "(corrects D-12)" not in led, "already run"


def next_id(p):
    n = max(int(x) for x in re.findall(rf"^### {p}-(\d+) ", led, re.M)) + 1
    return f"{p}-{n:02d}"


CID, DID = next_id("C"), next_id("D")
assert (CID, DID) == ("C-16", "D-37"), (CID, DID)

# ---- C-13: which table holds the 2,500 ------------------------------------------------------------
src = open(SRC_TXT, encoding="utf-8").read().splitlines()
ln = {m.group(1): i + 1 for i, s in enumerate(src) for m in [re.match(r"TABLE (S\d+): ", s)] if m}
title = {k: src[v - 1].split(": ", 1)[1].strip() for k, v in ln.items()}
assert title["S6"] == "RWM architecture" and title["S7"] == "Baseline architecture", title
assert title["S9"] == "RWM training parameters", title
s9 = src[ln["S9"] - 1:ln["S10"] - 1]
i_it = next(i for i, s in enumerate(s9) if s.strip() == "| max iterations")
assert s9[i_it + 2].strip() == "| [2500]", s9[i_it:i_it + 3]
it_line = ln["S9"] + i_it + 2
assert "forecast decay" in " ".join(s9) and "max iterations" not in " ".join(src[ln["S7"] - 1:ln["S8"] - 1])


def body(eid):
    s = led.index(f"### {eid} ")
    e = led.find("\n### ", s + 5)
    return led[s:len(led) if e < 0 else e]


# Every other entry that names Table S7 for something Table S7 does not hold. Asserted, not assumed.
assert "| Paper, Table S7 | **2500** |" in body("C-13") and "`EXT` paper Table S7" in body("C-13")
assert "2500 (paper Table S7)" in body("C-12")
assert "the count the paper's Table S7 states" in body("R-26")
assert "(paper Table S7)" in body("O-12")
assert "early read of the paper's Table S7" in body("C-08") and "SUPERSEDED BY C-09" in body("C-08")
assert "Table S7 of the paper describes a single base" in body("C-03")
assert "| base\n | GRU" in "\n".join(src[ln["S6"] - 1:ln["S7"] - 1])

entry_c = f"""
### {CID} — C-13 names the wrong table: the paper's 2,500 iterations are in Table S9, not Table S7 (corrects C-13) · **NEW**
**Corrects** C-13, whose table row and evidence line name "Table S7". C-13's claim is unchanged: the release
states three training lengths, 500, 2,500 and 5,000. Only the table number was wrong.

In arXiv:2501.10100v1, Table S7 is "{title['S7']}", the MLP, RSSM and transformer baselines (Appendix A-B2).
The 2,500 is the "max iterations" row of Table S9, "{title['S9']}" (Appendix A-C1), which also holds the
forecast horizon and the forecast decay α. The text extraction this was checked against is `{SRC_TXT}`
(Table S9 at line {ln['S9']}, the 2,500 at line {it_line}); like the other source texts it is gitignored.

The same table number appears in five other entries, for things Table S7 does not hold:
- C-12's table, O-12's table and R-26 name Table S7 for the 2,500 count. It is Table S9's.
- C-08's evidence line reads the forecast decay from "Table S7". It is in Table S9. C-08 is already
  superseded by C-09.
- C-03 says "Table S7 of the paper describes a single base". The RWM's own architecture, a single GRU base
  with MLP heads, is Table S6, "{title['S6']}". C-03's claim stands with Table S6 in place of Table S7.

None of these entries is edited. The paper cites Table S9 for the iteration count.
**Evidence** `EXT` arXiv:2501.10100v1, Appendix A-C1, Table S9; Appendix A-B, Tables S6 and S7.
**Status** CONFIRMED · **Relevance** METHOD
"""

# ---- D-12: the two difficulty ranges ---------------------------------------------------------------
rep = open("results/step3_report.txt", encoding="utf-8").read()
m = re.search(r"spread across episodes: ([\d.]+) to ([\d.]+)\s+\(mean ([\d.]+)\)", rep)
d12_lo, d12_hi, d12_mean = m.groups()
assert f"spans {d12_lo} to {d12_hi} (mean {d12_mean})" in body("D-12")
assert "`RUN` `step3_report.txt`" in body("D-12")
s4 = json.load(open("results/step4_0a_results.json"))
pe, rt = s4["per_episode_e"], s4["d12_retest"]
assert sorted(pe) == ["0", "1"]
step3_vals = {int(a): float(b) for a, b in re.findall(r"^\s+(\d)\s+[\d.]+\s+([\d.]+)", rep.split(
    "Per-episode difficulty")[1].split("spread across")[0], re.M)}
assert len(step3_vals) == 10 and all(abs(pe["0"][str(e)] - v) < 5e-5 for e, v in step3_vals.items())
A2 = json.load(open("results/a2_trajectory_level_control.json"))["h1_diagnostic"]
avg = {e: (pe["0"][e] + pe["1"][e]) / 2 for e in pe["0"]}
lo2, hi2 = A2["episode_difficulty_range"]
assert abs(min(avg.values()) - lo2) < 1e-12 and abs(max(avg.values()) - hi2) < 1e-12   # A2 = the offset mean
assert "averaged over the seeds" in A2["difficulty_source"]
pn = open("scripts/paper_numbers.py", encoding="utf-8").read()
assert 'put("d12_lo", f\'{_h1["episode_difficulty_range"][0]:.3f}\'' in pn          # the paper reads A2's
a2s = open("scripts/a2_trajectory_level_control.py", encoding="utf-8").read()
a2_line = a2s[:a2s.index("# D-12's per-episode difficulty, averaged over the seeds")].count("\n") + 1
s4s = open("scripts/step4_0a_restate.py", encoding="utf-8").read()
assert "OFFSETS = (0, 1)" in s4s and '"per_episode_e": {str(o): ep_e[o] for o in OFFSETS}' in s4s
sr = open("src/score_reference.py", encoding="utf-8").read()
assert "def rollout(self, state, action, start_step=32, action_offset=0" in sr
assert "pred, *_ = model.rollout(st, ac, E.START_STEP)\n        val = float(per_traj_e(pred, st).mean())" in sr
assert "n_traj=20, seed=7" in sr and "n_traj=20, seed=7" in s4s
r0, r1 = rt["0"], rt["1"]
assert s4["d12_survives"] and r1["ratio"] > 2 and abs(r1["corr_with_speed"]) < 0.3

entry_d = f"""
### {DID} — D-12's range and the paper's are the same measurement at different action alignments; the paper uses their mean (corrects D-12) · **NEW**
**Corrects** D-12, which gives per-episode difficulty as {d12_lo} to {d12_hi} citing `step3_report.txt` without
naming its action alignment, where §6.7 gives {lo2:.3f} to {hi2:.3f}. Both score the released checkpoint the same way, and differ
only in the action alignment (D-13):
- **D-12's range** (`results/step3_report.txt`, Step 3, written by `src/score_reference.py`). For each episode,
  20 trajectories of 400 steps drawn inside it (sampling seed 7), rolled out from step 32. The score is relative-L1
  per trajectory over the remaining steps, averaged over the 20. The rollout uses `action_offset=0`, the stale
  alignment the released evaluation code uses (B-05). `scripts/step4_0a_restate.py` reruns the same loop at both
  alignments; its offset-0 column, `per_episode_e["0"]` in `results/step4_0a_results.json`, reproduces Step 3's
  ten values.
- **The paper's range** (`results/a2_trajectory_level_control.json`, `h1_diagnostic.episode_difficulty_range`,
  written by `scripts/a2_trajectory_level_control.py`). For each episode, the mean of `per_episode_e["0"]` and
  `per_episode_e["1"]`: the same measurement at the stale alignment and at the causal one, averaged. The script's
  comment (`scripts/a2_trajectory_level_control.py:{a2_line}`) and the artifact's `difficulty_source` call the two
  keys "seeds". They are the two action offsets.

**The paper uses the second.** `scripts/paper_numbers.py` reads `d12_lo` and `d12_hi` from the A2 artifact, and
§6.7 partials that per-episode quantity out at h = 1. At the causal alignment alone (`per_episode_e["1"]`) the range
is {r1['min']:.3f} to {r1['max']:.3f}. D-12's two conclusions hold at either alignment
(`results/step4_0a_results.json`, `d12_retest`): the spread is {r0['ratio']:.2f}-fold at the stale alignment and
{r1['ratio']:.2f}-fold at the causal one, and the correlation with commanded speed is {r0['corr_with_speed']:+.3f} and
{r1['corr_with_speed']:+.3f}. D-12 is not edited.
**Evidence** `RUN` `results/step3_report.txt`, `results/step4_0a_results.json`, `results/a2_trajectory_level_control.json`; `SRC` `src/score_reference.py`, `scripts/step4_0a_restate.py`, `scripts/a2_trajectory_level_control.py`, `scripts/paper_numbers.py`.
**Status** CONFIRMED · **Relevance** METHOD
"""

new_led = led.rstrip("\n") + "\n" + entry_c + entry_d
R = open(RES, encoding="utf-8").read()
rows = {}
for p, label in (("C", "`C-` paper says one thing, code does another"),
                 ("D", "`D-` dataset properties and paper-verification findings")):
    mm = re.search(rf"^\| {re.escape(label)} \| (\d+) \|", R, re.M)
    n_now = int(re.findall(rf"^### {p}-(\d+) ", led, re.M)[-1])
    assert mm and int(mm.group(1)) == len(re.findall(rf"^### {p}-\d+ ", led, re.M)), (p, mm and mm.group(1))
    rows[p] = (mm.group(0), mm.group(0).replace(f"| {mm.group(1)} |", f"| {int(mm.group(1)) + 1} |"))
for old, new in rows.values():
    assert R.count(old) == 1
    R = R.replace(old, new)
shutil.copy(L, f"{BAK}/FINDINGS_LEDGER.md.h3.bak")
shutil.copy(RES, f"{BAK}/RESULTS.md.h3.bak")
open(L, "w", encoding="utf-8").write(new_led)
open(RES, "w", encoding="utf-8").write(R)
print(f"appended {CID} and {DID}; RESULTS.md C- and D- rows incremented")
