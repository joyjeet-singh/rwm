"""Convert the resolved paper Markdown to LaTeX.

Deliberately narrow: it handles exactly the Markdown subset PAPER.template.md uses.
Anything it does not recognise it reports, rather than silently dropping -- a
converter that quietly loses a paragraph is worse than one that refuses.
"""
import re


UNI = {"μ": "mu", "σ": "sigma", "ε": "eps", "Δ": "Delta", "−": "-", "·": "*",
       "α": "alpha", "β": "beta", "π": "pi", "γ": "gamma", "θ": "theta", "τ": "tau",
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
    # inline math must survive escaping intact, exactly as code spans do
    s = re.sub(r"\$[^$\n]+\$", stash, s)
    # A caret exponent in prose ("10^13") is a power, not a circumflex; the escape
    # below would set it as a literal caret. Marked here, raised after escaping.
    s = re.sub(r"(?<=\d)\^(\d+)", lambda m: "\x02" + m.group(1) + "\x03", s)
    for a, b in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("$", r"\$"),
                 ("#", r"\#"), ("_", r"\_"), ("{", r"\{"), ("}", r"\}"), ("~", r"\textasciitilde{}"),
                 ("^", r"\textasciicircum{}")):
        s = s.replace(a, b)
    s = re.sub("\x02(\\d+)\x03", r"\\textsuperscript{\1}", s)
    s = s.replace("—", "---").replace("–", "--").replace("×", r"$\times$")
    s = s.replace("σ", r"$\sigma$").replace("μ", r"$\mu$").replace("ε", r"$\varepsilon$")
    s = s.replace("λ", r"$\lambda$").replace("φ", r"$\phi$").replace("\u0303", "")
    # Relational operators reach the .tex from the LEDGER, not from the template:
    # M-64's committed title contains "h <= 128" as U+2264, and Appendix G quotes
    # rule titles verbatim. The ledger is append-only, so a rule's title cannot be
    # rewritten to suit the converter -- the converter has to set what the ledger says.
    s = s.replace("≤", r"$\le$").replace("≥", r"$\ge$").replace("≠", r"$\ne$")
    # A combining circumflex is a SEPARATE codepoint following the letter it
    # decorates, so "σ̂" is two characters and the sigma rule above has already
    # turned the first into $\sigma$ by the time this runs -- leaving a bare
    # U+0302 that LaTeX cannot set. Rewritten as a hat over the preceding math
    # rather than dropped: "sigma-hat" and "sigma" are different quantities in
    # §6.3 and losing the mark would silently merge them.
    s = re.sub(r"\$\\(sigma|mu)\$\u0302", lambda m: r"$\hat{\%s}$" % m.group(1), s)
    s = s.replace("\u0302", "")
    s = s.replace("∂", r"$\partial$")
    # alpha arrived with the Holm-Bonferroni thresholds and was not in this map;
    # pdflatex fails hard on an unmapped Unicode letter rather than warning.
    s = s.replace("α", r"$\alpha$").replace("β", r"$\beta$").replace("π", r"$\pi$")
    s = s.replace("γ", r"$\gamma$").replace("θ", r"$\theta$").replace("τ", r"$\tau$")
    s = s.replace("Δ", r"$\Delta$").replace("±", r"$\pm$").replace("≈", r"$\approx$")
    s = s.replace("§", r"\S{}").replace("“", "``").replace("”", "''")
    s = s.replace("−", "$-$")
    # text-mode LaTeX renders these as other glyphs; force math mode
    s = s.replace(chr(92) + "|", "$|$").replace("|", "$|$")
    s = s.replace(">", "$>$").replace("<", "$<$")

    def unstash(m):
        raw = tokens[int(m.group(1))]
        if raw.startswith("$"):
            return raw                      # inline math: emit verbatim
        # Inline code is protected from escaping, which means Unicode inside it would
        # reach \texttt{} raw and kill pdflatex. Transliterate rather than trust the author.
        # The few characters the paper's code spans carry are set as their glyphs
        # rather than transliterated: "?" for lambda and a dropped tilde changed
        # what the formula says. Marked before _ascii, set after escaping.
        t = re.sub(r"([A-Za-z])̃", "\x02t\\1\x03", raw.strip("`"))
        t = t.replace("λ", "\x02l\x03").replace("−", "\x02m\x03").replace("²", "\x02s\x03")
        t = _ascii(t)
        for a, b in (("\\", r"\textbackslash{}"), ("_", r"\_"), ("&", r"\&"),
                     ("%", r"\%"), ("#", r"\#"), ("{", r"\{"), ("}", r"\}"),
                     ("^", r"\textasciicircum{}"), ("~", r"\textasciitilde{}"),
                     ("$", r"\$")):
            t = t.replace(a, b)
        t = re.sub("\x02t([A-Za-z])\x03", r"$\\tilde{\\texttt{\1}}$", t)
        t = t.replace("\x02l\x03", r"$\lambda$").replace("\x02m\x03", "$-$")
        t = t.replace("\x02s\x03", r"\textsuperscript{2}")
        # "--" inside \texttt is a ligature and sets as one dash; a copied flag
        # would then be invalid. An empty group between the hyphens breaks it.
        t = re.sub(r"-(?=-)", "-{}", t)
        return r"\texttt{" + t + "}"

    s = re.sub(r"\x00(\d+)\x00", unstash, s)
    # bold / italic after escaping so the markers survive
    s = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", s)
    s = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"\\emph{\1}", s)
    return s


