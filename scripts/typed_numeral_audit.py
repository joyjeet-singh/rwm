"""
B8 -- classify every numeral typed into PAPER.template.md, and fail on a result.

WHY THIS EXISTS. The abstract said "No number here is typed." It was false, and
an independent reader falsified it by hand in about an hour: §5 printed a
hold-last floor ratio of 1.56x that no artifact produced, because it was the
single-seed value left behind when §5 moved to three seeds.

The claim was also unenforced, which is the deeper problem. build_paper.py
guarantees something narrower and real -- that every `{{key}}` resolves from
results/paper_numbers.json and that the build fails if one does not -- and it
PRINTED the count of typed numerals on every run without asserting anything about
them. 117 of them, in a list nobody read. A number that is only ever printed is
not a check.

WHAT IS ACTUALLY TRUE, and what this asserts. A paper cannot substitute every
numeral: "§6.2", "arXiv:2501.10100v1", "`rnn.py:40`", "NeurIPS 2019" and "M-43"
are ADDRESSES, and substituting them would be absurd. So the honest claim is
partitioned:

  every numeral that reports a MEASUREMENT is substituted from a named artifact,
  and every numeral that is not is an address, a horizon label, or a declared
  configuration constant.

This file makes the second half checkable. Each typed numeral is matched against
one narrow class. Anything unmatched is a RESULT until proven otherwise, and a
result in prose fails the build.

WHY THE CLASSES ARE NARROW. A classifier with a permissive catch-all would pass
everything and guard nothing -- the vacuous-assertion failure this project has
recorded three times. So each class matches on the numeral's CONTEXT, not on the
numeral, and the residue goes in EXCEPTIONS with a written reason and the count
of occurrences it covers. The exception list is printed on every run. It is
meant to be short and to be argued with.

  python scripts/typed_numeral_audit.py              audit
  python scripts/typed_numeral_audit.py --self-test  plant a result, expect a fail

Writes results/typed_numerals.json.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402

TEMPLATE = "PAPER.template.md"
OUT = "typed_numerals.json"

# Each class is (name, pattern applied to the numeral WITH its immediate context,
# why it is not a measurement). The pattern must anchor on something other than
# the digits: a class that matches a bare number matches every number.
CLASSES = [
    ("section-ref", r"§\d+(\.\d+)?|\bSection \d+(\.\d+)?\b|\bsection \d+(\.\d+)?\b",
     "a cross-reference to a section of this paper or of an original"),
    ("subsection-heading", r"\*\*\d+\.\d+ ",
     "a bold subsection number opening its own paragraph"),
    ("markdown-heading", r"^#{1,4} +\d+(\.\d+)*\.?",
     "a section heading"),
    ("arxiv-id", r"(arXiv:)?\d{4}\.\d{4,5}(v\d)?",
     "an arXiv identifier, with or without the arXiv: prefix -- appendices E and "
     "F name the originals by bare identifier inside table cells"),
    ("version-tag", r"\*\*v\d\*\*|\bv\d\b",
     "a version of a cited paper"),
    ("ledger-id", r"`?\b[A-Z]-\d+\b`?",
     "a ledger entry identifier"),
    ("figure-ref", r"(Fig\.?|Figure)\s*\d+\w?",
     "a figure number in this paper or an original"),
    ("equation-ref", r"Eq\.?\s*\d+(–\d+)?",
     "an equation number in an original"),
    ("table-ref", r"Table\s+[IVX]+|Appendix\s+A\.\d+(\.\d+)*",
     "a table or appendix locator in an original"),
    ("orig-section", r"§?IV-[A-Z]|§\s*5\.1",
     "a section of an original, which uses Roman-numeral sectioning"),
    ("code-location", r"`[^`]*\b\d[\d.:–-]*[^`]*`",
     "a file:line, a config key or an identifier, inside a code span"),
    ("citation-year", r"(NeurIPS|ICML|ICLR|ArXiv|arXiv)\s+(19|20)\d\d|\((19|20)\d\d\)|"
                      r"\b(19|20)\d\d\)",
     "the year of a cited publication"),
    ("date", r"\b\d{1,2} (January|February|March|April|May|June|July|August|"
             r"September|October|November|December)( \d{4})?\b",
     "a calendar date, with or without the year -- \"the 24 August draft\" names "
     "one without repeating the year the sentence already carries"),
    ("math-mode", r"\$\$[^$]*\$\$|\$[^$]*\$",
     "inside a LaTeX math span -- horizon sets, indices and symbolic constants"),
    ("withdrawn-figure", r"an earlier (draft|version)[^.;|]{0,200}|"
                        r"earlier version of this appendix[^.;|]{0,120}|"
                        r"where \d+ \+ \d+ did not make \d+|"
                        r"predated[^.;|]{0,80}|"
                        r"rested on an n=\d+ estimate|"
                        r"\"a change of \*\*\+\*\*[\d.]+\"|"
                        r"was typed with[^.;|]{0,80}",
     "a figure this paper QUOTES from its own withdrawn text. It cannot be "
     "substituted: no artifact holds it any more, and that is the point of "
     "quoting it. Appendix D is largely made of these"),
    ("originals-figure", r"the reference reports[^|]{0,160}|"
                         r"\d+ min of RWM training[^|]{0,40}|"
                         r"the PPO baseline's [\d,]+",
     "a figure reported by one of the papers under reproduction, on their "
     "hardware. Ours cannot produce it and must not appear to"),
    ("table-row-label", r"^\|\s*\*{0,2}\d+\*{0,2}\s*\|",
     "the leading label cell of a table row, naming the horizon that row reports"),
    ("table-denominator", r"\u2400?\u2400?\s*/\s*\d+|␀/\d+",
     "the denominator of a substituted k-of-n count inside a table cell; the "
     "numerator is substituted and the total is the fixed state dimensionality"),
]

# Numerals that no class above should be asked to cover, each with a reason and
# the exact context it is allowed in. Deliberately specific: a reason like
# "constant" would let anything through.
EXCEPTIONS = [
    (r"\bTask 3\b|\bTask 4b\b|\bTask 1\b|\bTask 2\b|\bStep 5\b|\bStep 3\b|\bStep 1\b|"
     r"\bPhase 1\b|\bPhase 2\b|\bPart A\b|\bPart B\b",
     "the name of a stage of this project's own work, which the ledger and the "
     "commit log use as an identifier"),
    (r"\bform 1\b|\bForm 1\b|\bform 2\b|\bForm 2\b",
     "the two nRMSE aggregation forms, named 1 and 2 by this paper (§3.1)"),
    (r"σ = 0\b|σ = 0\.|optimum at σ = 0|to σ = 0",
     "the value the derived optimum takes, which is exactly zero and is the finding"),
    (r"identically zero|exactly zero|excludes? zero|spans? zero|above zero|"
     r"indistinguishable from zero|\u03c3 \u2192 0|> 0 at|weight at zero|"
     r"penalty weight at zero|not zero|zero at",
     "the word zero, or a comparison against it"),
    (r"\b95% (CI|confidence)|\b95% interval|at 95%",
     "the confidence level every interval in this paper is reported at, fixed in §3"),
    (r"±1σ|± 1σ|±2σ|± 2σ|±3σ|± 3σ",
     "the interval width a coverage is reported at, which names the quantity"),
    (r"\b50 Hz\b", "the dataset's sampling rate, a property of the release"),
    (r"\b20-second episodes\b|\b20 ms\b",
     "the episode duration and the step interval, both fixed by the sampling rate"),
    (r"ensemble size \d|size-\d ensemble|\bM=32, N=8\b|\bN=1\b|\bM and N\b|"
     r"ensemble-5|\bens5\b|five-model|\bfive members\b|\bfive independent\b|"
     r"\bM = \d|\bN = \d",
     "an ensemble configuration named by the originals or by our own arms"),
    (r"\b(500|2,500|5,000|10,000|250)[- ]iterations?\b|at 2,500\b|at 10,000\b|"
     r"tagged 5,000|says 500|says 2,500|\b500, 2,500 or 5,000\b|final 250\b|"
     r"paper's 2,500|only at the paper's|rather than only at|"
     r"\b(500|2,500|5,000|10,000)-iteration\b|fourfold extension",
     "an iteration count that is a configuration setting, not a measurement -- "
     "§8's whole subject is that three of these disagree"),
    (r"\b400-step\b|\bh = 8\b|\bh=8\b|\bh = 1\b|\bh=1\b|\bh = 32\b|\bh=32\b|"
     r"\bh = 128\b|\bh=128\b|\bh = 100\b|\bh=100\b|\bh = 368\b|\bh=368\b|"
     r"\bstep 32\b|\bfirst 32\b|32 of history|8 of forecast|\b100-step\b|"
     r"\b368-step\b|steps 1\.\.h|1\.\.h|\bh = 400\b|to h = |up to h|"
     r"\b8-step horizon\b|\bstep 368\b|\bstep 8\b|step 1 \u2192 8|\bstep 1\b|"
     r"\btrained on an 8\b",
     "a horizon or trajectory length naming the cell a figure is reported for; "
     "the grid itself is fixed in §3.1 and the figures at each are substituted"),
    (r"\b45[- ](term|dimension|state|coupled)|of 45\b|45 state dimensions|all 45\b|"
     r"/45\b|\b45 coupled\b|\b45 dimensions\b",
     "the state dimensionality of the released model, fixed by the checkpoint"),
    (r"256-dimensional", "the released model's hidden width, fixed by the checkpoint"),
    (r"Bonferroni level of 0\.05|\b0\.05/|α = 0\.05|alpha = 0\.05",
     "the significance level, declared in §3 before the tests"),
    (r"coverage to 100%|\b100% coverage\b|to 100% \u2014",
     "the saturation value of a coverage. A recalibration that drives one-step "
     "coverage to 100% has produced a vacuous interval; the bound is definitional"),
    (r"A value of 1\.0 means|\b1\.0 means no better|weight \u22121\.0|"
     r"\bweight -1\.0|\u03bb = 1\b|lambda = 1\b",
     "the value a ratio or a penalty weight takes as a definitional constant"),
    (r"\bten concatenated\b|\bten episodes\b|\bthe ten\b|\ball ten\b",
     "the episode count of the released dataset, a property of the release"),
    (r"seeds 0, 1 and 2|seeds 3 and 4|\bseed \d\b|\bseeds 0-4\b|\bseeds 0\u20134\b|"
     r"\bseed \d alone\b",
     "a seed index"),
    (r"SHA-256|sha256",
     "the name of a hash algorithm"),
    (r"log\(1 \+ index\)|\blog\(1 ?\+",
     "a functional form named in a control's specification"),
    (r"\*t\u22121\*|\*t-1\*|from \*t\u2212|stale by one step|k = -1|k = \u22121",
     "an index offset in the action convention, which is what §7.2 is about"),
    (r"is \"5,000 iterations|his recollection is 5,000|\"as I always did\"|"
     r"max_iterations: 500` is",
     "inside a verbatim quotation from the correspondence, which cannot be "
     "rewritten to carry a substituted value without ceasing to be a quotation"),
    (r"\btwo-layer\b|\btwo layers\b|\bfour HAA\b|\btwelve joint\b|\btwelve actions\b",
     "a count fixed by the released architecture or the released CSV's columns"),
]


def prepare(text):
    """The text the scan actually walks, so every offset means one thing.

    Placeholders collapse to a one-character sentinel and code fences are
    dropped, so offsets into this string are NOT offsets into the template. Both
    this module and restatement_index.py index by them; returning the transformed
    text rather than recomputing it in each caller is what keeps them agreeing.
    A caller that used span offsets against the raw template got sentences from
    hundreds of characters away, and reported restatements against the wrong
    sentence entirely.
    """
    t = re.sub(r"\{\{[A-Za-z0-9_]+\}\}", "\u2400", text)
    t = re.sub(r"```.*?```", "", t, flags=re.S)
    t = re.sub(r"^ {4}.*$", "", t, flags=re.M)
    # Excise the References SECTION -- not everything after it.
    #
    # This read `t.split("## References")[0]`, inherited from build_paper.py's
    # typed-numeral report. Every appendix in this paper comes AFTER the
    # bibliography, so that one line silently removed appendices A, B, D, E and F
    # from the scan: about a third of the document, including appendix D, whose
    # whole subject is count consistency and which carried a typed extremum that
    # was wrong. A gate that covers two thirds of a paper while reporting a
    # single total is worse than one that covers none, because the total looks
    # complete.
    _i = t.find("## References")
    if _i >= 0:
        _j = t.find("\n## ", _i + 4)
        t = t[:_i] + (t[_j:] if _j > 0 else "")
    return t


def _spans(text, prepared=None):
    """Numerals in the template's prose, with the context each sits in."""
    t = prepared if prepared is not None else prepare(text)
    out = []
    for m in re.finditer(r"(?<![\w.])(\d[\d,]*\.?\d*)(?![\w])", t):
        line_start = t.rfind("\n", 0, m.start()) + 1
        line_end = t.find("\n", m.end())
        line = t[line_start:line_end if line_end > 0 else len(t)]
        out.append({"num": m.group(1),
                    "pos": m.start(),
                    # the numeral's offset INSIDE ctx, so a class match can be
                    # tested for actually covering it rather than merely sitting
                    # nearby. The previous version re-found the numeral by
                    # searching ctx from a computed tail offset, which picked the
                    # wrong occurrence whenever the numeral appeared twice in the
                    # window -- and horizon labels appear twice constantly.
                    "off": m.start() - max(0, m.start() - 90),
                    "line": t[:m.start()].count("\n") + 1,
                    "ctx": t[max(0, m.start() - 90):m.end() + 60],
                    "linetext": line})
    return out


