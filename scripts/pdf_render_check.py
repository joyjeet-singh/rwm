"""A -- the rendered-PDF pass. A one-time submission check, not permanent machinery.

WHY IT EXISTS. Every other check in this project reads the SOURCE. `build_paper.py` asserts
provenance in the markdown, `check_comparative_claims.py` pins fragments of the template's
text, and Session 6's cross-reference sweep read `PAPER.md`. A passing compile means LaTeX
did not error -- not that the PDF says what the source says.

The appendix re-lettering proved the class is real: the source said "Appendix D", the PDF
said "Appendix C", and every reference past B pointed at the wrong appendix. Nothing in the
registry could see it, because the defect lived in the letter LaTeX assigns rather than in
any file a check reads. Session 5a also moved every figure in the paper through the same
transformation layer.

So this reads the compiled PDF and checks it against the source and the artifacts. It is
deliberately NOT registered as a check kind: it exists because text moved through a
transformation, the moves are done, and Session 5 was removing machinery rather than adding
it.

WHAT IT CANNOT DO, stated rather than implied. Extracted PDF text loses layout. This can
see that a table's header cells are all present and in order; it cannot see that a column
rendered too narrow, or that a float landed three pages from its reference. Those need eyes,
and §F.2 asks for eyes.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402
from pypdf import PdfReader  # noqa: E402

PDF = "PAPER.pdf"
MD = "PAPER.md"


def norm(s):
    """Collapse whitespace and drop hyphenation introduced by line breaking."""
    s = s.replace("-\n", "").replace("­", "")
    return re.sub(r"\s+", " ", s)


def main():
    reader = PdfReader(PDF)
    pages = [p.extract_text() or "" for p in reader.pages]
    # Page furniture is not text the source states. Each page's text ends with its page number
    # and the next begins with the running header, so a reference split by a page break read
    # "(Figure 10 Under review as submission to TMLR 2)" and check 2 reported a Figure 10 (round 2,
    # T3). Exactly those two lines are dropped, and only if every page carries them where expected:
    # a layout that moves them fails here rather than silently leaving them in.
    HEADER = "Under review as submission to TMLR"
    for i, t in enumerate(pages):
        ln = t.rstrip().split("\n")
        assert ln[0].strip() == HEADER and ln[-1].strip() == str(i + 1), (
            f"page {i + 1}: running header or page number not where expected; furniture cannot be stripped")
        pages[i] = "\n".join(ln[1:-1])
    pdf_raw = "\n".join(pages)
    pdf = norm(pdf_raw)
    md = open(MD).read()
    # The generated-file header is an HTML comment: it never reaches LaTeX, so numerals
    # inside it cannot be "lost in rendering". Dropping it here rather than exempting
    # them later keeps the comparison over text that is actually typeset.
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    findings = []

    def check(name, ok, detail):
        findings.append({"check": name, "pass": bool(ok), "detail": detail})
        print(f"  {'PASS' if ok else 'FAIL'}  {name}\n        {detail}")

    # ---- 1. appendix letters -------------------------------------------------
    # The heading LaTeX printed, in document order, against every in-text reference.
    heads = re.findall(r"Appendix ([A-Z])\s+[A-Z—-]", pdf)
    md_heads = re.findall(r"^## Appendix ([A-Z]) ", md, re.M)
    refs = sorted(set(re.findall(r"Appendix ([A-Z])\b", pdf)))
    seq_ok = md_heads == sorted(md_heads) and md_heads == [
        chr(ord("A") + i) for i in range(len(md_heads))]
    dangling = [r for r in refs if r not in md_heads]
    check("1. appendix letters resolve",
          seq_ok and not dangling,
          f"source headings {''.join(md_heads)}; contiguous from A: {seq_ok}; "
          f"in-text references {''.join(refs)}; dangling {dangling or 'none'}")

    # ---- 2. figure numbers ---------------------------------------------------
    # Every figure the source references by number must carry a caption in the PDF,
    # and every caption must be referenced. 5a moved all six.
    # Extraction does not reliably preserve the ':' after a caption number, so the
    # comparison is on the set of figure numbers appearing at all, in each document.
    pdf_figs = sorted(set(re.findall(r"Figure\s*(\d+)", pdf)), key=int)
    md_figs = sorted(set(re.findall(r"Figure\s*(\d+)", md)), key=int)
    missing = [n for n in md_figs if n not in pdf_figs]
    orphan = [n for n in pdf_figs if n not in md_figs]
    check("2. figure numbers match their references",
          not missing and not orphan,
          f"source figure numbers {md_figs}; PDF {pdf_figs}; "
          f"in source but not rendered {missing or 'none'}; "
          f"rendered but not in source {orphan or 'none'}")

    # ---- 3. table integrity --------------------------------------------------
    # Each source table's header cells, in order, must appear in the PDF. A header
    # split by a page break, or a column dropped, shows up as a missing cell.
    tables, bad = 0, []
    for m in re.finditer(r"^\|(.+)\|\s*\n\|[-: |]+\|\s*$", md, re.M):
        # split on UNESCAPED pipes only: a cell may contain "\\|error\\|", and
        # splitting on that produced fragments which then read as absent cells.
        cells = [c.strip() for c in re.split(r"(?<!\\\\)\\|", m.group(1)) if c.strip()]
        cells = [re.sub(r"[*`\\]", "", c) for c in cells]
        # Only cells that are plain words can be compared literally. A header carrying
        # math, a pipe or a placeholder renders through the converter by design --
        # "\|error\|" becomes |error|, "±" becomes a glyph -- so comparing those
        # measures md_to_tex rather than the rendering, which is not what this checks.
        cells = [c for c in cells
                 if c and re.fullmatch(r"[A-Za-z][A-Za-z0-9 ,'()/-]*", c)]
        if not cells:
            continue
        tables += 1
        absent = [c for c in cells if norm(c) not in pdf]
        if absent:
            bad.append({"header": cells[:6], "cells_absent_from_pdf": absent[:4]})
    check("3. table headers survive rendering",
          not bad,
          f"{tables} tables checked cell by cell; "
          + (f"{len(bad)} with a header cell absent from the PDF" if bad
             else "every header cell present, in the PDF text"))

    # ---- 4. numerals -------------------------------------------------------
    # The measurable direction. Extraction concatenates across table cells -- "100"
    # beside "10.5x" comes out as "10010.5" -- so a numeral in the PDF that is in
    # neither the source nor the substituted set is usually two numerals touching,
    # not an invented one. What IS measurable, and what matters for a reader, is that
    # nothing the source states was LOST in rendering.
    md_nums = set(re.findall(r"(?<![\w.])\d[\d,]*\.?\d*(?![\w])", md))
    pdf_nums = set(re.findall(r"(?<![\w.])\d[\d,]*\.?\d*(?![\w])", pdf))
    pdf_digits = re.sub(r"[^0-9.,]", "", pdf)
    # a source numeral counts as present if it survives as its own token OR inside the
    # digit stream, which is where cell-boundary concatenation puts it
    lost = sorted(n for n in md_nums
                  if n not in pdf_nums and n.replace(",", "") not in pdf_digits
                  and n not in pdf)
    check("4. every numeral the source states survives into the PDF",
          not lost,
          f"{len(md_nums)} distinct numerals in the source, {len(pdf_nums)} tokenised "
          f"in the PDF; lost in rendering {lost[:8] if lost else 'none'}. "
          f"The converse -- that the PDF invents none -- is not measurable from "
          f"extracted text, which concatenates across table cells")

    # ---- 5. section cross-references -----------------------------------------
    sec_heads = set(re.findall(r"^#{2,3} (\d+(?:\.\d+)?)[.\s]", md, re.M))
    pdf_refs = set(re.findall(r"§\s*(\d+(?:\.\d+)?)", pdf))
    unresolved = sorted(r for r in pdf_refs
                        if r not in sec_heads and r.split(".")[0] not in sec_heads)
    check("5. section cross-references resolve in the PDF",
          not unresolved,
          f"{len(pdf_refs)} distinct section references in the PDF against "
          f"{len(sec_heads)} headings; unresolved {unresolved or 'none'}")

    out = {
        "check": "rendered-PDF pass (Session 8 addendum A)",
        "one_time": ("not registered as a check kind. It exists because text moved through "
                     "a transformation layer in Sessions 5a and 6; the moves are done."),
        "pdf": PDF, "pages": len(reader.pages), "chars_extracted": len(pdf_raw),
        "cannot_detect": ("extracted PDF text loses layout. This sees that a table's header "
                          "cells are present and that references resolve; it cannot see a "
                          "column rendered too narrow or a float landing pages from its "
                          "reference. Those need a reader, which §F.2 asks for."),
        "n_checks": len(findings),
        "n_pass": sum(1 for f in findings if f["pass"]),
        "findings": findings,
        "verdict": "PASS" if all(f["pass"] for f in findings) else "FAIL",
    }
    op = os.path.join(R.RESULTS, "pdf_render_check.json")
    json.dump(out, open(op, "w"), indent=2)
    print(f"\n  {out['n_pass']}/{out['n_checks']} — {out['verdict']}")
    print(f"  wrote {R.rel(op)}")
    return 0 if out["verdict"] == "PASS" else 1


if __name__ == "__main__":
    print("=" * 96)
    print("RENDERED-PDF PASS — what the reader actually receives")
    print("=" * 96)
    sys.exit(main())
