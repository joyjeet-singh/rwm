"""
T1 -- the bibliography for section 2, with every entry verified against the paper.

This paper had two references, both of them the papers being reproduced. TMLR has
no novelty criterion, but the absence converts into a CLAIMS problem: the framing
"neither paper runs this comparison, so we do" reads as an implicit novelty claim,
and there is direct precedent a reviewer will raise.

The rule this file enforces: no citation is invented. For each entry we record the
title, the full author list, the venue and the year as the arXiv metadata gives
them, plus -- where our text makes a claim about what the paper SAYS -- the
verbatim fragment it rests on and where it came from.

    python scripts/t1_bibliography.py               emit from the recorded record
    python scripts/t1_bibliography.py --verify      re-fetch and re-check

--verify needs the network, so it is not a reproduce.sh stage, for the same reason
scripts/verify_original_quotes.py is not. The recorded verification is what the
build reads, and --verify is how it gets refreshed.

Writes results/t1_bibliography_verified.json.
"""
import argparse
import html
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402

CHECKED_ON = "2026-08-23"
ATOM = {"a": "http://www.w3.org/2005/Atom"}

# Every field below was read from the arXiv API entry for the id, on CHECKED_ON.
# `fragments` are substrings verified present in the paper's own HTML rendering;
# they are the evidence for the "what it establishes" column and for anything our
# section 2 asserts about the work.
ENTRIES = [
    {
        "key": "lu2022",
        "arxiv": "2110.04135",
        "title": "Revisiting Design Choices in Offline Model-Based Reinforcement Learning",
        "authors": ["Cong Lu", "Philip J. Ball", "Jack Parker-Holder",
                    "Michael A. Osborne", "Stephen J. Roberts"],
        "venue": "ICLR 2022 (Spotlight)",
        "year": 2022,
        "establishes": "a calibration comparison of uncertainty heuristics in offline "
                       "MBRL, under a protocol built to capture the covariate shift "
                       "model-based RL induces, reporting rank and bivariate "
                       "correlation against true model error SEPARATELY",
        "why_we_engage":
            "This is direct precedent for 5.6's framing, four years earlier, on the "
            "same family of ensemble-disagreement penalties. It also independently "
            "supports our result rather than undercutting it: Lu et al. find the "
            "ensemble standard deviation -- the exact quantity system_dynamics.py:126 "
            "computes and envs/base.py:166 applies -- to have better correlation with "
            "model error than the MOPO and MOReL penalties. Our contribution is not "
            "the idea of checking; it is checking a RELEASED checkpoint from a "
            "pipeline deployed on hardware, and separating ranking from scale, which "
            "Lu et al. do not do because they never ask whether the penalty is a "
            "calibrated interval.",
        "fragments": [
            "We measure Spearman rank",
            "despite the similar rank correlations",
            "the bivariate correlations",
            "for the first time, capture the specific covariate shift induced by "
            "model-based RL",
            "the ensemble standard deviation is statistically strikingly similar to "
            "that used in",
        ],
    },
    {
        "key": "chua2018",
        "arxiv": "1805.12114",
        "title": "Deep Reinforcement Learning in a Handful of Trials using "
                 "Probabilistic Dynamics Models",
        "authors": ["Kurtland Chua", "Roberto Calandra", "Rowan McAllister",
                    "Sergey Levine"],
        "venue": "NeurIPS 2018",
        "year": 2018,
        "establishes": "the bounded log-variance head with a softplus squeeze between "
                       "learned min and max bounds, plus a small regulariser on those "
                       "bounds -- paired with a Gaussian negative-log-likelihood "
                       "objective",
        "why_we_engage":
            "5.3's parameterisation is inherited from this lineage LINE FOR LINE. PETS "
            "Appendix A.1 gives\n"
            "    logvar = max_logvar - softplus(max_logvar - logvar)\n"
            "    logvar = min_logvar + softplus(logvar - min_logvar)\n"
            "and mlp.py:92-93 is the same two lines in log-sigma rather than "
            "log-variance, with compute_bound_loss (system_dynamics.py:302) supplying "
            "PETS's regulariser on the bounds. What is NOT inherited is the objective: "
            "PETS uses 'the negative log prediction probability as our loss function', "
            "whose log-sigma term is exactly what opposes sigma -> 0. "
            "system_dynamics.py:283 substitutes squared error on a reparameterised "
            "sample, which has no such term. So the collapse 5.3 derives is a "
            "consequence of the SUBSTITUTION, not of the parameterisation -- and that "
            "makes 5.3 bigger than one repository, because any descendant that made "
            "the same substitution inherits the same optimum. We have not tested any "
            "other descendant and mark this as a hypothesis (11).",
        "fragments": [
            "logvar = max_logvar - tf.nn.softplus(max_logvar - logvar)",
            "logvar = min_logvar + tf.nn.softplus(logvar - min_logvar)",
            "with a small regularization penalty on term on max_logvar",
            "We use the negative log prediction probability as our loss function",
        ],
    },
    {
        "key": "yu2020",
        "arxiv": "2005.13239",
        "title": "MOPO: Model-based Offline Policy Optimization",
        "authors": ["Tianhe Yu", "Garrett Thomas", "Lantao Yu", "Stefano Ermon",
                    "James Zou", "Sergey Levine", "Chelsea Finn", "Tengyu Ma"],
        "venue": "NeurIPS 2020",
        "year": 2020,
        "establishes": "penalising the reward by an ensemble uncertainty estimate, "
                       "solving a pessimistic MDP that lower-bounds the true one",
        "why_we_engage": "the method the follow-up adapts. MOPO-PPO is named for it, "
                         "and Eq. 5's r~ = r - lambda u is MOPO's construction.",
        "fragments": [],
    },
    {
        "key": "kidambi2020",
        "arxiv": "2005.05951",
        "title": "MOReL : Model-Based Offline Reinforcement Learning",
        "authors": ["Rahul Kidambi", "Aravind Rajeswaran", "Praneeth Netrapalli",
                    "Thorsten Joachims"],
        "venue": "NeurIPS 2020",
        "year": 2020,
        "establishes": "an unknown-state-action detector built from pairwise ensemble "
                       "disagreement, used to construct a pessimistic MDP",
        "why_we_engage": "the alternative heuristic in the same family. Lu et al. find "
                         "the ensemble standard deviation 'strikingly similar' to "
                         "MOReL's quantity but better behaved, which is the quantity "
                         "the follow-up applies.",
        "fragments": [],
    },
    {
        "key": "lakshminarayanan2017",
        "arxiv": "1612.01474",
        "title": "Simple and Scalable Predictive Uncertainty Estimation using Deep "
                 "Ensembles",
        "authors": ["Balaji Lakshminarayanan", "Alexander Pritzel", "Charles Blundell"],
        "venue": "NeurIPS 2017",
        "year": 2017,
        "establishes": "deep ensembles: several networks trained from DIFFERENT random "
                       "initialisations and different data orderings, whose spread is "
                       "the uncertainty estimate",
        "why_we_engage":
            "This is what 'ensemble' is supposed to mean, and it is the contrast X-12 "
            "and M-44 rest on. The released checkpoint's five members share one GRU "
            "trunk and one recurrent hidden state and differ only in a 77,492-parameter "
            "output head -- 89.15% of each member is numerically identical to every "
            "other. That is not a deep ensemble in this sense, and 5.4 says so.",
        "fragments": [],
    },
    {
        "key": "kuleshov2018",
        "arxiv": "1807.00263",
        "title": "Accurate Uncertainties for Deep Learning Using Calibrated Regression",
        "authors": ["Volodymyr Kuleshov", "Nathan Fenner", "Stefano Ermon"],
        "venue": "ICML 2018",
        "year": 2018,
        "establishes": "recalibration of regression uncertainties by fitting a "
                       "post-hoc map on held-out data",
        "why_we_engage": "5.7's per-horizon multiplier is a coarse instance of this: "
                         "one scalar per forecast horizon, fitted on one held-out "
                         "episode and scored on the other. We say so rather than "
                         "presenting it as new.",
        "fragments": [],
    },
    {
        "key": "guo2017",
        "arxiv": "1706.04599",
        "title": "On Calibration of Modern Neural Networks",
        "authors": ["Chuan Guo", "Geoff Pleiss", "Yu Sun", "Kilian Q. Weinberger"],
        "venue": "ICML 2017",
        "year": 2017,
        "establishes": "that modern networks are systematically miscalibrated, and "
                       "that a single temperature parameter often repairs it",
        "why_we_engage": "background, and the closest precedent for the shape of 5.7's "
                         "result: a one-parameter post-hoc fix for a miscalibration "
                         "that is not a modelling failure.",
        "fragments": [],
    },
    {
        "key": "ovadia2019",
        "arxiv": "1906.02530",
        "title": "Can You Trust Your Model's Uncertainty? Evaluating Predictive "
                 "Uncertainty Under Dataset Shift",
        "authors": ["Yaniv Ovadia", "Emily Fertig", "Jie Ren", "Zachary Nado",
                    "D Sculley", "Sebastian Nowozin", "Joshua V. Dillon",
                    "Balaji Lakshminarayanan", "Jasper Snoek"],
        "venue": "NeurIPS 2019",
        "year": 2019,
        "establishes": "that calibration degrades under covariate shift, and that the "
                       "degradation is worse the further from the training "
                       "distribution the input lies",
        "why_we_engage": "why horizon-dependent failure is the expected shape rather "
                         "than a surprise. An autoregressive rollout generates its own "
                         "covariate shift, increasing with depth -- which is what 5.8's "
                         "flat sigma against growing error looks like from here.",
        "fragments": [],
    },
    {
        "key": "abbas2020",
        "arxiv": "2007.02418",
        "title": "Selective Dyna-style Planning Under Limited Model Capacity",
        "authors": ["Zaheer Abbas", "Samuel Sokota", "Erin J. Talvitie", "Martha White"],
        "venue": "ICML 2020",
        "year": 2020,
        "establishes": "that predictive uncertainty in MBRL has three sources -- "
                       "aleatoric, parameter, and MODEL INADEQUACY -- and that prior "
                       "selective-planning work attends only to the second",
        "why_we_engage":
            "prior comparison of what the penalty quantity is actually measuring. It "
            "also names the distinction our 5.1 turns on: the released checkpoint emits "
            "an aleatoric term and a parameter-uncertainty term, discards the first, "
            "and has no estimate of model inadequacy at all -- which is the source that "
            "grows with rollout depth.",
        "fragments": [],
    },
    {
        "key": "janner2019",
        "arxiv": "1906.08253",
        "title": "When to Trust Your Model: Model-Based Policy Optimization",
        "authors": ["Michael Janner", "Justin Fu", "Marvin Zhang", "Sergey Levine"],
        "venue": "NeurIPS 2019",
        "year": 2019,
        "establishes": "MBPO: short model rollouts branched from real states, with the "
                       "rollout length traded against model error",
        "why_we_engage": "the loop MOPO-PPO adapts, and the origin of the "
                         "rollout-length-versus-model-error trade the follow-up's "
                         "100-step imagination horizon sits inside (X-13).",
        "fragments": [],
    },
]


