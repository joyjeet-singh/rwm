"""
C2 -- which sentences of the paper are older than the revisions that invalidated them.

THE FINDING THIS IMPLEMENTS. The four defects an independent reader found by hand
are all one shape: a sentence restating a quantity another section owns, left stale
by a revision that correctly updated the owning section. Two revisions produced
three of the four:

  (a) adding h = 100 to the evaluation grid, which moved every calibration
      extremum and every "at the deployment horizon" figure;
  (b) replacing §5's single-seed figures with three-seed ones, which moved the A/B
      ratio, the floor ratios and everything downstream of the 0.3509 / 1.5540 pair.

A sentence written BEFORE one of those and not touched since is in a stale cohort.
That is a property of the git history, not of the prose, and it is checkable.

WHY THIS TIERING AND NOT THE EXISTING ONE. The C1 review currently sorts claims by
section and by newness. Neither would have surfaced either confirmed defect:
appendix D is old text that nobody expected to move, and §5's table is new. Sorting
by revision cohort puts both at the top, because both sentences predate the
revision that made them wrong. The tiering is chosen from the evidence of what
actually went wrong rather than from where trouble seems likely.

The two cohort commits are FOUND, not typed: each is the commit that introduced a
specific string into a specific file, resolved by `git log -S`. A hash typed here
would be one more number nobody re-derived.

Writes results/revision_cohorts.json.
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402

TEMPLATE = "PAPER.template.md"
OUT = "revision_cohorts.json"

# (label, file, string whose INTRODUCTION marks the revision, why it matters)
COHORTS = [
    ("h100-grid", "scripts/task_d_nind20.py", "HORIZONS = (1, 8, 32, 100, 128, 368)",
     "h = 100 entered the evaluation grid. Every calibration extremum, every "
     "\"at the deployment horizon\" figure and every per-horizon cell count moved."),
    ("three-seed", "scripts/paper_numbers.py", "d1_ratio",
     "§5's headline moved from one seed to three. The A/B ratio went 4.4x to "
     "4.61x and everything downstream of the 0.3509 / 1.5540 pair moved with it "
     "-- except the hold-last floor ratio, which is B1."),
]


def introducing_commit(path, needle):
    out = subprocess.run(
        ["git", "log", "--format=%H\t%ct\t%h\t%s", "-S", needle, "--", path],
        capture_output=True, text=True).stdout.strip().split("\n")
    assert out and out[0], f"no commit introduces {needle!r} into {path}"
    sha, ts, short, subj = out[-1].split("\t", 3)
    return {"sha": sha, "short": short, "ts": int(ts), "subject": subj}


def blame_lines(path):
    out = subprocess.run(["git", "blame", "--line-porcelain", "--", path],
                         capture_output=True, text=True).stdout
    lines, cur = [], {}
    for ln in out.split("\n"):
        if re.match(r"^[0-9a-f]{40} ", ln):
            cur = {"sha": ln.split()[0]}
        elif ln.startswith("author-time "):
            cur["ts"] = int(ln.split()[1])
        elif ln.startswith("summary "):
            cur["subject"] = ln[8:]
        elif ln.startswith("\t"):
            cur["text"] = ln[1:]
            lines.append(cur)
            cur = {}
    return lines


def sentences_from(lines):
    """Group blamed lines into sentences, keeping the NEWEST commit on each.

    A sentence spanning three lines written at three different times is as new as
    its newest line: an edit to any part of it is a chance to have re-derived the
    whole.
    """
    out, buf = [], []
    for n, l in enumerate(lines, 1):
        buf.append((n, l))
        if re.search(r"[.!?:;]\s*$", l["text"]) or not l["text"].strip():
            if any(x[1]["text"].strip() for x in buf):
                out.append(buf)
            buf = []
    if buf and any(x[1]["text"].strip() for x in buf):
        out.append(buf)
    rows = []
    for grp in out:
        text = " ".join(x[1]["text"] for x in grp).strip()
        if not text or text.startswith("#") or set(text) <= set("-| :"):
            continue
        newest = max(grp, key=lambda x: x[1]["ts"])[1]
        rows.append({"line": grp[0][0], "n_lines": len(grp),
                     "text": re.sub(r"\s+", " ", text)[:220],
                     "sha": newest["sha"], "ts": newest["ts"],
                     "subject": newest["subject"],
                     "has_placeholder": "{{" in text})
    return rows


def main():
    cohorts = []
    for label, path, needle, why in COHORTS:
        c = introducing_commit(path, needle)
        c.update({"label": label, "anchor_file": path, "anchor_string": needle,
                  "why": why})
        cohorts.append(c)
    cohorts.sort(key=lambda c: c["ts"])

    rows = sentences_from(blame_lines(TEMPLATE))
    for r in rows:
        r["stale_for"] = [c["label"] for c in cohorts if r["ts"] < c["ts"]]

    tier0 = [r for r in rows if r["stale_for"]]
    # A sentence with no placeholder cannot restate a derived quantity by holding a
    # stale one -- but it can still assert a stale RELATION, which is what §4's
    # count and appendix D's extremum were. Both partitions are reported.
    t0_num = [r for r in tier0 if r["has_placeholder"]]

    print("C2 — REVISION COHORTS")
    print("=" * 96)
    for c in cohorts:
        print(f"  cohort {c['label']:<12} {c['short']}  {c['subject'][:56]}")
        print(f"         anchor: {c['anchor_string'][:52]!r} in {c['anchor_file']}")
    print()
    print(f"  sentences in {TEMPLATE}          : {len(rows)}")
    print(f"  older than at least one cohort   : {len(tier0)}  <- Tier 0 for the C1 review")
    print(f"    of those, carrying a substituted value: {len(t0_num)}")
    for c in cohorts:
        n = sum(1 for r in rows if c["label"] in r["stale_for"])
        print(f"    older than {c['label']:<12}: {n}")
    print()
    print("  oldest fifteen, which is where both confirmed defects sat:")
    for r in sorted(tier0, key=lambda x: x["ts"])[:15]:
        print(f"    L{r['line']:<5} {r['subject'][:34]:<34} "
              f"{'NUM' if r['has_placeholder'] else '   '} {r['text'][:72]}")

    rec = {"template": TEMPLATE, "cohorts": cohorts,
           "n_sentences": len(rows), "n_tier0": len(tier0),
           "n_tier0_with_values": len(t0_num),
           "tier0": sorted(tier0, key=lambda x: x["ts"]),
           "all": rows}
    json.dump(rec, open(os.path.join(R.RESULTS, OUT), "w"), indent=2)
    print(f"\n  wrote results/{OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
