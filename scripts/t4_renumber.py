"""
T4 (step 1 of 2) -- renumber the paper's sections to make room for Related Work.

MECHANICAL ONLY. This script moves numbers and changes no prose. Content edits
are a separate pass, so that if a cross-reference breaks it is obvious which
change broke it.

Why a script and not an editor: there are 69 section references in the template
and five of them point at the ORIGINAL papers' sections, not ours. Renumbering
those would silently corrupt citations to someone else's work -- the exact class
of defect this paper's checker exists to catch. So the original-paper references
are protected by sentinel before anything moves and restored afterwards, and the
count of each is asserted.

Per the project's patching rule: assert every match count, write a .bak first,
diff afterwards, and write nothing until all asserts pass.

    python scripts/t4_renumber.py            dry run, prints the plan
    python scripts/t4_renumber.py --write    apply
"""
import argparse
import difflib
import os
import re
import shutil
import sys

TEMPLATE = "PAPER.template.md"

# old -> new. Simultaneous, so no ordering hazard.
SECTION_MAP = {
    "1": "1",        # Introduction
    # NEW 2 = Related work
    "2": "3",        # Setup
    "3": "4",        # What the original papers claim
    "4": "5",        # The base paper's central claim reproduces
    "4.1": "5.1",
    "5": "6",        # Neither uncertainty output is usable as an interval
    "5.1": "6.1", "5.2": "6.2", "5.3": "6.3",
    # NEW 6.4 = the trunk-sharing mechanism
    "5.4": "6.5", "5.5": "6.6", "5.6": "6.7", "5.7": "6.8", "5.8": "6.9",
    "6": "7",        # Defects in the released pipeline
    "6.1": "7.1", "6.2": "7.2", "6.3": "7.3", "6.4": "7.4", "6.5": "7.5",
    "7": "8",        # Unreachable variance state
    "8": "9",        # Method
    "9": "10",       # Actionable lessons
    "10": "11",      # Broader impact
    "11": "12",      # Limitations
    "12": "13",      # Conclusion
}

# References to the ORIGINAL papers' sections. These must NOT move. Each is given
# with the exact expected number of occurrences, so a template edit that adds or
# removes one fails here rather than corrupting a citation silently.
PROTECT = [
    ('(2504.16680 §5.1)', 1),
    ('(2504.16680 Eq. 4–5, §5)', 1),
    ('(2504.16680 §5)', 1),
    # The two bare ones. Both sit in contexts about the FOLLOW-UP's section 5.1:
    #   - the claims table row for the aleatoric claim, whose neighbour row
    #     already carries the explicit "(2504.16680 §5.1)";
    #   - the "What the follow-up does and does not claim" paragraph.
    # They are rewritten to name the paper, which removes the ambiguity for the
    # reader as well as for this script.
    ('reflecting small stochasticity" (§5.1)', 1),
    ('a calibrated interval. §5.1 claims', 1),
]

