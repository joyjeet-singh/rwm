"""
The two sources the RSSM baselines take settings from, verified the way the paper's own
bibliography is verified (scripts/t1_bibliography.py): title and author list against the
arXiv API, and every value this project relies on located on its page of the paper.

  DreamerV2  Hafner et al., "Mastering Atari with Discrete World Models", ICLR 2021,
             arXiv 2010.02193 -- the categorical RSSM of the original's Table S7.
  PlaNet     Hafner et al., "Learning Latent Dynamics for Planning from Pixels", ICML 2019,
             arXiv 1811.04551 -- the Gaussian RSSM of PLAN S2b's parameter-matched variant.

These are NOT added to t1_bibliography.ENTRIES here: that list IS the paper's reference
list (paper_numbers.py t1_reference_list), and an entry the paper does not yet cite would
enter it uncited. S9, which writes §5.3 citing them, adds them there; this record is what
it verifies against. Needs the network, like t1_bibliography.py --verify, so it is not a
reproduce.sh stage.

Writes results/baseline_citations_verified.json.
"""
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402
import t1_bibliography as T1  # noqa: E402

SRC = os.path.join(R.REPO_ROOT, "docs", "presubmission", "sources")

ENTRIES = [
    {"key": "hafner2021dreamerv2", "arxiv": "2010.02193",
     "title": "Mastering Atari with Discrete World Models",
     "authors": ["Danijar Hafner", "Timothy Lillicrap", "Mohammad Norouzi", "Jimmy Ba"],
     "venue": "ICLR 2021",
     # (what we take, page, a short pattern that must appear on that page's text)
     "values": [("categorical latents: 32 discrete latent dimensions of 32 classes", 19,
                 r"Discrete latent dimensions\s*—\s*32\s*Discrete latent classes\s*—\s*32"),
                ("KL loss scale beta = 0.1", 19, r"KL loss scale\s*β\s*0\.1"),
                ("KL balancing alpha = 0.8", 19, r"KL balancing\s*α\s*0\.8"),
                ("KL balancing is used instead of free nats", 18, r"instead of using free nats"),
                ("ELU activations in every model component", 4, r"ELU activation function for all"),
                ("straight-through gradients for categorical latents", 18, r"straight-through")]},
    {"key": "hafner2019planet", "arxiv": "1811.04551",
     "title": "Learning Latent Dynamics for Planning from Pixels",
     "authors": ["Danijar Hafner", "Timothy Lillicrap", "Ian Fischer", "Ruben Villegas",
                 "David Ha", "Honglak Lee", "James Davidson"],
     "venue": "ICML 2019",
     "values": [("3 free nats, KL clipped below", 12, r"3 free nats"),
                ("KL not scaled against reconstruction", 12,
                 r"do not scale the KL divergence"),
                ("30-dimensional diagonal Gaussian latents", 12,
                 r"30-dimensional diagonal Gaussians"),
                ("fully connected layers with ReLU", 12, r"ReLU activations")]},
]


def page_texts(arxiv_id):
    pdf = os.path.join(SRC, f"{arxiv_id}.pdf")
    if not os.path.exists(pdf):
        os.makedirs(SRC, exist_ok=True)
        urllib.request.urlretrieve(f"https://arxiv.org/pdf/{arxiv_id}", pdf)
    from pypdf import PdfReader
    return [re.sub(r"\s+", " ", p.extract_text() or "") for p in PdfReader(pdf).pages]


def main():
    ids = ",".join(e["arxiv"] for e in ENTRIES)
    root = ET.fromstring(T1.fetch(f"https://export.arxiv.org/api/query?id_list={ids}&max_results=10"))
    meta = {}
    for e in root.findall("a:entry", T1.ATOM):
        aid = e.find("a:id", T1.ATOM).text.rsplit("/", 1)[-1]
        meta[aid.split("v")[0]] = {
            "title": re.sub(r"\s+", " ", e.find("a:title", T1.ATOM).text).strip(),
            "authors": [a.find("a:name", T1.ATOM).text for a in e.findall("a:author", T1.ATOM)],
            "arxiv_version": aid}
    norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
    out, ok = [], True
    for ent in ENTRIES:
        m = meta.get(ent["arxiv"], {})
        pages = page_texts(ent["arxiv"])
        vals = []
        for what, page, pat in ent["values"]:
            found = bool(re.search(pat, pages[page - 1])) if page <= len(pages) else False
            vals.append({"value": what, "page": page, "found_on_page": found})
        rec = {"key": ent["key"], "arxiv": ent["arxiv"], "venue": ent["venue"],
               "found": bool(m), "title_matches": norm(m.get("title", "")) == norm(ent["title"]),
               "authors_match": m.get("authors") == ent["authors"],
               "title_arxiv": m.get("title"), "authors_arxiv": m.get("authors"),
               "arxiv_version": m.get("arxiv_version"), "values": vals}
        rec["verified"] = (rec["found"] and rec["title_matches"] and rec["authors_match"]
                           and all(v["found_on_page"] for v in vals))
        ok &= rec["verified"]
        out.append(rec)
        print(f"  {ent['key']:<22} title {rec['title_matches']}  authors {rec['authors_match']}  "
              + "  ".join(f"p{v['page']}:{'ok' if v['found_on_page'] else 'MISSING'}" for v in vals))
    json.dump({"purpose": "sources of the RSSM baselines' settings (BASELINE_SPECS.md), verified "
                          "as scripts/t1_bibliography.py verifies the paper's references",
               "not_in_t1_entries_until": "S9 cites them in the paper (§5.3)",
               "entries": out, "all_verified": bool(ok)},
              open(os.path.join(R.RESULTS, "baseline_citations_verified.json"), "w"), indent=2)
    print(f"  all verified: {ok}\n  wrote results/baseline_citations_verified.json")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
