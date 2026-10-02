"""Round 2, T5 items 1, 2 and 7: write docs/presubmission/round2/COVERAGE.md.

Inputs: coverage_mechanical.json (item 2(a), from t5_coverage.py, run on the template before T5) and the
phrase check of item 2(b) below, returned by one Sonnet 5.5 Explore subagent on the template as it stood
before T5's edits (HEAD d0c6451). Its line numbers at or after the old section 7.1 heading (line 1491)
are shifted by the four lines T5's section 7 pointer inserted, and so are item 2(a)'s. The subagent's text is kept verbatim in
`PHRASE`; the inclusion decisions and omission reasons are T5's own (item 4: a row needs status CONFIRMED and
no partial supersession without a replacement)."""
import json
import re

OLD_71, SHIFT = 1491, 4
PHRASE = """D-03 | covered | 262-263, 1491-1492 | "termination column identically zero" stated; the "never falls" and untrainable-termination-head consequence is not.
D-04 | covered | 265-273 | Resets at rows 999, 1,999 … 9,999; 999 + 9×1,000 + 1 orphan row.
D-07 | absent | - | No action-scale, 4-step lead, median gain 0.35 or 2.9× width statement anywhere.
D-10 | partly covered | 592, 1652-1654 | "Velocity commands from a single bounded box"; no 21 regimes, no two-commands-per-episode count.
D-12 | covered | 1136-1137 | Difficulty span and "uncorrelated with commanded speed" stated; paper's 0.562–1.591 differs from ledger's 0.601–1.674.
D-13 | covered | 1494-1499, 1507-1508 | Row t holds the producing action; reset-row zero-action refutation; implied scale 0.461 omitted.
B-01 | covered | 275-279, 1491-1492 | All 9,961 windows valid, 352 splice episodes; no `train.py:134` cite.
B-02 | absent | - | No falsy-index or reset-at-timestep-0 bug anywhere.
B-03 | absent | - | No `random_split` over windows, no 39-of-40 row overlap leakage.
B-04 | covered | 285-289, 1520-1521 | Eval trajectories drawn from training data; no held-out measurement; "5 of 10 crossed" omitted.
B-05 | covered | 1494-1518 | Training index-for-index, evaluation uses action from t−1, stale by one step.
C-01 | covered | 282-283, 892-901, 1615 | Paper describes two loss terms, implementation has 7; weights in the §6.3 term table.
C-02 | partly covered | 1844 | Only Appendix A "zero-delta model is the hold-last floor"; residual mean head never stated.
C-03 | partly covered | 1009-1010 | "The two shared trunks" used in a parameter share; separate GRUs and Table S7 single base not stated.
C-04 | covered | 999-1013 | One `state_base`, only heads replicated, one hidden state; spread is head disagreement.
C-05 | partly covered | 872, 1013 | Sampled loss (872) and ensemble mean fed back (1013) both appear; the asymmetry is never stated.
C-06 | covered | 143-166, 876-883, 910-912 | Double-softplus clamp, floor plus exp(log_delta), `mlp.py:91-93`, PETS origin.
C-07 | absent | - | No statement that actions are raw and unnormalised.
C-09 | absent | - | No forecast-decay statement; BUILD_CHECKS line 62 only names the retracted decay premise (not coverage).
C-10 | partly covered | 872-883, 1050-1066 | Collapse and near-constant σ (CoV) stated; −14.463, 5.23e-07, σ≈5.6e-05 and 0.0026 absent.
C-11 | covered | 878-883, 889-901 | `min_logstd` cancels algebraically, no gradient, one-way ratchet; no 25-of-106 count.
C-12 | partly covered | 1555-1565, 2004-2005 | Variance state out of reach of a constant-rate run; ~155,000 absent (supplementary doc only).
C-13 | partly covered | 1559 | "Every iteration count the release, the paper and the checkpoint tag state"; 500/2,500/5,000 and typo absent.
C-14 | covered | 742-770 | Aleatoric discarded at `envs/base.py:142`, epistemic applied at :166; author confirmation quoted.
C-15 | covered | 756-762 | Eq. 4 variance versus code standard deviation; author says Eq. 4 is high-level, code intended.
M-02 | covered | 1844 | Appendix A row: zero-delta model is the hold-last floor, 1.192e-07 (rendered).
M-04 | partly covered | 297-307, 1602-1608 | Independent-count caveat only; protocol A/B 0.709 vs 1.026 over 20 seeds, 1.7σ absent.
M-13 | absent | - | No auxiliary-branch teacher-forcing statement; line 282 only names the auxiliary heads.
M-17 | absent | - | No nRMSE tail-statistic or small-n bias; BUILD_CHECKS line 62 only names the n=10 framing (not coverage).
M-19 | partly covered | 338-341, 2014-2036 | Mean-of-ratios leverage, form 1 adopted; 0.0292–1.3873 span, g_z 52.3 and Jensen caveat absent.
M-20 | partly covered | 297-307, 1643-1646 | Only four non-overlapping 400-step trajectories stated; episode-composition effect (beats floor on 4 of 10) absent.
R-02 | absent | - | No protocol A/B (0.7672/1.2728; 0.709/1.026); only in-sample/out-of-sample arena framing.
R-03 | partly covered | 498-507, 565-575 | Hold-last floor used throughout (0.9930 held-out); 1.0070 and median r 0.9649 absent.
R-04 | partly covered | 565-575 | Released vs floor at h=1,8,100,368 on another arena; h=1 loss and h=16 optimum absent.
R-05 | absent | - | No comparison of boundary-crossing versus non-crossing trajectory error.
R-06 | partly covered | 1494-1518 | Swap re-measured on independent trajectories (7.9% at h=368, sign reverses); 0.066 absent.
R-07 | absent | - | No noise sweep reported; "noise" hits are synthetic known-noise data only.
R-08 | partly covered | 836, 872-883 | Total equals epistemic because aleatoric is tiny; 0.003 vs 0.276, hundredfold absent.
R-09 | partly covered | 24-25, 1512-1518 | Stale action raises h=1 error 34.2%; "model beats floor at every horizon", 0.827 absent.
R-15 | partly covered | 1494-1518 | Offset-0 versus offset-1 re-measured; Step-3 table (0.7672→0.7008, 1.2728→1.2046) absent.
R-17 | partly covered | 961, 1846 | Collapse predicted then observed; incomplete memorisation (91.6%) absent, row shows R-18's 1,506×.
R-22 | covered | 9-13, 432-452, 502-505 | AR beats TF under rule M-23 (4.61×, 10,000 iters); ledger's 4.3×/2,500-iteration figures absent.
R-23 | partly covered | 502-505 | "Arm reaching a lower training loss predicts worse"; 3× loss, 5× smaller gradients absent.
R-24 | partly covered | 967-973, 979-983 | Rate linear and near-identical (−9.3857e-05, 17 runs); 153,270 iterations and 31× lr absent.
R-25 | absent | - | No `min_logstd` drift (−9.8128, 5.2× slower, ~2.7e5); supplementary doc only.
R-26 | covered | 658-662 | All 48 runs incl. both arms still lowering training loss at 2,500; per-arm slopes absent.
R-28 | absent | - | No n=100 re-evaluation; paper reports M-16 "cannot be settled" at n_independent=4 (534-536).
R-29 | partly covered | 338-341, 2014-2036 | Generic form-2 inversion of a published comparison; 7-of-45 dimensions, g_z 52.3 vs 0.4386 absent.
R-30 | absent | - | No heavy-tail, two-region, 92.6% or effective-sample-2 finding.
R-31 | partly covered | 541 | "nRMSE aggregation is reported separately and does not change the direction"; four-variant n=100 table absent.
R-32 | partly covered | 2014-2036 | Mechanism only; form-2 sum 88.16, g_z 60%, `state_data_std` 0.04 (34.3×) absent.
R-33 | absent | - | No Jensen-mechanism test at 40 seeds; "Jensen" appears nowhere in the paper.
R-34 | partly covered | 565-575 | Released vs floor on held-out pair only; all-ten n=20 bootstrap, bimodality, 10 of 20 lose absent.
R-45 | partly covered | 1658 | Limits names the "per-dimension matched comparison" (seed 1); 18/45 vs 1/45 result stated nowhere.
R-46 | partly covered | 438, 528, 1658 | Persistence at 10,000 iterations; Limits names a "trend fit" whose result is absent.
R-47 | covered | 1523-1551 | 195 splices, 7,882 windows, 2.47% vs 3.53%, 0 of 32 hurt, 9 help, plus duplication control.
R-39 | partly covered | 451, 519-522 | 10-of-10 episode sign test; one trajectory carries the gap; episode-1 outlier (+6.97 vs +0.73) absent."""

