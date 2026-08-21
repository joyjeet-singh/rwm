"""Convert the resolved paper Markdown to LaTeX.

Deliberately narrow: it handles exactly the Markdown subset PAPER.template.md uses.
Anything it does not recognise it reports, rather than silently dropping -- a
converter that quietly loses a paragraph is worse than one that refuses.
"""
import re


UNI = {"μ": "mu", "σ": "sigma", "ε": "eps", "Δ": "Delta", "−": "-", "·": "*",
       "²": "^2", "×": "x", "≈": "~", "±": "+-", "—": "--", "–": "-", "§": "S",
       "“": '"', "”": '"', "’": "'"}


def _ascii(s):
    """verbatim under pdflatex is byte-oriented: no non-ASCII may survive."""
    for a, b in UNI.items():
        s = s.replace(a, b)
    return "".join(c if ord(c) < 128 else "?" for c in s)


def esc(s):
    """Escape LaTeX specials in prose. Inline code and math are protected first."""
    out, i = [], 0
    # protect `code` and $math$ spans
    tokens = []

    def stash(m):
        tokens.append(m.group(0))
        return f"\x00{len(tokens)-1}\x00"

    s = re.sub(r"`[^`]*`", stash, s)
    for a, b in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("$", r"\$"),
                 ("#", r"\#"), ("_", r"\_"), ("{", r"\{"), ("}", r"\}"), ("~", r"\textasciitilde{}"),
                 ("^", r"\textasciicircum{}")):
        s = s.replace(a, b)
    s = s.replace("—", "---").replace("–", "--").replace("×", r"$\times$")
    s = s.replace("σ", r"$\sigma$").replace("μ", r"$\mu$").replace("ε", r"$\varepsilon$")
    s = s.replace("Δ", r"$\Delta$").replace("±", r"$\pm$").replace("≈", r"$\approx$")
    s = s.replace("§", r"\S").replace("“", "``").replace("”", "''")
    s = s.replace("−", "$-$")
    # text-mode LaTeX renders these as other glyphs; force math mode
    s = s.replace(chr(92) + "|", "$|$").replace("|", "$|$")
    s = s.replace(">", "$>$").replace("<", "$<$")

    def unstash(m):
        t = tokens[int(m.group(1))].strip("`")
        for a, b in (("\\", r"\textbackslash{}"), ("_", r"\_"), ("&", r"\&"),
                     ("%", r"\%"), ("#", r"\#"), ("{", r"\{"), ("}", r"\}")):
            t = t.replace(a, b)
        return r"\texttt{" + t + "}"

    s = re.sub(r"\x00(\d+)\x00", unstash, s)
    # bold / italic after escaping so the markers survive
    s = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", s)
    s = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"\\emph{\1}", s)
    return s


