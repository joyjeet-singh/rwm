"""A.3 -- audit input discovery by pattern across scripts/ and src/.

WHY. `A-01` is not a novel finding. Appendix B already records this defect class: the
sigma-collapse family is selected by the recorded width field "rather than by filename --
it did neither until the first capacity-matched run walked into the family through a
glob." That fix landed in `scripts/paper_numbers.py` (the `_width` predicate at :531) and
in `scripts/paper_figures.py`. It never reached `scripts/task_d3_ens5.py:299`, which is
the same defect surviving in a script the fix did not visit.

So the question worth asking is not "is this one glob wrong" but "where else did the fix
not reach". This script enumerates every pattern-based input discovery and classifies it.

TWO CLASSES, from the addendum:

  open population   the set is genuinely "whatever exists", and that is correct and
                    stated. A build step that bundles the figures that exist, or a
                    verifier that compares whatever was regenerated, is open by design.
                    A run-artifact glob that is GUARDED -- filtered to the released
                    architecture -- is also open: the population is "all released-width
                    runs", which is the population the claim is about.

  frozen at write   the artifact records a comparison against a set that has since
                    changed, or could change without anything noticing. This is A-01's
                    shape: an unguarded glob over a directory that grows.

The classification is recorded here rather than enforced by a new check kind. Session 5
is removing build machinery and adding some here works against that; recording the input
set in the artifact makes a stale set show up in a `reproduce.sh` diff on its own.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402

SELF = os.path.join("scripts", "input_set_audit.py")

PATTERNS = re.compile(r"glob\.glob|iglob|\.glob\(|os\.listdir|os\.walk|os\.scandir")

# Every hit is classified by hand, with the reason recorded. A hit that is not in this
# table makes the script fail rather than pass silently -- an unclassified discovery is
# exactly what A-01 was.
#
# Keyed by (file, the line's source text), not by line number (round 2, T8). Keyed by
# number, every edit above a glob unclassified it -- paper_numbers.py alone moved six by
# 2026-10-02 -- and the audit failed on lines nobody had changed. Keyed by text it is as
# strict: a new discovery, or an existing one whose code changes, is unclassified until
# someone reads it. Reasons name their guard instead of citing a line number that drifts.
CLASSIFICATION = {
    ("scripts/build_paper.py", 'figs = sorted(f for f in os.listdir(R.FIGURES) if f.startswith("paper_fig"))'):
        ("open population", "bundles the paper figures that exist; a build step, not a comparison set"),
    ("scripts/build_supplementary.py", "for root, dirs, names in os.walk(d):"):
        ("open population", "walks the tree to bundle whatever is present"),
    ("scripts/compile_paper.py", 'for f in os.listdir("tex"):'): ("open population", "tex sources for compilation"),
    ("scripts/compile_paper.py", "for f in os.listdir(R.FIGURES):"): ("open population", "figures for compilation"),
    ("scripts/make_anon_bundle.py", "for root, dirs, names in os.walk(d):"): ("open population", "walks the tree to stage it"),
    ("scripts/make_anon_bundle.py", "for root, dirs, names in os.walk(staging):"): ("open population", "walks staging to anonymise"),
    ("scripts/make_anon_bundle.py", "for root, _, names in os.walk(staging):"): ("open population", "walks staging to verify"),
    ("scripts/pipeline_coverage.py", 'for f in sorted(glob.glob("scripts/*.py")) + sorted(glob.glob("src/*.py")):'):
        ("open population", "coverage over whatever source files exist is the point of the measure"),
    ("scripts/paper_figures.py", 'for f in sorted(glob.glob(os.path.join(R.RESULTS, "step5_arm*.json"))):'):
        ("open population", "GUARDED: the loop skips any run whose recorded rnn_hidden_size is not the released "
                            "width, the Appendix B fix"),
    ("scripts/paper_numbers.py", 'for _f in sorted(glob.glob("results/step5_arm*.json")):'):
        ("open population", "GUARDED by assertion: every run, of any width or objective, must share one iteration "
                            "count per group (main, _10k), so a run at another count fails the build instead of "
                            "entering iters_main or iters_long silently (round 2, T8: the glob the plan names)"),
    ("scripts/paper_numbers.py", 'runs_all = sorted(glob.glob("results/step5_arm*.json"))'):
        ("open population", "GUARDED: the _width predicate defined beside it filters to the released width, the "
                            "Appendix B fix itself"),
    ("scripts/paper_numbers.py", 'for _f in sorted(_glob.glob("results/step5_*.json")):'):
        ("open population", "the CPU budget deliberately includes every run, M-49's arm included, and Appendix B "
                            "states how many of them are that arm"),
    ("scripts/paper_numbers.py", 'for _f in sorted(_g.glob("results/step5_arm*.json")):'):
        ("open population", "GUARDED: _width(_f) != _released_w continues, inside the loop"),
    ("scripts/paper_numbers.py", '_all = len([f for f in _g.glob("results/step5_arm*.json")'):
        ("open population", "GUARDED: _width(f) == _released_w in the comprehension"),
    ("scripts/paper_numbers.py", 'for f in sorted(_g2.glob("results/step5_arm*.json")):'):
        ("open population", "the run inventory is deliberately every run, and run_total matches Appendix B. NOTE: "
                            "width is not part of the row key, so M-49's width-124 runs share a row with "
                            "released-width runs of the same shape. That is a presentation gap, not a stale set -- "
                            "no number it produces is wrong -- and it is logged rather than changed, per A.3's "
                            "'fix only what affects a published number'"),
    ("scripts/part_f_gate.py", "for f in sorted(os.listdir(R.FIGURES)):"): ("open population", "figures present, for the gate"),
    ("scripts/part_f_gate.py", "f\"{len(os.listdir(R.FIGURES))} figures {figbad or 'clean'}\")"):
        ("open population", "figures present, for the gate"),
    ("scripts/submission_check.py", 'for f in os.listdir("tex"):'): ("open population", "tex sources present"),
    ("scripts/submission_check.py", "for f in os.listdir(R.FIGURES):"): ("open population", "figures present"),
    ("scripts/training_tail_slopes.py", '"sweep": sorted(glob.glob(os.path.join(res, "mn_sweep_run_M*_N*_seed[012].json"))),'):
        ("open population", "GUARDED: the pattern pins seeds 0-2, and the group sizes are asserted (24, 18, 6, 6), so "
                            "a new run matching it fails the build rather than entering the slope population"),
    ("scripts/training_tail_slopes.py", '"baseline": sorted(glob.glob(os.path.join(res, "baseline_run_*_s7_seed[012].json"))),'):
        ("open population", "GUARDED: spec s7 and seeds 0-2 only (X1's x1v1/x1v2 runs do not match), with the group "
                            "sizes asserted"),
    ("scripts/training_tail_slopes.py", '"arm_2500": sorted(glob.glob(os.path.join(res, "step5_arm[AB]_seed[012].json"))),'):
        ("open population", "GUARDED: Arms A and B at seeds 0-2, 2,500-iteration runs only, with the group sizes asserted"),
    ("scripts/training_tail_slopes.py", '"arm_10000": sorted(glob.glob(os.path.join(res, "step5_arm[AB]_seed[012]_10k.json"))),'):
        ("open population", "GUARDED: Arms A and B at seeds 0-2, the _10k runs only, with the group sizes asserted"),
    ("scripts/verify_reproduction.py", "for _fn in sorted(os.listdir(B)):"):
        ("open population", "compares whatever a clean clone regenerated; open by definition"),
    ("scripts/verify_reproduction.py", "for fn in sorted(os.listdir(B)):"):
        ("open population", "compares whatever a clean clone regenerated; open by definition"),
    ("scripts/xref_sweep.py", "for root, _, names in os.walk(up):"):
        ("open population", "walks the pinned upstream trees to resolve the paper's file:line pointers; whatever the "
                            "pinned commit holds is the population"),
}

# Classified discoveries whose code no longer exists, kept with the reason they left.
RETIRED = {
    ("scripts/task_d3_ens5.py", "A-01"): (
        "frozen at write time, then fixed: the unguarded glob over results/step5_armA_seed?.json is now an "
        "explicit seed list (ENS1_SEEDS), so no pattern remains to classify; the script's own comment records it"),
}

def main():
    hits, unclassified, seen = [], [], set()
    for d in ("scripts", "src"):
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".py"):
                continue
            p = os.path.join(d, fn)
            # This script is the instrument, not the subject. It scans whatever
            # source files exist -- an open population by definition -- and writes
            # no published number. Skipping it is recorded in the artifact rather
            # than left as a silent exclusion, and its line numbers would otherwise
            # shift under the hand-written table every time it is edited.
            if p == SELF:
                continue
            for i, line in enumerate(open(p, encoding="utf-8"), 1):
                if not PATTERNS.search(line):
                    continue
                key = (p, line.strip())
                if key not in CLASSIFICATION:
                    unclassified.append({"file": p, "line": i, "text": line.strip()[:120]})
                    continue
                # A classification covers one line. Keyed by text, a second line with the same
                # text in the same file would otherwise inherit it unread; it is a new discovery
                # until someone reads it (round 2, T8 review).
                if key in seen:
                    unclassified.append({"file": p, "line": i, "text": line.strip()[:120],
                                         "why": "same text as a classified line in this file"})
                    continue
                seen.add(key)
                cls, why = CLASSIFICATION[key]
                hits.append({"file": p, "line": i, "citation": f"{p}:{i}",
                             "text": line.strip()[:120], "classification": cls,
                             "reason": why})

    frozen = [h for h in hits if h["classification"] == "frozen at write time"]
    out = {
        "audit": "input discovery by pattern, scripts/ and src/",
        "defect_class": (
            "Appendix B: the collapse family is selected by the recorded width field "
            "'rather than by filename -- it did neither until the first capacity-matched "
            "run walked into the family through a glob'. A-01 is that same defect in a "
            "script the fix never reached, not a new finding."),
        "classes": ["open population", "frozen at write time"],
        "n_hits": len(hits),
        "n_open": len(hits) - len(frozen),
        "n_frozen": len(frozen),
        "n_unclassified": len(unclassified),
        "unclassified": unclassified,
        "hits": hits,
        "frozen_citations": [h["citation"] for h in frozen],
        "retired": [{"file": k[0], "id": k[1], "note": v} for k, v in RETIRED.items()],
        "keyed_by": "(file, the line's source text); line numbers are reported, not matched",
        "self_exclusion": (
            "scripts/input_set_audit.py is excluded from its own scan. It is the "
            "instrument rather than the subject: it discovers whatever source files "
            "exist, which is an open population by definition, and it writes no "
            "published number. Recorded here rather than left silent."),
        "no_new_check_kind": (
            "Deliberate, per A.4. Session 5 is removing build machinery. The durable "
            "guard is that artifacts record the input file list they were computed over, "
            "so a stale set shows up in a reproduce.sh diff on its own."),
    }
    op = os.path.join(R.RESULTS, "input_set_audit.json")
    json.dump(out, open(op, "w"), indent=2)

    print("=" * 96)
    print("INPUT-SET AUDIT — discovery by pattern")
    print("=" * 96)
    print(f"  hits {len(hits)}   open {out['n_open']}   frozen {len(frozen)}   "
          f"unclassified {len(unclassified)}\n")
    for h in hits:
        mark = "!!" if h["classification"] == "frozen at write time" else "  "
        print(f"  {mark} {h['citation']:<38} {h['classification']}")
    if unclassified:
        print("\n  UNCLASSIFIED — an input discovery nobody has looked at:")
        for u in unclassified:
            print(f"    !! {u['file']}:{u['line']}  {u['text']}")
    print(f"\n  wrote {R.rel(op)}")
    return 1 if unclassified else 0


if __name__ == "__main__":
    sys.exit(main())