# Appendix H rows T5 added, by entry
APP_H = {"C-09", "M-13", "C-05", "C-07", "D-07", "C-13", "B-02", "B-03", "D-10", "R-25", "R-30", "R-39", "R-45", "R-29", "R-46"}
# absent entries left out (item 7), with the reason
OMIT = {
    "R-02": "superseded as headline by R-15 (offset-0 figures under the released evaluation); §7.2 restates the alignment question on independent trajectories",
    "R-05": "ten overlapping trajectories under the released protocol, which M-04 and §3 show cannot support a comparison; R-47 measures the splice question properly and §7.4 reports it",
    "R-07": "a noise sweep at ten overlapping trajectories under the released protocol, attributed to sampling variance (M-04) and confounded by C-07/D-07; the paper perturbs nothing",
    "R-28": "re-evaluates on overlapping trajectories, a count the paper no longer treats as a sample size (§3, M-20); its 'SETTLED' is for n = 100 overlapping windows, not the n_independent = 4 §5 reports",
    "M-17": "narrowed by R-30 (the tail is two regions) and replaced in mechanism by M-19, which Appendix G states; relative-L1 governing every rule is its practical consequence",
    "R-33": "status SUPPORTED, not CONFIRMED (item 4); its criterion was changed after M-19",
}
# partly covered entries not given an Appendix H row: why the body's statement suffices
PARTLY = {
    "C-02": "the residual mean head is what makes the zero-delta model the floor (Appendix A); an architectural detail no result turns on",
    "C-03": "§6.4 states the shared trunks; that there are two GRUs is a structural detail of the same finding",
    "C-10": "§6.3 states the collapse and its mechanism; the raw parameter values add nothing to the argument",
    "C-12": "§7.5 states the conclusion; the implied count is in the supplementary variance appendix",
    "M-04": "revised by R-28 and replaced by the independent-trajectory treatment of §3 (M-20, M-27)",
    "M-19": "Appendix G states the aggregation finding; its Jensen mechanism is not CONFIRMED",
    "M-20": "§3 states the effective sample size, which is the finding",
    "R-03": "the hold-last floor is used throughout; the missing figures are overlapping-trajectory ones",
    "R-04": "§5's head-to-head table gives the released checkpoint against the floor by horizon on independent trajectories",
    "R-06": "§7.2 re-measures the alignment cost on independent trajectories (S-20, R-76)",
    "R-08": "§6.2 states that total uncertainty is the epistemic value",
    "R-09": "§7.2 and the head-to-head table restate it on independent trajectories",
    "R-15": "superseded in part by S-09; §7.2 carries the replacement",
    "R-17": "Appendix A reports the overfit test with R-18's figure, which resolved R-17's open part",
    "R-23": "§5 states that the arm with the lower training loss predicts worse",
    "R-24": "§6.3 states the rate and its consistency across runs; the implied count is in the supplementary",
    "R-31": "§5 states that the nRMSE aggregation does not change the direction",
    "R-32": "Appendix G states the mechanism; the arithmetic stays in the ledger",
    "R-34": "§5 and §6 use the all-ten arena; the bimodality is not used by any claim",
}


