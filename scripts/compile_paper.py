"""Compile PAPER.tex and fail on anything a submission would fail on.

This exists because 'the LaTeX looks fine' is not a claim anyone should accept.
Earlier drafts of PAPER.tex passed a structural check and still did not compile:
raw Unicode inside verbatim killed pdflatex outright, emphasis that straddled a
line break emitted literal asterisks, and the reference list came out as two
separate items both numbered 1.

Writes results/compile_paper.json. Skips with a clear message when no TeX
distribution is installed, rather than silently reporting success.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402

CANDIDATES = ["pdflatex", "/Library/TeX/texbin/pdflatex",
              "/usr/local/texlive/2026basic/bin/universal-darwin/pdflatex"]


def find_pdflatex():
    for c in CANDIDATES:
        p = shutil.which(c) if os.sep not in c else (c if os.path.exists(c) else None)
        if p:
            return p
    return None


def main():
    exe = find_pdflatex()
    out = {"pdflatex": exe}
    if not exe:
        out["status"] = "SKIPPED — no TeX distribution found"
        json.dump(out, open(os.path.join(R.RESULTS, "compile_paper.json"), "w"), indent=2)
        print("COMPILE PAPER")
        print("=" * 70)
        print("  SKIPPED — no pdflatex on this machine.")
        print("  The paper's LaTeX is therefore UNVERIFIED here; do not treat a green")
        print("  pipeline as evidence that PAPER.tex compiles.")
        return 0

    with tempfile.TemporaryDirectory() as d:
        shutil.copy("PAPER.tex", d)
        # the TMLR style file is vendored under tex/ (see tex/README.md)
        for f in os.listdir("tex"):
            if f.endswith((".sty", ".bst")):
                shutil.copy(os.path.join("tex", f), d)
        os.makedirs(os.path.join(d, "figures"), exist_ok=True)
        for f in os.listdir(R.FIGURES):
            if f.startswith("paper_fig"):
                shutil.copy(os.path.join(R.FIGURES, f), os.path.join(d, "figures", f))
        log = ""
        for _ in range(2):                      # twice, so refs and page numbers settle
            r = subprocess.run([exe, "-interaction=nonstopmode", "PAPER.tex"],
                               cwd=d, capture_output=True, text=True)
            log = open(os.path.join(d, "PAPER.log"), errors="replace").read()
        pdf = os.path.join(d, "PAPER.pdf")
        ok_pdf = os.path.exists(pdf)
        size = os.path.getsize(pdf) if ok_pdf else 0
        m = re.search(r"Output written on PAPER\.pdf \((\d+) pages", log)
        pages = int(m.group(1)) if m else 0
        errors = re.findall(r"^! (.+)$", log, re.M)
        overfull = len(re.findall(r"Overfull \\hbox", log))
        underfull = len(re.findall(r"Underfull \\hbox", log))
        warnings = re.findall(r"^LaTeX Warning: (.+)$", log, re.M)
        # emphasis that failed to convert would show as literal asterisks
        stray = len(re.findall(r"\*\*", open("PAPER.tex").read()))

        out.update({"status": "OK" if (ok_pdf and not errors) else "FAILED",
                    "pages": pages, "bytes": size, "errors": errors[:10],
                    "overfull_hboxes": overfull, "underfull_hboxes": underfull,
                    "latex_warnings": warnings[:10],
                    "stray_markdown_emphasis": stray, "returncode": r.returncode})

    json.dump(out, open(os.path.join(R.RESULTS, "compile_paper.json"), "w"), indent=2)
    print("COMPILE PAPER")
    print("=" * 70)
    print(f"  engine            : {exe}")
    print(f"  pdf produced      : {out['status']}  ({out['pages']} pages, {out['bytes']:,} bytes)")
    print(f"  errors            : {len(out['errors'])}")
    for e in out["errors"]:
        print(f"    ! {e}")
    print(f"  overfull hboxes   : {overfull}")
    print(f"  underfull hboxes  : {underfull}")
    print(f"  LaTeX warnings    : {len(warnings)}")
    print(f"  stray ** in .tex  : {stray}")
    bad = (out["status"] != "OK") or errors or overfull or stray or warnings
    print(f"\n  RESULT: {'PASS' if not bad else 'FAIL'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
