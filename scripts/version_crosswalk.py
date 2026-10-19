"""G1 — crosswalk from the v1 text we read to the current versions of both originals.

For every claim Appendix D lists, and every passage the paper quotes from either original (plus the
four statements round 5's review raised: the follow-up's variance, ensemble and propagation claims),
this records the v1 fragment and where it sits, whether the same fragment is in every later version
and where, the current version's wording where it differs, and a `changed` label:

    no        the same fragment, in a section with the same title, main text or appendix alike
    moved     the same fragment, under a different section title, between main text and appendix, or
              (for a table row) in a differently numbered table
    reworded  v1's fragment is gone and the current version says something else about the same thing
    new       absent from v1, present later
    removed   in v1, in no later version

Every fragment is asserted present in the local text of the version it is attributed to. A failed
assertion exits 1 and writes nothing.

Not wired into reproduce.sh: it needs the downloaded originals, which are gitignored
(`docs/presubmission/sources/g1/`), and `--fetch` needs the network. Like
`scripts/verify_original_quotes.py`, it is run when a quotation or a version changes, and the
artifact it writes (`results/version_crosswalk.json`) is what is committed.

    python scripts/version_crosswalk.py --date 2026-10-19 --fetch   # download, then check
    python scripts/version_crosswalk.py --date 2026-10-19           # check what is on disk

Two texts are searched for each version: the arXiv HTML rendering (which gives section titles) and
the PDF text extracted with pypdf (which gives page numbers and is the only reliable text for the
training-parameter tables, where the HTML repeats every symbol). Both are compared with all
whitespace removed and with dashes, quotes and minus signs unified, because the PDF text breaks
lines inside words. Fragments are kept short (at most 30 words); the originals are under arXiv's
non-exclusive licence.

The two OpenReview workshop versions (forum ids u76d3gBWCX and mcwLgO93ym) could not be fetched:
OpenReview answers an automated client with a browser challenge. The artifact records that, and
that no workshop text was compared; it does not guess.
"""
import argparse
import hashlib
import html
import json
import os
import re
import sys
import urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
sys.path.insert(0, os.path.join(ROOT, "src"))
import rwm_data as R  # noqa: E402

SRC = os.path.join(ROOT, "docs", "presubmission", "sources", "g1")
OUT = os.path.join(R.RESULTS, "version_crosswalk.json")

FAMILIES = {
    "RWM": {"arxiv": "2501.10100", "versions": ["v1", "v2", "v3", "v4", "v5"], "current": "v5",
            "dates": {"v1": "2025-01-17", "v2": "2025-04-23", "v3": "2025-04-24",
                      "v4": "2025-11-24", "v5": "2025-12-14"}},
    "RWMU": {"arxiv": "2504.16680", "versions": ["v1", "v2", "v3"], "current": "v3",
             "dates": {"v1": "2025-04-23", "v2": "2026-01-07", "v3": "2026-01-08"}},
}
WORKSHOPS = [
    {"forum_id": "u76d3gBWCX", "url": "https://openreview.net/forum?id=u76d3gBWCX"},
    {"forum_id": "mcwLgO93ym", "url": "https://openreview.net/forum?id=mcwLgO93ym"},
]

# ---- the claims -------------------------------------------------------------------------------
# fam: RWM = arXiv 2501.10100, RWMU = arXiv 2504.16680.  v1: fragment in v1 (None if v1 lacks it).
# cur: fragment in the current version where it differs from v1's.  row: Appendix D row, if any.
# paper: where the current paper relies on it.  test: what a test of it must now say, for a claim
# that changed and that the paper tests.
C = []


def claim(cid, fam, what, v1, cur=None, row=None, paper="", tested=False, test=None):
    C.append(dict(id=cid, fam=fam, claim=what, v1=v1, cur=cur, appendix_d_row=row, paper=paper,
                  tested=tested, test=test))


