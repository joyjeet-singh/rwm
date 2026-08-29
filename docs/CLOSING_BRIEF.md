# Closing brief — what is done, what is deliberately not, and what a person must do

This exists so that three things are not confused with each other: work that remains, work that
was **descoped on purpose**, and work that only a human can perform. A list of "outstanding
items" that mixes all three is how a deferred decision comes to look like an unfinished one.

---

## 1. Descoped, deliberately, and not blocking submission (D7)

None of these gates the paper. They were on the critical path and are removed from it, and this
section is the record so they are not mistaken for loose ends.

| item | why it is off the path |
|---|---|
| **Hugging Face model-card push** | The card is built and verified (`MODEL_CARD.md`, `scripts/build_model_card.py`). Pushing it is a credentialed, *outward-facing* action that names the author, and doing it before a decision would de-anonymise a submission under review for no gain. After the decision, not before. |
| **GitHub repository description** | Same reason, smaller stakes. It is a one-line edit that can happen any time and cannot happen usefully now. |
| **MLRC 2026 targeting** | Out of reach on timing, and this is definite rather than estimated: the expression-of-interest deadline passed on 4 June 2026, and every remaining route needs a TMLR **acceptance** logged by 30 September 2026 — not a submission. Submitting in late August against TMLR's two-month first-decision target leaves no room for the revision round that "accepted with minor revisions" implies. `docs/SUBMISSION_VENUE.md` has the routes and the dates. |

**What this costs.** Nothing at submission. The model card and the repository description are
release artifacts for an accepted paper; MLRC was never reachable from here.

---

## 2. Human actions, which no script here performs

Each of these is drafted and none is executed. That separation is deliberate: every one is
outward-facing or credentialed, and a script that could perform it is a script that could perform
it by accident.

| action | drafted in | state |
|---|---|---|
| **Send the consent letter to the first author** | `docs/LETTER_TO_AUTHOR_CONSENT.md` | Drafted, not sent. It lists all five quoted fragments verbatim, discloses the five-hour exposure with both residual vectors, and offers paraphrase-only as a real option. |
| **Record the answer**, and if refused, apply the fallback | `docs/FALLBACK_NO_QUOTATION.md` | The rewrite is executable, not descriptive: `python scripts/a1_consent_letter.py --apply-fallback`. Tested end to end and reverted. |
| **The C1 claim review — 89 claims** | `docs/C1_REVIEW_CHECKLIST.md` | One printable file, Tier 0 first. The script that could have recorded verdicts has been **deleted** (F1); this gate is cleared by a person reading and signing, and by nothing else. |
| **Remove the unreachable objects from GitHub** | `docs/F3_GITHUB_UNREACHABLE_OBJECTS.md` | Two routes drafted, with the reasoning for preferring deletion-and-recreation if the repository has no forks: same outcome, immediate, and verifiable by you rather than reported to you. |
| **One external scientific read** | `docs/EXTERNAL_READ_BRIEF.md` | Three questions to press on, and an explicit request *not* to check numbers — 23 gates already do that, and none of them can tell whether the artifacts answer the right question. |
| **Declare the conflict to the Action Editor** | — | The authors of both papers under reproduction were contacted on 21 August 2026 and none should be assigned to review. Required regardless of anonymity. |
| **Send the reply to the first author's technical points** | `docs/E4_REPLY_DRAFT.md` | Generated from the artifacts, ready, separate from the consent letter. |

---

## 3. Decisions taken and recorded, so they are not re-opened by default

| decision | where |
|---|---|
| Submit double-blind, repository stays public, archival date out of the body | `docs/DOUBLE_BLIND_DECISION.md` |
| Title changed to describe the measurement rather than imply a reveal | ledger `D-19` |
| TMLR, not MLRC | `docs/SUBMISSION_VENUE.md` |

---

## 4. Pre-registered and not yet discharged

Two rules are committed with their minimum detectable effects and are waiting on runs. Both state
in their own text what they can and cannot resolve, because that is what `M-43` was committed
without.

- **`M-49`** — does trunk-sharing survive capacity matching? Five members at reduced width,
  matched to the shared-trunk arm's state-pathway capacity. Its MDE is almost exactly the size of
  the effect it re-tests, so it can detect survival at close to full size and **cannot** resolve a
  partial attenuation. §11 says so.
- **`M-51`/`M-52`** — discharged as `R-72`, and listed here only because `M-52` corrected `M-51`
  after commit and the pair should be read together.

If `M-49` does not complete before submission, §11 states the confound plainly and Appendix G
lists the rule as undischarged. That is a worse outcome than running it and a perfectly
publishable one; what is not acceptable is quietly dropping it.
