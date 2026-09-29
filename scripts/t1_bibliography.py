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
import hashlib
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
CHECKED_ON_REV3 = "2026-08-29"   # the six entries added in the revision-3 pass
CHECKED_ON_S9 = "2026-09-29"     # the two entries added in pre-submission S9 (5.3's RSSM)
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
    # ------------------------------------------------------------------
    # Added in the revision-3 pass. The first is the closest published work to
    # this paper's only CONSTRUCTIVE contribution and was missing; the next four
    # are the literature §6.4's mechanism belongs to, without which that section
    # reads as a new finding when the effect is known; the last is the natural
    # neighbour of §6.3.
    #
    # Every field below was read from the arXiv API entry for the id on
    # CHECKED_ON_REV3, and every fragment is verbatim from the abstract the API
    # returned. Where a venue is asserted it comes from the entry's own
    # journal_ref or comment field, not from recollection.
    # ------------------------------------------------------------------
    {
        "key": "malik2019",
        "arxiv": "1906.08312",
        "title": "Calibrated Model-Based Deep Reinforcement Learning",
        "authors": ["Ali Malik", "Volodymyr Kuleshov", "Jiaming Song", "Danny Nemer",
                    "Harlan Seymour", "Stefano Ermon"],
        "venue": "ICML 2019 (PMLR 97:4314-4323)",
        "year": 2019,
        "establishes": "that model-based RL needs uncertainties that are CALIBRATED "
                       "rather than merely ranked, and recalibrates a dynamics "
                       "model's uncertainty to obtain them",
        "why_we_engage":
            "This is the closest published work to 6.8, which is this paper's only "
            "constructive contribution, and citing Kuleshov 2018 without it left "
            "that section looking less positioned than it is. 6.8 says what is new "
            "relative to it: the conditioning variable is the FORECAST HORIZON, and "
            "a single global multiplier fails where a per-horizon one works. The "
            "distinction matters because open-loop rollout error accumulates with "
            "depth and a horizon-blind recalibration cannot follow it.",
        "fragments": [
            "good uncertainties must be calibrated",
        ],
    },
    {
        "key": "lee2015",
        "arxiv": "1511.06314",
        "title": "Why M Heads are Better than One: Training a Diverse Ensemble of "
                 "Deep Networks",
        "authors": ["Stefan Lee", "Senthil Purushwalkam", "Michael Cogswell",
                    "David Crandall", "Dhruv Batra"],
        "venue": "arXiv:1511.06314",
        "year": 2015,
        "establishes": "that multi-head architectures sharing a trunk are a distinct "
                       "and weaker form of ensembling than independently trained "
                       "networks, and that diversity has to be engineered rather "
                       "than assumed",
        "why_we_engage":
            "6.4 observes that five heads on one trunk cannot disagree about what "
            "the trunk does not already carry. That is not new, and saying so is "
            "the difference between a finding and a rediscovery. What IS new is "
            "finding it in a released robotics checkpoint whose authors deployed it "
            "on hardware, with the sharing quantified and the cost measured.",
        "fragments": [
            "ensembling as a first-class problem",
            "diverse",
        ],
    },
    {
        "key": "fort2019",
        "arxiv": "1912.02757",
        "title": "Deep Ensembles: A Loss Landscape Perspective",
        "authors": ["Stanislav Fort", "Huiyi Hu", "Balaji Lakshminarayanan"],
        "venue": "arXiv:1912.02757",
        "year": 2019,
        "establishes": "that the diversity of a deep ensemble comes from independent "
                       "random initialisation exploring different modes, and that "
                       "subspace methods do not match it",
        "why_we_engage":
            "It supplies the mechanism behind 6.4 and behind M-44's contrast: what "
            "independent initialisation buys is decorrelation that a shared trunk "
            "cannot produce. It is also the reason M-49 exists -- if independence "
            "is what matters, the contrast must hold capacity fixed to show it.",
        "fragments": [
            "random initialization",
            "diversity",
        ],
    },
    {
        "key": "havasi2021",
        "arxiv": "2010.06610",
        "title": "Training independent subnetworks for robust prediction",
        "authors": ["Marton Havasi", "Rodolphe Jenatton", "Stanislav Fort",
                    "Jeremiah Zhe Liu", "Jasper Snoek", "Balaji Lakshminarayanan",
                    "Andrew M. Dai", "Dustin Tran"],
        "venue": "ICLR 2021",
        "year": 2021,
        "establishes": "that ensemble-like uncertainty can be obtained inside one "
                       "network's forward pass (MIMO), and what that costs",
        "why_we_engage":
            "One of the two standard answers to the trunk-sharing problem 6.4 "
            "describes. A reader of 6.4 asks what to do instead; this and "
            "BatchEnsemble are the cheap answers, and 6.10's independent ensemble "
            "is the expensive one.",
        "fragments": [
            "single model",
        ],
    },
    {
        "key": "wen2020",
        "arxiv": "2002.06715",
        "title": "BatchEnsemble: An Alternative Approach to Efficient Ensemble and "
                 "Lifelong Learning",
        "authors": ["Yeming Wen", "Dustin Tran", "Jimmy Ba"],
        "venue": "ICLR 2020",
        "year": 2020,
        "establishes": "an ensemble whose members share a weight matrix and differ "
                       "by a rank-one factor each, trading diversity for cost "
                       "explicitly rather than incidentally",
        "why_we_engage":
            "The contrast that makes 6.4's point precise. BatchEnsemble shares "
            "deliberately and says what it gives up; the released checkpoint shares "
            "{{v1_shared_pct}}% of each member and reports the resulting spread as "
            "an uncertainty. The problem is not sharing, it is sharing and then "
            "reading the spread as if the members were independent.",
        "fragments": [
            "a shared weight among all ensemble members and a rank-one matrix per member",
        ],
    },
    {
        "key": "seitzer2022",
        "arxiv": "2203.09168",
        "title": "On the Pitfalls of Heteroscedastic Uncertainty Estimation with "
                 "Probabilistic Neural Networks",
        "authors": ["Maximilian Seitzer", "Arash Tavakoli", "Dimitrije Antic",
                    "Georg Martius"],
        "venue": "ICLR 2022",
        "year": 2022,
        "establishes": "that training a heteroscedastic Gaussian head by maximising "
                       "log-likelihood with gradient-based optimisers has failure "
                       "modes, demonstrated on a synthetic example",
        "why_we_engage":
            "The natural neighbour of 6.3. Seitzer et al. show a log-likelihood "
            "objective misbehaving on a sigma head; 6.3 shows a released model whose "
            "objective is not a log-likelihood at all -- a sample enters a squared "
            "error, whose optimum is sigma = 0 -- so the failure is more basic than "
            "the one they characterise, and E5 demonstrates it against known noise.",
        "fragments": [
            "log-likelihood",
        ],
    },
    # ------------------------------------------------------------------
    # Added in pre-submission S9, for §5.3's RSSM baseline. Metadata from the arXiv API on
    # CHECKED_ON_S9. No fragment is recorded because §5.3 asserts nothing a paper SAYS in
    # prose: the settings taken from DreamerV2 (and the PlaNet settings deliberately not
    # taken) are each checked against a page of the paper's PDF in
    # results/baseline_citations_verified.json, and cited row by row in
    # docs/presubmission/BASELINE_SPECS.md.
    # ------------------------------------------------------------------
    {
        "key": "hafner2019",
        "arxiv": "1811.04551",
        "title": "Learning Latent Dynamics for Planning from Pixels",
        "authors": ["Danijar Hafner", "Timothy Lillicrap", "Ian Fischer", "Ruben Villegas",
                    "David Ha", "Honglak Lee", "James Davidson"],
        # The arXiv record carries no journal_ref and its comment names no venue; the venue
        # is from the paper's own first page (v5 PDF): "Proceedings of the 36th International
        # Conference on Machine Learning, Long Beach, California, PMLR 97, 2019".
        "venue": "ICML 2019 (PMLR 97)",
        "year": 2019,
        "establishes": "the recurrent state-space model (RSSM): a latent dynamics model whose "
                       "state has a deterministic recurrent part and a stochastic part",
        "why_we_engage":
            "The base paper's RSSM baseline is this architecture, and 5.3 builds one. It is "
            "cited as the architecture's origin; the settings 5.3 takes come from DreamerV2, "
            "which replaces PlaNet's free nats with KL balancing.",
        "fragments": [],
    },
    {
        "key": "hafner2021",
        "arxiv": "2010.02193",
        "title": "Mastering Atari with Discrete World Models",
        "authors": ["Danijar Hafner", "Timothy Lillicrap", "Mohammad Norouzi", "Jimmy Ba"],
        "venue": "ICLR 2021",
        "year": 2021,
        "establishes": "an RSSM with categorical latents, KL balancing and straight-through "
                       "gradients (DreamerV2)",
        "why_we_engage":
            "Table S7 of the base paper fixes the RSSM's shapes and says it is categorical, "
            "and nothing else. 5.3 takes every unstated RSSM setting from DreamerV2 and reads "
            "Table S7's ambiguous latent size in DreamerV2's naming "
            "(docs/presubmission/BASELINE_SPECS.md).",
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


# The result of running --verify on CHECKED_ON_FULL. Kept in the file so the build is
# network-free and the record is reviewable in a diff. Refresh it by running --verify and
# pasting the per-entry results here; EVERY COUNT BELOW IS COMPUTED from _PER_ENTRY, never
# typed, so a stale count cannot survive a refreshed list.
CHECKED_ON_FULL = "2026-09-25"   # all sixteen entries re-verified against arXiv. They had been
# verified once before, in commit e094c3b on CHECKED_ON_REV3, which committed a --verify
# artifact reading 16 / 17 / 17; commit 614dddf then overwrote it with this script's plain
# output, 10 / 9 / 9, because RECORDED had not been refreshed and reproduce.sh runs the plain
# path. That silent loss is ledger entries D-33 and D-34, and it is what put "10 of 16" in
# the paper. The fix is the one D-34 prescribed: refresh RECORDED, and pair it with an
# assertion that the pinned table covers ENTRIES -- see check_pinned_covers_entries().
_PER_ENTRY = [   {   'key': 'lu2022',
        'title_matches': True,
        'authors_match': True,
        'published': '2021-10-08',
        'arxiv_version': '2110.04135v2',
        'comment': 'Spotlight @ ICLR 2022; Spotlight @ RL4RealLife Workshop ICML2021',
        'n_fragments': 5,
        'n_fragments_found': 5,
        'entry_fingerprint': '71d53f453a8cd738'},
    {   'key': 'chua2018',
        'title_matches': True,
        'authors_match': True,
        'published': '2018-05-30',
        'arxiv_version': '1805.12114v2',
        'comment': 'NIPS 2018, video and code available at '
                   'https://sites.google.com/view/drl-in-a-handful-of-trials/',
        'n_fragments': 4,
        'n_fragments_found': 4,
        'entry_fingerprint': 'c513c53268c0fc55'},
    {   'key': 'yu2020',
        'title_matches': True,
        'authors_match': True,
        'published': '2020-05-27',
        'arxiv_version': '2005.13239v6',
        'comment': 'NeurIPS 2020. First two authors contributed equally. Last two authors '
                   'advised equally',
        'entry_fingerprint': 'e1a456805d672d42'},
    {   'key': 'kidambi2020',
        'title_matches': True,
        'authors_match': True,
        'published': '2020-05-12',
        'arxiv_version': '2005.05951v3',
        'comment': 'First two authors contributed equally. Published at NeurIPS 2020. After '
                   'publication at NeurIPS 2020, (1) D4RL benchmark results have been added; '
                   '(2) hyper-parameter ablation studies have been added; (3) scope of Lemma 3 '
                   'has been extended',
        'entry_fingerprint': 'cb405cccdb6dbd31'},
    {   'key': 'lakshminarayanan2017',
        'title_matches': True,
        'authors_match': True,
        'published': '2016-12-05',
        'arxiv_version': '1612.01474v3',
        'comment': 'NIPS 2017',
        'note': 'arXiv preprint dated 2016; the venue year is 2017 and the entry cites the '
                "venue year, as the brief's table does",
        'entry_fingerprint': '47153a7632831a5f'},
    {   'key': 'kuleshov2018',
        'title_matches': True,
        'authors_match': True,
        'published': '2018-07-01',
        'arxiv_version': '1807.00263v1',
        'comment': 'ICML 2018',
        'entry_fingerprint': '4cb4086bceabf08e'},
    {   'key': 'guo2017',
        'title_matches': True,
        'authors_match': True,
        'published': '2017-06-14',
        'arxiv_version': '1706.04599v2',
        'comment': 'ICML 2017',
        'entry_fingerprint': 'd013013181084591'},
    {   'key': 'ovadia2019',
        'title_matches': True,
        'authors_match': True,
        'published': '2019-06-06',
        'arxiv_version': '1906.02530v2',
        'comment': 'Advances in Neural Information Processing Systems, 2019',
        'entry_fingerprint': '9f744486d24c5a48'},
    {   'key': 'abbas2020',
        'title_matches': True,
        'authors_match': True,
        'published': '2020-07-05',
        'arxiv_version': '2007.02418v3',
        'comment': 'Accepted at ICML 2020',
        'entry_fingerprint': 'e506d479e3b78a66'},
    {   'key': 'janner2019',
        'title_matches': True,
        'authors_match': True,
        'published': '2019-06-19',
        'arxiv_version': '1906.08253v3',
        'comment': 'NeurIPS 2019. Code at https://github.com/JannerM/mbpo, project page at: '
                   'https://jannerm.github.io/mbpo-www/',
        'entry_fingerprint': 'a5ad4d5d93ccb442'},
    {   'key': 'malik2019',
        'title_matches': True,
        'authors_match': True,
        'published': '2019-06-19',
        'arxiv_version': '1906.08312v1',
        'comment': None,
        'n_fragments': 1,
        'n_fragments_found': 1,
        'entry_fingerprint': '9ada00301936d275'},
    {   'key': 'lee2015',
        'title_matches': True,
        'authors_match': True,
        'published': '2015-11-19',
        'arxiv_version': '1511.06314v1',
        'comment': None,
        'n_fragments': 2,
        'n_fragments_found': 2,
        'entry_fingerprint': '620593a8a25ee296'},
    {   'key': 'fort2019',
        'title_matches': True,
        'authors_match': True,
        'published': '2019-12-05',
        'arxiv_version': '1912.02757v2',
        'comment': None,
        'n_fragments': 2,
        'n_fragments_found': 2,
        'entry_fingerprint': '7da81b41d6d6b845'},
    {   'key': 'havasi2021',
        'title_matches': True,
        'authors_match': True,
        'published': '2020-10-13',
        'arxiv_version': '2010.06610v2',
        'comment': 'Updated to the ICLR camera ready version, added reference to Soflaei et '
                   'al. 2020',
        'n_fragments': 1,
        'n_fragments_found': 1,
        'entry_fingerprint': 'e4dbdda6e2fa94ac'},
    {   'key': 'wen2020',
        'title_matches': True,
        'authors_match': True,
        'published': '2020-02-17',
        'arxiv_version': '2002.06715v2',
        'comment': None,
        'n_fragments': 1,
        'n_fragments_found': 1,
        'entry_fingerprint': 'd56ba4009279e36a'},
    {   'key': 'seitzer2022',
        'title_matches': True,
        'authors_match': True,
        'published': '2022-03-17',
        'arxiv_version': '2203.09168v2',
        'comment': 'ICLR 2022 camera-ready version. Code available at '
                   'http://github.com/martius-lab/beta-nll',
        'n_fragments': 1,
        'n_fragments_found': 1,
        'entry_fingerprint': '08920163622e7d19'},
    # The two entries added in pre-submission S9, verified by the same verify() on CHECKED_ON_S9
    # with ENTRIES restricted to them; the sixteen above were not re-fetched.
    {   'key': 'hafner2019',
        'title_matches': True,
        'authors_match': True,
        'published': '2018-11-12',
        'arxiv_version': '1811.04551v5',
        'comment': '20 pages, 12 figures, 1 table',
        'entry_fingerprint': '8aeb2cfad4f82bdb'},
    {   'key': 'hafner2021',
        'title_matches': True,
        'authors_match': True,
        'published': '2020-10-05',
        'arxiv_version': '2010.02193v4',
        'comment': 'Published at ICLR 2021. Website: https://danijar.com/dreamerv2',
        'entry_fingerprint': '8b3f331043afe526'}]


def fingerprint(ent):
    """A short hash of everything in an entry that verification checks against arXiv.

    Pinned into each RECORDED record at verification time, so that an entry edited AFTER it was
    verified -- a changed title, author list, identifier or fragment -- is caught rather than
    silently reported as verified. D-34 asked for coverage of every key; a key check alone would
    still pass an edited title, so the fingerprint covers the verified CONTENT, not just the key.
    """
    blob = json.dumps({"arxiv": ent["arxiv"], "title": ent["title"], "authors": ent["authors"],
                       "fragments": ent["fragments"]}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def check_pinned_covers_entries(per):
    """D-34's assertion: the pinned table must cover exactly ENTRIES, as they now stand.

    Turns the silent degradation D-33 and D-34 describe into a loud failure. It fails if an entry
    was added to ENTRIES without being verified, if a pinned record has no entry, or if any entry
    was edited after it was verified. The remedy in every case is to run --verify and refresh
    _PER_ENTRY, not to edit this check.
    """
    pinned = {q["key"]: q for q in per}
    keys = [e["key"] for e in ENTRIES]
    unverified = [k for k in keys if k not in pinned]
    orphaned = [k for k in pinned if k not in set(keys)]
    edited = [e["key"] for e in ENTRIES
              if e["key"] in pinned and pinned[e["key"]].get("entry_fingerprint") != fingerprint(e)]
    assert not (unverified or orphaned or edited), (
        f"RECORDED does not cover ENTRIES as they stand -- unverified {unverified}, "
        f"orphaned {orphaned}, edited since verification {edited}. Run --verify and refresh "
        "_PER_ENTRY; do not weaken this check.")


def record_from(per, checked_on):
    """The verification record, with every count derived from the per-entry results.

    Used by BOTH paths -- the recorded one the build reads and a live --verify -- so the two
    cannot disagree about how a count is formed.
    """
    return {"checked_on": checked_on,
            "method": METHOD,
            "n_entries": len(ENTRIES),
            "per_entry": per,
            "n_metadata_verified": sum(1 for q in per
                                       if q.get("title_matches") and q.get("authors_match")),
            "n_with_fragment_checks": sum(1 for q in per if "n_fragments" in q),
            "n_fragments_checked": sum(q.get("n_fragments", 0) for q in per),
            "n_fragments_verbatim": sum(q.get("n_fragments_found", 0) for q in per)}


METHOD = ("arXiv API metadata for title, author list and venue comment; for any "
          "entry whose 'why_we_engage' asserts what the paper SAYS, the asserted "
          "fragments were additionally matched as substrings of that paper's own "
          "arXiv HTML rendering after tag-stripping and whitespace collapse")
RECORDED = record_from(_PER_ENTRY, CHECKED_ON_FULL)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true",
                    help="re-fetch from arXiv and re-check every entry (needs network)")
    args = ap.parse_args()

    record = RECORDED
    if not args.verify:
        check_pinned_covers_entries(RECORDED["per_entry"])
    if args.verify:
        per = verify()
        bad = [p for p in per if not p.get("title_matches") or not p.get("authors_match")]
        frag_bad = [(p["key"], f["fragment"]) for p in per
                    for f in p.get("fragments", []) if not f["found"]]
        by_key = {e["key"]: e for e in ENTRIES}
        for q in per:
            q["entry_fingerprint"] = fingerprint(by_key[q["key"]])
        record = record_from(per, "RE-VERIFIED THIS RUN")
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