def shift(lines):
    if lines.strip() in ("-", ""):
        return "-"
    out = []
    for part in lines.split(","):
        a = [int(x) for x in re.findall(r"\d+", part)]
        a = [x + SHIFT if x >= OLD_71 else x for x in a]
        out.append("-".join(str(x) for x in a))
    return ", ".join(out)


ph = {}
for ln in PHRASE.split("\n"):
    i, c, l, w = [x.strip() for x in ln.split("|")]
    ph[i] = (c, shift(l), w)
mech = json.load(open("docs/presubmission/round2/coverage_mechanical.json"))
tpl = open("PAPER.template.md").read().split("\n")
h0 = next(i for i, x in enumerate(tpl, 1) if x.startswith("## Appendix H"))
hline = {}
for i, x in enumerate(tpl[h0:], h0 + 1):
    for eid in re.findall(r"(?<![\w-])([DBCMR]-\d+)(?![\w])", x.split("|")[2] if x.count("|") > 3 else ""):
        hline.setdefault(eid, i)
assert set(hline) == APP_H, (set(hline) ^ APP_H)
absent = {i for i, v in ph.items() if v[0] == "absent"}
assert absent - APP_H == set(OMIT), (absent - APP_H) ^ set(OMIT)
partly = {i for i, v in ph.items() if v[0] == "partly covered"}
assert partly - APP_H == set(PARTLY), (partly - APP_H) ^ set(PARTLY)

