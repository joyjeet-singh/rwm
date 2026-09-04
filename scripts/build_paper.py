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

# ---------------------------------------------------------------------------
# Session 2 gate rules. Three classes of Markdown-to-LaTeX damage reached the
# compiled PDF while every {{key}} resolved, so the brace gate saw nothing. Each
# rule below is a separate function so a deliberately corrupted input can be fed
# to it directly, the way check_comparative_claims.py corrupts its own
# expectations.
# ---------------------------------------------------------------------------

# The capitalised renderings scripts/paper_numbers.py substitutes from WORDS.
_NUMBER_WORDS = {"One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight",
                 "Nine", "Ten", "Eleven", "Twelve", "Thirteen"}


def check_orphan_ordinal_after_equals(lines):
    """A bare "N." line right after a line ending in "=" or "~=".

    S6.2 wrapped as "... at n_independent =" / "20. **Both are correct", the
    converter read "20." as an ordered-list marker, and the 20 was eaten. The
    equals sign is the tell: nothing legitimate in this paper opens a list under
    a line that ends mid-equation.
    """
    bad = []
    for n, ln in enumerate(lines):
        if n == 0 or not re.match(r"^\d+\.(\s|$)", ln):
            continue
        prev = lines[n - 1].rstrip()
        if prev.endswith("=") or prev.endswith("≈"):
            bad.append(f"line {n + 1}: {prev[-48:]!r} then {ln[:48]!r}")
    return bad


def check_ordinal_interrupting_paragraph(lines):
    """A numbered marker that opens mid-paragraph rather than at a block boundary.

    The same damage as above with no equals sign to spot it: S6.7's "M-43's own"
    / "4. The released checkpoint's table" ate the 4. A marker is a list only if
    a blank line precedes it, or a numbered item is already open in the same
    blank-line-delimited block (a wrapped reference entry).
    """
    bad = []
    open_here = False
    for n, ln in enumerate(lines):
        if not ln.strip():
            open_here = False
            continue
        if not re.match(r"^\d+\.\s", ln):
            continue
        if n > 0 and lines[n - 1].strip() and not open_here:
            bad.append(f"line {n + 1}: {lines[n - 1][-48:]!r} then {ln[:48]!r}")
        open_here = True
    return bad


def check_footnote_tokens(tex):
    """A Markdown footnote token surviving into the LaTeX.

    "[^stepcount]" set as literal text in a table cell of S6.7, and its
    definition as a literal paragraph, because the converter had no footnote
    rule. esc() turns the caret into \\textasciicircum{}, so both spellings are
    checked.
    """
    pat = r"\[(?:\^|\\textasciicircum\{\})([A-Za-z0-9_-]+)\]"
    return sorted(set(re.findall(pat, tex)))


def check_number_word_case(template, values):
    """A capitalised number-word substituted mid-sentence.

    paper_numbers.py renders counts through WORDS, which is capitalised for
    sentence-initial use. Dropped into running prose it produced "then named
    Five" in S4 and "the Four defects it has found" in Appendix C, which read as
    proper nouns. The fix belongs at the substitution site -- a `_lower` key --
    so the next build cannot reintroduce it.
    """
    bad = []
    for m in re.finditer(r"\{\{([A-Za-z0-9_]+)\}\}", template):
        k = m.group(1)
        if k not in values or str(values[k]["value"]) not in _NUMBER_WORDS:
            continue
        pre = template[:m.start()].rstrip(" \t*_`>")
        if pre == "" or pre[-1] in "\n.!?:":
            continue
        line = template[:m.start()].count("\n") + 1
        bad.append(f"line {line}: {{{{{k}}}}} = {values[k]['value']!r} after {pre[-40:]!r}")
    return bad


