"""Round 4, F11 step 5: refresh docs/COVER_STATEMENT.md (round 3's r8_cover.py, extended).

1. The rule count, the page count and the retraction counts, as r8_cover.py does.
2. Round 4's rules X3, X4 and X6-X8, rule X5 (not run, never pre-registered: D-38) and analyses N5-N6
   (REVIEW.md item 7). One bullet under the first acceptance
   question and two rows of the Reproducibility Certification table. Each sentence follows the paper's own
   wording for the same result (contributions 1-3 and 6, section 7.2's X8 sentence, section 11's X5 reason),
   keeps the scope the locked framing requires (X4 is size only; X5 is not run; X6 is the short-unit
   h = 100 result; X7 is pooled coverage on a checkpoint that trained on every episode; X8 covers its four
   rules), and so claims nothing the paper does not.

Every figure is read from results/paper_numbers.json; none is typed. Each pattern must match exactly once
(whitespace-tolerant), and nothing is written until all have. A second run is a no-op. Run from the
repository root after the final build; section 8's figures are refreshed separately by
docs/presubmission/s10fix_docs.py.
"""
import json
import re
import sys

F = sys.argv[1] if len(sys.argv) > 1 else "docs/COVER_STATEMENT.md"   # a path argument is for a dry run
N = json.load(open("results/paper_numbers.json"))


def v(k):
    assert k in N, f"no key {k} in results/paper_numbers.json"
    return N[k]["value"] if isinstance(N[k], dict) else N[k]


def sub(text):
    """Substitute every {{key}} from paper_numbers.json; refuse an unknown key."""
    return re.sub(r"\{\{(\w+)\}\}", lambda m: str(v(m.group(1))), text)


CAP = {13: "Thirteen", 14: "Fourteen", 15: "Fifteen", 16: "Sixteen", 17: "Seventeen"}
NUM = {"six": 6, "seven": 7, "eight": 8, "nine": 9}

n_rules, n_pos = int(v("appG_n_lead")), int(v("appG_n_positive"))
assert n_rules - n_pos == 1, (n_rules, n_pos)          # the sentence names exactly one negative lead
n_claims = NUM[str(v("n_retractions_word")).lower()]
n_fram = NUM[str(v("n_retract_framing_word")).lower()]

COUNTS = [
    ("page count",
     r"current at \d+ pages, the",
     f"current at {v('pdf_pages')} pages, the"),
    ("rule counts",
     r"\*\*\d+ pre-registered decision rules, with git lead times\.\*\* All but one name their conditions and "
     r"thresholds before their data existed, and Appendix E gives all \d+ with the lead time computed from git\. "
     r"\d+ have a positive lead",
     f"**{n_rules} pre-registered decision rules, with git lead times.** All but one name their conditions and "
     f"thresholds before their data existed, and Appendix E gives all {n_rules} with the lead time computed from "
     f"git. {n_pos} have a positive lead"),
    ("retraction counts",
     r"\*\*[A-Z][a-z]+ withdrawals kept in the record\*\* — [a-z]+ claims withdrawn on evidence and [a-z]+ "
     r"framings withdrawn —",
     f"**{CAP[n_claims + n_fram]} withdrawals kept in the record** — {str(v('n_retractions_word')).lower()} "
     f"claims withdrawn on evidence and {str(v('n_retract_framing_word')).lower()} framings withdrawn —"),
]

