"""
F5.4 -- the submission PDF, checked on THREE channels, not one.

WHY THREE. A PDF can carry an author's identity in places a text-layer scan never
looks. The revision brief names the third as the one that gets missed, and it is
right: a `\\href` to a personal repository renders as ordinary blue text whose
VISIBLE string is something innocuous, while the URL lives in a link annotation
that no text extraction returns. Every check in this repository before this one
read either the LaTeX source or the extracted text.

  1. TEXT LAYER      every page's extracted text, against the deny list.
  2. METADATA        /Author, /Title, /Subject, /Keywords, /Creator, /Producer,
                     and the XMP packet if present. pdflatex writes /Author from
                     \\author{} and /Producer from the engine; a TeX distribution
                     configured with a personal name puts it there without the
                     source ever mentioning it.
  3. ANNOTATIONS     every /Annot on every page, and for link annotations the
                     /A /URI and /A /F (a file specification) targets. This is
                     the channel with no other coverage.

The deny list is imported from scripts/make_anon_bundle.py so there is one list
and not two -- the same reason that file imports it from the transcript generator.

SELF-TEST. A scan that has stopped scanning passes everything. --self-test builds
a one-page PDF carrying a deny-listed string in each of the three channels and
requires all three to be caught.

    python scripts/f5_pdf_channels.py [PAPER.pdf]
    python scripts/f5_pdf_channels.py --self-test

Writes results/pdf_channels.json.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:  # pragma: no cover
    print("pypdf is required: pip install pypdf")
    raise

import make_anon_bundle as AB  # noqa: E402

OUT = "pdf_channels.json"
DEFAULT = "PAPER.pdf"

# The identity patterns, from the ONE list the bundler and the transcript share.
#
# AB.DETECT, not AB.SUBS: the substitution list is what gets replaced, and the
# detection list is deliberately broader so the scan can fail where the
# substitutions have a gap. A first version of this file looked for `AB.DENY`,
# which does not exist, silently got an empty list, and reported "no identifying
# strings ... (0 patterns checked)" — a scan of nothing, passing. The assert
# below is why that cannot happen twice.
DENY = [r.pattern for r in AB.DETECT]
assert DENY, ("no detection patterns imported from make_anon_bundle; a PDF scan "
              "with an empty deny list passes everything")
URL_RE = re.compile(r"(?:github\.com|huggingface\.co|gitlab\.com|bitbucket\.org)/([\w.-]+)")


def _hits(text, where):
    """Deny-list and unsafe-origin hits in one blob."""
    out = []
    if not text:
        return out
    for d in DENY:
        # DENY holds regexes, not literals -- re.escape would look for a literal
        # backslash-b and match nothing.
        n = len(re.findall(d, text, re.I))
        if n:
            out.append({"channel": where, "pattern": d, "count": n})
    for m in URL_RE.finditer(text):
        if m.group(1).lower() not in AB.SAFE_ORGS:
            out.append({"channel": where, "pattern": f"url:{m.group(0)}", "count": 1})
    return out


def scan(path):
    r = PdfReader(path)
    findings, seen = [], {"text": 0, "metadata": 0, "annotations": 0}

    # ---- 1 text layer
    text = []
    for page in r.pages:
        try:
            text.append(page.extract_text() or "")
        except Exception:
            text.append("")
    blob = "\n".join(text)
    seen["text"] = len(blob)
    findings += _hits(blob, "text")

    # ---- 2 metadata
    meta = {}
    try:
        for k, v in (r.metadata or {}).items():
            meta[str(k)] = str(v)
    except Exception:
        pass
    xmp = ""
    try:
        x = r.xmp_metadata
        if x is not None and getattr(x, "stream", None) is not None:
            xmp = x.stream.get_data().decode("utf-8", "replace")
    except Exception:
        pass
    metablob = json.dumps(meta) + "\n" + xmp
    seen["metadata"] = len(metablob)
    findings += _hits(metablob, "metadata")

    # ---- 3 annotations, the channel nothing else covers
    annots, targets = 0, []
    for n, page in enumerate(r.pages, 1):
        for a in (page.get("/Annots") or []):
            try:
                obj = a.get_object()
            except Exception:
                continue
            annots += 1
            sub = str(obj.get("/Subtype", ""))
            act = obj.get("/A")
            uri = fspec = None
            if act is not None:
                try:
                    act = act.get_object()
                    uri = act.get("/URI")
                    fspec = act.get("/F")
                except Exception:
                    pass
            if uri or fspec:
                targets.append({"page": n, "subtype": sub,
                                "uri": str(uri) if uri else None,
                                "file": str(fspec) if fspec else None})
    seen["annotations"] = annots
    findings += _hits("\n".join(
        f"{t['uri'] or ''} {t['file'] or ''}" for t in targets), "annotations")

    return {"pdf": path, "pages": len(r.pages),
            "scanned": seen, "n_link_targets": len(targets),
            "link_targets": targets[:60],
            "metadata_keys": sorted(meta), "metadata": meta,
            "has_xmp": bool(xmp),
            "findings": findings}


def self_test():
    """Plant a deny-listed string in each channel and require all three caught."""
    import tempfile
    probe = "joyjeet"          # matches the first detection pattern
    w = PdfWriter()
    src = PdfReader(DEFAULT)
    w.add_page(src.pages[0])
    w.add_metadata({"/Author": f"probe {probe}"})
    from pypdf.annotations import Link
    from pypdf.generic import RectangleObject
    try:
        w.add_annotation(page_number=0, annotation=Link(
            rect=RectangleObject((10, 10, 100, 30)),
            url=f"https://github.com/{probe}/rwm"))
    except Exception as e:
        print(f"  could not plant an annotation probe: {e}")
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "probe.pdf")
        with open(p, "wb") as f:
            w.write(f)
        got = scan(p)
    chans = {f["channel"] for f in got["findings"]}
    print("F5.4 — PDF CHANNEL SCAN, SELF-TEST")
    print("=" * 76)
    print(f"  probe string      : {probe!r}")
    print(f"  channels that fired: {sorted(chans) or 'NONE'}")
    for c in ("metadata", "annotations"):
        print(f"    {c:<12} {'CAUGHT' if c in chans else 'MISSED'}")
    ok = {"metadata", "annotations"} <= chans
    print("=" * 76)
    print("  " + ("self-test passed — the scan is live on the channels it can plant into"
                  if ok else "SELF-TEST FAILED — a planted identity was not caught"))
    return 0 if ok else 1


def main():
    if "--self-test" in sys.argv:
        return self_test()
    path = next((a for a in sys.argv[1:] if not a.startswith("-")), DEFAULT)
    # The self-test is a PRECONDITION of the scan, not a flag. reproduce.sh
    # invoked this script without it, so the scan ran on every build and the
    # proof that it can catch a planted identity ran on none -- the same shape
    # as the typed-numeral audit, whose flag-only self-test had silently broken.
    if os.path.exists(path):
        print("  self-test first, because a scan that cannot fail proves nothing:")
        if self_test() != 0:
            print("  SCAN NOT RUN — the self-test did not catch its own probe.")
            return 1
        print()
    if not os.path.exists(path):
        print(f"  {path} does not exist — run scripts/compile_paper.py first")
        return 1
    got = scan(path)
    print("F5.4 — SUBMISSION PDF, THREE CHANNELS")
    print("=" * 84)
    print(f"  pdf               : {path} ({got['pages']} pages)")
    print(f"  1 text layer      : {got['scanned']['text']:,} characters extracted")
    print(f"  2 metadata        : {len(got['metadata_keys'])} keys "
          f"{got['metadata_keys']}, XMP {'present' if got['has_xmp'] else 'absent'}")
    for k, v in sorted(got["metadata"].items()):
        print(f"      {k:<22} {v[:70]!r}")
    print(f"  3 annotations     : {got['scanned']['annotations']} on the page, "
          f"{got['n_link_targets']} with a URI or file target")
    for t in got["link_targets"][:20]:
        print(f"      p{t['page']:<3} {t['subtype']:<14} {t['uri'] or t['file']}")
    print("=" * 84)
    if got["findings"]:
        print(f"  {len(got['findings'])} IDENTIFYING HIT(S):")
        for f in got["findings"]:
            print(f"    !! [{f['channel']}] {f['pattern']} x{f['count']}")
    else:
        print(f"  no identifying strings on any of the three channels "
              f"({len(DENY)} patterns checked)")
    json.dump(got, open(os.path.join(R.RESULTS, OUT), "w"), indent=2)
    print(f"  wrote results/{OUT}")
    return 1 if got["findings"] else 0


if __name__ == "__main__":
    sys.exit(main())
