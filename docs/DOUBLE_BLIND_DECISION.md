# The double-blind question, decided

**Status: DECIDED. Submit under TMLR's standard double-blind process, with the public
repository left public and the Software Heritage date removed from the body.**

This document exists because the decision was being deferred, and deferral is itself a
choice — one that spends text on an anonymity the project does not have while leaving
the exposure it does have unmanaged.

## What the anonymity actually is

A reviewer who wants to identify the author can:

- search any quoted sentence of the paper and reach a public GitHub repository under a
  personal account;
- resolve the Software Heritage archival visit the paper dates to a specific day, which
  identifies one origin;
- read `CITATION.cff`, `NOTICE` or `MODEL_CARD.md` in any copy of the repository.

`scripts/make_anon_bundle.py` scrubs the submission bundle and asserts zero occurrences of
the deny-list across the staged tree, and the identifying files are excluded from it
entirely. That is real and it is worth having. It is **not** the same as the work being
unfindable, and the paper should not imply otherwise.

## Why not make the repository private

Three reasons, in order of weight.

1. **It would break the paper's central argument.** §8's pre-registration case rests on
   commit timestamps a reader can check, and the paper says so. A private repository turns
   "checkable at review time" into "take our word for it" — which is the thing this paper
   spends thirty pages not doing.
2. **The Software Heritage archive is already public and permanent**, and it is what bounds
   the back-dating objection. Making the origin private does not withdraw the archived
   snapshot, so the identifying link survives while the checkability does not.
3. **TMLR tolerates public preprints and public code.** Its policy does not require that
   the work be unfindable; it requires that authors not identify themselves *in the
   submission*, and that reviewers not go looking. Public artifacts are the norm in
   reproducibility work, and a reproduction whose code cannot be inspected is a weaker
   paper.

The residual risk is that a determined reviewer de-anonymises the submission. That risk is
accepted, deliberately, and the reason is (1): the alternative costs the argument.

## What changes as a consequence

1. **The Software Heritage date comes out of the body.** The paper cited archival "on
   21 August 2026", which is a one-field lookup away from the origin. §8 now states what the
   archive establishes — that the repository, with the whole pre-registration history in the
   form the paper cites, existed no later than a third-party archival moment before
   submission — **without the date**. The identifier and the date are disclosed on
   acceptance, which is what the paper already said it would do with the identifier.
2. **The conflict declaration goes to the Action Editor at submission**, naming the authors
   of both papers under reproduction as contacted and therefore ineligible to review. That
   is unrelated to anonymity and is required regardless.
3. **Nothing else changes.** The bundle scrubbing, the deny-list assertion and the
   exclusion of identifying files all stay exactly as they are.

## What this does NOT decide

Whether to *announce* the repository before a decision. The recommendation is not to: an
announcement during review is what turns "findable if you look" into "in front of a
reviewer who wasn't looking". That is a separate call and it is not urgent.
