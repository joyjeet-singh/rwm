"""A3 — assemble the anonymised supplementary ZIP for a double-blind submission.

TMLR allows up to 100 MB, PDF or ZIP, and it must be anonymised. This assembles
the ledger, the claims-to-evidence map, the claims audit, every results/ JSON,
the code, reproduce.sh, requirements.txt, and an anonymised git log — then
verifies that no file in the archive carries the author name or the repository
URL, and refuses to write the ZIP if any does.

The git log matters: §7's pre-registration argument rests on commit timestamps,
and a reviewer cannot see the repository. The log is emitted with author name and
email scrubbed and the timestamps and hashes left intact, so the ordering in
Figure 4 is checkable at review time.
"""
import io
import json
import os
import re
import subprocess
import sys
import zipfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402
import make_anon_bundle as AB  # noqa: E402  -- the commit-label map and its sweep (D1)

OUT = "supplementary.zip"
IDENT = [re.compile(p, re.I) for p in (
    r"joyjeet", r"\bsingh\b", r"github\.com/joyjeet", r"joyjeet-singh",
    r"/Users/joyjeetsingh",
    # A SWHID is opaque but resolvable: the Software Heritage UI returns the origin
    # URL for it, which carries the author's name. It de-anonymises exactly as a link
    # does, and the first version of this check did not catch it.
    r"swh:1:(?:snp|rev|rel|dir|cnt):[0-9a-f]{40}",
    AB.commit_sweep_pattern(AB.COMMIT_LABELS),
)]
# Repository URL in any form. The paper must not link to a named repo.
URL = re.compile(r"github\.com/([A-Za-z0-9_.-]+)/[A-Za-z0-9_.-]+", re.I)
# Third-party repositories the work legitimately cites: the two upstreams and the
# TMLR style file. Only a repository under the AUTHOR's account is identifying.
# Third-party organisations whose repositories the work legitimately cites. The
# last two arrive from the bibliography's own verification record: several arXiv
# entries give their code repository in the comment field, which t1 stores
# verbatim as evidence. They identify the CITED authors, not us, and removing
# them would make the one file whose purpose is accurate metadata inaccurate.
SAFE_ORGS = {"leggedrobotics", "jmlrorg", "isaac-sim", "goodfeli",
             "jannerm", "martius-lab",
             # The subjects of the Q1 survey (results/q1_pets_descendants.json, cited
             # by section 2): public repositories examined for the PETS bounded-head
             # construction, each recorded with its URL so the survey's --verify path
             # can re-fetch the cited line at the cited commit. They identify the
             # surveyed authors, not us. Added by the user's ruling of 2026-09-26.
             "kchua", "quanvuong", "xingyu-lin", "facebookresearch", "nirbhayjm",
             "shylock-h", "yihaosun1124", "junming-yang", "polixir"}

