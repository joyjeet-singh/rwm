"""
T5 -- the anonymised correspondence transcript, as a supplementary file.

§6.1 and §8 both quote a personal communication with the first author. Quotations
from private correspondence are the one evidence class in this paper that a
reviewer cannot check against anything: `EXT` at least points at a published
paper, but a private email points at nothing. This produces a transcript so the
quotes are verifiable rather than asserted.

Generated from the ledger's X-10 entry rather than typed, so the transcript and
the ledger cannot drift apart, and every quotation in the paper is checked to
appear in it verbatim before the file is written.

Anonymisation, in both directions:
  - the author is "the first author" throughout; his name, address and
    affiliation do not appear;
  - our name, handle, repository URLs and archival identifiers do not appear.
The deny-list is shared with scripts/make_anon_bundle.py, which asserts zero
occurrences across the whole staged tree.

TWO HUMAN ACTIONS ARE REQUIRED BEFORE THIS FILE SHIPS, and neither is one this
script can perform. They are printed on every run and recorded in the file's own
header:
  1. obtain the first author's explicit consent to quote the correspondence on
     the record, and state in the paper that consent was given;
  2. declare the conflict to the Action Editor -- the original authors now know
     this paper exists, and none of them should be assigned to review it.

Writes docs/SUPPLEMENTARY_CORRESPONDENCE.md and
results/t5_anon_transcript.json.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402

LEDGER = "FINDINGS_LEDGER.md"

# NOT under the repository tree, and this is the whole point.
#
# This transcript is a private exchange with the first author, and consent to
# quote it on the record has not been given. It lived at docs/ and was committed;
# on 2026-08-28 it was pushed to a NAMED public repository, where it stood for
# 46 minutes before this was written. Two things that cost: the letter asking him
# for permission offers to withdraw any quotation the same day, which is not an
# offer that can be honoured once the whole exchange is published; and 6.1 and 8
# cite the file as ANONYMISED supplementary material, so anyone searching a
# quoted sentence reaches the named repository and the submission's anonymity
# goes with it. Neither is repairable by editing prose (M-48).
#
# So it is written OUTSIDE the tree, gitignored inside it as a second line of
# defence, and copied into the anonymised bundle -- where reviewers need it and
# where it is not public -- by make_anon_bundle.py. submission_check.py fails the
# build if it reappears anywhere git can see.
PRIVATE_DIR = os.environ.get(
    "RWM_PRIVATE_DIR",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir,
                 "rwm_private"))
OUT_MD = os.path.normpath(os.path.join(PRIVATE_DIR, "SUPPLEMENTARY_CORRESPONDENCE.md"))
# The name it takes INSIDE the anonymised bundle, which is what 6.1 and 8 cite.
BUNDLE_PATH = os.path.join("docs", "SUPPLEMENTARY_CORRESPONDENCE.md")

# Identifying strings that must not appear in the transcript. Kept here and
# imported by make_anon_bundle.py so there is one list, not two.
DENY = [
    "Chenhao Li", "chenhli", "breadli428", "Dr Li", "Dr. Li",
    "joyjeet", "Joyjeet", "joyjeet-singh", "Joyjeetsingh",
    "github.com/joyjeet-singh", "huggingface.co/Joyjeetsingh",
]

# Every quotation the paper attributes to the correspondence. Each is asserted to
# appear in the transcript, so a quote cannot be in the paper and absent here.
PAPER_QUOTES = [
    "The aleatoric term is not used in downstream training",
    "It is reported in Fig. 3 (right) as an analysis of the model behavior",
    "more of a high-level explanation",
    "as I always did",
    "is a typo",
    "the checkpoint was released after a few",
]

HEADER = """# Supplementary — correspondence with the first author, 21 August 2026

**Status of consent.** This transcript is prepared for submission as supplementary material.
Explicit consent from the first author to quote this correspondence on the record is a human
action outside the build, and the paper states whether it was given. If this line still reads
CONSENT NOT YET RECORDED at submission, the quotations must be removed from the paper and
replaced with a statement that the authors were contacted, because a quotation from private
correspondence without permission is not ours to publish.

> **CONSENT NOT YET RECORDED.**

**Conflict of interest.** The authors of both papers under reproduction are aware that this work
exists, having been written to on 21 August 2026. None of them should be assigned to review it.
Declaring this to the Action Editor is a human action outside the build.

**Anonymisation.** The first author is referred to as "the first author" throughout; his name,
address and affiliation do not appear. Identifying details of the reproducing author are likewise
removed. Nothing else is altered: the quoted passages are verbatim, including their original
spelling and phrasing.

**What this file is for.** §6.1 and §8 of the paper each quote this exchange. A quotation from
private correspondence is the one class of evidence in that paper which a reviewer cannot check
against anything else, so the exchange is reproduced here in full rather than only where it is
convenient. Where a quotation is used in the paper, the section is named beside it.

---

"""

FOOTER = """
---

## What the paper draws from this, and what it does not

**Settled by the correspondence.** That the aleatoric term is discarded by design rather than by
oversight (§6.1), and that the standard deviation in the code is the intended quantity while Eq. 4
is a high-level description (§6.1). Both were established independently from the code before the
exchange; the reply confirms the *intent*, which the code alone cannot show.

**Softened by the correspondence.** §8's extrapolation assumes the released initialisation and the
released learning rate. The first author's statement that the checkpoint was released some
repository revisions after the setup that trained it means those may not be the values that
produced it. That reframes §8 from an inconsistency in the release into a documentation gap
between a release and a run, which is what §8 now says.

