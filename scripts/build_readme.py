"""
C2 -- build README.md from README.template.md, using the paper's own substitution.

The public README was materially behind the paper: 17 training runs against 24,
4,804 regenerated values against 6,073, 19 artifacts against 29, a headline the
paper had reframed, and -- the one that mattered -- an assertion §8 had explicitly
narrowed still standing as a finding. None of that was a mistake anyone made; it
is what happens when two documents state the same numbers and only one of them is
generated.

So the README is generated too, from the same `results/paper_numbers.json`, and
the `cross-artifact-sync` check in scripts/check_comparative_claims.py asserts
that the headline values actually appear in it.

Same contract as build_paper.py: a placeholder with no value, or a leftover
placeholder, fails the build rather than shipping.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402

TEMPLATE = "README.template.md"
OUT = "README.md"


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

    # The same typed-number surfacing build_paper.py does. A README is prose, so
    # some numerals are legitimate (version pins, commit prefixes, licence
    # names); listing them every build means a typed result number has to be
    # looked at rather than assumed benign.
    prose = re.sub(r"\{\{[A-Za-z0-9_]+\}\}", "", text)
    prose = re.sub(r"```.*?```", "", prose, flags=re.S)
    prose = re.sub(r"<!--.*?-->", "", prose, flags=re.S)
    typed = sorted({m.group(1) for m in
                    re.finditer(r"(?<![\w.])(\d[\d,]*\.?\d*)(?![\w])", prose)},
                   key=lambda x: (len(x), x))

    with open(OUT, "w") as f:
        f.write(out)

    print("README BUILD")
    print("=" * 72)
    print(f"  template            : {TEMPLATE} ({len(text.splitlines())} lines)")
    print(f"  placeholders filled : {len(used)}")
    print(f"  distinct artifacts  : {len(set(N[k]['source'] for k in used))}")
    print(f"  numerals typed in prose : {len(typed)}  {', '.join(typed)}")
    print(f"  wrote {OUT} ({len(out.splitlines())} lines)")


if __name__ == "__main__":
    main()