# ------------------------------------------------------------- wide tables
# An `l` column never wraps, so a table whose cells are paragraphs rather than
# labels sets to several times the text block and the \resizebox around it then
# shrinks the whole table to fit. Appendices D, E and F reached the PDF at
# 2.48pt, 0.78pt and 2.80pt against 9.96pt body text: present in the text layer,
# which is why an extraction reads them as run-together prose, and unreadable on
# the page. Over a width budget the table is emitted as a longtable of wrapping
# p{} columns instead -- same \small as before, no scaling, and it breaks across
# pages rather than overflowing one.
_CHARS_PER_LINE = 100          # characters of \small text across \linewidth
_WIDE_TABLE_CHARS = 2 * _CHARS_PER_LINE   # i.e. \resizebox would halve the font
# Floors are computed in points, not in characters, because a column that is one
# character short of its widest unbreakable token is an overfull box and the
# compile gate fails on any overfull box at all. \small typewriter is the widest
# face these tables use, at 4.73pt per character; 5.0 leaves a little slack.
_LINEWIDTH_PT = 469.75         # tmlr.sty: \textwidth 6.5 true in
_FLOOR_CHAR_PT = 5.0           # conservative width of one \small character
_TABCOLSEP_PT = 12.0           # the 2\tabcolsep each column spec subtracts


def _cell_width(s):
    """Rendered length of a Markdown cell, ignoring emphasis and code markers."""
    return len(re.sub(r"[*`]", "", s.strip()))


def _longest_token(s):
    """Longest run in the cell with no break opportunity inside it.

    "/" and "_" count as break opportunities because _wrap_cell puts an
    \\allowbreak after each; without that, results/m63_per_dimension_coverage.json
    is 39 unbreakable characters and its column would take 40% of the line.
    """
    return max((len(t) for t in re.split(r"[\s/_]+", re.sub(r"[*`]", "", s.strip()))),
               default=0)


def _column_fractions(widths, floors):
    """Fractions of \\linewidth: proportional to content, never below a floor."""
    n = len(widths)
    lo = [min((f * _FLOOR_CHAR_PT + _TABCOLSEP_PT) / _LINEWIDTH_PT, 1.0) for f in floors]
    if sum(lo) >= 1.0:                       # floors alone fill the line
        return [x / sum(lo) for x in lo]
    pinned = [False] * n
    while True:
        budget = 1.0 - sum(lo[k] for k in range(n) if pinned[k])
        tot = sum(widths[k] for k in range(n) if not pinned[k]) or 1
        frac = [lo[k] if pinned[k] else budget * widths[k] / tot for k in range(n)]
        short = [k for k in range(n) if not pinned[k] and frac[k] < lo[k]]
        if not short:
            return frac
        pinned[short[0]] = True              # one more column fixed at its floor


def _wrap_cell(s):
    """Let file paths and underscored identifiers break inside a p{} column."""
    if "\\url{" in s or "http" in s:
        return s
    return s.replace("/", "/\\allowbreak{}").replace("\\_", "\\_\\allowbreak{}")


