"""S8 step 3 -- discharge M-74, M-75 and M-76 as new ledger entries M-77, M-78 and M-79.

By the user's ruling (DECISIONS_FOR_USER.md#S8-discharge-status): the verdicts go into new
entries, and in each rule only the `Status` line changes, to say it is discharged and what it
returned. Not one character of any rule's text changes; the script asserts that the only lines
it alters in FINDINGS_LEDGER.md are those three Status lines.

Every figure is read from results/mn_sweep_verdict.json, results/baselines_verdict.json and
results/presubmission_runtime.json. Nothing is interpreted: each entry states what the verdict
script returned, with the rule's own "reported alongside, never governing" readings labelled
as such.

    python docs/presubmission/s8_write_discharges.py
"""
import json
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
J = lambda n: json.load(open(os.path.join(ROOT, "results", n)))
MV, BV, RT = J("mn_sweep_verdict.json"), J("baselines_verdict.json"), J("presubmission_runtime.json")
f3 = lambda x: f"{x:+.4f}"
ci = lambda c: f"[{c[0]:+.4f}, {c[1]:+.4f}]"
lab = lambda k: ("relative-L1" if k.split("_h")[0] == "l1" else "nRMSE") + " at h = " + k.split("_h")[1]
pv = lambda p: f"{p:.5f}"


def alongside(block):
    """'l1_h100: X; …' over the rule's reported-alongside readings, verbatim branch names."""
    out = []
    for k, v in block.items():
        b = v.get("branch") or v.get("verdict") if isinstance(v, dict) else None
        if b:
            met, h = k.split("_h")
            out.append(f"{'relative-L1' if met == 'l1' else 'nRMSE'} at h = {h} **{b}**")
    return "; ".join(out)


def m77():
    g = MV["governing"]
    rows = []
    for c in MV["priority_order"]:
        r = g["per_config"][c]
        res = ("REJECTED toward the configuration" if r["rejected"] and r["direction"] == "config"
               else "REJECTED toward the centre" if r["rejected"] else "not rejected")
        rt = RT["by_family"].get(f"M-74 {c}", {})
        sign = MV["per_episode_sign"][c]
        rows.append(f"| ({c[1:].split('_N')[0]}, {c.split('_N')[1]}) | {f3(r['D'])} | {ci(r['ci95'])} | "
                    f"{pv(r['p'])} | {r['rank']} / {r['level']:.5f} | {res} | "
                    f"{sign['positive']} / {sign['negative']} | {rt.get('mean_s', 0)/3600:.2f} |")
    conds = g["conditions"]
    return f"""### M-77 — `M-74` discharged: the centre (M, N) = (32, 8) returns NOT OPTIMAL AT OUR BUDGET · **NEW**
**Discharges** `M-74`. `scripts/verdict_mn_sweep.py`, exactly as committed before the first sweep run, on
`results/mn_sweep_eval.json` (`scripts/mn_sweep_eval.py`), returns **{MV['verdict']}**.

**The governing statistic, as the rule fixes it:** D_c = mean over the 4 held-out trajectories of [3-seed mean
error of configuration c − 3-seed mean error of the centre], {MV['governing_metric']} at h = {MV['governing_horizon']};
positive favours the centre. Exact cluster bootstrap over all 256 resamples; Holm step-down at family-wise
α = {MV['alpha']} over m = {g['m']} configurations, ties in the rule's priority order.

| (M, N) | D_c | 95% interval | p | Holm rank / level | result | episodes favouring the centre / the configuration (reported alongside) | mean h per run |
|---|---|---|---|---|---|---|---|
{chr(10).join(rows)}

Configurations excluding zero in their own favour: {', '.join(conds['configs_excluding_zero_in_their_favour'])}.
In the centre's favour: {', '.join(conds['configs_excluding_zero_in_centre_favour'])}. The centre has the lowest
error: {conds['centre_has_lowest_error']}. The centre's three seeds are the existing Arm A runs at 2,500
iterations, not re-trained, so the centre has no runtime row here.

**Reported alongside, never governing** (the rule's own list): held-out {alongside(MV['alongside'])}. In-sample
(n_independent = 16): {alongside(MV['in_sample'])}. The minimum detectable effect at Holm step 1, as a percentage of
the centre's error: {', '.join(f"{lab(k)} {v:.1f}%" for k, v in MV['mde_pct_of_centre_holm_step_1'].items())}.

**Training time, reported beside the verdict as the rule requires:** {RT['by_rule']['M-74']['n_runs']} runs,
{RT['by_rule']['M-74']['wall_clock_s']/3600:.2f} h of wall clock in all (`results/presubmission_runtime.json`).
{sum(1 for r in RT['runs'] if r['rule'] == 'M-74' and r['overlap_s'])} of them overlapped a CPU job a
session logged, which inflates their `wall_clock_s` and changes no weight; that artifact lists each overlap.
**Evidence** `RUN` `results/mn_sweep_verdict.json`, `results/mn_sweep_eval.json`, `results/presubmission_runtime.json`; the 24 sweep run artifacts (results/mn_sweep_run_M…_N…_seed….json); `SRC` `scripts/verdict_mn_sweep.py`.
**Status** CONFIRMED · **Relevance** CONTRIB
"""


