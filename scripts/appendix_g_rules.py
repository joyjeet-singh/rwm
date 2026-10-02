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
    """One line of a rule's committed text, safe to drop into a Markdown document.

    Two things the naive version got wrong. It truncated mid-word, and it
    truncated INSIDE emphasis markers -- `**The claim reproduces` with no closing
    pair -- which the Markdown-to-LaTeX converter carried through as a literal
    `**` into the .tex. The compile gate caught it as a stray marker, which is
    what that gate is for.

    Emphasis is stripped rather than balanced: this is a quotation of a rule's
    text inside a table row, and the rule's own bolding is noise there.
    """
    t = re.sub(r"\s+", " ", s).strip()
    t = re.sub(r"\*{1,3}([^*]+)\*{1,3}", r"\1", t)      # **bold** / *italic* -> plain
    t = t.replace("*", "")                                # any survivor
    if len(t) <= n:
        return t
    cut = t[:n]
    sp = cut.rfind(" ")
    return (cut[:sp] if sp > n * 0.6 else cut).rstrip(" ,;:") + " …"


def main():
    txt = open(LEDGER).read()
    FIG = json.load(open(os.path.join(R.RESULTS, "paper_figures.json")))
    NUM = json.load(open(os.path.join(R.RESULTS, "paper_numbers.json")))
    # The verdict a DISCHARGED rule actually returned. The ledger's Status line for
    # these says "PRE-REGISTERED, DISCHARGED", which records that the rule ran and
    # not what it said, and a table of verdicts that printed "DISCHARGED" in the
    # verdict column would be answering a different question from the one it asks.
    RETURNED = {"M-43": "e5_verdict", "M-44": "m44_verdict", "M-45": "m45_verdict",
                # M-16's Status line says the rule was pre-registered ("SETTLED"), not
                # what it returned; §5, §8 and the introduction cite the return (S10).
                "M-16": "m16_verdict"}
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
            continue
        # ...and any entry whose STATUS says it is a pre-registration, whatever
        # its title says. M-52's title is "M-51 named a quantity that does not
        # exist, and what replaced it" -- no match on the title rule -- so the one
        # mid-flight amendment to a pre-registration in this whole project was
        # silently absent from a table headed "every pre-registered rule" and
        # described in its own prose as "a census rather than a highlights reel".
        # It is the row a hostile reviewer most wants to see.
        blk_ = entry(txt, eid) or ""
        st_ = re.search(r"^\*\*Status\*\*\s*(.+)$", blk_, re.M)
        if st_ and "PRE-REGISTERED" in st_.group(1).upper() \
                and "NOT PRE-REGISTERED" not in st_.group(1).upper():
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
        # Drop the section reference from the TABLE's description column. Ledger
        # titles carry the numbering current when the entry was written -- M-45
        # reads "the within-trajectory control on §5.6", which is now §6.6 -- and
        # this column is a description this appendix generates, not a quotation,
        # so a stale reference in it is simply wrong rather than historical. The
        # quoted rule TEXTS below the table keep theirs, because those are
        # quotations and renumbering them would falsify them.
        title = re.sub(r"\s*(?:on|in|of)?\s*\u00a7\s*\d+(?:\.\d+)?\s*", " ", title).strip()
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
        # The RETURNED verdict, which a discharged rule states explicitly. This
        # must be tried FIRST: the fallbacks below scan for a bolded all-caps
        # phrase, and a rule's own text is full of them -- it enumerates its
        # possible outcomes. M-49 came out as "MECHANISM SURVIVES CAPACITY", which
        # is the first branch it DEFINES and not the one it RETURNED
        # (UNDER-POWERED); M-50 as "REFUTED" and M-51 as "SURVIVES BOTH", both
        # likewise branch definitions. A verdict column showing a rule's most
        # favourable possible outcome instead of its actual one is the worst
        # direction for this particular error.
        # Not line-anchored: the discharge line reads
        # "**Discharged** by `artifact`. **It returns X.**" on ONE line, so a
        # ^-anchored pattern matched nothing and fell through to the branch-
        # definition scan below.
        m_ret = re.search(r"\*\*It returns\s+(.+?)\.?\*\*", blk)
        if m_ret:
            verdict = m_ret.group(1).strip().strip("*").strip()
        m_st = re.search(r"^\*\*Status\*\*\s*([A-Z][A-Za-z ,]*?)\s*—\s*([^·\n]+)",
                         blk, re.M)
        if m_st and not verdict:
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
        _raw = rm.group(1) if rm else "\n".join(blk.split("\n")[1:6])
        # TWO PRODUCTS, not one longer one (Session 5 addendum B.1). The BODY gets
        # the table and nothing else; the full committed text goes to supplementary,
        # unabridged. Simply removing the truncation would have ballooned the very
        # appendix this session exists to shrink -- at fifteen rules it is the
        # obvious fix and the wrong one. A quotation ending mid-sentence now ships
        # nowhere: the table quotes titles, and the supplementary quotes in full.
        rule_text = one_line(_raw)
        # "In full, unabridged" means the whole committed entry, not a heuristic
        # slice of it. The cue regexes above match only some rules; the rest fell
        # through to a five-line head slice, which is exactly how a quotation ends
        # mid-sentence -- M-16 stopped at "and at the 2500". The supplementary takes
        # the block itself, minus its heading line, so there is nothing to cut.
        rule_text_full = "\n".join(blk.split("\n")[1:]).strip()
        if not m_ret and eid in RETURNED and RETURNED[eid] in NUM:
            verdict = str(NUM[RETURNED[eid]]["value"])
        if "NOT YET DISCHARGED" in status.upper():
            verdict = "not yet discharged"
        key = next((k for k in lead if k.startswith(eid + " ")), None)
        # Figure 4 plots a FIXED list of rules and the newest three are not on it.
        # Rather than grow that list -- Figure 4 is a figure, and it is legible at
        # eight bars -- the lead time is computed here the same way: the commit
        # that introduced the rule's ledger heading against the commit that
        # introduced the artifact discharging it. Same definition, same source,
        # and it generalises to every future rule without an edit.
        _self_lead = None
        _art = None
        if key is None:
            # Two forms name the discharging artifact. The older rules carry their
            # own `**Discharged** by` line; M-70 was discharged by setting only its
            # Status line, which is all its rule permitted, so the artifact is named
            # there. Reading only the first form left M-70's lead time "not
            # computed" in the one appendix that exists to state it.
            _art = (re.search(r"^\*\*Discharged\*\* by `([^`]+)`", blk, re.M)
                    or re.search(r"^\*\*Status\*\*[^\n]*?DISCHARGED by `([^`]+)`", blk, re.M))
            if _art:
                _rc = subprocess.run(
                    ["git", "log", "--format=%ct", "-S", f"### {eid} ",
                     "--", LEDGER], capture_output=True, text=True).stdout.split()
                _dc = subprocess.run(
                    ["git", "log", "--diff-filter=A", "--format=%ct", "--",
                     _art.group(1)], capture_output=True, text=True).stdout.split()
                if _rc and _dc:
                    _self_lead = (int(_dc[-1]) - int(_rc[-1])) / 3600.0
        if key is None and eid == "S-12":
            # S-12 withdraws the Task 3 rule, which Figure 4 labels by its subject
            # rather than by an identifier -- because at the time it was written it
            # had none.
            key = next((k for k in lead if k.startswith("Task 3")), None)
        rows.append({
            "id": eid, "title": title, "status": status, "verdict": verdict,
            "rule_text": rule_text,
            "rule_text_full": rule_text_full,
            "lead_hours": lead[key]["lead_hours"] if key else _self_lead,
            "lead_source": ("Figure 4" if key else
                            ("this appendix, from git" if _self_lead is not None
                             else None)),
            "tested_by": (lead[key]["tested_by"] if key else
                          (_art.group(1) if _art else None)),
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

    # The table and the ledger gate must count the same set. ledger_check.py
    # reports "pre-registered rules not yet discharged" from the Status lines; a
    # rule it counts and this table omits is exactly how M-52 went missing.
    def _status_says_prereg(eid_):
        b = entry(txt, eid_) or ""
        m_ = re.search(r"^\*\*Status\*\*\s*(.+)$", b, re.M)
        if not m_:
            return False
        st_ = m_.group(1).upper()
        # "NOT PRE-REGISTERED as a verdict" is R-38 saying of ITSELF that it is not
        # one. Matching the bare substring pulled it into a table of
        # pre-registrations, which is the inverse of what that entry exists to say.
        return "PRE-REGISTERED" in st_ and "NOT PRE-REGISTERED" not in st_
    _gate_ids = sorted({m.group(1) for m in re.finditer(r"^### ([A-Z]-\d+) ", txt, re.M)
                        if _status_says_prereg(m.group(1))})
    _missing = [x for x in _gate_ids if x not in {r["id"] for r in rows}]
    assert not _missing, (
        f"entries whose Status names a pre-registration are absent from Appendix E: "
        f"{_missing}. The table is headed 'every pre-registered rule'.")
    json.dump({"n_rules": len(rows), "n_with_lead_time": n_lead,
               "n_status_prereg": len(_gate_ids), "rules": rows},
              open(os.path.join(R.RESULTS, OUT), "w"), indent=2)
    print(f"  wrote results/{OUT}")

    # The supplementary half of B.1: every rule's committed text, in full, with no
    # ellipsis anywhere. Generated here rather than maintained by hand so it cannot
    # drift from the table beside it.
    _sup = os.path.join("docs", "APPENDIX_G_RULES.md")
    with open(_sup, "w") as _f:
        _f.write("# Appendix E, supplementary — every pre-registered rule "
                 "in its own committed words\n\n")
        _f.write("Generated by `scripts/appendix_g_rules.py` from `FINDINGS_LEDGER.md`. "
                 "The paper's Appendix E carries the table; this carries the text each "
                 "rule was committed with, **unabridged**.\n\n")
        _f.write("These are quotations. Their section references are the ones current "
                 "when each rule was committed and some no longer resolve — `M-45` "
                 "governs \"the within-trajectory control on section 5.6\", which is now "
                 "section 6.6. Round 2 renumbered section 6 (old → new: §6.5 → §6.3 (folded in), §6.6 → §6.5, §6.7 → §6.6, §6.8 → §6.7, §6.9 → §6.5 (folded in), §6.10 → §6.8, §6.11 → §6.8 (merged; the detail of both rules is in Appendices O and P)). Renumbering a quotation to keep a cross-reference checker "
                 "happy would falsify it, so they stand as written. The same holds for "
                 "appendix letters, which moved in the referee revision: a rule that "
                 "says \"Appendix D\" means the appendix that bore that letter when the "
                 "rule was committed.\n\n")
        for _r in rows:
            _f.write(f"## {_r['id']} — {_r['title']}\n\n{_r['rule_text_full']}\n\n")
    # UNABRIDGED, checked directly. This asserted that the file carried no "…",
    # as a proxy for "no quotation was cut". The proxy failed on the first rule
    # whose committed text USES an ellipsis -- M-70 writes its horizon bands as
    # {9 … 32} -- and it would have passed a quotation cut without one. The
    # property itself is checkable: every quoted text is the ledger block
    # verbatim, and the file is exactly the header plus those quotations.
    _body = open(_sup).read()
    # The first comparison below re-uses entry(), the function that cut the block,
    # so on its own it cannot see a wrong cut. The ledger is also split here a
    # second, independent way -- at each identifier heading -- and each quotation
    # must equal that block too.
    _by_id = {}
    for _b in re.split(r"\n(?=### [A-Z]+-\d+[a-z]? )", txt):
        _mm = re.match(r"### ([A-Z]+-\d+[a-z]?) ", _b)
        if _mm:
            _by_id.setdefault(_mm.group(1), _b)
    for _r in rows:
        _ind = _by_id.get(_r["id"])
        assert _ind is not None and \
            "\n".join(_ind.split("\n")[1:]).strip() == _r["rule_text_full"], \
            f"{_r['id']}: quotation differs from its block cut at identifier headings"
        _blk = entry(txt, _r["id"])
        assert _blk is not None and _r["rule_text_full"] == "\n".join(_blk.split("\n")[1:]).strip(), \
            f"{_r['id']}: supplementary quotation is not its ledger block verbatim"
        assert _r["rule_text_full"] in txt, f"{_r['id']}: quotation absent from the ledger"
        assert f"## {_r['id']} — {_r['title']}\n\n{_r['rule_text_full']}\n\n" in _body, \
            f"{_r['id']}: supplementary does not carry the full quotation"
    # An ellipsis the ledger does not contain is still an abridgement marker.
    assert _body.count("…") == sum(_r["rule_text_full"].count("…") for _r in rows), \
        "supplementary carries an ellipsis its ledger quotations do not"
    print(f"  wrote {_sup} ({len(rows)} rules, each its ledger block verbatim)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
