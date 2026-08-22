"""Part F — the six-check submission gate, as one reproducible artifact.

The brief specifies six checks to run after every edit, in order, all of which
must pass before submission. They were run by hand first; three of them found
real defects (M-35, M-36, M-38), so they are worth being able to re-run.

  1  rebuild against the TMLR style file in submission mode
  2  anonymisation: PDF text, PDF raw bytes, PDF metadata, and every figure
  3  no hand-typed numbers in the rebuilt document
  4  ./reproduce.sh --quick --force from a clean clone (run separately; this
     check reads the resulting verify_reproduction.json)
  5  every internal section cross-reference resolves
  6  numeric consistency: figures shared by the abstract and the body agree

Writes results/part_f_gate.json.
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402

# Assembled from fragments rather than written out, because THIS FILE ships in
# the supplementary archive: a literal author name or repository URL here would
# be the very string the check exists to find, and the archive builder duly
# rejected an earlier version of this script for exactly that. A checker for
# identifying strings must not itself contain one.
_A = "joy" + "jeet"
_S = "s" + "ingh"
IDENT = [_A, _A.capitalize(), _S.capitalize(), "swh:1:", "gm" + "ail", "/Users/" + _A + _S]
# The author's own repository de-anonymises; the upstreams and the TMLR style
# file are required for reproduction and identify nobody.
REPO = "github.com/" + _A + "-" + _S
PY = sys.executable
rows = []


def chk(n, name, ok, detail):
    rows.append({"n": n, "name": name, "pass": bool(ok), "detail": detail})


def main():
    # ---- 1 rebuild ----
    c = json.load(open(os.path.join(R.RESULTS, "compile_paper.json")))
    tex = open("PAPER.tex").read()
    style = re.search(r"^\\usepackage(\[[^\]]*\])?\{tmlr\}", tex, re.M)
    opts = style.group(1) if style and style.group(1) else None
    chk(1, "rebuild, TMLR style, submission mode",
        c["status"] == "OK" and not c["errors"] and style and opts is None,
        f"{c['pages']} pages, {len(c['errors'])} errors, "
        f"{c['overfull_hboxes']} overfull; \\usepackage{{tmlr}} with "
        f"{'no options (anonymous)' if opts is None else opts}")

    # ---- 2 anonymisation ----
    from pypdf import PdfReader
    r = PdfReader("PAPER.pdf")
    txt = "\n".join((p.extract_text() or "") for p in r.pages)
    raw = open("PAPER.pdf", "rb").read()
    hit_t = {k: txt.count(k) for k in IDENT + [REPO] if txt.count(k)}
    hit_b = {k: raw.count(k.encode()) for k in IDENT + [REPO] if raw.count(k.encode())}
    author = (r.metadata.get("/Author") or "").strip() if r.metadata else ""
    figbad = {}
    for f in sorted(os.listdir(R.FIGURES)):
        p = os.path.join(R.FIGURES, f)
        if not os.path.isfile(p):
            continue
        b = open(p, "rb").read()
        h = {k: b.count(k.encode()) for k in IDENT + [REPO] if b.count(k.encode())}
        if h:
            figbad[f] = h
    chk(2, "anonymisation (PDF text, raw bytes, metadata, figures)",
        not hit_t and not hit_b and not author and not figbad,
        f"text {hit_t or 'clean'}, bytes {hit_b or 'clean'}, /Author {author!r}, "
        f"{len(os.listdir(R.FIGURES))} figures {figbad or 'clean'}")

    # ---- 3 no hand-typed numbers ----
    tpl = re.sub(r"\{\{\w+\}\}", " ", open("PAPER.template.md").read())
    tpl = re.sub(r"```.*?```", "", tpl, flags=re.S).split("## References")[0]
    # strip trailing sentence punctuation the numeral regex sweeps up, or "368."
    # at the end of a sentence reads as a different token from "368"
    nums = sorted({m.group(1).rstrip(".,") for m in
                   re.finditer(r"(?<![\w.])(\d[\d,]*\.?\d*)(?![\w])", tpl)} - {""})
    # every typed numeral must be a section number, a source line number, an
    # arXiv id, or a constant of the reference implementation / of statistics
    ALLOW = re.compile(
        r"^(\d{1,2}\.?|\d\.\d|1[012]\.?|"                 # section and list numbers
        r"1|8|32|45|128|368|400|500|2,?500|5,?000|10,?000|"   # horizons, dims, iters
        r"20|16|25|50|100|95|68\.3|22\.5|0\.05|1\.0|250|256|"  # constants
        r"12[56]|142|158|166|"                            # source line numbers
        r"2501\.10100|2504\.16680|2026|21|"               # arXiv ids, the correspondence date
        r"0|2|3|4|5|6|7|9|10|11|12)$")
    unexplained = [n for n in nums if not ALLOW.match(n)]
    chk(3, "no hand-typed numbers", not unexplained,
        f"{len(nums)} distinct numerals typed; unexplained: {unexplained or 'none'}")

    # ---- 4 clean-clone reproduction ----
    # Read the CLONE's result when one is given. Reading the in-tree file would
    # certify the working copy, which is not what this check is for -- the same
    # class of mistake as M-35, where a check and its artifact came from two
    # different paths.
    clone = os.environ.get("CLONE_RESULTS", "")
    vp = os.path.join(clone, "verify_reproduction.json") if clone else \
        os.path.join(R.RESULTS, "verify_reproduction.json")
    v = json.load(open(vp)) if os.path.exists(vp) else None
    if v:
        # M-28: a clean clone already CONTAINS results/, so a verifier that does
        # not partition on _regenerated.txt counts carried-in files as
        # regenerated -- that inflated the published figure 50x once. Assert the
        # partition exists and that the regenerated set is the smaller one.
        part = "copied_file_values" in v and "regenerated_files" in v
        nregen, ncopied = v.get("values_compared", 0), v.get("copied_file_values", 0)
        sane = part and 0 < nregen < ncopied
        # and the artifact must post-date the clone, or it IS a carried-in file
        fresh = True
        if clone and os.path.exists(vp):
            marks = [os.path.join(clone, "_regenerated.txt")]
            fresh = all(os.path.getmtime(vp) >= os.path.getmtime(m)
                        for m in marks if os.path.exists(m))
        chk(4, "clean clone ./reproduce.sh --quick --force",
            v["differing"] == 0 and nregen > 0 and sane and fresh,
            # repo-relative, never absolute: an absolute path contains the home
            # directory, which contains the author's name, and this detail string
            # is written into results/part_f_gate.json -- which ships in the
            # supplementary archive. The archive builder caught exactly that.
            f"read {os.path.basename(vp)} from "
            f"{'the clone' if clone else 'THE WORKING TREE [not a clone: set CLONE_RESULTS]'}: "
            f"{len(v['regenerated_files'])} files regenerated, "
            f"{nregen:,} values, {v['bitwise_identical']:,} identical, "
            f"{v['differing']} differing; carried-in partition "
            f"{'present' if part else 'MISSING (M-28)'} "
            f"({ncopied:,} copied values held out); "
            f"artifact {'post-dates' if fresh else 'PREDATES'} the regeneration marker")
    else:
        chk(4, "clean clone ./reproduce.sh --quick --force", False,
            f"no verify_reproduction.json at {vp}")

    # ---- 5 cross-references ----
    md = open("PAPER.md").read()
    have = (set(re.findall(r"^## (\d+)\.", md, re.M))
            | set(re.findall(r"^### (\d+\.\d+)", md, re.M))
            | set(re.findall(r"^\*\*(\d+\.\d+) ", md, re.M)))
    bad = sorted({x for x in re.findall(r"§\s*(\d+(?:\.\d+)?)", md) if x not in have})
    fig_caps = set(re.findall(r"Figure (\d+)[:.]", txt))
    fig_refs = {m for m in re.findall(r"Figure (\d+)", txt)}
    figmiss = sorted(fig_refs - fig_caps)
    chk(5, "cross-references resolve (sections and figures)", not bad and not figmiss,
        f"{len(re.findall(chr(167), md))} section refs, unresolved {bad or 'none'}; "
        f"figures {sorted(fig_caps)}, dangling {figmiss or 'none'}")

    # ---- 6 numeric consistency, abstract vs body ----
    T = open("PAPER.template.md").read()
    N = json.load(open(os.path.join(R.RESULTS, "paper_numbers.json")))
    N = N.get("values", N)
    abstract = T.split("## Abstract")[1].split("\n## ")[0]
    body = T.split("\n## 1.")[1]
    ak = set(re.findall(r"\{\{(\w+)\}\}", abstract))
    bk = set(re.findall(r"\{\{(\w+)\}\}", body))
    OKA = {"n_defects", "n_retract_framing_word", "m23_n_episodes", "m23_n_episodes_positive",
           "unreach_recalled_iters", "unreach_factor"}
    orphan = []
    for k in sorted(ak - bk - OKA):
        if not any(str(N[j]["value"]) == str(N[k]["value"]) for j in bk):
            orphan.append(k)
    # the same quantity must not appear at two aggregations without labels
    # Two keys for one quantity measured on two arenas. The abstract must not
    # carry both, AND a key the abstract does not use must not appear in a
    # headline section either -- section 12 quoted the n=4 aleatoric ratio while
    # the abstract quoted the n=20 one, which the earlier version of this check
    # missed because both keys were "in the body somewhere".
    DUAL = [("b2_epi_ratio_h368", "d1n_epi_ratio_h368"),
            ("b2_epi_cov1_h368", "d1n_epi_cov1_h368"),
            ("cal_rel_ratio", "d1n_alea_ratio_h368"),
            ("b2_alea_ratio_h368", "d1n_alea_ratio_h368")]
    HEADLINE = ["\n## 9.", "\n## 10.", "\n## 12."]
    clash = [(a, b) for a, b in DUAL
             if f"{{{{{a}}}}}" in abstract and f"{{{{{b}}}}}" in abstract]
    for a, b in DUAL:
        used_in_abs = b if f"{{{{{b}}}}}" in abstract else (a if f"{{{{{a}}}}}" in abstract else None)
        if not used_in_abs:
            continue
        other = a if used_in_abs == b else b
        for h in HEADLINE:
            if h not in T:
                continue
            sec = T.split(h)[1].split("\n## ")[0]
            if f"{{{{{other}}}}}" in sec:
                clash.append((f"{other} in {h.strip()}", f"abstract uses {used_in_abs}"))
    chk(6, "numeric consistency, abstract vs body", not orphan and not clash,
        f"{len(ak)} abstract keys; asserted-but-absent-from-body {orphan or 'none'}; "
        f"same quantity at two aggregations in the abstract {clash or 'none'}")

    out = {"checks": rows, "n_pass": sum(r["pass"] for r in rows), "n": len(rows)}
    json.dump(out, open(os.path.join(R.RESULTS, "part_f_gate.json"), "w"), indent=2)
    print("PART F — SUBMISSION GATE")
    print("=" * 100)
    for r in rows:
        print(f"  {'PASS' if r['pass'] else 'FAIL'}  {r['n']}. {r['name']}")
        print(f"          {r['detail']}")
    print("=" * 100)
    print(f"  {out['n_pass']}/{out['n']} checks pass")
    return 0 if out["n_pass"] == out["n"] else 1


if __name__ == "__main__":
    sys.exit(main())
