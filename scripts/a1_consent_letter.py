"""
A1 -- the consent letter, and the rewrite that runs if consent is refused.

§6.1 and §8 of the paper quote a private exchange with the first author of both
papers under reproduction. The transcript's own header reads CONSENT NOT YET
RECORDED, and it says that if it still reads that at submission the quotations
must come out.

The letter was previously planned to go out AFTER the C1 claim review. That
ordering is wrong. If consent is refused or qualified, §6.1's resolution of the
Eq. 4 / code discrepancy and the whole of §8's resolution have to be rewritten --
and those sentences are inside the 89 claims the review is about. Reviewing text
that a pending answer may delete is wasted work at best and misleading at worst.
So the letter is drafted first, and the fallback rewrite is prepared beside it
rather than left to be improvised if the answer is no.

WHAT IS GENERATED AND WHY.

The list of quoted fragments is the part that must not be typed. `PAPER_QUOTES`
in scripts/t5_anon_transcript.py is a hand-maintained list of six strings, and a
hand-maintained list of what the paper quotes is the same defect class as a
hand-typed count: it can fall behind the paper, and the failure is silent because
nothing compares the two. Here the fragments are extracted from PAPER.template.md
itself -- every double-quoted span inside the two passages that attribute to the
correspondence -- and each is then asserted to appear verbatim in the transcript.
Consent obtained for a list that does not match what the paper prints is not
informed consent.

Three assertions, all of which must hold before either file is written:

  1. every extracted fragment appears verbatim in the transcript;
  2. the extracted set equals t5_anon_transcript.PAPER_QUOTES as a covering set,
     so the two mechanisms cannot disagree about what the paper quotes;
  3. the fallback's every `old` string occurs exactly once in the template.

The third is what makes the fallback real rather than aspirational: it is applied
by --apply-fallback, not by a person editing prose under time pressure.

    python scripts/a1_consent_letter.py                 write both documents
    python scripts/a1_consent_letter.py --apply-fallback  perform the rewrite

NOTHING HERE SENDS ANYTHING. The letter is a draft for a person to send.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402
# scripts.t5_anon_transcript is imported inside main(), not here: it imports THIS
# module for extract_fragments(), and a module-level import in both directions is
# a cycle. The extractor is the shared thing; the transcript writer is the caller.

TEMPLATE = "PAPER.template.md"
LETTER = os.path.join("docs", "LETTER_TO_AUTHOR_CONSENT.md")
FALLBACK = os.path.join("docs", "FALLBACK_NO_QUOTATION.md")
OUT_JSON = "a1_consent_letter.json"

# The two passages that attribute to the correspondence, located by their opening
# sentence rather than by section number, so a renumbering does not silently empty
# the extraction. Each is (section, start marker, end marker).
PASSAGES = [
    ("6.1", "Eq. 4 specifies a", "So the aleatoric head"),
    ("8", "**What the author says.**", "That last point reframes this section."),
]


def _unwrap(s):
    return re.sub(r"\s+", " ", s).strip()


def extract_fragments(tpl):
    """Every double-quoted span inside the passages that cite the correspondence."""
    out = []
    for sec, a, b in PASSAGES:
        i, j = tpl.find(a), tpl.find(b)
        assert i >= 0, f"§{sec}: opening marker {a!r} not found in {TEMPLATE}"
        assert j > i, f"§{sec}: closing marker {b!r} not found after the opening"
        seg = tpl[i:j]
        for m in re.finditer(r'"([^"]+)"', seg):
            out.append({"section": sec, "text": _unwrap(m.group(1))})
    return out


# ---------------------------------------------------------------- the fallback
#
# What each sentence becomes if consent is refused. `old` is matched
# whitespace-tolerantly and asserted to occur exactly once; `new` states the same
# fact without quoting, and says where the fact came from, because a reader must
# still be able to tell an author-supplied fact from a measured one.
REWRITES = [
    {"section": "6.1", "why": "the Eq. 4 / code discrepancy",
     "old": 'We asked, and the first author confirms the code is\n'
            'operative: the penalty is applied to the standard deviation as intended, and Eq. 4 is "more of a\n'
            'high-level explanation" (personal communication, 21 August 2026; the exchange is reproduced in\n'
            'full, anonymised, in the supplementary material as `SUPPLEMENTARY_CORRESPONDENCE.md`, so these\n'
            'quotations are checkable rather than asserted).',
     "new": 'We wrote to the first author on 21 August 2026 to ask which form was meant. He replied '
            'the same day that the implementation is operative and that Eq. 4 is a high-level '
            'description rather than the operative definition, so the discrepancy is a notational '
            'gap in the paper and not an implementation error. He was asked for permission to quote '
            'the exchange and it was not given, so it is reported here in summary; nothing in this '
            'paper rests on it, and the code is measured directly either way.'},
    {"section": "6.1", "why": "the aleatoric discard",
     "old": 'The same correspondence confirms the discard directly: "the aleatoric term is not used in\n'
            'downstream training. It is reported in Fig. 3 (right) as an analysis of the model behavior."',
     "new": 'The same correspondence confirms the discard directly, and states that the aleatoric '
            'term is reported as an analysis of model behaviour rather than consumed downstream.'},
    {"section": "8", "why": "the iteration count and the released repository",
     "old": 'He\n'
            'replied the same day; the exchange is reproduced in full, anonymised, in the supplementary\n'
            'material (`SUPPLEMENTARY_CORRESPONDENCE.md`): the released `max_iterations: 500` is "a typo"; his recollection is 5,000\n'
            'iterations, "as I always did"; he does not recall how the checkpoint was obtained; and — the part\n'
            'that matters most — "the checkpoint was released after a few iterations of the repo than the setup\n'
            'I used for the submission."',
     "new": 'He replied the same day. In summary, and without quotation, because permission to quote '
            'was asked for and not given: the released `max_iterations: 500` is a typographical '
            'error; his recollection is 5,000 iterations, which is his usual setting; he does not '
            'recall how the checkpoint was obtained; and — the part that matters most — the '
            'checkpoint was released some repository revisions after the setup that trained it.'},
]


def _pat(old):
    return re.compile(r"[\s>]+".join(re.escape(w) for w in old.split()))


def main():
    import t5_anon_transcript as T5
    tpl = open(TEMPLATE).read()
    frags = extract_fragments(tpl)
    transcript = open(T5.OUT_MD).read() if os.path.exists(T5.OUT_MD) else None
    assert transcript is not None, (
        f"the transcript is not at {T5.OUT_MD}. It is written outside the tree by "
        f"scripts/t5_anon_transcript.py (M-48); run that first, or set RWM_PRIVATE_DIR.")
    # Blockquote markers and the wrapping the transcript applies are formatting,
    # not content; compare on the unwrapped text.
    flat = _unwrap(transcript.replace("\n>", " ").replace(">", " "))

    # Case-insensitively, because lowering a quotation's first letter to fit the
    # syntax of the sentence carrying it is ordinary editorial practice and not an
    # alteration of what was said -- §6.1 does exactly that to "The aleatoric term".
    # Anything differing by MORE than case is an alteration and is reported as one:
    # the point of this check is that consent covers what the paper prints.
    missing = [f["text"] for f in frags if f["text"].lower() not in flat.lower()]
    assert not missing, (
        "the paper quotes fragments that are not in the transcript verbatim; consent "
        f"obtained for the transcript would not cover them: {missing}")
    altered = []
    for f in frags:
        i = flat.lower().find(f["text"].lower())
        exact = flat[i:i + len(f["text"])]
        if exact != f["text"] and exact.lower() != f["text"].lower():
            altered.append((f["text"], exact))
        f["case_changed_from"] = exact if exact != f["text"] else None
    assert not altered, f"quoted fragments altered beyond case: {altered}"

    # t5's gate -- "every quotation the paper uses appears in the transcript" --
    # ran over a HAND-MAINTAINED list of six strings. Two of the six were not in
    # the paper at all: "The aleatoric term is not used in downstream training"
    # (§6.1 lowers the T to fit its sentence) and "is a typo" (the paper quotes
    # `a typo`, with `is` outside the quotation marks). Its own artifact recorded
    # the drift -- n_quotations 6, n_quotations_used_in_paper 4 -- and nothing
    # compared the two, so the gate spent two of its six assertions guarding text
    # that was not there. t5 now derives the list from extract_fragments() below.
    derived = [f["text"] for f in frags]
    assert T5.PAPER_QUOTES == derived, (
        "t5_anon_transcript.PAPER_QUOTES is no longer derived from the paper: "
        f"{[q for q in T5.PAPER_QUOTES if q not in derived]} extra, "
        f"{[q for q in derived if q not in T5.PAPER_QUOTES]} missing")

    for r in REWRITES:
        n = len(_pat(r["old"]).findall(tpl))
        assert n == 1, f'fallback §{r["section"]} ({r["why"]}): {n} matches in {TEMPLATE}, expected 1'

    if "--apply-fallback" in sys.argv:
        out = tpl
        for r in REWRITES:
            out = _pat(r["old"]).sub(lambda _m, _r=r: _r["new"], out, count=1)
        open(TEMPLATE + ".preconsent.bak", "w").write(tpl)
        open(TEMPLATE, "w").write(out)
        print(f"applied {len(REWRITES)} rewrites to {TEMPLATE}; "
              f"original at {TEMPLATE}.preconsent.bak")
        print("  now run: python scripts/build_paper.py && "
              "python scripts/check_comparative_claims.py --self-test")
        return 0

    SWH = json.load(open(os.path.join(R.RESULTS, "swh_visit_check.json")))
    W = SWH["window"]

    by_sec = {}
    for f in frags:
        by_sec.setdefault(f["section"], []).append(f["text"])
    frag_block = ""
    for sec in sorted(by_sec):
        frag_block += f"\n**In §{sec} of the paper** ({len(by_sec[sec])} "
        frag_block += ("fragment" if len(by_sec[sec]) == 1 else "fragments") + "):\n\n"
        for t in by_sec[sec]:
            frag_block += f"> “{t}”\n\n"

    letter = f"""# Letter to the first author — request for permission to quote