claim("rwm_ar_beats_tf", "RWM", "RWM-AR outperforms RWM-TF",
      "RWM-AR significantly outperforms its teacher-forcing counterpart",
      row="RWM-AR consistently outperforms RWM-TF", paper="Appendix D; §5", tested=True)
claim("rwm_tf_poor", "RWM", "teacher forcing (N=1) gives poor autoregressive performance",
      "this setting leads to poor autoregressive performance",
      row="Teacher forcing gives \"poor autoregressive performance\"", paper="Appendix D; §5.2", tested=True)
claim("rwm_mn_optimal", "RWM", "M=32, N=8 is the optimal accuracy/training-time trade-off",
      "an optimal trade-off emerges",
      row="M=32, N=8 gives the optimal trade-off", paper="Appendix D; §5.2", tested=True)
claim("rwm_arch_baselines", "RWM", "RWM beats MLP, RSSM and transformer baselines",
      "consistently achieves the lowest prediction errors across all environments",
      row="Beats MLP, RSSM and transformer baselines", paper="Appendix D; §5.3", tested=True)
claim("rwm_generality", "RWM", "generality across robot morphologies",
      "RWM-AR demonstrates superior generalization and robustness across tasks, from manipulation to locomotion",
      row="Generality across quadruped, humanoid, manipulation", paper="Appendix D", tested=False)
claim("rwm_zero_shot", "RWM", "zero-shot hardware transfer",
      "we deploy it on ANYmal D hardware in a zero-shot transfer setup",
      cur="we deploy them on ANYmal D and Unitree G1 hardware in a zero-shot transfer setup",
      row="Zero-shot hardware transfer", paper="Appendix D", tested=False)
claim("rwm_vs_shac_dreamer", "RWM", "MBPO-PPO beats SHAC and Dreamer",
      "SHAC and Dreamer fail to produce a deployable policy due to its collapse during training",
      row="MBPO-PPO beats SHAC and Dreamer", paper="Appendix D", tested=False)
claim("rwm_sample_efficiency", "RWM", "~6M transitions against ~250M for model-free PPO (Table 1)",
      None, cur="state transitions 6M",
      row="Policies transfer to hardware from ~6M state transitions against ~250M",
      paper="Appendix D row 6; §9 (the headline sample-efficiency result)", tested=False,
      test="Cite v2 or later, not v1: v1 has no such table. results/original_paper_figures.json "
           "gives its location as 2501.10100v1 Table I (Limitations).")
claim("rwm_decay_factor", "RWM", "the loss has a decay factor alpha on each forecast step",
      "denotes a decay factor", paper="Appendix H (C-09)", tested=False)
claim("rwm_table_decay", "RWM", "the training table sets the forecast decay to 1.0 (equal weights)",
      "forecast decay α 1.0", paper="Appendix H (C-09)", tested=False)
claim("rwm_table_iterations", "RWM", "the training table sets 2,500 iterations",
      "max iterations - 2500", paper="Appendix H (C-13); §5.2", tested=False)

claim("rwmu_title_name", "RWMU", "title and method name",
      "Offline Robotic World Model: Learning Robotic Policies without a Physics Simulator",
      cur="Uncertainty-Aware Robotic World Model Makes Offline Model-Based Reinforcement Learning Work on Real Robots",
      paper="References, item 2", tested=False)
claim("rwmu_epistemic_follows", "RWMU", "epistemic uncertainty closely follows the prediction error",
      "closely follows the trend of the prediction error",
      row="Epistemic \"closely follows the trend of the prediction error\"", paper="Appendix D; §6.6", tested=True)
claim("rwmu_trust_metric", "RWMU", "the correlation justifies epistemic uncertainty as a trust metric",
      "justifies its role as a trust metric for policy optimization",
      row="Epistemic ... \"its role as a trust metric\"", paper="Appendix D; §6.6", tested=True)
