"""
One definition of the template placeholder, shared by the paper build and every gate (round 5, G6 item 2).

    {{key}}       the key's value from results/paper_numbers.json, as stored
    {{key|sN}}    the same value with every decimal rendered to N significant figures (N = 1..9); signs, brackets,
                  %, ×, words and integers (with or without thousands separators) are left exactly as they are

A "decimal" is a number token with a decimal point, optionally in scientific notation (9.69e-05 rounds its mantissa
and keeps its exponent). Rounding is decimal half-up on the token's own digits, so 0.695|s2 is 0.70, never the binary
float's 0.69. A decimal whose value is zero is left unchanged. Version-like tokens (2.2.2) and identifiers are not
numbers and are untouched. The value is never retyped: the formatter only rounds what the artifact stored.

    python scripts/placeholders.py --self-test     the 20-value unit test
"""
import re
import sys
from decimal import ROUND_HALF_UP, Decimal

KEY = r"[A-Za-z0-9_]+"
# group 1: the key; group 2: N of |sN, or None
PH = re.compile(r"\{\{(" + KEY + r")(?:\|s([1-9]))?\}\}")
PH_SRC = r"\{\{(" + KEY + r")(?:\|s[1-9])?\}\}"          # for callers that build their own patterns
PH_ANY = re.compile(r"\{\{" + KEY + r"(?:\|s[1-9])?\}\}")
DOC_TEMPLATES = ("BUILD_CHECKS", "APPENDIX_G_VARIANCE_ARITHMETIC", "SUPPLEMENT")
SUPPLEMENT_TEMPLATE = "docs/SUPPLEMENT.template.md"
SUPPLEMENT = "docs/SUPPLEMENT.md"

_DEC = re.compile(r"(?<![\w.])(\d{1,3}(?:,\d{3})+|\d+)\.(\d+)(?:([eE])([+\-]?\d+))?(?![\w]|\.\d)")


def _round(int_part, frac, n):
    commas = "," in int_part
    d = Decimal(int_part.replace(",", "") + "." + frac)
    if d == 0:
        return None
    exp = d.adjusted()                                    # position of the leading digit
    q = Decimal(1).scaleb(exp - n + 1)                    # the unit of the N-th significant figure
    r = d.quantize(q, rounding=ROUND_HALF_UP)
    if r.adjusted() > exp:                                # 9.96|s2 -> 10.0 would carry a third figure
        q = Decimal(1).scaleb(exp - n + 2)
        r = d.quantize(q, rounding=ROUND_HALF_UP)
    s = format(r, "f") if q < 1 else format(r.quantize(Decimal(1)), "f")
    if commas:
        ip, _, fp = s.partition(".")
        s = f"{int(ip):,}" + ("." + fp if fp else "")
    return s


def sig(value, n):
    """Render every decimal in `value` (a string) to n significant figures."""
    def one(m):
        out = _round(m.group(1), m.group(2), n)
        if out is None:
            return m.group(0)
        return out + (m.group(3) + m.group(4) if m.group(3) else "")
    return _DEC.sub(one, str(value))


def render(value, n):
    return str(value) if n is None else sig(str(value), int(n))


def substitute(text, N, missing=None, used=None):
    """Replace every placeholder in `text` from N ({key: {"value": ...}}); unknown keys are left and recorded."""
    def sub(m):
        k = m.group(1)
        if k not in N:
            if missing is not None:
                missing.append(k)
            return m.group(0)
        if used is not None:
            used.add(k)
        return render(N[k]["value"], m.group(2))
    return PH.sub(sub, text)


SUPPLEMENT_MARK = "## Supplementary material (docs/SUPPLEMENT)"


def with_supplement(text, built=False):
    """`text` with the supplement appended under a marker heading, so a passage moved there stays in the same scan.
    built=False appends the template (beside PAPER.template.md), built=True the generated docs/SUPPLEMENT.md (beside
    PAPER.md). Line numbers past the marker are the supplement's, offset by the marker's line."""
    import os
    p = SUPPLEMENT if built else SUPPLEMENT_TEMPLATE
    if not os.path.exists(p):
        return text
    return text.rstrip("\n") + "\n\n" + SUPPLEMENT_MARK + "\n\n" + open(p).read()


CASES = [  # (value, N, expected)
    ("0.7532", 2, "0.75"), ("33.427", 2, "33"), ("144,632", 2, "144,632"), ("1,234.567", 3, "1,230"),
    ("[0.695, 0.823]", 2, "[0.70, 0.82]"), ("+0.2816 [+0.1978, +0.3896]", 2, "+0.28 [+0.20, +0.39]"),
    ("-14.4632", 3, "-14.5"), ("68.2%", 2, "68%"), ("4.61×", 2, "4.6×"), ("0.0020", 1, "0.002"),
    ("9.692e-05", 2, "9.7e-05"), ("1e-08", 2, "1e-08"), ("0.125", 2, "0.13"), ("9.96", 2, "10"),
    ("0.000", 2, "0.000"), ("PROPAGATION NARROWS THE GAP", 2, "PROPAGATION NARROWS THE GAP"),
    ("torch 2.2.2", 2, "torch 2.2.2"), ("h = 368", 2, "h = 368"), ("p = 0.001953125", 3, "p = 0.00195"),
    ("2ac8686c 3.16", 2, "2ac8686c 3.2"),
]


def self_test():
    bad = [(v, n, want, sig(v, n)) for v, n, want in CASES if sig(v, n) != want]
    m = PH.fullmatch("{{x9_rel_f_h100_ci|s2}}")
    ok_ph = bool(m and m.group(1) == "x9_rel_f_h100_ci" and m.group(2) == "2" and PH.fullmatch("{{a_b}}").group(2) is None
                 and not PH.fullmatch("{{a|s0}}") and not PH.fullmatch("{{a|x2}}"))
    N = {"k": {"value": "0.7532 [0.6950, 0.8230]"}}
    ok_sub = substitute("v {{k}} / {{k|s2}}", N) == "v 0.7532 [0.6950, 0.8230] / 0.75 [0.70, 0.82]"
    return not bad and ok_ph and ok_sub, bad, ok_ph, ok_sub


if __name__ == "__main__":
    ok, bad, ok_ph, ok_sub = self_test()
    for v, n, want, got in bad:
        print(f"  FAIL {v!r}|s{n}: want {want!r}, got {got!r}")
    print(f"  placeholder pattern: {'ok' if ok_ph else 'FAIL'}; substitution: {'ok' if ok_sub else 'FAIL'}")
    print(f"  {len(CASES) - len(bad)}/{len(CASES)} display-precision cases pass")
    sys.exit(0 if ok else 1)
