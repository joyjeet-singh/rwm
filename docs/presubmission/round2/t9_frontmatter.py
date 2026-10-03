"""Round 2, T9 item 2, the mechanical half: does every number in the front matter appear in the body?

Front matter (PLAN T9): the abstract, the contributions, §3.2, §4, §9, §11 and §12.
Body: §2, §3 and §3.1, §5-§8, §10 and "Data and code". Appendices are reported separately.

Two levels:
  keys     every {{key}} in a front-matter section, looked up in the body's keys, then by rendered
           value among the body's keys, then in the appendices;
  numerals every numeric token in the RENDERED front-matter section (PAPER.md), looked up as a
           token in the rendered body. This is what catches §3.2, whose table is one generated key.
Writes nothing; prints a report. Read-only.
"""
import json
import re
import sys

ROOT = __file__.rsplit("/docs/", 1)[0]
T = open(f"{ROOT}/PAPER.template.md").read()
P = open(f"{ROOT}/PAPER.md").read()
N = json.load(open(f"{ROOT}/results/paper_numbers.json"))
N = N.get("values", N)


def sections(text):
    """Split at '## ' and '### ' headings -> list of (heading, body)."""
    out, head, buf = [], "PREAMBLE", []
    for ln in text.split("\n"):
        if ln.startswith("## ") or ln.startswith("### "):
            out.append((head, "\n".join(buf)))
            head, buf = ln, []
        else:
            buf.append(ln)
    out.append((head, "\n".join(buf)))
    return out


def contributions(sec1):
    i = sec1.index("**Contributions.**")
    lines, out, seen_bullet = sec1[i:].split("\n"), [], False
    for k, ln in enumerate(lines):
        if ln.startswith("- "):
            seen_bullet = True
        if seen_bullet and ln.strip() == "" and k + 1 < len(lines) and lines[k + 1].strip() \
                and not lines[k + 1].startswith("- "):
            break
        out.append(ln)
    return "\n".join(out)


def split(text):
    secs = sections(text)
    get = lambda pref: "\n".join(b for h, b in secs if h.startswith(pref))  # noqa: E731
    front = {
        "abstract": get("## Abstract"),
        "contributions": contributions(get("## 1. Introduction")),
        "3.2": get("### 3.2"),
        "4": get("## 4."),
        "9": get("## 9."),
        "11": get("## 11."),
        "12": get("## 12."),
    }
    body = "\n".join(b for h, b in secs if re.match(
        r"## (2|3|5|6|7|8|10)\.|### (3\.1|5\.|6\.|7\.)|## Data and code", h))
    appx = "\n".join(b for h, b in secs if h.startswith("## Appendix"))
    return front, body, appx


fT, bT, aT = split(T)
fP, bP, aP = split(P)
KEY = re.compile(r"\{\{(\w+)\}\}")
NUM = re.compile(r"(?<![\w.])[-+−]?\d[\d,]*(?:\.\d+)?(?![\w])")


def toks(s):
    return set(x.replace("−", "-").lstrip("+").rstrip(",") for x in NUM.findall(s))


bkeys, akeys = set(KEY.findall(bT)), set(KEY.findall(aT))
bvals = {str(N[k]["value"]) for k in bkeys if k in N}
btok, atok = toks(bP), toks(aP)
report = {}
for name in fT:
    ks = sorted(set(KEY.findall(fT[name])) - {"FIGURES"})
    rows = []
    for k in ks:
        if k in bkeys:
            continue
        v = str(N[k]["value"]) if k in N else "?"
        where = ("BODY-BY-VALUE" if v in bvals else "APPENDIX-ONLY" if k in akeys else "NOT IN BODY")
        rows.append((k, v[:70], where))
    nt = sorted(t for t in toks(fP[name]) - btok)
    report[name] = {"n_keys": len(ks), "keys_not_in_body": rows,
                    "numerals_not_in_body": [(t, "appendix" if t in atok else "nowhere") for t in nt]}

for name, r in report.items():
    print(f"== {name}: {r['n_keys']} keys")
    for k, v, w in r["keys_not_in_body"]:
        print(f"   key {k:32s} {w:14s} {v}")
    for t, w in r["numerals_not_in_body"]:
        print(f"   numeral {t:12s} rendered, not in body ({w})")
if "--json" in sys.argv:
    print(json.dumps(report, indent=1))