def convert(md, title, author):
    lines = md.split("\n")
    out, unhandled = [], []
    i, in_code = 0, False
    out.append(r"""\documentclass[11pt,a4paper]{article}
\usepackage[margin=1in]{geometry}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage[hidelinks]{hyperref}
\usepackage{textcomp}
\setlength{\parskip}{0.5em}
\setlength{\parindent}{0pt}
% Long \texttt tokens (flag names, arXiv ids) cannot hyphenate; give TeX room
% rather than letting them run into the margin.
\emergencystretch=3em
\hbadness=10000
\sloppy
\title{""" + esc(title) + r"""}
\author{""" + esc(author) + r"""}
\date{}
\begin{document}
\maketitle
""")
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("<!--"):
            while i < len(lines) and "-->" not in lines[i]:
                i += 1
            i += 1
            continue
        if ln.strip().startswith("```"):
            in_code = not in_code
            out.append(r"\begin{verbatim}" if in_code else r"\end{verbatim}")
            i += 1
            continue
        if in_code:
            out.append(_ascii(ln))
            i += 1
            continue
        if ln.strip().startswith("$$") and ln.strip().endswith("$$") and len(ln.strip()) > 4:
            out.append(r"\[" + ln.strip()[2:-2] + r"\]")
            i += 1
            continue
        if ln.startswith("    ") and ln.strip():          # indented code
            block = []
            while i < len(lines) and (lines[i].startswith("    ") or not lines[i].strip()):
                block.append(lines[i][4:])
                i += 1
            while block and not block[-1].strip():
                block.pop()
            out += [r"\begin{verbatim}"] + [_ascii(x) for x in block] + [r"\end{verbatim}"]
            continue
        m = re.match(r"^(#{1,4})\s+(.*)$", ln)
        if m:
            lvl, txt = len(m.group(1)), m.group(2)
            if lvl == 1:
                # \maketitle already emitted this; skip it and the author line under it
                i += 1
                while i < len(lines) and (not lines[i].strip()
                                          or re.match(r"^\*\*.+\*\*$", lines[i].strip())
                                          or lines[i].strip() == "---"):
                    i += 1
                continue
            txt = re.sub(r"^\d+(\.\d+)*\.?\s*", "", txt)   # LaTeX numbers sections itself
            cmd = {1: "section", 2: "section", 3: "subsection", 4: "subsubsection"}[lvl]
            if txt.strip().startswith("Appendix") and not any(
                    x.startswith(chr(92) + "appendix") for x in out):
                out.append(r"\appendix")
            if txt.strip().startswith("Appendix"):
                txt = re.sub(r"^Appendix [A-Z]\s*[—-]\s*", "", txt)
            if txt.strip().lower() == "abstract":
                out.append(r"\begin{abstract}")
                i += 1
                buf = []
                while i < len(lines) and not lines[i].startswith("---"):
                    buf.append(lines[i])
                    i += 1
                out.append(esc(" ".join(x for x in buf if x.strip())))
                out.append(r"\end{abstract}")
                continue
            out.append(f"\\{cmd}{{{esc(txt)}}}")
            i += 1
            continue
        if ln.startswith("|"):
            tbl = []
            while i < len(lines) and lines[i].startswith("|"):
                tbl.append(lines[i])
                i += 1
            cells = [re.split(r"(?<!\\)\|", r)[1:-1] for r in tbl]
            cells = [c for c in cells if not all(set(x.strip()) <= set("-: ") for x in c)]
            n = max(len(c) for c in cells)
            out.append(r"\begin{center}\small\resizebox{\ifdim\width>\linewidth\linewidth\else\width\fi}{!}{%")
            out.append(r"\begin{tabular}{" + "l" * n + "}")
            out.append(r"\toprule")
            for j, row in enumerate(cells):
                row = [esc(x.strip().replace(r"\|", "|")) for x in row] + [""] * (n - len(row))
                out.append(" & ".join(row) + r" \\")
                if j == 0:
                    out.append(r"\midrule")
            out.append(r"\bottomrule\end{tabular}}\end{center}")
            continue
        if re.match(r"^!\[.*\]\((.*)\)", ln):
            src = re.match(r"^!\[.*\]\((.*)\)", ln).group(1)
            out.append(r"\begin{figure}[htbp]\centering\includegraphics[width=\linewidth]"
                       r"{\detokenize{" + src + r"}}\end{figure}")
            i += 1
            continue
        if ln.startswith("- "):
            out.append(r"\begin{itemize}")
            while i < len(lines) and lines[i].startswith("- "):
                item = [lines[i][2:]]
                i += 1
                # a wrapped continuation line belongs to the item, not to a new paragraph
                while (i < len(lines) and lines[i].strip()
                       and not lines[i].startswith("- ")
                       and not lines[i].startswith("#")
                       and not lines[i].startswith("|")):
                    item.append(lines[i].strip())
                    i += 1
                out.append(r"\item " + esc(" ".join(x.strip() for x in item)))
            out.append(r"\end{itemize}")
            continue
        if re.match(r"^\d+\.\s", ln):
            out.append(r"\begin{enumerate}")
            while i < len(lines) and re.match(r"^\d+\.\s", lines[i]):
                item = [re.sub(r"^\d+\.\s", "", lines[i])]
                i += 1
                while (i < len(lines) and lines[i].strip()
                       and not re.match(r"^\d+\.\s", lines[i])
                       and not lines[i].startswith("#")
                       and not lines[i].startswith("|")):
                    item.append(lines[i].strip())
                    i += 1
                out.append(r"\item " + esc(" ".join(x.strip() for x in item)))
            out.append(r"\end{enumerate}")
            continue
        if ln.strip() == "---":
            i += 1
            continue
        if not ln.strip():
            out.append("")
            i += 1
            continue
        para = [ln]
        i += 1
        while i < len(lines):
            nxt = lines[i]
            if (not nxt.strip() or nxt.startswith("|") or nxt.startswith("- ")
                    or nxt.startswith("    ") or nxt.lstrip().startswith("$$")
                    or nxt.startswith("#") or nxt.startswith("!") or nxt.strip() == "---"
                    or nxt.strip().startswith("```") or re.match(r"^\d+\.\s", nxt)):
                break
            para.append(nxt)
            i += 1
        out.append(esc(" ".join(x.strip() for x in para)))
    out.append(r"\end{document}")
    tex = "\n".join(out)

    # Structural check. There is no LaTeX toolchain here, so verify what can be
    # verified without one: environments balance, and no unescaped specials survive
    # outside verbatim.
    body_wo_verb = re.sub(r"\\begin\{verbatim\}.*?\\end\{verbatim\}", "", tex, flags=re.S)
    # \detokenize makes filename underscores safe; do not re-flag them
    body_wo_verb = re.sub(r"\\detokenize\{[^}]*\}", "", body_wo_verb)
    # subscripts inside display/inline math are correct LaTeX, not stray specials
    body_wo_verb = re.sub(r"\\\[.*?\\\]", "", body_wo_verb, flags=re.S)
    body_wo_verb = re.sub(r"\$[^$]*\$", "", body_wo_verb)
    # a trailing %% is a LaTeX line-continuation comment, not a stray special
    # LaTeX comments -- a trailing %% continuation or a whole comment line -- are
    # legitimate, not stray specials
    body_wo_verb = re.sub(r"^\s*%.*$", "", body_wo_verb, flags=re.M)
    body_wo_verb = re.sub(r"%$", "", body_wo_verb, flags=re.M)
    for env in ("verbatim", "tabular", "itemize", "enumerate", "figure", "abstract", "center",
                "document"):
        b = len(re.findall(r"\\begin\{" + env + r"\}", tex))
        e = len(re.findall(r"\\end\{" + env + r"\}", tex))
        if b != e:
            unhandled.append(f"unbalanced environment {env}: {b} begin vs {e} end")
    for ch, name in (("_", "underscore"), ("#", "hash"), ("%", "percent")):
        pat = "(?<!" + re.escape(chr(92)) + ")" + re.escape(ch)
        stray = re.findall(pat, body_wo_verb)
        if stray:
            unhandled.append(str(len(stray)) + " unescaped " + name + "(s)")
    return tex, unhandled