def flatten(raw):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw)))


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "rwm-repro/1.0"})
    with urllib.request.urlopen(req, timeout=60) as f:
        return f.read().decode("utf-8", "replace")


def verify():
    """Re-fetch metadata and re-check every recorded fragment. Returns the record."""
    ids = ",".join(e["arxiv"] for e in ENTRIES)
    root = ET.fromstring(fetch(
        f"https://export.arxiv.org/api/query?id_list={ids}&max_results=40"))
    meta = {}
    for e in root.findall("a:entry", ATOM):
        aid = e.find("a:id", ATOM).text.rsplit("/", 1)[-1]
        base = aid.split("v")[0]
        meta[base] = {
            "title": re.sub(r"\s+", " ", e.find("a:title", ATOM).text).strip(),
            "authors": [a.find("a:name", ATOM).text for a in e.findall("a:author", ATOM)],
            "published": e.find("a:published", ATOM).text[:10],
            "comment": (re.sub(r"\s+", " ", c.text)
                        if (c := e.find("{http://arxiv.org/schemas/atom}comment"))
                        is not None else None),
            "arxiv_version": aid,
        }

    per = []
    for ent in ENTRIES:
        m = meta.get(ent["arxiv"])
        rec = {"key": ent["key"], "arxiv": ent["arxiv"], "found": m is not None}
        if m:
            # Titles: arXiv occasionally differs in spacing/punctuation from a
            # published title, so compare on alphanumerics only and record both.
            norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
            rec["title_matches"] = norm(m["title"]) == norm(ent["title"])
            rec["title_arxiv"] = m["title"]
            rec["authors_match"] = m["authors"] == ent["authors"]
            rec["authors_arxiv"] = m["authors"]
            rec["published"] = m["published"]
            rec["comment"] = m["comment"]
            rec["arxiv_version"] = m["arxiv_version"]
        if ent["fragments"]:
            body = flatten(fetch(f"https://arxiv.org/html/{m['arxiv_version']}"))
            rec["fragments"] = [{"fragment": f[:70],
                                 "found": re.sub(r"\s+", " ", f) in body}
                                for f in ent["fragments"]]
            rec["n_fragments_found"] = sum(1 for f in rec["fragments"] if f["found"])
            rec["n_fragments"] = len(rec["fragments"])
        per.append(rec)
    return per