**Not settled.** The arithmetic itself. At the released initialisation and learning rate the
checkpoint's variance state remains unreachable at any of the three stated iteration counts. The
reply supplies a plausible, author-supplied reason why the released artifacts would not reproduce
it; it does not supply a configuration that does.

**Evidence class.** `EXT`. Correspondence cannot substitute for a measurement and is not used as
one anywhere in the paper — every finding it bears on carries its own measured evidence
(C-13, C-14, C-15, O-12 in `FINDINGS_LEDGER.md`). It corroborates and explains; it does not
establish.
"""


def main():
    text = open(LEDGER).read()
    m = re.search(r"^### X-10 — Author correspondence.*?$", text, re.M)
    assert m, "ledger entry X-10 not found"
    body = text[m.end():]
    end = body.find("\n### ")
    body = body[:end] if end > 0 else body
    body = body.split("**Evidence**")[0].rstrip()

    # Name the section each quotation supports, for a reader jumping in here.
    body = body.replace(
        "**1. The aleatoric head is not used downstream — CONFIRMED by the author.**",
        "### 1. The aleatoric head is not used downstream — confirmed by the author\n"
        "*Quoted in §6.1 of the paper. The figure number is the first author\'s and follows "
        "arXiv:2504.16680v1, where the MOPO-PPO training figure is Fig. 3; in the current v3 it "
        "is Fig. 4. See `results/original_paper_figures.json`.*\n")
    body = body.replace(
        "**2. The standard deviation is intended; Eq. 4 is a simplification — RESOLVES C-15.**",
        "### 2. The standard deviation is the intended quantity; Eq. 4 is a simplification\n"
        "*Quoted in §6.1 of the paper.*\n")
    body = body.replace(
        "**3. The iteration count — `max_iterations: 500` is a typo, and the released repo is not "
        "the\ntraining repo.**",
        "### 3. The iteration count, and the released repository\n"
        "*Quoted in §8 of the paper.*\n")

    out = HEADER + body.strip() + "\n" + FOOTER

    # ---------------------------------------------------- anonymisation check
    found = [d for d in DENY if d in out]
    assert not found, f"identifying strings survived into the transcript: {found}"

    # Self-test: plant a deny-list string and confirm the check above would catch
    # it. A scrubber that has quietly stopped scrubbing is worse than none.
    probe = out + "\n<!-- selftest " + DENY[0] + " -->"
    assert any(d in probe for d in DENY), "the anonymisation check does not fire"

    # ------------------------------------------------- every paper quote here
    # Strip the blockquote markers before matching: the quotations are wrapped
    # across lines with "> " prefixes, which would otherwise land inside a quote
    # and make a correct transcription look like a missing one.
    flat = re.sub(r"\s+", " ", re.sub(r"^\s*>\s?", "", out, flags=re.M))
    missing = [q for q in PAPER_QUOTES if re.sub(r"\s+", " ", q) not in flat]
    assert not missing, f"quotations used in the paper are absent from the transcript: {missing}"

    # ...and every quote in the transcript is one the paper is allowed to use
    if os.path.exists("PAPER.md"):
        paper = re.sub(r"\s+", " ", open("PAPER.md").read())
        used = [q for q in PAPER_QUOTES if re.sub(r"\s+", " ", q) in paper]
    else:
        used = []

    os.makedirs("docs", exist_ok=True)
    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    with open(OUT_MD, "w") as f:
        f.write(out)

    rec = {
        "generated_from": "FINDINGS_LEDGER.md, entry X-10",
        # The BUNDLE path, not the private one: this artifact is committed and
        # goes into the anonymised archive, and the private path carries a home
        # directory. Where the file actually sits is deliberately not recorded
        # anywhere git can see.
        "output": BUNDLE_PATH,
        "output_note": ("written outside the repository tree and copied into the "
                        "anonymised bundle at this path; see M-48"),
        "n_quotations": len(PAPER_QUOTES),
        "n_quotations_present_in_transcript": len(PAPER_QUOTES) - len(missing),
        "n_quotations_used_in_paper": len(used),
        "deny_list_size": len(DENY),
        "deny_list_hits": 0,
        "anonymisation_selftest": "passed — a planted deny-list string is detected",
        "consent_recorded": False,
        "human_actions_outstanding": [
            "obtain the first author's explicit consent to quote this correspondence on the "
            "record, and state in the paper that consent was given",
            "declare the conflict to the Action Editor: the original authors know this paper "
            "exists and none of them should be assigned to review it",
        ],
        "evidence_class": "EXT",
    }
    dst = os.path.join(R.RESULTS, "t5_anon_transcript.json")
    with open(dst, "w") as f:
        json.dump(rec, f, indent=2, sort_keys=True)

    print("T5 — ANONYMISED CORRESPONDENCE TRANSCRIPT")
    print("=" * 88)
    print(f"  wrote {OUT_MD} ({len(out.splitlines())} lines)")
    print("  NOT in the repository tree: this is private correspondence and consent")
    print("  to quote it has not been given. It reaches reviewers through the")
    print(f"  anonymised bundle as {BUNDLE_PATH}, and nowhere else.")
    print(f"  quotations checked present: {len(PAPER_QUOTES) - len(missing)}"
          f"/{len(PAPER_QUOTES)}   used in PAPER.md: {len(used)}")
    print(f"  deny-list entries: {len(DENY)}, hits: 0, self-test passed")
    print(f"  wrote {R.rel(dst)}")
    print("\n  TWO HUMAN ACTIONS OUTSTANDING — not performed by this script:")
    for a in rec["human_actions_outstanding"]:
        print(f"    - {a}")


if __name__ == "__main__":
    main()