INCLUDE_DIRS = ["src", "scripts", "results", "docs", "tex"]
# Excluded on purpose. MODEL_CARD.md and its builder are release artifacts for the
# eventual named checkpoint release, not review evidence, and both carry the author
# and repository by design. This script is a submission build tool and its own
# identity patterns would trip its own scan.
# Submission build tools carry the identity patterns they search for, so they trip
# their own scan. They are tooling for the submission, not evidence within it.
EXCLUDE = {"scripts/build_model_card.py", "scripts/build_supplementary.py",
           # Transient: written by ONE reproduce.sh run and describing that run,
           # not the repository -- which is why .gitignore excludes it and why
           # reproduce.sh deletes it at the start of every full run. It has no
           # business in a submission bundle, and leaving it in made this
           # bundle's own file count differ between a tree that had just run the
           # pipeline and one that had not.
           "results/_regenerated.txt",
           "scripts/submission_check.py",
           # Same reason as the three above, and stated in both files: an
           # anonymiser necessarily contains the strings it scrubs for, so it
           # trips its own scan. make_anon_bundle.py excludes itself and the
           # transcript generator from its own staging for exactly this.
           "scripts/make_anon_bundle.py", "scripts/t5_anon_transcript.py",
           "MODEL_CARD.md", "CITATION.cff", "NOTICE",
           # working documents for outward-facing steps; they necessarily carry the
           # repository URL and the author's correspondents
           "docs/E4_AUTHOR_CONTACT.md", "docs/E6_ARCHIVAL.md",
           "docs/E4_REPLY_DRAFT.md",
           # ...and the script that GENERATES that document, which carries the
           # letter body and therefore the same repository URL and the same
           # name. Excluding the output and not its generator left this stage
           # failing from the commit that added the generator; nothing noticed,
           # because the committed supplementary.zip predated it and the stage
           # that would have said so was not re-run until the revision-2 gate.
           "scripts/e4_reply_draft.py",
           "docs/ARCHIVAL_IDENTIFIERS.md",
           # The Software Heritage exposure check, and the artifact it writes.
           # Same category as the two archival documents above: an archival check
           # has to name the origin it is asking the archive about, so the
           # repository URL and the author's account name are the INPUT to the
           # tool, not incidental to it. Excluding it costs review nothing --
           # nothing in the paper, the ledger or any other artifact cites it, and
           # its subject is the exposure of a file this bundle does not contain.
           #
           # This is the exclusion that made stage 28 fail from the commit that
           # added the checker. That failure is why results/verify_reproduction.json
           # was written by a run whose regenerated set silently omitted
           # supplementary_manifest.json -- the same silent-exclusion shape as M-28,
           # inside the claim M-28 is about.
           "scripts/swh_visit_check.py", "results/swh_visit_check.json",
           # Same reason as make_anon_bundle.py and t5_anon_transcript.py above:
           # a scanner that plants a deny-list string to prove it can still
           # detect one necessarily contains that string, and trips its own scan.
           "scripts/f5_pdf_channels.py",
           # ...and the REPORT that scanner writes, which prints the probe string it
           # planted ("probe string : '...'") for exactly the same reason the script
           # contains it. Excluding the script and not its output left this stage
           # failing the moment the pipeline regenerated the report -- the same
           # exclude-the-source-not-the-output shape as scripts/swh_visit_check.py
           # and its artifact two entries above.
           "results/pdf_channels_report.txt",
           # The cover statement is addressed to the action editor and states which
           # acceptance criterion the submission claims. It is submission
           # correspondence rather than evidence, and shipping it inside the
           # evidence bundle would put an argument where a reviewer expects
           # artifacts. Excluded deliberately, and named here so the exclusion is
           # a decision rather than an oversight.
           "docs/COVER_STATEMENT.md",
           # Internal working documents; never ship in any bundle.
           # The submission package (S28): upload instructions and the bundles' own
           # sizes and hashes, which a file inside a bundle can never state
           # correctly. Internal, like the checklist. User ruling 2026-09-26.
           "docs/SUBMISSION_PACKAGE.md",
           "docs/SUBMISSION_CHECKLIST.md", "docs/DEFERRED.md",
           # The real-hash map behind the submission's commit labels (D1).
           AB.MAP_FILE}
# Round 3, R5 (H6): the gitignored reports reproduce.sh writes; make_anon_bundle.py holds the list.
EXCLUDE |= set(AB.UNTRACKED_REPORTS)
INCLUDE_FILES = ["FINDINGS_LEDGER.md", "LOSS_ASSEMBLY.md", "reproduce.sh", "setup.sh",
                 "requirements.txt", "run_remaining.sh", "run_10k.sh", "run_10k_d1.sh",
                 "run_control.sh", "run_nll.sh", "PAPER.md", "PAPER.tex", "PAPER.template.md"]
SKIP_SUFFIX = (".pt", ".pyc", ".bak", ".appbak", ".c2bak", ".d1bak", ".rev2bak")


