"""
Every artifact the paper's numbers come from must have a stage that writes it.

WHY THIS IS A SCRIPT AND NOT A HABIT. This class of gap has now been found three
times in one revision, by hand, and two of the three hand-audits were themselves
wrong:

  attempt 1  matched artifact paths against reproduce.sh. A stage's DECLARED
             OUTPUT is routinely a different file from the one its script writes,
             so this reported artifacts as covered that were not, and vice versa.
  attempt 2  matched a filename appearing anywhere in a script. Scripts READ each
             other's artifacts, so paper_figures.py reading a1_ab_by_horizon.json
             counted as writing it.
  attempt 3  got the method right and still missed three artifacts, because it was
             run before three more scripts were added.

The failure mode is specific and quiet: `paper_numbers.py` loads the artifact
unconditionally, a clean clone already CONTAINS results/, so the stage that
should have regenerated it is simply absent and everything passes. The
reproduction figure then reports the file as *copied* rather than *regenerated* --
honestly, and in a partition nobody reads.

WHAT IT ASSERTS. For every `results/*.json` named as a source in
paper_numbers.json: some script writes it (detected at a json.dump or an
open(...,"w")), and reproduce.sh invokes that script.

Writes results/pipeline_coverage.json.
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402

OUT = "pipeline_coverage.json"

# Artifacts that must NOT have a stage, each with the reason. Deliberately short.
EXEMPT = {
    "verify_reproduction.json":
        "written by the clean-clone comparison itself, which runs from the "
        "repository root against a finished clone. A stage inside the pipeline "
        "would compare a tree against itself.",
    "compile_paper.json":
        "written by the LaTeX compile, which is stage 26; its declared output is "
        "the PDF rather than this artifact.",
}


READ_CUE = re.compile(r"(json\.load|\bJ\(|_art\(|\bart\()\s*\(?[^)]{0,60}$")


def writers():
    """script -> {artifacts it writes}.

    Three things this has to get right, and the first two versions did not.

    A script's output filename is usually a MODULE CONSTANT -- `OUT =
    "appendix_g_rules.json"` -- and the write is
    `json.dump(..., open(os.path.join(R.RESULTS, OUT), "w"))`, so the literal is
    nowhere near the write call. Constants are resolved first.

    A script READS other scripts' artifacts, so a bare filename match makes every
    consumer look like a producer. An occurrence immediately preceded by a load
    cue is a read and does not count.

    And a script with no write call at all writes nothing, whatever literals it
    contains.
    """
    out = {}
    for f in sorted(glob.glob("scripts/*.py")) + sorted(glob.glob("src/*.py")):
        name = os.path.basename(f)[:-3]
        txt = open(f).read()
        if not re.search(r'json\.dump\(|open\([^)]*["\']w["\']', txt):
            continue
        # module-level constants holding a .json filename
        consts = {c: v for c, v in re.findall(
            r'^([A-Z_][A-Z0-9_]*)\s*=\s*["\'](\w[\w.-]*\.json)["\']', txt, re.M)}
        written = set()
        # a constant used inside a write call
        for m in re.finditer(r'json\.dump\(|open\([^)]*["\']w["\']', txt):
            seg = txt[max(0, m.start() - 400):m.start() + 400]
            for c, v in consts.items():
                if re.search(r"\b" + c + r"\b", seg):
                    written.add(v)
            for a in re.findall(r'["\'](\w[\w.-]*\.json)["\']', seg):
                written.add(a)
        # ...and any literal in the file that is not exclusively a read
        for m in re.finditer(r'["\'](\w[\w.-]*\.json)["\']', txt):
            a = m.group(1)
            if a in written:
                continue
            before = txt[max(0, m.start() - 60):m.start()]
            if not READ_CUE.search(before):
                written.add(a)
        # Filenames BUILT rather than written literally: `f"step5_{run}.json"`,
        # `f"step4_4_overfit{args.tag}.json"`. The training stages produce one
        # artifact per run and their names exist only at runtime, so a literal
        # match finds nothing and the artifact looks orphaned. The literal PREFIX
        # before the first interpolation is recorded, and an artifact starting
        # with it counts as written by this script.
        for m in re.finditer(r'f["\']([\w.-]*?)\{', txt):
            pre = m.group(1)
            if len(pre) >= 6:
                written.add("prefix:" + pre)
        out[name] = written
    return out


def main():
    N = json.load(open(os.path.join(R.RESULTS, "paper_numbers.json")))
    srcs = {}
    for k, v in N.items():
        for s in re.findall(r"results/([\w./*-]+\.json)", str(v["source"])):
            if "*" not in s:
                srcs.setdefault(os.path.basename(s), []).append(k)

    rep = open("reproduce.sh").read()
    invoked = set(re.findall(r"scripts/(\w+)\.py", rep)) | set(
        re.findall(r"src/(\w+)\.py", rep))
    W = writers()
    by_artifact = {}
    for script, arts in W.items():
        for a in arts:
            by_artifact.setdefault(a, set()).add(script)

    rows, uncovered = [], []
    prefixes = {}
    for script, arts in W.items():
        for a in arts:
            if a.startswith("prefix:"):
                prefixes.setdefault(a[7:], set()).add(script)

    for a, keys in sorted(srcs.items(), key=lambda x: -len(x[1])):
        ws = set(by_artifact.get(a, set()))
        for pre, scripts in prefixes.items():
            if a.startswith(pre):
                ws |= scripts
        ws = {w for w in ws if not w.startswith("prefix:")}
        covered = bool(ws & invoked) or a in EXEMPT
        rows.append({"artifact": a, "n_paper_keys": len(keys),
                     "writers": sorted(ws), "invoked_writers": sorted(ws & invoked),
                     "covered": covered,
                     "exempt_reason": EXEMPT.get(a)})
        if not covered:
            uncovered.append(rows[-1])

    print("PIPELINE COVERAGE — every artifact the paper reads has a stage that writes it")
    print("=" * 96)
    print(f"  artifacts feeding paper_numbers.json : {len(rows)}")
    print(f"  paper keys they supply               : {sum(len(v) for v in srcs.values())}")
    print(f"  exempt, with a stated reason         : {len(EXEMPT)}")
    if uncovered:
        print(f"\n  {len(uncovered)} NOT WRITTEN BY ANY SCRIPT reproduce.sh RUNS:")
        for u in uncovered:
            print(f"    !! {u['artifact']:<38} {u['n_paper_keys']:>4} keys  "
                  f"writers {u['writers'] or 'none detected'}")
        print("\n  A clean clone carries these in and every check passes. The")
        print("  reproduction figure reports them as copied, not regenerated.")
    else:
        print("\n  every artifact has a writer the pipeline invokes")

    rec = {"n_artifacts": len(rows),
           "n_paper_keys": sum(len(v) for v in srcs.values()),
           "n_uncovered": len(uncovered), "uncovered": uncovered,
           "exempt": EXEMPT, "artifacts": rows}
    json.dump(rec, open(os.path.join(R.RESULTS, OUT), "w"), indent=2)
    print(f"  wrote results/{OUT}")
    return 1 if uncovered else 0


if __name__ == "__main__":
    sys.exit(main())