# the five are among Appendix E's rules (M-86 to M-90), so the lead counts them within the rule total
_X = [r["id"] for r in json.load(open("results/appendix_g_rules.json"))["rules"]]
assert all(i in _X for i in ("M-86", "M-87", "M-88", "M-89", "M-90")), "X3, X4, X6-X8 are not all in Appendix E"
BULLET_LEAD = f"- **Five of the {n_rules} rules test the paper's own weak points, and a sixth could not be run.**"
BULLET = BULLET_LEAD + sub(
    " Retrained on fixed folds with each of the ten episodes held out once, the base claim's direction"
    " replicates, {{x3_gap}} {{x3_ci}} at h = {{v2_diag_h}} over {{x3_n}} trajectories at {{iters_main}}"
    " iterations, not {{iters_long}} (rule X3: `{{x3_reading}}`). Matched to RWM's parameter count, the MLP"
    " baseline stays behind and the transformer cannot be told apart (rule X4: `{{x4_reading}}`; size is the"
    " one axis matched). On {{x6_n_units}} shorter units at h = {{v2_deploy_h}}, ensemble disagreement ranks"
    " error ahead of the model's own predicted step size, {{x6_margin}} {{x6_ci}} (rule X6:"
    " `{{x6_reading}}`); over the {{e7_nind}} whole trajectories the margin at h = {{v2_diag_h}} is not"
    " resolved, and X6 does not re-test it. Fitted on nine episodes and scored on the tenth, the"
    " disagreement's pooled coverage over all {{x7_n_traj}} trajectories is within the band at every horizon"
    " (rule X7: `{{x7_summary}}`), on episodes the checkpoint trained on, so they are unseen only by the"
    " multiplier. Re-scored with the released evaluation's timing, four of our rules keep their verdicts,"
    " though {{x8_n_changed}} of their alongside readings change (rule X8: `{{x8_reading}}`, a statement about"
    " those four rules only). The sixth, rule X5, a test of the penalty that needs no policy, was never"
    " pre-registered: its feasibility check found that the released data do not record the velocity command"
    " its reward terms score against, so it is reported as not run (ledger `D-38`). Two analyses made"
    " afterwards, section 7.2's figures for our own models and the difficulty"
    " control at the causal action timing, are labelled post hoc.\n")
# placed after the bullet on results that run against the paper's own arms, before the withdrawals
BULLET_ANCHOR = r"\n- \*\*[A-Z][a-z]+ withdrawals kept in the record\*\*"

ROWS_LEAD = "| a cross-fold re-test |"
ROWS = sub(
    "| a cross-fold re-test | the base claim retrained with each of the ten episodes held out once: rule X3"
    " returns `{{x3_reading}}` at {{iters_main}} iterations, over {{x3_n}} trajectories |\n"
    "| size-matched baselines | MLP and transformer baselines matched to RWM's parameter count: rule X4 returns"
    " `{{x4_reading}}`, the MLP behind and the transformer not told apart |\n")
# placed after the capacity-matched row
ROWS_ANCHOR = r"\| a capacity-matched re-test \|[^\n]*\n"


def ws(rx):
    return re.compile(r"\s+".join(rx.split(" ")))


def main():
    s = open(F, encoding="utf-8").read()
    plan = []
    for name, rx, new in COUNTS:
        hits = ws(rx).findall(s)
        if len(hits) != 1:
            sys.exit(f"STOP: '{name}' matched {len(hits)} times")
        plan.append((name, ws(rx), new))
    for name, pat, new in plan:
        s = pat.sub(lambda _: new, s, count=1)
        print(f"  applied: {name}")

    # round 4's additions: insert once; on a later run, replace in place so the figures stay current
    if BULLET_LEAD in s:
        i = s.index(BULLET_LEAD)
        j = s.index("\n- **", i + len(BULLET_LEAD))
        s = s[:i] + BULLET.rstrip("\n") + "\n" + s[j:]
        print("  replaced: round-4 bullet")
    else:
        m = list(re.finditer(BULLET_ANCHOR, s))
        if len(m) != 1:
            sys.exit(f"STOP: bullet anchor matched {len(m)} times")
        s = s[:m[0].start()] + "\n" + BULLET.rstrip("\n") + "\n" + s[m[0].start():]
        print("  inserted: round-4 bullet")
    if ROWS_LEAD in s:
        i = s.index(ROWS_LEAD)
        j = s.index("\n", s.index("\n", i) + 1) + 1        # the two rows
        s = s[:i] + ROWS + s[j:]
        print("  replaced: round-4 table rows")
    else:
        m = list(re.finditer(ROWS_ANCHOR, s))
        if len(m) != 1:
            sys.exit(f"STOP: table anchor matched {len(m)} times")
        s = s[:m[0].end()] + ROWS + s[m[0].end():]
        print("  inserted: round-4 table rows")
    open(F, "w", encoding="utf-8").write(s)


if __name__ == "__main__":
    main()