claim("rwmu_epistemic_aligns", "RWMU", "the follow-up's own summary of the same figure",
      None, cur="aligns with the long-horizon prediction error",
      paper="not quoted by the paper", tested=False,
      test="Added in v2 beside the same figure; the v1 claim above is unchanged. A test of the trust-metric claim need not change.")
claim("rwmu_aleatoric_low", "RWMU", "the aleatoric uncertainty remains low",
      "remains low, reflecting small stochasticity in the environment",
      row="Aleatoric \"remains low, reflecting small stochasticity\"", paper="Appendix D; §6.3", tested=True)
claim("rwmu_variance_effective", "RWMU", "the learned variance captures aleatoric uncertainty effectively",
      "The learned variance component captures aleatoric uncertainty effectively",
      paper="§6.1 says the follow-up only observes that the aleatoric term stays low", tested=True)
claim("rwmu_shared_trunk", "RWMU", "bootstrap ensembles on the prediction head, after a shared recurrent feature extractor",
      "apply bootstrap ensembles to the observation prediction head of the model after a shared recurrent feature extractor",
      paper="§6.4; Appendix R", tested=True)
claim("rwmu_mean_fed_forward", "RWMU", "inference uses the ensemble mean as the next observation; epistemic = variance across members",
      "the ensemble mean is used as the predicted next observation",
      paper="§6.4 (the rollout feeds the mean through one hidden state)", tested=True)
claim("rwmu_propagated", "RWMU", "uncertainty is effectively propagated over long horizons",
      None, cur="uncertainty effectively propagated over long horizons",
      paper="not yet in the paper", tested=True,
      test="v1 does not say this; v2 added it to the abstract and §4.1 with no change to Eq. 4 or the rollout. "
           "A test must score the propagated spread against accumulated error, not only one-step spread.")
claim("rwmu_penalty_improves", "RWMU", "penalising rewards by disagreement prevents policy exploitation",
      "By penalizing high-uncertainty transitions, MOPO-PPO prevents policy exploitation",
      row="Penalising rewards by ensemble disagreement improves the learned policy", paper="Appendix D", tested=False)
claim("rwmu_real_robots", "RWMU", "policy learning purely from offline data (real robots)",
      "enabling policy learning purely from offline data",
      cur="training policies entirely from offline datasets",
      row="Offline MBRL on real robots", paper="Appendix D", tested=False)
claim("rwmu_table_decay", "RWMU", "the training table sets the forecast decay to 1.0",
      "forecast decay α 1.0", paper="Appendix H (C-09)", tested=False)
claim("rwmu_table_iterations", "RWMU", "the training table sets 2,500 iterations and learning rate 1e-4",
      "max iterations - 2500", paper="Figure 4's learning-rate comparison; §5.2", tested=False)
claim("rwmu_table_lr", "RWMU", "the training table's learning rate",
      "learning rate - 1e-4", paper="Figure 4's learning-rate comparison", tested=False)


# ---- text loading -----------------------------------------------------------------------------
def squash(s):
    s = html.unescape(s)
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'),
                 ("–", "-"), ("−", "-"), ("—", "-"), ("∆", "Δ")):
        s = s.replace(a, b)
    return re.sub(r"\s+", "", s).lower()


def html_text(raw):
    """Flatten an arXiv HTML page, keeping its section titles as markers."""
    def mark(m):
        t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(2))).strip()
        return " ⟦H:%s⟧ " % html.unescape(t)
    raw = re.sub(r"<h([1-6])[^>]*class=\"[^\"]*ltx_title[^\"]*\"[^>]*>(.*?)</h\1>", mark, raw, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw)))


def pdf_text(path):
    from pypdf import PdfReader
    pages = [(p.extract_text() or "") for p in PdfReader(path).pages]
    return pages


def in_appendix(h):
    return bool(re.match(r"^(A\.\d|A-[A-Z]|Appendix)", h.strip()))


