"""
C3 -- stage an anonymised copy of the repository, scrub it, and prove the scrub ran.

scripts/build_supplementary.py already assembles an anonymised ZIP, and it works,
but it anonymises by EXCLUSION: files that carry the author or the repository URL
by design -- MODEL_CARD.md, CITATION.cff, NOTICE, the archival identifiers -- are
left out of the archive entirely. That is safe and it is lossy: a reviewer loses
the model card and the citation metadata.

This does it by SUBSTITUTION instead. Every file is copied into a staging
directory with the deny-list replaced by neutral placeholders, file PATHS are
checked as well as contents, and the whole staged tree is then re-scanned and the
build fails loudly if a single occurrence survives.

Three things the exclusion approach could not do:

  1  JSON metadata is scrubbed rather than skipped, so results/*.json ship with
     their provenance intact and their paths neutralised.
  2  File and directory NAMES are checked. A path is as identifying as a line.
  3  A SELF-TEST runs on every invocation: a file containing a known deny-list
     string is planted inside the staging tree, the scan is run, and the build
     fails if the scan does not find it. A scrubber that has quietly stopped
     scrubbing is worse than no scrubber, and nothing else in this repository
     would notice.

    python scripts/make_anon_bundle.py             stage, scan, self-test, report
    python scripts/make_anon_bundle.py --zip       also write the archive

Writes results/anon_bundle.json, and with --zip, supplementary_anon.zip.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402
from t5_anon_transcript import DENY as TRANSCRIPT_DENY  # noqa: E402
from t5_anon_transcript import OUT_MD as TRANSCRIPT_SRC  # noqa: E402
from t5_anon_transcript import BUNDLE_PATH as TRANSCRIPT_DST  # noqa: E402

OUT_ZIP = "supplementary_anon.zip"

# D1 -- commit identifiers are anonymised in SUBMITTED output only. The record
# (PAPER.md, the ledger, results/) keeps real hashes; the submission PDF and both
# bundles carry stable labels C001, C002, ... assigned in commit-date order. The
# map lives in MAP_FILE, which is excluded from every bundle.
MAP_FILE = "docs/COMMIT_LABEL_MAP.json"


def commit_label_map():
    """{full hash: label}, every commit reachable from HEAD, in commit-date order
    (ties kept in git's reverse log order). Empty when there is no git history,
    as in an unpacked bundle, whose content already carries labels."""
    out = subprocess.run(["git", "log", "--reverse", "--format=%H%x09%ct"],
                         capture_output=True, text=True).stdout
    rows = [l.split("\t") for l in out.splitlines() if l.strip()]
    rows = sorted(enumerate(rows), key=lambda r: (int(r[1][1]), r[0]))
    return {h: f"C{i:03d}" for i, (_, (h, _ct)) in enumerate(rows, 1)}


def hub_commit_label_map(repo):
    """{identifier: label} for commits of the author's Hugging Face model repository,
    labelled H001, H002, ... by first mention. The Hub is not queried: the identifiers
    are the ones this history records ("hub ... commit <hex>"), as known -- often
    abbreviated. A token that is a prefix of a repository commit is not taken."""
    out = subprocess.run(["git", "log", "--reverse", "--format=%B"],
                         capture_output=True, text=True).stdout
    found = []
    for t in re.findall(r"\bhub\b[^\n]{0,40}?\bcommit\s+`?([0-9a-f]{7,40})\b", out, re.I):
        t = t.lower()
        if t not in found and not any(h.startswith(t) for h in repo):
            found.append(t)
    return {t: f"H{i:03d}" for i, t in enumerate(found, 1)}


# Author-controlled commit identifiers that neither map above can see, because they
# are not in this repository's history. D1 anonymises them like any other commit hash.
#
# PREPURGE_COMMITS: the commits of the pre-purge backup (rwm_repro_prepurge_backup,
# whose origin is the author's GitHub repository) that the history rewrite removed --
# `git rev-list --all` there minus this repository's history -- in commit-date order.
# Listed here rather than read from the backup, because a reviewer's machine does not
# have it. The ledger's M-48 cites one of them, as pushed.
# UNRESOLVED_COMMITS: identifiers this history records that resolve in no local store.
PREPURGE_COMMITS = (
    "7859309f146ce1b84bdb853caf8a8b333d30a809",
    "66a25565930f47e6bff86efcc44ae3140ad3e257",
    "395ef35bec9924a211dcf01f76fa39d470263838",
    "da635be2833c1e024dc954ee0563947553654e2e",
    "925456ae42c16b5c1d66c0232345fb89f60c5e3d",
    "1979f01cddc7ec85b4398f75f6c5c0fc269ab675",
    "20955e254dbb4b6698cd39f89c6c7077ea2c50c1",
    "0288b47c5e02334b03a8dd1da74fc0961d41309f",
    "29bba9219be2a8be08b7c9b66922c231a4cc92de",
    "b84807453e01cd64065501e4435c575cba49b4d5",
    "6b5d84d0f5cf3f45e6bbe01e6b20b8c269ae976c",
    "4c2fd6aad050357ed5d9c82d23506ec952add620",
    "2fa6d1e6cfec1d1947fc14d5f9e09e953e81ff71",
    "c4c9954ae27a6060092ca34f794284138b4d1081",
    "f113319a1948f8fb5c950194c4dd5ad901b5b37f",
    "1ef8e21f56f33e271cead6b63ce279a435ceb862",
    "2642cdacb00abaedd69b5986a02e83d69be189c5",
    "45214f932d8705b97f915dd414d0d9fac182e571",
)
UNRESOLVED_COMMITS = ("edbfee88",)


def extra_commit_label_map(repo):
    """{identifier: label}: P001, P002, ... for PREPURGE_COMMITS and U001, ... for
    UNRESOLVED_COMMITS, in listed order. Empty without git history, like the maps
    above, so an unpacked bundle's map and sweep are not reduced to these alone."""
    if not repo:
        return {}
    out = {h: f"P{i:03d}" for i, h in enumerate(PREPURGE_COMMITS, 1)}
    out.update({t: f"U{i:03d}" for i, t in enumerate(UNRESOLVED_COMMITS, 1)})
    return out


def write_commit_label_map(cmap):
    with open(MAP_FILE, "w") as f:
        json.dump({"order": "commit date; H labels are Hugging Face model repository "
                            "commits, by first mention in this history; P labels are "
                            "commits of the pre-purge history, by commit date; U labels "
                            "are identifiers that resolve in no local store",
                   "labels": cmap}, f, indent=2)
        f.write("\n")


# A hash as written in text: 7 to 40 hex characters standing alone. Not preceded
# by a letter, digit or '.', and not followed by a letter, digit or '.digit', so
# the fractional part of a decimal is never a candidate.
_HASH_TOKEN = re.compile(r"(?<![0-9A-Za-z.])[0-9A-Fa-f]{7,40}(?![0-9A-Za-z]|\.\d)")


def apply_commit_labels(text, cmap):
    """Replace every full or abbreviated (7+) commit hash in `cmap` by its label.
    Tokens that are not a prefix of a known commit -- upstream pins, SHA-256
    checksums, claim IDs -- are left untouched."""
    if not cmap:
        return text
    by7 = {}
    for h in cmap:
        by7.setdefault(h[:7], []).append(h)

    def rep(m):
        t = m.group(0).lower()
        hits = [h for h in by7.get(t[:7], []) if h.startswith(t) or t.startswith(h)]
        assert len(hits) <= 1, f"ambiguous commit prefix {t}: {hits}"
        return cmap[hits[0]] if hits else m.group(0)
    return _HASH_TOKEN.sub(rep, text)


def commit_sweep_pattern(cmap):
    """One detection regex for author commit identifiers, full or abbreviated.

    Branch 1: a maximal hex run (letters around it may be non-hex, because PDF
    text extraction runs table cells together) that CONTAINS a commit's stem --
    its shortest prefix of 7+ characters holding a letter a-f. A run made only of
    digits and one exponent 'e' is refused, so no decimal or float can match.
    Branch 2: the few commits whose first seven characters are all digits, as a
    standalone integer exactly equal to such a prefix; a neighbouring '.', ','
    or digit refuses it, so the parts of a decimal cannot match."""
    assert cmap, "no commit history: an anonymity sweep for commit hashes would be empty"
    stems, digits = set(), set()
    for h in cmap:
        k = next(i for i in range(7, 41) if not h[:i].isdigit())
        stems.add(h[:k])
        digits.update(h[:i] for i in range(7, k))
    alt = lambda s: "|".join(sorted(s, key=lambda x: (-len(x), x)))
    pat = (r"(?<![0-9a-f])(?![0-9]*e[0-9]*(?![0-9a-f]))[0-9a-f]*?(?:" + alt(stems) +
           r")[0-9a-f]*")
    if digits:
        pat += r"|(?<![0-9a-z.,])(?:" + alt(digits) + r")(?![0-9a-z]|[.,]\d)"
    return pat


COMMIT_LABELS = commit_label_map()
COMMIT_LABELS.update(hub_commit_label_map(COMMIT_LABELS))
COMMIT_LABELS.update(extra_commit_label_map(COMMIT_LABELS))

# The deny list. Every entry is a literal string or a regex, and every one is
# replaced rather than merely detected. Shared with t5_anon_transcript.py so the
# transcript and the bundle cannot disagree about what counts as identifying.
SUBS = [
    # --- the reproducing author -------------------------------------------
    (r"github\.com/joyjeet-singh/rwm", "github.com/ANONYMISED/ANONYMISED"),
    (r"github\.com/joyjeet-singh", "github.com/ANONYMISED"),
    (r"huggingface\.co/Joyjeetsingh[A-Za-z0-9_./-]*", "huggingface.co/ANONYMISED"),
    (r"/Users/joyjeetsingh", "/Users/ANONYMISED"),
    (r"joyjeet[-_.]?singh", "ANONYMISED"),
    (r"Joyjeet\s+Singh", "ANONYMISED"),
    (r"joyjeetsingh\d*@[A-Za-z0-9.-]+", "ANONYMISED@example.invalid"),
    (r"\bJoyjeetsingh\b", "ANONYMISED"),
    (r"\bJoyjeet\b", "ANONYMISED"),
    (r"\bjoyjeet\b", "ANONYMISED"),
    # The bare SURNAME. CITATION.cff splits the name across two YAML fields, so
    # every pattern above matched `given-names` and none matched `family-names`,
    # and the anonymised bundle shipped "family-names: Singh / given-names:
    # ANONYMISED" -- a one-field de-anonymisation sitting beside the evidence that
    # the file had been scrubbed. Structured metadata defeats a scrubber written
    # for prose.
    #
    # Checked against the bibliography before adding: no author of the 16 verified
    # references carries this surname, so scrubbing it cannot corrupt a citation.
    (r"\bSingh\b", "ANONYMISED"),
    # ORCID identifiers resolve to a named person.
    (r"\b\d{4}-\d{4}-\d{4}-\d{3}[\dX]\b", "ORCID-ANONYMISED"),
    # A Software Heritage identifier is opaque but RESOLVABLE: the UI returns the
    # origin URL, which carries the account name. It de-anonymises exactly as a
    # link does.
    (r"swh:1:(?:snp|rev|rel|dir|cnt):[0-9a-f]{40}", "swh:1:ANONYMISED"),
    # --- the original authors, in the correspondence -----------------------
    # Their published work is cited normally; what is scrubbed is the private
    # correspondence's addressing, which is not ours to publish.
    (r"chenhli@[A-Za-z0-9.-]+", "ANONYMISED@example.invalid"),
    (r"krausea@[A-Za-z0-9.-]+", "ANONYMISED@example.invalid"),
    (r"breadli428[A-Za-z0-9./-]*", "ANONYMISED"),
    (r"\bDr\.? Li\b", "the first author"),
]
SUB_RE = [(re.compile(p), r) for p, r in SUBS]

# Detection patterns for the post-scrub scan. Deliberately BROADER than the
# substitutions: the scan must be able to fail even where the substitution list
# has a gap, which is the whole point of scanning after scrubbing rather than
# trusting the scrub.
DETECT = [re.compile(p, re.I) for p in (
    r"joyjeet", r"github\.com/joyjeet", r"huggingface\.co/joyjeet", r"\bSingh\b",
    r"/Users/joyjeetsingh", r"chenhli", r"breadli428",
    r"swh:1:(?:snp|rev|rel|dir|cnt):[0-9a-f]{40}",
    r"\b\d{4}-\d{4}-\d{4}-\d{3}[\dX]\b",
    commit_sweep_pattern(COMMIT_LABELS),
)]
# A repository URL under the author's account. Third-party repos the work
# legitimately cites are not identifying.
URL = re.compile(r"github\.com/([A-Za-z0-9_.-]+)/[A-Za-z0-9_.-]+", re.I)
SAFE_ORGS = {"leggedrobotics", "jmlrorg", "isaac-sim", "goodfeli", "jannerm",
             # arrives from the bibliography's verification record, which stores
             # arXiv comment fields verbatim as evidence
             # A CITED paper's own code repository. Seitzer et al. (ICLR 2022)
             # give it in their arXiv comment field, which the bibliography
             # verification records verbatim as evidence. It identifies THEM, not
             # us, and removing it would mean recording their metadata inaccurately
             # in the one file whose purpose is that the metadata is accurate.
             "martius-lab",
             "anonymised"}

INCLUDE_DIRS = ["src", "scripts", "results", "docs", "tex", "figures"]
INCLUDE_FILES = [
    "FINDINGS_LEDGER.md", "LOSS_ASSEMBLY.md", "PAPER.md", "PAPER.tex",
    "PAPER.template.md", "README.md", "README.template.md", "MODEL_CARD.md",
    "CITATION.cff", "NOTICE", "LICENSE", "reproduce.sh", "setup.sh",
    "requirements.txt", "run_remaining.sh", "run_10k.sh", "run_10k_d1.sh",
    "run_control.sh", "run_nll.sh", "run_ens5.sh", "run_indep_ens.sh",
    "run_tasks45.sh",
    # checkpoint_manifest.json was here and is gitignored -- written at release
    # time by the Hugging Face upload. A clean clone never has it, so the bundle
    # contained a file whose presence depended on whether the author had run an
    # upload step, and its own staged-file count differed between the two. The
    # checkpoint hashes it holds are already in MODEL_CARD.md, which IS in the
    # bundle. The assertion below makes the whole class impossible rather than
    # this one instance.
]
# This file and its sibling carry the very patterns they search for.
EXCLUDE = {"scripts/make_anon_bundle.py", "scripts/build_supplementary.py",
           # The cover statement is addressed to the action editor, not to a
           # reviewer, and build_supplementary.py already excludes it. The two
           # bundles must agree about what ships: they disagreed once, and the
           # reviewer's copy carried a file the supplementary archive did not.
           "docs/COVER_STATEMENT.md",
           # Transient: written by ONE reproduce.sh run and describing that run,
           # not the repository -- which is why .gitignore excludes it and why
           # reproduce.sh deletes it at the start of every full run. It has no
           # business in a submission bundle, and leaving it in made this
           # bundle's own file count differ between a tree that had just run the
           # pipeline and one that had not.
           "results/_regenerated.txt",
           "scripts/submission_check.py", "scripts/t5_anon_transcript.py",
           # Its own first line reads "Archival identifiers — NOT for the
           # anonymous submission", and it was in the anonymous submission. The
           # deliberate re-inclusion of the files build_supplementary.py excludes
           # was meant to give reviewers material they would otherwise lose; this
           # file is not that. It is a table of identifiers whose entire purpose
           # is to resolve to a repository under the author's name, and the SWHID
           # scrubber cannot reach the bare 40-hex revision SHA it prints beside
           # them -- SUBS matches `swh:1:...` with its prefix, and DETECT uses the
           # same pattern, so the post-scrub scan could not catch it either.
           "docs/ARCHIVAL_IDENTIFIERS.md",
           # The Software Heritage exposure checker and its artifact. Excluded
           # from supplementary.zip on the same grounds and not from here: an
           # archival check has to name the origin it asks the archive about, so
           # the repository URL and the account name are its INPUT. Found by the
           # surname pattern added above, immediately -- the scrubber's own
           # substitutions had been rewriting the URL and leaving the name in the
           # prose beside it.
           "scripts/swh_visit_check.py", "results/swh_visit_check.json",
           # Contains the deny-list probe it plants to prove its own scan is
           # live, so it trips that scan -- the same reason this file and
           # t5_anon_transcript.py are excluded above.
           "scripts/f5_pdf_channels.py",
           # Internal working documents; never ship in any bundle.
           "docs/SUBMISSION_CHECKLIST.md", "docs/DEFERRED.md",
           # The real-hash map behind the submission's commit labels (D1).
           MAP_FILE}
SKIP_SUFFIX = (".pt", ".pyc", ".bak", ".prebak", ".t2bak", ".t3bak", ".t4bak",
               ".tmpbak", ".zip", ".pdf")
BINARY_SUFFIX = (".png", ".jpg", ".gz")


def scrub_text(text):
    for pat, rep in SUB_RE:
        text = pat.sub(rep, text)
    return text


def scan(text):
    """Identifying hits in a blob. Broader than the substitutions on purpose."""
    hits = []
    for pat in DETECT:
        found = pat.findall(text)
        if found:
            hits.append((pat.pattern, len(found)))
    for m in URL.finditer(text):
        if m.group(1).lower() not in SAFE_ORGS:
            hits.append((f"url:{m.group(0)}", 1))
    return hits


def anon_git_log():
    """
    Every commit, with author identity removed and hashes and timestamps intact.

    §9's pre-registration argument rests on commit ordering and a reviewer cannot
    see the repository, so the hashes Figure 4 cites must resolve to something.
    Timestamps are author-settable with `git commit --date`; the paper says so.
    """
    fmt = "%H%x09%ad%x09%P%x09%s"
    out = subprocess.run(["git", "log", "--reverse", f"--format={fmt}",
                          "--date=format:%Y-%m-%d %H:%M:%S"],
                         capture_output=True, text=True).stdout
    rows = []
    for line in out.splitlines():
        h, date, parents, subject = line.split("\t", 3)
        rows.append("\t".join([COMMIT_LABELS[h], date,
                               " ".join(COMMIT_LABELS[p] for p in parents.split()),
                               subject]))
    head = ("# Anonymised commit log\n#\n"
            "# Author name and email removed; hashes replaced by stable labels (commit-date\n"
            "# order); author-date timestamps, subjects and parent links intact, because the\n"
            "# paper's pre-registration argument depends on ordering. Timestamps are settable\n"
            "# with `git commit --date`; the paper says so and bounds the argument accordingly.\n"
            "# label\tauthor date\tparent labels\tsubject\n")
    return head + apply_commit_labels(scrub_text("\n".join(rows) + "\n"), COMMIT_LABELS)


def collect():
    files = []
    for d in INCLUDE_DIRS:
        if not os.path.isdir(d):
            continue
        for root, dirs, names in os.walk(d):
            dirs[:] = [x for x in dirs if x != "__pycache__"]
            for n in sorted(names):
                p = os.path.join(root, n)
                if p in EXCLUDE or p.endswith(SKIP_SUFFIX) or n.startswith("."):
                    continue
                files.append(p)
    for f in INCLUDE_FILES:
        if os.path.exists(f) and f not in EXCLUDE:
            files.append(f)
    files = sorted(set(files))
    # Nothing git ignores may be staged.
    #
    # The bundle must be reproducible from a clean clone, and a gitignored file
    # is by definition one a clone does not have. Two got in: results/
    # _regenerated.txt, which describes one pipeline run, and
    # checkpoint_manifest.json, which is written by the release upload. Both
    # made the bundle's own file count depend on what the author had happened to
    # run, and that count was the only thing standing between this project and a
    # 100% clean-clone comparison. Asked of git rather than maintained by hand,
    # because a hand-maintained list is how both of them got in.
    ig = subprocess.run(["git", "check-ignore", "--stdin"], input="\n".join(files),
                        capture_output=True, text=True)
    ignored = [x for x in ig.stdout.split("\n") if x.strip()]
    assert not ignored, (
        "these staged files are gitignored, so a clean clone does not have them and "
        "the bundle is not reproducible from one: " + ", ".join(sorted(ignored)))
    return files


# Files that live OUTSIDE the repository tree and must nevertheless reach
# reviewers. There is exactly one, and the reason it is outside is the reason it
# has to be here: the correspondence transcript is private, consent to quote it
# has not been given, and 6.1 and 8 both cite it. It must not be in the
# repository (M-48) and it must be in the bundle. Sourced from
# t5_anon_transcript.py so there is one path, not two.
def external_files():
    return {TRANSCRIPT_SRC: TRANSCRIPT_DST}


def stage(files, staging):
    """Copy every file into `staging`, scrubbing contents and paths."""
    written, path_fixes, content_fixes = [], 0, 0
    ext = external_files()
    for src in list(files) + [p for p in ext if os.path.exists(p)]:
        dst_rel = ext.get(src) or scrub_text(src)
        if dst_rel != src:
            path_fixes += 1
        dst = os.path.join(staging, dst_rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if src.endswith(BINARY_SUFFIX):
            shutil.copy2(src, dst)
        else:
            raw = open(src, encoding="utf-8", errors="replace").read()
            new = apply_commit_labels(scrub_text(raw), COMMIT_LABELS)
            content_fixes += new != raw
            open(dst, "w", encoding="utf-8").write(new)
        written.append(dst_rel)
    with open(os.path.join(staging, "GIT_LOG_ANONYMISED.txt"), "w") as f:
        f.write(anon_git_log())
    written.append("GIT_LOG_ANONYMISED.txt")
    return written, path_fixes, content_fixes


def scan_tree(staging):
    """Every file's contents AND every path. Returns [(relpath, hits)]."""
    bad = []
    for root, dirs, names in os.walk(staging):
        for n in names:
            p = os.path.join(root, n)
            rel = os.path.relpath(p, staging)
            hits = scan(rel)                       # the path is as identifying as a line
            if not p.endswith(BINARY_SUFFIX):
                hits += scan(open(p, encoding="utf-8", errors="replace").read())
            if hits:
                bad.append((rel, hits))
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", action="store_true", help="also write the archive")
    args = ap.parse_args()

    files = collect()
    write_commit_label_map(COMMIT_LABELS)
    staging = tempfile.mkdtemp(prefix="anon_bundle_")
    try:
        written, path_fixes, content_fixes = stage(files, staging)

        # ---------------------------------------------------- the self-test
        # Plant a file whose content and whose NAME both carry a deny-list
        # string, then confirm the scan finds both. Run before the real scan, so
        # a scan that has stopped working cannot pass the real one vacuously.
        probe_dir = os.path.join(staging, "_selftest_joyjeet")
        os.makedirs(probe_dir, exist_ok=True)
        probe = os.path.join(probe_dir, "planted.txt")
        open(probe, "w").write(
            "planted by make_anon_bundle.py: joyjeet-singh, "
            "https://github.com/joyjeet-singh/rwm, "
            "swh:1:rev:0123456789abcdef0123456789abcdef01234567, "
            f"commit {max((h for h in COMMIT_LABELS if COMMIT_LABELS[h][0] == 'C'), key=COMMIT_LABELS.get)[:7]}\n")
        planted = scan_tree(staging)
        caught = [b for b in planted if "_selftest" in b[0]]
        assert caught, ("SELF-TEST FAILED: the scan did not detect a planted "
                        "deny-list string. The scrubber cannot be trusted.")
        assert any(p == DETECT[-1].pattern for _, hits in caught for p, _ in hits), (
            "SELF-TEST FAILED: a planted commit hash was not detected.")
        n_probe_hits = sum(n for _, hits in caught for _, n in hits)
        shutil.rmtree(probe_dir)

        # ------------------------------------------------------- the real scan
        bad = scan_tree(staging)

        # Files the PAPER cites by name must actually be in the bundle. §6.1 and
        # §8 each quote the author correspondence and say it is "reproduced in
        # full, anonymised, in the supplementary material"; a bundle that does
        # not carry it makes both citations false, and nothing here would have
        # noticed -- `docs/` is included by directory, so the file's presence was
        # incidental rather than asserted.
        cited = sorted({m for m in re.findall(r"`([\w./-]+\.(?:md|json|txt|py|cff))`",
                                              open("PAPER.md").read())
                        if m.startswith(("results/", "docs/", "scripts/", "src/"))
                        or m.isupper() or m.endswith(".md")})
        assert os.path.exists(TRANSCRIPT_SRC), (
            f"the correspondence transcript is not at {TRANSCRIPT_SRC}. It is generated "
            f"OUTSIDE this tree by scripts/t5_anon_transcript.py and must not be inside it "
            f"(M-48); run that script, or set RWM_PRIVATE_DIR.")
        REQUIRED = [TRANSCRIPT_DST, "FINDINGS_LEDGER.md",
                    "results/original_paper_figures.json"]
        staged_set = set(written)
        missing_required = [f for f in REQUIRED if f not in staged_set]
        assert not missing_required, (
            "the paper cites these by name and the bundle does not carry them: "
            + ", ".join(missing_required))
        missing_cited = [f for f in cited
                         if ("/" in f and f not in staged_set)]

        rec = {
            "n_files_staged": len(written),
            "n_paths_scrubbed": path_fixes,
            "n_files_content_scrubbed": content_fixes,
            "n_substitution_rules": len(SUBS),
            "n_detection_patterns": len(DETECT) + 1,
            "self_test": {
                "planted": "a file whose NAME and CONTENTS both carry deny-list strings",
                "detected": True,
                "n_hits_on_probe": n_probe_hits,
            },
            "residual_hits": [{"file": f, "hits": h} for f, h in bad],
            "n_residual_hits": len(bad),
            "required_files_present": REQUIRED,
            "cited_files_checked": len(cited),
            "cited_files_absent": missing_cited,
            "includes_previously_excluded": [
                f for f in ("MODEL_CARD.md", "CITATION.cff", "NOTICE")
                if any(w == f for w in written)],
            "excluded_as_identifying": ["docs/ARCHIVAL_IDENTIFIERS.md"],
            "zip_written": None,
        }

        print("C3 — ANONYMISED SUBMISSION BUNDLE")
        print("=" * 92)
        print(f"  staged            : {len(written)} files")
        print(f"  paths scrubbed    : {path_fixes}")
        print(f"  contents scrubbed : {content_fixes}")
        print(f"  substitution rules: {len(SUBS)}   detection patterns: "
              f"{len(DETECT) + 1}")
        print(f"  SELF-TEST         : planted probe detected "
              f"({n_probe_hits} hits) — the scan is live")
        print(f"  now included that the exclusion-based builder dropped: "
              f"{', '.join(rec['includes_previously_excluded']) or 'none'}")
        print(f"  files the paper cites by name : {len(cited)} checked, "
              f"{len(missing_cited)} absent from the bundle"
              + (f"  {missing_cited[:4]}" if missing_cited else ""))
        print(f"  required present  : {', '.join(REQUIRED)}")
        print(f"  residual identifying hits: {len(bad)}")
        for f, h in bad[:20]:
            print(f"    !! {f}: {h}")

        if args.zip and not bad:
            with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED) as z:
                for root, _, names in os.walk(staging):
                    for n in sorted(names):
                        p = os.path.join(root, n)
                        z.write(p, os.path.relpath(p, staging))
            rec["zip_written"] = OUT_ZIP
            rec["zip_bytes"] = os.path.getsize(OUT_ZIP)
            print(f"  wrote {OUT_ZIP} ({os.path.getsize(OUT_ZIP):,} bytes)")

        dst = os.path.join(R.RESULTS, "anon_bundle.json")
        with open(dst, "w") as f:
            json.dump(rec, f, indent=2, sort_keys=True)
        print(f"  wrote {R.rel(dst)}")

        assert not bad, (f"{len(bad)} files still carry identifying strings after "
                         f"scrubbing — refusing to ship")
        print("\n  PASS — zero identifying strings across the staged tree")
        return 0
    finally:
        shutil.rmtree(staging, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
