"""S3 -- append ledger entry S-20, the withdrawal of the alignment defect's 75% / 9.5% framing.

Every figure is read from results/alignment_defect_ci.json, never typed. Append-only: the
script asserts S-20 does not exist, that the last S- entry is S-19, and that RESULTS.md's S-
count reads 19, then appends and moves that one count. The Retracts line names no ID -- the
measurements it rests on (R-15) stand as measured -- following S-15 to S-19.

    python docs/presubmission/s3_write_s20.py
"""
import json
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
A = json.load(open(os.path.join(ROOT, "results", "alignment_defect_ci.json")))
ar = A["arenas"]
h4, h20, pa = ar["held_out_n4"], ar["all_ten_n20"], ar["protocol_a"]
f = lambda x: f"{x:.1f}"
ci = lambda c: f"[{c[0]:.1f}, {c[1]:.1f}]"
pub = A["published"]["pct"]
k_out = max(range(pa["n_trajectories"]),
            key=lambda i: pa["per_trajectory_overstatement_pct"]["nrmse_form1"][i])
rest = [x for i, x in enumerate(pa["per_trajectory_overstatement_pct"]["nrmse_form1"]) if i != k_out]

ENTRY = f"""### S-20 — "The released evaluation overstates its own model's error by 75%" · **NEW**
**Retracts** — a framing, not a numbered claim; the measurements it was computed from stand as measured
**What is retracted:** the size, and the sign-consistency, the paper gave the alignment defect.
The abstract, a contribution bullet, §3.1 and §7.2 said the released evaluation overstates its
checkpoint's error at h = 368 by {pub['nrmse_curve']:.0f}% in nRMSE and {pub['rel_l1']:.1f}% on
relative-L1, and that the checkpoint is "materially better" than its evaluation reports. Those
figures are exactly right for what they measured (`results/alignment_defect_ci.json` reproduces
both at printed precision): {pa['n_trajectories']} windows sampled, as the upstream harness samples
them, from the held-out pair, and **overlapping**. One of them, starting at row
{pa['starts'][k_out]:,}, is overstated by {f(pa['per_trajectory_overstatement_pct']['nrmse_form1'][k_out])}% in
nRMSE form 1 while the other {len(rest)} lie between {f(min(rest))}% and {f(max(rest))}%. The
published nRMSE averages ratios over dimensions at each step, and that lets the one window
dominate.

**What replaces it**, on the paper's own standard of independent trajectories with a cluster
bootstrap:
- **the held-out pair's {h4['n_trajectories']} non-overlapping trajectories:** relative-L1
  {f(h4['overstatement_pct']['rel_l1'])}% {ci(h4['ci95_pct']['rel_l1'])} and nRMSE form 1
  {f(h4['overstatement_pct']['nrmse_form1'])}% {ci(h4['ci95_pct']['nrmse_form1'])};
- **all ten episodes' {h20['n_trajectories']} non-overlapping trajectories:** relative-L1
  {f(h20['overstatement_pct']['rel_l1'])}% {ci(h20['ci95_pct']['rel_l1'])} and nRMSE form 1
  {f(h20['overstatement_pct']['nrmse_form1'])}% {ci(h20['ci95_pct']['nrmse_form1'])}. **The sign
  reverses.**

All of these are in-sample for the released checkpoint, which trained on every episode.

**What is not retracted:**
- the defect itself. Row t holds the action that produced state t (D-13). The evaluation's
  pairing is one step stale (B-05), and the fix is one line;
- R-15's measurements, which are correct for their arena.

What changes is what they license: a real correctness defect, whose cost in error is small and not
consistent in sign.

**Who found it:** PLAN S3 item 4, which asked for intervals on the two figures and set as stop
conditions that the four-trajectory estimates reproduce them, and that the twenty-trajectory
companion not reverse. Neither held. The user ruled "Restate on independent", 2026-09-28
(`docs/presubmission/DECISIONS_FOR_USER.md#S3-alignment-defect`).
**Evidence** `RUN` `results/alignment_defect_ci.json` (`scripts/alignment_defect_ci.py`), `results/step4_0a_results.json`.
**Status** RETRACTED · **Relevance** METHOD
"""


def main():
    lp = os.path.join(ROOT, "FINDINGS_LEDGER.md")
    txt = open(lp, encoding="utf-8").read()
    assert "### S-20 " not in txt, "S-20 exists; the ledger is append-only"
    ss = [int(x) for x in re.findall(r"^### S-(\d+) ", txt, re.M)]
    assert max(ss) == 19 and len(ss) == 19, (max(ss), len(ss))
    rp = os.path.join(ROOT, "RESULTS.md")
    res = open(rp, encoding="utf-8").read()
    row = re.compile(r"^(\|\s*`S-`[^|]*\|\s*)(\d+)(\s*\|)", re.M)
    assert row.findall(res)[0][1] == "19"
    with open(lp, "a", encoding="utf-8") as fh:
        fh.write(("\n" if not txt.endswith("\n") else "") + "\n" + ENTRY)
    open(rp, "w", encoding="utf-8").write(row.sub(lambda m: m.group(1) + "20" + m.group(3), res, count=1))
    print("appended S-20; RESULTS.md S- count 19 -> 20")


if __name__ == "__main__":
    main()
