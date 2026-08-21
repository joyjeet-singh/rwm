"""C1 — audit every declarative claim in the paper against its evidence.

Claims are enumerated MECHANICALLY from PAPER.template.md, not from recall: every
sentence in the abstract and body is extracted, and a sentence is treated as a
declarative claim if it carries a substituted number, a comparative, or an
assertive verb. For each claim the script records which {{keys}} it used, hence
which artifact backs it, and the sample size that artifact reports.

The VERDICT column is the one judgement in the file. It is stored in
results/c1_verdicts.json keyed by a hash of the claim text, so a claim whose
wording changes loses its verdict and reappears as UNREVIEWED rather than
silently keeping a stale one.

Writes results/task_c1_claims_audit.json and docs/CLAIMS_AUDIT.md.
"""
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402

TEMPLATE = "PAPER.template.md"
VERDICTS = "results/c1_verdicts.json"

ASSERTIVE = re.compile(
    r"\b(is|are|was|were|does|do|shows?|show|reproduces?|holds?|fails?|beats?|"
    r"exceeds?|implies|implied|cannot|never|every|all|none|no |confirms?|"
    r"establishes?|demonstrates?|proves?|means?|costs?|explains?)\b", re.I)
COMPARATIVE = re.compile(r"\b(more|less|better|worse|larger|smaller|higher|lower|"
                         r"than|×|x smaller|x larger|orders of magnitude)\b", re.I)


def sentences(text):
    text = re.sub(r"\|[^\n]*\|", " ", text)          # tables handled separately
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"\$\$.*?\$\$", " ", text, flags=re.S)
    text = re.sub(r"\n\s*\n", "\n\n", text)
    for para in text.split("\n\n"):
        p = " ".join(x.strip() for x in para.split("\n")).strip()
        if not p or p.startswith("#") or p.startswith("!") or p.startswith("---"):
            continue
        for s in re.split(r"(?<=[.!?])\s+(?=[A-Z*`$])", p):
            s = s.strip(" -*")
            if len(s) > 25:
                yield s


def main():
    tpl = open(TEMPLATE).read()
    nums = json.load(open(os.path.join(R.RESULTS, "paper_numbers.json")))
    verdicts = json.load(open(VERDICTS)) if os.path.exists(VERDICTS) else {}

    # section map
    body, sec = [], "(front matter)"
    for line in tpl.split("\n"):
        m = re.match(r"^#{2,3}\s+(.*)$", line)
        if m:
            sec = m.group(1).strip()
        body.append((sec, line))

    claims, seen = [], set()
    for sec in dict.fromkeys(s for s, _ in body):
        text = "\n".join(l for s, l in body if s == sec)
        for s in sentences(text):
            keys = re.findall(r"\{\{([A-Za-z0-9_]+)\}\}", s)
            quantitative = bool(keys) or bool(re.search(r"\b\d+(\.\d+)?\s*(%|×|x)\b", s))
            if not (quantitative or (ASSERTIVE.search(s) and COMPARATIVE.search(s))):
                continue
            h = hashlib.sha256(s.encode()).hexdigest()[:12]
            if h in seen:
                continue
            seen.add(h)
            srcs = sorted({nums[k]["source"] for k in keys if k in nums})
            v = verdicts.get(h, {})
            claims.append({
                "id": h, "section": sec, "claim": s,
                "keys": keys, "artifacts": srcs,
                "n_keys": len(keys),
                "generated": bool(keys),
                "verdict": v.get("verdict", "UNREVIEWED"),
                "sample_size": v.get("sample_size", ""),
                "note": v.get("note", ""),
            })

    tally = {}
    for c in claims:
        tally[c["verdict"]] = tally.get(c["verdict"], 0) + 1

    out = {"n_claims": len(claims), "by_verdict": tally, "claims": claims}
    op = os.path.join(R.RESULTS, "task_c1_claims_audit.json")
    json.dump(out, open(op, "w"), indent=2)

    os.makedirs("docs", exist_ok=True)
    L = ["# Claims-versus-evidence audit (C1)", "",
         "One row per declarative claim in the paper. Claims are enumerated mechanically from",
         "`PAPER.template.md` by `scripts/task_c1_claims_audit.py`; the verdict column is the",
         "only judgement, and is keyed to the claim's text so that rewording a claim resets it",
         "to UNREVIEWED rather than carrying a stale verdict forward.", "",
         f"**{len(claims)} claims.** " + ", ".join(f"{k}: {v}" for k, v in sorted(tally.items())),
         "", "| # | § | claim | backed by | verdict |", "|---|---|---|---|---|"]
    for i, c in enumerate(claims, 1):
        cl = c["claim"].replace("|", r"\|")
        cl = cl[:150] + ("…" if len(cl) > 150 else "")
        art = ", ".join(f"`{os.path.basename(a)}`" for a in c["artifacts"]) or "—"
        L.append(f"| {i} | {c['section'][:26]} | {cl} | {art} | **{c['verdict']}** |")
    open("docs/CLAIMS_AUDIT.md", "w").write("\n".join(L) + "\n")

    print("C1 — CLAIMS AUDIT")
    print("=" * 78)
    print(f"  claims extracted        : {len(claims)}")
    print(f"  carrying a generated number: {sum(1 for c in claims if c['generated'])}")
    print(f"  with NO backing artifact   : {sum(1 for c in claims if not c['artifacts'])}")
    for k, v in sorted(tally.items()):
        print(f"    {k:<12} {v}")
    print(f"\n  wrote {R.rel(op)} and docs/CLAIMS_AUDIT.md")


if __name__ == "__main__":
    main()
