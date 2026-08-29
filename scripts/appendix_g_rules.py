"""
D3 -- Appendix G: every pre-registered rule, its lead time and its verdict.

WHY. Ledger identifiers -- M-16, M-23, M-43, M-44, M-45, S-12 and the rest --
appear through the body with no table behind them. A reader who wants to know what
M-43 said has nowhere to look, so the identifier is either decoration or an
instruction to open a 330 KB ledger. The fix is one table, and then the identifier
can stay ONLY where a pre-registered verdict is being reported and come out
everywhere else.

GENERATED FROM THE LEDGER, not written here. Each row's rule text is the ledger's
own; its commit is resolved by subject (hashes do not survive a history rewrite and
subjects do -- Figure 4 learned that from M-48); its lead time comes from the same
computation Figure 4 plots; and its verdict is the ledger's Status line.

A rule with a negative lead time is included and drawn as such. Dropping the Task 3
rule because S-12 withdrew its pre-registration would be making the claim the
ledger withdraws.

Writes results/appendix_g_rules.json.
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402

LEDGER = "FINDINGS_LEDGER.md"
OUT = "appendix_g_rules.json"


def entry(txt, eid):
    i = txt.find(f"### {eid} ")
    if i < 0:
        return None
    b = txt[i:]
    j = b.find("\n### ", 5)
    return b[:j] if j > 0 else b


def one_line(s, n=300):
    return re.sub(r"\s+", " ", s).strip()[:n]


def main():
    txt = open(LEDGER).read()
    FIG = json.load(open(os.path.join(R.RESULTS, "paper_figures.json")))
    NUM = json.load(open(os.path.join(R.RESULTS, "paper_numbers.json")))
    # The verdict a DISCHARGED rule actually returned. The ledger's Status line for
    # these says "PRE-REGISTERED, DISCHARGED", which records that the rule ran and
    # not what it said, and a table of verdicts that printed "DISCHARGED" in the
    # verdict column would be answering a different question from the one it asks.
    RETURNED = {"M-43": "e5_verdict", "M-44": "m44_verdict", "M-45": "m45_verdict"}
    lead = FIG["fig4"]
    commits = {c["rule"]: c for c in FIG["fig4_commits"]}

    # Every ledger entry whose TITLE announces a pre-registered rule, in ledger
    # order. The title and not the status: M-22 and M-23 are settled and their
    # status lines say so rather than repeating "PRE-REGISTERED", and selecting on
    # the status quietly dropped both -- the two oldest rules in the paper.
    #
    # Excluded explicitly: an entry whose title says NOT PRE-REGISTERED. R-38 is
    # a measurement that says of itself that it is not a verdict, and a table of
    # pre-registered rules that listed it would be making R-38's own point wrong.
    ids = []
    for m in re.finditer(r"^### ([A-Z]-\d+) — (.+)$", txt, re.M):
        eid, title = m.group(1), m.group(2)
        if "NOT PRE-REGISTERED" in title.upper():
            continue
        if re.search(r"PRE-REGISTERED|Pre-registered", title):
            ids.append(eid)
    # ...plus the rule S-12 withdraws, which no longer announces itself as
    # pre-registered BECAUSE it was withdrawn. A table that dropped it would be
    # making the claim the ledger retracts.
    for extra in ("S-12",):
        if extra not in ids and entry(txt, extra):
            ids.append(extra)

    rows = []
    for eid in ids:
        blk = entry(txt, eid)
        title = blk.split("\n")[0]
        title = title.split("—", 1)[1].split("·")[0].strip() if "—" in title else title
        # "PRE-REGISTERED decision rule for X" -> "X". The column is headed
        # "what it governs" in a table of pre-registered rules; repeating the
        # category in every cell is noise.
        title = re.sub(r"^(?:PRE-REGISTERED|Pre-registered)[:,]?\s*"
                       r"(?:decision\s+)?rule\s+(?:for\s+)?", "", title)
        title = title[0].upper() + title[1:] if title else title
        st = re.search(r"^\*\*Status\*\*\s*(.+)$", blk, re.M)
        status = st.group(1).split("·")[0].strip() if st else "—"
        # The verdict the rule returned. The ledger states it in three shapes --
        # a Status line that carries it ("RESOLVED — reproduces at long horizon"),
        # a bolded ALL-CAPS verdict in the body, or "It returns X" -- so all three
        # are tried in order of how specific they are. A blank here would read as
        # "no verdict", which is a different and stronger claim than "not recorded
        # in a shape this parser knows".
        verdict = None
        m_st = re.search(r"^\*\*Status\*\*\s*([A-Z][A-Za-z ,]*?)\s*—\s*([^·\n]+)",
                         blk, re.M)
        if m_st:
            # cut at the first clause: the Status line often continues into the
            # commits that establish the verdict, which the `commit` column
            # already carries and which reads as a truncated sentence here
            tail = re.split(r"\s+(?:—|--|;|,)\s+|\s+in `", m_st.group(2).strip())[0]
            verdict = f"{m_st.group(1).strip()} — {tail.strip().rstrip(',')}"
        if not verdict:
            vm = re.search(r"\*\*It returns\s+\*{0,2}([A-Za-z][A-Za-z \-]{3,50}?)\*{0,2}\*\*",
                           blk)
            if vm:
                verdict = vm.group(1).strip()
        if not verdict:
            vm = re.search(r"\*\*([A-Z][A-Z ]{4,45}?)\*\*", blk)
            verdict = vm.group(1).strip() if vm else status
        # the rule's own statement: the first paragraph after a "Rule"/"conditions" cue
        rm = re.search(r"^\*\*(?:The rule|Rule|Decision rule|The decision rule)[^*]*\*\*\s*(.+?)(?=\n\n)",
                       blk, re.M | re.S)
        if not rm:
            rm = re.search(r"(?:conditions, all required|Verdict, decided in advance)"
                           r"[^\n]*\n+(.+?)(?=\n\n)", blk, re.S)
        rule_text = one_line(rm.group(1)) if rm else one_line(
            "\n".join(blk.split("\n")[1:6]))
        if eid in RETURNED and RETURNED[eid] in NUM:
            verdict = str(NUM[RETURNED[eid]]["value"])
        if "NOT YET DISCHARGED" in status.upper():
            verdict = "not yet discharged"
        key = next((k for k in lead if k.startswith(eid + " ")), None)
        if key is None and eid == "S-12":
            # S-12 withdraws the Task 3 rule, which Figure 4 labels by its subject
            # rather than by an identifier -- because at the time it was written it
            # had none.
            key = next((k for k in lead if k.startswith("Task 3")), None)
        rows.append({
            "id": eid, "title": title, "status": status, "verdict": verdict,
            "rule_text": rule_text,
            "lead_hours": lead[key]["lead_hours"] if key else None,
            "tested_by": lead[key]["tested_by"] if key else None,
            "rule_commit": commits.get(key, {}).get("rule_commit"),
            "commit_subject": None,
        })

    # the commit subject for each, resolved from the hash the figure printed
    for r in rows:
        if r["rule_commit"]:
            o = subprocess.run(["git", "show", "-s", "--format=%s", r["rule_commit"]],
                               capture_output=True, text=True)
            r["commit_subject"] = o.stdout.strip() or None

    # Rules with no figure-4 row: their lead time is not computed anywhere, and
    # saying so is better than leaving a blank a reader reads as zero.
    n_lead = sum(1 for r in rows if r["lead_hours"] is not None)

    print("APPENDIX G — PRE-REGISTERED RULES")
    print("=" * 100)
    for r in rows:
        lh = f"{r['lead_hours']:+.2f} h" if r["lead_hours"] is not None else "not computed"
        print(f"  {r['id']:<6} {lh:>14}  {r['verdict'][:28]:<28} {r['title'][:44]}")
    print("=" * 100)
    print(f"  {len(rows)} rules, {n_lead} with a computed lead time")

    json.dump({"n_rules": len(rows), "n_with_lead_time": n_lead, "rules": rows},
              open(os.path.join(R.RESULTS, OUT), "w"), indent=2)
    print(f"  wrote results/{OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