def _is_table(lines, i):
    """True when the pipe-line at `i` opens a real Markdown table.

    The separator row is what distinguishes a table from a sentence that
    happened to wrap onto a line beginning with a pipe. Markdown itself makes
    the same distinction; this converter did not.
    """
    return (i + 1 < len(lines) and lines[i + 1].startswith("|")
            and set(lines[i + 1].replace("|", "").strip()) <= set("-: ")
            and lines[i + 1].strip() != "")


def _is_olist(lines, i):
    """True when the numbered line at `i` really opens an ordered list.

    A marker only opens a list at a block boundary. Without that condition a
    wrapped prose line whose first token was a substituted numeral was read as a
    list item and the numeral was eaten by \\item: S6.2 reached the PDF as
    "... at n_independent =" followed by a list beginning "1. Both are correct",
    and S6.7 the same way with M-43's four horizons. Markdown itself only lets a
    list interrupt a paragraph in the one case this converter never needs.
    """
    return (re.match(r"^\d+\.\s", lines[i]) is not None
            and (i == 0 or not lines[i - 1].strip()))


def _footnotes(md):
    """Rewrite Markdown footnotes to numbered superscripts.

    Markdown footnote syntax is not LaTeX and this converter had no rule for it,
    so "[^stepcount]" reached the PDF as literal text inside a table cell and its
    definition reached it as a literal paragraph. \\footnote is not usable at that
    site -- the reference sits in a tabular inside a \\resizebox, where LaTeX drops
    the note -- so the reference becomes a superscript number and the definition
    keeps its place under the table with its wording untouched.

    Markers are \\x01N\\x01 so they survive esc() unescaped; convert() turns them
    into \\textsuperscript{N} once the LaTeX is assembled.
    """
    defs = set(re.findall(r"^\[\^([A-Za-z0-9_-]+)\]:", md, flags=re.M))
    order, undefined = {}, []

    def _ref(m):
        tok = m.group(1)
        if tok not in defs:
            undefined.append(tok)
            return m.group(0)
        if tok not in order:
            order[tok] = len(order) + 1
        return "\x01%d\x01" % order[tok]

    md = re.sub(r"\[\^([A-Za-z0-9_-]+)\]", _ref, md)
    md = re.sub(r"^(\x01\d+\x01):[ \t]*", r"\1 ", md, flags=re.M)
    return md, undefined