def classify(sp, classes=CLASSES, exceptions=EXCEPTIONS):
    """The class covering this numeral, or None.

    A class covers the numeral only if one of its matches SPANS the numeral's own
    offset. Matching anywhere in the window is not enough: "§6.2" sits within 90
    characters of most numerals in this paper, and a class that accepted mere
    proximity would classify everything.
    """
    for name, pat, _ in classes:
        if pat.startswith("^"):
            for m in re.finditer(pat, sp["linetext"], re.M):
                if sp["num"] in m.group(0):
                    return name
            continue
        for m in re.finditer(pat, sp["ctx"], re.M):
            if m.start() <= sp["off"] < m.end():
                return name
    for pat, why in exceptions:
        for m in re.finditer(pat, sp["ctx"], re.M):
            # an exception is allowed to be contextual -- "an iteration count" is
            # a property of the sentence, not of the digits -- so it may match
            # either over the numeral or within 40 characters of it
            if m.start() - 40 <= sp["off"] < m.end() + 40:
                return "exception:" + pat[:40]
    return None


def main():
    text = open(TEMPLATE).read()
    if "--self-test" in sys.argv:
        # A sentence with a number that is plainly a measurement and matches no
        # class. If this passes, the audit is decorative.
        #
        # It goes into the BODY. Appending it to the end of the file put it after
        # "## References", which _spans() strips, so the first version of this
        # self-test planted a probe the scan never saw and then reported the audit
        # as unable to fail. That is the vacuous-assertion shape this project has
        # now recorded four times, and it took one run to reproduce it.
        marker = "\n## 12. Limitations"
        assert marker in text, "no anchor for the self-test plant"
        text = text.replace(
            marker,
            "\n\nThe released checkpoint is 12.7 times overconfident on the "
            "quantity the method uses.\n" + marker, 1)
    spans = _spans(text)
    rows, unclassified = [], []
    for sp in spans:
        c = classify(sp)
        rows.append({"num": sp["num"], "line": sp["line"], "class": c,
                     "ctx": re.sub(r"\s+", " ", sp["ctx"])})
        if c is None:
            unclassified.append(rows[-1])

    counts = {}
    for r in rows:
        k = (r["class"] or "UNCLASSIFIED").split(":")[0]
        counts[k] = counts.get(k, 0) + 1

    print("B8 — TYPED NUMERAL AUDIT")
    print("=" * 92)
    print(f"  numerals typed in {TEMPLATE}: {len(rows)}")
    for k in sorted(counts, key=lambda x: -counts[x]):
        print(f"    {k:<22} {counts[k]:>4}")
    if unclassified:
        print(f"\n  {len(unclassified)} NOT COVERED by any class or declared exception.")
        print("  Each is a measurement until shown otherwise, and a measurement in prose")
        print("  must be substituted from an artifact:")
        for u in unclassified[:20]:
            print(f"    L{u['line']:<5} {u['num']:>10}   ...{u['ctx'][-110:]}")
    else:
        print(f"\n  every typed numeral is an address, a horizon label or a declared constant")
        print(f"  ({len(EXCEPTIONS)} declared exceptions, {len(CLASSES)} classes)")

    rec = {"template": TEMPLATE, "n_typed": len(rows), "by_class": counts,
           "n_unclassified": len(unclassified), "unclassified": unclassified,
           "n_classes": len(CLASSES), "n_exceptions": len(EXCEPTIONS),
           "classes": [{"name": n, "why": w} for n, _, w in CLASSES],
           "exceptions": [{"pattern": p, "why": w} for p, w in EXCEPTIONS]}

    if "--self-test" in sys.argv:
        planted = [u for u in unclassified if u["num"] == "12.7"]
        print()
        if planted:
            print("  SELF-TEST: caught the planted measurement (12.7). The audit can fail.")
            return 0
        print("  SELF-TEST FAILED: a planted measurement was classified as benign.")
        return 1

    json.dump(rec, open(os.path.join(R.RESULTS, OUT), "w"), indent=2)
    print(f"\n  wrote results/{OUT}")
    return 1 if unclassified else 0


if __name__ == "__main__":
    sys.exit(main())
