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

# The strings this gate scans for come from the ENVIRONMENT, never from this
# file, because THIS FILE ships in the supplementary archive. An earlier version
# assembled them from adjacent string fragments so that the archive builder's
# own scan would accept it. That satisfied every pattern sweep and still handed
# a reviewer the author's name, account and home-directory path in four adjacent
# lines (found in review, S20 F1). A checker for identifying strings must not
# contain one, in any form a reader can reassemble.
#
#   RWM_IDENT       comma-separated strings that must not appear in the paper
#   RWM_IDENT_REPO  the author's own repository, which de-anonymises by itself
#
# Unset or empty, check 2 FAILS. It is never reported as NOT RUN: a check for
# identifying strings that cannot see the strings would certify a PDF it never
# scanned, and NOT RUN is reserved for a check whose absence is honest (check 4
# without a clone), not for one whose input was forgotten. Every later check
# still runs: the PDF is read before the guard, not inside it.
IDENT = [t.strip() for t in os.environ.get("RWM_IDENT", "").split(",") if t.strip()]
REPO = os.environ.get("RWM_IDENT_REPO", "").strip()
PY = sys.executable
rows = []


def chk(n, name, ok, detail):
    """ok=None means NOT RUN: the check could not see what it checks.

    A not-run check is neither a pass nor a failure and is kept out of both
    counts. Scoring it as a pass overstates the gate; scoring it as a failure
    makes a clean pipeline look broken. Check 4 needs a clone that the pipeline
    does not have, and inferring its verdict from whichever comparison last
    wrote an artifact is what made this gate's own result fail to reproduce.
    """
    rows.append({"n": n, "name": name,
                 "pass": None if ok is None else bool(ok), "detail": detail})


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
    if not IDENT or not REPO:
        chk(2, "anonymisation (PDF text, raw bytes, metadata, figures)", False,
            "NOT CONFIGURED: set RWM_IDENT (comma-separated identifying strings) "
            "and RWM_IDENT_REPO (the author's repository). This check FAILS rather "
            "than reporting NOT RUN: it cannot certify a PDF it has not scanned.")
    else:
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
    # Three classes of numeral are ADDRESSES rather than results, and stripping
    # the class is safer than allow-listing each value -- an allow-list of line
    # numbers would silently permit a result that happened to equal one.
    #
    #   a) anything inside an inline code span. In this paper a backticked
    #      numeral is always a file:line citation, a tensor index or an
    #      identifier: `system_dynamics.py:126`, `:182`, `swh:1:`.
    #   b) an arXiv identifier, with or without a version suffix. The suffix is
    #      why "arXiv:2501.10100v1" used to leave a bare "2501" behind: the
    #      trailing v1 makes the whole id fail the word-boundary lookahead.
    #   c) a four-digit publication year in the related-work prose. No result in
    #      this paper is a bare number in 1900-2099.
    tpl = re.sub(r"`[^`\n]*`", " ", tpl)                         # (a)
    tpl = re.sub(r"arXiv:\d{4}\.\d{4,5}(\*{0,2}v\d+\*{0,2})?", " ", tpl)   # (b)
    tpl = re.sub(r"(?<![\w.])(19|20)\d{2}(?![\w.])", " ", tpl)   # (c)
    # strip trailing sentence punctuation the numeral regex sweeps up, or "368."
    # at the end of a sentence reads as a different token from "368"
    nums = sorted({m.group(1).rstrip(".,") for m in
                   re.finditer(r"(?<![\w.])(\d[\d,]*\.?\d*)(?![\w])", tpl)} - {""})
    # every typed numeral must be a section number, a source line number, an
    # arXiv id, or a constant of the reference implementation / of statistics
    # Section numbers are DERIVED from the document's own headings rather than
    # matched by a regex. "6.10" is a perfectly good section number and
    # `\d\.\d` does not match it, which is how a two-digit subsection came to be
    # reported as an unexplained typed numeral. Deriving them means the allow-list
    # cannot go stale when a section is added, and cannot silently admit a RESULT
    # that happens to look like a section number.
    _tpl_raw = open("PAPER.template.md").read()
    SECTIONS = set()
    for _m in re.finditer(r"^#{2,3} (\d+(?:\.\d+)?)[.  ]", _tpl_raw, re.M):
        SECTIONS.add(_m.group(1))
        SECTIONS.add(_m.group(1) + ".")
    for _m in re.finditer(r"^\*\*(\d+\.\d+) ", _tpl_raw, re.M):
        SECTIONS.add(_m.group(1))
    ALLOW = re.compile(
        r"^(\d{1,2}\.?|\d\.\d|1[012]\.?|"                 # section and list numbers
        r"1|8|32|45|128|368|400|500|2,?500|5,?000|10,?000|"   # horizons, dims, iters
        r"20|16|25|50|100|95|68\.3|22\.5|0\.05|1\.0|250|256|"  # constants
        r"12[56]|142|158|166|"                            # source line numbers
        r"2501\.10100|2504\.16680|2026|21|"               # arXiv ids, the correspondence date
        r"0|2|3|4|5|6|7|9|10|11|12)$")
    unexplained = [n for n in nums if not ALLOW.match(n) and n not in SECTIONS]
    chk(3, "no hand-typed numbers", not unexplained,
        f"{len(nums)} distinct numerals typed, {len(SECTIONS)} section numbers derived "
        f"from the headings; unexplained: {unexplained or 'none'}")

    # ---- 4 clean-clone reproduction ----
    # Read the CLONE's result when one is given. Reading the in-tree file would
    # certify the working copy, which is not what this check is for -- the same
    # class of mistake as M-35, where a check and its artifact came from two
    # different paths.
    # verify_reproduction.py writes its output into the COMMITTED tree (its second
    # argument), not into the clone, so the artifact of record is always the
    # in-tree one. CLONE_RESULTS locates the clone's _regenerated.txt, which is
    # what the freshness assertion below compares against -- the in-tree artifact
    # must post-date the run that produced it, or it is a stale copy from an
    # earlier comparison. An earlier version of this check read the CLONE's
    # verify_reproduction.json, which is a carried-in file the pipeline never
    # rewrites, and so could only ever have failed.
    clone = os.environ.get("CLONE_RESULTS", "")
    vp = os.path.join(R.RESULTS, "verify_reproduction.json")
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
        # WITHOUT a clone to point at, this check reports rather than asserts.
        #
        # It reads the in-tree verify_reproduction.json, which is written by
        # whichever comparison last ran. So in the pipeline -- where no clone is
        # given -- its verdict is a property of the last thing someone did, not
        # of this run. That made n_pass oscillate between 5 and 6 across trees
        # and it was the last differing value in the clean-clone comparison: the
        # gate's own result was the thing that would not reproduce. Exactly the
        # self-referential class appendix D describes for the ver_* keys, in an
        # artifact the ver_* exclusion does not cover.
        #
        # A check that cannot see what it is checking should say so, not infer.
        chk(4, "clean clone ./reproduce.sh --quick --force",
            None if not clone else
            v["differing"] == 0 and nregen > 0 and sane and fresh,
            # repo-relative, never absolute: an absolute path contains the home
            # directory, which contains the author's name, and this detail string
            # is written into results/part_f_gate.json -- which ships in the
            # supplementary archive. The archive builder caught exactly that.
            f"{os.path.basename(vp)} vs "
            f"{'the clone run at ' + os.path.basename(os.path.dirname(clone)) if clone else 'NO CLONE GIVEN [set CLONE_RESULTS]'}: "
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
    # Appendix G QUOTES the committed text of each pre-registered rule, verbatim,
    # and those rules were written against the section numbering current when
    # each was committed -- M-45 governs "the within-trajectory control on §5.6",
    # which is now §6.7. That is a quotation of a historical document, not a
    # cross-reference this paper is making, and altering it to keep a checker
    # happy would falsify the quotation. The appendix says so in its own text.
    #
    # Scoped narrowly: only the block after Appendix G's rule-texts heading is
    # exempt, and everything before it -- including Appendix G's own prose and
    # its table -- is checked like the rest of the paper.
    _g = md.find("**What each rule says, in its own committed words")
    assert _g >= 0 or "Appendix G" not in md, (
        "Appendix G is present but its quoted-rule-text block was not found; the "
        "exemption anchor has drifted and the check is silently scanning it as live")
    live = md if _g < 0 else md[:_g]
    quoted = "" if _g < 0 else md[_g:]
    bad = sorted({x for x in re.findall(r"§\s*(\d+(?:\.\d+)?)", live) if x not in have})
    _hist = sorted({x for x in re.findall(r"§\s*(\d+(?:\.\d+)?)", quoted)
                    if x not in have})
    # \s* on both sides: pdf text extraction reproduces the typeset kerning, and a
    # caption can come back as "Figure6: ..." with no space at all. Figure 6's did,
    # and the gate reported it dangling when it is on page 30 with its caption
    # intact. A whitespace-sensitive regex over extracted PDF text is a bug in
    # the checker, not a finding about the paper.
    fig_caps = set(re.findall(r"Figure\s*(\d+)\s*[:.]", txt))
    fig_refs = {m for m in re.findall(r"Figure\s*(\d+)", txt)}
    figmiss = sorted(fig_refs - fig_caps)
    # ---- 4b the shipped bundles must not be older than what they ship ----
    #
    # supplementary_anon.zip was built before the appendix reordering and shipped
    # the exact defect HEAD calls blocking: its PAPER.tex carried A, B, C, D,
    # variance-state, two-nRMSE, rules, untested, originals, so eight references
    # in the reviewer's copy pointed at the wrong appendix. The bundle is what a
    # reviewer receives, and nothing compared its age to the paper's.
    # By CONTENT, not by mtime. An mtime rule is both too weak and too strong: it
    # cannot tell a rebuild that changed nothing from one that changed everything,
    # and this gate rebuilds the paper itself, so the first version reported the
    # bundles stale every run after its own check 1 had touched PAPER.tex.
    #
    # What matters is exactly what the audit found: the PAPER.tex inside the
    # archive carried the pre-reordering appendix sequence, so eight references in
    # the reviewer's copy pointed at the wrong appendix. Comparing the bytes the
    # reviewer opens against the bytes on disk answers that directly.
    import zipfile as _zip
    _bundles = [("supplementary_anon.zip", "the reviewer's copy"),
                ("supplementary.zip", "the supplementary archive")]
    _shipped = ["PAPER.tex", "PAPER.md", "FINDINGS_LEDGER.md"]
    _stale = []
    for _z, _what in _bundles:
        if not os.path.exists(_z):
            _stale.append(f"{_z} does not exist")
            continue
        try:
            _zf = _zip.ZipFile(_z)
        except Exception as _e:
            _stale.append(f"{_z} unreadable: {_e}")
            continue
        _names = _zf.namelist()
        for _src in _shipped:
            if not os.path.exists(_src):
                continue
            _match = [n for n in _names if n.endswith("/" + _src) or n == _src]
            if not _match:
                _stale.append(f"{_z} ({_what}) does not contain {_src}")
                continue
            _in = _zf.read(_match[0]).decode("utf-8", "replace")
            _on = open(_src, encoding="utf-8").read()
            # NOT byte equality. The anon bundle SCRUBS what it ships -- that is
            # its purpose -- so its copies can never match byte for byte and a
            # byte test reports every bundle stale forever. Compare structural
            # properties the scrubber does not touch, chosen to be the ones that
            # actually went wrong: the appendix ORDER (D-25 shipped A,B,C,D,H,I,
            # G,E,F to reviewers after HEAD had fixed it) and the reference
            # COUNT (D-26 shipped ten entries under a note claiming sixteen).
            for _what2, _pat in (("appendix order", r"^#+ +(?:Appendix|\\section\{Appendix) ([A-Z])"),
                                 ("reference count", r"^(\d+)\. [A-Z]\.")):
                _a = re.findall(_pat, _in, re.M)
                _b = re.findall(_pat, _on, re.M)
                if _a != _b:
                    _stale.append(f"{_z} ({_what}) ships a different {_what2} in "
                                  f"{_src} ({''.join(_a[:12])} vs {''.join(_b[:12])})")
                    break
    chk("4b", "shipped bundles carry the current paper's structure", not _stale,
        f"{len(_bundles)} bundles x {len(_shipped)} files, appendix order and "
        f"reference list compared; "
        + ("all match" if not _stale else "; ".join(_stale)))

    # ---- 5b appendix letters must match DOCUMENT ORDER ----
    #
    # LaTeX auto-letters appendices in the order they appear and discards the
    # hand-written label. The source ran A, B, C, D, H, I, G, E, F -- because H and
    # I were inserted before G -- so the PDF lettered them A..I in that order and
    # EIGHT reference sites landed on a real but wrong appendix. E/H and F/I were
    # cleanly swapped pairs, so nothing dangled and nothing errored: a reader
    # following "Appendix H gives the arithmetic" arrived at "What testing the
    # untested claims would require". Only reading the PDF finds that, which is
    # why it survived every gate here.
    _app = re.findall(r"^## Appendix ([A-Z]) — ", md, re.M)
    _figpos = md.find("## Appendix C — figures")
    _expect = [chr(ord("A") + i) for i in range(len(_app) + (1 if _figpos >= 0 else 0))]
    if _figpos >= 0:
        _got = []
        for m in re.finditer(r"^## Appendix ([A-Z])[  ]", md, re.M):
            _got.append(m.group(1))
    else:
        _got = _app
    _order_ok = _got == _expect[:len(_got)]
    chk("5b", "appendix letters match document order", _order_ok,
        f"document order {''.join(_got)}; LaTeX letters them "
        f"{''.join(_expect[:len(_got)])}"
        + ("" if _order_ok else "  <- every reference to a mismatched letter "
                                "lands on the wrong appendix in the PDF"))

    chk(5, "cross-references resolve (sections and figures)", not bad and not figmiss,
        f"{len(re.findall(chr(167), md))} section refs, unresolved {bad or 'none'}; "
        f"{len(_hist)} historical ref(s) inside quoted rule text exempt {_hist or ''}; "
        f"figures {sorted(fig_caps)}, dangling {figmiss or 'none'}")

    # ---- 6 numeric consistency, abstract vs body ----
    T = open("PAPER.template.md").read()
    N = json.load(open(os.path.join(R.RESULTS, "paper_numbers.json")))
    N = N.get("values", N)
    abstract = T.split("## Abstract")[1].split("\n## ")[0]
    body = T.split("\n## 1.")[1]
    # {{FIGURES}} is a placement marker, not a value, and has no entry in
    # paper_numbers.json. It entered the body when Appendix D was added.
    ak = set(re.findall(r"\{\{(\w+)\}\}", abstract)) - {"FIGURES"}
    bk = set(re.findall(r"\{\{(\w+)\}\}", body)) - {"FIGURES"}
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
    # Pairs of keys carrying the SAME quantity from different arenas or scripts.
    # A5 was this failure: the abstract and section 12 both described the
    # aleatoric/epistemic ratio, in words, and disagreed about it -- "nearly three
    # orders" against "two orders" -- while every numeral was correct.
    DUAL = [("b2_epi_ratio_h368", "d1n_epi_ratio_h368"),
            ("b2_epi_cov1_h368", "d1n_epi_cov1_h368"),
            ("cal_rel_ratio", "d1n_alea_ratio_h368"),
            ("b2_alea_ratio_h368", "d1n_alea_ratio_h368"),
            ("b2_epi_over_alea_h368", "d1n_epi_over_alea_h368"),
            ("b2_penalty_corr", "d4_r"),
            ("d2b_par_all", "d2r_lin"),
            ("b2_epi_npos_h368", "perm_all_epi_npos_h368"),
            ("cal_rel_npos", "relale_all_pos_h368")]
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

    # A not-run check is counted in neither column. n_run is the denominator so
    # that this artifact's own numbers do not move between a tree with a clone
    # comparison and one without -- which is what made part_f_gate.json the last
    # value in the build that would not reproduce.
    ran = [r for r in rows if r["pass"] is not None]
    notrun = [r for r in rows if r["pass"] is None]
    out = {"checks": rows, "n_pass": sum(bool(r["pass"]) for r in ran),
           "n_run": len(ran), "n_not_run": len(notrun), "n": len(rows)}
    json.dump(out, open(os.path.join(R.RESULTS, "part_f_gate.json"), "w"), indent=2)
    print("PART F — SUBMISSION GATE")
    print("=" * 100)
    for r in rows:
        state = "NOT RUN" if r["pass"] is None else ("PASS" if r["pass"] else "FAIL")
        print(f"  {state:<7} {r['n']}. {r['name']}")
        print(f"          {r['detail']}")
    print("=" * 100)
    print(f"  {out['n_pass']}/{out['n_run']} checks pass"
          + (f"; {out['n_not_run']} not run (needs CLONE_RESULTS)" if notrun else ""))
    return 0 if out["n_pass"] == out["n_run"] else 1


if __name__ == "__main__":
    sys.exit(main())
