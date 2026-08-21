# E6 — archiving to Software Heritage: what to run, and when

**This is yours to run. I have not submitted anything.** Archiving is permanent and
outward-facing, so it needs your decision rather than mine.

## Why, in one paragraph

§7 of the paper rests on commit timestamps showing that each decision rule reached git before the
data that tested it. Those timestamps are settable with `git commit --date`, so on their own they
are self-reported. Software Heritage stamps an archival date that **you cannot set**, which is
what makes it evidence rather than assertion. MLRC recommends it explicitly for exactly this.

**It must predate the submission.** An archive created afterwards proves nothing about what
existed before. This is the one item in the whole hardening brief that is time-ordered.

## Current state, checked

```
GET /api/1/origin/https://github.com/joyjeet-singh/rwm/get/   ->  404
GET /api/1/origin/save/git/url/https://github.com/joyjeet-singh/rwm/  ->  404, no save requests
```

The repository is not archived and no save has ever been requested.

## Do this

**1. Push first.** The crawler archives what is public at crawl time, not what is on your disk.

```bash
cd ~/Downloads/PDM/rwm_repro && git push --follow-tags
```

**2. Request the save.** Either the web form at `https://archive.softwareheritage.org/save/`, or:

```bash
curl -X POST "https://archive.softwareheritage.org/api/1/origin/save/git/url/https://github.com/joyjeet-singh/rwm/"
```

No account is needed for a public repository. Anonymous requests are rate-limited but sufficient
for one submission.

**3. Poll until it succeeds.** Expect minutes, occasionally longer if the queue is busy.

```bash
curl -s "https://archive.softwareheritage.org/api/1/origin/save/git/url/https://github.com/joyjeet-singh/rwm/" | python3 -m json.tool
```

`save_task_status` moves `not yet scheduled` → `scheduled` → `succeeded`. Anything else, re-run
step 2.

**4. Get the identifier.** Once it succeeds:

```bash
curl -s "https://archive.softwareheritage.org/api/1/origin/https://github.com/joyjeet-singh/rwm/visit/latest/?require_snapshot=true" | python3 -m json.tool
```

The `snapshot` field is a hash; the citable identifier is `swh:1:snp:<that hash>`. For a specific
commit — better for a paper, because it pins the exact state — resolve the tag:

```bash
curl -s "https://archive.softwareheritage.org/api/1/revision/origin/https://github.com/joyjeet-singh/rwm/branch/refs/tags/v1.0.0/get/" | python3 -m json.tool
```

and cite `swh:1:rev:<id>`.

**5. Tell me the SWHID.** I will record it in the ledger and in the release metadata. It does
**not** go into the anonymous submission — it resolves to a repository with your name on it.

## The anonymity tension, and how the paper currently handles it

You cannot cite the SWHID in a double-blind submission. The paper therefore:

- ships an anonymised `git log` in the supplementary archive, with author and email scrubbed and
  hashes and timestamps intact, so a reviewer can check Figure 4's ordering at review time; and
- states plainly, in §10, that as of submission no archive exists and **a reviewer should treat
  the timestamps as self-reported and weigh §7 accordingly**.

If you archive before submitting, that sentence changes to say an archive exists and its
identifier will be disclosed on acceptance — which is materially stronger and costs one command.

If you would rather not archive, nothing breaks. §7 is one of several supports for the paper's
methodology section, not for its results, and the paper already discloses the weakness. That is a
legitimate choice; it just leaves the argument weaker than it needs to be.