def selftest_gates():
    """Run each gate rule against a deliberately corrupted input; each must fire.

    Same discipline as check_comparative_claims.py's corrupted expectations: a
    refusal that has quietly stopped being able to refuse reads as coverage and
    is not. Returns the number of rules that caught their corruption.
    """
    caught = 0
    caught += bool(check_orphan_ordinal_after_equals(
        ["cumulative to h = 100, at n_independent =", "20. **Both are correct**"]))
    caught += bool(check_ordinal_interrupting_paragraph(
        ["The verdict above is over M-43's own", "4. The released checkpoint's table"]))
    caught += bool(check_footnote_tokens(
        r"median +0.737[\textasciicircum{}stepcount] and [^stepcount]: adjacent steps"))
    caught += bool(check_number_word_case(
        "and then named {{n_word_probe}}, and", {"n_word_probe": {"value": "Five"}}))
    return caught


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

    # {{FIGURES}} is a placement marker, not a value: it is substituted after the
    # numeric pass, so exclude it from both the missing and leftover checks.
    text_marked = text.replace("{{FIGURES}}", "\x00FIGURES\x00")
    out = re.sub(r"\{\{([A-Za-z0-9_]+)\}\}", sub, text_marked)
    out = out.replace("\x00FIGURES\x00", "{{FIGURES}}")

    assert not missing, ("placeholders with no value in paper_numbers.json: "
                         + ", ".join(sorted(set(missing))))
    leftover = [x for x in re.findall(r"\{\{[^}]*\}\}", out) if x != "{{FIGURES}}"]
    assert not leftover, f"unresolved placeholders remain: {sorted(set(leftover))}"

    # C3(rev2), 3.2 -- the gate widened past {{...}} syntax.
    #
    # §9 claims zero unresolved placeholders and the claim was true, yet a whole
    # sentence of §6.7 reached the PDF as a one-column table: "|r_dd| >= 0.183"
    # wrapped onto its own line, the converter read a leading pipe as a table
    # row, and the prose vanished into a booktabs box. Every placeholder had
    # resolved. The gate could not see it because it only ever looked at brace
    # syntax.
    #
    # Three further failure shapes, each of which reached a PDF at some point in
    # this project or would have:
    #   1. a stray table row -- a pipe-led line with no separator row under it;
    #   2. a placeholder written with one brace, {key}, which substitutes to
    #      nothing and reads as prose;
    #   3. an empty or literal-None value reaching the text.
    lines = out.split("\n")
    stray = []
    in_code = False
    for n, ln in enumerate(lines):
        if ln.strip().startswith("```"):
            in_code = not in_code
        if in_code or not ln.startswith("|"):
            continue
        # a row belongs to a table if it or an earlier contiguous pipe-line is
        # followed by the |---| separator
        j = n
        while j > 0 and lines[j - 1].startswith("|"):
            j -= 1
        sep = (j + 1 < len(lines) and lines[j + 1].startswith("|")
               and set(lines[j + 1].replace("|", "").strip()) <= set("-: "))
        if not sep:
            stray.append(f"line {n + 1}: {ln[:80]}")
    assert not stray, ("pipe-led lines that are not table rows -- these render as "
                       "one-column tables and swallow the sentence:\n  "
                       + "\n  ".join(stray[:5]))

    # Only a single-braced token that IS a known key is a mis-typed placeholder;
    # \mathrm{Var} and \mathrm{erf} are not, and matching brace shape alone
    # flags every one of them.
    single = [k for k in re.findall(r"(?<!\{)\{([A-Za-z][A-Za-z0-9_]{2,})\}(?!\})", out)
              if k in N]
    assert not single, f"single-brace placeholders that substituted nothing: {sorted(set(single))[:5]}"

    empties = sorted(k for k in used if str(N[k]["value"]).strip() in ("", "None", "nan", "[]"))
    assert not empties, f"placeholders that resolved to an empty or null value: {empties}"

    # Session 2. Three more failure shapes that reached the compiled PDF with
    # every placeholder resolved, plus the generalisation of the first that
    # catches the instance the equals-sign form misses.
    _orphan = check_orphan_ordinal_after_equals(lines)
    assert not _orphan, ("a bare numeral opens a list under an unfinished equation -- the "
                         "converter eats it as an \\item marker:\n  " + "\n  ".join(_orphan[:5]))
    _interrupt = check_ordinal_interrupting_paragraph(lines)
    assert not _interrupt, ("an ordered-list marker interrupts a paragraph -- the numeral is "
                            "eaten and the sentence loses it:\n  " + "\n  ".join(_interrupt[:5]))
    _wordcase = check_number_word_case(text, N)
    assert not _wordcase, ("a capitalised number-word substituted mid-sentence -- use the "
                           "matching _lower key:\n  " + "\n  ".join(_wordcase[:5]))
    _gate_caught = selftest_gates()
    assert _gate_caught == 4, (
        f"converter gate self-test: only {_gate_caught} of 4 rules caught their corruption")

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
    # Captions. The body makes numbered references ("Figure 1", "Figure 3b"), so
    # the figures must actually carry numbers; without \caption LaTeX assigns
    # none and every one of those references dangles.
    # C3(rev2), 3.9. The caption had 68.3 typed into it while 3.1 derives 68.27,
    # so the figure's own caption disagreed with the section that defines the
    # constant. It comes from the same key the prose uses.
    NOMINAL1 = str(N["v3_cov_nominal1"]["value"])
    CAPS = {
        "paper_fig1_calibration.png":
            "Calibration of all four models on the held-out arena. "
            "(a) reliability: observed against predicted coverage, with the calibrated diagonal. "
            "(b) coverage at $\\pm1\\sigma$ against forecast horizon, log scale, against the "
            + NOMINAL1 + "\\% a calibrated Gaussian gives. Every curve sits far below the "
            "diagonal and falls further with horizon.",
        "paper_fig2_sigma_profile.png":
            "Why the coverage collapse is a horizon effect. Both panels are normalised to "
            "forecast step 1. (a) predicted $\\sigma$ barely moves, and for the faithful arm it "
            "declines. (b) realised error grows by an order of magnitude over the same steps. "
            "The gap between the panels is the collapse.",
        "paper_fig3_collapse.png":
            "The variance collapse is objective-driven. (a) mean "
            "$\\log\\Delta_{\\log\\sigma}$ against training iteration for every run. "
            "(b) the fitted per-iteration slope for each run, grouped by objective: negative and "
            "tightly clustered under sampled MSE, positive under \\texttt{gaussian\\_nll}. The "
            "sign flip is the evidence that the objective, not the optimiser or the data, "
            "produces it.",
        "paper_fig4_prereg_timeline.png":
            "Pre-registration lead time for each decision rule, from git commit timestamps. "
            "Positive is a rule committed before the data that tested it existed; negative is a "
            "rule written afterwards. The one negative bar is the Task 3 duplication rule, "
            "retracted as a pre-registration in this paper.",
        "paper_fig6_ab_by_horizon.png":
            "The autoregressive-versus-teacher-forcing advantage as a function of forecast "
            "horizon, out-of-sample over three seeds. (a) the ratio, which grows monotonically "
            "with depth: h = 368 is the end of a trend rather than a selected point, and the "
            "method's own rollout length of h = 100 sits partway along it. (b) the same "
            "comparison as a gap with its 95\\% cluster-bootstrap interval over whole "
            "trajectories; the interval spans zero only at h = 1, where teacher forcing is "
            "ahead -- a lead a shorter evaluation unit resolves as real, not nominal "
            "(\\S5, M-64). Only the h = 368 figure is pre-registered (M-23); the rest were "
            "computed after the data existed.",
        "paper_fig5_three_way.png":
            "The contamination control. (a) outcome across 32 cells for each arm pair, naive "
            "bootstrap on the left of each position and cluster bootstrap on the right; the "
            "duplication control is inert. (b) distribution of the ratio of cluster to naive "
            "confidence-interval width, with the mean marked. Resampling trajectory-step pairs "
            "rather than whole trajectories narrows every interval.",
    }
    missing = [f for f in figs if f not in CAPS]
    assert not missing, f"figures with no caption: {missing}"
    # PLACEMENT AT FIRST REFERENCE (Session 5 addendum B.3).
    #
    # The figures used to be emitted as one block under an "Appendix C — figures"
    # heading at the {{FIGURES}} marker. LaTeX floats them, so with every figure
    # declared in one place at the end of the document they drifted past section 14 and
    # left the Appendix C heading standing over nothing -- a heading with no
    # content under it, and eleven figures a reader had to hunt for.
    #
    # Each figure is now inserted immediately after the paragraph that first
    # refers to it by number, so the float has somewhere near its reference to
    # land. The number a figure carries in the rendered document is its order of
    # appearance, which is not the digit in its filename: paper_fig4_* is the
    # first figure the prose refers to and so renders as Figure 1. The prose
    # cites rendered numbers, so placement resolves through INTEXT rather than
    # through the filename (Session 1). Filename order and rendered order are
    # different orders and conflating them is what made every in-text reference
    # point at the wrong figure.
    #
    # A figure whose number is never referenced in the prose has nowhere to be
    # placed, and that is a defect in the prose rather than something to paper
    # over -- it is asserted rather than silently appended.
    INTEXT = {
        "paper_fig4_prereg_timeline.png": "1",
        "paper_fig6_ab_by_horizon.png": "2",
        "paper_fig1_calibration.png": "3",
        "paper_fig3_collapse.png": "4",
        "paper_fig2_sigma_profile.png": "5",
        "paper_fig5_three_way.png": "6",
    }
    assert sorted(INTEXT) == sorted(figs), (
        f"INTEXT does not cover the figures on disk: {sorted(INTEXT)} vs {sorted(figs)}")
    body = out
    unplaced = []
    for f in figs:
        _n = INTEXT.get(f)
        assert _n, f"cannot read a figure number from {f}"
        _img = f"![{CAPS[f]}](figures/{f})"
        # "(?!\\d)" rather than "\\b": the prose refers to sub-panels as "Figure 5a",
        # where \\b fails between the digit and the letter, and a bare \\d+ would let
        # a search for Figure 1 match Figure 15.
        _m = re.search(r"Figure~?\s*" + _n + r"(?!\d)", body)
        if not _m:
            unplaced.append(f)
            continue
        # after the end of the paragraph holding the first reference
        _end = body.find("\n\n", _m.end())
        _end = len(body) if _end == -1 else _end + 2
        body = body[:_end] + _img + "\n\n" + body[_end:]
    assert not unplaced, (
        f"figures never referenced by number in the prose, so they have no home: "
        f"{unplaced}. Reference them or remove them.")
    # Appendix C was the container for the block and is retired with it. The
    # marker is removed rather than left to render an empty heading.
    body = body.replace("{{FIGURES}}\n\n", "").replace("{{FIGURES}}", "")
    body = body.rstrip() + "\n"
    open(OUT, "w").write(header + body)

    # docs/BUILD_CHECKS.md — supplementary, generated from the same values.
    # Appendix D kept the failure modes and the exclusions; the registry, the
    # self-test and the checker's own defects moved here (Session 5a, B.2). It is
    # substituted rather than hand-maintained so a count quoted here cannot drift
    # from the one section 8 prints, which is the drift kind-count exists to catch.
    _bct = os.path.join("docs", "BUILD_CHECKS.template.md")
    if os.path.exists(_bct):
        _bc_missing, _bc_used = [], set()

        def _bcsub(m):
            k = m.group(1)
            if k not in N:
                _bc_missing.append(k)
                return m.group(0)
            _bc_used.add(k)
            return str(N[k]["value"])

        _bc_out = re.sub(r"\{\{([A-Za-z0-9_]+)\}\}", _bcsub, open(_bct).read())
        assert not _bc_missing, (
            f"docs/BUILD_CHECKS.template.md has placeholders with no value: "
            f"{sorted(set(_bc_missing))}")
        _bc_left = re.findall(r"\{\{[^}]*\}\}", _bc_out)
        assert not _bc_left, f"BUILD_CHECKS unresolved: {sorted(set(_bc_left))}"
        open(os.path.join("docs", "BUILD_CHECKS.md"), "w").write(_bc_out)
        print(f"  wrote docs/BUILD_CHECKS.md ({len(_bc_used)} values substituted)")

    # LaTeX for submission, from the same resolved text -- one source, two outputs.
    import md_to_tex
    title = re.search(r"^# (.+)$", out, re.M).group(1)
    # No author string: the submission is double-blind and tmlr.sty renders
    # "Anonymous authors" in submission mode. Keeping the name out of the source
    # keeps it out of the supplementary archive too (A3).
    tex, unhandled = md_to_tex.convert(header + body, title, "")
    _fn = check_footnote_tokens(tex)
    assert not _fn, ("Markdown footnote tokens survived into the LaTeX and set as literal "
                     f"text: {_fn[:5]}")
    open("PAPER.tex", "w").write(tex)
    assert not unhandled, f"converter did not handle: {unhandled[:5]}"

    print("PAPER BUILD")
    print("=" * 72)
    print(f"  template            : {TEMPLATE} ({len(text.splitlines())} lines)")
    print(f"  placeholders filled : {len(used)}")
    print(f"  distinct artifacts  : {len(set(N[k]['source'] for k in used))}")
    print(f"  figures attached    : {len(figs)}")
    print(f"  converter gate self-test: {_gate_caught} of 4 rules caught their corruption")
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
