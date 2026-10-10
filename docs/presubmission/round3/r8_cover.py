"""Round 3, R8 step 5: refresh docs/COVER_STATEMENT.md's rule count, page count and retraction counts
(section 8's figures are refreshed by docs/presubmission/s10fix_docs.py in the restatement).

Every figure is read from results/paper_numbers.json; none is typed. Each pattern must match exactly once
(whitespace-tolerant), and nothing is written until all have. Run from the repository root after the final
build.
"""
import json
import re
import sys

F = "docs/COVER_STATEMENT.md"
N = json.load(open("results/paper_numbers.json"))
v = lambda k: N[k]["value"] if isinstance(N[k], dict) else N[k]  # noqa: E731
CAP = {13: "Thirteen", 14: "Fourteen", 15: "Fifteen"}
NUM = {"six": 6, "seven": 7, "eight": 8, "nine": 9}

n_rules, n_pos = int(v("appG_n_lead")), int(v("appG_n_positive"))
assert n_rules - n_pos == 1, (n_rules, n_pos)          # the sentence names exactly one negative lead
n_claims = NUM[str(v("n_retractions_word")).lower()]
n_fram = NUM[str(v("n_retract_framing_word")).lower()]

EDITS = [
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


def main():
    s = open(F).read()
    plan = []
    for name, rx, new in EDITS:
        pat = re.compile(r"\s+".join(rx.split(" ")))
        hits = pat.findall(s)
        if len(hits) != 1:
            sys.exit(f"STOP: '{name}' matched {len(hits)} times")
        plan.append((name, pat, new))
    for name, pat, new in plan:
        s = pat.sub(lambda _: new, s, count=1)
        print(f"  applied: {name}")
    open(F, "w").write(s)


if __name__ == "__main__":
    main()
