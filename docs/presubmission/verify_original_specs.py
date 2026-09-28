"""Check ORIGINAL_SPECS.md's sentence fingerprints against local copies of the originals.

ORIGINAL_SPECS.md cites the original paper by location and by a fingerprint of the
supporting sentence, not by quotation (arXiv 2501.10100 carries arXiv's non-exclusive
licence, not a Creative Commons one). This script makes those citations checkable: it
extracts the text of the arXiv HTML renderings exactly as S1 did, one sentence per line
within each section, and confirms that every fingerprint listed in ANCHORS is found at
the stated section and sentence number.

    python docs/presubmission/verify_original_specs.py        # downloads if absent

Fingerprint: the first 16 hex digits of SHA-256 over the sentence lower-cased and
reduced to the characters a-z, 0-9 and '='.
"""
import hashlib
import os
import re
import sys
import urllib.request
from html.parser import HTMLParser

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sources")

FIG6_SHA256_16 = "20b746abe09a811b"

# (id, version, section heading as extracted, sentence number within it (1-based), fingerprint)
ANCHORS = [
    ("a1", "v1", "IV-C Dual-autoregressive Mechanism", 5, "e267a4ce50875f8d"),
    ("a1v2", "v2", "A.4.1 Dual-autoregressive Mechanism", 8, "7d7703430a4687e6"),
    ("a2", "v1", "IV-C Dual-autoregressive Mechanism", 6, "34e0821e66c8a9c3"),
    ("a4", "v1", "IV-C Dual-autoregressive Mechanism", 15, "4aef04b63766df0f"),
    ("a4b", "v1", "IV-C Dual-autoregressive Mechanism", 16, "80311d55bdf8df84"),
    ("a4v2", "v2", "A.4.1 Dual-autoregressive Mechanism", 11, "4aef04b63766df0f"),
    ("a4bv2", "v2", "A.4.1 Dual-autoregressive Mechanism", 12, "80311d55bdf8df84"),
    ("a5M", "v1", "IV-C Dual-autoregressive Mechanism", 7, "a1e5eae19cebbf0a"),
    ("a5P", "v1", "IV-C Dual-autoregressive Mechanism", 8, "a091cc9051fb6316"),
    ("a5N", "v1", "IV-C Dual-autoregressive Mechanism", 10, "d7a8b29d82a4f0e8"),
    ("a5B", "v1", "IV-C Dual-autoregressive Mechanism", 19, "78a64bd787cceacd"),
    ("a5Bv2", "v2", "A.4.1 Dual-autoregressive Mechanism", 15, "78a64bd787cceacd"),
    ("a6", "v1", "III-B Self-supervised Autoregressive Training", 18, "ca441931d104be9c"),
    ("a6f", "v1", "III-B Self-supervised Autoregressive Training", 21, "0f7314a0fe1da69b"),
    ("a6t", "v1", "IV-C Dual-autoregressive Mechanism", 13, "2128a12ffdf78dcd"),
    ("a6p", "v1", "IV-C Dual-autoregressive Mechanism", 14, "9c79973fb31bf1a6"),
    ("a7", "v1", "III-B Self-supervised Autoregressive Training", 13, "d0a1db174dc73f6f"),
    ("a8L", "v1", "III-B Self-supervised Autoregressive Training", 10, "5c9d9b819f10e470"),
    ("a8T", "v1", "A-C1 RWM", 1, "7b23b815569be0b9"),
    ("b1", "v1", "IV-D Generality across Robotic Environments", 1, "515dcb7a6c6bc288"),
    ("b2", "v1", "A-B2 Baselines", 1, "f9da1ad30f416d4a"),
    ("b3", "v1", "IV-D Generality across Robotic Environments", 20, "535776a35b4658b3"),
    ("b3v2", "v2", "4.3 Generality across Robotic Environments", 13, "535776a35b4658b3"),
    ("b4", "v1", "IV-D Generality across Robotic Environments", 3, "13a846592c1e38b5"),
    ("b5", "v1", "IV-D Generality across Robotic Environments", 4, "38bc8c0e5956fc15"),
    ("b6", "v1", "IV-D Generality across Robotic Environments", 5, "79fe26e7473b3e89"),
    ("b7", "v1", "IV-D Generality across Robotic Environments", 6, "7830b923fbabce73"),
    ("b8", "v1", "IV-D Generality across Robotic Environments", 9, "28c5383c8df6019d"),
    ("b9", "v1", "IV-D Generality across Robotic Environments", 22, "ba248682bab03f42"),
    ("b10", "v1", "IV-D Generality across Robotic Environments", 24, "8aaf51a50c90c019"),
    ("b11", "v1", "IV-B Robustness under Noise", 5, "8c8a5277294a067d"),
]


