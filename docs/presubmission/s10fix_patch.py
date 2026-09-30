"""S10-fix: the source edits for S11's B1, B2 and the denominator ruling (DECISIONS_FOR_USER.md#S11-clean-clone-blocked).

Every match is whitespace-tolerant (a phrase may wrap across lines) and must occur exactly once. Nothing is
written until every assertion has passed; each edited file gets a .bak first, removed once the diff is shown.
Run from the repository root.
"""
import re, shutil, subprocess, sys

def pat(old):
    return re.compile(r"\s+".join(re.escape(w) for w in old.split()))

EDITS = [
    # B1: pypdf is imported by five scripts and was never pinned.
    ("requirements.txt",
     "tensordict==0.3.2",
     "tensordict==0.3.2\n\n# pypdf reads the compiled PDF for the rendered-PDF check, the submission gates and the\n"
     "# PDF-channel anonymity scan (scripts/pdf_render_check.py, part_f_gate.py, submission_check.py,\n"
     "# f5_pdf_channels.py, baseline_citations.py). It was installed by hand and never pinned, so a venv\n"
     "# built from this file failed all four checks (found by the clean-clone session S11). Pinned to the\n"
     "# version every recorded check ran under.\npypdf==6.16.1"),
    ("scripts/submission_check.py",
     # the whole line with its preceding newline, so the next line keeps its own indentation
     '\n            sys.path.insert(0, "/tmp/pdfvenv/lib/python3.14/site-packages")',
     ""),
    # B2: part_f_gate check 6 requires every abstract number to appear in the body; the body prints 89.15.
    ("PAPER.template.md",
     "The members share {{v1_shared_pct0}}% of their parameters;",
     "The members share {{v1_shared_pct}}% of their parameters;"),
    # The denominator: ver_all is the set the comparison counts, not every value under results/.
    ("PAPER.template.md",
     "rewrites {{ver_claim_pct}}% of the numeric values under `results/`; the rest are carried in",
     "rewrites {{ver_claim_pct}}% of the numeric values under `results/` that the comparison counts; the rest are carried in"),
    ("docs/BUILD_CHECKS.template.md",
     "or {{ver_claim_pct}}% of the {{ver_all}} numeric values under `results/`. The other {{ver_copied}} are carried in",
     "or {{ver_claim_pct}}% of the {{ver_all}} numeric values under `results/` that the comparison counts. The other {{ver_copied}} are carried in"),
    ("docs/BUILD_CHECKS.template.md",
     "of the {{ver_all}} numeric values under `results/`, a clean clone regenerates {{ver_values}} and carries in {{ver_copied}}. The reproducibility claim covers {{ver_claim_pct}}% of the directory and is silent about the rest.",
     "of the {{ver_all}} numeric values under `results/` that the comparison counts, a clean clone regenerates {{ver_values}} and carries in {{ver_copied}}. The reproducibility claim covers {{ver_claim_pct}}% of that counted set and is silent about the rest."),
    ("README.template.md",
     "{{ver_values}} values is {{ver_claim_pct}}% of the {{ver_all}} numeric values under `results/`.",
     "{{ver_values}} values is {{ver_claim_pct}}% of the {{ver_all}} numeric values under `results/` that the comparison counts."),
]

texts = {}
for f, old, new in EDITS:
    t = texts.setdefault(f, open(f, encoding="utf-8").read())
    n = len(pat(old).findall(t)) if "\n" not in old else t.count(old)
    assert n == 1, f"{f}: {old[:60]!r} matches {n} times, expected 1"
for f, old, new in EDITS:
    t = texts[f]
    if "\n" in old:
        texts[f] = t.replace(old, new, 1)
    else:
        texts[f] = pat(old).sub(lambda m: new, t, count=1)
for f in texts:
    shutil.copy(f, f + ".bak")
    open(f, "w", encoding="utf-8").write(texts[f])
    print(subprocess.run(["diff", f + ".bak", f], capture_output=True, text=True).stdout)
    import os; os.remove(f + ".bak")
print("applied", len(EDITS), "edits to", len(texts), "files")
