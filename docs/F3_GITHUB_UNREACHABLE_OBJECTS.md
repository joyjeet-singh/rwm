# GitHub unreachable objects — the request, and the faster alternative

**Nothing here has been executed.** Both routes are human actions requiring a credentialed
session. This document drafts the first and records why the second may be better.

## What the problem is

`docs/SUPPLEMENTARY_CORRESPONDENCE.md` was pushed to a public repository on 28 August 2026 and
purged by history rewrite five hours later (`M-48`). A fresh clone after the force-push carries
zero commits and zero blobs with that path — checkable, and checked.

A force-push does not delete objects. It makes them **unreachable**, and unreachable objects
survive on GitHub's side until GitHub garbage-collects the repository. Until then, anyone who
recorded an object hash during the window could in principle still fetch the blob directly, and
GitHub serves unreachable objects by hash to anyone who asks for one.

`results/swh_visit_check.json` establishes that Software Heritage did **not** archive the file —
one visit to the origin, predating the commit that introduced it, and the archived tree does not
contain the path. That closes the one vector no rewrite could reach. It does not close this one.

## Route A — ask GitHub Support to run garbage collection

**Draft. Not sent.**

> **Subject:** Request to garbage-collect unreachable objects after a history rewrite
>
> Hello,
>
> I force-pushed a history rewrite to a private-content incident in one of my repositories on
> 28 August 2026, removing a file that should never have been committed. A fresh clone no longer
> contains it, but I understand the pre-rewrite objects remain reachable by direct hash until the
> repository is garbage-collected.
>
> Could you please run garbage collection on the repository so that those unreachable objects are
> removed? The file contained private correspondence with a third party who had not consented to
> its publication, so I would like to be able to tell them the removal is complete rather than
> pending.
>
> The repository has no forks. I am happy to delete and recreate it instead if that is simpler on
> your side; I would rather do whichever is faster and more certain.
>
> Thank you,
> ——

**What Route A does not give you:** a time bound, or a confirmation you can quote. Support may
run it promptly or may not, and "I have asked" is not the same fact as "it is gone".

## Route B — delete and recreate the repository

**If the repository has no forks, deleting and recreating it removes the unreachable objects
immediately and with certainty.** No support ticket, no waiting, no ambiguity about whether it
happened. Deleting a repository destroys its object store.

**Check first, in this order:**

1. **Forks.** A fork keeps a copy of the object store. If any fork exists, deletion does not help
   and Route A is the only option.
2. **Anything else the repository holds that is not reproducible** — issues, pull requests,
   releases, stars, the URL's history in anyone's bookmarks. A reproduction repository with no
   issues and no releases loses almost nothing; check rather than assume.
3. **Whether the Software Heritage archive should be preserved.** It already is: the archive is
   independent of the origin and survives deletion of it. That is the point of §8's argument and
   it is unaffected either way.

**If (1) is clear and (2) is acceptable, Route B is strictly better than Route A**: same outcome,
immediate, and verifiable by you rather than reported to you.

## What to tell the first author either way

The consent letter (`docs/LETTER_TO_AUTHOR_CONSENT.md`) says the removal is being pursued and
promises to report which route was taken and when it completed. That promise should be kept
whichever route is used, and it should say plainly that the second residual vector — anyone who
cloned during the five-hour window — is beyond reach of both.