def m7x(rule, nid, title):
    R = BV["rules"][rule]
    g = R["governing"]
    rows = []
    for b in BV["priority_order"]:
        r = g["per_baseline"][b]
        sign = R["per_episode_sign"][b]
        rt = RT["by_family"].get(f"{rule} {b}_{R['regime']}_{R['spec']}", {})
        rows.append(f"| {b} | {f3(r['D'])} | {ci(r['ci95'])} | {pv(r['p'])} | {r['rank']} / {r['level']:.5f} | "
                    f"**{r['result']}** | {sign['positive']} / {sign['negative']} | {rt.get('mean_s', 0)/3600:.2f} |")
    mde = BV["mde_pct_of_rwm_holm_step_1"][rule]
    return f"""### {nid} — `{rule}` discharged: {title} returns {R['verdict']} · **NEW**
**Discharges** `{rule}`. `scripts/verdict_baselines.py`, exactly as committed before any baseline run, on
`results/baselines_eval.json` (`scripts/baselines_eval.py`), returns **{R['verdict']}**.

**The governing statistic, as the rule fixes it:** D_b = mean over the 4 held-out trajectories of [3-seed mean
error of baseline b − 3-seed mean error of RWM (Arm A, (32, 8), 2,500 iterations, seeds 0–2)], relative-L1 at
h = 368; positive favours RWM. Baselines at the original's Table S7 sizes, regime `{R['regime']}`. Exact cluster
bootstrap over all 256 resamples; Holm step-down at α = {BV['alpha']} over m = {g['m']}, ties in the order
{', '.join(BV['priority_order'])}.

| baseline | D_b | 95% interval | p | Holm rank / level | result | episodes favouring RWM / the baseline (reported alongside) | mean h per run |
|---|---|---|---|---|---|---|---|
{chr(10).join(rows)}

**Reported alongside, never governing** (the rule's own list): held-out {alongside(R['alongside'])}. The minimum
detectable effect at Holm step 1, as a percentage of RWM's error: {', '.join(f"{lab(k)} {v:.1f}%" for k, v in mde.items())}.
Training time: {RT['by_rule'][rule]['n_runs']} runs, {RT['by_rule'][rule]['wall_clock_s']/3600:.2f} h
(`results/presubmission_runtime.json`); none overlapped a logged CPU job.
**Evidence** `RUN` `results/baselines_verdict.json`, `results/baselines_eval.json`, `results/presubmission_runtime.json`; the nine run artifacts of this regime (results/baseline_run_…_{R['regime']}_s7_seed….json); `SRC` `scripts/verdict_baselines.py`.
**Status** CONFIRMED · **Relevance** CONTRIB
"""


def main():
    import sys
    if "--dry-run" in sys.argv:
        print(m77()); print(m7x("M-75", "M-78", "the architecture claim, baselines teacher-forced,"))
        print(m7x("M-76", "M-79", "the architecture claim, baselines autoregressive,"))
        return
    lp = os.path.join(ROOT, "FINDINGS_LEDGER.md")
    txt = open(lp, encoding="utf-8").read()
    ms = [int(x) for x in re.findall(r"^### M-(\d+) ", txt, re.M)]
    assert max(ms) == 76 and "### M-77 " not in txt, max(ms)
    assert all(RT["by_rule"][r]["n_runs"] for r in ("M-74", "M-75", "M-76"))
    assert BV["matched_variants"] == {}, "matched variants were not run (S2b ruling); none may appear"

    # the three Status lines, each located inside its own rule's block
    new = txt
    changes = {"M-74": ("results/mn_sweep_verdict.json", MV["verdict"], "M-77"),
               "M-75": ("results/baselines_verdict.json", BV["rules"]["M-75"]["verdict"], "M-78"),
               "M-76": ("results/baselines_verdict.json", BV["rules"]["M-76"]["verdict"], "M-79")}
    for rid, (art, verdict, rec) in changes.items():
        i = new.index(f"### {rid} ")
        j = new.find("\n### ", i + 5)
        blk = new[i:j]
        old = f"**Status** PRE-REGISTERED, NOT YET DISCHARGED — awaits `{art}` · **Relevance** METHOD"
        assert blk.count(old) == 1, rid
        repl = (f"**Status** PRE-REGISTERED, DISCHARGED by `{art}`. **It returns {verdict}.** "
                f"Recorded in `{rec}`. · **Relevance** METHOD")
        new = new[:i] + blk.replace(old, repl) + new[j:]
    changed = [a for a, b in zip(txt.split("\n"), new.split("\n")) if a != b]
    assert len(changed) == 3 and all(c.startswith("**Status** PRE-REGISTERED, NOT YET") for c in changed), changed

    entries = [m77(), m7x("M-75", "M-78", "the architecture claim, baselines teacher-forced,"),
               m7x("M-76", "M-79", "the architecture claim, baselines autoregressive,")]
    new = new.rstrip("\n") + "\n\n" + "\n".join(entries)
    open(lp, "w", encoding="utf-8").write(new)

    rp = os.path.join(ROOT, "RESULTS.md")
    res = open(rp, encoding="utf-8").read()
    row = re.compile(r"^(\|\s*`M-`[^|]*\|\s*)(\d+)(\s*\|)", re.M)
    assert row.findall(res)[0][1] == "76"
    open(rp, "w", encoding="utf-8").write(row.sub(lambda m: m.group(1) + "79" + m.group(3), res, count=1))
    print("M-74/75/76 Status lines set; M-77, M-78, M-79 appended; RESULTS.md M- count 76 -> 79")


if __name__ == "__main__":
    main()
