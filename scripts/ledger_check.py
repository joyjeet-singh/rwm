"""
Ledger consistency check (release brief 1.1) -- also the claims-to-evidence map (3.4).

Every CONTRIB entry must carry an evidence class of SRC, DATA or RUN, and every
artifact it names must exist. An INFER-only CONTRIB entry is a blocker.

Third invariant, added after the review found R-27 still tagged CONFIRMED / CONTRIB
while S-10 retracted it, and rendered as CONFIRMED in the release-facing claims map:
every S-* entry declares a **Retracts** line naming the IDs it supersedes, and each
named ID must carry SUPERSEDED or RETRACTED in its own Status line and must not still
be tagged CONTRIB. A retraction that only exists in the retracting entry is invisible
to anyone reading the claim it retracts.
"""
import os, re, sys, json
LEDGER="FINDINGS_LEDGER.md"
txt=open(LEDGER).read()
blocks=re.split(r'\n### ', txt)
rows=[]
for b in blocks[1:]:
    m=re.match(r'([A-Z]-\d+)\s+—\s+(.*?)(?:\s+·|\n)', b)
    if not m: continue
    eid, claim = m.group(1), m.group(2).strip().rstrip('·').strip()
    body=b
    rel=re.search(r'\*\*Relevance\*\*\s*([A-Z]+)', body)
    relevance=rel.group(1) if rel else ""
    if not relevance:
        rel2=re.search(r'·\s*\*\*Relevance\*\*\s*([A-Z]+)', body)
        relevance=rel2.group(1) if rel2 else ""
    st=re.search(r'\*\*Status\*\*\s*(.+)', body)
    status=st.group(1).split('·')[0].strip() if st else ""
    ev=re.findall(r'`(SRC|DATA|RUN|EXT|INFER)`', body)
    arts=set(re.findall(r'`(results/[\w./-]+|figures/[\w./-]+|src/[\w./-]+|scripts/[\w./-]+)`', body))
    retr=re.search(r'\*\*Retracts\*\*\s*(.+)', body)
    rows.append({"id":eid,"claim":claim[:88],"relevance":relevance,"status":status,
                 "evidence":sorted(set(ev)),"artifacts":sorted(arts),
                 "retracts":sorted(set(re.findall(r'\b([A-Z]-\d+)\b', retr.group(1)))) if retr else []})
contrib=[r for r in rows if r["relevance"]=="CONTRIB"]
print("="*100); print("LEDGER CONSISTENCY CHECK"); print("="*100)
print(f"  entries parsed: {len(rows)}   tagged CONTRIB: {len(contrib)}")
hard={"SRC","DATA","RUN"}
flagged=[r for r in contrib if not (set(r["evidence"]) & hard)]
missing=[]
for r in rows:
    for a in r["artifacts"]:
        if not os.path.exists(a): missing.append((r["id"],a))
print(f"\n  CONTRIB entries lacking SRC/DATA/RUN evidence: {len(flagged)}")
for r in flagged:
    print(f"    !! {r['id']}  evidence={r['evidence'] or 'NONE PARSED'}  {r['claim'][:60]}")
print(f"\n  named artifacts that do not exist: {len(missing)}")
for eid,a in missing[:20]: print(f"    !! {eid} -> {a}")

by_id={r["id"]:r for r in rows}
supersessions=[(r["id"],t) for r in rows for t in r["retracts"]]
unmarked=[]
for sid,tid in supersessions:
    t=by_id.get(tid)
    if t is None:
        unmarked.append((sid,tid,"target does not exist")); continue
    st=t["status"].upper()
    if "SUPERSEDED" not in st and "RETRACTED" not in st:
        unmarked.append((sid,tid,f"target Status is {t['status'][:40]!r}"))
    elif t["relevance"]=="CONTRIB" and "IN PART" not in st:
        # a wholly superseded claim must not still be advertised as a contribution;
        # SUPERSEDED IN PART may, because part of it still stands.
        unmarked.append((sid,tid,"target still tagged CONTRIB"))
declared=[r["id"] for r in rows if r["id"].startswith("S-") and not r["retracts"]
          and not re.search(r'\*\*Retracts\*\*', txt.split("### "+r["id"])[1].split("\n### ")[0])]
print(f"\n  supersessions declared: {len(supersessions)}")
print(f"  retractions not reflected in the retracted entry: {len(unmarked)}")
for sid,tid,why in unmarked: print(f"    !! {sid} retracts {tid} but {why}")
if declared:
    print(f"  S-* entries with no **Retracts** line: {len(declared)}")
    for d in declared: print(f"    !! {d}")
json.dump(rows,open("results/claims_to_evidence.json","w"),indent=2)
with open("results/claims_to_evidence.md","w") as f:
    f.write("# Claims-to-evidence map\n\nOne row per CONTRIB ledger entry.\n\n")
    f.write("| ID | Claim | Evidence | Status | Artifacts |\n|---|---|---|---|---|\n")
    for r in contrib:
        f.write(f"| `{r['id']}` | {r['claim']} | {', '.join('`'+e+'`' for e in r['evidence']) or '—'} "
                f"| {r['status'][:40]} | {', '.join('`'+a+'`' for a in r['artifacts'][:2]) or '—'} |\n")
print(f"\n  wrote results/claims_to_evidence.md ({len(contrib)} CONTRIB rows)")
ok = not flagged and not missing and not unmarked and not declared
print(f"\n  RESULT: {'PASS' if ok else 'BLOCKER -- see flags above'}")
sys.exit(0 if ok else 1)