# The result of running --verify on CHECKED_ON. Kept in the file so the build is
# network-free and the record is reviewable in a diff.
RECORDED = {
    "checked_on": CHECKED_ON,
    "method": "arXiv API metadata for title, author list and venue comment; for any "
              "entry whose 'why_we_engage' asserts what the paper SAYS, the asserted "
              "fragments were additionally matched as substrings of that paper's own "
              "arXiv HTML rendering after tag-stripping and whitespace collapse",
    "n_entries": len(ENTRIES),
    "n_metadata_verified": 10,
    "n_with_fragment_checks": 2,
    "n_fragments_checked": 9,
    "n_fragments_verbatim": 9,
    "per_entry": [
        {"key": "lu2022", "title_matches": True, "authors_match": True,
         "published": "2021-10-08", "arxiv_version": "2110.04135v2",
         "comment": "Spotlight @ ICLR 2022; Spotlight @ RL4RealLife Workshop ICML2021",
         "n_fragments": 5, "n_fragments_found": 5},
        {"key": "chua2018", "title_matches": True, "authors_match": True,
         "published": "2018-05-30", "arxiv_version": "1805.12114v2",
         "comment": "NIPS 2018, video and code available",
         "n_fragments": 4, "n_fragments_found": 4},
        {"key": "yu2020", "title_matches": True, "authors_match": True,
         "published": "2020-05-27", "arxiv_version": "2005.13239v6",
         "comment": "NeurIPS 2020. First two authors contributed equally."},
        {"key": "kidambi2020", "title_matches": True, "authors_match": True,
         "published": "2020-05-12", "arxiv_version": "2005.05951v3",
         "comment": "Published at NeurIPS 2020."},
        {"key": "lakshminarayanan2017", "title_matches": True, "authors_match": True,
         "published": "2016-12-05", "arxiv_version": "1612.01474v3", "comment": "NIPS 2017",
         "note": "arXiv preprint dated 2016; the venue year is 2017 and the entry "
                 "cites the venue year, as the brief's table does"},
        {"key": "kuleshov2018", "title_matches": True, "authors_match": True,
         "published": "2018-07-01", "arxiv_version": "1807.00263v1", "comment": "ICML 2018"},
        {"key": "guo2017", "title_matches": True, "authors_match": True,
         "published": "2017-06-14", "arxiv_version": "1706.04599v2", "comment": "ICML 2017"},
        {"key": "ovadia2019", "title_matches": True, "authors_match": True,
         "published": "2019-06-06", "arxiv_version": "1906.02530v2",
         "comment": "Advances in Neural Information Processing Systems, 2019"},
        {"key": "abbas2020", "title_matches": True, "authors_match": True,
         "published": "2020-07-05", "arxiv_version": "2007.02418v3",
         "comment": "Accepted at ICML 2020"},
        {"key": "janner2019", "title_matches": True, "authors_match": True,
         "published": "2019-06-19", "arxiv_version": "1906.08253v3",
         "comment": "NeurIPS 2019."},
    ],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true",
                    help="re-fetch from arXiv and re-check every entry (needs network)")
    args = ap.parse_args()

    record = RECORDED
    if args.verify:
        per = verify()
        bad = [p for p in per if not p.get("title_matches") or not p.get("authors_match")]
        frag_bad = [(p["key"], f["fragment"]) for p in per
                    for f in p.get("fragments", []) if not f["found"]]
        record = {"checked_on": "RE-VERIFIED THIS RUN", "method": RECORDED["method"],
                  "n_entries": len(ENTRIES), "per_entry": per,
                  "n_metadata_verified": sum(1 for p in per if p.get("title_matches")
                                             and p.get("authors_match")),
                  "n_fragments_checked": sum(p.get("n_fragments", 0) for p in per),
                  "n_fragments_verbatim": sum(p.get("n_fragments_found", 0) for p in per)}
        assert not bad, f"metadata mismatch: {[b['key'] for b in bad]}"
        assert not frag_bad, f"fragments not found verbatim: {frag_bad}"

    out = {
        "purpose": "every section 2 reference, verified against the paper itself",
        "rule": "no entry is added that was not verified. Title, full author list and "
                "venue come from the arXiv API; anything our text asserts the paper "
                "SAYS is additionally matched verbatim against its HTML.",
        "evidence_class": "EXT",
        "entries": ENTRIES,
        "verification": record,
        "n_entries": len(ENTRIES),
        "n_references_before": 2,
        "n_references_after": 2 + len(ENTRIES),
        "untested_hypothesis": {
            "statement": "the sigma = 0 optimum affects any descendant of the PETS "
                         "parameterisation that replaced the Gaussian NLL with squared "
                         "error on a reparameterised sample",
            "grounds": "the parameterisation is inherited line for line (chua2018 "
                       "fragments); the objective is not (system_dynamics.py:283)",
            "status": "NOT TESTED outside this repository. Flagged in 2 and 11 as a "
                      "hypothesis and deliberately out of scope.",
        },
    }
    dst = os.path.join(R.RESULTS, "t1_bibliography_verified.json")
    with open(dst, "w") as f:
        json.dump(out, f, indent=2, sort_keys=True)

    print("T1 — BIBLIOGRAPHY VERIFICATION")
    print("=" * 100)
    for e in ENTRIES:
        v = next((p for p in record["per_entry"] if p["key"] == e["key"]), {})
        mark = "ok" if v.get("title_matches") and v.get("authors_match") else "!!"
        frag = (f"   fragments {v['n_fragments_found']}/{v['n_fragments']}"
                if "n_fragments" in v else "")
        print(f"  [{mark}] {e['key']:<22} {e['venue']:<22} arXiv:{e['arxiv']}{frag}")
    print(f"\n  {record['n_metadata_verified']} of {len(ENTRIES)} entries "
          f"metadata-verified; {record.get('n_fragments_verbatim', 0)} of "
          f"{record.get('n_fragments_checked', 0)} asserted fragments verbatim")
    print(f"  references: {out['n_references_before']} -> {out['n_references_after']}")
    print(f"\n  wrote {R.rel(dst)}")


if __name__ == "__main__":
    main()