def title_core(h):
    """A section title with its numbering removed, for comparing across renumbered versions."""
    h = re.sub(r"^(Appendix\s+)?[A-Z0-9]{1,4}(\.[0-9]+)*\s+(?=[A-Za-z])", "", h.strip())
    h = re.sub(r"^[IVX]+(-[A-Z])?\s+", "", h)
    h = re.sub(r"[^a-z]", "", h.lower())
    # the follow-up's model was renamed between versions; a heading that only carries the name is not moved
    return h.replace("uncertaintyawareroboticworldmodel", "").replace("offlineroboticworldmodel", "")


class Doc:
    def __init__(self, fam, ver):
        self.name = "%s%s" % (FAMILIES[fam]["arxiv"], ver)
        self.ver = ver
        self.html = html_text(open(os.path.join(SRC, self.name + ".html"), encoding="utf8", errors="replace").read())
        self.pages = pdf_text(os.path.join(SRC, self.name + ".pdf"))
        self.hq = squash(self.html)
        self.pq = [squash(p) for p in self.pages]
        # squash() drops spaces, so heading markers are located on a parallel, squashed stream
        self.markers = []
        self.hq_nomark = ""
        for part in re.split(r"(⟦H:[^⟧]*⟧)", self.html):
            if part.startswith("⟦H:"):
                self.markers.append((len(self.hq_nomark), part[3:-1]))
            else:
                self.hq_nomark += squash(part)

    def find(self, frag):
        """-> dict(found, section, page) for the fragment, or found=False."""
        q = squash(frag)
        out = {"found": False, "section": None, "page": None, "table": None}
        i = self.hq_nomark.find(q)
        if i >= 0:
            out["found"] = True
            sec = None
            for pos, h in self.markers:
                if pos <= i:
                    sec = h
            out["section"] = sec
        for n, p in enumerate(self.pq, 1):
            if q in p:
                out["found"] = True
                out["page"] = n
                j = p.find(q)
                t = re.findall(r"table(s?\d+)", p[:j])
                out["table"] = ("Table " + t[-1].upper()) if t else None
                break
        return out


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


URLS = {"pdf": "https://arxiv.org/pdf/%s%s", "html": "https://arxiv.org/html/%s%s",
        "_abs.html": "https://arxiv.org/abs/%s%s"}