def convert(md, title, author):
    md, fn_undefined = _footnotes(md)
    lines = md.split("\n")
    out, unhandled = [], []
    if fn_undefined:
        unhandled.append("footnote reference with no definition: "
                         + ", ".join(sorted(set(fn_undefined))))
    i, in_code = 0, False
    out.append(r"""\documentclass[10pt]{article}
% TMLR requires its official style file; non-compliance is grounds for desk
% rejection. No package option = anonymous submission mode, which replaces the
% author block with "Anonymous authors" and sets the "Under review" running head.
% Do NOT add [accepted] or [preprint] for a submission: both de-anonymise.
\usepackage{tmlr}

\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{booktabs}
% array for the \raggedright p-columns wide tables use, longtable so a table
% taller than a page breaks instead of overflowing it. Both are LaTeX tools.
\usepackage{array}
\usepackage{longtable}
\usepackage[hidelinks]{hyperref}
\usepackage{url}
\usepackage{textcomp}
% tmlr.sty fixes \textwidth, \textheight and the margins itself, so geometry
% must not be loaded here -- it would silently override the required layout.
\emergencystretch=3em
\hbadness=10000
\sloppy
\def\month{MM}
\def\year{YYYY}
\def\openreview{\url{https://openreview.net/forum?id=XXXX}}
\title{""" + esc(title) + r"""}
% Author intentionally omitted: the submission is double-blind and tmlr.sty
% renders "Anonymous authors" in this mode regardless.
\author{}
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
                # LaTeX supplies the letter; strip "Appendix X — " and capitalise what
                # is left, or the heading renders as "A verification chain".
                txt = re.sub(r"^Appendix [A-Z]\s*[—-]\s*", "", txt)
                txt = txt[:1].upper() + txt[1:]
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
        # A Markdown table is a run of pipe-delimited lines whose SECOND line is
        # the |---|---| separator. Without that condition any wrapped prose line
        # beginning with a pipe became a one-column tabular: "the rule's minimum
        # detectable effect at this sample size is |r_dd| >= 0.183" wrapped so
        # that "|r_dd| >= ..." started a line, and the sentence was replaced in
        # the PDF by a booktabs box containing the words "r_dd". Nothing in the
        # build could see it -- every placeholder resolved, so the unresolved-
        # placeholder gate passed. build_paper.py now also refuses a stray row.
        if ln.startswith("|") and _is_table(lines, i):
            tbl = []
            while i < len(lines) and lines[i].startswith("|"):
                tbl.append(lines[i])
                i += 1
            cells = [re.split(r"(?<!\\)\|", r)[1:-1] for r in tbl]
            cells = [c for c in cells if not all(set(x.strip()) <= set("-: ") for x in c)]
            n = max(len(c) for c in cells)
            body = [[esc(x.strip().replace(r"\|", "|")) for x in row] + [""] * (n - len(row))
                    for row in cells]
            colw = [max(_cell_width(c[k]) if k < len(c) else 0 for c in cells)
                    for k in range(n)]
            if sum(colw) > _WIDE_TABLE_CHARS:
                floors = [max(_longest_token(c[k]) if k < len(c) else 0 for c in cells)
                          for k in range(n)]
                spec = "".join(
                    r">{\raggedright\arraybackslash}p{\dimexpr %.4f\linewidth-2\tabcolsep\relax}"
                    % f for f in _column_fractions(colw, floors))
                hdr = " & ".join(_wrap_cell(x) for x in body[0]) + r" \\"
                out.append(r"\begingroup\small")
                out.append(r"\begin{longtable}{" + spec + "}")
                out.append(r"\toprule " + hdr + r" \midrule\endfirsthead")
                out.append(r"\toprule " + hdr + r" \midrule\endhead")
                out.append(r"\bottomrule\endlastfoot")
                for row in body[1:]:
                    out.append(" & ".join(_wrap_cell(x) for x in row) + r" \\")
                out.append(r"\end{longtable}\endgroup")
                continue
            out.append(r"\begin{center}\small\resizebox{\ifdim\width>\linewidth\linewidth\else\width\fi}{!}{%")
            out.append(r"\begin{tabular}{" + "l" * n + "}")
            out.append(r"\toprule")
            for j, row in enumerate(body):
                out.append(" & ".join(row) + r" \\")
                if j == 0:
                    out.append(r"\midrule")
            out.append(r"\bottomrule\end{tabular}}\end{center}")
            continue
        if re.match(r"^!\[.*\]\((.*)\)", ln):
            src = re.match(r"^!\[.*\]\((.*)\)", ln).group(1)
            cap = re.match(r"^!\[(.*)\]\(.*\)", ln).group(1)
            # The alt text is the caption. Escaping is already applied upstream
            # for prose, but this string never passes through esc(), so the few
            # LaTeX-active characters a caption can contain are handled here.
            cap = cap.replace("%", r"\%") if "\\%" not in cap else cap
            # [!ht] rather than [htbp]: the figures are now emitted next to the
            # paragraph that first refers to them (build_paper.py), so "here" is
            # the right answer and "p" -- a float page of its own at the end -- is
            # what used to carry them past section 14.
            out.append(r"\begin{figure}[!ht]\centering\includegraphics[width=\linewidth]"
                       r"{\detokenize{" + src + r"}}"
                       + (r"\caption{" + cap + r"}" if cap else "")
                       + r"\end{figure}")
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
        if _is_olist(lines, i):
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
                    or nxt.strip().startswith("```") or _is_olist(lines, i)):
                break
            para.append(nxt)
            i += 1
        out.append(esc(" ".join(x.strip() for x in para)))
    out.append(r"\end{document}")
    tex = "\n".join(out)
    tex = re.sub("\x01(\\d+)\x01", r"\\textsuperscript{\1}", tex)

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
    for env in ("verbatim", "tabular", "longtable", "itemize", "enumerate", "figure",
                "abstract", "center", "document"):
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
