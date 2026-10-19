"""G4 item 3: append one post hoc ledger entry (an R- result) to FINDINGS_LEDGER.md and move RESULTS.md's R- row.

    import g4_append as G; G.append(rid, title, body, evidence, relevance)

The ID must be the next free R- number; the entry must not exist yet; the body must hold no `### ` line (the ledger
splits entries on it). Every figure in a body is formatted from an artifact by its caller, never typed. Writes a .bak
copy of both files outside the repository first.
"""
import os
import re
import shutil

L, RES = "FINDINGS_LEDGER.md", "RESULTS.md"
EV = "/Users/Shared/rwm_verify/evidence/R5G4"


def append(rid, title, body, evidence, relevance="CONTRIB"):
    led = open(L, encoding="utf-8").read()
    nxt = max(int(n) for n in re.findall(r"^### R-(\d+) ", led, re.M)) + 1
    assert rid == f"R-{nxt}", (rid, nxt)
    assert f"### {rid} " not in led and "\n### " not in "\n" + body
    res = open(RES, encoding="utf-8").read()
    m = re.search(r"^\| `R-` [^|]*\| (\d+) \|", res, re.M)
    assert m and int(m.group(1)) == nxt - 1, (m and m.group(0), nxt)
    os.makedirs(EV, exist_ok=True)
    shutil.copy(L, os.path.join(EV, f"FINDINGS_LEDGER.md.before_{rid}"))
    shutil.copy(RES, os.path.join(EV, f"RESULTS.md.before_{rid}"))
    entry = (f"### {rid} — {title} · **NEW**\n{body.strip()}\n\n**Evidence** {evidence}\n"
             f"**Status** CONFIRMED · **Relevance** {relevance}\n")
    with open(L, "a", encoding="utf-8") as f:
        f.write(("\n" if led.endswith("\n") and not led.endswith("\n\n") else "") + entry)
    old = m.group(0)
    open(RES, "w", encoding="utf-8").write(res.replace(old, old.replace(f"| {nxt - 1} |", f"| {nxt} |"), 1))
    print(f"appended {rid}; RESULTS.md R- {nxt - 1} -> {nxt}")