**Generated by `scripts/a1_consent_letter.py`. Do not hand-edit.** The list of quoted
fragments below is extracted from `PAPER.template.md` and each one is checked to appear
verbatim in the transcript before this file is written, so what is being consented to is
exactly what the paper prints.

**This is a draft. Nothing sends it.** Sending it is a human action, as is recording the
answer in the transcript header.

---

Dear Dr ——,

Thank you again for your reply of 21 August 2026. It settled two questions that the released
code and paper could not, and it changed what I write in one section rather than merely
confirming it.

I am writing to ask for something I should have asked for at the same time: **your explicit
permission to quote that exchange on the record** — in a paper I intend to submit to TMLR, and
in anonymised supplementary material that accompanies it for reviewers. I did not ask when I
wrote to you, and I do not think a reply to a technical question implies permission to publish
it. So this asks properly, and it asks in a form you can say no to without costing me anything
I am not willing to lose.

## Exactly what would be quoted

{len(frags)} fragments in total, all of them from your reply of 21 August 2026. Nothing else from
the exchange appears in the paper. They are reproduced here in full so that what you are
agreeing to is not an abstraction:
{frag_block}Your name, affiliation and address appear nowhere. You are "the first author"
throughout, in the paper and in the supplementary transcript alike. The supplementary
material is not published: it goes to reviewers with the submission.

