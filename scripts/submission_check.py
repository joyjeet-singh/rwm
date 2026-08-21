"""Submission readiness gate: every 'done' criterion in the hardening brief, checked.

Written after an ad-hoc version of this check produced two false negatives — it
looked for "[accepted]" anywhere in PAPER.tex and found it in a comment warning
against using it, and it grepped the template for a phrase that the template wraps
across a line. Both made a finished item look pending. A gate that cries wolf is
worse than no gate, so the checks here are anchored to structure rather than to
loose substring matches, and each prints what it actually looked at.

Run after any change to the paper. Exits non-zero if anything is outstanding.
"""
import json
import os
import re
import subprocess
import sys
import zipfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402

PDFLATEX = "/Library/TeX/texbin/pdflatex"


def norm(p):
    """Collapse whitespace so a line-wrapped phrase still matches."""
    return re.sub(r"\s+", " ", open(p).read())


def built_pdf_text():
    """Build the paper in a scratch dir and extract its text, or return None."""
    import tempfile, shutil
    if not os.path.exists(PDFLATEX):
        return None
    with tempfile.TemporaryDirectory() as d:
        shutil.copy("PAPER.tex", d)
        for f in os.listdir("tex"):
            if f.endswith((".sty", ".bst")):
                shutil.copy(os.path.join("tex", f), d)
        os.makedirs(os.path.join(d, "figures"), exist_ok=True)
        for f in os.listdir(R.FIGURES):
            if f.startswith("paper_fig"):
                shutil.copy(os.path.join(R.FIGURES, f), os.path.join(d, "figures", f))
        subprocess.run([PDFLATEX, "-interaction=nonstopmode", "PAPER.tex"],
                       cwd=d, capture_output=True)
        pdf = os.path.join(d, "PAPER.pdf")
        if not os.path.exists(pdf):
            return None
        try:
            sys.path.insert(0, "/tmp/pdfvenv/lib/python3.14/site-packages")
            from pypdf import PdfReader
        except Exception:
            return "PYPDF_UNAVAILABLE"
        r = PdfReader(pdf)
        meta = {k: v for k, v in (r.metadata or {}).items()}
        return {"text": "\n".join((p.extract_text() or "") for p in r.pages),
                "meta": meta, "pages": len(r.pages)}


def main():
    tpl = norm("PAPER.template.md")
    tex = open("PAPER.tex").read()
    led = norm("FINDINGS_LEDGER.md")
    rows = []

    def chk(item, ok, detail):
        rows.append((item, bool(ok), detail))

    # A1 -- anonymisation, against the BUILT pdf
    pdf = built_pdf_text()
    if isinstance(pdf, dict):
        ident = ["joyjeet", "Joyjeet", "Singh", "github.com", "swh:1:"]
        hits = {p: pdf["text"].count(p) for p in ident if pdf["text"].count(p)}
        author = (pdf["meta"].get("/Author") or "").strip()
        chk("A1 anonymisation (built PDF text + metadata)", not hits and not author,
            f"{pdf['pages']} pages, text hits {hits or 'none'}, /Author {author!r}")
    else:
        chk("A1 anonymisation", False, f"could not build/read the PDF ({pdf})")

    # A2 -- the usepackage LINE, not any mention of the options
    m = re.search(r"^\\usepackage(\[[^\]]*\])?\{tmlr\}", tex, re.M)
    chk("A2 TMLR style file, submission mode", bool(m) and not (m.group(1) if m else None),
        f"line is {m.group(0)!r}" if m else "no \\usepackage{tmlr} found")

    # A3
    if os.path.exists("supplementary.zip"):
        z = zipfile.ZipFile("supplementary.zip")
        n, sz = len(z.namelist()), os.path.getsize("supplementary.zip")
        chk("A3 supplementary archive", n > 100 and sz < 100e6,
            f"{n} entries, {sz/1e6:.1f} MB, limit 100 MB")
    else:
        chk("A3 supplementary archive", False, "supplementary.zip absent")

    for item, needle, where, src in (
            ("A4 broader impact", "Broader impact", tpl, "template"),
            ("A5 actionable lessons", "Actionable lessons", tpl, "template"),
            ("A6 venue decision recorded", "MLRC 2026 requires", led, "ledger"),
            ("B1 source readings", "### C-14", led, "ledger"),
            ("B3 section 4 retargeted", "Which quantity the method actually uses", tpl, "template"),
            ("D3 hold-last floor in §3", "hold-last floor", tpl, "template"),
            ("E1 originals' claims table", "### O-14", led, "ledger"),
            ("E2 §4.3/§4.5 reconciled", "objective-driven", tpl, "template"),
            ("E3 §5.4 restated", "signature of regularisation", tpl, "template"),
            ("E4 author contact recorded", "wrote to the first author", tpl, "template"),
            ("E5 §6 assumptions enumerated", "if violated", tpl, "template"),
            ("E6 archived before submission", "archived by Software Heritage", tpl, "template"),
            ("E7 excluded artifact named", "step4_5_timing.json", tpl, "template")):
        chk(item, needle in where, f"found in {src}" if needle in where else f"absent from {src}")

    for item, path in (("B2 epistemic measured", "results/task_b2_epistemic.json"),
                       ("C3 multiplicity", "results/task_c3_multiplicity.json"),
                       ("D2 recalibration", "results/task_d2_recalibration.json")):
        chk(item, os.path.exists(path), path)

    # C1 -- no unreviewed claims, and report what is not SUPPORTED
    c1 = json.load(open("results/task_c1_claims_audit.json"))
    by = c1["by_verdict"]
    chk("C1 claims audit complete", by.get("UNREVIEWED", 0) == 0,
        f"{c1['n_claims']} claims: " + ", ".join(f"{k} {v}" for k, v in sorted(by.items())))

    # D1
    want = [f"results/step5_arm{a}_seed{s}_10k.json" for a in "AB" for s in (0, 2)]
    have = [f for f in want if os.path.exists(f)]
    chk("D1 four 10k runs", len(have) == 4, f"{len(have)}/4 complete")

    print("SUBMISSION READINESS")
    print("=" * 92)
    w = max(len(i) for i, _, _ in rows)
    for item, ok, detail in rows:
        print(f"  {'PASS' if ok else 'PENDING':<8} {item:<{w}}  {detail}")
    bad = [i for i, ok, _ in rows if not ok]
    print(f"\n  {len(rows) - len(bad)}/{len(rows)} criteria met")
    if bad:
        print("  outstanding: " + ", ".join(bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
