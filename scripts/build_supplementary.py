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

OUT = "supplementary.zip"
IDENT = [re.compile(p, re.I) for p in (
    r"joyjeet", r"\bsingh\b", r"github\.com/joyjeet", r"joyjeet-singh",
    r"/Users/joyjeetsingh",
    # A SWHID is opaque but resolvable: the Software Heritage UI returns the origin
    # URL for it, which carries the author's name. It de-anonymises exactly as a link
    # does, and the first version of this check did not catch it.
    r"swh:1:(?:snp|rev|rel|dir|cnt):[0-9a-f]{40}",
)]
# Repository URL in any form. The paper must not link to a named repo.
URL = re.compile(r"github\.com/([A-Za-z0-9_.-]+)/[A-Za-z0-9_.-]+", re.I)
# Third-party repositories the work legitimately cites: the two upstreams and the
# TMLR style file. Only a repository under the AUTHOR's account is identifying.
SAFE_ORGS = {"leggedrobotics", "jmlrorg", "isaac-sim", "goodfeli"}

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
           "docs/ARCHIVAL_IDENTIFIERS.md"}
INCLUDE_FILES = ["FINDINGS_LEDGER.md", "LOSS_ASSEMBLY.md", "reproduce.sh", "setup.sh",
                 "requirements.txt", "run_remaining.sh", "run_10k.sh", "run_10k_d1.sh",
                 "run_control.sh", "run_nll.sh", "PAPER.md", "PAPER.tex", "PAPER.template.md"]
SKIP_SUFFIX = (".pt", ".pyc", ".bak")


def anon_git_log():
    fmt = "%H%x09%ad%x09%s"
    out = subprocess.run(["git", "log", "--reverse", f"--format={fmt}",
                          "--date=format:%Y-%m-%d %H:%M:%S"],
                         capture_output=True, text=True).stdout
    head = ("# Anonymised commit log\n#\n"
            "# Author name and email are removed; hashes and timestamps are intact, because\n"
            "# section 7's pre-registration argument depends on the ordering of the latter.\n"
            "# Commit timestamps are settable with `git commit --date`; see the paper's\n"
            "# discussion of that limitation.\n#\n"
            "# hash\tdate\tsubject\n")
    return head + out


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


def main():
    files = []
    for d in INCLUDE_DIRS:
        if not os.path.isdir(d):
            continue
        for root, _, names in os.walk(d):
            if "__pycache__" in root:
                continue
            for n in sorted(names):
                if n.endswith(SKIP_SUFFIX):
                    continue
                files.append(os.path.join(root, n))
    files += [f for f in INCLUDE_FILES if os.path.exists(f)]
    files = sorted(set(files) - EXCLUDE)

    log = anon_git_log()
    problems, total = [], 0
    for f in files:
        try:
            txt = open(f, encoding="utf-8", errors="replace").read()
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
    print(f"  anonymised git log   : {len(log.splitlines()) - 7} commits, "
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
    open(OUT, "wb").write(buf.getvalue())
    zb = os.path.getsize(OUT)
    print(f"\n  wrote {OUT}: {len(files) + 1} entries, "
          f"{zb / 1e6:.1f} MB compressed from {size / 1e6:.1f} MB")
    print(f"  TMLR limit is 100 MB: {'OK' if zb < 100e6 else 'OVER LIMIT'}")
    json.dump({"files": len(files) + 1, "bytes": zb, "uncompressed": size,
               "identifying_hits": 0, "commits_in_log": len(log.splitlines()) - 7},
              open(os.path.join(R.RESULTS, "supplementary_manifest.json"), "w"), indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