## What I would be grateful for

Any one of these three, in a sentence, is enough:

1. **Yes** — the fragments above may be quoted as personal communication, dated, anonymised.
2. **Yes, with changes** — name any fragment you would rather I dropped or reworded, and I
   will use the paraphrase form below for that one.
3. **No** — and I will remove every quotation. This is a real option and not a courtesy: the
   rewrite is already written (`docs/FALLBACK_NO_QUOTATION.md`), it costs three sentences,
   and no finding in the paper depends on it. Every result your reply bears on carries its
   own measured evidence from the released code and checkpoint; your reply corroborates and
   explains, and it is nowhere the basis for a number.

If you would prefer not to appear at all, I will say only that the authors were contacted and
that a reply was received, with no content.

## One thing I have to tell you before you decide

I would rather you heard this from me than discovered it, and it is the reason this letter is
not simply an apology for a late request.

**The transcript of our exchange was briefly public.** I committed it to my repository and
pushed it to a public GitHub repository under my own name on **28 August 2026 at
{W['open'][11:16]} ({W['open_utc'][11:16]} UTC)**. I noticed, rewrote the history to remove it, and
force-pushed at **{W['shut'][11:16]}** the same day. **The exposure window was {W['hours']:.0f} hours**, and
during it the exchange was readable in full by anyone who looked.

