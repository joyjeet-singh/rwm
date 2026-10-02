"""B -- what each check actually reads, and whether moving text shrinks its coverage.

WHY THIS EXISTS. `retraction-consistency` never named Appendix D. It scanned
`PAPER.template.md` whole, and Appendix D was inside it. Session 5a moved that appendix's
machinery to `docs/BUILD_CHECKS.md` and the scan silently stopped covering it -- a
reader-facing surface where a retracted claim could have survived unnoticed. 5a caught it
and added the new file to the check's own list.

5b moves more text than any other session. A check whose coverage shrinks silently as text
moves reads as protection and is not, which is this paper's own thesis about assertions
turned on its own build.

So every check is classified here by HOW IT SELECTS ITS INPUT:

  whole-file      it scans a file end to end. Coverage follows the file, so text that
                  leaves the file leaves the check unless the check's file list is
                  extended with it.
  named-region    it addresses a region by name -- a section heading, a marker, a
                  key. Text moving within the file is fine; the region disappearing
                  is what breaks it, loudly.
  artifact-only   it reads `results/*.json` and never the prose. Moving prose cannot
                  affect it.

An unclassified check fails this script rather than passing silently, for the same reason
`scripts/input_set_audit.py` fails on an unclassified glob.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402

CHECKER = "scripts/check_comparative_claims.py"

# The prose surfaces that exist after 5a. A whole-file scanner covers exactly the ones in
# its own file list; anything else is outside it.
PROSE_SURFACES = ["PAPER.template.md", "docs/BUILD_CHECKS.template.md",
                  "docs/APPENDIX_G_RULES.md", "README.md", "MODEL_CARD.md", "RESULTS.md",
                  "docs/EXTERNAL_READ_BRIEF.md"]

# Hand-classified, with the reason recorded. Keyed by check kind.
SCOPE = {
    "overlap": ("artifact-only", "compares two intervals from results/*.json"),
    "compare": ("artifact-only", "compares two artifact values"),
    "relvar": ("artifact-only", "relative variation between artifact values"),
    "cell": ("artifact-only", "one named artifact cell against another"),
    "horizon-consistency": ("named-region",
        "delegated to scripts/horizon_sweep.py, which walks PAPER.template.md and "
        "resolves each numeral to the artifact cell it came from. Region = the sentence "
        "and paragraph around each substituted value, so it follows the text wherever it "
        "sits IN THAT FILE. Text moved OUT of PAPER.template.md leaves its coverage -- so "
        "since B4 the checker appends docs/BUILD_CHECKS.template.md to what it sweeps."),
    "extremum": ("whole-file", "searches PAPER.md for the sentence naming an extremum"),
    "sign": ("whole-file", "searches PAPER.md for the sentence stating a direction"),
    "orders": ("whole-file", "searches PAPER.md for the order-of-magnitude phrasing"),
    "horizon-label": ("whole-file", "searches PAPER.md for a figure's horizon label"),
    "horizon-forbidden": ("whole-file", "searches PAPER.md for a horizon that must not appear"),
    "count-dependence": ("whole-file", "searches PAPER.md for the dependent count"),
    "frequency-consistency": ("whole-file",
        "searches PAPER.md for the frequency wording -- 'every', 'none', 'all'"),
    "scope-consistency": ("whole-file",
        "searches PAPER.md for universal quantifiers against an enumerated set"),
    "rule-seed-scope": ("whole-file",
        "scans each file in its own `files` list (PAPER.template.md, docs/BUILD_CHECKS.template.md, "
        "README.template.md) for the rule-horizon figures near 'rule' or 'pre-register'"),
    "overstat-reversal": ("whole-file",
        "scans each file in its own `files` list (PAPER.template.md, docs/BUILD_CHECKS.template.md, "
        "README.template.md), paragraph by paragraph, for 'overstat' beside an alignment figure"),
    "interval-required": ("whole-file",
        "searches PAPER.md for quoted quantities and requires each to carry its interval"),
    "arithmetic": ("whole-file", "searches PAPER.md for the sentence stating the sum"),
    "count-consistency": ("whole-file",
        "scans each file in the claim's own `files` list for near-miss spellings of a "
        "canonical value"),
    "retraction-consistency": ("whole-file",
        "scans each file in the claim's own `files` list for a retracted assertion. THIS "
        "IS THE ONE THAT SHRANK in 5a: docs/BUILD_CHECKS.template.md was added to all "
        "four of its file lists when Appendix D's machinery moved there"),
    "cross-artifact-sync": ("whole-file",
        "reads the named reader-facing file and requires the paper to contain the "
        "sentence it asserts"),
    "abstract-budget": ("named-region",
        "splits PAPER.md on '## Abstract' and the next section heading. Breaks loudly if "
        "the heading is renamed; unaffected by text moving elsewhere"),
    "kind-count": ("named-region",
        "finds '**The check kinds.**' and counts the italicised names in that paragraph. "
        "RE-POINTED in 5a from PAPER.md to docs/BUILD_CHECKS.md when the enumeration "
        "moved. A missing region fails the check"),
    "unit-consistency": ("whole-file",
        "added in Session 6. Scans PAPER.md end to end for every n_independent figure and "
        "requires the enclosing paragraph to name the unit it counts. It names no file "
        "list, so its coverage is PAPER.md and nothing else -- text moved out of the paper "
        "leaves it, which is the property this audit exists to record"),
    "restatement": ("whole-file",
        "scans PAPER.template.md end to end for a numeral typed where a key exists, and "
        "for a numeral ambiguous between two units. Since B4 it scans "
        "docs/BUILD_CHECKS.template.md appended, because section 8's block and Appendix C "
        "moved there"),
    # B4: five kinds the audit could not see until its regex admitted underscores.
    "figure_reference": ("whole-file",
        "counts the figures embedded in PAPER.md and the figure numbers its prose cites; "
        "the supplementary files carry no figures"),
    "population_partition": ("artifact-only",
        "sums the run table's row counts and the collapse family against totals read from "
        "results/*.json and paper_numbers.json; the prose sentence is only its anchor"),
    "retraction_class_consistency": ("whole-file",
        "scans each file in the claim's own `files` list, paragraph by paragraph, for a "
        "retraction identifier and the class the sentence gives it. B4 added "
        "docs/BUILD_CHECKS.md: with only the template listed, the generated enumeration "
        "that moved there fell out of scope and the claim passed on 9 namings of 19"),
    "table_renders": ("whole-file",
        "compares every table in the built PAPER.md, found with the converter's own "
        "table detector, with PAPER.tex; the supplementary files are not typeset"),
    "arena_consistency": ("named-region",
        "reads section 3.2's evidence table and each section it names; a missing section "
        "fails the check"),
}


def main():
    src = open(CHECKER).read()
    # B4: the class was [a-z-]+, so the five kinds spelled with an underscore --
    # figure_reference, population_partition, retraction_class_consistency,
    # table_renders, arena_consistency -- were invisible here, and "0
    # unclassified" held over 22 kinds of 27.
    kinds = sorted(set(re.findall(r'"kind": "([a-z_-]+)"', src)))
    unclassified = [k for k in kinds if k not in SCOPE]

    # Which files does each whole-file scanner actually name?
    files_by_kind = {}
    surface_by_kind = {}
    for m in re.finditer(r'"kind":\s*"([a-z_-]+)"(.*?)(?=\{"id"|\Z)', src, re.S):
        k, blk = m.group(1), m.group(2)
        fm = re.search(r'"files":\s*\[(.*?)\]', blk, re.S)
        if fm:
            files_by_kind.setdefault(k, set()).update(
                re.findall(r'"([^"]+\.md)"', fm.group(1)))
        # B4 added `surface`: a claim evaluated against the paper followed by the
        # supplementary file its text moved to. Recorded so the audit shows it.
        sm = re.search(r'"surface":\s*\[(.*?)\]', blk, re.S)
        if sm:
            surface_by_kind.setdefault(k, set()).update(
                re.findall(r'"([^"]+\.md)"', sm.group(1)))

    rows, gaps = [], []
    for k in kinds:
        scope, why = SCOPE.get(k, ("UNCLASSIFIED", ""))
        named = sorted(files_by_kind.get(k, []))
        row = {"kind": k, "input_selection": scope, "reason": why,
               "files_named_by_claims": named,
               "surface_named_by_claims": sorted(surface_by_kind.get(k, []))}
        if scope == "whole-file" and named:
            # A whole-file scanner covers what it names and nothing else. Which NAME it
            # needs depends on the tier it works at: a check that scans PAPER.template.md
            # needs the BUILD_CHECKS template, and one that scans PAPER.md needs the
            # built file. Requiring one name of both tiers would report a gap that is
            # not there and miss one that is.
            tier = ("template" if "PAPER.template.md" in named
                    else ("built" if "PAPER.md" in named else None))
            want = {"template": "docs/BUILD_CHECKS.template.md",
                    "built": "docs/BUILD_CHECKS.md"}.get(tier)
            row["tier"] = tier
            row["requires"] = want
            if want:
                row["covers_moved_text"] = want in named
                if want not in named:
                    row["gap"] = (f"scans the {tier} tier but does not name {want}; "
                                  f"text moved there is outside this check")
                    gaps.append({"kind": k, "tier": tier, "missing": [want]})
        rows.append(row)

    out = {
        "audit": "how each comparative check selects its input, and what moving text costs",
        "why": ("retraction-consistency scanned PAPER.template.md whole; moving Appendix "
                "D's machinery to docs/BUILD_CHECKS.md took that text out of its scan "
                "without any check failing. 5b moves more text than any other session, so "
                "the scopes are enumerated before the moves rather than after."),
        "classes": {
            "whole-file": "scans a file end to end; coverage follows the file, so moved "
                          "text leaves the check unless its file list is extended",
            "named-region": "addresses a region by name; text moving within the file is "
                            "fine, and the region disappearing fails loudly",
            "artifact-only": "reads results/*.json only; prose moves cannot affect it",
        },
        "prose_surfaces_after_5a": PROSE_SURFACES,
        "n_kinds": len(kinds),
        "n_whole_file": sum(1 for r in rows if r["input_selection"] == "whole-file"),
        "n_named_region": sum(1 for r in rows if r["input_selection"] == "named-region"),
        "n_artifact_only": sum(1 for r in rows if r["input_selection"] == "artifact-only"),
        "n_unclassified": len(unclassified),
        "unclassified": unclassified,
        "coverage_gaps": gaps,
        "checks": rows,
        "note_on_paper_md_scanners": (
            "The whole-file scanners that search PAPER.md rather than a named file list "
            "are unaffected by 5b's moves in one direction and exposed in the other: text "
            "moved WITHIN PAPER.md keeps its coverage, text moved OUT of the paper loses "
            "it. 5b moved text out only to Appendix D's generated list, which is inside "
            "PAPER.md, so 5b left their coverage unchanged. B4 did move text OUT: section "
            "8's reproducibility block and all of Appendix C went to docs/BUILD_CHECKS.md. "
            "Every claim that pinned moved text now declares that file as a `surface` and "
            "is evaluated against the paper followed by it (surface_named_by_claims above); "
            "the whole-paper sweeps -- horizon-forbidden, horizon-consistency, restatement -- "
            "take the supplementary as well; unit-consistency needs nothing, because the "
            "moved text states no n_independent figure."),
    }
    op = os.path.join(R.RESULTS, "check_scope_audit.json")
    json.dump(out, open(op, "w"), indent=2)

    print("=" * 92)
    print("CHECK SCOPE AUDIT — what each check reads")
    print("=" * 92)
    print(f"  kinds {len(kinds)}   whole-file {out['n_whole_file']}   "
          f"named-region {out['n_named_region']}   artifact-only {out['n_artifact_only']}"
          f"   unclassified {len(unclassified)}\n")
    for r in rows:
        mark = "!!" if r.get("gap") else "  "
        print(f"  {mark} {r['kind']:24} {r['input_selection']}")
    if unclassified:
        print(f"\n  UNCLASSIFIED: {unclassified}")
    if gaps:
        print(f"\n  COVERAGE GAPS ({len(gaps)}):")
        for g in gaps:
            print(f"    !! {g['kind']} does not scan {g['missing']}")
    print(f"\n  wrote {R.rel(op)}")
    return 1 if unclassified else 0


if __name__ == "__main__":
    sys.exit(main())