rows, tally = [], {}
for r in mech:
    eid = r["id"]
    if eid in ph:
        c, lines, what = ph[eid]
        how = "(b) phrase"
    elif r["mechanical_covered"]:
        c = "covered"
        lines = shift(", ".join(str(x) for x in r["mechanical_lines"])) if r["mechanical_lines"] else "caption"
        what = "artifact-sourced keys: " + ", ".join(r["mechanical_keys"][:4])
        how = "(a) artifact"
    else:
        raise SystemExit(f"{eid}: neither mechanical nor phrase-checked")
    if eid in APP_H:
        after = f"covered: Appendix H, line {hline[eid]}" + (" (folded into R-45's row)" if eid == "R-29" else "")
    elif eid in OMIT:
        after = "left out: " + OMIT[eid]
    elif eid in PARTLY:
        after = "unchanged: " + PARTLY[eid]
    elif eid == "R-26":
        after = "covered by T4's §5.2 Limits sentence (item 6: not duplicated)"
    else:
        after = "unchanged"
    tally[c] = tally.get(c, 0) + 1
    rows.append(f"| `{eid}` | {r['claim'].replace('|', '/')} | {r['status'].replace('|', '/')[:40]} | {c} | {how} | {lines} | {what.replace('|', '/')} | {after.replace('|', '/')} |")

out = [
    "# Round 2, T5 — coverage of the contribution-tagged ledger entries",
    "",
    f"One row per entry tagged CONTRIB in `results/claims_to_evidence.json`: {len(rows)} (the plan's 102, plus R-76, R-77 and R-78 from T1).",
    "Generated by `round2/t5_coverage.py` (item 2(a)) and `round2/t5_coverage_md.py`; do not edit by hand.",
    "",
    "**How each entry was classified (PLAN T5 item 2).**",
    "- **(a) Mechanically.** An entry is covered if an artifact it names, in `claims_to_evidence.json` or on its ledger **Evidence** line, is the `source` of a `results/paper_numbers.json` key that `PAPER.template.md` or a `build_paper.py` caption uses.",
    "- **(b) By phrase.** Every other entry, and R-39 (one of the plan's candidates), was phrase-checked against the template by one Sonnet 5.5 Explore subagent. It read each ledger entry and grepped the template and `PAPER.md` for its distinguishing phrase and number.",
    "- **Line numbers** are of `PAPER.template.md` after T5.",
    "",
    f"**Before T5:** {tally.get('covered', 0)} covered, {tally.get('partly covered', 0)} partly covered, {tally.get('absent', 0)} absent.",
    f"**T5 added** Appendix H rows for {len(APP_H)} entries ({len(APP_H & absent)} absent, {len(APP_H & partly)} partly covered).",
    f"**Left out (item 7):** {len(OMIT)} absent entries, each with its reason below.",
    "",
    "| ID | title | ledger status | before T5 | method | template lines | what matched or is missing | after T5 |",
    "|---|---|---|---|---|---|---|---|",
] + rows + [
    "",
    "## Absent entries left out (item 7)",
    "",
] + [f"- **{k}** — {v}." for k, v in OMIT.items()] + [
    "",
    "## Noted, not fixed (OUT_OF_SCOPE.md)",
    "",
    "- **D-12.** The paper's difficulty span (`results/a2_trajectory_level_control.json`) differs from the ledger entry's (`step3_report.txt`). These are two artifacts under two protocols. This is for T10's read.",
    "- **R-28.** The ledger says SETTLED at 100 overlapping windows, while §5 says CANNOT BE SETTLED at n_independent = 4. These are different units, not a contradiction; the paper's is the governing one.",
]
open("docs/presubmission/round2/COVERAGE.md", "w").write("\n".join(out) + "\n")
print(f"wrote COVERAGE.md: {len(rows)} rows; before T5 {tally}; Appendix H {len(APP_H)}; omitted {len(OMIT)}")
