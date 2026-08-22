"""A4 — verify every quotation from the original papers against the published text.

`EXT` is the one evidence class no build check can reach: a quotation from someone
else's paper cannot be recomputed from anything in this repository. It can,
however, be checked mechanically against the source, and this does that.

Not wired into reproduce.sh, because it needs the network and a clean clone must
not. Run it when a quotation changes, and record the result in
results/original_paper_figures.json, which is what the build reads.

    python scripts/verify_original_quotes.py            # fetch and check
    python scripts/verify_original_quotes.py --cached D # check against HTML in D

Two normalisations are applied to the source before comparison, and neither
touches the quotation:

  - tags stripped and whitespace collapsed, so line breaks in the HTML do not
    count as differences;
  - arXiv's HTML emits MathML *and* its alt text, so "$N=1$" flattens to
    "N = 1 N=1". That duplication is collapsed. Without it a correct
    transcription of the teacher-forcing sentence reports as a mismatch, which
    is what happened the first time this was run.
"""
import argparse
import html
import json
import os
import re
import sys
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402

SOURCES = {"2501.10100v1": "https://arxiv.org/html/2501.10100v1",
           "2501.10100v2": "https://arxiv.org/html/2501.10100v2",
           "2504.16680v1": "https://arxiv.org/html/2504.16680v1"}


def flatten(raw):
    t = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", raw)))
    t = re.sub(r"([A-Za-z])\s*=\s*(\d+)\s+\1=\2", r"\1=\2", t)
    return re.sub(r"\s+", " ", t)


def load(cached):
    out = {}
    for k, url in SOURCES.items():
        if cached:
            p = os.path.join(cached, f"{k}.html")
            if not os.path.exists(p):
                p = os.path.join(cached, "rwmu.html" if k.startswith("2504") else f"{k}.html")
            raw = open(p, encoding="utf8", errors="replace").read()
        else:
            req = urllib.request.Request(url, headers={"User-Agent": "reproduction-study"})
            raw = urllib.request.urlopen(req, timeout=90).read().decode("utf8", "replace")
        out[k] = flatten(raw)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cached", default=None, help="directory of already-fetched HTML")
    ap.add_argument("--date", required=True, help="date of this verification, YYYY-MM-DD")
    args = ap.parse_args()

    src = load(args.cached)
    path = os.path.join(R.RESULTS, "original_paper_figures.json")
    OP = json.load(open(path))

    print("A4 — QUOTATION VERIFICATION AGAINST THE PUBLISHED TEXT")
    print("=" * 100)
    rows, bad = [], 0
    for c in OP["claims"]:
        q = re.sub(r"\s+", " ", c["original_states"]).strip()
        parts = [p.strip() for p in q.split("...") if p.strip()]
        per = []
        for p in parts:
            found = sorted(k for k, t in src.items() if p in t)
            per.append({"fragment": p[:70], "found_in": found})
        ok = all(x["found_in"] for x in per)
        bad += not ok
        rows.append({"key": c["key"], "verbatim": ok, "fragments": per})
        print(f"  {'OK  ' if ok else 'FAIL'} {c['key']:<18} "
              f"{'; '.join(','.join(x['found_in']) or 'NOT FOUND' for x in per)}")

    # The abbreviation the follow-up uses for its own method, recorded because a
    # review asserted the opposite and the artifact is the record of what the
    # paper says, not of what anyone remembers it saying.
    counts = {k: {"RWM-O": t.count("RWM-O"), "RWM-U": t.count("RWM-U")} for k, t in src.items()}
    print("\n  method-abbreviation census:")
    for k, v in counts.items():
        print(f"    {k}: RWM-O x{v['RWM-O']}, RWM-U x{v['RWM-U']}")

    OP["verification"] = {
        "date": args.date,
        "method": ("each original_states string matched as a substring of the published text, "
                   "after stripping tags, collapsing whitespace, and collapsing arXiv's "
                   "duplicated MathML alt text"),
        "sources": SOURCES,
        "n_checked": len(rows),
        "n_verbatim": len(rows) - bad,
        "per_claim": rows,
        "abbreviation_census": counts,
    }
    json.dump(OP, open(path, "w"), indent=2)
    print("=" * 100)
    print(f"  {len(rows) - bad}/{len(rows)} verbatim; recorded in {R.rel(path)} as of {args.date}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