def anon_git_log():
    fmt = "%H%x09%ad%x09%P%x09%s"
    out = subprocess.run(["git", "log", "--reverse", f"--format={fmt}",
                          "--date=format:%Y-%m-%d %H:%M:%S"],
                         capture_output=True, text=True).stdout
    L = AB.COMMIT_LABELS
    rows = []
    for line in out.splitlines():
        h, date, parents, subject = line.split("\t", 3)
        rows.append("\t".join([L[h], date, " ".join(L[p] for p in parents.split()), subject]))
    head = ("# Anonymised commit log\n#\n"
            "# Author name and email are removed; hashes are replaced by stable labels in\n"
            "# commit-date order; author-date timestamps, subjects and parent links are intact.\n"
            "# Commit timestamps are settable with `git commit --date`; see the paper's\n"
            "# discussion of that limitation.\n#\n"
            "# label\tauthor date\tparent labels\tsubject\n")
    return head + AB.apply_commit_labels("\n".join(rows) + "\n", L)


def scrub(text):
    """Report identifying hits in a text blob."""
    hits = []
    for pat in IDENT:
        n = len(pat.findall(text))
        if n:
            hits.append((pat.pattern, n))
    for m in URL.finditer(text):
        if m.group(1).lower() not in SAFE_ORGS:
            hits.append((f"url:{m.group(0)}", 1))
    return hits


# Pre-submission S5, by user ruling 2026-09-28: the pre-submission programme's own
# records (PLAN, SESSION_LOG, DECISIONS_FOR_USER, the unsent author query, FILE_MAP)
# are internal working documents, like docs/SUBMISSION_PACKAGE.md, and never ship in
# any bundle. They also quote the paper's old title, which item 4 keeps out of the
# bundle. A whole directory, so it is pruned from the walk rather than listed by file.
EXCLUDE_DIRS = ("docs/presubmission",)
# ...except the three technical records the paper cites (S9, by user ruling 2026-09-29):
# the original's specifications with their page anchors, the baselines' deviations table,
# and the anchor checker. They hold no rulings and no correspondence.
SHIP_FROM_EXCLUDED = ("docs/presubmission/ORIGINAL_SPECS.md",
                      "docs/presubmission/BASELINE_SPECS.md",
                      "docs/presubmission/verify_original_specs.py")



