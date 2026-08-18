"""
Ledger consistency check (release brief 1.1) -- also the claims-to-evidence map (3.4).

Every CONTRIB entry must carry an evidence class of SRC, DATA or RUN, and every
artifact it names must exist. An INFER-only CONTRIB entry is a blocker.
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
    rows.append({"id":eid,"claim":claim[:88],"relevance":relevance,"status":status,
                 "evidence":sorted(set(ev)),"artifacts":sorted(arts)})
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
json.dump(rows,open("results/claims_to_evidence.json","w"),indent=2)
with open("results/claims_to_evidence.md","w") as f:
    f.write("# Claims-to-evidence map\n\nOne row per CONTRIB ledger entry.\n\n")
    f.write("| ID | Claim | Evidence | Status | Artifacts |\n|---|---|---|---|---|\n")
    for r in contrib:
        f.write(f"| `{r['id']}` | {r['claim']} | {', '.join('`'+e+'`' for e in r['evidence']) or '—'} "
                f"| {r['status'][:40]} | {', '.join('`'+a+'`' for a in r['artifacts'][:2]) or '—'} |\n")
print(f"\n  wrote results/claims_to_evidence.md ({len(contrib)} CONTRIB rows)")
ok = not flagged and not missing
print(f"\n  RESULT: {'PASS' if ok else 'BLOCKER -- see flags above'}")
sys.exit(0 if ok else 1)
