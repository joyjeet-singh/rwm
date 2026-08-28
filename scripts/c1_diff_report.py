"""
C1 diff report -- make the human review of UNREVIEWED claims tractable.

WHY THIS AND NOT A BULK APPROVAL. `task_c1_claims_audit.py` drops a claim's
verdict when its wording changes, so a stale verdict cannot be carried forward
silently. A revision that rewrites prose therefore returns a pile of claims to
UNREVIEWED -- correctly. `c1_review_revision.py` exists to record a review a
person did, and its own docstring says running it after a prose change silently
approves the new wording. It is not this script's job to run it, and it is not
this script's job to replace the person.

WHAT THIS DOES INSTEAD. For every UNREVIEWED claim it prints, side by side:

  BEFORE   the last text that carried an approved verdict, from git
  NOW      the current text
  VALUES   the artifact value each {{key}} resolves to, before and after

...and then answers the only question that scales: **did the rewrite change the
claim, or only the wording?** A claim is routed to NEEDS REVIEW when any of

  - a resolved artifact value changed
  - the horizon named in the sentence changed
  - a count changed (k-of-n, "N of M", a bare integer)
  - a hedge word was added or removed (may, appears, suggests, established,
    supported, cannot, only, every, never...)

and to WORDING ONLY otherwise. The split is printed first, so the person knows
what they are agreeing to before they start rather than after.

A claim in WORDING ONLY is not approved by this script. It is *sorted*. The
person still says yes.

    python scripts/c1_diff_report.py                 the report
    python scripts/c1_diff_report.py --needs-review  only the pile that matters
    python scripts/c1_diff_report.py --rev <rev>     compare against another rev
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402

AUDIT = os.path.join(R.RESULTS, "task_c1_claims_audit.json")
VERDICTS = os.path.join(R.RESULTS, "c1_verdicts.json")

# Words that change what a sentence CLAIMS rather than how it reads. Adding or
# removing one of these is never "wording only".
HEDGES = [
    "may", "might", "appears", "suggests", "plausibly", "candidate", "hypothesis",
    "established", "supported", "not established", "cannot", "does not", "no ",
    "only", "every", "never", "all ", "none", "at least", "at most", "roughly",
    "approximately", "about", "up to", "bounds", "isolates", "conflates",
    "pre-registered", "post-hoc", "retracted", "withdrawn",
]


def git_show(rev, path):
    o = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True, text=True)
    return o.stdout if o.returncode == 0 else None


def resolved(text, numbers):
    """{key: value} for every placeholder in a claim, as the build resolves it."""
    return {k: str(numbers[k]["value"]) if k in numbers else "<absent>"
            for k in re.findall(r"\{\{([A-Za-z0-9_]+)\}\}", text)}


def horizons_named(text):
    return sorted({int(m.group(1)) for m in re.finditer(r"\bh\s*=?\s*(\d+)\b", text)}
                  | {int(m.group(1)) for m in re.finditer(r"\b(\d+)-step\b", text)})


def counts_in(text):
    return sorted(re.findall(r"(\d+)\s+of\s+(\d+)", text)) + \
        sorted(re.findall(r"(\d+)\s*/\s*(\d+)", text))


def hedges_in(text):
    t = text.lower()
    return sorted(h.strip() for h in HEDGES if h in t)


def classify(before, now, numbers_before, numbers_now):
    """Why this claim needs a person, or why it does not."""
    reasons = []
    if before is None:
        return ["no earlier text found — this claim is new"]
    rb, rn = resolved(before, numbers_before), resolved(now, numbers_now)
    changed = sorted(k for k in set(rb) & set(rn) if rb[k] != rn[k])
    if changed:
        reasons.append("resolved value changed: "
                       + ", ".join(f"{k} {rb[k]}→{rn[k]}" for k in changed[:4]))
    gone = sorted(set(rb) - set(rn))
    added = sorted(set(rn) - set(rb))
    if gone or added:
        reasons.append(f"placeholders changed: -{gone[:3]} +{added[:3]}")
    hb, hn = horizons_named(before), horizons_named(now)
    if hb != hn:
        reasons.append(f"horizon named changed: {hb or 'none'} → {hn or 'none'}")
    cb, cn = counts_in(before), counts_in(now)
    if cb != cn:
        reasons.append(f"count changed: {cb or 'none'} → {cn or 'none'}")
    eb, en = set(hedges_in(before)), set(hedges_in(now))
    if eb != en:
        d = sorted(en - eb), sorted(eb - en)
        reasons.append(f"hedging changed: +{d[0][:3]} -{d[1][:3]}")
    return reasons


def main():
    rev = sys.argv[sys.argv.index("--rev") + 1] if "--rev" in sys.argv else None
    only_needs = "--needs-review" in sys.argv
    audit = json.load(open(AUDIT))
    numbers_now = json.load(open(os.path.join(R.RESULTS, "paper_numbers.json")))

    un = [c for c in audit["claims"] if c["verdict"] == "UNREVIEWED"]
    if not un:
        print("C1 DIFF REPORT\n" + "=" * 92 + "\n  no UNREVIEWED claims.")
        return 0

    # The last revision at which every claim had a verdict is the natural
    # baseline: it is the text a person last agreed to.
    if rev is None:
        o = subprocess.run(["git", "log", "--format=%H", "-n", "40", "--",
                            "results/c1_verdicts.json"], capture_output=True, text=True)
        revs = [x for x in o.stdout.split() if x]
        rev = revs[0] if revs else "HEAD"
    prev_tpl = git_show(rev, "PAPER.template.md") or ""
    prev_numbers = {}
    raw = git_show(rev, "results/paper_numbers.json")
    if raw:
        try:
            prev_numbers = json.loads(raw)
        except json.JSONDecodeError:
            prev_numbers = {}

    # Match a current claim to its previous text by similarity on the NORMALISED
    # sentence -- placeholders and emphasis stripped, so a claim whose numbers
    # moved still matches the sentence it came from. A prefix match was tried
    # first and failed on every claim whose opening words were edited, which is
    # most of them in a revision that rewrote openings.
    import difflib

    def norm(t):
        t = re.sub(r"\{\{[A-Za-z0-9_]+\}\}", " ", t)
        t = re.sub(r"[*_`\[\]]", " ", t)
        return " ".join(t.split()).lower()

    prev_sentences = [x.strip() for x in re.split(r"(?<=[.!?])\s+", prev_tpl) if x.strip()]
    prev_norm = [(norm(x), x) for x in prev_sentences]

    def previous_of(claim):
        cn = norm(claim)
        if len(cn) < 25:
            return None
        best, best_r = None, 0.0
        for pn, raw in prev_norm:
            if abs(len(pn) - len(cn)) > max(120, 0.6 * len(cn)):
                continue
            r = difflib.SequenceMatcher(None, cn, pn).quick_ratio()
            if r < best_r or r < 0.55:
                continue
            r = difflib.SequenceMatcher(None, cn, pn).ratio()
            if r > best_r:
                best, best_r = raw, r
        return best if best_r >= 0.62 else None

    rows = []
    for c in un:
        prev = previous_of(c["claim"])
        why = classify(prev, c["claim"], prev_numbers, numbers_now)
        rows.append({"id": c["id"], "section": c["section"], "claim": c["claim"],
                     "previous": prev, "reasons": why,
                     "route": "NEEDS REVIEW" if why else "wording only",
                     "artifacts": c.get("artifacts", [])})

    needs = [r for r in rows if r["route"] == "NEEDS REVIEW"]
    wording = [r for r in rows if r["route"] == "wording only"]

    print("C1 DIFF REPORT — what the human review is actually being asked")
    print("=" * 104)
    print(f"  baseline revision        : {rev[:9]} (the last commit that carried verdicts)")
    print(f"  claims returned UNREVIEWED: {len(rows)}")
    print(f"    NEEDS REVIEW           : {len(needs)}   "
          f"(a value, a horizon, a count or a hedge changed)")
    print(f"    wording only           : {len(wording)}   "
          f"(same claim, different sentence — still yours to confirm)")
    print()
    print("  This script sorts. It does not approve. c1_review_revision.py records")
    print("  a review a person did, and running it after a prose change approves")
    print("  the new wording silently — which is why neither is a pipeline stage.")
    print()

    for r in (needs if only_needs else needs + wording):
        print("-" * 104)
        print(f"  [{r['id']}] {r['route']}   §{r['section'][:44]}")
        for why in r["reasons"]:
            print(f"      ! {why}")
        if r["previous"]:
            print(f"    BEFORE  {r['previous'][:300]}")
        else:
            print("    BEFORE  (no matching earlier sentence)")
        print(f"    NOW     {r['claim'][:300]}")
        if r["artifacts"]:
            print(f"    backed by {', '.join(r['artifacts'][:3])}")
    print("-" * 104)
    op = os.path.join(R.RESULTS, "c1_diff_report.json")
    json.dump({"baseline_rev": rev, "n_unreviewed": len(rows),
               "n_needs_review": len(needs), "n_wording_only": len(wording),
               "rows": rows}, open(op, "w"), indent=2)
    print(f"  {len(needs)} need a person; {len(wording)} are wording only. "
          f"wrote {R.rel(op)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