I checked what could be checked, and the result is favourable, but I want to state its limits
rather than its headline. Software Heritage archives public repositories permanently and its
takedown policy is narrow, so an archival crawl inside that window would have been the one
consequence no rewrite could reach. **There was none**: the archive holds {len(SWH['visits'])} visit to the
repository, on {SWH['visits'][0]['date_utc'][:10]}, which predates the commit that introduced the file, and
the archived tree does not contain it. Verdict: **{SWH['verdict']}**
(`results/swh_visit_check.json`).

**Two things that result does not cover, and I am not going to pretend otherwise:**

- **Unreachable objects on GitHub.** A force-push makes the old commits unreachable; it does
  not delete them. Until GitHub garbage-collects the repository, anyone who recorded an object
  hash during the window could in principle still fetch the blob. I am asking GitHub Support
  to run garbage collection; if the repository turns out to have no forks I will instead
  delete and recreate it, which removes those objects immediately and with certainty where a
  support request does not. I will tell you which I did, and when it is done.
- **Anyone who cloned or forked during the window.** A copy taken in those {W['hours']:.0f} hours is
  beyond the reach of anything I can do. The repository had no announced release and no
  followers at the time, so I think this is unlikely; I cannot show that it did not happen.

The file is now generated outside the repository tree, is gitignored inside it, and a build
gate fails if that path reappears in the working tree, the index, HEAD, or reachable history.

I am sorry. Asking for permission after the fact is bad enough without also having to report
that the material was exposed while I was failing to ask.

## Two other things, for completeness

**Conflict of interest.** You and your co-authors now know this work exists. I will declare
that to the Action Editor at submission and ask that none of you be assigned to review it.

**The reply to your technical points** is a separate document and is not what this letter is
for. It is ready and I will send it whenever you would like it; the finding most likely to be
useful to you concerns what the five ensemble members share, and it is a suggestion about the
released code rather than an observation about the paper.

Whatever you decide, thank you for answering a stranger's questions about a two-year-old
release in a single day. That is not the norm and it made this work better.

With apologies and thanks,

——

---

*Fragment list generated from `PAPER.template.md`; {len(frags)} fragments across
{len(by_sec)} sections, each verified verbatim against the transcript.
Exposure figures from `results/swh_visit_check.json` and ledger entry M-48.*
"""

    fb = f"""# Fallback — what the paper becomes if consent to quote is refused

**Generated by `scripts/a1_consent_letter.py`. Do not hand-edit.** Applied by:

    python scripts/a1_consent_letter.py --apply-fallback

