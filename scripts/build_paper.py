"""Build PAPER.md from PAPER.template.md by substituting values read from artifacts.

The point of the indirection: no number in the paper is typed. Every {{key}} resolves
from results/paper_numbers.json, which scripts/paper_numbers.py derives from the run
artifacts. The build fails if any placeholder is unresolved, so a paper that mentions
a quantity we no longer measure cannot be produced.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402

TEMPLATE = "PAPER.template.md"
OUT = "PAPER.md"


def main():
    N = json.load(open(os.path.join(R.RESULTS, "paper_numbers.json")))
    text = open(TEMPLATE).read()

    used, missing = set(), []

    def sub(m):
        k = m.group(1)
        if k not in N:
            missing.append(k)
            return m.group(0)
        used.add(k)
        return str(N[k]["value"])

    out = re.sub(r"\{\{([A-Za-z0-9_]+)\}\}", sub, text)

    assert not missing, ("placeholders with no value in paper_numbers.json: "
                         + ", ".join(sorted(set(missing))))
    leftover = re.findall(r"\{\{[^}]*\}\}", out)
    assert not leftover, f"unresolved placeholders remain: {sorted(set(leftover))}"

    unused = sorted(set(N) - used)

    # Typed-number check. The paper claims no number in it is typed by hand, and a
    # hand-typed retraction count ("Four claims...") once contradicted the derived
    # count in the same PDF. Everything numeric that is NOT a placeholder is listed
    # here every build, so a typed number has to be looked at rather than assumed
    # benign. Section numbers, arXiv ids and defined constants are expected.
    prose = re.sub(r"\{\{[A-Za-z0-9_]+\}\}", "", text)
    prose = re.sub(r"```.*?```", "", prose, flags=re.S)
    prose = re.sub(r"^ {4}.*$", "", prose, flags=re.M)
    prose = prose.split("## References")[0]
    WORDS = r"\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|" \
            r"thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty)\b"
    typed_words = sorted({m.group(0).lower() for m in re.finditer(WORDS, prose, re.I)})
    typed_nums = sorted({m.group(1) for m in
                         re.finditer(r"(?<![\w.])(\d[\d,]*\.?\d*)(?![\w])", prose)},
                        key=lambda x: (len(x), x))

    figs = sorted(f for f in os.listdir(R.FIGURES) if f.startswith("paper_fig"))
    header = (
        "<!-- GENERATED FILE — do not edit.\n"
        "     Prose lives in PAPER.template.md; every number is substituted from\n"
        "     results/paper_numbers.json by scripts/build_paper.py. Edit the template,\n"
        "     then run: python scripts/build_paper.py\n"
        f"     {len(used)} values substituted from {len(set(N[k]['source'] for k in used))} artifacts. -->\n\n")
    body = out.rstrip() + "\n\n## Figures\n\n"
    for f in figs:
        body += f"![{f}](figures/{f})\n\n"
    open(OUT, "w").write(header + body)

    # LaTeX for submission, from the same resolved text -- one source, two outputs.
    import md_to_tex
    title = re.search(r"^# (.+)$", out, re.M).group(1)
    tex, unhandled = md_to_tex.convert(header + body, title, "Joyjeet Singh")
    open("PAPER.tex", "w").write(tex)
    assert not unhandled, f"converter did not handle: {unhandled[:5]}"

    print("PAPER BUILD")
    print("=" * 72)
    print(f"  template            : {TEMPLATE} ({len(text.splitlines())} lines)")
    print(f"  placeholders filled : {len(used)}")
    print(f"  distinct artifacts  : {len(set(N[k]['source'] for k in used))}")
    print(f"  figures attached    : {len(figs)}")
    print(f"  numerals typed in prose : {len(typed_nums)}  "
          f"(section numbers, arXiv ids and constants expected)")
    print(f"  number-words in prose   : {len(typed_words)}  {', '.join(typed_words)}")
    if unused:
        print(f"  collected but unused: {len(unused)}")
        print("    " + ", ".join(unused))
    print(f"  wrote {OUT} ({len(body.splitlines())} lines)")
    print(f"  wrote PAPER.tex ({len(tex.splitlines())} lines)")
    print("\n  every number in the paper traces to:")
    for s in sorted(set(N[k]["source"] for k in used)):
        print(f"    {s}")


if __name__ == "__main__":
    main()