class _Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.out, self.skip, self.inmath = [], 0, False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        if tag in ("p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "div", "tr", "figcaption",
                   "br", "table"):
            self.out.append("\n")
        if tag in ("td", "th"):
            self.out.append(" | ")
        if tag == "math":
            alt = dict(attrs).get("alttext")
            if alt:
                self.out.append(" [" + alt + "] ")
                self.skip += 1
                self.inmath = True

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip -= 1
        if tag == "math" and self.inmath:
            self.skip -= 1
            self.inmath = False

    def handle_data(self, d):
        if not self.skip:
            self.out.append(d)


def lines(version):
    path = os.path.join(SRC, f"2501.10100{version}.html")
    if not os.path.exists(path):
        os.makedirs(SRC, exist_ok=True)
        urllib.request.urlretrieve(f"https://arxiv.org/html/2501.10100{version}", path)
    p = _Text()
    p.feed(open(path, encoding="utf-8").read())
    t = re.sub(r"[ \t]+", " ", "".join(p.out))
    t = re.sub(r"\n\s*\n+", "\n", t)
    return [x.strip() for x in t.split("\n")]


def fingerprint(s):
    return hashlib.sha256(re.sub(r"[^a-z0-9=]", "", s.lower()).encode()).hexdigest()[:16]


def section_sentences(ls, heading):
    """Sentences under the LAST occurrence of `heading` (the first is the contents list)."""
    idx = [i for i, x in enumerate(ls) if x == heading]
    assert idx, f"heading not found: {heading!r}"
    out = []
    for x in ls[idx[-1] + 1:]:
        if re.match(r"^(?:[IVX]+(?:-[A-Z]\d?)?|A(?:\.\d)+|\d(?:\.\d)*|A-[A-Z]\d?) [A-Z]", x) \
                and len(x) < 90:
            break
        if x and not x.startswith("|"):
            out.append(x)
    return out


def main():
    cache, bad = {}, 0
    for aid, ver, heading, n, fp in ANCHORS:
        ls = cache.setdefault(ver, lines(ver))
        sents = section_sentences(ls, heading)
        ok = 0 < n <= len(sents) and fingerprint(sents[n - 1]) == fp
        bad += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {aid:<6} {ver} {heading[:40]:<40} sentence {n}")
    print(f"  {len(ANCHORS) - bad} of {len(ANCHORS)} fingerprints found where stated")
    # The M/N heatmap (v1 Fig. 6 = v2 Fig. S8; one image file in both renderings), whose
    # printed cell values ORIGINAL_SPECS a.1 and a.5 record.
    for ver in ("v1", "v2"):
        img = os.path.join(SRC, f"{ver}_horizon_ablation.png")
        if not os.path.exists(img):
            urllib.request.urlretrieve(
                f"https://arxiv.org/html/2501.10100{ver}/horizon_ablation.png", img)
        h = hashlib.sha256(open(img, "rb").read()).hexdigest()[:16]
        ok = h == FIG6_SHA256_16
        bad += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {ver} horizon_ablation.png sha256 {h}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