Every `old` string below is asserted to occur **exactly once** in `PAPER.template.md`
before anything is written, so this is a rewrite that can be executed rather than a
description of one. The original is kept at `PAPER.template.md.preconsent.bak`.

## The size of the change

{len(frags)} quoted fragments across {len(by_sec)} sections, replaced by {len(REWRITES)} rewritten passages.
**No numbered claim, no measured number and no verdict changes.** The correspondence is
evidence class `EXT` throughout: it corroborates and explains, and it is nowhere the basis
for a measurement. Concretely, what survives the rewrite intact:

- §6.1's finding that the code computes a standard deviation where Eq. 4 specifies a
  variance — established from `system_dynamics.py:126` before the exchange, and measured.
- §6.1's finding that the aleatoric head is computed and discarded — established from the
  released code, and measured.
- §8's arithmetic — that at the released initialisation and learning rate the checkpoint's
  variance state is unreachable at any of the three stated iteration counts.

What is lost is the *author-supplied intent* behind each: that the code is operative by
design rather than by accident, and that the released repository is not the one that trained
the checkpoint. Those become reported-in-summary rather than quoted. §8's reframing from "an
inconsistency in the release" to "a documentation gap between a release and a run" **stands**,
because it follows from what he said and not from the words he said it in — but it stands on
a summary a reader cannot check against a transcript, and §12 should say so if this path is
taken.

## The rewrites, in order

"""
    for n, r in enumerate(REWRITES, 1):
        fb += (f"### {n}. §{r['section']} — {r['why']}\n\n**Currently:**\n\n"
               f"> {_unwrap(r['old'])}\n\n**Becomes:**\n\n> {_unwrap(r['new'])}\n\n")

    fb += """## What else has to change, and is not a prose edit

1. The transcript's own header (`scripts/t5_anon_transcript.py`, `HEADER`) says the
   quotations must be removed if consent is not recorded. If this path is taken, that header
   states the outcome instead: permission was asked for and declined.
2. `PAPER_QUOTES` in the same file becomes empty, and its gate — "every quotation in the
   paper appears in the transcript" — becomes vacuous. A gate that cannot fail is worth less
   than no gate (§9), so it must be **removed** rather than left standing over an empty list.
3. Whether the transcript ships at all becomes a question rather than a given. Refused
   consent to quote is not refused consent to include the transcript, but it is not consent
   to include it either. Ask that too, or drop the file and cite nothing.
4. `results/t5_anon_transcript.json` and the supplementary manifest change, so the clean-clone
   figure must be regenerated after the rewrite, not before.
"""

    open(LETTER, "w").write(letter)
    open(FALLBACK, "w").write(fb)
    rec = {"n_fragments": len(frags), "fragments": frags,
           "sections": sorted(by_sec), "n_rewrites": len(REWRITES),
           "transcript": os.path.basename(T5.OUT_MD),
           "all_verbatim_in_transcript": True,
           "swh_verdict": SWH["verdict"], "exposure_hours": W["hours"]}
    json.dump(rec, open(os.path.join(R.RESULTS, OUT_JSON), "w"), indent=2)

    print("A1 — CONSENT LETTER AND FALLBACK")
    print("=" * 72)
    print(f"  fragments extracted from {TEMPLATE} : {len(frags)}")
    for sec in sorted(by_sec):
        print(f"    §{sec}: {len(by_sec[sec])}")
    print(f"  all verbatim in the transcript      : yes")
    print(f"  t5 PAPER_QUOTES covered by them     : yes ({len(T5.PAPER_QUOTES)} entries)")
    print(f"  fallback rewrites, each matching once: {len(REWRITES)}")
    print(f"  SWH verdict                         : {SWH['verdict']}")
    print(f"  exposure window                     : {W['hours']:.0f} h")
    print(f"  wrote {LETTER}")
    print(f"  wrote {FALLBACK}")
    print(f"  wrote {os.path.join(R.RESULTS, OUT_JSON)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
