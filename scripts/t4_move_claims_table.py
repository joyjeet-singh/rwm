"""
T4 -- move the claims table to an appendix and leave a prose summary in the body.

Section 4 is currently a wall: eleven table rows, several of them a paragraph
long, in the third section a reviewer reads. The information is worth keeping and
the placement is not. This moves the table to Appendix C and leaves six lines of
prose saying what we tested, what we did not, and the fact that the original gives
no quantitative figure for any of the four we did test.

Appendix C is chosen because the paper already has A, B, D and E and no C -- the
lettering was left with a gap. Nothing is renumbered.

Mechanical: the table rows and the version note move verbatim. Only the framing
prose is rewritten, and no numeric placeholder is added or removed, so the build's
placeholder accounting is unchanged.
"""
import re
import shutil
import sys

TEMPLATE = "PAPER.template.md"

BODY = """A reproduction that does not say what it left alone invites the reader to assume it tested
everything. It did not.

**We tested four claims and left eight untested.** The four are the base paper's autoregressive
-versus-teacher-forcing comparison and its claim that teacher forcing generalises poorly
(§5), and the follow-up's two claims about what its uncertainty outputs report (§6). The eight we
did not test are, without exception, claims about **policy learning or hardware**: zero-shot
transfer, the sample-efficiency result, the comparisons against SHAC and Dreamer, generality
across robot morphologies, and the core claim that penalising rewards by disagreement improves the
learned policy. Each needs a simulator, an RL loop and an ANYmal; this work trains no policy at
all. §12 states what that bounds, and Appendix E sets out what testing them would take.

**For all {{orig_n_tested}} of the claims we did test, the original reports no quantitative
figure.** Each is asserted qualitatively and shown in a plot; none is given a number in text,
caption or table. So our {{d1_ratio}}× is neither a confirmation of a published figure nor a
contradiction of one — it is the first figure attached to the claim, and the same is true of the
follow-up's "strong correlation" between disagreement and error, for which §6.7 supplies the first
coefficient. Where a magnitude is legible only from a plotted curve we say so rather than
estimating it from the axis.

**Appendix C gives the full table**, claim by claim, with what the original states, where it
states it, and our verdict.

---
"""

APPENDIX_HEAD = """## Appendix C — every claim of the originals, and what we did with it

The body's §4 summarises this table. It is here in full because the third column — what the
original actually reports — is the answer to a question a reader of any reproduction should ask,
and because "no quantitative figure" is itself a finding that deserves to be checkable row by row.

*Section references follow arXiv:2501.10100**v1**, which uses Roman-numeral sectioning. v2
renumbered to Arabic and moved IV-C's material into Appendix A.4.1. References to
arXiv:2504.16680 follow **v1**, which is the version we read; it is now at
{{v4_current}} ({{v4_current_date}}), where §5.1 and Eq. 4–5 keep their numbers but every figure
and appendix table has moved — {{v2_fig_v1}} became {{v2_fig_v3}}, and the model was renamed
RWM-O to RWM-U. All locations are recorded in `results/original_paper_figures.json`.*

"""


def main():
    write = "--write" in sys.argv
    t = open(TEMPLATE).read()

    # ---- locate section 4's body: from its heading to the next H2 -----------
    m = re.search(r"^## 4\. What the original papers claim, and which claims we test\s*$",
                  t, re.M)
    assert m, "section 4 heading not found"
    start = m.end()
    nxt = t.find("\n## ", start)
    assert nxt > 0, "no section after 4"
    sec4 = t[start:nxt]

    # ---- split it: the table (and its version note) versus the framing ------
    vn = sec4.find("*Section references follow")
    assert vn > 0, "version note not found in section 4"
    table = sec4[vn:].rstrip()
    # the table must end with the last row, not a trailing rule
    table = re.sub(r"\n-{3,}\s*$", "", table).rstrip()
    n_rows = len([l for l in table.split("\n")
                  if l.startswith("|") and not re.match(r"^\|[\s-]+\|", l)])
    assert n_rows >= 10, f"expected the full claims table, found {n_rows} rows"
    print(f"  claims table: {n_rows} rows (including the header)")

    # ---- rebuild section 4 with the prose summary --------------------------
    new_sec4 = "\n" + BODY
    t = t[:start] + new_sec4 + t[nxt:]

    # ---- insert Appendix C before Appendix D -------------------------------
    d = t.find("## Appendix D —")
    assert d > 0, "Appendix D not found"
    appendix = APPENDIX_HEAD + table.split("*\n", 1)[-1].lstrip() + "\n\n---\n\n"
    t = t[:d] + appendix + t[d:]

    body_lines = len(BODY.strip().split("\n"))
    print(f"  body summary: {body_lines} lines, "
          f"{len(BODY.split())} words")
    print(f"  appendix C:   {len(appendix)} chars")

    if not write:
        print("  DRY RUN — re-run with --write")
        return
    shutil.copy(TEMPLATE, TEMPLATE + ".t4bak")
    open(TEMPLATE, "w").write(t)
    print(f"  wrote {TEMPLATE}")


if __name__ == "__main__":
    main()