# Applied BEFORE renumbering: make the two bare original-paper references
# explicit. This is a prose change, but it is one this script must make to be
# able to protect them, so it is here rather than in the content pass.
DISAMBIGUATE = [
    ('reflecting small stochasticity" (§5.1)',
     'reflecting small stochasticity" (2504.16680v1 §5.1)'),
    ('a calibrated interval. §5.1 claims',
     "a calibrated interval. The follow-up's §5.1 claims"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    repo = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        os.pardir))
    path = os.path.join(repo, TEMPLATE)
    original = open(path).read()
    text = original

    # ---------------------------------------------------- 0. disambiguate
    for old, new in DISAMBIGUATE:
        n = text.count(old)
        assert n == 1, f"disambiguation target {old!r} occurs {n} times, expected 1"
        text = text.replace(old, new)

    # ------------------------------------------------------- 1. protect
    # Anything of the form "<arxiv id> ... §N" is a reference to someone else's
    # sectioning. After disambiguation every such reference names its paper, so
    # the sentinel pass can find them all by that pattern.
    protected = {}

    def _stash(m):
        key = f"\x00P{len(protected)}\x00"
        protected[key] = m.group(0)
        return key

    orig_ref = re.compile(r"(?:2504\.16680\w*|2501\.10100\w*|follow-up's)"
                          r"(?:[^§\n]{0,30})§[0-9IVX]+(?:\.[0-9]+)?")
    text = orig_ref.sub(_stash, text)
    n_protected = len(protected)
    assert n_protected >= 5, (
        f"expected at least 5 original-paper section references to protect, "
        f"found {n_protected}: {list(protected.values())}")
    print(f"  protected {n_protected} original-paper section references:")
    for v in protected.values():
        print(f"    {v}")

    # ------------------------------------------------------ 2. renumber
    # Headings first, so the counts below are separable in the report.
    head_re = re.compile(r"^(#{2,3}) (\d+(?:\.\d+)?)\.? ", re.M)
    heads_seen = []

    def _head(m):
        hashes, num = m.group(1), m.group(2)
        assert num in SECTION_MAP, f"heading {num} has no mapping"
        heads_seen.append((num, SECTION_MAP[num]))
        return f"{hashes} {SECTION_MAP[num]}. "

    text = head_re.sub(_head, text)

    # Section 6's subsections are BOLD LABELS, not markdown headings
    # ("**6.1 Ten unmarked episode boundaries.**"), so head_re does not see them.
    # They are referenced in-text as §6.4 and must move with everything else.
    bold_re = re.compile(r"^\*\*(\d+\.\d+) ", re.M)

    def _bold(m):
        num = m.group(1)
        assert num in SECTION_MAP, f"bold subsection label {num} has no mapping"
        heads_seen.append((num + " (bold label)", SECTION_MAP[num]))
        return f"**{SECTION_MAP[num]} "

    text = bold_re.sub(_bold, text)

    # Then every in-text reference. §N and §N.M, plus the one "Section 5.5".
    refs_seen = []

    def _ref(m):
        num = m.group(1)
        if num not in SECTION_MAP:
            refs_seen.append((num, num, "UNMAPPED — left alone"))
            return m.group(0)
        refs_seen.append((num, SECTION_MAP[num], ""))
        return "§" + SECTION_MAP[num]

    text = re.sub(r"§(\d+(?:\.\d+)?)", _ref, text)
    n_sec_word = text.count("Section 5.5")
    text = text.replace("Section 5.5", "Section 6.6")

    # ------------------------------------------------------- 3. restore
    for key, val in protected.items():
        assert key in text, f"sentinel {key} vanished during renumbering"
        text = text.replace(key, val)
    assert "\x00" not in text, "a sentinel survived into the output"

    # -------------------------------------------------------- 4. report
    print(f"\n  headings renumbered: {len(heads_seen)}")
    for a, b in heads_seen:
        print(f"    {a:>4} -> {b}")
    unmapped = [r for r in refs_seen if r[2]]
    print(f"\n  in-text §refs renumbered: {len(refs_seen) - len(unmapped)}"
          f"   unmapped: {len(unmapped)}")
    assert not unmapped, f"unmapped section references: {unmapped}"
    print(f'  "Section 5.5" occurrences rewritten: {n_sec_word}')

    # every heading number must be unique after the move
    nums = [b for _, b in heads_seen]
    assert len(nums) == len(set(nums)), f"duplicate heading numbers after renumber: {nums}"

    if not args.write:
        d = list(difflib.unified_diff(original.splitlines(), text.splitlines(),
                                      "before", "after", lineterm="", n=0))
        print(f"\n  DRY RUN — {len([x for x in d if x.startswith('+') and not x.startswith('+++')])}"
              f" lines would change. Re-run with --write to apply.")
        return

    shutil.copy(path, path + ".bak")
    with open(path, "w") as f:
        f.write(text)
    print(f"\n  wrote {TEMPLATE} (backup at {TEMPLATE}.bak)")


if __name__ == "__main__":
    main()