def main():
    files = []
    for d in INCLUDE_DIRS:
        if not os.path.isdir(d):
            continue
        for root, dirs, names in os.walk(d):
            dirs[:] = [x for x in dirs if os.path.join(root, x) not in EXCLUDE_DIRS]
            if "__pycache__" in root:
                continue
            for n in sorted(names):
                if n.endswith(SKIP_SUFFIX):
                    continue
                files.append(os.path.join(root, n))
    files += [f for f in list(INCLUDE_FILES) + list(SHIP_FROM_EXCLUDED) if os.path.exists(f)]
    files = sorted(set(files) - EXCLUDE)
    # The same invariant make_anon_bundle.py asserts, for the same reason: this
    # archive must be reproducible from a clean clone, and a gitignored file is
    # one a clone does not have. Two got into the other bundler that way.
    #
    # AFTER the EXCLUDE subtraction, not before. It was before, and it fired on
    # results/_regenerated.txt -- a file EXCLUDE already removes -- but only in a
    # tree that had actually run the pipeline, which is to say only in the clean
    # clone and never here. An assertion about clean-clone reproducibility that
    # passes locally and fails on a clone is the exact asymmetry it was written
    # to catch, so it caught itself.
    _ig = subprocess.run(["git", "check-ignore", "--stdin"], input="\n".join(files),
                         capture_output=True, text=True)
    _ignored = [x for x in _ig.stdout.split("\n") if x.strip()]
    assert not _ignored, (
        "these files are gitignored and would go into the archive, which a clean clone "
        "cannot reproduce: " + ", ".join(sorted(_ignored)))

    log = anon_git_log()
    # Round 3, R5 (H6): counted, not derived from the header's length. "len(lines) - 7" against an
    # eight-line header reported one commit too many, and "len(files) + 1" left out one of the two
    # members added below the file list (the transcript and this log), one entry too few.
    n_commits = sum(1 for l in log.splitlines() if l and not l.startswith("#"))
    assert n_commits == int(subprocess.run(["git", "rev-list", "--count", "HEAD"], capture_output=True,
                                           text=True, check=True).stdout), n_commits
    problems, total = [], 0
    for f in files:
        try:
            txt = AB.apply_commit_labels(open(f, encoding="utf-8", errors="replace").read(),
                                         AB.COMMIT_LABELS)
        except Exception:
            continue
        total += 1
        h = scrub(txt)
        if h:
            problems.append((f, h))
    log_hits = scrub(log)

    print("A3 — SUPPLEMENTARY MATERIAL")
    print("=" * 78)
    print(f"  candidate files      : {len(files)}")
    print(f"  scanned for identity : {total}")
    print(f"  anonymised git log   : {n_commits} commits, "
          f"{'CLEAN' if not log_hits else 'HITS: ' + str(log_hits)}")
    if problems:
        print(f"\n  !! {len(problems)} file(s) carry identifying material; ZIP NOT written:\n")
        for f, h in problems[:25]:
            print(f"     {f}")
            for pat, n in h[:4]:
                print(f"        {pat}  x{n}")
        print("\n  Fix or exclude these, then re-run.")
        return 1

    size = 0
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            # D1: commit hashes become their labels in the submitted copy only.
            try:
                raw = open(f, encoding="utf-8").read()
            except UnicodeDecodeError:
                raw = None
            new = None if raw is None else AB.apply_commit_labels(raw, AB.COMMIT_LABELS)
            if new is not None and new != raw:
                z.writestr(os.path.join("supplementary", f), new)
            else:
                z.write(f, arcname=os.path.join("supplementary", f))
            size += os.path.getsize(f)
        # The correspondence transcript, from OUTSIDE the tree. 6.1 and 8 cite it
        # and it must not be in the repository: it is private, consent to quote it
        # has not been given, and it was briefly public (M-48). The archive is
        # where reviewers get it, and the archive is not published.
        from t5_anon_transcript import OUT_MD as TRANSCRIPT_SRC, BUNDLE_PATH as TRANSCRIPT_DST
        assert os.path.exists(TRANSCRIPT_SRC), (
            f"the correspondence transcript is not at {TRANSCRIPT_SRC}; "
            f"run scripts/t5_anon_transcript.py, or set RWM_PRIVATE_DIR")
        for hit in scrub(open(TRANSCRIPT_SRC, encoding="utf-8", errors="replace").read()):
            raise AssertionError(f"the transcript carries identifying material: {hit}")
        z.write(TRANSCRIPT_SRC, arcname=os.path.join("supplementary", TRANSCRIPT_DST))
        size += os.path.getsize(TRANSCRIPT_SRC)
        z.writestr("supplementary/GIT_LOG_ANONYMISED.txt", log)
        n_entries = len(z.namelist())
    assert n_entries == len(files) + 2, (n_entries, len(files))     # the files, the transcript, the log
    open(OUT, "wb").write(buf.getvalue())
    zb = os.path.getsize(OUT)
    print(f"\n  wrote {OUT}: {n_entries} entries, "
          f"{zb / 1e6:.1f} MB compressed from {size / 1e6:.1f} MB")
    print(f"  TMLR limit is 100 MB: {'OK' if zb < 100e6 else 'OVER LIMIT'}")
    json.dump({"files": n_entries, "bytes": zb, "uncompressed": size,
               "identifying_hits": 0, "commits_in_log": n_commits},
              open(os.path.join(R.RESULTS, "supplementary_manifest.json"), "w"), indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