def fetch():
    os.makedirs(SRC, exist_ok=True)
    for fam in FAMILIES.values():
        for v in fam["versions"]:
            for ext, url in URLS.items():
                p = os.path.join(SRC, "%s%s%s" % (fam["arxiv"], v, "." + ext if ext in ("pdf", "html") else ext))
                req = urllib.request.Request(url % (fam["arxiv"], v), headers={"User-Agent": "reproduction-study"})
                open(p, "wb").write(urllib.request.urlopen(req, timeout=180).read())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True, help="date of this check, YYYY-MM-DD")
    ap.add_argument("--fetch", action="store_true", help="download the originals first (needs the network)")
    args = ap.parse_args()
    if args.fetch:
        fetch()

    docs = {(f, v): Doc(f, v) for f, d in FAMILIES.items() for v in d["versions"]}
    failures, rows = [], []
    for c in C:
        fam = FAMILIES[c["fam"]]
        vs = fam["versions"]
        f1 = c["v1"]
        fc = c["cur"] or c["v1"]
        r1 = {v: docs[(c["fam"], v)].find(f1) if f1 else None for v in vs}
        rc = {v: docs[(c["fam"], v)].find(fc) for v in vs}
        # assertions: the v1 fragment is in v1, and the current fragment is in the current version
        if f1 and not r1["v1"]["found"]:
            failures.append("%s: v1 fragment not in v1: %r" % (c["id"], f1))
        if not rc[fam["current"]]["found"]:
            failures.append("%s: current fragment not in %s: %r" % (c["id"], fam["current"], fc))
        if f1 is None and rc["v1"]["found"]:
            failures.append("%s: declared absent from v1 but found there: %r" % (c["id"], fc))
        for fr in filter(None, (f1, fc)):
            if len(fr.split()) > 30:
                failures.append("%s: fragment over 30 words" % c["id"])

        if "_table_" not in c["id"] and c["id"] != "rwm_sample_efficiency":
            # a table label is meaningful only for a claim that is a table row
            for rr in (r1, rc):
                for x in rr.values():
                    if x:
                        x["table"] = None
        cur = fam["current"]
        s1 = (r1["v1"] or {}).get("section") if f1 else None
        sc = rc[cur]["section"]
        if f1 is None:
            changed = "new"
        elif c["cur"] is None:
            if not rc[cur]["found"]:
                changed = "removed"
            elif (s1 and sc and (title_core(s1) != title_core(sc) or in_appendix(s1) != in_appendix(sc))) or \
                    (r1["v1"]["table"] != rc[cur]["table"]):
                changed = "moved"
            else:
                changed = "no"
        else:
            # the same thing is said differently; "removed" only if nothing at all is said later
            changed = "reworded" if rc[cur]["found"] else "removed"
        rows.append({
            "id": c["id"], "family": c["fam"], "arxiv": fam["arxiv"], "claim": c["claim"],
            "appendix_d_row": c["appendix_d_row"], "paper_relies_on_it_in": c["paper"],
            "tested_by_the_paper": c["tested"],
            "v1": None if f1 is None else {"fragment": f1, "section": s1, "page": r1["v1"]["page"],
                                              "table": r1["v1"]["table"]},
            "current": {"version": cur, "fragment": fc, "section": sc, "page": rc[cur]["page"],
                        "table": rc[cur]["table"]},
            "v1_fragment_present_in": [v for v in vs if r1[v] and r1[v]["found"]] if f1 else [],
            "current_fragment_present_in": [v for v in vs if rc[v]["found"]],
            "first_version_with_current_fragment": next((v for v in vs if rc[v]["found"]), None),
            "workshop_version": "not compared: OpenReview text not reachable",
            "changed": changed,
            "what_a_test_must_now_say": c["test"] if changed in ("new", "moved", "reworded", "removed") else None,
        })

    if failures:
        print("ASSERTION FAILURES — nothing written")
        for f in failures:
            print("  " + f)
        return 1

    srcs = {}
    for fam in FAMILIES.values():
        for v in fam["versions"]:
            for ext in (".pdf", ".html", "_abs.html"):
                n = "%s%s%s" % (fam["arxiv"], v, ext)
                p = os.path.join(SRC, n)
                if os.path.exists(p):
                    srcs[n] = {"sha256": sha(p), "bytes": os.path.getsize(p)}
    counts = {k: sum(r["changed"] == k for r in rows) for k in ("no", "moved", "reworded", "new", "removed")}
    out = {
        "checked_on": args.date,
        "method": ("each fragment is asserted present, whitespace-removed and case-folded, in the arXiv HTML "
                   "rendering or the pypdf text of the version it is attributed to; section titles come from "
                   "the HTML, pages from the PDF"),
        "families": FAMILIES,
        "workshop_versions": [dict(w, status="not reachable",
                                   reason="OpenReview answered the automated request with a browser challenge "
                                          "(HTTP 403, ChallengeRequiredError); it was not bypassed; no text compared")
                              for w in WORKSHOPS],
        "sources": srcs,
        "n_claims": len(rows),
        "counts_by_label": counts,
        "claims": rows,
    }
    json.dump(out, open(OUT, "w"), indent=2, ensure_ascii=False)
    print("version crosswalk: %d claims, %s -> %s" % (len(rows), counts, R.rel(OUT)))
    for r in rows:
        print("  %-9s %-26s %s" % (r["changed"], r["id"], (r["current"]["section"] or "")[:50]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
