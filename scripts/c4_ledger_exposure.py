"""
C4 -- the ledger entry for the correspondence exposure, and the two claims it
touches.

M-48 records that `docs/SUPPLEMENTARY_CORRESPONDENCE.md` was pushed to a named
public repository and how long it stood there. It is entered as INFER because
the consequence -- what a reader who found it could then do -- is an inference,
while the window itself is a fact from the reflog.

Why it is worth an entry at all, when the file is gone and the history rewritten:
if the first author later declines permission to quote, this entry is the only
thing that says what was already public and for how long. A record that exists
only while the mistake is uncorrected is not a record.

Run with --write.
"""
import difflib
import re
import shutil
import sys

LEDGER = "FINDINGS_LEDGER.md"
ANCHOR = "## Candidate paper contributions"

NEW_ENTRIES = r"""
### M-48 — The correspondence transcript was published on a named repository for 46 minutes · **NEW**
**What happened.** `docs/SUPPLEMENTARY_CORRESPONDENCE.md` was committed on 23 August (`7859309`)
and pushed to `github.com/<author>/rwm` on **2026-08-28 at 11:46:49 +0530**, in the push that
brought the public repository up to date for submission. It was removed, and the history rewritten
to purge it, the same day. **Exposure window: 2026-08-28 11:46 to 12:32 +0530, 46 minutes**, on a
public repository under the author's own name, in full.

**What the file is.** The verbatim exchange with the first author of both papers under
reproduction, anonymised as to both parties but not consented to. The paper's own header on that
file reads `CONSENT NOT YET RECORDED`, and states that if it still reads that at submission the
quotations must come out of the paper.

**Two consequences, neither repairable by editing prose.**

1. *The offer in the letter.* The reply drafted for the first author asks permission to quote
   three fragments and offers to withdraw any of them the same day. That offer cannot be honoured
   for an exchange already published. If he opened the repository link in that letter during the
   window, he would have found the whole exchange there.
2. *The submission's anonymity, not merely the file's.* §6.1 and §8 cite the transcript as
   **anonymised** supplementary material. A reviewer, or anyone, searching a quoted sentence
   during the window would have reached a repository under the author's name — which
   de-anonymises the whole submission, not one file.

**What was done.** The transcript is now generated OUTSIDE the repository tree by
`scripts/t5_anon_transcript.py`, gitignored inside it, and copied into the anonymised bundle and
the supplementary archive — where reviewers need it and where it is not public. `submission_check`
gained **A0**, a public-tree gate that fails the build if a never-publish path appears in the
working tree, in git's index, in HEAD, or in reachable history. The history check is the one that
matters: a deletion commit satisfies the other three and leaves the file recoverable from the
public repository forever.

**What was not done, and is not this script's to do.** Consent has still not been given. The
window above is what a reader of this ledger needs if it is refused.

**The judgement that produced it, recorded because it is the useful part.** The exposure was not
an accident of tooling. The risk was identified before the push, in writing, and the decision to
push anyway was taken deliberately and then reversed. `.gitignore` would not have prevented it —
the file was already tracked, and an ignore rule does not apply to a tracked path. Only A0's
history check would have.
**Evidence** `INFER` `results/anon_bundle.json` `scripts/submission_check.py`.
**Status** CONFIRMED · **Relevance** METHOD


"""


def main():
    write = "--write" in sys.argv
    original = open(LEDGER).read()
    text = original
    ids = re.findall(r"^### ([A-Z]-\d+) ", NEW_ENTRIES, re.M)
    already = [i for i in ids if f"\n### {i} " in text]
    if already:
        print(f"  entries already present, not re-appending: {already}")
    else:
        assert ANCHOR in text
        i = text.index("\n" + ANCHOR)
        text = text[:i] + "\n" + NEW_ENTRIES.strip("\n") + "\n\n" + text[i + 1:]
        print(f"  appended: {', '.join(ids)}")
    if not write:
        print("  DRY RUN — re-run with --write")
        return
    shutil.copy(LEDGER, LEDGER + ".rev2bak")
    open(LEDGER, "w").write(text)
    d = list(difflib.unified_diff(original.splitlines(), text.splitlines(),
                                  "before", "after", lineterm="", n=0))
    print(f"  wrote {LEDGER} ({len(d)} diff lines)")


if __name__ == "__main__":
    main()
